"""OCR-4b: ABBYY/phiên/ACL giả, toàn bộ dữ liệu DEMO trong RAM.

Không tạo tài khoản, gọi ABBYY/COM/mạng/PG hoặc đọc cấu hình/khóa nguồn.
Không xóa tệp. Khởi chạy và ACL Windows thực: CHUA_KIEM (G2-33b).
"""

from dataclasses import replace
import hashlib
import io
from pathlib import Path
import pickle
import sys
import threading
import traceback
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from kho_tri_thuc.engines.e_ocr.abbyy import (
    BackendABBYY, CauHinhABBYY, DanhTinhWindows, LoiABBYY,
)
from kho_tri_thuc.engines.e_ocr.van_ban import trich_van_ban
from kho_tri_thuc.ha_tang.cong_ocr import CongOCR


CANARY = 'DEMO_OCR4B_SECRET_KHONG_LO'


def _sid(rid):
    return f'S-1-5-21-111-222-333-{rid}'


def _docx():
    with io.BytesIO() as out:
        with zipfile.ZipFile(out, 'w') as z:
            z.writestr('word/document.xml', '<document>DEMO 0001 1.234 đồng</document>')
        return out.getvalue()


class ABBYYGia(CongOCR):
    """Cùng interface chủ OCR; không tạo thư mục/sổ/HotFolderClient."""

    def __init__(self):
        self.goi = Mock(return_value=_docx())

    def ocr(self, raw, duoi, *, huy=None):
        return self.goi(raw, duoi, huy=huy)


