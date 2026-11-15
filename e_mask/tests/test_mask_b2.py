"""Gold DEMO và tấn công reader nội bộ; chưa Office/Local/Core thật."""

from dataclasses import FrozenInstanceError
import hashlib
import html
from pathlib import Path
import random
import struct
import unicodedata

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, ViecDaHuy

from e_mask import doc_tep as dt, doc_word as dw, xml_word as xw
from ho_tro_mask_b1 import CT_W, W, dong_goi, excel_demo, them_phan, word_demo
from ho_tro_mask_b2 import A, CP, CT_CHUNG, CUSTOM, EP, FMTID, VT, p, word_day_du, zip_office
from test_mask_b1 import cam_io, khong_huy, tu_choi


def doc(raw, kiem_huy=khong_huy):
    return dw.doc_word(raw, kiem_huy=kiem_huy)


def test_word_day_du_gold_vung_vi_tri_tung_text_va_metadata():
    phan = word_day_du()
    raw = zip_office(phan, descriptor=True)
    with cam_io():
        kq = doc(raw)
    assert kq.goi.zip.goc is raw
    assert kq.he_offset == 'unicode_code_point' and kq.phien_ban == 1
    assert kq.bam_tep == 'sha256:' + hashlib.sha256(raw).hexdigest()
    assert {p.ten: p.du_lieu for p in kq.goi.zip.phan} == {k: v.encode() for k, v in phan.items()}
    theme = kq.goi.cay['word/theme/theme1.xml']
    for tag in ('fillStyleLst', 'lnStyleLst', 'effectStyleLst', 'bgFillStyleLst'):
        assert len(theme.find('.//{' + A + '}' + tag)) == 3
    than = [v for v in kq.vung if v.loai == 'than']
    assert [v.van_ban for v in than] == [
        'DEMO Nguyễn Va\u200bn A\u0301nh', 'Ô gốc DEMO', 'Ô khác DEMO',
        'Tên DEMO ô nối', 'Ô cuối DEMO',
        'DEMO 😀 A&B\nC\rD\nE\t1.000.000 VND 30/10/2026\n\ufffc\ufffc\ufffc']
    assert len(than[0].anh_xa) == 3 and len({m.run for m in than[0].anh_xa}) == 3
    assert [m.style for m in than[0].anh_xa] == [('Normal', None), ('Normal', 'Emphasis'), ('Normal', 'Strong')]
    assert [m.an for m in than[0].anh_xa] == [False, False, True]
    assert than[1].o.hang == 0 and than[1].o.cot == 0 and than[1].o.gop_cot == 2
    assert than[2].o.cot == 2 and than[3].o.gop_tu == (0, 0)
    assert than[3].anh_xa[0].an is True
    assert len(kq.tham_chieu_note) == 3
    assert [r[:2] for r in kq.tham_chieu_note] == [('footnote', 2), ('footnote', 2), ('endnote', 3)]
    gold = {'dau_trang': ['Đầu trang DEMO'], 'chan_trang': ['Chân trang DEMO'],
            'footnote': ['\ufffc', 'Ghi chú DEMO lặp', 'Ghi chú DEMO lặp'], 'endnote': ['Cuối tài liệu DEMO']}
    for loai, values in gold.items():
        assert [v.van_ban for v in kq.vung if v.loai == loai] == values
    meta = [v.van_ban for v in kq.vung if v.loai == 'thuoc_tinh']
    assert meta == [
        'Normal.dotm', 'Quản lý DEMO', 'Công ty DEMO Ánh Dương', 'Microsoft Office Word', 'Title', 'Tựa DEMO',
        'Tiêu đề DEMO', 'Chủ đề DEMO', 'Người tạo DEMO', 'Mô tả DEMO', 'Người sửa DEMO', 'Từ khóa DEMO',
        'Tên DEMO & X', 'Giá trị DEMO', 'Số tiền DEMO (VND)', '1000000']
    assert [v.van_ban for v in kq.vung if v.loai == 'dinh_dang'] == [
        'Mục DEMO %1', 'Tên kiểu DEMO', 'Normal', 'Kiểu DEMO nghiêng', 'Kiểu DEMO đậm ẩn',
        'Office Theme', 'Office', 'Office', 'Office']
    assert kq.tong_ky_tu == sum(len(v.van_ban) for v in kq.vung)
    assert all(v.bam_van_ban == 'sha256:' + hashlib.sha256(v.van_ban.encode()).hexdigest() for v in kq.vung)
    assert all(v.ma == i for i, v in enumerate(kq.vung))
    assert not hasattr(kq, 'da_che') and not hasattr(kq, 'van_ban')
    assert 'DEMO' not in repr(kq) and 'DEMO' not in repr(kq.vung[0])
    with pytest.raises(FrozenInstanceError):
        kq.tong_ky_tu = 0


