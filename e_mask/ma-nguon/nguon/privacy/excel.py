"""Mask a bounded XLSX package by patching XML text spans, never round-tripping Excel.

Untouched ZIP members and all formula elements keep their original bytes. Unsupported
opaque features fail closed; selected phrases left in immutable XML become blockers.
"""
from __future__ import annotations

import io
import posixpath
import re
import struct
import unicodedata
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote
from xml.parsers import expat
from xml.sax.saxutils import escape

from .core import TOKEN, key, literal_pattern, validate_rules
from .types import PrivacyError

NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
MAX_BYTES = 20 * 1024 * 1024
MAX_EXPANDED = 80 * 1024 * 1024
MAX_TEXT = 500_000
DATE_1904_OFFSET = 1462
DRAW = "http://schemas.openxmlformats.org/drawingml/2006/main"
SHEET_DRAW = "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing"
EXTLINK = "http://schemas.microsoft.com/office/spreadsheetml/2021/extlinks2021"
EXCEL_ERRORS = {"#NULL!", "#DIV/0!", "#VALUE!", "#REF!", "#NAME?", "#NUM!", "#N/A", "#GETTING_DATA", "#SPILL!",
                "#CALC!", "#FIELD!", "#BLOCKED!", "#CONNECT!", "#BUSY!", "#UNKNOWN!", "#PYTHON!"}
SHEET_STATES = {"visible", "hidden", "veryHidden"}
ID_CATEGORIES = {"MA_SO_THUE", "TAI_KHOAN", "GIAY_TO", "DIEN_THOAI", "HOP_DONG"}
ESCAPE = re.compile(r"_x([0-9a-fA-F]{4})_")
HEADER_CODE = re.compile(r'&(?:"[^\"]*"|K[0-9A-Fa-f]{6}|[0-9]{1,3}|[LCRPNAFZDTBGISEUXY]|&)')
ALLOWED_PART = re.compile(
    r"(?:\[Content_Types\]\.xml|_rels/\.rels|docProps/(?:core|app|custom)\.xml|"
    r"xl/(?:workbook|styles|sharedStrings|calcChain)\.xml|xl/_rels/workbook\.xml\.rels|"
    r"xl/theme/theme\d+\.xml|xl/worksheets/sheet\d+\.xml|"
    r"xl/worksheets/_rels/sheet\d+\.xml\.rels|xl/comments(?:/comment)?\d*\.xml|"
    r"xl/comments/comment\d+\.xml|xl/tables/table\d+\.xml|"
    r"xl/drawings/drawing\d+\.xml|xl/drawings/_rels/drawing\d+\.xml\.rels|"
    r"xl/externalLinks/externalLink\d+\.xml|xl/externalLinks/_rels/externalLink\d+\.xml\.rels|"
    r"xl/printerSettings/printerSettings\d+\.bin|"
    r"xl/drawings/(?:commentsDrawing|vmlDrawing)\d+\.vml|xl/vmlDrawings/vmlDrawing\d+\.vml)"
)
# Never accepted, in any mode: active content, embedded objects and signatures.
UNSAFE_PART = re.compile(r"(?:xl/vbaProject\.bin|xl/activeX/.*|xl/embeddings/.*|xl/ctrlProps/.*|_xmlsignatures/.*|"
                         r"customUI/.*|xl/macrosheets/.*|xl/dialogsheets/.*)", re.I)
REL_TYPES = {"officeDocument", "worksheet", "styles", "theme", "sharedStrings",
             "calcChain", "comments", "vmlDrawing", "table", "extended-properties",
             "custom-properties", "core-properties"}
REL_TYPES.update({"drawing", "printerSettings", "externalLink"})
# Geometry and editable shape text only: images, charts, SmartArt, linked fields,
# hyperlinks and active controls are deliberately absent from this allowlist.
DRAW_TAGS = set("xfrm off ext chOff chExt prstGeom avLst gd custGeom gdLst ahLst ahXY ahPolar cxnLst cxn pos rect pathLst path moveTo lnTo arcTo quadBezTo cubicBezTo close pt noFill solidFill gradFill gsLst gs lin path fillToRect tileRect pattFill fgClr bgClr grpFill srgbClr scrgbClr schemeClr sysClr prstClr hslClr tint shade comp inv gray alpha alphaOff alphaMod hue hueOff hueMod sat satOff satMod lum lumOff lumMod red redOff redMod green greenOff greenMod blue blueOff blueMod gamma invGamma ln prstDash custDash ds round bevel miter headEnd tailEnd lnRef fillRef effectRef fontRef bodyPr lstStyle p pPr r rPr t br endParaRPr defRPr latin ea cs sym spcBef spcAft lnSpc spcPct spcPts buNone buChar buFont buSzPct buSzPts buClr buClrTx buFontTx buSzTx tabLst tab noAutofit normAutofit spAutoFit prstTxWarp highlight uFill uFillTx uLn uLnTx spLocks grpSpLocks cxnSpLocks effectLst outerShdw innerShdw glow softEdge reflection blur fillOverlay duotone extLst ext".split())
SHEET_DRAW_TAGS = set("wsDr twoCellAnchor oneCellAnchor absoluteAnchor from to col colOff row rowOff pos ext sp grpSp cxnSp nvSpPr nvGrpSpPr nvCxnSpPr cNvPr cNvSpPr cNvGrpSpPr cNvCxnSpPr spPr grpSpPr style txBody clientData stCxn endCxn".split())


def local(name):
    return name.rsplit("}", 1)[-1]


def decode_string(value):
    # One pass is important: _x005F_x0041_ represents literal '_x0041_', not 'A'.
    value = ESCAPE.sub(lambda m: chr(int(m[1], 16)), value)
    # Excel may escape an astral Unicode character as two UTF-16 code units.
    value = value.encode("utf-16", "surrogatepass").decode("utf-16", "surrogatepass")
    return unicodedata.normalize("NFC", value)


def encode_string(value):
    value = ESCAPE.sub(lambda m: "_x005F_" + m[0][1:], value)
    value = "".join(f"_x{ord(c):04X}_" if (ord(c) < 32 and c not in "\n\r\t") or 0xD800 <= ord(c) <= 0xDFFF else c for c in value)
    return escape(value).encode("utf-8")


@dataclass
class Node:
    name: str
    attrs: dict
    start: int
    start_end: int
    qname: str
    empty: bool
    parent: "Node | None" = None
    end_start: int = 0
    end: int = 0
    text: str = ""
    children: list = field(default_factory=list)

    def descendants(self, name=None):
        for child in self.children:
            if name is None or local(child.name) == name:
                yield child
            yield from child.descendants(name)

    def child(self, name):
        return next((c for c in self.children if local(c.name) == name), None)


class XML:
    def __init__(self, raw, part):
        self.raw, self.part, self.nodes, self.comments, self.namespaces = raw, part, [], [], []
        try:
            raw.decode("utf-8-sig")
        except UnicodeError:
            raise PrivacyError(f"XLSX có XML không phải UTF-8: {part}. Hãy Save As XLSX bằng Excel.") from None
        if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
            raise PrivacyError("Không nhận XLSX có DTD hoặc XML entity.")
        parser = expat.ParserCreate(namespace_separator="}")
        stack = []

        def fail(*args):
            raise PrivacyError("XLSX chứa chỉ thị XML không được hỗ trợ.")

        def start(name, attrs):
            if len(stack) >= 80 or len(self.nodes) >= 400_000:
                raise PrivacyError("Cấu trúc XML của XLSX vượt giới hạn.")
            at = parser.CurrentByteIndex
            match = re.match(br"<([^\s/>]+)", raw[at:at + 300])
            if not match:
                fail()
            quote = None
            stop = at
            while stop < len(raw):
                char = raw[stop]
                if quote:
                    if char == quote:
                        quote = None
                elif char in (34, 39):
                    quote = char
                elif char == 62:
                    break
                stop += 1
            node = Node(name, dict(attrs), at, stop + 1, match[1].decode("utf-8"),
                        raw[at:stop].rstrip().endswith(b"/"), stack[-1] if stack else None)
            if stack:
                stack[-1].children.append(node)
            else:
                self.root = node
            self.nodes.append(node)
            stack.append(node)

        def end(name):
            node = stack.pop()
            if node.empty:
                node.end_start = node.start_end
                node.end = node.start_end
            else:
                node.end_start = parser.CurrentByteIndex
                node.end = raw.index(b">", node.end_start) + 1

        def chars(value):
            if stack:
                stack[-1].text += value

        def comment(value):
            at = parser.CurrentByteIndex
            self.comments.append((at, raw.index(b"-->", at) + 3, b""))

        parser.StartElementHandler, parser.EndElementHandler = start, end
        parser.CharacterDataHandler = chars
        parser.CommentHandler = comment
        parser.StartNamespaceDeclHandler = lambda prefix, uri: self.namespaces.append(uri or "")
        parser.StartDoctypeDeclHandler = fail
        parser.EntityDeclHandler = fail
        parser.ExternalEntityRefHandler = fail
        parser.ProcessingInstructionHandler = fail
        try:
            parser.Parse(raw, True)
        except PrivacyError:
            raise  # limits and unsupported instructions keep their own message
        except (expat.ExpatError, ValueError, IndexError):
            raise PrivacyError(f"XML trong XLSX bị lỗi: {part}.") from None

    def text_patch(self, node, value):
        if node.children:
            raise PrivacyError("Không thể thay an toàn phần XML lồng nhau này.")
        payload = encode_string(value)
        if node.empty:
            opening = self.raw[node.start:node.start_end]
            opening = re.sub(br"/\s*>$", b">", opening)
            return node.start, node.end, opening + payload + f"</{node.qname}>".encode()
        return node.start_end, node.end_start, payload

    def attr_patch(self, node, name, value):
        opening = self.raw[node.start:node.start_end]
        expr = re.compile(rb"(?<![\w:.-])" + re.escape(name.encode()) + rb"\s*=\s*([\"'])(.*?)\1", re.S)
        match = expr.search(opening)
        encoded = escape(value, {'"': "&quot;", "'": "&apos;"}).encode("utf-8")
        if match:
            return node.start + match.start(2), node.start + match.end(2), encoded
        at = node.start_end - (2 if node.empty else 1)
        return at, at, b" " + name.encode() + b'="' + encoded + b'"'


