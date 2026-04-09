from utils.crypto_utils import sign_message, verify_signature


def create_signature(private_key, message):

    return sign_message(private_key, message)


def validate_signature(public_key, message, signature):

    return verify_signature(public_key, message, signature)