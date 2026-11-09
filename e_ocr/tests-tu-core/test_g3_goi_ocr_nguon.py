"""G3-GOI-17: nguồn OCR nội bộ, SHA byte gốc và import cô lập; chỉ DEMO/mock.

Không đọc thư mục công cụ cũ, không cài thư viện, không ghi/xóa tệp thử.
Ca mock kiểm closure import; ca DOCX cần đúng dependency thật, thiếu thì skip.
"""

import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import textwrap
import unittest


GOC = Path(__file__).resolve().parents[1]
GOI = GOC / 'engines/e_ocr'
VENDOR = GOI / 'vendor/mask_ocr'
XAC_NHAN = 'phần mềm nội bộ, Anh xác nhận 06/11/2026, chỉ dùng nội bộ'
SHA_GOC = {
    '__init__.py': 'd7c4302994002b7f2fc4b4986645e83115d7dfd4c0669004d5f0c107c0a0e2e6',
    'extraction.py': 'f573bb79a436fd2e968a4e8376b3128a973e81bed28d8398f1abdf6c092589a8',
    'layout.py': 'ae8f1310dfc4698c559bb15f56aae7d31389a675fa4924235b2b956b2da29a33',
    'common.py': 'e7daf60ac470ad47586e25ba5acdd0440246c52d22184bc7c39d5986f48791b7',
    'runtime.py': 'add0d540d63c5d01d47f00ae7faafc851d9b3dc13115fd905ca1a9eeb0916558',
}

# Chỉ bootstrap package đang kiểm, không thêm repo/src, SDK hay engine khác.
# -I -S loại PYTHONPATH, cwd và site-packages; ca thật thêm đúng hai dependency.
NHAP_CO_LAP = r'''
import importlib, importlib.abc, importlib.util, io, json, os
from pathlib import Path
import sys, types, zipfile

goi = Path(sys.argv[1]).resolve()
che_do = sys.argv[2]
sys.path.extend(json.loads(sys.argv[3]))
path_cu = sys.path[:]

class ChanNguonCu(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'mask_ocr', 'kho_tri_thuc', 'kho_tri_thuc_sdk'}:
            raise AssertionError('Không được nạp nguồn ngoài gói: ' + fullname)

sys.meta_path.insert(0, ChanNguonCu())

def kiem_io(event, args):
    if event in {'subprocess.Popen', 'os.system', 'socket.connect', 'socket.bind'}:
        raise AssertionError('Import/parser không được chạy tiến trình hoặc mạng')
    if event == 'open':
        path, mode, flags = args
        if isinstance(path, (str, bytes, os.PathLike)):
            ten = os.fsdecode(path).replace('\\', '/').lower()
            if 'd:/gpt/' in ten or ten.endswith(('.json', '.toml', '.traineddata')):
                raise AssertionError('Không được đọc nguồn/cấu hình/model ngoài gói')
        if (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (
            isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT)
        ):
            raise AssertionError('Ca kiểm chỉ đọc')

sys.addaudithook(kiem_io)
if che_do == 'mock':
    # Chỉ mock dependency ngoài; không thay parser hay hàm nội bộ được kiểm.
    sys.modules['pymupdf'] = types.ModuleType('pymupdf')
    xml = types.ModuleType('defusedxml')
    xml.ElementTree = types.ModuleType('ElementTree')
    sys.modules['defusedxml'] = xml

spec = importlib.util.spec_from_file_location(
    'e_ocr', goi / '__init__.py', submodule_search_locations=[str(goi)])
package = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = package
spec.loader.exec_module(package)
modules = {}
for name in ('__init__', 'common', 'extraction', 'layout', 'runtime'):
    fullname = 'e_ocr.vendor.mask_ocr' + ('.' + name if name != '__init__' else '')
    module = importlib.import_module(fullname)
    assert Path(module.__file__).resolve().parent == goi / 'vendor/mask_ocr'
    modules[name] = module
assert not any(n == 'mask_ocr' or n.startswith('mask_ocr.') for n in sys.modules)
assert not any(n.startswith('kho_tri_thuc') for n in sys.modules)
assert sys.path == path_cu
assert modules['__init__'].Extracted is modules['common'].Extracted
assert modules['extraction'].Extracted is modules['common'].Extracted
assert modules['runtime'].ExtractionError is modules['common'].ExtractionError
assert modules['layout'].paragraph_text is modules['extraction'].paragraph_text
assert modules['common'].normalize('a\u0301\x00 0007 06/11/2026') == 'á 0007 06/11/2026'
'''

