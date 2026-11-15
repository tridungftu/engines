"""Seam Local/Cloud; Cloud bản 1 bị khóa cứng, không đọc nguồn bí mật ngoài RAM.

Chuyển cấu trúc Messages/Chat Completions từ ma-nguon/lib/cong_ai.py §7.
Không mang theo env, Mask HTTP, fallback, proxy hoặc định tuyến của bản cũ.
"""
import http.client
import math
import uuid

from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu

from . import ai_cuc_bo
from .dto import GIOI_HAN_KY_TU, MA_MODEL
from .khuon_json import doc_json, json_chuan

BAT_CLOUD = False
HE_THONG = (
    "Chỉ dùng dữ liệu đã che được cung cấp để trả lời. Giữ nguyên mọi bí danh. "
    'Trả duy nhất JSON {"truong": [{"ten": "tra_loi", "gia_tri": "<giá trị nguyên văn>", '
    '"trich_dan": "<nguyên văn chứa giá trị trong nội dung đã che>"}]}. '
    'Không có căn cứ thì trả {"truong": []}, không bịa.'
)
TRAN_PHAN_HOI = 4 * 1024 * 1024


def kiem_van_ban_da_che(phong_bi):
    """Kiểm fail-closed theo LOAI-DU-LIEU-RIENG §2.4, chụp bản sao trong RAM."""
    def sai():
        return LoiNghiepVu("VAN_BAN_DA_CHE_KHONG_HOP_LE", "Cloud chỉ nhận phong bì văn bản đã che phiên bản 1.")

    if not isinstance(phong_bi, dict) or phong_bi.get("loai") != "van_ban_da_che":
        raise sai()
    data = phong_bi.get("van_ban_da_che")
    bat_buoc = {"phien_ban", "van_ban", "ma_yeu_cau", "con_sot", "kiem_tien_ngay", "chuyen_tiep"}
    if (not isinstance(data, dict) or not bat_buoc <= data.keys()
            or type(data["phien_ban"]) is not int or data["phien_ban"] != 1
            or not isinstance(data["van_ban"], str) or not data["van_ban"].strip()
            or not isinstance(data["ma_yeu_cau"], str) or not data["ma_yeu_cau"].strip()
            or not isinstance(data["chuyen_tiep"], dict)):
        raise sai()
    if type(data["con_sot"]) is not list or data["con_sot"] or data["kiem_tien_ngay"] is not True:
        raise LoiNghiepVu("MASK_CHUA_AN_TOAN", "Văn bản chưa qua đủ kiểm tra che định danh, tiền và ngày. Không được gửi Cloud.")
    if len(data["van_ban"]) > GIOI_HAN_KY_TU:
        raise LoiNghiepVu("VUOT_GIOI_HAN", "Văn bản đã che dài hơn 500.000 ký tự.")
    # Mã mở che tuyệt đối không được nằm trong phần văn bản gửi đi.
    if data["ma_yeu_cau"] in data["van_ban"]:
        raise LoiNghiepVu("MA_YEU_CAU_TRONG_NOI_DUNG", "Mã mở che không được xuất hiện trong nội dung gửi Cloud.")
    try:
        chuyen = {**data["chuyen_tiep"], "ma_yeu_cau": data["ma_yeu_cau"]}
        if len(json_chuan(chuyen)) > 64 * 1024:
            raise LoiNghiepVu("VUOT_GIOI_HAN", "Dữ liệu chuyển tiếp sau khi thêm mã mở che vượt 64 KiB.")
        return doc_json(json_chuan(phong_bi))
    except (ValueError, TypeError, RecursionError, OverflowError):
        raise sai() from None


def kiem_bat_cloud():
    if BAT_CLOUD is not True:
        raise LoiNghiepVu("CLOUD_DANG_TAT", "Cloud AI đang tắt ở bản 1. Hãy sử dụng Local AI.")


class NhaCungCapLocal:
    def hoi(self, cau_hinh, model, prompt, *, kiem_huy, khuon=None):
        return ai_cuc_bo.hoi_local(cau_hinh, model, prompt, kiem_huy=kiem_huy, khuon=khuon)