@pytest.mark.parametrize('codec', ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'utf-16-be'])
@pytest.mark.parametrize('cdata', [False, True])
def test_byte_map_code_point_entity_cr_cdata_nfd_cf_va_astral(codec, cdata):
    text = 'DEMO 😀 A\u0301\u200bnh & C\r\nD\rE'
    src = '<![CDATA[' + text + ']]>' if cdata else text.replace('&', '&amp;').replace('😀', '&#x1F600;')
    phan = word_demo(noi_dung=p(src + '&#13;&#xA;'))
    decl = 'UTF-8' if codec.startswith('utf-8') else ('UTF-16' if codec == 'utf-16' else codec.upper().replace('16-', '16'))
    phan['word/document.xml'] = ('<?xml version="1.0" encoding="' + decl + '"?>' + phan['word/document.xml']).encode(codec)
    kq = doc(dong_goi(phan))
    v = kq.vung[0]
    assert v.van_ban == 'DEMO 😀 A\u0301\u200bnh & C\nD\nE\r\n'
    assert unicodedata.normalize('NFC', v.van_ban) != v.van_ban
    assert len(v.anh_xa) == 1 and len(v.anh_xa[0].byte_ky_tu) == len(v.van_ban)
    source = phan['word/document.xml']
    actual_codec = ('utf-16-le' if source[:2] == b'\xff\xfe' else 'utf-16-be') if codec == 'utf-16' else 'utf-8' if codec == 'utf-8-sig' else codec
    for char, (dau, cuoi) in zip(v.van_ban, v.anh_xa[0].byte_ky_tu):
        token = source[dau:cuoi].decode(actual_codec)
        decoded = html.unescape(token) if token.startswith('&') else token.replace('\r\n', '\n').replace('\r', '\n')
        assert decoded == char
    assert v.bam_van_ban != kq.bam_tep


def test_thuoc_tinh_map_byte_entity_va_xml_attribute_newline():
    phan = word_day_du()
    phan['docProps/custom.xml'] = phan['docProps/custom.xml'].replace('Tên DEMO &amp; X', 'DEMO\r\nA&#13;B&#xA;C&amp;D')
    kq = doc(dong_goi(phan))
    v = next(v for v in kq.vung if v.phan == 'docProps/custom.xml' and v.anh_xa[0].thuoc_tinh == 'name')
    assert v.van_ban == 'DEMO A\rB\nC&D'
    m = v.anh_xa[0]
    assert m.kieu == 'attribute'
    raw = phan[v.phan].encode()
    assert raw[m.byte_bat_dau:m.byte_ket_thuc] == b'DEMO\r\nA&#13;B&#xA;C&amp;D'
    assert raw[slice(*m.byte_ky_tu[4])] == b'\r\n'


