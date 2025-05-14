from flask import Flask, request, render_template, jsonify, session
from flask import send_file, make_response, Blueprint
from werkzeug.utils import secure_filename
import mimetypes
import io
import psycopg2
from models.dataBaseModels import conn
from controllers.authentication import  login_required
import json 
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from urllib.parse import quote
from flask import jsonify
import base64
from datetime import datetime
from flask import current_app

education_bp = Blueprint('education', __name__)

@education_bp.route('/addQuestion', methods=['GET', 'POST'])
@login_required
def addQuestion_page():
    if not session.get('is_admin'):
        return render_template('mainStudent.html')
    return render_template('addQuestion.html')

@education_bp.route('/createTest', methods=['GET', 'POST'])
@login_required
def createTest_page():
    if not session.get('is_admin'):
        return render_template('mainStudent.html')

    return render_template('createTest.html')

@education_bp.route('/get-themes', methods=['GET'])
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
        current_app.logger.error(f"Database error in get_themes: {str(e)}")
        return jsonify({"error": "Ошибка базы данных"}), 500

@education_bp.route('/create-test', methods=['POST'])
@login_required
def create_test():
    try:
        theme_name = request.form.get('theme')
        easy = request.form.get('easyQuestions')
        medium = request.form.get('mediumQuestions')
        hard = request.form.get('hardQuestions')
        test_name = request.form.get('nameQuestion') 
        if not all([theme_name, test_name, easy, medium, hard]):
            return jsonify({"success": False, "error": "Не все обязательные поля заполнены"}), 400

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
            return jsonify({"success": False,"error": "Количество вопросов не может быть отрицательным"}), 400

        cur = conn.cursor()
        cur.execute("SELECT theme_id FROM theme WHERE theme_name = %s", (theme_name,))
        theme_result = cur.fetchone()
        
        if not theme_result:
            return jsonify({
                "success": False,
                "error": "Выбранная тема не существует"
            }), 404

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
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Ошибка базы данных"
        }), 500

    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера"
        }), 500

    finally:
        if 'cur' in locals():
            cur.close()

@education_bp.route('/get-tests-by-theme')
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
        current_app.logger.error(f"Error: {str(e)}")
        return jsonify([])

@education_bp.route('/delete-test/<int:test_id>', methods=['DELETE'])
@login_required
def delete_test(test_id):
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM test_options WHERE test_id = %s", (test_id,))
        conn.commit()
        return jsonify({"success": True, "message": "Тест удален"})
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка при удалении теста"}), 500


@education_bp.route('/get-test-questions/<string:test_name>')
@login_required
def get_test_questions(test_name):
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT easy_questions, medium_questions, hard_questions, theme_id
            FROM test_options
            WHERE test_name = %s
        """, (test_name,))
        test_settings = cur.fetchone()

        if not test_settings:
            return jsonify({"error": "Тест не найден"}), 404

        easy_questions, medium_questions, hard_questions, theme_id = test_settings

        questions = []
        unique_question_ids = set()

        if easy_questions > 0:
            cur.execute("""
                SELECT question_id, question_text, difficulty_level, question_type, score
                FROM questions
                WHERE theme_id = %s AND difficulty_level = 'легкий'
                ORDER BY RANDOM()
                LIMIT %s
            """, (theme_id, easy_questions))
            easy_questions_data = cur.fetchall()
            for question in easy_questions_data:
                if question[0] not in unique_question_ids:
                    unique_question_ids.add(question[0])
                    questions.append(question)

        if medium_questions > 0:
            cur.execute("""
                SELECT question_id, question_text, difficulty_level, question_type, score
                FROM questions
                WHERE theme_id = %s AND difficulty_level = 'средний'
                ORDER BY RANDOM()
                LIMIT %s
            """, (theme_id, medium_questions))
            medium_questions_data = cur.fetchall()
            for question in medium_questions_data:
                if question[0] not in unique_question_ids:
                    unique_question_ids.add(question[0])
                    questions.append(question)

        if hard_questions > 0:
            cur.execute("""
                SELECT question_id, question_text, difficulty_level, question_type, score
                FROM questions
                WHERE theme_id = %s AND difficulty_level = 'сложный'
                ORDER BY RANDOM()
                LIMIT %s
            """, (theme_id, hard_questions))
            hard_questions_data = cur.fetchall()
            for question in hard_questions_data:
                if question[0] not in unique_question_ids:
                    unique_question_ids.add(question[0])
                    questions.append(question)

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
        current_app.logger.error(f"Error: {str(e)}")
        return jsonify({"error": "Ошибка при загрузке вопросов"}), 500



@education_bp.route('/view-test/<string:test_name>')
@login_required
def view_test(test_name):
    try:
        cur = conn.cursor()
        cur.execute("SELECT test_id, test_name FROM test_options WHERE test_name = %s", (test_name,))
        test = cur.fetchone()

        # if not test:
        #     return render_template('error.html', message="Тест не найден"), 404

        test_id, test_name = test

        questions = get_test_questions(test_name).get_json()

        questions_json = json.dumps(questions)

        return render_template('viewTest.html',
                             test_id=test_id,
                             test_name=test_name,
                             questions=questions_json)
    except Exception as e:
        current_app.logger.error(f"Error: {str(e)}")
        return render_template('error.html', message="Ошибка при загрузке теста"), 500

@education_bp.route('/save_attempt', methods=['POST'])
def save_attempt():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Необходима авторизация'})

    data = request.get_json()

    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT attempt_id
            FROM attempts
            WHERE user_id = %s AND test_id = %s
        """, (session['user_id'], data['test_id']))

        attempt = cur.fetchone()

        if attempt:
            cur.execute("""
                UPDATE attempts
                SET mark = %s, attempt_data = NOW()
                WHERE attempt_id = %s
                RETURNING attempt_id
            """, (data['mark'], attempt[0]))
        else:
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

    
@education_bp.route('/get-directions', methods=['GET'])
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
        current_app.logger.error(f"Database error in get_directions: {str(e)}")
        return jsonify({"error": "Database error"}), 500

