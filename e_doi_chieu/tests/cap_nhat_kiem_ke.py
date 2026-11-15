"""Cập nhật băm LF và kiểm kê bytes gói; chỉ chạy khi chủ động sửa gói."""
import hashlib
import json
from pathlib import Path


GOI = Path(__file__).resolve().parents[1] / "goi/e_doi_chieu"


def cap_nhat():
    for p in GOI.rglob("*"):
        if p.is_file() and (p.suffix in {".py", ".json", ".md", ".lock", ".sql"}
                            or p.name == ".gitattributes"):
            raw = p.read_bytes().replace(b"\r\n", b"\n")
            p.write_bytes(raw)
    nguon = GOI / "NGUON.md"
    text = nguon.read_text(encoding="utf-8")
    dau, cuoi = "<!-- DC-S22-SHA:DAU -->", "<!-- DC-S22-SHA:CUOI -->"
    rows = []
    for p in sorted(GOI.rglob("*")):
        if p.is_file() and p != nguon and p != GOI / "sql/kiem_ke.json":
            raw = p.read_bytes()
            rows.append(f"| `{p.relative_to(GOI).as_posix()}` | `{hashlib.sha256(raw).hexdigest()}` |")
    block = dau + "\n| Tệp hiện hành | SHA-256 LF |\n|---|---|\n" + "\n".join(rows) + "\n" + cuoi
    if dau not in text or cuoi not in text:
        raise ValueError("Thiếu vùng băm DC-S22 trong NGUON.md.")
    text = text[:text.index(dau)] + block + text[text.index(cuoi) + len(cuoi):]
    nguon.write_text(text, encoding="utf-8", newline="\n")
    files = []
    for p in sorted(GOI.rglob("*")):
        if p.is_file() and p != GOI / "sql/kiem_ke.json":
            raw = p.read_bytes()
            files.append({"duong_dan": p.relative_to(GOI).as_posix(), "bytes": len(raw),
                          "sha256": hashlib.sha256(raw).hexdigest()})
    manifest = json.loads((GOI / "engine.json").read_text(encoding="utf-8"))
    (GOI / "sql/kiem_ke.json").write_text(
        json.dumps({"phien_ban": manifest["phien_ban"], "tep": files}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"Đã kiểm kê {len(files)} tệp, bytes và SHA-256 thực; nguồn chuẩn LF.")


if __name__ == "__main__":
    cap_nhat()
