"""EX-2: đối chiếu cây nguồn bất biến, Phụ lục A và hợp đồng CoreGia."""

from collections import Counter
from copy import deepcopy
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu, ViecDaHuy
from kho_tri_thuc_sdk.thu import CoreGia

from e_kiem_excel.bo_nhom import doc_bo_nhom, khop_tu_khoa, NGOAI_NHOM
from e_kiem_excel.chay import app
from e_kiem_excel.kiem_tra import KiemTra
from e_kiem_excel.so_do import SoDo
from sinh_demo import sheet, workbook
from test_tuong_duong import chay, goc, kiem_schema

TESTS = Path(__file__).resolve().parent
BO = (TESTS / 'demo/bo_nhom_review_ttkl.json').read_text(encoding='utf-8')
VIEC = SimpleNamespace(kiem_huy=lambda: None)


def tham_so(**them):
    return dict(bo_nhom_json=BO, **them)


def tao_demo(cells, ten='DEMO'):
    return workbook([(ten, sheet([('A1', 'Công ty DEMO Ánh Dương')] + cells), 'visible')])


def ket_qua_loi(raw, ts):
    core = CoreGia()
    tep = core.them_tep('DEMO.xlsx', raw)
    kq = core.chay_thu(app, 'excel.toan_ven@1', {'loai': 'tep', 'tep': tep}, ts)
    assert kq['trang_thai'] == 'LOI', kq
    assert kq['ket_qua'] is None
    return kq['loi']['ma']


@pytest.mark.parametrize('ten,dich', [('K1-K8-DEMO.xlsx', 'BTH!J39'), ('bang-kl-DEMO.xlsx', 'BTH!J39'),
                                    ('sach-DEMO.xlsx', 'DEMO!B3'), ('thieu-v-DEMO.xlsx', 'DEMO!B3')])
def test_toan_bo_cay_va_la_khop_nguon(goc, demo, ten, dich):
    cu = goc.KiemTra(demo / ten, o_dich=dich).chay()
    sd = SoDo((demo / ten).read_bytes())
    try:
        moi = KiemTra(sd, tham_so(o_dich=dich)).chay(VIEC)
        def chuan(rows):
            return [[Decimal(str(x)) if i == 4 and type(x) in (int, float, Decimal) else
                     (NGOAI_NHOM if i == 6 and str(x).startswith('Ngoài 7 nhóm') else x)
                     for i, x in enumerate(row)] for row in rows]
        assert chuan(moi.kq['cay']) == chuan(cu.kq['cay'])
        # So đủ mức/mã/ô K1–K7 với bản gốc chạy đủ K8; K8 thuộc EX-3.
        assert Counter((p['muc'], p['kt'], p['o']) for p in moi.ph) == Counter(
            (p['muc'], p['kt'], p['o']) for p in cu.ph if p['kt'] != 'K8')
        assert moi.kq['nhung'] == cu.kq['nhung']
        truong, data = chay((demo / ten).read_bytes(), tham_so(o_dich=dich))
        assert len(data['k7_cay']) == len(cu.kq['cay'])
        assert truong['so_ngoai_nhom'] == sum(r[6] == NGOAI_NHOM for r in moi.kq['cay'])
        assert data['bo_nhom'] == doc_bo_nhom(BO).tham_chieu
        schema = json.loads((TESTS / 'schema/toan_ven.schema.json').read_text(encoding='utf-8'))
        kiem_schema(data, schema, schema)
    finally:
        sd.dong(); cu.sd.wb.close(); cu.sd.wv.close()


def test_fixture_dung_nguyen_phu_luc_a_va_khong_vao_goi():
    phieu = (TESTS.parent / 'docs/PHIEU-ENGINE-e_kiem_excel.md').read_text(encoding='utf-8')
    a = phieu.split('## Phụ lục A —')[1].split('```json\n')[1].split('```')[0]
    assert json.loads(BO) == json.loads(a)
    assert not list((TESTS.parent / 'goi').rglob('bo_nhom_review_ttkl.json'))
    assert [n['ma'] for n in json.loads(BO)['nhom']] == ['2', '3-4', '1', '7', '5', '6', '1-2', '5b']


@pytest.mark.parametrize('td,nhan,sh', [
    ('Đơn giá', '', ''), ('KL HĐ', '', ''), ('Kỳ trước', '', ''), ('Kỳ này', '', ''),
    ('', 'Tạm ứng đợt 12', ''), ('', 'Thuế suất', ''), ('', 'Giá trị hợp đồng', ''),
    ('Diễn giải', '', ''), ('', '', 'Báo cáo DEMO'), ('', '', 'DEMO'),
])
def test_phan_nhom_tung_truong_hop_goc(goc, td, nhan, sh):
    n = doc_bo_nhom(BO).tim(td, nhan, sh)
    cu = goc.nhom_goc(td, nhan, sh)
    assert (n['ten'] if n else NGOAI_NHOM) == (NGOAI_NHOM if cu.startswith('Ngoài') else cu)


