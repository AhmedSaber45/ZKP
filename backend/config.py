import os

DB_PATH = os.getenv("DB_PATH", "database/zkp_auth.db")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")