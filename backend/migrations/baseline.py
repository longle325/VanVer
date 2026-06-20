from __future__ import annotations

from collections.abc import Iterable


def should_stamp_legacy_schema(
    existing_table_names: Iterable[str],
    model_table_names: Iterable[str],
    *,
    version_table: str = "alembic_version",
) -> bool:
    existing = set(existing_table_names)
    model_tables = set(model_table_names)
    if version_table in existing:
        return False
    return bool(model_tables) and model_tables.issubset(existing)
