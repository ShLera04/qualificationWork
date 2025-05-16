from flask import Blueprint, render_template, redirect, url_for, session
from controllers.authentication import login_required

user_bp= Blueprint('routes', __name__)

@user_bp.route('/mainLecturer')
@login_required
def mainLecturer_page():
    if not session.get('is_admin'):
        return redirect(url_for('routes.mainStudent_page'))
    return render_template('mainLecturer.html')

@user_bp.route('/mainStudent')
@login_required
def mainStudent_page():
    if session.get('is_admin'):
        return redirect(url_for('routes.mainLecturer_page'))
    return render_template('mainStudent.html')

@user_bp.route('/pageLecturer')
@login_required
def pageLecturer_page():
    if not session.get('is_admin'):
        return redirect(url_for('routes.pageStudent_page'))
    return render_template('pageLecturer.html')

@user_bp.route('/pageStudent')
@login_required
def pageStudent_page():
    if session.get('is_admin'):
        return redirect(url_for('routes.pageLecturer_page'))
    return render_template('pageStudent.html')