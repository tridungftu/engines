"""OCR-CR-7: client HTTPS thật nhận mã Core; HTTP/socket đều giả trong RAM."""

import hashlib
import http.client
import io
import ssl
import traceback
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from uuid import UUID

from kho_tri_thuc.engines.e_ocr import ket_noi_abbyy as kn
from kho_tri_thuc.engines.e_ocr import cau_noi_abbyy as cn


PDF = b'%PDF-1.4\nDEMO nhan dang\n%%EOF'
PDF_RA = b'%PDF-1.4\nDEMO lop chu\n%%EOF'
MA_CORE = 'ocr:0123456789abcdef0123456789abcdef'
TEN_TEP = 'ocr_0123456789abcdef0123456789abcdef'
KHOA = b'DEMO-khoa-trong-RAM-12345678901234567890'
HTTPS_THAT = http.client.HTTPSConnection


def phan_hoi_tu_cau(cau_noi, raw_gui):
    """Hai parser HTTP thật, chỉ socket và luồng byte là giả trong RAM."""
    peer = Mock()
    peer.getpeername.return_value = ('192.0.2.10', 12345)
    peer.makefile.return_value = io.BytesIO(raw_gui)
    raw_ra = bytearray()
    peer.sendall.side_effect = raw_ra.extend
    cn._XuLyHTTP(peer, ('192.0.2.10', 12345), SimpleNamespace(cau_noi=cau_noi))
    return io.BytesIO(raw_ra)


