"""MASK-R2: đã kiểm bằng Core giả (CoreGia), dữ liệu hoàn toàn DEMO.

Ngăn là NganEngine thật của SDK 2.2.0, không thay null+cờ bằng mock trả tên.
Wrapper transport chỉ quan sát hoặc gây mất ACK sau khi Core đã xử lý lô.
"""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from threading import Barrier
from types import SimpleNamespace
import unicodedata
from uuid import uuid4

import pytest
from kho_tri_thuc_sdk.engine import (ChuaRo, Engine, LoiDuongTruyen, LoiNghiepVu,
                                   NganEngine, NganXungDot)
from kho_tri_thuc_sdk.thu import CoreGia

from e_mask.che_van_ban import chuan_hoa, chuan_bi_danh
from e_mask.kho_dinh_danh import KhoDinhDanh
from e_mask.kho_ngan import AnhNgan, DauNgan, KhoNganBiMat, PortNgan, doc_het
from e_mask.kho_qua_core import KhoNhanDienQuaCore
from e_mask.khoi_tao_ngan import PHIEN_BAN_CHUAN_HOA
from e_mask.ngan import NganBoNho
from ho_tro_ngan import QuyenNganDemo


GOI = Path(__file__).resolve().parents[1] / 'goi/e_mask'
TEN = 'Công ty DEMO Ánh Dương'
TEN_KHAC = 'Công ty DEMO Bình Minh'
ALIAS = '[[MASKCT-0001]]'
CHE = 'mask.che_van_ban@1'


def _ket_qua_demo():
    return {'loai': 'van_ban_da_che', 'van_ban_da_che': {
        'phien_ban': 1, 'van_ban': 'DEMO đầu dò metadata', 'ma_yeu_cau': 'DEMO',
        'con_sot': [], 'kiem_tien_ngay': True, 'chuyen_tiep': {}}}


def _app(ham):
    app = Engine.tu_khai_bao(str(GOI / 'engine.json'))
    for nl in app.phieu['nang_luc']:
        app.nang_luc(nl['ma'])(ham)
    return app


@pytest.fixture
def bo():
    viec_kiem = []
    quyen = QuyenNganDemo()

    def kiem(viec):
        assert isinstance(viec.ngan, NganEngine)
        quyen.cap(viec.id)
        viec_kiem.pop(0)(viec)
        return _ket_qua_demo()

    app = _app(kiem)
    core = CoreGia(app)

    def chay(ham):
        viec_kiem.append(ham)
        kq = core.chay_thu(app, CHE, {'loai': 'van_ban', 'van_ban': 'DEMO'})
        assert kq['trang_thai'] == 'XONG', kq['loi']
        return kq

    return SimpleNamespace(app=app, core=core, quyen=quyen, chay=chay)


def _dong(ten=TEN, *, vung='DEMO', trang_thai='CHO_DUYET'):
    return dict(id_dinh_danh=uuid4().hex, vung_du_lieu=vung, gia_tri_goc=ten,
                gia_tri_chuan=chuan_hoa(ten), phien_ban_chuan_hoa=PHIEN_BAN_CHUAN_HOA,
                nhom='CONG_TY', trang_thai=trang_thai, so_gap=1)


def _them(viec, dong, alias=None):
    with viec.ngan.lo() as lo:
        lo.them('dinh_danh', dong)
        if alias:
            lo.them('bi_danh', dict(id_bi_danh=uuid4().hex,
                id_dinh_danh=dong['id_dinh_danh'], vung_du_lieu=dong['vung_du_lieu'],
                bi_danh=alias, bi_danh_chuan=chuan_bi_danh(alias), trang_thai='CHINH_THUC'))


def _va(dong, **gia_tri):
    return dict(id_dinh_danh=dong['id_dinh_danh'], row_version=1, gia_tri=gia_tri)


def _khong_lo(gia_tri):
    chu = json.dumps(gia_tri, ensure_ascii=False, default=str)
    for ten in (TEN, TEN_KHAC, chuan_hoa(TEN), chuan_hoa(TEN_KHAC)):
        assert ten not in chu
        assert sha256(ten.encode()).hexdigest() not in chu


