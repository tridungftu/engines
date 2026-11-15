"""Lượt ABBYY và hạn mức cùng lô ngăn; phương án B, không lưu trên máy."""

from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from uuid import NAMESPACE_URL, uuid4, uuid5

from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu

from .abbyy import LoiABBYYChuaNhan
from .ngan import NganXungDot


DANG_DO = {"dang_gui", "chua_ro"}
DA_CHOT = {"xong", "loi", "huy", "chua_gui", "tu_choi"}
HAN_XU_LY_GIAY = 30


def khoa_nhat_ky(phap_nhan_id, bam):
    if (type(phap_nhan_id) not in (str, int)
            or re.fullmatch(r"[A-Za-z0-9_.:@+-]{1,200}", str(phap_nhan_id)) is None
            or not isinstance(bam, str) or re.fullmatch(r"sha256:[a-f0-9]{64}", bam) is None):
        raise LoiNghiepVu("NGU_CANH_OCR_KHONG_HOP_LE", "Chưa xác định đúng pháp nhân hoặc tài liệu cần nhận dạng.")
    khoa = json.dumps([str(phap_nhan_id), bam], separators=(",", ":")).encode("utf-8")
    return "luot_abbyy." + sha256(khoa).hexdigest()


def tim_luot(ngan, phap_nhan_id, bam):
    khoa_nhat_ky(phap_nhan_id, bam)
    ds = ngan.tim("luot_abbyy", loc={"phap_nhan_id": str(phap_nhan_id), "bam_noi_dung": bam}, gioi_han=2)
    if len(ds.danh_sach) > 1:
        raise LoiNghiepVu("NHAT_KY_LUOT_CAN_KIEM_TRA", "Nhật ký lượt ABBYY cần được đối chiếu.")
    return ds.danh_sach[0] if ds.danh_sach else None


