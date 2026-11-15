"""Cổng ngăn theo đề nghị SDK 2.1; bản thay thế chỉ giữ dữ liệu trong RAM."""

from __future__ import annotations

from abc import ABC, abstractmethod
import base64
from copy import deepcopy
from dataclasses import dataclass
import hmac
import json
import secrets
import sys
from threading import RLock


class NganXungDot(Exception):
    ma = "NGAN_XUNG_DOT"
    thong_diep = "Dữ liệu ngăn đã thay đổi hoặc bị trùng. Hãy đọc lại và thử lại."
    thu_lai_duoc = True

    def __init__(self):
        super().__init__(self.thong_diep)


class NganKhongHopLe(ValueError):
    ma = "NGAN_KHONG_HOP_LE"
    thong_diep = "Yêu cầu ngăn không hợp lệ hoặc vượt giới hạn cho phép."
    thu_lai_duoc = False

    def __init__(self):
        super().__init__(self.thong_diep)


@dataclass(frozen=True, repr=False)
class BanGhi:
    gia_tri: dict
    row_version: int


@dataclass(frozen=True, repr=False)
class TrangNgan:
    danh_sach: list[BanGhi]
    tiep: str | None


class KetQuaLenh:
    """Chỉ đọc sau khi thoát with thành công; không công bố kết quả lô hỏng."""

    def __init__(self):
        self._ket_qua = None

    @property
    def ban_ghi(self):
        if self._ket_qua is None:
            raise NganKhongHopLe()
        return self._ket_qua[0]

    @property
    def row_version(self):
        return self.ban_ghi.row_version

    @property
    def gia_tri(self):
        return self.ban_ghi.gia_tri

    @property
    def da_tao(self):
        self.ban_ghi  # Kiểm lô đã được ghi.
        return self._ket_qua[1]


class LoNgan(ABC):
    @abstractmethod
    def __enter__(self): ...

    @abstractmethod
    def __exit__(self, loai_loi, loi, vet): ...

    @abstractmethod
    def them(self, bang, khoa, gia_tri) -> KetQuaLenh: ...

    @abstractmethod
    def sua(self, bang, khoa, gia_tri, *, row_version) -> KetQuaLenh: ...

    @abstractmethod
    def xoa(self, bang, khoa, *, row_version) -> KetQuaLenh: ...

    @abstractmethod
    def lay_hoac_tao(self, bang, khoa, gia_tri) -> KetQuaLenh: ...


class Ngan(ABC):
    @abstractmethod
    def doc(self, bang, khoa) -> BanGhi | None: ...

    @abstractmethod
    def tim(self, bang, loc=None, gioi_han=100, tiep=None) -> TrangNgan: ...

    @abstractmethod
    def lo(self) -> LoNgan: ...

    @abstractmethod
    def cho_phap_nhan(self, phap_nhan_id) -> Ngan: ...


def _json(gia_tri):
    """Chuẩn hóa khóa và từ chối đối tượng ngoài miền JSON, kể cả NaN."""
    def kiem(v):
        if type(v) is dict:
            if any(type(k) is not str for k in v):
                raise NganKhongHopLe()
            for x in v.values():
                kiem(x)
        elif type(v) is list:
            for x in v:
                kiem(x)
        elif v is not None and type(v) not in (str, int, float, bool):
            raise NganKhongHopLe()
    try:
        kiem(gia_tri)
        chuoi = json.dumps(gia_tri, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":"), allow_nan=False)
        chuoi.encode("utf-8")
        return chuoi
    except (ValueError, TypeError, RecursionError, UnicodeError):
        raise NganKhongHopLe() from None


def _ma_json(v):
    """So sánh giá trị JSON: 1 == 1.0, nhưng true khác 1, cả khi lồng nhau."""
    def chuan(x):
        if type(x) is float and x.is_integer():
            return int(x)
        if type(x) is dict:
            return {k: chuan(y) for k, y in x.items()}
        if type(x) is list:
            return [chuan(y) for y in x]
        return x
    return _json(chuan(v))


