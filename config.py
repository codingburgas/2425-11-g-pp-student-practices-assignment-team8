import os
from datetime import timedelta
from dotenv import load_dotenv
import sqlitecloud
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SESSION_TYPE = 'null'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    conn = sqlitecloud.connect(
        "sqlitecloud://cb0zln5enz.g4.sqlite.cloud:8860/chinook.sqlite?apikey=iH1c7C6VkEDX9vLfhR6awZ1V8UfiWRfnz46bJzwMIyA")
    for table in ['users', 'clubs', 'user_surveys', 'event_details', "club_events", "club_members", "club_request",
                  "model_info", "sqlite_sequence", "training_results", ]:  # etc.
        cursor = conn.execute(f'SELECT * FROM {table};')
        print(f"\n{table} rows:")
        for row in cursor.fetchall():
            print(dict(row))
    result = cursor.fetchone()

    print(result)

    conn.close()
