"""K2: launcher của một engine đã cài, chỉ chạy trong tiến trình con Core.

ABI bootstrap: tham_so.goi = {thu_muc_da_cai, module, phien_ban, core,
gioi_han}; tham_so.pin là GhimEngine dạng JSON; tham_so.runtime chứa
khoa_cong_khai (base64), core_epoch, ngu_canh và settings. Entry lấy từ
manifest thuộc hash toàn gói trong pin, không nhận module/path từ argv.
Phong bì bi_mat giữ raw credential của ProviderCredentialKenh.bootstrap;
bản chỉ Local cấp {} cho cổng AI, không dùng credential làm khóa AI.
"""

import base64
import importlib
import importlib.abc
import importlib.util
import json
import os
from pathlib import Path
import queue
import re
import sys
import threading
from uuid import UUID

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .khoi_chay_module import _DocLai, cai_dat, goi
from . import nap_engine
from .dich_vu_engine import GhimContract, GhimEngine
from .dispatcher import KiemSchema
from .kenh_engine import KenhCore
from ..sdk_core import kenh_khung as k
from ..sdk_core.bootstrap import (Bootstrap, BiMatBootstrap, PROTOCOL, TOI_DA,
                                  TOI_DA_KHOI_DONG, doc_thong_diep)
from ..sdk_core.engine import SDKEngine, LoiEngine
from ..sdk_core.module_runtime import doc_frame, _cac_phan
from ..sdk_core.ngu_canh import _xoa_loi


class LoiKhoiChayEngine(RuntimeError):
    def __init__(self):
        super().__init__('Chưa khởi chạy được công cụ xử lý.')


def _pin(data):
    data = dict(data)
    for name in ('engine_id', 'ho_so_mau_id'):
        data[name] = UUID(data[name])
    for name in ('dau_vao', 'dau_ra'):
        data[name] = GhimContract(**data[name])
    return GhimEngine(**data)


def _doc_goi(thu_muc, cfg):
    tham_so = cfg['tham_so']
    snap, pin = tham_so['goi'], _pin(tham_so['pin'])
    folder = cai_dat._duong_ngoai_git(thu_muc)
    if (str(folder) != snap['thu_muc_da_cai'] or cfg['module'] != snap['module']
            or cfg['phien_ban'] != snap['phien_ban']
            or (cfg['module'], cfg['phien_ban']) != (pin.ma_engine, pin.phien_ban_engine)):
        raise LoiKhoiChayEngine()
    limits = goi.GioiHan(**snap['gioi_han'])
    files, _ = goi._snapshot(folder, limits)
    if goi.bam_goi(files)[1] != pin.ma_bam_goi:
        raise LoiKhoiChayEngine()
    manifest = goi.doc_json(files['engine.json'], limits)
    schemas = goi.doc_json(files['contract/schemas.json'], limits)
    nap_engine._kiem_schema_manifest(manifest, schemas, limits)
    nap_engine._kiem_contract(schemas, manifest, limits)
    goi.kiem_phien_ban(snap['core'], manifest['tuong_thich']['core'])
    caps = [c for c in manifest['capability'] if c['ma'] == pin.capability]
    if ((manifest['ma'], manifest['phien_ban'], manifest['adapter']['ma'],
            manifest['adapter']['phien_ban']) != (pin.ma_engine, pin.phien_ban_engine,
                pin.ma_adapter, pin.phien_ban_adapter)
            or len(caps) != 1 or (caps[0]['dau_vao'], caps[0]['dau_ra']) !=
                (pin.dau_vao.ma, pin.dau_ra.ma)):
        raise LoiKhoiChayEngine()
    prefix = 'kho_tri_thuc.engines.' + pin.ma_engine
    entry = manifest['ho_so_chay_mau']['diem_vao']
    if (not entry.startswith(prefix + '.')
            or not re.fullmatch(r'[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*', entry)
            or entry[len(prefix) + 1:].replace('.', '/') + '.py' not in files):
        raise LoiKhoiChayEngine()
    return folder, files, schemas, prefix, entry


