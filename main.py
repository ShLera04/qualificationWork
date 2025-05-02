from flask import Flask, request, render_template, redirect, jsonify, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask import send_file, make_response
import mimetypes
import io
import pytz
import re
import random
import psycopg2
from psycopg2 import sql
import logging
import configparser, sys
import numpy as np
from models.dataBaseModels import conn
from functools import wraps
from datetime import datetime, timedelta
from controllers.authentication import auth_bp, login_required
from controllers.settings import settings_bp

logging.basicConfig(filename="main.log",
                    level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s",
                    filemode="w")

config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)
app.secret_key = config.get('app', 'secret_key')
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

app.register_blueprint(auth_bp)
app.register_blueprint(settings_bp)

@app.route('/addQuestion', methods=['GET', 'POST'])
@login_required
def addQuestion_page():
    if not session.get('is_admin'):
        # flash('Доступ запрещен', 'error')
        return render_template('mainStudent.html')
    return render_template('addQuestion.html')

@app.route('/test', methods=['GET', 'POST'])
def test_page():
    return render_template('test.html')

@app.route('/createTest', methods=['GET', 'POST'])
@login_required
def createTest_page():
    if not session.get('is_admin'):
        # flash('Доступ запрещен', 'error')
        return render_template('mainStudent.html')

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
@login_required
def pageLecturer_page():
    if not session.get('is_admin'):
        # flash('Доступ запрещен', 'error')
        return redirect(url_for('pageStudent_page'))
    return render_template('pageLecturer.html')

@app.route('/pageStudent')
@login_required
def pageStudent_page():
    if session.get('is_admin'):
        # flash('Доступ запрещен', 'error')
        return redirect(url_for('pageLecturer_page'))
    return render_template('pageStudent.html')

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

@app.route('/create-test', methods=['POST'])
def create_test():
    try:
        # Проверка аутентификации
        if 'user_id' not in session:
            return jsonify({
                "success": False,
                "error": "Для создания теста требуется авторизация"
            }), 401

        # Валидация данных
        theme_name = request.form.get('theme')
        easy = request.form.get('easyQuestions')
        medium = request.form.get('mediumQuestions')
        hard = request.form.get('hardQuestions')
        test_name = request.form.get('nameQuestion') 
        if not all([theme_name, test_name, easy, medium, hard]):
            return jsonify({
                "success": False,
                "error": "Не все обязательные поля заполнены"
            }), 400

        try:
            easy = int(easy)
            medium = int(medium)
            hard = int(hard)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Количество вопросов должно быть числом"
            }), 400

        if any(n < 0 for n in [easy, medium, hard]):
            return jsonify({
                "success": False,
                "error": "Количество вопросов не может быть отрицательным"
            }), 400

        # Поиск темы
        cur = conn.cursor()
        cur.execute("SELECT theme_id FROM theme WHERE theme_name = %s", (theme_name,))
        theme_result = cur.fetchone()
        
        if not theme_result:
            return jsonify({
                "success": False,
                "error": "Выбранная тема не существует"
            }), 404

        # Создание теста
        theme_id = theme_result[0]
        test_name = request.form.get('nameQuestion') 
        creation_date = datetime.now()

        cur.execute("""
            INSERT INTO test_options (
                test_name, user_id, theme_id, 
                difficulty_level, easy_questions, 
                medium_questions, hard_questions, deadline
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING test_id
        """, (test_name, session['user_id'], theme_id, 
              request.form['testDifficulty'], easy, 
              medium, hard, creation_date))
        
        new_test = cur.fetchone()
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Тест успешно создан",
            "test_id": new_test[0],
            "test_name": test_name
        }), 201

    except psycopg2.Error as e:
        conn.rollback()
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Ошибка базы данных"
        }), 500

    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера"
        }), 500

    finally:
        if 'cur' in locals():
            cur.close()
@app.route('/get-tests-by-theme')
def get_tests_by_theme():
    theme_name = request.args.get('theme_name')
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT test_id, test_name 
            FROM test_options 
            WHERE theme_id = (SELECT theme_id FROM theme WHERE theme_name = %s)
        """, (theme_name,))
        tests = [{'test_id': row[0], 'test_name': row[1]} for row in cur.fetchall()]
        return jsonify(tests)
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return jsonify([])

@app.route('/delete-test/<int:test_id>', methods=['DELETE'])
def delete_test(test_id):
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM test_options WHERE test_id = %s", (test_id,))
        conn.commit()
        return jsonify({"success": True, "message": "Тест удален"})
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка при удалении теста"}), 500

@app.route('/view-test/<int:test_id>')
def view_test(test_id):
    # Здесь реализуйте логику отображения теста
    return render_template('viewTest.html', test_id=test_id)

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
    
@app.route('/calculate_mixed_matrix', methods=['POST'])
def calculate_mixed_matrix():
    try:
        data = request.get_json()
        x = float(data['x'])
        y = float(data['y'])
        v = float(data['v'])
        a12 = float(data['a12'])

        # Проверка допустимости значений
        if not (0 <= x <= 1) or not (0 <= y <= 1):
            return jsonify({'error': 'Стратегии должны быть в диапазоне [0, 1]'}), 400

        if y == 0 or (1 - x) == 0:
            return jsonify({'error': 'Недопустимые значения для расчета'}), 400

        # Вычисления
        a21 = (v * (y - x) + a12 * x * (1 - y)) / (y * (1 - x))
        a11 = (v - a12 * (1 - y)) / y
        a22 = (v - a12 * x) / (1 - x)

        # Форматирование результатов
        matrix = [
            [round(a11, 10), round(a12, 10)],
            [round(a21, 10), round(a22, 10)]
        ]

        return jsonify({'matrix': matrix})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

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

if __name__ == '__main__':
    app.run()