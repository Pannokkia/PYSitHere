from database.database import get_connection


# ---------------------------------------------------------
# SCRIVANIE LIBERE / OCCUPATE
# ---------------------------------------------------------
def get_free_desks(date_str: str):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT d.id, d.name
        FROM desks d
        WHERE d.id NOT IN (
            SELECT desk_id FROM bookings WHERE date = ?
        )
        ORDER BY d.name
    """, (date_str,))

    rows = c.fetchall()
    conn.close()
    return rows


def get_booked_desks(date_str: str):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT b.desk_id, d.name
        FROM bookings b
        JOIN desks d ON b.desk_id = d.id
        WHERE b.date = ?
        ORDER BY d.name
    """, (date_str,))

    rows = c.fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------
# PRENOTAZIONI
# ---------------------------------------------------------
def book_desk(user_id: int, desk_id: int, date_str: str):
    conn = get_connection()
    c = conn.cursor()

    # evita doppie prenotazioni
    c.execute("""
        SELECT COUNT(*) FROM bookings
        WHERE desk_id = ? AND date = ?
    """, (desk_id, date_str))
    if c.fetchone()[0] > 0:
        conn.close()
        return False

    c.execute("""
        INSERT INTO bookings (user_id, desk_id, date)
        VALUES (?, ?, ?)
    """, (user_id, desk_id, date_str))

    conn.commit()
    conn.close()
    return True


def cancel_booking(booking_id: int, is_superuser: bool = False):
    conn = get_connection()
    c = conn.cursor()

    c.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))

    conn.commit()
    conn.close()


def get_user_bookings(user_id: int):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT b.id, d.name, b.date
        FROM bookings b
        JOIN desks d ON b.desk_id = d.id
        WHERE b.user_id = ?
        ORDER BY b.date DESC
    """, (user_id,))

    rows = c.fetchall()
    conn.close()
    return rows