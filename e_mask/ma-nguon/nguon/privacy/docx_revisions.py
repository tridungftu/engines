"""Accept Word tracked changes in memory before reading a DOCX (source 2.6.2).

Inserted/moved-in text is kept; deleted/moved-out text and old property changes
are dropped, as with Word Accept All Changes. Only the in-memory copy changes.
Unsafe or malformed input is returned unchanged; callers must validate it.
This helper does not mask identifiers or preserve revision history.
"""
from __future__ import annotations

import io
import re
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
MAX_ENTRIES, MAX_TOTAL, MAX_PART = 3000, 80 * 1024**2, 15 * 1024**2
MARKUP = re.compile(rb"<(?:\w+:)?(?:ins|del|moveFrom|moveTo|delText|delInstrText|\w+Change|cellIns|cellDel|cellMerge|"
                    rb"(?:customXml)?(?:Ins|Del|MoveFrom|MoveTo)Range(?:Start|End)|move(?:From|To)Range(?:Start|End))[\s/>]")
DROP_WITH_CONTENT = {"del", "moveFrom", "delText", "delInstrText"}   # rejected text
UNWRAP = {"ins", "moveTo"}                                           # accepted text: keep children
MARKERS = {"moveFromRangeStart", "moveFromRangeEnd", "moveToRangeStart", "moveToRangeEnd",
           "customXmlInsRangeStart", "customXmlInsRangeEnd", "customXmlDelRangeStart", "customXmlDelRangeEnd",
           "customXmlMoveFromRangeStart", "customXmlMoveFromRangeEnd", "customXmlMoveToRangeStart",
           "customXmlMoveToRangeEnd", "cellIns", "cellDel", "cellMerge"}
PROPERTY_CHANGES = {"rPrChange", "pPrChange", "sectPrChange", "tblPrChange", "tblPrExChange", "trPrChange",
                    "tcPrChange", "tblGridChange", "numberingChange"}


def local(tag) -> str:
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def _namespaces(data: bytes) -> list[tuple[str, str]]:
    return [value for _, value in ET.iterparse(io.BytesIO(data), events=("start-ns",))]


REVISIONS = {"ins", "del", "moveFrom", "moveTo"}


def _is_w(el, names) -> bool:
    """A WordprocessingML element; the four revision tags match in any namespace, as the input check does."""
    if not isinstance(el.tag, str) or local(el.tag) not in names:
        return False
    return el.tag.startswith(W) or local(el.tag) in REVISIONS


def _accept(root) -> int:
    """Rewrite one XML tree in place, like Word's «Accept All Changes»; returns the marks removed."""
    count = 0

    def walk(node, parent_name=""):
        nonlocal count
        index = 0
        while index < len(node):
            child = node[index]
            name = local(child.tag)
            if _is_w(child, REVISIONS) and parent_name in {"rPr", "trPr"}:
                node.remove(child)  # revision mark on a paragraph mark / table row property
                count += 1
                continue
            if _is_w(child, {"tr"}) and _row_deleted(child):
                node.remove(child)  # deleted table row
                count += 1
                continue
            if _is_w(child, DROP_WITH_CONTENT | PROPERTY_CHANGES | MARKERS):
                node.remove(child)  # rejected text, superseded formatting, range markers
                count += 1
                continue
            if _is_w(child, UNWRAP):
                node.remove(child)  # accepted text: its runs take its place
                for offset, grandchild in enumerate(list(child)):
                    node.insert(index + offset, grandchild)
                count += 1
                continue  # look again at the same index: nested revisions are handled too
            walk(child, name)
            index += 1

    walk(root, local(root.tag))
    return count


def _row_deleted(row) -> bool:
    props = row.find(W + "trPr")
    return props is not None and props.find(W + "del") is not None


def _safe(archive: zipfile.ZipFile) -> bool:
    entries = archive.infolist()
    names = {e.filename for e in entries}
    return (len(entries) <= MAX_ENTRIES and len(names) == len(entries)
            and sum(e.file_size for e in entries) <= MAX_TOTAL
            and not any(e.flag_bits & 1 or e.filename.startswith("/") or ".." in e.filename.split("/")
                        or "\\" in e.filename for e in entries))


def accept_tracked_changes(data: bytes) -> tuple[bytes, int]:
    """(DOCX bytes with every tracked change accepted, number of marks removed); unchanged if none/unsafe."""
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            if not _safe(archive):
                return data, 0
            parts, total = {}, 0
            for entry in archive.infolist():
                name = entry.filename
                if not (name.startswith("word/") and name.endswith(".xml")) or entry.file_size > MAX_PART:
                    continue
                raw = archive.read(entry)
                if not MARKUP.search(raw):
                    continue
                if b"<!DOCTYPE" in raw or b"<!ENTITY" in raw:
                    return data, 0  # caller must reject unsafe input
                for prefix, uri in _namespaces(raw):
                    if prefix and not re.fullmatch(r"ns\d+", prefix):
                        ET.register_namespace(prefix, uri)  # keep w:, w14:, … as written
                root = ET.fromstring(raw)
                count = _accept(root)
                if count:
                    parts[name] = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
                    total += count
            if not parts:
                return data, 0
            out = io.BytesIO()
            with zipfile.ZipFile(out, "w") as target:
                for entry in archive.infolist():
                    target.writestr(entry, parts.get(entry.filename) or archive.read(entry))
            return out.getvalue(), total
    except (zipfile.BadZipFile, ET.ParseError, ValueError, OSError, KeyError):
        return data, 0
