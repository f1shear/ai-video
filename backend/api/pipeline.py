"""
Pipeline orchestration — runs the three processing phases in background threads.

Each run_* function is called via threading.Thread; it reads/writes job state
through the JobStore and emits SSE events via events.emit*.
Data flows explicitly through function arguments and return values —
no globals except the shared store.
"""
import asyncio
import logging
from pathlib import Path

from domain.models import ProcessConfig, JobStatus, Checkpoint, ReasoningEffort
from settings import EXTENDED_THINKING_BUDGET, MODELS_WITHOUT_THINKING
from services.understand_service import generate_understanding
from services.checkpoint_service import generate_checkpoints
from services.learning_service import generate_learning_script
from infrastructure.transcriber import transcribe, get_video_duration
from infrastructure.overlay import apply_overlays
from infrastructure.player import build_player_html
from .job_store import store
from .events import emit, emit_clarify

logger = logging.getLogger("checkpoint_overlay")


def _add_usage(job_id: str, usage: dict) -> None:
    """Merge token usage from one service call into the job's running total."""
    if not usage:
        return
    existing = dict(store.require(job_id).get("token_usage") or {})
    merged_models = list(dict.fromkeys(
        existing.get("models", []) + usage.get("models", [])
    ))
    store.update(job_id, token_usage={
        "input_tokens":  existing.get("input_tokens", 0)  + usage.get("input_tokens", 0),
        "output_tokens": existing.get("output_tokens", 0) + usage.get("output_tokens", 0),
        "cost_usd":      existing.get("cost_usd", 0.0)    + usage.get("cost_usd", 0.0),
        "models":        merged_models,
    })


def run_understand(job_id: str) -> None:
    """
    Understand step — transcribe + extract frames + understand video + generate questions.
    Stores transcript, duration, and video_info in job.
    Streams questions to frontend via clarify SSE queue.
    """
    logger.info("understand start: job=%s", job_id)
    job = store.require(job_id)
    video_path: Path = job["video_path"]
    try:
        emit_clarify(job_id, "transcribing", "Transcribing audio...", 20)
        segments, duration, video_info, questions, usage = generate_understanding(str(video_path))
        store.update(job_id, transcript=segments, duration=duration, video_info=video_info)
        _add_usage(job_id, usage)
        logger.info("understand: %.0fs, %d segments, %d questions", duration, len(segments), len(questions))

        emit_clarify(job_id, "ready", "Ready!", 100, questions=questions)
        asyncio.run_coroutine_threadsafe(job["queue_clarify"].put(None), job["loop"])

    except Exception as e:
        logger.error("understand error: %s", e, exc_info=True)
        emit_clarify(job_id, "failed", str(e)[:200], 0)
        asyncio.run_coroutine_threadsafe(job["queue_clarify"].put(None), job["loop"])


