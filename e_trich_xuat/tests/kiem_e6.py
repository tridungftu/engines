"""Cổng E6 offline; artifact trả qua stdout/RAM, không sửa nguồn/runtime.

Thiếu nguồn/bản vàng được lead chấp nhận: exit 2 (chưa kiểm).
Nguồn sai băm: exit 3; byte khác: exit 1. Chỉ đủ mọi ca mới được exit 0.
"""

import argparse
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi/e_trich_xuat"))

from kho_tri_thuc_sdk import danh_muc_tham_so as e1, xlsx_mini
from kho_tri_thuc_sdk.thu import CoreGia
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from e_trich_xuat.tham_so import bam_bytes, doc_bo, doc_json, json_bytes
from doi_chieu_cu_e6 import CAC_TEP_NGUON, GOC, ThieuBangAI, chay_mac_dinh_chuyen_tiep, doc_bo_cu
from mau_tx3 import ai_demo, app_tx3


ENGINE = Path(__file__).resolve().parents[1]
BAM_XLSX_CU = "05846a2acd60f2cde708d13a163a137ee3fb0b4e08fd84f85a7e14e7ef861bcd"
THIEU = "Thiếu nguồn đối chiếu E6."
SAI_BAM = "Nguồn đối chiếu không khớp mã kiểm tra."
CAC_PHAN = ("bo_10_cot", "tham_so", "van_ban", "cau_hoi", "bang", "phan_hoi")


class LoiKiemE6(ValueError):
    def __init__(self, cau, ma_thoat):
        self.ma_thoat = ma_thoat
        super().__init__(cau)


def so_byte(trai, phai):
    """So bytes thực, báo offset từ 0/độ dài/băm; không in nội dung khác."""
    if not isinstance(trai, bytes) or not isinstance(phai, bytes):
        raise TypeError("Phép so E6 chỉ nhận byte.")
    dau = next((i for i, (a, b) in enumerate(zip(trai, phai)) if a != b), None)
    if dau is None and len(trai) != len(phai):
        dau = min(len(trai), len(phai))
    return {"trung_byte": trai == phai, "byte_khac_dau": dau,
            "so_byte_trai": len(trai), "so_byte_phai": len(phai),
            "bam_trai": bam_bytes(trai), "bam_phai": bam_bytes(phai)}


def cac_byte(v):
    # Giao thức cố định trước phép đo: không strip/NFC/round/bỏ cột/sắp mã.
    return {k: v[k].encode("utf-8") if isinstance(v[k], str) else json_bytes(v[k])
            for k in CAC_PHAN}


def so_cac_phan(trai, phai):
    if set(trai) != set(CAC_PHAN) or set(phai) != set(CAC_PHAN):
        raise LoiKiemE6(THIEU, 2)
    return {k: so_byte(trai[k], phai[k]) for k in CAC_PHAN}


def dong_nguyen_van(dong):
    return [[("Có" if r[k] else "Không") if k in ("dung", "luon_cloud")
             else str(r[k]) for k in e1.KHOA] for r in dong]