@pytest.mark.parametrize('co', [0, 2, 4, 6, 0x800, 0x806])
@pytest.mark.parametrize('descriptor,chu_ky,day_du', [(False, True, False), (True, True, False), (True, False, False), (True, True, True)])
def test_flags_office_descriptor_crc_size_va_offset_goc(co, descriptor, chu_ky, day_du):
    phan = word_day_du()
    raw = zip_office(phan, co=co, descriptor=descriptor, chu_ky=chu_ky, local_day_du=day_du)
    kq = doc(raw)
    for pz in kq.goi.zip.phan:
        assert raw[pz.le_dau:pz.le_dau + 4] == b'PK\x03\x04'
        assert raw[pz.le_danh_muc:pz.le_danh_muc + 4] == b'PK\x01\x02'
        assert raw[pz.le_du_lieu:pz.le_du_lieu + pz.so_byte_nen]
        assert pz.du_lieu == phan[pz.ten].encode()
        assert pz.le_cuoi == pz.le_du_lieu + pz.so_byte_nen + ((16 if chu_ky else 12) if descriptor else 0)
    assert kq.goi.zip.goc is raw


@pytest.mark.parametrize('index', [0, 1, 2])
@pytest.mark.parametrize('chu_ky', [False, True])
def test_descriptor_gia_crc_size_tu_choi(index, chu_ky):
    raw = bytearray(zip_office(word_day_du(), descriptor=True, chu_ky=chu_ky))
    goi = dt.doc_tep(bytes(raw), kiem_huy=khong_huy)
    pz = goi.zip.phan[0]
    pos = pz.le_du_lieu + pz.so_byte_nen + (4 if chu_ky else 0) + index * 4
    struct.pack_into('<I', raw, pos, (struct.unpack_from('<I', raw, pos)[0] + 1) & 0xffffffff)
    tu_choi(lambda: doc(bytes(raw)), 'MASK_TEP_CHUA_HO_TRO')


@pytest.mark.parametrize('co', [1, 0x10, 0x20, 0x40, 0x100, 0x1000, 0x4000, 0x8000])
def test_flag_lai_tu_choi(co):
    tu_choi(lambda: doc(zip_office(word_day_du(), co=co)), 'MASK_TEP_CHUA_HO_TRO')


def test_cong_flags_chung_excel_toi_thieu_khong_doi_reader_b3():
    kq = dt.doc_tep(zip_office(excel_demo(), descriptor=True), kiem_huy=khong_huy)
    assert kq.loai == 'xlsx'
    tu_choi(lambda: doc(zip_office(excel_demo())), 'MASK_TEP_CHUA_HO_TRO')


@pytest.mark.parametrize('ten', ['comments', 'commentsExtended', 'commentsIds', 'people', 'vbaProject', 'customXml', 'embeddings', 'media', 'unknown'])
def test_part_cam_mo_coi_ke_ca_khong_co_text(ten):
    phan = word_day_du()
    phan['word/' + ten + '.xml'] = f'<w:settings xmlns:w="{W}"/>'
    tu_choi(lambda: doc(dong_goi(phan)), 'MASK_TEP_CHUA_HO_TRO')


@pytest.mark.parametrize('node', ['ins', 'del', 'delText', 'moveFrom', 'moveTo', 'rPrChange', 'pPrChange', 'sectPrChange', 'tblPrChange', 'tcPrChange', 'cellIns', 'cellDel', 'commentRangeStart', 'commentRangeEnd', 'commentReference', 'fldSimple', 'instrText', 'fldChar', 'txbxContent', 'drawing', 'pict', 'object', 'altChunk', 'sdt', 'customXml', 'smartTag'])
def test_node_cam_khong_co_text_van_tu_choi(node):
    phan = word_demo(noi_dung='<w:p><w:r><w:' + node + '/></w:r></w:p>')
    tu_choi(lambda: doc(dong_goi(phan)), 'MASK_TEP_CHUA_HO_TRO')


@pytest.mark.parametrize('attr,value', [('author', 'Tên DEMO'), ('val', 'Tên DEMO'), ('unknown', 'Tên DEMO')])
def test_attribute_cam_o_node_da_biet(attr, value):
    phan = word_demo(noi_dung=f'<w:p><w:r><w:rPr><w:b w:{attr}="{value}"/></w:rPr><w:t>DEMO</w:t></w:r></w:p>')
    tu_choi(lambda: doc(dong_goi(phan)), 'MASK_TEP_CHUA_HO_TRO')


