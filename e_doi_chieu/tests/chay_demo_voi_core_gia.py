"""DC-12: điều phối DEMO ngoài runtime, chỉ CoreGia/Local/OCR giả.

SDK 2.2 giữ ngăn RAM của CoreGia; NganBoNho NGAN-0 chỉ kiểm tương thích
riêng, không thay viec.ngan. Tệp luôn được them_tep/tai_tep_ra trước khi dùng.
"""
import sys

sys.dont_write_bytecode = True

import importlib.util
import json
from pathlib import Path

from test_dc3 import Mau, chay, hs, kiem_loi
from test_dc4 import so
from test_dc6 import dat_tu_dien, chuan_bi, hau_kiem, DieuPhoiDEMO, chay_buoc
from test_dc8 import tao_mau, quet
from test_dc9 import doc_kq, xuat
from demo_lech_dau import CoreOCRVungDEMO, dat_cap_co_tu, manifest_ocr

THU_MUC = Path(__file__).resolve().parent


def dap_an():
    return json.loads((THU_MUC / "fixtures/DEMO-dap-an-dc12.json").read_text(encoding="utf-8"))["ca"]


def nap_mau(ca):
    m = Mau(CoreOCRVungDEMO())
    dat_tu_dien(m)
    dat_cap_co_tu(m, ca["word"], ca["ban_ky"])
    return m


def nhan_va_so(m):
    doc = chay_buoc(m, "doc_docx", {"loai": "tep", "tep": m.cap["nguon"]["word"]["tep"]})
    assert doc["trang_thai"] == "XONG", doc
    m.dat_vb(doc["ket_qua"], "word")
    # Bắt đầu bằng tệp JSON cặp, không ghim snapshot đã sửa để giả toàn tuyến.
    nhan = m.chay()
    assert nhan["trang_thai"] == "XONG", nhan
    r = so(m, nhan["ket_qua"])
    assert r["trang_thai"] == "XONG", r
    return r["ket_qua"]


def local_va_xuat(m, pb, *, nhan="nhieu_ocr", sai_trich=False, ocr_lai=False):
    provider = DieuPhoiDEMO()
    s = m.snapshot({"ket_qua": pb})
    if not any(d["cho_phan_loai"] for d in s["diem_lech"]):
        # Core bỏ qua AI đúng contract, không tạo tra_loi_ai thành công giả.
        t, out, _ = doc_kq(m, xuat(m, pb))
        assert provider.local == provider.cloud == 0
        return t, out, pb, None, None
    manifest = manifest_ocr(m, s) if ocr_lai else None
    request = chuan_bi(m, pb)
    reply = provider.hoi(m, request, nhan)
    if sai_trich:
        for row in reply["tra_loi_ai"]["du_lieu"]["diem"]:
            for ben in ("trai", "phai"):
                if row[ben]:
                    row[ben]["cau"] = "DEMO câu bịa không có trong nguồn."
    if manifest:
        from test_dc6 import giao
        vid = giao(m, "phan_loai_diem_lech", reply)
        m.core.ocr_vung_viec[vid] = manifest
        m.core.chay(chay.app)
        r = m.core.xem(vid)
    else:
        r = hau_kiem(m, reply)
    assert r["trang_thai"] == "XONG", r
    if manifest:
        from test_dc6 import giao
        vid = giao(m, "xuat_ket_qua", r["ket_qua"])
        m.core.ocr_vung_viec[vid] = manifest
        m.core.chay(chay.app)
        result = m.core.xem(vid)
    else:
        result = xuat(m, r["ket_qua"])
    t, out, _ = doc_kq(m, result)
    assert provider.local == 1 and provider.cloud == 0
    return t, out, r["ket_qua"], request, reply


def do_ca(ca):
    m = nap_mau(ca)
    pb = nhan_va_so(m)
    truoc = m.snapshot({"ket_qua": pb})
    t, out, _, request, _ = local_va_xuat(m, pb)
    points = out["diem_lech"]
    assert points, ca["ma"]
    assert {d["ma_diem"] for d in points} == {d["ma_diem"] for d in truoc["diem_lech"]}
    # Mỗi ca là một thay đổi nghiệp vụ đã cài, có thể sinh nhiều điểm edit script.
    # Không lấy danh sách đầu ra làm đáp án. Quy tắc kỳ vọng nằm trong JSON độc lập.
    bat_du = not ca["nghiem_trong"] or any(
        ca["quy_tac"] in d["quy_tac_trung"] and d["muc"] == "nghiem_trong" for d in points)
    if ca["nghiem_trong"]:
        assert all(d["muc"] == "nghiem_trong" for d in points if d["phep"] != "kiem_noi_bo")
    bi_an = any(d["muc"] == "nhieu_ocr" for d in points)
    assert bat_du and not bi_an, ca["ma"]
    assert t["de_nghi_chan"] and not t["da_kiem_du"]
    assert t["ket_luan"] == "chua_doi_chieu_duoc"  # Thiếu đo detector/trang, không báo sạch.
    return {"ma": ca["ma"], "nghiem_trong": ca["nghiem_trong"],
            "bat_du": bat_du, "bi_an_thanh_nhieu": bi_an, "so_diem_may": len(points),
            "so_nghiem_trong_may": sum(d["muc"] == "nghiem_trong" for d in points),
            "local_gia": int(request is not None)}


