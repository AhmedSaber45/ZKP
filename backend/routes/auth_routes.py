from flask import Blueprint, jsonify, request, session

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
        if result.get("status") == "success":
            session["user_email"] = email
        status_code = result.pop("code", 200)
        return jsonify(result), status_code
    except Exception as error:
        print(f"Login verify error: {error}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@auth_bp.route("/me", methods=["GET"])
def me():
    email = str(session.get("user_email", "")).strip().lower()
    if not email:
        return jsonify({"status": "error", "message": "Not authenticated"}), 401
    return jsonify({"status": "success", "email": email})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("user_email", None)
    return jsonify({"status": "success", "message": "Logged out"})