@pytest.mark.parametrize('part,truoc,sau', [
    ('word/styles.xml', 'w:styleId="Strong"', 'w:styleId="Tên DEMO"'),
    ('word/styles.xml', 'w:ascii="Calibri"', 'w:ascii="Tên DEMO"'),
    ('word/fontTable.xml', 'w:name="Calibri"', 'w:name="Tên DEMO"'),
    ('word/theme/theme1.xml', 'typeface="Calibri"', 'typeface="Tên DEMO"'),
    ('word/theme/theme1.xml', 'val="123456"', 'val="Tên DEMO"'),
    ('word/settings.xml', 'w:percent="100"', 'w:percent="Tên DEMO"'),
    ('docProps/app.xml', '<Pages>1</Pages>', '<Pages>Tên DEMO</Pages>'),
    ('docProps/app.xml', '<HyperlinkBase/>', '<HyperlinkBase>http://demo.invalid</HyperlinkBase>'),
    ('docProps/core.xml', '<cp:revision>1</cp:revision>', '<cp:revision>Tên DEMO</cp:revision>'),
    ('docProps/custom.xml', '<vt:i4>1000000</vt:i4>', '<vt:i4>Tên DEMO</vt:i4>'),
    ('docProps/custom.xml', FMTID, '{DEMO-NOT-A-FMTID}'),
])
def test_gia_tri_bat_bien_phai_duoc_profile_chung_minh(part, truoc, sau):
    phan = word_day_du()
    assert truoc in phan[part]
    phan[part] = phan[part].replace(truoc, sau)
    tu_choi(lambda: doc(dong_goi(phan)), 'MASK_TEP_CHUA_HO_TRO')


@pytest.mark.parametrize('part', ['docProps/core.xml', 'docProps/app.xml', 'docProps/custom.xml', 'word/styles.xml', 'word/theme/theme1.xml'])
def test_moi_metadata_style_theme_text_name_thuc_su_co_map(part):
    phan = word_day_du()
    if part.endswith('core.xml'):
        phan[part] = phan[part].replace('Tiêu đề DEMO', 'TÊN-DEMO-ĐỘC-LẬP')
    elif part.endswith('app.xml'):
        phan[part] = phan[part].replace('Quản lý DEMO', 'TÊN-DEMO-ĐỘC-LẬP')
    elif part.endswith('custom.xml'):
        phan[part] = phan[part].replace('Giá trị DEMO', 'TÊN-DEMO-ĐỘC-LẬP')
    elif part.endswith('styles.xml'):
        phan[part] = phan[part].replace('Kiểu DEMO đậm ẩn', 'TÊN-DEMO-ĐỘC-LẬP')
    else:
        phan[part] = phan[part].replace('Office Theme', 'TÊN-DEMO-ĐỘC-LẬP')
    kq = doc(dong_goi(phan))
    found = [v for v in kq.vung if v.van_ban == 'TÊN-DEMO-ĐỘC-LẬP']
    assert len(found) == 1 and found[0].phan == part and found[0].anh_xa


@pytest.mark.parametrize('bien', ['doan', 'o', 'story'])
def test_khong_ghep_qua_bien_de_doan_ten(bien):
    phan = word_demo(noi_dung=p('DEMO Nguyễn') + p('Văn Ánh'))
    if bien == 'o':
        phan = word_demo(noi_dung='<w:tbl><w:tr><w:tc>' + p('DEMO Nguyễn') + '</w:tc><w:tc>' + p('Văn Ánh') + '</w:tc></w:tr></w:tbl>')
    elif bien == 'story':
        phan = word_demo(noi_dung=p('DEMO Nguyễn') + '<w:sectPr><w:headerReference w:type="default" r:id="rId9"/></w:sectPr>')
        them_phan(phan, 'word/header1.xml', f'<w:hdr xmlns:w="{W}">{p("Văn Ánh")}</w:hdr>', CT_W + 'header+xml', 'header')
    kq = doc(dong_goi(phan))
    assert [v.van_ban for v in kq.vung] == ['DEMO Nguyễn', 'Văn Ánh']
    assert all('NguyễnVăn' not in v.van_ban and 'Nguyễn Văn' not in v.van_ban for v in kq.vung)


