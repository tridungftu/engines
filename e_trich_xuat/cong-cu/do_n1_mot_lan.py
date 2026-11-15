"""N1 đúng một lượt trên bộ DEMO/nền đã duyệt; chạy khô không phải phép đo N1."""
import argparse
from pathlib import Path
import sys

from ho_tro_do import (BAM_NGUON_CHAM, CACH_CHAM, ChuaRo, LocalGia, LocalThat, LoiDo, bam, bam_cau_hinh, bao_loi_artifact,
                      cau_hinh_model, cfg_gia, cham_n1, dat_ngan_sach_trich, doc_artifact, doc_bo_demo, doc_json, doc_model_spec,
                      co_du_so_runtime, do_mot_ca, dong_goi, ghi_artifact, kiem_context, luc, ma_37, yeu_cau_n1)


def kiem_nen(tep, bam_ghim, cfg, cac_ca, bam_bo_demo):
    nen, b = doc_artifact(tep)
    if b != bam_ghim:
        raise LoiDo("Nền N1 không khớp băm người chạy đã ghim.")
    if (nen.get("nhan") != "DEMO" or nen.get("chap_nhan_lead") != "đã duyệt"
            or not nen.get("bien_ban_lead") or nen.get("cach_cham") != CACH_CHAM
            or nen.get("bam_nguon_cham") != "sha256:" + BAM_NGUON_CHAM
            or nen.get("bam_bo_demo") != bam_bo_demo or nen.get("model") != cfg["id"]
            or nen.get("bam_cau_hinh") != bam_cau_hinh(cfg)
            or not isinstance(nen.get("cac_ca"), list)
            or [c.get("ma") for c in nen["cac_ca"]] != [c["ma"] for c in cac_ca]):
        raise LoiDo("Thiếu nền N1 được lead chấp nhận hoặc nền khác dữ liệu/model/cấu hình.")
    for c, n in zip(cac_ca, nen["cac_ca"]):
        if n.get("bam_nguon") != c["bam"]:
            raise LoiDo("Nguồn/đáp án N1 khác bộ nền đã chấp nhận.")
        t = n.get("cham", {})
        rows = t.get("tham_so", [])
        if (len(rows) != 37 or type(t.get("da_do")) is not int or t["da_do"] <= 0
                or [r.get("ma") for r in rows] != [r[0] for r in ma_37()]
                or type(t.get("dat")) is not int or not 0 <= t["dat"] <= t["da_do"]
                or t.get("ty_le") != t["dat"] / t["da_do"]
                or any(r.get("da_do") not in (0, 1) or type(r.get("da_do")) is not int
                       or (r.get("dat") not in (0, 1) if r["da_do"] else r.get("dat") is not None) for r in rows)
                or sum(r["da_do"] for r in rows) != t["da_do"]
                or sum(r["dat"] or 0 for r in rows) != t["dat"]):
            raise LoiDo("Nền N1 thiếu số đo hoặc mẫu số da_do hợp lệ.")
    return nen, b


def ghim_yeu_cau(req, core):
    r = req["yeu_cau_ai"]
    hs = doc_json(core.doc_tep(r["chuyen_tiep"]["trich_xuat"]["ho_so_hau_kiem"]["tep_id"]))
    return {"bam_bo": r["chuyen_tiep"]["trich_xuat"]["bam_bo_tham_so"],
            "bam_cau_hinh_trich_xuat": bam(hs["cau_hinh_da_ghim"]["gia_tri"]),
            "bam_prompt": bam(r["prompt"].encode("utf-8")),
            "bam_tai_lieu": bam(r["tai_lieu"].encode("utf-8")), "bam_khuon": bam(r["khuon_tra_loi"])}


def giu_luot_n1(tep_nen, bam_nen):
    dau = Path(tep_nen).resolve().parent / ("N1-" + bam_nen[7:] + ".da-nhan.json")
    ghi_artifact(dau, {"nhan": "DEMO", "phep_do": "N1", "bam_nen": bam_nen,
                       "trang_thai": "da_nhan_mot_lan", "luc_utc": luc()})
    return dau


