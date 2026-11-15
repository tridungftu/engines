"""MASK-2b: dữ liệu giả DEMO, không tên/hồ sơ vận hành hoặc gọi Cloud."""
import json
import unicodedata

import pytest
from kho_tri_thuc_sdk.thu import CoreGia

from e_mask import che_van_ban as x, tai_nguyen, ten_nguoi
from e_mask.chay import tao_app
from e_mask.duyet_dinh_danh import DuyetDinhDanh
from e_mask.kho_ngan import KHAI_NGAN
from e_mask.ngan import NganBoNho
from ho_tro_kho_demo import KhoBoNho
from ho_tro_ngan import ADMIN, QuyenNganDemo
from do_mask_2b import CAU_KHONG_TEN, CA_TEN, do, mau_cu


@pytest.fixture(autouse=True)
def tu_dien_sach():
    tai_nguyen.xoa_cache()
    tai_nguyen.nap_tu_goi()
    yield
    tai_nguyen.xoa_cache()


def bo_dau(chu):
    # Đáp án kiểm dùng phép bỏ dấu riêng, không gọi helper của runtime.
    return ''.join(c for c in unicodedata.normalize('NFD', chu.casefold().replace('đ', 'd'))
                   if not unicodedata.combining(c))


def bien_the(chu, dang):
    if dang == 'khong_dau':
        return bo_dau(chu)
    if dang == 'hoa':
        return chu.upper()
    if dang == 'dong':
        return chu.replace(' ', '\n')
    if dang == 'nfd_cf':
        return '\u200b'.join(unicodedata.normalize('NFD', chu))
    if dang == 'tab_nbsp':
        return chu.replace(' ', '\t\u00a0')
    return chu


@pytest.mark.parametrize('chu', CA_TEN)
@pytest.mark.parametrize('dang', ['goc', 'khong_dau', 'hoa', 'dong', 'nfd_cf', 'tab_nbsp'])
def test_bon_ca_lead_khong_duoc_lot(chu, dang):
    chu = bien_the(chu, dang)
    kq = x.che(chu, [], KhoBoNho())
    if kq['gui_duoc']:
        assert kq['so_cho_thay'] >= 1
        assert kq['con_sot'] == []
        for ten in ('nguyen van an', 'tran bao long', 'le thi hoa'):
            assert ten not in ' '.join(bo_dau(kq['van_ban_da_che']).split())
    else:
        assert kq['van_ban_da_che'] is None
        assert kq['con_sot']


@pytest.mark.parametrize('chu', [CA_TEN[0], CA_TEN[3],
                                'nguyễn văn an và trần bảo long',
                                'lê thị hoa (kế toán)', 'gửi nguyễn an'])
def test_nghi_ngo_chi_con_vi_tri_khong_phat_hanh(chu):
    kq = x.che(chu, [], KhoBoNho())
    assert not kq['gui_duoc'] and kq['van_ban_da_che'] is None
    muc = next(m for m in kq['con_sot'] if m.get('ly_do') == 'nghi tên người viết thường')
    assert muc['nhom'] == 'CA_NHAN'
    assert 'nguyen' in bo_dau(chu) or 'le thi hoa' in bo_dau(chu)
    assert 0 <= muc['vi_tri']['bat_dau'] < muc['vi_tri']['ket_thuc'] <= len(chu)
    for khoa in ('gia_tri', 'cum', 'ten'):
        assert khoa not in muc


@pytest.mark.parametrize('danh_xung', ['ông', 'bà', 'anh', 'chị', 'em', 'cô', 'chú', 'bác',
                                      'mr', 'mrs', 'ms', 'MR.'])
def test_danh_xung_che_va_mo_bang_bi_danh_tam(danh_xung):
    kho = KhoBoNho()
    chu = danh_xung + ' tran bao long đã ký; 1.000.000 VND; 30/10/2026.'
    kq = x.che(chu, [], kho)
    assert kq['gui_duoc'] and kq['kiem_tien_ngay']
    assert kq['so_cho_thay'] == 1 and kq['cho_duyet']['so_cum_vua_them'] == 1
    assert 'tran bao long' not in json.dumps(kq, ensure_ascii=False)
    assert kq['bi_danh'][0]['nhom'] == 'CA_NHAN'
    mo = x.mo_che(kq['van_ban_da_che'], kq['ma_yeu_cau'], kho)
    assert mo['mo_day_du'] and mo['van_ban_da_mo_che'] == chu


@pytest.mark.parametrize('ten', ['Lê An', 'Nguyễn Văn An', 'Trần Thị Minh Hoa',
                                'Nguyễn Văn Thanh', 'Nguyễn Văn Trọng', 'Nguyễn Đăng Khoa'])
def test_hai_ba_bon_am_tiet_co_danh_xung(ten):
    chu = 'chị ' + ten.lower() + ' (kế toán)'
    kq = x.che(chu, [], KhoBoNho())
    assert kq['gui_duoc'] and kq['so_cho_thay'] == 1
    assert ten.lower() not in kq['van_ban_da_che']
    assert kq['van_ban_da_che'].endswith(' (kế toán)')


