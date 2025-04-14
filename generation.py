import mysql.connector
import random
import string
from datetime import datetime, timedelta

# Параметры подключения к базе данных MySQL
DB_PARAMS = {
    'host': 'localhost',
    'user': 'user',  # Замените на ваше имя пользователя MySQL
    'password': 'password',  # Замените на ваш пароль MySQL
    'database': 'forum_db'  # Название вашей базы данных
}

# Функция для подключения к базе данных
def connect_db():
    try:
        conn = mysql.connector.connect(**DB_PARAMS)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Генерация случайной строки
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Генерация данных
def generate_data():
    conn = connect_db()
    if conn is None:
        return

    cur = conn.cursor()

    # Генерация данных пользователей
    users = [(random_string(10), f"{random_string(10)}@example.com", random_string(32), datetime.now() - timedelta(days=random.randint(0, 365))) for _ in range(100)]
    # Генерация данных тем
    topics = [(random.randint(1, 100), random_string(20), datetime.now() - timedelta(days=random.randint(0, 30))) for _ in range(50)]
    # Генерация данных сообщений
    messages = [(random.randint(1, 50), random.randint(1, 100), random_string(100), datetime.now() - timedelta(days=random.randint(0, 30))) for _ in range(200)]
    # Генерация данных логов
    logs = [(random.choice([None, random.randint(1, 100)]), random_string(64), random.choice(['first_visit', 'register', 'login', 'logout', 'create_topic', 'view_topic', 'delete_topic', 'post_message']), random.choice([random.randint(1, 50), None]), random.choice(['topic', 'message', None]), f"192.168.1.{random.randint(1, 254)}", random_string(20), datetime.now() - timedelta(days=random.randint(0, 30))) for _ in range(300)]

    # Вставка данных в таблицы
    try:
        cur.executemany("INSERT INTO users (username, email, password_hash, created_at) VALUES (%s, %s, %s, %s)", users)
        cur.executemany("INSERT INTO topics (user_id, title, created_at) VALUES (%s, %s, %s)", topics)
        cur.executemany("INSERT INTO messages (topic_id, user_id, content, created_at) VALUES (%s, %s, %s, %s)", messages)
        cur.executemany("INSERT INTO logs (user_id, session_id, action, target_id, target_type, ip_address, user_agent, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", logs)

        conn.commit()
        print("Data generation complete!")
    except mysql.connector.Error as err:
        print(f"Error while inserting data: {err}")
    finally:
        conn.close()

# Запуск скрипта
if __name__ == '__main__':
    generate_data()
