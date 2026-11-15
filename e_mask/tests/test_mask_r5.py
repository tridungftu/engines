"""MASK-R5: đã kiểm bằng Core giả (CoreGia); không Cloud/model thật."""
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import socket
import unicodedata

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, ViecDaHuy, LoiDuongTruyen

from e_mask import chuan_bi_ai as cb, phong_bi
from e_mask.anh_xa_ai import tao_anh_xa, bam_chu
from e_mask.chay import tao_app
from e_mask.hau_kiem_ai import NANG_LUC
from e_mask.ho_so_ai import KhoHoSoAI, bam_bytes, json_chuan
from e_mask.kho_anh_xa_ram import KhoAnhXaRAM
from ho_tro_mask_r5 import bo, chay, chuan_bi, chuan_bi_tat_ca, giao, noi_handler


def chan(k):
    assert k['trang_thai'] != 'XONG' and k['ket_qua'] is None, k


def test_rong_day_du_ram_khong_snapshot_ngan_va_giu_han():
    b = bo()
    k = chuan_bi(b)
    meta = k['ket_qua']['yeu_cau_ai']['chuyen_tiep']['mask_2c']
    assert 'ho_so' not in meta and 'tap_phan_hoi' not in meta
    assert len(json_chuan(meta)) < 4096
    han = b.ram._ban_ghi.han
    du = b.ram._ban_ghi.du_lieu
    assert du['ho_so_ai']['quy_tac']['anh_xa']['goc'] == b.chu
    giao(b)
    k = chay(b)
    assert k['trang_thai'] == 'XONG', k
    assert k['ket_qua']['van_ban_da_che']['van_ban'] == b.chu
    assert b.ram._ban_ghi.han == han
    assert du['giai_doan_ai'] == 'DA_HAU_KIEM' and 'phan_hoi_local' not in du
    assert not b.c._tep
    assert not b.c.xem_ngan('e_mask', 'dinh_danh')


@pytest.mark.parametrize('dang', ['NFC', 'NFD'])
@pytest.mark.parametrize('chen', ['', '\u200b', '\ufe0f', '\U000e0100', '\t', '\u00a0'])
def test_giu_goc_unicode_local_va_alias_ram_nguyen_van(dang, chen):
    ten = unicodedata.normalize(dang, 'Công ty DEMO Đá Cuội').replace(' ', chen + ' ')
    chu = 'bên: ' + ten + '; 1.000.000 VND ngày 30/10/2026.'
    b = bo(chu, seeds=[('Công ty DEMO Đá Cuội', 'CONG_TY', '[[MASKCT-R5-DEMO]]')])
    k = chuan_bi(b)
    assert k['ket_qua']['yeu_cau_ai']['tai_lieu'] == chu
    giao(b, [(5, 5+len(ten), 'to_chuc', 'chac')])
    k = chay(b)
    assert k['trang_thai'] == 'XONG', k
    assert b.ram._ban_ghi.du_lieu['alias_nguyen_van'] == {'[[MASKCT-R5-DEMO]]': ten}
    assert ten not in json.dumps(k, ensure_ascii=False)
    assert '1.000.000 VND ngày 30/10/2026' in k['ket_qua']['van_ban_da_che']['van_ban']


def test_cua_snapshot_cu_dong_khong_goi_cong_ngan():
    class Cam:
        def __getattr__(self, ten):
            pytest.fail('Không được dùng kho snapshot cũ.')
    k = KhoHoSoAI(ngan=Cam(), quyen=Cam(), cong=Cam())
    for ham in (k.luu, k.doc):
        with pytest.raises(LoiNghiepVu):
            ham(None, 'DEMO', None)


@pytest.mark.parametrize('goc', ['Nguyễn Văn An; NGUYỄN VĂN AN', 'a\u0301; á', 'a\u200bb; ab'])
def test_cung_alias_khac_nguyen_van_khong_chon_dau(goc):
    a, z = goc.split('; ')
    m = tao_anh_xa(goc, [(0, len(a), '[[DEMO]]'), (len(a)+2, len(goc), '[[DEMO]]')])
    with pytest.raises(ValueError):
        m.alias_nguyen_van()


