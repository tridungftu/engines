"""OCR-5b: nghiệm thu DEMO, không PostgreSQL/ABBYY/Word COM thật.

Khung chay/_VongNhan, SDKEngine, BanGiaoOCR, CongOCR, BanGiaoKetQua và
KhoTep chạy thật; chỉ driver metadata/quyền, ABBYY và bootstrap OS là giả.
Driver chỉ chứng minh việc truyền ngữ cảnh và chặn trước khi mở bytes;
không thay nghiệm thu SQL/ACL bằng login thật của G2-27/G2-33.
Backend của khung là seam DEMO, không công bố capability OCR production.
Tệp tạm được giữ lại, không cleanup bằng unlink/rmtree.

Hồi quy OCR-5c: ACK tạm/rollback không kết thúc bàn giao; SDK khác việc
bị chặn trước gửi bytes dù cùng hồ sơ và nguồn hợp lệ. BM-KENH đã nhận
stdin bi_mat riêng và từ chối bí mật trong tham_so; kiểm bằng test thường.
"""

from contextlib import contextmanager, redirect_stderr, redirect_stdout
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import base64
import hashlib
import io
import json
import logging
import os
from pathlib import Path
import socket
import sys
import tempfile
import threading
import traceback
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from kho_tri_thuc.core import ket_qua, tai_lieu, tep
from kho_tri_thuc.core.bi_mat import BiMat, gui_cho_con
from kho_tri_thuc.core.phien import MaBiMat
from kho_tri_thuc.core.viec import GiuViec
from kho_tri_thuc.engines.e_ocr import chay as ocr
from kho_tri_thuc.engines.e_ocr.abbyy import (
    BackendABBYY, CauHinhABBYY, DanhTinhWindows, LoiABBYY,
)
from kho_tri_thuc.engines.e_ocr.ban_giao import (
    BanGiaoOCR, CAN_DOI_CHIEU, CHO_CORE, DA_BAN_GIAO,
)
from kho_tri_thuc.ha_tang.cong_ocr import CongOCR
from kho_tri_thuc.ha_tang.primitives import DataError
from kho_tri_thuc.sdk_core import bootstrap as bs
from kho_tri_thuc.sdk_core.engine import KenhCore, LoiEngine, SDKEngine


PDF = b'%PDF-1.4\n/Type /Page\nDEMO OCR-5b 0001 31/10/2026\n%%EOF'
CANARY = b'DEMO_OCR5B_SECRET_KHONG_DUOC_LO_20261101'
OWNER = 'demo_chu_viec_ocr5b'
OTHER = 'demo_nguoi_khac_ocr5b'
LAP, XEM = 'DEMO:OCR:LAP', 'DEMO:OCR:XEM'


def _docx():
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as z:
        z.writestr(zipfile.ZipInfo('word/document.xml', (2026, 1, 1, 0, 0, 0)),
                   '<document><p>DEMO 0001: 1.234.567 đồng; 31/10/2026</p></document>')
    return out.getvalue()


DOCX = _docx()


def _lease(**doi):
    return GiuViec(**(dict(viec_id=uuid4(), buoc_viec_id=uuid4(), lan_thu_id=uuid4(),
        phap_nhan_id=uuid4(), module='demo', hanh_dong=LAP, instance_id=uuid4(),
        the_he=1, giu_den=datetime.now(timezone.utc) + timedelta(minutes=5),
        ma=MaBiMat('demo_lease_ocr5b_' + 'x' * 32)) | doi))


def _cong(root):
    return CongOCR(root / 'hot_folder_demo', tep_so_trang=root / 'so_demo.json',
                   thu_muc_dem=root / 'dem_demo', nghi=0.005,
                   cho_nhan=5, cho_toi_da=15, on_dinh=0.01)


class _ABBYYGia:
    """Watching giả: nhận bằng rename; chỉ xuất DOCX DEMO trong root tạm."""

    def __init__(self, cong):
        self.d = cong.thu_muc()
        self.nhan = cong.thu_muc_goc / 'da_nhan_demo'
        self.nhan.mkdir()
        self.da_nhan, self.cho_xuat, self.dung = (threading.Event() for _ in range(3))
        self.cho_xuat.set()
        self.raw, self.ma, self.loi = [], [], []
        self.thread = threading.Thread(target=self._chay, daemon=True)

    def _chay(self):
        try:
            while not self.dung.wait(0.005):
                for path in self.d['in'].iterdir():
                    self.raw.append(path.read_bytes())
                    self.ma.append(path.stem)
                    os.replace(path, self.nhan / path.name)
                    self.da_nhan.set()
                    if not self.cho_xuat.wait(15):
                        raise TimeoutError('ABBYY DEMO chưa được cho xuất')
                    (self.d['out'] / (path.stem + '.docx')).write_bytes(DOCX)
        except BaseException as exc:
            self.loi.append(exc)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *_):
        self.dung.set()
        self.cho_xuat.set()
        self.thread.join(5)
        if self.thread.is_alive() or self.loi:
            raise AssertionError('ABBYY giả lỗi hoặc không dừng')


