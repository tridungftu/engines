"""TC-7: kiểm quan hệ khẳng định/trường/thực thể/nguồn bằng Python.

Không thể chứng minh ngữ nghĩa văn xuôi tùy ý bằng phép tìm chuỗi. Đợt này
chỉ nhận mẫu trình bày xác định và các quy tắc định dạng được khai tường minh.
"""

from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import re

from .bang_chung import _doi_tuong
from .cau_hoi import khop_khuon, sai_khuon
from .kiem_dau_vao import bam, json_chuan, kiem_bam, kiem_hop, loi, thoi_diem
from .vi_tri import dinh_vi, lap_ban_do


_KHOA_BC = {"nguon", "thuc_the", "truong", "kieu", "gia_tri", "don_vi", "quy_tac", "hien_thi",
            "cau", "bat_dau", "ket_thuc", "vi_tri_gia_tri", "vi_tri", "trang_thai_duyet", "con_hieu_luc",
            "do_tin_cay", "moc_cong_bo", "moc_duyet", "hieu_luc_tu", "hieu_luc_den"}


def _bang(a, b):
    return json_chuan(a) == json_chuan(b)


def _thuc_the(x):
    _doi_tuong(x, ("loai", "ma", "gia_tri"))
    if any(type(v) is not str or not v.strip() for v in x.values()):
        loi("TC_SAI_NGUON")
    return json_chuan(x)


