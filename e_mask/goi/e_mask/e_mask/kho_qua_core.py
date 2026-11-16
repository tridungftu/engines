"""KhoNhanDienQuaCore dùng SDK, chỉ trả metadata/null+cờ.

KhoQuaCore/PortKho lịch sử giữ cho hồi quy RAM; không nối ngăn SDK vào
snapshot/nhật ký cũ. R3/R4/R5 thay các consumer này trước khi phát hành.
"""
from __future__ import annotations

from contextlib import contextmanager, ExitStack
from copy import deepcopy
from hashlib import sha256
import json
from re import fullmatch
from typing import Protocol
from uuid import uuid4
from threading import get_ident

from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, ViecDaHuy

from .che_van_ban import _kiem_dinh_danh, chuan_bi_danh, chuan_hoa
from .khoi_tao_ngan import can_bao_dam_core
from .ngan import CauHinhKhongHopLe, NganKhongHopLe, NganXungDot
from .nguon.privacy.core import CATEGORIES
from .quyen_yeu_cau import loi_kho, xac_minh


# Anh chốt 15/11/2026: MASKTAM cho tạm; mã Junsky không dùng họ này.
TIEN_TO_TU_SINH = 'MASK'


class KhoNhanDienQuaCore:
    """Quyền tin cậy trước mỗi truy cập, không snapshot hay map yêu cầu."""
    def __init__(self, *, viec, quyen, loai='che', ma_yeu_cau=None):
        from .kho_ngan import KhoNganBiMat
        self._viec, self._quyen = viec, quyen
        self._loai = loai
        self._ctx = xac_minh(quyen, viec, loai=loai, ma_yeu_cau=ma_yeu_cau)
        if loai != 'che':
            self.tra_dinh_danh(None)
        self._kho = KhoNganBiMat(viec, vung=self._ctx.vung)
        self.da_chot = False

    def __repr__(self):
        return 'KhoNhanDienQuaCore(<ẩn>)'

    def _kiem(self):
        ctx = xac_minh(self._quyen, self._viec, loai=self._loai,
                       ma_yeu_cau=self._ctx.ma_yeu_cau)
        if ctx != self._ctx:
            raise loi_kho('MASK_NGU_CANH_CHUA_XAC_MINH')

    def doc(self, id_dinh_danh):
        self._kiem()
        ket_qua = self._kho.doc(id_dinh_danh)
        self._kiem()
        return ket_qua

    def tim_ung_vien(self, gia_tri, nhom):
        self._kiem()
        ket_qua = self._kho.tim_ung_vien(gia_tri, nhom)
        self._kiem()
        return ket_qua

    def liet_ke_dinh_danh(self):
        # Không nạp danh mục bản rõ cho matcher cũ; R3 chuyển sang ứng viên.
        self._kiem()
        can_bao_dam_core()

    def tra_dinh_danh(self, *args, **kwargs):
        raise LoiNghiepVu('MASK_ANH_XA_KHONG_CON',
            'Không còn dữ liệu mở che của chuỗi này. Anh hãy chạy lại toàn bộ chuỗi che và hỏi AI.') from None

    def ghi_cho_duyet(self, *args, **kwargs):
        self._kiem()
        can_bao_dam_core()

    def ghi_nhan_gap_lai(self, *args, **kwargs):
        self._kiem()
        can_bao_dam_core()

    def chot(self, *args, **kwargs):
        self._kiem()
        can_bao_dam_core()

    @contextmanager
    def giao_dich(self):
        # Mã cũ không được bắt đầu giao dịch snapshot/map bằng ngăn SDK.
        self._kiem()
        can_bao_dam_core()
        yield self


