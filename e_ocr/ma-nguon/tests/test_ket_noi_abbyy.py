"""KN3: HTTP/PDF DEMO trong RAM; cấm socket, filesystem, tiến trình thật."""

from dataclasses import replace
from email.message import Message
import http.client
import importlib
import io
import ssl
import threading
import traceback
import unittest
from unittest.mock import Mock, patch
from uuid import UUID

from kho_tri_thuc.engines.e_ocr import ket_noi_abbyy as kn
from kho_tri_thuc.engines.e_ocr import cau_noi_abbyy as cn
from kho_tri_thuc.engines.e_ocr.chon_nguon import _ly_do_loi


KHOA = b'DEMO-khoa-chi-o-trong-RAM-1234567890123456'
PDF = b'%PDF-1.4\nDEMO quet\n%%EOF'
PDF_RA = b'%PDF-1.4\nDEMO lop chu\n%%EOF'


class PhanHoiGia:
    def __init__(self, body=PDF_RA, *, status=200, headers=None):
        self.status = status
        self.headers = [('Content-Type', 'application/pdf'), ('Content-Length', str(len(body)))]
        if headers is not None:
            self.headers = headers
        self.body = io.BytesIO(body)
        self.close = Mock()
        self.read1 = Mock(side_effect=self.body.read)

    def getheaders(self):
        return self.headers


