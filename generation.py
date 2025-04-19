import os
import random
from datetime import datetime, timedelta
import mysql.connector
import time


def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="rootpassword",
        database="forum_db",
    )

NUM_DAYS = 30
NUM_USERS = 20

ACTIONS = [
    "first_visit",
    "register",
    "login",
    "logout",
    "create_theme",
    "visit_theme",
    "delete_theme",
    "post_message",
]

OUTPUT_DIR = "data"


def ensure_output_dir() -> None:
    """
    Создаёт папку для сохранения файлов, если её ещё нет.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_users() -> list[str]:
    """
    Генерирует SQL-запросы для создания пользователей,
    включая как обычных, так и анонимных.
    """
    users_sql = []
    for user_id in range(1, NUM_USERS + 1):
        is_anon = random.choice([False, False, False, True])
        username = f"user{user_id}" if not is_anon else None
        username_sql = f"'{username}'" if username else "NULL"
        users_sql.append(
            f"INSERT INTO users (id, username, is_anonymous) "
            f"VALUES ({user_id}, {username_sql}, {str(is_anon).upper()});"
        )
    return users_sql


def generate_logs_and_data() -> (
    tuple[list[str], list[str], list[str], list[str]]
):
    """
    Генерирует SQL-запросы для логов, тем и сообщений за месяц.
    Возвращает: (логи, темы, сообщения, пользователи)
    """
    users = list(range(1, NUM_USERS + 1))
    themes_created = []
    logs_sql, themes_sql, messages_sql = [], [], []

    theme_id = 1
    message_id = 1
    log_id = 1
    start_date = datetime(2025, 4, 1)

    for day_offset in range(NUM_DAYS):
        day = start_date + timedelta(days=day_offset)

        for _ in range(2):
            timestamp = day + timedelta(seconds=random.randint(0, 86400))
            logs_sql.append(
                f"INSERT INTO logs (id, user_id, action_type, object_type, object_id, "
                f"description, server_response, created_at) "
                f"VALUES ({log_id}, NULL, 'create_theme', 'theme', NULL, "
                f"'create_theme by anonymous - error', 'error', '{timestamp}');"
            )
            log_id += 1

        for action in ACTIONS:
            count = random.randint(5, 10)

            for _ in range(count):
                timestamp = day + timedelta(seconds=random.randint(0, 86400))
                is_anon = action == "post_message" and random.choice(
                    [True, False]
                )
                user_id = random.choice(users) if not is_anon else None
                server_response = "success"
                object_id = "NULL"
                object_type = "NULL"
                description = f"{action} action"

                if action == "create_theme":
                    if user_id is None:
                        continue
                    object_id = theme_id
                    object_type = "'theme'"
                    themes_sql.append(
                        f"INSERT INTO themes (id, title, created_by, created_at) "
                        f"VALUES ({theme_id}, 'Theme {theme_id}', {user_id}, '{timestamp}');"
                    )
                    themes_created.append(theme_id)
                    theme_id += 1

                elif (
                    action in ["visit_theme", "delete_theme"]
                    and themes_created
                ):
                    object_id = random.choice(themes_created)
                    object_type = "'theme'"

                elif action == "post_message":
                    if themes_created:
                        theme_for_msg = random.choice(themes_created)
                        object_id = message_id
                        object_type = "'message'"
                        creator = "NULL" if is_anon else user_id
                        messages_sql.append(
                            f"INSERT INTO messages (id, text, created_by, theme_id, created_at) "
                            f"VALUES ({message_id}, 'Message {message_id}', "
                            f"{creator}, {theme_for_msg}, '{timestamp}');"
                        )
                        message_id += 1

                user_id_sql = str(user_id) if user_id is not None else "NULL"

                logs_sql.append(
                    f"INSERT INTO logs (id, user_id, action_type, object_type, object_id, "
                    f"description, server_response, created_at) "
                    f"VALUES ({log_id}, {user_id_sql}, '{action}', {object_type}, "
                    f"{object_id}, '{description}', '{server_response}', '{timestamp}');"
                )
                log_id += 1

    users_sql = generate_users()
    return logs_sql, themes_sql, messages_sql, users_sql


def write_sql_file(filename: str, sql_lines: list[str]) -> None:
    """
    Сохраняет список SQL-запросов в файл.
    """
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(sql_lines))


def main() -> None:
    """
    Точка входа: генерирует и сохраняет SQL-файлы.
    """
    ensure_output_dir()
    logs_sql, themes_sql, messages_sql, users_sql = generate_logs_and_data()
    write_sql_file("insert_users.sql", users_sql)
    write_sql_file("insert_themes.sql", themes_sql)
    write_sql_file("insert_messages.sql", messages_sql)
    write_sql_file("insert_logs.sql", logs_sql)


    conn = create_connection()
    cursor = conn.cursor()

    print("Генерация и вставка данных...")

    cursor.execute("DELETE FROM messages")
    cursor.execute("DELETE FROM logs")
    cursor.execute("DELETE FROM themes")
    cursor.execute("DELETE FROM users")

    logs, themes, messages, users = generate_logs_and_data()

    for query in users:
        cursor.execute(query)
    for query in themes:
        cursor.execute(query)
    for query in messages:
        cursor.execute(query)
    for query in logs:
        cursor.execute(query)

    conn.commit()
    cursor.close()
    conn.close()
    print("Данные успешно загружены!")

if __name__ == "__main__":
    main()