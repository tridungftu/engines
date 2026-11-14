import hashlib
import re
from pathlib import Path


def test_sha256_nguon_khop_toan_bo_goi():
    goi = Path(__file__).resolve().parents[1] / "goi" / "e_hoi_ai"
    noi_dung = (goi / "NGUON.md").read_text(encoding="utf-8")
    bang = noi_dung.split("## SHA-256 hiện hành", 1)[1]
    hang = re.findall(r"^([0-9a-f]{64})  (.+)$", bang, re.MULTILINE)
    duong_dan = [ten for _, ten in hang]
    tap_tep = {p.relative_to(goi).as_posix() for p in goi.rglob("*")
               if p.is_file() and p.name != "NGUON.md"}
    assert len(duong_dan) == len(set(duong_dan))
    assert set(duong_dan) == tap_tep
    for ma_bam, ten in hang:
        du_lieu = (goi / ten).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        assert hashlib.sha256(du_lieu).hexdigest() == ma_bam, ten
