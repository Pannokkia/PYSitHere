# 🖥️ PySitHere – Desk Booking System
Sistema completo per la gestione delle prenotazioni delle postazioni in ufficio.  
Applicazione desktop sviluppata in **Python** con interfaccia moderna basata su **CustomTkinter**.


---

## ✨ Funzionalità principali

### 👤 Gestione Utenti
- Login con ruoli: **utente** e **superuser**
- Creazione, modifica e cancellazione utenti
- Blocco/sblocco account
- Reset password
- Ricerca utenti + filtri
- Paginazione lista utenti

---

### 🗺️ Prenotazione Scrivanie
- Selezione del **giorno** tramite calendario
- Filtri avanzati:
  - **Giorno**
  - **Settimana**
  - **Mese**
- Mini‑mappa grafica del piano:
  - scrivanie **verdi** → libere  
  - scrivanie **rosse** → occupate  
- Tooltip informativi (nome, stato, giorno)
- **Zoom** della mini‑mappa con rotellina del mouse
- **Selezione scrivania cliccando sulla mini‑mappa**
- Lista prenotazioni personali con data e ID
- Prenotazione e cancellazione con un click

---

### 🏢 Gestione Uffici e Postazioni
- Editor grafico delle scrivanie:
  - aggiunta scrivania
  - eliminazione scrivania
  - trascinamento per riposizionamento
- Salvataggio automatico nel file `config.json`
- Supporto multi‑ufficio e multi‑piano

---

### 🗄️ Database
- SQLite integrato
- Tabelle:
  - `users`
  - `desks`
  - `bookings`
- Migrazione automatica (es. aggiunta colonna `is_blocked`)
- Creazione automatica superuser `admin/admin` se mancante

---

## 🧩 Configurazione Uffici e Postazioni (config.json)

Il file `config.json` definisce:

- uffici
- piani
- scrivanie
- coordinate grafiche delle postazioni

### Esempio:

```json
{
  "offices": [
    {
      "name": "Sede MI",
      "floors": [
        {
          "name": "Piano 1",
          "desks": [
            { "name": "Desk 1", "x": 120, "y": 80 },
            { "name": "Desk 2", "x": 260, "y": 80 },
            { "name": "Desk 3", "x": 120, "y": 200 },
            { "name": "Desk 4", "x": 260, "y": 200 }
          ]
        }
      ]
    }
  ]
}


📦 Moduli Python richiesti
Installazione:

pip install customtkinter tkcalendar pillow

Moduli utilizzati:

    - customtkinter

    - tkcalendar

    - Pillow

    - sqlite3 (standard)

    - json (standard)


▶️ Avvio dell’applicazione
python main.py


User definded:

admin --> admin
rossi --> prova
verdi -->prova