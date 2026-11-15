"""MASK-R6: đã kiểm bằng Core giả (CoreGia), không Cloud/Core thật."""
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiDuongTruyen, LoiNghiepVu, NganEngine, ViecDaHuy

from e_mask import che_van_ban, mo_che_ram
from e_mask.chay import tao_app
from e_mask.kho_anh_xa_ram import KhoAnhXaRAM
from ho_tro_mo_ram import ALIAS, TEN, DUOI, MO, bo, giao, chay, ket
from ho_tro_ngan import ai_demo


def loi(b, ma='MASK_MO_CHE_KHONG_DAY_DU'):
    k = chay(b)
    assert k['trang_thai'] == 'LOI' and k['ket_qua'] is None, k
    assert k['loi']['ma'] == ma, k
    assert TEN not in json.dumps(k, ensure_ascii=False)
    return k


def da_don(b):
    assert b.ram._ban_ghi is None
    assert len(b.da_don) == len(set(b.da_don)) == 1
    assert not hasattr(b.ram, 'ket_qua')
    assert not hasattr(b.app, 'kho_bi_danh_ram')


def test_du_truong_ai_giu_khoa_kieu_noi_dung_moi_va_tinh_lai_trich():
    b = bo()
    ai = ai_demo(b.m.da_che + ' AI thêm [ghi chú], 42.5, 2026-11-16.', b.ctx.ma_yeu_cau)
    ai['du_lieu'] = {ALIAS: [{'ten': ALIAS, 'so': 42.5, 'ngay': '2026-10-30',
                             'tien': {'so': 1000000, 'tien_te': 'VND'}, 'co': True, 'rong': None,
                             'can_cu': {'cau': ALIAS, 'bat_dau': 0, 'ket_thuc': len(ALIAS)}}]}
    ai['trich_dan'] = [{'cau': ALIAS, 'bat_dau': 0, 'ket_thuc': len(ALIAS)}]
    ai['chuyen_tiep']['tham_chieu_demo'] = 'opaque-DEMO'
    cu = deepcopy(ai)
    giao(b, ai=ai)
    k = ket(b)
    moi = json.loads(k['tra_loi_ai_da_mo_json'])
    assert k['van_ban_da_mo_che'] == TEN + DUOI + ' AI thêm [ghi chú], 42.5, 2026-11-16.'
    assert k['so_cho_mo'] == 4 and k['mo_day_du'] is True
    assert k['trang_thai_ma_yeu_cau'] == 'DA_DONG' and k['bi_danh_khong_ro_json'] == '[]'
    muc = moi['du_lieu'][ALIAS][0]
    assert muc['ten'] == TEN and type(muc['so']) is float and muc['so'] == 42.5
    assert muc['tien'] == {'so': 1000000, 'tien_te': 'VND'}
    assert muc['ngay'] == '2026-10-30' and muc['co'] is True and muc['rong'] is None
    for trich in (muc['can_cu'], moi['trich_dan'][0]):
        assert trich == {'cau': TEN, 'bat_dau': 0, 'ket_thuc': len(TEN), 'can_kiem_lai': True}
    assert moi['trang_thai'] == 'khong_thay_can_cu' and moi['kiem_trich_dan']['dat'] is False
    for ten in ('phien_ban', 'model', 'nha_cung_cap', 'ma_prompt', 'phien_ban_prompt',
                'phien_ban_engine', 'bam_dau_vao', 'ly_do_chon_model', 'chuyen_tiep'):
        assert moi[ten] == cu[ten]
    assert ai == cu and mo_che_ram.CHUYEN_QUY_TRINH in moi['canh_bao']
    assert any(mo_che_ram.CHUYEN_QUY_TRINH in str(v) for v in b.c.xem(b.v)['tien_do'])
    assert b.cong.da_tieu_thu == [True]
    da_don(b)


@pytest.mark.parametrize('alias', [ALIAS, ALIAS.lower(), '[ [ MASKCT-DEMO-0001 ] ]',
    '[\n[ MASKCT-DEMO-0001 ]\t]', ' '.join(ALIAS), '\u00a0'.join(ALIAS)])
