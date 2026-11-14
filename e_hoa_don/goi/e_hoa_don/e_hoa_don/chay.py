"""Cổng SDK cho một XML; bàn giao tệp chi tiết trước khi trả bộ trường."""

from kho_tri_thuc_sdk.engine import Engine, LoiDuongTruyen, LoiNghiepVu

from .doc import JSON_TOI_DA_BYTE, doc_xml
from .hoa_don_xml import MAX_XML_BYTES


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


if __name__ == "__main__":
    app.chay()
