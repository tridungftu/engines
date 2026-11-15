"""Nhận cặp qua SDK; snapshot ở Core, chỉ mục/CAS ở ngăn, không sổ đĩa."""
from copy import deepcopy
from hashlib import sha256
import io
import json
import math
from pathlib import Path
import re
import time
import uuid
import zipfile

from kho_tri_thuc_sdk.engine import ChuaRo, LoiDuongTruyen, LoiNghiepVu, ViecDaHuy

from .chuan_hoa import chuan_hoa, kiem_bo
from .doc_docx import MIME_DOCX, doc_bytes, _kiem_danh_muc, _kiem_zip
from .ngan import NganKhongHopLe, NganXungDot
from .vi_tri import kiem_anh, loi

MIB = 1048576
_GOI = Path(__file__).resolve().parent.parent
_SCHEMA_VB = json.loads((_GOI / "van_ban_tai_lieu.schema.json").read_text(encoding="utf-8"))
_SCHEMA_HS = json.loads((_GOI / "ho_so_doi_chieu.schema.json").read_text(encoding="utf-8"))
_BAM = re.compile(r"sha256:[0-9a-fA-F]{64}")
_KIEM = ("doc_hai_ban", "so_van_ban", "quy_tac_cung", "trang", "lech_dau", "sua_tay", "phan_loai_ai")
_DEM = ("so_diem", "so_nghiem_trong", "so_can_xem", "so_hinh_thuc", "so_nhieu_ocr", "so_vung_sua_tay", "so_trang_ocr_kem")


def bam(raw):
    return "sha256:" + sha256(raw).hexdigest()


