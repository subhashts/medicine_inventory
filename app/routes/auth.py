from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.models import Admin, Worker
from app import db, login_manager

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith('W'):
        return Worker.query.get(user_id)
    return Admin.query.get(int(user_id))

@auth_bp.route('/')
def home():
    if current_user.is_authenticated:
        if isinstance(current_user, Admin):
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('worker.dashboard'))
    return render_template('auth/home.html')

@auth_bp.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if Admin.query.filter_by(email=email).first():
            flash("Email already registered.")
            return redirect(url_for('auth.admin_signup'))
        admin = Admin(name=name, email=email)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        login_user(admin)
        return redirect(url_for('admin.dashboard'))
    return render_template('auth/admin_signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identity = request.form['identity']
        password = request.form['password']
        if identity.startswith('W'):
            worker = Worker.query.get(identity)
            if worker and worker.check_password(password):
                login_user(worker)
                return redirect(url_for('worker.dashboard'))
            flash("Invalid Worker credentials.")
        else:
            admin = Admin.query.filter_by(email=identity).first()
            if admin and admin.check_password(password):
                login_user(admin)
                return redirect(url_for('admin.dashboard'))
            flash("Invalid Admin credentials.")
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.home'))
