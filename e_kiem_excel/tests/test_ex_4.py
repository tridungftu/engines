"""EX-4: đáp án DEMO, đối chiếu nguồn, số thập phân và cổng CoreGia."""

import ast
from decimal import Decimal
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
import unicodedata

import openpyxl
import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia

from e_kiem_excel.chay import app
from e_kiem_excel import doc_bang as db
from sinh_demo import bang_kl, sheet, workbook

TESTS = Path(__file__).resolve().parent


def chay(raw, tham_so=None, ten='bang-DEMO.xlsx'):
    core = CoreGia()
    tep = core.them_tep(ten, raw)
    k = core.chay_thu(app, 'excel.doc_bang@1', {'loai': 'tep', 'tep': tep}, tham_so or {})
    if k['trang_thai'] != 'XONG':
        return k, None
    truong = k['ket_qua']['truong']
    return truong, json.loads(core.doc_tep(truong['tep_json']['tep_id']))


def sua_demo(**cac_o):
    wb = openpyxl.load_workbook(BytesIO(bang_kl()), data_only=True)
    try:
        for o, v in cac_o.items():
            wb['BTH'][o] = v
        raw = BytesIO()
        wb.save(raw)
        return raw.getvalue()
    finally:
        wb.close()


def test_dap_an_demo(demo):
    raw = (demo/'bang-kl-DEMO.xlsx').read_bytes()
    t, j = chay(raw)
    dap = json.loads((demo/'dap-an.json').read_text(encoding='utf-8'))['bang-kl-DEMO.xlsx']
    for k, v in dap.items():
        assert t[k] == v
    assert t['gia_tri_hop_dong'] is None
    assert t['so_canh_bao'] == 0 and t['tien_te_chua_ro'] is False
    assert t['phien_ban_engine'] == 'e_kiem_excel 0.1.0'
    assert t['bam_dau_vao'] == j['bam_dau_vao'] == 'sha256:'+sha256(raw).hexdigest()
    assert j['phien_ban'] == 1 and j['khuon'] == 'xay_dung_klgt'
    assert j['cot'] == dict(ten='B', dg='H', stt='A', dvt='C',
                            kl_hd='D', kl_kt='E', kl_kn='F', kl_lk='G',
                            gt_hd='I', gt_kt='J', gt_kn='K', gt_lk='L')
    assert len(j['dong']) == 31 and j['dong'][0]['dvt'] == ''
    for n, d in enumerate(j['dong'][1:], 7):
        assert d == {
            'vi_tri': f'BTH!{n}', 'stt': str(n-6), 'nhom': 'Nhóm công tác DEMO',
            'ten': f'Công tác DEMO {n:02d} bê tông', 'dvt': 'm3',
            'khoa': f'nhom cong tac demo|cong tac demo {n:02d} be tong|m3',
            'kl_hd': '25', 'kl_kt': '2', 'kl_kn': '5', 'kl_lk': '7',
            'don_gia': {'so': '1000000', 'tien_te': 'VND'},
            **{k: {'so': v, 'tien_te': 'VND'} for k, v in
               [('gt_hd','25000000'),('gt_kt','2000000'),('gt_kn','5000000'),('gt_lk','7000000')]},
            'canh_bao': [],
        }
    assert j['tong_hop'] == {'tt_ky_nay': {
        'gia_tri': {'so': '60000000', 'tien_te': 'VND'},
        'o': 'BTH!J39', 'nhan': 'Giá trị đề nghị thanh toán kỳ này'}}


@pytest.fixture
def goc_decimal():
    # Chỉ chuyển kiểu số trong mã tham chiếu tại RAM; không sửa ma-nguon.
    p = TESTS.parent/'ma-nguon'/'master_hd.py'
    raw = p.read_bytes().replace(b'\r\n', b'\n')
    assert sha256(raw).hexdigest() == '7c82daf635be14153599fb65a1059100c71b0b19a8a057e781187023688ae124'
    source = raw.decode('utf-8')
    tree = ast.parse(source)
    ten = {'nfc','bo_dau','num','_hdr_text','tim_bang_chi_tiet','khoa','tim_so_tong_hop'}
    doan = '\n\n'.join(ast.get_source_segment(source, n) for n in tree.body
                       if isinstance(n, ast.FunctionDef) and n.name in ten)
    doan = doan.replace('float(str(v).replace(",", ""))', 'Decimal(str(v).replace(",", ""))')
    doan = doan.replace('return float(v)', 'return Decimal(str(v))')
    doan = doan.replace('), float)', '), Decimal)')
    doan = doan.replace('and abs(v) > 1', '')
    doan = doan.replace('gia_tri=float(v)', 'gia_tri=Decimal(str(v))')
    nhan = next(n for n in tree.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == 'LABELS' for t in n.targets))
    doan = ast.get_source_segment(source, nhan) + '\n' + doan
    ns = dict(Decimal=Decimal, re=re, unicodedata=unicodedata)
    exec(compile(doan, str(p), 'exec'), ns)
    return ns


