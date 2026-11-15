"""Wrapper E6 chỉ trong kiểm thử: nguồn cũ chỉ đọc, không nạp Core/client AI.

Nạp thân hàm bằng AST, bỏ import/CLI của nguồn. Các seam duy nhất: I/O xuất
thành RAM, đọc DOCX XML (giống ma-nguon/docx.py), AI theo băng trả lời cố định.
Không thay thuật toán nhóm/dò/rà lại, câu hỏi, kiểm tra hoặc bảng của nguồn.
"""

import ast
from copy import deepcopy
from dataclasses import dataclass
import datetime
from decimal import Decimal, InvalidOperation
import io
import json
import os
from pathlib import Path
import re
from types import FunctionType, SimpleNamespace
import time
import unicodedata
import xml.etree.ElementTree as ET
import zipfile


GOC = Path(__file__).resolve().parents[1] / "ma-nguon"
CAC_TEP_NGUON = ("quy_trinh.py", "ai_chung.py", "docx.py",
    "vendor/review/danh_muc.py", "vendor/review/xlsx_mini.py",
    "vendor/review/doc_hop_dong.py", "vendor/review/cau_truc.py",
    "vendor/review/kiem_tra.py", "vendor/review/logic.py")


class ThieuBangAI(ValueError):
    """Băng AI không đủ hoặc còn lượt chưa dùng; không sinh câu trả lời."""


def _cam(*args, **kwargs):
    raise ValueError("Thao tác ngoài phạm vi đối chiếu E6.")


class _BoImport(ast.NodeTransformer):
    def visit_Import(self, node):
        return None

    def visit_ImportFrom(self, node):
        return None


def _nap(ten, them=None):
    """Chỉ nạp mã nguồn cố định trong worktree, không nạp đường từ fixture."""
    tree = ast.parse((GOC / ten).read_text(encoding="utf-8"))
    tree.body = [n for n in tree.body if isinstance(
        n, (ast.FunctionDef, ast.ClassDef, ast.Assign, ast.AnnAssign))]
    tree = _BoImport().visit(tree)
    ns = dict(re=re, _re=re, os=os, json=json, datetime=datetime, time=time,
              unicodedata=unicodedata, ET=ET, zipfile=zipfile,
              Decimal=Decimal, InvalidOperation=InvalidOperation, FunctionType=FunctionType)
    ns.update(them or {})
    exec(compile(ast.fix_missing_locations(tree), "<nguon-doi-chieu-E6>", "exec"), ns)
    return ns


def doc_bo_cu(tep):
    mini = _nap("vendor/review/xlsx_mini.py")
    dm = _nap("vendor/review/danh_muc.py", {"read_xlsx": mini["read_xlsx"]})
    # Không cho read_catalog tạo tệp nếu thiếu. XLSX phải được cổng E6 xác minh.
    dm["create_catalog"] = _cam
    return dm["read_catalog"](str(tep)), dm["load_params"](str(tep)), dm["HEADER"], dm["MAC_DINH"]


@dataclass(frozen=True)
class YeuCauCu:
    ma: str
    van_ban: str
    chi_dan: str
    truong: tuple