class _MetadataDemo:
    """Driver RAM của test, không import/connect psycopg, không giả đã kiểm SQL.

    transaction lồng là savepoint; chỉ transaction gốc công bố cho conn đọc.
    Quyền giả đặt ở driver để kiểm KhoTep gọi lại cửa quyền trước mở bytes.
    """

    def __init__(self, lease, tid, events, nguon):
        self.lease, self.tid, self.events = lease, tid, events
        self.nguon = deepcopy(nguon)
        self.committed = {}
        self.quyen_chu = True

    def conn(self, *, doc=False):
        db = self

        class Conn:
            autocommit = doc
            info = SimpleNamespace(transaction_status=0)
            data = None
            depth = 0

            @contextmanager
            def transaction(self):
                outer = self.depth == 0
                if outer:
                    self.data = deepcopy(db.committed)
                saved = deepcopy(self.data)
                self.depth += 1
                self.info = SimpleNamespace(transaction_status=2)
                try:
                    yield self
                except BaseException:
                    self.data = saved
                    raise
                else:
                    if outer:
                        db.committed = deepcopy(self.data)
                        db.events.append('commit')
                finally:
                    self.depth -= 1
                    self.info = SimpleNamespace(transaction_status=2 if self.depth else 0)

            def execute(self, sql, params):
                if 'ghi_metadata' in sql:
                    if self.depth == 0:
                        raise AssertionError('Ghi ngoài transaction DEMO')
                    ma, module, pn, hd, kind, tid, raw, rid, job, generation = params
                    if (module, pn, tid, job, generation) != (
                            'demo', db.lease.phap_nhan_id, db.tid,
                            db.lease.viec_id, db.lease.the_he):
                        raise AssertionError('Ngữ cảnh ghi không thuộc việc')
                    data = json.loads(raw)
                    if kind == 'tep':
                        self.data.setdefault('tep_id', str(uuid4()))
                        self.data['meta'] = data
                        db.events.append('hash')
                        result = self.data['tep_id']
                    elif kind == 'bien_the':
                        self.data['bien_the'] = data
                        result = True
                    elif kind == 'ket_qua':
                        if data['nguon'] != db.nguon:
                            raise AssertionError('Nguồn DEMO không thuộc hồ sơ hoặc sai hash')
                        self.data.setdefault('ket_qua_id', str(uuid4()))
                        self.data['provenance'] = data
                        self.data['viec_id'] = str(job)
                        self.data['the_he'] = generation
                        db.events.append('provenance')
                        result = self.data['ket_qua_id']
                    else:
                        raise AssertionError('Thao tác ngoài fixture DEMO')
                elif 'doc_metadata' in sql:
                    ma, module, pn, hd, tid, bien_the, job, generation = params
                    if (ma != OWNER or not db.quyen_chu or module != 'demo'
                            or pn != db.lease.phap_nhan_id or tid != db.tid
                            or bien_the != 'ocr'):
                        raise RuntimeError('Quyền DEMO từ chối')
                    data = db.committed if doc else self.data
                    result = {'tep': [], 'ket_qua': []}
                    if data and 'provenance' in data:
                        ref = tep.KhoTep._tham_chieu(data['tep_id'], data['meta'])
                        result['tep'].append(dict(so_phien_ban=1, bien_the='ocr', tham_chieu=ref))
                        result['ket_qua'].append(dict(id=data['ket_qua_id'], tep_id=data['tep_id']))
                else:
                    raise AssertionError('SQL ngoài fixture DEMO')
                return SimpleNamespace(fetchone=lambda: (result,))

        return Conn()


