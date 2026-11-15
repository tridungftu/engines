"""MASK-R6b: dữ liệu DEMO, đã kiểm bằng Core giả (CoreGia), không Cloud."""
from contextlib import contextmanager
import json
from threading import Thread
from time import perf_counter

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, ViecDaHuy

from e_mask import che_van_ban as cv, mo_che_ram as mr, phong_bi as pb
from e_mask.anh_xa_ai import AnhXaAI, LoiAnhXa
from e_mask.kho_anh_xa_ram import TRAN_ALIAS_MO
from ho_tro_mo_ram import ALIAS, TEN, MO, bo, giao, chay, ket
from ho_tro_ngan import ai_demo


def tu_choi(b, ma):
    k = chay(b)
    assert k['trang_thai'] == 'LOI' and k['loi']['ma'] == ma, k
    assert k['ket_qua'] is None and b.cong.so_nhan == 0
    assert b.c.ket_qua_cuoi_demo == {} and b.ram._ban_ghi is None
    assert len(b.da_don) == 1


def nhieu_alias(so):
    ten = [f'Tên DEMO {i:04d}' for i in range(so)]
    goc, phep, dau = ' / '.join(ten), [], 0
    for i, t in enumerate(ten):
        phep.append((dau, dau + len(t), f'[[KH-DEMO-{i:04d}]]'))
        dau += len(t) + 3
    return bo(goc=goc, phep=phep)


@pytest.mark.parametrize('mau', ['[[KH-DEMO-{:04d}]]', '[[P{:04d}-DEMO-001]]'])
def test_do_1000_alias_500000_ky_tu_duoi_2_giay(mau):
    aliases = [mau.format(i) for i in range(1000)]
    chu = ('Nội dung DEMO bình thường. ' * 20000)[:500000]
    assert len(chu) == 500000
    dau = perf_counter()
    assert cv._manh_bi_danh_con_lai(chu, aliases, []) == []
    giay = perf_counter() - dau
    print(f'R6b dò chung {mau}: 1000 alias x 500000 ký tự = {giay:.6f} giây')
    assert giay < 2


def test_handler_that_1000_alias_500000_ky_tu_duoi_2_giay():
    b = nhieu_alias(TRAN_ALIAS_MO)
    # Không tính dựng fixture/ánh xạ/giao việc vào thời gian chạy handler.
    giao(b, chu='DEMO ' * 100000)
    dau = perf_counter()
    k = ket(b)
    giay = perf_counter() - dau
    assert k['van_ban_da_mo_che'] == 'DEMO ' * 100000 and k['mo_day_du'] is True
    assert b.ram._ban_ghi is None
    print(f'R6b CoreGia: 1000 alias x 500000 ký tự = {giay:.6f} giây')
    assert giay < 2


@pytest.mark.parametrize('manh', ['KH-DEMO-001', 'kh-demo-001', 'K H - D E M O - 0 0 1',
    'KH-DEMO-00?', 'KH-DEMO-0!01', 'KH-DEMO-00\u200b', '?H-DEMO-001',
    '[KH-DEMO-777', 'KH-DEMO-777]', '[K?-DEMO-777', '[M?S?CT-999'])
def test_dau_vet_alias_mat_ngoac_hong_va_tien_to(manh):
    chu = 'DEMO: ' + manh + ' ; kết thúc.'
    cac = cv._manh_bi_danh_con_lai(chu, ['[[KH-DEMO-001]]'], [])
    assert cac and all(0 <= a < b <= len(chu) for a, b in cac)
    assert all(a < 6 + len(manh) and b > 6 for a, b in cac)


@pytest.mark.parametrize('chu', ['DEMO xKH-DEMO-001x', 'DEMO _KH-DEMO-001_',
    'DEMO KH-DEMO-002', 'DEMO KH-DEMO-0001', 'DEMO doanh nghiệp 2026-11-16 1.000.000 VND'])
def test_khong_bao_nham_ma_khac_va_phan_tu_dai_hon(chu):
    assert cv._manh_bi_danh_con_lai(chu, ['[[KH-DEMO-001]]'], []) == []