def chay_mac_dinh_chuyen_tiep(tep_bo, docx_bytes, bang_ai, *, ra_lai=True):
    """Thực thi pipeline nguồn với hai hàng đợi AI do fixture cung cấp.

    Không ghi tệp tạm: read_docx nhận BytesIO, read_contract chỉ nhận tên DEMO.
    Lược bỏ I/O save/xuất và tìm đáp án; không bỏ nội dung bảng/phản hồi.
    """
    dong, params, header, _ = doc_bo_cu(tep_bo)
    cau_truc = _nap("vendor/review/cau_truc.py")
    kt = _nap("vendor/review/kiem_tra.py", cau_truc)
    logic = _nap("vendor/review/logic.py", {**cau_truc, **kt})
    doc = _nap("vendor/review/doc_hop_dong.py")
    # Đúng seam namespace của ma-nguon/docx.py; không dùng Word/LibreOffice.
    boc = _nap("docx.py", {"_goc": SimpleNamespace(**doc)})
    doc["dem_sua_doi"] = boc["_dem_sua_doi"]
    doc["_co_sua_doi"] = lambda path: 0
    doc["chuyen_docx"] = _cam
    doc["_read_contract_pdf"] = _cam
    read = doc["read_docx"]

    def doc_ram(path):
        with io.BytesIO(docx_bytes) as f:
            return read(f)

    doc["read_docx"] = doc_ram
    ai_goc = _nap("ai_chung.py", {"YeuCauAI": YeuCauCu})
    chi_dan = ai_goc["CHI_DAN_TRICH"]
    cau_hoi, phan_hoi = [], []
    tape = deepcopy(bang_ai)
    if set(tape) != {"tim_vi_tri", "hoi_trich"} or not all(isinstance(v, list) for v in tape.values()):
        raise ThieuBangAI()

    class AIGiaCu:
        la_cloud = False
        ten = model = "DEMO-AI-gia-co-dinh"
        url = "DEMO-khong-mang"

        def __init__(self, *args, **kwargs):
            self.phan_hoi = phan_hoi

        def _lay(self, loai):
            if not tape[loai]:
                raise ThieuBangAI()
            v = tape[loai].pop(0)
            phan_hoi.append({"loai": loai, "du_lieu": deepcopy(v)})
            return deepcopy(v)

        def tim_vi_tri(self, ps, muc_luc, rows):
            # Chạy nguyên thân dựng DTO/tìm ID của adapter nguồn.
            return ai_goc["AIChung"].tim_vi_tri(self, ps, muc_luc, rows)

        def goi(self, yc):
            cau_hoi.append({"loai": "tim_vi_tri", "prompt": yc.chi_dan,
                            "tai_lieu": yc.van_ban, "truong": list(yc.truong)})
            found = self._lay("tim_vi_tri")
            return SimpleNamespace(truong={f"{ma}.{i}": SimpleNamespace(gia_tri=rid)
                for ma, ids in found.items() for i, rid in enumerate(ids, 1)})

        def _kiem_loi(self, kq):
            pass  # Băng giả chỉ có phản hồi thành công, không có provider.

        def hoi_trich(self, yc, what="AI"):
            cau_hoi.append({"loai": "hoi_trich", "prompt": yc.chi_dan,
                            "tai_lieu": yc.van_ban, "truong": list(yc.truong)})
            return self._lay("hoi_trich"), 0, 0

    ns = _nap("quy_trinh.py", {**cau_truc, **kt, **logic,
        "YeuCauAI": YeuCauCu, "AIChung": AIGiaCu,
        "AILoi": type("AILoi", (Exception,), {}), "DaDung": type("DaDung", (Exception,), {}),
        "CHI_DAN_TRICH": chi_dan, "danh_muc_xd": lambda: deepcopy(params),
        "kiem_docx": lambda path: path, "read_contract": doc["read_contract"],
        "save": lambda *args: None, "ghi_ket_qua_hd": lambda *args: None,
        "tim_dap_an": lambda *args: None, "load_key": lambda *args: None,
        "os": SimpleNamespace(path=os.path, fspath=os.fspath, makedirs=lambda *args, **kwargs: None)})
    p = ns["TrichXuat"](cong_ai=None, out_dir="DEMO-RAM", ra_lai=ra_lai)
    kq = p.xu_ly("DEMO-hop-dong.docx")
    if any(tape.values()):
        raise ThieuBangAI({"tim_vi_tri_con": len(tape["tim_vi_tri"]),
                           "hoi_trich_con": len(tape["hoi_trich"])})
    info = doc["read_contract"]("DEMO-hop-dong.docx")
    return {"dong": dong, "tham_so": params, "header": header,
            "van_ban": info["text"], "track_changes": info["report"]["track_changes_accepted"],
            "cau_hoi": cau_hoi, "bang": kq["bang"], "phan_hoi": phan_hoi}
