import hashlib


def generate_identity_proof(username):

    proof = hashlib.sha256(
        username.encode()
    ).hexdigest()

    return proof