import sqlite3
from config.config_loader import load_config

DB_NAME = "desks.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # ---------------------------------------------------------
    # TABELLA SCRIVANIE
    # ---------------------------------------------------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS desks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL
        )
    """)

    # ---------------------------------------------------------
    # TABELLA UTENTI (con is_blocked)
    # ---------------------------------------------------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            is_blocked INTEGER NOT NULL DEFAULT 0
        )
    """)

    # ---------------------------------------------------------
    # MIGRAZIONE AUTOMATICA: aggiunge is_blocked se manca
    # ---------------------------------------------------------
    try:
        c.execute("SELECT is_blocked FROM users LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE users ADD COLUMN is_blocked INTEGER DEFAULT 0")

    # ---------------------------------------------------------
    # TABELLA PRENOTAZIONI
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # CREA SUPERUSER SE NON ESISTE
    # ---------------------------------------------------------
    c.execute("SELECT COUNT(*) FROM users WHERE role='superuser'")
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO users (username, password, role, is_blocked)
            VALUES ('admin', 'admin', 'superuser', 0)
        """)

    # ---------------------------------------------------------
    # CREA SCRIVANIE DA CONFIG.JSON
    # ---------------------------------------------------------
    config = load_config()
    offices = config["offices"]

    c.execute("SELECT COUNT(*) FROM desks")
    if c.fetchone()[0] == 0:
        for office in offices:
            for floor in office["floors"]:
                for d in floor["desks"]:
                    c.execute("""
                        INSERT INTO desks (name, x, y)
                        VALUES (?, ?, ?)
                    """, (d["name"], d["x"], d["y"]))

    conn.commit()
    conn.close()