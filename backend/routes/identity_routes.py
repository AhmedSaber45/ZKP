from flask import Blueprint, request, jsonify
import sqlite3

identity_bp = Blueprint('identity', __name__)
DB_PATH = "database/zkp_auth.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@identity_bp.route('/register', methods=['POST'])
def register_identity():
    data = request.json
    user_id = data.get('user_id')
    proof = data.get('proof')

    conn = get_db_connection()
    conn.execute('INSERT INTO identities (user_id, identity_proof) VALUES (?, ?)', (user_id, proof))
    conn.commit()
    conn.close()

    return jsonify({"message": "Identity registered successfully"}), 201

@identity_bp.route('/verify', methods=['POST'])
def verify_identity():
    # Simple verification for demo purposes
    data = request.json
    user_id = data.get('user_id')
    proof = data.get('proof')

    conn = get_db_connection()
    record = conn.execute('SELECT * FROM identities WHERE user_id = ? AND identity_proof = ?', (user_id, proof)).fetchone()
    conn.close()

    if record:
        return jsonify({"verified": True}), 200
    else:
        return jsonify({"verified": False}), 404

@identity_bp.route('/register_digital', methods=['POST'])
def register_digital():
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400

    data = request.get_json()

    identity = data.get("identity")
    if not identity or not isinstance(identity, str):
        return jsonify({"error": "Field 'identity' is required and must be a string"}), 400

    try:
        from services.identity_service import register_identity
        result = register_identity(identity)

        conn = get_db_connection()
        conn.execute('''CREATE TABLE IF NOT EXISTS digital_identities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            identity_hash TEXT,
            public_key TEXT
        )''')
        
        conn.execute(
            "INSERT INTO digital_identities (user_id, identity_hash, public_key) VALUES (?, ?, ?)",
            (identity, result["identity_hash"], result["public_key"])
        )

        conn.commit()
        conn.close()

        return jsonify(result), 201

    except Exception as e:
        return jsonify({"error": "Failed to register identity", "details": str(e)}), 500
