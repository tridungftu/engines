"""R3: đã kiểm bằng Core giả (CoreGia); không model/mạng/Cloud.

Giữ ngữ nghĩa ngăn SDK thật, không mock trả tên thay cho null+cờ.
"""
import json
from pathlib import Path
from time import monotonic
import unicodedata

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, ViecDaHuy

from e_mask import che_van_ban as che, tra_cuu_dinh_danh as tra
from e_mask.hau_kiem_ai import HauKiemAI
from e_mask.kho_dinh_danh import KhoDinhDanh
from test_mask_r2 import bo, _dong, _them


TEN = 'Công ty DEMO Đá Cuội'
ALIAS = '[[MASKCT-R3-DEMO]]'


@pytest.fixture(autouse=True)
def tu_dien_sach():
    from e_mask import tai_nguyen
    tai_nguyen.xoa_cache()
    tai_nguyen.nap_tu_goi()
    yield
    tai_nguyen.xoa_cache()


def luot(viec, bo, goc):
    return tra.TraCuuDinhDanh(goc, KhoDinhDanh(quyen=bo.quyen).mo_kho_nhan_dien(viec),
                             han_monotonic=monotonic() + 60, kiem_huy=viec.kiem_huy)


@pytest.mark.parametrize('doi', [lambda s: s, lambda s: s.lower(),
                               lambda s: unicodedata.normalize('NFD', s),
                               lambda s: '\u200b'.join(s)])
def test_nguyen_van_chi_tu_dau_vao_ram_null_co(bo, monkeypatch, capsys, doi):
    goc = doi(TEN)
    dong = _dong(TEN, trang_thai='CHINH_THUC')
    def kiem(viec):
        _them(viec, dong, ALIAS)
        kho = KhoDinhDanh(quyen=bo.quyen).mo_kho_nhan_dien(viec)
        monkeypatch.setattr(kho, 'liet_ke_dinh_danh', lambda: pytest.fail('Không được liệt kê kho.'))
        l = tra.TraCuuDinhDanh(goc, kho, han_monotonic=monotonic() + 60, kiem_huy=viec.kiem_huy)
        try:
            l.them(tra.UngVien(0, len(goc), 'CONG_TY', 'dau_vao'))
            kq = l.ket_qua()
            assert kq.phep_thay == ((0, len(goc), ALIAS),)
            assert kq.alias_nguyen_van == {ALIAS: goc}
            assert goc not in repr(l) and goc not in repr(kq)
        finally:
            l.dong()
        assert not l._goc and not l._da_tim and not l._alias
    bo.chay(kiem)
    assert TEN not in json.dumps(bo.core.nhat_ky, ensure_ascii=False)
    assert not capsys.readouterr().err


@pytest.mark.parametrize('doi', [lambda s: s.upper(),
                               lambda s: unicodedata.normalize('NFD', s),
                               lambda s: s.replace(' ', '  '),
                               lambda s: '\u200b'.join(s)])
def test_cung_alias_nhieu_nguyen_van_chan_khong_chon_ten_dau(bo, doi):
    khac = doi(TEN)
    goc = TEN + '; ' + khac
    def kiem(viec):
        _them(viec, _dong(TEN, trang_thai='CHINH_THUC'), ALIAS)
        l = luot(viec, bo, goc)
        l.them(tra.UngVien(0, len(TEN), 'CONG_TY', 'quy_tac'))
        with pytest.raises(LoiNghiepVu) as exc:
            l.them(tra.UngVien(len(TEN) + 2, len(goc), 'CONG_TY', 'local'))
        assert exc.value.ma == 'MASK_MO_CHE_KHONG_DAY_DU'
        assert not l._alias and not l._goc
        assert TEN not in str(exc.value) and khac not in str(exc.value)
        with pytest.raises(LoiNghiepVu):
            l.ket_qua()
    bo.chay(kiem)


def test_local_dung_cung_luot_dem_trung_mot_lan(bo):
    goc = TEN + '; ' + TEN
    def kiem(viec):
        _them(viec, _dong(TEN, trang_thai='CHINH_THUC'), ALIAS)
        l = luot(viec, bo, goc)
        l.them(tra.UngVien(0, len(TEN), 'CONG_TY', 'dau_vao'))
        hk = HauKiemAI(ngan=None, quyen=None, cong=None, phien_ban_engine='DEMO')
        kq = hk._tra_ung_vien_ram(l, [(len(TEN) + 2, len(goc), 0, 1, 'CONG_TY')])
        assert kq.so_ung_vien == 1 and len(kq.phep_thay) == 2
        l.dong()
    bo.chay(kiem)


