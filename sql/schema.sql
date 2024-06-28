CREATE TABLE bot_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token VARCHAR(255) NOT NULL,
    server_id BIGINT NOT NULL,
    custom_commands TEXT,
    log_channel_moderation BIGINT,
    log_channel_message_events BIGINT,
    ticket_systems JSON
);

CREATE TABLE user_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    oauth_token VARCHAR(255),
    cookies TEXT
);