class _CoreDemo(KenhCore):
    """Seam IPC của test, gọi cửa bàn giao/hash/provenance Core thật."""

    def __init__(self, root, *, lease=None, tai_lieu_id=None, tep_nguon_id=None):
        self.lease = lease or _lease()
        self.tid, self.input_id = tai_lieu_id or uuid4(), tep_nguon_id or uuid4()
        self.request_id, self.engine_id = uuid4(), uuid4()
        self.events, self.received = [], []
        self.db = _MetadataDemo(self.lease, self.tid, self.events, self.metadata()['nguon'])
        self.kho = tep.KhoTep(root / 'var' / 'core-demo' / 'ocr5b' / 'kho-file')
        self.ban_giao = ket_qua.BanGiaoKetQua(self.kho, xac_minh_core=self._xac_minh)
        self.truoc_commit, self.sau_commit = threading.Event(), threading.Event()
        self.cho_commit, self.cho_ack = threading.Event(), threading.Event()
        self.cho_commit.set()
        self.cho_ack.set()
        self.loi_ack = False
        self.provisional = None

    def ctx(self, **doi):
        return dict(ma=MaBiMat(OWNER), module='demo', phap_nhan_id=self.lease.phap_nhan_id,
                    hanh_dong=XEM) | doi

    def metadata(self):
        return dict(bien_the='ocr', ma_contract='van_ban_tai_lieu.v1',
            phien_ban_contract='1.0.0', trang_thai='thanh_cong', ly_do=None,
            revision_truoc=0,
            nguon=[dict(tep_id=str(self.input_id), sha256=hashlib.sha256(PDF).hexdigest())])

    def sdk(self, lease=None):
        return SDKEngine(self.lease if lease is None else lease, kenh_core=self)

    def _xac_minh(self, conn, lease):
        # Mô phỏng resolver instance/lease đã xác thực, không tin ID payload.
        if (lease != self.lease or lease.ma is not self.lease.ma
                or lease.giu_den <= datetime.now(timezone.utc)):
            raise LoiEngine('VIEC_MAT_LEASE')
        return ket_qua.NguonCore(module='demo', phap_nhan_id=lease.phap_nhan_id,
            phien_ban_module='1.2.3-demo', engine_id=self.engine_id,
            ham='ocr.trich_van_ban@1', phien_ban_ham=ocr.PHIEN_BAN,
            viec_id=lease.viec_id, the_he=lease.the_he,
            buoc_id=lease.buoc_viec_id, lan_thu_id=lease.lan_thu_id)

    def goi(self, operation, giu_viec, **payload):
        if operation == 'doc_dau_vao':
            return dict(van_ban_demo='DEMO_OCR5B', du_lieu_ket_qua=self.metadata(),
                        revision_tep_truoc=0)
        if operation != 'ghi_ket_qua':
            raise AssertionError('Operation ngoài OCR-5b')
        self.received.append(payload['luong'])
        conn = self.db.conn()
        with conn.transaction():
            self.provisional = self.ban_giao.ghi(conn, giu_viec=giu_viec,
                tai_lieu_id=self.tid, request_id=self.request_id, het_han_luc=None,
                **payload, **self.ctx(hanh_dong=LAP))
            self.truoc_commit.set()
            if not self.cho_commit.wait(15):
                raise TimeoutError('Core DEMO chờ commit')
        self.sau_commit.set()
        if not self.cho_ack.wait(15):
            raise TimeoutError('Core DEMO chờ ACK')
        if self.loi_ack:
            raise RuntimeError(CANARY.decode())
        ack = self.ban_giao.xac_nhan_da_commit(self.db.conn(doc=True),
            tai_lieu_id=self.tid, ket_qua_id=self.provisional['ket_qua_id'],
            bien_the='ocr', **self.ctx())
        self.events.append('ack')
        return ack

    def doc(self, **doi):
        data = self.db.committed
        return self.kho.mo_doc(self.db.conn(doc=True), tai_lieu_id=self.tid,
            tep_id=data['tep_id'], bien_the='ocr', **self.ctx(**doi))


class _ProtocolDemo(io.BytesIO):
    def __init__(self):
        super().__init__()
        self.messages = []
        self.signals = {k: threading.Event() for k in (
            'san_sang', 'drain_chua_xong', 'da_thu_hoi')}

    def write(self, raw):
        message = bs.doc_thong_diep(raw)
        self.messages.append(message)
        self.signals[message['kieu']].set()
        return super().write(raw)


class _RuntimeDemo:
    """Entrypoint thật trong thread, listener loopback và pipe điều khiển thật.

    Bootstrap OS được tiêm; không giả đây là process/tài khoản Windows riêng.
    Seam backend.xu_ly chỉ nối dữ liệu DEMO với BanGiaoOCR, không vá khung.
    """

    def __init__(self, core, adapter):
        self.core, self.adapter = core, adapter
        self.loi, self.nhan = [], []
        self.revoked = False
        self.listener = socket.socket()
        self.listener.bind(('127.0.0.1', 0))
        self.listener.listen()
        self.address = self.listener.getsockname()
        rd, wr = os.pipe()
        self.reader, self.writer = os.fdopen(rd, 'rb'), os.fdopen(wr, 'wb', buffering=0)
        self.output = _ProtocolDemo()
        self.bootstrap = bs.Bootstrap()
        b = self.bootstrap
        b.socket, b.bo_doc = self.listener, object()
        b._vao, b._ra, b._duoc_accept = self.reader, self.output, False
        b._cfg = dict(module='demo', instance_id=str(core.lease.instance_id), pid=os.getpid(),
            dinh_danh_lan_tao='DEMO', nonce_khoi_dong='d' * 43,
            cong=self.address[1], the_he=core.lease.the_he, tham_so={})

        def xu_ly(marker):
            if marker != 'DEMO_OCR5B':
                raise AssertionError('Chỉ dữ liệu DEMO')
            return adapter.ocr(PDF, 'pdf')

        self.backend = SimpleNamespace(san_sang=lambda: True, xu_ly=xu_ly)
        self.thread = threading.Thread(target=self._chay, daemon=True)

    def _chay(self):
        def nhan_viec(conn, bo_doc):
            if conn.recv(1) != b'D':
                raise AssertionError('Marker DEMO không đúng')
            self.nhan.append(True)
            return self.core.sdk()

        try:
            ocr.chay(kiem_chu_ky=lambda *_: None, nhan_viec=nhan_viec, backend=self.backend)
        except BaseException as exc:
            self.loi.append(exc)
        finally:
            self.core.events.append('dung')

    def __enter__(self):
        self.patch = patch.object(ocr.Bootstrap, 'nhan', return_value=self.bootstrap)
        self.patch.start()
        bs.gui_thong_diep(self.writer, dict(protocol=bs.PROTOCOL, kieu='nhan_accept'))
        self.thread.start()
        if not self.output.signals['san_sang'].wait(5):
            self.__exit__(None, None, None)
            raise AssertionError('Khung không ready')
        self.conn = socket.create_connection(self.address, timeout=5)
        self.conn.sendall(b'D')
        return self

    def thu_hoi(self):
        if not self.revoked:
            bs.gui_thong_diep(self.writer, dict(protocol=bs.PROTOCOL, kieu='thu_hoi'))
            self.revoked = True

    def __exit__(self, *_):
        self.core.cho_commit.set()
        self.core.cho_ack.set()
        self.thu_hoi()
        self.thread.join(10)
        if hasattr(self, 'conn'):
            self.conn.close()
        self.writer.close()
        self.reader.close()
        self.listener.close()
        self.patch.stop()
        if self.thread.is_alive() or self.loi:
            raise AssertionError('Khung DEMO lỗi hoặc không drain')