def test_tim_chinh_xac_chi_null_co_khong_liet_ke_danh_muc(bo, monkeypatch, capsys):
    dong = _dong(trang_thai='CHINH_THUC')
    def kiem(viec):
        _them(viec, dong, ALIAS)
        goi = []
        tim = viec.ngan.tim
        def spy(bang, **kw):
            goi.append((bang, deepcopy(kw)))
            return tim(bang, **kw)
        monkeypatch.setattr(viec.ngan, 'tim', spy)
        kho = KhoDinhDanh(quyen=bo.quyen).mo_kho_nhan_dien(viec)
        kq = kho.tim_ung_vien(unicodedata.normalize('NFD', TEN.upper()), 'CONG_TY')
        assert kq['id_dinh_danh'] == dong['id_dinh_danh'] and kq['bi_danh'] == ALIAS
        assert kq['gia_tri_goc'] is kq['gia_tri_chuan'] is None
        assert kq['gia_tri_goc_da_ma_hoa'] is kq['gia_tri_chuan_da_ma_hoa'] is True
        _khong_lo(kq)
        assert goi[0] == ('dinh_danh', dict(loc={
            'gia_tri_chuan': chuan_hoa(TEN), 'vung_du_lieu': 'DEMO',
            'phien_ban_chuan_hoa': PHIEN_BAN_CHUAN_HOA}, gioi_han=2))
        for gia_tri in (TEN[:12], TEN + ' mới', TEN_KHAC):
            assert kho.tim_ung_vien(gia_tri, 'CONG_TY') is None
        _khong_lo(vars(kho._kho))
        _khong_lo(repr(kho))
    bo.chay(kiem)
    _khong_lo(bo.core.nhat_ky)
    _khong_lo(capsys.readouterr())


def test_alias_chinh_thuc_dung_lai_qua_hai_viec_khong_luu_map(bo):
    dong = _dong(trang_thai='CHINH_THUC')
    bo.chay(lambda v: _them(v, dong, ALIAS))
    ds, viec_id = [], []
    def tim(viec):
        kho = KhoDinhDanh(quyen=bo.quyen).mo_luot(viec)
        assert isinstance(kho, KhoNhanDienQuaCore)
        ds.append(kho.tim_ung_vien(TEN, 'CONG_TY'))
        viec_id.append(viec.id)
    bo.chay(tim)
    bo.chay(tim)
    assert len(set(viec_id)) == 2 and ds[0] == ds[1]
    assert bo.core.so_lan_ghi['ngan'] == 1
    for bang in ('dau_gap', 'cho_duyet', 'bi_danh_tam', 'ma_yeu_cau'):
        assert bo.core.xem_ngan('e_mask', bang) == []
    for muc in bo.core.xem_ngan('e_mask', 'dinh_danh'):
        _khong_lo({k: v for k, v in muc.items() if k not in {'gia_tri_goc', 'gia_tri_chuan'}})


def test_hai_ten_null_khong_gom_chung_va_demo_that_tach(bo):
    a, b, c = _dong(), _dong(TEN_KHAC), _dong(vung='THAT')
    def kiem(viec):
        for dong in (a, b, c):
            _them(viec, dong)
        demo, that = KhoNganBiMat(viec, vung='DEMO'), KhoNganBiMat(viec, vung='THAT')
        assert demo.tim_ung_vien(TEN, 'CONG_TY')['id_dinh_danh'] == a['id_dinh_danh']
        assert demo.tim_ung_vien(TEN_KHAC, 'CONG_TY')['id_dinh_danh'] == b['id_dinh_danh']
        assert that.tim_ung_vien(TEN, 'CONG_TY')['id_dinh_danh'] == c['id_dinh_danh']
        assert demo.doc(c['id_dinh_danh']) is that.doc(a['id_dinh_danh']) is None
        with pytest.raises(LoiNghiepVu):
            that.sua_metadata([_va(a, nhom='KHAC')])
    bo.chay(kiem)