class _LopGhi:
    """Overlay của một lô; None là dấu xóa. Không sửa kho trước khi đạt."""

    def __init__(self, goc):
        self._goc = goc
        self._moi = {}

    def get(self, khoa):
        if khoa in self._moi:
            return self._moi[khoa]
        return self._goc.get(khoa)

    def __setitem__(self, khoa, gia_tri):
        self._moi[khoa] = gia_tri

    def __delitem__(self, khoa):
        self._moi[khoa] = None

    def ap_dung(self):
        for khoa, gia_tri in self._moi.items():
            if gia_tri is None:
                self._goc.pop(khoa, None)
            else:
                self._goc[khoa] = gia_tri


class NganBoNho(Ngan):
    """khai_bao là danh sách ngan_du_lieu; cau_hinh luôn có khóa {}.

    Mỗi đối tượng gốc thuộc một engine. Các view pháp nhân chia sẻ cùng dữ liệu
    và cùng khóa luồng; tạo gốc mới sẽ có ngăn độc lập hoàn toàn.
    """

    def __init__(self, khai_bao=(), *, phap_nhan_id=None):
        self._khoa_luong = RLock()
        self._du_lieu = {}
        self._chi_muc = {}
        self._phien_ban = 0
        self._khoa_tiep = secrets.token_bytes(32)
        self._khai_bao = {"cau_hinh": {"bang": "cau_hinh", "khoa": [],
                                         "pham_vi": "engine", "duy_nhat": []}}
        try:
            for muc in deepcopy(khai_bao):
                _json(muc)
                ten = muc["bang"]
                if not isinstance(ten, str) or not ten or (ten in self._khai_bao and ten != "cau_hinh"):
                    raise NganKhongHopLe()
                if ten == "cau_hinh":
                    if (muc.get("khoa") != [] or muc.get("pham_vi", "engine") != "engine"
                            or muc.get("duy_nhat", [])):
                        raise NganKhongHopLe()
                    continue
                if muc.get("pham_vi", "engine") not in ("engine", "phap_nhan"):
                    raise NganKhongHopLe()
                cac_khoa = [muc["khoa"], *muc.get("duy_nhat", [])]
                if any(not isinstance(k, list) or not k or len(k) != len(set(k))
                       or any(not isinstance(t, str) or not t for t in k)
                       for k in cac_khoa):
                    raise NganKhongHopLe()
                self._khai_bao[ten] = muc
        except (KeyError, TypeError):
            raise NganKhongHopLe() from None
        self._goc = self
        self._phap_nhan_id = self._kiem_phap_nhan(phap_nhan_id)

    @staticmethod
    def _kiem_phap_nhan(p):
        if p is not None and (type(p) is not str or not p.strip()):
            raise NganKhongHopLe()
        _json(p)
        return p

    def cho_phap_nhan(self, phap_nhan_id):
        p = self._kiem_phap_nhan(phap_nhan_id)
        if p is None or (self._phap_nhan_id is not None and p != self._phap_nhan_id):
            raise NganKhongHopLe()
        moi = object.__new__(NganBoNho)
        moi._goc = self._goc
        moi._phap_nhan_id = p
        return moi

    def _bang(self, bang, khoa):
        if not isinstance(bang, str) or bang not in self._goc._khai_bao:
            raise NganKhongHopLe()
        muc = self._goc._khai_bao[bang]
        p = None
        if muc.get("pham_vi", "engine") == "phap_nhan":
            if type(khoa) is not dict:
                raise NganKhongHopLe()
            p = self._kiem_phap_nhan(khoa.get("phap_nhan_id", self._phap_nhan_id))
            if p is None:
                raise NganKhongHopLe()
            if self._phap_nhan_id is not None and p != self._phap_nhan_id:
                raise NganKhongHopLe()
        return muc, p

    def _gia_tri(self, gia_tri, p):
        if type(gia_tri) is not dict:
            raise NganKhongHopLe()
        _json(gia_tri)
        v = deepcopy(gia_tri)
        if p is not None:
            if "phap_nhan_id" in v and v["phap_nhan_id"] != p:
                raise NganKhongHopLe()
            v["phap_nhan_id"] = p
        return v

    def _bo_khoa(self, muc, p):
        return [set(k) | ({"phap_nhan_id"} if p is not None else set())
                for k in [muc["khoa"], *muc.get("duy_nhat", [])]]

    def _ma_chi_muc(self, bang, p, bo, v):
        return bang, p, tuple(sorted(bo)), _ma_json({k: v[k] for k in bo})

    def _chon(self, du_lieu, chi_muc, bang, khoa):
        muc, p = self._bang(bang, khoa)
        khoa = self._gia_tri(khoa, p)
        if set(khoa) not in self._bo_khoa(muc, p):
            raise NganKhongHopLe()
        ma = chi_muc.get(self._ma_chi_muc(bang, p, khoa.keys(), khoa))
        return ma, du_lieu.get(ma)

    def doc(self, bang, khoa):
        with self._goc._khoa_luong:
            return deepcopy(self._chon(self._goc._du_lieu, self._goc._chi_muc, bang, khoa)[1])

    def _ma_tiep(self, noi_dung):
        than = _json(noi_dung).encode("utf-8")
        chu_ky = hmac.digest(self._goc._khoa_tiep, than, "sha256")
        return base64.urlsafe_b64encode(chu_ky + than).decode("ascii")

    def _doc_tiep(self, tiep):
        try:
            raw = base64.b64decode(tiep, altchars=b"-_", validate=True)
            if not hmac.compare_digest(raw[:32], hmac.digest(self._goc._khoa_tiep, raw[32:], "sha256")):
                raise ValueError
            return json.loads(raw[32:])
        except (ValueError, TypeError, UnicodeError):
            raise NganKhongHopLe() from None

    def tim(self, bang, loc=None, gioi_han=100, tiep=None):
        loc = {} if loc is None else loc
        _, p = self._bang(bang, loc)
        loc = self._gia_tri(loc, p)
        if type(gioi_han) is not int or not 1 <= gioi_han <= 500:
            raise NganKhongHopLe()
        truy_van = [bang, p, loc]
        sau = ""
        if tiep is not None:
            con_tro = self._doc_tiep(tiep)
            if _ma_json(con_tro["truy_van"]) != _ma_json(truy_van):
                raise NganKhongHopLe()
            sau = con_tro["sau"]
        with self._goc._khoa_luong:
            ds = sorted((ma[2], ban) for ma, ban in self._goc._du_lieu.items()
                        if ma[:2] == (bang, p) and ma[2] > sau
                        and all(k in ban.gia_tri and _ma_json(ban.gia_tri[k]) == _ma_json(v)
                                for k, v in loc.items()))
            trang = ds[:gioi_han]
            moi = (self._ma_tiep({"truy_van": truy_van, "sau": trang[-1][0]})
                   if len(ds) > gioi_han else None)
            return TrangNgan(deepcopy([ban for _, ban in trang]), moi)

    def lo(self):
        return _LoBoNho(self)

    def _thuc_hien(self, du_lieu, chi_muc, phien_ban, lenh):
        thao_tac, bang, khoa, gia_tri, row_version = lenh
        muc, p = self._bang(bang, khoa)
        ma, cu = self._chon(du_lieu, chi_muc, bang, khoa)
        if thao_tac == "lay_hoac_tao" and cu is not None:
            return phien_ban, (deepcopy(cu), False)
        if thao_tac in ("sua", "xoa"):
            if type(row_version) is not int or row_version < 1:
                raise NganKhongHopLe()
            if cu is None or cu.row_version != row_version:
                raise NganXungDot()
        elif cu is not None:
            raise NganXungDot()
        if thao_tac == "xoa":
            del du_lieu[ma]
            for bo in self._bo_khoa(muc, p):
                del chi_muc[self._ma_chi_muc(bang, p, bo, cu.gia_tri)]
            return phien_ban + 1, (BanGhi(deepcopy(cu.gia_tri), phien_ban + 1), False)
        gia_tri = self._gia_tri(gia_tri, p)
        if any(k in gia_tri and _ma_json(gia_tri[k]) != _ma_json(v) for k, v in khoa.items()):
            raise NganKhongHopLe()
        v = {**(cu.gia_tri if cu else {}), **khoa, **gia_tri}
        if any(not k <= v.keys() for k in self._bo_khoa(muc, p)):
            raise NganKhongHopLe()
        khoa_chinh = {k: v[k] for k in muc["khoa"]}
        moi_ma = (bang, p, _ma_json(khoa_chinh))
        if thao_tac == "them" and set(khoa) != self._bo_khoa(muc, p)[0]:
            raise NganKhongHopLe()
        if cu is not None and moi_ma != ma:
            raise NganKhongHopLe()
        for bo in self._bo_khoa(muc, p):
            ma_khac = chi_muc.get(self._ma_chi_muc(bang, p, bo, v))
            if ma_khac is not None and ma_khac != ma:
                raise NganXungDot()
        if cu is not None:
            for bo in self._bo_khoa(muc, p):
                del chi_muc[self._ma_chi_muc(bang, p, bo, cu.gia_tri)]
        for bo in self._bo_khoa(muc, p):
            chi_muc[self._ma_chi_muc(bang, p, bo, v)] = moi_ma
        phien_ban += 1
        moi = BanGhi(deepcopy(v), phien_ban)
        du_lieu[moi_ma] = moi
        return phien_ban, (deepcopy(moi), cu is None)


