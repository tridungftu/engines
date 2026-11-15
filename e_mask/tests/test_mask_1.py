"""MASK-1: chỉ DEMO, lõi thuần; cổng vẫn kiểm bằng Core giả (CoreGia)."""
import ast
import hashlib
import importlib
from pathlib import Path
import re
import subprocess
import sys
import unicodedata

import pytest

GOI = Path(__file__).resolve().parents[1] / "goi" / "e_mask"
sys.path.insert(0, str(GOI))
from e_mask.nguon.privacy import core
from e_mask.nguon.privacy.company_names import company_spans
from e_mask.nguon.privacy.person_names import person_names
from e_mask.nguon.privacy.types import PrivacyError, normalize

TEN = "Công ty DEMO Ánh Dương"
TIEN_NGAY = "1.000.000 VND ngày 30/10/2026"
TEP = {"__init__.py", "types.py", "core.py", "company_names.py", "person_names.py"}


def quy_tac(source=TEN, token="[[KH-DEMO-00123]]", category="CONG_TY", **them):
    return {"source": source, "token": token, "category": category, "enabled": True, **them}


@pytest.mark.parametrize("dang", ["NFC", "NFD"])
@pytest.mark.parametrize("ngat", [" ", "  ", "\n", "\u00a0"])
def test_chuan_hoa_vi_tri_va_thay(dang, ngat):
    cum = unicodedata.normalize(dang, TEN.replace(" ", ngat))
    duoi = unicodedata.normalize(dang, " — nội dung DEMO giữ nguyên; " + TIEN_NGAY)
    text = "DEMO: " + cum + duoi
    spans = core.KnownText(text).spans(unicodedata.normalize(dang, TEN), loose=False)
    assert spans == [(6, 6 + len(cum))]
    assert text[slice(*spans[0])] == cum
    rules = core.validate_rules([quy_tac(source=unicodedata.normalize(dang, TEN))])
    masked, count = core.replace(text, rules)
    assert (masked, count) == ("DEMO: [[KH-DEMO-00123]]" + duoi, 1)
    assert core.numeric_review(text, masked, rules)["changed"] is False
    core.verify(masked, rules)
    assert core.key(cum) == core.key(TEN)
    assert normalize(unicodedata.normalize(dang, TEN)) == TEN


def test_ten_dai_uu_tien_mot_luot_khong_thay_lai_bi_danh():
    rules = core.validate_rules([
        quy_tac("DEMO Ánh Dương", "[[MASKCT-0001]]"),
        quy_tac(TEN, "[[KH-DEMO-00123]]"),
        quy_tac("KH", "[[MASKKHAC-0001]]", "KHAC"),
    ])
    assert core.replace(TEN + "; DEMO Ánh Dương", rules) == (
        "[[KH-DEMO-00123]]; [[MASKCT-0001]]", 2)


@pytest.mark.parametrize("mat_chu", ["DEMO Anh Duong", "DEMO Ánh Dương"])
def test_knowntext_bien_the_dau_va_ranh_gioi(mat_chu):
    text = "DEMO: " + mat_chu + "; XDEMO Anh Duong; DEMO Anh DuongX"
    finder = core.KnownText(text)
    assert finder.spans("DEMO Ánh Dương") == [(6, 6 + len(mat_chu))]
    assert finder.spans("DEMO Ánh Dương", loose=False) == (
        [(6, 6 + len(mat_chu))] if "Ánh" in mat_chu else [])
    assert core.KnownText("DEMO Án Phát").spans("DEMO An Phát") == []
    assert core.KnownText("DEMO\tÁnh Dương").spans("DEMO Anh Duong") == []


@pytest.mark.parametrize("token", ["[[KH-DEMO-00123]]", "[[KH.demo_Ab-00123]]",
                                    "[[MASKCT-100000]]", "[[MASKTAM-demo123]]"])
def test_bi_danh_hop_le_giu_ma_nguyen(token):
    assert core.validate_rules([quy_tac(token=token)])[0]["token"] == token
    assert core.alias_like("DEMO " + token)


@pytest.mark.parametrize("token", ["[CONG_TY_001]", "[[mã thật]]", "[[KH DEMO]]", "[[]]",
                                    "[[" + "K" * 101 + "]]", "[[KH-DEMO]]x"])
