"""AI-6: kiểm toàn thư mục bằng AST và chạy cổng thật với transport DEMO.

Dùng lại pipeline/DTO hiện có; viết mới chỉ test. Không gọi AI thật, không
chấm đáp án, không ghi phép đo TRICH-4. Mock transport không chứng minh độ
chính xác. Ba expectedFailure ghi nhận client/URL của bản review đóng băng
và đường TRICH-1a/3a chưa nối cổng chung; không sửa nguồn để che vi phạm.
"""

import ast
from contextlib import ExitStack
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch
import urllib.request
import zipfile

from kho_tri_thuc.engines.e_trich_xuat import ai_chung, quy_trinh as qt
from kho_tri_thuc.engines.e_trich_xuat import do_chinh_xac, tham_so
from kho_tri_thuc.m4.review_goc.trich_xuat import doc_hop_dong, ai_local, cloud
from kho_tri_thuc.tri_thuc import ai_cuc_bo
from kho_tri_thuc.tri_thuc.cong_ai import BoGhiBoNho, CongAI, KetQuaAI, YeuCauAI


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
ENGINE = ROOT / "engines" / "e_trich_xuat"
TEN_ENGINE = "kho_tri_thuc.engines.e_trich_xuat"
GOC = SRC / "kho_tri_thuc/m4/review_goc/trich_xuat"
TEXT = "DEMO hợp đồng số 00007, giá trị 1.000 đồng; tỷ lệ 0."
CLIENT = re.compile(r"^(requests|httpx|aiohttp|urllib\.request|http\.client|"
                    r"openai|anthropic|ollama)(\.|$)")
URL = re.compile(r"https?://|/api/(chat|generate|tags)\b|/v1/(chat|completions)\b")
XML_NAMESPACE = re.compile(
    r"https?://(?:schemas\.openxmlformats\.org|schemas\.microsoft\.com|purl\.org)"
    r"/[^\s\"'<>}{]*")

# Nợ cố định của bản review đóng băng: không miễn trừ theo cả tệp/thư mục.
# Khóa gồm đường dẫn tương đối + loại, dòng và nội dung đầy đủ của vi phạm.
GOC_REL = "src/kho_tri_thuc/m4/review_goc/trich_xuat/"
NO_CLIENT = {
    (GOC_REL + "ai_local.py", "client: dòng 10: http.client"):
        "Bản gốc còn transport HTTP trực tiếp, chờ lead thay bằng cổng chung.",
    (GOC_REL + "ai_local.py", "client: dòng 17: urllib.request"):
        "Bản gốc còn transport HTTP trực tiếp, chờ lead thay bằng cổng chung.",
    (GOC_REL + "may_ai.py", "client: dòng 14: urllib.request"):
        "Client riêng của bản gốc đóng băng, chưa được nối cổng chung.",
}
NO_URL = {
    (GOC_REL + filename, f"URL/protocol dòng {line}: {value}"):
        "Địa chỉ/protocol HTTP của bản gốc đóng băng, chờ lead nối cổng chung."
    for filename, line, value in (
        ("__main__.py", 53, "http://"),
        ("ai_local.py", 102, "/api/tags"),
        ("ai_local.py", 116, "/api/chat"),
        ("ai_local.py", 129, "/api/chat"),
        ("cau_hinh.py", 25, "http://localhost:11434"),
        ("may_ai.py", 21, "http://"),
        ("may_ai.py", 21, "https://"),
        ("may_ai.py", 24, "http://"),
        ("may_ai.py", 65, "/api/tags"),
        ("may_ai.py", 75, "/api/chat"),
        ("may_ai.py", 139, "http://"),
    )
}
NO_PHU_THUOC = {
    ("kho_tri_thuc.engines.e_trich_xuat." + entry,
     "kho_tri_thuc.m4.review_goc.trich_xuat.ai_local"):
        "TRICH-3b chưa tách tham_so khỏi quy_trinh gốc -> ai_local."
    for entry in ("chay", "quy_trinh", "tham_so")
}
# Ghim cả điểm import trên các đường nợ: thêm đường khác tới cùng client cũ
# cũng phải đỏ, dù tập cặp entry/client ở trên không đổi.
NO_CANH_PHU_THUOC = {
    ("kho_tri_thuc." + source, line, "kho_tri_thuc." + target):
        "Điểm import hiện có trên đường TRICH-3b tới ai_local của bản gốc."
    for source, line, target in (
        ("engines.e_trich_xuat.chay", 22, "engines.e_trich_xuat.tham_so"),
        ("engines.e_trich_xuat.quy_trinh", 23, "engines.e_trich_xuat.tham_so"),
        ("engines.e_trich_xuat.tham_so", 20, "m4.review_goc.trich_xuat.quy_trinh"),
        ("m4.review_goc.trich_xuat.ai_cloud", 12, "m4.review_goc.trich_xuat.ai_local"),
        ("m4.review_goc.trich_xuat.ai_cloud", 13, "m4.review_goc.trich_xuat.cloud"),
        ("m4.review_goc.trich_xuat.ai_cloud", 126, "m4.review_goc.trich_xuat.ai_local"),
        ("m4.review_goc.trich_xuat.cloud", 13, "m4.review_goc.trich_xuat.ai_local"),
        ("m4.review_goc.trich_xuat.cloud", 229, "m4.review_goc.trich_xuat.ai_cloud"),
        ("m4.review_goc.trich_xuat.ocr_abbyy", 342, "m4.review_goc.trich_xuat.ai_local"),
        ("m4.review_goc.trich_xuat.ocr_abbyy", 417, "m4.review_goc.trich_xuat.ai_local"),
        ("m4.review_goc.trich_xuat.quy_trinh", 16, "m4.review_goc.trich_xuat.ai_local"),
        ("m4.review_goc.trich_xuat.quy_trinh", 18, "m4.review_goc.trich_xuat.cloud"),
        ("m4.review_goc.trich_xuat.quy_trinh", 109, "m4.review_goc.trich_xuat.ocr_abbyy"),
        ("m4.review_goc.trich_xuat.quy_trinh", 303, "m4.review_goc.trich_xuat.ai_cloud"),
    )
}


