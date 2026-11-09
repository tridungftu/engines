"""Cổng ABBYY dùng chung cho mọi module, một engine và sổ Review 5.000 trang/30 ngày.

Bên gọi truyền Hot Folder của Review, đường dẫn ocr_abbyy/so_trang.json trong
dữ liệu Review và thư mục đệm riêng; không import bản Review đóng băng.
Sổ đọc cả [epoch, số trang] cũ và [epoch, số trang, mã giữ chỗ] mới.
Seam cũ sinh UUID riêng; lượt bền dùng mã Core cấp để nối sổ với biên nhận.
Chỉ hoàn bản ghi có đúng mã đã xác nhận sau ghi.
Chưa xác nhận được thì giữ dư, chờ lần đọc sổ sau đối chiếu đúng UUID.
Giữ chỗ trước khi gửi, chỉ hoàn khi chắc chắn ABBYY chưa nhận/xử lý.
Khóa .lock bảo vệ các tiến trình dùng cổng.

QD-20261026-06 chấp nhận Review cũ không tham gia khóa sổ/khóa in: có thể
chen hàng, vượt hạn mức giữa hai lần kiểm và ghi đè trong khe đua còn lại.
Cổng đọc lại/gộp ngay trước replace, kiểm sau ghi và thử khôi phục một lần;
không thể bảo đảm giao dịch tuyệt đối với Review không khóa. Rủi ro này hết
khi chuyển hẳn sang M4 ở cổng B. Mỗi bên chỉ nhận/dọn đúng mã việc của mình.
Không gọi ABBYY, AI hay dịch vụ mạng; không log tài liệu hoặc đường dẫn.
"""
from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
import errno
import hashlib
import io
import json
import logging
import math
import os
from pathlib import Path
import re
import secrets
import threading
import time
from uuid import UUID, uuid4
import zipfile
import zlib

from kho_tri_thuc.sdk_core.primitives import DataError


HAN_MUC, CUA_SO_NGAY = 5000, 30
TRAN_KET_QUA_MAC_DINH = 64 * 1024**2
TRAN_LOG_ABBYY = 64 * 1024
_DUOI = frozenset(("pdf", "jpg", "jpeg", "png", "tif", "tiff"))
_TU_LOI = ("error", "failed", "cannot", "unable", "lỗi", "không thể")
_KHOA: dict[tuple[str, str], threading.Lock] = {}
_CHO_DOI_CHIEU: dict[str, set[str]] = {}
_KHOA_DANH_SACH = threading.Lock()
_LOG = logging.getLogger(__name__)
# Một quy tắc cho mã Core và hai seam cũ; mọi nơi dùng fullmatch.
_MA_RE = re.compile(
    r"(?:ocr:[0-9a-f]{32}|hd\d{14}_[0-9a-f]{6}|[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})")
# Giữ dấu chấm/gạch trong token để không nhận nhầm tiền tố hoặc đuôi dài hơn.
_BIEN_TEN_TEP_LOG = re.compile(r"""[\s/\\:\"'()\[\]{},;=|<>]+""")


def chuan_hoa_ma_tuong_quan(ma, *, cho_ma_hd: bool = False) -> str:
    """Core dùng ocr:<32 hex> trong RAM/API/header; UUID cũ vẫn chuẩn hóa.

    Mã hd cũ chỉ dành cho cầu nối/Hot Folder. Dạng ocr_<hex> chỉ là tên
    tệp Windows, không được diễn giải thành mã yêu cầu từ header/API.
    """
    if (isinstance(ma, str) and _MA_RE.fullmatch(ma) is not None
            and (cho_ma_hd or not ma.startswith('hd'))):
        return ma
    # Giữ seam UUID cũ (chữ hoa, hex, URN, đối tượng UUID), không nới mã Core.
    ma = str(UUID(str(ma)))
    if _MA_RE.fullmatch(ma) is None:
        raise ValueError('Mã tương quan không hợp lệ.')
    return ma


def ten_tep_tuong_quan(ma: str) -> str:
    """Mã Core → phần tên tệp an toàn Windows, không gồm phần mở rộng."""
    if not isinstance(ma, str) or _MA_RE.fullmatch(ma) is None:
        raise ValueError('Mã tương quan không hợp lệ.')
    return ma.replace(':', '_')


def _ma_tuong_quan_tu_tep(ten: str) -> str | None:
    ten_ma = ten.partition('.')[0]
    ma = 'ocr:' + ten_ma[4:] if ten_ma.startswith('ocr_') else ten_ma
    try:
        # Không nhận tên chứa ':' hoặc tên gần giống mã hợp lệ.
        return ma if ten_tep_tuong_quan(ma) == ten_ma else None
    except ValueError:
        return None


