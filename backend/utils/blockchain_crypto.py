import base64
import hashlib
from typing import Optional, Tuple

from ecdsa import BadSignatureError, NIST256p, SigningKey, VerifyingKey
from ecdsa.util import sigdecode_string, sigencode_string

from utils.validators import is_valid_wallet_address


def normalize_wallet_address(value):
    if value is None:
        return ""
    return str(value).strip().lower()


def derive_wallet_address_from_public_key_der(public_key_der: bytes) -> str:
    digest = hashlib.sha256(public_key_der).hexdigest()
    return f"0x{digest[:40]}"


def decode_base64_bytes(value: str, label: str) -> bytes:
    try:
        return base64.b64decode(str(value).strip(), validate=True)
    except Exception as exc:
        raise ValueError(f"Invalid {label} encoding") from exc


def generate_wallet_keypair() -> Tuple[str, str, str]:
    signing_key = SigningKey.generate(curve=NIST256p)
    verifying_key = signing_key.get_verifying_key()

    private_key_pem = signing_key.to_pem()
    public_key_der = verifying_key.to_der()

    private_key_b64 = base64.b64encode(private_key_pem).decode("utf-8")
    public_key_b64 = base64.b64encode(public_key_der).decode("utf-8")
    wallet_address = derive_wallet_address_from_public_key_der(public_key_der)

    return wallet_address, private_key_b64, public_key_b64


def sign_transaction_payload(
    private_key_b64: str,
    sender: str,
    receiver: str,
    amount_text: str,
    data: str = "",
) -> str:
    private_key_pem = decode_base64_bytes(private_key_b64, "private key")
    signing_key = SigningKey.from_pem(private_key_pem)

    payload = (
        f"{normalize_wallet_address(sender)}|"
        f"{normalize_wallet_address(receiver)}|"
        f"{str(amount_text).strip()}|"
        f"{str(data).strip()}"
    ).encode("utf-8")

    signature = signing_key.sign_deterministic(
        payload,
        hashfunc=hashlib.sha256,
        sigencode=sigencode_string,
    )
    return base64.b64encode(signature).decode("utf-8")


def verify_transaction_signature(
    sender: str,
    receiver: str,
    amount_text: str,
    signature_b64: str,
    public_key_b64: str,
    data: str = "",
    enforce_wallet_binding: bool = False,
) -> Tuple[bool, Optional[str], Optional[str]]:
    sender = normalize_wallet_address(sender)
    receiver = normalize_wallet_address(receiver)
    amount_text = str(amount_text).strip()

    if not sender or not receiver or not amount_text:
        return False, "Missing transaction fields", None

    if not is_valid_wallet_address(sender):
        return False, "Invalid sender wallet address", None

    if not is_valid_wallet_address(receiver):
        return False, "Invalid receiver wallet address", None

    try:
        public_key_der = decode_base64_bytes(public_key_b64, "public key")
        signature_bytes = decode_base64_bytes(signature_b64, "signature")
    except ValueError as exc:
        return False, str(exc), None

    derived_address = derive_wallet_address_from_public_key_der(public_key_der)
    if enforce_wallet_binding and sender != normalize_wallet_address(derived_address):
        return False, "Sender wallet does not match the provided public key", None

    try:
        verifying_key = VerifyingKey.from_der(public_key_der)
        payload = f"{sender}|{receiver}|{amount_text}|{str(data).strip()}".encode("utf-8")
        verifying_key.verify(
            signature_bytes,
            payload,
            hashfunc=hashlib.sha256,
            sigdecode=sigdecode_string,
        )
    except BadSignatureError:
        return False, "Invalid transaction signature", None
    except Exception as exc:
        return False, f"Signature verification failed: {exc}", None

    return True, None, derived_address