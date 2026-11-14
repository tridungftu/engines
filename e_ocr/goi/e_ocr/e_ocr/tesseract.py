"""Nhánh Tesseract của mask_ocr, chuyển từ MuPDF worker sang CLI cục bộ.

Dùng bộ render PDF đã ghim, không thêm model/thư viện. Mọi tệp trang/TSV
nằm trong thư mục tạm của việc; không in stderr của chương trình ngoài.
"""

import csv
import io
import math
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import time

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .bang import doc_bang_trang
from .lop_chu import MAX_TEXT, KetQuaLopChu, LoiLopChu, _doc_trang
from .vendor.mask_ocr.common import normalize


MAX_PIXEL = 20_000_000
MAX_TSV = 16 * 1024**2
DPI = 150
THOI_HAN_TRANG = 300


def tim_tesseract(cau_hinh):
    """Ưu tiên đường dẫn cấu hình, rồi PATH và vị trí cài mặc định Windows."""
    ten = cau_hinh.get("duong_dan", "")
    if ten:
        tim_duoc = shutil.which(ten)
        if tim_duoc:
            return tim_duoc
    else:
        tim_duoc = shutil.which("tesseract")
        if tim_duoc:
            return tim_duoc
        if os.name == "nt":
            for bien in ("ProgramW6432", "ProgramFiles", "ProgramFiles(x86)"):
                goc = os.environ.get(bien)
                if goc:
                    tep = Path(goc) / "Tesseract-OCR" / "tesseract.exe"
                    if tep.is_file():
                        return str(tep)
    raise LoiNghiepVu(
        "NGUON_DU_PHONG_CHUA_CAI", "Cần dùng Tesseract nhưng chưa cài nguồn dự phòng. Hãy liên hệ quản trị viên."
    )


