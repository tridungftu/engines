"""MASK-2c-1: chỉ DEMO; quan hệ khoảng, snapshot/ACL bằng CoreGia."""
from dataclasses import FrozenInstanceError, replace
import json
from pathlib import Path
from types import SimpleNamespace
import unicodedata

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, ViecDaHuy
from kho_tri_thuc_sdk.thu import CoreGia

from e_mask import che_van_ban as x, tai_nguyen
from e_mask.anh_xa_ai import LoiAnhXa, PhepSua, bam_chu, kiem_anh_xa, tao_anh_xa
from e_mask.chay import tao_app
from e_mask.ho_so_ai import (DoanAI, HoSoAI, KHAI_NGAN_HO_SO_AI,
                             KhoHoSoAI, bam_bytes, doc_bytes, json_chuan)
from e_mask.kho_ngan import KHAI_NGAN
from e_mask.ngan import NganBoNho, NganXungDot
from ho_tro_ho_so_ai import CongHoSoCoreGiaDemo
from ho_tro_kho_demo import KhoBoNho
from ho_tro_ngan import QuyenNganDemo, viec_demo

TEN = 'Nguyễn Văn An'
DUOI = '; 1.000.000 VND; 30/10/2026; nội dung DEMO.'


@pytest.fixture(autouse=True)
def tu_dien():
    tai_nguyen.xoa_cache()
    tai_nguyen.nap_tu_goi()
    yield
    tai_nguyen.xoa_cache()


def ho_so(m, ke_hoach=None):
    if ke_hoach is None:
        ke_hoach = (DoanAI(0, 0, len(m.goc), 0, len(m.goc), bam_chu(m.goc)),)
    return HoSoAI(m, ke_hoach, 'e_mask 1.0.0')


def bo_kho():
    viec, quyen = viec_demo(), QuyenNganDemo()
    ctx = quyen.cap(viec.id)
    cong = CongHoSoCoreGiaDemo()
    cong.cap(viec, ctx)
    ngan = NganBoNho(KHAI_NGAN_HO_SO_AI)
    kho = KhoHoSoAI(ngan=ngan, quyen=quyen, cong=cong)
    return SimpleNamespace(viec=viec, q=quyen, ctx=ctx, cong=cong, n=ngan, kho=kho)


def mau():
    goc = 'DEMO: ' + TEN + DUOI
    return ho_so(tao_anh_xa(goc, [(6, 6 + len(TEN), '[[CN-DEMO-01]]')]))


@pytest.mark.parametrize('dang', ['NFC', 'NFD'])
@pytest.mark.parametrize('ngat', [' ', '\t', '\u00a0', '\n', '\u200b'])
@pytest.mark.parametrize('vo_hinh', ['', '\u200f', '\ufe0f', '\U000e0100'])
def test_quan_he_nfd_cf_selector_tab_nbsp(dang, ngat, vo_hinh):
    ten = unicodedata.normalize(dang, TEN.replace(' ', ngat))
    if vo_hinh:
        ten = vo_hinh.join(ten)
    goc = 'DEMO: ' + ten + unicodedata.normalize(dang, DUOI)
    a, b = 6, 6 + len(ten)
    m = tao_anh_xa(goc, [(a, b, '[[CN-DEMO-001]]')])
    kiem_anh_xa(m)
    assert m.goc == goc
    assert m.ban_do == unicodedata.normalize('NFC', ''.join(
        c for c in goc if unicodedata.category(c) != 'Cf'
        and not 0xFE00 <= ord(c) <= 0xFE0F and not 0xE0100 <= ord(c) <= 0xE01EF))
    assert m.da_che == 'DEMO: [[CN-DEMO-001]]' + unicodedata.normalize(dang, DUOI)
    assert m.da_che_tron(a, b) and not m.da_che_tron(a - 1, b)
    assert m.chuyen('da_che', 'goc', 7, 9) == ((a, b),)
    assert m.chuyen('goc', 'da_che', a, b) == ((6, 6 + len('[[CN-DEMO-001]]')),)
    do = m.chuyen('goc', 'ban_do', a, b)
    assert do and m.chuyen('ban_do', 'goc', *do[0]) == ((a, b),)
    # Số tiền, ngày và chữ không normalize trong bản che: round-trip chính xác.
    for chu in ('DEMO:', '1.000.000 VND', '30/10/2026'):
        dau = goc.index(chu)
        for dich in ('ban_do', 'da_che'):
            k = m.chuyen('goc', dich, dau, dau + len(chu))
            assert len(k) == 1
            assert m.chuyen(dich, 'goc', *k[0]) == ((dau, dau + len(chu)),)


