"""Ánh xạ Unicode vào nguồn bất biến; không suy đoán hộp hoặc sửa toàn văn.

Khối chữ không có offset được căn tuần tự trong đúng trang, chỉ được đi qua
khoảng trắng. Bảng dùng offset toàn cục hoặc phép chiếu hàng TAB/NEWLINE khớp
chính xác; không có ánh xạ kiểm được thì từ chối. Không đổi schema chung.
"""

from bisect import bisect_left
from copy import deepcopy

from .kiem_dau_vao import danh_sach, doi_tuong, kiem_hop, loi, so


def _khoang(v, a, z, chu=None):
    if ("bat_dau" in v) != ("ket_thuc" in v):
        loi("TC_SAI_NGUON")
    if "bat_dau" not in v:
        return None
    x, y = v["bat_dau"], v["ket_thuc"]
    if type(x) is not int or type(y) is not int or not a <= x <= y <= z:
        loi("TC_SAI_NGUON")
    if chu is not None and y - x != len(chu):
        loi("TC_SAI_NGUON")
    return x, y


def _hop(hop, trang, khung=None):
    if hop is None:
        return None
    if trang is None:
        loi("TC_SAI_NGUON")
    kiem_hop(hop)
    x0, y0, x1, y1 = khung or (0, 0, trang["rong"], trang["cao"])
    if not x0 <= hop[0] <= hop[2] <= x1 or not y0 <= hop[1] <= hop[3] <= y1:
        loi("TC_SAI_NGUON")
    return deepcopy(hop)


def _chuoi(v, vb, a, z, con_tro):
    chu = v.get("van_ban")
    if type(chu) is not str:
        loi("TC_SAI_NGUON")
    khoang = _khoang(v, a, z, chu)
    if khoang is None:
        # Không chọn một lần xuất hiện ở xa rồi bỏ nội dung đứng trước nó.
        x = vb.find(chu, con_tro, z)
        khoang = (x, x + len(chu))
    x, y = khoang
    if x < con_tro or vb[con_tro:x].strip() or vb[x:y] != chu:
        loi("TC_SAI_NGUON")
    return x, y


def _kiem_dong_tu(khoi, vb, a, z, trang, huy):
    def kiem(ds, x, y, loai):
        con_tro = x
        for i, muc in enumerate(danh_sach(ds)):
            if i % 32 == 0:
                huy()
            doi_tuong(muc, ("van_ban", "hop"))
            u, v = _chuoi(muc, vb, x, y, con_tro)
            _hop(muc["hop"], trang)
            if loai == "dong" and "tu" in muc:
                kiem(muc["tu"], u, v, "tu")
            con_tro = v
        if vb[con_tro:y].strip():
            loi("TC_SAI_NGUON")

    if "dong" in khoi:
        kiem(khoi["dong"], a, z, "dong")


def _kiem_luoi(cac_o, huy):
    """Kiểm ô gộp/ô trống bằng sweep, không bung lưới theo kích thước tự khai."""
    if not cac_o:
        loi("TC_SAI_NGUON")
    su_kien, dien_tich = [], 0
    so_hang = max(o["hang"] + o["gop_hang"] for o in cac_o)
    so_cot = max(o["cot"] + o["gop_cot"] for o in cac_o)
    for i, o in enumerate(cac_o):
        su_kien.extend(((o["hang"], 1, i), (o["hang"] + o["gop_hang"], 0, i)))
        dien_tich += o["gop_hang"] * o["gop_cot"]
    dang_mo = []
    for dem, (_, them, i) in enumerate(sorted(su_kien)):
        if dem % 32 == 0:
            huy()
        o = cac_o[i]
        khoa = (o["cot"], o["cot"] + o["gop_cot"], i)
        cho = bisect_left(dang_mo, khoa)
        if them:
            if ((cho and dang_mo[cho - 1][1] > khoa[0])
                    or (cho < len(dang_mo) and dang_mo[cho][0] < khoa[1])):
                loi("TC_SAI_NGUON")
            dang_mo.insert(cho, khoa)
        else:
            if cho >= len(dang_mo) or dang_mo[cho] != khoa:
                loi("TC_SAI_NGUON")
            dang_mo.pop(cho)
    if dien_tich != so_hang * so_cot:
        # Một ô rỗng vẫn phải có bản ghi; không tự chèn ô còn thiếu.
        loi("TC_SAI_NGUON")
    return so_hang, so_cot


