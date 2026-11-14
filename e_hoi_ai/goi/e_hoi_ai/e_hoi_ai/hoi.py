"""Adapter từ ma-nguon/hoi.py: mỗi việc một cấu hình, một lượt Local, một nhật ký."""
import json
import sys
import time

from kho_tri_thuc_sdk.engine import LoiNghiepVu, ViecDaHuy

from .cau_hinh_may import yeu_cau_cau_hinh
from .cong_ai import CongAI
from .dto import MA_DINH_DANH, YeuCauAI


class AdapterHoiAI:
    def __init__(self, cong_ai=None):
        self.cong_ai = CongAI() if cong_ai is None else cong_ai

    def goi(self, viec):
        bat_dau = time.perf_counter()
        yeu_cau = None
        model = ly_do_chon = ""
        ket_qua_kiem = "CHUA_KIEM"
        # Vẫn giữ mã/phiên bản hợp lệ khi prompt thiếu; không phản chiếu trường sai dạng vào log.
        metadata = {}
        for khoa in ("ma_prompt", "phien_ban_prompt"):
            gia_tri = viec.tham_so.get(khoa)
            metadata[khoa] = gia_tri if isinstance(gia_tri, str) and MA_DINH_DANH.fullmatch(gia_tri) else ""
        try:
            yeu_cau = YeuCauAI.tu_viec(viec)
            cau_hinh = yeu_cau_cau_hinh()
            model, ly_do_chon = self.cong_ai.chon_model(yeu_cau, cau_hinh)
            viec.tien_do(10, "Đang gửi yêu cầu tới Local AI.")
            viec.kiem_huy()
            ket_qua = self.cong_ai.goi(
                yeu_cau, cau_hinh, model=model, ly_do_chon=ly_do_chon, kiem_huy=viec.kiem_huy
            )
            ket_qua_kiem = ket_qua.ket_qua_kiem
            viec.tien_do(90, "Đã nhận phản hồi Local AI và kiểm trích dẫn.")
            viec.kiem_huy()
            return ket_qua.phong_bi()
        except LoiNghiepVu as exc:
            ket_qua_kiem = exc.ma
            raise
        except ViecDaHuy:
            ket_qua_kiem = "HUY"
            raise
        finally:
            # Chỉ metadata đã kiểm dạng mã; không ghi lỗi gốc, địa chỉ hoặc nội dung.
            print(json.dumps({
                **metadata,
                "model": model, "ly_do_chon": ly_do_chon,
                "thoi_gian_ms": round((time.perf_counter() - bat_dau) * 1000, 3),
                "ket_qua_kiem": ket_qua_kiem,
            }, ensure_ascii=False), file=sys.stderr)
