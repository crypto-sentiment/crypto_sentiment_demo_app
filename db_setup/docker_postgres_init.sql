CREATE TABLE news_titles (title_id BIGINT PRIMARY KEY, title VARCHAR(511) NOT NULL, source VARCHAR(72), pub_time TIMESTAMP);
CREATE TABLE model_predictions (title_id BIGINT PRIMARY KEY, negative FLOAT, neutral FLOAT, positive FLOAT, predicted_class INTEGER, entropy FLOAT);
CREATE TABLE labeled_news_titles (title_id BIGINT PRIMARY KEY, label INTEGER, annot_time TIMESTAMP);
