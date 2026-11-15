"""DC-13: công cụ đo DEMO ngoài runtime; mặc định chạy khô, chỉ Core qua handle.

Binding handle là đề nghị chờ Core review, không phải API SDK đã phát hành.
Không mở mạng, tải model, đọc tệp Word/scan, tìm cấu hình hoặc nhận khóa.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import queue
import re
import sys
import threading
import time

sys.dont_write_bytecode = True

from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu

WORKSPACE = Path(__file__).resolve().parents[2]
TRAN_BYTE = 4 * 1024 * 1024
CHO_ANH = "CHỜ ANH TỰ CHẠY"
LY_DO_THIEU = "Chưa có số đo đầy đủ từ Core; không tính là đạt."


def loi(ma="DC_DU_LIEU_THU_KHONG_HOP_LE"):
    cau = {
        "DC_CHUA_CO_MOI_TRUONG_THU": "Chưa có đủ môi trường Core, OCR và Local để thử DEMO.",
        "DC_HUY": "Đã dừng công cụ thử; kiểm tra trạng thái việc tại Core trước khi chạy tiếp.",
        "DC_LOI_NGUON_THU": "Nguồn thử báo lỗi; xem trạng thái việc tại Core.",
        "DC_BAO_CAO_KHONG_HOP_LE": "Chọn một tệp JSON DEMO mới trong workspace, ngoài thư mục gói.",
        "DC_THAM_SO_KHONG_HOP_LE": "Tham số chưa hợp lệ; xem hướng dẫn chạy công cụ.",
    }
    return LoiNghiepVu(ma, cau.get(ma, "Dữ liệu đo DEMO chưa hợp lệ hoặc vượt giới hạn."))


def so(x, *, nguyen=False, toi_thieu=0):
    try:
        return (type(x) is int if nguyen else type(x) in (int, float)) and math.isfinite(x) and x >= toi_thieu
    except OverflowError:
        return False


def ma_demo(x):
    return type(x) is str and re.fullmatch(r"DEMO-[A-Za-z0-9_-]{1,80}", x) is not None


def ma_core(x):
    return type(x) is str and re.fullmatch(r"[A-Za-z0-9_-]{1,160}", x) is not None


def bam(x):
    return type(x) is str and re.fullmatch(r"sha256:[a-f0-9]{64}", x) is not None


def ma_tuong_quan(x):
    if not ma_demo(x):
        raise loi()
    return x


def doc_json(raw):
    def cap(ds):
        d = {}
        for k, v in ds:
            if k in d:
                raise ValueError()
            d[k] = v
        return d
    try:
        if len(raw) > TRAN_BYTE:
            raise ValueError()
        return json.loads(raw, object_pairs_hook=cap, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
    except (ValueError, UnicodeError, RecursionError):
        raise loi() from None


def duong_workspace(ten, *, ghi=False):
    """Chỉ tệp được chỉ rõ; chặn liên kết ở mọi thành phần, không dò dữ liệu."""
    ma_loi = "DC_BAO_CAO_KHONG_HOP_LE" if ghi else "DC_DU_LIEU_THU_KHONG_HOP_LE"
    try:
        p = Path(ten)
        if not p.is_absolute():
            p = WORKSPACE / p
        # Kiểm trước resolve để không đi xuyên symlink/junction.
        for a in (p, *p.parents):
            if a.is_symlink() or getattr(a, "is_junction", lambda: False)():
                raise ValueError()
        p = p.resolve()
        rel = p.relative_to(WORKSPACE)
        cam = {"goi", ".git", ".env", "cau_hinh.that.toml", "var", "ma-nguon", "abbyy-hotfolder"}
        if any(v.lower() in cam or ":" in v for v in rel.parts) or p.suffix.lower() != ".json":
            raise ValueError()
        if ghi and (not p.name.startswith("DEMO-") or p.exists() or not p.parent.is_dir()):
            raise ValueError()
        if not ghi and (not p.is_file() or p.stat().st_size > TRAN_BYTE):
            raise ValueError()
        return p
    except (OSError, ValueError):
        raise loi(ma_loi) from None


def neo_dung(n):
    return (type(n) is dict and set(n) == {"bat_dau", "ket_thuc"}
            and so(n["bat_dau"], nguyen=True) and so(n["ket_thuc"], nguyen=True)
            and n["bat_dau"] <= n["ket_thuc"] <= 500000)


def giao_neo(a, b):
    if a["bat_dau"] == a["ket_thuc"]:
        return b["bat_dau"] <= a["bat_dau"] <= b["ket_thuc"]
    if b["bat_dau"] == b["ket_thuc"]:
        return a["bat_dau"] <= b["bat_dau"] <= a["ket_thuc"]
    return max(a["bat_dau"], b["bat_dau"]) < min(a["ket_thuc"], b["ket_thuc"])


def vung_dung(v):
    return (type(v) is dict and set(v) == {"trang", "hop"}
            and so(v["trang"], nguyen=True, toi_thieu=1)
            and type(v["hop"]) is list and len(v["hop"]) == 4
            and all(so(x) for x in v["hop"])
            and v["hop"][0] < v["hop"][2] and v["hop"][1] < v["hop"][3])


def kiem_bo(bo):
    try:
        if (set(bo) != {"phien_ban", "nhan", "ma_bo", "dap_an_day_du", "ca"}
                or type(bo["phien_ban"]) is not int or bo["phien_ban"] != 1
                or bo["nhan"] != "DEMO" or not ma_demo(bo["ma_bo"])
                or bo["dap_an_day_du"] is not True or not 1 <= len(bo["ca"]) <= 100):
            raise ValueError()
        mas = []
        for c in bo["ca"]:
            if (set(c) != {"ma", "word", "scan", "so_trang", "so_vung_can_ocr", "diem", "vung_sua_tay"}
                    or not ma_demo(c["ma"]) or not so(c["so_trang"], nguyen=True, toi_thieu=1)
                    or c["so_trang"] > 60 or not so(c["so_vung_can_ocr"], nguyen=True)
                    or len(c["diem"]) > 10000 or len(c["vung_sua_tay"]) > 10000):
                raise ValueError()
            mas.append(c["ma"])
            for ben, mime in (("word", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                              ("scan", "application/pdf")):
                t = c[ben]
                if (set(t) != {"tep_id", "bam", "mime"} or not ma_core(t["tep_id"])
                        or not bam(t["bam"]) or t["mime"] != mime):
                    raise ValueError()
            for d in c["diem"]:
                if (set(d) != {"neo", "nghiem_trong", "sua_that"} or not neo_dung(d["neo"])
                        or type(d["nghiem_trong"]) is not bool or type(d["sua_that"]) is not bool
                        or (d["nghiem_trong"] and not d["sua_that"])):
                    raise ValueError()
            ns = sorted((d["neo"]["bat_dau"], d["neo"]["ket_thuc"]) for d in c["diem"])
            if any(a[1] > b[0] for a, b in zip(ns, ns[1:])):
                raise ValueError()
            if any(not vung_dung(v) or v["trang"] > c["so_trang"] for v in c["vung_sua_tay"]):
                raise ValueError()
        if len(set(mas)) != len(mas):
            raise ValueError()
    except (KeyError, TypeError, ValueError):
        raise loi() from None
    return bo


def phep_do(tu=None, mau=None, ly_do=LY_DO_THIEU):
    dat_so = so(tu) and so(mau) and mau > 0
    return {"tu_so": tu, "mau_so": mau, "gia_tri": tu / mau if dat_so else None,
            "ly_do": None if dat_so else ly_do}


def trang_thai_cong(bat_du, bi_an):
    # Một phép đo đã thất bại vẫn là thất bại dù phép đo kia chưa có.
    if (bat_du["gia_tri"] is not None and bat_du["tu_so"] != bat_du["mau_so"]) or (
            bi_an["gia_tri"] is not None and bi_an["tu_so"] > 0):
        return "KHONG_DAT"
    if bat_du["gia_tri"] is None or bi_an["gia_tri"] is None:
        return "CHUA_DO"
    return "DAT_TREN_BO_DEMO"


def khung_bao_cao():
    return {"phien_ban": 1, "nhan": "DEMO", "che_do": "CHAY_KHO", "cong_chat_luong": "CHUA_DO",
            "ket_luan_do": "CHUA_DO",
            "nghiem_trong": phep_do(), "sua_that_bi_an": phep_do(), "sua_that_bo_sot": phep_do(),
            "so_do_chay_kho": {k: phep_do() for k in ("toa_do_tu_abbyy", "co_nghi_ngo_abbyy",
                "ocr_lai_vung_dung_word", "tu_dien", "detector_recall", "detector_precision",
                "lech_gia_moi_trang", "lech_dau_trang", "giay_xu_ly_core", "ram_dinh_bytes")},
            "pham_vi": "Hai chỉ tiêu trên bộ mẫu không chứng minh bảo đảm trên mọi tài liệu.",
            "phep_do_that": CHO_ANH, "ca": [],
            "nguong_trinh_anh": {"detector": None, "lech_gia": None, "ocr_kem": None,
                                 "ly_do": "Trình Anh duyệt dựa số đo; chưa đặt ngưỡng vận hành."},
            "trinh_duyet_core": {k: {"ket_qua": None, "ly_do": CHO_ANH} for k in (
                "hai_cot_va_anh", "bon_xac_nhan", "cas", "quyen", "chan_hieu_luc",
                "mo_hieu_luc", "hai_nguoi_q03", "bang_chung_demo")}}


def cham_ca(c, r, iou):
    """Chấm đáp án độc lập trong RAM; không gửi đáp án cho nguồn xử lý."""
    out = {"so_trang": c["so_trang"], "so_diem_dap_an": len(c["diem"])}
    ds = r.get("diem")
    day_du = r.get("diem_day_du") is True and type(ds) is list and len(ds) <= 10000
    if day_du:
        for d in ds:
            if (type(d) is not dict or not neo_dung(d.get("neo"))
                    or d.get("muc") not in {"nghiem_trong", "can_xem", "hinh_thuc", "nhieu_ocr"}
                    or type(d.get("an_mac_dinh")) is not bool):
                raise loi()
        # Ghép giao khoảng trên nguyên văn Word, một-một; mơ hồ giữ chưa đo.
        gh = [[j for j, d in enumerate(ds) if giao_neo(g["neo"], d["neo"])] for g in c["diem"]]
        used = [j for js in gh for j in js]
        if any(len(js) > 1 for js in gh) or len(used) != len(set(used)):
            day_du = False
    n = sum(g["nghiem_trong"] for g in c["diem"])
    m = sum(g["sua_that"] for g in c["diem"])
    if day_du:
        bat = an = sot = 0
        for g, js in zip(c["diem"], gh):
            d = ds[js[0]] if js else None
            if g["nghiem_trong"] and d and d["muc"] == "nghiem_trong" and not d["an_mac_dinh"]:
                bat += 1
            if g["sua_that"]:
                an += bool(d and (d["muc"] == "nhieu_ocr" or d["an_mac_dinh"]))
                sot += d is None
        sua_that_theo_j = {j: g["sua_that"] for g, js in zip(c["diem"], gh) for j in js}
        fp = sum(d["muc"] == "can_xem" for j, d in enumerate(ds) if not sua_that_theo_j.get(j, False))
        out.update(nghiem_trong=phep_do(bat, n), sua_that_bi_an=phep_do(an, m),
                   sua_that_bo_sot=phep_do(sot, m), lech_gia_moi_trang=phep_do(fp, c["so_trang"]))
    else:
        out.update(nghiem_trong=phep_do(None, n), sua_that_bi_an=phep_do(None, m),
                   sua_that_bo_sot=phep_do(None, m), lech_gia_moi_trang=phep_do(None, c["so_trang"]))
    tu = r.get("tu_abbyy")
    if type(tu) is list and len(tu) <= 500000:
        hop = co = 0
        for t in tu:
            if type(t) is not dict:
                raise loi()
            h = t.get("hop")
            if h is not None:
                if not vung_dung({"trang": 1, "hop": h}):
                    raise loi()
                hop += 1
            v = t.get("nghi_ngo")
            if v is not None and type(v) is not bool:
                raise loi()
            co += v is not None  # false là cờ thật có giá trị, khác thiếu cờ.
        out["toa_do_tu_abbyy"] = phep_do(hop, len(tu))
        out["co_nghi_ngo_abbyy"] = phep_do(co, len(tu))
    else:
        out["toa_do_tu_abbyy"] = phep_do()
        out["co_nghi_ngo_abbyy"] = phep_do()
    ocr = r.get("ocr_vung")
    if type(ocr) is list and len(ocr) == c["so_vung_can_ocr"] and all(type(x) is bool for x in ocr):
        out["ocr_lai_vung_dung_word"] = phep_do(sum(ocr), len(ocr))
    else:
        out["ocr_lai_vung_dung_word"] = phep_do(None, c["so_vung_can_ocr"])
    td = r.get("tu_dien", {})
    if (type(td) is dict and bam(td.get("bam")) and so(td.get("so_tu_kiem"), nguyen=True)
            and so(td.get("so_tu_co_can_cu"), nguyen=True) and td["so_tu_co_can_cu"] <= td["so_tu_kiem"]):
        out["tu_dien"] = {**phep_do(td["so_tu_co_can_cu"], td["so_tu_kiem"]), "bam": td["bam"]}
    else:
        out["tu_dien"] = phep_do()
    vung = r.get("vung_sua_tay")
    if r.get("detector_day_du") is True and type(vung) is list and iou is not None:
        if len(vung) > 10000 or any(not vung_dung(v) or v["trang"] > c["so_trang"] for v in vung):
            raise loi()
        pairs = []
        for i, g in enumerate(c["vung_sua_tay"]):
            for j, p in enumerate(vung):
                if g["trang"] != p["trang"]:
                    continue
                a, b = g["hop"], p["hop"]
                giao = max(0, min(a[2], b[2])-max(a[0], b[0])) * max(0, min(a[3], b[3])-max(a[1], b[1]))
                union = (a[2]-a[0])*(a[3]-a[1]) + (b[2]-b[0])*(b[3]-b[1]) - giao
                if giao / union >= iou:
                    pairs.append((giao / union, i, j))
        gs, ps = set(), set()
        for _, i, j in sorted(pairs, reverse=True):
            if i not in gs and j not in ps:
                gs.add(i)
                ps.add(j)
        out["detector_recall"] = phep_do(len(gs), len(c["vung_sua_tay"]))
        out["detector_precision"] = phep_do(len(ps), len(vung))
        out["iou_ghep_do"] = iou
    else:
        out["detector_recall"] = phep_do(None, len(c["vung_sua_tay"]))
        out["detector_precision"] = phep_do()
    # Vùng sửa tay cũng thuộc điểm Nghiêm trọng đã cài, không chỉ chấm chữ.
    out["nghiem_trong_chu"] = out["nghiem_trong"]
    so_vung = len(c["vung_sua_tay"])
    bat_vung = out["detector_recall"]["tu_so"] if so_vung else 0
    bat_chu = out["nghiem_trong_chu"]["tu_so"]
    out["nghiem_trong"] = phep_do(bat_chu + bat_vung if so(bat_chu) and so(bat_vung) else None, n + so_vung)
    out["sua_that_chu_bi_an"] = out["sua_that_bi_an"]
    an_chu = out["sua_that_chu_bi_an"]["tu_so"]
    # Mất vùng: chưa biết bị ẩn hay bỏ sót, không biến thành 0 sửa thật bị ẩn.
    out["sua_that_bi_an"] = phep_do(an_chu if so(an_chu) and bat_vung == so_vung else None, m + so_vung)
    sot_chu = out["sua_that_bo_sot"]["tu_so"]
    out["sua_that_bo_sot"] = phep_do(sot_chu + so_vung - bat_vung if so(sot_chu) and so(bat_vung) else None, m + so_vung)
    for k in ("giay_xu_ly_core", "ram_dinh_bytes"):
        v = r.get(k)
        co_so_do = so(v, nguyen=k == "ram_dinh_bytes") and v > 0
        out[k] = {"gia_tri": v if co_so_do else None, "ly_do": None if co_so_do else LY_DO_THIEU}
    giay = out["giay_xu_ly_core"]["gia_tri"]
    out["trang_moi_giay"] = phep_do(c["so_trang"], giay)
    out["diem_moi_giay"] = phep_do(len(ds) if day_du else None, giay)
    out["ocr_kem"] = phep_do()  # Chưa có ngưỡng duyệt; vẫn thu số từ lệch dấu theo trang.
    trang = r.get("lech_dau_trang")
    out["lech_dau_trang"] = []
    for i in range(c["so_trang"]):
        p = trang[i] if type(trang) is list and len(trang) == c["so_trang"] else {}
        if (type(p) is dict and so(p.get("so_tu"), nguyen=True) and so(p.get("so_tu_lech"), nguyen=True)
                and p["so_tu_lech"] <= p["so_tu"]):
            out["lech_dau_trang"].append(phep_do(p["so_tu_lech"], p["so_tu"]))
        else:
            out["lech_dau_trang"].append(phep_do())
    return out


class CongHandle:
    """JSONL UTF-8 qua hai CRT fd kế thừa từ host Core tin cậy, không mở socket.

    Không có khóa: host đã xác thực và gắn quyền. Không nhận fd 0/1/2 hoặc tệp
    thường, không đọc lại sau timeout, không retry. Host chịu vòng đời handle.
    """
    def __init__(self, vao, ra, han):
        import stat
        if vao == ra or any(x is None or x < 3 for x in (vao, ra)):
            raise loi("DC_CHUA_CO_MOI_TRUONG_THU")
        try:
            if any(not stat.S_ISFIFO(os.fstat(x).st_mode) for x in (vao, ra)):
                raise ValueError()
        except (OSError, ValueError):
            raise loi("DC_CHUA_CO_MOI_TRUONG_THU") from None
        self.vao, self.ra, self.han = vao, ra, han
        self.hong = False

    def trao_doi(self, req):
        if self.hong:
            raise OSError()
        q = queue.Queue(maxsize=1)
        def lam():
            try:
                # fd chỉ duplicate trong worker, tự đóng trong finally của with.
                with os.fdopen(os.dup(self.ra), "wb", buffering=0) as gui, os.fdopen(os.dup(self.vao), "rb") as nhan:
                    raw = json.dumps(req, ensure_ascii=True, allow_nan=False).encode() + b"\n"
                    con = memoryview(raw)
                    while con:
                        n = gui.write(con)
                        if not n:
                            raise OSError()
                        con = con[n:]
                    dong = nhan.readline(TRAN_BYTE + 1)
                    if not dong.endswith(b"\n"):
                        raise ValueError()
                    q.put((True, doc_json(dong)))
            except Exception:
                q.put((False, None))
        threading.Thread(target=lam, daemon=True).start()
        try:
            ok, r = q.get(timeout=self.han)
        except queue.Empty:
            self.hong = True
            raise TimeoutError() from None
        if not ok:
            self.hong = True
            raise OSError()
        return r


def trao(cong, thao_tac, mtq, noi_dung, *, co_the_da_nhan=False):
    try:
        r = cong.trao_doi({"phien_ban": 1, "thao_tac": thao_tac, "ma_tuong_quan": mtq, **noi_dung})
        if type(r) is not dict or r.get("ma_tuong_quan") != mtq:
            raise ValueError()
    except (KeyboardInterrupt, OSError, ValueError, TypeError, LoiNghiepVu):
        if co_the_da_nhan:
            raise ChuaRo(mtq) from None
        raise loi("DC_CHUA_CO_MOI_TRUONG_THU") from None
    if r.get("trang_thai") == "CHUA_RO":
        raise ChuaRo(mtq)
    if r.get("trang_thai") == "HUY":
        raise loi("DC_HUY")
    if r.get("trang_thai") == "LOI":
        if thao_tac == "kiem_moi_truong" or r.get("ma_loi") == "DC_CHUA_CO_MOI_TRUONG_THU":
            raise loi("DC_CHUA_CO_MOI_TRUONG_THU")
        raise loi("DC_LOI_NGUON_THU")
    return r


def thuc_hien(args, *, cong=None, kiem_huy=lambda: None):
    # Chạy khô trở về trước mọi đọc tệp/mở handle/ghi báo cáo.
    if not args.that:
        return khung_bao_cao()
    can = (args.bo_demo, args.ma_phien, args.module, args.quy_trinh, args.cau_hinh_core)
    if not all(can) or not ma_demo(args.ma_phien) or any(not ma_core(x) for x in can[2:]):
        raise loi("DC_CHUA_CO_MOI_TRUONG_THU")
    bo = kiem_bo(doc_json(duong_workspace(args.bo_demo).read_bytes()))
    mtq = ma_tuong_quan(args.ma_phien)
    if len(mtq) > 65:
        raise loi("DC_THAM_SO_KHONG_HOP_LE")
    dich = duong_workspace(args.bao_cao, ghi=True) if args.bao_cao else None
    if cong is None:
        cong = CongHandle(args.core_vao_fd, args.core_ra_fd, args.han_giay)
    bc = khung_bao_cao()
    bc["che_do"] = "DO_QUA_CORE"
    bc["phep_do_that"] = "Theo nguồn host Core cấp; trình duyệt vẫn chờ Anh kiểm."
    cau_hinh = {"module": args.module, "quy_trinh": args.quy_trinh, "cau_hinh_core": args.cau_hinh_core,
                "chi_local": True, "nhan": "DEMO"}
    kiem_huy()
    moi = trao(cong, "kiem_moi_truong", mtq, {**cau_hinh,
        "nguon_demo": [{"word": c["word"], "scan": c["scan"]} for c in bo["ca"]]})
    if (any(moi.get(k) is not True for k in ("core_that", "ocr_that", "local_that", "chi_local", "bo_demo_da_xac_minh"))
            or not bam(moi.get("bam_cau_hinh"))):
        raise loi("DC_CHUA_CO_MOI_TRUONG_THU")
    bc["bam_cau_hinh"] = moi["bam_cau_hinh"]
    for i, c in enumerate(bo["ca"]):
        kiem_huy()
        m = f"{mtq}-{i+1}"
        bat_dau = time.perf_counter()
        # Không truyền đáp án, số điểm hoặc ngưỡng ghép cho bộ xử lý.
        request = {**cau_hinh, "word": c["word"], "scan": c["scan"], "bam_cau_hinh": moi["bam_cau_hinh"]}
        r = trao(cong, "gui_viec", m, request, co_the_da_nhan=True)
        if r.get("trang_thai") == "DA_NHAN":
            # Một lần đọc trạng thái; chưa xong trả ChuaRo, không polling/gửi lại.
            r = trao(cong, "doc_viec", m, {}, co_the_da_nhan=True)
        if r.get("trang_thai") != "XONG":
            raise ChuaRo(m)
        if (r.get("cloud") != 0 or type(r.get("cloud")) is not int
                or type(r.get("so_trang")) is not int or r["so_trang"] != c["so_trang"]
                or r.get("bam_cau_hinh") != moi["bam_cau_hinh"]
                or r.get("bam_word") != c["word"]["bam"] or r.get("bam_scan") != c["scan"]["bam"]):
            raise loi()
        kiem_huy()
        row = cham_ca(c, r, args.iou_ghep)
        row["giay_cho_cong_cu"] = time.perf_counter() - bat_dau
        row["cloud"] = 0
        bc["ca"].append(row)
    for k in ("nghiem_trong", "sua_that_bi_an", "sua_that_bo_sot"):
        ps = [r[k] for r in bc["ca"]]
        # Mẫu số 0 ở một ca không mất số đo các ca có mẫu; null tử số không được bỏ qua.
        bc[k] = phep_do(sum(p["tu_so"] for p in ps) if all(so(p["tu_so"]) for p in ps) else None,
                       sum(p["mau_so"] for p in ps))
    bc["cong_chat_luong"] = trang_thai_cong(bc["nghiem_trong"], bc["sua_that_bi_an"])
    for row in bc["ca"]:
        for k in ("nghiem_trong_chu", "detector_recall"):
            p = row[k]
            if p["gia_tri"] is not None and p["tu_so"] != p["mau_so"]:
                bc["cong_chat_luong"] = "KHONG_DAT"
        if so(row["sua_that_chu_bi_an"]["tu_so"]) and row["sua_that_chu_bi_an"]["tu_so"] > 0:
            bc["cong_chat_luong"] = "KHONG_DAT"
    if bc["sua_that_bo_sot"]["gia_tri"] is None:
        bc["cong_chat_luong"] = "CHUA_DO" if bc["cong_chat_luong"] != "KHONG_DAT" else "KHONG_DAT"
    elif bc["sua_that_bo_sot"]["tu_so"]:
        bc["cong_chat_luong"] = "KHONG_DAT"
    can_do = ("toa_do_tu_abbyy", "co_nghi_ngo_abbyy", "ocr_lai_vung_dung_word", "tu_dien",
              "detector_recall", "detector_precision", "lech_gia_moi_trang", "giay_xu_ly_core", "ram_dinh_bytes",
              "trang_moi_giay", "diem_moi_giay")
    du_do = (all(row[k]["gia_tri"] is not None for row in bc["ca"] for k in can_do)
             and all(p["gia_tri"] is not None for row in bc["ca"] for p in row["lech_dau_trang"]))
    bc["ket_luan_do"] = ("KHONG_DAT" if bc["cong_chat_luong"] == "KHONG_DAT" else
                          "CHO_ANH_DUYET_NGUONG" if du_do and bc["cong_chat_luong"] == "DAT_TREN_BO_DEMO" else "CHUA_DO")
    bc.pop("so_do_chay_kho")
    # Đủ hai cổng không tự chứng nhận môi trường hay bật engine/module.
    r = trao(cong, "luu_bao_cao", mtq, {"bao_cao": bc}, co_the_da_nhan=True)
    if r.get("da_luu") is not True:
        raise ChuaRo(mtq)
    if dich:
        p = duong_workspace(args.bao_cao, ghi=True)
        raw = json.dumps(bc, ensure_ascii=False, allow_nan=False, indent=2).encode("utf-8")
        # Không ghi đè; dữ liệu chỉ là allowlist số đo, băm và câu cố định.
        with p.open("xb") as f:
            f.write(raw)
    return bc


class BoDocThamSo(argparse.ArgumentParser):
    def error(self, message):
        raise loi("DC_THAM_SO_KHONG_HOP_LE")


def tao_parser():
    p = BoDocThamSo(description="Đo đối chiếu DEMO qua Core; mặc định CHẠY KHÔ.", allow_abbrev=False)
    p.add_argument("--that", action="store_true", help="Chỉ Anh tự chạy khi đã cấp đủ môi trường.")
    for k in ("bo-demo", "ma-phien", "module", "quy-trinh", "cau-hinh-core", "bao-cao"):
        p.add_argument("--" + k)
    p.add_argument("--core-vao-fd", type=int)
    p.add_argument("--core-ra-fd", type=int)
    p.add_argument("--han-giay", type=float, default=30)
    p.add_argument("--iou-ghep", type=float, help="Ngưỡng ghép đáp án vùng do Anh chọn, không là ngưỡng detector.")
    return p


def main(argv=None):
    try:
        a = tao_parser().parse_args(argv)
        if not so(a.han_giay, toi_thieu=0.01) or a.han_giay > 60 or (a.iou_ghep is not None and
                (not so(a.iou_ghep, toi_thieu=0.000001) or a.iou_ghep > 1)):
            raise loi("DC_THAM_SO_KHONG_HOP_LE")
        bc = thuc_hien(a)
        print(json.dumps(bc, ensure_ascii=False, allow_nan=False, indent=2))
        return 0 if bc["che_do"] == "CHAY_KHO" or bc["ket_luan_do"] == "CHO_ANH_DUYET_NGUONG" else 2
    except ChuaRo as e:
        print("CHUA_RO: " + ma_tuong_quan(e.ma_tuong_quan) + "; tra cứu tại Core, không tự gửi lại.", file=sys.stderr)
        return 3
    except LoiNghiepVu as e:
        print(e.ma + ": " + e.thong_diep, file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("DC_HUY: Đã dừng; kiểm tra việc tại Core trước khi chạy tiếp.", file=sys.stderr)
        return 130
    except Exception:
        print("DC_LOI_CONG_CU: Không hoàn tất công cụ thử; kiểm tra việc tại Core.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
