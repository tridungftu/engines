"""MASK-B9: SDK, mẫu 7, ACK/quyền/cách ly; đã kiểm bằng Core giả (CoreGia)."""
from contextlib import contextmanager
from dataclasses import replace
import builtins
import io
import json
from pathlib import Path

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu
from kho_tri_thuc_sdk.engine_http import DuongHttp
from kho_tri_thuc_sdk.thu import MayChuGia

from e_mask.chay import tao_app
from e_mask.doc_word import doc_word
from e_mask.doc_excel import doc_excel
from e_mask.ho_so_ai import json_chuan
from e_mask.ho_so_tep import CHUAN_BI, VAN_BAN, GIU_DINH_DANG
from e_mask.kho_anh_xa_ram import KhoAnhXaRAM
from ho_tro_mask_b5 import TEN, ALIAS
from ho_tro_mask_b7 import chuan_bi_het, giao as giao_local, chay
from ho_tro_mask_b9 import MO, bo, giao, ket, loi
from test_mask_b8 import doi_alias


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('dang', ['tep', 'van_ban'])
@pytest.mark.parametrize('dong', [True, False])
def test_mau_7_bo_t_ten_co_dinh_nguyen_bytes_va_tieu_thu(loai, dang, dong):
    b = bo(loai, dang=dang)
    giao(b, dong=dong)
    if dang == 'van_ban':
        # B7 chỉ phát hành chuỗi; map đó dành mở văn bản mẫu 3/AI,
        # không được caller đổi thành tệp chưa từng được phát hành.
        assert loi(b)['loi']['ma'] == 'MASK_MO_CHE_KHONG_DAY_DU'
        assert b.mo.luot_upload == 0
        return
    t = ket(b)
    ref = t['tep_da_mo_che']
    assert ref['ten'] == 'mask-da-mo-che.' + loai
    assert b.c.doc_tep(ref['tep_id']) == b.goc_ram
    assert b.mo.da_tieu_thu == [True] and b.mo.so_nhan == 1
    chu = next(iter(b.c.ket_qua_cuoi_demo))
    assert b.mo.doc_dung_quyen(ref['tep_id'], chu) == b.goc_ram
    with pytest.raises(LoiNghiepVu):
        b.mo.doc_dung_quyen(ref['tep_id'], ('module-khac-DEMO',))
    assert not b.mo.cach_ly and not b.mo.dang_cach_ly


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_mo_tai_tep_ai_sua_giu_phan_moi_tien_ngay(loai):
    b = bo(loai)
    moi = '; DEMO bổ sung 2.000.000 VND ngày 2026-11-01.'
    raw = doi_alias(b.da_che, loai, ALIAS.lower() + moi)
    giao(b, raw=raw)
    t = ket(b)
    raw_ra = b.c.doc_tep(t['tep_da_mo_che']['tep_id'])
    doc = (doc_word if loai == 'docx' else doc_excel)(raw_ra, kiem_huy=lambda: None)
    assert any(TEN + moi in (v.van_ban if loai == 'docx' else v.chu) for v in doc.vung)


@pytest.mark.parametrize('payload, tham_so, can_bao', [(False, True, True), (True, False, False), (None, False, True)])
def test_payload_dong_viec_thang_tham_so_nhung_deu_don(payload, tham_so, can_bao):
    b = bo()
    giao(b, dong=payload, tham_so={'dong_viec': tham_so})
    ket(b)
    tien_do = b.c.xem(b.v)['tien_do']
    assert any('dữ liệu được dọn' in str(t) for t in tien_do) is can_bao


@pytest.mark.parametrize('khoa', ['module', 'nguoi_gui', 'tai_lieu', 'phap_nhan_id', 'DEMO',
    'map', 'anh_xa', 'path', 'url', 'van_ban', 'dinh_danh_da_biet', 'cloud', 'cau_hinh'])
def test_mau_7_khong_nhan_danh_tinh_hay_duong_tat(khoa):
    b = bo()
    giao(b, sua=lambda v: dict(v, **{khoa: TEN}))
    k = loi(b)
    assert k['loi']['ma'] == 'MASK_DAU_VAO' and b.mo.luot_upload == 0
    assert TEN not in repr(k)


@pytest.mark.parametrize('raw', [b'\xff', b'\xef\xbb\xbf{}', b'{}x', b'[]', b'{',
    b'{"ma_yeu_cau":"x","ma_yeu_cau":"y","tep":{}}',
    b'{"ma_yeu_cau":"x","tep":{"ten":"a","ten":"b"}}',
    b'{"tep":NaN}', b'{"tep":Infinity}', b'{"tep":-Infinity}', b'{"tep":1e9999}',
    b'{"tep":"\\ud800"}', b'{"tep":' + b'[' * 70 + b'0' + b']' * 70 + b'}'])
