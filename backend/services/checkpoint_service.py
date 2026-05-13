import json
import logging
import os
import re
from typing import List

from domain.models import (
    Checkpoint, CheckpointAlternative, FORMAT_DEFAULT_POSITION, Importance,
    OverlayPosition, OverlayRole, OverlayTemplate,
    ROLE_LAYER, ROLE_TEMPLATE,
    Style, VideoFormat,
)
from infrastructure.enricher import enrich_from_video_info
from infrastructure.frames import extract_frames
from infrastructure.scene_cuts import detect_scene_cuts, snap_to_cut
from prompts.checkpoints import (
    STYLE_NOTES, ANNOTATION_GUIDANCE,
    CHECKPOINT_INTERVAL, _DURATION_CAPS, MOCK_CHECKPOINTS,
)
from services._llm import make_client, get_response_text, tally, thinking_kwargs, LLM_MODEL

logger = logging.getLogger("checkpoint_overlay")

POSITION_VALUES = [p.value for p in OverlayPosition]
ROLE_VALUES = [r.value for r in OverlayRole]
TEMPLATE_VALUES = [t.value for t in OverlayTemplate]


def smart_duration(text: str, sub_text: str | None, role: OverlayRole) -> float:
    words = len(text.split()) + (len(sub_text.split()) * 0.5 if sub_text else 0)
    base = words * 0.30 + 1.0
    lo, hi = _DURATION_CAPS.get(role, (2.0, 8.0))
    return round(max(lo, min(base, hi)), 1)


def _evenly_spaced(
    video_duration: float,
    items: list,
    default_position: OverlayPosition = OverlayPosition.top_left,
) -> List[Checkpoint]:
    if not items:
        return []
    n = min(len(items), max(2, int(video_duration / CHECKPOINT_INTERVAL)))
    items = items[:n]
    gap = video_duration / (n + 1)
    checkpoints = []
    for i, (text, sub, role) in enumerate(items):
        ts = round(gap * (i + 1), 1)
        ts = min(ts, video_duration * 0.9)
        template = ROLE_TEMPLATE.get(role, OverlayTemplate.corner_badge)
        layer = ROLE_LAYER.get(role, "content")
        pos = OverlayPosition.center if role == OverlayRole.chapter else default_position
        checkpoints.append(Checkpoint(
            timestamp=ts,
            duration=smart_duration(text, sub, role),
            text=text,
            sub_text=sub,
            position=pos,
            rationale=None,
            importance=Importance.should,
            role=role,
            template=template,
            layer=layer,
            source_url=None,
        ))
    return checkpoints


def _mock_checkpoints(
    video_duration: float,
    default_position: OverlayPosition = OverlayPosition.top_left,
) -> tuple[List[Checkpoint], dict, dict]:
    return _evenly_spaced(video_duration, MOCK_CHECKPOINTS, default_position), {}, {}


