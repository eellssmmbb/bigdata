CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    registration_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE anonymous_users (
    anon_id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    first_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE topics (
    topic_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    created_by INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

CREATE TABLE messages (
    message_id SERIAL PRIMARY KEY,
    topic_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    anon_id INT,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (anon_id) REFERENCES anonymous_users(anon_id),
    CHECK (user_id IS NOT NULL OR anon_id IS NOT NULL)
);

CREATE TABLE action_types (
    action_type_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

INSERT INTO action_types (name, description) VALUES
('first_visit', 'Первый заход на сайт'),
('registration', 'Регистрация пользователя'),
('login', 'Вход в систему'),
('logout', 'Выход из системы'),
('topic_create', 'Создание темы'),
('topic_view', 'Просмотр темы'),
('topic_delete', 'Удаление темы'),
('message_post', 'Написание сообщения');

CREATE TABLE user_logs (
    log_id SERIAL PRIMARY KEY,
    action_type_id INT NOT NULL,
    user_id INT,
    anon_id INT,
    action_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    entity_type VARCHAR(50),
    entity_id INT,
    server_response VARCHAR(20) NOT NULL,
    additional_info TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    FOREIGN KEY (action_type_id) REFERENCES action_types(action_type_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (anon_id) REFERENCES anonymous_users(anon_id),
    CHECK (user_id IS NOT NULL OR anon_id IS NOT NULL)
);