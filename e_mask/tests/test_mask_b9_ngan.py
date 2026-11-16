"""Đầu dò lô B9 trên NganEngine/CoreGia thật của SDK, không kho RAM giả."""
from contextlib import contextmanager
from types import SimpleNamespace

import pytest
from kho_tri_thuc_sdk.engine import NganEngine
from kho_tri_thuc_sdk.thu import CoreGia
from e_mask.chay import tao_app
from e_mask.ho_so_ai import json_chuan
from e_mask.ho_so_tep import bao_ve
from e_mask.kho_anh_xa_ram import KhoAnhXaRAM
from e_mask.kho_qua_core import CongHauKiemTepSDK, KhoNhanDienQuaCore
from ho_tro_mask_b7 import CongTepCoreGia
from ho_tro_ngan import QuyenNganDemo
from ho_tro_ram import DongHoGia
from test_mask_r2 import _dong, _them


def dau_do(n, *, sai=None, monkeypatch=None):
    q, dh, cong = QuyenNganDemo(), DongHoGia(), CongTepCoreGia()
    app = tao_app(quyen=q)
    app.kho_anh_xa_ram = ram = KhoAnhXaRAM(quyen=q, dong_ho=dh, hen_gio=dh.hen_gio)
    c = CoreGia(app)
    cong.q, cong.dh, cong.core, cong.ram = q, dh, c, ram
    lo_da_ghi, bat = [], [False]
    lo_goc = NganEngine.lo
    @contextmanager
    def lo_spy(ngan):
        ds = []
        with lo_goc(ngan) as lo:
            class Lo:
                def __getattr__(self, ten):
                    return getattr(lo, ten)
                def sua(self, bang, khoa, gia_tri, **kw):
                    if bat[0]:
                        assert set(khoa) == {'id_dinh_danh'}
                        assert set(gia_tri) == {'so_gap'}
                        ds.append((bang, dict(khoa), dict(gia_tri), dict(kw)))
                    return lo.sua(bang, khoa, gia_tri, **kw)
            yield Lo()
        if bat[0]: lo_da_ghi.append(ds)
    monkeypatch.setattr(NganEngine, 'lo', lo_spy)

    @bao_ve
    def probe(v):
        ket = dict(loai='van_ban_da_che', van_ban_da_che=dict(phien_ban=1,
            van_ban='DEMO đầu dò chốt metadata', ma_yeu_cau=q.ve[(v.id, 'che')].ma_yeu_cau,
            con_sot=[], kiem_tien_ngay=True, chuyen_tiep={}))
        with CongHauKiemTepSDK(cong=cong, quyen=q, ram=ram) as sdk:
            with ram.buoc(v) as buoc:
                metas = []
                kho = KhoNhanDienQuaCore(viec=v, quyen=q)
                for i in range(n):
                    row = _dong('Công ty DEMO kho ' + str(i), trang_thai='CHINH_THUC')
                    _them(v, row, '[[MASKCT-DEMO-' + str(i) + ']]')
                    muc = kho.doc(row['id_dinh_danh'])
                    assert muc['gia_tri_goc'] is None and muc['gia_tri_goc_da_ma_hoa'] is True
                    metas.append({k: muc[k] for k in ('id_dinh_danh', 'id_bi_danh', 'bi_danh', 'nhom', 'row_version')})
                bat[0] = True
                if sai == 'cas':
                    cong.moc = lambda ten, _v: c.gay_xung_dot_ngan('dinh_danh') if ten == 'truoc_chot' else None
                elif sai == 'phien':
                    metas[-1]['row_version'] += 1
                elif sai == 'bo_ghi':
                    cong.chot_metadata = lambda *_a, **_kw: True
                elif sai == 'hai_lan':
                    def hai(v, ctx, *, chung_cu, metadata, ghi):
                        ghi()
                        ghi()
                        return True
                    cong.chot_metadata = hai
                chung = json_chuan(dict(phien_ban=1, nang_luc='DEMO-dau-do', kiem_tien_ngay=True))
                sdk.chot_metadata(v, buoc._ctx.quyen, chung_cu=chung, metadata=json_chuan(metas))
                sdk.ban_giao(v, buoc._ctx.quyen, chung_cu=chung, ket_qua=json_chuan(ket))
                buoc.du_lieu['giai_doan_ai'] = 'DA_HAU_KIEM'
                buoc.cho_ai()
        return ket
    app._ham['mask.che_van_ban@1'] = probe
    v = c.giao_viec('mask.che_van_ban@1', dict(loai='van_ban', van_ban='DEMO đầu dò'))
    q.cap(v)
    c.chay(app)
    return SimpleNamespace(k=c.xem(v), c=c, ram=ram, lo=lo_da_ghi, cong=cong)


@pytest.mark.parametrize('n', [0, 1, 100])
def test_chot_sdk_mot_lo_den_dung_100_khong_chia_gia_nguyen_tu(n, monkeypatch):
    b = dau_do(n, monkeypatch=monkeypatch)
    assert b.k['trang_thai'] == 'XONG', b.k
    assert [len(ds) for ds in b.lo] == ([n] if n else [])
    rows = b.c.xem_ngan('e_mask', 'dinh_danh')
    assert len(rows) == n and all(int(m['so_gap']) == 2 for m in rows)


@pytest.mark.parametrize('sai', ['cas', 'phien', 'bo_ghi'])
def test_cas_hoac_khong_ghi_khong_chot_mot_phan(sai, monkeypatch):
    b = dau_do(3, sai=sai, monkeypatch=monkeypatch)
    assert b.k['trang_thai'] == 'LOI' and b.k['ket_qua'] is None, b.k
    assert b.ram._ban_ghi is None and not b.lo
    assert all(int(m['so_gap']) == 1 for m in b.c.xem_ngan('e_mask', 'dinh_danh'))


def test_101_tu_choi_truoc_lo_khong_thanh_hai_lo(monkeypatch):
    b = dau_do(101, monkeypatch=monkeypatch)
    assert b.k['trang_thai'] == 'LOI' and b.k['ket_qua'] is None
    assert b.k['loi']['ma'] == 'MASK_QUA_GIOI_HAN'
    assert not b.lo and b.cong.dem_chot == 0
    assert all(int(m['so_gap']) == 1 for m in b.c.xem_ngan('e_mask', 'dinh_danh'))


def test_core_goi_ghi_hai_lan_khong_tang_dem_hai_lan(monkeypatch):
    b = dau_do(1, sai='hai_lan', monkeypatch=monkeypatch)
    assert b.k['trang_thai'] == 'CHUA_RO' and b.k['ket_qua'] is None
    assert b.ram._ban_ghi is None and len(b.lo) == 1
    assert int(b.c.xem_ngan('e_mask', 'dinh_danh')[0]['so_gap']) == 2
