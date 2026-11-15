"""Gold và đối kháng MASK-B3; chỉ DEMO, không Office/mạng/tệp máy."""

import builtins
from datetime import date, timedelta
import hashlib
from pathlib import Path
import socket
import struct
import unicodedata
import zlib

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu

from e_mask.doc_excel import doc_excel
from e_mask.xml_excel import chu_xml
from e_mask import xml_an_toan as xa
from e_mask import zip_an_toan as za
from ho_tro_mask_b1 import excel_demo, dong_goi, them_phan, CT_S, S, R, tao_zip
from ho_tro_mask_b3 import phan_demo, goi_office, CP, DC, DCT, XSI, EP, CUSTOM, VT, A


def doc(phan=None, **kw):
    return doc_excel(dong_goi(phan or phan_demo()), kiem_huy=kw.get('kiem_huy', lambda: None))


def loi(phan, *, ma='MASK_TEP_CHUA_HO_TRO', raw=None):
    sentinel = object()
    ket_qua = sentinel
    with pytest.raises(LoiNghiepVu) as exc:
        ket_qua = doc_excel(raw if raw is not None else dong_goi(phan), kiem_huy=lambda: None)
    assert ket_qua is sentinel
    assert exc.value.ma == ma
    assert exc.value.thong_diep in (za.CAU_CHUA_HO_TRO, za.CAU_QUA_GIOI_HAN)
    assert 'DEMO' not in str(exc.value)
    assert '/' not in str(exc.value) and '\\' not in str(exc.value)


def inline(chu, *, extra='', attr='', sheet=''):
    p = excel_demo(noi_dung=f'<row r="1"><c r="A1" t="inlineStr" {attr}><is>{chu}</is></c>{extra}</row>')
    if sheet:
        p['xl/worksheets/sheet1.xml'] = f'<worksheet xmlns="{S}">{sheet}<sheetData><row r="1"><c r="A1" t="inlineStr"><is>{chu}</is></c></row></sheetData></worksheet>'
    return p


def vung_o(x, address='A1', sheet=0):
    return next(v for v in x.vung if v.ma == 'o' and v.o == address and v.so_sheet == sheet)


def test_gold_moi_vung_va_gia_tri_style_demo():
    p = phan_demo(day_du=True)
    raw = goi_office(p)
    x = doc_excel(raw, kiem_huy=lambda: None)
    assert [(v.ma, v.chu) for v in x.vung] == [
        ('shared_string', 'DEMO Công ty Ánh Dương'), ('shared_string', 'DEMO tên chưa dùng'),
        ('ten_sheet', 'DEMO 1'), ('o', 'DEMO Công ty Ánh Dương'), ('o', 'DEMO Công ty Ánh Dương'),
        ('o', 'DEMO Trần Ánh Dương'), ('o', 'DEMO Nguyễn Lan'), ('o', '0000123'), ('o', 'DEMO ô gộp'),
        ('core', 'DEMO hồ sơ Ánh Dương'), ('core', 'DEMO Nguyễn Lan'), ('core', 'DEMO Trần Hà'),
        ('app', 'Microsoft Excel'), ('app', 'DEMO Trần Minh'), ('app', 'DEMO Ánh Dương'),
        ('app_ten_sheet', 'DEMO 1'), ('app', '16.0300'), ('custom_ten', 'DEMO chủ hồ sơ'),
        ('custom', 'DEMO Lê Hạ'), ('custom_ten', 'DEMO ngày')]
    assert x.tham_chieu_chu == (((0, 'A1'), (0, 'B1')), ())
    assert len(x.o) == 9 and x.gop_o == (('A3:B3',),)
    assert x.epoch1904 is False
    assert x.bam_tep == 'sha256:' + hashlib.sha256(raw).hexdigest()
    assert all(v.bam_chu == 'sha256:' + hashlib.sha256(v.chu.encode()).hexdigest() for v in x.vung)
    assert x.bam_tep not in {v.bam_chu for v in x.vung}
    assert x.goi.goi.zip.goc == raw
    cells = {o.dia_chi: o for o in x.o}
    assert (cells['B2'].gia_tri, cells['B2'].kieu, cells['B2'].style) == ('1000000', None, 2)
    assert x.styles[2]['formatCode'] == '#,##0" VND"'
    assert cells['B2'].xml_goc == b'<c r="B2" s="2"><v>1000000</v></c>'
    assert (cells['C2'].gia_tri, cells['C2'].kieu, cells['C2'].style) == ('46325', 'n', 1)
    assert x.styles[1]['formatCode'] == 'yyyy-mm-dd'
    assert date(1899, 12, 30) + timedelta(days=int(cells['C2'].gia_tri)) == date(2026, 10, 30)
    assert cells['C2'].xml_goc == b'<c r="C2" s="1" t="n"><v>46325</v></c>'
    assert (cells['D2'].gia_tri, cells['D2'].kieu) == ('1', 'b')
    assert all(cells[a].vung is None for a in ('B2', 'C2', 'D2'))
    assert vung_o(x, 'E2').chu == '0000123'
    assert cells['A1'].cot_an and not cells['A1'].hang_an
    assert cells['A2'].cot_an and cells['A2'].hang_an
    assert cells['B2'].hang_an and not cells['B2'].cot_an
    raw_xml = {z.ten: z.du_lieu for z in x.goi.goi.zip.phan}
    assert all(raw_xml[k] == (v.encode() if isinstance(v, str) else v) for k, v in p.items())
    assert 'Ánh Dương' not in repr(x) + repr(x.vung) + repr(x.o)


