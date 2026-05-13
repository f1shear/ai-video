"""
Detect scene cuts in a video using FFmpeg's scene-change filter.
Used to snap chapter/transition checkpoints to actual cut points.
"""
import logging
import re
import subprocess

logger = logging.getLogger("checkpoint_overlay")


def detect_scene_cuts(video_path: str, threshold: float = 0.35) -> list[float]:
    """
    Return a sorted list of timestamps (seconds) where hard scene cuts occur.
    Falls back to [] on any error — callers treat this as non-fatal.
    threshold: 0.0–1.0; lower = more sensitive.
    """
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-i", video_path,
                "-filter:v", f"select=gt(scene\\,{threshold}),showinfo",
                "-an", "-f", "null", "/dev/null",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        cuts: list[float] = []
        for line in (result.stdout + result.stderr).splitlines():
            m = re.search(r"pts_time:([\d.]+)", line)
            if m:
                t = float(m.group(1))
                if t > 0.5:  # skip the very first frame
                    cuts.append(t)
        cuts = sorted(set(round(t, 2) for t in cuts))
        logger.info("scene_cuts: found %d cuts (threshold=%.2f)", len(cuts), threshold)
        return cuts
    except Exception as e:
        logger.warning("scene_cuts: detection failed (non-fatal): %s", e)
        return []


def snap_to_cut(timestamp: float, cuts: list[float], window: float = 5.0) -> float:
    """
    If a scene cut falls within ±window seconds of timestamp, snap to it.
    Returns the original timestamp if no cut is close enough.
    """
    if not cuts:
        return timestamp
    nearest = min(cuts, key=lambda c: abs(c - timestamp))
    if abs(nearest - timestamp) <= window:
        return nearest
    return timestamp
