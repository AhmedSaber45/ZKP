from utils.crypto_utils import (
    hash_identity,
    generate_key_pair,
    serialize_private_key,
    serialize_public_key
)


def register_identity(identity):

    identity_hash = hash_identity(identity)

    private_key, public_key = generate_key_pair()

    return {

        "identity_hash": identity_hash,

        "private_key": serialize_private_key(private_key),

        "public_key": serialize_public_key(public_key)
    }