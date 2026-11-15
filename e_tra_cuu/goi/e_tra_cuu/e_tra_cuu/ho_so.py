"""TC-2: snapshot bất biến trong kho Core, phong bì chỉ mang tham chiếu."""

from .kiem_dau_vao import DocNguonCore, bam, json_chuan, kiem_du_lieu, loi


def nhan_yeu_cau(viec, cau_hinh, cua_nguon, phien_ban_engine):
    try:
        return _nhan_yeu_cau(viec, cau_hinh, cua_nguon, phien_ban_engine)
    except (ValueError, TypeError, KeyError, AttributeError, RecursionError, OverflowError):
        # Dữ liệu sai kiểu/lồng sâu không được lọt vào traceback SDK 2.0.
        # Hủy, mất lease, ChuaRo và lỗi đường truyền vẫn do SDK sở hữu.
        loi()


def _nhan_yeu_cau(viec, cau_hinh, cua_nguon, phien_ban_engine):
    viec.kiem_huy()
    doc = DocNguonCore(viec, cau_hinh["gia_tri"]["ngan_sach"])
    yeu_cau = doc.yeu_cau(cua_nguon)
    viec.tien_do(10, "Đang kiểm nguồn và phạm vi tra cứu.")
    du_lieu = kiem_du_lieu(doc, yeu_cau)
    snapshot = {
        "phien_ban": 1,
        "ma_yeu_cau": yeu_cau["ma_yeu_cau"],
        "tac_vu": yeu_cau["tac_vu"],
        "giai_doan": "da_nhan",
        "ngu_canh_core": yeu_cau["ngu_canh_core"],
        "cau_hinh": cau_hinh,
        "nguon": list(doc.nguon.values()),
        "du_lieu": du_lieu,
        "ket_qua": None,
    }
    noi_dung = json_chuan(snapshot)
    if len(noi_dung) > doc.tran["tep_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    tom_tat = dict.fromkeys(("trang_thai", "so_doan", "so_ung_vien", "tang",
                             "co_can_cu", "co_mau_thuan", "can_duyet", "nhan"))
    if yeu_cau["tac_vu"] == "xep_hang_lai":
        tom_tat["so_ung_vien"] = len(du_lieu["ung_vien"])
    if yeu_cau["tac_vu"] == "soan_tra_loi":
        tom_tat["tang"] = du_lieu["tang"]
    ho_so = {
        "phien_ban": 1, "ma_yeu_cau": yeu_cau["ma_yeu_cau"],
        "tac_vu": yeu_cau["tac_vu"], "giai_doan": "da_nhan",
        "ho_so": None, "bam_ho_so": bam(noi_dung),
        "bam_cau_hinh": bam(json_chuan(cau_hinh["gia_tri"])),
        "bam_danh_muc": (bam(json_chuan(du_lieu["danh_muc"]))
                         if du_lieu.get("danh_muc") is not None else None),
        "phien_ban_engine": "e_tra_cuu " + phien_ban_engine,
        "tom_tat": tom_tat, "canh_bao": [],
    }
    # Kiểm trần trước upload, kể cả mã opaque dài. Không tải rồi mới phát hiện
    # phong bì chắc chắn quá trần; kiểm lại metadata thực sau xác nhận Core.
    if len(json_chuan({"loai": "ho_so_tra_cuu", "ho_so_tra_cuu": ho_so})) > doc.tran["ho_so_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    viec.tien_do(90, "Đang gửi hồ sơ đã kiểm lên Core.")
    tep = viec.tai_tep_ra("ho-so-tra-cuu.json", noi_dung, "application/json")
    viec.kiem_huy()
    doc.kiem_tep(tep, json=True)
    if tep["kich_thuoc"] != len(noi_dung) or tep["ten"] != "ho-so-tra-cuu.json":
        loi("TC_SAI_NGUON")
    ho_so["ho_so"] = tep
    phong_bi = {"loai": "ho_so_tra_cuu", "ho_so_tra_cuu": ho_so}
    if len(json_chuan(phong_bi)) > doc.tran["ho_so_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    return phong_bi
