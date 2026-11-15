"""Hồi quy gộp B2/B3: XLSX DEMO kiểu Office qua cả hai cổng trong RAM."""

import struct

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu

from e_mask.doc_excel import doc_excel
from e_mask.doc_tep import doc_tep, doc_zip
from e_mask.zip_an_toan import CAU_CHUA_HO_TRO
from ho_tro_mask_b1 import excel_demo
from ho_tro_mask_b3 import goi_office


def _phan_excel():
    return excel_demo(noi_dung='<row r="1"><c r="A1" t="inlineStr">'
                      '<is><t>DEMO Nguyễn Lan</t></is></c></row>')


@pytest.mark.parametrize('chu_ky', [True, False])
def test_xlsx_office_qua_cong_chung_va_reader_excel(chu_ky):
    raw = goi_office(_phan_excel(), co=0x0006, descriptor=True, chu_ky=chu_ky)
    chung = doc_tep(raw, kiem_huy=lambda: None)
    excel = doc_excel(raw, kiem_huy=lambda: None).goi
    assert chung.loai == excel.goi.loai == 'xlsx'
    assert chung.zip.goc == excel.goi.zip.goc == raw
    assert len(chung.zip.phan) == len(excel.ban_ghi)
    for p, b in zip(chung.zip.phan, excel.ban_ghi):
        assert (p.ten, p.du_lieu) == (b.phan.ten, next(
            q.du_lieu for q in excel.goi.zip.phan if q.ten == p.ten))
        assert p.le_cuoi == b.le_cuoi_ban_ghi
        assert p.le_du_lieu + p.so_byte_nen == b.phan.le_cuoi
        assert p.le_cuoi - b.phan.le_cuoi == (16 if chu_ky else 12)
        assert b.co == 0x000e
    assert chung.zip.phan[-1].le_cuoi == chung.zip.le_danh_muc


@pytest.mark.parametrize('doc', [doc_tep, doc_excel])
@pytest.mark.parametrize('chu_ky', [True, False])
@pytest.mark.parametrize('truong', [0, 4, 8], ids=['crc', 'size_nen', 'size_goc'])
def test_xlsx_descriptor_sai_crc_hoac_size_bi_chan(doc, chu_ky, truong):
    raw = bytearray(goi_office(_phan_excel(), co=0x0006, descriptor=True, chu_ky=chu_ky))
    central = raw.index(b'PK\x01\x02')
    nen = struct.unpack_from('<I', raw, central + 20)[0]
    ten = struct.unpack_from('<H', raw, 26)[0]
    descriptor = 30 + ten + nen
    raw[descriptor + (4 if chu_ky else 0) + truong] ^= 1
    ket_qua = []
    with pytest.raises(LoiNghiepVu) as exc:
        ket_qua.append(doc(bytes(raw), kiem_huy=lambda: None))
    assert not ket_qua
    assert (exc.value.ma, exc.value.thong_diep) == (
        'MASK_TEP_CHUA_HO_TRO', CAU_CHUA_HO_TRO)


@pytest.mark.parametrize('cong', ['chung', 'excel'])
@pytest.mark.parametrize('do_dai,dat', [(256, True), (257, False)])
def test_ten_zip_office_gioi_han_chung_cho_excel(cong, do_dai, dat):
    from e_mask.doc_tep import _doc_zip_excel

    raw = goi_office({'D' * do_dai: b'DEMO'}, co=0x0006, descriptor=True)
    doc = doc_zip if cong == 'chung' else _doc_zip_excel
    if dat:
        ket_qua = doc(raw, lambda: None)
        goi = ket_qua if cong == 'chung' else ket_qua[0]
        assert goi.phan[0].ten == 'D' * 256
    else:
        with pytest.raises(LoiNghiepVu) as exc:
            doc(raw, lambda: None)
        assert exc.value.ma == 'MASK_TEP_CHUA_HO_TRO'
