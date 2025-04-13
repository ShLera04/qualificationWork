from flask import Flask, request, render_template, redirect, jsonify, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask import send_file, make_response
import mimetypes
import io
from datetime import datetime
import pytz
import re
import random
import psycopg2
from psycopg2 import sql
import logging
import configparser, sys
from flask import session
import numpy as np
from models.dataBaseModels import conn
from functools import wraps

logging.basicConfig(filename="main.log",
                    level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s",
                    filemode="w")

config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)
app.secret_key = config.get('app', 'secret_key')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Пожалуйста, войдите в систему для доступа к этой странице', 'warning')
            return redirect(url_for('entrance_page'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/addQuestion', methods=['GET', 'POST'])
def addQuestion_page():
    return render_template('addQuestion.html')

@app.route('/test', methods=['GET', 'POST'])
def test_page():
    return render_template('test.html')

@app.route('/createTest', methods=['GET', 'POST'])
def createTest_page():
    return render_template('createTest.html')

@app.route('/tttt', methods=['GET', 'POST'])
def tttt_page():
    return render_template('tttt.html')

@app.route('/mainLecturer')
@login_required
def mainLecturer_page():
    if not session.get('is_admin'):
        flash('Доступ запрещен', 'error')
        return redirect(url_for('mainStudent_page'))
    return render_template('mainLecturer.html')

@app.route('/mainStudent')
@login_required
def mainStudent_page():
    if session.get('is_admin'):
        flash('Доступ запрещен', 'error')
        return redirect(url_for('mainLecturer_page'))
    return render_template('mainStudent.html')


@app.route('/pageLecturer')
def pageLecturer_page():
    return render_template('pageLecturer.html')

@app.route('/pageStudent')
def pageStudent_page():
    return render_template('pageStudent.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT group_name FROM groups ORDER BY group_name")
        groups = [group[0] for group in cur.fetchall()]
        
        cur.execute("SELECT direction_name FROM direction ORDER BY direction_name")
        directions = [direction[0] for direction in cur.fetchall()]
        
        if request.method == 'POST':
            login = request.form['name']
            email = request.form['email']
            password = request.form['password']
            repetpassword = request.form['repetpassword']
            direction_name = request.form.get('direction', '').strip()
            group_name = request.form.get('group', '').strip()
            print(direction_name, group_name)

            if not direction_name or not group_name:
                flash("Пожалуйста, выберите корректное направление подготовки и группу", 'warning')
                return redirect(url_for('register'))

            if password != repetpassword:
                flash('Пароли не совпадают', 'error')
                return redirect(url_for('register'))
            
            if not is_strong_password(password):
                flash('Пароль должен содержать минимум 8 символов, включая заглавные и строчные буквы, цифры и специальные символы', 'error')
                return redirect(url_for('register'))

            cur.execute("SELECT * FROM users WHERE login = %s", (login,))
            if cur.fetchone():
                flash('Пользователь с таким логином уже существует', 'error')
                return redirect(url_for('register'))

            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                flash('Пользователь с таким email уже существует', 'error')
                return redirect(url_for('register'))

            cur.execute("SELECT direction_id FROM direction WHERE direction_name = %s", (direction_name,))
            direction_result = cur.fetchone()
            if not direction_result:
                flash('Выбранное направление не найдено', 'error')
                return redirect(url_for('register'))
            direction_id = direction_result[0]

            cur.execute("SELECT group_id FROM groups WHERE group_name = %s", (group_name,))
            group_result = cur.fetchone()
            if not group_result:
                flash('Выбранная группа не найдена', 'error')
                return redirect(url_for('register'))
            group_id = group_result[0]

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
            created_at = datetime.now(pytz.timezone('Europe/Moscow'))

            try:
                cur.execute(
                    "INSERT INTO users (login, password, email, is_admin, direction_id, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s) RETURNING user_id",
                    (login, hashed_password, email, False, direction_id, created_at)
                )
                user_id = cur.fetchone()[0]

                cur.execute(
                    "INSERT INTO students (user_id, group_id) "
                    "VALUES (%s, %s)",
                    (user_id, group_id)
                )

                conn.commit()
                flash('Регистрация прошла успешно', 'success')
                return redirect(url_for('register'))
                
            except Exception as e:
                conn.rollback()
                flash(f'Ошибка при регистрации: {str(e)}', 'error')
                app.logger.error(f"Registration error: {str(e)}")
                
    except Exception as e:
        flash(f'Ошибка при обработке запроса: {str(e)}', 'error')
        app.logger.error(f"Request processing error: {str(e)}")

    return render_template('register.html', groups=groups, directions=directions)

@app.route('/entrance', methods=['GET', 'POST'])
def entrance_page():
    if request.method == 'POST':
        cur = None
        try:
            login = request.form.get('login')
            password = request.form.get('password')

            if not login or not password:
                flash('Заполните все поля', 'error')
                return redirect(url_for('entrance_page'))

            cur = conn.cursor()

            cur.execute("SELECT user_id, password, is_admin, login FROM users WHERE login = %s", (login,))
            user = cur.fetchone()

            if not user:
                flash('Неверный логин или пароль', 'error')
                return redirect(url_for('entrance_page'))

            if check_password_hash(user[1], password):
                session['user_id'] = user[0]
                session['is_admin'] = user[2]
                session['login'] = user[3]
                session['logged_in'] = True
                
                if user[2]:
                    return redirect(url_for('mainLecturer_page'))
                else:
                    return redirect(url_for('mainStudent_page'))
            else:
                flash('Неверный логин или пароль', 'error')
                return redirect(url_for('entrance_page'))

        except Exception as e:
            flash(f'Ошибка входа: {str(e)}', 'error')
            app.logger.error(f"Login error: {str(e)}")
            return redirect(url_for('entrance_page'))

    return render_template('entrance.html')


@app.route('/get-themes', methods=['GET'])
def get_themes():
    cur = None
    try:
        cur = conn.cursor()
        
        cur.execute("SELECT theme_id, theme_name FROM theme")
        
        themes = cur.fetchall()
        
        themes_list = [{'name': theme[1]} for theme in themes]
        print(themes_list)
        return jsonify(themes_list)
        
    except psycopg2.Error as e:
        app.logger.error(f"Database error in get_themes: {str(e)}")
        return jsonify({"error": "Ошибка базы данных"}), 500
        
@app.route('/add-theme', methods=['POST'])
def add_theme():
    if not request.is_json:
        return jsonify({"success": False, "error": "Неверный формат запроса"}), 400

    data = request.get_json()
    theme_name = data.get('theme_name')

    if not theme_name:
        return jsonify({"success": False, "error": "Название темы обязательно для заполнения"}), 400

    cur = None
    try:
        cur = conn.cursor()

        cur.execute("SELECT theme_id FROM theme WHERE theme_name = %s", (theme_name,))
        if cur.fetchone():
            return jsonify({"success": False, "error": "Тема с таким названием уже существует"}), 409

        cur.execute("INSERT INTO theme (theme_name) VALUES (%s)", (theme_name,))
        conn.commit()

        return jsonify({"success": True, "message": "Тема успешно добавлена"}), 201

    except psycopg2.Error as e:
        conn.rollback()
        app.logger.error(f"Database error in add_theme: {str(e)}")
        flash('Ошибка базы данных при добавлении темы', 'error')
        return jsonify({"success": False, "error": "Database error"}), 500 
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error in add_theme: {str(e)}")
        flash('Ошибка сервера при добавлении темы', 'error')
        return jsonify({"success": False, "error": "Server error"}), 500


@app.route('/delete-theme/<string:theme_name>', methods=['DELETE'])
def delete_theme(theme_name):
    cur = None
    try:
        cur = conn.cursor()

        cur.execute("SELECT theme_id FROM theme WHERE theme_name = %s", (theme_name,))
        if not cur.fetchone():
            return jsonify({
                "success": False, 
                "error": f"Тема '{theme_name}' не найдена"
            }), 404

        cur.execute("DELETE FROM theme WHERE theme_name = %s", (theme_name,))
        conn.commit()

        return jsonify({
            "success": True,
            "message": f"Тема '{theme_name}' успешно удалена"
        })

    except psycopg2.Error as e:
        conn.rollback()
        app.logger.error(f"Ошибка базы данных при удалении темы: {str(e)}")
        return jsonify({
            "success": False, 
            "error": "Ошибка базы данных при удалении темы"
        }), 500

    except Exception as e:
        conn.rollback()
        app.logger.error(f"Ошибка при удалении темы: {str(e)}")
        return jsonify({
            "success": False, 
            "error": "Ошибка сервера при удалении темы"
        }), 500

@app.route('/get-admins', methods=['GET'])
def get_admins():
    cur = None
    try:
        cur = conn.cursor()
        cur.execute("SELECT login FROM users WHERE is_admin = TRUE")
        admins = cur.fetchall()
        admins_list = [{'name': admin[0]} for admin in admins]
        return jsonify(admins_list)
    except psycopg2.Error as e:
        app.logger.error(f"Database error in get_admins: {str(e)}")
        return jsonify({"error": "Database error"}), 500

@app.route('/get-students-for-admin', methods=['GET'])
def get_students_for_admin():
    cur = None
    try:
        cur = conn.cursor()
        cur.execute("SELECT login FROM users WHERE is_admin = FALSE")
        students = cur.fetchall()
        students_list = [{'name': student[0]} for student in students]
        return jsonify(students_list)
    except psycopg2.Error as e:
        app.logger.error(f"Database error in get_students_for_admin: {str(e)}")
        return jsonify({"error": "Database error"}), 500

@app.route('/add-admin', methods=['POST'])
def add_admin():
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    data = request.get_json()
    student_name = data.get('student_name')

    if not student_name:
        return jsonify({"success": False, "error": "Student name is required"}), 400

    cur = None
    try:
        cur = conn.cursor()
        cur.execute("UPDATE users SET is_admin = TRUE WHERE login = %s", (student_name,))
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": f"Права администратора предоставлены для {student_name}"
        })

    except psycopg2.Error as e:
        conn.rollback()
        app.logger.error(f"Database error in add_admin: {str(e)}")
        return jsonify({"success": False, "error": "Database error"}), 500
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error in add_admin: {str(e)}")
        return jsonify({"success": False, "error": "Server error"}), 500

@app.route('/delete-admin/<string:admin_name>', methods=['DELETE'])
def delete_admin(admin_name):
    cur = None
    try:
        cur = conn.cursor()

        if session.get('login') == admin_name:
            return jsonify({
                "success": False,
                "error": "Вы не можете забрать у себя права администратора"
            }), 400
        
        cur.execute("UPDATE users SET is_admin = FALSE WHERE login = %s", (admin_name,))
        
        if cur.rowcount == 0:
            return jsonify({
                "success": False,
                "error": f"Пользователь '{admin_name}' не найден"
            }), 404
            
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": f"Права администратора для '{admin_name}' успешно удалены"
        })

    except psycopg2.Error as e:
        conn.rollback()
        app.logger.error(f"Ошибка базы данных при удалении администратора: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Ошибка базы данных при удалении администратора"
        }), 500
        
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Ошибка при удалении администратора: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Ошибка сервера при удалении администратора"
        }), 500
    

