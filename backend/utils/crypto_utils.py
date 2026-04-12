import hashlib
import secrets


SRP_N_HEX = (
	"EEAF0AB9ADB38DD69C33F80AFA8FC5E860726187752123DAAFCB" 
	"B9E4D7EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C2" 
	"45E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE" 
	"386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007C" 
	"B8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DC" 
	"A3AD961C62F356208552BB9ED529077096966D670C354E4ABC98" 
	"04F1746C08CA237327FFFFFFFFFFFFFFFF"
)
SRP_N = int(SRP_N_HEX, 16)
SRP_G = 2


def int_to_hex(value):
	return format(value, "x")


def hex_to_int(value):
	normalized = str(value).strip().lower()
	if normalized.startswith("0x"):
		normalized = normalized[2:]
	if not normalized:
		raise ValueError("Missing hexadecimal value")
	return int(normalized, 16)


def hash_hex(*parts):
	joined = ":".join(str(part) for part in parts)
	return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def hash_int(*parts):
	return int(hash_hex(*parts), 16)


def random_hex(byte_length=16):
	return secrets.token_hex(byte_length)


def random_bigint(byte_length=32):
	return int(random_hex(byte_length), 16)


def normalize_mod(value):
	return value % SRP_N


def compute_multiplier_k():
	return hash_int(SRP_N_HEX.lower(), int_to_hex(SRP_G))


def compute_private_key(password, salt):
	return hash_int(password, str(salt).lower())


def compute_verifier(private_key):
	return pow(SRP_G, private_key, SRP_N)


def compute_scrambling_parameter(client_public, server_public):
	return hash_int(int_to_hex(client_public), int_to_hex(server_public))


def compute_server_public_ephemeral(verifier, secret_b):
	multiplier = compute_multiplier_k()
	return normalize_mod((multiplier * verifier) + pow(SRP_G, secret_b, SRP_N))


def compute_client_shared_secret(server_public, private_key, secret_a, scrambling):
	verifier_component = pow(SRP_G, private_key, SRP_N)
	base = normalize_mod(server_public - (compute_multiplier_k() * verifier_component))
	exponent = secret_a + (scrambling * private_key)
	return pow(base, exponent, SRP_N)


def compute_server_shared_secret(client_public, verifier, secret_b, scrambling):
	base = normalize_mod(client_public * pow(verifier, scrambling, SRP_N))
	return pow(base, secret_b, SRP_N)


def derive_session_key(shared_secret):
	return hash_hex(int_to_hex(shared_secret))


def compute_client_proof(client_public, server_public, session_key):
	return hash_hex(int_to_hex(client_public), int_to_hex(server_public), session_key)


def compute_server_proof(client_public, client_proof, session_key):
	return hash_hex(int_to_hex(client_public), client_proof, session_key)

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
