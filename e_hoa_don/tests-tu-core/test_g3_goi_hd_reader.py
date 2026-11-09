"""G3-GOI-22: bridge reader/Issue, hash legacy, XML DEMO và import thuần.

Các hash ghim (Issue, hash_vao có context, hash_du_lieu(context)) đã đo bằng
Python (hash_du_lieu) ở commit cha của lát, trước khi chuyển reader; sau lát
phải giữ nguyên nhờ __module__ legacy của các lớp reader (G3-GOI §6.3).
"""

import ast
from dataclasses import fields
from decimal import Decimal
import hashlib
import importlib
import importlib.util
from pathlib import Path
import pickle
import subprocess
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = 'kho_tri_thuc.engines.e_hoa_don.lib'
LIB = ROOT / 'engines/e_hoa_don/lib'
FIX = ROOT / 'tests/fixtures/m2_invoice_xml/inputs/G01-wrapped-positive.xml'
ISSUE_MODULE_TRUOC = 'kho_tri_thuc.nguon.fixture'
# Đối tượng: {'issue': Issue('DEMO', 'Dữ liệu giả.')} với mặc định $/ERROR.
HASH_ISSUE_TRUOC = '56a7e83982610fb27b1357b9ecb0b6c15c7bd877a7ef3b2e91a2370b1dd4ea61'
# Đo ở commit cha của lát (G01-wrapped-positive.xml, ctx_obs('O_G01'), thoi_diem 2026-01-01 UTC).
HASH_CTX_TRUOC = '32ade9ca521f731efc11f1d263f3c3018bdb2661218905f20e11396a7cb47889'
HASH_VAO_CTX_TRUOC = 'e842e8a57e67151d6f2dc29f643cc010d5a1c2773cd4177772183047e49134d4'


class BridgeReaderTests(unittest.TestCase):
    def test_module_ham_dto_va_globals_patch_cung_object(self):
        cu = importlib.import_module('kho_tri_thuc.nguon.hoa_don_xml')
        moi = importlib.import_module(PACKAGE + '.hoa_don_xml')
        self.assertIs(cu, moi)
        self.assertEqual(Path(cu.__file__).resolve(), LIB / 'hoa_don_xml.py')
        for ten, value in vars(moi).items():
            if not ten.startswith('__'):
                with self.subTest(ten=ten):
                    self.assertIs(getattr(cu, ten), value)
        with patch.object(cu, '_doc', return_value='Dữ liệu giả') as doc:
            self.assertEqual(moi.doc_hoa_don_xml(b'DEMO'), 'Dữ liệu giả')
            doc.assert_called_once()

    def test_data_error_decimal_va_primitives_cung_object(self):
        from kho_tri_thuc.ha_tang import primitives as cu
        from kho_tri_thuc.sdk_core import primitives as sdk
        moi = importlib.import_module(PACKAGE + '.hoa_don_xml')
        self.assertIs(moi.Decimal, Decimal)
        for ten in ('DataError', 'canonical_json', 'date_iso', 'sha256'):
            self.assertIs(getattr(moi, ten), getattr(sdk, ten))
            self.assertIs(getattr(moi, ten), getattr(cu, ten))
        with self.assertRaises(cu.DataError):
            moi.doc_hoa_don_xml('DEMO')

    def test_issue_goc_cung_class_giu_module_defaults_va_pickle(self):
        from kho_tri_thuc.nguon.fixture import Issue as cu
        from kho_tri_thuc.sdk_core.engine_legacy import Issue
        self.assertIs(cu, Issue)
        self.assertEqual(Issue.__module__, ISSUE_MODULE_TRUOC)
        self.assertEqual([f.name for f in fields(Issue)],
                         ['code', 'message', 'locator', 'severity'])
        value = Issue('DEMO', 'Dữ liệu giả.')
        self.assertEqual((value.locator, value.severity), ('$', 'ERROR'))
        self.assertIs(type(pickle.loads(pickle.dumps(value))), Issue)
        value.message = 'Issue vẫn mutable.'
        self.assertEqual(value.message, 'Issue vẫn mutable.')

    def test_hash_doi_tuong_chua_issue_giu_gia_tri_truoc_lat(self):
        from kho_tri_thuc.nguon.fixture import Issue
        from kho_tri_thuc.sdk_core.engine_legacy import hash_du_lieu
        self.assertEqual(hash_du_lieu({'issue': Issue('DEMO', 'Dữ liệu giả.')}),
                         HASH_ISSUE_TRUOC)

    def test_hash_context_va_hash_vao_engine_giu_gia_tri_truoc_lat(self):
        from datetime import datetime, timezone
        from test_hoa_don_xml import ctx_obs
        from kho_tri_thuc.ha_tang.engine import hash_du_lieu
        from kho_tri_thuc.ha_tang.engine_hoa_don import DauVaoHoaDon, EngineHoaDon
        moi = importlib.import_module(PACKAGE + '.hoa_don_xml')
        for ten in ('InvoiceReadContext', 'InvoiceReadResult', 'CompanyFact', 'InvoiceIssue'):
            self.assertEqual(getattr(moi, ten).__module__, 'kho_tri_thuc.nguon.hoa_don_xml')
        context = ctx_obs('O_G01')
        self.assertEqual(hash_du_lieu(context), HASH_CTX_TRUOC)
        ket = EngineHoaDon().chay(DauVaoHoaDon(FIX.read_bytes(), context, FIX.name),
                                  thoi_diem=datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(ket.bang_chung.hash_vao, HASH_VAO_CTX_TRUOC)

    def test_as_issue_tra_object_moi_moi_lan(self):
        from kho_tri_thuc.nguon.fixture import Issue
        moi = importlib.import_module(PACKAGE + '.hoa_don_xml')
        snapshot = moi.InvoiceIssue('DEMO', 'Dữ liệu giả.', '/DEMO', 'WARNING')
        a, b = snapshot.as_issue(), snapshot.as_issue()
        self.assertIs(type(a), Issue)
        self.assertIs(type(b), Issue)
        self.assertIsNot(a, b)
        self.assertEqual(a, b)
        a.message = 'Đã sửa bản chuyển đổi.'
        self.assertEqual((b.message, snapshot.message), ('Dữ liệu giả.', 'Dữ liệu giả.'))

    def test_reader_chep_nguyen_chi_doi_hai_import(self):
        # Chỉ thay 2 import sang SDK + khối giữ __module__ legacy cuối tệp; chuẩn LF.
        source = (LIB / 'hoa_don_xml.py').read_text(encoding='utf-8')
        self.assertEqual(hashlib.sha256(source.encode('utf-8')).hexdigest(),
                         '2a757150d69ef24d7369621b22f6c25895867005ca167655813c91700e600f2b')

    def test_xml_demo_giu_golden_decimal_raw_va_dto_qua_bridge(self):
        from test_hoa_don_xml import CONTENT, IDENTITY, ctx_obs
        cu = importlib.import_module('kho_tri_thuc.nguon.hoa_don_xml')
        moi = importlib.import_module(PACKAGE + '.hoa_don_xml')
        raw = FIX.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         '863ce3c1330ce67e6a41e74699f2ac378dbb574d03afa5d8257ce0d23c15fe97')
        context = ctx_obs('O_G01')
        a = cu.doc_hoa_don_xml(raw, context, artifact_name=FIX.name)
        b = moi.doc_hoa_don_xml(raw, context, artifact_name=FIX.name)
        self.assertIs(type(a), moi.InvoiceReadResult)
        self.assertEqual(a, b)
        self.assertEqual(cu.ra_json(a), moi.ra_json(b))
        self.assertIs(a.raw_xml, raw)
        self.assertEqual(a.raw_ref, moi.XmlRawRef(moi.sha256(raw), len(raw)))
        self.assertEqual(a.canonical_identity, IDENTITY['I_G01_A'])
        self.assertEqual(a.semantic_envelope.ra_dict(), CONTENT['C_G01']['envelope'])
        self.assertEqual(a.semantic_digest, CONTENT['C_G01']['semantic_sha256'])
        self.assertEqual((a.shape, a.issues, a.candidate_reasons), ('SUPPORTED_SUBSET', (), ()))
        line = a.lines[0]
        self.assertIs(type(line.quantity.exact_value), Decimal)
        self.assertEqual(line.quantity.exact_value, Decimal('10'))
        self.assertEqual(line.unit_price.exact_value.as_tuple(), Decimal('12.500000').as_tuple())
        self.assertEqual(line.source_amount.exact_value.as_tuple(), Decimal('125.000000').as_tuple())
        mutable = bytearray(raw)
        snapshot = moi.doc_hoa_don_xml(mutable, context)
        mutable[0] = 0
        self.assertIs(type(snapshot.raw_xml), bytes)
        self.assertEqual(snapshot.raw_xml, raw)


