# backend/src/services/fuzzy_search.py
from rapidfuzz import fuzz
from src.data.loader import get_mappings
from src.services.confidence import evaluate_confidence

def find_best_match(query_text: str) -> dict:
    records = get_mappings()
    best_score = 0.0
    best_record = None
    matched_term = ""

    for record in records:
        # Evaluate query against all three available text fields
        score_eng = fuzz.WRatio(query_text, record.get("namaste_term", ""))
        score_dev = fuzz.WRatio(query_text, record.get("namaste_term_devanagari", ""))
        score_icd = fuzz.WRatio(query_text, record.get("icd11_title", ""))

        max_for_record = max(score_eng, score_dev, score_icd)

        # Track the highest score and the exact string that triggered it
        if max_for_record > best_score:
            best_score = max_for_record
            best_record = record
            
            if max_for_record == score_eng:
                matched_term = record.get("namaste_term", "")
            elif max_for_record == score_dev:
                matched_term = record.get("namaste_term_devanagari", "")
            else:
                matched_term = record.get("icd11_title", "")

    # Rapidfuzz returns 0-100. Normalize to 0.0-1.0 to match the 0.85 threshold.
    normalized_score = round(best_score / 100, 4)

    return {
        "record": best_record,
        "score": normalized_score,
        "matched_term": matched_term
    }

def process_diagnosis(query_text: str) -> dict:
    """Single entry point for the controller to process a search."""
    match = find_best_match(query_text)
    
    if not match["record"]:
        return {"error": "No records loaded or matched."}

    record = match["record"]
    status = evaluate_confidence(match["score"])

    # Returns the exact shape required to build the FHIR R4 JSON
    return {
        "query": query_text,
        "matched_namaste_code": record.get("namaste_code", ""),
        "matched_icd11_code": record.get("icd11_code", ""),
        "namaste_display": record.get("namaste_term", ""),
        "icd11_display": record.get("icd11_title", ""),
        "confidence_score": match["score"],
        "status": status,
        "matched_on": match["matched_term"]
    }