from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify, make_response
import psycopg2
import configparser
import logging

logging.basicConfig(filename="server.log",
                    level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s",
                    filemode="w")

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


config = configparser.ConfigParser()
config.read('config.ini')

@app.route('/entrance', methods=['GET', 'POST'])
def entrance_page():
    return render_template('entrance.html')

@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/mainStudent')
def main_page():
    return render_template('mainStudent.html')

@app.route('/mainLecturer')
def admin_page():
    return render_template('mainLecturer.html')

@app.route('/createTest')
def test_page():
    return render_template('createTest.html')

@app.route('/pageStudent')
def page_page():
    return render_template('pageStudent.html')

@app.route('/pageLecturer')
def lll_page():
    return render_template('pageLecturer.html')

@app.route('/addQuestion')
def formula_page():
    return render_template('addQuestion.html')



@app.route('/register.html', methods=['POST'])
def register_user():
    log = request.form['login']
    pas = request.form['password']
    repet_pas = request.form['repetpassword']
    email = request.form['email']
    group_name = request.form['group']

    conn = psycopg2.connect(
        dbname='dataBase',
        user='postgres',
        password='12345',
        host='localhost',
        options="-c client_encoding=utf-8"
    )
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM allusers WHERE login = %s", (log,))
    count = cur.fetchone()[0]

    if count > 0:
        return redirect(url_for('register_page', message='Пользователь с таким логином уже зарегистрирован'))

    if pas == repet_pas:
        cur.execute("INSERT INTO allusers (login, password, email, is_admin, created_at) VALUES (%s, %s, %s, FALSE, NOW())", (log, pas, email))
        user_id = cur.lastrowid

        cur.execute("INSERT INTO students (user_id, direction_id) VALUES (%s, %s)", (user_id, 1))  # Замените 1 на реальный direction_id
        student_id = cur.lastrowid

        # cur.execute("SELECT group_id FROM allgroups WHERE group_name = %s", (group_name,))
        # group_id = cur.fetchone()[0]
        # cur.execute("INSERT INTO students_groups (student_id, group_id) VALUES (%s, %s)", (student_id, group_id))

        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('register_page', message='Регистрация прошла успешно!'))
    else:
        return redirect(url_for('register_page', message='Ваши пароли не совпали. Повторите ввод заново!'))

# @app.route('/entrance.html', methods=['POST'])
# def login_user():
#     log = request.form['login']
#     pas = request.form['password']

#     conn = psycopg2.connect(
#         dbname='register',
#         user='postgres',
#         password='12345',
#         host='localhost',
#         options="-c client_encoding=utf-8"
#     )
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM tableRegister WHERE login = %s AND password = %s", (log, pas))
#     user = cur.fetchone()

#     if user:
#         return redirect(url_for('main_page'))
#     else:
#         return redirect(url_for('entrance_page', message='Неверный логин или пароль. Попробуйте снова.'))

# def is_saddle_point(matrix, row, col):
#     element = matrix[row][col]
#     if element != min(matrix[row]):
#         return False
#     if element != max(matrix[i][col] for i in range(len(matrix))):
#         return False
#     return True

# def find_saddle_points(matrix):
#     saddle_points = []
#     row_min = [min(row) for row in matrix]
#     col_max = [max(col) for col in zip(*matrix)]

#     for i in range(len(matrix)):
#         for j in range(len(matrix[i])):
#             if matrix[i][j] == row_min[i] and matrix[i][j] == col_max[j]:
#                 saddle_points.append((i, j, matrix[i][j]))

#     return saddle_points

# def is_pareto_optimal(matrix_a, matrix_b):
#     pareto_optimal_points = []
#     n = len(matrix_a)
#     m = len(matrix_a[0])

#     for i in range(n):
#         for j in range(m):
#             current_a = matrix_a[i][j]
#             current_b = matrix_b[i][j]
#             is_optimal = True
#             for x in range(n):
#                 for y in range(m):
#                     if (matrix_a[x][y] >= current_a and
#                         matrix_b[x][y] >= current_b and
#                         (matrix_a[x][y] > current_a or matrix_b[x][y] > current_b)):
#                         is_optimal = False
#                         break
#                 if not is_optimal:
#                     break
#             if is_optimal:
#                 pareto_optimal_points.append((i, j, current_a, current_b))

#     return pareto_optimal_points

# def is_nash_equilibrium(matrix_a, matrix_b):
#     nash_points = []
#     n = len(matrix_a)
#     m = len(matrix_a[0])

#     for i in range(n):
#         for j in range(m):
#             current_a = matrix_a[i][j]
#             current_b = matrix_b[i][j]
#             is_nash = True

#             # Проверка строки (игрок 1 не может улучшить свой выигрыш)
#             for k in range(n):
#                 if matrix_a[k][j] >= current_a:
#                     is_nash = False
#                     break

#             # Проверка столбца (игрок 2 не может улучшить свой выигрыш)
#             if is_nash:
#                 for l in range(m):
#                     if matrix_b[i][l] >= current_b:
#                         is_nash = False
#                         break

