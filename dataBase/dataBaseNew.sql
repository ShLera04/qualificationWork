CREATE TABLE direction (
  direction_id SERIAL PRIMARY KEY NOT NULL,
  direction_name TEXT
);

CREATE TABLE groups (
  group_id SERIAL PRIMARY KEY NOT NULL,
  group_name TEXT
);

CREATE TABLE theme (
  theme_id SERIAL PRIMARY KEY NOT NULL,
  theme_name TEXT
);

CREATE TABLE files (
  file_id SERIAL PRIMARY KEY NOT NULL,
  file_name TEXT,
  file_data BYTEA  
);

CREATE TABLE users (
  user_id SERIAL PRIMARY KEY NOT NULL,
  login TEXT UNIQUE,
  password TEXT,
  is_admin BOOLEAN,
  email TEXT UNIQUE,
  direction_id INTEGER,
  created_at TIMESTAMP,
  FOREIGN KEY (direction_id) REFERENCES direction(direction_id)
);

CREATE TABLE students (
  student_id SERIAL PRIMARY KEY NOT NULL,
  user_id INTEGER UNIQUE,
  group_id INTEGER,
  FOREIGN KEY (user_id) REFERENCES users(user_id) 
  ON DELETE CASCADE,
  FOREIGN KEY (group_id) REFERENCES groups(group_id)
);

CREATE TABLE test_options (
  test_id SERIAL PRIMARY KEY NOT NULL,
  test_name TEXT,
  user_id INTEGER,
  theme_id INTEGER,
  difficulty_level TEXT CHECK (
    difficulty_level IN ('сложный', 'средний', 'легкий')
  ),
  easy_questions INTEGER,
  medium_questions INTEGER,
  hard_questions INTEGER,
  deadline TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
  ON DELETE CASCADE,
  FOREIGN KEY (theme_id) REFERENCES theme(theme_id)
  ON DELETE CASCADE
);

CREATE TABLE attempts (
  attempt_id SERIAL PRIMARY KEY NOT NULL,
  user_id INTEGER,
  test_id INTEGER,
  mark INTEGER,
  attempt_data TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
  ON DELETE CASCADE,
  FOREIGN KEY (test_id) REFERENCES test_options(test_id)
  ON DELETE CASCADE
);

CREATE TABLE questions (
  question_id SERIAL PRIMARY KEY NOT NULL,
  theme_id INTEGER,
  question_text TEXT,
  difficulty_level TEXT CHECK (
    difficulty_level IN ('сложный', 'средний', 'легкий')
  ),
  question_type TEXT CHECK (
    question_type IN ('с вводом значения', 'с единственным выбором ответа')
  ),
  score INTEGER,
  FOREIGN KEY (theme_id) REFERENCES theme(theme_id) ON DELETE CASCADE
);
CREATE TABLE answers (
  answer_id SERIAL PRIMARY KEY NOT NULL,
  question_id INTEGER,
  answer_text VARCHAR,
  is_correct BOOLEAN,
  FOREIGN KEY (question_id) REFERENCES questions(question_id)
  ON DELETE CASCADE
);

CREATE TABLE theme_files (
  theme_id INTEGER,
  file_id INTEGER,
  PRIMARY KEY (theme_id, file_id),
  FOREIGN KEY (theme_id) REFERENCES theme(theme_id)
  ON DELETE CASCADE,
  FOREIGN KEY (file_id) REFERENCES files(file_id)
  ON DELETE CASCADE
);

CREATE TABLE question_files (
  question_id INTEGER,
  file_id INTEGER,
  PRIMARY KEY (question_id, file_id),
  FOREIGN KEY (file_id) REFERENCES files(file_id)
  ON DELETE CASCADE,
  FOREIGN KEY (question_id) REFERENCES questions(question_id)
  ON DELETE CASCADE
);
