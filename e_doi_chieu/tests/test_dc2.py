"""Chỉ DEMO; đã kiểm bằng Core giả (CoreGia), không OCR/AI/Cloud thật."""
import hashlib
import importlib
import io
import json
from contextlib import nullcontext
from pathlib import Path
import struct
import sys
import zipfile

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia

GOI = Path(__file__).resolve().parents[1] / "goi/e_doi_chieu"
sys.path.insert(0, str(GOI))
chay = importlib.import_module("e_doi_chieu.chay")
doc = importlib.import_module("e_doi_chieu.doc_docx")
ct = importlib.import_module("e_doi_chieu.cau_truc")
W = doc.W_NS
R = doc.R_NS
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = doc.CT_NS


def p(text):
    from xml.sax.saxutils import escape
    return '<w:p><w:r><w:t xml:space="preserve">' + escape(text) + '</w:t></w:r></w:p>'


def tc(text="", props=""):
    return "<w:tc><w:tcPr>" + props + "</w:tcPr>" + p(text) + "</w:tc>"


def table_demo():
    return ('<w:tbl><w:tblGrid><w:gridCol/><w:gridCol/><w:gridCol/></w:tblGrid>'
            '<w:tr>' + tc("Ô gộp DEMO", '<w:gridSpan w:val="2"/><w:vMerge w:val="restart"/>') + tc() + '</w:tr>'
            '<w:tr>' + tc("", '<w:gridSpan w:val="2"/><w:vMerge/>') + tc("1.000.000 VND") + '</w:tr>'
            '<w:tr>' + tc("2026-10-30") + tc() + tc("Cuối bảng DEMO") + '</w:tr></w:tbl>')


def tao_goi(body=None, *, phu=None, sua=None, rels=None, compression=zipfile.ZIP_STORED):
    phu = phu or {}
    body = p("Công ty DEMO Ánh Dương") if body is None else body
    types = {'word/document.xml': doc.CT_DOC}
    links = []
    roots = {"header": "hdr", "footer": "ftr", "footnotes": "footnotes", "endnotes": "endnotes",
             "styles": "styles", "numbering": "numbering", "settings": "settings", "comments": "comments"}
    for name in phu:
        kind = next((k for k in roots if Path(name).stem.startswith(k)), None)
        if kind:
            types[name] = "application/vnd.openxmlformats-officedocument.wordprocessingml." + kind + "+xml"
            links.append(f'<Relationship Id="r{len(links)}" Type="{R}/{kind}" Target="{name[5:]}"/>')
    data = {
        '[Content_Types].xml': f'<Types xmlns="{CT}"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>' + ''.join(f'<Override PartName="/{k}" ContentType="{v}"/>' for k, v in types.items()) + '</Types>',
        '_rels/.rels': f'<Relationships xmlns="{REL}"><Relationship Id="main" Type="{R}/officeDocument" Target="word/document.xml"/></Relationships>',
        'word/document.xml': f'<w:document xmlns:w="{W}" xmlns:r="{R}"><w:body>{body}</w:body></w:document>',
        **phu,
    }
    if links or rels:
        data['word/_rels/document.xml.rels'] = f'<Relationships xmlns="{REL}">' + ''.join(links) + (rels or '') + '</Relationships>'
    data.update(sua or {})
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', compression=compression) as z:
        for name, value in data.items():
            i = zipfile.ZipInfo(name, (2026, 10, 30, 0, 0, 0))
            i.create_system = 0  # Bytes DEMO giống nhau trên Windows và Linux.
            i.compress_type = compression
            z.writestr(i, value.encode('utf-8') if isinstance(value, str) else value)
    return out.getvalue()


def chay_bytes(raw, core=None):
    core = core or CoreGia()
    tep = core.them_tep('DEMO.docx', raw, doc.MIME_DOCX)
    return core.chay_thu(chay.app, 'doi_chieu.doc_docx@1', {'loai': 'tep', 'tep': tep})


def loi(raw, ma="DC_WORD_KHONG_DOC_DUOC"):
    result = chay_bytes(raw)
    assert result['trang_thai'] == 'LOI', result
    assert result['ket_qua'] is None
    assert result['loi']['ma'] == ma, result
    assert 'DEMO bí mật' not in result['loi']['thong_diep']
    return result


