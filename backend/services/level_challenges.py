"""
Server-side level-challenge definitions used for authoritative grading.

The data file is generated from the canonical frontend definitions
(frontend/src/data/levelChallenges.ts) via
frontend/scripts/gen-level-challenge-keys.cjs, so the answer keys and rubrics
the server grades against always match the questions the UI renders.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "level_challenges.json"


@lru_cache(maxsize=1)
def _load() -> dict[str, list[dict[str, Any]]]:
    with _DATA_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def get_level_definition(slug: str, level: int) -> Optional[dict[str, Any]]:
    """Return the {level, phaseTitle, questions} definition, or None.

    The data file is keyed by the frontend's hyphenated slug (``chi-pheo``)
    while the database stores the underscore form (``chi_pheo``); normalize so
    either form resolves.
    """
    normalized = slug.replace("_", "-")
    for entry in _load().get(normalized, []):
        if entry.get("level") == level:
            return entry
    return None
