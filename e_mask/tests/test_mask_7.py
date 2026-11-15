"""Bằng chứng giới hạn nguồn cũ; test đạt không chứng nhận che tệp vận hành."""
import ast
import io
import json
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

import pytest
from ho_tro_khao_sat_tep import (NGUON, RULES, TEN, TOKEN, W, S, R, chu_xml,
                               dong_zip, excel_demo, mo_zip, nap_nguon, so_zip, word_demo)


def test_word_chi_dung_moi_khong_nhan_docx_goc():
    cay = ast.parse((NGUON / 'core.py').read_text(encoding='utf-8'))
    ham = next(n for n in cay.body if isinstance(n, ast.FunctionDef) and n.name == 'make_docx')
    assert [a.arg for a in ham.args.args] == ['text']
    assert any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and
               n.func.id == 'Document' and not n.args for n in ast.walk(ham))


def test_word_accept_khong_che_bat_ky_vung_nao():
    _, _, rev = nap_nguon()
    goc = word_demo()
    out, dem = rev.accept_tracked_changes(goc)
    assert dem == 2
    parts = mo_zip(out)
    for ten in ['document', 'header1', 'footer1', 'footnotes', 'endnotes', 'comments']:
        assert TEN.encode() in parts[f'word/{ten}.xml']
    assert TEN.encode() in parts['docProps/core.xml']
    assert b'delText' not in parts['word/document.xml']


@pytest.mark.parametrize('loai', ['hong', 'duong_di', 'entity', 'trung'])
def test_word_khong_an_toan_tra_nguyen_byte(loai):
    _, _, rev = nap_nguon()
    if loai == 'hong':
        data = b'DEMO khong phai ZIP'
    else:
        parts = mo_zip(word_demo())
        if loai == 'duong_di':
            parts['../DEMO.xml'] = '<DEMO/>'
        elif loai == 'entity':
            parts['word/document.xml'] = f'<!DOCTYPE demo [<!ENTITY x "DEMO">]><w:ins xmlns:w="{W}">&x;</w:ins>'
        data = dong_zip(parts)
        if loai == 'trung':
            out = io.BytesIO(data)
            with pytest.warns(UserWarning), zipfile.ZipFile(out, 'a') as z:
                z.writestr('word/document.xml', '<DEMO/>')
            data = out.getvalue()
    assert rev.accept_tracked_changes(data) == (data, 0)


@pytest.mark.parametrize('vung', ['sheet_an', 'o_an', 'binh_luan', 'thuoc_tinh'])
def test_excel_che_vung_ho_tro(vung):
    excel, _, _ = nap_nguon()
    parts = mo_zip(excel_demo())
    if vung == 'sheet_an':
        parts['xl/workbook.xml'] = parts['xl/workbook.xml'].replace(b'sheetId="1"', b'sheetId="1" state="veryHidden"')
    if vung == 'o_an':
        parts['xl/worksheets/sheet1.xml'] = parts['xl/worksheets/sheet1.xml'].replace(
            b'<sheetData>', b'<cols><col min="1" max="1" hidden="1"/></cols><sheetData>').replace(b'<row r="1">', b'<row r="1" hidden="1">')
    if vung == 'binh_luan':
        parts['xl/comments/comment1.xml'] = f'<comments xmlns="{S}"><authors><author>{TEN}</author></authors><commentList><comment ref="A1" authorId="0"><text><r><t>{TEN}</t></r></text></comment></commentList></comments>'
    if vung == 'thuoc_tinh':
        parts['docProps/core.xml'] = f'<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:creator>{TEN}</dc:creator></cp:coreProperties>'
    wb = excel.ExcelWorkbook(dong_zip(parts), 'DEMO.xlsx')
    kq = wb.mask(RULES)
    assert not kq.blockers and kq.output
    out = mo_zip(kq.output)
    assert all(TEN.encode() not in raw for raw in out.values())
    assert TOKEN.encode() in out['xl/worksheets/sheet1.xml']
    assert b'<v>1000000</v>' in out['xl/worksheets/sheet1.xml']
    assert b'<v>46325</v>' in out['xl/worksheets/sheet1.xml']
    if vung == 'sheet_an':
        assert b'veryHidden' in out['xl/workbook.xml']
    if vung == 'o_an':
        assert out['xl/worksheets/sheet1.xml'].count(b'hidden="1"') == 2