def kiem_offsets(blocks, text):
    for b in blocks:
        assert text[b['bat_dau']:b['ket_thuc']] == b['van_ban']
        assert not {'hop', 'so_trang'} & b.keys()
        for o in b.get('o', []):
            assert text[o['bat_dau']:o['ket_thuc']] == o['van_ban']
            kiem_offsets(o['khoi'], text)


def test_nguyen_van_cau_truc_bam_schema():
    text = "  DEMO 😀 A\u0301nh Dương\t1.000.000 VND\n2026-10-30  "
    raw = tao_goi(p(text) + table_demo() + p('Kết thúc DEMO'))
    result = chay_bytes(raw)
    assert result['trang_thai'] == 'XONG', result
    v = result['ket_qua']['van_ban_tai_lieu']
    assert v['van_ban'] == text + '\nÔ gộp DEMO |  | \n |  | 1.000.000 VND\n2026-10-30 |  | Cuối bảng DEMO\nKết thúc DEMO'
    assert v['bam_dau_vao'] == 'sha256:' + hashlib.sha256(raw).hexdigest()
    assert v['so_trang'] == 0 and v['trang'] == [] and v['nguon_doc'] == 'docx'
    assert len(v['canh_bao']) == 1 and 'Chưa phân trang Word' in v['canh_bao'][0]
    assert v['don_vi_offset'] == 'unicode_code_point'
    blocks = v['khoi_docx']
    assert [b['loai'] for b in blocks] == ['doan', 'bang', 'doan']
    assert blocks[1]['o'][0]['gop_cot'] == 2 and blocks[1]['o'][0]['gop_hang'] == 2
    assert [o['van_ban'] for o in blocks[1]['o']] == ['Ô gộp DEMO', '', '1.000.000 VND', '2026-10-30', '', 'Cuối bảng DEMO']
    kiem_offsets(blocks, v['van_ban'])
    from test_dc1 import kiem_schema
    kiem_schema(result['ket_qua'], json.loads((GOI / 'van_ban_tai_lieu.schema.json').read_text(encoding='utf-8')))
    assert chay_bytes(raw)['ket_qua'] == result['ket_qua']


@pytest.mark.parametrize('part,root', [('header1', 'hdr'), ('footer1', 'ftr'), ('footnotes', 'footnotes'), ('endnotes', 'endnotes')])
def test_doc_vung_phu_day_du(part, root):
    body = p('DEMO thân')
    content = p('DEMO phụ 1.000.000 VND 2026-10-30') + table_demo()
    if 'notes' in root:
        tag = root[:-1]
        content = f'<w:{tag} w:id="1">{content}</w:{tag}>'
        body += f'<w:p><w:r><w:{tag}Reference w:id="1"/></w:r></w:p>'
    raw = tao_goi(body, phu={f'word/{part}.xml': f'<w:{root} xmlns:w="{W}">{content}</w:{root}>'})
    result = chay_bytes(raw)
    assert result['trang_thai'] == 'XONG', result
    v = result['ket_qua']['van_ban_tai_lieu']
    assert v['van_ban'].count('DEMO phụ 1.000.000 VND 2026-10-30') == 1
    assert 'Cuối bảng DEMO' in v['van_ban']
    assert v['vung_docx'][-1]['loai'] == root
    kiem_offsets(v['khoi_docx'], v['van_ban'])


@pytest.mark.parametrize('mark', ['ins', 'del', 'moveFrom', 'moveTo', 'rPrChange', 'pPrChange', 'sectPrChange',
                                    'tblPrChange', 'tblGridChange', 'tcPrChange', 'trPrChange', 'cellIns', 'cellDel',
                                    'cellMerge', 'numberingChange', 'customXmlInsRangeStart', 'moveToRangeEnd',
                                    'commentRangeStart', 'commentRangeEnd', 'commentReference'])
def test_chua_chot_than_bang(mark):
    loi(tao_goi(table_demo() + f'<w:p><w:r><w:{mark}/></w:r></w:p>'), 'DC_WORD_CHUA_CHOT')


