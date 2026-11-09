"""Kiểm tĩnh gói e_trich_xuat bằng stdlib; không import Core, không gọi AI/Cloud. Dữ liệu giả."""

import json
from pathlib import Path
import unittest

GOC = Path(__file__).resolve().parents[1]


class GoiTinh(unittest.TestCase):
    def doc(self, ten):
        return json.loads((GOC / ten).read_text(encoding='utf-8'))

    def test_manifest_khop_thu_muc_va_diem_vao(self):
        manifest = self.doc('engine.json')
        self.assertEqual(manifest['ma'], GOC.name)
        entry = manifest['ho_so_chay_mau']['diem_vao']
        self.assertEqual(entry, 'kho_tri_thuc.engines.e_trich_xuat.tich_hop.chay_noi')
        self.assertTrue((GOC / (entry.split('.')[-2] + '.py')).is_file())

    def test_contract_du_closure_offline(self):
        bundle = self.doc('contract/schemas.json')
        for cap in self.doc('engine.json')['capability']:
            for key in ('dau_vao', 'dau_ra'):
                self.assertIn('urn:ktt:contract:' + cap[key], bundle)
        for identity, schema in bundle.items():
            self.assertEqual(schema['$id'], identity)
        self.assertIn('urn:ktt:contract:chung.v1', bundle)

    def test_vi_du_co_nhan_du_lieu_gia(self):
        vi_du = self.doc('contract/vi_du.json')
        self.assertIn('Dữ liệu giả', vi_du['luu_y'])
        for ca in vi_du['tham_chieu_tep.v1']['hop_le']:
            self.assertEqual(ca['sha256'], '0' * 64)

    def test_ma_nguon_canh_manifest(self):
        for ten in ('ai_chung.py', 'chay.py', 'docx.py', 'do_chinh_xac.py',
                    'quy_trinh.py', 'tham_so.py', 'tich_hop.py'):
            self.assertTrue((GOC / ten).is_file(), ten)


if __name__ == '__main__':
    unittest.main()
