"""MASK-2: xử lý thuần trong RAM; kho do phía tin cậy tiêm, không đọc/ghi dữ liệu.

Đây là giao diện nội bộ, chưa phải contract/API Core. Kho chịu trách nhiệm xác
minh phiên, module, người gửi, tài liệu và vùng DEMO/thật; không lấy từ văn bản.
Kết quả bị chặn không công bố văn bản chưa kiểm đạt (giá trị là None).
"""
from __future__ import annotations

from bisect import bisect_right
from collections import Counter
from contextlib import AbstractContextManager
from dataclasses import dataclass
import re
from typing import Protocol
import unicodedata

from .nguon.privacy import core, detectors, leftovers
from .nguon.privacy.types import bo_ky_tu_vo_hinh, chuan_hoa_vi_tri
from .tai_nguyen import ThieuTaiNguyen
from . import ten_nguoi
from .anh_xa_ai import tao_anh_xa, kiem_anh_xa
from .tra_cuu_dinh_danh import (TraCuuDinhDanh, UngVien, TRAN_VI_TRI,
                               chan_phat_hanh, loi as loi_ung_vien)


class LoiCheVanBan(ValueError):
    """Thông báo nghiệp vụ cố định, không đính kèm đầu vào/lỗi kho."""


class Kho(Protocol):
    """Protocol RAM lịch sử, chỉ giữ hồi quy trước R4/R5/R6.

    Tra cứu dùng giá trị NFC/lower/gộp khoảng trắng, chung toàn tập đoàn nhưng
    tách DEMO/thật. doc_yeu_cau phải từ chối sai module/người gửi/vùng/đã đóng.
    Giao dịch rollback cả mã yêu cầu, hàng chờ, tham chiếu, đếm và dấu chống lặp.
    Kho ở lát sau phải xác minh qua cổng Core, không tin dữ liệu caller.
    """

    def giao_dich(self) -> AbstractContextManager: ...
    def liet_ke_dinh_danh(self) -> list[dict]: ...
    def tra_bi_danh(self, gia_tri_chuan: str) -> dict | None: ...
    def cap_bi_danh_tam(self) -> str: ...
    def ghi_cho_duyet(self, gia_tri: str, nhom: str, bi_danh: str,
                     ma_yeu_cau: str) -> tuple[dict, bool]: ...
    def ghi_nhan_gap_lai(self, ma_yeu_cau: str, cum_chuan: str, nhom: str) -> None:
        """Tính cả lần đầu của cụm tạm; nguyên tử, mỗi yêu cầu + cụm chỉ một lần."""
        ...
    def tao_yeu_cau(self) -> str: ...
    def doc_yeu_cau(self, ma_yeu_cau: str) -> dict: ...
    def ghi_bi_danh_da_dung(self, ma_yeu_cau: str, bi_danh: list[str]) -> None: ...
    def tra_dinh_danh(self, bi_danh_chuan: str) -> str | None: ...
    def dong_yeu_cau(self, ma_yeu_cau: str) -> None: ...


_KHOANG_TRANG = re.compile(
    r'[\u0009-\u000d\u001c-\u0020\u0085\u00a0\u1680\u2000-\u200a'
    r'\u2028\u2029\u202f\u205f\u3000]+'
)
_BI_DANH = re.compile(r'\[\[[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\]\]')
_MA_ROI = r'[A-Za-z0-9?][A-Za-z0-9?_.\s-]{0,399}'
# Kể cả dấu ngoặc bị tách, xuống dòng và bí danh bị thiếu ngoặc đóng.
_VUNG_BI_DANH = re.compile(
    r'\[\s*\[[^\[\]]*(?:\]\s*\]|(?=[\[\]])|$)'
    r'|(?<!\[)\[(?!\s*\[)[^\[\]\r\n]*\]'
    rf'|(?<![\w\[]){_MA_ROI}\]\s*\]'
    rf'|(?<!\[)\[(?!\s*\[)\s*{_MA_ROI}(?:\s*\])?'
    rf'|(?<![\w\[]){_MA_ROI}\s*\]'
)
_GIA_TRI_SO = r'[-+]?(?:\d[\d.,]{0,298}\d|\d)'
_GIA_TRI_TIEN = r'[-+]?(?:\d[\d., \u00a0]{0,298}\d|\d)'
_SO = re.compile(rf'(?<![\w.,]){_GIA_TRI_SO}(?![\w.,])')
_DANG_TIEN = re.compile(r'\d[\d.,]{0,298}[.,]\d{1,3}')
_DANG_SO_KHAI = re.compile(r'[\d\W_]{2,300}')
_DON_VI_TIEN = r'(?:VND|VNĐ|USD|EUR|đồng|đ|₫|\$)'
_TIEN_KY_HIEU = re.compile(
    rf'(?<![\w.,]){_DON_VI_TIEN}[^\S\r\n]{{0,20}}[:：]?[^\S\r\n]{{0,20}}(?P<so_truoc>{_GIA_TRI_TIEN})(?![\w.,])'
    rf'|(?<![\w.,])(?P<so_sau>{_GIA_TRI_TIEN})[^\S\r\n]{{0,20}}{_DON_VI_TIEN}(?!\w)', re.I
)
_NGAY_SO = re.compile(
    r'(?<!\d)(?:\d{4}[/.-]\d{1,2}[/.-]\d{1,2}|\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})(?!\d)'
)
_NGAY_CHU = re.compile(
    r'(?<!\w)(?:ngày[^\S\r\n]{1,8})?(?:0?[1-9]|[12]\d|3[01])'
    r'[^\S\r\n]{1,8}tháng[^\S\r\n]{1,8}(?:0?[1-9]|1[0-2])'
    r'(?:[^\S\r\n]{1,8}năm[^\S\r\n]{1,8}\d{2,4})?(?!\w)', re.I
)
_NHAN_TRUONG = re.compile(
    r'(?<!\w)(?:(?P<CA_NHAN>họ\s+(?:và\s+)?tên|ông(?:\s*/\s*bà)?|bà)'
    r'|(?P<DIA_CHI>địa\s+chỉ)|(?P<MA_SO_THUE>MST|mã\s+số\s+thuế)'
    r'|(?P<GIAY_TO>CCCD|CMND)|(?P<TAI_KHOAN>(?:số\s+)?tài\s+khoản|STK|TK|A/C)'
    r'|(?P<DIEN_THOAI>điện\s+thoại|ĐT|SĐT|phone|tel)'
    r'|(?P<EMAIL>e-?mail))(?!\w)[^\S\r\n]*(?:[:：=][^\S\r\n]*)?', re.I
)
_NGAT_TRUONG = re.compile(
    r'\n[^\S\r\n]*\r?\n|[\t;|]|^[^\S\r\n]*[^\W\d_][^\r\n:：=]{0,59}[:：=]', re.M
)
_CONG_TY = re.compile(r'(?<!\w)công[^\S\r\n]+ty(?!\w)[^\S\r\n]+[^\x00\r\n\t;|\[\]]+', re.I)
_MST = re.compile(r'(?<!\w)\d(?:[ .-]?\d){9}(?:(?:[ .-]?\d){3})?(?!\w|[ .-]?\d)')
_GIAY_TO = re.compile(r'(?<![\w.,])(?:\d{12}|\d{9})(?![\w.,])')
_DIEN_THOAI_VN = re.compile(
    r'(?<![\w+])(?:(?:\+84[ .-]?|0)[35789](?:[ .-]?\d){8}'
    r'|(?:\+84[ .-]?2\d{1,2}|02\d{1,2}|\(0?2\d{1,2}\))(?:[ .-]?\d){7,8})(?!\w)'
)
_EMAIL = re.compile(r'(?<![\w.+-])[\w.+-]{1,64}@[\w.-]{1,253}\.[\w-]{2,63}(?![\w.-])')
_KHOI_DAI = re.compile(r'[^\s\x00]{1025,}')
_DAU_TIEN_NGAY = re.compile(r'[^\W\d_]|[$₫]|(?<=\d)(?:[.,]+|[/-])(?=\d)')
_SO_VAN_BAN = re.compile(r'(?<!\w)số[^\S\r\n]+(?P<so>\d{1,6}/\d{4})(?![\w/.-])', re.I)


