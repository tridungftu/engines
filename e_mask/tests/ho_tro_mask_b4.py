"""Oracle ZIP DEMO độc lập B4: zipfile/struct, không writer runtime."""

import io
import struct
import zipfile

from ho_tro_mask_b1 import dong_goi, word_demo, excel_demo
from ho_tro_mask_b2 import word_day_du, zip_office
from ho_tro_mask_b3 import phan_demo, goi_office


def khong_huy():
    pass


def mau(loai, *, co=6, descriptor=True, chu_ky=True, local_day_du=False, cach=8):
    if loai == 'docx':
        phan = word_day_du()
        if cach == 8:
            return zip_office(phan, co=co, descriptor=descriptor, chu_ky=chu_ky, local_day_du=local_day_du)
    else:
        phan = phan_demo(day_du=True)
    return goi_office(phan, co=co, descriptor=descriptor, chu_ky=chu_ky, cach=cach)


def mau_chu(loai, text, *, codec='utf-8', bom=False, cach=0):
    if loai == 'docx':
        phan = word_demo(noi_dung='<w:p><w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">'
                         + text + '</w:t></w:r></w:p>')
        ten = 'word/document.xml'
    else:
        phan = excel_demo(noi_dung='<row r="1"><c r="A1" t="inlineStr"><is><t xml:space="preserve">'
                          + text + '</t></is></c></row>')
        ten = 'xl/worksheets/sheet1.xml'
    khai = '<?xml version="1.0" encoding="' + ('UTF-8' if codec == 'utf-8' else 'UTF-16') + '"?>'
    prefix = {'utf-8': b'\xef\xbb\xbf', 'utf-16-le': b'\xff\xfe', 'utf-16-be': b'\xfe\xff'}[codec] if bom else b''
    phan[ten] = prefix + (khai + phan[ten]).encode(codec)
    return dong_goi(phan, cach=cach)


def liet_ke(raw):
    """Kiểm CRC bằng zipfile; ranh record/payload lấy trực tiếp bằng struct."""
    ket_qua = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        infos = z.infolist()
        moc = {p.header_offset: cuoi for p, cuoi in zip(
            sorted(infos, key=lambda p: p.header_offset),
            [p.header_offset for p in sorted(infos, key=lambda p: p.header_offset)][1:] + [z.start_dir])}
        pos = z.start_dir
        for p in infos:
            n, x = struct.unpack_from('<2H', raw, p.header_offset + 26)
            dau = p.header_offset + 30 + n + x
            cn, cx, cc = struct.unpack_from('<3H', raw, pos + 28)
            het = pos + 46 + cn + cx + cc
            ket_qua[p.filename] = {
                'chu': z.read(p), 'payload': raw[dau:dau + p.compress_size],
                'record': raw[p.header_offset:moc[p.header_offset]],
                'central': raw[pos:het], 'offset': p.header_offset, 'dau_payload': dau,
                'crc': p.CRC, 'size': p.file_size, 'nen': p.compress_size,
                'co': p.flag_bits, 'cach': p.compress_type, 'le_central': pos,
            }
            pos = het
    return ket_qua


def xoa_truong_muc(raw, *, sua=False):
    data = bytearray(raw)
    data[42:46] = b'\0' * 4
    if sua:
        data[16:28] = b'\0' * 12
    return bytes(data)
