from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os

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