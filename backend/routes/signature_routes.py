from flask import Blueprint, request, jsonify
from services.signature_service import create_signature, validate_signature
from utils.crypto_utils import deserialize_private_key, deserialize_public_key

signature_bp = Blueprint("signatures", __name__)

@signature_bp.route("/sign", methods=["POST"])
def sign():
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400

    data = request.get_json()
    message = data.get("message")
    private_key_pem = data.get("private_key")

    if not message or not isinstance(message, str):
        return jsonify({"error": "Field 'message' is required and must be a string"}), 400
    if not private_key_pem or not isinstance(private_key_pem, str):
        return jsonify({"error": "Field 'private_key' is required and must be a string"}), 400

    try:
        private_key = deserialize_private_key(private_key_pem)
        signature = create_signature(private_key, message)
        return jsonify({"signature": signature.hex()}), 201
    except Exception as e:
        return jsonify({"error": "Failed to sign message", "details": str(e)}), 500

@signature_bp.route("/verify", methods=["POST"])
def verify():
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400

    data = request.get_json()
    message = data.get("message")
    signature_hex = data.get("signature")
    public_key_pem = data.get("public_key")

    if not message or not isinstance(message, str):
        return jsonify({"error": "Field 'message' is required and must be a string"}), 400
    if not signature_hex or not isinstance(signature_hex, str):
        return jsonify({"error": "Field 'signature' is required and must be a string"}), 400
    if not public_key_pem or not isinstance(public_key_pem, str):
        return jsonify({"error": "Field 'public_key' is required and must be a string"}), 400

    try:
        signature = bytes.fromhex(signature_hex)
        public_key = deserialize_public_key(public_key_pem)
        valid = validate_signature(public_key, message, signature)
        return jsonify({"valid": valid}), 200
    except ValueError:
        return jsonify({"error": "Signature must be valid hex"}), 400
    except Exception as e:
        return jsonify({"error": "Failed to verify signature", "details": str(e)}), 500