"""Writer ZIP nội bộ MASK-B4: giữ local record/payload part không sửa.

Chỉ nhận reader B2/B3 + edit script có băm, toàn bộ công việc trong RAM.
Không phải năng lực che/phát hành; hai lớp và upload thuộc B7/B9.
"""

import io
import struct
import zlib

from .doc_excel import ExcelDaDoc, doc_excel
from .doc_word import TaiLieuWord, doc_word
from .va_xml import (
    chuan_bi_va, chu_vung, doc_lai_nguon, goi_cua, va_phan,
)
from .zip_an_toan import (
    KHOI_DOC, PHAN_TOI_DA, TEP_TOI_DA, TONG_GIAI_NEN_TOI_DA,
    TY_LE_TOI_DA, kiem_ban_ghi, kiem_kich_thuoc_tep, _sai, _vuot,
)


class _BoDem(io.BytesIO):
    """Chép có sửa _BoDem của Hóa đơn; tính cả central directory và EOCD."""

    def ghi(self, data, *, du_tru=0):
        if self.tell() + len(data) + du_tru > TEP_TOI_DA:
            _vuot()
        return super().write(data)


def _nen(raw, co, tran, kiem_huy):
    """Một lần DEFLATE, không retry/đổi method để né trần ratio.

    Mức nén theo general-purpose bits 1–2: normal/max/fast/superfast.
    zlib mỗi lượt chỉ nhận một khối bounded, kiểm trước khi thêm buffer.
    """
    dem = bytearray()
    nen = zlib.compressobj({0: 6, 2: 9, 4: 3, 6: 1}[co & 6], wbits=-15)
    def ghi(data):
        if len(dem) + len(data) > tran:
            _vuot()
        dem.extend(data)
    try:
        for i in range(0, len(raw), KHOI_DOC):
            kiem_huy()
            ghi(nen.compress(memoryview(raw)[i:i + KHOI_DOC]))
        kiem_huy()
        ghi(nen.flush())
        if len(raw) > TY_LE_TOI_DA * len(dem):
            _vuot()
        kiem_huy()
        return bytes(dem)
    finally:
        dem.clear()


def _kiem_noi_dung(tai_lieu, moi, du_kien, kiem_huy):
    """So nghĩa từng vùng sau parse thật, kể cả shared dùng lặp/unused."""
    if type(moi) is not type(tai_lieu) or len(moi.vung) != len(du_kien):
        _sai()
    for truoc, sau, chu in zip(tai_lieu.vung, moi.vung, du_kien):
        kiem_huy()
        if chu_vung(sau) != chu:
            _sai()
        if type(tai_lieu) is TaiLieuWord:
            if ((truoc.ma, truoc.loai, truoc.phan, truoc.story, truoc.nut, truoc.o)
                    != (sau.ma, sau.loai, sau.phan, sau.story, sau.nut, sau.o)):
                _sai()
        elif ((truoc.ma, truoc.so_sheet, truoc.o, truoc.chi_so_chu, truoc.duoc_sua)
              != (sau.ma, sau.so_sheet, sau.o, sau.chi_so_chu, sau.duoc_sua)):
            _sai()
    if type(tai_lieu) is ExcelDaDoc:
        if ((tai_lieu.shared, tai_lieu.tham_chieu_chu, tai_lieu.styles,
             tai_lieu.gop_o, tai_lieu.epoch1904)
                != (moi.shared, moi.tham_chieu_chu, moi.styles, moi.gop_o, moi.epoch1904)
                or len(tai_lieu.o) != len(moi.o)):
            _sai()
        for truoc, sau in zip(tai_lieu.o, moi.o):
            kiem_huy()
            # Cả raw type/value/style/numFmt/epoch và 0 đầu giữ nguyên.
            if truoc.vung is None and truoc.xml_goc != sau.xml_goc:
                _sai()
    kiem_huy()


