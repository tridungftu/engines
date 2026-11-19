"""EX-5: hai đáp án độc lập, biên tham số, từ khóa chung và vòng đời workbook."""

from copy import deepcopy
from datetime import datetime
from decimal import Decimal
from io import BytesIO
import json

import openpyxl
import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu

from e_kiem_excel import bo_nhom, chuan_hoa, doc_bang, doc_tong_quat as tq
from sinh_demo import sheet, workbook, bang_kl
from sinh_tong_quat import KHUON_GIA_THANH, KHUON_BAO_GIA
from test_ex_4 import chay


def tham_so(k=KHUON_GIA_THANH, **them):
    return {"khuon": "tong_quat", "khuon_cot_json": json.dumps(k, ensure_ascii=False), **them}


@pytest.mark.parametrize('ten,khuon', [('gia-thanh-DEMO.xlsx', KHUON_GIA_THANH), ('bao-gia-DEMO.xlsx', KHUON_BAO_GIA)])
def test_hai_dap_an_demo(demo, ten, khuon):
    t, j = chay((demo/ten).read_bytes(), tham_so(khuon))
    dap = json.loads((demo/'dap-an.json').read_text(encoding='utf-8'))[ten]
    for k in ('sheet', 'dong_tieu_de', 'so_dong', 'so_dong_nhom', 'so_canh_bao'):
        assert t[k] == dap[k]
    assert j['cot'] == dap['cot'] and j['tien_te'] == dap['tien_te']
    assert [d['gia_tri'] for d in j['dong'] if d['du_cot_bat_buoc']] == dap['gia_tri']
    assert j['khuon'] == 'tong_quat' and j['tong_hop'] == {}
    assert t['gia_tri_hop_dong'] is t['gia_tri_de_nghi'] is None
    assert not t['tien_te_chua_ro']
    assert len(j['canh_bao']) == dap['so_canh_bao']
    if 'gia-thanh' in ten:
        assert all(d['nhom'] == 'Nhóm sản xuất DEMO' for d in j['dong'])
    else:
        assert j['canh_bao'] == [{'ma':'SO_DANG_CHU','o':'Bao gia DEMO!F5','mo_ta':'Ô số đang được lưu dưới dạng chữ.'}]


@pytest.mark.parametrize('sai', [None, '', '{}', '[]', 'null', '{', '"DEMO"', 'true',
    '{"phien_ban":1,"phien_ban":1,"cot":[],"dong_dung":[]}', '['*1100,
    '\ud800', 12, {'cot': []}])
def test_khuon_json_sai(sai):
    with pytest.raises(LoiNghiepVu) as exc:
        tq.doc_khuon(sai)
    assert exc.value.ma == 'THAM_SO_KHONG_HOP_LE'


@pytest.mark.parametrize('duong,gia_tri', [
    ('phien_ban', True), ('phien_ban', 2), ('phien_ban', 1.0), ('cot', []), ('cot', {}),
    ('dong_dung', 'cong'), ('dong_dung', [None]), ('dong_dung', ['=']),
    ('cot.0.ma', ''), ('cot.0.ma', 'Có dấu'), ('cot.0.ma', 'x'*65),
    ('cot.0.tu_khoa', []), ('cot.0.tu_khoa', 'san pham'), ('cot.0.tu_khoa', [42]),
    ('cot.0.tu_khoa', [' ']), ('cot.0.tu_khoa', ['=  ']),
    ('cot.0.kieu', 'float'), ('cot.0.kieu', []), ('cot.0.bat_buoc', 1),
])
def test_cau_truc_sai(duong, gia_tri):
    k = deepcopy(KHUON_GIA_THANH)
    obj = k
    cac_khoa = duong.split('.')
    for key in cac_khoa[:-1]:
        obj = obj[int(key)] if isinstance(obj, list) else obj[key]
    obj[cac_khoa[-1]] = gia_tri
    with pytest.raises(LoiNghiepVu) as exc:
        tq.doc_khuon(json.dumps(k))
    assert exc.value.ma == 'THAM_SO_KHONG_HOP_LE'


