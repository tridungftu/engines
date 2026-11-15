"""Vị trí Unicode và kiểm hình học/khung ảnh; không dựng trang Word."""
import math
import re
import struct
import zlib

from kho_tri_thuc_sdk.engine import LoiNghiepVu


def loi(ma="DC_SAI_NGUON"):
    cau = {
        "DC_SAI_NGUON": "Nguồn đối chiếu đã thay đổi hoặc chưa khớp bản được ghim. Anh chọn lại hồ sơ.",
        "DC_SAI_DAU_VAO": "Dữ liệu đối chiếu chưa đúng định dạng. Anh kiểm tra lại hồ sơ.",
        "DC_THIEU_NGUON": "Chưa đủ nguồn hoặc quyền đọc tài liệu để đối chiếu. Anh kiểm tra lại hồ sơ được cấp.",
        "DC_QUA_GIOI_HAN": "Hồ sơ vượt giới hạn đối chiếu của lượt này.",
        "DC_OCR_KHONG_DOC_DUOC": "Bản ký chưa có kết quả đọc đầy đủ. Anh kiểm tra lại nguồn OCR.",
    }
    raise LoiNghiepVu(ma, cau[ma])


def _hop(hop, trang):
    if (type(hop) is not list or len(hop) != 4 or
            any(type(x) not in (int, float) or not math.isfinite(x) for x in hop)):
        loi()
    x0, y0, x1, y1 = hop
    if not (0 <= x0 < x1 <= trang["rong"] and 0 <= y0 < y1 <= trang["cao"]):
        loi()


def lap_vi_tri(van_ban, kiem_huy=lambda: None):
    """Giữ cây nguồn; chỉ neo khối OCR khi lát chữ xác định duy nhất.

    Đoạn OCR chưa neo được vẫn có vị trí trang/nguyên văn, không đoán hộp.
    DOCX đã có offset bắt buộc khớp, kể cả ô rỗng/gộp và cây lồng nhau.
    """
    chu = van_ban["van_ban"]
    ds = [{"bat_dau": 0, "ket_thuc": len(chu), "loai": "tai_lieu", "duong_dan": "/van_ban"}]
    bien = {0, len(chu)}
    chua_neo = []

    def them(nut, path, a, b, phu):
        ds.append({"bat_dau": a, "ket_thuc": b, "loai": nut.get("loai", "o"),
                   "duong_dan": path, **phu,
                   **{k: nut[k] for k in ("hop", "phan", "dieu", "khoan", "so_doan", "hang", "cot", "gop_hang", "gop_cot") if k in nut}})
        bien.update((a, b))

    def docx(khoi, path, a, b):
        for i, k in enumerate(khoi):
            kiem_huy()
            x, y = k.get("bat_dau"), k.get("ket_thuc")
            if (type(x) is not int or type(y) is not int or not a <= x <= y <= b or
                    chu[x:y] != k.get("van_ban")):
                loi()
            p = f"{path}/{i}"
            them(k, p, x, y, {})
            if k.get("loai") == "bang":
                for j, o in enumerate(k["o"]):
                    op = f"{p}/o/{j}"
                    ox, oy = o.get("bat_dau"), o.get("ket_thuc")
                    if (type(ox) is not int or type(oy) is not int or not x <= ox <= oy <= y or
                            chu[ox:oy] != o.get("van_ban")):
                        loi()
                    them(o, op, ox, oy, {})
                    docx(o["khoi"], op + "/khoi", ox, oy)

    if van_ban["nguon_doc"] == "docx":
        if van_ban["so_trang"] != 0 or van_ban["trang"] or "khoi_docx" not in van_ban:
            loi()
        docx(van_ban["khoi_docx"], "/khoi_docx", 0, len(chu))
    else:
        cac_trang = chu.split("\f")
        if len(cac_trang) != van_ban["so_trang"] or not all(x.strip() for x in cac_trang):
            loi("DC_OCR_KHONG_DOC_DUOC")
        moc = 0
        for i, trang in enumerate(van_ban["trang"]):
            kiem_huy()
            if trang["so"] != i + 1 or trang["don_vi"] not in ("pt", "px"):
                loi()
            cuoi = moc + len(cac_trang[i])
            them({"loai": "trang"}, f"/trang/{i}", moc, cuoi, {"so_trang": i + 1, "don_vi": trang["don_vi"]})

            def ocr(nut, path, a, b):
                kiem_huy()
                if "hop" in nut:
                    _hop(nut["hop"], trang)
                text = nut.get("van_ban")
                x, y = a, b
                if isinstance(text, str) and text:
                    dau = chu.find(text, a, b)
                    if dau < 0 or chu.find(text, dau + 1, b) >= 0:
                        chua_neo.append(path)
                        # Vẫn kiểm mọi hộp con; không gắn hộp vào lát đoán.
                        neo = False
                    else:
                        x, y, neo = dau, dau + len(text), True
                else:
                    neo = False
                if neo:
                    them(nut, path, x, y, {"so_trang": i + 1, "don_vi": trang["don_vi"]})
                for key in ("dong", "tu", "o"):
                    for j, con in enumerate(nut.get(key, [])):
                        ocr(con, f"{path}/{key}/{j}", x, y)

            for j, k in enumerate(trang["khoi"]):
                ocr(k, f"/trang/{i}/khoi/{j}", moc, cuoi)
            moc = cuoi + 1
    return ds, bien, chua_neo


