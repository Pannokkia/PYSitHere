from database.database import get_connection

def get_all_desks():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, x, y FROM desks")
    desks = c.fetchall()
    conn.close()
    return desks


def update_desk_position(desk_id, x, y):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE desks SET x=?, y=? WHERE id=?", (x, y, desk_id))
    conn.commit()
    conn.close()


def create_desk(name, x, y):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO desks (name, x, y) VALUES (?, ?, ?)", (name, x, y))
    conn.commit()
    conn.close()


def delete_desk(desk_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM desks WHERE id=?", (desk_id,))
    conn.commit()
    conn.close()