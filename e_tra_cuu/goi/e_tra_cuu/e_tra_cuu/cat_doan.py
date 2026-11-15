"""TC-3: cắt cấu trúc thuần Python; snapshot, quyền và tệp thuộc Core."""

from bisect import bisect_right
from copy import deepcopy
import re

from .kiem_dau_vao import (
    DocNguonCore, bam, danh_sach, doi_tuong, json_chuan, kiem_bam,
    kiem_du_lieu, loi, ma, so,
)
from .vi_tri import dinh_vi, lap_ban_do


BAN_THUAT_TOAN = "tc3-cau-truc-1"
_TRAN_DOC = {"json_chinh_toi_da_byte": 1048576, "tep_toi_da_byte": 20971520,
             "tong_doc_toi_da_byte": 67108864, "ho_so_toi_da_byte": 65536}
_TOM_TAT = ("trang_thai", "so_doan", "so_ung_vien", "tang", "co_can_cu",
            "co_mau_thuan", "can_duyet", "nhan")
_DIEU = re.compile(r"(?:^|(?<=\f))[ \t]*(?P<nhan>Đi(?:ề|e\u0302\u0300)u[ \t]+(?:\d+[a-zđ]?|[ivxlcdm]+))(?=[.:\s]|$)", re.I | re.M)
_KHOAN = re.compile(r"(?:^|(?<=\f))[ \t]*(?P<nhan>Kho(?:ả|a\u0309)n[ \t]+\d+[a-zđ]?|\d+[.)])(?=[.:\s]|$)", re.I | re.M)
_NGAT = re.compile(r"\f|\r?\n|[.!?…][\"'”’)]*(?:[ \t]+|(?=$))")


