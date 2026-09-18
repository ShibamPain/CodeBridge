"""
Shared constants for CodeBridge.
Stream 1 (fuzzy_search.py / confidence.py) and Stream 2 (controllers) both
import from here so the threshold and system URLs only ever live in one place.
"""

# --- Matching ---
# Rapidfuzz WRatio score (0-100) is normalized to 0-1 before comparing to this.
CONFIDENCE_THRESHOLD = 0.85

# --- FHIR R4 CodeSystem URLs ---
ICD11_SYSTEM_URL = "http://id.who.int/icd/release/11/2023-01"
NAMASTE_SYSTEM_URL = "https://namaste.ayush.gov.in/tm2"

# --- Status labels used in the response payload ---
STATUS_AUTO_CODED = "auto_coded"
STATUS_NEEDS_REVIEW = "needs_review"

# --- Resource defaults ---
FHIR_RESOURCE_TYPE = "Condition"