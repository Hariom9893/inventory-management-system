from datetime import datetime, timezone

from ..extensions import db


class InventoryTransaction(db.Model):
    __tablename__ = "inventory_transactions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

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

    type = db.Column(
        db.String(10),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

