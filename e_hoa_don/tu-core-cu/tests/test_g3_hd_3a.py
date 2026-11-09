"""HD-3a: XML DEMO/Core giả; Python/Node/socket/Windows Job thật.

Wire trong test chỉ là seam DEMO; không protocol portal nguồn, không thuế,
Chromium, CSDL hoặc tài khoản riêng/ACL (HD-3b).
"""

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import ctypes
import io
import json
import os
from pathlib import Path
import shutil
import socket
import sys
import threading
import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from kho_tri_thuc.core import tien_trinh as tt
from kho_tri_thuc.core.phien import MaBiMat
from kho_tri_thuc.core.viec import GiuViec
from kho_tri_thuc.engines.e_hoa_don import chay as hd
from kho_tri_thuc.sdk_core import bootstrap as bs
from kho_tri_thuc.sdk_core.engine import KenhCore, LoiEngine, SDKEngine

try:
    from .test_g2_21 import SoGia, _dong
    from .test_g3_hd_1 import RAW, CTX, XML_ID, DETAIL_ID
    from . import test_g2_17 as schema_tests
except ImportError:
    from test_g2_21 import SoGia, _dong
    from test_g3_hd_1 import RAW, CTX, XML_ID, DETAIL_ID
    import test_g2_17 as schema_tests

NODE = shutil.which('node')
METADATA = dict(bien_the='hoa_don', ma_contract='hoa_don.v1',
    phien_ban_contract='1.0.0', trang_thai='CHUA_DUYET', ly_do=None,
    revision_truoc=0, nguon=[])


def _lease():
    return GiuViec(viec_id=uuid4(), buoc_viec_id=uuid4(), lan_thu_id=uuid4(),
        phap_nhan_id=uuid4(), module='demo', hanh_dong='DEMO:HD:DOC',
        instance_id=uuid4(), the_he=1,
        giu_den=datetime.now(timezone.utc) + timedelta(minutes=2),
        ma=MaBiMat('n' * 43))


class KenhGia(KenhCore):
    def __init__(self, conn=None, *, cho_ack=False, loi_lan_dau=False):
        self.conn, self.cho_ack, self.loi_lan_dau = conn, cho_ack, loi_lan_dau
        self.go = []
        self.luong = self.raw = self.nguon = None

    def goi(self, operation, giu_viec, **payload):
        self.go.append(operation)
        if operation == 'doc_dau_vao':
            # Core đã lưu chi tiết HD-1 riêng trước khi cấp ID cho engine.
            return dict(tep_xml_id=XML_ID, chi_tiet_nguon_tep_id=DETAIL_ID,
                context=CTX, du_lieu_ket_qua=dict(METADATA), revision_tep_truoc=0)
        if operation == 'mo_doc':
            assert payload == {'tep_id': XML_ID}
            self.nguon = io.BytesIO(RAW)
            return self.nguon
        assert operation == 'ghi_ket_qua'
        self.raw = payload['luong'].read()
        assert payload['du_lieu'] == METADATA
        assert payload['revision_tep_truoc'] == 0
        if self.luong is not None:
            assert self.luong is payload['luong'] and not self.luong.closed
        self.luong = payload['luong']
        if self.loi_lan_dau:
            self.loi_lan_dau = False
            if self.conn is not None:
                self.conn.sendall(b'loi_ban_giao\n')
            raise RuntimeError('HD3A_CANARY')
        if self.conn is not None:
            if self.cho_ack:
                self.conn.sendall(b'cho_core\n')
                assert self.conn.recv(32) == b'core_da_nhan\n'
            self.conn.sendall(self.raw + b'\n')
        return {'ket_qua_id': 'DEMO_DA_NHAN'}


