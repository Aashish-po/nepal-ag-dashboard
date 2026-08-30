"""Add performance indexes.

Revision ID: 0002_add_indexes
Revises: 0002_rename_tables
Create Date: 2026-08-29 09:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic
revision = "0002_add_indexes"
down_revision = "0002_rename_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add indexes for query performance."""
    # Yields indexes
    op.create_index(
        "ix_yields_district_crop_year", "yields", ["district_id", "crop_id", "year"]
    )
    op.create_index("ix_yields_district_id", "yields", ["district_id"])
    op.create_index("ix_yields_crop_id", "yields", ["crop_id"])
    op.create_index("ix_yields_year", "yields", ["year"])

    # Climate indexes
    op.create_index(
        "ix_climate_district_date", "climate", ["district_id", "observation_date"]
    )
    op.create_index("ix_climate_district_id", "climate", ["district_id"])

    # Districts indexes
    op.create_index("ix_districts_province", "districts", ["province"])
    op.create_index("ix_districts_region", "districts", ["region"])
    op.create_index("ix_districts_name", "districts", ["name"])


def downgrade() -> None:
    """Remove indexes."""
    op.drop_index("ix_districts_name", table_name="districts")
    op.drop_index("ix_districts_region", table_name="districts")
    op.drop_index("ix_districts_province", table_name="districts")
    op.drop_index("ix_climate_district_id", table_name="climate")
    op.drop_index("ix_climate_district_date", table_name="climate")
    op.drop_index("ix_yields_year", table_name="yields")
    op.drop_index("ix_yields_crop_id", table_name="yields")
    op.drop_index("ix_yields_district_id", table_name="yields")
    op.drop_index("ix_yields_district_crop_year", table_name="yields")
