from typing import List

from fastapi import APIRouter, Query

from src.controllers.code_controller import handle_code
from src.controllers.history_controller import handle_get_history
from src.controllers.review_controller import handle_get_review_queue, handle_submit_review
from src.controllers.sync_controller import handle_sync
from src.models.request import CodeRequest, ReviewSubmission
from src.models.response import (
    CodeResponse,
    HistoryEntry,
    ReviewActionResult,
    ReviewItem,
    SyncResponse,
)

router = APIRouter(prefix="/v1")


@router.post("/code", response_model=CodeResponse, summary="Translate a diagnosis into ICD-11 + NAMASTE codes")
def post_code(payload: CodeRequest) -> CodeResponse:
    return handle_code(payload)


@router.get("/history", response_model=List[HistoryEntry], summary="Get past translations")
def get_history(limit: int = Query(default=50, ge=1, le=500)) -> List[HistoryEntry]:
    return handle_get_history(limit=limit)


@router.get("/review", response_model=List[ReviewItem], summary="Get matches below the confidence threshold")
def get_review_queue() -> List[ReviewItem]:
    return handle_get_review_queue()


@router.post("/review", response_model=ReviewActionResult, summary="Confirm or correct a low-confidence match")
def post_review(payload: ReviewSubmission) -> ReviewActionResult:
    return handle_submit_review(payload)


@router.post("/sync", response_model=SyncResponse, summary="Simulate a Ministry of Ayush code update")
def post_sync() -> SyncResponse:
    return handle_sync()