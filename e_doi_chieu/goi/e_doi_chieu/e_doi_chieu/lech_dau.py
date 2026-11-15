"""DC-7: kiểm lệch dấu, bằng chứng OCR vùng do Core điều phối và tỷ lệ trang.

Không gọi OCR/AI. Ngữ cảnh doi_chieu_ocr_vung là adapter C-DC-05 đề nghị,
chưa có trong SDK 2.0: vắng nó luôn giữ Cần xem cho cặp có nghĩa.
"""
from collections import Counter
from copy import deepcopy
import math

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from . import ho_so as hs
from . import quy_tac as qt
from . import so_chu as sc
from . import chuan_bi_ai as cb
from . import tu_dien as td
from .vi_tri import _hop, kiem_anh, loi

PHIEN_BAN = "DC-7-1"


def _chi_lech(s, kiem):
    """Nguồn duy nhất là edit script đã tái dựng, không tin nhãn tự khai."""
    sc.kiem_tai_dung(s["edit_script"], s["chuan_hoa"], kiem)
    points = {d["ma_diem"]: d for d in s["diem_lech"]}
    kq = set()
    for op in s["edit_script"]:
        kiem()
        ma = op["ma_diem"]
        if ma is None:
            continue
        d = points.get(ma)
        if d is None or any(op[k] != d[k] for k in ("word", "ban_ky", "phep")):
            loi()
        a, b = (op[k]["chuan_hoa"]["van_ban"] for k in ("word", "ban_ky"))
        if a and b and a != b and sc.bo_dau(a) == sc.bo_dau(b):
            if d["nhom"] != "chi_lech_dau":
                loi()
            kq.add(ma)
        elif d["nhom"] == "chi_lech_dau":
            loi()
    return kq


def _cum(d, tus):
    kq = {}
    for ben in ("word", "ban_ky"):
        v = d[ben]
        ids = [] if v is None else tus[ben].lay(v["bat_dau"], v["ket_thuc"])
        if not ids:
            return None
        ts = [tus[ben].tu[i] for i in ids]
        kq[ben] = {"bat_dau": ts[0]["bat_dau"], "ket_thuc": ts[-1]["ket_thuc"],
                    "van_ban": " ".join(t["van_ban"] for t in ts), "tu": ts, "chi_so": ids}
    if (len(kq["word"]["tu"]) != len(kq["ban_ky"]["tu"]) or
            sc.bo_dau(td.chuan(kq["word"]["van_ban"])) != sc.bo_dau(td.chuan(kq["ban_ky"]["van_ban"]))):
        return None
    return kq


def _vung(cum, vi_tri):
    if cum is None:
        return None
    ts = cum["ban_ky"]["tu"]
    pages = {t["so_trang"] for t in ts}
    if len(pages) != 1:
        return None
    a, b = cum["ban_ky"]["bat_dau"], cum["ban_ky"]["ket_thuc"]
    ds = [v for v in vi_tri.lay(a, b) if v.get("hop") is not None and v.get("so_trang") in pages
          and v["bat_dau"] <= a < b <= v["ket_thuc"]]
    if not ds:
        return None
    size = min(v["ket_thuc"] - v["bat_dau"] for v in ds)
    ds = [v for v in ds if v["ket_thuc"] - v["bat_dau"] == size]
    if len({(v["so_trang"], tuple(v["hop"]), v.get("don_vi")) for v in ds}) != 1:
        return None
    v = ds[0]
    # Hộp khối lớn hơn cụm vẫn xem/cắt được; không dùng nó để chứng minh OCR từ.
    return {"trang": v["so_trang"], "hop": deepcopy(v["hop"]), "don_vi": v.get("don_vi"),
            "bat_dau": a, "ket_thuc": b, "hop_dung_cum": v["bat_dau"] == a and v["ket_thuc"] == b}


