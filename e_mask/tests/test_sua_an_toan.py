"""Hồi quy kiểm độc lập của lead; mọi định danh dưới đây là DEMO đã duyệt."""
import json
import sys
import traceback
import unicodedata

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu

from e_mask import che_van_ban, phong_bi
from ho_tro_duyet_lich_su import DuyetDinhDanh
from e_mask.kho_dinh_danh import KhoDinhDanh
from e_mask.kho_ngan import khoa_dau, khoa_muc
from e_mask.nguon.privacy import core
from e_mask.nguon.privacy.types import chuan_hoa_vi_tri
from ho_tro_ngan import ADMIN, TEN, VAN_BAN, ai_demo, viec_demo
from test_mask_4_6 import CHE, MO, che_demo, ghep, mo_demo


def bo_an(chu):
    # Phép kiểm độc lập với helper chạy thật, tránh cùng bỏ sót một nhóm.
    return ''.join(c for c in chu if unicodedata.category(c) != 'Cf'
                   and not 0xFE00 <= ord(c) <= 0xFE0F
                   and not 0xE0100 <= ord(c) <= 0xE01EF
                   and ord(c) not in (0x180B, 0x180C, 0x180D, 0x180F))


def chuan(chu):
    return ' '.join(unicodedata.normalize('NFC', bo_an(chu)).split()).casefold()


MAU_LEAD = [
    ('Vinamilk Holdings', 'CONG_TY', 'Ký với Vin\u200bamilk Hol\u200bdings'),
    ('Trần Bảo Long', 'CA_NHAN', 'Ký với Tr\u200bần B\u200bảo L\u200bong'),
    ('Trần Bảo Long', 'CA_NHAN', 'Trần\u200d Bảo\u200d Long'),
    ('Nguyễn Văn An', 'CA_NHAN', 'Nguy\u200bễn Văn An'),
    ('Công ty TNHH Ánh Dương', 'CONG_TY', 'Công\u200b ty TNHH Ánh\u200b Dương'),
    ('Vinamilk Holdings', 'CONG_TY', 'Vina\u00admilk Holdings'),
]


@pytest.mark.parametrize('ten,nhom,chu', MAU_LEAD)
@pytest.mark.parametrize('da_duyet', [True, False], ids=['da_duyet', 'tu_phat_hien'])
def test_mau_lead_khong_lot_dinh_danh(ten, nhom, chu, da_duyet):
    n, q, c, app = ghep()
    if da_duyet:
        DuyetDinhDanh(n, ADMIN).nhap_demo(
            [{'gia_tri': ten, 'nhom': nhom, 'ma_junsky': 'KH-DEMO-001'}], thuc_hien=True)
    v = c.giao_viec(CHE, {'loai': 'van_ban', 'van_ban': chu})
    q.cap(v)
    c.chay(app)
    kq = c.xem(v)
    assert kq['trang_thai'] == 'XONG', kq
    ket = kq['ket_qua']['van_ban_da_che']
    assert ket['con_sot'] == [] and ket['kiem_tien_ngay']
    assert bo_an(ket['van_ban']) == ket['van_ban']
    assert chuan(ten) not in chuan(ket['van_ban'])
    for tu in ten.split():
        assert chuan(tu) not in chuan(ket['van_ban'])
    if da_duyet:
        assert ket['bi_danh'] == [{'bi_danh': '[[KH-DEMO-001]]', 'nhom': nhom, 'nguon': 'chinh_thuc'}]


@pytest.mark.parametrize('dau', ['\u200b', '\u200f', '\u2060', '\u2064', '\ufeff', '\u00ad',
                               '\u180e', '\u202e', '\u2067', '\ufe0f', '\U000e0100', '\u180f'])
