from flask import Blueprint, request,jsonify
from ..extensions import db
from ..models import Category,Product

category_bp = Blueprint("category",__name__)

@category_bp.route("/categories",methods=["POST"])
def create_category():
    data = request.get_json()
    name = data.get("name")

    if not name:
        return {"error": "Category name is required"},400

    existing_category = Category.query.filter_by(name=name).first()

    if existing_category:
        return {"error":"Category Name is already existed"},409

    category = Category(
    name=name
    )

    db.session.add(category)
    db.session.commit()

    return {
    "message": "Category created successfully"
    }, 201


@category_bp.route("/categories", methods=["GET"])
def get_categories():

    categories = Category.query.all()

    result = []

    for category in categories:
        result.append({
                "id" : category.id,
                "name" : category.name,
                "created_at" : category.created_at
        })

    return jsonify(result),200

@category_bp.route("/categories/<int:id>", methods=["GET"])
def get_categories_id(id):

    categories_at_id = Category.query.filter_by(id=id).first()

    if not categories_at_id:
        return {"error": "Category not found"}, 404
    
    result = [
        {    "id" : categories_at_id.id,
            "name" : categories_at_id.name,
            "created_at" : categories_at_id.created_at
        }
    ]

    return jsonify(result),200

@category_bp.route("/categories/<int:id>", methods=["PUT"])
def update_categories(id):

    data = request.get_json(silent=True)

    if not data:
        return {"error": "Request body is required"}, 400

    name = data.get("name")

    if not name:
        return {"error": "Name is required to update a category"}, 400

    categories_at_id = Category.query.filter_by(id=id).first()

    if not categories_at_id:
        return {"error" : "No record found matching with id"},404

    existing_category = Category.query.filter(
    Category.name == name,
    Category.id != id
    ).first()

    if existing_category:
        return {"error" : "Category is already existed with the same name "},409

    categories_at_id.name = name

    db.session.commit()

    return {
        "message": "Category updated successfully"
    }, 200

@category_bp.route("/categories/<int:id>",methods=["DELETE"])

def delete_category(id):

    category = Category.query.filter_by(id=id).first()

    if not category:
        return {"error" : "Category not found "},404

    product = Product.query.filter_by(category_id=id).first()

    if product:
        return {"error": "Product is linked with this category id"},409

    db.session.delete(category)
    db.session.commit()

    return {"message": "Category deleted successfully"}, 200
