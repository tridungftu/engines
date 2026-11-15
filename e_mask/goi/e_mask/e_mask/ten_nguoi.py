"""MASK-2b: dò họ + âm tiết, không phụ thuộc dấu hoặc chữ hoa.

Chỉ trả ứng viên/toạ độ nội bộ; không cấp bí danh, quyền hay lưu nội dung.
Tên dài/mơ hồ giữ lại để chặn, không tự cắt thành một tên được phép che.
"""
from bisect import bisect_right
from dataclasses import dataclass
import re
import unicodedata

from .nguon.privacy import detectors, leftovers


_TU = re.compile(r'[^\W\d_]+')
_CHU_VIET = frozenset('aăâbcdđeêghiklmnoôơpqrstuưvxy')
_DANH_XUNG = frozenset('ong ba anh chi em co chu bac mr mrs ms'.split())
# Không dùng "thì/thi", "nhận/nhan", "năm/nam", "đang/dang": trùng
# Thị, Nhân, Nam, Đăng. Khi không tách được lời văn, chặn để người dùng duyệt.
_NGAT = frozenset('va voi da duoc se la cua cho gui giua ben khi neu '
                  'de tren theo den'.split())
_CHUC_DANH = re.compile(r'\s*\(\s*(?:ke toan|giam doc|truong phong|chu tich|thu ky)(?!\w)')
# Cụm thông dụng trùng họ; chỉ áp dụng khi không có danh xưng/tên đã duyệt.
# Dùng cả cụm, không miễn mọi từ bắt đầu bằng họ như "lê", "cao", "lý".
_CUM_THONG_DUNG = (
    'lê thê', 'lệ phí', 'lễ tết', 'lý do', 'lý luận', 'lý lịch',
    'hồ sơ', 'hỗ trợ', 'hồ chứa', 'cao hơn', 'cao nhất', 'cao cấp', 'cao điểm',
    'cao tốc', 'cao su', 'lương tháng', 'lương cơ bản', 'lương phải trả',
    'lương thưởng', 'tăng giảm', 'tăng trưởng', 'tăng vốn', 'tăng doanh thu',
    'tăng chi phí', 'tăng dự phòng', 'lãi suất', 'lãi vay', 'lãi lỗ', 'lãi kép',
    'lại kiểm tra', 'lại chứng từ', 'đồ thị', 'đo lường', 'độ lệch',
    'thái độ', 'đào tạo', 'đáo hạn', 'chu kỳ', 'chữ ký', 'chữ số',
    'chủ nợ', 'chủ đầu tư', 'chủ sở hữu', 'mai nộp', 'mai thanh toán',
    'nghiệm thu', 'phân bổ', 'giữ nguyên', 'quá trình', 'gia hạn',
    'là địa điểm', 'là sai',
)


def chuan_ten(chu):
    """Bỏ dấu nhưng giữ ranh giới âm tiết, không ghép tên xuyên dấu câu."""
    chu = unicodedata.normalize('NFD', chu.casefold().replace('đ', 'd'))
    return ' '.join(''.join(c for c in chu if not unicodedata.combining(c)).split())


def la_danh_xung(chu):
    return chuan_ten(chu) in _DANH_XUNG


@dataclass(frozen=True)
class UngVienTen:
    bat_dau: int
    ket_thuc: int
    gia_tri: str
    tin_cay: bool
    co_ngu_canh: bool
    bat_buoc_duyet: bool = False


