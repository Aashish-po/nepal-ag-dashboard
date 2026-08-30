"""Add missing performance indexes to Climate, CommercializationIndex, and Forecasts.

Revision ID: 0003
Revises: 0002_add_indexes
Create Date: 2026-08-29 09:30:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic
revision = "0003"
down_revision = "0002_add_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add indexes for query performance on fact tables."""

    # ===== Climate Table Indexes =====
    # Primary query pattern: SELECT * FROM climate WHERE district_id = X AND observation_date BETWEEN Y AND Z
    op.create_index(
        "ix_climate_district_date",
        "climate",
        ["district_id", "observation_date"],
        if_not_exists=True,
    )
    # Direct district lookups
    op.create_index(
        "ix_climate_district_id", "climate", ["district_id"], if_not_exists=True
    )

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

    # Climate
    op.drop_index("ix_climate_district_id", table_name="climate", if_exists=True)
    op.drop_index("ix_climate_district_date", table_name="climate", if_exists=True)
