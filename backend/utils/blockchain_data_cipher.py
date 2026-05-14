import base64
import hashlib
import json
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config import BLOCKCHAIN_DATA_AES_KEY, SECRET_KEY

_AAD = b"zkp:blockchain:data:v1"


def _b64_encode(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _b64_decode(value: str, field_name: str) -> bytes:
    try:
        return base64.b64decode(str(value).strip(), validate=True)
    except Exception as exc:
        raise ValueError(f"Invalid encrypted payload field: {field_name}") from exc


def _load_aes_key() -> bytes:
    raw = str(BLOCKCHAIN_DATA_AES_KEY or "").strip()

    if raw:
        try:
            key = base64.b64decode(raw, validate=True)
        except Exception as exc:
            raise ValueError(
                "BLOCKCHAIN_DATA_AES_KEY must be a valid base64-encoded 32-byte key"
            ) from exc

        if len(key) != 32:
            raise ValueError("BLOCKCHAIN_DATA_AES_KEY must decode to exactly 32 bytes")
        return key

    # Backward-compatible fallback for local/dev use.
    return hashlib.sha256(str(SECRET_KEY).encode("utf-8")).digest()


def encrypt_transaction_data(plaintext: str) -> str:
    value = str(plaintext or "")
    if value == "":
        return ""

    key = _load_aes_key()
    nonce = os.urandom(12)
    ciphertext_and_tag = AESGCM(key).encrypt(nonce, value.encode("utf-8"), _AAD)

    payload = {
        "v": 1,
        "alg": "AES-256-GCM",
        "nonce": _b64_encode(nonce),
        "ciphertext": _b64_encode(ciphertext_and_tag),
    }
    return "enc:" + json.dumps(payload, separators=(",", ":"))


def decrypt_transaction_data(value: str) -> str:
    data = str(value or "")
    if data == "":
        return ""

    if not data.startswith("enc:"):
        return data

    try:
        payload = json.loads(data[4:])
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid encrypted payload format") from exc

    if payload.get("v") != 1 or payload.get("alg") != "AES-256-GCM":
        raise ValueError("Unsupported encrypted payload version")

    nonce = _b64_decode(payload.get("nonce", ""), "nonce")
    ciphertext_and_tag = _b64_decode(payload.get("ciphertext", ""), "ciphertext")

    if len(nonce) != 12:
        raise ValueError("Invalid AES-GCM nonce length")

    key = _load_aes_key()
    plaintext_bytes = AESGCM(key).decrypt(nonce, ciphertext_and_tag, _AAD)
    return plaintext_bytes.decode("utf-8")
