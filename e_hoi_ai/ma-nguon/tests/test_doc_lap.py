"""Kiểm gói e_hoi_ai và nhật ký qua SDK mock, dữ liệu giả trong RAM.

Không nhập test từ repo, không mở DB/tệp nhật ký, không gọi AI/dịch vụ.
Chạy cùng SDK và gói engine; kiểm wheel độc lập thuộc gate đóng gói của lead.
"""

from copy import deepcopy
from dataclasses import replace
import io
import json
from pathlib import Path
import unittest
from unittest.mock import Mock

from kho_tri_thuc.sdk_core.engine import SDKEngine
from kho_tri_thuc.engines.e_hoi_ai.lib import cong_ai as ca
from kho_tri_thuc.engines.e_hoi_ai.nhat_ky import BoGhiQuaCore, LoiNhatKy

GOC = Path(__file__).resolve().parents[1]


class GoiTinh(unittest.TestCase):
    def doc(self, ten):
        return json.loads((GOC / ten).read_text(encoding='utf-8'))

    def test_manifest_khop_thu_muc_va_diem_vao(self):
        manifest = self.doc('engine.json')
        self.assertEqual(manifest['ma'], GOC.name)
        entry = manifest['ho_so_chay_mau']['diem_vao']
        self.assertEqual(entry, 'kho_tri_thuc.engines.e_hoi_ai.chay')
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


class CoreNhatKyGia:
    """Core giả giữ snapshot và chống trùng; SDK chỉ là test double có spec."""

    def __init__(self):
        self.files = {}
        self.lan_ghi = []
        self.che_do = 'ack'
        self.snapshot = {'nhat_ky_ai': {
            'tep_ids': [], 'revision_tep_truoc': 3,
            'du_lieu_ket_qua': dict(bien_the='ai_demo', ma_contract='nhat_ky_ai_demo',
                phien_ban_contract='1', trang_thai='DEMO', ly_do=None,
                revision_truoc=0, nguon=[])}}
        self.sdk = Mock(spec_set=SDKEngine)
        self.sdk.doc_dau_vao.side_effect = lambda: deepcopy(self.snapshot)
        self.sdk.ghi_ket_qua.side_effect = self.ghi
        self.sdk.mo_doc.side_effect = lambda tep_id: io.BytesIO(self.files[tep_id])

    def ghi(self, *, luong, ten, du_lieu, revision_tep_truoc):
        raw = luong.read()
        self.lan_ghi.append(dict(raw=raw, ten=ten, du_lieu=deepcopy(du_lieu),
                                 revision_tep_truoc=revision_tep_truoc))
        if self.che_do == 'loi_truoc':
            raise RuntimeError('Dữ liệu giả: lỗi trước commit')
        record = json.loads(raw)
        tep_id = record['ma_yeu_cau'] + ':' + record['duong']
        if tep_id in self.files and self.files[tep_id] != raw:
            raise RuntimeError('Dữ liệu giả: khác bytes cùng khóa')
        self.files[tep_id] = raw
        ids = self.snapshot['nhat_ky_ai']['tep_ids']
        if tep_id not in ids:
            ids.append(tep_id)
        # Core/transport có thể đổi object sau khi nhận: không được đổi hàng retry.
        du_lieu['nguon'].append({'du_lieu_gia': True})
        if self.che_do == 'loi_sau':
            raise RuntimeError('Dữ liệu giả: mất ACK sau commit')
        return {'da_ban_giao': self.che_do == 'ack'}


