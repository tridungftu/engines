"""Hợp đồng EX-0, bộ chặn trước parser và fixture có dấu hiệu thật."""

import hashlib
from io import BytesIO
import json
from pathlib import Path
import sys
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import openpyxl
import pytest
from defusedxml.common import DefusedXmlException
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia
from e_kiem_excel.chay import app
from e_kiem_excel import nhan_dien as nd
from sinh_demo import NS, bang_kl, sinh, workbook, zip_xml

TESTS=Path(__file__).resolve().parent
GOI=TESTS.parent/'goi'/'e_kiem_excel'


def test_manifest():
    p=app.phieu
    assert p['phien_ban_manifest']==2
    assert len(p['nang_luc'])==2
    assert not set(p)&{'ngan_du_lieu','cau_hinh','du_lieu'}
    assert [len(n['truong_ra']) for n in p['nang_luc']]==[11,11]
    for n in p['nang_luc']:
        assert n['nhan']==['tep'] and n['tra']=='truong' and n['huy_duoc'] is True
        assert n['gioi_han']['tep_toi_da_mib']==20 and n['gioi_han']['thoi_han_giay']==120
        assert all(t['toi_da']>0 for t in n['tham_so'] if t['kieu']=='van_ban')
    assert {v['ma'] for v in p['nang_luc'][1]['tham_so'][0]['lua_chon']}=={'tong_quat','xay_dung_klgt'}


def test_demo_khong_thanh_cong_gia():
    kq=CoreGia().chay_thu_demo(app)
    assert len(kq)==3
    assert [k['trang_thai'] for k in kq]==['XONG','XONG','LOI']
    assert kq[2]['loi']['ma']=='CHUA_LAM' and kq[2]['ket_qua'] is None
    for k in kq[:2]:
        assert k['ket_qua']['truong']['tep_bao_cao'] is None
        assert k['ket_qua']['truong']['o_dich'] is None


def test_fixture_tat_dinh(demo,tmp_path):
    sinh(tmp_path)
    hashes=json.loads((TESTS/'demo'/'bam-fixture.json').read_text(encoding='utf-8'))
    for ten,bam in hashes.items():
        assert hashlib.sha256((demo/ten).read_bytes()).hexdigest()==bam
        assert (demo/ten).read_bytes()==(tmp_path/ten).read_bytes()==(TESTS/'demo'/ten).read_bytes()
    for tep in (GOI/'demo').glob('*.xlsx'):
        assert tep.read_bytes()==(demo/tep.name).read_bytes()


def test_cong_thuc_co_v(demo):
    for ten in ('sach-DEMO.xlsx','K1-K8-DEMO.xlsx','bang-kl-DEMO.xlsx'):
        with ZipFile(demo/ten) as z:
            so=0
            for t in z.namelist():
                if t.startswith('xl/worksheets/'):
                    for c in ET.fromstring(z.read(t)).iter('{'+NS+'}c'):
                        if c.find('{'+NS+'}f') is not None:
                            so+=1
                            assert c.find('{'+NS+'}v') is not None
            assert so>0
        f=openpyxl.load_workbook(demo/ten,data_only=False)
        v=openpyxl.load_workbook(demo/ten,data_only=True)
        assert f.worksheets[0]['A1'].value or f.worksheets[0]['B1'].value
        if ten=='sach-DEMO.xlsx':
            assert f['DEMO']['B3'].value=='=B2+1' and v['DEMO']['B3'].value==2
        f.close(); v.close()
    v=openpyxl.load_workbook(demo/'thieu-v-DEMO.xlsx',data_only=True)
    assert v['DEMO']['B3'].value is None
    v.close()


@pytest.mark.parametrize('ten,ma',[('cu-DEMO.xls','TEP_KHONG_HO_TRO'),('thuc-the-DEMO.xlsx','TEP_HONG')])
def test_tep_co_y_loi(demo,ten,ma):
    with pytest.raises(LoiNghiepVu) as exc:
        nd.kiem_tep((demo/ten).read_bytes(),ten)
    assert exc.value.ma==ma


