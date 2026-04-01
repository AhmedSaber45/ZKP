from flask import Flask, jsonify
from flask_cors import CORS
import sys
import os
import logging
logging.basicConfig(level=logging.DEBUG)
from werkzeug.exceptions import HTTPException

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from config import SECRET_KEY
from routes.auth_routes import auth_bp
from routes.blockchain_routes import blockchain_bp
from routes.voting_routes import voting_bp
from routes.identity_routes import identity_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY

CORS(app, resources={r"/api/*": {"origins": "*"}})

# Add error handler to ensure CORS headers are sent on errors
#@app.errorhandler(Exception)
#def handle_error(error):
 #   print(f"Error occurred: {error}")
  #  return jsonify({"status": "error", "message": str(error)}), 500
@app.errorhandler(HTTPException)
def handle_http_error(error):
    return jsonify({
        "status": "error",
        "code": error.code,
        "message": error.description
    }), error.code

@app.route('/')
def home():
    print("🔥 REQUEST RECEIVED")
    return jsonify({"message": "ZKP Backend API Running", "status": "Secure"})

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(blockchain_bp, url_prefix='/api/blockchain')
app.register_blueprint(voting_bp, url_prefix='/api/voting')
app.register_blueprint(identity_bp, url_prefix='/api/identity')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)