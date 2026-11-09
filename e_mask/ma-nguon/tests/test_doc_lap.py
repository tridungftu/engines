"""Kiểm AST và chặn trước spawn bằng mock; không chạy Mask. Dữ liệu giả."""

import ast
import importlib
from importlib.util import resolve_name
import json
from pathlib import Path
import unittest
from unittest.mock import Mock, create_autospec, patch

GOC = Path(__file__).resolve().parents[1]


class GoiTinh(unittest.TestCase):
    def test_import_chi_qua_sdk_ngoai_le_tuong_minh(self):
        # SDK chưa có env_con (lọc env + ghép SRC_CENTRAL); giữ nguyên
        # helper nguồn, không chép logic hoặc tự bổ sung API SDK trong lát 29.
        ngoai_le = {
            'chay.py': {'kho_tri_thuc.nguon.trich6_host.env_con'},
            'vong_doi.py': set(),
        }
        cam = ('kho_tri_thuc.ha_tang', 'kho_tri_thuc.nguon', 'kho_tri_thuc.core')
        for ten, cho_phep in ngoai_le.items():
            cay = ast.parse((GOC / ten).read_text(encoding='utf-8'))
            phu_thuoc = set()
            for nut in ast.walk(cay):
                if isinstance(nut, ast.Import):
                    nhap = [alias.name for alias in nut.names]
                elif isinstance(nut, ast.ImportFrom):
                    module = nut.module or ''
                    if nut.level:
                        module = resolve_name('.' * nut.level + module,
                                              'kho_tri_thuc.engines.e_mask')
                    nhap = [module + '.' + alias.name for alias in nut.names]
                else:
                    continue
                phu_thuoc.update(ten_nhap for ten_nhap in nhap
                                 if any(ten_nhap == goc or ten_nhap.startswith(goc + '.')
                                        for goc in cam))
            with self.subTest(tep=ten):
                self.assertEqual(phu_thuoc, cho_phep)

    def test_tep_ma_co_mat(self):
        for ten in ('chay.py', 'vong_doi.py', 'contract/du_thao.json'):
            self.assertTrue((GOC / ten).is_file(), ten)

    def test_chua_cong_bo_capability(self):
        for ten in ('engine.json', 'contract/schemas.json', 'contract/vi_du.json'):
            self.assertFalse((GOC / ten).exists(), ten)

    def test_du_thao_chua_kich_hoat(self):
        du_thao = json.loads((GOC / 'contract/du_thao.json').read_text(encoding='utf-8'))
        self.assertIs(du_thao['kich_hoat'], False)
        self.assertEqual(du_thao['trang_thai'], 'du_thao_cho_Anh_duyet')


class ChanTruocSpawn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chay = importlib.import_module('kho_tri_thuc.engines.e_mask.chay')
        cls.vong_doi = importlib.import_module('kho_tri_thuc.engines.e_mask.vong_doi')

    def test_thieu_seam_chan_ca_hai_khung_truoc_popen(self):
        for lop, them in (
                (self.chay.TienTrinhMask, {}),
                (self.vong_doi.VongDoiMask, {'danh_muc_da_mo': lambda p: False})):
            for seam, ma in (('cap_khoa', 'THIEU_SEAM_CAP_KHOA'),
                             ('kiem_san_sang', 'THIEU_SEAM_VONG_DOI')):
                cap, ready = Mock(return_value=True), Mock(return_value=True)
                cfg = dict(thu_muc_mask=GOC, cong=19357, cap_khoa=cap,
                           kiem_san_sang=ready, cho_phep_dung=lambda p: True, **them)
                cfg[seam] = None
                with self.subTest(lop=lop.__name__, seam=seam), patch.object(
                        self.chay.subprocess, 'Popen') as spawn:
                    with self.assertRaises(self.chay.LoiMask) as bat:
                        lop(**cfg).khoi_dong()
                    self.assertEqual(bat.exception.ma, ma)
                    spawn.assert_not_called()
                    cap.assert_not_called()
                    ready.assert_not_called()

    def test_launcher_sdk_chan_truoc_spawn_khong_fallback(self):
        from kho_tri_thuc.sdk_core.ho_so_engine import (
            BoKhoiChayTaiKhoan, LoiKhoiChayTaiKhoan,
        )

        for seam, ma in (
                ('bo_khoi_chay_tai_khoan', 'KHOI_CHAY_TAI_KHOAN_CHUA_CAU_HINH'),
                ('gan_job', 'THIEU_SEAM_GAN_JOB'),
                ('bi_mat', 'THIEU_KENH_BI_MAT'),
                ('acl', 'ACL_THU_MUC_KHONG_DUNG')):
            bo = create_autospec(BoKhoiChayTaiKhoan, instance=True)
            cap, job = Mock(return_value=True), Mock(return_value=True)
            cfg = dict(thu_muc_mask=GOC, cong=19357, cap_khoa=cap,
                       kiem_san_sang=lambda *a: True, cho_phep_dung=lambda p: True,
                       bat_khoi_chay_tai_khoan=True, bo_khoi_chay_tai_khoan=bo,
                       gan_job=job, bi_mat=self.chay.BiMatBootstrap(b'DU_LIEU_GIA_MASK'))
            if seam == 'acl':
                bo.kiem_tra.side_effect = LoiKhoiChayTaiKhoan(ma)
            else:
                cfg[seam] = None
            with self.subTest(seam=seam), patch.object(
                    self.chay.subprocess, 'Popen') as spawn:
                with self.assertRaises(self.chay.LoiMask) as bat:
                    self.chay.TienTrinhMask(**cfg).khoi_dong()
                self.assertEqual(bat.exception.ma, ma)
                spawn.assert_not_called()
                bo.khoi_chay.assert_not_called()
                cap.assert_not_called()
                job.assert_not_called()
                if seam == 'acl':
                    bo.kiem_tra.assert_called_once_with('mask')


if __name__ == '__main__':
    unittest.main()
