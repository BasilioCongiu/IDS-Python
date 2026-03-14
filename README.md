Obiettivo del progetto
Lo scopo del progetto è sviluppare un Intrusion Detection System (IDS) in grado di analizzare il traffico di rete in tempo reale.
Il sistema intercetta i pacchetti che transitano sulla rete, ne estrae le informazioni principali (metadati) e le rende visibili tramite una dashboard web interattiva.
L'obiettivo è creare uno strumento che permetta di:
    • osservare il traffico di rete live
    • comprendere chi comunica con chi
    • visualizzare i dati senza dover usare il terminale
Per realizzare questo sistema ho progettato un'architettura modulare che separa le tre fasi principali:
    1. Cattura dei pacchetti
    2. Analisi dei pacchetti
    3. Visualizzazione tramite web app

Architettura del sistema
Per mantenere il codice organizzato e scalabile ho applicato il principio di Separation of Concerns, dividendo il progetto in tre moduli indipendenti.
Network Traffic
      │
      ▼
+-------------+
| capture.py  |
| Packet sniff|
+-------------+
      │
      ▼
+-------------+
|  Queue      |
| Buffer      |
+-------------+
      │
      ▼
+-------------+
| analyzer.py |
| Metadata    |
| extraction  |
+-------------+
      │
      ▼
+-------------+
|   app.py    |
| Streamlit   |
| Dashboard   |
+-------------+
Moduli principali
capture.py
    • intercetta i pacchetti di rete
    • utilizza Scapy per effettuare lo sniffing
analyzer.py
    • elabora i pacchetti catturati
    • estrae metadati come:
        ◦ IP sorgente
        ◦ IP destinazione
        ◦ protocollo
        ◦ dimensione del pacchetto
app.py
    • interfaccia web sviluppata con Streamlit
    • visualizza i dati in tempo reale tramite dashboard

Cattura dei pacchetti (Packet Sniffing)
Il cuore del progetto è il packet sniffing, ovvero l'intercettazione passiva del traffico di rete.
Normalmente, quando la scheda di rete riceve un pacchetto, il sistema operativo lo invia direttamente allo stack TCP/IP per l'elaborazione.
Utilizzando Scapy, è possibile intercettare una copia di questi pacchetti mentre transitano sulla rete.
In pratica il sistema:
    1. ascolta il traffico sull'interfaccia di rete
    2. riceve una copia dei pacchetti
    3. li invia al modulo di analisi
Questo processo avviene in modo passivo, senza interferire con la comunicazione tra i dispositivi.

Multi-Threading e gestione della concorrenza
La cattura dei pacchetti è un'operazione continua e non deve essere interrotta.
Se la cattura e la visualizzazione fossero eseguite nello stesso flusso di esecuzione, l'interfaccia web potrebbe bloccare il sistema causando la perdita di pacchetti.
Per evitare questo problema ho utilizzato il multi-threading.
Un thread è un flusso di esecuzione indipendente all'interno dello stesso programma.
Nel progetto vengono utilizzati due thread principali:
    • Capture Thread → cattura i pacchetti
    • Analyzer Thread → analizza i pacchetti

Race Conditions e Queue Thread-Safe
Quando più thread accedono alla stessa risorsa si può verificare una race condition: un errore causato dall'accesso simultaneo ai dati.
Per evitare questo problema ho utilizzato una Queue thread-safe.
La Queue funge da buffer intermedio tra cattura e analisi:
Capture Thread  →  Queue  →  Analyzer Thread
Questa struttura garantisce che:
    • i pacchetti vengano inseriti in modo sicuro
    • i dati non vengano corrotti
    • i thread non interferiscano tra loro

Gestione dello stato in Streamlit
Un problema tipico di Streamlit è che lo script Python viene rieseguito ogni volta che l'utente interagisce con la pagina.
Senza una gestione dello stato, questo comportamento causerebbe il riavvio continuo dei thread di cattura.
Per risolvere il problema ho utilizzato st.session_state, che permette di mantenere oggetti persistenti durante la sessione utente.
In questo modo:
    • i thread restano attivi
    • la cattura continua
    • la dashboard può aggiornarsi senza interrompere il sistema.

Astrazione delle interfacce di rete
Durante lo sviluppo si è verificato un errore legato alla selezione dell'interfaccia di rete:
ValueError: Interface 'any' not found
Questo accade perché "any" non rappresenta una vera interfaccia di rete ma una pseudo-interfaccia utilizzata da alcuni strumenti di sniffing.
Per rendere il sistema indipendente dall'hardware ho implementato un layer di Network Abstraction.
Il sistema interroga automaticamente il sistema operativo per individuare l'interfaccia di rete attiva (quella usata per il routing) utilizzando funzioni come:
    • get_default_iface()
In questo modo il software può funzionare su macchine diverse senza configurazioni manuali.

Gestione della memoria – Sliding Window
Un sistema di monitoraggio che rimane attivo a lungo rischia di accumulare dati indefinitamente, causando un consumo eccessivo di memoria.
Per evitare questo problema ho implementato una Sliding Window.
Il sistema mantiene in memoria solo gli ultimi N pacchetti analizzati.
Quando arriva un nuovo pacchetto e il buffer è pieno:
    • il pacchetto più vecchio viene rimosso
    • il nuovo pacchetto viene aggiunto
Questo mantiene il sistema in uno stato stabile con uso di memoria costante nel tempo.

Tecnologie utilizzate
    • Python
    • Scapy → packet sniffing e manipolazione dei pacchetti
    • Streamlit → dashboard web interattiva
    • Threading → esecuzione concorrente
    • Queue → comunicazione thread-safe