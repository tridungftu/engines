"""Cổng ngăn tạm theo SDK 2.1 §3; chờ thay nguyên tệp bằng NGAN-0.

Chỉ RAM, không có cấu hình hay dữ liệu ghi ra máy. Kết quả đọc là bản sao.
"""

from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path
import sys
from threading import RLock


class NganXungDot(Exception):
    ma = "NGAN_XUNG_DOT"
    thu_lai_duoc = True

    def __init__(self):
        super().__init__("Dữ liệu vừa thay đổi. Hãy thử lại.")


@dataclass
class BanGhi:
    gia_tri: dict
    row_version: int
    da_tao: bool = False


class Ngan:
    def doc(self, bang, khoa, *, phap_nhan_id=None):
        raise NotImplementedError

    def tim(self, bang, loc=None, gioi_han=100, tiep=None, *, phap_nhan_id=None):
        raise NotImplementedError

    def lo(self, *, phap_nhan_id=None):
        raise NotImplementedError


class _Lo:
    def __init__(self, ngan, phap_nhan_id):
        self.ngan, self.phap_nhan_id = ngan, phap_nhan_id
        self.lenh, self.ket_qua = [], []

    def __enter__(self):
        return self

    def __exit__(self, loai, loi, vet):
        if loai is None:
            self.ket_qua = self.ngan._ghi_lo(self.lenh, self.phap_nhan_id)

    def _them_lenh(self, thao_tac, bang, khoa, gia_tri=None, row_version=None):
        if len(self.lenh) >= 100:
            raise ValueError("Một lô chỉ được có tối đa 100 lệnh.")
        self.lenh.append(deepcopy((thao_tac, bang, khoa, gia_tri, row_version)))

    def them(self, bang, khoa, gia_tri):
        self._them_lenh("them", bang, khoa, gia_tri)

    def sua(self, bang, khoa, gia_tri, *, row_version):
        self._them_lenh("sua", bang, khoa, gia_tri, row_version)

    def xoa(self, bang, khoa, *, row_version):
        self._them_lenh("xoa", bang, khoa, row_version=row_version)

    def lay_hoac_tao(self, bang, khoa, gia_tri):
        self._them_lenh("lay_hoac_tao", bang, khoa, gia_tri)