def _chay(lenh, *, viec, thoi_han, ma_loi, doc_stdout=False):
    viec.kiem_huy()
    try:
        tien_trinh = subprocess.Popen(
            lenh, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE if doc_stdout else subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except OSError:
        raise LoiNghiepVu("NGUON_DU_PHONG_CHUA_CAI", "Không khởi động được Tesseract. Hãy kiểm tra bộ cài nguồn dự phòng.") from None
    try:
        han = time.monotonic() + thoi_han
        while True:
            viec.kiem_huy()
            con_lai = han - time.monotonic()
            if con_lai <= 0:
                raise LoiNghiepVu("TESSERACT_QUA_THOI_HAN", "Tesseract quá thời hạn đọc tài liệu. Hãy chia nhỏ tài liệu.")
            try:
                out, _ = tien_trinh.communicate(timeout=min(0.1, con_lai))
                break
            except subprocess.TimeoutExpired:
                continue
        viec.kiem_huy()
        if tien_trinh.returncode:
            raise LoiNghiepVu(ma_loi, "Tesseract chưa đọc được tài liệu. Hãy kiểm tra bộ ngôn ngữ và tệp gốc.")
        return out or b""
    finally:
        if tien_trinh.poll() is None:
            tien_trinh.kill()
            tien_trinh.wait(timeout=5)
        if tien_trinh.stdout is not None:
            tien_trinh.stdout.close()


def _kiem_bo_doc(cau_hinh, viec):
    exe = tim_tesseract(cau_hinh)
    ngon_ngu = cau_hinh.get("ngon_ngu", "vie+eng")
    if ngon_ngu not in ("vie", "eng", "vie+eng", "eng+vie"):
        raise LoiNghiepVu("CAU_HINH_KHONG_HOP_LE", "Ngôn ngữ Tesseract phải là vie, eng hoặc vie+eng.")
    out = _chay([exe, "--list-langs"], viec=viec, thoi_han=10,
                ma_loi="NGUON_DU_PHONG_CHUA_CAI", doc_stdout=True)
    co_san = set(out.decode("utf-8", errors="replace").splitlines())
    if not set(ngon_ngu.split("+")) <= co_san:
        raise LoiNghiepVu("NGUON_DU_PHONG_CHUA_CAI", "Chưa cài đủ ngôn ngữ Tesseract đã chọn. Hãy cài bộ tiếng Việt và tiếng Anh.")
    return exe, ngon_ngu


def _hop_cac_tu(tu):
    return [min(t["hop"][0] for t in tu), min(t["hop"][1] for t in tu),
            max(t["hop"][2] for t in tu), max(t["hop"][3] for t in tu)]


def _doc_tsv(raw, *, so, rong, cao, pixel):
    """Giữ tọa độ từ do nguồn trả; không suy điểm tin cậy khi nguồn thiếu."""
    try:
        dong = {}
        for row in csv.DictReader(io.StringIO(raw.decode("utf-8-sig")), delimiter="\t"):
            if row["level"] != "5":
                continue
            text = normalize(row["text"]).strip()
            if not text:
                continue
            x, y, w, h = (int(row[k]) for k in ("left", "top", "width", "height"))
            if not (0 <= x < x + w <= pixel[0] and 0 <= y < y + h <= pixel[1]):
                raise ValueError
            hop = [x * rong / pixel[0], y * cao / pixel[1],
                   (x + w) * rong / pixel[0], (y + h) * cao / pixel[1]]
            khoa = tuple(int(row[k]) for k in ("block_num", "par_num", "line_num"))
            dong.setdefault(khoa, []).append({"van_ban": text, "hop": hop})
        khoi, texts = [], []
        for words in dong.values():
            text, box = " ".join(w["van_ban"] for w in words), _hop_cac_tu(words)
            khoi.append({"loai": "doan", "van_ban": text, "hop": box,
                         "dong": [{"van_ban": text, "hop": box, "tu": words}]})
            texts.append(text)
        if not texts:
            raise ValueError
        return {"so": so, "rong": rong, "cao": cao, "don_vi": "pt", "khoi": khoi}, "\n".join(texts)
    except (KeyError, ValueError, TypeError, UnicodeError, csv.Error):
        raise LoiNghiepVu("TESSERACT_KHONG_DOC_DUOC", "Tesseract chưa trả được chữ và vị trí đầy đủ. Hãy kiểm tra tài liệu gốc.") from None


def _ghep_bang(trang, bang):
    """Giữ hình học bảng vector gốc, điền chữ OCR vào đúng ô kể cả ô rỗng."""
    words = [w for k in trang["khoi"] for d in k["dong"] for w in d["tu"]]

    def trong(box, hop):
        return hop[0] <= (box[0] + box[2]) / 2 < hop[2] and hop[1] <= (box[1] + box[3]) / 2 < hop[3]

    da_ghep = set()
    for b in bang:
        for cell in b["o"]:
            tu_trong_o = [w for w in words if trong(w["hop"], cell["hop"])]
            cell["van_ban"] = " ".join(w["van_ban"] for w in tu_trong_o)
            da_ghep.update(id(w) for w in tu_trong_o)
    ngoai_bang = []
    # Một dòng OCR có thể chứa cả ô bảng và chú thích bên cạnh. Chỉ bỏ
    # đúng từ đã điền vào ô, không bỏ cả dòng theo tâm hộp bao của dòng.
    for k in trang["khoi"]:
        for d in k["dong"]:
            con_lai = [w for w in d["tu"] if id(w) not in da_ghep]
            if con_lai:
                text, box = " ".join(w["van_ban"] for w in con_lai), _hop_cac_tu(con_lai)
                ngoai_bang.append({"loai": "doan", "van_ban": text, "hop": box,
                                   "dong": [{"van_ban": text, "hop": box, "tu": con_lai}]})
    trang["khoi"] = sorted([*ngoai_bang, *bang], key=lambda k: (k["hop"][1], k["hop"][0]))


def doc_tesseract(raw, mime, cau_hinh, *, viec):
    exe, ngon_ngu = _kiem_bo_doc(cau_hinh, viec)
    # Import lười: PDF có lớp chữ và ABBYY không cần bộ render ảnh.
    from PIL import Image

    pages, texts = [], []
    canh_bao = ["Chữ do Tesseract nhận dạng có thể sai; cần đối chiếu tiền, ngày và bảng với bản gốc."]
    han_viec = time.monotonic() + 840

    def nhan_dang(anh, thu_muc, so, size, bang=()):
        viec.kiem_huy()
        if not 0 < anh.width * anh.height <= MAX_PIXEL:
            raise LoiNghiepVu("ANH_QUA_LON", "Trang vượt 20 triệu pixel. Hãy giảm kích thước hoặc chia nhỏ tài liệu.")
        vao = thu_muc / f"trang-{so}.png"
        dich = thu_muc / f"chu-{so}"
        anh.save(vao, format="PNG", dpi=(DPI, DPI))
        _chay([exe, str(vao), str(dich), "-l", ngon_ngu, "--dpi", str(DPI), "tsv"],
              viec=viec, thoi_han=min(THOI_HAN_TRANG, han_viec - time.monotonic()),
              ma_loi="TESSERACT_KHONG_DOC_DUOC")
        with dich.with_suffix(".tsv").open("rb") as f:
            tsv = f.read(MAX_TSV + 1)
        if len(tsv) > MAX_TSV:
            raise LoiNghiepVu("QUA_DO_DAI", "Kết quả Tesseract vượt giới hạn đọc. Hãy chia nhỏ tài liệu.")
        page, text = _doc_tsv(tsv, so=so, rong=size[0], cao=size[1], pixel=anh.size)
        if bang:
            _ghep_bang(page, bang)
        else:
            canh_bao.append("Chưa xác định cấu trúc bảng từ ảnh; cần đối chiếu bảng với bản gốc.")
        return page, text

    def them(page, text):
        pages.append(page)
        texts.append(text)
        if sum(map(len, texts)) + len(texts) - 1 > MAX_TEXT:
            raise LoiNghiepVu("QUA_DO_DAI", "Nội dung vượt giới hạn đọc. Hãy chia nhỏ tài liệu.")

    try:
        with TemporaryDirectory(prefix="e-ocr-tesseract-") as tam:
            thu_muc = Path(tam)
            ocr_pages = 0
            if mime == "application/pdf":
                import pdfplumber
                import pypdfium2

                pdf_anh = pypdfium2.PdfDocument(raw)
                try:
                    with pdfplumber.open(io.BytesIO(raw)) as pdf:
                        for i, trang_goc in enumerate(pdf.pages):
                            viec.kiem_huy()
                            viec.tien_do(60 + int(30 * i / len(pdf.pages)), "Đang đọc trang tài liệu bằng Tesseract.")
                            try:
                                page, text, warnings_page = _doc_trang(trang_goc, pdfplumber, viec.kiem_huy)
                                canh_bao.extend(warnings_page)
                            except LoiLopChu as loi:
                                if loi.ma != "KHONG_CO_LOP_CHU":
                                    raise
                                src = pdf_anh[i]
                                try:
                                    size = src.get_size()
                                    if math.ceil(size[0] * DPI / 72) * math.ceil(size[1] * DPI / 72) > MAX_PIXEL:
                                        raise LoiNghiepVu("ANH_QUA_LON", "Trang PDF quá lớn để nhận dạng. Hãy chia nhỏ tài liệu.")
                                    bitmap = src.render(scale=DPI / 72)
                                    try:
                                        anh = bitmap.to_pil()
                                        try:
                                            x0, y0 = trang_goc.bbox[:2]
                                            bang = doc_bang_trang(
                                                trang_goc, chuyen_hop=lambda b: [b[0]-x0, b[1]-y0, b[2]-x0, b[3]-y0],
                                                huong={}, kiem_huy=viec.kiem_huy,
                                            )
                                            page, text = nhan_dang(anh, thu_muc, i + 1, size, bang)
                                        finally:
                                            anh.close()
                                    finally:
                                        bitmap.close()
                                finally:
                                    src.close()
                                ocr_pages += 1
                            them(page, text)
                            trang_goc.close()
                finally:
                    pdf_anh.close()
            else:
                viec.tien_do(60, "Đang đọc ảnh tài liệu bằng Tesseract.")
                with Image.open(io.BytesIO(raw)) as goc:
                    with goc.convert("RGB") as anh:
                        page, text = nhan_dang(anh, thu_muc, 1, (anh.width * 72 / DPI, anh.height * 72 / DPI))
                them(page, text)
                ocr_pages = 1
    except OSError:
        raise LoiNghiepVu("TESSERACT_KHONG_DOC_DUOC", "Không đọc hoặc dọn được tệp tạm Tesseract. Hãy kiểm tra quyền lưu trữ.") from None
    viec.kiem_huy()
    return KetQuaLopChu("\f".join(texts), list(dict.fromkeys(canh_bao)), ocr_pages, pages)
