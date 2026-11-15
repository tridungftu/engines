"""Profile Word nội bộ B2 và map lexical sau cổng XML B1.

Parser B1 quyết định XML hợp lệ. Bộ đi byte dưới đây chỉ định vị trên XML
đã parse, đối chiếu lại từng giá trị; không thay parser bằng regex.
Không chuẩn hóa NFC/Cf, không serialize lại XML, không I/O.
"""

from dataclasses import dataclass, field
import re
from types import MappingProxyType

from .xml_an_toan import (
    A_NS, CP_NS, CUSTOM_NS, DC_NS, DCT_NS, EP_NS, R_NS, VT_NS,
    W_NS, XML_NS, XSI_NS,
)
from .zip_an_toan import _sai

W = "{" + W_NS + "}"
A = "{" + A_NS + "}"
BOOL = frozenset(("0", "1", "true", "false", "on", "off"))
STYLE = frozenset(("Normal", "DefaultParagraphFont", "TableNormal", "NoList",
    "Strong", "Emphasis", "Title", "Subtitle", "ListParagraph", "BodyText",
    "Caption", "Header", "Footer", "FootnoteText", "EndnoteText",
    "FootnoteReference", "EndnoteReference", "Hyperlink", "TableGrid",
    *("Heading" + str(i) for i in range(1, 10))))
FONT = frozenset(("", "Arial", "Arial Unicode MS", "Calibri", "Calibri Light",
    "Cambria", "Cambria Math", "Times New Roman", "Courier New", "Symbol",
    "Wingdings", "Segoe UI", "Tahoma", "Verdana", "Aptos", "Aptos Display",
    "ＭＳ ゴシック", "ＭＳ 明朝", "MS Gothic", "MS Mincho", "Yu Gothic",
    "Yu Mincho", "游ゴシック", "游明朝", "宋体", "SimSun", "新細明體",
    "PMingLiU", "MingLiU", "Malgun Gothic", "맑은 고딕", "Gulim", "굴림",
    "Batang", "바탕", "Microsoft YaHei", "Microsoft JhengHei", "DengXian",
    "等线", "Arial Narrow", "Angsana New", "Cordia New", "Mangal", "Vrinda",
    "Latha", "Raavi", "Shruti", "Tunga", "Gautami", "Kartika", "DaunPenh",
    "DokChampa", "Iskoola Pota", "Nyala", "Plantagenet Cherokee", "Ebrima",
    "Sylfaen", "Estrangelo Edessa", "Microsoft Himalaya", "Microsoft Yi Baiti",
    "Microsoft Uighur", "Nirmala UI", "Leelawadee UI", "Noto Sans"))
_LANG = frozenset(("vi-VN", "en-US", "en-GB", "fr-FR", "de-DE", "ja-JP",
                    "zh-CN", "zh-TW", "ko-KR", "ar-SA", "th-TH", "ru-RU"))


def qname(ten):
    return ten[1:].split("}", 1) if ten.startswith("{") else ("", ten)


def _enum(*ds):
    return lambda v: v in ds


def _so(v):
    return bool(re.fullmatch(r"-?[0-9]{1,10}", v)) and abs(int(v)) <= 2147483647


def _hex(n):
    return lambda v: bool(re.fullmatch("[0-9A-Fa-f]{" + str(n) + "}", v))


def _chu(v):
    return True  # Có map và bắt buộc qua hai lớp ở các lát sau, không bất biến.


_MAU = _enum("auto", "black", "blue", "cyan", "green", "magenta", "red",
    "yellow", "white", "darkBlue", "darkCyan", "darkGreen", "darkMagenta",
    "darkRed", "darkYellow", "darkGray", "lightGray", "none")
_THEME = _enum("dark1", "light1", "dark2", "light2", "accent1", "accent2",
    "accent3", "accent4", "accent5", "accent6", "hyperlink", "followedHyperlink",
    "background1", "text1", "background2", "text2", "none")