@pytest.mark.parametrize('khoa', ['ho_so', 'tap_phan_hoi', 'goc', 'map', 'ke_hoach', 'x'])
def test_chuyen_tiep_cam_object_noi_dung_ngoai_allowlist(khoa):
    b = bo()
    k = chuan_bi(b)
    m = k['ket_qua']['yeu_cau_ai']['chuyen_tiep']['mask_2c']
    m[khoa] = {'goc': b.chu}
    with pytest.raises(LoiNghiepVu):
        phong_bi.kiem_meta_ram(m)


@pytest.mark.parametrize('cach', ['nguon', 'cloud', 'engine', 'nang_luc', 'model', 'finish',
                                  'bam', 'prompt', 'span', 'du_lieu', 'quet', 'rong_gia'])
def test_sai_nguon_va_span_khong_phat_hanh_don_ram(cach):
    b = bo()
    chuan_bi(b)
    giao(b)
    p = b.bundle['phan_hoi'][0]
    a = p['tra_loi_ai']['tra_loi_ai']
    if cach == 'nguon': b.cong.nguon = None
    elif cach == 'cloud': a['nha_cung_cap'] = 'cloud'
    elif cach in {'engine', 'nang_luc', 'model'}: p['nguon'][cach] = 'gia'
    elif cach == 'finish': p['nguon']['hoan_tat']['ket_thuc'] = 'length'
    elif cach == 'bam': a['bam_dau_vao'] = 'sha256:'+'0'*64
    elif cach == 'prompt': a['ma_prompt'] = 'gia'
    elif cach == 'du_lieu': a['du_lieu'] = None
    elif cach == 'quet': a['du_lieu']['da_quet_het'] = False
    elif cach == 'span': a['du_lieu']['thuc_the'] = [dict(loai='nguoi', muc='chac', nguyen_van='bịa', bat_dau=0, ket_thuc=3)]
    else: a['kiem_trich_dan']['dat'] = False
    b.cong.raw = json_chuan(b.bundle)
    chan(chay(b))
    assert b.ram._ban_ghi is None


@pytest.mark.parametrize('loai', ['HUY', 'LOI', 'MAT_QUYEN', 'MAT_LEASE', 'KET_THUC', 'HET_HAN'])
def test_su_kien_khi_ranh_don_truoc_hau_kiem(loai):
    b = bo()
    chuan_bi(b)
    giao(b)
    du = b.ram._ban_ghi.du_lieu
    b.q.bao_ram(b.ctx.ma_yeu_cau, loai)
    assert not du
    chan(chay(b))


@pytest.mark.parametrize('loai', ['restart', 'khac_instance', 'ttl'])
def test_mat_ram_khong_phuc_hoi_tu_phan_hoi_hay_core(loai):
    b = bo()
    chuan_bi(b)
    giao(b)
    if loai == 'restart':
        b.app.kho_anh_xa_ram = KhoAnhXaRAM(quyen=b.q)
        noi_handler(b.app, b.q, b.cong)
    elif loai == 'khac_instance':
        b.q.ram_sua_ctx = lambda v: replace(v, instance='instance-khac-DEMO')
    else: b.dh.tien(600)
    k = chay(b)
    chan(k)
    assert k['loi']['ma'] == 'MASK_ANH_XA_KHONG_CON'


def test_replay_khong_phat_hanh_lan_hai_va_don_map():
    b = bo()
    chuan_bi(b)
    giao(b)
    assert chay(b)['trang_thai'] == 'XONG'
    b.c._viec[b.v]['trang_thai'] = 'CHO'
    b.c._hang.append(b.v)
    chan(chay(b))
    assert b.ram._ban_ghi is None


