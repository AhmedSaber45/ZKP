from flask import Blueprint, request, jsonify
import sqlite3
import os

auth_bp = Blueprint('auth', __name__)
DB_PATH = "database/zkp_auth.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    secret = data.get('secret') # In a real app, use hashing

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND hashed_secret = ?', (username, secret)).fetchone()
    conn.close()

    if user:
        return jsonify({"message": "Login Successful", "username": username}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    secret = data.get('secret')

    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, hashed_secret) VALUES (?, ?)', (username, secret))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "User already exists"}), 400
    finally:
        conn.close()

    return jsonify({"message": "Registration Successful"}), 201
