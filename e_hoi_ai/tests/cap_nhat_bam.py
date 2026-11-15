"""Sinh băm LF nguồn rồi kiểm kê raw bytes; chạy sau mỗi thay đổi gói."""
from hashlib import sha256
import json
from pathlib import Path


def main():
    goi = Path(__file__).resolve().parents[1] / "goi" / "e_hoi_ai"
    for p in goi.rglob("*"):
        if p.is_file():
            raw = p.read_bytes()
            lf = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
            if raw != lf:
                p.write_bytes(lf)
    nguon = goi / "NGUON.md"
    dau = nguon.read_text(encoding="utf-8").split("## SHA-256 hiện hành", 1)[0]
    hang = []
    for p in sorted(goi.rglob("*")):
        if not p.is_file() or p.name == "NGUON.md" or p.relative_to(goi).as_posix() == "sql/kiem_ke.json":
            continue
        hang.append(f"{sha256(p.read_bytes()).hexdigest()}  {p.relative_to(goi).as_posix()}")
    nguon.write_text(dau + "## SHA-256 hiện hành\n\n```text\n" + "\n".join(hang) + "\n```\n",
                     encoding="utf-8", newline="\n")
    kk = {"phien_ban": json.loads((goi / "engine.json").read_text(encoding="utf-8"))["phien_ban"], "tep": []}
    for p in sorted(goi.rglob("*")):
        if not p.is_file() or p.relative_to(goi).as_posix() == "sql/kiem_ke.json":
            continue
        raw = p.read_bytes()
        kk["tep"].append({"duong_dan": p.relative_to(goi).as_posix(), "bytes": len(raw), "sha256": sha256(raw).hexdigest()})
    (goi / "sql/kiem_ke.json").write_text(json.dumps(kk, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"[ĐẠT] Đã cập nhật băm LF và kiểm kê {len(kk['tep'])} tệp gói.")


if __name__ == "__main__":
    main()
