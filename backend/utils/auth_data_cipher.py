import base64
import hashlib
import json
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config import AUTH_DATA_AES_KEY, SECRET_KEY

_AAD = b"zkp:auth:field:v1"


def _b64_encode(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _b64_decode(value: str, field_name: str) -> bytes:
    try:
        return base64.b64decode(str(value).strip(), validate=True)
    except Exception as exc:
        raise ValueError(f"Invalid encrypted auth field: {field_name}") from exc


def _load_key() -> bytes:
    raw = str(AUTH_DATA_AES_KEY or "").strip()
    if raw:
        try:
            key = base64.b64decode(raw, validate=True)
        except Exception as exc:
            raise ValueError("AUTH_DATA_AES_KEY must be valid base64 for 32 bytes") from exc

        if len(key) != 32:
            raise ValueError("AUTH_DATA_AES_KEY must decode to exactly 32 bytes")
        return key

    # Dev fallback only.
    return hashlib.sha256(str(SECRET_KEY).encode("utf-8")).digest()


def encrypt_auth_value(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""

    nonce = os.urandom(12)
    ciphertext = AESGCM(_load_key()).encrypt(nonce, text.encode("utf-8"), _AAD)

    payload = {
        "v": 1,
        "alg": "AES-256-GCM",
        "nonce": _b64_encode(nonce),
        "ciphertext": _b64_encode(ciphertext),
    }
    return "encauth:" + json.dumps(payload, separators=(",", ":"))


def decrypt_auth_value(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""

    if not text.startswith("encauth:"):
        return text

    try:
        payload = json.loads(text[len("encauth:"):])
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid encrypted auth payload") from exc

    if payload.get("v") != 1 or payload.get("alg") != "AES-256-GCM":
        raise ValueError("Unsupported encrypted auth payload version")

    nonce = _b64_decode(payload.get("nonce", ""), "nonce")
    ciphertext = _b64_decode(payload.get("ciphertext", ""), "ciphertext")

    if len(nonce) != 12:
        raise ValueError("Invalid nonce length in encrypted auth payload")

    plaintext = AESGCM(_load_key()).decrypt(nonce, ciphertext, _AAD)
    return plaintext.decode("utf-8")
