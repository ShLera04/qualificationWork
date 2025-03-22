CREATE TABLE allusers (
  user_id SERIAL PRIMARY KEY,
  login VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL,
  is_admin BOOLEAN NOT NULL,
  email VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE students (
  student_id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL UNIQUE,
  direction_id INTEGER NOT NULL,
  group_id INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES allusers(user_id),
  FOREIGN KEY (group_id) REFERENCES allgroups(group_id)
);

CREATE TABLE lecturers (
  lecturer_id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  direction_id INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES allusers(user_id)
);

CREATE TABLE attempts (
  attempt_id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  mark INTEGER CHECK (mark BETWEEN 0 AND 7),
  attemp_data TIMESTAMP NOT NULL
);

CREATE TABLE theme (
  theme_id SERIAL PRIMARY KEY,
  theme_name VARCHAR(255) NOT NULL
);

CREATE TABLE direction (
  direction_id SERIAL PRIMARY KEY,
  direction_name VARCHAR(255) NOT NULL
);

CREATE TABLE files (
  file_id SERIAL PRIMARY KEY,
  file_name VARCHAR(255) NOT NULL,
  file_data TEXT NOT NULL
);

CREATE TABLE test_options (
  test_id SERIAL PRIMARY KEY,
  test_name VARCHAR(255) NOT NULL,
  lecturer_id INTEGER NOT NULL,
  difficulty_level VARCHAR(50) NOT NULL,
  total_questions INTEGER,
  easy_questions INTEGER NOT NULL,
  medium_questions INTEGER NOT NULL,
  hard_questions INTEGER NOT NULL,
  deadline TIMESTAMP NOT NULL,
  FOREIGN KEY (lecturer_id) REFERENCES lecturers(lecturer_id)
);

CREATE TABLE question_storage (
  question_id SERIAL PRIMARY KEY,
  text TEXT NOT NULL,
  difficulty_level VARCHAR(50) NOT NULL,
  question_type VARCHAR(50) NOT NULL,
  score INTEGER NOT NULL
);

CREATE TABLE answers (
  answer_id SERIAL PRIMARY KEY,
  answer_text TEXT NOT NULL,
  isCorrect BOOLEAN NOT NULL
);

CREATE TABLE questions_answers (
  questions_answers_id SERIAL PRIMARY KEY,
  answer_id INTEGER NOT NULL,
  question_id INTEGER NOT NULL,
  FOREIGN KEY (answer_id) REFERENCES answers(answer_id),
  FOREIGN KEY (question_id) REFERENCES question_storage(question_id)
);

CREATE TABLE questions_themes (
  questions_themes_id SERIAL PRIMARY KEY,
  question_id INTEGER NOT NULL,
  theme_id INTEGER NOT NULL,
  FOREIGN KEY (question_id) REFERENCES question_storage(question_id),
  FOREIGN KEY (theme_id) REFERENCES theme(theme_id)
);

CREATE TABLE files_themes (
  files_themes_id SERIAL PRIMARY KEY,
  file_id INTEGER NOT NULL,
  theme_id INTEGER NOT NULL,
  FOREIGN KEY (file_id) REFERENCES files(file_id),
  FOREIGN KEY (theme_id) REFERENCES theme(theme_id)
);

CREATE TABLE test_options_themes (
  test_options_themes_id SERIAL PRIMARY KEY,
  test_id INTEGER NOT NULL,
  theme_id INTEGER NOT NULL,
  FOREIGN KEY (test_id) REFERENCES test_options(test_id),
  FOREIGN KEY (theme_id) REFERENCES theme(theme_id)
);

CREATE TABLE test_options_attempts (
  tests_attempts_id SERIAL PRIMARY KEY,
  test_id INTEGER NOT NULL,
  attempt_id INTEGER NOT NULL,
  FOREIGN KEY (test_id) REFERENCES test_options(test_id),
  FOREIGN KEY (attempt_id) REFERENCES attempts(attempt_id)
);

CREATE TABLE questions_files (
  questions_files_id SERIAL PRIMARY KEY,
  question_id INTEGER NOT NULL,
  file_id INTEGER NOT NULL,
  FOREIGN KEY (question_id) REFERENCES question_storage(question_id),
  FOREIGN KEY (file_id) REFERENCES files(file_id)
);

CREATE TABLE allgroups (
  group_id SERIAL PRIMARY KEY,
  group_name VARCHAR(255) NOT NULL
);