def test_duyet_cung_id_khong_ghi_null_co_hay_chep_bi_mat(bo, monkeypatch):
    dong = _dong()
    def kiem(viec):
        _them(viec, dong)
        lenh_ghi = []
        ghi = viec.ngan._dt.ngan_ghi_lo
        def spy(lenh, **kw):
            lenh_ghi.extend(deepcopy(lenh))
            return ghi(lenh, **kw)
        monkeypatch.setattr(viec.ngan._dt, 'ngan_ghi_lo', spy)
        kho = KhoNganBiMat(viec, vung='DEMO')
        kho.duyet_cung_id(dong['id_dinh_danh'], row_version=1, bi_danh=ALIAS)
        assert len(lenh_ghi) == 2
        assert lenh_ghi[0]['gia_tri'] == {'trang_thai': 'CHINH_THUC'}
        assert all(l['thao_tac'] != 'xoa' for l in lenh_ghi)
        _khong_lo(lenh_ghi)
        kq = kho.doc(dong['id_dinh_danh'])
        assert (kq['row_version'], kq['so_gap'], kq['bi_danh']) == (2, 1, ALIAS)
        assert kho.tim_ung_vien(TEN, 'CONG_TY')['id_dinh_danh'] == dong['id_dinh_danh']
        with pytest.raises(LoiNghiepVu):
            kho.duyet_cung_id(dong['id_dinh_danh'], row_version=2, bi_danh='[[MASKCT-0002]]')
    bo.chay(kiem)
    assert len(bo.core.xem_ngan('e_mask', 'dinh_danh')) == 1
    assert len(bo.core.xem_ngan('e_mask', 'bi_danh')) == 1


@pytest.mark.parametrize('va', [dict(gia_tri_goc=None), dict(gia_tri_chuan=None),
    dict(gia_tri_goc_da_ma_hoa=True), dict(cum=TEN), dict(snapshot={'gia_tri': TEN}),
    dict(so_gap=2), dict(trang_thai='CHINH_THUC'), dict(nhom=TEN)])
def test_ban_va_tu_choi_bi_mat_json_dem_va_metadata_ten(bo, va):
    dong = _dong()
    def kiem(viec):
        _them(viec, dong)
        truoc = bo.core.so_lan_ghi['ngan']
        with pytest.raises(LoiNghiepVu) as exc:
            KhoNganBiMat(viec, vung='DEMO').sua_metadata([_va(dong, **va)])
        _khong_lo(str(exc.value))
        assert bo.core.so_lan_ghi['ngan'] == truoc
    bo.chay(kiem)


def test_tu_choi_la_trang_thai_khong_xoa_giu_bi_mat(bo):
    dong = _dong()
    def kiem(viec):
        _them(viec, dong)
        kho = KhoNganBiMat(viec, vung='DEMO')
        kho.sua_metadata([_va(dong, trang_thai='TU_CHOI')])
        assert kho.tim_ung_vien(TEN, 'CONG_TY')['trang_thai'] == 'TU_CHOI'
        assert kho.doc(dong['id_dinh_danh'])['gia_tri_chuan_da_ma_hoa'] is True
    bo.chay(kiem)


def test_alias_duy_nhat_cas_va_lo_rollback(bo):
    a, b = _dong(trang_thai='CHINH_THUC'), _dong(TEN_KHAC)
    def kiem(viec):
        _them(viec, a, ALIAS)
        _them(viec, b)
        kho = KhoNganBiMat(viec, vung='DEMO')
        for alias in (ALIAS, ALIAS.lower()):
            with pytest.raises(LoiNghiepVu) as exc:
                kho.duyet_cung_id(b['id_dinh_danh'], row_version=1, bi_danh=alias)
            assert exc.value.ma == 'MASK_XUNG_DOT'
            assert kho.doc(b['id_dinh_danh'])['row_version'] == 1
        bo.core.gay_xung_dot_ngan('dinh_danh')
        with pytest.raises(LoiNghiepVu) as exc:
            kho.sua_metadata([_va(a, nhom='KHAC'), _va(b, nhom='KHAC')])
        assert exc.value.ma == 'MASK_XUNG_DOT' and exc.value.thu_lai_duoc
        assert kho.doc(a['id_dinh_danh'])['row_version'] == 1
        kho.sua_metadata([_va(b, nhom='KHAC')])
        with pytest.raises(LoiNghiepVu):
            kho.sua_metadata([_va(a, nhom='KHAC'), _va(b, nhom='CONG_TY')])
        assert kho.doc(a['id_dinh_danh'])['row_version'] == 1
    bo.chay(kiem)