@pytest.mark.parametrize('ngat', [' ', '\u00a0', '\t', '\n'])
@pytest.mark.parametrize('da_duyet', [True, False])
def test_nfd_ket_hop_khoang_trang_va_dinh_dang(dau, ngat, da_duyet):
    n, q, c, app = ghep()
    ten = 'Nguyễn Văn An'
    if da_duyet:
        DuyetDinhDanh(n, ADMIN).nhap_demo(
            [{'gia_tri': ten, 'nhom': 'CA_NHAN', 'ma_junsky': 'CN-DEMO-001'}], thuc_hien=True)
    # Chèn ngay giữa chữ và dấu tổ hợp, đồng thời đổi dấu cách của tên.
    nfd = unicodedata.normalize('NFD', ten).replace(' ', ngat)
    bien_the = dau.join(nfd)
    chu = 'Ký với ' + bien_the + '; 1.000.000 VND ngày 30/10/2026.'
    v = c.giao_viec(CHE, {'loai': 'van_ban', 'van_ban': chu}); q.cap(v); c.chay(app)
    kq = c.xem(v)
    assert kq['trang_thai'] == 'XONG', kq
    ra = kq['ket_qua']['van_ban_da_che']['van_ban']
    assert bo_an(ra) == ra and 'nguyễn' not in chuan(ra)
    assert '1.000.000 VND' in ra and '30/10/2026' in ra


@pytest.mark.parametrize('nhan,so', [('MST', '0312345678'), ('STK', '0012345678901')])
@pytest.mark.parametrize('dau', ['\u200b', '\u2063', '\ufe0f', '\U000e0100'])
def test_mst_stk_co_zero_width_giua_chu_so(nhan, so, dau):
    n, q, c, app = ghep()
    chu = nhan + ': ' + dau.join(so) + '; 1.000.000 VND; 30/10/2026.'
    v = c.giao_viec(CHE, {'loai': 'van_ban', 'van_ban': chu}); q.cap(v); c.chay(app)
    kq = c.xem(v)
    assert kq['trang_thai'] == 'XONG', kq
    ra = kq['ket_qua']['van_ban_da_che']['van_ban']
    assert bo_an(ra) == ra and so not in bo_an(ra)
    assert '1.000.000 VND' in ra and '30/10/2026' in ra


def test_moi_cf_va_selector_deu_bi_bo_va_bi_chan_o_phong_bi():
    cac_cf = [chr(i) for i in range(sys.maxunicode + 1) if unicodedata.category(chr(i)) == 'Cf']
    selector = [chr(i) for a, b in [(0xFE00, 0xFE0F), (0xE0100, 0xE01EF), (0x180B, 0x180D), (0x180F, 0x180F)]
                for i in range(a, b + 1)]
    for dau in cac_cf + selector:
        chu = 'Tr' + dau + unicodedata.normalize('NFD', 'ần') + ' Bảo Long'
        ban_do, vi_tri = chuan_hoa_vi_tri(chu)
        assert ban_do == 'Trần Bảo Long'
        assert chu[vi_tri[0][0]:vi_tri[-1][1]] == chu
        with pytest.raises(LoiNghiepVu) as e:
            phong_bi.kiem_van_ban(chu)
        assert e.value.ma == 'MASK_DAU_VAO'
        dau_ra = {'loai': 'van_ban_da_che', 'van_ban_da_che': {
            'phien_ban': 1, 'van_ban': chu, 'ma_yeu_cau': 'DEMO',
            'con_sot': [], 'kiem_tien_ngay': True, 'chuyen_tiep': {}}}
        with pytest.raises(LoiNghiepVu):
            phong_bi.kiem_loai(dau_ra, 'van_ban_da_che')


def test_anh_xa_ve_nguyen_van_va_bo_cf_ngoai_ten():
    ten = 'Trần Bảo Long'
    cum = '\u2060'.join(unicodedata.normalize('NFD', ten))
    chu = '\ufeffKý với ' + cum + '; DEMO\u200f.'
    a, b = core.KnownText(chu).spans(ten)[0]
    assert chu[a:b] == cum
    assert core.KnownText(chu).spans(ten) == [(len('\ufeffKý với '), len('\ufeffKý với ') + len(cum))]


