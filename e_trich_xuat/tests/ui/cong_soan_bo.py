"""Cầu kiểm offline: Node KttCore giả gọi đúng hàm Python bằng stdin JSON."""
import json
from pathlib import Path
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "goi/e_trich_xuat"))
from e_trich_xuat.soan_bo import ham_thao_tac

if __name__ == "__main__":
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(ham_thao_tac(SimpleNamespace(dau_vao=json.load(sys.stdin))), ensure_ascii=False))
