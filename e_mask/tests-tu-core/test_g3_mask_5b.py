"""MASK-5b: preflight và chặn launcher đã bỏ; chỉ tài khoản/ACL/Job giả.

QĐ cuối e_mask §2.3/§5.3: không khởi chạy nguồn ngoài hoặc truyền khóa RAM.
Giữ kiểm cấu hình, thu hồi bootstrap và không phản chiếu bí mật khi từ chối.
"""

from dataclasses import replace
import io
import os
from pathlib import Path
import sys
import traceback
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from kho_tri_thuc.core import khoi_chay_tai_khoan as kc
from kho_tri_thuc.engines.e_mask import chay as mask
from kho_tri_thuc.sdk_core.bootstrap import BiMatBootstrap


ROOT = Path(__file__).resolve().parents[1]
DEMO = b'DEMO_MASK5B_SECRET'


class MaskTaiKhoanTest(unittest.TestCase):
    def setUp(self):
        self.lich = []
        self.proc = MagicMock()
        self.proc.stdin = io.BytesIO()
        self.proc.poll.return_value = None
        self.proc.terminate.side_effect = lambda: setattr(self.proc.poll, 'return_value', 0)
        self.spawn = MagicMock(side_effect=self._spawn)
        self.hs = kc.HoSoTaiKhoan(mask.HO_SO_TAI_KHOAN, 'ktt_mask_demo',
                                 str(ROOT / 'src'), str(ROOT / 'tests'))
        self.bo = kc.BoKhoiChayTaiKhoanGia(
            ho_so={self.hs.ma: self.hs}, tai_khoan_ton_tai={self.hs.tai_khoan},
            ho_so_duoc_phep={self.hs.ma}, acl={
                (self.hs.thu_muc_chuong_trinh, self.hs.tai_khoan): 'ReadAndExecute',
                (self.hs.thu_muc_lam_viec, self.hs.tai_khoan): 'Modify'},
            popen=self.spawn)
        self.bi_mat = BiMatBootstrap(DEMO)
        self.job = MagicMock(side_effect=lambda p: self.lich.append(('job', p)))
        self.ready = MagicMock(side_effect=self._ready)
        self.fallback = self.enterContext(patch.object(mask.subprocess, 'Popen'))

    def _spawn(self, *args, **kwargs):
        self.lich.append(('spawn', self.proc))
        return self.proc

    def _cap(self, *args, **kwargs):
        self.lich.append(('bi_mat', self.proc))
        self.fail('Launcher đã bỏ không được gọi callback cấp khóa.')

    def _ready(self, proc, cong):
        self.lich.append(('ready', proc))
        self.fail('Launcher đã bỏ không được kiểm readiness nguồn ngoài.')

    def _tao(self, **doi):
        cfg = dict(thu_muc_mask=ROOT / 'tests', cong=19357,
                   cap_khoa=self._cap, kiem_san_sang=self.ready,
                   cho_phep_dung=lambda p: True, bat_khoi_chay_tai_khoan=True,
                   bo_khoi_chay_tai_khoan=self.bo, gan_job=self.job,
                   bi_mat=self.bi_mat)
        cfg.update(doi)
        return mask.TienTrinhMask(**cfg)

    def _loi(self, ma, **doi):
        khung = self._tao(**doi)
        with self.assertRaises(mask.LoiMask) as bat:
            khung.khoi_dong()
        self.assertEqual(bat.exception.ma, ma)
        self.assertIsNone(bat.exception.__context__)
        self.assertNotIn(DEMO.decode(), ''.join(traceback.format_exception(bat.exception)))
        self.fallback.assert_not_called()
        self.spawn.assert_not_called()
        self.job.assert_not_called()
        self.ready.assert_not_called()
        self.proc.terminate.assert_not_called()
        self.assertEqual(self.lich, [])
        with self.assertRaisesRegex(Exception, 'BM_DA_LAY'):
            self.bi_mat.lay_mot_lan()
        return khung

    def test_du_ho_so_van_chan_launcher_khong_job_cap_khoa_va_ready(self):
        with patch.dict(os.environ, {'MASK5B_SECRET': DEMO.decode(),
                                     'PGPASSWORD': DEMO.decode()}):
            with patch.object(self.bo, 'kiem_tra', wraps=self.bo.kiem_tra) as kiem:
                self._loi('MASK_LAUNCHER_DA_BO')
        kiem.assert_called_once_with(mask.HO_SO_TAI_KHOAN)
        self.assertEqual(self.bo.ghi_nhan, [])

    def test_mac_dinh_tat_van_chan_ca_launcher_va_popen(self):
        cap = MagicMock(return_value=True)
        self.bo.ho_so.clear()
        self.fallback.return_value = self.proc
        khung = mask.TienTrinhMask(thu_muc_mask=ROOT / 'tests', cong=19357,
            cap_khoa=cap, kiem_san_sang=lambda *a: True,
            cho_phep_dung=lambda p: True, bo_khoi_chay_tai_khoan=self.bo)
        with self.assertRaises(mask.LoiMask) as bat:
            khung.khoi_dong()
        self.assertEqual(bat.exception.ma, 'MASK_LAUNCHER_DA_BO')
        self.fallback.assert_not_called()
        self.spawn.assert_not_called()
        cap.assert_not_called()

    def test_co_sai_khong_chay(self):
        for sai in ('true', 'false', 1, None):
            with self.subTest(sai=sai), self.assertRaisesRegex(
                    mask.LoiMask, 'CO_TAI_KHOAN_KHONG_HOP_LE'):
                self._tao(bat_khoi_chay_tai_khoan=sai)
        self.spawn.assert_not_called()
        self.fallback.assert_not_called()

    def test_thieu_seam_khoa_chan_truoc_launcher(self):
        self._loi('THIEU_SEAM_CAP_KHOA', cap_khoa=None)
        self.spawn.assert_not_called()
        self.job.assert_not_called()

    def test_thieu_vong_doi_chan_truoc_launcher(self):
        self._loi('THIEU_SEAM_VONG_DOI', kiem_san_sang=None)
        self.spawn.assert_not_called()

    def test_thieu_launcher_khong_fallback(self):
        self._loi('KHOI_CHAY_TAI_KHOAN_CHUA_CAU_HINH', bo_khoi_chay_tai_khoan=None)
        self.spawn.assert_not_called()

    def test_thieu_job_khong_cap_khoa(self):
        self._loi('THIEU_SEAM_GAN_JOB', gan_job=None)
        self.spawn.assert_not_called()

    def test_khong_nhan_bi_mat_raw_hoac_thieu_kenh(self):
        for sai in (None, DEMO, {'khoa': DEMO}):
            with self.subTest(kieu=type(sai).__name__):
                self.bi_mat = BiMatBootstrap(DEMO)
                khung = self._tao(bi_mat=sai)
                with self.assertRaisesRegex(mask.LoiMask, 'THIEU_KENH_BI_MAT'):
                    khung.khoi_dong()
        self.spawn.assert_not_called()

    def test_thieu_ho_so_khong_fallback(self):
        self._loi('HO_SO_TAI_KHOAN_KHONG_HOP_LE', ho_so_tai_khoan=None)
        self.spawn.assert_not_called()

    def test_ho_so_khong_tim_thay(self):
        self.bo.ho_so.clear()
        self._loi('HO_SO_TAI_KHOAN_KHONG_THAY')
        self.spawn.assert_not_called()

    def test_tai_khoan_khong_ton_tai(self):
        self.bo.tai_khoan_ton_tai.clear()
        self._loi('TAI_KHOAN_KHONG_TON_TAI')
        self.spawn.assert_not_called()

    def test_tai_khoan_khong_duoc_phep(self):
        self.bo.ho_so_duoc_phep.clear()
        self._loi('TAI_KHOAN_KHONG_DUOC_PHEP')
        self.spawn.assert_not_called()

    def test_acl_sai(self):
        self.bo.acl.clear()
        self._loi('ACL_THU_MUC_KHONG_DUNG')
        self.spawn.assert_not_called()

    def test_cwd_khong_khop_ho_so_khong_chay(self):
        self.bo.ho_so[self.hs.ma] = replace(self.hs, thu_muc_lam_viec=str(ROOT))
        self.bo.acl[(str(ROOT), self.hs.tai_khoan)] = 'Modify'
        # Nguồn ngoài đã bỏ; không còn so cwd để chạy script, vẫn tuyệt đối không spawn.
        self._loi('MASK_LAUNCHER_DA_BO')
        self.spawn.assert_not_called()

    def test_acl_thu_hoi_sau_preflight_van_chan_spawn(self):
        kiem = self.bo.kiem_tra
        lan = []
        def thu_hoi(ma):
            hs = kiem(ma)
            lan.append(ma)
            self.bo.acl.clear()
            return hs
        with patch.object(self.bo, 'kiem_tra', side_effect=thu_hoi):
            self._loi('MASK_LAUNCHER_DA_BO')
        self.assertEqual(lan, [self.hs.ma])
        self.spawn.assert_not_called()

    def test_spawn_loi_khong_fallback_khong_lo_bi_mat(self):
        self.spawn.side_effect = OSError(DEMO.decode())
        self._loi('MASK_LAUNCHER_DA_BO')
        self.spawn.assert_not_called()
        self.job.assert_not_called()
        self.ready.assert_not_called()

    def test_job_loi_khong_cap_khoa_khong_ready(self):
        self.job.side_effect = RuntimeError(DEMO.decode())
        cap = MagicMock()
        self._loi('MASK_LAUNCHER_DA_BO', cap_khoa=cap)
        cap.assert_not_called()
        self.ready.assert_not_called()
        self.proc.terminate.assert_not_called()

    def test_job_tu_choi_khong_cap_khoa(self):
        cap = MagicMock()
        self._loi('MASK_LAUNCHER_DA_BO', gan_job=lambda p: False, cap_khoa=cap)
        cap.assert_not_called()
        self.ready.assert_not_called()

    def test_cap_khoa_loi_dung_nguon_thu_hoi_ram_khong_ready(self):
        cap = MagicMock(side_effect=RuntimeError(DEMO.decode()))
        self._loi('MASK_LAUNCHER_DA_BO', cap_khoa=cap)
        cap.assert_not_called()
        self.ready.assert_not_called()
        self.proc.terminate.assert_not_called()

    def test_cap_khoa_tu_choi_khong_ready(self):
        self._loi('MASK_LAUNCHER_DA_BO', cap_khoa=lambda *a, **kw: False)
        self.ready.assert_not_called()
        self.proc.terminate.assert_not_called()

    def test_ma_loi_cua_callback_khong_phan_chieu_bi_mat(self):
        cap = MagicMock(side_effect=mask.LoiMask(DEMO.decode()))
        self._loi('MASK_LAUNCHER_DA_BO', cap_khoa=cap)
        cap.assert_not_called()
        self.ready.assert_not_called()

    def test_readiness_loi_khong_nhan_viec(self):
        self.ready.side_effect = RuntimeError(DEMO.decode())
        self._loi('MASK_LAUNCHER_DA_BO')
        self.proc.terminate.assert_not_called()

    def test_ban_that_chua_kiem(self):
        self.assertEqual(kc.TRANG_THAI_BAN_THAT, 'CHUA_KIEM')
        self.assertEqual(self.bo.trang_thai, 'GIA')


if __name__ == '__main__':
    unittest.main()
