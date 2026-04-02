from flask import Blueprint, request, jsonify
from services.auth_service import login_user, register_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "Invalid JSON"}), 400
        
        username = data.get("username")
        proof = data.get("proof")
        
        if not username or not proof:
            return jsonify({"status": "error", "message": "Username and proof required"}), 400

        result = login_user(username, proof)
        return jsonify(result)
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        print("Incoming request:", request.json)
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Invalid JSON"}), 400

        username = data.get("username")
        secret = data.get("secret")
        
        if not username or not secret:
            return jsonify({"status": "error", "message": "Username and secret required"}), 400

        result = register_user(username, secret)
        return jsonify(result)
    except Exception as e:
        print(f"Register error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500