class _ViTriGiuNguyen:
    def __getitem__(self, i):
        return i, i + 1


def _tim_tuyen_tinh(chu, mau):
    """KMP: trả cả lần khớp chồng nhau mà không thử lại cả cụm dài."""
    tien_to = [0] * len(mau)
    j = 0
    for i in range(1, len(mau)):
        while j and mau[i] != mau[j]:
            j = tien_to[j - 1]
        if mau[i] == mau[j]:
            j += 1
        tien_to[i] = j
    j = 0
    for i, c in enumerate(chu):
        while j and c != mau[j]:
            j = tien_to[j - 1]
        if c == mau[j]:
            j += 1
        if j == len(mau):
            yield i - j + 1
            j = tien_to[j - 1]


class _BoDo(core.KnownText):
    """Giữ matcher nguồn; cụm số dài dùng quét tuyến tính thay regex sinh."""

    def spans(self, value, loose=True, boundary=True, masking=False):
        if (len(value) <= 300 or not value[0].isdecimal() or not value[-1].isdecimal()
                or not core.NUMERIC_ID.fullmatch(value)):
            return super().spans(value, loose, boundary, masking)
        mau_so = core.skeleton(value) if loose else ''
        loose = loose and len(mau_so) >= core.KNOWN_MIN
        if not hasattr(self, '_loi_khoang'):
            loi = [0] * len(self.positions)
            for i in range(1, len(self.positions)):
                a, b = self.positions[i - 1], self.positions[i]
                loi[i] = loi[i - 1] + (b - a - 1 > core.KNOWN_GAP
                                       or any(not core._gap(c) for c in self.text[a + 1:b]))
            self._loi_khoang = loi
        # Khi mọi khoảng ngăn hợp lệ, lần khớp đúng chữ đã nằm trong tập loose.
        can_dung_chu = not loose or boundary or masking or (self._loi_khoang and self._loi_khoang[-1])
        dung_chu = set()
        if can_dung_chu:
            if not hasattr(self, '_chu_gop_trang'):
                phan, vi_tri, trang_truoc = [], [], False
                for i, c in enumerate(self.text):
                    trang = c.isspace()
                    if not trang or not trang_truoc:
                        phan.append(' ' if trang else c)
                        vi_tri.append(i)
                    trang_truoc = trang
                self._chu_gop_trang, self._vi_tri_gop_trang = ''.join(phan), vi_tri
            mau = ' '.join(value.split())
            cuoi = 0
            for i in _tim_tuyen_tinh(self._chu_gop_trang, mau):
                if i < cuoi:
                    continue  # Cùng quy tắc finditer: lần khớp đúng chữ không chồng nhau.
                a, b = self._vi_tri_gop_trang[i], self._vi_tri_gop_trang[i + len(mau) - 1] + 1
                if ((a and core._word(self.text[a - 1]))
                        or (b < len(self.text) and core._word(self.text[b]))):
                    continue
                dung_chu.add((a, b))
                cuoi = i + len(mau)
        vung = []
        if loose:
            for i in _tim_tuyen_tinh(self.folded, mau_so):
                j = i + len(mau_so) - 1
                if self._loi_khoang[i] != self._loi_khoang[j]:
                    continue
                a, b = self.positions[i], self.positions[j] + 1
                if boundary and not self._edges(a, b):
                    continue
                if masking and (a, b) not in dung_chu and self._money_or_date(a, b, value):
                    continue
                if vung and a < vung[-1][1]:
                    vung[-1] = (vung[-1][0], max(vung[-1][1], b))
                else:
                    vung.append((a, b))
        gop = []
        for a, b in sorted(dung_chu.union(vung)):
            if gop and a < gop[-1][1]:
                gop[-1] = (gop[-1][0], max(gop[-1][1], b))
            else:
                gop.append((a, b))
        return gop


def chuan_hoa(gia_tri: str) -> str:
    """Cùng quy tắc mask.chuan_hoa của migration 113, không bỏ dấu tiếng Việt."""
    return _KHOANG_TRANG.sub(' ', unicodedata.normalize('NFC', bo_ky_tu_vo_hinh(gia_tri))).strip(' ').lower()


def chuan_bi_danh(bi_danh: str) -> str:
    return ''.join(bi_danh.split()).lower()


