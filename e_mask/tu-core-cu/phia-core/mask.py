"""MASK-3D: snapshot → kho RAM của lượt → chốt; chỉ công bố sau commit.

Đây là kênh nội bộ Core, không phải API cho module. Kết nối được tiêm phải
đang rảnh; không lồng vào transaction của caller rồi trả kết quả trước commit.
Không mở kết nối, đọc cấu hình hoặc ghi log. Xung đột được thử tối đa ba lần,
mỗi lần lấy snapshot mới với cùng mã yêu cầu/lượt và đầu vào trong RAM.
Caller giữ mã để phát lại sau mất phản hồi; SQL luôn kiểm lại quyền.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from hashlib import sha256
import json
from threading import Lock
from uuid import UUID, uuid4

from engines.e_mask import che_van_ban
from .kho_mask import LoiKhoMask
from .phien import MaBiMat


class LoiLuotMask(LoiKhoMask):
    """Lỗi cố định; không giữ exception của driver/bộ xử lý."""


class XungDotLuotMask(LoiLuotMask):
    """Chưa công bố kết quả; có thể lấy snapshot mới rồi thử lại."""


class KhoLuot:
    """Cài port Kho bằng snapshot và nhật ký tạm, không có đường ghi CSDL."""

    def __init__(self, snapshot, ma_yeu_cau, *, loai):
        self._ma = str(UUID(str(ma_yeu_cau)))
        self._loai = loai
        self._snapshot = deepcopy(snapshot)
        self._danh_muc = deepcopy(snapshot['danh_muc'])
        self._theo_cum = {che_van_ban.chuan_hoa(m['gia_tri']): m for m in self._danh_muc}
        self._dang_goi = False
        self._da_chay = False
        self._hop_le = False
        self._nhat_ky = dict(cum=[], bi_danh_tam_moi=[], bi_danh_da_dung=[], dong_yeu_cau=False,
                            cum_da_tra=[], bi_danh_da_tra=[])
        self._da_gap = set()

    @contextmanager
    def giao_dich(self):
        if self._dang_goi or self._da_chay:
            raise LoiLuotMask('Lượt xử lý đã được sử dụng.')
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
        if not self._dang_goi or (ma is not None and str(ma) != self._ma):
            raise LoiLuotMask('Yêu cầu không thuộc lượt xử lý.')

    @property
    def nhat_ky(self):
        if not self._hop_le or self._dang_goi:
            raise LoiLuotMask('Lượt xử lý chưa hoàn tất.')
        return deepcopy(self._nhat_ky)

    def tao_yeu_cau(self):
        self._kiem()
        if self._loai != 'che':
            raise LoiLuotMask('Lượt xử lý chưa hợp lệ.')
        return self._ma

    def doc_yeu_cau(self, ma_yeu_cau):
        self._kiem(ma_yeu_cau)
        muc = self._snapshot['yeu_cau']
        if muc is None or muc['trang_thai'] != 'DANG_XU_LY':
            raise LoiLuotMask('Yêu cầu không còn hiệu lực.')
        return deepcopy(muc)

    def liet_ke_dinh_danh(self):
        self._kiem()
        return deepcopy(self._danh_muc)

    def tra_bi_danh(self, gia_tri_chuan):
        self._kiem()
        chuan = che_van_ban.chuan_hoa(gia_tri_chuan)
        bam = sha256(chuan.encode('utf-8')).hexdigest()
        if bam not in self._nhat_ky['cum_da_tra']:
            self._nhat_ky['cum_da_tra'].append(bam)
        muc = self._theo_cum.get(chuan)
        if muc is None:
            da_co = self._snapshot.get('cum_cho_toan_vung', {}).get(bam)
            if da_co is not None:
                # Chỉ nạp cụm vừa được đầu vào cung cấp; giữ nhóm đã có ở 119.
                muc = dict(gia_tri=gia_tri_chuan, nhom=da_co['nhom'],
                           bi_danh=da_co['bi_danh'], nguon='tam')
                self._theo_cum[chuan] = muc
                self._danh_muc.append(muc)
        return None if muc is None else {k: deepcopy(v) for k, v in muc.items() if k != 'gia_tri'}

    def cap_bi_danh_tam(self):
        self._kiem()
        ma = '[[MASKTAM-' + uuid4().hex + ']]'
        self._nhat_ky['bi_danh_tam_moi'].append(ma)
        return ma

    def ghi_cho_duyet(self, gia_tri, nhom, bi_danh, ma_yeu_cau):
        self._kiem(ma_yeu_cau)
        chuan = che_van_ban.chuan_hoa(gia_tri)
        cu = self.tra_bi_danh(chuan)
        if cu is not None:
            if bi_danh != cu['bi_danh'] and bi_danh in self._nhat_ky['bi_danh_tam_moi']:
                self._nhat_ky['bi_danh_tam_moi'].remove(bi_danh)
            self.ghi_nhan_gap_lai(ma_yeu_cau, chuan, cu['nhom'])
            return cu, False
        if bi_danh not in self._nhat_ky['bi_danh_tam_moi']:
            raise LoiLuotMask('Bí danh chưa được cấp trong lượt xử lý.')
        muc = dict(gia_tri=gia_tri, nhom=nhom, bi_danh=bi_danh, nguon='tam', so_lan_gap=1)
        self._theo_cum[chuan] = muc
        self._danh_muc.append(muc)
        self._nhat_ky['cum'].append(dict(gia_tri=gia_tri, nhom=nhom,
                                       bi_danh=bi_danh, chi_gap_lai=False))
        self._da_gap.add(chuan)
        return self.tra_bi_danh(chuan), True

    def ghi_nhan_gap_lai(self, ma_yeu_cau, cum_chuan, nhom):
        self._kiem(ma_yeu_cau)
        chuan = che_van_ban.chuan_hoa(cum_chuan)
        muc = self._theo_cum.get(chuan)
        if muc is None or muc['nhom'] != nhom:
            raise LoiLuotMask('Cụm định danh chưa hợp lệ.')
        if chuan not in self._da_gap:
            self._nhat_ky['cum'].append(dict(gia_tri=muc['gia_tri'], nhom=nhom,
                                           bi_danh=muc['bi_danh'], chi_gap_lai=True))
            self._da_gap.add(chuan)

    def ghi_bi_danh_da_dung(self, ma_yeu_cau, bi_danh):
        self._kiem(ma_yeu_cau)
        self._nhat_ky['bi_danh_da_dung'] = sorted(set(self._nhat_ky['bi_danh_da_dung']) | set(bi_danh))

    def tra_dinh_danh(self, bi_danh_chuan):
        self._kiem()
        chuan = che_van_ban.chuan_bi_danh(bi_danh_chuan)
        if chuan not in self._nhat_ky['bi_danh_da_tra']:
            self._nhat_ky['bi_danh_da_tra'].append(chuan)
        for muc in self._danh_muc:
            if any(b and che_van_ban.chuan_bi_danh(b) == chuan
                   for b in (muc['bi_danh'], muc.get('bi_danh_tam'))):
                return muc['gia_tri']
        return self._snapshot.get('bi_danh_bo_sung', {}).get(chuan)

    def dong_yeu_cau(self, ma_yeu_cau):
        self._kiem(ma_yeu_cau)
        self._nhat_ky['dong_yeu_cau'] = True


class Mask:
    """Điều phối nội bộ; đầu vào danh tính chỉ do Core tin cậy cung cấp."""

    def __init__(self, ket_noi, *, ma: MaBiMat, module: str, phap_nhan_id: UUID,
                 hanh_dong: str, tai_lieu_id: UUID, viec_id: UUID | None = None,
                 the_he: int | None = None):
        if not isinstance(ma, MaBiMat):
            raise ValueError('Cần mã phiên được Core cấp.')
        self._ket_noi = ket_noi
        # Một kết nối chỉ thuộc instance này. Hai lượt có thể xử lý RAM song
        # song, nhưng mỗi RPC phải sở hữu trọn transaction đến lúc commit.
        self._khoa_rpc = Lock()
        self._ma = ma
        self._ctx = (module, UUID(str(phap_nhan_id)), hanh_dong,
                     UUID(str(tai_lieu_id)), None if viec_id is None else UUID(str(viec_id)), the_he)

    def _goi(self, cua, yeu_cau, luot, loai, *du_lieu):
        # Chỉ hai câu SQL hằng; không nối tên cửa/tham số từ đầu vào.
        if cua == 'snapshot':
            sql = 'SELECT mask.snapshot_luot(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        else:
            sql = ('SELECT mask.chot_luot(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                   '%s,%s::jsonb,%s::jsonb)')
        loi_xung_dot = False
        try:
            with self._khoa_rpc:
                if self._ket_noi.info.transaction_status != 0:
                    raise LoiLuotMask('Kết nối đang có giao dịch khác.')
                args = (self._ma.lay_de_truyen(), *self._ctx, yeu_cau, luot, loai, *du_lieu)
                with self._ket_noi.transaction():
                    dong = self._ket_noi.execute(sql, args).fetchone()
                    kq = dong[0]
            return kq
        except Exception as exc:
            loi_xung_dot = getattr(exc, 'sqlstate', None) in ('40001', '40P01', '55P03')
        # Ngoài except: không giữ driver/chuỗi tham số trong cause hoặc context.
        du_lieu = dong = args = None
        if loi_xung_dot:
            raise XungDotLuotMask('Danh mục vừa thay đổi. Cần thử lại lượt xử lý.')
        raise LoiLuotMask('Không thể chốt lượt xử lý định danh.')

    def _chay(self, loai, van_ban, yeu_cau, luot, da_biet=None, dong_viec=False):
        yeu_cau, luot = UUID(str(yeu_cau)), UUID(str(luot))
        for lan in range(3):
            try:
                return self._chay_mot_lan(loai, van_ban, yeu_cau, luot, da_biet, dong_viec)
            except XungDotLuotMask:
                if lan == 2:
                    raise

    def _chay_mot_lan(self, loai, van_ban, yeu_cau, luot, da_biet, dong_viec):
        snapshot = self._goi('snapshot', yeu_cau, luot, loai)
        if snapshot['da_chot']:
            return self._goi('chot', yeu_cau, luot, loai, None, None, None)
        kho = KhoLuot(snapshot, yeu_cau, loai=loai)
        try:
            if loai == 'che':
                kq = che_van_ban.che(van_ban, da_biet, kho)
            else:
                kq = che_van_ban.mo_che(van_ban, str(yeu_cau), kho, dong_viec=dong_viec)
        except Exception:
            pass
        else:
            kq['ma_yeu_cau'] = str(yeu_cau)
            kq['ma_luot'] = str(luot)
            nhat_ky = kho.nhat_ky
            if loai == 'che' and not kq['gui_duoc']:
                nhat_ky['dong_yeu_cau'] = True
            return self._goi('chot', yeu_cau, luot, loai, snapshot['phien_ban'],
                             json.dumps(nhat_ky, ensure_ascii=False),
                             json.dumps(kq, ensure_ascii=False))
        raise LoiLuotMask('Không thể hoàn tất lượt xử lý định danh.')

    def che(self, van_ban, dinh_danh_da_biet=None, *, ma_yeu_cau=None, ma_luot=None):
        return self._chay('che', van_ban, uuid4() if ma_yeu_cau is None else ma_yeu_cau,
                          uuid4() if ma_luot is None else ma_luot, da_biet=dinh_danh_da_biet)

    def mo_che(self, van_ban, ma_yeu_cau, *, dong_viec=False, ma_luot=None):
        return self._chay('mo_che', van_ban, ma_yeu_cau,
                          uuid4() if ma_luot is None else ma_luot, dong_viec=dong_viec)
