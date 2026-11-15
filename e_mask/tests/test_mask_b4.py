"""MASK-B4 DEMO: bytes bất biến, map giả, writer có trần và hủy nguyên tử."""

from dataclasses import replace
from hashlib import sha256
import io
import socket
import struct
import zipfile
import zlib

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu

from e_mask import ghi_zip as writer, va_xml as va, zip_an_toan as za
from e_mask.doc_excel import doc_excel, ExcelDaDoc
from e_mask.doc_word import doc_word, TaiLieuWord
from ho_tro_mask_b1 import W, S, dong_goi, word_demo, excel_demo
from ho_tro_mask_b2 import zip_office, word_day_du
from ho_tro_mask_b3 import goi_office, phan_demo
from ho_tro_mask_b4 import (
    khong_huy as kh, mau, mau_chu, liet_ke, xoa_truong_muc,
)

DOC = {'docx': doc_word, 'xlsx': doc_excel}


def chu(v):
    return v.van_ban if hasattr(v, 'van_ban') else v.chu


def vung_chinh(tl):
    if type(tl) is TaiLieuWord:
        return next(i for i, v in enumerate(tl.vung) if v.loai == 'than' and v.van_ban)
    return next(i for i, v in enumerate(tl.vung) if v.ma == 'shared_string') if tl.shared else next(
        i for i, v in enumerate(tl.vung) if v.ma == 'o')


def lenh(tl, text='[[MASKCT-0001]]', *, vi=None, dau=0, cuoi=None):
    vi = vung_chinh(tl) if vi is None else vi
    cuoi = len(chu(tl.vung[vi])) if cuoi is None else cuoi
    return va.lap_kich_ban(tl, ((vi, dau, cuoi, text),), kiem_huy=kh)


def bi_chan(thao_tac, ma='MASK_TEP_CHUA_HO_TRO'):
    out = []
    with pytest.raises(LoiNghiepVu) as exc:
        out.append(thao_tac())
    assert not out
    assert (exc.value.ma, exc.value.thong_diep) == (ma,
        za.CAU_QUA_GIOI_HAN if ma == 'MASK_QUA_GIOI_HAN' else za.CAU_CHUA_HO_TRO)


@pytest.mark.parametrize('loai', DOC)
@pytest.mark.parametrize('co', [0, 2, 4, 6, 0x800, 0x806])
@pytest.mark.parametrize('descriptor,chu_ky,day_du', [
    (False, True, False), (True, True, False), (True, False, False),
    (True, True, True), (True, False, True)])
def test_no_edit_va_noop_giu_toan_zip(loai, co, descriptor, chu_ky, day_du):
    raw = mau(loai, co=co, descriptor=descriptor, chu_ky=chu_ky, local_day_du=day_du)
    tl = DOC[loai](raw, kiem_huy=kh)
    vi = vung_chinh(tl)
    for kb in (va.lap_kich_ban(tl, (), kiem_huy=kh), lenh(tl, chu(tl.vung[vi]), vi=vi)):
        moi = writer.ghi_goi(tl, kb, kiem_huy=kh)
        assert moi == raw and sha256(moi).digest() == sha256(raw).digest()


@pytest.mark.parametrize('loai', DOC)
@pytest.mark.parametrize('co', [0, 2, 4, 6, 0x806])
@pytest.mark.parametrize('descriptor,chu_ky', [(False, True), (True, True), (True, False)])
def test_mot_run_giu_sha_payload_record_va_muc_bat_bien(loai, co, descriptor, chu_ky):
    raw = mau(loai, co=co, descriptor=descriptor, chu_ky=chu_ky, local_day_du=True)
    tl = DOC[loai](raw, kiem_huy=kh)
    vi = vung_chinh(tl)
    kb = lenh(tl, dau=0, cuoi=4)
    moi = writer.ghi_goi(tl, kb, kiem_huy=kh)
    a, b = liet_ke(raw), liet_ke(moi)
    sua = {x.phan for x in kb.lenh[0].khoang}
    assert a.keys() == b.keys()
    for ten, p in a.items():
        q = b[ten]
        assert (p['co'], p['cach']) == (q['co'], q['cach'])
        assert xoa_truong_muc(p['central'], sua=ten in sua) == xoa_truong_muc(q['central'], sua=ten in sua)
        if ten not in sua:
            assert sha256(p['chu']).digest() == sha256(q['chu']).digest()
            assert sha256(p['payload']).digest() == sha256(q['payload']).digest()
            assert p['record'] == q['record']
        else:
            assert q['crc'] == zlib.crc32(q['chu']) and q['size'] == len(q['chu'])
            if descriptor:
                ds = q['record'][-(16 if chu_ky else 12):]
                assert struct.unpack('<3I', ds[4:] if chu_ky else ds) == (q['crc'], q['nen'], q['size'])
    doc_moi = DOC[loai](moi, kiem_huy=kh)
    assert chu(doc_moi.vung[vi]) == '[[MASKCT-0001]]' + chu(tl.vung[vi])[4:]
    if loai == 'xlsx':
        assert tl.styles == doc_moi.styles and tl.gop_o == doc_moi.gop_o
        assert [o.xml_goc for o in tl.o if o.vung is None] == [o.xml_goc for o in doc_moi.o if o.vung is None]
        assert next(o for o in doc_moi.o if o.dia_chi == 'B2').gia_tri == '1000000'
        assert next(o for o in doc_moi.o if o.dia_chi == 'C2').gia_tri == '46325'


