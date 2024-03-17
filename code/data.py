import sqlite3
from config import DB_NAME

# todo: переделать

settings_dict = {
    'subject': [
        'Русский',
        'Математика'
    ],
    'difficulty': [
        'новичок',
        'любитель',
        'профи'
    ]
}


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
        return e

    else:
        result = cursor.fetchall()
        connection.close()
        return result


def add_new_user(users_data: tuple, table: str, columns: list):
    sql_query = (
        f'INSERT INTO {table} '
        f'({', '.join(columns)}) '
        f'VALUES ({'?, ' * (len(columns) - 1) + '?'});')
    execute_query(sql_query, users_data)


def is_user_in_table(user_id: int, table: str) -> bool:
    sql_query = (
        f'SELECT * '
        f'FROM {table} '
        f'WHERE user_id = ?;'
    )
    return bool(execute_query(sql_query, (user_id,)))


def update_data(user_id: int, column_name: str, url: str, new_value: any, table: str):
    if is_user_in_table(user_id, table):
        sql_query = (
            f'UPDATE {table} '
            f'SET {column_name} = ? '
            f'WHERE user_id = ? '
            f'AND url = ?;'
        )

        execute_query(sql_query, (new_value, user_id, url))
        return True
    else:
        return False


def get_user_data(user_id: int, table: str):
    if is_user_in_table(user_id, table):
        sql_query = (
            f'SELECT * '
            f'FROM {table} '
            f'WHERE user_id = {user_id} '
        )
        row = execute_query(sql_query)[0]

        return row


def create_users_data_table():
    execute_query('''CREATE TABLE IF NOT EXISTS users_data (
                                id INTEGER PRIMARY KEY,
                                user_id INTEGER,
                                hero TEXT,
                                
                                story TEXT,
                                session INTEGER);''')


def get_table_data(table):
    sql_query = (
        f'SELECT * '
        f'FROM {table};'
    )
    res = execute_query(sql_query)
    return res


def drop(table):
    execute_query(f'DROP TABLE {table};')


def delete_user(user_id: int, table: str):
    if is_user_in_table(user_id, table):
        sql_query = (f'DELETE '
                     f'FROM {table} '
                     f'WHERE user_id = ?')
        execute_query(sql_query, (user_id,))


