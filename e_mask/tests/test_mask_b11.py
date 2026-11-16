"""Development DEMO B11 độc lập; không nhập công cụ/recipe held-out B10."""
from hashlib import sha256
import io
import json
from pathlib import Path
import unicodedata
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET
import zipfile

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu

from e_mask import tep_word as tw, tep_excel as tx, tai_nguyen
from ho_tro_mask_b1 import W, CT_W, CT_S, S, word_demo, excel_demo, them_phan
from ho_tro_mask_b3 import CP, DC, DCT, XSI, EP, CUSTOM, VT, STYLES, goi_office
from ho_tro_mask_b5 import bo as bo_ram
from ho_tro_mask_b7 import bo, chay, chuan_bi_het, giao
from ho_tro_mask_b8 import bo as bo_mo, giao as giao_mo, ket as ket_mo, da_don


DEV = json.loads(Path(__file__).with_name('demo_mask_b11.json').read_text(encoding='utf-8'))
TEN, ALIAS = DEV['ten'], DEV['alias']
SEEDS = ((TEN, 'CONG_TY', ALIAS),)


@pytest.fixture(autouse=True)
def _nguon_da_duyet():
    tai_nguyen.nap_tu_goi()


def _props(p, marker):
    """Ba loại metadata, có tên cần che và giá trị kỹ thuật cần giữ."""
    p['docProps/core.xml'] = (f'<cp:coreProperties xmlns:cp="{CP}" xmlns:dc="{DC}" '
        f'xmlns:dcterms="{DCT}" xmlns:xsi="{XSI}"><dc:creator>{TEN}</dc:creator>'
        f'<dc:title>{marker}</dc:title><dcterms:created xsi:type="dcterms:W3CDTF">'
        '2026-11-09T00:00:00Z</dcterms:created></cp:coreProperties>')
    p['docProps/app.xml'] = f'<Properties xmlns="{EP}"><Application>{marker}</Application><Company>{TEN}</Company></Properties>'
    p['docProps/custom.xml'] = (f'<Properties xmlns="{CUSTOM}" xmlns:vt="{VT}">'
        f'<property fmtid="{{D5CDD505-2E9C-101B-9397-08002B2CF9AE}}" pid="3" name="{marker}">'
        f'<vt:lpwstr>{TEN}</vt:lpwstr></property></Properties>')
    for rid, (ten, ct, qh) in enumerate([('core', 'application/vnd.openxmlformats-package.core-properties+xml', CP),
                         ('app', 'application/vnd.openxmlformats-officedocument.extended-properties+xml', EP),
                         ('custom', 'application/vnd.openxmlformats-officedocument.custom-properties+xml', CUSTOM)], 50):
        p['[Content_Types].xml'] = p['[Content_Types].xml'].replace('</Types>',
            f'<Override PartName="/docProps/{ten}.xml" ContentType="{ct}"/></Types>')
        kieu = ('http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties'
                if ten == 'core' else 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/'
                + ('extended-properties' if ten == 'app' else 'custom-properties'))
        p['_rels/.rels'] = p['_rels/.rels'].replace('</Relationships>',
            f'<Relationship Id="rId{rid}" Type="{kieu}" Target="docProps/{ten}.xml"/></Relationships>')
    return p


def _doan(chu, tach=False):
    cac = (chu[:13], chu[13:]) if tach else (chu,)
    return '<w:p>' + ''.join('<w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">'
        + escape(c) + '</w:t></w:r>' for c in cac) + '</w:p>'