@pytest.mark.parametrize('loai', DOC)
@pytest.mark.parametrize('descriptor', [False, True])
def test_stored_giu_method_khong_tu_doi_nen(loai, descriptor):
    raw = mau(loai, co=0, descriptor=descriptor, cach=0)
    tl = DOC[loai](raw, kiem_huy=kh)
    moi = writer.ghi_goi(tl, lenh(tl), kiem_huy=kh)
    assert all(x['cach'] == 0 for x in liet_ke(moi).values())


@pytest.mark.parametrize('loai', DOC)
@pytest.mark.parametrize('codec,bom', [('utf-8', False), ('utf-8', True),
    ('utf-16-le', False), ('utf-16-le', True), ('utf-16-be', False), ('utf-16-be', True)])
@pytest.mark.parametrize('noi_dung,moi', [
    ('DEMO A&amp;B &#x1F600; e\u0301&#13;Z', 'NFD e\u0301 & < > " \' \r\n\t 😀'),
    ('DEMO _x005F_x0041_ _xD83D__xDE00_', 'DEMO _x0041_ _x005F_ _xD83D__xDE00_'),
    ('DEMO A\r\nB&#13;C', 'DEMO A\rB\nC'),
])
def test_entity_nfd_cr_multibyte_va_escape_giong_ma(loai, codec, bom, noi_dung, moi):
    raw = mau_chu(loai, noi_dung, codec=codec, bom=bom)
    tl = DOC[loai](raw, kiem_huy=kh)
    vi = vung_chinh(tl)
    kb = lenh(tl, moi)
    out = writer.ghi_goi(tl, kb, kiem_huy=kh)
    sau = DOC[loai](out, kiem_huy=kh)
    assert chu(sau.vung[vi]) == moi
    a, b = liet_ke(raw), liet_ke(out)
    x = kb.lenh[0].khoang[0]
    assert a[x.phan]['chu'][:x.dau] == b[x.phan]['chu'][:x.dau]
    assert b[x.phan]['chu'].endswith(a[x.phan]['chu'][x.cuoi:])
    assert a[x.phan]['chu'][:3] == b[x.phan]['chu'][:3]


def test_excel_control_st_mot_luot_va_literal_escape():
    raw = mau_chu('xlsx', 'DEMO _x0041_ _x005F_x0041_')
    tl = doc_excel(raw, kiem_huy=kh)
    text = 'DEMO \x00\x01\x0b\ufffe _x0041_ _x005f_ _xD800_\r 😀'
    out = writer.ghi_goi(tl, lenh(tl, text), kiem_huy=kh)
    assert chu(doc_excel(out, kiem_huy=kh).vung[vung_chinh(tl)]) == text
    xml = liet_ke(out)['xl/worksheets/sheet1.xml']['chu']
    assert b'_x0000_' in xml and b'_x005F_x0041_' in xml and b'&#13;' in xml


@pytest.mark.parametrize('codec,bom', [('utf-8', False), ('utf-16-le', True), ('utf-16-be', True)])
def test_word_cdata_text_hon_hop_giu_delimiter_ngoai_span(codec, bom):
    raw = mau_chu('docx', 'DE<![CDATA[MO & e\u0301]]> &#13;GỐC', codec=codec, bom=bom)
    tl = doc_word(raw, kiem_huy=kh)
    vi = vung_chinh(tl)
    text = 'DEMO < & ]]>\r\n 😀'
    kb = lenh(tl, text, dau=2, cuoi=len(chu(tl.vung[vi])) - 3)
    out = writer.ghi_goi(tl, kb, kiem_huy=kh)
    assert chu(doc_word(out, kiem_huy=kh).vung[vi]) == chu(tl.vung[vi])[:2] + text + 'GỐC'
    a, b = liet_ke(raw)['word/document.xml']['chu'], liet_ke(out)['word/document.xml']['chu']
    assert '<![CDATA['.encode(codec) in a and '<![CDATA['.encode(codec) in b
    assert a[:kb.lenh[0].khoang[0].dau] == b[:kb.lenh[0].khoang[0].dau]


