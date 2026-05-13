"""
In-memory job storage. Thread-safe for reading; writers should call update().

JobDict is the single source of truth for job shape — every key that pipeline.py
and routes.py touch must be declared here.
"""
import asyncio
from pathlib import Path
from typing import Any, TypedDict

from domain.models import Checkpoint, ProcessConfig, TranscriptSegment


class _JobDictBase(TypedDict):
    """Fields that are always present from the moment a job is created."""
    status: str                              # JobStatus value
    message: str
    progress: int
    video_path: Path
    filename: str
    duration: float
    transcript: list[TranscriptSegment]
    checkpoints: list[Checkpoint]
    video_info: str
    source_urls: dict[str, str]
    queue_analysis: asyncio.Queue
    queue_export: asyncio.Queue
    queue_clarify: asyncio.Queue
    loop: asyncio.AbstractEventLoop
    output: Path | None
    error: str | None
    config: ProcessConfig | None
    learning_script: dict | None
    player_html: str | None
    token_usage: dict


class JobDict(_JobDictBase, total=False):
    """Optional fields set after creation (e.g. by the export route)."""
    _export_learning_script: dict


class JobStore:
    def __init__(self):
        self._jobs: dict[str, JobDict] = {}

    def create(self, job_id: str, loop: asyncio.AbstractEventLoop, video_path: Path, filename: str, duration: float) -> JobDict:
        """Create a new job dict and store it. Returns the job dict."""
        job: JobDict = {
            "status": "queued",
            "message": "Ready to process",
            "progress": 0,
            "output": None,
            "error": None,
            "video_path": video_path,
            "filename": filename,
            "duration": duration,
            "config": None,
            "transcript": [],
            "checkpoints": [],
            "video_info": "",
            "source_urls": {},
            "learning_script": None,
            "player_html": None,
            "token_usage": {},
            "queue_analysis": asyncio.Queue(),
            "queue_export": asyncio.Queue(),
            "queue_clarify": asyncio.Queue(),
            "loop": loop,
        }
        self._jobs[job_id] = job
        return job

    def get(self, job_id: str) -> JobDict | None:
        return self._jobs.get(job_id)

    def require(self, job_id: str) -> JobDict:
        """Get job or raise KeyError if not found."""
        job = self._jobs.get(job_id)
        if job is None:
            raise KeyError(job_id)
        return job

    def exists(self, job_id: str) -> bool:
        return job_id in self._jobs

    def update(self, job_id: str, **kwargs: Any) -> None:
        """Merge kwargs into job dict."""
        self._jobs[job_id].update(kwargs)  # type: ignore[typeddict-item]

# Singleton — imported by pipeline.py and routes.py
store = JobStore()