def _tep(loai, marker='TEST', bien_the='thuong', *, chu=None):
    ten = unicodedata.normalize('NFD', TEN) if bien_the == 'nfd' else TEN
    chu = marker + '; tổng chi đã đối chiếu; 3.754.200 VND; 2026-11-09.' if chu is None else chu
    if loai == 'docx':
        noi = _doan(ten, bien_the == 'run') + _doan(chu)
        if bien_the == 'bang':
            noi += '<w:tbl><w:tblGrid><w:gridCol w:w="2400"/></w:tblGrid><w:tr><w:tc>' + _doan(TEN) + '</w:tc></w:tr></w:tbl>'
        p = word_demo(noi_dung=noi)
        if bien_the == 'note':
            p['word/document.xml'] = p['word/document.xml'].replace('</w:body>',
                '<w:p><w:r><w:footnoteReference w:id="2"/></w:r></w:p></w:body>')
            them_phan(p, 'word/footnotes.xml', f'<w:footnotes xmlns:w="{W}"><w:footnote w:id="2">'
                + _doan(TEN) + '</w:footnote></w:footnotes>', CT_W + 'footnotes+xml', 'footnotes')
    else:
        val = '<t>' + escape(ten) + '</t>'
        if bien_the == 'rich':
            val = '<r><rPr><b/></rPr><t>' + escape(ten[:13]) + '</t></r><r><t xml:space="preserve">' + escape(ten[13:]) + '</t></r>'
        o_chu = '<c r="B1" t="s"><v>0</v></c>' if bien_the in ('rich', 'shared') else '<c r="B1" t="inlineStr"><is>' + val + '</is></c>'
        noi = '<row r="1" hidden="1">' + o_chu + '<c r="D1" s="2"><v>3754200</v></c><c r="E1" s="1"><v>46335</v></c></row>'
        noi += '<row r="2"><c r="B2" t="inlineStr"><is><t>' + escape(chu) + '</t></is></c></row>'
        p = excel_demo(noi_dung=noi)
        p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('DEMO 1', marker)
        them_phan(p, 'xl/styles.xml', STYLES, CT_S + 'styles+xml', 'styles', chu='xl/workbook.xml')
        if bien_the in ('rich', 'shared'):
            them_phan(p, 'xl/sharedStrings.xml', f'<sst xmlns="{S}"><si>{val}</si></sst>',
                CT_S + 'sharedStrings+xml', 'sharedStrings', rid='rId8', chu='xl/workbook.xml')
    return goi_office(_props(p, marker))


