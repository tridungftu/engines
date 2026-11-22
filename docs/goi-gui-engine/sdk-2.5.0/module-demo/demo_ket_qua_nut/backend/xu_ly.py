"""Lưu liên kết đợt–việc, đọc JSON kết quả qua SDK và ghi ngăn riêng."""
import json
from uuid import UUID

NGAN = "ket_qua"
DOT = ("DEMO-01", "DEMO-02", "DEMO-03")
COT = ("id", "dot_demo", "viec_id", "trang_thai", "so_dong", "so_tu",
       "dong_dau", "thong_diep", "ma_loi", "tep_ket_qua")


class LoiNghiepVu(Exception):
    def __init__(self, ma):
        self.ma = ma
        super().__init__(ma)


def _ra(dong):
    return {k: str(dong[k]) if k in ("id", "viec_id") and dong.get(k) is not None
            else dong.get(k) for k in COT}


def danh_sach(sdk, yeu_cau=None):
    ngan, dong, con_tro = sdk.ngan(NGAN), [], None
    while True:
        trang = ngan.doc({"da_luu_tru": False}, gioi_han=200, con_tro=con_tro)
        dong.extend(_ra(d) for d in trang["danh_sach"])
        con_tro = trang.get("con_tro_tiep")
        if not con_tro:
            return {"dot_demo": list(DOT), "danh_sach": dong}


def _tim_viec(ngan, viec_id):
    return ngan.doc({"viec_id": viec_id, "da_luu_tru": False},
                    gioi_han=2, con_tro=None)["danh_sach"]


def _loi(ngan, dong, ma, thong_diep):
    return ngan.sua(str(dong["id"]), {"trang_thai": "LOI", "ma_loi": ma,
                    "thong_diep": thong_diep, "so_dong": None,
                    "so_tu": None, "dong_dau": None})


# Lỗi không tự hết khi Core giao lại sự kiện; các lỗi khác (tạm thời) thì ném ra.
LOI_VINH_VIEN = frozenset({"KHONG_TIM_THAY", "VUOT_GIOI_HAN_KICH_THUOC", "PHAN_HOI_SAI_CONTRACT"})


def _nhan_ket_qua(sdk, dong, *, cho_chua_xong=False):
    ngan, viec_id = sdk.ngan(NGAN), str(dong["viec_id"])
    try:
        cac_tep = sdk.ket_qua.ds_tep(viec_id)
    except Exception as exc:
        # Lúc vừa lưu liên kết, việc có thể còn trong hàng chờ.
        if cho_chua_xong and getattr(exc, "ma", None) == "KHONG_TIM_THAY":
            return dong
        if getattr(exc, "ma", None) not in LOI_VINH_VIEN:
            raise
        return _loi(ngan, dong, "KET_QUA_KHONG_DOC_DUOC",
                    "Chưa đọc được tệp kết quả. Hãy liên hệ người quản trị.")
    tep_json = [t for t in cac_tep if t.get("mime") == "application/json"
                and t.get("ten") == "ket-qua.json"]
    if len(tep_json) != 1:
        return _loi(ngan, dong, "KET_QUA_THIEU_TEP",
                    "Không nhận được một tệp thống kê kết quả hợp lệ.")
    try:
        noi_dung = sdk.ket_qua.doc_tep(viec_id, tep_json[0]["tep_id"])
    except Exception as exc:
        if getattr(exc, "ma", None) not in LOI_VINH_VIEN:
            raise
        return _loi(ngan, dong, "KET_QUA_KHONG_DOC_DUOC",
                    "Chưa đọc được tệp kết quả. Hãy liên hệ người quản trị.")
    try:
        ket_qua = json.loads(noi_dung.decode("utf-8-sig"))
        if (not isinstance(ket_qua, dict)
                or set(ket_qua) != {"so_dong", "so_tu", "dong_dau"}
                or any(type(ket_qua[k]) is not int or ket_qua[k] < 0
                       for k in ("so_dong", "so_tu"))
                or not isinstance(ket_qua["dong_dau"], str)
                or "\0" in ket_qua["dong_dau"]
                or len(ket_qua["dong_dau"]) > 1_000_000):
            raise ValueError("Kết quả không đúng mẫu.")
    except (UnicodeError, ValueError):
        return _loi(ngan, dong, "KET_QUA_SAI_NOI_DUNG",
                    "Không đọc được thống kê trong tệp kết quả. Hãy kiểm tra lại quy trình.")
    return ngan.sua(str(dong["id"]), dict(ket_qua, trang_thai="XONG", tep_ket_qua=tep_json[0]["tep_id"],
                    thong_diep="Đã nhận kết quả.", ma_loi=None))


def ghi_viec(sdk, yeu_cau):
    than = yeu_cau.get("than") or {}
    try:
        viec_id = str(UUID(than.get("viec_id")))
    except (ValueError, TypeError, AttributeError):
        raise LoiNghiepVu("VIEC_KHONG_HOP_LE") from None
    if than.get("dot_demo") not in DOT:
        raise LoiNghiepVu("DOT_KHONG_HOP_LE")
    ngan = sdk.ngan(NGAN)
    cu = _tim_viec(ngan, viec_id)
    if cu and (len(cu) != 1 or cu[0]["dot_demo"] != than["dot_demo"]):
        raise LoiNghiepVu("VIEC_DA_GAN")
    dong = cu[0] if cu else ngan.them({"dot_demo": than["dot_demo"], "viec_id": viec_id,
                "trang_thai": "DA_GUI", "thong_diep": "Đã gửi, đang chờ kết quả."})
    # Đọc ngay sau khi lưu: vẫn nhận được kết quả nếu sự kiện về trước liên kết.
    if dong["trang_thai"] == "DA_GUI":
        dong = _nhan_ket_qua(sdk, dong, cho_chua_xong=True)
    return _ra(dong)


def nhan_quy_trinh_xong(sdk, su_kien):
    viec_id = str(su_kien["viec_id"])
    dong = _tim_viec(sdk.ngan(NGAN), viec_id)
    if len(dong) != 1:
        raise LoiNghiepVu("VIEC_CHUA_GAN")
    if dong[0]["trang_thai"] == "XONG":
        return _ra(dong[0])
    return _ra(_nhan_ket_qua(sdk, dong[0]))


def nhan_quy_trinh_loi(sdk, su_kien):
    ngan = sdk.ngan(NGAN)
    dong = _tim_viec(ngan, str(su_kien["viec_id"]))
    if len(dong) != 1:
        # Chưa lưu liên kết: chưa nhận, để Core giao lại thông báo có giới hạn.
        raise LoiNghiepVu("VIEC_CHUA_GAN")
    return _ra(_loi(ngan, dong[0], su_kien["ma_loi"], su_kien["thong_diep"]))


XU_LY = {"danh_sach": danh_sach, "ghi_viec": ghi_viec}
SU_KIEN = {"quy_trinh.xong": nhan_quy_trinh_xong, "quy_trinh.loi": nhan_quy_trinh_loi}
