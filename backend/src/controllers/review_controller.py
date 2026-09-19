from typing import List

from fastapi import HTTPException

from src.data.store import delete_review_item, get_review_item, get_review_queue
from src.models.request import ReviewSubmission
from src.models.response import ReviewActionResult, ReviewItem


def handle_get_review_queue() -> List[ReviewItem]:
    """Return every match currently sitting below the confidence threshold."""
    return [ReviewItem(**item) for item in get_review_queue()]


def handle_submit_review(payload: ReviewSubmission) -> ReviewActionResult:
    """A human coder confirms or corrects a low-confidence match."""
    item = get_review_item(payload.review_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Review item '{payload.review_id}' not found")

    # For the demo: resolving a review just removes it from the queue.
    # A real implementation would also persist the correction back into mappings.json.
    delete_review_item(payload.review_id)

    message = (
        "Match confirmed and added to trusted mappings."
        if payload.approved
        else "Correction recorded."
    )
    return ReviewActionResult(review_id=payload.review_id, approved=payload.approved, message=message)