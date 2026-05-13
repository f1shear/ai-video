import json
import logging
from domain.models import Checkpoint
from prompts.learning import build_learning_prompt
from ._llm import make_client, strip_fences, get_response_text, tally, thinking_kwargs, LLM_MODEL

logger = logging.getLogger("checkpoint_overlay")


def generate_learning_script(
    transcript_text: str,
    checkpoints: list[Checkpoint],
    video_summary: str,
    source_urls: dict[str, str],
    video_duration: float,
    feedback: str = "",
    audience: str = "adults",
    model: str = LLM_MODEL,
) -> tuple[dict, dict]:
    """Generate an interactive learning script (sections + quiz). Returns (script, usage)."""
    _client = make_client()
    usage: dict = {}

    cp_lines = []
    for cp in checkpoints:
        line = f"[{cp.timestamp:.1f}s] [{cp.role}] {cp.text}"
        if cp.sub_text:
            line += f" — {cp.sub_text}"
        if cp.layer == "chapters":
            line += " [CHAPTER]"
        cp_lines.append(line)

    urls_snippet = json.dumps(source_urls, ensure_ascii=False)[:1200]

    prompt = build_learning_prompt(
        transcript_text=transcript_text,
        cp_lines=cp_lines,
        video_summary=video_summary,
        urls_snippet=urls_snippet,
        video_duration=video_duration,
        audience=audience,
        feedback=feedback,
    )

    logger.info("learning: generating script, %d checkpoints, %.0fs video", len(checkpoints), video_duration)

    response = _client.messages.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        **thinking_kwargs(model, 0, max_tokens=4096),
    )
    tally(usage, response, model=model)

    raw = strip_fences(get_response_text(response))

    try:
        script = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error("learning: JSON parse failed: %s | raw start: %s", e, raw[:300])
        script = _fallback_script(checkpoints, video_duration, video_summary)

    _validate_and_fix(script, video_duration)
    logger.info("learning: %d sections, %d quiz points", len(script["sections"]), len(script["quiz_points"]))
    return script, usage


def _validate_and_fix(script: dict, video_duration: float) -> None:
    """Ensure sections cover the full video and quiz timestamps are plausible."""
    sections = script.get("sections", [])
    if not sections:
        script["sections"] = [_empty_section(0.0, video_duration)]
        return

    sections.sort(key=lambda s: s.get("start", 0))

    # Clamp ends, fill gaps
    for s in sections:
        s.setdefault("start", 0.0)
        s.setdefault("end", video_duration)
        s.setdefault("title", "")
        s.setdefault("summary", "")
        s.setdefault("key_facts", [])
        s.setdefault("links", [])
        s.setdefault("deep_dive", "")
        s.setdefault("summary_concise", "")
        s.setdefault("summary_detailed", "")

    sections[-1]["end"] = video_duration

    # Clamp quiz timestamps
    for qp in script.get("quiz_points", []):
        qp["timestamp"] = max(5.0, min(float(qp.get("timestamp", 10)), video_duration - 3))
        qp.setdefault("options", ["True", "False", "Maybe", "Unknown"])
        qp.setdefault("correct_index", 0)
        qp.setdefault("difficulty", "medium")
        qp.setdefault("hint", "")
        qp.setdefault("related_fact", "")
        qp.setdefault("easier_version", "")
        qp.setdefault("harder_version", "")


def _empty_section(start: float, end: float) -> dict:
    return {"start": start, "end": end, "title": "Video", "summary": "Watch and learn.",
            "key_facts": [], "deep_dive": "", "links": []}


def _fallback_script(checkpoints: list[Checkpoint], video_duration: float, summary: str) -> dict:
    return {
        "title": "Video Learning Experience",
        "sections": [_empty_section(0.0, video_duration) | {"summary": summary[:300] or "Watch and learn."}],
        "quiz_points": [],
    }