@pytest.mark.parametrize('so', [100, 101])
def test_lo_toi_da_100_khong_chia_gia_nguyen_tu(bo, so):
    dong = [_dong('Công ty DEMO ' + str(i)) for i in range(so)]
    def kiem(viec):
        for i in range(0, so, 100):  # Chỉ chuẩn bị dữ liệu DEMO, ngoài adapter.
            with viec.ngan.lo() as lo:
                for muc in dong[i:i + 100]:
                    lo.them('dinh_danh', muc)
        truoc = bo.core.so_lan_ghi['ngan']
        kho = KhoNganBiMat(viec, vung='DEMO')
        doi = [_va(m, nhom='KHAC') for m in dong]
        if so == 101:
            with pytest.raises(LoiNghiepVu) as exc:
                kho.sua_metadata(doi)
            assert exc.value.ma == 'MASK_QUA_GIOI_HAN'
            assert bo.core.so_lan_ghi['ngan'] == truoc
        else:
            kho.sua_metadata(doi)
            assert bo.core.so_lan_ghi['ngan'] == truoc + 1
        assert all(kho.doc(m['id_dinh_danh'])['row_version'] == (2 if so == 100 else 1) for m in dong)
    bo.chay(kiem)


def test_thieu_duy_nhat_bi_mat_chan_tao_dem_khong_gia_lay_hoac_tao(bo):
    dong = _dong()
    def kiem(viec):
        _them(viec, dong)
        kho = KhoNganBiMat(viec, vung='DEMO')
        for ham in (kho.lay_hoac_tao, kho.ghi_nhan_gap_lai):
            for _ in range(2):
                with pytest.raises(LoiNghiepVu) as exc:
                    ham(gia_tri=TEN, nhom='CONG_TY')
                assert exc.value.ma == 'MASK_KHO_CAN_CORE'
        assert bo.core.so_lan_ghi['ngan'] == 1
        # Duy nhất ID và lay_hoac_tao theo ID có thật, nhưng không thay thế
        # duy nhất theo bí mật của hai ID khác nhau.
        with viec.ngan.lo() as lo:
            lo.lay_hoac_tao('dinh_danh', {'id_dinh_danh': dong['id_dinh_danh']}, dong)
        assert lo.ket_qua[0].da_tao is False
        assert kho.doc(dong['id_dinh_danh'])['row_version'] == 1
        # SDK thật không có unique bí mật này trong R1, không mock thành có.
        with pytest.raises(LoiNghiepVu) as exc:
            with viec.ngan.lo() as lo:
                lo.lay_hoac_tao('dinh_danh', {
                    'vung_du_lieu': 'DEMO', 'gia_tri_chuan': chuan_hoa(TEN),
                    'phien_ban_chuan_hoa': PHIEN_BAN_CHUAN_HOA}, _dong())
        assert exc.value.ma == 'NGAN_DU_LIEU_SAI'
    bo.chay(kiem)


def test_bi_mat_trung_that_su_khong_chon_dong_dau(bo):
    def kiem(viec):
        _them(viec, _dong())
        _them(viec, _dong())
        with pytest.raises(LoiNghiepVu) as exc:
            KhoNganBiMat(viec, vung='DEMO').tim_ung_vien(TEN, 'CONG_TY')
        assert exc.value.ma == 'MASK_XUNG_DOT'
    bo.chay(kiem)


def test_mat_ack_sdk_gui_lai_cung_khoa_khong_cap_hai_alias(bo):
    dong = _dong()
    def kiem(viec):
        _them(viec, dong)
        bo.core.gay_mat_xac_nhan('ngan')
        KhoNganBiMat(viec, vung='DEMO').duyet_cung_id(
            dong['id_dinh_danh'], row_version=1, bi_danh=ALIAS)
        assert bo.core.so_lan_ghi['ngan'] == 2
        assert len(bo.core.xem_ngan('e_mask', 'bi_danh')) == 1
        khoa = [m[3] for m in bo.core.nhat_ky if m[0] == 'ngan']
        assert khoa[-1] == khoa[-2]
    bo.chay(kiem)