class CongHauKiemTepSDK:
    """B9: chốt metadata qua viec.ngan, một lô thật, không map/kết quả.

    C-P4-03: port tin cậy chot_metadata(..., ghi=...) giữ quyền và dấu
    chống lặp của Core, gọi ghi() đồng bộ đúng một lần rồi xác nhận.
    Callback chỉ có lô metadata; không trả tên, không cấp quyền từ payload.
    Thiếu binding này thì từ chối, không fallback protocol RAM lịch sử.
    """
    def __init__(self, *, cong, quyen, ram):
        self._cong, self._quyen, self._ram = cong, quyen, ram
        self._giao = ExitStack()
        self._nhan = self._bg = self._viec = self._ctx = self._chung_cu = None
        self._da_gui = False

    def __enter__(self):
        return self

    def _don(self):
        with self._ram._khoa:
            if self._bg is not None and self._ram._ban_ghi is self._bg:
                self._ram._don(self._bg)

    def __exit__(self, lop, exc, tb):
        try:
            self._giao.__exit__(lop, exc, tb)
            # Không cho context Core nuốt lỗi/hủy của handler/R4.
            if lop is not None:
                self._don()
                return False
            if not self._da_gui or self._bg is None:
                can_bao_dam_core()
            self._viec.kiem_huy()
            from .kho_anh_xa_ram import _bam, _chu
            from .quyen_yeu_cau import xac_minh_ram
            ctx = xac_minh(self._quyen, self._viec, loai='che',
                           ma_yeu_cau=self._ctx.ma_yeu_cau, thao_tac='tep_ai')
            cuoi = xac_minh_ram(self._quyen, self._viec, phien_ram=self._ram._phien_ram,
                                loai='che', ma_yeu_cau=self._ctx.ma_yeu_cau)
            with self._ram._khoa:
                if (ctx != self._ctx or self._ram._ban_ghi is not self._bg
                        or _chu(cuoi) != _chu(self._bg.ctx)
                        or self._viec.ngu_canh.get('phap_nhan_id') != cuoi.phap_nhan_id
                        or _bam(self._viec, 'che') != self._bg.bam_buoc.get(('che', ctx.ma_luot))
                        or self._ram._dong_ho() >= self._bg.han
                        or (cuoi.han_monotonic is not None and self._ram._dong_ho() >= cuoi.han_monotonic)
                        or self._bg.trang_thai != 'CHO_AI'
                        or self._bg.du_lieu.get('giai_doan_ai') != 'DA_HAU_KIEM'):
                    raise loi_kho('MASK_MA_YEU_CAU')
                if cuoi.han_monotonic is not None and cuoi.han_monotonic < self._bg.han:
                    self._bg.han = cuoi.han_monotonic
                    self._ram._dat_hen(self._bg)
        except BaseException as err:
            self._don()
            from kho_tri_thuc_sdk.engine import LoiDuongTruyen
            if self._da_gui and isinstance(err, (LoiDuongTruyen, TimeoutError, ConnectionError)):
                raise ChuaRo('mask-giao-tep-' + sha256(self._chung_cu).hexdigest()) from None
            raise
        finally:
            self._giao.close()
            self._nhan = self._bg = self._viec = self._ctx = self._chung_cu = None
        return False

    def __getattr__(self, ten):
        return getattr(self._cong, ten)

    def _kiem(self, viec, ctx):
        with self._ram._khoa:
            bg = self._ram._ban_ghi
            buoc = None if bg is None else bg.so_huu
            if buoc is None or buoc._viec.id != viec.id or buoc._ctx.quyen != ctx:
                raise loi_kho('MASK_MA_YEU_CAU')
        buoc.kiem()
        if xac_minh(self._quyen, viec, loai='che', ma_yeu_cau=ctx.ma_yeu_cau,
                    thao_tac='tep_ai') != ctx:
            raise loi_kho('MASK_MA_YEU_CAU')

    def _cach_ly(self, viec, ctx, chung_cu):
        self._kiem(viec, ctx)
        ham = getattr(self._cong, 'ban_giao_tep_cuoi', None)
        if not callable(ham) or self._nhan is not None:
            can_bao_dam_core()
        with self._ram._khoa:
            self._bg = self._ram._ban_ghi
            han = self._bg.han
        self._viec, self._ctx, self._chung_cu = viec, ctx, chung_cu
        self._nhan = self._giao.enter_context(ham(viec, ctx,
            chung_cu=chung_cu, han_monotonic=han))
        if not callable(self._nhan):
            can_bao_dam_core()
        self._kiem(viec, ctx)

    def ban_giao(self, viec, ctx, *, chung_cu, ket_qua):
        from .phong_bi import kiem_tham_chieu_tep
        self._kiem(viec, ctx)
        if self._nhan is None or chung_cu != self._chung_cu or self._da_gui:
            can_bao_dam_core()
        v = json.loads(ket_qua.decode('utf-8'))
        if v['loai'] == 'truong':
            kiem_tham_chieu_tep(v['truong']['tep_da_che'])
        v = None
        self._da_gui = True
        if self._nhan(ket_qua) is not True:
            raise ChuaRo('mask-giao-tep-' + sha256(chung_cu).hexdigest())
        self._kiem(viec, ctx)
        return True

    def chot_metadata(self, viec, ctx, *, chung_cu, metadata):
        from kho_tri_thuc_sdk.engine import NganXungDot as XungDotSDK
        from .khoi_tao_ngan import ngan_cua_viec
        from .phong_bi import _cap

        self._kiem(viec, ctx)
        ham = getattr(self._cong, 'chot_metadata', None)
        if not callable(ham):
            can_bao_dam_core()
        ngan = ngan_cua_viec(viec)
        ds = lenh = None
        dang, da_goi, da_ghi = True, False, False
        luong = get_ident()
        tuong_quan = 'mask-chot-tep-' + sha256(chung_cu + metadata).hexdigest()

        def ghi():
            nonlocal da_goi, da_ghi
            if not dang or da_goi or get_ident() != luong:
                raise loi_kho('MASK_XUNG_DOT')
            da_goi = True
            self._kiem(viec, ctx)
            kho = KhoNhanDienQuaCore(viec=viec, quyen=self._quyen,
                                     ma_yeu_cau=ctx.ma_yeu_cau)
            for m in ds:
                cu = kho.doc(m['id_dinh_danh'])
                if (cu is None or cu['trang_thai'] != 'CHINH_THUC'
                        or any(cu[k] != m[k] for k in m)):
                    raise loi_kho('MASK_XUNG_DOT')
                lenh.append((m['id_dinh_danh'], m['row_version'], cu['so_gap'] + 1))
            self._kiem(viec, ctx)
            # Không chia thành nhiều lô, không ghi bí mật/null/cờ từ doc().
            try:
                if lenh:
                    with ngan.lo() as lo:
                        for ma, phien, so in lenh:
                            self._kiem(viec, ctx)
                            lo.sua('dinh_danh', {'id_dinh_danh': ma},
                                   {'so_gap': so}, row_version=phien)
                        self._kiem(viec, ctx)
            except XungDotSDK:
                raise loi_kho('MASK_XUNG_DOT') from None
            except (ChuaRo, ViecDaHuy):
                raise
            except LoiNghiepVu as exc:
                if exc.ma in {'NGAN_DU_LIEU_SAI', 'NGAN_KHONG_THAY', 'NGAN_CAN_VIEC',
                              'NGAN_LO_QUA_LON', 'NGAN_KHONG_XOA', 'KHOA_CHONG_TRUNG_KHAC_NOI_DUNG'} and not exc.thu_lai_duoc:
                    raise loi_kho() from None
                raise ChuaRo(tuong_quan) from None
            except Exception:
                raise ChuaRo(tuong_quan) from None
            da_ghi = True
            self._kiem(viec, ctx)
            return True

        try:
            if (type(metadata) is not bytes or len(metadata) > 262144
                    or type(chung_cu) is not bytes or len(chung_cu) > 262144):
                raise loi_kho()
            def cam(_):
                raise ValueError
            ds = json.loads(metadata.decode('utf-8'), object_pairs_hook=_cap, parse_constant=cam)
            if type(ds) is not list:
                raise loi_kho()
            if len(ds) > 100:
                raise LoiNghiepVu('MASK_QUA_GIOI_HAN', 'Mỗi lô chỉ nhận tối đa 100 thay đổi.')
            ids, aliases = set(), set()
            for m in ds:
                if (type(m) is not dict or set(m) != {'id_dinh_danh', 'id_bi_danh', 'bi_danh', 'nhom', 'row_version'}
                        or any(type(m[k]) is not str or fullmatch(r'[0-9a-f]{32}|[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', m[k]) is None
                               for k in ('id_dinh_danh', 'id_bi_danh'))
                        or not _la_bi_danh(m['bi_danh']) or m['nhom'] not in CATEGORIES
                        or type(m['row_version']) is not int or m['row_version'] < 1
                        or m['id_dinh_danh'] in ids or chuan_bi_danh(m['bi_danh']) in aliases):
                    raise loi_kho()
                ids.add(m['id_dinh_danh'])
                aliases.add(chuan_bi_danh(m['bi_danh']))
            lenh = []
            # Cách ly cả upload chưa phát hành TRƯỚC lô và tai_tep_ra B7.
            self._cach_ly(viec, ctx, chung_cu)
            try:
                ok = ham(viec, ctx, chung_cu=chung_cu, metadata=metadata, ghi=ghi)
            except (ChuaRo, ViecDaHuy):
                raise
            except Exception:
                if da_ghi:
                    raise ChuaRo(tuong_quan) from None
                raise
            if ok is not True or not da_goi or not da_ghi:
                if da_ghi:
                    raise ChuaRo(tuong_quan)
                can_bao_dam_core()
            self._kiem(viec, ctx)
            return True
        finally:
            dang = False
            if type(ds) is list:
                ds.clear()
            if type(lenh) is list:
                lenh.clear()
            ghi = ham = ds = lenh = metadata = chung_cu = None