def test_tu_choi_bi_danh_cu_va_khong_hop_le(token):
    with pytest.raises(PrivacyError):
        core.validate_rules([quy_tac(token=token)])


@pytest.mark.parametrize("nhom,tien_to", [("CONG_TY", "MASKCT"), ("CA_NHAN", "MASKCN"),
    ("DIA_CHI", "MASKDC"), ("MA_SO_THUE", "MASKMST"), ("TAI_KHOAN", "MASKTK"),
    ("KHAC", "MASKKHAC"), ("EMAIL", "MASKKHAC")])
def test_ma_tu_sinh_khong_trung_va_khong_cat_so(nhom, tien_to):
    assert core.next_token(nhom, set()) == f"[[{tien_to}-0001]]"
    assert core.next_token(nhom, {f"[[{tien_to.lower()}-99999]]", "[[KH-DEMO-00123]]"}) == (
        f"[[{tien_to}-100000]]")
    so_lon = "9" * 30
    token = core.next_token(nhom, {f"[[{tien_to}-{so_lon}]]"})
    assert token == f"[[{tien_to}-{int(so_lon) + 1}]]"
    assert core.TOKEN.fullmatch(token)


def test_ma_tu_sinh_vuot_khuon_tu_choi_khong_cat():
    with pytest.raises(PrivacyError, match="vượt giới hạn"):
        core.next_token("CONG_TY", {"[[MASKCT-" + "9" * 94 + "]]"})


def test_known_rules_tan_dung_junsky_khong_cap_lai(monkeypatch):
    rules = core.validate_rules([quy_tac()])
    def cam_cap_ma(*args):
        pytest.fail("Không được cấp lại mã Junsky đã có.")
    monkeypatch.setattr(core, "next_token", cam_cap_ma)
    text = "DEMO: Cong ty DEMO Anh Duong; " + TEN
    fresh = core.known_rules(text, [(TEN, "CONG_TY", True)], rules, set())
    assert len(fresh) == 1
    assert fresh[0]["token"] == "[[KH-DEMO-00123]]"
    masked, count = core.replace(text, rules + fresh)
    assert count == 2 and masked.count("[[KH-DEMO-00123]]") == 2
    assert core.leaked_known(masked, [(TEN, "CONG_TY", True)]) == []


@pytest.mark.parametrize("ma,surface,nhom", [
    ("001234567890", "001.234.567.890", "TAI_KHOAN"),
    ("0012345678", "001 234 5678", "MA_SO_THUE"),
    ("12052026", "1205-2026", "GIAY_TO"),
])
def test_ma_so_demo_khong_bi_coi_la_tien_ngay(ma, surface, nhom):
    text = "Mã DEMO: " + surface + "; " + TIEN_NGAY
    known = [(ma, nhom, True)]
    assert core.KnownText(text).spans(ma, masking=True)
    rules = core.validate_rules(core.known_rules(text, known, [], set()))
    masked, count = core.replace(text, rules)
    assert count == 1 and surface not in masked
    assert masked.endswith(TIEN_NGAY)
    assert core.leaked_known(masked, known) == []
    assert core.numeric_review(text, masked, rules) == {
        "changed": False, "before_count": 2, "after_count": 2}


@pytest.mark.parametrize("ma,surface", [("1000000", "1.000.000 VND"),
                                       ("30102026", "30/10/2026")])
def test_khong_che_bien_the_trung_tien_ngay_nhung_van_bao_con_sot(ma, surface):
    text = "DEMO " + surface
    finder = core.KnownText(text)
    assert finder.spans(ma, masking=True) == []
    assert finder.spans(ma, masking=False)
    known = [(ma, "GIAY_TO", True)]
    assert core.known_rules(text, known, [], set()) == []
    assert core.leaked_known(text, known)


def test_bao_ve_ranh_gioi_so_va_bi_danh():
    assert core.KnownText("DEMO 1.001.234.567.890").spans("001234567890", masking=True) == []
    known = [("12345678", "GIAY_TO", True)]
    assert core.leaked_known("DEMO X001234567890Y", known)
    assert core.leaked_known("DEMO 1234[[KH-DEMO-00123]]5678", known) == []


@pytest.mark.parametrize("thay", ["999.000 VND ngày 30/10/2026", "1.000.000 VND ngày 31/10/2026",
                                  "1.000.000 VND", TIEN_NGAY + " 1.000.000 VND"])
