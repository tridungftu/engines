"""Chạy DEMO bằng CoreGia; Tesseract giả chỉ trong công cụ test này.

Mặc định dùng Tesseract thật nếu có đủ vie+eng. --gia ép nguồn giả cho
CI, vẫn đi qua render PDF, đọc PNG/JPEG, TSV và ba action SDK thật.
"""

from contextlib import ExitStack
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

sys.dont_write_bytecode = True
GOI = Path(__file__).resolve().parents[1] / "goi" / "e_ocr"
sys.path.insert(0, str(GOI))

from PIL import Image
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia, nap_engine_tu_goi

from demo.tao_bo_demo import KICH_THUOC, _phong_chu, _trang
from e_ocr import tesseract


class TesseractGia:
    """TSV đáp án DEMO cố định, không là phép đo độ chính xác OCR."""

    def __init__(self):
        self.lenh = []
        self._stack = ExitStack()

    def __enter__(self):
        self._stack.enter_context(patch.object(tesseract, "tim_tesseract", lambda _: "tesseract-DEMO"))
        self._stack.enter_context(patch.object(tesseract, "_chay", self._chay))
        return self

    def __exit__(self, *args):
        return self._stack.__exit__(*args)

    def _chay(self, lenh, *, viec, **kwargs):
        viec.kiem_huy()
        self.lenh.append(list(lenh))
        if "--list-langs" in lenh:
            return b"List of available languages (2):\neng\nvie\n"
        with Image.open(lenh[1]) as anh:
            rong, cao = anh.size
        so = int(Path(lenh[1]).stem.rsplit("-", 1)[1])
        image, lines = _trang(so)
        image.close()
        sx, sy = rong / KICH_THUOC[0], cao / KICH_THUOC[1]
        text = "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n"
        for i, (x, y, size, chu) in enumerate(lines, 1):
            width = round(_phong_chu(size).getlength(chu) * sx)
            text += (f"5\t1\t1\t1\t{i}\t1\t{round(x*sx)}\t{round(y*sy)}\t"
                     f"{width}\t{round(size*sy)}\t95\t{chu}\n")
        Path(lenh[2]).with_suffix(".tsv").write_text(text, encoding="utf-8")
        return b""


def chay_demo(*, gia=False):
    with TemporaryDirectory(prefix="e-ocr-DEMO-") as tam, ExitStack() as stack:
        # Cách ly cả cấu hình và dữ liệu: không đọc cấu hình OCR của máy.
        stack.enter_context(patch.dict(os.environ, {
            "PROGRAMDATA": tam, "KTT_ENGINE_DU_LIEU": str(Path(tam) / "du-lieu-DEMO"),
            "KTT_ENGINE_CAU_HINH": str(Path(tam) / "khong-co-cau-hinh-DEMO.json"),
        }))
        if not gia:
            try:
                tesseract._kiem_bo_doc({}, SimpleNamespace(kiem_huy=lambda: None))
            except LoiNghiepVu as loi:
                if loi.ma != "NGUON_DU_PHONG_CHUA_CAI":
                    raise
                gia = True
        if gia:
            stack.enter_context(TesseractGia())
            print("Đã kiểm bằng Core giả (CoreGia) + Tesseract giả; không đo độ chính xác OCR.")
        else:
            print("Đã kiểm bằng Core giả (CoreGia) + Tesseract thật (vie+eng); chỉ dữ liệu DEMO.")
        ket_qua = CoreGia().chay_thu_demo(nap_engine_tu_goi(GOI), GOI)
        for kq in ket_qua:
            print(f"[{'ĐẠT' if kq['trang_thai'] == 'XONG' else 'LỖI'}] {kq['ten']}")
        return ket_qua


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gia", action="store_true", help="Ép dùng Tesseract giả cho CI.")
    args = parser.parse_args()
    sys.exit(0 if all(k["trang_thai"] == "XONG" for k in chay_demo(gia=args.gia)) else 1)
