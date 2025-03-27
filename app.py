from flask import Flask, request, render_template, redirect,jsonify, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost/dataBase?client_encoding=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Создание экземпляра SQLAlchemy
db = SQLAlchemy(app)

# Определение моделей
class AllUser(db.Model):
    __tablename__ = 'allusers'
    user_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Europe/Moscow')))

class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('allusers.user_id'), nullable=False, unique=True)
    direction_id = db.Column(db.Integer, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('allgroups.group_id'), nullable=False)
    user = db.relationship('AllUser', backref=db.backref('students', lazy=True))


class Group(db.Model):
    __tablename__ = 'allgroups'
    group_id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(255), nullable=False)

class Direction(db.Model):
    __tablename__ = 'direction'
    direction_id = db.Column(db.Integer, primary_key=True)
    direction_name = db.Column(db.String(255), nullable=False)

class Theme(db.Model):
    __tablename__ = 'theme'
    theme_id = db.Column(db.Integer, primary_key=True)
    theme_name = db.Column(db.String(255), nullable=False)

class Lecturer(db.Model):
    __tablename__ = 'lecturers'
    lecturer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('allusers.user_id'), nullable=False)
    direction_id = db.Column(db.Integer, nullable=False)
    user = db.relationship('AllUser', backref=db.backref('lecturers', lazy=True))

@app.route('/entrance', methods=['GET', 'POST'])
def entrance_page():
    return render_template('entrance.html')

@app.route('/mainStudent')
def mainStudent_page():
    return render_template('mainStudent.html')

@app.route('/mainLecturer')
def mainLecturer_page():
    return render_template('mainLecturer.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/pageLecturer')
def pageLecturer_page():
    return render_template('pageLecturer.html')

# Маршрут для регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    groups = Group.query.all()
    directions = Direction.query.all()

    if request.method == 'POST':
        login = request.form['name']
        email = request.form['email']
        password = request.form['password']
        repetpassword = request.form['repetpassword']
        direction_id = request.form['direction']
        group_id = request.form['group']

        if (direction_id == "" or group_id == ""): 
            flash("Пожалуйста, выберите корректное направление подготовки и группу!", 'warning')
            return redirect(url_for('register'))

        
        # Проверка совпадения паролей
        if password != repetpassword:
            flash('Пароли не совпадают!', 'error')
            return redirect(url_for('register'))
        
        if not is_strong_password(password):
            flash('Пароль должен содержать минимум 8 символов, включая заглавные и строчные буквы, цифры и специальные символы.', 'error')
            return redirect(url_for('register'))

        # Проверка наличия пользователя с таким логином
        existing_user = AllUser.query.filter_by(login=login).first()
        if existing_user:
            flash('Пользователь с таким логином уже существует!', 'error')
            return redirect(url_for('register'))
        

        # Хеширование пароля
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

        # Создание нового пользователя
        new_user = AllUser(login=login, password=hashed_password, email=email, is_admin=False)

        try:
            db.session.add(new_user)
            db.session.commit()

            # Создание записи в таблице students
            new_student = Student(user_id=new_user.user_id, direction_id=direction_id, group_id=group_id)
            db.session.add(new_student)
            db.session.commit()

            flash('Регистрация прошла успешно!', 'success')
            return redirect(url_for('register'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при регистрации: {str(e)}', 'error')

    return render_template('register.html', groups=groups, directions=directions)

@app.route('/entrance.html', methods=['GET', 'POST'])
def entrance():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']

        # Проверка наличия пользователя с таким логином
        user = AllUser.query.filter_by(login=login).first()

        if user and check_password_hash(user.password, password):
            # flash('Вход выполнен успешно!', 'success')
            return redirect(url_for('mainStudent_page'))  # Перенаправьте на главную страницу или другую защищенную страницу
        else:
            flash('Неверный логин или пароль!', 'error')
            return redirect(url_for('entrance_page'))

    return render_template('entrance.html')

def is_saddle_point(matrix, row, col):
    element = matrix[row][col]
    if element != min(matrix[row]):
        return False
    if element != max(matrix[i][col] for i in range(len(matrix))):
        return False
    return True

def find_saddle_points(matrix):
    saddle_points = []
    row_min = [min(row) for row in matrix]
    col_max = [max(col) for col in zip(*matrix)]

    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] == row_min[i] and matrix[i][j] == col_max[j]:
                saddle_points.append((i, j, matrix[i][j]))

    return saddle_points

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

            # Проверка строки (игрок 1 не может улучшить свой выигрыш)
            for k in range(n):
                if matrix_a[k][j] >= current_a:
                    is_nash = False
                    break

            # Проверка столбца (игрок 2 не может улучшить свой выигрыш)
            if is_nash:
                for l in range(m):
                    if matrix_b[i][l] >= current_b:
                        is_nash = False
                        break

            if is_nash:
                nash_points.append((i, j, current_a, current_b))

    return nash_points

@app.route('/saddle_points', methods=['POST'])
def saddle_points():
    data = request.get_json()
    matrix = data['matrix']
    result = find_saddle_points(matrix)
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


@app.route('/get-themes', methods=['GET'])
def get_themes():
    themes = Theme.query.all()
    themes_list = [{'name': theme.theme_name} for theme in themes]
    return jsonify(themes_list)

@app.route('/get-lecturers', methods=['GET'])
def get_lecturers():
    lecturers = Lecturer.query.all()
    lecturers_list = [{'name': lecturer.user.login, 'lecturer_id': lecturer.lecturer_id} for lecturer in lecturers]
    return jsonify(lecturers_list)



@app.route('/get-students', methods=['GET'])
def get_students():
    students = Student.query.all()
    students_list = [{'name': student.user.login, 'student_id': student.student_id} for student in students]
    return jsonify(students_list)



@app.route('/add-theme',methods=['GET', 'POST'])
def add_theme():
    data = request.get_json()
    new_theme = Theme(theme_name=data['theme_name'])
    try:
        db.session.add(new_theme)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/delete-theme/<int:theme_id>', methods=['DELETE'])
def delete_theme(theme_id):
    theme = Theme.query.get(theme_id)
    if theme:
        try:
            db.session.delete(theme)
            db.session.commit()
            return jsonify({"success": True})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500
    else:
        return jsonify({"success": False, "error": "Theme not found"}), 404

@app.route('/delete-lecturer/<int:lecturer_id>', methods=['DELETE'])
def delete_lecturer(lecturer_id):
    lecturer = Lecturer.query.get(lecturer_id)
    if lecturer:
        try:
            db.session.delete(lecturer)
            db.session.commit()
            return jsonify({"success": True})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500
    else:
        return jsonify({"success": False, "error": "Lecturer not found"}), 404

@app.route('/add-admin', methods=['POST'])
def add_admin():
    data = request.get_json()
    student_id = data['student_id']
    student = Student.query.get(student_id)

    if student:
        try:
            new_lecturer = Lecturer(user_id=student.user_id, direction_id=student.direction_id)
            db.session.add(new_lecturer)
            db.session.commit()
            return jsonify({"success": True})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500
    else:
        return jsonify({"success": False, "error": "Student not found"}), 404


def is_strong_password(password):
    # Регулярное выражение для проверки пароля
    pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
    return bool(pattern.match(password))



if __name__ == '__main__':
    app.run(debug=True)
