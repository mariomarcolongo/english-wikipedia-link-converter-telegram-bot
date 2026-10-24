# Italian localization

For preferred English–Italian terminology, writing conventions, and content to preserve, see the [localization glossary](LOCALIZATION_GLOSSARY.md).

The bot uses a saved `/language en` or `/language it` preference when present. In automatic mode, it selects Italian when Telegram reports an `it` language code (including regional variants such as `it-IT`). All other or missing language codes use English. Command names and arguments remain unchanged; the privacy-policy link selects the matching language.

The `/privacy` command links to the full Italian policy at [`PRIVACY_POLICY.it.md`](PRIVACY_POLICY.it.md), which is published alongside the English policy. The English and Italian policy texts were aligned with the current queue, operational-state, and log-retention design.

## Changed bot text

| Context | Italian text |
| --- | --- |
| Conversion found | Trovata una pagina di Wikipedia in inglese per |
| Conversion not found | Nessuna pagina di Wikipedia in inglese trovata per |
| Delayed conversion | Elaborato in ritardo mentre il bot si riprendeva da un'interruzione del servizio. |
| Skipped stale private request | Il servizio del bot ha subito un'interruzione temporanea. Questa richiesta meno recente è stata ignorata per evitare messaggi in ritardo; se ti serve ancora, invia di nuovo il link a Wikipedia. |
| Skipped stale group conversions | Il servizio del bot ha subito un'interruzione temporanea. Le conversioni meno recenti sono state ignorate per non riempire la chat; invia di nuovo i link che ti servono ancora. |
| Rate limit | Troppe richieste di conversione. Attendi circa un minuto e riprova. |
| Inline result title, one link | Pagina di Wikipedia in inglese trovata |
| Inline result title, multiple links | Elaborati {count} link di Wikipedia in inglese |
| Inline result description | Tocca per visualizzare i link convertiti |
| Inline temporary error title | Conversione temporaneamente non disponibile |
| Inline temporary error description and message | La ricerca su Wikipedia non è andata a buon fine. Riprova. |
| Inline empty title | Nessun link a Wikipedia |
| Inline empty description | Scrivi o incolla un URL di Wikipedia non in inglese. |
| Inline empty message | Inserisci uno o più URL di pagine Wikipedia non in inglese. |
| Source reply | Puoi trovare qui il codice sorgente:\n{url}\n\nContribuisci liberamente o crea una tua versione con un fork! |
| License heading | Licenza |
| License text | Il codice in questo repository è distribuito con la licenza GNU Affero General Public License v3.0 (AGPL-3.0), salvo diversa indicazione. |
| Icon license text | L'icona del bot Telegram English Wikipedia Link Converter è distribuita con la licenza Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0). Consulta la directory dell'icona per maggiori dettagli. |
| Image credits heading and introduction | Crediti delle immagini — L'icona del bot include immagini provenienti dalle seguenti fonti: |
| Wikipedia logo credit | Logo di Wikipedia — Versione 2 di Vanished user 24kwjf10h32h, versione 1 di Nohat (ideata da Paullusmagnus); Wikimedia, utilizzata con licenza Creative Commons Attribuzione-Condividi allo stesso modo 3.0 non adattata (CC BY-SA 3.0); è disponibile qui su Wikimedia Commons. |
| Left arrow credit | Freccia a sinistra — di Icons8, distribuita con licenza CC0 e disponibile qui su Wikimedia Commons. |
| Healthy status | ✅ Operativo |
| Unhealthy status | ⚠️ Rilevata un'interruzione del servizio |
| Unknown status | ❔ Stato non ancora disponibile |
| Time since check, one second | {count} secondo fa |
| Time since check, zero or multiple seconds | {count} secondi fa |
| Unknown value | sconosciuto |
| Status labels | Stato: · Ultimo controllo esterno: · Aggiornamenti Telegram in attesa: · Elementi in coda: · Versione: |
| Status channel link | Aggiornamenti sullo stato del servizio |
| Greeting | Ciao {name}! |
| Bot introduction | Sono il bot English Wikipedia Link Converter. |
| Bot description | Converto i link a pagine Wikipedia in altre lingue nel corrispondente link alla versione inglese. |
| Commands heading | Comandi: |
| `/help` description | Mostra queste istruzioni |
| `/status` description | Controlla lo stato del servizio del bot |
| `/source` description | Mostra il link al codice sorgente del bot |
| `/license` description | Mostra le licenze e i crediti delle immagini |
| `/privacy` description | Mostra l'informativa sulla privacy del bot |
| `/language` description | Imposta o visualizza la preferenza della lingua |
| Current language prompt | Preferenza della lingua: {language}. |
| Language choices prompt | Scegli /language auto, /language en oppure /language it. |
| Automatic option name | Automatica (lingua di Telegram) |
| English option name | Inglese |
| Italian option name | Italiano |
| Language change confirmation | Lingua impostata su {language}. |
| Automatic language confirmation | Lingua impostata su automatica. Userò la lingua di Telegram quando disponibile; altrimenti userò l'inglese. |
| Preference save error | Non riesco a salvare la preferenza della lingua. Riprova più tardi. |
| Usage heading | Come usarmi: |
| Send-link instruction | Inviami un link a una pagina Wikipedia in un'altra lingua. |
| Group instruction | Aggiungimi a un gruppo per convertire i link condivisi dai partecipanti. |
| Inline instruction | Per usare la modalità inline, digita `@{username}` seguito dai link. |
| Service notices label and link | Avvisi sul servizio: · canale degli aggiornamenti |
| Add-to-group button | Aggiungimi al tuo gruppo |
| Service-status button | Stato del servizio |
| Privacy reply label | Informativa sulla privacy: |