def test_nfd_la_quan_he_khong_phai_song_anh():
    m = tao_anh_xa('DEMO: a\u0306\u0301; z', [])
    assert m.ban_do == 'DEMO: ắ; z' and m.da_che == m.goc
    assert m.chuyen('goc', 'ban_do', 7, 8) == ((6, 7),)
    assert m.chuyen('ban_do', 'goc', 6, 7) == ((6, 9),)
    assert m.chuyen('ban_do', 'da_che', 6, 7) == ((6, 9),)
    with pytest.raises(LoiAnhXa):
        tao_anh_xa(m.goc, [(6, 7, '[[DEMO]]')])


def test_cf_bi_bo_co_diem_neo_khong_coi_la_alias():
    m = tao_anh_xa('DEMO\u200b\ufe0f giữ nguyên', [])
    assert m.goc_che[1] == PhepSua((4, 6), (4, 4), 'bo_vo_hinh')
    assert m.chuyen('goc', 'da_che', 4, 6) == ((4, 4),)
    assert m.chuyen('da_che', 'goc', 4, 4) == ((4, 6),)
    assert not m.da_che_tron(4, 6)


@pytest.mark.parametrize('alias', ['[[A]]', '[[CN-DEMO-' + 'X' * 80 + ']]'])
def test_alias_dai_ngan_va_tung_lan_ten_lap(alias):
    goc = TEN + '; ' + TEN + DUOI
    a = len(TEN) + 2
    m = tao_anh_xa(goc, [(0, len(TEN), alias), (a, a + len(TEN), alias)])
    assert m.da_che == alias + '; ' + alias + DUOI
    for p in (p for p in m.goc_che if p.loai == 'thay_bi_danh'):
        assert m.chuyen('da_che', 'goc', *p.dich) == (p.goc,)
    assert not m.da_che_tron(0, a + len(TEN))
    assert m.da_che_tron(a, a + len(TEN))


def test_phan_giu_nguyen_unicode_ke_ca_dau_nfd_va_ngoai_bmp():
    chu = '😀; ' + unicodedata.normalize('NFD', 'nội dung')
    m = tao_anh_xa(chu, [])
    for i in range(len(chu)):
        k = m.chuyen('goc', 'da_che', i, i + 1)
        assert k == ((i, i + 1),)
        assert m.chuyen('da_che', 'goc', *k[0]) == ((i, i + 1),)
    assert m.he_offset == 'unicode_code_point'


def test_chon_ten_dai_chong_prefix_map_dung_span_thuc_te():
    ten = 'Công ty DEMO Ánh Dương'
    kho = KhoBoNho([{'gia_tri': ten, 'nhom': 'CONG_TY', 'ma_junsky': 'CT-DEMO-DAY-DU'},
                   {'gia_tri': 'Công ty DEMO Ánh', 'nhom': 'CONG_TY', 'ma_junsky': 'CT-DEMO-NGAN'}])
    kq, m = x.che_co_anh_xa(ten + '; 1.000.000 VND; 30/10/2026.', [], kho)
    assert kq['so_cho_thay'] == 1 and m.da_che.startswith('[[CT-DEMO-DAY-DU]]')
    p = next(p for p in m.goc_che if p.loai == 'thay_bi_danh')
    assert p.goc == (0, len(ten)) and m.da_che_tron(0, len(ten))