class ImportReaderTests(unittest.TestCase):
    def test_ast_loi_reader_chi_stdlib_va_sdk_ke_ca_lazy_import(self):
        stdlib = {'__future__', 'io', 're', 'zipfile', 'zlib', 'dataclasses',
                  'decimal', 'typing', 'xml', 'lzma', 'types'}
        for path in sorted(LIB.rglob('*.py')):
            with self.subTest(tep=path.name):
                tree = ast.parse(path.read_text(encoding='utf-8'))
                for node in ast.walk(tree):
                    names = []
                    if isinstance(node, ast.Import):
                        names = [a.name for a in node.names]
                    elif isinstance(node, ast.ImportFrom):
                        name = node.module or ''
                        if node.level:
                            name = importlib.util.resolve_name('.' * node.level + name, PACKAGE)
                        names = [name]
                    for name in names:
                        self.assertTrue(name.split('.')[0] in stdlib
                                        or name.startswith('kho_tri_thuc.sdk_core.')
                                        or name == PACKAGE + '.hoa_don_xml', name)
                    if isinstance(node, ast.Call):
                        fn = node.func
                        self.assertFalse(isinstance(fn, ast.Name) and fn.id == '__import__')
                        self.assertFalse(isinstance(fn, ast.Attribute) and fn.attr == 'import_module')

    def test_import_dau_tien_moi_module_trong_tien_trinh_co_lap(self):
        # §6.3.2: mỗi module phải là import ứng dụng ĐẦU TIÊN, không tái dùng process.
        modules = ('kho_tri_thuc.ha_tang.primitives', 'kho_tri_thuc.ha_tang.engine',
                   'kho_tri_thuc.nguon.trich6_host', 'kho_tri_thuc.core.viec')
        for name in modules:
            with self.subTest(module=name):
                code = ('import sys; sys.path.insert(0, ' + repr(str(ROOT / 'src')) + '); '
                        'import importlib; importlib.import_module(' + repr(name) + ')')
                result = subprocess.run([sys.executable, '-I', '-X', 'utf8', '-B', '-c', code],
                                        cwd=ROOT, capture_output=True, text=True,
                                        encoding='utf-8', timeout=30)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