@app.route('/get-directions', methods=['GET'])
def get_directions():
    cur = None
    try:
        cur = conn.cursor()
        cur.execute("SELECT direction_name FROM direction")
        directions = cur.fetchall()
        directions_list = [{'name': direction[0]} for direction in directions]
        return jsonify(directions_list)
    except psycopg2.Error as e:
        app.logger.error(f"Database error in get_directions: {str(e)}")
        return jsonify({"error": "Database error"}), 500

@app.route('/get-groups', methods=['GET'])
def get_groups():
    cur = None
    try:
        cur = conn.cursor()
        cur.execute("SELECT group_name FROM groups")
        groups = cur.fetchall()
        groups_list = [{'name': group[0]} for group in groups]
        return jsonify(groups_list)
    except psycopg2.Error as e:
        app.logger.error(f"Database error in get_groups: {str(e)}")
        return jsonify({"error": "Database error"}), 500

@app.route('/delete-students', methods=['DELETE'])
def delete_students():
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    data = request.get_json()
    direction_name = data.get('direction_name')
    group_name = data.get('group_name')

    if not direction_name or not group_name:
        return jsonify({"success": False, "error": "Direction name and group name are required"}), 400

    cur = None
    try:
        cur = conn.cursor()

        cur.execute("SELECT direction_id FROM direction WHERE direction_name = %s", (direction_name,))
        direction_id = cur.fetchone()
        if not direction_id:
            return jsonify({"success": False, "error": "Direction not found"}), 404

        cur.execute("SELECT group_id FROM groups WHERE group_name = %s", (group_name,))
        group_id = cur.fetchone()
        if not group_id:
            return jsonify({"success": False, "error": "Group not found"}), 404

        cur.execute(
            """
            SELECT u.user_id
            FROM users u
            JOIN students s ON u.user_id = s.user_id
            WHERE u.direction_id = %s AND s.group_id = %s
            """,
            (direction_id, group_id)
        )
        student_ids = cur.fetchall()

        if not student_ids:
            return jsonify({"success": False, "error": "No students found in the specified group and direction"}), 404

        cur.execute(
            "DELETE FROM users WHERE user_id IN %s AND is_admin = FALSE",
            (tuple(student[0] for student in student_ids),)
        )

        conn.commit()
        return jsonify({"success": True})
    except psycopg2.Error as e:
        conn.rollback()
        app.logger.error(f"Database error in delete_students: {str(e)}")
        return jsonify({"success": False, "error": "Database error"}), 500
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error in delete_students: {str(e)}")
        return jsonify({"success": False, "error": "Server error"}), 500


