"""Tái nạp fixture tệp con/cấu hình/quyền, không sửa CLI hoặc runtime."""

from copy import deepcopy

from kho_tri_thuc_sdk.engine import Engine

from e_tra_cuu import chay
from e_tra_cuu.kiem_dau_vao import bam, doc_json
from ho_tro_tc_2 import CoreGiaTepCon, GOI


def chay_vi_du(vd):
    root = GOI / "demo/tc-10/cong-chuan"
    pin = doc_json((root / "bam-DEMO.json").read_bytes())
    for ten, checksum in pin.items():
        assert bam((root / ten).read_bytes()) == checksum
    bo = next(doc_json(p.read_bytes()) for p in root.glob("*/fixture-DEMO.json")
              if doc_json(p.read_bytes())["vi_du"] == vd)
    assert not bo["da_duyet_nghiep_vu"]
    core = CoreGiaTepCon()
    app = Engine(deepcopy(chay.app.phieu), thu_muc_goi=GOI)
    core.nap_engine(app)
    core.dat_cau_hinh(app.ma, bo["cau_hinh"])
    app.cua_nguon = core.cua
    chay.dang_ky_nang_luc(app)
    for ref in bo["tep"]:
        raw = (GOI / ref["duong_dan"]).read_bytes()
        assert bam(raw) == ref["bam"]
        t = ref["tep"]
        assert core.them_tep(t["ten"], raw, t["mime"]) == t
    cap = deepcopy(bo["giay_cap"])
    for id_tep, ref in cap["tep"].items():
        raw = core.doc_tep(id_tep)
        assert bam(raw) == ref["bam"] and len(raw) == ref["tep"]["kich_thuoc"]
    i = core.giao_viec(vd["nang_luc"], deepcopy(vd["dau_vao"]), deepcopy(vd["tham_so"]),
                       phap_nhan_id=cap["ngu_canh_core"]["phap_nhan_id"])
    core.tep_duoc_mo[i] = set(cap["tep"])
    core.cua.giay_cap[i] = cap
    core.chay(app)
    kq = core.xem(i)
    if kq["trang_thai"] == "XONG":
        ra = kq["ket_qua"]
        if ra["loai"] == "ho_so_tra_cuu":
            h = ra["ho_so_tra_cuu"]
            raw = core.doc_tep(h["ho_so"]["tep_id"])
            assert bam(raw) == h["bam_ho_so"] and len(raw) == h["ho_so"]["kich_thuoc"]
        elif ra["loai"] == "yeu_cau_ai":
            h = ra["yeu_cau_ai"]["chuyen_tiep"]["tra_cuu"]
            assert bam(core.doc_tep(h["ho_so"]["tep_id"])) == h["bam_ho_so"]
        else:
            assert ra["loai"] == "truong"
            t = ra["truong"]["tep_json"]
            assert len(core.doc_tep(t["tep_id"])) == t["kich_thuoc"]
    return {"ten": vd["ten"], **kq}