def test_do_rieng_hai_truong_hop_phu_luc_a(goc):
    bo = doc_bo_nhom(BO)
    # Nhóm 6: gốc bỏ qua 'gia tri' ở nhãn dòng; Phụ lục xét cả nhãn dòng.
    mau = [('', 'Giá trị thuế DEMO'), ('VAT', 'Giá trị DEMO'), ('GTGT', 'Giá trị DEMO')]
    lech = [(td, nhan, goc.nhom_goc(td, nhan), bo.tim(td, nhan)) for td, nhan in mau]
    assert len(lech) == 3
    assert all(cu == '6 Tham số HĐ' and moi is None for _, _, cu, moi in lech)
    # dai|rong|cao: hành vi chứa chuỗi vẫn khớp, kể cả từ không chỉ kích thước.
    mau = ['Báo cáo DEMO', 'Trong DEMO', 'Đại diện DEMO']
    assert all(bo.tim(td)['ten'] == goc.nhom_goc(td) == '5 KL / diễn giải' for td in mau)
    # Đo bằng lá K7 thật, không chỉ gọi matcher.
    for td, nhan in [('VAT', 'Giá trị DEMO'), ('Báo cáo DEMO', 'Công việc DEMO')]:
        raw = tao_demo([('B3', 'Tên công việc'), ('C3', td), ('B7', nhan), ('C7', 1000000)])
        _, data = chay(raw, tham_so(o_dich='DEMO!C7'))
        assert data['k7_cay'][0]['nhom'] == (NGOAI_NHOM if td == 'VAT' else '5 KL / diễn giải')


@pytest.mark.parametrize('tu,chuoi,dat', [
    ('gia', 'đơn giá', True), ('=hd', 'KL HĐ', True), ('=hd', 'PLHD', False),
    ('=thuế', 'thuế, DEMO', True), ('dot #', 'đợt 123', True), ('dot #', 'đợt', False),
    ('=dot #', 'đợt 123a', False), ('=dot #', 'đợt 123', True),
    ('a.*', 'abc', False), ('(a+)+$', 'aaaa', False), ('dai|rong|cao', 'dài', False),
    ('#', '١٢٣', True), ('GIA  TRI', 'giá\ttrị', True), (' =hd ', 'KL HĐ', True),
])
def test_tu_khoa_khong_thuc_thi_regex(tu, chuoi, dat):
    assert khop_tu_khoa(tu, chuoi) is dat


def test_nhieu_dau_thang_khong_backtracking():
    assert not khop_tu_khoa('#1' * 30 + 'x', '1' * 300)
    assert khop_tu_khoa('đợt ###', 'đợt 123')
    assert not khop_tu_khoa('đợt ###', 'đợt 1')


def test_dieu_kien_va_thu_tu():
    d = json.loads(BO)
    assert doc_bo_nhom(BO).tim('Đơn giá KL HĐ', 'Kỳ trước')['ma'] == '2'
    assert doc_bo_nhom(BO).tim('KL', '', 'HĐ')['ma'] == '1'
    assert doc_bo_nhom(BO).tim('HĐ') is None
    d['nhom'][0]['khi'].append({'vung': ['nhan_dong'], 'tat_ca': [['=demo']]})
    assert doc_bo_nhom(json.dumps(d)).tim('', 'DEMO')['ma'] == '2'


def test_tran_30_nhom_200_tu_khoa_32kib():
    d = json.loads(BO)
    n = d['nhom'][0]
    d['nhom'] = [dict(deepcopy(n), ma=str(i), ten=f'Nhóm {i}') for i in range(30)]
    assert doc_bo_nhom(json.dumps(d))
    d['nhom'].append(dict(deepcopy(n), ma='31', ten='Nhóm 31'))
    with pytest.raises(LoiNghiepVu):
        doc_bo_nhom(json.dumps(d))
    d['nhom'] = [deepcopy(n)]
    d['nhom'][0]['khi'][0]['tat_ca'] = [[str(i) for i in range(200)]]
    assert doc_bo_nhom(json.dumps(d))
    d['nhom'][0]['khi'][0]['khong_co'] = ['201']
    with pytest.raises(LoiNghiepVu):
        doc_bo_nhom(json.dumps(d))
    d['nhom'] = [deepcopy(n)]
    s = json.dumps(d, ensure_ascii=False)
    # Đúng byte, không phải ký tự: khoảng trắng JSON hợp lệ ở cuối.
    assert doc_bo_nhom(s + ' ' * (32768 - len(s.encode('utf-8'))))
    for s in (s + ' ' * (32769 - len(s.encode('utf-8'))), s.replace('Đơn giá', 'Đ' * 20000)):
        with pytest.raises(LoiNghiepVu) as e:
            doc_bo_nhom(s)
        assert e.value.ma == 'THAM_SO_KHONG_HOP_LE'