def test_khong_noi_qua_vung_da_xet_va_toa_do_unicode():
    a = '[[KH-DEMO-001]]'
    chu = 'Đầu DEMO: ' + a + ' KH-DEMO-001'
    x = chu.index(a)
    assert cv._manh_bi_danh_con_lai(chu, [a], [(x, x + len(a))]) == [(x + len(a) + 1, len(chu))]
    chu = 'KH-DE[[KH-DEMO-001]]MO-001'
    assert cv._manh_bi_danh_con_lai(chu, [a], [(5, 5 + len(a))]) == []


def test_vuot_tran_alias_tu_choi_va_don():
    b = nhieu_alias(TRAN_ALIAS_MO + 1)
    giao(b, chu='DEMO')
    tu_choi(b, 'MASK_QUA_GIOI_HAN')


@pytest.mark.parametrize('noi', ['gia_tri', 'khoa'])
def test_vuot_tran_chuoi_con_ke_ca_chuoi_rong(noi):
    b = bo()
    ai = ai_demo('DEMO', b.ctx.ma_yeu_cau)
    ai['du_lieu'] = {'DEMO': [''] * (pb.TRAN_CHUOI_MO - 1)} if noi == 'gia_tri' else {f'k{i}': 0 for i in range(pb.TRAN_CHUOI_MO)}
    giao(b, ai=ai)
    tu_choi(b, 'MASK_QUA_GIOI_HAN')


def test_dung_bien_so_chuoi_con_khong_cat_ngam():
    b = bo()
    ai = ai_demo('DEMO', b.ctx.ma_yeu_cau)
    ai['du_lieu'] = {'DEMO': [''] * (pb.TRAN_CHUOI_MO - 2)}
    giao(b, ai=ai)
    k = ket(b)
    assert json.loads(k['tra_loi_ai_da_mo_json'])['du_lieu'] == ai['du_lieu']
    assert k['mo_day_du'] is True and b.ram._ban_ghi is None


@pytest.mark.parametrize('alias', [ALIAS, ALIAS.lower(), '[[KH-LA-DEMO]]',
    'MASKCT-DEMO-0001', 'M A S K C T - D E M O - 0 0 0 ?'])
def test_khoa_alias_khong_duoc_bao_da_mo_day_du(alias):
    b = bo()
    ai = ai_demo(ALIAS, b.ctx.ma_yeu_cau)
    ai['du_lieu'] = {'ngoai': [{alias: {'so': 42, 'gia_tri': ALIAS}}]}
    giao(b, ai=ai)
    k = ket(b)
    assert k['mo_day_du'] is False
    assert json.loads(k['tra_loi_ai_da_mo_json'])['du_lieu']['ngoai'][0][alias] == {'so': 42, 'gia_tri': TEN}
    assert b.ram._ban_ghi is None


def test_alias_bia_co_trong_map_nhung_khong_co_trong_ban_da_giao(monkeypatch):
    b = bo()
    fake = '[[KH-DEMO-CHUA-GIAO]]'
    # Mô phỏng map từng cấp có alias dư; bản da_che đã kiểm vẫn bất biến.
    b.ram._ban_ghi.du_lieu['alias_nguyen_van'][fake] = 'Tên DEMO chưa giao'
    that = AnhXaAI.alias_nguyen_van
    def tap_cap(m):
        return dict(that(m), **{fake: 'Tên DEMO chưa giao'})
    monkeypatch.setattr(AnhXaAI, 'alias_nguyen_van', tap_cap)
    giao(b, chu=ALIAS + ' ' + fake)
    tu_choi(b, 'MASK_MO_CHE_KHONG_DAY_DU')


@pytest.mark.parametrize('moc', ['kiem_map', 'map_hong', 'lap_alias'])
def test_timer_don_giua_luot_tra_dung_ma_mat_anh_xa(monkeypatch, moc):
    b = bo()
    that = mr.kiem_anh_xa
    that_alias = AnhXaAI.alias_nguyen_van
    da_chen = []
    def het_han():
        if not da_chen:
            da_chen.append(True)
            # Thực sự dọn từ luồng khác, không chỉ giả LoiNghiepVu.
            t = Thread(target=lambda: b.dh.tien(600))
            t.start()
            t.join(timeout=2)
            assert not t.is_alive()
    def kiem(m):
        that(m)
        if moc != 'lap_alias':
            het_han()
        if moc == 'map_hong':
            raise LoiAnhXa()
    def aliases(m):
        ket = that_alias(m)
        if moc == 'lap_alias':
            het_han()
        return ket
    monkeypatch.setattr(mr, 'kiem_anh_xa', kiem)
    monkeypatch.setattr(AnhXaAI, 'alias_nguyen_van', aliases)
    giao(b)
    tu_choi(b, 'MASK_ANH_XA_KHONG_CON')
    assert da_chen


