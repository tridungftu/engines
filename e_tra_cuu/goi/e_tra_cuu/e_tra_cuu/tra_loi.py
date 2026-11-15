"""TC-7: hai đường soạn, nhãn do Python quyết; snapshot chỉ giữ tại Core."""

from copy import deepcopy

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .bang_chung import TOM_TAT, doc_ho_so
from .cau_hoi import _THOI_DIEM
from .kiem_chung import LY_DO_CAN_DUYET, cau_tra_loi, co_mau_thuan, kiem_ai, kiem_bang_chung
from .kiem_dau_vao import bam, json_chuan, loi


KHONG_CAN_CU = "Không thấy căn cứ hợp lệ để trả lời. Anh cần bổ sung hoặc duyệt nguồn phù hợp."


def _phu_thuoc(s, profile, bang):
    d = s["du_lieu"]
    thoi_diem = (profile["phu_thuoc_thoi_diem"] or bool(_THOI_DIEM.search(d["cau_hoi"]))
                 or any(x["phu_thuoc_thoi_diem"] for x in d["phu_thuoc_cache"]))
    # Không tự tạo cache. Xuất đủ nguồn kể cả hai phía mâu thuẫn cho Core
    # kiểm quyền/hết hạn theo phiên bản, duyệt, công bố và phạm vi mỗi lần dùng.
    return {"nguon": deepcopy(s["nguon"]), "thuc_the": deepcopy(d["thuc_the"]),
            "ngu_canh_core": deepcopy(s["ngu_canh_core"]), "phu_thuoc_thoi_diem": thoi_diem,
            "co_van_ban_moi_cho_duyet": d["co_van_ban_moi_cho_duyet"],
            "duoc_tai_dung_cache": False if thoi_diem else None,
            "moc_nguon": [{k: deepcopy(b[k]) for k in ("nguon", "thuc_the", "truong", "trang_thai_duyet",
                "moc_cong_bo", "moc_duyet", "hieu_luc_tu", "hieu_luc_den")} for b in bang],
            "phu_thuoc_core": deepcopy(d["phu_thuoc_cache"])}


def soan_tra_loi(viec, cua, phien_ban, kiem_cau_hinh):
    try:
        return _soan_tra_loi(viec, cua, phien_ban, kiem_cau_hinh)
    except LoiNghiepVu as exc:
        if exc.ma == "TC_DAU_VAO_KHONG_HOP_LE":
            loi("TC_SAI_NGUON")
        raise