def kiem_nguon(goc=ENGINE):
    try:
        raw = (goc / "tham-chieu/DANH_MUC_THAM_SO.xlsx").read_bytes()
        nguon = (goc / "tham-chieu/NGUON.md").read_text(encoding="utf-8")
    except OSError:
        raise LoiKiemE6(THIEU, 2) from None
    ghim = re.findall(r"\| `DANH_MUC_THAM_SO.xlsx` \|[^\n]*?`([0-9a-f]{64})`", nguon)
    if ghim != [BAM_XLSX_CU] or hashlib.sha256(raw).hexdigest() != BAM_XLSX_CU:
        raise LoiKiemE6(SAI_BAM, 3)
    try:
        dm = e1.doc_danh_muc(raw)
        with io.BytesIO(raw) as f:
            nguyen = xlsx_mini.read_xlsx(f)
        dong_cu, params, header, mac_dinh = doc_bo_cu(goc / "tham-chieu/DANH_MUC_THAM_SO.xlsx")
        # Header và 370 ô kiểm nguyên văn; E1 có strip nên phải so ngược với bytes ô.
        can = [header] + dong_nguyen_van(dm.cac_dong)
        if (len(dm.cac_dong) != 37 or list(dm.cac_dong[0]) != e1.KHOA
                or [r["ma"] for r in dm.cac_dong] != [r[0] for r in mac_dinh]
                or nguyen != can or nguyen[0] != e1.HEADER
                or json_bytes(dong_cu) != json_bytes(dm.cac_dong)
                or json_bytes(params) != json_bytes(dm.tham_so)):
            raise LoiKiemE6("Nội dung bộ tham số đối chiếu E6 khác nguồn.", 1)
    except (ValueError, TypeError, KeyError):
        raise LoiKiemE6("Nội dung bộ tham số đối chiếu E6 khác nguồn.", 1) from None
    return dm, {"bam_xlsx": bam_bytes(raw), "bam_noi_dung_e1": dm.ma_bam_noi_dung,
                "bam_snapshot_json_DEMO": bam_bytes(json_bytes(tao_snapshot(dm))),
                "bam_ma_nguon_cu_LF": {ten: bam_bytes((GOC / ten).read_bytes().replace(b"\r\n", b"\n"))
                                       for ten in CAC_TEP_NGUON},
                "so_ma": len(dm.cac_dong), "so_cot": len(e1.KHOA),
                "nguyen_van_10_cot": True, "thu_tu_37_ma": True}


def tao_snapshot(dm, module="DEMO-crm"):
    return {"phien_ban": 1, "module": module, "loai_hop_dong": "XD",
            "phien_ban_bo": "DEMO-E6-1", "bam_tep_goc": "sha256:" + BAM_XLSX_CU,
            "ma_bam_noi_dung": dm.ma_bam_noi_dung,
            "cac_dong": deepcopy(dm.cac_dong), "quy_tac": deepcopy(dm.quy_tac)}


