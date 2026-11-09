"""Kiểm tĩnh gói e_hoa_don bằng stdlib; không import Core, không gọi cổng thuế. Dữ liệu giả."""

import ast
import importlib
from importlib.util import resolve_name
import json
from pathlib import Path
import unittest
from unittest.mock import patch

GOC = Path(__file__).resolve().parents[1]


class GoiTinh(unittest.TestCase):
    def doc(self, ten):
        return json.loads((GOC / ten).read_text(encoding='utf-8'))

    def test_manifest_khop_thu_muc_va_diem_vao(self):
        manifest = self.doc('engine.json')
        self.assertEqual(manifest['ma'], GOC.name)
        entry = manifest['ho_so_chay_mau']['diem_vao']
        self.assertEqual(entry, 'kho_tri_thuc.engines.e_hoa_don.chay')
        self.assertTrue((GOC / (entry.rsplit('.', 1)[1] + '.py')).is_file())

    def test_contract_du_closure_offline(self):
        bundle = self.doc('contract/schemas.json')
        for cap in self.doc('engine.json')['capability']:
            for key in ('dau_vao', 'dau_ra'):
                self.assertIn('urn:ktt:contract:' + cap[key], bundle)
        for identity, schema in bundle.items():
            self.assertEqual(schema['$id'], identity)
        self.assertIn('urn:ktt:contract:chung.v1', bundle)

    def test_vi_du_co_nhan_du_lieu_gia(self):
        self.assertIn('Dữ liệu giả', self.doc('contract/vi_du.json')['luu_y'])

    def test_ma_node_canh_ma_python(self):
        for ten in ('bang_ke.cjs', 'portal.cjs', 'doc.py', 'tai.py', 'phien.py'):
            self.assertTrue((GOC / ten).is_file(), ten)

    def test_chay_phien_chi_qua_sdk_ngoai_le_tuong_minh(self):
        # env_con (chèn đường dự án) lead chốt không chuyển vào SDK; lõi kiểm
        # tiến trình (kiem_tra_tien_trinh) chưa có tương đương SDK.
        ngoai_le = {
            'chay.py': {'kho_tri_thuc.nguon.trich6_host.env_con'},
            'phien.py': {'kho_tri_thuc.core.kiem_tra_tien_trinh.kiem_tra_tien_trinh'},
        }
        cam = ('kho_tri_thuc.ha_tang', 'kho_tri_thuc.nguon', 'kho_tri_thuc.core')
        for ten, cho_phep in ngoai_le.items():
            cay = ast.parse((GOC / ten).read_text(encoding='utf-8'))
            phu_thuoc = set()
            for nut in ast.walk(cay):
                if isinstance(nut, ast.Import):
                    nhap = [a.name for a in nut.names]
                elif isinstance(nut, ast.ImportFrom):
                    mod = nut.module or ''
                    if nut.level:
                        mod = resolve_name('.' * nut.level + mod,
                                           'kho_tri_thuc.engines.e_hoa_don')
                    nhap = [mod + '.' + a.name for a in nut.names]
                else:
                    continue
                phu_thuoc.update(n for n in nhap
                                 if any(n == g or n.startswith(g + '.') for g in cam))
            with self.subTest(tep=ten):
                self.assertEqual(phu_thuoc, cho_phep)


class DoiDuongCungObject(unittest.TestCase):
    def test_ten_doi_duong_la_cung_object(self):
        chay = importlib.import_module('kho_tri_thuc.engines.e_hoa_don.chay')
        phien = importlib.import_module('kho_tri_thuc.engines.e_hoa_don.phien')
        from kho_tri_thuc.core.kiem_tra_goi import KetQuaKiem
        from kho_tri_thuc.ha_tang.primitives import text_id
        from kho_tri_thuc.nguon.trich6_host import _doc_dong
        self.assertIs(chay._doc_dong, _doc_dong)
        self.assertIs(phien.KetQuaKiem, KetQuaKiem)
        self.assertIs(phien.text_id, text_id)

    def test_mac_dinh_chua_kiem_khi_khong_co_kt_that(self):
        phien = importlib.import_module('kho_tri_thuc.engines.e_hoa_don.phien')
        with patch.object(phien, 'kiem_tra_tien_trinh', return_value=()):
            ket_qua = phien.kiem_tra_moi_truong()
        self.assertTrue(ket_qua)
        self.assertEqual({r.ket_luan for r in ket_qua}, {'CHUA_KIEM'})
        # không tin cờ caller: hàm không nhận tham số
        with self.assertRaises(TypeError):
            phien.kiem_tra_moi_truong(da_xac_nhan=True)


if __name__ == '__main__':
    unittest.main()
