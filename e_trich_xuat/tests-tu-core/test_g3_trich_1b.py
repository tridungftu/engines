"""DEMO thuần: cổng thật với transport giả, chặn mạng/COM/OCR/Cloud.

Nguồn tests/test_trich_xuat.py đóng băng, không chạy server mock_ollama:
- test_toan_luong -> test_pipeline_37_qua_cong: giữ 37 mã, dẫn chứng và xuất;
  thay protocol cũ bằng CongAI/YeuCauAI/KetQuaAI (CD-038 câu 1C).
- test_ra_lai_sua_trich_dan_sai -> test_ra_lai_sau_dan_chung_sai: cổng loại
  dẫn chứng sai trước pipeline, lượt rà lại phải lấy được dẫn chứng đúng.
- test_json_hong_hoi_lai -> test_json_hong_khong_fallback: định dạng/lỗi do
  cổng chung xử lý, không còn retry protocol riêng của nguồn.
- test_prompt_bi_cat: không giả định num_ctx/token của client cũ; cần phép
  đo thực TRICH-4b, mock không chứng minh context/độ chính xác của model.
Thư mục DEMO dùng mkdtemp, giữ lại, không xóa tệp.
"""

import ast
from contextlib import ExitStack
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch
import urllib.request
import zipfile

from kho_tri_thuc.engines.e_trich_xuat import ai_chung, quy_trinh as qt, tham_so
from kho_tri_thuc.m4.review_goc.trich_xuat import doc_hop_dong, quy_trinh as goc
from kho_tri_thuc.tri_thuc import ai_cuc_bo
from kho_tri_thuc.tri_thuc.cong_ai import BoGhiBoNho, CongAI, KetQuaAI, YeuCauAI

ROOT = Path(__file__).resolve().parents[1]
TEXT = "DEMO hợp đồng số 00007, giá trị 1.000 đồng, không áp dụng; tỷ lệ 0."


def tao_docx():
    path = Path(tempfile.mkdtemp(prefix="ktt_demo_trich_1b_")) / "DEMO.docx"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", f'<w:document xmlns:w="{doc_hop_dong.W_NS}">'
                   '<w:body><w:p><w:del><w:r><w:delText>DEMO cũ</w:delText></w:r></w:del>'
                   f'<w:ins><w:r><w:t>{TEXT}</w:t></w:r></w:ins></w:p></w:body></w:document>')
    return path


class TransportGia:
    def __init__(self, *, sai_lan_dau=False, rong=False):
        self.prompts = []
        self.sai_lan_dau = sai_lan_dau
        self.rong = rong
        self.lan = {}

    def __call__(self, url, body):
        payload = json.loads(body)
        self.prompts.append(payload)
        prompt = payload["messages"][-1]["content"]
        names = re.search(r"Các trường cần điền: (.+)", prompt).group(1).split(", ")
        muc_luc = re.findall(r"^R\d+ \|.*", prompt, re.M)
        out = []
        for name in names:
            if self.rong:
                continue
            if name.endswith((".1", ".2", ".3")):
                if muc_luc and name.endswith(".1"):
                    out.append(dict(ten=name, gia_tri=muc_luc[0].split(" | ")[0], trich_dan=muc_luc[0]))
            else:
                self.lan[name] = self.lan.get(name, 0) + 1
                value = "đồng" if name.endswith(".don_vi") else "không áp dụng" if name.endswith(".ghi_chu") else "00007"
                quote = "DEMO bịa" if self.sai_lan_dau and name == "TC-01" and self.lan[name] == 1 else TEXT
                out.append(dict(ten=name, gia_tri=value, trich_dan=quote))
        return json.dumps(dict(truong=out, do_tin_cay=1), ensure_ascii=False)


def cong(transport=None):
    return CongAI(dict(local_ai=dict(enabled=True, model="DEMO-model",
        url="http://127.0.0.1:9/v1/chat/completions"),
        cong_ai=dict(cloud_bat=True)), bo_ghi=BoGhiBoNho(),
        local_transport=transport or TransportGia(),
        nha_cung_cap=Mock(), mask=Mock(), moi_truong={},
        kiem_xac_suat=lambda _: True)


