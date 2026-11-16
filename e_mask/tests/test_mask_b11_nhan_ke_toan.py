"""B11 lượt 4: danh sách đóng lead duyệt, development DEMO độc lập gold."""
import unicodedata
import xml.etree.ElementTree as ET

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu

from e_mask import tep_word as tw, tep_excel as tx
from ho_tro_mask_b5 import bo as bo_ram
from ho_tro_mask_b7 import bo, chay, chuan_bi_het, giao
from test_mask_b11 import (
    TEN, SEEDS, ALIAS, _nguon_da_duyet, _phan, _tep_phan_vi_du, _chu_doc_lap,
)
from test_mask_b11_hau_kiem import _cua_cuoi
from e_mask import hau_kiem_tep as hk


NHAN_DA_DUYET = (
    'số sổ cái', 'sổ cái', 'số chứng từ', 'chứng từ', 'số hóa đơn',
    'hóa đơn', 'số phiếu', 'phiếu thu', 'phiếu chi', 'số tài liệu',
    'bảng kê', 'bảng', 'trang', 'kỳ', 'tháng', 'quý', 'năm', 'dòng',
    'cột', 'mục', 'số',
)
VI_TRI = [('docx', 'noi_dung'), ('xlsx', 'noi_dung'),
          ('docx', 'tieu_de'), ('xlsx', 'tieu_de'), ('xlsx', 'ten_sheet')]
PHAN_VI_DU = [
    ('DEMO số sổ cái Vinamilk', 'Vinamilk'),
    ('DEMO sổ cái lan', 'lan'),
    ('DEMO số Techcombank 73', 'Techcombank'),
    ('DEMO bảng kê quỳnh trâm', 'quỳnh trâm'),
    ('DEMO số sổ cái 73 Hòa Phát', 'Hòa Phát'),
    ('DEMO sổcái 73', 'sổcái'),
    ('DEMO Số Sổ Cái 73', 'Số Sổ Cái'),
]
HOP_LE = ['DEMO số sổ cái 73', 'DEMO - số chứng từ 12/2026',
          'TEST bảng kê tháng 11', 'DEMO']


def test_danh_sach_dong_dung_nguyen_quyet_dinh_lead():
    assert tw.NHAN_KE_TOAN_SAU_MARKER == NHAN_DA_DUYET


@pytest.mark.parametrize('nhan', NHAN_DA_DUYET)
@pytest.mark.parametrize('marker', ['DEMO', 'TEST', 'SAMPLE', 'DRAFT'])
def test_moi_nhan_khop_nguyen_cum_sau_nfc_va_gon_khoang_trang(nhan, marker):
    duoi = unicodedata.normalize('NFD', nhan).replace(' ', '\t\u00a0  ')
    assert tw._duoi_marker_hop_le(' - ' + duoi + ' 73')
    chu = marker + ' ' + duoi + ' 73'
    # Cảnh báo marker vẫn có thật, chỉ được miễn sau kiểm đuôi hợp lệ.
    con, du = tw.che._kiem_con_sot(chu, [])
    assert du and con
    assert not list(tw._canh_bao_chu_chua_dat(chu, con))


@pytest.mark.parametrize('duoi', [
    'asố 73', 'sốa 73', '1số 73', 'số1 73', '_số 73', 'số_ 73',
    'sổcái 73', 'so so cai 73', 'Số Sổ Cái 73', 'số sổ cái Vinamilk',
    'sổ cái lan', 'số Techcombank 73', 'bảng kê quỳnh trâm',
    'số sổ cái 73 Hòa Phát',
    'số1 VND', '1 VNDsố', 'số2026-11-09', '2026-11-09số',
])
def test_chu_ngoai_danh_sach_va_tien_to_hau_to_khong_duoc_mien(duoi):
    assert not tw._duoi_marker_hop_le(duoi)


@pytest.mark.parametrize('nhan', NHAN_DA_DUYET)
def test_khong_ap_danh_sach_cho_duoi_tong_thu_chi(nhan):
    for dau in ('Tổng thu đã kiểm tra ', 'Tổng chi đã đối chiếu '):
        chu = dau + nhan + ' 73'
        assert not tw._duoi_tong_hop_hop_le(nhan + ' 73')
        # Không thay detector: kiểm trực tiếp cảnh báo nghi tên ở cụm tổng.
        muc = dict(nhom='CA_NHAN', ly_do='nghi tên người viết thường',
                   can_cu=['AM_TEN:DEMO'], vi_tri=dict(bat_dau=0, ket_thuc=8))
        assert list(tw._canh_bao_chu_chua_dat(chu, [muc])) == [muc]