@pytest.mark.parametrize('flags', [0, 2, 4, 6, 0x800, 0x806])
@pytest.mark.parametrize('descriptor,signature', [(False, True), (True, True), (True, False)])
def test_zip_office_co_nen_va_descriptor(flags, descriptor, signature):
    raw = goi_office(phan_demo(day_du=True), co=flags, descriptor=descriptor, chu_ky=signature)
    x = doc_excel(raw, kiem_huy=lambda: None)
    assert len(x.o) == 9
    for b in x.goi.ban_ghi:
        assert b.co == flags | (8 if descriptor else 0)
        assert b.le_cuoi_ban_ghi - b.phan.le_cuoi == (16 if signature else 12) if descriptor else b.le_cuoi_ban_ghi == b.phan.le_cuoi


@pytest.mark.parametrize('signature', [True, False])
@pytest.mark.parametrize('sua', ['crc', 'nen', 'size', 'local_flags', 'central_flags', 'duoi', 'thieu', 'payload', 'local_size'])
def test_descriptor_sai_khong_co_ket_qua(signature, sua):
    raw = bytearray(goi_office(phan_demo(), chu_ky=signature))
    center = raw.index(b'PK\x01\x02')
    n = struct.unpack_from('<I', raw, center + 20)[0]
    name = struct.unpack_from('<H', raw, 26)[0]
    dd = 30 + name + n
    if sua in ('crc', 'nen', 'size'):
        off = dd + (4 if signature else 0) + {'crc': 0, 'nen': 4, 'size': 8}[sua]
        raw[off] ^= 1
    elif sua == 'local_flags':
        raw[6] ^= 2
    elif sua == 'central_flags':
        raw[center + 8] |= 1
    elif sua == 'duoi':
        raw.extend(b'DEMO')
    elif sua == 'thieu':
        raw = raw[:-1]
    elif sua == 'local_size':
        struct.pack_into('<I', raw, 18, 1)
    else:
        raw[30 + name] ^= 1
    loi({}, raw=bytes(raw))


@pytest.mark.parametrize('cach,co', [(0, 2), (0, 6), (8, 1), (8, 0x10), (8, 0x40), (8, 0x1000), (8, 0x2000)])
def test_zip_co_ngoai_profile(cach, co):
    loi({}, raw=goi_office(phan_demo(), cach=cach, co=co))


def test_stored_descriptor_va_local_khai_dung():
    raw = goi_office(phan_demo(), cach=0, co=0)
    assert len(doc_excel(raw, kiem_huy=lambda: None).o) == 9


def test_map_rich_tach_ba_run_khong_noi_hai_o():
    x = doc()
    v = vung_o(x, 'C1')
    assert v.chu == 'DEMO Trần Ánh Dương'
    a = v.chu.index('Trần')
    xs = v.khoang_byte(a, len(v.chu))
    assert len(xs) == 3
    raw = next(p.du_lieu for p in x.goi.goi.zip.phan if p.ten == 'xl/worksheets/sheet1.xml')
    assert [raw[a:b].decode() for _, _, _, _, a, b in xs] == ['Trần ', 'Ánh ', 'Dương']
    assert [s[2] for s in xs] == [0, 1, 2]
    for phan, node, _, attr, a, b in xs:
        assert v.unicode_tu_byte(phan, node, a, b, thuoc_tinh=attr)
    p = inline('<t>DEMO Trần</t>', extra='<c r="B1" t="inlineStr"><is><t>Ánh Dương</t></is></c>')
    y = doc(p)
    assert [v.chu for v in y.vung if v.ma == 'o'] == ['DEMO Trần', 'Ánh Dương']
    assert vung_o(y).khoang_byte(0, len(vung_o(y).chu))[0][0].endswith('sheet1.xml')


@pytest.mark.parametrize('text,expected,piece', [
    ('DEMO _x0041_', 'DEMO A', b'_x0041_'),
    ('DEMO _x005F_x0041_', 'DEMO _x0041_', b'_x005F_'),
    ('DEMO _x000D_', 'DEMO \r', b'_x000D_'),
    ('DEMO &#13;', 'DEMO \r', b'&#13;'),
    ('DEMO _xD83D__xDE00_', 'DEMO 😀', b'_xD83D__xDE00_'),
    ('DEMO &#x1F600;', 'DEMO 😀', b'&#x1F600;'),
    ('DEMO &amp;', 'DEMO &', b'&amp;'),
    ('DEMO &lt;', 'DEMO <', b'&lt;'),
    ('DEMO &quot;', 'DEMO "', b'&quot;'),
    ('DEMO \r\n', 'DEMO \n', b'\r\n'),
    ('DEMO \r', 'DEMO \n', b'\r'),
    ('DEMO _x0001_', 'DEMO \x01', b'_x0001_'),
])
def test_map_entity_st_cr_surrogate_chinh_xac(text, expected, piece):
    p = inline('<t xml:space="preserve">' + text + '</t>')
    x = doc(p)
    v = vung_o(x)
    assert v.chu == expected
    m = v.manh[0]
    raw = p[m.phan].encode()
    target = raw.index(piece)
    i = next(i for i, b in enumerate(m.byte) if b[0] == target)
    assert raw[slice(*m.byte[i])] == piece
    giua = target + (1 if len(piece) > 1 else 0)
    assert v.unicode_tu_byte(m.phan, m.so_nut, giua, giua + 1) == ((i, i + 1),)
    assert m.byte[i][1] - m.byte[i][0] == len(piece)


def test_nfd_cf_khong_normalize_va_offset_dung():
    goc = 'DEMO Trần Ánh\u200b Dương & \r\n'
    p = inline('<t>' + goc.replace('&', '&amp;') + '</t>')
    x = doc(p)
    v = vung_o(x)
    assert v.chu == goc.replace('\r\n', '\n')
    assert not unicodedata.is_normalized('NFC', v.chu)
    assert '\u200b' in v.chu
    raw = p[v.manh[0].phan].encode()
    for i, c in enumerate(v.chu):
        data = raw[slice(*v.manh[0].byte[i])].decode()
        assert data == c or (data == '\r\n' and c == '\n') or (data == '&amp;' and c == '&')


