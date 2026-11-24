"""OCR-10: PDF DEMO thuần Python; đã kiểm bằng Core giả (CoreGia)."""

from pathlib import Path
from types import SimpleNamespace
import io
from zipfile import ZipFile
from xml.etree import ElementTree as ET

import pdfplumber
import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu

from demo.tao_pdf import pdf_demo
from e_ocr import lop_chu, tesseract
from test_ocr_1 import chay, hot_folder, ABBYYGia
from test_ocr_2 import cli_gia


NANG_LUC = ["ocr.doc_van_ban@1", "ocr.doc_tai_lieu@1", "ocr.xuat_word@1"]
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def khung(x, y, w, h):
    return [(x, y, x+w, y), (x, y+h, x+w, y+h),
            (x, y, x, y+h), (x+w, y, x+w, y+h)]


def pdf_khong_deu(ca, *, co_chu=True):
    if ca == "chong_o":
        net = khung(50, 180, 200, 100) + khung(100, 180, 200, 60)
    elif ca == "thieu_net":
        net = [(50, 180, 250, 180), (50, 230, 250, 230), (50, 280, 150, 280),
               (50, 180, 50, 280), (150, 180, 150, 280), (250, 180, 250, 260)]
    else:
        net = khung(50, 180, 200, 100) + khung(100, 200, 150, 80)
    # Một bảng tốt trên cùng trang phải vẫn còn cấu trúc sau hạ cấp.
    net += khung(50, 350, 200, 60) + [(150, 350, 150, 410)]
    chu = ("DEMO đầu trang", "DEMO ô thứ nhất", "DEMO ô thứ hai",
           "DEMO ngoài khung", "DEMO tốt", "DEMO cạnh bảng", "DEMO cuối trang") if co_chu else ()
    matrices = {i: (1, 0, 0, 1, x, 842-y) for i, (x, y) in enumerate(
        [(50, 100), (60, 220), (60, 255), (320, 220), (60, 380), (320, 380), (50, 450)])}
    return pdf_demo(chu, text_matrices=matrices, duong_ke=net)


def chu_lop(raw):
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        return "\n".join(line["text"] for line in pdf.pages[0].extract_text_lines())


def mo_word(core, kq):
    with ZipFile(io.BytesIO(core.doc_tep(kq["ket_qua"]["tep"]["tep_id"]))) as z:
        return ET.fromstring(z.read("word/document.xml"))


@pytest.mark.parametrize("nguon", ["lop_chu", "abbyy", "tesseract"])
@pytest.mark.parametrize("ca", ["chong_o", "thieu_net", "khung_chu_ky"])
@pytest.mark.parametrize("nang_luc", NANG_LUC)
def test_bang_hong_khong_dung_ca_tep(tmp_path, monkeypatch, hot_folder, ca, nang_luc, nguon):
    raw = pdf_khong_deu(ca)
    tep = tmp_path / f"DEMO-{ca}.pdf"
    tep.write_bytes(raw)
    dap_an = chu_lop(raw)
    if nguon == "abbyy":
        vao, ra, _ = hot_folder
        with ABBYYGia(vao, ra, raw):
            core, kq = chay(pdf_khong_deu(ca, co_chu=False), nang_luc,
                           tham_so={"nguon": "chi_abbyy"})
    elif nguon == "tesseract":
        gia_tsv(monkeypatch, raw)
        core, kq = chay(pdf_khong_deu(ca, co_chu=False), nang_luc,
                       tham_so={"nguon": "chi_tesseract"})
    else:
        core, kq = chay(tep.read_bytes(), nang_luc)
    assert kq["trang_thai"] == "XONG", kq
    if nang_luc == NANG_LUC[0]:
        assert kq["ket_qua"] == {"loai": "van_ban", "van_ban": dap_an}
    elif nang_luc == NANG_LUC[1]:
        data = kq["ket_qua"]["van_ban_tai_lieu"]
        assert data["van_ban"] == dap_an
        assert sum("Trang 1 có bảng kẻ không đều;" in w for w in data["canh_bao"]) == 1
        assert data["nguon_doc"] == {"lop_chu": "lop_chu_san"}.get(nguon, nguon)
        blocks = data["trang"][0]["khoi"]
        assert sum(b["loai"] == "bang" for b in blocks) == 1
        texts = [b["van_ban"] if b["loai"] == "doan" else
                 " ".join(c["van_ban"] for c in b["o"]) for b in blocks]
        assert " ".join(texts).split() == dap_an.split()
        assert all("hop" in b for b in blocks)
    else:
        root = mo_word(core, kq)
        assert len(list(root.iter(W + "tbl"))) == 1
        texts = [n.text for n in root.iter(W + "t") if n.text]
        warnings = [t for t in texts if "có bảng kẻ không đều;" in t]
        assert len(warnings) == 1
        assert len(list(root.iter(W + "pageBreakBefore"))) == 1
        assert " ".join(t for t in texts if t not in warnings).split() == dap_an.split()


