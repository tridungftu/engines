"""DC-8: ứng viên nét gạch/chèn từ pixel, chưa chứng nhận phát hiện sửa tay.

Không nhận danh sách vùng của caller làm kết quả detector. Không gọi OCR/AI.
Ngưỡng hình học dưới đây chỉ đã đo trên DEMO tổng hợp, chưa duyệt vận hành.
"""
from copy import deepcopy
import math
from statistics import median
import time

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from . import ho_so as hs
from .anh import HeToaDo, cat_png, doc_anh, loi_anh
from .vi_tri import _hop, loi

PHUONG_PHAP = "net_de_vung_chu"
PHIEN_BAN = "DC-8.1-thu-nghiem"
THAM_SO = {"muc_xam": 160, "gach_dai_theo_chu": 2.0, "chen_rong_theo_chu": 1.2,
           "chen_cao_min": 0.3, "chen_cao_max": 2.2, "mat_do_min": 0.05, "mat_do_max": 0.7,
           "khoang_cach_dong": 1.5, "run_toi_da": 100000, "tu_toi_da": 20000}
TRAN = {"so_trang_toi_da": 60, "pixel_anh": 20000000, "tep_mib": 20,
        "ho_so_mib": 20, "tong_byte_tep_con": 128 * hs.MIB, "diem_lech_toi_da": 10000}


def _giao(a, b):
    return max(0, min(a[2], b[2])-max(a[0], b[0])) * max(0, min(a[3], b[3])-max(a[1], b[1]))


def _trong(a, b):
    return b[0] <= a[0] < a[2] <= b[2] and b[1] <= a[1] < a[3] <= b[3]


def _tu_trang(page, he, kiem):
    tu, da_co = [], set()
    stack = [(page.get("khoi", []), "khoi")]
    while stack:
        ds, loai = stack.pop()
        if type(ds) is not list:
            loi_anh("DC_CHUA_CO_BO_PHAT_HIEN")
        for nut in ds:
            kiem()
            if type(nut) is not dict:
                loi_anh("DC_CHUA_CO_BO_PHAT_HIEN")
            if "hop" in nut:
                _hop(nut["hop"], page)
            if loai == "tu" and nut.get("van_ban", "").strip():
                if "hop" not in nut:
                    loi_anh("DC_CHUA_CO_BO_PHAT_HIEN")
                key = tuple(nut["hop"]), nut["van_ban"]
                if key not in da_co:
                    da_co.add(key)
                    tu.append({"hop": deepcopy(nut["hop"]), "hop_px": he.hop_thang(nut["hop"]),
                               "van_ban": nut["van_ban"]})
                if len(tu) > THAM_SO["tu_toi_da"]:
                    loi_anh("DC_QUA_GIOI_HAN")
            for key in ("khoi", "dong", "tu", "o"):
                if key in nut:
                    stack.append((nut[key], key))
    if not tu:
        loi_anh("DC_CHUA_CO_BO_PHAT_HIEN")
    return tu