@pytest.mark.parametrize('loai', DOC)
@pytest.mark.parametrize('quote', ['"', "'"])
def test_attribute_custom_escape_cr_lf_tab_va_metadata_khong_st(loai, quote):
    parts = word_day_du() if loai == 'docx' else phan_demo(day_du=True)
    parts['docProps/custom.xml'] = parts['docProps/custom.xml'].replace('name="DEMO chủ hồ sơ"',
        'name=' + quote + 'DEMO chủ hồ sơ' + quote)
    tl = DOC[loai](dong_goi(parts), kiem_huy=kh)
    vi = next(i for i, v in enumerate(tl.vung) if
              (loai == 'xlsx' and v.ma == 'custom_ten' or loai == 'docx' and
               v.phan == 'docProps/custom.xml' and v.anh_xa[0].thuoc_tinh == 'name'))
    text = 'DEMO & < " \' \r\n\t _x0041_ e\u0301 😀'
    out = writer.ghi_goi(tl, lenh(tl, text, vi=vi), kiem_huy=kh)
    assert chu(DOC[loai](out, kiem_huy=kh).vung[vi]) == text
    xml = liet_ke(out)['docProps/custom.xml']['chu']
    assert b'&#13;' in xml and b'&#10;' in xml and b'&#9;' in xml
    assert b'_x0041_' in xml and b'_x005F_x0041_' not in xml


def test_ten_qua_ba_run_chi_doi_mien_text_khong_doi_style_merge():
    parts = word_day_du()
    p_moi = ('<w:p>'
        '<w:r><w:rPr><w:b/></w:rPr><w:t>DEMO Nguyễ</w:t></w:r>'
        '<w:r><w:rPr><w:i/></w:rPr><w:t>n Ánh </w:t></w:r>'
        '<w:r><w:t>Dương tiếp</w:t></w:r></w:p>')
    doc = parts['word/document.xml']
    dau = doc.index('<w:p>')
    cuoi = doc.index('</w:p>', dau) + len('</w:p>')
    parts['word/document.xml'] = doc[:dau] + p_moi + doc[cuoi:]
    tl = doc_word(zip_office(parts, descriptor=True), kiem_huy=kh)
    vi = vung_chinh(tl)
    kb = lenh(tl, '[[MASKCN-0001]]', dau=5, cuoi=len(chu(tl.vung[vi])) - 5)
    out = writer.ghi_goi(tl, kb, kiem_huy=kh)
    root = doc_word(out, kiem_huy=kh)
    assert chu(root.vung[vi]) == 'DEMO [[MASKCN-0001]] tiếp'
    a, b = liet_ke(tl.goi.zip.goc), liet_ke(out)
    assert a['word/styles.xml']['record'] == b['word/styles.xml']['record']
    xml = b['word/document.xml']['chu']
    assert b'<w:rPr><w:b/></w:rPr>' in xml and b'<w:rPr><w:i/></w:rPr>' in xml
    assert xml.count(b'<w:r>') == a['word/document.xml']['chu'].count(b'<w:r>')


def test_shared_chi_patch_mot_lan_nhung_moi_noi_dung_va_unused_duoc_doc_lai():
    raw = mau('xlsx')
    tl = doc_excel(raw, kiem_huy=kh)
    ref = next(i for i, v in enumerate(tl.vung) if v.ma == 'o' and v.chi_so_chu == 0)
    kb = lenh(tl, vi=ref)
    out = writer.ghi_goi(tl, kb, kiem_huy=kh)
    moi = doc_excel(out, kiem_huy=kh)
    assert sum(chu(v) == '[[MASKCT-0001]]' for v in moi.vung) == 3
    assert moi.tham_chieu_chu == tl.tham_chieu_chu
    assert chu(moi.vung[moi.shared[1]]) == chu(tl.vung[tl.shared[1]])
    assert liet_ke(raw)['xl/worksheets/sheet1.xml']['record'] == liet_ke(out)['xl/worksheets/sheet1.xml']['record']
    # Hai ô cùng shared không có quyền tạo hai patch chồng lên một nguồn.
    ref2 = next(i for i, v in enumerate(tl.vung) if i != ref and v.ma == 'o' and v.chi_so_chu == 0)
    kb2 = va.lap_kich_ban(tl, ((ref, 0, 4, 'A'), (ref2, 0, 4, 'A')), kiem_huy=kh)
    bi_chan(lambda: writer.ghi_goi(tl, kb2, kiem_huy=kh))


@pytest.mark.parametrize('vi_chon', ['ten_sheet', 'app_ten_sheet'])
def test_sheet_name_can_doi_bi_chan(vi_chon):
    tl = doc_excel(mau('xlsx'), kiem_huy=kh)
    vi = next(i for i, v in enumerate(tl.vung) if v.ma == vi_chon)
    bi_chan(lambda: writer.ghi_goi(tl, lenh(tl, vi=vi), kiem_huy=kh))