@pytest.mark.parametrize('loai', ['timeout', 'chua_ro', 'huy', 'lease', 'loi'])
def test_local_chua_ro_chi_giu_trong_han_tuyet_doi(loai):
    b = bo()
    chuan_bi(b)
    giao(b)
    han = b.ram._ban_ghi.han
    def moc(ten, v):
        if ten != 'nhan_phan_hoi': return
        if loai == 'chua_ro': raise ChuaRo('bí mật DEMO')
        if loai == 'huy': raise ViecDaHuy()
        if loai == 'lease': raise LoiDuongTruyen('MAT_LEASE', 'bí mật DEMO', http_status=409)
        if loai == 'loi': raise ValueError('bí mật DEMO')
        raise TimeoutError('bí mật DEMO')
    b.cong.moc = moc
    k = chay(b)
    chan(k)
    assert 'bí mật' not in json.dumps(k, ensure_ascii=False)
    if loai == 'chua_ro':
        assert k['trang_thai'] == 'CHUA_RO' and b.ram._ban_ghi.han == han
        b.dh.tien(600)
    assert b.ram._ban_ghi is None


def test_spy_moi_cua_khong_map_ho_so_log_stderr_tep(monkeypatch, capsys):
    b = bo()
    def cam(*a, **kw): raise AssertionError('Cấm mạng/tệp đầu ra DEMO.')
    monkeypatch.setattr(socket, 'create_connection', cam)
    monkeypatch.setattr(Path, 'write_bytes', cam)
    monkeypatch.setattr(Path, 'write_text', cam)
    chuan_bi(b)
    giao(b)
    k = chay(b)
    assert k['trang_thai'] == 'XONG', k
    for ten, v in b.cong.cac_cua:
        if ten == 'ban_giao' and 'yeu_cau' in v:
            v = json.loads(v['yeu_cau'])
            # Chỉ tai_lieu của chính đoạn Local được phép đi qua contract.
            v['yeu_cau_ai'].pop('tai_lieu')
        chu = repr(v)
        assert b.chu not in chu
        assert not any(x in chu for x in ('goc_che', 'sach_do', 'alias_nguyen_van', 'ket_qua_quy_tac'))
    assert not b.c._tep
    assert not capsys.readouterr().err


def test_runtime_chua_noi_ram_khong_nhan_adapter_snapshot_cu():
    b = bo()
    b.app = tao_app(quyen=b.q, cong_chuan_bi_ai=b.cong, cong_hau_kiem_ai=b.cong)
    chan(chay(b))
    assert not b.cong.giao and not b.c._tep


@pytest.mark.parametrize('cach', ['du', 'thieu', 'lap', 'doi_cho', 'cloud_dau', 'sai_bam_dau', 'chua_giao'])
def test_core_dieu_phoi_du_doan_khong_lay_phan_dau(cach):
    b = bo('nội dung thông thường. ' * 800)
    if cach == 'chua_giao': chuan_bi(b)
    else: chuan_bi_tat_ca(b)
    assert len(cb.lap_ke_hoach(b.chu)) > 1
    giao(b)
    ds = b.bundle['phan_hoi']
    if cach == 'thieu': ds.pop(0)
    elif cach == 'lap': ds[0] = deepcopy(ds[-1])
    elif cach == 'doi_cho': ds.reverse()
    elif cach == 'cloud_dau': ds[0]['tra_loi_ai']['tra_loi_ai']['nha_cung_cap'] = 'cloud'
    elif cach == 'sai_bam_dau': ds[0]['tra_loi_ai']['tra_loi_ai']['bam_dau_vao'] = 'sha256:' + '0'*64
    if cach != 'du': b.cong.raw = json_chuan(b.bundle)
    k = chay(b)
    if cach == 'du': assert k['trang_thai'] == 'XONG', k
    else:
        chan(k)
        assert b.ram._ban_ghi is None


