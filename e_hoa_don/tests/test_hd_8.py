"""HD-8: oracle b? sung cho chu?i nhi?u ti?n t? v? kh?ng ghi b?n."""
import builtins
import io
import zipfile
from hashlib import sha256

from kho_tri_thuc_sdk.thu import CoreGia
from test_hd_5 import tao_zip
from test_hd_7 import GOI, nguon, xuat, doc_xlsx


def test_zip_nhieu_tien_te_khong_cong_khong_ghi_ben(monkeypatch):
    xml = (GOI / "demo/hoa-don-DEMO.xml").read_bytes()
    usd = xml.replace(b"<DVTTe>VND</DVTTe>", b"<DVTTe>USD</DVTTe>")
    assert sha256(xml).hexdigest() == "06fe9986063ee65483c7d91880b948a1ab65856d05767508face98695c8d07fe"
    assert sha256(usd).hexdigest() == "92f52d9d0049a15f9cbac3a4e27ef2268428f583a333f93f9b43ed868c7d6825"
    raw = tao_zip([("z.xml", xml), ("a.xml", usd), ("loi.xml", b"<HDon")])
    core = CoreGia()
    original = builtins.open
    def read_only(file, mode="r", *args, **kwargs):
        assert not set(mode) & set("wax+"), "Engine kh?ng ???c ghi t?p."
        return original(file, mode, *args, **kwargs)
    monkeypatch.setattr(builtins, "open", read_only)
    monkeypatch.setattr(io, "open", read_only)
    data = nguon(core, raw, zip=True)
    t, workbook = xuat(core, data)
    sheets, _ = doc_xlsx(workbook)
    assert [t[k] for k in ("so_hoa_don", "so_loi", "da_doc_het", "can_kiem_tra")] == [2, 1, False, True]
    assert [(r[1], r[2], r[6], r[10:14]) for r in sheets[0][1:]] == [
        ("1", "z.xml", "0000123", ["1000000", "100000", "1100000", "VND"]),
        ("2", "a.xml", "0000123", ["1000000", "100000", "1100000", "USD"]),
    ]
    assert [r[3] for r in sheets[1][14:]] == ["doc_duoc", "doc_duoc", "loi"]
    with zipfile.ZipFile(io.BytesIO(workbook)) as z:
        assert all(b"<f" not in z.read(n) for n in ("xl/worksheets/sheet1.xml", "xl/worksheets/sheet2.xml"))
