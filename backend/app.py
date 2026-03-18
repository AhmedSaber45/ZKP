from flask import Flask, jsonify
from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from config import DB_PATH, SECRET_KEY
from routes.auth_routes import auth_bp

app = Flask(__name__)
# session security cookies
app.secret_key = SECRET_KEY

# Enable CORS with proper configuration for development
#Allows frontend to call backend.
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

# Import routes
from routes.auth_routes import auth_bp
from routes.blockchain_routes import blockchain_bp
from routes.voting_routes import voting_bp
from routes.identity_routes import identity_bp

app = Flask(__name__)
CORS(app) # Enable CORS for frontend linking
app.secret_key = "ZKP_SECRET_DEMO_KEY"

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(blockchain_bp, url_prefix='/api/blockchain')
app.register_blueprint(voting_bp, url_prefix='/api/voting')
app.register_blueprint(identity_bp, url_prefix='/api/identity')

@app.route('/')
def home():
    return jsonify({"message": "ZKP Backend API Running", "status": "Secure"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)