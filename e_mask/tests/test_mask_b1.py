"""Kiểm tấn công/biên DEMO cho cổng nội bộ; chưa nghiệm thu Office/Core thật."""

import builtins
from contextlib import ExitStack, contextmanager, redirect_stderr, redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import random
import socket
import stat
import struct
import tempfile
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zipfile

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, ViecDaHuy

from e_mask import doc_tep as dt, xml_an_toan as xa, zip_an_toan as za
from ho_tro_mask_b1 import (
    CT, CT_RELS, CT_S, CT_W, R, REL, S, W, dong_goi, excel_demo,
    nen_raw, rels_demo, tao_zip, them_phan, types_demo, word_demo,
)

MIB = 1048576
CANARY = "TEN-RIENG-DEMO-KHONG-DUOC-LO"


def khong_huy():
    pass


@contextmanager
def cam_io():
    da_goi = []

    def cam(*args, **kwargs):
        da_goi.append(True)
        raise AssertionError('Cổng B1 đã gọi I/O ngoài RAM')

    out, err = io.StringIO(), io.StringIO()
    with ExitStack() as stack:
        for obj, ten in ((builtins, 'open'), (io, 'open'), (os, 'open'),
                         (tempfile, 'TemporaryFile'), (tempfile, 'NamedTemporaryFile'),
                         (tempfile, 'mkstemp'), (tempfile, 'mkdtemp'), (zipfile, 'ZipFile'),
                         (socket, 'create_connection'), (socket, 'getaddrinfo'), (socket.socket, 'connect')):
            stack.enter_context(patch.object(obj, ten, cam))
        stack.enter_context(redirect_stdout(out))
        stack.enter_context(redirect_stderr(err))
        yield
    assert not da_goi and out.getvalue() == err.getvalue() == ''


def tu_choi(ham, ma=None):
    output = []
    with cam_io():
        with pytest.raises(LoiNghiepVu) as loi:
            output.append(ham())
    e = loi.value
    assert e.ma in {"MASK_TEP_CHUA_HO_TRO", "MASK_QUA_GIOI_HAN"}
    if ma is not None:
        assert e.ma == ma
    assert e.thong_diep == {
        "MASK_TEP_CHUA_HO_TRO": "Tệp có nội dung chưa được hỗ trợ xử lý đầy đủ.",
        "MASK_QUA_GIOI_HAN": "Tệp vượt giới hạn xử lý thử nghiệm.",
    }[e.ma]
    assert not output
    assert CANARY not in str(e) and CANARY not in repr(e)
    assert e.__cause__ is None
    return e


def doc_goi(raw):
    return dt.doc_tep(raw, kiem_huy=khong_huy)


def doc_xml(raw, ngan=None, namespace=None, kiem_huy=khong_huy):
    return xa.doc_xml(raw, namespace={W} if namespace is None else namespace,
                      ngan_sach=xa.NganSachXML() if ngan is None else ngan, kiem_huy=kiem_huy)


@pytest.mark.parametrize("cach", [0, 8])
@pytest.mark.parametrize("tao", [word_demo, excel_demo])
def test_goi_dung_chi_tra_noi_bo_nguyen_bytes(tao, cach):
    phan = tao()
    raw = dong_goi(phan, cach)
    kq = doc_goi(raw)
    assert kq.loai == ("docx" if tao is word_demo else "xlsx")
    assert kq.zip.goc is raw
    assert {p.ten: p.du_lieu for p in kq.zip.phan} == {t: c.encode() for t, c in phan.items()}
    assert set(kq.cay) == set(phan)
    assert not hasattr(kq, "da_che")
    with pytest.raises(TypeError):
        kq.cay["DEMO"] = None
    assert "DEMO" not in repr(kq) and "document.xml" not in repr(kq.zip)


def test_docx_story_va_metadata_dung_graph_de_reader_sau_kiem():
    phan = word_demo(noi_dung='<w:p/><w:sectPr><w:headerReference w:type="default" r:id="rId9"/></w:sectPr>')
    them_phan(phan, "word/header1.xml", f'<w:hdr xmlns:w="{W}"><w:p><w:r><w:t>DEMO đầu</w:t></w:r></w:p></w:hdr>',
              CT_W + "header+xml", "header")
    them_phan(phan, "word/footnotes.xml", f'<w:footnotes xmlns:w="{W}"><w:footnote w:id="1"><w:p/></w:footnote></w:footnotes>',
              CT_W + "footnotes+xml", "footnotes", rid="rId10")
    them_phan(phan, "docProps/app.xml", f'<Properties xmlns="{xa.EP_NS}"><Company>Công ty DEMO</Company></Properties>',
              "application/vnd.openxmlformats-officedocument.extended-properties+xml", "extended-properties", chu="")
    kq = doc_goi(dong_goi(phan))
    assert kq.cay["word/header1.xml"].find(f'.//{{{W}}}t').text == 'DEMO đầu'
    assert 'Công ty DEMO' in ''.join(kq.cay['docProps/app.xml'].itertext())


@pytest.mark.parametrize("ten", [
    "/DEMO.xml", "C:/DEMO.xml", "C:DEMO.xml", "//DEMO/share.xml", "\\\\DEMO\\share.xml",
    "../DEMO.xml", "word/../DEMO.xml", "word/./DEMO.xml", "word//DEMO.xml",
    "word\\DEMO.xml", "word/%2e%2e/DEMO.xml", "word/DEMO%2exml", "word/%252e.xml",
    "word/DEMO.xml:ads", "word/DEMO.xml?x", "word/DEMO.xml#x", "word/DEMO\x00.xml",
    "word/DEMO\n.xml", "word/DEMO\u200b.xml", "word /DEMO.xml", "word./DEMO.xml", "word/",
])
def test_zip_ten_khong_an_toan(ten):
    tu_choi(lambda: za.doc_zip(tao_zip([{"ten": ten}]), khong_huy), "MASK_TEP_CHUA_HO_TRO")


