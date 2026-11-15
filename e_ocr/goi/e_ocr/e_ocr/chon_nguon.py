"""Chuyển OCR-CHON từ ma-nguon/chon_nguon.py sang SDK 2.0.

Giữ thứ tự ABBYY trước, bằng chứng chưa nhận và lý do chuyển; bỏ toàn bộ
cổng/SDK riêng cũ. Sổ và nhật ký lượt chỉ chứa mã, băm và số đếm.
"""

from dataclasses import dataclass
from hashlib import sha256
from datetime import date, datetime, timezone
import time
from uuid import uuid4

from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, NganXungDot

from .abbyy import BackendABBYY, LoiABBYYChuaNhan, LoiABBYYTuChoi
from .luot_abbyy import DA_CHOT, DANG_DO, NhatKyLuot, tim_luot, doc_map, ghi_map, doc_so_nguyen
from .lop_chu import KetQuaLopChu, LoiLopChu, doc_lop_chu
from .nhat_ky import cho_nguon, ghi_nguon, het_cho
from . import tesseract


LY_DO = {
    "het_han_muc": "Không đủ hạn mức ABBYY trong cửa sổ 30 ngày gần nhất.",
    "khong_ket_noi": "Nguồn ABBYY đang tắt hoặc không truy cập được.",
    "qua_thoi_gian": "ABBYY quá thời hạn trước khi nhận; đã rút tệp đang chờ.",
    "loi_nhan_dang": "ABBYY báo lỗi với căn cứ cho phép chuyển nguồn.",
}
KHOA_HAN_MUC = "han_muc_abbyy"
CUA_SO_GIAY = 30 * 86400


