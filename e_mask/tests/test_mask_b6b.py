"""MASK-B6b: số Excel DEMO, đã kiểm bằng Core giả (CoreGia)."""
from types import SimpleNamespace
from xml.etree import ElementTree as ET

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu

from e_mask import tep_excel as tx, tai_nguyen
from e_mask.doc_excel import doc_excel
from ho_tro_mask_b1 import excel_demo, them_phan, CT_S, S
from ho_tro_mask_b3 import STYLES, goi_office
from ho_tro_mask_b6 import bo


def excel_so(gia_tri, fmt, code=None, *, epoch1904=False, ke_thua=None):
    ET.register_namespace('', S)
    style = '' if ke_thua else ' s="1"'
    hang = ' s="1" customFormat="1"' if ke_thua == 'hang' else ''
    p = excel_demo(noi_dung=f'<row r="1"{hang}><c r="A1"{style} t="n"><v>{gia_tri}</v></c></row>')
    p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('DEMO 1', 'bảng')
    if epoch1904:
        p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('<sheets>', '<workbookPr date1904="1"/><sheets>')
    if ke_thua == 'cot':
        p['xl/worksheets/sheet1.xml'] = p['xl/worksheets/sheet1.xml'].replace(
            '<sheetData>', '<cols><col min="1" max="1" style="1"/></cols><sheetData>')
    root = ET.fromstring(STYLES)
    num = root.find(f'{{{S}}}numFmts')
    num.clear()
    num.set('count', str(int(code is not None)))
    if code is not None:
        ET.SubElement(num, f'{{{S}}}numFmt', numFmtId=str(fmt), formatCode=code)
    xfs = root.find(f'{{{S}}}cellXfs')
    xfs.remove(xfs[2])
    xfs.set('count', '2')
    xfs[1].set('numFmtId', str(fmt))
    them_phan(p, 'xl/styles.xml', ET.tostring(root, encoding='unicode'),
              CT_S + 'styles+xml', 'styles', rid='rId10', chu='xl/workbook.xml')
    return goi_office(p)


def chan(raw):
    b = bo()
    with pytest.raises(LoiNghiepVu) as exc:
        with b.ram.buoc(b.v) as buoc:
            tx.che_excel(raw, buoc=buoc)
    assert exc.value.ma == 'MASK_TEP_CHUA_HO_TRO'
    assert '123456789012' not in str(exc.value)
    assert b.ram._ban_ghi is None and not b.c._tep


@pytest.mark.parametrize('fmt', [0, 14, 22, 45, 46, 47])
@pytest.mark.parametrize('gia_tri', ['123456789012', '123456789', '1000000000',
                                  '1.23456789012e11', '123456789012.0'])
def test_dinh_dang_san_khong_mien_so_dinh_danh(fmt, gia_tri):
    chan(excel_so(gia_tri, fmt))


@pytest.mark.parametrize('code', ['0', 'dd/mm/yyyy', 'yyyy-mm-dd hh:mm:ss', 'hh:mm'])
def test_format_rieng_khong_mien_so_dinh_danh(code):
    chan(excel_so('123456789012', 164, code))


@pytest.mark.parametrize('fmt', [*range(5, 9), 14, 22, *range(41, 48)])
def test_khai_bao_lai_id_san_da_bi_reader_chan(fmt):
    # B3 chặn numFmt khai lại ID <164 từ trước: không nới profile để nhận nó.
    chan(excel_so('123456789012', fmt, '0'))


@pytest.mark.parametrize('fmt,code,gia_tri', [
    *[(f, None, v) for f in [*range(5, 9), *range(41, 45)]
      for v in ['1500000', '1234567.89', '1000000000', '123456789012', '999999999999',
                '-123456789012', '123456789012.00', '1.23456789012e11',
                '123456789012.89', '1234567890123456.01']],
    *[(164, f, v) for f in ['#,##0" VND"', '#,##0.00" VND"', '#,##0 [$VND-42A]']
      for v in ['1500000', '1500000.00', '1234567.89', '-1234567.89',
                '1000000000', '123456789012', '-999999999', '1e11',
                '123456789.12', '123456789012.89']],
    *[(f, None, '46325.5') for f in [*range(14, 23), 45, 46, 47]],
    (14, None, '46325'), (164, 'dd/mm/yyyy', '46325'), (164, 'yyyy-mm-dd', '46325.5'),
])
@pytest.mark.parametrize('epoch1904', [False, True])
def test_tien_ngay_that_giu_so_format_va_bytes(fmt, code, gia_tri, epoch1904):
    raw = excel_so(gia_tri, fmt, code, epoch1904=epoch1904)
    b = bo()
    with b.ram.buoc(b.v) as buoc:
        tx.che_excel(raw, buoc=buoc)
        s = buoc.du_lieu['tep_excel']
        sau = doc_excel(s['da_che'], kiem_huy=buoc.kiem)
        assert s['da_che'] == raw
        assert sau.o[0].gia_tri == gia_tri
        assert sau.o[0].xml_goc == s['tai_lieu'].o[0].xml_goc
        assert sau.styles == s['tai_lieu'].styles
        assert sau.epoch1904 is epoch1904
    assert b.ram._ban_ghi is None and not b.c._tep


