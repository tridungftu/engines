"""HD-3b: portal/Core/profile DEMO trong RAM; không thuế, Windows hay PG.

Thay controller dùng lại sổ Core giả để mô phỏng crash. Không coi đó là
restart tiến trình/sổ bền, ACL thật hay test tài khoản riêng G2-33b.
"""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
import socket
import subprocess
import sys
import traceback
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from kho_tri_thuc.engines.e_hoa_don import phien as hd, tai
from test_g3_hd_2a import CoreStub, PortalStub


CANARY = 'DEMO_COOKIE_CREDENTIAL_KHONG_LO'


class MoiTruongDemo:
    """Mọi xác nhận gắn đầy đủ phiên/pháp nhân; không có đường I/O thật."""

    def __init__(self):
        self.so = hd.SoPhienDemo()
        self.events = []
        self.profiles = {}
        self.opened = set()
        self.receipts = {}
        self.mo_ok = self.dong_ok = self.ack_ok = self.don_ok = True
        self.loi = None
        self.mat_ack = False

    def controller(self):
        return hd.QuanLyPhienDemo(so=self.so, portal=self, core=self,
                                 don_profile=self.don)

    def _ket_qua(self, phase, value):
        if self.loi == phase:
            raise RuntimeError(CANARY)
        if self.loi == phase + '_crash':
            raise KeyboardInterrupt()
        return value

    def mo(self, p):
        self.events.append(('mo', p))
        # Mô phỏng profile/cookie tạo dở trước khi launch ném lỗi.
        assert p.profile_id not in self.profiles
        self.profiles[p.profile_id] = {'chu': p, 'cookie': CANARY + p.phien_id}
        self.opened.add(p)
        return self._ket_qua('mo', self.mo_ok)

    def dong(self, p):
        self.events.append(('dong', p))
        ok = self._ket_qua('dong', self.dong_ok)
        if ok is True:
            self.opened.discard(p)
        return ok

    def ban_giao(self, p, ket_thuc):
        self.events.append(('ack', p))
        assert p not in self.opened
        ok = self._ket_qua('ack', self.ack_ok)
        if ok is not True:
            return ok
        key = (p.phap_nhan_id, p.nguon_id, p.phien_id, p.profile_id)
        if key in self.receipts:
            assert self.receipts[key] == ket_thuc
        self.receipts[key] = ket_thuc
        if self.mat_ack:
            self.mat_ack = False
            raise ConnectionError(CANARY)
        return True

    def don(self, p):
        self.events.append(('don', p))
        assert p not in self.opened
        key = (p.phap_nhan_id, p.nguon_id, p.phien_id, p.profile_id)
        assert key in self.receipts
        assert self.profiles[p.profile_id].get('chu', p) == p
        ok = self._ket_qua('don', self.don_ok)
        if ok is True:
            self.profiles[p.profile_id].clear()
        return ok