@app.route('/delete-student/<string:student_name>', methods=['DELETE'])
def delete_student(student_name):
    cur = None
    try:
        cur = conn.cursor()

        cur.execute("DELETE FROM users WHERE login = %s", (student_name,))

        if cur.rowcount == 0:
            return jsonify({"success": False, "error": "Студент не найден"}), 404

        conn.commit()
        return jsonify({"success": True, "message": f"Студент {student_name} успешно удален"})

    except psycopg2.Error as e:
        conn.rollback()
        app.logger.error(f"Database error in delete_student: {str(e)}")
        return jsonify({"success": False, "error": "Database error"}), 500
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error in delete_student: {str(e)}")
        return jsonify({"success": False, "error": "Server error"}), 500
    

@app.route('/change-student-group', methods=['POST'])
def change_student_group():
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    data = request.get_json()
    student_name = data.get('student_name')
    new_group_name = data.get('new_group_name')

    if not student_name or not new_group_name:
        return jsonify({"success": False, "error": "Student name and new group name are required"}), 400

    cur = None
    try:
        cur = conn.cursor()

        cur.execute("SELECT user_id FROM users WHERE login = %s", (student_name,))
        user_id = cur.fetchone()
        if not user_id:
            return jsonify({"success": False, "error": "Student not found"}), 404

        cur.execute("SELECT group_id FROM groups WHERE group_name = %s", (new_group_name,))
        group_id = cur.fetchone()
        if not group_id:
            return jsonify({"success": False, "error": "Group not found"}), 404

        cur.execute(
            "UPDATE students SET group_id = %s WHERE user_id = %s",
            (group_id, user_id)
        )

        if cur.rowcount == 0:
            return jsonify({"success": False, "error": "Failed to update student group"}), 500

        conn.commit()
        return jsonify({"success": True, "message": f"Group successfully changed for {student_name}"})

    except psycopg2.Error as e:
        conn.rollback()
        app.logger.error(f"Database error in change_student_group: {str(e)}")
        return jsonify({"success": False, "error": "Database error"}), 500
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error in change_student_group: {str(e)}")
        return jsonify({"success": False, "error": "Server error"}), 500

