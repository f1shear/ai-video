import json
import logging
from infrastructure.frames import extract_frames
from infrastructure.transcriber import transcribe, get_video_duration
from prompts.understand import UNDERSTAND_SYSTEM, build_questions_prompt, build_refine_prompt
from ._llm import make_client, strip_fences, get_response_text, tally, LLM_MODEL

logger = logging.getLogger("checkpoint_overlay")


def generate_understanding(video_path: str) -> tuple[list, float, str, list[dict], dict]:
    """
    Transcribe + extract frames → understand the video → generate questions.
    Returns (transcript_segments, duration, video_info, questions, usage).
    """
    client = make_client()
    usage: dict = {}

    duration = get_video_duration(video_path)
    segments = transcribe(video_path)
    transcript_text = " ".join(s.text for s in segments)

    n_frames = min(20, max(4, int(duration / 5)))
    frames = extract_frames(video_path, n_frames=n_frames, max_width=480)
    logger.info("understand: %.0fs video, %d segments, %d frames", duration, len(segments), len(frames))

    content: list = []
    if frames:
        content.append({"type": "text", "text": f"Here are {len(frames)} frames sampled from the video:"})
        for frame in frames:
            content.append({"type": "image", "source": {
                "type": "base64", "media_type": "image/jpeg", "data": frame["data"],
            }})
            content.append({"type": "text", "text": f"^ Frame at {frame['timestamp']:.1f}s"})
    content.append({"type": "text",
                    "text": f"Video duration: {duration:.0f}s\n\nFull transcript:\n{transcript_text}"})

    response = client.messages.create(
        model=LLM_MODEL,
        max_tokens=1200,
        system=UNDERSTAND_SYSTEM,
        messages=[{"role": "user", "content": content}],
    )
    tally(usage, response)
    video_info = get_response_text(response)
    logger.info("understand: video_info generated (%d chars)", len(video_info))

    questions, q_usage = _generate_questions(client, video_info)
    tally_merge(usage, q_usage)
    return segments, duration, video_info, questions, usage


def tally_merge(acc: dict, other: dict) -> None:
    acc["input_tokens"] = acc.get("input_tokens", 0) + other.get("input_tokens", 0)
    acc["output_tokens"] = acc.get("output_tokens", 0) + other.get("output_tokens", 0)
    acc["cost_usd"] = acc.get("cost_usd", 0.0) + other.get("cost_usd", 0.0)
    acc["models"] = list(dict.fromkeys(acc.get("models", []) + other.get("models", [])))


def _generate_questions(client, video_info: str) -> tuple[list[dict], dict]:
    usage: dict = {}
    try:
        response = client.messages.create(
            model=LLM_MODEL,
            max_tokens=600,
            messages=[{"role": "user", "content": build_questions_prompt(video_info)}],
        )
        tally(usage, response)
        raw = strip_fences(get_response_text(response))
        questions = json.loads(raw)
        if not isinstance(questions, list):
            raise ValueError("not a list")
        for i, q in enumerate(questions):
            q.setdefault("id", f"q{i + 1}")
        logger.info("understand: generated %d questions", len(questions))
        return questions[:5], usage
    except Exception as e:
        logger.warning("understand: question generation failed: %s", e)
        return [], usage


def refine_understanding(video_info: str, answers: list[dict]) -> tuple[str, dict]:
    """Refine video_info based on user answers. Returns (refined_video_info, usage)."""
    answered = [a for a in answers if str(a.get("answer", "")).strip()]
    if not answered:
        return video_info, {}

    client = make_client()
    usage: dict = {}
    response = client.messages.create(
        model=LLM_MODEL,
        max_tokens=1200,
        messages=[{"role": "user", "content": build_refine_prompt(video_info, answered)}],
    )
    tally(usage, response)
    refined = get_response_text(response)
    logger.info("understand: refined video_info (%d → %d chars)", len(video_info), len(refined))
    return refined, usage