@pytest.mark.parametrize('codec,bom,decl', [('utf-8', b'\xef\xbb\xbf', 'UTF-8'),
    ('utf-16-le', b'\xff\xfe', 'UTF-16'), ('utf-16-be', b'\xfe\xff', 'UTF-16'),
    ('utf-16-le', b'', 'UTF-16LE'), ('utf-16-be', b'', 'UTF-16BE')])
def test_map_utf16_bom_va_byte_khong_phai_utf8(codec, bom, decl):
    p = inline('<t>DEMO Ánh &#13; 😀</t>')
    key = 'xl/worksheets/sheet1.xml'
    p[key] = bom + (f'<?xml version="1.0" encoding="{decl}"?>' + p[key]).encode(codec)
    v = vung_o(doc(p))
    assert v.chu == 'DEMO Ánh \r 😀'
    for i, c in enumerate(v.chu):
        raw = p[key][slice(*v.manh[0].byte[i])].decode(codec)
        assert raw == c or raw == '&#13;' and c == '\r'


@pytest.mark.parametrize('text', ['_xD800_', '_xDC00_', '_xD800__x0041_', '_xDBFF__xD800_'])
def test_surrogate_le_phai_tu_choi(text):
    loi(inline('<t>DEMO ' + text + '</t>'))


def test_shared_lap_khac_sheet_va_muc_chua_dung_deu_co_map():
    p = phan_demo()
    them_phan(p, 'xl/worksheets/sheet2.xml', f'<worksheet xmlns="{S}"><sheetData><row r="1"><c r="Z1" t="s"><v>0</v></c></row></sheetData></worksheet>',
              CT_S + 'worksheet+xml', 'worksheet', rid='rId2', chu='xl/workbook.xml')
    p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('</sheets>', '<sheet name="DEMO 2" sheetId="2" r:id="rId2"/></sheets>')
    p['xl/sharedStrings.xml'] = p['xl/sharedStrings.xml'].replace('count="2"', 'count="3"')
    x = doc(p)
    assert x.tham_chieu_chu == (((0, 'A1'), (0, 'B1'), (1, 'Z1')), ())
    for address, sheet in [('A1', 0), ('B1', 0), ('Z1', 1)]:
        v = vung_o(x, address, sheet)
        assert v.manh is x.vung[x.shared[0]].manh
    assert x.vung[x.shared[1]].chu == 'DEMO tên chưa dùng'
    assert x.vung[x.shared[1]].manh


def test_map_ten_sheet_va_custom_attr_khong_cho_doi_ten_sheet():
    p = phan_demo(day_du=True)
    p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('DEMO 1', 'DEMO _x0041_ &amp; B')
    p['docProps/app.xml'] = p['docProps/app.xml'].replace('DEMO 1', 'DEMO A &amp; B')
    x = doc(p)
    v = next(v for v in x.vung if v.ma == 'ten_sheet')
    assert v.chu == 'DEMO A & B'
    assert v.manh[0].thuoc_tinh == 'name'
    v.kiem_thay_the(v.chu)
    with pytest.raises(LoiNghiepVu):
        v.kiem_thay_the('[[MASKCT-0001]]')
    v = next(v for v in x.vung if v.ma == 'custom_ten')
    assert v.chu == 'DEMO chủ hồ sơ' and v.duoc_sua
    a, b = v.manh[0].byte[0][0], v.manh[0].byte[-1][1]
    assert p['docProps/custom.xml'].encode()[a:b].decode() == 'DEMO chủ hồ sơ'
    assert v.unicode_tu_byte('docProps/custom.xml', v.manh[0].so_nut, a, b, thuoc_tinh='name') == ((0, len(v.chu)),)


@pytest.mark.parametrize('state', ['hidden', 'veryHidden', 'Hidden', 'DEMO Nguyễn Lan'])
def test_sheet_an_bi_chan_khac_hang_cot_an(state):
    p = phan_demo()
    p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('sheetId="1"', f'sheetId="1" state="{state}"')
    loi(p)


@pytest.mark.parametrize('ten', ['', 'DEMO [MASKCT-0001]', 'DEMO/A', "'DEMO", "DEMO'", 'D' * 32, 'DEMO _x000D_', 'DEMO _x200B_'])
def test_ten_sheet_khong_hop_le(ten):
    p = phan_demo()
    p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('name="DEMO 1"', 'name="' + ten + '"')
    loi(p)


@pytest.mark.parametrize('node', ['<f>DEMO Nguyễn Lan</f><v>1</v>', '<f/>', '<extLst/>', '<is><t>DEMO</t></is>', '<v>DEMO Nguyễn Lan</v>'])
def test_formula_cache_sai_kieu(node):
    p = excel_demo(noi_dung='<row r="1"><c r="A1">' + node + '</c></row>')
    loi(p)


@pytest.mark.parametrize('typ', ['str', 'f', 'DEMO Nguyễn Lan', 'b', 'd', 'e'])
def test_cell_type_va_value_sai(typ):
    loi(excel_demo(noi_dung=f'<row r="1"><c r="A1" t="{typ}"><v>DEMO Nguyễn Lan</v></c></row>'))


@pytest.mark.parametrize('node', [
    '<definedNames><definedName name="DEMO">DEMO Nguyễn Lan</definedName></definedNames>',
    '<externalReferences/>', '<connections/>', '<pivotCaches/>', '<extLst/>', '<fileSharing userName="DEMO Nguyễn Lan"/>',
    '<workbookProtection/>', '<webPublishing/>', '<customWorkbookViews/>'])
