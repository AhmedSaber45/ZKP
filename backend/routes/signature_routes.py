from flask import Blueprint, request, jsonify

from services.signature_service import (
    create_signature,
    validate_signature
)

from utils.crypto_utils import (
    deserialize_private_key,
    deserialize_public_key
)

signature_routes = Blueprint("signature_routes", __name__)


@signature_routes.route("/signature/sign", methods=["POST"])
def sign():

    data = request.json

    message = data["message"]

    private_key = deserialize_private_key(
        data["private_key"]
    )

    signature = create_signature(
        private_key,
        message
    )

    return jsonify({
        "signature": signature.hex()
    })


@signature_routes.route("/signature/verify", methods=["POST"])
def verify():

    data = request.json

    message = data["message"]

    signature = bytes.fromhex(
        data["signature"]
    )

    public_key = deserialize_public_key(
        data["public_key"]
    )

    valid = validate_signature(
        public_key,
        message,
        signature
    )

    return jsonify({
        "valid": valid
    })