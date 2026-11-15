"""Đọc DOCX trong RAM, chuyển có sửa từ ma-nguon/docx.py và
ma-nguon/vendor/review/doc_hop_dong.py (Accept All và Numbering).

Không chuyển định dạng, không phân trang suy đoán. Giữ cây khối DOCX riêng
vì schema trang chung yêu cầu hộp thật mà XML Word không cung cấp.
"""

import hashlib
import io
import json
from pathlib import PurePosixPath
import re
import stat
import xml.etree.ElementTree as ET
import zipfile
import zlib

from kho_tri_thuc_sdk.engine import LoiDuongTruyen, LoiNghiepVu, ViecDaHuy


MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = "{" + W_NS + "}"
CT = "{http://schemas.openxmlformats.org/package/2006/content-types}"
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
CT_DOC = "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"
REL_DOC = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
TEP_TOI_DA = 20 * 1048576
GIAI_NEN_TOI_DA = 64 * 1048576
XML_TOI_DA = 16 * 1048576
SO_MUC_ZIP_TOI_DA = 2048
TY_LE_NEN_TOI_DA = 200
SO_NUT_XML_TOI_DA = 200000
DO_SAU_XML_TOI_DA = 128
KY_TU_TOI_DA = 500000
SO_COT_TOI_DA = 256
SO_O_TOI_DA = 50000
JSON_TOI_DA = 20 * 1048576
CAU_GIOI_HAN = "Tài liệu vượt giới hạn xử lý; hãy chia tài liệu trước khi gửi."
CAU_DOCX_LOI = "Không đọc được cấu trúc tệp Word."
_XOA = {W + t for t in (
    "del", "moveFrom", "rPrChange", "pPrChange", "sectPrChange", "tblPrChange",
    "tblPrExChange", "tcPrChange", "trPrChange", "tblGridChange", "numberingChange",
    "moveFromRangeStart", "moveFromRangeEnd", "moveToRangeStart", "moveToRangeEnd",
    "customXmlDelRangeStart", "customXmlDelRangeEnd", "customXmlInsRangeStart",
    "customXmlInsRangeEnd", "cellIns", "cellDel", "cellMerge")}
_MO_GOI = {W + "ins", W + "moveTo"}


def _vuot():
    raise LoiNghiepVu("VUOT_GIOI_HAN", CAU_GIOI_HAN)


def _sai():
    raise LoiNghiepVu("DOCX_KHONG_HOP_LE", CAU_DOCX_LOI)


class _BoDungCay(ET.TreeBuilder):
    def __init__(self, kiem_huy):
        super().__init__()
        self._kiem_huy = kiem_huy
        self._sau = self._nut = 0

    def doctype(self, ten, pubid, system):
        _sai()

    def start(self, ten, thuoc_tinh):
        self._sau += 1
        self._nut += 1
        if self._sau > DO_SAU_XML_TOI_DA or self._nut > SO_NUT_XML_TOI_DA:
            _vuot()
        if self._nut % 128 == 0:
            self._kiem_huy()
        return super().start(ten, thuoc_tinh)

    def end(self, ten):
        self._sau -= 1
        return super().end(ten)


def _doc_xml(z, ten, kiem_huy):
    info = z.getinfo(ten)
    if info.file_size > XML_TOI_DA:
        _vuot()
    parser = ET.XMLParser(target=_BoDungCay(kiem_huy))
    da_doc = 0
    with z.open(info) as f:
        while True:
            kiem_huy()
            raw = f.read(min(65536, XML_TOI_DA + 1 - da_doc))
            if not raw:
                break
            da_doc += len(raw)
            if da_doc > XML_TOI_DA:
                _vuot()
            parser.feed(raw)
    if da_doc != info.file_size:
        _sai()
    return parser.close()


def _kiem_zip(z, kiem_huy):
    infos = z.infolist()
    if len(infos) > SO_MUC_ZIP_TOI_DA:
        _vuot()
    ten_da_co, tong = set(), 0
    for i in infos:
        kiem_huy()
        ten = i.filename
        if (ten in ten_da_co or "\\" in ten or "\0" in ten
                or PurePosixPath(ten).is_absolute() or ".." in PurePosixPath(ten).parts
                or ":" in ten or stat.S_ISLNK(i.external_attr >> 16)
                or i.flag_bits & 1 or i.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)):
            _sai()
        ten_da_co.add(ten)
        tong += i.file_size
        if (tong > GIAI_NEN_TOI_DA
                or ((ten.endswith(".xml") or ten.endswith(".rels")) and i.file_size > XML_TOI_DA)
                or i.file_size > TY_LE_NEN_TOI_DA * max(1, i.compress_size)):
            _vuot()
    if not {"[Content_Types].xml", "_rels/.rels", "word/document.xml"} <= ten_da_co:
        _sai()
    return ten_da_co