def test_prefix_va_chong_khong_duoc_nang_thanh_che_du():
    m = tao_anh_xa('Nguyễn Văn An', [(0, 6, '[[DEMO]]')])
    assert not m.da_che_tron(0, len(m.goc))
    assert m.da_che_tron(0, 6)
    with pytest.raises(LoiAnhXa):
        tao_anh_xa(m.goc, [(0, 6, '[[A]]'), (4, 10, '[[B]]')])
    with pytest.raises(x.LoiCheVanBan):
        x.che_co_anh_xa('gửi nguyễn văn an', [], KhoBoNho([
            {'gia_tri': 'Nguyễn Văn', 'nhom': 'CA_NHAN'}]))


def test_lop1_map_lay_dung_vung_da_chon_khong_ro_ra_ket_qua():
    chu = 'anh tran bao long đã ký; anh tran bao long; 1.000.000 VND; 30/10/2026.'
    kq, m = x.che_co_anh_xa(chu, [], KhoBoNho())
    assert kq['gui_duoc'] and kq['so_cho_thay'] == 2
    assert len([p for p in m.goc_che if p.loai == 'thay_bi_danh']) == 2
    assert m.da_che == kq['van_ban_da_che']
    assert set(kq) == {'ma_yeu_cau', 'van_ban_da_che', 'con_sot', 'kiem_tien_ngay',
                       'gui_duoc', 'so_cho_thay', 'bi_danh', 'cho_duyet', 'canh_bao'}
    assert not any(s in json.dumps(kq, ensure_ascii=False) for s in ('anh_xa', 'ban_do', 'goc_che'))


@pytest.mark.parametrize('ngat', [' ', '\t', '\u00a0', '\n'])
@pytest.mark.parametrize('chen', ['\u200b', '\ufe0f', '\U000e0100'])
def test_map_lop1_bao_du_ten_nfd_cf_tai_vong_thay(ngat, chen):
    ten = chen.join(unicodedata.normalize('NFD', TEN.replace(' ', ngat)))
    chu = 'gửi ' + ten + '; 1.000.000 VND; 30/10/2026.'
    kq, m = x.che_co_anh_xa(chu, [], KhoBoNho([{'gia_tri': TEN, 'nhom': 'CA_NHAN'}]))
    assert kq['gui_duoc'] and kq['so_cho_thay'] == 1
    assert m.da_che_tron(4, 4 + len(ten))
    phep = next(p for p in m.goc_che if p.loai == 'thay_bi_danh')
    assert m.chuyen('da_che', 'goc', *phep.dich) == ((4, 4 + len(ten)),)
    assert kq['kiem_tien_ngay']


@pytest.mark.parametrize('chu', ['gửi nguyễn văn an', 'gửi nguyễn\u200bvăn an',
                                'anh nguyễn văn bảo minh long'])
def test_lop1_chan_thi_khong_cap_snapshot(chu):
    with pytest.raises(x.LoiCheVanBan):
        x.che_co_anh_xa(chu, [], KhoBoNho())


def test_thieu_tai_nguyen_van_chan(monkeypatch):
    def thieu():
        raise tai_nguyen.ThieuTaiNguyen()
    monkeypatch.setattr(x.detectors, 'kiem_tai_nguyen', thieu)
    with pytest.raises(tai_nguyen.ThieuTaiNguyen):
        x.che_co_anh_xa('DEMO nội dung.', [], KhoBoNho())


