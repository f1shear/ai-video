"""
SSE event emission helpers. Puts JSON-encoded events onto the job's asyncio queue
so the StreamingResponse can pick them up.
"""
import asyncio
import json
import logging
from .job_store import store

logger = logging.getLogger("checkpoint_overlay")


def emit(job_id: str, status: str, message: str, progress: int, queue_key: str = "queue_analysis") -> None:
    """Emit a progress event onto the analysis or export SSE queue."""
    job = store.get(job_id)
    if not job:
        return
    store.update(job_id, status=status, message=message, progress=progress)
    payload = json.dumps({"status": status, "message": message, "progress": progress})
    try:
        asyncio.run_coroutine_threadsafe(job[queue_key].put(payload), job["loop"])  # type: ignore[literal-required]
    except Exception as e:
        logger.warning("emit failed: %s", e)


def emit_clarify(job_id: str, status: str, message: str, progress: int, questions: list | None = None) -> None:
    """Emit a progress event onto the clarify SSE queue."""
    job = store.get(job_id)
    if not job:
        return
    store.update(job_id, status=status, message=message, progress=progress)
    payload: dict = {"status": status, "message": message, "progress": progress}
    if questions is not None:
        payload["questions"] = questions
    try:
        asyncio.run_coroutine_threadsafe(job["queue_clarify"].put(json.dumps(payload)), job["loop"])
    except Exception as e:
        logger.warning("emit_clarify failed: %s", e)