def _khoa_cho(loai: str, thu_muc: Path) -> threading.Lock:
    key = loai, os.path.normcase(str(thu_muc.resolve()))
    with _KHOA_DANH_SACH:
        return _KHOA.setdefault(key, threading.Lock())


@contextmanager
def _khoa_tep(tep: Path, nghi: float, huy: threading.Event | None = None):
    """Giữ khóa byte đầu; giữ lock file để tránh khóa hai inode khác nhau."""
    khoa = _khoa_cho("tep", tep)
    while not khoa.acquire(timeout=nghi):
        _kiem_huy(huy)
    try:
        _kiem_huy(huy)
        tep.parent.mkdir(parents=True, exist_ok=True)
        with tep.open("a+b") as f:
            f.seek(0, os.SEEK_END)
            if f.tell() == 0:
                f.write(b"\0")
                f.flush()
            if os.name == "nt":
                import msvcrt

                def khoa_os(mo=False):
                    f.seek(0)
                    msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK if mo else msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                def khoa_os(mo=False):
                    f.seek(0)
                    fcntl.lockf(f.fileno(), fcntl.LOCK_UN if mo else fcntl.LOCK_EX | fcntl.LOCK_NB, 1)
            while True:
                _kiem_huy(huy)
                try:
                    khoa_os()
                    break
                except OSError as exc:
                    if exc.errno not in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                        raise
                    if huy is None:
                        time.sleep(nghi)
                    else:
                        huy.wait(nghi)
            try:
                _kiem_huy(huy)
                yield
            finally:
                khoa_os(mo=True)
    finally:
        khoa.release()


def _ma_moi() -> str:
    return "hd" + time.strftime("%Y%m%d%H%M%S") + "_" + secrets.token_hex(3)


def _docx_hop_le(raw: bytes) -> bool:
    """Như bản gốc: phải có word/document.xml và mọi mục ZIP đúng CRC."""
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as tep:
            return "word/document.xml" in tep.namelist() and tep.testzip() is None
    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError,
            NotImplementedError, EOFError, zlib.error):
        return False


def _xoa(tep: Path) -> None:
    if os.environ.get("CODEX_NO_DELETE_FILES", "").strip().lower() in ("1", "true", "yes", "on"):
        return
    try:
        tep.unlink()
    except OSError:
        pass


def _kiem_huy(huy: threading.Event | None) -> None:
    if huy is not None and huy.is_set():
        raise DataError("OCR_HUY", "Đã hủy nhận dạng tài liệu.")


