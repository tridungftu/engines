"""MASK-R7: đã kiểm bằng Core giả (CoreGia), chỉ DEMO, không UI Core thật."""
from contextlib import contextmanager
from copy import deepcopy
import json
from types import SimpleNamespace
from uuid import uuid4
import traceback

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, ViecDaHuy

from e_mask.duyet_dinh_danh import DuyetDinhDanh, kiem_ma_junsky
from e_mask.kho_ngan import KhoNganBiMat
from test_mask_r2 import bo, _dong, _them, TEN, TEN_KHAC, ALIAS, _khong_lo
from test_mask_r4 import ghep, cho_ai, mo


class QuyenAdminGia:
    """Adapter cửa Core đề nghị, ngoài gói; không giả SDK đã có cửa này."""
    def __init__(self):
        self.admin = self.xem = self.duyet = True
        self.vung, self.phien = 'DEMO', 'phien-DEMO'
        self.ve, self.goi = {}, []
        self.truoc_ghi = lambda: None
        self.sai_ve = None

    def xac_minh_admin(self):
        if not self.admin:
            raise RuntimeError(TEN)
        return self.vung

    def xem_tai_core(self, ma, phien):
        if not self.xem:
            raise RuntimeError(TEN)
        ve = uuid4().hex
        self.ve[ve] = (ma, phien, self.vung, self.phien)
        return ve

    @contextmanager
    def bien_nhan_duyet(self, viec, **kw):
        self.goi.append(deepcopy(kw))
        ve = self.ve.pop(kw['bien_nhan'], None)
        if (not self.admin or not self.xem or not self.duyet or
                ve != (kw['id_dinh_danh'], kw['row_version'], kw['vung'], self.phien)):
            raise LoiNghiepVu('MASK_BIEN_NHAN_KHONG_HOP_LE', TEN)
        self.truoc_ghi()
        yield (self.sai_ve if self.sai_ve is not None else
               dict(id_dinh_danh=kw['id_dinh_danh'], row_version=kw['row_version']))


def test_danh_sach_chi_metadata_sdk_null_co_va_khong_lo(bo, capsys):
    a, b = _dong(), _dong(TEN_KHAC, vung='THAT')
    def kiem(v):
        _them(v, a); _them(v, b)
        q = QuyenAdminGia()
        admin = DuyetDinhDanh(v, q)
        ds = admin.danh_sach()
        assert ds == {'danh_sach': [dict(id_dinh_danh=a['id_dinh_danh'],
            row_version=1, bi_danh=None, nhom='CONG_TY', trang_thai='CHO_DUYET', so_gap=1)], 'tiep': None}
        _khong_lo(ds)
        _khong_lo(repr(admin))
        raw = v.ngan.doc('dinh_danh', {'id_dinh_danh': a['id_dinh_danh']})
        assert raw.gia_tri['gia_tri_goc'] is raw.gia_tri['gia_tri_chuan'] is None
        assert raw.gia_tri['gia_tri_goc_da_ma_hoa'] is True
        q.admin = False
        with pytest.raises(LoiNghiepVu): admin.danh_sach()
    bo.chay(kiem)
    _khong_lo(bo.core.nhat_ky); _khong_lo(capsys.readouterr())


@pytest.mark.parametrize('tu_choi', [False, True])
def test_quyet_dinh_cung_id_khong_sao_bi_mat_null_co_no_xoa(bo, monkeypatch, tu_choi):
    dong = _dong()
    def kiem(v):
        _them(v, dong)
        q = QuyenAdminGia(); admin = DuyetDinhDanh(v, q)
        ghi, lenh = v.ngan._dt.ngan_ghi_lo, []
        def spy(ds, **kw):
            lenh.extend(deepcopy(ds)); return ghi(ds, **kw)
        monkeypatch.setattr(v.ngan._dt, 'ngan_ghi_lo', spy)
        ve = q.xem_tai_core(dong['id_dinh_danh'], 1)
        ham = admin.tu_choi if tu_choi else admin.duyet
        kq = ham(dong['id_dinh_danh'], 1, bien_nhan=ve)
        assert len(lenh) == (1 if tu_choi else 2)
        assert lenh[0]['thao_tac'] == 'sua' and lenh[0]['bang'] == 'dinh_danh'
        assert lenh[0]['khoa'] == {'id_dinh_danh': dong['id_dinh_danh']}
        assert lenh[0]['gia_tri'] == {'trang_thai': 'TU_CHOI' if tu_choi else 'CHINH_THUC'}
        assert all(l['thao_tac'] != 'xoa' for l in lenh)
        assert all(not any(k.startswith('gia_tri_') for k in l['gia_tri']) for l in lenh)
        assert KhoNganBiMat(v, vung='DEMO').tim_ung_vien(TEN, 'CONG_TY')['row_version'] == 2
        if not tu_choi: assert kq['bi_danh'].startswith('[[MASKCT-')
        _khong_lo(kq); _khong_lo(lenh); _khong_lo(q.goi)
        with pytest.raises(LoiNghiepVu): ham(dong['id_dinh_danh'], 1, bien_nhan=ve)
    bo.chay(kiem)
    assert len(bo.core.xem_ngan('e_mask', 'dinh_danh')) == 1
    for bang in ('cho_duyet', 'dau_gap', 'bi_danh_tam', 'ma_yeu_cau'):
        assert bo.core.xem_ngan('e_mask', bang) == []


