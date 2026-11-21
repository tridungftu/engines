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
    """Lô JSON (PL-6 thêm Excel/CSV): lớp 1/2/3, tệp kết quả, dấu hoàn tất trong Core."""
    from . import quy_trinh

    quy_trinh.bat_dau(viec)
    lo, du_lieu = quy_trinh.doc_tep_lo(viec)
    return {"loai": "truong", "truong": quy_trinh.chay_phan_luong(viec, lo, du_lieu)}


@app.nang_luc("audit.chuan_bi_phan_loai@1")
def chuan_bi_phan_loai(viec):
    from . import ngan_chuoi, quy_trinh

    quy_trinh.bat_dau(viec)
    lo, du_lieu = quy_trinh.doc_tep_lo(viec)
    cd = quy_trinh.doc_cai_dat(viec.tham_so, lo)
    return ngan_chuoi.chuan_bi(viec, lo, du_lieu, cd)


@app.nang_luc("audit.phan_luong_sau_ai@1")
def phan_luong_sau_ai(viec):
    from . import ngan_chuoi, quy_trinh

    quy_trinh.bat_dau(viec)
    return {"loai": "truong", "truong": ngan_chuoi.phan_luong_sau_ai(viec)}


@app.nang_luc("audit.phan_luong_hoa_don@1")
def phan_luong_hoa_don(viec):
    import json

    from . import doc_lo, hoa_don, quy_trinh
    from .loi import loi

    quy_trinh.bat_dau(viec)
    truong = viec.dau_vao["truong"]
    if not isinstance(truong, dict):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    ts = viec.tham_so
    tham_so_lo = {"ma_module": ts.get("ma_module"),
                  "loai_nghiep_vu": ts.get("loai_nghiep_vu") or None}
    so_bo = 0
    # doc_xml cũng có chi_tiet_nguon, nhưng đó là DTO XML, không phải
    # kiểm kê ZIP. Phiếu §5.4 dùng bộ trường của XML cho một nghiệp vụ.
    if (truong.get("nguon_doc") != "xml_strict"
            and (truong.get("nguon_doc") == "zip_xml_strict"
                 or truong.get("chi_tiet_nguon") is not None)):
        tep = hoa_don.lay_tep_chi_tiet(truong)
        with viec.mo_tep(tep["tep_id"]) as luong:
            du_lieu = luong.read(doc_lo.TOI_DA_BYTE + 1)
        lo, so_bo = hoa_don.lo_tu_chi_tiet_zip(du_lieu, **tham_so_lo)
    else:
        lo = hoa_don.lo_tu_hoa_don(truong, **tham_so_lo)
        try:
            du_lieu = json.dumps(truong, sort_keys=True, separators=(",", ":"),
                                 ensure_ascii=False, allow_nan=False).encode("utf-8")
        except (TypeError, ValueError, UnicodeError, RecursionError):
            raise loi("DU_LIEU_KHONG_HOP_LE") from None
        if len(du_lieu) > doc_lo.TOI_DA_BYTE:
            raise loi("VUOT_GIOI_HAN")
    canh_bao = [f"Bỏ {so_bo} hóa đơn không đọc được"] if so_bo else []
    return {"loai": "truong", "truong": quy_trinh.chay_phan_luong(
        viec, lo, du_lieu, canh_bao_them=canh_bao)}


@app.nang_luc("audit.ghi_ket_qua@1")
def ghi_ket_qua(viec):
    import json

    from . import __version__, ket_qua, ngan_ket_qua, quy_trinh

    viec.tien_do(5, "Đang đọc kết quả kiểm.")
    with viec.mo_tep(viec.dau_vao["tep"]["tep_id"]) as tep:
        du_lieu = tep.read(ket_qua.TOI_DA_BYTE + 1)
    noi_dung = ket_qua.doc_ket_qua_json(du_lieu)
    bai_hoc = []
    dem = ngan_ket_qua.ghi_ket_qua(
        viec, noi_dung, bai_hoc=bai_hoc, truoc_ghi=lambda: quy_trinh.bat_dau(viec))
    tep_bai_hoc = None
    if bai_hoc:
        # C4: giải thích chỉ đi từ tệp đầu vào qua RAM sang tệp của Core.
        # Tải lỗi để SDK báo lỗi thân thiện như phân luồng; gửi lại cả tệp
        # vẫn lấy đủ bài học mà không cộng thống kê các lô đã ghi lần nữa.
        du_lieu_bai_hoc = json.dumps({
            "phien_ban": 1, "ma_module": noi_dung.ma_module,
            "khau": viec.tham_so["khau"], "phien_ban_engine": __version__, "dong": bai_hoc,
        }, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
        tep_bai_hoc = viec.tai_tep_ra("bai-hoc-ai.json", du_lieu_bai_hoc, "application/json")
    return {"loai": "truong", "truong": {
        **dem, "so_ai_sai": len(bai_hoc), "tep_bai_hoc": tep_bai_hoc,
        "phien_ban_engine": __version__,
    }}


if __name__ == "__main__":
    app.chay()
