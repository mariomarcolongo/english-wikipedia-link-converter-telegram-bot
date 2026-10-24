# English Wikipedia Link Converter

Telegram bot that converts any non-English Wikipedia article URL into its English equivalent: https://t.me/ToEnWikipediaBot.

## Localization

The bot supports English and Italian. Use the [localization glossary](docs/LOCALIZATION_GLOSSARY.md) for consistent terminology and writing conventions, and the [Italian localization inventory](docs/ITALIAN_LOCALIZATION.md) for the translated messages and command descriptions.

## Reliability and security architecture

```text
Telegram webhook
      │
      ▼
AWS Lambda Function URL ── commands / inline queries ──► Telegram
      │
      └── link messages ──► Amazon SQS ──► dedicated worker Lambda
                                                │
                                                ├── Wikipedia API
                                                └── DynamoDB state / rate limits

EventBridge Scheduler ──► independent monitor Lambda
                              ├── Function URL health
                              ├── Telegram getWebhookInfo
                              ├── SQS / dead-letter queue
                              ├── SNS email alerts
                              └── optional Telegram status channel
```

The webhook acknowledges a conversion request only after SQS accepts it. SQS retries temporary failures and moves repeatedly failing updates to a dead-letter queue. DynamoDB provides update deduplication, processing leases, distributed abuse limits, recovery-notice suppression, and monitor state.

A separate monitor Lambda runs every 15 minutes, so the bot does not need to be healthy to report its own outage. `/status` displays the latest external check.

### Recovery behavior

To avoid flooding chats after an outage:

- group and channel messages older than 15 minutes are skipped;
- one recovery notice is sent per affected group during a six-hour recovery window;
- private requests 15–60 minutes old can be processed with a delay notice;
- at most three delayed private conversions are sent per chat during a six-hour recovery window;
- private requests older than one hour are skipped with one request-to-resend notice.

Telegram may redeliver webhook updates, and SQS/Lambda processing is at-least-once. The bot uses Telegram `update_id` values in DynamoDB to suppress duplicate processing.

## Abuse protection

- required Telegram webhook secret;
- POST-only webhook with JSON validation and a 64 KiB request limit;
- strict structural Wikipedia-domain validation;
- five links maximum per update;
- distributed limits of 10 conversion requests per user and 30 per chat per minute;
- separate distributed limits for commands and inline requests;
- rate-limit warnings deduplicated per chat;
- a worker event source capped at two concurrent invocations, plus reserved Lambda capacity when the account quota permits;
- SQS dead-letter handling and bounded retry behavior;
- short-lived repository-scoped GitHub OIDC deployment credentials;
- 14-day CloudWatch log retention;
- up to seven CloudWatch alarms and an optional AWS Budget, while keeping the account at or below ten standard alarms.

## AWS free-tier footprint

The deployment intentionally uses small, serverless resources:

- one 256 MB ARM64 webhook Lambda, requesting three reserved concurrent executions when quota permits;
- one 256 MB ARM64 SQS worker Lambda limited to two concurrent invocations;
- one 128 MB ARM64 monitor Lambda invoked every 15 minutes;
- one standard SQS queue and one dead-letter queue;
- one DynamoDB table provisioned at 10 read and 10 write capacity units;
- one EventBridge Scheduler schedule;
- one SNS topic;
- up to seven CloudWatch alarms, automatically capped so the account stays at or below ten standard alarms;
- 14-day log retention.

The SQS event source explicitly limits worker processing to two concurrent invocations. Deployment requests reserved capacity for the webhook, worker, and monitor when AWS allows it. Accounts with a total Lambda concurrency quota of 10 cannot reserve capacity because AWS requires 10 unreserved executions; deployment handles that specific limit by using the shared pool. Other Lambda workloads in the account can still compete for shared capacity. Explicit SQS maximum concurrency can increase idle polling compared with Lambda's polling optimization. ARM64 uses AWS Graviton and is selected for efficiency. The footprint is designed to remain inside the normal free allowances for a small bot, but AWS pricing and account eligibility can vary. Set `ALERT_EMAIL` and the deployment will also create a small monthly budget alert when the account has a free budget slot.

## Deployment

The GitHub Actions workflow tests every pull request and every `main` deployment under Python 3.13, matching the Lambda runtime. It cross-installs `manylinux2014_aarch64` wheels, inspects every native ELF extension, invokes the exact package on the ARM64 worker as a canary, and only then migrates the public webhook Lambda.

Required existing GitHub secrets:

- `AWS_REGION` — currently `eu-north-1`;
- `LAMBDA_FUNCTION_NAME` — currently `ToEnWikipediaBot`;
- the Telegram bot token remains in the Lambda environment as `TELEGRAM_BOT_TOKEN` or the legacy `YOUR_TELEGRAM_BOT_TOKEN`.

Optional GitHub secrets:

