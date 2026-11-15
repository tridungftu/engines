"""Đo T3 ngoài engine. Mặc định CHẠY KHÔ; chỉ --that cùng --url mới gọi Local."""
import argparse
from copy import deepcopy
from pathlib import Path
import sys

from ho_tro_do import (ChuaRo, LocalGia, LocalThat, LoiDo, VAI_TRO, bam, bao_loi_artifact, cfg_gia,
                      cau_hinh_model, dat_ngan_sach_trich, doc_model_spec, doc_artifact, doc_bo_demo, do_mot_ca,
                      co_du_so_runtime, corpus_t3, ghi_artifact, json_bytes, luc, tao_yeu_cau_t3)


def kiem_bien_ban(e6=None, n1=None):
    if not e6 and not n1:
        return None, None
    _, bam_bo_demo = doc_bo_demo()
    e = n = None
    if e6:
        e, _ = doc_artifact(e6)
        if (e.get("trang_thai") != "dat" or e.get("bam_manifest") != bam_bo_demo
                or e.get("chap_nhan_lead") != "đã duyệt"):
            raise LoiDo("Biên bản E6 chưa đạt hoặc khác bộ DEMO đã ghim.")
    if n1:
        n, _ = doc_artifact(n1)
        if (n.get("phep_do") != "N1" or n.get("che_do") != "that"
                or n.get("trang_thai") != "dat" or n.get("bam_bo_demo") != bam_bo_demo
                or not n.get("bam_nen")):
            raise LoiDo("Biên bản N1 thật chưa đạt hoặc khác nền/dữ liệu đã ghim.")
    return e, n