def test_json_utf8_nghiem_ngat_khoa_trung_nan_tran(raw):
    b = bo()
    giao(b, json_raw=raw)
    loi(b)
    assert b.mo.luot_upload == 0


@pytest.mark.parametrize('khoa, gia_tri', [
    ('tep_id', 'https://DEMO.invalid/a'), ('tep_id', '../DEMO.docx'), ('tep_id', 'D:DEMO'),
    ('ten', '../DEMO.docx'), ('ten', 'DEMO\\a.docx'), ('ten', 'DEMO\u200b.docx'),
    ('kich_thuoc', True), ('kich_thuoc', -1), ('kich_thuoc', '1'), ('kich_thuoc', 1048577),
    ('kich_thuoc', 1), ('mime', 'application/json'), ('mime', 'application/pdf')])
def test_tham_chieu_con_khong_path_url_sai_mime_kich_thuoc(khoa, gia_tri):
    b = bo()
    def sua(v):
        v['tep'][khoa] = gia_tri
        return v
    giao(b, sua=sua)
    loi(b)
    assert b.mo.luot_upload == 0


@pytest.mark.parametrize('dong', [None, 0, 1, 'false', [], {}])
def test_dong_viec_khong_phai_bool_bi_chan(dong):
    b = bo()
    giao(b, sua=lambda v: dict(v, dong_viec=dong))
    assert loi(b)['loi']['ma'] == 'MASK_DAU_VAO'


def test_core_khong_cap_quyen_tep_con_khong_fallback():
    b = bo()
    giao(b, quyen_con=False)
    loi(b)
    assert b.mo.luot_upload == 0


@pytest.mark.parametrize('sai', ['trung_khoa', 'nan', 'danh_tinh', 'de_quy', 'ds_501', 'ds_truong_la', 'sai_size'])
def test_mau_5_json_va_tham_chieu_con_cung_kiem_nghiem_ngat(sai):
    b = bo(san=False, boc=True)
    ref = b.dau['tep']
    v = json.loads(b.c.doc_tep(ref['tep_id']))
    if sai == 'danh_tinh': v['module'] = TEN
    elif sai == 'de_quy': v['tep'] = dict(ref)
    elif sai == 'ds_501': v['dinh_danh_da_biet'] = [dict(gia_tri=TEN, nhom='CONG_TY')] * 501
    elif sai == 'ds_truong_la': v['dinh_danh_da_biet'] = [dict(gia_tri=TEN, nhom='CONG_TY', bo_kiem=True)]
    elif sai == 'sai_size': v['tep']['kich_thuoc'] += 1
    raw = json_chuan(v)
    if sai == 'trung_khoa': raw = raw[:-1] + b',"tep":{}}'
    elif sai == 'nan': raw = raw[:-1] + b',"dinh_danh_da_biet":NaN}'
    ten, mime, _ = b.c._tep[ref['tep_id']]
    b.c._tep[ref['tep_id']] = ten, mime, raw
    b.c._viec[b.v]['dau_vao']['tep']['kich_thuoc'] = len(raw)
    k = chay(b)
    assert k['trang_thai'] == 'LOI' and k['ket_qua'] is None
    assert b.ram._ban_ghi is None and b.cong.dem_chot == 0


def test_tep_con_khai_nho_nhung_bytes_vuot_tran_khong_doc_het():
    b = bo()
    giao(b)
    ten, mime, _ = b.c._tep[b.ref_mo['tep_id']]
    b.c._tep[b.ref_mo['tep_id']] = ten, mime, b'x' * 1048577
    loi(b)
    assert b.mo.luot_upload == 0


@pytest.mark.parametrize('ghim, lifecycle', [(False, True), (True, False)])
def test_core_gia_khong_fallback_khi_thieu_ghim_hoac_lifecycle(ghim, lifecycle):
    b = bo(san=False)
    b.q.ram_ghim, b.q.ram_bao = ghim, lifecycle
    k = chay(b)
    assert k['trang_thai'] == 'LOI' and k['ket_qua'] is None
    assert k['loi']['ma'] == 'MASK_CHUOI_CHUA_GHIM' and b.ram._ban_ghi is None


def test_ma_caller_khong_chon_map_va_loi_don_map_cua_chu():
    b = bo()
    giao(b, sua=lambda v: dict(v, ma_yeu_cau='chuoi-khac-DEMO'))
    assert loi(b)['loi']['ma'] == 'MASK_MA_YEU_CAU'


@pytest.mark.parametrize('truong, gia_tri', [('module', 'module-khac-DEMO'), ('nguoi_gui', 'nguoi-khac-DEMO'),
    ('tai_lieu', 'tai-lieu-khac-DEMO'), ('vung', 'THAT')])
