import redis
import mysql.connector
import json

# Подключение к Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Подключение к MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="mydatabase"
)
cursor = db.cursor()

while True:
    # Чтение сообщения из Redis
    message = r.brpop('messages', timeout=0)  # Блокирующее извлечение
    if message:
        # Запись в MySQL
        cursor.execute("INSERT INTO messages (message) VALUES (%s)", (message[1].decode("utf-8"),))
        db.commit()
        print(f"Inserted: {message[1].decode("utf-8")}")
