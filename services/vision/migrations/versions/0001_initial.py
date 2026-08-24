"""Initial collection-isolated schema.

Revision ID: 0001
Revises:
"""

from alembic import op

from vision_service import models  # noqa: F401
from vision_service.database import Base

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