def test_workbook_vung_cam(node):
    p = phan_demo()
    p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('</workbook>', node + '</workbook>')
    loi(p)


@pytest.mark.parametrize('node', ['<drawing r:id="rId1"/>', '<legacyDrawing r:id="rId1"/>', '<hyperlinks/>', '<conditionalFormatting/>',
    '<dataValidations/>', '<autoFilter ref="A1:B2"/>', '<headerFooter><oddHeader>DEMO Nguyễn Lan</oddHeader></headerFooter>',
    '<sheetProtection/>', '<protectedRanges/>', '<extLst/>', '<oleObjects/>', '<controls/>', '<tableParts/>', '<picture/>'])
def test_sheet_vung_cam(node):
    p = phan_demo()
    p['xl/worksheets/sheet1.xml'] = p['xl/worksheets/sheet1.xml'].replace('</worksheet>', node + '</worksheet>').replace(f'xmlns="{S}"', f'xmlns="{S}" xmlns:r="{R}"')
    loi(p)


@pytest.mark.parametrize('path', ['xl/comments1.xml', 'xl/threadedComments/threadedComment1.xml', 'xl/persons/person.xml',
    'xl/charts/chart1.xml', 'xl/drawings/drawing1.xml', 'xl/media/image1.png', 'xl/embeddings/oleObject1.bin',
    'xl/vbaProject.bin', 'xl/externalLinks/externalLink1.xml', 'xl/connections.xml', 'customXml/item1.xml',
    'docProps/thumbnail.jpeg', '_xmlsignatures/sig1.xml', 'xl/printerSettings/printerSettings1.bin',
    'xl/tables/table1.xml', 'xl/worksheets/_rels/sheet1.xml.rels', 'xl/DEMO-Nguyen-Lan.xml'])
@pytest.mark.parametrize('mocoi', [True, False])
def test_part_cam_ke_ca_mo_coi(path, mocoi):
    p = phan_demo()
    if mocoi:
        p[path] = b'DEMO Nguyen Lan'
    else:
        them_phan(p, path, f'<worksheet xmlns="{S}"/>', CT_S + 'worksheet+xml', 'worksheet', rid='rId30', chu='xl/workbook.xml')
    loi(p)


@pytest.mark.parametrize('sua', ['sai_type', 'sai_root', 'rel_type', 'rel_target', 'rel_external', 'rel_duplicate', 'sheet_rid', 'sheet_double', 'part_mocoi'])
def test_danh_trao_type_root_quan_he_va_mo_coi(sua):
    p = phan_demo()
    if sua == 'sai_type':
        p['[Content_Types].xml'] = p['[Content_Types].xml'].replace(CT_S + 'styles+xml', CT_S + 'sharedStrings+xml')
    elif sua == 'sai_root':
        p['xl/styles.xml'] = f'<sst xmlns="{S}"/>'
    elif sua == 'rel_type':
        p['xl/_rels/workbook.xml.rels'] = p['xl/_rels/workbook.xml.rels'].replace(R + '/styles', R + '/sharedStrings')
    elif sua == 'rel_target':
        p['xl/_rels/workbook.xml.rels'] = p['xl/_rels/workbook.xml.rels'].replace('Target="styles.xml"', 'Target="sharedStrings.xml"')
    elif sua == 'rel_external':
        p['xl/_rels/workbook.xml.rels'] = p['xl/_rels/workbook.xml.rels'].replace('Target="styles.xml"', 'Target="styles.xml" TargetMode="External"')
    elif sua == 'rel_duplicate':
        p['xl/_rels/workbook.xml.rels'] = p['xl/_rels/workbook.xml.rels'].replace('rId10', 'rId1')
    elif sua == 'sheet_rid':
        p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('r:id="rId1"', 'r:id="rId10"')
    elif sua == 'sheet_double':
        p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('</sheets>', '<sheet name="DEMO 2" sheetId="2" r:id="rId1"/></sheets>')
    else:
        p['xl/theme/theme1.xml'] = '<a:theme xmlns:a="' + A + '" name="Office Theme"/>'
        p['[Content_Types].xml'] = p['[Content_Types].xml'].replace('</Types>', '<Override PartName="/xl/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/></Types>')
    loi(p)


@pytest.mark.parametrize('sua', ['font', 'style_name', 'format', 'format_id', 'font_ref', 'fill_ref', 'border_ref', 'xf_ref',
    'count', 'unknown_attr', 'unknown_node', 'style_index', 'row_style', 'col_style', 'calcChain'])
def test_styles_numfmt_moi_thuoc_tinh_chua_phan_loai(sua):
    p = phan_demo(day_du=True)
    replacements = {
        'font': ('val="Calibri"', 'val="DEMO Nguyễn Lan"'),
        'style_name': ('name="Normal"', 'name="DEMO Nguyễn Lan"'),
        'format': ('yyyy-mm-dd', '&quot;DEMO Nguyễn Lan&quot;'),
        'format_id': ('numFmtId="164" fontId', 'numFmtId="166" fontId'),
        'font_ref': ('fontId="1"', 'fontId="2"'), 'fill_ref': ('fillId="0"', 'fillId="2"'),
        'border_ref': ('borderId="0"', 'borderId="1"'), 'xf_ref': ('xfId="0"', 'xfId="9"'),
        'count': ('fonts count="2"', 'fonts count="3"'), 'unknown_attr': ('<xf ', '<xf name="DEMO Nguyễn Lan" '),
        'unknown_node': ('<dxfs count="0"/>', '<dxfs count="1"><dxf/></dxfs>')}
    if sua in replacements:
        a, b = replacements[sua]
        p['xl/styles.xml'] = p['xl/styles.xml'].replace(a, b)
    elif sua == 'calcChain':
        p['xl/calcChain.xml'] = f'<calcChain xmlns="{S}"><c r="A1" i="1"/></calcChain>'
    else:
        a, b = {'style_index': ('s="2"', 's="3"'), 'row_style': ('<row r="1"', '<row r="1" s="3"'),
                'col_style': ('min="1"', 'min="1" style="3"')}[sua]
        p['xl/worksheets/sheet1.xml'] = p['xl/worksheets/sheet1.xml'].replace(a, b)
    loi(p)


