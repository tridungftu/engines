import importlib.util
import io
import json
from pathlib import Path

import pytest
from kho_tri_thuc_sdk import danh_muc_tham_so as e1, xlsx_mini
from kho_tri_thuc_sdk.engine import LoiNghiepVu

p = Path(__file__).resolve().parents[1] / "ban-giao-module/snapshot.py"
spec = importlib.util.spec_from_file_location("tx5_snapshot", p)
tx5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tx5)


def excel(rows):
    f = io.BytesIO()
    xlsx_mini.write_xlsx(f, {"Danh_muc": {"rows": rows}})
    return f.getvalue()


def dong(ma="TT-01", dung="Có"):
    return [ma, "DEMO", "Ngày 2026-10-30; 1.000.000 VND", "ngày", "", dung, 1, "", "", "Không"]


def tao(raw, module="module_a", version="v1"):
    return tx5.tao_snapshot(raw, module=module, loai_hop_dong="DEMO", phien_ban_bo=version)


def test_giu_nguyen_e1():
    raw = excel([e1.HEADER, dong(), dong("TT-02", "Không")])
    dm = e1.doc_danh_muc(raw)
    result = tao(raw)
    bo = json.loads(result["bo_tham_so_json"])
    assert bo["cac_dong"] == dm.cac_dong and bo["quy_tac"] == dm.quy_tac
    assert bo["ma_bam_noi_dung"] == dm.ma_bam_noi_dung
    assert bo["bam_tep_goc"] == "sha256:" + dm.ma_bam
    assert "2026-10-30; 1.000.000 VND" in bo["cac_dong"][0]["mo_ta"]
    from e_trich_xuat.tham_so import doc_bo
    assert doc_bo(result)[1].cac_dong == dm.cac_dong


@pytest.mark.parametrize("rows", [[e1.HEADER[:-1], dong()], [e1.HEADER, dong(dung="sai")],
                                  [e1.HEADER, dong(), dong()]])
def test_loi_an_toan(rows):
    raw = excel(rows)
    with pytest.raises(e1.LoiDanhMuc):
        e1.doc_danh_muc(raw)
    with pytest.raises(LoiNghiepVu) as err:
        tao(raw)
    assert err.value.ma == "BO_THAM_SO_KHONG_HOP_LE"
    assert err.value.thong_diep == "Bộ tham số không đúng cấu trúc; hãy kiểm tra bảng Excel."


def test_vuot_va_hash():
    with pytest.raises(LoiNghiepVu) as err:
        tao(b"x" * (e1.GIOI_HAN_TEP + 1))
    assert err.value.ma == "VUOT_GIOI_HAN"
    from e_trich_xuat.tham_so import doc_bo
    result = tao(excel([e1.HEADER, dong()]))
    for value in (None, "sha256:" + "0" * 64):
        with pytest.raises(LoiNghiepVu):
            doc_bo({**result, "bam_bo_tham_so": value})


def test_hai_module_ghim_viec():
    from mau_tx3 import chuan_bi_demo, ts_demo
    raw = excel([e1.HEADER, dong()])
    a, b, a_moi = tao(raw), tao(raw, "module_b"), tao(raw, version="v2")
    viec_cu = ts_demo(**a)
    _, _, ket_qua_a = chuan_bi_demo(ts=viec_cu)
    _, _, ket_qua_b = chuan_bi_demo(ts=ts_demo(**b))
    _, _, ket_qua_moi = chuan_bi_demo(ts=ts_demo(**a_moi))
    def meta(kq):
        return kq["yeu_cau_ai"]["chuyen_tiep"]["trich_xuat"]
    assert meta(ket_qua_a)["module"] == "module_a"
    assert meta(ket_qua_b)["module"] == "module_b"
    assert meta(ket_qua_moi)["phien_ban_bo"] == "v2"
    assert json.loads(viec_cu["bo_tham_so_json"])["phien_ban_bo"] == "v1"
    assert meta(ket_qua_a)["bam_bo_tham_so"] == a["bam_bo_tham_so"]

