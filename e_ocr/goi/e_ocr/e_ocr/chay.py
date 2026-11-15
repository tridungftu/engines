"""Cổng SDK 2.0: ba action đọc/xuất Word dùng chung lõi nhận dạng."""

from kho_tri_thuc_sdk.engine import Engine

from .ban_giao import ban_giao_word
from .nhat_ky import do_luot, ghi_nguon
from .van_ban import trich_van_ban


app = Engine.tu_khai_bao("engine.json")


def _doc(viec):
    du_lieu = trich_van_ban(viec, phien_ban_engine=f"{app.ma} {app.phieu['phien_ban']}")
    ghi_nguon(du_lieu.get("nguon_doc"))
    return du_lieu


@app.nang_luc("ocr.doc_tai_lieu@1")
@do_luot
def doc_tai_lieu(viec):
    du_lieu = _doc(viec)
    return {"loai": "van_ban_tai_lieu", "van_ban_tai_lieu": du_lieu}


@app.nang_luc("ocr.doc_van_ban@1")
@do_luot
def doc_van_ban(viec):
    du_lieu = _doc(viec)
    return {"loai": "van_ban", "van_ban": du_lieu["van_ban"]}


@app.nang_luc("ocr.xuat_word@1")
@do_luot
def xuat_word(viec):
    du_lieu = _doc(viec)
    return ban_giao_word(viec, du_lieu)


if __name__ == "__main__":
    app.chay()
