import sqlite3
import hashlib
import random
from config import DB_PATH

P = 23
G = 5


def generate_challenge():
    return random.randint(1, 10)


def hash_voter(user_id):
    return hashlib.sha256(user_id.encode()).hexdigest()


def has_voted(voter_hash):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM votes WHERE voter_id=?", (voter_hash,))
    result = cursor.fetchone()

    conn.close()
    return result is not None


def verify_vote(voter_hash, record, s, candidate):
    t = record["commitment"]
    c = record["challenge"]
    y = record.get("public_key")

    if y is None:
        return {"status": "error", "message": "Missing public key"}

    left = pow(G, s, P)
    right = (t * pow(y, c, P)) % P

    if left != right:
        return {"status": "error", "message": "Invalid proof"}

    if has_voted(voter_hash):
        return {"status": "error", "message": "User already voted"}

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO votes (voter_id, choice) VALUES (?, ?)",
        (voter_hash, candidate)
    )

    conn.commit()
    conn.close()

    return {"status": "success", "message": "Vote recorded successfully"}