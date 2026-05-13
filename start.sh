#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

# ── virtualenv ─────────────────────────────────────────────────────────────
if [ ! -d "$ROOT/.venv" ]; then
  echo "→ Creating Python virtualenv..."
  python3 -m venv "$ROOT/.venv"
fi

echo "→ Installing/updating backend dependencies..."
"$ROOT/.venv/bin/pip" install -q -r "$ROOT/backend/requirements.txt"

# ── env file ───────────────────────────────────────────────────────────────
if [ ! -f "$ROOT/backend/.env" ]; then
  cp "$ROOT/backend/.env.example" "$ROOT/backend/.env"
  echo "→ Created backend/.env from .env.example"
  echo "  Add your ANTHROPIC_API_KEY there to enable real checkpoint generation."
  echo "  Without it the app uses mock checkpoints (still works end-to-end)."
fi

# ── frontend deps ──────────────────────────────────────────────────────────
if [ ! -d "$ROOT/frontend/node_modules" ]; then
  echo "→ Installing frontend dependencies..."
  cd "$ROOT/frontend" && npm install --silent
  cd "$ROOT"
fi

# ── launch both servers ────────────────────────────────────────────────────
echo ""
echo "Starting backend  →  http://localhost:8000"
echo "Starting frontend →  http://localhost:5173"
echo "Press Ctrl-C to stop both."
echo ""

# Backend
cd "$ROOT/backend"
"$ROOT/.venv/bin/uvicorn" main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Frontend
cd "$ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

# Wait and kill both on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait $BACKEND_PID $FRONTEND_PID
