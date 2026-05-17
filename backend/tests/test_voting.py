# tests/test_voting.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from services.voting_service import (
    generate_challenge,
    hash_voter,
    verify_vote,
)


# ── BLOCK 1: Voter Hashing ─────────────────────────────────

def test_hash_voter_length():
    # SHA-256 always produces 64 hex characters
    result = hash_voter("ahmed@gmail.com")
    assert len(result) == 64

def test_hash_voter_is_hex():
    result = hash_voter("ahmed@gmail.com")
    assert all(c in "0123456789abcdef" for c in result)

def test_hash_voter_deterministic():
    # Same input always gives same hash
    assert hash_voter("ahmed@gmail.com") == hash_voter("ahmed@gmail.com")

def test_hash_voter_different_inputs():
    # Different users must have different hashes
    assert hash_voter("ahmed@gmail.com") != hash_voter("ali@gmail.com")


# ── BLOCK 2: Challenge Generation ─────────────────────────

def test_challenge_in_range():
    for _ in range(50):  # run 50 times to catch randomness issues
        c = generate_challenge()
        assert 1 <= c <= 10

def test_challenge_is_integer():
    assert isinstance(generate_challenge(), int)


# ── BLOCK 3: ZKP Proof Verification ───────────────────────

P = 23
G = 5

def _make_valid_proof():
    """Helper: build a mathematically correct ZKP record."""
    x = 4          # private key (secret)
    r = 3          # random nonce
    y = pow(G, x, P)          # public key = G^x mod P
    t = pow(G, r, P)          # commitment = G^r mod P
    c = 2                      # challenge
    s = (r + c * x) % (P - 1) # response
    return {
        "record": {"commitment": t, "challenge": c, "public_key": y},
        "s": s,
    }

def test_valid_zkp_proof():
    proof = _make_valid_proof()
    voter_hash = "a" * 64  # fake hash, not in DB
    result = verify_vote(voter_hash, proof["record"], proof["s"], "candidate_a")
    # Either success or already voted — both mean proof passed math check
    assert result["status"] in ("success", "error")
    if result["status"] == "error":
        assert result["message"] == "User already voted"

def test_invalid_zkp_proof():
    proof = _make_valid_proof()
    voter_hash = "b" * 64
    result = verify_vote(voter_hash, proof["record"], 0, "candidate_a")
    assert result["status"] == "error"
    assert result["message"] == "Invalid proof"

def test_missing_public_key():
    record = {"commitment": 10, "challenge": 2}  # no public_key
    result = verify_vote("c" * 64, record, 5, "candidate_a")
    assert result["status"] == "error"
    assert result["message"] == "Missing public key"