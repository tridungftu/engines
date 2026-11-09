"""AI-1b-KHAI: gói DEMO kiểm SHA thật; CSDL/kênh/tiến trình đều giả.

Tệp tạm nằm dưới TMP của lượt test và được giữ lại, không xóa tệp.
"""

from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from kho_tri_thuc.core import chay_core, dich_vu_engine as dv, goi, ho_so_module as h
from kho_tri_thuc.core import ung_dung
from kho_tri_thuc.core.dispatcher import KiemSchema
from kho_tri_thuc.core.http import LoiHTTP
from kho_tri_thuc.sdk_core import kenh_khung as k
from tests import test_g2_24 as g24, test_g2_32_e2 as e2, test_g3_ai_4a as ai4


PROMPT = 'Trích số tiền DEMO kèm căn cứ.'
TEP_PROMPT = 'prompt/trich_tien.txt'


def _json(value):
    return json.dumps(value, ensure_ascii=False).encode('utf-8')


class HamHoiAIKhaiTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix='ai-ham-khai-DEMO-')).resolve()
        self.kiem = KiemSchema(json.loads((goi.THU_MUC_CONTRACT / 'manifest.json')
                                         .read_text(encoding='utf-8'))).kiem
        self.manifest = g24.manifest_demo()
        self.khai = dict(ma_function='trich_hop_dong', ma_prompt='trich_tien',
                         phien_ban_prompt=1, tep_prompt=TEP_PROMPT, mo_ta='Trích tiền DEMO')
        self.manifest['ham_hoi_ai'] = [self.khai]
        entry = self.manifest['contract']['cong_bo'][0]
        schema = {'$schema': goi.DRAFT, '$id': g24.CONTRACT_ID, 'type': 'object',
                  'additionalProperties': False, 'required': ['id'],
                  'properties': {'id': {'type': 'string'}}}
        description = dict(entry, muc_dich='Ghi chú DEMO', module_duoc_doc=['mau_demo'],
            truong=[dict(ten='id', nghia='Định danh DEMO', bat_buoc=True,
                         don_vi='khong_ap_dung', nguon='Thiết kế DEMO')])
        self.files = {
            'mau_demo/chay.py': b'raise RuntimeError("CAM CHAY GOI")',
            'ui/chinh.js': b'throw new Error("CAM CHAY ASSET");',
            'migration/kiem_ke.json': b'{}', 'migration/001_demo.sql': b'-- DEMO',
            entry['schema']: _json(schema), entry['vi_du']: _json({'id': 'DEMO'}),
            entry['tep_mo_ta']: _json(description), TEP_PROMPT: PROMPT.encode('utf-8')}
        self.conn = Mock()
        self.conn.execute.return_value.fetchone.side_effect = lambda: (deepcopy(self.data),)
        self.registry = self.enterContext(patch.object(h.dang_ky, 'doc_dang_ky',
            side_effect=lambda *a, **kw: deepcopy(self.rows)))
        # Chỉ bỏ ranh Git cho fixture TMP; giữ kiểm đường dẫn/link/handle của goi.
        self.enterContext(patch.object(h.cai_dat, '_duong_ngoai_git',
                                      side_effect=goi.kiem_duong_dan))
        self.guards = [self.enterContext(patch(target, side_effect=AssertionError('Cấm I/O thật')))
            for target in ('socket.socket', 'socket.create_connection', 'socket.getaddrinfo',
                           'subprocess.Popen')]
        self.cai()

    def tearDown(self):
        for guard in self.guards:
            guard.assert_not_called()

    def ghi(self, folder):
        files = {**self.files, 'module.json': _json(self.manifest)}
        hashes, _ = goi.bam_goi(files)
        files['goi/kiem_ke.json'] = _json(dict(phien_ban=self.manifest['phien_ban'], tep=[
            dict(duong_dan=n, bytes=len(raw), sha256=hashes[n]) for n, raw in files.items()]))
        for name, raw in files.items():
            path = folder / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        return goi.bam_goi(files)[1]

    def cai(self):
        source = self.root / 'nguon-demo'
        bam = self.ghi(source)
        self.folder = self.root / 'runtime' / 'mau_demo' / ('1.0.0-' + bam)
        self.ghi(self.folder)
        package = goi.doc_goi(self.folder, phien_ban_core='1.0.0')
        self.bam = bam
        self.data = dict(trang_thai='XONG', bam=bam,
            snapshot=dict(module='mau_demo', phien_ban='1.0.0', core='1.0.0',
                sdk_python='1.0.0', sdk_js='1.0.0', gioi_han={},
                thu_muc_runtime=str(self.root / 'runtime'),
                sha256_tung_tep=dict(package.sha256_tung_tep),
                bytes_tung_tep={n: len(raw) for n, raw in package.cac_tep.items()},
                cac_thu_muc=list(package.cac_thu_muc)),
            ho_so_runtime=dict(thu_muc_da_cai=str(self.folder), launch=None))
        self.rows = [dict(module='mau_demo', so_phien_ban='1.0.0',
                          trang_thai='da_cai', ma_bam_goi=bam)]
        return package

    def doc(self, **doi):
        return h.doc_hoi_ai(self.conn, **{**dict(module='mau_demo', phien_ban_module='1.0.0',
            ma_function='trich_hop_dong', ma_prompt='trich_tien', phien_ban_prompt='1'), **doi})

    def assert_chan(self, callback):
        with self.assertRaises(LoiHTTP) as caught:
            callback()
        self.assertEqual(caught.exception.status, 503)
        self.assertIn(caught.exception.ma, h.LOI)
        self.assertNotIn(str(self.root), caught.exception.thong_diep)
        self.assertIsNone(caught.exception.__context__)

    def test_khai_hop_le_doc_utf8_tu_goi_sha_khong_can_launch_crm(self):
        bam, khai = self.doc()
        self.assertEqual(bam, self.bam)
        self.assertEqual(khai, dict(ma_function='trich_hop_dong', ma_prompt='trich_tien',
                                   phien_ban_prompt='1', chi_dan=PROMPT))
        self.conn.execute.assert_called_with('SELECT loi.cd060_doc_runtime_hien_hanh(%s,%s)',
                                             ('mau_demo', self.bam))
        self.assertIsNone(h.ghim_launch(self.cai()))
        self.assertNotIn('ham_hoi_ai', self.data['ho_so_runtime'])

    def test_schema_tuy_chon_va_object_dong_ma_an_toan_phien_ban_nguyen_duong(self):
        ref = {'$ref': 'urn:ktt:manifest:module.v1'}
        self.assertTrue(self.kiem(ref, self.manifest))
        old = deepcopy(self.manifest)
        old.pop('ham_hoi_ai')
        self.assertTrue(self.kiem(ref, old))
        for changes in ({'truong_la': 'DEMO'}, {'ma_function': '../ngoai'},
                        {'ma_prompt': 'co khoang trang'}, {'phien_ban_prompt': 0},
                        {'phien_ban_prompt': -1}, {'phien_ban_prompt': True},
                        {'phien_ban_prompt': '1.0.0'}):
            value = deepcopy(self.manifest)
            value['ham_hoi_ai'][0].update(changes)
            with self.subTest(changes=changes):
                self.assertFalse(self.kiem(ref, value))
        for field in ('ma_function', 'ma_prompt', 'phien_ban_prompt', 'tep_prompt'):
            value = deepcopy(self.manifest)
            value['ham_hoi_ai'][0].pop(field)
            with self.subTest(field=field):
                self.assertFalse(self.kiem(ref, value))

    def test_tep_prompt_thoat_goi_tu_choi(self):
        for name in ('../ngoai.txt', 'prompt/../../ngoai.txt', '/ngoai.txt',
                     'C:/ngoai.txt', '\\\\may/ngoai.txt', 'prompt\\ngoai.txt',
                     './ngoai.txt', 'prompt//ngoai.txt'):
            self.manifest['ham_hoi_ai'][0]['tep_prompt'] = name
            # Giữ cả schema và bộ kiểm đường dẫn thật; không mở tệp ngoài gói.
            self.ghi(self.folder)
            with self.subTest(name=name):
                self.assert_chan(self.doc)

    def test_thieu_khai_hoac_function_prompt_khac_tu_choi(self):
        for changes in ({'ma_function': 'khac'}, {'ma_prompt': 'khac'},
                        {'module': 'khac'}, {'phien_ban_module': '2.0.0'}):
            with self.subTest(changes=changes):
                self.assert_chan(lambda: self.doc(**changes))
        for missing in ([], None):
            if missing is None:
                self.manifest.pop('ham_hoi_ai')
            else:
                self.manifest['ham_hoi_ai'] = missing
            self.cai()
            self.assert_chan(self.doc)

    def test_phien_ban_prompt_khac_khong_fallback_hoac_ep_kieu(self):
        for version in ('2', '01', '1.0.0', '', 1, True):
            with self.subTest(version=version):
                self.assert_chan(lambda: self.doc(phien_ban_prompt=version))

    def test_tep_prompt_phai_co_trong_danh_sach_sha(self):
        self.manifest['ham_hoi_ai'][0]['tep_prompt'] = 'prompt/khong_co.txt'
        self.cai()
        self.assert_chan(self.doc)

    def test_khai_trung_cung_khoa_khac_mo_ta_khong_chon_tuy_y(self):
        self.manifest['ham_hoi_ai'].append(dict(self.khai, mo_ta='Bản khai DEMO khác'))
        self.cai()
        self.assert_chan(self.doc)

    def test_prompt_trang_hoac_khong_utf8_tu_choi(self):
        for raw in (b'', b' \n\t', b'\xff\xfe'):
            self.files[TEP_PROMPT] = raw
            self.cai()
            with self.subTest(raw=raw):
                self.assert_chan(self.doc)

    def test_sua_prompt_sau_cai_khong_dung_cache_phai_cai_lai(self):
        self.doc()
        (self.folder / TEP_PROMPT).write_text('Nội dung DEMO đã bị đổi.', encoding='utf-8')
        self.assert_chan(self.doc)
        self.files[TEP_PROMPT] = 'Nội dung DEMO mới.'.encode('utf-8')
        # Kể cả tự tính lại kiểm kê cũng không khớp snapshot cài cũ.
        self.ghi(self.folder)
        self.assert_chan(self.doc)
        self.cai()
        self.assertEqual(self.doc()[1]['chi_dan'], 'Nội dung DEMO mới.')

    def test_snapshot_sai_sha_bytes_thu_muc_trang_thai_va_go_cai_deu_chan(self):
        original = deepcopy(self.data)
        for path, value in (('bam', 'b' * 64), ('trang_thai', 'DANG_CAI'),
                ('snapshot.sha256_tung_tep', {}), ('snapshot.bytes_tung_tep', {}),
                ('snapshot.cac_thu_muc', []), ('snapshot.module', 'khac'),
                ('snapshot.phien_ban', '2.0.0'),
                ('ho_so_runtime.thu_muc_da_cai', str(self.root))):
            self.data = deepcopy(original)
            obj = self.data
            parts = path.split('.')
            for key in parts[:-1]:
                obj = obj[key]
            obj[parts[-1]] = value
            with self.subTest(path=path):
                self.assert_chan(self.doc)
        self.data = None
        self.assert_chan(self.doc)
        self.rows = []
        self.assert_chan(self.doc)

    def test_loi_doc_goi_khong_lo_noi_dung_va_duong_dan(self):
        original = RuntimeError('DEMO_SECRET ' + str(self.root))
        with patch.object(goi, 'doc_goi', side_effect=original):
            self.assert_chan(self.doc)
        self.assertIsNone(original.__traceback__)
        self.assertNotIn('DEMO_SECRET', repr(original))

    def test_provider_thuc_di_qua_kiem_pin_cua_dich_vu_engine(self):
        pin = e2.pin_demo(capability='ai.hoi@1', ma_engine='e_hoi_ai',
            dau_vao=dv.GhimContract('hoi_ai.v2', '2.0.0', 'b' * 64),
            dau_ra=dv.GhimContract('tra_loi_ai.v2', '2.0.0', 'c' * 64))
        binding = e2.binding_demo(pin, module='mau_demo')
        service = dv.DichVuEngine([pin], loai_viec=[binding], ho_so_runtime=Mock(),
                                 doc_kt=Mock(), doc_hoi_ai=h.doc_hoi_ai)
        lease = replace(ai4._lease(), module='mau_demo')
        data = ai4._dau_vao_v2(lease)
        data['yeu_cau']['phien_ban_prompt'] = data['nguon_core']['phien_ban_prompt'] = '1'
        with patch.object(service, '_doi_chieu'):
            result = service.nguon_hoi_ai(self.conn, ghim=binding, giu=lease,
                dau_vao=data, phien_ban_module='1.0.0')
            self.assertEqual(result, data)
            data['yeu_cau']['chi_dan'] = 'Prompt giả mạo DEMO'
            with self.assertRaises(k.LoiKenh):
                service.nguon_hoi_ai(self.conn, ghim=binding, giu=lease,
                    dau_vao=data, phien_ban_module='1.0.0')

    def test_chay_core_noi_provider_nhung_khong_doc_goi_khi_dung_app(self):
        connect, ket = Mock(), Mock()
        ket.doc.return_value = SimpleNamespace(lay_de_truyen=lambda: b'DEMO_' + b'x' * 32)
        app = SimpleNamespace(cong_http=18443, http=SimpleNamespace(origin='http://127.0.0.1:18443'))
        pin = e2.pin_demo()
        with patch.object(ung_dung, 'tao_ung_dung', return_value=app) as factory, \
                patch.object(chay_core, '_DanhMucDuLieuLazy'), \
                patch.object(chay_core.kenh_bi_mat, 'tao_provider', return_value=None), \
                patch.object(goi, 'doc_goi', side_effect=AssertionError('Chưa cấp nguồn')):
            chay_core.dung_ung_dung(self.root / 'var/core-demo/ai-khai/cau-hinh-DEMO.json',
                ket=ket, ket_noi=connect,
                doc_kt=lambda conn: [], ghim_engine=[pin], loai_viec=[e2.binding_demo(pin)],
                ho_so_runtime=Mock())
        self.assertIs(factory.call_args.kwargs['dich_vu_engine']._doc_hoi_ai, h.doc_hoi_ai)
        connect.assert_not_called()


if __name__ == '__main__':
    unittest.main()
