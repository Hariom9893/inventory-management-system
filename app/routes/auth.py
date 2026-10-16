from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from ..extensions import db
from ..models import User
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from functools import wraps

auth_bp = Blueprint("auth", __name__)

def admin_required():
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = db.session.get(User, int(user_id))

            if not user or user.role != "admin":
                return {"error": "Admin access required"}, 403

            return fn(*args, **kwargs)

        return wrapper
    return decorator

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return {"error": "Request body is required"}, 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return {
            "error": "Name, email and password are required"
        }, 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return {
            "error": "Email already registered"
        }, 409

    password_hash = generate_password_hash(password)

    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
        role="user"
    )

    db.session.add(user)
    db.session.commit()

    return {
        "message": "User registered successfully"
    }, 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return {"error": "Email and password are required"}, 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return {"error": "Invalid email or password"}, 401

    access_token = create_access_token(identity=str(user.id))

    return {
    "access_token": access_token
        }, 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    return {
    "id": user.id,
    "name": user.name,
    "email": user.email,
    "role": user.role
       }, 200