#             if is_nash:
#                 nash_points.append((i, j, current_a, current_b))

#     return nash_points

# @app.route('/saddle_points', methods=['POST'])
# def saddle_points():
#     data = request.get_json()
#     matrix = data['matrix']
#     result = find_saddle_points(matrix)
#     return jsonify(result)

# @app.route('/pareto_optimal', methods=['POST'])
# def pareto_optimal():
#     data = request.get_json()
#     matrix_a = data['matrix_a']
#     matrix_b = data['matrix_b']
#     result = is_pareto_optimal(matrix_a, matrix_b)
#     return jsonify(result)

# @app.route('/nash_equilibrium', methods=['POST'])
# def nash_equilibrium():
#     data = request.get_json()
#     matrix_a = data['matrix_a']
#     matrix_b = data['matrix_b']
#     result = is_nash_equilibrium(matrix_a, matrix_b)
#     if result:
#         return jsonify(result)
#     else:
#         return jsonify([])

# @app.route('/get-themes', methods=['GET'])
# def get_themes():
#     conn = psycopg2.connect(
#         dbname='register',
#         user='postgres',
#         password='12345',
#         host='localhost',
#         options="-c client_encoding=utf-8"
#     )
#     cur = conn.cursor()
#     cur.execute("SELECT theme_id, theme_name FROM themes")
#     themes = cur.fetchall()
#     cur.close()
#     conn.close()
#     return jsonify([{"value": theme[0], "text": theme[1]} for theme in themes])
# @app.route('/get-themess', methods=['GET'])
# def get_themess():
#     conn = psycopg2.connect(
#         dbname='register',
#         user='postgres',
#         password='12345',
#         host='localhost',
#         options="-c client_encoding=utf-8"
#     )
#     cur = conn.cursor()
#     cur.execute("SELECT theme_id, theme_name FROM themes")
#     themes = cur.fetchall()
#     cur.close()
#     conn.close()
#     return jsonify([{"id": theme[0], "name": theme[1]} for theme in themes])


# @app.route('/get-directions', methods=['GET'])
# def get_directions():
#     conn = psycopg2.connect(
#         dbname='register',
#         user='postgres',
#         password='12345',
#         host='localhost',
#         options="-c client_encoding=utf-8"
#     )
#     cur = conn.cursor()
#     cur.execute("SELECT DISTINCT direction FROM tests")
#     directions = cur.fetchall()
#     cur.close()
#     conn.close()
#     return jsonify([{"value": direction[0], "text": direction[0]} for direction in directions])

# @app.route('/get-disciplines', methods=['GET'])
# def get_disciplines():
#     conn = psycopg2.connect(
#         dbname='register',
#         user='postgres',
#         password='12345',
#         host='localhost',
#         options="-c client_encoding=utf-8"
#     )
#     cur = conn.cursor()
#     cur.execute("SELECT DISTINCT discipline FROM tests")
#     disciplines = cur.fetchall()
#     cur.close()
#     conn.close()
#     return jsonify([{"value": discipline[0], "text": discipline[0]} for discipline in disciplines])

# @app.route('/get-question-types', methods=['GET'])
# def get_question_types():
#     conn = psycopg2.connect(
#         dbname='register',
#         user='postgres',
#         password='12345',
#         host='localhost',
#         options="-c client_encoding=utf-8"
#     )
#     cur = conn.cursor()
#     cur.execute("SELECT DISTINCT question_type FROM questions")
#     question_types = cur.fetchall()
#     cur.close()
#     conn.close()
#     return jsonify([question_type[0] for question_type in question_types])

# @app.route('/create-test', methods=['POST'])
# def create_test():
#     data = request.form
#     try:
#         conn = psycopg2.connect(
#             dbname='register',
#             user='postgres',
#             password='12345',
#             host='localhost',
#             options="-c client_encoding=utf-8"
#         )
#         cur = conn.cursor()

#         # Проверка существования теста с такими же параметрами
#         cur.execute("SELECT COUNT(*) FROM tests WHERE theme_id = %s AND direction = %s AND discipline = %s AND difficulty_level = %s AND total_questions = %s AND easy_questions = %s AND medium_questions = %s AND hard_questions = %s",
#                     (data['theme'], data['direction'], data['discipline'], data['testDifficulty'], data['totalQuestions'], data['easyQuestions'], data['mediumQuestions'], data['hardQuestions']))
#         count = cur.fetchone()[0]

#         if count > 0:
#             return jsonify({"status": "error", "message": "Тест с такими параметрами уже существует."})

#         # Вставка нового теста
#         cur.execute("INSERT INTO tests (theme_id, direction, discipline, difficulty_level, total_questions, easy_questions, medium_questions, hard_questions) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
#                     (data['theme'], data['direction'], data['discipline'], data['testDifficulty'], data['totalQuestions'], data['easyQuestions'], data['mediumQuestions'], data['hardQuestions']))
#         conn.commit()
#         cur.close()
#         conn.close()
#         return jsonify({"status": "success"})
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)})