@pytest.mark.parametrize('tien_to', ['MASKTAM', 'MASKCN'])
def test_alias_tam_cua_b_la_alias_la_o_a_khong_them_tham_chieu(tien_to):
    n, q, c, app = ghep()
    _, a, _ = che_demo(n, q, c, app)
    _, b, ket_b = che_demo(n, q, c, app)
    assert ket_b['cho_duyet']['so_cum_vua_them'] == 0
    assert n.tim('cho_duyet').danh_sach[0].gia_tri['so_lan_gap'] == 2
    alias = ket_b['bi_danh'][0]['bi_danh']
    if tien_to == 'MASKCN':
        # Một alias chưa duyệt mang tiền tố khác MASKTAM vẫn là tạm.
        alias = '[[MASKCN-DEMO-CHUA-DUYET]]'
        with n.lo() as lo:
            lo.them('bi_danh_tam', khoa_muc('DEMO', alias.lower()),
                    {'gia_tri': TEN, 'nhom': 'CONG_TY', 'bi_danh': alias, 'nguon': 'tam'})
            lo.them('dau_gap', khoa_muc('DEMO', khoa_dau('tham_chieu', b.ma_yeu_cau, alias.lower())),
                    {'loai_dau': 'tham_chieu', 'ma_yeu_cau': b.ma_yeu_cau, 'bi_danh': alias.lower()})
    _, kq = mo_demo(n, q, c, app, 'DEMO: ' + alias, a.ma_yeu_cau, dong=True)
    assert kq['trang_thai'] == 'XONG', kq
    ra = kq['ket_qua']['truong']
    assert ra['van_ban_da_mo_che'] == 'DEMO: ' + alias
    assert ra['so_cho_mo'] == 0 and not ra['mo_day_du']
    assert ra['trang_thai_ma_yeu_cau'] == 'DANG_XU_LY'
    la = json.loads(ra['bi_danh_khong_ro_json'])
    assert la[0]['bi_danh'] == alias and la[0]['vi_tri']['bat_dau'] == 6
    refs = [m.gia_tri for m in n.tim('dau_gap').danh_sach if m.gia_tri.get('loai_dau') == 'tham_chieu']
    assert not any(m['ma_yeu_cau'] == a.ma_yeu_cau and m['bi_danh'] == alias.lower() for m in refs)
    _, mo_b = mo_demo(n, q, c, app, alias, b.ma_yeu_cau)
    assert mo_b['ket_qua']['truong']['van_ban_da_mo_che'] == TEN


def test_ghi_alias_tam_ngoai_yeu_cau_bi_tu_choi():
    n, q, c, app = ghep()
    _, a, _ = che_demo(n, q, c, app)
    _, _, b = che_demo(n, q, c, app)
    v = viec_demo('ghi-ngoai-demo'); q.cap(v.id, loai='mo_che', ma_yeu_cau=a.ma_yeu_cau)
    kho = KhoDinhDanh(ngan=n, quyen=q).mo_luot(v, loai='mo_che', ma_yeu_cau=a.ma_yeu_cau)
    with pytest.raises(LoiNghiepVu):
        with kho.giao_dich():
            kho.ghi_bi_danh_da_dung(a.ma_yeu_cau, [b['bi_danh'][0]['bi_danh']])


