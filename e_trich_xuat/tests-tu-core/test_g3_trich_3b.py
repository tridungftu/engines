"""TRICH-3b: Core/SDK và CongAI thật, transport AI + kênh Core DEMO.

Không PostgreSQL/server/AI/Mask thật. Tái dùng fixture TRICH-1b/3a;
test adapter không thay phép đo độ chính xác TRICH-4b. Giữ tệp DEMO.
"""

import ast
import builtins
from contextlib import ExitStack
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys
import threading
import unittest
from unittest.mock import Mock, patch
import urllib.request

from kho_tri_thuc.engines.e_trich_xuat import tich_hop as trich
from kho_tri_thuc.m4.review_goc.trich_xuat import doc_hop_dong, cloud
from kho_tri_thuc.sdk_core.engine import LoiEngine, SDKEngine
from kho_tri_thuc.tri_thuc import ai_cuc_bo
from kho_tri_thuc.tri_thuc.cong_ai import CongAI

try:
    from .test_g3_trich_1b import TEXT, TransportGia, cong, tao_docx
    from .test_g3_trich_3a import KenhGia, _dau_vao, _schema, PHAN_HOI, MA, _lease
except ImportError:
    from test_g3_trich_1b import TEXT, TransportGia, cong, tao_docx
    from test_g3_trich_3a import KenhGia, _dau_vao, _schema, PHAN_HOI, MA, _lease


def _tham_chieu_lhd_e2(node):
    """LHD-E2: thêm nhận loại + phiên bản; thuật toán XD không đổi.

    Cập nhật AST THAM CHIẾU tại đúng các seam mới; AST production vẫn so
    toàn bộ, không bỏ hàm/nhánh thuật toán, dẫn chứng, rà lại hay ánh xạ.
    SHA nguồn cũ vẫn được kiểm trước khi áp dụng các thay đổi này.
    """
    node = deepcopy(node)
    if node.name == 'anh_xa_tham_so':
        node.args.kwonlyargs.append(ast.arg(arg='params'))
        node.args.kw_defaults.append(ast.Constant(value=None))
        node.body[1] = ast.If(test=ast.parse('params is None', mode='eval').body,
                              body=[node.body[1]], orelse=[])
        for statement in node.body:
            if (isinstance(statement, ast.Assign)
                    and ast.dump(statement.targets[0]) == ast.dump(ast.Name(id='params', ctx=ast.Store()))):
                statement.value = ast.parse('danh_muc_xd() if params is None else params', mode='eval').body
    elif node.name == 'TrichXuat':
        init = next(n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == '__init__')
        for name, value in (('params', None), ('loai_hop_dong', 'XD'), ('ten_loai', 'Hợp đồng xây dựng')):
            init.args.kwonlyargs.append(ast.arg(arg=name))
            init.args.kw_defaults.append(ast.Constant(value=value))
        for statement in init.body:
            if isinstance(statement, ast.Assign) and isinstance(statement.targets[0], ast.Attribute):
                if statement.targets[0].attr == 'params':
                    statement.value = ast.parse('danh_muc_xd() if params is None else params', mode='eval').body
                elif statement.targets[0].attr == 'ai':
                    statement.value.keywords.extend([
                        ast.keyword(arg='loai_hop_dong', value=ast.Name(id='loai_hop_dong', ctx=ast.Load())),
                        ast.keyword(arg='ten_loai', value=ast.Name(id='ten_loai', ctx=ast.Load()))])
        for sub in ast.walk(node):
            if isinstance(sub, ast.ImportFrom) and sub.module == 'm4.review_goc.trich_xuat.xuat':
                sub.module, sub.level = 'vendor.review.xuat', 1
    return node


