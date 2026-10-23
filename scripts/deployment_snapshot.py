"""Keep the previous release private on the runner; restore it on deploy failure.

Queues, state tables, and IAM policies are intentionally retained. Rollback
restores Lambda packages/configuration, webhook settings, and command menus,
and disables newly introduced worker mappings/monitor schedules.
"""

import argparse
import base64
import hashlib
import json
import os
import urllib.request
from pathlib import Path

from botocore.exceptions import ClientError

from aws_setup.common import (
    MONITOR_FUNCTION,
    SCHEDULE_NAME,
    WORKER_FUNCTION,
    client,
    telegram_api,
)

CONFIG_KEYS = ("Runtime", "Role", "Handler", "Description", "Timeout", "MemorySize")


def optional(operation, **kwargs):
    try:
        return operation(**kwargs)
    except ClientError as error:
        if error.response["Error"]["Code"] != "ResourceNotFoundException":
            raise
        return None


def private_write(path: Path, content: bytes) -> None:
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "wb") as file:
        file.write(content)


def digest(package: bytes) -> str:
    return base64.b64encode(hashlib.sha256(package).digest()).decode("ascii")


def token_from(config: dict) -> str:
    values = config.get("Environment", {}).get("Variables", {})
    token = values.get("TELEGRAM_BOT_TOKEN") or values.get("YOUR_TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Cannot snapshot deployment: the current bot token is missing")
    return token


def mappings(lambda_client) -> list:
    items = []
    marker = {}
    while True:
        response = optional(lambda_client.list_event_source_mappings, FunctionName=WORKER_FUNCTION, **marker)
        if response is None:
            return items
        items.extend(response.get("EventSourceMappings", []))
        if not response.get("NextMarker"):
            return items
        marker = {"Marker": response["NextMarker"]}


def capture(lambda_client, scheduler, main_name: str, directory: Path) -> None:
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    manifest = {"main": main_name, "functions": {}}
    for name in (main_name, WORKER_FUNCTION, MONITOR_FUNCTION):
        function = optional(lambda_client.get_function, FunctionName=name)
        if function is None:
            if name == main_name:
                raise RuntimeError("The existing bot Lambda was not found")
            manifest["functions"][name] = None
            continue
        config = function["Configuration"]
        if config.get("State", "Active") != "Active" or config.get("LastUpdateStatus", "Successful") != "Successful":
            raise RuntimeError(f"Cannot snapshot {name} while its configuration is unstable")
        try:
            with urllib.request.urlopen(function["Code"]["Location"], timeout=60) as response:
                package = response.read()
        except Exception:
            # Do not print the signed download URL from an HTTP exception.
            raise RuntimeError(f"Cannot download the previous package for {name}") from None
        if digest(package) != config["CodeSha256"]:
            raise RuntimeError(f"Previous package hash did not match for {name}")
        private_write(directory / f"{name}.zip", package)
        saved = {key: config[key] for key in CONFIG_KEYS}
        saved["Environment"] = {"Variables": config.get("Environment", {}).get("Variables", {})}
        saved["Architectures"] = config.get("Architectures", ["x86_64"])
        saved["CodeSha256"] = config["CodeSha256"]
        saved["concurrency"] = lambda_client.get_function_concurrency(FunctionName=name).get("ReservedConcurrentExecutions")
        manifest["functions"][name] = saved

    main_config = manifest["functions"][main_name]
    token = token_from(main_config)
    webhook = telegram_api(token, "getWebhookInfo")
    if webhook.get("has_custom_certificate"):
        raise RuntimeError("Automatic rollback cannot recover a custom Telegram TLS certificate")
    manifest["webhook"] = webhook
    manifest["commands"] = {
        language: telegram_api(token, "getMyCommands", {"language_code": language})
        for language in ("", "it")
    }
    manifest["function_url"] = optional(lambda_client.get_function_url_config, FunctionName=main_name)
    policy = optional(lambda_client.get_policy, FunctionName=main_name)
    manifest["policy"] = json.loads(policy["Policy"]) if policy else {"Statement": []}
    previous_mappings = mappings(lambda_client) if manifest["functions"][WORKER_FUNCTION] else []
    if any(item["State"] not in ("Enabled", "Disabled") for item in previous_mappings):
        raise RuntimeError("Cannot snapshot a worker event source while it is changing")
    manifest["mappings"] = {item["UUID"]: item["State"] == "Enabled" for item in previous_mappings}
    schedule = optional(scheduler.get_schedule, Name=SCHEDULE_NAME)
    manifest["schedule_state"] = schedule["State"] if schedule else None
    # The manifest includes environment secrets. Never upload it as an artifact.
    private_write(directory / "manifest.json", json.dumps(manifest, default=str).encode())
    print("Previous Lambda packages, configuration, and webhook captured privately on the runner.")


def restore_function(lambda_client, name: str, saved: dict, directory: Path) -> None:
    package = (directory / f"{name}.zip").read_bytes()
    if digest(package) != saved["CodeSha256"]:
        raise RuntimeError(f"Rollback package hash did not match for {name}")
    waiter = lambda_client.get_waiter("function_updated_v2")
    waiter.wait(FunctionName=name)
    # Submit package and architecture together so native wheels match the CPU.
    lambda_client.update_function_code(
        FunctionName=name, ZipFile=package, Architectures=saved["Architectures"],
    )
    waiter.wait(FunctionName=name)
    settings = {key: saved[key] for key in (*CONFIG_KEYS, "Environment")}
    lambda_client.update_function_configuration(FunctionName=name, **settings)
    waiter.wait(FunctionName=name)
    if saved["concurrency"] is None:
        lambda_client.delete_function_concurrency(FunctionName=name)
    else:
        lambda_client.put_function_concurrency(FunctionName=name, ReservedConcurrentExecutions=saved["concurrency"])
    actual = lambda_client.get_function_configuration(FunctionName=name)
    if actual["CodeSha256"] != saved["CodeSha256"]:
        raise RuntimeError(f"Rollback verification failed for {name}")


