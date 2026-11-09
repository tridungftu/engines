"""G3-GOI-16: identity, ranh giới import và khóa/ACK/timeout/hủy bằng mock.

Dữ liệu giả trong RAM và thư mục tạm rỗng; không chạy ABBYY, không xóa tệp.
"""

import ast
import errno
import importlib
from importlib.util import resolve_name
import io
import os
from pathlib import Path
import pickle
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, call, mock_open, patch
import zipfile

from kho_tri_thuc.engines.e_ocr.lib import cong_ocr as moi
from kho_tri_thuc.ha_tang import cong_ocr as cu
from kho_tri_thuc.sdk_core.primitives import DataError


LIB = Path(__file__).resolve().parents[1] / 'engines/e_ocr/lib'


class BridgeOCRTests(unittest.TestCase):
    def test_module_va_moi_doi_tuong_cung_identity(self):
        self.assertIs(cu, moi)
        self.assertEqual(Path(moi.__file__).resolve(), (LIB / 'cong_ocr.py').resolve())
        for ten, obj in vars(moi).items():
            with self.subTest(ten=ten):
                self.assertIs(getattr(cu, ten), obj)
        self.assertIs(cu.DataError, DataError)
        self.assertIs(cu._KHOA, moi._KHOA)

    def test_patch_duong_cu_tac_dong_loi_moi(self):
        with patch('kho_tri_thuc.ha_tang.cong_ocr._ma_moi', return_value='DEMO') as tao:
            self.assertEqual(moi._ma_moi(), 'DEMO')
        tao.assert_called_once_with()

    def test_ten_legacy_va_pickle_cung_lop(self):
        self.assertEqual(moi.CongOCR.__module__, 'kho_tri_thuc.ha_tang.cong_ocr')
        self.assertIs(pickle.loads(pickle.dumps(moi.CongOCR)), cu.CongOCR)
        self.assertIs(pickle.loads(pickle.dumps(moi.DataError)), DataError)

    def test_ast_loi_khong_import_ha_tang_core_nguon(self):
        cam = ('kho_tri_thuc.ha_tang', 'kho_tri_thuc.core', 'kho_tri_thuc.nguon')
        for tep in sorted(LIB.rglob('*.py')):
            tuong_doi = tep.relative_to(LIB).with_suffix('').parts
            package = '.'.join(('kho_tri_thuc', 'engines', 'e_ocr', 'lib',
                                *tuong_doi[:-1]))
            for node in ast.walk(ast.parse(tep.read_text(encoding='utf-8'))):
                with self.subTest(tep=tep.name, dong=getattr(node, 'lineno', 0)):
                    names = []
                    if isinstance(node, ast.Import):
                        names = [item.name for item in node.names]
                    elif isinstance(node, ast.ImportFrom):
                        ten = node.module or ''
                        if node.level:
                            ten = resolve_name('.' * node.level + ten, package)
                        names = [ten, *(ten + '.' + item.name for item in node.names)]
                    elif isinstance(node, ast.Call):
                        # Không lách static import qua tải động.
                        ham = node.func
                        self.assertFalse(isinstance(ham, ast.Name) and ham.id == '__import__')
                        self.assertFalse(isinstance(ham, ast.Attribute) and ham.attr == 'import_module')
                    for ten in names:
                        self.assertFalse(any(ten == x or ten.startswith(x + '.') for x in cam), ten)


