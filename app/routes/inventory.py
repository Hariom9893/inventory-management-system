
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models import InventoryTransaction, Product, User
from ..extensions import db
inventory_bp = Blueprint("inventory", __name__)


@inventory_bp.route("/inventory/transactions", methods=["GET"])
@jwt_required()
def get_inventory_transactions():

    query = InventoryTransaction.query

    # Product ID filter
    product_id = request.args.get("product_id", type=int)

    if product_id is not None:
        if product_id <= 0:
            return {"error": "Product ID must be positive"}, 400

        query = query.filter(
            InventoryTransaction.product_id == product_id
        )

    # Transaction type filter
    transaction_type = request.args.get("type")

    if transaction_type is not None:
        transaction_type = transaction_type.upper()

        if transaction_type not in ("IN", "OUT"):
            return {"error": "Type must be IN or OUT"}, 400

        query = query.filter(
            InventoryTransaction.type == transaction_type
        )

    transactions = query.order_by(
        InventoryTransaction.created_at.desc(),
        InventoryTransaction.id.desc()
    ).all()

    result = []

    for transaction in transactions:
        product = db.session.get(Product, transaction.product_id)
        user = db.session.get(User, transaction.user_id)

        result.append({
            "id": transaction.id,
            "product_id": transaction.product_id,
            "product_name": product.name if product else None,
            "user_id": transaction.user_id,
            "user_name": user.name if user else None,
            "type": transaction.type,
            "quantity": transaction.quantity,
            "created_at": transaction.created_at.isoformat()
        })

    return jsonify(result), 200