@app.route('/change-student-direction', methods=['POST'])
def change_student_direction():
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    data = request.get_json()
    student_name = data.get('student_name')
    new_direction_name = data.get('new_direction_name')

    if not student_name or not new_direction_name:
        return jsonify({"success": False, "error": "Student name and new direction name are required"}), 400

    cur = None
    try:
        cur = conn.cursor()

        cur.execute("SELECT user_id FROM users WHERE login = %s", (student_name,))
        user_id = cur.fetchone()
        if not user_id:
            return jsonify({"success": False, "error": "Пользователь не выбран"}), 404

        cur.execute("SELECT direction_id FROM direction WHERE direction_name = %s", (new_direction_name,))
        direction_id = cur.fetchone()
        if not direction_id:
            return jsonify({"success": False, "error": "Направление подготовки не выбрано"}), 404

        cur.execute(
            "UPDATE users SET direction_id = %s WHERE user_id = %s",
            (direction_id, user_id)
        )

        if cur.rowcount == 0:
            return jsonify({"success": False, "error": "Failed to update student direction"}), 500

        conn.commit()
        return jsonify({"success": True, "message": f"Direction successfully changed for {student_name}"})

    except psycopg2.Error as e:
        conn.rollback()
        app.logger.error(f"Database error in change_student_direction: {str(e)}")
        return jsonify({"success": False, "error": "Database error"}), 500
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error in change_student_direction: {str(e)}")
        return jsonify({"success": False, "error": "Server error"}), 500