@pytest.mark.parametrize('phan,a,b', [
    ('xl/workbook.xml', '<workbook ', '<workbook codeName="DEMO Nguyễn Lan" '),
    ('xl/worksheets/sheet1.xml', '<row r="1"', '<row r="1" author="DEMO Nguyễn Lan"'),
    ('xl/worksheets/sheet1.xml', '<c r="A1"', '<c r="A1" cm="1"'),
    ('xl/sharedStrings.xml', '<si>', '<si name="DEMO Nguyễn Lan">'),
    ('xl/sharedStrings.xml', '<si>', '<si><rPh sb="0" eb="1"><t>DEMO Nguyễn Lan</t></rPh>'),
    ('xl/sharedStrings.xml', '<t>', '<t author="DEMO Nguyễn Lan">'),
    ('xl/theme/theme1.xml', 'name="Office Theme"', 'name="DEMO Nguyễn Lan"'),
    ('xl/theme/theme1.xml', 'typeface="Calibri"', 'typeface="DEMO Nguyễn Lan"'),
    ('xl/theme/theme1.xml', 'val="000000"', 'val="DEMO Nguyễn Lan"'),
    ('xl/theme/theme1.xml', '<a:objectDefaults/>', '<a:objectDefaults><a:spDef/></a:objectDefaults>'),
    ('docProps/core.xml', '<cp:revision>1', '<cp:revision>DEMO Nguyễn Lan'),
    ('docProps/core.xml', '2026-10-30T00:00:00Z', '2026-02-30T00:00:00Z'),
    ('docProps/core.xml', '<dc:creator>', '<dc:creator name="DEMO Nguyễn Lan">'),
    ('docProps/app.xml', '<DocSecurity>0', '<DocSecurity>DEMO Nguyễn Lan'),
    ('docProps/app.xml', '<LinksUpToDate>false', '<LinksUpToDate>DEMO Nguyễn Lan'),
    ('docProps/app.xml', '</Properties>', '<HyperlinkBase>DEMO Nguyễn Lan</HyperlinkBase></Properties>'),
    ('docProps/app.xml', '<vt:lpstr>DEMO 1', '<vt:lpstr>DEMO Nguyễn Lan'),
    ('docProps/app.xml', '<vt:lpstr>Worksheets', '<vt:lpstr>DEMO Nguyễn Lan'),
    ('docProps/custom.xml', '<vt:lpwstr>', '<vt:lpwstr author="DEMO Nguyễn Lan">'),
    ('docProps/custom.xml', '<vt:lpwstr>', '<vt:vector>'),
    ('docProps/custom.xml', 'pid="3"', 'pid="2"'),
    ('docProps/custom.xml', 'name="DEMO ngày"', 'name="DEMO chủ hồ sơ"'),
])
def test_metadata_va_attribute_khong_duoc_bo_qua(phan, a, b):
    p = phan_demo(day_du=True)
    assert a in p[phan]
    p[phan] = p[phan].replace(a, b)
    loi(p)


@pytest.mark.parametrize('a,b', [('ref="A3:B3"', 'ref="XFE3:XFF3"'), ('ref="A3:B3"', 'ref="B3:A3"'),
    ('ref="A3:B3"', 'ref="A3:A3"'), ('count="1"><mergeCell', 'count="2"><mergeCell'),
    ('</mergeCells>', '<mergeCell ref="B3:C4"/></mergeCells>')])
def test_merge_sai_bien_chong_va_dem(a, b):
    p = phan_demo()
    p['xl/worksheets/sheet1.xml'] = p['xl/worksheets/sheet1.xml'].replace(a, b)
    if a == '</mergeCells>':
        p['xl/worksheets/sheet1.xml'] = p['xl/worksheets/sheet1.xml'].replace('mergeCells count="1"', 'mergeCells count="2"')
    loi(p)


@pytest.mark.parametrize('a,b', [('r="A1"', 'r="XFE1"'), ('r="A1"', 'r="A1048577"'), ('r="B1"', 'r="A1"'),
    ('row r="2"', 'row r="1"'), ('r="A1"', 'r="A2"'), ('<v>0</v>', '<v>2</v>'),
    ('<v>0</v>', '<v>-1</v>'), ('<v>0</v>', '<v>0.0</v>')])
def test_dia_chi_hang_va_shared_index_sai(a, b):
    p = phan_demo()
    p['xl/worksheets/sheet1.xml'] = p['xl/worksheets/sheet1.xml'].replace(a, b)
    loi(p)


@pytest.mark.parametrize('a,b', [('count="2"', 'count="3"'), ('uniqueCount="2"', 'uniqueCount="1"')])
def test_shared_count_sai(a, b):
    p = phan_demo()
    p['xl/sharedStrings.xml'] = p['xl/sharedStrings.xml'].replace(a, b)
    loi(p)


