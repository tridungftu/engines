"""Cổng nội bộ OOXML MASK-B1; chưa đọc/che/phát hành tệp qua SDK.

Phần ngoài profile bị từ chối cả gói. Cây và bytes chỉ sống trong RAM của
việc; reader/map hai lớp và writer thuộc các lát sau, không có cờ đã che.
"""

from dataclasses import dataclass, field
import json
import posixpath
from types import MappingProxyType

from .zip_an_toan import doc_zip, _kiem_ten, _sai, _vuot
from .xml_an_toan import (
    CP_NS, CT_NS, CUSTOM_NS, DC_NS, DCT_NS, EP_NS, GOC_NS,
    NganSachXML, REL_NS, R_NS, S_NS, VT_NS, W_NS, XML_NS, XSI_NS, doc_xml,
)

KY_TU_RA_TOI_DA = 2000000
BYTE_CHU_RA_TOI_DA = 8 * 1048576
JSON_BAO_CAO_TOI_DA = 256 * 1024
JSON_CHUYEN_TIEP_TOI_DA = 64 * 1024
JSON_KHUON_TOI_DA = 32 * 1024
_CT_REL = "application/vnd.openxmlformats-package.relationships+xml"
_CT_W = "application/vnd.openxmlformats-officedocument.wordprocessingml."
_CT_S = "application/vnd.openxmlformats-officedocument.spreadsheetml."
_CT_CHUNG = "application/vnd.openxmlformats-officedocument."


@dataclass(frozen=True)
class _LoaiPhan:
    loai: str
    content_type: str
    root: str
    namespace: frozenset
    quan_he: str


def _loai(loai, ct, ns, root, qh, *phu):
    return _LoaiPhan(loai, ct, "{" + ns + "}" + root,
                     frozenset((ns, XML_NS, *phu)), qh)


def _danh_so(ten, truoc, sau):
    if not ten.startswith(truoc) or not ten.endswith(sau):
        return False
    so = ten[len(truoc):-len(sau)]
    return (bool(so) and len(so) <= 3 and so.isascii() and so.isdecimal()
            and not so.startswith("0") and int(so) <= 256)


def _loai_phan(ten):
    if ten == "[Content_Types].xml":
        return _loai("khai_bao", "", CT_NS, "Types", "")
    if ten in ("_rels/.rels", "word/_rels/document.xml.rels", "xl/_rels/workbook.xml.rels"):
        return _loai("quan_he", _CT_REL, REL_NS, "Relationships", "")
    if ten == "docProps/core.xml":
        return _loai("core", "application/vnd.openxmlformats-package.core-properties+xml",
                     CP_NS, "coreProperties", GOC_NS + "package/2006/relationships/metadata/core-properties",
                     DC_NS, DCT_NS, XSI_NS)
    if ten == "docProps/app.xml":
        return _loai("app", _CT_CHUNG + "extended-properties+xml", EP_NS,
                     "Properties", R_NS + "/extended-properties", VT_NS)
    if ten == "docProps/custom.xml":
        return _loai("custom", _CT_CHUNG + "custom-properties+xml", CUSTOM_NS,
                     "Properties", R_NS + "/custom-properties", VT_NS)
    if ten == "word/document.xml":
        return _loai("word", _CT_W + "document.main+xml", W_NS, "document",
                     R_NS + "/officeDocument", R_NS)
    for loai, root in (("styles", "styles"), ("numbering", "numbering"),
                       ("settings", "settings"), ("fontTable", "fonts"),
                       ("webSettings", "webSettings"), ("footnotes", "footnotes"),
                       ("endnotes", "endnotes")):
        if ten == "word/" + loai + ".xml":
            return _loai("word", _CT_W + loai + "+xml", W_NS, root, R_NS + "/" + loai, R_NS)
    for loai, root in (("header", "hdr"), ("footer", "ftr")):
        if _danh_so(ten, "word/" + loai, ".xml"):
            return _loai("word", _CT_W + loai + "+xml", W_NS, root, R_NS + "/" + loai, R_NS)
    if ten == "xl/workbook.xml":
        return _loai("excel", _CT_S + "sheet.main+xml", S_NS, "workbook",
                     R_NS + "/officeDocument", R_NS)
    for loai, root in (("styles", "styleSheet"), ("sharedStrings", "sst")):
        if ten == "xl/" + loai + ".xml":
            return _loai("excel", _CT_S + loai + "+xml", S_NS, root, R_NS + "/" + loai, R_NS)
    if _danh_so(ten, "xl/worksheets/sheet", ".xml"):
        return _loai("excel", _CT_S + "worksheet+xml", S_NS, "worksheet", R_NS + "/worksheet", R_NS)
    # Theme chưa có phân loại attribute/text và map inverse trong B1.
    _sai()