def _kiem_van_ban(van_ban, *, cho_rong=False):
    if not isinstance(van_ban, str):
        raise LoiCheVanBan('Nội dung văn bản chưa hợp lệ.')
    if len(van_ban) > 500_000:
        raise LoiCheVanBan('Văn bản vượt giới hạn 500.000 ký tự.')
    if not cho_rong and not bo_ky_tu_vo_hinh(van_ban).strip():
        raise LoiCheVanBan('Cần nhập nội dung văn bản.')


def _kiem_dinh_danh(danh_sach, *, tien_ngay=frozenset(), la_khai_bao=False):
    if not isinstance(danh_sach, (list, tuple)) or len(danh_sach) > 500:
        raise LoiCheVanBan('Danh sách định danh cần có tối đa 500 mục.')
    ket_qua, da_co = [], {}
    for muc in danh_sach:
        if not isinstance(muc, dict):
            raise LoiCheVanBan('Danh sách định danh chưa hợp lệ.')
        gia_tri, nhom = muc.get('gia_tri'), muc.get('nhom', 'KHAC')
        if isinstance(gia_tri, str) and len(gia_tri) <= 300:
            gia_tri = bo_ky_tu_vo_hinh(gia_tri)
        if (not isinstance(gia_tri, str) or not 2 <= len(gia_tri) <= 300
                or not chuan_hoa(gia_tri) or '[' in gia_tri or ']' in gia_tri
                or any(unicodedata.category(c).startswith('C') and not c.isspace() for c in gia_tri)
                or not isinstance(nhom, str) or not 1 <= len(nhom) <= 20
                or nhom not in core.CATEGORIES):
            raise LoiCheVanBan('Giá trị định danh cần 2–300 ký tự và nhóm hợp lệ tối đa 20 ký tự.')
        if (_cac_tien_ngay(gia_tri) or chuan_hoa(gia_tri) in tien_ngay
                or (la_khai_bao and _DANG_SO_KHAI.fullmatch(gia_tri)
                    and any(c.isdigit() for c in gia_tri))):
            raise LoiCheVanBan('Định danh đã biết không được chứa số tiền hoặc ngày. Cần kiểm tra lại danh sách định danh.')
        khoa = chuan_hoa(gia_tri)
        if khoa in da_co and da_co[khoa] != nhom:
            raise LoiCheVanBan('Các nhóm định danh bị xung đột.')
        if khoa not in da_co:
            ket_qua.append((gia_tri, nhom, nhom != 'KHAC'))
        da_co[khoa] = nhom
    return ket_qua


def _nfc_vi_tri(van_ban):
    """Bản dò đã bỏ Cf/selector và NFC, ánh xạ về đúng đoạn nguyên văn."""
    chu, vi_tri = chuan_hoa_vi_tri(van_ban)
    return chu, _ViTriGiuNguyen() if vi_tri is None else vi_tri


def _an_bi_danh(van_ban):
    if '[' not in van_ban and ']' not in van_ban:
        return van_ban
    # Chỉ ẩn bí danh đúng khuôn. Ngoặc hỏng không được nuốt tên/tiền/ngày.
    return _BI_DANH.sub(lambda m: '\x00' * len(m.group()), van_ban)


def _phat_hien(van_ban):
    """Dùng các lớp privacy hiện có, không dùng suggest vốn cắt ở 500 dòng."""
    cum, day_du = [], True
    # Số văn bản dạng số/năm được giữ theo lệnh MASK-2b. Chỉ ẩn trên bản
    # dò, giữ nguyên chiều dài/toạ độ; không miễn số tài khoản/MST hoặc
    # mã hợp đồng có hậu tố chữ như 01/2026/HD-DEMO.
    van_ban = _SO_VAN_BAN.sub(lambda m: m.group()[:m.start('so') - m.start()]
                             + '\x00' * len(m.group('so')), van_ban)
    # Regex email/URL của nguồn thử lại ở từng ký tự trên một từ rất dài.
    # Đánh dấu CHƯA KIỂM, không cắt đầu vào hay công bố bản che là đã đạt.
    # NUL cùng chiều dài giữ nguyên ranh giới và tọa độ của các lớp còn lại.
    if _KHOI_DAI.search(van_ban):
        van_ban = _KHOI_DAI.sub(lambda m: '\x00' * len(m.group()), van_ban)
        day_du = False
    # Kiểm đủ nguồn trước mọi lớp; thiếu nguồn không phải kết quả quét rỗng.
    detectors.kiem_tai_nguyen()
    cac_lop = (
        lambda: [(f.source, f.category) for f in detectors.identifiers(van_ban)],
        lambda: [(s.source, 'CONG_TY') for s in core.company_spans(van_ban)],
        lambda: [(s, 'CA_NHAN') for s in core.person_names(van_ban)],
        lambda: [(f.source, f.category) for f in detectors.detect(van_ban)],
        lambda: [(s, n) for n, s in detectors.traces(van_ban)],
        lambda: _cum_con_sot(van_ban),
    )
    if any(c in van_ban for c in '\t\r\n\f\v'):
        # Chỉ bản dò tên được làm phẳng, giữ nguyên số ký tự/toạ độ. Nhãn
        # trường và kiểm tiền/ngày vẫn dùng ranh giới dòng của bản gốc.
        chu_ten = re.sub(r'[\t\r\n\f\v]', ' ', van_ban)
        cac_lop += (
            lambda: [(s.source, 'CONG_TY') for s in core.company_spans(chu_ten)],
            lambda: [(s, 'CA_NHAN') for s in core.person_names(chu_ten)],
            lambda: _cum_con_sot(chu_ten),
        )
    for lop in cac_lop:
        try:
            cum.extend(lop())
        except ThieuTaiNguyen:
            raise
        except Exception:
            day_du = False
    return cum, day_du


def _cum_con_sot(van_ban):
    # Dùng cùng bộ quét/lọc của nguồn. Không cần đếm số lần hay tạo ngữ cảnh:
    # regex đếm từ một cụm số dài và literal_pattern có hàng nghìn \s+ rất tốn.
    ban_do = core.TOKEN.sub(lambda m: '\x00' * len(m.group()), van_ban)
    da_co, ket_qua = {}, []
    for _, b, gia_tri in leftovers._candidates(ban_do):
        if len(gia_tri) < 2 or leftovers._ordinary(gia_tri):
            continue
        if ten_nguoi.la_danh_xung(gia_tri) and ban_do[b:].lstrip().startswith('\x00'):
            continue  # Danh xưng VIẾT HOA ngay trước một bí danh, không phải tên công ty.
        khoa = leftovers.fold(gia_tri)
        if khoa not in da_co:
            da_co[khoa] = (gia_tri, leftovers._guess(gia_tri))
            ket_qua.append(da_co[khoa])
    return ket_qua