DOCX_DEMO = r'''
extraction, layout = modules['extraction'], modules['layout']
w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def paragraph(text):
    return '<w:p><w:r><w:t>' + text + '</w:t></w:r></w:p>'
def cell(text='', props=''):
    return '<w:tc><w:tcPr>' + props + '</w:tcPr>' + paragraph(text) + '</w:tc>'
def docx(body):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        z.writestr('[Content_Types].xml', '<Types/>')
        z.writestr('word/document.xml',
                   '<w:document xmlns:w="' + w + '"><w:body>' + body + '</w:body></w:document>')
    return buf.getvalue()
def khong_ocr(_):
    raise AssertionError('DOCX DEMO không được gọi OCR ảnh')
'''


class NguonOCRTests(unittest.TestCase):
    def test_quyen_noi_bo_va_tap_tep_toi_thieu(self):
        nguon = (GOI / 'NGUON.md').read_text(encoding='utf-8')
        self.assertIn(XAC_NHAN, nguon)
        self.assertIn('local-mask-ocr', nguon)
        self.assertIn('2.1.0', nguon)
        self.assertIn(r'D:\GPT\OCR\mask_ocr', nguon)
        self.assertEqual((VENDOR / 'LICENSE').read_text(encoding='utf-8').strip(), XAC_NHAN)
        self.assertEqual({p.name for p in VENDOR.iterdir()}, {*SHA_GOC, 'LICENSE'})
        self.assertTrue((GOI / 'vendor/__init__.py').is_file())

    def test_sha256_byte_thuc_khop_nguon_md(self):
        nguon = (GOI / 'NGUON.md').read_text(encoding='utf-8')
        rows = re.findall(
            r'^\| `vendor/mask_ocr/([^`]+\.py)` \| `([a-f0-9]{64})` \| `([a-f0-9]{64})` \|$',
            nguon, re.MULTILINE)
        self.assertEqual(len(rows), len(SHA_GOC))
        self.assertEqual({ten: sha for ten, sha, _ in rows}, SHA_GOC)
        for ten, _, sha_goi in rows:
            with self.subTest(tep=ten):
                self.assertEqual(hashlib.sha256((VENDOR / ten).read_bytes()).hexdigest(), sha_goi)

    def test_chi_doi_cau_hien_thi_giu_nguyen_thuat_toan(self):
        for ten, sha in SHA_GOC.items():
            raw = (VENDOR / ten).read_bytes()
            if ten == 'extraction.py':
                cu = 'Nội dung đọc được vẫn được đưa ra để Anh kiểm tra.'
                moi = 'Nội dung đọc được vẫn được đưa ra để kiểm tra.'
                self.assertEqual(raw.count(moi.encode('utf-8')), 1)
                self.assertNotIn(cu.encode('utf-8'), raw)
                raw = raw.replace(moi.encode('utf-8'), cu.encode('utf-8'))
            self.assertEqual(hashlib.sha256(raw).hexdigest(), sha, ten)

    def test_closure_ke_ca_lazy_import_chi_dung_thu_vien_da_ghim(self):
        files = [GOI / 'vendor/__init__.py', *sorted(VENDOR.glob('*.py'))]
        for tep in files:
            tree = ast.parse(tep.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                with self.subTest(tep=tep.name, dong=getattr(node, 'lineno', 0)):
                    if isinstance(node, ast.ImportFrom) and node.level:
                        self.assertEqual(node.level, 1)
                        self.assertIn(node.module, {'common', 'extraction', 'runtime'})
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        names = ([n.name for n in node.names] if isinstance(node, ast.Import)
                                 else [node.module])
                        for name in names:
                            self.assertIn(name.split('.')[0],
                                          sys.stdlib_module_names | {'pymupdf', 'defusedxml'})
                    elif isinstance(node, ast.Call):
                        ham = node.func
                        self.assertFalse(isinstance(ham, ast.Name) and ham.id == '__import__')
                        self.assertFalse(isinstance(ham, ast.Attribute) and ham.attr == 'import_module')
                    elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                        self.assertIsNone(re.search(r'(?<![A-Za-z])[A-Za-z]:[/\\]', node.value))
                        self.assertNotIn('KTT_NGUON_OCR', node.value)

    def _chay_co_lap(self, *, mock=False, them=''):
        deps = []
        if not mock:
            for name in ('pymupdf', 'defusedxml'):
                spec = importlib.util.find_spec(name)
                if spec is None:
                    self.skipTest('CHUA_KIEM dependency thật: thiếu ' + name + '; không cài thêm')
                deps.append(str(Path(spec.origin).resolve().parent.parent))
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
                   KTT_NGUON_OCR='DEMO-nguon-cu-khong-duoc-doc',
                   LOCAL_OCR_DUAL_CONFIG='DEMO-cau-hinh-khong-duoc-doc.json')
        env.pop('PYTHONPATH', None)
        result = subprocess.run(
            [sys.executable, '-I', '-S', '-X', 'utf8', '-B', '-c',
             textwrap.dedent(NHAP_CO_LAP) + textwrap.dedent(them),
             str(GOI), 'mock' if mock else 'that', json.dumps(sorted(set(deps)))],
            cwd=sys.prefix, env=env, capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_import_co_lap_mock_khong_phu_thuoc_cong_cu_cu(self):
        self._chay_co_lap(mock=True)

    def test_import_co_lap_dependency_that(self):
        self._chay_co_lap()

    def test_docx_demo_giu_chu_viet_o_rong_o_gop_va_dinh_vi(self):
        self._chay_co_lap(them=DOCX_DEMO + r'''
props = '<w:gridSpan w:val="2"/><w:vMerge w:val="restart"/>'
rows = '<w:tr>' + cell('Gộp', props) + cell('0007') + '</w:tr>'
rows += '<w:tr>' + cell('', '<w:gridSpan w:val="2"/><w:vMerge/>') + cell() + '</w:tr>'
raw = docx(paragraph('DEMO Ánh Dương, 1.000.000 VND, 06/11/2026') +
           '<w:tbl><w:tblGrid>' + '<w:gridCol w:w="1440"/>' * 3 + '</w:tblGrid>' + rows + '</w:tbl>')
legacy = extraction.extract_docx(raw, image_reader=khong_ocr)
page = layout.word_layout(raw, legacy, embedded_pages=[])
assert 'Ánh Dương, 1.000.000 VND, 06/11/2026' in legacy.text
assert '0007' in legacy.text and legacy.ocr_pages == 0
table = page['blocks'][1]
assert (table['rows'], table['cols'], len(table['cells'])) == (2, 3, 3)
assert (table['cells'][0]['rowspan'], table['cells'][0]['colspan']) == (2, 2)
assert table['cells'][2]['unit_ids'] == []
assert len({unit['id'] for unit in page['units']}) == len(page['units'])
''')

    def test_docx_demo_loi_bi_tu_choi_khong_goi_ocr(self):
        self._chay_co_lap(them=DOCX_DEMO + r'''
bad = [docx('<w:ins>' + paragraph('DEMO') + '</w:ins>'),
       docx('<w:tbl><w:tr><w:tc><w:tbl/></w:tc></w:tr></w:tbl>'), b'DEMO DOCX hong']
for raw in bad:
    try:
        extraction.extract_docx(raw, image_reader=khong_ocr)
    except (modules['common'].ExtractionError, zipfile.BadZipFile):
        pass
    else:
        raise AssertionError('Không được nhận thành công tài liệu lỗi')
''')


if __name__ == '__main__':
    unittest.main()