def _nguong(s):
    q = s["bo_quy_tac"]["noi_dung"].get("lech_dau", {})
    if type(q) is not dict:
        loi()
    if q and (type(q.get("phien_ban")) is not int or q["phien_ban"] != 1):
        loi()
    nguong = q.get("nguong_ocr_kem")
    if nguong is None:
        return None
    if (type(nguong) is not dict or set(nguong) != {"ty_le", "phien_ban", "nguon_do"} or
            type(nguong["ty_le"]) not in (int, float) or not math.isfinite(nguong["ty_le"]) or
            not 0 <= nguong["ty_le"] <= 1 or any(type(nguong[k]) is not str or not nguong[k].strip()
                or len(nguong[k]) > 1000 for k in ("phien_ban", "nguon_do"))):
        loi()
    return deepcopy(nguong)


def _trang(s, tus, ids, kiem):
    pages = s["van_ban"]["ban_ky"]["van_ban_tai_lieu"]["trang"]
    rows = {p["so"]: {"so": p["so"], "so_tu_ocr": 0, "tu_lech": set(), "ma_diem": [],
                       "ma_nghiem_trong": [], "ma_nhieu_ocr": []} for p in pages}
    for t in tus.tu:
        kiem()
        rows[t["so_trang"]]["so_tu_ocr"] += 1
    for d in s["diem_lech"]:
        kiem()
        v = d["ban_ky"]
        touched = [] if v is None else tus.lay(v["bat_dau"], v["ket_thuc"])
        by_page = {}
        for i in touched:
            by_page.setdefault(tus.tu[i]["so_trang"], []).append(i)
        # Điểm cấu trúc/trang có thể không mang lát chữ, vẫn giữ riêng mức cứng.
        pos = (v or {}).get("vi_tri") or d.get("can_cu", {}).get("ban_ky") or {}
        no = pos.get("so_trang", pos.get("so")) if type(pos) is dict else None
        if no in rows:
            by_page.setdefault(no, [])
        for so, tokens in by_page.items():
            row = rows[so]
            row["ma_diem"].append(d["ma_diem"])
            if d["ma_diem"] in ids:
                row["tu_lech"].update(tokens)
            if d["muc"] in ("nghiem_trong", "nhieu_ocr"):
                row["ma_" + d["muc"]].append(d["ma_diem"])
    nguong = _nguong(s)
    images = {r["so"]: r for r in s["anh_trang"]}
    for row in rows.values():
        kiem()
        n, den = len(row.pop("tu_lech")), row["so_tu_ocr"]
        row.update(so_tu_lech_dau=n, ty_le=n/den if den else None,
                   phan_so={"tu_so": n, "mau_so": den}, nguong=nguong,
                   anh_trang=deepcopy(images.get(row["so"])), trang_thai="chua_kiem")
        if nguong is not None and den:
            row["trang_thai"] = "ocr_kem" if n > nguong["ty_le"] * den else "khong_vuot_nguong"
    return list(rows.values())


