from database.database import get_connection


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
def login(username, password):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT id, role, is_blocked 
        FROM users 
        WHERE username=? AND password=?
    """, (username, password))

    row = c.fetchone()
    conn.close()

    if not row:
        return None

    user_id, role, is_blocked = row

    if is_blocked == 1:
        return None  # utente bloccato

    return user_id, role


# ---------------------------------------------------------
# LISTA UTENTI
# ---------------------------------------------------------
def list_users():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT id, username, role, is_blocked
        FROM users
        ORDER BY username ASC
    """)

    rows = c.fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------
# REGISTRAZIONE UTENTE
# ---------------------------------------------------------
def register_user(username, password, role="user"):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO users (username, password, role, is_blocked)
        VALUES (?, ?, ?, 0)
    """, (username, password, role))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# RIMOZIONE UTENTE
# ---------------------------------------------------------
def remove_user(user_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("DELETE FROM users WHERE id=?", (user_id,))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# CAMBIO PASSWORD
# ---------------------------------------------------------
def update_password(user_id, new_password):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        UPDATE users 
        SET password=? 
        WHERE id=?
    """, (new_password, user_id))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# BLOCCO / SBLOCCO ACCOUNT
# ---------------------------------------------------------
def set_block_status(user_id, block):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        UPDATE users 
        SET is_blocked=? 
        WHERE id=?
    """, (1 if block else 0, user_id))

    conn.commit()
    conn.close()