@app.route('/delete-file-by-name/<string:file_name>', methods=['DELETE'])
def delete_file_by_name(file_name):
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM files WHERE file_name = %s", (file_name,))
        if cur.rowcount == 0:
            return jsonify({"success": False, "error": "Файл не найден"}), 404
        conn.commit()
        return jsonify({"success": True, "message": f"Файл {file_name} успешно удален"})
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error deleting file: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка при удалении файла"}), 500


def is_saddle_point(matrix, row, col):
    element = matrix[row][col]
    if element != min(matrix[row]):
        return False
    if element != max(matrix[i][col] for i in range(len(matrix))):
        return False
    return True

def find_saddle_points_for_both(matrix_a, matrix_b):
    def find_saddle_points(matrix):
        saddle_points = []
        if not matrix:
            return saddle_points
        row_min = [min(row) for row in matrix]
        col_max = [max(col) for col in zip(*matrix)]
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                if matrix[i][j] == row_min[i] and matrix[i][j] == col_max[j]:
                    saddle_points.append((i, j))
        return saddle_points

    return {
        "matrix_a": find_saddle_points(matrix_a),
        "matrix_b": find_saddle_points(matrix_b)
    }

def is_pareto_optimal(matrix_a, matrix_b):
    pareto_optimal_points = []
    n = len(matrix_a)
    m = len(matrix_a[0])

    for i in range(n):
        for j in range(m):
            current_a = matrix_a[i][j]
            current_b = matrix_b[i][j]
            is_optimal = True
            for x in range(n):
                for y in range(m):
                    if (matrix_a[x][y] >= current_a and
                        matrix_b[x][y] >= current_b and
                        (matrix_a[x][y] > current_a or matrix_b[x][y] > current_b)):
                        is_optimal = False
                        break
                if not is_optimal:
                    break
            if is_optimal:
                pareto_optimal_points.append((i, j, current_a, current_b))

    return pareto_optimal_points

