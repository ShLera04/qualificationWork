CREATE TABLE users (
  user_id INTEGER PRIMARY KEY NOT NULL,
  login VARCHAR UNIQUE,
  password VARCHAR,
  is_admin BOOLEAN,
  email VARCHAR UNIQUE,
  direction_id INTEGER,
  created_at TIMESTAMP
);

CREATE TABLE groups (
  group_id INTEGER PRIMARY KEY NOT NULL,
  group_name VARCHAR
);

CREATE TABLE direction (
  direction_id INTEGER PRIMARY KEY NOT NULL,
  direction_name VARCHAR
);

CREATE TABLE students (
  student_id INTEGER PRIMARY KEY NOT NULL,
  user_id INTEGER UNIQUE REFERENCES users(user_id),
  group_id INTEGER REFERENCES groups(group_id)
);

CREATE TABLE theme (
  theme_id INTEGER PRIMARY KEY NOT NULL,
  theme_name VARCHAR
);

CREATE TABLE files (
  file_id INTEGER PRIMARY KEY NOT NULL,
  file_name VARCHAR,
  file_data VARCHAR
);

CREATE TABLE test_options (
  test_id INTEGER PRIMARY KEY NOT NULL,
  test_name VARCHAR,
  user_id INTEGER REFERENCES users(user_id),
  theme_id INTEGER REFERENCES theme(theme_id),
  difficulty_level VARCHAR,
  easy_questions INTEGER,
  medium_questions INTEGER,
  hard_questions INTEGER,
  deadline TIMESTAMP
);

CREATE TABLE attempts (
  attempt_id INTEGER PRIMARY KEY NOT NULL,
  user_id INTEGER REFERENCES users(user_id),
  test_id INTEGER REFERENCES test_options(test_id),
  mark INTEGER,
  attempt_data TIMESTAMP
);

CREATE TABLE questions (
  question_id INTEGER PRIMARY KEY NOT NULL,
  theme_id INTEGER REFERENCES theme(theme_id),
  text VARCHAR,
  difficulty_level VARCHAR,
  question_type VARCHAR,
  score INTEGER
);

CREATE TABLE answers (
  answer_id INTEGER PRIMARY KEY NOT NULL,
  question_id INTEGER REFERENCES questions(question_id),
  answer_text VARCHAR,
  is_correct BOOLEAN
);

CREATE TABLE theme_files (
  theme_id INTEGER REFERENCES theme(theme_id),
  file_id INTEGER REFERENCES files(file_id),
  PRIMARY KEY (theme_id, file_id)
);

CREATE TABLE question_files (
  question_id INTEGER REFERENCES questions(question_id),
  file_id INTEGER REFERENCES files(file_id),
  PRIMARY KEY (question_id, file_id)
);

ALTER TABLE users ADD FOREIGN KEY (direction_id) REFERENCES direction(direction_id);
