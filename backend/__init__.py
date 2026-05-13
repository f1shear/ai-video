import sys
import os

# When imported as a package (e.g., from backend.api.routes import router),
# add the backend directory to sys.path so that absolute imports like
# "from domain.models import ..." resolve correctly.
_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
