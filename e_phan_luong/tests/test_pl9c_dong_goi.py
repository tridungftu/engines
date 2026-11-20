"""Kiểm phát hành bằng bộ đóng gói chung; chỉ dùng bytes DEMO của worktree.

CLI --kiem-ke bọc kiem_bam_goi.kiem mà không đổi công cụ thuộc lát khác.
CLI --dong-goi-thu ghi ZIP thử ngoài repo; không thay thế bản phát hành từ git.
"""
from hashlib import sha256
import importlib.util
from io import BytesIO
import json
from pathlib import Path
import runpy
import sys
import zipfile

TESTS = Path(__file__).resolve().parent
GOI = TESTS.parent / "goi" / "e_phan_luong"
REPO = TESTS.parents[1]
MA = "e_phan_luong"


def bo_dong_goi():
    spec = importlib.util.spec_from_file_location(
        "dong_goi_pl9c", REPO / "_chung" / "cong-cu" / "dong_goi.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def kiem_bam_goi(tep_kiem_ke):
    tep = Path(tep_kiem_ke).resolve()
    assert tep.name == "kiem_ke.json" and tep.parent.name == "sql", "Sai tệp kiểm kê."
    cong_cu = runpy.run_path(str(TESTS / "kiem_bam_goi.py"))
    return cong_cu["kiem"](tep.parents[1])


def kiem_phu_thuoc():
    from importlib.metadata import distributions, version
    assert sys.version_info >= (3, 11), "Yêu cầu Python từ 3.11."
    for ten, ban in {"kho_tri_thuc_sdk": "2.2.0", "openpyxl": "3.1.5",
                     "et_xmlfile": "2.0.0", "defusedxml": "0.7.1"}.items():
        assert version(ten) == ban, "Thư viện không đúng bản đã ghim."
    from openpyxl.xml import DEFUSEDXML, LXML
    assert DEFUSEDXML and not LXML, "Bộ đọc XML chưa đúng môi trường sạch."
    cho_phep = {"pip", "setuptools", "kho-tri-thuc-sdk", "openpyxl", "et-xmlfile", "defusedxml"}
    assert {d.metadata["Name"].lower().replace("_", "-") for d in distributions()} <= cho_phep, (
        "Môi trường sạch có thư viện ngoài danh sách.")


def doc_bytes_goi():
    dong_goi = bo_dong_goi()
    assert MA in dong_goi.CAC_ENGINE
    cac_tep = {}
    for tep in sorted(GOI.rglob("*")):
        assert not tep.is_symlink(), "Gói có liên kết."
        if tep.is_file():
            ten = tep.relative_to(GOI).as_posix()
            dong_goi.kiem_ten(ten, MA)
            cac_tep[ten] = tep.read_bytes()
    assert {"engine.json", "README.md", "NGUON.md", "CHANGELOG.md",
            "requirements.lock", "sql/001_tao_ngan.sql", "sql/kiem_ke.json",
            "contract/yeu_cau_ai.schema.json", "contract/tra_loi_ai.schema.json",
            "ui/bang_ty_le.js", "e_phan_luong/chay.py"} <= cac_tep.keys()
    dong_goi.kiem_ke_sql(cac_tep, dong_goi.doc_json(cac_tep["engine.json"]))
    return dong_goi, cac_tep


def dong_goi_thu(ra):
    ra = Path(ra).resolve()
    assert not ra.is_relative_to(REPO.resolve()), "ZIP thử phải nằm ngoài repo."
    dong_goi, cac_tep = doc_bytes_goi()
    raw = dong_goi.tao_zip(MA, cac_tep)
    assert raw == dong_goi.tao_zip(MA, dict(reversed(list(cac_tep.items())))), (
        "Đóng hai lần không cùng bytes.")
    ra.mkdir(parents=True, exist_ok=True)
    tep = ra / "e_phan_luong-0.1.0.zip"
    with tep.open("xb") as f:
        f.write(raw)
    (ra / "SHA256SUMS.txt").write_text(
        f"{sha256(raw).hexdigest()}  {tep.name}\n", encoding="ascii")
    return tep


def test_zip_tat_dinh_du_tep_va_kiem_ke():
    dong_goi, cac_tep = doc_bytes_goi()
    raw = dong_goi.tao_zip(MA, cac_tep)
    assert raw == dong_goi.tao_zip(MA, dict(reversed(list(cac_tep.items()))))
    with zipfile.ZipFile(BytesIO(raw)) as z:
        assert len(z.namelist()) == len(set(z.namelist())) == len(cac_tep)
        assert set(z.namelist()) == {f"{MA}/{ten}" for ten in cac_tep}
        for ten, noi_dung in cac_tep.items():
            assert z.read(f"{MA}/{ten}") == noi_dung
        kk = json.loads(z.read(f"{MA}/sql/kiem_ke.json"))
        assert {m["duong_dan"] for m in kk["tep"]} == set(cac_tep) - {"sql/kiem_ke.json"}
        for muc in kk["tep"]:
            noi_dung = z.read(f"{MA}/{muc['duong_dan']}")
            assert (len(noi_dung), sha256(noi_dung).hexdigest()) == (muc["bytes"], muc["sha256"])
        assert all(i.date_time == dong_goi.THOI_GIAN for i in z.infolist())


def test_tu_choi_tep_ngoai_goi_va_cache():
    import pytest
    dong_goi = bo_dong_goi()
    for ten in (".venv/a.py", "e_phan_luong/__pycache__/a.pyc", "tests/test_demo.py",
                "../ngoai.py", "e_phan_luong/a.pyc", "docs/ghi-chu.md"):
        with pytest.raises(dong_goi.LoiDongGoi):
            dong_goi.kiem_ten(ten, MA)


def test_kiem_ke_phat_hien_bytes_va_tep_thua():
    import pytest
    dong_goi, cac_tep = doc_bytes_goi()
    phieu = dong_goi.doc_json(cac_tep["engine.json"])
    for thay_doi in ({"README.md": cac_tep["README.md"] + b"DEMO"},
                     {"e_phan_luong/tep_thua.py": b"# DEMO\n"}):
        with pytest.raises(dong_goi.LoiDongGoi):
            dong_goi.kiem_ke_sql({**cac_tep, **thay_doi}, phieu)


def test_kich_ban_may_sach():
    sh = (TESTS / "kiem_may_sach.sh").read_text(encoding="utf-8")
    cmd = (TESTS / "KIEM-MAY-SACH.cmd").read_bytes().decode("ascii")
    for noi_dung in (sh, cmd):
        for bat_buoc in ("--no-index", "--require-hashes", "--kiem-ke", "kho_tri_thuc_sdk.thu",
                        "kiem_doc_lap.py", "requirements.lock"):
            assert bat_buoc in noi_dung


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    nhom = ap.add_mutually_exclusive_group(required=True)
    nhom.add_argument("--kiem-ke", type=Path)
    nhom.add_argument("--dong-goi-thu", type=Path)
    ap.add_argument("--phu-thuoc", action="store_true")
    args = ap.parse_args()
    if args.kiem_ke:
        if args.phu_thuoc:
            kiem_phu_thuoc()
        print(f"[ĐẠT] kiem_bam_goi: {kiem_bam_goi(args.kiem_ke)} tệp khớp kiểm kê.")
    else:
        print(f"[ĐẠT] ZIP thử bytes worktree: {dong_goi_thu(args.dong_goi_thu)}")