@pytest.mark.parametrize('n,dat', [(32767, True), (32768, False)])
@pytest.mark.parametrize('shared', [False, True])
def test_o_gioi_han_dung_vuot_khong_cat(n, dat, shared):
    p = inline('<t>' + 'D' * n + '</t>')
    if shared:
        p['xl/worksheets/sheet1.xml'] = f'<worksheet xmlns="{S}"><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c></row></sheetData></worksheet>'
        them_phan(p, 'xl/sharedStrings.xml', f'<sst xmlns="{S}" count="1" uniqueCount="1"><si><t>' + 'D' * n + '</t></si></sst>',
                  CT_S + 'sharedStrings+xml', 'sharedStrings', rid='rId2', chu='xl/workbook.xml')
    if dat:
        assert len(vung_o(doc(p)).chu) == n
    else:
        loi(p, ma='MASK_QUA_GIOI_HAN')


@pytest.mark.parametrize('n,dat', [(20000, True), (20001, False)])
def test_cell_limit_tong_nhieu_sheet_dung_va_vuot(n, dat):
    rows = ''.join(f'<row r="{i}"><c r="A{i}"><v>{i % 10}</v></c></row>' for i in range(1, 10001))
    p = excel_demo(so_sheet=2, noi_dung=rows)
    if n == 20001:
        p['xl/worksheets/sheet2.xml'] = p['xl/worksheets/sheet2.xml'].replace('</sheetData>', '<row r="10001"><c r="A10001"/></row></sheetData>')
    raw = goi_office(p)
    if dat:
        assert len(doc_excel(raw, kiem_huy=lambda: None).o) == 20000
    else:
        loi({}, raw=raw, ma='MASK_QUA_GIOI_HAN')


@pytest.mark.parametrize('n,dat', [(50, True), (51, False)])
def test_sheet_limit_dung_vuot(n, dat):
    p = excel_demo(so_sheet=n, noi_dung='<row r="1"><c r="A1"/></row>')
    if dat:
        assert len(doc(p).o) == 50
    else:
        loi(p, ma='MASK_QUA_GIOI_HAN')


def test_node_limit_tong_goi_co_theme_va_styles(monkeypatch):
    p = phan_demo(day_du=True)
    n = doc(p).goi.goi.thong_ke['so_nut']
    monkeypatch.setattr(xa, 'SO_NUT_TOI_DA', n)
    assert doc(p).goi.goi.thong_ke['so_nut'] == n
    monkeypatch.setattr(xa, 'SO_NUT_TOI_DA', n - 1)
    loi(p, ma='MASK_QUA_GIOI_HAN')


def test_tong_text_shared_lap_khong_dung_preview(monkeypatch):
    p = phan_demo()
    x = doc(p)
    # Trần hạ để cô lập phép đếm phần dùng lặp; giới hạn thực vẫn 500000.
    base = x.goi.goi.thong_ke['so_ky_tu']
    extra = 2 * len('DEMO Công ty Ánh Dương')
    import e_mask.doc_excel as de
    monkeypatch.setattr(de, 'KY_TU_VAO_TOI_DA', base + extra)
    assert doc(p)
    monkeypatch.setattr(de, 'KY_TU_VAO_TOI_DA', base + extra - 1)
    loi(p, ma='MASK_QUA_GIOI_HAN')


@pytest.mark.parametrize('v', ['1000000', '1.000000e+06', '-0', '+0001.00', '.25'])
def test_so_giu_raw_khong_ep_chuoi_hoac_float(v):
    p = excel_demo(noi_dung=f'<row r="1"><c r="A1" t="n"><v>{v}</v></c></row>')
    x = doc(p)
    assert x.o[0].gia_tri == v and x.o[0].kieu == 'n' and x.o[0].vung is None
    assert x.o[0].xml_goc == f'<c r="A1" t="n"><v>{v}</v></c>'.encode()


def test_epoch1904_va_ngay_iso_giu_nguyen():
    p = excel_demo(noi_dung='<row r="1"><c r="A1" t="d"><v>2026-10-30</v></c></row>')
    p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('<sheets>', '<workbookPr date1904="1"/><sheets>')
    x = doc(p)
    assert x.epoch1904 and x.o[0].gia_tri == '2026-10-30' and not [v for v in x.vung if v.ma == 'o']


@pytest.mark.parametrize('gia_tri', ['DEMO _x0041_\r\n&<', 'DEMO \x01', 'DEMO 😀', 'DEMO Nguyễn\u200b Lan'])
def test_chu_xml_chep_chon_loc_khu_hoi_st_cr(gia_tri):
    # Helper escape không là writer XLSX; reader độc lập đọc lại đúng chuỗi.
    p = inline('<t xml:space="preserve">' + chu_xml(gia_tri) + '</t>')
    assert vung_o(doc(p)).chu == gia_tri


@pytest.mark.parametrize('ma', ['huy', 'ChuaRo'])
@pytest.mark.parametrize('stage', [1, 50, 300, 700, 1000])
def test_huy_chua_ro_giu_nguyen_khong_tra_ket_qua(ma, stage):
    raw = goi_office(phan_demo(day_du=True))
    dem = 0
    error = RuntimeError('DEMO hủy') if ma == 'huy' else ChuaRo('DEMO-tuong-quan')
    def huy():
        nonlocal dem
        dem += 1
        if dem >= stage:
            raise error
    with pytest.raises(type(error)) as e:
        doc_excel(raw, kiem_huy=huy)
    assert e.value is error


def test_khong_mang_ghi_may_log_hay_trang_thai_chung(monkeypatch, capsys):
    raw = goi_office(phan_demo(day_du=True))
    def cam(*args, **kwargs):
        raise AssertionError('Không được gọi tài nguyên ngoài RAM')
    monkeypatch.setattr(socket, 'socket', cam)
    monkeypatch.setattr(builtins, 'open', cam)
    monkeypatch.setattr(Path, 'open', cam)
    a = doc_excel(raw, kiem_huy=lambda: None)
    b = doc_excel(raw, kiem_huy=lambda: None)
    assert a is not b and a.vung is not b.vung
    assert capsys.readouterr() == ('', '')
    loi({}, raw=b'DEMO Nguyen Lan')
    assert capsys.readouterr() == ('', '')


