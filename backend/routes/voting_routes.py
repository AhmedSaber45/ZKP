from flask import Blueprint, request, jsonify
from services.voting_service import generate_challenge, verify_vote
from config import ADMIN_EMAIL, ADMIN_PASSWORD
import hmac

voting_bp = Blueprint("voting", __name__)

challenge_store = {}
voter_public_keys = {}

@voting_bp.route("/start", methods=["POST"])
def start_vote():
    data = request.json
    voter_hash = data.get("voter_hash")
    commitment = data.get("commitment")
    public_key = data.get("public_key")

    if not voter_hash or commitment is None or public_key is None:
        return jsonify({"status": "error", "message": "Missing data"}), 400

    try:
        commitment = int(commitment)
        public_key = int(public_key)
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Invalid proof"}), 400

    stored_public_key = voter_public_keys.get(voter_hash)
    if stored_public_key is not None and stored_public_key != public_key:
        return jsonify({"status": "error", "message": "Invalid proof"}), 400

    if stored_public_key is None:
        voter_public_keys[voter_hash] = public_key

    challenge = generate_challenge()

    challenge_store[voter_hash] = {
        "commitment": commitment,
        "public_key": public_key,
        "challenge": challenge
    }

    return jsonify({"challenge": challenge})


@voting_bp.route("/submit", methods=["POST"])
def submit_vote():
    data = request.json

    voter_hash = data.get("voter_hash")
    candidate = data.get("candidate")
    response = data.get("response")

    if not voter_hash or not candidate or response is None:
        return jsonify({"status": "error", "message": "Missing data"}), 400

    record = challenge_store.pop(voter_hash, None)

    if not record:
        return jsonify({"status": "error", "message": "No active session"}), 400

    result = verify_vote(voter_hash, record, int(response), candidate)

    return jsonify(result)

@voting_bp.route("/results", methods=["GET"])
def results():
    import sqlite3
    from config import DB_PATH

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT choice, COUNT(*) FROM votes GROUP BY choice")
    rows = cursor.fetchall()

    conn.close()

    data = {row[0]: row[1] for row in rows}

    return jsonify({"status": "success", "data": data})


@voting_bp.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password are required"}), 400

    valid_email = hmac.compare_digest(email, ADMIN_EMAIL)
    valid_password = hmac.compare_digest(password, ADMIN_PASSWORD)

    if not (valid_email and valid_password):
        return jsonify({"status": "error", "message": "Invalid admin credentials"}), 401

    return jsonify({"status": "success", "message": "Admin authenticated"})







    