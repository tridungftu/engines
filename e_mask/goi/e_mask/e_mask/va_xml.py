"""Edit script nội bộ MASK-B4, ghim map B2/B3 và byte XML nguyên gốc.

Không có quyền phát hành, I/O, Ngan hoặc cờ hai lớp. Chỉ patch miền giá
trị đã qua parser/reader; không serialize cây hoặc thay toàn file bằng regex.
Mẫu đếm RAM/escape được chép có sửa từ Hóa đơn, xem NGUON.md.
"""

from bisect import bisect_right
from dataclasses import dataclass, field, fields
from hashlib import sha256
import re

from .doc_excel import ExcelDaDoc, doc_excel
from .doc_tep import (
    GoiExcel, GoiTep, KY_TU_RA_TOI_DA, kiem_byte_chu_ra, kiem_van_ban_ra,
)
from .doc_word import TaiLieuWord, doc_word
from .xml_an_toan import KY_TU_VAO_TOI_DA
from .zip_an_toan import GoiZip, PHAN_TOI_DA, TONG_GIAI_NEN_TOI_DA, _sai, _vuot


def bam(raw):
    return 'sha256:' + sha256(raw).hexdigest()


@dataclass(frozen=True, repr=False)
class KhoangByte:
    phan: str
    dau: int
    cuoi: int
    bam_phan: str
    bam_byte: str


@dataclass(frozen=True, repr=False)
class LenhSuaXML:
    vung: int
    dau: int
    cuoi: int
    chu_moi: str = field(repr=False)
    bam_vung: str
    khoang: tuple[KhoangByte, ...] = field(repr=False)


@dataclass(frozen=True, repr=False)
class KichBanXML:
    phien_ban: int
    bam_tep: str
    lenh: tuple[LenhSuaXML, ...] = field(repr=False)


def goi_cua(tai_lieu):
    if type(tai_lieu) is TaiLieuWord and type(tai_lieu.goi) is GoiTep:
        return tai_lieu.goi
    if (type(tai_lieu) is ExcelDaDoc and type(tai_lieu.goi) is GoiExcel
            and type(tai_lieu.goi.goi) is GoiTep):
        return tai_lieu.goi.goi
    _sai()


def doc_lai_nguon(tai_lieu, kiem_huy):
    """Không dùng cây/map caller đã sửa: đọc lại bytes bằng B1 và B2/B3."""
    goi = goi_cua(tai_lieu)
    if type(goi.zip) is not GoiZip:
        _sai()
    doc = doc_word if type(tai_lieu) is TaiLieuWord else doc_excel
    moi = doc(goi.zip.goc, kiem_huy=kiem_huy)
    if (goi.loai != goi_cua(moi).loai or goi.zip != goi_cua(moi).zip
            or goi.quan_he != goi_cua(moi).quan_he
            or goi.thong_ke != goi_cua(moi).thong_ke
            or type(tai_lieu) is ExcelDaDoc and tai_lieu.goi.ban_ghi != moi.goi.ban_ghi):
        _sai()
    for f in fields(tai_lieu):
        kiem_huy()
        if f.name != 'goi' and getattr(tai_lieu, f.name) != getattr(moi, f.name):
            _sai()
    return moi


def chu_vung(vung):
    return vung.van_ban if hasattr(vung, 'van_ban') else vung.chu


def _goc_vung(tai_lieu, vi):
    v = tai_lieu.vung[vi]
    if type(tai_lieu) is ExcelDaDoc and v.ma == 'o' and v.chi_so_chu is not None:
        return tai_lieu.shared[v.chi_so_chu]
    return vi


