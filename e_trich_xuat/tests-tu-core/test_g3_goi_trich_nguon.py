# -*- coding: utf-8 -*-
"""G3-GOI-32: closure Review vendor trong engines/e_trich_xuat/vendor/review (dữ liệu giả DEMO)."""
import ast
import hashlib
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
VENDOR = GOC / "engines" / "e_trich_xuat" / "vendor"
REVIEW = VENDOR / "review"
NGUON = GOC / "src" / "kho_tri_thuc" / "m4" / "review_goc" / "trich_xuat"
SHA = {
    "__init__": "f200159d6de51d346ea40d0abc2efe3132ac679dc0c31e778c10aa266490be8b",
    "doc_hop_dong": "1a73354377cd5a13aaa9c45254756d54099796150c7ad798ef26cff5e86c556f",  # RÚT GỌN
    "cau_truc": "2817a46ec2fc967d1e64eae1dd68e35047e687a7b654a9c8ce03f106b9aad5c6",
    "kiem_tra": "47ee35567cb7b864a6b3d6825bc90f93a7a26c0c6872a326e99ead9160467f12",
    "logic": "f7cfcf37ff2293d8f8ea994f1ae0a69f57d1d1d9a844f0620f018a3d285a4452",
    "xlsx_mini": "a29ed16811637daa756fcb2640557ec817734d3d2ee617c30deca51d3799857b",
    "xuat": "d255b2d01b67283b3b5febfb6c3f5f937df80c5020531bd04862fc89ad969efb",
    "danh_muc": "f0796984f7b18a4d0d3389b557a6324f3ad59ca488c29ad3284e11ca97ca2ff2",
    "cau_hinh": "8aa6e436e63125369c4c20a3c18753a6ac59b4f2f404b4878b202e34f4a35e04",  # RÚT GỌN

}
SHA_GOC_DOC_HOP_DONG = "bbe8d9579ad9cce2c4b50e77fa734e7fc9826cd7933abe1aad2e5bf8b3d8a98b"
SHA_GOC_CAU_HINH = "53defa8fc52859c2e14cc9a00701fbc055e8eb47e0bb69156ccd8cdcacc58d93"
CAM = ("kho_tri_thuc", "psycopg", "psycopg2", "win32com", "requests", "urllib", "anthropic", "openai",
       "http", "socket", "ai_local", "ai_cloud", "cloud", "may_ai")


def _sha(p):
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