@pytest.mark.parametrize("ma_loi", ["BANG_KHONG_DAY_DU", "BANG_QUA_LON"])
@pytest.mark.parametrize("nguon", ["lop_chu", "abbyy", "tesseract"])
def test_van_ban_thuan_khong_goi_do_bang(monkeypatch, hot_folder, cli_gia, ma_loi, nguon):
    def cam(*args, **kwargs):
        raise LoiNghiepVu(ma_loi, "DEMO không được dò bảng.")
    monkeypatch.setattr(lop_chu, "doc_bang_trang", cam)
    monkeypatch.setattr(tesseract, "doc_bang_trang", cam)
    monkeypatch.setattr(pdfplumber.page.Page, "find_tables", cam)
    raw = pdf_khong_deu("chong_o")
    if nguon == "abbyy":
        vao, ra, _ = hot_folder
        with ABBYYGia(vao, ra, raw):
            _, kq = chay(pdf_khong_deu("chong_o", co_chu=False), NANG_LUC[0],
                         tham_so={"nguon": "chi_abbyy"})
    else:
        _, kq = chay(raw if nguon == "lop_chu" else pdf_khong_deu("chong_o", co_chu=False),
                     NANG_LUC[0], tham_so={"nguon": "chi_tesseract"})
    assert kq["trang_thai"] == "XONG", kq
    assert set(kq["ket_qua"]) == {"loai", "van_ban"}


@pytest.mark.parametrize("ca", ["chong_o", "thieu_net", "khung_chu_ky"])
def test_do_lop_chu_khong_giu_bang_khong_canh_bao(ca):
    raw = pdf_khong_deu(ca)
    data = lop_chu.doc_lop_chu(raw, giu_bang=False)
    assert data.text == chu_lop(raw) and not data.warnings
    assert all(b["loai"] == "doan" for b in data.pages[0]["khoi"])


def gia_tsv(monkeypatch, raw):
    """Giả executable, giữ nguyên render PDF, dò bảng và ghép từ TSV thật."""
    page = lop_chu.doc_lop_chu(raw, giu_bang=False).pages[0]
    monkeypatch.setattr(tesseract, "_kiem_bo_doc", lambda *a: ("DEMO", "vie+eng"))

    def chay_cli(lenh, **kwargs):
        from PIL import Image
        with Image.open(lenh[1]) as anh:
            sx, sy = anh.width / page["rong"], anh.height / page["cao"]
        rows = ["level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext"]
        for i, block in enumerate(page["khoi"], 1):
            for j, word in enumerate(block["dong"][0]["tu"], 1):
                x0, y0, x1, y1 = word["hop"]
                rows.append(f"5\t1\t1\t1\t{i}\t{j}\t{round(x0*sx)}\t{round(y0*sy)}\t"
                            f"{round((x1-x0)*sx)}\t{round((y1-y0)*sy)}\t95\t{word['van_ban']}")
        Path(lenh[2]).with_suffix(".tsv").write_text("\n".join(rows), encoding="utf-8")
        return b""

    monkeypatch.setattr(tesseract, "_chay", chay_cli)


