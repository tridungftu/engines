"""B8: mở DOCX trên bytes hiện gửi, map chỉ RAM đúng chuỗi đã qua B7.

Tái dùng reader/patch/writer B1…B6 và bộ dò alias R6, không dò tên đã mở.
Các primitive chỉ được gọi dưới quyền sở hữu mở của R4; MoTepRAM quản
tiêu thụ/bàn giao. Không I/O hoặc đường phục hồi từ kho/Core.
"""
from functools import wraps

from . import che_van_ban as che, phong_bi
from .anh_xa_ai import LoiAnhXa, kiem_anh_xa
from .doc_word import doc_word
from .doc_tep import KY_TU_RA_TOI_DA, BYTE_CHU_RA_TOI_DA
from .ghi_zip import ghi_goi
from .ho_so_tep import GIU_DINH_DANG, TepDaMoRAM, bao_ve, loi
from .kho_anh_xa_ram import _BuocRAM, _bo_tham_chieu
from .mo_che_ram import _VUNG, kiem_map_ram
from .quyen_yeu_cau import loi_ram
from .va_xml import bam, chu_vung, lap_kich_ban, _goc_vung
from .zip_an_toan import kiem_kich_thuoc_tep


def _bao_ve_mo(ham):
    @wraps(ham)
    @bao_ve
    def goi(*a, **kw):
        buoc = kw.get('buoc')
        try:
            if type(buoc) is not _BuocRAM:
                raise loi_ram('MASK_ANH_XA_KHONG_CON')
            buoc.kiem()
            if buoc._loai != 'mo_che' or buoc.du_lieu.get('loi_mo_tep'):
                raise loi_ram('MASK_ANH_XA_KHONG_CON')
            return ham(*a, **kw)
        except BaseException:
            # Kể cả caller bắt lỗi trong with, không để lại map để thử mở.
            if type(buoc) is _BuocRAM and buoc._loai == 'mo_che':
                with buoc._kho._khoa:
                    bg = buoc._ban_ghi
                    if buoc._kho._ban_ghi is bg and bg.so_huu is buoc:
                        _bo_tham_chieu(bg.du_lieu)
                        bg.du_lieu['loi_mo_tep'] = True
                        buoc._cho_ai = False
            raise
        finally:
            a = kw = buoc = bg = None
    return goi