class NhatKyDocLap(unittest.TestCase):
    def setUp(self):
        self.core = CoreNhatKyGia()
        self.bo = BoGhiQuaCore(self.core.sdk)

    def ban_ghi(self, **kw):
        return replace(ca.BanGhiCongAI(ma_yeu_cau='DEMO-01',
            luc='2026-11-05T10:00:00+00:00', loai_viec='BOC_TACH_HOP_DONG',
            duong='LOCAL', nha_cung_cap='local', model='Dữ liệu giả',
            da_gui=True, ket_qua='DAT'), **kw)

    def kiem(self, dung=True, **kw):
        return self.ban_ghi(duong='CLOUD', nha_cung_cap='demo-cloud',
            ly_do_chuyen_cloud=('KIEM_XAC_SUAT',),
            ly_do=(ca.LOCAL_DUNG if dung else ca.LOCAL_SAI,), **kw)

    def test_ghi_dto_noi_bo_giu_du_metadata_utf8(self):
        record = self.kiem(token_vao=12, token_ra=34, chi_phi_uoc_usd=0.012,
            thoi_gian_ms=78, ma_luot_mask='DEMO-MASK', so_truong_bi_loai=1,
            trich_dan_hop_le=True, phap_nhan_id='DEMO-PN', viec_id='DEMO-VIEC')
        self.bo.ghi(record)
        payload = self.core.lan_ghi[0]
        self.assertEqual(json.loads(payload['raw']),
                         json.loads(json.dumps(record.thanh_dict())))
        self.assertIn('Dữ liệu giả'.encode('utf-8'), payload['raw'])
        self.assertEqual(payload['ten'], 'nhat-ky-ai.json')
        self.assertEqual(payload['revision_tep_truoc'], 3)
        self.assertEqual(payload['du_lieu'],
                         self.core.snapshot['nhat_ky_ai']['du_lieu_ket_qua'])
        self.assertTrue(self.bo.da_ban_giao())

    def test_retry_giu_bytes_metadata_revision_core_khong_ghi_trung(self):
        for che_do in ('cho_ack', 'loi_truoc', 'loi_sau'):
            with self.subTest(che_do=che_do):
                core = CoreNhatKyGia()
                bo = BoGhiQuaCore(core.sdk)
                core.che_do = che_do
                with self.assertRaises((LoiNhatKy, RuntimeError)):
                    bo.ghi(self.ban_ghi())
                dau = deepcopy(core.lan_ghi[0])
                self.assertFalse(bo.da_ban_giao())
                with self.assertRaisesRegex(LoiNhatKy, 'NHAT_KY_CHO_ACK'):
                    bo.thong_ke(2)
                core.snapshot['nhat_ky_ai']['revision_tep_truoc'] = 99
                core.snapshot['nhat_ky_ai']['du_lieu_ket_qua']['nguon'].append(
                    {'du_lieu_gia': 'snapshot mới'})
                core.che_do = 'ack'
                bo.thu_lai()
                self.assertEqual(core.lan_ghi[-1], dau)
                self.assertEqual(core.sdk.doc_dau_vao.call_count, 1)
                self.assertEqual(len(core.files), 1)
                self.assertTrue(bo.da_ban_giao())
                so_lan = len(core.lan_ghi)
                bo.thu_lai()
                self.assertEqual(len(core.lan_ghi), so_lan)

    def test_chi_ack_true_moi_go_hang_doi(self):
        for ack in (None, True, {}, {'da_ban_giao': False},
                    {'da_ban_giao': 1}, {'da_ban_giao': 'true'}):
            with self.subTest(ack=ack):
                core = CoreNhatKyGia()
                bo = BoGhiQuaCore(core.sdk)
                core.sdk.ghi_ket_qua.side_effect = None
                core.sdk.ghi_ket_qua.return_value = ack
                with self.assertRaisesRegex(LoiNhatKy, 'NHAT_KY_CHO_ACK'):
                    bo.ghi(self.ban_ghi())
                self.assertFalse(bo.da_ban_giao())
                core.sdk.ghi_ket_qua.return_value = {'da_ban_giao': True}
                bo.thu_lai()
                self.assertTrue(bo.da_ban_giao())

    def test_hang_doi_local_cloud_cung_yeu_cau_giu_thu_tu(self):
        self.core.che_do = 'loi_sau'
        for record in (self.ban_ghi(), self.kiem()):
            with self.assertRaises(RuntimeError):
                self.bo.ghi(record)
        self.assertEqual(len(self.core.files), 1)
        self.core.che_do = 'ack'
        self.bo.thu_lai()
        self.assertEqual([json.loads(raw)['duong'] for raw in self.core.files.values()],
                         ['LOCAL', 'CLOUD'])
        self.assertTrue(self.bo.da_ban_giao())

    def test_snapshot_thieu_metadata_giu_ban_ghi_de_thu_lai(self):
        for snapshot in ({}, {'nhat_ky_ai': {'tep_ids': []}},
                {'nhat_ky_ai': {'tep_ids': [], 'du_lieu_ket_qua': {},
                               'revision_tep_truoc': True}},
                {'nhat_ky_ai': {'tep_ids': [], 'du_lieu_ket_qua': {},
                               'revision_tep_truoc': -1}}):
            with self.subTest(snapshot=snapshot):
                core = CoreNhatKyGia()
                bo = BoGhiQuaCore(core.sdk)
                core.sdk.doc_dau_vao.side_effect = lambda: snapshot
                with self.assertRaises(LoiNhatKy):
                    bo.ghi(self.ban_ghi())
                self.assertFalse(bo.da_ban_giao())
                core.sdk.ghi_ket_qua.assert_not_called()
                core.sdk.doc_dau_vao.side_effect = lambda: deepcopy(core.snapshot)
                bo.thu_lai()
                self.assertTrue(bo.da_ban_giao())

    def test_snapshot_moi_moi_lan_doc_va_restart_adapter(self):
        self.assertEqual(self.bo.thong_ke(2), {})
        self.bo.ghi(self.ban_ghi())
        self.bo.ghi(self.kiem())
        tk = self.bo.thong_ke(2)
        moi = BoGhiQuaCore(self.core.sdk)
        self.assertEqual(moi.thong_ke(2), tk)
        self.core.snapshot['nhat_ky_ai']['tep_ids'] = ['DEMO-01:CLOUD']
        self.assertEqual(moi.thong_ke(2)['BOC_TACH_HOP_DONG'],
            dict(so_luot=0, so_kiem=1, so_kiem_cua_so=1, so_dung_cua_so=1))
        # Chỉ đọc đúng lịch sử Core cấp, không dò thêm tệp LOCAL còn trong kho giả.
        self.core.snapshot['nhat_ky_ai']['tep_ids'] = []
        self.assertEqual(moi.thong_ke(2), {})

    def test_thong_ke_cua_so_thu_tu_va_dieu_kien_cham(self):
        records = [self.ban_ghi(), self.kiem(), self.kiem(False),
            self.kiem(luc='2026-11-04T10:00:00+00:00'),
            self.kiem(ket_qua='LOI'), self.kiem(da_gui=False),
            replace(self.kiem(), ly_do=(ca.LOCAL_DUNG, ca.LOCAL_SAI)),
            replace(self.kiem(), ly_do_chuyen_cloud=('DUOI_NGUONG',)),
            self.ban_ghi(loai_viec='DEMO_KHAC', da_gui=False)]
        goc = ca.BoGhiBoNho()
        for i, record in enumerate(records):
            record = replace(record, ma_yeu_cau=f'DEMO-{i}')
            self.bo.ghi(record)
            goc.ghi(record)
        for cua_so in (1, 2, 100):
            with self.subTest(cua_so=cua_so):
                self.assertEqual(self.bo.thong_ke(cua_so), goc.thong_ke(cua_so))
        self.assertEqual(self.bo.thong_ke(1)['BOC_TACH_HOP_DONG'],
            dict(so_luot=1, so_kiem=3, so_kiem_cua_so=1, so_dung_cua_so=0))

    def test_snapshot_thieu_hong_khong_tra_so_khong_gia(self):
        self.assertEqual(self.bo.thong_ke(2), {})
        for snapshot in (None, {}, {'nhat_ky_ai': {}},
                {'nhat_ky_ai': {'tep_ids': ['x', 'x']}},
                {'nhat_ky_ai': {'tep_ids': ['']}},
                {'nhat_ky_ai': {'tep_ids': [1]}},
                {'nhat_ky_ai': {'tep_ids': ()}}):
            with self.subTest(snapshot=snapshot):
                self.core.sdk.doc_dau_vao.side_effect = lambda: snapshot
                with self.assertRaisesRegex(LoiNhatKy, 'NHAT_KY_THIEU_SNAPSHOT'):
                    self.bo.thong_ke(2)
        self.core.sdk.mo_doc.assert_not_called()

    def test_loi_doc_snapshot_hoac_tep_khong_dung_cache(self):
        self.bo.ghi(self.ban_ghi())
        self.assertEqual(self.bo.thong_ke(2)['BOC_TACH_HOP_DONG']['so_luot'], 1)
        for method in (self.core.sdk.doc_dau_vao, self.core.sdk.mo_doc):
            with self.subTest(method=method):
                cu = method.side_effect
                method.side_effect = RuntimeError('Dữ liệu giả: không đọc được Core')
                with self.assertRaises(RuntimeError):
                    self.bo.thong_ke(2)
                method.side_effect = cu

    def test_tep_json_hoac_metadata_hong_bi_tu_choi(self):
        record = self.ban_ghi().thanh_dict()
        for key, value in (('duong', 'KHAC'), ('da_gui', 1), ('ma_yeu_cau', ''),
                           ('ly_do', 'KHONG_PHAI_DANH_SACH')):
            data = {**record, key: value}
            with self.subTest(key=key):
                self.core.files['DEMO'] = json.dumps(data).encode('utf-8')
                self.core.snapshot['nhat_ky_ai']['tep_ids'] = ['DEMO']
                with self.assertRaises(LoiNhatKy):
                    self.bo.thong_ke(2)
        for raw in (b'{', b'{}', b'[]', b'\xff',
                    json.dumps({**record, 'prompt': 'Dữ liệu giả'}).encode('utf-8')):
            with self.subTest(raw=raw):
                self.core.files['DEMO'] = raw
                with self.assertRaisesRegex(LoiNhatKy, 'NHAT_KY_DU_LIEU'):
                    self.bo.thong_ke(2)

    def test_cua_so_khong_hop_le_khong_goi_core(self):
        for value in (True, False, 0, -1, 1.5, '2', None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.bo.thong_ke(value)
        self.core.sdk.doc_dau_vao.assert_not_called()


if __name__ == '__main__':
    unittest.main()