def test_sau_duyet_ma_tam_van_chi_mo_cho_yeu_cau_goc():
    n, q, c, app = ghep()
    _, a, ket_a = che_demo(n, q, c, app)
    _, b, ket_b = che_demo(n, q, c, app)
    admin = DuyetDinhDanh(n, ADMIN)
    muc = admin.danh_sach()[0]
    chinh_thuc = admin.duyet(muc['gia_tri']['khoa'], muc['row_version'], ma_junsky='KH-DEMO-001')
    alias_a = ket_a['bi_danh'][0]['bi_danh']
    alias_b = ket_b['bi_danh'][0]['bi_danh']
    _, mo_a = mo_demo(n, q, c, app, alias_b, a.ma_yeu_cau)
    assert not mo_a['ket_qua']['truong']['mo_day_du']
    assert mo_a['ket_qua']['truong']['van_ban_da_mo_che'] == alias_b
    _, mo_b = mo_demo(n, q, c, app, alias_b, b.ma_yeu_cau)
    assert mo_b['ket_qua']['truong']['van_ban_da_mo_che'] == TEN
    _, mo_b_sai = mo_demo(n, q, c, app, alias_a, b.ma_yeu_cau)
    assert not mo_b_sai['ket_qua']['truong']['mo_day_du']
    _, moi, ket_moi = che_demo(n, q, c, app)
    assert ket_moi['van_ban'].startswith(chinh_thuc)
    _, mo_moi = mo_demo(n, q, c, app, alias_a, moi.ma_yeu_cau)
    assert not mo_moi['ket_qua']['truong']['mo_day_du']


def test_chinh_thuc_mo_duoc_trong_cung_phap_nhan_ke_ca_chua_dung():
    n, q, c, app = ghep()
    _, a, _ = che_demo(n, q, c, app)
    DuyetDinhDanh(n, ADMIN).nhap_demo([
        {'gia_tri': 'Vinamilk Holdings', 'nhom': 'CONG_TY', 'ma_junsky': 'KH-DEMO-CHINH-THUC'}], thuc_hien=True)
    _, kq = mo_demo(n, q, c, app, '[[kh-demo-chinh-thuc]]', a.ma_yeu_cau)
    assert kq['ket_qua']['truong']['van_ban_da_mo_che'] == 'Vinamilk Holdings'
    assert kq['ket_qua']['truong']['mo_day_du']


@pytest.mark.parametrize('buoc', ['doc', 'tim', 'lo'])
@pytest.mark.parametrize('nang_luc', [CHE, MO])
@pytest.mark.parametrize('loai_loi', ['runtime', 'nghiep_vu'])
def test_loi_la_tu_ngan_khong_lo_ra_stdout_stderr(monkeypatch, capfd, buoc, nang_luc, loai_loi):
    n, q, c, app = ghep()
    _, ctx, ket = che_demo(n, q, c, app)
    def nem(*args, **kw):
        if loai_loi == 'nghiep_vu':
            raise LoiNghiepVu('MA_NGAN_LA', TEN + ' Nguyễn Văn An Vinamilk Holdings')
        raise RuntimeError(TEN + ' Nguyễn Văn An Vinamilk Holdings')
    monkeypatch.setattr(n, buoc, nem)
    dau = ({'loai': 'van_ban', 'van_ban': VAN_BAN} if nang_luc == CHE else
           {'loai': 'tra_loi_ai', 'tra_loi_ai': ai_demo(ket['van_ban'], ctx.ma_yeu_cau)})
    v = c.giao_viec(nang_luc, dau); q.cap(v, loai='che' if nang_luc == CHE else 'mo_che', ma_yeu_cau=ctx.ma_yeu_cau)
    c.chay(app)
    kq = c.xem(v)
    assert kq['trang_thai'] == 'LOI' and kq['loi']['ma'] == 'MASK_KHO_LOI'
    assert all(ten not in kq['loi']['thong_diep'] for ten in (TEN, 'Nguyễn Văn An', 'Vinamilk Holdings'))
    bat = capfd.readouterr()
    assert all(ten not in bat.out + bat.err for ten in (TEN, 'Nguyễn Văn An', 'Vinamilk Holdings'))
    assert 'Traceback' not in bat.err


