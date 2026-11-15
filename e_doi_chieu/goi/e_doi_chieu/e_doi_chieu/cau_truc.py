"""Cấu trúc DOCX và offset Unicode nửa mở; chuyển có sửa từ TX-1.

Nguồn và SHA-256 tại NGUON.md. Không Accept All hoặc sửa cây nguồn.
Dấu phân cách đoạn/bảng là quy ước tuần tự hóa, không phải dàn trang Word.
"""
import re
from kho_tri_thuc_sdk.engine import LoiNghiepVu

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = "{" + W_NS + "}"
KY_TU_TOI_DA = 500000
SO_COT_TOI_DA = 256
SO_O_TOI_DA = 50000


def _vuot():
    raise LoiNghiepVu("DC_QUA_GIOI_HAN", "Tài liệu vượt giới hạn xử lý. Anh chia nhỏ tài liệu trước khi gửi.")


def _sai():
    raise LoiNghiepVu("DC_WORD_KHONG_DOC_DUOC", "Không đọc đầy đủ được bản Word. Anh chọn tệp DOCX đã chốt có cấu trúc được hỗ trợ.")


def _val(el, ten, mac_dinh=None):
    ds = el.findall(W + ten)
    if len(ds) > 1:
        _sai()
    if not ds:
        return mac_dinh
    if W + "val" not in ds[0].attrib and ten != "isLgl":
        _sai()
    return ds[0].get(W + "val", mac_dinh)


def _nguyen(v, toi_da=1000000):
    if not isinstance(v, str) or not re.fullmatch(r"[0-9]{1,7}", v):
        _sai()
    n = int(v)
    if n > toi_da:
        _vuot()
    return n


