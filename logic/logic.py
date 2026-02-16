from database.database import get_connection


def get_user_by_username(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, username, password, role, is_blocked FROM users WHERE username = ?",
        (username,)
    )
    row = c.fetchone()
    conn.close()
    return row


def get_free_desks(date):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT id, name
        FROM desks
        WHERE id NOT IN (
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
        SELECT d.name, u.username
        FROM bookings b
        JOIN desks d ON b.desk_id = d.id
        JOIN users u ON b.user_id = u.id
        WHERE b.date = ?
    """, (date,))

    rows = c.fetchall()
    conn.close()
    return rows


def get_booked_desks_with_user(date):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT d.name, u.username
        FROM bookings b
        JOIN desks d ON b.desk_id = d.id
        JOIN users u ON b.user_id = u.id
        WHERE b.date = ?
    """, (date,))

    rows = c.fetchall()
    conn.close()
    return rows


def book_desk(user_id, desk_id, date):
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT id FROM bookings WHERE desk_id = ? AND date = ?", (desk_id, date))
    if c.fetchone():
        conn.close()
        return False

    c.execute("""
        INSERT INTO bookings (user_id, desk_id, date)
        VALUES (?, ?, ?)
    """, (user_id, desk_id, date))

    conn.commit()
    conn.close()
    return True


def cancel_booking(booking_id, is_superuser=False, user_id=None):
    conn = get_connection()
    c = conn.cursor()

    if is_superuser:
        c.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    else:
        c.execute("DELETE FROM bookings WHERE id = ? AND user_id = ?", (booking_id, user_id))

    conn.commit()
    conn.close()


def get_user_bookings(user_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT b.id, d.name, b.date
        FROM bookings b
        JOIN desks d ON b.desk_id = d.id
        WHERE b.user_id = ?
        ORDER BY b.date
    """, (user_id,))

    rows = c.fetchall()
    conn.close()
    return rows