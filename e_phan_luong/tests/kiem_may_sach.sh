#!/bin/sh
# Linux CI Python 3.11; doi so 1 la kho wheel offline da doi chieu hash.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
BANH=${1:-"$ROOT/.venv/banh"}
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUTF8=1
export PIP_NO_INDEX=1
export PIP_DISABLE_PIP_VERSION_CHECK=1
unset PYTHONPATH PYTHONHOME
PYTHON=${PYTHON:-python3}
"$PYTHON" -B -c 'import sys; assert sys.version_info[:2] == (3, 11), "Kiem may sach yeu cau Python 3.11."'
BANH=$(CDPATH= cd -- "$BANH" && pwd)
WHEEL="$ROOT/docs/goi-gui-engine/sdk-2.2.0/kho_tri_thuc_sdk-2.2.0-py3-none-any.whl"
"$PYTHON" -B -c 'import hashlib,sys; assert hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest()=="0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984"' "$WHEEL"
TMP_DEMO=$(mktemp -d "${TMPDIR:-/tmp}/kiem-phan-luong-DEMO-XXXXXXXX")
# Giu bang chung; khong xoa tep. Thu muc nay nam ngoai goi.
trap 'echo "Moi truong kiem: $TMP_DEMO"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
"$PYTHON" -B -m venv "$TMP_DEMO/venv"
PY="$TMP_DEMO/venv/bin/python"
if [ ! -f "$PY" ]; then PY="$TMP_DEMO/venv/Scripts/python.exe"; fi
"$PY" -B -m pip install --no-index --no-deps "$WHEEL"
"$PY" -B -m pip install --no-index --find-links "$BANH" --require-hashes --no-deps -r "$ROOT/e_phan_luong/goi/e_phan_luong/requirements.lock"
mkdir -p "$TMP_DEMO/kiem/goi" "$TMP_DEMO/kiem/tests"
cp -R "$ROOT/e_phan_luong/goi/e_phan_luong" "$TMP_DEMO/kiem/goi/"
for TEP in kiem_doc_lap.py kiem_bam_goi.py test_pl9c_dong_goi.py; do
    cp "$ROOT/e_phan_luong/tests/$TEP" "$TMP_DEMO/kiem/tests/"
done
cd "$TMP_DEMO/kiem"
# Adapter goi kiem_bam_goi.kiem; dung kiem ke SQL noi goi, khong nhan ban bam thu hai.
"$PY" -B tests/test_pl9c_dong_goi.py --kiem-ke goi/e_phan_luong/sql/kiem_ke.json --phu-thuoc
"$PY" -B -m kho_tri_thuc_sdk.thu goi/e_phan_luong
"$PY" -B tests/kiem_doc_lap.py
echo '[ĐẠT] Cài sạch offline; đã kiểm bằng Core giả (CoreGia).'