def ghi_goi(tai_lieu, kich_ban, *, kiem_huy):
    """Trả bytes ZIP khi toàn gói đạt; không nhận raw/dict/path thay reader.

    Reader gốc được dựng lại để chặn map/CRC/size/offset giả trong RAM.
    Đầu ra qua lại B1 + cùng reader, bao gồm mọi XML/quan hệ/metadata.
    Cổng reader hiện vẫn đếm bảo thủ 500.000 ký tự cả chiều đọc lại;
    writer không nới trần đó để làm qua một đầu ra khuếch đại.
    """
    kiem_huy()
    tai_lieu = doc_lai_nguon(tai_lieu, kiem_huy)
    goi = goi_cua(tai_lieu).zip
    ban_ghi = kiem_ban_ghi(goi, kiem_huy)
    cac_va, du_kien = chuan_bi_va(tai_lieu, kich_ban, kiem_huy)
    dem = _BoDem()
    thay_doi = {}
    try:
        if not cac_va:
            # Bao gồm script no-op: không viết lại cả EOCD hay header nào.
            kiem_kich_thuoc_tep(goi.goc)
            kiem_huy()
            return goi.goc
        raw = goi.goc
        du_tru = len(raw) - goi.le_danh_muc  # toàn central directory + EOCD
        tong = sum(p.so_byte + sum(len(d) - (b - a) for a, b, d in cac_va.get(p.ten, ()))
                   for p in goi.phan)
        if tong > TONG_GIAI_NEN_TOI_DA:
            _vuot()
        for b in sorted(ban_ghi, key=lambda b: b.phan.le_dau):
            kiem_huy()
            p = b.phan
            le_moi = dem.tell()
            if p.ten not in cac_va:
                # Chép cả local header + payload NÉN + descriptor nguyên bytes.
                for i in range(p.le_dau, b.le_cuoi_ban_ghi, KHOI_DOC):
                    kiem_huy()
                    dem.ghi(memoryview(raw)[i:min(i + KHOI_DOC, b.le_cuoi_ban_ghi)], du_tru=du_tru)
                thay_doi[p.ten] = (le_moi, None)
                continue
            data = va_phan(p.du_lieu, cac_va[p.ten], kiem_huy)
            if len(data) > PHAN_TOI_DA or tong > TONG_GIAI_NEN_TOI_DA:
                _vuot()
            descriptor_size = b.le_cuoi_ban_ghi - (p.le_du_lieu + p.so_byte_nen)
            header_size = p.le_du_lieu - p.le_dau
            tran_nen = TEP_TOI_DA - dem.tell() - du_tru - header_size - descriptor_size
            if tran_nen < 0:
                _vuot()
            payload = _nen(data, b.co, tran_nen, kiem_huy) if p.phuong_thuc == 8 else data
            if len(data) > TY_LE_TOI_DA * len(payload):
                _vuot()
            crc, nen, dai = zlib.crc32(data), len(payload), len(data)
            header = bytearray(raw[p.le_dau:p.le_du_lieu])
            if not b.local_rong:
                struct.pack_into('<3I', header, 14, crc, nen, dai)
            dem.ghi(header, du_tru=du_tru + descriptor_size + nen)
            for i in range(0, nen, KHOI_DOC):
                kiem_huy()
                dem.ghi(memoryview(payload)[i:i + KHOI_DOC], du_tru=du_tru + descriptor_size)
            if b.co & 8:
                descriptor = (b'PK\x07\x08' if b.descriptor_chu_ky else b'') + struct.pack('<3I', crc, nen, dai)
                dem.ghi(descriptor, du_tru=du_tru)
            thay_doi[p.ten] = (le_moi, (crc, nen, dai))
        le_danh_muc = dem.tell()
        for p in goi.phan:  # Giữ thứ tự central, độc lập thứ tự record vật lý.
            kiem_huy()
            le_moi, thong_so = thay_doi[p.ten]
            if thong_so is None and le_moi == p.le_dau:
                dem.ghi(memoryview(raw)[p.le_danh_muc:p.cuoi_danh_muc], du_tru=22)
            else:
                muc = bytearray(raw[p.le_danh_muc:p.cuoi_danh_muc])
                if thong_so is not None:
                    struct.pack_into('<3I', muc, 16, *thong_so)
                struct.pack_into('<I', muc, 42, le_moi)
                dem.ghi(muc, du_tru=22)
        kiem_huy()
        cuoi = bytearray(raw[-22:])
        struct.pack_into('<2I', cuoi, 12, dem.tell() - le_danh_muc, le_danh_muc)
        dem.ghi(cuoi)  # Đếm cả khi đóng ZIP, không trả ZIP cụt thiếu EOCD.
        kiem_huy()
        ket_qua = dem.getvalue()
        kiem_kich_thuoc_tep(ket_qua)
        doc = doc_word if type(tai_lieu) is TaiLieuWord else doc_excel
        moi = doc(ket_qua, kiem_huy=kiem_huy)
        kiem_ban_ghi(goi_cua(moi).zip, kiem_huy)
        _kiem_noi_dung(tai_lieu, moi, du_kien, kiem_huy)
        kiem_huy()
        return ket_qua
    finally:
        cac_va.clear()
        thay_doi.clear()
        dem.close()
