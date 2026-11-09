"""Chỉ két/tiến trình/HTTPS giả; giữ tệp thử trong var/tmp-test, không xóa.

Không đọc cấu hình/két thật, không socket, không ABBYY hay PostgreSQL.
"""

from contextlib import ExitStack, redirect_stderr, redirect_stdout
from ctypes import wintypes
import io
import json
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from tools import abbyy_ket_noi_tam as a


CANARY = 'DEMO_BI_MAT_KET_NOI_TAM_' + 'X' * 42


class KetGia:
    """Chỉ lưu dấu không chứa khóa; bytes thật giữ trong RAM test."""

    def __init__(self, folder):
        self.folder, self.khoa, self.da_thu = Path(folder), {}, []

    def luu(self, ten, khoa):
        self.khoa[ten] = khoa.lay_de_truyen()
        (self.folder / (ten + '.dpapi')).write_bytes(b'DEMO_DPAPI_KHONG_CHUA_KHOA')

    def thu_hoi(self, ten):
        self.da_thu.append(ten)
        self.khoa.pop(ten, None)
        tep = self.folder / (ten + '.dpapi')
        tep.rename(tep.with_name(tep.name + '.thu-hoi-DEMO'))


class KetNoiTamTests(unittest.TestCase):
    def setUp(self):
        self.root = a.GOC / 'var' / 'tmp-test' / ('abbyy-tam-' + uuid4().hex)
        self.root.mkdir(parents=True)
        self.ket_root = self.root / 'ket-gia'
        self.ket_root.mkdir()
        self.tep = self.root / 'abbyy-ket-noi-tam.json'
        self.ket = KetGia(self.ket_root)
        self.ket_factory = Mock(return_value=self.ket)
        self.tt = Mock()
        self.tt.danh_tinh.return_value = '123456789'
        self.p = Mock(pid=43210)
        self.p.stdin = io.BytesIO()
        self.p.stdout = io.BytesIO(b'SAN_SANG\n')
        self.args = SimpleNamespace(ip_core='192.168.1.20', dia_chi='127.0.0.1', cong=9443,
                                    gio=8, ket=str(self.ket_root), chung_thu='DEMO-cert',
                                    khoa_tls='DEMO-tls', hot_folder=str(self.root / 'hot-khong-ton-tai'))
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(a, '_kiem_ket', return_value=self.ket_root))
        self.tls = self.stack.enter_context(patch.object(a, '_tls'))
        self.stack.enter_context(patch.object(a, '_nhat_ky'))
        self.stack.enter_context(patch.object(a.kenh_bi_mat, 'dat_acl'))
        self.stack.enter_context(patch.object(a.kenh_bi_mat, 'kiem_acl', return_value=True))
        self.sinh_khoa = self.stack.enter_context(
            patch.object(a.secrets, 'token_urlsafe', return_value=CANARY))
        self.tao = self.stack.enter_context(patch.object(a, '_tao_tien_trinh', return_value=self.p))
        self.cap = self.stack.enter_context(patch.object(a, '_cap_cho_con'))

    def mo(self):
        return a.mo(self.args, tep=self.tep, ket_factory=self.ket_factory, tien_trinh=self.tt)

    def dong(self):
        return a.dong(tep=self.tep, ket_factory=self.ket_factory, tien_trinh=self.tt)

    def test_chay_kho_ca_ba_lenh_khong_doc_ghi_ket_tien_trinh(self):
        with patch.object(Path, 'open', side_effect=AssertionError('Không I/O')), \
                patch.object(a, 'mo') as mo, patch.object(a, 'dong') as dong, \
                patch.object(a, 'trang_thai') as trang, redirect_stdout(io.StringIO()) as out:
            for lenh in ('mo', 'dong', 'trang-thai'):
                self.assertEqual(a.main([lenh, '--chay-kho']), 0)
        for ham in (mo, dong, trang, self.tao, self.ket_factory):
            ham.assert_not_called()
        self.assertIn('Chạy khô', out.getvalue())
        self.assertEqual(list(self.root.iterdir()), [self.ket_root])

    def test_mo_luu_thang_ket_khong_lo_khoa_ngoai_ket(self):
        with redirect_stdout(io.StringIO()) as out, self.assertLogs(a.LOG, level='INFO') as logs:
            self.assertEqual(self.mo(), 0)
        self.sinh_khoa.assert_called_once_with(48)
        s = a._doc(self.tep)
        self.assertEqual(s['pid'], self.p.pid)
        self.assertEqual(s['tao_luc'], '123456789')
        self.assertEqual(s['trang_thai'], 'dang-mo')
        self.assertEqual(self.ket.khoa[s['ten_khoa']], CANARY.encode())
        sent = self.cap.call_args.args
        self.assertEqual(sent[3].lay_de_truyen(), CANARY.encode())
        self.assertEqual(sent[2]['ip_core'], '192.168.1.20')
        self.assertEqual(sent[2]['dia_chi'], '127.0.0.1')
        self.assertRegex(out.getvalue(), r'\d{2}/\d{2}/\d{4}')
        output = out.getvalue() + repr(logs.output) + self.tep.read_text(encoding='utf-8')
        self.assertNotIn(CANARY, output)
        for tep in self.root.rglob('*'):
            if tep.is_file():
                self.assertNotIn(CANARY.encode(), tep.read_bytes())
        self.assertFalse(Path(self.args.hot_folder).exists())

    def test_dong_dung_pid_va_thu_hoi_sau_khi_dung(self):
        with redirect_stdout(io.StringIO()):
            self.mo()
        s = a._doc(self.tep)
        self.tt.dung.side_effect = lambda *_: self.assertEqual(self.ket.da_thu, [])
        with redirect_stdout(io.StringIO()):
            self.assertEqual(self.dong(), 0)
            self.assertEqual(self.dong(), 0)  # Đóng lặp không dừng/thu hồi nhầm lần nữa.
        self.tt.dung.assert_called_once_with(43210, '123456789')
        self.assertEqual(self.ket.da_thu, [s['ten_khoa']])
        self.assertFalse((self.ket_root / (s['ten_khoa'] + '.dpapi')).exists())
        self.assertEqual(a._doc(self.tep)['trang_thai'], 'da-dong')

    def test_dung_that_bai_giu_trang_thai_de_thu_lai(self):
        with redirect_stdout(io.StringIO()):
            self.mo()
        self.tt.dung.side_effect = a.LoiKetNoi('DEMO không đúng tiến trình')
        with self.assertRaises(a.LoiKetNoi):
            self.dong()
        self.assertEqual(a._doc(self.tep)['pid'], 43210)
        self.assertTrue(a._doc(self.tep)['can_thu_hoi'])
        self.assertEqual(self.ket.da_thu, [])

    def test_thu_hoi_loi_dong_lai_khong_dung_pid_lan_hai(self):
        with redirect_stdout(io.StringIO()):
            self.mo()
        with patch.object(self.ket, 'thu_hoi', side_effect=OSError('DEMO')):
            with self.assertRaises(OSError):
                self.dong()
        s = a._doc(self.tep)
        self.assertIsNone(s['pid'])
        self.assertTrue(s['can_thu_hoi'])
        with redirect_stdout(io.StringIO()):
            self.dong()
        self.tt.dung.assert_called_once()
        self.assertFalse(a._doc(self.tep)['can_thu_hoi'])

    def test_khong_mo_de_len_phien_cu(self):
        with redirect_stdout(io.StringIO()):
            self.mo()
        with self.assertRaises(a.LoiKetNoi):
            self.mo()
        self.tao.assert_called_once()

    def test_khoi_dong_loi_dung_con_va_thu_hoi_khoa(self):
        self.cap.side_effect = RuntimeError(CANARY)
        with self.assertRaises(RuntimeError):
            self.mo()
        self.p.terminate.assert_called_once()
        self.p.wait.assert_called_once_with(timeout=10)
        self.assertFalse(a._doc(self.tep)['can_thu_hoi'])
        self.assertEqual(a._doc(self.tep)['trang_thai'], 'da-dong')
        self.assertEqual(len(self.ket.da_thu), 1)

    def test_khoi_dong_khong_tao_duoc_con_van_thu_hoi(self):
        self.tao.side_effect = OSError('DEMO')
        with self.assertRaises(OSError):
            self.mo()
        self.assertEqual(len(self.ket.da_thu), 1)
        self.assertFalse(a._doc(self.tep)['can_thu_hoi'])

    def test_da_het_han_khi_khoi_dong_khong_bao_mo_thanh_cong(self):
        self.args.gio = 0.000001
        with patch.object(a.time, 'time', side_effect=[100.0, 101.0]), \
                patch.object(a.LOG, 'warning'), \
                redirect_stdout(io.StringIO()) as out:
            with self.assertRaises(a.LoiKetNoi):
                self.mo()
        self.assertEqual(out.getvalue(), '')
        self.p.terminate.assert_called_once()
        self.assertFalse(a._doc(self.tep)['can_thu_hoi'])

    @unittest.skipUnless(os.name == 'nt', 'Khóa tệp Windows được mock trên Windows.')
    def test_tu_thu_hoi_cho_khoa_trang_thai_dang_ban(self):
        import msvcrt
        with patch.object(msvcrt, 'locking', side_effect=[OSError('DEMO bận'), None, None]) as lock, \
                patch.object(a.time, 'sleep') as nghi:
            with a._khoa(self.tep, doi_khoa=True):
                pass
        self.assertEqual(lock.call_count, 3)
        nghi.assert_called_once_with(0.05)

    def test_ip_cong_gio_sai_khong_sinh_khoa_hay_tao_tien_trinh(self):
        for ten, value in (('ip_core', '0.0.0.0'), ('ip_core', '8.8.8.8'),
                           ('dia_chi', '::'), ('dia_chi', '224.0.0.1'),
                           ('gio', float('nan')), ('gio', -1), ('gio', 0), ('cong', 0)):
            cu = getattr(self.args, ten)
            setattr(self.args, ten, value)
            with self.subTest(ten=ten, value=value), self.assertRaises((a.LoiKetNoi, ValueError)):
                self.mo()
            setattr(self.args, ten, cu)
        self.assertFalse(self.tep.exists())
        self.tao.assert_not_called()
        self.ket_factory.assert_not_called()

    def test_trang_thai_khong_doc_gia_tri_khoa_khong_dung_tien_trinh(self):
        with redirect_stdout(io.StringIO()):
            self.mo()
        truoc = self.tep.read_bytes()
        self.ket_factory.reset_mock()
        for identity in ('123456789', None, 'PID_DA_TAI_SU_DUNG'):
            self.tt.danh_tinh.return_value = identity
            with redirect_stdout(io.StringIO()) as out:
                self.assertEqual(a.trang_thai(tep=self.tep, tien_trinh=self.tt), 0)
            self.assertNotIn(CANARY, out.getvalue())
        self.ket_factory.assert_not_called()
        self.tt.dung.assert_not_called()
        self.assertEqual(self.tep.read_bytes(), truoc)

    def test_het_han_tu_dong_dong_va_thu_hoi_khong_can_lenh_dong(self):
        with redirect_stdout(io.StringIO()):
            self.mo()
        s = a._doc(self.tep)
        gio = [s['het_luc'] - 1]
        don_dieu = [100.0]
        may = Mock()

        def xu_ly():
            gio[0] += 0.5
            don_dieu[0] += 0.5

        with patch.object(a, '_tao_may_chu', return_value=may), \
                patch.object(a.bi_mat, 'KetBiMat', self.ket_factory), \
                patch.object(a.threading, 'Thread'), redirect_stdout(io.StringIO()):
            a._phuc_vu({'trang_thai': s, 'cau_hinh': {}, 'tep': str(self.tep)},
                       a.bi_mat.BiMat(CANARY.encode()),
                       dong_ho=lambda: gio[0], don_dieu=lambda: don_dieu[0], doi=lambda _: xu_ly())
        may.server_close.assert_called_once()
        self.assertEqual(don_dieu[0], 101.0)
        self.assertEqual(a._doc(self.tep)['trang_thai'], 'het-han')
        self.assertFalse(a._doc(self.tep)['can_thu_hoi'])
        self.assertIsNone(a._doc(self.tep)['pid'])
        self.assertEqual(self.ket.da_thu, [s['ten_khoa']])

    def test_doi_lui_gio_khong_keo_dai_thoi_han(self):
        with redirect_stdout(io.StringIO()):
            self.mo()
        s = a._doc(self.tep)
        gio = [s['het_luc'] - 1]
        don_dieu = [100.0]
        may = Mock()

        def xu_ly():
            gio[0] -= 100
            don_dieu[0] += 0.5

        with patch.object(a, '_tao_may_chu', return_value=may), \
                patch.object(a.bi_mat, 'KetBiMat', self.ket_factory), \
                patch.object(a.threading, 'Thread'), redirect_stdout(io.StringIO()):
            a._phuc_vu({'trang_thai': s, 'cau_hinh': {}, 'tep': str(self.tep)},
                       a.bi_mat.BiMat(CANARY.encode()),
                       dong_ho=lambda: gio[0], don_dieu=lambda: don_dieu[0], doi=lambda _: xu_ly())
        self.assertEqual(don_dieu[0], 101.0)
        self.assertEqual(a._doc(self.tep)['trang_thai'], 'het-han')

    def test_phien_cu_khong_thu_hoi_khoa_cua_phien_moi(self):
        with redirect_stdout(io.StringIO()):
            self.mo()
        s = a._doc(self.tep)
        cu = dict(s, phien=uuid4().hex, het_luc=0)
        with patch.object(a, '_tao_may_chu', return_value=Mock()), \
                patch.object(a.bi_mat, 'KetBiMat', self.ket_factory), redirect_stdout(io.StringIO()):
            a._phuc_vu({'trang_thai': cu, 'cau_hinh': {}, 'tep': str(self.tep)},
                       a.bi_mat.BiMat(CANARY.encode()))
        self.assertEqual(self.ket.da_thu, [])
        self.assertEqual(a._doc(self.tep), s)

    def test_dong_phien_bi_ngat_truoc_luu_hoac_sau_thu_hoi(self):
        with redirect_stdout(io.StringIO()):
            self.mo()
        s = a._doc(self.tep)
        # Mô phỏng đã rename nhưng chưa kịp ghi trạng thái.
        self.ket.thu_hoi(s['ten_khoa'])
        with redirect_stdout(io.StringIO()):
            self.dong()
        self.assertEqual(len(self.ket.da_thu), 1)
        self.assertFalse(a._doc(self.tep)['can_thu_hoi'])
        # Mô phỏng đã ghi dấu phiên nhưng chưa lưu được tệp khóa.
        phien = uuid4().hex
        s.update(phien=phien, ten_khoa='abbyy-tam-' + phien,
                 pid=None, tao_luc=None, can_thu_hoi=True, trang_thai='dang-chuan-bi')
        a._ghi(self.tep, s)
        with redirect_stdout(io.StringIO()):
            self.dong()
        self.assertFalse(a._doc(self.tep)['can_thu_hoi'])

    def test_cli_loi_khong_in_ngoai_le_chua_khoa(self):
        with patch.object(a, 'mo', side_effect=RuntimeError(CANARY)), \
                redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
            self.assertEqual(a.main(['mo']), 1)
        self.assertNotIn(CANARY, out.getvalue() + err.getvalue())

    def test_cmd_chi_ascii_runtime_dung_va_co_pause_khong_chcp(self):
        for ten, lenh in (('MO-KET-NOI-ABBYY-TAM.cmd', 'mo'), ('DONG-KET-NOI-ABBYY-TAM.cmd', 'dong')):
            raw = (a.GOC / 'tools' / ten).read_bytes()
            self.assertTrue(raw.isascii())
            text = raw.decode('ascii').lower()
            self.assertIn('pause', text)
            self.assertNotIn('chcp', text)
            self.assertIn('d:\\ktt-cd060-demo\\python313\\python.exe', text)
            self.assertIn('"%~dp0abbyy_ket_noi_tam.py" ' + lenh + ' %*', text)


