"""MASK-S22: SDK/cấu hình thật, kho bí danh vẫn RAM theo chỉ dẫn Lead."""
from pathlib import Path
import json

import pytest
import kho_tri_thuc_sdk
from kho_tri_thuc_sdk.engine import LoiDuongTruyen
from kho_tri_thuc_sdk.thu import CoreGia

from ho_tro_van_ban_lich_su import tao_app
from e_mask.kho_ngan import KHAI_NGAN
from e_mask.ngan import NganBoNho, NganKhongHopLe
from ho_tro_ngan import QuyenNganDemo, VAN_BAN


def test_phieu_cau_hinh_sdk_va_kho_ram_van_tach_kho_core_r1():
    app = tao_app()
    assert kho_tri_thuc_sdk.__version__ == '2.2.0'
    assert app.phieu['tuong_thich']['sdk'] == '>=2.2.0 <3.0.0'
    assert app.phieu['cau_hinh'] == {'schema': 'cau_hinh.schema.json'}
    assert {b['bang'] for b in app.phieu['ngan_du_lieu']} == {'dinh_danh', 'bi_danh'}
    assert app.phieu['du_lieu']['goi_migration']['thu_muc'] == 'sql'
    goi = Path(app.thu_muc_goi)
    assert (goi / 'sql/kiem_ke.json').is_file()
    # UI-MASK chỉ khai dự kiến cửa màn chưa được SDK 2.2.0 nhận.
    khai_ui = json.loads((goi / 'KHAI-SDK-2.1.json').read_text('utf-8'))
    assert set(khai_ui) == {'ghi_chu', 'giao_dien_quan_tri', 'can_core'}
    assert khai_ui['giao_dien_quan_tri'][0]['tep'] == 'ui/cau_hinh.js'
    assert not (goi / 'e_mask/cau_hinh.py').exists()
    schema = json.loads((goi / 'cau_hinh.schema.json').read_text('utf-8'))
    assert all('default' in truong for truong in schema['properties'].values())
    assert schema['properties']['thoi_han_anh_xa_giay']['default'] == 600


@pytest.mark.parametrize('cau_hinh, ttl', [({}, 600),
                                        ({'thoi_han_anh_xa_giay': 60}, 60),
                                        ({'thoi_han_anh_xa_giay': 600}, 600),
                                        ({'thoi_han_anh_xa_giay': 900}, 900)])
def test_core_gia_cau_hinh_snapshot_khong_dung_ngan_bi_danh(monkeypatch, cau_hinh, ttl):
    quyen = QuyenNganDemo()
    ram = NganBoNho(KHAI_NGAN)
    app = tao_app(ngan=ram, quyen=quyen)
    core = CoreGia(app)
    core.dat_cau_hinh(app.ma, cau_hinh)
    da_doc = []
    from e_mask.kho_dinh_danh import KhoDinhDanh
    xu_ly = KhoDinhDanh.xu_ly

    def kiem(self, viec, *a, **kw):
        da_doc.append(viec.cau_hinh)
        assert self._ngan is ram
        assert viec.ngan is not ram and app.ngan is not ram
        return xu_ly(self, viec, *a, **kw)

    monkeypatch.setattr(KhoDinhDanh, 'xu_ly', kiem)
    # Nếu vô tình dùng ngăn SDK, bảng chưa khai phải lỗi, không tự tạo bảng.
    core.gay_xung_dot_ngan('cho_duyet')
    ma = core.giao_viec('mask.che_van_ban@1', {'loai': 'van_ban', 'van_ban': VAN_BAN})
    quyen.cap(ma)
    core.chay(app)
    assert core.xem(ma)['trang_thai'] == 'XONG'
    assert da_doc == [{'thoi_han_anh_xa_giay': ttl}]
    assert ram.tim('cho_duyet').danh_sach
    assert core.xem_ngan(app.ma, 'cho_duyet') == []
    with pytest.raises(NganKhongHopLe):
        ram.doc('cau_hinh', {})


def test_core_gia_tu_choi_khoa_cau_hinh_la():
    app = tao_app()
    core = CoreGia(app)
    with pytest.raises(LoiDuongTruyen) as exc:
        core.dat_cau_hinh(app.ma, {'tu_cap_quyen': True})
    assert exc.value.ma == 'NGAN_DU_LIEU_SAI'


def test_demo_chuan_van_chan_thieu_quyen_khong_bao_thanh_cong_gia():
    # Giữ hai ví dụ; chứng minh blocker SDK/Core, không thêm quyền DEMO runtime.
    ds = CoreGia().chay_thu_demo(tao_app())
    assert len(ds) == 2
    assert all(k['trang_thai'] == 'LOI' and k['ket_qua'] is None for k in ds)
    assert all(k['loi']['ma'] == 'MASK_NGU_CANH_CHUA_XAC_MINH' for k in ds)
