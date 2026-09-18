"""
Handles POST /v1/code.

HACKATHON SPEED TRICK (per plan): this currently returns a hardcoded mock
FHIR response so the frontend and Swagger UI can be tested immediately,
without waiting on Stream 1's fuzzy matching engine.

=== INTEGRATION POINT (do this once Stream 1 hands off) ===
1. Uncomment the `from src.services.fuzzy_search import process_diagnosis` import.
2. Delete `_build_mock_result()` and the mock branch in `handle_code`.
3. Call `process_diagnosis(payload.text)` and pass its dict straight into
   `CodeResponse(**result)` — field names in response.py already match
   the dict shape process_diagnosis() is expected to return.
"""
import uuid
from datetime import datetime, timezone

from src.core.constants import ICD11_SYSTEM_URL, NAMASTE_SYSTEM_URL, STATUS_AUTO_CODED
from src.data.store import history, review_queue
from src.models.request import CodeRequest
from src.models.response import CodeResponse

# --- Stream 1 handoff import (currently disabled — see docstring above) ---
# from src.services.fuzzy_search import process_diagnosis

try:
    from src.services.fuzzy_search import process_diagnosis  # type: ignore
    _REAL_ENGINE_AVAILABLE = True
except ImportError:
    _REAL_ENGINE_AVAILABLE = False


def _build_mock_result(query_text: str) -> dict:
    """Deterministic fake result so the demo always looks good pre-integration."""
    return {
        "resourceType": "Condition",
        "code": {
            "coding": [
                {
                    "system": ICD11_SYSTEM_URL,
                    "code": "5A11",
                    "display": "Type 2 diabetes mellitus",
                },
                {
                    "system": NAMASTE_SYSTEM_URL,
                    "code": "TM2-AY-MDB-001",
                    "display": "Madhumeha",
                },
            ]
        },
        "confidence": 0.97,
        "status": STATUS_AUTO_CODED,
        "matched_term": query_text or "Madhumeha",
        "alternatives": [{"term": "Prameha", "confidence": 0.82}],
    }


def handle_code(payload: CodeRequest) -> CodeResponse:
    if _REAL_ENGINE_AVAILABLE:
        result_dict = process_diagnosis(payload.text)
    else:
        result_dict = _build_mock_result(payload.text)

    result = CodeResponse(**result_dict)

    # Log to in-memory history so GET /v1/history has something to show.
    history.append(
        {
            "id": str(uuid.uuid4()),
            "query_text": payload.text,
            "result": result.model_dump(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )

    # If below threshold, drop into the review queue too.
    if result.status != STATUS_AUTO_CODED:
        review_id = str(uuid.uuid4())
        review_queue[review_id] = {
            "review_id": review_id,
            "query_text": payload.text,
            "suggested": result.model_dump(),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    return result