def patched(raw, patches):
    # Multiple inserted attributes may share an insertion point, but modifications
    # to overlapping source spans indicate a programming error, never a safe export.
    ordered = sorted(set(patches), key=lambda p: (p[0], -p[1]))
    filtered = []
    for patch in ordered:
        # XML comments/cache children already covered by a wider replacement
        # must not become overlapping deletion operations.
        if filtered and patch[2] == b"" and filtered[-1][0] <= patch[0] and filtered[-1][1] >= patch[1]:
            continue
        filtered.append(patch)
    at, pieces = 0, []
    for start, end, value in filtered:
        if start < at:
            raise PrivacyError("Không thể tạo XLSX: các vùng thay thế XML bị chồng lấn.")
        pieces.extend((raw[at:start], value))
        at = end
    pieces.append(raw[at:])
    return b"".join(pieces)


def replace_pieces(pieces, matches, active):
    offsets, pos = [], 0
    for piece in pieces:
        offsets.append((pos, pos + len(piece)))
        pos += len(piece)
    updated = list(pieces)
    for match in reversed(matches):
        token = active[int(match.lastgroup[1:])]["token"]
        first = next((i for i, (a, b) in enumerate(offsets) if a <= match.start() < b), 0)
        last = next((i for i, (a, b) in enumerate(offsets) if a < match.end() <= b), first)
        a, b = offsets[first][0], offsets[last][0]
        if first == last:
            updated[first] = updated[first][:match.start() - a] + token + updated[first][match.end() - a:]
        else:
            updated[first] = updated[first][:match.start() - a] + token
            for i in range(first + 1, last):
                updated[i] = ""
            updated[last] = updated[last][match.end() - b:]
    return updated


def header_groups(text):
    """Header formatting codes remain raw; L/C/R sections cannot match each other."""
    groups, current, at = [], [], 0
    for match in HEADER_CODE.finditer(text):
        if at < match.start():
            current.append((False, text[at:match.start()]))
        code = match[0]
        if code in {"&L", "&C", "&R"}:
            if current:
                groups.append(current)
            current = [(True, code)]
        else:
            current.append((code != "&&", "&" if code == "&&" else code))
        at = match.end()
    if at < len(text):
        current.append((False, text[at:]))
    if current:
        groups.append(current)
    return groups


@dataclass
class Value:
    part: str
    nodes: list[Node]
    locations: list[str]
    kind: str = "text"
    cell: Node | None = None
    attribute: str | None = None
    protected_number: bool = False

    def strings(self):
        return [decode_string(n.attrs[self.attribute] if self.attribute else n.text) for n in self.nodes]

    @property
    def text(self):
        return "".join(self.strings())


@dataclass
class ExcelMaskResult:
    output: bytes | None
    preview: str
    replacements: int
    applied_sources: set[str]
    changes: list[dict]
    blockers: list[dict]
    warnings: list[str]
    summary: dict
    disclosures: list[dict] = field(default_factory=list)
    masked_texts: list[str] = field(default_factory=list)
    ai: dict = field(default_factory=dict)          # summary for the UI: removed parts, blockers, sheet names
    ai_plan: dict | None = field(default=None, repr=False)
    ai_applied: set[str] = field(default_factory=set)