def test_khoa_la_thieu_trung_va_khong_cot_bat_buoc():
    for loai in ('la', 'thieu', 'trung', 'khong_bat_buoc'):
        k = deepcopy(KHUON_GIA_THANH)
        if loai == 'la':
            k['regex'] = '.*'
        elif loai == 'thieu':
            del k['cot'][0]['kieu']
        elif loai == 'trung':
            k['cot'][1]['ma'] = k['cot'][0]['ma']
        else:
            for c in k['cot']:
                c['bat_buoc'] = False
        with pytest.raises(LoiNghiepVu):
            tq.doc_khuon(json.dumps(k))


def test_tran_sat_bien_cot_tu_khoa_byte():
    k = deepcopy(KHUON_GIA_THANH)
    k['cot'] = [{**k['cot'][0], 'ma': f'cot_{i}'} for i in range(30)]
    k['dong_dung'] = ['cong']*170
    s = json.dumps(k)
    assert len(tq.doc_khuon(s)['cot']) == 30  # đúng 200 từ khóa
    k['dong_dung'].append('cong')
    with pytest.raises(LoiNghiepVu):
        tq.doc_khuon(json.dumps(k))
    k['dong_dung'] = []
    k['cot'].append({**k['cot'][0], 'ma':'cot_30'})
    with pytest.raises(LoiNghiepVu):
        tq.doc_khuon(json.dumps(k))
    s = json.dumps(KHUON_GIA_THANH)
    sat = s + ' '*(32768-len(s.encode()))
    tq.doc_khuon(sat)
    for raw in (sat+' ', s+' '*(32768-len(s.encode())-1)+'á'):
        with pytest.raises(LoiNghiepVu) as exc:
            tq.doc_khuon(raw)
        assert exc.value.ma == 'THAM_SO_KHONG_HOP_LE'


@pytest.mark.parametrize('raw', ['NaN','Infinity','-Infinity'])
def test_khong_nhan_hang_json_ngoai_chuan(raw):
    s=json.dumps(KHUON_GIA_THANH).replace('"phien_ban": 1', '"phien_ban": '+raw)
    with pytest.raises(LoiNghiepVu):
        tq.doc_khuon(s)


@pytest.mark.parametrize('tu,chuoi,dat', [
    ('GIÁ ĐỢT #','gia dot 123',True), ('=ma','Mã hàng',True), ('=ma','mach',False),
    ('chi phi','CHI PHÍ vật liệu',True), ('dai|rong','dai',False),
    ('dai|rong','dai|rong',True), ('.*','abc',False), ('=dot #','dot 2a',False),
])
def test_matcher_dung_chung(tu,chuoi,dat):
    assert tq.khop_tu_khoa is bo_nhom.khop_tu_khoa
    assert tq.khop_tu_khoa(tu,chuoi) is dat


def tep_don(cac_o, gop=()):
    return workbook([('DEMO', sheet([('A1','Công ty DEMO Ánh Dương'), *cac_o],gop=gop),'visible')])


def khuon_don():
    return {'phien_ban':1, 'cot':[
        {'ma':'ten','tu_khoa':['=ten'],'bat_buoc':True,'kieu':'van_ban'},
        {'ma':'so','tu_khoa':['=so'],'bat_buoc':True,'kieu':'so'},
    ], 'dong_dung':['=tong cong']}


def test_khong_thay_bang_va_tieu_de_mo_ho():
    for cells in [[('A3','Tên')], [('A3','Tên'),('B3','Số'),('C3','Số')]]:
        t,_=chay(tep_don(cells),tham_so(khuon_don()))
        assert t['loi']['ma']=='KHONG_TIM_THAY_BANG'


def test_dong_thieu_sai_kieu_nhom_va_dung():
    raw=tep_don([('A3','Tên'),('B3','Số'),('A4','Nhóm DEMO'),
                 ('A5','Mặt hàng DEMO'),('B5','abc'), ('B6','123'),
                 ('A7','Tổng cộng'),('B7',999),('A8','DEMO đuôi'),('B8',1)])
    t,j=chay(raw,tham_so(khuon_don()))
    assert t['so_dong']==1 and t['so_dong_nhom']==1 and t['so_canh_bao']==3
    assert len(j['dong'])==3 and j['dong'][1]['gia_tri']['so'] is None
    assert not j['dong'][2]['du_cot_bat_buoc']
    assert {c['ma'] for c in j['canh_bao']}=={'GIA_TRI_SAI_KIEU','DONG_THIEU_COT_BAT_BUOC','SO_DANG_CHU'}