def test_numeric_review_bat_sua_mat_them_so(thay):
    rules = core.validate_rules([quy_tac()])
    before = TEN + ": " + TIEN_NGAY
    assert core.numeric_review(before, "[[KH-DEMO-00123]]: " + thay, rules)["changed"]


def test_doi_ten_va_goi_y_thu_cong_thieu_tai_nguyen():
    assert company_spans(TEN + " ký hợp đồng DEMO.")[0].source == TEN
    assert person_names("Ông DEMO Nguyễn An; chức vụ: DEMO") == ["DEMO Nguyễn An"]
    with pytest.raises(PrivacyError, match="Chưa có đủ tài nguyên"):
        core.suggest([TEN])
    with pytest.raises(PrivacyError, match="Chưa có đủ tài nguyên"):
        core.dau_vet("DEMO")
    with pytest.raises(PrivacyError, match="Chưa có đủ tài nguyên"):
        core.verify("DEMO", [], known=[])


def test_loi_khong_in_cum_goc(capsys):
    with pytest.raises(PrivacyError) as exc:
        core.validate_rules([quy_tac(), quy_tac(source=TEN.upper())])
    assert TEN not in str(exc.value)
    assert capsys.readouterr() == ("", "")


def test_nhap_sach_chi_stdlib_khong_doc_tai_nguyen_khong_ghi():
    code = r"""
import importlib, os, pathlib, sys
sys.path.insert(0, sys.argv[1])
def cam(event, args):
    if event == 'import' and args[0].split('.')[0] in {'cryptography', 'docx', 'kho_tri_thuc'}:
        raise AssertionError('Import ngoài phạm vi')
    if event.startswith(('subprocess.', 'socket.')) or event in {'os.system', 'os.spawn'}:
        raise AssertionError('Không được chạy nguồn ngoài')
    if event == 'open':
        name, mode, flags = args
        if (isinstance(mode, str) and any(c in mode for c in 'wax+')) or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC):
            raise AssertionError('Không được ghi tệp')
        if isinstance(name, str) and not name.endswith(('.py', '.pyc')):
            raise AssertionError('Không được đọc dữ liệu/tài nguyên')
sys.addaudithook(cam)
for name in ('', '.types', '.core', '.company_names', '.person_names'):
    importlib.import_module('e_mask.nguon.privacy' + name)
from e_mask.nguon.privacy import core
assert not any(name.endswith('.detectors') for name in sys.modules)
assert core.KnownText('DEMO').spans('DEMO') == [(0, 4)]
assert not any(hasattr(core, name) for name in ('encrypt_mapping', 'decrypt_mapping', 'make_docx', 'export_document', 'export_bundle'))
"""
    result = subprocess.run([sys.executable, "-I", "-S", "-B", "-X", "utf8", "-c", code, str(GOI)],
                            capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert result.returncode == 0, result.stderr


def test_gioi_han_dung_nam_tep_va_phu_thuoc():
    folder = GOI / "e_mask" / "nguon" / "privacy"
    assert {p.name for p in folder.iterdir()} == TEP | {"detectors.py", "leftovers.py"}
    for p in folder.glob("*.py"):
        tree = ast.parse(p.read_text("utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(alias.name.split('.')[0] in sys.stdlib_module_names for alias in node.names)
            if isinstance(node, ast.ImportFrom) and not node.level:
                assert node.module.split('.')[0] in sys.stdlib_module_names


def test_nguon_sha_truoc_sau_va_nguon_cu_nguyen_ven():
    doc = (GOI / "NGUON.md").read_text("utf-8")
    root = GOI.parents[2]
    rows = [line for line in doc.splitlines() if line.startswith("| `e_mask/ma-nguon/nguon/privacy/")]
    assert len(rows) == 7
    def sha_lf(p):
        return hashlib.sha256(p.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
    for row in rows:
        cols = [c.strip(' `') for c in row.strip('|').split('|')]
        source, dest, raw_before, raw_after, lf_before, lf_after, _ = cols
        assert re.fullmatch('[0-9a-f]{64}', raw_before)
        assert re.fullmatch('[0-9a-f]{64}', raw_after)
        assert sha_lf(root / source) == lf_before
        assert sha_lf(GOI / dest) == lf_after
