"""Kiểm kê bytes nguyên trạng + SHA-256, đúng định dạng e_demo_ngan.

Tính lại sau mọi thay đổi gói (gồm demo do PL-0B bàn giao):
    python -B e_phan_luong/tests/kiem_bam_goi.py --cap-nhat
"""

import argparse
from hashlib import sha256
import json
from pathlib import Path

GOI = Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"
TEP_KIEM_KE = "sql/kiem_ke.json"


def tinh_kiem_ke(goi=GOI):
    goi = Path(goi)
    ds = []
    for tep in sorted(goi.rglob("*"), key=lambda p: p.relative_to(goi).as_posix()):
        if tep.is_symlink() or (hasattr(tep, "is_junction") and tep.is_junction()):
            raise ValueError("Gói không được chứa liên kết.")
        if tep.name == "__pycache__" or tep.suffix.lower() in {".pyc", ".pyo"}:
            raise ValueError("Gói không được chứa bytecode.")
        if not tep.is_file() or tep.relative_to(goi).as_posix() == TEP_KIEM_KE:
            continue
        raw = tep.read_bytes()
        ds.append({"duong_dan": tep.relative_to(goi).as_posix(), "bytes": len(raw),
                   "sha256": sha256(raw).hexdigest()})
    phieu = json.loads((goi / "engine.json").read_text(encoding="utf-8"))
    return {"phien_ban": phieu["phien_ban"], "tep": ds}


def cap_nhat(goi=GOI):
    kq = tinh_kiem_ke(goi)
    (Path(goi) / TEP_KIEM_KE).write_text(
        json.dumps(kq, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def kiem(goi=GOI):
    mong = json.loads((Path(goi) / TEP_KIEM_KE).read_text(encoding="utf-8"))
    if mong != tinh_kiem_ke(goi):
        raise ValueError("Kiểm kê không khớp tên tệp, bytes hoặc SHA-256 toàn gói.")
    return len(mong["tep"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cap-nhat", action="store_true")
    args = ap.parse_args()
    if args.cap_nhat:
        cap_nhat()
    print(f"Kiểm kê khớp {kiem()} tệp (trừ chính kiểm kê).")