@pytest.mark.parametrize('sua', ['bam_goc', 'bam_ban_do', 'bam_da_che', 'phien_ban', 'goc_che'])
def test_map_hong_khong_phat_hanh_core_gia(monkeypatch, sua, capsys):
    that = x.tao_anh_xa
    def hong(*args):
        m = that(*args)
        gia_tri = 'sha256:' + '0' * 64 if sua.startswith('bam_') else 2 if sua == 'phien_ban' else ()
        return replace(m, **{sua: gia_tri})
    monkeypatch.setattr(x, 'tao_anh_xa', hong)
    n, q, c = NganBoNho(KHAI_NGAN), QuyenNganDemo(), CoreGia()
    v = c.giao_viec('mask.che_van_ban@1', {'loai': 'van_ban', 'van_ban': 'anh tran bao long' + DUOI})
    q.cap(v)
    c.chay(tao_app(ngan=n, quyen=q))
    ket = c.xem(v)
    assert ket['trang_thai'] == 'LOI' and ket['ket_qua'] is None
    assert ket['loi']['ma'] == 'MASK_DINH_DANH_CHUA_DAT'
    assert n.tim('cho_duyet').danh_sach == []
    log = capsys.readouterr()
    assert 'tran bao long' not in log.out + log.err + json.dumps(ket, ensure_ascii=False)


def test_bien_500000_500001():
    chu = ('nội dung ' * 55556)[:500000]
    kq, m = x.che_co_anh_xa(chu, [], KhoBoNho())
    assert len(m.goc) == 500000 and m.goc == m.da_che == kq['van_ban_da_che']
    assert m.chuyen('goc', 'da_che', 499990, 500000) == ((499990, 500000),)
    with pytest.raises(x.LoiCheVanBan, match='500.000'):
        x.che_co_anh_xa(chu + '.', [], KhoBoNho())
    with pytest.raises(LoiAnhXa):
        tao_anh_xa(chu + '.', [])


@pytest.mark.parametrize('dem', ['', '  ', '\n\t\u00a0'])
def test_so_dai_phu_toan_van_van_chan_va_dung_vi_tri_nhu_matcher_cu(dem):
    so = ('1 ' * 161).rstrip()
    chu = dem + so + dem
    cu = x.core.KnownText(chu).spans(so, boundary=False)
    assert cu == [(len(dem), len(dem) + len(so))]
    kq = x.che(chu, [], KhoBoNho())
    assert not kq['gui_duoc'] and kq['van_ban_da_che'] is None
    assert kq['so_cho_thay'] == 0 and kq['kiem_tien_ngay']
    vung = [m['vi_tri'] for m in kq['con_sot'] if m.get('nhom') == 'TAI_KHOAN']
    assert [(v['bat_dau'], v['ket_thuc']) for v in vung] == cu


def test_snapshot_bat_bien_va_round_trip_bytes():
    h = mau()
    assert doc_bytes(h.thanh_bytes()) == h
    assert h.anh_xa.goc not in repr(h) + repr(h.anh_xa)
    with pytest.raises(FrozenInstanceError):
        h.anh_xa.goc = 'DEMO khác'
    with pytest.raises(FrozenInstanceError):
        h.ke_hoach[0].ket_thuc = 0
    with pytest.raises(TypeError):
        h.ke_hoach[0] = h.ke_hoach[0]


@pytest.mark.parametrize('sua', ['hash', 'map', 'list', 'version', 'unicode', 'offset'])
def test_snapshot_hong_bam_map_phien_ban_khong_luu(sua):
    h = mau()
    m = h.anh_xa
    moi = {'hash': replace(m, bam_da_che='sha256:' + '0' * 64),
           'map': replace(m, goc_che=m.goc_che[1:]),
           'list': replace(m, goc_che=list(m.goc_che)),
           'version': replace(m, phien_ban=True),
           'unicode': replace(m, phien_ban_unicode='DEMO'),
           'offset': replace(m, he_offset='utf16')}[sua]
    b = bo_kho()
    with pytest.raises(LoiNghiepVu):
        b.kho.luu(b.viec, b.ctx.ma_yeu_cau, replace(h, anh_xa=moi))
    assert b.cong.core._tep == {} and b.n.tim('ho_so_ai').danh_sach == []


