"""Add missing performance indexes to CommercializationIndex and Forecasts.

Revision ID: 0003
Revises: 0002_add_indexes
Create Date: 2026-08-29 09:30:00.000000

Note: Climate table indexes were added in 0002_add_indexes.
"""

from alembic import op

# revision identifiers, used by Alembic
revision = "0003"
down_revision = "0002_add_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add indexes for query performance on fact tables."""

    # ===== CommercializationIndex Table Indexes =====
    # Primary query pattern: SELECT * FROM commercialization_index WHERE district_id = X
    op.create_index(
        "ix_commercialization_district_id",
        "commercialization_index",
        ["district_id"],
        if_not_exists=True,
    )

    # ===== Forecasts Table Indexes =====
    # Primary query pattern: SELECT * FROM forecasts WHERE district_id = X AND crop_id = Y AND forecast_month BETWEEN Z1 AND Z2
    op.create_index(
        "ix_forecasts_district_crop_month",
        "forecasts",
        ["district_id", "crop_id", "forecast_month"],
        if_not_exists=True,
    )
    # Direct district lookups
    op.create_index(
        "ix_forecasts_district_id", "forecasts", ["district_id"], if_not_exists=True
    )


def downgrade() -> None:
    """Remove indexes."""

    # Forecasts
    op.drop_index("ix_forecasts_district_id", table_name="forecasts", if_exists=True)
    op.drop_index(
        "ix_forecasts_district_crop_month", table_name="forecasts", if_exists=True
    )

    # CommercializationIndex
    op.drop_index(
        "ix_commercialization_district_id",
        table_name="commercialization_index",
        if_exists=True,
    )
