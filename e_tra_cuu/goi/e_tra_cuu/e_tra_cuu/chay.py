"""Điểm vào SDK 2.2.0; cấu hình chụp theo việc, dữ liệu qua ngăn Core."""

from copy import deepcopy
import json
import math
from pathlib import Path
import re

from kho_tri_thuc_sdk.engine import ChuaRo, Engine, LoiDuongTruyen, LoiNghiepVu, ViecDaHuy

from .ho_so import nhan_yeu_cau
from .cat_doan import cat_doan
from .chuan_bi_ai import chuan_bi_ai, doc_snapshot_ai
from .cau_hoi import phan_tich_cau_hoi
from .xep_hang import xep_hang_lai
from .phan_loai import phan_loai_tai_lieu
from .tra_loi import soan_tra_loi
from .xuat_ket_qua import xuat_ket_qua
from .bang_chung import chuan_bi_tang_mot
from .kiem_dau_vao import doi_tuong, loi
from .trang_thai import lay_hoac_tao_dot, cap_nhat_cac_dot


_GOI = Path(__file__).resolve().parent.parent
# Chỉ đọc schema đóng gói; giá trị cấu hình luôn do Core cấp.
SCHEMA = json.loads((_GOI / "cau_hinh.schema.json").read_text(encoding="utf-8"))


def _sai_cau_hinh():
    raise LoiNghiepVu("CAU_HINH_KHONG_HOP_LE",
                     "Cấu hình engine không hợp lệ. Hãy nhờ quản trị viên kiểm tra lại.")


def _kiem_muc_cau_hinh(v, s):
    """Kiểm riêng schema cấu hình đóng gói khi đọc lại snapshot cũ.

    Không phải bộ kiểm JSON Schema tổng quát; không nhận schema từ caller.
    Core kiểm cấu hình lúc lưu; engine kiểm lại kiểu, trần và quan hệ nghiệp vụ.
    """
    kieu = s["type"]
    hop_le = {"object": type(v) is dict, "string": type(v) is str,
              "integer": type(v) is int,
              "number": type(v) in (int, float) and math.isfinite(v)}
    if not hop_le.get(kieu, False):
        _sai_cau_hinh()
    if kieu == "object":
        props = s["properties"]
        if set(v) - props.keys() or not set(s.get("required", [])) <= v.keys():
            _sai_cau_hinh()
        v = deepcopy(v)
        for k, con in props.items():
            if k not in v and "default" in con:
                v[k] = deepcopy(con["default"])
            if k in v:
                v[k] = _kiem_muc_cau_hinh(v[k], con)
    elif kieu == "string":
        if (not s.get("minLength", 0) <= len(v) <= s.get("maxLength", math.inf)
                or ("pattern" in s and re.search(s["pattern"], v) is None)):
            _sai_cau_hinh()
    elif not s.get("minimum", -math.inf) <= v <= s.get("maximum", math.inf):
        _sai_cau_hinh()
    if "const" in s and (type(v) is not type(s["const"]) or v != s["const"]):
        _sai_cau_hinh()
    if "enum" in s and v not in s["enum"]:
        _sai_cau_hinh()
    return v


def yeu_cau_cau_hinh(viec):
    """Chỉ dùng bản chụp SDK của việc; không đọc app/ngăn hoặc tệp cấu hình."""
    cau_hinh = deepcopy(viec.cau_hinh)
    if type(cau_hinh) is dict and not {"phien_ban", "quy_tac_nhom"} <= cau_hinh.keys():
        raise LoiNghiepVu(
            "CHUA_CAU_HINH",
            "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình.",
        )
    try:
        cau_hinh = _kiem_muc_cau_hinh(cau_hinh, SCHEMA)
        phan_loai = cau_hinh["phan_loai"]
        da_do = phan_loai["trang_thai"] == "da_do"
        if (da_do and not {"nguong", "bam_bo_do"} <= phan_loai.keys()) or (
            not da_do and {"nguong", "bam_bo_do"} & phan_loai.keys()
        ):
            _sai_cau_hinh()
        if cau_hinh["cat_doan"]["do_dai_muc_tieu"] > cau_hinh["cat_doan"]["ky_tu_don_vi_toi_da"]:
            _sai_cau_hinh()
        json.dumps(cau_hinh, ensure_ascii=False, allow_nan=False).encode("utf-8")
        return cau_hinh
    except (ValueError, TypeError, AttributeError, RecursionError, OverflowError):
        _sai_cau_hinh()