@pytest.mark.parametrize('ten', ['bang-kl-DEMO.xlsx', 'K1-K8-DEMO.xlsx'])
def test_tuong_duong_goc_decimal(demo, goc_decimal, ten):
    wb = openpyxl.load_workbook(demo/ten, data_only=True)
    try:
        assert db.tim_bang_chi_tiet(wb) == goc_decimal['tim_bang_chi_tiet'](wb)
        assert db.tim_so_tong_hop(wb) == goc_decimal['tim_so_tong_hop'](wb)
    finally:
        wb.close()


def test_canh_bao_va_cong():
    raw = sua_demo(B8='Công tác DEMO 07 bê tông', H7='1000000', I7=1,
                   B38='Dòng DEMO sau Cộng', C38='m3', H38=5, D38=2, I38=10)
    t, j = chay(raw)
    assert t['so_dong'] == 30 and t['so_canh_bao'] == 3
    assert {(c['ma'], c['o']) for c in j['canh_bao']} == {
        ('SO_DANG_CHU', 'BTH!H7'), ('THANH_TIEN_LECH', 'BTH!I7'), ('TRUNG_KHOA', 'BTH!8')}
    assert j['dong'][1]['khoa']+'#2' == j['dong'][2]['khoa']
    assert all(d['vi_tri'] != 'BTH!38' for d in j['dong'])
    # Cống có đơn vị là hạng mục, không phải nhãn tổng cộng.
    t, j = chay(sua_demo(B7='Cống thoát nước DEMO'))
    assert t['so_dong'] == 30 and j['dong'][1]['ten'] == 'Cống thoát nước DEMO'


@pytest.mark.parametrize('ma', ['', 'USD', 'VND'])
def test_tien_te_chua_ro_va_tham_so(ma):
    raw = sua_demo(B2='Bảng khối lượng DEMO')
    t, j = chay(raw, {'tien_te': ma})
    assert t['tien_te_chua_ro'] == (ma == '')
    assert t['gia_tri_de_nghi'] == ({'so':'60000000', 'tien_te':ma} if ma else None)
    assert t['gia_tri_hop_dong'] is None
    assert j['tien_te'] == (ma or None)
    for d in j['dong'][1:]:
        for k in ('don_gia','gt_hd','gt_kt','gt_kn','gt_lk'):
            assert d[k]['tien_te'] == (ma or None)
            assert isinstance(d[k]['so'], str)


@pytest.mark.parametrize('ma', ['vnd', 'US1', ' VN', 'ĐỒN'])
def test_ma_tien_sai(ma):
    t, _ = chay(bang_kl(), {'tien_te':ma})
    assert t['trang_thai'] == 'LOI' and t['loi']['ma'] == 'THAM_SO_KHONG_HOP_LE'


def test_nhan_tien_te_file():
    t, j = chay(sua_demo(B2='Đơn vị tiền tệ: USD'))
    assert t['gia_tri_de_nghi']['tien_te'] == j['tien_te'] == 'USD'
    # Không suy ra từ tên công tác; hai đơn vị ghi rõ thì để chưa rõ.
    t, j = chay(sua_demo(B2='Đơn vị tiền VND / Đơn vị tiền USD'))
    assert t['tien_te_chua_ro'] and t['gia_tri_de_nghi'] is None
    t, j = chay(sua_demo(B2='Bảng DEMO', B7='Dịch vụ DEMO USD'))
    assert t['tien_te_chua_ro']


@pytest.mark.parametrize('so', ['2500000000.125', '-1000000000.25', '0', '0.5', '-1'])
def test_tong_tien_chinh_xac(so):
    # Ghi số trực tiếp trong XML để không bị workbook.save làm tròn qua float.
    raw = bang_kl()
    from zipfile import ZipFile
    from sinh_demo import zip_xml
    with ZipFile(BytesIO(raw)) as z:
        muc = {n:z.read(n) for n in z.namelist()}
    xml = muc['xl/worksheets/sheet1.xml'].decode()
    xml = xml.replace('<v>60000000</v>', '<v>'+so+'</v>')
    muc['xl/worksheets/sheet1.xml'] = xml.encode()
    raw = zip_xml(muc)
    t, j = chay(raw)
    assert t['gia_tri_de_nghi'] == {'so':so, 'tien_te':'VND'}
    assert j['tong_hop']['tt_ky_nay']['gia_tri'] == t['gia_tri_de_nghi']


def test_so_nguyen_vuot_float():
    so = '9007199254740993'
    # openpyxl.save có thể làm tròn số nguyên lớn; dùng OOXML trực tiếp.
    raw = workbook([('DEMO', sheet([
        ('A1','Công ty DEMO Ánh Dương'), ('A2','Đơn vị tiền VND'),
        ('A3','Tên công việc'), ('B3','Đơn vị'), ('C3','Khối lượng hợp đồng'),
        ('D3','Đơn giá'), ('E3','Giá trị hợp đồng'),
        ('A7','Công tác DEMO'), ('B7','m3'), ('C7',1), ('D7',int(so)), ('E7',int(so)),
        ('A8','Cộng'), ('A10','Giá trị đề nghị thanh toán kỳ này'), ('B10',int(so)),
    ]), 'visible')])
    t, j = chay(raw)
    assert j['dong'][0]['don_gia']['so'] == so
    assert t['gia_tri_de_nghi']['so'] == so
    assert str(Decimal(str(float(int(so))))) == '9007199254740992.0'


