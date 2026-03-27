import hashlib


SECRET_KEY = "zkp_project_secret"


def sign_message(message):

    combined = message + SECRET_KEY

    signature = hashlib.sha256(
        combined.encode()
    ).hexdigest()

    return signature


def verify_signature(message, signature):

    expected_signature = sign_message(message)

    return expected_signature == signature