class DongHoGia:
    """Đánh thức lịch heartbeat bằng thời gian giả, không ngủ 120 giây."""

    def __init__(self):
        self.gio = datetime(2026, 10, 31, tzinfo=timezone.utc)
        self.khoa = threading.Condition()
        self.da_cho = threading.Event()
        self.dung = False

    def __call__(self):
        with self.khoa:
            return self.gio

    def wait(self, giay):
        with self.khoa:
            den = self.gio + timedelta(seconds=giay)
            self.da_cho.set()
            self.khoa.wait_for(lambda: self.dung or self.gio >= den)
            return self.dung

    def set(self):
        with self.khoa:
            self.dung = True
            self.khoa.notify_all()

    def tang(self):
        self.da_cho.wait(0.2)
        with self.khoa:
            self.da_cho.clear()
            self.gio += timedelta(seconds=30)
            self.khoa.notify_all()
        return self.da_cho.wait(0.2)


def _child():
    def nhan_viec(conn, bo_doc):
        raw = conn.recv(64)
        assert raw in (b'DEMO_HD3A\n', b'DEMO_HD3A_GIU\n', b'DEMO_HD3A_LOI\n')
        return SDKEngine(_lease(), kenh_core=KenhGia(conn,
            cho_ack=raw != b'DEMO_HD3A\n', loi_lan_dau=raw == b'DEMO_HD3A_LOI\n'))

    def khong_nhan_the(*_):
        raise ValueError('Không cấp thẻ request trong seam DEMO')

    hd.chay(kiem_chu_ky=khong_nhan_the, nhan_viec=nhan_viec,
            node_executable=NODE)


class HDThuanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        schema_tests.BundleContractTest.setUpClass()
        cls.validator = schema_tests.BundleContractTest()

    def test_manifest_chi_doc_xml_khong_tai_gia_khong_ngoai_le_man_hinh(self):
        manifest = json.loads((ROOT / 'engines/e_hoa_don/engine.json')
                              .read_text(encoding='utf-8'))
        self.validator.validate('urn:ktt:manifest:engine.v1', manifest)
        self.assertEqual([c['ma'] for c in manifest['capability']], ['hoa_don.doc_xml@1'])
        self.assertEqual(manifest['phien_ban'], hd.PHIEN_BAN)
        self.assertEqual([c['dau_ra'] for c in manifest['capability']], hd.CONTRACTS)
        self.assertTrue(manifest['ho_so_chay_mau']['headless'])
        self.assertNotIn('ngoai_le_man_hinh', manifest['ho_so_chay_mau'])

    def test_xml_qua_sdk_dung_hd1_va_schema_khong_tu_nhan_nghiep_vu(self):
        kenh = KenhGia()
        self.assertEqual(hd.xu_ly_viec(SDKEngine(_lease(), kenh_core=kenh)),
                         {'ket_qua_id': 'DEMO_DA_NHAN'})
        data = json.loads(kenh.raw)
        self.validator.validate('urn:ktt:contract:hoa_don.v1', data)
        self.assertEqual(data['dau_hoa_don']['so_hoa_don'], '000001')
        self.assertEqual(data['dong'][0]['so_luong']['gia_tri'], '1.250000')
        self.assertEqual(data['tep_xml_id'], XML_ID)
        self.assertEqual(data['chi_tiet_nguon_tep_id'], DETAIL_ID)
        self.assertEqual(data, hd.doc_xml(RAW, CTX, tep_xml_id=XML_ID,
                                        chi_tiet_nguon_tep_id=DETAIL_ID).hoa_don)
        self.assertEqual(kenh.go, ['doc_dau_vao', 'mo_doc', 'ghi_ket_qua'])
        self.assertTrue(kenh.luong.closed and kenh.nguon.closed)

    def test_retry_giu_cung_ket_qua_khong_doc_lai_cho_den_ack(self):
        kenh = KenhGia(loi_lan_dau=True)
        goc = kenh.goi
        cho, ack = threading.Event(), threading.Event()
        cac_luong, raws, ket_qua = [], [], []
        def goi(operation, *args, **payload):
            if operation == 'ghi_ket_qua':
                cac_luong.append(payload['luong'])
                raws.append(payload['luong'].getvalue())
                if len(cac_luong) == 2:
                    cho.set()
                    if not ack.wait(3):
                        raise TimeoutError()
            return goc(operation, *args, **payload)
        kenh.goi = goi
        worker = threading.Thread(target=lambda: ket_qua.append(
            hd.xu_ly_viec(SDKEngine(_lease(), kenh_core=kenh))))
        with patch.object(hd, 'doc_xml', wraps=hd.doc_xml) as doc:
            worker.start()
            try:
                self.assertTrue(cho.wait(2))
                self.assertTrue(worker.is_alive())
                self.assertEqual(ket_qua, [])
                self.assertIs(cac_luong[0], cac_luong[1])
                self.assertFalse(cac_luong[0].closed)
            finally:
                ack.set()
                worker.join(3)
            doc.assert_called_once()
        self.assertFalse(worker.is_alive())
        self.assertEqual(ket_qua, [{'ket_qua_id': 'DEMO_DA_NHAN'}])
        self.assertEqual(raws, [kenh.raw, kenh.raw])
        self.assertTrue(cac_luong[0].closed)

    def test_mat_lease_khong_doc_khong_ban_giao(self):
        kenh = KenhGia()
        giu = replace(_lease(), giu_den=datetime.now(timezone.utc) - timedelta(seconds=1))
        with self.assertRaisesRegex(LoiEngine, 'VIEC_MAT_LEASE'):
            hd.xu_ly_viec(SDKEngine(giu, kenh_core=kenh))
        self.assertEqual(kenh.go, [])
        with self.assertRaises(TypeError):
            hd.xu_ly_viec(object())

    def test_heartbeat_giu_lease_retry_qua_120_giay_den_ack(self):
        for loi_heartbeat in (False, True):
            with self.subTest(loi_heartbeat=loi_heartbeat):
                dong_ho, kenh = DongHoGia(), KenhGia()
                giu = replace(_lease(), giu_den=dong_ho() + timedelta(seconds=120))
                goc, nhiep, luong, raws = kenh.goi, [], [], []
                def goi(operation, lease, **payload):
                    if operation == 'heartbeat':
                        nhiep.append(dong_ho())
                        if loi_heartbeat and len(nhiep) == 1:
                            raise RuntimeError('HD3A_HEARTBEAT_CANARY')
                        return replace(lease, giu_den=dong_ho() + timedelta(
                            seconds=payload['lease_giay']))
                    if operation == 'ghi_ket_qua':
                        self.assertGreater(lease.giu_den, dong_ho())
                        luong.append(payload['luong'])
                        raws.append(payload['luong'].read())
                        if dong_ho() < giu.giu_den + timedelta(seconds=30):
                            raise RuntimeError('HD3A_BAN_GIAO_CANARY')
                        payload['luong'].seek(0)
                    return goc(operation, lease, **payload)
                kenh.goi = goi
                def ngu(_):
                    if dong_ho() >= giu.giu_den + timedelta(seconds=60):
                        self.fail('Retry mắc kẹt vì lease hết hạn cục bộ')
                    dong_ho.tang()
                nhip_thread = MagicMock(wraps=threading)
                nhip_thread.Event.return_value = dong_ho
                with patch.object(hd, 'threading', nhip_thread), \
                        patch.object(hd.time, 'sleep', side_effect=ngu), \
                        patch.object(hd, 'doc_xml', wraps=hd.doc_xml) as doc:
                    self.assertEqual(hd.xu_ly_viec(SDKEngine(giu,
                        kenh_core=kenh, dong_ho=dong_ho)), {'ket_qua_id': 'DEMO_DA_NHAN'})
                    doc.assert_called_once()
                self.assertGreaterEqual(len(nhiep), 5)
                self.assertGreater(dong_ho(), giu.giu_den)
                self.assertEqual(len(luong), 6)
                self.assertTrue(all(s is luong[0] for s in luong))
                self.assertTrue(all(raw == raws[0] for raw in raws))
                self.assertTrue(luong[0].closed and dong_ho.dung)
                self.assertFalse(any(t.name == 'hoa-don-heartbeat'
                                     for t in threading.enumerate()))

    def test_heartbeat_khi_doc_xml_va_cho_ack_khong_retry(self):
        for giai_doan in ('doc_xml', 'cho_ack'):
            with self.subTest(giai_doan=giai_doan):
                dong_ho, kenh = DongHoGia(), KenhGia()
                giu = replace(_lease(), giu_den=dong_ho() + timedelta(seconds=120))
                goc, nhiep = kenh.goi, []
                def cho():
                    for _ in range(5):
                        self.assertTrue(dong_ho.tang(), 'Thiếu heartbeat khi giữ việc')
                    self.assertGreater(dong_ho(), giu.giu_den)
                    self.assertEqual(len(nhiep), 5)
                def goi(operation, lease, **payload):
                    if operation == 'heartbeat':
                        nhiep.append(dong_ho())
                        return replace(lease, giu_den=dong_ho() + timedelta(
                            seconds=payload['lease_giay']))
                    if operation == 'ghi_ket_qua' and giai_doan == 'cho_ack':
                        self.assertFalse(payload['luong'].closed)
                        cho()
                        self.assertFalse(payload['luong'].closed)
                    return goc(operation, lease, **payload)
                kenh.goi = goi
                doc_goc = hd.doc_xml
                def doc(*args, **kwargs):
                    if giai_doan == 'doc_xml':
                        cho()
                    return doc_goc(*args, **kwargs)
                nhip_thread = MagicMock(wraps=threading)
                nhip_thread.Event.return_value = dong_ho
                with patch.object(hd, 'threading', nhip_thread), \
                        patch.object(hd, 'doc_xml', side_effect=doc), \
                        patch.object(hd.time, 'sleep', side_effect=AssertionError(
                            'Không được retry khi chỉ đang chờ ACK')):
                    self.assertEqual(hd.xu_ly_viec(SDKEngine(giu,
                        kenh_core=kenh, dong_ho=dong_ho)), {'ket_qua_id': 'DEMO_DA_NHAN'})
                self.assertEqual(kenh.go.count('ghi_ket_qua'), 1)
                self.assertTrue(kenh.luong.closed and kenh.nguon.closed and dong_ho.dung)

    def test_loi_worker_khong_drain_thanh_cong(self):
        b = MagicMock()
        b.accept.side_effect = RuntimeError('HD3A_CANARY')
        vong = hd._VongNhan(b, lambda *_: None)
        vong.bat_dau()
        vong.worker.join(2)
        self.assertFalse(vong.drain())
        self.assertTrue(vong.loi)

    def test_node_chua_ready_khong_bao_ready_va_dong_listener(self):
        b = MagicMock()
        b.tham_so = {'cong_node_demo': 19123}
        b._cfg = {'instance_id': str(uuid4())}
        with patch.object(hd.Bootstrap, 'nhan', return_value=b), \
                patch.object(hd, 'NodeGia') as Node:
            Node.return_value.bat_dau.side_effect = bs.LoiBootstrap('CONG_BI_CHIEM')
            with self.assertRaisesRegex(bs.LoiBootstrap, 'CONG_BI_CHIEM'):
                hd.chay(kiem_chu_ky=lambda *_: None, nhan_viec=lambda *_: None,
                        node_executable='C:\\DEMO\\node.exe')
            b.bao_san_sang.assert_not_called()
            Node.return_value.dong.assert_called_once()
        b.socket.close.assert_called_once()

    def test_node_phai_o_job_va_khong_nhan_cong_tu_do(self):
        for cong in (0, 80, 65536, True, '19123'):
            with self.subTest(cong=cong), self.assertRaises(ValueError):
                hd.NodeGia(node_executable='C:\\DEMO\\node.exe', cong=cong, instance='DEMO')
        node = hd.NodeGia(node_executable=str(ROOT / 'node.exe'), cong=19123, instance='DEMO')
        with patch.object(hd, '_trong_job', return_value=False), \
                patch.object(hd.subprocess, 'Popen') as popen:
            with self.assertRaisesRegex(bs.LoiBootstrap, 'NODE_CAN_JOB_CORE'):
                node.bat_dau()
            popen.assert_not_called()

    def test_node_bind_bi_chiem_bao_dung_ma_chi_spawn_mot_lan(self):
        node = hd.NodeGia(node_executable=str(ROOT / 'node.exe'), cong=19123, instance='DEMO')
        proc = MagicMock(pid=12345, stdin=io.BytesIO(), stdout=io.BytesIO())
        with patch.object(hd, '_trong_job', return_value=True), \
                patch.object(hd.subprocess, 'Popen', return_value=proc) as popen, \
                patch.object(hd, '_doc_dong', return_value=b'{"ma":"CONG_BI_CHIEM"}\n'), \
                patch.dict(os.environ, {'TAX_PASSWORD': 'DEMO_CANARY'}, clear=False):
            with self.assertRaisesRegex(bs.LoiBootstrap, '^CONG_BI_CHIEM$'):
                node.bat_dau()
            popen.assert_called_once()
            args, kwargs = popen.call_args
            self.assertEqual(args[0][-2:], ['--port', '19123'])
            self.assertFalse(kwargs['shell'])
            self.assertTrue(kwargs['close_fds'])
            self.assertEqual(kwargs['creationflags'], hd.subprocess.CREATE_NO_WINDOW)
            self.assertNotIn('TAX_PASSWORD', kwargs['env'])
            self.assertNotIn('DEMO_CANARY', repr((args, kwargs)))
            proc.wait.assert_called_once_with(5)
        self.assertIsNone(node.proc)

    def test_node_readiness_sai_instance_pid_cong_hoac_khong_song_deu_bi_chan(self):
        ready = dict(demo=True, instance='DEMO', pid=12345, port=19123)
        for doi in ({'instance': 'CU'}, {'pid': 12346}, {'port': 19124}, {}):
            with self.subTest(doi=doi):
                node = hd.NodeGia(node_executable=str(ROOT / 'node.exe'),
                                  cong=19123, instance='DEMO')
                proc = MagicMock(pid=12345, stdin=io.BytesIO(), stdout=io.BytesIO())
                proc.poll.return_value = None if doi else 1
                with patch.object(hd, '_trong_job', return_value=True), \
                        patch.object(hd.subprocess, 'Popen', return_value=proc), \
                        patch.object(hd, '_doc_dong', return_value=json.dumps({**ready, **doi}).encode()):
                    with self.assertRaisesRegex(bs.LoiBootstrap, 'NODE_CHUA_SAN_SANG'):
                        node.bat_dau()
                self.assertIsNone(node.proc)

    def test_xml_qua_lon_dong_nguon_khong_parse_khong_ban_giao(self):
        kenh, goc = KenhGia(), KenhGia.goi
        def goi(operation, *args, **payload):
            if operation == 'mo_doc':
                kenh.go.append(operation)
                kenh.nguon = io.BytesIO(b'x' * (16 * 1024 * 1024 + 1))
                return kenh.nguon
            return goc(kenh, operation, *args, **payload)
        kenh.goi = goi
        with patch.object(hd, 'doc_xml') as doc:
            with self.assertRaisesRegex(ValueError, '16 MiB'):
                hd.xu_ly_viec(SDKEngine(_lease(), kenh_core=kenh))
            doc.assert_not_called()
        self.assertTrue(kenh.nguon.closed)
        self.assertEqual(kenh.go, ['doc_dau_vao', 'mo_doc'])