def test_case_space_mem_chi_trong_map_duy_nhat(alias):
    b = bo()
    giao(b, chu='Mới: ' + alias + ' và 1.000.000 VND, ngày 2026-10-30.')
    k = ket(b)
    assert k['van_ban_da_mo_che'] == 'Mới: ' + TEN + ' và 1.000.000 VND, ngày 2026-10-30.'
    da_don(b)


@pytest.mark.parametrize('ten', ['Co\u0302ng ty DEMO A\u0301nh Du\u031bo\u031bng',
                               'Công\u200b ty DEMO Ánh Dương', 'Công ty  DEMO\u00a0Ánh Dương'])
def test_nguyen_van_nfd_cf_khoang_trang_khong_chuan_hoa(ten):
    b = bo(goc=ten + DUOI, phep=[(0, len(ten), ALIAS)])
    giao(b, chu=ALIAS + ' AI mới\u200b, 73.')
    assert ket(b)['van_ban_da_mo_che'] == ten + ' AI mới\u200b, 73.'
    da_don(b)


@pytest.mark.parametrize('hong', ['[[MASKCT-NGOAI-0002]]', '[[KH-NGOAI-009]]', '[[KH-LA]]',
    '[[MASKCT-DEMO-0001]', '[MASKCT-DEMO-0001]]', 'MASKCT-DEMO-0001',
    'MASKCT-DEMO-000?', '[[MASKCT-DEMO-000?]]', '[[MASKCT-DEMO-0001',
    '[[MASKCT-DEMO-0001]]]', '[[[MASKCT-DEMO-0001]]', '[[MASKCT-0002]]',
    '[[MASKCT-DEMO-0001\u200b]]', 'M A S K C T - D E M O - 0 0 0 2'])
@pytest.mark.parametrize('noi', ['tra_loi', 'du_lieu', 'trich_dan'])
def test_alias_la_hong_thieu_khong_tra_mot_phan(hong, noi, capsys):
    b = bo()
    ai = ai_demo(ALIAS, b.ctx.ma_yeu_cau)
    if noi == 'tra_loi':
        ai['tra_loi'] += ' ' + hong
    elif noi == 'du_lieu':
        ai['du_lieu'] = {'l1': [None, {'l2': hong}]}
    else:
        ai['trich_dan'] = [{'cau': hong, 'bat_dau': 0, 'ket_thuc': len(hong)}]
    giao(b, ai=ai)
    loi(b)
    da_don(b)
    assert b.cong.so_nhan == 0 and b.c.ket_qua_cuoi_demo == {}
    assert capsys.readouterr() == ('', '')


def test_alias_chinh_thuc_ngoai_yeu_cau_khong_doc_kho_hoac_nguon(monkeypatch):
    b = bo()
    def cam(*a, **kw):
        pytest.fail('Không được tìm ngăn hoặc đọc nguồn để gỡ che.')
    monkeypatch.setattr(NganEngine, 'doc', cam)
    monkeypatch.setattr(NganEngine, 'tim', cam)
    # Tham chiếu cũ biết được cũng không thể là nguồn phục hồi.
    ai = ai_demo(ALIAS + ' [[KH-NGOAI-009]]', b.ctx.ma_yeu_cau)
    ai['chuyen_tiep']['ho_so'] = {'tep_id': 'nguon-DEMO'}
    giao(b, ai=ai)
    loi(b)
    da_don(b)


@pytest.mark.parametrize('hong', ['them_alias', 'thieu_alias', 'gia_tri_list', 'map_hong', 'nhieu_nguyen_van'])
def test_map_hong_hoac_mo_ho_chan_toan_bo(hong):
    if hong == 'nhieu_nguyen_van':
        goc = TEN + ' / ' + TEN.upper()
        b = bo(goc=goc, phep=[(0, len(TEN), ALIAS), (len(TEN)+3, len(goc), ALIAS)], aliases={ALIAS: TEN})
    else:
        b = bo()
        v = b.ram._ban_ghi.du_lieu
        if hong == 'them_alias': v['alias_nguyen_van']['[[KH-NGOAI-009]]'] = 'Tên DEMO ngoài'
        elif hong == 'thieu_alias': v['alias_nguyen_van'].clear()
        elif hong == 'gia_tri_list': v['alias_nguyen_van'][ALIAS] = [TEN, TEN.upper()]
        else: v['anh_xa_cuoi'] = replace(b.m, bam_da_che='sha256:' + '0'*64)
    giao(b)
    loi(b)
    da_don(b)