def _vung_nhan(van_ban, *, ten_da_che=frozenset()):
    """Tọa độ giá trị còn chữ/số; NUL tách phần đã che khỏi phần còn lại."""
    nhan = list(_NHAN_TRUONG.finditer(van_ban))
    for i, m in enumerate(nhan):
        if m.start() in ten_da_che:
            continue
        cuoi = nhan[i + 1].start() if i + 1 < len(nhan) else len(van_ban)
        ngat = _NGAT_TRUONG.search(van_ban, m.end(), cuoi)
        if ngat:
            cuoi = ngat.start()
        for phan in re.finditer(r'[^\x00]+', van_ban[m.end():cuoi]):
            a, b = m.end() + phan.start(), m.end() + phan.end()
            while a < b and (van_ban[a].isspace() or van_ban[a] in ':：=.,;–-'):
                a += 1
            while b > a and (van_ban[b - 1].isspace() or van_ban[b - 1] in ':：=.,;–-'):
                b -= 1
            if (m.lastgroup == 'TAI_KHOAN'
                    and re.fullmatch(_DON_VI_TIEN, van_ban[a:b], re.I)):
                continue  # Loại tiền tài khoản còn sau bí danh không phải định danh.
            if any(c.isalnum() for c in van_ban[a:b]):
                yield a, b, m.lastgroup


def _tien_theo_ngu_canh(van_ban, a, b):
    # Nguồn chỉ dùng 90 ký tự cuối trường; 180 ký tự đủ cả ranh giới từ.
    dau = max(0, a - 180)
    return detectors.money_context(van_ban[dau:b + 24], a - dau, b - dau)


def _cac_tien_ngay(van_ban):
    """Lập tập từ bản thật, độc lập với các vùng đã được chọn để che."""
    # Không có chữ/đơn vị tiền hoặc dấu nối hai chữ số thì mọi mẫu tiền/ngày
    # bên dưới đều không thể khớp. Quét một lượt trước các lớp ngữ cảnh.
    if not _DAU_TIEN_NGAY.search(van_ban):
        return []
    nfc, toa_do = _nfc_vi_tri(van_ban)
    if nfc != van_ban:
        return [(toa_do[a][0], toa_do[b - 1][1], loai,
                 van_ban[toa_do[a][0]:toa_do[b - 1][1]])
                for a, b, loai, _ in _cac_tien_ngay(nfc)]
    ket_qua = [(m.start(), m.end(), 'ngay', m.group())
               for mau in (_NGAY_SO, _NGAY_CHU) for m in mau.finditer(van_ban)]
    ngay = detectors.Spans((a, b) for a, b, _, _ in ket_qua)
    dinh_danh = detectors.Spans((a, b) for a, b, nhom in _vung_nhan(van_ban)
                               if nhom not in {'CA_NHAN', 'DIA_CHI'})
    tien_ro = []
    co_don_vi = re.search(_DON_VI_TIEN, van_ban, re.I) is not None
    for m in _TIEN_KY_HIEU.finditer(van_ban) if co_don_vi else ():
        a, b = m.span('so_truoc' if m.group('so_truoc') is not None else 'so_sau')
        if (not ngay.hit(m.start(), m.end())
                and (not dinh_danh.hit(a, b) or _tien_theo_ngu_canh(van_ban, a, b))):
            tien_ro.append((m.start(), m.end(), 'tien', m.group()))
    ket_qua.extend(tien_ro)
    da_dem = detectors.Spans((a, b) for a, b, _, _ in tien_ro)
    # Không có chữ/ngăn thập phân thì không thể có ngữ cảnh tiền. Tránh dò
    # từng số trên chuỗi bệnh lý chỉ gồm số và khoảng trắng/dấu chấm phẩy.
    if not re.search(r'[^\W\d_]|[.,$₫]', van_ban):
        return ket_qua
    for m in _SO.finditer(van_ban):
        a, b = m.span()
        if ngay.hit(a, b) or dinh_danh.hit(a, b) or da_dem.hit(a, b):
            continue
        so = m.group().lstrip('+-')
        truoc = re.split(r'[\n\t;|]', van_ban[max(0, a - 90):a])[-1]
        tien_khong = (so.startswith('0') and (detectors.MONEY_NEAR.match(van_ban[b:b + 8])
                                            or detectors.MONEY_FIELD.search(truoc)))
        # money_context của nguồn lấy cả đầu dòng: chỉ truyền cửa sổ hữu hạn,
        # cùng 90 ký tự ngữ cảnh mà nguồn thực sự dùng, không quét lại cả dòng.
        if (_DANG_TIEN.fullmatch(so) or tien_khong
                or _tien_theo_ngu_canh(van_ban, a, b)):
            ket_qua.append((a, b, 'tien', m.group()))
    return ket_qua


def _vung_tien_ngay(van_ban):
    return detectors.Spans((a, b) for a, b, _, _ in _cac_tien_ngay(van_ban))


def _kiem_tien_ngay(truoc, sau):
    def tap_gia_tri(chu):
        return Counter((loai, gia_tri) for _, _, loai, gia_tri in
                       _cac_tien_ngay(_an_bi_danh(bo_ky_tu_vo_hinh(chu))))
    return tap_gia_tri(truoc) == tap_gia_tri(sau)


def _vi_tri(dau, cuoi, xuong_dong):
    dong = bisect_right(xuong_dong, dau - 1)
    return {'bat_dau': dau, 'ket_thuc': cuoi, 'dong': dong + 1,
            'cot': dau - (xuong_dong[dong - 1] if dong else -1)}


