from database.database import get_connection

def authenticate(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, role FROM users WHERE username=? AND password=?",
              (username, password))
    result = c.fetchone()
    conn.close()
    return result


def create_user(username, password, role="user"):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
              (username, password, role))
    conn.commit()
    conn.close()


def get_all_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, role FROM users")
    users = c.fetchall()
    conn.close()
    return users


def delete_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()