@pytest.mark.parametrize('dang', ['goc', 'khong_dau', 'hoa', 'dong', 'nfd_cf'])
def test_ten_da_duyet_khop_bo_dau_giu_nguyen_bi_danh(dang):
    kho = KhoBoNho([{'gia_tri': 'Nguyễn Văn An', 'nhom': 'CA_NHAN', 'ma_junsky': 'CN-DEMO-001'}])
    chu = 'gửi ' + bien_the('nguyễn văn an', dang)
    kq = x.che(chu, [], kho)
    assert kq['gui_duoc'] and kq['van_ban_da_che'] == 'gửi [[CN-DEMO-001]]'
    assert kq['cho_duyet']['so_cum_vua_them'] == 0
    assert kq['bi_danh'][0]['nguon'] == 'chinh_thuc'


def test_khac_dau_thanh_cung_ten_da_duyet():
    kho = KhoBoNho([{'gia_tri': 'Nguyễn Văn An', 'nhom': 'CA_NHAN', 'ma_junsky': 'CN-DEMO-001'}])
    kq = x.che('gửi nguyện ván án', [], kho)
    assert kq['gui_duoc'] and kq['van_ban_da_che'] == 'gửi [[CN-DEMO-001]]'


def test_hai_ten_da_duyet_trung_sau_bo_dau_phai_chan():
    kho = KhoBoNho([{'gia_tri': ten, 'nhom': 'CA_NHAN'}
                    for ten in ['Nguyễn Văn An', 'Nguyễn Vân An']])
    kq = x.che('gửi nguyen van an', [], kho)
    assert not kq['gui_duoc'] and kq['van_ban_da_che'] is None


def test_khong_nang_tin_cay_moi_lan_gap_cung_ten():
    kq = x.che('anh tran bao long đã ký; gửi tran bao long', [], KhoBoNho())
    assert kq['so_cho_thay'] == 1
    assert not kq['gui_duoc'] and kq['van_ban_da_che'] is None


def test_bi_danh_tam_khong_bien_thanh_ten_da_duyet():
    kho = KhoBoNho()
    assert x.che('anh tran bao long đã ký', [], kho)['gui_duoc']
    kq = x.che('gửi tran bao long', [], kho)
    assert not kq['gui_duoc'] and kq['van_ban_da_che'] is None


def test_nul_do_caller_chen_khong_duoc_bo_kiem_nhan(monkeypatch):
    monkeypatch.setattr(x, '_phat_hien', lambda _: ([], True))
    con, het = x._kiem_con_sot('Ông: \x00tên demo lạ', [])
    assert het and any(m['nhom'] == 'CA_NHAN' for m in con)


def test_khong_che_prefix_da_duyet_roi_lot_duoi():
    kho = KhoBoNho([{'gia_tri': 'Nguyễn Văn', 'nhom': 'CA_NHAN'}])
    kq = x.che('gửi nguyễn văn an', [], kho)
    assert not kq['gui_duoc'] and kq['van_ban_da_che'] is None


def test_ten_qua_dai_khong_duoc_cat_ngam():
    kq = x.che('anh nguyễn văn bảo minh long', [], KhoBoNho())
    assert not kq['gui_duoc'] and kq['van_ban_da_che'] is None


@pytest.mark.parametrize('chu', ['anh hồ sơ văn bảo long', 'chu trần bảo long'])
def test_ngoai_le_khong_duoc_an_ten_co_danh_xung_hoac_ho_mo_ho(chu):
    kq = x.che(chu, [], KhoBoNho())
    assert not kq['gui_duoc'] and kq['van_ban_da_che'] is None


def test_hau_kiem_doc_lap_detector_cu_va_vi_tri_nfd_cf(monkeypatch):
    monkeypatch.setattr(x, '_phat_hien', lambda _: ([], True))
    chu = 'gửi\n' + '\u200f'.join(unicodedata.normalize('NFD', 'nguyễn văn an'))
    con, het = x._kiem_con_sot(chu, [])
    assert het
    muc = next(m for m in con if m.get('ly_do') == 'nghi tên người viết thường')
    a, b = muc['vi_tri']['bat_dau'], muc['vi_tri']['ket_thuc']
    assert a == 4 and b == len(chu)
    assert muc['vi_tri']['dong'] == 2 and muc['vi_tri']['cot'] == 1
    kq = x.che(chu, [], KhoBoNho())
    assert not kq['gui_duoc']


def test_loi_bo_do_moi_khong_duoc_thanh_cong_gia(monkeypatch):
    def hong(*args):
        raise RuntimeError('DEMO lỗi có thể chứa nội dung riêng')
    monkeypatch.setattr(ten_nguoi, 'tim', hong)
    with pytest.raises(x.LoiCheVanBan, match='Không thể che văn bản an toàn') as loi:
        x.che('nội dung DEMO', [], KhoBoNho())
    assert 'nội dung riêng' not in str(loi.value)