def chay_module(docx_raw, tham_so, du_lieu_ai, *, app=None):
    core, app = CoreGia(), app or app_tx3()

    def chay(ma, vao, ts=None):
        kq = core.chay_thu(app, ma, vao, ts)
        if kq["trang_thai"] != "XONG":
            raise LoiKiemE6("Đường module không hoàn tất đối chiếu E6.", 1)
        return kq["ket_qua"]

    bo, dm, bam = doc_bo(tham_so)
    tep = core.them_tep("DEMO-hop-dong.docx", docx_raw,
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    doc = chay("trich.doc_docx@1", {"loai": "tep", "tep": tep})
    yc = chay("trich.chuan_bi@1", doc, tham_so)
    ai = ai_demo(yc, deepcopy(du_lieu_ai))
    bang = chay("trich.hau_kiem@1", ai)["bang_trich_xuat"]
    if not (bang["module"] == bo["module"] and bang["phien_ban_bo"] == bo["phien_ban_bo"]
            and bang["loai_hop_dong"] == bo["loai_hop_dong"]
            and bang["bam_bo_tham_so"] == bam
            and bang["ma_bam_noi_dung"] == dm.ma_bam_noi_dung):
        raise LoiKiemE6("Metadata module không khớp đối chiếu E6.", 1)
    r = yc["yeu_cau_ai"]
    return cac_byte({"bo_10_cot": [e1.HEADER] + dong_nguyen_van(dm.cac_dong),
        "tham_so": dm.tham_so, "van_ban": r["tai_lieu"],
        "cau_hoi": [{"loai": "hoi_trich", "prompt": r["prompt"],
                     "tai_lieu": r["tai_lieu"], "truong": r["khuon_tra_loi"]["required"],
                     "khuon": r["khuon_tra_loi"]}],
        "bang": bang["bang"], "phan_hoi": [{"loai": "hoi_trich", "du_lieu": ai["tra_loi_ai"]["du_lieu"]}]}), {
            "module": bo["module"], "phien_ban_bo": bo["phien_ban_bo"],
            "bam_snapshot_json": bam, "so_dong": len(bang["bang"])}


def byte_cu(v):
    return cac_byte({"bo_10_cot": [v["header"]] + dong_nguyen_van(v["dong"]),
        "tham_so": v["tham_so"], **{k: v[k] for k in ("van_ban", "cau_hoi", "bang", "phan_hoi")}})


def _doc_ghim(goc, spec):
    try:
        # Chỉ nguồn trong thư mục manifest tại tham-chieu, không đường máy/symlink.
        ten = spec["tep"]
        rel = Path(ten)
        if not isinstance(ten, str) or rel.is_absolute() or ".." in rel.parts or ":" in ten or "\\" in ten:
            raise ValueError()
        p = goc / rel
        if any(q.is_symlink() for q in [p, *p.parents]) or not p.resolve().is_relative_to(goc.resolve()):
            raise ValueError()
        raw = p.read_bytes()
    except (OSError, ValueError, TypeError, KeyError):
        raise LoiKiemE6(THIEU, 2) from None
    if spec.get("bam") != bam_bytes(raw):
        raise LoiKiemE6(SAI_BAM, 3)
    return raw


def kiem_manifest(manifest, *, goc=ENGINE):
    dm, report = kiem_nguon(goc)
    report.update(trang_thai="chua_kiem", ai_that=0, cloud=0, cac_ca=[])
    try:
        p = Path(manifest)
        ref = goc / "tham-chieu"
        if not p.resolve().is_relative_to(ref.resolve()) or p.is_symlink():
            raise LoiKiemE6(THIEU, 2)
        m = doc_json(p.read_text(encoding="utf-8"))
        if (m.get("phien_ban") != 1 or m.get("nhan") != "DEMO"
                or not isinstance(m.get("chap_nhan_lead"), str) or not m["chap_nhan_lead"].strip()
                or {c["loai"] for c in m["cac_ca"]} != {"thuong", "track_changes"}
                or len({c["ma"] for c in m["cac_ca"]}) != len(m["cac_ca"])):
            raise LoiKiemE6(THIEU, 2)
        modules = set()
        for c in m["cac_ca"]:
            raw = {k: _doc_ghim(p.parent, c[k]) for k in ("docx", "ai", "tham_so", "vang")}
            ts, ai, vang = (doc_json(raw[k]) for k in ("tham_so", "ai", "vang"))
            bo, _, _ = doc_bo(ts)
            # Giữ nguyên bộ module; sai khác sẽ có offset byte, không điền bộ đúng.
            # Quy tắc ngoài 10 cột và băm nguồn kiểm riêng, không được bỏ sót.
            if bo["quy_tac"] != dm.quy_tac or bo.get("bam_tep_goc") != "sha256:" + BAM_XLSX_CU:
                raise LoiKiemE6("Bộ module khác nguồn đối chiếu E6.", 1)
            modules.add(bo["module"])
            cu = chay_mac_dinh_chuyen_tiep(goc / "tham-chieu/DANH_MUC_THAM_SO.xlsx", raw["docx"], ai["cu"])
            if (c["loai"] == "track_changes") != (cu["track_changes"] > 0):
                raise LoiKiemE6(THIEU, 2)
            old = byte_cu(cu)
            gold = {k: v.encode("utf-8") for k, v in vang.items()}
            base = so_cac_phan(gold, old)
            new, meta = chay_module(raw["docx"], ts, ai["moi"])
            diff = so_cac_phan(old, new)
            report["cac_ca"].append({"ma": c["ma"], "loai": c["loai"],
                "ban_vang_voi_nguon": base, "mac_dinh_voi_module": diff, "metadata": meta})
        if len(modules) < 2:
            raise LoiKiemE6(THIEU, 2)
    except LoiKiemE6 as exc:
        report["loi"] = str(exc)
        report["trang_thai"] = "chua_dat" if exc.ma_thoat == 1 else "chua_kiem"
        return report, exc.ma_thoat
    except LoiNghiepVu:
        report.update(trang_thai="chua_dat", loi="Đường module không hoàn tất đối chiếu E6.")
        return report, 1
    except (OSError, ValueError, KeyError, TypeError, AttributeError, ThieuBangAI):
        report["loi"] = THIEU
        return report, 2
    dat = all(v["trung_byte"] for c in report["cac_ca"]
              for k in ("ban_vang_voi_nguon", "mac_dinh_voi_module") for v in c[k].values())
    report["trang_thai"] = "dat" if dat else "chua_dat"
    return report, 0 if dat else 1


def chan_doan_co_che():
    """DEMO kỹ thuật chưa duyệt; luôn exit 2, kể cả mọi bytes có trùng.

    Không tạo bản vàng hoặc kịch bản nghiệm thu; chỉ định vị khác biệt hiện có.
    """
    from mau_docx import NUM, goi_docx, mau_track, p, so
    dm, report = kiem_nguon()
    report.update(trang_thai="chua_kiem", nhan="DEMO kỹ thuật chưa được lead chấp nhận",
                  ai_that=0, cloud=0, cac_ca=[], loi=THIEU)
    thuong = goi_docx(p("DEMO — Hợp đồng số DEMO-001") + so("Giá trị hợp đồng")
                     + p("Giá trị hợp đồng là 1.000.000 VND."), numbering=NUM)
    ts = {"bo_tham_so_json": json_bytes(tao_snapshot(dm)).decode("utf-8"),
          "prompt": "Chỉ trích từ tài liệu DEMO.", "ma_prompt": "DEMO-E6",
          "phien_ban_prompt": "DEMO-1", "ngan_sach_token_vao": 100000}
    ts["bam_bo_tham_so"] = bam_bytes(ts["bo_tham_so_json"].encode("utf-8"))
    # Câu trả lời rỗng/null chỉ kiểm cơ chế; không chứng nhận chất lượng.
    data = {r["ma"]: {"gia_tri": None, "don_vi": None, "ghi_chu": None, "trich_dan": []}
            for r in dm.cac_dong}
    for ten, raw, so_hoi in (("DEMO-thuong", thuong, 8), ("DEMO-track-changes", mau_track(), 7)):
        tape = {"tim_vi_tri": [{}], "hoi_trich": [[] for _ in range(so_hoi)]}
        cu = chay_mac_dinh_chuyen_tiep(ENGINE / "tham-chieu/DANH_MUC_THAM_SO.xlsx", raw, tape)
        moi, meta = chay_module(raw, ts, data)
        report["cac_ca"].append({"ma": ten, "bam_docx": bam_bytes(raw),
            "bam_bang_ai_gia": bam_bytes(json_bytes({"cu": tape, "moi": data})),
            "track_changes_da_nhan": cu["track_changes"],
            "so_cau_hoi_cu": len(cu["cau_hoi"]), "so_cau_hoi_moi": 1,
            "ket_qua_chan_doan": "chua_dat", "metadata": meta,
            "mac_dinh_voi_module": so_cac_phan(byte_cu(cu), moi)})
    return report, 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ENGINE / "tham-chieu/e6/chap-nhan.json")
    parser.add_argument("--chan-doan", action="store_true", help="DEMO kỹ thuật, luôn chưa kiểm/exit 2")
    args = parser.parse_args(argv)
    try:
        report, code = chan_doan_co_che() if args.chan_doan else kiem_manifest(args.manifest)
    except LoiKiemE6 as exc:
        report, code = {"trang_thai": "chua_dat" if exc.ma_thoat == 1 else "chua_kiem",
                        "loi": str(exc)}, exc.ma_thoat
    except Exception:
        report, code = {"trang_thai": "chua_kiem", "loi": "Công cụ đối chiếu E6 gặp lỗi kiểm."}, 4
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
