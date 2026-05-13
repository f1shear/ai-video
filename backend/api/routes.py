import asyncio
import logging
import os
import subprocess
import tempfile
import threading
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Query, UploadFile, HTTPException
from fastapi.responses import Response, StreamingResponse, FileResponse

from domain.models import ProcessConfig, JobStatus, ReasoningEffort
from settings import EXTENDED_THINKING_BUDGET, MODELS_WITHOUT_THINKING
from infrastructure.transcriber import get_video_duration
from services.checkpoint_service import generate_checkpoints
from services.learning_service import generate_learning_script
from services.understand_service import refine_understanding
from .job_store import store
from .pipeline import run_understand, run_analysis, run_export
from .schemas import (
    UploadResponse, StatusResponse, UnderstandAnswersRequest,
    ExportRequest, RegenerateRequest, RegenerateLearningRequest,
)
from .config import UPLOAD_DIR, ALLOWED_VIDEO_EXTENSIONS

logger = logging.getLogger("checkpoint_overlay")

router = APIRouter()


def _merge_usage(job_id: str, usage: dict) -> None:
    """Merge token usage from a service call into the job's running total."""
    if not usage:
        return
    existing = dict(store.require(job_id).get("token_usage") or {})
    store.update(job_id, token_usage={
        "input_tokens":  existing.get("input_tokens", 0)  + usage.get("input_tokens", 0),
        "output_tokens": existing.get("output_tokens", 0) + usage.get("output_tokens", 0),
        "cost_usd":      existing.get("cost_usd", 0.0)    + usage.get("cost_usd", 0.0),
        "models":        list(dict.fromkeys(
            existing.get("models", []) + usage.get("models", [])
        )),
    })


@router.post("/upload", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "No filename")
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(400, "Unsupported file type. Please upload MP4, MOV, AVI, MKV, or WebM.")

    job_id = str(uuid.uuid4())
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    video_path = job_dir / f"input{ext}"

    try:
        with open(video_path, "wb") as f:
            while chunk := await file.read(1024 * 1024):
                f.write(chunk)
    except Exception as e:
        import shutil
        shutil.rmtree(job_dir, ignore_errors=True)
        logger.error("upload: file write failed: %s", e)
        raise HTTPException(500, "Failed to save uploaded file. Please try again.")

    logger.info("upload: job=%s file=%s", job_id, file.filename)

    try:
        duration = get_video_duration(str(video_path))
    except Exception as e:
        logger.error("upload: could not read video: %s", e)
        raise HTTPException(400, "Could not read video file. Please check the file is a valid video.")

    loop = asyncio.get_running_loop()
    store.create(job_id, loop, video_path, file.filename, duration)

    return UploadResponse(job_id=job_id, filename=file.filename, duration=round(duration, 1))


@router.post("/pre-analyze/{job_id}")
async def pre_analyze_video(job_id: str):
    """Start the Understand step — transcribe, understand, generate questions."""
    if not store.exists(job_id):
        raise HTTPException(404, "Job not found")
    job = store.require(job_id)
    job["queue_clarify"] = asyncio.Queue()
    thread = threading.Thread(
        target=run_understand,
        args=(job_id,),
        daemon=True,
    )
    thread.start()
    return {"status": "started"}


@router.get("/pre-analyze-events/{job_id}")
async def stream_pre_analyze_events(job_id: str):
    if not store.exists(job_id):
        raise HTTPException(404, "Job not found")
    queue = store.require(job_id)["queue_clarify"]

    async def event_generator():
        while True:
            event = await queue.get()
            if event is None:
                yield "data: [DONE]\n\n"
                break
            yield f"data: {event}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/understand-answers/{job_id}")
async def submit_understand_answers(job_id: str, body: UnderstandAnswersRequest):
    """Refine video_info based on user answers. Synchronous — returns immediately."""
    if not store.exists(job_id):
        raise HTTPException(404, "Job not found")
    job = store.require(job_id)
    video_info = job.get("video_info", "")

    def _refine():
        refined, usage = refine_understanding(video_info, body.answers)
        store.update(job_id, video_info=refined)
        _merge_usage(job_id, usage)
        return refined

    try:
        refined = await asyncio.to_thread(_refine)
    except Exception as e:
        logger.error("understand-answers: refinement failed: %s", e, exc_info=True)
        raise HTTPException(500, "Failed to refine video understanding. Your answers were noted but could not be incorporated.")
    return {"video_info": refined}