def _chap_nhan_xml(root, kiem_huy):
    """Accept All: bỏ dòng/ô bị xóa, nối dấu đoạn bị xóa, giữ phần chèn."""
    so = sum(e.tag in _XOA | _MO_GOI for e in root.iter())

    def mo_goi(el):
        kiem_huy()
        giu = []
        for c in el:
            mo_goi(c)
            giu.extend(list(c) if c.tag in _MO_GOI else [c])
        el[:] = giu

    # Mở gói trước để dấu đoạn bị xóa còn nối được qua biên phần chèn/di chuyển.
    mo_goi(root)
    for parent in list(root.iter()):
        kiem_huy()
        giu = []
        for e in parent:
            if e.tag == W + "tr" and e.find(f"{W}trPr/{W}del") is not None:
                continue
            if e.tag == W + "tc" and e.find(f"{W}tcPr/{W}cellDel") is not None:
                continue
            giu.append(e)
        parent[:] = giu
        # Đi từ trái sang phải để chuỗi nhiều dấu đoạn bị xóa vẫn giữ thứ tự.
        giu, noi = [], []
        for i, p in enumerate(parent):
            if i % 128 == 0:
                kiem_huy()
            dau_xoa = p.find(f"{W}pPr/{W}rPr/{W}del") if p.tag == W + "p" else None
            if dau_xoa is not None and i + 1 < len(parent) and parent[i + 1].tag == W + "p":
                noi.extend(c for c in p if c.tag != W + "pPr")
            else:
                if noi:
                    pos = 1 if p.find(W + "pPr") is not None else 0
                    p[pos:pos] = noi
                    noi = []
                giu.append(p)
        parent[:] = giu

    def lam(el):
        kiem_huy()
        giu = []
        for c in el:
            if c.tag in _XOA:
                continue
            lam(c)
            giu.extend(list(c) if c.tag in _MO_GOI else [c])
        el[:] = giu

    lam(root)
    return so


def _val(el, ten, mac_dinh=None):
    c = el.find(W + ten)
    return c.get(W + "val", mac_dinh) if c is not None else mac_dinh


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
                self._abs[aid] = {_nguyen(l.attrib[W + "ilvl"], 8): self._muc(l)
                                  for l in a.findall(W + "lvl")}
            for n in numbering.findall(W + "num"):
                nid = n.attrib[W + "numId"]
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
                if s.get(W + "type") == "paragraph" and s.get(W + "default") in ("1", "true"):
                    self._style_mac_dinh = sid
                np = s.find(f"{W}pPr/{W}numPr")
                self._style[sid] = (_val(s, "basedOn"),
                                    _val(np, "numId") if np is not None else None,
                                    _val(np, "ilvl") if np is not None else None)

    @staticmethod
    def _muc(l):
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
            return m["text"] or "•"

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
        self.canh_bao = set()

    def _chu(self, el):
        ds = []
        for e in el:
            if e.tag == W + "t":
                ds.append(e.text or "")
            elif e.tag == W + "tab":
                ds.append("\t")
            elif e.tag in (W + "br", W + "cr"):
                ds.append("\n")
            elif e.tag == W + "noBreakHyphen":
                ds.append("‑")
            elif e.tag == W + "softHyphen":
                ds.append("\u00ad")
            elif e.tag == W + "txbxContent":
                ds.append(_noi_khoi(self.khoi(e)))
            elif e.tag not in (W + "pPr", W + "rPr", W + "instrText", W + "delText"):
                ds.append(self._chu(e))
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
        for el in container:
            self._kiem_huy()
            if el.tag == W + "p":
                ds.append(self._doan(el))
            elif el.tag == W + "tbl":
                ds.append(self._bang(el, do_sau + 1))
            elif el.tag == W + "sdt":
                c = el.find(W + "sdtContent")
                if c is not None:
                    ds.extend(self.khoi(c, do_sau))
            elif el.tag == W + "customXml":
                ds.extend(self.khoi(el, do_sau))
            elif el.tag == W + "altChunk":
                self.canh_bao.add("Có nội dung nhúng dạng khác chưa đọc được; cần kiểm tra tài liệu gốc.")
            elif any(e.tag == W + "t" for e in el.iter()):
                _sai()
        return ds

    def _phan_tu(self, container, ten):
        """Dòng/ô có thể nằm trong content control; không làm mất chúng."""
        for el in container:
            self._kiem_huy()
            if el.tag == W + ten:
                yield el
            elif el.tag == W + "sdt":
                c = el.find(W + "sdtContent")
                if c is not None:
                    yield from self._phan_tu(c, ten)
            elif el.tag == W + "customXml":
                yield from self._phan_tu(el, ten)

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
                    if goc is None or any(e.text for c in cells for e in c.iter(W + "t")):
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
        if not hang_o and any(e.tag == W + "t" for e in tbl.iter()):
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


