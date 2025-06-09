import os

class Config:
    SECRET_KEY = os.environ.get('dqwedqwdqw', 'super secret key')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mssql+pyodbc://SD2358\\SQLEXPRESS/proba?driver=ODBC+Driver+17+for+SQL+Server'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False