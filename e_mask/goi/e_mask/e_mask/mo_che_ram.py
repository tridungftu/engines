"""Mở che một lần từ RAM đúng chuỗi; không kho tra ngược hoặc cache bản rõ.

C-P4-02/05 chưa có binding SDK. Port bàn giao phải cách ly kết quả, giữ
quyền/lease/deadline đến khi RAM tiêu thụ xong rồi mới phát hành đúng
module/người. Adapter chỉ trong tests; không có đường tự cấp quyền.
"""
from contextlib import ExitStack
from copy import deepcopy
from hashlib import sha256
import re
from typing import Protocol

from kho_tri_thuc_sdk.engine import ChuaRo, LoiDuongTruyen, LoiNghiepVu, ViecDaHuy

from . import phong_bi
from .anh_xa_ai import AnhXaAI, LoiAnhXa, kiem_anh_xa
from .che_van_ban import _BI_DANH, _DoManhBiDanh, chuan_bi_danh
from .kho_anh_xa_ram import KhoAnhXaRAM, _BuocRAM, _bam
from .quyen_yeu_cau import NguCanhTinCay, loi_kho, loi_ram, xac_minh

CHUYEN_QUY_TRINH = (
    'Mở che dùng một lần; dữ liệu được dọn dù quy trình cũ chọn không đóng việc. '
    'Anh cần mở lại thì chạy lại toàn bộ chuỗi che và hỏi AI.'
)
KIEM_LAI = 'Nội dung đã mở che; cần kiểm tra lại nguyên văn và trích dẫn.'
_VUNG = re.compile(r'\[\s*\[[^\[\]]*(?:\]\s*\]|(?=[\[\]])|$)')


def loi(ma='MASK_MO_CHE_KHONG_DAY_DU'):
    cau = {
        'MASK_MO_CHE_KHONG_DAY_DU': 'Không thể mở che đầy đủ kết quả này. Anh hãy chạy lại toàn bộ chuỗi.',
        'MASK_MO_CHE_CHUA_CO_CUA_CORE': 'Chưa xác minh được quyền bàn giao kết quả mở che. Anh hãy thử lại sau.',
    }
    return LoiNghiepVu(ma, cau[ma])


class CongMoCheRAM(Protocol):
    """Cửa chung đề nghị, không phải API SDK đã có.

    Context manager yield hàm nhan(bytes) -> True, chỉ nhận kết quả cuối,
    không nhận map/gốc. Giữ kết quả chưa phát hành và khóa quyền xuyên
    __exit__; lỗi/hủy/TTL phải bỏ kết quả chờ. __exit__ thành công chỉ
    phát hành khi RAM đã tiêu thụ, đúng scope/instance/lease/deadline.
    Không nuốt ngoại lệ. Mất ACK sau nhận phải ChuaRo; Core giao lại
    kết quả đã nhận theo quyền, không gọi mở lại. Không gửi Cloud/log.
    """
    def ban_giao_cuoi(self, viec, ngu_canh, *, bam_dau_vao, han_monotonic): ...


def _don_ngoai_le(exc):
    """Không giữ frame xử lý/bản rõ qua chu kỳ ngoại lệ của ExitStack."""
    da_gap = set()
    cho = [exc]
    while cho:
        muc = cho.pop()
        if not isinstance(muc, BaseException) or id(muc) in da_gap:
            continue
        da_gap.add(id(muc))
        cho.extend((muc.__context__, muc.__cause__))
        muc.__traceback__ = muc.__context__ = muc.__cause__ = None