def test_che_mo_duyet_va_loi_duyet_khong_in_ten(monkeypatch, capsys):
    n, q, c, app = ghep()
    _, ctx, ket = che_demo(n, q, c, app)
    mo_demo(n, q, c, app, ket['van_ban'], ctx.ma_yeu_cau)
    admin = DuyetDinhDanh(n, ADMIN)
    muc = admin.danh_sach()[0]
    admin.duyet(muc['gia_tri']['khoa'], muc['row_version'])
    v = c.giao_viec(CHE, {'loai': 'van_ban', 'van_ban': 'Nguyễn Văn An'}); q.cap(v); c.chay(app)
    muc = admin.danh_sach()[0]
    def nem(*args, **kwargs):
        raise RuntimeError(TEN)
    monkeypatch.setattr(n, 'lo', nem)
    with pytest.raises(LoiNghiepVu) as e:
        admin.duyet(muc['gia_tri']['khoa'], muc['row_version'])
    assert e.value.ma == 'MASK_KHO_LOI' and e.value.__suppress_context__
    assert TEN not in ''.join(traceback.format_exception(e.value))
    bat = capsys.readouterr()
    assert all(ten not in bat.out + bat.err for ten in (TEN, 'Nguyễn Văn An'))


def test_khong_anh_xa_duoc_chan_truoc_phat_hanh():
    n, q, c, app = ghep()
    chu = 'DEMO: \u1100\u200b\u1161'  # NFC ghép Jamo qua hai ký tự có combining=0.
    v = c.giao_viec(CHE, {'loai': 'van_ban', 'van_ban': chu}); q.cap(v); c.chay(app)
    kq = c.xem(v)
    assert kq['trang_thai'] == 'LOI' and kq['loi']['ma'] == 'MASK_DAU_VAO'
    assert kq['ket_qua'] is None and not n.tim('ma_yeu_cau').danh_sach


def test_cf_ngoai_dinh_danh_va_trong_tien_ngay_duoc_bo():
    n, q, c, app = ghep()
    chu = '\ufeffDEMO\u200f: 1.00\u20600.000 VND ngày 30/10/20\u200d26.\U000e0100'
    v = c.giao_viec(CHE, {'loai': 'van_ban', 'van_ban': chu}); q.cap(v); c.chay(app)
    kq = c.xem(v)
    assert kq['trang_thai'] == 'XONG', kq
    assert kq['ket_qua']['van_ban_da_che']['van_ban'] == 'DEMO: 1.000.000 VND ngày 30/10/2026.'


@pytest.mark.parametrize('thao_tac', ['snapshot_luot', 'chot_luot'])
def test_port_loi_la_chi_tra_loi_co_dinh_khong_in_ten(tmp_path, capfd, thao_tac):
    from test_mask_3 import ghep as ghep_port, xu_ly_demo
    core_gia, q, v, _, lop = ghep_port(tmp_path)
    goi_goc = lop._goi_kho
    def port(goi, **kwargs):
        if goi == thao_tac:
            raise RuntimeError(TEN)
        return goi_goc(goi, **kwargs)
    lop._goi_kho = port
    with pytest.raises(LoiNghiepVu) as e:
        lop.xu_ly(v, xu_ly_demo)
    assert e.value.ma == 'MASK_KHO_LOI' and e.value.__suppress_context__
    assert TEN not in ''.join(traceback.format_exception(e.value))
    bat = capfd.readouterr()
    assert TEN not in bat.out + bat.err


@pytest.mark.parametrize('ma', ['KTT_ENGINE_DU_LIEU', 'PROGRAMDATA'])
def test_kiem_doc_lap_bat_ma_doc_cau_hinh_may(tmp_path, ma):
    from kiem_doc_lap import kiem_tra
    (tmp_path / 'demo.py').write_text('import os\nGIA_TRI = os.environ.get(' + repr(ma) + ')\n', encoding='utf-8')
    assert any('lưu dữ liệu máy' in m for m in kiem_tra(tmp_path))
