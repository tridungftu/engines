"""SDK engine chỉ giữ lease và kênh IPC tới Core, không nhận DB/SQL.

Bootstrap cấp kenh_core.goi(operation, giu_viec, **payload), là transport
sang tiến trình Core. Core xác minh lease/quyền và gắn nguồn G2-10/14 ở mỗi
lời gọi; kiểm thời gian cục bộ chỉ là chặn sớm, không thay kiểm phía Core.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone

from ..core.viec import GiuViec
from . import kenh_khung as k
from .ngu_canh import _xoa_loi


_LOI_OCR = {
    'OCR_LUOT_DAU_VAO': 400, 'OCR_LUOT_DANG_BI_CHAN': 409,
    'OCR_LUOT_XUNG_DOT': 409, 'OCR_LUOT_GIAO_DICH': 409,
    'OCR_LUOT_THAT_BAI': 500, '42501': 403,
}


class LoiEngine(RuntimeError):
    def __init__(self, ma='ENGINE_CORE'):
        self.ma = ma
        self.http_status = _LOI_OCR.get(ma, k.MA_LOI_HTTP.get(ma,
            409 if ma == 'VIEC_MAT_LEASE' else 503))
        self.thu_lai_duoc = False
        super().__init__(ma)


class KenhCore(ABC):
    """Kiểu kênh do bootstrap Core cấp; adapter IPC triển khai goi.

    Không bọc callable tùy ý do engine đưa vào. IPC thật thuộc G2-21/22.
    Với OCR, khoa là metadata header chống trùng, không phải trường DTO.
    Adapter giữ nguyên tên ocr.* và chỉ trả giữ/chốt sau commit của Core.
    """

    __slots__ = ()

    @abstractmethod
    def goi(self, operation, giu_viec, **payload):
        raise NotImplementedError

    def __repr__(self):
        return 'KenhCore(<an>)'

    def __reduce__(self):
        raise TypeError('Không serialize KenhCore')


class SDKEngine:
    __slots__ = ('__giu', '__kenh', '__dong_ho')

    def __init__(self, giu_viec, *, kenh_core, dong_ho=None):
        if not isinstance(giu_viec, GiuViec) or not isinstance(kenh_core, KenhCore):
            raise TypeError('Cần GiuViec và kênh Core')
        self.__giu, self.__kenh = giu_viec, kenh_core
        self.__dong_ho = dong_ho or (lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return 'SDKEngine(<an>)'

    def __reduce__(self):
        raise TypeError('Không serialize SDKEngine')

    def _goi(self, operation, **payload):
        if self.__giu.giu_den <= self.__dong_ho():
            raise LoiEngine('VIEC_MAT_LEASE')
        ma = 'ENGINE_CORE'
        try:
            return self.__kenh.goi(operation, self.__giu, **payload)
        except Exception as exc:
            if getattr(exc, 'ma', None) == 'VIEC_MAT_LEASE':
                ma = 'VIEC_MAT_LEASE'
            _xoa_loi(exc)
        finally:
            payload = None
        raise LoiEngine(ma) from None

    def doc_dau_vao(self):
        return self._goi('doc_dau_vao')

    def _goi_ocr(self, operation, **payload):
        ma = 'OCR_LUOT_DAU_VAO'
        data = ket_qua = khoa = None
        try:
            data = k.kiem_dto_ocr(operation, payload)
            if self.__giu.giu_den <= self.__dong_ho():
                raise LoiEngine('VIEC_MAT_LEASE')
            if operation in k.OPERATION_OCR_GHI:
                # Cùng lease/đối tượng/CAS dùng lại khóa qua retry, dựng lại SDK
                # và heartbeat. Không dùng hạn giữ, UUID ngẫu nhiên hay bộ đếm RAM.
                cha = k._json(dict(viec_id=str(self.__giu.viec_id),
                    lan_thu_id=str(self.__giu.lan_thu_id), the_he=self.__giu.the_he,
                    doi_tuong=data.get('ma_tuong_quan', data.get('bam_noi_dung'))))
                khoa = k.dan_khoa_con(cha, operation, data.get('phien_ban', 1))
                cha = None
            ma = 'ENGINE_CORE'
            ket_qua = self.__kenh.goi(operation, self.__giu, khoa=khoa, **data)
            ma = 'PHAN_HOI_SAI_CONTRACT'
            ket_qua = k.kiem_dto_ocr(operation, ket_qua, phan_hoi=True)
            if (operation == 'ocr.chot_luot'
                    and ket_qua['trang_thai'] != data['ket_qua']):
                raise k.LoiKenh(ma)
            return ket_qua
        except Exception as exc:
            code = getattr(exc, 'ma', None)
            if type(code) is str:
                if code in _LOI_OCR or code == 'VIEC_MAT_LEASE':
                    ma = code
                elif ma == 'ENGINE_CORE' and code in k.MA_LOI_HTTP:
                    ma = 'VIEC_MAT_LEASE' if code == 'MAT_LEASE' else code
            _xoa_loi(exc)
        finally:
            payload = data = ket_qua = khoa = None
        raise LoiEngine(ma) from None

    def ocr_giu_luot(self, *, bam_noi_dung, so_trang):
        """Giữ lượt, trả mã tương quan và phien_ban Core cấp để chốt CAS.

        Không tự thử lại khi mất phản hồi.
        """
        return self._goi_ocr('ocr.giu_luot', bam_noi_dung=bam_noi_dung, so_trang=so_trang)

    def ocr_chot_luot(self, *, ma_tuong_quan, ket_qua, phien_ban):
        """Chốt bằng phien_ban Core trả từ giữ/đọc lượt, không tự tăng phiên bản."""
        return self._goi_ocr('ocr.chot_luot', ma_tuong_quan=ma_tuong_quan,
                             ket_qua=ket_qua, phien_ban=phien_ban)

    def ocr_doc_luot(self, *, bam_noi_dung):
        """Đọc trạng thái và phien_ban nguyên hiện có theo DTO chung.

        khong_co nhận phien_ban null hoặc bỏ trường, không tự tạo phiên bản.
        Kết quả đọc không cấp quyền gửi nhận dạng.
        """
        return self._goi_ocr('ocr.doc_luot', bam_noi_dung=bam_noi_dung)

    def mo_doc(self, tep_id):
        # Core đối chiếu tệp với đầu vào được cấp cho chính lease này.
        return self._goi('mo_doc', tep_id=tep_id)

    def ghi_ket_qua(self, *, luong, ten, du_lieu, revision_tep_truoc):
        # Không có tai_lieu/module/actor/engine/version tự khai trên API.
        truong = {'bien_the', 'ma_contract', 'phien_ban_contract',
                  'trang_thai', 'ly_do', 'revision_truoc', 'nguon'}
        if (not isinstance(du_lieu, dict) or not truong <= set(du_lieu)
                or set(du_lieu) - truong - {'goc_id'}):
            raise ValueError('Trường kết quả ngoài phạm vi')
        data = dict(du_lieu)
        return self._goi('ghi_ket_qua', luong=luong, ten=ten, du_lieu=data,
                         revision_tep_truoc=revision_tep_truoc)

    def heartbeat(self, *, lease_giay=120):
        if type(lease_giay) is not int or not 1 <= lease_giay <= 3600:
            raise ValueError('Lease ngoài giới hạn')
        moi = self._goi('heartbeat', lease_giay=lease_giay)
        cu = self.__giu
        # Chỉ gia hạn cùng lease; không cho kênh đổi việc/thế hệ/danh tính.
        if (not isinstance(moi, GiuViec) or any(getattr(moi, k) != getattr(cu, k)
                for k in ('viec_id', 'buoc_viec_id', 'lan_thu_id', 'phap_nhan_id',
                          'module', 'hanh_dong', 'instance_id', 'the_he'))
                or moi.ma is not cu.ma or moi.giu_den <= self.__dong_ho()):
            raise LoiEngine('VIEC_MAT_LEASE')
        self.__giu = moi
        return True