def _ocr_core(viec, s, doc, candidates):
    """Chỉ đọc kết quả nằm trong manifest do Core cấp, không tin JSON caller."""
    core = viec.ngu_canh.get("doi_chieu_ocr_vung")
    if core is None:
        return {}, "chua_co_contract_ocr_vung"
    if len(hs.json_bytes(core)) > 65536:
        loi("DC_QUA_GIOI_HAN")
    hs._khoa(core, ("phien_ban", "ma_cap", "bam_ban_ky", "phien_ban_ban_ky", "ket_qua"))
    if (type(core["phien_ban"]) is not int or core["phien_ban"] != 1 or core["ma_cap"] != s["ma_cap"] or
            core["bam_ban_ky"] != s["nguon"]["ban_ky"]["bam"] or
            core["phien_ban_ban_ky"] != s["nguon"]["ban_ky"]["phien_ban"]):
        loi()
    ds = core["ket_qua"]
    if type(ds) is not list or len(ds) > doc.cau_hinh["diem_lech_toi_da"]:
        loi("DC_QUA_GIOI_HAN")
    refs, kq = set(), {}
    pages = {p["so"]: p for p in s["van_ban"]["ban_ky"]["van_ban_tai_lieu"]["trang"]}
    images = {p["so"]: p for p in s["anh_trang"]}
    for ref in ds:
        viec.kiem_huy()
        hs._khoa(ref, ("tep", "bam", "nguon_doc", "phien_ban_nguon", "nang_luc", "ma_ket_qua"))
        if (ref["nang_luc"] != "ocr.trich_vung@1" or type(ref["ma_ket_qua"]) is not str or
                not 1 <= len(ref["ma_ket_qua"]) <= 200 or not ref["ma_ket_qua"].strip()):
            loi()
        hs._ref({k: ref[k] for k in ("tep", "bam")}, ("application/json",), doc.cau_hinh["ho_so_mib"] * hs.MIB)
        if ref["tep"]["tep_id"] in refs:
            loi()
        refs.add(ref["tep"]["tep_id"])
        try:
            raw = doc.doc(ref, doc.cau_hinh["ho_so_mib"] * hs.MIB)
        except LoiNghiepVu as exc:
            if exc.ma != "DC_THIEU_NGUON":
                raise
            # Kết quả OCR là bằng chứng bổ sung, mất quyền/tệp không làm nó đạt.
            # Không biết mã điểm thì chặn dùng mọi kết quả còn lại của manifest.
            return {}, "thieu_ket_qua_ocr_vung"
        e = hs.doc_json(raw, viec.kiem_huy)
        hs._khoa(e, ("phien_ban", "ma_cap", "ma_diem", "bam_ban_ky", "phien_ban_ban_ky", "trang", "hop",
                     "don_vi", "bat_dau", "ket_thuc", "bam_anh_trang", "nguon_doc", "phien_ban_nguon", "van_ban"),
                     ("anh_cat", "nghi_ngo_abbyy"))
        ma, no = e["ma_diem"], e["trang"]
        if (type(e["phien_ban"]) is not int or e["phien_ban"] != 1 or type(no) is not int or no not in pages or
                type(ma) is not str or ma not in candidates or candidates[ma]["vung"] is None):
            loi()
        v = candidates[ma]["vung"]
        for key in ("ma_cap", "bam_ban_ky", "phien_ban_ban_ky"):
            if e[key] != core[key]:
                loi()
        if (any(e[k] != v[k] or type(e[k]) is not type(v[k]) for k in ("trang", "hop", "don_vi", "bat_dau", "ket_thuc")) or
                e["bam_anh_trang"] != images[no]["bam"] or e["don_vi"] != pages[no]["don_vi"] or
                any(e[k] != ref[k] for k in ("nguon_doc", "phien_ban_nguon"))):
            loi()
        _hop(e["hop"], pages[no])
        if type(e["van_ban"]) is not str or len(e["van_ban"]) > 500000:
            loi()
        source_ok = (e["nguon_doc"] in ("abbyy", "tesseract", "ocr_thu_hai") and
                     type(e["phien_ban_nguon"]) is str and bool(e["phien_ban_nguon"].strip()))
        cut = e.get("anh_cat")
        if cut is not None:
            hs._ref(cut, ("image/png", "image/jpeg"), doc.cau_hinh["tep_mib"] * hs.MIB)
            im = doc.doc(cut, doc.cau_hinh["tep_mib"] * hs.MIB)
            kiem_anh(im, cut["tep"]["mime"], doc.cau_hinh["pixel_anh"], viec.kiem_huy)
        kq.setdefault(ma, []).append({"tep": ref["tep"], "bam": ref["bam"], "noi_dung": e,
            "nang_luc": ref["nang_luc"], "ma_ket_qua": ref["ma_ket_qua"],
            "nguon_dat": source_ok, "khop_word": source_ok and v["hop_dung_cum"] and bool(e["van_ban"].strip()) and
                td.chuan(e["van_ban"]) == td.chuan(candidates[ma]["cum"]["word"]["van_ban"])})
    return kq, "da_nhan_manifest_core"


def _tra_cum(tu_dien, cum):
    if cum is None:
        return "chua_biet", None
    w, o = (cum[k]["van_ban"] for k in ("word", "ban_ky"))
    result, cc = tu_dien.tra(w, o)
    if result != "chua_biet":
        return result, cc
    ds = [tu_dien.tra(a["van_ban"], b["van_ban"]) for a, b in zip(cum["word"]["tu"], cum["ban_ky"]["tu"])
          if td.chuan(a["van_ban"]) != td.chuan(b["van_ban"])]
    if ds and all(t == "vo_nghia_co_can_cu" for t, _ in ds):
        return "vo_nghia_co_can_cu", [cc for _, cc in ds]
    if ds and all(t == "ca_hai_co_nghia" for t, _ in ds):
        return "ca_hai_co_nghia", None
    return "chua_biet", None