@education_bp.route('/get-groups', methods=['GET'])
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
        current_app.logger.error(f"Database error in get_groups: {str(e)}")
        return jsonify({"error": "Database error"}), 500

@education_bp.route('/delete-file-by-name/<string:file_name>', methods=['DELETE'])
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
        current_app.logger.error(f"Error deleting file: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка при удалении файла"}), 500

@education_bp.route('/section/<string:section_name>')
@login_required
def section_page(section_name):
    return render_template('pageLecturer.html', section_name=section_name)

@education_bp.route('/sectionStudent/<string:section_name>')
@login_required
def section_student_page(section_name):
    return render_template('pageStudent.html', section_name=section_name)

@education_bp.route('/upload-file', methods=['POST'])
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
        current_app.logger.error(f"Error uploading file: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка при загрузке файла"}), 500


@education_bp.route('/download-file-by-name/<string:file_name>', methods=['GET'])
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

        encoded_file_name = quote(file_name)

        response = make_response(send_file(
            file_stream,
            as_attachment=(disposition == 'attachment'),
            download_name=encoded_file_name,
            mimetype=mime_type
        ))

        response.headers['Content-Disposition'] = f'{disposition}; filename="{encoded_file_name}"'
        return response

    except Exception as e:
        current_app.logger.error(f"Error downloading file by name: {str(e)}")
    

@education_bp.route('/get-all-file-names', methods=['GET'])
@login_required
def get_all_file_names():
    cur = conn.cursor()
    try:
        cur.execute("SELECT file_name FROM files")
        files = cur.fetchall()
        return jsonify([file[0] for file in files])
    except Exception as e:
        current_app.logger.error(f"Error getting all file names: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка при получении имен файлов"}), 500
    
@education_bp.route('/get-attempts/<string:test_name>', methods=['GET'])
@login_required
def get_attempts(test_name):
    try:
        cur = conn.cursor()

        cur.execute("SELECT test_id FROM test_options WHERE test_name = %s", (test_name,))
        test = cur.fetchone()

        if not test:
            return jsonify({'success': False, 'error': 'Тест не найден'}), 404

        test_id = test[0]

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
        current_app.logger.error(f"Error getting attempts: {str(e)}")
        return jsonify({'success': False, 'error': 'Ошибка при получении попыток'}), 500
    
@education_bp.route('/get-files-by-theme', methods=['GET'])
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
        current_app.logger.error(f"Error getting files by theme: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка при получении файлов"}), 500


