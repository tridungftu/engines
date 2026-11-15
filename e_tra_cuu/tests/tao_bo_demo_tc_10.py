"""Nguồn tạo fixture TC-10, chỉ thư viện chuẩn, không gọi engine/model.

Đáp án do người viết test đặt, CHƯA được nghiệp vụ duyệt. Không chạy lại
generator trong bài chấm; sửa fixture phải review cả nguồn và đáp án.
"""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path


DEMO = Path(__file__).resolve().parents[1] / "goi/e_tra_cuu/demo/tc-10"
BEN_KY = "Bên ký: Công ty DEMO Ánh Dương (DEMO-P)."
DOI_TUONG = "Đối tượng DEMO-DT; Công trình DEMO-CT-01 tại địa điểm DEMO."
VAY = ("Công ty DEMO Ánh Dương\nĐiều 1. Nghĩa vụ DEMO\n"
       "Khoản vay DEMO-VAY-A có giá trị 1.000.000 VND, ngày 2026-10-30.\n"
       "Khoản vay DEMO-VAY-B có giá trị 2.000.000 USD, ngày 2026-11-01.\n"
       "Mã khoản vay 0007.")
NHAN_SU = ("Công ty DEMO Ánh Dương\nĐiều 1. Nghĩa vụ DEMO\n"
           "Nhân sự DEMO-NS-01 có giá trị 1.000.000 VND, ngày 2026-10-30.")
# Nhóm/loại đáp án được đặt ở đây, không lấy kết quả hay quy tắc runtime.
PHAN_LOAI = [
    ("phap_ly_du_an", "01", "Giấy phép xây dựng DEMO"),
    ("vay", "02", "Hợp đồng tín dụng DEMO"),
    ("mua_hang", "03", "Mua dịch vụ văn phòng DEMO"),
    ("thue_may", "03", "Thuê máy thi công DEMO"),
    ("cong_trinh", "04", "Thi công có BOQ DEMO"),
    ("thiet_bi_lap_dat", "04", "Thiết bị kèm lắp đặt DEMO"),
    ("vat_tu_cdt_cap", "04", "Vật tư chủ đầu tư cấp DEMO"),
    ("sua_chua_bao_tri", "04", "Sửa chữa bảo trì DEMO"),
    ("ban_nha", "05", "Hợp đồng bán nhà DEMO"),
    ("kcn", "05", "Điện năng gắn hợp đồng KCN DEMO"),
    ("ban_nhua", "05", "Bán nhựa DEMO"),
    ("ban_dien_doc_lap", "05", "Bán điện độc lập DEMO"),
    ("cp", "06", "Đại hội đồng cổ đông DEMO"),
    ("tnhh", "06", "Hội đồng thành viên chủ sở hữu DEMO"),
    ("quy_che_lao_dong", "07", "Quy chế thưởng phạt người lao động DEMO"),
    ("nhan_su", "07", "Hợp đồng lao động DEMO"),
    ("quy_che_khac", "08", "Quy chế văn thư DEMO"),
]


def bam(raw):
    return "sha256:" + sha256(raw).hexdigest()