class KhoaOCRTests(unittest.TestCase):
    def test_khoa_tep_tranh_chap_thu_lai_va_nha_khoa(self):
        khoa = Mock()
        khoa.acquire.side_effect = [False, True]
        f = mock_open()
        f.return_value.tell.return_value = 0
        if os.name == 'nt':
            os_module = importlib.import_module('msvcrt')
            ten_ham, mo_khoa = 'locking', os_module.LK_UNLCK
        else:
            os_module = importlib.import_module('fcntl')
            ten_ham, mo_khoa = 'lockf', os_module.LOCK_UN
        with patch.object(moi, '_khoa_cho', return_value=khoa), \
                patch.object(Path, 'mkdir'), patch.object(Path, 'open', f), \
                patch.object(moi.time, 'sleep') as nghi, \
                patch.object(os_module, ten_ham,
                             side_effect=[OSError(errno.EACCES, 'Dữ liệu giả'), None, None]) as os_khoa:
            with self.assertRaisesRegex(RuntimeError, 'Dữ liệu giả'):
                with cu._khoa_tep(Path('DEMO/in.lock'), 0.01):
                    raise RuntimeError('Dữ liệu giả')
        self.assertEqual(khoa.acquire.call_args_list, [call(timeout=0.01)] * 2)
        khoa.release.assert_called_once_with()
        nghi.assert_called_once_with(0.01)
        self.assertEqual(os_khoa.call_count, 3)
        self.assertEqual(os_khoa.call_args.args[1], mo_khoa)
        f.return_value.write.assert_called_once_with(b'\0')

    def test_huy_khi_cho_khoa_khong_mo_tep(self):
        khoa = Mock()
        khoa.acquire.return_value = False
        huy = threading.Event()
        huy.set()
        with patch.object(moi, '_khoa_cho', return_value=khoa), \
                patch.object(Path, 'open') as mo:
            with self.assertRaises(DataError) as bat:
                with moi._khoa_tep(Path('DEMO/in.lock'), 0.01, huy):
                    self.fail('Không được vào khóa sau hủy')
        self.assertEqual(bat.exception.code, 'OCR_HUY')
        mo.assert_not_called()
        khoa.release.assert_not_called()

    def test_cua_cu_va_moi_dung_chung_khoa_hot_folder(self):
        cau_hinh = dict(tep_so_trang=Path('DEMO/so.json'), thu_muc_dem=Path('DEMO/dem'))
        mot = cu.CongOCR(Path('DEMO/hot'), **cau_hinh)
        hai = moi.CongOCR(Path('DEMO/hot'), **cau_hinh)
        self.assertIs(mot._khoa, hai._khoa)