class SoHanMuc:
    """Cửa sổ trượt đúng 30*86400 giây, không đặt lại đầu tháng.

    Nhóm theo ngày UTC và giây trong ngày để sổ 5.000 lượt nhỏ hơn 64 KiB.
    dang_giu chỉ chặn cạnh tranh; da_nhan mới là trang đã dùng. Không tự
    hết hạn chỗ giữ còn dở: OCR-4 sẽ đối chiếu sau gián đoạn tiến trình.
    """

    def __init__(self, ngan, *, dong_ho=None):
        self.ngan = ngan
        self.dong_ho = dong_ho or time.time

    def _doc(self):
        # Đọc mốc CAS TRƯỚC các hàng; mọi thay đổi sổ đều tăng mốc này.
        # Nhờ vậy cả hai việc nằm hai bên nửa đêm cũng không giữ vượt trần.
        moc = self.ngan.doc("trang_thai_engine", {"ma": "han_muc"})
        hang, tiep = {}, None
        while True:
            trang = self.ngan.tim("han_muc_ngay", loc={}, gioi_han=500, tiep=tiep)
            for b in trang.danh_sach:
                hang[b.gia_tri["ngay"]] = b
            tiep = trang.tiep
            if tiep is None:
                break
        try:
            so = {"da_nhan": {}, "dang_giu": {} if moc is None else doc_map(moc.gia_tri["dang_giu"])}
            for ngay, b in hang.items():
                so["da_nhan"][ngay] = doc_map(b.gia_tri["da_nhan"])
        except (ValueError, TypeError, KeyError, RecursionError):
            raise LoiNghiepVu("SO_HAN_MUC_CAN_KIEM_TRA", "Sổ hạn mức ABBYY cần được đối chiếu lại.") from None
        return (moc, hang), self._doc_so(so)

    def _ghi(self, lo, anh, so):
        moc, hang = anh
        # Chỉ sửa các ngày còn trong cửa sổ hoặc vừa được hoàn trang.
        # Dòng lịch sử do Core ẩn sau 45 ngày; không ghi lại để kéo dài TTL.
        cac_ngay = set(so["da_nhan"])
        moc_giay = int(self.dong_ho()) - CUA_SO_GIAY
        for ngay in hang:
            dau = int(datetime.fromisoformat(ngay).replace(tzinfo=timezone.utc).timestamp())
            if dau + 86400 > moc_giay:
                cac_ngay.add(ngay)
        for ngay in sorted(cac_ngay):
            gia_tri = {"ngay": ngay, "da_nhan": ghi_map(so["da_nhan"].get(ngay, {}))}
            cu = hang.get(ngay)
            if cu is not None:
                if gia_tri["da_nhan"] == cu.gia_tri["da_nhan"]:
                    continue
            if cu is None:
                lo.them("han_muc_ngay", gia_tri)
            else:
                lo.sua("han_muc_ngay", {"ngay": ngay}, gia_tri, row_version=cu.row_version)
        # Chỗ giữ không hết hạn, kể cả ngừng engine lâu hơn 45 ngày.
        gia_tri = {"dang_giu": ghi_map(so["dang_giu"])}
        if moc is None:
            lo.them("trang_thai_engine", {"ma": "han_muc", "lan": 1, **gia_tri})
        else:
            gia_tri["lan"] = doc_so_nguyen(moc.gia_tri["lan"]) + 1
            lo.sua("trang_thai_engine", {"ma": "han_muc"}, gia_tri,
                   row_version=moc.row_version)

    def _cap_nhat(self, sua):
        for _ in range(12):
            anh, so = self._doc()
            so = sua(so)
            try:
                with self.ngan.lo() as lo:
                    self._ghi(lo, anh, so)
                return
            except NganXungDot:
                continue
        raise LoiNghiepVu("NGAN_XUNG_DOT", "Hạn mức vừa thay đổi. Hãy thử lại.", thu_lai_duoc=True)

    def _doc_so(self, cu):
        if cu is None:
            return {"da_nhan": {}, "dang_giu": {}}
        try:
            if type(cu) is not dict or set(cu) != {"da_nhan", "dang_giu"}:
                raise ValueError
            if any(type(cu[k]) is not dict for k in cu):
                raise ValueError
            moc = int(self.dong_ho()) - CUA_SO_GIAY
            moi = {"da_nhan": {}, "dang_giu": dict(cu["dang_giu"])}
            for ngay, giay in cu["da_nhan"].items():
                if date.fromisoformat(ngay).isoformat() != ngay or type(giay) is not dict:
                    raise ValueError
                dau_ngay = int(datetime.fromisoformat(ngay).replace(tzinfo=timezone.utc).timestamp())
                for luc, so in giay.items():
                    if (not luc.isdigit() or str(int(luc)) != luc or not 0 <= int(luc) < 86400
                            or type(so) is not int or not 1 <= so <= 5000):
                        raise ValueError
                    if dau_ngay + int(luc) > moc:
                        moi["da_nhan"].setdefault(ngay, {})[luc] = so
            if any(type(so) is not int or not 1 <= so <= 60 for so in moi["dang_giu"].values()):
                raise ValueError
            return moi
        except (ValueError, TypeError, AttributeError, OverflowError):
            raise LoiNghiepVu(
                "SO_HAN_MUC_CAN_KIEM_TRA", "Sổ hạn mức ABBYY không hợp lệ. Hãy liên hệ quản trị viên."
            ) from None

    @staticmethod
    def _tong(so):
        return sum(sum(giay.values()) for giay in so["da_nhan"].values())

    def da_dung(self):
        return self._tong(self._doc()[1])

    def giu(self, so_trang, han_muc):
        if type(so_trang) is not int or not 1 <= so_trang <= 60 or type(han_muc) is not int or not 0 <= han_muc <= 5000:
            raise LoiNghiepVu("SO_HAN_MUC_CAN_KIEM_TRA", "Số trang hoặc hạn mức ABBYY không hợp lệ.")
        ma = uuid4().hex

        def sua(cu):
            so = self._doc_so(cu)
            if self._tong(so) + sum(so["dang_giu"].values()) + so_trang > han_muc:
                raise LoiABBYYChuaNhan("ABBYY_HET_HAN_MUC", LY_DO["het_han_muc"])
            so["dang_giu"][ma] = so_trang
            return so

        self._cap_nhat(sua)
        return ma

    def ghi_nhan(self, ma):
        def sua(cu):
            so = self._doc_so(cu)
            if ma not in so["dang_giu"]:
                raise LoiNghiepVu("SO_HAN_MUC_CAN_KIEM_TRA", "Chưa xác nhận được hạn mức của lượt ABBYY.")
            so_trang = so["dang_giu"].pop(ma)
            luc = int(self.dong_ho())
            ngay = datetime.fromtimestamp(luc, timezone.utc).date().isoformat()
            giay = so["da_nhan"].setdefault(ngay, {})
            khoa = str(luc % 86400)
            giay[khoa] = giay.get(khoa, 0) + so_trang
            return so

        self._cap_nhat(sua)

    def bo_giu(self, ma):
        def sua(cu):
            so = self._doc_so(cu)
            so["dang_giu"].pop(ma, None)
            return so

        self._cap_nhat(sua)


@dataclass
class KetQuaChonNguon:
    ket_qua: KetQuaLopChu
    nguon_doc: str
    ly_do_chuyen_nguon: str | None = None


