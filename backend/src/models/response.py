from typing import List, Optional
from pydantic import BaseModel, Field

from src.core.constants import FHIR_RESOURCE_TYPE


class Coding(BaseModel):
    system: str
    code: str
    display: str


class CodeableConcept(BaseModel):
    coding: List[Coding]


class Alternative(BaseModel):
    term: str
    confidence: float


class CodeResponse(BaseModel):
    """FHIR R4-flavored Condition resource, extended with CodeBridge matching metadata."""

    resourceType: str = FHIR_RESOURCE_TYPE
    code: CodeableConcept
    confidence: float
    status: str  # "auto_coded" | "needs_review"
    matched_term: str
    alternatives: List[Alternative] = Field(default_factory=list)


class HistoryEntry(BaseModel):
    id: str
    query_text: str
    result: CodeResponse
    timestamp: str


class ReviewItem(BaseModel):
    review_id: str
    query_text: str
    suggested: CodeResponse
    created_at: str


class ReviewActionResult(BaseModel):
    review_id: str
    approved: bool
    message: str


class SyncResponse(BaseModel):
    updated_count: int
    changes: List[str]
    last_synced_at: str