_WORD = frozenset("""
document body hdr ftr footnotes footnote endnotes endnote footnoteReference
endnoteReference footnoteRef endnoteRef separator continuationSeparator
p r t tab br cr noBreakHyphen softHyphen tbl tr tc tblPr tblPrEx tblGrid
gridCol pPr rPr trPr tcPr sectPr pgSz pgMar pgNumType cols col docGrid
titlePg headerReference footerReference numPr ilvl numId pStyle rStyle b bCs
i iCs u strike dstrike vanish webHidden color sz szCs rFonts highlight
spacing position vertAlign lang rtl cs caps smallCaps emboss imprint
outline shadow snapToGrid kern w fitText jc ind tabs contextualSpacing
keepNext keepLines pageBreakBefore widowControl suppressLineNumbers
suppressAutoHyphens bidi adjustRightInd mirrorIndents textAlignment
tblW tblInd tblLayout tblLook tblBorders top left bottom right insideH insideV
tblCellMar tcMar tcW gridSpan vMerge vAlign cantSplit tblHeader trHeight
styles docDefaults rPrDefault pPrDefault style name basedOn next link
uiPriority qFormat hidden semiHidden unhideWhenUsed locked
numbering abstractNum num multiLevelType lvl start numFmt lvlText lvlJc suff
abstractNumId lvlOverride startOverride
settings zoom defaultTabStop evenAndOddHeaders defaultTableStyle
characterSpacingControl compat compatSetting themeFontLang clrSchemeMapping
doNotTrackMoves doNotTrackFormatting updateFields
fonts font altName panose1 charset family pitch sig
webSettings optimizeForBrowser allowPNG doNotSaveAsSingleFile
""".split())
_ATTR_WORD = frozenset("""
val id type w h orient code top right bottom left header footer gutter
space line lineRule before after beforeAutospacing afterAutospacing
ascii hAnsi eastAsia cs asciiTheme hAnsiTheme eastAsiaTheme cstheme
hint sz szCs b i strike color fill themeColor themeTint themeShade
themeFill themeFillTint themeFillShade numId ilvl start end firstLine hanging
firstLineChars hangingChars leftChars rightChars num space autoSep numStart
styleId default customStyle abstractNumId nsid tplc tentative restart
ascii hAnsi eastAsia cs majorHAnsi minorHAnsi bidi complexScript
embedRegular embedBold embedItalic embedBoldItalic pitch panose1
usb0 usb1 usb2 usb3 csb0 csb1 percent uri name
""".split())
_EXCEL = frozenset("""
workbook fileVersion workbookPr bookViews workbookView sheets sheet calcPr
worksheet sheetPr tabColor outlinePr pageSetUpPr dimension sheetViews
sheetView pane selection sheetFormatPr cols col sheetData row c v is t
sst si r rPr rFont b i u strike outline shadow condense extend color sz
family charset scheme vertAlign phoneticPr
styleSheet numFmts numFmt fonts font fills fill patternFill fgColor bgColor
borders border left right top bottom diagonal vertical horizontal
cellStyleXfs cellXfs xf alignment protection cellStyles cellStyle
dxfs dxf tableStyles colors indexedColors rgbColor mruColors
mergeCells mergeCell sheetProtection protectedRanges protectedRange
autoFilter filterColumn filters filter customFilters customFilter
printOptions pageMargins pageSetup headerFooter oddHeader oddFooter
evenHeader evenFooter firstHeader firstFooter rowBreaks colBreaks brk
ignoredErrors ignoredError
""".split())
_ATTR_EXCEL = frozenset("""
appName lastEdited lowestEdited rupBuild codeName date1904 showObjects
updateLinks filterPrivacy defaultThemeVersion windowWidth windowHeight
xWindow yWindow activeTab firstSheet tabRatio visibility minimized showSheetTabs
name sheetId state id calcId fullCalcOnLoad forceFullCalc calcMode ref
tabSelected workbookViewId showGridLines showRowColHeaders showZeros
rightToLeft zoomScale zoomScaleNormal topLeftCell view colorId activePane
xSplit ySplit sqref activeCell activeCellId baseColWidth defaultColWidth
defaultRowHeight customHeight zeroHeight outlineLevelRow outlineLevelCol
min max width style hidden bestFit customWidth outlineLevel collapsed phonetic
r s t cm vm spans ht customFormat thickTop thickBot
count uniqueCount val rgb indexed auto theme tint type patternType
numFmtId formatCode fontId fillId borderId xfId applyNumberFormat applyFont
applyFill applyBorder applyAlignment applyProtection pivotButton quotePrefix
horizontal vertical textRotation wrapText shrinkToFit indent relativeIndent
justifyLastLine readingOrder locked hidden builtinId customBuiltin
tableStyleId defaultTableStyle defaultPivotStyle diagonalUp diagonalDown
differentFirst differentOddEven scaleWithDoc alignWithMargins
left right top bottom header footer paperSize scale orientation fitToWidth
fitToHeight firstPageNumber useFirstPageNumber horizontalDpi verticalDpi
copies blackAndWhite draft cellComments errors usePrinterDefaults
horizontalCentered verticalCentered headings gridLines gridLinesSet
manualBreakCount id min max man pt evalError twoDigitTextNumber numberStoredAsText
formula formulaRange emptyCellReference unlockedFormula calculatedColumn
algorithmName hashValue saltValue spinCount password sheet objects scenarios
selectLockedCells selectUnlockedCells formatCells formatColumns formatRows
insertColumns insertRows insertHyperlinks deleteColumns deleteRows sort
autoFilter pivotTables colId blank val operator and
""".split())