def kiem_ngan_bo_nho():
    """Nạp nguyên mẫu NGAN-0 riêng; chuỗi runtime vẫn dùng SDK 2.2."""
    p = THU_MUC.parent / "goi/e_doi_chieu/tham_chieu_ngan_0/ngan.py"
    spec = importlib.util.spec_from_file_location("dc12_ngan_0", p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    ngan = mod.NganBoNho([{"bang": "demo", "khoa": ["ma"], "pham_vi": "phap_nhan",
                          "truong": [{"ma": "ma", "kieu": "van_ban"}]}])
    with ngan.lo() as lo:
        kq = lo.lay_hoac_tao("demo", {"phap_nhan_id": "DEMO-P", "ma": "DEMO"}, {})
    assert kq.da_tao and kq.gia_tri["ma"] == "DEMO"
    assert ngan.doc("demo", {"phap_nhan_id": "DEMO-Q", "ma": "DEMO"}) is None


def kiem_loi_nguon():
    cases = ("DC_SAI_NGUON", "DC_QUA_GIOI_HAN", "CHUA_CAU_HINH", "DC_OCR_KHONG_DOC_DUOC")
    for ma in cases:
        m = nap_mau(dap_an()[0])
        if ma == "DC_SAI_NGUON":
            m.cap["nguon"]["word"]["bam"] = "sha256:" + "0" * 64
        elif ma == "DC_QUA_GIOI_HAN":
            m.cau_hinh["so_trang_toi_da"] = 1
            m.dat_cau_hinh()
            dat_cap_co_tu(m, "DEMO", "DEMO\fDEMO")
        elif ma == "CHUA_CAU_HINH":
            m.core.dat_cau_hinh(chay.app.ma, {})
        else:
            m.cap["kiem_dau_vao"]["ocr_day_du"] = False
        kiem_loi(m.chay(), ma)
    return list(cases)


def chay_demo():
    kiem_ngan_bo_nho()
    rows = [do_ca(ca) for ca in dap_an()]
    # Tất cả 7 năng lực thật trong engine; Local và OCR được CoreGia điều phối.
    m = tao_mau("gach")
    dat_tu_dien(m)
    pb = nhan_va_so(m)
    scan = quet(m, None, pb)
    assert scan["trang_thai"] == "XONG", scan
    t, s, _, request, _ = local_va_xuat(m, scan["ket_qua"], nhan="can_xem")
    assert request is not None
    assert s["vung_sua_tay"] and t["de_nghi_chan"] and not t["da_kiem_du"]
    # Nhánh OCR lại đầy đủ căn cứ giả; không trộn vào mẫu số sửa thật.
    m = nap_mau({"word": "DEMO thuê.", "ban_ky": "DEMO thuế."})
    t, s, _, _, _ = local_va_xuat(m, nhan_va_so(m), ocr_lai=True)
    assert t["so_nhieu_ocr"] > 0 and all(d["muc"] == "nhieu_ocr" for d in s["diem_lech"])
    errors = kiem_loi_nguon()
    return {"nhan": "DEMO; đã kiểm bằng Core giả (CoreGia)", "so_ca_chuoi": len(rows) + 2,
            "nghiem_trong_bat_du": sum(r["bat_du"] for r in rows if r["nghiem_trong"]),
            "nghiem_trong_da_cai": sum(r["nghiem_trong"] for r in rows),
            "sua_that_bi_an_thanh_nhieu": sum(r["bi_an_thanh_nhieu"] for r in rows),
            "sua_that_da_cai": len(rows), "ca": rows, "loi_nguon": errors,
            "so_diem_may_trong_bo_dap_an": sum(r["so_diem_may"] for r in rows),
            "so_diem_nghiem_trong_trong_bo_dap_an": sum(r["so_nghiem_trong_may"] for r in rows),
            "so_luot_local_gia": sum(r["local_gia"] for r in rows) + 2,
            "cloud_that": 0, "ocr_that": 0, "ai_that": 0,
            "do_chat_luong_may_that": None,
            "ly_do_chua_do": "Chưa có Core/OCR/Local thật; detector/ngưỡng/nguồn từ điển chưa nghiệm thu."}


if __name__ == "__main__":
    print(json.dumps(chay_demo(), ensure_ascii=False, indent=2))
