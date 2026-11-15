"""OCR-3: mở lại DOCX, kiểm nội dung/lưới/ô gộp và bàn giao bằng CoreGia."""

from copy import deepcopy
import io
from pathlib import Path
from xml.etree import ElementTree as ET
import zipfile

import pytest

from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, ViecDaHuy
from kho_tri_thuc_sdk.thu import CoreGia, nap_engine_tu_goi

from demo.tao_pdf import CONG_TY, DONG_DEMO, NGAY, TIEN, pdf_demo
from e_ocr.xuat_word import MIME_DOCX, W, dung_docx


GOI = Path(__file__).resolve().parents[1] / "goi" / "e_ocr"
WORD = "ocr.xuat_word@1"


def bang_demo():
    cells = [
        (0, 0, 1, 2, "BẢNG DEMO"), (0, 2, 1, 2, ""),
        (1, 0, 2, 2, CONG_TY), (1, 2, 1, 1, TIEN), (1, 3, 1, 1, ""),
        (2, 2, 1, 1, NGAY), (2, 3, 1, 1, ""),
        (3, 0, 1, 1, ""), (3, 1, 1, 1, "  <DEMO> &\t  "), (3, 2, 1, 2, "2026-10-30"),
    ]
    xs, ys = [40, 100, 180, 340, 540], [120, 150, 180, 220, 260]
    return {"loai": "bang", "hop": [40, 120, 540, 260], "o": [
        {"hang": r, "cot": c, "gop_hang": rs, "gop_cot": cs, "van_ban": text,
         "hop": [xs[c], ys[r], xs[c + cs], ys[r + rs]]}
        for r, c, rs, cs, text in reversed(cells)
    ]}


def tai_lieu_demo():
    return {"phien_ban": 1, "so_trang": 2, "trang": [
        {"so": 2, "rong": 842, "cao": 595, "don_vi": "pt", "khoi": [
            {"loai": "doan", "hop": [30, 50, 500, 80], "van_ban": "DEMO TRANG HAI"}]},
        {"so": 1, "rong": 595, "cao": 842, "don_vi": "pt", "khoi": [
            {"loai": "doan", "hop": [40, 40, 540, 65], "van_ban": "DEMO TRƯỚC BẢNG"},
            bang_demo(),
            {"loai": "doan", "hop": [40, 300, 540, 340], "van_ban": "DEMO SAU BẢNG"}]},
    ]}