def _khoang(tai_lieu, vi, dau, cuoi, cac_phan, bam_phan, kiem_huy):
    if (type(vi) is not int or not 0 <= vi < len(tai_lieu.vung)
            or type(dau) is not int or type(cuoi) is not int):
        _sai()
    v = tai_lieu.vung[vi]
    if not 0 <= dau < cuoi <= len(chu_vung(v)):
        _sai()
    word = type(tai_lieu) is TaiLieuWord
    ds, da_lay = [], 0
    for m in (v.anh_xa if word else v.manh):
        kiem_huy()
        a, b = max(dau, m.bat_dau), min(cuoi, m.ket_thuc)
        if a >= b:
            continue
        if word and m.kieu not in ('text', 'attribute'):
            _sai()  # tab/br/note là markup, không phải miền text được sửa.
        phan = v.phan if word else m.phan
        raw = cac_phan[phan]
        spans = (m.byte_ky_tu if word else m.byte)[a - m.bat_dau:b - m.bat_dau]
        if len(spans) != b - a:
            _sai()
        # CDATA/text có thể cùng một node nhưng cách nhau bởi delimiter.
        # Chỉ gộp các khoảng byte tiếp giáp trong cùng mảnh, không nuốt markup.
        nhom = []
        for x, y in spans:
            if type(x) is not int or type(y) is not int or not 0 <= x < y <= len(raw):
                _sai()
            if nhom and nhom[-1][1] == x:
                nhom[-1] = (nhom[-1][0], y)
            else:
                nhom.append((x, y))
        for x, y in nhom:
            ds.append((KhoangByte(phan, x, y, bam_phan[phan], bam(raw[x:y])),
                       m.thuoc_tinh is not None,
                       not word and v.ma in ('o', 'shared_string')))
        da_lay += b - a
    if da_lay != cuoi - dau:
        _sai()
    return tuple(ds)


def lap_kich_ban(tai_lieu, thay_the, *, kiem_huy):
    """Nhận tuple (chỉ số vùng, đầu Unicode, cuối Unicode, chữ mới).

    Không phải contract public/JSON. Writer sẽ lập lại mọi băm/map từ bytes
    nguồn; script này không thể tự chứng nhận một gói giả đã qua B1.
    """
    goi = goi_cua(tai_lieu)
    if type(thay_the) is not tuple:
        _sai()
    if len(thay_the) > KY_TU_VAO_TOI_DA:
        _vuot()
    cac_phan = {p.ten: p.du_lieu for p in goi.zip.phan}
    bam_phan = {t: bam(b) for t, b in cac_phan.items()}
    lenh, bam_vung, da_doc, da_thay = [], {}, 0, 0
    try:
        for t in thay_the:
            kiem_huy()
            if type(t) is not tuple or len(t) != 4:
                _sai()
            vi, dau, cuoi, chu = t
            if (type(vi) is not int or not 0 <= vi < len(tai_lieu.vung)
                    or type(dau) is not int or type(cuoi) is not int or type(chu) is not str
                    or not 0 <= dau < cuoi <= len(chu_vung(tai_lieu.vung[vi]))):
                _sai()
            da_doc += cuoi - dau
            da_thay += len(chu)
            if da_doc > KY_TU_VAO_TOI_DA or da_thay > KY_TU_RA_TOI_DA:
                _vuot()
            kiem_van_ban_ra(chu, kiem_huy=kiem_huy)
            ds = _khoang(tai_lieu, vi, dau, cuoi, cac_phan, bam_phan, kiem_huy)
            v = tai_lieu.vung[vi]
            goc = _goc_vung(tai_lieu, vi)
            if goc not in bam_vung:
                bam_vung[goc] = bam(chu_vung(v).encode('utf-8'))
            lenh.append(LenhSuaXML(vi, dau, cuoi, chu, bam_vung[goc],
                                  tuple(x[0] for x in ds)))
        return KichBanXML(1, bam(goi.zip.goc), tuple(lenh))
    finally:
        cac_phan.clear()
        bam_phan.clear()
        bam_vung.clear()
        lenh.clear()