def json_bytes(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def doc_json(raw, kiem_huy=lambda: None):
    """UTF-8 nghiêm, khóa trùng/NaN/surrogate/độ sâu >64 đều từ chối."""
    def cap(pairs):
        d = {}
        for k, v in pairs:
            if k in d:
                loi("DC_SAI_DAU_VAO")
            d[k] = v
        return d

    def sai_hang(_):
        loi("DC_SAI_DAU_VAO")

    try:
        # Đếm trước parse để parser không cấp cây sâu hoặc lỗi RecursionError.
        text = raw.decode("utf-8", errors="strict")
        trong, escape, sau = False, False, 0
        for i, c in enumerate(text):
            if i % 4096 == 0:
                kiem_huy()
            if trong:
                if escape:
                    escape = False
                elif c == "\\":
                    escape = True
                elif c == '"':
                    trong = False
            elif c == '"':
                trong = True
            elif c in "[{":
                sau += 1
                if sau > 64:
                    loi("DC_QUA_GIOI_HAN")
            elif c in "]}":
                sau -= 1
        value = json.loads(text, object_pairs_hook=cap, parse_constant=sai_hang)
        stack = [value]
        while stack:
            kiem_huy()
            x = stack.pop()
            if type(x) is dict:
                stack.extend(x.keys())
                stack.extend(x.values())
            elif type(x) is list:
                stack.extend(x)
            elif type(x) is str:
                x.encode("utf-8", errors="strict")
            elif type(x) is float and not math.isfinite(x):
                loi("DC_SAI_DAU_VAO")
        return value
    except (UnicodeError, ValueError, RecursionError):
        loi("DC_SAI_DAU_VAO")


def kiem_schema(value, schema, root=None):
    """Tập con khép kín dùng bởi hai schema đã ghim; không tải schema ngoài."""
    root = schema if root is None else root
    tu_khoa = {"$schema", "$id", "$comment", "$defs", "$ref", "title", "description", "type", "const", "enum",
               "required", "properties", "additionalProperties", "items", "minItems", "maxItems", "minLength",
               "maxLength", "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "pattern", "oneOf"}
    if type(schema) is not dict or not schema.keys() <= tu_khoa:
        loi()
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/$defs/"):
            loi()
        kiem_schema(value, root["$defs"][ref.rsplit("/", 1)[-1]], root)
    if "oneOf" in schema:
        so = 0
        for con in schema["oneOf"]:
            try:
                kiem_schema(value, con, root)
                so += 1
            except LoiNghiepVu:
                pass
        if so != 1:
            loi()
    kinds = {"object": type(value) is dict, "array": type(value) is list,
             "string": type(value) is str, "integer": type(value) is int,
             "number": type(value) in (int, float), "boolean": type(value) is bool, "null": value is None}
    if "type" in schema:
        types = schema["type"] if type(schema["type"]) is list else [schema["type"]]
        if not any(kinds[k] for k in types):
            loi()
    if "const" in schema and json_bytes(value) != json_bytes(schema["const"]):
        loi()
    if "enum" in schema and not any(json_bytes(value) == json_bytes(v) for v in schema["enum"]):
        loi()
    if type(value) is dict:
        if not set(schema.get("required", [])) <= value.keys():
            loi()
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False and not value.keys() <= props.keys():
            loi()
        for k, x in value.items():
            if k in props:
                kiem_schema(x, props[k], root)
    if type(value) in (str, list):
        low, high = ("minLength", "maxLength") if type(value) is str else ("minItems", "maxItems")
        if not schema.get(low, 0) <= len(value) <= schema.get(high, math.inf):
            loi()
        if type(value) is list and "items" in schema:
            for x in value:
                kiem_schema(x, schema["items"], root)
    if type(value) is str and "pattern" in schema and re.search(schema["pattern"], value) is None:
        loi()
    if type(value) in (int, float):
        try:
            huu_han = math.isfinite(value)
        except OverflowError:
            huu_han = False
        if (not huu_han or not schema.get("minimum", -math.inf) <= value <= schema.get("maximum", math.inf) or
                not schema.get("exclusiveMinimum", -math.inf) < value < schema.get("exclusiveMaximum", math.inf)):
            loi()


def _khoa(value, bat_buoc, tuy_chon=()):
    if type(value) is not dict or not set(bat_buoc) <= value.keys() or not value.keys() <= set(bat_buoc) | set(tuy_chon):
        loi("DC_SAI_DAU_VAO")


def _chu(value, toi_da):
    if type(value) is not str or not 1 <= len(value) <= toi_da or not value.strip():
        loi("DC_SAI_DAU_VAO")


def _bam(value):
    if type(value) is not str or _BAM.fullmatch(value) is None:
        loi()
    return value.lower()


def _tep(tep, mimes, toi_da):
    _khoa(tep, ("tep_id", "ten", "mime", "kich_thuoc"))
    _chu(tep["tep_id"], 200)
    _chu(tep["ten"], 255)
    if (any(ord(c) < 32 for c in tep["tep_id"]) or
            any(c in tep["ten"] for c in ("/", "\\", "\0")) or tep["mime"] not in mimes or
            type(tep["kich_thuoc"]) is not int or tep["kich_thuoc"] <= 0):
        loi("DC_SAI_DAU_VAO")
    if tep["kich_thuoc"] > toi_da:
        loi("DC_QUA_GIOI_HAN")


def _ref(ref, mimes, toi_da, phien_ban=False):
    _khoa(ref, ("tep", "bam", "phien_ban") if phien_ban else ("tep", "bam"))
    _tep(ref["tep"], mimes, toi_da)
    _bam(ref["bam"])
    if phien_ban:
        _chu(ref["phien_ban"], 100)


class _DocTep:
    def __init__(self, viec, cau_hinh):
        self.viec, self.cau_hinh, self.tong = viec, cau_hinh, 0
        self.da_doc = {}

    def doc(self, ref, toi_da):
        """Mọi quyền do mo_tep kiểm; cache chỉ trong một việc, vẫn kiểm ref lặp."""
        tep = ref["tep"]
        _tep(tep, (tep["mime"],), toi_da)
        self.viec.kiem_huy()
        tid = tep["tep_id"]
        if tid in self.da_doc:
            raw, metadata = self.da_doc[tid]
            if metadata != tep:
                loi()
        else:
            con = self.cau_hinh["tong_byte_tep_con"] - self.tong
            if tep["kich_thuoc"] > con:
                loi("DC_QUA_GIOI_HAN")
            try:
                with self.viec.mo_tep(tid) as f:
                    raw = f.read(min(toi_da, con) + 1)
            except LoiDuongTruyen as exc:
                if exc.http_status in (403, 404, 410):
                    loi("DC_THIEU_NGUON")
                if exc.http_status == 413:
                    loi("DC_QUA_GIOI_HAN")
                raise
            except (FileNotFoundError, PermissionError):
                loi("DC_THIEU_NGUON")
            if len(raw) > min(toi_da, con):
                loi("DC_QUA_GIOI_HAN")
            self.tong += len(raw)
            self.da_doc[tid] = raw, deepcopy(tep)
        if len(raw) != tep["kich_thuoc"] or bam(raw) != _bam(ref["bam"]):
            loi()
        return raw


def _kiem_cap(cap, cau_hinh):
    keys = ("phien_ban", "ma_cap", "nguon", "van_ban", "anh_trang", "ban_chuan_phan_trang",
            "bo_quy_tac", "kiem_dau_vao", "bang_chung_ocr_lai")
    _khoa(cap, keys, ("anh_trang_word",))
    if type(cap["phien_ban"]) is not int or cap["phien_ban"] != 1:
        loi("DC_SAI_DAU_VAO")
    _chu(cap["ma_cap"], 200)
    for key in ("nguon", "van_ban"):
        _khoa(cap[key], ("word", "ban_ky"))
    tep_max = cau_hinh["tep_mib"] * MIB
    _ref(cap["nguon"]["word"], (MIME_DOCX,), tep_max, True)
    _ref(cap["nguon"]["ban_ky"], ("application/pdf",), tep_max, True)
    for ref in cap["van_ban"].values():
        _ref(ref, ("application/json",), cau_hinh["ho_so_mib"] * MIB)
    _ref(cap["bo_quy_tac"], ("application/json",), 65536, True)
    _khoa(cap["kiem_dau_vao"], ("word_da_chot", "ocr_day_du", "canh_bao"))
    k = cap["kiem_dau_vao"]
    if type(k["word_da_chot"]) is not bool or type(k["ocr_day_du"]) is not bool:
        loi("DC_SAI_DAU_VAO")
    if not k["word_da_chot"] or not k["ocr_day_du"]:
        loi("DC_OCR_KHONG_DOC_DUOC")
    if (type(k["canh_bao"]) is not list or len(k["canh_bao"]) > 100 or
            any(type(x) is not str or not 1 <= len(x) <= 1000 for x in k["canh_bao"])):
        loi("DC_SAI_DAU_VAO")
    if cap["ban_chuan_phan_trang"] is not None:
        _ref(cap["ban_chuan_phan_trang"], ("application/pdf",), tep_max, True)
        if "anh_trang_word" not in cap:
            loi("DC_THIEU_NGUON")
    elif "anh_trang_word" in cap:
        loi("DC_SAI_DAU_VAO")
    for key in ("anh_trang", "anh_trang_word"):
        if key not in cap:
            continue
        ds = cap[key]
        if type(ds) is not list:
            loi("DC_SAI_DAU_VAO")
        if len(ds) > cau_hinh["so_trang_toi_da"]:
            loi("DC_QUA_GIOI_HAN")
        for a in ds:
            _khoa(a, ("so", "tep", "bam"))
            if type(a["so"]) is not int or not 1 <= a["so"] <= cau_hinh["so_trang_toi_da"]:
                loi("DC_QUA_GIOI_HAN")
            _ref({k: a[k] for k in ("tep", "bam")}, ("image/png", "image/jpeg"), tep_max)
        if len({a["so"] for a in ds}) != len(ds):
            loi()
    if type(cap["bang_chung_ocr_lai"]) is not list:
        loi("DC_SAI_DAU_VAO")
    if len(cap["bang_chung_ocr_lai"]) > cau_hinh["diem_lech_toi_da"]:
        loi("DC_QUA_GIOI_HAN")
    for a in cap["bang_chung_ocr_lai"]:
        _ref(a, ("application/json",), cau_hinh["ho_so_mib"] * MIB)


def _pdf(raw):
    # DC-3 kiểm định dạng vận chuyển; OCR/PDF renderer thuộc Core/engine OCR.
    if not re.match(rb"%PDF-(?:1\.[0-9]|2\.0)[\r\n]", raw) or not raw.rstrip().endswith(b"%%EOF"):
        loi()


def _doc_hai_ban(cap, doc, cau_hinh, phien_ban_engine):
    vb, chu_ky_anh = {}, {}
    raw_word = doc.doc(cap["nguon"]["word"], cau_hinh["tep_mib"] * MIB)
    # Tái kiểm bản Word bằng chính DC-2, không tin word_da_chot của caller.
    _kiem_danh_muc(raw_word)
    try:
        with zipfile.ZipFile(io.BytesIO(raw_word)) as z:
            _kiem_zip(z, doc.viec.kiem_huy)
            if (len(z.infolist()) > cau_hinh["docx_so_muc"] or
                    sum(i.file_size for i in z.infolist()) > cau_hinh["docx_giai_nen_mib"] * MIB):
                loi("DC_QUA_GIOI_HAN")
    except zipfile.BadZipFile:
        loi()
    word_that = doc_bytes(raw_word, doc.viec.kiem_huy, lambda *a: None, phien_ban_engine=phien_ban_engine)
    _pdf(doc.doc(cap["nguon"]["ban_ky"], cau_hinh["tep_mib"] * MIB))
    for ben in ("word", "ban_ky"):
        pb = doc_json(doc.doc(cap["van_ban"][ben], cau_hinh["ho_so_mib"] * MIB), doc.viec.kiem_huy)
        kiem_schema(pb, _SCHEMA_VB)
        v = pb["van_ban_tai_lieu"]
        if _bam(v["bam_dau_vao"]) != _bam(cap["nguon"][ben]["bam"]):
            loi()
        if not v["van_ban"].strip() or v.get("trang_thai", "XONG") != "XONG" or v.get("loi"):
            loi("DC_OCR_KHONG_DOC_DUOC")
        if len(v["van_ban"]) > cau_hinh["ky_tu_moi_tai_lieu"] or v["so_trang"] > cau_hinh["so_trang_toi_da"]:
            loi("DC_QUA_GIOI_HAN")
        if v["so_trang"] != len(v["trang"]):
            loi()
        if ben == "word":
            # Phiên bản đọc đã ghim có thể cũ hơn phiên bản engine hiện tại.
            mong_doi = deepcopy(word_that["van_ban_tai_lieu"])
            mong_doi["phien_ban_engine"] = v["phien_ban_engine"]
            mong_doi["bam_dau_vao"] = v["bam_dau_vao"]  # Đã so digest, chấp nhận hex hoa/thường theo schema.
            if v != mong_doi:
                loi()
        elif v["nguon_doc"] == "docx" or not v["so_trang"]:
            loi("DC_OCR_KHONG_DOC_DUOC")
        vb[ben] = pb
    if sum(len(p["van_ban_tai_lieu"]["van_ban"]) for p in vb.values()) > cau_hinh["ky_tu_hai_tai_lieu"]:
        loi("DC_QUA_GIOI_HAN")
    trang = vb["ban_ky"]["van_ban_tai_lieu"]["trang"]
    if [a["so"] for a in cap["anh_trang"]] != list(range(1, len(trang) + 1)):
        loi("DC_THIEU_NGUON")
    for key in ("anh_trang", "anh_trang_word"):
        chu_ky_anh[key] = []
        for a in cap.get(key, []):
            raw = doc.doc(a, cau_hinh["tep_mib"] * MIB)
            dims = kiem_anh(raw, a["tep"]["mime"], cau_hinh["pixel_anh"], doc.viec.kiem_huy)
            if key == "anh_trang":
                page = trang[a["so"] - 1]
                if (page["don_vi"] == "px" and (dims["rong"], dims["cao"]) != (page["rong"], page["cao"]) or
                        page["don_vi"] not in ("pt", "px")):
                    loi()
            chu_ky_anh[key].append({"so": a["so"], **dims})
    if cap["ban_chuan_phan_trang"] is not None:
        _pdf(doc.doc(cap["ban_chuan_phan_trang"], cau_hinh["tep_mib"] * MIB))
        if not cap["anh_trang_word"] or [a["so"] for a in cap["anh_trang_word"]] != list(range(1, len(cap["anh_trang_word"]) + 1)):
            loi("DC_THIEU_NGUON")
    return vb, chu_ky_anh


def _phong_bi(snapshot, tep, raw):
    p = {k: deepcopy(snapshot[k]) for k in ("phien_ban", "ma_cap", "giai_doan", "tom_tat", "kiem_tra", "da_kiem_du",
                                          "ket_luan", "de_nghi_chan", "canh_bao", "phien_ban_engine")}
    p["nguon"] = {k: {"tep_id": v["tep"]["tep_id"], "phien_ban": v["phien_ban"], "bam": _bam(v["bam"])}
                  for k, v in snapshot["nguon"].items()}
    p.update(ho_so=tep, bam_ho_so=bam(raw), bam_bo_quy_tac=_bam(snapshot["bo_quy_tac"]["bam"]))
    pb = {"loai": "ho_so_doi_chieu", "ho_so_doi_chieu": p}
    kiem_schema(pb, _SCHEMA_HS)
    if len(json_bytes(pb)) > 65536:
        loi("DC_QUA_GIOI_HAN")
    return pb


def _lay_cu(doc, ban):
    pb = ban.gia_tri["phong_bi"]
    kiem_schema(pb, _SCHEMA_HS)
    p = pb["ho_so_doi_chieu"]
    raw = doc.doc({"tep": p["ho_so"], "bam": p["bam_ho_so"]}, doc.cau_hinh["ho_so_mib"] * MIB)
    snapshot = doc_json(raw, doc.viec.kiem_huy)
    if _phong_bi(snapshot, p["ho_so"], raw) != pb:
        loi()
    # Cùng băm không cấp quyền tới ID cũ. Mở lại mọi tham chiếu của kết quả
    # được tái dùng trong phạm vi việc hiện tại, kể cả sau khi người dùng tải lại.
    refs = [*snapshot["nguon"].values(), *snapshot["tham_chieu_van_ban"].values(),
            snapshot["bo_quy_tac"], *snapshot["anh_trang"], *snapshot.get("anh_trang_word", []),
            *snapshot["bang_chung_ocr_lai"]]
    if snapshot["ban_chuan_phan_trang"] is not None:
        refs.append(snapshot["ban_chuan_phan_trang"])
    for ref in refs:
        doc.doc(ref, doc.cau_hinh["tep_mib"] * MIB)
    return pb


def nhan_cap(viec, ngan, cau_hinh, *, phien_ban_engine):
    """Chỉ dùng ngu_canh do Core cấp, không lấy danh tính từ JSON yêu cầu."""
    viec.kiem_huy()
    _khoa(viec.dau_vao, ("loai", "tep"))
    if viec.dau_vao["loai"] != "tep":
        loi("DC_SAI_DAU_VAO")
    _tep(viec.dau_vao["tep"], ("application/json",), MIB)
    doc = _DocTep(viec, cau_hinh)
    ref = {"tep": viec.dau_vao["tep"], "bam": _bam(viec.tham_so.get("bam_yeu_cau"))}
    # Không parse trước khi hash bytes nguyên tệp và so metadata.
    cap = doc_json(doc.doc(ref, MIB), viec.kiem_huy)
    _kiem_cap(cap, cau_hinh)
    phap_nhan = viec.ngu_canh.get("phap_nhan_id")
    if type(phap_nhan) is not str or not phap_nhan.strip():
        loi("DC_THIEU_NGUON")
    viec.tien_do(5, "Đang kiểm tra nguồn và quyền đọc cặp tài liệu")
    vb, anh = _doc_hai_ban(cap, doc, cau_hinh, phien_ban_engine)
    bo = doc_json(doc.doc(cap["bo_quy_tac"], 65536), viec.kiem_huy)
    if _bam(cap["bo_quy_tac"]["bam"]) != _bam(cau_hinh["bam_bo_chuan_hoa"]):
        loi()
    q = kiem_bo(bo, cap["bo_quy_tac"]["phien_ban"], cau_hinh)
    bang_chung = []
    for a in cap["bang_chung_ocr_lai"]:
        # DC-7 mới đánh giá bằng chứng; hiện giữ nguyên đã ghim, không coi là kiểm đạt.
        bang_chung.append({**a, "noi_dung": doc_json(doc.doc(a, cau_hinh["ho_so_mib"] * MIB), viec.kiem_huy)})
    # Băm cả phiên bản/đầu ra dẫn xuất để không tái dùng một lần OCR khác.
    def dau_ref(ref):
        if ref is None:
            return None
        return {"bam": _bam(ref["bam"]), **{k: ref[k] for k in ("phien_ban", "so") if k in ref}}
    dau_cap = {"nguon": {k: dau_ref(v) for k, v in cap["nguon"].items()},
               "van_ban": {k: dau_ref(v) for k, v in cap["van_ban"].items()},
               "anh_trang": [dau_ref(v) for v in cap["anh_trang"]],
               "ban_chuan_phan_trang": dau_ref(cap["ban_chuan_phan_trang"]),
               "bang_chung_ocr_lai": [dau_ref(v) for v in cap["bang_chung_ocr_lai"]]}
    if "anh_trang_word" in cap:
        dau_cap["anh_trang_word"] = [dau_ref(v) for v in cap["anh_trang_word"]]
    khoa = {"phap_nhan_id": phap_nhan, "bam_cap": bam(json_bytes(dau_cap)),
            "bam_bo": _bam(cap["bo_quy_tac"]["bam"]), "phien_ban_engine": phien_ban_engine}
    chu_so_huu = str(viec.ngu_canh.get("viec_id", viec.id)) + ":" + str(viec.lan_thu)
    ma_luot, ban, giu = uuid.uuid4().hex, None, False
    try:
        for lan in range(50):
            viec.kiem_huy()
            try:
                with ngan.lo() as lo:
                    kq = lo.lay_hoac_tao("luot_doi_chieu", khoa,
                        {**khoa, "ma_luot": ma_luot, "trang_thai": "dang_nhan", "chu_so_huu": chu_so_huu})
                ban = kq.ban_ghi  # KetQuaLenh chỉ được đọc sau commit.
                if kq.da_tao:
                    giu = True
                    break
                if ban.gia_tri["trang_thai"] == "da_nhan":
                    return _lay_cu(doc, ban)
                if ban.gia_tri["trang_thai"] == "can_thu_lai":
                    with ngan.lo() as lo:
                        kq = lo.sua("luot_doi_chieu", {"phap_nhan_id": phap_nhan, "ma_luot": ban.gia_tri["ma_luot"]},
                                    {"trang_thai": "dang_nhan", "chu_so_huu": chu_so_huu}, row_version=ban.row_version)
                    ban, giu = kq.ban_ghi, True
                    break
            except NganXungDot:
                if lan == 49:
                    raise
            if lan % 10 == 0:
                viec.tien_do(15, "Đang chờ lượt cùng cặp tài liệu hoàn tất")
            time.sleep(.02)
        if not giu:
            raise LoiNghiepVu("DC_DANG_XU_LY", "Cặp tài liệu đang được xử lý. Anh thử lại sau.", thu_lai_duoc=True)
        viec.tien_do(25, "Đang chuẩn hóa và giữ ánh xạ về nguyên văn")
        ch = {k: chuan_hoa(v["van_ban_tai_lieu"], q, viec.kiem_huy) for k, v in vb.items()}
        if any(not x["van_ban"].strip() for x in ch.values()):
            loi("DC_OCR_KHONG_DOC_DUOC")
        canh_bao = ["Chưa so văn bản, chưa áp quy tắc cứng, chưa kiểm OCR kém và chưa quét vùng sửa tay.",
                    "Chưa kiểm chứng ánh xạ phân trang Word; chưa so trang vật lý của hai bản."]
        if any(x["chua_neo_cau_truc"] for x in ch.values()):
            canh_bao.append("Một số khối OCR chưa neo được duy nhất vào nguyên văn; chỉ giữ vị trí trang, không đoán hộp chữ.")
        snapshot = {**deepcopy(cap), "giai_doan": "da_nhan", "phien_ban_engine": phien_ban_engine,
                    "van_ban": vb, "tham_chieu_van_ban": deepcopy(cap["van_ban"]), "chuan_hoa": ch,
                    "bo_quy_tac": {**deepcopy(cap["bo_quy_tac"]), "noi_dung": bo},
                    "cau_hinh": deepcopy(cau_hinh), "kiem_anh": anh, "bang_chung_ocr_lai": bang_chung,
                    "tom_tat": {k: None for k in _DEM},
                    "kiem_tra": {k: "dat" if k == "doc_hai_ban" else "chua_kiem" for k in _KIEM},
                    "da_kiem_du": False, "ket_luan": None, "de_nghi_chan": True, "canh_bao": canh_bao,
                    **{k: None for k in ("edit_script", "diem_lech", "quet_anh", "vung_sua_tay", "trang_ocr_kem", "ai")}}
        raw = json_bytes(snapshot)
        if len(raw) > cau_hinh["ho_so_mib"] * MIB:
            loi("DC_QUA_GIOI_HAN")
        viec.tien_do(80, "Đang gửi hồ sơ đầy đủ lên Core")
        tep = viec.tai_tep_ra("ho-so-doi-chieu.json", raw, "application/json")
        pb = _phong_bi(snapshot, tep, raw)
        for lan in range(3):
            viec.kiem_huy()
            try:
                with ngan.lo() as lo:
                    kq = lo.sua("luot_doi_chieu", {"phap_nhan_id": phap_nhan, "ma_luot": ban.gia_tri["ma_luot"]},
                                {"trang_thai": "da_nhan", "phong_bi": pb}, row_version=ban.row_version)
                giu = False
                break
            except NganXungDot:
                ban = ngan.doc("luot_doi_chieu", khoa)
                if (ban is None or ban.gia_tri.get("chu_so_huu") != chu_so_huu or
                        ban.gia_tri["trang_thai"] != "dang_nhan" or lan == 2):
                    raise
        viec.tien_do(100, "Đã nhận cặp tài liệu và giữ hồ sơ tại Core")
        viec.kiem_huy()
        return pb
    finally:
        if (giu and ban is not None and ban.gia_tri.get("chu_so_huu") == chu_so_huu and
                ban.gia_tri.get("trang_thai") == "dang_nhan"):
            # Không xóa sổ; nhường lần thử mới bằng CAS. Không đè lỗi gốc/hủy.
            try:
                with ngan.lo() as lo:
                    lo.sua("luot_doi_chieu", {"phap_nhan_id": phap_nhan, "ma_luot": ban.gia_tri["ma_luot"]},
                           {"trang_thai": "can_thu_lai"}, row_version=ban.row_version)
            except Exception:
                pass