@pytest.mark.parametrize('loai', DOC)
@pytest.mark.parametrize('truong,gia_tri', [
    ('vung', -1), ('vung', True), ('vung', 99999), ('dau', -1), ('dau', True),
    ('dau', 1), ('cuoi', 0), ('cuoi', 999999), ('bam_vung', 'sha256:' + '0' * 64),
    ('chu_moi', None), ('chu_moi', b'DEMO'), ('chu_moi', '\ud800'), ('khoang', ())])
def test_script_gia_vung_unicode_bam_kieu_bi_chan(loai, truong, gia_tri):
    tl = DOC[loai](mau(loai), kiem_huy=kh)
    kb = lenh(tl)
    kb = replace(kb, lenh=(replace(kb.lenh[0], **{truong: gia_tri}),))
    bi_chan(lambda: writer.ghi_goi(tl, kb, kiem_huy=kh))


@pytest.mark.parametrize('truong,gia_tri', [('phan', 'docProps/DEMO-lạ.xml'),
    ('dau', 1), ('cuoi', 2), ('bam_phan', 'sha256:' + '1' * 64), ('bam_byte', 'sha256:' + '2' * 64)])
def test_script_gia_span_byte_part_hash_bi_chan(truong, gia_tri):
    tl = doc_word(mau_chu('docx', 'DEMO &amp; e\u0301 😀'), kiem_huy=kh)
    kb = lenh(tl)
    l = kb.lenh[0]
    l = replace(l, khoang=(replace(l.khoang[0], **{truong: gia_tri}), *l.khoang[1:]))
    bi_chan(lambda: writer.ghi_goi(tl, replace(kb, lenh=(l,)), kiem_huy=kh))


@pytest.mark.parametrize('truong,gia_tri', [('phien_ban', 2), ('phien_ban', True),
    ('bam_tep', 'sha256:' + '0' * 64), ('lenh', [])])
def test_kich_ban_sai_phien_ban_bam_va_tuple(truong, gia_tri):
    tl = doc_word(mau('docx'), kiem_huy=kh)
    kb = replace(lenh(tl), **{truong: gia_tri})
    bi_chan(lambda: writer.ghi_goi(tl, kb, kiem_huy=kh))


@pytest.mark.parametrize('loai', DOC)
@pytest.mark.parametrize('truong', ['crc', 'so_byte', 'so_byte_nen', 'le_dau', 'le_du_lieu',
    'le_cuoi', 'le_danh_muc', 'cuoi_danh_muc', 'du_lieu', 'ten'])
def test_metadata_package_ram_gia_bi_chan(loai, truong):
    tl = DOC[loai](mau(loai), kiem_huy=kh)
    kb = lenh(tl)
    g = va.goi_cua(tl)
    p = g.zip.phan[0]
    gia_tri = b'DEMO' if truong == 'du_lieu' else 'DEMO.xml' if truong == 'ten' else getattr(p, truong) + 1
    goi = replace(g, zip=replace(g.zip, phan=(replace(p, **{truong: gia_tri}), *g.zip.phan[1:])))
    fake = replace(tl, goi=goi if loai == 'docx' else replace(tl.goi, goi=goi))
    bi_chan(lambda: writer.ghi_goi(fake, kb, kiem_huy=kh))


@pytest.mark.parametrize('loai', DOC)
def test_map_reader_ram_gia_bi_chan(loai):
    tl = DOC[loai](mau(loai), kiem_huy=kh)
    kb = lenh(tl)
    vi = vung_chinh(tl)
    v = tl.vung[vi]
    if loai == 'docx':
        m = replace(v.anh_xa[0], byte_bat_dau=v.anh_xa[0].byte_bat_dau + 1)
        v = replace(v, anh_xa=(m, *v.anh_xa[1:]))
    else:
        m = replace(v.manh[0], byte=((1, 2), *v.manh[0].byte[1:]))
        v = replace(v, manh=(m, *v.manh[1:]))
    fake = replace(tl, vung=(*tl.vung[:vi], v, *tl.vung[vi + 1:]))
    bi_chan(lambda: writer.ghi_goi(fake, kb, kiem_huy=kh))


@pytest.mark.parametrize('loai', DOC)
@pytest.mark.parametrize('kieu', ['crc', 'size', 'offset', 'descriptor', 'flags', 'extra', 'truncated', 'trailing'])
def test_bytes_zip_gia_bi_chan_truoc_writer(loai, kieu):
    tl = DOC[loai](mau(loai), kiem_huy=kh)
    kb = lenh(tl)
    g = va.goi_cua(tl)
    raw = bytearray(g.zip.goc)
    p = g.zip.phan[0]
    if kieu == 'truncated':
        raw = raw[:-1]
    elif kieu == 'trailing':
        raw.extend(b'DEMO')
    elif kieu == 'descriptor':
        raw[p.le_du_lieu + p.so_byte_nen + 4] ^= 1
    elif kieu == 'flags':
        struct.pack_into('<H', raw, p.le_dau + 6, 0x41)
        struct.pack_into('<H', raw, p.le_danh_muc + 8, 0x41)
    else:
        at = {'crc': 16, 'size': 24, 'offset': 42, 'extra': 30}[kieu]
        raw[p.le_danh_muc + at] ^= 1
    goi = replace(g, zip=replace(g.zip, goc=bytes(raw)))
    fake = replace(tl, goi=goi if loai == 'docx' else replace(tl.goi, goi=goi))
    bi_chan(lambda: writer.ghi_goi(fake, kb, kiem_huy=kh))


