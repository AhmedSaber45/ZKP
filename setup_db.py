import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "zkp_auth.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"


def ensure_user_columns(connection):
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    if "email" not in existing_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    if "salt" not in existing_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN salt TEXT")
    if "verifier" not in existing_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN verifier TEXT")

    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email)")


with sqlite3.connect(DB_PATH) as connection:
    with open(SCHEMA_PATH, encoding="utf-8") as schema_file:
        connection.executescript(schema_file.read())

    ensure_user_columns(connection)
    connection.commit()

print("Database initialized successfully!")