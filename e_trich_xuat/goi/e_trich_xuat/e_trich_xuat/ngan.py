"""Cổng ngăn tạm theo đề nghị SDK 2.1 §3; chỉ RAM, chờ thay bằng NGAN-0.

Không sao chép toàn kho khi ghi lô: chỉ giữ thay đổi của các khóa/chỉ mục
bị tác động. Khóa luồng bao trọn kiểm điều kiện và chốt lô.
"""

from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
import json
import sys
import threading


class NganXungDot(Exception):
    ma = "NGAN_XUNG_DOT"
    thu_lai_duoc = True

    def __init__(self):
        super().__init__("Dữ liệu đã thay đổi; hãy đọc lại rồi lưu.")


@dataclass(frozen=True)
class BanGhi:
    gia_tri: dict
    row_version: int


class Ngan(ABC):
    @abstractmethod
    def doc(self, bang, khoa):
        """Trả None hoặc bản ghi có gia_tri và row_version."""

    @abstractmethod
    def tim(self, bang, loc=None, gioi_han=100, tiep=None):
        """Trả {danh_sach: [BanGhi], tiep}; tối đa 500 bản ghi/lần."""

    @abstractmethod
    def lo(self):
        """Context manager: ghi nguyên tử khi thoát thành công."""


def _json(v):
    try:
        return json.dumps(v, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError, UnicodeError, RecursionError):
        raise ValueError("Giá trị ngăn phải là JSON hợp lệ.") from None


class NganBoNho(Ngan):
    def __init__(self, khai_bao=None, *, phap_nhan_id=None):
        self._khoa = threading.RLock()
        self._bang = {}
        self._chi_muc = {}
        self._phien_ban = 0
        self._phap_nhan_id = phap_nhan_id
        self._khai = {}
        for k in khai_bao or [{"bang": "cau_hinh", "pham_vi": "engine",
                               "khoa": ["ma"], "duy_nhat": []}]:
            if k.get("pham_vi", "engine") not in ("engine", "phap_nhan"):
                raise ValueError("Phạm vi ngăn không hợp lệ.")
            if not k.get("khoa") or k["bang"] in self._khai:
                raise ValueError("Khai báo bảng ngăn không hợp lệ.")
            self._khai[k["bang"]] = deepcopy(k)

    def _dinh_nghia(self, bang):
        if bang not in self._khai:
            raise ValueError("Bảng ngăn chưa được khai báo.")
        return self._khai[bang]

    def _pham_vi(self, bang, v):
        self._dinh_nghia(bang)
        if not isinstance(v, dict):
            raise ValueError("Khóa và bộ lọc ngăn phải là đối tượng.")
        v = deepcopy(v)
        if self._khai[bang].get("pham_vi") == "phap_nhan":
            p = self._phap_nhan_id
            if p is not None:
                if "phap_nhan_id" in v and v["phap_nhan_id"] != p:
                    raise ValueError("Không được truy cập pháp nhân khác.")
                v["phap_nhan_id"] = p
            if not isinstance(v.get("phap_nhan_id"), str) or not v["phap_nhan_id"]:
                raise ValueError("Cần phạm vi pháp nhân khi truy cập ngăn.")
        return v

    def _cac_khoa(self, bang):
        k = self._dinh_nghia(bang)
        ds = list(k["khoa"])
        if k.get("pham_vi") == "phap_nhan" and "phap_nhan_id" not in ds:
            ds.insert(0, "phap_nhan_id")
        return tuple(ds)

    def _duy_nhat(self, bang):
        ds = [self._cac_khoa(bang)]
        for r in self._khai[bang].get("duy_nhat", []):
            r = tuple(r)
            if self._khai[bang].get("pham_vi") == "phap_nhan" and "phap_nhan_id" not in r:
                r = ("phap_nhan_id",) + r
            if r not in ds:
                ds.append(r)
        return ds

    @staticmethod
    def _gia_tri_khoa(v, truong):
        if any(t not in v or v[t] is None for t in truong):
            raise ValueError("Bản ghi ngăn thiếu khóa hoặc trường duy nhất.")
        return tuple(_json(v[t]) for t in truong)

    def _khoa_chinh(self, bang, khoa):
        if set(khoa) != set(self._cac_khoa(bang)):
            raise ValueError("Khóa đọc ngăn không đúng khai báo.")
        return self._gia_tri_khoa(khoa, self._cac_khoa(bang))

    def doc(self, bang, khoa):
        khoa = self._pham_vi(bang, khoa)
        k = self._khoa_chinh(bang, khoa)
        with self._khoa:
            return deepcopy(self._bang.get(bang, {}).get(k))

    def tim(self, bang, loc=None, gioi_han=100, tiep=None):
        loc = self._pham_vi(bang, {} if loc is None else loc)
        if type(gioi_han) is not int or not 1 <= gioi_han <= 500:
            raise ValueError("Mỗi lần chỉ tìm từ 1 đến 500 bản ghi.")
        try:
            bat_dau = 0 if tiep is None else int(tiep)
            if bat_dau < 0 or (tiep is not None and str(bat_dau) != tiep):
                raise ValueError
        except (TypeError, ValueError):
            raise ValueError("Mốc tìm tiếp không hợp lệ.") from None
        with self._khoa:
            ds = [v for _, v in sorted(self._bang.get(bang, {}).items())
                  if all(v.gia_tri.get(t) == x for t, x in loc.items())]
            cuoi = bat_dau + gioi_han
            return {"danh_sach": deepcopy(ds[bat_dau:cuoi]),
                    "tiep": str(cuoi) if cuoi < len(ds) else None}

    def lo(self):
        return _Lo(self)

    def _ghi_lo(self, cac_lenh):
        if len(cac_lenh) > 100:
            raise ValueError("Một lô chỉ có tối đa 100 lệnh.")
        with self._khoa:
            doi, chi_muc, ket_qua = {}, {}, []
            phien_ban = self._phien_ban

            def doc(bang, k):
                return doi[(bang, k)] if (bang, k) in doi else self._bang.get(bang, {}).get(k)

            def tim_khoa(bang, truong, gia_tri):
                k = (bang, truong, self._gia_tri_khoa(gia_tri, truong))
                return chi_muc[k] if k in chi_muc else self._chi_muc.get(k)

            def doi_chi_muc(bang, ban_ghi, k, moi):
                for truong in self._duy_nhat(bang):
                    cm = (bang, truong, self._gia_tri_khoa(ban_ghi.gia_tri, truong))
                    chi_muc[cm] = k if moi else None

            for thao_tac, bang, khoa, gia_tri, row_version in cac_lenh:
                khoa = self._pham_vi(bang, khoa)
                if thao_tac == "lay_hoac_tao":
                    truong = next((t for t in self._duy_nhat(bang) if set(t) == set(khoa)), None)
                    if truong is None:
                        raise ValueError("Lấy hoặc tạo phải dùng khóa duy nhất đã khai báo.")
                    k = tim_khoa(bang, truong, khoa)
                    cu = doc(bang, k) if k is not None else None
                    if cu is not None:
                        ket_qua.append({"ban_ghi": deepcopy(cu), "row_version": cu.row_version,
                                        "da_tao": False})
                        continue
                else:
                    k = self._khoa_chinh(bang, khoa)
                    cu = doc(bang, k)
                if thao_tac in ("sua", "xoa"):
                    if cu is None or type(row_version) is not int or cu.row_version != row_version:
                        raise NganXungDot()
                elif thao_tac == "them" and cu is not None:
                    raise NganXungDot()
                if thao_tac == "xoa":
                    doi_chi_muc(bang, cu, k, False)
                    doi[(bang, k)] = None
                    phien_ban += 1
                    ket_qua.append({"row_version": phien_ban, "da_tao": False, "ban_ghi": None})
                    continue
                if not isinstance(gia_tri, dict):
                    raise ValueError("Bản ghi ngăn phải là đối tượng.")
                if any(t in gia_tri and gia_tri[t] != x for t, x in khoa.items()):
                    raise ValueError("Giá trị không được đổi khóa của bản ghi.")
                v = self._pham_vi(bang, {**gia_tri, **khoa})
                _json(v).encode("utf-8")
                for x in v.values():
                    if isinstance(x, (dict, list)) and len(_json(x).encode("utf-8")) > 65536:
                        raise ValueError("Giá trị JSON trong ngăn vượt 64 KiB.")
                k = self._gia_tri_khoa(v, self._cac_khoa(bang))
                for truong in self._duy_nhat(bang):
                    trung = tim_khoa(bang, truong, v)
                    if trung is not None and (trung != k or cu is None):
                        raise NganXungDot()
                phien_ban += 1
                moi = BanGhi(deepcopy(v), phien_ban)
                if cu is not None:
                    doi_chi_muc(bang, cu, k, False)
                doi_chi_muc(bang, moi, k, True)
                doi[(bang, k)] = moi
                ket_qua.append({"ban_ghi": deepcopy(moi), "row_version": phien_ban,
                                "da_tao": cu is None})
            for (bang, k), v in doi.items():
                ds = self._bang.setdefault(bang, {})
                if v is None:
                    ds.pop(k, None)
                else:
                    ds[k] = v
            for k, v in chi_muc.items():
                if v is None:
                    self._chi_muc.pop(k, None)
                else:
                    self._chi_muc[k] = v
            self._phien_ban = phien_ban
            return ket_qua