def chup_cau_hinh(viec):
    # SDK 2.2.0 chưa công khai phien_ban_cau_hinh trên Viec. Không bịa CAS;
    # null biểu thị chưa có phiên bản, băm và snapshot Core ghim giá trị.
    return {"gia_tri": yeu_cau_cau_hinh(viec), "row_version": None}


def kiem_cau_hinh_da_chup(cau_hinh):
    """Kiểm giá trị đã ghim, không thay bằng cấu hình mới trong lúc hậu kiểm."""
    from types import SimpleNamespace

    doi_tuong(cau_hinh, ("gia_tri", "row_version"), ())

    try:
        phien = cau_hinh["row_version"]
        if phien is not None and (type(phien) is not int or phien < 1):
            loi("TC_SAI_NGUON")
        return {"gia_tri": yeu_cau_cau_hinh(SimpleNamespace(cau_hinh=cau_hinh["gia_tri"])),
                "row_version": cau_hinh["row_version"]}
    except LoiNghiepVu:
        loi("TC_SAI_NGUON")


app = Engine.tu_khai_bao("engine.json")


def ghi_bai_do_demo(viec, ung_dung, *, ma_dot=None, gia_tri=None, cac_dot=None):
    """Seam thuần cho test/cửa Core sau này, KHÔNG đăng ký API quản trị SDK.

    Core kiểm quyền trước khi gọi; pháp nhân chỉ lấy từ ngữ cảnh việc.
    Không nhận pháp nhân từ dữ liệu bài đo, không ghi tự động từ pipeline.
    """
    ngu_canh = getattr(viec, "ngu_canh", None)
    p = ngu_canh.get("phap_nhan_id") if isinstance(ngu_canh, dict) else None
    if not isinstance(p, str) or not p.strip():
        raise LoiNghiepVu("TC_THIEU_NGU_CANH", "Thiếu ngữ cảnh pháp nhân do Core cấp.")
    ngan_viec = getattr(viec, "ngan", None)
    if ngan_viec is None:
        raise LoiNghiepVu("NGAN_CAN_VIEC", "Cần nhận việc trước khi dùng ngăn này.")
    # Bảng pháp nhân bắt buộc đi trong việc; không fallback sang app.ngan.
    if cac_dot is not None:
        return cap_nhat_cac_dot(ngan_viec, cac_dot)
    return lay_hoac_tao_dot(ngan_viec, ma_dot, gia_tri)