class OCR5bTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix='g3_ocr_5b_demo_'))
        self.enterContext(patch.dict(os.environ, {'CODEX_NO_DELETE_FILES': '1'}))
        # Không tạo timer dọn muộn của cổng gốc.
        self.enterContext(patch.object(CongOCR, '_don_sau'))
        self.cong = _cong(self.root)
        self.core = _CoreDemo(self.root)
        self.adapter = self._adapter()

    def _adapter(self):
        return BanGiaoOCR(self.cong, viec_id=self.core.lease.viec_id,
                         thu_muc_ban_giao=self.root / 'ban_giao_demo')

    def _ocr(self):
        with _ABBYYGia(self.cong) as abbyy:
            raw = self.adapter.ocr(PDF, 'pdf')
        self.assertEqual(abbyy.raw, [PDF])
        self.assertEqual(raw, DOCX)
        return raw

    def _gui(self, *, sdk=None):
        return self.adapter.ban_giao(sdk=self.core.sdk() if sdk is None else sdk,
            du_lieu=self.core.metadata(), revision_tep_truoc=0)

    def _so_trang(self):
        return json.loads(self.cong.tep_so_trang.read_text(encoding='utf-8'))

    def _kiem_core(self):
        data = self.core.db.committed
        self.assertEqual(data['meta']['sha256'], hashlib.sha256(DOCX).hexdigest())
        self.assertEqual(data['meta']['kich_thuoc'], len(DOCX))
        p = data['provenance']
        self.assertEqual(p['tep_id'], data['tep_id'])
        self.assertEqual(p['engine_id'], str(self.core.engine_id))
        self.assertEqual(p['phien_ban_module'], '1.2.3-demo')
        self.assertEqual((p['ham'], p['phien_ban_ham']), ('ocr.trich_van_ban@1', ocr.PHIEN_BAN))
        self.assertEqual(p['buoc_id'], str(self.core.lease.buoc_viec_id))
        self.assertEqual(p['lan_thu_id'], str(self.core.lease.lan_thu_id))
        self.assertEqual((data['viec_id'], data['the_he']),
                         (str(self.core.lease.viec_id), self.core.lease.the_he))
        self.assertEqual(p['nguon'], self.core.metadata()['nguon'])
        self.assertNotIn('trang_thai_duyet', p)
        with self.core.doc() as stream:
            self.assertEqual(stream.read(), DOCX)

    def _drain(self, stage):
        if stage == 'commit':
            self.core.cho_commit.clear()
        elif stage == 'ack':
            self.core.cho_ack.clear()
        with _ABBYYGia(self.cong) as abbyy:
            if stage == 'abbyy':
                abbyy.cho_xuat.clear()
            # Runtime đóng trước backend, cả khi assertion lỗi.
            try:
                with _RuntimeDemo(self.core, self.adapter) as runtime:
                    signal = (abbyy.da_nhan if stage == 'abbyy' else
                              self.core.truoc_commit if stage == 'commit' else self.core.sau_commit)
                    self.assertTrue(signal.wait(8))
                    runtime.thu_hoi()
                    self.assertTrue(runtime.output.signals['drain_chua_xong'].wait(5))
                    self.assertTrue(runtime.thread.is_alive())
                    self.assertNotIn('ack', self.core.events)
                    self.assertNotIn('dung', self.core.events)
                    if stage == 'abbyy':
                        journal = json.loads((self.adapter.thu_muc / 'trang_thai.json').read_bytes())
                        self.assertEqual(journal['trang_thai'], CAN_DOI_CHIEU)
                    else:
                        self.assertEqual(self.adapter.trang_thai(), CHO_CORE)
                        self.assertEqual((self.adapter.thu_muc / 'ket_qua.docx').read_bytes(), DOCX)
                    if stage != 'ack':
                        self.assertEqual(self.core.db.committed, {})
                    else:
                        self._kiem_core()
                    # Kết nối sau drain chỉ nằm trong backlog, không nhận việc thứ hai.
                    with socket.create_connection(runtime.address, timeout=2) as moi:
                        moi.sendall(b'D')
                        moi.settimeout(0.1)
                        with self.assertRaises(socket.timeout):
                            moi.recv(1)
                    abbyy.cho_xuat.set()
                    self.core.cho_commit.set()
                    self.core.cho_ack.set()
                    self.assertTrue(runtime.output.signals['da_thu_hoi'].wait(8))
                    runtime.thread.join(5)
                    self.assertFalse(runtime.thread.is_alive())
                    self.assertEqual(runtime.nhan, [True])
                    self.assertEqual(runtime.output.messages[0]['contracts'], [])
            finally:
                abbyy.cho_xuat.set()
        self.assertEqual(abbyy.raw, [PDF])
        self.assertEqual(len(self.core.received), 1)
        self.assertTrue(self.core.received[0].closed)
        self.assertEqual(sum(x[1] for x in self._so_trang()), 1)
        self.assertEqual(self.core.events, ['hash', 'provenance', 'commit', 'ack', 'dung'])
        self._kiem_core()

    def test_drain_khi_abbyy_dang_xu_ly_khong_mat_khong_gui_lai(self):
        self._drain('abbyy')

    def test_core_hash_provenance_commit_truoc_dung(self):
        self._drain('commit')

    def test_drain_cho_ack_sau_commit_giu_nguyen_ket_qua(self):
        self._drain('ack')

    def test_ban_giao_sdk_core_that_chi_ack_sau_commit_va_replay_khong_gui_lai(self):
        self._ocr()
        self.assertEqual(self.adapter.trang_thai(), CHO_CORE)
        ack = self._gui()
        self.assertIs(ack['da_ban_giao'], True)
        self.assertEqual(self.adapter.trang_thai(), DA_BAN_GIAO)
        self._kiem_core()
        with patch.object(self.cong, 'ocr', side_effect=AssertionError('OCR lại')):
            adapter = self._adapter()
            self.assertEqual(adapter.ocr(PDF, 'pdf'), DOCX)
            self.assertIs(adapter.ban_giao(sdk=self.core.sdk(), du_lieu=self.core.metadata(),
                                         revision_tep_truoc=0), False)
        self.assertEqual(len(self.core.received), 1)
        self.assertEqual(sum(x[1] for x in self._so_trang()), 1)

    def test_mat_ack_sau_commit_khong_tu_gui_lai_hoan_trang_hoac_mat_docx(self):
        self._ocr()
        self.core.loi_ack = True
        so = self._so_trang()
        with self.assertRaises(LoiEngine) as bat:
            self._gui()
        self.assertNotIn(CANARY.decode(), ''.join(traceback.format_exception(bat.exception)))
        self.assertEqual(self.adapter.trang_thai(), CHO_CORE)
        self.assertEqual(len(self.core.received), 1)
        self.assertEqual(self._so_trang(), so)
        self.assertEqual((self.adapter.thu_muc / 'ket_qua.docx').read_bytes(), DOCX)
        self._kiem_core()
        # Core đối chiếu kết quả đã commit; không cần gửi bytes/OCR lại để tìm ACK.
        ack = self.core.ban_giao.xac_nhan_da_commit(self.core.db.conn(doc=True),
            tai_lieu_id=self.core.tid, ket_qua_id=self.core.provisional['ket_qua_id'],
            bien_the='ocr', **self.core.ctx())
        self.assertIs(ack['da_ban_giao'], True)
        self.assertEqual(len(self.core.received), 1)

    def test_lease_sai_instance_the_he_phap_nhan_chan_truoc_ghi_bytes(self):
        self._ocr()
        for doi in (dict(instance_id=uuid4()), dict(the_he=2), dict(phap_nhan_id=uuid4()),
                    dict(viec_id=uuid4()), dict(buoc_viec_id=uuid4()),
                    dict(lan_thu_id=uuid4()), dict(ma=MaBiMat('demo_gia_ma'))):
            with self.subTest(truong=next(iter(doi))):
                with patch.object(self.core.kho, 'tai_len') as ghi:
                    with self.assertRaisesRegex(LoiEngine, 'VIEC_MAT_LEASE'):
                        self._gui(sdk=self.core.sdk(replace(self.core.lease, **doi)))
                ghi.assert_not_called()
        self.assertEqual(self.core.db.committed, {})
        self.assertEqual(self.adapter.trang_thai(), CHO_CORE)

    def test_chu_viec_tai_duoc_nguoi_khac_phap_nhan_module_khac_bi_chan_truoc_bytes(self):
        self._ocr()
        self._gui()
        with self.core.doc() as stream:
            self.assertEqual(stream.read(), DOCX)
        for doi in (dict(ma=MaBiMat(OTHER)), dict(phap_nhan_id=uuid4()),
                    dict(module='khac', hanh_dong='KHAC:OCR:XEM')):
            with self.subTest(truong=next(iter(doi))):
                with patch.object(self.core.kho, '_doc_kiem') as mo:
                    with self.assertRaises(tai_lieu.LoiTaiLieu):
                        self.core.doc(**doi)
                mo.assert_not_called()
        # Thu hồi quyền sau một lần tải thành công phải được kiểm lại.
        self.core.db.quyen_chu = False
        with patch.object(self.core.kho, '_doc_kiem') as mo:
            with self.assertRaises(tai_lieu.LoiTaiLieu):
                self.core.doc()
        mo.assert_not_called()

    def test_ket_qua_bi_doi_hash_core_khong_ack_hoac_cho_tai(self):
        self._ocr()
        self._gui()
        meta = self.core.db.committed['meta']
        (self.core.kho.root / meta['khoa_luu_tru']).write_bytes(b'DEMO bi hong')
        with self.assertRaisesRegex(tep.LoiTep, 'TEP_HASH'):
            self.core.doc()
        with self.assertRaisesRegex(tep.LoiTep, 'TEP_HASH'):
            self.core.ban_giao.xac_nhan_da_commit(self.core.db.conn(doc=True),
                tai_lieu_id=self.core.tid, ket_qua_id=self.core.provisional['ket_qua_id'],
                bien_the='ocr', **self.core.ctx())

    def test_ack_chua_commit_va_rollback_khong_danh_dau_da_ban_giao(self):
        """ACK tạm từ Core thật bị từ chối cả trước và sau rollback."""
        self._ocr()
        so = self._so_trang()
        pending = None

        class RollbackDemo(Exception):
            pass

        with self.assertRaises(RollbackDemo):
            with self.core.db.conn().transaction() as conn:
                def chua_commit(operation, lease, **payload):
                    nonlocal pending
                    # Transaction gốc vẫn mở khi trả ACK tạm cho engine.
                    pending = self.core.ban_giao.ghi(conn, giu_viec=lease,
                        tai_lieu_id=self.core.tid, request_id=self.core.request_id,
                        het_han_luc=None, **payload, **self.core.ctx(hanh_dong=LAP))
                    self.assertIs(pending['da_ban_giao'], False)
                    return pending

                with patch.object(self.core, 'goi', side_effect=chua_commit):
                    with self.assertRaises(DataError) as bat:
                        self._gui()
                self.assertEqual(bat.exception.code, 'OCR_CHUA_XAC_NHAN')
                self.assertEqual(self.core.db.committed, {})
                self.assertEqual(self.adapter.trang_thai(), CHO_CORE)
                raise RollbackDemo()

        self.assertEqual(self.core.db.committed, {})
        with self.assertRaisesRegex(tep.LoiTep, 'TEP_KHONG_THAY'):
            self.core.ban_giao.xac_nhan_da_commit(self.core.db.conn(doc=True),
                tai_lieu_id=self.core.tid, ket_qua_id=pending['ket_qua_id'],
                bien_the='ocr', **self.core.ctx())
        with patch.object(self.core, 'goi', return_value=pending):
            with self.assertRaises(DataError) as bat:
                self._gui()
        self.assertEqual(bat.exception.code, 'OCR_CHUA_XAC_NHAN')
        self.assertEqual(self.adapter.trang_thai(), CHO_CORE)
        self.assertEqual((self.adapter.thu_muc / 'ket_qua.docx').read_bytes(), DOCX)
        self.assertEqual(self._so_trang(), so)

    def test_ack_thieu_xac_nhan_hoac_bien_nhan_giu_trang_thai_cho(self):
        self._ocr()
        so = self._so_trang()
        for ack in (None, False, True, {}, {'ket_qua_id': str(uuid4())},
                    {'da_ban_giao': False, 'ket_qua_id': str(uuid4())},
                    {'da_ban_giao': 1, 'ket_qua_id': str(uuid4())},
                    {'da_ban_giao': True}, {'da_ban_giao': True, 'ket_qua_id': None},
                    {'da_ban_giao': True, 'ket_qua_id': ''},
                    {'da_ban_giao': True, 'ket_qua_id': '   '}):
            with self.subTest(ack=ack), patch.object(self.core, 'goi', return_value=ack):
                with self.assertRaises(DataError) as bat:
                    self._gui()
                self.assertEqual(bat.exception.code, 'OCR_CHUA_XAC_NHAN')
                self.assertEqual(self.adapter.trang_thai(), CHO_CORE)
                self.assertEqual(self.core.db.committed, {})
                self.assertEqual((self.adapter.thu_muc / 'ket_qua.docx').read_bytes(), DOCX)
                self.assertEqual(self._so_trang(), so)

    def test_khong_ban_giao_ket_qua_viec_a_bang_sdk_viec_b(self):
        """SDK B hợp lệ cùng hồ sơ/nguồn A vẫn bị chặn trước đọc/gửi DOCX."""
        self._ocr()
        so = self._so_trang()
        khac = _CoreDemo(self.root / 'core_khac', lease=_lease(
            phap_nhan_id=self.core.lease.phap_nhan_id),
            tai_lieu_id=self.core.tid, tep_nguon_id=self.core.input_id)
        self.assertNotEqual(khac.lease.viec_id, self.core.lease.viec_id)
        self.assertEqual(khac.metadata()['nguon'], self.core.metadata()['nguon'])
        self.assertEqual(khac.db.tid, self.core.tid)
        with patch.object(khac, 'goi', wraps=khac.goi) as gui, \
                patch.object(khac.kho, 'tai_len', wraps=khac.kho.tai_len) as ghi, \
                patch.object(self.adapter, '_ket_qua', side_effect=AssertionError('Đọc DOCX')):
            with self.assertRaisesRegex(LoiEngine, 'VIEC_MAT_LEASE'):
                self._gui(sdk=khac.sdk())
        gui.assert_not_called()
        ghi.assert_not_called()
        self.assertEqual(khac.received, [])
        self.assertEqual(khac.db.committed, {})
        self.assertEqual(self.core.db.committed, {})
        self.assertEqual(self.adapter.trang_thai(), CHO_CORE)
        self.assertEqual((self.adapter.thu_muc / 'ket_qua.docx').read_bytes(), DOCX)
        self.assertEqual(self._so_trang(), so)


