# tests/test_auth.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from services.auth_service import (
    _is_valid_email,
    _is_valid_hex,
    _normalize_email,
    register_user,
)


# ── BLOCK 1: Email Validation ──────────────────────────────

def test_valid_email():
    assert _is_valid_email("ahmed@gmail.com") == True

def test_email_missing_at():
    assert _is_valid_email("ahmedgmail.com") == False

def test_email_missing_domain():
    assert _is_valid_email("ahmed@") == False

def test_email_empty():
    assert _is_valid_email("") == False

def test_email_none():
    assert _is_valid_email(None) == False

def test_email_uppercase_normalized():
    assert _normalize_email("  AHMED@Gmail.COM  ") == "ahmed@gmail.com"


# ── BLOCK 2: Hex Validation ────────────────────────────────

def test_valid_hex():
    assert _is_valid_hex("a1b2c3d4e5f6") == True

def test_hex_too_short():
    assert _is_valid_hex("a1b2", min_length=16) == False

def test_hex_invalid_chars():
    assert _is_valid_hex("zzzzzz") == False

def test_hex_empty():
    assert _is_valid_hex("") == False

def test_hex_none():
    assert _is_valid_hex(None) == False


# ── BLOCK 3: Register Validation (no DB needed) ────────────

def test_register_missing_fields():
    result = register_user("", "", "")
    assert result["status"] == "error"
    assert result["code"] == 400

def test_register_invalid_email():
    result = register_user("notanemail", "a" * 16, "b" * 64)
    assert result["status"] == "error"
    assert result["code"] == 400

def test_register_invalid_salt_too_short():
    result = register_user("test@test.com", "abc", "b" * 64)
    assert result["status"] == "error"
    assert result["code"] == 400

def test_register_invalid_verifier_too_short():
    result = register_user("test@test.com", "a" * 16, "xyz")
    assert result["status"] == "error"
    assert result["code"] == 400

def test_register_invalid_verifier_not_hex():
    result = register_user("test@test.com", "a" * 16, "z" * 64)
    assert result["status"] == "error"
    assert result["code"] == 400