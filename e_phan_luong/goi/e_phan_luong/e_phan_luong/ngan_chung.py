"""Tiện ích ngăn SDK 2.2.0; không giữ dữ liệu trên máy engine."""

from kho_tri_thuc_sdk.engine import NganXungDot

from .loi import loi


_COT_KHOA = {
    "luot": ("ma_luot",),
    "dong_luot": ("ma_luot", "ma"),
    "ket_qua_kiem": ("ma_luot", "ma", "khau"),
    "ty_le": ("khau", "loai"),
    "ho_so_hanh_vi": ("khau", "loai"),
    "chot_ky": ("ky", "khau", "loai"),
}


def ghi_lo_thu_lai(viec, lap_lenh, *, so_lan_thu_lai=3):
    """Một lần đầu + tối đa ba lần thử lại; trả số lần đã thử lại.

    lap_lenh(lo) phải tự đọc lại bản ghi/CAS trong mỗi lần gọi. Không giữ
    danh sách lệnh hoặc row_version từ lần xung đột trước để gửi lại.
    """
    if type(so_lan_thu_lai) is not int or so_lan_thu_lai < 0:
        raise loi("THAM_SO_KHONG_HOP_LE")
    for lan in range(so_lan_thu_lai + 1):
        viec.kiem_huy()
        try:
            with viec.ngan.lo() as lo:
                lap_lenh(lo)
            return lan
        except NganXungDot:
            if lan == so_lan_thu_lai:
                raise loi("NGAN_BAN") from None


def ghi_lay_hoac_tao_nhieu(viec, bang, ds: list[tuple[dict, dict]]):
    """Chia tối đa 100 lệnh/lô; nguyên tử từng lô, không phải cả ds.

    Gửi lại an toàn nhờ lay_hoac_tao; nếu một lô sau lỗi, những lô trước
    đã ghi vẫn tồn tại. Hàm không sửa danh sách hay dữ liệu đầu vào.
    """
    for dau in range(0, len(ds), 100):
        nhom = ds[dau:dau + 100]

        def lap_lenh(lo):
            for khoa, gia_tri in nhom:
                lo.lay_hoac_tao(bang, khoa, gia_tri)

        ghi_lo_thu_lai(viec, lap_lenh)


def tim_tat_ca(viec, bang, loc, *, gioi_han=500, toi_da=200000):
    """Duyệt hết trang theo các cột khóa duy nhất; vượt trần thì từ chối."""
    if (type(gioi_han) is not int or not 1 <= gioi_han <= 500
            or type(toi_da) is not int or toi_da < 0 or bang not in _COT_KHOA):
        raise loi("THAM_SO_KHONG_HOP_LE")
    sap_xep = [{"truong": cot, "giam": False} for cot in _COT_KHOA[bang]]
    ds = []
    tiep = None
    da_gap = set()
    while True:
        viec.kiem_huy()
        trang = viec.ngan.tim(bang, loc=loc, sap_xep=sap_xep, gioi_han=gioi_han, tiep=tiep)
        if len(ds) + len(trang.danh_sach) > toi_da:
            raise loi("VUOT_GIOI_HAN")
        ds.extend(trang.danh_sach)
        tiep = trang.tiep
        if tiep is None:
            return ds
        if tiep in da_gap:
            raise loi("NGAN_BAN")
        da_gap.add(tiep)
