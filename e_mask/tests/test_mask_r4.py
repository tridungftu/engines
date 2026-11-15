"""MASK-R4: RAM/vòng đời; đã kiểm bằng Core giả (CoreGia), chỉ DEMO."""
from dataclasses import replace
import json
from threading import Event, Thread, Timer

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, ViecDaHuy
from kho_tri_thuc_sdk.thu import CoreGia

from e_mask.chay import tao_app
from e_mask.kho_anh_xa_ram import KhoAnhXaRAM
from e_mask.quyen_yeu_cau import GhimTienTrinh, NguCanhRAM, SuKienRAM
from ho_tro_ngan import QuyenNganDemo, TEN, VAN_BAN, ai_demo, viec_demo
from ho_tro_ram import DongHoGia


ALIAS = '[[MASKCT-0001]]'
THIEU = 'MASK_ANH_XA_KHONG_CON'


def ghep(*, ttl=600, han=None):
    q, dh = QuyenNganDemo(), DongHoGia()
    q.ram_han = han
    kho = KhoAnhXaRAM(quyen=q, dong_ho=dh, hen_gio=dh.hen_gio)
    v = viec_demo()
    v.cau_hinh = {'thoi_han_anh_xa_giay': ttl}
    ctx = q.cap(v.id)
    return q, dh, kho, v, ctx.ma_yeu_cau


def cho_ai(kho, v):
    with kho.buoc(v) as b:
        b.du_lieu.update(anh_xa={ALIAS: TEN}, goc=VAN_BAN, bytes_goc=b'DEMO',
                         span=[(0, len(TEN))], phien_ban='DEMO', ke_hoach={'doan': [0]})
        b.cho_ai()
        du = b.du_lieu
    return du


def viec_mo(q, ma, *, id='mo-DEMO'):
    v = viec_demo(id)
    v.dau_vao = {'loai': 'tra_loi_ai', 'tra_loi_ai': ai_demo(ALIAS, ma)}
    v.cau_hinh = {'thoi_han_anh_xa_giay': 900}
    q.cap(v.id, loai='mo_che', ma_yeu_cau=ma)
    return v


def loi(ma, ham):
    with pytest.raises(LoiNghiepVu) as e:
        ham()
    assert e.value.ma == ma
    assert TEN not in str(e.value)
    return e.value


def mo(kho, q, ma, v=None):
    v = v or viec_mo(q, ma)
    with kho.buoc(v, loai='mo_che', ma_yeu_cau=ma) as b:
        return b.du_lieu['anh_xa'][ALIAS]


@pytest.mark.parametrize('ttl', [60, 600, 900])
def test_ttl_chup_dau_chuoi_khong_truot_retry_doi_cau_hinh(ttl):
    q, dh, kho, v, ma = ghep(ttl=ttl)
    du = cho_ai(kho, v)
    assert dh.hen[0].luc == 100 + ttl
    dh.tien(ttl - 1)
    v.cau_hinh['thoi_han_anh_xa_giay'] = 900 if ttl != 900 else 60
    with kho.buoc(v) as b:
        assert b.thu_lai and b.du_lieu is du
        b.cho_ai()
    assert len(dh.hen) == 1
    dh.tien(1)
    assert du == {} and kho._ban_ghi is None
    loi(THIEU, lambda: mo(kho, q, ma))
    loi(THIEU, lambda: cho_ai(kho, v))


def test_mac_dinh_600_va_monotonic_khong_phu_thuoc_gio_he_thong(monkeypatch):
    q, dh, kho, v, ma = ghep()
    v.cau_hinh = {}
    monkeypatch.setattr('time.time', lambda: -10**12)
    cho_ai(kho, v)
    assert dh.hen[0].luc == 700
    monkeypatch.setattr('time.time', lambda: 10**12)
    dh.tien(599)
    assert mo(kho, q, ma) == TEN
    loi(THIEU, lambda: mo(kho, q, ma))


