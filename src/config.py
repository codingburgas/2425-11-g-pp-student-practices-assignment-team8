import os

class Config:
    SECRET_KEY = os.environ.get('dqwedqwdqw', 'super secret key')
    SQLALCHEMY_DATABASE_URI = (f"mssql+pyodbc://MITAKA/proba?driver=ODBC+Driver+17+for+SQL+Server")
    SQLALCHEMY_TRACK_MODIFICATIONS = False