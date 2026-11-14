"""Ba năng lực OCR đã khai cổng; phần xử lý thuộc các lát sau OCR-0."""

from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu


app = Engine.tu_khai_bao("engine.json")


@app.nang_luc("ocr.doc_tai_lieu@1")
def doc_tai_lieu(viec):
    raise LoiNghiepVu(
        "CHUA_LAM", "Chức năng đọc tài liệu có vị trí chưa được triển khai."
    )


@app.nang_luc("ocr.doc_van_ban@1")
def doc_van_ban(viec):
    raise LoiNghiepVu(
        "CHUA_LAM", "Chức năng đọc văn bản chưa được triển khai."
    )


@app.nang_luc("ocr.xuat_word@1")
def xuat_word(viec):
    raise LoiNghiepVu(
        "CHUA_LAM", "Chức năng xuất Word chưa được triển khai."
    )


if __name__ == "__main__":
    app.chay()
