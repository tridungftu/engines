"""Đọc Excel/CSV trong RAM thành lô theo khuôn cột của module.

Excel chỉ giữ khoảng 15 chữ số có nghĩa: Decimal(repr(x)) giữ giá trị
openpyxl đọc được, không thể khôi phục chữ số Excel đã làm mất khi lưu.
Kiểm ZIP/XML chép-sửa từ e_kiem_excel/nhan_dien.py; không gọi engine đó.
"""
from __future__ import annotations

import csv
from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal
from io import BytesIO, StringIO
import json
from pathlib import PurePosixPath
import posixpath
import re
from xml.parsers import expat
from zipfile import BadZipFile, ZipFile, ZIP_DEFLATED, ZIP_STORED
import zlib

import openpyxl

from .doc_lo import TOI_DA_BYTE, TOI_DA_DONG, _doc_dong, doc_lo_json
from .kieu import Lo
from .loi import CAU_LOI, loi
from .tien import doc_so_thap_phan, doc_tien
from .tu_khoa import chuan, doc_json

GIAI_NEN_TOI_DA_BYTE = 128 * 1024 * 1024
ENTRY_TOI_DA = 2048
O_TOI_DA = 250_000
VUNG_TOI_DA = 500_000
OLE = bytes.fromhex("D0CF11E0A1B11AE1")
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
NS_REL = "http://schemas.openxmlformats.org/package/2006/relationships}"
CAC_TRUONG = frozenset({"ma", "ngay", "so_tien", "so_tien_quy_doi", "loai",
                       "doi_tac", "dien_giai", "tai_khoan_no", "tai_khoan_co",
                       "nhap_tay", "co_do_cung", "tien_te", "tien_te_quy_doi"})
BAT_BUOC = frozenset({"ma", "ngay", "so_tien"})


def _kiem_bytes(du_lieu):
    if not isinstance(du_lieu, bytes):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    if len(du_lieu) > TOI_DA_BYTE:
        raise loi("VUOT_GIOI_HAN")


def _toa_do(chuoi):
    m = re.fullmatch(r"([A-Z]{1,3})([1-9][0-9]{0,6})", chuoi or "")
    if not m:
        raise loi("DU_LIEU_KHONG_HOP_LE")
    cot = 0
    for chu in m[1]:
        cot = cot * 26 + ord(chu) - 64
    dong = int(m[2])
    if cot > 16384 or dong > 1048576:
        raise loi("DU_LIEU_KHONG_HOP_LE")
    return dong, cot


