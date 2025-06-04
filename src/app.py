from src import create_app, db, login_manager
from flask import Flask
from src.config import Config

app = create_app(Config)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from src.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app

if __name__ == '__main__':
    with app.app_context():
        #db.drop_all()
        db.create_all()
        app.debug = True
        app.run()



