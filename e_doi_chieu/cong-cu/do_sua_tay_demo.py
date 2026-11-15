"""Đo DEMO offline; Q13 chỉ đọc kết quả Local vision do Core xuất, không gọi AI.

Công cụ của người phát triển, nằm ngoài gói engine; chỉ xuất JSON ra stdout.
"""
import argparse
from hashlib import sha256
import json
import math
import re
from pathlib import Path
import sys
import time
import tracemalloc

GOC = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(GOC / "tests"))
sys.path.insert(0, str(GOC / "goi/e_doi_chieu"))
from demo_sua_tay import CAC_CA, mau_anh, metadata_anh
from e_doi_chieu import sua_tay as st
from e_doi_chieu.anh import HeToaDo, doc_anh


def bam(raw):
    return "sha256:"+sha256(raw).hexdigest()


def cham(gold, pred):
    """Ghép một-một theo IoU lớn nhất, ngưỡng 0,3; không dùng mock."""
    ds = []
    for i, g in enumerate(gold):
        for j, p in enumerate(pred):
            inter = st._giao(g, p)
            union = (g[2]-g[0])*(g[3]-g[1])+(p[2]-p[0])*(p[3]-p[1])-inter
            if union and inter/union >= 0.3:
                ds.append((inter/union, i, j))
    matched_g, matched_p = set(), set()
    for _, i, j in sorted(ds, reverse=True):
        if i not in matched_g and j not in matched_p:
            matched_g.add(i)
            matched_p.add(j)
    tp = len(matched_g)
    return {"tp": tp, "fp": len(pred)-tp, "fn": len(gold)-tp}


def tong_hop(ds):
    tp, fp, fn = (sum(d[k] for d in ds) for k in ("tp", "fp", "fn"))
    return {"tp": tp, "fp": fp, "fn": fn, "precision": tp/(tp+fp) if tp+fp else None,
            "recall": tp/(tp+fn) if tp+fn else None, "lech_gia_moi_trang": fp/len(ds) if ds else None}


def do_anh(bo):
    ds = []
    tracemalloc.start()
    bat_dau = time.perf_counter()
    try:
        for ten, a in bo.items():
            start = time.perf_counter()
            meta = metadata_anh(a, bam(a["raw"]))
            with doc_anh(a["raw"], "image/png", 20000000, lambda: None) as im:
                he = HeToaDo.tu_core(a["page"], meta, im.size)
                tu = st._tu_trang(a["page"], he, lambda: None)
                excluded = st._loai_tru(meta, a["page"], tu, he)
                kq = st.BoPhatHienNet().quet(im, tu, lambda: None)
                boxes = [he.hop_nguon(v["hop_px"]) for v in kq["vung"] if not
                         any(x["duoc_loai"] and st._trong(v["hop_px"], x["hop_px"]) for x in excluded)]
            ds.append({"ma": ten, "bam_anh": bam(a["raw"]), "dap_an": a["gold"], "phat_hien": boxes,
                       "so_vung_loai": len(kq["vung"])-len(boxes), "giay": round(time.perf_counter()-start, 6),
                       **cham(a["gold"], boxes)})
        giay, ram = round(time.perf_counter()-bat_dau, 6), tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    return {"phuong_phap": st.PHUONG_PHAP, "phien_ban": st.PHIEN_BAN, "so_trang": len(ds),
            "ghep_vung": "IoU >= 0.3, mot-mot", "giay_tong_co_tracemalloc": giay,
            "ram_python_dinh_bytes": ram, "ram_tien_trinh_bytes": None,
            "ket_qua": tong_hop(ds), "trang": ds, "du_dieu_kien_van_hanh": False}


def doc_vision(path, bo):
    """Chỉ chấm file export DEMO; không chứng nhận provenance/quyền/giấy phép."""
    from e_doi_chieu.ho_so import doc_json
    if path.stat().st_size > 1048576:
        raise ValueError()
    data = doc_json(path.read_bytes())
    for k in ("model", "phien_ban_model", "nguon", "giay_phep"):
        if type(data.get(k)) is not str or not 1 <= len(data[k]) <= 200:
            raise ValueError()
    if (data.get("nguon") != "core_local" or type(data.get("phien_ban")) is not int or data["phien_ban"] != 1 or
            type(data.get("bam_model")) is not str or not re.fullmatch(r"sha256:[0-9a-f]{64}", data["bam_model"])):
        raise ValueError()
    giay, ram = data.get("giay_tong"), data.get("ram_dinh_bytes")
    if giay is not None and (type(giay) not in (int, float) or not math.isfinite(giay) or giay <= 0):
        raise ValueError()
    if ram is not None and (type(ram) is not int or ram <= 0):
        raise ValueError()
    pages = data.get("trang")
    if type(pages) is not list or len(pages) != len(bo) or {p.get("ma") for p in pages} != set(bo):
        raise ValueError()
    ds = []
    for p in pages:
        a = bo[p["ma"]]
        if p.get("bam_anh") != bam(a["raw"]) or p.get("da_quet_toan_trang") is not True:
            raise ValueError()
        boxes = p.get("hop")
        if type(boxes) is not list or len(boxes) > 10000:
            raise ValueError()
        for b in boxes:
            st._hop(b, a["page"])
        ds.append({"ma": p["ma"], **cham(a["gold"], boxes)})
    return {"trang_thai": "da_cham_file_export_chua_xac_minh_nguon", "model": data["model"],
            "phien_ban_model": data["phien_ban_model"], "bam_model": data["bam_model"],
            "giay": giay, "ram": ram,
            "ket_qua": tong_hop(ds), "trang": ds, "du_dieu_kien_van_hanh": False}


def main():
    parser = argparse.ArgumentParser(description="Đo vùng sửa tay DEMO; không mạng/model/Cloud.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--chay-kho", action="store_true", help="In đầu vào cần Core cấp cho phép đo Q13.")
    mode.add_argument("--do-demo", action="store_true", help="Đo detector pixel thật trên bộ ảnh DEMO tổng hợp.")
    parser.add_argument("--ket-qua-vision", type=Path, help="File JSON DEMO do Core xuất; không gọi model.")
    args = parser.parse_args()
    bo = {ten: mau_anh(ten) for ten in CAC_CA}
    report = {"nhan": "DEMO tong hop; khong phai scan/viet tay that", "cloud": 0,
              "local_vision": {"trang_thai": "chua_do", "model": None, "giay": None, "ram": None,
                               "ket_qua": None}, "anh": None}
    if args.do_demo:
        report["anh"] = do_anh(bo)
    else:
        report["chay_kho"] = {"so_trang": len(bo), "nguon_can_co": [
            "Core dieu phoi Local vision va cap anh DEMO dung bam, he toa do goc tren trai",
            "Lead xac nhan model/phien ban/bam/giay phep va RAM/VRAM",
            "Ket qua tung trang: ma, bam_anh, da_quet_toan_trang, hop trong he toa do nguon",
            "Do thoi gian/RAM tren may that; khong suy ra tu ten model"],
            "anh": [{"ma": ten, "bam_anh": bam(a["raw"])} for ten, a in bo.items()]}
    if args.ket_qua_vision:
        try:
            report["local_vision"] = doc_vision(args.ket_qua_vision, bo)
        except Exception:
            print("Chưa chấm được kết quả Local vision DEMO. Anh kiểm tra đủ trang, băm và tọa độ.", file=sys.stderr)
            return 1
    print(json.dumps(report, ensure_ascii=False, allow_nan=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
