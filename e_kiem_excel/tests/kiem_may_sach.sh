#!/bin/sh
# Truyền thư mục wheel offline làm đối số 1; không truy cập mạng.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
BANH=${1:-"$ROOT/.venv/banh"}
WHEEL="$ROOT/docs/goi-gui-engine/sdk-2.2.0/kho_tri_thuc_sdk-2.2.0-py3-none-any.whl"
export PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH PYTHONHOME
python3 -B -c 'import hashlib,sys; assert hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest()=="0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984"' "$WHEEL"
TMP_DEMO=$(mktemp -d "${TMPDIR:-/tmp}/kiem-excel-DEMO-XXXXXXXX")
python3 -B -m venv "$TMP_DEMO/venv"
PY="$TMP_DEMO/venv/bin/python"
"$PY" -B -m pip install --no-index --no-deps "$WHEEL"
"$PY" -B -m pip install --no-index --find-links "$BANH" --require-hashes --no-deps -r "$ROOT/e_kiem_excel/goi/e_kiem_excel/requirements.lock"
mkdir -p "$TMP_DEMO/kiem/goi" "$TMP_DEMO/kiem/tests"
cp -R "$ROOT/e_kiem_excel/goi/e_kiem_excel" "$TMP_DEMO/kiem/goi/"
cp "$ROOT/e_kiem_excel/tests/kiem_doc_lap.py" "$TMP_DEMO/kiem/tests/"
cd "$TMP_DEMO/kiem"
MA_CLI=0
"$PY" -B -m kho_tri_thuc_sdk.thu goi/e_kiem_excel || MA_CLI=$?
"$PY" -B tests/kiem_doc_lap.py
# EX-0 giữ nguyên mã thoát CLI; không đổi CHUA_LAM thành XONG.
exit "$MA_CLI"