@pytest.mark.parametrize('sua', ['thieu', 'lap', 'hash', 'cat_tu', 'nfd', 'qua_8000', 'ngoai', 'mutable'])
def test_ke_hoach_doan_phai_phu_du_bam_dung_bien_an_toan(sua):
    chu = 'DEMO a\u0306\u0301n. ' + 'DEMO. ' * 1400
    m = tao_anh_xa(chu, [])
    # Biên chính và overlap đặt sau dấu cách, không cắt từ/NFD.
    bien = chu.index('DEMO. ', 5000)
    ke = (DoanAI(0, 0, bien + 6, 0, bien, bam_chu(chu[:bien + 6])),
          DoanAI(1, bien - 6, len(chu), bien, len(chu), bam_chu(chu[bien - 6:])))
    h = ho_so(m, ke)
    h.kiem()
    if sua == 'thieu':
        ke = ke[:1]
    elif sua == 'lap':
        ke = (ke[0], replace(ke[1], chi_so=0))
    elif sua == 'hash':
        ke = (replace(ke[0], bam_doan='sha256:' + '0' * 64), ke[1])
    elif sua == 'cat_tu':
        ke = (replace(ke[0], ket_thuc=4, ket_thuc_chinh=4, bam_doan=bam_chu(chu[:4])), ke[1])
    elif sua == 'nfd':
        ke = (replace(ke[0], ket_thuc=7, ket_thuc_chinh=7, bam_doan=bam_chu(chu[:7])), ke[1])
    elif sua == 'qua_8000':
        ke = (DoanAI(0, 0, len(chu), 0, len(chu), bam_chu(chu)),)
    elif sua == 'ngoai':
        ke = (ke[0], replace(ke[1], ket_thuc=len(chu) + 1))
    else:
        ke = list(ke)
    with pytest.raises(LoiNghiepVu):
        replace(h, ke_hoach=ke).thanh_bytes()


@pytest.mark.parametrize('chu,bien', [('DEMO a\u0306\u0301n. tiếp.', 8),
                                     ('DEMO tên. tiếp.', 7), ('DEMO a\u200bn. tiếp.', 7)])
def test_ke_hoach_khong_cat_giua_tu_nfd_cf_du_du_phu(chu, bien):
    # Cả hai đoạn có toàn bộ ngữ cảnh, chỉ biên vùng chính sai.
    ke = tuple(DoanAI(i, 0, len(chu), a, b, bam_chu(chu))
               for i, (a, b) in enumerate(((0, bien), (bien, len(chu)))))
    with pytest.raises(LoiNghiepVu):
        ho_so(tao_anh_xa(chu, []), ke).thanh_bytes()


def test_qua_tran_snapshot_khong_cat_ngam(monkeypatch):
    import e_mask.ho_so_ai as hs
    monkeypatch.setattr(hs, 'GIOI_HAN_HO_SO', 32)
    b = bo_kho()
    with pytest.raises(LoiNghiepVu):
        b.kho.luu(b.viec, b.ctx.ma_yeu_cau, mau())
    assert not b.cong.core._tep and not b.n.tim('ho_so_ai').danh_sach


@pytest.mark.parametrize('raw', [b'{"phien_ban":1,"phien_ban":1}', b'{"x":NaN}', b'{"x":Infinity}',
                                b'{}', b'[]', b'null', b'\xff'])
def test_json_hong_trung_khoa_hang_khong_hop_le(raw):
    with pytest.raises(LoiNghiepVu):
        doc_bytes(raw)


def test_core_gia_luu_doc_retry_chi_muc_khong_co_noi_dung(monkeypatch):
    b, h = bo_kho(), mau()
    def cam(*a, **kw):
        raise AssertionError('DEMO cấm ghi đĩa')
    monkeypatch.setattr('builtins.open', cam)
    monkeypatch.setattr(Path, 'write_bytes', cam)
    monkeypatch.setattr(Path, 'write_text', cam)
    dau = b.kho.luu(b.viec, b.ctx.ma_yeu_cau, h)
    assert b.kho.doc(b.viec, b.ctx.ma_yeu_cau, dau) == h
    assert b.kho.luu(b.viec, b.ctx.ma_yeu_cau, h) == dau
    assert len(b.cong.core._tep) == 1
    ds = b.n.tim('ho_so_ai').danh_sach
    assert len(ds) == 1
    chi = json.dumps(ds[0].gia_tri, ensure_ascii=False)
    assert TEN not in chi and h.anh_xa.goc not in chi and 'goc_che' not in chi
    assert dau.bam_ho_so == bam_bytes(b.cong.core.doc_tep(dau.ho_so.tep_id))


