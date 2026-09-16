from datetime import datetime, timezone

from ..extensions import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    sku = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    description = db.Column(
        db.String(500),
        nullable=True
    )

    price = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    current_stock = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    low_stock_threshold = db.Column(
        db.Integer,
        nullable=False,
        default=10
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

