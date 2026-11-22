"""Cập nhật bảng băm NGUON (LF), rồi kiểm kê bytes thực sau cùng."""

from hashlib import sha256
import json
from pathlib import Path
import re


GOI = Path(__file__).resolve().parents[1] / "goi" / "e_ocr"
KIEM_KE = GOI / "sql/kiem_ke.json"
NGUON = GOI / "NGUON.md"


def main():
    tep_goi = sorted(p for p in GOI.rglob("*") if p.is_file() and p != KIEM_KE)
    bang_bam = []
    for tep in tep_goi:
        if tep == NGUON:
            continue
        raw = tep.read_bytes()
        # Cùng quy ước LF của NGUON; wheel và các binary luôn giữ bytes.
        if tep.suffix in {".py", ".md", ".json", ".js", ".sql", ".lock"} or tep.name == ".gitattributes":
            raw = raw.replace(b"\r\n", b"\n")
        bang_bam.append(f"{sha256(raw).hexdigest()}  {tep.relative_to(GOI).as_posix()}")
    nguon = NGUON.read_text(encoding="utf-8")
    nguon, so = re.subn(r"```text\n(?:[0-9a-f]{64}  [^\n]+\n)+```",
                        "```text\n" + "\n".join(bang_bam) + "\n```", nguon)
    if so != 1:
        raise ValueError("Cần đúng một bảng băm trong NGUON.md.")
    NGUON.write_text(nguon, encoding="utf-8", newline="\n")
    phieu = json.loads((GOI / "engine.json").read_text(encoding="utf-8"))
    kiem_ke = {"phien_ban": phieu["phien_ban"], "tep": []}
    for tep in tep_goi:
        raw = tep.read_bytes()
        kiem_ke["tep"].append({"duong_dan": tep.relative_to(GOI).as_posix(),
                               "bytes": len(raw), "sha256": sha256(raw).hexdigest()})
    KIEM_KE.write_text(json.dumps(kiem_ke, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Đã cập nhật {len(bang_bam)} băm nguồn; kiểm kê {len(tep_goi)} tệp tính sau cùng.")


if __name__ == "__main__":
    main()
