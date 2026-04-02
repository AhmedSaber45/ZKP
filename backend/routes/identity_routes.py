from flask import Blueprint, request, jsonify

from services.identity_service import register_identity
from database import get_connection

identity_routes = Blueprint("identity_routes", __name__)


@identity_routes.route("/identity/register", methods=["POST"])
def register():

    data = request.json

    identity = data["identity"]

    result = register_identity(identity)

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO identities (email, identity_hash, public_key) VALUES (?, ?, ?)",
        (identity, result["identity_hash"], result["public_key"])
    )

    conn.commit()

    conn.close()

    return jsonify(result)