@pytest.mark.parametrize('s', ['null', '[]', 'true', '{', '{"a":1,"a":2}', '{"a":NaN}',
    BO.replace('"phien_ban": 1', '"phien_ban": true'),
    BO.replace('"tieu_de_cot"', '"regex"'), BO.replace('"don gia"', '"="'),
    BO.replace('[\n              "don gia"\n            ]', '[]'),
    BO.replace('"tat_ca":', '"regex":'), BO.replace('"don gia"', 'null'),
])
def test_sai_bo_nhom_qua_core(s, demo):
    assert ket_qua_loi((demo / 'sach-DEMO.xlsx').read_bytes(), {'bo_nhom_json': s}) == 'THAM_SO_KHONG_HOP_LE'


@pytest.mark.parametrize('dich', ['DEMO', 'DEMO!A0', 'DEMO!A1abc', 'DEMO!A1:B2', 'DEMO!A1!B2',
    'DEMO!XFE1', 'DEMO!A1048577', 'DEMO!A01', 'Khong co!A1', "'DEMO!A1", 'DEMO!1A', 'DEMO!A-1'])
def test_o_dich_sai_qua_core(demo, dich):
    assert ket_qua_loi((demo / 'sach-DEMO.xlsx').read_bytes(), {'o_dich': dich}) == 'THAM_SO_KHONG_HOP_LE'


def test_o_dich_uu_tien_nhan_khong_co_nhan_va_khong_bo_nhom(demo):
    raw = (demo / 'K1-K8-DEMO.xlsx').read_bytes()
    tr, data = chay(raw, {'o_dich': 'BTH!O1', 'nhan_o_dich_json': '["gia tri de nghi"]'})
    assert tr['o_dich'] == data['o_dich'] == 'BTH!O1'
    assert tr['so_ngoai_nhom'] is None and data['bo_nhom'] is None
    assert [r['nhom'] for r in data['k7_cay'] if r['la']] == ['Chưa phân nhóm']
    assert not [p for p in data['phat_hien'] if p['kiem'] == 'K7']
    tr, data = chay(raw, {'nhan_o_dich_json': '["GIÁ TRỊ  ĐỀ NGHỊ THANH TOÁN KỲ NÀY"]'})
    assert tr['o_dich'] == 'BTH!J39' and data['k7_cay']
    assert all(r['nhom'] == 'Chưa phân nhóm' for r in data['k7_cay'] if r['la'])
    for ts in ({}, {'nhan_o_dich_json': '["khong co DEMO"]'}):
        tr, data = chay(raw, ts)
        assert tr['o_dich'] is None and not data['k7_cay']
        k7 = [p for p in data['phat_hien'] if p['kiem'] == 'K7']
        assert len(k7) == 1 and k7[0]['muc'] == 'Kiểm soát'


@pytest.mark.parametrize('s', ['null', '{}', '[]', '[1]', '[""]', '["="]', '[NaN]', '[' * 1500])
def test_nhan_sai(s, demo):
    assert ket_qua_loi((demo / 'sach-DEMO.xlsx').read_bytes(), {'nhan_o_dich_json': s}) == 'THAM_SO_KHONG_HOP_LE'


def test_nhan_so_khong_bo_nguong_va_sheet_co_nhay():
    for v in (0, -1, Decimal('0.125'), 9007199254740993):
        raw = tao_demo([('B7', 'Chỉ tiêu DEMO'), ('C7', v)], "Bảng ' DEMO")
        tr, data = chay(raw, {'nhan_o_dich_json': '["chi tieu demo"]'})
        assert tr['o_dich'] == "Bảng ' DEMO!C7"
        assert data['k7_cay'][0]['gia_tri'] == format(Decimal(str(v)), 'f')
        tr, _ = chay(raw, {'o_dich': "'Bảng '' DEMO'!$c$7"})
        assert tr['o_dich'] == "Bảng ' DEMO!C7"


def test_decimal_dai_chu_trong_va_tham_chieu_lap():
    raw = tao_demo([('B3', 'Tên công việc'), ('C3', 'Khối lượng'), ('C7', Decimal('0.1')),
                    ('C8', Decimal('0.2')), ('C9', Decimal('-1000000000.125')),
                    ('C10', Decimal('-999999999.825'), 'SUM(C7:C9)'), ('D7', 'DEMO'),
                    ('D10', 1, 'C10+C10+D7+E7')])
    _, data = chay(raw, tham_so(o_dich='DEMO!D10'))
    rows = data['k7_cay']
    tong = next(r for r in rows if r['loai'] == 'Nhóm nhập tay')
    assert tong['gia_tri'] == '-999999999.825'
    assert {'Đã phân rã', 'Chữ', 'Trống'} <= {r['loai'] for r in rows}


