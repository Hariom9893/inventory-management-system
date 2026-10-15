from flask import Blueprint, request, jsonify

from ..extensions import db
from ..models import Product, Category


product_bp = Blueprint("product", __name__)


@product_bp.route("/products", methods=["POST"])
def create_product():

    data = request.get_json(silent=True)

    if not data:
        return {"error": "Request body is required"}, 400

    name = data.get("name")
    sku = data.get("sku")
    description = data.get("description")
    price = data.get("price")
    low_stock_threshold = data.get("low_stock_threshold")
    category_id = data.get("category_id")

    # Required fields
    if not name or not sku or price is None:
        return {
            "error": "Name, SKU and price are required"
        }, 400

    # Price validation
    if not isinstance(price, (int, float)) or isinstance(price, bool):
        return {
            "error": "Price must be a number"
        }, 400

    if price < 0:
        return {
            "error": "Price cannot be negative"
        }, 400

    # SKU uniqueness
    existing_product = Product.query.filter_by(sku=sku).first()

    if existing_product:
        return {
            "error": "Product with this SKU already exists"
        }, 409

    # Low stock threshold validation
    if low_stock_threshold is None:
        low_stock_threshold = 10

    if (
        not isinstance(low_stock_threshold, int)
        or isinstance(low_stock_threshold, bool)
    ):
        return {
            "error": "Low stock threshold must be an integer"
        }, 400

    if low_stock_threshold < 0:
        return {
            "error": "Low stock threshold cannot be negative"
        }, 400

    # Category validation
    if category_id is not None:

        if (
            not isinstance(category_id, int)
            or isinstance(category_id, bool)
        ):
            return {
                "error": "Category ID must be an integer"
            }, 400

        category = db.session.get(Category, category_id)

        if not category:
            return {
                "error": "Category not found"
            }, 404

    # Create product
    product = Product(
        name=name,
        sku=sku,
        description=description,
        price=price,
        current_stock=0,
        low_stock_threshold=low_stock_threshold,
        category_id=category_id
    )

    db.session.add(product)
    db.session.commit()

    return {
        "message": "Product created successfully",
        "product": {
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "description": product.description,
            "price": float(product.price),
            "current_stock": product.current_stock,
            "low_stock_threshold": product.low_stock_threshold,
            "category_id": product.category_id
        }
    }, 201

@product_bp.route("/products",methods=["GET"])
def display_product():
    products = Product.query.all()
    result = []
    for product in products:
        result.append({
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "description": product.description,
        "price": float(product.price),
        "current_stock": product.current_stock,
        "low_stock_threshold": product.low_stock_threshold,
        "category_id": product.category_id
        })

    return jsonify(result), 200

@product_bp.route("/products/<int:id>", methods=["GET"])
def get_product_by_id(id):

    product = Product.query.filter_by(id=id).first()

    if not product:
        return {"error": "Product not found"}, 404

    result = {
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "description": product.description,
        "price": float(product.price),
        "current_stock": product.current_stock,
        "low_stock_threshold": product.low_stock_threshold,
        "category_id": product.category_id
    }

    return jsonify(result), 200

@product_bp.route("/products/<int:id>", methods=["PUT"])
def update_product(id):

    data = request.get_json(silent=True)

    if not data:
        return {"error": "Request body is required"}, 400

    # Find product
    product = db.session.get(Product, id)

    if not product:
        return {"error": "Product not found"}, 404

    # Required fields for PUT
    name = data.get("name")
    sku = data.get("sku")
    price = data.get("price")

    if not name or not sku or price is None:
        return {
            "error": "Name, SKU and price are required"
        }, 400

    description = data.get("description")
    low_stock_threshold = data.get("low_stock_threshold", 10)
    category_id = data.get("category_id")

    # Price validation
    if isinstance(price, bool) or not isinstance(price, (int, float)):
        return {"error": "Price must be a number"}, 400

    if price < 0:
        return {"error": "Price cannot be negative"}, 400

    # SKU uniqueness (exclude current product)
    existing_product = Product.query.filter(
        Product.sku == sku,
        Product.id != id
    ).first()

    if existing_product:
        return {"error": "SKU already exists"}, 409

    # Low stock threshold validation
    if (
        not isinstance(low_stock_threshold, int)
        or isinstance(low_stock_threshold, bool)
    ):
        return {
            "error": "Low stock threshold must be an integer"
        }, 400

    if low_stock_threshold < 0:
        return {
            "error": "Low stock threshold cannot be negative"
        }, 400

    # Category validation
    if category_id is not None:

        if (
            not isinstance(category_id, int)
            or isinstance(category_id, bool)
        ):
            return {
                "error": "Category ID must be an integer"
            }, 400

        category = db.session.get(Category, category_id)

        if not category:
            return {"error": "Category not found"}, 404

    # Update product fields
    product.name = name
    product.sku = sku
    product.description = description
    product.price = price
    product.low_stock_threshold = low_stock_threshold
    product.category_id = category_id

    db.session.commit()

    return {
        "message": "Product updated successfully",
        "product": {
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "description": product.description,
            "price": float(product.price),
            "current_stock": product.current_stock,
            "low_stock_threshold": product.low_stock_threshold,
            "category_id": product.category_id
        }
    }, 200


@product_bp.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):

    product = db.session.get(Product, id)

    if not product:
        return {"error": "Product not found"}, 404

    db.session.delete(product)
    db.session.commit()

    return {"message": "Product deleted successfully"}, 200