def _qname(ten):
    if ten.startswith("{"):
        return ten[1:].split("}", 1)
    return "", ten


def _kiem_node(root, spec, kiem_huy):
    if root.tag != spec.root:
        _sai()
    for e in root.iter():
        kiem_huy()
        ns, ten = _qname(e.tag)
        if spec.loai == "word" and (ns != W_NS or ten not in _WORD):
            _sai()
        if spec.loai == "excel" and (ns != S_NS or ten not in _EXCEL):
            _sai()
        if spec.loai == "excel" and ten == "sheet" and e.get("state", "visible") != "visible":
            _sai()
        if spec.loai == "excel" and ten == "c" and e.get("t") == "str":
            _sai()  # Kiểu chuỗi cache của công thức, không phải inline/shared string.
        # Chỉ relationship id tại các node thực sự có nghĩa trong profile.
        for attr, gia_tri in e.attrib.items():
            ans, a = _qname(attr)
            if ans == XML_NS:
                if a != "space" or gia_tri not in ("default", "preserve"):
                    _sai()
            elif ans == R_NS:
                if a != "id" or (ns, ten) not in {
                        (W_NS, "headerReference"), (W_NS, "footerReference"), (S_NS, "sheet")}:
                    _sai()
            elif spec.loai == "word":
                if ans != W_NS or a not in _ATTR_WORD:
                    _sai()
            elif spec.loai == "excel":
                if ans or a not in _ATTR_EXCEL:
                    _sai()
    if spec.loai in ("core", "app", "custom"):
        _kiem_thuoc_tinh(root, spec, kiem_huy)


def _kiem_thuoc_tinh(root, spec, kiem_huy):
    cho = {
        CP_NS: {"coreProperties", "category", "contentStatus", "created", "creator",
                "description", "identifier", "keywords", "language", "lastModifiedBy",
                "lastPrinted", "modified", "revision", "subject", "title", "version"},
        DC_NS: {"title", "subject", "creator", "description", "identifier", "language"},
        DCT_NS: {"created", "modified"},
        EP_NS: set("Properties Template Manager Company Pages Words Characters PresentationFormat Lines Paragraphs Slides Notes TotalTime HiddenSlides MMClips ScaleCrop HeadingPairs TitlesOfParts LinksUpToDate CharactersWithSpaces SharedDoc HyperlinkBase HyperlinksChanged Application AppVersion DocSecurity".split()),
        CUSTOM_NS: {"Properties", "property"},
        VT_NS: set("vector variant lpstr lpwstr bstr i1 i2 i4 i8 int ui1 ui2 ui4 ui8 uint r4 r8 decimal bool date filetime".split()),
    }
    for e in root.iter():
        kiem_huy()
        ns, local = _qname(e.tag)
        if local not in cho.get(ns, set()):
            _sai()
        if local in ("HyperlinkBase", "LinksUpToDate", "HyperlinksChanged"):
            _sai()
        for attr, value in e.attrib.items():
            ans, a = _qname(attr)
            if (ans, a) == (XSI_NS, "type") and value == "dcterms:W3CDTF" and ns == DCT_NS:
                continue
            if ns == CUSTOM_NS and local == "property" and not ans and a in ("fmtid", "pid", "name"):
                continue
            if ns == VT_NS and local == "vector" and not ans and a in ("baseType", "size"):
                continue
            _sai()