@pytest.mark.parametrize('gia', [b'DEMO', {}, None, 'DEMO.docx', object()])
def test_chi_nhan_reader_da_qua_b1(gia):
    bi_chan(lambda: writer.ghi_goi(gia, None, kiem_huy=kh))


def test_khong_cho_chong_lenh_ke_ca_script_noop():
    tl = doc_word(mau('docx'), kiem_huy=kh)
    vi = vung_chinh(tl)
    kb = va.lap_kich_ban(tl, ((vi, 0, 4, 'DEMO'), (vi, 2, 6, '[[MASKCN-0001]]')), kiem_huy=kh)
    bi_chan(lambda: writer.ghi_goi(tl, kb, kiem_huy=kh))


def test_nhieu_lenh_nguoc_thu_tu_dung_offset_goc():
    tl = doc_word(mau_chu('docx', 'DEMO Ánh Dương và DEMO Lan'), kiem_huy=kh)
    vi = vung_chinh(tl)
    dau_lan = len('DEMO Ánh Dương và DEMO ')
    kb = va.lap_kich_ban(tl, ((vi, dau_lan, dau_lan + len('Lan'), 'B'), (vi, 5, 14, 'A')), kiem_huy=kh)
    out = writer.ghi_goi(tl, kb, kiem_huy=kh)
    assert chu(doc_word(out, kiem_huy=kh).vung[vi]) == 'DEMO A và DEMO B'


def test_tab_br_note_khong_la_text_span_duoc_sua():
    parts = word_demo(noi_dung='<w:p><w:r><w:t>DEMO</w:t><w:tab/><w:t>Lan</w:t></w:r></w:p>')
    tl = doc_word(dong_goi(parts), kiem_huy=kh)
    bi_chan(lambda: lenh(tl))


def test_custom_so_word_khong_duoc_ep_sang_bi_danh():
    parts = word_day_du()
    parts['docProps/custom.xml'] = parts['docProps/custom.xml'].replace('<vt:lpwstr>', '<vt:i4>').replace('</vt:lpwstr>', '</vt:i4>')
    # Chỉ thay một scalar chuỗi đầu, các scalar có kiểu khác giữ nguyên.
    import re
    parts['docProps/custom.xml'] = re.sub(r'<vt:i4>.*?</vt:i4>', '<vt:i4>123456</vt:i4>', parts['docProps/custom.xml'])
    tl = doc_word(dong_goi(parts), kiem_huy=kh)
    vi = next(i for i, v in enumerate(tl.vung) if chu(v) == '123456')
    bi_chan(lambda: writer.ghi_goi(tl, lenh(tl, vi=vi), kiem_huy=kh))


