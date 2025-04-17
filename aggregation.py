import mysql.connector
import sys
import datetime

# Настройки подключения к БД
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",  
    database="forum_db"
)
cursor = db_connection.cursor()

# Функция для агрегации данных
def aggregate_data(start_date, end_date):
    result = []

    current_date = start_date
    while current_date <= end_date:
        # Подсчитываем количество новых аккаунтов
        cursor.execute("""
            SELECT COUNT(*) FROM users WHERE created_at = %s
        """, (current_date,))
        new_accounts = cursor.fetchone()[0]

        # Подсчитываем количество сообщений
        cursor.execute("""
            SELECT COUNT(*) FROM messages WHERE DATE(created_at) = %s
        """, (current_date,))
        total_messages = cursor.fetchone()[0]

        # Подсчитываем количество сообщений от анонимов
        cursor.execute("""
            SELECT COUNT(*) FROM messages WHERE DATE(created_at) = %s AND user_id IS NULL
        """, (current_date,))
        anonymous_messages = cursor.fetchone()[0]

        # Вычисляем процент сообщений от анонимов
        anonymous_percent = (anonymous_messages / total_messages * 100) if total_messages > 0 else 0

        # Подсчитываем количество новых тем
        cursor.execute("""
            SELECT COUNT(*) FROM topics WHERE DATE(created_at) = %s
        """, (current_date,))
        new_topics = cursor.fetchone()[0]

        # Получаем количество тем на предыдущий день для расчета прироста
        prev_date = current_date - datetime.timedelta(days=1)
        cursor.execute("""
            SELECT COUNT(*) FROM topics WHERE DATE(created_at) = %s
        """, (prev_date,))
        prev_topics = cursor.fetchone()[0]

        # Вычисляем процентное изменение количества тем относительно предыдущего дня
        if prev_topics > 0:
            topic_growth_percent = ((new_topics / prev_topics) - 1) * 100
        else:
            topic_growth_percent = 0

        result.append({
            'day': current_date,
            'registrations': new_accounts,
            'anonymous_percent': f"{anonymous_percent:.2f}%",
            'total_messages': total_messages,
            'topic_growth_percent': f"{topic_growth_percent:.2f}%"
        })

        current_date += datetime.timedelta(days=1)

    return result

# Период передается через аргументы скрипта
if len(sys.argv) < 3:
    print("Использование: python aggregation.py <начальная_дата> <конечная_дата>")
    print("Пример: python aggregation.py 2025-04-01 2025-04-30")
    sys.exit(1)

start_date = datetime.datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
end_date = datetime.datetime.strptime(sys.argv[2], "%Y-%m-%d").date()

# Получаем данные агрегации
data = aggregate_data(start_date, end_date)

# Запись в CSV
import csv
with open("aggregation_report.csv", mode="w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=['day', 'registrations', 'anonymous_percent', 'total_messages', 'topic_growth_percent'])
    writer.writeheader()
    writer.writerows(data)

print("Отчет агрегации сохранен в 'aggregation_report.csv'.")

cursor.close()
db_connection.close()