def _codec(raw):
    if raw.startswith(b'\xef\xbb\xbf'):
        return 'utf-8', 3
    if raw.startswith(b'\xff\xfe'):
        return 'utf-16-le', 2
    if raw.startswith(b'\xfe\xff'):
        return 'utf-16-be', 2
    return ('utf-16-le' if raw.startswith(b'<\0') else
            'utf-16-be' if raw.startswith(b'\0<') else 'utf-8'), 0


def _mien_gia_tri(raw, kiem_huy):
    """Tokenizer chỉ định vị miền trên XML đã được Expat kiểm cú pháp.

    Giữ ranh giới CDATA/attribute/text, kể cả UTF-16 và dấu > trong quote.
    Không chọn node/giá trị bằng tìm kiếm chuỗi hoặc regex toàn file.
    """
    codec, bom = _codec(raw)
    try:
        chu = raw[bom:].decode(codec)
    except UnicodeError:
        _sai()
    le, at, ds = [bom], bom, []
    for i, c in enumerate(chu):
        if i % 1024 == 0:
            kiem_huy()
        at += len(c.encode(codec))
        le.append(at)
    i = 0
    try:
        while i < len(chu):
            kiem_huy()
            if chu.startswith('<?xml', i):
                j = chu.find('?>', i)
                if j < 0:
                    _sai()
                i = j + 2
            elif chu.startswith('<![CDATA[', i):
                j = chu.find(']]>', i + 9)
                if j < 0:
                    _sai()
                ds.append((le[i + 9], le[j], 'cdata'))
                i = j + 3
            elif chu[i] == '<':
                i += 1
                while i < len(chu) and chu[i] != '>':
                    if i % 1024 == 0:
                        kiem_huy()
                    if chu[i] in "\"'":
                        q, dau = chu[i], i + 1
                        i = chu.find(q, dau)
                        if i < 0:
                            _sai()
                        ds.append((le[dau], le[i], 'attribute'))
                    i += 1
                i += 1
            else:
                j = chu.find('<', i)
                j = len(chu) if j < 0 else j
                ds.append((le[i], le[j], 'text'))
                i = j
        ds.sort()
        return codec, tuple(x[0] for x in ds), tuple(ds)
    finally:
        le.clear()
        ds.clear()


_ST = re.compile(r'_x[0-9a-fA-F]{4}_')


def _ma_hoa(chu, codec, kieu, st, tran, kiem_huy):
    """Chép có sửa chu_xml: ST chỉ tại ô Excel; không đổi nghĩa metadata.

    Đếm trước mỗi cấp phát nhỏ. Attribute giữ tab/LF/CR bằng character ref.
    Trong CDATA: đóng/mở ngay TRONG span, escape phần mới ở miền XML text;
    không viết &amp; như chữ trong CDATA hoặc mất CR vì XML normalization.
    """
    dem = bytearray()
    def ghi(s):
        data = s.encode(codec)
        if len(dem) + len(data) > tran:
            _vuot()
        dem.extend(data)
    try:
        if kieu == 'cdata':
            ghi(']]>')
        for i, c in enumerate(chu):
            if i % 1024 == 0:
                kiem_huy()
            n = ord(c)
            hop_le = (c in '\t\n\r' or 0x20 <= n <= 0xD7FF
                      or 0xE000 <= n <= 0xFFFD or 0x10000 <= n <= 0x10FFFF)
            if not hop_le:
                if not st or 0xD800 <= n <= 0xDFFF:
                    _sai()
                ghi(f'_x{n:04X}_')
            elif st and c == '_' and _ST.match(chu, i):
                ghi('_x005F_')
            elif c == '\r' or kieu == 'attribute' and c in '\t\n':
                ghi(f'&#{n};')
            else:
                ghi({'&': '&amp;', '<': '&lt;', '>': '&gt;',
                     '"': '&quot;', "'": '&apos;'}.get(c, c))
        if kieu == 'cdata':
            ghi('<![CDATA[')
        kiem_huy()
        return bytes(dem)
    finally:
        dem.clear()