def _kiem_xlsx(du_lieu):
    """Chặn trần ZIP, XML có thực thể và vùng ô thưa trước openpyxl.

    Đọc theo khối 64 KiB; kiểm cả dung lượng khai báo lẫn số byte thực đọc.
    .rels được đọc trước để nhận ra worksheet có đường dẫn không đuôi XML.
    """
    _kiem_bytes(du_lieu)
    tong_doc = so_o = tong_vung = 0
    try:
        with ZipFile(BytesIO(du_lieu)) as goi:
            ds = goi.infolist()
            if (len(ds) > ENTRY_TOI_DA
                    or sum(t.file_size for t in ds) > GIAI_NEN_TOI_DA_BYTE):
                raise loi("VUOT_GIOI_HAN")
            ten = [t.filename for t in ds]
            if (len(set(ten)) != len(ten)
                    or not {"[Content_Types].xml", "xl/workbook.xml"} <= set(ten)):
                raise loi("DU_LIEU_KHONG_HOP_LE")
            xml_sheet = set()
            for muc in sorted(ds, key=lambda t: not t.filename.lower().endswith(".rels")):
                if muc.flag_bits & 1 or muc.compress_type not in {ZIP_STORED, ZIP_DEFLATED}:
                    raise loi("DU_LIEU_KHONG_HOP_LE")
                la_sheet = False
                max_dong = max_cot = dong_hien_tai = cot_hien_tai = o_gop = 0
                bo_doc = None
                if muc.filename.lower().endswith((".xml", ".rels")) or muc.filename in xml_sheet:
                    bo_doc = expat.ParserCreate(namespace_separator="}")

                    def cam(*_):
                        raise loi("DU_LIEU_KHONG_HOP_LE")

                    def bat_dau(nhan, tt):
                        nonlocal so_o, la_sheet, max_dong, max_cot
                        nonlocal dong_hien_tai, cot_hien_tai, o_gop
                        if nhan == NS_REL + "Relationship" and tt.get("Type", "").endswith("/worksheet"):
                            if tt.get("TargetMode") != "External":
                                target = tt.get("Target", "")
                                base = str(PurePosixPath(muc.filename).parent.parent)
                                xml_sheet.add(posixpath.normpath(
                                    target.lstrip("/") if target.startswith("/") else base + "/" + target))
                        if nhan == NS + "worksheet":
                            la_sheet = True
                        if la_sheet and nhan == NS + "dimension":
                            # read_only có thể tin dimension ngay cả khi XML rất ít ô.
                            vung = tt.get("ref", "").split(":")
                            if len(vung) not in (1, 2):
                                cam()
                            d, c = _toa_do(vung[-1])
                            max_dong, max_cot = max(max_dong, d), max(max_cot, c)
                        if la_sheet and nhan == NS + "row":
                            dong_hien_tai = int(tt.get("r", dong_hien_tai + 1))
                            cot_hien_tai = 0
                        if la_sheet and nhan == NS + "c":
                            so_o += 1
                            if so_o > O_TOI_DA:
                                raise loi("VUOT_GIOI_HAN")
                            d, c = (_toa_do(tt["r"]) if "r" in tt
                                    else (dong_hien_tai, cot_hien_tai + 1))
                            if not (1 <= d <= 1048576 and 1 <= c <= 16384):
                                cam()
                            cot_hien_tai = c
                            max_dong, max_cot = max(max_dong, d), max(max_cot, c)
                        if la_sheet and nhan == NS + "mergeCell":
                            vung = tt.get("ref", "").split(":")
                            if len(vung) not in (1, 2):
                                cam()
                            d1, c1 = _toa_do(vung[0])
                            d2, c2 = _toa_do(vung[-1])
                            if d2 < d1 or c2 < c1:
                                cam()
                            o_gop += (d2 - d1 + 1) * (c2 - c1 + 1)
                            if o_gop + so_o > O_TOI_DA:
                                raise loi("VUOT_GIOI_HAN")
                            max_dong, max_cot = max(max_dong, d2), max(max_cot, c2)
                        if la_sheet and tong_vung + max_dong * max_cot > VUNG_TOI_DA:
                            raise loi("VUOT_GIOI_HAN")

                    bo_doc.StartDoctypeDeclHandler = cam
                    bo_doc.EntityDeclHandler = cam
                    bo_doc.ExternalEntityRefHandler = cam
                    bo_doc.StartElementHandler = bat_dau
                with goi.open(muc) as luong:
                    while True:
                        khoi = luong.read(64 * 1024)
                        tong_doc += len(khoi)
                        if tong_doc > GIAI_NEN_TOI_DA_BYTE:
                            raise loi("VUOT_GIOI_HAN")
                        if bo_doc:
                            bo_doc.Parse(khoi, not khoi)
                        if not khoi:
                            break
                if la_sheet:
                    tong_vung += max_dong * max_cot
    except (BadZipFile, expat.ExpatError, zlib.error, OSError, ValueError,
            EOFError, NotImplementedError):
        raise loi("DU_LIEU_KHONG_HOP_LE") from None


def nhan_dien(du_lieu: bytes, ten: str | None, mime: str | None) -> str:
    """Nhận diện theo chữ ký trước, rồi đuôi/mime; không nhận .xls cũ."""
    _kiem_bytes(du_lieu)
    if du_lieu.startswith(OLE[:4]):
        raise loi("TEP_KHONG_HO_TRO")
    duoi = PurePosixPath((ten or "").replace("\\", "/")).suffix.lower()
    if du_lieu.startswith(b"PK\x03\x04") and duoi == ".xlsx":
        _kiem_xlsx(du_lieu)
        return "xlsx"
    dau = du_lieu.removeprefix(b"\xef\xbb\xbf").lstrip()
    if dau.startswith(b"{"):
        return "json"
    if duoi == ".csv" or (mime or "").split(";", 1)[0].strip().lower() == "text/csv":
        return "csv"
    raise loi("TEP_KHONG_HO_TRO")


