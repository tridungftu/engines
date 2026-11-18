"""Sinh OOXML DEMO tất định bằng zipfile; không cần Excel/LibreOffice."""

from collections import defaultdict
from decimal import Decimal
import hashlib
from io import BytesIO
import json
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED, ZIP_STORED

NHAN = "Công ty DEMO Ánh Dương"
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
GOI = Path(__file__).resolve().parents[2] / "goi" / "e_kiem_excel"


def o(vi_tri, gia_tri, cong_thuc=None):
    """Giá trị công thức do caller tự tính, tuyệt đối không eval công thức."""
    if cong_thuc is not None:
        v = "" if gia_tri is None else f"<v>{gia_tri}</v>"
        kieu = ' t="e"' if isinstance(gia_tri, str) and gia_tri.startswith("#") else ""
        return f'<c r="{vi_tri}"{kieu}><f>{escape(cong_thuc.lstrip("="))}</f>{v}</c>'
    if isinstance(gia_tri, str):
        return f'<c r="{vi_tri}" t="inlineStr"><is><t>{escape(gia_tri)}</t></is></c>'
    return f'<c r="{vi_tri}"><v>{gia_tri}</v></c>'


def sheet(cac_o, *, gop=()):
    dong = defaultdict(list)
    for vi_tri, gt, *ct in cac_o:
        so = int("".join(c for c in vi_tri if c.isdigit()))
        dong[so].append(o(vi_tri, gt, *ct))
    xml = f'<worksheet xmlns="{NS}"><sheetData>'
    xml += "".join(f'<row r="{r}">{"".join(ds)}</row>' for r, ds in sorted(dong.items()))
    xml += "</sheetData>"
    if gop:
        xml += '<mergeCells>' + "".join(f'<mergeCell ref="{v}"/>' for v in gop) + '</mergeCells>'
    return (xml + '</worksheet>').encode()


def zip_xml(muc, *, nen=ZIP_DEFLATED):
    raw = BytesIO()
    with ZipFile(raw, 'w') as z:
        for ten, data in muc.items():
            zi = ZipInfo(ten, (2026, 10, 30, 0, 0, 0))
            zi.compress_type = nen
            zi.create_system = 0
            zi.external_attr = 0o600 << 16
            z.writestr(zi, data)
    return raw.getvalue()


def workbook(ds, *, nen=ZIP_DEFLATED):
    """ds = [(tên, XML sheet, visible|hidden)]."""
    types = '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
    wb = f'<workbook xmlns="{NS}" xmlns:r="{REL}"><sheets>'
    rels = '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    muc = {'_rels/.rels': f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="{REL}/officeDocument" Target="xl/workbook.xml"/></Relationships>'}
    for i, (ten, data, trang_thai) in enumerate(ds, 1):
        wb += f'<sheet name={quoteattr(ten)} sheetId="{i}" state="{trang_thai}" r:id="rId{i}"/>'
        types += f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        rels += f'<Relationship Id="rId{i}" Type="{REL}/worksheet" Target="worksheets/sheet{i}.xml"/>'
        muc[f'xl/worksheets/sheet{i}.xml'] = data
    muc['[Content_Types].xml'] = types + '</Types>'
    muc['xl/workbook.xml'] = wb + '</sheets></workbook>'
    muc['xl/_rels/workbook.xml.rels'] = rels + '</Relationships>'
    return zip_xml(muc, nen=nen)


def bang_kl(*, cai_loi=False):
    cells = [('B1', NHAN), ('B2', 'Bảng khối lượng DEMO — đơn vị tiền VND')]
    hdr = {'A':'STT', 'B':'Tên công việc', 'C':'Đơn vị', 'D':'Khối lượng', 'H':'Đơn giá', 'I':'Giá trị'}
    cells += [(c+'3', v) for c,v in hdr.items()]
    cells += [(c+'4',v) for c,v in zip('DEFGIJKL', ['Hợp đồng','Kỳ trước','Kỳ này','Lũy kế hết kỳ này']*2)]
    cells += [('A6','A'),('B6','Nhóm công tác DEMO')]
    for r in range(7,37):
        dg = 1000000
        cells += [('A'+str(r),r-6),('B'+str(r),f'Công tác DEMO {r:02d} bê tông'),('C'+str(r),'m3'),('D'+str(r),25),('E'+str(r),2),('H'+str(r),dg)]
        # 30 liên kết theo dòng để đủ điều kiện K3 của mã gốc.
        rr = r + 1 if cai_loi and r==18 else r
        cells += [('F'+str(r),5,f"='Nguon'!D{rr}"),('G'+str(r),7 if cai_loi else 7,f'E{r}+F{r}' if not cai_loi else None)]
        for c, klc, kl in [('I','D',25),('J','E',2),('K','F',5),('L','G',7)]:
            ct=f'{klc}{r}*H{r}'
            val=kl*dg
            if cai_loi and c=='J' and r==20:
                cells.append((c+str(r),val))
            elif cai_loi and c=='J' and r==21:
                cells.append((c+str(r),int(Decimal(val)*Decimal('1.08')),ct+'*1.08'))
            else:
                cells.append((c+str(r),val,ct))
    cells += [('B37','Cộng'),('F39','Giá trị đề nghị thanh toán kỳ này')]
    total=30*2*1000000 + (160000 if cai_loi else 0)
    cells += [('J39', total+(777 if cai_loi else 0),'SUM(J7:J36)'+('+O1' if cai_loi else ''))]
    if cai_loi:
        cells += [('M7','#REF!','#REF!'),('N7',1000000,"'An'!D7"),('O1',777),('P10','1000000')]
    nguon = [('B1',NHAN),('B3','Tên công việc'),('D3','Khối lượng kỳ này')]
    for r in range(7,37):
        ten = 'Ống thép DEMO hoàn toàn khác' if cai_loi and r==19 else f'Công tác DEMO {r:02d} bê tông'
        nguon += [('B'+str(r),ten),('D'+str(r),5)]
    ds=[('BTH',sheet(cells,gop=('D3:G3','I3:L3')), 'visible'),('Nguon',sheet(nguon),'visible')]
    if cai_loi:
        ds.append(('An',sheet([('B1',NHAN),('D7',1000000)]),'hidden'))
    return workbook(ds)


