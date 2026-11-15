"""Đọc DOCX không tin cậy trong RAM; không mở liên kết/đối tượng nhúng.

Chuyển có sửa kiểm ZIP/XML của TX-1, nguồn/băm trong NGUON.md.
Chỉ hỗ trợ WordprocessingML transitional; vùng chưa hiểu luôn từ chối.
"""
import hashlib
import io
import json
import posixpath
import re
import stat
import struct
import xml.etree.ElementTree as ET
import zipfile
import zlib

from kho_tri_thuc_sdk.engine import LoiDuongTruyen, LoiNghiepVu, ViecDaHuy
from .cau_truc import (W, W_NS, DanhSo, _DocNoiDung, _gan_vi_tri,
                       _noi_khoi, _sai, _vuot, KY_TU_TOI_DA)

MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
CT = "{" + CT_NS + "}"
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT_DOC = MIME_DOCX + ".main+xml"
TEP_TOI_DA = 20 * 1048576
GIAI_NEN_TOI_DA = 100 * 1048576
XML_TOI_DA = 16 * 1048576
SO_MUC_ZIP_TOI_DA = 2000
TY_LE_NEN_TOI_DA = 200
SO_NUT_XML_TOI_DA = 200000
DO_SAU_XML_TOI_DA = 128
JSON_TOI_DA = 20 * 1048576
_SUA_DOI = set("ins del delText delInstrText moveFrom moveTo cellIns cellDel cellMerge numberingChange conflictIns conflictDel".split())
_ROOT_VUNG = {"document", "hdr", "ftr", "footnotes", "endnotes"}
_ROOT_PHU = {"styles", "numbering", "settings", "fonts", "webSettings"}
_KIEU_VUNG = {"header": "hdr", "footer": "ftr", "footnotes": "footnotes", "endnotes": "endnotes"}


def _chua_chot():
    raise LoiNghiepVu("DC_WORD_CHUA_CHOT", "Bản Word còn sửa đổi hoặc bình luận. Anh chọn bản đã chốt để đối chiếu.")


class _BoDungCay(ET.TreeBuilder):
    def __init__(self, kiem_huy, ngan_sach):
        super().__init__()
        self.kiem_huy, self.ngan_sach = kiem_huy, ngan_sach
        self.sau = 0

    def doctype(self, ten, pubid, system):
        _sai()

    def start(self, ten, thuoc_tinh):
        self.sau += 1
        self.ngan_sach[0] += 1
        if self.sau > DO_SAU_XML_TOI_DA or self.ngan_sach[0] > SO_NUT_XML_TOI_DA:
            _vuot()
        if self.ngan_sach[0] % 128 == 0:
            self.kiem_huy()
        return super().start(ten, thuoc_tinh)

    def end(self, ten):
        self.sau -= 1
        return super().end(ten)


def _doc_xml(z, ten, kiem_huy, ngan_sach, du_lieu):
    info = z.getinfo(ten)
    if info.file_size > XML_TOI_DA:
        _vuot()
    parser = ET.XMLParser(target=_BoDungCay(kiem_huy, ngan_sach))
    # ZipExtFile dừng ở file_size tự khai: không đủ để phát hiện một luồng
    # DEFLATE có đuôi bị giấu. Kiểm header bằng zipfile, rồi giải nén có trần
    # độc lập tới EOF thật và kiểm CRC; không tin kích thước ZIP là sự thật.
    with z.open(info):
        pass
    n, extra = struct.unpack_from("<2H", du_lieu, info.header_offset + 26)
    le = info.header_offset + 30 + n + extra
    het = le + info.compress_size
    if het > z.start_dir:
        _sai()
    da_doc, crc = 0, 0
    decoder = zlib.decompressobj(-15) if info.compress_type == zipfile.ZIP_DEFLATED else None
    while le < het:
        kiem_huy()
        chunk = du_lieu[le:min(le + 65536, het)]
        le += len(chunk)
        while chunk:
            kiem_huy()
            if decoder is None:
                raw, chunk = chunk, b""
            else:
                raw = decoder.decompress(chunk, min(65536, XML_TOI_DA + 1 - da_doc))
                chunk = decoder.unconsumed_tail
                if decoder.unused_data:
                    _sai()
            da_doc += len(raw)
            if da_doc > XML_TOI_DA:
                _vuot()
            if da_doc > info.file_size:
                _sai()
            crc = zlib.crc32(raw, crc)
            parser.feed(raw)
    if da_doc != info.file_size or crc != info.CRC or decoder is not None and not decoder.eof:
        _sai()
    return parser.close()