def _map_bang(khoi, vb, a, z, con_tro, huy):
    """Chỉ suy map ô khi phép chiếu xác định khớp toàn bộ vùng bảng.

    Giữ chỉ các ô gốc của ô gộp, nối ô cùng hàng bằng TAB, các hàng bằng LF
    hoặc CRLF. Kiểu chiếu khác cần offset tường minh từ adapter Core.
    """
    cac_o = danh_sach(khoi.get("o"))
    if _khoang(khoi, a, z) is not None and all("bat_dau" in o and "ket_thuc" in o for o in cac_o):
        return khoi
    for i, o in enumerate(cac_o):
        if i % 32 == 0:
            huy()
        doi_tuong(o, ("hang", "cot", "gop_hang", "gop_cot", "van_ban"))
        for k in ("hang", "cot", "gop_hang", "gop_cot"):
            so(o[k], 1 if k.startswith("gop_") else 0, nguyen=True)
        if type(o["van_ban"]) is not str:
            loi("TC_SAI_NGUON")
    if not cac_o:
        loi("TC_SAI_NGUON")
    cac_o = sorted(cac_o, key=lambda o: (o["hang"], o["cot"]))
    # Hàng không có ô gốc được biểu diễn bằng dòng rỗng; không bung một số
    # hàng tự khai vượt sức chứa chính văn bản đang đối chiếu.
    so_hang = max(o["hang"] + o["gop_hang"] for o in cac_o)
    if so_hang > len(vb) + 1:
        loi("TC_SAI_NGUON")
    khoang = _khoang(khoi, a, z)
    if khoang is not None:
        x, y = khoang
        if x < con_tro:
            loi("TC_SAI_NGUON")
    elif "van_ban" in khoi:
        x, y = _chuoi(khoi, vb, a, z, con_tro)
    else:
        x = y = None
    for xuong_dong in ("\n", "\r\n"):
        phan, vi_tri, dai, hang, cot = [], [], 0, 0, 0
        for i, o in enumerate(cac_o):
            if i % 32 == 0:
                huy()
            if o["hang"] > hang:
                p = xuong_dong * (o["hang"] - hang)
                phan.append(p); dai += len(p); cot = 0
            if cot:
                phan.append("\t"); dai += 1
            vi_tri.append((dai, dai + len(o["van_ban"])))
            phan.append(o["van_ban"]); dai += len(o["van_ban"])
            hang, cot = o["hang"], cot + 1
        phan.append(xuong_dong * (so_hang - hang - 1))
        chu = "".join(phan)
        if not chu:
            continue
        u = vb.find(chu, x if x is not None else con_tro, y if y is not None else z)
        v = u + len(chu)
        if u < 0 or vb[x if x is not None else con_tro:u].strip():
            continue
        if y is not None and vb[v:y].strip():
            continue
        moi = deepcopy(khoi)
        moi["bat_dau"], moi["ket_thuc"] = (x, y) if x is not None else (u, v)
        moi["o"] = []
        for o, (dau, cuoi) in zip(cac_o, vi_tri):
            da_khai = _khoang(o, moi["bat_dau"], moi["ket_thuc"], o["van_ban"])
            if da_khai is not None and da_khai != (u + dau, u + cuoi):
                loi("TC_SAI_NGUON")
            moi["o"].append({**o, "bat_dau": u + dau, "ket_thuc": u + cuoi})
        return moi
    loi("TC_SAI_NGUON")


