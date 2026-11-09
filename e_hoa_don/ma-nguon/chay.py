"""HD-3a: Bootstrap/SDK Core + Node DEMO trong cây Windows Job.

CD-036: dùng lại Bootstrap/SDK, doc.doc_xml (HD-1), env_con/_doc_dong;
bọc vòng nhận/drain theo e_ocr.chay; viết mới Node stub cố định dưới đây.
Không nạp server.js/job.js nguồn, không portal/Chromium hoặc tải thật.
Node stub chỉ kiểm bind/Job/readiness, KHÔNG chứng minh protocol nguồn H.
Listener adapter dùng fromshare; cổng Node DEMO riêng do Core cấp trong
tham_so.cong_node_demo, có khoảng hở bind --port và tuyệt đối không dò.
"""

from __future__ import annotations

from contextlib import contextmanager
import ctypes
import io
import json
import os
import socket
import subprocess
import threading
import time

from ...nguon.trich6_host import env_con
from ...sdk_core.bootstrap import Bootstrap, LoiBootstrap, PROTOCOL, gui_thong_diep
from ...sdk_core.engine import LoiEngine, SDKEngine
from ...sdk_core.ngu_canh import _xoa_loi
from ...sdk_core.tien_trinh_phu import _doc_dong
from .doc import doc_xml


PHIEN_BAN = '0.1.0-demo.1'
CONTRACTS = ['hoa_don.v1']

# Mã stub mới, không sao chép/giả định owned protocol của bộ tải nguồn.
_NODE_DEMO = r"""
const net = require('node:net');
const readline = require('node:readline');
const args = process.argv.slice(1);
if (args.length !== 2 || args[0] !== '--port') process.exit(2);
const port = Number(args[1]);
if (!Number.isInteger(port) || port < 1024 || port > 65535) process.exit(2);
const input = readline.createInterface({input: process.stdin});
let server;
input.once('line', line => {
  let cfg;
  try { cfg = JSON.parse(line); } catch { process.exit(2); }
  if (typeof cfg.instance !== 'string' || !cfg.instance) process.exit(2);
  server = net.createServer(conn => conn.end(JSON.stringify({
    demo: true, instance: cfg.instance, pid: process.pid, port
  }) + '\n'));
  server.on('error', err => {
    console.log(JSON.stringify({ma: err.code === 'EADDRINUSE' ?
      'CONG_BI_CHIEM' : 'NODE_BIND_LOI'}));
    process.exit(3);
  });
  server.listen({host: '127.0.0.1', port, exclusive: true}, () => {
    console.log(JSON.stringify({demo: true, instance: cfg.instance,
      pid: process.pid, port}));
  });
});
input.on('close', () => { if (server) server.close(); });
"""


def _trong_job(proc=None):
    if os.name != 'nt':
        return False
    from ctypes import wintypes as w
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.GetCurrentProcess.restype = w.HANDLE
    k.IsProcessInJob.argtypes = [w.HANDLE, w.HANDLE, ctypes.POINTER(w.BOOL)]
    k.IsProcessInJob.restype = w.BOOL
    h = k.GetCurrentProcess() if proc is None else w.HANDLE(int(proc._handle))
    trong = w.BOOL()
    return bool(k.IsProcessInJob(h, None, ctypes.byref(trong)) and trong.value)