class MaTuongQuanTests(unittest.TestCase):
    def setUp(self):
        for ten in ('socket.socket', 'socket.create_connection', 'socket.getaddrinfo',
                    'subprocess.Popen', 'builtins.open', 'pathlib.Path.open',
                    'pathlib.Path.read_bytes', 'pathlib.Path.write_bytes', 'pathlib.Path.mkdir'):
            p = patch(ten, side_effect=AssertionError('Cấm I/O thật trong test OCR-CR-7'))
            p.start()
            self.addCleanup(p.stop)
        self.tls = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.client = kn.KetNoiABBYY(kn.CauHinhKetNoi(
            bat=True, may_chu='abbyy.demo.invalid', khoa=KHOA, tls=self.tls))
        self.http = Mock()
        self.http.getresponse.side_effect = self._phan_hoi
        p = patch.object(kn.http.client, 'HTTPSConnection', return_value=self.http)
        self.tao_http = p.start()
        self.addCleanup(p.stop)

    @staticmethod
    def _phan_hoi():
        ph = Mock(status=200)
        ph.getheaders.return_value = [('Content-Type', 'application/pdf'),
                                     ('Content-Length', str(len(PDF_RA)))]
        ph.read1.side_effect = [PDF_RA, b'']
        return ph

    def _gui(self, ma):
        self.http.reset_mock()
        self.assertEqual(self.client.doc_pdf(PDF, ma_yeu_cau=ma), PDF_RA)
        self.http.connect.assert_called_once()
        self.http.putrequest.assert_called_once_with('POST', '/ocr/pdf', skip_accept_encoding=True)
        self.http.send.assert_called_once_with(PDF)
        return dict(x.args for x in self.http.putheader.call_args_list)['X-Request-ID']

    def test_ma_core_hop_le_gui_nguyen_ma_va_khong_sinh_uuid(self):
        with patch.object(kn, 'uuid4', side_effect=AssertionError('Không thay mã Core')):
            for hex_ma in ('0' * 32, 'f' * 32, MA_CORE[4:]):
                with self.subTest(hex_ma=hex_ma):
                    self.assertEqual(self._gui('ocr:' + hex_ma), 'ocr:' + hex_ma)

    def test_uuid_cu_van_chuan_hoa_va_gui_duoc(self):
        ma = UUID('12345678-1234-5678-9abc-def012345678')
        for dau_vao in (str(ma), ma, str(ma).upper(), ma.hex, ma.urn, '{' + str(ma) + '}'):
            with self.subTest(dau_vao=dau_vao):
                self.assertEqual(self._gui(dau_vao), str(ma))

    def test_khong_cap_ma_van_sinh_uuid_moi(self):
        ma_1 = self._gui(None)
        ma_2 = self._gui(None)
        self.assertEqual(UUID(ma_1).version, 4)
        self.assertEqual(UUID(ma_2).version, 4)
        self.assertNotEqual(ma_1, ma_2)

    def test_ma_core_sai_va_dang_khac_bi_chan_truoc_ket_noi(self):
        cac_ma_sai = (
            'ocr:' + 'a' * 31, 'ocr:' + 'a' * 33,
            'ocr:' + 'A' * 32, MA_CORE[:-1] + 'F', 'OCR:' + 'a' * 32,
            MA_CORE[:-1] + 'g', MA_CORE[:-1] + 'é', MA_CORE[:-1] + 'ａ',
            'ocr:' + '１' * 32, 'ocr:', ' ' + MA_CORE, MA_CORE + ' ',
            MA_CORE + '\n', MA_CORE + '\r\nX-Request-ID: DEMO', MA_CORE + '\x00',
            MA_CORE + '/demo', '../' + MA_CORE, MA_CORE.replace(':', ':/'),
            TEN_TEP, 'hd20261108000000_abcdef', 'demo:' + 'a' * 32,
            '', 123, b'ocr:' + b'a' * 32,
        )
        for ma in cac_ma_sai:
            with self.subTest(ma=ma):
                with self.assertRaises(kn.LoiKetNoiABBYY) as cm:
                    self.client.doc_pdf(PDF, ma_yeu_cau=ma)
                err = cm.exception
                self.assertEqual(err.code, 'ABBYY_CAU_HINH')
                self.assertEqual(str(err), 'Cấu hình kết nối nhận dạng chưa hợp lệ.')
                self.assertIsNone(err.ma_yeu_cau)
                self.assertFalse(err.chua_ro_da_nhan)
                self.assertIsNone(err.__cause__)
                self.assertIsNone(err.__context__)
        self.tao_http.assert_not_called()
        self.http.putheader.assert_not_called()
        self.http.send.assert_not_called()

    def test_ma_core_qua_http_client_va_parser_that_voi_socket_gia(self):
        sock = Mock()
        sock.makefile.return_value = io.BytesIO(
            b'HTTP/1.1 200 OK\r\nContent-Type: application/pdf\r\nContent-Length: '
            + str(len(PDF_RA)).encode('ascii') + b'\r\nConnection: close\r\n\r\n' + PDF_RA)
        with patch.object(kn.http.client, 'HTTPSConnection', HTTPS_THAT), \
                patch('socket.create_connection', return_value=sock), \
                patch.object(self.tls, 'wrap_socket', return_value=sock):
            self.assertEqual(self.client.doc_pdf(PDF, ma_yeu_cau=MA_CORE), PDF_RA)
        raw_gui = b''.join(x.args[0] for x in sock.sendall.call_args_list)
        self.assertTrue(raw_gui.startswith(b'POST /ocr/pdf HTTP/1.1\r\n'))
        self.assertEqual(raw_gui.count(b'X-Request-ID: ' + MA_CORE.encode('ascii') + b'\r\n'), 1)
        self.assertNotIn(TEN_TEP.encode('ascii'), raw_gui)
        self.assertTrue(raw_gui.endswith(PDF))
        sock.close.assert_called()

    def _gui_qua_cau(self, *, doi_header=None):
        backend = Mock(spec=cn.HotFolderPDF)
        backend.doc_pdf.return_value = PDF_RA
        logs = []
        cau = cn.CauNoiABBYY(cn.CauHinhCauNoi(
            bat=True, khoa=KHOA, ip_core=('192.0.2.10',)),
            hot_folder=backend, ghi_log=logs.append)
        sock, raw_gui = Mock(), bytearray()
        sock.sendall.side_effect = raw_gui.extend

        def nhan(*args, **kwargs):
            raw = bytes(raw_gui)
            if doi_header is not None:
                raw = raw.replace(b'X-Request-ID: ' + MA_CORE.encode('ascii') + b'\r\n',
                                  doi_header)
            phan_hoi = phan_hoi_tu_cau(cau, raw)
            if doi_header is None:
                self.assertIn(b'X-Correlation-ID: ' + MA_CORE.encode('ascii') + b'\r\n',
                              phan_hoi.getvalue())
            return phan_hoi

        sock.makefile.side_effect = nhan
        with patch.object(kn.http.client, 'HTTPSConnection', HTTPS_THAT), \
                patch('socket.create_connection', return_value=sock), \
                patch.object(self.tls, 'wrap_socket', return_value=sock):
            if doi_header is None:
                self.assertEqual(self.client.doc_pdf(PDF, ma_yeu_cau=MA_CORE), PDF_RA)
            else:
                with self.assertRaises(kn.LoiKetNoiABBYY) as cm:
                    self.client.doc_pdf(PDF, ma_yeu_cau=MA_CORE)
                self.assertEqual(cm.exception.code, 'ABBYY_PHAN_HOI_SAI')
                self.assertEqual(cm.exception.ma_yeu_cau, MA_CORE)
                self.assertFalse(cm.exception.chua_ro_da_nhan)
        return cau, backend, logs

    def test_ma_core_xuyen_client_va_cau_voi_hai_parser_http_that(self):
        cau, backend, logs = self._gui_qua_cau()
        self.assertEqual(cau._ma_da_nhan, {MA_CORE})
        self.assertEqual(logs[0]['ma_tuong_quan'], MA_CORE)
        self.assertEqual(logs[0]['ket_qua'], 200)
        backend.doc_pdf.assert_called_once()
        self.assertEqual(backend.doc_pdf.call_args.kwargs['ma_tuong_quan'], MA_CORE)

    def test_header_sai_va_gia_mao_bi_cau_chan_qua_duong_http_that(self):
        for ma in (TEN_TEP, 'ocr:' + 'a' * 31, 'ocr:' + 'a' * 33,
                   'ocr:' + 'A' * 32, MA_CORE + '.pdf', '../' + MA_CORE):
            with self.subTest(ma=ma):
                cau, backend, logs = self._gui_qua_cau(
                    doi_header=b'X-Request-ID: ' + ma.encode('ascii') + b'\r\n')
                self.assertEqual(cau._ma_da_nhan, set())
                self.assertEqual(logs[0]['ma_tuong_quan'], '')
                self.assertEqual(logs[0]['ket_qua'], 400)
                backend.doc_pdf.assert_not_called()
        for ma in (MA_CORE, TEN_TEP):
            with self.subTest(header_trung=ma):
                cau, backend, logs = self._gui_qua_cau(doi_header=(
                    b'X-Request-ID: ' + MA_CORE.encode('ascii')
                    + b'\r\nx-request-id: ' + ma.encode('ascii') + b'\r\n'))
                self.assertEqual(cau._ma_da_nhan, set())
                self.assertEqual(logs[0]['ket_qua'], 400)
                backend.doc_pdf.assert_not_called()

    def test_loi_ket_noi_giu_ma_goc_nhung_thong_diep_khong_lo_ma_bam(self):
        bam = hashlib.sha256(PDF).hexdigest()
        for sau_gui in (False, True):
            with self.subTest(sau_gui=sau_gui):
                self.http.reset_mock()
                self.http.connect.side_effect = None
                self.http.getresponse.side_effect = self._phan_hoi
                exc = ConnectionResetError(MA_CORE + ' ' + TEN_TEP + ' ' + bam)
                if sau_gui:
                    self.http.getresponse.side_effect = exc
                else:
                    self.http.connect.side_effect = exc
                with self.assertNoLogs(), patch('sys.stdout', new_callable=io.StringIO) as stdout, \
                        patch('sys.stderr', new_callable=io.StringIO) as stderr:
                    with self.assertRaises(kn.LoiKetNoiABBYY) as cm:
                        self.client.doc_pdf(PDF, ma_yeu_cau=MA_CORE)
                err = cm.exception
                self.assertEqual(err.code, 'ABBYY_CHUA_RO_DA_NHAN' if sau_gui else 'ABBYY_KHONG_KET_NOI')
                self.assertEqual(err.ma_yeu_cau, MA_CORE)
                self.assertEqual(err.chua_ro_da_nhan, sau_gui)
                thong_diep = (str(err) + repr(err) + ''.join(traceback.format_exception(err))
                              + stdout.getvalue() + stderr.getvalue())
                for bi_mat in (MA_CORE, TEN_TEP, MA_CORE[4:], bam):
                    self.assertNotIn(bi_mat, thong_diep)
                    self.assertNotIn(bi_mat, str(exc))
                self.assertIsNone(err.__cause__)
                self.assertIsNone(err.__context__)
                self.assertIsNone(exc.__traceback__)
                self.http.connect.assert_called_once()
                self.http.close.assert_called_once()
                if sau_gui:
                    self.assertIn(('X-Request-ID', MA_CORE),
                                  [x.args for x in self.http.putheader.call_args_list])
                    self.http.send.assert_called_once_with(PDF)
                else:
                    self.http.send.assert_not_called()


if __name__ == '__main__':
    unittest.main()
