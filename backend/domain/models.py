from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from settings import LLM_MODEL


class VideoFormat(str, Enum):
    vertical = "vertical"
    horizontal = "horizontal"
    square = "square"


class Style(str, Enum):
    clean = "clean"
    cinematic = "cinematic"
    bold = "bold"
    minimal = "minimal"


class FontSize(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"


class OverlayPosition(str, Enum):
    top_left = "top_left"
    top_center = "top_center"
    top_right = "top_right"
    bottom_left = "bottom_left"
    bottom_center = "bottom_center"
    bottom_right = "bottom_right"
    center = "center"  # type: ignore[assignment]  # shadows str.center method


class OverlayRole(str, Enum):
    label = "label"          # names a subject, place, person
    fact = "fact"            # verifiable data — date, stat, record
    chapter = "chapter"      # section divider / narrative boundary
    annotation = "annotation"  # supplementary context or clarification
    cta = "cta"              # call to action


class OverlayTemplate(str, Enum):
    corner_badge = "corner_badge"          # small rounded rect, edge-anchored
    lower_third = "lower_third"            # full-width gradient bar at bottom
    chyron = "chyron"                      # thin full-width subtitle band
    cinematic_title = "cinematic_title"    # centred pill + horizontal rules
    pill = "pill"                          # compact centred outlined pill


class Importance(str, Enum):
    must = "must"      # critical — viewer confused without it
    should = "should"  # important context
    could = "could"    # nice to have
    would = "would"    # bonus detail


# Default position per video format
FORMAT_DEFAULT_POSITION: dict = {
    VideoFormat.vertical: OverlayPosition.top_left,
    VideoFormat.horizontal: OverlayPosition.bottom_left,
    VideoFormat.square: OverlayPosition.top_left,
}

# Default template per role
ROLE_TEMPLATE: dict = {
    OverlayRole.label:      OverlayTemplate.corner_badge,
    OverlayRole.fact:       OverlayTemplate.corner_badge,
    OverlayRole.chapter:    OverlayTemplate.cinematic_title,
    OverlayRole.annotation: OverlayTemplate.corner_badge,
    OverlayRole.cta:        OverlayTemplate.lower_third,
}

# Layer name per role (default: "content")
ROLE_LAYER: dict = {
    OverlayRole.chapter: "chapters",
}


class TranscriptSegment(BaseModel):
    start: float
    end: float
    text: str


class CheckpointAlternative(BaseModel):
    text: str
    sub_text: Optional[str] = None
    role: OverlayRole = OverlayRole.label
    template: OverlayTemplate = OverlayTemplate.corner_badge
    confidence: float = 0.7
    rationale: Optional[str] = None


class Checkpoint(BaseModel):
    timestamp: float
    duration: float
    text: str
    sub_text: Optional[str] = None
    position: OverlayPosition = OverlayPosition.bottom_left
    rationale: Optional[str] = None
    importance: Importance = Importance.should
    role: OverlayRole = OverlayRole.label
    template: OverlayTemplate = OverlayTemplate.corner_badge
    layer: str = "content"          # "content" | "subtitles" | "chapters"
    source_url: Optional[str] = None
    confidence: float = 0.8
    alternatives: List[CheckpointAlternative] = []


class ReasoningEffort(str, Enum):
    standard = "standard"
    extended = "extended"


class ProcessConfig(BaseModel):
    video_format: VideoFormat
    style: Style
    font_size: FontSize = FontSize.medium
    model: str = LLM_MODEL
    reasoning_effort: ReasoningEffort = ReasoningEffort.standard


class JobStatus(str, Enum):
    queued = "queued"
    transcribing = "transcribing"
    finding_checkpoints = "finding_checkpoints"
    generating_learning = "generating_learning"
    checkpoints_ready = "checkpoints_ready"
    creating_overlays = "creating_overlays"
    exporting = "exporting"
    done = "done"
    failed = "failed"


class ProgressEvent(BaseModel):
    status: JobStatus
    message: str
    progress: int
