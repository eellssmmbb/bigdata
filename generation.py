import mysql.connector
import csv
import sys
from datetime import datetime, timedelta

# Параметры подключения к MySQL
DB_PARAMS = {
    'host': 'localhost',
    'port': 3306,
    'user': 'user',  
    'password': 'password',
    'database': 'forum_db'
}

# Подключение к БД
def connect_db():
    print("Connecting to MySQL database...")
    return mysql.connector.connect(**DB_PARAMS)

# Агрегация данных
def aggregate_data(start_date, end_date):
    conn = connect_db()
    cur = conn.cursor()

    results = []

    query = """
    SELECT 
        DATE(timestamp) AS day,
        COUNT(DISTINCT CASE WHEN action_id = 2 THEN user_id END) AS new_accounts,
        COUNT(CASE WHEN action_id = 8 THEN 1 END) AS total_messages,
        COUNT(CASE WHEN action_id = 8 AND user_id IS NULL THEN 1 END) AS anonymous_messages,
        COUNT(CASE WHEN action_id = 5 THEN 1 END) AS new_themes
    FROM logs
    WHERE timestamp BETWEEN %s AND %s
    GROUP BY day
    ORDER BY day;
    """

    cur.execute(query, (start_date, end_date))
    rows = cur.fetchall()

    prev_day_themes = None

    for row in rows:
        day, new_accounts, total_messages, anonymous_messages, new_themes = row

        anonymous_percentage = (anonymous_messages / total_messages * 100) if total_messages > 0 else 0

        if prev_day_themes is not None:
            theme_growth_percentage = ((new_themes - prev_day_themes) / prev_day_themes * 100) if prev_day_themes > 0 else 0
        else:
            theme_growth_percentage = 0

        results.append([day, new_accounts, anonymous_percentage, total_messages, theme_growth_percentage])
        prev_day_themes = new_themes

    conn.close()
    return results

# Запись в CSV
def write_to_csv(data, filename='aggregated_logs.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Day', 'New Accounts', 'Anonymous Messages (%)', 'Total Messages', 'Theme Growth (%)'])
        writer.writerows(data)

# Основная функция
def main():
    if len(sys.argv) < 3:
        print("Usage: python generation.py YYYY-MM-DD YYYY-MM-DD")
        sys.exit(1)

    start_date = sys.argv[1]
    end_date = sys.argv[2]

    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        sys.exit(1)

    print(f"Aggregating from {start_date_obj} to {end_date_obj}...")

    data = aggregate_data(start_date, end_date)
    write_to_csv(data)

    print("Done. Data saved to 'aggregated_logs.csv'.")

if __name__ == '__main__':
    main()
