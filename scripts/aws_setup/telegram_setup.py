from aws_setup.common import telegram_api


def configure_webhook(token: str, function_url: str, secret_token: str) -> dict:
    telegram_api(
        token,
        "setWebhook",
        {
            "url": function_url,
            "secret_token": secret_token,
            "max_connections": 3,
            "allowed_updates": ["message", "channel_post", "inline_query"],
            "drop_pending_updates": False,
        },
    )
    telegram_api(
        token,
        "setMyCommands",
        {
            "commands": [
                {"command": "start", "description": "Start the bot and show instructions"},
                {"command": "help", "description": "Show usage instructions"},
                {"command": "status", "description": "Check the service status"},
                {"command": "source", "description": "View the source code"},
                {"command": "license", "description": "View licenses and image credits"},
                {"command": "privacy", "description": "View the privacy policy"},
            ]
        },
    )
    telegram_api(
        token,
        "setMyCommands",
        {
            "language_code": "it",
            "commands": [
                {"command": "start", "description": "Avvia il bot e mostra le istruzioni"},
                {"command": "help", "description": "Mostra le istruzioni per l'uso"},
                {"command": "status", "description": "Controlla lo stato del servizio"},
                {"command": "source", "description": "Visualizza il codice sorgente"},
                {"command": "license", "description": "Visualizza licenze e crediti delle immagini"},
                {"command": "privacy", "description": "Visualizza l'informativa sulla privacy"},
            ],
        },
    )
    info = telegram_api(token, "getWebhookInfo")
    actual = str(info.get("url", "")).rstrip("/")
    expected = function_url.rstrip("/")
    if actual != expected:
        raise RuntimeError("Telegram webhook verification failed")
    return info
