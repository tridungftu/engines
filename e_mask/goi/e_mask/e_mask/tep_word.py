"""MASK-B5: che Word nội bộ, không có cửa phát hành hoặc upload.

B1/B2/B4 kiểm và patch bytes; MASK-2b/R3 tìm từng ứng viên chính xác;
R4 sở hữu toàn bộ dữ liệu, R5 kiểm map/tiền/ngày. B7/B9 còn phải kiểm
nguồn Local đủ mọi vùng và quyền bàn giao. Không nhận cờ đã kiểm Local.
Nguồn/symbol/quyền/băm trước và sau được ghi trong NGUON.md.
"""
from dataclasses import dataclass
from functools import wraps
from hashlib import sha256
from time import monotonic

from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, ViecDaHuy

from . import che_van_ban as che, tai_nguyen
from .anh_xa_ai import AnhXaAI, LoiAnhXa, kiem_anh_xa, tao_anh_xa
from .chuan_bi_ai import ket_qua_ram, _kiem_span
from .doc_word import doc_word
from .ghi_zip import ghi_goi
from .hau_kiem_ai import _bien_thuc_the
from .ho_so_ai import json_chuan
from .kho_anh_xa_ram import _BuocRAM, _bo_tham_chieu
from .kho_dinh_danh import KhoDinhDanh
from .mo_che_ram import _don_ngoai_le
from .nguon.privacy.types import bo_ky_tu_vo_hinh
from .quyen_yeu_cau import loi_kho, loi_ram
from .tra_cuu_dinh_danh import (
    TRAN_KY_TU_DO, TRAN_UNG_VIEN, TRAN_VI_TRI, TraCuuDinhDanh, UngVien,
    chan_phat_hanh, loi as loi_ung_vien,
)
from .va_xml import bam, lap_kich_ban


_CAU = {
    'MASK_TEP_CHUA_HO_TRO': 'Tệp có nội dung chưa được hỗ trợ xử lý đầy đủ.',
    'MASK_QUA_GIOI_HAN': 'Dữ liệu vượt giới hạn xử lý. Anh hãy chia nhỏ tài liệu.',
    'MASK_DINH_DANH_CHUA_DAT': 'Chưa kiểm tra hết định danh. Không thể trả kết quả che.',
    'MASK_WORD_RAM': 'Không xác minh được dữ liệu Word trong chuỗi này. Anh hãy chạy lại toàn bộ chuỗi.',
    'MASK_KHO_CAN_CORE': 'Chưa có đủ bảo đảm của Core cho kho định danh.',
}
_LOI_RAM = frozenset(('MASK_ANH_XA_KHONG_CON', 'MASK_CHUOI_CHUA_GHIM',
    'MASK_CHUOI_DANG_XU_LY', 'MASK_BUOC_DANG_XU_LY', 'MASK_DAU_VAO_THAY_DOI',
    'MASK_VONG_DOI_KHONG_HOP_LE'))
_LOI_UNG_VIEN = frozenset(('MASK_R3_CHUA_CHUNG_MINH', 'MASK_UNG_VIEN_QUA_TRAN',
    'MASK_UNG_VIEN_QUA_HAN', 'MASK_UNG_VIEN_CHUA_DAT', 'MASK_MO_CHE_KHONG_DAY_DU'))


def _loi(ma='MASK_WORD_RAM'):
    return LoiNghiepVu(ma, _CAU[ma])


def _kiem_buoc(buoc):
    if type(buoc) is not _BuocRAM:
        raise loi_ram('MASK_ANH_XA_KHONG_CON')
    buoc.kiem()
    if buoc._loai != 'che':
        raise loi_ram('MASK_VONG_DOI_KHONG_HOP_LE')
    if buoc.du_lieu.get('loi_word'):
        raise _loi()