def test_qua_2000_ung_vien_khong_rpc_thu_2001(bo, monkeypatch):
    cac = ['demor3x' + str(i) for i in range(2001)]
    goc = ';'.join(cac)
    def kiem(viec):
        l = luot(viec, bo, goc)
        goi, tim = [], l._kho.tim_ung_vien
        def spy(*args):
            goi.append(1)
            return tim(*args)
        monkeypatch.setattr(l._kho, 'tim_ung_vien', spy)
        a = 0
        for ten in cac[:2000]:
            l.them(tra.UngVien(a, a + len(ten), 'KHAC', 'truong'))
            a += len(ten) + 1
        assert l.ket_qua().so_ung_vien == 2000
        with pytest.raises(LoiNghiepVu) as exc:
            l.them(tra.UngVien(a, len(goc), 'KHAC', 'truong'))
        assert exc.value.ma == 'MASK_UNG_VIEN_QUA_TRAN' and len(goi) == 2000
        assert not l._goc and not l._da_tim
    bo.chay(kiem)


def test_ngan_sach_do_va_deadline_sau_rpc(bo, monkeypatch):
    def kiem(viec):
        l = luot(viec, bo, TEN)
        with pytest.raises(LoiNghiepVu) as exc:
            l.tinh_chi_phi(tra.TRAN_KY_TU_DO + 1)
        assert exc.value.ma == 'MASK_UNG_VIEN_QUA_TRAN' and not l._goc
        gio = [10.0]
        monkeypatch.setattr(tra, 'monotonic', lambda: gio[0])
        kho = KhoDinhDanh(quyen=bo.quyen).mo_kho_nhan_dien(viec)
        tim = kho.tim_ung_vien
        def cham(*args):
            ket = tim(*args)
            gio[0] = 20.0
            return ket
        monkeypatch.setattr(kho, 'tim_ung_vien', cham)
        l = tra.TraCuuDinhDanh(TEN, kho, han_monotonic=15.0, kiem_huy=viec.kiem_huy)
        with pytest.raises(LoiNghiepVu) as exc:
            l.them(tra.UngVien(0, len(TEN), 'CONG_TY', 'local'))
        assert exc.value.ma == 'MASK_UNG_VIEN_QUA_HAN' and not l._goc
    bo.chay(kiem)


@pytest.mark.parametrize('gia_tri', [-1, True, 1.5])
def test_khong_tru_nguoc_ngan_sach(bo, gia_tri):
    def kiem(viec):
        l = luot(viec, bo, TEN)
        with pytest.raises(LoiNghiepVu):
            l.tinh_chi_phi(gia_tri)
        assert not l._goc
    bo.chay(kiem)


def test_het_han_truoc_rpc_khong_doi_kho(bo, monkeypatch):
    def kiem(viec):
        gio = [10.0]
        monkeypatch.setattr(tra, 'monotonic', lambda: gio[0])
        kho = KhoDinhDanh(quyen=bo.quyen).mo_kho_nhan_dien(viec)
        l = tra.TraCuuDinhDanh(TEN, kho, han_monotonic=15.0, kiem_huy=viec.kiem_huy)
        monkeypatch.setattr(kho, 'tim_ung_vien', lambda *args: pytest.fail('Đã hết hạn trước truy cập.'))
        gio[0] = 15.0
        with pytest.raises(LoiNghiepVu) as exc:
            l.them(tra.UngVien(0, len(TEN), 'CONG_TY', 'local'))
        assert exc.value.ma == 'MASK_UNG_VIEN_QUA_HAN' and not l._goc
    bo.chay(kiem)


@pytest.mark.parametrize('dang', ['ten_ro', 'thieu_co', 'alias_hong'])
def test_metadata_bat_thuong_khong_duoc_dung_de_bu_ten(bo, monkeypatch, dang):
    def kiem(viec):
        _them(viec, _dong(TEN, trang_thai='CHINH_THUC'), ALIAS)
        l = luot(viec, bo, TEN)
        tim = l._kho.tim_ung_vien
        def hong(*args):
            muc = tim(*args)  # Vẫn bắt đầu từ kết quả SDK null+cờ thật.
            if dang == 'ten_ro':
                muc['gia_tri_goc'] = TEN
            elif dang == 'thieu_co':
                muc.pop('gia_tri_chuan_da_ma_hoa')
            else:
                muc['bi_danh'] = '[MASKDEMO-R3]'
            return muc
        monkeypatch.setattr(l._kho, 'tim_ung_vien', hong)
        with pytest.raises(LoiNghiepVu) as exc:
            l.them(tra.UngVien(0, len(TEN), 'CONG_TY', 'local'))
        assert not l._goc and TEN not in str(exc.value)
    bo.chay(kiem)