def _kiem_danh_muc(raw):
    """Chặn số mục/ZIP64 trước khi ZipFile cấp phát danh sách central directory."""
    moc = raw.rfind(b"PK\x05\x06", max(0, len(raw) - 65557))
    if moc < 0 or moc + 22 > len(raw):
        _sai()
    _, dia, dia_muc, so_dia, so_muc, kich, le, ghi_chu = struct.unpack_from("<4s4H2IH", raw, moc)
    if moc + 22 + ghi_chu != len(raw) or dia or dia_muc or so_dia != so_muc:
        _sai()
    if so_muc > SO_MUC_ZIP_TOI_DA:
        _vuot()
    # Không cần ZIP64 với trần 20 MiB/2.000 mục; không nhận gói tự chạy.
    if le + kich != moc or not raw.startswith(b"PK\x03\x04"):
        _sai()
    pos = le
    for _ in range(so_muc):
        if raw[pos:pos + 4] != b"PK\x01\x02" or pos + 46 > moc:
            _sai()
        n, x, c = struct.unpack_from("<3H", raw, pos + 28)
        pos += 46 + n + x + c
    if pos != moc:
        _sai()


def _kiem_zip(z, kiem_huy):
    infos = z.infolist()
    if len(infos) > SO_MUC_ZIP_TOI_DA:
        _vuot()
    ten_da_co, tong = set(), 0
    for i in infos:
        kiem_huy()
        ten = i.filename
        # Không chuẩn hóa tên rồi đoán: từ chối cả alias/case/percent encoding.
        phan = ten.rstrip("/").split("/")
        if (ten.casefold() in ten_da_co or i.orig_filename != ten or
                any(p in ("", ".", "..") for p in phan) or
                any(c in ten for c in ("\\", ":", "%", "?", "#")) or
                any(ord(c) < 32 for c in ten) or
                stat.S_ISLNK(i.external_attr >> 16) or i.flag_bits & 1 or
                i.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)):
            _sai()
        ten_da_co.add(ten.casefold())
        tong += i.file_size
        if (tong > GIAI_NEN_TOI_DA or
                (ten.lower().endswith((".xml", ".rels")) and i.file_size > XML_TOI_DA) or
                i.file_size > TY_LE_NEN_TOI_DA * max(1, i.compress_size)):
            _vuot()
    ten = {i.filename for i in infos if not i.is_dir()}
    if not {"[Content_Types].xml", "_rels/.rels", "word/document.xml"} <= ten:
        _sai()
    return ten


def _quet_chua_chot(cay, kiem_huy):
    for root in cay.values():
        for e in root.iter():
            kiem_huy()
            ns, _, ten = e.tag[1:].partition("}") if e.tag.startswith("{") else ("", "", e.tag)
            # Bao gồm namespace Word mở rộng w14/w15/w16; không phụ thuộc prefix.
            word = "wordprocessing" in ns or "/word/" in ns
            if word and (ten in _SUA_DOI or ten.endswith("Change") or
                         "Range" in ten and ("move" in ten.lower() or "customXml" in ten) or
                         "comment" in ten.lower()):
                _chua_chot()


def _quan_he(cay, ten, kiem_huy):
    ds = {}
    for tep, root in cay.items():
        if not tep.lower().endswith(".rels"):
            continue
        kiem_huy()
        if root.tag != REL + "Relationships":
            _sai()
        if tep == "_rels/.rels":
            chu = ""
        else:
            thu_muc, la = posixpath.split(tep)
            if posixpath.basename(thu_muc) != "_rels":
                _sai()
            chu = posixpath.join(posixpath.dirname(thu_muc), la[:-5])
            if chu not in ten:
                _sai()
        muc = ds.setdefault(chu, {})
        for r in root:
            if r.tag != REL + "Relationship" or r.get("TargetMode", "Internal") != "Internal":
                _sai()
            rid, target, loai = r.get("Id"), r.get("Target", ""), r.get("Type", "")
            if (not rid or rid in muc or not target or not loai or
                    any(c in target for c in ("\\", ":", "%", "?", "#")) or
                    any(ord(c) < 32 for c in target)):
                _sai()
            dich = posixpath.normpath(posixpath.join(posixpath.dirname(chu), target)) if not target.startswith("/") else target[1:]
            if dich.startswith(("../", "/")) or dich not in ten:
                _sai()
            if loai.rsplit("/", 1)[-1] in ("oleObject", "package", "aFChunk", "altChunk", "subDocument", "control", "vbaProject"):
                _sai()
            muc[rid] = (loai, dich)
    # Một tài liệu chính tại vị trí được hỗ trợ; không đoán main part khác.
    main = [v for v in ds.get("", {}).values() if v[0] == R_NS + "/officeDocument"]
    if main != [(R_NS + "/officeDocument", "word/document.xml")]:
        _sai()
    for tep, root in cay.items():
        if root.tag == REL + "Relationships" and not tep.lower().endswith(".rels"):
            _sai()
        for e in root.iter():
            for attr, rid in e.attrib.items():
                if attr.startswith("{" + R_NS + "}") and rid not in ds.get(tep, {}):
                    _sai()
    return ds