def _bao_ve(ham):
    """Dọn cả khi caller bắt lỗi ngay trong with; không giữ frame có gốc."""
    @wraps(ham)
    def goi(*a, **kw):
        buoc, da_so_huu = kw.get('buoc'), False
        try:
            _kiem_buoc(buoc)
            da_so_huu = True
            return ham(*a, **kw)
        except BaseException as exc:
            if da_so_huu:
                with buoc._kho._khoa:
                    bg = buoc._ban_ghi
                    if buoc._kho._ban_ghi is bg and bg.so_huu is buoc:
                        _bo_tham_chieu(bg.du_lieu)
                        bg.du_lieu['loi_word'] = True
                        buoc._cho_ai = False
                        # R4 kết thúc bản ghi khi ra with. Dọn dữ liệu ngay,
                        # giữ quyền sở hữu để R4 không đổi mã lỗi thành mất RAM.
                bg = None
            ma = getattr(exc, 'ma', None)
            if isinstance(exc, ViecDaHuy):
                loi = ViecDaHuy()
            elif isinstance(exc, ChuaRo):
                loi = ChuaRo('mask-word-' + sha256(str(exc.ma_tuong_quan).encode('utf-8')).hexdigest())
            elif isinstance(exc, LoiNghiepVu):
                if ma in _CAU:
                    loi = _loi(ma)
                elif ma in _LOI_RAM:
                    loi = loi_ram(ma)
                elif ma in _LOI_UNG_VIEN:
                    loi = loi_ung_vien(ma)
                else:
                    loi = loi_kho(ma)
            elif isinstance(exc, (che.LoiCheVanBan, LoiAnhXa)):
                loi = _loi('MASK_DINH_DANH_CHUA_DAT')
            elif isinstance(exc, Exception):
                loi = _loi()
            else:
                loi = (KeyboardInterrupt() if isinstance(exc, KeyboardInterrupt)
                       else SystemExit(1) if isinstance(exc, SystemExit) else _loi())
            _don_ngoai_le(exc)
        # Không để args chứa bytes hoặc handle trong frame lỗi của B5.
        a = kw = buoc = ma = None
        raise loi from None
    return goi


@dataclass(frozen=True, slots=True)
class DauWordRAM:
    """Chỉ băm/số đếm; không phải van_ban_da_che hay chứng cứ Local."""
    bam_goc: str
    bam_da_che: str
    so_vung: int
    so_phep_thay: int


class _KhoWord:
    """Cache ứng viên RAM chung mọi vùng; chỉ gọi kho R2 trên cache miss.

    Chuẩn hóa/nhóm/alias được ghim trong chuỗi, không đọc danh mục. Không
    giữ việc/handle ở cache. Mọi lần dùng đều kiểm lại quyền R4.
    """
    def __init__(self, buoc, ngan_sach):
        self.buoc, self.ngan_sach = buoc, ngan_sach
        self.kho = KhoDinhDanh(quyen=buoc._kho._quyen).mo_kho_nhan_dien(buoc._viec)

    def tim_ung_vien(self, nguyen_van, nhom):
        self.buoc.kiem()
        khoa = che.chuan_hoa(nguyen_van)
        cache = self.ngan_sach['da_tim']
        if khoa not in cache:
            if len(cache) >= TRAN_UNG_VIEN:
                raise loi_ung_vien('MASK_UNG_VIEN_QUA_TRAN')
            muc = self.kho.tim_ung_vien(nguyen_van, nhom)
            self.buoc.kiem()
            cache[khoa] = (nhom, muc)
        nhom_cu, muc = cache[khoa]
        if nhom_cu != nhom:
            raise loi_ung_vien()
        self.buoc.kiem()
        return muc


class _LuotVung:
    """Detector chạy riêng từng đơn vị logic, budget tính chung cả chuỗi."""
    def __init__(self, vung, kho):
        self.ma, self.kho = vung.ma, kho
        buoc = kho.buoc
        con_lai = max(0, buoc._ban_ghi.han - buoc._kho._dong_ho())
        self.luot = TraCuuDinhDanh(vung.van_ban, kho,
            han_monotonic=monotonic() + con_lai, kiem_huy=buoc.kiem)

    def kiem_han(self):
        self.luot.kiem_han()

    def tinh_chi_phi(self, so_ky_tu):
        self.kiem_han()
        if type(so_ky_tu) is not int or so_ky_tu < 0:
            raise loi_ung_vien()
        ns = self.kho.ngan_sach
        ns['ky_tu_do'] += so_ky_tu
        if ns['ky_tu_do'] > TRAN_KY_TU_DO:
            raise loi_ung_vien('MASK_UNG_VIEN_QUA_TRAN')
        self.luot.tinh_chi_phi(so_ky_tu)

    def them(self, ung_vien):
        self.kiem_han()
        if type(ung_vien) is not UngVien:
            raise loi_ung_vien()
        vi_tri = self.kho.ngan_sach['vi_tri']
        vi_tri.add((self.ma, ung_vien.bat_dau, ung_vien.ket_thuc))
        if len(vi_tri) > TRAN_VI_TRI:
            raise loi_ung_vien('MASK_UNG_VIEN_QUA_TRAN')
        self.luot.them(ung_vien)

    def ket_qua(self):
        return self.luot.ket_qua()

    def dong(self):
        self.luot.dong()
        self.kho = None