class TestTrichNguon(unittest.TestCase):
    def test_sha_khop(self):
        self.assertEqual(sorted(p.stem for p in REVIEW.glob("*.py")), sorted(SHA))
        for ten, sha in SHA.items():
            self.assertEqual(_sha(REVIEW / (ten + ".py")), sha, ten)
            if ten not in ("cau_hinh", "doc_hop_dong") and (NGUON / (ten + ".py")).exists():
                self.assertEqual(_sha(NGUON / (ten + ".py")), sha, "nguồn " + ten)

    def test_cau_hinh_rut_gon(self):
        if (NGUON / "cau_hinh.py").exists():
            self.assertEqual(_sha(NGUON / "cau_hinh.py"), SHA_GOC_CAU_HINH)
        txt = (REVIEW / "cau_hinh.py").read_text(encoding="utf-8")
        for c in ("http://", "https://", "os.environ"):
            self.assertNotIn(c, txt)
        cam = {"doc_khoa", "luu_khoa", "xoa_khoa", "khoa_an", "_ENV_KHOA", "FILE_KHOA", "luu_cau_hinh", "doc_cau_hinh"}
        ten = set()
        for n in ast.walk(ast.parse(txt)):
            if isinstance(n, ast.Name):
                ten.add(n.id)
            elif isinstance(n, (ast.FunctionDef, ast.ClassDef)):
                ten.add(n.name)
            elif isinstance(n, ast.Attribute):
                ten.add(n.attr)
        self.assertFalse(ten & cam)
        self.assertNotIn("os", ten)

    def test_doc_hop_dong_rut_gon(self):
        if (NGUON / "doc_hop_dong.py").exists():
            self.assertEqual(_sha(NGUON / "doc_hop_dong.py"), SHA_GOC_DOC_HOP_DONG)

    def test_khong_tien_trinh_ngoai(self):
        cam_import = {"subprocess", "ctypes", "win32com", "pythoncom", "multiprocessing"}
        cam_goi = {"system", "startfile", "popen", "Popen"}
        cam_chuoi = ("ComObject", "powershell", "soffice", "Word.Application")
        for p in sorted(REVIEW.glob("*.py")) + [VENDOR / "__init__.py"]:
            txt = p.read_text(encoding="utf-8")
            for c in cam_chuoi:
                self.assertNotIn(c.lower(), txt.lower(), p.name + " " + c)
            for n in ast.walk(ast.parse(txt)):
                if isinstance(n, ast.Import):
                    self.assertFalse({a.name.split(".")[0] for a in n.names} & cam_import, p.name)
                elif isinstance(n, ast.ImportFrom) and n.level == 0:
                    self.assertNotIn((n.module or "").split(".")[0], cam_import, p.name)
                elif isinstance(n, ast.Call):
                    f = n.func
                    ten = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
                    self.assertNotIn(ten, cam_goi, p.name)

    def test_doc_nem_ma_loi_co_dinh(self):
        import tempfile
        ma = ("import importlib.util, sys, os\n"
              "sp = importlib.util.spec_from_file_location('rv', r'%s', submodule_search_locations=[r'%s'])\n"
              "m = importlib.util.module_from_spec(sp); sys.modules['rv'] = m; sp.loader.exec_module(m)\n"
              "import importlib; d = importlib.import_module('rv.doc_hop_dong')\n"
              "f = os.path.join(sys.argv[1], 'DEMO.doc'); open(f, 'wb').write(b'DEMO')\n"
              "try:\n    d.read_contract(f)\nexcept ValueError as e:\n    print(e)\n"
              "assert d.MA_LOI_DOC == 'CAN_CHUYEN_DOC_NGOAI_ENGINE'\n" % (REVIEW / "__init__.py", REVIEW))
        with tempfile.TemporaryDirectory() as tam:
            r = subprocess.run([sys.executable, "-X", "utf8", "-B", "-I", "-c", ma, tam], capture_output=True,
                               text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("CAN_CHUYEN_DOC_NGOAI_ENGINE", r.stdout)

    def test_ast_khong_import_cam(self):
        for p in [VENDOR / "__init__.py"] + sorted(REVIEW.glob("*.py")):
            cay = ast.parse(p.read_text(encoding="utf-8"))
            for n in ast.walk(cay):
                ten = []
                if isinstance(n, ast.Import):
                    ten = [a.name for a in n.names]
                elif isinstance(n, ast.ImportFrom) and n.level == 0:
                    ten = [n.module or ""]
                for t in ten:
                    goc = t.split(".")[0]
                    self.assertNotIn(goc, CAM, "%s import %s" % (p.name, t))
                if isinstance(n, ast.Attribute) and n.attr == "path" and isinstance(n.value, ast.Name) \
                        and n.value.id == "sys":
                    self.fail("%s dùng sys.path" % p.name)

    def test_import_doc_lap_va_ham_thuan(self):
        ma = (
            "import importlib.util, sys\n"
            "sp = importlib.util.spec_from_file_location('rv', r'%s', submodule_search_locations=[r'%s'])\n"
            "m = importlib.util.module_from_spec(sp); sys.modules['rv'] = m; sp.loader.exec_module(m)\n"
            "import importlib\n"
            "kt = importlib.import_module('rv.kiem_tra'); ct = importlib.import_module('rv.cau_truc')\n"
            "importlib.import_module('rv.logic'); importlib.import_module('rv.xuat'); importlib.import_module('rv.danh_muc')\n"
            "importlib.import_module('rv.doc_hop_dong')\n"
            "assert ct.bo_dau('Hợp đồng DEMO') == 'Hop dong DEMO', ct.bo_dau('Hợp đồng DEMO')\n"
            "assert not any(k.startswith('kho_tri_thuc') for k in sys.modules)\n"
            "print('OK')\n" % (REVIEW / "__init__.py", REVIEW))
        r = subprocess.run([sys.executable, "-X", "utf8", "-B", "-I", "-c", ma], capture_output=True,
                           text=True, encoding="utf-8", cwd=str(VENDOR))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("OK", r.stdout)

    def test_khong_xlsx_theo_doi_git(self):
        r = subprocess.run(["git", "-C", str(GOC), "ls-files", "engines/e_trich_xuat/vendor"],
                           capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            self.skipTest("không có git")
        self.assertFalse([x for x in r.stdout.splitlines() if x.lower().endswith(".xlsx")])


if __name__ == "__main__":
    unittest.main()