def _kieu_noi_dung(cay, ten):
    root = cay["[Content_Types].xml"]
    if root.tag != CT + "Types":
        _sai()
    mac_dinh, rieng = {}, {}
    for e in root:
        if e.tag == CT + "Default":
            khoa, dich = e.get("Extension", "").lower(), mac_dinh
        elif e.tag == CT + "Override":
            khoa, dich = e.get("PartName", ""), rieng
            if not khoa.startswith("/") or khoa[1:] not in ten:
                _sai()
        else:
            _sai()
        if not khoa or khoa in dich or not e.get("ContentType"):
            _sai()
        dich[khoa] = e.get("ContentType")
    kieu = {t: rieng.get("/" + t, mac_dinh.get(t.rsplit(".", 1)[-1].lower())) for t in ten}
    if kieu.get("word/document.xml") != CT_DOC or any(v is None for v in kieu.values()):
        _sai()
    for t, v in kieu.items():
        if "macro" in v.lower() or "oleObject" in v or "vba" in v.lower():
            _sai()
        if (v.endswith("+xml") or v in ("application/xml", "text/xml")) and t not in cay:
            _sai()  # XML trong đuôi khác vẫn phải được quét; không đọc thiếu.
    return kieu


def doc_bytes(du_lieu, kiem_huy, tien_do, *, phien_ban_engine):
    """Bytes thật → phong bì; trả nguyên văn/cấu trúc đã ghim cùng offset."""
    if len(du_lieu) > TEP_TOI_DA:
        _vuot()
    kiem_huy()
    try:
        _kiem_danh_muc(du_lieu)
        with zipfile.ZipFile(io.BytesIO(du_lieu)) as z:
            ten = _kiem_zip(z, kiem_huy)
            tien_do(20, "Đang kiểm tra cấu trúc tệp Word")
            ngan_sach = [0]
            cay = {t: _doc_xml(z, t, kiem_huy, ngan_sach, du_lieu) for t in sorted(ten)
                   if t.lower().endswith((".xml", ".rels"))}
            kieu = _kieu_noi_dung(cay, ten)
            _quet_chua_chot(cay, kiem_huy)
            qh = _quan_he(cay, ten, kiem_huy)
            # Không bỏ sót story bị đổi tên/mất khai báo/đặt sai content type.
            vung = []
            for t, root in cay.items():
                kiem_huy()
                if t.lower().endswith(".rels") or t == "[Content_Types].xml":
                    continue
                local = root.tag.removeprefix(W) if root.tag.startswith(W) else None
                if local in _ROOT_VUNG:
                    if local != "document":
                        loai = next((k for k, v in _KIEU_VUNG.items() if v == local), None)
                        if (kieu[t] != "application/vnd.openxmlformats-officedocument.wordprocessingml." + loai + "+xml" or
                                not any(r == R_NS + "/" + loai and d == t for r, d in qh.get("word/document.xml", {}).values())):
                            _sai()
                    elif t != "word/document.xml":
                        _sai()
                    vung.append((t, local, root))
                elif root.tag.startswith(W) and local not in _ROOT_PHU:
                    _sai()
                elif any(e.tag in {W + s for s in ("t", "p", "r", "tbl", "drawing", "pict", "object", "txbxContent", "fldSimple", "instrText", "sym", "altChunk")} for e in root.iter()):
                    _sai()
                if "wordprocessingml." in kieu[t] and local not in _ROOT_VUNG | _ROOT_PHU:
                    _sai()
                if local in _ROOT_PHU:
                    loai = "fontTable" if local == "fonts" else local
                    if (kieu[t] != "application/vnd.openxmlformats-officedocument.wordprocessingml." + loai + "+xml" or
                            not any(r == R_NS + "/" + loai and d == t for r, d in qh.get("word/document.xml", {}).values())):
                        _sai()
                    if any(e.tag in {W + s for s in ("numStyleLink", "styleLink", "lvlPicBulletId")} for e in root.iter()):
                        _sai()
            if not any(t == "word/document.xml" and l == "document" for t, l, _ in vung):
                _sai()
            for t, l, _ in vung:
                if l == "document" and kieu[t] != CT_DOC:
                    _sai()
            # Quan hệ Word phải trỏ đúng loại cây; không coi một phần sai gốc
            # như header/footnote đã được đọc.
            for _, (r, dich) in qh.get("word/document.xml", {}).items():
                loai = r.removeprefix(R_NS + "/")
                expected = {**_KIEU_VUNG, "styles": "styles", "numbering": "numbering",
                            "settings": "settings", "fontTable": "fonts", "webSettings": "webSettings"}.get(loai)
                if expected is not None and (dich not in cay or cay[dich].tag != W + expected):
                    _sai()
            tien_do(55, "Đang đọc đoạn văn, bảng và chú thích")
            def phu(loai):
                ds = [d for r, d in qh.get("word/document.xml", {}).values() if r == R_NS + "/" + loai]
                if len(ds) > 1:
                    _sai()
                return cay[ds[0]] if ds else None
            danh_so = DanhSo(phu("numbering"), phu("styles"))
            doc = _DocNoiDung(danh_so, kiem_huy)
            khoi, cac_vung = [], []
            # Thân trước; phần phụ theo tên OPC để có thứ tự ổn định, không giả vị trí trang.
            for t, local, root in sorted(vung, key=lambda x: (x[0] != "word/document.xml", x[0])):
                kiem_huy()
                if root.text and root.text.strip() or any(e.tail and e.tail.strip() for e in root):
                    _sai()
                if local == "document":
                    if [e.tag for e in root] != [W + "body"]:
                        _sai()
                    containers = [(None, root[0])]
                elif local in ("footnotes", "endnotes"):
                    tag = "footnote" if local == "footnotes" else "endnote"
                    if any(e.tag != W + tag for e in root):
                        _sai()
                    ids = [e.get(W + "id") for e in root]
                    if None in ids or len(ids) != len(set(ids)):
                        _sai()
                    containers = list(zip(ids, root))
                else:
                    containers = [(None, root)]
                for ma, container in containers:
                    doc.bat_dau_phan()
                    blocks = doc.khoi(container)
                    for k in blocks:
                        k["phan"] = t
                        if ma is not None:
                            k["ma_chu_thich"] = ma
                    cac_vung.append({"phan": t, "loai": local, "ma": ma, "tu_khoi": len(khoi), "so_khoi": len(blocks)})
                    khoi.extend(blocks)
            # Reference không có đích chú thích cũng là đọc thiếu.
            for ten_note in ("footnote", "endnote"):
                ids = {e.get(W + "id") for _, l, r in vung if l == ten_note + "s" for e in r}
                for _, _, root in vung:
                    if any(e.get(W + "id") not in ids for e in root.iter(W + ten_note + "Reference")):
                        _sai()
            text = _noi_khoi(khoi)
            if len(text) > KY_TU_TOI_DA:
                _vuot()
            _gan_vi_tri(khoi)
            ket_qua = {"loai": "van_ban_tai_lieu", "van_ban_tai_lieu": {
                "phien_ban": 1, "van_ban": text, "trang": [], "nguon_doc": "docx",
                "ly_do_chuyen_nguon": None, "so_trang": 0,
                "phien_ban_engine": phien_ban_engine,
                "bam_dau_vao": "sha256:" + hashlib.sha256(du_lieu).hexdigest(),
                "canh_bao": ["Chưa phân trang Word; vị trí theo cấu trúc và offset Unicode, không có số trang hoặc hộp tọa độ."],
                "don_vi_offset": "unicode_code_point", "khoi_docx": khoi, "vung_docx": cac_vung}}
            if len(json.dumps(ket_qua, ensure_ascii=False).encode("utf-8")) > JSON_TOI_DA:
                _vuot()
            kiem_huy()
            return ket_qua
    except (LoiNghiepVu, ViecDaHuy):
        raise
    except (zipfile.BadZipFile, zipfile.LargeZipFile, ET.ParseError, KeyError,
            ValueError, TypeError, OverflowError, RecursionError, OSError, RuntimeError,
            struct.error, zlib.error, NotImplementedError):
        _sai()


