from flask import render_template, flash, redirect, url_for
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
    if not current_user.is_authenticated or current_user.role != 'developer':
        flash("Access denied")
        return redirect(url_for('main_bp.index'))

    clients = User.query.filter_by(role='client').all()
    return render_template("clients.html", clients=clients)
