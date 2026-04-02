import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_PATH = os.path.join(BASE_DIR, "..", "database", "identities.db")


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def create_table_if_not_exists():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS identities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        identity_hash TEXT,
        public_key TEXT
    )
    """)

    conn.commit()
    conn.close()