@pytest.mark.parametrize('part,root', [('header1', 'hdr'), ('footer1', 'ftr'), ('footnotes', 'footnotes'), ('endnotes', 'endnotes'), ('comments', 'comments'), ('styles', 'styles'), ('numbering', 'numbering')])
@pytest.mark.parametrize('mark', ['ins', 'commentReference'])
def test_chua_chot_moi_phan_word(part, root, mark):
    raw = tao_goi(phu={f'word/{part}.xml': f'<w:{root} xmlns:w="{W}">{table_demo()}<w:{mark}/></w:{root}>'})
    result = loi(raw, 'DC_WORD_CHUA_CHOT')
    assert result['loi']['thong_diep'] == 'Bản Word còn sửa đổi hoặc bình luận. Anh chọn bản đã chốt để đối chiếu.'


def test_comment_namespace_mo_rong_va_track_setting():
    loi(tao_goi(phu={'word/commentsExtended.xml': '<w15:commentsEx xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml"><w15:commentEx/></w15:commentsEx>'}), 'DC_WORD_CHUA_CHOT')
    result = chay_bytes(tao_goi(phu={'word/settings.xml': f'<w:settings xmlns:w="{W}"><w:trackRevisions/></w:settings>'}))
    assert result['trang_thai'] == 'XONG'


@pytest.mark.parametrize('body', [
    '<w:altChunk/>', '<w:p><w:r><w:drawing/></w:r></w:p>', '<w:p><w:r><w:pict/></w:r></w:p>',
    '<w:p><w:r><w:object/></w:r></w:p>', '<w:p><w:fldSimple w:instr="DEMO"/></w:p>',
    '<w:p><w:r><w:instrText>DEMO</w:instrText></w:r></w:p>', '<w:p><w:r><w:sym/></w:r></w:p>',
    '<w:subDoc/>', '<w:moi/>', '<w:p><w:moi>' + p('DEMO bí mật') + '</w:moi></w:p>',
    '<w:p><w:pPr><w:t>DEMO bí mật</w:t></w:pPr></w:p>', '<w:sdt><w:sdtPr/></w:sdt>',
    '<w:tbl><w:tr><w:moi>' + tc('DEMO bí mật') + '</w:moi></w:tr></w:tbl>',
    '<w:p><w:r><m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"/></w:r></w:p>',
    '<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"/>',
])
def test_vung_chua_ho_tro_khong_duoc_canh_bao_roi_thanh_cong(body):
    loi(tao_goi(body))


@pytest.mark.parametrize('value', [b'DEMO', b'PK\x03\x04', b'', b'not zip DEMO bi mat'])
def test_hong_zip(value):
    loi(value)


@pytest.mark.parametrize('xml', [
    '<w:document',
    f'<!DOCTYPE x [<!ENTITY demo "DEMO bí mật">]><w:document xmlns:w="{W}"><w:body>{p("&demo;")}</w:body></w:document>',
    f'<!DOCTYPE x SYSTEM "file:///DEMO"><w:document xmlns:w="{W}"><w:body/></w:document>',
    f'<w:document xmlns:w="{W}"><w:body><w:p/></w:body><w:body/></w:document>',
])
def test_hong_xml_dtd(xml):
    loi(tao_goi(sua={'word/document.xml': xml}))


def test_dtd_utf16_phan_phu_va_hong_header():
    xml = f'<?xml version="1.0" encoding="utf-16"?><!DOCTYPE x [<!ENTITY a "DEMO">]><w:hdr xmlns:w="{W}"/>'
    loi(tao_goi(phu={'word/header1.xml': xml.encode('utf-16')}))
    loi(tao_goi(phu={'word/header1.xml': b'<DEMO'}))


@pytest.mark.parametrize('name', ['../DEMO.xml', '/DEMO.xml', 'word/../DEMO.xml', 'word/./DEMO.xml',
                                   'word\\DEMO.xml', 'word//DEMO.xml', 'word/%2e.xml', 'C:DEMO.xml',
                                   'word/document.xml\x00DEMO', 'WORD/DOCUMENT.XML'])
