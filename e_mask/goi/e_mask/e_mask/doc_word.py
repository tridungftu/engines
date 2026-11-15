"""Reader Word MASK-B2: đối tượng nội bộ từng vùng, chưa là bản đã che.

Chép chọn lọc walker story/notes DC và run/bảng gộp TX, chuyển có sửa.
Không ghép hai ô/story, không bỏ chữ ẩn, không tạo DOCX hoặc gọi Local.
Nguồn, quyền và băm trước/sau tại NGUON.md.
"""

from dataclasses import dataclass, field
import hashlib

from .doc_tep import doc_tep
from .xml_an_toan import (
    A_NS, CP_NS, CUSTOM_NS, EP_NS, KY_TU_VAO_TOI_DA, SO_O_TOI_DA, W_NS,
)
from .xml_word import (
    GiaTriXML, W, anh_xa_xml, kiem_cay_word, kiem_properties, kiem_theme,
    qname, thuoc_tinh_theme, thuoc_tinh_word,
)
from .zip_an_toan import _sai, _vuot


def _bam(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True, repr=False)
class ManhWord:
    bat_dau: int
    ket_thuc: int
    nut: tuple
    run: tuple | None
    thuoc_tinh: str | None
    kieu: str
    byte_bat_dau: int
    byte_ket_thuc: int
    byte_ky_tu: tuple = field(repr=False)
    an: bool
    style: tuple


@dataclass(frozen=True, repr=False)
class ViTriO:
    bang: tuple
    hang: int
    cot: int
    gop_cot: int
    gop_tu: tuple | None


@dataclass(frozen=True, repr=False)
class VungWord:
    ma: int
    loai: str
    phan: str
    story: tuple
    nut: tuple
    o: ViTriO | None
    van_ban: str = field(repr=False)
    bam_van_ban: str
    anh_xa: tuple[ManhWord, ...] = field(repr=False)


@dataclass(frozen=True, repr=False)
class TaiLieuWord:
    phien_ban: int
    he_offset: str
    phien_ban_map: str
    bam_tep: str
    goi: object = field(repr=False)
    vung: tuple[VungWord, ...] = field(repr=False)
    tong_ky_tu: int
    tham_chieu_note: tuple = field(repr=False)


def _val(e, ten, default=None):
    if e is None:
        return default
    c = e.find(W + ten)
    return c.get(W + "val", default) if c is not None else default


def _an(rpr):
    return tuple(None if rpr is None or rpr.find(W + t) is None else
                 _val(rpr, t, "true") not in ("0", "false", "off")
                 for t in ("vanish", "webHidden"))


def _chong(duoi, tren):
    return tuple(a if b is None else b for a, b in zip(duoi, tren))