class KetNoiTests(unittest.TestCase):
    def setUp(self):
        for ten in ('socket.socket', 'socket.create_connection', 'socket.getaddrinfo',
                    'subprocess.Popen', 'builtins.open', 'pathlib.Path.open',
                    'pathlib.Path.read_bytes', 'pathlib.Path.write_bytes', 'pathlib.Path.mkdir'):
            p = patch(ten, side_effect=AssertionError('Cấm I/O thật trong test KN3'))
            p.start()
            self.addCleanup(p.stop)
        self.tls = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.c = kn.CauHinhKetNoi(bat=True, may_chu='abbyy.demo.invalid', khoa=KHOA, tls=self.tls)
        self.ph = PhanHoiGia()
        self.http = Mock()
        self.http.getresponse.return_value = self.ph
        p = patch.object(kn.http.client, 'HTTPSConnection', return_value=self.http)
        self.tao_http = p.start()
        self.addCleanup(p.stop)
        self.client = kn.KetNoiABBYY(self.c)

    def loi(self, code, *, client=None, **kwargs):
        with self.assertRaises(kn.LoiKetNoiABBYY) as cm:
            (client or self.client).doc_pdf(PDF, **kwargs)
        self.assertEqual(cm.exception.code, code)
        self.assertEqual(cm.exception.ma, code)
        return cm.exception

    def test_mac_dinh_tat_va_import_khong_io(self):
        with patch.object(kn.ssl, 'create_default_context', side_effect=AssertionError('Không tự đọc CA')):
            importlib.reload(kn)
            client = kn.KetNoiABBYY()
            self.assertFalse(client.san_sang())
            self.loi('ABBYY_KHONG_KET_NOI', client=client)
        self.tao_http.assert_not_called()

    def test_san_sang_chi_la_cau_hinh_cuc_bo_khong_probe_mang(self):
        self.assertTrue(self.client.san_sang())
        self.tao_http.assert_not_called()
        self.tls.check_hostname = False
        self.assertFalse(self.client.san_sang())
        self.loi('ABBYY_KHONG_KET_NOI')
        self.tao_http.assert_not_called()

    def test_tu_choi_cau_hinh_http_url_khoa_va_gioi_han_sai(self):
        for kw in ({'may_chu': 'http://abbyy.demo.invalid'}, {'may_chu': 'khoa@may'},
                   {'may_chu': 'may\r\nAuthorization: bi-mat'}, {'may_chu': 'may:9443'},
                   {'may_chu': '::1%khoa'}, {'khoa': b'qua-ngan'}, {'khoa': b'x' * 31 + b'\n'},
                   {'khoa': 'x' * 40}, {'tls': None}, {'cong': 0}, {'bat': 1},
                   {'doc_giay': 0}, {'ket_noi_giay': float('nan')},
                   {'toi_da_giay': float('inf')}, {'toi_da_byte_ra': True}, {'toi_da_byte': -1}):
            with self.subTest(truong=next(iter(kw))):
                with self.assertRaises(kn.LoiKetNoiABBYY) as cm:
                    kn.KetNoiABBYY(replace(self.c, **kw))
                self.assertEqual(cm.exception.code, 'ABBYY_CAU_HINH')
        self.tao_http.assert_not_called()

    def test_tls_bat_buoc_ca_hostname_va_tls_12(self):
        for mode in (ssl.CERT_NONE, ssl.CERT_OPTIONAL):
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.check_hostname = False
            ctx.verify_mode = mode
            with self.assertRaises(kn.LoiKetNoiABBYY):
                kn.KetNoiABBYY(replace(self.c, tls=ctx))
        self.tls.check_hostname = False
        with self.assertRaises(kn.LoiKetNoiABBYY):
            kn.KetNoiABBYY(self.c)
        self.tao_http.assert_not_called()

    def test_tls_cu_bi_tu_choi_va_ipv6_hop_le(self):
        self.assertTrue(kn.KetNoiABBYY(replace(self.c, may_chu='2001:db8::10')).san_sang())
        with patch('warnings.warn'):
            # Không nới xuống TLS cũ; chỉ giả thuộc tính để kiểm validation.
            with patch.object(ssl.SSLContext, 'minimum_version', new=ssl.TLSVersion.TLSv1_1):
                with self.assertRaises(kn.LoiKetNoiABBYY):
                    kn.KetNoiABBYY(self.c)

    def test_post_pdf_khoa_chi_header_uuid_va_khong_debug(self):
        self.assertEqual(self.client.doc_pdf(PDF, '.PDF'), PDF_RA)
        self.tao_http.assert_called_once()
        args, kw = self.tao_http.call_args
        self.assertEqual(args, ('abbyy.demo.invalid', 9443))
        self.assertIs(kw['context'], self.tls)
        self.assertGreater(kw['timeout'], 0)
        self.assertLessEqual(kw['timeout'], self.c.ket_noi_giay)
        self.http.set_debuglevel.assert_called_once_with(0)
        self.http.putrequest.assert_called_once_with('POST', '/ocr/pdf', skip_accept_encoding=True)
        h = dict(x.args for x in self.http.putheader.call_args_list)
        self.assertEqual(h['Authorization'], 'Bearer ' + KHOA.decode())
        self.assertEqual(h['Content-Length'], str(len(PDF)))
        self.assertEqual(h['Content-Type'], 'application/pdf')
        self.assertEqual(UUID(h['X-Request-ID']).version, 4)
        self.http.send.assert_called_once_with(PDF)
        self.http.close.assert_called_once()
        self.ph.close.assert_called_once()
        self.assertNotIn(KHOA.decode(), repr(self.c))

    def test_ma_core_cap_duoc_giu_nguyen_va_ma_moi_khong_trung(self):
        ma = str(UUID(int=24))
        self.client.doc_pdf(PDF, ma_yeu_cau=ma)
        self.assertIn(('X-Request-ID', ma), [x.args for x in self.http.putheader.call_args_list])
        self.http.reset_mock()
        self.http.getresponse.return_value = PhanHoiGia()
        self.client.doc_pdf(PDF)
        h1 = dict(x.args for x in self.http.putheader.call_args_list)['X-Request-ID']
        self.http.reset_mock()
        self.http.getresponse.return_value = PhanHoiGia()
        self.client.doc_pdf(PDF)
        h2 = dict(x.args for x in self.http.putheader.call_args_list)['X-Request-ID']
        self.assertNotEqual(h1, h2)
        self.loi('ABBYY_CAU_HINH', ma_yeu_cau='../DEMO-khong-phai-ma')

    def test_dau_vao_sai_va_anh_bi_chan_truoc_gui(self):
        for raw, duoi in ((b'', 'pdf'), (bytearray(PDF), 'pdf'), (b'%PDF-hong', 'pdf'),
                          (PDF, 'png'), (PDF, '../pdf'), (PDF, None)):
            with self.subTest(duoi=duoi):
                with self.assertRaises(kn.LoiKetNoiABBYY) as cm:
                    self.client.doc_pdf(raw, duoi)
                self.assertEqual(cm.exception.code, 'OCR_DINH_DANG')
        self.loi('OCR_KICH_THUOC', client=kn.KetNoiABBYY(replace(self.c, toi_da_byte=len(PDF) - 1)))
        self.tao_http.assert_not_called()

    def test_timeout_ket_noi_chua_gui_va_fallback_nhan_dung_ly_do(self):
        self.http.connect.side_effect = TimeoutError('DEMO loi bi mat')
        err = self.loi('OCR_QUA_GIO')
        self.assertFalse(err.chua_ro_da_nhan)
        self.assertEqual(_ly_do_loi(err), 'qua_thoi_gian')
        self.http.endheaders.assert_not_called()
        self.http.connect.assert_called_once()

    def test_mat_ket_noi_truoc_gui(self):
        self.http.connect.side_effect = ConnectionRefusedError('DEMO')
        err = self.loi('ABBYY_KHONG_KET_NOI')
        self.assertFalse(err.chua_ro_da_nhan)
        self.assertEqual(_ly_do_loi(err), 'khong_ket_noi')
        self.http.send.assert_not_called()

    def test_mat_phan_hoi_timeout_reset_va_http_hong_deu_chua_ro(self):
        for exc in (TimeoutError('DEMO'), ConnectionResetError('DEMO'),
                    http.client.RemoteDisconnected('DEMO'), http.client.BadStatusLine('DEMO')):
            with self.subTest(loai=type(exc).__name__):
                self.http.reset_mock()
                self.http.getresponse.side_effect = exc
                err = self.loi('ABBYY_CHUA_RO_DA_NHAN')
                self.assertTrue(err.chua_ro_da_nhan)
                self.assertIsNotNone(UUID(err.ma_yeu_cau))
                self.http.connect.assert_called_once()
                self.http.send.assert_called_once()
                self.http.close.assert_called_once()

    def test_loi_gui_mot_phan_khong_duoc_khang_dinh_chua_nhan(self):
        for pha in ('endheaders', 'send'):
            with self.subTest(pha=pha):
                self.http.reset_mock()
                getattr(self.http, pha).side_effect = BrokenPipeError('DEMO')
                self.assertTrue(self.loi('ABBYY_CHUA_RO_DA_NHAN').chua_ro_da_nhan)
                getattr(self.http, pha).side_effect = None

    def test_chung_thu_sai_ca_het_han_hoac_hostname_deu_khong_gui_khoa(self):
        for ly_do in ('certificate verify failed', 'certificate has expired', 'hostname mismatch'):
            with self.subTest(ly_do=ly_do):
                self.http.connect.side_effect = ssl.SSLCertVerificationError(1, ly_do)
                self.assertFalse(self.loi('ABBYY_CHUNG_THU').chua_ro_da_nhan)
        self.http.putheader.assert_not_called()
        self.http.send.assert_not_called()

    def test_connect_http_client_that_truyen_ca_va_hostname_den_tls(self):
        # Chạy connect chuẩn với socket giả; tầng TLS từ chối chứng thư.
        with patch.object(kn.http.client, 'HTTPSConnection', self._http_that), \
                patch('socket.create_connection', return_value=Mock()) as tao_socket, \
                patch.object(self.tls, 'wrap_socket', side_effect=ssl.SSLCertVerificationError(1, 'DEMO')) as boc:
            self.loi('ABBYY_CHUNG_THU')
        tao_socket.assert_called_once()
        self.assertEqual(boc.call_args.kwargs['server_hostname'], self.c.may_chu)
        self.assertEqual(self.tls.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(self.tls.check_hostname)

    def test_http_client_va_parser_that_voi_socket_gia_khong_debug_lo_khoa(self):
        for chunked in (False, True):
            with self.subTest(chunked=chunked):
                sock = Mock()
                body = (f'{len(PDF_RA):x}\r\n'.encode() + PDF_RA + b'\r\n0\r\n\r\n') if chunked else PDF_RA
                kich_thuoc = b'Transfer-Encoding: chunked' if chunked else f'Content-Length: {len(body)}'.encode()
                sock.makefile.return_value = io.BytesIO(b'HTTP/1.1 200 OK\r\nContent-Type: application/pdf\r\n'
                                                       + kich_thuoc + b'\r\nConnection: close\r\n\r\n' + body)
                with patch.object(kn.http.client, 'HTTPSConnection', self._http_that), \
                        patch('socket.create_connection', return_value=sock), \
                        patch.object(self.tls, 'wrap_socket', return_value=sock), \
                        patch.object(http.client.HTTPConnection, 'debuglevel', 1), \
                        patch('sys.stdout', new_callable=io.StringIO) as stdout:
                    self.assertEqual(self.client.doc_pdf(PDF), PDF_RA)
                self.assertEqual(stdout.getvalue(), '')
                gui = b''.join(call.args[0] for call in sock.sendall.call_args_list)
                self.assertTrue(gui.startswith(b'POST /ocr/pdf HTTP/1.1\r\n'))
                self.assertEqual(gui.count(KHOA), 1)
                self.assertTrue(gui.endswith(PDF))
                sock.close.assert_called()

    def test_status_khong_doc_body_khong_redirect_khong_gui_lai(self):
        for status, code, chua_ro in ((401, 'ABBYY_KHOA_SAI', False),
                                     (403, 'ABBYY_KHOA_HOAC_IP', False),
                                     (409, 'ABBYY_YEU_CAU_TRUNG', True),
                                     (413, 'OCR_KICH_THUOC', False),
                                     (503, 'ABBYY_BAN', False),
                                     (504, 'ABBYY_CHUA_RO_DA_NHAN', True),
                                     (502, 'ABBYY_LOI_XU_LY', True),
                                     (302, 'ABBYY_PHAN_HOI_SAI', True)):
            with self.subTest(status=status):
                self.http.reset_mock()
                ph = PhanHoiGia(KHOA, status=status)
                self.http.getresponse.return_value = ph
                err = self.loi(code)
                self.assertEqual(err.chua_ro_da_nhan, chua_ro)
                ph.read1.assert_not_called()
                self.http.connect.assert_called_once()
                self.http.send.assert_called_once()

    def test_phan_hoi_sai_mime_do_dai_encoding_header_trung(self):
        for headers in ([('Content-Type', 'text/html')],
                        [('Content-Type', 'application/pdf'), ('Content-Length', '-1')],
                        [('Content-Type', 'application/pdf'), ('Content-Length', '１２')],
                        [('Content-Type', 'application/pdf'), ('Content-Length', '9' * 40)],
                        [('Content-Type', 'application/pdf'), ('Content-Length', '1'), ('content-length', '1')],
                        [('Content-Type', 'application/pdf'), ('content-type', 'application/pdf')],
                        [('Content-Type', 'application/pdf'), ('Content-Encoding', 'gzip')],
                        [('Content-Type', 'application/pdf'), ('Transfer-Encoding', 'gzip')],
                        [('Content-Type', 'application/pdf'), ('Transfer-Encoding', 'chunked'), ('Content-Length', '1')]):
            with self.subTest(headers=headers):
                ph = PhanHoiGia(headers=headers)
                self.http.getresponse.return_value = ph
                self.assertTrue(self.loi('ABBYY_PHAN_HOI_SAI').chua_ro_da_nhan)
                ph.read1.assert_not_called()

    def test_qua_co_header_chan_truoc_doc(self):
        self.ph.headers[-1] = ('Content-Length', str(self.c.toi_da_byte_ra + 1))
        self.loi('ABBYY_PHAN_HOI_QUA_CO')
        self.ph.read1.assert_not_called()

    def test_qua_co_khong_length_va_chunked_doc_toi_da_gioi_han_cong_mot(self):
        for chuyen in ([], [('Transfer-Encoding', 'chunked')]):
            with self.subTest(chunked=bool(chuyen)):
                ph = PhanHoiGia(body=PDF_RA + b'x' * 50,
                               headers=[('Content-Type', 'application/pdf')] + chuyen)
                self.http.getresponse.return_value = ph
                self.loi('ABBYY_PHAN_HOI_QUA_CO', client=kn.KetNoiABBYY(replace(self.c, toi_da_byte_ra=32)))
                self.assertEqual(ph.body.tell(), 33)
                self.assertEqual(ph.read1.call_args.args[0], 33)

    def test_pdf_sai_thieu_noi_dung_va_ket_thuc(self):
        for body in (b'', b'<html>DEMO</html>', b'%PDF-1.4\nDEMO'):
            self.http.getresponse.return_value = PhanHoiGia(body)
            self.loi('ABBYY_PHAN_HOI_SAI')

    def test_body_bi_cat_mat_va_read_timeout_deu_chua_ro(self):
        self.ph.headers[-1] = ('Content-Length', str(len(PDF_RA) + 1))
        self.assertEqual(self.loi('ABBYY_CHUA_RO_DA_NHAN').nguyen_nhan, 'ABBYY_PHAN_HOI_SAI')
        for exc in (TimeoutError('DEMO'), http.client.IncompleteRead(b'DEMO-bi-mat'), ConnectionResetError()):
            self.ph.read1.side_effect = exc
            self.loi('ABBYY_CHUA_RO_DA_NHAN')

    def test_doc_tung_khoi_va_timeout_rieng_ca_khi_http_da_tach_socket(self):
        ph = PhanHoiGia(headers=[('Content-Type', 'application/pdf')])
        ph.read1.side_effect = [PDF_RA[:8], PDF_RA[8:], b'']
        sock = self.http.sock

        def nhan():
            self.http.sock = None  # HTTPResponse.will_close trong stdlib.
            return ph

        self.http.getresponse.side_effect = nhan
        self.assertEqual(self.client.doc_pdf(PDF), PDF_RA)
        self.assertEqual(ph.read1.call_count, 3)
        self.assertGreaterEqual(sock.settimeout.call_count, 6)
        self.assertTrue(all(0 < x.args[0] <= self.c.doc_giay for x in sock.settimeout.call_args_list))

    def test_huy_truoc_connect_khong_gui(self):
        huy = threading.Event()
        huy.set()
        err = self.loi('OCR_HUY', huy=huy)
        self.assertFalse(err.chua_ro_da_nhan)
        self.tao_http.assert_not_called()

    def test_huy_sau_connect_truoc_header_khong_gui(self):
        huy = threading.Event()
        self.http.connect.side_effect = huy.set
        self.assertFalse(self.loi('OCR_HUY', huy=huy).chua_ro_da_nhan)
        self.http.putheader.assert_not_called()

    def test_huy_giua_cac_khoi_gui_khong_gui_phan_con_lai(self):
        huy = threading.Event()
        self.http.send.side_effect = lambda raw: huy.set()
        with self.assertRaises(kn.LoiKetNoiABBYY) as cm:
            self.client.doc_pdf(b'%PDF-' + b'x' * 150_000 + b'%%EOF', huy=huy)
        self.assertEqual(cm.exception.code, 'OCR_HUY')
        self.assertTrue(cm.exception.chua_ro_da_nhan)
        self.http.send.assert_called_once()
        self.http.getresponse.assert_not_called()

    def test_huy_sau_doc_ket_qua_khong_tra_thanh_cong(self):
        huy = threading.Event()

        def doc(n):
            huy.set()
            return PDF_RA

        self.ph.read1.side_effect = doc
        self.assertTrue(self.loi('OCR_HUY', huy=huy).chua_ro_da_nhan)

    def test_huy_dang_cho_header_dong_socket_khong_co_luong_gui_ngam(self):
        huy = threading.Event()
        dong = threading.Event()
        self.http.sock.shutdown.side_effect = lambda how: dong.set()

        def nhan():
            huy.set()
            if not dong.wait(1):
                self.fail('Luồng hủy chưa đóng socket giả')
            raise OSError('DEMO socket da dong')

        self.http.getresponse.side_effect = nhan
        self.assertTrue(self.loi('OCR_HUY', huy=huy).chua_ro_da_nhan)
        self.http.sock.shutdown.assert_called_once_with(kn.socket.SHUT_RDWR)
        self.http.send.assert_called_once()

    def test_huy_dang_doc_body_sau_khi_http_tach_socket(self):
        huy, dong = threading.Event(), threading.Event()
        sock = self.http.sock
        sock.shutdown.side_effect = lambda how: dong.set()

        def nhan():
            self.http.sock = None
            return self.ph

        def doc(n):
            huy.set()
            if not dong.wait(1):
                self.fail('Hủy chưa đóng socket của phản hồi')
            raise OSError('DEMO')

        self.http.getresponse.side_effect = nhan
        self.ph.read1.side_effect = doc
        self.assertTrue(self.loi('OCR_HUY', huy=huy).chua_ro_da_nhan)
        sock.shutdown.assert_called_once()
        self.ph.close.assert_called_once()

    def test_deadline_tong_ngat_cho_doc_ke_ca_khong_co_tin_hieu_huy(self):
        dong = threading.Event()
        self.http.sock.shutdown.side_effect = lambda how: dong.set()

        def nhan():
            if not dong.wait(1):
                self.fail('Deadline chưa đóng socket giả')
            raise OSError('DEMO')

        self.http.getresponse.side_effect = nhan
        err = self.loi('ABBYY_CHUA_RO_DA_NHAN', client=kn.KetNoiABBYY(replace(self.c, toi_da_giay=0.1)))
        self.assertEqual(err.nguyen_nhan, 'OCR_QUA_GIO')
        self.http.sock.shutdown.assert_called_once()

    def test_loi_goc_va_loi_dong_khong_lo_khoa_trong_log_ngoai_le(self):
        exc = RuntimeError(KHOA.decode() + ' DEMO duong dan noi dung')
        self.http.getresponse.side_effect = exc
        self.http.close.side_effect = RuntimeError(KHOA.decode())
        with self.assertNoLogs(), patch('sys.stdout', new_callable=io.StringIO) as stdout, \
                patch('sys.stderr', new_callable=io.StringIO) as stderr:
            err = self.loi('ABBYY_CHUA_RO_DA_NHAN')
        text = ''.join(traceback.format_exception(err)) + repr(vars(err)) + stdout.getvalue() + stderr.getvalue()
        self.assertNotIn(KHOA.decode(), text)
        self.assertNotIn(KHOA.decode(), str(exc))
        self.assertIsNone(err.__context__)
        self.assertIsNone(err.__cause__)
        self.assertIsNone(exc.__traceback__)

    def test_giao_thuc_kn2_that_trong_ram_trung_ma_khoa_ip(self):
        backend = Mock()
        backend.doc_pdf.return_value = PDF_RA
        service = cn.CauNoiABBYY(cn.CauHinhCauNoi(bat=True, khoa=KHOA, ip_core=('192.0.2.10',)),
                                hot_folder=backend, ghi_log=lambda x: None)
        ma = str(UUID(int=28))
        ip = ['192.0.2.10']

        def nhan():
            headers = Message()
            for call in self.http.putheader.call_args_list:
                headers[call.args[0]] = call.args[1]
            peer = Mock()
            peer.getpeername.return_value = (ip[0], 123)
            body = b''.join(call.args[0] for call in self.http.send.call_args_list)
            result = service.xu_ly(cn.YeuCau(peer, headers, io.BytesIO(body)))
            return PhanHoiGia(result.noi_dung, status=result.ma_http,
                              headers=[('Content-Type', result.loai_noi_dung),
                                       ('Content-Length', str(len(result.noi_dung)))])

        self.http.getresponse.side_effect = nhan
        self.assertEqual(self.client.doc_pdf(PDF, ma_yeu_cau=ma), PDF_RA)
        self.http.reset_mock()
        self.loi('ABBYY_YEU_CAU_TRUNG', ma_yeu_cau=ma)
        backend.doc_pdf.assert_called_once()
        for sai_khoa in (True, False):
            self.http.reset_mock()
            ip[0] = '192.0.2.10' if sai_khoa else '192.0.2.11'
            client = kn.KetNoiABBYY(replace(self.c, khoa=b'x' * 40)) if sai_khoa else self.client
            self.loi('ABBYY_KHOA_HOAC_IP', client=client)
        backend.doc_pdf.assert_called_once()


# Giữ lớp chuẩn trước setUp patch factory để kiểm đường TLS stdlib.
KetNoiTests._http_that = staticmethod(http.client.HTTPSConnection)


if __name__ == '__main__':
    unittest.main()
