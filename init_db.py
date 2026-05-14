import sqlite3
import os

DB_PATH = "database/zkp_auth.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        public_key INTEGER,
        email TEXT UNIQUE,
        salt TEXT,
        verifier TEXT
    );

    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        amount REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voter_id TEXT,
        choice TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS identities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        identity_proof TEXT
    );

    CREATE TABLE IF NOT EXISTS blockchain_blocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        index_num INTEGER,
        timestamp TEXT,
        data TEXT,
        previous_hash TEXT,
        hash TEXT
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("DB created successfully")