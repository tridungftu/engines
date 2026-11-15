"""AI-12: vai trò trường trong $comment và tương thích khuôn TC/DC đã có.

Không suy vai trò từ tên trường đứng riêng. Khuôn ngoài năm cấu trúc đã biết
giữ kiểm nguyên văn bảo thủ; schema gốc/chuyển tiếp không bị sửa.
"""
from copy import deepcopy
import re

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .khuon_json import _tham_chieu, khop

TIEN_TO = "ktt:ai12:"
VAI_TRO = {"metadata", "trich_xuat", "trich_dan", "tong_hop"}


def _loi_khuon():
    raise LoiNghiepVu("KHUON_KHONG_HOP_LE", "Vai trò trường trong khuôn trả lời không hợp lệ. Anh nhờ quản trị viên module kiểm tra.")


def _vai_tro(s):
    chu = s.get("$comment") if isinstance(s, dict) else None
    if isinstance(chu, str) and chu.startswith(TIEN_TO):
        vai = chu[len(TIEN_TO):]
        if vai not in VAI_TRO:
            _loi_khuon()
        return vai


def _kiem_chu_thich(s):
    if isinstance(s, bool):
        return
    vai = _vai_tro(s)
    if vai == "metadata" and ("properties" in s or "items" in s
            or any(t in (s.get("type") if isinstance(s.get("type"), list) else [s.get("type")]) for t in ("object", "array"))):
        _loi_khuon()
    for k in ("properties", "$defs"):
        for con in s.get(k, {}).values():
            _kiem_chu_thich(con)
    for k in ("items", "additionalProperties", "not"):
        if k in s:
            _kiem_chu_thich(s[k])
    for k in ("prefixItems", "allOf", "anyOf", "oneOf"):
        for con in s.get(k, []):
            _kiem_chu_thich(con)


def _dong(s, ten):
    return (isinstance(s, dict) and s.get("type") == "object"
            and s.get("additionalProperties") is False
            and set(s.get("properties", {})) == set(ten)
            and set(s.get("required", [])) == set(ten))


def _gan(s, duong, vai):
    for k in duong.split("/") if duong else []:
        s = s["items"] if k == "*" else s["properties"][k]
    cu = _vai_tro(s)
    if cu is not None and cu != vai:
        _loi_khuon()  # Không cho annotation hạ giá trị trích thành metadata.
    s["$comment"] = TIEN_TO + vai


