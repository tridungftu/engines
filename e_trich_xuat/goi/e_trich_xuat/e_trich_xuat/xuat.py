"""TX-3: xuất hai tệp trong RAM; lõi chờ review, chưa đăng ký runtime."""

from copy import deepcopy
from io import BytesIO

from kho_tri_thuc_sdk.engine import ChuaRo, LoiDuongTruyen, LoiNghiepVu, ViecDaHuy

from .hau_kiem import kiem_bang, kiem_tep, loi
from .tham_so import json_bytes
from .xlsx_mini import write_xlsx


MIME_EXCEL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _o(v):
    # Dữ liệu JSON là chuẩn. Tiền/ngày/số dài giữ bằng text JSON/nguyên văn
    # để Excel không đổi độ chính xác, số 0 đầu hoặc công thức.
    if v is None:
        return "null"
    return v if isinstance(v, str) else json_bytes(v).decode("utf-8")


def cac_sheet(b):
    cot = ["Mã", "Tên", "Kiểu", "Giá trị", "Nguyên văn AI", "Đơn vị nguyên văn",
           "Ghi chú", "Cần soát", "Lý do", "Kiểm tra logic", "Dấu kiểm tạm E6", "Đã chuyển kiểu"]
    bang = [cot]
    dan = [["Mã", "Câu nguyên văn", "Bắt đầu Unicode", "Kết thúc Unicode",
            "Loại vị trí", "Nhãn", "Số trang", "Hộp OCR"]]
    for r in b["bang"]:
        bang.append([r["ma"], r["ten"], r["kieu"], _o(r["gia_tri"]), _o(r["nguyen_van"]),
                     _o(r["don_vi_nguyen_van"]), _o(r["ghi_chu"]), _o(r["can_soat"]),
                     "\n".join(r["ly_do"]), "\n".join(r["kiem_tra_logic"]),
                     _o(r.get("dau_kiem_tam_e6")), _o(r["kieu_da_chuyen"])])
        for q in r["dan_chung"]:
            v = q["vi_tri"]
            dan.append([r["ma"], q["cau"], q["bat_dau"], q["ket_thuc"], v["loai"],
                        v["nhan"], _o(v["so_trang"]), _o(v["hop"])])
    # Mỗi lá metadata/phản hồi gốc là một ô, không thêm dấu nháy JSON
    # khiến trường sát trần bị vượt chỉ vì cách đóng gói Excel.
    def phang(v):
        rows = [["Trường", "Kiểu JSON", "Giá trị"]]
        def them(k, x):
            if isinstance(x, dict) and x:
                for key, val in x.items():
                    them(k + "." + key if k else key, val)
            elif isinstance(x, list) and x:
                for i, val in enumerate(x):
                    them(k + f"[{i}]", val)
            else:
                kieu = ("string" if isinstance(x, str) else "null" if x is None
                        else "boolean" if type(x) is bool else "array" if isinstance(x, list)
                        else "object" if isinstance(x, dict) else "number")
                rows.append([k, kieu, _o(x)])
        them("", v)
        return {"rows": rows, "widths": [55, 15, 85]}
    return {"Kết quả": {"rows": bang, "widths": [16, 35, 16, 40, 40]},
            "Dẫn chứng": {"rows": dan, "widths": [16, 75, 20, 20, 16, 35, 12, 30]},
            "Nguồn": phang({k: v for k, v in b.items() if k != "bang"}),
            "AI nguyên văn": phang({r["ma"]: r.get("phan_hoi_ai") for r in b["bang"]})}

def xuat_ket_qua(viec):
    viec.kiem_huy()
    phong_bi = deepcopy(viec.dau_vao)
    raw = kiem_bang(phong_bi)
    b = phong_bi["bang_trich_xuat"]
    viec.tien_do(15, "Đã kiểm bảng trước khi xuất.")
    # Không có tệp tạm trên đĩa. BytesIO đóng trong finally cả lỗi/hủy.
    bo_nho = BytesIO()
    try:
        try:
            write_xlsx(bo_nho, cac_sheet(b), kiem_huy=viec.kiem_huy)
            excel = bo_nho.getvalue()
            viec.kiem_huy()
            viec.tien_do(55, "Đã tạo đủ dữ liệu JSON và Excel.")
            tep_json = viec.tai_tep_ra("ket-qua-trich-xuat.json", raw, "application/json")
            viec.kiem_huy()
            viec.tien_do(75, "Đang gửi đủ tệp kết quả tới Core.")
            tep_excel = viec.tai_tep_ra("ket-qua-trich-xuat.xlsx", excel, MIME_EXCEL)
            if not (kiem_tep(tep_json, mime="application/json")
                    and kiem_tep(tep_excel, mime=MIME_EXCEL)
                    and tep_json["kich_thuoc"] == len(raw)
                    and tep_excel["kich_thuoc"] == len(excel)
                    and tep_json["tep_id"] != tep_excel["tep_id"]):
                loi("XUAT_KET_QUA_LOI")
        except (ViecDaHuy, ChuaRo):
            raise
        except LoiDuongTruyen as exc:
            if exc.http_status in (404, 409, 410):
                raise
            loi("XUAT_KET_QUA_LOI")
        except LoiNghiepVu as exc:
            if exc.ma in ("O_EXCEL_QUA_DAI", "VUOT_GIOI_HAN", "XUAT_KET_QUA_LOI"):
                raise
            loi("XUAT_KET_QUA_LOI")
        except Exception:
            loi("XUAT_KET_QUA_LOI")
        viec.tien_do(100, "Đã gửi đủ tệp JSON và Excel.")
        viec.kiem_huy()
        return {"loai": "truong", "truong": {
            "tep_json": tep_json, "tep_excel": tep_excel, **b["tom_tat"]}}
    finally:
        bo_nho.close()