@pytest.mark.parametrize('thieu', ['admin', 'xem', 'duyet', 'phien', 'vung', 'cua', 've', 'co_tu_khai', 'id_khac', 'phien_khac'])
@pytest.mark.parametrize('tu_choi', [False, True])
def test_thieu_quyen_cua_ve_khong_duyet_mu(bo, thieu, tu_choi):
    dong = _dong()
    def kiem(v):
        _them(v, dong)
        q = QuyenAdminGia(); ve = q.xem_tai_core(dong['id_dinh_danh'], 1)
        if thieu in {'admin', 'xem', 'duyet'}: setattr(q, thieu, False)
        elif thieu == 'phien': q.phien = 'phien-khac-DEMO'
        elif thieu == 'vung': q.vung = 'THAT'
        elif thieu == 'cua': q.bien_nhan_duyet = None
        elif thieu == 've': ve = uuid4().hex
        elif thieu == 'co_tu_khai': ve = {'da_xem': True}
        elif thieu == 'id_khac': ve = q.xem_tai_core(uuid4().hex, 1)
        elif thieu == 'phien_khac': ve = q.xem_tai_core(dong['id_dinh_danh'], 2)
        admin = DuyetDinhDanh(v, q)
        with pytest.raises(LoiNghiepVu) as e:
            (admin.tu_choi if tu_choi else admin.duyet)(dong['id_dinh_danh'], 1, bien_nhan=ve)
        _khong_lo(''.join(traceback.format_exception(e.value)))
        assert KhoNganBiMat(v, vung='DEMO').doc(dong['id_dinh_danh'])['trang_thai'] == 'CHO_DUYET'
    bo.chay(kiem)


@pytest.mark.parametrize('sai', [dict(row_version=True), dict(ten=TEN), dict(da_xem=True)])
def test_bien_nhan_tra_ve_sai_khuon_khong_ten(bo, sai):
    dong = _dong()
    def kiem(v):
        _them(v, dong); q = QuyenAdminGia()
        q.sai_ve = dict(id_dinh_danh=dong['id_dinh_danh'], row_version=1) | sai
        with pytest.raises(LoiNghiepVu):
            DuyetDinhDanh(v, q).duyet(dong['id_dinh_danh'], 1,
                bien_nhan=q.xem_tai_core(dong['id_dinh_danh'], 1))
        assert KhoNganBiMat(v, vung='DEMO').doc(dong['id_dinh_danh'])['row_version'] == 1
    bo.chay(kiem)


def test_cas_giua_xem_va_duyet_rollback_alias_va_khong_tu_thu_lai(bo):
    dong = _dong()
    def kiem(v):
        _them(v, dong); q = QuyenAdminGia(); admin = DuyetDinhDanh(v, q)
        ve = q.xem_tai_core(dong['id_dinh_danh'], 1)
        q.truoc_ghi = lambda: bo.core.gay_xung_dot_ngan('dinh_danh')
        with pytest.raises(LoiNghiepVu) as e:
            admin.duyet(dong['id_dinh_danh'], 1, bien_nhan=ve)
        assert e.value.ma == 'MASK_XUNG_DOT'
        assert not bo.core.xem_ngan('e_mask', 'bi_danh')
        assert KhoNganBiMat(v, vung='DEMO').doc(dong['id_dinh_danh'])['row_version'] == 1
        with pytest.raises(LoiNghiepVu): admin.duyet(dong['id_dinh_danh'], 1, bien_nhan=ve)
    bo.chay(kiem)