@pytest.mark.parametrize('loai,nhom', [('nguoi', 'CA_NHAN'), ('to_chuc', 'CONG_TY'), ('dia_chi', 'DIA_CHI')])
def test_local_che_bo_sung_alias_chinh_thuc_trong_ram(loai, nhom):
    ten = 'orvella mivanta'
    b = bo('gửi: '+ten+'; nội dung.', seeds=[(ten, nhom, '[[MASKKHAC-R5-DEMO]]')])
    chuan_bi(b)
    assert ten in b.ram._ban_ghi.du_lieu['ho_so_ai']['ket_qua_quy_tac']['van_ban_da_che']
    giao(b, [(5, 5+len(ten), loai, 'chac')])
    k = chay(b)
    assert k['trang_thai'] == 'XONG', k
    assert k['ket_qua']['van_ban_da_che']['van_ban'] == 'gửi: [[MASKKHAC-R5-DEMO]]; nội dung.'
    assert b.ram._ban_ghi.du_lieu['alias_nguyen_van'] == {'[[MASKKHAC-R5-DEMO]]': ten}


def test_ten_local_moi_chua_co_bao_dam_core_khong_ghi_map_ngan():
    b = bo('gửi: orvella mivanta; nội dung.')
    chuan_bi(b)
    giao(b, [(5, 20, 'nguoi', 'chac')])
    k = chay(b)
    chan(k)
    assert not b.c.xem_ngan('e_mask', 'dinh_danh') and not b.c.xem_ngan('e_mask', 'bi_danh')
    assert b.ram._ban_ghi is None


@pytest.mark.parametrize('cach', ['thieu_trich', 'bool', 'ngoai', 'cat_nfd', 'nghi_ngo', 'tien', 'ngay', 'alias', 'chen_cf'])
def test_bien_span_nghi_van_vung_bao_ve_khong_phat_hanh(cach):
    ten = unicodedata.normalize('NFD', 'orvella mivánta')
    b = bo('gửi: '+ten+'; 1.000.000 VND ngày 30/10/2026.', seeds=[(ten, 'CA_NHAN', '[[MASKCN-R5-DEMO]]')])
    chuan_bi(b)
    a, z = 5, 5+len(ten)
    if cach == 'cat_nfd': z = next(i for i,c in enumerate(b.chu) if unicodedata.category(c).startswith('M'))
    elif cach == 'tien': a = b.chu.index('1.000.000'); z = a+9
    elif cach == 'ngay': a = b.chu.index('30/10'); z = a+10
    elif cach == 'alias': a, z = 0, len(b.chu)
    elif cach == 'chen_cf': a, z = 6, 5+len(ten)
    giao(b, [(a, z, 'nguoi', 'nghi_ngo' if cach == 'nghi_ngo' else 'chac')])
    ai = b.bundle['phan_hoi'][0]['tra_loi_ai']['tra_loi_ai']
    if cach == 'thieu_trich': ai['trich_dan'] = []
    if cach == 'bool': ai['du_lieu']['thuc_the'][0]['bat_dau'] = True
    if cach == 'ngoai': ai['du_lieu']['thuc_the'][0]['ket_thuc'] = 8001
    b.cong.raw = json_chuan(b.bundle)
    chan(chay(b))
    assert b.ram._ban_ghi is None


@pytest.mark.parametrize('truong', ['module', 'nguoi_gui', 'tai_lieu', 'vung', 'phien', 'ma_luot', 'phap_nhan_id', 'dau_vao'])
def test_quyen_bi_doi_trong_cua_core_khong_phat_hanh(truong):
    b = bo()
    chuan_bi(b)
    giao(b)
    def moc(ten, v):
        if ten != 'chung_thuc': return
        if truong in {'module', 'nguoi_gui', 'tai_lieu', 'vung'}: setattr(b.q, truong, 'THAT' if truong == 'vung' else 'khac-DEMO')
        elif truong in {'phien', 'ma_luot'}: b.q.ve[b.v, 'che'] = replace(b.q.ve[b.v, 'che'], **{truong: 'khac-DEMO'})
        elif truong == 'phap_nhan_id': v.ngu_canh['phap_nhan_id'] = 'khac-DEMO'
        else: v.dau_vao['tra_loi_ai']['tra_loi'] = 'đổi DEMO'
    b.cong.moc = moc
    chan(chay(b))
    assert b.ram._ban_ghi is None