@pytest.mark.parametrize('loai,vi_tri', VI_TRI)
@pytest.mark.parametrize('chu,ten_that', PHAN_VI_DU)
@pytest.mark.parametrize('da_biet', [False, True])
def test_luot_4_hai_lop_khong_co_ban_ro_trong_moi_phan_tep(loai, vi_tri, chu, ten_that, da_biet):
    nhom = 'CONG_TY' if ten_that in {'Vinamilk', 'Techcombank', 'Hòa Phát'} else 'CA_NHAN'
    seeds = SEEDS + ((ten_that, nhom, '[[MASK-B11-LUOT4]]'),) if da_biet else SEEDS
    b = bo(loai, raw=_tep_phan_vi_du(loai, chu, vi_tri), seeds=seeds, dang='tep')
    try:
        assert ten_that.encode() in b''.join(_phan(b.raw).values())
        k = chay(b)
        if k['trang_thai'] == 'XONG':
            chuan_bi_het(b)
            giao(b)
            k = chay(b)
        if k['trang_thai'] == 'XONG':
            raw = b.c.doc_tep(k['ket_qua']['truong']['tep_da_che']['tep_id'])
            for ten_phan, du in _phan(raw).items():
                cay = ET.fromstring(du)
                cac_chu = [du.decode('utf-8'), ''.join(cay.itertext())]
                cac_chu.extend(v for n in cay.iter() for v in n.attrib.values())
                for phan_ten in ten_that.split():
                    assert all(_chu_doc_lap(phan_ten) not in _chu_doc_lap(c)
                               for c in cac_chu), ten_phan
        else:
            assert k['trang_thai'] == 'LOI' and k['ket_qua'] is None
            assert k['loi']['ma'] in {'MASK_DINH_DANH_CHUA_DAT', 'MASK_TEP_CHUA_HO_TRO'}, k
            assert b.ram._ban_ghi is None and not b.cong.giao_cuoi
    finally:
        if b.ram._ban_ghi:
            b.ram._don(b.ram._ban_ghi)


@pytest.mark.parametrize('loai,vi_tri,chu', [
    (loai, vi_tri, chu) for loai, vi_tri in VI_TRI for chu in HOP_LE
    if vi_tri != 'ten_sheet' or not any(c in chu for c in '\\/*?:[]')
])
def test_cu_phap_duoc_duyet_phat_hanh_hai_lop_va_qua_moi_zip_part(loai, vi_tri, chu):
    b = bo(loai, raw=_tep_phan_vi_du(loai, chu, vi_tri), seeds=SEEDS, dang='tep')
    try:
        chuan_bi_het(b)
        giao(b)
        k = chay(b)
        assert k['trang_thai'] == 'XONG', k
        raw = b.c.doc_tep(k['ket_qua']['truong']['tep_da_che']['tep_id'])
        cac_phan = _phan(raw)
        assert ALIAS.encode() in b''.join(cac_phan.values())
        for ten_phan, du in cac_phan.items():
            cay = ET.fromstring(du)
            cac_chu = [du.decode('utf-8'), ''.join(cay.itertext())]
            cac_chu.extend(v for n in cay.iter() for v in n.attrib.values())
            assert all(TEN not in c for c in cac_chu), ten_phan
        ten_phan = ('word/document.xml' if loai == 'docx' else 'xl/worksheets/sheet1.xml') if vi_tri == 'noi_dung' else (
            'docProps/core.xml' if vi_tri == 'tieu_de' else 'xl/workbook.xml')
        assert chu.encode() in cac_phan[ten_phan]
    finally:
        if b.ram._ban_ghi:
            b.ram._don(b.ram._ban_ghi)


@pytest.mark.parametrize('ham', [tw._kiem_vung, tx._kiem_vung])
@pytest.mark.parametrize('chu', HOP_LE + [
    'SAMPLE số sổ cái 73; tổng chi đã đối chiếu.',
    'DRAFT bảng kê: 3.754.200 VND, 12 USD; tổng thu đã kiểm tra.',
    'DEMO ngày 9 tháng 11 năm 2026.',
    unicodedata.normalize('NFD', 'DEMO số  sổ\u00a0cái 73'),
])
def test_hai_dinh_dang_giu_nguyen_nhan_tien_ngay_va_nfd(ham, chu):
    b = bo_ram(seeds=())
    with b.ram.buoc(b.v) as buoc:
        assert ham(chu, (), buoc).da_che == chu


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('chu', HOP_LE)
def test_cua_cuoi_cung_nhan_danh_sach_dong(loai, chu, monkeypatch):
    s, sau = _cua_cuoi(monkeypatch, loai, chu)
    assert hk._kiem_cuoi(s, kiem=lambda: None, buoc=None) is sau


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('chu', [c for c, _ in PHAN_VI_DU] + [
    'DEMO số sổ cái 0123456789012',
    'DEMO số sổ cái; Số tài khoản: 2026-11-09',
])
def test_cua_cuoi_van_chan_chu_la_va_dinh_danh_so(loai, chu, monkeypatch):
    s, _ = _cua_cuoi(monkeypatch, loai, chu)
    con, du = hk.che._kiem_con_sot(chu, [])
    assert du and con
    with pytest.raises(LoiNghiepVu) as exc:
        hk._kiem_cuoi(s, kiem=lambda: None, buoc=None)
    assert exc.value.ma == 'MASK_DINH_DANH_CHUA_DAT'
