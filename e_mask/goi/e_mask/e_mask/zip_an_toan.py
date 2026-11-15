"""Cổng ZIP nội bộ MASK-B1: chỉ RAM, profile cổ điển, từ chối cả gói.

Chép có sửa kiểm danh mục/EOF/CRC từ mẫu nội repo; xem NGUON.md.
Không dùng ZipExtFile (có thể cắt theo kích thước tự khai).
"""

from dataclasses import dataclass, field
from datetime import datetime
import stat
import struct
import unicodedata
import zlib

from kho_tri_thuc_sdk.engine import LoiNghiepVu

MIB = 1048576
TEP_TOI_DA = MIB
TONG_GIAI_NEN_TOI_DA = 8 * MIB
PHAN_TOI_DA = 2 * MIB
SO_PHAN_TOI_DA = 256
TY_LE_TOI_DA = 200
KHOI_DOC = 65536
CAU_CHUA_HO_TRO = "Tệp có nội dung chưa được hỗ trợ xử lý đầy đủ."
CAU_QUA_GIOI_HAN = "Tệp vượt giới hạn xử lý thử nghiệm."


def _sai():
    raise LoiNghiepVu("MASK_TEP_CHUA_HO_TRO", CAU_CHUA_HO_TRO) from None


def _vuot():
    raise LoiNghiepVu("MASK_QUA_GIOI_HAN", CAU_QUA_GIOI_HAN) from None


def kiem_kich_thuoc_tep(du_lieu):
    """Dùng riêng cho cả chiều vào và chiều ra, trước phát hành."""
    if type(du_lieu) is not bytes:
        _sai()
    if len(du_lieu) > TEP_TOI_DA:
        _vuot()


def _kiem_ten(ten):
    # Chép quy tắc NFC/casefold từ closure ZIP; không sửa tên rồi đoán đích.
    phan = ten.split("/")
    if (not ten or any(p in ("", ".", "..") for p in phan)
            or any(c in ten for c in '\\:%?#<>|"*')
            or any(unicodedata.category(c).startswith("C") for c in ten)
            or any(p.endswith((" ", ".")) for p in phan)):
        _sai()
    return unicodedata.normalize("NFC", unicodedata.normalize("NFC", ten).casefold())


@dataclass(frozen=True, repr=False)
class PhanZip:
    ten: str
    phuong_thuc: int
    crc: int
    so_byte_nen: int
    so_byte: int
    le_dau: int
    le_du_lieu: int
    le_cuoi: int
    le_danh_muc: int
    cuoi_danh_muc: int
    du_lieu: bytes = field(default=b"", repr=False)


@dataclass(frozen=True, repr=False)
class GoiZip:
    goc: bytes = field(repr=False)
    phan: tuple[PhanZip, ...] = field(repr=False)
    le_danh_muc: int


def _kiem_danh_muc(raw, kiem_huy):
    """Tiền kiểm EOCD và từng record trước cấp phát danh sách thành viên."""
    kiem_kich_thuoc_tep(raw)
    kiem_huy()
    moc = len(raw) - 22
    if moc < 0 or raw[moc:moc + 4] != b"PK\x05\x06":
        _sai()
    _, dia, dia_muc, so_dia, so_muc, kich, le, ghi_chu = struct.unpack_from("<4s4H2IH", raw, moc)
    if (dia or dia_muc or so_dia != so_muc or ghi_chu
            or so_muc == 65535 or kich == 0xffffffff or le == 0xffffffff):
        _sai()
    if so_muc > SO_PHAN_TOI_DA:
        _vuot()
    if not so_muc or le + kich != moc or not raw.startswith(b"PK\x03\x04"):
        _sai()
    pos = le
    for _ in range(so_muc):
        kiem_huy()
        if pos + 46 > moc or raw[pos:pos + 4] != b"PK\x01\x02":
            _sai()
        n, x, c = struct.unpack_from("<3H", raw, pos + 28)
        if not n or x or c:  # Whitelist extra/comment rỗng, cả hai header.
            _sai()
        pos += 46 + n
        if pos > moc:
            _sai()
    if pos != moc:
        _sai()
    return le, so_muc


def _kiem_header(tao, can, co, cach, gio, ngay, dia, noi_bo, ngoai):
    # Chỉ DOS/Unix, phiên bản cổ điển, STORED/DEFLATE; không descriptor.
    if (tao >> 8 not in (0, 3) or tao & 255 not in (10, 20)
            or can not in (10, 20) or co not in (0, 0x800)
            or cach not in (0, 8) or cach == 8 and can != 20
            or dia or noi_bo or ngoai & 0xffff not in (0, 1, 32, 33)):
        _sai()
    mode = ngoai >> 16
    if stat.S_IFMT(mode) not in (0, stat.S_IFREG) or mode & ~(stat.S_IFREG | 0o777):
        _sai()
    try:
        datetime(1980 + (ngay >> 9), (ngay >> 5) & 15, ngay & 31,
                 gio >> 11, (gio >> 5) & 63, (gio & 31) * 2)
    except ValueError:
        _sai()


