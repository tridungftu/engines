"""DTO chuyển từ ma-nguon/dto.py và lib/cong_ai.py sang hợp đồng SDK 2.0."""
from dataclasses import dataclass
import re

from kho_tri_thuc_sdk.engine import LoiNghiepVu

MA_DINH_DANH = re.compile(r"[A-Za-z0-9_.:-]{1,200}")
MA_MODEL = re.compile(r"[A-Za-z0-9._:/-]{1,200}")
GIOI_HAN_KY_TU = 500_000
KHONG_THAY_CAN_CU = "không thấy căn cứ"


def kiem_prompt(prompt):
    """Giữ quy tắc kiem_prompt của lõi cũ; không có prompt mặc định."""
    if not isinstance(prompt, str) or not prompt.strip():
        raise LoiNghiepVu(
            "THIEU_PROMPT", "Chức năng chưa có prompt. Hãy nhờ quản trị viên module bổ sung."
        )


@dataclass(frozen=True)
class YeuCauAI:
    van_ban: str
    chi_dan: str
    ma_prompt: str
    phien_ban_prompt: str
    model_uu_tien: str | None = None

    @classmethod
    def tu_viec(cls, viec):
        tham_so = viec.tham_so
        prompt = tham_so.get("prompt")
        kiem_prompt(prompt)
        ma, phien_ban = tham_so.get("ma_prompt"), tham_so.get("phien_ban_prompt")
        model = tham_so.get("model_uu_tien")
        if isinstance(model, str) and not model.strip():
            model = None
        if (not isinstance(ma, str) or not MA_DINH_DANH.fullmatch(ma)
                or not isinstance(phien_ban, str) or not MA_DINH_DANH.fullmatch(phien_ban)
                or (model is not None and (not isinstance(model, str)
                                          or not MA_MODEL.fullmatch(model)))):
            raise LoiNghiepVu(
                "CAI_DAT_BUOC_KHONG_HOP_LE", "Mã prompt, phiên bản hoặc tên model không hợp lệ."
            )
        dau_vao = viec.dau_vao
        van_ban = dau_vao.get("van_ban")
        if dau_vao.get("loai") == "van_ban_tai_lieu":
            tai_lieu = dau_vao.get("van_ban_tai_lieu")
            van_ban = tai_lieu.get("van_ban") if isinstance(tai_lieu, dict) else None
        if not isinstance(van_ban, str):
            raise LoiNghiepVu("DAU_VAO_KHONG_HOP_LE", "Tài liệu cần có trường văn bản hợp lệ.")
        # SDK đợt 1 chỉ áp trần ký tự cho loại gốc van_ban, chưa áp cho loại riêng.
        if len(van_ban) > GIOI_HAN_KY_TU or len(prompt) > GIOI_HAN_KY_TU:
            raise LoiNghiepVu("VUOT_GIOI_HAN", "Văn bản hoặc prompt dài hơn 500.000 ký tự.")
        return cls(van_ban, prompt, ma, phien_ban, model)


@dataclass(frozen=True)
class TruongAI:
    ten: str
    gia_tri: str
    trich_dan: str


@dataclass(frozen=True)
class KetQuaAI:
    tra_loi: str
    co_can_cu: bool
    trich_dan: tuple[str, ...]
    model: str
    ly_do_chon_model: str
    ket_qua_kiem: str
    canh_bao: tuple[str, ...] = ()

    def phong_bi(self):
        # Cảnh báo nằm trong trường trả lời để hiện được ở Core.
        tra_loi = self.tra_loi
        if self.canh_bao:
            tra_loi += "\nCảnh báo: " + " ".join(self.canh_bao)
        return {"loai": "truong", "truong": {
            "tra_loi": tra_loi, "co_can_cu": self.co_can_cu,
            "trich_dan": "\n".join(self.trich_dan), "model": self.model,
            "ly_do_chon_model": self.ly_do_chon_model,
        }}
