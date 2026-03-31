import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR, "database", "zkp_auth.db")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