def _phan(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        return {t: z.read(t) for t in z.namelist()}


@pytest.mark.parametrize('loai,bien_the', [('docx', b) for b in ('thuong', 'run', 'bang', 'note')]
                         + [('xlsx', b) for b in ('thuong', 'rich', 'shared')])
@pytest.mark.parametrize('marker', DEV['marker'])
def test_development_hai_lop_phat_hanh_giu_metadata_tien_ngay_va_format(loai, bien_the, marker):
    raw = _tep(loai, marker, bien_the)
    b = bo(loai, raw=raw, seeds=SEEDS, dang='tep')
    try:
        chuan_bi_het(b)
        # Lớp 1 chưa tải tệp ra: vẫn bắt buộc nguồn Local và hậu kiểm B7/B9.
        assert not b.cong.giao_cuoi
        giao(b)
        k = chay(b)
        assert k['trang_thai'] == 'XONG', k
        s = b.ram._ban_ghi.du_lieu['tep_word' if loai == 'docx' else 'tep_excel']
        sau = _phan(s['da_che']); truoc = _phan(raw)
        assert ALIAS.encode() in b''.join(sau.values())
        assert TEN.encode() not in b''.join(sau.values())
        # Oracle literal/ElementTree riêng, không dùng reader/map làm gold.
        for t in truoc:
            a, z = ET.fromstring(truoc[t]), ET.fromstring(sau[t])
            assert [(n.tag, n.attrib) for n in a.iter()] == [(n.tag, n.attrib) for n in z.iter()]
        assert marker.encode() in sau['docProps/core.xml']
        assert b'2026-11-09T00:00:00Z' in sau['docProps/core.xml']
        main = sau['word/document.xml' if loai == 'docx' else 'xl/worksheets/sheet1.xml']
        assert b'3.754.200 VND' in main and b'2026-11-09' in main
        if loai == 'xlsx':
            assert b'<v>3754200</v>' in main and b'<v>46335</v>' in main
            assert sau['xl/styles.xml'] == truoc['xl/styles.xml']
    finally:
        if b.ram._ban_ghi:
            b.ram._don(b.ram._ban_ghi)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_development_khu_hoi_dung_bytes_ram(loai):
    b = bo_mo(loai, raw=_tep(loai), seeds=SEEDS)
    giao_mo(b)
    assert ket_mo(b).du_lieu == b.raw
    da_don(b)


@pytest.mark.parametrize('chi_tieu', DEV['chi_tieu'])
@pytest.mark.parametrize('trang_thai', DEV['trang_thai'])
def test_ngu_phap_tong_hop_khong_bao_nham(chi_tieu, trang_thai):
    b = bo_ram(seeds=())
    chu = 'tổng ' + chi_tieu + ' ' + trang_thai + '.'
    with b.ram.buoc(b.v) as buoc:
        m = tw._kiem_vung(chu, (), buoc)
        assert m.da_che == chu


@pytest.mark.parametrize('chu', DEV['chan'])
@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_vung_tu_do_nghi_ten_hoac_so_van_chan(loai, chu):
    b = bo(loai, raw=_tep(loai, chu=chu), seeds=SEEDS, dang='tep')
    k = chay(b)
    assert k['trang_thai'] == 'LOI' and k['ket_qua'] is None
    assert b.ram._ban_ghi is None and not b.cong.giao_cuoi


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_nguon_local_sai_van_chan_va_don_ram(loai):
    b = bo(loai, raw=_tep(loai), seeds=SEEDS, dang='tep')
    chuan_bi_het(b)
    def sai(v):
        for p in v['phan_hoi']:
            p['nguon']['nha_cung_cap'] = 'cloud'
        return v
    giao(b, sua=sai)
    k = chay(b)
    assert k['trang_thai'] == 'LOI' and k['ket_qua'] is None
    assert b.ram._ban_ghi is None and not b.cong.giao_cuoi


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_local_bao_dinh_danh_tai_marker_van_phai_che_hoac_chan(loai):
    b = bo(loai, raw=_tep(loai, 'SAMPLE'), seeds=SEEDS, dang='tep')
    chuan_bi_het(b)
    h = b.ram._ban_ghi.du_lieu['ho_so_tep']
    a = h['map_quy_tac'].goc.index('SAMPLE')
    giao(b, spans=[(a, a + 6, 'to_chuc', 'chac')])
    k = chay(b)
    assert k['trang_thai'] == 'LOI' and k['ket_qua'] is None
    assert b.ram._ban_ghi is None and not b.cong.giao_cuoi


@pytest.mark.parametrize('ham', [tw._kiem_vung, tx._kiem_vung])
@pytest.mark.parametrize('gate', ['day_du', 'so', 'tien_ngay'])
def test_mien_canh_bao_khong_bo_hau_kiem_bat_buoc(ham, gate, monkeypatch):
    b = bo_ram(seeds=())
    if gate == 'day_du':
        that = tw.che._kiem_con_sot
        monkeypatch.setattr(tw.che, '_kiem_con_sot', lambda *a, **kw: (that(*a, **kw)[0], False))
    elif gate == 'so':
        monkeypatch.setattr(tw.che.core, 'numeric_review', lambda *a: {'changed': True})
    else:
        monkeypatch.setattr(tw.che, '_kiem_tien_ngay', lambda *a: False)
    with pytest.raises(LoiNghiepVu):
        with b.ram.buoc(b.v) as buoc:
            ham('SAMPLE', (), buoc)
    assert b.ram._ban_ghi is None


@pytest.mark.parametrize('ham', [tw._kiem_vung, tx._kiem_vung])
def test_marker_la_dinh_danh_da_biet_khong_duoc_mien_phan_con_sot(ham):
    b = bo_ram(seeds=())
    with pytest.raises(LoiNghiepVu):
        with b.ram.buoc(b.v) as buoc:
            ham('SAMPLE; SAMPLE', ((0, 6, ALIAS),), buoc)


def test_sha_held_out_b10_va_mask_2c_khong_doi():
    goc = Path(__file__).resolve().parents[1]
    # Byte LF cố định chạy được cả Linux và Windows checkout CRLF.
    # Không ghi/chuẩn hóa hai tệp được bảo vệ trên đĩa.
    for t, ma in [('cong-cu/demo/mask_tep_held_out.json', '8e6acb7ea56a2991553e7e3867dbf3510cba3f70cd0c464aeb33b2c51a6c1e46'),
                  ('cong-cu/mask_2c_4_ung_vien_demo.json', 'b3569b357132a7f7e0a7202b6e3d3c0b5fec2228c6ebd09604e7d05092485dd8')]:
        assert sha256((goc / t).read_bytes().replace(b'\r\n', b'\n')).hexdigest() == ma


# Phản ví dụ DEMO của rà bảo mật lượt 3; không phải gold B10.
PHAN_VI_DU_B11 = [
    ('DEMO - Vinamilk; tổng chi đã đối chiếu', 'Vinamilk'),
    ('DEMO (Techcombank); 3.754.200 VND', 'Techcombank'),
    ('DEMO.Vinamilk', 'Vinamilk'),
    ('DRAFT – Techcombank', 'Techcombank'),
    ('Tổng thu đã tổng hợp quỳnh trâm', 'quỳnh trâm'),
    ('Tổng chi đã kiểm tra cho Lan', 'Lan'),
    ('Tổng chi đã đối chiếu: Lan', 'Lan'),
    ('Tổng thu đã kiểm tra Hồng', 'Hồng'),
    ('DEMO & Vinamilk', 'Vinamilk'),
    ('SAMPLE - Techcombank', 'Techcombank'),
    ('DEMO (Techcombank)', 'Techcombank'),
    ('TEST - Vinamilk', 'Vinamilk'),
]


def _tep_phan_vi_du(loai, chu, vi_tri):
    if vi_tri == 'noi_dung':
        return _tep(loai, chu=chu)
    p = {t: raw.decode('utf-8') for t, raw in _phan(_tep(loai)).items()}
    if vi_tri == 'tieu_de':
        p['docProps/core.xml'] = p['docProps/core.xml'].replace(
            '<dc:title>TEST</dc:title>', '<dc:title>' + escape(chu) + '</dc:title>')
    else:
        p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('name="TEST"',
            'name="' + escape(chu, {'"': '&quot;'}) + '"')
    return goi_office(p)


def _chu_doc_lap(chu):
    return ''.join(c for c in unicodedata.normalize('NFD', chu).casefold() if c.isalnum())


@pytest.mark.parametrize('loai,vi_tri,chu,ten_that', [
    (loai, vi_tri, chu, ten) for chu, ten in PHAN_VI_DU_B11
    for loai, vi_tri in [('docx', 'noi_dung'), ('xlsx', 'noi_dung'),
                        ('docx', 'tieu_de'), ('xlsx', 'tieu_de'), ('xlsx', 'ten_sheet')]
    if vi_tri != 'ten_sheet' or (len(chu) <= 31 and not any(c in chu for c in ':;'))
])
@pytest.mark.parametrize('da_biet', [False, True])
def test_phan_vi_du_luot_3_hai_lop_khong_phat_hanh_ban_ro(loai, vi_tri, chu, ten_that, da_biet):
    seeds = SEEDS + ((ten_that, 'CONG_TY' if ten_that in ('Vinamilk', 'Techcombank')
                      else 'CA_NHAN', '[[MASK-B11-LUOT3]]'),) if da_biet else SEEDS
    b = bo(loai, raw=_tep_phan_vi_du(loai, chu, vi_tri), seeds=seeds, dang='tep')
    try:
        assert ten_that.encode('utf-8') in b''.join(_phan(b.raw).values())
        k = chay(b)
        if k['trang_thai'] == 'XONG':
            chuan_bi_het(b)
            giao(b)  # Local giả không tự bổ sung tên mà lớp 1 bỏ sót.
            k = chay(b)
        if k['trang_thai'] == 'XONG':
            ref = k['ket_qua']['truong']['tep_da_che']
            raw = b.c.doc_tep(ref['tep_id'])
            for ten_phan, du in _phan(raw).items():
                cay = ET.fromstring(du)
                # Oracle riêng: mọi ZIP part, cả text tách run và attribute;
                # bỏ dấu/Cf/dấu câu để không bỏ qua bản rõ đổi encoding.
                cac_chu = [du.decode('utf-8'), ''.join(cay.itertext())]
                cac_chu.extend(v for n in cay.iter() for v in n.attrib.values())
                for phan_ten in ten_that.split():
                    assert all(_chu_doc_lap(phan_ten) not in _chu_doc_lap(c)
                               for c in cac_chu), ten_phan
        else:
            assert k['trang_thai'] == 'LOI' and k['ket_qua'] is None
            assert k['loi']['ma'] in {'MASK_DINH_DANH_CHUA_DAT', 'MASK_TEP_CHUA_HO_TRO'}, k
            assert b.ram._ban_ghi is None and not b.cong.giao_cuoi
    finally:
        if b.ram._ban_ghi:
            b.ram._don(b.ram._ban_ghi)


@pytest.mark.parametrize('ham', [tw._kiem_vung, tx._kiem_vung])
@pytest.mark.parametrize('chu', [
    'DEMO - (123). &', 'TEST 42', 'SAMPLE\u00a0(2026)', 'DRAFT – 7.',
    'Tổng thu đã tổng hợp', 'Tổng chi đã đối chiếu: 3.754.200 VND.',
    'Tổng chi đã kiểm tra (2026-11-09).',
    'Tổng thu đã tổng hợp: 12 USD, 34 EUR, 56 đồng.',
    'Tổng thu đã kiểm tra ngày 9 tháng 11 năm 2026.',
])
def test_luot_3_cu_phap_dong_chi_so_tien_ngay_van_duoc_mien(ham, chu):
    b = bo_ram(seeds=())
    with b.ram.buoc(b.v) as buoc:
        assert ham(chu, (), buoc).da_che == chu
