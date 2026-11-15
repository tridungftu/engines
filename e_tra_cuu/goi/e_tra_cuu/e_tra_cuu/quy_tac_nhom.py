"""TC-5: quy tắc xác định trên bộ được Core ghim; không có danh mục mặc định.

Từ điển dấu hiệu/bên ký, quan hệ đối tượng và phạm vi bài đo là tài nguyên
Core cấp theo tham chiếu cấu hình. Fixture DEMO không là chính sách vận hành.
So khớp dấu hiệu chỉ giúp đề xuất; không xác nhận pháp lý hoặc xếp kho.
"""

import re
import unicodedata

from .kiem_dau_vao import danh_sach, doi_tuong, kiem_bam, loi, ma


NHOM_QUY_TAC = {
    "cong_trinh": "04", "thiet_bi_lap_dat": "04", "vat_tu_cdt_cap": "04",
    "sua_chua_bao_tri": "04", "thue_may": "03", "mua_hang": "03",
    "quy_che_lao_dong": "07", "quy_che_khac": "08", "nhan_su": "07",
    "phap_ly_du_an": "01", "vay": "02", "ban_nha": "05", "kcn": "05",
    "ban_nhua": "05", "ban_dien_doc_lap": "05", "phap_ly_cong_ty": "06",
}
LY_DO = {
    "PHAP_NHAN_CHUA_RO": "Chưa xác minh được bên ký khớp pháp nhân của việc.",
    "THIEU_CAN_CU": "Chưa có đủ căn cứ nguyên văn để đề xuất phân loại.",
    "CHUA_NHAN_DIEN": "Chưa nhận diện được loại tài liệu theo bộ quy tắc đã cấp.",
    "HON_HOP": "Có nhiều bản chất nghiệp vụ cần người duyệt phân định.",
    "THIEU_CONG_TRINH": "Thiếu thông tin công trình hoặc tài sản được Core cấp để phân loại.",
    "SAI_QUY_TAC": "Đề xuất của AI chưa khớp thứ tự quy tắc nghiệp vụ.",
    "THIEU_LOAI": "Chưa chọn được loại đang hoạt động phù hợp trong danh mục.",
    "CHO_KICH_HOAT": "Nhánh tài liệu đang chờ kích hoạt.",
    "NGUNG_NHAN_MOI": "Loại tài liệu đã ngừng nhận mới.",
    "LOAI_HINH": "Loại tài liệu chưa phù hợp loại hình pháp nhân CP/TNHH đã được Core cấp.",
    "DOI_TUONG": "Chưa xác minh được đối tượng phù hợp trong danh mục được cấp.",
    "NGOAI_PHAM_VI": "Nhóm đề xuất nằm ngoài phạm vi Core cấp cho việc.",
    "CHUA_DO": "Chưa có ngưỡng phân loại đã đo đúng phạm vi model và prompt này.",
    "DUOI_NGUONG": "Điểm đề xuất chưa đạt ngưỡng phân loại đã đo.",
    "AI_DE_NGHI_CHO": "AI đề nghị kiểm tra thêm; cần người duyệt xem căn cứ.",
    "DOI_BAN_CHAT": "Phụ lục có thể làm đổi bản chất; đề nghị Core duyệt chuyển cả bộ hồ sơ.",
    "PHU_LUC_CHUA_RO": "Chưa đủ quan hệ và căn cứ để đề nghị chuyển cả bộ hồ sơ.",
}


def _chu(v):
    return unicodedata.normalize("NFC", v).casefold()


def _co(chuoi, cac_dau_hieu):
    # Không sửa chuỗi nguồn/offset. Biên từ tránh mã DEMO-A khớp DEMO-AB.
    chuoi = _chu(chuoi)
    return any(re.search(r"(?<!\w)" + re.escape(_chu(x)) + r"(?!\w)", chuoi)
               for x in cac_dau_hieu)