def test_kieu_ngay_excel_va_tien_chua_ro(demo):
    wb=openpyxl.load_workbook(BytesIO((demo/'bao-gia-DEMO.xlsx').read_bytes()))
    try:
        ws=wb['Bao gia DEMO']
        ws['B2']='Bảng báo giá DEMO'
        ws['H5']=datetime(2026,10,30,13,15)
        ws['H6']='2026-02-30'
        raw=BytesIO(); wb.save(raw)
        t,j=chay(raw.getvalue(),tham_so(KHUON_BAO_GIA))
        assert t['tien_te_chua_ro'] and j['tien_te'] is None
        assert j['dong'][0]['gia_tri']['hieu_luc']=='2026-10-30'
        assert j['dong'][1]['gia_tri']['hieu_luc'] is None
        assert j['dong'][0]['gia_tri']['don_gia']=={'so':'2500000000.125','tien_te':None}
        t,j=chay(raw.getvalue(),tham_so(KHUON_BAO_GIA,tien_te='EUR'))
        assert j['dong'][0]['gia_tri']['don_gia']['tien_te']=='EUR'
        assert not t['tien_te_chua_ro']
    finally:
        wb.close()


def test_don_vi_trong_dinh_dang_o(demo):
    wb=openpyxl.load_workbook(BytesIO((demo/'bao-gia-DEMO.xlsx').read_bytes()))
    try:
        ws=wb['Bao gia DEMO']; ws['B2']='Báo giá DEMO'
        ws['F5'].number_format='#,##0 "EUR"'
        raw=BytesIO(); wb.save(raw)
        t,j=chay(raw.getvalue(),tham_so(KHUON_BAO_GIA))
        assert j['tien_te']=='EUR' and not t['tien_te_chua_ro']
    finally:
        wb.close()


def test_loi_qua_cong_khong_lo_noi_dung():
    t,_=chay(bang_kl(), {'khuon':'tong_quat','khuon_cot_json':'{"DEMO":"noi dung khong duoc lo"}'})
    assert t['loi']['ma']=='THAM_SO_KHONG_HOP_LE'
    assert 'noi dung khong duoc lo' not in t['loi']['thong_diep']


def test_helper_ex4_truc_tiep_dung_ex1():
    assert doc_bang._nfc is chuan_hoa.nfc
    assert doc_bang._bo_dau is chuan_hoa.bo_dau
    assert doc_bang._num is chuan_hoa.num
    assert doc_bang._num(Decimal('9007199254740993'))==Decimal('9007199254740993')


def test_huy_va_loi_deu_dong_workbook(demo,monkeypatch):
    raw=(demo/'bao-gia-DEMO.xlsx').read_bytes()
    wb=openpyxl.load_workbook(BytesIO(raw),data_only=True)
    dong=[]
    monkeypatch.setattr(wb,'close',lambda: dong.append(True))
    monkeypatch.setattr(tq.openpyxl,'load_workbook',lambda *a,**kw: wb)
    def huy():
        raise RuntimeError('HUY_DEMO')
    monkeypatch.setattr(tq,'_tim_bang',lambda *a: huy())
    with pytest.raises(RuntimeError,match='HUY_DEMO'):
        tq.doc_tong_quat(raw,tham_so(KHUON_BAO_GIA),'e_kiem_excel 0.1.0')
    assert dong==[True]


def test_tran_json_va_tep_hong(demo,monkeypatch):
    raw=(demo/'gia-thanh-DEMO.xlsx').read_bytes()
    ts=tham_so()
    _,noi_dung=tq.doc_tong_quat(raw,ts,'e_kiem_excel 0.1.0')
    monkeypatch.setattr(tq,'TEP_TOI_DA_BYTE',len(noi_dung))
    assert tq.doc_tong_quat(raw,ts,'e_kiem_excel 0.1.0')[1]==noi_dung
    monkeypatch.setattr(tq,'TEP_TOI_DA_BYTE',len(noi_dung)-1)
    with pytest.raises(LoiNghiepVu) as exc:
        tq.doc_tong_quat(raw,ts,'e_kiem_excel 0.1.0')
    assert exc.value.ma=='VUOT_GIOI_HAN'
    with pytest.raises(LoiNghiepVu) as exc:
        tq.doc_tong_quat(b'DEMO hong',ts,'e_kiem_excel 0.1.0')
    assert exc.value.ma=='TEP_HONG'