def test_graph_content_type_root_namespace_danh_trao():
    phan = word_day_du()
    cases = []
    for truoc, sau, part in [
        ('header+xml', 'footer+xml', '[Content_Types].xml'),
        ('/header"', '/footer"', 'word/_rels/document.xml.rels'),
        ('<w:hdr', '<w:ftr', 'word/header1.xml'),
        (W, W + '/unknown', 'word/header1.xml'),
        ('xmlns:w=', 'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:w=', 'word/document.xml'),
        ('<w:body>', '<w:body><w:t>Tên DEMO</w:t>', 'word/document.xml'),
    ]:
        cp = dict(phan)
        assert truoc in cp[part]
        cp[part] = cp[part].replace(truoc, sau)
        cases.append(cp)
    for cp in cases:
        tu_choi(lambda: doc(dong_goi(cp)), 'MASK_TEP_CHUA_HO_TRO')


@pytest.mark.parametrize('dang', ['note_trung', 'note_thieu', 'gop_sai', 'style_thieu', 'style_vong'])
def test_quan_he_nghia_note_style_va_merge_sai(dang):
    phan = word_day_du()
    if dang == 'note_trung':
        phan['word/footnotes.xml'] = phan['word/footnotes.xml'].replace('w:id="4"', 'w:id="2"')
    elif dang == 'note_thieu':
        phan['word/document.xml'] = phan['word/document.xml'].replace('w:id="2"', 'w:id="99"')
    elif dang == 'gop_sai':
        phan['word/document.xml'] = phan['word/document.xml'].replace('w:vMerge w:val="restart"', 'w:vMerge w:val="continue"')
    elif dang == 'style_thieu':
        phan['word/document.xml'] = phan['word/document.xml'].replace('w:val="Strong"', 'w:val="Title"')
    else:
        phan['word/styles.xml'] = phan['word/styles.xml'].replace('<w:name w:val="Normal"/>', '<w:name w:val="Normal"/><w:basedOn w:val="Normal"/>')
    tu_choi(lambda: doc(dong_goi(phan)), 'MASK_TEP_CHUA_HO_TRO')


@pytest.mark.parametrize('loi', [
    '<w:p><w:pPr/><w:pPr/></w:p>',
    '<w:p><w:r><w:t>DEMO</w:t><w:rPr/></w:r></w:p>',
    '<w:p><w:r><w:rPr><w:vanish/><w:vanish w:val="0"/></w:rPr></w:r></w:p>',
    '<w:p><w:r><w:t><w:b/></w:t></w:r></w:p>',
    '<w:p><w:r>Định danh DEMO ngoài text node</w:r></w:p>',
    '<w:sectPr/>' + p('DEMO'),
])
def test_cau_truc_quen_nhung_vi_tri_hoac_so_lan_lai_phai_tu_choi(loi):
    tu_choi(lambda: doc(dong_goi(word_demo(noi_dung=loi))), 'MASK_TEP_CHUA_HO_TRO')


@pytest.mark.parametrize('kieu,chu', [
    ('i1', '128'), ('i2', '-32769'), ('i4', '2147483648'),
    ('i8', '9223372036854775808'), ('uint', '-1'), ('ui1', '256'),
    ('r4', 'NaN'), ('r8', 'Infinity'), ('decimal', '1E999'),
    ('bool', 'Tên DEMO'), ('filetime', 'Tên DEMO'),
])
def test_property_co_kieu_khong_dung_quy_cach_khong_bat_bien(kieu, chu):
    phan = word_day_du()
    phan['docProps/custom.xml'] = phan['docProps/custom.xml'].replace('<vt:i4>1000000</vt:i4>', f'<vt:{kieu}>{chu}</vt:{kieu}>')
    tu_choi(lambda: doc(dong_goi(phan)), 'MASK_TEP_CHUA_HO_TRO')


