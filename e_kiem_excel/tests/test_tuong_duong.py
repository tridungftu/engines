"""So với mã gốc bất biến và kiểm hợp đồng EX-1 bằng CoreGia."""

from collections import Counter
from copy import deepcopy
from decimal import Decimal
import hashlib
from io import BytesIO
import json
from pathlib import Path
import re
from types import SimpleNamespace
from zipfile import ZipFile

import openpyxl
import pytest
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu, Viec, ViecDaHuy
from kho_tri_thuc_sdk.thu import CoreGia

from e_kiem_excel.chay import app
from e_kiem_excel.chuan_hoa import bo_dau, nfc, num, so, so_tien
from e_kiem_excel.kiem_tra import KiemTra, ma_hoa_json
from e_kiem_excel.so_do import SoDo
from sinh_demo import sheet, workbook, zip_xml

TESTS = Path(__file__).resolve().parent
SHA_NGUON = {
    'toan_ven.py': 'a97396de2be4cecfb060cd52689f4eec648f7904a7fd132089e10e3c897f6023',
    'master_hd.py': '7c82daf635be14153599fb65a1059100c71b0b19a8a057e781187023688ae124',
}


@pytest.fixture
def goc(monkeypatch):
    thu_muc = TESTS.parent / 'ma-nguon'
    for ten, bam in SHA_NGUON.items():
        # Chỉ chuẩn hóa checkout CRLF trong RAM; không ghi lại mã gốc.
        assert hashlib.sha256((thu_muc / ten).read_bytes().replace(b'\r\n', b'\n')).hexdigest() == bam
    monkeypatch.syspath_prepend(str(thu_muc))
    import toan_ven
    assert Path(toan_ven.__file__).resolve() == (thu_muc / 'toan_ven.py').resolve()
    return toan_ven


def chay(raw, tham_so=None):
    core = CoreGia()
    tep = core.them_tep('DEMO.xlsx', raw)
    kq = core.chay_thu(app, 'excel.toan_ven@1', {'loai': 'tep', 'tep': tep}, tham_so)
    assert kq['trang_thai'] == 'XONG', kq
    truong = kq['ket_qua']['truong']
    data = core.doc_tep(truong['tep_json']['tep_id'])
    assert truong['tep_json']['kich_thuoc'] == len(data)
    assert truong['tep_json']['mime'] == 'application/json'
    return truong, json.loads(data)


def chay_goc_1_6(kt):
    for ten in ('k1_tong_quan', 'k2_ban_do_cong_thuc', 'k3_lien_ket_dong',
                'k4_sheet_an', 'k5_so_dang_chu', 'k6_tham_so_nhung'):
        getattr(kt, ten)()


@pytest.mark.parametrize('ten', ['K1-K8-DEMO.xlsx', 'sach-DEMO.xlsx', 'thieu-v-DEMO.xlsx', 'bang-kl-DEMO.xlsx'])
def test_tuong_duong_k1_k6(goc, demo, ten):
    kt = goc.KiemTra(demo / ten)
    try:
        chay_goc_1_6(kt)
        truong, chi_tiet = chay((demo / ten).read_bytes())
        assert Counter((p['muc'], p['kt'], p['o']) for p in kt.ph) == Counter(
            (p['muc'], p['kiem'], p['o']) for p in chi_tiet['phat_hien'])
        dem = Counter(p['muc'] for p in kt.ph)
        assert [truong[k] for k in ('so_co_cao', 'so_co_trung_binh', 'so_kiem_soat')] == [
            dem['Cao'], dem['Trung bình'], dem['Kiểm soát']]
        assert truong['bam_dau_vao'] == 'sha256:' + hashlib.sha256((demo / ten).read_bytes()).hexdigest()
        assert truong['da_tinh_lai'] == (ten != 'thieu-v-DEMO.xlsx')
        assert truong['o_dich'] is None and truong['tep_bao_cao'] is None and truong['so_ngoai_nhom'] is None
        assert chi_tiet['k7_cay'] == chi_tiet['k8_nguon'] == []
        assert chi_tiet['bo_nhom'] is None and chi_tiet['canh_bao']
    finally:
        kt.sd.wb.close(); kt.sd.wv.close()


