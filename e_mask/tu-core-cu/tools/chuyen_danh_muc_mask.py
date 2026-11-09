"""Chuyển bản xuất JSON quy tắc Mask v2 qua kết nối do Core cung cấp.

Không tự tìm danh mục, không đọc cấu hình/kết nối, không tự nối CSDL.
Đầu vào: list quy tắc hoặc {"rules": [...]}; source/category, tùy chọn
ma_junsky do người vận hành bổ sung rõ ràng. Không suy Junsky từ token cũ.
Mặc định chỉ SELECT; ghi phải chọn chay_thu=False và truyền kết nối psycopg.
Transaction ngoài do caller quyết định; mỗi dòng lỗi dùng savepoint riêng.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import sys
import unicodedata


TIEN_TO = {
    'CONG_TY': 'MASKCT', 'CA_NHAN': 'MASKCN', 'DIA_CHI': 'MASKDC',
    'MA_SO_THUE': 'MASKMST', 'TAI_KHOAN': 'MASKTK', 'EMAIL': 'MASKKHAC',
    'DIEN_THOAI': 'MASKKHAC', 'GIAY_TO': 'MASKKHAC', 'HOP_DONG': 'MASKKHAC',
    'DU_AN': 'MASKKHAC', 'KHAC': 'MASKKHAC',
}

# Cùng tập ký tự với mask.chuan_hoa: Unicode White_Space và U+001C–U+001F.
# Không dùng split()/[:space:] để tập khoảng trắng không phụ thuộc locale.
_KHOANG_TRANG = re.compile(
    r'[\u0009-\u000d\u001c-\u0020\u0085\u00a0\u1680\u2000-\u200a'
    r'\u2028\u2029\u202f\u205f\u3000]+'
)


def chuan_hoa(gia_tri: str) -> str:
    """Khớp Unicode lower/NFC/gộp khoảng trắng của SQL dùng und-x-icu.

    Giữ nguyên dấu tiếng Việt, không phụ thuộc locale của CSDL hay hệ điều hành.
    """
    return _KHOANG_TRANG.sub(' ', unicodedata.normalize('NFC', gia_tri)).strip(' ').lower()


def bi_danh(nhom: str, *, so: int = 1, ma_junsky: str | None = None) -> str:
    """Quy tắc thuần để kiểm trước nhập; SQL mới là nơi cấp số chính thức."""
    if nhom not in TIEN_TO:
        raise ValueError('Nhóm định danh chưa hợp lệ.')
    if ma_junsky is not None:
        if (not isinstance(ma_junsky, str)
                or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}', ma_junsky)):
            raise ValueError('Mã đối tượng chưa hợp lệ.')
        if ma_junsky.upper().startswith('MASK'):
            raise ValueError('Tiền tố mã đối tượng trùng vùng dành cho bí danh.')
        return '[['+ma_junsky+']]'
    if type(so) is not int or so < 1:
        raise ValueError('Số thứ tự chưa hợp lệ.')
    return f'[[{TIEN_TO[nhom]}-{so:04d}]]'


@dataclass(repr=False)
class KetQua:
    truoc: int = 0
    sau: int = 0
    loi: dict[str, int] = field(default_factory=dict)
    se_them: dict[str, int] = field(default_factory=dict)
    se_bo_qua: dict[str, int] = field(default_factory=dict)
    se_cho_duyet: dict[str, int] = field(default_factory=dict)
    chua_doi_chieu: dict[str, int] = field(default_factory=dict)

    def __repr__(self):
        return (f'KetQua(truoc={self.truoc}, sau={self.sau}, loi={self.loi!r}, '
                f'se_them={self.se_them!r}, se_bo_qua={self.se_bo_qua!r}, '
                f'se_cho_duyet={self.se_cho_duyet!r}, chua_doi_chieu={self.chua_doi_chieu!r})')


class _LoiDong(ValueError):
    pass


def _doc_muc(muc):
    if not isinstance(muc, dict):
        raise _LoiDong('dinh_dang')
    gia_tri, nhom = muc.get('source'), muc.get('category', 'KHAC')
    if (not isinstance(gia_tri, str) or not 2 <= len(gia_tri) <= 300
            or not chuan_hoa(gia_tri) or not isinstance(nhom, str) or nhom not in TIEN_TO
            or any(unicodedata.category(c).startswith('C') and not c.isspace() for c in gia_tri)
            or '[' in gia_tri or ']' in gia_tri):
        raise _LoiDong('dinh_dang')
    if type(muc.get('enabled', True)) is not bool:
        raise _LoiDong('dinh_dang')
    if not muc.get('enabled', True):
        raise _LoiDong('muc_tat')
    # Không tách âm thầm tên khác vốn dùng chung token trong lõi cũ.
    canonical = muc.get('canonical')
    if canonical is not None and (not isinstance(canonical, str)
                                  or chuan_hoa(canonical) != chuan_hoa(gia_tri)):
        raise _LoiDong('ten_khac')
    ma = muc.get('ma_junsky')
    try:
        bi_danh(nhom, ma_junsky=ma)
    except ValueError:
        if isinstance(ma, str) and ma.upper().startswith('MASK'):
            raise _LoiDong('tien_to') from None
        raise _LoiDong('dinh_dang') from None
    return unicodedata.normalize('NFC', gia_tri), nhom, ma


def _loai_csdl(exc):
    return {'23505': 'xung_dot', '23514': 'rang_buoc', '23502': 'rang_buoc',
            '42501': 'quyen'}.get(getattr(exc, 'sqlstate', None), 'csdl')


def chuyen_danh_muc(duong_dan, ket_noi, *, la_demo: bool, chay_thu: bool = True) -> KetQua:
    """Trả số đếm, không giữ lỗi driver/giá trị/đường dẫn trong kết quả.

    Chạy thử không DML, không nextval và không đổi GUC; nếu có kết nối thì
    caller phải đặt ktt.mask_la_demo đúng vùng trước khi gọi. RLS tiếp tục
    là rào bắt buộc. Chuyển thật đặt GUC cục bộ và phục hồi trong transaction.
    """
    loi = Counter()
    kq = KetQua()
    if type(la_demo) is not bool or type(chay_thu) is not bool:
        kq.loi = {'tham_so': 1}
        return kq
    try:
        data = json.loads(Path(duong_dan).read_text(encoding='utf-8-sig'))
        if isinstance(data, dict):
            data = data.get('rules')
        if not isinstance(data, list):
            raise ValueError
    except (OSError, ValueError, TypeError, RecursionError):
        kq.loi = {'tep': 1}
        return kq
    # Một token cũ có thể chỉ nhiều tên của cùng đối tượng. Chưa có quy tắc
    # chọn tên mở che chuẩn thì báo cả nhóm, không tự chia thành các bí danh mới.
    token_cu = {}
    for muc in data:
        if isinstance(muc, dict) and isinstance(muc.get('token'), str) and isinstance(muc.get('source'), str):
            token_cu.setdefault(muc['token'], set()).add(chuan_hoa(muc['source']))
    dong = []
    cho_duyet = Counter()
    da_gap = set()
    ma_da_gap = set()
    for muc in data:
        try:
            gia_tri, nhom, ma = _doc_muc(muc)
        except _LoiDong as exc:
            loi[str(exc)] += 1
            if chay_thu and str(exc) == 'ten_khac':
                cho_duyet[muc.get('category', 'KHAC')] += 1
            continue
        if isinstance(muc.get('token'), str) and len(token_cu[muc['token']])>1:
            loi['ten_khac'] += 1
            if chay_thu:
                cho_duyet[nhom] += 1
            continue
        khoa = chuan_hoa(gia_tri)
        if khoa in da_gap:
            loi['trung_trong_tep'] += 1
            continue
        if ma is not None and ma.lower() in ma_da_gap:
            loi['xung_dot'] += 1
            continue
        da_gap.add(khoa)
        if ma is not None:
            ma_da_gap.add(ma.lower())
        dong.append((gia_tri, nhom, ma))
    if chay_thu:
        kq.se_cho_duyet = dict(cho_duyet)
        # Chưa có kết nối/đủ quyền thì không đoán mục nào đã có trong CSDL.
        kq.chua_doi_chieu = dict(Counter(nhom for _, nhom, _ in dong))
    if ket_noi is None:
        if not chay_thu:
            loi['ket_noi'] += 1
        kq.loi = dict(loi)
        return kq
    dem_sql = 'SELECT count(*) FROM mask.dinh_danh WHERE la_demo=%s'
    tim_sql = ('SELECT nhom,ma_junsky FROM mask.dinh_danh '
               'WHERE la_demo=%s AND gia_tri_chuan=mask.chuan_hoa(%s)')
    se_them, se_bo_qua, chua_doi_chieu = Counter(), Counter(), Counter()
    try:
        with ket_noi.transaction():
            cu = ket_noi.execute("SELECT current_setting('ktt.mask_la_demo',true)").fetchone()[0]
            if chay_thu and cu != ('true' if la_demo else 'false'):
                kq.loi = dict(loi + Counter({'quyen': 1}))
                return kq
            if not chay_thu:
                ket_noi.execute("SELECT set_config('ktt.mask_la_demo',%s,true)",
                                ('true' if la_demo else 'false',))
            kq.truoc = ket_noi.execute(dem_sql, (la_demo,)).fetchone()[0]
            for gia_tri, nhom, ma in dong:
                try:
                    with ket_noi.transaction():
                        da_co = ket_noi.execute(tim_sql, (la_demo, gia_tri)).fetchone()
                        if da_co is not None:
                            if tuple(da_co) != (nhom, ma):
                                loi['xung_dot'] += 1
                            elif chay_thu:
                                se_bo_qua[nhom] += 1
                            continue
                        if ma is not None and ket_noi.execute(
                                'SELECT EXISTS (SELECT FROM mask.dinh_danh '
                                'WHERE la_demo=%s AND lower(bi_danh COLLATE "und-x-icu")'
                                '=lower(%s COLLATE "und-x-icu"))',
                                (la_demo, '[['+ma+']]')).fetchone()[0]:
                            loi['xung_dot'] += 1
                            continue
                        if chay_thu:
                            se_them[nhom] += 1
                        else:
                            ket_noi.execute("""INSERT INTO mask.dinh_danh
                                (gia_tri,nhom,ma_junsky,nguon,la_demo)
                                VALUES(%s,%s,%s,'MASK_V2',%s)""", (gia_tri, nhom, ma, la_demo))
                except Exception as exc:
                    loi[_loai_csdl(exc)] += 1
                    if chay_thu:
                        chua_doi_chieu[nhom] += 1
            kq.sau = ket_noi.execute(dem_sql, (la_demo,)).fetchone()[0]
            if not chay_thu:
                ket_noi.execute("SELECT set_config('ktt.mask_la_demo',%s,true)", (cu or '',))
    except Exception as exc:
        # Transaction ngoài đã rollback toàn đợt; không công bố số ghi đã lùi.
        loi[_loai_csdl(exc)] += 1
        kq.sau = kq.truoc
    else:
        if chay_thu:
            kq.se_them, kq.se_bo_qua = dict(se_them), dict(se_bo_qua)
            kq.chua_doi_chieu = dict(chua_doi_chieu)
    kq.loi = dict(loi)
    return kq


_NHAN_LOI = {
    'tep': 'tệp', 'dinh_dang': 'định dạng', 'muc_tat': 'mục tắt', 'ten_khac': 'tên khác',
    'tien_to': 'tiền tố', 'trung_trong_tep': 'trùng trong tệp', 'xung_dot': 'xung đột',
    'rang_buoc': 'ràng buộc', 'quyen': 'quyền', 'csdl': 'kết nối dữ liệu',
    'ket_noi': 'thiếu kết nối', 'tham_so': 'tham số',
}

_NHAN_NHOM = {
    'CONG_TY': 'Công ty', 'CA_NHAN': 'Cá nhân', 'DIA_CHI': 'Địa chỉ',
    'MA_SO_THUE': 'Mã số thuế', 'TAI_KHOAN': 'Tài khoản', 'EMAIL': 'Thư điện tử',
    'DIEN_THOAI': 'Điện thoại', 'GIAY_TO': 'Giấy tờ', 'HOP_DONG': 'Hợp đồng',
    'DU_AN': 'Dự án', 'KHAC': 'Khác',
}


class _ThamSo(argparse.ArgumentParser):
    def error(self, message):
        # Không in usage/argv: tham số có thể chứa tên tệp/định danh.
        raise ValueError


def main(argv=None, *, ket_noi=None) -> int:
    chay_thu = True
    parser = _ThamSo(add_help=False)
    parser.add_argument('tep')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--chay-thu', action='store_true')
    mode.add_argument('--ghi', action='store_true')
    vung = parser.add_mutually_exclusive_group()
    vung.add_argument('--demo', action='store_true')
    vung.add_argument('--van-hanh', action='store_true')
    try:
        args = parser.parse_args(argv)
    except (ValueError, SystemExit):
        kq = KetQua(loi={'tham_so': 1})
    else:
        chay_thu = not args.ghi
        kq = chuyen_danh_muc(args.tep, ket_noi, la_demo=not args.van_hanh, chay_thu=chay_thu)
    print(f'Số dòng trước: {kq.truoc}')
    print(f'Số dòng sau: {kq.sau}')
    if chay_thu:
        for nhan, dem in (('Sẽ thêm', kq.se_them), ('Sẽ bỏ qua (đã có)', kq.se_bo_qua),
                          ('Sẽ vào danh sách chờ', kq.se_cho_duyet),
                          ('Chưa đối chiếu', kq.chua_doi_chieu)):
            print(f'{nhan}: {sum(dem.values())}')
            for nhom in sorted(dem):
                print(f'{nhan} ({_NHAN_NHOM[nhom]}): {dem[nhom]}')
    for ma in sorted(kq.loi):
        print(f'Lỗi {_NHAN_LOI[ma]}: {kq.loi[ma]}')
    return 1 if kq.loi else 0


if __name__ == '__main__':
    sys.exit(main())
