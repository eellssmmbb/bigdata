-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB;

-- Таблица тем
CREATE TABLE IF NOT EXISTS topics (
    topic_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
) ENGINE=InnoDB;

-- Таблица сообщений
CREATE TABLE IF NOT EXISTS posts (
    post_id INT AUTO_INCREMENT PRIMARY KEY,
    content TEXT NOT NULL,
    topic_id INT NOT NULL,
    created_by INT, -- NULL для анонимов
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_anonymous BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id)
) ENGINE=InnoDB;

-- Таблица логов
CREATE TABLE IF NOT EXISTS user_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT, -- NULL для анонимных действий
    action_type ENUM(
        'first_visit',
        'register',
        'login',
        'logout',
        'create_topic',
        'view_topic',
        'delete_topic',
        'post_message'
    ) NOT NULL,
    action_details JSON,
    server_response ENUM('success', 'error') NOT NULL,
    action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;

-- Индексы для оптимизации
CREATE INDEX idx_user_logs_action_time ON user_logs(action_time);
CREATE INDEX idx_user_logs_action_type ON user_logs(action_type);
CREATE INDEX idx_posts_created_at ON posts(created_at);
CREATE INDEX idx_topics_created_at ON topics(created_at);