_ONOFF = set("b bCs i iCs strike dstrike vanish webHidden rtl cs caps smallCaps emboss imprint outline shadow snapToGrid contextualSpacing keepNext keepLines pageBreakBefore widowControl suppressLineNumbers suppressAutoHyphens bidi adjustRightInd mirrorIndents titlePg cantSplit tblHeader qFormat hidden semiHidden unhideWhenUsed locked autoRedefine personal personalCompose personalReply doNotTrackMoves doNotTrackFormatting updateFields evenAndOddHeaders optimizeForBrowser allowPNG doNotSaveAsSingleFile noProof suppressOverlap".split())
_RPR = set("rStyle rFonts b bCs i iCs u strike dstrike vanish webHidden color sz szCs highlight spacing position vertAlign lang rtl cs caps smallCaps emboss imprint outline shadow snapToGrid kern w fitText noProof".split())
_PPR = set("pStyle numPr rPr sectPr spacing jc ind tabs contextualSpacing keepNext keepLines pageBreakBefore widowControl suppressLineNumbers suppressAutoHyphens bidi adjustRightInd mirrorIndents textAlignment".split())
_BORDER = set("top left bottom right insideH insideV".split())
_CELL = set("tcW gridSpan vMerge vAlign tcMar tcBorders shd noWrap".split())
_TABLE = set("tblW tblInd tblLayout tblLook tblBorders tblCellMar tblStyle jc".split())
_CON = {
    "document": {"body"}, "body": {"p", "tbl", "sectPr"},
    "hdr": {"p", "tbl"}, "ftr": {"p", "tbl"},
    "footnotes": {"footnote"}, "endnotes": {"endnote"},
    "footnote": {"p", "tbl"}, "endnote": {"p", "tbl"},
    "p": {"pPr", "r", "proofErr"},
    "r": {"rPr", "t", "tab", "br", "cr", "noBreakHyphen", "softHyphen",
          "footnoteReference", "endnoteReference", "footnoteRef", "endnoteRef",
          "separator", "continuationSeparator"},
    "pPr": _PPR, "rPr": _RPR,
    "tbl": {"tblPr", "tblGrid", "tr"}, "tr": {"tblPrEx", "trPr", "tc"},
    "tc": {"tcPr", "p", "tbl"}, "tblPr": _TABLE, "tblPrEx": _TABLE,
    "trPr": {"cantSplit", "tblHeader", "trHeight"}, "tcPr": _CELL,
    "tblGrid": {"gridCol"}, "tblBorders": _BORDER, "tcBorders": _BORDER,
    "tblCellMar": {"top", "left", "bottom", "right"},
    "tcMar": {"top", "left", "bottom", "right"},
    "sectPr": set("headerReference footerReference pgSz pgMar pgNumType cols docGrid titlePg type".split()),
    "cols": {"col"}, "tabs": {"tab"}, "numPr": {"ilvl", "numId"},
    "styles": {"docDefaults", "latentStyles", "style"},
    "docDefaults": {"rPrDefault", "pPrDefault"}, "rPrDefault": {"rPr"},
    "pPrDefault": {"pPr"}, "latentStyles": {"lsdException"},
    "style": set("name aliases basedOn next link uiPriority qFormat hidden semiHidden unhideWhenUsed locked autoRedefine personal personalCompose personalReply rPr pPr tblPr tcPr trPr".split()),
    "numbering": {"abstractNum", "num", "numIdMacAtCleanup"},
    "abstractNum": {"nsid", "multiLevelType", "tmpl", "lvl"},
    "num": {"abstractNumId", "lvlOverride"}, "lvlOverride": {"startOverride", "lvl"},
    "lvl": {"start", "numFmt", "lvlText", "lvlJc", "suff", "pPr", "rPr", "lvlRestart"},
    "settings": set("zoom defaultTabStop evenAndOddHeaders defaultTableStyle characterSpacingControl compat themeFontLang clrSchemeMapping doNotTrackMoves doNotTrackFormatting updateFields proofState rsids".split()),
    "compat": {"compatSetting"}, "rsids": {"rsidRoot", "rsid"},
    "fonts": {"font"}, "font": {"altName", "panose1", "charset", "family", "pitch", "sig"},
    "webSettings": {"optimizeForBrowser", "allowPNG", "doNotSaveAsSingleFile"},
}
_ATTR = {t: {"val": lambda v: v in BOOL} for t in _ONOFF}
_ATTR.update({t: {"val": _so} for t in set("sz szCs kern position ilvl numId abstractNumId start startOverride uiPriority defaultTabStop numIdMacAtCleanup lvlRestart".split())})
_ATTR.update({t: {"val": _chu} for t in ("name", "aliases", "lvlText")})
_ATTR.update({t: {"val": lambda v: v in STYLE} for t in ("pStyle", "rStyle", "tblStyle", "basedOn", "next", "link", "defaultTableStyle")})
_ATTR.update({
    "style": {"styleId": lambda v: v in STYLE, "type": _enum("paragraph", "character", "table", "numbering"), "default": lambda v: v in BOOL, "customStyle": lambda v: v in BOOL},
    "latentStyles": {k: (lambda v: v in BOOL) for k in ("defLockedState", "defSemiHidden", "defUnhideWhenUsed", "defQFormat")},
    "lsdException": {"name": _chu, **{k: (lambda v: v in BOOL) for k in ("locked", "semiHidden", "unhideWhenUsed", "qFormat")}, "uiPriority": _so},
    "rFonts": {**{k: (lambda v: v in FONT) for k in ("ascii", "hAnsi", "eastAsia", "cs")}, **{k: _enum("majorAscii", "majorHAnsi", "majorEastAsia", "majorBidi", "minorAscii", "minorHAnsi", "minorEastAsia", "minorBidi") for k in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme")}, "hint": _enum("default", "eastAsia", "cs")},
    "font": {"name": lambda v: v in FONT and bool(v)}, "altName": {"val": lambda v: v in FONT},
    "panose1": {"val": _hex(20)}, "charset": {"val": _hex(2)},
    "family": {"val": _enum("auto", "decorative", "modern", "roman", "script", "swiss")},
    "pitch": {"val": _enum("default", "fixed", "variable")},
    "sig": {k: _hex(8) for k in ("usb0", "usb1", "usb2", "usb3", "csb0", "csb1")},
    "lang": {k: (lambda v: v in _LANG) for k in ("val", "eastAsia", "bidi")},
    "themeFontLang": {k: (lambda v: v in _LANG) for k in ("val", "eastAsia", "bidi")},
    "color": {"val": lambda v: v == "auto" or _hex(6)(v), "themeColor": _THEME, "themeTint": _hex(2), "themeShade": _hex(2)},
    "highlight": {"val": _MAU}, "u": {"val": _enum("none", "single", "double", "words", "thick", "dotted", "dash", "wave"), "color": lambda v: v == "auto" or _hex(6)(v)},
    "spacing": {k: _so for k in ("val", "before", "after", "line", "beforeLines", "afterLines")},
    "vertAlign": {"val": _enum("baseline", "superscript", "subscript")},
    "jc": {"val": _enum("start", "end", "left", "right", "center", "both", "distribute", "numTab")},
    "lvlJc": {"val": _enum("left", "right", "center", "start", "end")},
    "ind": {k: _so for k in ("left", "right", "start", "end", "firstLine", "hanging", "leftChars", "rightChars", "firstLineChars", "hangingChars")},
    "textAlignment": {"val": _enum("auto", "top", "center", "baseline", "bottom")},
    "pgSz": {"w": _so, "h": _so, "orient": _enum("portrait", "landscape"), "code": _so},
    "pgMar": {k: _so for k in ("top", "left", "bottom", "right", "header", "footer", "gutter")},
    "pgNumType": {"start": _so, "fmt": _enum("decimal", "upperRoman", "lowerRoman", "upperLetter", "lowerLetter")},
    "cols": {"num": _so, "space": _so, "equalWidth": lambda v: v in BOOL, "sep": lambda v: v in BOOL},
    "col": {"w": _so, "space": _so}, "docGrid": {"type": _enum("default", "lines", "linesAndChars", "snapToChars"), "linePitch": _so, "charSpace": _so},
    "type": {"val": _enum("nextPage", "continuous", "evenPage", "oddPage", "nextColumn")},
    "headerReference": {"type": _enum("default", "first", "even")}, "footerReference": {"type": _enum("default", "first", "even")},
    "footnote": {"id": _so, "type": _enum("normal", "separator", "continuationSeparator", "continuationNotice")},
    "endnote": {"id": _so, "type": _enum("normal", "separator", "continuationSeparator", "continuationNotice")},
    "footnoteReference": {"id": _so}, "endnoteReference": {"id": _so},
    "br": {"type": _enum("textWrapping", "page", "column"), "clear": _enum("none", "all", "left", "right")},
    "tab": {"val": _enum("left", "center", "right", "decimal", "bar", "clear", "num"), "pos": _so, "leader": _enum("none", "dot", "hyphen", "underscore", "heavy", "middleDot")},
    "gridCol": {"w": _so}, "gridSpan": {"val": lambda v: _so(v) and 1 <= int(v) <= 256},
    "vMerge": {"val": _enum("restart", "continue")}, "vAlign": {"val": _enum("top", "center", "bottom", "both")},
    "tblW": {"w": _so, "type": _enum("nil", "auto", "pct", "dxa")},
    "tcW": {"w": _so, "type": _enum("nil", "auto", "pct", "dxa")},
    "tblInd": {"w": _so, "type": _enum("nil", "auto", "pct", "dxa")},
    "tblLayout": {"type": _enum("fixed", "autofit")},
    "tblLook": {"val": _hex(4), **{k: (lambda v: v in BOOL) for k in ("firstRow", "lastRow", "firstColumn", "lastColumn", "noHBand", "noVBand")}},
    "trHeight": {"val": _so, "hRule": _enum("auto", "exact", "atLeast")},
    "abstractNum": {"abstractNumId": _so}, "num": {"numId": _so}, "lvl": {"ilvl": _so, "tentative": lambda v: v in BOOL}, "lvlOverride": {"ilvl": _so},
    "numFmt": {"val": _enum("decimal", "decimalZero", "upperRoman", "lowerRoman", "upperLetter", "lowerLetter", "bullet", "none", "ordinal", "cardinalText", "ordinalText")},
    "multiLevelType": {"val": _enum("singleLevel", "multilevel", "hybridMultilevel")},
    "suff": {"val": _enum("tab", "space", "nothing")}, "nsid": {"val": _hex(8)}, "tmpl": {"val": _hex(8)},
    "zoom": {"percent": _so, "val": _enum("none", "fullPage", "bestFit", "textFit")},
    "characterSpacingControl": {"val": _enum("doNotCompress", "compressPunctuation", "compressPunctuationAndJapaneseKana")},
    "compatSetting": {"name": _enum("compatibilityMode", "overrideTableStyleFontSizeAndJustification", "enableOpenTypeFeatures", "doNotFlipMirrorIndents", "differentiateMultirowTableHeaders"), "uri": _enum("http" + "://schemas.microsoft.com/office/word"), "val": _so},
    "clrSchemeMapping": {k: _enum("light1", "dark1", "light2", "dark2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6", "hyperlink", "followedHyperlink") for k in ("bg1", "t1", "bg2", "t2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6", "hyperlink", "followedHyperlink")},
    "proofState": {"spelling": _enum("clean", "dirty"), "grammar": _enum("clean", "dirty")},
    "proofErr": {"type": _enum("spellStart", "spellEnd", "gramStart", "gramEnd")},
    "rsid": {"val": _hex(8)}, "rsidRoot": {"val": _hex(8)},
    "w": {"val": _so}, "fitText": {"val": _so, "id": _so},
    "shd": {"val": _enum("clear", "nil", "solid"), "color": lambda v: v == "auto" or _hex(6)(v), "fill": lambda v: v == "auto" or _hex(6)(v)},
    "noWrap": {"val": lambda v: v in BOOL},
})
_ATTR["latentStyles"].update({"count": _so, "defUIPriority": _so})
_ATTR["spacing"].update({"lineRule": _enum("auto", "atLeast", "exact"), "beforeAutospacing": lambda v: v in BOOL, "afterAutospacing": lambda v: v in BOOL})
for _t in _BORDER:
    _ATTR[_t] = {"val": _enum("nil", "none", "single", "double", "dotted", "dashed", "thick"), "sz": _so, "space": _so, "color": lambda v: v == "auto" or _hex(6)(v), "w": _so, "type": _enum("nil", "auto", "pct", "dxa"), "themeColor": _THEME, "themeTint": _hex(2), "themeShade": _hex(2)}
_LA = set(_ATTR) | {"t", "cr", "noBreakHyphen", "softHyphen", "footnoteRef", "endnoteRef", "separator", "continuationSeparator"}


def thuoc_tinh_word(ten, attr, value):
    """True = phải quét/patch; False = bất biến chỉ sau kiểm giá trị hữu hạn."""
    ns, a = qname(attr)
    if ns == XML_NS and a == "space" and ten == "t" and value in ("default", "preserve"):
        return False
    if ns == R_NS and a == "id" and ten in ("headerReference", "footerReference"):
        if not re.fullmatch(r"rId[1-9][0-9]{0,2}", value):
            _sai()
        return False
    if ns == W_NS and a in ("rsidR", "rsidRPr", "rsidRDefault", "rsidP") and ten in ("p", "r", "tr", "sectPr") and _hex(8)(value):
        return False
    check = _ATTR.get(ten, {}).get(a) if ns == W_NS else None
    if check is None or not check(value):
        _sai()
    return check is _chu


def kiem_cay_word(root, kiem_huy):
    """Chép có sửa walker chặt/không bỏ vùng từ reader TX/DC; không Accept All."""
    def di(e):
        kiem_huy()
        ns, t = qname(e.tag)
        if ns != W_NS or t not in _CON and t not in _LA:
            _sai()
        if t != "t" and e.text and e.text.strip():
            _sai()
        if e.tail and e.tail.strip():
            _sai()
        for attr, value in e.attrib.items():
            thuoc_tinh_word(t, attr, value)
        lap_duoc = {
            "body": {"p", "tbl"}, "hdr": {"p", "tbl"}, "ftr": {"p", "tbl"},
            "footnote": {"p", "tbl"}, "endnote": {"p", "tbl"},
            "footnotes": {"footnote"}, "endnotes": {"endnote"},
            "p": {"r", "proofErr"}, "r": _CON["r"] - {"rPr"},
            "tbl": {"tr"}, "tr": {"tc"}, "tc": {"p", "tbl"},
            "tblGrid": {"gridCol"}, "cols": {"col"}, "tabs": {"tab"},
            "styles": {"style"}, "latentStyles": {"lsdException"},
            "numbering": {"abstractNum", "num"}, "abstractNum": {"lvl"},
            "num": {"lvlOverride"}, "compat": {"compatSetting"},
            "fonts": {"font"}, "rsids": {"rsid"},
            "sectPr": {"headerReference", "footerReference"},
        }.get(t, set())
        da_co = set()
        for c in e:
            ct = qname(c.tag)[1]
            if c.tag not in {W + k for k in _CON.get(t, ())} or ct in da_co and ct not in lap_duoc:
                _sai()
            da_co.add(ct)
            di(c)
        if t == "body" and any(c.tag == W + "sectPr" for c in list(e)[:-1]):
            _sai()
        pr = {"p": "pPr", "r": "rPr", "tc": "tcPr", "tbl": "tblPr"}.get(t)
        if pr and any(c.tag == W + pr for c in list(e)[1:]):
            _sai()
        if t == "t" and len(e):
            _sai()
        if t in ("style", "font", "abstractNum", "num", "lvl", "footnote", "endnote", "footnoteReference", "endnoteReference"):
            key = {"style": "styleId", "font": "name", "abstractNum": "abstractNumId", "num": "numId", "lvl": "ilvl"}.get(t, "id")
            if W + key not in e.attrib:
                _sai()
        if t in ("headerReference", "footerReference") and not {W + "type", "{" + R_NS + "}id"} <= set(e.attrib):
            _sai()
        if t == "style" and W + "type" not in e.attrib:
            _sai()
    di(root)


# DrawingML: toàn bộ text/name có map; typeface chỉ hằng font đã kiểm.
_ACON = {
    "theme": {"themeElements", "objectDefaults", "extraClrSchemeLst"},
    "themeElements": {"clrScheme", "fontScheme", "fmtScheme"},
    "clrScheme": set("dk1 lt1 dk2 lt2 accent1 accent2 accent3 accent4 accent5 accent6 hlink folHlink".split()),
    "fontScheme": {"majorFont", "minorFont"},
    "majorFont": {"latin", "ea", "cs", "font"}, "minorFont": {"latin", "ea", "cs", "font"},
    "fmtScheme": {"fillStyleLst", "lnStyleLst", "effectStyleLst", "bgFillStyleLst"},
    "fillStyleLst": {"solidFill", "gradFill", "noFill"}, "bgFillStyleLst": {"solidFill", "gradFill", "noFill"},
    "lnStyleLst": {"ln"}, "effectStyleLst": {"effectStyle"},
    "effectStyle": {"effectLst", "scene3d", "sp3d"}, "effectLst": {"outerShdw", "glow", "softEdge"},
    "solidFill": {"srgbClr", "schemeClr", "sysClr"}, "gradFill": {"gsLst", "lin", "path", "tileRect"},
    "gsLst": {"gs"}, "gs": {"srgbClr", "schemeClr", "sysClr"},
    "path": {"fillToRect"}, "ln": {"solidFill", "noFill", "prstDash", "miter", "headEnd", "tailEnd", "round", "bevel"},
    "outerShdw": {"srgbClr", "schemeClr"}, "glow": {"srgbClr", "schemeClr"},
    "scene3d": {"camera", "lightRig"}, "camera": {"rot"}, "lightRig": {"rot"},
    "sp3d": {"bevelT", "bevelB"},
}
for _t in _ACON["clrScheme"]:
    _ACON[_t] = {"srgbClr", "sysClr"}
for _t in ("srgbClr", "sysClr", "schemeClr"):
    _ACON[_t] = set("tint shade satMod satOff lumMod lumOff alpha alphaMod alphaOff hueMod hueOff".split())
_AATTR = {t: {"name": _chu} for t in ("theme", "clrScheme", "fontScheme", "fmtScheme")}
_AATTR.update({t: {"typeface": lambda v: v in FONT, "panose": _hex(20), "pitchFamily": _so, "charset": _so} for t in ("latin", "ea", "cs")})
_AATTR.update({
    "font": {"typeface": lambda v: v in FONT, "script": _enum("Jpan", "Hang", "Hans", "Hant", "Arab", "Hebr", "Thai", "Ethi", "Beng", "Gujr", "Khmr", "Knda", "Guru", "Cans", "Cher", "Yiii", "Tibt", "Thaa", "Deva", "Telu", "Taml", "Syrc", "Orya", "Mlym", "Laoo", "Sinh", "Mong", "Viet", "Uigh", "Geor")},
    "srgbClr": {"val": _hex(6)}, "sysClr": {"val": _enum("windowText", "window"), "lastClr": _hex(6)},
    "schemeClr": {"val": _enum("phClr", "dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6", "hlink", "folHlink")},
    "gradFill": {"rotWithShape": _enum("0", "1"), "flip": _enum("none", "x", "y", "xy")},
    "lin": {"ang": _so, "scaled": _enum("0", "1")}, "path": {"path": _enum("circle", "rect", "shape")},
    "gs": {"pos": _so}, "fillToRect": {k: _so for k in ("l", "t", "r", "b")}, "tileRect": {k: _so for k in ("l", "t", "r", "b")},
    "ln": {"w": _so, "cap": _enum("flat", "rnd", "sq"), "cmpd": _enum("sng", "dbl", "thickThin", "thinThick", "tri"), "algn": _enum("ctr", "in")},
    "prstDash": {"val": _enum("solid", "dot", "dash", "lgDash", "dashDot", "lgDashDot", "lgDashDotDot", "sysDash", "sysDot", "sysDashDot", "sysDashDotDot")},
    "miter": {"lim": _so},
    "headEnd": {"type": _enum("none", "triangle", "stealth", "diamond", "oval", "arrow"), "w": _enum("sm", "med", "lg"), "len": _enum("sm", "med", "lg")},
    "outerShdw": {**{k: _so for k in ("blurRad", "dist", "dir", "sx", "sy", "kx", "ky")}, "algn": _enum("b", "bl", "br", "ctr", "l", "r", "t", "tl", "tr"), "rotWithShape": _enum("0", "1")},
    "glow": {"rad": _so}, "softEdge": {"rad": _so},
    "camera": {"prst": _enum("orthographicFront"), "fov": _so, "zoom": _so},
    "lightRig": {"rig": _enum("threePt", "balanced", "soft", "harsh"), "dir": _enum("b", "bl", "br", "l", "r", "t", "tl", "tr")},
    "rot": {"lat": _so, "lon": _so, "rev": _so},
    "sp3d": {"contourW": _so, "extrusionH": _so, "prstMaterial": _enum("warmMatte", "plastic", "metal", "matte")},
    "bevelT": {"w": _so, "h": _so, "prst": _enum("circle", "relaxedInset", "cross", "coolSlant", "angle", "softRound", "convex", "slope")},
})
_AATTR["tailEnd"] = _AATTR["headEnd"]
_AATTR["bevelB"] = _AATTR["bevelT"]
for _t in _ACON["srgbClr"]:
    _AATTR[_t] = {"val": _so}
_ALEAF = set(_AATTR) | {"objectDefaults", "extraClrSchemeLst", "noFill", "round", "bevel"}


def thuoc_tinh_theme(ten, attr, value):
    check = _AATTR.get(ten, {}).get(attr)
    if check is None or not check(value):
        _sai()
    return check is _chu


def kiem_theme(root, kiem_huy):
    def di(e):
        kiem_huy()
        ns, t = qname(e.tag)
        if ns != A_NS or t not in _ACON and t not in _ALEAF:
            _sai()
        if e.text and e.text.strip() or e.tail and e.tail.strip():
            _sai()
        for k, v in e.attrib.items():
            thuoc_tinh_theme(t, k, v)
        for c in e:
            if c.tag not in {A + x for x in _ACON.get(t, ())}:
                _sai()
            di(c)
    di(root)


_CORE_TEXT = {DC_NS: set("title subject creator description identifier language".split()),
              CP_NS: set("keywords lastModifiedBy category contentStatus version".split())}
_APP_TEXT = set("Template Manager Company PresentationFormat Application".split())
_APP_NUM = set("Pages Words Characters Lines Paragraphs Slides Notes TotalTime HiddenSlides MMClips CharactersWithSpaces DocSecurity".split())
_APP_BOOL = set("ScaleCrop LinksUpToDate SharedDoc HyperlinksChanged".split())
_VT_TEXT = {"lpstr", "lpwstr", "bstr"}
_VT_NUM = set("i1 i2 i4 i8 int ui1 ui2 ui4 ui8 uint r4 r8 decimal".split())
_FMTID = "{D5CDD505-2E9C-101B-9397-08002B2CF9AE}"


def _ngay(v):
    # Hình thức thời gian hữu hạn, không là chuỗi tên/path tự do.
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}(?:T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,7})?(?:Z|[+-][0-9]{2}:[0-9]{2}))?", v):
        return False
    from datetime import datetime
    try:
        datetime.fromisoformat(v)
        return True
    except ValueError:
        return False


