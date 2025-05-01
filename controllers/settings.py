from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from controllers.authentication import login_required
from models.dataBaseModels import conn
import psycopg2
from functools import wraps
import logging
from flask import current_app

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
@login_required
def settings_page():
    if not session.get('is_admin'):
        return redirect(url_for('mainStudent_page'))
    return render_template('settings.html')

@settings_bp.route('/add-theme', methods=['POST'])
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
            return jsonify({"success": False, "error": f"Тема '{theme_name}' уже существует"}), 409

        cur.execute("INSERT INTO theme (theme_name) VALUES (%s)", (theme_name,))
        conn.commit()

        return jsonify({"success": True, "message": f"Тема '{theme_name}' успешно добавлена"}), 201

    except psycopg2.Error as e:
        conn.rollback()
        current_app.logger.error(f"Database error in add_theme: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка базы данных при добавлении темы"}), 500 
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error in add_theme: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка сервера при добавлении темы"}), 500

@settings_bp.route('/delete-theme/<string:theme_name>', methods=['DELETE'])
def delete_theme(theme_name):
    cur = None
    try:
        cur = conn.cursor()

        cur.execute("SELECT theme_id FROM theme WHERE theme_name = %s", (theme_name,))
        if not cur.fetchone():
            return jsonify({
                "success": False, "error": f"Тема '{theme_name}' не найдена"}), 404

        cur.execute("DELETE FROM theme WHERE theme_name = %s", (theme_name,))
        conn.commit()

        return jsonify({"success": True, "message": f"Тема '{theme_name}' успешно удалена"})

    except psycopg2.Error as e:
        conn.rollback()
        current_app.logger.error(f"Ошибка базы данных при удалении темы: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка базы данных при удалении темы"}), 500

    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Ошибка при удалении темы: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка сервера при удалении темы"}), 500
    
@settings_bp.route('/get-admins', methods=['GET'])
def get_admins():
    cur = None
    try:
        cur = conn.cursor()
        cur.execute("SELECT login FROM users WHERE is_admin = TRUE")
        admins = cur.fetchall()
        admins_list = [{'name': admin[0]} for admin in admins]
        return jsonify(admins_list)
    except psycopg2.Error as e:
        current_app.logger.error(f"Database error in get_admins: {str(e)}")
        return jsonify({"error": "Ошибка базы данных"}), 500

@settings_bp.route('/get-students-for-admin', methods=['GET'])
def get_students_for_admin():
    cur = None
    try:
        cur = conn.cursor()
        cur.execute("SELECT login FROM users WHERE is_admin = FALSE")
        students = cur.fetchall()
        students_list = [{'name': student[0]} for student in students]
        return jsonify(students_list)
    except psycopg2.Error as e:
        current_app.logger.error(f"Database error in get_students_for_admin: {str(e)}")
        return jsonify({"error": "Ошибка базы данных"}), 500

@settings_bp.route('/add-admin', methods=['POST'])
def add_admin():
    if not request.is_json:
        return jsonify({"success": False, "error": "Некорректный формат запроса"}), 400

    data = request.get_json()
    student_name = data.get('student_name')

    if not student_name or student_name=="Выберите пользователя":
        return jsonify({"success": False, "error": "Укажите имя пользователя"}), 400

    cur = None
    try:
        cur = conn.cursor()
        cur.execute("UPDATE users SET is_admin = TRUE WHERE login = %s", (student_name,))
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": f"Права администратора успешно предоставлены"
        })

    except psycopg2.Error as e:
        conn.rollback()
        current_app.logger.error(f"Database error in add_admin: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка базы данных"}), 500
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error in add_admin: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка сервера"}), 500

@settings_bp.route('/delete-admin/<string:admin_name>', methods=['DELETE'])
def delete_admin(admin_name):
    cur = None
    try:
        cur = conn.cursor()

        if session.get('login') == admin_name:
            return jsonify({"success": False, "error": "Вы не можете забрать у себя права администратора"}), 400
        
        cur.execute("UPDATE users SET is_admin = FALSE WHERE login = %s", (admin_name,))
        
        if cur.rowcount == 0:
            return jsonify({"success": False, "error": f"Пользователь '{admin_name}' не найден"}), 404
            
        conn.commit()
        
        return jsonify({"success": True, "message": f"Права администратора успешно удалены"})

    except psycopg2.Error as e:
        conn.rollback()
        current_app.logger.error(f"Ошибка базы данных при удалении администратора: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка базы данных при удалении администратора"}), 500
        
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Ошибка при удалении администратора: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка сервера при удалении администратора"}), 500

