import hmac
import sqlite3
import time

from config import DB_PATH
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


def _cleanup_expired_sessions():
    cutoff = time.time() - LOGIN_SESSION_TTL_SECONDS
    expired_emails = [
        email for email, session in login_sessions.items() if session["created_at"] < cutoff
    ]
    for email in expired_emails:
        login_sessions.pop(email, None)


def is_email_registered(email):
    if not email:
        return {"status": "error", "message": "Email is required", "code": 400}

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
    if not email or not salt or not verifier:
        return {"status": "error", "message": "Email, salt, and verifier are required", "code": 400}

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, salt, verifier) VALUES (?, ?, ?, ?)",
            (email.lower(), email.lower(), salt.lower(), verifier.lower()),
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
    if not email or not client_public_hex:
        return {"status": "error", "message": "Email and client public value are required", "code": 400}

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
            (email.lower(),),
        )
        user = cursor.fetchone()
        if not user:
            return {"status": "error", "message": "User not found", "code": 404}

        salt, verifier_hex = user
        verifier = hex_to_int(verifier_hex)
        secret_b = random_bigint()
        server_public = compute_server_public_ephemeral(verifier, secret_b)
        scrambling = compute_scrambling_parameter(client_public, server_public)

        login_sessions[email.lower()] = {
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
    if not email or not client_proof:
        return {"status": "error", "message": "Email and proof are required", "code": 400}

    _cleanup_expired_sessions()
    session = login_sessions.pop(email.lower(), None)
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