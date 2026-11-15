"""TC-6: điểm chỉ sắp thứ tự, giữ nguyên mọi ứng viên/nguồn Core đã cấp."""

from copy import deepcopy

from .cau_hoi import (_THOI_DIEM, doc_phan_hoi, khop_khuon, luu_ket_qua, phu_thuoc,
                      sai_khuon)
from .kiem_dau_vao import loi


def xep_hang_lai(viec, cua_nguon, phien_ban_engine, kiem_cau_hinh):
    s, doc, cap, a = doc_phan_hoi(viec, cua_nguon, phien_ban_engine, kiem_cau_hinh, "xep_hang_lai")
    ung_vien = s["du_lieu"]["ung_vien"]
    if not ung_vien:
        # Core phải rẽ nhánh từ hồ sơ da_nhan; không tạo phản hồi Local giả.
        loi("TC_SAI_GIAI_DOAN")
    if len(ung_vien) > 50:
        loi("TC_QUA_GIOI_HAN")
    d = a["du_lieu"]
    if not khop_khuon(d, s["ai"]["khuon_tra_loi"], kiem_huy=viec.kiem_huy):
        sai_khuon()
    ds = d["xep_hang"]
    cac_ma = [x["ma_ung_vien"] for x in ds]
    if len(cac_ma) != len(set(cac_ma)) or set(cac_ma) != {x["ma_ung_vien"] for x in ung_vien}:
        sai_khuon()
    diem = {x["ma_ung_vien"]: x["diem"] for x in ds}
    # Cùng điểm giữ thứ tự tập gốc Core, độc lập thứ tự model gửi lại.
    chi_so = {x["ma_ung_vien"]: i for i, x in enumerate(ung_vien)}
    xep_hang = []
    for uv in sorted(ung_vien, key=lambda x: (-diem[x["ma_ung_vien"]], chi_so[x["ma_ung_vien"]])):
        viec.kiem_huy()
        xep_hang.append({**deepcopy(uv), "diem_xep_hang": diem[uv["ma_ung_vien"]]})
    # Phụ thuộc thời điểm cũng được Core ghim khi chuyển phân tích sang tìm lai.
    td = cap.get("phu_thuoc_thoi_diem")
    if type(td) is not bool:
        loi("TC_CHUA_CO_CUA_CORE")
    td = td or bool(_THOI_DIEM.search(s["du_lieu"]["cau_hoi"]))
    kq = {"xep_hang": xep_hang, "thuc_the": deepcopy(s["du_lieu"]["thuc_the"]),
          "thang_diem": deepcopy(s["du_lieu"]["thang_diem"]), "diem_chi_de_sap_xep": True,
          "phu_thuoc_cache": phu_thuoc(s, s["du_lieu"]["thuc_the"], td)}
    return luu_ket_qua(viec, s, doc, kq, "da_xep_hang", phien_ban_engine,
                      canh_bao=["Điểm xếp hạng chỉ dùng sắp thứ tự, chưa phải độ tin cậy đã duyệt."])