def doc_theo_nguon(raw, mime, so_trang, *, viec, cau_hinh, ngan):
    nguon = viec.tham_so.get("nguon", "tu_dong")
    bam = "sha256:" + sha256(raw).hexdigest()
    # Lựa chọn nguồn mới không được bỏ qua lượt ABBYY còn dở. Khi không
    # có lượt dở, chi_tesseract vẫn bỏ backend và sổ hạn mức ABBYY.
    cu = None
    if nguon == "chi_tesseract":
        ban_ghi = tim_luot(ngan, viec.ngu_canh.get("phap_nhan_id"), bam)
        cu = None if ban_ghi is None else ban_ghi.gia_tri
    if nguon == "chi_tesseract" and (cu is None or (
            type(cu) is dict and isinstance(cu.get("trang_thai"), str) and cu["trang_thai"] in DA_CHOT)):
        ghi_nguon("tesseract")
        return KetQuaChonNguon(
            tesseract.doc_tesseract(raw, mime, cau_hinh.get("tesseract", {}), viec=viec), "tesseract"
        )
    so = SoHanMuc(ngan)
    nhat_ky = NhatKyLuot(so, viec.ngu_canh.get("phap_nhan_id"), bam, so_trang)
    luot = nhat_ky.doc()
    doc_lai = luot is not None and luot["trang_thai"] in DANG_DO
    da_nhan = False

    def khi_da_nhan():
        nonlocal da_nhan
        da_nhan = True
        nhat_ky.cap_nhat(nhan=True)

    def doc_ket_qua(pdf):
        het_cho()
        viec.tien_do(75, "Đã nhận kết quả ABBYY; đang đọc lớp chữ.")
        try:
            ket_qua = doc_lop_chu(pdf, kiem_huy=viec.kiem_huy)
        except LoiLopChu:
            raise LoiNghiepVu(
                "ABBYY_THIEU_LOP_CHU", "Kết quả ABBYY chưa có lớp chữ đầy đủ. Hãy kiểm tra cấu hình xuất PDF."
            ) from None
        if len(ket_qua.pages) != so_trang:
            raise LoiNghiepVu(
                "KET_QUA_KHONG_KHOP", "Số trang kết quả ABBYY không khớp tài liệu gốc. Hãy kiểm tra lại nguồn nhận dạng."
            )
        return KetQuaChonNguon(ket_qua, "abbyy")

    try:
        viec.kiem_huy()
        abbyy = cau_hinh.get("abbyy", {"bat": False})
        if (nguon == "chi_abbyy" and not doc_lai
                and (not abbyy.get("thu_muc_vao") or not abbyy.get("thu_muc_ra"))):
            raise LoiNghiepVu("CHUA_CAU_HINH", "Engine chưa được cấu hình. Admin vào Quản lý engine › OCR › Cấu hình.")
        backend = BackendABBYY(abbyy, chi_doc=doc_lai)
        if not doc_lai:
            luot, moi = nhat_ky.giu(abbyy["han_muc_trang_30_ngay"])
            doc_lai = not moi
        ghi_nguon("abbyy")
        with nhat_ky.xu_ly(viec) as viec_nguon, cho_nguon():
            return backend.doc_pdf(
                raw, {"application/pdf": "pdf", "image/png": "png", "image/jpeg": "jpg"}[mime],
                viec=viec_nguon, khi_da_nhan=khi_da_nhan,
                khi_chua_ro=lambda: nhat_ky.cap_nhat("chua_ro"),
                ma_tuong_quan=nhat_ky.ma, doc_lai=doc_lai,
                xu_ly_ket_qua=doc_ket_qua, khi_ket_thuc=nhat_ky.cap_nhat,
            )
    except LoiABBYYTuChoi:
        if nguon == "chi_abbyy":
            raise
        ly_do = "loi_nhan_dang"
    except LoiABBYYChuaNhan as loi:
        if doc_lai:
            # Nguồn hiện tắt/đổi quyền không phủ định lượt đã gửi trước đó.
            raise ChuaRo(nhat_ky.ma) from None
        if da_nhan or nguon == "chi_abbyy":
            raise
        ly_do = {
            "ABBYY_HET_HAN_MUC": "het_han_muc", "ABBYY_DANG_TAT": "khong_ket_noi",
            "ABBYY_CHUA_CAU_HINH": "khong_ket_noi", "ABBYY_QUA_THOI_HAN": "qua_thoi_gian",
            "ABBYY_KHONG_TRUY_CAP_DUOC": "loi_nhan_dang",
        }.get(loi.ma, "loi_nhan_dang")
    viec.kiem_huy()
    viec.tien_do(55, "Đang chuyển sang nguồn Tesseract.")
    ghi_nguon("tesseract")
    return KetQuaChonNguon(
        tesseract.doc_tesseract(raw, mime, cau_hinh.get("tesseract", {}), viec=viec),
        "tesseract", LY_DO[ly_do],
    )