@pytest.mark.parametrize('gia_tri', ['-1', '0', '73416', '1234567.89', '1e300'])
@pytest.mark.parametrize('fmt,code', [(14, None), (22, None), (164, 'dd/mm/yyyy'), (46, None)])
def test_ngay_ngoai_mien_chan_ca_khi_detector_khong_bao(gia_tri, fmt, code):
    chan(excel_so(gia_tri, fmt, code))


@pytest.mark.parametrize('ke_thua', ['hang', 'cot'])
@pytest.mark.parametrize('fmt,code', [(7, None), (14, None), (164, 'dd/mm/yyyy')])
def test_style_hieu_luc_ke_thua_van_kiem_so(ke_thua, fmt, code):
    chan(excel_so('1234567890123', fmt, code, ke_thua=ke_thua))


@pytest.mark.parametrize('fmt,code', [*[(f, None) for f in [*range(5, 9), *range(41, 45)]],
    (164, '#,##0" VND"'), (164, '#,##0.00" VND"'), (164, '#,##0 [$VND-42A]')])
@pytest.mark.parametrize('gia_tri', ['1234567890123', '1000000000000', '1234567890123456',
                                  '-1234567890123', '1234567890123.00', '1.234567890123e12'])
def test_tien_nguyen_tu_13_chu_so_nghi_dinh_danh_bi_chan(fmt, code, gia_tri):
    chan(excel_so(gia_tri, fmt, code))


def test_tien_bieu_dien_cuc_doan_van_chan():
    chan(excel_so('1e-999999', 164, '#,##0.00" VND"'))


@pytest.mark.parametrize('nguon', ['ds', 'ngan'])
@pytest.mark.parametrize('fmt,code,gia_tri', [(0, None, '123456789012'),
    (7, None, '123456789012'), (164, '#,##0" VND"', '123456789012'),
    (14, None, '123456789012'), (14, None, '46325'), (7, None, '123456789.12')])
def test_dinh_danh_da_khai_van_chan_bat_ke_format(nguon, fmt, code, gia_tri):
    b = bo(seeds=((gia_tri, 'KHAC', '[[MASKKHAC-0001]]'),) if nguon == 'ngan' else ())
    ds = [dict(gia_tri=gia_tri, nhom='KHAC')] if nguon == 'ds' else []
    with pytest.raises(LoiNghiepVu):
        with b.ram.buoc(b.v) as buoc:
            tx.che_excel(excel_so(gia_tri, fmt, code), buoc=buoc, dinh_danh=ds)
    assert b.ram._ban_ghi is None and not b.c._tep


@pytest.mark.parametrize('gia_tri', ['123456789012.00', '1.23456789012e11', '-123456789012'])
def test_tien_bieu_dien_khac_khong_ne_dinh_danh_ngan(gia_tri):
    b = bo(seeds=(('123456789012', 'KHAC', '[[MASKKHAC-0001]]'),))
    with pytest.raises(LoiNghiepVu) as exc:
        with b.ram.buoc(b.v) as buoc:
            tx.che_excel(excel_so(gia_tri, 7), buoc=buoc)
    assert exc.value.ma == 'MASK_TEP_CHUA_HO_TRO'
    assert b.ram._ban_ghi is None and not b.c._tep


@pytest.mark.parametrize('epoch1904,gia_tri,dat', [
    (False, '1', True), (False, '0.999', False),
    (False, '73415.999', True), (False, '73416', False),
    (True, '0', True), (True, '-0.001', False),
    (True, '71953.999', True), (True, '71954', False),
])
def test_bien_lich_1900_2100_theo_epoch(epoch1904, gia_tri, dat):
    raw = excel_so(gia_tri, 164, 'dd/mm/yyyy hh:mm', epoch1904=epoch1904)
    if not dat:
        chan(raw)
        return
    b = bo()
    with b.ram.buoc(b.v) as buoc:
        tx.che_excel(raw, buoc=buoc)
        assert buoc.du_lieu['tep_excel']['da_che'] == raw


def test_format_code_hieu_luc_thang_id_va_khong_mien_detector(monkeypatch):
    tai_nguyen.nap_tu_goi()
    # Reader hiện chặn khai lại builtin. Kiểm thêm gate nội bộ để không tái
    # sinh bypass nếu reader sau này mở profile cho khai lại styles.
    o = SimpleNamespace(vung=None, gia_tri='1234567.89', kieu='n', style_hieu_luc=0)
    tai_lieu = SimpleNamespace(o=[o], styles=[{'numFmtId': '7', 'formatCode': '0'}],
                              epoch1904=False, goi=SimpleNamespace(goi=SimpleNamespace(cay={})))
    buoc = SimpleNamespace(kiem=lambda: None)
    with pytest.raises(LoiNghiepVu):
        tx._kiem_so_bat_bien(tai_lieu, buoc)
    tai_lieu.styles[0] = {'numFmtId': '14', 'formatCode': '0'}
    o.gia_tri = '73051'
    tx._kiem_so_bat_bien(tai_lieu, buoc)  # 0 là số thường, không phải ngày lỗi.
    tai_lieu.styles[0] = {'numFmtId': '7', 'formatCode': '0'}
    o.gia_tri = '1234567.89'
    goi = []
    def chua_quet_het(chu, ds):
        goi.append(chu)
        return [], False
    monkeypatch.setattr(tx.che, '_kiem_con_sot', chua_quet_het)
    with pytest.raises(LoiNghiepVu):
        tx._kiem_so_bat_bien(tai_lieu, buoc)
    assert goi
