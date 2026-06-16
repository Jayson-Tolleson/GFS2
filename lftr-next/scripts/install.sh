#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
if command -v npm >/dev/null 2>&1; then
  (cd frontend && npm install && npm run build)
else
  echo "npm not found; skipping frontend install/build"
fi
cat <<MSG
LFTR Next installed.
Run backend: cd $ROOT && . .venv/bin/activate && python -m app.main
Run frontend: cd $ROOT/frontend && npm run dev
Check health: $ROOT/scripts/check_health.sh
Check scene: $ROOT/scripts/check_scene_snapshot.sh
MSG