def tao_bo():
    DEMO.mkdir(parents=True, exist_ok=True)
    nguon, kich_ban, dap_an = {}, [], {}

    def them_nguon(ma, chu, nhom="02", phien="1"):
        ten = ma + "-DEMO.txt"
        raw = chu.encode("utf-8")
        (DEMO / ten).write_bytes(raw)
        nguon[ma] = {"tep": ten, "bam": bam(raw), "bytes": len(raw),
                     "nhom": nhom, "phien_ban": phien}

    them_nguon("vay", VAY)
    them_nguon("vay-moi", VAY.replace("1.000.000 VND", "2.000.000 VND"), phien="2")
    them_nguon("nhan-su", NHAN_SU, "07")

    for quy_tac, nhom, ten in PHAN_LOAI:
        ma = "PL-" + quy_tac
        chu = BEN_KY + "\n" + ten + ".\n" + DOI_TUONG
        them_nguon(ma, chu, nhom)
        cho = quy_tac in {"ban_nhua", "ban_dien_doc_lap"}
        kich_ban.append({"ma": ma, "tac_vu": "phan_loai", "nguon": [ma], "nhom": nhom,
                        "quy_tac": quy_tac, "loai_hinh": "TNHH" if quy_tac == "tnhh" else "CP",
                        "trang_thai_loai": "cho_kich_hoat" if cho else "hoat_dong",
                        "local": {"nhom_de_xuat": nhom, "loai_de_xuat": None if cho else "DEMO-" + quy_tac,
                                  "doi_tuong": "DEMO-DT", "diem": 0.95,
                                  "ly_do_cho": [], "de_nghi_chuyen_bo": False}})
        dap_an[ma] = {"chi_so": ["phan_loai_dung"], "nhom": nhom,
                      "giai_doan": "cho_phan_loai" if cho else "da_phan_loai",
                      "nhom_de_xuat": nhom, "loai_de_xuat": None if cho else "DEMO-" + quy_tac,
                      "ly_do": ["CHO_KICH_HOAT"] if cho else []}

    for ma, quy_tac, chu, sua, ly_do in [
        ("PL-vat-tu-thieu-cong-trinh", "vat_tu_cdt_cap", BEN_KY + "\nVật tư chủ đầu tư cấp DEMO.\nĐối tượng DEMO-DT.",
         {"cong_trinh": False}, "THIEU_CONG_TRINH"),
        ("PL-sua-chua-thieu-cong-trinh", "sua_chua_bao_tri", BEN_KY + "\nSửa chữa bảo trì DEMO.\nĐối tượng DEMO-DT.",
         {"cong_trinh": False}, "THIEU_CONG_TRINH"),
        ("PL-vay-chua-do", "vay", BEN_KY + "\nHợp đồng tín dụng DEMO.\n" + DOI_TUONG,
         {"da_do": False}, "CHUA_DO"),
    ]:
        nhom = "02" if quy_tac == "vay" else "04"
        them_nguon(ma, chu, nhom)
        local = {"nhom_de_xuat": nhom, "loai_de_xuat": "DEMO-" + quy_tac, "doi_tuong": "DEMO-DT",
                 "diem": 0.95, "ly_do_cho": [], "de_nghi_chuyen_bo": False}
        kich_ban.append({"ma": ma, "tac_vu": "phan_loai", "nguon": [ma], "nhom": nhom,
                        "quy_tac": quy_tac, "local": local, **sua})
        dap_an[ma] = {"chi_so": ["phan_loai_dung"], "nhom": nhom, "giai_doan": "cho_phan_loai",
                      "nhom_de_xuat": nhom, "loai_de_xuat": "DEMO-" + quy_tac, "ly_do": [ly_do]}

    def bang(ma_nguon="vay", entity="DEMO-VAY-A", *, ngay=True):
        b = entity == "DEMO-VAY-B"
        ns = ma_nguon == "nhan-su"
        so, tien_te = (2000000, "USD") if b else (2000000 if ma_nguon == "vay-moi" else 1000000, "VND")
        ngay_iso = "2026-11-01" if b else "2026-10-30"
        hien = f'{so // 1000000}.000.000 {tien_te}'
        cau = f'{"Nhân sự" if ns else "Khoản vay"} {entity} có giá trị {hien}, ngày {ngay_iso}.'
        e = {"loai": "nhan_su" if ns else "khoan_vay", "ma": entity, "gia_tri": entity}
        ds = [{"nguon": ma_nguon, "thuc_the": e, "truong": "gia_tri", "gia_tri": {"so": so, "tien_te": tien_te},
               "hien_thi": hien, "don_vi": tien_te, "cau": cau}]
        if ngay:
            ds.append({"nguon": ma_nguon, "thuc_the": deepcopy(e), "truong": "ngay", "gia_tri": ngay_iso,
                       "hien_thi": ngay_iso, "don_vi": None, "cau": cau})
        return ds

    def tra(ma, tang=1, *, entity="DEMO-VAY-A", ma_nguon="vay", ai=False, bang_khac=None,
            tu_choi=False, nhan=None, **sua):
        ds = bang(ma_nguon, entity) if bang_khac is None else deepcopy(bang_khac)
        nhom = "07" if ma_nguon == "nhan-su" else "02"
        cb = {"ma": ma, "tac_vu": "soan_tra_loi", "nhom": nhom, "module": "M7" if nhom == "07" else "M9",
              "nguon": list(dict.fromkeys([ma_nguon] + [b["nguon"] for b in ds])), "tang": tang,
              "ai": ai, "cau_hoi": f'Giá trị và ngày của {entity} là gì?', "thuc_the": bang(ma_nguon, entity)[0]["thuc_the"],
              "local": {"bang_chung": ds}, **sua}
        kich_ban.append(cb)
        claims, cac_cau = [], []
        for b in ds:
            raw = (DEMO / nguon[b["nguon"]]["tep"]).read_bytes()
            text = raw.decode("utf-8")
            a = text.index(b["cau"])
            src = "DEMO-NGUON-" + str(cb["nguon"].index(b["nguon"]) + 1)
            claims.append({"thuc_the": b["thuc_the"]["ma"], "truong": b["truong"],
                           "gia_tri": deepcopy(b["gia_tri"]), "don_vi": b["don_vi"],
                           "can_cu": [{"ma_nguon": src, "phien_ban_nguon": nguon[b["nguon"]]["phien_ban"],
                                       "bam_goc": bam(raw), "cau": b["cau"], "bat_dau": a, "ket_thuc": a + len(b["cau"])}]})
            cac_cau.append(f'{"Giá trị" if b["truong"] == "gia_tri" else "Ngày"} ({b["thuc_the"]["ma"]}): {b["hien_thi"]}.')
        mau_thuan = bool(sua.get("mau_thuan"))
        dap_an[ma] = {"chi_so": ["tu_choi_dung"] if tu_choi else ["tra_loi_dung", "trich_dan_dung"],
                      "nhom": nhom, "khang_dinh": [] if tu_choi else claims,
                      "nhan": None if tu_choi else nhan or ("vang" if ai or mau_thuan else "xanh"),
                      "co_mau_thuan": mau_thuan,
                      "tra_loi": None if tu_choi else ("Có mâu thuẫn trong bằng chứng; Anh cần duyệt các giá trị sau.\n" if mau_thuan else "") + "\n".join(cac_cau)}

    tra("TL-Python-A")
    tra("TL-Python-B", entity="DEMO-VAY-B")
    tra("TL-Local-A", 2, ai=True)
    tra("TL-Local-B", 2, ai=True, entity="DEMO-VAY-B")
    tra("TL-Local-tang-1", ai=True)
    tra("TL-Local-tang-3", 3, ai=True)
    tra("TL-khong-dap-an", bang_khac=[], tu_choi=True)
    tra("TL-het-hieu-luc", tu_choi=True, trang_thai_bang={"con_hieu_luc": False, "hieu_luc_den": "2026-10-31"})
    tra("TL-phien-ban-moi", ma_nguon="vay-moi")
    tra("TL-van-ban-cho-duyet", nhan="vang", co_van_ban_moi_cho_duyet=True)
    tra("TL-nhan-su-Local", 2, ai=True, ma_nguon="nhan-su", entity="DEMO-NS-01")
    tra("TL-mau-thuan-Python", bang_khac=bang(ngay=False) + bang("vay-moi", ngay=False), mau_thuan=True)
    tra("TL-mau-thuan-Local", 2, ai=True, bang_khac=bang(ngay=False) + bang("vay-moi", ngay=False), mau_thuan=True)
    tra("TL-phu-thuoc-thoi-diem", 2, ai=True, phu_thuoc_thoi_diem=True,
        cau_hoi="Hiện nay giá trị và ngày của DEMO-VAY-A là gì?")
    for sai in ("gia_tri", "offset", "ngay", "quote"):
        tra("TL-tu-choi-" + sai, 2, ai=True, tu_choi=True, sai_local=sai)

    header = {"phien_ban": 1, "nhan": "DEMO", "da_duyet_nghiep_vu": False,
              "nguong_that_da_duyet": False, "nhom_duoc_kich_hoat": [],
              "ghi_chu": "Đáp án kiểm cơ chế, chưa nghiệm thu nghiệp vụ hoặc accuracy model thật."}
    files = {"bo-ca-DEMO.json": {**header, "nguon": nguon, "kich_ban": kich_ban},
             "dap-an-DEMO.json": {**header, "dap_an": dap_an}}
    for ten, data in files.items():
        (DEMO / ten).write_bytes((json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8"))
    pin = {p.name: bam(p.read_bytes()) for p in sorted(DEMO.iterdir()) if p.is_file() and p.name != "bam-DEMO.json"}
    (DEMO / "bam-DEMO.json").write_bytes((json.dumps(pin, indent=2) + "\n").encode("ascii"))
    print(f"Đã tạo {len(kich_ban)} ca DEMO; đáp án chưa được nghiệp vụ duyệt.")


if __name__ == "__main__":
    tao_bo()