def test_lech_da_biet_voi_chay_day_du_goc(goc, demo):
    """Không sửa thuật toán cho khớp: bản gốc đủ K7 phát thêm K6 tại J21."""
    kt = goc.KiemTra(demo / 'K1-K8-DEMO.xlsx', o_dich='BTH!J39')
    try:
        kt.chay()
        _, data = chay((demo / 'K1-K8-DEMO.xlsx').read_bytes(), {'o_dich': 'BTH!J39'})
        cu = Counter((p['muc'], p['kt'], p['o']) for p in kt.ph if p['kt'] in {f'K{i}' for i in range(1, 7)})
        moi = Counter((p['muc'], p['kiem'], p['o']) for p in data['phat_hien'])
        assert cu - moi == Counter({('Trung bình', 'K6', 'BTH!J21'): 1})
        assert not moi - cu
        assert data['k6_hang_so'][0]['hang_so'] == '1.08'
        assert data['k6_hang_so'][0]['so_trong_cay'] == '0'
    finally:
        kt.sd.wb.close(); kt.sd.wv.close()


def test_k6_cung_cay_goc_va_bo_chu_hd(goc, demo):
    kt = goc.KiemTra(demo / 'K1-K8-DEMO.xlsx', o_dich='BTH!J39')
    sd = SoDo((demo / 'K1-K8-DEMO.xlsx').read_bytes())
    try:
        kt.chay()
        moi = KiemTra(sd, {}).chay(SimpleNamespace(kiem_huy=lambda: None))
        moi.kq['cay'] = kt.kq['cay']  # dữ liệu kiểm độc lập, không dựng K7 trong runtime EX-1
        moi.k6_tham_so_nhung()
        assert moi.kq['nhung'] == kt.kq['nhung']
        ph = [p for p in moi.ph if p['kt'] == 'K6']
        assert [(p['muc'], p['kt'], p['o']) for p in ph] == [('Trung bình', 'K6', 'BTH!J21')]
        assert all('HĐ' not in p['mo_ta'] and p['tai_lieu'] == '' for p in ph)
    finally:
        sd.dong(); kt.sd.wb.close(); kt.sd.wv.close()


def kiem_schema(v, schema, goc):
    """Bộ kiểm độc lập cho tập từ khóa schema này, chỉ dùng stdlib."""
    if '$ref' in schema:
        return kiem_schema(v, goc['$defs'][schema['$ref'].split('/')[-1]], goc)
    if 'anyOf' in schema:
        for nhanh in schema['anyOf']:
            try:
                kiem_schema(v, nhanh, goc)
                return
            except AssertionError:
                pass
        raise AssertionError('Không khớp nhánh schema.')
    if 'const' in schema:
        assert v == schema['const']
    if 'enum' in schema:
        assert v in schema['enum']
    if 'type' in schema:
        loai = schema['type'] if isinstance(schema['type'], list) else [schema['type']]
        assert any({'null': v is None, 'boolean': type(v) is bool, 'integer': type(v) is int,
                    'string': isinstance(v, str), 'object': isinstance(v, dict), 'array': isinstance(v, list)}[t] for t in loai)
    if isinstance(v, str) and 'pattern' in schema:
        assert re.search(schema['pattern'], v)
    if isinstance(v, dict):
        props = schema['properties']
        assert set(schema['required']) <= set(v)
        if schema.get('additionalProperties') is False:
            assert set(v) <= set(props)
        for k, value in v.items():
            kiem_schema(value, props[k], goc)
    if isinstance(v, list):
        assert len(v) >= schema.get('minItems', 0)
        assert len(v) <= schema.get('maxItems', len(v))
        for value in v:
            kiem_schema(value, schema['items'], goc)


@pytest.mark.parametrize('ten', ['K1-K8-DEMO.xlsx', 'sach-DEMO.xlsx', 'thieu-v-DEMO.xlsx', 'bang-kl-DEMO.xlsx'])
def test_json_schema_va_so_chuoi(demo, ten):
    _, data = chay((demo / ten).read_bytes())
    schema = json.loads((TESTS / 'schema/toan_ven.schema.json').read_text(encoding='utf-8'))
    kiem_schema(data, schema, schema)
    def khong_so(v):
        assert type(v) not in (int, float)
        if isinstance(v, dict):
            for k, x in v.items():
                if k != 'phien_ban':
                    khong_so(x)
        if isinstance(v, list):
            for x in v:
                khong_so(x)
    khong_so(data)
    hong = deepcopy(data); hong['k1_sheet'][0]['so_dong'] = 123
    with pytest.raises(AssertionError):
        kiem_schema(hong, schema, schema)
    hong = deepcopy(data); del hong['k1_sheet'][0]['sheet']
    with pytest.raises(AssertionError):
        kiem_schema(hong, schema, schema)