# Mẫu 15 vốn bị lớp số/ngày cũ chặn; vẫn đo đủ 30 mẫu trong báo cáo,
# không sửa bộ tiền/ngày ở lát tên người. 29 câu còn lại phải không bị chặn.
@pytest.mark.parametrize('chu', [s for i, s in enumerate(CAU_KHONG_TEN, 1) if i != 15])
def test_cau_nghiep_vu_khong_ten_khong_bi_chan(chu):
    kq = x.che(chu, [], KhoBoNho())
    assert kq['gui_duoc'] and kq['con_sot'] == []


@pytest.mark.parametrize('chu', ['hà nội', 'ha noi', 'HÀ NỘI', 'lê thê', 'le the',
                                'LÊ THÊ', 'cao hơn', 'lý do', 'tăng doanh thu'])
def test_cum_trung_ho_duoc_loai_bang_ca_cum(chu):
    assert ten_nguoi.tim(chu) == []
    assert x.che(chu, [], KhoBoNho())['gui_duoc']


def test_do_lap_lai_co_nguon_khong_bia_mau():
    assert len(list(mau_cu())) == 14
    ket = do()
    assert ket['am_tinh_co_san']['so_chan_nham'] == 0
    assert ket['am_tinh_co_san']['so_che_nham'] == 1
    assert ket['am_tinh_bo_sung']['vi_tri_chan_nham'] == [15]
    assert ket['am_tinh_bo_sung']['vi_tri_che_nham'] == [30]


@pytest.mark.parametrize('chu', CA_TEN)
def test_core_gia_chan_hoac_che_truoc_phat_hanh(chu, capsys):
    n, q, c = NganBoNho(KHAI_NGAN), QuyenNganDemo(), CoreGia()
    app = tao_app(ngan=n, quyen=q)
    v = c.giao_viec('mask.che_van_ban@1', {'loai': 'van_ban', 'van_ban': chu})
    q.cap(v)
    c.chay(app)
    kq = c.xem(v)
    if chu.startswith(('giữa', 'gửi')):
        assert kq['trang_thai'] == 'LOI'
        assert kq['loi']['ma'] == 'MASK_DINH_DANH_CHUA_DAT'
        assert kq.get('ket_qua') is None
        assert n.tim('cho_duyet').danh_sach == []
    else:
        assert kq['trang_thai'] == 'XONG', kq
        ket = kq['ket_qua']['van_ban_da_che']
        assert ket['con_sot'] == [] and ket['kiem_tien_ngay']
        assert ket['so_cho_thay'] == 1
        assert n.tim('cho_duyet').danh_sach
    log = capsys.readouterr()
    for ten in ('nguyễn văn an', 'tran bao long', 'lê thị hoa', 'nguyen van an'):
        assert ten not in (log.out + log.err + json.dumps(kq, ensure_ascii=False))


def test_core_gia_ten_da_duyet_bo_dau_giu_alias():
    n, q, c = NganBoNho(KHAI_NGAN), QuyenNganDemo(), CoreGia()
    DuyetDinhDanh(n, ADMIN).nhap_demo([{'gia_tri': 'Nguyễn Văn An', 'nhom': 'CA_NHAN',
                                     'ma_junsky': 'CN-DEMO-001'}], thuc_hien=True)
    v = c.giao_viec('mask.che_van_ban@1', {'loai': 'van_ban', 'van_ban': 'gửi nguyen van an'})
    q.cap(v)
    c.chay(tao_app(ngan=n, quyen=q))
    kq = c.xem(v)
    assert kq['trang_thai'] == 'XONG', kq
    assert kq['ket_qua']['van_ban_da_che']['van_ban'] == 'gửi [[CN-DEMO-001]]'


@pytest.mark.parametrize('cf', ['\u200b', '\u200c', '\u200d', '\u2060', '\ufeff', '\u00ad'])
@pytest.mark.parametrize('ten', ['nguyễn văn an', 'nguyen van an'])
@pytest.mark.parametrize('ranh_gioi', [0, 1])
def test_cf_thay_dau_cach_khong_lot(cf, ten, ranh_gioi):
    am = ten.split()
    am[ranh_gioi] += cf + am.pop(ranh_gioi + 1)
    chu = 'thanh toán cho ' + ' '.join(am)
    kq = x.che(chu, [], KhoBoNho())
    assert not kq['gui_duoc'] or (kq['so_cho_thay'] and bo_dau(ten).replace(' ', '') not in bo_dau(kq['van_ban_da_che']).replace(' ', ''))
    assert kq['van_ban_da_che'] is None or cf not in kq['van_ban_da_che']


@pytest.mark.xfail(strict=True, reason="giới hạn quy tắc, nợ CAO")
@pytest.mark.parametrize('chu', ['mạc đĩnh chi', 'lương thế vinh', 'từ minh tâm',
                                  'phụ trách hạng mục: văn tiến dũng'])
def test_held_out_ten_khong_lot(chu):
    kq = x.che(chu, [], KhoBoNho())
    assert not kq['gui_duoc'] or kq['so_cho_thay'] > 0
