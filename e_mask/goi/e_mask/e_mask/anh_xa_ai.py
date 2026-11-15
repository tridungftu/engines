"""MASK-2c-1: edit script nội bộ, chỉ RAM; offset Unicode code point.

Gốc → bỏ Cf/selector → NFC và gốc → che là các script riêng. Hợp thành
qua gốc để chuyển giữa bản dò và bản che; phép đổi nhiều-một trả khoảng
bao, không nội suy vị trí trong tên hay cụm NFD. Không xuất qua phong bì.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import re
import unicodedata

from .nguon.privacy.types import (bo_ky_tu_vo_hinh, cac_khoang_vo_hinh,
                                  chuan_hoa_vi_tri, la_bien_to_hop)

PHIEN_BAN_MAP = 1
HE_OFFSET = 'unicode_code_point'
_BI_DANH = re.compile(r'\[\[[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\]\]')


class LoiAnhXa(ValueError):
    def __init__(self):
        super().__init__('Không xác minh được ánh xạ văn bản an toàn.')


def bam_chu(chu):
    try:
        return 'sha256:' + sha256(chu.encode('utf-8')).hexdigest()
    except (AttributeError, UnicodeError):
        raise LoiAnhXa() from None


@dataclass(frozen=True, slots=True)
class PhepSua:
    goc: tuple[int, int]
    dich: tuple[int, int]
    loai: str


def _khoang(k, do_dai, *, co_rong=False):
    if (type(k) is not tuple or len(k) != 2 or any(type(i) is not int for i in k)
            or not 0 <= k[0] <= k[1] <= do_dai or (not co_rong and k[0] == k[1])):
        raise LoiAnhXa()


def _gop(cac_khoang):
    ket = []
    for a, b in sorted(set(cac_khoang)):
        if ket and a <= ket[-1][1]:
            ket[-1] = (ket[-1][0], max(b, ket[-1][1]))
        else:
            ket.append((a, b))
    return tuple(ket)


def _chuyen(phep_sua, khoang, *, nguoc=False):
    a, b = khoang
    if not phep_sua and a == b == 0:
        return ((0, 0),)
    ket = []
    for phep in phep_sua:
        (s, e), (u, v) = (phep.dich, phep.goc) if nguoc else (phep.goc, phep.dich)
        if s == e:  # Cf bị bỏ: điểm neo, không có ký tự ở phía đích.
            if (a == b == s) or a < s < b:
                ket.append((u, v))
        elif a == b:
            if s <= a <= e:
                ket.append((u + a - s, u + a - s) if phep.loai == 'giu_nguyen' else (u, v))
        elif a < e and s < b:
            # Chỉ phép GIỮ NGUYÊN mới có tọa độ từng code point tương ứng.
            ket.append((u + max(a, s) - s, u + min(b, e) - s)
                       if phep.loai == 'giu_nguyen' else (u, v))
    return _gop(ket)


@dataclass(frozen=True, slots=True, repr=False)
class AnhXaAI:
    goc: str
    ban_do: str
    da_che: str
    goc_sach: tuple[PhepSua, ...]
    sach_do: tuple[PhepSua, ...]
    goc_che: tuple[PhepSua, ...]
    bam_goc: str
    bam_ban_do: str
    bam_da_che: str
    phien_ban: int = PHIEN_BAN_MAP
    he_offset: str = HE_OFFSET
    phien_ban_unicode: str = unicodedata.unidata_version

    def chuyen(self, tu, den, bat_dau, ket_thuc):
        """Trả các khoảng bao; round-trip chỉ chính xác ở phần giữ nguyên.

        Khoảng rỗng dùng để tra điểm neo Cf. Kết quả khoảng bao của alias/NFD
        không được coi là bằng chứng che đủ; dùng da_che_tron cho việc đó.
        """
        chu = {'goc': self.goc, 'ban_do': self.ban_do, 'da_che': self.da_che}
        if tu not in chu or den not in chu:
            raise LoiAnhXa()
        _khoang((bat_dau, ket_thuc), len(chu[tu]), co_rong=True)
        cac = ((bat_dau, ket_thuc),)
        if tu == den:
            return cac
        if tu == 'ban_do':
            cac = _gop(k for p in cac for k in _chuyen(self.sach_do, p, nguoc=True))
            cac = _gop(k for p in cac for k in _chuyen(self.goc_sach, p, nguoc=True))
        elif tu == 'da_che':
            cac = _gop(k for p in cac for k in _chuyen(self.goc_che, p, nguoc=True))
        if den == 'ban_do':
            cac = _gop(k for p in cac for k in _chuyen(self.goc_sach, p))
            cac = _gop(k for p in cac for k in _chuyen(self.sach_do, p))
        elif den == 'da_che':
            cac = _gop(k for p in cac for k in _chuyen(self.goc_che, p))
        return cac

    def da_che_tron(self, bat_dau, ket_thuc):
        """Chỉ một phép thay alias bao trọn span gốc mới chứng minh đã che."""
        _khoang((bat_dau, ket_thuc), len(self.goc))
        return any(p.loai == 'thay_bi_danh' and p.goc[0] <= bat_dau
                   and ket_thuc <= p.goc[1] for p in self.goc_che)


def _them(phep, a, b, c, d, loai):
    if a == b:
        return
    if (phep and loai in {'giu_nguyen', 'bo_vo_hinh'} and phep[-1].loai == loai
            and phep[-1].goc[1] == a and phep[-1].dich[1] == c):
        cu = phep.pop()
        a, c = cu.goc[0], cu.dich[0]
    phep.append(PhepSua((a, b), (c, d), loai))


def _giu_va_bo(goc, a, b, dau_dich, phep):
    chu, cuoi, dich = [], a, dau_dich
    for x, y in cac_khoang_vo_hinh(goc[a:b]):
        x, y = x + a, y + a
        giu = goc[cuoi:x]
        chu.append(giu)
        _them(phep, cuoi, x, dich, dich + len(giu), 'giu_nguyen')
        dich += len(giu)
        _them(phep, x, y, dich, dich, 'bo_vo_hinh')
        cuoi = y
    giu = goc[cuoi:b]
    chu.append(giu)
    _them(phep, cuoi, b, dich, dich + len(giu), 'giu_nguyen')
    return ''.join(chu)


def tao_anh_xa(goc, thay):
    """thay = các (đầu, cuối, alias) đúng từ vòng thay tên, không diff chuỗi."""
    if type(goc) is not str or not 0 < len(goc) <= 500_000:
        raise LoiAnhXa()
    goc_sach, sach_do, goc_che = [], [], []
    sach = _giu_va_bo(goc, 0, len(goc), 0, goc_sach)
    ban_do, vi_tri = chuan_hoa_vi_tri(sach)
    if vi_tri is None:
        _them(sach_do, 0, len(sach), 0, len(ban_do), 'giu_nguyen')
    else:
        i = 0
        while i < len(ban_do):
            a, b = vi_tri[i]
            j = i + 1
            while j < len(ban_do) and vi_tri[j] == (a, b):
                j += 1
            _them(sach_do, a, b, i, j,
                  'giu_nguyen' if sach[a:b] == ban_do[i:j] else 'nfc')
            i = j
    phan, cuoi, dich = [], 0, 0
    for a, b, alias in thay:
        _khoang((a, b), len(goc))
        if (a < cuoi or type(alias) is not str or not _BI_DANH.fullmatch(alias)
                or not la_bien_to_hop(goc, a) or not la_bien_to_hop(goc, b)):
            raise LoiAnhXa()
        giu = _giu_va_bo(goc, cuoi, a, dich, goc_che)
        phan.extend((giu, alias))
        dich += len(giu)
        _them(goc_che, a, b, dich, dich + len(alias), 'thay_bi_danh')
        dich += len(alias)
        cuoi = b
    phan.append(_giu_va_bo(goc, cuoi, len(goc), dich, goc_che))
    da_che = ''.join(phan)
    return AnhXaAI(goc, ban_do, da_che, tuple(goc_sach), tuple(sach_do), tuple(goc_che),
                   bam_chu(goc), bam_chu(ban_do), bam_chu(da_che))


def _kiem_script(goc, dich, phep, cac_loai):
    if type(phep) is not tuple:
        raise LoiAnhXa()
    dau_goc = dau_dich = 0
    for p in phep:
        if type(p) is not PhepSua:
            raise LoiAnhXa()
        _khoang(p.goc, len(goc))
        _khoang(p.dich, len(dich), co_rong=True)
        if p.goc[0] != dau_goc or p.dich[0] != dau_dich or p.loai not in cac_loai:
            raise LoiAnhXa()
        x, y = goc[slice(*p.goc)], dich[slice(*p.dich)]
        if ((p.loai == 'giu_nguyen' and x != y)
                or (p.loai == 'bo_vo_hinh' and (y or bo_ky_tu_vo_hinh(x)))
                or (p.loai == 'nfc' and unicodedata.normalize('NFC', x) != y)
                or (p.loai == 'thay_bi_danh' and not _BI_DANH.fullmatch(y))):
            raise LoiAnhXa()
        dau_goc, dau_dich = p.goc[1], p.dich[1]
    if dau_goc != len(goc) or dau_dich != len(dich):
        raise LoiAnhXa()


def kiem_anh_xa(m):
    """Kiểm hai đầu, phủ đủ, ngữ nghĩa và script chuẩn; không chỉ so băm."""
    if (type(m) is not AnhXaAI or type(m.phien_ban) is not int
            or m.phien_ban != PHIEN_BAN_MAP or m.he_offset != HE_OFFSET
            or m.phien_ban_unicode != unicodedata.unidata_version
            or any(type(s) is not str for s in (m.goc, m.ban_do, m.da_che))):
        raise LoiAnhXa()
    sach = bo_ky_tu_vo_hinh(m.goc)
    _kiem_script(m.goc, sach, m.goc_sach, {'giu_nguyen', 'bo_vo_hinh'})
    _kiem_script(sach, m.ban_do, m.sach_do, {'giu_nguyen', 'nfc'})
    _kiem_script(m.goc, m.da_che, m.goc_che, {'giu_nguyen', 'bo_vo_hinh', 'thay_bi_danh'})
    thay = [(p.goc[0], p.goc[1], m.da_che[slice(*p.dich)])
            for p in m.goc_che if p.loai == 'thay_bi_danh']
    if m != tao_anh_xa(m.goc, thay):
        raise LoiAnhXa()