def ap_dung(s, viec, doc, *, hau_kiem=False):
    kiem = viec.kiem_huy
    ids = _chi_lech(s, kiem)
    tus = {k: td.CacTu(s["van_ban"][k]["van_ban_tai_lieu"]["van_ban"], kiem) for k in ("word", "ban_ky")}
    vi_tri = qt._ChiMuc(s["chuan_hoa"]["ban_ky"]["vi_tri"])
    candidates = {}
    for d in s["diem_lech"]:
        kiem()
        if d["ma_diem"] in ids:
            cum = _cum(d, tus)
            candidates[d["ma_diem"]] = {"cum": cum, "vung": _vung(cum, vi_tri)}
    eligible = {d["ma_diem"] for d in s["diem_lech"] if d["ma_diem"] in ids and not
                (d["quy_tac_trung"] or d["vung_bao_ve"] or d["muc"] == "nghiem_trong" or d["muc_san"] != "can_xem")}
    tu_dien, meta = (td.doc_tu_dien(s, doc, s["cau_hinh"], kiem) if hau_kiem and eligible else (None, None))
    ocr, contract = _ocr_core(viec, s, doc, candidates) if hau_kiem else ({}, "cho_hau_kiem")
    ai = {r["ma_diem"]: r for r in (s.get("ai") or {}).get("ket_qua", [])}
    rows = []
    for d in s["diem_lech"]:
        kiem()
        ma = d["ma_diem"]
        if ma not in candidates:
            continue
        c = candidates[ma]
        nhan, can_cu = _tra_cum(tu_dien, c["cum"]) if tu_dien is not None and ma in eligible else ("chua_tra", None)
        evidence = ocr.get(ma, [])
        a = ai.get(ma, {})
        ai_ok = (s.get("ai", {}).get("nha_cung_cap") == "local" if s.get("ai") else False) and (
            a.get("trich_dan_dat") is True and a.get("cho_dc7") is True and a.get("nhan") == "nhieu_ocr")
        ocr_ok = bool(evidence) and all(e["khop_word"] for e in evidence)
        muc = d["muc"]
        ly_do = "cho_hau_kiem" if not hau_kiem else "chua_du_can_cu"
        if ma not in eligible:
            ly_do = "giu_quy_tac_cung_hoac_muc_da_nang"
        elif hau_kiem:
            if nhan == "vo_nghia_co_can_cu" or nhan == "ca_hai_co_nghia" and ai_ok and ocr_ok:
                muc, ly_do = "nhieu_ocr", "vo_nghia_co_can_cu" if nhan == "vo_nghia_co_can_cu" else "ai_va_ocr_lai_cung_khop_word"
            else:
                muc = "can_xem"
                ly_do = "tu_la_chua_biet" if nhan == "chua_biet" else "thieu_ai_hoac_ocr_lai_dung_vung"
        d["muc"] = muc
        rows.append({"ma_diem": ma, "muc": muc, "tu_dien": nhan, "can_cu_vo_nghia": can_cu,
            "ly_do": ly_do, "vung": c["vung"], "ai_dat": bool(ai_ok), "ocr_lai_dat": ocr_ok,
            "bang_chung_ocr_lai": evidence, "anh_cat": next((e["noi_dung"]["anh_cat"] for e in evidence if e["noi_dung"].get("anh_cat")), None)})
    pages = _trang(s, tus["ban_ky"], ids, kiem)
    s["lech_dau"] = {"phien_ban": PHIEN_BAN, "hau_kiem": hau_kiem, "tu_dien": meta, "contract_ocr_vung": contract,
        "mau_so": "Token OCR trên nguyên văn từng trang, tách khoảng trắng, bỏ dấu câu ở mép, giữ dấu câu bên trong; mỗi token đếm một lần.",
        "tu_so": "Số token OCR phân biệt giao với edit script chỉ lệch dấu, gồm cả vùng bảo vệ.", "ket_qua": rows, "trang": pages}
    s["trang_ocr_kem"] = [deepcopy(p) for p in pages if p["trang_thai"] == "ocr_kem"]
    du_trang = all(p["trang_thai"] != "chua_kiem" for p in pages)
    s["tom_tat"]["so_trang_ocr_kem"] = len(s["trang_ocr_kem"]) if du_trang else None
    s["kiem_tra"]["lech_dau"] = "dat" if du_trang and (hau_kiem or not eligible) else "chua_kiem"
    counts = Counter(d["muc"] for d in s["diem_lech"])
    s["tom_tat"].update({"so_" + k: counts[k] for k in qt._MUC})
    s.update(da_kiem_du=False, ket_luan=None, de_nghi_chan=True)
    for warning in (["Chưa có ngưỡng trang OCR kém đã đo; chưa đủ căn cứ kết luận trang tốt."] if not du_trang else []):
        if warning not in s["canh_bao"]:
            s["canh_bao"].append(warning)
    if meta and meta["pham_vi"] == "DEMO":
        s["canh_bao"].append("Từ điển chỉ là fixture DEMO; nguồn tiếng Việt có giấy phép vẫn chờ DC-Q14.")
    if hau_kiem and eligible and contract == "chua_co_contract_ocr_vung":
        s["canh_bao"].append("Chưa có contract OCR vùng tin cậy của Core; cặp có nghĩa vẫn cần xem, cờ ABBYY không thay OCR lại.")
    return s