@pytest.mark.parametrize('loai', ['quyen', 'cong', 'tham_chieu', 'chi_muc', 'tep', 'metadata', 'bam'])
def test_thieu_quyen_tham_chieu_hash_phai_tu_choi(loai):
    b, h = bo_kho(), mau()
    dau = b.kho.luu(b.viec, b.ctx.ma_yeu_cau, h)
    if loai == 'quyen':
        b.q.thu_hoi = True
    elif loai == 'cong':
        b.kho = KhoHoSoAI(ngan=b.n, quyen=b.q)
    elif loai == 'tham_chieu':
        dau = None
    elif loai == 'chi_muc':
        b.kho = KhoHoSoAI(ngan=NganBoNho(KHAI_NGAN_HO_SO_AI), quyen=b.q, cong=b.cong)
    elif loai == 'tep':
        b.cong.core._tep.clear()
    elif loai == 'metadata':
        dau = replace(dau, ho_so=replace(dau.ho_so, kich_thuoc=dau.ho_so.kich_thuoc + 1))
    else:
        dau = replace(dau, bam_ho_so='sha256:' + '0' * 64)
    with pytest.raises(LoiNghiepVu):
        b.kho.doc(b.viec, b.ctx.ma_yeu_cau, dau)


@pytest.mark.parametrize('truong', ['module', 'nguoi_gui', 'tai_lieu', 'vung', 'phap_nhan_id'])
def test_khong_doc_cheo_chu_yeu_cau(truong):
    b = bo_kho()
    dau = b.kho.luu(b.viec, b.ctx.ma_yeu_cau, mau())
    if truong == 'phap_nhan_id':
        b.viec.ngu_canh[truong] = 'pn-demo-khac'
    else:
        setattr(b.q, truong, 'THAT' if truong == 'vung' else 'demo-khac')
    with pytest.raises(LoiNghiepVu):
        b.kho.doc(b.viec, b.ctx.ma_yeu_cau, dau)


@pytest.mark.parametrize('thieu', ['quyen', 'port', 've_core', 'ma', 'phap_nhan'])
def test_khong_co_cua_tin_cay_khong_luu(thieu):
    b = bo_kho()
    ma = b.ctx.ma_yeu_cau
    if thieu == 'quyen':
        b.kho = KhoHoSoAI(ngan=b.n, cong=b.cong)
    elif thieu == 'port':
        b.kho = KhoHoSoAI(ngan=b.n, quyen=b.q)
    elif thieu == 've_core':
        b.cong._ve.clear()
    elif thieu == 'ma':
        ma = 'DEMO-ma-khong-duoc-cap'
    else:
        b.viec.ngu_canh.pop('phap_nhan_id')
    with pytest.raises(LoiNghiepVu):
        b.kho.luu(b.viec, ma, mau())
    assert not b.cong.core._tep and not b.n.tim('ho_so_ai').danh_sach


def test_snapshot_qua_hai_buoc_core_cung_quyen():
    b = bo_kho()
    dau = b.kho.luu(b.viec, b.ctx.ma_yeu_cau, mau())
    viec2 = viec_demo('viec-demo-buoc-2')
    b.q.cap(viec2.id, ma_yeu_cau=b.ctx.ma_yeu_cau)
    assert b.kho.doc(viec2, b.ctx.ma_yeu_cau, dau) == mau()