@pytest.mark.parametrize('han', [99, 100, 110, 700, 1000])
def test_han_core_som_hon_ttl(han):
    q, dh, kho, v, ma = ghep(han=han)
    if han <= 100:
        loi(THIEU, lambda: cho_ai(kho, v))
        assert kho._ban_ghi is None
    else:
        du = cho_ai(kho, v)
        assert dh.hen[-1].luc == min(han, 700)
        dh.tien(min(han, 700) - 100)
        assert du == {}


def test_core_rut_han_retry_khong_noi_han():
    q, dh, kho, v, ma = ghep(han=650)
    du = cho_ai(kho, v)
    q.ram_han = 1000
    with kho.buoc(v) as b:
        b.cho_ai()
    assert kho._ban_ghi.han == 650
    q.ram_han = 120
    with kho.buoc(v) as b:
        b.cho_ai()
    assert dh.hen[-1].luc == 120
    dh.tien(20)
    assert du == {}


@pytest.mark.parametrize('ttl', [None, True, 59, 901, 60.5, '600'])
def test_ttl_sai_tu_choi_khong_tao_map(ttl):
    q, dh, kho, v, ma = ghep(ttl=ttl)
    loi('MASK_CAU_HINH_KHONG_HOP_LE', lambda: cho_ai(kho, v))
    assert kho._ban_ghi is None and dh.hen == []


def test_timer_chay_som_khong_noi_han_va_timer_cu_khong_don_chuoi_moi():
    q, dh, kho, v, ma = ghep(ttl=60)
    cu = cho_ai(kho, v)
    hen_cu = dh.hen[0]
    dh.tien(1)
    hen_cu.no()
    assert dh.hen[-1].luc == 160
    assert mo(kho, q, ma) == TEN and cu == {}
    v2 = viec_demo('che-khac-DEMO'); v2.cau_hinh = {}
    q.cap(v2.id)
    moi = cho_ai(kho, v2)
    hen_cu.no()
    assert moi['goc'] == VAN_BAN
    q.bao_ram(q.ve[v2.id, 'che'].ma_yeu_cau)
    assert moi == {}


@pytest.mark.parametrize('ly_do', ['HUY', 'LOI', 'KET_THUC', 'MAT_QUYEN', 'MAT_LEASE', 'HET_HAN'])
def test_don_ngay_khi_mask_ranh_cho_ai(ly_do):
    q, dh, kho, v, ma = ghep()
    du = cho_ai(kho, v)
    map_cu = du['anh_xa']
    q.bao_ram(ma, ly_do)
    assert kho._ban_ghi is None and du == {} and map_cu == {}
    assert dh.hen[0].da_huy
    loi(THIEU, lambda: mo(kho, q, ma))


@pytest.mark.parametrize('loi_nguon', [ValueError, ViecDaHuy, KeyboardInterrupt, SystemExit])
@pytest.mark.parametrize('dang_mo', [True, False])
def test_finally_don_moi_loi_va_huy(loi_nguon, dang_mo):
    q, dh, kho, v, ma = ghep()
    if dang_mo:
        du = cho_ai(kho, v)
        v = viec_mo(q, ma)
    with pytest.raises(loi_nguon):
        with kho.buoc(v, loai='mo_che' if dang_mo else 'che',
                      ma_yeu_cau=ma if dang_mo else None) as b:
            if not dang_mo:
                b.du_lieu['anh_xa'] = {ALIAS: TEN}
                du = b.du_lieu
                b.cho_ai()  # Lỗi sau tuyên bố chờ vẫn phải dọn.
            raise loi_nguon('DEMO')
    assert du == {} and kho._ban_ghi is None and dh.hen[0].da_huy