def ve_nguon(chuan_hoa, bat_dau, ket_thuc):
    """Map lát chuẩn hóa về các lát nguyên văn và nút nguồn thực sự giao nhau.

    Map bốn số: [đầu chuẩn, cuối chuẩn, đầu gốc, cuối gốc]. Đoạn có độ
    dài bằng nhau là tịnh tiến; đoạn co/giãn trỏ cả cụm nguồn bị thay.
    """
    if (type(bat_dau) is not int or type(ket_thuc) is not int or
            not 0 <= bat_dau <= ket_thuc <= len(chuan_hoa["van_ban"])):
        loi("DC_SAI_DAU_VAO")
    lat = []
    for x, y, a, b in chuan_hoa["anh_xa"]:
        dau, cuoi = max(x, bat_dau), min(y, ket_thuc)
        if dau >= cuoi:
            continue
        if y - x == b - a:
            a, b = a + dau - x, a + cuoi - x
        if lat and lat[-1][1] == a:
            lat[-1][1] = b
        elif not lat or lat[-1] != [a, b]:
            lat.append([a, b])
    # Lát rỗng dùng vị trí chèn ở phía phải; cuối chuỗi dùng mép cuối.
    if not lat:
        a = len(chuan_hoa["nguyen_van"])
        for x, y, g, h in chuan_hoa["anh_xa"]:
            if x <= bat_dau < y:
                a = g + bat_dau - x if y - x == h - g else g
                break
        lat = [[a, a]]
    vi_tri = [v for v in chuan_hoa["vi_tri"] if any(
        v["bat_dau"] < b and a < v["ket_thuc"] or a == b and v["bat_dau"] <= a <= v["ket_thuc"]
        for a, b in lat)]
    return {"lat_nguon": [{"bat_dau": a, "ket_thuc": b,
                           "van_ban": chuan_hoa["nguyen_van"][a:b]} for a, b in lat],
            "vi_tri": vi_tri}


