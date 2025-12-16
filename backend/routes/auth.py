from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from backend.extensions import bcrypt
from backend.models.auth_user import AuthUser
from backend.utils.auth_storage import load_users, save_users

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not email or not password or not name:
        return jsonify({"error": "Missing email, password, or name"}), 400

    users = load_users()
    if any(u.email == email for u in users):
        return jsonify({"error": "Email already exists"}), 409

    # Hash password
    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

    new_user = AuthUser(email=email, password_hash=hashed_pw, name=name)
    users.append(new_user)
    save_users(users)

    return (
        jsonify({"message": "User created successfully", "id": new_user.id}),
        201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    users = load_users()

    user = next((u for u in users if u.email == email), None)

    if user and bcrypt.check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=user.id)

        return (
            jsonify(
                {
                    "access_token": access_token,
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                    },
                }
            ),
            200,
        )

    return jsonify({"error": "Identifiants non valides"}), 401
