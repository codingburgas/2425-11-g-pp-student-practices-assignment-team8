from datetime import timedelta
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    app.template_folder = template_dir

    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    app.config['SESSION_PERMANENT'] = False
    login_manager.remember_cookie_duration = timedelta(seconds=0)
    login_manager.session_protection = 'strong'

    with app.app_context():
        db.create_all()

    from .auth import auth_bp
    from .main import main_bp
    from .profile import prof_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(prof_bp)

    return app