def test_vuot_do_sau_khong_cat_ngam_va_huy_trong_k7():
    raw = tao_demo([('B3', 'Tên công việc')] + [('C'+str(i), i, 'C'+str(i+1)) for i in range(7, 24)] + [('C24', 1)])
    assert ket_qua_loi(raw, {'o_dich': 'DEMO!C7'}) == 'VUOT_GIOI_HAN'
    sd = SoDo(raw)
    kt = KiemTra(sd, {'o_dich': 'DEMO!C7'})
    def huy():
        raise ViecDaHuy()
    kt._kiem_huy = huy
    try:
        with pytest.raises(ViecDaHuy):
            kt.k7_cay_truy_vet()
    finally:
        sd.dong()


def test_ham_bo_nhom_tham_chieu_bam_on_dinh():
    d = json.loads(BO)
    bo = doc_bo_nhom(BO)
    assert bo.tham_chieu == doc_bo_nhom(json.dumps(d, ensure_ascii=False)).tham_chieu
    raw = json.dumps(d, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    assert bo.tham_chieu['bam'] == 'sha256:' + sha256(raw).hexdigest()


def test_k7_file_ngoai_va_ha_muc_cot_phu(goc, tmp_path):
    import openpyxl
    from io import BytesIO
    from openpyxl.workbook.external_link.external import ExternalBook, ExternalLink, ExternalSheetNames
    from openpyxl.packaging.relationship import Relationship
    wb = openpyxl.Workbook()
    wb.active.title = 'DEMO'
    wb.active['A1'] = 'Công ty DEMO Ánh Dương'
    wb.active['C7'] = '=[1]DEMO!A7'
    wb.active['D7'] = 1000000
    lk = ExternalLink(externalBook=ExternalBook(sheetNames=ExternalSheetNames(sheetName=['DEMO']), id='rId1'))
    lk.file_link = Relationship(Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/externalLinkPath',
                               Target='file:///thu-muc-DEMO/nguon-DEMO.xlsx', TargetMode='External')
    wb._external_links = [lk]
    out = BytesIO(); wb.save(out); wb.close()
    raw = out.getvalue()
    p = tmp_path / 'DEMO.xlsx'; p.write_bytes(raw)
    for dich, muc in [('DEMO!C7', 'Cao'), ('DEMO!D7', 'Trung bình')]:
        cu = goc.KiemTra(p, o_dich=dich).chay()
        try:
            _, data = chay(raw, tham_so(o_dich=dich))
            assert Counter((p['muc'], p['kiem'], p['o']) for p in data['phat_hien']) == Counter(
                (p['muc'], p['kt'], p['o']) for p in cu.ph if p['kt'] != 'K8')
            assert next(p['muc'] for p in data['phat_hien'] if p['kiem'] == 'K1' and p['o'] == '[1]') == muc
            assert 'thu-muc-DEMO' not in json.dumps(data)
        finally:
            cu.sd.wb.close(); cu.sd.wv.close()


def test_k7_chu_trinh_va_sheet_khong_co():
    raw = tao_demo([('C7', 1, 'C8'), ('C8', 1, 'C7'), ('D7', 1, "'Khong co'!C7")])
    _, data = chay(raw, {'o_dich': 'DEMO!C7'})
    assert [r['loai'] for r in data['k7_cay']] == ['Công thức', 'Công thức', 'Đã phân rã']
    _, data = chay(raw, {'o_dich': 'DEMO!D7'})
    assert data['k7_cay'][-1]['loai'] == 'Lỗi tham chiếu'


def test_tran_dai_va_mau_khong_cat_ngam():
    raw = tao_demo([('C7', 1, 'SUM(D1:D250001)')])
    assert ket_qua_loi(raw, {'o_dich': 'DEMO!C7'}) == 'VUOT_GIOI_HAN'
    raw = tao_demo([('B3', 'Tên công việc'), ('C7', 1, 'SUM(D7:D19)')]
                   + [('D'+str(i), 1, f'E{i}*{i}') for i in range(7, 20)])
    assert ket_qua_loi(raw, {'o_dich': 'DEMO!C7'}) == 'VUOT_GIOI_HAN'


def test_tong_decimal_khong_lam_tron_28_chu_so():
    v = 10**30
    raw = tao_demo([('C7', 0, 'SUM(D7:D9)'), ('D7', v), ('D8', 1), ('D9', -v)])
    _, data = chay(raw, {'o_dich': 'DEMO!C7'})
    assert next(r['gia_tri'] for r in data['k7_cay'] if r['loai'] == 'Nhóm nhập tay') == '1'