def test_ngan_van_dung_mau_va_reader_khong_them_kho():
    goc = Path(__file__).resolve().parents[2]
    chuan = (goc / '_chung/mau-ma/ngan.py').read_bytes().replace(b'\r\n', b'\n')
    runtime = (goc / 'e_mask/goi/e_mask/e_mask/ngan.py').read_bytes().replace(b'\r\n', b'\n')
    assert runtime == chuan
    from e_mask.ngan import NganBoNho, chon_ngan
    class App:
        pass
    a = App()
    a.ngan = NganBoNho()
    assert chon_ngan(a) is a.ngan


def test_nguon_da_doc_khong_sua_sha_bytes_va_lf():
    goc = Path(__file__).resolve().parents[2]
    for p, bam in [
        ('e_hoa_don/goi/e_hoa_don/e_hoa_don/xlsx_toi_thieu.py', 'ad6a6c8e89d73e5e994c4f21066c7ee76640b261eaf253dc82a69cf1337fa46d'),
        ('e_mask/ma-nguon/nguon/privacy/excel.py', 'b837f86a9accaea662357b485fb0d835a6deef4ba4e9f8ccffb0bb9a1243fdc7'),
        ('e_mask/ma-nguon/nguon/privacy/excel_values.py', '6bbcb1c0e19923d13923ca935970199626aca668ec3f23d903ef3e512c22e901')]:
        assert hashlib.sha256((goc / p).read_bytes().replace(b'\r\n', b'\n')).hexdigest() == bam


@pytest.mark.parametrize('n,dat', [(100000, True), (100001, False)])
def test_node_limit_100000_thuc_khong_nang_tran(n, dat):
    p = phan_demo()
    baseline = doc(p).goi.goi.thong_ke['so_nut']
    so, du = divmod(n - baseline, 8)
    fonts = '<font><b/><i/><strike/><outline/><shadow/><condense/><extend/></font>' * so + '<font/>' * du
    p['xl/styles.xml'] = p['xl/styles.xml'].replace('fonts count="2"', f'fonts count="{2 + so + du}"').replace('</fonts>', fonts + '</fonts>')
    raw = dong_goi(p)  # STORED, không để ratio cao che mất phép thử 100000 node.
    assert len(raw) < 1048576
    if dat:
        assert doc_excel(raw, kiem_huy=lambda: None).goi.goi.thong_ke['so_nut'] == 100000
    else:
        loi({}, raw=raw, ma='MASK_QUA_GIOI_HAN')


def test_format_ke_thua_hang_cot_khong_doi_raw_cell():
    p = phan_demo()
    key = 'xl/worksheets/sheet1.xml'
    p[key] = f'<worksheet xmlns="{S}"><cols><col min="1" max="1" style="1"/><col min="2" max="2" style="2"/></cols><sheetData>' \
             '<row r="1"><c r="A1"><v>46325</v></c><c r="B1"><v>1000000</v></c></row>' \
             '<row r="2" s="2" customFormat="1"><c r="A2"><v>1000000</v></c><c r="B2" s="1"><v>46325</v></c></row></sheetData></worksheet>'
    # Không dùng shared strings trong bản này.
    p['xl/sharedStrings.xml'] = p['xl/sharedStrings.xml'].replace('count="2"', 'count="0"')
    x = doc(p)
    assert [o.style_goc for o in x.o] == [None, None, None, '1']
    assert [o.style_hieu_luc for o in x.o] == [1, 2, 2, 1]
    assert [(o.style_hang, o.style_cot) for o in x.o] == [(None, 1), (None, 2), (2, 1), (2, 2)]
    assert x.o[0].xml_goc == b'<c r="A1"><v>46325</v></c>'


@pytest.mark.parametrize('sep', [' ', '\n', '\r\n', '\t'])
def test_khai_xml_hop_le_khong_nham_voi_pi(sep):
    p = inline('<t>DEMO Nguyễn Lan</t>')
    key = 'xl/worksheets/sheet1.xml'
    p[key] = '<?xml' + sep + 'version="1.0" encoding="UTF-8"?>' + p[key]
    assert vung_o(doc(p)).chu == 'DEMO Nguyễn Lan'


@pytest.mark.parametrize('kieu', ['dtd', 'entity', 'pi', 'comment', 'xmlns_la', 'namespace_gia'])
@pytest.mark.parametrize('codec', ['utf-8', 'utf-16'])
def test_b1_xml_attack_van_chan_tren_cong_excel(kieu, codec):
    p = inline('<t>DEMO Nguyễn Lan</t>')
    key = 'xl/worksheets/sheet1.xml'
    if kieu in ('dtd', 'entity'):
        dtd = '<!DOCTYPE worksheet>' if kieu == 'dtd' else '<!DOCTYPE worksheet [<!ENTITY demo SYSTEM "file:///DEMO-Nguyen-Lan">]>'
        p[key] = dtd + p[key]
    elif kieu == 'pi':
        p[key] = '<?demo DEMO-Nguyen-Lan?>' + p[key]
    elif kieu == 'comment':
        p[key] = p[key].replace('<sheetData>', '<!-- DEMO Nguyen Lan --><sheetData>')
    elif kieu == 'xmlns_la':
        p[key] = p[key].replace('<worksheet ', '<worksheet xmlns:demo="urn:DEMO-Nguyen-Lan" ')
    else:
        p[key] = p[key].replace(S, 'urn:DEMO-Nguyen-Lan')
    p[key] = (f'<?xml version="1.0" encoding="{codec}"?>' + p[key]).encode(codec)
    loi(p)