class _NapEngine(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Layout engine ở gốc gói; chặn fallback sang shim nguồn hoặc sys.path."""
    def __init__(self, folder, files, prefix):
        self.folder, self.files, self.prefix = folder, files, prefix

    def _ten(self, fullname):
        return fullname[len(self.prefix):].lstrip('.').replace('.', '/')

    def find_spec(self, fullname, path=None, target=None):
        if fullname == self.prefix or fullname.startswith(self.prefix + '.'):
            base = self._ten(fullname)
            for name, package in ((base + '/__init__.py' if base else '__init__.py', True),
                                  (base + '.py', False)):
                if name in self.files:
                    return importlib.util.spec_from_loader(fullname, self,
                        origin=str(self.folder / name), is_package=package)
            raise LoiKhoiChayEngine()

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        base = self._ten(module.__name__)
        package = module.__spec__.submodule_search_locations is not None
        name = (base + '/__init__.py' if base else '__init__.py') if package else base + '.py'
        module.__file__ = str(self.folder / name)
        if package:
            module.__path__ = []
        exec(compile(self.files[name], module.__file__, 'exec'), module.__dict__)


class _DieuKhien:
    """Đóng pipe/kênh rảnh cũng đi qua thu_hoi/drain của Bootstrap hiện có."""
    def __init__(self, bootstrap, kenh_dong):
        self.b, self.dong = bootstrap, kenh_dong
        self.q = queue.Queue(maxsize=1)
        self.stop = threading.Event()
        self.vao = bootstrap._vao
        threading.Thread(target=self._doc, name='engine-dieu-khien', daemon=True).start()

    def _doc(self):
        while not self.stop.is_set():
            try:
                raw = self.vao.readline(TOI_DA)
            except (OSError, ValueError):
                raw = b''
            while not self.stop.is_set():
                try:
                    self.q.put(raw, timeout=.1)
                    break
                except queue.Full:
                    pass
            if not raw:
                return

    def readline(self, size):
        while True:
            try:
                raw = self.q.get(timeout=.1)
                if raw or not self.b._duoc_accept:
                    return raw
                self.dong.set()
            except queue.Empty:
                pass
            if self.b._duoc_accept and self.dong.is_set():
                return (json.dumps(dict(protocol=PROTOCOL, kieu='thu_hoi')) + '\n').encode('ascii')


class _SocketDocLai:
    def __init__(self, sock, raw):
        self.sock, self.raw = sock, raw

    def recv(self, size):
        if self.raw:
            out, self.raw = self.raw[:size], self.raw[size:]
            return out
        return self.sock.recv(size)

    def __getattr__(self, name):
        return getattr(self.sock, name)


class _BoGhiTheoViec:
    """Chỉ ghép writer hiện có với SDK của lease; không giữ kho nhật ký riêng."""
    def __init__(self, factory):
        self.factory, self.hien_tai = factory, None

    def gan(self, sdk):
        if not self.da_ban_giao():
            raise LoiKhoiChayEngine()
        self.hien_tai = self.factory(sdk)

    def ghi(self, record):
        if self.hien_tai is None:
            raise LoiKhoiChayEngine()
        return self.hien_tai.ghi(record)

    def thong_ke(self, window):
        if self.hien_tai is None:
            raise LoiKhoiChayEngine()
        return self.hien_tai.thong_ke(window)

    def da_ban_giao(self):
        return self.hien_tai is None or self.hien_tai.da_ban_giao()

    def thu_lai(self):
        if self.hien_tai is not None:
            return self.hien_tai.thu_lai()


def chay(thu_muc, *, stdin=None, stdout=None):
    # Reader điều khiển có thể còn chờ pipe lúc con kết thúc. Dùng raw I/O
    # để không giữ khóa BufferedReader của stdin khi Python đóng interpreter.
    vao = sys.stdin.buffer.raw if stdin is None else stdin
    dong = vao.readline(TOI_DA_KHOI_DONG + 1)
    cfg = doc_thong_diep(dong, gioi_han=TOI_DA_KHOI_DONG)
    folder, files, schemas, prefix, entry = _doc_goi(thu_muc, cfg)
    runtime = cfg['tham_so']['runtime']
    key = Ed25519PublicKey.from_public_bytes(base64.b64decode(runtime['khoa_cong_khai'], validate=True))
    binding = dict(runtime['ngu_canh'], **{name: cfg[name] for name in (
        'issuer', 'module', 'instance_id', 'the_he', 'nonce_khoi_dong')},
        core_epoch=runtime['core_epoch'])
    verifier = k.BoKiemThe(key, **{name: binding[name] for name in (
        'issuer', 'module', 'instance_id', 'the_he', 'nonce_khoi_dong', 'core_epoch')})
    check = KiemSchema(schemas).kiem
    if any(name == prefix or name.startswith(prefix + '.') for name in sys.modules):
        raise LoiKhoiChayEngine()
    loader, previous_cwd = _NapEngine(folder, files, prefix), Path.cwd()
    bootstrap = control = None
    credential = None
    closed = threading.Event()
    sys.meta_path.insert(0, loader)
    os.chdir(folder)
    try:
        backend = importlib.import_module(entry)
        # Bản 1 hiện có writer Hỏi AI. Không tự chọn writer cho engine khác.
        writer = importlib.import_module(prefix + '.nhat_ky').BoGhiQuaCore
        bo_ghi = _BoGhiTheoViec(writer)
        bootstrap = Bootstrap.nhan(kiem_chu_ky=key.verify, stdin=_DocLai(dong, vao), stdout=stdout)
        credential = bootstrap.bi_mat.lay_mot_lan()
        if len(credential) < 32:
            raise LoiKhoiChayEngine()
        bootstrap.bi_mat = BiMatBootstrap(b'{}')
        control = _DieuKhien(bootstrap, closed)
        bootstrap._vao = control
        seen = set()

        class KenhTheoViec(KenhCore):
            def __init__(self, sock):
                self._sock, self._da_noi = sock, False

            def nhan_viec(self):
                try:
                    if not self._da_noi:
                        self._sock.settimeout(5)
                        raw = doc_frame(self._sock, timeout=5)
                        trailer = k._doc_json(_cac_phan(raw)[2])
                        cid = trailer['ket_noi_id']
                        if cid in seen or len(seen) >= 100000:
                            raise LoiKhoiChayEngine()
                        proof = k.BoProof(credential, cid, vai='con', loai_con='engine')
                        seen.add(cid)
                        super().__init__(_SocketDocLai(self._sock, raw), proof=proof,
                            kiem_the=verifier, ngu_canh=binding)
                        self._da_noi = True
                    lease = super().nhan_viec()
                    if lease is not None:
                        bo_ghi.gan(SDKEngine(lease, kenh_core=self))
                    return lease
                except LoiEngine as exc:
                    # Vòng nhận việc của engine giữ nguyên chính sách chờ/thử lại.
                    if not exc.thu_lai_duoc:
                        closed.set()
                    raise
                except Exception as exc:
                    closed.set()
                    _xoa_loi(exc)
                    raise LoiEngine() from None

        def nhan_viec(sock, bo_doc):
            # KenhCore kiểm MAC/challenge và thẻ ký trong vòng nhận việc;
            # lỗi xác thực được xử lý như đóng kênh rảnh, không kẹt drain.
            return KenhTheoViec(sock)

        return backend.chay_tu_core(bootstrap=bootstrap, kiem_chu_ky=key.verify,
            nhan_viec=nhan_viec, settings=runtime['settings'], bo_ghi=bo_ghi, kiem_schema=check)
    finally:
        if control is not None:
            control.stop.set()
        if bootstrap is not None:
            bootstrap.bi_mat.thu_hoi()
            bootstrap.socket.close()
        credential = None
        sys.meta_path.remove(loader)
        os.chdir(previous_cwd)


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    try:
        if len(args) != 1:
            raise LoiKhoiChayEngine()
        chay(Path(args[0]))
        return 0
    except Exception as exc:
        _xoa_loi(exc)
    print('Chưa khởi chạy được công cụ xử lý.', file=sys.stderr)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
