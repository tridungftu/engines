"""DC-9: tổng hợp bảo thủ, snapshot được ghim tại Core và xuất đúng một lượt."""
from collections import Counter
from copy import deepcopy

from kho_tri_thuc_sdk.engine import LoiNghiepVu, ViecDaHuy, ChuaRo

from . import ho_so as hs
from . import chuan_bi_ai as cb
from . import quy_tac as qt
from . import so_chu as sc

PHIEN_BAN = "DC-9-1"
CAC_MUC = ("nghiem_trong", "can_xem", "hinh_thuc", "nhieu_ocr")
TRUONG_DEM = tuple("so_" + k for k in CAC_MUC) + ("so_vung_sua_tay", "so_trang_ocr_kem")


def loi(ma):
    raise LoiNghiepVu(ma, {
        "DC_HO_SO_CHUA_DU": "Hồ sơ chưa đến bước xuất hoặc còn điểm đang chờ phân loại. Anh hoàn tất các bước đối chiếu trước khi xuất.",
        "DC_SAI_NGUON": "Hồ sơ đối chiếu không khớp nguồn đã ghim. Anh kiểm tra lại cặp tài liệu và phiên bản.",
        "DC_THIEU_TAI_NGUYEN": "Chưa đủ font tiếng Việt hợp lệ để lập báo cáo. Anh nhờ quản trị viên bổ sung tài nguyên của gói.",
        "DC_KHONG_XUAT_DUOC": "Chưa xuất được đầy đủ JSON và PDF lên kho Core. Anh thử lại lượt xuất báo cáo.",
    }[ma])


def _kiem_diem(s, kiem=lambda: None):
    """Giữ sàn DC-5; ngoại lệ nhiễu chỉ từ snapshot DC-7 đã ghim."""
    restored = deepcopy(s)
    rows = {r["ma_diem"]: r for r in (s.get("lech_dau") or {}).get("ket_qua", [])}
    for d in restored["diem_lech"]:
        kiem()
        if d["muc"] == "nhieu_ocr" and d["muc_san"] == "can_xem":
            r = rows.get(d["ma_diem"], {})
            if (d["nhom"] != "chi_lech_dau" or d["quy_tac_trung"] or d["vung_bao_ve"] or
                    r.get("muc") != "nhieu_ocr" or not (
                        r.get("tu_dien") == "vo_nghia_co_can_cu" and r.get("can_cu_vo_nghia") or
                        r.get("tu_dien") == "ca_hai_co_nghia" and r.get("ai_dat") is True and r.get("ocr_lai_dat") is True)):
                loi("DC_SAI_NGUON")
            d["muc"] = "can_xem"
        for ben in ("word", "ban_ky"):
            v = d[ben]
            if v is not None:
                a, b = v["bat_dau"], v["ket_thuc"]
                text = s["van_ban"][ben]["van_ban_tai_lieu"]["van_ban"]
                if (type(a) is not int or type(b) is not int or not 0 <= a <= b <= len(text) or
                        text[a:b] != v["nguyen_van"]):
                    loi("DC_SAI_NGUON")
    qt.kiem_bat_bien(restored)
    sc.kiem_tai_dung(s["edit_script"], s["chuan_hoa"], kiem)
    dem = Counter(d["muc"] for d in s["diem_lech"])
    expected = {"so_diem": len(s["diem_lech"]), **{"so_"+k: dem[k] for k in CAC_MUC}}
    vung = s.get("vung_sua_tay")
    expected["so_vung_sua_tay"] = len(vung) if vung is not None else None
    if vung is not None and (not isinstance(vung, list) or len({v["ma"] for v in vung}) != len(vung)):
        loi("DC_SAI_NGUON")
    ld = (s.get("lech_dau") or {}).get("trang", [])
    kem = s.get("trang_ocr_kem")
    if kem is not None and kem != [p for p in ld if p["trang_thai"] == "ocr_kem"]:
        loi("DC_SAI_NGUON")
    expected["so_trang_ocr_kem"] = (len(kem) if kem is not None and ld and
        all(p["trang_thai"] != "chua_kiem" for p in ld) else None)
    if any(s["tom_tat"][k] != v or type(s["tom_tat"][k]) is not type(v) for k, v in expected.items()):
        loi("DC_SAI_NGUON")


