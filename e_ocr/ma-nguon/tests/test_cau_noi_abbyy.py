"""KN2/OCR-CR-6: PDF, cầu nối và Hot Folder giả; không mạng/ABBYY thật."""

from collections import OrderedDict
from dataclasses import replace
from email.message import Message
import importlib
import io
import json
import re
import ssl
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from uuid import UUID
import warnings

from kho_tri_thuc.engines.e_ocr import cau_noi_abbyy as cn
from kho_tri_thuc.engines.e_ocr import abbyy, chon_nguon as chon
from kho_tri_thuc.engines.e_ocr.ket_noi_abbyy import CauHinhKetNoi, KetNoiABBYY
from kho_tri_thuc.engines.e_ocr.lib import cong_ocr as ocr
from kho_tri_thuc.engines.e_ocr.tests import test_hot_folder_pdf as hf
from kho_tri_thuc.engines.e_ocr.tests.test_ket_noi_abbyy_ma import HTTPS_THAT, phan_hoi_tu_cau
from kho_tri_thuc.sdk_core.engine import SDKEngine
from kho_tri_thuc.sdk_core.primitives import DataError


KHOA = b'DEMO-khoa-cau-noi-khong-phai-khoa-that-123456'
IP_CORE = '192.0.2.10'
PDF = b'%PDF-1.4\nDEMO quet\n%%EOF'
PDF_RA = b'%PDF-1.4\nDEMO lop chu\n%%EOF'


