import sqlite3
from database.database import get_connection


# ---------------------------------------------------------
# UTENTI
# ---------------------------------------------------------
def get_user_by_username(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, password, role, is_blocked FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row


def get_username(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


# ---------------------------------------------------------
# SCRIVANIE
# ---------------------------------------------------------
def get_free_desks(date):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT desks.id, desks.name
        FROM desks
        WHERE desks.id NOT IN (
            SELECT desk_id FROM bookings WHERE date = ?
        )
    """, (date,))
    rows = c.fetchall()
    conn.close()
    return rows


def get_booked_desks(date):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT desks.id, desks.name
        FROM bookings
        JOIN desks ON desks.id = bookings.desk_id
        WHERE bookings.date = ?
    """, (date,))
    rows = c.fetchall()
    conn.close()
    return rows


# 🔥 NUOVA FUNZIONE: scrivania + username
def get_booked_desks_with_user(date):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT desks.name, users.username
        FROM bookings
        JOIN desks ON desks.id = bookings.desk_id
        JOIN users ON users.id = bookings.user_id
        WHERE bookings.date = ?
    """, (date,))
    rows = c.fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------
# PRENOTAZIONI
# ---------------------------------------------------------
def book_desk(user_id, desk_id, date):
    conn = get_connection()
    c = conn.cursor()

    # verifica se già prenotata
    c.execute("SELECT id FROM bookings WHERE desk_id = ? AND date = ?", (desk_id, date))
    if c.fetchone():
        conn.close()
        return False

    c.execute("INSERT INTO bookings (user_id, desk_id, date) VALUES (?, ?, ?)", (user_id, desk_id, date))
    conn.commit()
    conn.close()
    return True


def cancel_booking(booking_id, is_superuser=False):
    conn = get_connection()
    c = conn.cursor()

    if is_superuser:
        c.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    else:
        c.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))

    conn.commit()
    conn.close()


def get_user_bookings(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT bookings.id, desks.name, bookings.date
        FROM bookings
        JOIN desks ON desks.id = bookings.desk_id
        WHERE bookings.user_id = ?
        ORDER BY bookings.date ASC
    """, (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows
