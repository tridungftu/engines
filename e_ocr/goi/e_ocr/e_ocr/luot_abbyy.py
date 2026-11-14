"""Nhật ký lượt ABBYY chỉ giữ metadata, ghi cùng sổ hạn mức trong một giao dịch.

Dấu bền theo pháp nhân + băm; khóa hệ điều hành chỉ ngăn hai tiến trình
cùng đọc/dọn PDF. Không hết hạn lượt chưa rõ theo đồng hồ hoặc lease Core.
"""

from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from uuid import NAMESPACE_URL, uuid5

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .abbyy import LoiABBYYChuaNhan


KHOA_HAN_MUC = "han_muc_abbyy"
DANG_DO = {"dang_gui", "chua_ro"}
DA_CHOT = {"xong", "loi", "huy", "chua_gui", "tu_choi"}


def khoa_nhat_ky(phap_nhan_id, bam):
    if (type(phap_nhan_id) not in (str, int)
            or re.fullmatch(r"[A-Za-z0-9_.:@+-]{1,200}", str(phap_nhan_id)) is None
            or not isinstance(bam, str) or re.fullmatch(r"sha256:[a-f0-9]{64}", bam) is None):
        raise LoiNghiepVu("NGU_CANH_OCR_KHONG_HOP_LE", "Chưa xác định đúng pháp nhân hoặc tài liệu cần nhận dạng.")
    khoa = json.dumps([str(phap_nhan_id), bam], separators=(",", ":")).encode("utf-8")
    return "luot_abbyy." + sha256(khoa).hexdigest()