def test_zip_ten_khong_an_toan(name):
    raw = tao_goi()
    buf = io.BytesIO(raw)
    with (pytest.warns(UserWarning) if '\x00' in name else nullcontext()), zipfile.ZipFile(buf, 'a') as z:
        z.writestr(name, 'DEMO')
    loi(buf.getvalue())


def test_zip_trung_symlink_crc():
    buf = io.BytesIO(tao_goi())
    with pytest.warns(UserWarning), zipfile.ZipFile(buf, 'a') as z:
        z.writestr('word/document.xml', 'DEMO')
    loi(buf.getvalue())
    buf = io.BytesIO(tao_goi())
    with zipfile.ZipFile(buf, 'a') as z:
        i = zipfile.ZipInfo('DEMO-link')
        i.create_system = 3
        i.external_attr = 0o120777 << 16
        z.writestr(i, 'DEMO')
    loi(buf.getvalue())
    raw = tao_goi()
    loi(raw.replace(b'C\xc3\xb4ng', b'X\xc3\xb4ng', 1))


@pytest.mark.parametrize('target,mode', [('https://example.invalid/DEMO', 'External'), ('file:///DEMO', 'External'),
                                        ('https://example.invalid', 'Internal'), ('../../../DEMO.xml', 'Internal'),
                                        ('%2e%2e/DEMO.xml', 'Internal'), ('missing.xml', 'Internal')])
def test_quan_he_ngoai_va_dich_sai(target, mode):
    loi(tao_goi(rels=f'<Relationship Id="x" Type="{R}/hyperlink" Target="{target}" TargetMode="{mode}"/>'))


def test_quan_he_ngoai_phan_phu_va_nhung():
    loi(tao_goi(phu={'word/header1.xml': f'<w:hdr xmlns:w="{W}"/>'}, sua={
        'word/_rels/header1.xml.rels': f'<Relationships xmlns="{REL}"><Relationship Id="x" Type="{R}/hyperlink" Target="https://example.invalid" TargetMode="External"/></Relationships>'}))
    loi(tao_goi(sua={'word/DEMO.xml': '<DEMO/>'}, rels=f'<Relationship Id="x" Type="{R}/oleObject" Target="DEMO.xml"/>'))


def test_doc_sdt_customxml_bang_long_tab_break_va_hyperlink_noi():
    inner = '<w:tbl><w:tr>' + tc('DEMO lồng') + '</w:tr></w:tbl>'
    body = ('<w:sdt><w:sdtPr/><w:sdtContent><w:customXml>' + p('DEMO') + '</w:customXml></w:sdtContent></w:sdt>'
            '<w:p><w:hyperlink w:anchor="DEMO"><w:r><w:t>A</w:t><w:tab/><w:t>B</w:t><w:br/><w:t>C</w:t><w:noBreakHyphen/><w:softHyphen/></w:r></w:hyperlink></w:p>'
            '<w:tbl><w:sdt><w:sdtContent><w:tr><w:sdt><w:sdtContent><w:tc>' + p('DEMO ô') + inner + '</w:tc></w:sdtContent></w:sdt></w:tr></w:sdtContent></w:sdt></w:tbl>')
    result = chay_bytes(tao_goi(body))
    assert result['trang_thai'] == 'XONG', result
    v = result['ket_qua']['van_ban_tai_lieu']
    assert v['van_ban'] == 'DEMO\nA\tB\nC‑\u00ad\nDEMO ô\nDEMO lồng'
    kiem_offsets(v['khoi_docx'], v['van_ban'])


def test_loi_gop_doc_co_noi_dung_khong_bi_mat():
    body = table_demo().replace('<w:vMerge/></w:tcPr>' + p(''), '<w:vMerge/></w:tcPr>' + p('DEMO không được mất'))
    loi(tao_goi(body))
    loi(tao_goi('<w:p><w:r><w:footnoteReference w:id="99"/></w:r></w:p>'))