@pytest.mark.parametrize('ma_loi, status, gui_lai', [
    ('MAT_PHAN_HOI', 503, True), ('NGAN_MAT_PHAN_HOI', 503, True),
    ('MAT_PHAN_HOI', 408, False), ('NGAN_MAT_PHAN_HOI', 408, False)])
def test_mat_moi_ack_chua_ro_retry_khong_cap_dem_lai(bo, monkeypatch, capsys, ma_loi, status, gui_lai):
    dong = _dong()
    def kiem(viec):
        _them(viec, dong)
        ghi = viec.ngan._dt.ngan_ghi_lo
        khoa = []
        def mat_ack(lenh, **kw):
            ghi(lenh, **kw)
            khoa.append(kw['khoa'])
            raise LoiDuongTruyen(ma_loi, TEN, http_status=status, thu_lai_duoc=gui_lai)
        monkeypatch.setattr(viec.ngan._dt, 'ngan_ghi_lo', mat_ack)
        kho = KhoNganBiMat(viec, vung='DEMO')
        ma = []
        for _ in range(2):
            with pytest.raises(ChuaRo) as exc:
                kho.duyet_cung_id(dong['id_dinh_danh'], row_version=1, bi_danh=ALIAS)
            ma.append(exc.value.ma_tuong_quan)
            _khong_lo(str(exc.value))
        assert ma[0] == ma[1] and len(khoa) == (4 if gui_lai else 1) and len(set(khoa)) == 1
        assert bo.core.so_lan_ghi['ngan'] == 2
        with pytest.raises(LoiNghiepVu) as exc:
            KhoNganBiMat(viec, vung='DEMO').duyet_cung_id(
                dong['id_dinh_danh'], row_version=1, bi_danh='[[MASKCT-0002]]')
        assert exc.value.ma == 'MASK_XUNG_DOT'
        assert len(bo.core.xem_ngan('e_mask', 'bi_danh')) == 1
        assert kho.doc(dong['id_dinh_danh'])['so_gap'] == 1
    bo.chay(kiem)
    _khong_lo(capsys.readouterr())


def test_hai_viec_core_gia_xung_dot_cung_id_chi_mot_alias(bo):
    dong = _dong()
    bo.chay(lambda v: _them(v, dong))
    rao = Barrier(2)
    ket_qua = []
    def tranh(viec):
        kho = KhoNganBiMat(viec, vung='DEMO')
        phien = kho.doc(dong['id_dinh_danh'])['row_version']
        rao.wait(timeout=10)
        try:
            kho.duyet_cung_id(dong['id_dinh_danh'], row_version=phien,
                             bi_danh='[[MASKCT-' + uuid4().hex + ']]')
            ket_qua.append((viec.id, 'DA_GHI'))
        except LoiNghiepVu as exc:
            ket_qua.append((viec.id, exc.ma))
        return _ket_qua_demo()
    apps = [_app(tranh), _app(tranh)]
    ma = [bo.core.giao_viec(CHE, {'loai': 'van_ban', 'van_ban': 'DEMO'}) for _ in range(2)]
    with ThreadPoolExecutor(2) as pool:
        futures = [pool.submit(bo.core.chay, app) for app in apps]
        for f in futures:
            f.result(timeout=20)
    assert sorted(k for _, k in ket_qua) == ['DA_GHI', 'MASK_XUNG_DOT']
    assert len({m for m, _ in ket_qua}) == 2
    assert all(bo.core.xem(m)['trang_thai'] == 'XONG' for m in ma)
    assert len(bo.core.xem_ngan('e_mask', 'bi_danh')) == 1