def _dinh_dang_so(n, fmt):
    if fmt == "decimal":
        return str(n)
    if fmt == "decimalZero":
        return f"{n:02d}"
    if fmt in ("lowerLetter", "upperLetter"):
        s = ""
        while n > 0:
            n, r = divmod(n - 1, 26)
            s = chr(97 + r) + s
        return s.upper() if fmt == "upperLetter" else s
    if fmt in ("lowerRoman", "upperRoman"):
        s = ""
        for v, r in [(1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"),
                     (90, "xc"), (50, "l"), (40, "xl"), (10, "x"), (9, "ix"),
                     (5, "v"), (4, "iv"), (1, "i")]:
            q, n = divmod(n, v)
            s += r * q
        return s.upper() if fmt == "upperRoman" else s
    _sai()


class DanhSo:
    """Numbering nguồn cũ: đổi sang cây đã kiểm, bộ đếm riêng từng numId."""
    def __init__(self, numbering, styles):
        self._abs, self._num, self._style = {}, {}, {}
        self._dem = {}
        self._style_mac_dinh = None
        if numbering is not None:
            for a in numbering.findall(W + "abstractNum"):
                aid = a.attrib[W + "abstractNumId"]
                if aid in self._abs or len({l.get(W + "ilvl") for l in a.findall(W + "lvl")}) != len(a.findall(W + "lvl")):
                    _sai()
                self._abs[aid] = {_nguyen(l.attrib[W + "ilvl"], 8): self._muc(l)
                                  for l in a.findall(W + "lvl")}
            for n in numbering.findall(W + "num"):
                nid = n.attrib[W + "numId"]
                if nid in self._num:
                    _sai()
                aid = _val(n, "abstractNumId")
                if aid not in self._abs:
                    _sai()
                muc = {k: dict(v) for k, v in self._abs[aid].items()}
                for o in n.findall(W + "lvlOverride"):
                    il = _nguyen(o.attrib[W + "ilvl"], 8)
                    lvl = o.find(W + "lvl")
                    if lvl is not None:
                        muc[il] = self._muc(lvl)
                    if il not in muc:
                        _sai()
                    if _val(o, "startOverride") is not None:
                        muc[il]["start"] = _nguyen(_val(o, "startOverride"))
                self._num[nid] = muc
        if styles is not None:
            for s in styles.findall(W + "style"):
                sid = s.attrib[W + "styleId"]
                if sid in self._style:
                    _sai()
                if s.get(W + "type") == "paragraph" and s.get(W + "default") in ("1", "true"):
                    self._style_mac_dinh = sid
                np = s.find(f"{W}pPr/{W}numPr")
                self._style[sid] = (_val(s, "basedOn"),
                                    _val(np, "numId") if np is not None else None,
                                    _val(np, "ilvl") if np is not None else None)

    @staticmethod
    def _muc(l):
        if _val(l, "lvlText") is None and _val(l, "numFmt") != "none":
            _sai()
        return {"start": _nguyen(_val(l, "start", "1")),
                "fmt": _val(l, "numFmt", "decimal"), "text": _val(l, "lvlText", ""),
                "lgl": _val(l, "isLgl", "true") not in ("false", "0") if l.find(W + "isLgl") is not None else False,
                "restart": _val(l, "lvlRestart")}

    def nhan(self, p):
        ppr = p.find(W + "pPr")
        sid = _val(ppr, "pStyle", self._style_mac_dinh) if ppr is not None else self._style_mac_dinh
        nid = il = None
        da_thay = set()
        while sid is not None and sid in self._style:
            if sid in da_thay:
                _sai()
            da_thay.add(sid)
            sid, n, l = self._style[sid]
            nid, il = n if nid is None else nid, l if il is None else il
        if sid is not None and sid not in self._style:
            _sai()
        np = ppr.find(W + "numPr") if ppr is not None else None
        if np is not None:
            nid, il = _val(np, "numId", nid), _val(np, "ilvl", il)
        if nid is None or nid == "0":
            return ""
        il = _nguyen(il or "0", 8)
        if nid not in self._num or il not in self._num[nid]:
            _sai()
        muc = self._num[nid]
        dem = self._dem.setdefault(nid, {})
        dem[il] = dem.get(il, muc[il]["start"] - 1) + 1
        for k in list(dem):
            if k > il:
                restart = _nguyen(muc[k]["restart"], 9) if muc[k]["restart"] is not None else k
                if restart and il < restart:
                    del dem[k]
        m = muc[il]
        if m["fmt"] == "none":
            return ""
        if m["fmt"] == "bullet":
            return m["text"]

        def thay(match):
            k = int(match.group(1)) - 1
            if k not in muc:
                _sai()
            return _dinh_dang_so(dem.get(k, muc[k]["start"]), "decimal" if m["lgl"] else muc[k]["fmt"])

        return re.sub(r"%([1-9])", thay, m["text"])


def _noi_khoi(khoi):
    cac_chu, moc = [], 0
    for i, k in enumerate(khoi):
        if i:
            moc += 1
        k["_le"] = moc
        cac_chu.append(k["van_ban"])
        moc += len(k["van_ban"])
        if moc > KY_TU_TOI_DA:
            _vuot()
    return "\n".join(cac_chu)


def _gan_vi_tri(khoi, moc=0):
    for k in khoi:
        bat_dau = moc + k.pop("_le")
        k.update(bat_dau=bat_dau, ket_thuc=bat_dau + len(k["van_ban"]))
        if k["loai"] == "bang":
            for o in k["o"]:
                le = bat_dau + o.pop("_le")
                o.update(bat_dau=le, ket_thuc=le + len(o["van_ban"]))
                _gan_vi_tri(o["khoi"], le)


class _DocNoiDung:
    def __init__(self, danh_so, kiem_huy):
        self._danh_so, self._kiem_huy = danh_so, kiem_huy
        self._so_doan = self._so_o = 0
        self._dieu = None

    def bat_dau_phan(self):
        """Mỗi story Word có ngữ cảnh Điều và bộ đếm danh sách riêng."""
        self._dieu = None
        self._danh_so._dem.clear()

    def _chu(self, el):
        if el.text and el.text.strip():
            _sai()
        ds = []
        for e in el:
            self._kiem_huy()
            if e.tail and e.tail.strip():
                _sai()
            if e.tag in {W + s for s in ("tab", "br", "cr", "noBreakHyphen", "softHyphen")} and (len(e) or e.text and e.text.strip()):
                _sai()
            if e.tag == W + "t":
                if len(e):
                    _sai()
                ds.append(e.text or "")
            elif e.tag == W + "tab":
                ds.append("\t")
            elif e.tag in (W + "br", W + "cr"):
                ds.append("\n")
            elif e.tag == W + "noBreakHyphen":
                ds.append("‑")
            elif e.tag == W + "softHyphen":
                ds.append("\u00ad")
            elif e.tag in {W + s for s in ("r", "hyperlink", "smartTag", "customXml", "dir", "bdo", "sdtContent")}:
                ds.append(self._chu(e))
            elif e.tag == W + "sdt":
                c = e.find(W + "sdtContent")
                if c is None or len(e.findall(W + "sdtContent")) != 1 or any(x.tag not in {W + "sdtPr", W + "sdtEndPr", W + "sdtContent"} for x in e):
                    _sai()
                for x in e:
                    if x is not c:
                        _kiem_thuoc_tinh(x)
                ds.append(self._chu(c))
            elif e.tag in {W + s for s in ("pPr", "rPr", "customXmlPr", "smartTagPr", "sdtPr", "sdtEndPr")}:
                _kiem_thuoc_tinh(e)
            elif e.tag not in _DAU_MOC:
                _sai()
            elif len(e) or e.text and e.text.strip():
                _sai()
        return "".join(ds)

    def _doan(self, p):
        self._kiem_huy()
        self._so_doan += 1
        nhan = self._danh_so.nhan(p)
        chu = self._chu(p)
        chu = nhan + (" " if chu else "") + chu if nhan else chu
        if len(chu) > KY_TU_TOI_DA:
            _vuot()
        m = re.match(r"^\s*(?:Điều|ĐIỀU)\s+([0-9]{1,7})\b", chu)
        if m:
            self._dieu = int(m.group(1))
        k = {"loai": "doan", "so_doan": self._so_doan, "van_ban": chu}
        refs = [{"loai": "footnote" if e.tag == W + "footnoteReference" else "endnote", "ma": e.get(W + "id")}
                for e in p.iter() if e.tag in (W + "footnoteReference", W + "endnoteReference")]
        if refs:
            k["chu_thich"] = refs
        if self._dieu is not None:
            k["dieu"] = self._dieu
        m = re.match(r"^\s*([0-9]{1,7}(?:\.[0-9]{1,7})*[.)])\s", chu)
        if m:
            k["khoan"] = m.group(1)
        return k

    def khoi(self, container, do_sau=0):
        if do_sau > 16:
            _vuot()
        ds = []
        if container.text and container.text.strip():
            _sai()
        for el in container:
            self._kiem_huy()
            if el.tail and el.tail.strip():
                _sai()
            if el.tag == W + "p":
                ds.append(self._doan(el))
            elif el.tag == W + "tbl":
                ds.append(self._bang(el, do_sau + 1))
            elif el.tag == W + "sdt":
                c = el.find(W + "sdtContent")
                if c is None or len(el.findall(W + "sdtContent")) != 1 or any(x.tag not in {W + "sdtPr", W + "sdtEndPr", W + "sdtContent"} for x in el):
                    _sai()
                for x in el:
                    if x is not c:
                        _kiem_thuoc_tinh(x)
                ds.extend(self.khoi(c, do_sau + 1))
            elif el.tag == W + "customXml":
                ds.extend(self.khoi(el, do_sau + 1))
            elif el.tag in {W + s for s in ("sectPr", "tcPr", "customXmlPr")}:
                _kiem_thuoc_tinh(el)
            elif el.tag not in _DAU_MOC or len(el) or el.text and el.text.strip():
                _sai()
        return ds

    def _phan_tu(self, container, ten):
        """Dòng/ô trong content control vẫn giữ đúng vị trí."""
        if container.text and container.text.strip():
            _sai()
        for el in container:
            self._kiem_huy()
            if el.tail and el.tail.strip():
                _sai()
            if el.tag == W + ten:
                yield el
            elif el.tag == W + "sdt":
                c = el.find(W + "sdtContent")
                if c is None or len(el.findall(W + "sdtContent")) != 1 or any(x.tag not in {W + "sdtPr", W + "sdtEndPr", W + "sdtContent"} for x in el):
                    _sai()
                for x in el:
                    if x is not c:
                        _kiem_thuoc_tinh(x)
                yield from self._phan_tu(c, ten)
            elif el.tag == W + "customXml":
                yield from self._phan_tu(el, ten)
            elif el.tag in {W + s for s in ("tblPr", "tblGrid", "trPr", "tblPrEx", "customXmlPr")}:
                _kiem_thuoc_tinh(el)
            elif el.tag not in _DAU_MOC or len(el) or el.text and el.text.strip():
                _sai()

    def _bang(self, tbl, do_sau):
        cac_o, hang_o = [], []
        grid = tbl.find(W + "tblGrid")
        so_cot = len(grid.findall(W + "gridCol")) if grid is not None else 0
        dang_gop = {}
        for hang, tr in enumerate(self._phan_tu(tbl, "tr")):
            self._kiem_huy()
            trpr = tr.find(W + "trPr")
            cot = _nguyen(_val(trpr, "gridBefore", "0"), SO_COT_TOI_DA) if trpr is not None else 0
            sau = _nguyen(_val(trpr, "gridAfter", "0"), SO_COT_TOI_DA) if trpr is not None else 0
            nhom = []
            for tc in self._phan_tu(tr, "tc"):
                pr = tc.find(W + "tcPr")
                span = _nguyen(_val(pr, "gridSpan", "1"), SO_COT_TOI_DA) if pr is not None else 1
                if not span:
                    _sai()
                hm = pr.find(W + "hMerge") if pr is not None else None
                vm = pr.find(W + "vMerge") if pr is not None else None
                vm = vm.get(W + "val", "continue") if vm is not None else None
                if hm is not None and hm.get(W + "val", "continue") not in ("continue", "restart"):
                    _sai()
                if hm is not None and hm.get(W + "val", "continue") == "continue":
                    if not nhom or not nhom[-1][3] or nhom[-1][2] != vm:
                        _sai()
                    nhom[-1][0].append(tc)
                    nhom[-1][1] += span
                else:
                    nhom.append([[tc], span, vm, hm is not None])
            if not nhom:
                _sai()
            o_hang, gop_tiep = {}, {}
            for cells, span, vm, hm in nhom:
                self._kiem_huy()
                self._so_o += 1
                if self._so_o > SO_O_TOI_DA or cot + span + sau > SO_COT_TOI_DA:
                    _vuot()
                if vm == "continue":
                    goc = dang_gop.get((cot, span))
                    blocks = [k for c in cells for k in self.khoi(c, do_sau)]
                    if goc is None or any(k["van_ban"] or k["loai"] != "doan" for k in blocks):
                        _sai()
                    goc["gop_hang"] += 1
                    gop_tiep[(cot, span)] = goc
                else:
                    if vm not in (None, "restart"):
                        _sai()
                    khoi = [k for c in cells for k in self.khoi(c, do_sau)]
                    chu = _noi_khoi(khoi)
                    o = {"hang": hang, "cot": cot, "gop_hang": 1, "gop_cot": span,
                         "van_ban": chu, "khoi": khoi}
                    cac_o.append(o)
                    o_hang[cot] = o
                    if vm == "restart":
                        gop_tiep[(cot, span)] = o
                cot += span
            so_cot = max(so_cot, cot + sau)
            hang_o.append(o_hang)
            dang_gop = gop_tiep
        if not hang_o:
            _sai()
        if so_cot > SO_COT_TOI_DA:
            _vuot()
        cac_hang, moc = [], 0
        for hang, ds in enumerate(hang_o):
            chu, le = [], 0
            for cot in range(so_cot):
                if cot:
                    le += 3
                o = ds.get(cot)
                t = o["van_ban"] if o is not None else ""
                if o is not None:
                    o["_le"] = moc + le
                chu.append(t)
                le += len(t)
            cac_hang.append(" | ".join(chu))
            moc += le + 1
            if moc > KY_TU_TOI_DA:
                _vuot()
        return {"loai": "bang", "so_hang": len(hang_o), "so_cot": so_cot,
                "o": cac_o, "van_ban": "\n".join(cac_hang)}


_DAU_MOC = {W + s for s in ("bookmarkStart", "bookmarkEnd", "proofErr", "permStart", "permEnd",
                            "footnoteReference", "endnoteReference", "footnoteRef", "endnoteRef",
                            "separator", "continuationSeparator", "lastRenderedPageBreak")}


def _kiem_thuoc_tinh(el):
    """Không được giấu vùng nội dung trong nhánh thuộc tính bị bỏ qua."""
    for e in el.iter():
        if (not e.tag.startswith(W) or e.tag in {W + s for s in
                ("t", "p", "r", "tbl", "tc", "tr", "altChunk", "drawing", "pict", "object", "txbxContent", "fldSimple", "instrText")} or
                e.text and e.text.strip() or e.tail and e.tail.strip()):
            _sai()
