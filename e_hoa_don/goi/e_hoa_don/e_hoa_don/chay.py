"""Cổng SDK cho một XML; bàn giao tệp chi tiết trước khi trả bộ trường."""

from kho_tri_thuc_sdk.engine import Engine, LoiDuongTruyen, LoiNghiepVu

from .doc import JSON_TOI_DA_BYTE, doc_xml
from .hoa_don_xml import MAX_XML_BYTES
from .zip import CAU_VUOT_TRAN, ZIP_TOI_DA_BYTE, doc_zip
from .bang_ke import lap_bang_ke


if not callable(getattr(Engine, "_ghi", None)):
    raise RuntimeError("SDK không có hook nhật ký cần thiết; không thể khởi động an toàn.")


class CongHoaDon(Engine):
    """Bọc nhật ký SDK 2.0.0 tới khi SDK có hook nhật ký an toàn công khai.

    SDK có thể đưa traceback/nội dung exception vào câu nhật ký. Không chép
    câu đó ra stderr; lỗi chuẩn vẫn do SDK gửi Core, không đổi luồng điều khiển.
    """

    def _ghi(self, cau):
        super()._ghi("HD_SDK_THONG_BAO")


app = CongHoaDon.tu_khai_bao("engine.json")


@app.nang_luc("hoa_don.doc_xml@2")
def doc_hoa_don(viec):
    tep = viec.dau_vao["tep"]
    viec.kiem_huy()
    viec.tien_do(10, "Đang đọc XML hóa đơn.")
    try:
        with viec.mo_tep(tep["tep_id"]) as luong:
            du_lieu = luong.read(MAX_XML_BYTES + 1)
    except (LoiDuongTruyen, LoiNghiepVu) as loi:
        if not (
            isinstance(loi, LoiDuongTruyen) and loi.ma == "VUOT_GIOI_HAN_KICH_THUOC"
            or isinstance(loi, LoiNghiepVu) and loi.ma == "VUOT_GIOI_HAN"
        ):
            raise
        raise LoiNghiepVu(
            "HD_XML_QUA_LON",
            "Tệp XML vượt giới hạn 16 MiB. Anh hãy gửi tệp nhỏ hơn.",
        ) from None
    if len(du_lieu) > MAX_XML_BYTES:
        raise LoiNghiepVu(
            "HD_XML_QUA_LON",
            "Tệp XML vượt giới hạn 16 MiB. Anh hãy gửi tệp nhỏ hơn.",
        )
    viec.kiem_huy()
    truong, bao_cao = doc_xml(du_lieu, tep_xml=tep)
    viec.kiem_huy()
    viec.tien_do(60, "Đã đọc cấu trúc XML hóa đơn.")
    if len(bao_cao) > JSON_TOI_DA_BYTE:
        raise LoiNghiepVu(
            "HD_KET_QUA_QUA_LON",
            "Kết quả đọc hóa đơn vượt giới hạn. Anh hãy chia nhỏ dữ liệu đầu vào.",
        )
    viec.kiem_huy()
    viec.tien_do(80, "Đang lưu chi tiết nguồn hóa đơn.")
    truong["chi_tiet_nguon"] = viec.tai_tep_ra(
        "hoa-don-chi-tiet.json", bao_cao, "application/json"
    )
    viec.tien_do(100, "Đã đọc XML hóa đơn; cần kiểm tra kết quả nguồn.")
    viec.kiem_huy()
    return {"loai": "truong", "truong": truong}


@app.nang_luc("hoa_don.doc_zip@1")
def doc_hoa_don_zip(viec):
    tep = viec.dau_vao["tep"]
    viec.kiem_huy()
    viec.tien_do(10, "Đang đọc gói ZIP hóa đơn.")
    try:
        with viec.mo_tep(tep["tep_id"]) as luong:
            # Không tin kích thước metadata, kể cả nguồn trả các khối ngắn.
            raw = bytearray()
            while len(raw) <= ZIP_TOI_DA_BYTE:
                viec.kiem_huy()
                chunk = luong.read(min(64 * 1024, ZIP_TOI_DA_BYTE + 1 - len(raw)))
                if not chunk:
                    break
                raw.extend(chunk)
    except (LoiDuongTruyen, LoiNghiepVu) as loi:
        if not (
            isinstance(loi, LoiDuongTruyen) and loi.ma == "VUOT_GIOI_HAN_KICH_THUOC"
            or isinstance(loi, LoiNghiepVu) and loi.ma == "VUOT_GIOI_HAN"
        ):
            raise
        raise LoiNghiepVu("HD_ZIP_VUOT_GIOI_HAN", CAU_VUOT_TRAN) from None
    if len(raw) > ZIP_TOI_DA_BYTE:
        raise LoiNghiepVu("HD_ZIP_VUOT_GIOI_HAN", CAU_VUOT_TRAN)
    viec.kiem_huy()
    truong, bao_cao = doc_zip(bytes(raw), tep_zip=tep, kiem_huy=viec.kiem_huy)
    viec.tien_do(60, "Đã kiểm kê gói ZIP hóa đơn; kết quả cần kiểm tra.")
    viec.kiem_huy()
    viec.tien_do(80, "Đang lưu báo cáo kiểm kê gói ZIP.")
    viec.kiem_huy()
    truong["chi_tiet_nguon"] = viec.tai_tep_ra(
        "hoa-don-goi-chi-tiet.json", bao_cao, "application/json"
    )
    viec.tien_do(100, "Đã trả báo cáo gói ZIP; cần kiểm tra kết quả nguồn.")
    viec.kiem_huy()
    return {"loai": "truong", "truong": truong}


@app.nang_luc("hoa_don.bang_ke_xlsx@1")
def bang_ke_hoa_don(viec):
    return lap_bang_ke(viec)


if __name__ == "__main__":
    app.chay()