def test_num_goc_va_phep_nhan_decimal():
    assert db._num('1,234.25') == Decimal('1234.25')
    assert db._num('-0.1') == Decimal('-0.1')
    assert all(db._num(x) is None for x in (True, 'NaN', 'Infinity', 'abc'))
    t, j = chay(sua_demo(D7=0.1, H7=0.2, I7=0.02))
    assert not any(c['o']=='BTH!I7' for c in j['canh_bao'])
    assert 0.1 * 0.2 != 0.02


def test_khong_co_bang_va_tep_hong(demo):
    t, _ = chay((demo/'sach-DEMO.xlsx').read_bytes())
    assert t['loi']['ma'] == 'KHONG_TIM_THAY_BANG'
    # ZIP/XML hợp lệ nhưng cấu trúc workbook hỏng, không lộ exception.
    from sinh_demo import zip_xml
    t, _ = chay(zip_xml({'demo.xml':b'<DEMO/>'}))
    assert t['loi']['ma'] == 'TEP_HONG'
    assert not any(x in t['loi']['thong_diep'] for x in ('Traceback', 'site-packages', 'KeyError'))


def test_huy_va_tran_json(monkeypatch):
    def huy():
        raise RuntimeError('HUY_DEMO')
    with pytest.raises(RuntimeError, match='HUY_DEMO'):
        db.doc_klgt(bang_kl(), {}, 'e_kiem_excel 0.1.0', huy)
    monkeypatch.setattr(db, 'TEP_TOI_DA_BYTE', 64)
    with pytest.raises(LoiNghiepVu) as e:
        db.doc_klgt(bang_kl(), {}, 'e_kiem_excel 0.1.0')
    assert e.value.ma == 'VUOT_GIOI_HAN'


def test_tong_quat_de_ex5():
    t, _ = chay(bang_kl(), {'khuon':'tong_quat'})
    assert t['loi']['ma'] == 'CHUA_LAM'



def test_tong_hop_cac_nhan_va_sheet_an(goc_decimal):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'DEMO'
    nhan = ['Giá trị hợp đồng', 'Lũy kế thực hiện đến hết kỳ trước',
            'Giá trị thực hiện kỳ này', 'Lũy kế thực hiện đến hết kỳ này',
            'Giữ lại', 'Thu hồi tạm ứng', 'Giá trị đề nghị thanh toán kỳ này']
    for r, t in enumerate(nhan, 1):
        ws.cell(r, 1, t)
        ws.cell(r, 3, r*0.125)
    an = wb.create_sheet('An DEMO')
    an.sheet_state = 'hidden'
    an['A1'] = nhan[0]
    an['B1'] = 999
    try:
        tong = db.tim_so_tong_hop(wb)
        assert tong == goc_decimal['tim_so_tong_hop'](wb)
        assert list(tong) == list(db.LABELS)
        assert all(v['o'].startswith('DEMO!') for v in tong.values())
        assert tong['gt_hd']['gia_tri'] == Decimal('0.125')
    finally:
        wb.close()


def test_tong_hop_so_dang_chu():
    t, j = chay(sua_demo(J39='1,234.25', B41='Giá trị hợp đồng', C41='-2500000000.125'))
    assert t['gia_tri_de_nghi'] == {'so':'1234.25','tien_te':'VND'}
    assert t['gia_tri_hop_dong'] == {'so':'-2500000000.125','tien_te':'VND'}
    assert {(c['ma'],c['o']) for c in j['canh_bao']} == {
        ('SO_DANG_CHU','BTH!J39'), ('SO_DANG_CHU','BTH!C41')}


@pytest.mark.parametrize('fmt', ['#,##0.00 "USD"', '[$USD-409] #,##0.00'])
def test_tien_te_dinh_dang_o(fmt):
    wb = openpyxl.load_workbook(BytesIO(sua_demo(B2='Bảng khối lượng DEMO')), data_only=True)
    try:
        wb['BTH']['H7'].number_format = fmt
        raw = BytesIO()
        wb.save(raw)
        t, j = chay(raw.getvalue())
        assert not t['tien_te_chua_ro'] and j['tien_te'] == 'USD'
    finally:
        wb.close()


def test_khoa_nguyen_cong_thuc_va_trung_ba_lan(goc_decimal):
    it = {'nhom':' A / I  Đào đất ', 'ten':'  ĐẮP  nền\u0300 '+ 'x'*150, 'dvt':' M3 '}
    assert db.khoa(it) == goc_decimal['khoa'](it)
    assert len(db.khoa(it).split('|')[1]) == 120
    t, j = chay(sua_demo(B8='Công tác DEMO 07 bê tông', B9='Công tác DEMO 07 bê tông'))
    assert [d['khoa'] for d in j['dong'][1:4]] == [j['dong'][1]['khoa']+s for s in ('','#2','#3')]
    assert t['so_canh_bao'] == 2