def _phep_alias(m):
    return tuple((p.goc[0], p.goc[1], m.da_che[slice(*p.dich)])
                 for p in m.goc_che if p.loai == 'thay_bi_danh') if m else ()


def _kiem_vung(goc, phep, buoc):
    """Dùng R5; xử lý báo trùng ngày ISO đúng chính sách MASK-2b.

    R5 có thể báo GIAY_TO/TAI_KHOAN bên trong một ngày đã được chính
    _cac_tien_ngay nhận diện. Chỉ miễn các khoảng số nằm trọn ngày đó;
    vẫn kiểm đủ, nguyên tiền/ngày, numeric_review và mọi nghi vấn khác.
    Không nới detector tên hoặc dùng kết quả này làm chứng cứ Local.
    """
    try:
        return ket_qua_ram(buoc._ctx.quyen.ma_yeu_cau, goc, phep, buoc=buoc)[1]
    except LoiNghiepVu as exc:
        if exc.ma != 'MASK_DINH_DANH_CHUA_DAT':
            raise
    buoc.kiem()
    m = tao_anh_xa(goc, phep)
    m.alias_nguyen_van()
    _kiem_span(m)
    tat_ca = [(goc[a:b], 'KHAC', True) for a, b, _ in phep]
    con_sot, day_du = che._kiem_con_sot(m.da_che, tat_ca)
    ngay = [(a, b) for a, b, loai, _ in che._cac_tien_ngay(m.da_che) if loai == 'ngay']
    for muc in con_sot:
        buoc.kiem()
        a, b = muc['vi_tri']['bat_dau'], muc['vi_tri']['ket_thuc']
        if (muc['nhom'] not in {'GIAY_TO', 'TAI_KHOAN'}
                or not any(x <= a < b <= y for x, y in ngay)):
            raise _loi('MASK_DINH_DANH_CHUA_DAT')
    if not day_du or not con_sot or not che._kiem_tien_ngay(goc, m.da_che):
        raise _loi('MASK_DINH_DANH_CHUA_DAT')
    so_sanh, cuoi = [], 0
    try:
        for a, b, _ in phep:
            so_sanh.extend((bo_ky_tu_vo_hinh(goc[cuoi:a]), '\x00'))
            cuoi = b
        so_sanh.append(bo_ky_tu_vo_hinh(goc[cuoi:]))
        if che.core.numeric_review(''.join(so_sanh), che._an_bi_danh(m.da_che), [])['changed']:
            raise _loi('MASK_DINH_DANH_CHUA_DAT')
    finally:
        so_sanh.clear()
    buoc.kiem()
    return m


def _gop_alias(cac_map, buoc):
    ket, da_gap = {}, {}
    for m in cac_map:
        buoc.kiem()
        if m is None:
            continue
        for alias, goc in m.alias_nguyen_van().items():
            khoa = che.chuan_bi_danh(alias)
            if khoa in da_gap and da_gap[khoa] != (alias, goc):
                raise loi_ung_vien('MASK_MO_CHE_KHONG_DAY_DU')
            da_gap[khoa] = (alias, goc)
            ket[alias] = goc
    return ket


def _ghi(tai_lieu, cac_map, buoc):
    thay = []
    try:
        for i, m in enumerate(cac_map):
            buoc.kiem()
            if m is None:
                if tai_lieu.vung[i].van_ban:
                    raise _loi()
                continue
            if m.goc != tai_lieu.vung[i].van_ban:
                raise _loi()
            for p in m.goc_che:
                if p.loai != 'giu_nguyen':
                    thay.append((i, *p.goc, m.da_che[slice(*p.dich)]))
        kich_ban = lap_kich_ban(tai_lieu, tuple(thay), kiem_huy=buoc.kiem)
        raw = ghi_goi(tai_lieu, kich_ban, kiem_huy=buoc.kiem)
        # B4 đã đọc lại; B5 vẫn kiểm trên bytes thực, không dùng preview.
        sau = doc_word(raw, kiem_huy=buoc.kiem)
        if len(sau.vung) != len(cac_map):
            raise _loi()
        for v, m in zip(sau.vung, cac_map):
            buoc.kiem()
            if v.van_ban != (m.da_che if m else ''):
                raise _loi()
        buoc.kiem()
        return raw, sau, kich_ban
    finally:
        thay.clear()


