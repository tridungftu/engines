"""B7 hai lớp Local giả, chỉ DEMO; không đo chất lượng model thật."""
from copy import deepcopy
from dataclasses import replace
import json
import unicodedata

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu

from e_mask.chay import tao_app
from e_mask.ho_so_tep import CHUAN_BI, VAN_BAN, GIU_DINH_DANG
from e_mask.kho_anh_xa_ram import KhoAnhXaRAM
from e_mask.ho_so_ai import json_chuan
from ho_tro_mask_b5 import TEN, ALIAS, word, moi_vung_co_ten
from ho_tro_mask_b6 import excel, moi_vung
from ho_tro_mask_b7 import bo, chay, chuan_bi, chuan_bi_het, giao


def loi_khong_phat_hanh(b, k, *, ma=None):
    assert k['trang_thai'] in {'LOI', 'HUY'}, k
    assert k['ket_qua'] is None
    if ma:
        assert k['loi']['ma'] == ma, k
    assert b.ram._ban_ghi is None
    assert b.cong.dem_chot == 0
    assert not b.cong.giao_cuoi
    assert len(b.c._tep) == (2 if b.dau['tep']['mime'] == 'application/json' else 1)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('dang', ['van_ban', 'tep'])
def test_hai_lop_ban_giao_dung_loai_va_chot_mot_lan(loai, dang):
    b = bo(loai, dang=dang)
    k = chuan_bi_het(b)
    assert k['ket_qua']['loai'] == 'yeu_cau_ai'
    assert TEN in k['ket_qua']['yeu_cau_ai']['tai_lieu']
    bg = b.ram._ban_ghi
    assert bg.so_huu is None and bg.trang_thai == 'CHO_AI'
    assert b.cong.dem_chot == 0 and not b.cong.giao_cuoi
    giao(b)
    k = chay(b)
    assert k['trang_thai'] == 'XONG', k
    assert b.cong.dem_chot == 1
    assert b.ram._ban_ghi is bg and bg.so_huu is None
    assert bg.du_lieu['giai_doan_ai'] == 'DA_HAU_KIEM'
    assert 'phan_hoi_local' not in bg.du_lieu['ho_so_tep']
    if dang == 'van_ban':
        v = k['ket_qua']['van_ban_da_che']
        assert ALIAS in v['van_ban'] and TEN not in v['van_ban']
        assert v['con_sot'] == [] and v['kiem_tien_ngay'] is True
        assert len(b.c._tep) == 1
    else:
        v = k['ket_qua']['truong']
        assert v['con_sot_json'] == '[]' and v['kiem_tien_ngay'] is True
        ref = v['tep_da_che']
        assert ref['ten'] == 'mask-da-che.' + loai
        from e_mask.doc_word import doc_word
        from e_mask.doc_excel import doc_excel
        raw = b.c.doc_tep(ref['tep_id'])
        doc = (doc_word if loai == 'docx' else doc_excel)(raw, kiem_huy=lambda: None)
        assert any(ALIAS in (x.van_ban if loai == 'docx' else x.chu) for x in doc.vung)
    # Core giao lại kết quả đã nhận, không chạy lại hậu kiểm/chốt.
    kq = k['ket_qua']
    b.q.bao_ram(b.ctx.ma_yeu_cau, 'KET_THUC')
    assert b.ram._ban_ghi is None and bg.du_lieu == {}
    assert kq == k['ket_qua']


@pytest.mark.parametrize('loai,raw', [('docx', moi_vung_co_ten), ('xlsx', moi_vung)])
def test_local_quet_du_moi_vung_goc(loai, raw):
    b = bo(loai, raw=raw())
    chuan_bi_het(b)
    h = b.ram._ban_ghi.du_lieu['ho_so_tep']
    s = b.ram._ban_ghi.du_lieu['tep_word' if loai == 'docx' else 'tep_excel']
    assert {i for _a, _z, i in h['mien'] if i is not None} >= {
        i for i, x in enumerate(s['anh_xa']) if x is not None}
    assert all('ho_so_ai' not in p for _ten, p in b.cong.cac_cua if isinstance(p, dict))
    giao(b)
    k = chay(b)
    assert k['trang_thai'] == 'XONG', k
    assert TEN not in k['ket_qua']['van_ban_da_che']['van_ban']


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_mau_5_json_van_qua_hai_lop(loai):
    b = bo(loai, boc=True)
    chuan_bi_het(b)
    giao(b)
    assert chay(b)['trang_thai'] == 'XONG'


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('sai', ['cloud', 'cloud_nguon', 'offset', 'thieu_quet', 'nghi_ngo',
    'trich_dan', 'model', 'prompt', 'ho_so', 'bam', 'trung_phan_hoi', 'thieu_phan_hoi',
    'da_cat', 'them_khoa', 'chung_thuc'])