class ExcelWorkbook:
    def __init__(self, data: bytes, filename: str):
        if Path(filename).suffix.lower() != ".xlsx":
            raise PrivacyError("Excel hiện hỗ trợ .xlsx. Hãy Save As .xlsx trước; chưa nhận .xls, .xlsm hoặc .xlsb.")
        if not 0 < len(data) <= MAX_BYTES:
            raise PrivacyError("File Excel rỗng hoặc vượt 20 MB.")
        self.parts, self.infos, self.xml, self.values = {}, [], {}, []
        self.warnings = ["Giữ nguyên tên sheet, công thức, định dạng và ô gộp. Nội dung ở sheet/ô ẩn cũng được kiểm tra."]
        self.suggestion_texts, self.formulas, self.sheet_names = [], [], []
        self.protected_preview = []
        self.disclosures, self.external_targets = [], []
        self.external_parts, self.binary_parts = set(), set()
        self.preview_truncated = False
        self.locations, self.numeric_count, self.hidden_sheets = {}, 0, []
        self.part_sheets, self.cell_count = {}, 0
        # 2.3.0: parts that are not unsafe but cannot be masked in place. They block the
        # structure-preserving export and are dropped (with confirmation) by the AI export.
        self.unsupported: dict[str, str] = {}
        self.grid: dict[str, list] = {}
        self.merges: dict[str, list[str]] = {}
        self.columns: dict[str, list[dict]] = {}
        self.sheet_states: dict[str, str] = {}
        self.shared_index: list[int] = []
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                infos = [i for i in archive.infolist() if not i.is_dir()]
                names = [i.filename for i in infos]
                if len(names) > 2000 or len(names) != len(set(names)) or len({n.casefold() for n in names}) != len(names):
                    raise PrivacyError("XLSX có quá nhiều phần hoặc có phần ZIP trùng tên.")
                if sum(i.file_size for i in infos) > MAX_EXPANDED:
                    raise PrivacyError("XLSX sau giải nén vượt giới hạn 80 MB.")
                for info in infos:
                    name = info.filename
                    if (info.external_attr >> 16) & 0o170000 == 0o120000:
                        raise PrivacyError("Không nhận XLSX có ZIP member dạng symbolic link.")
                    if info.flag_bits & 1 or info.file_size > 32 * 1024 * 1024 or (info.file_size > 1024 * 1024 and info.file_size > max(1, info.compress_size) * 1000):
                        raise PrivacyError("XLSX mã hóa hoặc có tỷ lệ nén/kích thước bất thường.")
                    if UNSAFE_PART.fullmatch(name):
                        raise PrivacyError(f"XLSX có thành phần chưa hỗ trợ an toàn: {name}. Không nhận macro, "
                                           "ActiveX, đối tượng nhúng hoặc chữ ký số.")
                    if not ALLOWED_PART.fullmatch(name):
                        self.unsupported[name] = self._describe_unsupported(name)
                        continue
                    self.parts[name] = archive.read(info)
                    self.infos.append(info)
        except (zipfile.BadZipFile, RuntimeError, NotImplementedError, OSError):
            raise PrivacyError("Không đọc được XLSX; kiểm tra file không đặt mật khẩu và không bị lỗi.") from None
        required = {"[Content_Types].xml", "_rels/.rels", "xl/workbook.xml", "xl/_rels/workbook.xml.rels"}
        if not required.issubset(self.parts):
            raise PrivacyError("File không có đầy đủ cấu trúc XLSX.")
        node_count = 0
        for name, raw in self.parts.items():
            if name.endswith(".bin"):
                self._read_printer_settings(name, raw)
                continue
            self.xml[name] = XML(raw, name)
            node_count += len(self.xml[name].nodes)
            if node_count > 500_000:
                raise PrivacyError("Workbook vượt giới hạn 500.000 phần tử XML.")
        self.reserved_tokens = {token for xml in self.xml.values() for node in xml.nodes
                                for text in [node.text, *node.attrs.values()]
                                for token in TOKEN.findall(decode_string(text))}
        self._validate_relationships()
        workbook = self.xml["xl/workbook.xml"]
        if workbook.root.name != NS + "}workbook":
            raise PrivacyError("Định dạng XLSX Strict chưa được hỗ trợ. Hãy Save As Excel Workbook (.xlsx).")
        self.protected_styles = self._protected_styles()
        self._read_cells()
        self._read_metadata()
        self._read_drawings()
        self._read_external_links()
        self._read_protected()
        self.relevance_texts = [decode_string(text) for xml in self.xml.values() for node in xml.nodes
                                for text in [node.text, *node.attrs.values()] if text.strip()]
        self.relevance_texts += [v.text for v in self.values] + [uri for xml in self.xml.values() for uri in xml.namespaces]
        self.relevance_texts.extend(d["value"] for d in self.disclosures)
        self.relevance_texts = list(dict.fromkeys(self.relevance_texts))
        self.reserved_tokens.update(token for text in self.relevance_texts for token in TOKEN.findall(text))
        for value in self.values:
            if value.kind == "header/footer":
                self.suggestion_texts.extend("".join(text for control, text in group if not control)
                                             for group in header_groups(value.text))
            elif value.kind != "number":
                self.suggestion_texts.append(value.text)
        self.suggestion_texts = list(dict.fromkeys(text for text in self.suggestion_texts if text.strip()))
        self.original_preview = self._preview({})
        if self.preview_truncated:
            self.warnings.append("Bản xem trước chỉ hiển thị tối đa 500.000 ký tự. Mọi ô và phần được hỗ trợ trong toàn bộ workbook vẫn được kiểm tra và Mask.")
        self.summary = {
            "sheet_names": list(self.sheet_names), "sheet_names_changed": False,
            "sheet_count": len(self.sheet_names), "formula_count": len(self.formulas),
            "numeric_ids_changed": 0, "numeric_cell_count": self.numeric_count,
            "hidden_sheets": list(self.hidden_sheets), "text_value_count": len(self.values),
            "cell_count": self.cell_count, "uncompressed_bytes": sum(map(len, self.parts.values())),
            "preview_truncated": self.preview_truncated,
            "external_link_count": len([p for p in self.external_parts if not p.endswith('.rels')]),
            "external_target_count": len(self.external_targets),
            "disclosure_count": len(self.disclosures),
        }
        if self.formulas:
            self.warnings.append("Kết quả công thức lưu sẵn được giữ để AI đọc được số liệu; kết quả dạng chữ được Mask cùng quy tắc. Mask không tính lại công thức; giữ nguyên chế độ tính toán của workbook.")
        if self.hidden_sheets:
            self.warnings.append("Workbook có sheet ẩn: " + ", ".join(self.hidden_sheets) + ". Các ô ẩn vẫn được xử lý.")
        if self.external_parts:
            self.warnings.append("Giữ nguyên liên kết workbook ngoài và cache liên kết. Đường dẫn, tên và dữ liệu nguồn có thể còn trong file; cần xem danh sách thông tin giữ nguyên trước khi xuất. Phần mềm không truy cập hoặc cập nhật nguồn liên kết.")

    @staticmethod
    def _describe_unsupported(name):
        kinds = [("xl/media/", "Ảnh"), ("xl/charts/", "Biểu đồ"), ("xl/pivot", "Pivot"), ("xl/metadata.xml", "Metadata Excel 365"),
                 ("xl/richData/", "Dữ liệu ảnh trong ô"), ("xl/threadedComments/", "Chú thích dạng hội thoại"),
                 ("xl/persons/", "Danh sách người chú thích"), ("xl/connections.xml", "Kết nối dữ liệu"),
                 ("xl/queryTables/", "Truy vấn dữ liệu"), ("customXml/", "Dữ liệu XML tùy chỉnh"),
                 ("docProps/thumbnail", "Ảnh thu nhỏ"), ("xl/slicer", "Slicer"), ("xl/timeline", "Timeline")]
        label = next((text for prefix, text in kinds if name.startswith(prefix)), "Thành phần chưa hỗ trợ")
        return f"{label}: không thể Mask tại chỗ nên không giữ được trong chế độ giữ nguyên cấu trúc."

    def _mark_unsupported(self, part, reason):
        self.unsupported.setdefault(part, reason)

    def _read_printer_settings(self, part, raw):
        # DEVMODE is copied as inert bytes, never handed to a printer/driver.
        # Validate both fixed Windows layouts and the declared driver-extra size.
        valid, device = False, ""
        if 76 <= len(raw) <= 128 * 1024:
            for size_offset, minimum, name_size, encoding in ((68, 76, 64, "utf-16-le"), (36, 44, 32, "latin-1")):
                size, extra = struct.unpack_from("<HH", raw, size_offset)
                if minimum <= size <= 4096 and size + extra == len(raw):
                    valid = True
                    device = raw[:name_size].decode(encoding, errors="replace").split("\0", 1)[0]
                    break
        if not valid:
            raise PrivacyError(f"Thiết lập máy in không có cấu trúc DEVMODE hợp lệ: {part}.")
        self.binary_parts.add(part)
        self.disclosures.append({"location": part, "kind": "printer_settings",
            "reason": "Giữ nguyên thiết lập in nhị phân. Không thể kiểm tra đầy đủ tên máy in, máy tính hoặc dữ liệu riêng của driver trong phần này.",
            "value": device or "Thiết lập máy in nhị phân"})

    def _validate_relationships(self):
        self.relationships = {}
        for part, xml in self.xml.items():
            if not part.endswith(".rels"):
                continue
            relation_map = {}
            base = "" if part == "_rels/.rels" else part.rsplit("/_rels/", 1)[0]
            for node in xml.root.children:
                attrs = node.attrs
                type_name = attrs.get("Type", "").rsplit("/", 1)[-1]
                target = attrs.get("Target", "")
                ident = attrs.get("Id", "")
                if not ident or ident in relation_map:
                    raise PrivacyError("XLSX có relationship trùng hoặc thiếu Id.")
                external = attrs.get("TargetMode", "").casefold() == "external"
                if external and attrs.get("Type") == REL + "/externalLinkPath" and re.fullmatch(r"xl/externalLinks/_rels/externalLink\d+\.xml\.rels", part):
                    if not target or len(target) > 16384:
                        raise PrivacyError("Liên kết workbook ngoài không hợp lệ hoặc quá dài.")
                    # Deliberately do not normalize, resolve, open or fetch targets.
                    relation_map[ident] = (type_name, target)
                    self.external_targets.append((part, ident, unquote(target)))
                    continue
                if part.startswith("xl/externalLinks/"):
                    self._mark_unsupported(part.replace("/_rels/", "/").removesuffix(".rels"),
                                           "Liên kết ngoài dạng DDE/OLE hoặc chưa hỗ trợ.")
                    continue
                if external:
                    self._mark_unsupported(f"{part} → {type_name}", f"Liên kết ra ngoài ({type_name}): {target[:200]}")
                    continue
                if "\\" in target or ":" in target or "?" in target or "#" in target:
                    raise PrivacyError(f"Đường dẫn relationship không hợp lệ: {part}.")
                resolved = posixpath.normpath(target.lstrip("/") if target.startswith("/") else posixpath.join(base, target))
                if type_name not in REL_TYPES:
                    self._mark_unsupported(resolved, self.unsupported.get(resolved) or
                                           f"Thành phần {type_name}: không thể Mask tại chỗ.")
                    continue
                if resolved not in self.parts:
                    if resolved in self.unsupported:
                        continue
                    raise PrivacyError(f"XLSX có relationship đến phần bị thiếu: {part}.")
                constrained = {
                    "drawing": (r"xl/worksheets/_rels/sheet\d+\.xml\.rels", r"xl/drawings/drawing\d+\.xml"),
                    "printerSettings": (r"xl/worksheets/_rels/sheet\d+\.xml\.rels", r"xl/printerSettings/printerSettings\d+\.bin"),
                    "externalLink": (r"xl/_rels/workbook\.xml\.rels", r"xl/externalLinks/externalLink\d+\.xml"),
                }
                if type_name in constrained:
                    source_pattern, target_pattern = constrained[type_name]
                    if attrs.get("Type") != REL + "/" + type_name or not re.fullmatch(source_pattern, part) or not re.fullmatch(target_pattern, resolved):
                        raise PrivacyError(f"Relationship không đúng loại/vị trí: {part} ({type_name}).")
                relation_map[ident] = (type_name, resolved)
            self.relationships[part] = relation_map
        for part, xml in self.xml.items():
            try:
                if re.fullmatch(r"xl/drawings/drawing\d+\.xml", part):
                    self._validate_drawing(xml)
                elif part.startswith("xl/externalLinks/"):
                    self.external_parts.add(part)
                    if not part.endswith(".rels"):
                        self._validate_external_link(xml)
                if part.endswith(".vml"):
                    self._validate_vml(xml)
            except PrivacyError as error:
                self._mark_unsupported(part, str(error))
        for part in list(self.unsupported):
            self.external_parts.discard(part)
        for node in self.xml["[Content_Types].xml"].root.children:
            content_type = node.attrs.get("ContentType", "").lower()
            if any(s in content_type for s in ("macroenabled", "vbaproject", "oleobject", "activex", "digital-signature")):
                raise PrivacyError("XLSX chứa macro, đối tượng nhúng hoặc chữ ký số chưa được hỗ trợ.")

    def _validate_vml(self, xml):
        if any(local(n.name) in {"imagedata", "image", "object"} for n in xml.nodes):
            raise PrivacyError("VML có ảnh hoặc đối tượng; chưa hỗ trợ Mask tại chỗ.")
        for node in xml.nodes:
            if local(node.name) == "shape":
                objects = list(node.descendants("ClientData"))
                if len(objects) != 1 or objects[0].attrs.get("ObjectType") != "Note":
                    raise PrivacyError("VML ngoài ghi chú ô; chưa hỗ trợ Mask tại chỗ.")
            if local(node.name) == "textbox" and any(n.text.strip() for n in [node, *node.descendants()]):
                raise PrivacyError("VML có chữ riêng ngoài phần ghi chú; chưa hỗ trợ Mask tại chỗ.")

    def _validate_drawing(self, xml):
        if xml.root.name != SHEET_DRAW + "}wsDr":
            raise PrivacyError(f"Drawing chưa có cấu trúc hình vẽ Excel được hỗ trợ: {xml.part}.")
        extensions = {
            "http://schemas.microsoft.com/office/drawing/2014/main}creationId",
            "http://schemas.microsoft.com/office/drawing/2010/main}hiddenFill",
            "http://schemas.microsoft.com/office/drawing/2010/main}hiddenLine",
        }
        for node in xml.nodes:
            namespace, _, tag = node.name.rpartition("}")
            if not ((namespace == DRAW and tag in DRAW_TAGS) or
                    (namespace == SHEET_DRAW and tag in SHEET_DRAW_TAGS) or node.name in extensions):
                raise PrivacyError(f"Drawing có đối tượng chưa hỗ trợ: {xml.part} ({tag or node.name}). Chỉ nhận hình vẽ và chữ; chưa nhận ảnh, biểu đồ, hyperlink hoặc đối tượng nhúng.")
            if any((local(attr) in {"macro", "textlink"} and value.strip()) or attr.startswith(REL + "}")
                   for attr, value in node.attrs.items()):
                raise PrivacyError(f"Drawing có macro hoặc nội dung liên kết chưa hỗ trợ: {xml.part}.")

    def _validate_external_link(self, xml):
        allowed = set("externalLink externalBook sheetNames sheetName definedNames definedName sheetDataSet sheetData row cell v".split())
        if xml.root.name != NS + "}externalLink" or len([n for n in xml.root.children if n.name == NS + "}externalBook"]) != 1:
            raise PrivacyError("Chỉ hỗ trợ externalBook; không nhận liên kết DDE/OLE.")
        relpart = xml.part.rsplit("/", 1)[0] + "/_rels/" + xml.part.rsplit("/", 1)[1] + ".rels"
        rels = self.relationships.get(relpart, {})
        for node in xml.nodes:
            namespace, _, tag = node.name.rpartition("}")
            if not ((namespace == NS and tag in allowed) or
                    (namespace == EXTLINK and tag in {"alternateUrls", "absoluteUrl", "relativeUrl"})):
                raise PrivacyError(f"Cấu trúc liên kết ngoài chưa hỗ trợ: {xml.part} ({tag}).")
            for attr, value in node.attrs.items():
                if attr == REL + "}id" and (value not in rels or rels[value][0] != "externalLinkPath"):
                    raise PrivacyError(f"Liên kết workbook ngoài bị thiếu/sai đích: {xml.part}.")
            if tag in {"externalBook", "absoluteUrl", "relativeUrl"} and REL + "}id" not in node.attrs:
                raise PrivacyError(f"Liên kết workbook ngoài thiếu relationship: {xml.part}.")

    def _protected_styles(self):
        xml = self.xml.get("xl/styles.xml")
        if not xml:
            return set()
        try:
            formats = {int(n.attrs.get("numFmtId", "0")): n.attrs.get("formatCode", "") for n in xml.root.descendants("numFmt")}
        except ValueError:
            raise PrivacyError("XLSX có mã định dạng số không hợp lệ.") from None
        xfs = xml.root.child("cellXfs")
        result = set()
        for index, node in enumerate(xfs.children if xfs else []):
            try:
                fmt = int(node.attrs.get("numFmtId", "0"))
            except ValueError:
                raise PrivacyError("XLSX có mã định dạng số không hợp lệ.") from None
            # ID-like integer formats remain eligible; currency, dates, percentages,
            # decimals/scientific and other formatted numbers stay numeric.
            if fmt not in {0, 1, 49} and not re.fullmatch(r"0+", formats.get(fmt, "")):
                result.add(index)
        return result

    def _rich_nodes(self, container):
        # Phonetic annotations are handled separately, never mixed into visible text.
        return [n for n in container.descendants("t") if not any(local(p.name) == "rPh" for p in self._ancestors(n, container))]

    @staticmethod
    def _ancestors(node, stop):
        parent = node.parent
        while parent and parent is not stop:
            yield parent
            parent = parent.parent

    def _read_cells(self):
        shared = self.xml.get("xl/sharedStrings.xml")
        strings = []
        if shared:
            for index, si in enumerate(n for n in shared.root.children if local(n.name) == "si"):
                item = Value(shared.part, self._rich_nodes(si), [], "text")
                strings.append(item)
                self.shared_index.append(len(self.values))
                self.values.append(item)
                for phonetic in si.descendants("rPh"):
                    self.values.append(Value(shared.part, list(phonetic.descendants("t")), [f"Shared string {index}: phiên âm"], "phonetic"))
        workbook = self.xml["xl/workbook.xml"]
        sheets = list(workbook.root.descendants("sheet"))
        if not 1 <= len(sheets) <= 200:
            raise PrivacyError("Workbook cần 1–200 sheet.")
        relations = self.relationships["xl/_rels/workbook.xml.rels"]
        sheet_parts = set()
        for sheet in sheets:
            name, rid = sheet.attrs.get("name", ""), sheet.attrs.get(REL + "}id", "")
            if not name or name.casefold() in {s.casefold() for s in self.sheet_names} or rid not in relations or relations[rid][0] != "worksheet":
                raise PrivacyError("Tên sheet hoặc liên kết worksheet không hợp lệ.")
            self.sheet_names.append(name)
            if sheet.attrs.get("state", "visible") != "visible":
                self.hidden_sheets.append(name)
            part = relations[rid][1]
            if part in sheet_parts:
                raise PrivacyError("Nhiều sheet tham chiếu cùng một worksheet.")
            sheet_parts.add(part)
            self.part_sheets[part] = name
            state = sheet.attrs.get("state", "visible")
            self.sheet_states[part] = state if state in SHEET_STATES else "hidden"
            xml = self.xml[part]
            cells, count = {}, 0
            grid = self.grid.setdefault(part, [])
            self.merges[part] = [n.attrs.get("ref", "") for n in xml.root.descendants("mergeCell") if n.attrs.get("ref")]
            self.columns[part] = [dict(n.attrs) for n in xml.root.descendants("col")]
            for cell in xml.root.descendants("c"):
                address = cell.attrs.get("r", "")
                if not re.fullmatch(r"[A-Z]{1,3}[1-9][0-9]{0,6}", address) or address in cells:
                    raise PrivacyError(f"Địa chỉ ô bị thiếu, trùng hoặc không hợp lệ trong sheet {name}.")
                column, row_number = re.fullmatch(r"([A-Z]+)(\d+)", address).groups()
                column_number = 0
                for char in column:
                    column_number = column_number * 26 + ord(char) - 64
                if column_number > 16384 or int(row_number) > 1048576:
                    raise PrivacyError(f"Địa chỉ ô vượt giới hạn Excel trong sheet {name}.")
                location = f"{name}!{address}"
                self.locations[(part, cell.start)] = location
                count += 1
                self.cell_count += 1
                if self.cell_count > 200_000:
                    raise PrivacyError("Workbook vượt 200.000 ô.")
                if count > 200_000:
                    raise PrivacyError("Sheet vượt 200.000 ô.")
                formula, val = cell.child("f"), cell.child("v")
                style_index = cell.attrs.get("s", "0")
                position = (int(row_number), column_number, address)
                if formula is not None:
                    self.formulas.append((part, cell, formula, location))
                    cache = cell.child("is")
                    cache_text = "".join(n.text for n in cache.descendants("t")) if cache else (val.text if val else None)
                    grid.append((*position, "f", (decode_string(formula.text), cell.attrs.get("t", "n"), cache_text),
                                 style_index))
                    cells[address] = ""
                    continue
                typ = cell.attrs.get("t", "n")
                if typ == "s":
                    try:
                        index = int(val.text) if val else -1
                        if index < 0:
                            raise ValueError()
                        item = strings[index]
                    except (ValueError, IndexError):
                        raise PrivacyError(f"Shared string không hợp lệ tại {location}.") from None
                    item.locations.append(location)
                    grid.append((*position, "t", self.shared_index[index], style_index))
                elif typ == "inlineStr":
                    inline = cell.child("is")
                    item = Value(part, self._rich_nodes(inline) if inline else [], [location], cell=cell)
                    grid.append((*position, "t", len(self.values), style_index))
                    self.values.append(item)
                    if inline:
                        for phonetic in inline.descendants("rPh"):
                            self.values.append(Value(part, list(phonetic.descendants("t")), [location + ": phiên âm"], "phonetic"))
                elif typ == "str" and val:
                    item = Value(part, [val], [location], cell=cell)
                    grid.append((*position, "t", len(self.values), style_index))
                    self.values.append(item)
                elif typ in {"n", ""} and val:
                    if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", val.text.strip()):
                        raise PrivacyError(f"Ô số có dữ liệu không hợp lệ tại {location}.")
                    try:
                        style = int(cell.attrs.get("s", "0"))
                    except ValueError:
                        raise PrivacyError(f"Style không hợp lệ tại {location}.") from None
                    item = Value(part, [val], [location], "number", cell, protected_number=style in self.protected_styles)
                    grid.append((*position, "n", len(self.values), style_index))
                    self.values.append(item)
                    self.numeric_count += 1
                elif typ in {"b", "e", "d"} or val is None:
                    if val is not None:
                        grid.append((*position, typ, val.text, style_index))
                    cells[address] = val.text if val else ""
                    continue
                else:
                    raise PrivacyError(f"Kiểu ô chưa hỗ trợ tại {location}: {typ}.")
                cells[address] = item.text
            # Labels guide suggestions only. Replacement always remains per-cell.
            for address, text in cells.items():
                if re.search(r"(?:mã\s*số\s*thuế|MST|số\s*tài\s*khoản|STK|CCCD|CMND|hộ\s*chiếu|điện\s*thoại)\s*[:：]?\s*$", text, re.I):
                    match = re.fullmatch(r"([A-Z]+)(\d+)", address)
                    col = 0
                    for char in match[1]:
                        col = col * 26 + ord(char) - 64
                    nxt, letters = col + 1, ""
                    while nxt:
                        nxt, rem = divmod(nxt - 1, 26)
                        letters = chr(65 + rem) + letters
                    adjacent = cells.get(letters + match[2], "")
                    if adjacent:
                        self.suggestion_texts.append(text.rstrip(" :：") + ": " + adjacent)
            for node in xml.nodes:
                if local(node.name) in {"oddHeader", "oddFooter", "evenHeader", "evenFooter", "firstHeader", "firstFooter"}:
                    self.values.append(Value(part, [node], [f"{name}: {local(node.name)}"], "header/footer"))
        # Reject an unreferenced worksheet: it can carry data outside the visible UI.
        if {p for p in self.parts if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", p)} != sheet_parts:
            raise PrivacyError("XLSX chứa worksheet không được workbook tham chiếu; không thể kiểm tra đầy đủ.")
        for index, item in enumerate(strings):
            if not item.locations:
                item.locations.append(f"Shared string {index} (không còn ô tham chiếu)")

    def _read_metadata(self):
        for part, xml in self.xml.items():
            if re.fullmatch(r"xl/comments(?:/comment)?\d*\.xml", part) or part.startswith("xl/comments/"):
                for node in xml.root.descendants("author"):
                    self.values.append(Value(part, [node], [f"{part}: tác giả ghi chú"], "comment author"))
                for comment in xml.root.descendants("comment"):
                    text = comment.child("text")
                    if text:
                        self.values.append(Value(part, self._rich_nodes(text), [f"{part}: ghi chú {comment.attrs.get('ref', '?')}"], "comment"))
            elif part == "docProps/core.xml":
                for node in xml.root.children:
                    if not node.children and local(node.name) not in {"created", "modified", "lastPrinted", "revision"}:
                        self.values.append(Value(part, [node], [f"Thuộc tính: {local(node.name)}"], "metadata"))
            elif part == "docProps/app.xml":
                for node in xml.root.children:
                    if local(node.name) in {"Company", "Manager", "Template", "HyperlinkBase"} and not node.children:
                        self.values.append(Value(part, [node], [f"Thuộc tính: {local(node.name)}"], "metadata"))
            elif part == "docProps/custom.xml":
                for prop in xml.root.children:
                    if "name" in prop.attrs:
                        self.values.append(Value(part, [prop], ["Tên thuộc tính riêng"], "metadata", attribute="name"))
                    for node in prop.children:
                        if local(node.name) in {"lpstr", "lpwstr", "bstr"} and not node.children:
                            self.values.append(Value(part, [node], [f"Thuộc tính riêng: {prop.attrs.get('name', '?')}"], "metadata"))

    def _read_drawings(self):
        for part, xml in self.xml.items():
            if not re.fullmatch(r"xl/drawings/drawing\d+\.xml", part) or part in self.unsupported:
                continue
            labels = []
            for relpart, rels in self.relationships.items():
                if any(kind == "drawing" and target == part for kind, target in rels.values()):
                    sheetpart = relpart.replace("/_rels/", "/").removesuffix(".rels")
                    labels.append(self.part_sheets.get(sheetpart, sheetpart))
            prefix = ", ".join(labels) or part
            for index, node in enumerate(xml.nodes):
                if node.name == DRAW + "}p":
                    runs = [n for n in node.descendants() if n.name == DRAW + "}t"]
                    if runs:
                        self.values.append(Value(part, runs, [f"{prefix}: hình vẽ, đoạn {index}"], "drawing text"))
                elif node.name == SHEET_DRAW + "}cNvPr":
                    for attr in ("name", "descr", "title"):
                        if attr in node.attrs:
                            self.values.append(Value(part, [node], [f"{prefix}: hình vẽ {node.attrs.get('id', '?')} @{attr}"], "drawing metadata", attribute=attr))

    def _read_external_links(self):
        for part, ident, target in self.external_targets:
            self.disclosures.append({"location": f"{part}: {ident}", "kind": "external_link",
                "reason": "Đường dẫn/tên workbook nguồn được giữ nguyên cùng liên kết ngoài; có thể chứa tên người, công ty hoặc thư mục nội bộ.", "value": target})
        for part in sorted(self.external_parts):
            for start, end, _ in self.xml[part].comments:
                self.disclosures.append({"location": part + ": XML comment", "kind": "external_metadata",
                    "reason": "Ghi chú XML của liên kết ngoài được giữ nguyên và chưa được Mask.",
                    "value": self.parts[part][start + 4:end - 3].decode("utf-8")})
            if part.endswith(".rels"):
                continue
            for node in self.xml[part].nodes:
                tag = local(node.name)
                fields = []
                if tag == "sheetName":
                    fields.append((" @val", node.attrs.get("val", "")))
                elif tag == "definedName":
                    fields.extend((" @" + name, value) for name, value in node.attrs.items() if name in {"name", "refersTo"})
                if node.text.strip():
                    fields.append(("", node.text))
                for suffix, text in fields:
                    if not text:
                        continue
                    parent = node.parent
                    address = ""
                    while parent:
                        if local(parent.name) == "cell":
                            address = " ô " + parent.attrs.get("r", "?")
                        if local(parent.name) == "sheetData":
                            address = " sheetId " + parent.attrs.get("sheetId", "?") + address
                            break
                        parent = parent.parent
                    self.disclosures.append({"location": f"{part}: {tag}{address}{suffix}", "kind": "external_cache",
                        "reason": "Tên hoặc dữ liệu cache của workbook ngoài được giữ nguyên; chưa được Mask và không được truy cập/cập nhật từ nguồn.",
                        "value": decode_string(text)})
        for part, cell, formula, location in self.formulas:
            if re.search(r"\[(?:\d+|[^\]]+\.xlsx?)\]", formula.text, re.I):
                self.disclosures.append({"location": location, "kind": "external_formula",
                    "reason": "Giữ nguyên công thức tham chiếu workbook ngoài; công thức có thể chứa tên nguồn hoặc tên sheet.",
                    "value": decode_string(formula.text)})

    def _read_protected(self):
        """Show human-readable immutable values, so formula-only names are reviewable."""
        def add(location, text, suggest=True):
            text = decode_string(text)
            if text.strip():
                self.protected_preview.append((location, text))
                if suggest:
                    self.suggestion_texts.append(text)

        for name in self.sheet_names:
            add("Tên sheet — giữ nguyên", name)
        for part, cell, formula, location in self.formulas:
            add(location + " công thức — giữ nguyên", formula.text, False)
            self.suggestion_texts.extend(literal.replace('""', '"') for literal in re.findall(r'"((?:[^\"]|"")*)"', formula.text))
            val = cell.child("v")
            if val and cell.attrs.get("t") == "str":
                add(location + " kết quả chữ công thức — sẽ xóa cache", val.text)
        for part, xml in self.xml.items():
            for node in xml.nodes:
                tag = local(node.name)
                if tag == "definedName":
                    add("Tên vùng — giữ nguyên", node.attrs.get("name", ""))
                    add("Nội dung tên vùng — giữ nguyên", node.text, False)
                    self.suggestion_texts.extend(literal.replace('""', '"') for literal in re.findall(r'"((?:[^\"]|"")*)"', node.text))
                elif tag in {"dataValidation", "tableColumn", "hyperlink"}:
                    for name in ("errorTitle", "error", "promptTitle", "prompt", "display", "tooltip", "name"):
                        if name in node.attrs:
                            add(f"{part}: {tag} @{name} — giữ nguyên", node.attrs[name])
                elif tag in {"formula1", "formula2"}:
                    add(f"{part}: {tag} — giữ nguyên", node.text, False)
                    self.suggestion_texts.extend(literal.replace('""', '"') for literal in re.findall(r'"((?:[^\"]|"")*)"', node.text))
                elif tag == "numFmt" and "formatCode" in node.attrs:
                    add("Định dạng số — giữ nguyên", node.attrs["formatCode"], False)
                    self.suggestion_texts.extend(literal.replace('""', '"') for literal in re.findall(r'"((?:[^\"]|"")*)"', node.attrs["formatCode"]))
                elif part == "docProps/custom.xml" and tag == "property":
                    for child in node.children:
                        if local(child.name) not in {"lpstr", "lpwstr", "bstr"} and child.text.strip():
                            add("Thuộc tính riêng có kiểu dữ liệu — giữ nguyên", node.attrs.get("name", "") + ": " + child.text)

    def _preview(self, replacements, masked=False):
        rows, length, truncated = [], 0, False
        def append(row):
            nonlocal length, truncated
            if length + len(row) + 1 > MAX_TEXT - 160:
                truncated = True
                return False
            rows.append(row)
            length += len(row) + 1
            return True
        for index, value in enumerate(self.values):
            text = replacements.get(index, value.text)
            if not text:
                continue
            for location in value.locations:
                if not append(f"{location} [{value.kind}]: {text}"):
                    break
            if truncated:
                break
        if self.protected_preview and not truncated:
            append("\nCẤU TRÚC ĐƯỢC GIỮ NGUYÊN / CACHE CÔNG THỨC:")
            for location, text in self.protected_preview:
                if not append(f"{location}: " + ("[Đã xóa cache chữ]" if masked and "sẽ xóa cache" in location else text)):
                    break
        if truncated:
            rows.append("[Bản xem trước đã rút gọn; toàn bộ workbook vẫn được kiểm tra và Mask.]")
            self.preview_truncated = True
        return "\n".join(rows)

    BUILTIN_DATE = set(range(14, 18)) | {22} | set(range(27, 37)) | set(range(50, 59))
    BUILTIN_TIME = set(range(18, 22)) | set(range(45, 48))

    def _style_kinds(self):
        """Style index -> 'date' | 'datetime' | 'time' | 'percent' | 'grouped' | 'grouped_decimal'."""
        if hasattr(self, "_kinds"):
            return self._kinds
        xml, kinds = self.xml.get("xl/styles.xml"), {}
        if xml:
            codes = {n.attrs.get("numFmtId", ""): n.attrs.get("formatCode", "") for n in xml.root.descendants("numFmt")}
            xfs = xml.root.child("cellXfs")
            for index, node in enumerate(xfs.children if xfs else []):
                fmt = node.attrs.get("numFmtId", "0")
                code = re.sub(r'"[^"]*"|\\.|\[[^\]]*\]', "", codes.get(fmt, "")).lower()
                number = int(fmt) if fmt.isdigit() else -1
                has_date = bool(re.search(r"[dy]", code)) or number in self.BUILTIN_DATE
                has_time = bool(re.search(r"[hs]", code)) or number in self.BUILTIN_TIME or number == 22
                if has_date:
                    kinds[str(index)] = "datetime" if has_time else "date"
                elif has_time:
                    kinds[str(index)] = "time"
                elif number in {9, 10} or code.endswith("%"):
                    kinds[str(index)] = "percent"
                elif number in {3, 38, 37} or ("#,##0" in code and "." not in code):
                    kinds[str(index)] = "grouped"
                elif number in {4, 39, 40} or "#,##0." in code:
                    kinds[str(index)] = "grouped_decimal"
        self._kinds = kinds
        return kinds

    def _date1904(self):
        pr = self.xml["xl/workbook.xml"].root.child("workbookPr")
        return bool(pr and pr.attrs.get("date1904", "0").lower() in {"1", "true"})

    def _ai_removed(self):
        """Content the AI export does not copy and that may matter to the user."""
        labels = []
        for reason in self.unsupported.values():
            labels.append(reason.split(":", 1)[0])
        if self.external_parts or self.external_targets:
            labels.append("Liên kết workbook ngoài và dữ liệu cache của chúng")
        if any(v.kind in {"drawing text", "drawing metadata"} for v in self.values):
            labels.append("Hình vẽ và chữ trong hình vẽ")
        if any(v.kind == "header/footer" for v in self.values):
            labels.append("Đầu trang / chân trang")
        if self.binary_parts:
            labels.append("Thiết lập máy in")
        return list(dict.fromkeys(labels))

    def _ai_plan(self, active, expression, previews):
        """Values-only workbook plan: every string is masked with the same rules."""
        tokens = {}

        masked_cache = {}

        def mask_text(text):
            if not expression or not text:
                return text
            if text not in masked_cache:
                found = list(expression.finditer(text))
                for m in found:
                    tokens[key(active[int(m.lastgroup[1:])]["source"])] = True
                masked_cache[text] = (expression.sub(lambda m: active[int(m.lastgroup[1:])]["token"], text)
                                      if found else text)
            return masked_cache[text]

        number_rules = {self._number_key(r["source"]): r for r in active}
        number_rules.pop(None, None)
        kinds, offset = self._style_kinds(), DATE_1904_OFFSET if self._date1904() else 0
        taken, sheets, formulas = set(), [], []
        from .excel_values import safe_sheet_name

        def number_cell(text, style):
            # Any number whose digits equal a selected identifier becomes its alias
            # ("1234567890.00", "-1234567890" included): AI output has no formulas to break.
            rule = number_rules.get(self._number_key(text))
            if rule is not None:
                tokens[key(rule["source"])] = True
                return "s", rule["token"], None
            fmt = kinds.get(style)
            if fmt in {"date", "datetime"} and offset:
                text = repr(float(text) + offset)
            return "n", text, fmt

        def literal_cell(kind, value):
            # Only genuine Excel booleans/error codes are copied as such; anything else is text.
            text = decode_string(str(value)).strip()
            if kind == "e" and text in EXCEL_ERRORS:
                return "e", text, None
            if kind == "b" and text in {"0", "1"}:
                return "b", text, None
            return "s", mask_text(text), None

        shared = {i: previews.get(i, v.text) for i, v in enumerate(self.values)}
        for part, name in self.part_sheets.items():
            masked_name = safe_sheet_name(mask_text(name), taken)
            cells = []
            for row, col, address, kind, payload, style in self.grid.get(part, []):
                if kind == "t":
                    text = shared[payload]
                    if text:
                        cells.append((row, col, "s", text, None))
                elif kind == "n":
                    cells.append((row, col, *number_cell(self.values[payload].text, style)))
                elif kind in {"b", "e"}:
                    cells.append((row, col, *literal_cell(kind, payload)))
                elif kind == "d":
                    cells.append((row, col, "s", mask_text(decode_string(payload)), None))
                elif kind == "f":
                    formula, cache_kind, cache = payload
                    formulas.append((masked_name, address, "=" + mask_text(formula)))
                    if cache is None:
                        continue
                    if cache_kind in {"str", "inlineStr"}:
                        cells.append((row, col, "s", mask_text(decode_string(cache)), None))
                    elif cache_kind in {"b", "e"}:
                        cells.append((row, col, *literal_cell(cache_kind, cache)))
                    elif cache_kind == "s" and cache.strip().isdigit() and int(cache) < len(self.shared_index):
                        cells.append((row, col, "s", shared[self.shared_index[int(cache)]], None))
                    elif re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", cache.strip()):
                        cells.append((row, col, *number_cell(cache.strip(), style)))
            sheets.append({"name": masked_name, "state": self.sheet_states.get(part, "visible"),
                           "cells": cells, "merges": self.merges.get(part, []), "cols": self.columns.get(part, [])})
        if formulas:
            rows = [(1, 1, "s", "Sheet", None), (1, 2, "s", "Ô", None), (1, 3, "s", "Công thức (đã Mask)", None)]
            for index, (sheet, address, formula) in enumerate(formulas[:100_000], 2):
                rows += [(index, 1, "s", sheet, None), (index, 2, "s", address, None), (index, 3, "s", formula, None)]
            sheets.append({"name": safe_sheet_name("Cong_thuc", taken), "state": "visible", "cells": rows,
                           "cols": [{"min": "1", "max": "1", "width": "18"}, {"min": "3", "max": "3", "width": "60"}],
                           "frozen_header": True})
        notes = [(v.locations[0], previews.get(i, v.text)) for i, v in enumerate(self.values)
                 if v.kind == "comment" and v.text.strip()]
        if notes:
            rows = [(1, 1, "s", "Vị trí", None), (1, 2, "s", "Ghi chú (đã Mask)", None)]
            for index, (where, text) in enumerate(notes, 2):
                rows += [(index, 1, "s", mask_text(where), None), (index, 2, "s", text, None)]
            sheets.append({"name": safe_sheet_name("Ghi_chu", taken), "state": "visible", "cells": rows,
                           "cols": [{"min": "1", "max": "1", "width": "30"}, {"min": "2", "max": "2", "width": "70"}]})
        blockers = []
        for sheet in sheets:
            for text in [sheet["name"]] + [c[3] for c in sheet["cells"] if c[2] == "s"]:
                if expression and expression.search(TOKEN.sub(" ", str(text))):
                    blockers.append({"location": f"Bản cho AI: {sheet['name']}", "reason": "Cụm đã chọn vẫn còn.",
                                     "value": str(text)[:200]})
        renamed = [(n, s["name"]) for n, s in zip(self.part_sheets.values(), sheets) if n != s["name"]]
        return {"sheets": sheets, "removed": self._ai_removed(), "blockers": blockers[:50],
                "applied": set(tokens), "renamed_sheets": renamed}

    def mask(self, rules):
        clean = validate_rules(rules)
        cache_key = tuple((r["source"], r["token"], r["category"], r["enabled"]) for r in clean)
        cached = getattr(self, "_last_mask", None)
        if cached and cached[0] == cache_key:
            return cached[1]  # same rules (e.g. canonical-name edits only): reuse the last result
        result = self._mask(clean)
        self._last_mask = (cache_key, result)
        return result

    def _mask(self, rules):
        active = sorted((r for r in rules if r["enabled"]), key=lambda r: len(r["source"]), reverse=True)
        expression = re.compile("|".join(f"(?P<R{i}>{literal_pattern(r['source'])})" for i, r in enumerate(active)), re.I) if active else None
        patches = {p: [] if p in self.external_parts else list(x.comments) for p, x in self.xml.items()}
        changes, blockers, applied, previews = [], [], set(), {}
        count, numeric_changed = 0, 0

        seen_texts = {}

        def apply_text(text):
            # Repeated strings (names in many cells, formula caches) are matched once.
            if text not in seen_texts:
                matches = list(expression.finditer(text)) if expression else []
                seen_texts[text] = (matches, expression.sub(lambda m: active[int(m.lastgroup[1:])]["token"], text)
                                    if matches else text)
            return seen_texts[text]

        for index, value in enumerate(self.values):
            before = value.text
            if value.kind == "header/footer" and expression:
                chunks, header_matches = [], []
                for group in header_groups(before):
                    pieces = [text for control, text in group if not control]
                    found = list(expression.finditer("".join(pieces)))
                    header_matches.extend(found)
                    values = iter(replace_pieces(pieces, found, active))
                    chunks.append("".join(text if control else next(values).replace("&", "&&") for control, text in group))
                if header_matches:
                    after = "".join(chunks)
                    patches[value.part].append(self.xml[value.part].text_patch(value.nodes[0], after))
                    previews[index] = after
                    applied.update(key(active[int(m.lastgroup[1:])]["source"]) for m in header_matches)
                    count += len(header_matches)
                    changes.append({"location": value.locations[0], "before": before, "after": after, "kind": value.kind, "numeric": False})
                continue
            matches, after = apply_text(before)
            if not matches:
                continue
            if value.kind == "number":
                eligible = [r for r in active if r["category"] in ID_CATEGORIES and r["source"].strip() == before.strip()]
                if not eligible or value.protected_number:
                    blockers.append({"location": value.locations[0], "value": before,
                                     "reason": "Giữ số liệu tài chính/ngày/tỷ lệ. Chỉ thay toàn bộ ô số nguyên khi chọn đúng nhóm mã định danh và không có định dạng tài chính."})
                    continue
                rule = eligible[0]
                after = rule["token"]
                xml = self.xml[value.part]
                patches[value.part].append(xml.attr_patch(value.cell, "t", "inlineStr"))
                node = value.nodes[0]
                prefix = value.cell.qname.rpartition(":")[0]
                q = prefix + ":" if prefix else ""
                replacement = f"<{q}is><{q}t>".encode() + encode_string(after) + f"</{q}t></{q}is>".encode()
                patches[value.part].append((node.start, node.end, replacement))
                applied.add(key(rule["source"]))
                occurrences = 1
                numeric_changed += len(value.locations)
            else:
                pieces = value.strings()
                # Assign the replacement to the run where its first character was.
                # Other text and every run's rPr formatting remain in place.
                updated = replace_pieces(pieces, matches, active)
                applied.update(key(active[int(m.lastgroup[1:])]["source"]) for m in matches)
                xml = self.xml[value.part]
                for node, old, new in zip(value.nodes, pieces, updated):
                    if old != new:
                        patches[value.part].append(xml.attr_patch(node, value.attribute, new) if value.attribute else xml.text_patch(node, new))
                        if not value.attribute and local(node.name) == "t" and new != new.strip() and node.attrs.get("http://www.w3.org/XML/1998/namespace}space") != "preserve":
                            patches[value.part].append(xml.attr_patch(node, "xml:space", "preserve"))
                occurrences = len(matches)
            previews[index] = after
            for location in value.locations:
                changes.append({"location": location, "before": before, "after": after,
                                "kind": value.kind, "numeric": value.kind == "number"})
            count += occurrences * max(1, len(value.locations))

        # Formula caches are what AI tools read (pandas/openpyxl do not recalculate).
        # Mask text caches in place; keep numeric caches unless the cached value is
        # itself a selected numeric identifier. Formula source and attributes survive.
        id_values = {self._number_key(r["source"]) for r in active if r["category"] in ID_CATEGORIES}
        id_values.discard(None)
        for part, cell, formula, location in self.formulas:
            xml = self.xml[part]
            kind = cell.attrs.get("t", "n")
            for node in cell.children:
                name = local(node.name)
                if name not in {"v", "is"}:
                    continue
                if name == "v" and kind == "str":
                    cached = decode_string(node.text)
                    found = list(expression.finditer(cached)) if expression else []
                    if found:
                        after = expression.sub(lambda m: active[int(m.lastgroup[1:])]["token"], cached)
                        patches[part].append(xml.text_patch(node, after))
                        applied.update(key(active[int(m.lastgroup[1:])]["source"]) for m in found)
                        changes.append({"location": location, "before": cached, "after": after,
                                        "kind": "formula cache", "numeric": False})
                elif name == "v" and kind in {"n", ""}:
                    if self._number_key(node.text) in id_values:
                        patches[part].append((node.start, node.end, b""))
                        changes.append({"location": location, "before": node.text, "after": "",
                                        "kind": "formula cache", "numeric": True})
                elif name == "is" or kind in {"s", "inlineStr"}:
                    cached_text = "".join(n.text for n in node.descendants("t")) if name == "is" else node.text
                    if expression and expression.search(decode_string(cached_text)):
                        patches[part].append((node.start, node.end, b""))
        if self.formulas:
            xml = self.xml["xl/workbook.xml"]
            calc = xml.root.child("calcPr")
            if calc:
                for name, val in (("fullCalcOnLoad", "1"), ("forceFullCalc", "1")):
                    patches[xml.part].append(xml.attr_patch(calc, name, val))
            else:
                prefix = xml.root.qname.rpartition(":")[0]
                q = prefix + ":" if prefix else ""
                payload = f'<{q}calcPr fullCalcOnLoad="1" forceFullCalc="1"/>'.encode()
                # calcPr precedes the optional workbook extension list.
                ext = xml.root.child("extLst")
                at = ext.start if ext else xml.root.end_start
                patches[xml.part].append((at, at, payload))
        for part, reason in self.unsupported.items():
            blockers.append({"location": part, "reason": reason + " Dùng chế độ «Cho AI» để bỏ thành phần này.",
                             "value": ""})
        output_parts = {p: patched(raw, patches.get(p, [])) for p, raw in self.parts.items()}
        audit_blockers, audit_disclosures = self._audit(output_parts, expression, active)
        blockers.extend(audit_blockers)
        disclosures = list(self.disclosures)
        disclosures.extend(audit_disclosures)
        disclosures = list({(d["location"], d["value"], d["kind"]): d for d in disclosures}.values())
        unique = {}
        for blocker in blockers:
            unique[(blocker["location"], blocker["value"])] = blocker
        blockers = list(unique.values())
        warnings = list(self.warnings)
        if numeric_changed:
            warnings.append(f"Đã đổi {numeric_changed} ô mã định danh dạng số sang chuỗi Mask. Kết quả công thức lưu sẵn được giữ, trừ các kết quả trùng đúng mã đã Mask. Nếu mở bằng Excel và tính lại, công thức tham chiếu các ô này có thể đổi kết quả; cần xác nhận riêng.")
        summary = {**self.summary, "numeric_ids_changed": numeric_changed, "changed_values": len(changes), "blocker_count": len(blockers), "disclosure_count": len(disclosures)}
        output = None
        if not blockers:
            stream = io.BytesIO()
            with zipfile.ZipFile(stream, "w") as archive:
                for info in self.infos:
                    # No original filename, ZIP comments or arbitrary extra fields.
                    clean = zipfile.ZipInfo(info.filename, info.date_time)
                    clean.compress_type = zipfile.ZIP_DEFLATED
                    clean.external_attr = info.external_attr
                    archive.writestr(clean, output_parts[info.filename])
            output = stream.getvalue()
        plan = self._ai_plan(active, expression, previews)
        masked_texts = [previews.get(i, v.text) for i, v in enumerate(self.values) if v.kind != "number"]
        masked_texts += [sheet["name"] for sheet in plan["sheets"]]
        # Everything else the AI file contains as text (formula results, date cells, notes), and the
        # string literals of formulas; formula syntax itself (SUM, VLOOKUP…) is not a leftover.
        for sheet in plan["sheets"]:
            for cell in sheet["cells"]:
                if cell[2] == "s" and not str(cell[3]).startswith("="):
                    masked_texts.append(str(cell[3]))
                elif cell[2] == "s":
                    masked_texts += [lit.replace('""', '"') for lit in re.findall(r'"((?:[^"]|"")*)"', cell[3])]
        masked_texts = list(dict.fromkeys(masked_texts))
        ai = {"removed": plan["removed"], "blockers": plan["blockers"], "renamed_sheets": plan["renamed_sheets"],
              "sheet_count": len(plan["sheets"])}
        result = ExcelMaskResult(output, self._preview(previews, True), count, applied, changes,
                                 blockers, warnings, summary, disclosures, masked_texts, ai, plan)
        # Catalogue learning in AI mode counts what the AI file replaced (values, names, formula text).
        value_sources = {key(r["source"]) for i in previews for r in active
                         if re.search(literal_pattern(r["source"]), self.values[i].text, re.I)}
        result.ai_applied = value_sources | plan["applied"]
        return result

    @staticmethod
    def _number_key(text):
        """Canonical digits of an integer-like value, e.g. '1234567890.0' -> '1234567890'."""
        value = str(text).strip()
        match = re.fullmatch(r"[+-]?(\d+)(?:\.0*)?", value)
        return (match[1].lstrip("0") or "0") if match else None

    @staticmethod
    def _part_matches(raw, expression):
        """Exact, fast audit pre-scan: the same node text / attribute / namespace values as
        _audit (expat, identical decoding), without building the node tree."""
        class Found(Exception):
            pass
        stack = []

        def check(text):
            if text and expression.search(TOKEN.sub("", decode_string(text))):
                raise Found()

        def start(name, attrs):
            stack.append([])
            for value in attrs.values():
                check(value)

        def end(name):
            check("".join(stack.pop()))

        def chars(data):
            if stack:
                stack[-1].append(data)

        parser = expat.ParserCreate(namespace_separator="}")
        parser.StartElementHandler, parser.EndElementHandler = start, end
        parser.CharacterDataHandler = chars
        parser.StartNamespaceDeclHandler = lambda prefix, uri: check(uri or "")
        try:
            parser.Parse(raw, True)
        except Found:
            return True
        except (expat.ExpatError, ValueError, IndexError):
            return True  # let the full audit report the problem
        return False

    def _audit(self, parts, expression, active):
        if not expression:
            return [], []
        result, disclosures = [], []
        for part, raw in parts.items():
            if part in self.binary_parts:
                continue
            external = part in self.external_parts
            if not external and not self._part_matches(raw, expression):
                continue
            xml = self.xml[part] if raw == self.parts[part] else XML(raw, part)
            for uri in xml.namespaces:
                if expression.search(TOKEN.sub("", decode_string(uri))):
                    finding = {"location": part + ": namespace", "reason": "Cụm đã chọn còn trong namespace XML bất biến.", "value": uri}
                    if external:
                        disclosures.append({**finding, "kind": "external_metadata"})
                    else:
                        result.append(finding)
            for node in xml.nodes:
                loc = f"{part}: {local(node.name)}"
                if local(node.name) == "sheet":
                    loc = "Tên sheet: " + node.attrs.get("name", "?")
                else:
                    parent = node
                    while parent:
                        if local(parent.name) == "c" and "r" in parent.attrs:
                            sheet = self.part_sheets.get(part, "Worksheet")
                            loc = f"{sheet}!{parent.attrs['r']}: {local(node.name)}"
                            break
                        parent = parent.parent
                candidates = [("", node.text)] + [(" @" + local(attr), text) for attr, text in node.attrs.items()]
                for suffix, raw_text in candidates:
                    value = decode_string(unquote(raw_text) if external else raw_text)
                    if expression.search(TOKEN.sub("", value)):
                        reason = "Cụm đã chọn còn trong cấu trúc bất biến. Không tự đổi tên sheet, công thức, tên vùng hoặc metadata liên quan đến cấu trúc."
                        formula_text = not suffix and local(node.name) in {"f", "formula", "formula1", "formula2", "definedName"}
                        if external or formula_text:
                            disclosures.append({"location": loc + suffix, "value": value,
                                "kind": "external_sensitive" if external else "formula_sensitive",
                                "reason": "Cụm đã chọn vẫn còn trong liên kết/cache workbook ngoài được giữ nguyên." if external else "Cụm đã chọn vẫn còn trong công thức được giữ nguyên. Giá trị này chưa được Mask."})
                        else:
                            result.append({"location": loc + suffix, "reason": reason, "value": value})
        return result, disclosures