@pytest.mark.parametrize('dang_mo, bao_cho, con_han', [
    (False, True, True), (False, False, True), (True, False, True), (False, True, False),
])
def test_chua_ro_chi_giu_khi_dang_cho_trong_han(dang_mo, bao_cho, con_han):
    q, dh, kho, v, ma = ghep()
    du = cho_ai(kho, v) if dang_mo else None
    if dang_mo:
        v = viec_mo(q, ma)
    mong_doi = ChuaRo if con_han else LoiNghiepVu
    with pytest.raises(mong_doi):
        with kho.buoc(v, loai='mo_che' if dang_mo else 'che',
                      ma_yeu_cau=ma if dang_mo else None) as b:
            du = b.du_lieu
            du['anh_xa'] = {ALIAS: TEN}
            if bao_cho:
                b.cho_ai()
            if not con_han:
                dh.tien(600)
            raise ChuaRo('tuong-quan-DEMO')
    if not dang_mo and bao_cho and con_han:
        assert kho._ban_ghi.trang_thai == 'CHO_AI' and kho._ban_ghi.so_huu is None
        assert du
        q.bao_ram(ma)
    else:
        assert kho._ban_ghi is None and du == {}


@pytest.mark.parametrize('cot', ['module', 'nguoi_gui', 'tai_lieu', 'vung', 'phien'])
def test_sai_quyen_khong_don_map_dung(cot):
    q, dh, kho, v, ma = ghep()
    du = cho_ai(kho, v)
    vmo = viec_mo(q, ma)
    ctx = q.ve[vmo.id, 'mo_che']
    q.ve[vmo.id, 'mo_che'] = replace(ctx, **{cot: 'THAT' if cot == 'vung' else 'khac-DEMO'})
    # QuyenNganDemo thay module/người/tài liệu/vùng theo nguồn phiên hiện tại.
    cu = getattr(q, cot, None)
    if cot != 'phien':
        setattr(q, cot, 'THAT' if cot == 'vung' else 'khac-DEMO')
    loi('MASK_MA_YEU_CAU', lambda: mo(kho, q, ma, vmo))
    assert du
    q.ve[vmo.id, 'mo_che'] = ctx
    if cot != 'phien':
        setattr(q, cot, cu)
    assert mo(kho, q, ma, vmo) == TEN and du == {}


def test_sai_phap_nhan_nguon_thieu_va_payload_khong_tu_cap_quyen():
    q, dh, kho, v, ma = ghep()
    du = cho_ai(kho, v)
    vmo = viec_mo(q, ma)
    vmo.ngu_canh.update(phap_nhan_id='tu-khai-DEMO', module='tu-khai-DEMO')
    q.ram_phap_nhan = 'khac-DEMO'
    loi('MASK_MA_YEU_CAU', lambda: mo(kho, q, ma, vmo))
    assert du
    q.ram_phap_nhan = ''
    loi('MASK_NGU_CANH_CHUA_XAC_MINH', lambda: mo(kho, q, ma, vmo))
    q.ram_phap_nhan = 'pn-demo'
    assert mo(kho, q, ma, vmo) == TEN


@pytest.mark.parametrize('thay', ['instance', 'phien_ram'])
def test_khac_instance_restart_khong_cuu_map(thay):
    q, dh, kho, v, ma = ghep()
    du = cho_ai(kho, v)
    vmo = viec_mo(q, ma)
    q.ram_sua_ctx = lambda c: replace(c, **{thay: 'khac-DEMO'})
    loi(THIEU, lambda: mo(kho, q, ma, vmo))
    q.ram_sua_ctx = lambda c: c
    kho_moi = KhoAnhXaRAM(quyen=q, dong_ho=dh, hen_gio=dh.hen_gio)
    loi(THIEU, lambda: mo(kho_moi, q, ma, vmo))
    loi(THIEU, lambda: cho_ai(kho_moi, v))
    assert du and mo(kho, q, ma, vmo) == TEN


