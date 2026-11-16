"""B11 lượt 2: kiểm riêng cửa cuối bằng detector thật, chỉ dữ liệu DEMO.

Writer và lần kiểm map trước đó được cô lập để ca độc hại thực sự tới
biểu thức hậu kiểm mới; không thay detector/bộ lọc/kiểm nhãn-ngày.
Phát hành hai lớp và regression B5/B6/B6b/B8 chạy bằng bộ test thật.
"""
from types import SimpleNamespace

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu

from e_mask import hau_kiem_tep as hk, tai_nguyen, tep_word as tw, tep_excel as tx
from e_mask.anh_xa_ai import tao_anh_xa
from e_mask.ho_so_ai import bam_bytes


@pytest.fixture(autouse=True)
def _tu_dien_demo():
    tai_nguyen.nap_tu_goi()


def _cua_cuoi(monkeypatch, loai, chu):
    module = tw if loai == 'docx' else tx
    m = tao_anh_xa(chu, ())
    sau = SimpleNamespace(vung=[SimpleNamespace(van_ban=chu, chu=chu)])
    raw = b'DEMO B11 cua cuoi'
    s = dict(loai=loai, tai_lieu=None, anh_xa=[m], da_che=raw,
             bam_da_che=bam_bytes(raw), kich_ban=())
    monkeypatch.setattr(module, '_ghi', lambda *a: (raw, sau, ()))
    monkeypatch.setattr(module, '_kiem_vung', lambda *a: m)
    return s, sau


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('chu', [
    'SAMPLE; Công ty DEMO Kim Sơn Phát',
    'Công ty DRAFT',
    'khách hàng SAMPLE',
    'Họ tên: tổng chi đã đối chiếu.',
    'Ông tổng thu đã đối chiếu.',
    'người liên hệ: tổng chi đã đối chiếu.',
    'SAMPLE; Trần Minh An',
    'SAMPLE; TRẦN MINH AN',
    'SAMPLE; 0123456789012',
    'SAMPLE; Số tài khoản: 1234-56-78',
    'SAMPLE; CCCD: 09/11/2026',
    'SAMPLE; Tài khoản: 2026-11-09',
    'DEMO - Vinamilk; tổng chi đã đối chiếu',
    'DEMO (Techcombank); 3.754.200 VND',
    'DEMO.Vinamilk',
    'DRAFT – Techcombank',
    'DEMO (Techcombank)',
    'TEST - Vinamilk',
    'DEMO & Vinamilk',
    'SAMPLE - Techcombank',
    'Tổng thu đã tổng hợp quỳnh trâm',
    'Tổng chi đã kiểm tra cho Lan',
    'Tổng chi đã đối chiếu: Lan',
    'Tổng thu đã kiểm tra Hồng',
])
def test_hau_kiem_khong_mien_ten_cong_ty_nguoi_nhan_danh_xung_hoa_va_so(loai, chu, monkeypatch):
    s, _ = _cua_cuoi(monkeypatch, loai, chu)
    con, du = hk.che._kiem_con_sot(chu, [])
    assert du and con  # Detector thật phải có cảnh báo trước khi qua cửa B11.
    with pytest.raises(LoiNghiepVu) as exc:
        hk._kiem_cuoi(s, kiem=lambda: None, buoc=None)
    assert exc.value.ma == 'MASK_DINH_DANH_CHUA_DAT'


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('chu', ['SAMPLE', 'TEST', 'DRAFT', 'DEMO',
                               'tổng chi đã đối chiếu.', 'tổng thu đang tổng hợp.'])
def test_hau_kiem_dung_bo_loc_da_duyet_cho_cu_phap_dong(loai, chu, monkeypatch):
    s, sau = _cua_cuoi(monkeypatch, loai, chu)
    con, du = hk.che._kiem_con_sot(chu, [])
    assert du and con  # Đối chứng sẽ hỏng nếu hậu kiểm quay lại biểu thức cũ.
    assert hk._kiem_cuoi(s, kiem=lambda: None, buoc=None) is sau


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_hau_kiem_van_chan_khi_detector_chua_quet_du(loai, monkeypatch):
    s, _ = _cua_cuoi(monkeypatch, loai, 'SAMPLE')
    that = hk.che._kiem_con_sot
    monkeypatch.setattr(hk.che, '_kiem_con_sot', lambda *a: (that(*a)[0], False))
    with pytest.raises(LoiNghiepVu) as exc:
        hk._kiem_cuoi(s, kiem=lambda: None, buoc=None)
    assert exc.value.ma == 'MASK_DINH_DANH_CHUA_DAT'
