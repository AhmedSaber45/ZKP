from flask import Blueprint, request, jsonify
from services.signature_service import sign_message, verify_signature

signature_bp = Blueprint("signature", __name__)


@signature_bp.route("/sign", methods=["POST"])
def sign():

    data = request.json

    message = data.get("message")

    signature = sign_message(message)

    return jsonify({
        "signature": signature
    })


@signature_bp.route("/verify", methods=["POST"])
def verify():

    data = request.json

    message = data.get("message")
    signature = data.get("signature")

    result = verify_signature(message, signature)

    return jsonify({
        "valid": result
    })