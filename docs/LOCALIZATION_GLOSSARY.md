# Localization glossary

Use this English–Italian glossary when adding or revising bot messages, Telegram command descriptions, and localized documentation. It records the terminology used by this project; it is not a complete list of translated strings.

The runtime strings live in `TEXT` in [`ToEnWikipediaBot.py`](../ToEnWikipediaBot.py). The [Italian localization inventory](ITALIAN_LOCALIZATION.md) documents the messages and command menu. Keep both aligned when changing visible text. This glossary guides future edits and does not change the bot's behavior.

## Core terminology

| English term | Preferred Italian | Usage |
| --- | --- | --- |
| bot | bot | Lowercase in ordinary prose; keep the product name unchanged. |
| Wikipedia page / article | pagina di Wikipedia / articolo di Wikipedia | Prefer *pagina* in conversion messages; use *articolo* for article content or titles. |
| English Wikipedia | Wikipedia in inglese | Refers to the English-language edition. |
| non-English Wikipedia link | link a una pagina Wikipedia in un'altra lingua | Use the shorter *URL di Wikipedia non in inglese* where space is limited. |
| link | link | Invariable: *un link*, *i link*. |
| URL | URL | Uppercase and invariable: *un URL*, *gli URL*. Preserve the address itself. |
| conversion | conversione | Finding the corresponding English page and returning its link. The bot does not translate article text. |
| converted links | link convertiti | Links returned by the conversion process. |
| lookup | ricerca | A Wikipedia lookup; avoid literal translations such as *consultazione della tabella*. |
| inline mode | modalità inline | Telegram's feature for using `@{username}` inside a chat. |
| inline query | ricerca inline | The user's inline request, as in the privacy policy. |
| group | gruppo | A Telegram group; *partecipanti* for its members. |
| command | comando | Localize the description, preserving the command itself. |
| language preference | preferenza della lingua | The saved user choice, distinct from Telegram's language. |
| automatic language selection | selezione automatica della lingua | Display the option as *Automatica (lingua di Telegram)*. |

## Service status and errors

| English term | Preferred Italian | Usage |
| --- | --- | --- |
| service status | stato del servizio | Used for the status button and `/status`. |
| operational | operativo | Current healthy status: *✅ Operativo*. |
| outage / service disruption | interruzione del servizio | Use plain wording in user-facing notices. |
| temporarily unavailable | temporaneamente non disponibile | A temporary service or conversion failure, not a missing Wikipedia page. |
| recovery | ripristino | In notices, a full phrase such as *il bot si riprendeva da un'interruzione del servizio* can be more natural. |
| delayed request | richiesta elaborata in ritardo | Distinguish delayed processing from a failed conversion. |
| older / stale request | richiesta meno recente | Avoid *richiesta scaduta* unless the text specifically describes an expiry. |
| retry | riprova / nuovo tentativo | *Riprova* in instructions; *nuovo tentativo* in explanatory prose. |
| resend the link | invia di nuovo il link | The user must submit the link again. |
| rate limit | limite d'uso | In the error itself, explain the action: *Troppe richieste di conversione. Attendi circa un minuto e riprova.* |
| last external check | ultimo controllo esterno | The independent monitor's check, not the user's last request. |
| Telegram pending updates | aggiornamenti Telegram in attesa | Telegram events awaiting delivery or processing, not software updates. |
| queue depth | elementi in coda | Number of queued items; avoid the literal *profondità della coda*. |
| status updates | aggiornamenti sullo stato del servizio | Service news, distinct from pending Telegram events. |
| service notices | avvisi sul servizio | Operational notices in help text. |
| unknown | sconosciuto | A value is unknown; use *Stato non ancora disponibile* for an unavailable status. |
| version | versione | Preserve the version identifier or commit hash. |

## Source, licensing, and privacy

| English term | Preferred Italian | Usage |
| --- | --- | --- |
| source code | codice sorgente | `/source` and contribution instructions. |
| repository | repository | Invariable; do not translate repository names or paths. |
| fork | fork | Explain the action as *crea una tua versione con un fork*. |
| license | licenza | Preserve license identifiers and the license linked by the original text. |
| image credits | crediti delle immagini | Attribution for the bot icon's components. |
| Privacy Policy | informativa sulla privacy | Title case only at the start of a heading or sentence. |
| user ID / chat ID / update ID | identificativo dell'utente / della chat / dell'aggiornamento | Use *ID Telegram* where the existing text needs a shorter label. |
| operational state | stato operativo | Technical processing state, distinct from service health. |
| processing queue | coda di elaborazione | Temporary storage for accepted conversion requests. |
| dead-letter queue | coda di messaggi non recapitabili | Operational handling of repeatedly unsuccessful updates. |
| logs | log | Invariable: *i log*. |
| retention | conservazione | Data retention; do not alter durations or deletion conditions while translating. |
| expiry | scadenza | Distinguish the configured expiry from actual automatic deletion. |

## Writing conventions

- Address the user informally with **tu**. Let the bot speak in the first person: *Inviami*, *Aggiungimi*, *Userò*.
- Use short, direct instructions. Prefer *Riprova* or *invia di nuovo il link* when those are the actions the user can take.
- Use sentence case for Italian headings, buttons, and menu descriptions: *Stato del servizio*, not *Stato Del Servizio*.
- Keep button labels short and descriptive. Keep help and command-menu descriptions consistent in meaning; they need not be identical sentences.
- Preserve accents and apostrophes: *modalità*, *è*, *un'interruzione*, *l'inglese*. Use natural Italian word order rather than copying English capitalization or syntax.
- Keep a missing English page distinct from a temporary lookup failure. Use the existing *Nessuna pagina di Wikipedia in inglese trovata per* for the former and retry wording for the latter.
- Preserve numbers, time units, and operational guarantees. Do not turn *circa un minuto* into an exact promise or automatic expiry into immediate deletion.

## Content to preserve

- **Names:** English Wikipedia Link Converter, Telegram, Wikipedia, Wikimedia Commons, Wikimedia Foundation, Amazon Web Services (AWS), and AWS service names.
- **Commands and arguments:** `/start`, `/help`, `/status`, `/source`, `/license`, `/privacy`, `/language`, and `auto`, `en`, `it` in command examples.
- **Identifiers and addresses:** usernames, article titles received from users, URLs, email addresses, file paths, version hashes, and API identifiers. Translate link labels where appropriate; select the matching localized privacy-policy URL for each language.
- **Formatting:** preserve placeholder names and braces exactly, including `{name}`, `{count}`, `{url}`, `{username}`, and `{language}`. Placeholders may move to fit Italian grammar. Preserve HTML tags, link destinations, and intended line breaks; markup such as `<b>` and `<code>` must remain balanced in the final message.
- **Licenses:** preserve `AGPL-3.0`, `CC BY-SA 4.0`, `CC BY-SA 3.0`, and `CC0`, their versions, attribution names, and destinations. Follow the existing license reply for displayed license titles.

## Maintaining the glossary

When introducing a term, check the relevant runtime messages, Telegram menu descriptions in [`scripts/aws_setup/telegram_setup.py`](../scripts/aws_setup/telegram_setup.py), and localized documentation together. Add the agreed English–Italian mapping here when it is reusable. If an existing translation changes, update the runtime or menu text and the localization inventory in the same change.

For another language, add its own terminology and writing conventions rather than assuming Italian grammar applies. Language selection and fallback behavior remain defined by the implementation; glossary entries alone do not enable a new language.
