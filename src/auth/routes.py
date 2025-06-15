from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from itsdangerous import URLSafeTimedSerializer
from .forms import LoginForm, RegistrationForm
from . import auth_bp
from .models import User
from .. import db, login_manager
from config import Config
from .send_verification import *

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
                flash('Account not activated.')
                return redirect(url_for('auth_bp.login'))

            login_user(user, remember=form.remember_me.data if hasattr(form, 'remember_me') else False)

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main_bp.index'))

        flash('Invalid username or password.')
    return render_template("login.html", form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('auth_bp.login'))

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
            code = generate_verification_code()
            send_verification_email(new_user.email, code)
            # Store code and email in session for verification
            session['verification_code'] = str(code)
            session['verification_email'] = new_user.email
            return redirect(url_for('auth.verify_code'))

    return render_template("register.html", form=form)

@auth_bp.route('/verify-code', methods=['GET', 'POST'])
def verify_code():
    email = session.get('verification_email')
    if not email:
        flash('No verification process started. Please register first.', 'danger')
        return redirect(url_for('auth.register'))
    error = None
    if request.method == 'POST':
        entered_code = request.form.get('code')
        real_code = session.get('verification_code')
        if entered_code == real_code:
            flash('Email verified successfully!', 'success')
            # Optionally, mark user as verified in DB here
            session.pop('verification_code', None)
            session.pop('verification_email', None)
            return redirect(url_for('auth.login'))
        else:
            error = 'Incorrect code. Please try again.'
    return render_template('verification_sent.html', email=email, error=error)

@auth_bp.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        email = request.form.get("email")

        if not email:
            flash("Please enter an email address.", "error")
            return redirect(url_for("auth.verify"))

        code = generate_verification_code()
        success = send_verification_email(email, code)

        if success:
            flash("Verification email sent!", "success")
            return render_template("verification_sent.html", email=email, code=code)
        else:
            flash("Failed to send email. Try again later.", "error")
            return redirect(url_for("auth.verify"))

    return render_template("verify.html")

@auth_bp.route('/debug_session')
@login_required
def debug_session():
    from flask import session, current_app

    debug_info = {
        'session_data': dict(session),
        'current_user': current_user.username if current_user.is_authenticated else 'Not authenticated',
        'session_type': current_app.config.get('SESSION_TYPE'),
        'is_azure': current_app.config.get('WEBSITE_SITE_NAME') is not None,
        'session_file_dir': current_app.config.get('SESSION_FILE_DIR', 'Not set')
    }

    return f"<pre>{debug_info}</pre>"