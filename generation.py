import random
import mysql.connector
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

# Настройка подключения к базе данных
conn = mysql.connector.connect(
    host='localhost',
    user='root',  
    password='password',  
    database='forum_db'
)
cursor = conn.cursor()

# Функция для создания пользователей
def create_users(num_users):
    users = []
    for _ in range(num_users):
        username = fake.user_name()
        password = fake.password()
        email = fake.email()
        users.append((username, password, email))

    cursor.executemany("""
        INSERT INTO users (username, password, email)
        VALUES (%s, %s, %s)
    """, users)
    conn.commit()

# Функция для создания действий с минимальными порогами
def generate_logs():
    logs = []
    created_topics = 0
    created_messages = 0
    logins = 0
    errors = 0

    # Минимальные пороги
    min_topic_creation = 5
    min_message_creation = 5
    min_login = 5

    # Генерация пользователей для логинов (если их еще нет)
    create_users(10)

    # Генерация логинов (смешанные действия успешные и с ошибками)
    for _ in range(min_login):
        username = fake.user_name()
        password = fake.password()
        email = fake.email()
        action_type = "login"
        status = random.choice(["success", "error"])
        description = "Login attempt"
        logs.append((username, password, email, action_type, None, status, description))
        logins += 1

    # Генерация создания тем (с минимумом 2 ошибок из-за отсутствия логина)
    while created_topics < min_topic_creation:
        username = fake.user_name()
        password = fake.password()
        email = fake.email()
        action_type = "create_topic"
        status = "error" if errors < 2 else "success"  # Делаем 2 ошибки по причине отсутствия логина
        description = "Create a new topic"
        
        # Добавляем логи
        if status == "error" and errors < 2:
            logs.append((username, password, email, action_type, None, status, description))
            errors += 1
        else:
            # Создаем тему
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            user_id = cursor.fetchone()
            if user_id:
                user_id = user_id[0]
                # Создаем тему
                cursor.execute("""
                    INSERT INTO topics (user_id, title)
                    VALUES (%s, %s)
                """, (user_id, fake.sentence()))
                conn.commit()
                logs.append((username, password, email, action_type, None, status, description))
        created_topics += 1

    # Генерация создания сообщений
    while created_messages < min_message_creation:
        username = fake.user_name()
        password = fake.password()
        email = fake.email()
        action_type = "create_message"
        status = random.choice(["success", "error"])
        description = "Create a new message"
        
        # Добавление сообщения к случайной теме
        cursor.execute("SELECT id FROM topics ORDER BY RAND() LIMIT 1")
        topic_id = cursor.fetchone()[0]

        if random.choice([True, False]):  # Равномерное распределение между залогиненым и незалогиненым пользователем
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            user_id = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO messages (topic_id, user_id, content)
                VALUES (%s, %s, %s)
            """, (topic_id, user_id, fake.text()))
            conn.commit()
            logs.append((username, password, email, action_type, topic_id, status, description))
        else:
            logs.append((username, password, email, action_type, topic_id, status, description))
        created_messages += 1
    
    # Генерация случайных дополнительных действий
    additional_actions = random.randint(5, 10)  # Дополнительные случайные действия
    for _ in range(additional_actions):
        username = fake.user_name()
        password = fake.password()
        email = fake.email()
        action_type = random.choice(["create_topic", "create_message", "login"])
        status = random.choice(["success", "error"])
        description = fake.text()
        logs.append((username, password, email, action_type, None, status, description))
    
    return logs

# Функция для вставки данных в базу данных
def insert_logs(logs):
    cursor.executemany("""
        INSERT INTO logs (username, password, email, action_type, target_id, status, description)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, logs)
    conn.commit()
    print(f"{len(logs)} logs added.")

# Генерация данных и вставка в базу
logs = generate_logs()
insert_logs(logs)

# Закрытие соединения
cursor.close()
conn.close()
