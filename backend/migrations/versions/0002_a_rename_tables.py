"""Rename legacy auto-named tables to their canonical names.

The original ``Base`` used a ``declared_attr`` that pluralised class names,
producing ``climates``, ``exportcrops``, ``commercializationindexs``. The ORM
now declares explicit ``__tablename__``s, and the raw SQL / ETL already target
the canonical ``climate``, ``export_crops``, ``commercialization_index``. This
migration renames those tables in any database created under the old scheme.

On a fresh database, 0001 already creates the canonical names, so each rename is
skipped (the source table is absent). The renamed tables were empty in every
known environment, so this is metadata-only and loss-free.
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import inspect

revision = "0002_rename_tables"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None

_RENAMES = [
    ("climates", "climate"),
    ("exportcrops", "export_crops"),
    ("commercializationindexs", "commercialization_index"),
]


def upgrade() -> None:
    existing = set(inspect(op.get_bind()).get_table_names())
    for old, new in _RENAMES:
        if old in existing and new not in existing:
            op.rename_table(old, new)


def downgrade() -> None:
    # No-op: everything (ORM, raw SQL, ETL) targets canonical names; renaming back
    # would re-break them. 0001's drop_all uses canonical names, so leaving these
    # untouched keeps the round-trip clean.
    pass
