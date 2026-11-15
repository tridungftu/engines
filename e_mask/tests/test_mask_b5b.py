"""MASK-B5b: dữ liệu số DEMO; đã kiểm bằng Core giả (CoreGia), 0 Cloud."""
from hashlib import sha256
import json
from pathlib import Path
import unicodedata

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu

from e_mask import che_van_ban as che, tai_nguyen, tep_word as tw
from e_mask.doc_word import doc_word
from ho_tro_kho_demo import KhoBoNho
from ho_tro_mask_b5 import bo, word


CA_LOT = [
    ('Số tài khoản: ', '1234-56-78'),
    ('Số tài khoản: ', '12-34-5678'),
    ('Số tài khoản: ', '0123/45/67'),
    ('Số CCCD: ', '12/34/5678'),
    ('Số CCCD: ', '1234.56.78'),
    ('Số hộ chiếu: ', '1234-12-30'),
]
NHAN = [
    'Số tài khoản: ', 'SO TAI KHOAN ', 'số TÀI KHOẢN ', 'STK: ', 'stk ', 'TK ',
    'account no.: ', 'ACC ', 'Số thẻ: ', 'the so ', 'MSDN: ',
    'tài khoản số ', 'tai khoan so: ', 'CCCD: ', 'cccd ', 'CMND ', 'CMT: ',
    'căn cước ', 'CAN CUOC CONG DAN: ', 'hộ chiếu ', 'ho chieu: ', 'passport ',
    'mã số thuế: ', 'MA SO THUE ', 'MST ', 'giấy phép: ', 'GIAY PHEP ', 'GPLX: ',
    'Số tài khoản (DEMO) số tham chiếu: ',
    unicodedata.normalize('NFD', 'Số tài khoản: '), 'Số tà\u200bi khoản: ',
]


@pytest.fixture(autouse=True)
def tu_dien_sach():
    tai_nguyen.xoa_cache()
    tai_nguyen.nap_tu_goi()
    yield
    tai_nguyen.xoa_cache()


def _van_ban(chu):
    try:
        kq = che.che(chu, [], KhoBoNho())
    except che.LoiCheVanBan as exc:
        assert str(exc) == 'Không thể che văn bản an toàn. Cần kiểm tra lại trước khi gửi.'
        return None
    return kq['van_ban_da_che']


def _word(chu):
    b = bo(seeds=())
    try:
        with b.ram.buoc(b.v) as buoc:
            tw.che_word(word(chu), buoc=buoc, dinh_danh=[])
            raw = buoc.du_lieu['tep_word']['da_che']
            # Đọc lại bytes thật, không chỉ kiểm bản preview/map.
            return '\n'.join(v.van_ban for v in doc_word(raw, kiem_huy=buoc.kiem).vung)
    except LoiNghiepVu as exc:
        assert exc.ma in {'MASK_DINH_DANH_CHUA_DAT', 'MASK_R3_CHUA_CHUNG_MINH',
                          'MASK_UNG_VIEN_CHUA_DAT'}
        assert b.ram._ban_ghi is None
        assert not b.c._tep
        return None


@pytest.mark.parametrize('xu_ly', [_van_ban, _word], ids=['van_ban', 'Word'])
@pytest.mark.parametrize('nhan,so', CA_LOT)
def test_sau_ca_lo_khong_duoc_tra_so_ro(xu_ly, nhan, so):
    chu = nhan + so
    assert not any(loai == 'ngay' for _, _, loai, _ in che._cac_tien_ngay(chu))
    kq = xu_ly(chu)
    assert kq is None or so not in kq


@pytest.mark.parametrize('xu_ly', [_van_ban, _word], ids=['van_ban', 'Word'])
@pytest.mark.parametrize('nhan', NHAN)
@pytest.mark.parametrize('so', ['2026-10-30', '30/10/2026'])
def test_nhan_dinh_danh_thang_ca_ngay_hop_lich(xu_ly, nhan, so):
    chu = nhan + so
    assert not any(loai == 'ngay' for _, _, loai, _ in che._cac_tien_ngay(chu))
    kq = xu_ly(chu)
    assert kq is None or so not in kq


@pytest.mark.parametrize('so', [
    '2026-13-01', '2026-12-32', '2026-00-10', '2026-10-00',
    '1899-12-30', '2101-12-30', '2026-02-29', '2100-02-29',
    '31/04/2026', '12-34-5678', '1234.56.78', '30/10/26',
    '31 tháng 4 năm 2026', '30 tháng 10 năm 1899',
])
def test_ngay_sai_lich_khong_duoc_mien(so):
    assert not any(loai == 'ngay' for _, _, loai, _ in che._cac_tien_ngay('ngày ' + so))