def test_nguon_khuon_span_sai_chan_va_don(loai, sai):
    b = bo(loai)
    chuan_bi_het(b)
    def sua(v):
        p = v['phan_hoi'][0]
        a = p['tra_loi_ai']['tra_loi_ai']
        if sai == 'cloud': a['nha_cung_cap'] = 'cloud'
        elif sai == 'cloud_nguon': p['nguon']['nha_cung_cap'] = 'cloud'
        elif sai == 'offset': a['du_lieu']['thuc_the'][0]['bat_dau'] += 1
        elif sai == 'thieu_quet': a['du_lieu']['da_quet_het'] = False
        elif sai == 'nghi_ngo': a['du_lieu']['thuc_the'][0]['muc'] = 'nghi_ngo'
        elif sai == 'trich_dan': a['trich_dan'] = []
        elif sai == 'model': a['model'] = 'model-khac'
        elif sai == 'prompt': a['ma_prompt'] = 'prompt-khac'
        elif sai == 'ho_so': a['chuyen_tiep']['mask_2c']['ho_so']['tep_id'] = 'tep-caller'
        elif sai == 'bam': a['bam_dau_vao'] = 'sha256:' + '0' * 64
        elif sai == 'trung_phan_hoi': v['phan_hoi'].append(deepcopy(p))
        elif sai == 'thieu_phan_hoi': v['phan_hoi'] = []
        elif sai == 'da_cat': p['nguon']['hoan_tat']['ket_thuc'] = 'length'
        elif sai == 'them_khoa': a['du_lieu']['them'] = TEN
        return v
    giao(b, sua=sua)
    if sai == 'chung_thuc': b.cong.nguon = b'{}'
    loi_khong_phat_hanh(b, chay(b))


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('cua', ['dang_tra', 'cau_hinh', 'kiem_ngan_sach', 'kiem_tep',
                               'chi_so_doan', 'ban_giao'])
def test_thieu_cong_chuan_bi_don_ram(loai, cua):
    b = bo(loai)
    setattr(b.cong, cua, None)
    loi_khong_phat_hanh(b, chay(b), ma='MASK_AI_CHUA_CO_CUA_CORE')


@pytest.mark.parametrize('cua', ['nhan_phan_hoi', 'chung_thuc', 'kiem_han',
                               'kiem_nguon_tep', 'chot_metadata', 'ban_giao'])