@pytest.mark.parametrize('raw', [b'{"x":1,"x":1}', b'{"x":NaN}', b'{"x":Infinity}', b'{}', b'\xff'])
def test_phan_hoi_json_nghiem_khong_phuc_hoi_ho_so(raw):
    b = bo()
    chuan_bi(b)
    giao(b)
    b.cong.raw = raw
    chan(chay(b))
    assert b.ram._ban_ghi is None


@pytest.mark.parametrize('cach', ['bam', 'map', 'goc', 'quy_tac', 'profile', 'khuon', 'prompt', 'phien_ban'])
def test_ho_so_ram_bi_doi_khong_nhan_du_bam_tu_khai(cach):
    b = bo()
    chuan_bi(b)
    giao(b)
    v = b.ram._ban_ghi.du_lieu
    s = v['ho_so_ai']
    if cach == 'bam': v['dau_ho_so_ai'] = replace(v['dau_ho_so_ai'], bam_ho_so='sha256:'+'0'*64)
    elif cach == 'map': s['quy_tac']['anh_xa']['goc_che'][0]['goc'][1] += 1
    elif cach == 'goc': s['quy_tac']['anh_xa']['goc'] += 'đổi'
    elif cach == 'quy_tac': s['ket_qua_quy_tac']['kiem_tien_ngay'] = False
    elif cach == 'profile': s['profile']['nha_cung_cap_bat_buoc'] = 'cloud'
    elif cach == 'khuon': s['khuon']['additionalProperties'] = True
    elif cach == 'prompt': s['cau_hinh']['prompt'] = 'đổi DEMO'
    else: s['quy_tac']['anh_xa']['phien_ban_unicode'] = 'khac-DEMO'
    chan(chay(b))
    assert b.ram._ban_ghi is None


def test_tep_giu_ref_nhung_bytes_doi_chan_retry():
    b = bo()
    raw = json_chuan({'van_ban': b.chu})
    ref = b.c.them_tep('DEMO.json', raw, 'application/json')
    b.c._viec[b.v]['dau_vao'] = {'loai': 'tep', 'tep': ref}
    chuan_bi(b)
    ten, mime, _ = b.c._tep[ref['tep_id']]
    b.c._tep[ref['tep_id']] = ten, mime, raw.replace('nội dung'.encode(), 'nội đổi'.encode())
    b.v = b.c.giao_viec(cb.NANG_LUC, {'loai': 'tep', 'tep': ref})
    b.q.cap(b.v, ma_yeu_cau=b.ctx.ma_yeu_cau)
    chan(chay(b))
    assert b.ram._ban_ghi is None


@pytest.mark.parametrize('cua', ['nhan_phan_hoi', 'kiem_han', 'chung_thuc', 'ban_giao'])
def test_huy_va_ttl_dang_xu_ly_khong_phat_hanh(cua):
    b = bo()
    chuan_bi(b)
    giao(b)
    def moc(ten, v):
        if ten == cua: b.dh.tien(600)
    b.cong.moc = moc
    chan(chay(b))
    assert b.ram._ban_ghi is None


def test_chua_ro_sau_chot_khong_cache_ban_ro_de_retry():
    b = bo()
    chuan_bi(b)
    giao(b)
    def moc(ten, v):
        if ten == 'ban_giao': raise ChuaRo('DEMO-ack')
    b.cong.moc = moc
    k = chay(b)
    chan(k)
    assert k['trang_thai'] == 'CHUA_RO' and b.ram._ban_ghi is None