def test_tran_bang_do_tu_choi_khong_giu_map(monkeypatch):
    b = bo()
    monkeypatch.setattr(cv, 'TRAN_NUT_DO_MANH', 10)
    giao(b)
    tu_choi(b, 'MASK_QUA_GIOI_HAN')


@pytest.mark.parametrize('i', range(len('kh-demo-001')))
@pytest.mark.parametrize('dang', ['thay', 'chen'])
def test_ky_tu_la_o_moi_vi_tri_khong_duoc_mo(i, dang):
    ma = 'kh-demo-001'
    if dang == 'chen' and i == 0:
        # Một dấu câu trước mã trần vẫn để lại toàn bộ mã trần đã biết.
        hong = '!' + ma
    else:
        hong = ma[:i] + '!' + ma[i + (dang == 'thay'):]
    assert cv._manh_bi_danh_con_lai('DEMO: ' + hong + ' ;', ['[[' + ma + ']]'], [])


def test_day_ngoac_dai_qua_trinh_do_khong_binh_phuong():
    dau = perf_counter()
    assert cv._manh_bi_danh_con_lai('[' * 500000, ['[[KH-DEMO-001]]'], []) == []
    assert perf_counter() - dau < 2


def test_kiem_han_trong_chuoi_lon_khong_co_alias(monkeypatch):
    b = bo()
    that = cv._DoManhBiDanh.quet
    dem = []
    def quet(self, *a, **kw):
        kiem = self.kiem
        def chen():
            dem.append(1)
            if len(dem) == 20:
                b.dh.tien(600)
            kiem()
        self.kiem = chen
        return that(self, *a, **kw)
    monkeypatch.setattr(cv._DoManhBiDanh, 'quet', quet)
    giao(b, chu='DEMO ' * 100000)
    tu_choi(b, 'MASK_ANH_XA_KHONG_CON')
    assert len(dem) == 20


@pytest.mark.parametrize('kieu', ['loi', 'huy', 'chua_ro', 'timeout'])
def test_frame_handler_khong_giu_ket_raw_chu_sau_ngoai_le(kieu):
    b = bo()
    @contextmanager
    def hong(*a, **kw):
        def nhan(raw):
            if kieu == 'loi': raise LoiNghiepVu('DEMO', 'Lỗi DEMO.')
            if kieu == 'huy': raise ViecDaHuy()
            if kieu == 'chua_ro': raise ChuaRo('DEMO')
            raise TimeoutError()
        yield nhan
    b.cong.ban_giao_cuoi = hong
    that, ngoai_le = b.app._ham[MO], []
    def giu(v):
        try:
            return that(v)
        except BaseException as exc:
            ngoai_le.append(exc)
            raise
    b.app._ham[MO] = giu
    giao(b)
    k = chay(b)
    assert k['trang_thai'] == {'loi': 'LOI', 'huy': 'HUY', 'chua_ro': 'CHUA_RO', 'timeout': 'CHUA_RO'}[kieu]
    assert b.ram._ban_ghi is None and ngoai_le
    tb, da_kiem = ngoai_le[0].__traceback__, False
    while tb:
        f = tb.tb_frame
        if f.f_code is mr.MoCheRAM.mo.__code__:
            assert all(f.f_locals.get(ten) is None for ten in ('ket', 'raw', 'chu', 'ai'))
            da_kiem = True
        tb = tb.tb_next
    assert da_kiem


def test_frame_doc_json_bo_raw_khi_json_hong():
    from io import BytesIO
    from types import SimpleNamespace
    v = SimpleNamespace(dau_vao={'tep': {'mime': 'application/json', 'tep_id': 'DEMO'}},
                        mo_tep=lambda _: BytesIO(b'{"DEMO": invalid}'))
    with pytest.raises(LoiNghiepVu) as e:
        pb._doc_json(v)
    tb = e.value.__traceback__
    while tb and tb.tb_frame.f_code is not pb._doc_json.__code__:
        tb = tb.tb_next
    assert tb and tb.tb_frame.f_locals['raw'] is None