def test_ung_vien_tu_caller_khong_co_trong_dau_vao_khong_tra_kho(bo, monkeypatch):
    # Trường nguyên vẹn tự sinh một truy vấn hợp lệ dù tên caller không có;
    # theo dõi đối số riêng để chỉ cấm giá trị caller ngoài đầu vào.
    def kiem_thuc(viec):
        kho = KhoDinhDanh(quyen=bo.quyen).mo_kho_nhan_dien(viec)
        tim = kho.tim_ung_vien
        def spy(gia_tri, nhom):
            assert gia_tri in 'nội dung dự kiến.' and gia_tri != TEN
            return tim(gia_tri, nhom)
        monkeypatch.setattr(kho, 'tim_ung_vien', spy)
        k = che.khao_sat_che_chinh_xac('nội dung dự kiến.', [{'gia_tri': TEN, 'nhom': 'CONG_TY'}],
            kho, han_monotonic=monotonic() + 60, kiem_huy=viec.kiem_huy)
        assert not k.doi_chieu.alias_nguyen_van
    bo.chay(kiem_thuc)


@pytest.mark.parametrize('loi_nguon', [ChuaRo('mask-demo-r3'), ViecDaHuy()])
def test_chua_ro_huy_khong_bien_thanh_danh_sach_rong(bo, monkeypatch, loi_nguon):
    def kiem(viec):
        l = luot(viec, bo, TEN)
        def hong(*args):
            raise loi_nguon
        monkeypatch.setattr(l._kho, 'tim_ung_vien', hong)
        with pytest.raises(type(loi_nguon)):
            l.them(tra.UngVien(0, len(TEN), 'CONG_TY', 'local'))
        assert not l._goc
    bo.chay(kiem)


def test_khao_sat_khong_dung_matcher_danh_muc_giu_tien_ngay(bo, monkeypatch):
    goc = TEN + '; thanh toán 1.000.000 VND ngày 2026-10-30.'
    def kiem(viec):
        _them(viec, _dong(TEN, trang_thai='CHINH_THUC'), ALIAS)
        kho = KhoDinhDanh(quyen=bo.quyen).mo_kho_nhan_dien(viec)
        monkeypatch.setattr(kho, 'liet_ke_dinh_danh', lambda: pytest.fail('Không được liệt kê kho.'))
        hau_kiem = che._kiem_con_sot
        def chi_ram(chu, da_biet, **kw):
            assert da_biet == []
            return hau_kiem(chu, da_biet, **kw)
        monkeypatch.setattr(che, '_kiem_con_sot', chi_ram)
        kq = che.khao_sat_che_chinh_xac(goc, [], kho, han_monotonic=monotonic() + 60,
                                      kiem_huy=viec.kiem_huy)
        assert kq.anh_xa.da_che == ALIAS + goc[len(TEN):]
        assert kq.doi_chieu.alias_nguyen_van == {ALIAS: TEN}
        assert kq.kiem_tien_ngay
        assert not hasattr(kq, 'gui_duoc')
    bo.chay(kiem)


@pytest.mark.parametrize('noi_bo', [False, True])
def test_handler_sdk_khong_roi_ve_ram_lich_su_khong_phat_hanh(bo, monkeypatch, noi_bo):
    def kiem(viec):
        kho = KhoDinhDanh(quyen=bo.quyen).mo_kho_nhan_dien(viec)
        def cam(*args):
            pytest.fail('Không được chạy giao dịch lịch sử.')
        monkeypatch.setattr(kho, 'giao_dich', cam)
        with pytest.raises(LoiNghiepVu) as exc:
            (che.che_co_anh_xa if noi_bo else che.che)(TEN, [], kho)
        assert exc.value.ma == 'MASK_R3_CHUA_CHUNG_MINH'
        hk = HauKiemAI(ngan=None, quyen=None, cong=None, phien_ban_engine='DEMO')
        with pytest.raises(LoiNghiepVu) as exc:
            hk._che_them(kho, None, None, [])
        assert exc.value.ma == 'MASK_R3_CHUA_CHUNG_MINH'
    bo.chay(kiem)


def test_gold_demo_da_dong_bang():
    from hashlib import sha256
    tep = Path(__file__).with_name('demo_mask_r3.json')
    assert sha256(tep.read_bytes()).hexdigest() == 'b200f74a29547965c637487ee0c6ded78cb6174028b5ce09236e06f5798d5181'
    gold = json.loads(tep.read_text(encoding='utf-8'))
    assert len(gold['duong']) == 16 and len(gold['am']) == 18
    assert all(chu.count(ten) == 1 for _, ten, chu in gold['duong'])