def test_cung_ma_mem_hai_nguyen_van_khong_chon_ten_dau():
    goc = TEN + ' / ' + TEN.upper()
    b = bo(goc=goc, phep=[(0, len(TEN), ALIAS), (len(TEN)+3, len(goc), ALIAS.lower())])
    giao(b, chu=ALIAS)
    loi(b)
    da_don(b)


def test_cau_trich_lap_dung_vi_tri_va_cau_khong_doi_cung_duoc_tinh_lai():
    goc = TEN + ' / ' + TEN + '; phần DEMO.'
    b = bo(goc=goc, phep=[(0, len(TEN), ALIAS), (len(TEN)+3, 2*len(TEN)+3, ALIAS)])
    sau = len(ALIAS) + 3
    cau = 'phần DEMO'
    a = b.m.da_che.index(cau)
    ai = ai_demo(ALIAS, b.ctx.ma_yeu_cau)
    ai['trich_dan'] = [{'cau': ALIAS, 'bat_dau': sau, 'ket_thuc': sau+len(ALIAS)},
                       {'cau': cau, 'bat_dau': a, 'ket_thuc': a+len(cau)}]
    giao(b, ai=ai)
    trich = json.loads(ket(b)['tra_loi_ai_da_mo_json'])['trich_dan']
    assert (trich[0]['bat_dau'], trich[0]['ket_thuc']) == (len(TEN)+3, 2*len(TEN)+3)
    assert trich[1]['bat_dau'] == goc.index(cau)
    assert all(goc[t['bat_dau']:t['ket_thuc']] == t['cau'] for t in trich)
    da_don(b)


def test_trich_khong_xac_dinh_duoc_vi_tri_bo_offset_cu():
    goc = TEN + ' / ' + TEN
    b = bo(goc=goc, phep=[(0,len(TEN),ALIAS), (len(TEN)+3,len(goc),ALIAS)])
    ai = ai_demo(ALIAS, b.ctx.ma_yeu_cau)
    ai['trich_dan'] = [{'cau': ALIAS.lower(), 'bat_dau': 987, 'ket_thuc': 999}]
    giao(b, ai=ai)
    moi = json.loads(ket(b)['tra_loi_ai_da_mo_json'])
    assert moi['trich_dan'][0] == {'cau': TEN, 'bat_dau': None, 'ket_thuc': None, 'can_kiem_lai': True}
    assert moi['kiem_trich_dan']['dat'] is False
    da_don(b)


def test_ai_khong_nhac_alias_khong_bat_buoc_tra_het_ten():
    b = bo()
    ai = ai_demo('AI thêm 42.5 và 2026-10-30.', b.ctx.ma_yeu_cau)
    giao(b, ai=ai, dong=True)
    k = ket(b)
    assert json.loads(k['tra_loi_ai_da_mo_json']) == ai
    assert k['so_cho_mo'] == 0
    da_don(b)


@pytest.mark.parametrize('dong', [False, True])
def test_mau3_dong_viec_khong_giu_map_va_co_thong_bao(dong):
    b = bo()
    giao(b, mau3=dict(van_ban=ALIAS, ma_yeu_cau=b.ctx.ma_yeu_cau, dong_viec=dong))
    k = ket(b)
    assert k['van_ban_da_mo_che'] == TEN and k['tra_loi_ai_da_mo_json'] is None
    assert k['trang_thai_ma_yeu_cau'] == 'DA_DONG'
    assert any(mo_che_ram.CHUYEN_QUY_TRINH in str(v) for v in b.c.xem(b.v)['tien_do']) is (not dong)
    da_don(b)


def test_replay_khong_tao_map_hoac_cache_ban_ro():
    b = bo()
    giao(b)
    ket(b)
    giao(b)
    loi(b, 'MASK_ANH_XA_KHONG_CON')
    da_don(b)
    assert b.cong.so_nhan == 1