def khuon_hau_kiem(khuon, chuyen_tiep):
    """Bổ sung annotation trên bản sao cho đúng cấu trúc producer phiên bản 1.

    Chuyển tiếp chỉ chọn quy ước, không chứng minh nguồn/quyền. Trường mới hoặc
    cấu trúc khác không được miễn kiểm. Không tự miễn mọi enum/const: ngày/tiền
    có enum vẫn có thể là giá trị tài liệu.
    """
    if khuon is None:
        return None
    _kiem_chu_thich(khuon)
    s = deepcopy(khuon)
    ct = chuyen_tiep.get("tra_cuu", {})
    tac = ct.get("tac_vu") if isinstance(ct, dict) and type(ct.get("phien_ban")) is int and ct["phien_ban"] == 1 else None
    cac_truong = {
        "phan_loai": "nhom_de_xuat loai_de_xuat doi_tuong diem can_cu ly_do_cho de_nghi_chuyen_bo",
        "phan_tich_cau_hoi": "y_dinh thuc_the ham_de_xuat phu_thuoc_thoi_diem thoi_diem",
        "xep_hang_lai": "xep_hang",
        "soan_tra_loi": "tra_loi khang_dinh co_mau_thuan",
    }
    try:
        if tac in cac_truong and _dong(s, cac_truong[tac].split()):
            if tac == "phan_loai":
                for ten in ("nhom_de_xuat", "loai_de_xuat", "doi_tuong"):
                    if "enum" not in s["properties"][ten]:
                        _loi_khuon()
                for ten in ("nhom_de_xuat", "loai_de_xuat", "doi_tuong", "diem", "ly_do_cho/*", "de_nghi_chuyen_bo"):
                    _gan(s, ten, "metadata")
                _gan(s, "can_cu/*", "trich_dan")
            elif tac == "phan_tich_cau_hoi":
                if not _dong(s["properties"]["thuc_the"]["items"], ("loai", "ma", "gia_tri")):
                    _loi_khuon()
                for ten in ("y_dinh", "thuc_the/*/loai", "thuc_the/*/ma", "phu_thuoc_thoi_diem", "thoi_diem"):
                    _gan(s, ten, "metadata")
                _gan(s, "thuc_the/*/gia_tri", "trich_xuat")
                hs = s["properties"]["ham_de_xuat"]["items"]
                for h in hs.get("oneOf", []) if isinstance(hs, dict) else []:
                    if not _dong(h, ("ten", "phien_ban", "tham_so")):
                        _loi_khuon()
                    for ten in ("ten", "phien_ban"):
                        if "const" not in h["properties"][ten]:
                            _loi_khuon()
                        _gan(h, ten, "metadata")
                    _gan(h, "tham_so", "trich_xuat")
            elif tac == "xep_hang_lai":
                item = s["properties"]["xep_hang"]["items"]
                if not _dong(item, ("ma_ung_vien", "diem")) or "enum" not in item["properties"]["ma_ung_vien"]:
                    _loi_khuon()
                for ten in ("ma_ung_vien", "diem"):
                    _gan(item, ten, "metadata")
            else:
                item = s["properties"]["khang_dinh"]["items"]
                if not _dong(item, ("thuc_the", "truong", "gia_tri", "don_vi", "can_cu")):
                    _loi_khuon()
                _gan(s, "tra_loi", "tong_hop")
                _gan(s, "co_mau_thuan", "metadata")
                for ten in ("thuc_the", "truong"):
                    _gan(item, ten, "metadata")
                for ten in ("gia_tri", "don_vi"):
                    _gan(item, ten, "trich_xuat")
                _gan(item, "can_cu/*", "trich_dan")
        else:
            ct = chuyen_tiep.get("doi_chieu", {})
            if (isinstance(ct, dict) and type(ct.get("phien_ban")) is int and ct["phien_ban"] == 1
                    and _dong(s, ("diem",))):
                item = s["properties"]["diem"]["items"]
                if not _dong(item, ("ma_diem", "nhan", "ly_do", "trai", "phai")):
                    _loi_khuon()
                for ten in ("ma_diem", "nhan"):
                    if "enum" not in item["properties"][ten]:
                        _loi_khuon()
                for ten in ("ma_diem", "nhan", "ly_do"):
                    _gan(item, ten, "metadata")
                for ten in ("trai", "phai"):
                    _gan(item, ten, "trich_dan")
    except (KeyError, TypeError, AttributeError):
        _loi_khuon()
    return s