def test_so_tu_dong_va_style():
    numbering = f'<w:numbering xmlns:w="{W}"><w:abstractNum w:abstractNumId="0"><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="Điều %1."/></w:lvl></w:abstractNum><w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num></w:numbering>'
    body = '<w:p><w:pPr><w:numPr><w:numId w:val="1"/></w:numPr></w:pPr><w:r><w:t>DEMO</w:t></w:r></w:p>' * 2
    result = chay_bytes(tao_goi(body, phu={'word/numbering.xml': numbering}))
    assert result['trang_thai'] == 'XONG', result
    assert result['ket_qua']['van_ban_tai_lieu']['van_ban'] == 'Điều 1. DEMO\nĐiều 2. DEMO'


def test_zip_bomb_va_so_muc_truoc_giai_nen(monkeypatch):
    bomb = tao_goi(p('D' * 200000), compression=zipfile.ZIP_DEFLATED)
    def khong_duoc_doc(*a, **kw):
        pytest.fail('Đã giải nén trước khi kiểm trần')
    monkeypatch.setattr(doc, '_doc_xml', khong_duoc_doc)
    loi(bomb, 'DC_QUA_GIOI_HAN')
    buf = io.BytesIO(tao_goi())
    with zipfile.ZipFile(buf, 'a') as z:
        for i in range(2000):
            z.writestr(f'DEMO-{i}', b'')
    loi(buf.getvalue(), 'DC_QUA_GIOI_HAN')
    # Khai tổng giải nén >100 MiB trong central directory, không cần cấp phát.
    raw = bytearray(tao_goi())
    pos = raw.index(b'PK\x01\x02')
    struct.pack_into('<I', raw, pos + 24, 101 * 1048576)
    loi(bytes(raw), 'DC_QUA_GIOI_HAN')


def test_tran_xml_do_sau_ky_tu(monkeypatch):
    raw = tao_goi('<w:customXml>' * 129 + p('DEMO') + '</w:customXml>' * 129)
    loi(raw, 'DC_QUA_GIOI_HAN')
    loi(tao_goi(p('D' * 500001)), 'DC_QUA_GIOI_HAN')
    with monkeypatch.context() as m:
        m.setattr(doc, 'XML_TOI_DA', 100)
        loi(tao_goi(), 'DC_QUA_GIOI_HAN')
    with monkeypatch.context() as m:
        m.setattr(doc, 'SO_NUT_XML_TOI_DA', 10)
        loi(tao_goi(p('DEMO') * 5), 'DC_QUA_GIOI_HAN')
    with monkeypatch.context() as m:
        m.setattr(doc, 'JSON_TOI_DA', 100)
        loi(tao_goi(), 'DC_QUA_GIOI_HAN')


def test_huy_core_gia_khi_dang_doc(monkeypatch):
    core = CoreGia()
    tep = core.them_tep('DEMO.docx', tao_goi(p('DEMO') * 400), doc.MIME_DOCX)
    vid = core.giao_viec('doi_chieu.doc_docx@1', {'loai': 'tep', 'tep': tep})
    original = doc._doc_xml
    def huy(*a, **kw):
        core.huy(vid)
        return original(*a, **kw)
    monkeypatch.setattr(doc, '_doc_xml', huy)
    core.chay(chay.app)
    result = core.xem(vid)
    assert result['trang_thai'] == 'HUY' and result['ket_qua'] is None


def test_viec_mo_tep_doc_bytes_that_tran_kich_thuoc_va_huy():
    raw = tao_goi()
    class Viec:
        dau_vao = {'loai': 'tep', 'tep': {'tep_id': 'DEMO', 'mime': doc.MIME_DOCX, 'kich_thuoc': len(raw)}}
        so_lan = 0
        def kiem_huy(self): pass
        def tien_do(self, *a): pass
        def mo_tep(self, tep_id):
            self.so_lan += 1
            assert tep_id == 'DEMO'
            return io.BytesIO(raw)
    viec = Viec()
    doc.doc_docx(viec, phien_ban_engine='DEMO')
    assert viec.so_lan == 1
    viec.dau_vao['tep']['kich_thuoc'] += 1
    with pytest.raises(LoiNghiepVu, match='Không đọc đầy đủ'):
        doc.doc_docx(viec, phien_ban_engine='DEMO')
    viec.dau_vao['tep']['kich_thuoc'] = doc.TEP_TOI_DA + 1
    with pytest.raises(LoiNghiepVu) as ex:
        doc.doc_docx(viec, phien_ban_engine='DEMO')
    assert ex.value.ma == 'DC_QUA_GIOI_HAN' and viec.so_lan == 2


