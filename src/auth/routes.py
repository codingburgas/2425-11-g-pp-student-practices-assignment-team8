from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from . import auth_bp
from .forms import LoginForm, RegisterForm
from .models import User
from .. import db, login_manager, mail
from ..config import Config

# Token serializer
serializer = URLSafeTimedSerializer(Config.SECRET_KEY)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def send_login_notification_email(user):
    msg = Message("Login Notification", recipients=[user.email])
    msg.body = f"Hello {user.username}, you have successfully logged in."
    mail.send(msg)

def send_verification_email(user):
    token = serializer.dumps(user.email, salt='email-confirm')
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    msg = Message('Confirm Your Email', recipients=[user.email])
    msg.body = f'''Hi {user.username}, please click the link to verify your account:
{confirm_url}

This link will expire in 1 hour.'''
    mail.send(msg)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            if not user.is_active:
                flash('Please verify your email before logging in.')
                return redirect(url_for('auth.login'))
            login_user(user, remember=False)

            if user.email:
                send_login_notification_email(user)

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
            email='apo@example.com',
            role='developer',
            is_active=True  # Ensure dev account is active
        )
        dev.password = '123'
        db.session.add(dev)
        db.session.commit()

    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.')
        elif User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.')
        else:
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                role='client',
                is_active=False  # Set to inactive until verified
            )
            new_user.password = form.password.data
            db.session.add(new_user)
            db.session.commit()
            send_verification_email(new_user)
            flash('Registration successful! Check your email to verify your account.')
            return redirect(url_for('auth.login'))

    return render_template("register.html", form=form)

@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return '<h3>The confirmation link has expired.</h3>'
    except BadSignature:
        return '<h3>Invalid or broken confirmation link.</h3>'

    user = User.query.filter_by(email=email).first_or_404()
    if user.is_active:
        return '<h3>Account already confirmed. You can now log in.</h3>'

    user.is_active = True
    db.session.commit()
    return '<h3>Email confirmed successfully. You can now <a href="/auth/login">log in</a>.</h3>'
