from flask import Blueprint, request, jsonify
from services.identity_service import generate_identity_proof

identity_bp = Blueprint("identity", __name__)


@identity_bp.route("/generate_proof", methods=["POST"])
def generate_proof():

    data = request.json

    username = data.get("username")

    proof = generate_identity_proof(username)

    return jsonify({
        "proof": proof
    })