def test_thieu_cong_hau_kiem_chan(cua):
    b = bo()
    chuan_bi_het(b)
    giao(b)
    setattr(b.cong, cua, None)
    k = chay(b)
    assert k['trang_thai'] == 'LOI' and k['ket_qua'] is None
    assert b.ram._ban_ghi is None and not b.cong.giao_cuoi


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('su_kien', ['HUY', 'LOI', 'KET_THUC', 'MAT_LEASE', 'MAT_QUYEN'])
def test_su_kien_o_ai_khi_mask_ranh_don_ngay(loai, su_kien):
    b = bo(loai)
    chuan_bi_het(b)
    bg = b.ram._ban_ghi
    giao(b)
    b.q.bao_ram(b.ctx.ma_yeu_cau, su_kien)
    assert bg.du_lieu == {} and b.ram._ban_ghi is None
    loi_khong_phat_hanh(b, chay(b), ma='MASK_ANH_XA_KHONG_CON')


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('han', ['ttl', 'deadline'])
def test_timer_ranh_va_han_tuyet_doi(loai, han):
    b = bo(loai, ttl=60)
    if han == 'deadline': b.q.ram_han = b.dh.luc + 20
    chuan_bi_het(b)
    bg = b.ram._ban_ghi
    giao(b)
    b.dh.tien(60 if han == 'ttl' else 20)
    assert bg.du_lieu == {} and b.ram._ban_ghi is None
    loi_khong_phat_hanh(b, chay(b), ma='MASK_ANH_XA_KHONG_CON')


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('sai', ['restart', 'instance', 'module', 'nguoi_gui', 'tai_lieu', 'vung', 'phap_nhan'])
def test_khong_phuc_hoi_qua_worker_hoac_quyen_khac(loai, sai):
    b = bo(loai)
    chuan_bi_het(b)
    bg = b.ram._ban_ghi
    giao(b)
    if sai == 'restart':
        b.app.kho_anh_xa_ram = KhoAnhXaRAM(quyen=b.q, dong_ho=b.dh, hen_gio=b.dh.hen_gio)
    elif sai == 'instance': b.q.ram_sua_ctx = lambda ctx: replace(ctx, instance='instance-khac')
    elif sai == 'phap_nhan': b.q.ram_phap_nhan = 'phap-nhan-khac'
    else: setattr(b.q, sai, 'nguon-khac' if sai != 'vung' else 'THAT')
    k = chay(b)
    assert k['trang_thai'] == 'LOI' and k['ket_qua'] is None
    assert b.cong.dem_chot == 0 and not b.cong.giao_cuoi
    # Một caller sai không được dọn map của chủ khác; chủ nhận lifecycle/TTL.
    if b.ram._ban_ghi is not None:
        b.ram.nhan_su_kien(__import__('e_mask.quyen_yeu_cau', fromlist=['SuKienRAM']).SuKienRAM(bg.ctx, 'HUY'))
    assert bg.du_lieu == {}


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_tai_lieu_doi_cung_ref_khong_phat_hanh(loai):
    b = bo(loai)
    chuan_bi_het(b)
    giao(b)
    ten, mime, raw = b.c._tep[b.ref['tep_id']]
    b.c._tep[b.ref['tep_id']] = (ten, mime, raw[:-1] + bytes([raw[-1] ^ 1]))
    loi_khong_phat_hanh(b, chay(b))


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_retry_chuan_bi_khong_gia_han_ttl_khong_chot(loai):
    b = bo(loai, ttl=60)
    k = chuan_bi_het(b)
    bg, han = b.ram._ban_ghi, b.ram._ban_ghi.han
    b.dh.tien(59)
    b.c.dat_cau_hinh('e_mask', {'thoi_han_anh_xa_giay': 900})
    b.v = b.c.giao_viec(CHUAN_BI, b.dau)
    b.q.cap(b.v, ma_yeu_cau=b.ctx.ma_yeu_cau)
    assert chuan_bi(b)['ket_qua'] == k['ket_qua']
    assert bg.han == han and b.cong.dem_chot == 0
    b.dh.tien(1)
    assert bg.du_lieu == {} and b.ram._ban_ghi is None


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_chuoi_thu_hai_khong_day_map_cu(loai):
    b = bo(loai)
    chuan_bi_het(b)
    bg = b.ram._ban_ghi
    b.v = b.c.giao_viec(CHUAN_BI, b.dau)
    b.q.cap(b.v)
    k = chay(b)
    assert k['trang_thai'] == 'LOI' and k['loi']['ma'] == 'MASK_CHUOI_DANG_XU_LY'
    assert b.ram._ban_ghi is bg and bg.du_lieu


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('nguon', ['chuan_bi', 'phan_hoi'])
def test_chua_ro_chi_giu_ram_con_han(loai, nguon):
    b = bo(loai, ttl=60)
    if nguon == 'phan_hoi':
        chuan_bi_het(b)
        giao(b)
    def moc(ten, v):
        if ten == ('ban_giao' if nguon == 'chuan_bi' else 'nhan_phan_hoi'):
            raise ChuaRo('DEMO-nguon-chua-ro')
    b.cong.moc = moc
    k = chay(b)
    assert k['trang_thai'] == 'CHUA_RO' and k['ket_qua'] is None, k
    bg = b.ram._ban_ghi
    assert bg is not None and bg.so_huu is None
    han = bg.han
    b.dh.tien(60)
    assert b.ram._ban_ghi is None and bg.du_lieu == {} and bg.han == han