def _kiem_con_sot(van_ban, da_biet, *, da_do=None):
    bo_do = None
    ten_da_che = set()
    if da_do is None:
        nfc, toa_do = _nfc_vi_tri(van_ban)
        # Giá trị của Ông/Bà đã là bí danh hoàn chỉnh; lời văn sau tên
        # vẫn được dò độc lập, không coi toàn bộ phần "đã ký" là tên.
        # Chỉ tin bí danh đúng khuôn, không cho NUL do caller chèn bỏ kiểm.
        ten_da_che = {m.start() for m in _NHAN_TRUONG.finditer(nfc)
                      if m.lastgroup == 'CA_NHAN' and _BI_DANH.match(nfc, m.end())}
        nfc = _an_bi_danh(nfc)
        cum, day_du = _phat_hien(nfc)
    else:
        nfc, toa_do, cum, day_du, bo_do = da_do
    if da_biet:
        cum += [(m['cum'], m['nhom_goi_y']) for m in core.leaked_known(nfc, da_biet)]
    vung = set(_vung_nhan(nfc, ten_da_che=ten_da_che))
    vung.update((m.start(), m.end(), 'CONG_TY') for m in _CONG_TY.finditer(nfc))
    vung.update((m.start(), m.end(), 'MA_SO_THUE') for m in _MST.finditer(nfc)
                if not _tien_theo_ngu_canh(nfc, m.start(), m.end())
                and not detectors.DATE.search(m.group()))
    bao_ve = _vung_tien_ngay(nfc)
    for mau, nhom in ((_GIAY_TO, 'GIAY_TO'), (_DIEN_THOAI_VN, 'DIEN_THOAI'), (_EMAIL, 'EMAIL')):
        vung.update((m.start(), m.end(), nhom) for m in mau.finditer(nfc)
                    if not bao_ve.hit(m.start(), m.end()))
    for gia_tri, nhom in set(cum):
        if (len(gia_tri) > 300 and gia_tri.isascii()
                and gia_tri.replace(' ', '').isdecimal() and nfc.strip() == gia_tri):
            # Nghi vấn số phủ toàn văn: vị trí đúng chữ đã biết, không cần
            # dựng bộ khung/KMP 500.000 ký tự lần nữa. Vẫn thêm con_sot,
            # không miễn kiểm hoặc coi số dài là đã che.
            dau = len(nfc) - len(nfc.lstrip())
            vi_tri = [(dau, dau + len(gia_tri))]
        else:
            if bo_do is None:
                bo_do = _BoDo(nfc)
            vi_tri = bo_do.spans(gia_tri, boundary=False)
        if not vi_tri:
            # Không định vị được cảnh báo của lõi cũng không được báo đã kiểm hết.
            day_du = False
        vung.update((a, b, nhom if nhom in core.CATEGORIES else 'KHAC') for a, b in vi_tri)
    xuong_dong = [i for i, c in enumerate(van_ban) if c == '\n']
    con_sot = [{'nhom': nhom, 'vi_tri': _vi_tri(toa_do[a][0], toa_do[b - 1][1], xuong_dong)}
               for a, b, nhom in sorted(vung) if a < b]
    # Lớp độc lập trên bản đã che: không phụ thuộc việc detector cũ có tìm
    # ra tên hay không. Chỉ trả nhóm/vị trí/lý do, không nguyên văn tên.
    for ten in ten_nguoi.tim(nfc):
        con_sot.append({'nhom': 'CA_NHAN', 'ly_do': ('nghi tên người nước ngoài' if ten.nuoc_ngoai
                                                  else 'nghi tên người viết thường'),
                        'diem': ten.diem, 'can_cu': list(ten.can_cu),
                        'vi_tri': _vi_tri(toa_do[ten.bat_dau][0],
                                          toa_do[ten.ket_thuc - 1][1], xuong_dong)})
    return con_sot, day_du


@dataclass(frozen=True, repr=False)
class KhaoSatChe:
    """Bản khảo sát nội bộ RAM, không phải van_ban_da_che được phát hành."""
    anh_xa: object
    doi_chieu: object
    con_sot: tuple
    kiem_tien_ngay: bool


def thu_thap_ung_vien(van_ban, da_biet, luot):
    """Ứng viên có vị trí từ đầu vào/quy tắc; không nhận danh mục kho.

    Chỉ định vị giá trị detector đã đề nghị bằng chữ/NFC/khoảng trắng,
    không fuzzy, prefix hoặc thử mọi n-gram. Từng giá trị gửi kho vẫn là
    nguyên văn của vị trí hiện tại; không dùng tên detector làm tên mở che.
    """
    luot.kiem_han()
    nfc, toa_do = _nfc_vi_tri(van_ban)
    bao_ve = _vung_tien_ngay(van_ban)
    vi_tri = {}

    def them(a, b, nhom, nguon):
        if a >= b:
            return
        a, b = toa_do[a][0], toa_do[b - 1][1]
        if not 2 <= b - a <= 300 or bao_ve.hit(a, b):
            return
        if (a, b) not in vi_tri:
            if len(vi_tri) >= TRAN_VI_TRI:
                raise loi_ung_vien('MASK_UNG_VIEN_QUA_TRAN')
            vi_tri[a, b] = UngVien(a, b, nhom, nguon)

    def dinh_vi(gia_tri, nhom, nguon):
        luot.kiem_han()
        if not 2 <= len(gia_tri) <= 300:
            return
        luot.tinh_chi_phi(len(nfc))
        phan = chuan_hoa(gia_tri).split(' ')
        mau = re.compile(r'(?<!\w)' + r'\s+'.join(re.escape(p) for p in phan) + r'(?!\w)', re.I)
        for m in mau.finditer(nfc):
            luot.kiem_han()
            them(m.start(), m.end(), nhom, nguon)

    # Danh sách này do caller đưa cùng đầu vào hiện tại, không phải từ kho.
    for gia_tri, nhom, _ in da_biet:
        dinh_vi(gia_tri, nhom, 'dau_vao')
    for a, b, nhom in _vung_nhan(nfc):
        luot.kiem_han()
        them(a, b, nhom, 'truong')
    for ten in ten_nguoi.tim(nfc):
        luot.kiem_han()
        them(ten.bat_dau, ten.ket_thuc, 'CA_NHAN', 'quy_tac')
    phat_hien, day_du = _phat_hien(nfc)
    luot.kiem_han()
    if not day_du:
        raise loi_ung_vien()
    da_do = set()
    for gia_tri, nhom in phat_hien:
        khoa = (chuan_hoa(gia_tri), nhom)
        if khoa not in da_do:
            dinh_vi(gia_tri, nhom, 'quy_tac')
            da_do.add(khoa)
    # Mỗi trường/đoạn nguyên vẹn là một ứng viên, không tách mọi chuỗi con.
    # Trường không có nhãn dùng nhóm KHAC; xung đột nhóm tại Core thì chặn.
    for m in re.finditer(r'[^\r\n\t;|]+', nfc):
        luot.kiem_han()
        a, b = m.span()
        while a < b and nfc[a].isspace():
            a += 1
        while b > a and nfc[b - 1].isspace():
            b -= 1
        if 2 <= b - a <= 300:
            them(a, b, 'KHAC', 'truong')
    for muc in sorted(vi_tri.values(), key=lambda v: (v.bat_dau, -v.ket_thuc)):
        luot.them(muc)
    return luot.ket_qua()