@pytest.mark.parametrize('ten,raw,ma',[('a.xls',b'PK\x03\x04','TEP_KHONG_HO_TRO'),('a.xlsx',b'abc','TEP_HONG'),('a.xlsx',nd.OLE,'TEP_KHONG_HO_TRO'),('a.csv',b'DEMO','TEP_KHONG_HO_TRO'),('a.xlsx',b'PK\x03\x04DEMO','TEP_HONG')])
def test_nhan_dien(ten,raw,ma):
    with pytest.raises(LoiNghiepVu) as exc:
        nd.kiem_tep(raw,ten)
    assert exc.value.ma==ma
    assert ten not in exc.value.thong_diep


@pytest.mark.parametrize('duoi',['.xlsx','.xlsm','.XLSX'])
def test_nhan_zip_hop_le(demo,duoi):
    k=nd.kiem_tep((demo/'sach-DEMO.xlsx').read_bytes(),'DEMO'+duoi)
    assert k['so_o']==3 and k['so_entry']==5


def test_bom_nen(demo):
    with ZipFile(demo/'sach-DEMO.xlsx') as z:
        muc={n:z.read(n) for n in z.namelist()}
    muc['dem-DEMO.bin']=b'0'*(nd.GIAI_NEN_TOI_DA_BYTE+1)
    raw=zip_xml(muc)
    assert len(raw)<nd.TEP_TOI_DA_BYTE
    with pytest.raises(LoiNghiepVu) as exc:
        nd.kiem_tep(raw,'DEMO.xlsx')
    assert exc.value.ma=='VUOT_GIOI_HAN'


@pytest.mark.parametrize('hang,gia_tri',[('ENTRY_TOI_DA',4),('O_TOI_DA',2),('GIAI_NEN_TOI_DA_BYTE',100),('TEP_TOI_DA_BYTE',100)])
def test_tran(demo,monkeypatch,hang,gia_tri):
    monkeypatch.setattr(nd,hang,gia_tri)
    with pytest.raises(LoiNghiepVu) as exc:
        nd.kiem_tep((demo/'sach-DEMO.xlsx').read_bytes(),'DEMO.xlsx')
    assert exc.value.ma=='VUOT_GIOI_HAN'


def test_tran_o_sat_bien(demo,monkeypatch):
    monkeypatch.setattr(nd,'O_TOI_DA',3)
    assert nd.kiem_tep((demo/'sach-DEMO.xlsx').read_bytes(),'DEMO.xlsx')['so_o']==3


def test_vung_thua():
    xml=f'<worksheet xmlns="{NS}"><sheetData><row r="1048576"><c r="XFD1048576"><v>1</v></c></row></sheetData></worksheet>'.encode()
    with pytest.raises(LoiNghiepVu) as exc:
        nd.kiem_tep(workbook([('DEMO',xml,'visible')]),'DEMO.xlsx')
    assert exc.value.ma=='VUOT_GIOI_HAN'


def test_thuc_the_utf16_va_workbook(demo):
    with ZipFile(demo/'thuc-the-DEMO.xlsx') as z:
        muc={n:z.read(n) for n in z.namelist()}
    xml=muc['xl/worksheets/sheet1.xml'].decode()
    muc['xl/worksheets/sheet1.xml']=xml.encode('utf-16')
    with pytest.raises(LoiNghiepVu,match='Không đọc') as exc:
        nd.kiem_tep(zip_xml(muc),'DEMO.xlsx')
    assert exc.value.ma=='TEP_HONG'
    muc['xl/worksheets/sheet1.xml']=bang_kl()  # phần không cần parse vì workbook bị từ chối trước
    muc['xl/workbook.xml']=xml.encode()
    with pytest.raises(LoiNghiepVu) as exc:
        nd.kiem_tep(zip_xml(muc),'DEMO.xlsx')
    assert exc.value.ma=='TEP_HONG'