def _doc_snapshot(viec, cua, phien_ban, kiem_cau_hinh):
    pb = doi_tuong(viec.dau_vao, ("loai", "ho_so_tra_cuu"), ())
    if pb["loai"] != "ho_so_tra_cuu":
        loi()
    h = doi_tuong(pb["ho_so_tra_cuu"], ("phien_ban", "ma_yeu_cau", "tac_vu", "giai_doan",
                     "ho_so", "bam_ho_so", "bam_cau_hinh", "bam_danh_muc", "phien_ban_engine",
                     "tom_tat", "canh_bao"), ())
    if h["tac_vu"] != "cat_doan" or h["giai_doan"] != "da_nhan":
        loi("TC_SAI_GIAI_DOAN")
    if type(h["phien_ban"]) is not int or h["phien_ban"] != 1:
        loi("TC_SAI_NGUON")
    ma(h["ma_yeu_cau"])
    for k in ("bam_ho_so", "bam_cau_hinh"):
        kiem_bam(h[k])
    if h["bam_danh_muc"] is not None:
        kiem_bam(h["bam_danh_muc"])
    if h["phien_ban_engine"] != "e_tra_cuu " + phien_ban:
        loi("TC_SAI_NGUON")
    tt = doi_tuong(h["tom_tat"], _TOM_TAT, ())
    if any(x is not None for x in tt.values()) or h["canh_bao"] != []:
        loi("TC_SAI_NGUON")
    if len(json_chuan(pb)) > _TRAN_DOC["ho_so_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    p = viec.ngu_canh.get("phap_nhan_id")
    if type(p) is not str or not p.strip():
        loi("TC_THIEU_NGU_CANH")
    if cua is None or not callable(getattr(cua, "doc_quyen", None)):
        loi("TC_CHUA_CO_CUA_CORE")
    cap = cua.doc_quyen(viec.id)
    if (type(cap) is not dict or type(cap.get("tep")) is not dict
            or type(cap.get("nguon")) is not dict or type(cap.get("dau_vao")) is not dict
            or type(cap.get("ngu_canh_core")) is not dict
            or type(cap.get("metadata_core")) is not dict):
        loi("TC_CHUA_CO_CUA_CORE")
    if json_chuan(cap["dau_vao"]) != json_chuan(pb):
        loi("TC_SAI_NGUON")
    if cap["ngu_canh_core"].get("phap_nhan_id") != p:
        loi("TC_CHUA_CO_CUA_CORE")
    if cap.get("ma_yeu_cau") != h["ma_yeu_cau"] or cap.get("tac_vu") != h["tac_vu"]:
        loi("TC_SAI_NGUON")
    doc = DocNguonCore(viec, _TRAN_DOC.copy())
    doc.giay_cap = deepcopy(cap)
    s = doc.doc_ref({"tep": h["ho_so"], "bam": h["bam_ho_so"]})
    doi_tuong(s, ("phien_ban", "ma_yeu_cau", "tac_vu", "giai_doan", "ngu_canh_core",
                   "cau_hinh", "nguon", "du_lieu", "ket_qua"), ())
    if (type(s["phien_ban"]) is not int or s["phien_ban"] != 1
            or any(s[k] != h[k] for k in ("ma_yeu_cau", "tac_vu", "giai_doan"))
            or s["ket_qua"] is not None):
        loi("TC_SAI_NGUON")
    if json_chuan(s["ngu_canh_core"]) != json_chuan(cap["ngu_canh_core"]):
        loi("TC_CHUA_CO_CUA_CORE")
    # Kiểm bản cấu hình đã ghim, không đọc lại giá trị ngăn hiện tại giữa chuỗi.
    cau_hinh = kiem_cau_hinh(s["cau_hinh"])
    if (json_chuan(cau_hinh) != json_chuan(s["cau_hinh"])
            or bam(json_chuan(cau_hinh["gia_tri"])) != kiem_bam(h["bam_cau_hinh"])):
        loi("TC_SAI_NGUON")
    doc.tran = cau_hinh["gia_tri"]["ngan_sach"]
    if (h["ho_so"]["kich_thuoc"] > doc.tran["tep_toi_da_byte"]
            or doc.tong_doc > doc.tran["tong_doc_toi_da_byte"]
            or len(json_chuan(pb)) > doc.tran["ho_so_toi_da_byte"]):
        loi("TC_QUA_GIOI_HAN")
    d = deepcopy(doi_tuong(s["du_lieu"], ("tai_lieu", "metadata_core"), ("danh_muc",)))
    tl = doi_tuong(d["tai_lieu"], ("ma_nguon", "phien_ban_nguon", "goc", "van_ban", "van_ban_tai_lieu"), ())
    tl.pop("van_ban_tai_lieu")
    # Mở lại qua cửa Core: kiểm bytes gốc, JSON OCR, phiên bản và băm toàn văn.
    da_kiem = kiem_du_lieu(doc, {"tac_vu": "cat_doan", "du_lieu": d,
                               "ngu_canh_core": s["ngu_canh_core"]})
    if (json_chuan(da_kiem) != json_chuan(s["du_lieu"])
            or json_chuan(s["nguon"]) != json_chuan(list(doc.nguon.values()))
            or json_chuan(da_kiem["metadata_core"]) != json_chuan(cap["metadata_core"])):
        loi("TC_SAI_NGUON")
    dm = da_kiem.get("danh_muc")
    bam_dm = bam(json_chuan(dm)) if dm is not None else None
    if (kiem_bam(h["bam_danh_muc"]) if h["bam_danh_muc"] is not None else None) != bam_dm:
        loi("TC_SAI_NGUON")
    return h, s, doc


def _nhan(vb, vung, huy):
    bang = [v for v in vung if v["loai_khoi"] == "bang"]
    dau_bang = [v["bat_dau"] for v in bang]

    def trong_bang(x):
        i = bisect_right(dau_bang, x) - 1
        return i >= 0 and x < bang[i]["ket_thuc"]

    su_kien = []
    for mau, loai in ((_DIEU, "dieu"), (_KHOAN, "khoan")):
        for i, m in enumerate(mau.finditer(vb)):
            if i % 32 == 0:
                huy()
            if not trong_bang(m.start()):
                su_kien.append((m.start(), loai, m.group("nhan")))
    ds, dieu, khoan, a = [], None, None, 0
    for x, loai, nhan in sorted(su_kien):
        if loai == "khoan" and dieu is None and nhan[0].isdigit():
            continue  # Số tiền/mã hoặc danh sách ngoài Điều không thành Khoản.
        if x > a:
            ds.append({"bat_dau": a, "ket_thuc": x, "dieu": dieu, "khoan": khoan})
        if loai == "dieu":
            dieu, khoan = nhan, None
        else:
            khoan = nhan
        a = x
    if a < len(vb):
        ds.append({"bat_dau": a, "ket_thuc": len(vb), "dieu": dieu, "khoan": khoan})
    return ds


def _chia_chu(vb, a, z, vung, dau_vung, muc_tieu, tran, huy):
    if z - a <= muc_tieu:
        return [(a, z)]
    moc = {a, z}
    for i, m in enumerate(_NGAT.finditer(vb, a, z)):
        if i % 32 == 0:
            huy()
        moc.add(m.end())
    i = max(0, bisect_right(dau_vung, a) - 1)
    while i < len(vung) and vung[i]["bat_dau"] < z:
        if i % 32 == 0:
            huy()
        r = vung[i]
        if a < r["ket_thuc"] < z:
            moc.add(r["ket_thuc"])
        i += 1
    ds = sorted(moc)
    kq = []
    for i, (x, y) in enumerate(zip(ds, ds[1:])):
        if i % 32 == 0:
            huy()
        if y - x > tran:
            loi("TC_KHONG_CAT_DUOC")
        if x < y:
            kq.append((x, y))
    return kq


def _cac_map(cac_vung, ma_nguon):
    ds, a = [], 0
    for x, y, vai_tro in cac_vung:
        ds.append({"doan_bat_dau": a, "doan_ket_thuc": a + y - x,
                   "ma_nguon": ma_nguon, "nguon_bat_dau": x, "nguon_ket_thuc": y,
                   "vai_tro": vai_tro})
        a += y - x
    return ds


def _cat_bang(bang, muc_tieu, tran, huy):
    nhom = bang["nhom_hang"]
    so_tieu_de = len(bang["hang_tieu_de"])
    tieu_de = [n for n in nhom if n["hang_bat_dau"] < so_tieu_de]
    than = [n for n in nhom if n["hang_bat_dau"] >= so_tieu_de]
    do_dai_tieu_de = tieu_de[-1]["ket_thuc"] - bang["bat_dau"] if tieu_de else 0
    if do_dai_tieu_de > tran:
        loi("TC_KHONG_CAT_DUOC")
    ds, dang_gom, do_dai = [], list(tieu_de), do_dai_tieu_de
    co_than, lan_dau = False, True

    def ghi():
        nonlocal dang_gom, do_dai, co_than, lan_dau
        if dang_gom:
            ds.append((lan_dau, dang_gom))
            lan_dau = False
        dang_gom, do_dai, co_than = [], do_dai_tieu_de, False

    for i, n in enumerate(than):
        if i % 32 == 0:
            huy()
        dai = n["ket_thuc"] - n["bat_dau"]
        if co_than and do_dai + dai > muc_tieu:
            ghi()
        if do_dai + dai > tran:
            loi("TC_KHONG_CAT_DUOC")
        dang_gom.append(n)
        do_dai += dai
        co_than = True
    ghi()
    kq = []
    for lan_dau, ns in ds:
        a, z = ns[0]["bat_dau"], ns[-1]["ket_thuc"]
        cac_vung = [(a, z, "noi_dung")]
        cac_o = [(o, "noi_dung") for n in ns for o in n["o"]]
        if not lan_dau and tieu_de:
            cac_vung.insert(0, (bang["bat_dau"], bang["bat_dau"] + do_dai_tieu_de, "ngu_canh_lap"))
            cac_o = [(o, "ngu_canh_lap") for n in tieu_de for o in n["o"]] + cac_o
        kq.append((cac_vung, {"so_hang": bang["so_hang"], "so_cot": bang["so_cot"],
                    "hang_tieu_de": deepcopy(bang["hang_tieu_de"]),
                    "hang_bat_dau": ns[0]["hang_bat_dau"], "hang_ket_thuc": ns[-1]["hang_ket_thuc"],
                    "bat_dau_nguon": bang["bat_dau"], "ket_thuc_nguon": bang["ket_thuc"], "o": cac_o}))
    return kq


def _tao_doan(vb, vung, dau_vung, nhan, dau_nhan, cac_vung, bang, nguon, metadata, huy):
    maps = _cac_map(cac_vung, nguon["ma_nguon"])
    chu = "".join(vb[a:z] for a, z, _ in cac_vung)
    vi_tri, vung_vi_tri = dinh_vi(vung, maps, huy, dau_vung)
    nhan_doan = []
    for a, z, vai_tro in cac_vung:
        i = max(0, bisect_right(dau_nhan, a) - 1)
        while i < len(nhan) and nhan[i]["bat_dau"] < z:
            if i % 32 == 0:
                huy()
            n = nhan[i]
            x, y = max(a, n["bat_dau"]), min(z, n["ket_thuc"])
            if x < y:
                nhan_doan.append({**n, "bat_dau": x, "ket_thuc": y, "vai_tro": vai_tro})
            i += 1
    dieu, khoan = ({n[k] for n in nhan_doan} for k in ("dieu", "khoan"))
    lien_tuc = len(cac_vung) == 1 and cac_vung[0][2] == "noi_dung"
    dinh_danh = {"ban_thuat_toan": BAN_THUAT_TOAN, "nguon": nguon, "vung": cac_vung}
    d = {"ma_doan": "tc-" + bam(json_chuan(dinh_danh))[7:], "ban_thuat_toan": BAN_THUAT_TOAN,
         **nguon, "loai_khoi": "bang" if bang else "doan", "nguyen_van": chu,
         "bat_dau": cac_vung[0][0] if lien_tuc else None,
         "ket_thuc": cac_vung[0][1] if lien_tuc else None,
         "dieu": next(iter(dieu)) if len(dieu) == 1 else None,
         "khoan": next(iter(khoan)) if len(khoan) == 1 else None,
         "nhan_cau_truc": nhan_doan, "map_nguon": maps,
         "metadata_core": deepcopy(metadata), "vi_tri": vi_tri,
         "so_trang": vi_tri["trang"], "hop": vi_tri["hop"], "vung_vi_tri": vung_vi_tri, "bang": None}
    if bang:
        b = {k: v for k, v in bang.items() if k != "o"}
        b["ma_bang"] = "bang-" + bam(json_chuan([nguon, bang["bat_dau_nguon"], bang["ket_thuc_nguon"]]))[7:]
        b["o"] = []
        for i, (o, vai_tro) in enumerate(bang["o"]):
            if i % 32 == 0:
                huy()
            m = next(m for m in maps if m["vai_tro"] == vai_tro)
            x = m["doan_bat_dau"] + o["bat_dau"] - m["nguon_bat_dau"]
            y = x + len(o["van_ban"])
            b["o"].append({**o, "vai_tro": vai_tro, "ma_nguon": nguon["ma_nguon"],
                           "doan_bat_dau": x, "doan_ket_thuc": y})
        d["bang"] = b
    return d


def cat_cau_truc(v, nguon, metadata, cau_hinh, muc_tieu, viec):
    vb, huy = v["van_ban"], viec.kiem_huy
    vung = lap_ban_do(v, huy)
    dau_vung = [r["bat_dau"] for r in vung]
    nhan = _nhan(vb, vung, huy)
    dau_nhan = [n["bat_dau"] for n in nhan]
    tran = cau_hinh["ky_tu_don_vi_toi_da"]
    bang = [r["bang"] for r in vung if r["loai_khoi"] == "bang"]
    # Các ranh Điều/Khoản luôn được xét trước câu/khối/trang.
    moc = sorted({0, len(vb), *(n["bat_dau"] for n in nhan),
                  *(x for b in bang for x in (b["bat_dau"], b["ket_thuc"]))})
    don_vi, j = [], 0
    for i, (a, z) in enumerate(zip(moc, moc[1:])):
        if i % 32 == 0:
            huy()
        while j < len(bang) and bang[j]["ket_thuc"] <= a:
            j += 1
        if j < len(bang) and bang[j]["bat_dau"] <= a < bang[j]["ket_thuc"]:
            don_vi.extend(_cat_bang(bang[j], muc_tieu, tran, huy))
        else:
            don_vi.extend(([(x, y, "noi_dung")], None)
                          for x, y in _chia_chu(vb, a, z, vung, dau_vung, muc_tieu, tran, huy))
    ds, dang_gom, dieu_gom = [], [], None

    def ghi(cac_vung, b=None):
        if not cac_vung:
            return
        if len(ds) >= cau_hinh["so_doan_toi_da"]:
            loi("TC_QUA_GIOI_HAN")
        ds.append(_tao_doan(vb, vung, dau_vung, nhan, dau_nhan, cac_vung, b, nguon, metadata, huy))
        if len(ds) % 32 == 0:
            viec.tien_do(30 + min(50, int(50 * cac_vung[-1][1] / len(vb))), "Đang cắt và kiểm vị trí nguồn.")

    for i, (cac_vung, b) in enumerate(don_vi):
        if i % 32 == 0:
            huy()
        a, z, _ = cac_vung[-1]
        dieu = nhan[max(0, bisect_right(dau_nhan, a) - 1)]["dieu"]
        if b:
            ghi(dang_gom)
            dang_gom = []
            ghi(cac_vung, b)
        else:
            if dang_gom and (dieu != dieu_gom or z - dang_gom[0][0] > muc_tieu):
                ghi(dang_gom)
                dang_gom = []
            if z - a > tran:
                loi("TC_KHONG_CAT_DUOC")
            if dang_gom:
                dang_gom[0] = (dang_gom[0][0], z, "noi_dung")
            else:
                dang_gom = [(a, z, "noi_dung")]
            dieu_gom = dieu
    ghi(dang_gom)
    # Tái dựng theo vùng nội dung, không tính tiêu đề ngữ cảnh lần thứ hai.
    con_tro = 0
    for i, d in enumerate(ds):
        if i % 32 == 0:
            huy()
        if len(d["nguyen_van"]) > tran:
            loi("TC_KHONG_CAT_DUOC")
        for m in d["map_nguon"]:
            x, y = m["nguon_bat_dau"], m["nguon_ket_thuc"]
            if d["nguyen_van"][m["doan_bat_dau"]:m["doan_ket_thuc"]] != vb[x:y]:
                loi("TC_SAI_NGUON")
            if m["vai_tro"] == "noi_dung":
                if x != con_tro:
                    loi("TC_SAI_NGUON")
                con_tro = y
    if con_tro != len(vb) or len({d["ma_doan"] for d in ds}) != len(ds):
        loi("TC_SAI_NGUON")
    return ds


def cat_doan(viec, cua_nguon, phien_ban_engine, kiem_cau_hinh):
    viec.kiem_huy()
    h, s, doc = _doc_snapshot(viec, cua_nguon, phien_ban_engine, kiem_cau_hinh)
    viec.tien_do(20, "Đã kiểm snapshot và quyền nguồn tra cứu.")
    ch = s["cau_hinh"]["gia_tri"]["cat_doan"]
    muc_tieu = viec.tham_so.get("do_dai_muc_tieu", ch["do_dai_muc_tieu"])
    so(muc_tieu, 200, 8000, nguyen=True)
    if muc_tieu > ch["ky_tu_don_vi_toi_da"]:
        loi("TC_QUA_GIOI_HAN")
    tl = s["du_lieu"]["tai_lieu"]
    nguon = {k: doc.nguon[tl["ma_nguon"]][k] for k in ("ma_nguon", "tep_id", "phien_ban_nguon", "bam_goc", "bam_van_ban")}
    ds = cat_cau_truc(tl["van_ban_tai_lieu"]["van_ban_tai_lieu"], nguon,
                     s["du_lieu"]["metadata_core"], ch, muc_tieu, viec)
    s["giai_doan"] = "da_cat_doan"
    s["ket_qua"] = {"doan": ds, "ban_thuat_toan": BAN_THUAT_TOAN, "do_dai_muc_tieu": muc_tieu}
    noi_dung = json_chuan(s)
    if len(noi_dung) > doc.tran["tep_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    ra = deepcopy(h)
    ra.update(giai_doan="da_cat_doan", ho_so=None, bam_ho_so=bam(noi_dung))
    ra["tom_tat"].update(trang_thai="da_cat_doan", so_doan=len(ds))
    if len(json_chuan({"loai": "ho_so_tra_cuu", "ho_so_tra_cuu": ra})) > doc.tran["ho_so_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    viec.tien_do(90, "Đang gửi các đoạn và snapshot lên Core.")
    tep = viec.tai_tep_ra("ho-so-cat-doan.json", noi_dung, "application/json")
    viec.kiem_huy()
    doc.kiem_tep(tep, json=True)
    if tep["ten"] != "ho-so-cat-doan.json" or tep["kich_thuoc"] != len(noi_dung):
        loi("TC_SAI_NGUON")
    ra["ho_so"] = tep
    pb = {"loai": "ho_so_tra_cuu", "ho_so_tra_cuu": ra}
    if len(json_chuan(pb)) > doc.tran["ho_so_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    return pb
