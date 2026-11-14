"""Khung AI-6, chưa đăng ký năng lực: chỉ kiểm bằng Cloud giả trong bộ nhớ."""
from hashlib import sha256

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .cong_ai import CANH_BAO, danh_gia, doc_json_tra_loi
from .dto import KHONG_THAY_CAN_CU, MA_DINH_DANH, YeuCauAI
from .khuon_json import doc_json, json_chuan
from .nha_cung_cap import kiem_bat_cloud, kiem_van_ban_da_che


def hoi_cloud(van_ban_da_che, *, nha_cung_cap, model, ma_prompt, phien_ban_prompt,
              phien_ban_engine, kiem_huy=lambda: None):
    """Văn bản đã che phải chứa cả yêu cầu đã qua Mask; không nhận prompt thô.

    ma_prompt/phiên bản chỉ ở kết quả nội bộ. Bản 1 luôn trả CLOUD_DANG_TAT;
    test thay cờ trong bộ nhớ và tiêm transport giả, không bật Cloud vận hành.
    """
    phong_bi = kiem_van_ban_da_che(van_ban_da_che)
    kiem_bat_cloud()
    if any(not isinstance(v, str) or not MA_DINH_DANH.fullmatch(v)
           for v in (ma_prompt, phien_ban_prompt, phien_ban_engine)):
        raise LoiNghiepVu("CAU_HINH_CLOUD_KHONG_HOP_LE", "Mã prompt hoặc phiên bản Cloud AI không hợp lệ.")
    data = phong_bi["van_ban_da_che"]
    kiem_huy()
    text = nha_cung_cap.hoi(phong_bi, model=model, kiem_huy=kiem_huy)
    kiem_huy()
    yeu_cau = YeuCauAI(data["van_ban"], "", ma_prompt, phien_ban_prompt)
    truong, loi = danh_gia(doc_json_tra_loi(text), yeu_cau)
    trich = tuple(dict.fromkeys(t.trich_dan for t in truong))
    co_can_cu = bool(truong) and not loi
    return {"loai": "tra_loi_ai", "tra_loi_ai": {
        "phien_ban": 1, "trang_thai": "co_can_cu" if co_can_cu else "khong_thay_can_cu",
        "tra_loi": "\n".join(t.gia_tri for t in truong) if co_can_cu else KHONG_THAY_CAN_CU,
        "du_lieu": None,
        "trich_dan": [{"cau": t, "bat_dau": data["van_ban"].index(t),
                       "ket_thuc": data["van_ban"].index(t) + len(t)} for t in trich],
        "kiem_trich_dan": {"dat": not loi, "loi": list(loi)}, "nha_cung_cap": "cloud",
        "model": model, "ly_do_chon_model": "khung_cloud_AI_6",
        "ma_prompt": ma_prompt, "phien_ban_prompt": phien_ban_prompt,
        "phien_ban_engine": "e_hoi_ai " + phien_ban_engine,
        "bam_dau_vao": "sha256:" + sha256(json_chuan(phong_bi)).hexdigest(),
        "chuyen_tiep": doc_json(json_chuan({**data["chuyen_tiep"], "ma_yeu_cau": data["ma_yeu_cau"]})),
        "canh_bao": [CANH_BAO[k] for k in loi],
    }}
