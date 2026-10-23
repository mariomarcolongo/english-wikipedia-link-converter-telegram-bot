# Privacy Policy

_Last updated: 2026-10-23_

This Privacy Policy describes how the **English Wikipedia Link Converter Bot** ("we", "us", or the "Bot") handles information when you interact with it on Telegram.

This policy supplements Telegram's [Standard Bot Privacy Policy](https://telegram.org/privacy-tpa). Telegram's general terms and definitions also apply.

## 1. Information processed

- **Telegram update data:** Telegram sends the Bot the message or inline query needed to provide the requested feature. For link conversion, this can include the submitted Wikipedia URL and its article title. The Bot does not keep a chat history.
- **Operational identifiers and counters:** The Bot uses Telegram user, chat, and update identifiers to apply rate limits, prevent duplicate processing, and manage recovery notices. These records are stored in DynamoDB and expire automatically. The table does not store message text.
- **Temporary processing data:** Updates accepted for conversion may be held in Amazon SQS while they await processing or retry. Repeatedly failing updates may enter a dead-letter queue for operational troubleshooting.
- **Logs:** The Bot logs warnings and errors for operations. It is designed not to log message text, user names, bot tokens, or webhook secrets.

## 2. How information is used

The Bot uses submitted Wikipedia links and article titles to find corresponding English Wikipedia pages, and uses operational identifiers to provide the service reliably and limit abuse.

## 3. Service providers

- **Telegram** delivers updates and messages to and from the Bot.
- **Amazon Web Services (AWS)** runs the Bot and its queue, operational state, and monitoring services. AWS may process service data as part of operating those services.
- **The Wikimedia Foundation's public Wikipedia API** receives the submitted article title and language edition for a requested lookup. The Bot does not send Telegram user or chat identifiers to Wikipedia.

## 4. Retention

Message updates in the processing queue are retained only as needed for processing, retry, or dead-letter handling. Operational DynamoDB records have automatic expiration. CloudWatch logs are configured for 14-day retention. Telegram and third-party services may retain data under their own policies.

## 5. Sharing and security

We do not sell personal information. Information is processed by the providers described above to deliver and operate the Bot. Connections to Telegram and Wikipedia use HTTPS. Do not send sensitive personal information to the Bot.

## 6. Your choices and requests

You can stop interacting with the Bot at any time. For privacy questions or requests, please open an issue at [the project's GitHub issue tracker](https://github.com/mariomarcolongo/english-wikipedia-link-converter-telegram-bot/issues).

## Disclaimer

This Bot is an independent service and is not maintained, endorsed, or affiliated with Telegram Messenger Inc. or the Wikimedia Foundation.