class KenhVaKN2Tests(unittest.TestCase):
    def test_cap_khoa_dung_pipe_core_khong_args_env(self):
        rd, wr = os.pipe()
        with os.fdopen(rd, 'rb') as reader, os.fdopen(wr, 'wb') as writer:
            p = SimpleNamespace(stdin=writer, stdout=io.BytesIO(b'SAN_SANG\n'),
                                args=['DEMO'], env={})
            a._cap_cho_con(p, {'phien': 'DEMO'}, {'dia_chi': '127.0.0.1'},
                           a.bi_mat.BiMat(CANARY.encode()), Path('DEMO.json'))
            c = a.doc_thong_diep(reader.readline(65_536))
            k = a.doc_thong_diep(reader.readline(65_536))
        self.assertNotIn(CANARY, repr(c) + repr(p.args) + repr(p.env))
        import base64
        self.assertEqual(base64.b64decode(k['du_lieu']), CANARY.encode())

    def test_bao_san_sang_windows_crlf_va_timeout_dong_an_toan(self):
        for dong in (b'SAN_SANG\r\n', b'SAI\r\n'):
            rd, wr = os.pipe()
            with os.fdopen(rd, 'rb'), os.fdopen(wr, 'wb') as writer:
                p = SimpleNamespace(stdin=writer, stdout=io.BytesIO(dong))
                if dong.startswith(b'SAN_SANG'):
                    a._cap_cho_con(p, {}, {}, a.bi_mat.BiMat(CANARY.encode()), Path('DEMO.json'))
                else:
                    with self.assertRaises(a.LoiKetNoi):
                        a._cap_cho_con(p, {}, {}, a.bi_mat.BiMat(CANARY.encode()), Path('DEMO.json'))
        with patch.object(a, 'queue') as hang, patch.object(a.threading, 'Thread'), \
                patch.object(a.bi_mat, 'gui_cho_con'):
            # Dùng Queue thật có get giả để không chờ 20 giây.
            import queue
            hang.Empty = queue.Empty
            hang.Queue.return_value.get.side_effect = queue.Empty
            p = SimpleNamespace(stdin=io.BytesIO(), stdout=io.BytesIO())
            with self.assertRaises(a.LoiKetNoi):
                a._cap_cho_con(p, {}, {}, a.bi_mat.BiMat(CANARY.encode()), Path('DEMO.json'))

    def test_kn2_nhan_dung_tls_ip_noi_bo_va_khong_doc_hot_folder(self):
        from kho_tri_thuc.engines.e_ocr import cau_noi_abbyy as kn2
        c = dict(ip_core='192.168.1.20', dia_chi='127.0.0.1', cong=9443,
                 hot_folder='D:/DEMO_HOT_FOLDER_KHONG_DOC')
        with patch.object(a, '_tls') as tls, patch.object(kn2, 'CauNoiABBYY') as cau, \
                patch.object(kn2, '_MayChuHTTPS') as may, \
                patch.object(Path, 'open', side_effect=AssertionError('Không đọc Hot Folder')):
            self.assertIs(a._tao_may_chu(c, a.bi_mat.BiMat(CANARY.encode())), may.return_value)
        cfg = cau.call_args.args[0]
        self.assertTrue(cfg.bat)
        self.assertIs(cfg.tls, tls.return_value)
        self.assertEqual(cfg.ip_core, ('192.168.1.20',))
        self.assertEqual(cfg.dia_chi, '127.0.0.1')

    def test_tls_bat_buoc_server_va_toi_thieu_12(self):
        import ssl
        with patch.object(a.ssl, 'SSLContext') as factory:
            c = {'chung_thu': 'DEMO-cert', 'khoa_tls': 'DEMO-tls'}
            a._tls(c)
        factory.assert_called_once_with(ssl.PROTOCOL_TLS_SERVER)
        self.assertEqual(factory.return_value.minimum_version, ssl.TLSVersion.TLSv1_2)
        self.assertEqual(factory.return_value.load_cert_chain.call_args.args, ('DEMO-cert', 'DEMO-tls'))

    def test_lenh_tao_con_khong_khoa_va_an_cua_so(self):
        with patch.object(a.subprocess, 'Popen') as popen:
            a._tao_tien_trinh()
        args, kw = popen.call_args
        self.assertNotIn(CANARY, repr(args) + repr(kw))
        self.assertNotIn('env', kw)
        self.assertIn('-B', args[0])
        self.assertEqual(kw['stdin'], a.subprocess.PIPE)
        self.assertEqual(kw['creationflags'], a.subprocess.CREATE_NO_WINDOW)

    def test_windows_pid_tai_su_dung_khong_dung_tien_trinh_khac(self):
        api = Mock()
        tt = object.__new__(a.TienTrinhWindows)
        tt.api = api
        tt.ct, tt.wt = Mock(), wintypes
        api.OpenProcess.return_value = 777
        with patch.object(tt, '_danh_tinh', return_value='TAO_LUC_MOI'):
            with self.assertRaises(a.LoiKetNoi):
                tt.dung(43210, 'TAO_LUC_CU')
        api.TerminateProcess.assert_not_called()
        api.CloseHandle.assert_called_once_with(777)

    def test_windows_dung_cung_handle_sau_khi_xac_minh(self):
        api = Mock()
        tt = object.__new__(a.TienTrinhWindows)
        tt.api = api
        tt.ct, tt.wt = Mock(), wintypes
        api.OpenProcess.return_value = 777
        api.WaitForSingleObject.return_value = 0
        with patch.object(tt, '_danh_tinh', return_value='TAO_LUC_DUNG'):
            tt.dung(43210, 'TAO_LUC_DUNG')
        api.TerminateProcess.assert_called_once_with(777, 0)
        api.WaitForSingleObject.assert_called_once_with(777, 10_000)
        api.CloseHandle.assert_called_once_with(777)


if __name__ == '__main__':
    unittest.main()