def test_retry_doi_dau_vao_ket_thuc_map_khong_truot_ttl():
    q, dh, kho, v, ma = ghep()
    du = cho_ai(kho, v)
    v.dau_vao['van_ban'] += ' DEMO đổi'
    loi('MASK_DAU_VAO_THAY_DOI', lambda: cho_ai(kho, v))
    assert du == {} and dh.hen[0].da_huy
    loi(THIEU, lambda: mo(kho, q, ma))


def test_hai_chuoi_khong_day_map_cu_va_su_kien_sai_khong_don():
    q, dh, kho, v, ma = ghep()
    du = cho_ai(kho, v)
    v2 = viec_demo('khac-DEMO'); v2.cau_hinh = {}
    ctx2 = q.cap(v2.id)
    loi('MASK_CHUOI_DANG_XU_LY', lambda: cho_ai(kho, v2))
    for cot, moi in [('phap_nhan_id', 'khac-DEMO'), ('instance', 'khac-DEMO'), ('phien_ram', 'khac-DEMO')]:
        q.bao_ram(ma, **{cot: moi})
        assert du
    q.bao_ram(ctx2.ma_yeu_cau)
    kho.nhan_su_kien({'ma_yeu_cau': ma, 'ket_thuc': 'HUY'})
    assert du and mo(kho, q, ma) == TEN


def test_hai_open_dong_thoi_chi_mot_so_huu_khong_giu_khoa_khi_cho_ai():
    q, dh, kho, v, ma = ghep()
    du = cho_ai(kho, v)
    vmo = viec_mo(q, ma)
    vao, ra, ket_qua = Event(), Event(), []
    def mot():
        with kho.buoc(vmo, loai='mo_che', ma_yeu_cau=ma) as b:
            vao.set()
            assert ra.wait(5)
            ket_qua.append(b.du_lieu['anh_xa'][ALIAS])
    t = Thread(target=mot)
    t.start()
    try:
        assert vao.wait(5)
        loi('MASK_BUOC_DANG_XU_LY', lambda: mo(kho, q, ma, vmo))
        assert du
    finally:
        ra.set(); t.join(5)
    assert not t.is_alive() and ket_qua == [TEN] and du == {}
    loi(THIEU, lambda: mo(kho, q, ma, vmo))


@pytest.mark.parametrize('cach', ['timer', 'HUY', 'LOI', 'MAT_LEASE'])
def test_timeout_huy_dua_mo_khong_phat_hanh_ban_ro(cach):
    q, dh, kho, v, ma = ghep(ttl=60)
    du = cho_ai(kho, v)
    vao, ra, ket_qua, loi_ra = Event(), Event(), [], []
    vmo = viec_mo(q, ma)
    def mo_cham():
        try:
            with kho.buoc(vmo, loai='mo_che', ma_yeu_cau=ma) as b:
                du_kien = b.du_lieu['anh_xa'][ALIAS]
                vao.set()
                assert ra.wait(5)
            ket_qua.append(du_kien)
        except LoiNghiepVu as exc:
            loi_ra.append(exc.ma)
    t = Thread(target=mo_cham)
    t.start()
    try:
        assert vao.wait(5)
        if cach == 'timer':
            dh.tien(60)
        else:
            q.bao_ram(ma, cach)
        assert du == {}
    finally:
        ra.set(); t.join(5)
    assert not t.is_alive() and ket_qua == [] and loi_ra == [THIEU]


def test_quyen_thu_hoi_khi_dang_mo_finally_don():
    q, dh, kho, v, ma = ghep()
    du = cho_ai(kho, v)
    with pytest.raises(LoiNghiepVu):
        with kho.buoc(viec_mo(q, ma), loai='mo_che', ma_yeu_cau=ma) as b:
            _ = b.du_lieu['anh_xa'][ALIAS]
            q.thu_hoi = True
    assert du == {} and kho._ban_ghi is None


def test_huy_truoc_nhan_buoc_mo_van_don_map_dung():
    q, dh, kho, v, ma = ghep()
    du = cho_ai(kho, v)
    vmo = viec_mo(q, ma)
    def huy():
        raise ViecDaHuy()
    vmo.kiem_huy = huy
    with pytest.raises(ViecDaHuy):
        mo(kho, q, ma, vmo)
    assert du == {} and kho._ban_ghi is None