@pytest.mark.parametrize('loai', DOC)
@pytest.mark.parametrize('lech', [0, 1])
def test_output_container_dung_1mib_va_cong_1_byte(loai, lech):
    raw = mau_chu(loai, 'D') if loai == 'docx' else mau('xlsx', co=0, descriptor=False, cach=0)
    tl = DOC[loai](raw, kiem_huy=kh)
    vi = vung_chinh(tl) if loai == 'docx' else next(i for i, v in enumerate(tl.vung) if v.ma == 'custom')
    kb0 = lenh(tl, 'D', vi=vi)
    x = kb0.lenh[0].khoang[0]
    size = za.TEP_TOI_DA - len(raw) + (x.cuoi - x.dau) + lech
    text = '界' * (size // 3) + 'D' * (size % 3)
    kb = lenh(tl, text, vi=vi)
    if lech:
        bi_chan(lambda: writer.ghi_goi(tl, kb, kiem_huy=kh), 'MASK_QUA_GIOI_HAN')
    else:
        out = writer.ghi_goi(tl, kb, kiem_huy=kh)
        assert len(out) == za.TEP_TOI_DA
        assert chu(DOC[loai](out, kiem_huy=kh).vung[vi]) == text


def test_khuyech_dai_entity_vuot_2mib_part_bi_chan_truoc_nen(monkeypatch):
    tl = doc_word(mau_chu('docx', 'D'), kiem_huy=kh)
    kb = lenh(tl, '&' * (za.PHAN_TOI_DA // 5 + 1))
    monkeypatch.setattr(writer, '_nen', lambda *a: pytest.fail('Không được nén khi part đã vượt trần'))
    bi_chan(lambda: writer.ghi_goi(tl, kb, kiem_huy=kh), 'MASK_QUA_GIOI_HAN')


def test_tong_8mib_khi_chuan_bi_escape_khong_cho_cap_phat_vuot(monkeypatch):
    tl = doc_word(mau('docx'), kiem_huy=kh)
    # Cửa tổng độc lập trần part/container: chỉ hạ budget output, giữ B1 gốc.
    tong = sum(p.so_byte for p in tl.goi.zip.phan)
    monkeypatch.setattr(va, 'TONG_GIAI_NEN_TOI_DA', tong + 8)
    bi_chan(lambda: writer.ghi_goi(tl, lenh(tl, '&' * 20), kiem_huy=kh), 'MASK_QUA_GIOI_HAN')


@pytest.mark.parametrize('lech', [0, 1])
def test_budget_part_2mib_thuc_tai_cua_patch_doc_lap_ratio_container(lech):
    tl = doc_word(mau_chu('docx', 'D'), kiem_huy=kh)
    kb0 = lenh(tl, 'D')
    p = tl.goi.zip.phan[-1]
    bo = sum(x.cuoi - x.dau for x in kb0.lenh[0].khoang)
    can = za.PHAN_TOI_DA - p.so_byte + bo + lech
    text = '&' * (can // 5) + 'D' * (can % 5)
    kb = lenh(tl, text)
    if lech:
        bi_chan(lambda: va.chuan_bi_va(tl, kb, kh), 'MASK_QUA_GIOI_HAN')
    else:
        xs, _ = va.chuan_bi_va(tl, kb, kh)
        assert len(va.va_phan(p.du_lieu, xs[p.ten], kh)) == za.PHAN_TOI_DA


@pytest.mark.parametrize('lech', [0, 1])
def test_budget_tong_8mib_thuc_nhieu_part_truoc_ghi_zip(lech):
    tl = doc_word(mau('docx'), kiem_huy=kh)
    ten = ('word/document.xml', 'word/header1.xml', 'word/footer1.xml',
           'word/footnotes.xml', 'word/endnotes.xml')
    vi = [next(i for i, v in enumerate(tl.vung) if v.phan == t and v.van_ban
               and all(m.kieu == 'text' for m in v.anh_xa)) for t in ten]
    kb0 = va.lap_kich_ban(tl, tuple((i, 0, len(chu(tl.vung[i])), 'D') for i in vi), kiem_huy=kh)
    bo = sum(x.cuoi - x.dau for l in kb0.lenh for x in l.khoang)
    nen_co = sum(p.so_byte for p in tl.goi.zip.phan) - bo
    can = za.TONG_GIAI_NEN_TOI_DA - nen_co + lech
    sizes = [can // 5] * 4 + [can - 4 * (can // 5)]
    kb = va.lap_kich_ban(tl, tuple((i, 0, len(chu(tl.vung[i])),
        '&' * (n // 5) + 'D' * (n % 5)) for i, n in zip(vi, sizes)), kiem_huy=kh)
    if lech:
        bi_chan(lambda: va.chuan_bi_va(tl, kb, kh), 'MASK_QUA_GIOI_HAN')
    else:
        xs, _ = va.chuan_bi_va(tl, kb, kh)
        assert sum(p.so_byte + sum(len(d) - (b - a) for a, b, d in xs.get(p.ten, ()))
                   for p in tl.goi.zip.phan) == za.TONG_GIAI_NEN_TOI_DA


def test_ratio_output_vuot_200_tu_choi_khong_doi_compression(monkeypatch):
    tl = doc_word(mau_chu('docx', 'DEMO', cach=8), kiem_huy=kh)
    kb = lenh(tl, 'A' * 100000)
    cu = zlib.compressobj
    calls = []
    def nen(*args, **kwargs):
        calls.append((args, kwargs))
        return cu(*args, **kwargs)
    monkeypatch.setattr(zlib, 'compressobj', nen)
    bi_chan(lambda: writer.ghi_goi(tl, kb, kiem_huy=kh), 'MASK_QUA_GIOI_HAN')
    assert len(calls) == 1 and calls[0][0] == (6,)


@pytest.mark.parametrize('lech', [0, 1])
def test_tran_ky_tu_ra_2_trieu_truoc_escape(lech):
    tl = doc_word(mau_chu('docx', 'D'), kiem_huy=kh)
    if lech:
        bi_chan(lambda: lenh(tl, 'A' * (2000000 + lech)), 'MASK_QUA_GIOI_HAN')
    else:
        kb = lenh(tl, 'A' * 2000000)
        # Đạt cửa ký tự nhưng cổng part/ratio/reader vẫn áp, không cắt xuống.
        bi_chan(lambda: writer.ghi_goi(tl, kb, kiem_huy=kh), 'MASK_QUA_GIOI_HAN')


def test_shared_output_dem_ca_moi_lan_dung_truoc_ghi(monkeypatch):
    tl = doc_excel(mau('xlsx'), kiem_huy=kh)
    monkeypatch.setattr(va, 'KY_TU_RA_TOI_DA', tl.so_ky_tu + 20)
    bi_chan(lambda: writer.ghi_goi(tl, lenh(tl, 'DEMO' * 20), kiem_huy=kh), 'MASK_QUA_GIOI_HAN')


def test_excel_32768_utf16_khong_cat():
    tl = doc_excel(mau_chu('xlsx', 'D'), kiem_huy=kh)
    bi_chan(lambda: writer.ghi_goi(tl, lenh(tl, '😀' * 16384), kiem_huy=kh), 'MASK_QUA_GIOI_HAN')


@pytest.mark.parametrize('loai', DOC)
def test_xml_injection_thanh_text_khong_them_node(loai):
    tl = DOC[loai](mau_chu(loai, 'D'), kiem_huy=kh)
    text = 'DEMO </t><macro> & <!DOCTYPE x [<!ENTITY z SYSTEM "DEMO">]>'
    out = writer.ghi_goi(tl, lenh(tl, text), kiem_huy=kh)
    moi = DOC[loai](out, kiem_huy=kh)
    assert chu(moi.vung[vung_chinh(tl)]) == text
    assert va.goi_cua(tl).thong_ke['so_nut'] == va.goi_cua(moi).thong_ke['so_nut']


def test_doc_lai_output_tu_choi_xml_hong_du_crc_size_dung(monkeypatch):
    tl = doc_word(mau('docx'), kiem_huy=kh)
    cu = writer.va_phan
    def hong(raw, xs, huy):
        return cu(raw, xs, huy).replace(b'</w:document>', b'</w:SAI>')
    monkeypatch.setattr(writer, 'va_phan', hong)
    bi_chan(lambda: writer.ghi_goi(tl, lenh(tl), kiem_huy=kh))


def test_doc_lai_output_tu_choi_noi_dung_sai_du_xml_crc_hop_le(monkeypatch):
    tl = doc_word(mau_chu('docx', 'DEMO'), kiem_huy=kh)
    cu = writer.va_phan
    monkeypatch.setattr(writer, 'va_phan', lambda raw, xs, huy: cu(raw, xs, huy).replace(b'MASKCT', b'MASKCN'))
    bi_chan(lambda: writer.ghi_goi(tl, lenh(tl), kiem_huy=kh))


def test_st_ghep_ma_o_bien_span_khong_duoc_am_tham_doi_nghia():
    tl = doc_excel(mau_chu('xlsx', 'DEMO _xZZZZ_'), kiem_huy=kh)
    kb = lenh(tl, '0041', dau=7, cuoi=11)
    bi_chan(lambda: writer.ghi_goi(tl, kb, kiem_huy=kh))


@pytest.mark.parametrize('loai', DOC)
@pytest.mark.parametrize('loi', [RuntimeError('HỦY DEMO'), ChuaRo('DEMO-tuong-quan')])
def test_huy_giua_ghi_giu_nguyen_ngoai_le_don_buffer_khong_io(loai, loi, monkeypatch, capsys):
    tl = DOC[loai](mau(loai), kiem_huy=kh)
    kb = lenh(tl)
    dem = []
    cu = writer._BoDem
    class Dem(cu):
        def __init__(self):
            super().__init__()
            dem.append(self)
    monkeypatch.setattr(writer, '_BoDem', Dem)
    def cam(*a, **k):
        pytest.fail('Writer gọi I/O ngoài RAM')
    monkeypatch.setattr('builtins.open', cam)
    monkeypatch.setattr(socket, 'socket', cam)
    def huy():
        if dem and dem[0].tell() > 0:
            raise loi
    out = []
    with pytest.raises(type(loi)) as exc:
        out.append(writer.ghi_goi(tl, kb, kiem_huy=huy))
    assert exc.value is loi and not out and dem and all(d.closed for d in dem)
    assert capsys.readouterr() == ('', '')


@pytest.mark.parametrize('loai', DOC)
def test_khong_io_log_khi_thanh_cong_va_loi(loai, monkeypatch, capsys):
    tl = DOC[loai](mau(loai), kiem_huy=kh)
    kb = lenh(tl)
    def cam(*a, **k):
        pytest.fail('Writer gọi I/O ngoài RAM')
    monkeypatch.setattr('builtins.open', cam)
    monkeypatch.setattr(socket, 'socket', cam)
    assert writer.ghi_goi(tl, kb, kiem_huy=kh)
    bi_chan(lambda: writer.ghi_goi(tl, replace(kb, bam_tep='DEMO-sai'), kiem_huy=kh))
    assert capsys.readouterr() == ('', '')


def test_huy_cuoi_sau_khi_output_doc_lai_van_khong_tra_bytes(monkeypatch):
    tl = doc_word(mau('docx'), kiem_huy=kh)
    da_doc = []
    doc = writer.doc_word
    def doc_ra(*a, **k):
        out = doc(*a, **k)
        da_doc.append(True)
        return out
    monkeypatch.setattr(writer, 'doc_word', doc_ra)
    loi = RuntimeError('HỦY DEMO')
    def huy():
        if da_doc:
            raise loi
    with pytest.raises(RuntimeError) as exc:
        writer.ghi_goi(tl, lenh(tl), kiem_huy=huy)
    assert exc.value is loi


def test_central_khac_thu_tu_record_vat_ly_van_giu_dung_bytes():
    raw = mau('docx')
    muc = liet_ke(raw)
    pos = min(p['le_central'] for p in muc.values())
    raw = raw[:pos] + b''.join(p['central'] for p in reversed(list(muc.values()))) + raw[-22:]
    tl = doc_word(raw, kiem_huy=kh)
    out = writer.ghi_goi(tl, lenh(tl), kiem_huy=kh)
    a, b = liet_ke(raw), liet_ke(out)
    assert list(a) == list(b)
    for ten in a:
        if ten != 'word/document.xml':
            assert a[ten]['record'] == b[ten]['record']


def test_no_ten_zip_256_257_dong_o_helper_chung_b1():
    assert za._kiem_ten('D' * 256) == 'd' * 256
    bi_chan(lambda: za._kiem_ten('D' * 257))


@pytest.mark.parametrize('loai,nhom', [
    ('docx', 'dau_trang'), ('docx', 'chan_trang'), ('docx', 'footnote'),
    ('docx', 'endnote'), ('docx', 'thuoc_tinh'), ('docx', 'dinh_dang'),
    ('xlsx', 'core'), ('xlsx', 'app'), ('xlsx', 'custom'), ('xlsx', 'custom_ten'), ('xlsx', 'o')])
def test_patch_moi_nhom_vung_reader_khong_chi_than(loai, nhom):
    raw = mau(loai)
    tl = DOC[loai](raw, kiem_huy=kh)
    vi = next(i for i, v in enumerate(tl.vung) if chu(v) and (
        loai == 'docx' and v.loai == nhom and all(m.kieu != 'ky_hieu' for m in v.anh_xa)
        or loai == 'xlsx' and v.ma == nhom and v.duoc_sua))
    kb = lenh(tl, vi=vi)
    out = writer.ghi_goi(tl, kb, kiem_huy=kh)
    assert chu(DOC[loai](out, kiem_huy=kh).vung[vi]) == '[[MASKCT-0001]]'
    sua = {x.phan for x in kb.lenh[0].khoang}
    a, b = liet_ke(raw), liet_ke(out)
    assert all(p['record'] == b[t]['record'] for t, p in a.items() if t not in sua)


def test_chong_unicode_bi_chan_truoc_cap_phat_map_byte(monkeypatch):
    tl = doc_word(mau('docx'), kiem_huy=kh)
    kb = lenh(tl)
    kb = replace(kb, lenh=kb.lenh * 2)
    monkeypatch.setattr(va, '_khoang', lambda *a: pytest.fail('Phải chặn chồng trước map'))
    bi_chan(lambda: writer.ghi_goi(tl, kb, kiem_huy=kh))


@pytest.mark.parametrize('control', ['\x00', '\x01', '\ufffe', '\uffff'])
def test_word_khong_ma_hoa_control_bang_st_cua_excel(control):
    tl = doc_word(mau_chu('docx', 'DEMO'), kiem_huy=kh)
    bi_chan(lambda: writer.ghi_goi(tl, lenh(tl, 'DEMO' + control), kiem_huy=kh))


def test_nguon_b4_sha_bytes_lf_truoc_sau_va_dich_hien_hanh():
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    truoc = json.loads((root / 'e_mask/docs/SHA-NGUON-MASK-B4-TRUOC.json').read_text('utf-8'))
    doc = (root / 'e_mask/goi/e_mask/NGUON.md').read_text('utf-8').split('## MASK-B4 —')[1]
    for ten, hashes in truoc.items():
        b = (root / ten).read_bytes()
        if not ten.endswith('zip_an_toan.py'):
            assert hashes == {'bytes': sha256(b).hexdigest(), 'lf': sha256(b.replace(b'\r\n', b'\n')).hexdigest()}
        assert all(h in doc for h in hashes.values())
    for ten in ('ghi_zip.py', 'va_xml.py', 'zip_an_toan.py'):
        b = (root / 'e_mask/goi/e_mask/e_mask' / ten).read_bytes()
        assert sha256(b).hexdigest() in doc and sha256(b.replace(b'\r\n', b'\n')).hexdigest() in doc
