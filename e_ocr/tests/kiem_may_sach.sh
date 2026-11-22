#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
PYTHON=${PYTHON:-python3}
export PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1
"$PYTHON" -B -X utf8 "$ROOT/e_ocr/tests/kiem_may_sach.py"
