"""Dựng bytes DEMO độc lập bằng struct; không tệp tài liệu thật/ghi đĩa."""

import struct
import zlib

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_W = "application/vnd.openxmlformats-officedocument.wordprocessingml."
CT_S = "application/vnd.openxmlformats-officedocument.spreadsheetml."
CT_RELS = "application/vnd.openxmlformats-package.relationships+xml"


def nen_raw(raw):
    nen = zlib.compressobj(wbits=-15)
    return nen.compress(raw) + nen.flush()


def tao_zip(ds):
    """Mỗi dict có thể khai metadata khác bytes thật để dựng ca tấn công."""
    local, central = bytearray(), bytearray()
    for p in ds:
        ten = p["ten"]
        if isinstance(ten, str):
            ten = ten.encode("utf-8")
        raw = p.get("raw", b"DEMO")
        cach = p.get("cach", 0)
        payload = p.get("payload", nen_raw(raw) if cach == 8 else raw)
        extra = p.get("extra", b"")
        comment = p.get("comment", b"")
        du = {"can": 20, "co": 0, "cach": cach, "gio": 0, "ngay": 0x21,
              "crc": zlib.crc32(raw), "nen": len(payload), "dai": len(raw), "n": len(ten)}
        du.update(p.get("chung", {}))
        l = {**du, **p.get("local", {})}
        c = {**du, **p.get("central", {})}
        offset = len(local)
        local.extend(struct.pack("<4s5H3I2H", b"PK\x03\x04", *[l[k] for k in (
            "can", "co", "cach", "gio", "ngay", "crc", "nen", "dai", "n")], len(extra)))
        local.extend(p.get("ten_local", ten))
        local.extend(extra)
        local.extend(payload)
        central.extend(struct.pack("<4s6H3I5H2I", b"PK\x01\x02", p.get("tao", 0x0314),
                                   *[c[k] for k in ("can", "co", "cach", "gio", "ngay", "crc", "nen", "dai", "n")],
                                   len(extra), len(comment), p.get("dia", 0), p.get("noi_bo", 0),
                                   p.get("ngoai", 0o100600 << 16), p.get("offset", offset)))
        central.extend(ten)
        central.extend(extra)
        central.extend(comment)
    return bytes(local + central + struct.pack("<4s4H2IH", b"PK\x05\x06", 0, 0,
                                               len(ds), len(ds), len(central), len(local), 0))


def dong_goi(phan, cach=0):
    return tao_zip([{"ten": ten, "raw": chu.encode() if isinstance(chu, str) else chu,
                     "cach": cach} for ten, chu in phan.items()])


def types_demo(overrides):
    return (f'<Types xmlns="{CT}"><Default Extension="rels" ContentType="{CT_RELS}"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            + ''.join(f'<Override PartName="/{ten}" ContentType="{ct}"/>' for ten, ct in overrides)
            + '</Types>')


def rels_demo(ds):
    return (f'<Relationships xmlns="{REL}">'
            + ''.join(f'<Relationship Id="{rid}" Type="{R}/{loai}" Target="{dich}"/>' for rid, loai, dich in ds)
            + '</Relationships>')


def word_demo(chu="DEMO — Dữ liệu giả", noi_dung=None):
    return {
        "[Content_Types].xml": types_demo([("word/document.xml", CT_W + "document.main+xml")]),
        "_rels/.rels": rels_demo([("rId1", "officeDocument", "word/document.xml")]),
        "word/document.xml": (f'<w:document xmlns:w="{W}" xmlns:r="{R}"><w:body>'
                              + (f'<w:p><w:r><w:t>{chu}</w:t></w:r></w:p>' if noi_dung is None else noi_dung)
                              + '</w:body></w:document>'),
    }


def excel_demo(so_sheet=1, noi_dung="<row><c><is><t>DEMO</t></is></c></row>"):
    sheets = [(f'xl/worksheets/sheet{i}.xml', CT_S + "worksheet+xml") for i in range(1, so_sheet + 1)]
    phan = {
        "[Content_Types].xml": types_demo([("xl/workbook.xml", CT_S + "sheet.main+xml"), *sheets]),
        "_rels/.rels": rels_demo([("rId1", "officeDocument", "xl/workbook.xml")]),
        "xl/_rels/workbook.xml.rels": rels_demo([(f'rId{i}', 'worksheet', f'worksheets/sheet{i}.xml') for i in range(1, so_sheet + 1)]),
        "xl/workbook.xml": f'<workbook xmlns="{S}" xmlns:r="{R}"><sheets>'
            + ''.join(f'<sheet name="DEMO {i}" sheetId="{i}" r:id="rId{i}"/>' for i in range(1, so_sheet + 1))
            + '</sheets></workbook>',
    }
    for i in range(1, so_sheet + 1):
        phan[f'xl/worksheets/sheet{i}.xml'] = f'<worksheet xmlns="{S}"><sheetData>{noi_dung}</sheetData></worksheet>'
    return phan


def them_phan(phan, ten, xml, ct, loai_qh, *, rid="rId9", chu="word/document.xml", dich=None):
    """Bổ sung CT/relationship đúng để lỗi nội dung không bị lỗi ZIP che mất."""
    phan[ten] = xml
    phan["[Content_Types].xml"] = phan["[Content_Types].xml"].replace(
        '</Types>', f'<Override PartName="/{ten}" ContentType="{ct}"/></Types>')
    qh = "_rels/.rels" if not chu else chu.rsplit('/', 1)[0] + '/_rels/' + chu.rsplit('/', 1)[1] + '.rels'
    if qh not in phan:
        phan[qh] = rels_demo([])
    target = dich if dich is not None else (ten if not chu else ten.split('/', 1)[1])
    phan[qh] = phan[qh].replace('</Relationships>',
        f'<Relationship Id="{rid}" Type="{R}/{loai_qh}" Target="{target}"/></Relationships>')
    return phan
