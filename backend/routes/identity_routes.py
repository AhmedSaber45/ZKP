from flask import Blueprint, request, jsonify

from services.identity_service import register_identity
from database import get_connection

identity_routes = Blueprint("identity_routes", __name__)


@identity_routes.route("/identity/register", methods=["POST"])
def register():
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400

    data = request.get_json()

    identity = data.get("identity")
    if not identity or not isinstance(identity, str):
        return jsonify({"error": "Field 'identity' is required and must be a string"}), 400

    try:
        result = register_identity(identity)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO identities (email, identity_hash, public_key) VALUES (?, ?, ?)",
            (identity, result["identity_hash"], result["public_key"])
        )

        conn.commit()
        conn.close()

        return jsonify(result), 201

    except Exception as e:
        return jsonify({"error": "Failed to register identity", "details": str(e)}), 500