@settings_bp.route('/delete-students', methods=['DELETE'])
def delete_students():
    if not request.is_json:
        return jsonify({"success": False, "error": "Некорректный формат запроса"}), 400

    data = request.get_json()
    direction_name = data.get('direction_name')
    group_name = data.get('group_name')

    if not direction_name or not group_name:
        return jsonify({"success": False, "error": "Требуется указать направление подготовки и группу"}), 400

    cur = None
    try:
        cur = conn.cursor()

        cur.execute("SELECT direction_id FROM direction WHERE direction_name = %s", (direction_name,))
        direction_id = cur.fetchone()
        if not direction_id:
            return jsonify({"success": False, "error": "Выберите направление подготовки"}), 404

        cur.execute("SELECT group_id FROM groups WHERE group_name = %s", (group_name,))
        group_id = cur.fetchone()
        if not group_id:
            return jsonify({"success": False, "error": "Выберите группу"}), 404

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
            return jsonify({"success": False, "error": "Не найдены пользователи с выбранными направлением подготовки и группы"}), 404

        cur.execute(
            "DELETE FROM users WHERE user_id IN %s AND is_admin = FALSE",
            (tuple(student[0] for student in student_ids),)
        )

        conn.commit()
        return jsonify({"success": True})
    except psycopg2.Error as e:
        conn.rollback()
        current_app.logger.error(f"Database error in delete_students: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка базы данных"}), 500
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error in delete_students: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка сервера"}), 500


@settings_bp.route('/delete-student/<string:student_name>', methods=['DELETE'])
def delete_student(student_name):
    cur = None
    try:
        cur = conn.cursor()
        if not student_name or student_name=="Выберите пользователя":
            return jsonify({"success": False, "message": f"Выберите пользователя"})

        cur.execute("DELETE FROM users WHERE login = %s", (student_name,))


        if cur.rowcount == 0:
            return jsonify({"success": False, "error": "Выберите пользователя"}), 404

        conn.commit()
        return jsonify({"success": True, "message": f"Пользователь успешно удален"})

    except psycopg2.Error as e:
        conn.rollback()
        current_app.logger.error(f"Database error in delete_student: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка базы данных"}), 500
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error in delete_student: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка сервера"}), 500
    

@settings_bp.route('/change-student-group', methods=['POST'])
def change_student_group():
    if not request.is_json:
        return jsonify({"success": False, "error": "Некорректный формат запроса"}), 400

    data = request.get_json()
    student_name = data.get('student_name')
    new_group_name = data.get('new_group_name')

    if not student_name or not new_group_name:
        return jsonify({"success": False, "error": "Необходимо указать имя пользователя и номер новой группы"}), 400

    cur = None
    try:
        cur = conn.cursor()

        cur.execute("SELECT user_id FROM users WHERE login = %s", (student_name,))
        user_id = cur.fetchone()
        if not user_id:
            return jsonify({"success": False, "error": "Выберите пользователя"}), 404

        cur.execute("SELECT group_id FROM groups WHERE group_name = %s", (new_group_name,))
        group_id = cur.fetchone()
        if not group_id:
            return jsonify({"success": False, "error": "Выберите группу"}), 404

        cur.execute(
            "UPDATE students SET group_id = %s WHERE user_id = %s",
            (group_id, user_id)
        )

        if cur.rowcount == 0:
            return jsonify({"success": False, "error": "Не удалось обновить группу у пользователя"}), 500

        conn.commit()
        return jsonify({"success": True, "message": f"Группа успешно обновлена"})

    except psycopg2.Error as e:
        conn.rollback()
        current_app.logger.error(f"Database error in change_student_group: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка базы данных"}), 500
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error in change_student_group: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка сервера"}), 500

@settings_bp.route('/change-student-direction', methods=['POST'])
def change_student_direction():
    if not request.is_json:
        return jsonify({"success": False, "error": "Некорректный формат запроса"}), 400

    data = request.get_json()
    student_name = data.get('student_name')
    new_direction_name = data.get('new_direction_name')

    if not student_name or not new_direction_name:
        return jsonify({"success": False, "error": "Необходимо указать имя пользователя и новое направление подготовки"}), 400

    cur = None
    try:
        cur = conn.cursor()

        cur.execute("SELECT user_id FROM users WHERE login = %s", (student_name,))
        user_id = cur.fetchone()
        if not user_id:
            return jsonify({"success": False, "error": "Выберите пользователя"}), 404

        cur.execute("SELECT direction_id FROM direction WHERE direction_name = %s", (new_direction_name,))
        direction_id = cur.fetchone()
        if not direction_id:
            return jsonify({"success": False, "error": "Выберите направление подготовки"}), 404

        cur.execute(
            "UPDATE users SET direction_id = %s WHERE user_id = %s",
            (direction_id, user_id)
        )

        if cur.rowcount == 0:
            return jsonify({"success": False, "error": "Не удалось обновить направление подготовки у пользователя"}), 500

        conn.commit()
        return jsonify({"success": True, "message": f"Направление подготовки успешно обновлено"})

    except psycopg2.Error as e:
        conn.rollback()
        current_app.logger.error(f"Database error in change_student_direction: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка базы данных"}), 500
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error in change_student_direction: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка сервера"}), 500