@pytest.mark.parametrize("hai", [("DEMO.xml", "DEMO.xml"), ("DEMO.xml", "demo.XML"),
                                  ("DÉMO.xml", "DE\u0301MO.xml"), ("Straße.xml", "STRASSE.xml")])
def test_trung_ten_nfc_casefold_tu_choi_ca_goi(hai):
    raw = tao_zip([{"ten": n, "chung": {"co": 0x800}} for n in hai])
    tu_choi(lambda: za.doc_zip(raw, khong_huy), "MASK_TEP_CHUA_HO_TRO")


@pytest.mark.parametrize("sua", [
    {"ngoai": (stat.S_IFLNK | 0o777) << 16}, {"ngoai": (stat.S_IFDIR | 0o755) << 16},
    {"ngoai": (stat.S_IFIFO | 0o600) << 16}, {"ngoai": (stat.S_IFREG | 0o4600) << 16},
    {"ngoai": (stat.S_IFREG | 0o600) << 16 | 16},
    {"chung": {"co": 1}}, {"chung": {"co": 8}}, {"chung": {"co": 64}}, {"chung": {"co": 0x1000}},
    {"chung": {"cach": 12}}, {"chung": {"cach": 99}}, {"chung": {"can": 45}},
    {"tao": 0x6314}, {"noi_bo": 1}, {"dia": 1}, {"extra": b'\x75\x70\x04\x00DEMO'},
    {"comment": CANARY.encode()}, {"local": {"crc": 1}}, {"local": {"dai": 1}},
    {"local": {"co": 0x800}}, {"local": {"can": 10}}, {"local": {"cach": 8}},
    {"ten_local": b'demo.xml'}, {"chung": {"ngay": 0}}, {"chung": {"gio": 0xffff}},
    {"chung": {"nen": 0xffffffff}}, {"chung": {"dai": 0xffffffff}}, {"offset": 0xffffffff},
    {"ten": b'DEMO\xff.xml'},
])
def test_zip_header_ngoai_whitelist(sua):
    raw = tao_zip([{"ten": "DEMO.xml", **sua}])
    tu_choi(lambda: za.doc_zip(raw, khong_huy))


@pytest.mark.parametrize("cach", [0, 8])
@pytest.mark.parametrize("sua", [
    {"crc": 123}, {"dai": 3}, {"dai": 8}, {"nen": 3}, {"nen": 8},
])
def test_crc_size_khai_sai(cach, sua):
    raw = tao_zip([{"ten": CANARY + '.xml', "raw": b'DEMO', "cach": cach, "chung": sua}])
    tu_choi(lambda: za.doc_zip(raw, khong_huy))


@pytest.mark.parametrize("payload", [
    nen_raw(b'DEMO') + b'TEN-DEMO', nen_raw(b'DEMO') + nen_raw('DEMO giấu đuôi'.encode()),
    nen_raw(b'DEMO')[:-1], b'not-DEFLATE-DEMO',
])
def test_de_flates_eof_that_khong_duoi_khong_ghep_luong(payload):
    raw = tao_zip([{"ten": CANARY + '.xml', "raw": b'DEMO', "cach": 8, "payload": payload}])
    tu_choi(lambda: za.doc_zip(raw, khong_huy), "MASK_TEP_CHUA_HO_TRO")


def test_khai_nho_giau_duoi_de_flates_crc_tien_to_dung_van_bi_chan():
    # Prefix CRC và file_size đều đúng; reader cắt theo file_size sẽ đọc nhầm đạt.
    raw = tao_zip([{"ten": CANARY + '.xml', "raw": b'DEMO', "cach": 8,
                    "payload": nen_raw(b'DEMO' + b'A' * 100000)}])
    tu_choi(lambda: za.doc_zip(raw, khong_huy), "MASK_TEP_CHUA_HO_TRO")


@pytest.mark.parametrize("raw", [b'PK\x03\x04DEMO', b'PK\x05\x06DEMO', b'PK\x07\x08DEMO'])
def test_zip_long(raw):
    tu_choi(lambda: za.doc_zip(tao_zip([{"ten": 'DEMO.xml', 'raw': raw}]), khong_huy))


@pytest.mark.parametrize("them", [b'x', b'PK\x06\x06' + b'DEMO', b'PK\x06\x07' + b'DEMO'])
def test_trailing_data_zip64_locator(them):
    raw = tao_zip([{"ten": 'DEMO.xml'}]) + them
    tu_choi(lambda: za.doc_zip(raw, khong_huy))


@pytest.mark.parametrize("le,fmt,gia_tri", [(4, '<H', 1), (6, '<H', 1), (8, '<H', 2),
                                          (10, '<H', 65535), (12, '<I', 0xffffffff),
                                          (16, '<I', 0xffffffff), (20, '<H', 1)])
def test_eocd_multidisk_zip64_comment(le, fmt, gia_tri):
    raw = bytearray(tao_zip([{"ten": 'DEMO.xml'}]))
    struct.pack_into(fmt, raw, len(raw) - 22 + le, gia_tri)
    tu_choi(lambda: za.doc_zip(bytes(raw), khong_huy))


