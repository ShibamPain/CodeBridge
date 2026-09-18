from typing import List

from src.data.store import history
from src.models.response import HistoryEntry


def handle_get_history(limit: int = 50) -> List[HistoryEntry]:
    """Return the most recent translations, newest first."""
    recent = list(reversed(history))[:limit]
    return [HistoryEntry(**entry) for entry in recent]