class ImportVaNguonTests(unittest.TestCase):
    def test_import_va_catalog_trong_env_con_khong_home(self):
        from kho_tri_thuc.core.tien_trinh import env_con
        from kho_tri_thuc.engines.e_trich_xuat import tham_so

        env = env_con()
        for key in ('USERPROFILE', 'HOMEPATH', 'HOME', 'HD_THU_MUC_KHOA'):
            self.assertNotIn(key, {k.upper() for k in env})
        code = '''
import json
import os
import sys
assert not {'USERPROFILE', 'HOMEPATH', 'HOME', 'HD_THU_MUC_KHOA'} & set(os.environ)
from kho_tri_thuc.engines.e_trich_xuat import tich_hop
assert not any(name in sys.modules for name in (
    'kho_tri_thuc.m4.review_goc.trich_xuat.danh_muc',
    'kho_tri_thuc.m4.review_goc.trich_xuat.cau_hinh'))
print(json.dumps(tich_hop.danh_muc_xd(), ensure_ascii=False))
'''
        result = subprocess.run([sys.executable, '-X', 'utf8', '-B', '-c', code],
            env=env, cwd=Path(__file__).resolve().parents[1],
            capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), tham_so.danh_muc_xd())

    def test_import_sach_khong_keo_client_rieng(self):
        # Nạp lại entry khi module cũ chưa có trong sys.modules. Chặn cả
        # import bắc cầu dù test fixture khác đã nạp review gốc trước đó.
        import sys
        import types
        from importlib.util import resolve_name
        name = trich.__name__
        real_import = builtins.__import__
        blocked = {
            'kho_tri_thuc.engines.e_trich_xuat.' + n
            for n in ('tham_so', 'chay', 'quy_trinh')
        } | {
            'kho_tri_thuc.m4.review_goc.trich_xuat.' + n
            for n in ('quy_trinh', 'ai_local', 'ai_cloud', 'may_ai', 'cloud',
                      'danh_muc', 'cau_hinh')
        }

        def guard(module, globals=None, locals=None, fromlist=(), level=0):
            base = resolve_name('.' * level + module, globals['__package__']) if level else module
            names = {base} | {base + '.' + n for n in (fromlist or ())}
            self.assertFalse(names & blocked, names & blocked)
            return real_import(module, globals, locals, fromlist, level)

        fresh = types.ModuleType(name)
        fresh.__package__ = trich.__package__
        # LHD-E2: mô phỏng module import thật, có __file__ cho catalog legacy.
        fresh.__file__ = trich.__file__
        with patch.dict(sys.modules):
            for key in tuple(sys.modules):
                if key.startswith(('kho_tri_thuc.engines.e_trich_xuat',
                                   'kho_tri_thuc.m4.review_goc.trich_xuat')):
                    sys.modules.pop(key)
            sys.modules[name] = fresh
            with patch.object(builtins, '__import__', guard):
                exec(compile(Path(trich.__file__).read_text(encoding='utf-8'),
                             trich.__file__, 'exec'), fresh.__dict__)
                data = _dau_vao()
                raw, text = fresh.BackendTrichXuat(cong_ai=cong()).xu_ly(data)
                mapped = fresh.anh_xa_tham_so(raw, tep_id=data['tep_id'],
                    phan_hoi_nguon_tep_id=PHAN_HOI, van_ban=text,
                    loai_hop_dong=data['loai_hop_dong'], danh_muc_id=data['danh_muc_id'],
                    danh_muc_sha256=data['danh_muc_sha256'])
            self.assertEqual(len(mapped['tham_so']), 37)
            self.assertFalse(set(sys.modules) & blocked)

    def test_than_ham_nguon_sha_khong_doi_thuat_toan(self):
        root = Path(__file__).resolve().parents[1]
        own = ast.parse(Path(trich.__file__).read_text(encoding='utf-8'))
        own_defs = {n.name: n for n in own.body
                    if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        selected = {
            'tham_so': ('anh_xa_tham_so',),
            'danh_muc': ('_split', '_muc', 'ten_ngan', 'to_param'),
            'quy_trinh': ('ten_an_toan', 'build_prompt', 'chia_doan',
                         'ghep_kiem_tra', '_co_gia_tri', 'TrichXuat'),
            'chay': ('_ban_giao', 'xu_ly_viec', '_VongNhan', 'chay'),
        }
        for source, sha in trich.NGUON_CHEP.items():
            path = root / source
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), sha)
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in selected[path.stem]:
                    copied_name = '_chay_khung' if path.stem == 'chay' and node.name == 'chay' else node.name
                    node.name = copied_name
                    self.assertEqual(ast.dump(_tham_chieu_lhd_e2(node), include_attributes=False),
                                     ast.dump(own_defs[copied_name], include_attributes=False))

    def test_gate_ast_van_bat_doi_thuat_toan(self):
        # Mutation probe: sửa kết quả rà lại hoặc bỏ kiểm revision đều bị bắt.
        path = Path(trich.__file__)
        tree = ast.parse(path.read_text(encoding='utf-8'))
        read_text = Path.read_text
        for name in ('TrichXuat', 'anh_xa_tham_so'):
            changed_tree = deepcopy(tree)
            changed = next(n for n in changed_tree.body if getattr(n, 'name', '') == name)
            if name == 'TrichXuat':
                method = next(n for n in changed.body if getattr(n, 'name', '') == 'ra_lai')
                method.body[-1] = ast.parse('return 0').body[0]
            else:
                changed.body = [n for n in changed.body if not (
                    isinstance(n, ast.If) and 'revision' in ast.unparse(n.test))]
            mutated = ast.unparse(changed_tree)

            def read_mutated(tep, *args, **kwargs):
                return mutated if tep == path else read_text(tep, *args, **kwargs)

            # Chạy chính gate so với AST tham chiếu đã ghim, không chỉ so
            # hai AST tự dựng với nhau. Không sửa tệp production trên đĩa.
            with self.subTest(ham=name), patch.object(Path, 'read_text', read_mutated):
                with self.assertRaises(AssertionError):
                    self.test_than_ham_nguon_sha_khong_doi_thuat_toan()