class BiMatOCR5bTests(unittest.TestCase):
    def _khong_lo(self, *values):
        captured = '\n'.join(str(v) for v in values)
        for secret in (CANARY.decode(), base64.b64encode(CANARY).decode()):
            self.assertNotIn(secret, captured)

    def _wire(self):
        # Kênh duy nhất dùng chính gui_cho_con qua pipe; không két/cấu hình nguồn.
        rd, wr = os.pipe()
        with os.fdopen(rd, 'rb') as reader, os.fdopen(wr, 'wb') as writer:
            proc = SimpleNamespace(stdin=writer)
            gui_cho_con(proc, BiMat(CANARY))
            return reader.readline(bs.TOI_DA)

    def _bootstrap(self, *, tham_so=None, secret=True):
        cfg = dict(protocol=bs.PROTOCOL, kieu='khoi_dong', pid=os.getpid(),
            dinh_danh_lan_tao='DEMO_CREATE', cong=19125, dia_chi_nghe='127.0.0.1',
            phien_ban=ocr.PHIEN_BAN, the_he=1, tham_so={} if tham_so is None else tham_so,
            issuer='core-demo', module='demo', instance_id=str(uuid4()),
            nonce_khoi_dong='n' * 43, socket=base64.b64encode(b'DEMO_SHARE').decode())
        wire = io.BytesIO()
        bs.gui_thong_diep(wire, cfg)
        if secret:
            wire.write(self._wire())
        bs.gui_thong_diep(wire, dict(protocol=bs.PROTOCOL, kieu='nhan_accept'))
        bs.gui_thong_diep(wire, dict(protocol=bs.PROTOCOL, kieu='thu_hoi'))
        wire.seek(0)
        listener = Mock()
        listener.getsockname.return_value = ('127.0.0.1', 19125)
        out = io.BytesIO()
        with patch.object(bs, 'dinh_danh_lan_tao', return_value='DEMO_CREATE'), \
                patch.object(bs.socket, 'fromshare', return_value=listener, create=True):
            bootstrap = bs.Bootstrap.nhan(kiem_chu_ky=lambda *_: None, stdin=wire, stdout=out)
        return bootstrap, wire, out

    def test_core_gui_bi_mat_chi_stdin_khong_env_args_log(self):
        out, err, log = io.StringIO(), io.StringIO(), io.StringIO()
        handler = logging.StreamHandler(log)
        logger = logging.getLogger()
        logger.addHandler(handler)
        env = dict(os.environ)
        try:
            with redirect_stdout(out), redirect_stderr(err), \
                    patch.object(Path, 'open', side_effect=AssertionError('Cấm cấu hình/đĩa')), \
                    patch('subprocess.Popen', side_effect=AssertionError('Cấm launcher thật')):
                wire = self._wire()
        finally:
            logger.removeHandler(handler)
        message = bs.doc_thong_diep(wire)
        self.assertEqual(set(message), {'protocol', 'kieu', 'du_lieu'})
        self.assertEqual((message['protocol'], message['kieu']), (bs.PROTOCOL, 'bi_mat'))
        self.assertEqual(base64.b64decode(message['du_lieu']), CANARY)
        self.assertEqual(dict(os.environ), env)
        self._khong_lo(out.getvalue(), err.getvalue(), log.getvalue(), repr(BiMat(CANARY)))

    def test_bm_kenh_stdin_bi_mat_khong_lam_lech_nhan_accept_va_drain(self):
        """BM-KENH nhận bí mật riêng, giữ đúng thứ tự accept và drain."""
        bootstrap, wire, out = self._bootstrap()
        try:
            bootstrap.bao_san_sang(phien_ban=ocr.PHIEN_BAN, contracts=[], kiem_san_sang=lambda: True)
            bootstrap.cho_thu_hoi(ngung_accept=lambda: None, drain=lambda: True)
            self.assertEqual(wire.read(), b'')
            self._khong_lo(out.getvalue(), repr(bootstrap))
            self.assertEqual([bs.doc_thong_diep(line)['kieu']
                              for line in out.getvalue().splitlines(keepends=True)],
                             ['san_sang', 'da_thu_hoi'])
        finally:
            bootstrap.socket.close()

    def test_bm_kenh_cam_bi_mat_trong_tham_so_khoi_dong(self):
        """BM-KENH từ chối bí mật qua kênh tham_so cũ."""
        with self.assertRaises(bs.LoiBootstrap):
            bootstrap, _, _ = self._bootstrap(tham_so={'bi_mat': CANARY.decode()}, secret=False)
            bootstrap.socket.close()

    def test_abbyy_loi_canary_khong_lo_exception_log_ket_qua(self):
        sid = lambda rid: f'S-1-5-21-111-222-333-{rid}'
        cfg = CauHinhABBYY(sid(1004), sid(1000), sid(1001), (sid(1002),), 4, 1)
        identity = DanhTinhWindows(cfg.sid_ocr, 4, True, True)
        cong = Mock(spec=CongOCR)
        phase = Mock(return_value=(identity, identity))
        acl = Mock(return_value=True)
        backend = BackendABBYY(cau_hinh=cfg, cong_ocr=cong, kiem_phien=phase, kiem_acl=acl)
        log, out, err = io.StringIO(), io.StringIO(), io.StringIO()
        handler = logging.StreamHandler(log)
        logger = logging.getLogger()
        logger.addHandler(handler)
        try:
            for seam in (phase, acl, cong.ocr):
                exc = RuntimeError(CANARY.decode())
                seam.side_effect = exc
                try:
                    with redirect_stdout(out), redirect_stderr(err):
                        try:
                            backend.ocr(PDF, 'pdf')
                        except LoiABBYY as loi:
                            self.assertIsNone(loi.__context__)
                            self.assertIsNone(loi.__cause__)
                            self._khong_lo(''.join(traceback.format_exception(loi)), repr(exc))
                        else:
                            self.fail('Lỗi ABBYY giả phải bị chặn')
                finally:
                    seam.side_effect = None
            self._khong_lo(out.getvalue(), err.getvalue(), log.getvalue(), repr(backend), DOCX)
        finally:
            logger.removeHandler(handler)

    def test_canary_stdin_hong_khong_phan_chieu_vao_loi(self):
        rd, wr = os.pipe()
        with os.fdopen(rd, 'rb'), os.fdopen(wr, 'wb') as writer:
            with patch('kho_tri_thuc.core.bi_mat.gui_thong_diep',
                       side_effect=RuntimeError(CANARY.decode())):
                try:
                    gui_cho_con(SimpleNamespace(stdin=writer), BiMat(CANARY))
                except Exception as exc:
                    self._khong_lo(''.join(traceback.format_exception(exc)), repr(exc))
                    self.assertIsNone(exc.__context__)
                else:
                    self.fail('Pipe lỗi phải báo thất bại')


class CachLyThatOCR5bTests(unittest.TestCase):
    @unittest.skip('CHUA_KIEM G2-33: cần tài khoản/SID hạn chế và phiên Windows riêng có màn hình; '
                   'lát này cấm tạo tài khoản, không dùng SID giả làm bằng chứng cách ly thật')
    def test_tai_khoan_va_phien_abbyy_rieng(self):
        pass

    @unittest.skip('CHUA_KIEM G2-33: cần ca âm từ process engine dưới tài khoản riêng, ACL/DPAPI/'
                   'Core process memory/token/handle và Windows Job; chỉ dùng bí mật DEMO')
    def test_engine_khong_doc_ket_core_hoac_thoat_job(self):
        pass

    @unittest.skip('CHUA_KIEM G2-27: quyền tải bằng login/MTQ PostgreSQL thật chưa được nghiệm thu; '
                   'handoff OCR-5b cấm kết nối PostgreSQL, driver RAM chỉ kiểm ranh giới gọi quyền')
    def test_quyen_tai_sql_bang_login_that(self):
        pass


if __name__ == '__main__':
    unittest.main()
