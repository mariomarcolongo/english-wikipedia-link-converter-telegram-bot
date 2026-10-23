import io
import base64
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from botocore.exceptions import ClientError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import bootstrap_oidc
import bootstrap_oidc_v2
import deployment_snapshot as snapshot
import deploy_arm64
import inspect_oidc
from aws_setup import lambda_resources


def missing():
    return ClientError({"Error": {"Code": "ResourceNotFoundException"}}, "GetFunction")


class DeploymentTrustTests(unittest.TestCase):
    def test_oidc_diagnostics_never_print_tokens_or_unselected_claims(self):
        payload = {"aud": "sts.amazonaws.com", "sub": "public-subject", "private_claim": "do-not-log"}
        encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
        token = f"header.{encoded}.signature"
        response = io.BytesIO(json.dumps({"value": token}).encode())
        output = io.StringIO()
        with patch.dict(os.environ, {"ACTIONS_ID_TOKEN_REQUEST_URL": "https://example/token?job=1", "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "private-request-token"}), patch.object(inspect_oidc.urllib.request, "urlopen", return_value=response), patch("sys.stdout", output):
            inspect_oidc.main()
        self.assertEqual(json.loads(output.getvalue()), {"aud": "sts.amazonaws.com", "sub": "public-subject"})
        self.assertNotIn(token, output.getvalue())
        self.assertNotIn("private-request-token", output.getvalue())
        self.assertNotIn("do-not-log", output.getvalue())

    def test_both_bootstraps_match_production_environment_token(self):
        provider = "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
        for module in (bootstrap_oidc, bootstrap_oidc_v2):
            statement = module.trust_policy(provider)["Statement"][0]
            conditions = statement["Condition"]["StringEquals"]
            self.assertEqual(conditions["token.actions.githubusercontent.com:aud"], "sts.amazonaws.com")
            self.assertEqual(conditions["token.actions.githubusercontent.com:sub"],
                             "repo:mariomarcolongo@84038748/english-wikipedia-link-converter-telegram-bot@782735600:environment:production")
            self.assertNotIn("*", conditions["token.actions.githubusercontent.com:sub"])

    def test_package_and_architecture_are_uploaded_in_one_request(self):
        client = Mock()
        deploy_arm64.update_code(client, "bot", b"arm package")
        client.update_function_code.assert_called_once_with(
            FunctionName="bot", ZipFile=b"arm package", Publish=False, Architectures=["arm64"])
        client.update_function_configuration.assert_not_called()

    def test_prepared_url_does_not_grant_public_access(self):
        client = Mock()
        client.get_function_url_config.side_effect = missing()
        client.create_function_url_config.return_value = {"FunctionUrl": "https://example/"}
        self.assertEqual(lambda_resources.prepare_function_url(client, "bot"), "https://example/")
        client.create_function_url_config.assert_called_once_with(
            FunctionName="bot", AuthType="AWS_IAM", InvokeMode="BUFFERED")
        client.add_permission.assert_not_called()


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.client, self.scheduler = Mock(), Mock()
        self.package = b"previous real Lambda ZIP"
        self.config = {
            "Runtime": "python3.13", "Role": "arn:aws:iam::123456789012:role/bot",
            "Handler": "ToEnWikipediaBot.lambda_handler", "Description": "previous release",
            "Timeout": 15, "MemorySize": 256, "Architectures": ["x86_64"],
            "CodeSha256": snapshot.digest(self.package),
            "Environment": {"Variables": {"TELEGRAM_BOT_TOKEN": "private-token", "TELEGRAM_WEBHOOK_SECRET": "private-secret", "DEPLOYMENT_VERSION": "previous"}},
        }
        self.client.get_function.side_effect = [
            {"Configuration": self.config, "Code": {"Location": "https://example/package"}},
            missing(), missing(),
        ]
        self.client.get_function_concurrency.return_value = {}
        self.client.get_function_url_config.return_value = {"AuthType": "AWS_IAM", "InvokeMode": "BUFFERED"}
        self.client.get_policy.side_effect = missing()
        self.scheduler.get_schedule.side_effect = missing()
        self.webhook = {"url": "https://old-api.example/", "max_connections": 40, "allowed_updates": ["message"]}

    def telegram(self, token, method, payload=None):
        self.assertEqual(token, "private-token")
        if method == "getWebhookInfo":
            return self.webhook
        if method == "getMyCommands":
            return [{"command": "start", "description": "Previous menu"}]
        return True

    def capture(self, directory):
        with patch.object(snapshot.urllib.request, "urlopen", return_value=io.BytesIO(self.package)), patch.object(snapshot, "telegram_api", side_effect=self.telegram):
            snapshot.capture(self.client, self.scheduler, "bot", directory)

    def test_capture_keeps_secrets_private_and_original_code(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "snapshot"
            self.capture(directory)
            saved = json.loads((directory / "manifest.json").read_text())
            self.assertEqual((directory / "bot.zip").read_bytes(), self.package)
            self.assertEqual(saved["functions"]["bot"]["Architectures"], ["x86_64"])
            self.assertIsNone(saved["functions"][snapshot.WORKER_FUNCTION])
            self.assertEqual(os.stat(directory / "manifest.json").st_mode & 0o777, 0o600)
            self.assertEqual(os.stat(directory).st_mode & 0o777, 0o700)

    def test_wrong_download_hash_prevents_a_usable_snapshot(self):
        self.config["CodeSha256"] = "wrong"
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            with self.assertRaisesRegex(RuntimeError, "hash did not match"):
                self.capture(directory)
            self.assertFalse((directory / "manifest.json").exists())
            self.client.update_function_code.assert_not_called()

    def test_restore_returns_previous_architecture_environment_webhook_and_menus(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self.capture(directory)
            self.client.get_function_configuration.return_value = self.config
            self.client.list_event_source_mappings.return_value = {
                "EventSourceMappings": [{"UUID": "new-worker", "State": "Enabled"}]}
            with patch.object(snapshot, "telegram_api", side_effect=self.telegram) as telegram:
                snapshot.restore(self.client, self.scheduler, directory)
            self.client.update_function_code.assert_called_once_with(
                FunctionName="bot", ZipFile=self.package, Architectures=["x86_64"])
            self.assertEqual(self.client.update_function_configuration.call_args.kwargs["Environment"], self.config["Environment"])
            self.client.delete_function_concurrency.assert_called_once_with(FunctionName="bot")
            self.client.update_function_url_config.assert_called_once_with(
                FunctionName="bot", AuthType="AWS_IAM", InvokeMode="BUFFERED", Cors={})
            self.client.update_event_source_mapping.assert_called_once_with(UUID="new-worker", Enabled=False)
            webhook = next(call.args[2] for call in telegram.call_args_list if call.args[1] == "setWebhook")
            self.assertEqual(webhook["url"], self.webhook["url"])
            self.assertEqual(webhook["secret_token"], "private-secret")
            self.assertFalse(webhook["drop_pending_updates"])
            self.assertEqual(sum(call.args[1] == "setMyCommands" for call in telegram.call_args_list), 2)

    def test_tampered_rollback_zip_is_never_deployed(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "bot.zip").write_bytes(b"tampered")
            with self.assertRaisesRegex(RuntimeError, "Rollback package hash"):
                snapshot.restore_function(self.client, "bot", self.config, directory)
            self.client.update_function_code.assert_not_called()

    def test_cutover_failure_restores_gateway_and_removes_new_public_access(self):
        old = {"Sid": "previous-gateway", "Principal": {"Service": "apigateway.amazonaws.com"},
               "Condition": {"ArnLike": {"AWS:SourceArn": "arn:previous-api"}}}
        self.client.get_policy.side_effect = None
        self.client.get_policy.return_value = {"Policy": json.dumps({"Statement": [
            {"Sid": "FunctionURLAllowPublicAccess", "Principal": "*"},
            {"Sid": "FunctionURLAllowPublicInvoke", "Principal": "*"},
        ]})}
        snapshot.restore_url_and_permissions(self.client, "bot", {
            "function_url": {"AuthType": "AWS_IAM"}, "policy": {"Statement": [old]},
        })
        self.assertEqual(self.client.remove_permission.call_count, 2)
        self.client.add_permission.assert_called_once_with(
            FunctionName="bot", StatementId="previous-gateway", Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com", SourceArn="arn:previous-api")

    def test_new_monitor_schedule_is_disabled_after_failed_first_deploy(self):
        self.client.list_event_source_mappings.return_value = {"EventSourceMappings": []}
        self.scheduler.get_schedule.side_effect = None
        self.scheduler.get_schedule.return_value = {
            "Name": snapshot.SCHEDULE_NAME, "State": "ENABLED",
            "Target": {"Arn": "new-monitor", "RoleArn": "role"},
            "ScheduleExpression": "rate(15 minutes)", "FlexibleTimeWindow": {"Mode": "OFF"},
        }
        snapshot.restore_triggers(self.client, self.scheduler, {"mappings": {}, "schedule_state": None})
        self.assertEqual(self.scheduler.update_schedule.call_args.kwargs["State"], "DISABLED")

    def test_main_recovery_is_attempted_even_if_worker_recovery_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self.capture(directory)
            manifest = json.loads((directory / "manifest.json").read_text())
            manifest["functions"][snapshot.WORKER_FUNCTION] = self.config
            (directory / "manifest.json").write_text(json.dumps(manifest))
            with patch.object(snapshot, "restore_function", side_effect=[RuntimeError("worker failed"), None]) as restore_function, patch.object(snapshot, "restore_triggers"), patch.object(snapshot, "restore_url_and_permissions"), patch.object(snapshot, "restore_telegram") as telegram:
                with self.assertRaisesRegex(RuntimeError, "Rollback incomplete"):
                    snapshot.restore(self.client, self.scheduler, directory)
            self.assertEqual(restore_function.call_args_list[-1].args[1], "bot")
            telegram.assert_called_once()


if __name__ == "__main__":
    unittest.main()
