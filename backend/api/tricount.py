import os
from datetime import timedelta

from flask import Flask, jsonify
from flask_cors import CORS

from backend.extensions import bcrypt, jwt
from backend.routes.auth import auth_bp
from backend.routes.tricounts import tricount_bp

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
if not app.config["JWT_SECRET_KEY"]:
    raise RuntimeError("JWT_SECRET_KEY is not set")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

CORS(app)
jwt.init_app(app)
bcrypt.init_app(app)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(tricount_bp, url_prefix="/api/tricounts")


@app.route("/")
def api_root():
    return jsonify({"status": "ok", "message": "Tricount API running"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