def _decimal(v):
    if not (type(v) is int or (type(v) is str and re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", v))):
        return None
    try:
        x = Decimal(v)
        return x if x.is_finite() else None
    except InvalidOperation:
        return None


def hien_thi(b):
    """Không đổi tỷ lệ, làm tròn, tổng, đơn vị hoặc suy tiền tệ."""
    v, k, q, dv = b["gia_tri"], b["kieu"], b["quy_tac"], b["don_vi"]
    if k == "so_tien":
        if type(v) is not dict or set(v) != {"so", "tien_te"} or _decimal(v["so"]) is None:
            return None
        if type(v["tien_te"]) is not str or not re.fullmatch(r"[A-Z]{3}", v["tien_te"]) or dv != v["tien_te"]:
            return None
        chu = str(v["so"])
        if q == "tien_chuan":
            return chu + " " + v["tien_te"]
        if q != "tien_nhom_ba":
            return None
        # Nhóm ký tự, không đưa tiền qua float hoặc phép toán Decimal có làm tròn.
        dau = "-" if chu.startswith("-") else ""
        nguyen, _, le = chu.lstrip("-").partition(".")
        # Dựng lại từ trái để giữ cả số lớn hơn 2**53 và chữ số thập phân.
        nhom = ".".join(reversed([nguyen[max(0, len(nguyen) - i - 3):len(nguyen) - i]
                                  for i in range(0, len(nguyen), 3)]))
        return dau + nhom + ("," + le if le else "") + " " + v["tien_te"]
    if k == "ngay":
        if type(v) is not str or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", v) or dv is not None:
            return None
        try:
            d = date.fromisoformat(v)
        except ValueError:
            return None
        if q == "ngay_iso":
            return v
        return f"{d.day:02}/{d.month:02}/{d.year:04}" if q == "ngay_viet" else None
    if k == "so" and q == "so_chuan" and _decimal(v) is not None:
        return str(v) + (" " + dv if dv is not None else "")
    if k == "van_ban" and q == "nguyen_van" and type(v) is str and v.strip() and dv is None:
        return v
    if k == "co_khong" and q == "co_khong" and type(v) is bool and dv is None:
        return "Có" if v else "Không"
    return None


def _ngay(v):
    if v is None:
        return None
    if type(v) is not str or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", v):
        loi("TC_SAI_NGUON")
    try:
        return date.fromisoformat(v)
    except ValueError:
        loi("TC_SAI_NGUON")


def _gia_tri_nguyen_cum(b, chu):
    a, z = b["vi_tri_gia_tri"]
    if type(a) is not int or type(z) is not int or not b["bat_dau"] <= a < z <= b["ket_thuc"]:
        return False
    x, y = a - b["bat_dau"], z - b["bat_dau"]
    if chu[x:y] != b["hien_thi"]:
        return False
    # Không nhận '5' trong '15'/'5.000.000', mã 007 trong 0007, hoặc nửa ngày.
    cam = r"[\w.,/+%-]"
    return not ((x and re.match(cam, chu[x - 1])) or re.match(r"[\w/+-]|[.,][0-9]", chu[y:]))


def _dieu(vb, a):
    cac = [m.group(1) for m in re.finditer(r"(?m)^[ \t]*(Điều[ \t]+[0-9]+[^\r\n\f]*)", vb) if m.start() <= a]
    return cac[-1] if cac else None


def _co_cum(chu, cum, *, flags=0):
    return re.search(r"(?<![\w-])" + re.escape(cum) + r"(?![\w-])", chu, flags) is not None


def kiem_bang_chung(s, doc, cap, viec):
    """Trả danh sách căn cứ đã kiểm và lý do tầng chưa đủ; không truy vấn tầng sau."""
    c = cap.get("kiem_chung_tra_loi")
    if c is None:
        loi("TC_CHUA_CO_CUA_CORE")
    _doi_tuong(c, ("phien_ban", "trang_thai_nguon", "bam_du_lieu", "truong_can_tra_loi",
                  "nguong_tin_cay", "phu_thuoc_thoi_diem", "bang_chung"))
    if len(json_chuan(c)) > doc.tran["tep_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    d = s["du_lieu"]
    if (type(c["phien_ban"]) is not int or c["phien_ban"] != 1
            or kiem_bam(c["bam_du_lieu"]) != bam(json_chuan(d))):
        loi("TC_SAI_NGUON")
    if c["trang_thai_nguon"] != "da_tra":
        loi("TC_CHUA_CO_CUA_CORE")
    if type(c["phu_thuoc_thoi_diem"]) is not bool:
        loi("TC_SAI_NGUON")
    entities = [_thuc_the(x) for x in d["thuc_the"]]
    if not entities or len(set(entities)) != len(entities) or len({x["ma"] for x in d["thuc_the"]}) != len(entities):
        loi("TC_SAI_NGUON")
    fields = c["truong_can_tra_loi"]
    if type(fields) is not list or not fields or len(fields) > 100:
        loi("TC_SAI_NGUON")
    for f in fields:
        _doi_tuong(f, ("ma", "ten", "kieu", "don_vi"))
        if any(type(f[k]) is not str or not f[k].strip() for k in ("ma", "ten", "kieu")):
            loi("TC_SAI_NGUON")
        if f["don_vi"] is not None and (type(f["don_vi"]) is not str or not f["don_vi"].strip()):
            loi("TC_SAI_NGUON")
    if len({f["ma"] for f in fields}) != len(fields):
        loi("TC_SAI_NGUON")
    if type(c["bang_chung"]) is not list or len(c["bang_chung"]) > doc.tran["so_ung_vien_toi_da"]:
        loi("TC_QUA_GIOI_HAN")
    nguong = c["nguong_tin_cay"]
    da_do = False
    if nguong is not None:
        _doi_tuong(nguong, ("trang_thai", "gia_tri", "bam_bo_do", "da_duyet"))
        kiem_bam(nguong["bam_bo_do"])
        if type(nguong["gia_tri"]) not in (int, float) or not 0 <= nguong["gia_tri"] <= 1 or type(nguong["da_duyet"]) is not bool:
            loi("TC_SAI_NGUON")
        da_do = nguong["trang_thai"] == "da_do" and nguong["da_duyet"]
    bang, ly_do, maps = [], [], {}
    if any(not _co_cum(d["cau_hoi"], e["gia_tri"]) for e in d["thuc_the"]):
        ly_do.append("THUC_THE_KHONG_KHOP_CAU_HOI")
    now = datetime.fromisoformat(s["ngu_canh_core"]["thoi_diem"])
    for b in c["bang_chung"]:
        viec.kiem_huy()
        _doi_tuong(b, _KHOA_BC)
        doc.kiem_nguon_da_cap(b["nguon"])
        if b["nguon"]["ma_nguon"] not in doc.nguon:
            loi("TC_SAI_NGUON")
        _thuc_the(b["thuc_the"])
        for k in ("cau", "hien_thi", "truong", "kieu", "quy_tac"):
            if type(b[k]) is not str or not b[k].strip():
                loi("TC_SAI_NGUON")
        if (type(b["bat_dau"]) is not int or type(b["ket_thuc"]) is not int
                or b["bat_dau"] < 0 or b["ket_thuc"] - b["bat_dau"] != len(b["cau"])
                or type(b["vi_tri_gia_tri"]) is not list or len(b["vi_tri_gia_tri"]) != 2):
            loi("TC_SAI_NGUON")
        _doi_tuong(b["vi_tri"], ("trang", "hop", "dieu"))
        p = b["vi_tri"]["trang"]
        if p is not None and (type(p) is not int or p < 1):
            loi("TC_SAI_NGUON")
        if b["vi_tri"]["hop"] is not None:
            if p is None:
                loi("TC_SAI_NGUON")
            kiem_hop(b["vi_tri"]["hop"])
        if b["vi_tri"]["dieu"] is not None and type(b["vi_tri"]["dieu"]) is not str:
            loi("TC_SAI_NGUON")
        if (b["trang_thai_duyet"] not in ("da_duyet", "cho_duyet", "tu_choi")
                or type(b["con_hieu_luc"]) is not bool or type(b["do_tin_cay"]) not in (int, float)
                or not 0 <= b["do_tin_cay"] <= 1):
            loi("TC_SAI_NGUON")
        thoi_diem(b["moc_cong_bo"])
        if b["moc_duyet"] is not None:
            thoi_diem(b["moc_duyet"])
        tu, den = _ngay(b["hieu_luc_tu"]), _ngay(b["hieu_luc_den"])
        if tu and den and tu > den:
            loi("TC_SAI_NGUON")
        f = next((f for f in fields if f["ma"] == b["truong"]), None)
        if f is None or _thuc_the(b["thuc_the"]) not in entities:
            continue
        don_vi_dat = (b["don_vi"] == f["don_vi"] or
                      (f["don_vi"] is None and b["kieu"] in ("so_tien", "so")))
        if (b["kieu"] != f["kieu"] or not don_vi_dat or hien_thi(b) != b["hien_thi"]
                or not _gia_tri_nguyen_cum(b, b["cau"])
                or not _co_cum(b["cau"], b["thuc_the"]["gia_tri"])
                or not _co_cum(b["cau"], f["ten"], flags=re.I)):
            ly_do.append("QUAN_HE_GIA_TRI_KHONG_DAT")
            continue
        n = b["nguon"]
        if d["tang"] == 1:
            # Dữ liệu đã duyệt được cấp độc lập: caller không tự biến văn bản thành Xanh.
            can = {k: b[k] for k in ("nguon", "thuc_the", "truong", "kieu", "gia_tri", "don_vi",
                                     "trang_thai_duyet", "con_hieu_luc", "do_tin_cay", "moc_cong_bo")}
            if not any(_bang(can, x) for x in d["bang_chung"]):
                ly_do.append("QUAN_HE_TANG_MOT_KHONG_DAT")
                continue
        else:
            vb = doc.van_ban[n["ma_nguon"]]
            if (vb["van_ban"][b["bat_dau"]:b["ket_thuc"]] != b["cau"]
                    or not any(x["ma_nguon"] == n["ma_nguon"] and x["phien_ban_nguon"] == n["phien_ban_nguon"]
                               and x["bat_dau"] <= b["bat_dau"] < b["ket_thuc"] <= x["ket_thuc"] for x in d["bang_chung"])):
                ly_do.append("TRICH_DAN_KHONG_DAT")
                continue
            if n["ma_nguon"] not in maps:
                maps[n["ma_nguon"]] = lap_ban_do(vb, viec.kiem_huy)
            vt, _ = dinh_vi(maps[n["ma_nguon"]], [{"nguon_bat_dau": b["bat_dau"],
                          "nguon_ket_thuc": b["ket_thuc"], "vai_tro": "noi_dung"}], viec.kiem_huy)
            if not _bang(b["vi_tri"], {**vt, "dieu": _dieu(vb["van_ban"], b["bat_dau"])}):
                ly_do.append("VI_TRI_KHONG_DAT")
                continue
        het_hieu_luc = (not b["con_hieu_luc"] or (tu is not None and now.date() < tu)
                       or (den is not None and now.date() > den) or datetime.fromisoformat(b["moc_cong_bo"]) > now)
        if het_hieu_luc:
            ly_do.append("HET_HIEU_LUC")
            continue  # Bản hết hiệu lực không là một phía mâu thuẫn tại thời điểm hỏi.
        if d["tang"] == 1:
            if b["trang_thai_duyet"] != "da_duyet" or b["moc_duyet"] is None:
                ly_do.append("CHUA_DUYET")
            elif datetime.fromisoformat(b["moc_duyet"]) > now:
                ly_do.append("CHUA_DUYET")
            if not da_do:
                ly_do.append("THIEU_NGUONG_DA_DO")
            elif Decimal(str(b["do_tin_cay"])) < Decimal(str(nguong["gia_tri"])):
                ly_do.append("DUOI_NGUONG_TIN_CAY")
        bang.append(deepcopy(b))
    for e in d["thuc_the"]:
        for f in fields:
            if not any(_bang(b["thuc_the"], e) and b["truong"] == f["ma"] for b in bang):
                ly_do.append("THIEU_TRUONG_HOAC_THUC_THE")
    if not d["bang_chung"] or not bang:
        ly_do.append("KHONG_CO_BANG_CHUNG")
    return bang, list(dict.fromkeys(ly_do)), c


def co_mau_thuan(bang):
    nhom = {}
    for b in bang:
        khoa = (_thuc_the(b["thuc_the"]), b["truong"])
        # Giá trị tiền khác biểu diễn int/chuỗi Decimal vẫn cùng giá trị.
        v = b["gia_tri"]
        if b["kieu"] == "so_tien":
            v = (Decimal(str(v["so"])), v["tien_te"])
        elif b["kieu"] == "so":
            v = Decimal(str(v))
        else:
            v = json_chuan(v)
        nhom.setdefault(khoa, set()).add(v)
    return any(len(v) > 1 for v in nhom.values())


def cau_tra_loi(bang, fields, mau_thuan):
    ten = {f["ma"]: f["ten"] for f in fields}
    cac_cau = [f'{ten[b["truong"]]} ({b["thuc_the"]["gia_tri"]}): {b["hien_thi"]}.' for b in bang]
    return ("Có mâu thuẫn trong bằng chứng; Anh cần duyệt các giá trị sau.\n" if mau_thuan else "") + "\n".join(cac_cau)


def _quote(q, ai):
    if type(q) is not dict or set(q) != {"cau", "bat_dau", "ket_thuc"}:
        return None
    x, z = q["bat_dau"], q["ket_thuc"]
    if (type(x) is not int or type(z) is not int or not 0 <= x < z <= len(ai["tai_lieu"])
            or q["cau"] != ai["tai_lieu"][x:z]):
        return None
    return next((m for m in ai["map_nguon"] if m["ma_nguon"] is not None
                 and m["ai_bat_dau"] <= x < z <= m["ai_ket_thuc"]), None)


def kiem_ai(a, s, bang, profile, viec):
    v = a["du_lieu"]
    if a["trang_thai"] == "khong_thay_can_cu" and v is None:
        return False
    # Hình dạng sai là lỗi khuôn; mã thực thể/nguồn/đoạn không khớp là hỏng
    # quan hệ chứng cứ, trả không căn cứ thay vì giữ câu bịa có nhãn Vàng.
    khuon = deepcopy(s["ai"]["khuon_tra_loi"])
    props = khuon["properties"]["khang_dinh"]["items"]["properties"]
    props["thuc_the"] = {"type": "string", "minLength": 1}
    for k in ("ma_nguon", "ma_doan"):
        props["can_cu"]["items"]["properties"][k] = {"type": "string", "minLength": 1}
    if not khop_khuon(v, khuon, kiem_huy=viec.kiem_huy):
        sai_khuon()
    if (a["trang_thai"] != "co_can_cu" or not a["kiem_trich_dan"]["dat"] or a["kiem_trich_dan"]["loi"]
            or not a["trich_dan"] or any(_quote(q, s["ai"]) is None for q in a["trich_dan"])):
        return False
    if len(v["khang_dinh"]) != len(bang):
        return False
    da_gap = set()
    for k in v["khang_dinh"]:
        viec.kiem_huy()
        hop = []
        for i, b in enumerate(bang):
            if (k["thuc_the"] != b["thuc_the"]["ma"] or k["truong"] != b["truong"]
                    or not _bang(k["gia_tri"], b["gia_tri"]) or k["don_vi"] != b["don_vi"]):
                continue
            for q in k["can_cu"]:
                m = _quote({j: q[j] for j in ("cau", "bat_dau", "ket_thuc")}, s["ai"])
                if m is None or q["ma_nguon"] != b["nguon"]["ma_nguon"] or q["ma_doan"] != m["ma_doan"]:
                    continue
                a0 = m["nguon_bat_dau"] + q["bat_dau"] - m["ai_bat_dau"]
                z0 = a0 + len(q["cau"])
                if (m["ma_nguon"] == b["nguon"]["ma_nguon"] and a0 == b["bat_dau"] and z0 == b["ket_thuc"]
                        and q["cau"] == b["cau"] and any(t["bat_dau"] <= q["bat_dau"] < q["ket_thuc"] <= t["ket_thuc"]
                        for t in a["trich_dan"])):
                    hop.append(i)
            # Mọi quote trong một khẳng định phải trỏ cùng căn cứ thực, không kèm câu bịa.
            if len(hop) and (len(k["can_cu"]) != 1):
                return False
        hop = set(hop) - da_gap
        if len(hop) != 1:
            return False
        da_gap.update(hop)
    mau_thuan = co_mau_thuan(bang)
    return (len(da_gap) == len(bang) and v["co_mau_thuan"] is mau_thuan
            and v["tra_loi"] == cau_tra_loi(bang, profile["truong_can_tra_loi"], mau_thuan))