class PortKho(Protocol):
    def __call__(self, thao_tac: str, *, ma_yeu_cau: str, ma_luot: str,
                 loai: str, **payload) -> dict:
        """snapshot_luot hoặc chot_luot; không nhận danh tính tự khai.

        chot_luot với nhật ký None chỉ đọc lại lượt đã chốt sau kiểm quyền.
        CAS bao trùm alias/cụm/đếm/tham chiếu/yêu cầu/kết quả. Đã nhận chốt
        chưa trả phải ném ChuaRo; lỗi xác định phải đảm bảo chưa ghi gì.
        """
        ...


def bam_noi_dung(gia_tri):
    try:
        raw = json.dumps(gia_tri, ensure_ascii=True, sort_keys=True,
                         separators=(',', ':'), allow_nan=False).encode('utf-8')
        return sha256(raw).hexdigest()
    except (TypeError, ValueError, UnicodeError, RecursionError):
        raise loi_kho() from None


def _la_bi_danh(gia_tri):
    return isinstance(gia_tri, str) and fullmatch(r'\[\[[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\]\]', gia_tri)


def _kiem_snapshot(snap):
    try:
        if not isinstance(snap, dict) or type(snap.get('da_chot')) is not bool:
            raise ValueError
        if not {'phien_ban', 'yeu_cau'} <= snap.keys() or not isinstance(snap.get('danh_muc'), list):
            raise ValueError
        yc = snap.get('yeu_cau')
        if yc is not None and (not isinstance(yc, dict) or yc.get('trang_thai') not in {'DANG_XU_LY', 'DA_DONG'}):
            raise ValueError
        theo_cum, theo_bi_danh = set(), {}
        for muc in snap['danh_muc']:
            if (not isinstance(muc, dict) or not _la_bi_danh(muc.get('bi_danh'))
                    or muc.get('nguon') not in {'tam', 'chinh_thuc'}
                    or (muc.get('bi_danh_tam') is not None and not _la_bi_danh(muc['bi_danh_tam']))):
                raise ValueError
            _kiem_dinh_danh([{'gia_tri': muc['gia_tri'], 'nhom': muc['nhom']}])
            chuan = chuan_hoa(muc['gia_tri'])
            if chuan in theo_cum:
                raise ValueError
            theo_cum.add(chuan)
            for bi_danh in (muc['bi_danh'], muc.get('bi_danh_tam')):
                if bi_danh:
                    b = chuan_bi_danh(bi_danh)
                    if b in theo_bi_danh and theo_bi_danh[b] != chuan:
                        raise ValueError
                    theo_bi_danh[b] = chuan
        cum_cho = snap.get('cum_cho_toan_vung', {})
        if not isinstance(cum_cho, dict):
            raise ValueError
        for bam, muc in cum_cho.items():
            if (not isinstance(bam, str) or fullmatch(r'[0-9a-f]{64}', bam) is None
                    or not isinstance(muc, dict) or set(muc) != {'nhom', 'bi_danh', 'nguon'}
                    or not isinstance(muc['nhom'], str) or muc['nhom'] not in CATEGORIES
                    or not _la_bi_danh(muc['bi_danh']) or muc['nguon'] != 'tam'):
                raise ValueError
        bo_sung = snap.get('bi_danh_bo_sung', {})
        if (not isinstance(bo_sung, dict)
                or any(not _la_bi_danh(k) or not isinstance(v, str) or not v for k, v in bo_sung.items())):
            raise ValueError
        tam_duoc_dung = snap.get('bi_danh_tam_duoc_dung', [])
        if not isinstance(tam_duoc_dung, list) or any(not _la_bi_danh(b) for b in tam_duoc_dung):
            raise ValueError
    except (KeyError, TypeError, ValueError):
        raise loi_kho() from None