def _ben_ky(chuoi, cac_dau_hieu):
    # Không lấy một tên xuất hiện trong câu kể/trích dẫn làm bên ký. Bộ Core
    # phải cấp cả dòng nhận diện bên ký; thiếu hoặc nhiều bên khớp thì chờ.
    dong = {_chu(x.strip()) for x in chuoi.splitlines()}
    return any(_chu(x.strip()) in dong for x in cac_dau_hieu)


def kiem_bo_quy_tac(v, dm):
    """Bộ miền đóng, chỉ thư viện chuẩn; mọi mã liên kết lại snapshot danh mục."""
    try:
        doi_tuong(v, ("phien_ban", "phap_nhan", "loai", "doi_tuong", "phep_do", "quy_che_khac"), ())
        if type(v["phien_ban"]) is not int or v["phien_ban"] != 1:
            loi("TC_SAI_NGUON")
        if any(type(x) is not str or not x.strip() or len(x) > 1000
               for x in danh_sach(v["quy_che_khac"], 100)):
            loi("TC_SAI_NGUON")
        chi_muc = {k: {x["ma"]: x for x in dm[k]} for k in ("nhom", "loai", "doi_tuong", "loai_hinh_phap_nhan")}
        for ten, cac_truong in (("phap_nhan", ("ma", "loai_hinh", "dau_hieu_ben_ky")),
                          ("loai", ("ma", "quy_tac", "loai_hinh", "dau_hieu")),
                          ("doi_tuong", ("ma", "nhom", "loai", "dau_hieu", "thong_tin_cong_trinh"))):
            cac_ma = []
            for x in danh_sach(v[ten], 1000):
                doi_tuong(x, cac_truong, ())
                cac_ma.append(ma(x["ma"]))
                dh = danh_sach(x["dau_hieu_ben_ky" if ten == "phap_nhan" else "dau_hieu"], 100)
                if not dh or any(type(y) is not str or not y.strip() or len(y) > 1000 for y in dh):
                    loi("TC_SAI_NGUON")
                if ten == "phap_nhan":
                    if x["loai_hinh"] not in {"CP", "TNHH"} or x["loai_hinh"] not in chi_muc["loai_hinh_phap_nhan"]:
                        loi("TC_SAI_NGUON")
                elif ten == "loai":
                    q = x["quy_tac"]
                    if (q not in NHOM_QUY_TAC or x["ma"] not in chi_muc["loai"]
                            or chi_muc["loai"][x["ma"]]["nhom"] != NHOM_QUY_TAC[q]
                            or any(y not in {"CP", "TNHH"} for y in danh_sach(x["loai_hinh"]))):
                        loi("TC_SAI_NGUON")
                else:
                    if (x["ma"] not in chi_muc["doi_tuong"] or type(x["thong_tin_cong_trinh"]) is not bool
                            or not danh_sach(x["nhom"]) or any(y not in chi_muc["nhom"] for y in x["nhom"])
                            or any(y not in chi_muc["loai"] for y in danh_sach(x["loai"]))):
                        loi("TC_SAI_NGUON")
            if len(cac_ma) != len(set(cac_ma)):
                loi("TC_SAI_NGUON")
        pd = v["phep_do"]
        if pd is not None:
            doi_tuong(pd, ("bam_bo_do", "ma_prompt", "phien_ban_prompt", "model", "phien_ban_engine_ai"), ())
            kiem_bam(pd["bam_bo_do"])
            if any(type(pd[k]) is not str or not pd[k].strip() for k in pd):
                loi("TC_SAI_NGUON")
        return v
    except (KeyError, TypeError, ValueError):
        loi("TC_SAI_NGUON")