def _doc_map(buoc, loai, doc):
    """Chụp cùng khóa timer; kiểm băm, đủ hai lớp và map của bản đã giao."""
    aliases = gop = {}
    s = h = cac_map = goc = da_che = m = None
    try:
        m, aliases = kiem_map_ram(buoc)
        with buoc._kho._khoa:
            buoc._kho._kiem_buoc(buoc)
            du = buoc._ban_ghi.du_lieu
            h = du.get('ho_so_tep')
            s = du.get('tep_word' if loai == 'docx' else 'tep_excel')
            if type(h) is not dict or type(s) is not dict:
                raise loi_ram('MASK_ANH_XA_KHONG_CON')
            if (h.get('giai_doan') != 'DA_HAU_KIEM' or s.get('giai_doan') != 'DA_HAU_KIEM'
                    or h.get('loai') != loai or s.get('loai') != loai
                    or h.get('dang_tra') != 'tep' or h.get('nang_luc_cuoi') != GIU_DINH_DANG):
                raise loi('MASK_MO_CHE_KHONG_DAY_DU')
            goc, da_che, cac_map = s.get('goc'), s.get('da_che'), s.get('anh_xa')
            if (type(goc) is not bytes or type(da_che) is not bytes or type(cac_map) is not tuple
                    or s.get('phien_ban') != 1 or bam(goc) != s.get('bam_goc')
                    or bam(da_che) != s.get('bam_da_che') or h.get('bam_tep') != s['bam_goc']
                    or s.get('vung_da_doc') != tuple(range(len(cac_map)))
                    or s.get('vung_da_kiem_local') != tuple(range(len(cac_map)))):
                raise loi('MASK_MO_CHE_KHONG_DAY_DU')
            # Không giữ dict state có thể bị timer clear khi đọc/parser chạy.
            if type(s.get('alias_nguyen_van')) is not dict:
                raise loi('MASK_MO_CHE_KHONG_DAY_DU')
            gop = s['alias_nguyen_van'].copy()
        truoc, sau = doc(goc, kiem_huy=buoc.kiem), doc(da_che, kiem_huy=buoc.kiem)
        if len(truoc.vung) != len(cac_map) or len(sau.vung) != len(cac_map):
            raise loi('MASK_MO_CHE_KHONG_DAY_DU')
        that = {}
        for a, b, ax in zip(truoc.vung, sau.vung, cac_map):
            buoc.kiem()
            if ax is None:
                if chu_vung(a) or chu_vung(b):
                    raise loi('MASK_MO_CHE_KHONG_DAY_DU')
                continue
            kiem_anh_xa(ax)
            if ax.goc != chu_vung(a) or ax.da_che != chu_vung(b):
                raise loi('MASK_MO_CHE_KHONG_DAY_DU')
            ngoai_alias = []
            at = 0
            for p in ax.goc_che:
                if p.loai == 'thay_bi_danh':
                    ngoai_alias.extend((ax.goc[at:p.goc[0]], '\x00'))
                    at = p.goc[1]
            ngoai_alias.append(ax.goc[at:])
            if not che._kiem_tien_ngay(''.join(ngoai_alias), che._BI_DANH.sub('\x00', ax.da_che)):
                raise loi('MASK_MO_CHE_KHONG_DAY_DU')
            ngoai_alias.clear()
            for alias, nguyen_van in ax.alias_nguyen_van().items():
                ma = che.chuan_bi_danh(alias)
                if ma in that and that[ma] != nguyen_van:
                    raise loi('MASK_MO_CHE_KHONG_DAY_DU')
                that[ma] = nguyen_van
        if ({che.chuan_bi_danh(k): v for k, v in gop.items()} != that or that != aliases
                or len(that) != len(gop)):
            raise loi('MASK_MO_CHE_KHONG_DAY_DU')
        buoc.kiem()
        return goc, da_che, aliases.copy()
    except LoiAnhXa:
        buoc.kiem()
        raise loi('MASK_MO_CHE_KHONG_DAY_DU') from None
    finally:
        aliases.clear()
        gop.clear()
        s = h = du = cac_map = goc = da_che = m = truoc = sau = ax = that = None


class _MoAliasTep:
    def __init__(self, aliases, kiem):
        self.aliases, self.kiem = aliases, kiem
        self.do = che._DoManhBiDanh(aliases, kiem)
        self.da_gap, self.so_cho = set(), 0
        self.ky_tu = self.byte = 0

    def doan(self, chu):
        phep, phan, cuoi = [], [], 0
        try:
            for m in _VUNG.finditer(chu):
                self.kiem()
                ma = che.chuan_bi_danh(m.group())
                a, b = m.start() - 1, m.end()
                while a >= 0 and chu[a].isspace():
                    if a % 2048 == 0: self.kiem()
                    a -= 1
                while b < len(chu) and chu[b].isspace():
                    if b % 2048 == 0: self.kiem()
                    b += 1
                if (not che._BI_DANH.fullmatch(ma) or ma not in self.aliases
                        or a >= 0 and chu[a] == '[' or b < len(chu) and chu[b] == ']'):
                    raise loi('MASK_MO_CHE_KHONG_DAY_DU')
                phep.append((m.start(), m.end(), self.aliases[ma]))
                self.da_gap.add(ma)
                self.so_cho += 1
            if self.do.quet(chu, [(a, b) for a, b, _ in phep], ma_mask_roi=True):
                raise loi('MASK_MO_CHE_KHONG_DAY_DU')
            dai = len(chu) + sum(len(v) - (b - a) for a, b, v in phep)
            if self.ky_tu + dai > KY_TU_RA_TOI_DA:
                raise phong_bi.loi('MASK_QUA_GIOI_HAN')
            for a, b, v in phep:
                phan.extend((chu[cuoi:a], v))
                cuoi = b
            phan.append(chu[cuoi:])
            moi = ''.join(phan)
            self.ky_tu += len(moi)
            self.byte += len(moi.encode('utf-8'))
            if self.byte > BYTE_CHU_RA_TOI_DA:
                raise phong_bi.loi('MASK_QUA_GIOI_HAN')
            self.kiem()
            return tuple(phep), moi
        finally:
            phep.clear()
            phan.clear()
            chu = moi = m = v = None

    def dong(self):
        self.aliases.clear()
        self.da_gap.clear()
        self.do.kiem = self.kiem = None


