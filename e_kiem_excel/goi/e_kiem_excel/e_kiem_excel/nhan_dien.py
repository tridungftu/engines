"""Kiểm tệp trong RAM trước openpyxl; không giải nén ra máy."""

from io import BytesIO
from pathlib import PurePosixPath
import posixpath
import re
from xml.parsers import expat
from zipfile import BadZipFile, ZipFile, ZIP_STORED, ZIP_DEFLATED
import zlib

from kho_tri_thuc_sdk.engine import LoiNghiepVu

TEP_TOI_DA_BYTE = 20 * 1024 * 1024
GIAI_NEN_TOI_DA_BYTE = 128 * 1024 * 1024
ENTRY_TOI_DA = 2048
O_TOI_DA = 250_000
VUNG_TOI_DA = 500_000
OLE = bytes.fromhex("D0CF11E0A1B11AE1")
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CAU_VUOT_TRAN = "Tệp vượt giới hạn xử lý. Vui lòng tách tệp hoặc liên hệ quản trị."
CAU_HONG = "Không đọc được tệp Excel này. Vui lòng mở và lưu lại tệp rồi gửi lại."


def _vuot():
    raise LoiNghiepVu("VUOT_GIOI_HAN", CAU_VUOT_TRAN)


def _hong():
    raise LoiNghiepVu("TEP_HONG", CAU_HONG)


def kiem_tep(du_lieu, ten_tep, *, kiem_huy=lambda: None):
    """Đếm ô bằng SAX/Expat theo luồng, cấm mọi DTD/thực thể ở mọi XML.

    Chặn cả hình chữ nhật ô rất thưa: thuật toán gốc dùng iter_rows(),
    có thể tạo thêm hàng tỷ ô dù XML chỉ chứa hai thẻ c.
    """
    duoi = PurePosixPath(ten_tep.replace("\\", "/")).suffix.lower()
    if duoi not in {".xlsx", ".xlsm"} or du_lieu.startswith(OLE[:4]):
        raise LoiNghiepVu("TEP_KHONG_HO_TRO", "Chỉ nhận tệp Excel .xlsx hoặc .xlsm. Vui lòng lưu lại tệp theo định dạng này.")
    if len(du_lieu) > TEP_TOI_DA_BYTE:
        _vuot()
    if not du_lieu.startswith(b"PK\x03\x04"):
        _hong()
    so_o = tong_doc = tong_vung = 0
    try:
        with ZipFile(BytesIO(du_lieu)) as goi:
            ds = goi.infolist()
            if len(ds) > ENTRY_TOI_DA or sum(t.file_size for t in ds) > GIAI_NEN_TOI_DA_BYTE:
                _vuot()
            ten = [t.filename for t in ds]
            if len(set(ten)) != len(ten) or not {"[Content_Types].xml", "xl/workbook.xml"} <= set(ten):
                _hong()
            # .rels đi trước: worksheet có thể đặt ở đường dẫn/đuôi khác .xml.
            xml_sheet = set()
            for muc in sorted(ds, key=lambda t: not t.filename.lower().endswith('.rels')):
                kiem_huy()
                if muc.flag_bits & 1 or muc.compress_type not in {ZIP_STORED, ZIP_DEFLATED}:
                    _hong()
                la_sheet = False
                max_dong = max_cot = 0
                dong_hien_tai = cot_hien_tai = o_gop = 0
                bo_doc = None
                if muc.filename.lower().endswith((".xml", ".rels")) or muc.filename in xml_sheet:
                    bo_doc = expat.ParserCreate(namespace_separator="}")

                    def cam(*args):
                        _hong()

                    def bat_dau(nhan, thuoc_tinh):
                        nonlocal so_o, max_dong, max_cot, la_sheet, dong_hien_tai, cot_hien_tai, o_gop
                        if nhan == NS_REL + '}Relationship' and thuoc_tinh.get('Type', '').endswith('/worksheet'):
                            if thuoc_tinh.get('TargetMode') != 'External':
                                target = thuoc_tinh.get('Target', '')
                                base = str(PurePosixPath(muc.filename).parent.parent)
                                xml_sheet.add(posixpath.normpath(target.lstrip('/') if target.startswith('/') else base+'/'+target))
                        if nhan == NS + '}worksheet':
                            la_sheet = True
                        if la_sheet and nhan == NS + '}row':
                            try:
                                dong_hien_tai = int(thuoc_tinh.get('r', dong_hien_tai + 1))
                            except ValueError:
                                _hong()
                            cot_hien_tai = 0
                        if la_sheet and nhan == NS + "}c":
                            so_o += 1
                            if so_o > O_TOI_DA:
                                _vuot()
                            vi_tri = thuoc_tinh.get("r")
                            dong, cot = _toa_do(vi_tri) if vi_tri else (dong_hien_tai, cot_hien_tai + 1)
                            cot_hien_tai = cot
                            if not (1 <= cot <= 16384 and 1 <= dong <= 1048576):
                                _hong()
                            max_dong, max_cot = max(max_dong, dong), max(max_cot, cot)
                            if tong_vung + max_dong * max_cot > VUNG_TOI_DA:
                                _vuot()
                        if la_sheet and nhan == NS + '}mergeCell':
                            vung = thuoc_tinh.get('ref', '').split(':')
                            if len(vung) not in (1, 2):
                                _hong()
                            d1, c1 = _toa_do(vung[0]); d2, c2 = _toa_do(vung[-1])
                            if d2 < d1 or c2 < c1:
                                _hong()
                            o_gop += (d2-d1+1)*(c2-c1+1)
                            if o_gop + so_o > O_TOI_DA:
                                _vuot()
                            max_dong, max_cot = max(max_dong,d2), max(max_cot,c2)
                            if tong_vung + max_dong * max_cot > VUNG_TOI_DA:
                                _vuot()

                    bo_doc.StartDoctypeDeclHandler = cam
                    bo_doc.EntityDeclHandler = cam
                    bo_doc.ExternalEntityRefHandler = cam
                    bo_doc.StartElementHandler = bat_dau
                with goi.open(muc) as luong:
                    while True:
                        kiem_huy()
                        khoi = luong.read(64 * 1024)
                        tong_doc += len(khoi)
                        if tong_doc > GIAI_NEN_TOI_DA_BYTE:
                            _vuot()
                        if bo_doc:
                            bo_doc.Parse(khoi, not khoi)
                        if not khoi:
                            break
                if la_sheet:
                    tong_vung += max_dong * max_cot
    except (BadZipFile, expat.ExpatError, zlib.error, OSError, ValueError, EOFError, NotImplementedError):
        _hong()
    return {"so_o": so_o, "so_entry": len(ds), "giai_nen_byte": tong_doc, "so_o_vung": tong_vung}


def _toa_do(vi_tri):
    m = re.fullmatch(r"([A-Z]{1,3})([1-9][0-9]{0,6})", vi_tri)
    if not m:
        _hong()
    cot = 0
    for chu in m[1]:
        cot = cot * 26 + ord(chu) - 64
    dong = int(m[2])
    if cot > 16384 or dong > 1048576:
        _hong()
    return dong, cot