def mo_docx(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        assert archive.testzip() is None
        types = ET.fromstring(archive.read("[Content_Types].xml"))
        assert any(n.get("PartName") == "/word/document.xml" for n in types)
        rels = ET.fromstring(archive.read("_rels/.rels"))
        assert any(n.get("Target") == "word/document.xml" for n in rels)
        return ET.fromstring(archive.read("word/document.xml"))


def chu(node):
    return "".join(n.text or "" for n in node.iter(W + "t"))


def test_docx_giu_du_luoi_o_trong_va_gop_hai_chieu():
    data = tai_lieu_demo()
    truoc = deepcopy(data)
    root = mo_docx(dung_docx(data))
    assert data == truoc, "Xuất Word không sửa dữ liệu nguồn."
    table, = root.iter(W + "tbl")
    grid = table.find(W + "tblGrid")
    assert [int(c.get(W + "w")) for c in grid] == [1200, 1600, 3200, 4000]
    # 16 vị trí lưới: gộp ngang bỏ 5 tc; ô kéo dọc có tc tiếp nối ở hàng 2.
    assert len(list(table.iter(W + "tc"))) == 11
    assert len(list(table.iter(W + "gridSpan"))) == 5
    rows = table.findall(W + "tr")
    anchors, occupied, active = {}, set(), {}
    for r, row in enumerate(rows):
        c = 0
        next_active = {}
        for cell in row.findall(W + "tc"):
            span = cell.find(W + "tcPr/" + W + "gridSpan")
            cs = int(span.get(W + "val")) if span is not None else 1
            merge = cell.find(W + "tcPr/" + W + "vMerge")
            if merge is not None and merge.get(W + "val") == "continue":
                anchor = active[c]
                anchors[anchor]["gop_hang"] += 1
                assert chu(cell) == "", "Không lặp nội dung ô gộp dọc."
            else:
                anchor = (r, c)
                anchors[anchor] = {"gop_hang": 1, "gop_cot": cs, "van_ban": chu(cell)}
            if merge is not None:
                next_active[c] = anchor
            for x in range(c, c + cs):
                assert (r, x) not in occupied
                occupied.add((r, x))
            c += cs
        assert c == 4
        active = next_active
    assert len(occupied) == 16
    expected = {(o["hang"], o["cot"]): {
        k: o[k] for k in ("gop_hang", "gop_cot", "van_ban")
    } for o in bang_demo()["o"]}
    # Tab là phần tử OOXML, không phải text node.
    expected[3, 1]["van_ban"] = "  <DEMO> &  "
    assert anchors == expected
    assert {pos for pos, cell in anchors.items() if cell["van_ban"] == ""} == {
        (0, 2), (1, 3), (2, 3), (3, 0)
    }
    assert [m.get(W + "val") for m in table.iter(W + "vMerge")] == ["restart", "continue"]
    assert len(list(root.iter(W + "tab"))) == 1
    assert {TIEN, NGAY, "2026-10-30", CONG_TY} <= {chu(c) for c in table.iter(W + "tc")}


def test_vi_tri_bang_thu_tu_khoi_va_phan_trang():
    root = mo_docx(dung_docx(tai_lieu_demo()))
    text = chu(root)
    assert text.index("DEMO TRƯỚC BẢNG") < text.index("BẢNG DEMO") < text.index("DEMO SAU BẢNG")
    assert text.index("DEMO SAU BẢNG") < text.index("DEMO TRANG HAI")
    pos, = root.iter(W + "tblpPr")
    assert (pos.get(W + "horzAnchor"), pos.get(W + "vertAnchor")) == ("page", "page")
    assert (pos.get(W + "tblpX"), pos.get(W + "tblpY")) == ("800", "2400")
    sizes = list(root.iter(W + "pgSz"))
    assert [(s.get(W + "w"), s.get(W + "h")) for s in sizes] == [("11900", "16840"), ("16840", "11900")]
    assert sizes[1].get(W + "orient") == "landscape"
    body = root.find(W + "body")
    assert body[-1].tag == W + "sectPr"
    assert len(body.findall(W + "p/" + W + "pPr/" + W + "sectPr")) == 1


def test_hai_bang_lien_nhau_va_trang_rong_khong_bi_mat():
    data = tai_lieu_demo()
    data["trang"][0]["khoi"] = []
    data["trang"][1]["khoi"] = [bang_demo(), bang_demo()]
    root = mo_docx(dung_docx(data))
    body = list(root.find(W + "body"))
    indices = [i for i, n in enumerate(body) if n.tag == W + "tbl"]
    assert indices[1] > indices[0] + 1
    assert body[indices[0] + 1].tag == W + "p"
    assert len(list(root.iter(W + "sectPr"))) == 2


def test_schema_khong_co_hop_tung_o_van_giu_du_o():
    data = tai_lieu_demo()
    for cell in data["trang"][1]["khoi"][1]["o"]:
        cell.pop("hop")
    root = mo_docx(dung_docx(data))
    assert len(list(root.iter(W + "tc"))) == 11
    assert [int(c.get(W + "w")) for c in root.iter(W + "gridCol")] == [2500] * 4


@pytest.mark.parametrize("sua,ma", [
    (lambda d: d["trang"][1]["khoi"][1]["o"].pop(), "CAU_TRUC_WORD_KHONG_HOP_LE"),
    (lambda d: d["trang"][1]["khoi"][1]["o"].append(deepcopy(bang_demo()["o"][0])), "CAU_TRUC_WORD_KHONG_HOP_LE"),
    (lambda d: d["trang"][1]["khoi"][1]["o"][0].update(gop_cot=41), "BANG_QUA_LON"),
    (lambda d: d["trang"][1]["khoi"][1]["o"][0].update(gop_hang=101), "BANG_QUA_LON"),
    (lambda d: d["trang"][1]["khoi"][1]["o"][0].update(gop_hang=0), "CAU_TRUC_WORD_KHONG_HOP_LE"),
    (lambda d: d["trang"][0].update(so=1), "CAU_TRUC_WORD_KHONG_HOP_LE"),
    (lambda d: d.update(so_trang=3), "CAU_TRUC_WORD_KHONG_HOP_LE"),
    (lambda d: d["trang"][0].update(don_vi="khong-ro"), "CAU_TRUC_WORD_KHONG_HOP_LE"),
    (lambda d: d["trang"][0].update(rong=float("nan")), "CAU_TRUC_WORD_KHONG_HOP_LE"),
    (lambda d: d["trang"][1]["khoi"][0].update(van_ban="DEMO\x00"), "CAU_TRUC_WORD_KHONG_HOP_LE"),
    (lambda d: d["trang"][1]["khoi"][0].update(van_ban="D" * 500_001), "QUA_DO_DAI"),
    (lambda d: d.update(trang=[deepcopy(d["trang"][0])] * 61, so_trang=61), "QUA_SO_TRANG"),
])
def test_tu_choi_du_lieu_khong_day_du_hoac_qua_tran(sua, ma):
    data = tai_lieu_demo()
    sua(data)
    with pytest.raises(LoiNghiepVu) as err:
        dung_docx(data)
    assert err.value.ma == ma


def chay_word(raw, ten="DEMO.goc.pdf"):
    core = CoreGia()
    tep = core.them_tep(ten, raw, "application/pdf")
    kq = core.chay_thu(nap_engine_tu_goi(GOI), WORD, {"loai": "tep", "tep": tep})
    return core, kq


def test_action_that_doc_pdf_giu_bang_va_tai_docx_ra():
    core, kq = chay_word(pdf_demo(DONG_DEMO, DONG_DEMO, DONG_DEMO, bang=True))
    assert kq["trang_thai"] == "XONG", kq
    tep = kq["ket_qua"]["tep"]
    assert kq["ket_qua"]["loai"] == "tep"
    assert tep["ten"] == "DEMO.goc-OCR.docx" and tep["mime"] == MIME_DOCX
    raw = core.doc_tep(tep["tep_id"])
    assert tep["kich_thuoc"] == len(raw)
    root = mo_docx(raw)
    assert len(list(root.iter(W + "tbl"))) == 3
    assert len(list(root.iter(W + "sectPr"))) == 3
    assert len(list(root.iter(W + "tc"))) == 21
    assert sum(chu(c) == "" for c in root.iter(W + "tc")) == 6
    assert len(list(root.iter(W + "gridSpan"))) == 3
    assert chu(root).count("BANG DEMO") == 3
    assert all(chu(root).count(s) == 6 for s in (TIEN, NGAY))
    assert chu(root).count(CONG_TY) == 3


@pytest.mark.parametrize("ten", ["Công ty DEMO.pdf", "C:\\DEMO\\Công ty DEMO.pdf", "/DEMO/Công ty DEMO.pdf"])
def test_action_dung_du_lieu_chung_giu_gop_doc_va_ten_goc(monkeypatch, ten):
    monkeypatch.setattr("e_ocr.chay.trich_van_ban", lambda *a, **kw: tai_lieu_demo())
    core, kq = chay_word(pdf_demo(DONG_DEMO), ten)
    assert kq["trang_thai"] == "XONG", kq
    tep = kq["ket_qua"]["tep"]
    assert tep["ten"] == "Công ty DEMO-OCR.docx"
    root = mo_docx(core.doc_tep(tep["tep_id"]))
    assert len(list(root.iter(W + "vMerge"))) == 2


@pytest.mark.parametrize("loi,trang_thai", [(ChuaRo("DEMO-luot"), "CHUA_RO"), (ViecDaHuy(), "HUY")])
def test_khong_tai_docx_khi_nguon_chua_ro_hoac_huy(monkeypatch, loi, trang_thai):
    def dung(*args, **kwargs):
        raise loi
    monkeypatch.setattr("e_ocr.chay.trich_van_ban", dung)
    core, kq = chay_word(pdf_demo(DONG_DEMO))
    assert kq["trang_thai"] == trang_thai
    assert kq["ket_qua"] is None and core.so_lan_ghi["ket_qua"] == 0
    assert core.so_lan_ghi.get("tep", 0) == 0


def test_huy_trong_luc_dung_bang_khong_doi_thanh_loi_cau_truc():
    count = 0
    def huy():
        nonlocal count
        count += 1
        if count == 8:
            raise ViecDaHuy()
    with pytest.raises(ViecDaHuy):
        dung_docx(tai_lieu_demo(), kiem_huy=huy)


@pytest.mark.parametrize("ten,loi", [("D" * 250 + ".pdf", "TEN_TEP_KHONG_HOP_LE"), ("DEMO.pdf", "CAU_TRUC_WORD_KHONG_HOP_LE")])
def test_loi_dung_word_khong_tai_tep_hoac_nop_ket_qua(monkeypatch, ten, loi):
    data = tai_lieu_demo()
    data["trang"][1]["khoi"][1]["o"].pop()
    monkeypatch.setattr("e_ocr.chay.trich_van_ban", lambda *a, **kw: data)
    core, kq = chay_word(pdf_demo(DONG_DEMO), ten)
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == loi
    assert kq["ket_qua"] is None
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == 0


def test_xuong_dong_khoang_trang_va_ky_tu_xml_duoc_giu():
    data = tai_lieu_demo()
    data["trang"][1]["khoi"][0]["van_ban"] = "  DEMO <&>\r\n1.000.000 VND\n30/10/2026  "
    root = mo_docx(dung_docx(data))
    p = root.find(W + "body/" + W + "p")
    assert chu(p) == "  DEMO <&>1.000.000 VND30/10/2026  "
    assert len(list(p.iter(W + "br"))) == 2