@pytest.mark.parametrize('chu,so', [
    ('Ngày ký: 2026-10-30', '2026-10-30'), ('ngày 30/10/2026', '30/10/2026'),
    ('ngày 29/02/2024', '29/02/2024'), ('ngày 1900-01-01', '1900-01-01'),
    ('ngày 2100-12-31', '2100-12-31'), ('ngày 30 tháng 10 năm 2026', 'ngày 30 tháng 10 năm 2026'),
])
def test_ngay_that_giu_nguyen_word(chu, so):
    assert any(loai == 'ngay' and gt == so for _, _, loai, gt in che._cac_tien_ngay(chu))
    kq = _word(chu)
    assert kq is not None and chu in kq


@pytest.mark.parametrize('chu', ['Ngày ký: 2026-10-30', 'ngày 30/10/2026'])
def test_ngay_that_van_ban_giu_nguyen(chu):
    kq = _van_ban(chu)
    assert kq == chu
    assert che._kiem_tien_ngay(chu, chu)
    assert not che._kiem_tien_ngay(chu, chu.replace('2026', '2027'))


@pytest.mark.parametrize('truoc', ['STK\n', 'CCCD\r\n', 'MST\u2029', 'TK' + ' ' * 121,
                                  'STK: [[MASKTK-DEMO]]; ngày ',
                                  'DEMOstk ', 'demoTK ', 'passportx '])
def test_khong_muon_nhan_ngoai_doan_cua_so_hoac_giua_tu(truoc):
    chu = truoc + '2026-10-30'
    assert che._nhan_dinh_danh_truoc(chu, len(truoc)) is None


@pytest.mark.parametrize('nhan', ['Số tài khoản:', 'TK:', 'CCCD:', 'account:'])
def test_tin_cay_nhan_r5_thang_ngay_ke_ca_ngoai_cua_so_gan(nhan):
    chu = nhan + ' ' * 160 + '2026-10-30'
    assert che._nhan_dinh_danh_truoc(chu, chu.index('2026')) is None
    assert not any(loai == 'ngay' for _, _, loai, _ in che._cac_tien_ngay(chu))
    b = bo(seeds=())
    with pytest.raises(LoiNghiepVu) as exc:
        with b.ram.buoc(b.v) as buoc:
            tw._kiem_vung(chu, (), buoc)
    assert exc.value.ma == 'MASK_DINH_DANH_CHUA_DAT'


def test_word_nhan_va_so_tach_run_van_chan():
    b = bo(seeds=())
    raw = word(noi_dung='<w:p><w:r><w:t>Số tài </w:t></w:r>'
               '<w:r><w:t>khoản: 2026-</w:t></w:r><w:r><w:t>10-30</w:t></w:r></w:p>')
    with pytest.raises(LoiNghiepVu):
        with b.ram.buoc(b.v) as buoc:
            tw.che_word(raw, buoc=buoc, dinh_danh=[])
    assert b.ram._ban_ghi is None and not b.c._tep


@pytest.mark.parametrize('nhan,so', CA_LOT + [('STK: ', '2026-10-30'), ('CMT ', '30/10/2026')])
def test_truc_tiep_nhanh_mien_tru_word_khong_bo_canh_bao_tu_nhan(nhan, so):
    b = bo(seeds=())
    with pytest.raises(LoiNghiepVu) as exc:
        with b.ram.buoc(b.v) as buoc:
            tw._kiem_vung(nhan + so, (), buoc)
    assert exc.value.ma == 'MASK_DINH_DANH_CHUA_DAT'
    assert b.ram._ban_ghi is None


def test_held_out_mask_2c_giu_sha_va_khong_giam_lop_quy_tac():
    # Đối chiếu HEAD trước B5b: 28 ca còn nguyên gold, 14/75 câu thường bị
    # chặn ở NHÁNH QUY TẮC LỊCH SỬ; không phải chứng nhận Local/hai lớp.
    # Chỉ đọc bộ đóng băng; không chép tên từ gold vào luật hoặc test.
    p = Path(__file__).resolve().parents[1] / 'cong-cu/mask_2c_4_ung_vien_demo.json'
    bo_gold = json.loads(p.read_text(encoding='utf-8'))
    raw = json.dumps(bo_gold['noi_dung'], ensure_ascii=False, sort_keys=True,
                     separators=(',', ':'), allow_nan=False).encode('utf-8')
    assert bo_gold['sha256_noi_dung'] == 'sha256:' + sha256(raw).hexdigest() == (
        'sha256:b720fb2d9a330110ed5c4d5fd777b9728887f863651a2b0c46dc395dc45c95ad')
    cac = bo_gold['noi_dung']['ung_vien']
    assert len(cac) == 190 and sum(bool(c['gold']) for c in cac) == 115
    lot, chan_nham = 0, 0
    for c in cac:
        kq = _van_ban(c['van_ban'])
        if c['gold']:
            lot += kq is not None and any(g['nguyen_van'] in kq for g in c['gold'])
        else:
            chan_nham += kq is None
    assert lot <= 28
    assert chan_nham <= 14