@router.post("/process/{job_id}")
async def process_video(job_id: str, config: ProcessConfig):
    if not store.exists(job_id):
        raise HTTPException(404, "Job not found")
    store.update(job_id, config=config)
    logger.info("process: job=%s config=%s", job_id, config)

    thread = threading.Thread(
        target=run_analysis,
        args=(job_id, config),
        daemon=True,
    )
    thread.start()
    return {"status": "started"}


@router.get("/events/{job_id}")
async def stream_events(job_id: str):
    if not store.exists(job_id):
        raise HTTPException(404, "Job not found")

    queue = store.require(job_id)["queue_analysis"]

    async def event_generator():
        while True:
            event = await queue.get()
            if event is None:
                yield "data: [DONE]\n\n"
                break
            yield f"data: {event}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/checkpoints/{job_id}")
async def get_checkpoints(job_id: str):
    if not store.exists(job_id):
        raise HTTPException(404, "Job not found")
    job = store.require(job_id)
    if job["status"] not in (JobStatus.checkpoints_ready, JobStatus.generating_learning,
                              JobStatus.creating_overlays, JobStatus.exporting, JobStatus.done):
        raise HTTPException(400, "Checkpoints not ready yet")
    return {
        "summary": job.get("video_info", ""),
        "checkpoints": [cp.model_dump() for cp in job["checkpoints"]],
        "source_urls": job.get("source_urls", {}),
        "learning_script": job.get("learning_script") or {"title": "", "sections": [], "quiz_points": []},
        "token_usage": job.get("token_usage") or {},
    }


@router.post("/export/{job_id}")
async def export_video(job_id: str, request: ExportRequest):
    if not store.exists(job_id):
        raise HTTPException(404, "Job not found")
    job = store.require(job_id)
    config = job.get("config")
    if not config:
        raise HTTPException(400, "No config found for this job")
    logger.info("export: job=%s checkpoints=%d", job_id, len(request.checkpoints))

    if request.learning_script:
        store.update(job_id, _export_learning_script=request.learning_script)

    job["queue_export"] = asyncio.Queue()

    thread = threading.Thread(
        target=run_export,
        args=(job_id, request.checkpoints, config),
        daemon=True,
    )
    thread.start()
    return {"status": "started"}


@router.get("/export-events/{job_id}")
async def stream_export_events(job_id: str):
    if not store.exists(job_id):
        raise HTTPException(404, "Job not found")

    queue = store.require(job_id)["queue_export"]

    async def event_generator():
        while True:
            event = await queue.get()
            if event is None:
                yield "data: [DONE]\n\n"
                break
            yield f"data: {event}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/frame/{job_id}")