def test_huy_sau_kiem_cuoi_truoc_chot_van_chan_output():
    q, dh, kho, v, ma = ghep()
    du = cho_ai(kho, v)
    ket_qua = []
    with pytest.raises(LoiNghiepVu) as exc:
        with kho.buoc(viec_mo(q, ma), loai='mo_che', ma_yeu_cau=ma) as b:
            du_kien = b.du_lieu['anh_xa'][ALIAS]
            kiem = b.kiem
            def kiem_roi_huy():
                kiem()
                q.bao_ram(ma)
            b.kiem = kiem_roi_huy
        ket_qua.append(du_kien)
    assert exc.value.ma == THIEU and ket_qua == [] and du == {}


def test_tin_hieu_huy_dua_khoi_tao_khong_tao_lai_map():
    q, dh, kho, v, ma = ghep()
    xac_minh = q.xac_minh_ram
    def nhan_roi_huy(*a, **kw):
        ctx = xac_minh(*a, **kw)
        q.bao_ram(ma)
        return ctx
    q.xac_minh_ram = nhan_roi_huy
    loi(THIEU, lambda: cho_ai(kho, v))
    assert kho._ban_ghi is None and dh.hen == []


def test_dang_ky_cong_nhan_su_kien_luong_khac_khong_deadlock():
    q, dh, kho, v, ma = ghep()
    dang_ky = q.dang_ky_vong_doi_ram
    da_bao = Event()
    def dang_ky_va_bao(ham, *, phien_ram):
        ghim = dang_ky(ham, phien_ram=phien_ram)
        ctx = NguCanhRAM(q.ve[v.id, 'che'], 'pn-demo', ghim.instance, phien_ram, None)
        def bao():
            ham(SuKienRAM(ctx, 'HUY'))
            da_bao.set()
        t = Thread(target=bao, daemon=True)
        t.start()
        assert da_bao.wait(5)
        t.join(5)
        return ghim
    q.dang_ky_vong_doi_ram = dang_ky_va_bao
    loi(THIEU, lambda: cho_ai(kho, v))
    assert da_bao.is_set() and kho._ban_ghi is None and dh.hen == []


def test_mo_chuoi_cu_khong_don_map_chuoi_moi():
    q, dh, kho, v, ma = ghep()
    cho_ai(kho, v)
    assert mo(kho, q, ma) == TEN
    v2 = viec_demo('chuoi-moi-DEMO'); v2.cau_hinh = {}
    q.cap(v2.id)
    moi = cho_ai(kho, v2)
    loi(THIEU, lambda: mo(kho, q, ma))
    q.bao_ram(ma)
    assert moi['anh_xa'][ALIAS] == TEN
    q.bao_ram(q.ve[v2.id, 'che'].ma_yeu_cau)
    assert moi == {}


def test_don_buffer_co_memoryview_khong_loi_timer():
    q, dh, kho, v, ma = ghep(ttl=60)
    with kho.buoc(v) as b:
        du = b.du_lieu
        du['bytes_goc'] = bytearray(b'DEMO')
        nhin = memoryview(du['bytes_goc'])
        b.cho_ai()
    dh.tien(60)
    assert du == {} and kho._ban_ghi is None
    nhin.release()


def test_timer_thread_don_khi_ranh_khong_can_handler_tiep_theo():
    q, dh, _, v, ma = ghep(ttl=60)
    cong, da_don = Event(), Event()
    cac_hen = []
    def hen_gio(giay, ham):
        def chay():
            try:
                assert cong.wait(5)
                ham()
            finally:
                da_don.set()
        t = Timer(0, chay)
        t.daemon = True
        cac_hen.append(t)
        return t
    kho = KhoAnhXaRAM(quyen=q, dong_ho=dh, hen_gio=hen_gio)
    du = cho_ai(kho, v)
    try:
        assert kho._ban_ghi.trang_thai == 'CHO_AI'
        dh.tien(60, chay_timer=False)
        cong.set()
        assert da_don.wait(5)
        assert du == {} and kho._ban_ghi is None
    finally:
        cong.set()
        for t in cac_hen:
            t.cancel(); t.join(5)