def _dau(s):
    return DauWordRAM(s['bam_goc'], s['bam_da_che'], len(s['anh_xa']),
                      len(s['kich_ban'].lenh))


def _luu_ram(buoc, s, *, ban_cu=None):
    """Điểm ghi nguyên tử với timer/hủy R4; không gọi port dưới khóa.

    Không lấy du_lieu rồi ghi sau checkpoint: timer có thể vừa clear
    dictionary đó và việc ghi sẽ dựng lại map trong bản ghi đã kết thúc.
    """
    with buoc._kho._khoa:
        buoc._kho._kiem_buoc(buoc)
        du = buoc._ban_ghi.du_lieu
        if ban_cu is None:
            if 'tep_word' in du:
                raise _loi()
            du['tep_word'] = s
        else:
            if du.get('tep_word') is not ban_cu:
                raise _loi()
            ban_cu.update(s)
            s = ban_cu
        return _dau(s)


def _doc_ram(buoc):
    s = buoc.du_lieu.get('tep_word')
    if (type(s) is not dict or s.get('phien_ban') != 1
            or s.get('giai_doan') != 'CHO_LOCAL'
            or type(s.get('goc')) is not bytes or type(s.get('da_che')) is not bytes
            or bam(s['goc']) != s.get('bam_goc') or bam(s['da_che']) != s.get('bam_da_che')):
        raise _loi()
    tai_lieu, cac_map = s.get('tai_lieu'), s.get('anh_xa')
    if (type(cac_map) is not tuple or len(cac_map) != len(tai_lieu.vung)
            or tai_lieu.bam_tep != s['bam_goc'] or tai_lieu.goi.zip.goc != s['goc']
            or s.get('vung_da_doc') != tuple(range(len(cac_map)))
            or s.get('vung_da_kiem_local') != ()):
        raise _loi()
    for v, m in zip(tai_lieu.vung, cac_map):
        buoc.kiem()
        if m is None:
            if v.van_ban:
                raise _loi()
        else:
            if type(m) is not AnhXaAI or m.goc != v.van_ban:
                raise _loi()
            kiem_anh_xa(m)
    if _gop_alias(cac_map, buoc) != s.get('alias_nguyen_van'):
        raise _loi()
    buoc.kiem()
    return s


@_bao_ve
def che_word(du_lieu, *, buoc, dinh_danh=()):
    """Lớp quy tắc → patch/map chỉ RAM; trả băm/số đếm, chưa phát hành.

    Caller B7 sở hữu handle R4 và phải nhường bằng cho_ai(). Không tạo
    kho riêng, không lấy mã yêu cầu từ caller, không upload hồ sơ/map.
    Tên mới chưa đủ bảo đảm C-P4-03 thì bị chặn bởi hậu kiểm R5.
    """
    if type(du_lieu) is not bytes:
        raise _loi('MASK_TEP_CHUA_HO_TRO')
    da_biet = che._kiem_dinh_danh(dinh_danh, la_khai_bao=True)
    bam_dinh_danh = bam(json_chuan(da_biet))
    v = buoc.du_lieu
    if 'ho_so_ai' in v or 'alias_nguyen_van' in v:
        raise loi_ram('MASK_VONG_DOI_KHONG_HOP_LE')
    if 'tep_word' in v:
        s = _doc_ram(buoc)
        if s['goc'] != du_lieu or s['bam_dinh_danh'] != bam_dinh_danh:
            raise loi_ram('MASK_DAU_VAO_THAY_DOI')
        return _dau(s)
    tai_lieu = doc_word(du_lieu, kiem_huy=buoc.kiem)
    tai_nguyen.nap_tu_goi()
    ngan_sach = dict(da_tim={}, vi_tri=set(), ky_tu_do=0)
    kho = _KhoWord(buoc, ngan_sach)
    cac_map = []
    try:
        for vung in tai_lieu.vung:
            buoc.kiem()
            goc, phep = vung.van_ban, ()
            if not goc:
                cac_map.append(None)
                continue
            if bo_ky_tu_vo_hinh(goc).strip():
                luot = _LuotVung(vung, kho)
                try:
                    phep = che.thu_thap_ung_vien(goc, da_biet, luot).phep_thay
                finally:
                    luot.dong()
            m = _kiem_vung(goc, phep, buoc)
            cac_map.append(m)
        aliases = _gop_alias(cac_map, buoc)
        raw, sau, kich_ban = _ghi(tai_lieu, cac_map, buoc)
        s = dict(phien_ban=1, giai_doan='CHO_LOCAL', goc=du_lieu, da_che=raw,
            bam_goc=bam(du_lieu), bam_da_che=bam(raw), bam_dinh_danh=bam_dinh_danh,
            tai_lieu=tai_lieu, tai_lieu_da_che=sau, anh_xa=tuple(cac_map),
            kich_ban=kich_ban, alias_nguyen_van=aliases, ngan_sach=ngan_sach,
            vung_da_doc=tuple(range(len(cac_map))), vung_da_kiem_local=())
        buoc.kiem()
        return _luu_ram(buoc, s)
    finally:
        cac_map.clear()
        kho = None