def sinh(thu_muc=None, *, chep_goi=False):
    out=Path(thu_muc or Path(__file__).parent)
    out.mkdir(parents=True, exist_ok=True)
    sach=workbook([('DEMO',sheet([('A1',NHAN),('B2',1),('B3',2,'B2+1')]),'visible')])
    thieu=workbook([('DEMO',sheet([('A1',NHAN),('B3',None,'1+1')]),'visible')])
    xml=f'<!DOCTYPE worksheet [<!ENTITY a "DEMO"><!ENTITY b "&a;&a;"><!ENTITY c "&b;&b;">]><worksheet xmlns="{NS}"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>&c;</t></is></c></row></sheetData></worksheet>'.encode()
    files={'sach-DEMO.xlsx':sach,'thieu-v-DEMO.xlsx':thieu,'thuc-the-DEMO.xlsx':workbook([('DEMO',xml,'visible')]),'cu-DEMO.xls':bytes.fromhex('D0CF11E0A1B11AE1')+b'DEMO\0'*20,'K1-K8-DEMO.xlsx':bang_kl(cai_loi=True),'bang-kl-DEMO.xlsx':bang_kl()}
    for ten,raw in files.items():
        (out/ten).write_bytes(raw)
    # Bộ nhóm của module chỉ là fixture test, không chép vào gói runtime.
    bo_nhom = Path(__file__).with_name('bo_nhom_review_ttkl.json').read_bytes()
    (out/'bo_nhom_review_ttkl.json').write_bytes(bo_nhom)
    dap_an={
      'nhan':NHAN,'tien_te':'VND','ngay':'2026-10-30',
      'K1-K8-DEMO.xlsx':{'o_dich':'BTH!J39','kiem_nguon_kl':True,'dau_hieu':[
        {'kiem':'K1','muc':'Cao','o':'BTH!M7','ly_do':'Công thức #REF! có giá trị lỗi lưu'},
        {'kiem':'K2','muc':'Cao','o':'BTH!J20','ly_do':'Nhập tay giữa hơn 10 công thức cùng mẫu'},
        {'kiem':'K1','muc':'Trung bình','o':'BTH','ly_do':'Công thức chứa #REF!'},
        {'kiem':'K2','muc':'Trung bình','o':'BTH!F18','o_lien_quan':['BTH!F18','BTH!J21'],'ly_do':'Mã gốc gom hai công thức lệch mẫu theo sheet'},
        {'kiem':'K3','muc':'Cao','o':'BTH!F18','ly_do':'Trỏ lệch tên công tác trong cặp sheet có 30 liên kết'},
        {'kiem':'K4','muc':'Trung bình','o':'An','ly_do':'Sheet ẩn được tham chiếu'},
        {'kiem':'K5','muc':'Trung bình','o':'BTH!P10','ly_do':'Số lưu dạng chữ'},
        {'kiem':'K6','muc':'Trung bình','o':'BTH!J21','ly_do':'Hằng 1.08 trong cột cây K7'},
        {'kiem':'K7','muc':'Cao','o':'BTH!O1','ly_do':'Ô nhập tay ngoài nhóm'},
        {'kiem':'K8','muc':'Cao','o':'BTH!E','ly_do':'KL kỳ trước nhập tay'},
        {'kiem':'K8','muc':'Cao','o':'BTH!G','ly_do':'KL lũy kế nhập tay'}]},
      'sach-DEMO.xlsx':{'phat_hien_K1_K6':[],'gia_tri_luu':{'DEMO!B3':2}},
      'thieu-v-DEMO.xlsx':{'kiem':'K1','muc':'Kiểm soát','o':'DEMO','da_tinh_lai':False},
      'thuc-the-DEMO.xlsx':{'ma_loi':'TEP_HONG'},'cu-DEMO.xls':{'ma_loi':'TEP_KHONG_HO_TRO'},
      'bang-kl-DEMO.xlsx':{'sheet':'BTH','dong_tieu_de':3,'so_dong':30,'so_dong_nhom':1,'gia_tri_de_nghi':{'so':'60000000','tien_te':'VND'}}}
    (out/'dap-an.json').write_text(json.dumps(dap_an,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    bam={ten:hashlib.sha256(raw).hexdigest() for ten,raw in sorted(files.items())}
    bam['dap-an.json']=hashlib.sha256((out/'dap-an.json').read_bytes()).hexdigest()
    bam['bo_nhom_review_ttkl.json']=hashlib.sha256(bo_nhom).hexdigest()
    (out/'bam-fixture.json').write_text(json.dumps(bam,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if chep_goi:
        demo=GOI/'demo'; demo.mkdir(parents=True,exist_ok=True)
        for ten in ('K1-K8-DEMO.xlsx','bang-kl-DEMO.xlsx','sach-DEMO.xlsx'):
            (demo/ten).write_bytes(files[ten])
    return files


if __name__=='__main__':
    sinh(chep_goi=True)
