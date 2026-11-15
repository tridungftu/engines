"""MASK-R1: đã kiểm bằng Core giả (CoreGia), chỉ DEMO.

Đầu dò SDK ngoài gói kiểm khai báo/cấu hình/ngăn, không thay handler vận hành
và không chứng minh luồng che/mở che cũ đã nối R1 hoặc không còn kho RAM cũ.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from types import SimpleNamespace
from uuid import uuid4

import pytest
from kho_tri_thuc_sdk.engine import Engine, LoiDuongTruyen, LoiNghiepVu, NganXungDot, kiem_phieu
from kho_tri_thuc_sdk.thu import CoreGia

from e_mask.khoi_tao_ngan import ngan_cua_viec, thoi_han_anh_xa_giay
from e_mask.ngan import NganBoNho
from kiem_doc_lap import _kiem_ke, _kiem_lenh_sql, kiem_tra


GOI = Path(__file__).resolve().parents[1] / 'goi/e_mask'
PHIEU = json.loads((GOI / 'engine.json').read_text(encoding='utf-8'))
TEN_GOC = 'Công ty DEMO Ánh Dương'
TEN_CHUAN = 'công ty demo ánh dương'


def _dinh_danh():
    return dict(id_dinh_danh=uuid4().hex, vung_du_lieu='DEMO',
                gia_tri_goc=TEN_GOC, gia_tri_chuan=TEN_CHUAN,
                phien_ban_chuan_hoa='DEMO-1', nhom='CONG_TY',
                trang_thai='CHO_DUYET', so_gap=1)


def _bi_danh(id_dinh_danh):
    return dict(id_bi_danh=uuid4().hex, id_dinh_danh=id_dinh_danh,
                vung_du_lieu='DEMO', bi_danh='[[MASKCT-0001]]',
                bi_danh_chuan='MASKCT-0001', trang_thai='CHINH_THUC')


def _dau_do(kiem, *, cau_hinh=None):
    # Chỉ đăng ký đầu dò ở test trên đúng manifest/schema mới; không nới chay.py.
    app = Engine.tu_khai_bao(str(GOI / 'engine.json'))
    core = CoreGia(app)
    if cau_hinh is not None:
        core.dat_cau_hinh(app.ma, cau_hinh)

    def ngoai_dau_do(viec):
        raise LoiNghiepVu('DEMO_NGOAI_DAU_DO', 'Năng lực này không thuộc phép kiểm DEMO.')

    for nang_luc in app.phieu['nang_luc']:
        if nang_luc['ma'] != 'mask.che_van_ban@1':
            app.nang_luc(nang_luc['ma'])(ngoai_dau_do)

    @app.nang_luc('mask.che_van_ban@1')
    def do(viec):
        kiem(viec, core)
        return {'loai': 'van_ban_da_che', 'van_ban_da_che': {
            'phien_ban': 1, 'van_ban': 'DEMO', 'ma_yeu_cau': 'DEMO',
            'con_sot': [], 'kiem_tien_ngay': True, 'chuyen_tiep': {},
        }}

    kq = core.chay_thu(app, 'mask.che_van_ban@1', {'loai': 'van_ban', 'van_ban': 'DEMO'})
    assert kq['trang_thai'] == 'XONG', kq['loi']
    return core, app


def _kiem_bi_mat(ban_ghi):
    assert ban_ghi is not None
    for ten in ('gia_tri_goc', 'gia_tri_chuan'):
        assert ban_ghi.gia_tri[ten] is None
        assert ban_ghi.gia_tri[ten + '_da_ma_hoa'] is True
        assert ten + '_bam' not in ban_ghi.gia_tri
    chu = json.dumps(ban_ghi.gia_tri, ensure_ascii=False)
    assert TEN_GOC not in chu and TEN_CHUAN not in chu


def test_khai_bao_kho_kin_va_cau_hinh_dung_sdk():
    assert kiem_phieu(PHIEU, GOI) == []
    assert PHIEU['tuong_thich']['sdk'] == '>=2.2.0 <3.0.0'
    assert PHIEU['che_do_chay'] == 'cuc_bo'
    assert PHIEU['tai_nguyen']['so_viec_dong_thoi'] == 1
    assert PHIEU['bi_mat'] == []  # Khác cờ bí mật của cột ngăn, không xin khóa.
    assert {b['bang'] for b in PHIEU['ngan_du_lieu']} == {'dinh_danh', 'bi_danh'}
    for bang in PHIEU['ngan_du_lieu']:
        truong = {t['ma']: t for t in bang['truong']}
        assert bang['pham_vi'] == 'engine'
        assert bang['khoa'] == ['id_' + bang['bang']]
        assert all(t['kieu'] != 'json' for t in truong.values())
        assert not {'ma_yeu_cau', 'anh_xa', 'cum', 'dinh_danh', 'snapshot'} & truong.keys()
        assert all(not truong[k].get('bi_mat') for k in bang['khoa'])
        if bang['bang'] == 'dinh_danh':
            assert {k for k, t in truong.items() if t.get('bi_mat')} == {
                'gia_tri_goc', 'gia_tri_chuan'}
            assert all(truong[k]['bat_buoc'] for k in ('gia_tri_goc', 'gia_tri_chuan'))
            assert bang['duy_nhat'] == [['id_dinh_danh']]
    schema = json.loads((GOI / 'cau_hinh.schema.json').read_text(encoding='utf-8'))
    assert schema['additionalProperties'] is False
    assert set(schema['properties']) == {'thoi_han_anh_xa_giay'}
    ttl = schema['properties']['thoi_han_anh_xa_giay']
    assert (ttl['type'], ttl['default'], ttl['minimum'], ttl['maximum']) == ('integer', 600, 60, 900)
    assert (GOI.parents[1] / 'LUU-TRU/sdk_truoc_2_2/KHAI-SDK-2.1.json').is_file()


@pytest.mark.parametrize('cau_hinh, dung', [(None, 600), ({}, 600),
                                         ({'thoi_han_anh_xa_giay': 60}, 60),
                                         ({'thoi_han_anh_xa_giay': 900}, 900)])
def test_sdk_dien_mac_dinh_va_bien_ttl(cau_hinh, dung):
    def kiem(viec, core):
        assert viec.cau_hinh == {'thoi_han_anh_xa_giay': dung}
        assert thoi_han_anh_xa_giay(viec) == dung
    _dau_do(kiem, cau_hinh=cau_hinh)


@pytest.mark.parametrize('gia_tri', [59, 901, True, False, None, '600', 600.5, [], {}])
def test_core_gia_tu_choi_cau_hinh_ttl_sai(gia_tri):
    app = Engine.tu_khai_bao(str(GOI / 'engine.json'))
    core = CoreGia(app)
    with pytest.raises(LoiDuongTruyen) as exc:
        core.dat_cau_hinh(app.ma, {'thoi_han_anh_xa_giay': gia_tri})
    assert exc.value.ma == 'NGAN_DU_LIEU_SAI'


@pytest.mark.parametrize('cau_hinh', [None, [], {'khac': 600},
                                   {'thoi_han_anh_xa_giay': True},
                                   {'thoi_han_anh_xa_giay': 600.0},
                                   {'thoi_han_anh_xa_giay': 59},
                                   {'thoi_han_anh_xa_giay': 901}])
def test_cua_doc_ttl_tu_choi_du_lieu_khong_phai_so_nguyen(cau_hinh):
    with pytest.raises(LoiNghiepVu) as exc:
        thoi_han_anh_xa_giay(SimpleNamespace(cau_hinh=cau_hinh))
    assert exc.value.ma == 'MASK_CAU_HINH_KHONG_HOP_LE'


def test_doi_cau_hinh_khong_doi_ban_chup_cua_viec():
    def kiem(viec, core):
        assert thoi_han_anh_xa_giay(viec) == 600
        core.dat_cau_hinh('e_mask', {'thoi_han_anh_xa_giay': 60})
        assert thoi_han_anh_xa_giay(viec) == 600
    _dau_do(kiem)


def test_ngan_sdk_ghi_doc_tim_bang_chinh_xac_chi_null_va_co(capsys):
    dong = _dinh_danh()
    alias = _bi_danh(dong['id_dinh_danh'])
    def kiem(viec, core):
        ngan = ngan_cua_viec(viec)
        assert ngan is viec.ngan
        with ngan.lo() as lo:
            lo.them('dinh_danh', dong)
            lo.them('bi_danh', alias)
        _kiem_bi_mat(ngan.doc('dinh_danh', {'id_dinh_danh': dong['id_dinh_danh']}))
        for cot, gia_tri in [('gia_tri_goc', TEN_GOC), ('gia_tri_chuan', TEN_CHUAN)]:
            ds = ngan.tim('dinh_danh', loc={cot: gia_tri, 'vung_du_lieu': 'DEMO'})
            assert len(ds.danh_sach) == 1
            _kiem_bi_mat(ds.danh_sach[0])
            for khong_khop in (gia_tri[:10], gia_tri + ' DEMO', gia_tri.upper()):
                assert ngan.tim('dinh_danh', loc={cot: khong_khop}).danh_sach == []
        assert ngan.tim('dinh_danh', loc={'gia_tri_chuan': TEN_CHUAN,
                                         'vung_du_lieu': 'THAT'}).danh_sach == []
        doc_alias = ngan.doc('bi_danh', {'id_bi_danh': alias['id_bi_danh']})
        assert doc_alias.gia_tri['id_dinh_danh'] == dong['id_dinh_danh']
        assert doc_alias.gia_tri['bi_danh'] == alias['bi_danh']
        assert TEN_GOC not in json.dumps(doc_alias.gia_tri, ensure_ascii=False)
        assert TEN_CHUAN not in json.dumps(core.nhat_ky, ensure_ascii=False)
    _dau_do(kiem)
    xuat = capsys.readouterr()
    assert TEN_GOC not in xuat.out + xuat.err and TEN_CHUAN not in xuat.out + xuat.err


def test_sua_metadata_khong_ghi_null_de_bi_mat_va_cas():
    dong = _dinh_danh()
    khoa = {'id_dinh_danh': dong['id_dinh_danh']}
    def kiem(viec, core):
        ngan = ngan_cua_viec(viec)
        with ngan.lo() as lo:
            lo.them('dinh_danh', dong)
        cu = ngan.doc('dinh_danh', khoa)
        with ngan.lo() as lo:
            lo.sua('dinh_danh', khoa, {'trang_thai': 'CHINH_THUC', 'so_gap': 2},
                   row_version=cu.row_version)
        moi = ngan.doc('dinh_danh', khoa)
        _kiem_bi_mat(moi)
        assert moi.row_version == cu.row_version + 1
        assert moi.gia_tri['trang_thai'] == 'CHINH_THUC'
        assert len(ngan.tim('dinh_danh', loc={'gia_tri_chuan': TEN_CHUAN}).danh_sach) == 1
        with pytest.raises(NganXungDot):
            with ngan.lo() as lo:
                lo.sua('dinh_danh', khoa, {'trang_thai': 'TU_CHOI'}, row_version=cu.row_version)
        assert ngan.doc('dinh_danh', khoa).gia_tri['trang_thai'] == 'CHINH_THUC'
    _dau_do(kiem)


def test_cho_phep_trung_bi_mat_la_thieu_c_p4_03_chua_nghiem_thu_duy_nhat():
    # Chứng minh khoảng thiếu, KHÔNG coi hai tên trùng là chống trùng đã đạt.
    def kiem(viec, core):
        ngan = ngan_cua_viec(viec)
        with ngan.lo() as lo:
            lo.them('dinh_danh', _dinh_danh())
            lo.them('dinh_danh', _dinh_danh())
        ds = ngan.tim('dinh_danh', loc={'gia_tri_chuan': TEN_CHUAN, 'vung_du_lieu': 'DEMO'})
        assert len(ds.danh_sach) == 2
        assert len({d.gia_tri['id_dinh_danh'] for d in ds.danh_sach}) == 2
        for d in ds.danh_sach:
            _kiem_bi_mat(d)
    _dau_do(kiem)


def test_duy_nhat_alias_va_lo_nguyen_tu():
    dong = _dinh_danh()
    alias = _bi_danh(dong['id_dinh_danh'])
    def kiem(viec, core):
        ngan = ngan_cua_viec(viec)
        with ngan.lo() as lo:
            lo.them('dinh_danh', dong)
            lo.them('bi_danh', alias)
        with pytest.raises(NganXungDot):
            with ngan.lo() as lo:
                lo.sua('dinh_danh', {'id_dinh_danh': dong['id_dinh_danh']},
                       {'so_gap': 99}, row_version=1)
                lo.them('bi_danh', dict(alias, id_bi_danh=uuid4().hex))
        assert ngan.doc('dinh_danh', {'id_dinh_danh': dong['id_dinh_danh']}).row_version == 1
        assert len(ngan.tim('bi_danh').danh_sach) == 1
    _dau_do(kiem)


def test_loi_khi_thieu_cua_ngan_khong_tao_ram():
    for viec in (SimpleNamespace(), SimpleNamespace(ngan=None),
                 SimpleNamespace(ngan=NganBoNho([]))):
        with pytest.raises(LoiNghiepVu) as exc:
            ngan_cua_viec(viec)
        assert exc.value.ma == 'MASK_NGAN_CHUA_CO'


def test_migration_dung_schema_cot_he_thong_va_cot_bi_mat():
    chu = (GOI / 'sql/001_tao_kho_bi_danh.sql').read_text(encoding='utf-8')
    _kiem_lenh_sql(chu)
    bang = dict(re.findall(r'CREATE TABLE eng_e_mask\.(\w+)\s*\((.*?)\n\);', chu, re.S))
    assert set(bang) == {b['bang'] for b in PHIEU['ngan_du_lieu']}
    he_thong = {'id', 'phap_nhan_id', 'row_version', 'tao_luc', 'sua_luc', 'het_han_luc', 'viec_id'}
    for khai in PHIEU['ngan_du_lieu']:
        than = bang[khai['bang']]
        cac_cot = set(re.findall(r'^    (\w+) (?:uuid|text|bytea|numeric|bigint|timestamptz)\b', than, re.M))
        dung = he_thong | {t['ma'] for t in khai['truong']}
        dung |= {t['ma'] + '_bam' for t in khai['truong'] if t.get('bi_mat')}
        assert cac_cot == dung
        for t in khai['truong']:
            if t.get('bi_mat'):
                assert f"{t['ma']} bytea NOT NULL" in than
                assert f"{t['ma']}_bam bytea NOT NULL" in than
        for nhom in khai['duy_nhat']:
            assert 'UNIQUE (' + ', '.join(nhom) + ')' in than
    assert 'CREATE SCHEMA' not in chu and 'INSERT' not in chu
    assert not re.search(r'UNIQUE\s*\([^)]*(?:gia_tri_goc|gia_tri_chuan)', chu)


def test_kiem_ke_day_du_bytes_va_sha_tung_tep():
    _kiem_ke(GOI, (GOI / 'sql/kiem_ke.json').read_text(encoding='utf-8'))


def _goi_kiem(tmp_path, lenh='CREATE TABLE eng_e_mask.demo (id uuid PRIMARY KEY);'):
    (tmp_path / 'sql').mkdir()
    phieu = {'ma': 'e_mask', 'phien_ban': 'DEMO', 'du_lieu': deepcopy(PHIEU['du_lieu'])}
    (tmp_path / 'engine.json').write_text(json.dumps(phieu), encoding='utf-8')
    (tmp_path / 'sql/001_demo.sql').write_text(lenh, encoding='utf-8')
    kk = {'phien_ban': 'DEMO', 'tep': []}
    for p in sorted(tmp_path.rglob('*')):
        if p.is_file():
            b = p.read_bytes()
            kk['tep'].append({'duong_dan': p.relative_to(tmp_path).as_posix(),
                              'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()})
    (tmp_path / 'sql/kiem_ke.json').write_text(json.dumps(kk), encoding='utf-8')
    return kk


def test_kiem_doc_lap_chi_cho_migration_da_khai_va_kiem_ke(tmp_path):
    _goi_kiem(tmp_path)
    assert kiem_tra(tmp_path) == []


@pytest.mark.parametrize('lenh', [
    'CREATE TABLE public.demo (id uuid PRIMARY KEY);',
    'CREATE TABLE eng_khac.demo (id uuid PRIMARY KEY);',
    'DROP TABLE eng_e_mask.demo;', 'DELETE FROM eng_e_mask.demo;',
    "INSERT INTO eng_e_mask.demo VALUES ('DEMO');", 'SELECT 1;',
    'CREATE SCHEMA eng_e_mask;',
    'CREATE TABLE eng_e_mask.demo (id uuid DEFAULT public.demo());',
    'CREATE TABLE eng_e_mask.demo (id uuid REFERENCES public.demo(id));',
    "DO $$ BEGIN RAISE NOTICE 'DEMO'; END $$;",
])
def test_kiem_doc_lap_chan_lenh_ngoai_migration_r1(tmp_path, lenh):
    _goi_kiem(tmp_path, lenh)
    assert kiem_tra(tmp_path)


@pytest.mark.parametrize('loai', ['bytes', 'sha', 'thieu', 'lap', 'vuot_goi', 'them_tep'])
def test_kiem_doc_lap_chan_kiem_ke_sai(tmp_path, loai):
    kk = _goi_kiem(tmp_path)
    if loai == 'bytes':
        kk['tep'][0]['bytes'] += 1
    elif loai == 'sha':
        kk['tep'][0]['sha256'] = '0' * 64
    elif loai == 'thieu':
        kk['tep'].pop()
    elif loai == 'lap':
        kk['tep'].append(deepcopy(kk['tep'][0]))
    elif loai == 'vuot_goi':
        kk['tep'][0]['duong_dan'] = '../demo.py'
    else:
        (tmp_path / 'them_demo.py').write_text('# DEMO', encoding='utf-8')
    (tmp_path / 'sql/kiem_ke.json').write_text(json.dumps(kk), encoding='utf-8')
    assert kiem_tra(tmp_path)
