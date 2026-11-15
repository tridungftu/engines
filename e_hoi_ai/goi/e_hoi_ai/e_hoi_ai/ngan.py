"""Cổng ngăn tạm AI-8; chờ thay nguyên tệp bằng bản NGAN-0 chính thức."""
from copy import deepcopy
from dataclasses import dataclass
import json
import sys
from threading import RLock


class NganXungDot(Exception):
    ma = "NGAN_XUNG_DOT"
    thu_lai_duoc = True

    def __init__(self):
        super().__init__("Dữ liệu đã thay đổi. Hãy tải lại và thử lại.")


@dataclass(frozen=True)
class BanGhi:
    gia_tri: dict
    row_version: int


class Ngan:
    def doc(self, bang, khoa):
        raise NotImplementedError

    def tim(self, bang, loc=None, gioi_han=100, tiep=None):
        raise NotImplementedError

    def lo(self):
        raise NotImplementedError


class NganBoNho(Ngan):
    def __init__(self, khai_bao=(), *, phap_nhan_id=None):
        self.khai_bao = {b["bang"]: deepcopy(b) for b in khai_bao}
        self.phap_nhan_id = phap_nhan_id
        self._ban_ghi = {}
        self._khoa = RLock()
        self._phien = [0]

    def voi_phap_nhan(self, phap_nhan_id):
        ngan = NganBoNho(self.khai_bao.values(), phap_nhan_id=phap_nhan_id)
        ngan._ban_ghi, ngan._khoa, ngan._phien = self._ban_ghi, self._khoa, self._phien
        return ngan

    def _pham_vi(self, bang, gia_tri):
        gia_tri = deepcopy(gia_tri)
        if self.khai_bao.get(bang, {}).get("pham_vi") == "phap_nhan":
            if not self.phap_nhan_id:
                raise ValueError("Chưa xác định pháp nhân của việc.")
            if gia_tri.get("phap_nhan_id", self.phap_nhan_id) != self.phap_nhan_id:
                raise ValueError("Không được truy cập dữ liệu của pháp nhân khác.")
            gia_tri["phap_nhan_id"] = self.phap_nhan_id
        return gia_tri

    @staticmethod
    def _khop(hang, loc):
        return all(k in hang.gia_tri and hang.gia_tri[k] == v for k, v in loc.items())

    def doc(self, bang, khoa):
        loc = self._pham_vi(bang, khoa)
        with self._khoa:
            ds = [h for h in self._ban_ghi.get(bang, []) if self._khop(h, loc)]
            if len(ds) > 1:
                raise ValueError("Khóa đọc phải xác định một bản ghi.")
            return deepcopy(ds[0]) if ds else None

    def tim(self, bang, loc=None, gioi_han=100, tiep=None):
        if type(gioi_han) is not int or not 1 <= gioi_han <= 500:
            raise ValueError("Mỗi lần tìm phải từ 1 đến 500 bản ghi.")
        loc = self._pham_vi(bang, loc or {})
        bat_dau = int(tiep or 0)
        if bat_dau < 0:
            raise ValueError("Mốc tìm không hợp lệ.")
        with self._khoa:
            ds = [h for h in self._ban_ghi.get(bang, []) if self._khop(h, loc)]
            cuoi = bat_dau + gioi_han
            return {"danh_sach": deepcopy(ds[bat_dau:cuoi]),
                    "tiep": str(cuoi) if cuoi < len(ds) else None}

    def lo(self):
        return _Lo(self)


class _Lo:
    def __init__(self, ngan):
        self.ngan, self.lenh, self.ket_qua = ngan, [], []

    def __enter__(self):
        return self

    def them(self, bang, khoa, gia_tri):
        self._them("them", bang, khoa, gia_tri)

    def sua(self, bang, khoa, gia_tri, *, row_version):
        self._them("sua", bang, khoa, gia_tri, row_version)

    def xoa(self, bang, khoa, *, row_version):
        self._them("xoa", bang, khoa, {}, row_version)

    def lay_hoac_tao(self, bang, khoa, gia_tri):
        self._them("lay_hoac_tao", bang, khoa, gia_tri)

    def _them(self, thao_tac, bang, khoa, gia_tri, row_version=None):
        if len(self.lenh) >= 100:
            raise ValueError("Một lô chỉ được có tối đa 100 lệnh.")
        self.lenh.append((thao_tac, bang, deepcopy(khoa), deepcopy(gia_tri), row_version))

    def __exit__(self, loai, loi, vet):
        if loai is not None:
            return False
        n = self.ngan
        with n._khoa:
            moi = deepcopy(n._ban_ghi)
            phien, ket_qua = n._phien[0], []
            for tt, bang, khoa, gia_tri, rv in self.lenh:
                khoa = n._pham_vi(bang, khoa)
                hang = moi.setdefault(bang, [])
                ds = [h for h in hang if n._khop(h, khoa)]
                if len(ds) > 1:
                    raise NganXungDot()
                cu = ds[0] if ds else None
                if tt == "lay_hoac_tao" and cu is None:
                    ung_vien = n._pham_vi(bang, {**gia_tri, **khoa})
                    khai = n.khai_bao.get(bang, {})
                    for r in khai.get("duy_nhat", []):
                        r = list(r)
                        if khai.get("pham_vi") == "phap_nhan":
                            r.append("phap_nhan_id")
                        trung = [h for h in hang if all(k in ung_vien and h.gia_tri.get(k) == ung_vien[k] for k in r)]
                        if trung:
                            if cu is not None and cu != trung[0]:
                                raise NganXungDot()
                            cu = trung[0]
                if tt == "lay_hoac_tao" and cu:
                    ket_qua.append({"row_version": cu.row_version, "da_tao": False})
                    continue
                if tt == "them" and cu or tt in {"sua", "xoa"} and (
                        cu is None or type(rv) is not int or cu.row_version != rv):
                    raise NganXungDot()
                if cu:
                    hang.remove(cu)
                phien += 1
                if tt != "xoa":
                    if any(k in gia_tri and gia_tri[k] != v for k, v in khoa.items()):
                        raise ValueError("Không được đổi khóa của bản ghi.")
                    gt = n._pham_vi(bang, {**gia_tri, **khoa})
                    if len(json.dumps(gt, ensure_ascii=False, allow_nan=False).encode("utf-8")) > 65536:
                        raise ValueError("Bản ghi vượt giới hạn 64 KiB.")
                    khai = n.khai_bao.get(bang, {})
                    rang_buoc = list(khai.get("duy_nhat", []))
                    if khai.get("khoa"):
                        rang_buoc.append(khai["khoa"])
                    if khai.get("pham_vi") == "phap_nhan":
                        rang_buoc = [list(set(r) | {"phap_nhan_id"}) for r in rang_buoc]
                    for r in rang_buoc:
                        if any(all(k in gt and h.gia_tri.get(k) == gt[k] for k in r) for h in hang):
                            raise NganXungDot()
                    hang.append(BanGhi(gt, phien))
                ket_qua.append({"row_version": phien, "da_tao": cu is None})
            n._ban_ghi.clear()
            n._ban_ghi.update(moi)
            n._phien[0], self.ket_qua = phien, ket_qua
        return False


_khoa_chon = RLock()


def chon_ngan(app):
    with _khoa_chon:
        if getattr(app, "ngan", None) is None:
            app.ngan = NganBoNho()
            print("Đang lưu tạm trong bộ nhớ; khởi động lại sẽ mất hạn mức/dấu chống trùng",
                  file=sys.stderr)
        return app.ngan
