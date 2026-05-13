import base64
import json
import logging
import os
import subprocess
import tempfile

logger = logging.getLogger("checkpoint_overlay")


def extract_frames(video_path: str, n_frames: int = 8, max_width: int = 320) -> list[dict]:
    """
    Extract n evenly-spaced frames from video as compressed JPEGs for LLM vision.
    Returns list of {"timestamp": float, "data": str (base64 JPEG)}.
    Falls back to empty list on any error so checkpoint generation still works.
    """
    try:
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", video_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = float(json.loads(result.stdout)["format"]["duration"])
    except Exception as e:
        logger.warning("extract_frames: could not get duration: %s", e)
        return []

    # Skip first/last 3% to avoid fade-in/fade-out black frames
    margin = max(0.5, duration * 0.03)
    usable = duration - 2 * margin
    if usable <= 0 or n_frames < 1:
        return []

    frames = []
    for i in range(n_frames):
        ts = margin + (usable / max(n_frames - 1, 1)) * i
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        tmp.close()
        try:
            cmd = [
                "ffmpeg", "-y",
                "-ss", f"{ts:.3f}",
                "-i", video_path,
                "-frames:v", "1",
                "-q:v", "18",           # high compression (scale 1–31; 18 ≈ small JPEG, still legible)
                "-vf", f"scale={max_width}:-2",  # -2 keeps even height for codecs
                tmp.name,
            ]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode == 0 and os.path.getsize(tmp.name) > 0:
                with open(tmp.name, "rb") as f:
                    data = base64.standard_b64encode(f.read()).decode()
                frames.append({"timestamp": round(ts, 1), "data": data})
            else:
                logger.debug("extract_frames: ffmpeg failed at %.1fs: %s", ts, r.stderr[-200:])
        except Exception as e:
            logger.warning("extract_frames: frame at %.1fs failed: %s", ts, e)
        finally:
            try:
                os.unlink(tmp.name)
            except Exception:
                pass

    logger.info("extract_frames: extracted %d/%d frames from %s", len(frames), n_frames, video_path)
    return frames
