from flask import Flask, jsonify, request
from config import DB_PATH, SECRET_KEY
import sqlite3
import os

app = Flask(__name__)
app.secret_key = SECRET_KEY

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Home / Test route
@app.route('/')
def home():
    return jsonify({"message": "Backend Running"})

# Example route template
@app.route('/example', methods=['GET'])
def example():
    return jsonify({"message": "Example route"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)