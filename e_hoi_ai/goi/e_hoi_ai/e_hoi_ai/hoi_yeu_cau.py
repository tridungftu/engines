"""AI-2: yêu cầu có cấu trúc, chỉ Local, một lần hỏi lại khi sai khuôn."""
from datetime import datetime
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import re
import sys
import time
from types import SimpleNamespace

from kho_tri_thuc_sdk.engine import LoiNghiepVu, ViecDaHuy

from .ai_cuc_bo import LocalAIKhongSanSang
from .cau_hinh_may import yeu_cau_cau_hinh
from .cong_ai import CANH_BAO, MA_SO, danh_gia, ghep_khung
from .dto import KHONG_THAY_CAN_CU, MA_DINH_DANH, YeuCauAI, kiem_prompt
from .khuon_json import boc_khuon, doc_json, json_chuan, khop, kiem_khuon


def _loi_dau_vao():
    return LoiNghiepVu("DAU_VAO_KHONG_HOP_LE", "Yêu cầu hỏi AI không đúng cấu trúc dữ liệu phiên bản 1.")


def _doc_yeu_cau(viec):
    du_lieu = viec.dau_vao.get("yeu_cau_ai")
    if not isinstance(du_lieu, dict):
        raise _loi_dau_vao()
    kiem_prompt(du_lieu.get("prompt"))
    bat_buoc = {"phien_ban", "ma_prompt", "phien_ban_prompt", "prompt", "tai_lieu",
                "khuon_tra_loi", "bat_buoc_trich_dan", "model_uu_tien", "chuyen_tiep"}
    if (not bat_buoc <= du_lieu.keys() or type(du_lieu["phien_ban"]) is not int
            or du_lieu["phien_ban"] != 1 or type(du_lieu["bat_buoc_trich_dan"]) is not bool
            or not isinstance(du_lieu["chuyen_tiep"], dict)):
        raise _loi_dau_vao()
    try:
        raw = json_chuan(viec.dau_vao)
        for khoa, tran in (("chuyen_tiep", 64 * 1024), ("khuon_tra_loi", 32 * 1024)):
            if len(json_chuan(du_lieu[khoa])) > tran:
                raise LoiNghiepVu("VUOT_GIOI_HAN", "Dữ liệu chuyển tiếp vượt 64 KiB hoặc khuôn trả lời vượt 32 KiB.")
    except (ValueError, TypeError, RecursionError, OverflowError):
        raise _loi_dau_vao() from None
    yeu_cau = YeuCauAI.tu_viec(SimpleNamespace(
        tham_so=du_lieu, dau_vao={"loai": "van_ban", "van_ban": du_lieu["tai_lieu"]},
    ))
    khuon = du_lieu["khuon_tra_loi"]
    if khuon is not None:
        kiem_khuon(khuon)
    return yeu_cau, du_lieu, "sha256:" + sha256(raw).hexdigest()


def _cac_la(v):
    if isinstance(v, dict):
        return [x for a in v.values() for x in _cac_la(a)]
    if isinstance(v, list):
        return [x for a in v for x in _cac_la(a)]
    return [] if v is None else [v]


def _duoc_dan(v, cac_trich):
    """Đối chiếu cả dữ liệu có kiểu; chỉ chuẩn hóa tiền dạng nhóm 3 số và ngày."""
    text = "true" if v is True else "false" if v is False else str(v)
    if isinstance(v, str):
        if any(v and v in trich for trich in cac_trich):
            return True
        # Ngày trong dữ liệu YYYY-MM-DD, nguồn có thể còn DD/MM/YYYY.
        try:
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
                ngay = datetime.strptime(v, "%Y-%m-%d").strftime("%d/%m/%Y")
                return any(ngay in t for t in cac_trich)
        except ValueError:
            pass
        return False
    if type(v) in (int, float):
        for trich in cac_trich:
            for so in MA_SO.findall(trich):
                # Không coi 1.000 thành 1 hay 100 thành một phần của 1000.
                if re.fullmatch(r"[+-]?\d{1,3}(?:\.\d{3})+", so):
                    so = so.replace(".", "")
                try:
                    if Decimal(so) == Decimal(text):
                        return True
                except InvalidOperation:
                    pass
        return False
    return any(re.search(r"(?<!\w)" + text + r"(?!\w)", t) for t in cac_trich)


def _kiem_tra_loi(phan_hoi, yeu_cau, du_lieu):
    cac_truong, cac_loi = danh_gia(phan_hoi, yeu_cau)
    trich = tuple(dict.fromkeys(t.trich_dan for t in cac_truong))
    loi = list(cac_loi)
    if du_lieu is not None and any(not _duoc_dan(v, trich) for v in _cac_la(du_lieu)):
        loi.append("DU_LIEU_NGOAI_TRICH_DAN")
    if du_lieu and not cac_truong and "THIEU_TRICH_DAN" not in loi:
        loi.append("THIEU_TRICH_DAN")
    return cac_truong, trich, list(dict.fromkeys(loi))