@pytest.mark.parametrize('sai', ['module','nguoi_gui','tai_lieu','vung','phap_nhan','instance'])
def test_sai_quyen_khong_mo_khong_don_map_nguoi_khac(sai):
    b = bo()
    giao(b)
    if sai in {'module','nguoi_gui','tai_lieu'}: setattr(b.q, sai, 'khac-DEMO')
    elif sai == 'vung': b.q.vung = 'THAT'
    elif sai == 'phap_nhan': b.q.ram_sua_ctx = lambda ctx: replace(ctx, phap_nhan_id='pn-khac-DEMO')
    else: b.q.ram_sua_ctx = lambda ctx: replace(ctx, instance='instance-khac-DEMO')
    loi(b, 'MASK_ANH_XA_KHONG_CON' if sai == 'instance' else 'MASK_MA_YEU_CAU')
    assert b.ram._ban_ghi is not None and not b.da_don
    assert b.cong.so_nhan == 0
    b.dh.tien(601)
    da_don(b)


@pytest.mark.parametrize('ly_do', ['restart','ttl','khac_instance','huy_ranh','loi_ranh','mat_lease_ranh'])
def test_mat_ram_khong_phuc_hoi_tu_nguon_hoac_ngan(ly_do):
    b = bo()
    if ly_do == 'restart':
        b.app = tao_app(quyen=b.q, cong_mo_che=b.cong)
    elif ly_do == 'ttl': b.dh.tien(600)
    elif ly_do == 'khac_instance': b.q.ram_sua_ctx = lambda ctx: replace(ctx, instance='khac-DEMO')
    else: b.q.bao_ram(b.ctx.ma_yeu_cau, {'huy_ranh':'HUY','loi_ranh':'LOI','mat_lease_ranh':'MAT_LEASE'}[ly_do])
    giao(b)
    loi(b, 'MASK_ANH_XA_KHONG_CON')
    assert b.cong.so_nhan == 0
    b.dh.tien(601)
    da_don(b)


@pytest.mark.parametrize('moc', ['vao', 'nhan', 'ra'])
@pytest.mark.parametrize('su_kien', ['HUY','LOI','MAT_LEASE','MAT_QUYEN','TTL'])
def test_terminal_dua_ban_giao_khong_phat_hanh(moc, su_kien):
    b = bo()
    def chen(ten, v):
        if ten == moc:
            if su_kien == 'TTL': b.dh.tien(600)
            else: b.q.bao_ram(b.ctx.ma_yeu_cau, su_kien)
            if moc == 'ra' and su_kien != 'TTL': b.q.thu_hoi = True
    b.cong.moc = chen
    giao(b)
    k = chay(b)
    assert k['trang_thai'] == 'LOI' and k['ket_qua'] is None
    assert b.c.ket_qua_cuoi_demo == {}
    da_don(b)


@pytest.mark.parametrize('mat_ack', ['nhan','ra'])
def test_mat_ack_chua_ro_khong_cache_khong_mo_lai(mat_ack):
    b = bo()
    b.cong.mat_ack = mat_ack
    giao(b)
    k = chay(b)
    assert k['trang_thai'] == 'CHUA_RO' and k['ket_qua'] is None
    assert k['ma_tuong_quan'] == 'mask-mo-' + sha256(b.q.ve[b.v,'mo_che'].ma_luot.encode()).hexdigest()
    assert 'chuoi-tu-nguon' not in json.dumps(k)
    da_don(b)
    if mat_ack == 'ra':
        assert len(b.c.ket_qua_cuoi_demo) == 1  # Chỉ Core giữ kết quả đã nhận.
    giao(b)
    loi(b, 'MASK_ANH_XA_KHONG_CON')
    assert b.cong.so_nhan == 1


@pytest.mark.parametrize('tra', [False, None, {'da_luu': True}])
def test_ban_giao_khong_xac_nhan_khong_thanh_cong_gia(tra):
    b = bo()
    b.cong.tra = tra
    giao(b)
    loi(b, 'MASK_MO_CHE_CHUA_CO_CUA_CORE')
    da_don(b)
    assert b.c.ket_qua_cuoi_demo == {}


