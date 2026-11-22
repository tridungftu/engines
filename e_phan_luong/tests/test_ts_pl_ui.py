"""TS-PL: KttCore giả (Node, không mạng) và đối chiếu bộ đọc Python thật."""
from decimal import Decimal
import json
from pathlib import Path
import re
import shutil
import subprocess

import pytest

from e_phan_luong.doc_bang import _doc_khuon
from e_phan_luong.loi import LoiNghiepVu
from e_phan_luong.nguong import doc_nguong
from e_phan_luong.phan_loai import doc_bo_phan_loai, doc_danh_muc_loai
from e_phan_luong.ty_le import doc_chinh_sach

THU_MUC = Path(__file__).resolve().parent
GOI = THU_MUC.parent / "goi" / "e_phan_luong"
NODE = shutil.which("node")


def chay_node(*lenh):
    assert NODE, "Cần Node để nghiệm thu TS-PL; không bỏ qua test UI."
    kq = subprocess.run([NODE, *map(str, lenh)], capture_output=True, text=True,
                        encoding="utf-8", timeout=90, cwd=THU_MUC.parents[1])
    # Data URL chứa mã UI, rút gọn stack để báo lỗi dễ đọc.
    loi = re.sub(r"data:text/javascript;base64,[A-Za-z0-9+/=]+", "ui/TS-PL", kq.stdout + kq.stderr)
    assert kq.returncode == 0, loi
    return kq.stdout


def test_ts_pl_node_kttcore_gia_khong_mang():
    chay_node("--test", THU_MUC / "ui" / "tham_so.test.mjs")


def test_ts_pl_json_xuat_ra_khop_bo_doc_hien_hanh():
    ds = json.loads(chay_node(THU_MUC / "ui" / "xuat_mau.mjs"))
    assert len(ds) >= 13
    for ca in ds:
        ts = ca["tham_so"]
        try:
            danh_muc = doc_danh_muc_loai(ts["danh_muc_loai_json"])
            doc_bo_phan_loai(ts["bo_phan_loai_json"], danh_muc)
            if ts["nguong_json"]:
                ng = doc_nguong(None, ts["nguong_json"])
                if "999999999999999999.123456" in ts["nguong_json"]:
                    assert ng.pm.so == Decimal("999999999999999999.123456")
            doc_chinh_sach(ts["chinh_sach_json"])
            if ts["khuon_cot_json"]:
                _doc_khuon(ts["khuon_cot_json"])
            hop_le = True
        except LoiNghiepVu:
            hop_le = False
        assert hop_le == ca["hop_le"], ca["ten"]


def test_ts_pl_khai_du_kha_nang_khong_them_cau_hinh_bi_mat():
    phieu = json.loads((GOI / "engine.json").read_text(encoding="utf-8"))
    khai = json.loads((GOI / "KHAI-SDK-2.1.json").read_text(encoding="utf-8"))
    assert not (GOI / "cau_hinh.schema.json").exists()
    assert phieu["bi_mat"] == []
    assert "giao_dien_tham_so" not in phieu
    man = khai["giao_dien_tham_so"]
    assert len(man) == len(phieu["nang_luc"]) == 5
    for nl in phieu["nang_luc"]:
        ts_json = {t["ma"] for t in nl["tham_so"] if t["ma"].endswith("_json")}
        muc = next(x for x in man if x["nang_luc"] == nl["ma"])
        assert set(muc["tham_so"]) == ts_json
        assert (GOI / muc["tep"]).is_file()
        for ts in nl["tham_so"]:
            if ts["ma"] in ts_json:
                assert "Mẫu DEMO:" in ts["mo_ta"]
                assert "trống" in ts["mo_ta"].lower()
                assert len(ts["mo_ta"]) <= 500
    assert "luu_tham_so" in khai["hop_dong_du_kien_D2"]
