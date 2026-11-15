#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
TMP_VENV=$(mktemp -d "${TMPDIR:-/tmp}/ktt-ai5-XXXXXX")
trap 'rm -rf -- "$TMP_VENV"' EXIT HUP INT TERM
export PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1 PIP_DISABLE_PIP_VERSION_CHECK=1
"${PYTHON:-python3}" -m venv "$TMP_VENV/venv"
if [ -x "$TMP_VENV/venv/bin/python" ]; then
    PY="$TMP_VENV/venv/bin/python"
else
    PY="$TMP_VENV/venv/Scripts/python.exe"
fi
"$PY" -m pip install --no-index --no-deps "$ROOT/docs/goi-gui-engine/sdk-2.0.0/kho_tri_thuc_sdk-2.0.0-py3-none-any.whl"
"$PY" -m pip install --no-index --no-deps -r "$ROOT/e_hoi_ai/goi/e_hoi_ai/requirements.lock"
"$PY" "$ROOT/e_hoi_ai/tests/chay_demo_voi_local_gia.py"