def _claude_checkpoints(
    transcript: list,
    video_info: str,
    style: Style,
    video_duration: float,
    video_path: str,
    default_position: OverlayPosition = OverlayPosition.top_left,
    feedback: str = "",
    model: str = LLM_MODEL,
    thinking_budget: int = 0,
) -> tuple[List[Checkpoint], dict, dict]:
    client = make_client()

    transcript_text = "\n".join(
        f"[{seg.start:.1f}s - {seg.end:.1f}s] {seg.text}"
        for seg in transcript
    )

    enrichment_context = ""
    source_urls: dict[str, str] = {}
    try:
        enrichment_context, source_urls = enrich_from_video_info(video_info)
        logger.info("enrichment: %d chars, %d source URLs", len(enrichment_context), len(source_urls))
    except Exception as e:
        logger.warning("enrichment failed (non-fatal): %s", e)

    scene_cuts: list[float] = []
    try:
        scene_cuts = detect_scene_cuts(video_path)
    except Exception as e:
        logger.warning("scene cut detection failed (non-fatal): %s", e)

    n_frames = min(24, max(4, int(video_duration / 5)))
    frames = extract_frames(video_path, n_frames=n_frames, max_width=480)
    logger.info(
        "checkpoint LLM: style=%s dur=%.1fs frames=%d enrichment=%d cuts=%d",
        style, video_duration, len(frames), len(enrichment_context), len(scene_cuts),
    )

    style_note = STYLE_NOTES.get(style.value, STYLE_NOTES['clean'])
    system = f"""You are placing text overlay annotations on a video. A previous analysis has already understood this video in detail — it is your primary source of truth:

{video_info}

Style: {style_note}

{ANNOTATION_GUIDANCE}

POSITIONING
Look at the frames. Before deciding where to place each overlay, notice where faces, key subjects, and on-screen text are. Place annotations in clear areas — corners, edges, or regions with neutral backgrounds. Be consistent within a continuous scene.

WHAT TO ANNOTATE
Work through the timeline and ask: what is actually happening or being discussed here, and what would a curious viewer want to know?
- A named place, person, or object appears → identify it specifically
- A date, number, or notable fact is mentioned → surface it
- The topic or scene clearly shifts → use a chapter marker
- Something surprising or illuminating can be said → say it
- Nothing specific to say → skip the moment

Aim for roughly one annotation per {CHECKPOINT_INTERVAL}s of interesting content, but let the material set the pace.

FIELD GUIDE
text: max 6 words — the specific thing being annotated
sub_text: max 8 words — a fact that adds new information (null if nothing genuinely useful)
role: label | fact | chapter | annotation | cta
  label — names a subject, place, or person
  fact — a verifiable date, statistic, or record
  chapter — clear topic or scene boundary (always position "center", template "cinematic_title")
  annotation — context that doesn't fit label/fact
  cta — call to action
template: corner_badge | lower_third | chyron | cinematic_title | pill
  corner_badge — default compact badge
  lower_third — wider bar for introductions
  chyron — thin full-width strip
  cinematic_title — centred pill for chapters
  pill — compact centred note
position: {' | '.join(POSITION_VALUES)}
importance: must | should | could | would
confidence: 0.9–1.0 = verified fact; 0.7–0.9 = well-supported; <0.7 = uncertain

Return ONLY valid JSON — no prose, no markdown fences:
{{
  "checkpoints": [
    {{
      "timestamp": <seconds 0–{video_duration:.1f}>,
      "text": "<specific label>",
      "sub_text": "<supporting fact or null>",
      "role": "<role>",
      "template": "<template>",
      "position": "<position>",
      "importance": "<importance>",
      "rationale": "<one sentence: why this moment, why this wording>",
      "confidence": <0.0–1.0>,
      "alternatives": [
        {{
          "text": "<different angle on same moment>",
          "sub_text": "<or null>",
          "role": "<role>",
          "template": "<template>",
          "confidence": <0.0–1.0>,
          "rationale": "<why this alternative>"
        }}
      ]
    }}
  ]
}}

Provide 2 alternatives per checkpoint, each with a genuinely different framing or emphasis.
duration is computed automatically — do not include it.
"""

    if feedback:
        system += f"\n\nFEEDBACK FROM PREVIOUS RUN — apply this to improve your output:\n{feedback}"

    content: list = []
    if frames:
        content.append({"type": "text",
                        "text": f"Here are {len(frames)} frames sampled evenly from the video:"})
        for frame in frames:
            content.append({"type": "image", "source": {
                "type": "base64", "media_type": "image/jpeg", "data": frame["data"],
            }})
            content.append({"type": "text", "text": f"^ Frame at {frame['timestamp']:.1f}s"})

    if enrichment_context:
        content.append({"type": "text", "text": enrichment_context})

    content.append({"type": "text",
                    "text": f"Full audio transcript:\n{transcript_text}\n\nReturn the JSON:"})

    usage: dict = {}
    response = client.messages.create(
        model=model,
        system=system,
        messages=[{"role": "user", "content": content}],
        **thinking_kwargs(model, thinking_budget, max_tokens=5000),
    )
    tally(usage, response, model=model)

    raw = get_response_text(response)
    logger.info("LLM raw (first 500): %s", raw[:500])

    data = None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        for pattern in [r'```(?:json)?\s*(\{.*?\})\s*```', r'(\{[\s\S]*\})']:
            m = re.search(pattern, raw, re.DOTALL)
            if m:
                try:
                    data = json.loads(m.group(1))
                    break
                except json.JSONDecodeError:
                    continue

    if data is None:
        raise ValueError(f"Could not parse JSON from LLM response: {raw[:300]}")

    raw_items = data.get("checkpoints", data) if isinstance(data, dict) else data

    url_lookup = {k.lower(): v for k, v in source_urls.items()}

    checkpoints: List[Checkpoint] = []
    for item in raw_items:
        try:
            try:
                ts = float(item.get("timestamp", 0))
            except (TypeError, ValueError):
                ts = 0.0

            text = str(item.get("text", "")).strip()
            sub = item.get("sub_text")
            if sub:
                sub = str(sub).strip() or None

            try:
                role = OverlayRole(item.get("role", "label"))
            except ValueError:
                role = OverlayRole.label

            try:
                template = OverlayTemplate(item.get("template", ROLE_TEMPLATE.get(role, OverlayTemplate.corner_badge).value))
            except ValueError:
                template = ROLE_TEMPLATE.get(role, OverlayTemplate.corner_badge)

            pos_val = item.get("position", default_position.value)
            try:
                pos = OverlayPosition(pos_val)
            except ValueError:
                pos = default_position

            if role == OverlayRole.chapter:
                pos = OverlayPosition.center
                ts = snap_to_cut(ts, scene_cuts, window=5.0)
                template = OverlayTemplate.cinematic_title

            try:
                importance = Importance(item.get("importance", "should"))
            except ValueError:
                importance = Importance.should

            rationale = str(item.get("rationale", "")).strip() or None
            layer = ROLE_LAYER.get(role, "content")
            try:
                confidence = max(0.0, min(1.0, float(item.get("confidence", 0.8))))
            except (TypeError, ValueError):
                confidence = 0.8

            alternatives: list[CheckpointAlternative] = []
            for alt in item.get("alternatives", [])[:3]:
                try:
                    alt_role = OverlayRole(alt.get("role", "label"))
                except ValueError:
                    alt_role = OverlayRole.label
                try:
                    alt_template = OverlayTemplate(alt.get("template", ROLE_TEMPLATE.get(alt_role, OverlayTemplate.corner_badge).value))
                except ValueError:
                    alt_template = OverlayTemplate.corner_badge
                alt_sub = alt.get("sub_text")
                if alt_sub:
                    alt_sub = str(alt_sub).strip() or None
                try:
                    alt_conf = max(0.0, min(1.0, float(alt.get("confidence", 0.7))))
                except (TypeError, ValueError):
                    alt_conf = 0.7
                alternatives.append(CheckpointAlternative(
                    text=str(alt.get("text", "")).strip(),
                    sub_text=alt_sub,
                    role=alt_role,
                    template=alt_template,
                    confidence=alt_conf,
                    rationale=str(alt.get("rationale", "")).strip() or None,
                ))

            source_url: str | None = None
            text_lower = text.lower()
            for place_lower, url in url_lookup.items():
                if place_lower in text_lower or text_lower in place_lower:
                    source_url = url
                    break

            if text and 0 <= ts < video_duration:
                dur = smart_duration(text, sub, role)
                checkpoints.append(Checkpoint(
                    timestamp=round(ts, 2),
                    duration=dur,
                    text=text,
                    sub_text=sub,
                    position=pos,
                    rationale=rationale,
                    importance=importance,
                    role=role,
                    template=template,
                    layer=layer,
                    source_url=source_url,
                    confidence=confidence,
                    alternatives=alternatives,
                ))
        except Exception as exc:
            logger.warning("skipping malformed checkpoint item: %s — %s", item, exc)

    checkpoints.sort(key=lambda c: c.timestamp)
    logger.info("generated %d checkpoints, %d source URLs", len(checkpoints), len(source_urls))
    return checkpoints, source_urls, usage


def generate_checkpoints(
    transcript: list,
    video_info: str,
    style: Style,
    video_duration: float,
    video_path: str = "",
    video_format: VideoFormat = VideoFormat.horizontal,
    feedback: str = "",
    model: str = LLM_MODEL,
    thinking_budget: int = 0,
) -> tuple[List[Checkpoint], dict, dict]:
    """Returns (checkpoints, source_urls, usage)."""
    default_position = FORMAT_DEFAULT_POSITION.get(video_format, OverlayPosition.bottom_left)
    use_mock = os.getenv("USE_MOCK_CHECKPOINTS", "false").lower() == "true"
    has_key = bool(os.getenv("ANTHROPIC_API_KEY"))

    if use_mock or not has_key:
        logger.info("using mock checkpoints (mock=%s has_key=%s)", use_mock, has_key)
        return _mock_checkpoints(video_duration, default_position)

    return _claude_checkpoints(
        transcript, video_info, style, video_duration, video_path, default_position,
        feedback=feedback, model=model, thinking_budget=thinking_budget,
    )