def kiem_du_lieu(du_lieu, khuon, tai_lieu, trich_ngoai, duoc_dan, cac_so):
    """Kiểm schema đã khớp, span đúng offset và giá trị trong căn cứ của từng mục.

    Duyệt $ref/nhánh thực sự khớp; annotation trong not/nhánh không khớp không
    được miễn kiểm. Giữ riêng từng vị trí lặp, không dò/chữa offset bằng index.
    """
    spans, loi, ngan_sach = [], [], [100_000]

    def buoc(sau):
        ngan_sach[0] -= 1
        if sau > 64 or ngan_sach[0] < 0:
            raise ValueError

    def lop(v, schemas, sau=0):
        kq = []
        for s in schemas:
            buoc(sau)
            if isinstance(s, bool):
                continue
            kq.append(s)
            if "$ref" in s:
                kq.extend(lop(v, [_tham_chieu(khuon, s["$ref"])], sau + 1))
            kq.extend(lop(v, s.get("allOf", []), sau + 1))
            for k in ("anyOf", "oneOf"):
                kq.extend(lop(v, [a for a in s.get(k, []) if khop(v, a, khuon)], sau + 1))
        return kq

    def span(v):
        if v is None:
            return None
        if (not isinstance(v, dict)
                or not v.keys() <= {"cau", "bat_dau", "ket_thuc", "ma_nguon", "ma_doan"}):
            loi.append("TRICH_DAN_SAI")
            return None
        cau, a, b = (v.get(k) for k in ("cau", "bat_dau", "ket_thuc"))
        if (not isinstance(cau, str) or not cau.strip() or type(a) is not int or type(b) is not int
                or not 0 <= a < b <= len(tai_lieu) or tai_lieu[a:b] != cau):
            loi.append("TRICH_DAN_SAI")
            return None
        t = {"cau": cau, "bat_dau": a, "ket_thuc": b}
        if t not in spans:
            spans.append(t)
        return cau

    def con(layers, ten):
        return [s.get("properties", {}).get(ten, s.get("additionalProperties", True)) for s in layers]

    def items(layers, i):
        return [s.get("prefixItems", [])[i] if i < len(s.get("prefixItems", [])) else s.get("items", True) for s in layers]

    def gia_tri(v, trich):
        if isinstance(v, dict):
            if set(v) == {"so", "tien_te"}:
                # Tiền phải cùng số và mã tiền trong một cụm; không ghép số của
                # khoản này với tiền tệ của khoản khác trong câu trích rộng.
                tt = v["tien_te"]
                if not isinstance(tt, str) or re.fullmatch(r"[A-Z]{3}", tt) is None:
                    return False
                mau = re.compile(r"(?<![\w.,+\-])[+-]?\d+(?:[.,]\d+)*\s+" + tt + r"(?!\w)")
                return any(duoc_dan(v["so"], (m.group(),)) for t in trich for m in mau.finditer(t))
            return all(gia_tri(x, trich) for x in v.values())
        if isinstance(v, list):
            return all(gia_tri(x, trich) for x in v)
        return v is None or duoc_dan(v, trich)

    def duyet(v, schemas, trich, sau=0):
        buoc(sau)
        layers = lop(v, schemas)
        roles = {_vai_tro(s) for s in layers} - {None}
        if "trich_dan" in roles:
            span(v)
            return
        if isinstance(v, dict) and isinstance(v.get("can_cu"), list):
            cc_layers = lop(v["can_cu"], con(layers, "can_cu"))
            # Chỉ scope theo can_cu nếu schema đã đánh dấu citation, không tin tên khóa.
            if any(_vai_tro(s) == "trich_dan" for s in lop(None, items(cc_layers, 0))):
                trich = tuple(t for x in v["can_cu"] if (t := span(x)) is not None)
        if "trich_xuat" in roles:
            if not gia_tri(v, trich):
                loi.append("DU_LIEU_NGOAI_TRICH_DAN")
            return
        if roles == {"metadata"}:
            if isinstance(v, (dict, list)):
                loi.append("VAI_TRO_KHONG_HOP_LE")
            return
        if "tong_hop" in roles:
            # Câu tổng hợp không phải nguyên văn; mọi token số vẫn phải có căn cứ.
            if (not isinstance(v, str) or not set(cac_so.findall(v)) <= {x for t in trich for x in cac_so.findall(t)}):
                loi.append("SO_NGOAI_NGUON")
            return
        if isinstance(v, dict):
            for k, x in v.items():
                duyet(x, con(layers, k), trich, sau + 1)
        elif isinstance(v, list):
            for i, x in enumerate(v):
                duyet(x, items(layers, i), trich, sau + 1)
        elif not gia_tri(v, trich):
            loi.append("DU_LIEU_NGOAI_TRICH_DAN")

    try:
        duyet(du_lieu, [khuon], trich_ngoai)
    except (ValueError, RecursionError):
        loi.append("VUOT_TRAN_HAU_KIEM")
    return spans, loi