@pytest.mark.parametrize('cua', ['chot_metadata', 'ban_giao_cuoi'])
def test_mat_ack_ket_thuc_don_khong_chot_lai(cua):
    b = bo()
    chuan_bi_het(b)
    giao(b)
    def moc(ten, v):
        if ten == cua: raise TimeoutError('DEMO-mat-ACK')
    b.cong.moc = moc
    k = chay(b)
    assert k['trang_thai'] == 'CHUA_RO' and k['ket_qua'] is None, k
    assert b.ram._ban_ghi is None and b.cong.dem_chot == 1
    b.v = b.c.giao_viec(VAN_BAN, b.bundle['phan_hoi'][-1]['tra_loi_ai'])
    b.q.cap(b.v, ma_yeu_cau=b.ctx.ma_yeu_cau)
    assert chay(b)['trang_thai'] == 'LOI' and b.cong.dem_chot == 1


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_dang_tra_ghim_khong_doi_handler_cuoi(loai):
    b = bo(loai, dang='van_ban')
    chuan_bi_het(b)
    giao(b, nang_luc=GIU_DINH_DANG)
    loi_khong_phat_hanh(b, chay(b), ma='MASK_AI_NGUON')


def test_thieu_ghim_va_lifecycle_tu_choi_truoc_doc_tep():
    for thuoc in ('ram_ghim', 'ram_bao'):
        b = bo()
        setattr(b.q, thuoc, False)
        k = chay(b)
        assert k['trang_thai'] == 'LOI' and k['loi']['ma'] == 'MASK_CHUOI_CHUA_GHIM'
        assert not b.cong.cac_cua and b.ram._ban_ghi is None


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_local_chi_them_che_khi_lop_mot_dat(loai):
    ten, alias = 'zestoria', '[[MASKCT-0002]]'
    raw = word('đã bàn giao cho ' + ten + '.') if loai == 'docx' else excel('đã bàn giao cho ' + ten + '.')
    b = bo(loai, raw=raw, seeds=((ten, 'CONG_TY', alias),))
    chuan_bi_het(b)
    h = b.ram._ban_ghi.du_lieu['ho_so_tep']
    assert ten in h['map_quy_tac'].da_che and alias not in h['map_quy_tac'].da_che
    spans = []
    for a, z, i in h['mien']:
        if i is not None and ten in h['map_quy_tac'].goc[a:z]:
            x = h['map_quy_tac'].goc.index(ten, a, z)
            spans.append((x, x+len(ten), 'to_chuc', 'chac'))
    giao(b, spans=spans)
    k = chay(b)
    assert k['trang_thai'] == 'XONG', k
    assert alias in k['ket_qua']['van_ban_da_che']['van_ban']
    assert ten not in k['ket_qua']['van_ban_da_che']['van_ban']


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('dang', ['nfd', 'cf', 'rich'])
def test_unicode_va_run_giu_nguyen_goc_local(loai, dang):
    ten = unicodedata.normalize('NFD', TEN) if dang == 'nfd' else TEN.replace('DEMO', 'DE\u200bMO') if dang == 'cf' else TEN
    if dang == 'rich':
        if loai == 'docx':
            from ho_tro_mask_b1 import W
            raw = word(noi_dung=f'<w:p><w:r><w:t>{TEN[:10]}</w:t></w:r><w:r><w:t>{TEN[10:]}</w:t></w:r></w:p>')
        else:
            raw = excel(noi_dung=f'<row r="1"><c r="A1" t="inlineStr"><is><r><t>{TEN[:10]}</t></r><r><t>{TEN[10:]}</t></r></is></c></row>')
    else:
        raw = word(ten) if loai == 'docx' else excel(ten)
    b = bo(loai, raw=raw)
    k = chuan_bi_het(b)
    assert ten in k['ket_qua']['yeu_cau_ai']['tai_lieu']
    giao(b)
    k = chay(b)
    assert k['trang_thai'] == 'XONG', k
    assert b.ram._ban_ghi.du_lieu['alias_nguyen_van'][ALIAS] == ten


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('sai', ['thieu_doan', 'overlap', 'dao_thu_tu', 'chua_giao_het'])
def test_nhieu_doan_phai_du_va_khop_overlap(loai, sai):
    chu = ('nội dung; ' * 710) + TEN + '; ' + ('nội dung; ' * 220)
    b = bo(loai, raw=word(chu) if loai == 'docx' else excel(chu))
    chuan_bi_het(b)
    assert len(b.cong.giao) > 1
    def sua(v):
        if sai == 'thieu_doan': v['phan_hoi'].pop(0)
        elif sai == 'dao_thu_tu': v['phan_hoi'].reverse()
        elif sai == 'overlap':
            p = v['phan_hoi'][0]['tra_loi_ai']['tra_loi_ai']
            p['du_lieu']['thuc_the'] = []
            p['trich_dan'] = []
            p['trang_thai'] = 'khong_thay_can_cu'
        return v
    giao(b, sua=sua)
    if sai == 'chua_giao_het': b.ram._ban_ghi.du_lieu['ho_so_tep']['da_giao'].pop(0)
    loi_khong_phat_hanh(b, chay(b))


