#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
WHEEL="$ROOT/docs/goi-gui-engine/sdk-2.0.0/kho_tri_thuc_sdk-2.0.0-py3-none-any.whl"
EXPECTED=a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892
export PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH PYTHONHOME
python3 -B -c 'import hashlib,sys; assert hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest() == sys.argv[2]' "$WHEEL" "$EXPECTED"
TMP=$(mktemp -d "${TMPDIR:-/tmp}/hoa-don-DEMO-XXXXXXXX")
python3 -B -m venv "$TMP/venv"
"$TMP/venv/bin/python" -B -m pip install --no-index --no-deps "$WHEEL"
mkdir -p "$TMP/kiem/goi" "$TMP/kiem/tests"
cp -R "$ROOT/e_hoa_don/goi/e_hoa_don" "$TMP/kiem/goi/e_hoa_don"
cp "$ROOT/e_hoa_don/tests/kiem_doc_lap.py" "$TMP/kiem/tests/"
cd "$TMP/kiem"
"$TMP/venv/bin/python" -B -m kho_tri_thuc_sdk.thu goi/e_hoa_don
"$TMP/venv/bin/python" -B tests/kiem_doc_lap.py
printf 'Clean install DEMO: DAT (CoreGia)\n'
