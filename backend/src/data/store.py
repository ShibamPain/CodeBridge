"""
Tiny in-memory data store shared by the controllers.
Not in the original tree, but code_controller (writes), history_controller
(reads), and review_controller (reads/writes) all need a common place to
stash state for the demo — no real DB for a 30-hour hackathon.
Swap this for real persistence post-hackathon.
"""
from typing import Dict, List

history: List[dict] = []          # every /v1/code call, most recent last
review_queue: Dict[str, dict] = {}  # review_id -> {query_text, suggested, created_at}