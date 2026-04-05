from flask import Blueprint, request, jsonify
import sqlite3

blockchain_bp = Blueprint('blockchain', __name__)
DB_PATH = "database/zkp_auth.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@blockchain_bp.route('/transaction', methods=['POST'])
def add_transaction():
    data = request.json
    sender = data.get('sender')
    receiver = data.get('receiver')
    amount = data.get('amount')

    conn = get_db_connection()
    conn.execute('INSERT INTO transactions (sender, receiver, amount) VALUES (?, ?, ?)', (sender, receiver, amount))
    conn.commit()
    conn.close()

    return jsonify({"message": "Transaction recorded successfully"}), 201

@blockchain_bp.route('/history', methods=['GET'])
def get_history():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM transactions ORDER BY timestamp DESC').fetchall()
    conn.close()
    
    history = [dict(row) for row in rows]
    return jsonify(history), 200
