"""Đóng băng ví dụ cổng chung từ CoreGia/Local giả; chỉ công cụ test.

Mỗi ref có bytes/băm thật. Fixture tái nạp cùng mã CoreGia, quyền được tiêm
ngoài payload trong tests. CLI SDK chưa có cửa nạp chúng: giữ nguyên lỗi.
"""

from copy import deepcopy
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi/e_tra_cuu"))

from e_tra_cuu.kiem_dau_vao import bam, doc_json, json_chuan
from ho_tro_tc_2 import GOI
from ho_tro_tc_3 import BoCatDoan
from ho_tro_tc_4 import BoAI
from ho_tro_tc_6 import BoHauKiem
from ho_tro_tc_10 import chay_ca, hoi_local, nap_bo


GOC = GOI / "demo/tc-10/cong-chuan"


def dong_goi():
    corpus, _ = nap_bo()
    cac_bo = []
    bo = BoCatDoan()
    bo.nhan()
    cac_bo.append(("cat-doan", bo, bo.giao_cat()))
    bo = BoAI()
    bo.nhan_ai("phan_loai")
    cac_bo.append(("chuan-bi-ai", bo, bo.giao_ai()))
    for tac in ("phan_tich_cau_hoi", "xep_hang_lai"):
        bo = BoHauKiem()
        bo.chuan_bi_hau(tac)
        quote = bo.yc["du_lieu"]["cau_hoi"] if tac == "phan_tich_cau_hoi" else bo.van_ban
        ai, _ = hoi_local(bo, bo.pb_ai, bo.du_lieu_local(), [quote])
        cac_bo.append((tac.replace("_", "-"), bo, bo.giao_hau(ai["ket_qua"])))
    for ma, ten in (("PL-vay", "phan-loai"), ("TL-Local-A", "soan-tra-loi")):
        ca = next(c for c in corpus["kich_ban"] if c["ma"] == ma)
        q = chay_ca(ca, corpus)
        bo = q["bo"]
        i = bo.pl_id if ten == "phan-loai" else bo.soan_id
        cac_bo.append((ten, bo, i))
        if ten == "soan-tra-loi":
            i = next(i for i, v in bo.core._viec.items() if v["nang_luc"] == "tra_cuu.xuat_ket_qua@1")
            cac_bo.append(("xuat-ket-qua", bo, i))

    phieu = doc_json((GOI / "engine.json").read_bytes())
    # Giữ nguyên năm ví dụ nhận yêu cầu, không bỏ ca khó để làm xanh CLI.
    phieu["chay_thu_demo"] = [v for v in phieu["chay_thu_demo"] if v["nang_luc"] == "tra_cuu.nhan_yeu_cau@1"]
    for ten, bo, i in cac_bo:
        target = GOC / ten
        target.mkdir(parents=True, exist_ok=True)
        viec = bo.core._viec[i]
        cap = deepcopy(bo.core.cua.giay_cap[i])
        tep = []
        max_id = max(int(t.rsplit("-", 1)[1]) for t in bo.core._tep)
        for n in range(1, max_id + 1):
            id_tep = f"tep-{n}"
            if id_tep in bo.core._tep:
                name, mime, raw = bo.core._tep[id_tep]
            else:
                # Chỗ mã việc dùng chung bộ đếm SDK: nạp tệp DEMO không tham
                # chiếu để tái lập ID. Không có ref thiếu bytes hoặc băm giả.
                name, mime = "vi-tri-ma-viec-DEMO.json", "application/json"
                raw = json_chuan({"nhan": "DEMO", "muc_dich": "Vị trí mã việc, không phải nguồn nghiệp vụ."})
            path = target / (id_tep + "." + ("txt" if mime == "text/plain" else "json"))
            path.write_bytes(raw)
            tep.append({"tep": {"tep_id": id_tep, "ten": name, "mime": mime, "kich_thuoc": len(raw)},
                        "bam": bam(raw), "duong_dan": path.relative_to(GOI).as_posix()})
        vd = {"nang_luc": viec["nang_luc"], "ten": "TC10 DEMO tệp con — " + ten,
              "dau_vao": deepcopy(viec["dau_vao"]), "tham_so": deepcopy(viec["tham_so"])}
        fixture = {"nhan": "DEMO", "vi_du": vd, "cau_hinh": deepcopy(bo.cau_hinh),
                   "giay_cap": cap, "tep": tep, "da_duyet_nghiep_vu": False}
        raw = (json.dumps(fixture, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
        (target / "fixture-DEMO.json").write_bytes(raw)
        phieu["chay_thu_demo"].append(vd)
    (GOI / "engine.json").write_bytes((json.dumps(phieu, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    files = {p.relative_to(GOC).as_posix(): bam(p.read_bytes()) for p in sorted(GOC.rglob("*"))
             if p.is_file() and p.name != "bam-DEMO.json"}
    (GOC / "bam-DEMO.json").write_bytes((json.dumps(files, indent=2) + "\n").encode("ascii"))
    print(f'Đã đóng băng {len(cac_bo)} ví dụ tệp con; tổng {len(phieu["chay_thu_demo"])} ví dụ cổng chuẩn.')


if __name__ == "__main__":
    dong_goi()
