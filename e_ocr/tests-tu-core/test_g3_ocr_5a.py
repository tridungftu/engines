"""OCR-5a thuần: CongOCR thật + ABBYY/Core giả, chỉ dữ liệu DEMO tự tạo.

Không xóa tệp thử, không ABBYY/COM/network/PG. Backend giả đổi tên đầu vào
để mô phỏng ABBYY nhận; CongOCR được bật chế độ không xóa của repo.
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from uuid import uuid4
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from kho_tri_thuc.core.phien import MaBiMat
from kho_tri_thuc.core.viec import GiuViec
from kho_tri_thuc.engines.e_ocr.ban_giao import (
    BanGiaoOCR, CAN_DOI_CHIEU, CHO_CORE, DA_BAN_GIAO,
)
from kho_tri_thuc.ha_tang.cong_ocr import CongOCR
from kho_tri_thuc.ha_tang.primitives import DataError
from kho_tri_thuc.m9.ocr_hot_folder import HotFolderM9
from kho_tri_thuc.sdk_core.engine import KenhCore, LoiEngine, SDKEngine


PDF = b"%PDF-1.4\n/Type /Page\nDEMO OCR-5a\n%%EOF"
METADATA = dict(bien_the="ocr_demo", ma_contract="ocr_demo", phien_ban_contract="1",
                trang_thai="DEMO", ly_do=None, revision_truoc=0, nguon=[])


def _docx(raw):
    with io.BytesIO() as buf:
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("word/document.xml", '<document><p>DEMO ' + hashlib.sha256(raw).hexdigest()
                       + '</p></document>')
        return buf.getvalue()


def _cong(goc):
    return CongOCR(goc / "hot_demo", tep_so_trang=goc / "review_demo" / "so_trang.json",
                   thu_muc_dem=goc / "dem_demo", nghi=0.005, cho_nhan=0.5,
                   cho_toi_da=3, on_dinh=0.01)


class AbbyyGia:
    """Chỉ viết kết quả theo đúng mã đầu vào, không thay thuật toán CongOCR."""
    def __init__(self, cong):
        self.d = cong.thu_muc()
        self.nhan = cong.thu_muc_goc / "abbyy_da_nhan_demo"
        self.nhan.mkdir(exist_ok=True)
        self.dung = threading.Event()
        self.cac_ma, self.raw, self.so_tep_in, self.loi = [], [], [], []
        self.thread = threading.Thread(target=self._chay, daemon=True)

    def _chay(self):
        try:
            while not self.dung.wait(0.002):
                tep = list(self.d["in"].iterdir())
                self.so_tep_in.append(len(tep))
                for vao in tep:
                    raw = vao.read_bytes()
                    ma = vao.stem
                    os.replace(vao, self.nhan / vao.name)
                    self.cac_ma.append(ma)
                    self.raw.append(raw)
                    (self.d["out"] / (ma + ".docx")).write_bytes(_docx(raw))
        except BaseException as exc:
            self.loi.append(exc)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *_):
        self.dung.set()
        self.thread.join(5)
        if self.thread.is_alive() or self.loi:
            raise AssertionError("Backend ABBYY DEMO lỗi hoặc không dừng")


class CoreGia(KenhCore):
    def __init__(self, *, loi=False, ack=True, viec_id=None):
        self.loi, self.ack = loi, ack
        self.raw = []
        self.du_lieu = []
        self.lease = GiuViec(viec_id=uuid4() if viec_id is None else viec_id,
            buoc_viec_id=uuid4(), lan_thu_id=uuid4(),
            phap_nhan_id=uuid4(), module="demo", hanh_dong="DEMO:OCR:LAP",
            instance_id=uuid4(), the_he=1,
            giu_den=datetime.now(timezone.utc) + timedelta(minutes=2),
            ma=MaBiMat("d" * 43))

    def sdk(self):
        return SDKEngine(self.lease, kenh_core=self)

    def goi(self, operation, giu_viec, **payload):
        assert operation == "ghi_ket_qua"
        self.raw.append(payload["luong"].read())
        self.du_lieu.append(payload["du_lieu"])
        if self.loi:
            raise RuntimeError("DEMO mat ACK")
        # Mô phỏng ACK sau commit; biên nhận tạm chưa kết thúc bàn giao.
        return {"da_ban_giao": True, "ket_qua_id": "DEMO_DA_NHAN"} if self.ack else None


class OCR5aTests(unittest.TestCase):
    def setUp(self):
        self.goc = Path(tempfile.mkdtemp(prefix="g3_ocr_5a_demo_"))
        self.cong = _cong(self.goc)
        self.core = CoreGia()
        self.viec_id = self.core.lease.viec_id
        self.patches = [patch.dict(os.environ, {"CODEX_NO_DELETE_FILES": "1"}),
                        patch.object(CongOCR, "_don_sau")]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)

    def _adapter(self, viec_id=None, cong=None):
        return BanGiaoOCR(self.cong if cong is None else cong,
                         viec_id=self.viec_id if viec_id is None else viec_id,
                         thu_muc_ban_giao=self.goc / "ban_giao_demo")

    def _so(self):
        return json.loads(self.cong.tep_so_trang.read_text(encoding="utf-8"))

    def _dat_so(self, trang):
        self.cong.tep_so_trang.parent.mkdir(parents=True, exist_ok=True)
        self.cong.tep_so_trang.write_text(json.dumps([[time.time(), trang]]), encoding="utf-8")

    def _loi(self, ma, ham):
        with self.assertRaises(DataError) as bat:
            ham()
        self.assertEqual(bat.exception.code, ma)

    def _ban_giao(self, adapter, core=None):
        return adapter.ban_giao(sdk=(self.core if core is None else core).sdk(),
                               du_lieu=METADATA, revision_tep_truoc=0)

    def test_chi_dung_cong_duoc_tiem_va_khong_tao_so_thu_hai(self):
        with patch.object(CongOCR, "__init__", side_effect=AssertionError("Tạo cổng thứ hai")):
            adapter = self._adapter()
        self.assertIs(adapter.cong_ocr, self.cong)
        self.assertEqual(adapter.trang_thai(), "chua_chay")
        with AbbyyGia(self.cong) as abbyy:
            self.assertEqual(adapter.ocr(PDF, ".PDF"), _docx(PDF))
        self.assertEqual(len(abbyy.cac_ma), 1)
        self.assertEqual(sum(x[1] for x in self._so()), 1)
        self.assertFalse(any("trang" in p.name for p in adapter.thu_muc.iterdir()
                             if p.name != "trang_thai.json"))

    def test_hai_duong_tuong_tranh_mot_chu_hot_folder_khong_trung_in_out(self):
        # Đường M9/Review-M4 và e_ocr dùng cùng root, sổ và đệm do Core cấp.
        cu = HotFolderM9(self.cong.thu_muc_goc, thu_muc_du_lieu=self.goc / "review_demo",
                        tep_so_trang=self.cong.tep_so_trang, thu_muc_dem=self.cong.thu_muc_dem,
                        nghi=0.005, cho_nhan=0.5, cho_toi_da=3, on_dinh=0.01)
        self.assertIs(cu._khoa, self.cong._khoa)
        self._dat_so(4998)
        adapter = self._adapter()
        raw_cu = PDF + b" DEMO cu"
        bat_dau = threading.Barrier(2)

        def goi(cong, raw):
            bat_dau.wait(5)
            return cong.ocr(raw, "pdf")

        with AbbyyGia(self.cong) as abbyy, ThreadPoolExecutor(2) as pool:
            a = pool.submit(goi, cu, raw_cu)
            b = pool.submit(goi, adapter, PDF)
            self.assertEqual(a.result(10), _docx(raw_cu))
            self.assertEqual(b.result(10), _docx(PDF))
        self.assertEqual(sum(x[1] for x in self._so()), 5000)
        self.assertEqual(len(set(abbyy.cac_ma)), 2)
        self.assertEqual(max(abbyy.so_tep_in), 1)
        self.assertEqual(set(abbyy.raw), {raw_cu, PDF})
        self._loi("OCR_HET_HAN_MUC", lambda: self._adapter(uuid4()).ocr(PDF + b" DEMO them", "pdf"))
        self.assertEqual(sum(x[1] for x in self._so()), 5000)

    def test_tranh_trang_cuoi_khong_vuot_han_muc(self):
        self._dat_so(4999)
        bat_dau = threading.Barrier(2)

        def goi(cong, raw):
            bat_dau.wait(5)
            try:
                return cong.ocr(raw, "pdf")
            except DataError as exc:
                return exc.code

        with AbbyyGia(self.cong) as abbyy, ThreadPoolExecutor(2) as pool:
            a = pool.submit(goi, _cong(self.goc), PDF + b" DEMO cu")
            b = pool.submit(goi, self._adapter(), PDF)
            ket_qua = [a.result(10), b.result(10)]
        self.assertEqual(ket_qua.count("OCR_HET_HAN_MUC"), 1)
        self.assertEqual(sum(isinstance(x, bytes) for x in ket_qua), 1)
        self.assertEqual(len(abbyy.cac_ma), 1)
        self.assertEqual(sum(x[1] for x in self._so()), 5000)

    def test_hai_ben_cung_noi_dung_dung_dem_khong_tinh_hai_lan(self):
        bat_dau = threading.Barrier(2)

        def goi(cong):
            bat_dau.wait(5)
            return cong.ocr(PDF, "pdf")

        with AbbyyGia(self.cong) as abbyy, ThreadPoolExecutor(2) as pool:
            a = pool.submit(goi, _cong(self.goc))
            b = pool.submit(goi, self._adapter())
            self.assertEqual(a.result(10), b.result(10))
        self.assertEqual(len(abbyy.cac_ma), 1)
        self.assertEqual(sum(x[1] for x in self._so()), 1)

    def test_hai_adapter_cung_viec_chi_gui_mot_lan(self):
        with AbbyyGia(self.cong) as abbyy, ThreadPoolExecutor(2) as pool:
            a = pool.submit(self._adapter().ocr, PDF, "pdf")
            b = pool.submit(self._adapter().ocr, PDF, "pdf")
            self.assertEqual(a.result(10), b.result(10))
        self.assertEqual(len(abbyy.cac_ma), 1)
        self.assertEqual(sum(x[1] for x in self._so()), 1)

    def test_crash_tien_trinh_sau_wait_truoc_ghi_dem_khong_gui_lai_hoan_trang(self):
        # os._exit bỏ qua finally: đã nhận DOCX, CongOCR chưa ghi đệm và
        # adapter chưa nhận kết quả, tương đương cửa sổ crash sau wait().
        with AbbyyGia(self.cong) as abbyy:
            p = subprocess.run([sys.executable, "-B", "-X", "utf8", str(Path(__file__).resolve()),
                                "--crash-demo", str(self.goc), str(self.viec_id)],
                               capture_output=True, timeout=15)
        self.assertEqual(p.returncode, 73, p.stderr.decode("utf-8", errors="replace"))
        self.assertEqual(len(abbyy.cac_ma), 1)
        so = self._so()
        self.assertEqual(sum(x[1] for x in so), 1)
        self.assertFalse((self.cong.thu_muc_dem / (hashlib.sha256(PDF).hexdigest() + ".docx")).exists())
        adapter = self._adapter(cong=_cong(self.goc))
        self.assertEqual(adapter.trang_thai(), CAN_DOI_CHIEU)
        with patch.object(adapter.cong_ocr, "ocr", side_effect=AssertionError("Tự gửi lại")):
            self._loi("OCR_CAN_DOI_CHIEU", lambda: adapter.ocr(PDF, "pdf"))
            self._loi("OCR_CAN_DOI_CHIEU", lambda: self._ban_giao(adapter))
        self.assertEqual(self._so(), so)
        self.assertIn("cần đối chiếu", (adapter.thu_muc / "trang_thai.json").read_text(encoding="utf-8"))

    def test_giu_docx_qua_restart_chi_danh_dau_sau_ack(self):
        adapter = self._adapter()
        with AbbyyGia(self.cong):
            docx = adapter.ocr(PDF, "pdf")
        self.assertEqual(adapter.trang_thai(), CHO_CORE)
        adapter = self._adapter(cong=_cong(self.goc))
        with patch.object(adapter.cong_ocr, "ocr", side_effect=AssertionError("OCR lại")):
            self.assertEqual(adapter.ocr(PDF, "pdf"), docx)
            self.assertEqual(self._ban_giao(adapter),
                             {"da_ban_giao": True, "ket_qua_id": "DEMO_DA_NHAN"})
        self.assertEqual(adapter.trang_thai(), DA_BAN_GIAO)
        self.assertEqual(self.core.raw, [docx])
        self.assertEqual(self.core.du_lieu, [METADATA])
        self.assertFalse(self._ban_giao(adapter))
        self.assertEqual(self.core.raw, [docx])
        self.assertEqual((adapter.thu_muc / "ket_qua.docx").read_bytes(), docx)
        self.assertEqual(sum(x[1] for x in self._so()), 1)

    def test_mat_ack_hoac_mat_lease_khong_ban_giao_khong_hoan_khong_ocr_lai(self):
        adapter = self._adapter()
        with AbbyyGia(self.cong):
            docx = adapter.ocr(PDF, "pdf")
        so = self._so()
        core = CoreGia(loi=True, viec_id=self.viec_id)
        with self.assertRaises(LoiEngine):
            self._ban_giao(adapter, core)
        self.assertEqual(core.raw, [docx])  # Không vòng lặp retry.
        self.assertEqual(adapter.trang_thai(), CHO_CORE)
        self._loi("OCR_CHUA_XAC_NHAN", lambda: self._ban_giao(
            adapter, CoreGia(ack=False, viec_id=self.viec_id)))
        from dataclasses import replace
        core.lease = replace(core.lease, giu_den=datetime.now(timezone.utc) - timedelta(seconds=1))
        with self.assertRaisesRegex(LoiEngine, "VIEC_MAT_LEASE"):
            self._ban_giao(adapter, core)
        self.assertEqual(core.raw, [docx])
        self.assertEqual(adapter.trang_thai(), CHO_CORE)
        self.assertEqual(self._so(), so)
        self.assertEqual((adapter.thu_muc / "ket_qua.docx").read_bytes(), docx)

    def test_cung_ma_khac_noi_dung_bi_chan_truoc_cong(self):
        adapter = self._adapter()
        with AbbyyGia(self.cong):
            adapter.ocr(PDF, "pdf")
        with patch.object(self.cong, "ocr") as goi:
            self._loi("OCR_VIEC_XUNG_DOT", lambda: adapter.ocr(PDF + b" DEMO doi", "pdf"))
            self._loi("OCR_VIEC_XUNG_DOT", lambda: adapter.ocr(PDF, "png"))
        goi.assert_not_called()

    def test_nhat_ky_hong_khong_dat_ve_chua_chay(self):
        adapter = self._adapter()
        adapter.thu_muc.mkdir(parents=True)
        (adapter.thu_muc / "trang_thai.json").write_bytes(b"{DEMO hong")
        with patch.object(self.cong, "ocr") as goi:
            self._loi("OCR_CAN_DOI_CHIEU", lambda: adapter.ocr(PDF, "pdf"))
        goi.assert_not_called()

    def test_ket_qua_hong_hoac_mat_khong_ocr_lai(self):
        adapter = self._adapter()
        with AbbyyGia(self.cong):
            adapter.ocr(PDF, "pdf")
        (adapter.thu_muc / "ket_qua.docx").write_bytes(_docx(b"DEMO ket qua khac"))
        self._loi("OCR_CAN_DOI_CHIEU", lambda: self._ban_giao(adapter))
        self.assertEqual(adapter.trang_thai(), CAN_DOI_CHIEU)
        self.assertEqual(self.core.raw, [])
        self.assertEqual(sum(x[1] for x in self._so()), 1)

    def test_loi_truoc_gui_chi_cong_hoan_trang_adapter_khong_gui_lai(self):
        # Không backend: CongOCR rút được đầu vào rồi hoàn đúng bản ghi.
        self.cong.cho_nhan = 0.02
        adapter = self._adapter()
        self._loi("OCR_KHONG_NHAN", lambda: adapter.ocr(PDF, "pdf"))
        self.assertEqual(self._so(), [])
        self.assertEqual(adapter.trang_thai(), CAN_DOI_CHIEU)
        self._loi("OCR_CAN_DOI_CHIEU", lambda: adapter.ocr(PDF, "pdf"))

    def test_dau_vao_khong_hop_le_khong_tao_y_dinh_gui(self):
        adapter = self._adapter()
        for raw, duoi in ((b"", "pdf"), (PDF, "docx"), (PDF, None)):
            self._loi("OCR_DINH_DANG", lambda: adapter.ocr(raw, duoi))
        self.assertFalse(adapter.thu_muc.exists())
        with self.assertRaises(TypeError):
            BanGiaoOCR(object(), viec_id=uuid4(), thu_muc_ban_giao=self.goc)
        for viec in ("../DEMO", None, "DEMO"):
            with self.assertRaises(ValueError):
                BanGiaoOCR(self.cong, viec_id=viec, thu_muc_ban_giao=self.goc)
        with self.assertRaises(TypeError):
            adapter.ban_giao(sdk=object(), du_lieu=METADATA, revision_tep_truoc=0)


def _crash_demo(goc, viec_id):
    os.environ["CODEX_NO_DELETE_FILES"] = "1"
    cong = _cong(Path(goc))
    wait = cong._chay_hot_folder

    def wait_roi_crash(*args, **kwargs):
        wait(*args, **kwargs)
        os._exit(73)

    cong._chay_hot_folder = wait_roi_crash
    cong._don_sau = lambda *_: None
    BanGiaoOCR(cong, viec_id=viec_id,
               thu_muc_ban_giao=Path(goc) / "ban_giao_demo").ocr(PDF, "pdf")


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--crash-demo":
        _crash_demo(sys.argv[2], sys.argv[3])
    else:
        unittest.main()
