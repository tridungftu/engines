#!/bin/sh
# Default: dry run. Add --cai only after approved wheels/hashes exist.
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
exec python3 -B "$(dirname "$0")/kiem_may_sach.py" "$@"
