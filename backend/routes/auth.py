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
        return jsonify({"error": "Email, mot de passe ou nom manquant"}), 400

    auth_users = load_users()
    if any(u.email == email for u in auth_users):
        return jsonify({"error": "Cet email est déjà utilisé"}), 409
    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

    new_auth_user = AuthUser(email=email, password_hash=hashed_pw, name=name)
    auth_users.append(new_auth_user)
    save_users(users=auth_users)

    return (
        jsonify(
            {"message": "Utilisateur créé avec succès", "id": new_auth_user.id}
        ),
        201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email ou mot de passe manquant"}), 400

    auth_users = load_users()

    auth_user = next((u for u in auth_users if u.email == email), None)

    if auth_user and bcrypt.check_password_hash(
        auth_user.password_hash, password
    ):
        access_token = create_access_token(identity=auth_user.email)

        return (
            jsonify(
                {
                    "access_token": access_token,
                    "auth_user": {
                        "id": auth_user.id,
                        "name": auth_user.name,
                        "email": auth_user.email,
                    },
                }
            ),
            200,
        )

    return jsonify({"error": "Identifiants non valides"}), 401