def cac_import(tree, module):
    """Chuẩn hóa cả import tương đối và alias, không import/chạy mã nguồn."""
    package = module.rsplit(".", 1)[0]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                base = importlib.util.resolve_name("." * node.level + base, package)
            yield base
            yield from (base + "." + a.name for a in node.names)


def vi_pham(tree, module):
    found = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports = cac_import(ast.Module(body=[node], type_ignores=[]), module)
            found.extend(f"client: dòng {node.lineno}: {name}"
                         for name in imports if CLIENT.match(name))
    # Loại docstring: mô tả protocol/nguồn không phải địa chỉ được thực thi.
    docs = {id(n.body[0].value) for n in ast.walk(tree)
            if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            and n.body and isinstance(n.body[0], ast.Expr)
            and isinstance(n.body[0].value, ast.Constant)
            and isinstance(n.body[0].value.value, str)}
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and id(node) not in docs
                and URL.search(XML_NAMESPACE.sub("", node.value))):
            # Chỉ bỏ URI namespace: vẫn bắt endpoint khác trong cùng chuỗi XML.
            found.append(f"URL/protocol dòng {node.lineno}: {node.value}")
    return sorted(set(found))


def ten_module(p):
    """Tên module Python; engine nằm ngoài src nhưng vẫn import qua namespace cũ (shim)."""
    if ENGINE in p.parents:
        return ".".join((TEN_ENGINE, *p.relative_to(ENGINE).with_suffix("").parts))
    return ".".join(p.relative_to(SRC).with_suffix("").parts)


def quet_nguon():
    paths = sorted(set(ENGINE.rglob("*.py")) | set(GOC.rglob("*.py")))
    return {ten_module(p):
            (p, ast.parse(p.read_text(encoding="utf-8-sig"), filename=str(p)))
            for p in paths}


def phu_thuoc(modules, start):
    """Đóng bắc cầu import tĩnh trong cả hai thư mục được giao kiểm."""
    seen, pending = set(), [start]
    while pending:
        name = pending.pop()
        if name in seen or name not in modules:
            continue
        seen.add(name)
        pending.extend(cac_import(modules[name][1], name))
    return seen


def loi_review_goc(modules, prefix):
    return {(p.relative_to(ROOT).as_posix(), violation)
            for name, (p, tree) in modules.items() if GOC in p.parents
            for violation in vi_pham(tree, name) if violation.startswith(prefix)}


def loi_phu_thuoc(modules):
    clients = {name for name, (_, tree) in modules.items()
               if any(v.startswith("client:") for v in vi_pham(tree, name))}
    return {(name, dep) for name, (path, _) in modules.items() if ENGINE in path.parents
            for dep in phu_thuoc(modules, name) & clients}


