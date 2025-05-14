from flask import Blueprint, render_template, redirect, url_for, flash, session, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz
import re
from models.dataBaseModels import conn
from functools import wraps
from flask import current_app

auth_bp = Blueprint('auth', __name__)

def is_strong_password(password):
    pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&+-])[A-Za-z\d@$!%*?&+-]{8,}$')
    return bool(pattern.match(password))

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Пожалуйста, войдите в систему для доступа к этой странице', 'warning')
            return redirect(url_for('auth.entrance_page'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT group_name FROM groups ORDER BY group_name")
        groups = [group[0] for group in cur.fetchall()]
        
        cur.execute("SELECT direction_name FROM direction ORDER BY direction_name")
        directions = [direction[0] for direction in cur.fetchall()]

        form_data = {
            'name': '',
            'email': '',
            'direction': '',
            'group': ''
        }
        
        if request.method == 'POST':
            form_data = {
                'name': request.form.get('name', ''),
                'email': request.form.get('email', ''),
                'direction': request.form.get('direction', ''),
                'group': request.form.get('group', '')
            }
            login = request.form['name']
            email = request.form['email']
            password = request.form['password']
            repetpassword = request.form['repetpassword']
            direction_name = request.form.get('direction', '').strip()
            group_name = request.form.get('group', '').strip()

            if  not is_valid_email(email):
                flash("Пожалуйста, введите корректный адрес электронной почты", 'warning')
                return render_template('register.html', groups=groups, directions=directions, form=form_data)

            if not direction_name or not group_name:
                flash("Пожалуйста, выберите корректное направление подготовки и группу", 'warning')
                return render_template('register.html', groups=groups, directions=directions, form=form_data)

            if password != repetpassword:
                flash('Пароли не совпадают', 'error')
                return render_template('register.html', groups=groups, directions=directions, form=form_data)
            
            if not is_strong_password(password):
                flash('Пароль должен содержать минимум 8 символов, включая заглавные и строчные буквы, цифры и специальные символы', 'error')
                return render_template('register.html', groups=groups, directions=directions, form=form_data)

            cur.execute("SELECT * FROM users WHERE login = %s", (login,))
            if cur.fetchone():
                flash('Пользователь с таким логином уже существует', 'error')
                return render_template('register.html', groups=groups, directions=directions, form=form_data)

            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                flash('Пользователь с таким email уже существует', 'error')
                return render_template('register.html', groups=groups, directions=directions, form=form_data)

            cur.execute("SELECT direction_id FROM direction WHERE direction_name = %s", (direction_name,))
            direction_result = cur.fetchone()
            if not direction_result:
                flash('Выбранное направление не найдено', 'error')
                return render_template('register.html', groups=groups, directions=directions, form=form_data)
            direction_id = direction_result[0]

            cur.execute("SELECT group_id FROM groups WHERE group_name = %s", (group_name,))
            group_result = cur.fetchone()
            if not group_result:
                flash('Выбранная группа не найдена', 'error')
                return render_template('register.html', groups=groups, directions=directions, form=form_data)
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
                form_data = {
                    'name': '',
                    'email': '',
                    'direction': '',
                    'group': ''
                }
                return redirect(url_for('auth.register'))
                
            except Exception as e:
                conn.rollback()
                flash(f'Ошибка при регистрации', 'error')
                current_app.logger.error(f"Registration error: {str(e)}")
                
    except Exception as e:
        flash(f'Ошибка при обработке запроса', 'error')
        current_app.logger.error(f"Request processing error: {str(e)}")

    return render_template('register.html', groups=groups, directions=directions, form=form_data)

@auth_bp.route('/entrance', methods=['GET', 'POST'])
def entrance_page():
    if request.method == 'POST':
        cur = None
        try:
            login = request.form.get('login', '')
            password = request.form.get('password', '')

            if not login or not password:
                flash('Заполните все поля', 'error')
                return render_template('entrance.html', login=login)

            cur = conn.cursor()

            cur.execute("SELECT user_id, password, is_admin, login FROM users WHERE login = %s", (login,))
            user = cur.fetchone()

            if not user:
                flash('Неверный логин или пароль', 'error')
                return render_template('entrance.html', login=login)

            if check_password_hash(user[1], password):
                session['user_id'] = user[0]
                session['is_admin'] = user[2]
                session['login'] = user[3]
                session['logged_in'] = True
                
                if user[2]:
                    return redirect(url_for('routes.mainLecturer_page'))
                else:
                    return redirect(url_for('routes.mainStudent_page'))
            else:
                flash('Неверный логин или пароль', 'error')
                return render_template('entrance.html', login=login)

        except Exception as e:
            flash(f'Ошибка входа', 'error')
            current_app.logger.error(f"Login error: {str(e)}")
            return render_template('entrance.html', login=login)

    return render_template('entrance.html', login='')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    session.pop('login', None)
    session.pop('logged_in', None)
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('auth.entrance_page'))

@auth_bp.route('/get_user_info')
@login_required
def get_user_info():
    return jsonify({
        'logged_in': session.get('logged_in', False),
        'login': session.get('login', 'Гость')
    })