def doc_ho_so(viec, ngan, cau_hinh):
    """Băm không thay quyền; chỉ nhận phong bì do engine chốt trong Ngăn."""
    try:
        hs.kiem_schema(viec.dau_vao, hs._SCHEMA_HS)
        if len(hs.json_bytes(viec.dau_vao)) > 65536:
            hs.loi("DC_QUA_GIOI_HAN")
        p = viec.dau_vao["ho_so_doi_chieu"]
        if p["giai_doan"] not in ("da_so", "da_quet_anh", "da_hau_kiem"):
            loi("DC_HO_SO_CHUA_DU")
        scope = cb.pham_vi(viec)
        cb.da_ghim(ngan, scope["phap_nhan_id"], viec.dau_vao, p["giai_doan"], viec.kiem_huy)
        doc = hs._DocTep(viec, deepcopy(cau_hinh))
        raw = doc.doc({"tep": p["ho_so"], "bam": p["bam_ho_so"]}, min(20, cau_hinh["ho_so_mib"]) * hs.MIB)
        s = hs.doc_json(raw, viec.kiem_huy)
        if hs._phong_bi(s, p["ho_so"], raw) != viec.dau_vao:
            loi("DC_SAI_NGUON")
        hs.kiem_schema(s["cau_hinh"], sc._SCHEMA_CH)
        for k, tr in sc._TRAN.items():
            doc.cau_hinh[k] = min(s["cau_hinh"][k], cau_hinh[k], tr)
        if doc.tong > doc.cau_hinh["tong_byte_tep_con"] or len(raw) > doc.cau_hinh["ho_so_mib"] * hs.MIB:
            hs.loi("DC_QUA_GIOI_HAN")
        if type(s["diem_lech"]) is not list:
            loi("DC_HO_SO_CHUA_DU")
        if len(s["diem_lech"]) > doc.cau_hinh["diem_lech_toi_da"]:
            hs.loi("DC_QUA_GIOI_HAN")
        _kiem_diem(s, viec.kiem_huy)
        if any(qt._MUC[d["muc"]] < qt._MUC[d["muc_san"]] for d in s["diem_lech"]):
            # Dùng đúng validator DC-7: tính lại từ từ điển/OCR và gốc đã ghim,
            # không nhận boolean chứng nhận trong snapshot thay cho bằng chứng.
            from . import lech_dau
            ref = s["ho_so_truoc_dc7"]
            before_raw = doc.doc(ref, doc.cau_hinh["ho_so_mib"] * hs.MIB)
            before = hs.doc_json(before_raw, viec.kiem_huy)
            cb.da_ghim(ngan, scope["phap_nhan_id"], hs._phong_bi(before, ref["tep"], before_raw),
                       before["giai_doan"], viec.kiem_huy)
            lech_dau.kiem_bat_bien(s, before, viec=viec, doc=doc)
        if any(d["cho_phan_loai"] for d in s["diem_lech"]):
            loi("DC_HO_SO_CHUA_DU")
        if s.get("ai") and s["ai"].get("nha_cung_cap") != "local":
            loi("DC_SAI_NGUON")
        for ben in ("word", "ban_ky"):
            doc.doc(s["nguon"][ben], doc.cau_hinh["tep_mib"] * hs.MIB)
            vb = hs.doc_json(doc.doc(s["tham_chieu_van_ban"][ben], doc.cau_hinh["ho_so_mib"] * hs.MIB), viec.kiem_huy)
            hs.kiem_schema(vb, hs._SCHEMA_VB)
            if (vb != s["van_ban"][ben] or vb["van_ban_tai_lieu"]["bam_dau_vao"].lower() != s["nguon"][ben]["bam"].lower() or
                    vb["van_ban_tai_lieu"]["van_ban"] != s["chuan_hoa"][ben]["nguyen_van"]):
                loi("DC_SAI_NGUON")
        bo = s["bo_quy_tac"]
        if hs.doc_json(doc.doc(bo, 65536), viec.kiem_huy) != bo["noi_dung"]:
            loi("DC_SAI_NGUON")
        refs = [*s["anh_trang"], *s.get("anh_trang_word", []), *s["bang_chung_ocr_lai"]]
        for k in ("ban_chuan_phan_trang", "ho_so_truoc", "ho_so_truoc_dc7"):
            if s.get(k) is not None:
                refs.append(s[k])
        for v in s.get("vung_sua_tay") or []:
            if v["muc"] != "nghiem_trong" or v["muc_san"] != "nghiem_trong":
                loi("DC_SAI_NGUON")
            refs.append({"tep": v["anh_cat"], "bam": v["bam_anh_cat"]})
        if len(s.get("vung_sua_tay") or []) > doc.cau_hinh["diem_lech_toi_da"]:
            hs.loi("DC_QUA_GIOI_HAN")
        for row in (s.get("lech_dau") or {}).get("ket_qua", []):
            if row.get("anh_cat"):
                refs.append(row["anh_cat"])
        for ref in refs:
            viec.kiem_huy()
            doc.doc(ref, doc.cau_hinh["tep_mib"] * hs.MIB)
        return s, doc
    except LoiNghiepVu as exc:
        if exc.ma in ("DC_HO_SO_CHUA_DU", "DC_QUA_GIOI_HAN"):
            raise
        loi("DC_SAI_NGUON")
    except (KeyError, TypeError, ValueError, OverflowError):
        loi("DC_SAI_NGUON")


