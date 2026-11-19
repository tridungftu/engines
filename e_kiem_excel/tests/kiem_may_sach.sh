#!/bin/sh
# Truyền thư mục wheel offline làm đối số 1; không truy cập mạng.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
BANH=${1:-"$ROOT/.venv/banh"}
# Đổi sang đường tuyệt đối trước khi rời repo.
BANH=$(CDPATH= cd -- "$BANH" && pwd)
WHEEL="$ROOT/docs/goi-gui-engine/sdk-2.2.0/kho_tri_thuc_sdk-2.2.0-py3-none-any.whl"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUTF8=1
unset PYTHONPATH PYTHONHOME
python3 -B -c 'import sys; assert sys.version_info[:2] == (3, 11), "Kiểm Linux CI yêu cầu Python 3.11."'
python3 -B -c 'import hashlib,sys; assert hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest()=="0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984"' "$WHEEL"
TMP_DEMO=$(mktemp -d "${TMPDIR:-/tmp}/kiem-excel-DEMO-XXXXXXXX")
# Chỉ xóa môi trường test vừa tạo, không xóa bất kỳ tệp repo nào.
trap 'rm -rf -- "$TMP_DEMO"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
python3 -B -m venv "$TMP_DEMO/venv"
PY="$TMP_DEMO/venv/bin/python"
"$PY" -B -m pip install --no-index --no-deps "$WHEEL"
"$PY" -B -m pip install --no-index --find-links "$BANH" --require-hashes --no-deps -r "$ROOT/e_kiem_excel/goi/e_kiem_excel/requirements.lock"
mkdir -p "$TMP_DEMO/kiem/goi" "$TMP_DEMO/kiem/tests"
cp -R "$ROOT/e_kiem_excel/goi/e_kiem_excel" "$TMP_DEMO/kiem/goi/"
cp "$ROOT/e_kiem_excel/tests/kiem_doc_lap.py" "$TMP_DEMO/kiem/tests/"
cp "$ROOT/e_kiem_excel/tests/kiem_bam_goi.py" "$TMP_DEMO/kiem/tests/"
cp "$ROOT/e_kiem_excel/tests/demo/bam-goi.json" "$TMP_DEMO/kiem/tests/"
cd "$TMP_DEMO/kiem"
"$PY" -B tests/kiem_bam_goi.py --kiem-ke tests/bam-goi.json --goi goi/e_kiem_excel --phu-thuoc
"$PY" -B -m kho_tri_thuc_sdk.thu goi/e_kiem_excel
"$PY" -B tests/kiem_doc_lap.py
echo '[ĐẠT] Cài sạch offline; đã kiểm bằng Core giả (CoreGia): 5/5 DEMO.'