def test_bam_bytes_sai_va_map_sai_du_co_bam_moi_khong_doc():
    b, h = bo_kho(), mau()
    dau = b.kho.luu(b.viec, b.ctx.ma_yeu_cau, h)
    ten, mime, raw = b.cong.core._tep[dau.ho_so.tep_id]
    b.cong.core._tep[dau.ho_so.tep_id] = (ten, mime, raw.replace(b'DEMO', b'FAKE', 1))
    with pytest.raises(LoiNghiepVu):
        b.kho.doc(b.viec, b.ctx.ma_yeu_cau, dau)
    v = json.loads(raw)
    v['anh_xa']['goc_che'][0]['goc'][1] += 1
    with pytest.raises(LoiNghiepVu):
        doc_bytes(json_chuan(v))


def test_khong_tai_dung_cung_ma_khi_noi_dung_doi():
    b = bo_kho()
    b.kho.luu(b.viec, b.ctx.ma_yeu_cau, mau())
    with pytest.raises(LoiNghiepVu) as loi:
        b.kho.luu(b.viec, b.ctx.ma_yeu_cau, ho_so(tao_anh_xa('DEMO khác.', [])))
    assert loi.value.ma == 'MASK_AI_XUNG_DOT' and len(b.cong.core._tep) == 1


@pytest.mark.parametrize('moc', ['luu', 'doc', 'chot'])
def test_thu_hoi_quyen_o_tung_cua_khong_phat_hanh(monkeypatch, moc):
    b = bo_kho()
    if moc == 'luu':
        that = b.cong.luu
        def thu(*args):
            ref = that(*args)
            b.q.thu_hoi = True
            return ref
        monkeypatch.setattr(b.cong, 'luu', thu)
    else:
        that = b.cong.kiem_quyen
        def kiem(viec, ctx, *, tham_chieu, thao_tac):
            if thao_tac == ('doc_ho_so_ai' if moc == 'doc' else 'chot_ho_so_ai'):
                b.cong.thu_hoi = True
            return that(viec, ctx, tham_chieu=tham_chieu, thao_tac=thao_tac)
        monkeypatch.setattr(b.cong, 'kiem_quyen', kiem)
    with pytest.raises(LoiNghiepVu):
        b.kho.luu(b.viec, b.ctx.ma_yeu_cau, mau())
    assert b.n.tim('ho_so_ai').danh_sach == []


def test_chua_ro_cas_huy_va_loi_port_khong_lo_noi_dung(monkeypatch, capsys):
    b = bo_kho()
    that = b.cong.luu
    def mat_ack(*args):
        that(*args)
        raise ChuaRo('tuong-quan-DEMO')
    monkeypatch.setattr(b.cong, 'luu', mat_ack)
    with pytest.raises(ChuaRo):
        b.kho.luu(b.viec, b.ctx.ma_yeu_cau, mau())
    assert b.n.tim('ho_so_ai').danh_sach == []
    monkeypatch.setattr(b.cong, 'luu', that)
    dau = b.kho.luu(b.viec, b.ctx.ma_yeu_cau, mau())
    assert len(b.cong.core._tep) == 1  # retry cùng mã+băm, không tạo tệp lặp
    def huy():
        raise ViecDaHuy()
    b.viec.kiem_huy = huy
    with pytest.raises(ViecDaHuy):
        b.kho.doc(b.viec, b.ctx.ma_yeu_cau, dau)
    b.viec.kiem_huy = lambda: None
    def hong(*args):
        raise RuntimeError(TEN)
    monkeypatch.setattr(b.cong, 'doc', hong)
    with pytest.raises(LoiNghiepVu) as loi:
        b.kho.doc(b.viec, b.ctx.ma_yeu_cau, dau)
    log = capsys.readouterr()
    assert TEN not in str(loi.value) + log.out + log.err


def test_xung_dot_ngan_khong_tra_tham_chieu(monkeypatch):
    b = bo_kho()
    def xung_dot():
        raise NganXungDot()
    monkeypatch.setattr(b.n, 'lo', xung_dot)
    with pytest.raises(LoiNghiepVu) as loi:
        b.kho.luu(b.viec, b.ctx.ma_yeu_cau, mau())
    assert loi.value.ma == 'MASK_AI_XUNG_DOT' and loi.value.thu_lai_duoc
    assert b.n.tim('ho_so_ai').danh_sach == []
