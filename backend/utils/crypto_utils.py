import hashlib

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization


def hash_identity(identity):
    return hashlib.sha256(identity.encode()).hexdigest()


def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    public_key = private_key.public_key()

    return private_key, public_key


def sign_message(private_key, message):

    return private_key.sign(
        message.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )


def verify_signature(public_key, message, signature):

    try:

        public_key.verify(
            signature,
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return True

    except Exception:
        return False


def serialize_private_key(private_key):

    return private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()
    ).decode()


def serialize_public_key(public_key):

    return public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()


def deserialize_private_key(private_key):

    return serialization.load_pem_private_key(
        private_key.encode(),
        password=None
    )


def deserialize_public_key(public_key):

    return serialization.load_pem_public_key(
        public_key.encode()
    )