def test_hai_admin_mot_phien_chi_mot_nguoi_duyet_va_alias_duy_nhat(bo):
    a, b = _dong(), _dong(TEN_KHAC)
    def kiem(v):
        _them(v, a); _them(v, b)
        q1, q2 = QuyenAdminGia(), QuyenAdminGia()
        ve1 = q1.xem_tai_core(a['id_dinh_danh'], 1); ve2 = q2.xem_tai_core(a['id_dinh_danh'], 1)
        DuyetDinhDanh(v, q1).duyet(a['id_dinh_danh'], 1, bien_nhan=ve1, ma_junsky='KH-DEMO-001')
        with pytest.raises(LoiNghiepVu):
            DuyetDinhDanh(v, q2).duyet(a['id_dinh_danh'], 1, bien_nhan=ve2)
        with pytest.raises(LoiNghiepVu) as e:
            DuyetDinhDanh(v, q1).duyet(b['id_dinh_danh'], 1,
                bien_nhan=q1.xem_tai_core(b['id_dinh_danh'], 1), ma_junsky='kh-demo-001')
        assert e.value.ma == 'MASK_XUNG_DOT'
        assert KhoNganBiMat(v, vung='DEMO').doc(b['id_dinh_danh'])['row_version'] == 1
    bo.chay(kiem)


@pytest.mark.parametrize('ma', ['MASKCT-1', 'maskcn', 'MASKDC-1', 'MASKMST', 'MASKTK', 'MASKKHAC', 'MASKTAM', '<img src=x>', TEN, '', 'a b'])
def test_junsky_khong_xss_tien_to_mask_ten(ma):
    with pytest.raises(LoiNghiepVu): kiem_ma_junsky(ma)


def test_quyet_dinh_admin_khong_doi_map_ram_dang_chay(bo):
    q, dh, ram, v_ram, ma = ghep()
    du = cho_ai(ram, v_ram); truoc = deepcopy(du)
    dong = _dong()
    def kiem(v):
        _them(v, dong); admin = QuyenAdminGia()
        DuyetDinhDanh(v, admin).duyet(dong['id_dinh_danh'], 1,
            bien_nhan=admin.xem_tai_core(dong['id_dinh_danh'], 1), ma_junsky='KH-DEMO-MOI')
        assert du == truoc
    bo.chay(kiem)
    assert mo(ram, q, ma) == TEN and du == {}


def test_mat_ack_sau_core_nhan_chua_ro_khong_gui_lai_bang_ve_moi(bo, monkeypatch, capsys):
    dong = _dong()
    def kiem(v):
        _them(v, dong); q = QuyenAdminGia(); admin = DuyetDinhDanh(v, q)
        ghi = v.ngan._dt.ngan_ghi_lo
        def mat(lenh, **kw):
            ghi(lenh, **kw); raise RuntimeError(TEN)
        monkeypatch.setattr(v.ngan._dt, 'ngan_ghi_lo', mat)
        with pytest.raises(ChuaRo) as e:
            admin.duyet(dong['id_dinh_danh'], 1, bien_nhan=q.xem_tai_core(dong['id_dinh_danh'], 1))
        _khong_lo(''.join(traceback.format_exception(e.value)))
        with pytest.raises(ChuaRo):
            admin.duyet(dong['id_dinh_danh'], 1, bien_nhan=q.xem_tai_core(dong['id_dinh_danh'], 1))
    bo.chay(kiem)
    assert len(bo.core.xem_ngan('e_mask', 'bi_danh')) == 1
    _khong_lo(capsys.readouterr())

@pytest.mark.parametrize('doi', ['admin', 'vung'])
def test_thu_hoi_quyen_sau_vao_cua_truoc_ghi(bo, doi):
    dong = _dong()
    def kiem(v):
        _them(v, dong); q = QuyenAdminGia()
        q.truoc_ghi = lambda: setattr(q, doi, False if doi == 'admin' else 'THAT')
        with pytest.raises(LoiNghiepVu):
            DuyetDinhDanh(v, q).duyet(dong['id_dinh_danh'], 1,
                bien_nhan=q.xem_tai_core(dong['id_dinh_danh'], 1))
        assert KhoNganBiMat(v, vung='DEMO').doc(dong['id_dinh_danh'])['row_version'] == 1
    bo.chay(kiem)


def test_phien_doi_sau_xem_buoc_xem_lai_khong_goi_cua_bang_ve_cu(bo):
    dong = _dong()
    def kiem(v):
        _them(v, dong); q = QuyenAdminGia(); ve = q.xem_tai_core(dong['id_dinh_danh'], 1)
        KhoNganBiMat(v, vung='DEMO').sua_metadata([dict(id_dinh_danh=dong['id_dinh_danh'],
            row_version=1, gia_tri={'nhom': 'KHAC'})])
        with pytest.raises(LoiNghiepVu) as e:
            DuyetDinhDanh(v, q).duyet(dong['id_dinh_danh'], 1, bien_nhan=ve)
        assert e.value.ma == 'MASK_XUNG_DOT' and q.goi == []
        assert not bo.core.xem_ngan('e_mask', 'bi_danh')
    bo.chay(kiem)