def test_thieu_cua_ban_giao_don_map_va_chan():
    b = bo()
    b.cong.ban_giao_cuoi = None
    giao(b)
    loi(b, 'MASK_MO_CHE_CHUA_CO_CUA_CORE')
    da_don(b)


@pytest.mark.parametrize('hong', ['ma_khac','ma_thieu','dong_sai','du_lieu_sai'])
def test_loi_parse_trong_quyen_so_huu_van_don_map(hong):
    b = bo()
    ai = ai_demo(ALIAS, b.ctx.ma_yeu_cau)
    if hong == 'ma_khac': ai['chuyen_tiep']['ma_yeu_cau'] = 'khac-DEMO'
    elif hong == 'ma_thieu': ai['chuyen_tiep'].clear()
    elif hong == 'du_lieu_sai': ai['du_lieu'] = ['khong-la-object']
    if hong == 'dong_sai':
        giao(b, mau3=dict(van_ban=ALIAS, ma_yeu_cau=b.ctx.ma_yeu_cau, dong_viec=1))
    else: giao(b, ai=ai)
    loi(b, 'MASK_MA_YEU_CAU' if hong.startswith('ma_') else 'MASK_DAU_VAO')
    da_don(b)


def test_ngoai_le_chua_du_lieu_khong_ro_log_stderr(monkeypatch, capsys):
    b = bo()
    def hong(ten, v):
        if ten == 'nhan': raise LoiNghiepVu('MA_LA', TEN + ' duong-may-DEMO')
    b.cong.moc = hong
    giao(b)
    loi(b, 'MASK_MA_YEU_CAU')
    da_don(b)
    assert TEN not in json.dumps(b.c.nhat_ky, ensure_ascii=False)
    assert capsys.readouterr() == ('','')


def test_cua_mo_cu_khong_nhan_kho_tra_nguoc():
    class KhoCam:
        def __getattr__(self, _): pytest.fail('Không được truy cập kho tra ngược.')
    with pytest.raises(LoiNghiepVu) as exc:
        che_van_ban.mo_che(ALIAS, 'yeu-cau-DEMO', KhoCam())
    assert exc.value.ma == 'MASK_ANH_XA_KHONG_CON'


def test_phieu_nhan_tra_giu_nguyen():
    p = tao_app().phieu
    m = next(n for n in p['nang_luc'] if n['ma'] == MO)
    assert m['nhan'] == ['tra_loi_ai','tep'] and m['tra'] == 'truong'
    assert {t['ma'] for t in m['truong_ra']} == {'van_ban_da_mo_che','so_cho_mo',
        'bi_danh_khong_ro_json','mo_day_du','trang_thai_ma_yeu_cau','tra_loi_ai_da_mo_json'}


def test_che_cu_khong_phat_hanh_map_bang_ngan_lich_su():
    from ho_tro_ngan import QuyenNganDemo
    from kho_tri_thuc_sdk.thu import CoreGia
    q = QuyenNganDemo()
    app = tao_app(quyen=q)
    c = CoreGia(app)
    v = c.giao_viec('mask.che_van_ban@1', {'loai':'van_ban','van_ban':TEN+DUOI})
    q.cap(v)
    c.chay(app)
    k = c.xem(v)
    assert k['trang_thai'] == 'LOI' and k['loi']['ma'] == 'MASK_R3_CHUA_CHUNG_MINH'
    assert app.kho_anh_xa_ram._ban_ghi is None
    assert all(c.xem_ngan('e_mask', t) == [] for t in ('dinh_danh','bi_danh','ma_yeu_cau','dau_gap'))