def _so_vt(t, v):
    from decimal import Decimal
    bits = {"i1": 8, "i2": 16, "i4": 32, "i8": 64, "int": 32,
            "ui1": 8, "ui2": 16, "ui4": 32, "ui8": 64, "uint": 32}
    if t in bits:
        if not re.fullmatch(r"-?[0-9]{1,20}", v):
            return False
        n, b = int(v), bits[t]
        return 0 <= n < 2 ** b if t.startswith("u") else -(2 ** (b - 1)) <= n < 2 ** (b - 1)
    if not re.fullmatch(r"-?[0-9]{1,29}(?:\.[0-9]{1,28})?(?:[eE][+-]?[0-9]{1,3})?", v):
        return False
    n = Decimal(v)
    if t == "decimal":
        return n.as_tuple().exponent >= -28 and n.copy_abs() <= Decimal("79228162514264337593543950335")
    return n.copy_abs() <= Decimal("3.4028234663852886e38" if t == "r4" else "1.7976931348623157e308")


def kiem_properties(root, loai, kiem_huy):
    """Trả node text/attribute phải quét; phần còn lại kiểm kiểu và cấu trúc."""
    quet = set()
    def la(e):
        if len(e):
            _sai()
        return e.text or ""
    def attrs_rong(e):
        if e.attrib:
            _sai()
    if root.attrib or root.text and root.text.strip():
        _sai()
    da_co, pid = set(), set()
    for e in root:
        kiem_huy()
        ns, t = qname(e.tag)
        if e.tail and e.tail.strip():
            _sai()
        if loai == "core":
            if e.tag in da_co:
                _sai()
            da_co.add(e.tag)
            chu = la(e)
            if t in _CORE_TEXT.get(ns, set()):
                attrs_rong(e)
                quet.add((id(e), None))
            elif ns == CP_NS and t == "revision":
                attrs_rong(e)
                if not re.fullmatch(r"[0-9]{1,10}", chu):
                    _sai()
            elif (ns, t) in {(DCT_NS, "created"), (DCT_NS, "modified"), (CP_NS, "lastPrinted")}:
                if e.attrib != ({"{" + XSI_NS + "}type": "dcterms:W3CDTF"} if ns == DCT_NS else {}) or not _ngay(chu):
                    _sai()
            else:
                _sai()
        elif loai == "app":
            if ns != EP_NS or t in da_co:
                _sai()
            da_co.add(t)
            attrs_rong(e)
            if t in _APP_TEXT:
                la(e)
                quet.add((id(e), None))
            elif t in _APP_NUM:
                if not re.fullmatch(r"[0-9]{1,10}", la(e)):
                    _sai()
            elif t in _APP_BOOL:
                if la(e) not in ("true", "false", "0", "1"):
                    _sai()
            elif t == "AppVersion":
                if not re.fullmatch(r"[0-9]{1,4}(?:\.[0-9]{1,4}){1,3}", la(e)):
                    _sai()
            elif t == "HyperlinkBase":
                if la(e):
                    _sai()
            elif t in ("HeadingPairs", "TitlesOfParts"):
                if e.text and e.text.strip() or len(e) != 1:
                    _sai()
                vector = e[0]
                if vector.tag != "{" + VT_NS + "}vector" or set(vector.attrib) != {"baseType", "size"} or vector.get("baseType") != ("variant" if t == "HeadingPairs" else "lpstr") or vector.get("size") != str(len(vector)) or vector.text and vector.text.strip():
                    _sai()
                for c in vector:
                    kiem_huy()
                    attrs_rong(c)
                    if c.tail and c.tail.strip():
                        _sai()
                    if t == "HeadingPairs":
                        if c.tag != "{" + VT_NS + "}variant" or len(c) != 1 or c.text and c.text.strip():
                            _sai()
                        c = c[0]
                        attrs_rong(c)
                    if c.tag == "{" + VT_NS + "}lpstr":
                        la(c)
                        quet.add((id(c), None))
                    elif t == "HeadingPairs" and c.tag == "{" + VT_NS + "}i4" and re.fullmatch(r"[0-9]{1,10}", la(c)):
                        pass
                    else:
                        _sai()
                    if c.tail and c.tail.strip():
                        _sai()
            else:
                _sai()
        elif loai == "custom":
            if ns != CUSTOM_NS or t != "property" or set(e.attrib) != {"fmtid", "pid", "name"} or e.get("fmtid") != _FMTID or not re.fullmatch(r"[0-9]{1,10}", e.get("pid", "")) or int(e.get("pid")) < 2 or e.get("pid") in pid or e.get("name") in da_co or not e.get("name") or len(e) != 1 or e.text and e.text.strip():
                _sai()
            pid.add(e.get("pid"))
            da_co.add(e.get("name"))
            quet.add((id(e), "name"))
            c = e[0]
            attrs_rong(c)
            cns, ct = qname(c.tag)
            chu = la(c)
            if cns != VT_NS or c.tail and c.tail.strip():
                _sai()
            if ct in _VT_TEXT:
                quet.add((id(c), None))
            elif ct in _VT_NUM:
                if not _so_vt(ct, chu):
                    _sai()
            elif ct == "bool":
                if chu not in ("true", "false", "0", "1"):
                    _sai()
            elif ct in ("date", "filetime"):
                if not _ngay(chu):
                    _sai()
            else:
                _sai()
            # Kiểu số/ngày hợp lệ chưa chứng minh nghiệp vụ an toàn: custom
            # có thể chứa MST/mã định danh. Giữ map và đưa vào tổng quét.
            # Writer sau này phải từ chối khi cần thay alias làm sai kiểu.
            quet.add((id(c), None))
        else:
            _sai()
    return quet


