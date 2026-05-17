# tests/test_signature.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from services.identity_service import register_identity
from services.signature_service import create_signature, validate_signature


# ── Helper ─────────────────────────────────────────────────

from utils.crypto_utils import deserialize_private_key, deserialize_public_key

def _get_keypair():
    result = register_identity("test@test.com")
    private_key = deserialize_private_key(result["private_key"])
    public_key = deserialize_public_key(result["public_key"])
    return private_key, public_key
# ── BLOCK 1: Signature Creation ────────────────────────────

def test_signature_is_string():
    private_key, _ = _get_keypair()
    sig = create_signature(private_key, "hello world")
    assert isinstance(sig, bytes)

def test_signature_not_empty():
    private_key, _ = _get_keypair()
    sig = create_signature(private_key, "hello world")
    assert len(sig) > 0

def test_different_messages_different_signatures():
    private_key, _ = _get_keypair()
    sig1 = create_signature(private_key, "message one")
    sig2 = create_signature(private_key, "message two")
    assert sig1 != sig2


# ── BLOCK 2: Signature Verification ────────────────────────

def test_valid_signature_verifies():
    private_key, public_key = _get_keypair()
    message = "ahmed transfer 100"
    sig = create_signature(private_key, message)
    result = validate_signature(public_key, message, sig)
    assert result is True

def test_tampered_message_fails():
    private_key, public_key = _get_keypair()
    sig = create_signature(private_key, "original message")
    result = validate_signature(public_key, "tampered message", sig)
    assert result is False

def test_wrong_public_key_fails():
    private_key, _ = _get_keypair()
    _, wrong_public_key = _get_keypair()  # different key pair
    sig = create_signature(private_key, "hello world")
    result = validate_signature(wrong_public_key, "hello world", sig)
    assert result is False

def test_empty_message_signs_and_verifies():
    private_key, public_key = _get_keypair()
    sig = create_signature(private_key, "")
    result = validate_signature(public_key, "", sig)
    assert result is True

def test_single_bit_mutation_fails():
    # Core ZKP property from your report
    private_key, public_key = _get_keypair()
    message = "exact original message"
    sig = create_signature(private_key, message)
    mutated = message[:-1] + ("X" if message[-1] != "X" else "Y")
    result = validate_signature(public_key, mutated, sig)
    assert result is False