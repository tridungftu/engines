#!/bin/sh
set -eu
TX25_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
export PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1 PIP_DISABLE_PIP_VERSION_CHECK=1
if [ -n "${TX25_KHO_WHEEL:-${TX7_KHO_WHEEL:-}}" ]; then
    set -- --kho-wheel "${TX25_KHO_WHEEL:-$TX7_KHO_WHEEL}" "$@"
fi
exec "${PYTHON:-python3}" -B -X utf8 "$TX25_ROOT/e_trich_xuat/tests/kiem_may_sach.py" --tao-venv "$@"
# Keep the isolated venv as evidence. No engine data/configuration is written.
