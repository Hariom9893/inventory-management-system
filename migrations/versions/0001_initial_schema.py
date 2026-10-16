
"""Baseline migration for the existing inventory database."""

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Existing tables already match the SQLAlchemy models.
    # This baseline intentionally makes no schema changes.
    pass


def downgrade():
    # Do not drop existing tables or data.
    pass