def kiem_bat_bien(out, goc, *, viec=None, doc=None):
    """Sàn/nhật ký DC-5 bất biến; chỉ Python DC-7 phân loại ứng viên tạm.

    Không sửa validator DC-5 hoặc cho AI quyền hạ mức. Gốc phải đọc từ Core.
    Mọi phần hạ phải có chứng nhận DC-7; caller không được tự tạo gốc.
    """
    restored = deepcopy(out)
    old = {d["ma_diem"]: d for d in goc["diem_lech"]}
    rows = {r["ma_diem"]: r for r in out["lech_dau"]["ket_qua"]}
    ref = out.get("ho_so_truoc_dc7")
    if ref is not None and doc is not None:
        if hs.doc_json(doc.doc(ref, doc.cau_hinh["ho_so_mib"] * hs.MIB), doc.viec.kiem_huy) != goc:
            loi()
    da_kiem_lai = False
    for d in restored["diem_lech"]:
        cu = old.get(d["ma_diem"])
        if cu is None:
            loi()
        if qt._MUC[d["muc"]] < qt._MUC[cu["muc"]]:
            # Chứng nhận trong out không tự là nguồn tin cậy. Kiểm lại độc lập
            # từ gốc, từ điển/tệp có quyền và manifest trong ngữ cảnh Core.
            if not da_kiem_lai:
                if viec is None or doc is None:
                    loi()
                expected = ap_dung(deepcopy(goc), viec, doc, hau_kiem=True)
                if ref is not None:
                    expected["ho_so_truoc_dc7"] = ref
                if out != expected:
                    loi()
                da_kiem_lai = True
            r = rows.get(d["ma_diem"], {})
            if (cu["muc"] != "can_xem" or cu["muc_san"] != "can_xem" or cu["quy_tac_trung"] or cu["vung_bao_ve"] or
                    cu["nhom"] != "chi_lech_dau" or d["muc"] != "nhieu_ocr" or r.get("muc") != "nhieu_ocr" or
                    not (r.get("tu_dien") == "vo_nghia_co_can_cu" and r.get("can_cu_vo_nghia") or
                         r.get("tu_dien") == "ca_hai_co_nghia" and r.get("ai_dat") is True and r.get("ocr_lai_dat") is True)):
                loi()
            d["muc"] = cu["muc"]
    qt.kiem_bat_bien(restored, goc)
    return True


