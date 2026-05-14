import hmac
import re
import sqlite3
import time

from config import DB_PATH
from utils.auth_data_cipher import decrypt_auth_value, encrypt_auth_value
from utils.crypto_utils import (
    SRP_N,
    compute_client_proof,
    compute_multiplier_k,
    compute_scrambling_parameter,
    compute_server_proof,
    compute_server_public_ephemeral,
    compute_server_shared_secret,
    derive_session_key,
    hex_to_int,
    int_to_hex,
    random_bigint,
)


LOGIN_SESSION_TTL_SECONDS = 300
login_sessions = {}
EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
HEX_PATTERN = re.compile(r"^[0-9a-fA-F]+$")


def _normalize_email(value):
    return str(value or "").strip().lower()


def _is_valid_email(email):
    return bool(EMAIL_PATTERN.fullmatch(str(email or "")))


def _is_valid_hex(value, min_length=1):
    text = str(value or "").strip()
    return len(text) >= int(min_length) and bool(HEX_PATTERN.fullmatch(text))


def _cleanup_expired_sessions():
    cutoff = time.time() - LOGIN_SESSION_TTL_SECONDS
    expired_emails = [
        email for email, session in login_sessions.items() if session["created_at"] < cutoff
    ]
    for email in expired_emails:
        login_sessions.pop(email, None)


def is_email_registered(email):
    email = _normalize_email(email)
    if not email:
        return {"status": "error", "message": "Email is required", "code": 400}

    if not _is_valid_email(email):
        return {"status": "error", "message": "Invalid email format", "code": 400}

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE email = ? LIMIT 1", (email.lower(),))
        existing_user = cursor.fetchone()

        return {
            "status": "success",
            "registered": bool(existing_user),
        }
    except Exception as error:
        print(f"Email check error: {error}")
        raise
    finally:
        if conn:
            conn.close()


def register_user(email, salt, verifier):
    email = _normalize_email(email)
    salt = str(salt or "").strip().lower()
    verifier = str(verifier or "").strip().lower()

    if not email or not salt or not verifier:
        return {"status": "error", "message": "Email, salt, and verifier are required", "code": 400}

    if not _is_valid_email(email):
        return {"status": "error", "message": "Invalid email format", "code": 400}

    if not _is_valid_hex(salt, min_length=16):
        return {"status": "error", "message": "Invalid registration salt", "code": 400}

    if not _is_valid_hex(verifier, min_length=64):
        return {"status": "error", "message": "Invalid registration verifier", "code": 400}

    encrypted_salt = encrypt_auth_value(salt)
    encrypted_verifier = encrypt_auth_value(verifier)

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, salt, verifier) VALUES (?, ?, ?, ?)",
            (email, email, encrypted_salt, encrypted_verifier),
        )
        conn.commit()
        return {"status": "success", "message": "User registered with password verifier"}
    except sqlite3.IntegrityError:
        return {"status": "error", "message": "Email already registered", "code": 409}
    except Exception as error:
        print(f"Database error: {error}")
        raise
    finally:
        if conn:
            conn.close()


def start_login(email, client_public_hex):
    email = _normalize_email(email)
    if not email or not client_public_hex:
        return {"status": "error", "message": "Email and client public value are required", "code": 400}

    if not _is_valid_email(email):
        return {"status": "error", "message": "Invalid email format", "code": 400}

    _cleanup_expired_sessions()

    try:
        client_public = hex_to_int(client_public_hex)
    except ValueError:
        return {"status": "error", "message": "Invalid client public value", "code": 400}

    if client_public % SRP_N == 0:
        return {"status": "error", "message": "Invalid client public value", "code": 400}

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT salt, verifier FROM users WHERE email = ? AND verifier IS NOT NULL",
            (email,),
        )
        user = cursor.fetchone()
        if not user:
            return {"status": "error", "message": "User not found", "code": 404}

        stored_salt, stored_verifier = user
        salt = decrypt_auth_value(stored_salt).lower()
        verifier_hex = decrypt_auth_value(stored_verifier).lower()

        if not _is_valid_hex(salt, min_length=16) or not _is_valid_hex(verifier_hex, min_length=64):
            return {"status": "error", "message": "Stored credentials are invalid", "code": 500}

        verifier = hex_to_int(verifier_hex)
        secret_b = random_bigint()
        server_public = compute_server_public_ephemeral(verifier, secret_b)
        scrambling = compute_scrambling_parameter(client_public, server_public)

        login_sessions[email] = {
            "client_public": client_public,
            "server_public": server_public,
            "secret_b": secret_b,
            "scrambling": scrambling,
            "verifier": verifier,
            "created_at": time.time(),
        }

        return {
            "status": "success",
            "salt": salt.lower(),
            "B": int_to_hex(server_public),
            "k": int_to_hex(compute_multiplier_k()),
        }
    except Exception as error:
        print(f"Login start error: {error}")
        raise
    finally:
        if conn:
            conn.close()


def verify_login(email, client_proof):
    email = _normalize_email(email)
    client_proof = str(client_proof or "").strip().lower()

    if not email or not client_proof:
        return {"status": "error", "message": "Email and proof are required", "code": 400}

    if not _is_valid_email(email):
        return {"status": "error", "message": "Invalid email format", "code": 400}

    if not _is_valid_hex(client_proof, min_length=64):
        return {"status": "error", "message": "Invalid client proof format", "code": 400}

    _cleanup_expired_sessions()
    session = login_sessions.pop(email, None)
    if not session:
        return {"status": "error", "message": "Login session expired. Start login again.", "code": 400}

    shared_secret = compute_server_shared_secret(
        session["client_public"],
        session["verifier"],
        session["secret_b"],
        session["scrambling"],
    )
    session_key = derive_session_key(shared_secret)
    expected_proof = compute_client_proof(
        session["client_public"],
        session["server_public"],
        session_key,
    )

    if not hmac.compare_digest(client_proof.lower(), expected_proof):
        return {"status": "error", "message": "Invalid proof", "code": 401}

    return {
        "status": "success",
        "message": "Login successful",
        "M2": compute_server_proof(session["client_public"], expected_proof, session_key),
    }