def test_custom_property_so_co_the_la_ma_dinh_danh_van_phai_co_map():
    phan = word_day_du()
    phan['docProps/custom.xml'] = phan['docProps/custom.xml'].replace('Số tiền DEMO (VND)', 'Mã định danh DEMO').replace('1000000', '0123456789')
    kq = doc(dong_goi(phan))
    found = [v for v in kq.vung if v.phan == 'docProps/custom.xml' and v.van_ban == '0123456789']
    assert len(found) == 1 and found[0].anh_xa[0].kieu == 'text'
    assert found[0].anh_xa[0].byte_ky_tu
    node = kq.goi.cay[found[0].phan]
    for i in found[0].anh_xa[0].nut:
        node = node[i]
    assert node.tag == '{' + VT + '}i4' and node.text == '0123456789'


@pytest.mark.parametrize('dia_chi', ['word/document.xml', 'word/header1.xml', 'word/footer1.xml', 'word/footnotes.xml', 'word/endnotes.xml'])
def test_chu_an_va_khong_xuat_hien_trong_preview_van_co_gold(dia_chi):
    phan = word_day_du()
    root = phan[dia_chi]
    # Chèn đúng run trong đoạn đầu của từng story/notes, giữ mọi đoạn còn lại.
    root = root.replace('<w:p>', '<w:p><w:r><w:rPr><w:webHidden/></w:rPr><w:t>DEMO-CANARY-ẨN</w:t></w:r>', 1)
    phan[dia_chi] = root
    kq = doc(dong_goi(phan))
    found = [v for v in kq.vung if 'DEMO-CANARY-ẨN' in v.van_ban]
    assert len(found) == 1 and found[0].phan == dia_chi and found[0].anh_xa[0].an


def test_map_tat_ca_vi_tri_text_va_attribute_duoc_quyet_dinh_quet():
    kq = doc(zip_office(word_day_du(), descriptor=True))
    for v in kq.vung:
        source = next(pz.du_lieu for pz in kq.goi.zip.phan if pz.ten == v.phan)
        root = kq.goi.cay[v.phan]
        vi_tri = 0
        for m in v.anh_xa:
            assert m.bat_dau == vi_tri
            assert m.ket_thuc == m.bat_dau + len(m.byte_ky_tu)
            e = root
            for chi_so in m.nut:
                e = e[chi_so]
            if m.kieu == 'text':
                assert (e.text or '') == v.van_ban[m.bat_dau:m.ket_thuc]
            elif m.kieu == 'attribute':
                assert e.get(m.thuoc_tinh) == v.van_ban[m.bat_dau:m.ket_thuc]
            else:
                assert source[m.byte_bat_dau:m.byte_ket_thuc].startswith(b'<w:')
            if m.run is not None:
                r = root
                for chi_so in m.run:
                    r = r[chi_so]
                assert r.tag == '{' + W + '}r'
            assert all(0 <= dau < cuoi <= len(source) for dau, cuoi in m.byte_ky_tu)
            vi_tri = m.ket_thuc
        assert vi_tri == len(v.van_ban)


@pytest.mark.parametrize('exc', [ViecDaHuy(), ChuaRo('DEMO-tuong-quan')])
@pytest.mark.parametrize('moc', [1, 30, 300, 1200, 2200])
def test_huy_chua_ro_truyen_nguyen_khong_output_tung_giai_doan(exc, moc):
    raw = zip_office(word_day_du(), descriptor=True)
    dem, out = 0, []
    def huy():
        nonlocal dem
        dem += 1
        if dem == moc:
            raise exc
    with cam_io():
        with pytest.raises(type(exc)) as e:
            out.append(doc(raw, huy))
    assert e.value is exc and not out