@pytest.mark.parametrize('kieu,hop_le,khong_hop_le', [
    ('i1', '-128', '128'), ('i2', '32767', '32768'), ('i4', '-2147483648', '-2147483649'),
    ('i8', '9223372036854775807', '9223372036854775808'), ('int', '2147483647', '2147483648'),
    ('ui1', '255', '256'), ('ui2', '65535', '65536'), ('ui4', '4294967295', '4294967296'),
    ('ui8', '18446744073709551615', '18446744073709551616'), ('uint', '4294967295', '-1'),
    ('r4', '1.25', 'NaN'), ('r8', '-1.25e3', 'Infinity'), ('decimal', '1000000.00', 'DEMO Nguyen Lan'),
    ('bool', 'false', 'DEMO Nguyen Lan'), ('date', '2026-10-30', '2026-13-30'),
    ('filetime', '2026-10-30T00:00:00Z', 'DEMO Nguyen Lan')])
def test_custom_type_ngay_so_boolean_bien(kieu, hop_le, khong_hop_le):
    p = phan_demo(day_du=True)
    key = 'docProps/custom.xml'
    old = '<vt:lpwstr>DEMO Lê Hạ</vt:lpwstr>'
    p[key] = p[key].replace(old, f'<vt:{kieu}>{hop_le}</vt:{kieu}>')
    assert doc(p)
    p[key] = p[key].replace(f'<vt:{kieu}>{hop_le}', f'<vt:{kieu}>{khong_hop_le}')
    loi(p)


@pytest.mark.parametrize('loai', ['shared', 'inline'])
def test_rich_shared_inline_nfd_cf_va_st_lap(loai):
    text = 'DEMO Trần\u200b Ánh _x000D_ Dương'
    rich = '<r><rPr><color rgb="FF000000"/><b/></rPr><t>DEMO Trần\u200b </t></r><r><t>Ánh _x000D_ Dương</t></r>'
    p = inline(rich)
    if loai == 'shared':
        key = 'xl/worksheets/sheet1.xml'
        p[key] = f'<worksheet xmlns="{S}"><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c></row></sheetData></worksheet>'
        them_phan(p, 'xl/sharedStrings.xml', f'<sst xmlns="{S}" count="1" uniqueCount="2"><si>' + rich + '</si><si><t>DEMO _x0041_ chưa dùng</t></si></sst>',
                  CT_S + 'sharedStrings+xml', 'sharedStrings', rid='rId2', chu='xl/workbook.xml')
    v = vung_o(doc(p))
    assert v.chu == text.replace('_x000D_', '\r') and len(v.manh) == 2
    assert '\u200b' in v.chu and not unicodedata.is_normalized('NFC', v.chu)


def test_cuoi_vung_dai_khong_co_preview_bo_duoi():
    p = inline('<t>' + 'D' * 32000 + ' DEMO Nguyễn Lan</t>')
    v = vung_o(doc(p))
    assert v.chu.endswith(' DEMO Nguyễn Lan')
    assert len(v.manh[0].byte) == len(v.chu)
    assert v.khoang_byte(32001, len(v.chu))


def test_chu_rong_map_neo_khong_nham_vao_tail_sau_node():
    a = vung_o(doc(inline('<t/>')))
    b = vung_o(doc(inline('<t></t>')))
    assert a.chu == b.chu == '' and a.manh[0].neo is None
    assert b.manh[0].neo is not None


def test_hai_shared_khong_dung_len_toi_da_nhung_tong_vuot():
    p = phan_demo()
    p['xl/sharedStrings.xml'] = f'<sst xmlns="{S}" count="2" uniqueCount="17">' + ''.join('<si><t>' + 'D' * 30000 + '</t></si>' for _ in range(17)) + '</sst>'
    loi(p, ma='MASK_QUA_GIOI_HAN')


@pytest.mark.parametrize('value', ['NaN', 'Infinity', '1e9999', '1e9999999999999999999999999999'])
def test_so_khong_huu_han_ngoai_mien_chi_co_loi_nghiep_vu(value):
    p = excel_demo(noi_dung=f'<row r="1"><c r="A1"><v>{value}</v></c></row>')
    loi(p)


@pytest.mark.parametrize('phan,a,b', [
    ('xl/styles.xml', 'sz val="11"', 'sz val="410"'),
    ('xl/styles.xml', 'family val="2"', 'family val="6"'),
    ('xl/styles.xml', 'color theme="1"', 'color theme="1" tint="1.1"'),
    ('xl/worksheets/sheet1.xml', 'width="12"', 'width="256"'),
    ('xl/worksheets/sheet1.xml', 'defaultRowHeight="15"', 'defaultRowHeight="410"'),
    ('xl/worksheets/sheet1.xml', '<row r="1"', '<row r="1" ht="-1"'),
    ('xl/worksheets/sheet1.xml', '<row r="1"', '<row r="1" outlineLevel="8"'),
])
def test_style_so_va_layout_ngoai_profile(phan, a, b):
    p = phan_demo()
    p[phan] = p[phan].replace(a, b)
    loi(p)


@pytest.mark.parametrize('text', [
    '<![CDATA[DEMO Nguyễn Lan]]>', 'DEMO <![CDATA[Nguyễn]]> Lan',
    '_x00<![CDATA[41_]]>', '<![CDATA[_x0041_]]> DEMO',
])
def test_cdata_chua_co_profile_patch_phai_chan(text):
    loi(inline('<t>' + text + '</t>'))
