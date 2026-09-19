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

from fastapi import HTTPException

from src.core.constants import (
    ICD11_SYSTEM_URL,
    NAMASTE_SYSTEM_URL,
    STATUS_AUTO_CODED,
    STATUS_NEEDS_REVIEW,
)
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


class EngineResultError(ValueError):
    """Raised when Stream 1's engine returns data that's missing, malformed,
    or too suspicious to serve as-is. Caught in handle_code() and turned
    into a clean 502 instead of a raw crash or, worse, silently-wrong data."""


def _adapt_engine_result(raw: dict) -> dict:
    """
    Stream 1's process_diagnosis() returns a flat dict with different field
    names than our FHIR-shaped CodeResponse expects. This adapter converts
    theirs into ours, and REFUSES to pass through data that looks broken
    rather than silently forwarding it to the doctor/EMR.
    """
    required_fields = [
        "matched_icd11_code",
        "matched_namaste_code",
        "icd11_display",
        "namaste_display",
        "confidence_score",
    ]
    missing = [f for f in required_fields if raw.get(f) in (None, "")]
    if missing:
        raise EngineResultError(
            f"process_diagnosis() returned incomplete data — missing/empty field(s): {missing}. "
            f"Raw output: {raw}"
        )

    icd_code = raw["matched_icd11_code"]
    namaste_code = raw["matched_namaste_code"]
    confidence = raw["confidence_score"]

    if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
        raise EngineResultError(
            f"confidence_score must be a number between 0 and 1, got: {confidence!r} (raw: {raw})"
        )

    # NOTE: We do NOT flag namaste_code containing icd_code as suspicious.
    # In this domain, an "equivalent" TM2 mapping legitimately looks like
    # icd11_code="SN00", namaste_code="SN00(ABB-31)" — the NAMASTE code
    # intentionally embeds the TM2 code as a prefix. Quality control here
    # is confidence.py's threshold, not code-string shape.
    status = raw.get("status", STATUS_NEEDS_REVIEW)

    return {
        "resourceType": "Condition",
        "code": {
            "coding": [
                {
                    "system": ICD11_SYSTEM_URL,
                    "code": icd_code,
                    "display": raw["icd11_display"],
                },
                {
                    "system": NAMASTE_SYSTEM_URL,
                    "code": namaste_code,
                    "display": raw["namaste_display"],
                },
            ]
        },
        "confidence": confidence,
        "status": status,
        "matched_term": raw.get("query") or raw.get("matched_on", ""),
        "alternatives": raw.get("alternatives", []),
    }


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
        raw_result = process_diagnosis(payload.text)
        try:
            result_dict = _adapt_engine_result(raw_result)
        except EngineResultError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Matching engine returned invalid data: {exc}",
            )
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