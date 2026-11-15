"""MASK-2b: chấm điểm tên, chỉ trả ứng viên/toạ độ và căn cứ nội bộ.

Điểm >= 8: che; 4..7: con_sot; < 4: bỏ qua. Tên dài, trùng bỏ dấu,
tên nước ngoài và ranh giới hỏng bị giới hạn điểm ở mức cần duyệt.
Danh sách bổ sung do lead cấp/tự soạn, chỉ họ hoặc âm tiết; xem NGUON.md.
"""
from bisect import bisect_right
from dataclasses import dataclass
import re
import unicodedata

from .nguon.privacy import detectors, leftovers


_TU = re.compile(r'[^\W\d_]+')
_DANH_XUNG = frozenset('ong ba anh chi em co chu bac mr mrs ms'.split())
_XUNG_CO_DAU = frozenset('ông bà anh chị em cô chú bác mr mrs ms'.split())
_XUNG_TAT = frozenset('a c o b'.split())  # Bắt buộc có dấu chấm.
_NGAT = frozenset('va voi da duoc se la cua cho gui giua ben khi neu '
                  'de tren theo den ky boi truoc sau ngay hom nay tai trong'.split())
_DONG_TU = frozenset('ky gui voi giua boi cua'.split())
_AM_DEM = frozenset('van thi duc minh thanh quoc bao xuan ngoc hoai huu'.split())
_LOI_VAN = frozenset('là đã được sẽ đang với của cho gửi giữa bởi trước sau '
                     'hôm nay ngày tại trong trên theo đến khi nếu để'.split())
_CHUC_DANH = re.compile(r'\s*\(\s*(?:ke toan|giam doc|truong phong|chu tich|thu ky)(?!\w)')
_NHAN_NUOC_NGOAI = re.compile(r'(?<!\w)(?:ten\s+)?nguoi\s+nuoc\s+ngoai\s*$')
_SAU_KY = re.compile(r'\s+(?:(?:đã|da)\s+)?(?:ký|ky|gửi|gui)(?!\w)', re.I)
NGUONG_CHE = 8
NGUONG_CON_SOT = 4

