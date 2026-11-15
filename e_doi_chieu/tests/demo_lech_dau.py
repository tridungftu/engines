"""Chỉ DEMO: adapter Core cấp nguồn OCR vùng giả, không có adapter trong gói."""
from copy import deepcopy
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw

from test_dc3 import Mau, CoreTepConDEMO, hs, chay, PN, MODULE
from test_dc4 import dat_cap
from test_dc5 import bo_demo, dat_bo


class CoreOCRVungDEMO(CoreTepConDEMO):
    def __init__(self):
        super().__init__()
        self.ocr_vung_viec = {}

    def _nhan_viec(self, ma):
        v = super()._nhan_viec(ma)
        if v and v["id"] in self.ocr_vung_viec:
            v["ngu_canh"]["doi_chieu_ocr_vung"] = deepcopy(self.ocr_vung_viec[v["id"]])
        return v


def dat_tu_dien(m, bo=None, value=None):
    raw = (Path(__file__).parent / "fixtures/DEMO-tu-dien-dc7.json").read_bytes() if value is None else hs.json_bytes(value)
    value = json.loads(raw)
    ref = m.luu("DEMO-tu-dien-dc7.json", raw, "application/json")
    ref["phien_ban"] = value["phien_ban_bo"]
    b = deepcopy(bo) if bo is not None else bo_demo()
    b["lech_dau"] = {"phien_ban": 1, "tu_dien": ref, "nguong_ocr_kem": None}
    m.cau_hinh.update(ma_tu_dien=value["ma"], bam_tu_dien=ref["bam"])
    dat_bo(m, b)
    return b


def dat_cap_co_tu(m, word, ocr):
    dat_cap(m, word, ocr)
    vb = m.vb()
    v = vb["van_ban_tai_lieu"]
    # Hộp OCR và raster đều là fixture; chỉ kiểm liên kết và offset, không đo OCR.
    for i, (page, text) in enumerate(zip(v["trang"], ocr.split("\f"))):
        parts = text.split()
        w, h = max(100, 40*len(parts)), 60
        page.update(rong=w, cao=h)
        words = []
        with Image.new("RGB", (w, h), "white") as im, io.BytesIO() as out:
            draw = ImageDraw.Draw(im)
            for j, part in enumerate(parts):
                t = part.strip(".,:;!?()[]")
                if t:
                    box = [j*40, 10, j*40+35, 30]
                    words.append({"van_ban": t, "hop": box, "nghi_ngo": True})
                    draw.rectangle(box, outline="black")
            im.save(out, format="PNG")
            ref = m.luu(f"DEMO-trang-tu-{i}.png", out.getvalue(), "image/png")
        page["khoi"] = [{"loai": "doan", "van_ban": text, "hop": [0, 0, w, h],
                          "dong": [{"van_ban": text, "hop": [0, 0, w, h], "tu": words}]}]
        m.cap["anh_trang"][i] = {"so": i+1, **ref}
    m.dat_vb(vb)


def manifest_ocr(m, s, *, text=None, anh_cat=False):
    rows = []
    for r in s["lech_dau"]["ket_qua"]:
        v = r["vung"]
        if v is None:
            continue
        d = next(d for d in s["diem_lech"] if d["ma_diem"] == r["ma_diem"])
        from e_doi_chieu.tu_dien import CacTu
        w = CacTu(s["van_ban"]["word"]["van_ban_tai_lieu"]["van_ban"])
        tokens = w.lay(d["word"]["bat_dau"], d["word"]["ket_thuc"])
        e = {"phien_ban": 1, "ma_cap": s["ma_cap"], "ma_diem": r["ma_diem"],
             "bam_ban_ky": s["nguon"]["ban_ky"]["bam"], "phien_ban_ban_ky": s["nguon"]["ban_ky"]["phien_ban"],
             **{k: deepcopy(v[k]) for k in ("trang", "hop", "don_vi", "bat_dau", "ket_thuc")},
             "bam_anh_trang": s["anh_trang"][v["trang"]-1]["bam"], "nguon_doc": "ocr_thu_hai",
             "phien_ban_nguon": "DEMO-ocr-2", "van_ban": text if text is not None else " ".join(w.tu[i]["van_ban"] for i in tokens),
             "nghi_ngo_abbyy": True}
        if anh_cat:
            page = s["anh_trang"][v["trang"]-1]
            with Image.open(io.BytesIO(m.core.doc_tep(page["tep"]["tep_id"]))) as im, im.crop(v["hop"]) as cut, io.BytesIO() as out:
                cut.save(out, format="PNG")
                e["anh_cat"] = m.luu("DEMO-anh-cat.png", out.getvalue(), "image/png")
        ref = m.luu("DEMO-ocr-vung.json", hs.json_bytes(e), "application/json")
        rows.append({**ref, "nguon_doc": e["nguon_doc"], "phien_ban_nguon": e["phien_ban_nguon"],
                     "nang_luc": "ocr.trich_vung@1", "ma_ket_qua": "DEMO-kq-"+ref["tep"]["tep_id"]})
    return {"phien_ban": 1, "ma_cap": s["ma_cap"], "bam_ban_ky": s["nguon"]["ban_ky"]["bam"],
            "phien_ban_ban_ky": s["nguon"]["ban_ky"]["phien_ban"], "ket_qua": rows}
