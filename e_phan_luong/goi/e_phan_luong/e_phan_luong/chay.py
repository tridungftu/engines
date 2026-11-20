"""Cổng SDK PL-0; các năng lực chưa triển khai đều từ chối rõ ràng."""

from kho_tri_thuc_sdk.engine import Engine as EngineSDK, LoiNghiepVu


if not callable(getattr(EngineSDK, "_ghi", None)):
    raise RuntimeError("SDK thiếu cổng nhật ký cần thiết để khởi động an toàn.")


class Engine(EngineSDK):
    """Theo mẫu e_kiem_excel: nhật ký SDK chỉ chứa mã cố định."""

    def _ghi(self, cau):
        super()._ghi("PL_SDK_THONG_BAO")


app = Engine.tu_khai_bao("engine.json")


@app.nang_luc("audit.phan_luong@1")
def phan_luong(viec):
    """PL-2: lô JSON, lớp 1/2/3, tệp kết quả và dấu hoàn tất trong Core."""
    from decimal import Decimal
    from hashlib import sha256

    from . import __version__, chon_mau, ngan_luot
    from .doc_lo import doc_lo_json
    from .loi import loi
    from .nguong import doc_nguong
    from .phan_loai import doc_bo_phan_loai, doc_danh_muc_loai
    from .phan_luong import xet_lop1_lo, xet_lop23_lo
    from .ty_le import doc_chinh_sach
    from .xuat_json import tao_tep_json, tao_truong_ra

    tep = viec.dau_vao["tep"]
    ten, mime = tep.get("ten", "").lower(), tep.get("mime", "").lower()
    if (ten.endswith((".xlsx", ".xls", ".csv"))
            or mime in {"text/csv", "application/vnd.ms-excel",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
            or not (ten.endswith(".json") or mime == "application/json")):
        raise loi("TEP_KHONG_HO_TRO")
    with viec.mo_tep(tep["tep_id"]) as f:
        du_lieu = f.read()
    viec.tien_do(10, "Đang kiểm tra lô nghiệp vụ.")
    lo = doc_lo_json(du_lieu)
    ts = viec.tham_so
    ng = doc_nguong(lo.nguong, ts.get("nguong_json"))
    danh_muc = doc_danh_muc_loai(ts.get("danh_muc_loai_json"))
    bo = doc_bo_phan_loai(ts.get("bo_phan_loai_json"), danh_muc)
    duoi_sad = ts.get("ty_le_duoi_sad")
    if duoi_sad is not None:
        # Cổng SDK trả số JSON bằng float; đổi qua chuỗi, không Decimal(float).
        if isinstance(duoi_sad, bool) or not isinstance(duoi_sad, (int, float, Decimal)):
            raise loi("THAM_SO_KHONG_HOP_LE")
        duoi_sad = Decimal(str(duoi_sad))
    cs = doc_chinh_sach(ts.get("chinh_sach_json"), ty_le_duoi_sad=duoi_sad)
    ds_lop1 = xet_lop1_lo(lo, ts, nguong=ng, danh_muc=danh_muc, bo=bo,
                          truong_phan_loai=ts.get("truong_phan_loai"))
    hat_giong = chon_mau.sinh_hat_giong()
    bam_dau_vao = "sha256:" + sha256(du_lieu).hexdigest()
    # Hạt giống mới tạo lượt mới; ghim hạt giống + đầu vào tái hiện cả mã lượt.
    ma_luot = "PL-" + sha256(b"\x1f".join((
        hat_giong, lo.ma_module.encode("utf-8"), ts["khau"].encode("utf-8"),
        bam_dau_vao.encode("ascii"),
    ))).hexdigest()
    thong_tin = {
        "ma_luot": ma_luot, "bam_hat_giong": chon_mau.bam_hat_giong(hat_giong),
        "bam_dau_vao": bam_dau_vao, "phien_ban_engine": __version__,
        "khau": ts["khau"], "ma_module": lo.ma_module,
    }
    viec.tien_do(50, "Đang chọn mẫu kiểm tra.")
    ds_dong = xet_lop23_lo(viec, lo, ds_lop1, khau=ts["khau"], cs=cs, hat_giong=hat_giong)
    noi_dung = tao_tep_json(ds_dong, thong_tin=thong_tin)
    tep_json = viec.tai_tep_ra("phan-luong.json", noi_dung, "application/json")
    truong = tao_truong_ra(lo, ng, ds_dong, thong_tin=thong_tin, tep_json=tep_json)
    viec.tien_do(90, "Đang ghi kết quả lượt phân luồng.")
    ngan_luot.ghi_luot(viec, {
        "ma_luot": ma_luot, "ma_module": lo.ma_module, "khau": ts["khau"],
        "hat_giong": hat_giong.hex(), "bam_dau_vao": bam_dau_vao,
    }, ds_dong)
    return {"loai": "truong", "truong": truong}


@app.nang_luc("audit.chuan_bi_phan_loai@1")
def chuan_bi_phan_loai(viec):
    raise LoiNghiepVu("CHUA_LAM", "Năng lực đang được xây dựng.")


@app.nang_luc("audit.phan_luong_sau_ai@1")
def phan_luong_sau_ai(viec):
    raise LoiNghiepVu("CHUA_LAM", "Năng lực đang được xây dựng.")


@app.nang_luc("audit.phan_luong_hoa_don@1")
def phan_luong_hoa_don(viec):
    raise LoiNghiepVu("CHUA_LAM", "Năng lực đang được xây dựng.")


@app.nang_luc("audit.ghi_ket_qua@1")
def ghi_ket_qua(viec):
    from . import __version__, ket_qua, ngan_ket_qua

    viec.tien_do(5, "Đang đọc kết quả kiểm.")
    with viec.mo_tep(viec.dau_vao["tep"]["tep_id"]) as tep:
        du_lieu = tep.read(ket_qua.TOI_DA_BYTE + 1)
    noi_dung = ket_qua.doc_ket_qua_json(du_lieu)
    dem = ngan_ket_qua.ghi_ket_qua(viec, noi_dung)
    return {"loai": "truong", "truong": {**dem, "phien_ban_engine": __version__}}


if __name__ == "__main__":
    app.chay()
