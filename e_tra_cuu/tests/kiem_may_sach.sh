#!/bin/sh
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
export PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1 PIP_NO_INDEX=1 PIP_DISABLE_PIP_VERSION_CHECK=1
exec "${TC10_PYTHON:-python3}" -B "$SCRIPT_DIR/kiem_may_sach.py" "$@"
