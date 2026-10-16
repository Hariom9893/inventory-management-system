from functools import wraps

from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from ..extensions import db
from ..models import User

auth_bp = Blueprint("auth", __name__)


def admin_required():
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()

            try:
                user_id = int(user_id)
            except (TypeError, ValueError):
                return {"error": "Invalid user identity"}, 401

            user = db.session.get(User, user_id)

            if not user or user.role != "admin":
                return {"error": "Admin access required"}, 403

            return fn(*args, **kwargs)

        return wrapper
    return decorator


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {"error": "Valid JSON request body is required"}, 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([name, email, password]):
        return {
            "error": "Name, email and password are required"
        }, 400

    if not isinstance(name, str) or not name.strip():
        return {"error": "Name must be a non-empty string"}, 400

    if not isinstance(email, str) or not email.strip():
        return {"error": "Email must be a non-empty string"}, 400

    if not isinstance(password, str) or len(password) < 8:
        return {
            "error": "Password must be at least 8 characters long"
        }, 400

    name = name.strip()
    email = email.strip().lower()

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return {"error": "Email already registered"}, 409

    try:
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role="user"
        )

        db.session.add(user)
        db.session.commit()

    except Exception:
        db.session.rollback()
        return {"error": "Registration failed"}, 500

    return {"message": "User registered successfully"}, 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {"error": "Valid JSON request body is required"}, 400

    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not email.strip():
        return {"error": "Email is required"}, 400

    if not isinstance(password, str) or not password:
        return {"error": "Password is required"}, 400

    email = email.strip().lower()
    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return {"error": "Invalid email or password"}, 401

    access_token = create_access_token(identity=str(user.id))

    return {"access_token": access_token}, 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return {"error": "Invalid user identity"}, 401

    user = db.session.get(User, user_id)

    if not user:
        return {"error": "User not found"}, 404

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }, 200