def test_defusedxml_hoat_dong(demo):
    from openpyxl.xml import DEFUSEDXML
    assert DEFUSEDXML
    with pytest.raises(ValueError) as exc:
        openpyxl.load_workbook(demo/'thuc-the-DEMO.xlsx')
    assert isinstance(exc.value.__cause__, DefusedXmlException)


@pytest.mark.parametrize('nl',['excel.toan_ven@1','excel.doc_bang@1'])
@pytest.mark.parametrize('ten,ma',[('cu-DEMO.xls','TEP_KHONG_HO_TRO'),('thuc-the-DEMO.xlsx','TEP_HONG')])
def test_core_gia_kiem_truoc_openpyxl(demo,monkeypatch,nl,ten,ma):
    def cam(*a,**k):
        pytest.fail('Không được nạp openpyxl trong khung EX-0.')
    monkeypatch.setattr(openpyxl,'load_workbook',cam)
    core=CoreGia()
    tep=core.them_tep(ten,(demo/ten).read_bytes(),'application/octet-stream')
    k=core.chay_thu(app,nl,{'loai':'tep','tep':tep})
    assert k['trang_thai']=='LOI' and k['loi']['ma']==ma and k['ket_qua'] is None


@pytest.mark.parametrize('gui_kem',[True,False])
def test_mime_xlsm_sdk(demo,gui_kem):
    core=CoreGia()
    tep=core.them_tep('DEMO.xlsm',(demo/'sach-DEMO.xlsx').read_bytes())
    assert tep['mime']=='application/vnd.ms-excel.sheet.macroEnabled.12'
    pb={'loai':'tep','tep':tep}
    viec_id=core.giao_viec('excel.toan_ven@1',pb,gui_kem_dau_vao=gui_kem)
    core.chay(app)
    k=core.xem(viec_id)
    assert k['trang_thai']=='XONG'
    assert tep['mime'].endswith('macroEnabled.12')  # không sửa phong bì của caller


def test_huy(demo):
    def huy():
        raise RuntimeError('HUY_DEMO')
    with pytest.raises(RuntimeError,match='HUY_DEMO'):
        nd.kiem_tep((demo/'sach-DEMO.xlsx').read_bytes(),'DEMO.xlsx',kiem_huy=huy)


def test_sheet_doi_duoi_va_namespace(demo,monkeypatch):
    with ZipFile(demo/'sach-DEMO.xlsx') as z:
        muc={n:z.read(n) for n in z.namelist()}
    muc['xl/khac/demo.bin']=muc.pop('xl/worksheets/sheet1.xml')
    muc['xl/_rels/workbook.xml.rels']=muc['xl/_rels/workbook.xml.rels'].replace(b'worksheets/sheet1.xml',b'khac/demo.bin')
    monkeypatch.setattr(nd,'O_TOI_DA',2)
    with pytest.raises(LoiNghiepVu) as exc:
        nd.kiem_tep(zip_xml(muc),'DEMO.xlsx')
    assert exc.value.ma=='VUOT_GIOI_HAN'
    xml=f'<s:worksheet xmlns:s="{NS}"><s:sheetData><s:row r="1"><s:c r="A1"><s:v>1</s:v></s:c><s:c r="B1"><s:v>2</s:v></s:c><s:c r="C1"><s:v>3</s:v></s:c></s:row></s:sheetData></s:worksheet>'
    with pytest.raises(LoiNghiepVu) as exc:
        nd.kiem_tep(workbook([('DEMO',xml,'visible')]),'DEMO.xlsx')
    assert exc.value.ma=='VUOT_GIOI_HAN'