def kiem_anh(raw, mime, pixel_toi_da, kiem_huy=lambda: None):
    """PNG: CRC + DEFLATE đủ dòng; JPEG: khung/marker/kích thước, chưa giải mã.

    DC-8 phải giải mã JPEG bằng thư viện đã ghim trước khi quét ảnh.
    """
    def kich(w, h):
        if w <= 0 or h <= 0:
            loi()
        if w * h > pixel_toi_da:
            loi("DC_QUA_GIOI_HAN")
        return w, h

    try:
        if mime == "image/png":
            if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
                loi()
            pos, idat, het = 8, [], False
            da_idat = False
            w = h = stride = None
            while pos < len(raw):
                kiem_huy()
                n, = struct.unpack_from(">I", raw, pos)
                tag, data = raw[pos + 4:pos + 8], raw[pos + 8:pos + 8 + n]
                crc, = struct.unpack_from(">I", raw, pos + 8 + n)
                if zlib.crc32(tag + data) != crc or pos + n + 12 > len(raw):
                    loi()
                if w is None and tag != b"IHDR":
                    loi()
                if tag == b"IHDR":
                    if w is not None or n != 13:
                        loi()
                    w, h, bit, color, comp, filt, inter = struct.unpack(">IIBBBBB", data)
                    kich(w, h)  # Trần pixel trước khi giải nén.
                    hop_le = {0: (1, 2, 4, 8, 16), 2: (8, 16), 3: (1, 2, 4, 8), 4: (8, 16), 6: (8, 16)}
                    if color not in hop_le or bit not in hop_le[color] or comp or filt or inter:
                        loi()  # PNG interlace chưa hỗ trợ trong DC-3.
                    stride = (w * {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color] * bit + 7) // 8 + 1
                elif tag == b"IDAT":
                    if het:
                        loi()
                    idat.append(data)
                    da_idat = True
                elif tag == b"IEND":
                    if n or not da_idat or pos + 12 != len(raw):
                        loi()
                    break
                else:
                    if da_idat:
                        het = True
                    if tag[0] & 32 == 0 and tag != b"PLTE":
                        loi()
                pos += n + 12
            else:
                loi()
            d, so = zlib.decompressobj(), 0
            for data in idat:
                while data:
                    kiem_huy()
                    out = d.decompress(data, 65536)
                    data = d.unconsumed_tail
                    if d.unused_data:
                        loi()
                    for i in range((-so) % stride, len(out), stride):
                        if out[i] > 4:
                            loi()
                    so += len(out)
                    if so > stride * h:
                        loi("DC_QUA_GIOI_HAN")
            if not d.eof or so != stride * h:
                loi()
            return {"rong": w, "cao": h, "da_giai_ma": True}
        if mime != "image/jpeg" or not raw.startswith(b"\xff\xd8"):
            loi()
        pos, dims, scan = 2, None, False
        while pos < len(raw):
            kiem_huy()
            if raw[pos] != 255:
                loi()
            while pos < len(raw) and raw[pos] == 255:
                pos += 1
            tag = raw[pos]
            pos += 1
            if tag == 217:
                if not scan or dims is None or pos != len(raw):
                    loi()
                return {"rong": dims[0], "cao": dims[1], "da_giai_ma": False}
            if tag in (0, 216) or 208 <= tag <= 215:
                loi()
            n, = struct.unpack_from(">H", raw, pos)
            if n < 2 or pos + n > len(raw):
                loi()
            data = raw[pos + 2:pos + n]
            if tag in (192, 193, 194):
                if dims is not None or len(data) < 6:
                    loi()
                bit, h, w, components = struct.unpack_from(">BHHB", data)
                if bit != 8 or components not in (1, 3, 4) or len(data) != 6 + 3 * components:
                    loi()
                dims = kich(w, h)
            elif 195 <= tag <= 207 and tag not in (196, 200, 204):
                loi()
            pos += n
            if tag == 218:
                if dims is None or len(data) < 4:
                    loi()
                scan = True
                # Chỉ tìm marker không escaped trong entropy, không giải mã DCT.
                while pos < len(raw):
                    at = raw.find(b"\xff", pos)
                    if at < 0 or at + 1 >= len(raw):
                        loi()
                    end = at + 1
                    while end < len(raw) and raw[end] == 255:
                        end += 1
                    if end >= len(raw):
                        loi()
                    if raw[end] == 0 or 208 <= raw[end] <= 215:
                        pos = end + 1
                    else:
                        pos = at
                        break
        loi()
    except (struct.error, IndexError, zlib.error, OverflowError):
        loi()