### Complete license reply text

This is the complete Italian text shown by `/license` (the linked phrases point to the same license and attribution pages as in English):

> **Licenza**
>
> Il codice in questo repository è distribuito con la licenza GNU Affero General Public License v3.0 (AGPL-3.0), salvo diversa indicazione.
>
> L'icona del bot Telegram **English Wikipedia Link Converter** è distribuita con la licenza Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0). Consulta la directory dell'icona per maggiori dettagli.
>
> **Crediti delle immagini**
>
> L'icona del bot include immagini provenienti dalle seguenti fonti:
>
> - **Logo di Wikipedia**, versione 2 di Vanished user 24kwjf10h32h, versione 1 di Nohat (ideata da Paullusmagnus); Wikimedia, utilizzata con licenza Creative Commons Attribuzione-Condividi allo stesso modo 3.0 non adattata (CC BY-SA 3.0); è disponibile qui su Wikimedia Commons.
> - **Freccia a sinistra**, di Icons8, distribuita con licenza CC0 e disponibile qui su Wikimedia Commons.

## Telegram command menu

The Italian command menu uses the same command names as the English menu:

| Command | Italian description |
| --- | --- |
| `/start` | Avvia il bot e mostra le istruzioni |
| `/help` | Mostra le istruzioni per l'uso |
| `/status` | Controlla lo stato del servizio |
| `/source` | Visualizza il codice sorgente |
| `/license` | Visualizza licenze e crediti delle immagini |
| `/privacy` | Visualizza l'informativa sulla privacy |
| `/language` | Imposta o visualizza la preferenza della lingua |

## Privacy policy

The `/language` command accepts `/language en`, `/language it`, and `/language auto`. Choices are stored per Telegram user in DynamoDB and expire one year after being set. `auto` removes the saved choice. The full Italian privacy policy is maintained in [`PRIVACY_POLICY.it.md`](PRIVACY_POLICY.it.md). The `/privacy` command preserves the English policy URL for English users and selects the `.it.html` page for Italian users. GitHub Pages publishes the repository's `docs` directory, so the Italian Markdown file is published as `PRIVACY_POLICY.it.html` after the branch is merged and Pages rebuilds.
