from flask import Flask, request, render_template, redirect, jsonify, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask import send_file, make_response
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import os
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
from controllers.algorithms import algo_bp
import json 
logging.basicConfig(filename="main.log",
                    level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s",
                    filemode="w")

config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)
app.secret_key = config.get('app', 'secret_key')
is_test = config.getboolean('app', 'is_test')
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

app.register_blueprint(auth_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(algo_bp)


@app.route('/createTestcopy', methods=['GET', 'POST'])
@login_required
def createTestcopy_page():
    return render_template('createTestcopy.html')

@app.route('/addQuestion', methods=['GET', 'POST'])
@login_required
def addQuestion_page():
    if not session.get('is_admin'):
        # flash('Доступ запрещен', 'error')
        return render_template('mainStudent.html')
    return render_template('addQuestion.html')

@app.route('/test', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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

from flask import jsonify

import base64

@app.route('/get-test-questions/<string:test_name>')
@login_required
def get_test_questions(test_name):
    try:
        cur = conn.cursor()
        # Получаем настройки теста
        cur.execute("""
            SELECT easy_questions, medium_questions, hard_questions, theme_id
            FROM test_options
            WHERE test_name = %s
        """, (test_name,))
        test_settings = cur.fetchone()

        if not test_settings:
            return jsonify({"error": "Тест не найден"}), 404

        easy_questions, medium_questions, hard_questions, theme_id = test_settings

        # Получаем вопросы по уровню сложности и количеству
        questions = []

        if easy_questions > 0:
            cur.execute("""
                SELECT question_id, question_text, difficulty_level, question_type, score
                FROM questions
                WHERE theme_id = %s AND difficulty_level = 'легкий'
                ORDER BY RANDOM()
                LIMIT %s
            """, (theme_id, easy_questions))
            questions.extend(cur.fetchall())

        if medium_questions > 0:
            cur.execute("""
                SELECT question_id, question_text, difficulty_level, question_type, score
                FROM questions
                WHERE theme_id = %s AND difficulty_level = 'средний'
                ORDER BY RANDOM()
                LIMIT %s
            """, (theme_id, medium_questions))
            questions.extend(cur.fetchall())

        if hard_questions > 0:
            cur.execute("""
                SELECT question_id, question_text, difficulty_level, question_type, score
                FROM questions
                WHERE theme_id = %s AND difficulty_level = 'сложный'
                ORDER BY RANDOM()
                LIMIT %s
            """, (theme_id, hard_questions))
            questions.extend(cur.fetchall())

        # Преобразуем вопросы в список словарей
        formatted_questions = []
        for question in questions:
            question_id = question[0]
            cur.execute("""
                SELECT answer_id, answer_text, is_correct
                FROM answers
                WHERE question_id = %s
            """, (question_id,))
            answers = [{"answer_id": row[0], "answer_text": row[1], "is_correct": row[2]} for row in cur.fetchall()]

            cur.execute("""
                SELECT f.file_name, f.file_data
                FROM files f
                JOIN question_files qf ON f.file_id = qf.file_id
                WHERE qf.question_id = %s
            """, (question_id,))
            file_data = cur.fetchone()
            image_base64 = None
            if file_data:
                image_base64 = base64.b64encode(file_data[1]).decode('utf-8')

            formatted_questions.append({
                "question_id": question_id,
                "question_text": question[1],
                "difficulty_level": question[2],
                "question_type": question[3],
                "score": question[4],
                "answers": answers,
                "image": image_base64
            })

        return jsonify(formatted_questions)

    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return jsonify({"error": "Ошибка при загрузке вопросов"}), 500



@app.route('/view-test/<string:test_name>')
@login_required
def view_test(test_name):
    try:
        cur = conn.cursor()
        cur.execute("SELECT test_id, test_name FROM test_options WHERE test_name = %s", (test_name,))
        test = cur.fetchone()

        if not test:
            return render_template('error.html', message="Тест не найден"), 404

        test_id, test_name = test

        # Получаем вопросы для теста
        questions = get_test_questions(test_name).get_json()

        # Сериализация данных в JSON
        questions_json = json.dumps(questions)

        return render_template('viewTest.html',
                             test_id=test_id,
                             test_name=test_name,
                             questions=questions_json)
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return render_template('error.html', message="Ошибка при загрузке теста"), 500



@app.route('/save_attempt', methods=['POST'])
def save_attempt():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Необходима авторизация'})

    data = request.get_json()

    try:
        cur = conn.cursor()

        # Проверяем, существует ли уже запись для данного пользователя и теста
        cur.execute("""
            SELECT attempt_id
            FROM attempts
            WHERE user_id = %s AND test_id = %s
        """, (session['user_id'], data['test_id']))

        attempt = cur.fetchone()

        if attempt:
            # Если запись существует, обновляем её
            cur.execute("""
                UPDATE attempts
                SET mark = %s, attempt_data = NOW()
                WHERE attempt_id = %s
                RETURNING attempt_id
            """, (data['mark'], attempt[0]))
        else:
            # Если записи нет, создаем новую
            cur.execute("""
                INSERT INTO attempts (user_id, test_id, mark, attempt_data)
                VALUES (%s, %s, %s, NOW())
                RETURNING attempt_id
            """, (session['user_id'], data['test_id'], data['mark']))

        attempt_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({'success': True, 'attempt_id': attempt_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})

    
@app.route('/get-directions', methods=['GET'])
@login_required
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
@login_required
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
@login_required
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

@app.route('/section/<string:section_name>')
@login_required
def section_page(section_name):
    return render_template('pageLecturer.html', section_name=section_name)

@app.route('/sectionStudent/<string:section_name>')
@login_required
def section_student_page(section_name):
    return render_template('pageStudent.html', section_name=section_name)

@app.route('/upload-file', methods=['POST'])
@login_required
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
        cur.execute("INSERT INTO files (file_name, file_data) VALUES (%s, %s) RETURNING file_id",
                    (file_name, file_data))
        file_id = cur.fetchone()[0]

        cur.execute("SELECT theme_id FROM theme WHERE theme_name = %s", (section_name,))
        theme_id = cur.fetchone()

        if not theme_id:
            return jsonify({"success": False, "error": "Раздел не найден"}), 404

        theme_id = theme_id[0]

        cur.execute("INSERT INTO theme_files (theme_id, file_id) VALUES (%s, %s)",
                    (theme_id, file_id))

        conn.commit()
        return jsonify({"success": True, "file_id": file_id}), 201
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error uploading file: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка при загрузке файла"}), 500


@app.route('/download-file-by-name/<string:file_name>', methods=['GET'])
@login_required
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
@login_required
def get_all_file_names():
    cur = conn.cursor()
    try:
        cur.execute("SELECT file_name FROM files")
        files = cur.fetchall()
        return jsonify([file[0] for file in files])
    except Exception as e:
        app.logger.error(f"Error getting all file names: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка при получении имен файлов"}), 500
    
@app.route('/get-attempts/<string:test_name>', methods=['GET'])
@login_required
def get_attempts(test_name):
    try:
        cur = conn.cursor()

        # Сначала получаем test_id по test_name
        cur.execute("SELECT test_id FROM test_options WHERE test_name = %s", (test_name,))
        test = cur.fetchone()

        if not test:
            return jsonify({'success': False, 'error': 'Тест не найден'}), 404

        test_id = test[0]

        # Затем получаем попытки по test_id
        cur.execute("""
            SELECT mark, attempt_data
            FROM attempts
            WHERE user_id = %s AND test_id = %s
            ORDER BY attempt_data DESC
        """, (session['user_id'], test_id))

        attempts = []
        for row in cur.fetchall():
            attempts.append({
                'mark': row[0],
                'attempt_data': row[1].strftime('%Y-%m-%d %H:%M:%S')
            })

        return jsonify({'success': True, 'attempts': attempts})
    except Exception as e:
        app.logger.error(f"Error getting attempts: {str(e)}")
        return jsonify({'success': False, 'error': 'Ошибка при получении попыток'}), 500
    
@app.route('/get-files-by-theme', methods=['GET'])
@login_required
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


@app.route('/create-question', methods=['POST'])
@login_required
def create_question():
    if not session.get('is_admin'):
        return jsonify({'status': 'error', 'message': 'Доступ запрещен'}), 403

    try:
        # Получаем данные из формы
        theme_name = request.form.get('theme')
        question_text = request.form.get('formulationQuestion')
        difficulty_level = request.form.get('difficulty-level')
        question_type = request.form.get('question-type')
        score = request.form.get('score')  # Получаем баллы из формы

        # Валидация обязательных полей
        if not all([theme_name, question_text, difficulty_level, question_type, score]):
            return jsonify({'status': 'error', 'message': 'Не все обязательные поля заполнены'}), 400

        # Проверяем, что score - число
        try:
            score = int(score)
            if score <= 0:
                return jsonify({'status': 'error', 'message': 'Баллы должны быть положительным числом'}), 400
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Баллы должны быть числом'}), 400

        cur = conn.cursor()

        # 1. Находим ID темы
        cur.execute("SELECT theme_id FROM theme WHERE theme_name = %s", (theme_name,))
        theme = cur.fetchone()
        if not theme:
            return jsonify({'status': 'error', 'message': 'Тема не найдена'}), 404

        theme_id = theme[0]
        question_type_db = 'с вводом значения' if question_type == 'value' else 'с единственным выбором ответа'

        # 2. Вставляем вопрос в базу данных (добавляем score)
        cur.execute(
            """INSERT INTO questions (theme_id, question_text, difficulty_level, question_type, score)
               VALUES (%s, %s, %s, %s, %s) RETURNING question_id""",
            (theme_id, question_text, difficulty_level, question_type_db, score)
        )
        question_id = cur.fetchone()[0]

        # 3. Обрабатываем ответы в зависимости от типа вопроса
        if question_type == 'value':
            correct_value = request.form.get('correct-value')
            if not correct_value:
                conn.rollback()
                return jsonify({'status': 'error', 'message': 'Не указано правильное значение'}), 400

            cur.execute(
                """INSERT INTO answers (question_id, answer_text, is_correct)
                   VALUES (%s, %s, %s)""",
                (question_id, correct_value, True)
            )

        elif question_type == 'single':
            options = []
            i = 1
            while True:
                option = request.form.get(f'option-{i}')
                if option is None:
                    break
                options.append(option)
                i += 1

            correct_option = int(request.form.get('correct-option', 0))

            if len(options) < 2:
                conn.rollback()
                return jsonify({'status': 'error', 'message': 'Должно быть минимум 2 варианта ответа'}), 400

            if not (1 <= correct_option <= len(options)):
                conn.rollback()
                return jsonify({'status': 'error', 'message': 'Не выбран правильный вариант'}), 400

            for i, option_text in enumerate(options, start=1):
                cur.execute(
                    """INSERT INTO answers (question_id, answer_text, is_correct)
                       VALUES (%s, %s, %s)""",
                    (question_id, option_text, i == correct_option)
                )

        # 4. Обрабатываем загруженный файл
        if 'fileInput' in request.files:  # Изменили с 'file' на 'fileInput'
            file = request.files['fileInput']  # Получаем только первый файл
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_data = file.read()

                try:
                    # Вставляем файл в базу
                    cur.execute(
                        """INSERT INTO files (file_name, file_data)
                        VALUES (%s, %s) RETURNING file_id""",
                        (filename, file_data)  # Убрали psycopg2.Binary()
                    )
                    file_id = cur.fetchone()[0]

                    # Связываем файл с вопросом
                    cur.execute(
                        """INSERT INTO question_files (question_id, file_id)
                        VALUES (%s, %s)""",
                        (question_id, file_id)
                    )
                    conn.commit()  # Коммитим после каждого файла

                except Exception as e:
                    conn.rollback()
                    app.logger.error(f"Error processing file {filename}: {str(e)}")
                    return jsonify({
                        'status': 'error',
                        'message': 'Ошибка при обработке файла'
                    }), 500

        conn.commit()
        return jsonify({
            'status': 'success',
            'message': 'Вопрос успешно добавлен',
            'question_id': question_id
        })

    except psycopg2.Error as e:
        conn.rollback()
        app.logger.error(f"Database error in create_question: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Ошибка базы данных при добавлении вопроса'
        }), 500
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Unexpected error in create_question: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Внутренняя ошибка сервера'
        }), 500
    finally:
        if 'cur' in locals():
            cur.close()



def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    print(is_test)
    if is_test:
        app.run()
    else:
        app.run(host='0.0.0.0', port=5000) 