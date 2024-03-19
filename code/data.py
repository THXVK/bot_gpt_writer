import sqlite3
from config import DB_NAME

# todo: переделать

settings_dict = {

}

characters_list = ['олег', 'мамут', '?']


def create_db():
    connection = sqlite3.connect(DB_NAME)
    connection.close()


def execute_query(query: str, data: tuple | None = None, db_name: str = DB_NAME):
    try:
        connection = sqlite3.connect(db_name, check_same_thread=False)
        cursor = connection.cursor()

        if data:
            cursor.execute(query, data)
            connection.commit()
        else:
            cursor.execute(query)

    except sqlite3.Error as e:
        # todo: логи
        return e

    else:
        result = cursor.fetchall()
        connection.close()
        return result


def create_users_data_table():
    sql_query = (
        f"CREATE TABLE IF NOT EXISTS users_data "
        f"(id INTEGER PRIMARY KEY, "
        f"user_id INTEGER, "
        f"sessions INTEGER, "
        f"tokens INTEGER, "
        f" hero TEXT, "
        f"location TEXT, "
        f"story TEXT);"
    )
    execute_query(sql_query)


def add_new_user(user_id: int):
    if not is_user_in_table(user_id):
        sql_query = (
            f"INSERT INTO users_data "
            f"(user_id, sessions) "
            f"VALUES (?, 0);"
        )

        execute_query(sql_query, (user_id,))
        return True
    else:
        return False


def is_user_in_table(user_id: int) -> bool:
    sql_query = (
        f'SELECT * '
        f'FROM users_data '
        f'WHERE user_id = ?;'
    )
    return bool(execute_query(sql_query, (user_id,)))


def get_user_data(user_id: int):
    if is_user_in_table(user_id):
        sql_query = (
            f'SELECT * '
            f'FROM users_data '
            f'WHERE user_id = {user_id} '
        )
        row = execute_query(sql_query)[0]

        return row


def update_row(user_id: int, column_name: str, new_value: str | int | None) -> bool:
    if is_user_in_table(user_id):
        sql_query = (
            f"UPDATE users_data "
            f"SET {column_name} = ? "
            f"WHERE user_id = ?;"
        )

        execute_query(sql_query, (new_value, user_id))
        return True
    else:
        return False


def get_table_data():
    sql_query = (
        f'SELECT * '
        f'FROM users_data;'
    )
    res = execute_query(sql_query)
    return res


def drop(table):
    execute_query(f'DROP TABLE {table};')


def delete_user(user_id: int):
    if is_user_in_table(user_id):
        sql_query = (
            f"DELETE "
            f"FROM users_data "
            f"WHERE user_id = ?;"
        )

        execute_query(sql_query, (user_id,))
        return True
    else:
        return False


create_db()
create_users_data_table()
