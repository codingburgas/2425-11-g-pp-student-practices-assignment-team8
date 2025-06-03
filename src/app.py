from flask import Flask
from config import Config
from src import create_app, db
from flask_mail import Mail

app = create_app(Config)
mail = Mail(app)

if __name__ == '__main__':
    with app.app_context():
        #db.drop_all()
        db.create_all()
        app.debug = True
        app.run()