def tim(chu, danh_muc=()):
    """Bản dò phải được bỏ Cf/selector và NFC, caller ánh xạ về nguyên văn.

    2–4 âm tiết: danh xưng hoặc đúng một tên chính thức => được che. "và"
    và ngoặc chức danh chỉ củng cố nghi vấn, không đủ để tự cho phát hành.
    5 âm tiết trở lên => chặn; không coi phần đầu là toàn bộ tên.
    """
    ho = {chuan_ten(s) for s in detectors.surnames()[0]}
    cum_thuong, tu_thuong = leftovers.allowlist()
    cum_mien = {chuan_ten(s) for s in cum_thuong | detectors.places()}
    tu_mien = {chuan_ten(s) for s in tu_thuong}
    viet_tat = {chuan_ten(s) for s in detectors.acronyms()}
    thong_dung = {chuan_ten(s) for s in _CUM_THONG_DUNG}
    da_duyet = {}
    for muc in danh_muc:
        if muc['nhom'] == 'CA_NHAN' and muc.get('nguon') == 'chinh_thuc':
            da_duyet.setdefault(chuan_ten(muc['gia_tri']), []).append(muc['gia_tri'])
    tu = list(_TU.finditer(chu))
    khoa_tu = [chuan_ten(m.group()) for m in tu]
    # Loại cả những họ nằm giữa cụm thường: "giữ nguyên", "gia hạn".
    # Không lấy prefix riêng "nguyên", "hạn" làm một ngoại lệ toàn cục.
    theo_dau = {}
    for cum in cum_mien | thong_dung:
        am = tuple(cum.split())
        theo_dau.setdefault(am[0], []).append(am)
    mien = set()
    for i, khoa in enumerate(khoa_tu):
        for am in theo_dau.get(khoa, ()):
            cuoi = i + len(am)
            if (tuple(khoa_tu[i:cuoi]) == am
                    and all(chu[tu[k - 1].end():tu[k].start()].isspace()
                            for k in range(i + 1, cuoi))):
                mien.update(range(i, cuoi))
    ket_qua = []
    for i, dau in enumerate(tu):
        if (khoa_tu[i] not in ho or (dau.start() and (chu[dau.start() - 1].isalnum()
                                                    or chu[dau.start() - 1] == '_'))):
            continue
        if (dau.group().casefold() == 'chú' and i + 1 < len(tu)
                and khoa_tu[i + 1] in ho and chu[dau.end():tu[i + 1].start()].isspace()):
            continue  # "chú trần ...": Chú là danh xưng, không phải họ Chu.
        j = i + 1
        while j < min(len(tu), i + 5):
            m = tu[j]
            if (not chu[tu[j - 1].end():m.start()].isspace()
                    or khoa_tu[j] in _NGAT
                    or m.group().casefold() == 'đang'
                    or not all(c in _CHU_VIET for c in khoa_tu[j])):
                break
            j += 1
        if j - i < 2:
            continue
        a, b = dau.start(), tu[j - 1].end()
        gia_tri = ' '.join(m.group() for m in tu[i:j])
        khoa = ' '.join(khoa_tu[i:j])
        truoc = chu[tu[i - 1].end():a] if i else ''
        danh_xung = bool(i and khoa_tu[i - 1] in _DANH_XUNG
                         and re.fullmatch(r'\s*[.:：]?\s+', truoc))
        va_truoc = bool(i and khoa_tu[i - 1] == 'va' and truoc.isspace())
        va_sau = bool(j < len(tu) and khoa_tu[j] == 'va'
                      and chu[b:tu[j].start()].isspace())
        ngu_canh = va_truoc or va_sau or bool(_CHUC_DANH.match(chuan_ten(chu[b:b + 80])))
        ten_chinh_thuc = da_duyet.get(khoa, [])
        tin_cay = j - i <= 4 and (danh_xung or len(ten_chinh_thuc) == 1)
        if len(ten_chinh_thuc) > 1:
            tin_cay = False  # Không chọn tuỳ tiện hai tên trùng nhau sau bỏ dấu.
        if not tin_cay and not danh_xung and not ten_chinh_thuc:
            if (i in mien or khoa in cum_mien or khoa in viet_tat
                    or (not ngu_canh and all(s in tu_mien for s in khoa_tu[i:j]))):
                continue
        ket_qua.append(UngVienTen(a, b, ten_chinh_thuc[0] if len(ten_chinh_thuc) == 1
                                 else gia_tri, tin_cay, ngu_canh,
                                 len(ten_chinh_thuc) > 1
                                 or (not tin_cay and dau.group()[0].islower())))
    vung_tin_cay = detectors.Spans((m.bat_dau, m.ket_thuc) for m in ket_qua if m.tin_cay)
    loc = []
    for ten in ket_qua:
        i = bisect_right(vung_tin_cay.starts, ten.bat_dau) - 1
        if (not ten.tin_cay and i >= 0 and ten.ket_thuc <= vung_tin_cay.ends[i]):
            continue  # "Nguyễn Đăng Khoa": Đăng Khoa nằm trong tên đã được che đủ.
        loc.append(ten)
    return loc