def _rong_cau_truc(e):
    if len(e) or e.text and e.text.strip() or e.tail and e.tail.strip():
        _sai()


def _kieu_noi_dung(cay, loai):
    root = cay["[Content_Types].xml"]
    if root.attrib or root.text and root.text.strip():
        _sai()
    mac_dinh, rieng = {}, {}
    for e in root:
        _rong_cau_truc(e)
        if e.tag == "{" + CT_NS + "}Default" and set(e.attrib) == {"Extension", "ContentType"}:
            k, v = e.get("Extension"), e.get("ContentType")
            if k not in ("rels", "xml") or v != {"rels": _CT_REL, "xml": "application/xml"}[k] or k in mac_dinh:
                _sai()
            mac_dinh[k] = v
        elif e.tag == "{" + CT_NS + "}Override" and set(e.attrib) == {"PartName", "ContentType"}:
            k, v = e.get("PartName", ""), e.get("ContentType")
            if not k.startswith("/") or k[1:] not in loai or k == "/[Content_Types].xml" or k in rieng:
                _sai()
            rieng[k] = v
        else:
            _sai()
    for ten, spec in loai.items():
        if ten == "[Content_Types].xml":
            continue
        if rieng.get("/" + ten, mac_dinh.get(ten.rsplit(".", 1)[-1])) != spec.content_type:
            _sai()


def _chu_quan_he(ten):
    return {"_rels/.rels": "", "word/_rels/document.xml.rels": "word/document.xml",
            "xl/_rels/workbook.xml.rels": "xl/workbook.xml"}[ten]


def _quan_he(cay, loai, chinh, kiem_huy):
    ds, tep_qh = {}, {}
    for ten, spec in loai.items():
        if spec.loai != "quan_he":
            continue
        chu = _chu_quan_he(ten)
        if chu and chu != chinh:
            _sai()
        root = cay[ten]
        if root.attrib or root.text and root.text.strip():
            _sai()
        muc, da_co = {}, set()
        ds[chu], tep_qh[chu] = muc, ten
        for e in root:
            kiem_huy()
            _rong_cau_truc(e)
            if (e.tag != "{" + REL_NS + "}Relationship" or
                    set(e.attrib) not in ({"Id", "Type", "Target"}, {"Id", "Type", "Target", "TargetMode"})
                    or e.get("TargetMode", "Internal") != "Internal"):
                _sai()
            rid, target, kieu = e.get("Id", ""), e.get("Target", ""), e.get("Type", "")
            if not _danh_so(rid + ".x", "rId", ".x") or rid in muc:
                _sai()
            _kiem_ten(target)
            dich = posixpath.join(posixpath.dirname(chu), target)
            if dich not in loai or dich in da_co or not loai[dich].quan_he or kieu != loai[dich].quan_he:
                _sai()
            if chu == "":
                if dich != chinh and loai[dich].loai not in ("core", "app", "custom"):
                    _sai()
            elif dich == chinh or not dich.startswith(posixpath.dirname(chinh) + "/"):
                _sai()
            da_co.add(dich)
            muc[rid] = (kieu, dich)
    main = [v for v in ds.get("", {}).values() if v[0] == R_NS + "/officeDocument"]
    if main != [(R_NS + "/officeDocument", chinh)]:
        _sai()
    # Mọi part phải đi tới được từ package, kể cả part không có text nhìn thấy.
    da_doc, cho = {"[Content_Types].xml"}, [""]
    while cho:
        kiem_huy()
        chu = cho.pop()
        if chu in tep_qh:
            da_doc.add(tep_qh[chu])
        for _, dich in ds.get(chu, {}).values():
            if dich not in da_doc:
                da_doc.add(dich)
                cho.append(dich)
    if da_doc != set(loai):
        _sai()
    da_dung = set()
    for ten, root in cay.items():
        for e in root.iter():
            kiem_huy()
            for attr, rid in e.attrib.items():
                if attr == "{" + R_NS + "}id":
                    qh = ds.get(ten, {}).get(rid)
                    if qh is None:
                        _sai()
                    kieu = {"headerReference": "header", "footerReference": "footer", "sheet": "worksheet"}.get(_qname(e.tag)[1])
                    if qh[0] != R_NS + "/" + str(kieu):
                        _sai()
                    da_dung.add((ten, rid))
    for chu, muc in ds.items():
        for rid, (kieu, _) in muc.items():
            if kieu.rsplit("/", 1)[-1] in ("header", "footer", "worksheet") and (chu, rid) not in da_dung:
                _sai()
    return ds