class BoPhatHienNet:
    """Run pixel + thành phần liên thông 8 lân cận, dùng hình học từ OCR.

    Không dùng sắc mực. Nét ngoài OCR chỉ thành ứng viên khi đạt hình học
    nét liên tục biến thiên và nằm gần dòng chữ; vẫn có thể là dấu/ký hiệu.
    """
    phuong_phap, phien_ban = PHUONG_PHAP, PHIEN_BAN
    da_do_demo = True

    def quet(self, im, tu, kiem):
        kiem()
        cao = median(t["hop_px"][3]-t["hop_px"][1] for t in tu)
        if cao < 3:
            loi_anh("DC_CHUA_CO_BO_PHAT_HIEN")
        # Chỉ mục dải ngang; có trần thao tác cho OCR có hộp bất thường.
        dai, chi_phi = {}, 0
        for t in tu:
            kiem()
            b = t["hop_px"]
            for k in range(max(0, int(b[1]//cao)-2), int(b[3]//cao)+3):
                dai.setdefault(k, []).append(t)
                chi_phi += 1
                if chi_phi > 200000:
                    loi_anh("DC_QUA_GIOI_HAN")
        with im.convert("L") as gray, gray.point(lambda p: 1 if p < THAM_SO["muc_xam"] else 0) as mask:
            pixels = mask.tobytes()
        cha, hop, dien_tich, lech, gach = [], [], [], [], []

        def goc(i):
            while cha[i] != i:
                cha[i] = cha[cha[i]]
                i = cha[i]
            return i

        def noi(i, j):
            i, j = goc(i), goc(j)
            if i != j:
                if i > j:
                    i, j = j, i
                cha[j] = i
                hop[i] = [min(hop[i][0], hop[j][0]), min(hop[i][1], hop[j][1]),
                          max(hop[i][2], hop[j][2]), max(hop[i][3], hop[j][3])]
                dien_tich[i] += dien_tich[j]
                lech[i] = [min(lech[i][0], lech[j][0]), max(lech[i][1], lech[j][1])]

        truoc, gach_dang = [], []
        for y in range(im.height):
            if y % 16 == 0:
                kiem()
            row, x, nay, j = pixels[y*im.width:(y+1)*im.width], 0, [], 0
            gach_dang = [i for i in gach_dang if gach[i][3] >= y-2]
            while x < im.width:
                a = row.find(b"\x01", x)
                if a < 0:
                    break
                b = row.find(b"\x00", a)
                b = im.width if b < 0 else b
                i, x = len(cha), b
                if i >= THAM_SO["run_toi_da"]:
                    loi_anh("DC_QUA_GIOI_HAN")
                cha.append(i)
                hop.append([a, y, b, y+1])
                dien_tich.append(b-a)
                lech.append([a, a])
                while j < len(truoc) and truoc[j][1] < a:
                    j += 1
                k = j
                while k < len(truoc) and truoc[k][0] <= b:
                    noi(i, truoc[k][2])
                    k += 1
                nay.append((a, b, i))
                if b-a >= cao*THAM_SO["gach_dai_theo_chu"]:
                    hits = [t for t in dai.get(int(y//cao), []) if
                            t["hop_px"][1]+0.2*(t["hop_px"][3]-t["hop_px"][1]) <= y <
                            t["hop_px"][3]-0.2*(t["hop_px"][3]-t["hop_px"][1]) and
                            min(b, t["hop_px"][2])-max(a, t["hop_px"][0]) > 0]
                    if len(hits) >= 2 or any(b-a >= 1.2*(t["hop_px"][2]-t["hop_px"][0]) for t in hits):
                        box = [a, y, b, y+1]
                        nhom = next((i for i in gach_dang if a <= gach[i][2]+2 and b >= gach[i][0]-2), None)
                        if nhom is not None:
                            old = gach[nhom]
                            gach[nhom] = [min(a, old[0]), old[1], max(b, old[2]), y+1]
                        else:
                            gach.append(box)
                            gach_dang.append(len(gach)-1)
            truoc = nay
        kiem()
        vung = [{"hop_px": b, "loai": "gach_de", "can_cu": "net_lien_tuc_cat_qua_vung_giua_chu_in"} for b in gach]
        for i, b in enumerate(hop):
            if i % 256 == 0:
                kiem()
            if cha[i] != i:
                continue
            w, h = b[2]-b[0], b[3]-b[1]
            if (not (w >= cao*THAM_SO["chen_rong_theo_chu"] and
                     cao*THAM_SO["chen_cao_min"] <= h <= cao*THAM_SO["chen_cao_max"] and
                     THAM_SO["mat_do_min"] <= dien_tich[i]/(w*h) <= THAM_SO["mat_do_max"]) or
                    lech[i][1]-lech[i][0] < cao*0.4):
                continue
            near = {id(t): t for k in range(max(0, int(b[1]//cao)-2), int(b[3]//cao)+3) for t in dai.get(k, [])}.values()
            near = list(near)
            che_chu = sum(_giao(b, t["hop_px"]) for t in near)
            if che_chu > w*h*0.4 or any(_giao(b, g) for g in gach):
                continue
            if any(max(t["hop_px"][0]-b[2], b[0]-t["hop_px"][2], 0) <= cao*2 and
                   max(t["hop_px"][1]-b[3], b[1]-t["hop_px"][3], 0) <= cao*THAM_SO["khoang_cach_dong"] for t in near):
                vung.append({"hop_px": b, "loai": "net_chen_gan_chu", "can_cu": "net_lien_thong_bien_thien_gan_dong_chu"})
        kiem()
        return {"pham_vi_px": [0, 0, im.width, im.height], "da_quet_toan_trang": True,
                "so_pixel_da_quet": im.width*im.height, "vung": vung}


def chon_detector(cau_hinh):
    if (cau_hinh.get("phuong_phap_detector") != PHUONG_PHAP or
            cau_hinh.get("phien_ban_detector") != PHIEN_BAN):
        loi_anh("DC_CHUA_CO_BO_PHAT_HIEN")
    return BoPhatHienNet()


class _ViecCoHan:
    def __init__(self, viec, giay):
        self.viec, self.han = viec, time.perf_counter()+min(giay, 900)

    def __getattr__(self, ten):
        return getattr(self.viec, ten)

    def kiem_huy(self):
        self.viec.kiem_huy()
        if time.perf_counter() >= self.han:
            loi_anh("DC_QUA_GIOI_HAN")


def _doc_snapshot(viec, cau_hinh):
    hs.kiem_schema(viec.dau_vao, hs._SCHEMA_HS)
    if len(hs.json_bytes(viec.dau_vao)) > 65536:
        loi_anh("DC_QUA_GIOI_HAN")
    pin = viec.dau_vao["ho_so_doi_chieu"]
    if pin["giai_doan"] not in ("da_nhan", "da_so"):
        loi("DC_SAI_DAU_VAO")
    doc = hs._DocTep(viec, cau_hinh)
    raw = doc.doc({"tep": pin["ho_so"], "bam": pin["bam_ho_so"]}, cau_hinh["ho_so_mib"]*hs.MIB)
    s = hs.doc_json(raw, viec.kiem_huy)
    if (hs._phong_bi(s, pin["ho_so"], raw) != viec.dau_vao or s.get("quet_anh") is not None or
            s.get("vung_sua_tay") is not None or s["kiem_tra"]["sua_tay"] != "chua_kiem" or
            s["ket_luan"] is not None or s["da_kiem_du"] or not s["de_nghi_chan"]):
        loi()
    effective = deepcopy(cau_hinh)
    for k, tr in TRAN.items():
        v = s.get("cau_hinh", {}).get(k)
        if type(v) is not int or not 1 <= v <= tr:
            loi()
        effective[k] = min(v, cau_hinh[k], tr)
    doc.cau_hinh = effective
    if len(raw) > min(effective["tong_byte_tep_con"], effective["ho_so_mib"]*hs.MIB):
        loi_anh("DC_QUA_GIOI_HAN")
    for k in ("phuong_phap_detector", "phien_ban_detector"):
        if s["cau_hinh"].get(k) != cau_hinh.get(k):
            loi_anh("DC_CHUA_CO_BO_PHAT_HIEN")
    for ben, ref in s["tham_chieu_van_ban"].items():
        vb = hs.doc_json(doc.doc(ref, effective["ho_so_mib"]*hs.MIB), viec.kiem_huy)
        hs.kiem_schema(vb, hs._SCHEMA_VB)
        if vb != s["van_ban"][ben] or hs._bam(vb["van_ban_tai_lieu"]["bam_dau_vao"]) != hs._bam(s["nguon"][ben]["bam"]):
            loi()
    for ref in s["nguon"].values():
        doc.doc(ref, effective["tep_mib"]*hs.MIB)
    bo = s["bo_quy_tac"]
    if hs.doc_json(doc.doc(bo, 65536), viec.kiem_huy) != bo["noi_dung"] or hs._bam(bo["bam"]) != pin["bam_bo_quy_tac"].lower():
        loi()
    refs_khac = [*s.get("anh_trang_word", []), *s.get("bang_chung_ocr_lai", [])]
    for key in ("ban_chuan_phan_trang", "ho_so_truoc"):
        if s.get(key) is not None:
            refs_khac.append(s[key])
    for ref in refs_khac:
        doc.doc(ref, effective["tep_mib"]*hs.MIB)
    return s, doc, effective


def _metadata(viec, s, pixel_toi_da):
    core = viec.ngu_canh.get("doi_chieu_anh")
    if core is None:
        loi_anh()
    if len(hs.json_bytes(core)) > 65536:
        loi_anh("DC_QUA_GIOI_HAN")
    pin = viec.dau_vao["ho_so_doi_chieu"]
    if (type(core) is not dict or core.get("phien_ban") != 1 or core.get("ma_cap") != s["ma_cap"] or
            core.get("bam_ho_so") != pin["bam_ho_so"] or core.get("bam_ban_ky") != s["nguon"]["ban_ky"]["bam"]):
        loi_anh()
    vb = s["van_ban"]["ban_ky"]["van_ban_tai_lieu"]
    pages, refs, ds = vb["trang"], s.get("anh_trang"), core.get("trang")
    n = vb["so_trang"]
    if n > min(s["cau_hinh"]["so_trang_toi_da"], 60):
        loi_anh("DC_QUA_GIOI_HAN")
    if (not n or type(ds) is not list or type(refs) is not list or len(pages) != n or len(refs) != n or len(ds) != n or
            any(any(type(a) is not dict or type(a.get("so")) is not int for a in li) for li in (pages, refs, ds)) or
            any([a.get("so") for a in li] != list(range(1, n+1)) for li in (pages, refs, ds))):
        loi_anh()
    for a, m in zip(refs, ds):
        if (m.get("bam_anh") != a["bam"] or type(m.get("rong_px")) is not int or
                type(m.get("cao_px")) is not int or min(m["rong_px"], m["cao_px"]) <= 0):
            loi_anh()
        if m["rong_px"]*m["cao_px"] > min(pixel_toi_da, 20000000):
            loi_anh("DC_QUA_GIOI_HAN")
    return pages, refs, ds


def _loai_tru(meta, page, tu, he, kiem=lambda: None):
    ds, kq = meta.get("vung_loai_tru", []), []
    if type(ds) is not list or len(ds) > 100:
        loi_anh("DC_QUA_GIOI_HAN")
    noi_dung, stack = [], list(page.get("khoi", []))
    while stack:
        kiem()
        nut = stack.pop()
        if nut.get("van_ban", "").strip() and "hop" in nut:
            noi_dung.append(nut["hop"])
        for key in ("khoi", "dong", "tu", "o"):
            stack.extend(nut.get(key, []))
    for v in ds:
        kiem()
        if type(v) is not dict or v.get("loai") not in ("chu_ky", "con_dau", "ky_nhay"):
            loi_anh()
        _hop(v.get("hop"), page)
        cc = v.get("can_cu")
        du = (type(cc) is dict and cc.get("nguon") == "core_xac_nhan" and
              cc.get("bam_anh") == meta["bam_anh"] and type(cc.get("ma")) is str and 1 <= len(cc["ma"]) <= 200)
        chong = any(_giao(v["hop"], b) for b in noi_dung)
        kq.append({"loai": v["loai"], "hop": deepcopy(v["hop"]), "du_can_cu": du,
                   "chong_noi_dung": chong, "duoc_loai": du and not chong, "can_xem": not du or chong,
                   "can_cu": {k: cc[k] for k in ("nguon", "ma", "bam_anh")} if du else None,
                   "hop_px": he.hop_thang(v["hop"])})
    return kq


def phat_hien_sua_tay(viec, cau_hinh, *, phien_ban_engine, thoi_han_viec_giay):
    viec = _ViecCoHan(viec, thoi_han_viec_giay)
    viec.kiem_huy()
    if viec.tham_so.get("che_do", "day_du") != "day_du":
        loi("DC_SAI_DAU_VAO")
    s, doc, tran = _doc_snapshot(viec, cau_hinh)
    pages, refs, metadata = _metadata(viec, s, tran["pixel_anh"])
    if len(pages) > tran["so_trang_toi_da"]:
        loi_anh("DC_QUA_GIOI_HAN")
    detector = chon_detector(cau_hinh)
    if (getattr(detector, "da_do_demo", False) is not True or not callable(getattr(detector, "quet", None)) or
            detector.phuong_phap != cau_hinh["phuong_phap_detector"] or detector.phien_ban != cau_hinh["phien_ban_detector"]):
        loi_anh("DC_CHUA_CO_BO_PHAT_HIEN")
    # Kiểm đủ quyền/băm/byte mọi ảnh trước chạy detector và trước tải ảnh ra.
    for ref in refs:
        viec.kiem_huy()
        try:
            hs._ref({k: ref[k] for k in ("tep", "bam")}, ("image/png", "image/jpeg"), tran["tep_mib"]*hs.MIB)
            doc.doc(ref, tran["tep_mib"]*hs.MIB)
        except LoiNghiepVu as exc:
            if exc.ma == "DC_THIEU_NGUON":
                loi_anh()
            raise
    quet, vung, anh_ra, tong_ra = [], [], [], 0
    for page, ref, meta in zip(pages, refs, metadata):
        viec.kiem_huy()
        raw = doc.doc(ref, tran["tep_mib"]*hs.MIB)
        with doc_anh(raw, ref["tep"]["mime"], tran["pixel_anh"], viec.kiem_huy) as im:
            he = HeToaDo.tu_core(page, meta, im.size)
            tu = _tu_trang(page, he, viec.kiem_huy)
            loai_tru = _loai_tru(meta, page, tu, he, viec.kiem_huy)
            with im.rotate(he.xoay, expand=True) as thang:
                kq = detector.quet(thang, tu, viec.kiem_huy)
                if (type(kq) is not dict or kq.get("da_quet_toan_trang") is not True or
                        kq.get("pham_vi_px") != [0, 0, thang.width, thang.height] or
                        kq.get("so_pixel_da_quet") != thang.width*thang.height or type(kq.get("vung")) is not list):
                    loi_anh("DC_CHUA_CO_BO_PHAT_HIEN")
                if len(kq["vung"])+len(vung) > tran["diem_lech_toi_da"]:
                    loi_anh("DC_QUA_GIOI_HAN")
                for v in kq["vung"]:
                    if type(v) is not dict or v.get("loai") not in ("gach_de", "net_chen_gan_chu"):
                        loi_anh("DC_CHUA_CO_BO_PHAT_HIEN")
                    _hop(v.get("hop_px"), {"rong": thang.width, "cao": thang.height})
                # Cảnh báo vùng chưa thể loại trừ được ghi riêng nguồn, không
                # tính là detector phát hiện và không thay việc quét pixel.
                can_xem_meta = [{"loai": "vung_chu_ky_dau_can_xem", "hop_px": l["hop_px"]}
                               for l in loai_tru if l["can_xem"] and
                               not any(_giao(l["hop_px"], v["hop_px"]) for v in kq["vung"])]
                so_loai = 0
                ung_vien = kq["vung"]+can_xem_meta
                if len(ung_vien)+len(vung) > tran["diem_lech_toi_da"]:
                    loi_anh("DC_QUA_GIOI_HAN")
                for v in ung_vien:
                    viec.kiem_huy()
                    b = v.get("hop_px")
                    _hop(b, {"rong": thang.width, "cao": thang.height})
                    if any(l["duoc_loai"] and _trong(b, l["hop_px"]) for l in loai_tru):
                        so_loai += 1
                        continue
                    chu = [{"van_ban": t["van_ban"], "hop": deepcopy(t["hop"]), "nguon": "ocr_giao_net_gach"}
                           for t in tu if v["loai"] == "gach_de" and _giao(b, t["hop_px"])]
                    hop_nguon, hop_anh = he.hop_nguon(b), he.hop_anh(b)
                    pad = median(t["hop_px"][3]-t["hop_px"][1] for t in tu)
                    hop_cat = [max(0, hop_anh[0]-pad), max(0, hop_anh[1]-pad),
                               min(im.width, hop_anh[2]+pad), min(im.height, hop_anh[3]+pad)]
                    cut, box = cat_png(im, hop_cat, viec.kiem_huy)
                    tong_ra += len(cut)
                    if len(cut) > tran["tep_mib"]*hs.MIB or tong_ra > tran["tong_byte_tep_con"]:
                        loi_anh("DC_QUA_GIOI_HAN")
                    can_xem = any(not l["duoc_loai"] and _giao(b, l["hop_px"]) for l in loai_tru)
                    ma = "ST-"+hs.bam(hs.json_bytes({"so_trang": page["so"], "bam_anh": ref["bam"], "hop": hop_nguon,
                            "loai": v["loai"], "phien_ban": detector.phien_ban}))[7:31]
                    vung.append({"ma": ma, "so_trang": page["so"], "hop": hop_nguon, "don_vi": page["don_vi"],
                                 "hop_anh_px": hop_anh, "hop_cat_anh_px": box, "bam_anh_nguon": ref["bam"], "loai": v["loai"],
                                 "phuong_phap": detector.phuong_phap, "phien_ban": detector.phien_ban,
                                 "nguon_ung_vien": "metadata_can_xem" if v["loai"] == "vung_chu_ky_dau_can_xem" else "detector_pixel",
                                 "can_cu": {"gach_de": "Có nét cắt vùng chữ in.",
                                            "net_chen_gan_chu": "Có nét liên tục biến thiên gần dòng chữ.",
                                            "vung_chu_ky_dau_can_xem": "Vùng chữ ký hoặc dấu chưa đủ căn cứ loại trừ; Anh cần xem ảnh."}[v["loai"]],
                                 "chu_in_bi_de": chu or None, "chu_tay": None, "can_xem": True,
                                 "vung_loai_tru_chua_du_can_cu": can_xem, "muc_san": "nghiem_trong",
                                 "muc": "nghiem_trong", "bat_buoc_xac_nhan": True, "bam_anh_cat": hs.bam(cut)})
                    anh_ra.append(cut)
            quet.append({"so_trang": page["so"], "bam_anh": ref["bam"], "phuong_phap": detector.phuong_phap,
                         "phien_ban": detector.phien_ban, "so_pixel_da_quet": im.width*im.height,
                         "pham_vi_anh_px": [0, 0, im.width, im.height], "da_quet_toan_trang": True,
                         "he_toa_do": {k: deepcopy(meta[k]) for k in ("he_toa_do", "ti_le", "xoay", "rong_px", "cao_px", "rong_nguon", "cao_nguon", "don_vi")},
                         "vung_loai_tru": loai_tru, "so_ung_vien_pixel": len(kq["vung"]),
                         "so_vung_can_xem_tu_metadata": len(can_xem_meta), "so_ung_vien_loai": so_loai})
        viec.tien_do(10+int(65*page["so"]/len(pages)), "Đang quét ảnh và giữ các vùng cần xem")
    # Chỉ sau khi mọi trang hoàn tất mới tải crop; không có tệp tạm trên đĩa.
    for v, raw in zip(vung, anh_ra):
        viec.kiem_huy()
        v["anh_cat"] = viec.tai_tep_ra("vung-"+v["ma"]+".png", raw, "image/png")
    pin = viec.dau_vao["ho_so_doi_chieu"]
    s.update(giai_doan="da_quet_anh", phien_ban_engine=phien_ban_engine,
             ho_so_truoc={"tep": deepcopy(pin["ho_so"]), "bam": pin["bam_ho_so"]}, vung_sua_tay=vung,
             quet_anh={"trang": quet, "phuong_phap": detector.phuong_phap, "phien_ban": detector.phien_ban,
                       "bam_tham_so": hs.bam(hs.json_bytes(THAM_SO)), "tham_so": deepcopy(THAM_SO),
                       "bam_cau_hinh": hs.bam(hs.json_bytes(cau_hinh)), "bam_metadata_core": hs.bam(hs.json_bytes(metadata)),
                       "pham_vi": "ung_vien_thu_nghiem", "da_do_demo": True,
                       "du_dieu_kien_ket_luan_sach": False, "so_do_chat_luong_ho_so": None},
             da_kiem_du=False, ket_luan=None, de_nghi_chan=True)
    s["tom_tat"]["so_vung_sua_tay"] = len(vung)
    # Quét đủ pixel không chứng minh đủ recall; chưa đo DC-13, chưa bỏ chặn.
    s["kiem_tra"]["sua_tay"] = "chua_kiem"
    cb = "Đã quét ảnh bằng phương pháp thử nghiệm trên DEMO; chưa đủ căn cứ kết luận không có sửa tay. Các vùng nghi ngờ phải được xác nhận."
    if cb not in s["canh_bao"]:
        s["canh_bao"].append(cb)
    raw = hs.json_bytes(s)
    if len(raw) > tran["ho_so_mib"]*hs.MIB:
        loi_anh("DC_QUA_GIOI_HAN")
    viec.kiem_huy()
    tep = viec.tai_tep_ra("ho-so-da-quet-anh.json", raw, "application/json")
    pb = hs._phong_bi(s, tep, raw)
    viec.tien_do(100, "Đã giữ ảnh vùng nghi ngờ tại Core; hồ sơ vẫn cần kiểm tra")
    viec.kiem_huy()
    return pb