def khao_sat_che_chinh_xac(van_ban, dinh_danh_da_biet, kho, *, han_monotonic, kiem_huy):
    """Đầu dò nội bộ cho R3, không ghi kho/chốt/kết quả hoặc gọi Local.

    Chỉ trả bằng chứng trong RAM để đo thiếu sót. Chưa có Local thật và
    C-P4-03 nên mọi handler SDK vẫn bị chan_phat_hanh đóng cố định.
    """
    _kiem_van_ban(van_ban)
    da_biet = _kiem_dinh_danh([] if dinh_danh_da_biet is None else dinh_danh_da_biet,
                             la_khai_bao=True)
    luot = TraCuuDinhDanh(van_ban, kho, han_monotonic=han_monotonic, kiem_huy=kiem_huy)
    try:
        kq = thu_thap_ung_vien(van_ban, da_biet, luot)
        anh_xa = tao_anh_xa(van_ban, kq.phep_thay)
        kiem_anh_xa(anh_xa)
        con_sot, day_du = _kiem_con_sot(anh_xa.da_che, [])
        luot.kiem_han()
        if not day_du:
            raise loi_ung_vien()
        tien_ngay = _kiem_tien_ngay(van_ban, anh_xa.da_che)
        phan, cuoi = [], 0
        for a, b, _ in kq.phep_thay:
            phan.extend((bo_ky_tu_vo_hinh(van_ban[cuoi:a]), '\x00'))
            cuoi = b
        phan.append(bo_ky_tu_vo_hinh(van_ban[cuoi:]))
        tien_ngay = tien_ngay and not core.numeric_review(
            ''.join(phan), _an_bi_danh(anh_xa.da_che), [])['changed']
        luot.kiem_han()
        return KhaoSatChe(anh_xa, kq, tuple(con_sot), tien_ngay)
    finally:
        luot.dong()


def che(van_ban: str, dinh_danh_da_biet, kho: Kho) -> dict:
    """Che theo mẫu 1–2. Định danh đã biết: [{gia_tri, nhom}], hoặc None.

    gui_duoc chỉ True khi đã kiểm hết, con_sot rỗng và tiền/ngày giữ nguyên.
    Không trả cụm gốc trong hàng chờ/cảnh báo. Lỗi kho được che thông tin.
    """
    return _chay_che(van_ban, dinh_danh_da_biet, kho, noi_bo=False)


def che_co_anh_xa(van_ban: str, dinh_danh_da_biet, kho: Kho):
    """Cửa nội bộ cho lát Local sau: (kết quả cũ, map bất biến trong RAM).

    Không cấp map khi lớp quy tắc chặn. Quyền/kho vẫn do bên tin cậy cấp,
    không đăng ký thêm năng lực hoặc đưa map vào kết quả công khai.
    """
    return _chay_che(van_ban, dinh_danh_da_biet, kho, noi_bo=True)


def _chay_che(van_ban, dinh_danh_da_biet, kho, *, noi_bo):
    if callable(getattr(kho, 'tim_ung_vien', None)):
        # Ngăn SDK R2 không được rơi về matcher/snapshot RAM lịch sử.
        chan_phat_hanh()
    _kiem_van_ban(van_ban)
    da_biet = _kiem_dinh_danh([] if dinh_danh_da_biet is None else dinh_danh_da_biet,
                             tien_ngay=frozenset(chuan_hoa(v) for _, _, _, v in _cac_tien_ngay(van_ban)),
                             la_khai_bao=True)
    detectors.kiem_tai_nguyen()
    try:
        with kho.giao_dich():
            return _che(van_ban, da_biet, kho, noi_bo=noi_bo)
    except Exception:
        raise LoiCheVanBan('Không thể che văn bản an toàn. Cần kiểm tra lại trước khi gửi.') from None