def _gui_json(host, duong, headers, body, timeout):
    """HTTPS cố định; không proxy/env/redirect/retry, không lưu nội dung xuống đĩa."""
    ket_noi = http.client.HTTPSConnection(host, timeout=timeout)
    try:
        try:
            ket_noi.connect()
        except (OSError, http.client.HTTPException):
            raise LoiNghiepVu("CLOUD_KHONG_SAN_SANG", "Không kết nối được Cloud AI. Hãy thử lại sau.", thu_lai_duoc=True) from None
        try:
            ket_noi.request("POST", duong, body=json_chuan(body), headers=headers)
            phan_hoi = ket_noi.getresponse()
            raw = phan_hoi.read(TRAN_PHAN_HOI + 1)
        except (OSError, http.client.HTTPException):
            # Có thể nguồn đã nhận POST. Không tự gửi lại, không dùng mã mở che ra ngoài.
            raise ChuaRo("cloud-" + uuid.uuid4().hex) from None
        if len(raw) > TRAN_PHAN_HOI:
            raise LoiNghiepVu("VUOT_GIOI_HAN", "Phản hồi Cloud AI vượt giới hạn cho phép.")
        if phan_hoi.status == 202:
            raise ChuaRo("cloud-" + uuid.uuid4().hex)
        if phan_hoi.status != 200:
            raise LoiNghiepVu("CLOUD_TU_CHOI", "Cloud AI chưa trả được kết quả hợp lệ.")
        try:
            return doc_json(raw)
        except (ValueError, UnicodeError, RecursionError, OverflowError):
            raise LoiNghiepVu("CLOUD_PHAN_HOI_LOI", "Cloud AI trả phản hồi không hợp lệ.") from None
    finally:
        ket_noi.close()


class NhaCungCapCloud:
    """Khóa chỉ từ tham số khởi tạo; gui_json là seam kiểm bằng Cloud giả trong RAM.

    Cả phương thức provider cũng chỉ nhận phong bì đã che và kiểm BAT_CLOUD.
    Không khởi tạo provider này trong CongAI hoặc handler hai năng lực bản 1.
    """
    PHIEN_BAN_ANTHROPIC = "2026-10-21"  # Giữ mốc trong mã nguồn cũ; chưa kiểm API thật.

    def __init__(self, loai, khoa, *, gui_json=None, timeout=60, max_tokens=4096):
        if (loai not in ("anthropic", "openai") or not isinstance(khoa, str) or not khoa
                or len(khoa) > 512 or any(ord(c) < 33 or ord(c) > 126 for c in khoa)
                or type(timeout) not in (int, float) or not math.isfinite(timeout) or not 0 < timeout <= 600
                or type(max_tokens) is not int or not 1 <= max_tokens <= 32768):
            raise LoiNghiepVu("CAU_HINH_CLOUD_KHONG_HOP_LE", "Tham số khởi tạo Cloud AI không hợp lệ.")
        self.loai, self._khoa = loai, khoa
        self._gui = _gui_json if gui_json is None else gui_json
        self.timeout, self.max_tokens = timeout, max_tokens

    def hoi(self, van_ban_da_che, *, model, kiem_huy=lambda: None):
        phong_bi = kiem_van_ban_da_che(van_ban_da_che)
        kiem_bat_cloud()
        data = phong_bi["van_ban_da_che"]
        if (not isinstance(model, str) or not MA_MODEL.fullmatch(model)
                or data["ma_yeu_cau"] in model):
            raise LoiNghiepVu("CAU_HINH_CLOUD_KHONG_HOP_LE", "Tên model Cloud AI không hợp lệ.")
        # Chỉ lấy văn bản đã che; không serialize phong bì, metadata hoặc chuyen_tiep.
        noi_dung = data["van_ban"]
        if self.loai == "anthropic":
            host, duong = "api.anthropic.com", "/v1/messages"
            headers = {"x-api-key": self._khoa, "anthropic-version": self.PHIEN_BAN_ANTHROPIC,
                       "content-type": "application/json"}
            body = {"model": model, "max_tokens": self.max_tokens, "system": HE_THONG,
                    "messages": [{"role": "user", "content": noi_dung}]}
        else:
            host, duong = "api.openai.com", "/v1/chat/completions"
            headers = {"Authorization": "Bearer " + self._khoa, "Content-Type": "application/json"}
            body = {"model": model, "max_completion_tokens": self.max_tokens,
                    "messages": [{"role": "system", "content": HE_THONG}, {"role": "user", "content": noi_dung}]}
        kiem_huy()
        try:
            phan_hoi = self._gui(host, duong, headers, body, self.timeout)
        except (ChuaRo, LoiNghiepVu):
            raise
        except Exception:
            # Transport tùy biến có thể đã gửi; không phản chiếu ngoại lệ chứa bí mật.
            raise ChuaRo("cloud-" + uuid.uuid4().hex) from None
        finally:
            headers.clear()
        kiem_huy()
        try:
            if self.loai == "anthropic":
                if phan_hoi.get("stop_reason") not in ("end_turn", "stop_sequence"):
                    raise ValueError
                blocks = phan_hoi["content"]
                if not isinstance(blocks, list):
                    raise ValueError
                text = "".join(b["text"] for b in blocks if b.get("type") == "text")
            else:
                muc = phan_hoi["choices"][0]
                if muc.get("finish_reason") != "stop":
                    raise ValueError
                text = muc["message"]["content"]
            if not isinstance(text, str) or not text.strip():
                raise ValueError
            return text
        except (KeyError, IndexError, TypeError, AttributeError, ValueError):
            raise LoiNghiepVu("CLOUD_PHAN_HOI_LOI", "Cloud AI chưa trả câu trả lời đầy đủ và hợp lệ.") from None