class _LoBoNho(LoNgan):
    def __init__(self, ngan):
        self._ngan = ngan
        self._lenh = []
        self._mo = False
        self._da_dung = False
        self._loi = False

    def __enter__(self):
        if self._da_dung:
            raise NganKhongHopLe()
        self._da_dung = self._mo = True
        return self

    def _them_lenh(self, thao_tac, bang, khoa, gia_tri=None, row_version=None):
        if not self._mo or self._loi or len(self._lenh) >= 100:
            self._loi = True
            raise NganKhongHopLe()
        try:
            _, p = self._ngan._bang(bang, khoa)
            khoa = self._ngan._gia_tri(khoa, p)
            if gia_tri is not None:
                gia_tri = self._ngan._gia_tri(gia_tri, p)
        except NganKhongHopLe:
            self._loi = True
            raise
        kq = KetQuaLenh()
        self._lenh.append(((thao_tac, bang, khoa, gia_tri, row_version), kq))
        return kq

    def them(self, bang, khoa, gia_tri):
        return self._them_lenh("them", bang, khoa, gia_tri)

    def sua(self, bang, khoa, gia_tri, *, row_version):
        return self._them_lenh("sua", bang, khoa, gia_tri, row_version)

    def xoa(self, bang, khoa, *, row_version):
        return self._them_lenh("xoa", bang, khoa, row_version=row_version)

    def lay_hoac_tao(self, bang, khoa, gia_tri):
        return self._them_lenh("lay_hoac_tao", bang, khoa, gia_tri)

    def __exit__(self, loai_loi, loi, vet):
        if not self._mo:
            raise NganKhongHopLe()
        self._mo = False
        if loai_loi is not None:
            return False
        if self._loi:
            raise NganKhongHopLe()
        goc = self._ngan._goc
        with goc._khoa_luong:
            du_lieu = _LopGhi(goc._du_lieu)
            chi_muc = _LopGhi(goc._chi_muc)
            phien_ban = goc._phien_ban
            ket_qua = []
            for lenh, _ in self._lenh:
                phien_ban, kq = self._ngan._thuc_hien(du_lieu, chi_muc, phien_ban, lenh)
                ket_qua.append(kq)
            du_lieu.ap_dung()
            chi_muc.ap_dung()
            goc._phien_ban = phien_ban
            for (_, cho), kq in zip(self._lenh, ket_qua):
                cho._ket_qua = kq
        return False


_KHOA_CHON = RLock()
_DA_CANH_BAO = False


def chon_ngan(app):
    """Ưu tiên app.ngan; tái sử dụng RAM khi app cho gắn thuộc tính ngan.

    SDK 2.0: engine tự truyền khai báo vào NganBoNho rồi gắn app.ngan trước
    khi gọi hàm này, vì phiếu 2.0 chưa cho phép trường ngan_du_lieu.
    App không cho gắn (ví dụ __slots__) thì caller giữ ngăn được trả về.
    """
    global _DA_CANH_BAO
    with _KHOA_CHON:
        ngan = getattr(app, "ngan", None)
        if ngan is None:
            ngan = NganBoNho(getattr(app, "phieu", {}).get("ngan_du_lieu", []))
            try:
                app.ngan = ngan
            except AttributeError:
                pass  # App dùng __slots__ không có chỗ gắn; caller giữ ngăn trả về.
        if isinstance(ngan, NganBoNho) and not _DA_CANH_BAO:
            print("Đang lưu tạm trong bộ nhớ; khởi động lại sẽ mất hạn mức/dấu chống trùng",
                  file=sys.stderr)
            _DA_CANH_BAO = True
        return ngan
