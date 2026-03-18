from flask import Blueprint, jsonify, request

from services.auth_service import is_email_registered, register_user, start_login, verify_login


auth_bp = Blueprint("auth", __name__)


def _json_payload():
    return request.get_json(silent=True) or {}


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = _json_payload()
        email = data.get("email", "").strip().lower()
        salt = data.get("salt", "").strip().lower()
        verifier = data.get("verifier", "").strip().lower()

        result = register_user(email, salt, verifier)
        status_code = result.pop("code", 200)
        return jsonify(result), status_code
    except Exception as error:
        print(f"Register error: {error}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@auth_bp.route("/register/check", methods=["POST"])
def register_check():
    try:
        data = _json_payload()
        email = data.get("email", "").strip().lower()

        result = is_email_registered(email)
        status_code = result.pop("code", 200)
        return jsonify(result), status_code
    except Exception as error:
        print(f"Register check error: {error}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@auth_bp.route("/login/start", methods=["POST"])
def login_start():
    try:
        data = _json_payload()
        email = data.get("email", "").strip().lower()
        client_public = data.get("A", "")

        result = start_login(email, client_public)
        status_code = result.pop("code", 200)
        return jsonify(result), status_code
    except Exception as error:
        print(f"Login start error: {error}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@auth_bp.route("/login/verify", methods=["POST"])
def login_verify():
    try:
        data = _json_payload()
        email = data.get("email", "").strip().lower()
        client_proof = data.get("M1", "").strip().lower()

        result = verify_login(email, client_proof)
        status_code = result.pop("code", 200)
        return jsonify(result), status_code
    except Exception as error:
        print(f"Login verify error: {error}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500
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
