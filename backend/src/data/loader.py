# backend/src/data/loader.py
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_MAPPINGS_PATH = Path(__file__).parent / "mappings.json"
_mappings_cache: list[dict[str, Any]] | None = None


def load_mappings() -> list[dict[str, Any]]:
    """
    Reads mappings.json from disk and parses it into a list of dicts.
    Populates the module-level cache. Called once at startup (and lazily
    if something accesses get_mappings() before startup runs).
    """
    global _mappings_cache

    try:
        with open(_MAPPINGS_PATH, encoding="utf-8") as f:
            raw = json.load(f)
        _mappings_cache = raw["mappings"]
    except FileNotFoundError:
        logger.error(f"mappings.json not found at {_MAPPINGS_PATH}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"mappings.json at {_MAPPINGS_PATH} is not valid JSON: {e}")
        raise
    except KeyError:
        logger.error(f"mappings.json at {_MAPPINGS_PATH} is missing the top-level 'mappings' key")
        raise

    logger.info(f"Loaded {len(_mappings_cache)} mappings from {_MAPPINGS_PATH}")
    return _mappings_cache


def get_mappings() -> list[dict[str, Any]]:
    """
    Accessor used by fuzzy_search.py and anywhere else that needs the
    in-memory dataset. Lazy-loads if load_mappings() hasn't run yet.
    """
    if _mappings_cache is None:
        load_mappings()
    return _mappings_cache