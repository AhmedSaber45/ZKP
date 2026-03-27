import sqlite3
from config import DB_PATH


def save_identity(username, public_key):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO identities(username, public_key)
        VALUES (?, ?)
        """,
        (username, public_key)
    )

    conn.commit()

    conn.close()