async def get_frame(
    job_id: str,
    t: float = Query(0.0, description="Timestamp in seconds"),
):
    if not store.exists(job_id):
        raise HTTPException(404, "Job not found")
    video_path = str(store.require(job_id)["video_path"])

    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    tmp.close()
    try:
        cmd = [
            "ffmpeg", "-y",
            "-ss", f"{max(0.0, t):.3f}",
            "-i", video_path,
            "-frames:v", "1",
            "-q:v", "4",
            "-vf", "scale=640:-2",
            tmp.name,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(tmp.name) or os.path.getsize(tmp.name) == 0:
            logger.warning("get_frame failed at t=%.2f: %s", t, r.stderr[-200:])
            raise HTTPException(500, "Frame extraction failed")
        with open(tmp.name, "rb") as f:
            data = f.read()
        return Response(content=data, media_type="image/jpeg")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_frame error: %s", e)
        raise HTTPException(500, "Frame extraction error")
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass


@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    if not store.exists(job_id):
        raise HTTPException(404, "Job not found")
    job = store.require(job_id)
    return StatusResponse(
        status=job["status"],
        message=job["message"],
        progress=job["progress"],
        error=job.get("error"),
    )


@router.get("/download/{job_id}")
async def download_result(job_id: str):
    if not store.exists(job_id):
        raise HTTPException(404, "Job not found")
    job = store.require(job_id)
    if job["status"] != JobStatus.done or not job.get("output"):
        raise HTTPException(400, "Video is not ready yet")
    output_path = job["output"]
    assert output_path is not None
    if not output_path.exists():
        raise HTTPException(500, "Output file not found")
    return FileResponse(
        str(output_path),
        media_type="video/mp4",
        filename="checkpoint_overlay_result.mp4",
    )


@router.get("/video/{job_id}")
async def stream_video(job_id: str):
    """Serve the exported video with range-request support (required for HTML5 video seeking)."""
    if not store.exists(job_id):
        raise HTTPException(404, "Job not found")
    job = store.require(job_id)
    if job["status"] != JobStatus.done or not job.get("output"):
        raise HTTPException(400, "Video not ready yet")
    output_path = job["output"]
    assert output_path is not None
    if not output_path.exists():
        raise HTTPException(500, "Output file not found")
    return FileResponse(str(output_path), media_type="video/mp4")


@router.get("/player/{job_id}", response_class=Response)
async def get_player(job_id: str):
    """Serve the self-contained interactive learning player HTML."""
    if not store.exists(job_id):
        raise HTTPException(404, "Job not found")
    job = store.require(job_id)
    player_html = job.get("player_html")
    if not player_html:
        raise HTTPException(400, "Player not ready yet — export the video first")
    return Response(content=player_html, media_type="text/html")


@router.post("/regenerate/{job_id}")
async def regenerate_checkpoints_endpoint(job_id: str, request: RegenerateRequest):
    """Re-run AI analysis with optional user feedback. Returns updated checkpoints + learning script."""
    if not store.exists(job_id):
        raise HTTPException(404, "Job not found")
    job = store.require(job_id)
    config = job.get("config")
    if not config:
        raise HTTPException(400, "Job not configured")

    transcript = job.get("transcript", [])
    video_path = job.get("video_path")
    duration = job.get("duration", 0.0)
    video_info = job.get("video_info", "")

    def _do_regenerate():
        model = config.model
        thinking_budget = (
            EXTENDED_THINKING_BUDGET
            if config.reasoning_effort == ReasoningEffort.extended
               and model not in MODELS_WITHOUT_THINKING
            else 0
        )
        checkpoints, source_urls, cp_usage = generate_checkpoints(
            transcript=transcript,
            video_info=video_info,
            style=config.style,
            video_duration=duration,
            video_path=str(video_path),
            video_format=config.video_format,
            feedback=request.feedback,
            model=model,
            thinking_budget=thinking_budget,
        )
        transcript_text = " ".join(s.text for s in transcript)
        learning_script, ls_usage = generate_learning_script(
            transcript_text=transcript_text,
            checkpoints=checkpoints,
            video_summary=video_info,
            source_urls=source_urls,
            video_duration=duration,
            model=model,
        )
        for usage in (cp_usage, ls_usage):
            _merge_usage(job_id, usage)
        store.update(job_id,
                     checkpoints=checkpoints,
                     source_urls=source_urls,
                     learning_script=learning_script)
        return {
            "summary": video_info,
            "checkpoints": [cp.model_dump() for cp in checkpoints],
            "source_urls": source_urls,
            "learning_script": learning_script,
            "token_usage": store.require(job_id).get("token_usage") or {},
        }

    try:
        return await asyncio.to_thread(_do_regenerate)
    except Exception as e:
        logger.error("regenerate: failed: %s", e, exc_info=True)
        raise HTTPException(500, str(e)[:300] or "Regeneration failed. Please try again.")


@router.post("/regenerate-learning/{job_id}")
async def regenerate_learning_endpoint(job_id: str, request: RegenerateLearningRequest):
    """Re-run learning script generation with optional user feedback."""
    if not store.exists(job_id):
        raise HTTPException(404, "Job not found")
    job = store.require(job_id)
    transcript = job.get("transcript", [])

    def _do_regenerate():
        transcript_text = " ".join(s.text for s in transcript)
        learning_script, ls_usage = generate_learning_script(
            transcript_text=transcript_text,
            checkpoints=job.get("checkpoints", []),
            video_summary=job.get("video_info", ""),
            source_urls=job.get("source_urls", {}),
            video_duration=job.get("duration", 0.0),
            feedback=request.feedback,
        )
        _merge_usage(job_id, ls_usage)
        store.update(job_id, learning_script=learning_script)
        return {"learning_script": learning_script}

    try:
        return await asyncio.to_thread(_do_regenerate)
    except Exception as e:
        logger.error("regenerate-learning: failed: %s", e, exc_info=True)
        raise HTTPException(500, str(e)[:300] or "Learning regeneration failed. Please try again.")