def _doc_khuon(chuoi):
    k = doc_json(chuoi)
    if (not isinstance(k, dict) or set(k) != {"phien_ban", "sheet", "cot", "dong_dung"}
            or type(k["phien_ban"]) is not int or k["phien_ban"] != 1
            or not (k["sheet"] is None or isinstance(k["sheet"], str) and k["sheet"].strip())
            or not isinstance(k["cot"], list) or not 1 <= len(k["cot"]) <= 30
            or not isinstance(k["dong_dung"], list)):
        raise loi("THAM_SO_KHONG_HOP_LE")
    cac_ma, tu = set(), list(k["dong_dung"])
    for c in k["cot"]:
        if (not isinstance(c, dict) or set(c) != {"ma", "tu_khoa", "bat_buoc"}
                or not isinstance(c["ma"], str) or c["ma"] in cac_ma
                or not (c["ma"] in CAC_TRUONG
                        or c["ma"].startswith("thuoc_tinh.") and len(c["ma"]) > 11)
                or type(c["bat_buoc"]) is not bool
                or not isinstance(c["tu_khoa"], list) or not c["tu_khoa"]):
            raise loi("THAM_SO_KHONG_HOP_LE")
        cac_ma.add(c["ma"])
        tu.extend(c["tu_khoa"])
    if (not BAT_BUOC <= {c["ma"] for c in k["cot"] if c["bat_buoc"]}
            or len(tu) > 200 or any(not isinstance(t, str) or not chuan(t) for t in tu)):
        raise loi("THAM_SO_KHONG_HOP_LE")
    return k


def _co(v):
    return v is not None and (not isinstance(v, str) or bool(v.strip()))


def _ngay(v):
    if isinstance(v, datetime):
        return v.date().isoformat()
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, str) and re.fullmatch(r"[0-9]{2}/[0-9]{2}/[0-9]{4}", v):
        try:
            return datetime.strptime(v, "%d/%m/%Y").date().isoformat()
        except ValueError:
            raise loi("DU_LIEU_KHONG_HOP_LE") from None
    return v  # doc_lo kiểm ISO nghiêm và ngày thực tế.


def _so(v):
    if type(v) in (int, float):
        v = Decimal(repr(v))
    return format(doc_so_thap_phan(v), "f")


def _tim_tieu_de(cac_dong, khuon):
    for hang in cac_dong:
        tieu_de = [chuan(v) for v in hang]
        anh_xa = {}
        for c in khuon["cot"]:
            tu = {chuan(t) for t in c["tu_khoa"]}
            trung = [i for i, v in enumerate(tieu_de) if v in tu]
            if len(trung) > 1 or c["bat_buoc"] and not trung:
                break
            if trung:
                anh_xa[c["ma"]] = trung[0]
        else:
            if len(set(anh_xa.values())) == len(anh_xa):
                return anh_xa
    return None


def _doc_cac_dong(cac_dong, khuon, tien_te, *, cot=None):
    cac_dong = iter(cac_dong)
    if cot is None:
        cot = _tim_tieu_de(cac_dong, khuon)
    if cot is None:
        raise loi("THAM_SO_KHONG_HOP_LE")
    ds = []
    for hang in cac_dong:
        if not any(_co(v) for v in hang):
            continue
        dau = next(v for v in hang if _co(v))
        if chuan(dau) in {chuan(t) for t in khuon["dong_dung"]}:
            break
        if len(ds) >= TOI_DA_DONG:
            raise loi("VUOT_GIOI_HAN")
        gia_tri = {k: hang[i] for k, i in cot.items() if i < len(hang) and _co(hang[i])}
        dong = {}
        for k, v in gia_tri.items():
            if k in {"so_tien", "so_tien_quy_doi", "tien_te", "tien_te_quy_doi"}:
                continue
            if k == "ngay":
                dong[k] = _ngay(v)
            elif k in {"nhap_tay", "co_do_cung"}:
                if type(v) is bool:
                    dong[k] = v
                elif str(v).lower() in {"true", "false", "0", "1"}:
                    dong[k] = str(v).lower() in {"true", "1"}
                else:
                    raise loi("DU_LIEU_KHONG_HOP_LE")
            elif k.startswith("thuoc_tinh."):
                dong.setdefault("thuoc_tinh", {})[k[11:]] = str(v)
            else:
                dong[k] = str(v)
        for k, cot_te in (("so_tien", "tien_te"), ("so_tien_quy_doi", "tien_te_quy_doi")):
            if k in gia_tri:
                # Cột có mặt nhưng ô trống nghĩa là chưa rõ; không lấp bằng cài đặt.
                te = gia_tri.get(cot_te) if cot_te in cot else tien_te
                dong[k] = {"so": _so(gia_tri[k]), "tien_te": te}
        ds.append(dong)
    return ds


