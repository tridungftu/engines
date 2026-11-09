"""TRICH-1a: bọc trích 37 tham số XD và ánh xạ tham_so.v1 bằng AI được tiêm.

Nguồn chính thức: D:/Claude/Ho tro review ho so xay dung/review_xaydung/
trich_xuat/{quy_trinh,danh_muc}.py, phương pháp v3, PHIEN_BAN=2026-10-15a.
SHA256 nguồn và bản repo m4/review_goc được ghi riêng bên dưới: bản repo chưa
có bổ sung common/RULE_ONLY của nguồn độc lập. Dùng closure vendor thuần và
adapter pipeline của engine; không nạp pipeline nguồn có client riêng.
Danh mục XLSX XD ghim riêng, không dùng hash mã Python thay hash danh mục.
Prompt/protocol nguồn chỉ thử bằng AI giả ở lát này; tích hợp mẫu cổng chung
thuộc TRICH-1b/3b, phép đo độ chính xác thuộc TRICH-4. Không tạo AI client.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from uuid import UUID

from .vendor.review import danh_muc as _dm
from .vendor.review.kiem_tra import la_khong_co, la_ok, norm

from .docx import _boc_ham, kiem_docx, read_contract

NGUON_SHA256 = {
    "quy_trinh.py": "c554d9b8489ddc39e9db3c6466ac2f464fd03ffe267c4f222dd874e6c31cc0d3",
    "danh_muc.py": "4309decb0b62b9ee76ba449f69ea5080c33abb23d4e488b6a1d8cc2602e5bf6b",
}
BAN_REPO_SHA256 = {
    "quy_trinh.py": "a76e95a55cb7253cc7446ead9e7fd495fb9c3ea457c612259bd062aa27b26264",
    "danh_muc.py": "f0796984f7b18a4d0d3389b557a6324f3ad59ca488c29ad3284e11ca97ca2ff2",
}
PHIEN_BAN_NGUON = "2026-10-15a"
DANH_MUC_ID = "XD"
DANH_MUC_SHA256 = "05846a2acd60f2cde708d13a163a137ee3fb0b4e08fd84f85a7e14e7ef861bcd"
# QD-TAM-20261106-04: catalog ngoài git, chỉ đọc sau khi xác minh SHA.
DANH_MUC_THAM_SO = (Path(__file__).resolve().parents[2] / "src" / "kho_tri_thuc"
                    / "m4" / "review_goc" / "trich_xuat" / "DANH_MUC_THAM_SO.xlsx")


def danh_muc_xd(path=None):
    """Đọc catalog ghim có sẵn; không để load_params tự tạo/ghi đè catalog."""
    path = Path(DANH_MUC_THAM_SO if path is None else path)
    if hashlib.sha256(path.read_bytes()).hexdigest() != DANH_MUC_SHA256:
        raise ValueError("TRICH_DANH_MUC_SAI_HASH")
    params = _dm.load_params(path)
    if [p["ma"] for p in params] != [p[0] for p in _dm.MAC_DINH] or len(params) != 37:
        raise ValueError("TRICH_DANH_MUC_SAI_37_MA")
    return params


def _ai_legacy(ai, *, cloud=None, dung=None):
    """Thích nghi AI được tiêm của TRICH-1a/3a sang pipeline DTO hiện có.

    Không tạo client; giữ câu hỏi legacy đã lưu trong adapter AI chung.
    Đường vận hành qua CongAI vẫn thuộc quy_trinh.TrichXuat.
    """
    from .ai_chung import AIChung, CAU_TRICH_GOC, CAU_VI_TRI_GOC

    class AILegacy(AIChung):
        def __init__(self):
            TrichXuat._kiem_ai(ai, cloud)
            self.phan_hoi = []
            self.model = ai.model
            self.url = ai.url
            self.ten = getattr(ai, "ten", "Local AI")

        def hoi_trich(self, yeu_cau, what="AI"):
            TrichXuat._kiem_ai(ai, cloud)
            ds = yeu_cau.chi_dan.split("\nTHAM SỐ:\n", 1)[1]
            prompt = CAU_TRICH_GOC.format(ds=ds, blocks=yeu_cau.van_ban)
            return ai.hoi_trich(prompt, what)

        def tim_vi_tri(self, params, muc_luc, rows):
            TrichXuat._kiem_ai(ai, cloud)
            ds = "\n".join(f"- {p['ma']} | {p['mo_ta']}" for p in params)
            prompt = CAU_VI_TRI_GOC.format(ds=ds, muc_luc=muc_luc, phan="")
            schema = {"type": "object", "properties": {"vi_tri": {
                "type": "array", "items": {"type": "object", "properties": {
                    "ma": {"type": "string"}, "ids": {
                        "type": "array", "items": {"type": "string"}}},
                    "required": ["ma", "ids"]}}}, "required": ["vi_tri"]}
            data, _, _ = ai.chat_json(prompt, schema, "vi_tri", 32768,
                                      "tìm vị trí qua mục lục")
            found = {}
            for item in data["vi_tri"]:
                if isinstance(item, dict):
                    ids = found.setdefault(str(item.get("ma", "")), [])
                    for rid in item.get("ids", []):
                        if rid in rows and rid not in ids:
                            ids.append(rid)
            return {ma: ids[:3] for ma, ids in found.items()}

    return AILegacy()


class TrichXuat:
    """Đường legacy dùng adapter pipeline, DOCX/XML và AI được tiêm.

    xu_ly trả đầy đủ phản hồi gốc, kể cả ghi_chu/kiem_tra/dieu_khoan/
    trich_dan/vi_tri_do_duoc và các tệp nguồn trong out_dir. Core tiếp nhận
    và cấp phan_hoi_nguon_tep_id trước khi gọi anh_xa_tham_so. Bàn giao/dọn
    out_dir thuộc vòng đời engine ở TRICH-3a; lát này không xóa tệp.
    """

    def __init__(self, *, ai, out_dir, cloud=None, ra_lai=True):
        self._kiem_ai(ai, cloud)
        # Import trễ vì pipeline cũng dùng danh_muc_xd; không sửa globals chung.
        from . import quy_trinh as pipeline
        self.ai, self.cloud = ai, None
        self._pipeline = pipeline.TrichXuat.__new__(pipeline.TrichXuat)
        khoi_tao = _boc_ham(pipeline.TrichXuat.__init__, AIChung=_ai_legacy)
        khoi_tao(self._pipeline, cong_ai=ai, out_dir=out_dir,
                 cloud=None, ra_lai=ra_lai)

    @staticmethod
    def _kiem_ai(ai, cloud):
        if cloud is not None or ai is None or getattr(ai, "la_cloud", None) is not False:
            raise ValueError("TRICH_CLOUD_BI_CHAN: cần ai.la_cloud=False, cloud=None")

    def ocr_pdf(self, *args, **kwargs):
        raise ValueError("TRICH_OCR_BI_CHAN: PDF phải qua e_ocr")

    def xu_ly(self, path):
        path = kiem_docx(path)
        self._kiem_ai(self.ai, self.cloud)
        return self._pipeline.xu_ly(path)


def anh_xa_tham_so(phan_hoi, *, tep_id, phan_hoi_nguon_tep_id, van_ban,
                   loai_hop_dong, danh_muc_id, danh_muc_sha256, revision=1):
    """Ánh xạ phản hồi đã lưu, không sửa phản hồi và không tự đoán tiền/ngày.

    Chưa có kiểu nghiệp vụ được catalog quy định: giữ giá trị xác định dưới
    kiểu van_ban; thiếu giá trị/dẫn chứng kiểm được thành chua_ro. Không dùng
    vi_tri_do_duoc (vị trí ứng viên) thay dẫn chứng. Core kiểm quyền các ID.
    """
    if (loai_hop_dong, danh_muc_id, danh_muc_sha256) != ("XD", DANH_MUC_ID, DANH_MUC_SHA256):
        raise ValueError("TRICH_DANH_MUC_KHONG_HO_TRO")
    tep_uuids = []
    for value in (tep_id, phan_hoi_nguon_tep_id):
        if not isinstance(value, str):
            raise ValueError("TRICH_TEP_ID_SAI")
        try:
            parsed = UUID(value)
        except ValueError as exc:
            raise ValueError("TRICH_TEP_ID_SAI") from exc
        if str(parsed) != value.lower():
            raise ValueError("TRICH_TEP_ID_SAI")
        tep_uuids.append(parsed)
    if tep_uuids[0] == tep_uuids[1]:
        raise ValueError("TRICH_PHAN_HOI_PHAI_LA_TEP_RIENG")
    if type(revision) is not int or revision < 1:
        raise ValueError("TRICH_REVISION_SAI")
    params = danh_muc_xd()
    allowed = {p["ma"] for p in params}
    by_ma = {}
    for row in phan_hoi["bang"]:
        ma = row["ma"]
        if ma not in allowed or ma in by_ma:
            raise ValueError("TRICH_MA_LA_HOAC_TRUNG")
        by_ma[ma] = row

    result = []
    for p in params:
        row = by_ma.get(p["ma"], {})
        value = row.get("gia_tri")
        if value is not None and not isinstance(value, str):
            raise ValueError("TRICH_GIA_TRI_NGUON_SAI_KIEU")
        quote = row.get("trich_dan") or ""
        locator = row.get("dieu_khoan") or row.get("row_id") or ""
        warnings = [f"{key}: {row[key]}" for key in
                    ("ghi_chu", "kiem_tra", "vi_tri_do_duoc") if row.get(key)]
        evidence = []
        if quote.strip() and locator.strip() and norm(quote) in norm(van_ban):
            evidence = [{"vi_tri": {"tep_id": tep_id, "dinh_vi": locator}, "trich_dan": quote}]
        reason = None
        if value is None or not value.strip() or la_khong_co(value):
            reason = "Chưa xác định" if not value else value
        elif not evidence:
            reason = "Chưa có dẫn chứng kiểm được"
        typed = {"kieu": "chua_ro", "ly_do": reason} if reason else {"kieu": "van_ban", "gia_tri": value}
        if reason:
            warnings.append(reason)
        result.append({"ma": p["ma"], "ten": p["ten"], "gia_tri": typed,
                       "nguyen_van": value, "dan_chung": evidence,
                       "can_soat": bool(reason) or not la_ok(row.get("kiem_tra", "")),
                       "canh_bao": warnings})
    return {"contract": "tham_so.v1", "phien_ban": "1.0.0", "revision": revision,
            "nguon_tep_ids": [tep_id], "loai_hop_dong": loai_hop_dong,
            "danh_muc_id": danh_muc_id, "danh_muc_sha256": danh_muc_sha256,
            "phan_hoi_nguon_tep_id": phan_hoi_nguon_tep_id, "tham_so": result}
