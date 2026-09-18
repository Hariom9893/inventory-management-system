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