class _VanChuyenHotFolder:
    """Chỉ vận chuyển theo mã việc; không biết sổ hạn mức hoặc số trang."""

    @staticmethod
    def _doc_ket_qua(tep: Path, toi_da_byte_ra: int) -> bytes:
        if type(toi_da_byte_ra) is not int or toi_da_byte_ra <= 0:
            raise DataError("OCR_LOI_ABBYY", "Cấu hình nhận dạng chưa hợp lệ.")
        if tep.stat().st_size > toi_da_byte_ra:
            raise DataError("OCR_QUA_CO", "Kết quả nhận dạng vượt dung lượng cho phép.")
        # Tệp vẫn có thể lớn thêm sau stat; chỉ đọc thêm một byte để phát hiện vượt trần.
        with tep.open("rb") as f:
            raw = f.read(toi_da_byte_ra + 1)
        if len(raw) > toi_da_byte_ra:
            raise DataError("OCR_QUA_CO", "Kết quả nhận dạng vượt dung lượng cho phép.")
        return raw

    @staticmethod
    def _rut(d: dict[str, Path], ma: str, duoi: str) -> bool:
        ten = ten_tep_tuong_quan(ma)
        dich = d["tam"] / f"{ten}.rut"
        try:
            os.replace(d["in"] / f"{ten}.{duoi}", dich)
        except OSError:
            return False
        _xoa(dich)
        return True

    @staticmethod
    def _don(d: dict[str, Path], ma: str) -> None:
        # Chỉ xóa file của chính mã ngẫu nhiên này, không xóa file người dùng.
        ten = ten_tep_tuong_quan(ma)
        for thu_muc in d.values():
            try:
                for tep in thu_muc.iterdir():
                    if tep.name.startswith(ten + ".") and tep.is_file():
                        _xoa(tep)
            except OSError:
                pass

    @classmethod
    def _don_sau(cls, thu_muc: Path, ma: str) -> None:
        # Như bản gốc: dọn một lần kết quả đến muộn, chỉ đúng mã này.
        hen = threading.Timer(120, cls._don, args=({"out": thu_muc}, ma))
        hen.daemon = True
        hen.start()

    @staticmethod
    def _ghi_ket_qua_muon(ma: str) -> None:
        # Chỉ mã đối chiếu cho Admin; không đọc/log nội dung, băm hoặc đường dẫn.
        try:
            _LOG.warning('%s', json.dumps(dict(ma_tuong_quan=ma,
                         ket_qua='kết quả muộn'), ensure_ascii=False))
        except Exception:
            pass

    @classmethod
    def _quet_ket_qua_muon(cls, thu_muc: Path) -> None:
        """Chạy khi giữ khóa in hoặc sau lượt; chỉ ghi nhận, không gọi chốt Core.

        Kết quả giữ nguyên để Admin đối chiếu, kể cả Core đã chốt lượt.
        Lần quét kế tiếp vẫn thấy kết quả nếu cầu khởi động lại/lỡ lịch hẹn.
        """
        try:
            for tep in thu_muc.iterdir():
                ma = _ma_tuong_quan_tu_tep(tep.name)
                if (ma is not None and not ma.startswith('hd')
                        and tep.name == ten_tep_tuong_quan(ma) + '.pdf' and tep.is_file()):
                    cls._ghi_ket_qua_muon(ma)
        except OSError:
            pass

    @classmethod
    def _hen_ket_qua_muon(cls, thu_muc: Path, ma: str) -> None:
        ten = ten_tep_tuong_quan(ma)
        def doi_chieu():
            try:
                if (thu_muc / (ten + '.pdf')).is_file():
                    cls._ghi_ket_qua_muon(ma)
            except OSError:
                pass

        hen = threading.Timer(120, doi_chieu)
        hen.daemon = True
        hen.start()

    @staticmethod
    def _loi_abbyy(thu_muc: Path, ma: str, duoi_vao: str = "pdf",
                  duoi_ra: str = "pdf") -> bool:
        ten = ten_tep_tuong_quan(ma)
        ten_day_du = (f"{ten}.{duoi_vao}", f"{ten}.{duoi_ra}")
        for tep in thu_muc.iterdir():
            ma_tep = _ma_tuong_quan_tu_tep(tep.name)
            if ((ma_tep is not None and ma_tep != ma)
                    or (ma_tep is None and tep.name.startswith(('ocr_', 'ocr:')))):
                continue
            if tep.suffix.lower() not in (".txt", ".log") or not tep.is_file():
                continue
            try:
                with tep.open("rb") as f:
                    f.seek(max(0, tep.stat().st_size - TRAN_LOG_ABBYY))
                    raw = f.read(TRAN_LOG_ABBYY + 1)[:TRAN_LOG_ABBYY]
                enc = "utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else (
                    "utf-16-le" if raw.count(b"\0") > len(raw) // 4 else "utf-8-sig")
                chu = raw.decode(enc, errors="replace").lower()
            except OSError:
                continue
            ten_cho = ten_day_du
            # Log riêng cũ có thể ghi mã trần; tên log phải đúng toàn bộ lượt.
            if tep.name == f"{ten}.log" or tep.name == f"{ten}.txt":
                ten_cho += (ten,)
            for dong in chu.splitlines():
                if (any(tu in dong for tu in _TU_LOI)
                        and any(token == ten_ky_vong
                                for token in _BIEN_TEN_TEP_LOG.split(dong)
                                for ten_ky_vong in ten_cho)):
                    return True
        return False

    def _van_chuyen(self, raw: bytes, duoi: str, d: dict[str, Path],
                    ma: str, huy, *, duoi_ra: str, hop_le, hoan_chua_gui=None,
                    toi_da_byte_ra: int = TRAN_KET_QUA_MAC_DINH,
                    giu_doi_chieu: bool = False) -> bytes:
        ten = ten_tep_tuong_quan(ma)
        vao, ra = d["in"] / f"{ten}.{duoi}", d["out"] / f"{ten}.{duoi_ra}"
        part, nhan = d["tam"] / f"{ten}.part", d["nhan"] / f"{ten}.{duoi_ra}"
        thu_muc_ra = d["out"]
        da_dua, da_nhan, da_xuat_ban = False, False, False
        da_tra = False
        ky_cu, dung_tu = None, 0.0
        try:
            with part.open("wb") as f:
                f.write(raw)
                f.flush()
                os.fsync(f.fileno())
            _kiem_huy(huy)
            os.replace(part, vao)
            da_dua = da_xuat_ban = True
            t0 = time.monotonic()
            while True:
                _kiem_huy(huy)
                now = time.monotonic()
                if now - t0 >= self.cho_toi_da:
                    raise DataError("OCR_QUA_GIO", "Đã quá thời gian chờ kết quả nhận dạng.")
                if not vao.exists():
                    da_nhan = True
                if not da_nhan and now - t0 >= self.cho_nhan:
                    if self._rut(d, ma, duoi):
                        da_dua = False
                        raise DataError("OCR_KHONG_NHAN", "ABBYY chưa nhận tài liệu trong thời gian chờ.")
                    da_nhan = True  # ABBYY có thể đang giữ file trên Windows.
                if self._loi_abbyy(d["out"], ma, duoi, duoi_ra):
                    raise DataError("OCR_LOI_ABBYY", "ABBYY không hoàn tất nhận dạng tài liệu.")
                try:
                    st = ra.stat()
                except FileNotFoundError:
                    ky_cu = None
                else:
                    da_nhan = True
                    ky = st.st_size, st.st_mtime_ns
                    if ky != ky_cu:
                        ky_cu, dung_tu = ky, now
                    elif now - dung_tu >= self.on_dinh:
                        if hop_le(self._doc_ket_qua(ra, toi_da_byte_ra)):
                            try:
                                os.replace(ra, nhan)
                            except OSError:
                                pass  # ABBYY có thể vẫn giữ file.
                            else:
                                ket_qua = self._doc_ket_qua(nhan, toi_da_byte_ra)
                                st_nhan = nhan.stat()
                                # Kiểm lại sau khi nhận để tránh đổi file giữa stat và rename.
                                if (st_nhan.st_size, st_nhan.st_mtime_ns) == ky and hop_le(ket_qua):
                                    _kiem_huy(huy)
                                    da_tra = True
                                    return ket_qua
                                os.replace(nhan, ra)
                                ky_cu = None
                if huy is None:
                    time.sleep(self.nghi)
                else:
                    huy.wait(self.nghi)
        finally:
            rut_duoc = not da_dua or self._rut(d, ma, duoi)
            chua_nhan = not da_xuat_ban
            if da_xuat_ban and not da_nhan and rut_duoc:
                try:
                    # Có thể hủy trước vòng đọc output. Rút được input chỉ
                    # cho phép hoàn nếu chưa từng thấy ABBYY nhận và không
                    # có dấu vết cùng mã trong out/nhan; lỗi kiểm tra giữ dư.
                    chua_nhan = not any(
                        tep.name.startswith(ten + ".")
                        for key in ("out", "nhan") for tep in d[key].iterdir())
                except OSError:
                    pass
            if giu_doi_chieu:
                # Giữ out/nhan theo mã bền, không dọn mất bằng chứng đến muộn.
                if not da_tra:
                    try:
                        if nhan.is_file():
                            self._ghi_ket_qua_muon(ma)
                    except OSError:
                        pass
                d = {k: d[k] for k in ("in", "tam")}
            self._don(d, ma)
            if da_dua:
                if giu_doi_chieu:
                    self._hen_ket_qua_muon(thu_muc_ra, ma)
                else:
                    self._don_sau(d["out"], ma)
            if chua_nhan and hoan_chua_gui is not None:
                hoan_chua_gui(ma)