def test_merge_bom():
    xml=f'<worksheet xmlns="{NS}"><sheetData/><mergeCells><mergeCell ref="A1:XFD1048576"/></mergeCells></worksheet>'
    with pytest.raises(LoiNghiepVu) as exc:
        nd.kiem_tep(workbook([('DEMO',xml,'visible')]),'DEMO.xlsx')
    assert exc.value.ma=='VUOT_GIOI_HAN'


def test_o_khong_ghi_toa_do():
    xml=f'<worksheet xmlns="{NS}"><sheetData><row><c><v>1</v></c></row><row><c><v>2</v></c></row></sheetData></worksheet>'
    k=nd.kiem_tep(workbook([('DEMO',xml,'visible')]),'DEMO.xlsx')
    assert k['so_o']==2 and k['so_o_vung']==2


def test_nhat_ky_an_toan(capsys):
    app._ghi('NOI_DUNG_BI_MAT_DEMO')
    out=capsys.readouterr()
    assert 'NOI_DUNG_BI_MAT_DEMO' not in out.err+out.out
    assert 'EX_SDK_THONG_BAO' in out.err


def test_dau_hieu_k1_k8_bang_ma_goc(demo,monkeypatch):
    # Chỉ test nhập mã tham chiếu; runtime không có đường dẫn/import này.
    goc=TESTS.parent/'ma-nguon'
    expected={'toan_ven.py':'a97396de2be4cecfb060cd52689f4eec648f7904a7fd132089e10e3c897f6023','master_hd.py':'7c82daf635be14153599fb65a1059100c71b0b19a8a057e781187023688ae124'}
    for ten,bam in expected.items():
        # Git Windows checkout đổi LF thành CRLF; xác minh đúng bytes nguồn LF.
        assert hashlib.sha256((goc/ten).read_bytes().replace(b'\r\n',b'\n')).hexdigest()==bam
    monkeypatch.syspath_prepend(str(goc))
    import toan_ven
    kt=toan_ven.KiemTra(demo/'K1-K8-DEMO.xlsx',o_dich='BTH!J39')
    sd=kt.sd
    kt.chay()
    assert {f'K{i}' for i in range(1,9)} <= {x['kt'] for x in kt.ph}
    dap=json.loads((demo/'dap-an.json').read_text(encoding='utf-8'))
    for x in dap['K1-K8-DEMO.xlsx']['dau_hieu']:
        assert any(p['kt']==x['kiem'] and all(p[k]==x[k] for k in ('muc','o')) for p in kt.ph),x
    assert set((x['kt'],x['muc'],x['o']) for x in kt.ph)==set((x['kiem'],x['muc'],x['o']) for x in dap['K1-K8-DEMO.xlsx']['dau_hieu'])
    assert ('BTH','J21') in {(x[0],x[1]) for x in kt.kq['lech']}
    sd.wb.close(); sd.wv.close()
    kt=toan_ven.KiemTra(demo/'sach-DEMO.xlsx')
    sd=kt.sd
    kt.k1_tong_quan(); kt.k2_ban_do_cong_thuc(); kt.k3_lien_ket_dong(); kt.k4_sheet_an(); kt.k5_so_dang_chu(); kt.k6_tham_so_nhung()
    assert kt.ph==[]
    sd.wb.close(); sd.wv.close()
    import master_hd
    wb=openpyxl.load_workbook(demo/'bang-kl-DEMO.xlsx',data_only=True)
    bang=master_hd.tim_bang_chi_tiet(wb)
    assert bang['sheet']=='BTH' and bang['hdr']==3
    assert sum(bool(i['dvt']) for i in bang['items'])==30
    assert master_hd.tim_so_tong_hop(wb)['tt_ky_nay']['gia_tri']==60000000
    wb.close()


def test_doc_lap():
    from kiem_doc_lap import kiem_doc_lap,kiem_tien_trinh_sach
    assert kiem_doc_lap()==[]
    assert kiem_tien_trinh_sach()==[]
