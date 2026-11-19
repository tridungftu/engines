"""Hai bảng tổng quát DEMO, khuôn và đáp án độc lập với runtime."""

from decimal import Decimal


def cot(ma, tu, kieu, bat_buoc=True):
    return {"ma": ma, "tu_khoa": [tu], "bat_buoc": bat_buoc, "kieu": kieu}


KHUON_GIA_THANH = {
    "phien_ban": 1,
    "cot": [cot("san_pham", "san pham", "van_ban"), cot("san_luong", "san luong", "so"),
            cot("vat_lieu", "chi phi vat lieu", "so_tien"), cot("nhan_cong", "chi phi nhan cong", "so_tien"),
            cot("ngay", "ngay", "ngay"), cot("ghi_chu", "ghi chu", "van_ban", False)],
    "dong_dung": ["=tong cong"],
}
KHUON_BAO_GIA = {
    "phien_ban": 1,
    "cot": [cot("ma_hang", "=ma hang", "van_ban"), cot("mo_ta", "mo ta", "van_ban"),
            cot("don_gia", "gia dot #", "so_tien"), cot("hieu_luc", "hieu luc", "ngay"),
            cot("chiet_khau", "chiet khau", "so", False)],
    "dong_dung": ["=cong"],
}

DAP_AN = {
    "gia-thanh-DEMO.xlsx": {
        "sheet": "Gia thanh DEMO", "dong_tieu_de": 3, "so_dong": 2, "so_dong_nhom": 1,
        "cot": {"san_pham": "A", "san_luong": "B", "vat_lieu": "C", "nhan_cong": "D", "ngay": "E"},
        "tien_te": "VND", "so_canh_bao": 0,
        "gia_tri": [
            {"san_pham": "SP DEMO 001", "san_luong": "12.5", "vat_lieu": {"so": "1000000", "tien_te": "VND"},
             "nhan_cong": {"so": "250000", "tien_te": "VND"}, "ngay": "2026-10-30", "ghi_chu": None},
            {"san_pham": "SP DEMO 002", "san_luong": "0", "vat_lieu": {"so": "-125.25", "tien_te": "VND"},
             "nhan_cong": {"so": "0", "tien_te": "VND"}, "ngay": "2026-10-31", "ghi_chu": None},
        ],
    },
    "bao-gia-DEMO.xlsx": {
        "sheet": "Bao gia DEMO", "dong_tieu_de": 4, "so_dong": 2, "so_dong_nhom": 0,
        "cot": {"ma_hang": "B", "mo_ta": "D", "don_gia": "F", "hieu_luc": "H", "chiet_khau": "J"},
        "tien_te": "USD", "so_canh_bao": 1,
        "gia_tri": [
            {"ma_hang": "0001", "mo_ta": "Dịch vụ DEMO A", "don_gia": {"so": "2500000000.125", "tien_te": "USD"},
             "hieu_luc": "2026-10-30", "chiet_khau": "0.05"},
            {"ma_hang": "0002", "mo_ta": "Dịch vụ DEMO B", "don_gia": {"so": "9007199254740993", "tien_te": "USD"},
             "hieu_luc": "2026-11-01", "chiet_khau": None},
        ],
    },
}


def cac_mau():
    from sinh_demo import NHAN, sheet, workbook
    gia_thanh = [
        ("A1", NHAN), ("A2", "Bảng giá thành DEMO — đơn vị tiền VND"),
        ("A3", "Sản phẩm"), ("B3", "Sản lượng"), ("C3", "Chi phí"), ("E3", "Ngày"),
        ("C4", "Vật liệu"), ("D4", "Nhân công"), ("A5", "Nhóm sản xuất DEMO"),
        ("A6", "SP DEMO 001"), ("B6", Decimal("12.5")), ("C6", 1000000), ("D6", 250000), ("E6", "2026-10-30"),
        ("A7", "SP DEMO 002"), ("B7", 0), ("C7", Decimal("-125.25")), ("D7", 0), ("E7", "31/10/2026"),
        ("A8", "Tổng cộng"), ("C8", Decimal("999874.75"), "SUM(C6:C7)"),
        ("A9", "DEMO sau dòng dừng"), ("B9", 1), ("C9", 999), ("D9", 999), ("E9", "2026-10-30"),
    ]
    bao_gia = [
        ("A1", NHAN), ("B2", "Bảng báo giá DEMO — tiền tệ USD"),
        ("B4", "Mã hàng"), ("D4", "Mô tả"), ("F4", "Giá đợt 12"), ("H4", "Hiệu lực"), ("J4", "Chiết khấu"),
        ("B5", "0001"), ("D5", "Dịch vụ DEMO A"), ("F5", "2500000000.125"), ("H5", "30/10/2026"), ("J5", Decimal("0.05")),
        ("B6", "0002"), ("D6", "Dịch vụ DEMO B"), ("F6", 9007199254740993), ("H6", "2026-11-01"),
        ("B7", "Cộng"), ("F7", 0, "0"),
        ("B8", "0003"), ("D8", "DEMO sau dòng dừng"), ("F8", 999), ("H8", "2026-10-30"),
    ]
    return {
        "gia-thanh-DEMO.xlsx": workbook([("Gia thanh DEMO", sheet(gia_thanh, gop=("A3:A4", "B3:B4", "C3:D3", "E3:E4", "A5:E5")), "visible")]),
        "bao-gia-DEMO.xlsx": workbook([("Gioi thieu DEMO", sheet([("A1", NHAN)]), "visible"), ("Bao gia DEMO", sheet(bao_gia), "visible")]),
    }
