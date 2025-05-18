from flask import Flask
from config import Config
from src import create_app, db

app = create_app(Config)

if __name__ == '__main__':
    with app.app_context():
        #db.drop_all()
        db.create_all()
        app.debug = True
        app.run()



