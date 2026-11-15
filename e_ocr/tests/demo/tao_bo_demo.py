"""Sinh DEMO vào thư mục tạm do bên kiểm thử cấp; không tự dọn/xóa tệp.

PDF được ghi bằng stdlib, ảnh bằng Pillow đã ghim. Không cần thư viện
sinh PDF, ABBYY, Tesseract, dữ liệu ngoài hoặc kết nối mạng. Word đáp án
dùng bộ ghi OOXML trong gói, luôn được tạo, không cần python-docx.
"""

from __future__ import annotations

from dataclasses import dataclass
import io
from itertools import groupby
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


CONG_TY = 'Công ty DEMO Ánh Dương'
TIEN = '1.000.000 VND'
NGAY = '30/10/2026'
KICH_THUOC = (1240, 1754)
BON_DIEM = [[80, 70], [1160, 70], [1160, 410], [80, 410]]
HANG_BANG = [
    ['BẢNG DEMO — ô gộp ba cột', None, None],
    ['Nội dung', 'Số tiền / ngày', 'Ghi chú'],
    ['Khoản DEMO', TIEN, ''],
    ['Ngày DEMO', NGAY, 'DEMO'],
]


@dataclass(frozen=True)
class BoDemo:
    thu_muc: Path
    pdf_quet: Path
    anh_png: Path
    anh_jpeg: Path
    anh_vung: Path
    anh_da_cat: Path
    dap_an: Path
    pdf_abbyy_gia: Path
    pdf_abbyy_anh: Path
    pdf_61_trang: Path | None
    tep_qua_co: Path | None
    tep_hong: Path | None
    word_dap_an: Path