def _bang(khoi, vb, a, z, trang, con_tro, huy):
    khoi = _map_bang(khoi, vb, a, z, con_tro, huy)
    khoang = _khoang(khoi, a, z)
    if khoang is None or khoang[0] == khoang[1]:
        loi("TC_SAI_NGUON")
    a, z = khoang
    if "van_ban" in khoi and khoi["van_ban"] != vb[a:z]:
        loi("TC_SAI_NGUON")
    hop = _hop(khoi.get("hop"), trang)
    cac_o = []
    for i, o in enumerate(danh_sach(khoi.get("o"))):
        if i % 32 == 0:
            huy()
        doi_tuong(o, ("hang", "cot", "gop_hang", "gop_cot", "van_ban"))
        for k in ("hang", "cot", "gop_hang", "gop_cot"):
            so(o[k], 1 if k.startswith("gop_") else 0, nguyen=True)
        if type(o["van_ban"]) is not str:
            loi("TC_SAI_NGUON")
        vt = _khoang(o, a, z, o["van_ban"])
        if vt is None or vb[vt[0]:vt[1]] != o["van_ban"]:
            loi("TC_SAI_NGUON")
        cac_o.append({k: o[k] for k in ("hang", "cot", "gop_hang", "gop_cot", "van_ban")})
        cac_o[-1].update(bat_dau=vt[0], ket_thuc=vt[1], hop=_hop(o.get("hop"), trang, hop))
    so_hang, so_cot = _kiem_luoi(cac_o, huy)
    cac_o.sort(key=lambda o: (o["hang"], o["cot"]))
    con_tro = a
    for i, o in enumerate(cac_o):
        if i % 32 == 0:
            huy()
        if o["bat_dau"] < con_tro or vb[con_tro:o["bat_dau"]].strip(" \t\r\n|"):
            loi("TC_SAI_NGUON")
        con_tro = o["ket_thuc"]
    if vb[con_tro:z].strip(" \t\r\n|"):
        loi("TC_SAI_NGUON")
    tieu_de = danh_sach(khoi.get("hang_tieu_de", []))
    if any(type(r) is not int or r < 0 or r >= so_hang for r in tieu_de):
        loi("TC_SAI_NGUON")
    # Tiêu đề lặp chỉ là phần đầu liên tục do nguồn khai rõ.
    if tieu_de != list(range(len(tieu_de))):
        loi("TC_SAI_NGUON")
    if any(o["hang"] < len(tieu_de) < o["hang"] + o["gop_hang"] for o in cac_o):
        loi("TC_SAI_NGUON")
    # Ranh giới hàng nằm trong ô gộp không được phép cắt.
    moc = sorted({0, so_hang, *(o["hang"] for o in cac_o)})
    gop = sorted((o["hang"], o["hang"] + o["gop_hang"]) for o in cac_o if o["gop_hang"] > 1)
    ranh, j, cuoi = [], 0, -1
    for r in moc:
        while j < len(gop) and gop[j][0] < r:
            cuoi = max(cuoi, gop[j][1])
            j += 1
        if r >= cuoi:
            ranh.append(r)
    nhom = []
    chi_so = 0
    for r, s in zip(ranh, ranh[1:]):
        cac_o_nhom = []
        while chi_so < len(cac_o) and cac_o[chi_so]["hang"] < s:
            cac_o_nhom.append(cac_o[chi_so])
            chi_so += 1
        if not cac_o_nhom:
            loi("TC_SAI_NGUON")
        nhom.append({"hang_bat_dau": r, "hang_ket_thuc": s,
                     "bat_dau": min(o["bat_dau"] for o in cac_o_nhom), "o": cac_o_nhom})
    nhom[0]["bat_dau"] = a
    for i, n in enumerate(nhom):
        n["ket_thuc"] = nhom[i + 1]["bat_dau"] if i + 1 < len(nhom) else z
    return {"bat_dau": a, "ket_thuc": z, "so_hang": so_hang, "so_cot": so_cot,
            "hang_tieu_de": deepcopy(tieu_de), "nhom_hang": nhom, "hop": hop}