def test_timer_don_giua_checkpoint_va_doc_map_van_dung_ma_loi():
    q, dh, kho, v, ma = ghep(ttl=60)
    cho_ai(kho, v)
    with pytest.raises(LoiNghiepVu) as exc:
        with kho.buoc(viec_mo(q, ma), loai='mo_che', ma_yeu_cau=ma) as b:
            anh_xa = b.du_lieu['anh_xa']
            dh.tien(60)
            _ = anh_xa[ALIAS]
    assert exc.value.ma == THIEU and TEN not in str(exc.value)
    assert exc.value.__suppress_context__


def test_timer_loi_dat_lai_phai_don_khong_traceback(capsys):
    q, dh, kho, v, ma = ghep()
    du = cho_ai(kho, v)
    def hen_loi(*a, **kw):
        raise RuntimeError(TEN)
    kho._hen_gio = hen_loi
    dh.hen[0].no()  # Chạy sớm, lỗi khi đặt lại timer.
    assert du == {} and kho._ban_ghi is None
    assert capsys.readouterr() == ('', '')


@pytest.mark.parametrize('doi', [
    {'phap_nhan_id': None}, {'instance': ''}, {'phien_ram': ''},
    {'han_monotonic': float('nan')}, {'han_monotonic': float('inf')},
    {'han_monotonic': True}, {'duoc_tao': 1}, {'quyen': {}},
])
def test_nguon_ram_thieu_hay_sai_kieu_tu_choi(doi):
    q, dh, kho, v, ma = ghep()
    q.ram_sua_ctx = lambda c: replace(c, **doi)
    loi('MASK_NGU_CANH_CHUA_XAC_MINH', lambda: cho_ai(kho, v))
    assert kho._ban_ghi is None and dh.hen == []


def test_su_kien_sai_module_nguoi_tai_lieu_khong_don_map_khac():
    q, dh, kho, v, ma = ghep()
    du = cho_ai(kho, v)
    for cot in ('module', 'nguoi_gui', 'tai_lieu', 'vung', 'phien', 'ma_yeu_cau'):
        cu = q.ram_ctx[ma]
        ngu_canh = replace(cu, quyen=replace(cu.quyen, **{cot: 'THAT' if cot == 'vung' else 'khac-DEMO'}))
        kho.nhan_su_kien(SuKienRAM(ngu_canh, 'HUY'))
        assert du
    for ket_thuc in ({}, [], True, None, 'KHONG_BIET'):
        kho.nhan_su_kien(SuKienRAM(q.ram_ctx[ma], ket_thuc))
        assert du
    assert mo(kho, q, ma) == TEN


@pytest.mark.parametrize('cot', ['instance', 'phien_ram'])
def test_doi_instance_khi_dang_mo_don_va_yeu_cau_chay_lai(cot):
    q, dh, kho, v, ma = ghep()
    du = cho_ai(kho, v)
    with pytest.raises(LoiNghiepVu) as exc:
        with kho.buoc(viec_mo(q, ma), loai='mo_che', ma_yeu_cau=ma) as b:
            _ = b.du_lieu['anh_xa'][ALIAS]
            q.ram_sua_ctx = lambda c: replace(c, **{cot: 'khac-DEMO'})
    assert exc.value.ma == THIEU and du == {}