def goi_theo_yeu_cau(viec, cong, *, phien_ban):
    bat_dau = time.perf_counter()
    model = ly_do = ""
    ket_qua_kiem = "CHUA_KIEM"
    du_lieu_vao = viec.dau_vao.get("yeu_cau_ai")
    metadata = {}
    for k in ("ma_prompt", "phien_ban_prompt"):
        v = du_lieu_vao.get(k) if isinstance(du_lieu_vao, dict) else None
        metadata[k] = v if isinstance(v, str) and MA_DINH_DANH.fullmatch(v) else ""
    try:
        yeu_cau, vao, bam = _doc_yeu_cau(viec)
        cau_hinh = yeu_cau_cau_hinh()
        viec.kiem_huy()
        model, ly_do = cong.chon_model(yeu_cau, cau_hinh, kiem_huy=viec.kiem_huy)
        khuon = vao["khuon_tra_loi"]
        khuon_gui = boc_khuon(khuon) if khuon is not None else None
        prompt = ghep_khung(yeu_cau)
        if khuon is not None:
            prompt += ("\nThay đối tượng JSON mẫu bằng {\"du_lieu\": <đối tượng đúng khuôn>, "
                       "\"truong\": [<các giá trị nguyên văn và trích dẫn như trên>]}. "
                       "Mọi giá trị trong du_lieu phải có căn cứ từ các trích dẫn; "
                       "tiền kèm mã tiền tệ, ngày YYYY-MM-DD. Khuôn của du_lieu:\n"
                       + json_chuan(khuon).decode("utf-8"))
        viec.tien_do(10, "Đang gửi yêu cầu tới Local AI.")
        for lan in range(2 if khuon is not None else 1):
            viec.kiem_huy()
            try:
                text = cong.nha_cung_cap["local"].hoi(
                    cau_hinh["local_ai"], model, prompt, kiem_huy=viec.kiem_huy, khuon=khuon_gui,
                )
            except LocalAIKhongSanSang:
                raise LoiNghiepVu(
                    "LOCAL_AI_KHONG_SAN_SANG", "Local AI chưa sẵn sàng. Hãy kiểm tra máy AI và thử lại.",
                    thu_lai_duoc=True,
                ) from None
            viec.kiem_huy()
            try:
                text = text.strip()
                if text.startswith("```json\n") and text.endswith("\n```"):
                    text = text[8:-4]
                phan_hoi = doc_json(text)
            except (ValueError, TypeError, RecursionError, OverflowError):
                phan_hoi = None
            if khuon is None:
                du_lieu = None
                break
            du_lieu = phan_hoi.get("du_lieu") if isinstance(phan_hoi, dict) else None
            if isinstance(du_lieu, dict) and khop(du_lieu, khuon):
                break
            if lan == 1:
                raise LoiNghiepVu("AI_TRA_SAI_KHUON", "Local AI trả dữ liệu sai khuôn sau một lần hỏi lại.")
            viec.tien_do(50, "Dữ liệu chưa đúng khuôn. Đang yêu cầu Local AI trả lại một lần.")
            # Không phản chiếu nội dung phản hồi lỗi vào prompt hoặc nhật ký.
            prompt += "\nLần trước dữ liệu sai khuôn. Hãy trả lại đúng khuôn đã cung cấp, giữ phần trích dẫn nguyên văn."
        if not isinstance(phan_hoi, dict) or not isinstance(phan_hoi.get("truong"), list):
            phan_hoi = None
        cac_truong, cac_trich, loi = _kiem_tra_loi(phan_hoi, yeu_cau, du_lieu)
        co_can_cu = bool(cac_truong) and not loi
        ket_qua_kiem = "KHONG_DAT" if loi else "DAT" if co_can_cu else "KHONG_THAY_CAN_CU"
        viec.tien_do(90, "Đã nhận phản hồi Local AI và kiểm trích dẫn.")
        viec.kiem_huy()
        return {"loai": "tra_loi_ai", "tra_loi_ai": {
            "phien_ban": 1, "trang_thai": "co_can_cu" if co_can_cu else "khong_thay_can_cu",
            "tra_loi": "\n".join(t.gia_tri for t in cac_truong) if co_can_cu else KHONG_THAY_CAN_CU,
            "du_lieu": du_lieu,
            "trich_dan": [{"cau": t, "bat_dau": yeu_cau.van_ban.index(t),
                           "ket_thuc": yeu_cau.van_ban.index(t) + len(t)} for t in cac_trich],
            "kiem_trich_dan": {"dat": not loi, "loi": loi}, "nha_cung_cap": "local",
            "model": model, "ly_do_chon_model": ly_do,
            "ma_prompt": yeu_cau.ma_prompt, "phien_ban_prompt": yeu_cau.phien_ban_prompt,
            "phien_ban_engine": "e_hoi_ai " + phien_ban, "bam_dau_vao": bam,
            "chuyen_tiep": doc_json(json_chuan(vao["chuyen_tiep"])),
            "canh_bao": [CANH_BAO.get(k, "Có dữ liệu không được chứng minh bằng trích dẫn.") for k in loi],
        }}
    except LoiNghiepVu as exc:
        ket_qua_kiem = exc.ma
        raise
    except ViecDaHuy:
        ket_qua_kiem = "HUY"
        raise
    finally:
        print(json.dumps({**metadata, "model": model, "ly_do_chon": ly_do,
                          "thoi_gian_ms": round((time.perf_counter() - bat_dau) * 1000, 3),
                          "ket_qua_kiem": ket_qua_kiem}, ensure_ascii=False), file=sys.stderr)
