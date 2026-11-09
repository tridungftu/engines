"""Chuẩn bị lát 8: lead thử Local qua cổng chung, chỉ dùng tài liệu DEMO.

Không tự tìm hồ sơ chạy, không đọc cấu hình thật/két/env. Core hoặc lead
xuất riêng phần settings của engine thành JSON DEMO rồi truyền --cau-hinh.
Nhận {"local_ai": {...}} hoặc {"settings": {"local_ai": {...}}}; các khóa
Local là enabled, url, model, timeout_seconds như engine Hỏi AI. Không dùng
cấu hình Cloud. Discovery chỉ chọn ba họ model CD-106, không tự tải model.
Đây là thử cổng Local, không thay bài nghiệm thu Core/SDK/giao diện của lead.

Chạy khô: --cau-hinh Local-DEMO.json (không có truy cập mạng).
Lead chạy thật: --thuc-hien --cau-hinh Local-DEMO.json --ra Ket-qua-DEMO.json
Thêm --dia-chi-sai để thử mất kết nối; có thể truyền địa chỉ Local thử riêng.
Exit: 0 = đạt; 1 = có ca chưa đạt; 2 = lỗi cấu hình/tham số/ghi tệp.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
import time


# Đường dẫn Unicode được lấy trong Python; chạy được từ thư mục bất kỳ.
GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOC / "src"))
from kho_tri_thuc.engines.e_hoi_ai.lib import ai_cuc_bo as ai  # noqa: E402
from kho_tri_thuc.engines.e_hoi_ai.lib import cong_ai as ca  # noqa: E402


MODELS = ("gpt-oss-20b", "Qwen3 8B", "Gemma")
VAN_BAN_DEMO = (
    "TÀI LIỆU GIẢ DEMO. Số hợp đồng: DEMO-001. "
    "Số tiền: 1.000.000 VND. Ngày thanh toán: 30/10/2026."
)
GIA_TRI_DEMO = {"so_hop_dong": "DEMO-001", "so_tien": "1.000.000 VND",
                "ngay_thanh_toan": "30/10/2026"}
NHAN_TRUONG = ("Số hợp đồng", "Số tiền", "Ngày thanh toán")
DIA_CHI_SAI = "http://127.0.0.1:1/v1/chat/completions"
LOI_DISCOVERY = frozenset((
    "LOCAL_AI_CAU_HINH_KHONG_HOP_LE", "LOCAL_AI_DIA_CHI_KHONG_HOP_LE",
    "LOCAL_AI_MODEL_KHONG_CUC_BO", "LOCAL_AI_HET_THOI_GIAN",
    "LOCAL_AI_CHUYEN_HUONG_BI_CHAN", "LOCAL_AI_HTTP_LOI",
    "LOCAL_AI_KET_NOI_LOI", "LOCAL_AI_PHAN_HOI_KHONG_HOP_LE",
    "LOCAL_AI_DUONG_MANG_KHONG_HOP_LE", "LOCAL_AI_QUA_NHIEU_MODEL",
    "LOCAL_AI_ID_MODEL_KHONG_HOP_LE"))


class LoiChuanBi(ValueError):
    """Chỉ chứa câu cố định, không chứa giá trị cấu hình/ngoại lệ gốc."""


class _ChiLocal:
    """Seam khóa Cloud/Mask: không đọc khóa, không dùng môi trường hệ điều hành."""

    def co_khoa(self):
        return False

    def cam(self, *args, **kwargs):
        raise RuntimeError("Thử nghiệm chỉ cho phép Local AI.")

    tra_loi = che = mo_che = ket_thuc = cam


def _tep_demo(ten: str) -> Path:
    path = Path(ten).resolve()
    parts = {p.casefold() for p in path.parts}
    if (parts & {"plhn-that", "web-that", "bi-mat", "du-lieu-ke-toan", ".git"}
            or any(p.startswith(".env") for p in parts)
            or path.name.casefold() == "cau_hinh.that.toml"
            or path.suffix.casefold() != ".json"):
        raise LoiChuanBi("Chỉ sử dụng tệp JSON cấu hình hoặc kết quả DEMO riêng.")
    return path


def doc_cau_hinh(ten: str | None) -> dict:
    if not ten:
        raise LoiChuanBi("Cần chỉ định tệp JSON cấu hình Local DEMO bằng --cau-hinh.")
    path = _tep_demo(ten)
    try:
        with path.open("r", encoding="utf-8-sig") as stream:
            text = stream.read(65537)
        if len(text) > 65536:
            raise ValueError
        raw = json.loads(text)
        settings = raw.get("settings", raw) if isinstance(raw, dict) else None
        local = settings.get("local_ai") if isinstance(settings, dict) else None
        if (not isinstance(local, dict) or local.get("enabled") is not True
                or not isinstance(local.get("url"), str)):
            raise ValueError
        cfg = ai.local_ai_settings({"local_ai": local})
        if (cfg["error"] or not cfg["enabled"] or not isinstance(cfg["model"], str)
                or (cfg["model"] and not ai._MODEL_ID.fullmatch(cfg["model"]))):
            raise ValueError
        # Chỉ giữ nhóm Local đã chuẩn hóa, không nhận đường dẫn khóa/Cloud.
        return {key: cfg[key] for key in ai.DEFAULTS}
    except (OSError, ValueError, TypeError, OverflowError, RecursionError):
        raise LoiChuanBi("Cấu hình Local DEMO chưa hợp lệ hoặc chưa bật; cần kiểm tra lại.") from None


def _discovery(cfg: dict) -> tuple[list[dict], str]:
    result = ai.discover_local_models({"local_ai": cfg})
    if (not isinstance(result, dict) or not isinstance(result.get("model_phat_hien"), list)
            or result.get("ma_loi") != ""):
        code = result.get("ma_loi") if isinstance(result, dict) else None
        return [], code if code in LOI_DISCOVERY else "LOCAL_AI_PHAN_HOI_KHONG_HOP_LE"
    return result["model_phat_hien"], ""


def _chon_model(models: list[dict], nhan: str, uu_tien: str) -> tuple[dict | None, str]:
    prefix = {"gpt-oss-20b": "gpt-oss-20b", "Qwen3 8B": "qwen3-8b", "Gemma": "gemma"}[nhan]
    found = {}
    for item in models:
        if not isinstance(item, dict):
            continue
        model = item.get("id_model")
        if not isinstance(model, str) or not ai._MODEL_ID.fullmatch(model):
            continue
        short = model.casefold().rsplit("/", 1)[-1].replace(":", "-").replace("_", "-")
        # Không nhận nhầm 80B/200B; Gemma là họ model chưa kê khai kích thước.
        if short.startswith(prefix) and (prefix == "gemma" or short == prefix
                                        or short[len(prefix):len(prefix) + 1] in ("-", ".")):
            found[model] = item
    if uu_tien in found:
        return found[uu_tien], ""
    if len(found) == 1:
        return next(iter(found.values())), ""
    return None, "LOCAL_NHIEU_MODEL_PHU_HOP" if found else "LOCAL_KHONG_CO_MODEL"


def _truong_dung(truong: dict) -> dict:
    return {ten: item for ten, item in truong.items()
            if ten in GIA_TRI_DEMO and item.gia_tri == GIA_TRI_DEMO[ten]
            and item.nguon == ca.DUONG_LOCAL and item.trich_dan
            and item.trich_dan in VAN_BAN_DEMO and item.gia_tri in item.trich_dan}


def _hoi(cfg: dict) -> tuple[bool, str, str, int]:
    ghi = ca.BoGhiBoNho()
    chan = _ChiLocal()
    cong = ca.CongAI({"local_ai": dict(cfg), "cong_ai": {"cloud_bat": False}},
        bo_ghi=ghi, moi_truong={}, nha_cung_cap=chan, mask=chan,
        kiem_xac_suat=lambda _: False)
    # Cùng cờ khóa bản 1 trong runtime/adapter, kể cả cấu hình đầu vào bật Cloud.
    cong.cai_dat["cloud_bat"] = False
    yc = ca.YeuCauAI("BOC_TACH_HOP_DONG", VAN_BAN_DEMO,
        "Trích đúng ba trường DEMO: số hợp đồng, số tiền, ngày thanh toán; có trích dẫn nguyên văn.",
        tuple(GIA_TRI_DEMO))
    kq = cong.goi(yc, kiem_tra=lambda fields, _: set(fields) - set(_truong_dung(fields)))
    cloud = sum(b.da_gui for b in ghi.ban_ghi if b.duong == ca.DUONG_CLOUD)
    dung = _truong_dung(kq.truong)
    dat = (kq.duong == ca.DUONG_LOCAL and kq.muc == ca.MUC_VANG
           and set(dung) == set(GIA_TRI_DEMO) and not kq.truong_bi_loai
           and not any(ma in kq.ly_do for ma in ("DUOI_NGUONG", "THIEU_TRUONG")) and cloud == 0)
    # Chỉ xuất các trường DEMO đã kiểm, bỏ toàn bộ phần văn bản tự do.
    # Đây là phép chọn dữ liệu kết quả, không tạo bộ che hay đường Mask riêng.
    preview = "; ".join(f"{nhan}: {dung[ten].gia_tri}" for nhan, ten in
                        zip(NHAN_TRUONG, GIA_TRI_DEMO) if ten in dung)[:200]
    loi = next((ma for ma in ("LOCAL_KHONG_CHAY", "LOCAL_LOI", "LOCAL_TAT")
                if ma in kq.ly_do), "LOCAL_KET_QUA_KHONG_DAT") if not dat else ""
    return dat, loi, preview, cloud


def thuc_hien(cfg: dict, dia_chi_sai: str | None = None) -> dict:
    start = time.perf_counter()
    models, loi = _discovery(cfg)
    do_ms = int((time.perf_counter() - start) * 1000)
    report = {"ngay_thu": datetime.now().strftime("%d/%m/%Y"), "chi_local": True,
              "so_luot_cloud": 0, "discovery_ms": do_ms, "ket_qua": []}
    for nhan in MODELS:
        row = {"model": nhan, "con": False, "san_sang": False,
               "thoi_gian_ms": 0, "dat": False, "ma_loi_local": loi, "trich_doan": ""}
        item, ma = _chon_model(models, nhan, cfg["model"]) if not loi else (None, loi)
        row["con"] = item is not None or ma == "LOCAL_NHIEU_MODEL_PHU_HOP"
        row["ma_loi_local"] = ma
        if item is not None:
            state, software = item.get("trang_thai"), item.get("loai_phan_mem")
            row["trang_thai_phat_hien"] = state if state in ("san_sang", "da_tai", "chua_ro") else "chua_ro"
            if state == "da_tai" and software == "lm_studio":
                row["ma_loi_local"] = "LOCAL_MODEL_CHUA_SAN_SANG"
            else:
                # Ollama da_tai/OpenAI chua_ro chưa chứng minh nằm trong RAM;
                # một câu hỏi thật sẽ kiểm readiness, không báo sẵn sàng trước.
                t0 = time.perf_counter()
                row["dat"], row["ma_loi_local"], row["trich_doan"], cloud = _hoi(
                    {**cfg, "model": item["id_model"]})
                row["thoi_gian_ms"] = int((time.perf_counter() - t0) * 1000)
                row["san_sang"] = row["ma_loi_local"] not in ("LOCAL_KHONG_CHAY", "LOCAL_LOI", "LOCAL_TAT")
                report["so_luot_cloud"] += cloud
        report["ket_qua"].append(row)
    if dia_chi_sai:
        # Luôn đi qua CongAI cả khi discovery lỗi để kiểm không có fallback.
        bad = {**cfg, "url": dia_chi_sai, "model": "gpt-oss-20b", "timeout_seconds": 1}
        t0 = time.perf_counter()
        _, ma_do = _discovery(bad)
        _, ma_goi, _, cloud = _hoi(bad)
        report["so_luot_cloud"] += cloud
        report["mat_ket_noi"] = {"model": "gpt-oss-20b", "san_sang": ma_goi not in
            ("LOCAL_KHONG_CHAY", "LOCAL_LOI", "LOCAL_TAT"),
            "thoi_gian_ms": int((time.perf_counter() - t0) * 1000),
            "dat": ma_do in ("LOCAL_AI_KET_NOI_LOI", "LOCAL_AI_HET_THOI_GIAN")
                   and ma_goi == "LOCAL_KHONG_CHAY" and cloud == 0,
            "ma_loi_local": ma_goi, "ma_loi_discovery": ma_do, "trich_doan": ""}
    return report


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        # argparse mặc định phản chiếu tham số sai, có thể chứa địa chỉ/khóa.
        raise LoiChuanBi("Tham số chưa hợp lệ; dùng --help để xem cách chạy.")


def main(argv=None) -> int:
    parser = _Parser(description="Thử Local AI bằng tài liệu giả DEMO; mặc định chỉ kiểm cấu hình.",
        epilog="Cấu hình JSON: local_ai gồm enabled, url, model, timeout_seconds, giống settings của engine.")
    parser.add_argument("--cau-hinh", metavar="JSON_DEMO", help="Bản cấu hình Local DEMO do Core/lead cấp.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--chay-kho", action="store_true", help="Chỉ kiểm cấu hình và in kế hoạch (mặc định).")
    mode.add_argument("--thuc-hien", action="store_true", help="Lead gọi Local thật; cần --ra.")
    parser.add_argument("--ra", metavar="JSON_KET_QUA", help="Tệp kết quả DEMO mới; không ghi đè tệp có sẵn.")
    parser.add_argument("--dia-chi-sai", nargs="?", const=DIA_CHI_SAI, metavar="DIA_CHI_LOCAL",
                        help="Thêm ca mất kết nối; mặc định dùng cổng đóng trên máy này.")
    try:
        args = parser.parse_args(argv)
        cfg = doc_cau_hinh(args.cau_hinh)
        if args.dia_chi_sai:
            bad = ai.local_ai_settings({"local_ai": {**cfg, "url": args.dia_chi_sai}})
            if bad["error"] or bad["url"] == cfg["url"]:
                raise LoiChuanBi("Ca mất kết nối cần địa chỉ Local hợp lệ khác địa chỉ đang dùng.")
            args.dia_chi_sai = bad["url"]
        out = _tep_demo(args.ra) if args.ra else None
        if out and (out.exists() or not out.parent.is_dir()):
            raise LoiChuanBi("Cần chọn tệp kết quả mới trong thư mục có sẵn.")
        if not args.thuc_hien:
            print("Cấu hình Local DEMO hợp lệ. Chạy khô: chưa dò máy và chưa gửi câu hỏi.")
            print("Kế hoạch: dò model; thử gpt-oss-20b, Qwen3 8B, Gemma qua cổng AI chung.")
            print("Tài liệu giả DEMO; trích số hợp đồng, số tiền, ngày thanh toán; đo thời gian.")
            if args.dia_chi_sai:
                print("Có thêm ca mất kết nối: yêu cầu báo lỗi Local và cho thử lại.")
            print("Cloud bị khóa; 0 lượt Cloud. Chỉ chạy thật khi có --thuc-hien và --ra.")
            return 0
        if out is None:
            raise LoiChuanBi("Chạy thật cần --ra để lưu kết quả DEMO.")
        report = thuc_hien(cfg, args.dia_chi_sai)
        with out.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
        for row in report["ket_qua"]:
            print(f"{row['model']}: {'đạt' if row['dat'] else 'chưa đạt; cần kiểm tra Local và thử lại'}.")
        if "mat_ket_noi" in report:
            print("Ca mất kết nối: " + ("đạt; đã nhận lỗi Local." if report["mat_ket_noi"]["dat"]
                                         else "chưa đạt; cần kiểm tra Local và thử lại."))
        print("Đã lưu báo cáo DEMO. Số lượt Cloud: " + str(report["so_luot_cloud"]) + ".")
        dat = all(row["dat"] for row in report["ket_qua"])
        return 0 if dat and report.get("mat_ket_noi", {"dat": True})["dat"] and not report["so_luot_cloud"] else 1
    except LoiChuanBi as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception:
        print("Chưa hoàn tất thử Local hoặc ghi báo cáo DEMO; kiểm tra cấu hình và thử lại.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