class NodeGia:
    """Chỉ launcher DEMO; không credentials, không breakaway khỏi Job Core."""

    def __init__(self, *, node_executable, cong, instance):
        if (not isinstance(node_executable, str) or not os.path.isabs(node_executable)
                or type(cong) is not int or not 1024 <= cong <= 65535
                or not isinstance(instance, str) or not instance):
            raise ValueError('Cần Node executable và cổng/instance DEMO do Core cấp')
        self.node_executable, self.cong, self.instance = node_executable, cong, instance
        self.proc = None

    def bat_dau(self):
        if self.proc is not None or not _trong_job():
            raise LoiBootstrap('NODE_CAN_JOB_CORE')
        self.proc = subprocess.Popen(
            [self.node_executable, '-e', _NODE_DEMO, '--', '--port', str(self.cong)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            env=env_con(), close_fds=True, shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            gui_thong_diep(self.proc.stdin, {'instance': self.instance})
            raw = _doc_dong(self.proc.stdout, 5)
            try:
                ready = json.loads(raw) if raw else None
            except (ValueError, TypeError):
                ready = None
            if ready == {'ma': 'CONG_BI_CHIEM'}:
                raise LoiBootstrap('CONG_BI_CHIEM')
            if (ready != {'demo': True, 'instance': self.instance,
                          'pid': self.proc.pid, 'port': self.cong}
                    or not self.san_sang()):
                raise LoiBootstrap('NODE_CHUA_SAN_SANG')
        except BaseException:
            self.dong()
            raise

    def san_sang(self):
        return (self.proc is not None and self.proc.poll() is None
                and _trong_job(self.proc))

    def dong(self):
        if self.proc is None:
            return
        proc = self.proc
        try:
            proc.stdin.close()
            try:
                proc.wait(5)
            except subprocess.TimeoutExpired:
                # Chỉ Popen stub sở hữu; chỉ gọi sau drain hoặc lỗi preflight.
                proc.terminate()
                proc.wait(5)
        finally:
            proc.stdout.close()
        self.proc = None


@contextmanager
def _giu_lease(sdk):
    """Gia hạn cùng SDK cả khi đọc/parse hoặc ghi_ket_qua đang chờ ACK."""
    dung = threading.Event()

    def heartbeat():
        cho = 30  # SDK gia hạn 120 giây; còn thời gian retry lỗi tạm thời.
        while not dung.wait(cho):
            try:
                sdk.heartbeat()
                cho = 30
            except LoiEngine as exc:
                _xoa_loi(exc)
                cho = 1

    worker = threading.Thread(target=heartbeat, name='hoa-don-heartbeat')
    worker.start()
    try:
        yield
    finally:
        dung.set()
        worker.join()


def xu_ly_viec(sdk):
    """Đọc XML qua Core, bọc HD-1, giữ cùng bộ đệm tới ACK.

    nhan_viec/SDK là seam Core như OCR-4a, không đặt wire protocol mới.
    Core đã lưu XML và JSON chi tiết nguồn HD-1, cấp ID riêng/context và
    metadata đã kiểm quyền; engine không tự tạo ID, provenance hoặc lease.
    """
    if not isinstance(sdk, SDKEngine):
        raise TypeError('Cần SDKEngine do Core cấp')
    with _giu_lease(sdk):
        return _xu_ly_viec(sdk)


def _xu_ly_viec(sdk):
    dau_vao = sdk.doc_dau_vao()
    with sdk.mo_doc(dau_vao['tep_xml_id']) as nguon:
        raw = nguon.read(16 * 1024 * 1024 + 1)
    if len(raw) > 16 * 1024 * 1024:
        raise ValueError('XML vượt giới hạn 16 MiB')
    kq = doc_xml(raw, dau_vao['context'], tep_xml_id=dau_vao['tep_xml_id'],
                 chi_tiet_nguon_tep_id=dau_vao['chi_tiet_nguon_tep_id'],
                 revision=dau_vao.get('revision', 1))
    raw = json.dumps(kq.hoa_don, ensure_ascii=False, allow_nan=False).encode('utf-8')
    with io.BytesIO(raw) as luong:
        while True:
            luong.seek(0)
            try:
                return sdk.ghi_ket_qua(luong=luong, ten='hoa-don.json',
                    du_lieu=dau_vao['du_lieu_ket_qua'],
                    revision_tep_truoc=dau_vao['revision_tep_truoc'])
            except LoiEngine as exc:
                _xoa_loi(exc)
                time.sleep(0.1)


class _VongNhan:
    """Một worker như OCR-4a; lỗi/chưa ACK giữ instance để Core xử lý."""

    def __init__(self, bootstrap, nhan_viec):
        self.bootstrap, self.nhan_viec = bootstrap, nhan_viec
        self.khoa = threading.Lock()
        self.dung = self.loi = False
        self.worker = threading.Thread(target=self._chay, name='hoa-don-demo')

    def bat_dau(self):
        self.bootstrap.socket.settimeout(0.1)
        self.worker.start()

    def _chay(self):
        try:
            while True:
                with self.khoa:
                    if self.dung:
                        return
                try:
                    conn, _ = self.bootstrap.accept()
                except socket.timeout:
                    continue
                except LoiBootstrap as exc:
                    if exc.ma == 'CHUA_CO_QUYEN_ACCEPT':
                        return
                    raise
                with conn:
                    with self.khoa:
                        if self.dung:
                            return
                    conn.settimeout(None)
                    sdk = self.nhan_viec(conn, self.bootstrap.bo_doc)
                    xu_ly_viec(sdk)
        except Exception as exc:
            _xoa_loi(exc)
            self.loi = True

    def ngung_accept(self):
        with self.khoa:
            self.dung = True

    def drain(self):
        self.worker.join(0.1)
        return not self.worker.is_alive() and not self.loi


def chay(*, kiem_chu_ky, nhan_viec, node_executable=None):
    """Core gọi; Node tùy chọn chỉ trong hồ sơ thử HD-3a, không tải thật."""
    if not callable(kiem_chu_ky) or not callable(nhan_viec):
        raise TypeError('Cần bộ kiểm chữ ký và seam nhận việc của Core')
    bootstrap = Bootstrap.nhan(kiem_chu_ky=kiem_chu_ky)
    vong = _VongNhan(bootstrap, nhan_viec)
    node, bat_dau = None, False

    def drain():
        da_bao = False
        while not vong.drain():
            if not da_bao:
                gui_thong_diep(bootstrap._ra,
                    {'protocol': PROTOCOL, 'kieu': 'drain_chua_xong'})
                da_bao = True
            time.sleep(0.1)
        if node is not None:
            node.dong()
        return True

    try:
        if node_executable is not None:
            node = NodeGia(node_executable=node_executable,
                cong=bootstrap.tham_so['cong_node_demo'],
                instance=bootstrap._cfg['instance_id'])
            node.bat_dau()
        bootstrap.bao_san_sang(phien_ban=PHIEN_BAN, contracts=list(CONTRACTS),
            kiem_san_sang=lambda: callable(doc_xml) and (node is None or node.san_sang()))
        vong.bat_dau()
        bat_dau = True
        bootstrap.cho_thu_hoi(ngung_accept=vong.ngung_accept, drain=drain)
    finally:
        if bat_dau:
            vong.ngung_accept()
            drain()
        elif node is not None:
            node.dong()
        bootstrap.socket.close()
