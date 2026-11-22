import base64
import copy
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
from types import SimpleNamespace

import pytest
from kho_tri_thuc_sdk import danh_muc_tham_so as e1, xlsx_mini
from kho_tri_thuc_sdk.engine import Engine
from kho_tri_thuc_sdk.thu import CoreGia

from e_trich_xuat.soan_bo import ham_thao_tac
from e_trich_xuat.tham_so import doc_bo


def excel(rows=None, rules=None):
    out = io.BytesIO()
    sheets = {"Danh_muc": {"rows": rows or [e1.HEADER, ["TT-01", "DEMO", "Trích tên hợp đồng DEMO", "tên", "", "Có", 1, "", "", "Không"]]}}
    if rules is not None:
        sheets["Quy_tac"] = {"rows": rules}
    xlsx_mini.write_xlsx(out, sheets)
    return out.getvalue()


def goi(lenh, **kw):
    return ham_thao_tac(SimpleNamespace(dau_vao={"lenh": lenh, **kw}))


def nhap(raw=None):
    return goi("nhap_excel", bo={"module":"module_demo","loai_hop_dong":"DEMO","phien_ban_bo":"demo-1"},
               tep_base64=base64.b64encode(raw or excel()).decode())


def test_excel_sua_xuat_va_doc_lai_nguyen_bytes():
    kq = nhap()
    assert kq["dat"]
    bo, dm, bam = doc_bo(kq["tham_so"])
    assert dm.cac_dong == e1.doc_danh_muc(excel()).cac_dong
    assert bo["bam_tep_goc"].startswith("sha256:")
    bo["cac_dong"][0]["mo_ta"] = "Trích tên công ty DEMO Ánh Dương 🌞"
    sua = goi("kiem_bo", bo=bo)
    assert sua["dat"] and sua["tham_so"]["bam_bo_tham_so"] != bam
    assert doc_bo(sua["tham_so"])[0]["ma_bam_noi_dung"] != kq["bo"]["ma_bam_noi_dung"]
    assert goi("doc_bo", tham_so=sua["tham_so"])["tham_so"] == sua["tham_so"]


def test_quy_tac_giu_nguyen_va_tham_chieu_khong_ton_tai():
    raw = excel([e1.HEADER, ["TT-01","DEMO","Tỷ lệ","tỷ lệ","","Có",1,"","","Không"]],
                [e1.QUY_TAC_HEADER, ["Tổng tỷ lệ","TT-01","<=","100"]])
    kq = nhap(raw)
    assert kq["bo"]["quy_tac"] == e1.doc_danh_muc(raw).quy_tac
    bo = kq["bo"]
    bo["quy_tac"][0]["ma_tham_so"] = ["TT-99"]
    kq = goi("kiem_bo", bo=bo)
    assert not kq["dat"] and kq["loi"][0]["truong"] == "quy_tac"


@pytest.mark.parametrize("truong,gia_tri", [("ma","TT-001x"),("nhom",""),("mo_ta",""),("muc",4),("dung",False),("tk","a"*61)])
def test_loi_truong_va_khong_xuat_ban_sai(truong, gia_tri):
    bo = nhap()["bo"]
    bo["cac_dong"][0][truong] = gia_tri
    kq = goi("kiem_bo", bo=bo)
    assert not kq["dat"] and "tham_so" not in kq
    assert kq["loi"][0]["thong_bao"]


def test_trung_ma_tran_byte_va_bam_sai():
    kq = nhap(); bo = kq["bo"]
    bo["cac_dong"].append(copy.deepcopy(bo["cac_dong"][0]))
    assert "trùng" in goi("kiem_bo", bo=bo)["loi"][0]["thong_bao"]
    bo["cac_dong"][0]["mo_ta"] = "x"*65536
    assert "64 KiB" in goi("kiem_bo", bo=bo)["loi"][0]["thong_bao"]
    assert not goi("doc_bo", tham_so={**kq["tham_so"],"bam_bo_tham_so":"sha256:"+"0"*64})["dat"]
    bo = nhap()["bo"]
    bo["cac_dong"] = [{**bo["cac_dong"][0],"ma":f"TT-{n:03d}"} for n in range(201)]
    assert "200" in goi("kiem_bo", bo=bo)["loi"][0]["thong_bao"]


@pytest.mark.parametrize("raw", [b"DEMO khong phai Excel", b"x"*(2*1024*1024+1)], ids=["sai-tep","vuot-tran"])
def test_excel_loi_va_qua_tran(raw):
    kq = nhap(raw)
    assert not kq["dat"] and "tham_so" not in kq


def test_loi_e1_khong_chen_gia_tri_nhap():
    bo = nhap()["bo"]; bo["cac_dong"][0]["ma"] = "DEMO_KHONG_DUOC_LO"
    kq = goi("kiem_bo", bo=bo)
    assert "DEMO_KHONG_DUOC_LO" not in json.dumps(kq)
    assert kq["loi"][0]["truong"] == "cac_dong.0.ma"


def test_thao_tac_bang_core_gia_khong_dang_ky_vao_engine_that():
    # SDK 2.2.0 chưa có decorator quản trị; adapter này CHỈ tồn tại trong test.
    phieu = json.loads((Path(__file__).parents[1]/"goi/e_trich_xuat/engine.json").read_text(encoding="utf-8"))
    phieu["chay_thu_demo"] = []
    phieu.pop("cau_hinh", None)
    phieu["nang_luc"] = [{"ma":"demo.soan_bo@1","ten":"DEMO soạn bộ","nhan":["van_ban"],"tra":"van_ban",
                          "gioi_han":{"ky_tu_toi_da":5000000,"thoi_han_giay":30}}]
    app = Engine(phieu)
    @app.nang_luc("demo.soan_bo@1")
    def lam(viec):
        return {"loai":"van_ban", "van_ban":json.dumps(ham_thao_tac(SimpleNamespace(dau_vao=json.loads(viec.dau_vao["van_ban"]))),ensure_ascii=False)}
    vao = {"lenh":"kiem_bo","bo":nhap()["bo"]}
    kq = CoreGia().chay_thu(app,"demo.soan_bo@1",{"loai":"van_ban","van_ban":json.dumps(vao)})
    assert kq["trang_thai"] == "XONG"
    # Không phụ thuộc phong bì kết quả nội bộ của CoreGia để kiểm bytes ở đây.
    assert goi("kiem_bo",bo=vao["bo"])["dat"]


def test_node_ts_tx():
    assert shutil.which("node"), "Cần Node để kiểm màn TS-TX."
    kq = subprocess.run(["node","--test",str(Path(__file__).parent/"ui/soan_bo_ts_tx.test.mjs")],
                        capture_output=True,text=True,encoding="utf-8",timeout=180,
                        env={**__import__("os").environ,"TX_PYTHON":sys.executable})
    assert kq.returncode == 0, kq.stdout+kq.stderr