@pytest.mark.parametrize('d', [Decimal('2.5E+9'), Decimal('-1234567890.125'), Decimal('0.00125')])
def test_decimal_so_tien_qua_sdk(d):
    phieu = deepcopy(app.phieu)
    phieu['nang_luc'] = [phieu['nang_luc'][0]]
    phieu['nang_luc'][0]['truong_ra'] = [{'ma': 'tien_demo', 'ten': 'Tiền DEMO', 'kieu': 'so_tien'}]
    phieu['chay_thu_demo'] = []
    thu = Engine(phieu)
    @thu.nang_luc('excel.toan_ven@1')
    def tra(viec):
        return {'loai': 'truong', 'truong': {'tien_demo': so_tien(d, 'VND')}}
    core = CoreGia()
    tep = core.them_tep('DEMO.xlsx', b'DEMO')
    kq = core.chay_thu(thu, 'excel.toan_ven@1', {'loai': 'tep', 'tep': tep})
    assert kq['trang_thai'] == 'XONG'
    tien = kq['ket_qua']['truong']['tien_demo']
    assert tien == {'so': format(d, 'f'), 'tien_te': 'VND'}
    assert Decimal(tien['so']) == d and 'E' not in tien['so']
    assert so_tien(d, '') is None


def test_chuan_hoa_giu_quy_tac_nguon():
    assert bo_dau('ĐƠN  GIÁ') == 'don gia'
    assert nfc('a\u0301') == 'á'
    assert so('1.234.567.890') == Decimal('1234567890')
    assert so('-123,45') == Decimal('-123.45')
    assert num('1,234.125') == Decimal('1234.125')
    assert num(0) == Decimal(0) and num(0.1) == Decimal('0.1')
    assert all(num(x) is None for x in (None, '', 'DEMO', float('nan'), 'Infinity', True))
    with pytest.raises(LoiNghiepVu) as exc:
        so_tien(1, 'vnd')
    assert exc.value.ma == 'THAM_SO_KHONG_HOP_LE'


def test_tep_hong_sau_lop_chan_khong_lo_traceback(capsys):
    raw = workbook([('DEMO', sheet([('A1', 'Công ty DEMO Ánh Dương'), ('B2', 1)]), 'visible')])
    with ZipFile(BytesIO(raw)) as z:
        muc = {n: z.read(n) for n in z.namelist()}
    muc['xl/worksheets/sheet1.xml'] = muc['xl/worksheets/sheet1.xml'].replace(b'r="B2"', b'r="B2" s="LOI_DEMO"')
    core = CoreGia()
    tep = core.them_tep('DEMO.xlsx', zip_xml(muc))
    kq = core.chay_thu(app, 'excel.toan_ven@1', {'loai': 'tep', 'tep': tep})
    assert kq['trang_thai'] == 'LOI' and kq['loi']['ma'] == 'TEP_HONG'
    assert kq['ket_qua'] is None
    noi_dung = json.dumps(kq) + ''.join(capsys.readouterr())
    assert all(s not in noi_dung for s in ('Traceback', 'ValueError', 'LOI_DEMO', str(TESTS)))


@pytest.mark.parametrize('dang_dung', [True, False])
def test_lien_ket_chi_giu_ten_khong_mo_nguon(dang_dung):
    from openpyxl.workbook.external_link.external import ExternalBook, ExternalLink, ExternalSheetNames
    from openpyxl.packaging.relationship import Relationship
    wb = openpyxl.Workbook()
    wb.active.title = 'DEMO'
    wb.active['A1'] = 'Công ty DEMO Ánh Dương'
    wb.active['B2'] = '=[1]DEMO!A1' if dang_dung else '=1+1'
    lk = ExternalLink(externalBook=ExternalBook(sheetNames=ExternalSheetNames(sheetName=['DEMO']), id='rId1'))
    lk.file_link = Relationship(Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/externalLinkPath',
                               Target=r'file:///C:\thu-muc-DEMO\gia-DEMO.xlsx', TargetMode='External')
    wb._external_links = [lk]
    luong = BytesIO(); wb.save(luong); wb.close()
    raw = luong.getvalue()
    sd = SoDo(raw)
    try:
        assert sd.ngoai == {1: 'gia-DEMO.xlsx'}
        assert not hasattr(sd, 'path')
    finally:
        sd.dong()
    truong, chi_tiet = chay(raw)
    assert truong['co_lien_ket_ngoai'] is dang_dung
    assert chi_tiet['k1_lien_ket_ngoai'] == [{'stt': '1', 'ten_tep': 'gia-DEMO.xlsx', 'so_cong_thuc': '1' if dang_dung else '0'}]
    assert 'thu-muc-DEMO' not in json.dumps(chi_tiet)


