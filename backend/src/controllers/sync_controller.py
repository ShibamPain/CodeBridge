from src.models.response import SyncResponse
from src.services.sync_engine import run_sync


def handle_sync() -> SyncResponse:
    result = run_sync()
    return SyncResponse(**result)