from src.core.constants import CONFIDENCE_THRESHOLD

def evaluate_confidence(score: float) -> str:
    if score >= CONFIDENCE_THRESHOLD:
        return "auto_coded"
    return "needs_review"