def test_khong_io_log_hay_xuat_map_trong_repr(monkeypatch, capsys):
    import builtins
    import logging
    from pathlib import Path
    import tempfile
    q, dh, kho, v, ma = ghep()
    def cam(*a, **kw):
        pytest.fail('Kho RAM không được lưu hoặc ghi log dữ liệu')
    with monkeypatch.context() as m:
        for lop, ten in [(builtins, 'open'), (Path, 'write_bytes'), (Path, 'write_text'),
                         (tempfile, 'TemporaryFile'), (tempfile, 'NamedTemporaryFile'),
                         (logging, 'error'), (logging, 'info'), (logging, 'exception')]:
            m.setattr(lop, ten, cam)
        du = cho_ai(kho, v)
        assert TEN not in repr(kho) + repr(kho._ban_ghi) + repr(q.ram_ctx[ma])
        assert mo(kho, q, ma) == TEN and du == {}
    assert capsys.readouterr() == ('', '')


@pytest.mark.parametrize('hong', ['quyen', 'ghim', 'thong_bao', 'phien_ram', 'xac_minh_ram'])
def test_runtime_tu_choi_thieu_cua_core_truoc_khi_doc_ghi_nghiep_vu(monkeypatch, hong):
    q = QuyenNganDemo()
    if hong == 'quyen':
        q = None
    elif hong == 'ghim':
        q.ram_ghim = False
    elif hong == 'thong_bao':
        q.ram_bao = False
    elif hong == 'phien_ram':
        q.dang_ky_vong_doi_ram = lambda *a, **k: GhimTienTrinh('instance-DEMO', 'khac-DEMO', True, True)
    else:
        q.xac_minh_ram = None
    from e_mask import phong_bi
    def cam(*a, **kw):
        pytest.fail('Không được đi vào nghiệp vụ khi chưa có ghim/lifecycle')
    monkeypatch.setattr(phong_bi, 'doc_che', cam)
    app = tao_app(quyen=q)
    kq = CoreGia().chay_thu(app, 'mask.che_van_ban@1', {'loai': 'van_ban', 'van_ban': VAN_BAN})
    assert kq['trang_thai'] == 'LOI' and kq['ket_qua'] is None
    assert kq['loi']['ma'] == ('MASK_NGU_CANH_CHUA_XAC_MINH' if q is None else 'MASK_CHUOI_CHUA_GHIM')


def test_core_gia_cho_ai_huy_restart_khong_luu_map_ra_cong(monkeypatch, capsys):
    q, dh, kho, v, ma = ghep()
    app = tao_app(quyen=q)
    app.kho_anh_xa_ram = kho
    # Chỉ test R4: adapter nối API kho mới; R5/R6 mới thay handler nghiệp vụ.
    def che(viec):
        cho_ai(kho, viec)
        ctx = q.ve[viec.id, 'che']
        return {'loai': 'van_ban_da_che', 'van_ban_da_che': dict(
            phien_ban=1, van_ban=ALIAS, ma_yeu_cau=ctx.ma_yeu_cau,
            con_sot=[], kiem_tien_ngay=True, chuyen_tiep={})}
    monkeypatch.setitem(app._ham, 'mask.che_van_ban@1', che)
    core = CoreGia(app)
    ma_viec = core.giao_viec('mask.che_van_ban@1', {'loai': 'van_ban', 'van_ban': VAN_BAN})
    ctx = q.cap(ma_viec)
    core.chay(app)
    kq = core.xem(ma_viec)
    assert kq['trang_thai'] == 'XONG'
    du = kho._ban_ghi.du_lieu
    q.bao_ram(ctx.ma_yeu_cau, 'HUY')  # Không còn handler Mask đang chạy.
    assert du == {}
    loi(THIEU, lambda: mo(kho, q, ctx.ma_yeu_cau))
    assert all(core.xem_ngan(app.ma, bang) == [] for bang in ['dinh_danh', 'bi_danh'])
    xuat = json.dumps([kq, core.nhat_ky], ensure_ascii=False)
    assert TEN not in xuat and 'anh_xa' not in xuat and 'bytes_goc' not in xuat
    assert capsys.readouterr() == ('', '')