def test_tesseract_van_ban_thuan_khong_canh_bao_bang(cli_gia):
    from demo.tao_pdf import DONG_DEMO
    raw = pdf_khong_deu("chong_o", co_chu=False)
    data = tesseract.doc_tesseract(raw, "application/pdf", {},
                                  viec=SimpleNamespace(kiem_huy=lambda: None, tien_do=lambda *a: None),
                                  giu_bang=False)
    assert data.text == "\n".join(DONG_DEMO)
    assert data.warnings and all("bảng" not in w.lower() for w in data.warnings)
    assert all(b["loai"] == "doan" for b in data.pages[0]["khoi"])


@pytest.mark.parametrize("hang,cot", [(101, 1), (1, 41)])
@pytest.mark.parametrize("nang_luc", NANG_LUC)
def test_tran_bang_chi_ap_dung_khi_giu_bang(hang, cot, nang_luc):
    net = khung(50, 180, 450, 505)
    net += [(50 + 450*i/cot, 180, 50 + 450*i/cot, 685) for i in range(1, cot)]
    net += [(50, 180 + 505*i/hang, 500, 180 + 505*i/hang) for i in range(1, hang)]
    raw = pdf_demo(("DEMO vượt trần bảng",), duong_ke=net)
    _, kq = chay(raw, nang_luc)
    if nang_luc == NANG_LUC[0]:
        assert kq["trang_thai"] == "XONG", kq
        assert kq["ket_qua"]["van_ban"] == chu_lop(raw)
    else:
        assert kq["trang_thai"] == "LOI", kq
        assert kq["loi"]["ma"] == "BANG_QUA_LON"


def test_phien_ban_ocr_10():
    from e_ocr import PHIEN_BAN
    from kho_tri_thuc_sdk.thu import nap_engine_tu_goi
    from test_ocr_1 import GOI
    assert PHIEN_BAN == nap_engine_tu_goi(GOI).phieu["phien_ban"] == "1.0.12"


@pytest.mark.parametrize("ten", ["DEMO-bang-3-trang.pdf", "DEMO-ABBYY-gia-1-trang.pdf",
                                 "DEMO-ABBYY-gia-3-trang.pdf"])
@pytest.mark.parametrize("nang_luc", [NANG_LUC[1], NANG_LUC[2]])
def test_bang_demo_hop_le_giu_nguyen(ten, nang_luc):
    from demo.tao_bo_demo import HANG_BANG
    from test_ocr_1 import GOI
    legacy = ten == "DEMO-bang-3-trang.pdf"
    rows = [["BANG DEMO", None, None], ["DEMO", "1.000.000 VND", ""],
            ["DEMO", "30/10/2026", ""]] if legacy else HANG_BANG
    dap_an = [(r, c, 1, 3 if r == 0 else 1, text)
              for r, row in enumerate(rows) for c, text in enumerate(row) if text is not None]
    core, kq = chay((GOI / "demo" / ten).read_bytes(), nang_luc)
    assert kq["trang_thai"] == "XONG", kq
    so_trang = 1 if "1-trang" in ten else 3
    if nang_luc == NANG_LUC[1]:
        data = kq["ket_qua"]["van_ban_tai_lieu"]
        assert data["so_trang"] == so_trang and not data["canh_bao"]
        for page in data["trang"]:
            bang, = [b for b in page["khoi"] if b["loai"] == "bang"]
            assert [(c["hang"], c["cot"], c["gop_hang"], c["gop_cot"], c["van_ban"])
                    for c in bang["o"]] == dap_an
    else:
        root = mo_word(core, kq)
        tables = list(root.iter(W + "tbl"))
        assert len(tables) == so_trang
        assert not list(root.iter(W + "pageBreakBefore"))
        for table in tables:
            assert ["".join(t.text or "" for t in c.iter(W + "t"))
                    for c in table.iter(W + "tc")] == [c[-1] for c in dap_an]
            assert [n.get(W + "val") for n in table.iter(W + "gridSpan")] == ["3"]
