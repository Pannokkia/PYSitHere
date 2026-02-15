from database.desk_db import get_all_desks, update_desk_position, create_desk, delete_desk

def list_desks():
    return get_all_desks()


def move_desk(desk_id, x, y):
    update_desk_position(desk_id, x, y)


def add_desk(name, x, y):
    create_desk(name, x, y)


def remove_desk(desk_id):
    delete_desk(desk_id)