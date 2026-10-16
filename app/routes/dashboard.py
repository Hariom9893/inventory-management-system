from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from ..extensions import db
from ..models import Product, Category

dashboard_bp = Blueprint("dashboard", __name__)
@dashboard_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def get_dashboard():
    total_products = Product.query.count()

    total_categories = Category.query.count()

    low_stock_count = Product.query.filter(
        Product.current_stock <= Product.low_stock_threshold
    ).count()

    inventory_value = db.session.query(
        func.coalesce(
            func.sum(Product.price * Product.current_stock), 0
        )
    ).scalar()

    return jsonify({
        "total_products": total_products,
        "total_categories": total_categories,
        "low_stock_count": low_stock_count,
        "inventory_value": float(inventory_value)
    }), 200