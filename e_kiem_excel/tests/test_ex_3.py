"""EX-3: K8 đối chiếu mã gốc và báo cáo thật qua CoreGia."""

from collections import Counter
from decimal import Decimal
from io import BytesIO
import json
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile

import openpyxl
import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu, ViecDaHuy
from kho_tri_thuc_sdk.thu import CoreGia

from e_kiem_excel.bao_cao import ghi, _sheet
from e_kiem_excel.chay import app
from e_kiem_excel.kiem_tra import KiemTra
from e_kiem_excel.so_do import SoDo
from sinh_demo import NHAN, sheet, workbook, zip_xml
from test_tuong_duong import goc, kiem_schema

TESTS = Path(__file__).resolve().parent
VIEC = SimpleNamespace(kiem_huy=lambda: None)
SHEETS = ['Phat hien', 'K1 Tong quan', 'K1 File ngoai', 'K2 Mau cot', 'K2 Lech mau',
          'K2 Go tay', 'K3 Lien ket dong', 'K4 Sheet an', 'K4 Khac ban hien',
          'K5 So dang chu', 'K6 Hang so', 'K7 Cay truy vet', 'K8 Nguon KL',
          'K8 Tung dong', 'K8 Nguon ky truoc']


def chay(raw, **ts):
    core = CoreGia()
    tep = core.them_tep('DEMO.xlsx', raw)
    kq = core.chay_thu(app, 'excel.toan_ven@1', {'loai': 'tep', 'tep': tep}, ts)
    assert kq['trang_thai'] == 'XONG', kq
    tr = kq['ket_qua']['truong']
    data = json.loads(core.doc_tep(tr['tep_json']['tep_id']))
    bao = core.doc_tep(tr['tep_bao_cao']['tep_id'])
    assert len(bao) == tr['tep_bao_cao']['kich_thuoc']
    assert tr['tep_bao_cao']['mime'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return tr, data, openpyxl.load_workbook(BytesIO(bao), data_only=False)


@pytest.mark.parametrize('bat', [True, False])
@pytest.mark.parametrize('co_bo', [True, False])
def test_bao_cao_du_sheet_k8_cong_tac_va_bo_nhom(demo, bat, co_bo):
    ts = dict(o_dich='BTH!J39', kiem_nguon_kl=bat)
    if co_bo:
        ts['bo_nhom_json'] = (demo / 'bo_nhom_review_ttkl.json').read_text(encoding='utf-8')
    tr, data, wb = chay((demo / 'K1-K8-DEMO.xlsx').read_bytes(), **ts)
    try:
        assert wb.sheetnames == (SHEETS if bat else SHEETS[:-3])
        assert (tr['so_ngoai_nhom'] is not None) == co_bo
        assert bool(data['k8_nguon']) == bat
        assert any(p['kiem'] == 'K8' for p in data['phat_hien']) == bat
        assert data['canh_bao'] == []
        for ws in wb:
            assert ws.freeze_panes
            # Công thức nguồn chỉ là chuỗi hiển thị, không được chạy trong báo cáo.
            assert all(c.data_type != 'f' for row in ws for c in row)
        assert wb['Phat hien']['A5'].value == '#'
        assert wb['Phat hien']['B6'].fill.fgColor.rgb.endswith('F8D7D3')
        schema = json.loads((TESTS / 'schema/toan_ven.schema.json').read_text(encoding='utf-8'))
        kiem_schema(data, schema, schema)
        assert set(tr) == {t['ma'] for t in app.phieu['nang_luc'][0]['truong_ra']}
    finally:
        wb.close()


@pytest.mark.parametrize('ten', ['K1-K8-DEMO.xlsx', 'bang-kl-DEMO.xlsx'])
def test_k8_du_cot_va_phat_hien_khop_dap_an_va_nguon(goc, demo, ten):
    cu = goc.KiemTra(demo / ten)
    sd = SoDo((demo / ten).read_bytes())
    try:
        cu.k8_nguon_kl()
        moi = KiemTra(sd, {'kiem_nguon_kl': True}).chay(VIEC)
        for k in ('nguon', 'tang', 'tang_kt', 'bang_sh', 'cot_kl'):
            assert moi.kq[k] == cu.kq[k]
        assert Counter((p['muc'], p['kt'], p['o']) for p in moi.ph if p['kt'] == 'K8') == Counter(
            (p['muc'], p['kt'], p['o']) for p in cu.ph)
        if ten == 'K1-K8-DEMO.xlsx':
            dap = json.loads((demo / 'dap-an.json').read_text(encoding='utf-8'))[ten]['dau_hieu']
            assert {(p['muc'], p['kt'], p['o']) for p in moi.ph if p['kt'] == 'K8'} == {
                (p['muc'], p['kiem'], p['o']) for p in dap if p['kiem'] == 'K8'}
    finally:
        sd.dong(); cu.sd.wb.close(); cu.sd.wv.close()


def bang_phan_nhanh():
    cells = [('B1', NHAN), ('B2', 'Đơn vị tiền VND')]
    cells += [(c+'3', v) for c, v in {'A':'STT', 'B':'Tên công việc', 'C':'Đơn vị',
               'D':'Khối lượng', 'H':'Đơn giá', 'I':'Giá trị'}.items()]
    cells += [(c+'4',v) for c,v in zip('DEFGIJKL', ['Hợp đồng','Kỳ trước','Kỳ này','Lũy kế hết kỳ này']*2)]
    cong_thuc = {7: None, 8: 'D8', 9: 'D9*0.5', 10: 'Nguon!D10', 11: 'Nguon!D11',
                 12: 'Nguon!D13', 13: 'IF(Nguon!D13>D13,D13,Nguon!D13)',
                 14: 'An!D14', 15: '[1]Nguon!D15', 16: 'SUM(Nguon!D16:D17)', 17: 'Nguon!D17*2'}
    nguon, an = [('B1', NHAN), ('B3','Tên công việc'), ('D3','Diễn giải')], [('B1', NHAN)]
    for r, ct in cong_thuc.items():
        cells += [('A'+str(r),r-6), ('B'+str(r),('Ống thép DEMO hoàn toàn khác' if r==12 else f'Công tác DEMO {r}')), ('C'+str(r),'m3'),
                  ('D'+str(r),25), ('E'+str(r),2), ('F'+str(r),5), ('H'+str(r),1000000),
                  ('G'+str(r),25 if r in (8,13) else 12.5 if r==9 else 40 if r==17 else 5,ct)]
        nguon += [('B'+str(r),f'Công tác DEMO {r}')]
        an += [('B'+str(r),f'Công tác DEMO {r}'), ('D'+str(r),5)]
        if r != 11:
            nguon.append(('D'+str(r),30 if r==13 else 5,'2+3' if r==10 else None))
    cells.append(('B18', 'Cộng'))
    return workbook([('BTH',sheet(cells,gop=('D3:G3','I3:L3')),'visible'),
                     ('Nguon',sheet(nguon),'visible'), ('An',sheet(an),'hidden')])


def test_cac_nhanh_k8_khop_nguon(goc, tmp_path):
    raw = bang_phan_nhanh()
    p = tmp_path / 'nguon-DEMO.xlsx'; p.write_bytes(raw)
    cu, sd = goc.KiemTra(p), SoDo(raw)
    try:
        cu.k8_nguon_kl()
        moi = KiemTra(sd, {}); moi.k8_nguon_kl()
        for k in ('nguon', 'tang', 'tang_kt'):
            assert moi.kq[k] == cu.kq[k]
        assert [r[7] for r in moi.kq['nguon']] == ['Nhập tay','Bằng KL HĐ','Tỷ lệ × KL HĐ',
                'Tính từ diễn giải / công thức','Nguồn trống','Link lệch dòng','Nhập tay',
                'Nhập tay','File ngoài','Tính từ diễn giải / công thức','Hệ số × ô khác']
        assert 'đang bị chặn' in moi.kq['nguon'][6][8]
        assert 'qua sheet ẩn' in moi.kq['nguon'][7][8]
        assert Counter((p['muc'],p['kt'],p['o']) for p in moi.ph) == Counter(
            (p['muc'],p['kt'],p['o']) for p in cu.ph)
    finally:
        sd.dong(); cu.sd.wb.close(); cu.sd.wv.close()


def sua_xml(raw, cu, moi):
    with ZipFile(BytesIO(raw)) as z:
        muc = {n: z.read(n).replace(cu, moi) if n.startswith('xl/worksheets/') else z.read(n) for n in z.namelist()}
    return zip_xml(muc)


@pytest.mark.parametrize('ma', ['VND', 'USD', None, 'xung_dot'])
def test_tien_trong_json_va_bao_cao_khong_tu_gan_don_vi(demo, ma):
    raw = (demo / 'K1-K8-DEMO.xlsx').read_bytes()
    moi = '' if ma is None else 'VND; Currency: USD' if ma == 'xung_dot' else ma
    raw = sua_xml(raw, b'VND', moi.encode())
    _, data, wb = chay(raw, o_dich='BTH!J39', kiem_nguon_kl=True)
    try:
        code = None if ma in (None, 'xung_dot') else ma
        assert data['k8_nguon'][0]['gia_tri_luy_ke'] == {'so':'7000000', 'tien_te':code}
        for ten, cot in [('K8 Tung dong', 'F'), ('K8 Nguon KL', 'C'), ('K2 Go tay', 'E')]:
            vals = [wb[ten].cell(r, openpyxl.utils.column_index_from_string(cot)).value
                    for r in range(5 if ten=='K8 Nguon KL' else 4, wb[ten].max_row+1)]
            assert any(v is not None for v in vals) == bool(code)
            if code:
                assert all(v is None or str(v).endswith(' '+code) for v in vals)
            else:
                assert all(v is None for v in vals)
        for row in wb['K7 Cay truy vet'].iter_rows():
            if row[2].value == 'BTH!J39':
                assert row[4].value == (f'60160777 {code}' if code else None)
        if code is None:
            assert all('GT lũy kế' not in p['mo_ta'] for p in data['phat_hien'] if p['kiem']=='K8')
    finally:
        wb.close()


def test_k8_thieu_bang_la_kiem_soat_khong_lo_loi(demo):
    _, data, wb = chay((demo/'sach-DEMO.xlsx').read_bytes(), kiem_nguon_kl=True)
    try:
        assert wb.sheetnames == SHEETS
        p = [p for p in data['phat_hien'] if p['kiem']=='K8']
        assert len(p)==1 and p[0]['muc']=='Kiểm soát'
        assert 'Không nhận được bảng' in p[0]['mo_ta']
        assert data['k8_nguon'] == []
    finally:
        wb.close()


def test_tat_k8_khong_goi_doc_bang(demo, monkeypatch):
    import e_kiem_excel.kiem_tra as module
    monkeypatch.setattr(module, 'tim_bang_chi_tiet', lambda *a: pytest.fail('K8 đang tắt.'))
    _, _, wb = chay((demo/'K1-K8-DEMO.xlsx').read_bytes(), kiem_nguon_kl=False)
    wb.close()


def test_k8_huy_khong_bi_nuot(demo):
    sd = SoDo((demo/'K1-K8-DEMO.xlsx').read_bytes())
    try:
        kt = KiemTra(sd, {})
        def huy():
            raise ViecDaHuy()
        kt._kiem_huy = huy
        with pytest.raises(ViecDaHuy):
            kt.k8_nguon_kl()
    finally:
        sd.dong()


def test_bao_cao_huy_dong_workbook(demo, monkeypatch):
    sd = SoDo((demo/'sach-DEMO.xlsx').read_bytes())
    try:
        kt = KiemTra(sd, {}).chay(VIEC)
        da_dong = []
        dong = openpyxl.Workbook.close
        monkeypatch.setattr(openpyxl.Workbook, 'close', lambda wb: (da_dong.append(True), dong(wb)))
        def huy():
            raise ViecDaHuy()
        kt._kiem_huy = huy
        with pytest.raises(ViecDaHuy):
            ghi(kt)
        assert da_dong == [True]
    finally:
        sd.dong()


def test_bao_cao_khong_cat_ngam_o_dai():
    wb = openpyxl.Workbook()
    try:
        with pytest.raises(LoiNghiepVu) as e:
            _sheet(wb,'DEMO','DEMO',['DEMO'],[20],[['A'*32768]])
        assert e.value.ma == 'VUOT_GIOI_HAN'
    finally:
        wb.close()


@pytest.mark.parametrize('dg', ['1000000000000000000000000000001', '-1000000000.125', '0.125'])
def test_decimal_k8_fallback_va_tong_khong_mat_chu_so(dg):
    raw = sua_xml(bang_phan_nhanh(), b'<v>1000000</v>', f'<v>{dg}</v>'.encode())
    sd = SoDo(raw)
    try:
        kt = KiemTra(sd, {})
        kt.k8_nguon_kl()
        from decimal import localcontext
        with localcontext() as ctx:
            ctx.prec = 100
            expected = round(Decimal('5') * Decimal(dg))
        assert kt.kq['nguon'][0][5] == expected
        assert sum(int(row[2]) for row in kt.kq['tang']) == sum(row[5] for row in kt.kq['nguon'])
        assert sum(int(row[3]) for row in kt.kq['tang']) == sum(row[6] for row in kt.kq['nguon'])
    finally:
        sd.dong()


def test_k8_vuot_tang_tu_choi_khong_cat_ngam():
    raw = workbook([('DEMO', sheet([('A1',NHAN)] +
                    [(f'G{r}',1,f'G{r+1}') for r in range(1,12)]), 'visible')])
    sd = SoDo(raw)
    try:
        kt = KiemTra(sd, {})
        with pytest.raises(LoiNghiepVu) as e:
            kt._nguon('DEMO',7,1,Decimal('25'))
        assert e.value.ma == 'VUOT_GIOI_HAN'
    finally:
        sd.dong()