@unittest.skipUnless(os.name == 'nt' and hasattr(socket.socket, 'share') and NODE,
                     'CHUA_KIEM: cần Windows share/fromshare, Job và Node')
class HDTienTrinhTest(unittest.TestCase):
    def setUp(self):
        self.controllers = []
        self.addCleanup(self._dong)

    def _dong(self):
        for c in self.controllers:
            if c._proc is not None:
                try:
                    c.thu_hoi(timeout=5)
                except tt.LoiTienTrinh:
                    c._job.ket_thuc()
                    c._proc.wait(5)
                    c.kiem_con()
            c.dong()

    def _cong(self):
        with socket.socket() as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            s.bind(('127.0.0.1', 0))
            return s.getsockname()[1]

    def _tao(self, *, cong=None, cong_node=None, **doi):
        cong = self._cong() if cong is None else cong
        cong_node = self._cong() if cong_node is None else cong_node
        while cong_node == cong:
            cong_node = self._cong()
        d = _dong()
        d.update(module=None, engine_ho_so_id=str(uuid4()), cong=cong)
        so = SoGia(d)
        c = tt.TienTrinhCore(so_cong_id=d['id'], giao_dich=so.giao_dich,
            lenh=[sys.executable, '-B', '-X', 'utf8', str(Path(__file__).resolve()), '--child'],
            phien_ban=hd.PHIEN_BAN, issuer='core-demo', contracts=hd.CONTRACTS,
            ma_chu='e_hoa_don', tham_so={'cong_node_demo': cong_node},
            cho_khoi_dong=10, cho_dung=2, **doi)
        self.controllers.append(c)
        return c, so, cong_node

    def _conn(self, cong):
        conn = socket.create_connection(('127.0.0.1', cong), timeout=3)
        self.addCleanup(conn.close)
        return conn

    def _node(self, c, cong):
        with self._conn(cong) as conn, conn.makefile('rb') as reader:
            info = json.loads(reader.readline())
        self.assertEqual(info['instance'], str(c.instance_id))
        self.assertTrue(info['demo'])
        self.assertEqual(info['port'], cong)
        from ctypes import wintypes as w
        k = ctypes.WinDLL('kernel32', use_last_error=True)
        k.OpenProcess.argtypes, k.OpenProcess.restype = [w.DWORD, w.BOOL, w.DWORD], w.HANDLE
        k.CloseHandle.argtypes = [w.HANDLE]
        k.IsProcessInJob.argtypes = [w.HANDLE, w.HANDLE, ctypes.POINTER(w.BOOL)]
        k.WaitForSingleObject.argtypes = [w.HANDLE, w.DWORD]
        h = k.OpenProcess(0x100000 | 0x1000, False, info['pid'])
        self.assertTrue(h)
        self.addCleanup(k.CloseHandle, h)
        trong = w.BOOL()
        self.assertTrue(k.IsProcessInJob(h, c._job._h, ctypes.byref(trong)))
        self.assertTrue(trong.value)
        return k, h

    def test_ready_xml_node_trong_dung_job_va_thu_hoi_giu_listener(self):
        c, so, cong_node = self._tao()
        c.khoi_dong()
        proc = c._proc
        k, node = self._node(c, cong_node)
        self.assertEqual((c.trang_thai, c.chu_accept), ('ready', 'con'))
        self.assertGreaterEqual(c._job.so_tien_trinh(), 2)
        with self._conn(so.dong['cong']) as conn, conn.makefile('rb') as reader:
            conn.sendall(b'DEMO_HD3A\n')
            data = json.loads(reader.readline())
            self.assertEqual(data['contract'], 'hoa_don.v1')
            self.assertEqual(data['dau_hoa_don']['so_hoa_don'], '000001')
        self.assertTrue(c.thu_hoi(timeout=5))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(k.WaitForSingleObject(node, 3000), 0)
        self.assertEqual(so.dong['trang_thai'], 'TRONG')
        with self._conn(so.dong['cong']):
            accepted, _ = c.accept(timeout=3)
            accepted.close()

    def test_job_ket_thuc_ca_engine_va_node_stub(self):
        c, so, cong_node = self._tao()
        c.khoi_dong()
        proc, job = c._proc, c._job
        k, node = self._node(c, cong_node)
        job.ket_thuc()
        proc.wait(5)
        self.assertEqual(k.WaitForSingleObject(node, 3000), 0)
        self.assertTrue(c.kiem_con())
        self.assertEqual(so.dong['trang_thai'], 'TRONG')

    def test_engine_crash_node_ket_thuc_khong_mo_coi(self):
        c, so, cong_node = self._tao()
        c.khoi_dong()
        k, node = self._node(c, cong_node)
        c._proc.terminate()
        c._proc.wait(5)
        self.assertEqual(k.WaitForSingleObject(node, 3000), 0)
        self.assertTrue(c.kiem_con())

    def test_drain_va_loi_ban_giao_giu_node_ket_qua_den_ack(self):
        for loi in (False, True):
            with self.subTest(loi=loi):
                c, so, cong_node = self._tao()
                c.khoi_dong()
                proc = c._proc
                k, node = self._node(c, cong_node)
                conn = self._conn(so.dong['cong'])
                reader = conn.makefile('rb')
                self.addCleanup(reader.close)
                conn.sendall(b'DEMO_HD3A_LOI\n' if loi else b'DEMO_HD3A_GIU\n')
                if loi:
                    self.assertEqual(reader.readline(), b'loi_ban_giao\n')
                self.assertEqual(reader.readline(), b'cho_core\n')
                with self.assertRaisesRegex(tt.LoiTienTrinh, 'DUNG_CHUA_XAC_NHAN'):
                    c.thu_hoi(timeout=0.05)
                self.assertEqual(bs.doc_thong_diep(tt._doc_dong(proc.stdout, 3)),
                                 {'protocol': bs.PROTOCOL, 'kieu': 'drain_chua_xong'})
                self.assertIsNone(proc.poll())
                self.assertEqual(k.WaitForSingleObject(node, 0), 258)
                self.assertEqual((c.trang_thai, c.chu_accept), ('dang_dung', 'con'))
                self.assertNotIn('tra', [ten for ten, _ in so.go])
                moi = self._conn(so.dong['cong'])
                moi.sendall(b'DEMO_HD3A\n')
                moi.settimeout(0.1)
                with self.assertRaises(socket.timeout):
                    moi.recv(1024)
                conn.sendall(b'core_da_nhan\n')
                self.assertEqual(json.loads(reader.readline())['contract'], 'hoa_don.v1')
                self.assertEqual(bs.doc_thong_diep(tt._doc_dong(proc.stdout, 5)),
                                 {'protocol': bs.PROTOCOL, 'kieu': 'da_thu_hoi'})
                proc.wait(5)
                self.assertEqual(proc.returncode, 0)
                self.assertEqual(k.WaitForSingleObject(node, 0), 0)
                self.assertTrue(c.kiem_con())

    def test_restart_giu_cong_doi_instance_node(self):
        c, so, cong_node = self._tao()
        c.khoi_dong()
        cu, listener = c.instance_id, c._nghe
        self._node(c, cong_node)
        self.assertTrue(c.thu_hoi(timeout=5))
        c.khoi_dong()
        self.assertNotEqual(c.instance_id, cu)
        self.assertIs(c._nghe, listener)
        self.assertEqual(c.the_he, 2)
        self._node(c, cong_node)
        self.assertTrue(c.thu_hoi(timeout=5))

    def test_version_va_contract_sai_khong_ready(self):
        for truong, gia_tri in (('_phien_ban', 'KHAC_RUNTIME'),
                                ('_contracts', ['hoa_don.tai_cong_thue@1'])):
            with self.subTest(truong=truong):
                c, so, _ = self._tao()
                setattr(c, truong, gia_tri)
                with self.assertRaisesRegex(tt.LoiTienTrinh, 'TIEN_TRINH_KHONG_HOP_LE'):
                    c.khoi_dong()
                self.assertNotIn('san_sang', [ten for ten, _ in so.go])

    def test_cong_adapter_bi_chiem_khong_do_cong_khong_dung_chu_la(self):
        with socket.socket() as la:
            la.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            la.bind(('127.0.0.1', 0))
            la.listen()
            cong = la.getsockname()[1]
            c, so, _ = self._tao(cong=cong)
            with self.assertRaisesRegex(tt.LoiTienTrinh, 'CONG_BI_CHIEM'):
                c.khoi_dong()
            self.assertEqual(so.dong['cong'], cong)
            self.assertNotIn('san_sang', [ten for ten, _ in so.go])
            with self._conn(cong):
                accepted, _ = la.accept()
                accepted.close()

    def test_cong_node_bi_chiem_khong_ready_khong_doi_cong(self):
        with socket.socket() as la:
            la.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            la.bind(('127.0.0.1', 0))
            la.listen()
            cong = la.getsockname()[1]
            # Kiểm mã bind tại chính launcher Node; vẫn thuộc Job Core test.
            c, so, cong_node = self._tao(cong_node=cong)
            with self.assertRaises(tt.LoiTienTrinh):
                c.khoi_dong()
            self.assertEqual(cong_node, cong)
            self.assertNotIn('san_sang', [ten for ten, _ in so.go])
            with self._conn(cong):
                accepted, _ = la.accept()
                accepted.close()


if __name__ == '__main__':
    if '--child' in sys.argv:
        _child()
    else:
        unittest.main()