def test_noi_handler_r5_that_dung_cung_kho_r4_den_mo_che():
    from types import SimpleNamespace
    from kho_tri_thuc_sdk.thu import CoreGia
    from e_mask import chuan_bi_ai as cb
    from ho_tro_mask_r5 import CongRAMCoreGia, giao as giao_local
    from ho_tro_mo_ram import CongMoCoreGia
    from ho_tro_ngan import QuyenNganDemo
    from ho_tro_ram import DongHoGia
    from test_mask_r2 import _dong, _them
    q, dh, local = QuyenNganDemo(), DongHoGia(), CongRAMCoreGia()
    cuoi = CongMoCoreGia(q, dh)
    app = tao_app(quyen=q, cong_chuan_bi_ai=local, cong_hau_kiem_ai=local, cong_mo_che=cuoi)
    app.kho_anh_xa_ram = ram = KhoAnhXaRAM(quyen=q, dong_ho=dh, hen_gio=dh.hen_gio)
    c = CoreGia(app)
    c.ket_qua_cuoi_demo = {}
    cuoi.core, cuoi.ram = c, ram
    # Chỉ nạp catalogue đã duyệt qua ngăn SDK thật; không thay handler R5.
    that = app._ham[cb.NANG_LUC]
    ban_chieu = []
    def seed(v):
        d = _dong(TEN, trang_thai='CHINH_THUC')
        d['nhom'] = 'CONG_TY'
        _them(v, d, ALIAS)
        ban_chieu.extend(v.ngan.tim('dinh_danh').danh_sach)
        return that(v)
    app._ham[cb.NANG_LUC] = seed
    chu = TEN + DUOI
    v = c.giao_viec(cb.NANG_LUC, {'loai':'van_ban','van_ban':chu})
    ctx = q.cap(v)
    b = SimpleNamespace(c=c, q=q, dh=dh, ram=ram, app=app, cong=local, v=v, ctx=ctx, chu=chu)
    c.chay(app)
    assert c.xem(v)['trang_thai'] == 'XONG', c.xem(v)
    giao_local(b, [(0,len(TEN),'to_chuc','chac')])
    c.chay(app)
    k = c.xem(b.v)
    assert k['trang_thai'] == 'XONG', k
    assert ram._ban_ghi.du_lieu['giai_doan_ai'] == 'DA_HAU_KIEM'
    b.m = ram._ban_ghi.du_lieu['anh_xa_cuoi']
    giao(b, chu=k['ket_qua']['van_ban_da_che']['van_ban'] + ' AI thêm.')
    assert ket(b)['van_ban_da_mo_che'] == chu + ' AI thêm.'
    assert ram._ban_ghi is None and cuoi.da_tieu_thu == [True]
    assert not c._tep
    assert c.xem_ngan('e_mask','ma_yeu_cau') == []
    assert c.xem_ngan('e_mask','dau_gap') == []
    assert ban_chieu and all(r.gia_tri['gia_tri_goc'] is None and r.gia_tri['gia_tri_goc_da_ma_hoa']
                            for r in ban_chieu)


@pytest.mark.parametrize('buoc', ['LOP_1','CHO_LOCAL'])
def test_chua_hau_kiem_khong_duoc_mo_som(buoc):
    b = bo()
    b.ram._ban_ghi.du_lieu['giai_doan_ai'] = buoc
    giao(b)
    loi(b, 'MASK_VONG_DOI_KHONG_HOP_LE')
    da_don(b)


def test_khong_mo_nguon_khong_ghi_tep_ban_ro_khi_thanh_cong(monkeypatch, capsys):
    from kho_tri_thuc_sdk.engine import Viec
    b = bo()
    giao(b)
    def cam(*a, **kw):
        pytest.fail('Không được tải nguồn, snapshot hoặc ghi tệp để mở che.')
    monkeypatch.setattr(Viec, 'mo_tep', cam)
    monkeypatch.setattr(Viec, 'tai_tep_ra', cam)
    monkeypatch.setattr(NganEngine, 'doc', cam)
    monkeypatch.setattr(NganEngine, 'tim', cam)
    assert ket(b)['van_ban_da_mo_che'] == TEN + DUOI
    da_don(b)
    assert not b.c._tep
    assert TEN not in json.dumps(b.c.nhat_ky, ensure_ascii=False)
    assert capsys.readouterr() == ('','')


