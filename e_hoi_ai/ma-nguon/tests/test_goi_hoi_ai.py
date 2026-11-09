"""AI-LAT3: metadata, closure thư viện và readiness; chỉ thuần/mock.

Không build/cài gói, gọi AI, CSDL, socket hoặc tiến trình ngoài. Bootstrap
thật trao đổi JSON trong RAM; vòng nhận việc và provider đều là mock.
"""

import ast
from hashlib import sha256
from importlib import metadata
from importlib.util import resolve_name
import io
import json
from pathlib import Path
import re
import sys
import tomllib
from types import ModuleType
import unittest
from unittest.mock import Mock, patch

from kho_tri_thuc.engines.e_hoi_ai import chay as runtime
from kho_tri_thuc.sdk_core.bootstrap import Bootstrap, LoiBootstrap, PROTOCOL


GOI = Path(__file__).resolve().parents[1]
TEN_GOI = 'kho_tri_thuc.engines.e_hoi_ai'
SDK = 'kho_tri_thuc.sdk_core'


def _imports_engine():
    """Kiểm cả import lazy bằng AST, không thực thi mã hoặc nạp cấu hình."""
    for tep in sorted(GOI.rglob('*.py')):
        rel = tep.relative_to(GOI)
        if rel.parts[0] == 'tests':
            continue
        package = '.'.join((TEN_GOI, *rel.parts[:-1]))
        for node in ast.walk(ast.parse(tep.read_text(encoding='utf-8'))):
            names = []
            if isinstance(node, ast.Import):
                names = [item.name for item in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [resolve_name('.' * node.level + (node.module or ''), package)]
                if node.module is None:
                    names = [name + '.' + item.name for name in names for item in node.names]
            elif isinstance(node, ast.Call):
                func = node.func
                if ((isinstance(func, ast.Name) and func.id in ('__import__', 'import_module'))
                        or (isinstance(func, ast.Attribute) and func.attr == 'import_module')):
                    raise AssertionError(f'{rel}:{node.lineno}: cần import tường minh')
            for name in names:
                yield str(rel), node.lineno, name


class GoiHoiAITests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((GOI / 'engine.json').read_text(encoding='utf-8'))
        self.project = tomllib.loads((GOI / 'pyproject.toml').read_text(encoding='utf-8'))

    def test_phien_ban_metadata_manifest_runtime_dong_bo(self):
        version = self.manifest['phien_ban']
        self.assertRegex(version, r'^\d+\.\d+\.\d+-demo\.\d+$')
        self.assertEqual(runtime.PHIEN_BAN, version)
        self.assertEqual(self.project['project']['version'], version.replace('-demo.', '.dev'))

    def test_build_chi_gom_engine_va_lib_khong_gom_core(self):
        config = self.project['tool']['setuptools']
        self.assertEqual(config['packages'], [TEN_GOI, TEN_GOI + '.lib'])
        self.assertEqual(config['package-dir'], {TEN_GOI: '.'})
        self.assertFalse(config['include-package-data'])
        self.assertEqual(self.project['project']['dependencies'], [])
        # Đối chiếu layout thật, không chỉ kiểm tên package khai báo.
        expected = {TEN_GOI if p.parent == GOI else TEN_GOI + '.' +
                    '.'.join(p.parent.relative_to(GOI).parts)
                    for p in GOI.rglob('__init__.py')
                    if 'tests' not in p.relative_to(GOI).parts}
        self.assertEqual(set(config['packages']), expected)

    def test_du_lieu_phan_phoi_du_manifest_contract_lock_va_test(self):
        patterns = self.project['tool']['setuptools']['package-data'][TEN_GOI]
        included = {p.relative_to(GOI).as_posix() for pattern in patterns for p in GOI.glob(pattern)
                    if p.is_file()}
        expected = {'engine.json', 'contract/schemas.json', 'contract/vi_du.json',
                    'requirements.lock', 'NGUON.md', 'README.md', 'CHANGELOG.md',
                    'tests/test_doc_lap.py', 'tests/test_goi_hoi_ai.py'}
        self.assertEqual(included, expected)
        self.assertEqual(self.manifest['ho_so_chay_mau']['diem_vao'], TEN_GOI + '.chay')

    def test_yeu_cau_sdk_toi_thieu_khong_ghim_candidate(self):
        nguon = (GOI / 'NGUON.md').read_text(encoding='utf-8')
        project = (GOI / 'pyproject.toml').read_text(encoding='utf-8')
        for text in (nguon, project):
            self.assertIn('SDK Python >=1.5.0', text)
        self.assertNotIn('chuyển engine sang SDK 1.5.0 của CRM', nguon)
        self.assertEqual(self.project['project']['dependencies'], [])

    def test_contract_v2_va_ref_chi_dung_bundle_offline(self):
        bundle = json.loads((GOI / 'contract/schemas.json').read_text(encoding='utf-8'))
        for cap in self.manifest['capability']:
            self.assertEqual(cap['ma'], 'ai.hoi@1')
            self.assertEqual((cap['dau_vao'], cap['dau_ra']), ('hoi_ai.v2', 'tra_loi_ai.v2'))
            for key in ('dau_vao', 'dau_ra'):
                self.assertIn('urn:ktt:contract:' + cap[key], bundle)

        def kiem(value):
            if isinstance(value, dict):
                ref = value.get('$ref', '')
                if ref and not ref.startswith('#'):
                    self.assertIn(ref.split('#', 1)[0], bundle)
                for child in value.values():
                    kiem(child)
            elif isinstance(value, list):
                for child in value:
                    kiem(child)

        for identity, schema in bundle.items():
            self.assertEqual(schema['$id'], identity)
            kiem(schema)


class BamNguonHienHanhTests(unittest.TestCase):
    def setUp(self):
        self.nguon = (GOI / 'NGUON.md').read_text(encoding='utf-8')
        self.teps = {p.relative_to(GOI).as_posix(): p for p in GOI.rglob('*')
                     if p.is_file() and p.suffix in ('.py', '.json', '.toml', '.lock')
                     and not {'tests', '__pycache__'} & set(p.relative_to(GOI).parts)}

    def kiem_bam(self, text, doc_bytes=None):
        section = text.split('### Tập tệp hiện hành và SHA-256\n', 1)[1].split('\n## ', 1)[0]
        rows = {}
        for line in section.splitlines():
            if not line.startswith('| `'):
                continue
            row = re.fullmatch(r'\| `([^`]+)` \| `([0-9a-f]{64})` \| ([^|]+) \|', line)
            self.assertIsNotNone(row, 'Hàng nguồn/SHA-256 chưa hợp lệ: ' + line)
            name, digest, _ = row.groups()
            self.assertNotIn(name, rows, 'Tệp lặp trong bảng: ' + name)
            rows[name] = digest
        self.assertEqual(set(rows), set(self.teps), 'Bảng nguồn thiếu/thừa tệp hiện hành')
        for name, path in self.teps.items():
            raw = path.read_bytes() if doc_bytes is None else doc_bytes(path)
            self.assertEqual(sha256(raw).hexdigest(), rows[name], 'SHA-256 lệch: ' + name)

    def test_bang_du_tep_nguon_lib_contract_va_metadata_khop_byte_that(self):
        self.kiem_bam(self.nguon)

    def test_doi_mot_byte_o_tung_tep_bi_phat_hien(self):
        for name, path in self.teps.items():
            raw = path.read_bytes()
            changed = bytes([raw[0] ^ 1]) + raw[1:]
            with self.subTest(tep=name), self.assertRaisesRegex(AssertionError, 'SHA-256 lệch'):
                self.kiem_bam(self.nguon, lambda p: changed if p == path else p.read_bytes())

    def test_bang_thieu_thua_lap_va_sha_khong_du_64_ky_tu_bi_chan(self):
        line = next(line for line in self.nguon.splitlines() if line.startswith('| `__init__.py`'))
        for case, text in {
                'thiếu tệp': self.nguon.replace(line + '\n', ''),
                'thừa tệp test': self.nguon.replace(line, line + '\n' +
                    line.replace('__init__.py', 'tests/test_doc_lap.py')),
                'lặp tệp': self.nguon.replace(line, line + '\n' + line),
                'băm ngắn': self.nguon.replace(line, re.sub(r'[0-9a-f]{64}', 'a' * 63, line)),
        }.items():
            with self.subTest(ca=case), self.assertRaises(AssertionError):
                self.kiem_bam(text)


class KhoaThuVienTests(unittest.TestCase):
    SDK_IMPORT = {'cryptography': SDK}
    BAC_CAU = {'cffi': 'cryptography', 'pycparser': 'cffi'}

    def setUp(self):
        self.lock = (GOI / 'requirements.lock').read_text(encoding='utf-8')

    def _kiem_khoa(self, text):
        pins, sdk, bac_cau = {}, {}, {}
        for line in text.splitlines():
            if not line.strip():
                continue
            if line.startswith('#'):
                if line.startswith(('# sdk:', '# bac-cau:')):
                    row = re.fullmatch(r'# (sdk|bac-cau): ([\w.-]+) \| ([\w.-]+) \| (.+)', line)
                    self.assertIsNotNone(row, 'Thiếu tên hoặc lý do: ' + line)
                    kind, name, parent, reason = row.groups()
                    self.assertGreaterEqual(len(reason.strip()), 10)
                    entries = sdk if kind == 'sdk' else bac_cau
                    self.assertNotIn(name, entries)
                    entries[name] = parent
                continue
            row = re.fullmatch(r'([a-z][a-z0-9-]*)==([0-9][A-Za-z0-9.!+_-]*)', line)
            self.assertIsNotNone(row, 'Chỉ dùng exact pin: ' + line)
            name, version = row.groups()
            self.assertNotIn(name, pins)
            pins[name] = version
        self.assertEqual(sdk, self.SDK_IMPORT)
        self.assertEqual(bac_cau, self.BAC_CAU)
        self.assertEqual(set(pins), set(sdk) | set(bac_cau))
        self.assertTrue(set(bac_cau.values()) <= set(pins))
        for file, line, name in _imports_engine():
            self.assertTrue(name.split('.')[0] in sys.stdlib_module_names
                            or name == TEN_GOI or name.startswith(TEN_GOI + '.')
                            or name == SDK or name.startswith(SDK + '.'),
                            f'{file}:{line}: import ngoài closure: {name}')
        return pins

    def test_import_ke_ca_lazy_chi_stdlib_noi_bo_sdk(self):
        self._kiem_khoa(self.lock)

    def test_exact_pin_khop_metadata_dang_cai(self):
        for name, expected in self._kiem_khoa(self.lock).items():
            with self.subTest(goi=name):
                self.assertEqual(metadata.version(name), expected)

    def test_bac_cau_dung_quan_he_runtime_trong_metadata(self):
        for name, parent in self.BAC_CAU.items():
            with self.subTest(goi=name):
                requirements = metadata.requires(parent) or []
                names = {re.match(r'[\w.-]+', item).group().lower() for item in requirements
                         if 'extra ==' not in item}
                self.assertIn(name, names)

    def test_thieu_thua_sdk_candidate_pin_gia_va_thieu_ly_do_bi_chan(self):
        variants = {
            'thiếu pin': self.lock.replace('cryptography==49.0.0\n', ''),
            'thiếu bắc cầu': self.lock.replace('pycparser==3.0\n', ''),
            'gói thừa': self.lock + '\nrequests==2.0.0\n',
            'SDK candidate': self.lock + '\nkho-tri-thuc-sdk==1.4.1\n',
            'khoảng thay pin': self.lock.replace('cffi==2.0.0', 'cffi>=2.0.0'),
            'pin lặp': self.lock + '\ncffi==2.0.0\n',
            'ngoại lệ giả': self.lock + '\n# bac-cau: requests | cffi | Lý do ngoài closure.\n',
            'thiếu lý do': re.sub(r'(# sdk: cryptography \| [\w.]+ \| ).*', r'\1', self.lock),
        }
        for case, text in variants.items():
            with self.subTest(ca=case), self.assertRaises(AssertionError):
                self._kiem_khoa(text)

    def test_import_moi_ke_ca_lazy_phai_bao_loi(self):
        imports = list(_imports_engine())
        for name in ('requests', 'openai', 'anthropic', 'psycopg',
                     'kho_tri_thuc.core.viec', 'kho_tri_thuc.tri_thuc.cong_ai',
                     'kho_tri_thuc.engines.e_ocr.chay'):
            with self.subTest(import_moi=name), patch(
                    __name__ + '._imports_engine', return_value=imports + [('lib/demo.py', 1, name)]):
                with self.assertRaises(AssertionError):
                    self._kiem_khoa(self.lock)


class PhienBanReadinessTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((GOI / 'engine.json').read_text(encoding='utf-8'))
        self.source = compile((GOI / 'chay.py').read_text(encoding='utf-8'), str(GOI / 'chay.py'), 'exec')
        for target in ('socket.socket', 'socket.create_connection', 'socket.getaddrinfo',
                       'subprocess.Popen', 'urllib.request.OpenerDirector.open'):
            self.enterContext(patch(target, side_effect=AssertionError('Cấm mạng/tiến trình thật')))

    def nap_runtime(self, manifest, *, loi_doc=None):
        module = ModuleType(TEN_GOI + '.kiem_goi_trong_ram')
        module.__package__ = TEN_GOI
        module.__file__ = str(GOI / 'chay.py')
        raw = manifest if isinstance(manifest, bytes) else json.dumps(manifest).encode('utf-8')
        luong = io.BytesIO(raw)
        doc_bytes = Mock(wraps=luong.read)
        luong.read = doc_bytes
        with patch.object(Path, 'open', autospec=True, return_value=luong,
                          side_effect=loi_doc) as doc_goi:
            exec(self.source, module.__dict__)
        doc_goi.assert_called_once_with(GOI / 'engine.json', 'rb')
        if loi_doc is None:
            doc_bytes.assert_called_once_with(64 * 1024 + 1)
            self.assertTrue(luong.closed)
        else:
            doc_bytes.assert_not_called()
        return module

    def chay_readiness(self, module, *, san_sang=True, demo=False, loi_goi=False):
        bootstrap = Bootstrap.__new__(Bootstrap)
        bootstrap._cfg = dict(module='e_hoi_ai', instance_id='DEMO', pid=123,
            dinh_danh_lan_tao='DEMO', nonce_khoi_dong='DEMO', cong=23456,
            the_he=1, phien_ban='KHONG_LAY_PHIEN_BAN_TU_CORE')
        bootstrap._duoc_accept = False
        bootstrap._vao = io.BytesIO(b''.join((json.dumps(
            {'protocol': PROTOCOL, 'kieu': kind}) + '\n').encode('ascii')
            for kind in ('nhan_accept', 'thu_hoi')))
        bootstrap._ra = io.BytesIO()
        bootstrap.socket = Mock()
        bootstrap.bi_mat = Mock()
        bootstrap.bo_doc = Mock()
        vong = Mock()
        vong.drain.return_value = True
        provider = Mock()
        provider.cai_dat = {'cloud_bat': True}
        bo_ghi = Mock()
        bo_ghi.da_ban_giao.return_value = True
        with patch.object(module.Bootstrap, 'nhan', return_value=bootstrap), \
                patch.object(module, '_VongNhan', return_value=vong) as tao_vong, \
                patch.object(module.bm.BiMatRAM, 'tu_bootstrap') as tao_bi_mat, \
                patch.object(module.bm, 'tao_cong_ai', return_value=provider), \
                patch.object(module, '_kiem_local', return_value=san_sang) as kiem:
            kwargs = dict(kiem_chu_ky=lambda *a: True, nhan_viec=Mock(),
                          bo_ghi=bo_ghi, kiem_schema=Mock(return_value=True), demo=demo)
            if loi_goi:
                with self.assertRaises(LoiBootstrap) as error:
                    module.chay(**kwargs)
                self.assertEqual(error.exception.ma, 'AI_GOI_HONG_PHIEN_BAN')
                self.assertEqual(str(error.exception), 'Gói Hỏi AI hỏng phiên bản.')
                self.assertIsNone(error.exception.__context__)
                self.assertEqual(bootstrap._ra.getvalue(), b'')
                self.assertFalse(bootstrap._duoc_accept)
                tao_vong.assert_not_called()
                tao_bi_mat.assert_not_called()
                kiem.assert_not_called()
                bootstrap.socket.close.assert_called_once_with()
                bootstrap.bi_mat.thu_hoi.assert_called_once_with()
            elif san_sang:
                module.chay(**kwargs)
                vong.bat_dau.assert_called_once_with()
                if not demo:
                    kiem.assert_called_once_with(provider)
                    self.assertFalse(provider.cai_dat['cloud_bat'])
            else:
                with self.assertRaises(LoiBootstrap) as error:
                    module.chay(**kwargs)
                self.assertEqual(error.exception.ma, 'CHUA_SAN_SANG')
                vong.bat_dau.assert_not_called()
                self.assertEqual(bootstrap._ra.getvalue(), b'')
            bootstrap.socket.accept.assert_not_called()
        return [json.loads(line) for line in bootstrap._ra.getvalue().splitlines()]

    def test_readiness_thuc_gui_dung_phien_ban_manifest_va_contract_v2(self):
        module = self.nap_runtime(self.manifest)
        messages = self.chay_readiness(module)
        self.assertEqual(messages[0]['phien_ban'], self.manifest['phien_ban'])
        self.assertEqual(messages[0]['contracts'], ['hoi_ai.v2', 'tra_loi_ai.v2'])
        self.assertEqual([m['kieu'] for m in messages], ['san_sang', 'da_thu_hoi'])

    def test_doi_manifest_trong_ram_readiness_tu_dong_theo_ban_moi(self):
        manifest = {**self.manifest, 'phien_ban': '9.8.7-demo.6'}
        module = self.nap_runtime(manifest)
        self.assertEqual(module.PHIEN_BAN, manifest['phien_ban'])
        self.assertEqual(self.chay_readiness(module)[0]['phien_ban'], manifest['phien_ban'])
        self.assertEqual(runtime.PHIEN_BAN, self.manifest['phien_ban'])

    def test_model_chua_san_sang_khong_gui_readiness_khong_nhan_viec(self):
        self.chay_readiness(self.nap_runtime(self.manifest), san_sang=False)

    def test_demo_khong_cong_bo_contract_that(self):
        messages = self.chay_readiness(self.nap_runtime(self.manifest), demo=True)
        self.assertEqual(messages[0]['phien_ban'], self.manifest['phien_ban'])
        self.assertEqual(messages[0]['contracts'], [])

    def test_manifest_hong_hoac_thieu_phien_ban_bao_loi_huu_han(self):
        variants = ({}, [], None, {'phien_ban': None}, {'phien_ban': 1},
                    {'phien_ban': ''}, {'phien_ban': '  '}, {'phien_ban': 'không hợp lệ'},
                    {'phien_ban': '1.2.3\n'}, b'{', b'\xff', b'[' * 2000)
        for manifest in variants:
            with self.subTest(manifest=manifest):
                module = self.nap_runtime(manifest)
                self.assertIsNone(module.PHIEN_BAN)
                self.chay_readiness(module, loi_goi=True)

    def test_manifest_thieu_hoac_khong_doc_duoc_khong_lo_duong_dan(self):
        for error in (FileNotFoundError('DEMO-nguon-thieu'), PermissionError('DEMO-duong-dan')):
            with self.subTest(loi=type(error).__name__):
                module = self.nap_runtime({}, loi_doc=error)
                self.assertIsNone(module.PHIEN_BAN)
                self.chay_readiness(module, loi_goi=True, demo=True)

    def test_manifest_qua_lon_chan_truoc_json_va_khong_doc_het(self):
        raw = json.dumps(self.manifest).encode('utf-8')
        raw += b' ' * (64 * 1024 + 1 - len(raw))
        with patch.object(json, 'loads', side_effect=AssertionError('Không parse tệp quá lớn')):
            module = self.nap_runtime(raw)
        self.assertIsNone(module.PHIEN_BAN)
        self.chay_readiness(module, loi_goi=True)

    def test_manifest_dung_gioi_han_van_readiness_binh_thuong(self):
        raw = json.dumps(self.manifest).encode('utf-8')
        module = self.nap_runtime(raw + b' ' * (64 * 1024 - len(raw)))
        self.assertEqual(self.chay_readiness(module)[0]['phien_ban'], self.manifest['phien_ban'])


if __name__ == '__main__':
    unittest.main()