def test_nguon_da_nhan_chua_tra_chung_thuc_truoc_dien_giai_ai():
    b = bo()
    chuan_bi(b)
    giao(b)
    p = b.bundle['phan_hoi'][0]
    p['nguon']['trang_thai'] = 'CHUA_RO'
    p['tra_loi_ai']['tra_loi_ai']['du_lieu'] = None
    b.cong.raw = json_chuan(b.bundle)
    # Payload được Core giao lúc đang chờ; cửa tin cậy phải ChuaRo,
    # không suy rỗng/sai khuôn từ phản hồi chưa hoàn tất để phát hành.
    b.c._viec[b.v]['dau_vao'] = deepcopy(p['tra_loi_ai'])
    def moc(ten, v):
        if ten == 'chung_thuc': raise ChuaRo('DEMO-dang-cho')
    b.cong.moc = moc
    k = chay(b)
    assert k['trang_thai'] == 'CHUA_RO' and k['ket_qua'] is None, k
    assert b.ram._ban_ghi is not None
    b.dh.tien(600)
    assert b.ram._ban_ghi is None


def test_tep_doi_ngay_trong_ban_giao_cung_ref_cung_size_chan():
    b = bo()
    raw = json_chuan({'van_ban': b.chu})
    ref = b.c.them_tep('DEMO.json', raw, 'application/json')
    b.c._viec[b.v]['dau_vao'] = {'loai': 'tep', 'tep': ref}
    def moc(ten, v):
        if ten == 'ban_giao':
            ten_tep, mime, raw = b.c._tep[ref['tep_id']]
            b.c._tep[ref['tep_id']] = ten_tep, mime, raw.replace(b'VND', b'USD')
    b.cong.moc = moc
    chan(chay(b))
    assert b.ram._ban_ghi is None


@pytest.mark.parametrize('cach', ['prompt', 'budget', 'dau_vao', 'chi_so', 'chi_so_bool'])
def test_retry_cung_chuoi_doi_ghim_khong_keo_dai_han(cach):
    b = bo()
    chuan_bi(b)
    if cach == 'prompt': b.cong.cfg['prompt'] += ' đổi DEMO'
    elif cach == 'budget': b.cong.budget[b.ctx.ma_yeu_cau]['token_ra_toi_da'] += 1
    elif cach == 'dau_vao': b.c._viec[b.v]['dau_vao']['van_ban'] += ' đổi'
    elif cach == 'chi_so': b.cong.i = 9
    else: b.cong.i = False
    b.c._viec[b.v]['trang_thai'] = 'CHO'
    b.c._hang.append(b.v)
    chan(chay(b))
    assert b.ram._ban_ghi is None


def test_chua_ro_chuan_bi_giu_map_retry_khong_tao_lai():
    b = bo()
    def moc(ten, v):
        if ten == 'ban_giao': raise ChuaRo('DEMO-da-nhan')
    b.cong.moc = moc
    k = chay(b)
    assert k['trang_thai'] == 'CHUA_RO'
    du = b.ram._ban_ghi.du_lieu
    dau, han = du['dau_ho_so_ai'], b.ram._ban_ghi.han
    b.cong.moc = lambda *a: None
    b.c._viec[b.v]['trang_thai'] = 'CHO'
    b.c._hang.append(b.v)
    assert chay(b)['trang_thai'] == 'XONG'
    assert b.ram._ban_ghi.du_lieu['dau_ho_so_ai'] == dau
    assert b.ram._ban_ghi.han == han


def test_cung_luot_doi_chi_so_hop_le_van_chan_replay():
    b = bo('nội dung thông thường. ' * 800)
    chuan_bi(b)
    b.cong.i = 1
    b.c._viec[b.v]['trang_thai'] = 'CHO'
    b.c._hang.append(b.v)
    chan(chay(b))
    assert b.ram._ban_ghi is None


def test_cam_ngan_ghi_snapshot_va_cam_upload_tep(monkeypatch):
    from kho_tri_thuc_sdk.engine import NganEngine, Viec
    b = bo()
    def cam(*a, **kw): pytest.fail('R5 không ghi ngăn/snapshot/upload.')
    monkeypatch.setattr(NganEngine, 'lo', cam)
    monkeypatch.setattr(Viec, 'tai_tep_ra', cam)
    chuan_bi(b)
    giao(b)
    assert chay(b)['trang_thai'] == 'XONG'
    assert not b.c._tep