def _chu_du_kien(tai_lieu, cac_lenh, kiem_huy):
    moi, tong, so_byte = {}, 0, 0
    for vi, v in enumerate(tai_lieu.vung):
        kiem_huy()
        goc = _goc_vung(tai_lieu, vi)
        if goc not in moi:
            chu = chu_vung(tai_lieu.vung[goc])
            ds = sorted(cac_lenh.get(goc, ()), key=lambda l: l.dau)
            dai = len(chu) + sum(len(l.chu_moi) - (l.cuoi - l.dau) for l in ds)
            if dai > KY_TU_RA_TOI_DA:
                _vuot()
            manh, at = [], 0
            try:
                for l in ds:
                    if l.dau < at:
                        _sai()
                    manh.extend((chu[at:l.dau], l.chu_moi))
                    at = l.cuoi
                manh.append(chu[at:])
                moi[goc] = ''.join(manh)
            finally:
                manh.clear()
            if type(tai_lieu) is ExcelDaDoc:
                v.kiem_thay_the(moi[goc])
                if v.ma in ('o', 'shared_string') and len(moi[goc].encode('utf-16-le')) // 2 > 32767:
                    _vuot()
        chu = moi[goc]
        tong += len(chu)
        if tong > KY_TU_RA_TOI_DA:
            _vuot()
        kiem_van_ban_ra(chu, kiem_huy=kiem_huy)
        for i in range(0, len(chu), 8192):
            kiem_huy()
            so_byte += len(chu[i:i + 8192].encode('utf-8'))
            kiem_byte_chu_ra(so_byte)
    return tuple(moi[_goc_vung(tai_lieu, i)] for i in range(len(tai_lieu.vung)))


