from flask import Blueprint, request, jsonify
import sqlite3

voting_bp = Blueprint('voting', __name__)
DB_PATH = "database/zkp_auth.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@voting_bp.route('/vote', methods=['POST'])
def cast_vote():
    data = request.json
    voter_id = data.get('voter_id')
    choice = data.get('choice')

    conn = get_db_connection()
    conn.execute('INSERT INTO votes (voter_id, choice) VALUES (?, ?)', (voter_id, choice))
    conn.commit()
    conn.close()

    return jsonify({"message": "Vote cast successfully"}), 201

@voting_bp.route('/results', methods=['GET'])
def get_results():
    conn = get_db_connection()
    rows = conn.execute('SELECT choice, COUNT(*) as count FROM votes GROUP BY choice').fetchall()
    conn.close()
    
    results = [dict(row) for row in rows]
    return jsonify(results), 200