def test_so_muc_duoc_kiem_truoc_tao_central_directory(monkeypatch):
    raw = bytearray(tao_zip([{"ten": 'DEMO.xml'}]))
    struct.pack_into('<HH', raw, len(raw) - 22 + 8, 257, 257)
    da_tao = []
    monkeypatch.setattr(za, 'PhanZip', lambda *a: da_tao.append(a))
    tu_choi(lambda: za.doc_zip(bytes(raw), khong_huy), "MASK_QUA_GIOI_HAN")
    assert not da_tao
    # EOCD khai nhỏ hơn danh mục thật cũng không được tạo danh sách.
    raw = bytearray(tao_zip([{"ten": 'DEMO1.xml'}, {"ten": 'DEMO2.xml'}]))
    struct.pack_into('<HH', raw, len(raw) - 22 + 8, 1, 1)
    tu_choi(lambda: za.doc_zip(bytes(raw), khong_huy), "MASK_TEP_CHUA_HO_TRO")
    assert not da_tao


def test_self_extracting_gap_overlap_va_local_mo_coi():
    raw = tao_zip([{"ten": 'DEMO1.xml'}, {"ten": 'DEMO2.xml'}])
    tu_choi(lambda: za.doc_zip(b'MZ-DEMO' + raw, khong_huy))
    # Hai central record cùng trỏ một local header dù đổi tên central hợp lệ.
    chong = tao_zip([{"ten": 'DEMO1.xml'}, {"ten": 'DEMO2.xml', "offset": 0}])
    tu_choi(lambda: za.doc_zip(chong, khong_huy))
    # Có bytes ngoài local payload trước central, đã chỉnh EOCD để đúng vị trí.
    le = struct.unpack_from('<I', raw, len(raw) - 6)[0]
    co_duoi = bytearray(raw[:le] + b'DEMO-KENH-RO' + raw[le:])
    struct.pack_into('<I', co_duoi, len(co_duoi) - 6, le + len(b'DEMO-KENH-RO'))
    tu_choi(lambda: za.doc_zip(bytes(co_duoi), khong_huy))


@pytest.mark.parametrize("them", [0, 1])
def test_container_dung_1mib_va_cong_1(them):
    ten = 'DEMO.xml'
    dai = MIB - (98 + 2 * len(ten)) + them
    raw = tao_zip([{"ten": ten, 'raw': b'D' * dai}])
    assert len(raw) == MIB + them
    if them:
        tu_choi(lambda: za.doc_zip(raw, khong_huy), "MASK_QUA_GIOI_HAN")
    else:
        assert za.doc_zip(raw, khong_huy).phan[0].du_lieu == b'D' * dai
        za.kiem_kich_thuoc_tep(raw)  # Chiều ra kiểm lại độc lập.
    if them:
        tu_choi(lambda: za.kiem_kich_thuoc_tep(raw), "MASK_QUA_GIOI_HAN")