# Nguyên các họ hiếm do lead cung cấp trong lệnh sửa ngày 15/11/2026.
_HO_BO_SUNG = 'Ưng Âu Khúc Lục Thân Ninh Quan Ông Vi Mẫn Khổng Bế Nông Lò Hầu'
# Tự soạn âm tiết tên/đệm phổ biến, không chứa tổ hợp tên một người cụ thể.
_AM_TEN = '''
a an anh ánh ân ấn ba bách bạch bảo bích bình bội bửu cẩm cam cát chấn châu
chi chiến chính chung chương công cường dã dân danh dần di diễm diên diệu
doanh du duy duyên dũng dương đạt đan đăng đạo đồng đông đức định đinh đoan
gia giang giao hạ hải hà hân hạnh hằng hằng hảo hiền hiển hiếu hiệp hoài
hoan hoàng hoa hòa hoàn hồng huấn huệ hùng hưng hương huy huyền hữu khải
khang khánh khanh khiêm khoa khôi khương kiên kiệt kim kính kỳ lam lan
lâm lệ lê liên liêm linh loan long lợi lộc luân luận lương lưu ly lý mai
mẫn mạnh minh mỹ nam ngân ngọc nguyên nguyệt nga nghĩa nghị nhi nhiên
nhân nhật như nhu nhung nho ninh nữ oanh phan phong phúc phú phượng
phương phụng quân quang quảng quốc quý quyền quyên sang sơn sĩ sỹ sinh
tài tân tấn tâm tây thạch thái thắng thanh thành thảo thiên thiện thị thi
thịnh thọ thuận thu thủy thụy thư thương thường tiến tiền tín tình tinh
toàn tôn trang trâm trân trí triết trinh trình trọng trung trúc trường
tú tuấn tuệ tuyền tuyết tùng uy uyên văn vân vĩ vi việt vinh vĩnh võ vọng
vũ vương xuân xuyến y yên ý
'''
# Cụm 2–3 âm tiết: áp dụng ở MỌI vị trí, kể cả họ nằm giữa cụm.
_CUM_THONG_DUNG = (
    'báo cáo', 'tài chính', 'phương thức', 'thanh toán', 'thanh lý',
    'thuế giá trị', 'giá trị', 'lý thuyết', 'phạm vi', 'đoàn kiểm toán',
    'hoàng hôn', 'lương thực', 'mai sau', 'kim ngạch', 'châu á',
    'trịnh trọng', 'võ đoán', 'dương tính', 'vương quốc', 'tạ ơn',
    'ngô nghê', 'bùi nhùi', 'mạc định', 'trương mục', 'phan bổ', 'đinh kèm',
    'trần nợ', 'lâm thời', 'tăng giá', 'tài sản', 'cố định', 'hữu hình',
    'đường thẳng', 'làm việc', 'văn phòng', 'nguyên liệu', 'thị trường',
    'hóa đơn', 'hoa đơn', 'kế toán', 'kiểm toán', 'chuyển khoản',
    'chi phí', 'tổng tiền', 'phụ lục', 'hiệu lực', 'quản lý',
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
    khoa = chuan_ten(chu)
    return khoa.rstrip('.') in _DANH_XUNG or (khoa.endswith('.') and khoa[:-1] in _XUNG_TAT)


_HO_THEM = frozenset(chuan_ten(s) for s in _HO_BO_SUNG.split())
_AM = frozenset(chuan_ten(s) for s in _AM_TEN.split())


# Nhận dạng hình thức âm tiết, không bổ sung từ vào danh sách tên.
_AM_TIET = re.compile(r"(?:ngh|ng|nh|gh|gi|kh|ph|th|tr|ch|qu|[bcdghklmnpqrstvx])?"
                      r"[aeiouy]+(?:ch|nh|ng|[cmnpt])?$")


def ban_do_cf(chu):
    """Chỉ dùng để dò tên; thay Cf giữa hai âm tiết bằng khoảng trắng."""
    ho = {chuan_ten(s) for s in detectors.surnames()[0]}
    ket_qua = list(chu)
    for i, c in enumerate(chu):
        if (unicodedata.category(c) != 'Cf' or i == 0 or i + 1 == len(chu)
                or not chu[i - 1].isalpha() or not chu[i + 1].isalpha()):
            continue
        a, b = i - 1, i + 1
        while a > 0 and (chu[a - 1].isalpha() or unicodedata.combining(chu[a - 1])):
            a -= 1
        while b < len(chu) and (chu[b].isalpha() or unicodedata.combining(chu[b])):
            b += 1
        truoc, sau = chuan_ten(chu[a:i]), chuan_ten(chu[i + 1:b])
        if (truoc in ho or _AM_TIET.fullmatch(truoc)) and _AM_TIET.fullmatch(sau):
            ket_qua[i] = ' '
    return ''.join(ket_qua)


@dataclass(frozen=True)
class UngVienTen:
    bat_dau: int
    ket_thuc: int
    gia_tri: str
    tin_cay: bool
    co_ngu_canh: bool
    bat_buoc_duyet: bool = False
    diem: int = 0
    can_cu: tuple[str, ...] = ()
    nuoc_ngoai: bool = False


def tim(chu, danh_muc=()):
    """Bản dò đã bỏ Cf/selector, NFC; caller ánh xạ về nguyên văn.

    Cửa sinh ứng viên Việt: họ trong từ điển/họ bổ sung hoặc danh xưng.
    Cụm thường trừ 8 điểm; danh xưng/tên chính thức không bị miễn ngầm.
    Tên nước ngoài cần ngữ cảnh, luôn chặn; không suy họ Việt từ từ bất kỳ.
    """
    ho = {chuan_ten(s) for s in detectors.surnames()[0]} | _HO_THEM
    cum_thuong, _ = leftovers.allowlist()
    cum_mien = {chuan_ten(s) for s in cum_thuong | detectors.places()}
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
    mien, dau_cum = set(), set()
    for i, khoa in enumerate(khoa_tu):
        for am in theo_dau.get(khoa, ()):
            cuoi = i + len(am)
            if (tuple(khoa_tu[i:cuoi]) == am
                    and all(chu[tu[k - 1].end():tu[k].start()].isspace()
                            for k in range(i + 1, cuoi))):
                mien.update(range(i, cuoi))
                dau_cum.add(i)
    ket_qua = []
    for i, dau in enumerate(tu):
        if dau.start() and (chu[dau.start() - 1].isalnum() or chu[dau.start() - 1] == '_'):
            continue
        goc = dau.group().casefold()
        if goc in _LOI_VAN:
            continue  # "là" không phải họ Lã, "đang" không phải tên Đăng.
        la_xung = khoa_tu[i] in _DANH_XUNG and (goc in _XUNG_CO_DAU or goc.isascii())
        if la_xung and goc != 'chu':
            continue  # Không lấy chính danh xưng làm từ đầu một tên nước ngoài.
        if (dau.group().casefold() == 'chú' and i + 1 < len(tu)
                and khoa_tu[i + 1] in ho and chu[dau.end():tu[i + 1].start()].isspace()):
            continue  # "chú trần ...": Chú là danh xưng, không phải họ Chu.
        a = dau.start()
        truoc = chu[tu[i - 1].end():a] if i else ''
        co_the_xung = bool(i and khoa_tu[i - 1] in _DANH_XUNG | _XUNG_TAT)
        lien_truoc = bool(co_the_xung and re.fullmatch(r'\s*[.:：=]?\s+', truoc))
        goc_truoc = tu[i - 1].group().casefold() if i else ''
        danh_xung = bool(lien_truoc and (i - 1 not in mien or '.' in truoc)
                         and ((khoa_tu[i - 1] in _DANH_XUNG
                               and (goc_truoc in _XUNG_CO_DAU or goc_truoc.isascii()))
                              or (khoa_tu[i - 1] in _XUNG_TAT and '.' in truoc)))
        dong_tu = bool(i and truoc.isspace() and khoa_tu[i - 1] in _DONG_TU)
        nhan_ngoai = bool(i and khoa_tu[i - 1] == 'ngoai'
                          and _NHAN_NUOC_NGOAI.search(chuan_ten(chu[max(0, a - 80):a])))
        la_ho = khoa_tu[i] in ho
        if not la_ho and not danh_xung and not dau.group().isascii():
            continue
        # Không nhận danh xưng là họ Ông khi theo ngay sau là họ của tên.
        if (dau.group().casefold() == 'ông' and i + 1 < len(tu)
                and khoa_tu[i + 1] in ho and chu[dau.end():tu[i + 1].start()].isspace()):
            continue
        j = i + 1
        while j < min(len(tu), i + 5):
            m = tu[j]
            if (not chu[tu[j - 1].end():m.start()].isspace()
                    or khoa_tu[j] in _NGAT
                    or m.group().casefold() == 'đang'
                    or (j in dau_cum and not danh_xung)):
                break
            j += 1
        b = tu[j - 1].end()
        am = khoa_tu[i:j]
        gia_tri = ' '.join(m.group() for m in tu[i:j])
        khoa = ' '.join(am)
        sau_ky = bool(_SAU_KY.match(chu, b))
        latin = all(m.group().isascii() for m in tu[i:j])
        nuoc_ngoai = bool(latin and len(am) >= 2
                          and (not la_ho or any(s not in _AM for s in am[1:]))
                          and not (danh_xung and not la_ho and all(s in _AM for s in am))
                          and (dong_tu or danh_xung or nhan_ngoai or sau_ky))
        if not la_ho and not danh_xung and not nuoc_ngoai:
            continue
        if len(am) < (1 if danh_xung else 2):
            continue
        diem, can_cu = 0, []

        def cong(so, ly_do):
            nonlocal diem
            diem += so
            can_cu.append(f'{ly_do}:{so:+d}')

        if la_ho:
            cong(3, 'HO_TU_DIEN')
            ten_dung = sum(s in _AM for s in am[1:])
            cong(min(ten_dung, 2), 'AM_TEN')
            if len(am) >= 3 and am[1] in _AM_DEM:
                cong(1, 'AM_DEM')
            if not danh_xung:
                cong(-(len(am) - 1 - ten_dung), 'AM_CHUA_BIET')
            if len(am) >= 2 and all(m.group()[:1].isupper() for m in tu[i:j]):
                cong(4, 'VIET_HOA_TEN')
        if danh_xung:
            cong(5, 'DANH_XUNG')
            if not la_ho:
                cong(3, 'TEN_SAU_DANH_XUNG')
        if nuoc_ngoai:
            cong(4, 'LATIN_CO_NGU_CANH')
        if dong_tu:
            cong(1, 'DONG_TU_LIEN_TRUOC')
        chuc_danh = bool(chu[b:b + 10].lstrip().startswith('(')
                         and _CHUC_DANH.match(chuan_ten(chu[b:b + 80])))
        if chuc_danh:
            cong(1, 'CHUC_DANH_LIEN_SAU')
        if any(k in mien for k in range(i, j)) or khoa in viet_tat:
            cong(-8, 'CUM_THONG_DUNG')
        ten_chinh_thuc = da_duyet.get(khoa, [])
        if len(ten_chinh_thuc) == 1:
            cong(8, 'TEN_CHINH_THUC')
        mo_ho_chu = bool(dau.group().casefold() == 'chu' and i + 1 < j and khoa_tu[i + 1] in ho)
        qua_dai = len(am) > (4 if la_ho else 3)
        loi_bien = bool(b < len(chu) and (chu[b].isalnum() or chu[b] == '_'))
        bat_buoc = qua_dai or loi_bien or nuoc_ngoai or len(ten_chinh_thuc) > 1 or mo_ho_chu
        if (len(ten_chinh_thuc) > 1 or mo_ho_chu
                or danh_xung and diem < NGUONG_CON_SOT):
            cong(max(0, NGUONG_CON_SOT - diem), 'BAT_BUOC_DUYET')
            bat_buoc = True
        if diem < NGUONG_CON_SOT:
            continue
        if bat_buoc and diem >= NGUONG_CHE:
            cong(NGUONG_CHE - 1 - diem, 'GIOI_HAN_CAN_DUYET')
        tin_cay = diem >= NGUONG_CHE and not bat_buoc
        ket_qua.append(UngVienTen(a, b, ten_chinh_thuc[0] if len(ten_chinh_thuc) == 1
                                 else gia_tri, tin_cay, dong_tu or danh_xung or chuc_danh or nuoc_ngoai,
                                 bat_buoc or not tin_cay, diem, tuple(can_cu), nuoc_ngoai))
    vung_tin_cay = detectors.Spans((m.bat_dau, m.ket_thuc) for m in ket_qua if m.tin_cay)
    loc = []
    for ten in ket_qua:
        i = bisect_right(vung_tin_cay.starts, ten.bat_dau) - 1
        if (not ten.tin_cay and i >= 0 and ten.ket_thuc <= vung_tin_cay.ends[i]):
            continue  # "Nguyễn Đăng Khoa": Đăng Khoa nằm trong tên đã được che đủ.
        loc.append(ten)
    return loc
