# InfoNav
Progetto per lavoro di tesi in Metodi e Modelli per la Sicurezza delle Applicazioni


## Abstract
All’interno di una città la criminalità non è equamente distribuita, ma esistono zone dove la frequenza di atti delittuosi è maggiore e zone dove, invece, la frequenza risulta di molto inferiore. L’obiettivo è quindi utilizzare informazioni presenti sul web, come open data e articoli di giornale, per determinare quali strade sono più pericolose calcolando il tasso di criminalità per esse e disegnarle su una mappa per restituire un output di facile lettura e consentire a chiunque di poterlo interpretare facilmente, ottenendo uno strumento usabile. L’esperimento è stato condotto sulla città di Bari.


## Requisiti
* Python 3.8 o versioni successive:
    > scarica [Python](https://www.python.org/downloads/)
* Chiave Google API
    > se non l'avete già ecco una guida di [come ottenere una chiave](https://www.webipedia.it/web-development/google-api-key-mappe/#:~:text=Come%20ottenere%20una%20Google%20API%20Key,-L%27API%20key&text=Crea%20un%20nuovo%20progetto%2C%20assegnagli,sul%20tuo%20sito%20in%20WordPress.)
* Un web browser qualsiasi


### Azioni necessarie
Sostituire tutte le occorrenze in tutti i file dove si trova la stringa `#YourAPI-Key` con la vostra Chiave API di Google

## Avvio
1. Run del file `app.py`
2. Utilizzare il web browser per visitare il link `localhost:5000`