@_bao_ve
def che_them_word(cac_ung_vien, *, buoc):
    """Primitive cho B7 SAU khi kiểm nguồn/đủ đoạn/span Local.

    Nhận tuple (mã vùng, UngVien) trên GỐC, không nhận alias hay nguyên văn
    từ model. Không chứng thực Local, không đánh dấu vùng đã kiểm Local,
    không mở cửa phát hành; B7/B9 phải hậu kiểm toàn bộ chứng cứ riêng.
    """
    s = _doc_ram(buoc)
    if type(cac_ung_vien) is not tuple or len(cac_ung_vien) > TRAN_VI_TRI:
        raise loi_ung_vien('MASK_UNG_VIEN_QUA_TRAN')
    theo_vung = {}
    cac_map = list(s['anh_xa'])
    kho = _KhoWord(buoc, s['ngan_sach'])
    try:
        for muc in cac_ung_vien:
            buoc.kiem()
            if (type(muc) is not tuple or len(muc) != 2 or type(muc[0]) is not int
                    or not 0 <= muc[0] < len(cac_map) or type(muc[1]) is not UngVien
                    or muc[1].nguon != 'local'):
                raise loi_ung_vien()
            i, u = muc
            m = cac_map[i]
            a, b = u.bat_dau, u.ket_thuc
            if (m is None or type(a) is not int or type(b) is not int
                    or not 0 <= a < b <= len(m.goc)
                    or not _bien_thuc_the(m, a, b) or che._vung_tien_ngay(m.goc).hit(a, b)
                    or any(a < p.end() and p.start() < b for p in che._VUNG_BI_DANH.finditer(m.goc))):
                raise loi_ung_vien()
            da_che = _phep_alias(m)
            if any(a < y and x < b and (a, b) != (x, y) for x, y, _ in da_che):
                raise loi_ung_vien()
            if any(a < x.ket_thuc and x.bat_dau < b
                   and (a, b) != (x.bat_dau, x.ket_thuc) for x in theo_vung.get(i, ())):
                raise loi_ung_vien()
            theo_vung.setdefault(i, set()).add(u)
        for i, cac in theo_vung.items():
            buoc.kiem()
            luot = _LuotVung(s['tai_lieu'].vung[i], kho)
            try:
                for u in sorted(cac, key=lambda u: (u.bat_dau, u.ket_thuc, u.nhom)):
                    luot.them(u)
                    if luot.luot._da_tim[che.chuan_hoa(cac_map[i].goc[u.bat_dau:u.ket_thuc])][1] is None:
                        chan_phat_hanh()
                phep = set(_phep_alias(cac_map[i])) | set(luot.ket_qua().phep_thay)
                m = _kiem_vung(cac_map[i].goc, tuple(sorted(phep)), buoc)
                cac_map[i] = m
            finally:
                luot.dong()
        aliases = _gop_alias(cac_map, buoc)
        raw, sau, kich_ban = _ghi(s['tai_lieu'], cac_map, buoc)
        buoc.kiem()
        return _luu_ram(buoc, dict(da_che=raw, bam_da_che=bam(raw), tai_lieu_da_che=sau,
            anh_xa=tuple(cac_map), kich_ban=kich_ban, alias_nguyen_van=aliases), ban_cu=s)
    finally:
        theo_vung.clear()
        cac_map.clear()
        kho = None
