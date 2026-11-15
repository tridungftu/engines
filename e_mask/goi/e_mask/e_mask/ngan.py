"""Bản bọc tạm NGAN-0; chỉ thư viện chuẩn, không ghi đĩa.

API theo đề nghị SDK 2.1. Lead thay nguyên tệp bằng mẫu chung khi gộp.
"""
from contextlib import AbstractContextManager
from copy import deepcopy
from dataclasses import dataclass
import json
from threading import RLock
import sys
from typing import Protocol


class NganXungDot(Exception):
    ma = 'NGAN_XUNG_DOT'
    thu_lai_duoc = True

    def __init__(self):
        super().__init__('Dữ liệu vừa thay đổi. Hãy thử lại.')


@dataclass(frozen=True, repr=False)
class BanGhi:
    gia_tri: dict
    row_version: int


class Ngan(Protocol):
    def doc(self, bang, khoa): ...
    def tim(self, bang, loc=None, gioi_han=100, tiep=None): ...
    def lo(self): ...


def _json(gia_tri):
    return json.dumps(gia_tri, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False)


class NganBoNho:
    def __init__(self, bang=None, *, phap_nhan_id=None, _goc=None):
        self._bang = {b['ma']: deepcopy(b) for b in (bang or [])}
        self._phap_nhan = phap_nhan_id
        self._goc = _goc or self
        if _goc is None:
            self._du_lieu, self._khoa, self._phien = {}, RLock(), 0

    def theo_phap_nhan(self, phap_nhan_id):
        return NganBoNho(list(self._bang.values()), phap_nhan_id=phap_nhan_id, _goc=self._goc)

    def _pham_vi(self, bang, du_lieu):
        du_lieu = deepcopy(du_lieu)
        if self._bang.get(bang, {}).get('pham_vi') == 'phap_nhan':
            if not self._phap_nhan or du_lieu.get('phap_nhan_id', self._phap_nhan) != self._phap_nhan:
                raise ValueError('Phạm vi pháp nhân chưa hợp lệ.')
            du_lieu['phap_nhan_id'] = self._phap_nhan
        return du_lieu

    def _khoa_muc(self, bang, du_lieu):
        cot = list(self._bang.get(bang, {}).get('khoa', du_lieu.keys()))
        if self._bang.get(bang, {}).get('pham_vi') == 'phap_nhan' and 'phap_nhan_id' not in cot:
            cot.append('phap_nhan_id')
        return _json({k: du_lieu[k] for k in cot})

    def doc(self, bang, khoa):
        khoa = self._pham_vi(bang, khoa)
        with self._goc._khoa:
            muc = self._goc._du_lieu.get(bang, {}).get(self._khoa_muc(bang, khoa))
            return deepcopy(muc)

    def tim(self, bang, loc=None, gioi_han=100, tiep=None):
        if type(gioi_han) is not int or not 1 <= gioi_han <= 500:
            raise ValueError('Giới hạn tìm chưa hợp lệ.')
        loc = self._pham_vi(bang, loc or {})
        dau = int(tiep or 0)
        if dau < 0:
            raise ValueError('Mốc tìm chưa hợp lệ.')
        with self._goc._khoa:
            ds = [deepcopy(m) for _, m in sorted(self._goc._du_lieu.get(bang, {}).items())
                  if all(m.gia_tri.get(k) == v for k, v in loc.items())]
        cuoi = dau + gioi_han
        return {'danh_sach': ds[dau:cuoi], 'tiep': str(cuoi) if cuoi < len(ds) else None}

    def lo(self):
        return _Lo(self)


class _Lo(AbstractContextManager):
    def __init__(self, ngan):
        self.ngan, self.lenh, self.ket_qua = ngan, [], []

    def _them_lenh(self, thao_tac, bang, khoa, gia_tri=None, row_version=None):
        if len(self.lenh) >= 100:
            raise ValueError('Một lô có tối đa 100 lệnh.')
        self.lenh.append((thao_tac, bang, deepcopy(khoa), deepcopy(gia_tri), row_version))

    def them(self, bang, khoa, gia_tri):
        self._them_lenh('them', bang, khoa, gia_tri)

    def sua(self, bang, khoa, gia_tri, *, row_version):
        self._them_lenh('sua', bang, khoa, gia_tri, row_version)

    def xoa(self, bang, khoa, *, row_version):
        self._them_lenh('xoa', bang, khoa, row_version=row_version)

    def lay_hoac_tao(self, bang, khoa, gia_tri):
        self._them_lenh('lay_hoac_tao', bang, khoa, gia_tri)

    def __exit__(self, loai, loi, vet):
        if loai is not None:
            return False
        ngan, goc = self.ngan, self.ngan._goc
        with goc._khoa:
            moi, phien, ket_qua = deepcopy(goc._du_lieu), goc._phien, []
            for tt, bang, khoa, gia_tri, rv in self.lenh:
                khoa = ngan._pham_vi(bang, khoa)
                gia_tri = dict(ngan._pham_vi(bang, gia_tri or {}), **khoa)
                ds = moi.setdefault(bang, {})
                # lay_hoac_tao có thể dùng khóa duy nhất khác khóa chính.
                khoa_cu, cu = next(((k, m) for k, m in ds.items() if all(m.gia_tri.get(t) == v for t, v in khoa.items())), (None, None))
                if tt == 'lay_hoac_tao' and cu is not None:
                    ket_qua.append({'ban_ghi': deepcopy(cu), 'row_version': cu.row_version, 'da_tao': False})
                    continue
                if tt == 'them' and cu is not None or tt in {'sua', 'xoa'} and (cu is None or cu.row_version != rv):
                    raise NganXungDot()
                if tt in {'sua', 'xoa'}:
                    del ds[khoa_cu]
                if tt == 'xoa':
                    ket_qua.append({'row_version': None, 'da_tao': False})
                    continue
                khoa_moi = ngan._khoa_muc(bang, gia_tri if bang in ngan._bang else khoa)
                if khoa_moi in ds:
                    raise NganXungDot()
                for cot in ngan._bang.get(bang, {}).get('duy_nhat', []):
                    cot = list(cot)
                    if ngan._bang.get(bang, {}).get('pham_vi') == 'phap_nhan':
                        cot.append('phap_nhan_id')
                    if any(all(m.gia_tri.get(k) == gia_tri.get(k) for k in cot) for m in ds.values()):
                        raise NganXungDot()
                _json(gia_tri)
                for v in gia_tri.values():
                    if isinstance(v, (dict, list)) and len(_json(v).encode('utf-8')) > 65536:
                        raise ValueError('Giá trị vượt giới hạn ngăn.')
                phien += 1
                muc = BanGhi(gia_tri, phien)
                ds[khoa_moi] = muc
                ket_qua.append({'ban_ghi': deepcopy(muc), 'row_version': phien, 'da_tao': cu is None})
            goc._du_lieu, goc._phien = moi, phien
            self.ket_qua = ket_qua
        return False


_khoa_chon = RLock()
_da_canh_bao = False


def chon_ngan(app):
    global _da_canh_bao
    with _khoa_chon:
        if getattr(app, 'ngan', None) is not None:
            return app.ngan
        if not hasattr(app, '_ngan_tam'):
            app._ngan_tam = NganBoNho()
        if not _da_canh_bao:
            print('Đang lưu tạm trong bộ nhớ; khởi động lại sẽ mất hạn mức/dấu chống trùng', file=sys.stderr)
            _da_canh_bao = True
        return app._ngan_tam
