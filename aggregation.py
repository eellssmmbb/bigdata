import mysql.connector
import csv
from datetime import datetime, timedelta


def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="rootpassword",
        database="forum_db",
    )


def get_aggregation_data(start_date, end_date):
    conn = create_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        DATE(t.created_at) AS day,
        COUNT(DISTINCT u.id) AS new_accounts,
        (SUM(CASE WHEN m.created_by IS NULL THEN 1 ELSE 0 END) / COUNT(m.id)) * 100 AS anonymous_message_percentage,
        COUNT(m.id) AS total_messages,
        ((COUNT(DISTINCT t2.id) - COUNT(DISTINCT t.id)) / COUNT(DISTINCT t.id)) * 100 AS topic_growth
    FROM
        users u
    JOIN
        themes t ON DATE(t.created_at) BETWEEN %s AND %s
    LEFT JOIN
        messages m ON m.theme_id = t.id
    LEFT JOIN
        themes t2 ON DATE(t2.created_at) = DATE(t.created_at) - INTERVAL 1 DAY
    GROUP BY
        DATE(t.created_at);
    """

    cursor.execute(query, (start_date, end_date))
    data = cursor.fetchall()

    cursor.close()
    conn.close()
    return data


def calculate_theme_change(data):
    aggregated_data = []
    for i in range(1, len(data)):
        current_day = data[i]
        previous_day = data[i - 1]

        current_day_themes = current_day[3]
        previous_day_themes = previous_day[3]

        if previous_day_themes == 0:
            topic_growth = 0
        else:
            topic_growth = (
                (current_day_themes - previous_day_themes)
                / previous_day_themes
            ) * 100

        aggregated_data.append(
            {
                "day": current_day[0],
                "new_accounts": current_day[1],
                "anonymous_message": current_day[2],
                "total_messages": current_day[3],
                "topic_growth": topic_growth,
            }
        )

    return aggregated_data


def write_to_csv(data, filename):
    keys = data[0].keys() if data else []
    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)


def main():
    start_date = "2025-04-01"
    end_date = "2025-04-30"

    data = get_aggregation_data(start_date, end_date)

    aggregated_data = calculate_theme_change(data)

    output_filename = f"forum_aggregation_{start_date}_{end_date}.csv"
    write_to_csv(aggregated_data, output_filename)
    print(f"Данные успешно записаны в файл {output_filename}")


if __name__ == "__main__":
    main()