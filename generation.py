# generation.py (исправленная версия)
import random
from datetime import datetime, timedelta
import pymysql
from faker import Faker

def generate_test_data():
    fake = Faker()
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3307,
        user='user',
        password='password',
        db='forum_db'
    )
    
    try:
        cursor = conn.cursor()
        
        # 1. Очистка старых данных
        cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        cursor.execute("TRUNCATE users;")
        cursor.execute("TRUNCATE topics;")
        cursor.execute("TRUNCATE posts;")
        cursor.execute("TRUNCATE user_logs;")
        cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
        
        # 2. Генерация 10 пользователей
        users = []
        for _ in range(10):
            cursor.execute(
                "INSERT INTO users (username, email) VALUES (%s, %s)",
                (fake.user_name(), fake.email())
            )
            users.append(cursor.lastrowid)
        conn.commit()
        
        # 3. Генерация тем (20 штук)
        topics = []
        for _ in range(20):
            cursor.execute(
                "INSERT INTO topics (title, created_by) VALUES (%s, %s)",
                (fake.sentence(), random.choice(users))
            )
            topics.append(cursor.lastrowid)
        conn.commit()
        
        # 4. Генерация данных за 30 дней
        start_date = datetime.now() - timedelta(days=30)
        for day in range(30):
            current_date = start_date + timedelta(days=day)
            
            # Регистрации (3-5 в день)
            for _ in range(random.randint(3, 5)):
                cursor.execute(
                    """INSERT INTO user_logs 
                    (user_id, action_type, server_response, action_time)
                    VALUES (%s, 'register', 'success', %s)""",
                    (random.choice(users), current_date)
                )
            
            # Создание тем (2-4 в день)
            for _ in range(random.randint(2, 4)):
                user_id = random.choice(users)
                cursor.execute(
                    """INSERT INTO user_logs 
                    (user_id, action_type, server_response, action_time)
                    VALUES (%s, 'create_topic', 'success', %s)""",
                    (user_id, current_date)
                )
                cursor.execute(
                    "INSERT INTO topics (title, created_by) VALUES (%s, %s)",
                    (fake.sentence(), user_id)
                )
                topics.append(cursor.lastrowid)
            
            # Сообщения (10-20 в день)
            for _ in range(random.randint(10, 20)):
                is_anonymous = random.choice([True, False])
                user_id = None if is_anonymous else random.choice(users)
                cursor.execute(
                    """INSERT INTO posts 
                    (content, topic_id, created_by, is_anonymous)
                    VALUES (%s, %s, %s, %s)""",
                    (fake.text(), random.choice(topics), user_id, is_anonymous)
                )
            
            conn.commit()
        
        print("Тестовые данные успешно сгенерированы!")
        
    finally:
        conn.close()

if __name__ == "__main__":
    generate_test_data()