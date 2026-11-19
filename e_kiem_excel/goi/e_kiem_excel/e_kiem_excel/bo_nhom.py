"""Bộ nhóm do module truyền; từ khóa là dữ liệu, không phải regex thực thi."""

from hashlib import sha256
import json
import re

from kho_tri_thuc_sdk.engine import LoiNghiepVu
from .chuan_hoa import bo_dau

VUNG = {"tieu_de_cot", "ten_sheet", "nhan_dong"}
CHUA_PHAN_NHOM = "Chưa phân nhóm"
NGOAI_NHOM = "Ngoài nhóm — cần giải thích"
TAI_LIEU_NGOAI = "Yêu cầu nhà thầu giải trình nguồn"


def sai_tham_so():
    raise LoiNghiepVu("THAM_SO_KHONG_HOP_LE", "Cài đặt bước chưa đúng. Quản trị viên kiểm tra lại cài đặt của quy trình.")


def _khong_trung(cap):
    d = {}
    for k, v in cap:
        if k in d:
            sai_tham_so()
        d[k] = v
    return d


def doc_json(chuoi, tran):
    if not isinstance(chuoi, str):
        sai_tham_so()
    try:
        if len(chuoi.encode("utf-8")) > tran:
            sai_tham_so()
        return json.loads(chuoi, object_pairs_hook=_khong_trung,
                          parse_constant=lambda _: sai_tham_so())
    except (ValueError, UnicodeError, RecursionError):
        sai_tham_so()


def kiem_tu_khoa(tu):
    if not isinstance(tu, str) or not tu.strip() or (tu.startswith("=") and not tu[1:].strip()):
        sai_tham_so()
    return tu


def khop_tu_khoa(tu, van_ban):
    """Chứa chuỗi; = khớp nguyên từ Unicode; # khớp >=1 chữ số.

    Mọi ký tự khác (kể cả .*|[]()) được hiểu nguyên văn. Không có cửa regex.
    Hàm dùng chung cho khuôn cột; tự chuẩn hóa cả hai phía.
    """
    kiem_tu_khoa(tu)
    nguyen_tu = tu.startswith("=")
    tu = bo_dau(tu[1:] if nguyen_tu else tu)
    van_ban = bo_dau(van_ban)
    # Gộp ## để tránh nhiều lượng từ kề nhau. Chỉ mẫu do engine tạo được chạy.
    mau = r"\d+".join(re.escape(x) for x in re.split(r"#+", tu))
    if nguyen_tu:
        mau = r"(?<!\w)" + mau + r"(?!\w)"
    return re.search(mau, van_ban) is not None


class BoNhom:
    def __init__(self, du_lieu):
        self.du_lieu = du_lieu
        raw = json.dumps(du_lieu, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.tham_chieu = {"ten_bo": du_lieu["ten_bo"], "bam": "sha256:" + sha256(raw).hexdigest()}

    def tim(self, tieu_de_cot, nhan_dong="", ten_sheet=""):
        vung = dict(tieu_de_cot=tieu_de_cot, nhan_dong=nhan_dong, ten_sheet=ten_sheet)
        for nhom in self.du_lieu["nhom"]:
            for dk in nhom["khi"]:
                t = " ".join(str(vung[v] or "") for v in dk["vung"])
                if (all(any(khop_tu_khoa(tu, t) for tu in ds) for ds in dk["tat_ca"])
                        and not any(khop_tu_khoa(tu, t) for tu in dk.get("khong_co", []))):
                    return nhom
        return None

    def tai_lieu(self, ten):
        return next((n["tai_lieu"] for n in self.du_lieu["nhom"] if n["ten"] == ten), "")


def doc_bo_nhom(chuoi):
    if chuoi == "":
        return None
    d = doc_json(chuoi, 32768)
    if (not isinstance(d, dict) or set(d) != {"phien_ban", "ten_bo", "nhom"}
            or type(d["phien_ban"]) is not int or d["phien_ban"] != 1
            or not isinstance(d["ten_bo"], str) or not d["ten_bo"].strip()
            or not isinstance(d["nhom"], list) or not 1 <= len(d["nhom"]) <= 30):
        sai_tham_so()
    ma, ten, so_tu = set(), set(), 0
    for n in d["nhom"]:
        if (not isinstance(n, dict) or set(n) != {"ma", "ten", "tai_lieu", "khi"}
                or any(not isinstance(n[k], str) or not n[k].strip() for k in ("ma", "ten", "tai_lieu"))
                or n["ma"] in ma or n["ten"] in ten or n["ten"] in {NGOAI_NHOM, CHUA_PHAN_NHOM}
                or not isinstance(n["khi"], list) or not n["khi"]):
            sai_tham_so()
        ma.add(n["ma"]); ten.add(n["ten"])
        for dk in n["khi"]:
            if (not isinstance(dk, dict) or not {"vung", "tat_ca"} <= set(dk)
                    or set(dk) - {"vung", "tat_ca", "khong_co"}
                    or not isinstance(dk["vung"], list) or not dk["vung"]
                    or any(not isinstance(v, str) or v not in VUNG for v in dk["vung"])
                    or len(set(dk["vung"])) != len(dk["vung"])
                    or not isinstance(dk["tat_ca"], list) or not dk["tat_ca"]
                    or not isinstance(dk.get("khong_co", []), list)):
                sai_tham_so()
            if any(not isinstance(ds, list) or not ds for ds in dk["tat_ca"]):
                sai_tham_so()
            for ds in dk["tat_ca"] + [dk.get("khong_co", [])]:
                for tu in ds:
                    kiem_tu_khoa(tu)
                    so_tu += 1
                    if so_tu > 200:
                        sai_tham_so()
    return BoNhom(d)