def doc_bytes(du_lieu, kiem_huy, tien_do, *, phien_ban_engine):
    """Seam thuần dùng trong handler; bytes gốc không bị chỉnh sửa."""
    if len(du_lieu) > TEP_TOI_DA:
        _vuot()
    kiem_huy()
    try:
        with zipfile.ZipFile(io.BytesIO(du_lieu)) as z:
            ten = _kiem_zip(z, kiem_huy)
            tien_do(25, "Đang kiểm tra cấu trúc tệp Word")
            ct = _doc_xml(z, "[Content_Types].xml", kiem_huy)
            rel = _doc_xml(z, "_rels/.rels", kiem_huy)
            if (ct.tag != CT + "Types" or rel.tag != REL + "Relationships"
                    or not any(c.get("PartName") == "/word/document.xml" and c.get("ContentType") == CT_DOC
                               for c in ct.findall(CT + "Override"))
                    or not any(r.get("Type") == REL_DOC and r.get("Target", "").lstrip("/") == "word/document.xml"
                               and r.get("TargetMode", "Internal") == "Internal"
                               for r in rel.findall(REL + "Relationship"))):
                _sai()
            root = _doc_xml(z, "word/document.xml", kiem_huy)
            if root.tag != W + "document" or root.find(W + "body") is None:
                _sai()
            tien_do(45, "Đang chấp nhận các sửa đổi trong bộ nhớ")
            so_sua = _chap_nhan_xml(root, kiem_huy)
            numbering = _doc_xml(z, "word/numbering.xml", kiem_huy) if "word/numbering.xml" in ten else None
            styles = _doc_xml(z, "word/styles.xml", kiem_huy) if "word/styles.xml" in ten else None
            for cay, tag in [(numbering, "numbering"), (styles, "styles")]:
                if cay is not None:
                    if cay.tag != W + tag:
                        _sai()
                    _chap_nhan_xml(cay, kiem_huy)
            tien_do(65, "Đang đọc đoạn văn, bảng và số tự động")
            doc = _DocNoiDung(DanhSo(numbering, styles), kiem_huy)
            khoi = doc.khoi(root.find(W + "body"))
            text = _noi_khoi(khoi)
            _gan_vi_tri(khoi)
            canh_bao = ["Chưa phân trang Word; vị trí theo đoạn/Điều/Khoản, không có số trang hoặc hộp tọa độ."]
            if so_sua:
                canh_bao.append("Đã Accept All các sửa đổi bằng XML trong bộ nhớ; tệp gốc không đổi.")
            if any(e.tag in (W + "drawing", W + "pict", W + "object") for e in root.iter()):
                canh_bao.append("Có hình ảnh hoặc đối tượng nhúng; nội dung dạng ảnh chưa được nhận dạng chữ.")
            if any(n.startswith(("word/header", "word/footer", "word/footnotes", "word/endnotes")) for n in ten):
                canh_bao.append("Chỉ đọc phần thân; đầu/chân trang và chú thích cần kiểm tra trên tài liệu gốc.")
            canh_bao.extend(sorted(doc.canh_bao))
            ket_qua = {"loai": "van_ban_tai_lieu", "van_ban_tai_lieu": {
                "phien_ban": 1, "van_ban": text, "trang": [], "nguon_doc": "docx",
                "ly_do_chuyen_nguon": None, "so_trang": 0,
                "phien_ban_engine": phien_ban_engine,
                "bam_dau_vao": "sha256:" + hashlib.sha256(du_lieu).hexdigest(),
                "canh_bao": canh_bao, "khoi_docx": khoi, "so_sua_doi_da_chap_nhan": so_sua}}
            if len(json.dumps(ket_qua, ensure_ascii=False).encode("utf-8")) > JSON_TOI_DA:
                _vuot()
            kiem_huy()
            return ket_qua
    except (LoiNghiepVu, ViecDaHuy):
        raise
    except (zipfile.BadZipFile, zipfile.LargeZipFile, ET.ParseError, KeyError,
            ValueError, TypeError, OverflowError, RecursionError, OSError, RuntimeError, zlib.error):
        raise LoiNghiepVu("DOCX_KHONG_HOP_LE", CAU_DOCX_LOI) from None


def doc_docx(viec, *, phien_ban_engine):
    viec.kiem_huy()
    dv = viec.dau_vao
    tep = dv.get("tep", {}) if isinstance(dv, dict) else {}
    if not isinstance(dv, dict) or not isinstance(tep, dict) or dv.get("loai") != "tep" or tep.get("mime") != MIME_DOCX:
        raise LoiNghiepVu("TEP_KHONG_HO_TRO", "Chỉ nhận tệp Word định dạng DOCX.")
    if not isinstance(tep.get("tep_id"), str) or not tep["tep_id"]:
        _sai()
    if type(tep.get("kich_thuoc")) is not int or tep["kich_thuoc"] < 0:
        _sai()
    if tep["kich_thuoc"] > TEP_TOI_DA:
        _vuot()
    viec.tien_do(5, "Đang nhận tệp Word")
    try:
        with viec.mo_tep(tep["tep_id"]) as f:
            du_lieu = f.read(TEP_TOI_DA + 1)
    except LoiDuongTruyen as loi:
        if loi.http_status == 413:
            _vuot()
        raise
    if len(du_lieu) > TEP_TOI_DA:
        _vuot()
    if len(du_lieu) != tep["kich_thuoc"]:
        _sai()
    ket_qua = doc_bytes(du_lieu, viec.kiem_huy, viec.tien_do,
                       phien_ban_engine=phien_ban_engine)
    viec.tien_do(100, "Đã đọc nội dung Word")
    viec.kiem_huy()
    return ket_qua