def test_local_khong_ghep_thuc_the_qua_hai_o_doc_lap():
    raw = excel(noi_dung='<row r="1"><c r="A1" t="inlineStr"><is><t>zest</t></is></c>'
                        '<c r="B1" t="inlineStr"><is><t>oria</t></is></c></row>')
    b = bo('xlsx', raw=raw, seeds=())
    chuan_bi_het(b)
    h = b.ram._ban_ghi.du_lieu['ho_so_tep']
    a = h['map_quy_tac'].goc.index('zest')
    giao(b, spans=[(a, a+len('zest\noria'), 'to_chuc', 'chac')])
    loi_khong_phat_hanh(b, chay(b), ma='MASK_AI_CON_SOT')


def test_ngu_canh_o_so_bat_bien_co_local_va_khong_patch_so():
    raw = excel(noi_dung='<row r="1"><c r="A1" t="inlineStr"><is><t>giá trị</t></is></c>'
                        '<c r="B1"><v>1000000</v></c></row>')
    b = bo('xlsx', raw=raw, seeds=())
    chuan_bi_het(b)
    h = b.ram._ban_ghi.du_lieu['ho_so_tep']
    goc = h['map_quy_tac'].goc
    assert 'giá trị\n1000000' in goc
    a = goc.index('1000000')
    giao(b, spans=[(a, a+7, 'to_chuc', 'chac')])
    loi_khong_phat_hanh(b, chay(b))


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_spy_khong_luu_ho_so_map_goc_ngoai_local(monkeypatch, capsys, caplog, loai):
    import builtins
    import io
    b = bo(loai)
    mo, io_mo = builtins.open, io.open
    def spy(ham):
        def goi(tep, mode='r', *a, **kw):
            assert not any(k in mode for k in ('w', 'a', 'x', '+'))
            return ham(tep, mode, *a, **kw)
        return goi
    with monkeypatch.context() as mp:
        mp.setattr(builtins, 'open', spy(mo))
        mp.setattr(io, 'open', spy(io_mo))
        chuan_bi_het(b)
        giao(b)
        k = chay(b)
        assert k['trang_thai'] == 'XONG', k
    assert len(b.c._tep) == 1  # Chỉ tệp người dùng đã đưa vào, không snapshot.
    for ten, kw in b.cong.cac_cua:
        if ten == 'ban_giao' and 'yeu_cau' in kw:
            y = json.loads(kw['yeu_cau'])
            assert TEN not in json.dumps(y['yeu_cau_ai']['chuyen_tiep'], ensure_ascii=False)
            continue  # Chỉ đoạn Local được phép mang nguyên văn.
        assert TEN not in repr(kw)
    # Inspector CoreGia thấy cả dữ liệu seed của cột bí mật; engine chỉ
    # đọc null+cờ (đã assert trong chot_metadata), metadata không có tên.
    for dong in b.c.xem_ngan('e_mask', 'dinh_danh'):
        assert TEN not in repr({k: v for k, v in dong.items() if k not in {'gia_tri_goc', 'gia_tri_chuan'}})
    assert capsys.readouterr() == ('', '') and not caplog.records