class Trich3bTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.dict(ai_cuc_bo._CONNECTION_FAILURES, {}, clear=True))
        for obj, name in ((urllib.request, 'urlopen'), (urllib.request, 'build_opener'),
                          (socket, 'create_connection'), (socket.socket, 'connect'),
                          (subprocess, 'Popen'), (subprocess, 'run'),
                          (doc_hop_dong, '_word'), (cloud, 'kiem_tra_cloud'),
                          (trich.TrichXuat, 'ocr_pdf')):
            self.stack.enter_context(patch.object(obj, name, side_effect=AssertionError(name)))

    def dau_vao(self):
        data = _dau_vao()
        data['docx'] = tao_docx()
        data['out_dir'] = data['docx'].parent / 'DEMO-out'
        return data

    def test_core_cong_ai_37_ma_nguon_hash_dan_chung(self):
        data, c = self.dau_vao(), cong()
        kenh = KenhGia(data)
        settings = deepcopy(c.cai_dat)
        before = data['docx'].read_bytes()
        lease = _lease()
        result = trich.xu_ly_viec(SDKEngine(lease, kenh_core=kenh),
                                backend=trich.BackendTrichXuat(cong_ai=c))
        self.assertEqual(result, {'ket_qua_id': 'DEMO_DA_NHAN'})
        self.assertEqual([op for op, _ in kenh.go], ['doc_dau_vao', 'ghi_ket_qua', 'ghi_ket_qua'])
        self.assertTrue(all(giu is lease for _, giu in kenh.go))
        source, mapped = (json.loads(kenh.raw[n]) for n in ('phan-hoi-nguon.json', 'tham-so.json'))
        self.assertEqual(tuple(r['ma'] for r in source['bang']), MA)
        self.assertEqual(tuple(r['ma'] for r in mapped['tham_so']), MA)
        self.assertEqual(mapped['phan_hoi_nguon_tep_id'], PHAN_HOI)
        self.assertEqual(mapped['nguon_tep_ids'], [data['tep_id']])
        provenance = source['nguon']
        self.assertEqual(provenance['tep_id'], data['tep_id'])
        self.assertEqual(provenance['sha256'], hashlib.sha256(before).hexdigest())
        for k in ('danh_muc_id', 'danh_muc_sha256', 'loai_hop_dong'):
            self.assertEqual(provenance[k], data[k])
            self.assertEqual(mapped[k], data[k])
        self.assertEqual(provenance['phien_ban_nguon'], trich.PHIEN_BAN_NGUON)
        for k, module in (('quy_trinh', trich), ('ai_chung', trich.ai_chung)):
            self.assertEqual(provenance[k], dict(duong_dan=module.NGUON, sha256=module.NGUON_SHA256))
        for raw, row in zip(source['bang'], mapped['tham_so']):
            for k in ('ghi_chu', 'kiem_tra', 'dieu_khoan', 'trich_dan', 'vi_tri_do_duoc'):
                self.assertIn(k, raw)
            self.assertEqual(row['gia_tri'], {'kieu': 'van_ban', 'gia_tri': '00007'})
            self.assertEqual(row['dan_chung'][0]['trich_dan'], TEXT)
            self.assertEqual(row['dan_chung'][0]['vi_tri']['tep_id'], data['tep_id'])
        self.assertEqual(source['phieu_kiem_tra']['accept_by'], 'Python')
        self.assertTrue(source['phan_hoi_ai'])
        self.assertTrue(all(x['ma_yeu_cau'] and x['duong'] == 'LOCAL' for x in source['phan_hoi_ai']))
        self.assertFalse(source['tom_tat']['token_da_do'])
        self.assertEqual(c.cai_dat, settings)
        self.assertEqual(c._mask.mock_calls + c._nha_cung_cap.mock_calls, [])
        self.assertEqual(data['docx'].read_bytes(), before)
        self.assertTrue(all(s.closed for s in kenh.luong.values()))
        _schema(mapped, 'ky_thuat.json', 'urn:ktt:contract:tham_so.v1')

    def test_retry_ack_khong_trich_lai_va_cho_nguon_truoc_anh_xa(self):
        for ten in ('phan-hoi-nguon.json', 'tham-so.json'):
            with self.subTest(ten=ten):
                transport = TransportGia()
                kenh = KenhGia(self.dau_vao(), giu=ten, loi=ten)
                backend = Mock(wraps=trich.BackendTrichXuat(cong_ai=cong(transport)))
                result, errors = [], []

                def run():
                    try:
                        result.append(trich.xu_ly_viec(SDKEngine(_lease(), kenh_core=kenh), backend=backend))
                    except Exception as exc:
                        errors.append(exc)

                worker = threading.Thread(target=run)
                worker.start()
                try:
                    self.assertTrue(kenh.cho_ack.wait(10))
                    n_calls = len(transport.prompts)
                    self.assertGreater(n_calls, 0)
                    self.assertTrue(worker.is_alive())
                    self.assertEqual(result, [])
                    self.assertEqual(kenh.dem[ten], 2)
                    if ten == 'phan-hoi-nguon.json':
                        self.assertNotIn('tham-so.json', kenh.raw)
                finally:
                    kenh.ack.set()
                    worker.join(10)
                self.assertFalse(worker.is_alive())
                self.assertEqual(errors, [])
                self.assertEqual(result, [{'ket_qua_id': 'DEMO_DA_NHAN'}])
                backend.xu_ly.assert_called_once()
                self.assertEqual(len(transport.prompts), n_calls)
                self.assertTrue(all(s.closed for s in kenh.luong.values()))

    def test_thieu_va_loi_ai_khong_bien_thanh_0_hoac_cloud(self):
        for transport in (TransportGia(rong=True), Mock(side_effect=ConnectionError('DEMO'))):
            with self.subTest(transport=type(transport).__name__):
                c, kenh = cong(transport), KenhGia(self.dau_vao())
                trich.xu_ly_viec(SDKEngine(_lease(), kenh_core=kenh),
                                backend=trich.BackendTrichXuat(cong_ai=c))
                raw = json.loads(kenh.raw['phan-hoi-nguon.json'])
                mapped = json.loads(kenh.raw['tham-so.json'])
                self.assertEqual(len(mapped['tham_so']), 37)
                self.assertTrue(all(r['gia_tri']['kieu'] == 'chua_ro' and r['can_soat']
                                    for r in mapped['tham_so']))
                self.assertTrue(raw['phan_hoi_ai'])
                if isinstance(transport, Mock):
                    self.assertGreater(raw['tom_tat']['loi_ai'], 0)
                self.assertEqual(c._mask.mock_calls + c._nha_cung_cap.mock_calls, [])

    def test_sai_catalog_tep_pdf_khong_goi_ai_hay_ban_giao(self):
        data, c = self.dau_vao(), cong()
        changes = ({'loai_hop_dong': 'MUA_HH'}, {'danh_muc_id': ''},
                   {'danh_muc_sha256': '0' * 64}, {'tep_id': 'DEMO-sai'},
                   {'docx': 'DEMO.doc'}, {'docx': 'DEMO.PDF'})
        with patch.object(CongAI, 'goi') as goi:
            for change in changes:
                with self.subTest(change=change):
                    kenh = KenhGia(data | change)
                    with self.assertRaises(ValueError) as error:
                        trich.xu_ly_viec(SDKEngine(_lease(), kenh_core=kenh),
                                        backend=trich.BackendTrichXuat(cong_ai=c))
                    if change.get('docx') == 'DEMO.PDF':
                        self.assertEqual(error.exception.ma, 'CHUA_KIEM')
                        self.assertIn('OCR-5b', str(error.exception))
                    self.assertEqual(kenh.raw, {})
            goi.assert_not_called()

    def test_tep_doi_giua_luot_khong_ban_giao(self):
        kenh = KenhGia(self.dau_vao())
        original = trich.TrichXuat.xu_ly

        def xu_ly(tx, path):
            result = original(tx, path)
            with path.open('ab') as f:
                f.write(b'DEMO changed')
            return result

        with patch.object(trich.TrichXuat, 'xu_ly', xu_ly):
            with self.assertRaisesRegex(ValueError, 'TEP_NGUON_DA_DOI'):
                trich.xu_ly_viec(SDKEngine(_lease(), kenh_core=kenh),
                                backend=trich.BackendTrichXuat(cong_ai=cong()))
        self.assertEqual(kenh.raw, {})

    def test_cloud_va_sai_sdk_mat_lease_bi_chan(self):
        for value in ({}, False, {'bat': True}):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'CLOUD_BI_CHAN'):
                trich.BackendTrichXuat(cong_ai=cong(), cloud=value)
        with self.assertRaises(TypeError):
            trich.BackendTrichXuat(cong_ai=object())
        backend = Mock()
        with self.assertRaises(TypeError):
            trich.xu_ly_viec(object(), backend=backend)
        lease = replace(_lease(), giu_den=datetime.now(timezone.utc) - timedelta(seconds=1))
        kenh = KenhGia(self.dau_vao())
        with self.assertRaisesRegex(LoiEngine, 'VIEC_MAT_LEASE'):
            trich.xu_ly_viec(SDKEngine(lease, kenh_core=kenh), backend=backend)
        backend.xu_ly.assert_not_called()
        self.assertEqual(kenh.go, [])

    def test_khung_readiness_chua_cong_bo_capability(self):
        b = Mock()
        with patch.object(trich.Bootstrap, 'nhan', return_value=b), \
                patch.object(trich, '_VongNhan') as vong:
            vong.return_value.drain.return_value = True
            trich.chay(kiem_chu_ky=lambda *_: None, nhan_viec=lambda *_: None, cong_ai=cong())
        self.assertEqual(b.bao_san_sang.call_args.kwargs['contracts'], [])
        self.assertTrue(b.bao_san_sang.call_args.kwargs['kiem_san_sang']())
        b.socket.close.assert_called_once()
        with patch.object(trich, 'danh_muc_xd', side_effect=ValueError('TRICH_DANH_MUC_SAI_HASH')):
            with self.assertRaisesRegex(ValueError, 'DANH_MUC_SAI_HASH'):
                trich.BackendTrichXuat(cong_ai=cong()).san_sang()


if __name__ == '__main__':
    unittest.main()
