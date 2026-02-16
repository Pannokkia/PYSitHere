import sqlite3
import os
import json

# Percorso assoluto della ROOT del progetto (PYSitHere)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Percorso assoluto della cartella "database"
DB_DIR = os.path.join(ROOT_DIR, "database")

# Percorso assoluto del file desks.db
DB_PATH = os.path.join(DB_DIR, "desks.db")

# Percorso del config.json
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "config.json")


def get_connection():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    return sqlite3.connect(DB_PATH)


def init_db():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    first_creation = not os.path.exists(DB_PATH)

    conn = get_connection()
    c = conn.cursor()

    # -------------------------
    # TABELLA UTENTI
    # -------------------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            is_blocked INTEGER NOT NULL DEFAULT 0
        )
    """)

    # -------------------------
    # TABELLA PRENOTAZIONI
    # -------------------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            desk_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(desk_id) REFERENCES desks(id)
        )
    """)

    # -------------------------
    # TABELLA SCRIVANIE
    # -------------------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS desks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            office_id TEXT NOT NULL,
            floor_name TEXT NOT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL
        )
    """)

    # -------------------------
    # CREA ADMIN SE NON ESISTE
    # -------------------------
    c.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO users (username, password, role, is_blocked)
            VALUES ('admin', 'admin', 'admin', 0)
        """)
        print("Creato utente admin (username: admin, password: admin)")

    # -------------------------
    # IMPORTA SCRIVANIE DA config.json
    # -------------------------
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        for office in cfg.get("offices", []):
            office_id = office["id"]

            for floor in office.get("floors", []):
                floor_name = floor["name"]

                for desk in floor.get("desks", []):
                    # Evita duplicati
                    c.execute("""
                        SELECT COUNT(*) FROM desks
                        WHERE name = ? AND office_id = ? AND floor_name = ?
                    """, (desk["name"], office_id, floor_name))

                    if c.fetchone()[0] == 0:
                        c.execute("""
                            INSERT INTO desks (name, office_id, floor_name, x, y)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            desk["name"],
                            office_id,
                            floor_name,
                            desk["x"],
                            desk["y"]
                        ))

        print("Scrivanie sincronizzate con config.json")

    conn.commit()
    conn.close()

    print(f"DB inizializzato in: {DB_PATH}")