def chuan_bi_va(tai_lieu, kich_ban, kiem_huy):
    """Kiểm toàn script, trần và lexical context trước khi ghi part/ZIP."""
    goi = goi_cua(tai_lieu)
    if (type(kich_ban) is not KichBanXML or type(kich_ban.phien_ban) is not int
            or kich_ban.phien_ban != 1 or kich_ban.bam_tep != bam(goi.zip.goc)
            or type(kich_ban.lenh) is not tuple):
        _sai()
    if len(kich_ban.lenh) > KY_TU_VAO_TOI_DA:
        _vuot()
    raw = {p.ten: p.du_lieu for p in goi.zip.phan}
    bam_phan = {t: bam(b) for t, b in raw.items()}
    bam_vung, da_doc, da_thay = {}, 0, 0
    lenh_vung, cho_va, mien, sizes = {}, {}, {}, {t: len(b) for t, b in raw.items()}
    ds = []
    try:
        for l in kich_ban.lenh:
            kiem_huy()
            if (type(l) is not LenhSuaXML or type(l.khoang) is not tuple
                    or type(l.vung) is not int or not 0 <= l.vung < len(tai_lieu.vung)
                    or type(l.dau) is not int or type(l.cuoi) is not int
                    or type(l.chu_moi) is not str
                    or not 0 <= l.dau < l.cuoi <= len(chu_vung(tai_lieu.vung[l.vung]))):
                _sai()
            da_doc += l.cuoi - l.dau
            da_thay += len(l.chu_moi)
            if da_doc > KY_TU_VAO_TOI_DA or da_thay > KY_TU_RA_TOI_DA:
                _vuot()
            if len(l.khoang) > l.cuoi - l.dau:
                _sai()
            kiem_van_ban_ra(l.chu_moi, kiem_huy=kiem_huy)
            lenh_vung.setdefault(_goc_vung(tai_lieu, l.vung), []).append(l)
        # Chặn overlap trên Unicode trước khi cấp phát map/miền lexical.
        for xs in lenh_vung.values():
            cuoi = 0
            for l in sorted(xs, key=lambda l: l.dau):
                kiem_huy()
                if l.dau < cuoi:
                    _sai()
                cuoi = l.cuoi
        du_kien = _chu_du_kien(tai_lieu, lenh_vung, kiem_huy)
        for l in kich_ban.lenh:
            kiem_huy()
            xs = _khoang(tai_lieu, l.vung, l.dau, l.cuoi, raw, bam_phan, kiem_huy)
            goc = _goc_vung(tai_lieu, l.vung)
            if goc not in bam_vung:
                bam_vung[goc] = bam(chu_vung(tai_lieu.vung[l.vung]).encode('utf-8'))
            if (l.bam_vung != bam_vung[goc]
                    or l.khoang != tuple(x[0] for x in xs)
                    or any(type(x) is not KhoangByte for x in l.khoang)):
                _sai()
            # Kể cả no-op, không cho hai lệnh cùng tuyên bố sửa một khoảng.
            for x, attr, st in xs:
                ds.append((x.phan, x.dau, x.cuoi))
            if l.chu_moi == chu_vung(tai_lieu.vung[l.vung])[l.dau:l.cuoi]:
                continue
            for j, (x, attr, st) in enumerate(xs):
                if x.phan not in mien:
                    mien[x.phan] = _mien_gia_tri(raw[x.phan], kiem_huy)
                codec, starts, ranges = mien[x.phan]
                at = bisect_right(starts, x.dau) - 1
                if at < 0 or not ranges[at][0] <= x.dau < x.cuoi <= ranges[at][1]:
                    _sai()
                kieu = ranges[at][2]
                if attr != (kieu == 'attribute'):
                    _sai()
                cho_va.setdefault(x.phan, []).append((x.dau, x.cuoi, l.chu_moi if j == 0 else '', codec, kieu, st))
        cuoi, truoc = 0, None
        for phan, a, b in sorted(ds):
            kiem_huy()
            if phan == truoc and a < cuoi:
                _sai()
            truoc, cuoi = phan, b
        # Trừ tất cả bytes sẽ bỏ trước khi thêm, không phụ thuộc thứ tự lệnh.
        for t, xs in cho_va.items():
            sizes[t] -= sum(b - a for a, b, *_ in xs)
        tong = sum(sizes.values())
        ket_qua = {}
        for t, xs in cho_va.items():
            kiem_huy()
            cac_va = []
            for a, b, chu, codec, kieu, st in sorted(xs):
                kiem_huy()
                tran = min(PHAN_TOI_DA - sizes[t], TONG_GIAI_NEN_TOI_DA - tong)
                data = _ma_hoa(chu, codec, kieu, st, tran, kiem_huy)
                sizes[t] += len(data)
                tong += len(data)
                cac_va.append((a, b, data))
            ket_qua[t] = tuple(cac_va)
        if tong > TONG_GIAI_NEN_TOI_DA or any(n > PHAN_TOI_DA for n in sizes.values()):
            _vuot()
        return ket_qua, du_kien
    finally:
        raw.clear()
        bam_phan.clear()
        bam_vung.clear()
        lenh_vung.clear()
        cho_va.clear()
        mien.clear()
        ds.clear()


def va_phan(raw, cac_va, kiem_huy):
    """Nối bytes theo khoảng đã kiểm; nguyên bytes ngoài span, có trần ghi."""
    dem, at = bytearray(), 0
    def ghi(data):
        if len(dem) + len(data) > PHAN_TOI_DA:
            _vuot()
        dem.extend(data)
    try:
        for a, b, data in cac_va:
            kiem_huy()
            if not at <= a < b <= len(raw):
                _sai()
            for i in range(at, a, 65536):
                kiem_huy()
                ghi(memoryview(raw)[i:min(a, i + 65536)])
            ghi(data)
            at = b
        for i in range(at, len(raw), 65536):
            kiem_huy()
            ghi(memoryview(raw)[i:i + 65536])
        kiem_huy()
        return bytes(dem)
    finally:
        dem.clear()
