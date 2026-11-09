"""OCR-KN1: filesystem, khóa, đồng hồ và Timer đều giả trong RAM.

Không tạo thư mục/tệp, xóa tệp thật, mở socket hoặc gọi máy ABBYY.
PDF lớp chữ DEMO và DOCX được tạo trong RAM bằng bộ sinh đã có/stdlib.
"""

from contextlib import contextmanager
import hashlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from uuid import UUID
import zipfile

import pdfplumber  # Nạp dependency trước khi chặn toàn bộ filesystem.

from kho_tri_thuc.engines.e_ocr.lib import cong_ocr as ocr
from kho_tri_thuc.engines.e_ocr import cau_noi_abbyy as cn
from kho_tri_thuc.engines.e_ocr import ban_giao as bg
from kho_tri_thuc.engines.e_ocr.chon_nguon import ChonNguonOCR
from kho_tri_thuc.engines.e_ocr.lop_chu import doc_lop_chu
from kho_tri_thuc.engines.e_ocr.tests.test_lop_chu import CHU, TIEN, NGAY, pdf_demo
from kho_tri_thuc.sdk_core.primitives import DataError


MA = 'hd20261107000000_123456'
MA_KHAC = 'hd20261107000000_abcdef'


class TepRAM(io.BytesIO):
    def __init__(self, raw=b'', ghi=None, doc=None):
        super().__init__(raw)
        self.ghi = ghi
        self.doc = doc

    def read(self, n=-1):
        raw = super().read(n)
        if self.doc is not None:
            self.doc(n, len(raw))
        return raw

    def fileno(self):
        return 123  # os.fsync đã mock; không dùng descriptor thật.

    def close(self):
        if not self.closed and self.ghi is not None:
            self.ghi(self.getvalue())
        super().close()


class HeTepRAM:
    def __init__(self):
        self.goc = Path('hot-folder-DEMO')
        self.d = {k: self.goc / k for k in ('in', 'out', 'tam', 'nhan')}
        self.dirs = {self.goc, *self.d.values()}
        self.files, self.moves, self.deleted, self.calls = {}, [], [], []
        self.reads = []
        self.locks, self.sent = [], []
        self.now, self.stamp = 0.0, 0
        self.sau_gui, self.sau_doi, self.sau_nghi = None, None, None
        self.cho_khoa = False

    def put(self, path, raw):
        self.stamp += 1
        self.files[path] = raw, self.stamp

    def read(self, path):
        self.calls.append(('read', path))
        if path not in self.files:
            raise FileNotFoundError(str(path))
        return self.files[path][0]

    def stat(self, path, *args, **kwargs):
        self.calls.append(('stat', path))
        if path not in self.files:
            raise FileNotFoundError(str(path))
        raw, stamp = self.files[path]
        return SimpleNamespace(st_size=len(raw), st_mtime_ns=stamp)

    def open(self, path, mode='r', *args, **kwargs):
        self.calls.append(('open', path))
        if mode == 'wb':
            return TepRAM(ghi=lambda raw: self.put(path, raw))
        if mode == 'rb':
            return TepRAM(self.read(path), doc=lambda n, size: self.reads.append((path, n, size)))
        raise AssertionError('Không được đọc/ghi sổ hoặc cấu hình: ' + mode)

    def is_dir(self, path):
        self.calls.append(('is_dir', path))
        return path in self.dirs

    def iterdir(self, path):
        self.calls.append(('iterdir', path))
        return iter([p for p in self.files if p.parent == path])

    def unlink(self, path):
        self.deleted.append(path)
        self.files.pop(path, None)

    def replace(self, src, dst):
        src, dst = Path(src), Path(dst)
        if src not in self.files:
            raise FileNotFoundError(str(src))
        self.moves.append((src, dst))
        self.files[dst] = self.files.pop(src)
        if dst.parent == self.d['in']:
            self.sent.append((dst, self.files[dst][0]))
            if self.sau_gui is not None:
                self.sau_gui(dst)
        if self.sau_doi is not None:
            self.sau_doi(src, dst)

    def sleep(self, giay):
        self.now += giay
        if self.sau_nghi is not None:
            self.sau_nghi()

    @contextmanager
    def khoa(self, path, nghi, huy=None):
        self.locks.append(path)
        while self.cho_khoa:
            ocr._kiem_huy(huy)
            huy.wait(nghi)
        ocr._kiem_huy(huy)
        yield


class HuyRAM:
    def __init__(self, fs):
        self.fs, self.bat = fs, False

    def set(self):
        self.bat = True

    def is_set(self):
        return self.bat

    def wait(self, giay):
        self.fs.sleep(giay)
        return self.bat


