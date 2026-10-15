from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Product, Category, InventoryTransaction

product_bp = Blueprint("product", __name__)


@product_bp.route("/products", methods=["POST"])
@jwt_required()
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


@product_bp.route("/products", methods=["GET"])
def display_product():

    query = Product.query

    # 1. Search by product name or SKU
    search = request.args.get("search", "").strip()

    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f"%{search}%"),
                Product.sku.ilike(f"%{search}%")
            )
        )

    # 2. Filter by category ID
    category_id = request.args.get("category_id", type=int)

    if category_id is not None:
        if category_id <= 0:
            return {"error": "Category ID must be positive"}, 400

        query = query.filter(Product.category_id == category_id)

    # 3. Filter low-stock products
    low_stock = request.args.get("low_stock")

    if low_stock is not None:
        if low_stock.lower() not in ("true", "false"):
            return {"error": "low_stock must be true or false"}, 400

        if low_stock.lower() == "true":
            query = query.filter(
                Product.current_stock <= Product.low_stock_threshold
            )
        else:
            query = query.filter(
                Product.current_stock > Product.low_stock_threshold
            )

    # 4. Pagination validation
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    if page < 1:
        return {"error": "Page must be at least 1"}, 400

    if per_page < 1 or per_page > 100:
        return {"error": "per_page must be between 1 and 100"}, 400

    # 5. Total count before pagination
    total = query.count()

    # 6. Fetch requested page
    products = (
        query.order_by(Product.id.asc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

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

    return jsonify({
        "products": result,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page
        }
    }), 200


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
@jwt_required()
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
@jwt_required()
def delete_product(id):

    product = db.session.get(Product, id)

    if not product:
        return {"error": "Product not found"}, 404

    db.session.delete(product)
    db.session.commit()

    return {"message": "Product deleted successfully"}, 200


@product_bp.route("/products/<int:id>/stock-in", methods=["POST"])
@jwt_required()
def stock_in(id):

    # 1. Request body validate karo
    data = request.get_json(silent=True)

    if not data:
        return {"error": "Request body is required"}, 400

    # 2. Quantity validate karo
    quantity = data.get("quantity")

    if (
        not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity <= 0
    ):
        return {"error": "Quantity must be a positive integer"}, 400

    # 3. Product exist karta hai ya nahi
    product = db.session.get(Product, id)

    if not product:
        return {"error": "Product not found"}, 404

    # 4. JWT se logged-in admin ki ID lo
    user_id = int(get_jwt_identity())

    try:
        # 5. Stock update karo
        product.current_stock += quantity

        # 6. Inventory history record banao
        transaction = InventoryTransaction(
            product_id=product.id,
            user_id=user_id,
            type="IN",
            quantity=quantity
        )

        db.session.add(transaction)

        # 7. Dono changes ek saath save karo
        db.session.commit()

    except Exception:
        # Failure par dono changes rollback honge
        db.session.rollback()
        return {"error": "Stock-in operation failed"}, 500

    # 8. Success response
    return {
        "message": "Stock added successfully",
        "product_id": product.id,
        "quantity_added": quantity,
        "current_stock": product.current_stock
    }, 200




@product_bp.route("/products/<int:id>/stock-out", methods=["POST"])
@jwt_required()
def stock_out(id):

    data = request.get_json(silent=True)

    if not data:
        return {"error": "Request body is required"}, 400

    quantity = data.get("quantity")

    if (
        not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity <= 0
    ):
        return {"error": "Quantity must be a positive integer"}, 400

    user_id = int(get_jwt_identity())

    try:
        # Atomic update: stock sufficient ho tabhi decrement hoga
        result = (
            db.session.query(Product)
            .filter(
                Product.id == id,
                Product.current_stock >= quantity
            )
            .update(
                {
                    Product.current_stock:
                        Product.current_stock - quantity
                },
                synchronize_session=False
            )
        )

        if result == 0:
            db.session.rollback()

            product_exists = db.session.get(Product, id)

            if not product_exists:
                return {"error": "Product not found"}, 404

            return {"error": "Insufficient stock"}, 400

        transaction = InventoryTransaction(
            product_id=id,
            user_id=user_id,
            type="OUT",
            quantity=quantity
        )

        db.session.add(transaction)
        db.session.flush()

        product = db.session.get(Product, id)
        current_stock = product.current_stock

        db.session.commit()

    except Exception:
        db.session.rollback()
        return {"error": "Stock-out operation failed"}, 500

    return {
        "message": "Stock issued successfully",
        "product_id": id,
        "quantity_removed": quantity,
        "current_stock": current_stock
    }, 200


@product_bp.route("/products/low-stock", methods=["GET"])
@jwt_required()
def get_low_stock_products():

    products = Product.query.filter(
        Product.current_stock <= Product.low_stock_threshold
    ).all()

    result = []

    for product in products:
        result.append({
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "current_stock": product.current_stock,
            "low_stock_threshold": product.low_stock_threshold
        })

    return jsonify(result), 200