def is_nash_equilibrium(matrix_a, matrix_b):
    nash_points = []
    n = len(matrix_a)
    m = len(matrix_a[0])

    for i in range(n):
        for j in range(m):
            current_a = matrix_a[i][j]
            current_b = matrix_b[i][j]
            is_nash = True

            for k in range(n):
                if matrix_a[k][j] > current_a:
                    is_nash = False
                    break

            if is_nash:
                for l in range(m):
                    if matrix_b[i][l] > current_b:
                        is_nash = False
                        break

            if is_nash:
                nash_points.append((i, j, current_a, current_b))

    return nash_points

def generate_matrix_with_saddle_points(rows, cols, saddle_points_count, max_attempts=100):
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        matrix = np.random.randint(0, 100, size=(rows, cols)).tolist()

        def find_saddle_points(matrix):
            saddle_points = []
            for i in range(len(matrix)):
                for j in range(len(matrix[0])):
                    if (matrix[i][j] == min(matrix[i]) and
                        matrix[i][j] == max([row[j] for row in matrix])):
                        saddle_points.append([i, j])
            return saddle_points

        current_saddle_points = find_saddle_points(matrix)
        while len(current_saddle_points) < saddle_points_count:
            i, j = np.random.randint(0, rows), np.random.randint(0, cols)
            matrix[i] = [max(x, matrix[i][j]) for x in matrix[i]]
            for row in matrix:
                row[j] = min(row[j], matrix[i][j])
            current_saddle_points = find_saddle_points(matrix)

        while len(current_saddle_points) > saddle_points_count:
            idx = np.random.randint(0, len(current_saddle_points))
            i, j = current_saddle_points[idx]
            matrix[i][j] = np.random.randint(0, 100)
            current_saddle_points = find_saddle_points(matrix)

        if len(current_saddle_points) == saddle_points_count:
            return {
                "matrix": matrix,
                "saddle_points": current_saddle_points,
                "rows": rows,
                "cols": cols,
                "k": saddle_points_count
            }

    raise ValueError("Не удалось сгенерировать матрицу с заданным количеством седловых точек")


@app.route('/generate_saddle_matrix', methods=['POST'])
def generate_saddle_matrix():
    try:
        data = request.get_json()
        rows = int(data['rows'])
        cols = int(data['cols'])
        k = int(data['k'])
        
        if k > rows * cols:
            return jsonify({
                "error": f"Количество седловых точек не может превышать {rows * cols}"
            }), 400
        
        result = generate_matrix_with_saddle_points(rows, cols, k)
        return jsonify(result)
    except ValueError as ve:
        return jsonify({
            "error": str(ve)
        }), 500
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/section/<string:section_name>')
def section_page(section_name):
    return render_template('pageLecturer.html', section_name=section_name)

@app.route('/sectionStudent/<string:section_name>')
def section_student_page(section_name):
    return render_template('pageStudent.html', section_name=section_name)

@app.route('/saddle_points', methods=['POST'])
def saddle_points():
    data = request.get_json()
    matrix_a = data['matrix_a']
    matrix_b = data['matrix_b']
    result = find_saddle_points_for_both(matrix_a, matrix_b)
    return jsonify(result)

@app.route('/pareto_optimal', methods=['POST'])
def pareto_optimal():
    data = request.get_json()
    matrix_a = data['matrix_a']
    matrix_b = data['matrix_b']
    result = is_pareto_optimal(matrix_a, matrix_b)
    return jsonify(result)

@app.route('/nash_equilibrium', methods=['POST'])
def nash_equilibrium():
    data = request.get_json()
    matrix_a = data['matrix_a']
    matrix_b = data['matrix_b']
    result = is_nash_equilibrium(matrix_a, matrix_b)
    if result:
        return jsonify(result)
    else:
        return jsonify([])
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    session.pop('login', None)
    session.pop('logged_in', None)
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('entrance_page'))