# @app.route('/create-question', methods=['POST'])
# def create_question():
#     data = request.form
#     try:
#         conn = psycopg2.connect(
#             dbname='register',
#             user='postgres',
#             password='12345',
#             host='localhost',
#             options="-c client_encoding=utf-8"
#         )
#         cur = conn.cursor()

#         # Логирование полученных данных
#         logging.info(f"Received data: {data}")

#         # Вставка вопроса в таблицу questions
#         cur.execute("INSERT INTO questions (theme_id, question_text, direction, discipline, question_type, difficulty_level) VALUES (%s, %s, %s, %s, %s, %s)",
#                     (data['theme'], data['question'], data['direction'], data['discipline'], data['questionType'], data['difficulty-level']))

#         # Получение ID вставленного вопроса
#         cur.execute("SELECT question_id FROM questions WHERE question_text = %s", (data['question'],))
#         question_id = cur.fetchone()[0]

#         # Вставка ответов в таблицу answers
#         if data['questionType'] == 'с единственным выбором ответа':
#             options = [data[key] for key in data if key.startswith('option-')]
#             correct_answer = data['correct-answer']
#             logging.info(f"Options: {options}, Correct Answer: {correct_answer}")
#             for option in options:
#                 is_correct = option == correct_answer
#                 cur.execute("INSERT INTO answers (question_id, answer_text, is_correct, numeric_answer) VALUES (%s, %s, %s, %s)",
#                             (question_id, option, is_correct, None))
#         elif data['questionType'] == 'с множественным выбором ответа':
#             options = [data[key] for key in data if key.startswith('option-')]
#             correct_answers = [data[key] for key in data if key.startswith('correct-answer-')]
#             logging.info(f"Options: {options}, Correct Answers: {correct_answers}")
#             for option in options:
#                 is_correct = option in correct_answers
#                 cur.execute("INSERT INTO answers (question_id, answer_text, is_correct, numeric_answer) VALUES (%s, %s, %s, %s)",
#                             (question_id, option, is_correct, None))
#         elif data['questionType'] == 'с вводом значения':
#             logging.info(f"Correct Answer: {data['correct-answer']}")
#             cur.execute("INSERT INTO answers (question_id, answer_text, is_correct, numeric_answer) VALUES (%s, %s, %s, %s)",
#                         (question_id, data['correct-answer'], True, data['correct-answer']))

#         conn.commit()
#         cur.close()
#         conn.close()
#         return jsonify({"status": "success"})
#     except Exception as e:
#         logging.error(f"Error: {str(e)}")
#         return jsonify({"status": "error", "message": str(e)})


# @app.route('/add-theme', methods=['POST'])
# def add_theme():
#     data = request.json
#     theme_name = data.get('theme_name')

#     if not theme_name:
#         return jsonify({"status": "error", "message": "Theme name is required"}), 400

#     conn = psycopg2.connect(
#         dbname='register',
#         user='postgres',
#         password='12345',
#         host='localhost',
#         options="-c client_encoding=utf-8"
#     )
#     cur = conn.cursor()

#     try:
#         cur.execute("INSERT INTO themes (theme_name) VALUES (%s) RETURNING theme_id, theme_name", (theme_name,))
#         new_theme = cur.fetchone()
#         conn.commit()
#     except psycopg2.errors.UniqueViolation:
#         conn.rollback()
#         return jsonify({"status": "error", "message": "Theme already exists"}), 409
#     except Exception as e:
#         conn.rollback()
#         return jsonify({"status": "error", "message": str(e)}), 500
#     finally:
#         cur.close()
#         conn.close()

#     return jsonify({"status": "success", "theme": {"id": new_theme[0], "name": new_theme[1]}})

# @app.route('/get-regular-users', methods=['GET'])
# def get_regular_users():
#     conn = psycopg2.connect(
#         dbname='register',
#         user='postgres',
#         password='12345',
#         host='localhost',
#         options="-c client_encoding=utf-8"
#     )
#     cur = conn.cursor()
#     cur.execute("SELECT login FROM tableRegister WHERE isAdmin = %s", (False,))
#     users = cur.fetchall()
#     cur.close()
#     conn.close()
#     return jsonify([{"value": user[0], "text": user[0]} for user in users])

# @app.route('/add-admin', methods=['POST'])
# def add_admin():
#     data = request.json
#     admin_name = data.get('admin_name')

#     if not admin_name:
#         return jsonify({"status": "error", "message": "Имя администратора обязательно"}), 400

#     conn = psycopg2.connect(
#         dbname='register',
#         user='postgres',
#         password='12345',
#         host='localhost',
#         options="-c client_encoding=utf-8"
#     )
#     cur = conn.cursor()

#     try:
#         # Обновление поля isAdmin на True для выбранного пользователя
#         cur.execute("UPDATE tableRegister SET isAdmin = %s WHERE login = %s", (True, admin_name))
#         conn.commit()
#     except Exception as e:
#         conn.rollback()
#         return jsonify({"status": "error", "message": str(e)}), 500
#     finally:
#         cur.close()
#         conn.close()

#     return jsonify({"status": "success"})


if __name__ == '__main__':
    app.run()
    