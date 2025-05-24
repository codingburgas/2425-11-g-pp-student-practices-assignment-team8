from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from . import auth_bp
from .forms import LoginForm, RegisterForm
from .models import User
from .. import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=False)
            return redirect(url_for('main_bp.index'))
        flash('Invalid username or password.')

    return render_template("login.html", form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))

    # Ensure dev user exists
    if not User.query.filter_by(username='apo').first():
        dev = User(username='apo', password='123', role='developer')
        db.session.add(dev)
        db.session.commit()

    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.')
        else:
            new_user = User(username=form.username.data,
                            password=form.password.data,
                            role='client')
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.')
            return redirect(url_for('auth.login'))

    return render_template("register.html", form=form)