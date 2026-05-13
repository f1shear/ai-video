import logging
import os
import json
import subprocess
from typing import List
from domain.models import TranscriptSegment

logger = logging.getLogger("checkpoint_overlay")


def get_video_duration(video_path: str) -> float:
    """Use ffprobe to get video duration in seconds."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])


def _mock_transcript(video_path: str) -> List[TranscriptSegment]:
    duration = get_video_duration(video_path)
    # Generate plausible mock segments roughly every 15s
    sentences = [
        "Welcome to this video. Let me walk you through the main points.",
        "First, we'll look at the introduction and set the context.",
        "Now let's dive into the first major topic.",
        "Here is an important concept you should understand.",
        "Let me demonstrate this step by step.",
        "This is a key moment in the workflow.",
        "Pay attention to this detail — it matters later.",
        "We're now moving to the next section.",
        "Here's where things get interesting.",
        "Let me summarize what we've covered so far.",
        "Now for the final part of our journey.",
        "And that's a wrap. Thanks for watching.",
    ]
    n = max(3, min(len(sentences), int(duration / 12)))
    chunk = duration / n
    segments = []
    for i in range(n):
        start = i * chunk
        end = start + chunk * 0.9
        segments.append(TranscriptSegment(
            start=round(start, 2),
            end=round(end, 2),
            text=sentences[i % len(sentences)]
        ))
    return segments


def _whisper_transcript(video_path: str) -> List[TranscriptSegment]:
    import whisper  # type: ignore
    audio_path = video_path.rsplit(".", 1)[0] + "_audio.wav"
    subprocess.run([
        "ffmpeg", "-y", "-i", video_path,
        "-ac", "1", "-ar", "16000",
        "-vn", audio_path
    ], check=True, capture_output=True)

    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, fp16=False)
    finally:
        if os.path.exists(audio_path):
            os.unlink(audio_path)

    segments = []
    for seg in result.get("segments", []):
        segments.append(TranscriptSegment(
            start=round(seg["start"], 2),
            end=round(seg["end"], 2),
            text=seg["text"].strip()
        ))
    return segments


def transcribe(video_path: str) -> List[TranscriptSegment]:
    use_mock = os.getenv("USE_MOCK_TRANSCRIPTION", "false").lower() == "true"
    if use_mock:
        return _mock_transcript(video_path)
    try:
        return _whisper_transcript(video_path)
    except ImportError:
        # whisper not installed — fall back gracefully so local dev still works
        logger.warning("whisper not installed; using mock transcript. Set USE_MOCK_TRANSCRIPTION=true to suppress this warning.")
        return _mock_transcript(video_path)
    # All other exceptions (ffmpeg failure, file error, etc.) propagate —
    # the caller must surface them rather than silently fabricate data.
