"""Khung SDK; n?ng l?c ??c Word ch?a ???c tri?n khai."""
import json
from pathlib import Path

from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu
from .ngan import NganBoNho, chon_ngan
from .cau_hinh import CauHinhKhongHopLe, doc_cau_hinh

_GOI = Path(__file__).resolve().parent.parent
app = Engine.tu_khai_bao(str(_GOI / "engine.json"))
_khai = json.loads((_GOI / "KHAI-SDK-2.1.json").read_text(encoding="utf-8"))
_schema = json.loads((_GOI / "cau_hinh.schema.json").read_text(encoding="utf-8"))
if getattr(app, "ngan", None) is None:
    app.ngan = NganBoNho(_khai["ngan_du_lieu"])
ngan = chon_ngan(app)


def can_cau_hinh():
    """D?ng cho c?c vi?c c?n c?u h?nh trong nh?ng l?t ti?p theo."""
    try:
        cau_hinh = doc_cau_hinh(ngan, _schema)
    except CauHinhKhongHopLe as exc:
        raise LoiNghiepVu(exc.ma, exc.thong_diep, thu_lai_duoc=exc.thu_lai_duoc) from None
    if cau_hinh is None:
        raise LoiNghiepVu("CHUA_CAU_HINH", "Engine ch?a ???c c?u h?nh. Admin v?o Qu?n l? engine ? ??i chi?u b?n k? ? C?u h?nh.")
    return cau_hinh


@app.nang_luc("doi_chieu.doc_docx@1")
def doc_docx(viec):
    raise LoiNghiepVu("CHUA_LAM", "Ch?c n?ng ??c b?n Word ?ang ???c ho?n thi?n.")


if __name__ == "__main__":
    app.chay()
