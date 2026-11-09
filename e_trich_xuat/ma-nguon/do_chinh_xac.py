"""TRICH-4a: chấm kết quả đã có, không chạy trích xuất hay gọi AI.

Định dạng gốc: trich_xuat/kiem_tra.py:load_key đọc TSV UTF-8 BOM tùy ý,
mã ở cột 1, đáp án ở cột 4; compare chấm giá trị (không chấm dẫn chứng).
Nguồn: D:/Claude/Ho tro review ho so xay dung/review_xaydung/
trich_xuat/kiem_tra.py, phiên bản nguồn 2026-10-15a; SHA256 bên dưới.
Bản repo có cùng SHA256; dùng lại compare nguyên, kể cả phép chứa chuỗi
khá rộng của nguồn. Không coi số test DEMO là độ chính xác thực.

Gọi do_chinh_xac với DAP_AN_*.tsv, JSON phản hồi gốc {"bang": [...]},
DOCX nguồn và tệp mã nguồn của pipeline đã tạo JSON. ket_qua=None biểu
diễn chưa có phép đo. Trả báo cáo JSON-serializable, không tự ghi tệp,
không tìm hồ sơ, không thay đáp án, không kết luận nghiệm thu trước/sau.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

from .vendor.review import kiem_tra as _kt
from .vendor.review import danh_muc as _dm

NGUON_CHAM = (
    "D:/Claude/Ho tro review ho so xay dung/review_xaydung/"
    "trich_xuat/kiem_tra.py"
)
NGUON_CHAM_SHA256 = "47ee35567cb7b864a6b3d6825bc90f93a7a26c0c6872a326e99ead9160467f12"
CACH_CHAM = "review-2026-10-15a/compare-gia-tri-v1"
DANH_MUC_NGUON_SHA256 = "f0796984f7b18a4d0d3389b557a6324f3ad59ca488c29ad3284e11ca97ca2ff2"


def _doc_tep(path):
    path = Path(path).resolve(strict=True)
    raw = path.read_bytes()
    return raw, {"duong_dan": str(path), "sha256": hashlib.sha256(raw).hexdigest()}


def _doc_nguon_vendor(path):
    """Đọc nguồn vendor, chuẩn hóa CRLF->LF trước khi băm (git lưu LF,
    bản làm việc Windows CRLF); SHA ghim giữ nguyên theo bản LF."""
    path = Path(path).resolve(strict=True)
    raw = path.read_bytes().replace(b"\r\n", b"\n")
    return raw, {"duong_dan": str(path), "sha256": hashlib.sha256(raw).hexdigest()}


def _doc_dap_an(raw, allowed):
    """Giữ cách tách cột load_key; chặn ghi đè/trượt cột âm thầm."""
    result = {}
    for line in raw.decode("utf-8-sig").splitlines():
        cells = line.split("\t")
        ma = cells[0]
        if ma not in allowed:
            if re.match(r"^(TC|TT)-", ma):
                raise ValueError("TRICH_DO_MA_LA")
            if line.strip() and ma not in ("Mã", "Mã tham số"):
                raise ValueError("TRICH_DO_DAP_AN_SAI_DONG")
            continue
        if len(cells) < 4:
            raise ValueError("TRICH_DO_DAP_AN_THIEU_COT")
        if ma in result:
            raise ValueError("TRICH_DO_MA_TRUNG")
        result[ma] = cells[3]
    return result


def _doc_ket_qua(raw, allowed):
    value = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(value, dict) or not isinstance(value.get("bang"), list):
        raise ValueError("TRICH_DO_CAN_PHAN_HOI_GOC_BANG")
    result = {}
    for row in value["bang"]:
        if not isinstance(row, dict) or not isinstance(row.get("ma"), str):
            raise ValueError("TRICH_DO_KET_QUA_SAI_DONG")
        ma = row["ma"]
        if ma not in allowed:
            raise ValueError("TRICH_DO_MA_LA")
        if ma in result:
            raise ValueError("TRICH_DO_MA_TRUNG")
        got = row.get("gia_tri")
        if got is not None and not isinstance(got, str):
            raise ValueError("TRICH_DO_GIA_TRI_PHAI_LA_CHUOI")
        result[ma] = got
    return result


def do_chinh_xac(dap_an, ket_qua=None, *, tep_nguon, nguon,
                 phien_ban_nguon, model, cau_hinh):
    """Một tài liệu/lần; thiếu đáp án hoặc kết quả không vào mẫu số da_do.

    nguon là tệp mã pipeline, phien_ban_nguon/model/cau_hinh do bên chạy
    cung cấp theo điều kiện thực đã dùng, không tự suy từ máy hiện tại.
    dat/ty_le=None khi chưa có đo; 0 chỉ xuất hiện khi đã đo và sai.
    Tỷ lệ trong [0, 1] tính trên da_do; trạng thái chưa đo đủ giữ lộ rõ
    việc thiếu ca, không dùng tỷ lệ bộ phận để công bố đạt 37 tham số.
    """
    for value in (phien_ban_nguon, model):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("TRICH_DO_THIEU_DIEU_KIEN")
    if not isinstance(cau_hinh, dict):
        raise ValueError("TRICH_DO_CAU_HINH_PHAI_LA_OBJECT")
    # Snapshot cấu hình, không giữ tham chiếu mutable hoặc NaN/Infinity.
    config = json.loads(json.dumps(cau_hinh, ensure_ascii=False, allow_nan=False))
    _, scorer = _doc_nguon_vendor(_kt.__file__)
    if scorer["sha256"] != NGUON_CHAM_SHA256:
        raise ValueError("TRICH_DO_NGUON_CHAM_SAI_HASH")
    # Chấm đúng 37 mã chuẩn, không cần catalog XLSX ngoài git, không gọi
    # load_params (có thể tự tạo XLSX khi thiếu). Không suy hash XLSX từ mã.
    _, catalog = _doc_nguon_vendor(_dm.__file__)
    if catalog["sha256"] != DANH_MUC_NGUON_SHA256:
        raise ValueError("TRICH_DO_DANH_MUC_SAI_HASH")
    params = [{"ma": p[0], "ten": p[2]} for p in _dm.MAC_DINH]
    allowed = {p["ma"] for p in params}
    if len(params) != 37 or len(allowed) != 37:
        raise ValueError("TRICH_DO_DANH_MUC_SAI_37_MA")
    if not (Path(dap_an).name.startswith("DAP_AN_") and Path(dap_an).suffix == ".tsv"):
        raise ValueError("TRICH_DO_CAN_DAP_AN_TSV")
    gold_raw, gold_file = _doc_tep(dap_an)
    gold = _doc_dap_an(gold_raw, allowed)
    _, input_file = _doc_tep(tep_nguon)
    _, source_file = _doc_tep(nguon)
    source_file["phien_ban"] = phien_ban_nguon
    got, result_file = {}, None
    if ket_qua is not None:
        result_raw, result_file = _doc_tep(ket_qua)
        got = _doc_ket_qua(result_raw, allowed)

    rows = []
    for p in params:
        ma = p["ma"]
        expected, actual = gold.get(ma), got.get(ma)
        missing = []
        if expected is None or not expected.strip():
            missing.append("thiếu đáp án")
        if actual is None or not actual.strip():
            missing.append("thiếu kết quả")
        status = "chưa đo" if missing else _kt.compare(expected, actual)
        passed = None if missing else int(status == "ĐÚNG")
        rows.append({"ma": ma, "ten": p["ten"], "dap_an": expected,
                     "gia_tri": actual, "trang_thai": status,
                     "ly_do": "; ".join(missing) if missing else None,
                     "dat": passed, "da_do": int(not missing),
                     "ty_le": None if missing else float(passed)})
    measured = sum(row["da_do"] for row in rows)
    passed = sum(row["dat"] for row in rows if row["dat"] is not None) if measured else None
    _, implementation = _doc_tep(__file__)
    return {
        "do_luc_utc": datetime.now(timezone.utc).isoformat(),
        "nguon": source_file, "tep_nguon": input_file,
        "dap_an": gold_file, "ket_qua": result_file,
        "model": model, "cau_hinh": config,
        "danh_muc": {"id": "XD", "pham_vi": "MAC_DINH: 37 tham số chuẩn",
                     "nguon": catalog},
        "cach_cham": {"id": CACH_CHAM, "ham": "kiem_tra.compare",
                      "nguon": NGUON_CHAM, "sha256": scorer["sha256"],
                      "cong_cu": implementation,
                      "pham_vi": "giá trị; giữ phép chứa chuỗi của nguồn, không chấm dẫn chứng",
                      "mau_so": "da_do; thiếu đáp án/kết quả là chưa đo"},
        "tong_hop": {"tong": len(rows), "da_do": measured,
                     "chua_do": len(rows) - measured, "dat": passed,
                     "sai": measured - passed if measured else None,
                     "ty_le": passed / measured if measured else None,
                     "trang_thai": ("chưa đo" if not measured else
                                    "chưa đo đủ" if measured < len(rows) else "đã đo")},
        "tham_so": rows,
        "ca_sai": [row["ma"] for row in rows if row["dat"] == 0],
    }