def test_sai_scope_khong_mo_va_khong_don_map_chu_khac(truong, gia_tri):
    b = bo()
    giao(b)
    setattr(b.q, truong, gia_tri)
    loi(b, don=False)
    assert b.ram._ban_ghi is b.bg and b.bg.du_lieu
    b.dh.tien(601)
    assert not b.bg.du_lieu


@pytest.mark.parametrize('sai', ['instance', 'phap_nhan', 'restart'])
def test_khac_instance_phap_nhan_restart_khong_phuc_hoi(sai):
    b = bo()
    giao(b)
    if sai == 'instance':
        b.q.ram_sua_ctx = lambda ctx: replace(ctx, instance='worker-khac-DEMO')
    elif sai == 'phap_nhan':
        b.q.ram_sua_ctx = lambda ctx: replace(ctx, phap_nhan_id='pn-khac-DEMO')
    else:
        b.app.kho_anh_xa_ram = KhoAnhXaRAM(quyen=b.q, dong_ho=b.dh, hen_gio=b.dh.hen_gio)
    loi(b, don=False)
    assert b.mo.luot_upload == 0
    b.dh.tien(601)
    assert b.ram._ban_ghi is None


@pytest.mark.parametrize('ket_thuc', ['HUY', 'LOI', 'KET_THUC', 'MAT_QUYEN', 'MAT_LEASE', 'HET_HAN'])
def test_core_huy_khi_mask_ranh_cho_ai_don_ngay(ket_thuc):
    b = bo()
    giao(b)
    b.q.bao_ram(b.ctx.ma_yeu_cau, ket_thuc)
    assert b.ram._ban_ghi is None and not b.bg.du_lieu
    loi(b)


@pytest.mark.parametrize('moc', ['kiem_tep_truoc', 'kiem_tep_sau', 'vao', 'nhan', 'ra'])
@pytest.mark.parametrize('kieu', ['huy', 'ttl'])
def test_huy_ttl_tai_cac_bien_khong_phat_hanh_dang_do(moc, kieu):
    b = bo()
    giao(b)
    def chen(ten, v):
        if ten == moc:
            if kieu == 'ttl': b.dh.tien(601)
            else: b.q.bao_ram(b.ctx.ma_yeu_cau, 'HUY')
    b.mo.moc = chen
    loi(b)
    assert not b.c.ket_qua_cuoi_demo


@pytest.mark.parametrize('thieu', ['kiem_tep_mo', 'ban_giao_cuoi', 'budget', 'quyen'])
def test_thieu_cua_core_budget_quyen_khong_upload(thieu):
    b = bo()
    giao(b)
    if thieu == 'budget': b.mo.budget = False
    elif thieu == 'quyen': b.mo.tep_hop_le = False
    else: setattr(b.mo, thieu, None)
    loi(b)
    assert b.mo.luot_upload == 0


@pytest.mark.parametrize('sai', ['[[MASKCT-LA]]', '[[MASKCT-DEMO-000X]]', 'MASKCT-DEMO-0001', ''])
@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_alias_la_hong_thieu_khong_tra_tep_mo_do(loai, sai):
    b = bo(loai)
    giao(b, raw=doi_alias(b.da_che, loai, sai))
    assert loi(b)['loi']['ma'] == 'MASK_MO_CHE_KHONG_DAY_DU'
    assert b.mo.luot_upload == 0


def test_da_tieu_thu_retry_khong_chay_mo_lai():
    b = bo()
    giao(b)
    ket(b)
    so = b.mo.luot_upload
    cu = dict(b.mo.phat_hanh)
    giao(b)
    k = chay(b)
    assert k['trang_thai'] == 'LOI' and k['ket_qua'] is None
    assert b.mo.phat_hanh == cu
    assert b.mo.luot_upload == so and b.mo.so_nhan == 1


@pytest.mark.parametrize('thao_tac', ['tep', 'ket_qua', 'ket_thuc'])
def test_sdk_mat_mot_ack_gui_lai_cung_khoa_khong_mo_lai(thao_tac):
    b = bo()
    giao(b)
    truoc = b.c.so_lan_ghi[thao_tac]
    b.c.gay_mat_xac_nhan(thao_tac)
    ket(b)
    assert b.c.so_lan_ghi[thao_tac] == truoc + 1
    assert b.mo.so_nhan == 1


