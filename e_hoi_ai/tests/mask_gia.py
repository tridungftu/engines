"""Fixture DEMO ngoài gói, CoreGia giữ snapshot thật trong bộ nhớ."""
from copy import deepcopy
from hashlib import sha256

from e_hoi_ai.hoi_mask import KHUON_MASK
from e_hoi_ai.khuon_json import json_chuan
from local_gia import TAI_LIEU


def bam(raw):
    return "sha256:" + sha256(raw).hexdigest()


def snapshot(yc):
    goc = yc["tai_lieu"]
    profile = {"phien_ban": 1, "loai": ["nguoi", "to_chuc", "dia_chi"],
               "muc": ["chac", "nghi_ngo"], "he_offset": "unicode_code_point",
               "tran_doan": 8000, "tran_span": 300, "tran_so_doan": 128}
    return json_chuan({"nhan": "DEMO", "goc": goc, "da_che_quy_tac": goc,
                       "map": [{"bat_dau": 0, "ket_thuc": len(goc), "loai": "giu_nguyen"}],
                       "profile": profile, "prompt": yc["prompt"], "khuon": yc["khuon_tra_loi"],
                       "doan": [{"bat_dau": 0, "ket_thuc": len(goc)}]})


def yeu_cau_demo(goc=None, core=None):
    yc = {"phien_ban": 1, "ma_prompt": "demo.mask_2c", "phien_ban_prompt": "DEMO-1",
          "prompt": "DEMO: Liệt kê mọi người, tổ chức, địa chỉ và từng lần xuất hiện, giữ nguyên văn và offset; nghi vấn thì đánh dấu nghi_ngo.",
          "tai_lieu": TAI_LIEU if goc is None else goc, "khuon_tra_loi": deepcopy(KHUON_MASK),
          "bat_buoc_trich_dan": True, "model_uu_tien": None, "chuyen_tiep": {}}
    profile = {"phien_ban": 1, "loai": ["nguoi", "to_chuc", "dia_chi"],
               "muc": ["chac", "nghi_ngo"], "he_offset": "unicode_code_point",
               "tran_doan": 8000, "tran_span": 300, "tran_so_doan": 128}
    p = {"phien_ban": 1, "ma_yeu_cau": "DEMO-mask-ai-9", "nha_cung_cap_bat_buoc": "local",
         "ho_so": {"tep_id": "DEMO-snapshot-ai-9", "ten": "DEMO-snapshot-ai-9.json", "mime": "application/json"},
         "phien_ban_map": 1, "chi_so_doan": 0, "so_doan": 1, "bat_dau_doan": 0,
         "he_offset": "unicode_code_point", "bam_profile": bam(json_chuan(profile))}
    yc["chuyen_tiep"]["mask_2c"] = p
    raw = snapshot(yc)
    p.update(bam_goc=bam(yc["tai_lieu"].encode("utf-8")),
             bam_da_che_quy_tac=bam(yc["tai_lieu"].encode("utf-8")),
             bam_doan=bam(yc["tai_lieu"].encode("utf-8")), ket_thuc_doan=len(yc["tai_lieu"]),
             bam_prompt=bam(yc["prompt"].encode("utf-8")),
             bam_khuon=bam(json_chuan(yc["khuon_tra_loi"])), bam_ho_so=bam(raw))
    p["ho_so"]["kich_thuoc"] = len(raw)
    if core is not None:
        p["ho_so"] = core.them_tep(p["ho_so"]["ten"], raw, "application/json")
    return yc


def phan_hoi_demo():
    # Gold DEMO được ghim vị trí từng lần; không phải detector của model.
    return {"da_quet_het": True, "thuc_the": [{
        "loai": "to_chuc", "nguyen_van": "Công ty DEMO Ánh Dương", "bat_dau": 29,
        "ket_thuc": 51, "muc": "chac",
    }]}


