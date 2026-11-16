"""B8: tệp AI giả lập; đã kiểm bằng Core giả (CoreGia), chưa Office thật."""
from hashlib import sha256
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import io
import json
import unicodedata
import zipfile

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, NganEngine, Viec, ViecDaHuy

from e_mask.doc_word import doc_word
from e_mask.doc_excel import doc_excel
from e_mask.kho_anh_xa_ram import KhoAnhXaRAM
from e_mask.va_xml import chu_vung, goi_cua
from ho_tro_mask_b2 import zip_office
from ho_tro_mask_b3 import goi_office
from ho_tro_mask_b5 import TEN, ALIAS, word, moi_vung_co_ten
from ho_tro_mask_b6 import excel, moi_vung
from ho_tro_mask_b8 import bo, giao, chay, ket, da_don


def parts(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        return {n: z.read(n) for n in z.namelist()}


def sua(raw, ham, *, cach=8):
    p = parts(raw)
    ham(p)
    return goi_office(p, cach=cach, co=0 if cach == 0 else 6)


def doi_alias(raw, loai, alias):
    phan = 'word/document.xml' if loai == 'docx' else 'xl/worksheets/sheet1.xml'
    def doi(p):
        assert ALIAS.encode() in p[phan]
        p[phan] = p[phan].replace(ALIAS.encode(), alias.encode())
    return sua(raw, doi)


def loi(b, ma='MASK_MO_CHE_KHONG_DAY_DU'):
    k = chay(b)
    assert k['trang_thai'] == 'LOI' and k['ket_qua'] is None, k
    assert k['loi']['ma'] == ma, k
    assert TEN not in json.dumps(k, ensure_ascii=False)
    assert b.ket is None and not b.c.ket_qua_cuoi_demo
    return k


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('dong', [True, False])
def test_khong_sua_tra_chinh_bytes_goc_ram_va_tieu_thu(loai, dong):
    b = bo(loai)
    giao(b, dong=dong)
    k = ket(b)
    assert k.du_lieu is b.goc_ram
    assert k.du_lieu == b.raw
    assert k.bam_ket_qua == 'sha256:' + sha256(b.raw).hexdigest()
    assert k.nguyen_bytes and k.so_cho_mo > 0
    assert b.mo.so_nhan == 1 and b.mo.da_tieu_thu == [True]
    assert set(vars(b.opener)) == {'ram', 'quyen', 'cong'}
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('alias', [ALIAS.lower(), '[ [ MASKCT-0001 ] ]',
    ' '.join(ALIAS), '\u00a0'.join(ALIAS), '[\n[ MASKCT-0001 ]\t]'])
def test_case_space_chi_mo_trong_map_duy_nhat(loai, alias):
    b = bo(loai)
    giao(b, doi_alias(b.da_che, loai, alias))
    k = ket(b)
    assert not k.nguyen_bytes
    doc = (doc_word if loai == 'docx' else doc_excel)(k.du_lieu, kiem_huy=lambda: None)
    assert any(chu_vung(v) == TEN for v in doc.vung)
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_ai_tach_run_them_noi_dung_format_tien_ngay_giu_bytes_bat_bien(loai):
    b = bo(loai)
    def doi(p):
        if loai == 'docx':
            t = p['word/document.xml'].decode()
            t = t.replace(ALIAS, '[[mas</w:t></w:r><w:r><w:rPr><w:b/><w:i/></w:rPr>'
                          '<w:t>kct- 0001]]')
            t = t.replace('</w:body>', '<w:p><w:r><w:rPr><w:b/></w:rPr><w:t>'
                'AI thêm 2.500.000 VND ngày 2026-11-16; DEMO mới.</w:t></w:r></w:p></w:body>')
            p['word/document.xml'] = t.encode()
        else:
            t = p['xl/worksheets/sheet1.xml'].decode().replace('<is><t>' + ALIAS + '</t></is>',
                '<is><r><rPr><b/></rPr><t>[[mas</t></r><r><rPr><i/></rPr>'
                '<t>kct- 0001]]</t></r></is>')
            t = t.replace('</row>', '<c r="B1" t="inlineStr"><is><t>'
                'AI thêm 2.500.000 VND ngày 2026-11-16; DEMO mới.</t></is></c>'
                '<c r="C1" t="n"><v>2500000.00</v></c></row>')
            p['xl/worksheets/sheet1.xml'] = t.encode()
    raw = sua(b.da_che, doi)
    truoc = (doc_word if loai == 'docx' else doc_excel)(raw, kiem_huy=lambda: None)
    giao(b, raw)
    k = ket(b)
    sau = (doc_word if loai == 'docx' else doc_excel)(k.du_lieu, kiem_huy=lambda: None)
    assert not k.nguyen_bytes and k.du_lieu != b.raw
    assert any('AI thêm 2.500.000 VND ngày 2026-11-16; DEMO mới.' in chu_vung(v) for v in sau.vung)
    assert any(chu_vung(v) == TEN for v in sau.vung)
    a, z = goi_cua(truoc).zip, goi_cua(sau).zip
    for x, y in zip(a.phan, z.phan):
        if x.du_lieu == y.du_lieu:
            assert a.goc[x.le_dau:x.le_cuoi] == z.goc[y.le_dau:y.le_cuoi]
    # Kiểm markup literal bên ngoài vùng thay, gồm run rỗng vẫn có format.
    thay = 'word/document.xml' if loai == 'docx' else 'xl/worksheets/sheet1.xml'
    p = parts(k.du_lieu)
    assert (b'<w:rPr><w:b/><w:i/></w:rPr>' if loai == 'docx' else b'<rPr><i/></rPr>') in p[thay]
    if loai == 'xlsx':
        assert b'<c r="C1" t="n"><v>2500000.00</v></c>' in p[thay]
    da_don(b)


def test_excel_shared_rich_runs_nhieu_o_giu_index_format_merge_so_tien_ngay():
    b = bo('xlsx', raw=moi_vung())
    def doi(p):
        p['xl/sharedStrings.xml'] = p['xl/sharedStrings.xml'].replace(ALIAS.encode(),
            b'[[maskct- 0001]]')
        # Thay giá trị AI trên chính ô số: mở phải giữ giá trị MỚI, không trả gốc.
        p['xl/worksheets/sheet1.xml'] = p['xl/worksheets/sheet1.xml'].replace(b'>1000000<', b'>2750000.00<')
    raw = sua(b.da_che, doi)
    a = doc_excel(raw, kiem_huy=lambda: None)
    giao(b, raw)
    k = ket(b)
    z = doc_excel(k.du_lieu, kiem_huy=lambda: None)
    assert (z.shared, z.tham_chieu_chu, z.styles, z.gop_o, z.epoch1904) == (
        a.shared, a.tham_chieu_chu, a.styles, a.gop_o, a.epoch1904)
    for x, y in zip(a.o, z.o):
        if x.vung is None:
            assert x.xml_goc == y.xml_goc
    assert any(o.gia_tri == '2750000.00' for o in z.o)
    assert any(o.gia_tri == '46325' for o in z.o)
    assert any(o.hang_an for o in z.o) and any(o.cot_an for o in z.o)
    assert all(ALIAS not in chu_vung(v) for v in z.vung)
    da_don(b)


@pytest.mark.parametrize('loai,raw', [('docx', moi_vung_co_ten), ('xlsx', moi_vung)])
@pytest.mark.parametrize('sua_ai', [True, False])
def test_mo_moi_vung_da_nhan_ke_ca_metadata_story_attribute(loai, raw, sua_ai):
    b = bo(loai, raw=raw())
    raw_ai = b.da_che
    if sua_ai:
        raw_ai = sua(raw_ai, lambda p: p.update({t: v.replace(ALIAS.encode(), ALIAS.lower().encode())
                                                 for t, v in p.items()}))
    giao(b, raw_ai)
    k = ket(b)
    doc = (doc_word if loai == 'docx' else doc_excel)(k.du_lieu, kiem_huy=lambda: None)
    assert all(ALIAS not in chu_vung(v) for v in doc.vung)
    assert sum(TEN in chu_vung(v) for v in doc.vung) >= 5
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('ten', [unicodedata.normalize('NFD', TEN),
    'Công\u200b ty DEMO Ánh Dương', 'Công ty  DEMO\u00a0Ánh Dương'])
def test_khoi_phuc_nguyen_van_nfd_cf_space_khong_che_lai(loai, ten):
    raw = (word if loai == 'docx' else excel)(ten)
    b = bo(loai, raw=raw, seeds=((ten, 'CONG_TY', ALIAS),))
    giao(b, doi_alias(b.da_che, loai, ALIAS.lower()))
    doc = (doc_word if loai == 'docx' else doc_excel)(ket(b).du_lieu, kiem_huy=lambda: None)
    assert any(chu_vung(v) == ten for v in doc.vung)
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('hong', ['[[MASKCT-NGOAI-0002]]', '[[KH-NGOAI-009]]', '[[KH-LA]]',
    '[[MASKCT-0001]', '[MASKCT-0001]]', 'MASKCT-0001', 'MASKCT-000?',
    '[[MASKCT-000?]]', '[[MASKCT-0001', '[[MASKCT-0001]]]', '[[[MASKCT-0001]]',
    '[[MASKCT-0001\u200b]]', 'M A S K C T - 0 0 0 2', ''])
def test_alias_la_hong_thieu_chan_khong_tra_mot_phan(loai, hong, capsys):
    b = bo(loai)
    giao(b, doi_alias(b.da_che, loai, hong))
    loi(b)
    assert b.mo.so_nhan == 0
    da_don(b)
    assert capsys.readouterr() == ('', '')


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_alias_ngoai_yeu_cau_ke_ca_da_co_trong_kho_khong_tra_nguoc(loai, monkeypatch):
    b = bo(loai, seeds=((TEN, 'CONG_TY', ALIAS), ('Công ty DEMO Mặt Trăng', 'CONG_TY', '[[KH-NGOAI-009]]')))
    def cam(*a, **kw):
        pytest.fail('Cửa mở không được đọc kho hoặc tải bản gốc/map.')
    monkeypatch.setattr(NganEngine, 'tim', cam)
    monkeypatch.setattr(NganEngine, 'doc', cam)
    monkeypatch.setattr(Viec, 'mo_tep', cam)
    monkeypatch.setattr(Viec, 'tai_tep_ra', cam)
    giao(b, doi_alias(b.da_che, loai, ALIAS + ' [[KH-NGOAI-009]]'))
    loi(b)
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('hong', ['map_thieu', 'map_them', 'map_mo_ho', 'map_bam', 'goc_bam',
    'che_bam', 'chua_local', 'thieu_vung_local', 'dang_tra', 'thieu_ho_so'])
def test_map_ram_hong_thieu_mo_ho_khong_thanh_cong_gia(loai, hong):
    b = bo(loai)
    du = b.bg.du_lieu
    s = du['tep_word' if loai == 'docx' else 'tep_excel']
    if hong == 'map_thieu': du['alias_nguyen_van'].clear()
    elif hong == 'map_them': du['alias_nguyen_van']['[[KH-LA]]'] = 'Tên DEMO khác'
    elif hong == 'map_mo_ho': du['alias_nguyen_van'][ALIAS] = [TEN, TEN.upper()]
    elif hong == 'map_bam': du['anh_xa_cuoi'] = replace(du['anh_xa_cuoi'], bam_da_che='sha256:' + '0' * 64)
    elif hong == 'goc_bam': s['goc'] += b'X'
    elif hong == 'che_bam': s['da_che'] += b'X'
    elif hong == 'chua_local': du['giai_doan_ai'] = 'CHO_LOCAL'
    elif hong == 'thieu_vung_local': s['vung_da_kiem_local'] = ()
    elif hong == 'dang_tra': du['ho_so_tep']['dang_tra'] = 'van_ban'
    else: du.pop('ho_so_tep')
    giao(b)
    loi(b, 'MASK_VONG_DOI_KHONG_HOP_LE' if hong == 'chua_local' else
        'MASK_ANH_XA_KHONG_CON' if hong == 'thieu_ho_so' else 'MASK_MO_CHE_KHONG_DAY_DU')
    assert b.mo.so_nhan == 0
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('sai', ['module', 'nguoi_gui', 'tai_lieu', 'vung', 'phap_nhan', 'instance', 'ma_caller'])
def test_quyen_nguon_tin_cay_khong_don_map_nguoi_khac(loai, sai):
    b = bo(loai)
    giao(b, ma='caller-DEMO' if sai == 'ma_caller' else None)
    if sai in {'module', 'nguoi_gui', 'tai_lieu'}: setattr(b.q, sai, 'khac-DEMO')
    elif sai == 'vung': b.q.vung = 'THAT'
    elif sai == 'phap_nhan': b.q.ram_sua_ctx = lambda c: replace(c, phap_nhan_id='pn-khac-DEMO')
    elif sai == 'instance': b.q.ram_sua_ctx = lambda c: replace(c, instance='instance-khac-DEMO')
    loi(b, 'MASK_ANH_XA_KHONG_CON' if sai == 'instance' else 'MASK_MA_YEU_CAU')
    assert b.mo.so_nhan == 0
    if sai != 'ma_caller':
        assert b.ram._ban_ghi is b.bg  # Một việc sai quyền không được phá map chủ.
        b.dh.tien(600)
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('ly_do', ['ttl', 'deadline', 'restart', 'worker', 'HUY', 'LOI', 'KET_THUC', 'MAT_LEASE'])
def test_mat_ram_restart_khac_worker_huy_ranh_khong_phuc_hoi(loai, ly_do):
    b = bo(loai)
    if ly_do == 'ttl': b.dh.tien(600)
    elif ly_do == 'deadline':
        b.q.ram_han = b.dh() + 5
        b.dh.tien(5)
    elif ly_do == 'restart':
        b.opener.ram = KhoAnhXaRAM(quyen=b.q, dong_ho=b.dh, hen_gio=b.dh.hen_gio)
    elif ly_do == 'worker': b.q.ram_sua_ctx = lambda c: replace(c, instance='worker-DEMO')
    else: b.q.bao_ram(b.ctx.ma_yeu_cau, ly_do)
    giao(b)
    loi(b, 'MASK_ANH_XA_KHONG_CON')
    assert b.mo.so_nhan == 0
    b.dh.tien(601)
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('moc', ['kiem_tep_truoc', 'kiem_tep_sau', 'vao', 'nhan', 'ra'])
@pytest.mark.parametrize('su_kien', ['HUY', 'TTL', 'MAT_LEASE'])
def test_timeout_huy_dua_mo_khong_phat_hanh(loai, moc, su_kien):
    b = bo(loai)
    def chen(ten, v):
        if ten != moc: return
        if su_kien == 'TTL': b.dh.tien(600)
        else:
            b.q.bao_ram(b.ctx.ma_yeu_cau, su_kien)
            if moc == 'ra': b.q.thu_hoi = True
    b.mo.moc = chen
    giao(b)
    loi(b, 'MASK_ANH_XA_KHONG_CON' if moc != 'ra' or su_kien == 'TTL' else 'MASK_MA_YEU_CAU')
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('mat_ack', ['nhan', 'ra'])
def test_mat_ack_chua_ro_khong_cache_ban_ro_khong_mo_lai(loai, mat_ack):
    b = bo(loai)
    b.mo.mat_ack = mat_ack
    giao(b)
    k = chay(b)
    assert k['trang_thai'] == 'CHUA_RO' and k['ket_qua'] is None, k
    assert 'chuoi-tu-nguon' not in json.dumps(k)
    assert b.ket is None
    da_don(b)
    assert len(b.c.ket_qua_cuoi_demo) == (1 if mat_ack == 'ra' else 0)
    b.c.ket_qua_cuoi_demo.clear()
    giao(b)
    loi(b, 'MASK_ANH_XA_KHONG_CON')
    assert b.mo.so_nhan == 1
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('sai', ['thieu_kiem', 'thieu_giao', 'budget', 'acl'])
def test_thieu_cong_hoac_budget_quyen_tep_khong_du_thi_chan(loai, sai):
    b = bo(loai)
    if sai == 'thieu_kiem': b.mo.kiem_tep_mo = None
    elif sai == 'thieu_giao': b.mo.ban_giao_cuoi = None
    elif sai == 'budget': b.mo.budget = False
    else: b.mo.kiem_tep = False
    giao(b)
    loi(b, 'MASK_MO_CHE_CHUA_CO_CUA_CORE')
    assert b.mo.so_nhan == 0
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_khong_co_tac_dung_ghi_kho_upload_tam_log_hoac_ho_so(loai, monkeypatch, capsys):
    b = bo(loai)
    def cam(*a, **kw):
        pytest.fail('B8 không có cửa ghi map/gốc/tra kho/upload.')
    monkeypatch.setattr(NganEngine, 'tim', cam)
    monkeypatch.setattr(NganEngine, 'doc', cam)
    monkeypatch.setattr(NganEngine, 'lo', cam)
    monkeypatch.setattr(Viec, 'mo_tep', cam)
    monkeypatch.setattr(Viec, 'tai_tep_ra', cam)
    monkeypatch.setattr('builtins.open', cam)
    giao(b, doi_alias(b.da_che, loai, ALIAS.lower()))
    n = len(b.c._tep)
    k = ket(b)
    assert len(b.c._tep) == n
    assert TEN not in json.dumps(b.mo.cua, ensure_ascii=False)
    assert TEN not in json.dumps(b.c.nhat_ky, ensure_ascii=False)
    assert len(b.c.ket_qua_cuoi_demo) == 1
    assert list(b.c.ket_qua_cuoi_demo.values()) == [k.du_lieu]
    assert capsys.readouterr() == ('', '')
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_double_open_hai_luong_mot_lan_ban_giao_sau_do_khong_retry(loai):
    b = bo(loai)
    loi_hai = []
    def chen(ten, v):
        if ten != 'vao': return
        def mo_hai():
            try:
                b.opener.mo(v, b.raw_mo, loai=loai, ma_yeu_cau=b.ctx.ma_yeu_cau)
            except LoiNghiepVu as exc:
                loi_hai.append(exc.ma)
        with ThreadPoolExecutor(max_workers=1) as pool:
            pool.submit(mo_hai).result(timeout=10)
    b.mo.moc = chen
    giao(b)
    ket(b)
    assert loi_hai == ['MASK_ANH_XA_KHONG_CON'] and b.mo.so_nhan == 1
    da_don(b)
    b.ket = None
    b.c.ket_qua_cuoi_demo.clear()
    giao(b)
    loi(b, 'MASK_ANH_XA_KHONG_CON')
    assert b.mo.so_nhan == 1


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('codec', ['utf-8-sig', 'utf-16', 'utf-16-be'])
def test_ai_luu_doi_encoding_va_entity_van_patch_dung_bytes(loai, codec):
    b = bo(loai)
    def doi(p):
        phan = 'word/document.xml' if loai == 'docx' else 'xl/worksheets/sheet1.xml'
        p[phan] = p[phan].decode().replace(ALIAS, '&#91;[maskct-0001]&#93;').encode(codec)
    giao(b, sua(b.da_che, doi))
    k = ket(b)
    doc = (doc_word if loai == 'docx' else doc_excel)(k.du_lieu, kiem_huy=lambda: None)
    assert any(chu_vung(v) == TEN for v in doc.vung)
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('hong', ['phan_la', 'dtd', 'xml_comment', 'pi', 'markup', 'sai_dinh_dang'])
def test_ai_them_vung_khong_tin_cay_tu_choi_ca_goi(loai, hong):
    b = bo(loai)
    def doi(p):
        phan = 'word/document.xml' if loai == 'docx' else 'xl/worksheets/sheet1.xml'
        if hong == 'phan_la': p['DEMO-la.xml'] = b'<DEMO/>'
        elif hong == 'dtd': p[phan] = b'<!DOCTYPE a [<!ENTITY x "DEMO">]>' + p[phan]
        elif hong == 'xml_comment': p[phan] = b'<!--DEMO-->' + p[phan]
        elif hong == 'pi': p[phan] = b'<?DEMO x?>' + p[phan]
        elif hong == 'markup':
            if loai == 'docx': p[phan] = p[phan].replace(b'<w:p>', b'<w:p><w:commentRangeStart w:id="0"/>', 1)
            else: p[phan] = p[phan].replace(b'<v>', b'<f>DEMO()</f><v>', 1) if b'<v>' in p[phan] else p[phan].replace(b'<is>', b'<f>DEMO()</f><is>', 1)
        else: p[phan] = b'<DEMO xmlns="urn:DEMO"/>'
    giao(b, sua(b.da_che, doi))
    loi(b, 'MASK_TEP_CHUA_HO_TRO')
    assert b.mo.so_nhan == 0
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('hong', ['container', 'ratio', 'so_ky_tu'])
def test_tran_vao_khong_cat_ngam_va_don(loai, hong):
    b = bo(loai)
    if hong == 'container': raw = b'X' * (1048576 + 1)
    else:
        def doi(p):
            phan = 'word/document.xml' if loai == 'docx' else 'xl/worksheets/sheet1.xml'
            p[phan] = p[phan].replace(ALIAS.encode(), ALIAS.encode() + b'X' * (500001 if hong == 'so_ky_tu' else 50000))
        raw = sua(b.da_che, doi, cach=0 if hong == 'so_ky_tu' else 8)
    giao(b, raw)
    loi(b, 'MASK_QUA_GIOI_HAN')
    da_don(b)


def test_tran_ra_khuech_dai_word_tu_choi_truoc_ghi_tra():
    ten = 'Công ty DEMO ' + 'Ánh ' * 20 + 'Dương'
    b = bo('docx', raw=word(ten), seeds=((ten, 'CONG_TY', ALIAS),))
    def doi(p):
        p['word/document.xml'] = p['word/document.xml'].replace(ALIAS.encode(), (ALIAS.encode() + b'; ') * 22000)
    giao(b, sua(b.da_che, doi, cach=0))
    loi(b, 'MASK_QUA_GIOI_HAN')
    assert b.mo.so_nhan == 0
    da_don(b)


def test_excel_mo_vuot_tran_o_khong_cat_32767():
    ten = 'Công ty DEMO ' + 'Ánh ' * 20 + 'Dương'
    b = bo('xlsx', raw=excel(ten), seeds=((ten, 'CONG_TY', ALIAS),))
    giao(b, doi_alias(b.da_che, 'xlsx', (ALIAS + '; ') * 400))
    loi(b, 'MASK_QUA_GIOI_HAN')
    da_don(b)


@pytest.mark.parametrize('ten', ['MASKCT-0001', 'M A S K C T - 0 0 0 1'])
def test_khong_doi_ten_sheet_mu_ke_ca_mat_ngoac(ten):
    b = bo('xlsx')
    giao(b, sua(b.da_che, lambda p: p.update({'xl/workbook.xml':
        p['xl/workbook.xml'].replace('bảng'.encode(), ten.encode())})))
    loi(b)
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('moc', ['kiem_tep_sau', 'nhan'])
def test_dau_vao_doi_giua_luot_khong_ban_giao(loai, moc):
    b = bo(loai)
    def chen(ten, v):
        if ten == moc: v.tham_so['dong_viec'] = not v.tham_so['dong_viec']
    b.mo.moc = chen
    giao(b)
    loi(b, 'MASK_DAU_VAO_THAY_DOI')
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_huy_truoc_handler_van_don_map_dung_chu(loai):
    b = bo(loai)
    giao(b)
    ham = b.app._ham['mask.mo_che_van_ban@1']
    def huy(v):
        v.kiem_huy = lambda: (_ for _ in ()).throw(ViecDaHuy())
        return ham(v)
    b.app._ham['mask.mo_che_van_ban@1'] = huy
    k = chay(b)
    assert k['trang_thai'] == 'HUY' and k['ket_qua'] is None
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('moc', ['kiem_tep_sau', 'nhan', 'ra'])
def test_loi_nguon_chua_noi_dung_khong_lo_stderr_log(loai, moc, capsys):
    b = bo(loai)
    def chen(ten, v):
        if ten == moc: raise RuntimeError(TEN + ' đường-máy-DEMO')
    b.mo.moc = chen
    giao(b)
    loi(b, 'MASK_TEP_RAM')
    assert capsys.readouterr() == ('', '')
    assert TEN not in json.dumps(b.c.nhat_ky, ensure_ascii=False)
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('moc', ['nhan', 'ra'])
def test_timeout_ack_sau_nhan_la_chua_ro_va_don(loai, moc):
    b = bo(loai)
    def chen(ten, v):
        if ten == moc: raise TimeoutError(TEN)
    b.mo.moc = chen
    giao(b)
    k = chay(b)
    assert k['trang_thai'] == 'CHUA_RO' and k['ket_qua'] is None, k
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_admin_duyet_giua_chuoi_khong_doi_map_da_ghim(loai):
    from e_mask.duyet_dinh_danh import DuyetDinhDanh
    from test_mask_r7 import QuyenAdminGia
    b = bo(loai)
    # Một việc Admin thật trên ngăn SDK giả, dùng biên nhận R7 đúng ID/version.
    # Đưa tên hiện có về chờ duyệt rồi cấp alias mới; map chuỗi vẫn giữ alias cũ.
    giao(b, doi_alias(b.da_che, loai, ALIAS.lower()))
    mo = b.app._ham['mask.mo_che_van_ban@1']
    def duyet(v):
        ds = v.ngan.tim('dinh_danh', loc={'vung_du_lieu': 'DEMO'}).danh_sach
        dong = next(d for d in ds if d.gia_tri['nhom'] == 'CONG_TY')
        ma = dong.gia_tri['id_dinh_danh']
        with v.ngan.lo() as lo:
            lo.sua('dinh_danh', {'id_dinh_danh': ma}, {'trang_thai': 'CHO_DUYET'}, row_version=dong.row_version)
        phien = v.ngan.doc('dinh_danh', {'id_dinh_danh': ma}).row_version
        q = QuyenAdminGia()
        ve = q.xem_tai_core(ma, phien)
        k = DuyetDinhDanh(v, q).duyet(ma, phien, bien_nhan=ve, ma_junsky='DEMO-MOI-0002')
        assert k['bi_danh'] == '[[DEMO-MOI-0002]]'
        assert b.bg.du_lieu['alias_nguyen_van'] == {ALIAS: TEN}
        return mo(v)
    b.app._ham['mask.mo_che_van_ban@1'] = duyet
    k = ket(b)
    doc = (doc_word if loai == 'docx' else doc_excel)(k.du_lieu, kiem_huy=lambda: None)
    assert any(chu_vung(v) == TEN for v in doc.vung)
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('trong', ['doc', 'patch'])
def test_het_han_ngay_trong_reader_patch_khong_co_bytes_ra(loai, trong, monkeypatch):
    from e_mask import mo_tep_word, mo_tep_excel
    b = bo(loai)
    giao(b, doi_alias(b.da_che, loai, ALIAS.lower()))
    if trong == 'doc':
        module = mo_tep_word if loai == 'docx' else mo_tep_excel
        ten = 'doc_word' if loai == 'docx' else 'doc_excel'
        doc = getattr(module, ten)
        n = 0
        def het(*a, **kw):
            nonlocal n
            k = doc(*a, **kw)
            n += 1
            if n == 3: b.dh.tien(600)
            return k
        monkeypatch.setattr(module, ten, het)
    else:
        lap = mo_tep_word.lap_kich_ban
        def het(*a, **kw):
            k = lap(*a, **kw)
            b.dh.tien(600)
            return k
        monkeypatch.setattr(mo_tep_word, 'lap_kich_ban', het)
    loi(b, 'MASK_ANH_XA_KHONG_CON')
    assert b.mo.so_nhan == 0
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_map_rong_hop_le_khong_co_alias_van_tra_nguyen_bytes(loai):
    raw = (word if loai == 'docx' else excel)('kiểm tra dữ liệu giả.')
    b = bo(loai, raw=raw, seeds=())
    giao(b)
    k = ket(b)
    assert k.du_lieu is b.goc_ram and k.so_cho_mo == 0
    da_don(b)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_so_tai_khoan_vua_mo_khong_bi_detector_che_lai(loai, monkeypatch):
    from e_mask import che_van_ban
    so, alias = '1234567890123', '[[MASKTK-0001]]'
    raw = (word if loai == 'docx' else excel)('Tài khoản: ' + so)
    b = bo(loai, raw=raw, seeds=((so, 'TAI_KHOAN', alias),))
    def cam(*a, **kw):
        pytest.fail('Không được che lại số định danh vừa mở.')
    monkeypatch.setattr(che_van_ban, 'thu_thap_ung_vien', cam)
    def doi(p):
        t = 'word/document.xml' if loai == 'docx' else 'xl/worksheets/sheet1.xml'
        p[t] = p[t].replace(alias.encode(), alias.lower().encode())
    giao(b, sua(b.da_che, doi))
    k = ket(b)
    doc = (doc_word if loai == 'docx' else doc_excel)(k.du_lieu, kiem_huy=lambda: None)
    assert any(chu_vung(v) == 'Tài khoản: ' + so for v in doc.vung)
    da_don(b)
