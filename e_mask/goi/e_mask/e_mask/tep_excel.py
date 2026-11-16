"""MASK-B6: che Excel nội bộ, không có cửa phát hành hoặc upload.

B1/B3/B4 kiểm và patch bytes; MASK-2b/R3 tìm từng ứng viên chính xác;
R4 sở hữu toàn bộ dữ liệu, R5 kiểm map/tiền/ngày. B7/B9 còn phải kiểm
nguồn Local đủ mọi vùng và quyền bàn giao. Không nhận cờ đã kiểm Local.
Nguồn/symbol/quyền/băm trước và sau được ghi trong NGUON.md.
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from functools import wraps
from hashlib import sha256
from time import monotonic

from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, ViecDaHuy

from . import che_van_ban as che, tai_nguyen
from .anh_xa_ai import AnhXaAI, LoiAnhXa, kiem_anh_xa, tao_anh_xa
from .chuan_bi_ai import ket_qua_ram, _kiem_span
from .doc_excel import ExcelDaDoc, doc_excel
from .ghi_zip import ghi_goi
from .hau_kiem_ai import _bien_thuc_the
from .ho_so_ai import json_chuan
from .kho_anh_xa_ram import _BuocRAM, _bo_tham_chieu
from .kho_dinh_danh import KhoDinhDanh
from .khoi_tao_ngan import PHIEN_BAN_CHUAN_HOA
from .mo_che_ram import _don_ngoai_le
from .nguon.privacy.types import bo_ky_tu_vo_hinh
from .quyen_yeu_cau import loi_kho, loi_ram
from .tra_cuu_dinh_danh import (
    TRAN_KY_TU_DO, TRAN_UNG_VIEN, TRAN_VI_TRI, TraCuuDinhDanh, UngVien,
    chan_phat_hanh, loi as loi_ung_vien,
)
from .va_xml import bam, lap_kich_ban, _goc_vung


_CAU = {
    'MASK_TEP_CHUA_HO_TRO': 'Tệp có nội dung chưa được hỗ trợ xử lý đầy đủ.',
    'MASK_QUA_GIOI_HAN': 'Dữ liệu vượt giới hạn xử lý. Anh hãy chia nhỏ tài liệu.',
    'MASK_DINH_DANH_CHUA_DAT': 'Chưa kiểm tra hết định danh. Không thể trả kết quả che.',
    'MASK_EXCEL_RAM': 'Không xác minh được dữ liệu Excel trong chuỗi này. Anh hãy chạy lại toàn bộ chuỗi.',
    'MASK_KHO_CAN_CORE': 'Chưa có đủ bảo đảm của Core cho kho định danh.',
}
_LOI_RAM = frozenset(('MASK_ANH_XA_KHONG_CON', 'MASK_CHUOI_CHUA_GHIM',
    'MASK_CHUOI_DANG_XU_LY', 'MASK_BUOC_DANG_XU_LY', 'MASK_DAU_VAO_THAY_DOI',
    'MASK_VONG_DOI_KHONG_HOP_LE'))
_LOI_UNG_VIEN = frozenset(('MASK_R3_CHUA_CHUNG_MINH', 'MASK_UNG_VIEN_QUA_TRAN',
    'MASK_UNG_VIEN_QUA_HAN', 'MASK_UNG_VIEN_CHUA_DAT', 'MASK_MO_CHE_KHONG_DAY_DU'))


def _loi(ma='MASK_EXCEL_RAM'):
    return LoiNghiepVu(ma, _CAU[ma])


def _kiem_buoc(buoc):
    if type(buoc) is not _BuocRAM:
        raise loi_ram('MASK_ANH_XA_KHONG_CON')
    buoc.kiem()
    if buoc._loai != 'che':
        raise loi_ram('MASK_VONG_DOI_KHONG_HOP_LE')
    if buoc.du_lieu.get('loi_excel'):
        raise _loi()


def _bao_ve(ham):
    """Dọn cả khi caller bắt lỗi ngay trong with; không giữ frame có gốc."""
    @wraps(ham)
    def goi(*a, **kw):
        buoc, da_so_huu = kw.get('buoc'), False
        luot = None
        try:
            _kiem_buoc(buoc)
            da_so_huu = True
            # Phạm vi gom chỉ trong primitive Excel; không đổi handle R4
            # dùng chung hoặc giữ quyền đã xác minh qua lượt sau.
            luot = kw['buoc'] = _BuocExcel(buoc)
            ket = ham(*a, **kw)
            buoc.kiem()  # Không trả kết quả tính bằng scope đã bị thu hồi.
            return ket
        except BaseException as exc:
            if da_so_huu:
                with buoc._kho._khoa:
                    bg = buoc._ban_ghi
                    if buoc._kho._ban_ghi is bg and bg.so_huu is buoc:
                        _bo_tham_chieu(bg.du_lieu)
                        bg.du_lieu['loi_excel'] = True
                        buoc._cho_ai = False
                        # R4 kết thúc bản ghi khi ra with. Dọn dữ liệu ngay,
                        # giữ quyền sở hữu để R4 không đổi mã lỗi thành mất RAM.
                bg = None
            ma = getattr(exc, 'ma', None)
            if isinstance(exc, ViecDaHuy):
                loi = ViecDaHuy()
            elif isinstance(exc, ChuaRo):
                loi = ChuaRo('mask-excel-' + sha256(str(exc.ma_tuong_quan).encode('utf-8')).hexdigest())
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
        finally:
            if luot is not None:
                luot.doc_excel_cache.clear()
                luot.goc = None
        # Không để args chứa bytes hoặc handle trong frame lỗi của B6.
        a = kw = buoc = ma = None
        raise loi from None
    return goi


class _BuocExcel:
    """Checkpoint cục bộ mỗi 64 callback/10 ms, Core mỗi khối/50 ms.

    Hủy/TTL/timer/lease từ lifecycle R4 kiểm tại checkpoint cục bộ.
    Scope Core kiểm lại tối đa 4096 callback hoặc 50 ms, cùng các ranh
    giới đọc kho và bàn giao. Không nới hạn hoặc cache quyền qua lượt.
    """
    def __init__(self, buoc):
        self.goc = buoc
        self.doc_excel_cache = {}
        self._lan, self._luc = 0, monotonic()
        self._cuc_bo = self._luc

    def __getattr__(self, ten):
        return getattr(self.goc, ten)

    def kiem(self):
        self._lan += 1
        luc = monotonic()
        if self._lan >= 4096 or luc - self._luc >= .05:
            self.xac_minh()
        elif self._lan % 64 == 0 or luc - self._cuc_bo >= .01:
            b = self.goc
            b._viec.kiem_huy()
            with b._kho._khoa:
                b._kho._kiem_buoc(b)
            self._cuc_bo = luc

    def xac_minh(self):
        self.goc.kiem()
        self._lan, self._luc = 0, monotonic()
        self._cuc_bo = self._luc

    @property
    def du_lieu(self):
        self.kiem()
        return self.goc._ban_ghi.du_lieu


@dataclass(frozen=True, slots=True)
class DauExcelRAM:
    """Chỉ băm/số đếm; không phải van_ban_da_che hay chứng cứ Local."""
    bam_goc: str
    bam_da_che: str
    so_vung: int
    so_phep_thay: int


class _KhoExcel:
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
    def __init__(self, vi, vung, kho):
        # Mã loại o/core/app có thể lặp; budget đếm theo chỉ số vùng.
        self.ma, self.kho = vi, kho
        buoc = kho.buoc
        con_lai = max(0, buoc._ban_ghi.han - buoc._kho._dong_ho())
        self.luot = TraCuuDinhDanh(vung.chu, kho,
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


_FORMAT_SAN = {
    5: '"$"#,##0_);("$"#,##0)', 6: '"$"#,##0_);[Red]("$"#,##0)',
    7: '"$"#,##0.00_);("$"#,##0.00)', 8: '"$"#,##0.00_);[Red]("$"#,##0.00)',
    14: 'mm-dd-yy', 15: 'd-mmm-yy', 16: 'd-mmm', 17: 'mmm-yy',
    18: 'h:mm AM/PM', 19: 'h:mm:ss AM/PM', 20: 'h:mm', 21: 'h:mm:ss',
    22: 'm/d/yy h:mm',
    41: '_(* #,##0_);_(* (#,##0);_(* "-"_);_(@_)',
    42: '_("$"* #,##0_);_("$"* (#,##0);_("$"* "-"_);_(@_)',
    43: '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)',
    44: '_("$"* #,##0.00_);_("$"* (#,##0.00);_("$"* "-"??_);_(@_)',
    45: 'mm:ss', 46: '[h]:mm:ss', 47: 'mmss.0',
}
_FORMAT_NGAY = frozenset((
    'dd/mm/yyyy', 'yyyy-mm-dd', 'dd/mm/yyyy hh:mm', 'yyyy-mm-dd hh:mm:ss',
    'hh:mm', 'hh:mm:ss', *(_FORMAT_SAN[i] for i in (*range(14, 23), 45, 46, 47)),
))
_FORMAT_TIEN = frozenset((
    '#,##0" VND"', '#,##0 "VND"', '#,##0.00" VND"', '#,##0 [$VND-42A]',
    *(_FORMAT_SAN[i] for i in (*range(5, 9), *range(41, 45))),
))


def _format_so(style):
    # B3 đã gắn formatCode khai báo vào style hiệu lực (hoặc từ chối khai
    # lại ID builtin). Chỉ dùng mặc định builtin khi không có khai báo.
    code = style.get('formatCode')
    return code if code is not None else _FORMAT_SAN.get(int(style.get('numFmtId', '0')), 'General')


def _kiem_so_bat_bien(tai_lieu, buoc):
    """Ô số/metadata không có miền sửa chữ: cần che thì chặn cả tệp.

    Không biến MST/tài khoản dạng số thành chuỗi để đặt alias. Ô tiền có
    phần lẻ khác 0 hoặc tối đa 12 chữ số nguyên được giữ theo lead 16/11.
    Chỉ serial ngày trong miền hợp lệ được miễn. Khai
    báo số làm định danh đã bị lớp kiểm đầu vào từ chối. B7 kiểm Local đúng
    ngữ cảnh cho cả các ô/thuộc tính bất biến này, không tự chứng nhận.
    """
    da_kiem = set()
    def kiem(chu):
        buoc.kiem()
        if chu in da_kiem:
            return
        con_sot, day_du = che._kiem_con_sot(chu, [])
        if con_sot or not day_du:
            raise _loi('MASK_TEP_CHUA_HO_TRO')
        da_kiem.add(chu)

    da_tim = set()
    def kiem_da_khai(*gia_tri):
        # Tra đúng giá trị qua ngăn bí mật, không dò hình dạng định danh,
        # không đọc bản rõ/danh mục. Phạm vi lấy từ quyền R4 đã xác minh.
        for chu in gia_tri:
            buoc.kiem()
            khoa = che.chuan_hoa(chu)
            if khoa in da_tim:
                continue
            if len(da_tim) >= TRAN_UNG_VIEN:
                raise loi_ung_vien('MASK_UNG_VIEN_QUA_TRAN')
            trang = buoc._viec.ngan.tim('dinh_danh', loc={
                'gia_tri_chuan': khoa, 'vung_du_lieu': buoc._ctx.quyen.vung,
                'phien_ban_chuan_hoa': PHIEN_BAN_CHUAN_HOA}, gioi_han=2)
            buoc.kiem()
            if trang.danh_sach or trang.tiep is not None:
                raise _loi('MASK_TEP_CHUA_HO_TRO')
            da_tim.add(khoa)

    for o in tai_lieu.o:
        buoc.kiem()
        if o.vung is None and o.gia_tri is not None and o.kieu in (None, 'n'):
            code = _format_so(tai_lieu.styles[o.style_hieu_luc])
            so = Decimal(o.gia_tri)
            if code in _FORMAT_NGAY:
                # Epoch 1900 có ngày nhuận giả của Excel trước tháng 3;
                # cận trên là 01/01/2101, không nhận phần giờ của ngày đó.
                epoch = date(1904, 1, 1) if tai_lieu.epoch1904 else date(1899, 12, 30)
                duoi = 0 if tai_lieu.epoch1904 else 1
                tren = (date(2101, 1, 1) - epoch).days
                if not duoi <= so < tren:
                    raise _loi('MASK_TEP_CHUA_HO_TRO')
                kiem_da_khai(o.gia_tri)
                continue
            # Chuẩn hóa chỉ để kiểm trong RAM: chặn định danh giấu bằng
            # exponent/.0/dấu; không sửa lexical hoặc bytes của ô nguồn.
            if not -128 <= so.as_tuple().exponent <= 308:
                raise _loi('MASK_TEP_CHUA_HO_TRO')
            chuan = format(so.copy_abs(), 'f')
            nguyen = chuan.partition('.')[0]
            la_nguyen = so == so.to_integral_value()
            if code in _FORMAT_TIEN and (not la_nguyen or len(nguyen) <= 12):
                # .00/exponent/dấu được xét theo giá trị, không số ký tự
                # lexical. Khai báo định danh vẫn thắng format tiền.
                chuan_gon = nguyen if la_nguyen else chuan.rstrip('0')
                kiem_da_khai(o.gia_tri, chuan_gon,
                             '-' + chuan_gon if so < 0 else chuan_gon)
                continue
            if la_nguyen and len(nguyen) >= 9:
                raise _loi('MASK_TEP_CHUA_HO_TRO')
            kiem(o.gia_tri)
            kiem(chuan)
    # Thuộc tính có kiểu số không nằm trong các vùng chuỗi có thể patch.
    root = tai_lieu.goi.goi.cay.get('docProps/custom.xml')
    if root is not None:
        for e in root:
            buoc.kiem()
            v = e[0]
            if v.tag.rsplit('}', 1)[-1] in {
                    'i1', 'i2', 'i4', 'i8', 'int', 'ui1', 'ui2', 'ui4', 'ui8',
                    'uint', 'r4', 'r8', 'decimal'}:
                kiem(v.text)
    buoc.kiem()


def _gop_alias(cac_map, buoc):
    ket, da_gap, da_kiem = {}, {}, set()
    for m in cac_map:
        buoc.kiem()
        if m is None or id(m) in da_kiem:
            continue
        da_kiem.add(id(m))
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
            goc = _goc_vung(tai_lieu, i)
            if goc != i:
                # Shared chỉ patch một lần, mọi ô phải có cùng map.
                if m != cac_map[goc]:
                    raise _loi()
                continue
            if m is None:
                if tai_lieu.vung[i].chu:
                    raise _loi()
                continue
            if m.goc != tai_lieu.vung[i].chu:
                raise _loi()
            for p in m.goc_che:
                if p.loai != 'giu_nguyen':
                    thay.append((i, *p.goc, m.da_che[slice(*p.dich)]))
        kich_ban = lap_kich_ban(tai_lieu, tuple(thay), kiem_huy=buoc.kiem)
        raw = ghi_goi(tai_lieu, kich_ban, kiem_huy=buoc.kiem)
        # B4 đã đọc lại; B6 vẫn kiểm trên bytes thực, không dùng preview.
        sau = doc_excel(raw, kiem_huy=buoc.kiem)
        if (len(sau.vung) != len(cac_map)
                or (tai_lieu.shared, tai_lieu.tham_chieu_chu, tai_lieu.styles,
                    tai_lieu.gop_o, tai_lieu.epoch1904)
                != (sau.shared, sau.tham_chieu_chu, sau.styles,
                    sau.gop_o, sau.epoch1904) or len(tai_lieu.o) != len(sau.o)):
            raise _loi()
        for v, cu, m in zip(sau.vung, tai_lieu.vung, cac_map):
            buoc.kiem()
            if (v.chu != (m.da_che if m else '')
                    or (v.ma, v.so_sheet, v.o, v.chi_so_chu, v.duoc_sua)
                    != (cu.ma, cu.so_sheet, cu.o, cu.chi_so_chu, cu.duoc_sua)):
                raise _loi()
        for cu, moi in zip(tai_lieu.o, sau.o):
            buoc.kiem()
            # Shared <v> là index; giữ lexical/kiểu số/ngày và style.
            if ((cu.so_sheet, cu.dia_chi, cu.kieu, cu.gia_tri, cu.style,
                 cu.style_goc, cu.style_hang, cu.style_cot, cu.style_hieu_luc,
                 cu.chi_so_chu, cu.vung, cu.hang_an, cu.cot_an)
                    != (moi.so_sheet, moi.dia_chi, moi.kieu, moi.gia_tri, moi.style,
                        moi.style_goc, moi.style_hang, moi.style_cot, moi.style_hieu_luc,
                        moi.chi_so_chu, moi.vung, moi.hang_an, moi.cot_an)
                    or (cu.vung is None or cu.chi_so_chu is not None)
                    and cu.xml_goc != moi.xml_goc):
                raise _loi()
        buoc.kiem()
        return raw, sau, kich_ban
    finally:
        thay.clear()


def _dau(s):
    return DauExcelRAM(s['bam_goc'], s['bam_da_che'], len(s['anh_xa']),
                      len(s['kich_ban'].lenh))


def _luu_ram(buoc, s, *, ban_cu=None):
    """Điểm ghi nguyên tử với timer/hủy R4; không gọi port dưới khóa.

    Không lấy du_lieu rồi ghi sau checkpoint: timer có thể vừa clear
    dictionary đó và việc ghi sẽ dựng lại map trong bản ghi đã kết thúc.
    """
    if isinstance(buoc, _BuocExcel):
        buoc.xac_minh()
        buoc = buoc.goc
    with buoc._kho._khoa:
        buoc._kho._kiem_buoc(buoc)
        du = buoc._ban_ghi.du_lieu
        if ban_cu is None:
            if 'tep_excel' in du:
                raise _loi()
            du['tep_excel'] = s
        else:
            if du.get('tep_excel') is not ban_cu:
                raise _loi()
            ban_cu.update(s)
            s = ban_cu
        return _dau(s)


def _doc_ram(buoc):
    s = buoc.du_lieu.get('tep_excel')
    if (type(s) is not dict or s.get('phien_ban') != 1
            or s.get('giai_doan') != 'CHO_LOCAL'
            or type(s.get('goc')) is not bytes or type(s.get('da_che')) is not bytes
            or bam(s['goc']) != s.get('bam_goc') or bam(s['da_che']) != s.get('bam_da_che')):
        raise _loi()
    tai_lieu, cac_map = s.get('tai_lieu'), s.get('anh_xa')
    if (type(tai_lieu) is not ExcelDaDoc or type(cac_map) is not tuple
            or len(cac_map) != len(tai_lieu.vung)
            or tai_lieu.bam_tep != s['bam_goc'] or tai_lieu.goi.goi.zip.goc != s['goc']
            or s.get('vung_da_doc') != tuple(range(len(cac_map)))
            or s.get('vung_da_kiem_local') != ()):
        raise _loi()
    for v, m in zip(tai_lieu.vung, cac_map):
        buoc.kiem()
        if m is None:
            if v.chu:
                raise _loi()
        else:
            if type(m) is not AnhXaAI or m.goc != v.chu:
                raise _loi()
            kiem_anh_xa(m)
    for i, m in enumerate(cac_map):
        buoc.kiem()
        if m != cac_map[_goc_vung(tai_lieu, i)]:
            raise _loi()
    if _gop_alias(cac_map, buoc) != s.get('alias_nguyen_van'):
        raise _loi()
    buoc.kiem()
    return s


@_bao_ve
def che_excel(du_lieu, *, buoc, dinh_danh=()):
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
    if 'ho_so_ai' in v or 'alias_nguyen_van' in v or 'tep_word' in v:
        raise loi_ram('MASK_VONG_DOI_KHONG_HOP_LE')
    if 'tep_excel' in v:
        s = _doc_ram(buoc)
        if s['goc'] != du_lieu or s['bam_dinh_danh'] != bam_dinh_danh:
            raise loi_ram('MASK_DAU_VAO_THAY_DOI')
        return _dau(s)
    tai_lieu = doc_excel(du_lieu, kiem_huy=buoc.kiem)
    tai_nguyen.nap_tu_goi()
    _kiem_so_bat_bien(tai_lieu, buoc)
    ngan_sach = dict(da_tim={}, vi_tri=set(), ky_tu_do=0)
    kho = _KhoExcel(buoc, ngan_sach)
    cac_map = []
    da_kiem = {}
    try:
        for i, vung in enumerate(tai_lieu.vung):
            buoc.kiem()
            goc_vung = _goc_vung(tai_lieu, i)
            if goc_vung != i:
                if vung.chu != tai_lieu.vung[goc_vung].chu:
                    raise _loi()
                cac_map.append(cac_map[goc_vung])
                continue
            goc, phep = vung.chu, ()
            if not goc:
                cac_map.append(None)
                continue
            if goc in da_kiem:
                m, chi_phi, vi_tri = da_kiem[goc]
                # Không giảm budget vì cache: từng vị trí vẫn thuộc ô
                # riêng; thứ tự cấp/ghim alias không thay đổi.
                ngan_sach['ky_tu_do'] += chi_phi
                ngan_sach['vi_tri'].update((i, a, b) for a, b in vi_tri)
                if (ngan_sach['ky_tu_do'] > TRAN_KY_TU_DO
                        or len(ngan_sach['vi_tri']) > TRAN_VI_TRI):
                    raise loi_ung_vien('MASK_UNG_VIEN_QUA_TRAN')
                vung.kiem_thay_the(m.da_che)
                cac_map.append(m)
                continue
            chi_phi = ngan_sach['ky_tu_do']
            vi_tri = ()
            if bo_ky_tu_vo_hinh(goc).strip():
                luot = _LuotVung(i, vung, kho)
                try:
                    phep = che.thu_thap_ung_vien(goc, da_biet, luot).phep_thay
                    vi_tri = tuple(luot.luot._vi_tri)
                finally:
                    luot.dong()
            m = _kiem_vung(goc, phep, buoc)
            vung.kiem_thay_the(m.da_che)
            cac_map.append(m)
            da_kiem[goc] = (m, ngan_sach['ky_tu_do'] - chi_phi, vi_tri)
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
        da_kiem.clear()
        cac_map.clear()
        kho = None


@_bao_ve
def che_them_excel(cac_ung_vien, *, buoc):
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
    kho = _KhoExcel(buoc, s['ngan_sach'])
    try:
        for muc in cac_ung_vien:
            buoc.kiem()
            if (type(muc) is not tuple or len(muc) != 2 or type(muc[0]) is not int
                    or not 0 <= muc[0] < len(cac_map) or type(muc[1]) is not UngVien
                    or muc[1].nguon != 'local'):
                raise loi_ung_vien()
            i, u = muc
            i = _goc_vung(s['tai_lieu'], i)
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
            luot = _LuotVung(i, s['tai_lieu'].vung[i], kho)
            try:
                for u in sorted(cac, key=lambda u: (u.bat_dau, u.ket_thuc, u.nhom)):
                    luot.them(u)
                    if luot.luot._da_tim[che.chuan_hoa(cac_map[i].goc[u.bat_dau:u.ket_thuc])][1] is None:
                        chan_phat_hanh()
                phep = set(_phep_alias(cac_map[i])) | set(luot.ket_qua().phep_thay)
                m = _kiem_vung(cac_map[i].goc, tuple(sorted(phep)), buoc)
                s['tai_lieu'].vung[i].kiem_thay_the(m.da_che)
                cac_map[i] = m
            finally:
                luot.dong()
        for i in range(len(cac_map)):
            buoc.kiem()
            cac_map[i] = cac_map[_goc_vung(s['tai_lieu'], i)]
        aliases = _gop_alias(cac_map, buoc)
        raw, sau, kich_ban = _ghi(s['tai_lieu'], cac_map, buoc)
        buoc.kiem()
        return _luu_ram(buoc, dict(da_che=raw, bam_da_che=bam(raw), tai_lieu_da_che=sau,
            anh_xa=tuple(cac_map), kich_ban=kich_ban, alias_nguyen_van=aliases), ban_cu=s)
    finally:
        theo_vung.clear()
        cac_map.clear()
        kho = None