def kiem_map_ram(buoc):
    if type(buoc) is not _BuocRAM:
        raise loi_ram('MASK_ANH_XA_KHONG_CON')
    giai_doan, m, aliases = buoc.chup_map_mo()
    theo_ma, da_tra = {}, False
    try:
        buoc.kiem()
        if giai_doan != 'DA_HAU_KIEM':
            raise loi_ram('MASK_VONG_DOI_KHONG_HOP_LE')
        if type(m) is not AnhXaAI or type(aliases) is not dict:
            raise loi_ram('MASK_ANH_XA_KHONG_CON')
        kiem_anh_xa(m)
        # Chỉ phép thay thực sự ở bản cuối được dùng để mở; không mượn
        # alias trong kho/detector/đoạn Local hoặc bản quy tắc trước đó.
        if m.alias_nguyen_van() != aliases:
            raise loi()
        # Bản cuối R5 bàn giao chính m.da_che. Không dùng danh sách alias
        # cấp trước đó để mở alias chưa xuất hiện trong văn bản đã giao.
        da_giao = set()
        for muc in _BI_DANH.finditer(m.da_che):
            buoc.kiem()
            da_giao.add(chuan_bi_danh(muc.group()))
        for alias, goc in aliases.items():
            buoc.kiem()
            if type(alias) is not str or not _BI_DANH.fullmatch(alias) or type(goc) is not str:
                raise loi()
            ma = chuan_bi_danh(alias)
            if ma not in da_giao:
                continue
            if ma in theo_ma and theo_ma[ma] != goc:
                raise loi()
            theo_ma[ma] = goc
    except LoiAnhXa:
        buoc.kiem()
        raise loi() from None
    except Exception:
        # Timer có thể dọn giữa kiểm map và kết luận nghiệp vụ.
        buoc.kiem()
        raise
    else:
        buoc.kiem()
        da_tra = True
        return m, theo_ma
    finally:
        if type(aliases) is dict:
            aliases.clear()
        if not da_tra:
            theo_ma.clear()
        m = goc = None


class _MoChu:
    def __init__(self, buoc, aliases):
        self.buoc, self.aliases = buoc, aliases
        self.so_cho, self.so_ky_tu, self.da_doi = 0, 0, False
        self.so_chu = 0
        self.do_manh = _DoManhBiDanh(aliases, buoc.kiem)

    def dem_chu(self):
        self.buoc.kiem()
        self.so_chu += 1
        if self.so_chu > phong_bi.TRAN_CHUOI_MO:
            raise phong_bi.loi('MASK_QUA_GIOI_HAN')

    def mo(self, chu):
        phan = []
        try:
            self.dem_chu()
            phan, da_xet, cuoi = [], [], 0
            do_dai = len(chu)
            for muc in _VUNG.finditer(chu):
                self.buoc.kiem()
                ma = chuan_bi_danh(muc.group())
                truoc, sau = muc.start() - 1, muc.end()
                while truoc >= 0 and chu[truoc].isspace():
                    if truoc % 2048 == 0:
                        self.buoc.kiem()
                    truoc -= 1
                while sau < len(chu) and chu[sau].isspace():
                    if sau % 2048 == 0:
                        self.buoc.kiem()
                    sau += 1
                if (not _BI_DANH.fullmatch(ma) or ma not in self.aliases
                        or sau < len(chu) and chu[sau] == ']'
                        or truoc >= 0 and chu[truoc] == '['):
                    raise loi()
                do_dai += len(self.aliases[ma]) - len(muc.group())
                phan.extend((chu[cuoi:muc.start()], self.aliases[ma]))
                da_xet.append(muc.span())
                cuoi = muc.end()
                self.so_cho += 1
            if self.so_ky_tu + do_dai > 500000:
                raise phong_bi.loi('MASK_QUA_GIOI_HAN')
            # Mã mất ngoặc, hỏng một ký tự hoặc một mảnh mã không được đoán.
            if self.do_manh.quet(chu, da_xet, ma_mask_roi=True):
                raise loi()
            phan.append(chu[cuoi:])
            moi = ''.join(phan)
            self.so_ky_tu += len(moi)
            if self.so_ky_tu > 500000:
                raise phong_bi.loi('MASK_QUA_GIOI_HAN')
            self.da_doi = self.da_doi or moi != chu
            self.buoc.kiem()
            return moi
        except Exception:
            self.buoc.kiem()
            raise
        finally:
            phan.clear()
            chu = moi = muc = None



def mo_van_ban(chu, buoc):
    """Cửa thuần nội bộ dưới handle R4, không nhận kho/ngăn lịch sử."""
    _m, aliases = kiem_map_ram(buoc)
    mo = None
    try:
        mo = _MoChu(buoc, aliases)
        moi = mo.mo(chu)
        return dict(van_ban_da_mo_che=moi, so_cho_mo=mo.so_cho,
                    bi_danh_khong_ro=[], mo_day_du=True, kiem_tien_ngay=True,
                    trang_thai_ma_yeu_cau='DA_DONG')
    finally:
        aliases.clear()
        if mo is not None:
            mo.buoc = None
            mo.do_manh.kiem = None
        chu = moi = _m = None