def canh_phu_thuoc(modules):
    clients = {name for name, (_, tree) in modules.items()
               if any(v.startswith("client:") for v in vi_pham(tree, name))}
    closures = {name: phu_thuoc(modules, name) for name in modules}
    reached = set().union(*(closures[name] for name, (path, _) in modules.items()
                            if ENGINE in path.parents))
    return {(name, node.lineno, target)
            for name in reached for node in ast.walk(modules[name][1])
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for target in cac_import(ast.Module(body=[node], type_ignores=[]), name)
            if closures.get(target, set()) & clients}


class KiemTinhTests(unittest.TestCase):
    def test_quet_de_quy_toan_hai_thu_muc(self):
        modules = quet_nguon()
        self.assertEqual({p for p, _ in modules.values()},
                         set(ENGINE.rglob("*.py")) | set(GOC.rglob("*.py")))
        for path in (ENGINE / "ai_chung.py", ENGINE / "chay.py", GOC / "ai_local.py",
                     GOC / "ai_cloud.py", GOC / "may_ai.py"):
            self.assertIn(path, {p for p, _ in modules.values()})

    def test_engine_khong_client_hoac_url_rieng(self):
        errors = {str(p.relative_to(ROOT)): vi_pham(tree, name)
                  for name, (p, tree) in quet_nguon().items() if ENGINE in p.parents}
        self.assertEqual({p: v for p, v in errors.items() if v}, {})

    def test_review_goc_khong_client_rieng(self):
        self.assertEqual(loi_review_goc(quet_nguon(), "client:") - NO_CLIENT.keys(), set())

    @unittest.expectedFailure
    def test_no_client_da_biet(self):
        self.assertEqual(loi_review_goc(quet_nguon(), "client:") & NO_CLIENT.keys(),
                         set(), NO_CLIENT)

    def test_review_goc_khong_url_may_ai(self):
        self.assertEqual(loi_review_goc(quet_nguon(), "URL/") - NO_URL.keys(), set())

    @unittest.expectedFailure
    def test_no_url_da_biet(self):
        self.assertEqual(loi_review_goc(quet_nguon(), "URL/") & NO_URL.keys(),
                         set(), NO_URL)

    def test_moi_entry_engine_chi_phu_thuoc_cong_chung(self):
        modules = quet_nguon()
        self.assertEqual(loi_phu_thuoc(modules) - NO_PHU_THUOC.keys(), set())
        self.assertEqual(canh_phu_thuoc(modules) - NO_CANH_PHU_THUOC.keys(), set())

    def test_no_phu_thuoc_da_biet(self):
        self.assertEqual(loi_phu_thuoc(quet_nguon()) & NO_PHU_THUOC.keys(),
                         set(), NO_PHU_THUOC)

    def test_ast_nhan_alias_import_tuong_doi_va_url(self):
        tree = ast.parse('import httpx as h\nfrom . import ai_local as ai\n'
                         'endpoint = "http://DEMO.invalid/api/chat"\n')
        name = "kho_tri_thuc.m4.review_goc.trich_xuat.quy_trinh"
        self.assertIn("kho_tri_thuc.m4.review_goc.trich_xuat.ai_local",
                      list(cac_import(tree, name)))
        self.assertTrue(any(v.startswith("client:") for v in vi_pham(tree, name)))
        self.assertTrue(any(v.startswith("URL/") for v in vi_pham(tree, name)))
        self.assertEqual(vi_pham(ast.parse('"""Nguồn /api/chat"""'), name), [])

    def test_namespace_xml_khong_bao_sai_nhung_van_bat_url_ai(self):
        namespace = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        valid = (namespace, "{" + namespace + "}p",
                 '<?xml version="1.0"?><w:document xmlns:w="' + namespace + '"/>',
                 '" Type="' + namespace + '" Target="sheet1.xml"/>',
                 "{http://purl.org/dc/elements/1.1/}title")
        name = "kho_tri_thuc.m4.review_goc.trich_xuat.demo"
        for value in valid:
            with self.subTest(value=value):
                self.assertEqual(vi_pham(ast.parse("xml = " + repr(value)), name), [])
        for value in (valid[2] + "http://DEMO.invalid/api/chat",
                      '{http://DEMO.invalid/api/chat}p',
                      '<?xml version="1.0"?><url>http://DEMO.invalid</url>',
                      "http://schemas.openxmlformats.org.DEMO.invalid/api/chat",
                      "/api/generate", "/v1/chat/completions"):
            with self.subTest(value=value):
                self.assertTrue(any(v.startswith("URL/") for v in
                                    vi_pham(ast.parse("xml = " + repr(value)), name)))

    def test_vi_pham_moi_lam_assertion_do_du_no_cu_con(self):
        # Chỉ sửa AST trong bộ nhớ; chạy đúng assertion thường của bộ kiểm tĩnh.
        fixtures = (
            (GOC / "ai_local.py", "import httpx as demo", "test_review_goc_khong_client_rieng"),
            (GOC / "doc_hop_dong.py", "import httpx as demo", "test_review_goc_khong_client_rieng"),
            (GOC / "ai_local.py", 'url = "http://DEMO.invalid/api/chat"',
             "test_review_goc_khong_url_may_ai"),
            (GOC / "doc_hop_dong.py", 'url = "http://DEMO.invalid/api/chat"',
             "test_review_goc_khong_url_may_ai"),
            (ENGINE / "ai_chung.py", "from kho_tri_thuc.m4.review_goc.trich_xuat import may_ai",
             "test_moi_entry_engine_chi_phu_thuoc_cong_chung"),
            (ENGINE / "chay.py", "from kho_tri_thuc.m4.review_goc.trich_xuat import ai_local",
             "test_moi_entry_engine_chi_phu_thuoc_cong_chung"),
        )
        for path, source, method in fixtures:
            with self.subTest(path=path.name, source=source):
                modules = quet_nguon()
                name = ten_module(path)
                tree = modules[name][1]
                node = ast.parse(source).body[0]
                ast.increment_lineno(node, max(n.lineno for n in ast.walk(tree)
                                              if hasattr(n, "lineno")))
                tree.body.append(node)
                with patch.dict(globals(), quet_nguon=lambda: modules):
                    result = unittest.TestResult()
                    KiemTinhTests(method).run(result)
                self.assertEqual(len(result.failures), 1, result.errors)
                self.assertEqual(result.errors, [])
                self.assertEqual(result.expectedFailures, [])


class CongChungTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.lan_tra_loi = {}
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.dict(ai_cuc_bo._CONNECTION_FAILURES, {}, clear=True))
        # Hàng rào: nếu luồng đi chệch khỏi transport DEMO, test phải thất bại.
        for obj, attr in ((urllib.request, "urlopen"), (urllib.request, "build_opener"),
                          (socket.socket, "connect"), (socket, "create_connection"),
                          (subprocess, "run"), (subprocess, "Popen"),
                          (doc_hop_dong, "_word"), (ai_local.MayAI, "_http"),
                          (cloud, "kiem_tra_cloud"), (do_chinh_xac, "do_chinh_xac")):
            mock = self.stack.enter_context(patch.object(obj, attr, side_effect=AssertionError(attr)))
            self.addCleanup(mock.assert_not_called)
        # Không tìm đáp án hoặc chấm số mock thành số đo thực TRICH-4.
        self.stack.enter_context(patch.object(qt, "tim_dap_an", return_value=None))
        self.load_key = self.stack.enter_context(patch.object(qt, "load_key", return_value=None))

    def cong(self, transport, enabled=True):
        self.provider, self.mask = Mock(), Mock()
        self.bo_ghi = BoGhiBoNho()
        return CongAI(dict(local_ai=dict(enabled=enabled, model="DEMO-AI-6",
            url="http://127.0.0.1:9/v1/chat/completions"), cong_ai=dict(cloud_bat=True)),
            bo_ghi=self.bo_ghi, local_transport=transport, nha_cung_cap=self.provider,
            mask=self.mask, moi_truong={}, kiem_xac_suat=lambda _: True)

    def khong_cloud(self):
        self.assertEqual(self.provider.mock_calls, [])
        self.assertEqual(self.mask.mock_calls, [])
        self.assertFalse(any(b.duong == "CLOUD" and b.da_gui for b in self.bo_ghi.ban_ghi))

    def tra_loi(self, url, body):
        prompt = json.loads(body)["messages"][-1]["content"]
        names = re.search(r"Các trường cần điền: (.+)", prompt).group(1).split(", ")
        rows = re.findall(r"^R\d+ \|.*", prompt, re.M)
        fields = []
        for name in names:
            if name.endswith((".1", ".2", ".3")):
                if rows and name.endswith(".1"):
                    fields.append(dict(ten=name, gia_tri=rows[0].split(" | ")[0], trich_dan=rows[0]))
            elif "." not in name:
                self.lan_tra_loi[name] = self.lan_tra_loi.get(name, 0) + 1
                quote = "DEMO dẫn chứng sai" if name == "TC-01" and self.lan_tra_loi[name] == 1 else TEXT
                fields.append(dict(ten=name, gia_tri="00007", trich_dan=quote))
        return json.dumps(dict(truong=fields, do_tin_cay=0.2), ensure_ascii=False)

    def pipeline(self, cong):
        # Tệp DEMO riêng, giữ lại theo quy tắc không xóa; không ghi vào repo.
        folder = Path(tempfile.mkdtemp(prefix="ktt_demo_ai_6_"))
        path = folder / "DEMO.docx"
        with zipfile.ZipFile(path, "w") as z:
            z.writestr("word/document.xml", f'<w:document xmlns:w="{doc_hop_dong.W_NS}">'
                       f'<w:body><w:p><w:r><w:t>{TEXT}</w:t></w:r></w:p></w:body></w:document>')
        calls, replies, logs, phases = [], [], [], []
        original = CongAI.goi
        config = deepcopy(cong.cai_dat)

        def goi(instance, request, **kwargs):
            self.assertIsInstance(request, YeuCauAI)
            self.assertEqual(request.loai_viec, "BOC_TACH_HOP_DONG")
            self.assertFalse(instance.cai_dat["cloud_bat"])
            self.assertTrue(request.van_ban and request.truong)
            calls.append(request)
            phases.append(phases_now[0])
            out = original(instance, request, **kwargs)
            self.assertIsInstance(out, KetQuaAI)
            replies.append(out)
            return out

        phases_now = [None]

        def progress(step, *args):
            phases_now[0] = step

        tx = qt.TrichXuat(cong_ai=cong, out_dir=folder / "out", ghi_log=logs.append,
                          tien_do=progress, cloud=None)
        with patch.object(CongAI, "goi", goi):
            raw = tx.xu_ly(path)
        self.assertEqual(cong.cai_dat, config)
        self.assertIsNone(tx.cloud)
        self.assertFalse(tx.ai.la_cloud)
        self.assertEqual(len(raw["bang"]), 37)
        self.assertEqual({r["ma"] for r in raw["bang"]}, {p["ma"] for p in tham_so.danh_muc_xd()})
        self.assertEqual(len(raw["phan_hoi_ai"]), len(calls))
        self.assertTrue(all(r.ma_yeu_cau for r in replies))
        self.assertFalse(raw["tom_tat"]["token_da_do"])
        self.load_key.assert_called_once_with(None)
        self.khong_cloud()
        persisted = json.loads((folder / "out/DEMO" / raw["tep"]["json"]).read_text(encoding="utf-8"))
        self.assertEqual(persisted["phan_hoi_ai"], json.loads(json.dumps(raw["phan_hoi_ai"])))
        return raw, calls, logs, phases

    def test_pipeline_do_vi_tri_trich_nhom_ra_lai_qua_dto_chung(self):
        raw, calls, _, phases = self.pipeline(self.cong(self.tra_loi))
        self.assertTrue({2, 3, 5}.issubset(phases), phases)
        self.assertTrue(any(ai_chung.CHI_DAN_VI_TRI in r.chi_dan for r in calls))
        self.assertTrue(any(ai_chung.CHI_DAN_TRICH in r.chi_dan for r in calls))
        self.assertEqual(raw["tom_tat"]["loi_ai"], 0)
        self.assertGreaterEqual(self.lan_tra_loi["TC-01"], 2)
        self.assertTrue(any("TC-01" in r["truong_bi_loai"] for r in raw["phan_hoi_ai"]))
        self.assertTrue(any(r["gia_tri"] == "00007" and r["trich_dan"] == TEXT for r in raw["bang"]))

    def test_local_chac_bi_chon_kiem_xac_suat_van_khong_cloud(self):
        reply = json.dumps(dict(truong=[dict(ten="TC-01", gia_tri="00007", trich_dan=TEXT)],
                                do_tin_cay=1))
        transport = Mock(return_value=reply)
        cong = self.cong(transport)
        request = YeuCauAI("BOC_TACH_HOP_DONG", TEXT, "DEMO", ("TC-01",))
        # Bộ chọn mẫu luôn đồng ý nếu được hỏi; cổng chỉ Local được chặn sớm hơn.
        with patch.object(CongAI, "_chon_kiem", return_value=True), \
                patch.object(CongAI, "_cloud", autospec=True, side_effect=CongAI._cloud) as cloud_call:
            result = ai_chung.AIChung(cong).goi(request)
        transport.assert_called_once()
        self.assertEqual(json.loads(transport.call_args.args[1])['model'], 'DEMO-AI-6')
        self.assertEqual(result.duong, "LOCAL")
        self.assertEqual(result.truong["TC-01"].gia_tri, "00007")
        self.assertEqual(result.truong["TC-01"].nguon, "LOCAL")
        self.assertEqual(len(self.bo_ghi.ban_ghi), 1)
        record = self.bo_ghi.ban_ghi[0]
        self.assertEqual((record.duong, record.model, record.da_gui), ('LOCAL', 'DEMO-AI-6', True))
        cloud_call.assert_not_called()
        self.khong_cloud()

    def _loi_pipeline(self, transport, code, enabled=True):
        raw, calls, logs, _ = self.pipeline(self.cong(transport, enabled))
        count = raw["tom_tat"]["loi_ai"]
        self.assertGreater(count, 0)
        self.assertEqual(count, len(calls))
        self.assertEqual(count, sum("LỖI " in log for log in logs))
        for phase in ("LỖI tìm vị trí:", "LỖI nhóm ", "LỖI rà lại đoạn "):
            self.assertTrue(any(phase in log and code in log for log in logs), phase)
        self.assertTrue(all(code in r["ly_do"] and r["thong_bao"] for r in raw["phan_hoi_ai"]))
        self.assertIn(f"lỗi AI: {count}", logs[-1])

    def test_local_mat_ket_noi_bao_loi_khong_cloud(self):
        self._loi_pipeline(Mock(side_effect=ConnectionError("DEMO mất kết nối")), "LOCAL_KHONG_CHAY")

    def test_local_json_hong_bao_loi_khong_cloud(self):
        self._loi_pipeline(lambda *a: "DEMO JSON hỏng", "PHAN_HOI_KHONG_HOP_LE")

    def test_local_tat_bao_loi_khong_cloud(self):
        transport = Mock(side_effect=AssertionError("Local đã tắt"))
        self._loi_pipeline(transport, "LOCAL_TAT", enabled=False)
        transport.assert_not_called()

    def test_local_khong_tim_thay_khong_bao_loi_gia(self):
        raw, _, logs, _ = self.pipeline(self.cong(lambda *a: '{"truong": [], "do_tin_cay": 0}'))
        self.assertEqual(raw["tom_tat"]["loi_ai"], 0)
        self.assertFalse(any("LỖI " in log for log in logs))
        self.assertTrue(all(r["gia_tri"] in ("", "Không tìm thấy trong HĐ") for r in raw["bang"]))

    def test_local_loi_o_hai_seam_giu_ma_va_thong_bao(self):
        request = YeuCauAI("BOC_TACH_HOP_DONG", TEXT, "DEMO", ("TC-01",))
        for code in ("LOCAL_TAT", "LOCAL_KHONG_CHAY", "LOCAL_LOI", "PHAN_HOI_KHONG_HOP_LE"):
            for seam in ("hoi_trich", "tim_vi_tri"):
                with self.subTest(code=code, seam=seam):
                    ai = ai_chung.AIChung(self.cong(self.tra_loi))
                    result = KetQuaAI(request.loai_viec, "DO", {}, "KHONG", "DEMO lỗi Local", (code,))
                    with patch.object(CongAI, "goi", return_value=result) as call:
                        with self.assertRaisesRegex(ai_chung.AILoi, code + ": DEMO lỗi Local"):
                            if seam == "hoi_trich":
                                ai.hoi_trich(request)
                            else:
                                ai.tim_vi_tri([dict(ma="TC-01", mo_ta="DEMO")], "R001 | DEMO", {"R001"})
                    call.assert_called_once()
                    self.assertIsInstance(call.call_args.args[0], YeuCauAI)
                    self.assertEqual(ai.phan_hoi[0]["ly_do"], (code,))
                    self.assertEqual(ai.phan_hoi[0]["thong_bao"], result.thong_bao)
                    self.khong_cloud()


if __name__ == "__main__":
    unittest.main()