@pytest.mark.parametrize('moc', ['nhan', 'ra'])
def test_mat_ack_ban_giao_chua_ro_khong_giu_map_retry(moc):
    b = bo()
    giao(b)
    b.mo.mat_ack = moc
    k = chay(b)
    assert k['trang_thai'] == 'CHUA_RO' and k['ket_qua'] is None
    assert b.ram._ban_ghi is None and not b.bg.du_lieu
    assert bool(b.c.ket_qua_cuoi_demo) is (moc == 'ra')
    assert bool(b.mo.phat_hanh) is (moc == 'ra')
    if moc == 'ra':
        chu, raw = next(iter(b.c.ket_qua_cuoi_demo.items()))
        t = json.loads(raw)['truong']
        assert b.mo.doc_dung_quyen(t['tep_da_mo_che']['tep_id'], chu) == b.goc_ram
    da_nhan = b.mo.so_nhan
    giao(b)
    assert chay(b)['trang_thai'] == 'LOI' and b.mo.so_nhan == da_nhan


def test_partial_upload_mat_ack_het_retry_thu_hoi_ban_ro():
    b = bo()
    giao(b)
    tai = b.c._tai_tep_ra
    def do(ma, v, ten, raw, mime, khoa):
        tai(ma, v, ten, raw, mime, khoa)
        raise TimeoutError(TEN)
    b.c._tai_tep_ra = do
    loi(b, trang='CHUA_RO')
    assert b.mo.thu_hoi and b.mo.so_nhan == 0
    assert all(not ten.startswith('mask-da-mo-che') for ten, _mime, _raw in b.c._tep.values())


@pytest.mark.parametrize('moc', ['kiem_tep_truoc', 'vao', 'nhan', 'ra'])
def test_loi_port_khong_dump_payload_traceback_stderr(moc, capsys, caplog):
    b = bo()
    giao(b)
    def chen(ten, v):
        if ten == moc: raise RuntimeError(TEN)
    b.mo.moc = chen
    k = loi(b)
    assert TEN not in repr(k)
    assert capsys.readouterr() == ('', '') and not caplog.records


def test_spy_khong_ghi_tep_tam_ro_map_ngoai_ket_qua_cuoi(monkeypatch, capsys, caplog):
    b = bo()
    giao(b)
    def boc(ham):
        def mo(p, mode='r', *a, **kw):
            assert not any(c in mode for c in 'wax+')
            return ham(p, mode, *a, **kw)
        return mo
    monkeypatch.setattr(builtins, 'open', boc(builtins.open))
    monkeypatch.setattr(io, 'open', boc(io.open))
    t = ket(b)
    assert TEN not in repr(t)
    assert not hasattr(b.mo, 'anh_xa') and b.ram._ban_ghi is None
    for ten, kw in b.cong.cac_cua:
        if ten == 'ban_giao' and 'yeu_cau' in kw:
            v = json.loads(kw['yeu_cau'])
            assert TEN not in repr(v['yeu_cau_ai']['chuyen_tiep'])
        else:
            assert TEN not in repr(kw)
    assert capsys.readouterr() == ('', '') and not caplog.records


@pytest.mark.parametrize('cua', ['ban_giao_tep_cuoi', 'chot_metadata'])
def test_b7_thieu_binding_b9_khong_bao_thanh_cong_gia(cua):
    b = bo(san=False)
    chuan_bi_het(b)
    setattr(b.cong, cua, None)
    giao_local(b)
    k = chay(b)
    assert k['trang_thai'] == 'LOI' and k['ket_qua'] is None
    assert b.ram._ban_ghi is None and b.cong.dem_chot == 0


@pytest.mark.parametrize('moc', ['vao_cach_ly', 'ra_cach_ly'])
def test_b7_loi_ban_giao_ngoai_handle_van_don_map(moc):
    b = bo(san=False)
    chuan_bi_het(b)
    giao_local(b)
    def chen(ten, v):
        if ten == moc: raise RuntimeError(TEN)
    b.cong.moc = chen
    k = chay(b)
    assert k['trang_thai'] == 'LOI' and k['ket_qua'] is None
    assert b.ram._ban_ghi is None


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_b9_http_gia_cung_handler_acl_ngan_upload_ack(loai):
    b = bo(loai)
    giao(b)
    khoa = 'khoa-engine-DEMO-b9-0000000000'
    with MayChuGia(b.c, {'e_mask': khoa}) as may:
        dt = DuongHttp(may.url, 'e_mask', khoa, 'instance-DEMO')
        b.c.gay_mat_xac_nhan('tep')
        b.app.chay(dt, dung_khi_het_viec=True, khoang_gia_han=0.02, cho_gui_lai_giay=0)
        cac = list(may.cac_loi_goi)
    k = b.c.xem(b.v)
    assert k['trang_thai'] == 'XONG', k
    assert b.ram._ban_ghi is None and b.mo.so_nhan == 1
    assert b.c.doc_tep(k['ket_qua']['truong']['tep_da_mo_che']['tep_id']) == b.goc_ram
    assert cac  # Transport HTTP thật qua MayChuGia, không mock SDK mo_tep.