def du_lieu_nen_vua(dai):
    rng = random.Random(20261030)
    block = b'DEMO' + rng.randbytes(16380)
    return (block * ((dai + 16383) // 16384))[:dai]


@pytest.mark.parametrize("them", [0, 1])
def test_phan_dung_2mib_va_cong_1(them):
    data = du_lieu_nen_vua(2 * MIB + them)
    raw = tao_zip([{"ten": 'DEMO.xml', 'raw': data, 'cach': 8}])
    assert len(raw) < MIB and len(data) <= len(nen_raw(data)) * 200
    if them:
        tu_choi(lambda: za.doc_zip(raw, khong_huy), "MASK_QUA_GIOI_HAN")
    else:
        assert za.doc_zip(raw, khong_huy).phan[0].du_lieu == data


@pytest.mark.parametrize("them", [0, 1])
def test_tong_dung_8mib_va_cong_1(them):
    data = du_lieu_nen_vua(2 * MIB)
    ds = [{"ten": f'DEMO{i}.xml', 'raw': data, 'cach': 8} for i in range(4)]
    if them:
        ds.append({"ten": 'DEMO4.xml', 'raw': b'x'})
    raw = tao_zip(ds)
    assert len(raw) < MIB
    if them:
        tu_choi(lambda: za.doc_zip(raw, khong_huy), "MASK_QUA_GIOI_HAN")
    else:
        kq = za.doc_zip(raw, khong_huy)
        assert sum(len(p.du_lieu) for p in kq.phan) == 8 * MIB


@pytest.mark.parametrize("them", [0, 1])
def test_so_phan_256_va_257(them):
    raw = tao_zip([{"ten": f'DEMO{i}.xml', 'raw': b''} for i in range(256 + them)])
    if them:
        tu_choi(lambda: za.doc_zip(raw, khong_huy), "MASK_QUA_GIOI_HAN")
    else:
        assert len(za.doc_zip(raw, khong_huy).phan) == 256


@pytest.mark.parametrize("them", [0, 1])
def test_ratio_200_va_vuot_phan_nho(them):
    data = b'A' * (4400 + them)
    assert len(nen_raw(data)) == 22
    raw = tao_zip([{"ten": 'DEMO.xml', 'raw': data, 'cach': 8}])
    if them:
        tu_choi(lambda: za.doc_zip(raw, khong_huy), "MASK_QUA_GIOI_HAN")
    else:
        assert za.doc_zip(raw, khong_huy).phan[0].du_lieu == data


def test_bomb_nho_va_tran_bytes_thuc_trong_luc_giai_nen(monkeypatch):
    data = b'A' * 8192
    tu_choi(lambda: za.doc_zip(tao_zip([{"ten": 'DEMO.xml', 'raw': data, 'cach': 8}]), khong_huy), "MASK_QUA_GIOI_HAN")
    # Bỏ tiền kiểm metadata riêng để đo cửa byte thực, không đổi trần runtime.
    payload = nen_raw(data)
    phan = za.PhanZip('DEMO.xml', 8, 0, len(payload), 8192, 0, 0, len(payload), 0, 0)
    tu_choi(lambda: za._giai_nen(payload, phan, [0], khong_huy), "MASK_QUA_GIOI_HAN")
    # Tổng byte thực ở biên cũng được chặn, dù metadata của phần đang đọc nhỏ.
    raw = b'DEMO'
    phan = za.PhanZip('DEMO.xml', 0, 0, 4, 4, 0, 0, 4, 0, 0)
    tu_choi(lambda: za._giai_nen(raw, phan, [8 * MIB - 3], khong_huy), "MASK_QUA_GIOI_HAN")


def test_giai_nen_thuc_bounded_va_don_buffer_finally(monkeypatch):
    buffers, tran = [], []
    goc_nen = za.zlib.decompressobj

    class Dem(bytearray):
        def __init__(self):
            super().__init__()
            buffers.append(self)

        def extend(self, raw):
            assert len(self) + len(raw) <= 2 * MIB
            super().extend(raw)

    class Nen:
        def __init__(self, *a):
            self.goc = goc_nen(*a)

        def decompress(self, chunk, max_length):
            tran.append(max_length)
            return self.goc.decompress(chunk, max_length)

        def __getattr__(self, ten):
            return getattr(self.goc, ten)

    monkeypatch.setattr(za, 'bytearray', Dem, raising=False)
    monkeypatch.setattr(za.zlib, 'decompressobj', Nen)
    data = du_lieu_nen_vua(2 * MIB + 1)
    payload = nen_raw(data)
    phan = za.PhanZip('DEMO.xml', 8, 0, len(payload), len(data), 0, 0, len(payload), 0, 0)
    tu_choi(lambda: za._giai_nen(payload, phan, [0], khong_huy), "MASK_QUA_GIOI_HAN")
    assert buffers and all(len(b) == 0 for b in buffers)
    assert tran and 0 < min(tran) <= max(tran) <= 65536


@pytest.mark.parametrize("chu", [
    f'<!DOCTYPE w:document [<!ENTITY x "{CANARY}">]><w:document xmlns:w="{W}">&x;</w:document>',
    f'<!DOCTYPE w:document SYSTEM "file:///{CANARY}"><w:document xmlns:w="{W}"/>',
    f'<!DOCTYPE w:document [<!ENTITY x SYSTEM "https://example.invalid/{CANARY}">]><w:document xmlns:w="{W}">&x;</w:document>',
    f'<!DOCTYPE w:document [<!ENTITY % x SYSTEM "https://example.invalid/{CANARY}">%x;]><w:document xmlns:w="{W}"/>',
    f'<?DEMO {CANARY}?><w:document xmlns:w="{W}"/>',
    f'<w:document xmlns:w="{W}"><?xml-stylesheet href="{CANARY}"?></w:document>',
    f'<w:document xmlns:w="{W}"><!--{CANARY}--></w:document>',
])
@pytest.mark.parametrize("encoding", ['utf-8', 'utf-16', 'utf-16le', 'utf-16be'])
def test_dtd_entity_xxe_pi_comment_utf8_utf16(chu, encoding):
    raw = (f'<?xml version="1.0" encoding="{encoding}"?>' + chu).encode(encoding)
    tu_choi(lambda: doc_xml(raw), "MASK_TEP_CHUA_HO_TRO")


@pytest.mark.parametrize("encoding", ['utf-8', 'utf-16', 'utf-16le', 'utf-16be'])
def test_khai_bao_xml_hop_le_khong_bi_coi_pi(encoding):
    raw = (f'<?xml version="1.0" encoding="{encoding}" standalone="yes"?>'
           f'<w:document xmlns:w="{W}"><w:t>DEMO &amp; Ánh Dương</w:t></w:document>').encode(encoding)
    root = doc_xml(raw)
    assert root.find(f'{{{W}}}t').text == 'DEMO & Ánh Dương'


@pytest.mark.parametrize("chu", [
    f'<?xml version="1.1"?><w:document xmlns:w="{W}"/>',
    f'<?xml version="1.0" encoding="ISO-8859-1"?><w:document xmlns:w="{W}"/>',
    f'<w:document xmlns:w="{W}" xmlns:DEMO="urn:{CANARY}"/>',
    f'<w:document xmlns:w="{W}" xmlns:DEMO="{W}"/>',
    '<document/>', f'<w:document xmlns:w="{W}">&notDeclared;</w:document>',
    f'<w:document xmlns:w="{W}"><w:t DEMO="1" DEMO="2"/></w:document>',
    f'<w:document xmlns:w="{W}">DEMO',
])
def test_encoding_namespace_va_xml_hong(chu):
    tu_choi(lambda: doc_xml(chu.encode()), "MASK_TEP_CHUA_HO_TRO")


@pytest.mark.parametrize("encoding", ['x-DEMO-unknown', 'UTF-7', 'US-ASCII', 'cp1258', 'UTF-32', 'UCS-2'])
def test_encoding_ngoai_profile_deu_loi_nghiep_vu_co_dinh(encoding):
    raw = (f'<?xml version="1.0" encoding="{encoding}"?><w:document xmlns:w="{W}"/>').encode()
    tu_choi(lambda: doc_xml(raw), 'MASK_TEP_CHUA_HO_TRO')


@pytest.mark.parametrize("them", [0, 1])
def test_depth_64_va_65(them):
    raw = (f'<w:document xmlns:w="{W}">' + '<w:r>' * (63 + them)
           + '</w:r>' * (63 + them) + '</w:document>').encode()
    if them:
        tu_choi(lambda: doc_xml(raw), "MASK_QUA_GIOI_HAN")
    else:
        assert doc_xml(raw).tag == f'{{{W}}}document'


@pytest.mark.parametrize("them", [0, 1])
def test_100000_node_tong_nhieu_phan_va_cong_1(them):
    ngan = xa.NganSachXML()
    for n in (50000, 50000 + them):
        raw = (f'<w:document xmlns:w="{W}">' + '<w:r/>' * (n - 1) + '</w:document>').encode()
        if them and ngan.so_nut:
            tu_choi(lambda: doc_xml(raw, ngan), "MASK_QUA_GIOI_HAN")
        else:
            doc_xml(raw, ngan)
    assert ngan.so_nut == 100000 + them


@pytest.mark.parametrize("them", [0, 1])
def test_500000_codepoint_text_tail_attribute_tong_nhieu_phan(them):
    ngan = xa.NganSachXML()
    raw = (f'<w:document xmlns:w="{W}" w:val="DEMO"><w:r>Ánh</w:r> Dương'
           + 'x' * (250000 - 4 - 3 - 6) + '</w:document>').encode()
    doc_xml(raw, ngan)
    assert ngan.so_ky_tu == 250000
    raw = (f'<w:document xmlns:w="{W}">' + 'x' * (250000 + them) + '</w:document>').encode()
    if them:
        tu_choi(lambda: doc_xml(raw, ngan), "MASK_QUA_GIOI_HAN")
    else:
        doc_xml(raw, ngan)
    assert ngan.so_ky_tu == 500000 + them


@pytest.mark.parametrize("them", [0, 1])
def test_node_100000_tong_goi_docx_thuc(them):
    phan = word_demo(noi_dung='<w:p>' + '<w:r/>' * (99991 + them) + '</w:p>')
    assert sum(sum(1 for _ in ET.fromstring(raw).iter()) for raw in phan.values()) == 100000 + them
    raw = dong_goi(phan)
    assert len(raw) < MIB
    if them:
        tu_choi(lambda: doc_goi(raw), 'MASK_QUA_GIOI_HAN')
    else:
        assert doc_goi(raw).thong_ke['so_nut'] == 100000


@pytest.mark.parametrize("them", [0, 1])
def test_500000_codepoint_tong_goi_gom_metadata(them):
    phan = word_demo(chu='')
    them_phan(phan, 'docProps/app.xml', f'<Properties xmlns="{xa.EP_NS}"><Company>DEMO</Company></Properties>',
              'application/vnd.openxmlformats-officedocument.extended-properties+xml', 'extended-properties', chu='')
    # Oracle độc lập cộng chuỗi từ bytes đã dựng, không hỏi bộ đếm runtime.
    ngoai = sum(sum(len(e.text or '') + len(e.tail or '') + sum(map(len, e.attrib.values()))
                    for e in ET.fromstring(v).iter()) for v in phan.values())
    phan['word/document.xml'] = phan['word/document.xml'].replace('<w:t></w:t>', '<w:t>' + 'D' * (500000 - ngoai + them) + '</w:t>')
    raw = dong_goi(phan)
    assert len(raw) < MIB
    if them:
        tu_choi(lambda: doc_goi(raw), 'MASK_QUA_GIOI_HAN')
    else:
        assert doc_goi(raw).thong_ke['so_ky_tu'] == 500000


@pytest.mark.parametrize("them", [0, 1])
def test_so_sheet_50_51(them):
    raw = dong_goi(excel_demo(50 + them))
    if them:
        tu_choi(lambda: doc_goi(raw), "MASK_QUA_GIOI_HAN")
    else:
        assert doc_goi(raw).thong_ke['so_sheet'] == 50


@pytest.mark.parametrize("them", [0, 1])
def test_so_o_20000_20001_tong_nhieu_sheet(them):
    phan = excel_demo(2, '<row>' + '<c/>' * 10000 + '</row>')
    if them:
        phan['xl/worksheets/sheet2.xml'] = phan['xl/worksheets/sheet2.xml'].replace('</row>', '<c/></row>')
    raw = dong_goi(phan)
    if them:
        tu_choi(lambda: doc_goi(raw), "MASK_QUA_GIOI_HAN")
    else:
        assert doc_goi(raw).thong_ke['so_o'] == 20000


@pytest.mark.parametrize("them", [0, 1])
def test_van_ban_ra_2000000_codepoint_va_cong_1(them):
    chu = '🟦' * (2000000 + them)
    if them:
        tu_choi(lambda: dt.kiem_van_ban_ra(chu, kiem_huy=khong_huy), "MASK_QUA_GIOI_HAN")
    else:
        dt.kiem_van_ban_ra(chu, kiem_huy=khong_huy)


@pytest.mark.parametrize("them", [0, 1])
def test_bo_dem_utf8_ra_8mib_va_cong_1(them):
    # 2 triệu code point hợp lệ chỉ có tối đa 8.000.000 byte (<8 MiB).
    # Kiểm riêng cửa đếm byte dùng khi ghi luồng, không tăng trần ký tự.
    chunk = b'D' * (8 * MIB + them)
    if them:
        tu_choi(lambda: dt.kiem_byte_chu_ra(len(chunk)), "MASK_QUA_GIOI_HAN")
    else:
        dt.kiem_byte_chu_ra(len(chunk))


@pytest.mark.parametrize("loai,tran", [('bao_cao', 256 * 1024), ('chuyen_tiep', 64 * 1024), ('khuon', 32 * 1024)])
@pytest.mark.parametrize("them", [0, 1])
@pytest.mark.parametrize("unicode", [False, True])
def test_tran_json_utf8_dung_va_cong_1(loai, tran, them, unicode):
    # JSON {"x":"..."} có 8 byte khung; Unicode không dùng ensure_ascii.
    n = tran - 8 + them
    chu = ('Á' * (n // 2) + 'x' * (n % 2)) if unicode else 'x' * n
    val = {'x': chu}
    assert len(json.dumps(val, ensure_ascii=False, separators=(',', ':')).encode()) == tran + them
    if them:
        tu_choi(lambda: dt.ma_hoa_json_noi_bo(val, loai=loai, kiem_huy=khong_huy), "MASK_QUA_GIOI_HAN")
    else:
        raw = dt.ma_hoa_json_noi_bo(val, loai=loai, kiem_huy=khong_huy)
        assert len(raw) == tran and json.loads(raw) == val


@pytest.mark.parametrize("val", [{'x': float('nan')}, {'x': float('inf')}, {'x': object()}, {'x': '\ud800'}])
def test_json_loi_khong_tra_dau_ra_do(val):
    tu_choi(lambda: dt.ma_hoa_json_noi_bo(val, loai='bao_cao', kiem_huy=khong_huy))


def test_json_vong_tham_chieu_va_chu_dung_lai():
    vong = []
    vong.append(vong)
    tu_choi(lambda: dt.ma_hoa_json_noi_bo(vong, loai='bao_cao', kiem_huy=khong_huy))
    chung = {'DEMO': []}
    assert json.loads(dt.ma_hoa_json_noi_bo([chung, chung], loai='bao_cao', kiem_huy=khong_huy)) == [chung, chung]
    tu_choi(lambda: dt.ma_hoa_json_noi_bo({'x': '\n' * (256 * 1024 // 2)}, loai='bao_cao', kiem_huy=khong_huy), 'MASK_QUA_GIOI_HAN')


@pytest.mark.parametrize("ten", [
    'word/comments.xml', 'word/commentsExtended.xml', 'word/people.xml',
    'word/vbaProject.bin', 'word/embeddings/DEMO.bin', 'word/afchunk1.html',
    'word/media/DEMO.png', 'docProps/thumbnail.jpeg', 'customXml/item1.xml',
    '_xmlsignatures/sig1.xml', 'word/printerSettings/printerSettings1.bin',
    'xl/comments1.xml', 'xl/threadedComments/threadedComment1.xml', 'xl/persons/person.xml',
    'xl/charts/chart1.xml', 'xl/drawings/drawing1.xml', 'xl/media/DEMO.png',
    'xl/externalLinks/externalLink1.xml', 'xl/connections.xml', 'xl/calcChain.xml',
    'xl/vbaProject.bin', 'xl/workbook.bin', f'word/{CANARY}.xml',
])
def test_part_la_ke_ca_mo_coi_deu_tu_choi(ten):
    phan = word_demo()
    phan[ten] = '<DEMO/>'
    tu_choi(lambda: doc_goi(dong_goi(phan)), "MASK_TEP_CHUA_HO_TRO")


@pytest.mark.parametrize("noi_dung", [
    '<w:ins/>', '<w:del/>', '<w:delText/>', '<w:rPrChange/>', '<w:moveFrom/>',
    '<w:commentRangeStart/>', '<w:commentReference/>', '<w:fldSimple/>',
    '<w:instrText/>', '<w:drawing/>', '<w:pict/>', '<w:object/>', '<w:txbxContent/>',
    '<w:sdt/>', '<w:altChunk/>', f'<w:DEMO>{CANARY}</w:DEMO>',
    '<w:p w:author="DEMO"/>', '<w:p w:rsidR="DEMO"/>', '<w:p DEMO="DEMO"/>',
    '<w:p r:embed="rId1"/>',
])
def test_word_node_attribute_vung_chua_kiem(noi_dung):
    tu_choi(lambda: doc_goi(dong_goi(word_demo(noi_dung=noi_dung))), "MASK_TEP_CHUA_HO_TRO")


@pytest.mark.parametrize("node", ['f', 'definedNames', 'externalReferences', 'extLst', 'drawing', 'legacyDrawing', 'oleObjects', 'controls'])
def test_excel_formula_cache_definedname_drawing_extension(node):
    phan = excel_demo(noi_dung=f'<row><c><{node}>{CANARY}</{node}><v>1</v></c></row>')
    tu_choi(lambda: doc_goi(dong_goi(phan)), "MASK_TEP_CHUA_HO_TRO")


def test_excel_cached_formula_t_str_khong_f_van_tu_choi():
    tu_choi(lambda: doc_goi(dong_goi(excel_demo(noi_dung='<row><c t="str"><v>DEMO</v></c></row>'))), 'MASK_TEP_CHUA_HO_TRO')


@pytest.mark.parametrize("state", ['hidden', 'veryHidden', 'Hidden', CANARY])
def test_sheet_an_tu_choi_ca_workbook(state):
    phan = excel_demo()
    phan['xl/workbook.xml'] = phan['xl/workbook.xml'].replace('name="DEMO 1"', f'name="DEMO 1" state="{state}"')
    tu_choi(lambda: doc_goi(dong_goi(phan)), "MASK_TEP_CHUA_HO_TRO")


def test_o_hang_cot_an_duoc_dem_khong_bo_qua():
    phan = excel_demo(noi_dung='<row hidden="1"><c><is><t>DEMO ô ẩn</t></is></c><c><v>1000000</v></c><c><v>46325</v></c></row>')
    phan['xl/worksheets/sheet1.xml'] = phan['xl/worksheets/sheet1.xml'].replace('<sheetData>', '<cols><col min="1" max="1" hidden="1"/></cols><sheetData>')
    kq = doc_goi(dong_goi(phan))
    assert kq.thong_ke['so_o'] == 3
    root = kq.cay['xl/worksheets/sheet1.xml']
    assert [v.text for v in root.iter(f'{{{S}}}v')] == ['1000000', '46325']
    assert root.find(f'.//{{{S}}}row').get('hidden') == '1'


@pytest.mark.parametrize("dich", ['https://example.invalid/DEMO', 'file:///DEMO', '//DEMO/a', '/word/document.xml',
                                  '../DEMO.xml', 'word/../DEMO.xml', r'word\document.xml', 'word/%64ocument.xml',
                                  'word/document.xml#DEMO', 'word/document.xml?DEMO'])
def test_quan_he_uri_path_nguy_hiem(dich):
    phan = word_demo()
    phan['_rels/.rels'] = phan['_rels/.rels'].replace('Target="word/document.xml"', f'Target="{dich}"')
    tu_choi(lambda: doc_goi(dong_goi(phan)), "MASK_TEP_CHUA_HO_TRO")


@pytest.mark.parametrize("sua", [
    lambda s: s.replace('/officeDocument', '/hyperlink'),
    lambda s: s.replace('Target="', 'TargetMode="External" Target="'),
    lambda s: s.replace('Target="', 'TargetMode="external" Target="'),
    lambda s: s.replace('Target="', f'DEMO="{CANARY}" Target="'),
    lambda s: s.replace('rId1', CANARY),
    lambda s: s.replace('</Relationships>', '<Relationship Id="rId1" Type="DEMO" Target="DEMO"/></Relationships>'),
])
def test_quan_he_ngoai_sai_loai_sai_khuon(sua):
    phan = word_demo()
    phan['_rels/.rels'] = sua(phan['_rels/.rels'])
    tu_choi(lambda: doc_goi(dong_goi(phan)), "MASK_TEP_CHUA_HO_TRO")


@pytest.mark.parametrize("loi", ['mo_coi', 'sai_ct', 'sai_root', 'sai_type_qh', 'rid_khong_co', 'quan_he_thua', 'trung_ct', 'ct_mo_coi', 'root_tron'])
def test_content_types_graph_va_part_mo_coi(loi):
    phan = word_demo()
    if loi == 'mo_coi':
        phan['word/styles.xml'] = f'<w:styles xmlns:w="{W}"/>'
        phan['[Content_Types].xml'] = types_demo([('word/document.xml', CT_W + 'document.main+xml'), ('word/styles.xml', CT_W + 'styles+xml')])
    elif loi == 'sai_ct':
        phan['[Content_Types].xml'] = phan['[Content_Types].xml'].replace('document.main+xml', 'template.macroEnabledTemplate.main+xml')
    elif loi == 'sai_root':
        phan['word/document.xml'] = f'<w:hdr xmlns:w="{W}"/>'
    elif loi == 'sai_type_qh':
        them_phan(phan, 'word/styles.xml', f'<w:styles xmlns:w="{W}"/>', CT_W + 'styles+xml', 'numbering')
    elif loi == 'rid_khong_co':
        phan = word_demo(noi_dung='<w:sectPr><w:headerReference r:id="rId99"/></w:sectPr>')
    elif loi == 'quan_he_thua':
        them_phan(phan, 'word/header1.xml', f'<w:hdr xmlns:w="{W}"/>', CT_W + 'header+xml', 'header')
    elif loi == 'trung_ct':
        phan['[Content_Types].xml'] = phan['[Content_Types].xml'].replace('</Types>', f'<Override PartName="/word/document.xml" ContentType="{CT_W}document.main+xml"/></Types>')
    elif loi == 'ct_mo_coi':
        phan['[Content_Types].xml'] = phan['[Content_Types].xml'].replace('</Types>', '<Override PartName="/word/DEMO.xml" ContentType="application/xml"/></Types>')
    else:
        phan.update(excel_demo())
    tu_choi(lambda: doc_goi(dong_goi(phan)), "MASK_TEP_CHUA_HO_TRO")


def test_shared_string_lap_that_khong_ne_tran():
    phan = excel_demo(noi_dung='<row>' + '<c t="s"><v>0</v></c>' * 6 + '</row>')
    them_phan(phan, 'xl/sharedStrings.xml', f'<sst xmlns="{S}"><si><t>' + 'D' * 100000 + '</t></si></sst>',
              CT_S + 'sharedStrings+xml', 'sharedStrings', chu='xl/workbook.xml')
    tu_choi(lambda: doc_goi(dong_goi(phan)), "MASK_QUA_GIOI_HAN")
    phan['xl/worksheets/sheet1.xml'] = phan['xl/worksheets/sheet1.xml'].replace('<v>0</v>', '<v>99</v>')
    tu_choi(lambda: doc_goi(dong_goi(phan)), "MASK_TEP_CHUA_HO_TRO")


@pytest.mark.parametrize("ngoai_le", [ViecDaHuy(), RuntimeError('DEMO hủy'), ValueError('DEMO hủy'), ChuaRo('DEMO-chua-ro')])
def test_huy_khong_bi_nuot_o_cac_giai_doan(ngoai_le):
    raw = dong_goi(word_demo(noi_dung='<w:p><w:r><w:t>DEMO</w:t></w:r></w:p>' * 150))
    dem = [0]

    def dem_goi():
        dem[0] += 1

    dt.doc_tep(raw, kiem_huy=dem_goi)
    tong = dem[0]
    for moc in (1, 4, 15, tong // 2, tong - 1, tong):
        dem[0] = 0

        def huy():
            dem[0] += 1
            if dem[0] == moc:
                raise ngoai_le

        with cam_io():
            with pytest.raises(type(ngoai_le)) as loi:
                dt.doc_tep(raw, kiem_huy=huy)
        assert loi.value is ngoai_le
        assert dem[0] == moc


def test_huy_trong_giai_nen_xml_json_va_van_ban_ra():
    loi = ViecDaHuy()

    def huy():
        raise loi

    raw = f'<w:document xmlns:w="{W}">DEMO</w:document>'.encode()
    for ham in (lambda: doc_xml(raw, kiem_huy=huy),
                lambda: dt.ma_hoa_json_noi_bo({'DEMO': 'DEMO'}, loai='bao_cao', kiem_huy=huy),
                lambda: dt.kiem_van_ban_ra('DEMO', kiem_huy=huy)):
        with cam_io():
            with pytest.raises(ViecDaHuy) as e:
                ham()
        assert e.value is loi


def test_khong_mang_khong_ghi_dia_khong_zipfile_warning(monkeypatch, capsys):
    dung = dong_goi(word_demo())
    hong = word_demo()
    hong['word/DEMO.xml'] = CANARY
    hong = dong_goi(hong)
    so_io = []

    def cam(*args, **kwargs):
        so_io.append(True)
        raise AssertionError('Cổng B1 đã gọi I/O ngoài RAM')

    with monkeypatch.context() as m:
        for obj, ten in ((builtins, 'open'), (io, 'open'), (os, 'open'),
                         (tempfile, 'TemporaryFile'), (tempfile, 'NamedTemporaryFile'),
                         (tempfile, 'mkstemp'), (tempfile, 'mkdtemp'), (zipfile, 'ZipFile'),
                         (socket, 'create_connection'), (socket, 'getaddrinfo'), (socket.socket, 'connect')):
            m.setattr(obj, ten, cam)
        doc_goi(dung)
        tu_choi(lambda: doc_goi(hong))
        tu_choi(lambda: doc_xml((f'<!DOCTYPE w:document SYSTEM "https://example.invalid/{CANARY}"><w:document xmlns:w="{W}"/>').encode()))
    assert not so_io
    out = capsys.readouterr()
    assert out.out == out.err == ''


def test_manifest_va_handler_chua_khai_nang_luc_tep():
    goc = Path(__file__).resolve().parents[1] / 'goi/e_mask'
    manifest = json.loads((goc / 'engine.json').read_text(encoding='utf-8'))
    assert all('tep' not in n['ma'] for n in manifest['nang_luc'])
    for ten in ('chay.py', 'phong_bi.py'):
        raw = (goc / 'e_mask' / ten).read_text(encoding='utf-8')
        assert 'zip_an_toan' not in raw and 'xml_an_toan' not in raw and 'from .doc_tep' not in raw


def test_nguon_mau_khong_doi_va_bam_lf_khop_p2():
    goc = Path(__file__).resolve().parents[2]
    nguon = {
        'e_hoa_don/goi/e_hoa_don/e_hoa_don/zip.py': '3be2a2156de2ba8f63c5a9679b8c4d344a6d7e5a8d12f838d5d440b2d4b3e733',
        'e_hoa_don/goi/e_hoa_don/e_hoa_don/hoa_don_xml.py': '8b7cb17848a5861b7384aefa31b22d6cc39f28b2e3486a0c4bc938929d397f32',
        'e_doi_chieu/goi/e_doi_chieu/e_doi_chieu/doc_docx.py': '7e63532c8ae2358ccc1b90a1bb65cb85e83c5c743fb3d8d9287fb2ed3cce3945',
        'e_doi_chieu/goi/e_doi_chieu/e_doi_chieu/cau_truc.py': 'ddde14383f97bf5c1fa1a2161aed7db8f3ea1e36004c16350a2db52018c2d333',
        'e_trich_xuat/goi/e_trich_xuat/e_trich_xuat/docx.py': '4290748070f8d5a8deee8a051c9ccdb384b1cb3ee8780e833d2781e5f84f1653',
    }
    for ten, sha in nguon.items():
        assert hashlib.sha256((goc / ten).read_bytes().replace(b'\r\n', b'\n')).hexdigest() == sha


def test_nguon_b1_utf8_va_sha_ban_chuyen_sau_sua():
    goi = Path(__file__).resolve().parents[1] / 'goi/e_mask'
    text = (goi / 'NGUON.md').read_text(encoding='utf-8')
    phan = text.split('## MASK-B1 — cổng ZIP/XML nội bộ, 15/11/2026')[1]
    assert 'Quyền tái dùng' in phan and '?' not in phan and '\ufffd' not in phan
    for ten in ('doc_tep.py', 'zip_an_toan.py', 'xml_an_toan.py'):
        raw = (goi / 'e_mask' / ten).read_bytes()
        assert hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest() in phan


def test_bien_doi_byte_dem_ngoai_le_co_dinh_khong_ro_du_lieu():
    raw = dong_goi(word_demo())
    rng = random.Random(20261115)
    for _ in range(300):
        sua = bytearray(raw)
        pos = rng.randrange(len(sua))
        sua[pos] ^= 1 << rng.randrange(8)
        with cam_io():
            try:
                kq = doc_goi(bytes(sua))
            except LoiNghiepVu as e:
                assert e.ma in ('MASK_TEP_CHUA_HO_TRO', 'MASK_QUA_GIOI_HAN')
                assert CANARY not in str(e)
            else:
                # Một số bit thuộc timestamp/quyền trong whitelist vẫn hợp lệ.
                assert kq.loai == 'docx'
