"""G3-GOI-23: ánh xạ trạng thái engine hóa đơn ở lib/trang_thai.py, cùng identity, hash không đổi."""

import ast
from datetime import datetime, timezone
import importlib
import importlib.util
from lzma import LZMAError
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = 'kho_tri_thuc.engines.e_hoa_don.lib'
LIB_TRANG_THAI = ROOT / 'engines/e_hoa_don/lib/trang_thai.py'
FIX = ROOT / 'tests/fixtures/m2_invoice_xml/inputs/G01-wrapped-positive.xml'

# Đo ở commit cha của lát (G01-wrapped-positive.xml, ctx_obs('O_G01'), thoi_diem 2026-01-01 UTC).
HASH_VAO_CTX = 'e842e8a57e67151d6f2dc29f643cc010d5a1c2773cd4177772183047e49134d4'
HASH_RA_CTX = 'd50176894849625b2c22ea6da80dfd61384ac2749782e655bf1c2722ae4c6363'
HASH_VAO_NONE = 'fc20cfda982b190810fd6d3d505868d870ee703bfa1a127b275a96d75a19e4d4'
HASH_RA_NONE = 'd2d3184288f201830661535de96bf0b20614dfd9c46a5693e3e2fb59abf5ec34'
HASH_BANG_CHUNG_CTX = '87288148a529365cd011a8a455dae2c99d90fc6972bd472ee05483983d845571'
HASH_BANG_CHUNG_NONE = '347c68599e4ef1b84091ff904c453f58566cc390e31819ee8e7bce4eef6013e9'
HASH_DU_LIEU_CTX = 'bb9475417f0f45e72ea5682e4728c5345c8722431bb5977dac2dda3a9493cc89'


class IdentityTests(unittest.TestCase):
    def test_enum_cung_object_qua_moi_duong_import(self):
        from kho_tri_thuc.ha_tang import engine as cu
        from kho_tri_thuc.sdk_core import engine_legacy as sdk
        moi = importlib.import_module(PACKAGE + '.trang_thai')
        self.assertIs(moi.TrangThaiEngine, sdk.TrangThaiEngine)
        self.assertIs(cu.TrangThaiEngine, sdk.TrangThaiEngine)
        self.assertEqual(sdk.TrangThaiEngine.__module__, 'kho_tri_thuc.ha_tang.engine')
        self.assertEqual(sum(1 for v in vars(moi).values()
                             if isinstance(v, type) and v.__name__ == 'TrangThaiEngine'), 1)

    def test_bang_anh_xa_va_ham_cung_object_voi_adapter_va_doc(self):
        from kho_tri_thuc.ha_tang import engine_hoa_don as adapter
        moi = importlib.import_module(PACKAGE + '.trang_thai')
        doc = importlib.import_module('kho_tri_thuc.engines.e_hoa_don.doc')
        for ten in ('ANH_XA_MA_DATAERROR_HOA_DON', 'ANH_XA_NGOAI_LE_HOA_DON',
                    '_trang_thai_xml', '_trang_thai_zip', '_THIEU_CONTEXT', '_LOI_GOI'):
            with self.subTest(ten=ten):
                self.assertIs(getattr(adapter, ten), getattr(moi, ten))
        self.assertIs(doc.ANH_XA_NGOAI_LE_HOA_DON, moi.ANH_XA_NGOAI_LE_HOA_DON)
        self.assertIs(doc._trang_thai_xml, moi._trang_thai_xml)

    def test_ngoai_le_lzma_va_ma_dataerror_giu_nguyen(self):
        moi = importlib.import_module(PACKAGE + '.trang_thai')
        from kho_tri_thuc.ha_tang.primitives import DataError
        from kho_tri_thuc.sdk_core import primitives as sdk
        self.assertIs(DataError, sdk.DataError)
        self.assertEqual(set(moi.ANH_XA_NGOAI_LE_HOA_DON), {LZMAError})
        self.assertEqual(moi.ANH_XA_NGOAI_LE_HOA_DON[LZMAError][1], 'HOADON_ZIP_LZMA_HONG')
        self.assertEqual(set(moi.ANH_XA_MA_DATAERROR_HOA_DON),
                         {'INPUT_NOT_BYTES', 'INPUT_NAME_TYPE', 'CONTEXT_FIELD_TYPE'})


class ImportTests(unittest.TestCase):
    def test_ast_trang_thai_khong_import_ha_tang_core_nguon(self):
        tree = ast.parse(LIB_TRANG_THAI.read_text(encoding='utf-8'))
        da_thay = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                name = node.module or ''
                if node.level:
                    name = importlib.util.resolve_name('.' * node.level + name, PACKAGE)
                names = [name]
            else:
                continue
            da_thay += names
            for name in names:
                self.assertFalse(name.startswith(('kho_tri_thuc.ha_tang', 'kho_tri_thuc.core',
                                                  'kho_tri_thuc.nguon')), name)
        self.assertIn('kho_tri_thuc.sdk_core.engine_legacy', da_thay)

    def test_trang_thai_khong_dinh_nghia_lop(self):
        tree = ast.parse(LIB_TRANG_THAI.read_text(encoding='utf-8'))
        self.assertEqual([n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)], [])


class HashTests(unittest.TestCase):
    def test_hash_bang_chung_engine_khong_doi(self):
        from test_hoa_don_xml import ctx_obs
        from kho_tri_thuc.ha_tang.engine import hash_du_lieu
        from kho_tri_thuc.ha_tang.engine_hoa_don import DauVaoHoaDon, EngineHoaDon
        raw = FIX.read_bytes()
        t = datetime(2026, 1, 1, tzinfo=timezone.utc)
        e = EngineHoaDon()
        k = e.chay(DauVaoHoaDon(raw, ctx_obs('O_G01'), 'G01-wrapped-positive.xml'), thoi_diem=t)
        k2 = e.chay(DauVaoHoaDon(raw, None, 'G01-wrapped-positive.xml'), thoi_diem=t)
        self.assertEqual((k.trang_thai.value, k.ma), ('XONG', 'DA_DOC_HOA_DON'))
        self.assertEqual((k2.trang_thai.value, k2.ma), ('CHO', 'CONTEXT_ABSENT'))
        self.assertEqual(k.bang_chung.hash_vao, HASH_VAO_CTX)
        self.assertEqual(k.bang_chung.hash_ra, HASH_RA_CTX)
        self.assertEqual(k2.bang_chung.hash_vao, HASH_VAO_NONE)
        self.assertEqual(k2.bang_chung.hash_ra, HASH_RA_NONE)
        self.assertEqual(hash_du_lieu(k.bang_chung), HASH_BANG_CHUNG_CTX)
        self.assertEqual(hash_du_lieu(k2.bang_chung), HASH_BANG_CHUNG_NONE)
        self.assertEqual(hash_du_lieu(k.du_lieu), HASH_DU_LIEU_CTX)


if __name__ == '__main__':
    unittest.main()