class CongOCR(_VanChuyenHotFolder):
    def __init__(self, thu_muc_goc: Path, *, tep_so_trang: Path, thu_muc_dem: Path,
                 cho_nhan=300, cho_toi_da=1800, nghi=1.0, on_dinh=2.0):
        try:
            self.cho_nhan, self.cho_toi_da, self.nghi, self.on_dinh = (
                float(x) for x in (cho_nhan, cho_toi_da, nghi, on_dinh)
            )
            if not all(math.isfinite(x) and x > 0 for x in (
                    self.cho_nhan, self.cho_toi_da, self.nghi, self.on_dinh)):
                raise ValueError
            self.thu_muc_goc = Path(thu_muc_goc).resolve()
            self.tep_so_trang = Path(tep_so_trang).resolve()
            self.thu_muc_dem = Path(thu_muc_dem).resolve()
            self._khoa = _khoa_cho("hot_folder", self.thu_muc_goc)
            self._giu_cho: dict[str, list] = {}
            # Các đối tượng cùng sổ trong tiến trình chia sẻ danh sách chờ;
            # đọc/ghi danh sách trong khóa sổ hiện có, không tạo sổ thứ hai.
            with _KHOA_DANH_SACH:
                self._cho_doi_chieu = _CHO_DOI_CHIEU.setdefault(
                    os.path.normcase(str(self.tep_so_trang)), set())
        except (OSError, ValueError, TypeError):
            raise DataError("OCR_LOI_ABBYY", "Cấu hình nhận dạng chưa hợp lệ.") from None

    def thu_muc(self) -> dict[str, Path]:
        d = {k: self.thu_muc_goc / k for k in ("in", "out", "tam", "nhan")}
        for p in d.values():
            p.mkdir(parents=True, exist_ok=True)
        return d

    def _doc_so(self) -> list:
        """Gọi trong khóa sổ; đối chiếu lượt chưa xác nhận trước khi trả số dư."""
        ds = self._doc_so_goc()
        for ma in tuple(self._cho_doi_chieu):
            for ban_ghi in [x for x in ds if len(x) == 3 and x[2] == ma]:
                ds.remove(ban_ghi)
                # Đọc xác nhận bên trong _ghi_so không được tự gọi lại đối
                # chiếu/gộp ds cũ, tránh đệ quy hoặc thêm lại trang vừa hoàn.
                self._ghi_so(ds, bot=ban_ghi, _doi_chieu=False)
                ds = self._doc_so_goc()
            if any(len(x) == 3 and x[2] == ma for x in ds):
                raise DataError("OCR_LOI_ABBYY", "Không xác nhận được hoàn trang nhận dạng.")
            # Chỉ bỏ chờ khi đã xác nhận hoàn, hoặc đọc thấy không có mã.
            # Lỗi ở bất kỳ bước nào giữ mã để lần đọc sau tiếp tục đối chiếu.
            self._cho_doi_chieu.discard(ma)
            _LOG.info("Đã đối chiếu lượt giữ trang OCR chưa xác nhận.")
        return ds

    def _doc_so_goc(self) -> list:
        try:
            ds = json.loads(self.tep_so_trang.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return []
        # Không đặt sổ hỏng về 0; giữ nguyên bản ghi hai cột cũ của Review.
        if not isinstance(ds, list) or any(
            not isinstance(x, list) or len(x) not in (2, 3)
            or type(x[0]) not in (int, float) or not math.isfinite(x[0])
            or type(x[1]) is not int or x[1] < 0
            or (len(x) == 3 and (not isinstance(x[2], str) or not x[2]))
            for x in ds
        ):
            raise ValueError
        moc = time.time() - CUA_SO_NGAY * 86400
        return [x for x in ds if x[0] >= moc]

    def _ghi_so(self, ds: list, *, them: list | None = None,
                bot: list | None = None, _doi_chieu: bool = True) -> None:
        """Gọi trong khóa sổ; giữ cả bản ghi cũ trùng nhau và mã giữ chỗ mới."""
        tep = self.tep_so_trang
        doc_so = self._doc_so if _doi_chieu else self._doc_so_goc
        tam = tep.with_name("." + tep.name + "." + secrets.token_hex(16) + ".tmp")
        try:
            for lan in range(2):
                with tam.open("w", encoding="utf-8") as f:
                    json.dump(ds, f, ensure_ascii=False, allow_nan=False)
                    f.flush()
                    os.fsync(f.fileno())
                # Review có thể vừa ghi sau lần đọc đầu, ngay cả khi ta giữ khóa.
                moi = doc_so()
                if bot is not None and bot in moi:
                    moi.remove(bot)  # So đủ ba cột, gồm mã giữ chỗ của lượt này.
                dem = Counter(tuple(x) for x in ds) | Counter(tuple(x) for x in moi)
                gop = [list(x) for x, so in dem.items() for _ in range(so)]
                if them is not None and sum(x[1] for x in gop) > HAN_MUC:
                    raise DataError("OCR_HET_HAN_MUC", "Đã hết hạn mức trang nhận dạng trong 30 ngày.")
                if gop != ds:
                    with tam.open("w", encoding="utf-8") as f:
                        json.dump(gop, f, ensure_ascii=False, allow_nan=False)
                        f.flush()
                        os.fsync(f.fileno())
                os.replace(tam, tep)
                sau = doc_so()
                if (them is None or them in sau) and (bot is None or bot not in sau):
                    return
                _LOG.warning("Sổ trang OCR bị ghi đồng thời; kiểm tra và khôi phục có giới hạn.")
                # Một lần thử lại, vẫn gộp bản ghi Review mới ở lần đọc kế tiếp.
                ds = gop
            raise DataError("OCR_LOI_ABBYY", "Không xác nhận được cập nhật sổ trang nhận dạng.")
        finally:
            _xoa(tam)

    def _giu_trang(self, trang: int, ma: str, *, huy: threading.Event | None = None,
                  ma_ben: str | None = None) -> None:
        if ma_ben is not None and (not isinstance(ma_ben, str)
                or re.fullmatch(r'[A-Za-z0-9_:-]{1,128}', ma_ben) is None):
            raise DataError("OCR_LOI_ABBYY", "Thông tin giữ trang nhận dạng chưa hợp lệ.")
        with _khoa_tep(self.tep_so_trang.with_suffix(".lock"), self.nghi, huy):
            ds = self._doc_so()
            if ma_ben is not None:
                cu = [x for x in ds if len(x) == 3 and x[2] == ma_ben]
                if cu:
                    if len(cu) != 1 or cu[0][1] != trang:
                        raise DataError("OCR_LOI_ABBYY", "Cần đối chiếu lượt giữ trang nhận dạng.")
                    self._giu_cho[ma] = cu[0]
                    return
            if sum(x[1] for x in ds) + trang > HAN_MUC:
                raise DataError("OCR_HET_HAN_MUC", "Đã hết hạn mức trang nhận dạng trong 30 ngày.")
            ban_ghi = [time.time(), trang, ma_ben if ma_ben is not None else str(uuid4())]
            try:
                self._ghi_so(ds + [ban_ghi], them=ban_ghi)
                if ban_ghi not in self._doc_so():
                    raise DataError("OCR_LOI_ABBYY", "Không xác nhận được cập nhật sổ trang nhận dạng.")
            except BaseException:
                # Có thể đã lưu rồi mới lỗi/hủy khi đọc xác nhận. Chỉ nhận
                # con trỏ nếu đọc lại thấy đúng UUID; chưa lưu thì không hoàn.
                try:
                    if ban_ghi in self._doc_so():
                        self._giu_cho[ma] = ban_ghi
                except BaseException:
                    # QD-TAM-20261107-04: không có con trỏ để hoàn mù và
                    # không gửi ABBYY. Giữ dư đến lần đọc thành công kế tiếp,
                    # kể cả khi đọc phục hồi bị KeyboardInterrupt.
                    self._cho_doi_chieu.add(ban_ghi[2])
                    _LOG.warning("Chưa xác nhận được lượt giữ trang OCR; giữ dư chờ đối chiếu.")
                raise
            self._giu_cho[ma] = ban_ghi

    def _hoan_trang(self, ma: str) -> None:
        ban_ghi = self._giu_cho.get(ma)
        if ban_ghi is None or len(ban_ghi) != 3:
            return
        with _khoa_tep(self.tep_so_trang.with_suffix(".lock"), self.nghi):
            ds = self._doc_so()
            if ban_ghi in ds:
                ds.remove(ban_ghi)
            self._ghi_so(ds, bot=ban_ghi)
            self._giu_cho.pop(ma, None)

    def _chay_hot_folder(self, raw: bytes, duoi: str, d: dict[str, Path],
                        ma: str, huy: threading.Event | None) -> bytes:
        # Đường DOCX giữ nguyên chính sách hoàn khi chưa gửi/rút được đầu vào.
        return self._van_chuyen(raw, duoi, d, ma, huy, duoi_ra="docx",
                               hop_le=_docx_hop_le, hoan_chua_gui=self._hoan_trang,
                               toi_da_byte_ra=TRAN_KET_QUA_MAC_DINH)

    def ocr(self, raw: bytes, duoi: str, *, huy: threading.Event | None = None) -> bytes:
        """PDF/ảnh → DOCX; đệm SHA256 bền vững, không ghi nội dung vào log.

        Lỗi và hủy sau khi ABBYY nhận vẫn tính trang. Kết quả đến muộn không
        được nhận; dọn thêm một lần sau 120 giây như bản gốc Review.
        """
        if not isinstance(duoi, str) or duoi.lower().lstrip(".") not in _DUOI or not isinstance(raw, bytes) or not raw:
            raise DataError("OCR_DINH_DANG", "Chỉ nhận tài liệu PDF hoặc ảnh scan được hỗ trợ.")
        duoi = duoi.lower().lstrip(".")
        _kiem_huy(huy)
        while not self._khoa.acquire(timeout=self.nghi):
            _kiem_huy(huy)
        try:
            _kiem_huy(huy)
            self.thu_muc_dem.mkdir(parents=True, exist_ok=True)
            dem = self.thu_muc_dem / (hashlib.sha256(raw).hexdigest() + ".docx")
            try:
                docx = self._doc_ket_qua(dem, TRAN_KET_QUA_MAC_DINH)
            except FileNotFoundError:
                pass
            else:
                if _docx_hop_le(docx):
                    return docx
            with _khoa_tep(self.thu_muc_goc / "in.lock", self.nghi, huy):
                # Tiến trình khác có thể vừa ghi đệm trong lúc ta chờ khóa in.
                try:
                    docx = self._doc_ket_qua(dem, TRAN_KET_QUA_MAC_DINH)
                except FileNotFoundError:
                    pass
                else:
                    if _docx_hop_le(docx):
                        return docx
                _kiem_huy(huy)
                d = self.thu_muc()
                trang = max(1, len(re.findall(rb"/Type\s*/Page(?![a-zA-Z])", raw))) if duoi == "pdf" else 1
                ma = _ma_moi()
                try:
                    self._giu_trang(trang, ma, huy=huy)
                    docx = self._chay_hot_folder(raw, duoi, d, ma, huy)
                finally:
                    self._giu_cho.pop(ma, None)
                tam = dem.with_name(ma + ".tmp")
                try:
                    tam.write_bytes(docx)
                    os.replace(tam, dem)
                finally:
                    _xoa(tam)
                return docx
        except (OSError, ValueError, TypeError, OverflowError) as exc:
            if isinstance(exc, DataError):
                raise
            raise DataError("OCR_LOI_ABBYY", "Không hoàn tất xử lý nhận dạng tài liệu.") from None
        finally:
            self._khoa.release()


class _ChoHotFolder:
    """Tín hiệu hủy kèm thời hạn, dùng cả trong khóa tệp; không tạo luồng."""

    def __init__(self, huy, cho_toi_da):
        self.huy = huy
        self.het_luc = time.monotonic() + cho_toi_da

    def is_set(self):
        if self.huy is not None and self.huy.is_set():
            return True
        if time.monotonic() >= self.het_luc:
            raise DataError("OCR_QUA_GIO", "Đã quá thời gian chờ kết quả nhận dạng.")
        return False

    def wait(self, giay):
        if self.is_set():
            return True
        giay = min(giay, max(0.0, self.het_luc - time.monotonic()))
        if self.huy is None:
            time.sleep(giay)
        else:
            self.huy.wait(giay)
        return self.is_set()


def _pdf_hop_le(raw: bytes) -> bool:
    # Chỉ kiểm dấu đầu/cuối của tệp đã ghi xong. Lớp chọn nguồn kiểm PDF,
    # lớp chữ và số trang bằng bộ đọc hiện có; transport không tự đếm trang.
    return raw.startswith(b"%PDF-") and raw.rstrip().endswith(b"%%EOF")


class HotFolderPDF(_VanChuyenHotFolder):
    """Backend PDF cho ChonNguonOCR; Core cấp thư mục và bật tường minh.

    Mặc định tắt. Không đọc cấu hình, tự tạo Hot Folder hoặc kiểm máy ABBYY
    khi khởi tạo. Không dùng sổ trang/đệm DOCX; bên gọi chịu trách nhiệm
    hạn mức và đối chiếu sau lỗi. ABBYY phải được cấu hình xuất PDF lớp chữ
    cùng mã việc vào out; kiểm đủ lớp chữ thuộc lớp chọn nguồn hiện có.
    """

    def __init__(self, thu_muc_goc: Path, *, bat=False, cho_nhan=300,
                 cho_toi_da=1800, nghi=1.0, on_dinh=2.0):
        try:
            self.cho_nhan, self.cho_toi_da, self.nghi, self.on_dinh = (
                float(x) for x in (cho_nhan, cho_toi_da, nghi, on_dinh)
            )
            if type(bat) is not bool or not all(math.isfinite(x) and x > 0 for x in (
                    self.cho_nhan, self.cho_toi_da, self.nghi, self.on_dinh)):
                raise ValueError
            # Không resolve/stat hoặc dò thư mục trong lúc khởi tạo.
            self.thu_muc_goc = Path(thu_muc_goc)
            self.bat = bat
        except (OSError, ValueError, TypeError):
            raise DataError("OCR_LOI_ABBYY", "Cấu hình nhận dạng chưa hợp lệ.") from None

    def san_sang(self) -> bool:
        """Chỉ báo đường cục bộ được bật và đủ thư mục, không xác nhận ABBYY chạy."""
        if not self.bat:
            return False
        try:
            return all((self.thu_muc_goc / k).is_dir() for k in ("in", "out", "tam", "nhan"))
        except OSError:
            return False

    def doc_pdf(self, raw: bytes, duoi: str = "pdf", *, huy=None,
                toi_da_byte_ra: int = TRAN_KET_QUA_MAC_DINH,
                ma_tuong_quan: str | None = None) -> bytes:
        """PDF/ảnh → bytes PDF; không đếm/giữ/hoàn trang hoặc gửi lại tài liệu.

        duoi giữ tương thích cách ChonNguonOCR gọi backend cho PDF/PNG/JPEG.
        Thời hạn bao gồm chờ khóa chung in.lock với đường DOCX hiện có.
        Luôn kiểm kích thước và đọc có trần ở cả trước/sau khi nhận tệp.
        Có mã Core: ánh xạ ocr:<hex> thành ocr_<hex> cho tên tệp Windows;
        ABBYY phải giữ nguyên tên đầu vào khi xuất PDF vào out.
        Không có mã: giữ nguyên tên và chính sách dọn của seam cũ.
        """
        if ma_tuong_quan is not None:
            try:
                ten = ten_tep_tuong_quan(ma_tuong_quan)
            except ValueError:
                raise DataError("OCR_MA_YEU_CAU", "Thông tin yêu cầu nhận dạng không hợp lệ.") from None
        if type(toi_da_byte_ra) is not int or toi_da_byte_ra <= 0:
            raise DataError("OCR_LOI_ABBYY", "Cấu hình nhận dạng chưa hợp lệ.")
        if (not isinstance(raw, bytes) or not raw or not isinstance(duoi, str)
                or duoi.lower().lstrip(".") not in _DUOI):
            raise DataError("OCR_DINH_DANG", "Chỉ nhận tài liệu PDF hoặc ảnh scan được hỗ trợ.")
        cho = _ChoHotFolder(huy, self.cho_toi_da)
        chua_gui = True

        def xac_nhan_chua_gui(ma):
            nonlocal chua_gui
            chua_gui = True

        try:
            _kiem_huy(huy)
            if not self.san_sang():
                raise DataError("ABBYY_KHONG_KET_NOI", "Không kết nối được máy ABBYY.")
            with _khoa_tep(self.thu_muc_goc / "in.lock", min(self.nghi, self.cho_toi_da), cho):
                _kiem_huy(cho)
                if not self.san_sang():
                    raise DataError("ABBYY_KHONG_KET_NOI", "Không kết nối được máy ABBYY.")
                d = {k: self.thu_muc_goc / k for k in ("in", "out", "tam", "nhan")}
                if ma_tuong_quan is not None:
                    self._quet_ket_qua_muon(d["out"])
                    # Không ghi đè hoặc nhận lại kết quả của lượt cũ, kể cả
                    # sau khi cầu khởi động lại. Core là nơi quyết định CAS.
                    if any(tep.name.startswith(ten + '.')
                           for thu_muc in d.values() for tep in thu_muc.iterdir()):
                        chua_gui = False  # Có bằng chứng lượt trước, không hoàn mù.
                        raise DataError("OCR_CHO_DOI_CHIEU", "Tài liệu đang chờ đối chiếu kết quả nhận dạng.")
                chua_gui = False
                return self._van_chuyen(raw, duoi.lower().lstrip("."), d,
                                       ma_tuong_quan if ma_tuong_quan is not None else _ma_moi(), cho,
                                       duoi_ra="pdf", hop_le=_pdf_hop_le,
                                       hoan_chua_gui=xac_nhan_chua_gui,
                                       toi_da_byte_ra=toi_da_byte_ra,
                                       giu_doi_chieu=ma_tuong_quan is not None)
        except (OSError, ValueError, TypeError, OverflowError) as exc:
            if isinstance(exc, DataError):
                exc.chua_ro_da_nhan = not chua_gui
                raise
            loi = DataError("OCR_LOI_ABBYY", "Không hoàn tất xử lý nhận dạng tài liệu.")
            loi.chua_ro_da_nhan = not chua_gui
            raise loi from None
        except BaseException as exc:
            # Callback chỉ xác nhận chưa nhận khi không có dấu đã xử lý.
            # Không tính trang tại transport; seam cũ bỏ qua metadata này.
            exc.chua_ro_da_nhan = not chua_gui
            raise


# Giữ định danh lớp legacy cho hash/pickle và consumer hiện có.
CongOCR.__module__ = 'kho_tri_thuc.ha_tang.cong_ocr'
