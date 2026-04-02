import sqlite3
from config import DB_PATH
from utils.hashing_utils import hash_secret

def register_user(username, secret):
    hashed = hash_secret(secret)
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, hashed_secret) VALUES (?, ?)",
            (username, hashed)
        )
        conn.commit()
        return {"status": "success", "message": "User registered"}
    except sqlite3.IntegrityError as e:
        # Username already exists
        print(f"IntegrityError: {e}")
        return {"status": "error", "message": "User already exists"}
    except Exception as e:
        print(f"Database error: {e}")
        raise e
    finally:
        if conn:
            conn.close()


def login_user(username, proof):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT hashed_secret FROM users WHERE username=?",
            (username,)
        )
        user = cursor.fetchone()
        if not user:
            return {"status": "error", "message": "User not found"}
        if proof == user[0]:  # temporary, replace with ZKP later
            return {"status": "success", "message": "Login successful"}
        return {"status": "error", "message": "Invalid proof"}
    except Exception as e:
        print(f"Database error: {e}")
        raise e
    finally:
        if conn:
            conn.close()