def _kiem_chu_dung_lai(cay, ngan_sach, kiem_huy):
    """Không dùng một shared string để né tổng nội dung ở nhiều ô thật."""
    root = cay.get("xl/sharedStrings.xml")
    chu = [] if root is None else ["".join(e.itertext()) for e in root]
    for ten, sheet in cay.items():
        if not ten.startswith("xl/worksheets/"):
            continue
        for e in sheet.iter("{" + S_NS + "}c"):
            kiem_huy()
            if e.get("t") == "s":
                v = e.find("{" + S_NS + "}v")
                so = "" if v is None else v.text or ""
                if not so or not so.isascii() or not so.isdecimal() or len(so) > 6 or int(so) >= len(chu):
                    _sai()
                ngan_sach.them_chu(len(chu[int(so)]))


@dataclass(frozen=True, repr=False)
class GoiTep:
    loai: str
    zip: object = field(repr=False)
    cay: object = field(repr=False)
    quan_he: object = field(repr=False)
    thong_ke: object = field(repr=False)


def doc_tep(du_lieu, *, kiem_huy):
    """Kiểm mọi part/graph trước trả đối tượng nội bộ; không nhận MIME/tên máy."""
    goi = doc_zip(du_lieu, kiem_huy)
    loai, cay = {}, {}
    try:
        for p in goi.phan:
            kiem_huy()
            loai[p.ten] = _loai_phan(p.ten)
        if not {"[Content_Types].xml", "_rels/.rels"} <= set(loai):
            _sai()
        chinh = [t for t in ("word/document.xml", "xl/workbook.xml") if t in loai]
        if len(chinh) != 1:
            _sai()
        chinh = chinh[0]
        if any(t.startswith("xl/" if chinh.startswith("word/") else "word/") for t in loai):
            _sai()
        ngan_sach = NganSachXML()
        for p in goi.phan:
            spec = loai[p.ten]
            root = doc_xml(p.du_lieu, namespace=spec.namespace, ngan_sach=ngan_sach, kiem_huy=kiem_huy)
            _kiem_node(root, spec, kiem_huy)
            cay[p.ten] = root
        _kieu_noi_dung(cay, loai)
        qh = _quan_he(cay, loai, chinh, kiem_huy)
        _kiem_chu_dung_lai(cay, ngan_sach, kiem_huy)
        kiem_huy()
        return GoiTep("docx" if chinh.startswith("word/") else "xlsx", goi,
                      MappingProxyType(dict(cay)),
                      MappingProxyType({k: MappingProxyType(v) for k, v in qh.items()}),
                      MappingProxyType({"so_nut": ngan_sach.so_nut, "so_ky_tu": ngan_sach.so_ky_tu,
                                        "so_sheet": ngan_sach.so_sheet, "so_o": ngan_sach.so_o}))
    finally:
        loai.clear()
        cay.clear()


def kiem_van_ban_ra(chu, *, kiem_huy):
    if type(chu) is not str:
        _sai()
    if len(chu) > KY_TU_RA_TOI_DA:
        _vuot()
    so_byte = 0
    for pos in range(0, len(chu), 8192):
        kiem_huy()
        try:
            so_byte += len(chu[pos:pos + 8192].encode("utf-8"))
        except UnicodeError:
            _sai()
        kiem_byte_chu_ra(so_byte)
    kiem_huy()


