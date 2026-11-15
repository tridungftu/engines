"""Catalog Local theo API, lưu trong bộ nhớ; không xếp hạng chất lượng model."""
from collections import OrderedDict
from dataclasses import dataclass
from fnmatch import fnmatchcase
import http.client
import time
import urllib.error
import urllib.request

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from . import ai_cuc_bo
from .dto import MA_MODEL

THOI_GIAN_DEM = 300
CAC_API = (
    ("ollama", "/api/tags", "models", "name"),
    ("lm_studio", "/api/v1/models", "models", "key"),
    ("lm_studio", "/api/v0/models", "data", "id"),
    ("openai_compatible", "/v1/models", "data", "id"),
)
LOI_PHAT_HIEN = (ValueError, OSError, http.client.HTTPException, TypeError,
                 KeyError, RecursionError, OverflowError)


@dataclass(frozen=True)
class ModelLocal:
    ma: str
    kha_dung: bool


@dataclass(frozen=True)
class DanhSachModel:
    loai: str
    api: tuple
    models: tuple[ModelLocal, ...]


def _chuan_hoa(data, api):
    loai, _, truong, khoa = api
    muc = data.get(truong) if isinstance(data, dict) else None
    if not isinstance(muc, list):
        raise ValueError("Danh sách model không hợp lệ.")
    models = {}
    for m in muc:
        if not isinstance(m, dict):
            raise ValueError("Metadata model không hợp lệ.")
        ma = m.get(khoa)
        if loai == "ollama" and ma is None:
            ma = m.get("model")
        if not isinstance(ma, str) or not MA_MODEL.fullmatch(ma):
            raise ValueError("Mã model không hợp lệ.")
        kha_dung = (
            not ai_cuc_bo.model_tu_xa(m)
            and m.get("type", "llm") == "llm"
            and m.get("state") != "not-loaded"
            and ("loaded_instances" not in m or bool(m["loaded_instances"]))
        )
        models[ma] = models.get(ma, True) and kha_dung
    # Giữ nguyên ID và thứ tự nguồn; mục trùng chỉ khả dụng nếu mọi metadata cho phép.
    return DanhSachModel(loai, api, tuple(ModelLocal(ma, kha_dung) for ma, kha_dung in models.items()))


def _bo_doc(cau_hinh):
    parsed = ai_cuc_bo.kiem_url(cau_hinh["url"])
    nguon = ai_cuc_bo.nguon_tailscale(parsed.hostname, parsed.port)
    bo_mo = urllib.request.build_opener(
        urllib.request.ProxyHandler({}), ai_cuc_bo._KhongChuyenHuong(),
        ai_cuc_bo._MoHTTPBangIP(nguon),
    )
    return bo_mo, parsed._replace(path="").geturl()


def _doc_api(bo_mo, goc, cau_hinh, api, kiem_huy):
    kiem_huy()
    data = ai_cuc_bo._doc_json(bo_mo, goc + api[1], cau_hinh["timeout_giay"])
    kiem_huy()
    return _chuan_hoa(data, api)


class BoPhatHienModel:
    def __init__(self, dong_ho=time.monotonic):
        self.dong_ho = dong_ho
        self._dem = OrderedDict()

    def phat_hien(self, cau_hinh, *, kiem_huy=lambda: None, lam_moi=False):
        """Lỗi discovery trả None, không cache lỗi và không ảnh hưởng khởi động."""
        kiem_huy()
        try:
            bo_mo, goc = _bo_doc(cau_hinh)
            cu = self._dem.get(goc)
            if not lam_moi and cu and self.dong_ho() - cu[0] < THOI_GIAN_DEM:
                self._dem.move_to_end(goc)
                return cu[1]
            self._dem.pop(goc, None)
            for api in CAC_API:
                try:
                    catalog = _doc_api(bo_mo, goc, cau_hinh, api, kiem_huy)
                except urllib.error.HTTPError as exc:
                    exc.close()
                    continue
                except LOI_PHAT_HIEN:
                    continue
                self._dem[goc] = (self.dong_ho(), catalog)
                if len(self._dem) > 64:
                    self._dem.popitem(last=False)
                return catalog
        except LOI_PHAT_HIEN:
            pass
        return None

    def kha_dung_hien_tai(self, cau_hinh, *, kiem_huy=lambda: None):
        """Cache loại API/catalog 5 phút; kiểm khả dụng bằng metadata mới mỗi lượt."""
        catalog = self.phat_hien(cau_hinh, kiem_huy=kiem_huy)
        if catalog is None:
            return None
        try:
            bo_mo, goc = _bo_doc(cau_hinh)
            moi = _doc_api(bo_mo, goc, cau_hinh, catalog.api, kiem_huy)
            # Không kéo dài TTL discovery khi chỉ kiểm trạng thái.
            self._dem[goc] = (self._dem[goc][0], moi)
            return moi
        except urllib.error.HTTPError as exc:
            exc.close()
        except LOI_PHAT_HIEN:
            pass
        # Dịch vụ có thể đã đổi API; không dùng catalog cũ sau lỗi kiểm khả dụng.
        return self.phat_hien(cau_hinh, kiem_huy=kiem_huy, lam_moi=True)


bo_phat_hien = BoPhatHienModel()


def chon_model(yeu_cau, cau_hinh, *, kiem_huy=lambda: None):
    catalog = bo_phat_hien.kha_dung_hien_tai(cau_hinh["local_ai"], kiem_huy=kiem_huy)
    cac_ma = [m.ma for m in catalog.models if m.kha_dung] if catalog else []
    if yeu_cau.model_uu_tien in cac_ma:
        return yeu_cau.model_uu_tien, "model_uu_tien"
    for quy_tac in cau_hinh.get("quy_tac_model", []):
        if fnmatchcase(yeu_cau.ma_prompt, quy_tac["mau_ma_prompt"]):
            if quy_tac["uu_tien"] in cac_ma:
                return quy_tac["uu_tien"], "quy_tac_ma_prompt"
            for ma in quy_tac["du_phong"]:
                if ma in cac_ma:
                    return ma, "du_phong_quy_tac_ma_prompt"
    if cac_ma:
        return cac_ma[0], "model_dau_tien_kha_dung"
    raise LoiNghiepVu(
        "LOCAL_AI_KHONG_SAN_SANG", "Không có model Local AI khả dụng. Hãy kiểm tra máy AI và thử lại.",
        thu_lai_duoc=True,
    )
