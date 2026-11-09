"""G3-GOI-10/11: discovery một cấp và nối pins E2, không kích hoạt.

Root do composition tin cậy cấp, không lấy từ request. Kết quả nội bộ giữ
snapshot JSON bất biến; DAT chỉ là kiểm discovery, không phải KT, quyền chạy,
package hash, registry hay pins. Bước cài/khởi chạy phải kiểm lại toàn gói.
doc_engines chỉ đọc thư mục/JSON; QuanLyEngine dùng snapshot toàn gói của
Core để đối chiếu hash với pins trước khi chuyển sang provider runtime E2.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import json
import os
from pathlib import Path
import re
import stat
from types import MappingProxyType
from urllib.parse import unquote

from . import goi


_CONTRACT = 'urn:ktt:contract:'
_MANIFEST = 'urn:ktt:manifest:engine.v1'


@dataclass(frozen=True)
class EnginePhatHien:
    """DTO nội bộ; không trả đường dẫn/bytes trực tiếp qua HTTP.

    sha256_json chỉ băm engine.json và contract/schemas.json đã đọc.
    Không dùng giá trị này làm sha256_goi hoặc bỏ qua kiểm KT/runtime.
    manifest trả bản mới để caller không sửa snapshot đã kiểm.
    """

    thu_muc: Path
    ma: str | None
    phien_ban: str | None
    ket_luan: str
    ly_do: tuple[str, ...]
    cac_tep_json: object
    sha256_tung_tep: object
    sha256_json: str | None

    @property
    def manifest(self):
        raw = self.cac_tep_json.get('engine.json')
        return goi.doc_json(raw, goi.GioiHan(json=len(raw))) if raw else None


class _ChuaKiem(goi.LoiGoi):
    pass


def _thu_muc(path):
    path = goi.kiem_duong_dan(path)
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode):
        raise goi.LoiGoi('Đường dẫn gói phải là thư mục tồn tại.')
    return info


def _tep_thuong(path):
    goi.kiem_duong_dan(path)
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise goi.LoiGoi('Gói phải dùng tệp thường, không liên kết hoặc tệp đặc biệt.')
    return info


def _dau_tep(info):
    # Windows/Python 3.12 có thể trả ctime khác giữa lstat và fstat cho
    # tệp vừa ghi (creation/change time). Dùng identity, size, mtime như
    # snapshot Core; sau đó còn đối chiếu lại chính bytes JSON.
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


def _doc_json(path, limits):
    before = _tep_thuong(path)
    if before.st_size > min(limits.json, limits.moi_tep):
        raise goi.LoiGoi('JSON vượt giới hạn kích thước.')
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_BINARY', 0)
                 | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
    with os.fdopen(fd, 'rb') as stream:
        opened = goi._kiem_handle(stream.fileno(), path)
        raw = stream.read(min(limits.json, limits.moi_tep) + 1)
        after = os.fstat(stream.fileno())
    if (_dau_tep(before) != _dau_tep(opened)
            or _dau_tep(opened) != _dau_tep(after)
            or _dau_tep(after) != _dau_tep(_tep_thuong(path))
            or len(raw) != before.st_size):
        raise goi.LoiGoi('Tệp JSON thay đổi trong lúc đọc.')
    return raw, goi.doc_json(raw, limits)


def _diem_vao(folder, manifest):
    entry = manifest['ho_so_chay_mau']['diem_vao']
    prefix = 'kho_tri_thuc.engines.' + manifest['ma'] + '.'
    if not isinstance(entry, str) or not entry.startswith(prefix):
        raise goi.LoiGoi('Điểm khởi chạy phải thuộc chính gói engine.')
    suffix = entry[len(prefix):].split('.')
    if any(not re.fullmatch(r'[a-z][a-z0-9_]*', part) for part in suffix):
        raise goi.LoiGoi('Điểm khởi chạy không hợp lệ.')
    # Phần cuối có thể là hàm, như tich_hop.chay_noi. Chỉ xác minh
    # module chứa nó tồn tại; không import để kiểm callable/side effect.
    for count in range(len(suffix), 0, -1):
        module = folder.joinpath(*suffix[:count])
        for candidate in (module.with_suffix('.py'), module / '__init__.py'):
            try:
                _tep_thuong(candidate)
                return
            except FileNotFoundError:
                continue
    raise goi.LoiGoi('Gói thiếu tệp chứa điểm khởi chạy.')


def _id_contract(ref):
    return ref if ref.startswith(_CONTRACT) else _CONTRACT + ref


def _kiem_contract(bundle, manifest, limits):
    """Closure phải có trong bundle, không mượn schema thiếu từ Core/mạng.

    Contract đã công bố phải giữ nguyên nội dung theo Core (cùng ID/hash
    JSON chuẩn hóa). Đây là bản phân phối; không duyệt contract mới.
    """
    core = goi.doc_json((goi.THU_MUC_CONTRACT / 'ky_thuat.json').read_bytes(), limits)
    if not isinstance(bundle, dict) or not bundle:
        raise goi.LoiGoi('Gói thiếu bộ contract công bố.')
    for identity, schema in bundle.items():
        if (identity not in core or not isinstance(schema, dict)
                or schema.get('$id') != identity
                or json.dumps(schema, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
                != json.dumps(core[identity], sort_keys=True, ensure_ascii=False, separators=(',', ':'))):
            raise goi.LoiGoi('Contract không khớp bản công bố của Core.')

    def resolve(ref, base):
        identity, _, fragment = ref.partition('#')
        identity = identity or base
        if identity not in bundle:
            raise goi.LoiGoi('Bộ contract thiếu tham chiếu offline.')
        target = bundle[identity]
        if fragment:
            fragment = unquote(fragment)
            if not fragment.startswith('/'):
                raise goi.LoiGoi('Tham chiếu contract không hợp lệ.')
            for token in fragment[1:].split('/'):
                token = token.replace('~1', '/').replace('~0', '~')
                target = target[int(token)] if isinstance(target, list) else target[token]
        return target

    for cap in manifest['capability']:
        for name in ('dau_vao', 'dau_ra'):
            resolve(_id_contract(cap[name]), '')
    for identity, schema in bundle.items():
        pending = [schema]
        while pending:
            node = pending.pop()
            if not isinstance(node, dict):
                continue
            for field in ('$ref', '$dynamicRef'):
                if field in node:
                    resolve(node[field], identity)
            pending.extend(goi._schema_children(node))


def _kiem_schema_manifest(manifest, bundle, limits):
    # Không có dependency sẵn có thì CHUA_KIEM; không dùng fallback
    # giản lược để chứng nhận schema, không cài thêm thư viện.
    try:
        Validator, checker, registry, _, schemas = goi.dung_registry_schema(gioi_han=limits)
    except goi.LoiGoi as exc:
        if str(exc).startswith('Thiếu jsonschema/referencing;'):
            raise _ChuaKiem('Chưa có bộ kiểm schema đầy đủ để xác minh gói.') from None
        raise
    try:
        Validator(schemas[_MANIFEST], registry=registry, format_checker=checker).validate(manifest)
        for schema in bundle.values():
            Validator.check_schema(schema)
    except Exception:
        raise goi.LoiGoi('Manifest hoặc schema contract không hợp lệ.') from None


def _kiem_manifest(manifest, folder, core_version):
    if (not isinstance(manifest, dict) or manifest.get('loai') != 'engine'
            or type(manifest.get('phien_ban_manifest')) is not int
            or manifest['phien_ban_manifest'] != 1
            or not re.fullmatch(r'[a-z][a-z0-9_]*', manifest.get('ma', ''))):
        raise goi.LoiGoi('Bản khai gói engine không hợp lệ.')
    goi._semver(manifest['phien_ban'])
    if manifest['ma'] != folder.name:
        raise goi.LoiGoi('Mã engine không khớp tên thư mục gói.')
    goi.kiem_phien_ban(core_version, manifest['tuong_thich']['core'])
    caps = manifest['capability']
    if not isinstance(caps, list) or not caps:
        raise goi.LoiGoi('Gói chưa công bố năng lực đã kiểm.')
    seen = set()
    for cap in caps:
        code = cap['ma']
        if not isinstance(code, str) or not re.fullmatch(r'[a-z][a-z0-9_.]*@[1-9][0-9]*', code):
            raise goi.LoiGoi('Năng lực chưa ghim phiên bản hợp lệ.')
        if code in seen:
            raise goi.LoiGoi('Gói khai trùng năng lực.')
        seen.add(code)
    _diem_vao(folder, manifest)


def _doc_engine(folder, limits, core_version):
    files = {}
    identity = version = None
    state, reasons = 'KHONG_DAT', ()
    try:
        before = _thu_muc(folder)
        raw, manifest = _doc_json(folder / 'engine.json', limits)
        files['engine.json'] = raw
        if isinstance(manifest, dict):
            code, ver = manifest.get('ma'), manifest.get('phien_ban')
            if isinstance(code, str) and re.fullmatch(r'[a-z][a-z0-9_]*', code):
                identity = code
            if isinstance(ver, str):
                goi._semver(ver)
                version = ver
        _kiem_manifest(manifest, folder, core_version)
        raw, bundle = _doc_json(folder / 'contract' / 'schemas.json', limits)
        files['contract/schemas.json'] = raw
        if sum(map(len, files.values())) > limits.ca_goi:
            raise goi.LoiGoi('JSON của gói vượt giới hạn tổng kích thước.')
        _kiem_contract(bundle, manifest, limits)
        # Kiểm lại JSON sau khi gom để phát hiện đổi giữa hai lần đọc.
        for name, expected in files.items():
            if _doc_json(folder / name, limits)[0] != expected:
                raise goi.LoiGoi('JSON của gói thay đổi trong lúc khám phá.')
        after = _thu_muc(folder)
        if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
            raise goi.LoiGoi('Thư mục gói thay đổi trong lúc khám phá.')
        _kiem_schema_manifest(manifest, bundle, limits)
        state = 'DAT'
        reasons = ('Đã kiểm bản khai và contract tĩnh; chưa xác nhận điều kiện vận hành.',)
    except _ChuaKiem as exc:
        state, reasons = 'CHUA_KIEM', (str(exc),)
    except FileNotFoundError:
        reasons = ('Gói thiếu bản khai, bộ contract hoặc tệp khởi chạy.',)
    except goi.LoiGoi as exc:
        reasons = (str(exc),)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, IndexError, RecursionError):
        reasons = ('Không đọc hoặc xác minh được gói engine an toàn.',)
    hashes, digest = goi.bam_goi(files)
    return EnginePhatHien(folder, identity, version, state, reasons,
                         MappingProxyType(files), MappingProxyType(hashes), digest if files else None)


def doc_engines(thu_muc_engines, *, phien_ban_core, gioi_han=None):
    """Quét đúng một cấp, trả mọi thư mục ứng viên kể cả gói thiếu/sai.

    Không chọn thắng khi trùng mã (kể cả khác version), không cài/đăng ký,
    không spawn/import engine hay đọc mã Python. Tệp gốc như du_kien.json
    không phải engine. Root tuyệt đối giúp kết quả không phụ thuộc cwd.
    Lỗi root được raise; lỗi từng gói nằm trong kết quả, không bị bỏ im lặng.
    """
    limits = gioi_han or goi.GioiHan()
    goi._semver(phien_ban_core)
    if not isinstance(thu_muc_engines, (str, Path)) or not Path(thu_muc_engines).is_absolute():
        raise goi.LoiGoi('Thư mục engine phải là đường dẫn tuyệt đối từ cấu hình Core.')
    root = goi.kiem_duong_dan(thu_muc_engines)
    try:
        before = _thu_muc(root)
        folders = []
        with os.scandir(root) as entries:
            for count, entry in enumerate(entries, 1):
                if count > limits.so_muc:
                    raise goi.LoiGoi('Thư mục engine vượt giới hạn số mục.')
                info = entry.stat(follow_symlinks=False)
                if (stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode)
                        or getattr(info, 'st_file_attributes', 0) & 0x400):
                    folders.append(root / entry.name)
        results = [_doc_engine(p, limits, phien_ban_core)
                   for p in sorted(folders, key=lambda p: (p.name.casefold(), p.name))]
        after = _thu_muc(root)
        if _dau_tep(before) != _dau_tep(after):
            raise goi.LoiGoi('Thư mục engine thay đổi trong lúc khám phá.')
    except OSError:
        raise goi.LoiGoi('Không đọc được thư mục engine đã cấu hình.') from None
    counts = {}
    names = {}
    for row in results:
        if row.ma:
            counts[row.ma] = counts.get(row.ma, 0) + 1
        key = row.thu_muc.name.casefold()
        names[key] = names.get(key, 0) + 1
    return tuple(replace(row, ket_luan='KHONG_DAT', ly_do=row.ly_do + (
        'Trùng mã engine hoặc tên thư mục; chưa được chọn gói để sử dụng.',))
        if counts.get(row.ma, 0) > 1 or names[row.thu_muc.name.casefold()] > 1 else row
        for row in results)


class QuanLyEngine:
    """Nối inventory tĩnh với provider E2, không cài/ghi registry hay bật engine.

    Pins vẫn do bootstrap đã duyệt cấp; E2 tiếp tục kiểm registry, contract,
    hồ sơ, KT và lease mỗi lần dùng. Manager chỉ kiểm thêm gói trên đĩa khớp
    pins, không biến DAT discovery thành bằng chứng vận hành. Snapshot ban
    đầu chỉ phục vụ inventory nội bộ; không phải response HTTP quản trị.
    """

    def __init__(self, thu_muc_engines, *, phien_ban_core, gioi_han=None):
        self._root = thu_muc_engines
        self._core = phien_ban_core
        self._limits = gioi_han or goi.GioiHan()
        self._phat_hien = doc_engines(self._root, phien_ban_core=self._core,
                                     gioi_han=self._limits)

    @property
    def phat_hien(self):
        return self._phat_hien

    def _kiem_ghim(self, pin):
        rows = doc_engines(self._root, phien_ban_core=self._core,
                           gioi_han=self._limits)
        found = [r for r in rows if r.ma == pin.ma_engine
                 or r.thu_muc.name == pin.ma_engine]
        if len(found) != 1 or found[0].ket_luan != 'DAT':
            raise goi.LoiGoi('Gói đã ghim chưa đủ bằng chứng discovery.')
        row = found[0]
        manifest = row.manifest
        if (manifest['ma'], manifest['phien_ban'], manifest['adapter']['ma'],
                manifest['adapter']['phien_ban']) != (
                pin.ma_engine, pin.phien_ban_engine, pin.ma_adapter,
                pin.phien_ban_adapter):
            raise goi.LoiGoi('Gói không khớp danh tính đã ghim.')
        caps = [c for c in manifest['capability'] if c['ma'] == pin.capability]
        if (len(caps) != 1 or (caps[0]['dau_vao'], caps[0]['dau_ra'])
                != (pin.dau_vao.ma, pin.dau_ra.ma)):
            raise goi.LoiGoi('Gói không khớp capability/contract đã ghim.')
        # Tái dùng snapshot/hash toàn gói của bộ kiểm Core. sha256_json của
        # discovery tuyệt đối không thay cho ma_bam_goi trong registry/pins.
        files, _ = goi._snapshot(row.thu_muc, self._limits)
        if (any(files.get(name) != raw for name, raw in row.cac_tep_json.items())
                or goi.bam_goi(files)[1] != pin.ma_bam_goi):
            raise goi.LoiGoi('Bytes gói đã thay đổi hoặc khác pins đã duyệt.')

    def ghep_runtime(self, provider):
        """Bọc provider tin cậy; root rỗng lúc dựng giữ nguyên đường E2 cũ.

        Không cập nhật pins khi gói đổi version. Lần dựng Core tiếp theo vẫn
        cần cùng pins đã duyệt; provider giữ công tắc TAT/drain/ACK hiện có.
        Đây không phải launcher; không dùng đường dẫn discovery để thực thi.
        """
        if provider is None or not self._phat_hien:
            return provider
        if not callable(provider):
            raise ValueError('Cần provider runtime Core.')

        def runtime(pin):
            from .dich_vu_engine import LoiDichVuEngine
            failed = False
            try:
                self._kiem_ghim(pin)
            except (goi.LoiGoi, OSError, ValueError, TypeError, KeyError):
                failed = True
            if failed:
                # Không phản chiếu path/JSON hoặc diagnostic hệ điều hành.
                raise LoiDichVuEngine('ENGINE_GOI_KHONG_KHOP') from None
            return provider(pin)

        return runtime
