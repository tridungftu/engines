"""Bộ ảnh DEMO tổng hợp có đáp án; không phải ảnh scan/viết tay thật."""
from copy import deepcopy
import io

from PIL import Image, ImageDraw, ImageFont

CAC_CA = ("khong_vet", "gach", "chen", "sat_chu", "chu_ky", "dau", "ky_nhay", "ky_chong_chu",
          "muc_mau_in", "net_xa_chu", "net_mo", "net_trong_chu")


def mau_anh(ten, *, ti_le=1, xoay=0):
    im = Image.new("RGB", (480, 240), "white")
    d, font, tu = ImageDraw.Draw(im), ImageFont.load_default(size=22), []
    for y, words in ((80, [(40, "DEMO"), (145, "1000000"), (270, "VND")]),
                     (140, [(40, "DEMO"), (145, "2026-10-30")])):
        for x, text in words:
            box = list(d.textbbox((x, y), text, font=font))
            d.text((x, y), text, font=font, fill="blue" if ten == "muc_mau_in" else "black")
            tu.append({"van_ban": text, "hop": box})
    gold, exclusions = [], []
    if ten == "gach":
        y = (tu[0]["hop"][1]+tu[0]["hop"][3])//2
        d.line([(30, y), (310, y)], fill="black", width=3)
        gold = [[30, y-1, 311, y+2]]
    elif ten in ("chen", "sat_chu", "chu_ky", "ky_nhay", "ky_chong_chu", "net_xa_chu", "net_mo"):
        x, y = {"chen": (65, 59), "sat_chu": (105, 80), "chu_ky": (325, 82),
                "ky_nhay": (325, 82), "ky_chong_chu": (65, 79), "net_xa_chu": (380, 200),
                "net_mo": (65, 59)}[ten]
        points = [(x, y+16), (x+5, y+2), (x+10, y+15), (x+16, y), (x+23, y+16), (x+30, y+2), (x+37, y+15)]
        d.line(points, fill=(190, 190, 190) if ten == "net_mo" else "black", width=2)
        box = [x-1, y-1, x+39, y+18]
        if ten in ("chen", "sat_chu", "ky_chong_chu", "net_mo"):
            gold = [box]
        if ten in ("chu_ky", "ky_nhay", "ky_chong_chu"):
            exclusions = [{"loai": "ky_nhay" if ten == "ky_nhay" else "chu_ky", "hop": box}]
    elif ten == "dau":
        box = [320, 80, 355, 112]
        d.ellipse(box, outline="red", width=2)
        exclusions = [{"loai": "con_dau", "hop": [319, 79, 357, 114]}]
    elif ten == "net_trong_chu":
        # Sửa mảnh trong hộp một chữ: ca khó để công bố bỏ sót của heuristic.
        x0, y0, x1, y1 = tu[0]["hop"]
        box = [x0+4, y0+3, x0+10, y1-2]
        d.line([box[:2], box[2:]], fill="black", width=1)
        gold = [box]
    page = {"so": 1, "rong": 480, "cao": 240, "don_vi": "pt", "khoi": [{
        "loai": "doan", "van_ban": "DEMO 1000000 VND DEMO 2026-10-30", "hop": [30, 75, 315, 170],
        "dong": [{"van_ban": "DEMO 1000000 VND", "hop": [30, 75, 315, 110], "tu": tu[:3]},
                 {"van_ban": "DEMO 2026-10-30", "hop": [30, 135, 315, 170], "tu": tu[3:]}]}]}
    if ti_le != 1:
        enlarged = im.resize((480*ti_le, 240*ti_le), resample=Image.Resampling.NEAREST)
        im.close()
        im = enlarged
    if xoay:
        rotated = im.rotate(-xoay, expand=True)
        im.close()
        im = rotated
    with io.BytesIO() as out:
        im.save(out, format="PNG")
        raw = out.getvalue()
    im.close()
    return {"raw": raw, "page": page, "gold": gold, "loai_tru": exclusions,
            "ti_le": ti_le, "xoay": xoay, "rong_px": (240 if xoay in (90, 270) else 480)*ti_le,
            "cao_px": (480 if xoay in (90, 270) else 240)*ti_le}


def metadata_anh(mau, bam):
    m = {k: mau[k] for k in ("ti_le", "xoay", "rong_px", "cao_px")}
    m.update(so=1, bam_anh=bam, rong_nguon=480, cao_nguon=240, don_vi="pt", he_toa_do="goc_tren_trai")
    m["vung_loai_tru"] = []
    for v in mau["loai_tru"]:
        m["vung_loai_tru"].append({**deepcopy(v), "can_cu": {"nguon": "core_xac_nhan", "ma": "DEMO-vung-da-duyet", "bam_anh": bam}})
    return m