class KhoQuaCore:
    def __init__(self, *, goi_kho=None, quyen=None, viec=None, loai='che',
                 ma_yeu_cau=None, bam_dau_vao, kho_tam=None):
        if not callable(goi_kho):
            raise loi_kho('MASK_KHO_CHUA_NOI')
        self._ngu_canh = xac_minh(quyen, viec, loai=loai, ma_yeu_cau=ma_yeu_cau)
        self._ma, self._luot = self._ngu_canh.ma_yeu_cau, self._ngu_canh.ma_luot
        self._loai, self._goi_kho = loai, goi_kho
        self._quyen, self._viec = quyen, viec
        if kho_tam is None:
            raise loi_kho('MASK_KHO_CHUA_NOI')
        self._kho_tam = kho_tam
        self._bam_dau_vao = bam_dau_vao
        self._bam_chot = None
        self._dau = self._ghi_dau(1)
        self._snapshot = deepcopy(self._goi('snapshot_luot'))
        _kiem_snapshot(self._snapshot)
        self.da_chot = self._snapshot['da_chot']
        if self._dau['trang_thai'] == 4 and not self.da_chot and not self._snapshot.get('da_phuc_hoi'):
            raise loi_kho('MASK_XUNG_DOT')
        self._danh_muc = deepcopy(self._snapshot['danh_muc'])
        self._tam_duoc_dung = {chuan_bi_danh(b) for b in self._snapshot.get('bi_danh_tam_duoc_dung', [])}
        # Cụm chờ của yêu cầu khác vẫn dùng để phát hiện, nhưng không tái dùng
        # bí danh của họ. Mỗi yêu cầu sinh bí danh tạm riêng cho cùng một cụm.
        self._theo_cum = {chuan_hoa(m['gia_tri']): m for m in self._danh_muc
                         if m['nguon'] == 'chinh_thuc' or chuan_bi_danh(m['bi_danh']) in self._tam_duoc_dung}
        self._dang_goi = self._da_chay = self._hop_le = self._can_hoi_lai = False
        self._nhat_ky = dict(cum=[], bi_danh_tam_moi=[], bi_danh_da_dung=[], dong_yeu_cau=False,
                            cum_da_tra=[], bi_danh_da_tra=[])
        self._da_gap = set()

    def __repr__(self):
        return 'KhoQuaCore(<ẩn>)'

    def _ghi_dau(self, trang_thai):
        return self._kho_tam.ghi(vung=self._ngu_canh.vung, ma_luot=self._luot,
                                ma_yeu_cau=self._ma, bam_dau_vao=self._bam_dau_vao,
                                trang_thai=trang_thai, bam_chot=self._bam_chot)

    def _goi(self, thao_tac, **payload):
        ngu_canh = xac_minh(self._quyen, self._viec, loai=self._loai, ma_yeu_cau=self._ma,
                           thao_tac=('snapshot' if thao_tac == 'snapshot_luot'
                                     else 'doc_lai' if payload.get('nhat_ky') is None else 'chot'))
        if ngu_canh != self._ngu_canh:
            raise loi_kho('MASK_NGU_CANH_CHUA_XAC_MINH')
        try:
            return self._goi_kho(thao_tac, ma_yeu_cau=self._ma,
                                 ma_luot=self._luot, loai=self._loai, **payload)
        except ChuaRo:
            try:
                self._dau = self._ghi_dau(3)
            except Exception:
                # Nguồn đã nhận việc: lỗi ghi dấu không được làm mất CHUA_RO.
                pass
            # Dùng mã từ khóa lượt đã băm, không chuyển câu/mã tùy ý của nguồn.
            raise ChuaRo('mask-' + self._dau['tuong_quan']) from None
        except ViecDaHuy:
            raise
        except (NganXungDot, NganKhongHopLe, CauHinhKhongHopLe) as exc:
            raise LoiNghiepVu(exc.ma, exc.thong_diep,
                             thu_lai_duoc=exc.thu_lai_duoc) from None
        except Exception as exc:
            ma = getattr(exc, 'ma', None)
        for lop in (NganKhongHopLe, CauHinhKhongHopLe):
            if ma == lop.ma:
                raise LoiNghiepVu(lop.ma, lop.thong_diep, thu_lai_duoc=lop.thu_lai_duoc) from None
        raise loi_kho(ma) from None

    def chot(self, ket_qua=None):
        if self._can_hoi_lai and not self.da_chot:
            snap = self._goi('snapshot_luot')
            _kiem_snapshot(snap)
            self.da_chot = snap['da_chot']
            if snap.get('da_phuc_hoi'):
                self._snapshot = deepcopy(snap)
        if self.da_chot:
            # Đọc lại từ port có kiểm quyền; không lấy kết quả từ JSON/snapshot.
            kq = self._goi('chot_luot', phien_ban=None, nhat_ky=None, ket_qua=None)
        else:
            nhat_ky = self.nhat_ky
            if not isinstance(ket_qua, dict):
                raise loi_kho()
            kq = deepcopy(ket_qua)
            kq.update(ma_yeu_cau=self._ma, ma_luot=self._luot)
            if self._loai == 'che' and kq.get('gui_duoc') is not True:
                raise loi_kho()
            self._bam_chot = bam_noi_dung([nhat_ky, kq])
            self._dau = self._ghi_dau(2)
            self._can_hoi_lai = True
            kq = self._goi('chot_luot', phien_ban=self._snapshot['phien_ban'],
                           nhat_ky=nhat_ky, ket_qua=kq)
        if (not isinstance(kq, dict) or kq.get('ma_yeu_cau') != self._ma
                or kq.get('ma_luot') != self._luot):
            raise loi_kho()
        self.da_chot = True
        self._ghi_dau(4)
        return deepcopy(kq)

    @contextmanager
    def giao_dich(self):
        if self.da_chot or self._dang_goi or self._da_chay:
            raise loi_kho()
        self._dang_goi = self._da_chay = True
        try:
            yield self
            self._hop_le = True
        finally:
            self._dang_goi = False
            if not self._hop_le:
                self._nhat_ky = None
                self._theo_cum.clear()
                self._danh_muc.clear()

    def _kiem(self, ma=None):
        if not self._dang_goi or (ma is not None and ma != self._ma):
            raise loi_kho('MASK_MA_YEU_CAU')

    @property
    def nhat_ky(self):
        if not self._hop_le or self._dang_goi:
            raise loi_kho()
        return deepcopy(self._nhat_ky)

    def tao_yeu_cau(self):
        self._kiem()
        if self._loai != 'che':
            raise loi_kho()
        return self._ma

    def doc_yeu_cau(self, ma_yeu_cau):
        self._kiem(ma_yeu_cau)
        muc = self._snapshot['yeu_cau']
        if muc is None or muc['trang_thai'] != 'DANG_XU_LY':
            raise loi_kho('MASK_MA_YEU_CAU')
        return deepcopy(muc)

    def liet_ke_dinh_danh(self):
        self._kiem()
        return deepcopy(self._danh_muc)

    def tra_bi_danh(self, gia_tri_chuan):
        self._kiem()
        chuan = chuan_hoa(gia_tri_chuan)
        bam = sha256(chuan.encode('utf-8')).hexdigest()
        if bam not in self._nhat_ky['cum_da_tra']:
            self._nhat_ky['cum_da_tra'].append(bam)
        muc = self._theo_cum.get(chuan)
        if muc is None:
            da_co = self._snapshot.get('cum_cho_toan_vung', {}).get(bam)
            if da_co is not None and chuan_bi_danh(da_co['bi_danh']) in self._tam_duoc_dung:
                muc = dict(gia_tri=gia_tri_chuan, nhom=da_co['nhom'],
                           bi_danh=da_co['bi_danh'], nguon=da_co['nguon'])
                self._theo_cum[chuan] = muc
                self._danh_muc.append(muc)
        return None if muc is None else {k: deepcopy(v) for k, v in muc.items() if k != 'gia_tri'}

    def cap_bi_danh_tam(self):
        self._kiem()
        ma = '[[' + TIEN_TO_TU_SINH + 'TAM-' + uuid4().hex + ']]'
        if not _la_bi_danh(ma):
            raise loi_kho()
        self._nhat_ky['bi_danh_tam_moi'].append(ma)
        return ma

    def ghi_cho_duyet(self, gia_tri, nhom, bi_danh, ma_yeu_cau):
        self._kiem(ma_yeu_cau)
        _kiem_dinh_danh([{'gia_tri': gia_tri, 'nhom': nhom}])
        chuan = chuan_hoa(gia_tri)
        cu = self.tra_bi_danh(chuan)
        if cu is not None:
            if bi_danh != cu['bi_danh'] and bi_danh in self._nhat_ky['bi_danh_tam_moi']:
                self._nhat_ky['bi_danh_tam_moi'].remove(bi_danh)
            self.ghi_nhan_gap_lai(ma_yeu_cau, chuan, cu['nhom'])
            return cu, False
        if bi_danh not in self._nhat_ky['bi_danh_tam_moi']:
            raise loi_kho()
        da_cho = (any(chuan_hoa(m['gia_tri']) == chuan for m in self._snapshot['danh_muc'])
                  or sha256(chuan.encode('utf-8')).hexdigest() in self._snapshot.get('cum_cho_toan_vung', {}))
        muc = dict(gia_tri=gia_tri, nhom=nhom, bi_danh=bi_danh, nguon='tam', so_lan_gap=1)
        self._theo_cum[chuan] = muc
        self._danh_muc.append(muc)
        self._nhat_ky['cum'].append(dict(gia_tri=gia_tri, nhom=nhom,
                                       bi_danh=bi_danh, chi_gap_lai=False))
        self._da_gap.add(chuan)
        return self.tra_bi_danh(chuan), not da_cho

    def ghi_nhan_gap_lai(self, ma_yeu_cau, cum_chuan, nhom):
        self._kiem(ma_yeu_cau)
        chuan = chuan_hoa(cum_chuan)
        muc = self._theo_cum.get(chuan)
        if muc is None or muc['nhom'] != nhom:
            raise loi_kho()
        if chuan not in self._da_gap:
            self._nhat_ky['cum'].append(dict(gia_tri=muc['gia_tri'], nhom=nhom,
                                           bi_danh=muc['bi_danh'], chi_gap_lai=True))
            self._da_gap.add(chuan)

    def ghi_bi_danh_da_dung(self, ma_yeu_cau, bi_danh):
        self._kiem(ma_yeu_cau)
        chinh_thuc = {chuan_bi_danh(m['bi_danh']) for m in self._danh_muc if m['nguon'] == 'chinh_thuc'}
        duoc_dung = chinh_thuc | self._tam_duoc_dung | {chuan_bi_danh(b) for b in self._nhat_ky['bi_danh_tam_moi']}
        if any(not _la_bi_danh(b) or chuan_bi_danh(b) not in duoc_dung for b in bi_danh):
            raise loi_kho()
        self._nhat_ky['bi_danh_da_dung'] = sorted(set(self._nhat_ky['bi_danh_da_dung']) | set(bi_danh))

    def tra_dinh_danh(self, bi_danh_chuan):
        self._kiem()
        chuan = chuan_bi_danh(bi_danh_chuan)
        if chuan not in self._nhat_ky['bi_danh_da_tra']:
            self._nhat_ky['bi_danh_da_tra'].append(chuan)
        gia_tri = None
        for muc in self._danh_muc:
            if (muc['nguon'] == 'chinh_thuc' and chuan_bi_danh(muc['bi_danh']) == chuan
                    or chuan in self._tam_duoc_dung and any(b and chuan_bi_danh(b) == chuan
                        for b in (muc['bi_danh'], muc.get('bi_danh_tam')))):
                gia_tri = muc['gia_tri']
                break
        if gia_tri is None and chuan in self._tam_duoc_dung:
            gia_tri = self._snapshot.get('bi_danh_bo_sung', {}).get(chuan)
        return gia_tri

    def dong_yeu_cau(self, ma_yeu_cau):
        self._kiem(ma_yeu_cau)
        self._nhat_ky['dong_yeu_cau'] = True
