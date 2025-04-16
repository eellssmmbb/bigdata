import csv
import sys
from datetime import datetime, timedelta
import pymysql


def get_db_connection():
    return pymysql.connect(
        host='127.0.0.1',  
        port=3307,        
        user='user',       
        password='password', 
        database='forum_db'  
    )


def calculate_daily_stats(cursor, current_date):
    stats = {
        'new_accounts': 0,         # Новые аккаунты
        'anonymous_percent': 0.0,  # % анонимных сообщений
        'total_posts': 0,          # Всего сообщений
        'topic_growth': 0.0        # Рост тем (%)
    }
    
    # 1. Подсчет новых регистраций
    cursor.execute("""
        SELECT COUNT(*) 
        FROM user_logs 
        WHERE action_type = 'register' 
        AND server_response = 'success'
        AND DATE(action_time) = %s;
    """, (current_date,))
    stats['new_accounts'] = cursor.fetchone()[0]
    
    # 2. Расчет процента анонимных сообщений
    cursor.execute("""
        SELECT 
            COUNT(*) AS total,          
            SUM(is_anonymous) AS anonymous  
        FROM posts
        WHERE DATE(created_at) = %s;
    """, (current_date,))
    
    total_posts, anonymous_posts = cursor.fetchone()
    if total_posts > 0:
        stats['anonymous_percent'] = (anonymous_posts / total_posts) * 100
    
    # 3. Общее количество сообщений за день
    stats['total_posts'] = total_posts
    
    return stats


def calculate_topic_growth(cursor, current_date, prev_topics_count):
    # Считаем общее количество тем на текущую дату
    cursor.execute("""
        SELECT COUNT(*)
        FROM topics
        WHERE DATE(created_at) <= %s;
    """, (current_date,))
    current_topics_count = cursor.fetchone()[0]
    
    # Рассчитываем процент роста
    if prev_topics_count > 0:
        growth = ((current_topics_count - prev_topics_count) / 
                 prev_topics_count) * 100
    else:
        growth = 0.0  
    
    return current_topics_count, growth


def write_stats_to_csv(stats, filename='forum_stats.csv'):
    # Заголовки столбцов
    fieldnames = [
        'Day',             
        'New Accounts',     
        'Anonymous Posts %', 
        'Total Posts',    
        'Topic Growth %'   
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()  # Записываем заголовки
        
        for day_stats in stats:
            writer.writerow({
                'Day': day_stats['date'],
                'New Accounts': day_stats['new_accounts'],
                'Anonymous Posts %': f"{day_stats['anonymous_percent']:.2f}%",
                'Total Posts': day_stats['total_posts'],
                'Topic Growth %': f"{day_stats['topic_growth']:.2f}%"
            })


def main(start_date, end_date):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        stats = []  # Собранная статистика
        current_date = start_date
        prev_topics_count = 0  # Количество тем за предыдущий день
        
        # Обрабатываем каждый день в диапазоне
        while current_date <= end_date:
            # Получаем дневную статистику
            daily_stats = calculate_daily_stats(cursor, current_date)
            
            # Рассчитываем рост тем
            current_topics_count, growth = calculate_topic_growth(
                cursor, current_date, prev_topics_count
            )
            
            # Сохраняем результаты
            stats.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'new_accounts': daily_stats['new_accounts'],
                'anonymous_percent': daily_stats['anonymous_percent'],
                'total_posts': daily_stats['total_posts'],
                'topic_growth': growth
            })
            
            prev_topics_count = current_topics_count
            current_date += timedelta(days=1)  # Переходим к следующему дню
        
        # Записываем результаты в CSV
        write_stats_to_csv(stats)
        print(f"Сохранена в forum_stats.csv")
        
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    # Проверяем аргументы командной строки
    if len(sys.argv) != 3:
        print("Использование: python aggregate_data.py ГГГГ-ММ-ДД ГГГГ-ММ-ДД")
        sys.exit(1)
    
    try:
        # Парсим даты из аргументов
        start = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
        end = datetime.strptime(sys.argv[2], '%Y-%m-%d').date()
        
        # Запускаем основной процесс
        main(start, end)
    except ValueError as e:
        print(f"Ошибка формата даты: {e}")
        sys.exit(1)