def doc_docx(viec, *, phien_ban_engine):
    viec.kiem_huy()
    dv = viec.dau_vao
    tep = dv.get("tep", {}) if isinstance(dv, dict) else {}
    if (not isinstance(dv, dict) or not isinstance(tep, dict) or dv.get("loai") != "tep" or tep.get("mime") != MIME_DOCX or
            not isinstance(tep.get("tep_id"), str) or not tep["tep_id"] or
            type(tep.get("kich_thuoc")) is not int or tep["kich_thuoc"] < 0):
        _sai()
    if tep["kich_thuoc"] > TEP_TOI_DA:
        _vuot()
    viec.tien_do(5, "Đang nhận tệp Word")
    try:
        with viec.mo_tep(tep["tep_id"]) as f:
            raw = f.read(TEP_TOI_DA + 1)
    except LoiDuongTruyen as exc:
        if exc.http_status == 413:
            _vuot()
        raise
    if len(raw) > TEP_TOI_DA:
        _vuot()
    if len(raw) != tep["kich_thuoc"]:
        _sai()
    kq = doc_bytes(raw, viec.kiem_huy, viec.tien_do, phien_ban_engine=phien_ban_engine)
    viec.tien_do(100, "Đã đọc nội dung Word")
    viec.kiem_huy()
    return kq