def _kiem_tien_ngay(truoc, sau, phep, kiem):
    """Đối chiếu phần ngoài alias; số định danh vừa mở không phải tiền mới.

    Không chạy detector hoặc che lại tên. Vị trí sau được tính từ chính
    script mở, giữ mọi chữ/số/ngày do AI bổ sung ngoài các span này.
    """
    a0 = b0 = 0
    phan_a, phan_b = [], []
    try:
        for a, b, goc in phep:
            kiem()
            z = b0 + a - a0
            if sau[b0:z] != truoc[a0:a] or sau[z:z + len(goc)] != goc:
                raise loi('MASK_MO_CHE_KHONG_DAY_DU')
            phan_a.extend((truoc[a0:a], '\x00'))
            phan_b.extend((sau[b0:z], '\x00'))
            a0, b0 = b, z + len(goc)
        phan_a.append(truoc[a0:])
        phan_b.append(sau[b0:])
        a, b = ''.join(phan_a), ''.join(phan_b)
        if a != b or not che._kiem_tien_ngay(a, b):
            raise loi('MASK_MO_CHE_KHONG_DAY_DU')
        kiem()
    finally:
        phan_a.clear()
        phan_b.clear()
        truoc = sau = phep = a = b = goc = None


def _mo_tep(raw, *, buoc, loai, doc):
    goc = da_che = aliases = mo = tai_lieu = moi = ket = None
    thay, du_kien, cac_phep = [], [], []
    try:
        kiem_kich_thuoc_tep(raw)
        goc, da_che, aliases = _doc_map(buoc, loai, doc)
        tai_lieu = doc(raw, kiem_huy=buoc.kiem)  # Cả gói AI là đầu vào không tin cậy.
        mo = _MoAliasTep(aliases, buoc.kiem)
        da_sua = set()
        for i, v in enumerate(tai_lieu.vung):
            buoc.kiem()
            chu = chu_vung(v)
            phep, du_kien_chu = mo.doan(chu)
            if loai == 'xlsx':
                v.kiem_thay_the(du_kien_chu)  # Không sửa tên sheet mù.
            du_kien.append(du_kien_chu)
            cac_phep.append(phep)
            nguon = _goc_vung(tai_lieu, i)
            if nguon not in da_sua:
                thay.extend((i, a, b, g) for a, b, g in phep)
                da_sua.add(nguon)
        if mo.da_gap != set(aliases):
            raise loi('MASK_MO_CHE_KHONG_DAY_DU')
        nguyen = bam(raw) == bam(da_che)
        if nguyen:
            # Không dựng lại container: chính bytes gốc còn ở RAM.
            ket = goc
            kiem_kich_thuoc_tep(ket)
            doc(ket, kiem_huy=buoc.kiem)
        else:
            script = lap_kich_ban(tai_lieu, tuple(thay), kiem_huy=buoc.kiem)
            ket = ghi_goi(tai_lieu, script, kiem_huy=buoc.kiem)
            moi = doc(ket, kiem_huy=buoc.kiem)
            if len(moi.vung) != len(du_kien):
                raise loi('MASK_MO_CHE_KHONG_DAY_DU')
            for v, sau, chu, phep in zip(tai_lieu.vung, moi.vung, du_kien, cac_phep):
                buoc.kiem()
                if chu_vung(sau) != chu:
                    raise loi('MASK_MO_CHE_KHONG_DAY_DU')
                _kiem_tien_ngay(chu_vung(v), chu_vung(sau), phep, buoc.kiem)
            # B4 đã so nguyên lexical/kiểu/style/epoch/bytes ô bất biến.
        kiem_kich_thuoc_tep(ket)
        buoc.kiem()
        return TepDaMoRAM(ket, bam(raw), bam(ket), mo.so_cho, nguyen)
    finally:
        if mo is not None:
            mo.dong()
        if type(aliases) is dict:
            aliases.clear()
        thay.clear()
        du_kien.clear()
        cac_phep.clear()
        goc = da_che = raw = tai_lieu = moi = ket = script = mo = v = sau = chu = phep = None


@_bao_ve_mo
def mo_word(du_lieu, *, buoc):
    return _mo_tep(du_lieu, buoc=buoc, loai='docx', doc=doc_word)