@education_bp.route('/create-question', methods=['POST'])
@login_required
def create_question():
    if not session.get('is_admin'):
        return jsonify({'status': 'error', 'message': 'Доступ запрещен'}), 403

    try:
        theme_name = request.form.get('theme')
        question_text = request.form.get('formulationQuestion')
        difficulty_level = request.form.get('difficulty-level')
        question_type = request.form.get('question-type')
        score = request.form.get('score')

        if not all([theme_name, question_text, difficulty_level, question_type, score]):
            return jsonify({'status': 'error', 'message': 'Не все обязательные поля заполнены'}), 400

        try:
            score = int(score)
            if score <= 0:
                return jsonify({'status': 'error', 'message': 'Баллы должны быть положительным числом'}), 400
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Баллы должны быть числом'}), 400

        cur = conn.cursor()

        cur.execute("SELECT theme_id FROM theme WHERE theme_name = %s", (theme_name,))
        theme = cur.fetchone()
        if not theme:
            return jsonify({'status': 'error', 'message': 'Тема не найдена'}), 404

        theme_id = theme[0]
        question_type_db = 'с вводом значения' if question_type == 'value' else 'с единственным выбором ответа'

        cur.execute(
            """INSERT INTO questions (theme_id, question_text, difficulty_level, question_type, score)
               VALUES (%s, %s, %s, %s, %s) RETURNING question_id""",
            (theme_id, question_text, difficulty_level, question_type_db, score)
        )
        question_id = cur.fetchone()[0]

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

        if 'fileInput' in request.files:
            file = request.files['fileInput']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_data = file.read()

                try:
                    cur.execute(
                        """INSERT INTO files (file_name, file_data)
                        VALUES (%s, %s) RETURNING file_id""",
                        (filename, file_data)
                    )
                    file_id = cur.fetchone()[0]

                    cur.execute(
                        """INSERT INTO question_files (question_id, file_id)
                        VALUES (%s, %s)""",
                        (question_id, file_id)
                    )
                    conn.commit()

                except Exception as e:
                    conn.rollback()
                    current_app.logger.error(f"Error processing file {filename}: {str(e)}")
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
        current_app.logger.error(f"Database error in create_question: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Ошибка базы данных при добавлении вопроса'
        }), 500
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Unexpected error in create_question: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Внутренняя ошибка сервера'
        }), 500
    finally:
        if 'cur' in locals():
            cur.close()
@education_bp.route('/generate-test-results-pdf', methods=['GET'])
@login_required
def generate_test_results_pdf():
    theme_name = request.args.get('theme_name')
    test_name = request.args.get('test_name')
    

    try:
        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))

        cur = conn.cursor()

        cur.execute("SELECT theme_id FROM theme WHERE theme_name = %s", (theme_name,))
        theme = cur.fetchone()
        if not theme:
            return jsonify({"success": False, "error": "Тема не найдена"}), 404

        theme_id = theme[0]

        cur.execute("SELECT test_id FROM test_options WHERE test_name = %s AND theme_id = %s", (test_name, theme_id))
        test = cur.fetchone()
        if not test:
            return jsonify({"success": False, "error": "Тест не найден"}), 404

        test_id = test[0]

        cur.execute("""
            SELECT u.login, a.mark, a.attempt_data, d.direction_name, g.group_name
            FROM attempts a
            JOIN users u ON a.user_id = u.user_id
            LEFT JOIN students s ON u.user_id = s.user_id
            LEFT JOIN direction d ON u.direction_id = d.direction_id
            LEFT JOIN groups g ON s.group_id = g.group_id
            WHERE a.test_id = %s
            ORDER BY a.attempt_data DESC
        """, (test_id,))

        results = cur.fetchall()

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        styles = getSampleStyleSheet()
        styles['Title'].fontName = 'Arial'
        styles['Normal'].fontName = 'Arial'

        title1 = Paragraph(f"Результаты теста: {test_name}",  styles['Title'] )
        title2 = Paragraph(f"Тема: {theme_name}", styles['Title'])

        elements.append(title1)
        elements.append(title2)

        data = [["Пользователь", "Оценка", "Дата попытки", "Направление подготовки", "Группа"]]
        for result in results:
            data.append([
                result[0],
                str(result[1]),
                result[2].strftime('%Y-%m-%d %H:%M:%S'),
                result[3] or '',
                result[4] or ''
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)
        doc.build(elements)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'results_{theme_name}_{test_name}.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        current_app.logger.error(f"Error generating test results PDF: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка при генерации PDF с результатами теста"}), 500
    finally:
        if 'cur' in locals():
            cur.close()


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
