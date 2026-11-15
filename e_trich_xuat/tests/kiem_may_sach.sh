#!/bin/sh
set -eu
TX6_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
TX6_TMP=$(mktemp -d "${TMPDIR:-/tmp}/tx6-sach-XXXXXX")
export PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1 PIP_DISABLE_PIP_VERSION_CHECK=1
"${PYTHON:-python3}" -B -m venv "$TX6_TMP/venv"
TX6_PY="$TX6_TMP/venv/bin/python"
"$TX6_PY" -B -m pip install --no-compile --no-index --no-deps "$TX6_ROOT/docs/goi-gui-engine/sdk-2.2.0/kho_tri_thuc_sdk-2.2.0-py3-none-any.whl"
"$TX6_PY" -B -m pip install --no-compile --no-index --no-deps --find-links "${TX7_KHO_WHEEL:?Can kho wheel phu thuoc da ghim}" -r "$TX6_ROOT/e_trich_xuat/goi/e_trich_xuat/requirements.lock"
"$TX6_PY" -B "$TX6_ROOT/e_trich_xuat/tests/kiem_may_sach.py" "$@"
# Keep the isolated venv as evidence. No engine data/configuration is written.
