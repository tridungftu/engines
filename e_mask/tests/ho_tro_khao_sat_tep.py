"""MASK-7: fixture DEMO trong RAM và nạp nguồn repo, không phải parser sản phẩm."""
import ast
import importlib.util
import io
from pathlib import Path
import re
import sys
from types import ModuleType
import zipfile
import xml.etree.ElementTree as ET

NGUON = Path(__file__).resolve().parents[1] / 'ma-nguon/nguon/privacy'
TEN = 'DEMO_ANH_DUONG'
TOKEN = '[KHAC_001]'  # Đúng khuôn nguồn cũ, không giả đã port sang [[...]].
RULES = [{'source': TEN, 'token': TOKEN, 'category': 'KHAC', 'enabled': True}]
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'


def nap_nguon():
    """Chạy nguyên Excel/revisions; core chỉ nạp closure stdlib bằng AST.

    Không import core cũ đầy đủ (crypto/docx chưa ghim). Năm định nghĩa giữ
    nguyên AST từ repo; không thay matcher/validate_rules, không mock kết quả.
    make_docx chỉ khảo sát tĩnh, KHÔNG chạy trong harness này.
    """
    ten_goi = '_mask7_khao_sat'
    if ten_goi + '.excel' in sys.modules:
        return tuple(sys.modules[ten_goi + '.' + n] for n in ('excel', 'excel_values', 'docx_revisions'))
    goi = ModuleType(ten_goi)
    goi.__path__ = [str(NGUON)]
    sys.modules[ten_goi] = goi

    def nap(ten):
        spec = importlib.util.spec_from_file_location(ten_goi + '.' + ten, NGUON / (ten + '.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        return mod

    loai = nap('types')
    core = ModuleType(ten_goi + '.core')
    core.__dict__.update(re=re, normalize=loai.normalize, PrivacyError=loai.PrivacyError)
    cay = ast.parse((NGUON / 'core.py').read_text(encoding='utf-8'))
    chon = {'CATEGORIES', 'TOKEN', 'key', 'literal_pattern', 'validate_rules'}
    dinh_nghia = [n for n in cay.body if
                 (isinstance(n, ast.FunctionDef) and n.name in chon) or
                 (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in chon for t in n.targets))]
    assert len(dinh_nghia) == len(chon)
    exec(compile(ast.Module(body=dinh_nghia, type_ignores=[]), '<nguon-core-repo-MASK-7>', 'exec'), core.__dict__)
    sys.modules[core.__name__] = core
    return nap('excel'), nap('excel_values'), nap('docx_revisions')


def dong_zip(parts):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for ten, data in parts.items():
            info = zipfile.ZipInfo(ten, (2000, 1, 1, 0, 0, 0))
            z.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED)
    return out.getvalue()


def mo_zip(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        return {n: z.read(n) for n in z.namelist()}


def word_demo(chu=TEN):
    def xml(vung, noi_dung):
        return f'<w:{vung} xmlns:w="{W}">{noi_dung}</w:{vung}>'
    doan = f'<w:p><w:r><w:t>{chu}</w:t></w:r></w:p>'
    parts = {f'word/{ten}.xml': xml(vung, doan) for ten, vung in
             [('header1', 'hdr'), ('footer1', 'ftr'), ('footnotes', 'footnotes'),
              ('endnotes', 'endnotes'), ('comments', 'comments')]}
    parts['word/document.xml'] = xml('document', '<w:body>' + doan +
        f'<w:ins>{doan}</w:ins><w:del><w:r><w:delText>{TEN}</w:delText></w:r></w:del></w:body>')
    parts['docProps/core.xml'] = f'<p xmlns="urn:DEMO"><author>{TEN}</author></p>'
    return dong_zip(parts)  # OOXML tối giản để thử helper, không chứng nhận Word mở được.


def excel_demo(chu=TEN):
    _, values, _ = nap_nguon()
    # Chia nhỏ ô theo fixture, không cắt nội dung. Không dùng fallback này làm sản phẩm.
    cells = [(i + 1, 1, 's', chu[a:a + 1000], None) for i, a in enumerate(range(0, len(chu), 1000))]
    cells += [(1, 2, 'n', '1000000', 'grouped'), (1, 3, 'n', '46325', 'date'),
              (1, 4, 's', 'VND; 2026-10-30; DEMO', None)]
    return values.build_values_workbook({'sheets': [{'name': 'DEMO', 'state': 'visible', 'cells': cells}]})


def chu_xml(data):
    """Đếm ký tự text/tail XML sau giải mã, không đếm markup/attribute."""
    tong = 0
    for ten, raw in mo_zip(data).items():
        if ten.endswith('.xml'):
            tong += sum(len(t) for t in ET.fromstring(raw).itertext())
    return tong


def so_zip(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        ds = z.infolist()
        return {'byte_zip': len(data), 'byte_nen_thanh_vien': sum(i.compress_size for i in ds),
                'byte_giai_nen': sum(i.file_size for i in ds), 'so_phan': len(ds),
                'phan_lon_nhat': max(i.file_size for i in ds),
                'ty_le_phan_lon_nhat': round(max(i.file_size / max(1, i.compress_size) for i in ds), 3)}