- `ALERT_EMAIL` — SNS and AWS Budget alerts; confirm the SNS subscription email after deployment;
- `ADMIN_CHAT_ID` — private Telegram administrator alerts;
- `STATUS_CHANNEL_ID` — channel username or numeric ID for outage/recovery posts;
- `STATUS_CHANNEL_URL` — public link displayed by `/start`, `/help`, and `/status`;
- `STATUS_BOT_TOKEN` — optional separate bot used only to publish alerts. Without it, the main bot token is used.

Optional GitHub repository variable:

- `MONTHLY_BUDGET_USD` — defaults to `1`.

### One-time AWS OIDC bootstrap

Production deployments use only short-lived GitHub OIDC credentials. The workflow does not read static AWS access-key secrets or fall back to an IAM user.

For a new AWS account, an administrator first runs `scripts/bootstrap_oidc_v2.py` with temporary AWS administrator credentials, `AWS_REGION`, and `LAMBDA_FUNCTION_NAME` set. This requires an existing bot Lambda so the script can scope deployment permissions to its execution role. The legacy JSON bootstrap policy in `aws/` is available for a temporary, administrator-controlled IAM-user migration; remove that inline policy after setup.

The deployment role is restricted to this repository's immutable owner/repository IDs and its `production` environment. The repository's OIDC settings have `use_immutable_subject=true`; AWS trust includes those IDs. Configure that GitHub environment to allow deployments from the `main` branch only. The job rejects stale commits and serializes production deployments without cancelling an active rollout. OIDC token permission is limited to the deploy job, with bounded retries for temporary authentication failures. Diagnostic output includes public identity claims, never the token itself.

After migrating an old installation, remove the temporary bootstrap policy and the repository's obsolete `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets. Subsequent merges to `main` deploy automatically without either key.

The deployment automatically:

1. verifies the Python tests, dependency review, and ARM64 native wheels;
2. privately snapshots the actual deployed Lambda packages, configuration, Function URL policy, webhook, and command menus on the runner;
3. validates the ARM64 package through a real worker Lambda invocation;
4. prepares dependencies and runtime settings, then uploads the public package and ARM64 architecture together;
5. creates or updates SQS, DynamoDB, SNS, IAM, the dedicated worker and monitor Lambdas, schedule, alarms, log retention, and optional budget;
6. creates and stores a webhook secret without printing it, then checks the configured handler before opening public Function URL access;
7. points Telegram directly to the Lambda Function URL with `drop_pending_updates=false`;
8. limits Telegram to `message`, `channel_post`, and `inline_query` updates;
9. configures the BotFather command menu through `setMyCommands`;
10. invokes the independent monitor, verifies the live commit matches the workflow commit, and removes legacy API Gateway invoke permission only after the Function URL webhook is verified.

If deployment fails after production changes begin, the workflow restores the previous packages, architectures, runtime configuration, concurrency settings, Function URL access, webhook, and command menus. It disables worker mappings and monitor schedules introduced by a failed first migration. A secondary function rollback failure does not prevent recovery of the main bot and webhook. Queue contents, state tables, and infrastructure policies are retained; this is a service rollback, not a destructive infrastructure rollback. Failures before production changes do not trigger a rollback.

Snapshots contain runtime secrets, stay in a private directory on the ephemeral runner, are never uploaded as artifacts, and are removed at the end of the job. A manually cancelled run attempts recovery, but a forcibly terminated runner or AWS outage can interrupt recovery and require a manual workflow rerun. GitHub Actions notifications report deployment failures; the independent AWS monitor checks runtime health every 15 minutes once provisioned.

The old API Gateway resource may remain visible in AWS after its invoke permission is removed. It can be deleted manually once the Function URL webhook has been verified.

## Operations

- `/status` shows the most recent independent check, Telegram pending-update count, queue depth, and deployed version.
- CloudWatch alarms cover Function URL 5xx responses, webhook and worker Lambda errors, throttles, queue age, dead-letter messages, and monitor errors.
- The independent monitor additionally detects a mismatched webhook URL, a growing Telegram backlog, a stale SQS backlog, and dead-letter messages.
- Monitor notifications are transition-based, with six-hour reminders during a continuing outage, to avoid alert spam.

Do not store or log message text, user names, bot tokens, or webhook secrets. The persistent DynamoDB records contain operational keys and counters only and expire automatically, except for the current monitor status record.

## License

The code in this repository is licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0)](https://www.gnu.org/licenses/agpl-3.0.en.html), except where otherwise specified.

The icon for the English Wikipedia Link Converter Telegram Bot is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)][cc-by-sa]. See the [icon directory](https://github.com/mariomarcolongo/English-Wikipedia-Link-Converter-Telegram-Bot/tree/main/Telegram-Bot-Icon) for more details.

### Image credits

- **Wikipedia logo**, Version2 by Vanished user 24kwjf10h32h, Version 1 by Nohat (concept by Paullusmagnus); Wikimedia, used under [CC BY-SA 3.0][cc-by-sa-3.0].
- **Left arrow**, by Icons8, available under [CC0](https://creativecommons.org/share-your-work/public-domain/cc0/).

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/
[cc-by-sa-3.0]: https://creativecommons.org/licenses/by-sa/3.0/
