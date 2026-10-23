# Informativa sulla privacy

_Ultimo aggiornamento: 23 ottobre 2026_

Questa informativa descrive come il **bot English Wikipedia Link Converter** ("noi" o il "Bot") tratta le informazioni quando interagisci con il Bot su Telegram.

Questa informativa integra l'[Informativa standard sulla privacy dei bot di Telegram](https://telegram.org/privacy-tpa). Si applicano anche i termini e le definizioni generali di Telegram.

## 1. Informazioni trattate

- **Dati degli aggiornamenti Telegram:** Telegram invia al Bot il messaggio o la ricerca inline necessari per fornire la funzione richiesta. Per convertire un link, questi dati possono includere l'URL Wikipedia inviato e il titolo dell'articolo. Il Bot non conserva la cronologia delle chat.
- **Identificativi e contatori operativi:** il Bot usa gli identificativi Telegram dell'utente, della chat e dell'aggiornamento per applicare limiti d'uso, evitare elaborazioni duplicate e gestire gli avvisi di ripristino. Questi dati sono conservati in DynamoDB e scadono automaticamente. La tabella non conserva il testo dei messaggi.
- **Preferenza della lingua:** se scegli l'inglese o l'italiano con `/language en` o `/language it`, il Bot salva in DynamoDB il tuo ID Telegram e la lingua scelta, con una scadenza impostata a un anno dall'ultima modifica. La rimozione automatica del record può richiedere altro tempo. `/language auto` elimina la preferenza salvata e ripristina la selezione automatica basata sulla lingua di Telegram.
- **Dati temporanei di elaborazione:** gli aggiornamenti accettati per la conversione possono essere mantenuti temporaneamente in Amazon SQS in attesa di elaborazione o di un nuovo tentativo. Gli aggiornamenti che continuano a non riuscire possono essere spostati in una coda di messaggi non recapitabili per la gestione operativa.
- **Log:** il Bot registra avvisi ed errori operativi. È progettato per non registrare il testo dei messaggi, i nomi utente, i token del bot o i segreti del webhook.

## 2. Uso delle informazioni

Il Bot usa i link Wikipedia e i titoli degli articoli inviati per trovare le pagine corrispondenti su Wikipedia in inglese. Usa gli identificativi operativi per fornire il servizio in modo affidabile e limitare gli abusi.

## 3. Fornitori di servizi

- **Telegram** trasmette gli aggiornamenti e i messaggi da e verso il Bot.
- **Amazon Web Services (AWS)** esegue il Bot e i servizi di coda, stato operativo e monitoraggio. AWS può trattare i dati di servizio nell'ambito della gestione di tali servizi.
- **L'API pubblica di Wikipedia della Wikimedia Foundation** riceve il titolo dell'articolo inviato e l'edizione linguistica per la ricerca richiesta. Il Bot non invia a Wikipedia gli identificativi Telegram dell'utente o della chat.

## 4. Conservazione

Gli aggiornamenti nella coda di elaborazione sono conservati solo per il tempo necessario all'elaborazione, ai nuovi tentativi o alla gestione degli errori. I record operativi di DynamoDB hanno una scadenza automatica. I log di CloudWatch sono configurati per una conservazione di 14 giorni. Telegram e i servizi di terze parti possono conservare i dati secondo le proprie informative.

## 5. Condivisione e sicurezza

Non vendiamo informazioni personali. I fornitori descritti sopra trattano le informazioni per fornire e gestire il Bot. Le connessioni a Telegram e Wikipedia usano HTTPS. Non inviare al Bot informazioni personali sensibili.

## 6. Scelte e richieste

Puoi smettere di usare il Bot in qualsiasi momento. Per domande o richieste relative alla privacy, apri una segnalazione nel [tracker GitHub del progetto](https://github.com/mariomarcolongo/english-wikipedia-link-converter-telegram-bot/issues).

## Dichiarazione di non affiliazione

Questo Bot è un servizio indipendente e non è gestito, approvato o affiliato con Telegram Messenger Inc. o la Wikimedia Foundation.