def run_analysis(job_id: str, config: ProcessConfig) -> None:
    """
    Analysis step (Process).
    Generates checkpoints from the stored video_info → generates learning content.
    """
    logger.info("analysis start: job=%s", job_id)
    job = store.require(job_id)
    video_path: Path = job["video_path"]
    try:
        if job.get("transcript"):
            transcript = job["transcript"]
            duration = job["duration"]
            logger.info("analysis: using cached transcript (%d segments)", len(transcript))
            emit(job_id, JobStatus.transcribing, "Using cached transcript...", 15)
        else:
            emit(job_id, JobStatus.transcribing, "Transcribing video audio...", 15)
            transcript = transcribe(str(video_path))
            duration = get_video_duration(str(video_path))
            store.update(job_id, transcript=transcript, duration=duration)
            logger.info("analysis transcribed: %.1fs, %d segments", duration, len(transcript))

        video_info = job.get("video_info", "")

        model = config.model
        thinking_budget = (
            EXTENDED_THINKING_BUDGET
            if config.reasoning_effort == ReasoningEffort.extended
               and model not in MODELS_WITHOUT_THINKING
            else 0
        )
        logger.info("analysis: model=%s thinking_budget=%d", model, thinking_budget)

        emit(job_id, JobStatus.finding_checkpoints, "Generating overlays with AI...", 50)
        checkpoints, source_urls, cp_usage = generate_checkpoints(
            transcript=transcript,
            video_info=video_info,
            style=config.style,
            video_duration=duration,
            video_path=str(video_path),
            video_format=config.video_format,
            model=model,
            thinking_budget=thinking_budget,
        )
        store.update(job_id, checkpoints=checkpoints, source_urls=source_urls)
        _add_usage(job_id, cp_usage)

        emit(job_id, JobStatus.generating_learning, "Generating interactive learning content...", 80)
        transcript_text = " ".join(s.text for s in transcript)
        learning_ok = True
        try:
            learning_script, ls_usage = generate_learning_script(
                transcript_text=transcript_text,
                checkpoints=checkpoints,
                video_summary=video_info,
                source_urls=source_urls,
                video_duration=duration,
                model=model,
            )
            store.update(job_id, learning_script=learning_script)
            _add_usage(job_id, ls_usage)
        except Exception as e:
            logger.warning("analysis: learning content failed (non-fatal): %s", e)
            store.update(job_id, learning_script={"title": "Video", "sections": [], "quiz_points": []})
            learning_ok = False

        done_msg = f"Found {len(checkpoints)} checkpoints — review them below."
        if not learning_ok:
            done_msg += " Side panel content failed to generate — use Regenerate in the Review tab."
        emit(job_id, JobStatus.checkpoints_ready, done_msg, 100)
        asyncio.run_coroutine_threadsafe(job["queue_analysis"].put(None), job["loop"])

    except Exception as e:
        logger.error("analysis error: %s", e, exc_info=True)
        store.update(job_id, error="Processing failed. Please try again.")
        emit(job_id, JobStatus.failed, "Processing failed. Please try again.", 0)
        asyncio.run_coroutine_threadsafe(job["queue_analysis"].put(None), job["loop"])


def run_export(job_id: str, checkpoints: list[Checkpoint], config: ProcessConfig) -> None:
    """
    Export step.
    Burns checkpoints onto the video via FFmpeg, then builds the interactive HTML player.
    """
    logger.info("export start: job=%s checkpoints=%d", job_id, len(checkpoints))
    job = store.require(job_id)
    video_path: Path = job["video_path"]
    try:
        emit(job_id, JobStatus.creating_overlays, "Building overlay layout...", 20,
             queue_key="queue_export")
        output_path = video_path.parent / f"{job_id}_output.mp4"

        emit(job_id, JobStatus.exporting, "Rendering final video...", 50,
             queue_key="queue_export")
        apply_overlays(
            input_path=str(video_path),
            output_path=str(output_path),
            checkpoints=checkpoints,
            style=config.style,
            font_size=config.font_size,
        )
        store.update(job_id, output=output_path)

        approved_ls = job.get("_export_learning_script") or job.get("learning_script") or {}
        player_html = build_player_html(job_id, approved_ls)
        store.update(job_id, player_html=player_html)

        emit(job_id, JobStatus.done, "Your video is ready!", 100, queue_key="queue_export")
        asyncio.run_coroutine_threadsafe(job["queue_export"].put(None), job["loop"])

    except Exception as e:
        logger.error("export error: %s", e, exc_info=True)
        err = str(e)
        user_msg = "Video export failed. Please check your video file and try again."
        if "ffmpeg" in err.lower():
            user_msg = "FFmpeg export failed. " + err[-200:]
        store.update(job_id, error=user_msg)
        emit(job_id, JobStatus.failed, user_msg, 0, queue_key="queue_export")
        asyncio.run_coroutine_threadsafe(job["queue_export"].put(None), job["loop"])
