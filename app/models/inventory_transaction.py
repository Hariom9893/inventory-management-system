from datetime import datetime, timezone
from ..extensions import db


class InventoryTransaction(db.Model):
    __tablename__ = "inventory_transactions"

    __table_args__ = (
        db.CheckConstraint(
            "quantity > 0",
            name="chk_transaction_quantity"
        ),
        db.CheckConstraint(
            "`type` IN ('IN', 'OUT')",
            name="chk_transaction_type"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    type = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