def _che(van_ban, da_biet, kho, *, noi_bo=False):
    # Nhánh hồi quy RAM lịch sử; ngăn SDK phải đi lõi ứng viên R3 và hiện
    # bị chặn chất lượng. Giữ nhánh này tới R5/R6, không coi là P4 vận hành.
    if callable(getattr(kho, 'tim_ung_vien', None)):
        chan_phat_hanh()
    ma = kho.tao_yeu_cau()
    # Gồm danh mục chính thức và cụm tạm có sẵn trong cùng vùng của kho.
    danh_muc = kho.liet_ke_dinh_danh()
    tat_ca = [(m['gia_tri'], m['nhom'], m['nhom'] != 'KHAC') for m in danh_muc] + da_biet
    nfc, toa_do = _nfc_vi_tri(van_ban)
    bo_do = None
    phat_hien, day_du = _phat_hien(nfc)
    cac_ten = [(ten, toa_do) for ten in ten_nguoi.tim(nfc, danh_muc)]
    ban_cf = ten_nguoi.ban_do_cf(van_ban)
    if ban_cf != van_ban:
        nfc_cf, toa_do_cf = _nfc_vi_tri(ban_cf)
        cac_ten.extend((ten, toa_do_cf) for ten in ten_nguoi.tim(nfc_cf, danh_muc))
    nhan = list(_vung_nhan(nfc))
    co_dia_chi = any(nhom == 'DIA_CHI' for _, _, nhom in nhan)
    ung_vien, da_xet = [], set()
    for gia_tri, nhom, mem in tat_ca + [(s, n, False) for s, n in phat_hien]:
        khoa = (chuan_hoa(gia_tri), nhom, mem)
        if khoa in da_xet or not khoa[0]:
            continue
        da_xet.add(khoa)
        # Cụm dài không được che; chỉ cần tọa độ ở đây khi nó có thể giúp
        # mở rộng trường địa chỉ. Hậu kiểm vẫn dò đầy đủ cụm dài và biến thể.
        if len(gia_tri) > 300 and not co_dia_chi:
            continue
        if bo_do is None:
            bo_do = _BoDo(nfc)
        for a, b in bo_do.spans(gia_tri, loose=mem, masking=True):
            if a < b:
                ung_vien.append((toa_do[a][0], toa_do[b - 1][1], gia_tri, nhom))
    # Dùng toạ độ từng lần gặp, không truyền tên có danh xưng cho matcher
    # toàn văn rồi mặc nhiên nâng tin cậy các lần không có danh xưng.
    for ten, toa_do_ten in cac_ten:
        if ten.tin_cay:
            ung_vien.append((toa_do_ten[ten.bat_dau][0], toa_do_ten[ten.ket_thuc - 1][1],
                             ten.gia_tri, 'CA_NHAN'))
    bao_ve = _vung_tien_ngay(van_ban)
    # Không mất nhãn công ty do che riêng tiền tố của một tên dài hơn.
    duoi_cong_ty = {toa_do[m.start()][0]: toa_do[m.end() - 1][1]
                   for m in _CONG_TY.finditer(nfc)}
    # Lõi có thể chỉ nhận ra phần tên riêng của địa chỉ; che trọn trường đó.
    da_phat_hien = detectors.Spans((a, b) for a, b, _, _ in ung_vien)
    for a, b, nhom in nhan:
        a, b = toa_do[a][0], toa_do[b - 1][1]
        if nhom == 'DIA_CHI' and da_phat_hien.hit(a, b):
            ung_vien.append((a, b, bo_ky_tu_vo_hinh(van_ban[a:b]), nhom))
    da_chiem = core.Occupied()
    co_ngoac = '[' in van_ban or ']' in van_ban
    for m in _VUNG_BI_DANH.finditer(van_ban) if co_ngoac else ():
        da_chiem.update([m.span()])
    chon = []
    for a, b, gia_tri, nhom in sorted(ung_vien, key=lambda x: (-(x[1] - x[0]), x[0])):
        if (da_chiem.touches(a, b) or bao_ve.hit(a, b) or not 2 <= len(gia_tri) <= 300
                or '[' in gia_tri or ']' in gia_tri or nhom not in core.CATEGORIES
                or any(c.isalnum() for c in van_ban[b:duoi_cong_ty.get(a, b)])):
            continue
        da_chiem.update([(a, b)])
        chon.append((a, b, gia_tri, nhom))
    phan, so_sanh, da_dung, phep_thay = [], [], {}, []
    cuoi, so_moi = 0, 0
    for a, b, gia_tri, nhom in sorted(chon):
        muc = kho.tra_bi_danh(chuan_hoa(gia_tri))
        if muc is None:
            muc, moi = kho.ghi_cho_duyet(gia_tri, nhom, kho.cap_bi_danh_tam(), ma)
            so_moi += int(moi)
        bi_danh = muc['bi_danh']
        if not _BI_DANH.fullmatch(bi_danh) or muc['nguon'] not in {'chinh_thuc', 'tam'}:
            raise ValueError('Bí danh chưa hợp lệ.')
        if muc['nguon'] == 'tam':
            kho.ghi_nhan_gap_lai(ma, chuan_hoa(gia_tri), muc['nhom'])
        doan = bo_ky_tu_vo_hinh(van_ban[cuoi:a])
        phan.extend([doan, bi_danh])
        so_sanh.extend([doan, '\x00'])
        phep_thay.append((a, b, bi_danh))
        cuoi = b
        da_dung[bi_danh] = {'bi_danh': bi_danh, 'nhom': muc['nhom'], 'nguon': muc['nguon']}
    duoi = bo_ky_tu_vo_hinh(van_ban[cuoi:])
    phan.append(duoi)
    so_sanh.append(duoi)
    da_che = ''.join(phan)
    # Không có ứng viên được phép che và không có bí danh: bản dò không đổi.
    # Dùng lại lần quét đã hoàn tất; các lớp hậu kiểm độc lập vẫn chạy đầy đủ.
    co_ung_vien_che = any(2 <= len(gia_tri) <= 300 for _, _, gia_tri, _ in ung_vien)
    da_do = ((nfc, toa_do, phat_hien, day_du, bo_do)
             if not co_ung_vien_che and not co_ngoac and da_che == van_ban else None)
    con_sot, da_kiem_het = _kiem_con_sot(da_che, tat_ca, da_do=da_do)
    # Nếu matcher cũ chỉ che phần đầu, họ đã mất khỏi bản hậu kiểm. Giữ
    # nghi vấn từ bản gốc để không phát hành phần đuôi chưa che của tên.
    xuong_dong_goc = [i for i, c in enumerate(van_ban) if c == '\n']
    vung_da_che = detectors.Spans((a, b) for a, b, _, _ in chon)
    cong_ty_da_che = detectors.Spans((a, b) for a, b, _, nhom in chon if nhom == 'CONG_TY')
    for ten, toa_do_ten in cac_ten:
        a, b = toa_do_ten[ten.bat_dau][0], toa_do_ten[ten.ket_thuc - 1][1]
        i = bisect_right(vung_da_che.starts, a) - 1
        che_du = i >= 0 and b <= vung_da_che.ends[i]
        if ten.nuoc_ngoai:
            c = bisect_right(cong_ty_da_che.starts, a) - 1
            if c >= 0 and b <= cong_ty_da_che.ends[c]:
                continue  # Cả cụm Latin đã được che như công ty, không còn tên để lọt.
        if not ten.bat_buoc_duyet and che_du:
            continue
        if vung_da_che.hit(a, b) or toa_do_ten is not toa_do:
            con_sot.append({'nhom': 'CA_NHAN', 'ly_do': ('nghi tên người nước ngoài' if ten.nuoc_ngoai
                                                      else 'nghi tên người viết thường'),
                            'diem': ten.diem, 'can_cu': list(ten.can_cu),
                            'vi_tri': _vi_tri(a, b, xuong_dong_goc)})
    canh_bao = []
    if not day_du or not da_kiem_het:
        con_sot.append({'ly_do': 'Chưa kiểm tra đầy đủ định danh.'})
        canh_bao.append('Thiếu tài nguyên hoặc chưa hoàn tất kiểm tra định danh; không được gửi.')
    if co_ngoac and _VUNG_BI_DANH.search(van_ban):
        con_sot.append({'ly_do': 'Văn bản đầu vào đã chứa dấu bí danh cần kiểm tra.'})
    kiem_tien_ngay = (_kiem_tien_ngay(van_ban, da_che)
                      and not core.numeric_review(''.join(so_sanh), _an_bi_danh(da_che), [])['changed'])
    if not kiem_tien_ngay:
        canh_bao.append('Kiểm tra tiền và ngày chưa đạt; không được gửi.')
    gui_duoc = not con_sot and kiem_tien_ngay
    anh_xa = None
    if gui_duoc:
        anh_xa = tao_anh_xa(van_ban, phep_thay)
        kiem_anh_xa(anh_xa)
        if anh_xa.ban_do != nfc or anh_xa.da_che != da_che:
            raise LoiCheVanBan('Không xác minh được ánh xạ văn bản an toàn.')
    if noi_bo and not gui_duoc:
        raise LoiCheVanBan('Chưa kiểm tra hết định danh. Không thể tạo hồ sơ nội bộ.')
    kho.ghi_bi_danh_da_dung(ma, list(da_dung))
    ket_qua = {'ma_yeu_cau': ma, 'van_ban_da_che': da_che if gui_duoc else None,
            'con_sot': con_sot, 'kiem_tien_ngay': kiem_tien_ngay, 'gui_duoc': gui_duoc,
            'so_cho_thay': len(chon), 'bi_danh': list(da_dung.values()),
            'cho_duyet': {'so_cum_vua_them': so_moi}, 'canh_bao': canh_bao}
    return (ket_qua, anh_xa) if noi_bo else ket_qua


