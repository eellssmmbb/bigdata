import mysql.connector
from datetime import datetime

def aggregate_data(start_date, end_date):
    # Подключение к базе данных
    conn = mysql.connector.connect(
        host="localhost",
        user="root",  # Используйте пользователя с доступом
        password="your_password",
        database="forum_db"
    )
    cursor = conn.cursor()

    query = """
    SELECT action, COUNT(*) 
    FROM logs 
    WHERE timestamp BETWEEN %s AND %s
    GROUP BY action
    """
    cursor.execute(query, (start_date, end_date))

    # Печать результатов
    results = cursor.fetchall()
    if results:
        for row in results:
            print(f"Action: {row[0]}, Count: {row[1]}")
    else:
        print("No data found for this period.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    start_date = "2024-03-01 00:00:00"
    end_date = "2024-04-31 23:59:59"
    aggregate_data(start_date, end_date)