class ABBYYTests(unittest.TestCase):
    def setUp(self):
        self.cfg = CauHinhABBYY(_sid(1004), _sid(1000), _sid(1001),
                               (_sid(1002), _sid(1003), _sid(1005)), 4, 1)
        self.engine = DanhTinhWindows(self.cfg.sid_ocr, 4, True, True)
        self.abbyy = replace(self.engine)
        self.cong = ABBYYGia()
        self.phien = Mock(side_effect=lambda: (self.engine, self.abbyy))
        self.acl = Mock(return_value=True)
        self.backend = self.tao()

    def tao(self, **kwargs):
        return BackendABBYY(**(dict(cau_hinh=self.cfg, cong_ocr=self.cong,
                                    kiem_phien=self.phien, kiem_acl=self.acl) | kwargs))

    def bi_chan(self, ma):
        with self.assertRaises(LoiABBYY) as cm:
            self.backend.ocr(b'%PDF-DEMO', 'pdf')
        self.assertEqual(cm.exception.ma, ma)
        self.cong.goi.assert_not_called()

    def test_phien_rieng_goi_dung_mot_cong_khong_doc_nguon(self):
        huy = threading.Event()
        with patch('builtins.open', side_effect=AssertionError('Cấm đọc cấu hình')):
            self.assertTrue(self.backend.san_sang())
            raw = self.backend.ocr(b'%PDF-DEMO', 'pdf', huy=huy)
        self.assertEqual(raw, self.cong.goi.return_value)
        self.cong.goi.assert_called_once_with(b'%PDF-DEMO', 'pdf', huy=huy)
        self.assertEqual(self.phien.call_count, 2)
        self.acl.assert_called_with(self.cong, self.engine, self.abbyy)

    def test_ghep_adapter_van_ban_giu_hash_nguon_khong_goi_ngoai(self):
        raw = b'%PDF-DEMO'
        tep_id = '10000000-0000-4000-8000-000000000001'
        docx_id = '10000000-0000-4000-8000-000000000002'
        phan_hoi_id = '10000000-0000-4000-8000-000000000003'
        ref = dict(contract='tham_chieu_tep.v1', phien_ban='1.0.0',
                   tep_id=tep_id, ten_tep='DEMO.pdf', mime='application/pdf',
                   kich_thuoc=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                   het_han_luc=None)
        text = 'DEMO 0001 1.234 đồng'
        extract = Mock(return_value=SimpleNamespace(text=text, warnings=[], ocr_pages=0))
        layout = Mock(return_value={'units': [{'id': 'p1-u0', 'text': text}]})
        with patch('socket.socket', side_effect=AssertionError('Cấm mạng')), \
                patch('subprocess.Popen', side_effect=AssertionError('Cấm gọi nguồn')), \
                patch('builtins.open', side_effect=AssertionError('Cấm đọc cấu hình')):
            result = trich_van_ban(raw, ref, cong_ocr=self.backend,
                                  tep_docx_id=docx_id, phan_hoi_nguon_tep_id=phan_hoi_id,
                                  extract_docx=extract, word_layout=layout)
        self.assertEqual(result.van_ban['van_ban'], text)
        self.assertEqual(result.van_ban['nguon_tep_ids'], [tep_id, docx_id])
        self.assertEqual(result.phan_hoi_nguon['tham_chieu_tep']['sha256'], ref['sha256'])
        self.assertEqual(result.docx, self.cong.goi.return_value)
        self.cong.goi.assert_called_once_with(raw, 'pdf', huy=None)
        self.assertEqual(layout.call_args.kwargs['embedded_pages'], [])

    def test_sid_engine_khac_ocr_bi_chan(self):
        for sid in (self.cfg.sid_core, self.cfg.sid_module, *self.cfg.sid_engine_khac):
            with self.subTest(sid=sid):
                self.engine = replace(self.engine, sid=sid)
                self.bi_chan('ABBYY_PHIEN_KHONG_HOP_LE')

    def test_abbyy_khong_dung_tai_khoan_bi_chan(self):
        self.abbyy = replace(self.abbyy, sid=self.cfg.sid_core)
        self.bi_chan('ABBYY_PHIEN_KHONG_HOP_LE')

    def test_phien_service_phien_core_phien_khac_bi_chan(self):
        for truong in ('engine', 'abbyy'):
            goc = getattr(self, truong)
            for phien_id in (0, 1, 5, True, 4.0):
                with self.subTest(truong=truong, phien_id=phien_id):
                    setattr(self, truong, replace(goc, phien_id=phien_id))
                    self.bi_chan('ABBYY_PHIEN_KHONG_HOP_LE')
            setattr(self, truong, goc)

    def test_khong_man_hinh_hoac_khong_han_che_bi_chan(self):
        for truong in ('engine', 'abbyy'):
            goc = getattr(self, truong)
            for ten in ('han_che', 'co_man_hinh'):
                for gia_tri in (False, None, 1, 'CHUA_KIEM'):
                    with self.subTest(truong=truong, ten=ten, gia_tri=gia_tri):
                        setattr(self, truong, replace(goc, **{ten: gia_tri}))
                        self.bi_chan('ABBYY_PHIEN_KHONG_HOP_LE')
            setattr(self, truong, goc)

    def test_acl_thieu_bang_chung_khong_duoc_coi_la_dat(self):
        for ket_qua in (False, None, 1, 'CHUA_KIEM', {'dat': True}):
            with self.subTest(ket_qua=ket_qua):
                self.acl.return_value = ket_qua
                self.bi_chan('ABBYY_ACL_CHUA_DAT')

    def test_logout_hoac_acl_doi_sau_ready_van_chan(self):
        self.assertTrue(self.backend.san_sang())
        self.acl.return_value = False
        self.bi_chan('ABBYY_ACL_CHUA_DAT')
        self.acl.return_value = True
        self.abbyy = replace(self.abbyy, phien_id=0)
        self.bi_chan('ABBYY_PHIEN_KHONG_HOP_LE')

    def test_seam_hong_khong_lo_canary_exception_log_repr(self):
        for seam in (self.phien, self.acl, self.cong.goi):
            with self.subTest(seam=type(seam).__name__):
                exc = RuntimeError(CANARY)
                seam.side_effect = exc
                out, err = io.StringIO(), io.StringIO()
                with patch('sys.stdout', out), patch('sys.stderr', err):
                    try:
                        self.backend.ocr(b'%PDF-DEMO', 'pdf')
                    except LoiABBYY as loi:
                        self.assertNotIn(CANARY, ''.join(traceback.format_exception(loi)))
                        self.assertIsNone(loi.__context__)
                        self.assertIsNone(loi.__cause__)
                    else:
                        self.fail('Seam lỗi phải chặn')
                self.assertNotIn(CANARY, out.getvalue() + err.getvalue())
                self.assertNotIn(CANARY, repr(exc))
                self.assertNotIn(CANARY, repr(self.backend))
                seam.side_effect = ((lambda: (self.engine, self.abbyy))
                                    if seam is self.phien else None)
        self.assertEqual(self.cong.goi.call_count, 1)

    def test_phien_sai_hinh_dang_bi_chan(self):
        for du_lieu in (None, (), (self.engine,), ('ktt_e_ocr', 'ktt_e_ocr')):
            with self.subTest(du_lieu=du_lieu):
                self.phien.side_effect = None
                self.phien.return_value = du_lieu
                self.bi_chan('ABBYY_PHIEN_KHONG_HOP_LE')

    def test_cau_hinh_sid_trung_hoac_khong_phai_sid_bi_chan(self):
        for thay in (dict(sid_ocr=self.cfg.sid_core), dict(sid_core=self.cfg.sid_module),
                     dict(sid_engine_khac=(self.cfg.sid_ocr,)),
                     dict(sid_engine_khac=list(self.cfg.sid_engine_khac)),
                     dict(sid_ocr='ktt_e_ocr'), dict(sid_ocr=CANARY),
                     dict(phien_ocr=0), dict(phien_ocr=True), dict(phien_ocr=1),
                     dict(phien_core=-1), dict(phien_core=False)):
            with self.subTest(thay=thay):
                with self.assertRaises(LoiABBYY) as cm:
                    self.tao(cau_hinh=replace(self.cfg, **thay))
                self.assertEqual(cm.exception.ma, 'ABBYY_CAU_HINH_SAI')
                self.assertNotIn(CANARY, str(cm.exception))
        self.phien.assert_not_called()

    def test_thieu_seam_khong_tu_tao_cong_hoac_doc_cau_hinh(self):
        for thay in (dict(cau_hinh={}), dict(cong_ocr=None),
                     dict(kiem_phien=None), dict(kiem_acl=None)):
            with self.subTest(thay=thay), self.assertRaises(LoiABBYY):
                self.tao(**thay)
        self.phien.assert_not_called()

    def test_docx_hong_khong_tra_thanh_cong_khong_tu_gui_lai(self):
        self.cong.goi.return_value = b'DEMO khong phai DOCX'
        with self.assertRaises(LoiABBYY) as cm:
            self.backend.ocr(b'%PDF-DEMO', 'pdf')
        self.assertEqual(cm.exception.ma, 'ABBYY_DOCX_KHONG_HOP_LE')
        self.cong.goi.assert_called_once()

    def test_khong_serialize_seam_co_the_giu_bi_mat_ram(self):
        with self.assertRaises(TypeError):
            pickle.dumps(self.backend)

    @unittest.skip('CHUA_KIEM: tài khoản/ACL/DPAPI/Job/phiên Windows thật chờ G2-33b')
    def test_cach_ly_windows_that(self):
        pass


if __name__ == '__main__':
    unittest.main()