def test_huy_giua_cac_kiem_va_dong_workbook(demo, monkeypatch):
    da_chay = []
    dong = []
    k1 = KiemTra.k1_tong_quan
    def sau_k1(self):
        k1(self); da_chay.append('K1')
    def kiem_huy(self):
        if da_chay:
            raise ViecDaHuy()
    dong_goc = SoDo.dong
    def dong_sd(self):
        dong.append(True); dong_goc(self)
    monkeypatch.setattr(KiemTra, 'k1_tong_quan', sau_k1)
    monkeypatch.setattr(KiemTra, 'k2_ban_do_cong_thuc', lambda self: pytest.fail('Không chạy K2 sau khi hủy.'))
    monkeypatch.setattr(Viec, 'kiem_huy', kiem_huy)
    monkeypatch.setattr(SoDo, 'dong', dong_sd)
    core = CoreGia()
    tep = core.them_tep('DEMO.xlsx', (demo / 'sach-DEMO.xlsx').read_bytes())
    kq = core.chay_thu(app, 'excel.toan_ven@1', {'loai': 'tep', 'tep': tep})
    assert kq['trang_thai'] == 'HUY' and kq['ket_qua'] is None
    assert da_chay == ['K1'] and dong == [True]


def test_tran_json_theo_bytes_khong_cat_ngam(monkeypatch):
    import e_kiem_excel.kiem_tra as kt
    data = {'DEMO': 'Tiếng Việt'}
    raw = ma_hoa_json(data)
    monkeypatch.setattr(kt, 'JSON_TOI_DA_BYTE', len(raw))
    assert ma_hoa_json(data) == raw
    monkeypatch.setattr(kt, 'JSON_TOI_DA_BYTE', len(raw) - 1)
    with pytest.raises(LoiNghiepVu) as exc:
        ma_hoa_json(data)
    assert exc.value.ma == 'VUOT_GIOI_HAN'


@pytest.mark.parametrize('cong_thuc', [
    '=A1+$B$2+SUM(C3:D9)', "='Tên DEMO'!$D7+[1]DEMO!A2",
    '=IF(A1="B2",C3*1.08,D4*60%)', '=ROUND((A5+B6)*0.15,2)',
    "='Tên ''DEMO'!E1:E3", '=SUM(A1:A3)+SUBTOTAL(9,B2:B4)',
])
def test_ham_tham_chieu_giu_nguyen_thuat_toan(goc, cong_thuc):
    from e_kiem_excel import tham_chieu as tc
    assert tc.bo_chuoi(cong_thuc) == goc.bo_chuoi(cong_thuc)
    assert tc.tach_tham_chieu(cong_thuc, 'DEMO') == goc.tach_tham_chieu(cong_thuc, 'DEMO')
    assert tc.mau_cong_thuc(cong_thuc, 5, 3) == goc.mau_cong_thuc(cong_thuc, 5, 3)
    assert tc.hang_so_nhung(cong_thuc) == goc.hang_so_nhung(cong_thuc)
    assert tc.la_tong(cong_thuc) == goc.la_tong(cong_thuc)


def test_kiem_doc_lap_cho_regex_nhung_chan_chay_ma(tmp_path):
    from kiem_doc_lap import kiem_doc_lap
    tep = tmp_path / 'DEMO.py'
    tep.write_text('import re\nre.compile("DEMO")\n', encoding='utf-8')
    assert kiem_doc_lap(tmp_path) == []
    tep.write_text('compile("DEMO", "DEMO", "exec")\n', encoding='utf-8')
    assert kiem_doc_lap(tmp_path)