@pytest.mark.parametrize('cua', ['kiem_tep', 'nhan_phan_hoi', 'chung_thuc', 'truoc_chot'])
def test_ngoai_le_port_khong_ro_goc_stderr(capsys, caplog, cua):
    b = bo()
    if cua != 'kiem_tep':
        chuan_bi_het(b)
        giao(b)
    def moc(ten, v):
        if ten == cua: raise RuntimeError(TEN)
    b.cong.moc = moc
    k = chay(b)
    loi_khong_phat_hanh(b, k)
    assert TEN not in repr(k)
    assert capsys.readouterr() == ('', '') and not caplog.records


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('giai_doan', ['chuan_bi', 'hau_kiem'])
def test_huy_giua_handler_khong_tai_tao_map(loai, giai_doan):
    b = bo(loai)
    if giai_doan == 'hau_kiem':
        chuan_bi_het(b)
        giao(b)
    def moc(ten, v):
        if ten == ('ban_giao' if giai_doan == 'chuan_bi' else 'chung_thuc'):
            b.q.bao_ram(b.ctx.ma_yeu_cau, 'HUY')
    b.cong.moc = moc
    loi_khong_phat_hanh(b, chay(b), ma='MASK_ANH_XA_KHONG_CON')


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_retry_cung_ma_tep_doi_chan_va_don(loai):
    b = bo(loai)
    chuan_bi_het(b)
    ten, mime, raw = b.c._tep[b.ref['tep_id']]
    b.c._tep[b.ref['tep_id']] = (ten, mime, raw[:-1] + bytes([raw[-1] ^ 1]))
    b.v = b.c.giao_viec(CHUAN_BI, b.dau)
    b.q.cap(b.v, ma_yeu_cau=b.ctx.ma_yeu_cau)
    loi_khong_phat_hanh(b, chay(b))


@pytest.mark.parametrize('dang', ['tokenizer', 'provider', 'token_vao', 'han'])
def test_ngan_sach_chua_do_hoac_qua_tran_khong_gui_local(dang):
    b = bo()
    goc = b.cong.kiem_ngan_sach
    def sai(*a, **kw):
        bn = goc(*a, **kw)
        if dang == 'tokenizer': bn['tung_doan_da_do'] = False
        elif dang == 'provider': bn['nha_cung_cap'] = 'cloud'
        elif dang == 'token_vao': bn['token_vao'] = [bn['context_token']]
        elif dang == 'han': b.cong.con_han = False
        return bn
    b.cong.kiem_ngan_sach = sai
    loi_khong_phat_hanh(b, chay(b))
    assert not b.cong.giao


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_lop_mot_loi_khong_duoc_goi_local_cuu(loai):
    b = bo(loai, seeds=())
    loi_khong_phat_hanh(b, chay(b))
    assert not b.cong.giao


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_mat_ack_upload_khong_tra_tep_do_va_don(loai):
    b = bo(loai, dang='tep')
    chuan_bi_het(b)
    giao(b)
    b.c.gay_mat_xac_nhan('tep', 4)
    k = chay(b)
    assert k['trang_thai'] == 'CHUA_RO' and k['ket_qua'] is None, k
    assert b.ram._ban_ghi is None and b.cong.dem_chot == 1
    assert not b.cong.giao_cuoi
    # Một upload bản CHE được SDK nhận; Core phải cách ly/thu hồi C-P4-05.
    assert b.c.so_lan_ghi['tep'] == 1


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_sdk_mat_ack_ket_qua_retry_cung_idempotency_khong_chot_hai_lan(loai):
    b = bo(loai)
    chuan_bi_het(b)
    giao(b)
    b.c.gay_mat_xac_nhan('ket_qua', 1)
    k = chay(b)
    assert k['trang_thai'] == 'XONG', k
    assert b.cong.dem_chot == 1 and len(b.cong.giao_cuoi) == 1


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_nguon_ma_caller_khong_cap_quyen(loai):
    b = bo(loai)
    chuan_bi_het(b)
    giao(b)
    dau = deepcopy(b.bundle['phan_hoi'][-1]['tra_loi_ai'])
    dau['tra_loi_ai']['chuyen_tiep']['mask_2c']['ma_yeu_cau'] = 'caller-tu-cap'
    b.c._viec[b.v]['dau_vao'] = dau
    loi_khong_phat_hanh(b, chay(b), ma='MASK_AI_NGUON')


def test_word_scalar_so_khong_co_mien_patch_phai_chan_lop_mot():
    from io import BytesIO
    from zipfile import ZipFile
    from ho_tro_mask_b2 import zip_office
    with ZipFile(BytesIO(moi_vung_co_ten())) as z:
        phan = {n: z.read(n) for n in z.namelist()}
    assert b'<cp:revision>1</cp:revision>' in phan['docProps/core.xml']
    phan['docProps/core.xml'] = phan['docProps/core.xml'].replace(
        b'<cp:revision>1</cp:revision>', b'<cp:revision>0101234567</cp:revision>')
    b = bo(raw=zip_office(phan))
    loi_khong_phat_hanh(b, chay(b), ma='MASK_TEP_CHUA_HO_TRO')
    assert not b.cong.giao