def chay(configs, local, *, that=False, e6=None, n1=None):
    report = {"phien_ban": 1, "nhan": "DEMO", "phep_do": "T3", "luc_utc": luc(),
              "che_do": "that" if that else "chay_kho", "trang_thai": "chua_do",
              "so_luot_cloud": 0, "so_luot_local_that": 0, "cac_ca": [],
              "phuong_an_neu_khong_dat": {"b_batch": "12–18 giờ công ước tính riêng, chờ duyệt",
                                         "c_nhieu_buoc": "18–24 giờ công ước tính riêng, chờ duyệt"}}
    if len(configs) != 3 or {c["vai_tro"] for c in configs} != set(VAI_TRO) or len({c["id"] for c in configs}) != 3:
        raise LoiDo("T3 cần đúng ba ID riêng: Qwen3 8B, gpt-oss 20B và Gemma đã phát hiện.")
    e, n = kiem_bien_ban(e6, n1) if that else (None, None)
    ids = local.phat_hien()
    if any(c["id"] not in ids for c in configs):
        raise LoiDo("Chưa phát hiện đủ ba ID model đã ghim; không gửi tài liệu.")
    try:
        for cfg in configs:
            for n in (1, 20, 60):
                try:
                    core, app, req, bam_prompt_goc = tao_yeu_cau_t3(n, cfg["id"], cfg.get("ngan_sach_trich", 100000))
                except LoiDo as exc:
                    report["cac_ca"].append({"mau": "DEMO-" + str(n), "model": cfg["id"],
                        "vai_tro": cfg["vai_tro"], "trang_thai": "khong_dat", "qua_hau_kiem": False,
                        "loi": str(exc), "mau_so": 37, "so_o_tra": None,
                        "so_o_co_dan_chung_hop_le": None, "so_can_soat": None,
                        "token_vao": None, "token_ra": None, "token_reasoning": None,
                        "thoi_gian_giay": None, "tu_choi": True, "nguon_tu_choi": "chuan_bi",
                        "tran": None, "cat": None})
                    continue
                so, _ = do_mot_ca(core, app, req, cfg, local)
                # Khuôn Phụ lục A nội tuyến dẫn chứng; TX-2 dùng thêm $defs/dan_chung.
                # Báo riêng hai băm, không coi prompt/khuôn thực giống mẫu đếm lịch sử.
                khuon_goc = deepcopy(req["yeu_cau_ai"]["khuon_tra_loi"])
                khuon_goc["$defs"]["o"]["properties"]["trich_dan"]["items"] = khuon_goc["$defs"].pop("dan_chung")
                prompt_goc = corpus_t3()[1]
                so.update(mau="DEMO-" + str(n), vai_tro=cfg["vai_tro"],
                          bam_prompt_phu_luc_a=bam_prompt_goc, bam_khuon_phu_luc_a=bam(khuon_goc),
                          token_uoc_luong_phu_luc_a=(len(prompt_goc) + len(req["yeu_cau_ai"]["tai_lieu"])
                                                     + len(json_bytes(khuon_goc).decode("utf-8")) + 3) // 4)
                report["cac_ca"].append(so)
    except ChuaRo as exc:
        report.update(trang_thai="chua_ro", ma_tuong_quan=exc.ma_tuong_quan,
                      ly_do="Nguồn đã nhận việc nhưng chưa trả; dừng phép đo, không gửi lại mù.")
        report["cac_ca"].append(getattr(exc, "so_do", {"trang_thai": "chua_ro"}))
        report["so_luot_local_that"] = local.so_gui if that else 0
        return report, 2
    report["so_luot_local_that"] = local.so_gui if that else 0
    if not that:
        report.update(trang_thai="chay_kho", ket_luan="T3 chưa đo; chỉ kiểm công cụ bằng Local giả.")
        return report, 0 if all(c["qua_hau_kiem"] for c in report["cac_ca"]) else 1
    report.update(bam_bien_ban_e6=doc_artifact(e6)[1] if e6 else None,
                  bam_bien_ban_n1=doc_artifact(n1)[1] if n1 else None)
    for c in report["cac_ca"]:
        du_so = co_du_so_runtime(c)
        # Một N1 duy nhất chứng minh đúng model/cấu hình được đo, không suy sang model khác.
        c["du_dieu_kien_mot_luot"] = bool(e and n and du_so and c.get("qua_hau_kiem")
            and c["so_o_tra"] == 37 and c["so_o_co_dan_chung_hop_le"] == 37
            and c["so_can_soat"] == 0 and not any(c[k] for k in ("tu_choi", "tran", "cat"))
            and c["model"] == n.get("model") and c["bam_cau_hinh"] == n.get("bam_cau_hinh"))
    report["pham_vi_du_dieu_kien"] = [{"model": c["model"], "mau": c["mau"],
                                       "bam_cau_hinh": c["bam_cau_hinh"]}
                                      for c in report["cac_ca"] if c["du_dieu_kien_mot_luot"]]
    report["trang_thai"] = "dat_theo_pham_vi" if report["pham_vi_du_dieu_kien"] else "chua_kiem"
    report["ket_luan"] = "Chỉ áp dụng cho tải/cấu hình đã đo; thiếu số/biên bản thì chưa kiểm."
    return report, 0 if report["pham_vi_du_dieu_kien"] else 2


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--that", action="store_true")
    p.add_argument("--url")
    p.add_argument("--model-json", action="append", default=[], help="JSON cấu hình đã xác minh, mỗi model một mục.")
    p.add_argument("--model-spec", action="append", default=[], help="vai_tro,ID,context,ra,boc,runtime,quant,bam_bien_ban")
    p.add_argument("--ngan-sach-trich", type=int, help="Trần cấu hình Trích xuất đã ghim; chạy thật phải cung cấp.")
    p.add_argument("--bien-ban-e6", type=Path)
    p.add_argument("--bien-ban-n1", type=Path)
    p.add_argument("--dau-ra", type=Path)
    args = p.parse_args(argv)
    try:
        if args.that and (not args.url or not args.dau_ra or not (args.model_json or args.model_spec) or args.ngan_sach_trich is None):
            raise LoiDo("Chạy thật cần --url, ba cấu hình model, --ngan-sach-trich đã ghim và --dau-ra.")
        if args.dau_ra and args.dau_ra.exists():
            raise LoiDo("Artifact đã tồn tại; không ghi đè kết quả phép đo trước.")
        configs = [cau_hinh_model(x) for x in args.model_json] + [doc_model_spec(x) for x in args.model_spec]
        configs = configs or [cfg_gia(v) for v in VAI_TRO]
        dat_ngan_sach_trich(configs, args.ngan_sach_trich if args.ngan_sach_trich is not None else 100000)
        local = LocalThat(args.url, configs) if args.that else LocalGia(configs)
        report, code = chay(configs, local, that=args.that, e6=args.bien_ban_e6, n1=args.bien_ban_n1)
        if args.dau_ra:
            ghi_artifact(args.dau_ra, report)
        print("T3: " + report["trang_thai"] + "; " + str(len(report["cac_ca"])) + " tải/model; Cloud: 0.")
        if not args.that:
            print("CHẠY KHÔ: Local giả, không mạng. T3 chưa đo; token runtime/thời gian để null.")
        return code
    except (LoiDo, ChuaRo) as exc:
        print(str(exc), file=sys.stderr)
        bao_loi_artifact(args.dau_ra, "T3", str(exc))
        return exc.ma_thoat if isinstance(exc, LoiDo) else 2
    except Exception:
        cau = "Không hoàn tất phép đo T3; chưa có kết luận đạt. Kiểm dữ liệu và cấu hình đo."
        print(cau, file=sys.stderr)
        bao_loi_artifact(args.dau_ra, "T3", cau)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