def _vi_tri_trich(cu, moi, m, ten, buoc):
    """Tái tính trên gốc đang RAM; không giữ offset bản che làm chứng cứ.

    Dùng vị trí đã ghim khi đúng nguyên văn bản che. Nếu không, chỉ nhận
    câu xuất hiện duy nhất trong gốc. Không phân biệt được thì bỏ tọa độ.
    Dù tìm được vị trí, kết luận kiểm nguyên văn vẫn hạ để hậu kiểm lại.
    """
    buoc.kiem()
    a, b, cau = cu.get('bat_dau'), cu.get('ket_thuc'), moi[ten]
    vi_tri = None
    if (type(a) is int and type(b) is int and 0 <= a < b <= len(m.da_che)
            and m.da_che[a:b] == cu[ten]):
        cac = m.chuyen('da_che', 'goc', a, b)
        if len(cac) == 1 and m.goc[slice(*cac[0])] == cau:
            vi_tri = cac[0]
    if vi_tri is None and cau:
        dau = m.goc.find(cau)
        if dau >= 0 and m.goc.find(cau, dau + 1) < 0:
            vi_tri = (dau, dau + len(cau))
    moi.update(bat_dau=vi_tri[0] if vi_tri else None,
               ket_thuc=vi_tri[1] if vi_tri else None, can_kiem_lai=True)


def _ket_qua(chu, ai, dong, buoc):
    m, aliases = kiem_map_ram(buoc)
    mo, cac_trich = None, []
    du_khoa = True

    def duyet(v):
        nonlocal du_khoa
        try:
            buoc.kiem()
            if type(v) is str:
                return mo.mo(v)
            if type(v) is list:
                return [duyet(t) for t in v]
            if type(v) is dict:
                # Giữ nguyên khóa theo contract; dấu vết alias trong khóa
                # phải hạ cờ đầy đủ, kể cả alias nguyên vẹn đã biết.
                for k in v:
                    mo.dem_chu()
                    if _VUNG.search(k) or mo.do_manh.quet(k, [], ma_mask_roi=True):
                        du_khoa = False
                kq = {k: duyet(t) for k, t in v.items()}
                for ten in ('cau', 'nguyen_van'):
                    if type(v.get(ten)) is str and {'bat_dau', 'ket_thuc'} <= v.keys():
                        cac_trich.append((v, kq, ten))
                return kq
            return v
        finally:
            v = kq = t = k = None


    moi = None
    try:
        mo = _MoChu(buoc, aliases)
        if ai is None:
            van_ban = mo.mo(chu)
        else:
            moi = deepcopy(ai)
            moi['tra_loi'] = van_ban = mo.mo(chu)
            moi['du_lieu'] = duyet(ai['du_lieu'])
            moi['trich_dan'] = duyet(ai['trich_dan'])
            if mo.da_doi:
                for cu, trich, ten in cac_trich:
                    _vi_tri_trich(cu, trich, m, ten, buoc)
                moi['kiem_trich_dan'] = dict(dat=False, loi=[KIEM_LAI])
                moi['trang_thai'] = 'khong_thay_can_cu'
                moi['canh_bao'].append(KIEM_LAI)
            if not dong:
                moi['canh_bao'].append(CHUYEN_QUY_TRINH)
        kq = dict(van_ban_da_mo_che=van_ban, so_cho_mo=mo.so_cho,
                  bi_danh_khong_ro=[], mo_day_du=du_khoa,
                  trang_thai_ma_yeu_cau='DA_DONG')
        return phong_bi.ket_qua_mo(kq, moi)
    finally:
        # Hàm đệ quy cục bộ có cell trỏ chính nó. Ngắt cell chủ động,
        # không để map/handle sống thêm một chu kỳ GC sau khi mở xong.
        duyet = None
        aliases.clear()
        cac_trich.clear()
        if mo is not None:
            mo.buoc = None
            mo.do_manh.kiem = None
        if moi is not None:
            moi.clear()
        chu = ai = van_ban = kq = m = cu = trich = None


