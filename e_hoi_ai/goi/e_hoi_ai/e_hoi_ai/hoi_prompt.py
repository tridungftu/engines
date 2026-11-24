"""AI-13: chuyển nguyên prompt của module tới Local, chỉ kiểm khuôn nếu có."""
import json
import sys
import time

from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, ViecDaHuy

from .ai_cuc_bo import LocalAIKhongSanSang
from .dto import GIOI_HAN_KY_TU, MA_DINH_DANH, MA_MODEL, YeuCauAI, kiem_prompt
from .hoi import lay_ngan, yeu_cau_cau_hinh
from .hoi_yeu_cau import _doc_yeu_cau
from .khuon_json import doc_json, json_chuan, khop


def _doc_prompt(viec):
    if viec.dau_vao.get("loai") == "yeu_cau_ai":
        yeu_cau, vao, _ = _doc_yeu_cau(viec)
        # Cả nhóm tham số nguồn bị bỏ qua, kể cả model ưu tiên và mã phiên bản.
        hai_nguon = any(viec.tham_so.get(k) not in (None, "") for k in (
            "ma_prompt", "phien_ban_prompt", "prompt", "model_uu_tien",
        ))
        return yeu_cau, vao["khuon_tra_loi"], hai_nguon
    prompt = viec.tham_so.get("prompt")
    kiem_prompt(prompt)
    ma, phien_ban = (viec.tham_so.get(k) if viec.tham_so.get(k) is not None else ""
                    for k in ("ma_prompt", "phien_ban_prompt"))
    model = viec.tham_so.get("model_uu_tien")
    if isinstance(model, str) and not model.strip():
        model = None
    if (any(not isinstance(v, str) or v and not MA_DINH_DANH.fullmatch(v) for v in (ma, phien_ban))
            or model is not None and (not isinstance(model, str) or not MA_MODEL.fullmatch(model))):
        raise LoiNghiepVu("CAI_DAT_BUOC_KHONG_HOP_LE", "Mã prompt, phiên bản hoặc tên model không hợp lệ.")
    vao = viec.dau_vao
    tai_lieu = vao.get("van_ban_tai_lieu")
    van_ban = (tai_lieu.get("van_ban") if isinstance(tai_lieu, dict) else None
               ) if vao.get("loai") == "van_ban_tai_lieu" else vao.get("van_ban")
    if not isinstance(van_ban, str):
        raise LoiNghiepVu("DAU_VAO_KHONG_HOP_LE", "Tài liệu cần có trường văn bản hợp lệ.")
    if len(prompt) > GIOI_HAN_KY_TU or len(van_ban) > GIOI_HAN_KY_TU:
        raise LoiNghiepVu("VUOT_GIOI_HAN", "Văn bản hoặc prompt dài hơn 500.000 ký tự.")
    return YeuCauAI(van_ban, prompt, ma, phien_ban, model), None, False


def goi_theo_prompt(viec, cong):
    bat_dau = time.perf_counter()
    model = ly_do = ""
    metadata = {}
    ket_qua_kiem = "CHUA_KIEM"
    try:
        yeu_cau, khuon, hai_nguon = _doc_prompt(viec)
        metadata = {k: v for k, v in (("ma_prompt", yeu_cau.ma_prompt),
                                     ("phien_ban_prompt", yeu_cau.phien_ban_prompt))
                    if MA_DINH_DANH.fullmatch(v)}
        noi_dung = yeu_cau.chi_dan + ("\n\n" + yeu_cau.van_ban if yeu_cau.van_ban else "")
        cau_hinh = yeu_cau_cau_hinh(viec)
        viec.kiem_huy()
        viec.tien_do(10, "Đang gửi prompt của module tới Local AI.")
        model, ly_do = cong.chon_model(yeu_cau, cau_hinh, kiem_huy=viec.kiem_huy, ngan=lay_ngan(viec))
        du_lieu_json = ""
        for lan in range(2 if khuon is not None else 1):
            viec.kiem_huy()
            try:
                text = cong.nha_cung_cap["local"].hoi(
                    cau_hinh["local_ai"], model, noi_dung, kiem_huy=viec.kiem_huy,
                    khuon=khuon, ngan_sach_mask=True, prompt_module=True,
                )
            except LocalAIKhongSanSang:
                raise LoiNghiepVu(
                    "LOCAL_AI_KHONG_SAN_SANG", "Local AI chưa sẵn sàng. Hãy kiểm tra máy AI và thử lại.",
                    thu_lai_duoc=True,
                ) from None
            viec.kiem_huy()
            if khuon is None:
                break
            try:
                du_lieu = doc_json(text)
                if khop(du_lieu, khuon):
                    du_lieu_json = json_chuan(du_lieu).decode("utf-8")
                    break
            except (ValueError, TypeError, RecursionError, OverflowError):
                pass
            if lan == 1:
                raise LoiNghiepVu("AI_TRA_SAI_KHUON", "Local AI trả dữ liệu sai khuôn sau một lần hỏi lại.")
            viec.tien_do(50, "Dữ liệu chưa đúng khuôn. Đang gửi lại nguyên prompt một lần.")
        ket_qua_kiem = "DAT"
        viec.tien_do(90, "Đã nhận phản hồi Local AI.")
        viec.kiem_huy()
        return {"loai": "truong", "truong": {
            "tra_loi": text, "du_lieu_json": du_lieu_json,
            "model": model, "ly_do_chon_model": ly_do,
            "noi_dung_gui_ai": noi_dung if viec.tham_so.get("tra_noi_dung_gui") is True else "",
            "canh_bao": ("Đã dùng prompt, tài liệu và model ưu tiên trong phong bì yeu_cau_ai; "
                         "bỏ qua nhóm tham số prompt của bước.") if hai_nguon else "",
        }}
    except LoiNghiepVu as exc:
        ket_qua_kiem = exc.ma
        raise
    except ChuaRo:
        ket_qua_kiem = "CHUA_RO"
        raise
    except ViecDaHuy:
        ket_qua_kiem = "HUY"
        raise
    finally:
        print(json.dumps({**metadata, "model": model, "ly_do_chon": ly_do,
                          "thoi_gian_ms": round((time.perf_counter() - bat_dau) * 1000, 3),
                          "ket_qua_kiem": ket_qua_kiem}, ensure_ascii=False), file=sys.stderr)