def xu_ly_ho_so(viec, ngan, cau_hinh, pb, *, hau_kiem=False):
    """Cổng nội bộ sau so/hậu kiểm; cùng loại hồ sơ, không thêm capability."""
    viec = sc._ViecCoHan(viec, 300)
    scope = cb.pham_vi(viec)
    hs.kiem_schema(pb, hs._SCHEMA_HS)
    p = pb["ho_so_doi_chieu"]
    if not hau_kiem:
        goc, doc, _ = cb.doc_goc(viec, ngan, cau_hinh, pb)
    else:
        doc = hs._DocTep(viec, cau_hinh)
        raw = doc.doc({"tep": p["ho_so"], "bam": p["bam_ho_so"]}, min(20, cau_hinh["ho_so_mib"]) * hs.MIB)
        goc = hs.doc_json(raw, viec.kiem_huy)
        if p["giai_doan"] != "da_hau_kiem" or hs._phong_bi(goc, p["ho_so"], raw) != pb:
            loi()
        cb.da_ghim(ngan, scope["phap_nhan_id"], pb, "da_hau_kiem", viec.kiem_huy)
        # Bản AI ghim cả phạm vi và hồ sơ Python gốc; không nhận bản do caller tự sửa.
        before = hs.doc_json(doc.doc(goc["ho_so_truoc"], cau_hinh["ho_so_mib"] * hs.MIB), viec.kiem_huy)
        if before["ai"]["pham_vi"] != scope:
            loi()
        python, doc, _ = cb.doc_goc(viec, ngan, cau_hinh, before["ai"]["ho_so_goc"], doc)
        qt.kiem_bat_bien(goc, python)
    if len(hs.json_bytes(pb)) > 65536:
        loi("DC_QUA_GIOI_HAN")
    core = viec.ngu_canh.get("doi_chieu_ocr_vung") if hau_kiem else None
    if core is not None and len(hs.json_bytes(core)) > 65536:
        loi("DC_QUA_GIOI_HAN")
    key = {"phap_nhan_id": scope["phap_nhan_id"], "bam_bo": p["bam_bo_quy_tac"], "phien_ban_engine": p["phien_ban_engine"],
           "bam_cap": hs.bam(hs.json_bytes({"buoc": PHIEN_BAN, "pham_vi": scope, "bam_ho_so": p["bam_ho_so"],
               "hau_kiem": hau_kiem, "core": core, "gioi_han": doc.cau_hinh}))}
    ban = ngan.doc("luot_doi_chieu", key)
    if ban is not None and ban.gia_tri["trang_thai"] == p["giai_doan"]:
        cp = ban.gia_tri["phong_bi"]["ho_so_doi_chieu"]
        try:
            doc.doc({"tep": cp["ho_so"], "bam": cp["bam_ho_so"]}, doc.cau_hinh["ho_so_mib"] * hs.MIB)
        except LoiNghiepVu as exc:
            if exc.ma != "DC_THIEU_NGUON":
                raise
            # Chỉ dựng lại từ nguồn đã kiểm quyền, không tái dùng tham chiếu cũ.
            with ngan.lo() as lo:
                lo.sua("luot_doi_chieu", {"phap_nhan_id": scope["phap_nhan_id"], "ma_luot": ban.gia_tri["ma_luot"]},
                       {"trang_thai": "can_thu_lai"}, row_version=ban.row_version)
    with cb.luot(viec, ngan, key, "dang_kiem_lech_dau", p["giai_doan"]) as (cu, chot):
        # Tái tính bằng cùng nguồn tin cậy trước khi tái dùng, không tin chứng nhận tự khai.
        out = ap_dung(deepcopy(goc), viec, doc, hau_kiem=hau_kiem)
        out["ho_so_truoc_dc7"] = {"tep": deepcopy(p["ho_so"]), "bam": p["bam_ho_so"]}
        kiem_bat_bien(out, goc, viec=viec, doc=doc)
        raw = hs.json_bytes(out)
        if len(raw) > min(20, doc.cau_hinh["ho_so_mib"]) * hs.MIB:
            loi("DC_QUA_GIOI_HAN")
        if cu is not None:
            cp = cu["ho_so_doi_chieu"]
            old = doc.doc({"tep": cp["ho_so"], "bam": cp["bam_ho_so"]}, doc.cau_hinh["ho_so_mib"] * hs.MIB)
            if old != raw or hs._phong_bi(out, cp["ho_so"], raw) != cu:
                loi()
            return cu
        viec.tien_do(90, "Đang gửi kiểm lệch dấu và tỷ lệ OCR trang lên Core")
        tep = viec.tai_tep_ra("ho-so-kiem-lech-dau.json", raw, "application/json")
        result = hs._phong_bi(out, tep, raw)
        chot(result)
        viec.kiem_huy()
        return result