class NganBoNho(Ngan):
    """Bản giả có khóa luồng, CAS và commit cả lô; khai_bao là danh sách bảng.

    phap_nhan_id tùy chọn dùng cho ngăn gắn một việc. Bản không gắn pháp
    nhân là ngăn quản trị của engine; caller phải truyền pháp nhân trong khóa.
    """

    def __init__(self, khai_bao=(), *, phap_nhan_id=None):
        self._khai_bao = {b["bang"]: deepcopy(b) for b in khai_bao}
        self._bang, self._phien = {}, 0
        self._khoa = RLock()
        self.phap_nhan_id = phap_nhan_id

    def _pham_vi(self, bang, khoa, phap_nhan_id):
        khoa = deepcopy(khoa)
        pn = self.phap_nhan_id if self.phap_nhan_id is not None else phap_nhan_id
        if self._khai_bao.get(bang, {}).get("pham_vi") == "phap_nhan" and pn is not None:
            if "phap_nhan_id" in khoa and str(khoa["phap_nhan_id"]) != str(pn):
                raise ValueError("Không được truy cập dữ liệu của pháp nhân khác.")
            khoa["phap_nhan_id"] = str(pn)
        return khoa

    @staticmethod
    def _khop(ban_ghi, khoa):
        return all(ban_ghi.gia_tri.get(k) == v for k, v in khoa.items())

    def doc(self, bang, khoa, *, phap_nhan_id=None):
        khoa = self._pham_vi(bang, khoa, phap_nhan_id)
        with self._khoa:
            ds = [b for b in self._bang.get(bang, []) if self._khop(b, khoa)]
            if len(ds) > 1:
                raise ValueError("Khóa ngăn chưa xác định duy nhất một bản ghi.")
            return deepcopy(ds[0]) if ds else None

    def tim(self, bang, loc=None, gioi_han=100, tiep=None, *, phap_nhan_id=None):
        if type(gioi_han) is not int or not 1 <= gioi_han <= 500:
            raise ValueError("Số bản ghi mỗi trang phải từ 1 đến 500.")
        loc = self._pham_vi(bang, loc or {}, phap_nhan_id)
        dau = 0 if tiep is None else int(tiep)
        with self._khoa:
            ds = [deepcopy(b) for b in self._bang.get(bang, []) if self._khop(b, loc)]
        cuoi = dau + gioi_han
        return {"danh_sach": ds[dau:cuoi], "tiep": str(cuoi) if cuoi < len(ds) else None}

    def lo(self, *, phap_nhan_id=None):
        return _Lo(self, phap_nhan_id)

    def _duy_nhat(self, bang):
        b = self._khai_bao.get(bang, {})
        khoa = list(b.get("khoa", []))
        if b.get("pham_vi") == "phap_nhan" and "phap_nhan_id" not in khoa:
            khoa.insert(0, "phap_nhan_id")
        return ([khoa] if khoa else []) + b.get("duy_nhat", [])

    def _ghi_lo(self, lenh, phap_nhan_id):
        with self._khoa:
            moi, phien, ket_qua = deepcopy(self._bang), self._phien, []
            for tac, bang, khoa, gia_tri, version in lenh:
                khoa = self._pham_vi(bang, khoa, phap_nhan_id)
                ds = moi.setdefault(bang, [])
                trung = [b for b in ds if self._khop(b, khoa)]
                if len(trung) > 1:
                    raise NganXungDot()
                cu = trung[0] if trung else None
                if tac == "lay_hoac_tao" and cu is not None:
                    ket_qua.append(BanGhi(deepcopy(cu.gia_tri), cu.row_version, False))
                    continue
                if tac == "them" and cu is not None:
                    raise NganXungDot()
                if tac in {"sua", "xoa"} and (cu is None or cu.row_version != version):
                    raise NganXungDot()
                if tac == "xoa":
                    ds.remove(cu)
                    ket_qua.append(BanGhi({}, cu.row_version))
                    continue
                gia_tri = {**deepcopy(gia_tri), **khoa}
                if len(json.dumps(gia_tri, ensure_ascii=False, allow_nan=False).encode("utf-8")) > 65536:
                    raise ValueError("Bản ghi vượt giới hạn 64 KiB.")
                for cac_khoa in self._duy_nhat(bang):
                    if any(k not in gia_tri for k in cac_khoa):
                        raise ValueError("Thiếu trường khóa của bản ghi ngăn.")
                    if any(b is not cu and all(b.gia_tri.get(k) == gia_tri[k] for k in cac_khoa) for b in ds):
                        raise NganXungDot()
                phien += 1
                ban_ghi = BanGhi(gia_tri, phien)
                if cu is not None:
                    ds.remove(cu)
                ds.append(ban_ghi)
                ket_qua.append(BanGhi(deepcopy(gia_tri), phien, cu is None))
            self._bang, self._phien = moi, phien
            return ket_qua


_KHOA_CHON = RLock()
_DA_CANH_BAO = False


def chon_ngan(app):
    global _DA_CANH_BAO
    if getattr(app, "ngan", None) is not None:
        return app.ngan
    with _KHOA_CHON:
        if getattr(app, "_ngan_bo_nho", None) is None:
            khai = []
            goc = getattr(app, "thu_muc_goi", None)
            tep = Path(goc) / "KHAI-SDK-2.1.json" if goc is not None else None
            if tep is not None and tep.is_file():
                khai = json.loads(tep.read_text(encoding="utf-8"))["ngan_du_lieu"]
            app._ngan_bo_nho = NganBoNho(khai)
        if not _DA_CANH_BAO:
            print("Đang lưu tạm trong bộ nhớ; khởi động lại sẽ mất hạn mức/dấu chống trùng", file=sys.stderr)
            _DA_CANH_BAO = True
        return app._ngan_bo_nho
