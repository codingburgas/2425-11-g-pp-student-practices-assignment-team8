from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user

from . import prof_bp
from .. import db
from ..auth.forms import ProfileForm
from ..auth.models import User



@prof_bp.route("/settings")
def settings():
    return render_template("dashboard.html", current_user=current_user)
@prof_bp.route('/profile', methods=['GET', 'POST'])

def profile():
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        if current_user.username != form.username.data:
            if db.session.query(User).filter_by(username=form.username.data).first():
                flash("Username already taken.")
                return redirect(url_for('profile.profile'))
            current_user.username = form.username.data

        current_user.password = form.password.data

        db.session.commit()
        flash("Profile updated.")
        return redirect(url_for('profile.profile'))

    return render_template("dashboard.html", form=form, current_user=current_user)
@prof_bp.route("/clients")
def view_clients():
    if not current_user.is_authenticated or (current_user.role != 'developer' and current_user.role != 'teacher'):
        flash("Access denied")
        return redirect(url_for('main_bp.index'))

    clients = User.query.filter_by(role='client').all()
    return render_template("clients.html", clients=clients)

@prof_bp.route("/promote", methods=['POST'])
def promote_user():
    if not current_user.is_authenticated or current_user.role != 'developer':
        flash("Access denied.")
        return redirect(url_for('main_bp.index'))

    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()

    if not user:
        flash("User not found.")
    elif user.role == 'teacher':
        flash(f"{username} is already a teacher.")
    elif user.role == 'developer':
        flash("Cannot promote a developer.")
    else:
        user.role = 'teacher'
        db.session.commit()
        flash(f"{username} has been promoted to teacher.")

    return redirect(url_for('profile.promote_page'))

@prof_bp.route("/promote_user")
def promote_page():
    if not current_user.is_authenticated or current_user.role != 'developer':
        flash("Access denied.")
        return redirect(url_for('main_bp.index'))

    users = User.query.filter(User.role != 'developer').all()
    return render_template("promote.html", users=users)