class NhatKyLuot:
    def __init__(self, so, phap_nhan_id, bam, so_trang):
        self.khoa = khoa_nhat_ky(phap_nhan_id, bam)
        if type(so_trang) is not int or not 1 <= so_trang <= 60:
            raise LoiNghiepVu("NGU_CANH_OCR_KHONG_HOP_LE", "Số trang của lượt ABBYY không hợp lệ.")
        self.so, self.kho = so, so.kho
        self.phap_nhan_id, self.bam, self.so_trang = str(phap_nhan_id), bam, so_trang
        self.ma = None

    def _ma_luot(self, lan_gui):
        return uuid5(NAMESPACE_URL, f"e_ocr:{self.khoa}:{lan_gui}").hex

    def _kiem(self, luot):
        if luot is None:
            return None
        try:
            if (type(luot) is not dict or set(luot) != {
                    "ma_tuong_quan", "phap_nhan_id", "bam", "so_trang", "lan_gui",
                    "trang_thai", "da_nhan", "da_hoan", "luc_giu", "luc_nhan"}
                    or luot["phap_nhan_id"] != self.phap_nhan_id or luot["bam"] != self.bam
                    or type(luot["so_trang"]) is not int or luot["so_trang"] != self.so_trang
                    or type(luot["lan_gui"]) is not int or luot["lan_gui"] < 1
                    or luot["ma_tuong_quan"] != self._ma_luot(luot["lan_gui"])
                    or luot["trang_thai"] not in DANG_DO | DA_CHOT
                    or type(luot["da_nhan"]) is not bool or type(luot["da_hoan"]) is not bool
                    or type(luot["luc_giu"]) is not int or luot["luc_giu"] < 0
                    or (luot["da_nhan"] and (type(luot["luc_nhan"]) is not int or luot["luc_nhan"] < 0))
                    or (not luot["da_nhan"] and luot["luc_nhan"] is not None)
                    or (luot["da_hoan"] != (luot["trang_thai"] in {"chua_gui", "tu_choi"}))
                    or (luot["trang_thai"] in {"xong", "loi", "huy"} and not luot["da_nhan"])
                    or (luot["trang_thai"] == "chua_gui" and luot["da_nhan"])):
                raise ValueError
            return luot
        except (ValueError, TypeError, KeyError):
            raise LoiNghiepVu("NHAT_KY_LUOT_CAN_KIEM_TRA", "Nhật ký lượt ABBYY không hợp lệ. Hãy liên hệ quản trị viên.") from None

    def doc(self):
        luot = self._kiem(self.kho.doc(self.khoa))
        if luot is not None:
            self.ma = luot["ma_tuong_quan"]
        return luot

    def giu(self, han_muc):
        if type(han_muc) is not int or not 0 <= han_muc <= 5000:
            raise LoiNghiepVu("SO_HAN_MUC_CAN_KIEM_TRA", "Hạn mức ABBYY không hợp lệ.")
        moi = False

        def sua(cu):
            nonlocal moi
            so = self.so._doc_so(cu[KHOA_HAN_MUC])
            luot = self._kiem(cu[self.khoa])
            if luot is None or luot["trang_thai"] not in DANG_DO:
                if self.so._tong(so) + sum(so["dang_giu"].values()) + self.so_trang > han_muc:
                    raise LoiABBYYChuaNhan("ABBYY_HET_HAN_MUC", "Không đủ hạn mức ABBYY trong cửa sổ 30 ngày gần nhất.")
                lan = 1 if luot is None else luot["lan_gui"] + 1
                ma = self._ma_luot(lan)
                luot = {"ma_tuong_quan": ma, "phap_nhan_id": self.phap_nhan_id,
                        "bam": self.bam, "so_trang": self.so_trang, "lan_gui": lan,
                        "trang_thai": "dang_gui", "da_nhan": False, "da_hoan": False,
                        "luc_giu": int(self.so.dong_ho()), "luc_nhan": None}
                so["dang_giu"][ma] = self.so_trang
                moi = True
            return {KHOA_HAN_MUC: so, self.khoa: luot}

        luot = self.kho.cap_nhat_nhieu([KHOA_HAN_MUC, self.khoa], sua)[self.khoa]
        self.ma = luot["ma_tuong_quan"]
        return luot, moi

    def cap_nhat(self, trang_thai=None, *, nhan=False):
        """Chốt/nhả đúng một lần; không ghi đè thế hệ mới hoặc hạ trạng thái đã chốt."""
        if trang_thai is not None and trang_thai not in DANG_DO | DA_CHOT:
            raise ValueError("Trạng thái lượt không hợp lệ.")

        def sua(cu):
            so = self.so._doc_so(cu[KHOA_HAN_MUC])
            luot = self._kiem(cu[self.khoa])
            if luot is None:
                raise LoiNghiepVu("NHAT_KY_LUOT_CAN_KIEM_TRA", "Không tìm thấy lượt ABBYY cần đối chiếu.")
            if luot["ma_tuong_quan"] != self.ma or luot["trang_thai"] not in DANG_DO:
                return {KHOA_HAN_MUC: so, self.khoa: luot}
            luot = dict(luot)
            if nhan and not luot["da_nhan"]:
                if so["dang_giu"].pop(self.ma, None) != self.so_trang:
                    raise LoiNghiepVu("SO_HAN_MUC_CAN_KIEM_TRA", "Chưa xác nhận được hạn mức của lượt ABBYY.")
                luc = int(self.so.dong_ho())
                ngay = datetime.fromtimestamp(luc, timezone.utc).date().isoformat()
                giay = so["da_nhan"].setdefault(ngay, {})
                khoa = str(luc % 86400)
                giay[khoa] = giay.get(khoa, 0) + self.so_trang
                luot.update(da_nhan=True, luc_nhan=luc)
            if trang_thai in {"chua_gui", "tu_choi"}:
                if luot["da_nhan"] and trang_thai == "chua_gui":
                    raise LoiNghiepVu("NHAT_KY_LUOT_CAN_KIEM_TRA", "Lượt ABBYY đã được nhận; không thể tự hoàn hạn mức.")
                so["dang_giu"].pop(self.ma, None)
                if luot["da_nhan"]:
                    luc = luot["luc_nhan"]
                    ngay = datetime.fromtimestamp(luc, timezone.utc).date().isoformat()
                    giay = so["da_nhan"].get(ngay, {})
                    khoa = str(luc % 86400)
                    if khoa in giay:
                        if giay[khoa] < self.so_trang:
                            raise LoiNghiepVu("SO_HAN_MUC_CAN_KIEM_TRA", "Sổ hạn mức ABBYY cần được đối chiếu lại.")
                        giay[khoa] -= self.so_trang
                        if not giay[khoa]:
                            del giay[khoa]
                        if not giay:
                            so["da_nhan"].pop(ngay, None)
                luot["da_hoan"] = True
            if trang_thai is not None:
                luot["trang_thai"] = trang_thai
            return {KHOA_HAN_MUC: so, self.khoa: self._kiem(luot)}

        return self.kho.cap_nhat_nhieu([KHOA_HAN_MUC, self.khoa], sua)[self.khoa]
