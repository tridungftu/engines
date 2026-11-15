"""Thử Local bằng ca DEMO của gói; mặc định không truy cập mạng."""
import argparse
from copy import deepcopy
from unittest.mock import patch
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
from e_hoi_ai.chay import app, bo_hoi
from kho_tri_thuc_sdk.thu import CoreGia

def doc_demo():
    phieu = json.loads((Path(__file__).resolve().parents[1] / "goi" / "e_hoi_ai" / "engine.json").read_text(encoding="utf-8"))
    return phieu["chay_thu_demo"]


def kiem_demo(vd, kq):
    if kq["trang_thai"] != "XONG":
        return False, False
    if vd["nang_luc"] == "ai.hoi_tai_lieu@1":
        truong = kq["ket_qua"]["truong"]
        if vd["tham_so"]["ma_prompt"] == "demo.hoi_nguoi_bao_lanh":
            return (not truong["co_can_cu"] and truong["tra_loi"].lower() == "kh\u00f4ng th\u1ea5y c\u0103n c\u1ee9"
                    and not truong["trich_dan"]), bool(truong["trich_dan"])
        return (truong["co_can_cu"] and set(truong["tra_loi"].splitlines()) == {"1.000.000 VND", "30/10/2026"}), bool(truong["trich_dan"])
    ra = kq["ket_qua"]["tra_loi_ai"]
    dung = (ra["du_lieu"] == {"so_tien": {"so": 1000000, "tien_te": "VND"}, "ngay": "2026-10-30"}
            and ra["kiem_trich_dan"]["dat"] and ra["chuyen_tiep"] == vd["dau_vao"]["yeu_cau_ai"]["chuyen_tiep"])
    return dung, bool(ra["trich_dan"])


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
            YeuCauAI("DEMO", "DEMO", "demo.hoi", "1"), {"local_ai": {}}, model="demo", ly_do_chon="demo", kiem_huy=lambda: None)
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
    demos = doc_demo()
    if not demos:
        raise ValueError("Bo DEMO rong.")
    cong_cu = bo_hoi.cong_ai
    try:
        bo_hoi.cong_ai = cong
        with patch("e_hoi_ai.hoi.yeu_cau_cau_hinh", return_value=cau_hinh), patch("e_hoi_ai.hoi_yeu_cau.yeu_cau_cau_hinh", return_value=cau_hinh):
            for model in catalog.models if catalog else []:
                for vd_goc in demos:
                    vd = deepcopy(vd_goc)
                    row = {"model": model.ma, "ca_demo": vd["ten"], "dung": False, "co_trich_dan": False, "thoi_gian_ms": 0, "trang_thai": "khong_san_sang"}
                    if model.kha_dung:
                        if vd["nang_luc"] == "ai.hoi_tai_lieu@1":
                            vd["tham_so"]["model_uu_tien"] = model.ma
                        else:
                            vd["dau_vao"]["yeu_cau_ai"]["model_uu_tien"] = model.ma
                        start = time.perf_counter()
                        kq = CoreGia().chay_thu(app, vd["nang_luc"], vd["dau_vao"], vd.get("tham_so"))
                        row["thoi_gian_ms"] = round((time.perf_counter() - start) * 1000)
                        row["trang_thai"] = kq["trang_thai"]
                        row["dung"], row["co_trich_dan"] = kiem_demo(vd, kq)
                    rows.append(row)
    finally:
        bo_hoi.cong_ai = cong_cu
    return {"che_do": "that", "ca_demo": "chay_thu_demo trong engine.json",
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
            print(f"{row['model']} | {row['ca_demo']} | {row['dung']} | {row['co_trich_dan']} | {row['thoi_gian_ms']} | {row['trang_thai']}")
        print("Local tắt giả lập:", "không sẵn sàng" if report["local_tat_gia_lap"]["khong_san_sang"] else "chưa đạt")
        print("Cloud:", report["so_luot_cloud"], "— Báo cáo:", ten)
        return 0 if (report["ket_qua"] and all(r["dung"] for r in report["ket_qua"])
                     and report["local_tat_gia_lap"]["khong_san_sang"] and report["so_luot_cloud"] == 0) else 1
    except (OSError, ValueError):
        print("Không thể thử Local hoặc ghi báo cáo DEMO; kiểm tra địa chỉ và thư mục chạy.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
