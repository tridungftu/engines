#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
PYTHON=${PYTHON:-python3}
VENV=$(mktemp -d "${TMPDIR:-/tmp}/e-ocr-clean-XXXXXXXX")
export PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1
"$PYTHON" -m venv "$VENV"
P="$VENV/bin/python"
"$P" -c 'import hashlib, pathlib, sys; assert hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest() == "a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892"' "$ROOT/docs/goi-gui-engine/sdk-2.0.0/kho_tri_thuc_sdk-2.0.0-py3-none-any.whl"
"$P" -m pip install --no-index --no-deps "$ROOT/docs/goi-gui-engine/sdk-2.0.0/kho_tri_thuc_sdk-2.0.0-py3-none-any.whl"
"$P" -m pip install --require-hashes --only-binary=:all: -r "$ROOT/e_ocr/goi/e_ocr/requirements.lock"
"$P" -m pip check
"$P" "$ROOT/e_ocr/tests/chay_demo.py" --gia
