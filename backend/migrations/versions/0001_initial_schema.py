"""Create the ORM schema."""

from __future__ import annotations

from alembic import op
from api.models.db_models import Base
from sqlalchemy import ARRAY, JSON

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    # PostgreSQL stores export countries as TEXT[]. SQLite has no array type,
    # so the local validation database uses JSON for the same logical value.
    if bind.dialect.name == "sqlite":
        column = Base.metadata.tables["exportcrops"].c.main_export_countries
        if isinstance(column.type, ARRAY):
            column.type = JSON()

    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