def test_alias_mask_tu_sinh_trung_cung_rollback(bo, monkeypatch):
    a, b = _dong(trang_thai='CHINH_THUC'), _dong(TEN_KHAC)
    def kiem(v):
        _them(v, a, ALIAS); _them(v, b); q = QuyenAdminGia()
        monkeypatch.setattr('e_mask.duyet_dinh_danh.bi_danh_moi', lambda nhom: ALIAS.lower())
        with pytest.raises(LoiNghiepVu) as e:
            DuyetDinhDanh(v, q).duyet(b['id_dinh_danh'], 1,
                bien_nhan=q.xem_tai_core(b['id_dinh_danh'], 1))
        assert e.value.ma == 'MASK_XUNG_DOT'
        assert KhoNganBiMat(v, vung='DEMO').doc(b['id_dinh_danh'])['trang_thai'] == 'CHO_DUYET'
    bo.chay(kiem)


def test_hai_admin_dong_thoi_chi_mot_lo_dat(bo):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    dong = _dong()
    def kiem(v):
        _them(v, dong); cho = Barrier(2)
        def duyet(i):
            q = QuyenAdminGia(); q.truoc_ghi = lambda: cho.wait(timeout=10)
            try:
                DuyetDinhDanh(v, q).duyet(dong['id_dinh_danh'], 1,
                    bien_nhan=q.xem_tai_core(dong['id_dinh_danh'], 1), ma_junsky=f'KH-DEMO-{i}')
                return 'DAT'
            except LoiNghiepVu as e:
                return e.ma
        with ThreadPoolExecutor(max_workers=2) as pool:
            assert sorted(pool.map(duyet, [1, 2])) == ['DAT', 'MASK_XUNG_DOT']
        assert len(bo.core.xem_ngan('e_mask', 'bi_danh')) == 1
    bo.chay(kiem)


def test_loi_ket_thuc_cua_sau_ghi_la_chua_ro_khong_thanh_cong_gia(bo):
    dong = _dong()
    def kiem(v):
        _them(v, dong); q = QuyenAdminGia(); goc = q.bien_nhan_duyet
        @contextmanager
        def cua(*args, **kw):
            with goc(*args, **kw) as ve: yield ve
            raise RuntimeError(TEN)
        q.bien_nhan_duyet = cua
        with pytest.raises(ChuaRo) as e:
            DuyetDinhDanh(v, q).duyet(dong['id_dinh_danh'], 1,
                bien_nhan=q.xem_tai_core(dong['id_dinh_danh'], 1))
        _khong_lo(''.join(traceback.format_exception(e.value)))
        assert KhoNganBiMat(v, vung='DEMO').doc(dong['id_dinh_danh'])['trang_thai'] == 'CHINH_THUC'
    bo.chay(kiem)


def test_cua_nuot_loi_cas_khong_bao_thanh_cong(bo):
    dong = _dong()
    def kiem(v):
        _them(v, dong); q = QuyenAdminGia(); goc = q.bien_nhan_duyet
        @contextmanager
        def cua(*args, **kw):
            try:
                with goc(*args, **kw) as ve: yield ve
            except LoiNghiepVu: pass
        q.bien_nhan_duyet = cua
        q.truoc_ghi = lambda: bo.core.gay_xung_dot_ngan('dinh_danh')
        with pytest.raises(LoiNghiepVu):
            DuyetDinhDanh(v, q).duyet(dong['id_dinh_danh'], 1,
                bien_nhan=q.xem_tai_core(dong['id_dinh_danh'], 1))
        assert KhoNganBiMat(v, vung='DEMO').doc(dong['id_dinh_danh'])['row_version'] == 1
    bo.chay(kiem)


def test_khong_con_admin_ram_nhap_don_dong_o_runtime():
    assert not any(hasattr(DuyetDinhDanh, ten) for ten in ('nhap_demo', 'don', 'dong'))
    from e_mask.ngan import NganBoNho
    from e_mask.kho_ngan import KHAI_NGAN
    from ho_tro_ngan import ADMIN
    with pytest.raises(LoiNghiepVu): DuyetDinhDanh(NganBoNho(KHAI_NGAN), ADMIN).danh_sach()