def test_tran_tong_text_b1_dung_500000_va_cong_mot_ke_ca_metadata():
    phan = word_day_du()
    kq = dt.doc_tep(dong_goi(phan), kiem_huy=khong_huy)
    con = 500000 - kq.thong_ke['so_ky_tu']
    phan['docProps/core.xml'] = phan['docProps/core.xml'].replace('Tiêu đề DEMO', 'Tiêu đề DEMO' + 'a' * con)
    raw = dong_goi(phan)
    assert len(raw) < 1048576
    kq = doc(raw)
    assert kq.goi.thong_ke['so_ky_tu'] == 500000 and kq.tong_ky_tu <= 500000
    phan['docProps/core.xml'] = phan['docProps/core.xml'].replace('Tiêu đề DEMO', 'Tiêu đề DEMOa')
    tu_choi(lambda: doc(dong_goi(phan)), 'MASK_QUA_GIOI_HAN')


def test_tran_text_logic_reader_dung_500000_va_cong_mot_doc_lap_b1():
    # Ký hiệu tab không có text XML để B1 đếm, nhưng có code point logic.
    # Cả hai đầu vào đều dưới trần B1: ca +1 phải bị chính reader chặn.
    for them, dat in ((0, True), (1, False)):
        than = '<w:p><w:r><w:t>' + 'a' * (495000 + them) + '</w:t>' + '<w:tab/>' * 5000 + '</w:r></w:p>'
        raw = dong_goi(word_demo(noi_dung=than))
        assert dt.doc_tep(raw, kiem_huy=khong_huy).thong_ke['so_ky_tu'] < 500000
        if dat:
            kq = doc(raw)
            assert kq.tong_ky_tu == 500000
            assert len(kq.vung[0].van_ban) == 500000
        else:
            tu_choi(lambda: doc(raw), 'MASK_QUA_GIOI_HAN')


@pytest.mark.parametrize('n,dat', [(20000, True), (20001, False)])
def test_tran_o_word_dem_moi_o_ke_ca_rong(n, dat):
    phan = word_demo(noi_dung='<w:tbl><w:tr>' + ('<w:tc><w:p/></w:tc>' * n) + '</w:tr></w:tbl>')
    raw = dong_goi(phan)
    if dat:
        kq = doc(raw)
        assert len(kq.vung) == n
    else:
        tu_choi(lambda: doc(raw), 'MASK_QUA_GIOI_HAN')


def test_gioi_han_ten_zip_va_target_256_257():
    assert dt._kiem_ten('D' * 256) == 'd' * 256
    tu_choi(lambda: dt._kiem_ten('D' * 257), 'MASK_TEP_CHUA_HO_TRO')


def test_bien_doi_byte_ngau_nhien_chi_co_thanh_cong_noi_bo_hoac_loi_an_toan():
    rnd = random.Random(20261115)
    raw = zip_office(word_day_du(), descriptor=True)
    for _ in range(100):
        cp = bytearray(raw)
        cp[rnd.randrange(len(cp))] ^= rnd.randrange(1, 256)
        try:
            kq = doc(bytes(cp))
        except Exception as e:
            from kho_tri_thuc_sdk.engine import LoiNghiepVu
            assert isinstance(e, LoiNghiepVu)
            assert e.ma in ('MASK_TEP_CHUA_HO_TRO', 'MASK_QUA_GIOI_HAN')
        else:
            assert not hasattr(kq, 'da_che')


def test_khong_import_engine_khac_khong_doi_manifest_va_nguon_co_sha():
    goi = Path(__file__).resolve().parents[1] / 'goi/e_mask'
    nguon = (goi / 'NGUON.md').read_text(encoding='utf-8')
    for ten in ('doc_word.py', 'xml_word.py', 'doc_tep.py'):
        raw = (goi / 'e_mask' / ten).read_bytes()
        # SHA bytes ghi đúng checkout lúc bàn giao; SHA LF dùng cho hồi quy
        # Linux/Windows vì Git có thể đổi CRLF sau checkout.
        assert hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest() in nguon
        assert b'from e_doi_chieu' not in raw and b'from e_trich_xuat' not in raw
