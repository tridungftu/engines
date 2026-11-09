"""AI-4b: chuyển bí mật bootstrap G2-21 sang seam RAM của CongAI.

Dùng lại Bootstrap (stdin/handle do Core cấp), CongAI và seam moi_truong/mask.
Bootstrap nhận dòng bi_mat riêng; engine lấy payload RAM một lần trước
readiness, chỉ nhận tên bien_khoa_api của cài đặt, không đọc stdin. Mask do Core tiêm sẵn;
không dựng MaskV2 đọc tệp, không mở két, không nhận credential CSDL.
Tài khoản/ACL thực thuộc G2-33b, CHUA_KIEM trong lát này. Không sửa launcher
AI-4a hay công bố capability Cloud; tích hợp vận hành thuộc AI-5b.
"""

from collections.abc import Mapping
import json

from ...sdk_core.bootstrap import Bootstrap
from ...sdk_core.ngu_canh import _json_cac_cap, _xoa_loi
from .lib.cong_ai import CongAI, cong_ai_settings


class LoiBiMat(RuntimeError):
    def __init__(self):
        super().__init__('AI_BI_MAT_KHONG_HOP_LE')


class BiMatRAM(Mapping):
    """Mapping chỉ đọc, repr ẩn; thu hồi sau drain, không bảo đảm zeroize str.

    Giữ cùng mapping trong CongAI để thu hồi không fallback sang OS env.
    Không serialize/copy ra kho lưu; chỉ provider trong cổng được lấy khóa.
    """

    __slots__ = ('__khoa',)

    def __init__(self):
        # Rỗng vẫn là mapping được tiêm, Local luôn dùng được khi thiếu khóa.
        self.__khoa = {}

    @classmethod
    def tu_bootstrap(cls, bootstrap, settings=None):
        """Chỉ nhận Bootstrap đã xác minh G2-21; không nhận args/env/path."""
        raw = payload = None
        obj = cls()
        try:
            if not isinstance(bootstrap, Bootstrap):
                raise LoiBiMat()
            payload = bootstrap.bi_mat.lay_mot_lan()
            raw = json.loads(payload, object_pairs_hook=_json_cac_cap)
            ten_duoc_phep = cong_ai_settings(settings)['bien_khoa_api']
            # Thiếu/rỗng phải được Core khai rõ bằng {}, không đọc nguồn khác.
            if type(raw) is not dict or len(raw) > 1:
                raise LoiBiMat()
            for ten, khoa in raw.items():
                if (type(ten) is not str or ten != ten_duoc_phep
                        or type(khoa) is not str or not 1 <= len(khoa) <= 4096
                        or khoa != khoa.strip()
                        or any(ord(c) < 33 or ord(c) > 126 for c in khoa)):
                    raise LoiBiMat()
            obj.__khoa.update(raw)
        except Exception as exc:
            obj.thu_hoi()
            _xoa_loi(exc)
        else:
            return obj
        finally:
            if type(raw) is dict:
                raw.clear()
            raw = payload = settings = ten = khoa = ten_duoc_phep = None
        # Ngoài except để không giữ context parser/giá trị đầu vào.
        raise LoiBiMat()

    def __getitem__(self, ten):
        # Không phản chiếu tên khóa lạ trong KeyError/repr/traceback.
        try:
            return self.__khoa[ten]
        except (KeyError, TypeError):
            pass
        raise KeyError('AI_KHONG_CO_KHOA')

    def __iter__(self):
        return iter(self.__khoa)

    def __len__(self):
        return len(self.__khoa)

    def __repr__(self):
        return 'BiMatRAM(<an>)'

    def __reduce__(self):
        raise TypeError('Không serialize BiMatRAM')

    def thu_hoi(self):
        """Gọi sau khi các lượt dùng khóa đã drain; idempotent."""
        self.__khoa.clear()


def tao_cong_ai(settings, *, bi_mat, mask, bo_ghi, nha_cung_cap=None,
                local_transport=None, kiem_xac_suat=None):
    """Bọc CongAI, bắt buộc hai seam RAM kể cả Local hoặc thiếu khóa.

    bo_ghi do caller cấp (BoGhiQuaCore ở runtime); không mở CSDL hoặc tạo
    kho thống kê riêng. Không gọi provider/Mask trong bước dựng cổng.
    """
    try:
        if (not isinstance(bi_mat, BiMatRAM) or mask is None
                or not all(callable(getattr(mask, ten, None)) for ten in
                           ('co_khoa', 'che', 'mo_che', 'ket_thuc'))
                or not all(callable(getattr(bo_ghi, ten, None)) for ten in
                           ('ghi', 'thong_ke'))):
            raise LoiBiMat()
        ten_duoc_phep = cong_ai_settings(settings)['bien_khoa_api']
        if any(ten != ten_duoc_phep for ten in bi_mat):
            raise LoiBiMat()
        return CongAI(settings, bo_ghi=bo_ghi, mask=mask,
                      moi_truong=bi_mat, nha_cung_cap=nha_cung_cap,
                      local_transport=local_transport,
                      kiem_xac_suat=kiem_xac_suat)
    except Exception as exc:
        _xoa_loi(exc)
    raise LoiBiMat()
