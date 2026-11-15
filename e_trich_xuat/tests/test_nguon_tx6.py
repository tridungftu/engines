"""Mọi SHA trong sổ nguồn phải khớp; mã nguồn văn bản CRLF->LF, nhị phân nguyên bytes."""
import hashlib
from pathlib import Path
import re


def test_cac_bam_trong_nguon_khop_tai_nguyen_thuc():
    goc = Path(__file__).resolve().parents[2]
    goi = goc / "e_trich_xuat/goi/e_trich_xuat"
    s = (goi / "NGUON.md").read_text(encoding="utf-8")
    ds = re.findall(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \|$", s, re.M)
    assert len(ds) >= 70
    for ten, b in ds:
        o_repo = goc / ten
        p = o_repo if ten.startswith(("_chung/", "e_trich_xuat/", "e_hoi_ai/", "docs/goi-gui-engine/")) and o_repo.is_file() else goi / ten
        raw = p.read_bytes()
        if p.suffix.lower() not in (".docx", ".xlsx", ".whl"):
            raw = raw.replace(b"\r\n", b"\n")
        assert hashlib.sha256(raw).hexdigest() == b, ten
