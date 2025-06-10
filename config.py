import os
from datetime import timedelta
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = quote_plus(os.getenv('SECRET_KEY'))

    # Azure SQL Database connection
    DB_USER = quote_plus(os.getenv('DB_USER'))
    DB_PASSWORD = quote_plus(os.getenv('DB_PASSWORD'))
    DB_SERVER = quote_plus(os.getenv('DB_SERVER'))
    DB_NAME = quote_plus(os.getenv('DB_NAME'))

    # Construct the connection string for Azure SQL Database with correct driver name
    SQLALCHEMY_DATABASE_URI = (
        f'mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:1433/{DB_NAME}'
        '?driver=ODBC+Driver+17+for+SQL+Server'
        '&Encrypt=yes'
        '&TrustServerCertificate=yes'
        '&Connection+Timeout=30'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'