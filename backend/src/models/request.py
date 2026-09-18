from typing import Optional
from pydantic import BaseModel, Field


class CodeRequest(BaseModel):
    """Incoming payload for POST /v1/code"""

    text: str = Field(
        ...,
        min_length=1,
        description="Free-text diagnosis in English, Hindi, or Sanskrit.",
        examples=["Madhumeha"],
    )
    language: Optional[str] = Field(
        default=None,
        description="Optional ISO language hint: 'en', 'hi', 'sa'. Not required for matching.",
        examples=["en"],
    )


class ReviewSubmission(BaseModel):
    """Incoming payload for POST /v1/review — a coder confirming/correcting a low-confidence match."""

    review_id: str
    corrected_icd_code: Optional[str] = None
    corrected_namaste_code: Optional[str] = None
    approved: bool = Field(
        ..., description="True if the coder confirms the suggested match is correct."
    )
    reviewer_notes: Optional[str] = None