class PhienDemoTests(unittest.TestCase):
    def setUp(self):
        self.env = MoiTruongDemo()
        self.controller = self.env.controller()

    def mo(self, phap_nhan='DEMO_A', controller=None):
        return (controller or self.controller).mo_phien(
            demo=True, phap_nhan_id=phap_nhan, nguon_id='DEMO_NGUON')

    def chan_moi(self):
        for pn in ('DEMO_A', 'DEMO_B'):
            with self.subTest(phap_nhan=pn):
                with self.assertRaisesRegex(hd.LoiPhienDemo, '^HD_PROFILE_CHUA_DON$'):
                    self.mo(pn, self.env.controller())

    def test_xong_loi_huy_crash_dong_ack_don_va_khong_dung_lai(self):
        profiles, sessions = set(), set()
        for end in ('xong', 'loi', 'huy', 'crash'):
            for pn in ('DEMO_A', 'DEMO_A', 'DEMO_B'):
                with self.subTest(end=end, phap_nhan=pn):
                    p = self.mo(pn)
                    self.assertNotIn(p.profile_id, profiles)
                    self.assertNotIn(p.phien_id, sessions)
                    profiles.add(p.profile_id)
                    sessions.add(p.phien_id)
                    result = self.controller.ket_thuc(p, end)
                    self.assertEqual(result, hd.TienDoPhien(p, end, True, True, True))
                    self.assertEqual([e for e, s in self.env.events if s == p],
                                     ['mo', 'dong', 'ack', 'don'])
                    self.assertEqual(self.env.profiles[p.profile_id], {})

    def test_phien_dang_mo_chan_ca_cung_va_khac_phap_nhan(self):
        self.mo()
        self.chan_moi()
        self.assertEqual(len(self.env.events), 1)

    def test_dong_browser_that_bai_khong_ack_khong_don(self):
        p = self.mo()
        self.env.dong_ok = False
        with self.assertRaisesRegex(hd.LoiPhienDemo, '^HD_DONG_BROWSER_LOI$'):
            self.controller.ket_thuc(p, 'huy')
        self.assertEqual(self.controller.tien_do(p), hd.TienDoPhien(p, 'huy'))
        self.assertEqual([e for e, _ in self.env.events], ['mo', 'dong'])
        self.chan_moi()
        self.env.dong_ok = True
        self.assertTrue(self.controller.ket_thuc(p, 'huy').da_don)

    def test_cho_ack_giu_profile_va_retry_khong_dong_lai(self):
        p = self.mo()
        self.env.ack_ok = False
        with self.assertRaisesRegex(hd.LoiPhienDemo, '^HD_CHO_ACK$'):
            self.controller.ket_thuc(p, 'xong')
        self.assertEqual(self.controller.tien_do(p), hd.TienDoPhien(p, 'xong', True))
        self.assertIn('cookie', self.env.profiles[p.profile_id])
        self.chan_moi()
        self.env.ack_ok = True
        self.controller.ket_thuc(p, 'xong')
        self.assertEqual([e for e, _ in self.env.events], ['mo', 'dong', 'ack', 'ack', 'don'])

    def test_mat_ack_sau_luu_khong_tai_lai_khong_don_som(self):
        p = self.mo()
        self.env.mat_ack = True
        with self.assertRaisesRegex(hd.LoiPhienDemo, '^HD_CHO_ACK$'):
            self.controller.ket_thuc(p, 'loi')
        self.assertEqual(len(self.env.receipts), 1)
        self.chan_moi()
        result, = self.env.controller().phuc_hoi_crash()
        self.assertEqual(result.ket_thuc, 'loi')
        self.assertTrue(result.da_don)
        self.assertEqual(len(self.env.receipts), 1)
        self.assertEqual(sum(e == 'mo' for e, _ in self.env.events), 1)

    def test_don_that_bai_chan_moi_retry_chi_don(self):
        p = self.mo()
        self.env.don_ok = False
        with self.assertRaisesRegex(hd.LoiPhienDemo, '^HD_DON_PROFILE_LOI$'):
            self.controller.ket_thuc(p, 'xong')
        self.assertEqual(self.controller.tien_do(p), hd.TienDoPhien(p, 'xong', True, True))
        self.chan_moi()
        self.env.don_ok = True
        self.env.controller().phuc_hoi_crash()
        self.assertEqual([e for e, _ in self.env.events], ['mo', 'dong', 'ack', 'don', 'don'])
        self.assertNotEqual(self.mo('DEMO_B').profile_id, p.profile_id)

    def test_crash_khi_dang_mo_phai_phuc_hoi_truoc_phien_moi(self):
        p = self.mo()
        controller = self.env.controller()
        self.chan_moi()
        result, = controller.phuc_hoi_crash()
        self.assertEqual(result, hd.TienDoPhien(p, 'crash', True, True, True))
        self.assertNotEqual(self.mo().profile_id, p.profile_id)

    def test_phuc_hoi_crash_don_that_bai_van_chan_phien_moi(self):
        p = self.mo()
        self.env.don_ok = False
        with self.assertRaisesRegex(hd.LoiPhienDemo, '^HD_DON_PROFILE_LOI$'):
            self.env.controller().phuc_hoi_crash()
        self.chan_moi()
        self.assertEqual(self.controller.tien_do(p), hd.TienDoPhien(p, 'crash', True, True))
        self.assertIn('cookie', self.env.profiles[p.profile_id])
        self.env.don_ok = True
        result, = self.env.controller().phuc_hoi_crash()
        self.assertTrue(result.da_don)
        self.assertNotEqual(self.mo('DEMO_B').profile_id, p.profile_id)

    def test_crash_giua_cac_buoc_don_giu_trang_thai_bao_thu(self):
        for phase in ('dong', 'ack', 'don'):
            with self.subTest(phase=phase):
                self.setUp()
                p = self.mo()
                self.env.loi = phase + '_crash'
                with self.assertRaises(KeyboardInterrupt):
                    self.controller.ket_thuc(p, 'huy')
                self.chan_moi()
                self.assertFalse(self.controller.tien_do(p).da_don)
                self.env.loi = None
                result, = self.env.controller().phuc_hoi_crash()
                self.assertTrue(result.da_don)
                self.assertEqual(result.ket_thuc, 'huy')
                self.assertEqual(sum(e == 'mo' for e, _ in self.env.events), 1)

    def test_mo_loi_hoac_crash_giu_profile_tao_do_de_don(self):
        for phase, exception, end in (('mo', hd.LoiPhienDemo, 'loi'),
                                      ('mo_crash', KeyboardInterrupt, 'crash')):
            with self.subTest(phase=phase):
                self.setUp()
                self.env.loi = phase
                with self.assertRaises(exception):
                    self.mo()
                self.chan_moi()
                self.env.loi = None
                result, = self.env.controller().phuc_hoi_crash()
                self.assertEqual(result.ket_thuc, end)
                self.assertTrue(result.da_don)
                self.assertEqual(self.env.profiles[result.phien.profile_id], {})

    def test_loi_seam_khong_lo_canary_context_hay_traceback(self):
        for phase, code in (('mo', 'HD_MO_PROFILE_LOI'), ('dong', 'HD_DONG_BROWSER_LOI'),
                            ('ack', 'HD_CHO_ACK'), ('don', 'HD_DON_PROFILE_LOI')):
            with self.subTest(phase=phase):
                self.setUp()
                p = None if phase == 'mo' else self.mo()
                self.env.loi = phase
                try:
                    self.mo() if p is None else self.controller.ket_thuc(p, 'loi')
                except hd.LoiPhienDemo as error:
                    self.assertEqual(str(error), code)
                    self.assertIsNone(error.__context__)
                    self.assertNotIn(CANARY, ''.join(traceback.format_exception(error)))
                else:
                    self.fail('Phải báo lỗi seam')
                self.chan_moi()

    def test_khong_nhan_truthy_thay_ack_that(self):
        for field in ('mo_ok', 'dong_ok', 'ack_ok', 'don_ok'):
            for value in (1, 'true', {}, None):
                with self.subTest(field=field, value=value):
                    self.setUp()
                    p = None if field == 'mo_ok' else self.mo()
                    setattr(self.env, field, value)
                    with self.assertRaises(hd.LoiPhienDemo):
                        self.mo() if p is None else self.controller.ket_thuc(p, 'xong')
                    self.chan_moi()

    def test_khong_ban_giao_don_hoac_doc_cheo_phien(self):
        p = self.mo()
        for fake in (replace(p, phap_nhan_id='DEMO_B'), replace(p, nguon_id='NGUON_KHAC'),
                     replace(p, profile_id='PROFILE_KHAC'), replace(p, phien_id='PHIEN_KHAC'), None):
            with self.subTest(fake=fake):
                with self.assertRaisesRegex(hd.LoiPhienDemo, '^HD_PHIEN_SAI$'):
                    self.controller.ket_thuc(fake, 'huy')
                with self.assertRaisesRegex(hd.LoiPhienDemo, '^HD_PHIEN_SAI$'):
                    self.controller.tien_do(fake)
        self.assertEqual(len(self.env.events), 1)

    def test_ket_thuc_idempotent_khong_doi_ket_luan(self):
        p = self.mo()
        result = self.controller.ket_thuc(p, 'xong')
        self.assertEqual(self.controller.ket_thuc(p, 'xong'), result)
        self.assertEqual(self.controller.phuc_hoi_crash(), ())
        with self.assertRaisesRegex(hd.LoiPhienDemo, '^HD_KET_THUC_DA_GHI$'):
            self.controller.ket_thuc(p, 'huy')
        self.assertEqual(len(self.env.events), 4)

    def test_profile_da_don_van_khong_duoc_cap_lai(self):
        p = self.mo()
        self.controller.ket_thuc(p, 'xong')
        for fake in (p, replace(p, phien_id='PHIEN_MOI'), replace(p, profile_id='PROFILE_MOI')):
            with patch.object(tai, 'uuid4', side_effect=[fake.phien_id, fake.profile_id]):
                with self.assertRaisesRegex(hd.LoiPhienDemo, '^HD_PROFILE_DA_DUNG$'):
                    self.mo()
        self.assertEqual(len(self.env.events), 4)

    def test_hai_controller_cung_so_chi_mot_phien_duoc_mo(self):
        def mo(pn):
            try:
                return self.mo(pn, self.env.controller())
            except hd.LoiPhienDemo as error:
                return str(error)
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(mo, ('DEMO_A', 'DEMO_B')))
        self.assertEqual(sum(isinstance(r, tai.PhienGia) for r in results), 1)
        self.assertIn('HD_PROFILE_CHUA_DON', results)
        self.assertEqual(len(self.env.events), 1)

    def test_chi_demo_va_ket_thuc_hop_le(self):
        for value in (False, 1, 'true', None):
            with self.assertRaisesRegex(hd.LoiPhienDemo, '^HD_CHI_DEMO$'):
                self.controller.mo_phien(demo=value, phap_nhan_id='DEMO_A', nguon_id='DEMO_NGUON')
        self.assertEqual(self.env.events, [])
        p = self.mo()
        with self.assertRaisesRegex(hd.LoiPhienDemo, '^HD_KET_THUC_SAI$'):
            self.controller.ket_thuc(p, 'succeeded')
        self.assertIsNone(self.controller.tien_do(p).ket_thuc)

    def test_ban_giao_hd2a_du_xml_coverage_truoc_don_profile(self):
        p = self.mo()
        work = tai.TaiHoaDonGia(phap_nhan_id=p.phap_nhan_id, nguon_id=p.nguon_id,
            tu_ngay='2026-10-01', den_ngay='2026-10-31', huong='mua_vao', portal=PortalStub())
        work.phien = p
        work.tiep_tuc()
        core = CoreStub(work)
        core.ack_phien = False
        original = self.env.ban_giao

        def ban_giao(session, end):
            self.assertEqual(session, p)
            if work.ban_giao(core).da_ack_phien:
                return original(session, end)
            return False

        with patch.object(self.env, 'ban_giao', side_effect=ban_giao):
            with self.assertRaisesRegex(hd.LoiPhienDemo, '^HD_CHO_ACK$'):
                self.controller.ket_thuc(p, 'xong')
            self.assertEqual(len(core.receipts), 1)
            self.assertIn('cookie', self.env.profiles[p.profile_id])
            self.chan_moi()
            core.ack_phien = True
            self.assertTrue(self.controller.ket_thuc(p, 'xong').da_don)
        self.assertEqual(work.ban_giao(core).trang_thai_viec, 'succeeded')
        self.assertEqual(len(core.summaries), 1)
        self.assertEqual(len(work._portal.calls), 2)


