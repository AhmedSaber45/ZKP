from flask import Flask


from database import create_table_if_not_exists
from routes.identity_routes import identity_routes
from routes.signature_routes import signature_routes

app = Flask(__name__)


create_table_if_not_exists()

app.register_blueprint(identity_routes)
app.register_blueprint(signature_routes)


@app.route("/")
def home():
    return "Digital Trust Mode Backend Running ✅"


if __name__ == "__main__":
    app.run(debug=True)