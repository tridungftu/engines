"""Sinh fixture PL-0B bằng thư viện chuẩn; không chạy engine hay gọi AI.

Chạy từ bất kỳ thư mục nào: python -B <đường tới sinh_demo.py>.
JSON UTF-8 không BOM, LF, khóa sắp xếp; không phụ thuộc đồng hồ hoặc locale.
bam-demo.json băm mọi JSON đầu ra trừ chính nó (tránh băm tự tham chiếu).
Đáp án lớp 1 dựng sẵn, không gọi thuật toán engine để sinh đáp án.
khau thuộc Cài đặt bước: cùng lô chạy riêng cho từng khâu trong KHAU.
tep_id và ma_luot là mã giả DEMO; cần nạp vào CoreGia trước test tích hợp.
"""

from __future__ import annotations

import copy
import hashlib
import json
import random
from pathlib import Path


HAT_GIONG = 20261120
CONG_TY = "Công ty DEMO Ánh Dương"
KHAU = ("kt_kiem", "ktt_duyet", "cfo_duyet")
TEN_LOAI = (
    ("thanh_toan_ncc", "Thanh toán nhà cung cấp DEMO", "thanh toán"),
    ("tam_ung", "Tạm ứng DEMO", "tạm ứng"),
    ("luong", "Lương DEMO", "lương"),
    ("chi_phi_khac", "Chi phí khác DEMO", "chi phí khác"),
    ("thu_tien", "Thu tiền DEMO", "thu tiền"),
)


def ma_hoa(du_lieu: object) -> bytes:
    return (json.dumps(du_lieu, ensure_ascii=False, sort_keys=True,
                       indent=2, allow_nan=False) + "\n").encode("utf-8")


def bam(du_lieu: bytes) -> str:
    return "sha256:" + hashlib.sha256(du_lieu).hexdigest()


def tien(so: int, tien_te: str = "VND") -> dict:
    return {"so": str(so), "tien_te": tien_te}