def tong_hop(s):
    """Hàm thuần: thiếu kiểm thắng nhãn kết luận nhưng không che điểm đã biết."""
    if any(d.get("cho_phan_loai") is not False for d in s["diem_lech"]):
        loi("DC_HO_SO_CHUA_DU")
    out = deepcopy(s)
    dem = Counter(d["muc"] for d in s["diem_lech"])
    if not set(dem) <= set(CAC_MUC):
        loi("DC_SAI_NGUON")
    vung, kem = s.get("vung_sua_tay"), s.get("trang_ocr_kem")
    pages = s["van_ban"]["ban_ky"]["van_ban_tai_lieu"]
    n = pages["so_trang"]
    thieu = [k for k in hs._KIEM if s["kiem_tra"].get(k) != "dat"]
    # AI không cần khi toàn bộ điểm do quy tắc cứng/hình thức Python xử lý.
    if (s["kiem_tra"].get("phan_loai_ai") in ("chua_kiem", "khong_ap_dung") and s.get("ai") is None and
            all(d["muc"] == "nghiem_trong" or d["muc_san"] == "hinh_thuc" for d in s["diem_lech"])):
        thieu.remove("phan_loai_ai")
    if (not s.get("kiem_dau_vao", {}).get("ocr_day_du") or n < 1 or
            [p["so"] for p in pages["trang"]] != list(range(1, n + 1)) or
            [p["so"] for p in s["anh_trang"]] != list(range(1, n + 1))):
        thieu.append("nguon_trang_ocr")
    quet = s.get("quet_anh") or {}
    if (vung is None or quet.get("du_dieu_kien_ket_luan_sach") is not True or
            not quet.get("so_do_chat_luong_ho_so") or
            [p["so_trang"] for p in quet.get("trang", [])] != list(range(1, n + 1)) or
            not all(p.get("da_quet_toan_trang") is True for p in quet.get("trang", []))):
        thieu.append("do_chat_luong_sua_tay")
    ld = (s.get("lech_dau") or {}).get("trang", [])
    du_ocr = (n > 0 and [p["so"] for p in ld] == list(range(1, n + 1)) and
              all(p.get("trang_thai") in ("ocr_kem", "khong_vuot_nguong") for p in ld))
    if not du_ocr or kem is None:
        thieu.append("do_chat_luong_ocr")
    if (s.get("kiem_trang") or {}).get("trang_thai") != "dat":
        thieu.append("kiem_trang_vat_ly")
    for k in ("vung_bao_ve", "so_va_ngay", "tien_bang_chu"):
        if (s.get("kiem_quy_tac") or {}).get(k, {}).get("da_kiem_du") is not True:
            thieu.append("quy_tac_" + k)
    thieu = list(dict.fromkeys(thieu))
    du = not thieu
    so_kem = len(kem) if kem is not None and (du_ocr or kem) else None
    out["tom_tat"] = {"so_diem": len(s["diem_lech"]), **{"so_" + k: dem[k] for k in CAC_MUC},
        "so_vung_sua_tay": len(vung) if vung is not None else None, "so_trang_ocr_kem": so_kem}
    nghiem = dem["nghiem_trong"] > 0 or bool(vung)
    ket_luan = ("chua_doi_chieu_duoc" if not du else "lech_nghiem_trong" if nghiem else
                "can_xem" if dem["can_xem"] or so_kem else
                "khop_co_thay_doi_hinh_thuc" if dem["hinh_thuc"] or dem["nhieu_ocr"] else "khop")
    out.update(giai_doan="da_tong_hop", ket_luan=ket_luan, da_kiem_du=du, de_nghi_chan=not du or nghiem,
               tong_hop={"phien_ban": PHIEN_BAN, "phan_chua_kiem": thieu,
                         "pham_vi_so_dem": "Các điểm đã biết; giá trị null là hạng mục chưa đo đủ.",
                         "xac_nhan": "Chưa có dữ liệu xác nhận tin cậy từ Core.",
                         "hieu_luc": "Core/module quyết định hiệu lực thực tế."})
    return out