def _phong_chu(size):
    # Không hạ dấu tiếng Việt khi thiếu font; dùng font hệ thống sẵn có.
    for name in ('arial.ttf', 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    raise RuntimeError('Cần font Arial hoặc DejaVu Sans để sinh DEMO tiếng Việt đúng dấu.')


def _trang(number):
    image = Image.new('RGB', KICH_THUOC, 'white')
    draw, lines = ImageDraw.Draw(image), []

    def chu(x, y, text, size=36):
        draw.text((x, y), text, font=_phong_chu(size), fill='black')
        # Cùng nội dung/vị trí dùng cho lớp chữ giả; tọa độ đầu vào là pixel.
        lines.append((x, y, size, text))

    chu(100, 80, 'DEMO — HỒ SƠ HOÀN TOÀN GIẢ', 40)
    chu(100, 180, CONG_TY, 42)
    chu(100, 260, TIEN, 40)
    chu(100, 330, NGAY, 40)
    xs, ys = [100, 430, 830, 1140], [500, 590, 680, 770, 860]
    draw.rectangle((xs[0], ys[0], xs[-1], ys[-1]), outline='black', width=3)
    for y in ys[1:-1]:
        draw.line((xs[0], y, xs[-1], y), fill='black', width=3)
    for x in xs[1:-1]:
        # Hàng đầu gộp ba cột, không vẽ đường xuyên ô gộp.
        draw.line((x, ys[1], x, ys[-1]), fill='black', width=3)
    for row, cells in enumerate(HANG_BANG):
        for col, text in enumerate(cells):
            if text:
                chu(xs[col] + 14, ys[row] + 24, text, 32)
    chu(100, 1570, f'DEMO — Trang {number}', 32)
    return image, lines


def _stream(data, attrs=b''):
    return (b'<< /Length ' + str(len(data)).encode('ascii') + b' ' + attrs
            + b' >>\nstream\n' + data + b'\nendstream')


def _pdf(images, lines=None):
    """PDF ảnh JPEG thật; tùy chọn lớp chữ ẩn Type0/ToUnicode tiếng Việt.

    Không dùng lại ảnh 1 pixel của unit test OCR-NOI. Mỗi trang có ảnh
    bảng đầy đủ. Bản quét không có font/ký tự để parser lấy đáp án sẵn.
    """
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'']

    def them(obj):
        objects.append(obj)
        return len(objects)

    font_id = None
    if lines is not None:
        chars = sorted({c for page in lines for *_, text in page for c in text})
        cmap = ('/CIDInit /ProcSet findresource begin\n12 dict begin\nbegincmap\n'
                '/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def\n'
                '/CMapName /DemoUnicode def\n/CMapType 2 def\n'
                '1 begincodespacerange\n<0000> <FFFF>\nendcodespacerange\n')
        for start in range(0, len(chars), 100):
            group = chars[start:start + 100]
            cmap += f'{len(group)} beginbfchar\n'
            cmap += '\n'.join(f'<{ord(c):04X}> <{c.encode("utf-16-be").hex()}>' for c in group)
            cmap += '\nendbfchar\n'
        cmap += 'endcmap\nCMapName currentdict /CMap defineresource pop\nend\nend'
        cmap_id = them(_stream(cmap.encode('ascii')))
        desc_id = them(b'<< /Type /FontDescriptor /FontName /DEMO /Flags 4 '
                       b'/FontBBox [0 -200 1000 900] /ItalicAngle 0 /Ascent 800 '
                       b'/Descent -200 /CapHeight 700 /StemV 80 >>')
        cid_id = them((f'<< /Type /Font /Subtype /CIDFontType2 /BaseFont /DEMO /DW 600 '
                       '/CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> '
                       f'/FontDescriptor {desc_id} 0 R /CIDToGIDMap /Identity >>').encode('ascii'))
        font_id = them((f'<< /Type /Font /Subtype /Type0 /BaseFont /DEMO /Encoding /Identity-H '
                        f'/DescendantFonts [{cid_id} 0 R] /ToUnicode {cmap_id} 0 R >>').encode('ascii'))
    image_ids, page_ids = {}, []
    for index, image in enumerate(images):
        # PDF 61 trang dùng lại cùng đối tượng ảnh, tránh 61 bản ảnh trong RAM.
        key = id(image)
        if key not in image_ids:
            stream = io.BytesIO()
            image.save(stream, format='JPEG', quality=92)
            attrs = (f'/Type /XObject /Subtype /Image /Width {image.width} /Height {image.height} '
                     '/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode').encode('ascii')
            image_ids[key] = them(_stream(stream.getvalue(), attrs))
        content = b'q 595 0 0 842 0 0 cm /Im1 Do Q\n'
        if lines is not None:
            content += b'BT 3 Tr\n'
            for x, y, size, text in lines[index]:
                scale_x, scale_y = 595 / image.width, 842 / image.height
                content += (f'/F1 {size * scale_x:.4f} Tf 1 0 0 1 '
                            f'{x * scale_x:.4f} {842 - (y + size) * scale_y:.4f} Tm\n'
                            f'<{text.encode("utf-16-be").hex()}> Tj\n').encode('ascii')
            content += b'ET\n'
            # ABBYY giả trả cả hình học bảng trong PDF lớp chữ. Bản quét
            # phía trên chỉ có ảnh; không gài lớp chữ/vector làm đáp án.
            sx, sy = 595 / image.width, 842 / image.height
            for y in (500, 590, 680, 770, 860):
                content += f'{100*sx:.4f} {842-y*sy:.4f} m {1140*sx:.4f} {842-y*sy:.4f} l S\n'.encode('ascii')
            for x, y in ((100, 500), (430, 590), (830, 590), (1140, 500)):
                content += f'{x*sx:.4f} {842-860*sy:.4f} m {x*sx:.4f} {842-y*sy:.4f} l S\n'.encode('ascii')
        content_id = them(_stream(content))
        font = '' if font_id is None else f'/Font << /F1 {font_id} 0 R >> '
        page_ids.append(them((f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] '
                              f'/Resources << {font}/XObject << /Im1 {image_ids[key]} 0 R >> >> '
                              f'/Contents {content_id} 0 R >>').encode('ascii')))
    kids = ' '.join(f'{number} 0 R' for number in page_ids)
    objects[1] = f'<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>'.encode('ascii')
    output, offsets = io.BytesIO(), [0]
    output.write(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
    for number, obj in enumerate(objects, 1):
        offsets.append(output.tell())
        output.write(f'{number} 0 obj\n'.encode('ascii') + obj + b'\nendobj\n')
    xref = output.tell()
    output.write(f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode('ascii'))
    for offset in offsets[1:]:
        output.write(f'{offset:010d} 00000 n \n'.encode('ascii'))
    output.write((f'trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n'
                  f'startxref\n{xref}\n%%EOF\n').encode('ascii'))
    return output.getvalue()


def _word_dap_an(path):
    from e_ocr.xuat_word import dung_docx

    pages = []
    sx, sy = 595 / KICH_THUOC[0], 842 / KICH_THUOC[1]
    xs, ys = [100, 430, 830, 1140], [500, 590, 680, 770, 860]
    for number in range(1, 4):
        blocks = [{"loai": "doan", "van_ban": text, "hop": [48, y, 550, y + 22]}
                  for y, text in zip((38, 86, 124, 158, 196), (
                      'DEMO — ĐÁP ÁN OCR, KHÔNG PHẢI KẾT QUẢ NHẬN DẠNG',
                      CONG_TY, TIEN, NGAY, f'DEMO — Trang {number}'))]
        blocks.append({"loai": "bang", "hop": [xs[0]*sx, ys[0]*sy, xs[-1]*sx, ys[-1]*sy],
                       "o": [{"hang": r, "cot": c, "gop_hang": 1,
                              "gop_cot": 3 if r == 0 else 1, "van_ban": text,
                              "hop": [xs[c]*sx, ys[r]*sy, xs[3 if r == 0 else c+1]*sx, ys[r+1]*sy]}
                             for r, row in enumerate(HANG_BANG)
                             for c, text in enumerate(row) if text is not None]})
        pages.append({"so": number, "rong": 595, "cao": 842, "don_vi": "pt", "khoi": blocks})
    with path.open('xb') as stream:
        stream.write(dung_docx({"phien_ban": 1, "so_trang": 3, "trang": pages}))
    return path


def tao_bo_demo(thu_muc: Path, *, ca_loi=True) -> BoDemo:
    """Chỉ tạo tệp mới trong đích được cấp; gọi lại cùng đích sẽ báo lỗi.

    ca_loi=False để sinh tệp nhỏ đưa vào gói. PDF 61 trang, >20 MiB và
    tệp hỏng chỉ sinh trong tmp_path lúc test; không đọc kho/cấu hình thật.
    """
    root = Path(thu_muc)
    root.mkdir(parents=True, exist_ok=True)
    pages = [_trang(number) for number in range(1, 4)]
    images, lines = [p[0] for p in pages], [p[1] for p in pages]

    def ghi(name, raw):
        path = root / name
        with path.open('xb') as stream:
            stream.write(raw)
        return path

    def anh(name, image, fmt):
        stream = io.BytesIO()
        image.save(stream, format=fmt)
        return ghi(name, stream.getvalue())

    pdf = ghi('DEMO-quet-3-trang.pdf', _pdf(images))
    png = anh('DEMO-1-trang.png', images[0], 'PNG')
    jpeg = anh('DEMO-1-trang.jpg', images[1], 'JPEG')
    vung = anh('DEMO-vung.png', images[0], 'PNG')
    cat = anh('DEMO-vung-da-cat.png', images[0].crop((80, 70, 1160, 410)), 'PNG')
    abbyy = ghi('DEMO-ABBYY-gia-3-trang.pdf', _pdf(images, lines))
    abbyy_anh = ghi('DEMO-ABBYY-gia-1-trang.pdf', _pdf(images[:1], lines[:1]))
    qua_trang = qua_co = hong = None
    if ca_loi:
        qua_trang = ghi('DEMO-61-trang.pdf', _pdf([images[0]] * 61))
        qua_co = root / 'DEMO-hon-20-MiB.pdf'
        with qua_co.open('xb') as stream:
            stream.write(pdf.read_bytes())
            # Trần kích thước chặn trước parser/ABBYY.
            stream.write(b'\0' * (20 * 1024**2 + 1 - stream.tell()))
        hong = ghi('DEMO-hong.pdf', b'%PDF-1.4\nDEMO - tep hong, khong co cau truc PDF\n')
    word = _word_dap_an(root / 'DEMO-dap-an.docx')
    answer = {
        'nhan': 'DEMO — HỒ SƠ HOÀN TOÀN GIẢ',
        'truong': {'cong_ty': CONG_TY, 'so_tien': {'so': 1000000, 'tien_te': 'VND'}, 'ngay': '2026-10-30'},
        'nguyen_van': [CONG_TY, TIEN, NGAY],
        'trang': [{'so_trang': n, 'dong': [' '.join(line[3] for line in row)
                  for _, row in groupby(ls, key=lambda line: line[1])]}
                  for n, ls in enumerate(lines, 1)],
        'bang': {'so_hang': 4, 'so_cot': 3, 'hang': HANG_BANG,
                 'o_trong': [[2, 2]], 'o_gop': [{'hang': 0, 'cot': 0, 'so_cot': 3, 'so_hang': 1}]},
        'vung': {'bon_diem': BON_DIEM, 'kich_thuoc_cat': [1080, 340],
                 'van_ban': '\n'.join(line[3] for line in lines[0][:4])},
        'word': {'da_tao': True, 'ghi_chu': 'Word chỉ là đáp án, không phải kết quả OCR.'},
    }
    dap_an = ghi('DEMO-dap-an.json', (json.dumps(answer, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    for image in images:
        image.close()
    return BoDemo(root, pdf, png, jpeg, vung, cat, dap_an, abbyy, abbyy_anh,
                  qua_trang, qua_co, hong, word)
