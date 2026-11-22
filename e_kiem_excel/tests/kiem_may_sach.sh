#!/bin/sh
# Truyền thư mục wheel offline làm đối số 1; không truy cập mạng.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
BANH=${1:-"$ROOT/e_kiem_excel/goi/e_kiem_excel/wheels"}
# Đổi sang đường tuyệt đối trước khi rời repo.
BANH=$(CDPATH= cd -- "$BANH" && pwd)
WHEEL="$ROOT/docs/goi-gui-engine/sdk-2.5.0/kho_tri_thuc_sdk-2.5.0-py3-none-any.whl"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUTF8=1
unset PYTHONPATH PYTHONHOME
python3 -B -c 'import sys; assert sys.version_info >= (3, 11), "Cần Python từ 3.11 trở lên."'
python3 -B -c 'import hashlib,sys; assert hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest()=="b235b513deb557f65f5a90c81e1d81e9b51799093fdaefb3bb5c5e1e954d2b55"' "$WHEEL"
TMP_DEMO=$(mktemp -d "${TMPDIR:-/tmp}/kiem-excel-DEMO-XXXXXXXX")
# Chỉ xóa môi trường test vừa tạo, không xóa bất kỳ tệp repo nào.
trap 'rm -rf -- "$TMP_DEMO"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
python3 -B -m venv "$TMP_DEMO/venv"
PY="$TMP_DEMO/venv/bin/python"
"$PY" -I -X utf8 -B -m pip install --isolated --no-index --no-deps "$WHEEL"
"$PY" -I -X utf8 -B -m pip install --isolated --no-index --find-links "$BANH" --require-hashes --only-binary :all: --no-deps -r "$ROOT/e_kiem_excel/goi/e_kiem_excel/requirements.lock"
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
