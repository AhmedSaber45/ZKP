# tests/test_blockchain.py
import sys
import os
import hashlib
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from services.blockchain_service import Blockchain, DIFFICULTY_PREFIX, MINING_REWARD

bc = Blockchain()

# ── Helper ─────────────────────────────────────────────────

def _addr(seed: str) -> str:
    return "0x" + hashlib.sha256(seed.encode()).hexdigest()[:40]

def _make_wallet(email, seed):
    try:
        return bc.create_wallet_for_user(email, _addr(seed))
    except ValueError as e:
        if "already" in str(e).lower():
            return bc.get_wallet_for_user(email)
        raise  # ← shows real error instead of hiding it
# ── BLOCK 1: Genesis Block ─────────────────────────────────

def test_chain_not_empty():
    chain = bc.get_all_chain()
    assert len(chain) >= 1

def test_genesis_block_index():
    chain = bc.get_all_chain()
    assert chain[0]["index"] == 0

def test_genesis_block_previous_hash():
    chain = bc.get_all_chain()
    assert chain[0]["previous_hash"] == "0"

def test_genesis_block_has_hash():
    chain = bc.get_all_chain()
    assert len(chain[0]["hash"]) == 64


# ── BLOCK 2: Hash Calculation ──────────────────────────────

def test_hash_is_64_chars():
    block = bc.get_last_block()
    h = bc.calculate_hash(block)
    assert len(h) == 64

def test_hash_is_deterministic():
    block = bc.get_last_block()
    assert bc.calculate_hash(block) == bc.calculate_hash(block)

def test_hash_changes_with_nonce():
    block = bc.get_last_block()
    h1 = bc.calculate_hash(block)
    block["nonce"] += 1
    h2 = bc.calculate_hash(block)
    assert h1 != h2


# ── BLOCK 3: Chain Validity ────────────────────────────────

def test_chain_is_valid():
    assert bc.is_chain_valid() is True

def test_last_block_hash_matches():
    block = bc.get_last_block()
    assert bc.calculate_hash(block) == block["hash"]


# ── BLOCK 4: Wallet Creation ───────────────────────────────

def test_create_wallet_returns_keys():
    wallet = _make_wallet("wallet_test@test.com", "seed1")  # ← inside function
    assert "wallet_address" in wallet
    assert "private_key_b64" in wallet
    assert "public_key_b64" in wallet

def test_wallet_default_balance():
    wallet = _make_wallet("balance_test@test.com", "seed2")  # ← inside function
    assert float(wallet["balance"]) == 1000.0

def test_duplicate_wallet_raises():
    _make_wallet("dup_test@test.com", "seed3")  # ← inside function
    with pytest.raises(ValueError):
        bc.create_wallet_for_user("dup_test@test.com", _addr("seed99"))

def test_negative_balance_raises():
    with pytest.raises(ValueError):
        bc.create_wallet_for_user(
            "neg_test@test.com",
            _addr("seed4"),
            initial_balance=-100
        )

def test_invalid_wallet_address_raises():
    with pytest.raises(ValueError):
        bc.create_wallet_for_user("bad@test.com", "notavalidaddress")


# ── BLOCK 5: Transactions ──────────────────────────────────

def test_zero_amount_raises():
    _make_wallet("sender_zero@test.com", "seed5")  # ← inside function
    with pytest.raises(ValueError, match="greater than zero"):
        bc.create_signed_transaction("sender_zero@test.com", _addr("seed6"), 0)

def test_negative_amount_raises():
    _make_wallet("sender_neg@test.com", "seed6")  # ← inside function
    with pytest.raises(ValueError, match="greater than zero"):
        bc.create_signed_transaction("sender_neg@test.com", _addr("seed5"), -50)

def test_send_to_self_raises():
    _make_wallet("self_send@test.com", "seed7")  # ← inside function
    with pytest.raises(ValueError, match="different from sender"):
        bc.create_signed_transaction("self_send@test.com", _addr("seed7"), 10)

def test_insufficient_balance_raises():
    _make_wallet("broke@test.com", "seed8")   # ← inside function
    _make_wallet("rich@test.com",  "seed9")   # ← inside function
    with pytest.raises(ValueError, match="Insufficient"):
        bc.create_signed_transaction("broke@test.com", _addr("seed9"), 99999999)

def test_valid_transaction_created():
    _make_wallet("alice@test.com", "seed10")  # ← inside function
    _make_wallet("bob@test.com",   "seed11")  # ← inside function
    tx = bc.create_signed_transaction("alice@test.com", _addr("seed11"), 10)
    assert tx["status"] == "pending"
    assert tx["amount"] == 10.0
    assert len(tx["signature"]) > 0


# ── BLOCK 6: Mining & Proof of Work ───────────────────────

def test_mined_block_hash_starts_with_difficulty():
    _make_wallet("miner@test.com", "seed12")  # ← inside function
    _make_wallet("recv@test.com",  "seed13")  # ← inside function
    bc.create_signed_transaction("miner@test.com", _addr("seed13"), 5)
    block = bc.mine_block(miner_wallet=_addr("seed12"))
    assert block["hash"].startswith(DIFFICULTY_PREFIX)

def test_mined_block_index_increments():
    last = bc.get_last_block()
    _make_wallet("miner2@test.com", "seed14")  # ← inside function
    _make_wallet("recv2@test.com",  "seed15")  # ← inside function
    bc.create_signed_transaction