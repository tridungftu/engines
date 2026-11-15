"""DC-9: PDF ảnh tiếng Việt, phân trang theo kích thước thật; chỉ dùng RAM."""
from hashlib import sha256
import io
import json
from pathlib import Path
import struct
import unicodedata

from . import ho_so as hs
from .anh import doc_anh, HeToaDo, cat_png
from .tong_hop import loi, TRUONG_DEM

BAM_FONT = "319cff6e7a31f0f2a41c475dca42890aa5d19fe16017e2290f8c1d4e14f76481"
FONT = Path(__file__).resolve().parent.parent / "tai_nguyen/font/Roboto-Regular.ttf"
NHAN = {"khop": "Khớp", "khop_co_thay_doi_hinh_thuc": "Khớp - có thay đổi hình thức",
        "can_xem": "Cần xem", "lech_nghiem_trong": "Lệch nghiêm trọng", "chua_doi_chieu_duoc": "Chưa đối chiếu được",
        "nghiem_trong": "Nghiêm trọng", "hinh_thuc": "Thay đổi hình thức", "nhieu_ocr": "Nhiễu OCR"}
NHAN_DEM = dict(zip(TRUONG_DEM, ("Nghiêm trọng", "Cần xem", "Hình thức", "Nhiễu OCR", "Vùng sửa tay", "Trang OCR kém")))
NHAN_KIEM = {"doc_hai_ban": "Đọc hai bản", "so_van_ban": "So văn bản", "quy_tac_cung": "Quy tắc cứng",
    "trang": "Trang", "lech_dau": "Lệch dấu", "sua_tay": "Sửa tay", "phan_loai_ai": "Phân loại Local AI",
    "nguon_trang_ocr": "Đủ nguồn các trang OCR", "do_chat_luong_sua_tay": "Chất lượng phát hiện sửa tay",
    "do_chat_luong_ocr": "Chất lượng OCR từng trang", "kiem_trang_vat_ly": "Trang vật lý",
    "quy_tac_vung_bao_ve": "Vùng bảo vệ", "quy_tac_so_va_ngay": "Số và ngày", "quy_tac_tien_bang_chu": "Tiền bằng chữ"}


def _font():
    """Không tìm font hệ điều hành; kiểm băm và cmap trước khi dựng trang."""
    try:
        from PIL import ImageFont
        raw = FONT.read_bytes()
        if sha256(raw).hexdigest() != BAM_FONT:
            loi("DC_THIEU_TAI_NGUYEN")
        n = struct.unpack_from(">H", raw, 4)[0]
        tables = {raw[12+i*16:16+i*16]: struct.unpack_from(">II", raw, 20+i*16) for i in range(n)}
        offset, size = tables[b"cmap"]
        cmap = raw[offset:offset+size]
        n = struct.unpack_from(">H", cmap, 2)[0]
        chars = set()
        for i in range(n):
            platform, encoding, off = struct.unpack_from(">HHI", cmap, 4+i*8)
            if platform not in (0, 3) or platform == 3 and encoding not in (1, 10):
                continue
            fmt = struct.unpack_from(">H", cmap, off)[0]
            if fmt != 4:
                continue
            length, _, seg2 = struct.unpack_from(">HHH", cmap, off+2)
            sub, seg = cmap[off:off+length], seg2//2
            ends = struct.unpack_from(">"+"H"*seg, sub, 14)
            starts = struct.unpack_from(">"+"H"*seg, sub, 16+seg*2)
            deltas = struct.unpack_from(">"+"h"*seg, sub, 16+seg*4)
            ranges = struct.unpack_from(">"+"H"*seg, sub, 16+seg*6)
            for j, (a, b) in enumerate(zip(starts, ends)):
                for cp in range(a, min(b, 65534)+1):
                    glyph = (cp+deltas[j]) & 65535
                    if ranges[j]:
                        pos = 16+seg*6+j*2+ranges[j]+(cp-a)*2
                        glyph = struct.unpack_from(">H", sub, pos)[0]
                        if glyph:
                            glyph = (glyph+deltas[j]) & 65535
                    if glyph:
                        chars.add(cp)
        if not chars:
            loi("DC_THIEU_TAI_NGUYEN")
        return ImageFont.truetype(io.BytesIO(raw), size=25), chars
    except (OSError, ValueError, KeyError, struct.error, ImportError):
        loi("DC_THIEU_TAI_NGUYEN")