def _manh_bi_danh_con_lai(van_ban, cac_ma, da_xet):
    """Dò trên bản bỏ khoảng trắng, trả tọa độ đầu vào, không đoán giá trị gốc.

    cac_ma chỉ là map RAM đã kiểm của yêu cầu, không danh mục để tra ngược.
    Các vùng đã mở/đã báo được ngăn bằng NUL, không nối nhầm qua chúng.
    """
    phan = list(van_ban)
    for a, b in da_xet:
        phan[a:b] = '\x00' * (b - a)
    toa_do = [i for i, c in enumerate(phan) if not c.isspace()]
    chu = ''.join(phan[i].lower() for i in toa_do)
    ma = {chuan_bi_danh(m)[2:-2] for m in cac_ma if m and _BI_DANH.fullmatch(m)}
    vung = set()
    for muc in ma:
        dau = 0
        while (a := chu.find(muc, dau)) >= 0:
            b = a + len(muc)
            goc_a, goc_b = toa_do[a], toa_do[b - 1] + 1
            if not ((goc_a and (van_ban[goc_a - 1].isalnum() or van_ban[goc_a - 1] == '_'))
                    or (goc_b < len(van_ban) and (van_ban[goc_b].isalnum() or van_ban[goc_b] == '_'))):
                vung.add((a, b))
            dau = a + len(muc)
        # Chỉ nhận một ký tự lạ thay/chen trong mã đã được kho cấp, kể cả
        # mất hết ngoặc. Không coi chữ/số khác là wildcard (mã chưa cấp).
        # NUL và ngoặc không được khớp để khỏi nối qua vùng đã xét.
        if len(muc) < 2:
            continue
        ky_tu_la = r'[^\x00a-z0-9_.\[\]-]'
        dang_hong = []
        for i in range(len(muc)):
            truoc, sau = re.escape(muc[:i]), re.escape(muc[i + 1:])
            if i:
                dang_hong.append(truoc + ky_tu_la + re.escape(muc[i:]))
            dang_hong.append(truoc + ky_tu_la + sau)
        for m in re.finditer('|'.join(dang_hong), chu):
            a, b = toa_do[m.start()], toa_do[m.end() - 1] + 1
            # Không lấy một phần của mã dài hơn hoặc chữ thường liền cạnh.
            # Kiểm trên đầu vào để khoảng trắng ngăn văn xuôi vẫn có hiệu lực.
            if ((a and (van_ban[a - 1].isalnum() or van_ban[a - 1] == '_'))
                    or (b < len(van_ban) and (van_ban[b].isalnum() or van_ban[b] == '_'))):
                continue
            vung.add(m.span())
    tien_to = {'maskct-', 'maskcn-', 'maskdc-', 'maskmst-', 'masktk-', 'maskkhac-', 'masktam-'}
    tien_to.update(m.rsplit('-', 1)[0] + '-' for m in ma if '-' in m)
    # Dấu ? chỉ báo mã hỏng, tuyệt đối không dùng nó làm wildcard để tra kho.
    mau_tien_to = '|'.join(''.join('[%s?]' % c if c.isalnum() else re.escape(c) for c in p)
                          for p in sorted(tien_to))
    mau_ma = rf'(?:{mau_tien_to})[a-z0-9?_.-]{{1,100}}'
    for mau in (rf'[\[\]]+{mau_ma}', rf'{mau_ma}[\[\]]+'):
        vung.update(m.span() for m in re.finditer(mau, chu))
    # Gộp các dấu vết cùng mảnh, tránh báo lặp mã trần và ngoặc cạnh mã.
    gop = []
    for a, b in sorted(vung):
        if gop and a <= gop[-1][1]:
            gop[-1][1] = max(gop[-1][1], b)
        else:
            gop.append([a, b])
    return [(toa_do[a], toa_do[b - 1] + 1) for a, b in gop]


def mo_che(van_ban_co_bi_danh, ma_yeu_cau, kho, *, dong_viec=False):
    """Chỉ nhận handle RAM R4; kho tra ngược lịch sử không còn hợp lệ.

    Vòng đời/tiêu thụ thuộc handler R6, không do dong_viec điều khiển.
    Hàm này không đọc ngăn, không tìm alias ngoài map bản cuối của chuỗi.
    """
    from .kho_anh_xa_ram import _BuocRAM
    from .mo_che_ram import mo_van_ban
    from .quyen_yeu_cau import loi_ram, loi_kho
    if type(kho) is not _BuocRAM:
        raise loi_ram('MASK_ANH_XA_KHONG_CON')
    if ma_yeu_cau != kho._ctx.quyen.ma_yeu_cau:
        raise loi_kho('MASK_MA_YEU_CAU')
    return mo_van_ban(van_ban_co_bi_danh, kho)
