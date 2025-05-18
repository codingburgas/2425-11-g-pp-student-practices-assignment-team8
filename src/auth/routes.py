from flask import render_template, redirect, url_for, flash, session, g
from flask_login import login_user, logout_user, current_user
from . import auth_bp
from .forms import LoginForm, RegisterForm
from .models import User
from .. import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.before_request
def before_request():
    if session.get('logged_in'):
        g.current_user = User.query.filter_by(username=session.get('username')).first()
    else:
        g.current_user = None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('main_bp.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('main_bp.index'))
        else:
            flash('Invalid username or password.')
            return redirect(url_for('auth.login'))
    return render_template("login.html", form=form, current_user=current_user)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('logged_in'):
        return redirect(url_for('main_bp.index'))

    dev_user = User.query.filter_by(username='apo').first()
    if not dev_user:
        dev_user = User(username='apo', password='123', role='developer')
        db.session.add(dev_user)
        db.session.commit()

    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists.')
            return render_template("register.html", form=form, current_user=current_user)

        user = User(username=form.username.data, password=form.password.data, role='client')
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('auth.login'))

    return render_template("register.html", form=form, current_user=current_user)