def lap_ban_do(v, huy):
    """Trả phân hoạch đủ nguồn: chữ, bảng, khoảng trắng và ký tự ngắt trang."""
    vb, vung = v["van_ban"], []

    def them(a, z, loai, p, hop=None, bang=None):
        if a < z:
            vung.append({"bat_dau": a, "ket_thuc": z, "loai_khoi": loai,
                         "so_trang": p, "hop": hop, "bang": bang})

    def khoi_trong_trang(cac_khoi, a, z, trang):
        p = trang["so"] if trang else None
        if not cac_khoi:
            them(a, z, "doan", p)
            return
        con_tro = a
        for i, khoi in enumerate(danh_sach(cac_khoi)):
            if i % 32 == 0:
                huy()
            doi_tuong(khoi, ("loai",))
            if khoi["loai"] == "doan":
                x, y = _chuoi(khoi, vb, a, z, con_tro)
                hop = _hop(khoi.get("hop"), trang)
                _kiem_dong_tu(khoi, vb, x, y, trang, huy)
                bang = None
            elif khoi["loai"] == "bang":
                bang = _bang(khoi, vb, a, z, trang, con_tro, huy)
                x, y, hop = bang["bat_dau"], bang["ket_thuc"], bang["hop"]
            else:
                loi("TC_SAI_NGUON")
            if x < con_tro or vb[con_tro:x].strip():
                loi("TC_SAI_NGUON")
            them(con_tro, x, "phan_cach", p)
            them(x, y, khoi["loai"], p, hop, bang)
            con_tro = y
        if vb[con_tro:z].strip():
            loi("TC_SAI_NGUON")
        them(con_tro, z, "phan_cach", p)

    if v["so_trang"] == 0:
        if v["nguon_doc"] != "docx" or v["trang"]:
            loi("TC_SAI_NGUON")
        khoi_trong_trang(v.get("khoi", []), 0, len(vb), None)
    else:
        cac_trang = vb.split("\f")
        if len(cac_trang) != v["so_trang"]:
            loi("TC_SAI_NGUON")
        a = 0
        for chu, trang in zip(cac_trang, v["trang"]):
            huy()
            z = a + len(chu)
            khoi_trong_trang(trang["khoi"], a, z, trang)
            if z < len(vb):
                them(z, z + 1, "phan_cach", None)
            a = z + 1
    con_tro = 0
    for i, r in enumerate(vung):
        if i % 32 == 0:
            huy()
        if r["bat_dau"] != con_tro:
            loi("TC_SAI_NGUON")
        con_tro = r["ket_thuc"]
    if con_tro != len(vb):
        loi("TC_SAI_NGUON")
    return vung


def dinh_vi(vung, cac_map, huy, dau=None):
    """Giữ hộp nguồn ở cấp khối/ô; không lấy bao chữ nhật của nhiều khối."""
    vi_tri = []
    if dau is None:
        dau = [r["bat_dau"] for r in vung]
    for m in cac_map:
        a, z = m["nguon_bat_dau"], m["nguon_ket_thuc"]
        i = max(0, bisect_left(dau, a) - 1)
        while i < len(vung) and vung[i]["bat_dau"] < z:
            if i % 32 == 0:
                huy()
            r = vung[i]
            x, y = max(a, r["bat_dau"]), min(z, r["ket_thuc"])
            if x < y:
                vi_tri.append({"bat_dau": x, "ket_thuc": y, "so_trang": r["so_trang"],
                               "hop": deepcopy(r["hop"]), "vai_tro": m["vai_tro"],
                               "muc_hop": "khoi" if r["hop"] is not None else None})
            i += 1
    trang = {p["so_trang"] for p in vi_tri if p["so_trang"] is not None}
    p = next(iter(trang)) if len(trang) == 1 else None
    hop_thuc = [v["hop"] for v in vi_tri if v["hop"] is not None]
    hop = hop_thuc[0] if p is not None and hop_thuc and all(h == hop_thuc[0] for h in hop_thuc) else None
    return {"trang": p, "hop": deepcopy(hop)}, vi_tri