def chay(cac_ca, bam_bo_demo, cfg, local, *, that=False, nen=None, bam_nen=None):
    report = {"phien_ban": 1, "nhan": "DEMO", "phep_do": "N1", "luc_utc": luc(),
              "che_do": "that" if that else "chay_kho", "trang_thai": "chua_kiem",
              "model": cfg["id"], "bam_cau_hinh": bam_cau_hinh(cfg), "bam_bo_demo": bam_bo_demo,
              "bam_nen": bam_nen, "cach_cham": CACH_CHAM, "bam_nguon_cham": "sha256:" + BAM_NGUON_CHAM,
              "so_luot_cloud": 0,
              "so_luot_local_that": 0, "cac_ca": [], "so_lan_n1": 1 if that else 0}
    if cfg["id"] not in local.phat_hien():
        raise LoiDo("Không phát hiện đúng ID model N1 đã ghim; không gửi tài liệu.")
    try:
        for i, c in enumerate(cac_ca):
            core, app, req = yeu_cau_n1(c, cfg)
            # So băm điều kiện trước gửi; không thấy kết quả rồi mới chọn bộ/cấu hình.
            ghim = ghim_yeu_cau(req, core)
            if that and nen["cac_ca"][i].get("ghim") != ghim:
                raise LoiDo("Prompt/tài liệu/khuôn/bộ N1 khác nền đã ghim; không gửi.")
            so, bang = do_mot_ca(core, app, req, cfg, local, vang=c["vang"])
            cham = cham_n1(c["vang"], bang["bang"] if bang else None)
            row = {"ma": c["ma"], "bam_nguon": c["bam"], "ghim": ghim, "so_do": so, "cham": cham}
            if that:
                cu = nen["cac_ca"][i]["cham"]
                # Không cho tỷ lệ trên một tập con thuận lợi thay mẫu số/mã nền.
                row["cung_mau_so"] = ([(r["ma"], r["da_do"]) for r in cham["tham_so"]]
                                        == [(r["ma"], r["da_do"]) for r in cu["tham_so"]])
                row["khong_thap_hon_nen"] = bool(row["cung_mau_so"] and cham["ty_le"] is not None
                                                  and cham["ty_le"] >= cu["ty_le"])
            report["cac_ca"].append(row)
            if not bang:
                break  # Không chạy lại hoặc hỏi nhiều vòng khi có lỗi.
    except ChuaRo as exc:
        report.update(trang_thai="chua_ro", ma_tuong_quan=exc.ma_tuong_quan,
                      ly_do="Nguồn đã nhận nhưng chưa trả; giữ dấu một lần, không tự gửi lại.")
        report["so_luot_local_that"] = local.so_gui if that else 0
        return report, 2
    report["so_luot_local_that"] = local.so_gui if that else 0
    if not that:
        report.update(trang_thai="chay_kho", ket_luan="N1 chưa kiểm; số chấm Local giả không phải nền thật.")
        return report, 0 if len(report["cac_ca"]) == len(cac_ca) and all(c["so_do"]["qua_hau_kiem"] for c in report["cac_ca"]) else 1
    dat = len(report["cac_ca"]) == len(cac_ca) and all(c["khong_thap_hon_nen"]
        and c["cham"]["da_do"] == 37
        and c["so_do"]["qua_hau_kiem"] and c["so_do"]["so_o_tra"] == 37
        and co_du_so_runtime(c["so_do"])
        for c in report["cac_ca"])
    report["trang_thai"] = "dat" if dat else "chua_dat"
    return report, 0 if dat else 1


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--that", action="store_true")
    p.add_argument("--url")
    nhom = p.add_mutually_exclusive_group()
    nhom.add_argument("--model-json")
    nhom.add_argument("--model-spec")
    p.add_argument("--bo-demo", type=Path)
    p.add_argument("--ngan-sach-trich", type=int, help="Trần cấu hình Trích xuất đã ghim; chạy thật phải cung cấp.")
    p.add_argument("--nen", type=Path)
    p.add_argument("--bam-nen")
    p.add_argument("--dau-ra", type=Path)
    args = p.parse_args(argv)
    try:
        if args.that and (not all((args.url, args.model_json or args.model_spec, args.nen, args.bam_nen, args.dau_ra)) or args.ngan_sach_trich is None):
            raise LoiDo("N1 chưa kiểm: cần URL, model, --ngan-sach-trich, nền đã duyệt/băm và --dau-ra.")
        if args.dau_ra and args.dau_ra.exists():
            raise LoiDo("Biên bản đã tồn tại; N1 không được chạy lại để chọn kết quả tốt.")
        cfg = (cau_hinh_model(args.model_json) if args.model_json else doc_model_spec(args.model_spec)
               if args.model_spec else cfg_gia("qwen3_8b"))
        dat_ngan_sach_trich([cfg], args.ngan_sach_trich if args.ngan_sach_trich is not None else 100000)
        cac_ca, bam_bo_demo = doc_bo_demo(args.bo_demo)
        nen = b = None
        local = LocalThat(args.url, [cfg]) if args.that else LocalGia([cfg])
        if args.that:
            nen, b = kiem_nen(args.nen, args.bam_nen, cfg, cac_ca, bam_bo_demo)
            if cfg["id"] not in local.phat_hien():
                raise LoiDo("Chưa phát hiện đúng model N1; không tiêu thụ lượt đo.")
            # Kiểm TOÀN bộ tập đầu vào trước lượt POST đầu tiên.
            for i, c in enumerate(cac_ca):
                core, _, req = yeu_cau_n1(c, cfg)
                if ghim_yeu_cau(req, core) != nen["cac_ca"][i].get("ghim"):
                    raise LoiDo("Prompt/tài liệu/khuôn/bộ N1 khác nền đã ghim; không gửi.")
                kiem_context(dong_goi(req, cfg["id"], local.loai, cfg["token_ra_toi_da"]), cfg)
            # Artifact giữ dấu trước mọi POST, độc lập tên --dau-ra. Không xóa sau lỗi.
            giu_luot_n1(args.nen, b)
        report, code = chay(cac_ca, bam_bo_demo, cfg, local, that=args.that, nen=nen, bam_nen=b)
        if args.dau_ra:
            ghi_artifact(args.dau_ra, report)
        print("N1: " + report["trang_thai"] + "; Cloud: 0.")
        if not args.that:
            print("CHẠY KHÔ: không mạng, không tiêu thụ lượt N1. Nền/biên bản máy thật: chưa kiểm.")
        return code
    except (LoiDo, ChuaRo) as exc:
        print(str(exc), file=sys.stderr)
        bao_loi_artifact(args.dau_ra, "N1", str(exc))
        return exc.ma_thoat if isinstance(exc, LoiDo) else 2
    except Exception:
        cau = "N1 chưa kiểm: không hoàn tất phép đo; giữ dấu đã nhận nếu có, không tự chạy lại."
        print(cau, file=sys.stderr)
        bao_loi_artifact(args.dau_ra, "N1", cau)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