@pytest.mark.parametrize('vung', ['ten_sheet', 'chart'])
def test_excel_vung_chua_che_chan_xuat(vung):
    excel, _, _ = nap_nguon()
    parts = mo_zip(excel_demo())
    if vung == 'ten_sheet':
        parts['xl/workbook.xml'] = parts['xl/workbook.xml'].replace(b'name="DEMO"', f'name="{TEN}"'.encode())
    else:
        parts['xl/charts/chart1.xml'] = f'<chart xmlns="urn:DEMO"><title>{TEN}</title></chart>'
    kq = excel.ExcelWorkbook(dong_zip(parts), 'DEMO.xlsx').mask(RULES)
    assert kq.blockers and kq.output is None
    # Báo cáo cũ có thể chứa nguyên văn: không đưa trực tiếp ra cổng mới.
    if vung == 'ten_sheet':
        assert TEN in json.dumps(kq.blockers)


@pytest.mark.parametrize('vung', ['cong_thuc', 'lien_ket_ngoai'])
def test_excel_disclosure_van_co_the_xuat_dinh_danh(vung):
    excel, _, _ = nap_nguon()
    parts = mo_zip(excel_demo())
    if vung == 'cong_thuc':
        parts['xl/worksheets/sheet1.xml'] = parts['xl/worksheets/sheet1.xml'].replace(
            b'</sheetData>', f'<row r="2"><c r="B2" t="str"><f>"{TEN}"</f><v>{TEN}</v></c></row></sheetData>'.encode())
    else:
        parts['xl/_rels/workbook.xml.rels'] = parts['xl/_rels/workbook.xml.rels'].replace(
            b'</Relationships>', f'<Relationship Id="rExt" Type="{R}/externalLink" Target="externalLinks/externalLink1.xml"/></Relationships>'.encode())
        parts['xl/externalLinks/externalLink1.xml'] = f'<externalLink xmlns="{S}" xmlns:r="{R}"><externalBook r:id="rSrc"><sheetNames><sheetName val="{TEN}"/></sheetNames></externalBook></externalLink>'
        parts['xl/externalLinks/_rels/externalLink1.xml.rels'] = f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rSrc" Type="{R}/externalLinkPath" Target="DEMO/{TEN}.xlsx" TargetMode="External"/></Relationships>'
    kq = excel.ExcelWorkbook(dong_zip(parts), 'DEMO.xlsx').mask(RULES)
    assert not kq.blockers and kq.output and kq.disclosures
    assert TEN in json.dumps(kq.disclosures)
    assert any(TEN.encode() in raw for raw in mo_zip(kq.output).values())


def test_excel_values_cat_o_va_doi_ten_khong_phai_giu_dinh_dang():
    _, values, _ = nap_nguon()
    chu = 'DEMO ' * 7000
    out = values.build_values_workbook({'sheets': [{'name': 'DEMO', 'state': 'visible',
        'cells': [(1, 1, 's', chu, None)]}]})
    root = ET.fromstring(mo_zip(out)['xl/worksheets/sheet1.xml'])
    assert len(root.find(f'.//{{{S}}}t').text) == 32767 < len(chu)
    assert values.safe_sheet_name('[[MASKCT-0001]]', set()) == 'MASKCT-0001'


def test_do_zip_ky_tu_va_chua_co_nang_luc_tep_trong_goi():
    data = word_demo()
    assert so_zip(data)['byte_zip'] == len(data) and chu_xml(data) > 0
    manifest = json.loads((Path(__file__).resolve().parents[1] / 'goi/e_mask/engine.json').read_text(encoding='utf-8'))
    assert {n['ma'] for n in manifest['nang_luc']} == {'mask.che_van_ban@1', 'mask.mo_che_van_ban@1'}