class CauNoiTests(unittest.TestCase):
    def setUp(self):
        self.chan = []
        for ten in ('socket.socket', 'socket.create_connection', 'subprocess.Popen',
                    'builtins.open', 'pathlib.Path.open', 'pathlib.Path.read_bytes',
                    'pathlib.Path.write_bytes', 'pathlib.Path.mkdir'):
            p = patch(ten, side_effect=AssertionError('Không mạng/tiến trình/filesystem thật'))
            self.chan.append(p.start())
            self.addCleanup(p.stop)
        self.now = 0.0
        self.logs = []
        self.backend = Mock(spec=cn.HotFolderPDF)
        self.backend.doc_pdf.return_value = PDF_RA
        self.c = cn.CauHinhCauNoi(bat=True, khoa=KHOA, ip_core=(IP_CORE,))
        self.dv = self.tao_dich_vu()

    def tao_dich_vu(self, **cau_hinh):
        return cn.CauNoiABBYY(replace(self.c, **cau_hinh), hot_folder=self.backend,
                             ghi_log=self.logs.append, dong_ho=lambda: self.now)

    def yeu_cau(self, *, ip=IP_CORE, khoa=KHOA, ma=1, raw=PDF, headers=None, **kwargs):
        h = Message()
        if khoa is not None:
            h['Authorization'] = 'Bearer ' + khoa.decode('ascii')
        h['Content-Length'] = str(len(raw))
        h['Content-Type'] = 'application/pdf'
        h['X-Request-ID'] = str(UUID(int=ma))
        for k, v in (headers or {}).items():
            if k in h:
                h.replace_header(k, v)
            else:
                h[k] = v
        ket_noi = Mock()
        ket_noi.getpeername.return_value = (ip, 12345)
        return cn.YeuCau(ket_noi, h, io.BytesIO(raw), **kwargs)

    def test_thieu_sai_khoa_van_kiem_socket_va_so_sanh_hang_thoi_gian(self):
        for khoa in (None, b'DEMO-sai-khoa'):
            with self.subTest(khoa_co_mat=khoa is not None):
                req = self.yeu_cau(khoa=khoa)
                with patch.object(cn.hmac, 'compare_digest', wraps=cn.hmac.compare_digest) as so:
                    self.assertEqual(self.dv.xu_ly(req).ma_http, 403)
                so.assert_called_once()
                req.ket_noi.getpeername.assert_called_once()
                self.assertEqual(req.luong.tell(), 0)
        self.backend.doc_pdf.assert_not_called()

    def test_dung_khoa_sai_ip_va_socket_loi_deu_tu_choi(self):
        for ip in ('192.0.2.11', 'khong-phai-ip'):
            self.assertEqual(self.dv.xu_ly(self.yeu_cau(ip=ip)).ma_http, 403)
        req = self.yeu_cau()
        req.ket_noi.getpeername.side_effect = OSError('DEMO loi socket bi mat')
        self.assertEqual(self.dv.xu_ly(req).ma_http, 403)
        self.backend.doc_pdf.assert_not_called()

    def test_x_forwarded_for_gia_khong_thay_the_ip_socket(self):
        req = self.yeu_cau(ip='192.0.2.99', headers={'X-Forwarded-For': IP_CORE})
        self.assertEqual(self.dv.xu_ly(req).ma_http, 403)
        req = self.yeu_cau(headers={'X-Forwarded-For': '192.0.2.99'})
        self.assertEqual(self.dv.xu_ly(req).ma_http, 200)

    def test_ipv4_mapped_cua_socket_duoc_chuan_hoa(self):
        self.assertEqual(self.dv.xu_ly(self.yeu_cau(ip='::ffff:' + IP_CORE)).ma_http, 200)

    def test_header_khoa_trung_bi_tu_choi(self):
        req = self.yeu_cau()
        req.headers['authorization'] = 'Bearer ' + KHOA.decode()
        self.assertEqual(self.dv.xu_ly(req).ma_http, 403)
        self.backend.doc_pdf.assert_not_called()

    def test_header_khoa_unicode_khong_duoc_thay_bang_ky_tu_khac(self):
        dv = self.tao_dich_vu(khoa=KHOA + b'?')
        req = self.yeu_cau(headers={'Authorization': 'Bearer ' + KHOA.decode() + 'Đ'})
        self.assertEqual(dv.xu_ly(req).ma_http, 403)
        self.backend.doc_pdf.assert_not_called()

    def test_qua_co_tu_header_khong_doc_body(self):
        req = self.yeu_cau(headers={'Content-Length': str(self.c.toi_da_byte + 1)})
        self.assertEqual(self.dv.xu_ly(req).ma_http, 413)
        self.assertEqual(req.luong.tell(), 0)
        self.backend.doc_pdf.assert_not_called()

    def test_doc_tung_khoi_co_gioi_han_va_tra_nguyen_pdf(self):
        req = self.yeu_cau()
        req = replace(req, luong=Mock(read1=Mock(side_effect=[PDF[:8], PDF[8:]])))
        ph = self.dv.xu_ly(req)
        self.assertEqual((ph.ma_http, ph.loai_noi_dung, ph.noi_dung),
                         (200, 'application/pdf', PDF_RA))
        self.assertEqual([x.args[0] for x in req.luong.read1.call_args_list], [len(PDF), len(PDF) - 8])
        self.backend.doc_pdf.assert_called_once()
        args, kw = self.backend.doc_pdf.call_args
        self.assertEqual(args, (PDF, 'pdf'))
        self.assertFalse(kw['huy'].is_set())
        self.assertEqual(kw['toi_da_byte_ra'], self.c.toi_da_byte_ra)
        self.assertEqual(ph.ma_tuong_quan, req.headers['X-Request-ID'])
        self.assertEqual(kw['ma_tuong_quan'], ph.ma_tuong_quan)

    def test_do_dai_am_trung_transfer_encoding_mime_va_ma_sai(self):
        for h in ({'Content-Length': '-1'}, {'Content-Length': '0'},
                  {'Content-Length': '9' * 50}, {'Content-Length': '１２'},
                  {'Transfer-Encoding': 'chunked'}, {'Content-Type': 'text/plain'},
                  {'X-Request-ID': '../DEMO.pdf'}):
            with self.subTest(headers=h):
                self.assertEqual(self.dv.xu_ly(self.yeu_cau(headers=h)).ma_http, 400)
        req = self.yeu_cau()
        req.headers['content-length'] = str(len(PDF))
        self.assertEqual(self.dv.xu_ly(req).ma_http, 400)
        req = self.yeu_cau()
        req.headers['Transfer-Encoding'] = 'chunked'
        req.headers['transfer-encoding'] = 'identity'
        self.assertEqual(self.dv.xu_ly(req).ma_http, 400)
        self.backend.doc_pdf.assert_not_called()

    def test_backend_tiem_chu_ky_cu_khong_can_tham_so_ma_moi(self):
        da_goi = []
        class BackendCu:
            def doc_pdf(inner, raw, duoi, *, huy, toi_da_byte_ra):
                da_goi.append((raw, duoi, toi_da_byte_ra))
                return PDF_RA
        dv = cn.CauNoiABBYY(self.c, hot_folder=BackendCu(), ghi_log=self.logs.append)
        self.assertEqual(dv.xu_ly(self.yeu_cau()).ma_http, 200)
        self.assertEqual(da_goi, [(PDF, 'pdf', self.c.toi_da_byte_ra)])

    def test_ket_qua_tra_sau_deadline_ghi_muon_khong_tra_thanh_cong(self):
        def nhan(*args, **kw):
            self.now = 6
            return PDF_RA
        self.backend.doc_pdf.side_effect = nhan
        dv = self.tao_dich_vu(toi_da_giay=5)
        self.assertEqual(dv.xu_ly(self.yeu_cau()).ma_http, 504)
        self.assertEqual(self.logs[0]['ket_qua'], 'kết quả muộn')
        self.assertEqual(self.logs[0]['ma_tuong_quan'], str(UUID(int=1)))
        self.assertEqual(dv.xu_ly(self.yeu_cau()).ma_http, 409)
        self.assertEqual(self.backend.doc_pdf.call_count, 1)

    def test_body_thieu_vuot_do_dai_va_pdf_hong_khong_gui(self):
        for raw in (b'', b'khong phai PDF', PDF[:-5]):
            dv = self.tao_dich_vu()
            self.assertEqual(dv.xu_ly(self.yeu_cau(raw=raw)).ma_http, 400)
        for phan in (b'', PDF + b'qua do dai'):
            req = replace(self.yeu_cau(), luong=Mock(read1=Mock(return_value=phan)))
            self.assertEqual(self.tao_dich_vu().xu_ly(req).ma_http, 400)
        self.backend.doc_pdf.assert_not_called()

    def test_trung_ma_sau_thanh_cong_khong_gui_lai(self):
        self.assertEqual(self.dv.xu_ly(self.yeu_cau()).ma_http, 200)
        req = self.yeu_cau(raw=PDF.replace(b'quet', b'khac'))
        self.assertEqual(self.dv.xu_ly(req).ma_http, 409)
        self.assertEqual(req.luong.tell(), 0)
        self.assertEqual(self.backend.doc_pdf.call_count, 1)

    def test_trung_ma_dang_xu_ly_va_hang_day_khong_gui_lai(self):
        dv = self.tao_dich_vu(toi_da_cho=0)
        def nhan(*args, **kwargs):
            self.assertEqual(dv.xu_ly(self.yeu_cau()).ma_http, 409)
            self.assertEqual(dv.xu_ly(self.yeu_cau(ma=2)).ma_http, 503)
            return PDF_RA
        self.backend.doc_pdf.side_effect = nhan
        self.assertEqual(dv.xu_ly(self.yeu_cau()).ma_http, 200)
        self.assertEqual(self.backend.doc_pdf.call_count, 1)
        self.backend.doc_pdf.side_effect = None
        self.assertEqual(dv.xu_ly(self.yeu_cau(ma=2)).ma_http, 200)

    def test_hai_luong_cho_huu_han_va_xu_ly_tuan_tu(self):
        dv = self.tao_dich_vu(toi_da_cho=1, cho_hang_giay=2)
        dang_chay, da_doc, tiep_tuc = threading.Event(), threading.Event(), threading.Event()
        ket_qua = []
        def nhan(*args, **kwargs):
            dang_chay.set()
            if not tiep_tuc.wait(2):
                raise TimeoutError
            return PDF_RA
        def doc(n):
            da_doc.set()
            return PDF
        self.backend.doc_pdf.side_effect = nhan
        req2 = replace(self.yeu_cau(ma=2), luong=Mock(read1=Mock(side_effect=doc)))
        t1 = threading.Thread(target=lambda: ket_qua.append(dv.xu_ly(self.yeu_cau()).ma_http))
        t2 = threading.Thread(target=lambda: ket_qua.append(dv.xu_ly(req2).ma_http))
        t1.start()
        try:
            self.assertTrue(dang_chay.wait(1))
            t2.start()
            self.assertTrue(da_doc.wait(1))
            self.assertEqual(dv.xu_ly(self.yeu_cau(ma=3)).ma_http, 503)
            self.assertEqual(self.backend.doc_pdf.call_count, 1)
        finally:
            tiep_tuc.set()
            t1.join(3)
            if t2.ident is not None:
                t2.join(3)
        self.assertFalse(t1.is_alive() or t2.is_alive())
        self.assertEqual(ket_qua, [200, 200])

    def test_so_ma_huu_han_khong_tu_quen_ma_cu(self):
        dv = self.tao_dich_vu(toi_da_ma=1)
        self.assertEqual(dv.xu_ly(self.yeu_cau()).ma_http, 200)
        self.assertEqual(dv.xu_ly(self.yeu_cau(ma=2)).ma_http, 503)
        self.assertEqual(dv.xu_ly(self.yeu_cau()).ma_http, 409)
        self.assertEqual(self.backend.doc_pdf.call_count, 1)

    def test_cho_hang_qua_gio_khong_goi_abbyy_va_khong_gui_lai(self):
        self.dv._xu_ly = Mock(acquire=Mock(return_value=False))
        self.assertEqual(self.dv.xu_ly(self.yeu_cau()).ma_http, 504)
        self.assertEqual(self.dv.xu_ly(self.yeu_cau()).ma_http, 409)
        self.dv._xu_ly.release.assert_not_called()
        self.backend.doc_pdf.assert_not_called()

    def test_timeout_doc_va_nho_giot_deu_khong_gui_abbyy(self):
        for cach in ('timeout', 'nho_giot'):
            with self.subTest(cach=cach):
                self.now = 0
                def doc(n):
                    if cach == 'timeout':
                        raise TimeoutError('DEMO noi dung bi mat')
                    self.now += 3
                    return b'%'
                req = replace(self.yeu_cau(), luong=Mock(read1=Mock(side_effect=doc)))
                self.assertEqual(self.tao_dich_vu(toi_da_giay=5).xu_ly(req).ma_http, 504)
                self.assertLessEqual(req.luong.read1.call_count, 2)
        self.backend.doc_pdf.assert_not_called()

    def test_deadline_duoc_truyen_va_kiem_sau_ket_qua(self):
        for hop_tac in (False, True):
            self.now = 0
            def nhan(*args, huy, toi_da_byte_ra, ma_tuong_quan):
                self.assertEqual(toi_da_byte_ra, self.c.toi_da_byte_ra)
                self.assertEqual(ma_tuong_quan, str(UUID(int=1)))
                self.now = 6
                if hop_tac:
                    huy.is_set()
                return PDF_RA
            self.backend.doc_pdf.side_effect = nhan
            dv = self.tao_dich_vu(toi_da_giay=5)
            self.assertEqual(dv.xu_ly(self.yeu_cau()).ma_http, 504)
            self.assertEqual(dv.xu_ly(self.yeu_cau()).ma_http, 409)
            self.assertFalse(dv._xu_ly.locked())
            self.assertEqual(dv._dang_nhan, 0)

    def test_deadline_kep_nhip_cho_hot_folder_khong_tao_luong_moi(self):
        han = cn._HetHan(5, lambda: self.now)
        self.now = 4
        def nghi(giay):
            self.now += giay
        with patch.object(cn.time, 'sleep', side_effect=nghi) as sleep:
            with self.assertRaises(TimeoutError):
                han.wait(60)
        sleep.assert_called_once_with(1)

    def test_pdf_tra_ve_sai_hoac_qua_co_khong_thanh_cong_gia(self):
        for raw in (b'DOCX', PDF_RA[:-5], PDF_RA + b' ' * 100):
            self.backend.doc_pdf.return_value = raw
            self.assertEqual(self.tao_dich_vu(toi_da_byte_ra=len(PDF_RA)).xu_ly(self.yeu_cau()).ma_http, 502)

    def test_timeout_native_hot_folder_va_loi_doc_body_duoc_lam_sach(self):
        self.backend.doc_pdf.side_effect = DataError('OCR_QUA_GIO', 'D:\\DEMO\\nhay-cam.pdf')
        ph = self.dv.xu_ly(self.yeu_cau())
        self.assertEqual(ph.ma_http, 504)
        self.assertNotIn(b'DEMO', ph.noi_dung)
        req = replace(self.yeu_cau(ma=2), luong=Mock(read1=Mock(side_effect=OSError(KHOA.decode()))))
        self.assertEqual(self.dv.xu_ly(req).ma_http, 502)
        self.assertEqual(self.backend.doc_pdf.call_count, 1)

    def test_log_va_phan_hoi_khong_lo_khoa_duong_dan_header_exception(self):
        bi_mat = 'D:\\DEMO\\ho-so-nhay-cam.pdf'
        self.backend.doc_pdf.side_effect = RuntimeError(bi_mat + KHOA.decode())
        req = self.yeu_cau(headers={'X-Demo': bi_mat, 'Content-Disposition': bi_mat})
        with patch.object(cn.logging, 'getLogger') as logger:
            self.dv._ghi_log = self.dv._log
            ph = self.dv.xu_ly(req)
        raw_log = logger.return_value.info.call_args.args[0]
        record = json.loads(raw_log)
        self.assertEqual(set(record), {'ma_tuong_quan', 'ket_qua', 'thoi_gian_giay', 'so_trang'})
        self.assertEqual(record['ma_tuong_quan'], ph.ma_tuong_quan)
        self.assertEqual(record['ma_tuong_quan'], req.headers['X-Request-ID'])
        self.assertIsNone(record['so_trang'])
        for raw in (raw_log, ph.noi_dung.decode(), repr(self.c), repr(req), repr(ph)):
            self.assertNotIn(bi_mat, raw)
            self.assertNotIn(KHOA.decode(), raw)
            self.assertNotIn('RuntimeError', raw)
        self.assertEqual(ph.ma_http, 502)
        self.assertEqual(self.dv.xu_ly(self.yeu_cau()).ma_http, 409)

    def test_loi_noi_nhan_log_khong_gui_lai_hoac_lam_hong_ket_qua(self):
        self.dv._ghi_log = Mock(side_effect=RuntimeError('DEMO log loi'))
        self.assertEqual(self.dv.xu_ly(self.yeu_cau()).ma_http, 200)
        self.assertEqual(self.backend.doc_pdf.call_count, 1)

    def test_mac_dinh_tat_va_import_khong_bind_doc_cau_hinh(self):
        with patch.object(cn, '_MayChuHTTPS') as server:
            self.assertIsNone(cn.chay(cn.CauHinhCauNoi()))
            self.assertEqual(cn.CauNoiABBYY().xu_ly(self.yeu_cau()).ma_http, 503)
            server.assert_not_called()
        importlib.reload(cn)
        for guard in self.chan:
            guard.assert_not_called()

    def test_chi_chay_moi_bind_va_dung_adapter_hot_folder(self):
        tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)  # Không nạp chứng thư/tệp.
        c = replace(self.c, tls=tls, thu_muc_hot_folder='DEMO-hot-folder')
        with patch.object(cn, 'HotFolderPDF', return_value=self.backend) as adapter:
            with patch.object(cn, '_MayChuHTTPS') as server:
                cn.chay(c)
        adapter.assert_called_once_with('DEMO-hot-folder', bat=True, cho_toi_da=c.toi_da_giay)
        server.return_value.serve_forever.assert_called_once_with()
        server.return_value.server_close.assert_called_once_with()

    def test_khong_bind_khi_thieu_tls_sai_tls_hoac_cau_hinh(self):
        for c in (self.c, replace(self.c, tls=ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)),
                  replace(self.c, khoa=b''), replace(self.c, ip_core=('192.0.2.0/24',)),
                  replace(self.c, bat=1), replace(self.c, toi_da_cho=-1),
                  replace(self.c, toi_da_giay=float('nan')), replace(self.c, toi_da_byte=0)):
            with self.subTest(cau_hinh=c):
                with patch.object(cn, '_MayChuHTTPS') as server:
                    with self.assertRaises(ValueError):
                        cn.chay(c)
                    server.assert_not_called()

    def test_tls_1_1_bi_tu_choi_truoc_khi_tao_adapter_va_bind(self):
        tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            tls.minimum_version = ssl.TLSVersion.TLSv1_1
        with patch.object(cn, 'HotFolderPDF') as adapter, \
                patch.object(cn, '_MayChuHTTPS') as server:
            with self.assertRaises(ValueError):
                cn.chay(replace(self.c, tls=tls))
        adapter.assert_not_called()
        server.assert_not_called()

    def test_sai_route_phuong_thuc_khong_gui_abbyy(self):
        for kw in ({'duong_dan': '/ocr/pdf?khoa=' + KHOA.decode()}, {'phuong_thuc': 'GET'}):
            ph = self.dv.xu_ly(self.yeu_cau(**kw))
            self.assertEqual(ph.ma_http, 404)
            self.assertNotIn(KHOA.decode(), ph.noi_dung.decode())
        self.backend.doc_pdf.assert_not_called()

    def test_http_tat_access_log_va_loi_parser_khong_phan_chieu_du_lieu(self):
        handler = cn._XuLyHTTP.__new__(cn._XuLyHTTP)
        handler.wfile = io.BytesIO()
        handler.send_response_only, handler.send_header, handler.end_headers = Mock(), Mock(), Mock()
        with patch.object(cn.logging, 'getLogger') as logger:
            handler.log_message('%s', KHOA.decode())
            handler.log_error('%s', 'D:\\DEMO\\ho-so.pdf')
            handler.send_error(400, KHOA.decode(), 'D:\\DEMO\\ho-so.pdf')
            cn._MayChuHTTPS.handle_error(None, None, None)
        logger.assert_not_called()
        self.assertNotIn(KHOA, handler.wfile.getvalue())
        self.assertNotIn(b'DEMO', handler.wfile.getvalue())

    def test_http_truyen_socket_that_va_dong_ket_noi_khong_gui_header_goc(self):
        req = self.yeu_cau()
        handler = cn._XuLyHTTP.__new__(cn._XuLyHTTP)
        handler.connection, handler.headers, handler.rfile = req.ket_noi, req.headers, req.luong
        handler.command, handler.path, handler.wfile = 'POST', '/ocr/pdf', io.BytesIO()
        handler.server = SimpleNamespace(cau_noi=self.dv)
        handler.send_response_only, handler.send_header, handler.end_headers = Mock(), Mock(), Mock()
        handler.do_POST()
        self.assertEqual(handler.wfile.getvalue(), PDF_RA)
        self.assertTrue(handler.close_connection)
        req.ket_noi.getpeername.assert_called_once()
        self.assertNotIn(KHOA.decode(), repr(handler.send_header.call_args_list))

    def test_http_parser_that_voi_socket_gia_tra_pdf_va_chan_url_loi(self):
        for dung in (True, False):
            with self.subTest(dung=dung):
                req = self.yeu_cau()
                if dung:
                    raw = ('POST /ocr/pdf HTTP/1.1\r\n' + ''.join(
                        k + ': ' + v + '\r\n' for k, v in req.headers.items())
                        + '\r\n').encode() + PDF
                else:
                    raw = b'GET /' + KHOA + b' HTTP/1.1\r\n\r\n'
                req.ket_noi.makefile.return_value = io.BytesIO(raw)
                ra = bytearray()
                req.ket_noi.sendall.side_effect = ra.extend
                cn._XuLyHTTP(req.ket_noi, (IP_CORE, 1), SimpleNamespace(cau_noi=self.dv))
                self.assertNotIn(KHOA, ra)
                if dung:
                    self.assertIn(b'200', ra.split(b'\r\n')[0])
                    self.assertTrue(ra.endswith(PDF_RA))
                else:
                    self.assertIn(b'501', ra.split(b'\r\n')[0])

    def test_doc_header_co_deadline_va_giu_nguyen_body_da_dem(self):
        req = self.yeu_cau()
        luong = cn._DocHTTP(io.BytesIO(b'DEMO: 1\r\n\r\n' + PDF), req.ket_noi,
                            cn._HetHan(5, lambda: self.now))
        self.assertEqual(luong.readline(65537), b'DEMO: 1\r\n')
        self.assertEqual(luong.readline(65537), b'\r\n')
        self.assertEqual(luong.read1(8) + luong.read1(100), PDF)
        self.assertEqual(luong.read1(100), b'')
        luong.close()
        self.assertTrue(luong.luong.closed)

    def test_header_nho_giot_van_het_han_khong_keo_dai_vo_han(self):
        def doc(n):
            self.now += 3
            return b'x'
        raw = Mock(read1=Mock(side_effect=doc))
        luong = cn._DocHTTP(raw, Mock(), cn._HetHan(5, lambda: self.now))
        with self.assertRaises(TimeoutError):
            luong.readline(65537)
        self.assertEqual(raw.read1.call_count, 2)

    def test_header_gioi_han_do_dai_va_eof(self):
        luong = cn._DocHTTP(io.BytesIO(b'123456\n'), Mock(), cn._HetHan(5, lambda: self.now))
        self.assertEqual(luong.readline(4), b'1234')
        self.assertEqual(luong.readline(4), b'56\n')
        self.assertEqual(luong.readline(4), b'')

    def test_server_gioi_han_luong_va_tls_khong_socket_that(self):
        tls = Mock()
        dv = self.tao_dich_vu(tls=tls, toi_da_ket_noi=1)
        with patch.object(cn.ThreadingHTTPServer, '__init__'):
            server = cn._MayChuHTTPS(dv)
        server.shutdown_request = Mock()
        with patch.object(cn.ThreadingHTTPServer, 'process_request') as process:
            server.process_request(Mock(), ('192.0.2.10', 1))
            server.process_request(Mock(), ('192.0.2.10', 2))
            self.assertEqual(process.call_count, 1)
            server.shutdown_request.assert_called_once()
        with patch.object(cn.ThreadingHTTPServer, 'process_request_thread'):
            server.process_request_thread(Mock(), (IP_CORE, 1))
        self.assertTrue(server._ket_noi.acquire(blocking=False))
        peer = Mock()
        peer.getpeername.return_value = (IP_CORE, 1)
        with patch.object(cn.ThreadingHTTPServer, 'get_request', return_value=(peer, (IP_CORE, 1))):
            self.assertEqual(server.get_request()[0], tls.wrap_socket.return_value)
        peer.settimeout.assert_called_once_with(self.c.doc_giay)
        tls.wrap_socket.assert_called_once_with(peer, server_side=True)

    def test_ip_sai_chan_truoc_tls_va_loi_tls_khong_lo_exception(self):
        tls = Mock()
        dv = self.tao_dich_vu(tls=tls)
        with patch.object(cn.ThreadingHTTPServer, '__init__'):
            server = cn._MayChuHTTPS(dv)
        for ip in ('192.0.2.99', IP_CORE):
            peer = Mock()
            peer.getpeername.return_value = (ip, 1)
            tls.wrap_socket.side_effect = RuntimeError(KHOA.decode())
            with patch.object(cn.ThreadingHTTPServer, 'get_request', return_value=(peer, (ip, 1))):
                with self.assertRaises(OSError) as err:
                    server.get_request()
            self.assertNotIn(KHOA.decode(), str(err.exception))
            peer.close.assert_called_once()
        tls.wrap_socket.assert_called_once()

    def test_loi_tao_luong_tra_slot_va_loi_server_van_dong(self):
        dv = self.tao_dich_vu(toi_da_ket_noi=1)
        with patch.object(cn.ThreadingHTTPServer, '__init__'):
            server = cn._MayChuHTTPS(dv)
        with patch.object(cn.ThreadingHTTPServer, 'process_request', side_effect=RuntimeError('DEMO')):
            with self.assertRaises(RuntimeError):
                server.process_request(Mock(), (IP_CORE, 1))
        self.assertTrue(server._ket_noi.acquire(blocking=False))
        tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        with patch.object(cn, 'HotFolderPDF', return_value=self.backend):
            with patch.object(cn, '_MayChuHTTPS') as mock_server:
                mock_server.return_value.serve_forever.side_effect = KeyboardInterrupt
                with self.assertRaises(KeyboardInterrupt):
                    cn.chay(replace(self.c, tls=tls))
        mock_server.return_value.server_close.assert_called_once()


