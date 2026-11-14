"""PDF DEMO thuần Python, chuyển bộ sinh từ ma-nguon/tests/test_lop_chu.py.

Chữ ẩn Type0/ToUnicode ở dưới ảnh DEMO; không cần PyMuPDF, font hệ thống
hoặc OCR thật. Mọi dữ liệu là giả, chỉ kiểm parser và vận chuyển Hot Folder.
"""

import io


CONG_TY = "Công ty DEMO Ánh Dương"
TIEN = "1.000.000 VND"
NGAY = "30/10/2026"
DONG_DEMO = ("DEMO - HO SO GIA", CONG_TY, TIEN, NGAY)


def _stream(data, attrs=b""):
    return (b"<< /Length " + str(len(data)).encode("ascii") + b" " + attrs
            + b" >>\nstream\n" + data + b"\nendstream")


def _anh_demo():
    # Nhãn DEMO là ảnh thật, không có ký tự PDF để bản quét bị đọc nhầm.
    mau = [
        ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
        ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
        ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
        ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    ]
    return bytes(0 if c == "1" else 255 for y in range(7) for c in "0".join(m[y] for m in mau))


def pdf_demo(*pages, rotate=0, text_matrices=None, bang=False, chu_bang=True):
    """Mỗi phần tử là tuple dòng; tuple rỗng tạo trang chỉ có ảnh DEMO."""
    table_lines = ((60, 632, "BANG DEMO"), (60, 602, "DEMO"), (190, 602, TIEN),
                   (60, 572, "DEMO"), (190, 572, NGAY)) if bang and chu_bang else ()
    chars = sorted(set("".join(text for lines in pages for text in lines)
                       + "".join(text for _, _, text in table_lines)))
    mapping = "\n".join(f"<{ord(c):04X}> <{c.encode('utf-16-be').hex()}>" for c in chars)
    cmap = ("/CIDInit /ProcSet findresource begin\n12 dict begin\nbegincmap\n"
            "/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def\n"
            "/CMapName /DemoUnicode def\n/CMapType 2 def\n"
            "1 begincodespacerange\n<0000> <FFFF>\nendcodespacerange\n"
            f"{len(chars)} beginbfchar\n{mapping}\nendbfchar\n"
            "endcmap\nCMapName currentdict /CMap defineresource pop\nend\nend").encode("ascii")
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>", b"",
               b"<< /Type /Font /Subtype /Type0 /BaseFont /DEMO /Encoding /Identity-H "
               b"/DescendantFonts [4 0 R] /ToUnicode 6 0 R >>",
               b"<< /Type /Font /Subtype /CIDFontType2 /BaseFont /DEMO /DW 600 "
               b"/CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> "
               b"/FontDescriptor 5 0 R /CIDToGIDMap /Identity >>",
               b"<< /Type /FontDescriptor /FontName /DEMO /Flags 4 /FontBBox [0 -200 1000 900] "
               b"/ItalicAngle 0 /Ascent 800 /Descent -200 /CapHeight 700 /StemV 80 >>",
               _stream(cmap),
               _stream(_anh_demo(), b"/Type /XObject /Subtype /Image /Width 23 /Height 7 "
                       b"/ColorSpace /DeviceGray /BitsPerComponent 8")]
    page_ids = []
    for lines in pages:
        page_id = len(objects) + 1
        page_ids.append(page_id)
        objects.append((f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Rotate {rotate} "
                        "/Resources << /Font << /F1 3 0 R >> /XObject << /Im1 7 0 R >> >> "
                        f"/Contents {page_id + 1} 0 R >>").encode("ascii"))
        content = b"BT /F1 12 Tf 3 Tr\n"
        for index, line in enumerate(lines):
            matrix = (text_matrices or {}).get(index, (1, 0, 0, 1, 50, 750 - 24 * index))
            content += " ".join(map(str, matrix)).encode("ascii") + b" Tm\n"
            content += b"<" + line.encode("utf-16-be").hex().encode("ascii") + b"> Tj\n"
        for x, y, text in table_lines:
            content += f"1 0 0 1 {x} {y} Tm\n<{text.encode('utf-16-be').hex()}> Tj\n".encode("ascii")
        # Vẽ ảnh sau chữ ẩn: PDF kiểu text under image, không có OCR thứ hai.
        content += b"ET\nq 460 0 0 140 50 40 cm /Im1 Do Q\n"
        if bang:
            for y in (560, 590, 620, 650):
                content += f"50 {y} m 450 {y} l S\n".encode("ascii")
            for x, y in ((50, 650), (180, 620), (310, 620), (450, 650)):
                content += f"{x} 560 m {x} {y} l S\n".encode("ascii")
        objects.append(_stream(content))
    kids = " ".join(f"{number} 0 R" for number in page_ids)
    objects[1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("ascii")
    output, offsets = io.BytesIO(), [0]
    output.write(b"%PDF-1.4\n%DEMO\n")
    for number, obj in enumerate(objects, 1):
        offsets.append(output.tell())
        output.write(f"{number} 0 obj\n".encode("ascii") + obj + b"\nendobj\n")
    xref = output.tell()
    output.write(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets[1:]:
        output.write(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.write((f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
                  f"startxref\n{xref}\n%%EOF\n").encode("ascii"))
    return output.getvalue()
