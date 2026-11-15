"""Fixture XLSX/CoreGia B6, chỉ DEMO trong RAM; không Office/Local thật."""
from e_mask.xml_excel import chu_xml
from ho_tro_mask_b1 import excel_demo, them_phan, CT_S, S
from ho_tro_mask_b3 import goi_office, phan_demo
from ho_tro_mask_b5 import bo, TEN, ALIAS, DS


def excel(chu=TEN, *, noi_dung=None, shared=False, codec=None, so_sheet=1, cach=8):
    if noi_dung is None:
        noi_dung = ('<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>0</v></c></row>'
                    if shared else '<row r="1"><c r="A1" t="inlineStr"><is><t>' + chu_xml(chu) + '</t></is></c></row>')
    p = excel_demo(noi_dung=noi_dung)
    p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('DEMO 1', 'bảng')
    if shared:
        them_phan(p, 'xl/sharedStrings.xml', f'<sst xmlns="{S}" count="{so_sheet * 2}" uniqueCount="1"><si><t>'
                  + chu_xml(chu) + '</t></si></sst>', CT_S + 'sharedStrings+xml', 'sharedStrings', rid='rId11', chu='xl/workbook.xml')
    if so_sheet == 2:
        p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('</sheets>', '<sheet name="bảng hai" sheetId="2" r:id="rId2"/></sheets>')
        them_phan(p, 'xl/worksheets/sheet2.xml', f'<worksheet xmlns="{S}"><sheetData>' + noi_dung + '</sheetData></worksheet>',
                  CT_S + 'worksheet+xml', 'worksheet', rid='rId2', chu='xl/workbook.xml')
    if codec:
        for ten in p:
            p[ten] = p[ten].encode(codec) if isinstance(p[ten], str) else p[ten]
    return goi_office(p, cach=cach, co=0 if cach == 0 else 6)


def moi_vung():
    p = phan_demo(day_du=True)
    for name in ('xl/workbook.xml', 'docProps/app.xml'):
        p[name] = p[name].replace('DEMO 1', 'bảng')
    for ten, value in tuple(p.items()):
        if ten == 'xl/sharedStrings.xml':
            value = value.replace('DEMO Công ty Ánh Dương', TEN).replace('DEMO tên chưa dùng', TEN)
        elif ten == 'xl/worksheets/sheet1.xml':
            value = value.replace('DEMO Trần ', 'Công ty DEMO ').replace('DEMO Nguyễn Lan', TEN).replace('DEMO ô gộp', TEN)
        elif ten == 'docProps/core.xml':
            value = value.replace('DEMO hồ sơ Ánh Dương', TEN).replace('DEMO Nguyễn Lan', TEN).replace('DEMO Trần Hà', TEN)
        elif ten == 'docProps/app.xml':
            value = value.replace('Microsoft Excel', 'công cụ').replace('DEMO Trần Minh', TEN).replace('DEMO Ánh Dương', TEN)
        elif ten == 'docProps/custom.xml':
            value = value.replace('DEMO chủ hồ sơ', TEN).replace('DEMO Lê Hạ', TEN)
            value = value.replace('DEMO ngày', TEN + '; thuộc tính')
        p[ten] = value
    return goi_office(p)