def restore_url_and_permissions(lambda_client, main_name: str, manifest: dict) -> None:
    saved_url = manifest["function_url"]
    if saved_url:
        lambda_client.update_function_url_config(
            FunctionName=main_name, AuthType=saved_url["AuthType"],
            InvokeMode=saved_url.get("InvokeMode", "BUFFERED"), Cors=saved_url.get("Cors", {}),
        )
    else:
        optional(lambda_client.delete_function_url_config, FunctionName=main_name)

    current = optional(lambda_client.get_policy, FunctionName=main_name)
    statements = json.loads(current["Policy"])["Statement"] if current else []
    original = {item["Sid"]: item for item in manifest["policy"]["Statement"]}
    current_ids = {item["Sid"] for item in statements}
    for sid in ("FunctionURLAllowPublicAccess", "FunctionURLAllowPublicInvoke"):
        if sid in current_ids and sid not in original:
            lambda_client.remove_permission(FunctionName=main_name, StatementId=sid)
    for sid, statement in original.items():
        principal = statement.get("Principal", {})
        if sid in current_ids or not isinstance(principal, dict) or principal.get("Service") != "apigateway.amazonaws.com":
            continue
        args = {"FunctionName": main_name, "StatementId": sid, "Action": "lambda:InvokeFunction", "Principal": "apigateway.amazonaws.com"}
        for condition in statement.get("Condition", {}).values():
            for key, value in condition.items():
                if key.lower() == "aws:sourcearn":
                    args["SourceArn"] = value
                elif key.lower() == "aws:sourceaccount":
                    args["SourceAccount"] = value
                else:
                    raise RuntimeError("Cannot automatically restore an unfamiliar API Gateway permission condition")
        lambda_client.add_permission(**args)


def restore_triggers(lambda_client, scheduler, manifest: dict) -> None:
    for item in mappings(lambda_client):
        enabled = manifest["mappings"].get(item["UUID"], False)
        if (item["State"] == "Enabled") != enabled:
            lambda_client.update_event_source_mapping(UUID=item["UUID"], Enabled=enabled)
    schedule = optional(scheduler.get_schedule, Name=SCHEDULE_NAME)
    if schedule:
        state = manifest["schedule_state"] or "DISABLED"
        if schedule["State"] != state:
            keys = ("Name", "GroupName", "ScheduleExpression", "FlexibleTimeWindow", "Target", "ScheduleExpressionTimezone", "StartDate", "EndDate", "Description", "KmsKeyArn", "ActionAfterCompletion")
            settings = {key: schedule[key] for key in keys if key in schedule}
            scheduler.update_schedule(**settings, State=state)


def restore_telegram(manifest: dict) -> None:
    config = manifest["functions"][manifest["main"]]
    token = token_from(config)
    webhook = manifest["webhook"]
    if webhook.get("url"):
        payload = {key: webhook[key] for key in ("url", "max_connections", "allowed_updates") if key in webhook}
        secret = config["Environment"]["Variables"].get("TELEGRAM_WEBHOOK_SECRET")
        if secret:
            payload["secret_token"] = secret
        telegram_api(token, "setWebhook", {**payload, "drop_pending_updates": False})
    else:
        telegram_api(token, "deleteWebhook", {"drop_pending_updates": False})
    for language, commands in manifest["commands"].items():
        telegram_api(token, "setMyCommands", {"language_code": language, "commands": commands})
    actual = telegram_api(token, "getWebhookInfo")
    if actual.get("url", "") != webhook.get("url", ""):
        raise RuntimeError("Previous Telegram webhook did not restore correctly")


def restore(lambda_client, scheduler, directory: Path) -> None:
    manifest = json.loads((directory / "manifest.json").read_text())
    failures = []

    def attempt(label, operation, *args):
        try:
            operation(*args)
        except Exception as error:
            # Secondary resource failures must not prevent main/webhook recovery.
            failures.append(label)
            print(f"::error::Rollback failed for {label}: {type(error).__name__}")

    for name in (WORKER_FUNCTION, MONITOR_FUNCTION, manifest["main"]):
        saved = manifest["functions"][name]
        if saved:
            attempt(name, restore_function, lambda_client, name, saved, directory)
    attempt("worker and monitor triggers", restore_triggers, lambda_client, scheduler, manifest)
    attempt("Function URL and API Gateway permissions", restore_url_and_permissions, lambda_client, manifest["main"], manifest)
    attempt("Telegram webhook and commands", restore_telegram, manifest)
    if failures:
        raise RuntimeError(f"Rollback incomplete for: {', '.join(failures)}")
    print("Previous Lambda release and Telegram webhook restored; queued updates and state retained.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("capture", "restore"))
    args = parser.parse_args()
    region = os.environ["AWS_REGION"]
    directory = Path(os.environ["DEPLOYMENT_SNAPSHOT_DIR"])
    lambda_client, scheduler = client("lambda", region), client("scheduler", region)
    if args.operation == "capture":
        capture(lambda_client, scheduler, os.getenv("LAMBDA_FUNCTION_NAME", "ToEnWikipediaBot"), directory)
    else:
        restore(lambda_client, scheduler, directory)


if __name__ == "__main__":
    main()