def test_demo_goi_that():
    results = CoreGia().chay_thu_demo(chay.app, GOI)
    assert results and all(r['trang_thai'] == 'XONG' for r in results)
    assert (GOI / 'demo/DEMO-ban-chot.docx').read_bytes() == tao_goi(p('Công ty DEMO Ánh Dương') + table_demo())


@pytest.mark.parametrize('body', [
    '<w:p><w:r><w:br><w:t>DEMO bí mật</w:t></w:br></w:r></w:p>',
    '<w:p><w:r><w:tab><w:t>DEMO bí mật</w:t></w:tab></w:r></w:p>',
    '<w:p><w:r><w:lastRenderedPageBreak><w:t>DEMO bí mật</w:t></w:lastRenderedPageBreak></w:r></w:p>',
    '<w:sectPr><w:t>DEMO bí mật</w:t></w:sectPr>',
])
def test_khong_giau_chu_trong_node_la(body):
    loi(tao_goi(body))


def test_phan_phu_sai_root_va_xml_duoi_la():
    loi(tao_goi(phu={'word/header1.xml': f'<w:styles xmlns:w="{W}"/>'}))
    loi(tao_goi(phu={'word/DEMO.xml': f'<w:hdr xmlns:w="{W}">{p("DEMO")}</w:hdr>'}))
    loi(tao_goi(sua={'word/DEMO.data': b'<DEMO/>', '[Content_Types].xml':
        f'<Types xmlns="{CT}"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="data" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="{doc.CT_DOC}"/></Types>'}))


def test_dtd_phan_phu_khong_lien_quan_va_xml_quan_he():
    loi(tao_goi(sua={'docProps/DEMO.xml': '<!DOCTYPE x [<!ENTITY d "DEMO">]><x>&d;</x>'}))
    loi(tao_goi(sua={'word/DEMO.xml': f'<Relationships xmlns="{REL}"><Relationship Id="x" Type="{R}/hyperlink" Target="https://example.invalid" TargetMode="External"/></Relationships>'}))


def test_bang_hmerge_va_o_rong_cuoi():
    body = ('<w:tbl><w:tr>' + tc('DEMO A', '<w:hMerge w:val="restart"/>') + tc('DEMO B', '<w:hMerge/>') + tc() + '</w:tr></w:tbl>')
    result = chay_bytes(tao_goi(body))
    assert result['trang_thai'] == 'XONG', result
    v = result['ket_qua']['van_ban_tai_lieu']
    assert v['van_ban'] == 'DEMO A\nDEMO B |  | '
    assert v['khoi_docx'][0]['o'][0]['gop_cot'] == 2
    kiem_offsets(v['khoi_docx'], v['van_ban'])


def test_20mib_byte_that_va_khong_ghi_dia(monkeypatch):
    raw = tao_goi()
    def cam_ghi(*args, **kwargs):
        pytest.fail('Bộ đọc đã truy cập đĩa')
    monkeypatch.setattr('builtins.open', cam_ghi)
    assert doc.doc_bytes(raw, lambda: None, lambda *a: None, phien_ban_engine='DEMO')['loai'] == 'van_ban_tai_lieu'
    with pytest.raises(LoiNghiepVu) as ex:
        doc.doc_bytes(b'X' * (doc.TEP_TOI_DA + 1), lambda: None, lambda *a: None, phien_ban_engine='DEMO')
    assert ex.value.ma == 'DC_QUA_GIOI_HAN'


def test_doc_tep_tran_bytes_that_va_dong_handle(monkeypatch):
    raw = tao_goi()
    monkeypatch.setattr(doc, 'TEP_TOI_DA', 100)
    handle = io.BytesIO(raw)
    class Viec:
        dau_vao = {'loai': 'tep', 'tep': {'tep_id': 'DEMO', 'mime': doc.MIME_DOCX, 'kich_thuoc': 100}}
        def kiem_huy(self): pass
        def tien_do(self, *a): pass
        def mo_tep(self, *a): return handle
    with pytest.raises(LoiNghiepVu) as ex:
        doc.doc_docx(Viec(), phien_ban_engine='DEMO')
    assert ex.value.ma == 'DC_QUA_GIOI_HAN' and handle.closed


