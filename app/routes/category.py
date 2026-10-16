from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models import Category, Product
from .auth import admin_required

category_bp = Blueprint("category", __name__)


@category_bp.route("/categories", methods=["POST"])
@admin_required()
def create_category():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {"error": "Valid JSON request body is required"}, 400

    name = data.get("name")

    if not isinstance(name, str) or not name.strip():
        return {"error": "Category name is required"}, 400

    name = name.strip()

    existing_category = Category.query.filter_by(name=name).first()

    if existing_category:
        return {"error": "Category name already exists"}, 409

    try:
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()

    except Exception:
        db.session.rollback()
        return {"error": "Category creation failed"}, 500

    return {"message": "Category created successfully"}, 201


@category_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.query.order_by(Category.id.asc()).all()

    result = [
        {
            "id": category.id,
            "name": category.name,
            "created_at": (
                category.created_at.isoformat()
                if category.created_at else None
            )
        }
        for category in categories
    ]

    return jsonify(result), 200


@category_bp.route("/categories/<int:id>", methods=["GET"])
def get_category_by_id(id):
    category = db.session.get(Category, id)

    if not category:
        return {"error": "Category not found"}, 404

    result = {
        "id": category.id,
        "name": category.name,
        "created_at": (
            category.created_at.isoformat()
            if category.created_at else None
        )
    }

    return jsonify(result), 200


@category_bp.route("/categories/<int:id>", methods=["PUT"])
@admin_required()
def update_category(id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {"error": "Valid JSON request body is required"}, 400

    name = data.get("name")

    if not isinstance(name, str) or not name.strip():
        return {"error": "Category name is required"}, 400

    name = name.strip()

    category = db.session.get(Category, id)

    if not category:
        return {"error": "Category not found"}, 404

    existing_category = Category.query.filter(
        Category.name == name,
        Category.id != id
    ).first()

    if existing_category:
        return {"error": "Category name already exists"}, 409

    try:
        category.name = name
        db.session.commit()

    except Exception:
        db.session.rollback()
        return {"error": "Category update failed"}, 500

    return {"message": "Category updated successfully"}, 200


@category_bp.route("/categories/<int:id>", methods=["DELETE"])
@admin_required()
def delete_category(id):
    category = db.session.get(Category, id)

    if not category:
        return {"error": "Category not found"}, 404

    product = Product.query.filter_by(category_id=id).first()

    if product:
        return {
            "error": "Cannot delete category because products are linked to it"
        }, 409

    try:
        db.session.delete(category)
        db.session.commit()

    except Exception:
        db.session.rollback()
        return {"error": "Category deletion failed"}, 500

    return {"message": "Category deleted successfully"}, 200