class MaTuongQuanHotFolderTests(unittest.TestCase):
    """Dùng lại hệ tệp/đồng hồ RAM; mọi chốt Core đều qua SDK giả."""

    def setUp(self):
        self.giu_trang_that = ocr.CongOCR._giu_trang
        self.fx = hf.HotFolderPDFTests()
        self.fx.setUp()
        self.addCleanup(self.fx.doCleanups)
        self.fs, self.backend = self.fx.fs, self.fx.backend
        self.ma, self.khac = 'ocr:0123456789abcdef0123456789abcdef', 'ocr:fedcba9876543210fedcba9876543210'
        self.ten_ma, self.ten_khac = 'ocr_0123456789abcdef0123456789abcdef', 'ocr_fedcba9876543210fedcba9876543210'
        self.logs = []
        self.c = cn.CauHinhCauNoi(bat=True, khoa=KHOA, ip_core=(IP_CORE,))
        self.dv = self.tao_cau()

    def tao_cau(self):
        return cn.CauNoiABBYY(self.c, hot_folder=self.backend,
                             ghi_log=self.logs.append, dong_ho=lambda: self.fs.now)

    def yeu_cau(self, ma=None):
        ket_noi = Mock()
        ket_noi.getpeername.return_value = (IP_CORE, 12345)
        return cn.YeuCau(ket_noi, {
            'Authorization': 'Bearer ' + KHOA.decode('ascii'),
            'Content-Length': str(len(self.fx.raw)), 'Content-Type': 'application/pdf',
            'X-Request-ID': self.ma if ma is None else ma,
        }, io.BytesIO(self.fx.raw))

    def tra_ket_qua(self, raw=None):
        def nhan(vao):
            self.fs.files.pop(vao)
            if raw is not None:
                self.fs.put(self.fs.d['out'] / (vao.stem + '.pdf'), raw)
        self.fs.sau_gui = nhan

    def test_cung_ma_core_xuyen_cau_ten_tep_phan_hoi_va_log(self):
        self.tra_ket_qua(self.fx.pdf)
        with patch.object(ocr, '_ma_moi', side_effect=AssertionError('Không sinh mã mới')):
            ph = self.dv.xu_ly(self.yeu_cau())
        self.assertEqual(ph.ma_http, 200)
        self.assertEqual((ph.ma_tuong_quan, ph.noi_dung), (self.ma, self.fx.pdf))
        self.assertEqual(self.fs.sent, [(self.fs.d['in'] / (self.ten_ma + '.pdf'), self.fx.raw)])
        self.assertIn((self.fs.d['out'] / (self.ten_ma + '.pdf'),
                       self.fs.d['nhan'] / (self.ten_ma + '.pdf')), self.fs.moves)
        for _, tep in self.fs.moves:
            self.assertFalse(any(c in tep.name for c in ':\\/'))
        self.assertEqual(self.logs[0]['ma_tuong_quan'], self.ma)
        # Kết quả đã nhận giữ bằng chứng theo mã, không bị lịch dọn cũ xóa.
        self.assertIn(self.fs.d['nhan'] / (self.ten_ma + '.pdf'), self.fs.files)

    def test_ma_hd_va_uuid_cu_van_qua_cau_va_hot_folder(self):
        self.tra_ket_qua(self.fx.pdf)
        for ma in (hf.MA, str(UUID(int=3)), '12345678-9ABC-DEF0-1234-56789ABCDEF0'):
            with self.subTest(ma=ma):
                ph = self.tao_cau().xu_ly(self.yeu_cau(ma))
                ma_chuan = ma if ma.startswith('hd') else str(UUID(ma))
                self.assertEqual((ph.ma_http, ph.ma_tuong_quan), (200, ma_chuan))
                self.assertEqual(self.fs.sent[-1][0], self.fs.d['in'] / (ma_chuan + '.pdf'))

    def test_khong_co_ma_giu_nguyen_seam_cu(self):
        self.fx.tra_ket_qua(self.fx.pdf)
        self.assertEqual(self.backend.doc_pdf(self.fx.raw), self.fx.pdf)
        self.assertEqual(self.fs.sent[0][0].stem, hf.MA)
        self.assertEqual(self.fs.files, {})

    def test_ma_sai_bi_chan_truoc_khi_cham_he_tep(self):
        for ma in ('../DEMO.pdf', '', 'f' * 64, 1, UUID(int=1), self.ten_ma,
                   'ocr:' + 'a' * 31, 'ocr:' + 'a' * 33, 'ocr:' + 'g' * 32,
                   'ocr:' + 'A' * 32, self.ma + '\n', self.ma + '/x', self.ma + '\\x'):
            with self.subTest(ma=repr(ma)):
                with self.assertRaises(DataError) as bat:
                    self.backend.doc_pdf(self.fx.raw, ma_tuong_quan=ma)
                self.assertEqual(bat.exception.code, 'OCR_MA_YEU_CAU')
                req = self.yeu_cau(ma)
                self.assertEqual(self.dv.xu_ly(req).ma_http, 400)
                self.assertEqual(req.luong.tell(), 0)
        self.assertEqual(self.fs.calls, [])
        self.assertEqual(self.fs.sent, [])

    def test_header_ma_core_trung_bi_chan_truoc_doc_body_va_hot_folder(self):
        for ma in (self.ma, self.ten_ma, self.khac):
            with self.subTest(ma_trung=ma):
                req = self.yeu_cau()
                headers = Message()
                for k, v in req.headers.items():
                    headers[k] = v
                headers['x-request-id'] = ma
                ph = self.dv.xu_ly(replace(req, headers=headers))
                self.assertEqual((ph.ma_http, ph.ma_tuong_quan), (400, ''))
                self.assertEqual(req.luong.tell(), 0)
                self.assertEqual(self.dv._ma_da_nhan, set())
        self.assertEqual(self.fs.calls, [])
        self.assertEqual(self.fs.sent, [])

    def test_ket_qua_khac_ma_va_ten_gan_giong_khong_duoc_ghep(self):
        sai = [self.fs.d['out'] / (ten + '.pdf') for ten in (
            self.ten_khac, self.ten_ma + '0', self.ten_ma + '.khac',
            'ocr_' + 'a' * 31, 'ocr_' + 'a' * 33, 'ocr_' + 'g' * 32,
            'ocr_' + 'a' * 31 + '-', 'ocr_' + 'A' * 32)]
        def nhan(vao):
            self.fs.files.pop(vao)
            for tep in sai:
                self.fs.put(tep, PDF_RA)
        self.fs.sau_gui = nhan
        def xuat_dung():
            if self.fs.now >= 0.3:
                self.fs.sau_nghi = None
                self.fs.put(self.fs.d['out'] / (self.ten_ma + '.pdf'), self.fx.pdf)
        self.fs.sau_nghi = xuat_dung
        with patch.object(ocr._LOG, 'warning'):
            self.assertEqual(self.backend.doc_pdf(self.fx.raw, ma_tuong_quan=self.ma), self.fx.pdf)
        self.assertGreaterEqual(self.fs.now, 0.3)
        for tep in sai:
            self.assertEqual(self.fs.files[tep][0], PDF_RA)
            self.assertNotIn(('read', tep), self.fs.calls)

    def test_log_loi_ma_khac_khong_anh_huong_luot_hien_tai(self):
        ten_sai = (self.ten_khac, 'ocr_' + 'a' * 31, 'ocr_' + 'a' * 33, 'ocr_' + 'g' * 32)
        for ten in ten_sai:
            self.fs.put(self.fs.d['out'] / (ten + '.log'),
                        (self.ten_ma + '.pdf ERROR DEMO kín').encode('utf-8'))
        self.assertFalse(self.backend._loi_abbyy(self.fs.d['out'], self.ma))
        for ten in ten_sai:
            self.assertNotIn(('read', self.fs.d['out'] / (ten + '.log')), self.fs.calls)
        self.fs.put(self.fs.d['out'] / (self.ten_ma + '.log'),
                    (self.ten_ma + '.pdf ERROR DEMO').encode('utf-8'))
        self.assertTrue(self.backend._loi_abbyy(self.fs.d['out'], self.ma))

    def phan_hoi_voi_log_chung(self, dong):
        self.fs.files.clear()
        self.fs.put(self.fs.d['out'] / 'abbyy.log', dong.encode('utf-8'))
        self.tra_ket_qua(self.fx.pdf)
        return self.tao_cau().xu_ly(self.yeu_cau())

    def test_log_chung_ten_dai_hon_mot_ky_tu_van_nhan_pdf_dung(self):
        ph = self.phan_hoi_voi_log_chung(self.ten_ma + '0.pdf ERROR DEMO')
        self.assertEqual(ph.ma_http, 200)
        self.assertEqual((ph.ma_tuong_quan, ph.noi_dung), (self.ma, self.fx.pdf))

    def test_log_chung_ten_them_tien_to_hau_to_khong_chan_pdf_dung(self):
        for ten in ('x' + self.ten_ma + '.pdf', self.ten_ma + '0.pdf',
                    self.ten_ma + '.pdf0', self.ten_ma + '.pdf.bak',
                    self.ten_ma + '.khac.pdf', self.ten_ma + '_khac.pdf',
                    self.ten_ma + '-khac.pdf', self.ma + '.pdf', self.ten_ma):
            with self.subTest(ten=ten):
                ph = self.phan_hoi_voi_log_chung('ERROR "D:\\DEMO\\' + ten + '"')
                self.assertEqual((ph.ma_http, ph.noi_dung), (200, self.fx.pdf))

    def test_log_chung_dung_ten_pdf_va_loi_van_tra_loi_qua_cau(self):
        for mau in ('{} ERROR', 'ERROR {}', '\t{}\tERROR',
                    'ERROR "D:\\DEMO\\ho so\\{}"', "ERROR '/DEMO/ho so/{}'",
                    'ERROR [{}]', 'ERROR tep={};', 'ERROR ({})'):
            with self.subTest(mau=mau):
                dong = mau.format(self.ten_ma + '.pdf')
                ph = self.phan_hoi_voi_log_chung(dong)
                self.assertEqual(ph.ma_http, 502)
                self.assertEqual(ph.ma_tuong_quan, self.ma)
                self.assertTrue(self.backend._loi_abbyy(self.fs.d['out'], self.ma))

    def test_log_chung_chi_so_ten_day_du_cho_ca_ma_hd_uuid_cu(self):
        for ma in (hf.MA, str(UUID(int=3)), self.ma):
            ten = ocr.ten_tep_tuong_quan(ma)
            for ten_log, co_loi in ((ten + '0.pdf', False), ('x' + ten + '.pdf', False),
                                    (ten + '.pdf.bak', False), (ten + '.pdf', True)):
                with self.subTest(ma=ma, ten_log=ten_log):
                    self.fs.files.clear()
                    self.fs.put(self.fs.d['out'] / 'abbyy.log', (ten_log + ' ERROR').encode())
                    self.assertEqual(self.backend._loi_abbyy(self.fs.d['out'], ma), co_loi)

    def test_log_dung_ten_anh_dau_vao_van_bao_loi_abbyy(self):
        for duoi in ('png', 'jpg', 'jpeg', 'tif', 'tiff'):
            with self.subTest(duoi=duoi):
                self.fs.files.clear()
                self.fs.put(self.fs.d['out'] / 'abbyy.log',
                            (self.ten_ma + '.' + duoi + ' ERROR').encode())
                self.tra_ket_qua(self.fx.pdf)
                with self.assertRaises(DataError) as bat:
                    self.backend.doc_pdf(b'DEMO anh', duoi, ma_tuong_quan=self.ma)
                self.assertEqual(bat.exception.code, 'OCR_LOI_ABBYY')
                self.assertEqual(self.fs.sent[-1][0].name, self.ten_ma + '.' + duoi)

    def test_mutation_so_chuoi_con_bi_ca_log_ten_dai_hon_bat(self):
        def so_chuoi_con(thu_muc, ma, *args):
            dong = self.fs.read(thu_muc / 'abbyy.log').decode().lower()
            return (ma in dong or ocr.ten_tep_tuong_quan(ma) in dong) and 'error' in dong

        with patch.object(ocr._VanChuyenHotFolder, '_loi_abbyy', staticmethod(so_chuoi_con)), \
                self.assertRaisesRegex(AssertionError, '502 != 200'):
            self.test_log_chung_ten_dai_hon_mot_ky_tu_van_nhan_pdf_dung()

    def test_qua_gio_ket_qua_muon_chi_ghi_nhat_ky_giu_bang_chung(self):
        self.tra_ket_qua()
        self.assertEqual(self.dv.xu_ly(self.yeu_cau()).ma_http, 504)
        muon, khac = (self.fs.d['out'] / (ten + '.pdf') for ten in (self.ten_ma, self.ten_khac))
        kin = b'DEMO noi dung kin D:\\DEMO\\ho-so.pdf bam:' + b'f' * 64
        self.fs.put(muon, kin)
        self.fs.put(khac, PDF_RA)
        callback = self.fx.timer.call_args.args[1]
        with self.assertLogs(ocr.__name__, level='WARNING') as logs:
            callback()
        record = json.loads(logs.records[0].getMessage())
        self.assertEqual(record, dict(ma_tuong_quan=self.ma, ket_qua='kết quả muộn'))
        self.assertEqual(self.fs.files[muon][0], kin)
        self.assertEqual(self.fs.files[khac][0], PDF_RA)
        self.assertNotIn(('read', muon), self.fs.calls)
        self.assertEqual(self.dv.xu_ly(self.yeu_cau()).ma_http, 409)
        self.assertEqual(len(self.fs.sent), 1)

    def test_khoi_dong_lai_gap_ket_qua_cu_khong_gui_lai_hoac_nhan_nham(self):
        for noi in ('out', 'nhan', 'in', 'tam'):
            with self.subTest(noi=noi):
                self.fs.files.clear()
                tep = self.fs.d[noi] / (self.ten_ma + '.pdf')
                self.fs.put(tep, PDF_RA)
                backend = self.fx.tao_backend()
                with patch.object(ocr._LOG, 'warning'), patch.object(ocr, '_ma_moi',
                        side_effect=AssertionError('Không sinh mã sau restart')):
                    self.assertIsNot(backend, self.backend)
                    dv = cn.CauNoiABBYY(self.c, hot_folder=backend, ghi_log=self.logs.append,
                                       dong_ho=lambda: self.fs.now)
                    self.assertEqual(dv.xu_ly(self.yeu_cau()).ma_http, 502)
                self.assertEqual(self.fs.files[tep][0], PDF_RA)
                self.assertEqual(self.fs.sent, [])

    def test_huy_sau_doi_ten_nhan_ghi_muon_va_giu_bang_chung(self):
        self.tra_ket_qua(self.fx.pdf)
        nhan = self.fs.d['nhan'] / (self.ten_ma + '.pdf')
        self.fs.sau_doi = lambda src, dst: self.fx.huy.set() if dst == nhan else None
        with self.assertLogs(ocr.__name__, level='WARNING') as logs, self.assertRaises(DataError) as bat:
            self.backend.doc_pdf(self.fx.raw, huy=self.fx.huy, ma_tuong_quan=self.ma)
        self.assertEqual(bat.exception.code, 'OCR_HUY')
        self.assertTrue(bat.exception.chua_ro_da_nhan)
        self.assertEqual(self.fs.files[nhan][0], self.fx.pdf)
        self.assertEqual(json.loads(logs.records[0].getMessage()),
                         dict(ma_tuong_quan=self.ma, ket_qua='kết quả muộn'))

    def test_quet_sau_khoi_dong_lai_ghi_muon_khong_doc_noi_dung(self):
        tep = self.fs.d['out'] / (self.ten_khac + '.pdf')
        self.fs.put(tep, b'DEMO kin')
        self.tra_ket_qua(self.fx.pdf)
        with self.assertLogs(ocr.__name__, level='WARNING') as logs:
            self.assertEqual(self.dv.xu_ly(self.yeu_cau()).ma_http, 200)
        self.assertEqual(json.loads(logs.records[0].getMessage()),
                         dict(ma_tuong_quan=self.khac, ket_qua='kết quả muộn'))
        self.assertNotIn(('read', tep), self.fs.calls)

    def test_quet_bo_qua_ten_la_gia_mao_khong_doc_noi_dung(self):
        ten_sai = ('ocr_' + 'a' * 31, 'ocr_' + 'a' * 33, 'ocr_' + 'g' * 32,
                   'ocr_' + 'a' * 31 + '-', 'ocr_' + 'A' * 32,
                   self.ten_khac + '.khac', self.ten_khac + '_khac', 'DEMO')
        for ten in ten_sai:
            self.fs.put(self.fs.d['out'] / (ten + '.pdf'), 'DEMO kín'.encode('utf-8'))
        self.tra_ket_qua(self.fx.pdf)
        with patch.object(ocr._LOG, 'warning') as log:
            self.assertEqual(self.dv.xu_ly(self.yeu_cau()).ma_http, 200)
        log.assert_not_called()
        for ten in ten_sai:
            tep = self.fs.d['out'] / (ten + '.pdf')
            self.assertEqual(self.fs.files[tep][0], 'DEMO kín'.encode('utf-8'))
            self.assertNotIn(('read', tep), self.fs.calls)

    def test_mutation_regex_cu_bi_ca_ma_core_bat(self):
        cu = re.compile(r'^(hd\d{14}_[0-9a-f]{6}|[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})(?:\.|$)')
        with patch.object(ocr, '_MA_RE', cu), self.assertRaisesRegex(AssertionError, '400 != 200'):
            self.test_cung_ma_core_xuyen_cau_ten_tep_phan_hoi_va_log()

    def test_tran_ket_qua_van_duoc_kiem_tren_ten_ma_core(self):
        self.tra_ket_qua(b'%PDF-1.4\n' + b'x' * 100 + b'\n%%EOF')
        dv = cn.CauNoiABBYY(replace(self.c, toi_da_byte_ra=32), hot_folder=self.backend,
                           ghi_log=self.logs.append, dong_ho=lambda: self.fs.now)
        self.assertEqual(dv.xu_ly(self.yeu_cau()).ma_http, 502)
        self.assertEqual(self.fs.reads, [])
        self.assertEqual(dv.xu_ly(self.yeu_cau()).ma_http, 409)
        self.assertEqual(len(self.fs.sent), 1)

    def test_so_trang_cau_hot_folder_va_chot_cas_cung_ma_core_khong_chot_lai(self):
        sdk = Mock(spec=SDKEngine)
        sdk.ocr_doc_luot.return_value = dict(trang_thai='khong_co')
        sdk.ocr_giu_luot.return_value = dict(
            ma_tuong_quan=self.ma, trang_thai='dang_giu', phien_ban=7)
        sdk.ocr_chot_luot.return_value = dict(trang_thai='da_tieu')
        cong = self.fx.tao_cong_docx()
        rows = []
        def ghi_so(ds, **kw):
            rows[:] = [x[:] for x in ds]
        tls = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        client = KetNoiABBYY(CauHinhKetNoi(
            bat=True, may_chu='abbyy.demo.invalid', khoa=KHOA, tls=tls))
        sock, raw_gui = Mock(), bytearray()
        sock.sendall.side_effect = raw_gui.extend
        def qua_cau(*args, **kwargs):
            self.assertEqual(rows[0][2], self.ma)
            self.assertIn(b'X-Request-ID: ' + self.ma.encode('ascii') + b'\r\n', raw_gui)
            return phan_hoi_tu_cau(self.dv, bytes(raw_gui))
        sock.makefile.side_effect = qua_cau
        self.tra_ket_qua(self.fx.pdf)
        with patch.object(cong, '_doc_so', side_effect=lambda: [x[:] for x in rows]), \
                patch.object(cong, '_ghi_so', side_effect=ghi_so), \
                patch.object(cong, '_giu_trang', side_effect=lambda *a, **kw:
                             self.giu_trang_that(cong, *a, **kw)), \
                patch('http.client.HTTPSConnection', HTTPS_THAT), \
                patch('socket.create_connection', return_value=sock), \
                patch.object(tls, 'wrap_socket', return_value=sock), \
                patch.object(chon, '_dem_trang', return_value=('pdf', 1)), \
                patch.object(chon, '_LUOT_CHO', {}), patch.object(chon, '_LUOT_XONG', OrderedDict()):
            selector = chon.ChonNguonOCR(abbyy=abbyy.BackendKetNoiABBYY(ket_noi=client),
                                        cong_ocr=cong, sdk=sdk, mask_ocr=Mock())
            self.assertEqual(selector.doc(self.fx.raw, 'pdf').nguon_doc, 'ABBYY')
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][1:], [1, self.ma])
            self.assertEqual(self.dv._ma_da_nhan, {self.ma})
            self.assertEqual(self.logs[0]['ma_tuong_quan'], self.ma)
            self.assertEqual(self.fs.sent, [(self.fs.d['in'] / (self.ten_ma + '.pdf'), self.fx.raw)])
            sdk.ocr_chot_luot.assert_called_once_with(
                ma_tuong_quan=self.ma, ket_qua='da_tieu', phien_ban=7)
            # Admin/Core đã chốt; PDF xuất thêm chỉ thành bằng chứng muộn.
            sdk.ocr_doc_luot.return_value = dict(trang_thai='da_tieu', phien_ban=8)
            self.fs.put(self.fs.d['out'] / (self.ten_ma + '.pdf'), self.fx.pdf)
            with self.assertLogs(ocr.__name__, level='WARNING'):
                self.fx.timer.call_args.args[1]()
            with self.assertRaises(DataError) as bat:
                selector.doc(self.fx.raw, 'pdf')
            self.assertEqual(bat.exception.code, 'OCR_DA_XU_LY')
            self.assertEqual(sdk.ocr_chot_luot.call_count, 1)
            self.assertEqual(len(self.fs.sent), 1)
            self.assertEqual(len(rows), 1)


if __name__ == '__main__':
    unittest.main()
