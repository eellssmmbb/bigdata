import psycopg2
import csv
import sys
from datetime import datetime, timedelta

# Параметры подключения к базе данных
DB_PARAMS = {
    'dbname': 'forum_db',
    'user': 'user',
    'password': 'password', 
    'host': 'localhost',
    'port': '5432' 
}

# Функция для подключения к базе данных
def connect_db():
    print("Connecting to database...")
    return psycopg2.connect(**DB_PARAMS)

# Функция для агрегации данных
def aggregate_data(start_date, end_date):
    print(f"Aggregating data between {start_date} and {end_date}...")
    conn = connect_db()
    cur = conn.cursor()

    # Словарь для хранения данных по дням
    results = []

    # Основной запрос для получения данных по дням
    query = """
    SELECT 
        DATE(timestamp) AS day,
        COUNT(DISTINCT CASE WHEN action_id = 1 THEN user_id END) AS new_accounts,
        COUNT(CASE WHEN action_id = 7 THEN 1 END) AS total_messages,
        COUNT(CASE WHEN action_id = 7 AND user_id IS NULL THEN 1 END) AS anonymous_messages
    FROM logs
    WHERE timestamp BETWEEN %s AND %s
    GROUP BY day
    ORDER BY day;
    """
    
    # Выполняем запрос
    print("Executing query...")
    cur.execute(query, (start_date, end_date))

    # Получаем результаты
    rows = cur.fetchall()

    # Добавляем расчет процента анонимных сообщений и прироста тем
    prev_day_messages = None
    prev_day_themes = None

    for row in rows:
        day, new_accounts, total_messages, anonymous_messages = row

        # Процент анонимных сообщений
        anonymous_percentage = (anonymous_messages / total_messages * 100) if total_messages > 0 else 0

        # Прирост тем
        if prev_day_themes is not None:
            theme_growth_percentage = (new_accounts - prev_day_themes) / prev_day_themes * 100 if prev_day_themes > 0 else 0
        else:
            theme_growth_percentage = 0

        # Сохраняем данные
        results.append([day, new_accounts, anonymous_percentage, total_messages, theme_growth_percentage])

        # Обновляем данные для следующего дня
        prev_day_messages = total_messages
        prev_day_themes = new_accounts

    # Закрываем соединение с базой данных
    conn.close()

    print("Data aggregation complete.")
    return results

# Функция для записи данных в CSV файл
def write_to_csv(data, filename='aggregated_logs.csv'):
    print(f"Writing data to {filename}...")
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Day', 'New Accounts', 'Anonymous Messages (%)', 'Total Messages', 'Theme Growth (%)'])
        writer.writerows(data)
    print("Data written to CSV successfully.")

# Основная функция
def main():
    if len(sys.argv) < 3:
        print("Please provide start and end dates in YYYY-MM-DD format")
        print(f"Arguments received: {sys.argv}")
        sys.exit(1)

    start_date = sys.argv[1]
    end_date = sys.argv[2]

    print(f"Start date: {start_date}, End date: {end_date}")

    try:
        # Проверяем, что даты корректны
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        print(f"Invalid date format. Expected YYYY-MM-DD. Received start: {start_date}, end: {end_date}")
        sys.exit(1)

    # Агрегируем данные
    aggregated_data = aggregate_data(start_date_obj, end_date_obj)

    # Записываем в CSV файл
    write_to_csv(aggregated_data)

    print("Aggregation complete. Data saved to 'aggregated_logs.csv'.")

# Запуск скрипта
if __name__ == '__main__':
    main()