class _DocWord:
    def __init__(self, goi, kiem_huy):
        self.goi, self.kiem_huy = goi, kiem_huy
        self.vung, self.maps, self.refs = [], {}, []
        self.tong = self.so_o = 0
        self.styles, self.styles_an = {}, {}
        self.mac_dinh = None
        self.an_mac_dinh = (False, False)

    def _doc_styles(self):
        root = self.goi.cay.get("word/styles.xml")
        if root is None:
            return
        rpr = root.find(W + "docDefaults/" + W + "rPrDefault/" + W + "rPr")
        self.an_mac_dinh = _chong(self.an_mac_dinh, _an(rpr))
        for s in root.findall(W + "style"):
            self.kiem_huy()
            sid = s.get(W + "styleId")
            if sid in self.styles:
                _sai()
            self.styles[sid] = s
            if s.get(W + "type") == "paragraph" and s.get(W + "default") in ("1", "true", "on"):
                if self.mac_dinh is not None:
                    _sai()
                self.mac_dinh = sid
        for sid, s in self.styles.items():
            for t in ("basedOn", "next", "link"):
                ref = _val(s, t)
                if ref is not None and ref not in self.styles:
                    _sai()
            self._style_an(sid, set())

    def _style_an(self, sid, dang_doc):
        if sid is None:
            return (None, None)
        if sid not in self.styles or sid in dang_doc:
            _sai()
        if sid not in self.styles_an:
            self.kiem_huy()
            s = self.styles[sid]
            dang_doc.add(sid)
            try:
                self.styles_an[sid] = _chong(self._style_an(_val(s, "basedOn"), dang_doc), _an(s.find(W + "rPr")))
            finally:
                dang_doc.remove(sid)
        return self.styles_an[sid]

    def _them_vung(self, phan, loai, story, nut, o, manh):
        self.kiem_huy()
        chu, maps, pos = [], [], 0
        for e, v, run, attr, kieu, an, style in manh:
            self.kiem_huy()
            self.tong += len(v.chu)
            if self.tong > KY_TU_VAO_TOI_DA:
                _vuot()
            chu.append(v.chu)
            maps.append(ManhWord(pos, pos + len(v.chu), self.maps[phan][id(e)].duong,
                run, attr, kieu, v.byte_bat_dau, v.byte_ket_thuc, v.byte_ky_tu, an, style))
            pos += len(v.chu)
        vb = "".join(chu)
        self.vung.append(VungWord(len(self.vung), loai, phan, story, nut, o, vb, _bam(vb.encode("utf-8")), tuple(maps)))

    def _doan(self, p, phan, loai, story, o):
        self.kiem_huy()
        ppr = p.find(W + "pPr")
        ps = _val(ppr, "pStyle", self.mac_dinh)
        an_p = _chong(self.an_mac_dinh, self._style_an(ps, set()))
        manh = []
        try:
            for r in p:
                if r.tag != W + "r":
                    continue  # pPr/proofErr đã kiểm cấu trúc, mọi attribute sẽ đi vòng phụ.
                self.kiem_huy()
                rpr = r.find(W + "rPr")
                rs = _val(rpr, "rStyle")
                an_r = _chong(_chong(an_p, self._style_an(rs, set())), _an(rpr))
                rpath = self.maps[phan][id(r)].duong
                for e in r:
                    t = qname(e.tag)[1]
                    m = self.maps[phan][id(e)]
                    if t == "t":
                        v, kieu = m.text, "text"
                    elif t in ("tab", "br", "cr", "noBreakHyphen", "softHyphen", "footnoteReference", "endnoteReference", "footnoteRef", "endnoteRef", "separator", "continuationSeparator"):
                        chu = {"tab": "\t", "br": "\n", "cr": "\n", "noBreakHyphen": "\u2011", "softHyphen": "\u00ad"}.get(t, "\ufffc")
                        v = GiaTriXML(chu, ((m.bat_dau, m.ket_thuc),), m.bat_dau, m.ket_thuc)
                        kieu = "ky_hieu"
                        if t in ("footnoteReference", "endnoteReference"):
                            self.refs.append((t.removesuffix("Reference"), int(e.get(W + "id")), phan, m.duong))
                        if t in ("footnoteRef", "endnoteRef") and story[0] != t.removesuffix("Ref"):
                            _sai()
                    else:
                        continue  # rPr được kiểm, không có nhánh bỏ qua vùng chưa hiểu.
                    manh.append((e, v, rpath, None, kieu, any(an_r), (ps, rs)))
            self._them_vung(phan, loai, story, self.maps[phan][id(p)].duong, o, manh)
        finally:
            manh.clear()

    def _bang(self, tbl, phan, loai, story):
        # Chép chọn lọc _DocNoiDung._bang của TX: vị trí/span/vMerge.
        # Khác TX: giữ mọi ô vật lý và chữ trong ô tiếp nối, không nối qua ô.
        grid = tbl.find(W + "tblGrid")
        so_cot = len(grid) if grid is not None else None
        dang_gop = {}
        for hang, tr in enumerate(tbl.findall(W + "tr")):
            self.kiem_huy()
            cot, gop_tiep = 0, {}
            cells = tr.findall(W + "tc")
            if not cells:
                _sai()
            for tc in cells:
                self.kiem_huy()
                self.so_o += 1
                if self.so_o > SO_O_TOI_DA:
                    _vuot()
                pr = tc.find(W + "tcPr")
                span = int(_val(pr, "gridSpan", "1"))
                vm = None if pr is None else pr.find(W + "vMerge")
                vm = vm.get(W + "val", "continue") if vm is not None else None
                goc = None
                if vm == "continue":
                    goc = dang_gop.get((cot, span))
                    if goc is None:
                        _sai()
                    gop_tiep[(cot, span)] = goc
                elif vm == "restart":
                    gop_tiep[(cot, span)] = (hang, cot)
                if so_cot is not None and cot + span > so_cot:
                    _sai()
                o = ViTriO(self.maps[phan][id(tbl)].duong, hang, cot, span, goc)
                self._khoi(tc, phan, loai, story, o)
                cot += span
            if so_cot is not None and cot != so_cot:
                _sai()
            dang_gop = gop_tiep

    def _khoi(self, container, phan, loai, story, o=None):
        for el in container:
            self.kiem_huy()
            if el.tag == W + "p":
                self._doan(el, phan, loai, story, o)
            elif el.tag == W + "tbl":
                self._bang(el, phan, loai, story)
            # Phần cấu trúc khác đã được kiem_cay_word kiểm kỹ và vòng phụ
            # kiểm mọi attribute; không dùng cảnh báo để thay quét nội dung.

    def _phu(self, phan, root):
        ns, local = qname(root.tag)
        quet = None
        if ns in (CP_NS, EP_NS, CUSTOM_NS):
            loai = {CP_NS: "core", EP_NS: "app", CUSTOM_NS: "custom"}[ns]
            quet = kiem_properties(root, loai, self.kiem_huy)
        for e in root.iter():
            self.kiem_huy()
            m = self.maps[phan][id(e)]
            if quet is not None and (id(e), None) in quet:
                self._them_vung(phan, "thuoc_tinh", ("metadata", None), m.duong, None,
                    [(e, m.text, None, None, "text", False, ())])
            for attr, value in e.attrib.items():
                if ns == W_NS:
                    doc = thuoc_tinh_word(qname(e.tag)[1], attr, value)
                elif ns == A_NS:
                    doc = thuoc_tinh_theme(qname(e.tag)[1], attr, value)
                else:
                    doc = quet is not None and (id(e), attr) in quet
                if doc:
                    self._them_vung(phan, "thuoc_tinh" if quet is not None else "dinh_dang",
                        ("metadata" if quet is not None else "dinh_dang", None), m.duong, None,
                        [(e, m.thuoc_tinh[attr], None, attr, "attribute", False, ())])

    def doc(self):
        cac_note = {"footnote": set(), "endnote": set()}
        self._doc_styles()
        # Chép có sửa vòng story doc_bytes của DC: thân trước, tên OPC sau;
        # không bịa phân trang/toạ độ, không đổi thành một chuỗi nối mọi vùng.
        for phan in sorted(self.goi.cay, key=lambda t: (t != "word/document.xml", t)):
            self.kiem_huy()
            root = self.goi.cay[phan]
            ns, local = qname(root.tag)
            if ns not in (W_NS, A_NS, CP_NS, EP_NS, CUSTOM_NS):
                continue  # CT/relationships chỉ định danh cố định đã kiểm B1.
            if ns == W_NS:
                kiem_cay_word(root, self.kiem_huy)
            elif ns == A_NS:
                kiem_theme(root, self.kiem_huy)
            else:
                kiem_properties(root, {CP_NS: "core", EP_NS: "app", CUSTOM_NS: "custom"}[ns], self.kiem_huy)
            raw = next(p.du_lieu for p in self.goi.zip.phan if p.ten == phan)
            self.maps[phan] = anh_xa_xml(raw, root, self.kiem_huy)
            if local == "document":
                if [e.tag for e in root] != [W + "body"]:
                    _sai()
                self._khoi(root[0], phan, "than", ("than", None))
            elif local in ("hdr", "ftr"):
                loai = "dau_trang" if local == "hdr" else "chan_trang"
                self._khoi(root, phan, loai, (loai, None))
            elif local in ("footnotes", "endnotes"):
                tag = local.removesuffix("s")
                for e in root:
                    ma = int(e.get(W + "id"))
                    if ma in cac_note[tag]:
                        _sai()
                    cac_note[tag].add(ma)
                    self._khoi(e, phan, tag, (tag, ma))
            self._phu(phan, root)
        if any(ma not in cac_note[loai] for loai, ma, _, _ in self.refs):
            _sai()
        self.kiem_huy()
        return TaiLieuWord(1, "unicode_code_point", "word-xml-byte-1",
            _bam(self.goi.zip.goc), self.goi, tuple(self.vung), self.tong, tuple(self.refs))

    def don(self):
        self.vung.clear()
        self.maps.clear()
        self.refs.clear()
        self.styles.clear()
        self.styles_an.clear()


def doc_word(du_lieu, *, kiem_huy):
    """Bytes không tin cậy → reader nội bộ sau toàn bộ cổng B1 và profile B2.

    Không nhận filename/path/MIME làm bằng chứng; không upload, ghi Ngan,
    sinh cờ an toàn hoặc phát hành đầu ra văn bản/tệp.
    """
    goi = doc_tep(du_lieu, kiem_huy=kiem_huy)
    if goi.loai != "docx":
        _sai()
    doc = _DocWord(goi, kiem_huy)
    try:
        return doc.doc()
    finally:
        doc.don()
