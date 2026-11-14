"""Cổng SDK 2.0: hai action đọc dùng chung lõi; xuất Word thuộc OCR-3."""

from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu

from .van_ban import trich_van_ban


app = Engine.tu_khai_bao("engine.json")


@app.nang_luc("ocr.doc_tai_lieu@1")
def doc_tai_lieu(viec):
    du_lieu = trich_van_ban(viec, phien_ban_engine=f"{app.ma} {app.phieu['phien_ban']}")
    return {"loai": "van_ban_tai_lieu", "van_ban_tai_lieu": du_lieu}


@app.nang_luc("ocr.doc_van_ban@1")
def doc_van_ban(viec):
    du_lieu = trich_van_ban(viec, phien_ban_engine=f"{app.ma} {app.phieu['phien_ban']}")
    return {"loai": "van_ban", "van_ban": du_lieu["van_ban"]}


@app.nang_luc("ocr.xuat_word@1")
def xuat_word(viec):
    raise LoiNghiepVu(
        "CHUA_LAM", "Chức năng xuất Word chưa được triển khai."
    )


if __name__ == "__main__":
    app.chay()
