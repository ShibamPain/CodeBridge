"""
Simulates the Ministry of Ayush pushing an update to the NAMASTE/TM2 or
ICD-11 code set. In a real system this would hit an external registry;
for the hackathon demo we simulate a plausible diff and update an
in-memory "last synced" timestamp so the frontend can show a live
"Synced just now" state.
"""
import random
from datetime import datetime, timezone

_last_synced_at: str | None = None

# A pool of plausible fake changes so each demo run looks slightly different.
_SIMULATED_CHANGE_POOL = [
    "Added new NAMASTE code TM2-AY-PRM-014 for 'Prameha, kaphaja type'",
    "Updated display name for ICD-11 code 5A11 to 'Type 2 diabetes mellitus, confirmed'",
    "Deprecated legacy code NAM-OLD-0091 in favor of TM2-AY-MDB-001",
    "Added synonym mapping: 'मधुमेह' -> TM2-AY-MDB-001",
    "Revised confidence threshold guidance for dosha-pattern matches",
]


def run_sync() -> dict:
    """
    Simulate checking for and applying a Ministry update.
    Returns a dict matching the SyncResponse model.
    """
    global _last_synced_at

    num_changes = random.randint(1, 3)
    changes = random.sample(_SIMULATED_CHANGE_POOL, k=num_changes)

    _last_synced_at = datetime.now(timezone.utc).isoformat()

    return {
        "updated_count": num_changes,
        "changes": changes,
        "last_synced_at": _last_synced_at,
    }


def get_last_synced_at() -> str | None:
    return _last_synced_at