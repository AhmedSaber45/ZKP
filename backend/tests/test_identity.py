# tests/test_identity.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from services.identity_service import register_identity


# ── BLOCK 1: Identity Registration Output ─────────────────

def test_register_returns_three_keys():
    result = register_identity("ahmed@gmail.com")
    assert "identity_hash" in result
    assert "private_key" in result
    assert "public_key" in result

def test_identity_hash_length():
    # SHA-256 always 64 hex chars
    result = register_identity("ahmed@gmail.com")
    assert len(result["identity_hash"]) == 64

def test_identity_hash_is_hex():
    result = register_identity("ahmed@gmail.com")
    assert all(c in "0123456789abcdef" for c in result["identity_hash"])

def test_identity_hash_deterministic():
    # Same identity always produces same hash
    r1 = register_identity("ahmed@gmail.com")
    r2 = register_identity("ahmed@gmail.com")
    assert r1["identity_hash"] == r2["identity_hash"]

def test_different_identities_different_hashes():
    r1 = register_identity("ahmed@gmail.com")
    r2 = register_identity("ali@gmail.com")
    assert r1["identity_hash"] != r2["identity_hash"]


# ── BLOCK 2: RSA Key Pair ──────────────────────────────────

def test_private_key_is_string():
    result = register_identity("ahmed@gmail.com")
    assert isinstance(result["private_key"], str)

def test_public_key_is_string():
    result = register_identity("ahmed@gmail.com")
    assert isinstance(result["public_key"], str)

def test_private_key_pem_header():
    result = register_identity("ahmed@gmail.com")
    assert "PRIVATE KEY" in result["private_key"]

def test_public_key_pem_header():
    result = register_identity("ahmed@gmail.com")
    assert "PUBLIC KEY" in result["public_key"]

def test_keys_are_unique_per_identity():
    # Every registration generates a fresh key pair
    r1 = register_identity("ahmed@gmail.com")
    r2 = register_identity("ahmed@gmail.com")
    assert r1["private_key"] != r2["private_key"]
    assert r1["public_key"] != r2["public_key"]