@app.route('/get_user_info')
def get_user_info():
    return jsonify({
        'logged_in': session.get('logged_in', False),
        'login': session.get('login', 'Гость')
    })

@app.route('/upload-file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "Файл не найден"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "Не выбран файл"}), 400

    file_data = file.read()
    file_name = file.filename
    section_name = request.form.get('section_name')

    if not section_name:
        return jsonify({"success": False, "error": "Название раздела не найдено"}), 400

    cur = conn.cursor()
    try:
        # Вставка файла в таблицу files
        cur.execute("INSERT INTO files (file_name, file_data) VALUES (%s, %s) RETURNING file_id",
                    (file_name, file_data))
        file_id = cur.fetchone()[0]

        # Получение theme_id по section_name
        cur.execute("SELECT theme_id FROM theme WHERE theme_name = %s", (section_name,))
        theme_id = cur.fetchone()

        if not theme_id:
            return jsonify({"success": False, "error": "Раздел не найден"}), 404

        theme_id = theme_id[0]

        # Вставка записи в таблицу theme_files
        cur.execute("INSERT INTO theme_files (theme_id, file_id) VALUES (%s, %s)",
                    (theme_id, file_id))

        conn.commit()
        return jsonify({"success": True, "file_id": file_id}), 201
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error uploading file: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка при загрузке файла"}), 500


@app.route('/download-file-by-name/<string:file_name>', methods=['GET'])
def download_file_by_name(file_name):
    cur = conn.cursor()
    try:
        cur.execute("SELECT file_data FROM files WHERE file_name = %s", (file_name,))
        file_record = cur.fetchone()

        if not file_record:
            return jsonify({"success": False, "error": "Файл не найден"}), 404

        file_data = file_record[0]
        file_stream = io.BytesIO(file_data)

        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type is None:
            mime_type = 'application/octet-stream'

        # Для PDF устанавливаем inline, для других типов - attachment
        disposition = 'inline' if file_name.lower().endswith('.pdf') else 'attachment'
        
        response = make_response(send_file(
            file_stream,
            as_attachment=(disposition == 'attachment'),
            download_name=file_name,
            mimetype=mime_type
        ))
        
        response.headers['Content-Disposition'] = f'{disposition}; filename="{file_name}"'
        return response

    except Exception as e:
        app.logger.error(f"Error downloading file by name: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка при скачивании файла"}), 500
    

@app.route('/get-all-file-names', methods=['GET'])
def get_all_file_names():
    cur = conn.cursor()
    try:
        cur.execute("SELECT file_name FROM files")
        files = cur.fetchall()
        return jsonify([file[0] for file in files])
    except Exception as e:
        app.logger.error(f"Error getting all file names: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка при получении имен файлов"}), 500
    
@app.route('/get-files-by-theme', methods=['GET'])
def get_files_by_theme():
    theme_name = request.args.get('theme_name')
    if not theme_name:
        return jsonify({"success": False, "error": "Название раздела не найдено"}), 400

    cur = conn.cursor()
    try:
        cur.execute("SELECT theme_id FROM theme WHERE theme_name = %s", (theme_name,))
        theme_id = cur.fetchone()

        if not theme_id:
            return jsonify({"success": False, "error": "Раздел не найден"}), 404

        theme_id = theme_id[0]

        cur.execute("""
            SELECT f.file_name
            FROM files f
            JOIN theme_files tf ON f.file_id = tf.file_id
            WHERE tf.theme_id = %s
        """, (theme_id,))

        files = cur.fetchall()
        return jsonify([file[0] for file in files])
    except Exception as e:
        app.logger.error(f"Error getting files by theme: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка при получении файлов"}), 500

def is_strong_password(password):
    pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&+-])[A-Za-z\d@$!%*?&+-]{8,}$')
    return bool(pattern.match(password))
if __name__ == '__main__':
    app.run()