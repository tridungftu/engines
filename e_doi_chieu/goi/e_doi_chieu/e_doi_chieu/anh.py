"""Ảnh một trang trong RAM; phép đổi tọa độ chỉ từ metadata Core cấp."""
from dataclasses import dataclass
import io
import math
import warnings

from kho_tri_thuc_sdk.engine import LoiNghiepVu
from .vi_tri import _hop


def loi_anh(ma="DC_THIEU_ANH"):
    cau = {
        "DC_THIEU_ANH": "Chưa đủ ảnh trang hợp lệ và hệ tọa độ được Core cấp. Anh kiểm tra lại nguồn ảnh.",
        "DC_CHUA_CO_BO_PHAT_HIEN": "Chưa có bộ phát hiện sửa tay và dữ liệu hỗ trợ đã đo phù hợp. Hồ sơ vẫn cần kiểm tra.",
        "DC_QUA_GIOI_HAN": "Hồ sơ vượt giới hạn đối chiếu của lượt này.",
    }
    raise LoiNghiepVu(ma, cau[ma])


def _pillow():
    try:
        import PIL
        from PIL import Image
    except ImportError:
        loi_anh("DC_CHUA_CO_BO_PHAT_HIEN")
    if PIL.__version__ != "12.3.0":
        loi_anh("DC_CHUA_CO_BO_PHAT_HIEN")
    return Image


def doc_anh(raw, mime, pixel_toi_da, kiem_huy):
    """Kiểm header trước giải mã, rồi verify/load thực; không mở tên tệp."""
    Image = _pillow()
    kiem_huy()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(raw)) as im:
                if im.width * im.height > min(pixel_toi_da, 20000000):
                    loi_anh("DC_QUA_GIOI_HAN")
                if (im.format != {"image/png": "PNG", "image/jpeg": "JPEG"}.get(mime) or
                        im.mode not in ("1", "L", "RGB", "RGBA", "LA", "P")):
                    loi_anh()
                im.verify()
            kiem_huy()
            with Image.open(io.BytesIO(raw)) as im:
                if getattr(im, "n_frames", 1) != 1 or im.getexif().get(274, 1) != 1:
                    loi_anh()
                im.load()
                # Alpha luôn ghép nền trắng, tránh biến vùng trong suốt thành nét đen.
                rgba = im.convert("RGBA")
                try:
                    nen = Image.new("RGB", im.size, "white")
                    try:
                        with rgba.getchannel("A") as alpha:
                            nen.paste(rgba, mask=alpha)
                    except BaseException:
                        nen.close()
                        raise
                finally:
                    rgba.close()
                try:
                    kiem_huy()
                except BaseException:
                    nen.close()
                    raise
                return nen
    except (Image.DecompressionBombError, Image.DecompressionBombWarning):
        loi_anh("DC_QUA_GIOI_HAN")
    except (OSError, ValueError, SyntaxError, EOFError):
        loi_anh()


@dataclass(frozen=True)
class HeToaDo:
    rong: float
    cao: float
    don_vi: str
    ti_le: float
    xoay: int
    rong_px: int
    cao_px: int

    @classmethod
    def tu_core(cls, page, meta, kich_thuoc):
        if type(meta) is not dict:
            loi_anh()
        nums = [page.get("rong"), page.get("cao"), meta.get("ti_le")]
        if any(type(x) not in (int, float) or not math.isfinite(x) or x <= 0 for x in nums):
            loi_anh()
        if (page.get("don_vi") not in ("px", "pt") or meta.get("he_toa_do") != "goc_tren_trai" or
                type(meta.get("xoay")) is not int or meta["xoay"] not in (0, 90, 180, 270) or
                any(type(meta.get(k)) is not int or meta[k] <= 0 for k in ("rong_px", "cao_px")) or
                (meta["rong_px"], meta["cao_px"]) != kich_thuoc or
                meta.get("rong_nguon") != page["rong"] or meta.get("cao_nguon") != page["cao"] or
                meta.get("don_vi") != page["don_vi"]):
            loi_anh()
        w, h = page["rong"] * meta["ti_le"], page["cao"] * meta["ti_le"]
        if meta["xoay"] in (90, 270):
            w, h = h, w
        if abs(w - kich_thuoc[0]) > 0.51 or abs(h - kich_thuoc[1]) > 0.51:
            loi_anh()
        return cls(page["rong"], page["cao"], page["don_vi"], meta["ti_le"], meta["xoay"], *kich_thuoc)

    def hop_thang(self, hop):
        _hop(hop, {"rong": self.rong, "cao": self.cao})
        w, h = self._kich_thuoc_thang()
        return [hop[0]*w/self.rong, hop[1]*h/self.cao, hop[2]*w/self.rong, hop[3]*h/self.cao]

    def _kich_thuoc_thang(self):
        return (self.cao_px, self.rong_px) if self.xoay in (90, 270) else (self.rong_px, self.cao_px)

    def hop_anh(self, hop):
        x0, y0, x1, y1 = hop
        w, h = self._kich_thuoc_thang()
        return {0: [x0, y0, x1, y1], 90: [h-y1, x0, h-y0, x1],
                180: [w-x1, h-y1, w-x0, h-y0], 270: [y0, w-x1, y1, w-x0]}[self.xoay]

    def hop_nguon(self, hop_thang):
        w, h = self._kich_thuoc_thang()
        hop = [hop_thang[0]*self.rong/w, hop_thang[1]*self.cao/h,
               hop_thang[2]*self.rong/w, hop_thang[3]*self.cao/h]
        _hop(hop, {"rong": self.rong, "cao": self.cao})
        return hop


def cat_png(im, hop_px, kiem_huy):
    """Hộp nửa mở, làm tròn ra ngoài; trả cả hộp pixel thực đã cắt."""
    _hop(hop_px, {"rong": im.width, "cao": im.height})
    box = [math.floor(hop_px[0]), math.floor(hop_px[1]), math.ceil(hop_px[2]), math.ceil(hop_px[3])]
    kiem_huy()
    with im.crop(tuple(box)) as cut, io.BytesIO() as out:
        cut.save(out, format="PNG")
        raw = out.getvalue()
    kiem_huy()
    return raw, box