@pytest.mark.parametrize('su_kien', ['huy_sdk', 'loi_ngoai_y_muon', 'het_han'])
def test_dung_giua_luc_thay_chu_khong_ra_mot_phan(monkeypatch, su_kien):
    b = bo()
    that = mo_che_ram._MoChu.mo
    def chen(self, chu):
        k = that(self, chu)
        if su_kien == 'huy_sdk': raise ViecDaHuy()
        if su_kien == 'loi_ngoai_y_muon': raise ValueError(TEN)
        b.dh.tien(600)
        return k
    monkeypatch.setattr(mo_che_ram._MoChu, 'mo', chen)
    giao(b)
    k = chay(b)
    assert k['trang_thai'] == ('HUY' if su_kien == 'huy_sdk' else 'LOI')
    assert k['ket_qua'] is None and b.cong.so_nhan == 0
    da_don(b)


@pytest.mark.parametrize('thao_tac', ['ket_qua','ket_thuc'])
def test_sdk_gui_lai_ack_khong_goi_mo_lan_hai(thao_tac):
    b = bo()
    b.c.gay_mat_xac_nhan(thao_tac, so_lan=1)
    giao(b)
    assert ket(b)['van_ban_da_mo_che'] == TEN + DUOI
    assert b.cong.so_nhan == 1
    da_don(b)


def test_vuot_tran_sau_mo_tu_choi_khong_cat_ngam():
    b = bo()
    giao(b, chu=ALIAS + 'a' * (500000-len(ALIAS)))
    loi(b, 'MASK_QUA_GIOI_HAN')
    da_don(b)


@pytest.mark.parametrize('kieu', ['duong_truyen','timeout'])
def test_mat_phan_hoi_sau_nhan_chua_ro_va_thong_diep_khong_ro(kieu):
    b = bo()
    def chen(ten, v):
        if ten == 'nhan':
            if kieu == 'timeout': raise TimeoutError(TEN)
            raise LoiDuongTruyen('MA_DEMO', http_status=503, thu_lai_duoc=True)
    b.cong.moc = chen
    giao(b)
    k = chay(b)
    assert k['trang_thai'] == 'CHUA_RO' and k['ket_qua'] is None
    assert TEN not in json.dumps(k, ensure_ascii=False)
    da_don(b)


@pytest.mark.parametrize('moc', ['vao','nhan'])
def test_dau_vao_bi_doi_giua_ban_giao_khong_phat_hanh(moc):
    b = bo()
    def doi(ten, v):
        if ten == moc:
            v.dau_vao['tra_loi_ai']['tra_loi'] += ' thay-DEMO'
    b.cong.moc = doi
    giao(b)
    loi(b, 'MASK_DAU_VAO_THAY_DOI')
    da_don(b)
    assert b.c.ket_qua_cuoi_demo == {}


@pytest.mark.parametrize('ket_thuc', ['xong','loi','huy','chua_ro'])
def test_khong_giu_handle_hoac_map_phu_thuoc_chu_ky_gc(monkeypatch, ket_thuc):
    import gc
    import weakref
    b = bo()
    cac_mo, cac_buoc = [], []
    that = mo_che_ram._MoChu.__init__
    def ghi_nhan(self, buoc, aliases):
        that(self, buoc, aliases)
        cac_mo.append(weakref.ref(self))
        cac_buoc.append(weakref.ref(buoc))
    monkeypatch.setattr(mo_che_ram._MoChu, '__init__', ghi_nhan)
    gc.collect()
    dang_bat = gc.isenabled()
    gc.disable()
    try:
        if ket_thuc == 'loi':
            giao(b, chu=ALIAS+' [[KH-NGOAI-009]]')
        else:
            giao(b)
        if ket_thuc == 'huy':
            def huy(ten, v):
                if ten == 'nhan': raise ViecDaHuy()
            b.cong.moc = huy
        elif ket_thuc == 'chua_ro':
            b.cong.mat_ack = 'ra'
        k = chay(b)
        assert k['trang_thai'] == {'xong':'XONG','loi':'LOI','huy':'HUY','chua_ro':'CHUA_RO'}[ket_thuc]
        da_don(b)
        assert cac_mo and all(v() is None for v in cac_mo)
        assert all(v() is None for v in cac_buoc)
    finally:
        if dang_bat: gc.enable()