@dataclass(frozen=True, repr=False)
class GiaTriXML:
    chu: str = field(repr=False)
    byte_ky_tu: tuple = field(repr=False)
    byte_bat_dau: int
    byte_ket_thuc: int


@dataclass(frozen=True, repr=False)
class NutXML:
    duong: tuple
    bat_dau: int
    ket_thuc: int
    text: GiaTriXML = field(repr=False)
    thuoc_tinh: object = field(repr=False)


def _gia_tri(chu, le, dau, cuoi, *, attr=False, cdata=False):
    ds, moc = [], []
    i = dau
    while i < cuoi:
        j, c = i + 1, chu[i]
        if c == "&" and not cdata:
            j = chu.find(";", i, cuoi) + 1
            if not j:
                _sai()
            ref = chu[i + 1:j - 1]
            if ref.startswith("#x"):
                c = chr(int(ref[2:], 16))
            elif ref.startswith("#"):
                c = chr(int(ref[1:]))
            else:
                c = {"amp": "&", "lt": "<", "gt": ">", "apos": "'", "quot": '"'}.get(ref)
                if c is None:
                    _sai()
        elif c == "\r":
            j += int(j < cuoi and chu[j] == "\n")
            c = " " if attr else "\n"
        elif attr and c in "\t\n":
            c = " "
        ds.append(c)
        moc.append((le[i], le[j]))
        i = j
    return GiaTriXML("".join(ds), tuple(moc), le[dau], le[cuoi])