def doc_lo_bang(du_lieu, kieu, *, khuon_cot_json: str, ma_module: str,
               tien_te: str | None, ky: str | None) -> Lo:
    """Đọc bảng; dùng parser doc_lo kiểm thông tin lô và từng dòng."""
    _kiem_bytes(du_lieu)
    if du_lieu.startswith(OLE[:4]):
        raise loi("TEP_KHONG_HO_TRO")
    khuon = _doc_khuon(khuon_cot_json)
    lo = doc_lo_json(json.dumps({"phien_ban": 1, "ma_module": ma_module,
                                "ky": ky, "nghiep_vu": []}).encode("utf-8"))
    # Kiểm cả cài đặt không được dùng do bảng đã có cột tiền tệ.
    doc_tien({"so": "0", "tien_te": tien_te})
    if kieu == "xlsx":
        _kiem_xlsx(du_lieu)
        try:
            wb = openpyxl.load_workbook(BytesIO(du_lieu), read_only=True, data_only=True,
                                        keep_links=False)
        except Exception:
            raise loi("DU_LIEU_KHONG_HOP_LE") from None
        try:
            if khuon["sheet"] is not None:
                if khuon["sheet"] not in wb.sheetnames:
                    raise loi("THAM_SO_KHONG_HOP_LE")
                cac_sheet = [wb[khuon["sheet"]]]
            else:
                cac_sheet = wb.worksheets
            # sheet=null: lấy bảng đầu tiên có tiêu đề khớp, theo thứ tự sheet.
            for sheet in cac_sheet:
                cac_dong = sheet.iter_rows(values_only=True)
                cot = _tim_tieu_de(cac_dong, khuon)
                if cot is not None:
                    ds = _doc_cac_dong(cac_dong, khuon, tien_te, cot=cot)
                    break
            else:
                raise loi("THAM_SO_KHONG_HOP_LE")
        except Exception as exc:
            if getattr(exc, "ma", None) in CAU_LOI:
                raise
            raise loi("DU_LIEU_KHONG_HOP_LE") from None
        finally:
            wb.close()
    elif kieu == "csv":
        gioi_han_cu = csv.field_size_limit()
        try:
            csv.field_size_limit(TOI_DA_BYTE)
            chuoi = du_lieu.decode("utf-8-sig")
            # Thử hai dấu phân cách: tiêu đề phải khớp khuôn, không đoán từ dòng dữ liệu.
            for dau in (",", ";"):
                cac_dong = csv.reader(StringIO(chuoi, newline=""), delimiter=dau, strict=True)
                try:
                    cot = _tim_tieu_de(cac_dong, khuon)
                except csv.Error:
                    # Dấu sai có thể làm QUOTE_ALL lỗi trước khi tìm thấy tiêu đề.
                    continue
                if cot is not None:
                    ds = _doc_cac_dong(cac_dong, khuon, tien_te, cot=cot)
                    break
            else:
                raise loi("THAM_SO_KHONG_HOP_LE")
        except UnicodeDecodeError:
            raise loi("TEP_KHONG_HO_TRO") from None
        except csv.Error:
            raise loi("DU_LIEU_KHONG_HOP_LE") from None
        finally:
            csv.field_size_limit(gioi_han_cu)
    else:
        raise loi("TEP_KHONG_HO_TRO")
    # Không áp trần byte lần hai lên JSON trung gian (có thể lớn hơn tệp bảng).
    # Luật từng dòng dùng đúng hàm của doc_lo, không diễn giải lại ở đây.
    nghiep_vu, cac_ma = [], set()
    for chi_so, dong in enumerate(ds):
        nv = _doc_dong(dong, chi_so)
        if nv.ma in cac_ma:
            raise loi("DU_LIEU_KHONG_HOP_LE")
        cac_ma.add(nv.ma)
        nghiep_vu.append(nv)
    return replace(lo, nghiep_vu=tuple(nghiep_vu))