def kiem_byte_chu_ra(so_byte):
    if so_byte > BYTE_CHU_RA_TOI_DA:
        _vuot()


def ma_hoa_json_noi_bo(gia_tri, *, loai, kiem_huy):
    """Chép iterencode có đếm từ wrapper ZIP; trần riêng báo cáo/chuyển tiếp/khuôn."""
    tran = {"bao_cao": JSON_BAO_CAO_TOI_DA, "chuyen_tiep": JSON_CHUYEN_TIEP_TOI_DA,
            "khuon": JSON_KHUON_TOI_DA}.get(loai)
    if tran is None:
        _sai()
    # Không để encoder cấp phát một token khổng lồ hoặc vòng tham chiếu.
    dang_doc, toi_thieu = set(), [0]

    def kiem(v, sau):
        kiem_huy()
        if sau > 64:
            _vuot()
        toi_thieu[0] += len(v) if isinstance(v, str) else 1
        if toi_thieu[0] > tran:
            _vuot()
        if isinstance(v, (dict, list, tuple)):
            if id(v) in dang_doc:
                _sai()
            if len(v) > tran:
                _vuot()
            dang_doc.add(id(v))
            try:
                if isinstance(v, dict):
                    for k, x in v.items():
                        if type(k) is not str:
                            _sai()
                        kiem(k, sau + 1)
                        kiem(x, sau + 1)
                else:
                    for x in v:
                        kiem(x, sau + 1)
            finally:
                dang_doc.remove(id(v))

    kiem(gia_tri, 0)
    dem = bytearray()
    encoder = json.JSONEncoder(ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    try:
        iterator = encoder.iterencode(gia_tri)
        while True:
            kiem_huy()
            try:
                chunk = next(iterator)
            except StopIteration:
                break
            except (ValueError, TypeError, RecursionError):
                _sai()
            try:
                data = chunk.encode("utf-8")
            except UnicodeError:
                _sai()
            if len(dem) + len(data) > tran:
                _vuot()
            dem.extend(data)
        kiem_huy()
        return bytes(dem)
    finally:
        dem.clear()


# MASK-B3: khối Excel riêng để lead gộp độc lập với reader Word MASK-B2.
@dataclass(frozen=True, repr=False)
class PhanZipExcel:
    """le_cuoi là cuối payload; cuối local record gồm cả descriptor nếu có."""

    phan: object = field(repr=False)
    le_cuoi_ban_ghi: int
    co: int


@dataclass(frozen=True, repr=False)
class GoiExcel:
    goi: GoiTep = field(repr=False)
    ban_ghi: tuple[PhanZipExcel, ...] = field(repr=False)


def _doc_zip_excel(raw, kiem_huy):
    """Dùng tiền kiểm/giải nén B1; kiểm thêm cờ nén và descriptor Office.

    Không sửa bytes đầu vào hoặc thay cổng B1 toàn cục. B4 phải chép local
    record tới le_cuoi_ban_ghi, không nhầm descriptor là payload DEFLATE.
    """
    import struct
    from . import zip_an_toan as z

    le, so = z._kiem_danh_muc(raw, kiem_huy)
    muc, ban_ghi, da_co, tong, pos = [], [], set(), 0, le
    try:
        for _ in range(so):
            kiem_huy()
            (_, tao, can, co, cach, gio, ngay, crc, nen, dai,
             n, x, c, dia, noi_bo, ngoai, dau) = struct.unpack_from('<4s6H3I5H2I', raw, pos)
            if co & ~0x80e or (cach != 8 and co & 6):
                _sai()
            z._kiem_header(tao, can, co & 0x800, cach, gio, ngay, dia, noi_bo, ngoai)
            if 0xffffffff in (nen, dai, dau):
                _sai()
            tong += dai
            if (dai > z.PHAN_TOI_DA or tong > z.TONG_GIAI_NEN_TOI_DA
                    or dai > z.TY_LE_TOI_DA * nen):
                _vuot()
            if cach == 0 and nen != dai:
                _sai()
            ten_byte = raw[pos + 46:pos + 46 + n]
            try:
                ten = ten_byte.decode('utf-8' if co & 0x800 else 'ascii')
            except UnicodeError:
                _sai()
            chuan = z._kiem_ten(ten)
            if len(ten) > 256 or chuan in da_co:
                _sai()
            da_co.add(chuan)
            if dau + 30 > le or raw[dau:dau + 4] != b'PK\x03\x04':
                _sai()
            (_, lc, lf, lm, lt, ld, lcrc, ln, ls, lten, lx) = struct.unpack_from('<4s5H3I2H', raw, dau)
            if (lc, lf, lm, lt, ld, lten, lx) != (can, co, cach, gio, ngay, n, 0):
                _sai()
            if (lcrc, ln, ls) not in (((0, 0, 0), (crc, nen, dai)) if co & 8 else ((crc, nen, dai),)):
                _sai()
            bat_dau, het = dau + 30 + n, dau + 30 + n + nen
            if het > le or raw[dau + 30:bat_dau] != ten_byte:
                _sai()
            cuoi = het
            if co & 8:
                # Descriptor cổ điển: có/không chữ ký; cả CRC và hai size phải khớp.
                if raw[het:het + 4] == b'PK\x07\x08':
                    cuoi += 4
                if cuoi + 12 > le or struct.unpack_from('<3I', raw, cuoi) != (crc, nen, dai):
                    _sai()
                cuoi += 12
            p = z.PhanZip(ten, cach, crc, nen, dai, dau, bat_dau, het, pos, pos + 46 + n)
            muc.append(p)
            ban_ghi.append(PhanZipExcel(p, cuoi, co))
            pos += 46 + n
        cuoi = 0
        for b in sorted(ban_ghi, key=lambda b: b.phan.le_dau):
            kiem_huy()
            if b.phan.le_dau != cuoi:
                _sai()
            cuoi = b.le_cuoi_ban_ghi
        if cuoi != le:
            _sai()
        ds, thuc = [], [0]
        for p in muc:
            data = z._giai_nen(raw, p, thuc, kiem_huy)
            ds.append(z.PhanZip(p.ten, p.phuong_thuc, p.crc, p.so_byte_nen,
                               p.so_byte, p.le_dau, p.le_du_lieu, p.le_cuoi,
                               p.le_danh_muc, p.cuoi_danh_muc, data))
        kiem_huy()
        return z.GoiZip(raw, tuple(ds), le), tuple(ban_ghi)
    finally:
        muc.clear()
        ban_ghi.clear()


def doc_goi_excel(du_lieu, *, kiem_huy):
    """Cổng B1 mở rộng có kiểm cho B3, chưa thay reader ngữ nghĩa Excel."""
    from .xml_an_toan import A_NS

    zip_goi, ban_ghi = _doc_zip_excel(du_lieu, kiem_huy)
    loai, cay = {}, {}
    try:
        for p in zip_goi.phan:
            kiem_huy()
            if p.ten == 'xl/theme/theme1.xml':
                spec = _loai('theme', _CT_CHUNG + 'theme+xml', A_NS, 'theme', R_NS + '/theme')
            elif p.ten == 'xl/calcChain.xml':
                spec = _loai('calcChain', _CT_S + 'calcChain+xml', S_NS, 'calcChain', R_NS + '/calcChain')
            else:
                spec = _loai_phan(p.ten)
            if p.ten.startswith('word/'):
                _sai()
            loai[p.ten] = spec
        if not {'[Content_Types].xml', '_rels/.rels', 'xl/workbook.xml',
                'xl/_rels/workbook.xml.rels'} <= set(loai):
            _sai()
        ngan_sach = NganSachXML()
        for p in zip_goi.phan:
            spec = loai[p.ten]
            root = doc_xml(p.du_lieu, namespace=spec.namespace,
                           ngan_sach=ngan_sach, kiem_huy=kiem_huy)
            if root.tag != spec.root:
                _sai()
            cay[p.ten] = root
        _kieu_noi_dung(cay, loai)
        qh = _quan_he(cay, loai, 'xl/workbook.xml', kiem_huy)
        kiem_huy()
        goi = GoiTep('xlsx', zip_goi, MappingProxyType(dict(cay)),
                     MappingProxyType({k: MappingProxyType(v) for k, v in qh.items()}),
                     MappingProxyType({'so_nut': ngan_sach.so_nut,
                                       'so_ky_tu': ngan_sach.so_ky_tu,
                                       'so_sheet': ngan_sach.so_sheet, 'so_o': ngan_sach.so_o}))
        return GoiExcel(goi, ban_ghi)
    finally:
        loai.clear()
        cay.clear()
