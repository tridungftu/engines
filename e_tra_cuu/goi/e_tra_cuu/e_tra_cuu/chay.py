"""Điểm vào SDK 2.0; cấu hình và dữ liệu chỉ qua ngăn."""

import json
from pathlib import Path

from kho_tri_thuc_sdk.engine import ChuaRo, Engine, LoiDuongTruyen, LoiNghiepVu, ViecDaHuy

from .cau_hinh import CauHinhKhongHopLe, doc_cau_hinh
from .ngan import NganBoNho, NganKhongHopLe, NganXungDot, chon_ngan
from .ho_so import nhan_yeu_cau
from .cat_doan import cat_doan
from .chuan_bi_ai import chuan_bi_ai, doc_snapshot_ai
from .cau_hoi import phan_tich_cau_hoi
from .xep_hang import xep_hang_lai
from .phan_loai import phan_loai_tai_lieu
from .tra_loi import soan_tra_loi
from .bang_chung import chuan_bi_tang_mot
from .kiem_dau_vao import doi_tuong, loi


_GOI = Path(__file__).resolve().parent.parent
# Chỉ đọc metadata/schema đóng gói, không đọc giá trị cấu hình trên đĩa.
KHAI_BAO = json.loads((_GOI / "KHAI-SDK-2.1.json").read_text(encoding="utf-8"))
SCHEMA = json.loads((_GOI / "cau_hinh.schema.json").read_text(encoding="utf-8"))


def khoi_tao_ngan(ung_dung):
    """Gắn đúng một ngăn RAM khi SDK chưa cấp ngăn."""
    if getattr(ung_dung, "ngan", None) is None:
        ung_dung.ngan = NganBoNho(KHAI_BAO["ngan_du_lieu"])
    return chon_ngan(ung_dung)


def chup_cau_hinh(ngan):
    """Ghim giá trị và phiên bản từ MỘT lần đọc; mẫu NGAN-0 giữ nguyên."""
    try:
        ban = ngan.doc("cau_hinh", {})

        class BanDaDoc:
            def doc(self, bang, khoa):
                return ban

        cau_hinh = doc_cau_hinh(BanDaDoc(), SCHEMA)
        if cau_hinh is None:
            raise LoiNghiepVu(
                "CHUA_CAU_HINH",
                "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình.",
            )
        # Các quan hệ không diễn đạt bằng tập từ khóa schema tối thiểu.
        phan_loai = cau_hinh["phan_loai"]
        da_do = phan_loai["trang_thai"] == "da_do"
        if (da_do and not {"nguong", "bam_bo_do"} <= phan_loai.keys()) or (
            not da_do and {"nguong", "bam_bo_do"} & phan_loai.keys()
        ):
            raise CauHinhKhongHopLe()
        if cau_hinh["cat_doan"]["do_dai_muc_tieu"] > cau_hinh["cat_doan"]["ky_tu_don_vi_toi_da"]:
            raise CauHinhKhongHopLe()
        if type(ban.row_version) is not int or ban.row_version < 1:
            raise CauHinhKhongHopLe()
        # Bao gồm kiểm UTF-8; không để dữ liệu cấu hình lọt vào traceback SDK.
        json.dumps(cau_hinh, ensure_ascii=False, allow_nan=False).encode("utf-8")
        return {"gia_tri": cau_hinh, "row_version": ban.row_version}
    except (CauHinhKhongHopLe, NganKhongHopLe, NganXungDot) as exc:
        raise LoiNghiepVu(exc.ma, exc.thong_diep, thu_lai_duoc=exc.thu_lai_duoc) from None
    except (ValueError, TypeError, AttributeError, RecursionError, OverflowError):
        raise LoiNghiepVu("CAU_HINH_KHONG_HOP_LE", CauHinhKhongHopLe.thong_diep) from None


def yeu_cau_cau_hinh(ngan):
    return chup_cau_hinh(ngan)["gia_tri"]


def kiem_cau_hinh_da_chup(cau_hinh):
    """Dùng cùng bộ kiểm với bản đọc ngăn, giữ nguyên mẫu NGAN-0."""
    from types import SimpleNamespace

    doi_tuong(cau_hinh, ("gia_tri", "row_version"), ())

    class NganSnapshot:
        def doc(self, bang, khoa):
            return SimpleNamespace(**cau_hinh)

    try:
        return chup_cau_hinh(NganSnapshot())
    except LoiNghiepVu:
        loi("TC_SAI_NGUON")


app = Engine.tu_khai_bao("engine.json")
ngan = khoi_tao_ngan(app)


def dang_ky_nang_luc(ung_dung):
    """Cửa nguồn là dependency do bên chủ Core gắn, không lấy từ payload.

    SDK 2.0 chưa có cửa này. Chỉ tests gắn adapter C-TC-02/03; runtime
    thiếu cửa phải từ chối, không coi đây là API SDK đã được phát hành.
    """
    @ung_dung.nang_luc("tra_cuu.nhan_yeu_cau@1")
    def nhan(viec):
        try:
            ngan_viec = getattr(viec, "ngan", None)
            if ngan_viec is None:
                ngan_viec = ung_dung.ngan
            cau_hinh = chup_cau_hinh(ngan_viec)
            return nhan_yeu_cau(viec, cau_hinh, getattr(ung_dung, "cua_nguon", None),
                                ung_dung.phien_ban)
        except (LoiNghiepVu, LoiDuongTruyen, ChuaRo, ViecDaHuy):
            raise
        except Exception:
            # SDK 2.0 ghi traceback ngoại lệ bất ngờ. Chặn tại biên handler
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

    for nang_luc in ung_dung.phieu["nang_luc"]:
        if nang_luc["ma"] not in {"tra_cuu.nhan_yeu_cau@1", "tra_cuu.cat_doan@1", "tra_cuu.chuan_bi_ai@1",
                                 "tra_cuu.phan_loai_tai_lieu@1", "tra_cuu.phan_tich_cau_hoi@1",
                                 "tra_cuu.xep_hang_lai@1", "tra_cuu.soan_tra_loi@1"}:
            ung_dung.nang_luc(nang_luc["ma"])(chua_lam)


dang_ky_nang_luc(app)


if __name__ == "__main__":
    app.chay()
