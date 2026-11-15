"""TC-11: đo DEMO ngoài runtime, mặc định chỉ kiểm ghim trong RAM.

Adapter là seam nội bộ để lead nối hợp đồng Core được công bố, KHÔNG phải
API Core mới. Bản SDK được giao chưa có discovery/đo/tokenizer qua cửa chung:
CoreThat từ chối trước nhập khóa/gọi mạng. Không import engine/provider khác.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlsplit

sys.dont_write_bytecode = True
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu


GOC = Path(__file__).resolve().parents[2]
DEMO = GOC / "e_tra_cuu/goi/e_tra_cuu/demo/tc-10"
BAM_BO_MAC_DINH = "sha256:445f5c7700291c27e85aa3510671e47c6c6449cab6dc337a9015123290c9ab4a"
CHI_SO = ("tra_loi_dung", "trich_dan_dung", "tu_choi_dung", "phan_loai_dung")
CHI_TIET = ("cat_doan_vi_tri", "cau_hoi_ham", "xep_hang", "tien", "ngay")
VAI_TRO = ("gpt_oss_20b", "qwen3_8b", "gemma")
TAC_VU = ("phan_loai", "cat_doan", "phan_tich_cau_hoi", "xep_hang_lai", "soan_tra_loi")
CA_CORE = (
    "rls_hai_phap_nhan_truoc_ai", "nhom_07_local_truoc_ai", "cache_quyen_moi_nguon",
    "cache_thuc_the_a_b", "cache_thay_phien_ban", "cache_doi_nhom", "cache_thu_quyen",
    "cache_duyet", "cache_cong_bo", "tra_lai_tu_dau", "tang_1_dung_dung",
    "tang_2_dung_dung", "tang_3_nen_http_202", "k5_du_lieu_moi", "k5_mau_thuan",
    "trich_dan_dung_trang_hoac_khong_co_trang", "ui_cau_hinh_khung_core",
    "ui_trang_thai_khung_core", "postgresql", "pgvector", "unaccent", "pg_trgm",
    "tai_20_dong_thoi", "tai_150_nguoi",
)
SO_DO = ("context_hieu_dung", "token_vao", "token_ra", "thoi_gian_runtime_giay",
         "thoi_gian_core_giay", "so_doan", "so_ung_vien")
CAU_THIEU = "Chưa có số đo hoặc bằng chứng từ Core/runtime."
CAU_MOI_TRUONG = "Chưa đủ môi trường để thử tra cứu. Anh nhờ quản trị viên kiểm tra các dịch vụ cần thiết."


def loi(ma="TC_DAU_VAO_KHONG_HOP_LE", cau="Đầu vào thử DEMO chưa hợp lệ. Anh kiểm tra bộ dữ liệu và các bản ghim."):
    exc = LoiNghiepVu(ma, cau)
    exc.tc11_noi_bo = True
    return exc


def thieu_moi_truong():
    return loi("TC_CHUA_CO_MOI_TRUONG_THU", CAU_MOI_TRUONG)


def json_bytes(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def bam(raw):
    return "sha256:" + sha256(raw).hexdigest()


def la_bam(v):
    return isinstance(v, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", v) is not None


def json_nghiem(raw):
    def cap(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise ValueError
            out[k] = v
        return out
    def cam(_):
        raise ValueError
    try:
        v = json.loads(raw.decode("utf-8"), object_pairs_hook=cap, parse_constant=cam)
        json_bytes(v)  # Loại cả số float tràn thành inf và surrogate lẻ.
        return v
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise loi() from None


def doc_tep(duong, gioi_han=2 * 1024 * 1024):
    try:
        p = Path(duong).resolve()
        if any(k.lower() in {".env", "cau_hinh.that.toml", "var", "bi-mat", "in", "out", "jobs", "state"} for k in p.parts):
            raise loi()
        # Chỉ đọc đường đầu vào được chỉ định; không dò thư mục hay cấu hình máy.
        with p.open("rb") as f:
            raw = f.read(gioi_han + 1)
        if len(raw) > gioi_han:
            raise loi("TC_QUA_GIOI_HAN", "Bộ DEMO vượt giới hạn thử. Anh giảm phạm vi bộ thử.")
        return raw
    except OSError:
        raise loi() from None


def ten_an_toan(v):
    # Chỉ metadata model/version, không thông điệp tùy ý từ Core.
    return (isinstance(v, str) and 0 < len(v) <= 200
            and re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.:/@+\-]*", v) is not None
            and not re.match(r"^[A-Za-z]:", v) and "://" not in v and ".." not in v)


def kiem_url(v):
    try:
        p = urlsplit(v)
        _ = p.port
        if (p.scheme not in {"http", "https"} or not p.hostname or p.username or p.password
                or p.query or p.fragment or p.path not in {"", "/"}
                or any(ord(c) < 33 for c in v) or "\\" in v
                or (p.scheme == "http" and p.hostname not in {"localhost", "127.0.0.1", "::1"})):
            raise ValueError
        return v.rstrip("/")
    except (ValueError, TypeError):
        raise loi("TC_DIA_CHI_CORE_KHONG_HOP_LE", "Địa chỉ Core chưa hợp lệ. Máy khác cần dùng HTTPS và không kèm khóa trong địa chỉ.") from None


def nap_bo(thu_muc=DEMO, bam_bo=BAM_BO_MAC_DINH):
    """Đọc bộ TC-10 đã ghim; đáp án chỉ cho bộ chấm, không gửi cho model.

    Bộ bổ sung được lead cấp có thể thêm ba tác vụ thuần theo cùng danh sách
    kich_ban/dap_an; đáp án du_lieu là kết quả chuẩn, không điểm model tự khai.
    """
    root = Path(thu_muc).resolve()
    raw = doc_tep(root / "bam-DEMO.json")
    if not la_bam(bam_bo) or bam(raw) != bam_bo:
        raise loi("TC_SAI_NGUON", "Bộ DEMO không khớp bản ghim. Anh nhờ lead kiểm tra lại bộ thử.")
    pins = json_nghiem(raw)
    if not isinstance(pins, dict) or not 2 <= len(pins) <= 128:
        raise loi()
    files = {}
    total = 0
    for ten, checksum in pins.items():
        if (not isinstance(ten, str) or not re.fullmatch(r"[A-Za-z0-9_-]+-DEMO\.(json|txt)", ten)
                or not la_bam(checksum)):
            raise loi()
        path = (root / ten).resolve()
        if path.parent != root:  # Kể cả symlink trỏ ra ngoài.
            raise loi()
        data = doc_tep(path)
        total += len(data)
        if total > 8 * 1024 * 1024:
            raise loi("TC_QUA_GIOI_HAN", "Bộ DEMO vượt giới hạn thử. Anh giảm phạm vi bộ thử.")
        if bam(data) != checksum:
            raise loi("TC_SAI_NGUON", "Bộ DEMO không khớp bản ghim. Anh nhờ lead kiểm tra lại bộ thử.")
        files[ten] = data
    try:
        corpus, gold = (json_nghiem(files[n]) for n in ("bo-ca-DEMO.json", "dap-an-DEMO.json"))
        if any(v["nhan"] != "DEMO" or v["phien_ban"] != 1 for v in (corpus, gold)):
            raise ValueError
        cases, answers = corpus["kich_ban"], gold["dap_an"]
        if not cases or len(cases) > 200 or len({c["ma"] for c in cases}) != len(cases):
            raise ValueError
        if {c["ma"] for c in cases} != set(answers):
            raise ValueError
        for source in corpus["nguon"].values():
            data = files[source["tep"]]
            if bam(data) != source["bam"] or len(data) != source["bytes"] or not source["phien_ban"]:
                raise ValueError
        for c in cases:
            if c["tac_vu"] not in TAC_VU or not set(c["nguon"]) <= set(corpus["nguon"]):
                raise ValueError
            a = answers[c["ma"]]
            if not set(a["chi_so"]) <= set(CHI_SO) or len(set(a["chi_so"])) != len(a["chi_so"]):
                raise ValueError
        # local là phản hồi giả lịch sử của TC-10, tuyệt đối không gửi đi.
        gui = deepcopy(corpus)
        for c in gui["kich_ban"]:
            c.pop("local", None)
        return {"corpus": gui, "dap_an": answers, "files": files, "bam_bo": bam_bo,
                "bam_ca": pins["bo-ca-DEMO.json"], "bam_dap_an": pins["dap-an-DEMO.json"],
                "da_duyet_nghiep_vu": corpus.get("da_duyet_nghiep_vu") is True and gold.get("da_duyet_nghiep_vu") is True}
    except (KeyError, TypeError, ValueError):
        raise loi() from None


def nap_ghim(path=None, checksum=None):
    if path is None:
        return None
    raw = doc_tep(path)
    if not la_bam(checksum) or bam(raw) != checksum:
        raise loi("TC_SAI_NGUON", "Bản ghim bài thử không khớp. Anh nhờ lead kiểm tra lại.")
    v = json_nghiem(raw)
    # Chỉ dấu phiên bản/băm trên Core; KHÔNG tệp giá trị cấu hình engine.
    if (not isinstance(v, dict) or set(v) != {"nhan", "phien_ban", "engine", "danh_muc", "cau_hinh", "prompt"}
            or v["nhan"] != "DEMO" or v["phien_ban"] != 1):
        raise loi()
    for key in ("engine", "danh_muc", "cau_hinh"):
        p = v[key]
        if (not isinstance(p, dict) or set(p) != {"phien_ban", "bam"}
                or not ten_an_toan(p["phien_ban"]) or not la_bam(p["bam"])):
            raise loi()
    if not isinstance(v["prompt"], dict) or set(v["prompt"]) != set(TAC_VU) - {"cat_doan"}:
        raise loi()
    for p in v["prompt"].values():
        if (not isinstance(p, dict) or set(p) != {"ma", "phien_ban", "bam"}
                or not all(ten_an_toan(p[k]) for k in ("ma", "phien_ban")) or not la_bam(p["bam"])):
            raise loi()
    return v


class CoreThat:
    """Chốt thiếu hợp đồng, không đoán route/auth/schema Core.

    Không dùng API nhận việc của engine làm API nộp việc. Lead cần adapter
    public discovery/tokenizer/chuỗi/kết quả trước khi mở cửa này. Không có
    tùy chọn CLI tải Python/plugin hoặc bỏ qua kiểm môi trường.
    """
    la_gia = False

    def __init__(self, core_url):
        self.core_url = kiem_url(core_url)

    def kiem_moi_truong(self, ghim):
        # Chưa có cửa chung được công bố cho bài đo. Không hỏi khóa vô ích,
        # không network/getpass/env/DB; không lấy cờ CLI làm chứng thực Core.
        raise thieu_moi_truong()


def so(v, *, nguyen=False, duong=False):
    return (type(v) in ({int} if nguyen else {int, float}) and 0 <= v <= 10**12 and math.isfinite(v)
            and (v > 0 if duong else v >= 0))


def kiem_moi_truong(env, ghim):
    if not ghim or not isinstance(env, dict):
        raise thieu_moi_truong()
    for dich_vu in ("core", "ai", "ocr", "tx", "embedding"):
        s = env.get(dich_vu, {})
        if not isinstance(s, dict) or s.get("co_that") is not True or not la_bam(s.get("bam_kiem")):
            raise thieu_moi_truong()
    if env.get("ghim") != ghim or env.get("chi_local") is not True:
        raise thieu_moi_truong()
    models = env.get("models")
    if (not isinstance(models, list) or len(models) != 3 or not all(isinstance(m, dict) for m in models)
            or {m.get("vai_tro") for m in models} != set(VAI_TRO)):
        raise thieu_moi_truong()
    if len({m.get("id") for m in models}) != 3:
        raise thieu_moi_truong()
    for m in [*models, env["embedding"]]:
        if (not all(ten_an_toan(m.get(k)) for k in ("id", "runtime", "phien_ban"))
                or not la_bam(m.get("bam_phat_hien")) or m.get("local") is not True
                or not so(m.get("context_hieu_dung"), nguyen=True, duong=True)):
            raise thieu_moi_truong()
    # Capability + bằng chứng do Core/Hỏi AI cấp; không suy từ tên model.
    e = env["embedding"]
    if (e.get("lead_chon") is not True or e.get("ho_tro_nhung") is not True
            or not la_bam(e.get("bam_kiem_tieng_viet"))):
        raise thieu_moi_truong()
    return models


def rut_khang_dinh(kq, trich=False):
    out = []
    for k in kq.get("khang_dinh", []):
        item = {"thuc_the": k["thuc_the"]["ma"], **{t: k[t] for t in ("truong", "gia_tri", "don_vi")}}
        if trich:
            item["can_cu"] = [{**{t: c["nguon"][t] for t in ("ma_nguon", "phien_ban_nguon", "bam_goc")},
                                **{t: c[t] for t in ("cau", "bat_dau", "ket_thuc")}} for c in k["can_cu"]]
        out.append(item)
    return out


def cham(gold, out):
    """Bộ chấm TC-10 theo giá trị/thực thể/nguồn/offset; không điểm tự khai."""
    checks = {k: False for k in gold["chi_so"]}
    try:
        k = out["ket_qua"]
        expected = gold.get("khang_dinh", [])
        if "tra_loi_dung" in checks:
            checks["tra_loi_dung"] = (k.get("co_can_cu") is True
                and json_bytes(rut_khang_dinh(k)) == json_bytes([{t: v for t, v in x.items() if t != "can_cu"} for x in expected])
                and all(k.get(t) == gold[t] for t in ("tra_loi", "co_mau_thuan", "nhan")))
        if "trich_dan_dung" in checks:
            checks["trich_dan_dung"] = bool(expected) and json_bytes(rut_khang_dinh(k, True)) == json_bytes(expected)
        if "tu_choi_dung" in checks:
            checks["tu_choi_dung"] = (k.get("trang_thai") == "khong_thay_can_cu" and k.get("co_can_cu") is False
                and k.get("khang_dinh") == [] and k.get("nhan") is None and bool(k.get("tra_loi"))
                and not any(c.isdigit() for c in k["tra_loi"]))
        if "phan_loai_dung" in checks:
            checks["phan_loai_dung"] = (out["giai_doan"] == gold["giai_doan"]
                and all(k.get(t) == gold[t] for t in ("nhom_de_xuat", "loai_de_xuat"))
                and set(gold["ly_do"]) <= set(k["kiem_tra"]["ma_ly_do"])
                and k["kiem_tra"]["chi_la_de_xuat"] is True and k["kiem_tra"]["diem_la_xac_suat"] is False)
    except (KeyError, TypeError, ValueError):
        pass  # Kết quả thiếu không được tính đạt.
    return checks


def cham_chi_tiet(gold, out, tac_vu):
    result = {}
    key = {"cat_doan": "cat_doan_vi_tri", "phan_tich_cau_hoi": "cau_hoi_ham", "xep_hang_lai": "xep_hang"}.get(tac_vu)
    if key and "du_lieu" in gold:
        # Đáp án bổ sung ghim toàn bộ vị trí/đoạn/hàm/tham số/hoán vị ứng viên.
        result[key] = json_bytes(out.get("ket_qua")) == json_bytes(gold["du_lieu"])
    expected = gold.get("khang_dinh", [])
    for ten in ("tien", "ngay"):
        if ten == "tien":
            items = [k for k in expected if isinstance(k.get("gia_tri"), dict) and "tien_te" in k["gia_tri"]]
        else:
            items = [k for k in expected if isinstance(k.get("gia_tri"), str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", k["gia_tri"])]
        if items:
            try:
                got = rut_khang_dinh(out["ket_qua"])
                result[ten] = all({t: v for t, v in k.items() if t != "can_cu"} in got for k in items)
            except (KeyError, TypeError):
                result[ten] = False
    return result


def ty_le(values, du_kien):
    tu, mau = sum(v is True for v in values), len(values)
    return {"tu_so": tu, "mau_so": mau, "so_ca_du_kien": du_kien,
            "chua_do": max(0, du_kien - mau), "ty_le": tu / mau if mau else None,
            "ly_do": None if mau == du_kien and mau else CAU_THIEU}


def tong_hop(bo, rows):
    gold = bo["dap_an"]
    return {c: ty_le([r["chi_so"][c] for r in rows if c in r["chi_so"]],
                    sum(c in v["chi_so"] for v in gold.values())) for c in CHI_SO}


def bao_cao_moi(bo, ghim=None, *, gia=False):
    return {"nhan": "DEMO", "phien_ban": 1, "phep_do": "TC-11", "trang_thai": "chua_do",
        "moi_truong": "adapter_gia" if gia else "chua_kiem", "core_that": "chua_kiem",
        "ket_luan_phep_do_that": "CHỜ ANH TỰ CHẠY", "bam_bo": bo["bam_bo"], "bam_ca": bo["bam_ca"],
        "bam_dap_an": bo["bam_dap_an"], "ghim": ghim, "da_duyet_nghiep_vu": bo["da_duyet_nghiep_vu"],
        "so_luot_cloud": 0, "so_viec_gui": 0, "model_duoc_chot": None, "nguong_duoc_chot": None,
        "accuracy_model_that": None, "models": [], "cac_ca": [], "chi_so": tong_hop(bo, []),
        "chi_tiet": {k: ty_le([], 0) for k in CHI_TIET},
        "kiem_core": {k: {"trang_thai": "chua_kiem", "bam_bien_ban": None, "ly_do": CAU_THIEU} for k in CA_CORE},
        "ly_do_thieu": {k: CAU_THIEU for k in SO_DO}, **{k: None for k in SO_DO}}


def so_do_runtime(raw):
    raw = raw if isinstance(raw, dict) else {}
    if raw.get("nguon") != "runtime_qua_core":
        raw = {}  # Ký tự/4 hoặc số không rõ nguồn tuyệt đối không là telemetry.
    out, reasons = {}, {}
    for k in SO_DO:
        v = raw.get(k)
        valid = so(v, nguyen=k not in {"thoi_gian_runtime_giay", "thoi_gian_core_giay"}, duong=k == "context_hieu_dung")
        out[k] = v if valid else None
        if not valid:
            reasons[k] = CAU_THIEU
    out["ly_do_thieu"] = reasons
    return out


def nhan_bien_ban_core(report, items, *, gia):
    # Không nhận cờ boolean đơn lẻ. Chỉ kết quả của adapter Core, có băm biên
    # bản; bài tải riêng phải ghi số người và số đồng thời thực sự đo.
    for key in CA_CORE:
        b = items.get(key, {}) if isinstance(items, dict) else {}
        if not isinstance(b, dict) or b.get("trang_thai") not in {"dat", "khong_dat"} or not la_bam(b.get("bam_bien_ban")):
            continue
        if key.startswith("tai_") and (b.get("bai_tai_rieng") is not True
                or not so(b.get("so_nguoi"), nguyen=True, duong=True)
                or not so(b.get("dong_thoi"), nguyen=True, duong=True)
                or (key == "tai_20_dong_thoi" and b["dong_thoi"] < 20)
                or (key == "tai_150_nguoi" and b["so_nguoi"] < 150)):
            continue
        report["kiem_core"][key] = {"trang_thai": "da_kiem_gia" if gia else b["trang_thai"],
            "ket_qua_adapter": b["trang_thai"], "bam_bien_ban": b["bam_bien_ban"], "ly_do": None}
        if key.startswith("tai_"):
            report["kiem_core"][key].update({k: b[k] for k in ("so_nguoi", "dong_thoi")})


def kiem_context(plan, model):
    # Tokenizer phải đếm ĐẦY ĐỦ khuôn/prompt/context/wrapper, cộng dự phòng
    # đầu ra. Ký tự/4 không tham gia quyết định cho phép gửi.
    if (not isinstance(plan, dict) or plan.get("nguon_dem") != "tokenizer_runtime"
            or plan.get("day_du_khung") is not True or plan.get("model_id") != model["id"]
            or not la_bam(plan.get("bam_noi_dung_gui"))
            or not so(plan.get("token_vao"), nguyen=True)
            or not so(plan.get("token_ra_du_phong"), nguyen=True, duong=True)):
        raise thieu_moi_truong()
    if plan["token_vao"] + plan["token_ra_du_phong"] > model["context_hieu_dung"]:
        raise loi("TC_QUA_NGAN_SACH_AI", "Ngữ cảnh vượt sức chứa đã kiểm của model. Anh giảm phạm vi câu hỏi hoặc tài liệu.")


def ket_so_lieu(r, bo):
    for i, m in enumerate(r["models"]):
        rows = [row for row in r["cac_ca"] if row["model"] == i]
        m["chi_so"] = tong_hop(bo, rows)
        m["chi_tiet"] = {}
        for key in CHI_TIET:
            vals = [row["chi_tiet"][key] for row in rows if key in row["chi_tiet"]]
            du_kien = sum(key in cham_chi_tiet(bo["dap_an"][c["ma"]], {}, c["tac_vu"]) for c in bo["corpus"]["kich_ban"])
            m["chi_tiet"][key] = ty_le(vals, du_kien)
        m["so_ca_chua_xong"] = len(bo["corpus"]["kich_ban"]) - sum(row["trang_thai"] in {"da_do", "da_do_gia"} for row in rows)
    if r["models"]:
        r["chi_so"] = None
        r["ly_do_chi_so"] = "Xem tử số/mẫu số riêng từng model; không gộp ba model."
        r["chi_tiet"] = None


def chay(bo, ghim=None, adapter=None, *, kiem_huy=lambda: None):
    """Mỗi ca chỉ nộp một lần; không poll/retry/chuyển Cloud/batch.

    Adapter (chỉ test tại lát này): kiem_moi_truong, chuan_bi, gui_viec,
    nhan_ket_qua, bien_ban_core, giu_bao_cao. Core giữ quyền/chuỗi/kho tệp.
    """
    gia = bool(getattr(adapter, "la_gia", False))
    r = bao_cao_moi(bo, ghim, gia=gia)
    if adapter is None:
        r["trang_thai"] = "chay_kho"
        return r, 0
    try:
        kiem_huy()
        env = adapter.kiem_moi_truong(deepcopy(ghim))
        models = kiem_moi_truong(env, ghim)
        r["models"] = [{k: m[k] for k in ("vai_tro", "id", "runtime", "phien_ban", "context_hieu_dung", "bam_phat_hien")} for m in models]
        r["embedding"] = {k: env["embedding"][k] for k in ("id", "runtime", "phien_ban", "context_hieu_dung", "bam_phat_hien", "bam_kiem_tieng_viet")}
        for model_index, model in enumerate(models):
            rows = []
            for index, c in enumerate(bo["corpus"]["kich_ban"]):
                kiem_huy()
                row = {"model": model_index, "ca": index, "trang_thai": "chua_do", "chi_so": {}, "chi_tiet": {},
                       "thoi_gian_cong_cu_giay": None, **so_do_runtime({})}
                row["ly_do_thieu"]["thoi_gian_cong_cu_giay"] = CAU_THIEU
                r["cac_ca"].append(row)
                try:
                    plan = adapter.chuan_bi(deepcopy(c), deepcopy(model), deepcopy(ghim))
                    if (not isinstance(plan, dict) or not ten_an_toan(plan.get("ma_tuong_quan"))
                            or type(plan.get("goi_ai")) is not bool
                            or not la_bam(plan.get("bam_noi_dung_gui"))
                            or plan["goi_ai"] != c.get("ai", c["tac_vu"] != "cat_doan")):
                        raise thieu_moi_truong()
                    if plan["goi_ai"]:
                        kiem_context(plan, model)
                    kiem_huy()
                    start = time.perf_counter()
                    # Đối số không có đáp án/Local giả/files chứa đáp án.
                    r["so_viec_gui"] += 1
                    try:
                        ticket = adapter.gui_viec(deepcopy(c), deepcopy(model), deepcopy(plan))
                    except (OSError, TimeoutError):
                        raise ChuaRo(plan["ma_tuong_quan"]) from None
                    if not isinstance(ticket, dict) or ticket.get("ma_tuong_quan") != plan["ma_tuong_quan"]:
                        raise ChuaRo(plan["ma_tuong_quan"])
                    if ticket.get("http") == 202 or ticket.get("trang_thai") in {"CHO", "CHUA_RO"}:
                        raise ChuaRo(ticket["ma_tuong_quan"])
                    kiem_huy()
                    try:
                        result = adapter.nhan_ket_qua(ticket)
                    except (OSError, TimeoutError):
                        raise ChuaRo(ticket["ma_tuong_quan"]) from None
                    row["thoi_gian_cong_cu_giay"] = time.perf_counter() - start
                    row["ly_do_thieu"].pop("thoi_gian_cong_cu_giay", None)
                    if not isinstance(result, dict):
                        raise ChuaRo(ticket["ma_tuong_quan"])
                    status = result.get("trang_thai")
                    if status in {"CHO", "CHUA_RO"}:
                        raise ChuaRo(ticket["ma_tuong_quan"])
                    if status == "HUY":
                        raise KeyboardInterrupt
                    if status != "XONG":
                        raise loi("TC_THU_KHONG_DAT", "Việc thử DEMO chưa hoàn tất thành công.")
                    # Kiểm danh tính runtime thật của lượt; không gán số của
                    # model khác hoặc biến ký tự/4 thành token đo được.
                    if ((plan["goi_ai"] and (result.get("model_id") != model["id"] or result.get("local") is not True
                            or result.get("model_phien_ban") != model["phien_ban"]
                            or result.get("runtime") != model["runtime"]))
                            or result.get("ghim") != ghim
                            or result.get("bam_noi_dung_gui") != plan.get("bam_noi_dung_gui")
                            or result.get("cat_ngam") is not False or result.get("batch") is not False):
                        raise thieu_moi_truong()
                    out = result.get("dau_ra", {})
                    row.update(trang_thai="da_do_gia" if gia else "da_do",
                               chi_so=cham(bo["dap_an"][c["ma"]], out),
                               chi_tiet=cham_chi_tiet(bo["dap_an"][c["ma"]], out, c["tac_vu"]))
                    row.update(so_do_runtime(result.get("so_do")))
                    row["nguon_so_do"] = "adapter_gia" if gia else "runtime_qua_core"
                    row["goi_ai"] = plan["goi_ai"]
                    if plan["goi_ai"]:
                        row["context_hieu_dung"] = model["context_hieu_dung"]
                        row["ly_do_thieu"].pop("context_hieu_dung", None)
                    else:
                        for k in ("context_hieu_dung", "token_vao", "token_ra"):
                            row[k] = None
                            row["ly_do_thieu"][k] = "Không áp dụng: đường Python không gọi AI."
                except LoiNghiepVu as exc:
                    if exc.ma != "TC_QUA_NGAN_SACH_AI":
                        raise
                    row.update(trang_thai="tu_choi_context", ma_loi=exc.ma)
                rows.append(row)
            r["models"][model_index]["chi_so"] = tong_hop(bo, rows)
        nhan_bien_ban_core(r, adapter.bien_ban_core(), gia=gia)
        r["trang_thai"] = "da_kiem_adapter_gia" if gia else "da_do_chua_nghiem_thu"
        ket_so_lieu(r, bo)
        # Ưu tiên RAM/Core. Không fallback ghi đĩa nếu Core chưa có cửa báo cáo.
        adapter.giu_bao_cao(deepcopy(r))
        du = all(not any(v == CAU_THIEU for v in row.get("ly_do_thieu", {"chua_do": CAU_THIEU}).values()) for row in r["cac_ca"])
        dat = all(all(row["chi_so"].values()) and all(row["chi_tiet"].values()) for row in r["cac_ca"])
        day_du = all(m["chi_tiet"][k]["mau_so"] for m in r["models"] for k in CHI_TIET)
        core_du = all(v["trang_thai"] in {"dat", "da_kiem_gia"} for v in r["kiem_core"].values())
        core_sai = any(v.get("ket_qua_adapter") == "khong_dat" for v in r["kiem_core"].values())
        return r, (1 if not dat or core_sai else 2 if not du or not day_du or not core_du else 0)
    except BaseException as exc:
        ket_so_lieu(r, bo)
        if isinstance(exc, ChuaRo):
            r["trang_thai"] = "chua_ro"
            r["bam_ma_tuong_quan"] = bam(str(exc.ma_tuong_quan).encode("utf-8", errors="replace"))
        elif isinstance(exc, KeyboardInterrupt):
            r["trang_thai"] = "huy"
        else:
            r["trang_thai"] = "chua_kiem"
        if isinstance(exc, (ChuaRo, KeyboardInterrupt)) or (isinstance(exc, LoiNghiepVu) and getattr(exc, "tc11_noi_bo", False)):
            exc.bao_cao = r
            raise
        wrapped = loi("TC_THU_KHONG_HOAN_TAT", "Chưa hoàn tất bài thử DEMO. Anh nhờ lead kiểm tra cửa Core và đầu vào.")
        wrapped.bao_cao = r
        raise wrapped from None


def duong_bao_cao(path, workspace):
    if not workspace:
        raise loi("TC_BAO_CAO_KHONG_HOP_LE", "Anh chỉ định workspace khi xuất báo cáo DEMO.")
    try:
        root = Path(workspace).resolve(strict=True)
        target = Path(path).resolve()
        relative = target.relative_to(root)
        cam = {"goi", ".git", ".venv", "ma-nguon", "in", "out", "jobs", "state", "var"}
        if (not root.is_dir() or target.suffix != ".json" or target.exists()
                or not target.parent.is_dir() or any(p.lower() in cam for p in root.parts + relative.parts)
                or not re.fullmatch(r"[A-Za-z0-9_-]*DEMO[A-Za-z0-9_-]*\.json", target.name)):
            raise ValueError
        return target
    except (OSError, ValueError):
        raise loi("TC_BAO_CAO_KHONG_HOP_LE", "Chọn artifact DEMO mới trong workspace, ngoài thư mục gói và dữ liệu hệ thống.") from None


def ghi_bao_cao(path, report):
    # Report được dựng theo allowlist; không nguồn, câu hỏi, đáp án, khóa,
    # URL, đường tệp, thông điệp tùy ý hoặc ID việc từ adapter.
    try:
        with path.open("xb") as f:
            f.write(json_bytes(report) + b"\n")
    except OSError:
        raise loi("TC_BAO_CAO_KHONG_HOP_LE", "Không ghi được artifact DEMO. Anh chọn tên mới trong workspace có quyền ghi.") from None


class BoDocLenh(argparse.ArgumentParser):
    def error(self, message):
        # argparse mặc định phản chiếu đối số (có thể là khóa/path) ra log.
        raise loi("TC_THAM_SO_KHONG_HOP_LE", "Tham số chưa hợp lệ. Anh xem --help; không truyền khóa trên dòng lệnh.")


def main(argv=None):
    p = BoDocLenh(description=__doc__, allow_abbrev=False)
    p.add_argument("--that", action="store_true", help="Anh tự chạy; thiếu cửa chung Core thì từ chối trước kết nối.")
    p.add_argument("--core", help="Địa chỉ Core do Anh cấp, không kèm khóa.")
    p.add_argument("--bo-demo", type=Path, help="Thư mục bộ DEMO do lead cấp.")
    p.add_argument("--bam-bo", help="SHA-256 bytes bam-DEMO.json, lead xác nhận ngoài bộ thử.")
    p.add_argument("--ghim", type=Path, help="Manifest DEMO chỉ dấu phiên bản/băm trên Core, không giá trị cấu hình.")
    p.add_argument("--bam-ghim", help="SHA-256 bytes manifest ghim.")
    p.add_argument("--bao-cao", type=Path, help="Chỉ khi Anh chọn: artifact mới có DEMO trong tên, đuôi .json.")
    p.add_argument("--workspace", type=Path, help="Workspace được Anh chọn cho artifact.")
    report, target = None, None
    try:
        a = p.parse_args(argv)
        if a.bao_cao:
            target = duong_bao_cao(a.bao_cao, a.workspace)
        if (bool(a.bo_demo) != bool(a.bam_bo) or bool(a.ghim) != bool(a.bam_ghim)
                or (a.that and not all((a.core, a.bo_demo, a.bam_bo, a.ghim, a.bam_ghim)))):
            raise loi("TC_THAM_SO_KHONG_HOP_LE", "Chạy thật cần địa chỉ Core, bộ DEMO và bản ghim có băm do Anh hoặc lead cấp.")
        bo = nap_bo(a.bo_demo or DEMO, a.bam_bo or BAM_BO_MAC_DINH)
        ghim = nap_ghim(a.ghim, a.bam_ghim)
        adapter = CoreThat(a.core) if a.that else None
        report, code = chay(bo, ghim, adapter)
        if not a.that:
            print("CHẠY KHÔ: đã kiểm băm bộ DEMO; không mạng/ghi bền mặc định. Phép đo thật CHỜ ANH TỰ CHẠY.")
    except (LoiNghiepVu, ChuaRo, KeyboardInterrupt) as exc:
        report = getattr(exc, "bao_cao", report)
        if isinstance(exc, LoiNghiepVu):
            print(exc.thong_diep, file=sys.stderr)
            code = 2
        elif isinstance(exc, ChuaRo):
            print("Nguồn đã nhận việc nhưng chưa trả. Anh nhờ Core kiểm tra lượt hiện tại; không tự gửi lại.", file=sys.stderr)
            code = 2
        else:
            print("Đã dừng bài thử. Việc đã gửi cần kiểm tra trạng thái tại Core trước khi thử tiếp.", file=sys.stderr)
            code = 130
    except Exception:
        print("Chưa hoàn tất bài thử DEMO. Anh nhờ lead kiểm tra đầu vào và workspace.", file=sys.stderr)
        code = 2
    if target and report:
        try:
            ghi_bao_cao(target, report)
        except LoiNghiepVu as exc:
            print(exc.thong_diep, file=sys.stderr)
            return 2
    return code


if __name__ == "__main__":
    raise SystemExit(main())
