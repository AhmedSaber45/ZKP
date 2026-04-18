from flask import Blueprint, request, jsonify, session
from services.blockchain_service import blockchain
from utils.validators import is_valid_wallet_address
from utils.blockchain_crypto import normalize_wallet_address

blockchain_bp = Blueprint("blockchain", __name__)


def _current_user_email():
    return str(session.get("user_email", "")).strip().lower()


def _require_user_email():
    email = _current_user_email()
    if not email:
        return None, (jsonify({"status": "error", "message": "Authentication required"}), 401)
    return email, None


@blockchain_bp.route("/wallet", methods=["GET"])
def get_wallet():
    user_email, error_response = _require_user_email()
    if error_response:
        return error_response

    wallet = blockchain.get_wallet_for_user(user_email)
    if not wallet:
        return jsonify({"status": "error", "message": "Wallet setup required", "needsSetup": True}), 404

    return jsonify(
        {
            "status": "success",
            "wallet": {
                "address": wallet["wallet_address"],
                "public_key": wallet["public_key_b64"],
                "balance": float(wallet["balance"]),
            },
        }
    )


@blockchain_bp.route("/wallet/setup", methods=["POST"])
def setup_wallet():
    user_email, error_response = _require_user_email()
    if error_response:
        return error_response

    data = request.get_json() or {}
    wallet_address = normalize_wallet_address(data.get("wallet_address", ""))
    initial_balance = data.get("initial_balance", None)

    if not wallet_address:
        return jsonify({"status": "error", "message": "wallet_address is required"}), 400

    try:
        wallet = blockchain.create_wallet_for_user(user_email, wallet_address, initial_balance)
    except ValueError as exc:
        return jsonify({"status": "error", "message": str(exc)}), 400

    return jsonify(
        {
            "status": "success",
            "wallet": {
                "address": wallet["wallet_address"],
                "public_key": wallet["public_key_b64"],
                "balance": float(wallet["balance"]),
            },
        }
    )

# Add Transaction
@blockchain_bp.route("/transaction", methods=["POST"])
def add_transaction():
    user_email, error_response = _require_user_email()
    if error_response:
        return error_response

    data = request.get_json() or {}
    receiver = normalize_wallet_address(data.get("receiver", ""))
    amount_text = str(data.get("amount", "")).strip()
    metadata = str(data.get("data", "")).strip()

    if not receiver or not amount_text:
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    if not is_valid_wallet_address(receiver):
        return jsonify({"status": "error", "message": "Invalid receiver wallet address"}), 400

    try:
        tx = blockchain.create_signed_transaction(
            sender_user_email=user_email,
            receiver_wallet=receiver,
            amount=amount_text,
            data=metadata,
        )
        return jsonify({"status": "success", "transaction": tx})
    except ValueError as exc:
        return jsonify({"status": "error", "message": str(exc)}), 400

# Mine Block
@blockchain_bp.route("/mine", methods=["POST"])
def mine_block():
    user_email, error_response = _require_user_email()
    if error_response:
        return error_response

    data = request.get_json() or {}
    miner_address = normalize_wallet_address(data.get("miner", "")) or None

    if not miner_address:
        wallet = blockchain.get_wallet_for_user(user_email)
        if not wallet:
            return jsonify({"status": "error", "message": "Wallet setup required"}), 400
        miner_address = wallet["wallet_address"]

    if miner_address and not is_valid_wallet_address(miner_address):
        return jsonify({"status": "error", "message": "Invalid miner wallet address"}), 400

    try:
        block = blockchain.mine_block(miner_address)
        return jsonify({"status": "success", "block": block})
    except ValueError as exc:
        return jsonify({"status": "error", "message": str(exc)}), 400

# Get Chain
@blockchain_bp.route("/chain", methods=["GET"])
def get_chain():
    user_email, error_response = _require_user_email()
    if error_response:
        return error_response

    wallet = blockchain.get_wallet_for_user(user_email)
    if not wallet:
        return jsonify({"status": "error", "message": "Wallet setup required", "needsSetup": True}), 404
    wallet_address = wallet["wallet_address"]
    wallet_chain = blockchain.get_wallet_chain_view(wallet_address)
    return jsonify(
        {
            "wallet": wallet_address,
            "length": len(wallet_chain),
            "transactionCount": blockchain.get_wallet_transaction_count(wallet_address),
            "chain": wallet_chain,
        }
    )

# Validate Chain
@blockchain_bp.route("/validate", methods=["GET"])
def validate_chain():
    is_valid = blockchain.is_chain_valid()
    return jsonify({"valid": is_valid})


@blockchain_bp.route("/notifications", methods=["GET"])
def get_notifications():
    user_email, error_response = _require_user_email()
    if error_response:
        return error_response

    wallet = blockchain.get_wallet_for_user(user_email)
    if not wallet:
        return jsonify({"status": "error", "message": "Wallet setup required", "needsSetup": True}), 404
    notifications = blockchain.get_notifications(wallet["wallet_address"])
    return jsonify({"status": "success", "notifications": notifications})