def ap_quy_tac(s, a, de_xuat, can_cu, bo):
    """Mọi đường ra đều cần Core duyệt; điểm model không là xác suất."""
    d, nc = s["du_lieu"], s["ngu_canh_core"]
    dm = d["danh_muc"]
    vb = d["tai_lieu"]["van_ban_tai_lieu"]["van_ban_tai_lieu"]["van_ban"]
    # Từng dấu hiệu phải có trong một câu trích đã kiểm, không nối hai lát
    # cách xa nhau thành một câu giả. Toàn văn dùng để bắt bản chất bị bỏ sót.
    cau_trich = [c["cau"] for c in can_cu]
    duoc_trich = lambda dh: any(_co(q, dh) for q in cau_trich)
    ly_do = []

    def cho(ma_ly_do):
        if ma_ly_do not in ly_do:
            ly_do.append(ma_ly_do)

    pn = [p for p in bo["phap_nhan"] if _ben_ky(vb, p["dau_hieu_ben_ky"])]
    phap_nhan = pn[0] if len(pn) == 1 and pn[0]["ma"] == nc["phap_nhan_id"] else None
    if phap_nhan is None or not any(_ben_ky(q, phap_nhan["dau_hieu_ben_ky"]) for q in cau_trich):
        cho("PHAP_NHAN_CHUA_RO")
    if not can_cu or a["trang_thai"] != "co_can_cu":
        cho("THIEU_CAN_CU")
    loai_dm = {x["ma"]: x for x in dm["loai"]}
    nhan_dien = [x for x in bo["loai"] if _co(vb, x["dau_hieu"])]
    qs = {x["quy_tac"] for x in nhan_dien}
    if _co(vb, bo["quy_che_khac"]):
        qs.add("quy_che_khac")
    # Thuê thiết bị thi công vẫn là 03; không lấy riêng chữ "công trình"
    # để đổi sang 04. Vật tư/sửa chữa thiếu thông tin không rơi về mua hàng.
    if "thue_may" in qs and not qs & {"thiet_bi_lap_dat", "vat_tu_cdt_cap", "sua_chua_bao_tri"}:
        chon = {"thue_may"}
    elif qs & {"cong_trinh", "thiet_bi_lap_dat", "vat_tu_cdt_cap", "sua_chua_bao_tri"}:
        chon = qs & {"thiet_bi_lap_dat", "vat_tu_cdt_cap", "sua_chua_bao_tri"} or {"cong_trinh"}
        if "thue_may" in qs or len(chon) > 1:
            cho("HON_HOP")
    elif "mua_hang" in qs:
        chon = {"mua_hang"}
    elif "quy_che_lao_dong" in qs:
        chon = {"quy_che_lao_dong"}
    else:
        chon = qs - {"quy_che_khac"} or qs
    nhoms = {NHOM_QUY_TAC[q] for q in chon}
    nhom = next(iter(nhoms)) if len(nhoms) == 1 else None
    if not nhoms:
        cho("CHUA_NHAN_DIEN")
    elif len(nhoms) > 1:
        cho("HON_HOP")
    if nhom is not None and nhom not in nc["nhom"]:
        cho("NGOAI_PHAM_VI")
        nhom = None
    ld = de_xuat["loai_de_xuat"]
    loai_khop = next((x for x in nhan_dien if x["ma"] == ld and x["quy_tac"] in chon), None)
    goc_08 = nhom == "08" and ld is None and duoc_trich(bo["quy_che_khac"])
    if de_xuat["nhom_de_xuat"] != nhom:
        cho("SAI_QUY_TAC")
    # Nếu Python nhận diện loại ngừng/chờ, vẫn chờ kể cả AI trả null đúng khuôn.
    for x in nhan_dien:
        if x["quy_tac"] in chon:
            tt = loai_dm[x["ma"]]["trang_thai"]
            if tt != "hoat_dong":
                cho("CHO_KICH_HOAT" if tt == "cho_kich_hoat" else "NGUNG_NHAN_MOI")
    if goc_08:
        pass  # Xếp đề xuất ở gốc 08, không tạo mã loại hoặc thư mục con.
    elif loai_khop is None or nhom is None or loai_dm[ld]["nhom"] != nhom:
        cho("THIEU_LOAI")
        ld = None
    elif not duoc_trich(loai_khop["dau_hieu"]):
        cho("THIEU_CAN_CU")
        ld = None
    elif loai_khop["loai_hinh"] and (phap_nhan is None or phap_nhan["loai_hinh"] not in loai_khop["loai_hinh"]):
        cho("LOAI_HINH")
        ld = None
    dt = next((x for x in bo["doi_tuong"] if x["ma"] == de_xuat["doi_tuong"]), None)
    if nhom == "08" and de_xuat["doi_tuong"] is None:
        dt = None  # Gốc 08 không bắt buộc một thư mục đối tượng.
    elif (dt is None or nhom not in dt["nhom"] or (dt["loai"] and ld not in dt["loai"])
            or not duoc_trich(dt["dau_hieu"])):
        dt = None
        cho("DOI_TUONG")
    if nhom == "04" and (dt is None or not dt["thong_tin_cong_trinh"]):
        cho("THIEU_CONG_TRINH")
    pl = s["cau_hinh"]["gia_tri"]["phan_loai"]
    pd = bo["phep_do"]
    da_do = (pl["trang_thai"] == "da_do" and pd is not None
             and pd["bam_bo_do"] == pl["bam_bo_do"]
             and all(pd[k] == a[k] for k in ("ma_prompt", "phien_ban_prompt", "model"))
             and pd["phien_ban_engine_ai"] == a["phien_ban_engine"])
    if not da_do:
        cho("CHUA_DO")
    elif de_xuat["diem"] < pl["nguong"]:
        cho("DUOI_NGUONG")
    if de_xuat["ly_do_cho"]:
        cho("AI_DE_NGHI_CHO")
    cu, qh = d["phan_loai_cu"], d["quan_he_phu_luc"]
    chuyen = False
    quy_tac_cu = next((x for x in bo["loai"] if cu is not None and x["ma"] == cu.get("loai")), None)
    doi_ban_chat = cu is not None and nhom is not None and (
        cu.get("nhom") != nhom or (quy_tac_cu is not None and loai_khop is not None
                                  and quy_tac_cu["quy_tac"] != loai_khop["quy_tac"]))
    if doi_ban_chat:
        # Quan hệ cũ phải do Core ghim, có mã bộ; cờ model riêng không đủ.
        if (qh is not None and type(qh.get("ma_bo_ho_so")) is str and qh["ma_bo_ho_so"].strip()
                and cu.get("nhom") in {x["ma"] for x in dm["nhom"]}
                and can_cu and (goc_08 or (loai_khop is not None and duoc_trich(loai_khop["dau_hieu"])))):
            chuyen = True
            cho("DOI_BAN_CHAT")
        else:
            cho("PHU_LUC_CHUA_RO")
    elif de_xuat["de_nghi_chuyen_bo"]:
        cho("PHU_LUC_CHUA_RO")
    # Không có căn cứ/bên ký: không giữ nhãn đoán làm một phân loại đã xác minh.
    if "PHAP_NHAN_CHUA_RO" in ly_do or "THIEU_CAN_CU" in ly_do:
        nhom, ld, dt, chuyen = None, None, None, False
    kq = {"nhom_de_xuat": nhom, "loai_de_xuat": ld,
          "doi_tuong": dt["ma"] if dt is not None else None,
          "diem": de_xuat["diem"], "can_cu": can_cu,
          "ly_do_cho": [LY_DO[x] for x in ly_do], "de_nghi_chuyen_bo": chuyen,
          "kiem_tra": {"ma_ly_do": ly_do, "chi_la_de_xuat": True, "can_duyet": True,
              "phap_nhan_id": nc["phap_nhan_id"], "diem_la_xac_suat": False,
              "xac_suat_hieu_chinh": None, "nguong_da_do": da_do,
              "quy_tac_ap_dung": sorted(chon),
              "ma_bo_ho_so": qh["ma_bo_ho_so"] if chuyen else None}}
    return ("cho_phan_loai" if ly_do else "da_phan_loai"), kq
