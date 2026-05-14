import hashlib
import json
import sqlite3
import threading
import time
import uuid
from datetime import datetime

from config import DB_PATH
from utils.blockchain_crypto import (
    generate_wallet_keypair,
    normalize_wallet_address,
    sign_transaction_payload,
    verify_transaction_signature,
)
from utils.blockchain_data_cipher import decrypt_transaction_data, encrypt_transaction_data
from utils.validators import is_valid_wallet_address

DIFFICULTY_PREFIX = "0000"
MINING_REWARD = 50.0
DEFAULT_USER_BALANCE = 1000.0


class Blockchain:
    def __init__(self):
        self._lock = threading.RLock()
        self._ensure_tables()
        self._ensure_genesis_block()

    def _connect(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_tables(self):
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS blockchain_wallets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email TEXT UNIQUE NOT NULL,
                    wallet_address TEXT UNIQUE NOT NULL,
                    private_key_b64 TEXT NOT NULL,
                    public_key_b64 TEXT NOT NULL,
                    balance REAL NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS blockchain_transactions_secure (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tx_id TEXT UNIQUE NOT NULL,
                    sender TEXT NOT NULL,
                    receiver TEXT NOT NULL,
                    amount REAL NOT NULL,
                    amount_text TEXT NOT NULL,
                    data TEXT,
                    signature TEXT NOT NULL,
                    public_key TEXT NOT NULL,
                    status TEXT NOT NULL,
                    block_index INTEGER,
                    created_at TEXT NOT NULL,
                    confirmed_at TEXT
                );

                CREATE TABLE IF NOT EXISTS blockchain_blocks_secure (
                    index_num INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    transactions_json TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    nonce INTEGER NOT NULL,
                    hash TEXT NOT NULL,
                    miner_wallet TEXT
                );

                CREATE TABLE IF NOT EXISTS blockchain_notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    wallet_address TEXT NOT NULL,
                    tx_id TEXT,
                    event_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    is_read INTEGER NOT NULL DEFAULT 0
                );
                """
            )

    def _ensure_genesis_block(self):
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(1) AS c FROM blockchain_blocks_secure").fetchone()
            if row["c"] > 0:
                return

            genesis = {
                "index": 0,
                "timestamp": self._now_iso(),
                "transactions": [],
                "previous_hash": "0",
                "nonce": 0,
            }
            genesis["hash"] = self.calculate_hash(genesis)

            conn.execute(
                """
                INSERT INTO blockchain_blocks_secure
                (index_num, timestamp, transactions_json, previous_hash, nonce, hash, miner_wallet)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    genesis["index"],
                    genesis["timestamp"],
                    json.dumps(genesis["transactions"], separators=(",", ":")),
                    genesis["previous_hash"],
                    genesis["nonce"],
                    genesis["hash"],
                    None,
                ),
            )

    def _now_iso(self):
        return datetime.utcnow().isoformat() + "Z"

    def calculate_hash(self, block):
        block_copy = {
            "index": block["index"],
            "timestamp": block["timestamp"],
            "transactions": block["transactions"],
            "previous_hash": block["previous_hash"],
            "nonce": block["nonce"],
        }
        encoded = json.dumps(block_copy, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def get_last_block(self):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM blockchain_blocks_secure ORDER BY index_num DESC LIMIT 1"
            ).fetchone()
        return self._row_to_block(row)

    def _row_to_block(self, row):
        if row is None:
            return None
        return {
            "index": row["index_num"],
            "timestamp": row["timestamp"],
            "transactions": json.loads(row["transactions_json"]),
            "previous_hash": row["previous_hash"],
            "nonce": row["nonce"],
            "hash": row["hash"],
            "miner_wallet": row["miner_wallet"],
        }

    def get_wallet_for_user(self, user_email):
        user_email = str(user_email).strip().lower()
        if not user_email:
            raise ValueError("Missing user email")

        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM blockchain_wallets WHERE user_email = ?",
                (user_email,),
            ).fetchone()

        return dict(row) if row else None

    def create_wallet_for_user(self, user_email, wallet_address, initial_balance=None):
        user_email = str(user_email).strip().lower()
        wallet_address = normalize_wallet_address(wallet_address)

        if not user_email:
            raise ValueError("Missing user email")

        if not is_valid_wallet_address(wallet_address):
            raise ValueError("Invalid wallet address format")

        if initial_balance is None:
            balance_value = DEFAULT_USER_BALANCE
        else:
            try:
                balance_value = float(initial_balance)
            except (TypeError, ValueError):
                raise ValueError("Initial balance must be a valid number")

            if balance_value < 0:
                raise ValueError("Initial balance cannot be negative")

        with self._lock, self._connect() as conn:
            existing_for_user = conn.execute(
                "SELECT * FROM blockchain_wallets WHERE user_email = ?",
                (user_email,),
            ).fetchone()
            if existing_for_user:
                raise ValueError("Wallet already set for this user")

            existing_wallet = conn.execute(
                "SELECT 1 FROM blockchain_wallets WHERE wallet_address = ?",
                (wallet_address,),
            ).fetchone()
            if existing_wallet:
                raise ValueError("Wallet address already in use")

            _derived_wallet_address, private_key_b64, public_key_b64 = generate_wallet_keypair()
            created_at = self._now_iso()

            conn.execute(
                """
                INSERT INTO blockchain_wallets
                (user_email, wallet_address, private_key_b64, public_key_b64, balance, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user_email,
                    wallet_address,
                    private_key_b64,
                    public_key_b64,
                    balance_value,
                    created_at,
                ),
            )

            return {
                "user_email": user_email,
                "wallet_address": wallet_address,
                "private_key_b64": private_key_b64,
                "public_key_b64": public_key_b64,
                "balance": balance_value,
                "created_at": created_at,
            }

    def get_wallet_by_address(self, wallet_address):
        wallet_address = normalize_wallet_address(wallet_address)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM blockchain_wallets WHERE wallet_address = ?",
                (wallet_address,),
            ).fetchone()
        return dict(row) if row else None

    def get_wallet_balance(self, wallet_address):
        wallet = self.get_wallet_by_address(wallet_address)
        return float(wallet["balance"]) if wallet else 0.0

    def _insert_notification(self, conn, wallet_address, tx_id, event_type, message):
        conn.execute(
            """
            INSERT INTO blockchain_notifications
            (wallet_address, tx_id, event_type, message, created_at, is_read)
            VALUES (?, ?, ?, ?, ?, 0)
            """,
            (wallet_address, tx_id, event_type, message, self._now_iso()),
        )

    def create_signed_transaction(self, sender_user_email, receiver_wallet, amount, data=""):
        receiver_wallet = normalize_wallet_address(receiver_wallet)
        data_plaintext = str(data or "").strip()
        amount_value = float(amount)

        if amount_value <= 0:
            raise ValueError("Amount must be greater than zero")

        with self._lock, self._connect() as conn:
            sender_wallet = self.get_wallet_for_user(sender_user_email)
            if not sender_wallet:
                raise ValueError("Wallet setup required before creating transactions")
            sender_address = sender_wallet["wallet_address"]

            if receiver_wallet == sender_address:
                raise ValueError("Receiver must be different from sender")

            receiver_exists = conn.execute(
                "SELECT 1 FROM blockchain_wallets WHERE wallet_address = ?",
                (receiver_wallet,),
            ).fetchone()
            if not receiver_exists:
                raise ValueError("Receiver wallet does not exist")

            if float(sender_wallet["balance"]) < amount_value:
                raise ValueError("Insufficient balance")

            amount_text = f"{amount_value:.8f}".rstrip("0").rstrip(".")
            encrypted_data = encrypt_transaction_data(data_plaintext)
            signature = sign_transaction_payload(
                sender_wallet["private_key_b64"],
                sender_address,
                receiver_wallet,
                amount_text,
                encrypted_data,
            )

            ok, error_message, _ = verify_transaction_signature(
                sender_address,
                receiver_wallet,
                amount_text,
                signature,
                sender_wallet["public_key_b64"],
                data=encrypted_data,
            )
            if not ok:
                raise ValueError(error_message or "Invalid transaction signature")

            tx_id = str(uuid.uuid4())
            created_at = self._now_iso()

            conn.execute(
                """
                INSERT INTO blockchain_transactions_secure
                (tx_id, sender, receiver, amount, amount_text, data, signature, public_key,
                 status, block_index, created_at, confirmed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', NULL, ?, NULL)
                """,
                (
                    tx_id,
                    sender_address,
                    receiver_wallet,
                    amount_value,
                    amount_text,
                    encrypted_data,
                    signature,
                    sender_wallet["public_key_b64"],
                    created_at,
                ),
            )

            self._insert_notification(
                conn,
                sender_address,
                tx_id,
                "transaction_created",
                f"Transaction {tx_id} created and waiting for mining.",
            )
            self._insert_notification(
                conn,
                receiver_wallet,
                tx_id,
                "transaction_pending",
                f"Incoming transaction {tx_id} is pending confirmation.",
            )

            return {
                "id": tx_id,
                "sender": sender_address,
                "receiver": receiver_wallet,
                "amount": amount_value,
                "amount_text": amount_text,
                "data": encrypted_data,
                "signature": signature,
                "public_key": sender_wallet["public_key_b64"],
                "status": "pending",
                "timestamp": created_at,
            }

    def _pending_transactions(self, conn):
        rows = conn.execute(
            """
            SELECT *
            FROM blockchain_transactions_secure
            WHERE status = 'pending'
            ORDER BY created_at ASC
            """
        ).fetchall()
        return [dict(row) for row in rows]

    def mine_block(self, miner_wallet=None):
        miner_wallet = normalize_wallet_address(miner_wallet)

        with self._lock, self._connect() as conn:
            if miner_wallet:
                miner_row = conn.execute(
                    "SELECT 1 FROM blockchain_wallets WHERE wallet_address = ?",
                    (miner_wallet,),
                ).fetchone()
                if not miner_row:
                    raise ValueError("Miner wallet does not exist")

            pending = self._pending_transactions(conn)
            if not pending and not miner_wallet:
                raise ValueError("No pending transactions to mine")

            transactions = []
            for tx in pending:
                transactions.append(
                    {
                        "id": tx["tx_id"],
                        "sender": tx["sender"],
                        "receiver": tx["receiver"],
                        "amount": tx["amount"],
                        "amount_text": tx["amount_text"],
                        "data": tx["data"] or "",
                        "signature": tx["signature"],
                        "public_key": tx["public_key"],
                        "timestamp": tx["created_at"],
                    }
                )

            if miner_wallet:
                reward_tx = {
                    "id": str(uuid.uuid4()),
                    "sender": "network",
                    "receiver": miner_wallet,
                    "amount": MINING_REWARD,
                    "amount_text": str(MINING_REWARD),
                    "data": "mining_reward",
                    "signature": "",
                    "public_key": "",
                    "timestamp": self._now_iso(),
                }
                transactions.append(reward_tx)

            last_block = self._row_to_block(
                conn.execute(
                    "SELECT * FROM blockchain_blocks_secure ORDER BY index_num DESC LIMIT 1"
                ).fetchone()
            )

            block = {
                "index": last_block["index"] + 1,
                "timestamp": self._now_iso(),
                "transactions": transactions,
                "previous_hash": last_block["hash"],
                "nonce": 0,
            }

            while True:
                hash_value = self.calculate_hash(block)
                if hash_value.startswith(DIFFICULTY_PREFIX):
                    block["hash"] = hash_value
                    break
                block["nonce"] += 1

            conn.execute(
                """
                INSERT INTO blockchain_blocks_secure
                (index_num, timestamp, transactions_json, previous_hash, nonce, hash, miner_wallet)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    block["index"],
                    block["timestamp"],
                    json.dumps(block["transactions"], separators=(",", ":")),
                    block["previous_hash"],
                    block["nonce"],
                    block["hash"],
                    miner_wallet,
                ),
            )

            confirmed_at = self._now_iso()
            for tx in pending:
                conn.execute(
                    """
                    UPDATE blockchain_transactions_secure
                    SET status = 'confirmed', block_index = ?, confirmed_at = ?
                    WHERE tx_id = ?
                    """,
                    (block["index"], confirmed_at, tx["tx_id"]),
                )

                conn.execute(
                    "UPDATE blockchain_wallets SET balance = balance - ? WHERE wallet_address = ?",
                    (tx["amount"], tx["sender"]),
                )
                conn.execute(
                    "UPDATE blockchain_wallets SET balance = balance + ? WHERE wallet_address = ?",
                    (tx["amount"], tx["receiver"]),
                )

                self._insert_notification(
                    conn,
                    tx["sender"],
                    tx["tx_id"],
                    "transaction_confirmed",
                    f"Transaction {tx['tx_id']} was confirmed in block #{block['index']}.",
                )
                self._insert_notification(
                    conn,
                    tx["receiver"],
                    tx["tx_id"],
                    "transaction_received",
                    f"You received {tx['amount']} in transaction {tx['tx_id']}.",
                )

            if miner_wallet:
                conn.execute(
                    "UPDATE blockchain_wallets SET balance = balance + ? WHERE wallet_address = ?",
                    (MINING_REWARD, miner_wallet),
                )
                self._insert_notification(
                    conn,
                    miner_wallet,
                    None,
                    "mining_reward",
                    f"Mining reward {MINING_REWARD} credited in block #{block['index']}.",
                )

            return block

    def get_wallet_chain(self, wallet_address):
        wallet_address = normalize_wallet_address(wallet_address)
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM blockchain_blocks_secure ORDER BY index_num ASC"
            ).fetchall()

        filtered_chain = []
        for row in rows:
            block = self._row_to_block(row)
            matching_transactions = [
                tx
                for tx in block["transactions"]
                if tx.get("sender") == wallet_address or tx.get("receiver") == wallet_address
            ]
            if matching_transactions:
                block["transactions"] = matching_transactions
                filtered_chain.append(block)
        return filtered_chain

    def get_wallet_chain_view(self, wallet_address):
        wallet_address = normalize_wallet_address(wallet_address)
        chain = self.get_wallet_chain(wallet_address)

        for block in chain:
            for tx in block.get("transactions", []):
                raw_data = tx.get("data", "")
                tx["data_encrypted"] = bool(str(raw_data).startswith("enc:"))
                if not raw_data:
                    tx["data_plaintext"] = ""
                    continue

                try:
                    tx["data_plaintext"] = decrypt_transaction_data(raw_data)
                except Exception:
                    tx["data_plaintext"] = "[encrypted-unavailable]"

        return chain

    def get_wallet_transaction_count(self, wallet_address):
        wallet_address = normalize_wallet_address(wallet_address)
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT COUNT(1) AS c
                FROM blockchain_transactions_secure
                WHERE (sender = ? OR receiver = ?) AND status = 'confirmed'
                """,
                (wallet_address, wallet_address),
            ).fetchone()
        return int(row["c"]) if row else 0

    def get_all_chain(self):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM blockchain_blocks_secure ORDER BY index_num ASC"
            ).fetchall()
        return [self._row_to_block(row) for row in rows]

    def get_notifications(self, wallet_address, limit=50):
        wallet_address = normalize_wallet_address(wallet_address)
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, tx_id, event_type, message, created_at, is_read
                FROM blockchain_notifications
                WHERE wallet_address = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (wallet_address, int(limit)),
            ).fetchall()
        return [dict(row) for row in rows]

    def is_chain_valid(self):
        chain = self.get_all_chain()
        if not chain:
            return False

        for i, current in enumerate(chain):
            if self.calculate_hash(current) != current.get("hash"):
                return False

            if i == 0:
                if current.get("previous_hash") != "0" or current.get("index") != 0:
                    return False
                continue

            previous = chain[i - 1]
            if current.get("previous_hash") != previous.get("hash"):
                return False

            for tx in current.get("transactions", []):
                if tx.get("sender") == "network":
                    continue
                ok, _, _ = verify_transaction_signature(
                    tx.get("sender", ""),
                    tx.get("receiver", ""),
                    tx.get("amount_text", str(tx.get("amount", ""))),
                    tx.get("signature", ""),
                    tx.get("public_key", ""),
                    data=tx.get("data", ""),
                )
                if not ok:
                    return False

        return True


blockchain = Blockchain()