class HotFolderOCRTests(unittest.TestCase):
    def setUp(self):
        self.cong = moi.CongOCR.__new__(moi.CongOCR)
        self.cong.cho_nhan, self.cong.cho_toi_da = 1, 10
        self.cong.nghi, self.cong.on_dinh = 0.01, 0.5
        self.d = {ten: Path('DEMO') / ten for ten in ('in', 'out', 'tam', 'nhan')}
        self.ma = 'hd20261105000000_123456'
        self.raw = b'Du lieu gia OCR'
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as tep:
            tep.writestr('word/document.xml', '<document>Dữ liệu giả</document>')
        self.docx = buf.getvalue()
        self.replace = self._patch(moi.os, 'replace')
        self._patch(moi.os, 'fsync')
        self._patch(Path, 'open', mock_open(read_data=self.docx))
        self.exists = self._patch(Path, 'exists', return_value=False)
        self.stat = self._patch(Path, 'stat', side_effect=FileNotFoundError)
        self.gio = self._patch(moi.time, 'monotonic')
        self.nghi = self._patch(moi.time, 'sleep')
        self.rut = self._patch(self.cong, '_rut', return_value=False)
        self.don = self._patch(self.cong, '_don')
        self.don_sau = self._patch(self.cong, '_don_sau')
        self.hoan = self._patch(self.cong, '_hoan_trang')
        self._patch(self.cong, '_loi_abbyy', return_value=False)

    def _patch(self, obj, ten, *args, **kwargs):
        p = patch.object(obj, ten, *args, **kwargs)
        value = p.start()
        self.addCleanup(p.stop)
        return value

    def _chay(self, huy=None):
        return self.cong._chay_hot_folder(self.raw, 'pdf', self.d, self.ma, huy)

    def _loi(self, code, huy=None):
        with self.assertRaises(DataError) as bat:
            self._chay(huy)
        self.assertEqual(bat.exception.code, code)
        self.don.assert_called_once_with(self.d, self.ma)

    def test_qua_cho_nhan_rut_duoc_thi_hoan_trang(self):
        goc = Path(tempfile.mkdtemp(prefix='ocr-cong-DEMO-'))
        for ten in ('out', 'nhan'):
            self.d[ten] = goc / ten
            self.d[ten].mkdir()
        self.exists.return_value = True
        self.gio.side_effect = [0, 1]
        self.rut.return_value = True
        self._loi('OCR_KHONG_NHAN')
        self.rut.assert_called_once_with(self.d, self.ma, 'pdf')
        self.hoan.assert_called_once_with(self.ma)
        self.don_sau.assert_not_called()

    def test_qua_cho_nhan_output_khong_ton_tai_giu_chua_ro_khong_hoan_trang(self):
        goc = Path(tempfile.mkdtemp(prefix='ocr-cong-DEMO-'))
        self.d['out'] = goc / 'out-khong-ton-tai'
        self.d['nhan'] = goc / 'nhan'
        self.d['nhan'].mkdir()
        with self.assertRaises(FileNotFoundError):
            list(self.d['out'].iterdir())
        self.exists.return_value = True
        self.gio.side_effect = [0, 1]
        self.rut.return_value = True
        self._loi('OCR_KHONG_NHAN')
        self.rut.assert_called_once_with(self.d, self.ma, 'pdf')
        self.hoan.assert_not_called()
        self.don_sau.assert_not_called()

    def test_da_ack_qua_gio_khong_hoan_trang(self):
        self.gio.side_effect = [0, 1, 10]
        self._loi('OCR_QUA_GIO')
        self.hoan.assert_not_called()
        self.don_sau.assert_called_once_with(self.d['out'], self.ma)

    def test_khong_rut_duoc_coi_da_nhan_khong_bao_khong_nhan(self):
        self.exists.return_value = True
        self.gio.side_effect = [0, 1, 10]
        self._loi('OCR_QUA_GIO')
        self.assertEqual(self.rut.call_count, 2)
        self.hoan.assert_not_called()

    def test_huy_truoc_publish_khong_gui_va_hoan_trang(self):
        huy = threading.Event()
        huy.set()
        self._loi('OCR_HUY', huy)
        self.replace.assert_not_called()
        self.hoan.assert_called_once_with(self.ma)
        self.don_sau.assert_not_called()

    def test_huy_sau_ack_khong_hoan_trang(self):
        huy = Mock()
        huy.is_set.side_effect = [False, False, True]
        self.gio.side_effect = [0, 1]
        self._loi('OCR_HUY', huy)
        huy.wait.assert_called_once_with(0.01)
        self.hoan.assert_not_called()
        self.don_sau.assert_called_once_with(self.d['out'], self.ma)

    def test_ack_ket_qua_on_dinh_moi_nhan_docx(self):
        self.gio.side_effect = [0, 1, 2]
        self.stat.side_effect = None
        self.stat.return_value = SimpleNamespace(st_size=len(self.docx), st_mtime_ns=123)
        self.assertEqual(self._chay(), self.docx)
        self.assertEqual(self.replace.call_args_list, [
            call(self.d['tam'] / (self.ma + '.part'), self.d['in'] / (self.ma + '.pdf')),
            call(self.d['out'] / (self.ma + '.docx'), self.d['nhan'] / (self.ma + '.docx')),
        ])
        self.nghi.assert_called_once_with(0.01)
        self.hoan.assert_not_called()
        self.don.assert_called_once_with(self.d, self.ma)
        self.don_sau.assert_called_once_with(self.d['out'], self.ma)


if __name__ == '__main__':
    unittest.main()