class NhatKyLuot:
    def __init__(self, so, phap_nhan_id, bam, so_trang):
        self.khoa = khoa_nhat_ky(phap_nhan_id, bam)
        if type(so_trang) is not int or not 1 <= so_trang <= 60:
            raise LoiNghiepVu("NGU_CANH_OCR_KHONG_HOP_LE", "Số trang của lượt ABBYY không hợp lệ.")
        self.so, self.ngan = so, so.ngan
        self.phap_nhan_id, self.bam, self.so_trang = str(phap_nhan_id), bam, so_trang
        self.ma, self.chu = None, None
        self._da_nam_quyen = False
        self._da_doc, self._da_thay = False, None

    def _ma_luot(self, lan_gui):
        return uuid5(NAMESPACE_URL, f"e_ocr:{self.khoa}:{lan_gui}").hex

    def _khoa(self, ma=None):
        return {"phap_nhan_id": self.phap_nhan_id, "ma_tuong_quan": ma or self.ma}

    def _kiem(self, luot):
        if luot is None:
            return None
        try:
            if (type(luot) is not dict or set(luot) != {
                    "ma_tuong_quan", "phap_nhan_id", "bam_noi_dung", "so_trang", "lan_gui",
                    "trang_thai", "da_nhan", "da_hoan", "luc_giu", "luc_nhan", "chu_xu_ly", "han_xu_ly"}
                    or luot["phap_nhan_id"] != self.phap_nhan_id or luot["bam_noi_dung"] != self.bam
                    or type(luot["so_trang"]) is not int or luot["so_trang"] != self.so_trang
                    or type(luot["lan_gui"]) is not int or luot["lan_gui"] < 1
                    or luot["ma_tuong_quan"] != self._ma_luot(luot["lan_gui"])
                    or luot["trang_thai"] not in DANG_DO | DA_CHOT
                    or type(luot["da_nhan"]) is not bool or type(luot["da_hoan"]) is not bool
                    or type(luot["luc_giu"]) is not int or luot["luc_giu"] < 0
                    or (luot["da_nhan"] and (type(luot["luc_nhan"]) is not int or luot["luc_nhan"] < 0))
                    or (not luot["da_nhan"] and luot["luc_nhan"] is not None)
                    or luot["da_hoan"] != (luot["trang_thai"] in {"chua_gui", "tu_choi"})
                    or (luot["trang_thai"] in {"xong", "loi", "huy"} and not luot["da_nhan"])
                    or (luot["trang_thai"] == "chua_gui" and luot["da_nhan"])
                    or (luot["chu_xu_ly"] is not None and
                        (not isinstance(luot["chu_xu_ly"], str) or re.fullmatch(r"[a-f0-9]{32}", luot["chu_xu_ly"]) is None))
                    or type(luot["han_xu_ly"]) is not int or luot["han_xu_ly"] < 0):
                raise ValueError
            return luot
        except (ValueError, TypeError, KeyError):
            raise LoiNghiepVu("NHAT_KY_LUOT_CAN_KIEM_TRA", "Nhật ký lượt ABBYY không hợp lệ. Hãy liên hệ quản trị viên.") from None

    def doc(self):
        b = tim_luot(self.ngan, self.phap_nhan_id, self.bam)
        luot = self._kiem(None if b is None else b.gia_tri)
        if luot is not None:
            self.ma = luot["ma_tuong_quan"]
        self._da_doc = True
        self._da_thay = None if luot is None else (luot["ma_tuong_quan"], luot["trang_thai"])
        return luot

    def giu(self, han_muc):
        if type(han_muc) is not int or not 0 <= han_muc <= 5000:
            raise LoiNghiepVu("SO_HAN_MUC_CAN_KIEM_TRA", "Hạn mức ABBYY không hợp lệ.")
        for _ in range(12):
            anh, so = self.so._doc()
            b = tim_luot(self.ngan, self.phap_nhan_id, self.bam)
            cu = self._kiem(None if b is None else b.gia_tri)
            # Việc khác đã bắt đầu/kết thúc kể từ lần đọc đầu: nhập lượt đó,
            # không tạo thế hệ mới từ một quyết định đọc đã cũ (nợ OCR-4 #1).
            hien_tai = None if cu is None else (cu["ma_tuong_quan"], cu["trang_thai"])
            if self._da_doc and hien_tai != self._da_thay and cu is not None:
                self.ma = cu["ma_tuong_quan"]
                return cu, False
            if cu is not None and cu["trang_thai"] in DANG_DO:
                self.ma = cu["ma_tuong_quan"]
                return cu, False
            if self.so._tong(so) + sum(so["dang_giu"].values()) + self.so_trang > han_muc:
                raise LoiABBYYChuaNhan("ABBYY_HET_HAN_MUC", "Không đủ hạn mức ABBYY trong cửa sổ 30 ngày gần nhất.")
            lan = 1 if cu is None else cu["lan_gui"] + 1
            ma = self._ma_luot(lan)
            luot = {"ma_tuong_quan": ma, "phap_nhan_id": self.phap_nhan_id,
                    "bam_noi_dung": self.bam, "so_trang": self.so_trang, "lan_gui": lan,
                    "trang_thai": "dang_gui", "da_nhan": False, "da_hoan": False,
                    "luc_giu": int(self.so.dong_ho()), "luc_nhan": None,
                    "chu_xu_ly": None, "han_xu_ly": 0}
            so["dang_giu"][ma] = self.so_trang
            try:
                with self.ngan.lo() as lo:
                    if b is not None:
                        lo.xoa("luot_abbyy", self._khoa(cu["ma_tuong_quan"]), row_version=b.row_version)
                    ket_qua = lo.lay_hoac_tao("luot_abbyy",
                                   {"phap_nhan_id": self.phap_nhan_id, "bam_noi_dung": self.bam}, luot)
                    self.so._ghi(lo, anh, so)
                luot = self._kiem(ket_qua.gia_tri)
                self.ma = luot["ma_tuong_quan"]
                return luot, ket_qua.da_tao
            except NganXungDot:
                continue
        self._xung_dot()

    @staticmethod
    def _xung_dot():
        raise LoiNghiepVu("NGAN_XUNG_DOT", "Dữ liệu OCR vừa thay đổi. Hãy thử lại.", thu_lai_duoc=True)

    def _kiem_quyen(self, luot):
        if self.chu is not None and (luot["chu_xu_ly"] != self.chu or
                                    luot["han_xu_ly"] <= self.so.dong_ho()):
            raise ChuaRo(self.ma)

    def _ghi_chua_ro(self, lo, luot, trang_thai_cu):
        """Chỉ tổng số theo ngày UTC, không đưa định danh ra phạm vi engine."""
        cu_chua_ro = trang_thai_cu == "chua_ro"
        moi_chua_ro = luot["trang_thai"] == "chua_ro"
        if cu_chua_ro == moi_chua_ro:
            return
        khoa = {"ma": "chua_ro"}
        cu = self.ngan.doc("trang_thai_engine", khoa)
        theo_ngay = {} if cu is None else dict(cu.gia_tri["theo_ngay"])
        ngay = datetime.fromtimestamp(luot["luc_giu"], timezone.utc).date().isoformat()
        dem = theo_ngay.get(ngay, 0) + (1 if moi_chua_ro else -1)
        if dem < 0:
            raise LoiNghiepVu("NHAT_KY_LUOT_CAN_KIEM_TRA", "Số lượt chưa rõ cần được đối chiếu lại.")
        if dem:
            theo_ngay[ngay] = dem
        else:
            theo_ngay.pop(ngay, None)
        gia_tri = {"so_luot": sum(theo_ngay.values()), "theo_ngay": theo_ngay}
        if cu is None:
            lo.them("trang_thai_engine", khoa, gia_tri)
        else:
            lo.sua("trang_thai_engine", khoa, gia_tri, row_version=cu.row_version)

    def cap_nhat(self, trang_thai=None, *, nhan=False):
        if trang_thai is not None and trang_thai not in DANG_DO | DA_CHOT:
            raise ValueError("Trạng thái lượt không hợp lệ.")
        for _ in range(12):
            anh, so = self.so._doc()
            b = self.ngan.doc("luot_abbyy", self._khoa())
            if b is None:
                raise ChuaRo(self.ma)
            luot = self._kiem(b.gia_tri)
            self._kiem_quyen(luot)
            if luot["trang_thai"] not in DANG_DO:
                return luot
            trang_thai_cu = luot["trang_thai"]
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
            try:
                with self.ngan.lo() as lo:
                    lo.sua("luot_abbyy", self._khoa(), self._kiem(luot), row_version=b.row_version)
                    self._ghi_chua_ro(lo, luot, trang_thai_cu)
                    self.so._ghi(lo, anh, so)
                return luot
            except NganXungDot:
                continue
        self._xung_dot()

    def _quyen(self, *, nha=False):
        for _ in range(12):
            b = self.ngan.doc("luot_abbyy", self._khoa())
            if b is None:
                raise ChuaRo(self.ma)
            luot = self._kiem(b.gia_tri)
            luc = int(self.so.dong_ho())
            if nha:
                if luot["chu_xu_ly"] != self.chu:
                    return
                luot.update(chu_xu_ly=None, han_xu_ly=0)
            else:
                if self._da_nam_quyen and (luot["chu_xu_ly"] != self.chu or luot["han_xu_ly"] <= luc):
                    raise ChuaRo(self.ma)
                if (luot["trang_thai"] not in DANG_DO or
                        (luot["chu_xu_ly"] not in {None, self.chu} and luot["han_xu_ly"] > luc)):
                    raise ChuaRo(self.ma)
                if luot["chu_xu_ly"] == self.chu and luot["han_xu_ly"] > luc + 10:
                    return
                # Hết quyền xử lý chỉ cho đọc lại. Không hết hạn dấu lượt hay hoàn trang.
                luot.update(chu_xu_ly=self.chu, han_xu_ly=luc + HAN_XU_LY_GIAY)
            try:
                with self.ngan.lo() as lo:
                    lo.sua("luot_abbyy", self._khoa(), luot, row_version=b.row_version)
                if not nha:
                    self._da_nam_quyen = True
                return
            except NganXungDot:
                continue
        self._xung_dot()

    @contextmanager
    def xu_ly(self, viec):
        self.chu = uuid4().hex
        self._da_nam_quyen = False
        self._quyen()
        nk = self

        class ViecNguon:
            def __getattr__(self, ten):
                return getattr(viec, ten)

            def kiem_huy(self):
                viec.kiem_huy()
                # CAS kiểm quyền trước mỗi thao tác nguồn, chặn worker cũ đã mất quyền.
                nk._quyen()

        try:
            yield ViecNguon()
        finally:
            self._quyen(nha=True)
            self.chu = None