class MoiTruongTests(unittest.TestCase):
    def test_g227_thieu_g233b_khong_gia_dat(self):
        with patch.object(hd, 'kiem_tra_tien_trinh', wraps=hd.kiem_tra_tien_trinh) as check:
            results = hd.kiem_tra_moi_truong()
        check.assert_called_once_with('e_hoa_don', phien_ban='1.0.0')
        self.assertTrue(all(r.ket_luan == 'CHUA_KIEM' for r in results))
        self.assertTrue(all(r.ly_do for r in results))
        for result in results:
            self.assertEqual((result.doi_tuong, result.phien_ban), ('e_hoa_don', '1.0.0'))
            if result.ma.startswith('KT'):
                self.assertIn('G2-33b', ' '.join(result.ly_do))
        self.assertEqual({r.ma for r in results},
                         {'KT08', 'KT09', 'KT10', 'KT11', 'KT12', 'KT13', 'KT16',
                          'HD_PROFILE_NGUON', 'HD_COVERAGE_NGUON'})

    def test_khong_io_mang_tao_process_doc_cau_hinh_hoac_don_tep(self):
        env = MoiTruongDemo()
        with patch.object(socket, 'socket', side_effect=AssertionError('Mạng bị cấm')), \
             patch.object(subprocess, 'Popen', side_effect=AssertionError('Process bị cấm')), \
             patch('builtins.open', side_effect=AssertionError('Đọc tệp bị cấm')), \
             patch.object(Path, 'read_bytes', side_effect=AssertionError('Đọc tệp bị cấm')), \
             patch.object(Path, 'read_text', side_effect=AssertionError('Đọc tệp bị cấm')), \
             patch.object(Path, 'unlink', side_effect=AssertionError('Xóa tệp bị cấm')):
            self.assertTrue(all(r.ket_luan == 'CHUA_KIEM' for r in hd.kiem_tra_moi_truong()))
            controller = env.controller()
            p = controller.mo_phien(demo=True, phap_nhan_id='DEMO_A', nguon_id='DEMO_NGUON')
            self.assertTrue(controller.ket_thuc(p, 'xong').da_don)
        self.assertNotIn(CANARY, repr(controller.tien_do(p)))


if __name__ == '__main__':
    unittest.main()