def _soan_tra_loi(viec, cua, phien_ban, kiem_cau_hinh):
    s, doc, cap, a = doc_ho_so(viec, cua, phien_ban, kiem_cau_hinh)
    bang, ly_do, profile = kiem_bang_chung(s, doc, cap, viec)
    d = s["du_lieu"]
    viec.tien_do(35, "Đang kiểm từng khẳng định, số liệu và vị trí nguồn.")
    # Hồ sơ có đoạn tầng 2/3 không cho caller tự chèn lời văn xin nhãn Xanh.
    if a is None and d["tang"] != 1 and d["bang_chung"]:
        loi("TC_SAI_GIAI_DOAN")
    if a is not None and not kiem_ai(a, s, bang, profile, viec):
        ly_do.append("KHANG_DINH_AI_KHONG_DAT")
    ly_do_chan = [ma for ma in ly_do if d["tang"] == 1 or ma not in LY_DO_CAN_DUYET]
    dat = bool(bang) and not ly_do_chan
    mau_thuan = co_mau_thuan(bang)
    can_duyet = mau_thuan or (dat and (d["tang"] > 1 or d["co_van_ban_moi_cho_duyet"]))
    canh_bao = [cau for ma, cau in LY_DO_CAN_DUYET.items() if ma in ly_do]
    if d["co_van_ban_moi_cho_duyet"]:
        canh_bao.append("Có văn bản mới chờ duyệt; Anh cần kiểm tra bản cập nhật.")
    if mau_thuan:
        canh_bao.append("Các nguồn có giá trị mâu thuẫn; Anh cần duyệt, chưa chọn một nguồn thay nguồn khác.")
    nhan = ("xanh" if a is None and d["tang"] == 1 and not can_duyet else "vang") if dat else None
    khang_dinh = [{k: deepcopy(b[k]) for k in ("thuc_the", "truong", "kieu", "gia_tri", "don_vi", "hien_thi")} |
                  {"can_cu": [{k: deepcopy(b[k]) for k in ("nguon", "cau", "bat_dau", "ket_thuc", "vi_tri",
                    "vi_tri_gia_tri", "moc_cong_bo", "moc_duyet", "trang_thai_duyet")}]} for b in bang] if dat else []
    # Khi phản hồi AI sai, không giữ câu bịa như câu trả lời Vàng. Nếu Core
    # đã cung cấp mâu thuẫn, vẫn giữ cả hai căn cứ hợp lệ riêng để người duyệt xem.
    mau_thuan_core = [{k: deepcopy(b[k]) for k in ("nguon", "thuc_the", "truong", "gia_tri", "don_vi",
                        "cau", "bat_dau", "ket_thuc", "vi_tri")} for b in bang] if mau_thuan else []
    kq = {"trang_thai": "co_can_cu" if dat else "khong_thay_can_cu",
          "tra_loi": cau_tra_loi(bang, profile["truong_can_tra_loi"], mau_thuan) if dat else KHONG_CAN_CU,
          "khang_dinh": khang_dinh, "nhan": nhan, "tang": d["tang"], "co_can_cu": dat,
          "co_mau_thuan": mau_thuan, "mau_thuan": mau_thuan_core, "can_duyet": can_duyet,
          "ly_do": list(dict.fromkeys(ly_do)), "canh_bao": canh_bao,
          "phu_thuoc_cache": _phu_thuoc(s, profile, bang),
          "de_nghi_k5": {"du_lieu_moi": dat and d["tang"] > 1, "co_mau_thuan": mau_thuan,
                         "da_duyet": False, "da_tao_viec": False},
          "ai": {"nha_cung_cap": "local", "model": a["model"], "ma_prompt": a["ma_prompt"],
                 "phien_ban_prompt": a["phien_ban_prompt"], "bam_dau_vao": a["bam_dau_vao"]} if a is not None else None}
    return _luu(viec, s, doc, kq, phien_ban)


def _luu(viec, s, doc, kq, phien_ban):
    s = deepcopy(s)
    s.update(giai_doan="da_soan", ket_qua=kq)
    raw = json_chuan(s)
    if len(raw) > doc.tran["tep_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    tt = dict.fromkeys(TOM_TAT)
    tt.update({k: kq[k] for k in ("trang_thai", "tang", "co_can_cu", "co_mau_thuan", "can_duyet", "nhan")})
    h = {"phien_ban": 1, "ma_yeu_cau": s["ma_yeu_cau"], "tac_vu": "soan_tra_loi", "giai_doan": "da_soan",
         "ho_so": None, "bam_ho_so": bam(raw), "bam_cau_hinh": bam(json_chuan(s["cau_hinh"]["gia_tri"])),
         "bam_danh_muc": None, "phien_ban_engine": "e_tra_cuu " + phien_ban, "tom_tat": tt,
         "canh_bao": kq["canh_bao"]}
    pb = {"loai": "ho_so_tra_cuu", "ho_so_tra_cuu": h}
    if len(json_chuan(pb)) > doc.tran["ho_so_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    viec.tien_do(90, "Đang gửi câu trả lời và căn cứ đã kiểm lên Core.")
    tep = viec.tai_tep_ra("ho-so-tra-loi.json", raw, "application/json")
    viec.tien_do(95, "Đã gửi hồ sơ trả lời, đang kiểm xác nhận và trạng thái việc.")
    viec.kiem_huy()
    doc.kiem_tep(tep, json=True)
    if tep["ten"] != "ho-so-tra-loi.json" or tep["kich_thuoc"] != len(raw):
        loi("TC_SAI_NGUON")
    h["ho_so"] = tep
    if len(json_chuan(pb)) > doc.tran["ho_so_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    return pb
