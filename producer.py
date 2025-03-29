import random
import string
import time
import redis

# Подключение к Redis
r = redis.Redis(host='localhost', port=6379, db=0)

while True:
    # Генерация случайного сообщения
    message = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    r.lpush('messages', {'message': message})
    print(f"Sent: {message}")
    time.sleep(60)  # Ждать 1 минуту