def _doc_danh_muc(raw, kiem_huy):
    le, so_muc = _kiem_danh_muc(raw, kiem_huy)
    pos, tong = le, 0
    cac_phan, da_co = [], set()
    for _ in range(so_muc):
        kiem_huy()
        (_, tao, can, co, cach, gio, ngay, crc, nen, dai,
         n, x, c, dia, noi_bo, ngoai, dau) = struct.unpack_from("<4s6H3I5H2I", raw, pos)
        _kiem_header(tao, can, co, cach, gio, ngay, dia, noi_bo, ngoai)
        if 0xffffffff in (nen, dai, dau):
            _sai()
        tong += dai
        if (dai > PHAN_TOI_DA or tong > TONG_GIAI_NEN_TOI_DA
                or dai > TY_LE_TOI_DA * nen):
            _vuot()
        if cach == 0 and nen != dai:
            _sai()
        ten_byte = raw[pos + 46:pos + 46 + n]
        try:
            ten = ten_byte.decode("utf-8" if co & 0x800 else "ascii")
        except UnicodeError:
            _sai()
        chuan = _kiem_ten(ten)
        if chuan in da_co:
            _sai()
        da_co.add(chuan)
        if dau + 30 > le or raw[dau:dau + 4] != b"PK\x03\x04":
            _sai()
        (_, lcan, lco, lcach, lgio, lngay, lcrc, lnen,
         ldai, ln, lx) = struct.unpack_from("<4s5H3I2H", raw, dau)
        if ((lcan, lco, lcach, lgio, lngay, lcrc, lnen, ldai, ln, lx)
                != (can, co, cach, gio, ngay, crc, nen, dai, n, 0)):
            _sai()
        bat_dau = dau + 30 + ln
        het = bat_dau + nen
        if het > le or raw[dau + 30:bat_dau] != ten_byte:
            _sai()
        cac_phan.append(PhanZip(ten, cach, crc, nen, dai, dau, bat_dau,
                               het, pos, pos + 46 + n))
        pos += 46 + n
    # Từ chối overlap, record mồ côi, prefix tự chạy, padding/trailing data.
    cuoi = 0
    for phan in sorted(cac_phan, key=lambda p: p.le_dau):
        kiem_huy()
        if phan.le_dau != cuoi:
            _sai()
        cuoi = phan.le_cuoi
    if cuoi != le:
        _sai()
    return le, cac_phan


def _giai_nen(raw, phan, tong, kiem_huy):
    """Đọc bounded đến EOF thật, kể cả khai nhỏ và giấu đuôi DEFLATE."""
    da_doc, crc = 0, 0
    dem = bytearray()
    decoder = zlib.decompressobj(-15) if phan.phuong_thuc == 8 else None

    def nhan(du_lieu):
        nonlocal da_doc, crc
        da_doc += len(du_lieu)
        tong[0] += len(du_lieu)
        if (da_doc > PHAN_TOI_DA or tong[0] > TONG_GIAI_NEN_TOI_DA
                or da_doc > TY_LE_TOI_DA * phan.so_byte_nen):
            _vuot()
        if da_doc > phan.so_byte:
            _sai()
        crc = zlib.crc32(du_lieu, crc)
        dem.extend(du_lieu)

    def giai(chunk):
        # +1 để phát hiện vượt trần/kích thước, trước khi thêm vào buffer.
        tran = min(KHOI_DOC, PHAN_TOI_DA + 1 - da_doc,
                   TONG_GIAI_NEN_TOI_DA + 1 - tong[0],
                   phan.so_byte + 1 - da_doc,
                   TY_LE_TOI_DA * phan.so_byte_nen + 1 - da_doc)
        try:
            du_lieu = decoder.decompress(chunk, tran)
        except zlib.error:
            _sai()
        if decoder.unused_data:
            _sai()
        nhan(du_lieu)
        return du_lieu

    try:
        pos = phan.le_du_lieu
        while pos < phan.le_cuoi:
            kiem_huy()
            chunk = raw[pos:min(pos + KHOI_DOC, phan.le_cuoi)]
            pos += len(chunk)
            if decoder is None:
                nhan(chunk)
            else:
                while chunk:
                    kiem_huy()
                    giai(chunk)
                    chunk = decoder.unconsumed_tail
        if decoder is not None:
            # Không flush() không trần; rút nốt output nội bộ nếu có.
            while not decoder.eof:
                kiem_huy()
                if not giai(b""):
                    break
            if not decoder.eof or decoder.unconsumed_tail or decoder.unused_data:
                _sai()
        if da_doc != phan.so_byte or crc != phan.crc:
            _sai()
        if dem.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")):
            _sai()
        kiem_huy()
        return bytes(dem)
    finally:
        dem.clear()


def doc_zip(du_lieu, kiem_huy):
    """Cổng nội bộ; chỉ trả khi mọi thành viên đạt, không ghi tệp/log."""
    le, muc = _doc_danh_muc(du_lieu, kiem_huy)
    ket_qua, tong = [], [0]
    try:
        for phan in muc:
            data = _giai_nen(du_lieu, phan, tong, kiem_huy)
            ket_qua.append(PhanZip(phan.ten, phan.phuong_thuc, phan.crc,
                                   phan.so_byte_nen, phan.so_byte, phan.le_dau,
                                   phan.le_du_lieu, phan.le_cuoi,
                                   phan.le_danh_muc, phan.cuoi_danh_muc, data))
        kiem_huy()
        return GoiZip(du_lieu, tuple(ket_qua), le)
    finally:
        muc.clear()
        ket_qua.clear()