def sinh_bo_demo() -> dict[str, bytes]:
    """Trả đường dẫn tương đối với thư mục engine → bytes, chưa ghi đĩa."""
    ngau_nhien = random.Random(HAT_GIONG)
    nguong = {"pm": tien(5_000_000_000), "te": tien(3_000_000_000),
              "sad": tien(250_000_000)}
    danh_muc = [{"ma": ma, "ten": ten, "mo_ta": f"Nghiệp vụ {ten}"}
                for ma, ten, _ in TEN_LOAI]
    bo = {"phien_ban": 1, "quy_tac": [
        {"loai": ma, "khi": [{"tat_ca": [[tu]], "khong_co": []}]}
        for ma, _, tu in TEN_LOAI
    ]}
    ds, dap_an = [], {}
    # Nền: đối tác riêng, tiền < TE; không vô tình tạo nhóm chia nhỏ.
    for chi_so in range(500):
        stt = chi_so + 1
        ma, _, tu = TEN_LOAI[chi_so % 5]
        nguon = "module" if stt % 3 == 0 else "quy_tac"
        ds.append({
            "ma": f"PC-DEMO-{stt:04d}",
            "loai": ma if nguon == "module" else None,
            "ngay": f"2026-{10 + ngau_nhien.randrange(2):02d}-{1 + ngau_nhien.randrange(28):02d}",
            "so_tien": tien(1_000_001 + ngau_nhien.randrange(2_799_000_000)),
            "so_tien_quy_doi": None, "doi_tac": f"DEMO-NCC-{stt:04d}",
            "dien_giai": f"{tu.capitalize()} DEMO nghiệp vụ {stt:04d}",
            "tai_khoan_no": "331", "tai_khoan_co": "1121",
            "nhap_tay": False, "co_do_cung": False, "thuoc_tinh": {},
        })
        dap_an[ds[-1]["ma"]] = {"ly_do": [], "loai": ma, "nguon_loai": nguon}

    def cai(stt, ca, *, ly_do=(), loai="thanh_toan_ncc", nguon="quy_tac", **doi):
        dong = ds[stt - 1]
        dong.update(ngay="2026-11-16", so_tien=tien(251_000_001), loai=None,
                    dien_giai="Thanh toán DEMO", thuoc_tinh={"ca_demo": ca})
        dong.update(doi)
        dap_an[dong["ma"]] = {"ly_do": list(ly_do), "loai": loai, "nguon_loai": nguon}

    cai(1, "vuot_te", so_tien=tien(3_200_000_000), ly_do=("VUOT_TE",))
    cai(2, "vuot_pm", so_tien=tien(5_100_000_000), ly_do=("VUOT_PM",))
    for stt, ngay in ((3, "2026-11-09"), (4, "2026-11-10"), (5, "2026-11-15")):
        cai(stt, "chia_nho", so_tien=tien(1_100_000_000), ngay=ngay,
            doi_tac="DEMO-NCC-CHIA-NHO", ly_do=("NGHI_CHIA_NHO",))
    cai(6, "doi_tac_moi", doi_tac="DEMO-NCC-MOI", loai="luong",
        dien_giai="Lương DEMO cho đối tác mới")
    cai(7, "so_tron", so_tien=tien(10_000_000))
    cai(8, "ngay_nghi", ngay="2026-11-21")
    cai(9, "cuoi_ky", ngay="2026-11-30")
    cai(10, "nhap_tay", nhap_tay=True)
    cai(11, "co_do_cung", co_do_cung=True, ly_do=("CO_DO_CUNG",))
    cai(12, "usd_chua_quy_doi", so_tien=tien(1000, "USD"), ly_do=("CHUA_QUY_DOI",))
    cai(13, "usd_co_quy_doi", so_tien=tien(124000, "USD"),
        so_tien_quy_doi=tien(3_100_000_000), ly_do=("VUOT_TE",))
    # Ca âm về dữ liệu: cố ý không có mã tiền tệ, không được tự gán VND.
    cai(14, "thieu_tien_te", so_tien={"so": "1000000"}, ly_do=("CHUA_RO_TIEN_TE",))
    cai(15, "module_da_gan", loai="luong", nguon="module")
    ds[14]["loai"] = "luong"  # Nội dung vẫn khớp thanh toán: module phải thắng.
    cai(16, "chi_quy_tac_phan_loai")
    cai(17, "khong_khop", loai="chua_phan_loai", nguon="chua_phan_loai",
        dien_giai="Nội dung ZZZ DEMO chưa xác định")
    cai(18, "tam_ung", loai="tam_ung", dien_giai="Tạm ứng DEMO công tác")
    cai(19, "chi_phi_khac", loai="chi_phi_khac", dien_giai="Chi phí khác DEMO")
    cai(20, "thu_tien", loai="thu_tien", dien_giai="Thu tiền DEMO")

    lo = {"phien_ban": 1, "ten": CONG_TY, "ma_module": "demo_thanh_toan",
          "ky": "2026-11", "nguong": nguong, "nghiep_vu": ds}
    lo_nho = {**lo, "nghiep_vu": copy.deepcopy(ds[:20])}
    # Hồ sơ giả cho cờ DOI_TAC_MOI: mọi đối tác trừ DEMO-NCC-MOI đã gặp ở mỗi loại.
    ho_so = {"doi_tac_da_gap_theo_loai": {
        ma: sorted({d["doi_tac"] for d in ds if d["doi_tac"] != "DEMO-NCC-MOI"})
        for ma, _, _ in TEN_LOAI
    }}
    dap_an_day_du = {
        "phien_ban": 1, "ten": CONG_TY, "khau": list(KHAU),
        "ghi_chu": "DEMO: ly_do chỉ lớp 1; không dự đoán CHON_MAU/KHONG_CHON. "
                    "Cùng lô áp dụng riêng từng khâu; không chia lô theo khâu.",
        "ho_so_demo": ho_so, "theo_ma": dap_an,
        "co_ky_vong_theo_ma": {
            "PC-DEMO-0006": ["DOI_TAC_MOI"], "PC-DEMO-0007": ["SO_TRON"],
            "PC-DEMO-0008": ["NGAY_NGHI"], "PC-DEMO-0009": ["CUOI_KY"],
            "PC-DEMO-0010": ["NHAP_TAY"],
        },
    }
    ket_qua = []
    for khau in KHAU:
        for stt in range(1, 21):
            trang_thai = "sai" if stt <= 4 else "khong_kiem" if stt == 17 else "dat"
            so_sai = {1: 1_000_000, 2: 250_000_000, 3: 3_000_000_000, 4: 0}.get(stt, 0)
            ket_qua.append({
                "ma_luot": f"PL-DEMO-202611-{khau}", "ma": f"PC-DEMO-{stt:04d}",
                "khau": khau, "ket_qua": trang_thai, "so_tien_sai": tien(so_sai),
                "loai_dung": "chi_phi_khac" if stt == 4 else None,
            })

    # Snapshot DEMO cho hậu kiểm, gồm lô và kết quả module/quy tắc đã xác định.
    snapshot = {"phien_ban": 1, "ten": CONG_TY, "lo": lo_nho,
                "phan_loai": {d["ma"]: {"loai": dap_an[d["ma"]]["loai"],
                                        "nguon_loai": dap_an[d["ma"]]["nguon_loai"]}
                              for d in ds[:20] if d["ma"] != "PC-DEMO-0017"},
                "cho_ai": [{"chi_so": 0, "noi_dung": ds[16]["dien_giai"],
                            "ma": ["PC-DEMO-0017"]}]}
    snapshot_byte = ma_hoa(snapshot)
    chuyen_tiep = {"phan_luong": {
        "phien_ban": 1, "tep_lo": {"tep_id": "tep-DEMO-lo-chuyen-tiep",
                                     "ten": "lo-chuyen-tiep-DEMO.json",
                                     "mime": "application/json", "kich_thuoc": len(snapshot_byte)},
        "bam_tep": bam(snapshot_byte), "khau": "ktt_duyet", "khong_can_ai": False,
    }}
    khuon = {
        "$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object",
        "required": ["phan_loai"], "additionalProperties": False,
        "properties": {"phan_loai": {"type": "array", "items": {
            "type": "object", "required": ["chi_so", "loai", "tin_cay"],
            "additionalProperties": False, "properties": {
                "chi_so": {"type": "integer", "minimum": 0},
                "loai": {"type": "string", "enum": [d["ma"] for d in danh_muc]},
                "tin_cay": {"type": "number", "minimum": 0, "maximum": 1},
            },
        }}},
    }
    yeu_cau = {"loai": "yeu_cau_ai", "yeu_cau_ai": {
        "phien_ban": 1, "ma_prompt": "demo_thanh_toan.phan_loai_DEMO",
        "phien_ban_prompt": "DEMO-1", "prompt": "DEMO: chỉ chọn loại trong danh mục.",
        "tai_lieu": json.dumps([{"chi_so": 0, "noi_dung": ds[16]["dien_giai"]}], ensure_ascii=False),
        "khuon_tra_loi": khuon, "bat_buoc_trich_dan": False,
        "model_uu_tien": "DEMO-local-gia", "chuyen_tiep": chuyen_tiep,
    }}
    tra_loi = {"loai": "tra_loi_ai", "tra_loi_ai": {
        "phien_ban": 1, "trang_thai": "co_can_cu", "tra_loi": "Phân loại DEMO.",
        "du_lieu": {"phan_loai": [{"chi_so": 0, "loai": "chi_phi_khac", "tin_cay": 0.9}]},
        "trich_dan": [], "kiem_trich_dan": {"dat": True, "loi": []},
        "nha_cung_cap": "local", "model": "DEMO-local-gia",
        "ly_do_chon_model": "DEMO dựng tay để kiểm hậu xử lý, không gọi nhà cung cấp.",
        "ma_prompt": yeu_cau["yeu_cau_ai"]["ma_prompt"], "phien_ban_prompt": "DEMO-1",
        "phien_ban_engine": "e_hoi_ai DEMO-1", "bam_dau_vao": bam(ma_hoa(yeu_cau)),
        "chuyen_tiep": chuyen_tiep, "canh_bao": [],
    }}
    doi_tuong = {
        "tests/demo/lo-500-DEMO.json": lo,
        "tests/demo/dap-an-lop1.json": dap_an_day_du,
        "tests/demo/danh-muc-loai-DEMO.json": danh_muc,
        "tests/demo/bo-phan-loai-DEMO.json": bo,
        "tests/demo/nguong-DEMO.json": nguong,
        "tests/demo/ket-qua-kiem-mau-DEMO.json": {
            "phien_ban": 1, "ten": CONG_TY, "ma_module": "demo_thanh_toan", "ket_qua": ket_qua},
        "tests/demo/lo-chuyen-tiep-DEMO.json": snapshot,
        "tests/demo/yeu-cau-ai-DEMO.json": yeu_cau,
        "goi/e_phan_luong/demo/lo-nho-DEMO.json": lo_nho,
    }
    for ca in ("dung-enum", "sai-enum", "tin-cay-thap", "cloud", "khong-thay-can-cu"):
        phong_bi = copy.deepcopy(tra_loi)
        noi_dung = phong_bi["tra_loi_ai"]
        if ca == "sai-enum":
            noi_dung["du_lieu"]["phan_loai"][0]["loai"] = "loai_ngoai_danh_muc_DEMO"
        elif ca == "tin-cay-thap":
            noi_dung["du_lieu"]["phan_loai"][0]["tin_cay"] = 0.4
        elif ca == "cloud":
            noi_dung.update(nha_cung_cap="cloud", model="DEMO-cloud-gia")
        elif ca == "khong-thay-can-cu":
            noi_dung.update(trang_thai="khong_thay_can_cu", du_lieu=None,
                            tra_loi="Không thấy căn cứ DEMO.",
                            kiem_trich_dan={"dat": False, "loi": ["Thiếu căn cứ DEMO."]})
        doi_tuong[f"tests/demo/tra-loi-ai-{ca}.json"] = phong_bi
    ket_qua_byte = {ten: ma_hoa(noi_dung) for ten, noi_dung in doi_tuong.items()}
    ket_qua_byte["tests/demo/bam-demo.json"] = ma_hoa({
        "phien_ban": 1, "ten": CONG_TY, "hat_giong_demo": HAT_GIONG,
        "tep": {ten: bam(noi_dung) for ten, noi_dung in ket_qua_byte.items()},
    })
    return ket_qua_byte


def ghi_bo_demo() -> None:
    goc_engine = Path(__file__).resolve().parents[2]
    for ten, noi_dung in sinh_bo_demo().items():
        dich = goc_engine / ten
        dich.parent.mkdir(parents=True, exist_ok=True)
        dich.write_bytes(noi_dung)


if __name__ == "__main__":
    ghi_bo_demo()