class Trich1bTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.dict(ai_cuc_bo._CONNECTION_FAILURES, {}, clear=True))
        for obj, name in ((urllib.request, "urlopen"), (urllib.request, "build_opener"),
                          (socket, "create_connection"), (subprocess, "run"),
                          (doc_hop_dong, "_word"), (goc.TrichXuat, "ocr_pdf")):
            self.stack.enter_context(patch.object(obj, name, side_effect=AssertionError(name)))

    def test_nguon_sha_va_phien_ban(self):
        for module in (ai_chung, qt):
            self.assertEqual(hashlib.sha256((ROOT / module.NGUON).read_bytes()).hexdigest(), module.NGUON_SHA256)
            self.assertEqual(module.PHIEN_BAN_NGUON, "2026-10-15a")

    def test_khong_import_client_hoac_url_ai(self):
        for module in (ai_chung, qt):
            src = Path(module.__file__).read_text(encoding="utf-8")
            self.assertNotRegex(src, r"https?://|/api/chat|/v1/chat/completions")
            for node in ast.walk(ast.parse(src)):
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                else:
                    continue
                self.assertFalse(any(re.search(r"(^|\.)(requests|httpx|urllib|http|socket|anthropic|openai|ai_local|ai_cloud|may_ai)(\.|$)", n) for n in names), names)

    def test_danh_sach_cau_doi_co_ly_do(self):
        self.assertEqual({x["id"] for x in ai_chung.CAU_HOI_DOI},
                         {"TRICH-NHOM", "TRICH-VI-TRI", "TRICH-RA-LAI", "TRICH-JSON"})
        for row in ai_chung.CAU_HOI_DOI:
            self.assertTrue(all(row[k].strip() for k in ("goc", "moi", "ly_do", "cau_goc", "cau_moi")))
            self.assertNotEqual(row["goc"], row["moi"])

    def test_pipeline_37_qua_cong(self):
        path = tao_docx()
        before = path.read_bytes()
        c = cong()
        settings = deepcopy(c.cai_dat)
        calls = []
        original = CongAI.goi

        def goi(instance, yc, **kwargs):
            self.assertIsInstance(yc, YeuCauAI)
            self.assertFalse(instance.cai_dat["cloud_bat"])
            calls.append(yc)
            out = original(instance, yc, **kwargs)
            self.assertIsInstance(out, KetQuaAI)
            return out

        tx = qt.TrichXuat(cong_ai=c, cloud=None, out_dir=path.parent / "out")
        with patch.object(CongAI, "goi", goi):
            raw = tx.xu_ly(path)
        self.assertEqual(c.cai_dat, settings)
        self.assertIsNone(tx.cloud)
        self.assertFalse(tx.ai.la_cloud)
        self.assertGreater(len(calls), 1)
        self.assertTrue(any("MỤC LỤC" in yc.chi_dan for yc in calls))
        self.assertTrue(any(ai_chung.CHI_DAN_TRICH in yc.chi_dan for yc in calls))
        self.assertEqual([r["ma"] for r in raw["bang"]], [p["ma"] for p in tham_so.danh_muc_xd()])
        self.assertEqual(len(raw["bang"]), 37)
        for row in raw["bang"]:
            self.assertEqual(row["gia_tri"], "00007")
            self.assertEqual(row["don_vi"], "đồng")
            self.assertIn("không áp dụng", row["ghi_chu"])
            self.assertEqual(row["trich_dan"], TEXT)
            self.assertTrue(row["dieu_khoan"])
            self.assertTrue(row["row_id"])
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(raw["phieu_kiem_tra"]["accept_by"], "Python")
        self.assertEqual(len(raw["phan_hoi_ai"]), len(calls))
        self.assertTrue(all(x["ma_yeu_cau"] for x in raw["phan_hoi_ai"]))
        self.assertFalse(raw["tom_tat"]["token_da_do"])
        saved = path.parent / "out" / "DEMO" / raw["tep"]["json"]
        self.assertEqual(json.loads(saved.read_text(encoding="utf-8")), json.loads(json.dumps(raw)))
        c._mask.assert_not_called()
        self.assertEqual(c._mask.mock_calls, [])
        self.assertEqual(c._nha_cung_cap.mock_calls, [])

    def test_ra_lai_sau_dan_chung_sai(self):
        path = tao_docx()
        transport = TransportGia(sai_lan_dau=True)
        c = cong(transport)
        raw = qt.TrichXuat(cong_ai=c, out_dir=path.parent / "out").xu_ly(path)
        first = raw["bang"][0]
        self.assertGreaterEqual(transport.lan["TC-01"], 2)
        self.assertEqual(first["gia_tri"], "00007")
        self.assertEqual(first["trich_dan"], TEXT)
        self.assertIn("rà lại", first["ghi_chu"])
        self.assertTrue(any("TC-01" in x["truong_bi_loai"] for x in raw["phan_hoi_ai"]))
        self.assertEqual(raw["tom_tat"]["loi_ai"], 0)

    def test_json_hong_khong_fallback(self):
        c = cong(lambda *a: "DEMO JSON hỏng")
        ai = ai_chung.AIChung(c, cloud=None)
        out = ai.goi(YeuCauAI("BOC_TACH_HOP_DONG", TEXT, "DEMO", ("TC-01",)))
        self.assertEqual(out.duong, "KHONG")
        self.assertFalse(out.truong)
        self.assertTrue(out.ly_do)
        self.assertEqual(c._mask.mock_calls + c._nha_cung_cap.mock_calls, [])
        self._kiem_pipeline_loi(c, "PHAN_HOI_KHONG_HOP_LE")

    def test_local_loi_khong_goi_mask_cloud(self):
        c = cong(Mock(side_effect=ConnectionError("DEMO lỗi mạng")))
        yc = YeuCauAI("BOC_TACH_HOP_DONG", TEXT, "DEMO", ("TC-01",))
        out = ai_chung.AIChung(c).goi(yc)
        self.assertEqual(out.duong, "KHONG")
        self.assertTrue(out.ly_do)
        self.assertEqual(c._mask.mock_calls + c._nha_cung_cap.mock_calls, [])
        self._kiem_pipeline_loi(c, "LOCAL_KHONG_CHAY")

    def _kiem_pipeline_loi(self, c, ma_loi):
        path = tao_docx()
        logs = []
        raw = qt.TrichXuat(cong_ai=c, out_dir=path.parent / "out", ghi_log=logs.append).xu_ly(path)
        n_err = raw["tom_tat"]["loi_ai"]
        self.assertGreater(n_err, 0)
        self.assertEqual(n_err, sum("LỖI " in log for log in logs))
        self.assertTrue(any("LỖI tìm vị trí:" in log and ma_loi in log for log in logs))
        self.assertTrue(any("LỖI nhóm " in log and ma_loi in log for log in logs))
        self.assertTrue(any("LỖI rà lại đoạn " in log and ma_loi in log for log in logs))
        self.assertIn(f"lỗi AI: {n_err}", logs[-1])
        self.assertEqual(len(raw["bang"]), 37)
        self.assertTrue(raw["phan_hoi_ai"])
        self.assertTrue(all(ma_loi in x["ly_do"] and x["thong_bao"] for x in raw["phan_hoi_ai"]))
        self.assertEqual(len(raw["phan_hoi_ai"]), n_err)
        saved = path.parent / "out" / "DEMO" / raw["tep"]["json"]
        persisted = json.loads(saved.read_text(encoding="utf-8"))
        self.assertEqual(persisted["tom_tat"]["loi_ai"], n_err)
        self.assertEqual(persisted["phan_hoi_ai"], json.loads(json.dumps(raw["phan_hoi_ai"])))
        self.assertEqual(c._mask.mock_calls + c._nha_cung_cap.mock_calls, [])

    def test_loi_van_hanh_va_json_truyen_qua_hai_seam(self):
        yc = YeuCauAI("BOC_TACH_HOP_DONG", TEXT, "DEMO", ("TC-01",))
        params = [{"ma": "TC-01", "mo_ta": "DEMO"}]
        for ma_loi in ("LOCAL_TAT", "LOCAL_KHONG_CHAY", "LOCAL_LOI", "PHAN_HOI_KHONG_HOP_LE"):
            for seam in ("hoi_trich", "tim_vi_tri"):
                with self.subTest(ma_loi=ma_loi, seam=seam):
                    ai = ai_chung.AIChung(cong())
                    kq = KetQuaAI("BOC_TACH_HOP_DONG", "DO", {}, "KHONG", "DEMO lỗi AI", (ma_loi,))
                    with patch.object(CongAI, "goi", return_value=kq):
                        with self.assertRaisesRegex(ai_chung.AILoi, ma_loi + ": DEMO lỗi AI"):
                            if seam == "hoi_trich":
                                ai.hoi_trich(yc)
                            else:
                                ai.tim_vi_tri(params, "R001 | DEMO", {"R001"})
                    self.assertEqual(len(ai.phan_hoi), 1)
                    self.assertEqual(ai.phan_hoi[0]["ly_do"], (ma_loi,))
                    self.assertEqual(ai.phan_hoi[0]["thong_bao"], kq.thong_bao)

    def test_gia_tri_so_khong_khong_bi_mat(self):
        c = cong(lambda *a: json.dumps(dict(truong=[dict(ten="TC-01", gia_tri="0", trich_dan=TEXT)], do_tin_cay=1)))
        yc = YeuCauAI("BOC_TACH_HOP_DONG", TEXT, "DEMO", ("TC-01",))
        items, _, _ = ai_chung.AIChung(c).hoi_trich(yc)
        self.assertEqual(items[0]["gia_tri"], "0")
        self.assertEqual(items[0]["trich_dan"], TEXT)

    def test_thieu_khong_bien_thanh_so_khong(self):
        path = tao_docx()
        logs = []
        raw = qt.TrichXuat(cong_ai=cong(TransportGia(rong=True)), out_dir=path.parent / "out",
                          ghi_log=logs.append).xu_ly(path)
        self.assertEqual(len(raw["bang"]), 37)
        self.assertTrue(all(r["gia_tri"] in ("", "Không tìm thấy trong HĐ") for r in raw["bang"]))
        self.assertTrue(all(r["gia_tri"] != "0" for r in raw["bang"]))
        self.assertEqual(raw["tom_tat"]["loi_ai"], 0)
        self.assertIn("lỗi AI: 0", logs[-1])
        self.assertFalse(any("LỖI " in log for log in logs))
        self.assertTrue(raw["phan_hoi_ai"])
        for phan_hoi in raw["phan_hoi_ai"]:
            self.assertEqual(phan_hoi["duong"], "LOCAL")
            self.assertEqual(phan_hoi["ly_do"], ("KHONG_THAY_CAN_CU",))
            self.assertEqual(phan_hoi["thong_bao"], "Không thấy căn cứ trong tài liệu.")
            self.assertEqual(phan_hoi["truong"], {})

    def test_cloud_bi_chan_ca_khi_thay_doi_sau_khoi_tao(self):
        c = cong()
        for value in ({}, False, {"bat": True}):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "CLOUD_BI_CHAN"):
                qt.TrichXuat(cong_ai=c, out_dir="DEMO", cloud=value)
        tx = qt.TrichXuat(cong_ai=c, out_dir="DEMO")
        tx.cloud = {}
        with self.assertRaisesRegex(ValueError, "CLOUD_BI_CHAN"):
            tx.xu_ly("DEMO.docx")

    def test_pdf_va_ocr_bi_chan(self):
        tx = qt.TrichXuat(cong_ai=cong(), out_dir="DEMO")
        with self.assertRaisesRegex(ValueError, "CHI_DOCX"):
            tx.xu_ly("DEMO.pdf")
        with self.assertRaisesRegex(ValueError, "OCR_BI_CHAN"):
            tx.ocr_pdf("DEMO.pdf")

    def test_dung_truoc_goi_cong(self):
        stop = threading.Event()
        stop.set()
        with patch.object(CongAI, "goi") as goi:
            with self.assertRaises(ai_chung.DaDung):
                ai_chung.AIChung(cong(), dung=stop).goi(YeuCauAI("BOC_TACH_HOP_DONG", TEXT, "DEMO"))
            goi.assert_not_called()

    def test_loc_vi_tri_chi_nhan_id_that_toi_da_ba(self):
        params = [{"ma": "TC-01", "mo_ta": "DEMO"}]
        c = cong()
        ai = ai_chung.AIChung(c)
        from kho_tri_thuc.tri_thuc.cong_ai import TruongAI
        data = {f"TC-01.{i}": TruongAI(f"TC-01.{i}", rid, rid, "LOCAL")
                for i, rid in enumerate(("R001", "R001", "R999"), 1)}
        with patch.object(CongAI, "goi", return_value=KetQuaAI("BOC_TACH_HOP_DONG", "VANG", data, "LOCAL", "DEMO")):
            self.assertEqual(ai.tim_vi_tri(params, "R001 | DEMO", {"R001"}), {"TC-01": ["R001"]})

    def test_khong_sua_globals_nguon(self):
        self.assertIs(goc.TrichXuat.xu_ly.__globals__["read_contract"], doc_hop_dong.read_contract)
        self.assertIsNot(qt.TrichXuat.ra_lai, goc.TrichXuat.ra_lai)
        self.assertIs(qt.check, goc.check)
        self.assertIs(qt.kiem_tra_logic, goc.kiem_tra_logic)


if __name__ == "__main__":
    unittest.main()
