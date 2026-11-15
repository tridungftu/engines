"""Tạo DEMO ngoài runtime để kiểm render thủ công; không ghi trong gói engine.

Chạy bằng venv với --thu-muc chỉ định trong workspace. pypdfium2 chỉ là
công cụ QA offline, không được import bởi engine hoặc yêu cầu khi pytest.
"""
import argparse
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from test_dc9 import (tao_mau, dat_bo, bo_demo, dat_tu_dien, so, quet, DieuPhoiDEMO,
                      chuan_bi, hau_kiem, ghim_demo, xuat, doc_kq, bc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--thu-muc", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    output = (root / args.thu_muc).resolve()
    if not output.is_relative_to(root) or output.is_relative_to(root/"e_doi_chieu/goi"):
        parser.error("Thư mục DEMO phải ở trong workspace và ngoài thư mục gói.")
    output.mkdir(parents=True, exist_ok=True)
    m = tao_mau("gach")
    dat_bo(m, bo_demo())
    dat_tu_dien(m)
    r = so(m)
    assert r["trang_thai"] == "XONG", r
    r = quet(m, None, r["ket_qua"])
    assert r["trang_thai"] == "XONG", r
    s = m.snapshot(r)
    if any(d["cho_phan_loai"] for d in s["diem_lech"]):
        provider = DieuPhoiDEMO()
        r = hau_kiem(m, provider.hoi(m, chuan_bi(m, r["ket_qua"])))
        assert r["trang_thai"] == "XONG" and provider.cloud == 0
        s = m.snapshot(r)
    # Các điểm dài nhân bản có nhãn DEMO, chỉ để ép phân trang và kiểm glyph.
    diem = deepcopy(s["diem_lech"][0])
    for i in range(4):
        d = deepcopy(diem)
        d["ma_diem"] = f"DEMO-DIEM-DAI-{i+1}"
        d["ly_do_ai"] = ("DEMO: Đối chiếu bản ký Công ty Ánh Dương; tiền 1.000.000 VND, "
                           "ngày 2026-10-30. Thuê/thuế, lãi/lại và ký tự ẮẰẲẴẶ ẾỀỂỄỆ ỚỜỞỠỢ ỨỪỬỮỰ. " * 12)
        s["diem_lech"].append(d)
    pb = ghim_demo(m, s)
    image_pages = []
    original = bc._PDF.anh
    def anh(p, *a, **kw):
        result = original(p, *a, **kw)
        image_pages.append(len(p.pages))
        return result
    with patch.object(bc._PDF, "anh", anh):
        _, out, pdf = doc_kq(m, xuat(m, pb))
    (output/"DEMO-DC9-dai-va-anh.pdf").write_bytes(pdf)
    import pypdfium2 as pdfium
    with pdfium.PdfDocument(pdf) as document:
        page_nos = sorted({0, min(2, len(document)-1), *image_pages})
        for n in page_nos:
            page = document[n]
            try:
                bitmap = page.render(scale=1.5)
                try:
                    with bitmap.to_pil() as im:
                        im.save(output/f"DEMO-trang-{n+1:03d}.png")
                finally:
                    bitmap.close()
            finally:
                page.close()
        print(f"DEMO: {len(document)} trang PDF; đã render trang {[n+1 for n in page_nos]}.")
        print(f"Ảnh cắt ở trang {[n+1 for n in image_pages]}; kết luận {out['ket_luan']}; 0 Cloud.")


if __name__ == "__main__":
    main()