@pytest.mark.parametrize('lop', ['anh', 'dau', 'port', 'liet_ke'])
def test_ngan_sdk_khong_di_vao_snapshot_ram_cu(bo, lop):
    def kiem(viec):
        with pytest.raises(LoiNghiepVu):
            if lop == 'anh':
                AnhNgan(viec.ngan, 'DEMO')
            elif lop == 'dau':
                DauNgan(viec.ngan)
            elif lop == 'port':
                PortNgan(viec.ngan, bo.quyen, viec, loai='che', ma_yeu_cau=None, bam_dau_vao='DEMO')
            else:
                doc_het(viec.ngan, 'dinh_danh', 'DEMO')
        assert bo.core.so_lan_ghi['ngan'] == 0
    bo.chay(kiem)


def test_kho_moi_khong_fallback_ram_callback_snapshot_hoac_bam_ten(bo, monkeypatch):
    def cam(*a, **kw):
        pytest.fail('Không được gọi snapshot hoặc băm đường cũ.')
    def kiem(viec):
        monkeypatch.setattr('e_mask.kho_dinh_danh.bam_noi_dung', cam)
        kho = KhoDinhDanh(ngan=viec.ngan, quyen=bo.quyen, goi_kho=cam).mo_luot(viec)
        assert isinstance(kho, KhoNhanDienQuaCore)
        assert kho.tim_ung_vien(TEN, 'CONG_TY') is None
        for ham in (kho.liet_ke_dinh_danh, kho.chot, kho.ghi_cho_duyet, kho.ghi_nhan_gap_lai):
            with pytest.raises(LoiNghiepVu) as exc:
                ham()
            assert exc.value.ma == 'MASK_KHO_CAN_CORE'
        with pytest.raises(LoiNghiepVu) as exc:
            kho.tra_dinh_danh(ALIAS)
        assert exc.value.ma == 'MASK_ANH_XA_KHONG_CON'
    bo.chay(kiem)
    with pytest.raises(LoiNghiepVu) as exc:
        KhoNganBiMat(SimpleNamespace(ngan=NganBoNho()), vung='DEMO')
    assert exc.value.ma == 'MASK_NGAN_CHUA_CO'


def test_quyen_thu_hoi_hoac_doi_vung_giua_tim_chan_ket_qua(bo, monkeypatch):
    def kiem(viec):
        _them(viec, _dong(trang_thai='CHINH_THUC'), ALIAS)
        kho = KhoDinhDanh(quyen=bo.quyen).mo_kho_nhan_dien(viec)
        tim = viec.ngan.tim
        def doi_vung(*a, **kw):
            ket_qua = tim(*a, **kw)
            bo.quyen.vung = 'THAT'
            return ket_qua
        monkeypatch.setattr(viec.ngan, 'tim', doi_vung)
        with pytest.raises(LoiNghiepVu) as exc:
            kho.tim_ung_vien(TEN, 'CONG_TY')
        assert exc.value.ma == 'MASK_NGU_CANH_CHUA_XAC_MINH'
        _khong_lo(str(exc.value))
    bo.chay(kiem)


def test_mo_che_khong_tra_nguoc_kho_bi_mat(bo):
    def kiem(viec):
        ctx = bo.quyen.cap(viec.id, loai='mo_che')
        with pytest.raises(LoiNghiepVu) as exc:
            KhoDinhDanh(quyen=bo.quyen).mo_luot(
                viec, loai='mo_che', ma_yeu_cau=ctx.ma_yeu_cau)
        assert exc.value.ma == 'MASK_ANH_XA_KHONG_CON'
        assert bo.core.so_lan_ghi['ngan'] == 0
    bo.chay(kiem)


def test_ma_chua_ro_tu_nguon_khong_lam_lo_ten(bo, monkeypatch):
    def kiem(viec):
        tim = viec.ngan._dt.ngan_tim
        def loi(bang, **kw):
            tim(bang, **kw)
            raise ChuaRo(TEN)
        monkeypatch.setattr(viec.ngan._dt, 'ngan_tim', loi)
        kho = KhoNganBiMat(viec, vung='DEMO')
        with pytest.raises(ChuaRo) as exc:
            kho.tim_ung_vien(TEN, 'CONG_TY')
        _khong_lo([exc.value.ma_tuong_quan, str(exc.value)])
        assert bo.core.so_lan_ghi['ngan'] == 0
    bo.chay(kiem)