@pytest.mark.parametrize('compression', [zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED])
def test_kich_thuoc_crc_gia_khong_duoc_giau_duoi_xml(compression):
    import zlib
    xml = f'<w:document xmlns:w="{W}"><w:body>{p("DEMO")}</w:body></w:document>'.encode()
    raw = bytearray(tao_goi(sua={'word/document.xml': xml + b'DEMO khong duoc bo qua'}, compression=compression))
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        info = z.getinfo('word/document.xml')
    # Giả cả CRC/kích thước của đoạn đầu để ZipExtFile thông thường đọc đạt.
    struct.pack_into('<I', raw, info.header_offset + 14, zlib.crc32(xml))
    struct.pack_into('<I', raw, info.header_offset + 22, len(xml))
    pos = 0
    while True:
        pos = raw.index(b'PK\x01\x02', pos)
        n, ex, cm = struct.unpack_from('<3H', raw, pos + 28)
        if raw[pos + 46:pos + 46 + n] == b'word/document.xml':
            struct.pack_into('<I', raw, pos + 16, zlib.crc32(xml))
            struct.pack_into('<I', raw, pos + 24, len(xml))
            break
        pos += 46 + n + ex + cm
    loi(bytes(raw))


def test_deflate_nhieu_chunk_giu_dung_nguyen_van():
    import random
    rng = random.Random(20261030)
    text = 'DEMO ' + ''.join(rng.choices('abcXYZ0123456789 ÁnhDương😀', k=80000))
    result = chay_bytes(tao_goi(p(text), compression=zipfile.ZIP_DEFLATED))
    assert result['trang_thai'] == 'XONG', result
    assert result['ket_qua']['van_ban_tai_lieu']['van_ban'] == text


def test_zip_data_descriptor_hop_le():
    class Luong(io.BytesIO):
        def seek(self, *a):
            raise io.UnsupportedOperation('DEMO không seek')
    buf = Luong()
    with zipfile.ZipFile(io.BytesIO(tao_goi())) as source, zipfile.ZipFile(buf, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name in source.namelist():
            z.writestr(name, source.read(name))
    result = chay_bytes(buf.getvalue())
    assert result['trang_thai'] == 'XONG', result


@pytest.mark.parametrize('tag', ['numStyleLink', 'styleLink', 'lvlPicBulletId'])
def test_numbering_chua_ho_tro_khong_mat_nhan(tag):
    xml = f'<w:numbering xmlns:w="{W}"><w:{tag} w:val="DEMO"/></w:numbering>'
    loi(tao_goi(phu={'word/numbering.xml': xml}))


def test_so_tu_dong_style_ke_thua_va_sai_tham_chieu():
    numbering = f'<w:numbering xmlns:w="{W}"><w:abstractNum w:abstractNumId="0"><w:lvl w:ilvl="0"><w:numFmt w:val="upperRoman"/><w:lvlText w:val="%1."/></w:lvl></w:abstractNum><w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num></w:numbering>'
    styles = f'<w:styles xmlns:w="{W}"><w:style w:styleId="DEMO-base"><w:pPr><w:numPr><w:numId w:val="1"/></w:numPr></w:pPr></w:style><w:style w:styleId="DEMO"><w:basedOn w:val="DEMO-base"/></w:style></w:styles>'
    body = '<w:p><w:pPr><w:pStyle w:val="DEMO"/></w:pPr><w:r><w:t>DEMO</w:t></w:r></w:p>'
    result = chay_bytes(tao_goi(body, phu={'word/numbering.xml': numbering, 'word/styles.xml': styles}))
    assert result['trang_thai'] == 'XONG', result
    assert result['ket_qua']['van_ban_tai_lieu']['van_ban'] == 'I. DEMO'
    loi(tao_goi(body))  # Không đoán nhãn của style mất nguồn.
    loi(tao_goi(body, phu={'word/numbering.xml': numbering.replace('</w:numbering>', '<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num></w:numbering>'), 'word/styles.xml': styles}))
