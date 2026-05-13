import tempfile
from pathlib import Path

UPLOAD_DIR = Path(tempfile.gettempdir()) / "checkpoint_overlay"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