def anh_xa_xml(raw, root, kiem_huy):
    """Map XML đã qua B1; mỗi code point → đúng khoảng byte part giải nén.

    Khoảng không phải offset trong container ZIP nén. CDATA/entity/CR và
    UTF-16 surrogate pair vẫn có khoảng riêng, không giả một char một byte.
    """
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        codec = "utf-16-le" if raw[:2] == b"\xff\xfe" else "utf-16-be"
        bom = 2
    elif raw.startswith(b"\x00<") or raw.startswith(b"<\x00"):
        codec, bom = ("utf-16-be" if raw.startswith(b"\x00<") else "utf-16-le"), 0
    else:
        codec, bom = "utf-8", 3 if raw.startswith(b"\xef\xbb\xbf") else 0
    try:
        chu = raw[bom:].decode(codec)
    except UnicodeError:
        _sai()
    le, at = [bom], bom
    for i, c in enumerate(chu):
        if i % 1024 == 0:
            kiem_huy()
        at += len(c.encode(codec))
        le.append(at)
    nodes, paths = [], {}
    def liet_ke(e, path):
        nodes.append(e)
        paths[id(e)] = path
        for i, c in enumerate(e):
            liet_ke(c, (*path, i))
    liet_ke(root, ())
    k, i, stack = 0, 0, []
    ket_qua, text, bat_dau, attrs = {}, {}, {}, {}
    try:
        while i < len(chu):
            kiem_huy()
            if chu.startswith("<?xml", i):
                j = chu.find("?>", i)
                if j < 0:
                    _sai()
                i = j + 2
                continue
            if chu.startswith("<![CDATA[", i):
                j = chu.find("]]>", i + 9)
                if j < 0 or not stack:
                    _sai()
                text[id(stack[-1])].append(_gia_tri(chu, le, i + 9, j, cdata=True))
                i = j + 3
                continue
            if chu[i] != "<":
                j = chu.find("<", i)
                if j < 0:
                    j = len(chu)
                v = _gia_tri(chu, le, i, j)
                if stack:
                    text[id(stack[-1])].append(v)
                elif v.chu.strip():
                    _sai()
                i = j
                continue
            # Tokenize tag đã hợp lệ theo Expat; dấu > trong quote không đóng tag.
            j, quote = i + 1, None
            while j < len(chu):
                c = chu[j]
                if quote:
                    if c == quote:
                        quote = None
                elif c in "\"'":
                    quote = c
                elif c == ">":
                    break
                j += 1
            if j >= len(chu):
                _sai()
            if chu.startswith("</", i):
                if not stack:
                    _sai()
                e = stack.pop()
                end = le[j + 1]
            else:
                if k >= len(nodes):
                    _sai()
                e = nodes[k]
                k += 1
                nid = id(e)
                bat_dau[nid], text[nid] = le[i], []
                m = re.match(r"[^\s/>]+", chu[i + 1:j])
                if m is None or m.group().split(":")[-1] != qname(e.tag)[1]:
                    _sai()
                a, vs = i + 1 + m.end(), []
                while a < j:
                    while a < j and chu[a].isspace():
                        a += 1
                    if a >= j or chu[a] == "/":
                        break
                    nam = re.match(r"[^\s=]+", chu[a:j])
                    if nam is None:
                        _sai()
                    name = nam.group()
                    a += nam.end()
                    while a < j and chu[a].isspace():
                        a += 1
                    if chu[a] != "=":
                        _sai()
                    a += 1
                    while a < j and chu[a].isspace():
                        a += 1
                    q = chu[a]
                    if q not in "\"'":
                        _sai()
                    endv = chu.find(q, a + 1, j)
                    if endv < 0:
                        _sai()
                    if name != "xmlns" and not name.startswith("xmlns:"):
                        vs.append((name, _gia_tri(chu, le, a + 1, endv, attr=True)))
                    a = endv + 1
                if len(vs) != len(e.attrib):
                    _sai()
                da = {}
                for (name, v), (key, val) in zip(vs, e.attrib.items()):
                    if name.split(":")[-1] != qname(key)[1] or v.chu != val:
                        _sai()
                    da[key] = v
                attrs[nid] = da
                if chu[j - 1] != "/":
                    stack.append(e)
                    i = j + 1
                    continue
                end = le[j + 1]
            nid = id(e)
            vals = text[nid]
            v = GiaTriXML("".join(x.chu for x in vals), tuple(p for x in vals for p in x.byte_ky_tu), vals[0].byte_bat_dau if vals else end, vals[-1].byte_ket_thuc if vals else end)
            # Với node có con, phần whitespace có thể gồm tail của các con.
            if not len(e) and v.chu != (e.text or "") or len(e) and v.chu.strip():
                _sai()
            ket_qua[nid] = NutXML(paths[nid], bat_dau[nid], end, v, MappingProxyType(attrs[nid]))
            i = j + 1
        if stack or k != len(nodes) or len(ket_qua) != len(nodes):
            _sai()
        kiem_huy()
        return MappingProxyType(dict(ket_qua))
    finally:
        stack.clear()
        nodes.clear()
        ket_qua.clear()
        text.clear()
        attrs.clear()
        le.clear()