class _PDF:
    """Mỗi lần chỉ giữ một trang raster và JPEG của nó, không giữ mọi bitmap.

    Pillow dựng trang/nén JPEG; writer PDF 1.4 tối thiểu dùng xref byte thật.
    Trần bytes/trang từ chối toàn báo cáo, tuyệt đối không cắt phần còn lại.
    """
    W, H, LE, DAY, DONG = 1240, 1754, 80, 1640, 37

    def __init__(self, kiem, toi_da):
        import PIL
        from PIL import Image, ImageDraw
        if PIL.__version__ != "12.3.0":
            loi("DC_THIEU_TAI_NGUYEN")
        self.Image, self.ImageDraw = Image, ImageDraw
        self.font, self.chars = _font()
        self.kiem, self.toi_da = kiem, toi_da
        self.out = io.BytesIO(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        self.out.seek(0, 2)
        self.offsets, self.pages = {}, []
        self.im = None
        self._moi()

    def _obj(self, no, raw):
        self.kiem()
        if self.out.tell()+len(raw) > self.toi_da:
            hs.loi("DC_QUA_GIOI_HAN")
        self.offsets[no] = self.out.tell()
        self.out.write(f"{no} 0 obj\n".encode()+raw+b"\nendobj\n")

    def _moi(self):
        self.im = self.Image.new("RGB", (self.W, self.H), "white")
        self.draw = self.ImageDraw.Draw(self.im)
        self.y = self.LE
        self.draw.line((self.LE, 58, self.W-self.LE, 58), fill="#254b63", width=4)

    def _dong_trang(self):
        self.kiem()
        if len(self.pages) >= 2000:
            hs.loi("DC_QUA_GIOI_HAN")
        no = 3 + len(self.pages)*3
        self.draw.text((self.LE, self.H-65), f"Đối chiếu bản ký | Trang {len(self.pages)+1}", font=self.font, fill="#555555")
        with io.BytesIO() as jpg:
            self.im.save(jpg, format="JPEG", quality=95, subsampling=0)
            data = jpg.getvalue()
        self._obj(no, (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.2 841.92] "
            f"/Resources << /XObject << /I {no+1} 0 R >> >> /Contents {no+2} 0 R >>").encode())
        self._obj(no+1, (f"<< /Type /XObject /Subtype /Image /Width {self.W} /Height {self.H} "
            f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length {len(data)} >>\nstream\n").encode()+data+b"\nendstream")
        cmd = b"q 595.2 0 0 841.92 0 0 cm /I Do Q\n"
        self._obj(no+2, f"<< /Length {len(cmd)} >>\nstream\n".encode()+cmd+b"endstream")
        self.pages.append(no)
        self.im.close()
        self.im = None

    def _cho(self, h):
        if self.y+h > self.DAY:
            self._dong_trang()
            self._moi()

    def _ve_dong(self, text, mau):
        self.kiem()
        self._cho(self.DONG)
        self.draw.text((self.LE, self.y), text, font=self.font, fill=mau, anchor="lt")
        self.y += self.DONG

    def chu(self, text, mau="#182d3a"):
        # NFC cho dấu tổ hợp; ký tự không có glyph được ghi U+... thay ô vuông.
        # Nguyên văn bytes/Unicode đầy đủ luôn giữ trong JSON.
        text = unicodedata.normalize("NFC", str(text)).replace("\t", "    ")
        text = "".join(c if c == "\n" or ord(c) in self.chars else f"[U+{ord(c):04X}]" for c in text)
        width = self.W - 2*self.LE
        for para in text.split("\n"):
            if not para:
                self._ve_dong("", mau)
            start = 0
            while start < len(para):
                self.kiem()
                # Đo một cửa sổ nhỏ; không đo lại cả đoạn nửa triệu ký tự
                # cho từng dòng hoặc nhờ Pillow cấp bitmap chuỗi rất dài.
                lo, hi = 1, min(512, len(para)-start)
                while lo < hi:
                    mid = (lo+hi+1)//2
                    if self.draw.textbbox((0, 0), para[start:start+mid], font=self.font)[2] <= width:
                        lo = mid
                    else:
                        hi = mid-1
                end = start+lo
                if end < len(para):
                    space = para.rfind(" ", start, end)
                    if space > start:
                        end = space+1
                self._ve_dong(para[start:end], mau)
                start = end

    def anh(self, raw, mime, pixels):
        with doc_anh(raw, mime, pixels, self.kiem) as im:
            scale = min((self.W-2*self.LE)/im.width, (self.DAY-self.LE-20)/im.height, 2)
            w, h = max(1, int(im.width*scale)), max(1, int(im.height*scale))
            self._cho(h+20)
            with im.resize((w, h), self.Image.Resampling.LANCZOS) as small:
                self.im.paste(small, (self.LE, self.y))
            self.y += h+20

    def xong(self, tom_tat):
        self._dong_trang()
        self._obj(1, b"<< /Type /Catalog /Pages 2 0 R >>")
        kids = " ".join(f"{n} 0 R" for n in self.pages)
        self._obj(2, f"<< /Type /Pages /Kids [{kids}] /Count {len(self.pages)} >>".encode())
        no = 3+len(self.pages)*3
        subject = (b"\xfe\xff"+json.dumps(tom_tat, ensure_ascii=False, sort_keys=True).encode("utf-16-be")).hex()
        self._obj(no, f"<< /Title (Doi chieu ban ky) /Subject <{subject}> >>".encode())
        xref = self.out.tell()
        self.out.write(f"xref\n0 {no+1}\n0000000000 65535 f \n".encode())
        for i in range(1, no+1):
            self.out.write(f"{self.offsets[i]:010d} 00000 n \n".encode())
        self.out.write(f"trailer\n<< /Size {no+1} /Root 1 0 R /Info {no} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
        if self.out.tell() > self.toi_da:
            hs.loi("DC_QUA_GIOI_HAN")
        return self.out.getvalue()

    def close(self):
        if self.im is not None:
            self.im.close()
        self.out.close()


def _chi_tiet(p, title, value):
    p.chu(title, "#254b63")
    p.chu(json.dumps(value, ensure_ascii=False, sort_keys=True) if not isinstance(value, str) else value)


def _anh_diem(p, d, s, doc):
    ld = next((r for r in (s.get("lech_dau") or {}).get("ket_qua", [])
               if r["ma_diem"] == d["ma_diem"]), None)
    if ld and ld.get("anh_cat"):
        ref = ld["anh_cat"]
        raw = doc.doc(ref, doc.cau_hinh["tep_mib"] * hs.MIB)
        p.chu("Ảnh cắt OCR lại đã ghim đúng điểm/vùng")
        p.anh(raw, ref["tep"]["mime"], doc.cau_hinh["pixel_anh"])
        return
    v = d.get("ban_ky")
    pos = (v or {}).get("vi_tri")
    if type(pos) is dict:
        pos = [pos]
    positions = pos if type(pos) is list else []
    found = False
    for at in positions:
        if at.get("hop") is None or at.get("so_trang") is None:
            continue
        no = at["so_trang"]
        page = next((x for x in s["van_ban"]["ban_ky"]["van_ban_tai_lieu"]["trang"] if x["so"] == no), None)
        ref = next((x for x in s["anh_trang"] if x["so"] == no), None)
        meta = next((x.get("he_toa_do") for x in (s.get("quet_anh") or {}).get("trang", []) if x["so_trang"] == no), None)
        if not page or not ref or not meta:
            continue
        raw = doc.doc(ref, doc.cau_hinh["tep_mib"] * hs.MIB)
        with doc_anh(raw, ref["tep"]["mime"], doc.cau_hinh["pixel_anh"], p.kiem) as im:
            he = HeToaDo.tu_core(page, meta, im.size)
            cut, _ = cat_png(im, he.hop_anh(at["hop"]), p.kiem)
        p.chu(f"Ảnh cắt bản ký - trang {no}")
        p.anh(cut, "image/png", doc.cau_hinh["pixel_anh"])
        found = True
    if not found:
        p.chu("Chưa đủ tọa độ/hệ quy chiếu tin cậy để cắt ảnh điểm này; xem vị trí nguồn và phần chưa kiểm.")


def dung_pdf(s, doc, kiem):
    p = None
    try:
        p = _PDF(kiem, min(doc.cau_hinh["tep_mib"]*hs.MIB, doc.cau_hinh["tong_byte_tep_con"]))
        p.chu("BÁO CÁO ĐỐI CHIẾU BẢN KÝ", "#254b63")
        p.chu("Kết luận: " + NHAN[s["ket_luan"]])
        p.chu("Đã kiểm đủ: " + ("Có" if s["da_kiem_du"] else "Chưa"))
        p.chu("Đề nghị chặn: " + ("Có" if s["de_nghi_chan"] else "Không"))
        for k in TRUONG_DEM:
            value = s["tom_tat"][k]
            p.chu(NHAN_DEM[k]+": "+("Chưa đo đủ" if value is None else str(value)))
        thieu = s["tong_hop"]["phan_chua_kiem"]
        p.chu("Phần chưa kiểm: " + ("; ".join(NHAN_KIEM[k] for k in thieu) if thieu else "Không còn"))
        p.chu(s["tong_hop"]["xac_nhan"])
        p.chu(s["tong_hop"]["hieu_luc"])
        p.chu("Số đếm phản ánh điểm đã biết; báo cáo dở giữ mọi điểm Nghiêm trọng đã phát hiện.")
        _chi_tiet(p, "Nguồn và phiên bản đã ghim", s["nguon"])
        for warning in s["canh_bao"]:
            p.chu("Lưu ý: " + warning)
        for nhieu in (False, True):
            p.chu("PHỤ LỤC - TOÀN BỘ NHIỄU OCR" if nhieu else "CHI TIẾT ĐIỂM LỆCH", "#254b63")
            for d in s["diem_lech"]:
                kiem()
                if (d["muc"] == "nhieu_ocr") != nhieu:
                    continue
                p.chu("Điểm " + d["ma_diem"], "#254b63")
                p.chu("Mức: "+NHAN[d["muc"]]+" | Sàn: "+NHAN[d["muc_san"]])
                _chi_tiet(p, "Lý do / quy tắc / bằng chứng", {k: d[k] for k in
                    ("ly_do_ai", "can_cu", "can_cu_quy_tac", "quy_tac_trung", "lech_dau") if k in d})
                for ten, rows in (("Bằng chứng lệch dấu", (s.get("lech_dau") or {}).get("ket_qua", [])),
                                  ("Hậu kiểm Local AI", (s.get("ai") or {}).get("ket_qua", []))):
                    for row in rows:
                        if row["ma_diem"] == d["ma_diem"]:
                            _chi_tiet(p, ten, row)
                for ben, nhan in (("word", "BẢN WORD"), ("ban_ky", "BẢN KÝ - CHỮ OCR")):
                    v = d[ben]
                    p.chu(nhan, "#254b63")
                    p.chu(v["nguyen_van"] if v is not None else "Không có đoạn tương ứng ở phía này.")
                    if v is not None:
                        _chi_tiet(p, "Vị trí nguồn (không suy đoán trang Word)", {k: val for k, val in v.items() if k != "nguyen_van"})
                _anh_diem(p, d, s, doc)
        p.chu("VÙNG SỬA TAY / NGHI SỬA TAY", "#254b63")
        for v in s.get("vung_sua_tay") or []:
            kiem()
            _chi_tiet(p, "Vùng " + v["ma"], {k: val for k, val in v.items() if k not in ("anh_cat",)})
            raw = doc.doc({"tep": v["anh_cat"], "bam": v["bam_anh_cat"]}, doc.cau_hinh["tep_mib"] * hs.MIB)
            p.anh(raw, v["anh_cat"]["mime"], doc.cau_hinh["pixel_anh"])
        p.chu("TRANG OCR KÉM", "#254b63")
        for row in s.get("trang_ocr_kem") or []:
            _chi_tiet(p, "Trang OCR kém", row)
        return p.xong({"ket_luan": s["ket_luan"], "da_kiem_du": s["da_kiem_du"],
                       "de_nghi_chan": s["de_nghi_chan"], **s["tom_tat"]})
    finally:
        if p is not None:
            p.close()
