from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from config import DB_PATH, SECRET_KEY
from routes.auth_routes import auth_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Enable CORS with proper configuration for development
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Add error handler to ensure CORS headers are sent on errors
@app.errorhandler(Exception)
def handle_error(error):
    print(f"Error occurred: {error}")
    return jsonify({"status": "error", "message": str(error)}), 500

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# Home / Test route
@app.route('/')
def home():
    return jsonify({"message": "Backend Running"})


# Register Authentication Routes
app.register_blueprint(auth_bp, url_prefix="/api/auth")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)