def dang_ky_nang_luc(ung_dung):
    """Cửa nguồn là dependency do bên chủ Core gắn, không lấy từ payload.

    SDK 2.2.0 chưa có cửa này. Chỉ tests gắn adapter C-TC-02/03; runtime
    thiếu cửa phải từ chối, không coi đây là API SDK đã được phát hành.
    """
    @ung_dung.nang_luc("tra_cuu.nhan_yeu_cau@1")
    def nhan(viec):
        try:
            cau_hinh = chup_cau_hinh(viec)
            return nhan_yeu_cau(viec, cau_hinh, getattr(ung_dung, "cua_nguon", None),
                                ung_dung.phien_ban)
        except (LoiNghiepVu, LoiDuongTruyen, ChuaRo, ViecDaHuy):
            raise
        except Exception:
            # SDK ghi traceback ngoại lệ bất ngờ. Chặn tại biên handler
            # để lỗi adapter/ngăn không đưa nội dung nguồn vào nhật ký SDK.
            raise LoiNghiepVu("ENGINE_LOI_XU_LY", "Engine gặp lỗi khi xử lý việc này.") from None

    def chua_lam(viec):
        raise LoiNghiepVu("CHUA_LAM", "Chức năng tra cứu đang được hoàn thiện.")

    @ung_dung.nang_luc("tra_cuu.cat_doan@1")
    def cat(viec):
        try:
            return cat_doan(viec, getattr(ung_dung, "cua_nguon", None),
                            ung_dung.phien_ban, kiem_cau_hinh_da_chup)
        except (LoiNghiepVu, LoiDuongTruyen, ChuaRo, ViecDaHuy):
            raise
        except (ValueError, TypeError, KeyError, AttributeError, RecursionError, OverflowError):
            loi()
        except Exception:
            raise LoiNghiepVu("ENGINE_LOI_XU_LY", "Engine gặp lỗi khi xử lý việc này.") from None

    @ung_dung.nang_luc("tra_cuu.chuan_bi_ai@1")
    def chuan_bi(viec):
        try:
            h = viec.dau_vao.get("ho_so_tra_cuu", {})
            if h.get("tac_vu") == "soan_tra_loi" and h.get("tom_tat", {}).get("tang") == 1:
                return chuan_bi_tang_mot(viec, getattr(ung_dung, "cua_nguon", None),
                                        ung_dung.phien_ban, kiem_cau_hinh_da_chup)
            if (h.get("tac_vu") == "xep_hang_lai"
                    and h.get("tom_tat", {}).get("so_ung_vien") == 0):
                # Kiểm nguồn trước khi từ chối nhánh AI rỗng. Core rẽ từ da_nhan.
                doc_snapshot_ai(viec, getattr(ung_dung, "cua_nguon", None),
                                ung_dung.phien_ban, kiem_cau_hinh_da_chup)
                loi("TC_SAI_GIAI_DOAN")
            return chuan_bi_ai(viec, getattr(ung_dung, "cua_nguon", None),
                               ung_dung.phien_ban, kiem_cau_hinh_da_chup)
        except (LoiNghiepVu, LoiDuongTruyen, ChuaRo, ViecDaHuy):
            raise
        except (ValueError, TypeError, KeyError, AttributeError, RecursionError, OverflowError):
            loi()
        except Exception:
            raise LoiNghiepVu("ENGINE_LOI_XU_LY", "Engine gặp lỗi khi xử lý việc này.") from None

    def hau_kiem_tc_6(ham):
        def xu_ly(viec):
            try:
                return ham(viec, getattr(ung_dung, "cua_nguon", None),
                           ung_dung.phien_ban, kiem_cau_hinh_da_chup)
            except (LoiNghiepVu, LoiDuongTruyen, ChuaRo, ViecDaHuy):
                raise
            except (ValueError, TypeError, KeyError, AttributeError, RecursionError, OverflowError):
                raise LoiNghiepVu("TC_AI_SAI_KHUON", "Phản hồi AI chưa đúng khuôn hoặc căn cứ tra cứu. Anh thử lại từ hồ sơ.") from None
            except Exception:
                raise LoiNghiepVu("ENGINE_LOI_XU_LY", "Engine gặp lỗi khi xử lý việc này.") from None
        return xu_ly

    ung_dung.nang_luc("tra_cuu.phan_tich_cau_hoi@1")(hau_kiem_tc_6(phan_tich_cau_hoi))
    ung_dung.nang_luc("tra_cuu.xep_hang_lai@1")(hau_kiem_tc_6(xep_hang_lai))
    ung_dung.nang_luc("tra_cuu.soan_tra_loi@1")(hau_kiem_tc_6(soan_tra_loi))

    @ung_dung.nang_luc("tra_cuu.phan_loai_tai_lieu@1")
    def phan_loai(viec):
        try:
            return phan_loai_tai_lieu(viec, getattr(ung_dung, "cua_nguon", None),
                                     ung_dung.phien_ban, kiem_cau_hinh_da_chup)
        except (LoiNghiepVu, LoiDuongTruyen, ChuaRo, ViecDaHuy):
            raise
        except (ValueError, TypeError, KeyError, AttributeError, RecursionError, OverflowError):
            loi("TC_SAI_NGUON")
        except Exception:
            raise LoiNghiepVu("ENGINE_LOI_XU_LY", "Engine gặp lỗi khi xử lý việc này.") from None

    @ung_dung.nang_luc("tra_cuu.xuat_ket_qua@1")
    def xuat(viec):
        try:
            return xuat_ket_qua(viec, getattr(ung_dung, "cua_nguon", None),
                                ung_dung.phien_ban, kiem_cau_hinh_da_chup)
        except (LoiNghiepVu, LoiDuongTruyen, ChuaRo, ViecDaHuy):
            raise
        except (ValueError, TypeError, KeyError, AttributeError, RecursionError, OverflowError):
            loi("TC_SAI_NGUON")
        except Exception:
            raise LoiNghiepVu("ENGINE_LOI_XU_LY", "Engine gặp lỗi khi xử lý việc này.") from None

    for nang_luc in ung_dung.phieu["nang_luc"]:
        if nang_luc["ma"] not in {"tra_cuu.nhan_yeu_cau@1", "tra_cuu.cat_doan@1", "tra_cuu.chuan_bi_ai@1",
                                 "tra_cuu.phan_loai_tai_lieu@1", "tra_cuu.phan_tich_cau_hoi@1",
                                 "tra_cuu.xep_hang_lai@1", "tra_cuu.soan_tra_loi@1", "tra_cuu.xuat_ket_qua@1"}:
            ung_dung.nang_luc(nang_luc["ma"])(chua_lam)


dang_ky_nang_luc(app)


if __name__ == "__main__":
    app.chay()