class _Lo:
    def __init__(self, ngan):
        self._ngan, self._lenh = ngan, []
        self._dong = False
        self.ket_qua = []

    def __enter__(self):
        if self._dong:
            raise ValueError("Lô ngăn đã kết thúc.")
        return self

    def __exit__(self, loai_loi, loi, vet):
        self._dong = True
        if loai_loi is None:
            self.ket_qua = self._ngan._ghi_lo(self._lenh)
        return False

    def _them_lenh(self, thao_tac, bang, khoa, gia_tri=None, row_version=None):
        if self._dong or len(self._lenh) >= 100:
            raise ValueError("Lô đã đóng hoặc vượt 100 lệnh.")
        self._lenh.append((thao_tac, bang, deepcopy(khoa), deepcopy(gia_tri), row_version))

    def them(self, bang, khoa, gia_tri):
        self._them_lenh("them", bang, khoa, gia_tri)

    def sua(self, bang, khoa, gia_tri, *, row_version):
        self._them_lenh("sua", bang, khoa, gia_tri, row_version)

    def xoa(self, bang, khoa, *, row_version):
        self._them_lenh("xoa", bang, khoa, row_version=row_version)

    def lay_hoac_tao(self, bang, khoa, gia_tri):
        self._them_lenh("lay_hoac_tao", bang, khoa, gia_tri)


_khoa_chon = threading.Lock()
_da_canh_bao = False


def chon_ngan(app):
    global _da_canh_bao
    with _khoa_chon:
        ngan = getattr(app, "ngan", None)
        if ngan is not None:
            return ngan
        ngan = getattr(app, "_ngan_tam", None)
        if ngan is None:
            ngan = NganBoNho()
            app._ngan_tam = ngan
        if not _da_canh_bao:
            print("Đang lưu tạm trong bộ nhớ; khởi động lại sẽ mất hạn mức/dấu chống trùng",
                  file=sys.stderr, flush=True)
            _da_canh_bao = True
        return ngan