class MoCheRAM:
    def __init__(self, *, ram, quyen, cong):
        self.ram, self.quyen, self.cong = ram, quyen, cong

    def mo(self, viec):
        ctx, da_gui = None, False
        try:
            if type(self.ram) is not KhoAnhXaRAM or self.quyen is None:
                raise loi_ram('MASK_ANH_XA_KHONG_CON')
            # Lấy mã từ port quyền trước parse. Đầu vào lỗi/hủy vẫn dọn
            # đúng map của việc đã cấp quyền; mã caller không chọn map.
            ctx = self.quyen.xac_minh(viec, loai='mo_che', ma_yeu_cau=None, thao_tac='ram')
            if type(ctx) is not NguCanhTinCay:
                raise loi_kho('MASK_MA_YEU_CAU')
            ctx = xac_minh(self.quyen, viec, loai='mo_che',
                          ma_yeu_cau=ctx.ma_yeu_cau, thao_tac='ram', kiem_huy=False)
            xong = False
            # Port thoát sau buoc(): bản rõ chờ tại Core chỉ được phát
            # hành sau chốt tiêu thụ nguyên tử của R4, không trước đó.
            with ExitStack() as giao:
                with self.ram.buoc(viec, loai='mo_che', ma_yeu_cau=ctx.ma_yeu_cau) as buoc:
                    bam_vao = _bam(viec, 'mo_che')
                    chu, ma, dong, ai = phong_bi.doc_mo(viec)
                    if ma != ctx.ma_yeu_cau:
                        raise loi_kho('MASK_MA_YEU_CAU')
                    viec.tien_do(10, 'Đang kiểm tra quyền mở che.')
                    if not dong:
                        viec.tien_do(15, CHUYEN_QUY_TRINH)
                    ket = _ket_qua(chu, ai, dong, buoc)
                    ham = getattr(self.cong, 'ban_giao_cuoi', None)
                    if not callable(ham):
                        raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE')
                    raw = phong_bi.json_chu(ket).encode('utf-8')
                    bam = sha256(phong_bi.json_chu([viec.dau_vao, viec.tham_so]).encode('utf-8')).hexdigest()
                    nhan = giao.enter_context(ham(viec, buoc._ctx,
                        bam_dau_vao='sha256:' + bam, han_monotonic=buoc._ban_ghi.han))
                    if not callable(nhan):
                        raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE')
                    buoc.kiem()
                    if _bam(viec, 'mo_che') != bam_vao:
                        raise loi_ram('MASK_DAU_VAO_THAY_DOI')
                    viec.tien_do(100, 'Đã kiểm tra đầy đủ kết quả mở che.')
                    da_gui = True
                    if nhan(raw) is not True:
                        raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE')
                    buoc.kiem()
                    if _bam(viec, 'mo_che') != bam_vao:
                        raise loi_ram('MASK_DAU_VAO_THAY_DOI')
                xong = True
            if not xong:  # Không chấp nhận port nuốt ngoại lệ của bước RAM.
                raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE')
            return ket
        except ChuaRo as exc:
            # Không tin mã/thông điệp tùy ý từ nguồn, không cache bản rõ.
            ma = ctx.ma_luot if type(ctx) is NguCanhTinCay else 'khong-ro'
            _don_ngoai_le(exc)
            raise ChuaRo('mask-mo-' + sha256(ma.encode('utf-8')).hexdigest()) from None
        except ViecDaHuy:
            raise
        except LoiNghiepVu as exc:
            ma = exc.ma
            _don_ngoai_le(exc)
            if ma in {'MASK_MO_CHE_KHONG_DAY_DU', 'MASK_MO_CHE_CHUA_CO_CUA_CORE'}:
                raise loi(ma) from None
            if ma in {'MASK_DAU_VAO', 'MASK_QUA_GIOI_HAN', 'MASK_MA_YEU_CAU'}:
                raise phong_bi.loi(ma) from None
            if ma in {'MASK_ANH_XA_KHONG_CON', 'MASK_CHUOI_CHUA_GHIM',
                          'MASK_CHUOI_DANG_XU_LY', 'MASK_BUOC_DANG_XU_LY',
                          'MASK_DAU_VAO_THAY_DOI', 'MASK_VONG_DOI_KHONG_HOP_LE'}:
                raise loi_ram(ma) from None
            raise loi_kho('MASK_MA_YEU_CAU') from None
        except (LoiDuongTruyen, TimeoutError, ConnectionError) as exc:
            _don_ngoai_le(exc)
            if da_gui:
                raise ChuaRo('mask-mo-' + sha256(ctx.ma_luot.encode('utf-8')).hexdigest()) from None
            raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE') from None
        except Exception as exc:
            _don_ngoai_le(exc)
            raise loi() from None
        finally:
            # Return đã giữ kết quả cho caller; frame lỗi không giữ thêm
            # bản rõ/bytes đầu ra khi SDK giữ ngoại lệ để báo trạng thái.
            ket = raw = chu = ai = nhan = ham = buoc = None