class HotFolderPDFTests(unittest.TestCase):
    def setUp(self):
        self.fs = fs = HeTepRAM()
        self.pdf = pdf_demo((CHU, TIEN, NGAY))
        self.raw = b'%PDF-1.4\nDEMO tai lieu goc\n%%EOF'
        self.ra = fs.d['out'] / (MA + '.pdf')
        self.nhan = fs.d['nhan'] / (MA + '.pdf')
        self.huy = HuyRAM(fs)
        replacements = {
            'open': lambda p, *a, **k: fs.open(p, *a, **k),
            'read_bytes': lambda p: fs.read(p),
            'write_bytes': lambda p, raw: fs.put(p, raw),
            'exists': lambda p: p in fs.files or p in fs.dirs,
            'stat': lambda p, *a, **k: fs.stat(p, *a, **k),
            'is_dir': lambda p: fs.is_dir(p),
            'is_file': lambda p: p in fs.files,
            'iterdir': lambda p: fs.iterdir(p),
            'resolve': lambda p, *a, **k: p,
            'unlink': lambda p, *a, **k: fs.unlink(p),
        }
        for name, replacement in replacements.items():
            self._patch(patch.object(Path, name, replacement))
        self.mkdir = self._patch(patch.object(Path, 'mkdir', side_effect=AssertionError('Không tạo thư mục')))
        self._patch(patch('builtins.open', side_effect=AssertionError('Không filesystem thật')))
        self._patch(patch.object(ocr.os, 'replace', side_effect=fs.replace))
        self.fsync = self._patch(patch.object(ocr.os, 'fsync'))
        self._patch(patch.object(ocr, '_xoa', side_effect=fs.unlink))
        self._patch(patch.object(ocr, '_ma_moi', return_value=MA))
        self.khoa_that = ocr._khoa_tep
        self.khoa = self._patch(patch.object(ocr, '_khoa_tep', side_effect=fs.khoa))
        self._patch(patch.object(ocr.time, 'monotonic', side_effect=lambda: fs.now))
        self._patch(patch.object(ocr.time, 'sleep', side_effect=fs.sleep))
        self.timer = self._patch(patch.object(ocr.threading, 'Timer'))
        for name in ('_doc_so', '_ghi_so', '_giu_trang', '_hoan_trang'):
            self._patch(patch.object(ocr.CongOCR, name, side_effect=AssertionError('Transport không dùng sổ')))
        for name in ('socket.socket', 'socket.create_connection', 'subprocess.Popen'):
            self._patch(patch(name, side_effect=AssertionError('Không mạng/tiến trình')))
        self.backend = self.tao_backend()

    def _patch(self, patcher):
        value = patcher.start()
        self.addCleanup(patcher.stop)
        return value

    def tao_backend(self, **kwargs):
        options = dict(bat=True, nghi=0.1, on_dinh=0.2, cho_nhan=0.5, cho_toi_da=2)
        options.update(kwargs)
        return ocr.HotFolderPDF(self.fs.goc, **options)

    def tra_ket_qua(self, raw=None, duoi='pdf', nhan=True):
        def tra(vao):
            if nhan:
                self.fs.files.pop(vao)
            if raw is not None:
                self.fs.put(self.fs.d['out'] / (vao.stem + '.' + duoi), raw)
        self.fs.sau_gui = tra

    def loi(self, ma, ham):
        with self.assertRaises(DataError) as caught:
            ham()
        self.assertEqual(caught.exception.code, ma)
        self.assertNotIn(str(self.fs.goc), str(caught.exception))
        self.assertNotIn('DEMO-KIN', str(caught.exception))
        return caught.exception

    def test_mac_dinh_tat_khoi_tao_va_kiem_khong_dung_filesystem(self):
        backend = ocr.HotFolderPDF(self.fs.goc)
        self.assertFalse(backend.san_sang())
        self.loi('ABBYY_KHONG_KET_NOI', lambda: backend.doc_pdf(self.raw))
        self.assertEqual(self.fs.calls, [])
        self.khoa.assert_not_called()
        self.mkdir.assert_not_called()

    def test_san_sang_chi_kiem_thu_muc_khong_tao_ghi_hoac_xac_nhan_may(self):
        self.assertTrue(self.backend.san_sang())
        self.assertEqual(self.fs.calls, [('is_dir', p) for p in self.fs.d.values()])
        for p in self.fs.d.values():
            self.fs.dirs.discard(p)
            self.assertFalse(self.backend.san_sang())
            self.fs.dirs.add(p)
        with patch.object(Path, 'is_dir', side_effect=PermissionError('DEMO-KIN')):
            self.assertFalse(self.backend.san_sang())
        self.mkdir.assert_not_called()
        self.khoa.assert_not_called()

    def test_cau_hinh_sai_khong_truy_cap_filesystem(self):
        for key in ('nghi', 'on_dinh', 'cho_nhan', 'cho_toi_da'):
            for value in (0, -1, float('nan'), float('inf'), None):
                with self.subTest(key=key, value=value):
                    self.loi('OCR_LOI_ABBYY', lambda: self.tao_backend(**{key: value}))
        self.loi('OCR_LOI_ABBYY', lambda: self.tao_backend(bat='true'))
        self.assertEqual(self.fs.calls, [])

    def test_dau_vao_sai_va_duoi_chua_duong_dan_bi_chan_truoc_filesystem(self):
        for raw, duoi in ((b'', 'pdf'), ('DEMO', 'pdf'), (bytearray(b'DEMO'), 'pdf'),
                          (self.raw, '../pdf'), (self.raw, 'pdf/x'), (self.raw, None)):
            with self.subTest(duoi=duoi):
                self.loi('OCR_DINH_DANG', lambda: self.backend.doc_pdf(raw, duoi))
        self.assertEqual(self.fs.calls, [])
        self.khoa.assert_not_called()

    def test_pdf_co_lop_chu_tra_nguyen_bytes_khong_dem_trang_va_chung_khoa_docx(self):
        self.tra_ket_qua(self.pdf)
        result = self.backend.doc_pdf(self.raw)
        self.assertEqual(result, self.pdf)
        self.assertIn(CHU, doc_lop_chu(result).text)
        self.assertEqual(self.fs.sent, [(self.fs.d['in'] / (MA + '.pdf'), self.raw)])
        self.assertEqual(self.fs.locks, [self.fs.goc / 'in.lock'])
        self.assertGreaterEqual(self.fs.now, 0.2)
        self.assertIn((self.ra, self.nhan), self.fs.moves)
        self.assertEqual(self.fs.files, {})
        self.mkdir.assert_not_called()

    def test_tran_doc_sai_bi_tu_choi_truoc_filesystem(self):
        for tran in (None, 0, -1, True, False, 32.0, '32'):
            with self.subTest(tran=tran):
                self.loi('OCR_LOI_ABBYY', lambda: self.backend.doc_pdf(
                    self.raw, toi_da_byte_ra=tran))
        self.assertEqual(self.fs.calls, [])
        self.assertEqual(self.fs.sent, [])
        self.khoa.assert_not_called()

    def test_tran_mac_dinh_la_64_mib_huu_han(self):
        self.assertEqual(ocr.TRAN_KET_QUA_MAC_DINH, 64 * 1024**2)
        self.assertEqual(ocr.HotFolderPDF.doc_pdf.__kwdefaults__['toi_da_byte_ra'],
                         ocr.TRAN_KET_QUA_MAC_DINH)

    def test_khong_truyen_tran_doc_duoc_pdf_nho_bang_mac_dinh(self):
        self.tra_ket_qua(self.pdf)
        tran = len(self.pdf)
        # Python giữ default lúc định nghĩa hàm, nên thu nhỏ cả hằng và default.
        with patch.object(ocr, 'TRAN_KET_QUA_MAC_DINH', tran), \
                patch.dict(ocr.HotFolderPDF.doc_pdf.__kwdefaults__, toi_da_byte_ra=tran):
            self.assertEqual(self.backend.doc_pdf(self.raw), self.pdf)
        self.assertEqual(self.fs.reads, [(self.ra, tran + 1, tran), (self.nhan, tran + 1, tran)])

    def test_khong_truyen_tran_tu_choi_pdf_vuot_mac_dinh_truoc_doc(self):
        self.tra_ket_qua(self.pdf)
        with patch.object(ocr, 'TRAN_KET_QUA_MAC_DINH', 32), \
                patch.dict(ocr.HotFolderPDF.doc_pdf.__kwdefaults__, toi_da_byte_ra=32):
            self.loi('OCR_QUA_CO', lambda: self.backend.doc_pdf(self.raw))
        self.assertEqual(self.fs.reads, [])

    def test_pdf_vuot_tran_stat_khong_doc_ket_qua(self):
        self.tra_ket_qua(b'%PDF-1.4\n' + b'x' * 100 + b'\n%%EOF')
        self.loi('OCR_QUA_CO', lambda: self.backend.doc_pdf(self.raw, toi_da_byte_ra=32))
        self.assertIn(('stat', self.ra), self.fs.calls)
        self.assertNotIn(('read', self.ra), self.fs.calls)
        self.assertNotIn(('read', self.nhan), self.fs.calls)
        self.assertEqual(self.fs.reads, [])
        self.assertEqual(len(self.fs.sent), 1)

    def test_pdf_dung_tran_duoc_doc_co_tran_o_ca_hai_buoc(self):
        self.tra_ket_qua(self.pdf)
        tran = len(self.pdf)
        self.assertEqual(self.backend.doc_pdf(self.raw, toi_da_byte_ra=tran), self.pdf)
        self.assertEqual(self.fs.reads, [(self.ra, tran + 1, tran), (self.nhan, tran + 1, tran)])

    def test_pdf_tang_sau_stat_chi_doc_tran_cong_mot_roi_dung(self):
        for dich in (self.ra, self.nhan):
            with self.subTest(buoc=dich.parent.name):
                self.fs.reads.clear()
                self.tra_ket_qua(self.raw)
                def mo(tep, mode='r', *args, **kwargs):
                    if tep == dich and mode == 'rb':
                        self.fs.put(tep, b'%PDF-1.4\n' + b'x' * 100 + b'\n%%EOF')
                    return self.fs.open(tep, mode, *args, **kwargs)
                with patch.object(Path, 'open', mo):
                    self.loi('OCR_QUA_CO', lambda: self.backend.doc_pdf(
                        self.raw, toi_da_byte_ra=32))
                truoc = [(self.ra, 33, len(self.raw))] if dich == self.nhan else []
                self.assertEqual(self.fs.reads, truoc + [(dich, 33, 33)])
                self.assertEqual(self.fs.files, {})

    def test_pdf_tang_khi_doi_ten_bi_stat_chan_truoc_lan_doc_thu_hai(self):
        self.tra_ket_qua(self.raw)
        def doi(src, dst):
            if dst == self.nhan:
                self.fs.put(dst, b'%PDF-1.4\n' + b'x' * 100 + b'\n%%EOF')
        self.fs.sau_doi = doi
        self.loi('OCR_QUA_CO', lambda: self.backend.doc_pdf(self.raw, toi_da_byte_ra=32))
        self.assertEqual(self.fs.reads, [(self.ra, 33, len(self.raw))])
        self.assertIn(('stat', self.nhan), self.fs.calls)
        self.assertNotIn(('read', self.nhan), self.fs.calls)

    def test_guard_len_sau_doc_chan_pdf_hop_le_vuot_tran_mot_byte(self):
        self.fs.put(self.ra, self.raw)
        tran = len(self.raw)
        raw_lon = b'%PDF-1.4\n' + b'x' * (tran + 1 - 15) + b'\n%%EOF'
        self.assertEqual(len(raw_lon), tran + 1)
        self.assertTrue(ocr._pdf_hop_le(raw_lon))
        def mo(tep, mode='r', *args, **kwargs):
            self.fs.put(tep, raw_lon)  # Tăng sau stat, ngay trước khi đọc.
            return self.fs.open(tep, mode, *args, **kwargs)
        with patch.object(Path, 'open', mo):
            self.loi('OCR_QUA_CO', lambda: self.backend._doc_ket_qua(self.ra, tran))
        self.assertEqual(self.fs.reads, [(self.ra, tran + 1, tran + 1)])

    def test_cau_noi_chan_pdf_115_byte_voi_tran_32_truoc_khi_doc(self):
        ket_qua = b'%PDF-1.4\n' + b'x' * 100 + b'\n%%EOF'
        self.assertEqual(len(ket_qua), 115)
        self.tra_ket_qua(ket_qua)
        khoa = b'DEMO-khoa-cau-noi-khong-phai-khoa-that-123456'
        c = cn.CauHinhCauNoi(bat=True, khoa=khoa, ip_core=('192.0.2.10',), toi_da_byte_ra=32)
        dv = cn.CauNoiABBYY(c, hot_folder=self.backend, ghi_log=Mock(), dong_ho=lambda: self.fs.now)
        ket_noi = Mock()
        ket_noi.getpeername.return_value = ('192.0.2.10', 12345)
        req = cn.YeuCau(ket_noi, {
            'Authorization': 'Bearer ' + khoa.decode('ascii'),
            'Content-Length': str(len(self.raw)), 'Content-Type': 'application/pdf',
            'X-Request-ID': str(UUID(int=1)),
        }, io.BytesIO(self.raw))
        self.assertEqual(dv.xu_ly(req).ma_http, 502)
        self.assertNotIn(('read', self.ra), self.fs.calls)
        self.assertNotIn(('read', self.nhan), self.fs.calls)
        self.assertEqual(self.fs.reads, [])
        self.assertEqual(dv.xu_ly(req).ma_http, 409)
        self.assertEqual(len(self.fs.sent), 1)

    def test_chu_ky_tuong_thich_chon_nguon_voi_anh_png_jpeg(self):
        for duoi in ('.PNG', 'jpg', 'JPEG'):
            with self.subTest(duoi=duoi):
                self.tra_ket_qua(self.pdf)
                self.assertEqual(self.backend.doc_pdf(b'DEMO anh', duoi, huy=self.huy), self.pdf)
                self.assertEqual(self.fs.sent[-1][0].suffix, '.' + duoi.lower().lstrip('.'))

    def test_chon_nguon_goi_adapter_that_va_chi_ben_goi_giu_trang(self):
        self.tra_ket_qua(self.pdf)
        cong = self.tao_cong_docx()
        mask = Mock(side_effect=AssertionError('Không chuyển nguồn khi đủ lớp chữ'))
        chon = ChonNguonOCR(abbyy=self.backend, cong_ocr=cong, mask_ocr=mask)
        with patch.object(cong, '_giu_trang') as giu, patch.object(cong, '_hoan_trang') as hoan:
            result = chon.doc(self.pdf, 'pdf')
        self.assertEqual(result.nguon_doc, 'ABBYY')
        self.assertIn(CHU, result.text)
        giu.assert_called_once()
        self.assertEqual(giu.call_args.args[0], 1)
        hoan.assert_not_called()
        mask.assert_not_called()
        self.assertEqual(len(self.fs.sent), 1)

    def test_khong_nhan_docx_hoac_pdf_ma_khac_va_khong_don_ma_khac(self):
        khac = self.fs.d['out'] / (MA_KHAC + '.pdf')
        log = self.fs.d['out'] / (MA_KHAC + '.log')
        self.fs.put(khac, self.pdf)
        self.fs.put(log, (MA + ' ERROR DEMO').encode())
        self.tra_ket_qua(b'DEMO DOCX', duoi='docx')
        self.loi('OCR_QUA_GIO', lambda: self.backend.doc_pdf(self.raw))
        self.assertEqual(set(self.fs.files), {khac, log})
        self.assertTrue(all(p.name.startswith(MA + '.') for p in self.fs.deleted))

    def test_chua_nhan_rut_dau_vao_va_khong_hen_don_muon(self):
        self.loi('OCR_KHONG_NHAN', lambda: self.backend.doc_pdf(self.raw))
        self.assertIn((self.fs.d['in'] / (MA + '.pdf'), self.fs.d['tam'] / (MA + '.rut')), self.fs.moves)
        self.assertEqual(self.fs.files, {})
        self.timer.assert_not_called()

    def test_da_nhan_qua_gio_khong_gui_lai_va_don_muon_chi_dung_ma(self):
        self.tra_ket_qua()
        self.loi('OCR_QUA_GIO', lambda: self.backend.doc_pdf(self.raw))
        self.assertEqual(len(self.fs.sent), 1)
        self.timer.assert_called_once()
        giay, callback = self.timer.call_args.args
        self.assertEqual(giay, 120)
        self.assertTrue(self.timer.return_value.daemon)
        self.timer.return_value.start.assert_called_once()
        khac = self.fs.d['out'] / (MA_KHAC + '.pdf')
        self.fs.put(khac, self.pdf)
        self.fs.put(self.ra, self.pdf)
        callback(*self.timer.call_args.kwargs['args'])
        self.assertEqual(set(self.fs.files), {khac})

    def test_huy_truoc_gui_khong_cham_filesystem(self):
        self.huy.set()
        self.loi('OCR_HUY', lambda: self.backend.doc_pdf(self.raw, huy=self.huy))
        self.assertEqual(self.fs.calls, [])
        self.assertEqual(self.fs.sent, [])

    def test_huy_sau_ghi_part_khong_gui_va_don_part_trong_ram(self):
        self.fsync.side_effect = lambda fd: self.huy.set()
        self.loi('OCR_HUY', lambda: self.backend.doc_pdf(self.raw, huy=self.huy))
        self.assertEqual(self.fs.sent, [])
        self.assertEqual(self.fs.files, {})
        self.timer.assert_not_called()

    def test_huy_khi_cho_ket_qua_sau_nhan(self):
        self.tra_ket_qua()
        self.fs.sau_nghi = self.huy.set
        self.loi('OCR_HUY', lambda: self.backend.doc_pdf(self.raw, huy=self.huy))
        self.assertEqual(len(self.fs.sent), 1)
        self.timer.assert_called_once()

    def test_huy_sau_nhan_ket_qua_khong_tra_thanh_cong(self):
        self.tra_ket_qua(self.pdf)
        self.fs.sau_doi = lambda src, dst: self.huy.set() if dst == self.nhan else None
        self.loi('OCR_HUY', lambda: self.backend.doc_pdf(self.raw, huy=self.huy))
        self.assertEqual(self.fs.files, {})

    def test_pdf_con_ghi_do_cho_on_dinh_va_dau_ket_thuc(self):
        self.tra_ket_qua(self.pdf[:-10])
        def ghi_tiep():
            if self.fs.now >= 0.4:
                self.fs.sau_nghi = None
                self.fs.put(self.ra, self.pdf)
        self.fs.sau_nghi = ghi_tiep
        self.assertEqual(self.backend.doc_pdf(self.raw), self.pdf)
        self.assertGreaterEqual(self.fs.now, 0.6)

    def test_pdf_sai_dinh_dang_khong_tra_thanh_cong(self):
        self.tra_ket_qua(b'DEMO khong phai PDF\n%%EOF')
        self.loi('OCR_QUA_GIO', lambda: self.backend.doc_pdf(self.raw))

    def test_abbyy_giu_ket_qua_khi_doi_ten_thi_cho_tiep(self):
        self.tra_ket_qua(self.pdf)
        replace = self.fs.replace
        da_chan = []
        def doi(src, dst):
            if src == self.ra and not da_chan:
                da_chan.append(True)
                raise PermissionError('DEMO file dang mo')
            return replace(src, dst)
        with patch.object(ocr.os, 'replace', side_effect=doi):
            self.assertEqual(self.backend.doc_pdf(self.raw), self.pdf)
        self.assertTrue(da_chan)

    def test_kiem_lai_size_mtime_sau_doi_ten_truoc_khi_tra(self):
        self.tra_ket_qua(self.pdf)
        pdf_moi = pdf_demo(('DEMO noi dung thay doi',))
        da_doi = []
        def doi(src, dst):
            if dst == self.nhan and not da_doi:
                da_doi.append(True)
                self.fs.put(dst, pdf_moi)
        self.fs.sau_doi = doi
        self.assertEqual(self.backend.doc_pdf(self.raw), pdf_moi)
        self.assertIn((self.nhan, self.ra), self.fs.moves)
        self.assertEqual(self.fs.moves.count((self.ra, self.nhan)), 2)

    def test_loi_abbyy_chi_nhan_dung_ma(self):
        self.tra_ket_qua()
        self.fs.put(self.fs.d['out'] / (MA + '.log'), (MA + ' ERROR DEMO').encode())
        self.loi('OCR_LOI_ABBYY', lambda: self.backend.doc_pdf(self.raw))
        self.assertEqual(len(self.fs.sent), 1)

    def test_log_loi_doc_duoi_tep_voi_tran_rieng(self):
        self.assertEqual(ocr.TRAN_LOG_ABBYY, 64 * 1024)
        for duoi in ('log', 'txt'):
            with self.subTest(duoi=duoi):
                self.fs.files.clear()
                self.fs.reads.clear()
                tep = self.fs.d['out'] / (MA + '.' + duoi)
                self.fs.put(tep, b'x' * 100 + b'\n' + (MA + ' ERROR').encode())
                with patch.object(ocr, 'TRAN_LOG_ABBYY', 32):
                    self.assertTrue(self.backend._loi_abbyy(self.fs.d['out'], MA))
                self.assertEqual(self.fs.reads, [(tep, 33, 32)])

    def test_log_tang_sau_stat_chi_doc_tran_cong_mot_va_cat_phan_thua(self):
        tep = self.fs.d['out'] / (MA + '.log')
        self.fs.put(tep, b'DEMO')
        prefix = (MA + ' ERRO').encode().rjust(32, b' ')
        stream = TepRAM(b'DEMO', doc=lambda n, size: self.fs.reads.append((tep, n, size)))
        doc = stream.read
        def tang_roi_doc(n=-1):
            self.assertIn(('stat', tep), self.fs.calls)
            pos = stream.tell()
            raw = prefix + b'R' + b'x' * 100
            self.fs.put(tep, raw)
            stream.seek(0)
            stream.write(raw)
            stream.seek(pos)
            return doc(n)
        with patch.object(ocr, 'TRAN_LOG_ABBYY', 32), \
                patch.object(Path, 'open', return_value=stream), \
                patch.object(stream, 'read', side_effect=tang_roi_doc):
            # Byte thứ 33 hoàn thành từ ERROR, phải bị cắt trước khi xét lỗi.
            self.assertFalse(self.backend._loi_abbyy(self.fs.d['out'], MA))
        self.assertEqual(self.fs.reads, [(tep, 33, 33)])

    def test_loi_filesystem_khong_lo_noi_dung_duong_dan(self):
        self.fsync.side_effect = OSError(str(self.fs.goc) + ' DEMO-KIN')
        self.loi('OCR_LOI_ABBYY', lambda: self.backend.doc_pdf(self.raw))
        self.assertEqual(self.fs.sent, [])
        self.assertEqual(self.fs.files, {})

    def test_qua_gio_khi_tranh_khoa_khong_gui_tep(self):
        self.fs.cho_khoa = True
        self.loi('OCR_QUA_GIO', lambda: self.backend.doc_pdf(self.raw))
        self.assertAlmostEqual(self.fs.now, self.backend.cho_toi_da)
        self.assertEqual(self.fs.sent, [])
        self.assertEqual(self.fs.files, {})

    def test_huy_khi_tranh_khoa_khong_gui_tep(self):
        self.fs.cho_khoa = True
        self.fs.sau_nghi = self.huy.set
        self.loi('OCR_HUY', lambda: self.backend.doc_pdf(self.raw, huy=self.huy))
        self.assertEqual(self.fs.sent, [])

    def test_khoa_tep_that_tranh_khoa_python_van_kiem_thoi_han_pdf(self):
        backend = self.tao_backend(nghi=1, cho_toi_da=0.2)
        lock = Mock()
        def acquire(*, timeout):
            self.fs.sleep(timeout)
            return False
        lock.acquire.side_effect = acquire
        with patch.object(ocr, '_khoa_tep', self.khoa_that), \
                patch.object(ocr, '_khoa_cho', return_value=lock):
            self.loi('OCR_QUA_GIO', lambda: backend.doc_pdf(self.raw))
        self.assertAlmostEqual(self.fs.now, 0.2)
        lock.release.assert_not_called()
        self.assertEqual(self.fs.sent, [])
        self.mkdir.assert_not_called()

    def test_khoa_tep_that_tranh_khoa_python_van_kiem_huy_pdf(self):
        lock = Mock()
        def acquire(*, timeout):
            self.huy.set()
            return False
        lock.acquire.side_effect = acquire
        with patch.object(ocr, '_khoa_tep', self.khoa_that), \
                patch.object(ocr, '_khoa_cho', return_value=lock):
            self.loi('OCR_HUY', lambda: self.backend.doc_pdf(self.raw, huy=self.huy))
        lock.release.assert_not_called()
        self.assertEqual(self.fs.sent, [])
        self.mkdir.assert_not_called()

    def test_docx_cu_van_nhan_docx_va_khong_hoan_khi_da_nhan(self):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as archive:
            archive.writestr('word/document.xml', '<DEMO/>')
        docx = stream.getvalue()
        self.tra_ket_qua(docx, duoi='docx')
        cong = self.tao_cong_docx()
        with patch.object(cong, '_hoan_trang') as hoan:
            self.assertEqual(cong._chay_hot_folder(self.raw, 'pdf', self.fs.d, MA, None), docx)
        hoan.assert_not_called()
        self.assertIn((self.fs.d['out'] / (MA + '.docx'), self.fs.d['nhan'] / (MA + '.docx')), self.fs.moves)
        tran = ocr.TRAN_KET_QUA_MAC_DINH
        self.assertEqual(self.fs.reads, [(self.fs.d['out'] / (MA + '.docx'), tran + 1, len(docx)),
                                        (self.fs.d['nhan'] / (MA + '.docx'), tran + 1, len(docx))])

    def tao_cong_docx(self):
        return ocr.CongOCR(self.fs.goc, tep_so_trang=Path('so-DEMO.json'),
                          thu_muc_dem=Path('dem-DEMO'), nghi=0.1, on_dinh=0.2,
                          cho_nhan=0.5, cho_toi_da=2)

    def dat_dem_docx(self, raw, sau_khoa):
        self.fs.files.clear()
        self.fs.reads.clear()
        cong = self.tao_cong_docx()
        dem = cong.thu_muc_dem / (hashlib.sha256(self.raw).hexdigest() + '.docx')
        @contextmanager
        def khoa(tep, nghi, huy=None):
            with self.fs.khoa(tep, nghi, huy):
                self.fs.put(dem, raw)
                yield
        self.khoa.side_effect = khoa if sau_khoa else self.fs.khoa
        if not sau_khoa:
            self.fs.put(dem, raw)
        return cong, dem

    def test_docx_dem_cu_van_doc_co_tran_truoc_va_sau_khoa(self):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as archive:
            archive.writestr('word/document.xml', '<DEMO/>')
        docx = stream.getvalue()
        for sau_khoa in (False, True):
            with self.subTest(sau_khoa=sau_khoa):
                cong, dem = self.dat_dem_docx(docx, sau_khoa)
                with patch.object(Path, 'mkdir'), \
                        patch.object(ocr, 'TRAN_KET_QUA_MAC_DINH', len(docx)):
                    self.assertEqual(cong.ocr(self.raw, 'pdf'), docx)
                self.assertEqual(self.fs.reads, [(dem, len(docx) + 1, len(docx))])
        self.assertEqual(self.fs.sent, [])

    def test_docx_dem_vuot_tran_mac_dinh_bi_chan_truoc_doc_o_ca_hai_buoc(self):
        for sau_khoa in (False, True):
            with self.subTest(sau_khoa=sau_khoa):
                cong, _ = self.dat_dem_docx(b'x' * 33, sau_khoa)
                with patch.object(Path, 'mkdir'), patch.object(ocr, 'TRAN_KET_QUA_MAC_DINH', 32):
                    self.loi('OCR_QUA_CO', lambda: cong.ocr(self.raw, 'pdf'))
                self.assertEqual(self.fs.reads, [])
        self.assertEqual(self.fs.sent, [])

    def test_docx_dem_tang_sau_stat_chi_doc_tran_cong_mot_o_ca_hai_buoc(self):
        for sau_khoa in (False, True):
            with self.subTest(sau_khoa=sau_khoa):
                cong, dem = self.dat_dem_docx(b'DEMO', sau_khoa)
                def mo(tep, mode='r', *args, **kwargs):
                    if tep == dem and mode == 'rb':
                        self.fs.put(tep, b'x' * 100)
                    return self.fs.open(tep, mode, *args, **kwargs)
                with patch.object(Path, 'mkdir'), patch.object(Path, 'open', mo), \
                        patch.object(ocr, 'TRAN_KET_QUA_MAC_DINH', 32):
                    self.loi('OCR_QUA_CO', lambda: cong.ocr(self.raw, 'pdf'))
                self.assertEqual(self.fs.reads, [(dem, 33, 33)])
        self.assertEqual(self.fs.sent, [])

    def test_docx_cu_chua_nhan_van_hoan_dung_ma(self):
        cong = self.tao_cong_docx()
        with patch.object(cong, '_hoan_trang') as hoan:
            self.loi('OCR_KHONG_NHAN', lambda: cong._chay_hot_folder(self.raw, 'pdf', self.fs.d, MA, None))
        hoan.assert_called_once_with(MA)

    def test_docx_cu_qua_gio_sau_nhan_van_giu_trang(self):
        self.tra_ket_qua()
        cong = self.tao_cong_docx()
        with patch.object(cong, '_hoan_trang') as hoan:
            self.loi('OCR_QUA_GIO', lambda: cong._chay_hot_folder(self.raw, 'pdf', self.fs.d, MA, None))
        hoan.assert_not_called()

    def tao_ban_giao(self):
        adapter = bg.BanGiaoOCR(self.tao_cong_docx(), viec_id=str(UUID(int=1)),
                               thu_muc_ban_giao=Path('ban-giao-DEMO'))
        with io.BytesIO() as stream:
            with zipfile.ZipFile(stream, 'w') as archive:
                archive.writestr('word/document.xml', '<DEMO/>')
            docx = stream.getvalue()
        data = dict(viec_id=adapter.viec_id, trang_thai=bg.CHO_CORE,
                    sha256_docx=hashlib.sha256(docx).hexdigest())
        nhat_ky = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.fs.put(adapter._tep, nhat_ky)
        self.fs.put(adapter._docx, docx)
        return adapter, data, nhat_ky, docx

    def test_ban_giao_nhat_ky_va_docx_dung_tran_van_doc_duoc(self):
        adapter, data, nhat_ky, docx = self.tao_ban_giao()
        self.assertEqual(bg.TRAN_NHAT_KY_BAN_GIAO, 64 * 1024)
        self.assertEqual(bg.TRAN_DOCX_BAN_GIAO, 64 * 1024**2)
        with patch.object(bg, 'TRAN_NHAT_KY_BAN_GIAO', len(nhat_ky)), \
                patch.object(bg, 'TRAN_DOCX_BAN_GIAO', len(docx)):
            self.assertEqual(adapter._doc(), data)
            self.assertEqual(adapter._ket_qua(data), docx)
        self.assertEqual(self.fs.reads, [(adapter._tep, len(nhat_ky) + 1, len(nhat_ky)),
                                        (adapter._docx, len(docx) + 1, len(docx))])
        self.assertEqual(self.fs.sent, [])

    def test_ban_giao_nhat_ky_va_docx_vuot_tran_stat_khong_doc(self):
        for loai in ('nhat_ky', 'docx'):
            with self.subTest(loai=loai):
                adapter, data, _, _ = self.tao_ban_giao()
                tep = adapter._tep if loai == 'nhat_ky' else adapter._docx
                self.fs.put(tep, b'x' * 33)
                self.fs.reads.clear()
                with patch.object(bg, 'TRAN_NHAT_KY_BAN_GIAO', 32), \
                        patch.object(bg, 'TRAN_DOCX_BAN_GIAO', 32):
                    self.loi('OCR_CAN_DOI_CHIEU', adapter._doc if loai == 'nhat_ky'
                             else lambda: adapter._ket_qua(data))
                self.assertEqual(self.fs.reads, [])
                if loai == 'docx':
                    self.assertEqual(json.loads(self.fs.files[adapter._tep][0])['trang_thai'],
                                     bg.CAN_DOI_CHIEU)
        self.assertEqual(self.fs.sent, [])

    def test_ban_giao_nhat_ky_va_docx_tang_sau_stat_chi_doc_tran_cong_mot(self):
        for loai in ('nhat_ky', 'docx'):
            with self.subTest(loai=loai):
                adapter, data, _, _ = self.tao_ban_giao()
                tep = adapter._tep if loai == 'nhat_ky' else adapter._docx
                self.fs.put(tep, b'DEMO')
                self.fs.reads.clear()

                def mo(path, mode='r', *args, **kwargs):
                    if path == tep and mode == 'rb':
                        self.fs.put(path, b'x' * 100)
                    return self.fs.open(path, mode, *args, **kwargs)

                with patch.object(bg, 'TRAN_NHAT_KY_BAN_GIAO', 32), \
                        patch.object(bg, 'TRAN_DOCX_BAN_GIAO', 32), patch.object(Path, 'open', mo):
                    self.loi('OCR_CAN_DOI_CHIEU', adapter._doc if loai == 'nhat_ky'
                             else lambda: adapter._ket_qua(data))
                self.assertEqual(self.fs.reads, [(tep, 33, 33)])
                if loai == 'docx':
                    self.assertEqual(json.loads(self.fs.files[adapter._tep][0])['trang_thai'],
                                     bg.CAN_DOI_CHIEU)
        self.assertEqual(self.fs.sent, [])


if __name__ == '__main__':
    unittest.main()
