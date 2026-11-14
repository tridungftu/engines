"""Thử Local bằng ca DEMO của gói; mặc định không truy cập mạng."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_hoi_ai"))
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from e_hoi_ai import ai_cuc_bo, chon_model
from e_hoi_ai.cong_ai import CongAI, NhaCungCapLocal
from e_hoi_ai.dto import YeuCauAI

VAN_BAN = "DEMO — Hợp đồng DEMO-001 của Công ty DEMO Ánh Dương. Số tiền thanh toán là 1.000.000 VND. Ngày thanh toán là 30/10/2026."
YEU_CAU = YeuCauAI(VAN_BAN, "DEMO: Số tiền và ngày thanh toán là bao nhiêu?", "demo.hoi", "1")
DAP_AN = {"1.000.000 VND", "30/10/2026"}


class DemCloud:
    def __init__(self):
        self.so_luot = 0

    def hoi(self, *args, **kwargs):
        self.so_luot += 1
        raise RuntimeError("Công cụ chỉ cho phép Local.")


class LocalTat:
    def hoi(self, *args, **kwargs):
        raise ai_cuc_bo.LocalAIKhongSanSang("Local tắt giả lập.")


def thu_tat(cloud):
    try:
        CongAI(nha_cung_cap={"local": LocalTat(), "cloud": cloud}).goi(
            YEU_CAU, {"local_ai": {}}, model="demo", ly_do_chon="demo", kiem_huy=lambda: None)
    except LoiNghiepVu as exc:
        return {"khong_san_sang": exc.ma == "LOCAL_AI_KHONG_SAN_SANG", "ma_loi": exc.ma}
    return {"khong_san_sang": False, "ma_loi": "KHONG_BAO_LOI"}


def thuc_hien(url):
    ai_cuc_bo.kiem_url(url)
    cau_hinh = {"local_ai": {"url": url, "timeout_giay": 120}}
    cloud = DemCloud()
    cong = CongAI(nha_cung_cap={"local": NhaCungCapLocal(), "cloud": cloud})
    catalog = chon_model.BoPhatHienModel().phat_hien(cau_hinh["local_ai"], lam_moi=True)
    rows = []
    if catalog:
        for model in catalog.models:
            row = {"model": model.ma, "dung": False, "co_trich_dan": False, "thoi_gian_ms": 0, "trang_thai": "khong_san_sang"}
            if model.kha_dung:
                start = time.perf_counter()
                try:
                    ket_qua = cong.goi(YEU_CAU, cau_hinh, model=model.ma,
                                       ly_do_chon="thu_demo", kiem_huy=lambda: None)
                    row["co_trich_dan"] = bool(ket_qua.trich_dan) and ket_qua.co_can_cu
                    row["dung"] = ket_qua.co_can_cu and set(ket_qua.tra_loi.splitlines()) == DAP_AN
                    row["trang_thai"] = "da_tra_loi"
                except LoiNghiepVu as exc:
                    row["trang_thai"] = exc.ma
                finally:
                    row["thoi_gian_ms"] = round((time.perf_counter() - start) * 1000)
            rows.append(row)
    return {"che_do": "that", "ca_demo": "manifest hiện có; AI-4 chưa có trên nhánh này",
            "phat_hien": "thanh_cong" if catalog is not None else "khong_san_sang",
            "ket_qua": rows, "local_tat_gia_lap": thu_tat(cloud), "so_luot_cloud": cloud.so_luot}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Thử Local bằng dữ liệu DEMO; mặc định chạy khô.")
    parser.add_argument("--that", action="store_true", help="Cho phép kết nối Local thật khi có --url.")
    parser.add_argument("--url", help="Địa chỉ HTTP Local AI, gồm cổng.")
    args = parser.parse_args(argv)
    if args.that and not args.url:
        parser.error("--that cần --url.")
    if not args.that:
        print("CHẠY KHÔ: không dò model, không gọi mạng. Dùng --that và --url để chạy thật.")
        return 0
    try:
        report = thuc_hien(args.url)
        ten = "ket-qua-local-demo-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f") + ".json"
        with Path(ten).open("x", encoding="utf-8") as tep:
            json.dump(report, tep, ensure_ascii=False, indent=2)
            tep.write("\n")
        print("Model | Đúng đáp án | Có trích dẫn | Thời gian (ms) | Trạng thái")
        for row in report["ket_qua"]:
            print(f"{row['model']} | {row['dung']} | {row['co_trich_dan']} | {row['thoi_gian_ms']} | {row['trang_thai']}")
        print("Local tắt giả lập:", "không sẵn sàng" if report["local_tat_gia_lap"]["khong_san_sang"] else "chưa đạt")
        print("Cloud:", report["so_luot_cloud"], "— Báo cáo:", ten)
        return 0 if (report["ket_qua"] and all(r["dung"] and r["co_trich_dan"] for r in report["ket_qua"])
                     and report["local_tat_gia_lap"]["khong_san_sang"] and report["so_luot_cloud"] == 0) else 1
    except (OSError, ValueError):
        print("Không thể thử Local hoặc ghi báo cáo DEMO; kiểm tra địa chỉ và thư mục chạy.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