def xuat_ket_qua(viec, ngan, cau_hinh, *, phien_ban_engine):
    from . import bao_cao
    viec = sc._ViecCoHan(viec, 180)
    viec.tien_do(5, "Đang kiểm nguồn hồ sơ trước khi xuất báo cáo")
    s, doc = doc_ho_so(viec, ngan, cau_hinh)
    out = tong_hop(s)
    pin = viec.dau_vao["ho_so_doi_chieu"]
    out["tong_hop"]["ho_so_dau_vao"] = {"tep": deepcopy(pin["ho_so"]), "bam": pin["bam_ho_so"]}
    scope = cb.pham_vi(viec)
    khoa = {"bam_bo": s["bo_quy_tac"]["bam"], "phien_ban_engine": phien_ban_engine,
            "bam_cap": hs.bam(hs.json_bytes({"buoc": PHIEN_BAN, "pham_vi": scope,
                "ho_so": viec.dau_vao, "gioi_han": doc.cau_hinh, "font": bao_cao.BAM_FONT}))}
    with cb.luot(viec, ngan, khoa, "dang_xuat", "da_xuat") as (cu, chot):
        if cu is not None:
            # Kiểm quyền/tính toàn vẹn cả hai tệp trước khi trả lại kết quả cũ.
            try:
                t = cu["ket_qua"]["truong"]
                raw = doc.doc({"tep": t["tep_json"], "bam": cu["bam_json"]}, doc.cau_hinh["ho_so_mib"] * hs.MIB)
                saved = hs.doc_json(raw, viec.kiem_huy)
                if {k: v for k, v in saved.items() if k != "bao_cao_pdf"} != out:
                    loi("DC_SAI_NGUON")
                pdf = doc.doc(saved["bao_cao_pdf"], doc.cau_hinh["tep_mib"] * hs.MIB)
                if not pdf.startswith(b"%PDF-"):
                    loi("DC_KHONG_XUAT_DUOC")
            except (ViecDaHuy, ChuaRo):
                raise
            except Exception:
                loi("DC_KHONG_XUAT_DUOC")
            return cu["ket_qua"]
        try:
            # Dựng đủ cả hai trước tải, thiếu font/PDF không trả JSON thành công.
            pdf = bao_cao.dung_pdf(out, doc, viec.kiem_huy)
            viec.kiem_huy()
            tep_pdf = viec.tai_tep_ra("doi-chieu.pdf", pdf, "application/pdf")
            hs._tep(tep_pdf, ("application/pdf",), doc.cau_hinh["tep_mib"] * hs.MIB)
            out["bao_cao_pdf"] = {"tep": tep_pdf, "bam": hs.bam(pdf)}
            raw = hs.json_bytes(out)
            if len(raw) > doc.cau_hinh["ho_so_mib"] * hs.MIB:
                hs.loi("DC_QUA_GIOI_HAN")
            viec.kiem_huy()
            tep_json = viec.tai_tep_ra("doi-chieu.json", raw, "application/json")
            hs._tep(tep_json, ("application/json",), doc.cau_hinh["ho_so_mib"] * hs.MIB)
            hs._phong_bi(out, tep_json, raw)  # Kiểm schema/quan hệ snapshot kết quả trước chốt.
            kq = {"loai": "truong", "truong": {"ket_luan": out["ket_luan"],
                **{k: out["tom_tat"][k] for k in TRUONG_DEM}, "da_kiem_du": out["da_kiem_du"],
                "de_nghi_chan": out["de_nghi_chan"], "tep_json": tep_json, "tep_pdf": tep_pdf}}
            chot({"ket_qua": kq, "bam_json": hs.bam(raw)})
        except (ViecDaHuy, ChuaRo):
            raise
        except LoiNghiepVu as exc:
            if exc.ma in ("DC_THIEU_TAI_NGUYEN", "DC_QUA_GIOI_HAN"):
                raise
            loi("DC_KHONG_XUAT_DUOC")
        except Exception:
            loi("DC_KHONG_XUAT_DUOC")
        viec.tien_do(100, "Đã xuất đủ JSON và PDF vào kho Core")
        return kq
