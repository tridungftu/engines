"""MASK-5: kiểm seam màn DEMO bằng engine thật, kho RAM và từ vựng DEMO."""
from contextlib import ExitStack
import unittest
from unittest.mock import patch

from engines.e_mask.che_van_ban import che, mo_che
from engines.e_mask.kho_bo_nho import KhoBoNho
from engines.e_mask.nguon.privacy import detectors, leftovers


# Các khóa màn chay_thu_mask.js dùng và ui_chay_thu_mask.cjs mô phỏng.
# Nguồn: che_van_ban.py:385–388, 419, 500, 511, 514, 521–528, 616, 631–633.
KHOA_CHE = {'ma_yeu_cau', 'van_ban_da_che', 'con_sot', 'kiem_tien_ngay',
            'gui_duoc', 'so_cho_thay', 'bi_danh', 'cho_duyet', 'canh_bao'}
KHOA_MO = {'van_ban_da_mo_che', 'so_cho_mo', 'bi_danh_khong_ro',
           'mo_day_du', 'trang_thai_ma_yeu_cau'}
KHOA_VI_TRI = {'bat_dau', 'ket_thuc', 'dong', 'cot'}
CONG_TY = 'Công ty DEMO Ánh Dương'
VAN_BAN = CONG_TY + '; Công ty DEMO Ngôi Sao; 1.000.000 VND; 30/10/2026.'


class Mask5SeamTests(unittest.TestCase):
    def setUp(self):
        self.xoa_cache()
        self.tai_nguyen = ExitStack()
        self.addCleanup(self.xoa_cache)
        self.addCleanup(self.tai_nguyen.close)
        tu_dien = {'vn_surnames.txt': ['Nguyễn *', 'Trần *'],
                   'vn_places.txt': [], 'common_acronyms.txt': ['DEMO VND USD VAT GTGT']}
        self.tai_nguyen.enter_context(patch.object(
            detectors, '_lines', side_effect=lambda ten: tu_dien[ten]))
        self.tai_nguyen.enter_context(patch.object(
            leftovers, 'allowlist', return_value=(frozenset(), frozenset(
                'demo vnd usd dữ liệu giả ngày thanh toán'.split()))))

    @staticmethod
    def xoa_cache():
        for ham in (detectors.surnames, detectors.places, detectors.acronyms,
                    detectors._ascii_surnames, leftovers.allowlist):
            ham.cache_clear()

    def kiem_khoa_che(self, kq):
        self.assertEqual(set(kq), KHOA_CHE)
        self.assertEqual(set(kq['cho_duyet']), {'so_cum_vua_them'})
        for muc in kq['bi_danh']:
            self.assertEqual(set(muc), {'bi_danh', 'nhom', 'nguon'})

    def test_khoa_engine_khop_seam_man_demo(self):
        kho = KhoBoNho([{'gia_tri': CONG_TY, 'nhom': 'CONG_TY', 'ma_junsky': 'CT-0001'}])
        kq = che(VAN_BAN, [], kho)
        self.kiem_khoa_che(kq)
        self.assertTrue(kq['gui_duoc'])
        self.assertTrue(kq['kiem_tien_ngay'])
        self.assertEqual(kq['con_sot'], [])
        self.assertEqual({m['nguon'] for m in kq['bi_danh']}, {'chinh_thuc', 'tam'})

        # Tên đầu vào mở che đúng như payload của màn; kho do host tin cậy tiêm.
        payload = {'van_ban_co_bi_danh': kq['van_ban_da_che'],
                   'ma_yeu_cau': kq['ma_yeu_cau'], 'dong_viec': False}
        mo = mo_che(**payload, kho=kho)
        self.assertEqual(set(mo), KHOA_MO)
        self.assertEqual(mo['van_ban_da_mo_che'], VAN_BAN)
        self.assertTrue(mo['mo_day_du'])
        self.assertEqual(mo['trang_thai_ma_yeu_cau'], 'DANG_XU_LY')

        mo = mo_che(kq['van_ban_da_che'] + '\n[[LA-9999]]', kq['ma_yeu_cau'], kho, dong_viec=True)
        self.assertEqual(set(mo), KHOA_MO)
        self.assertFalse(mo['mo_day_du'])
        self.assertEqual(mo['trang_thai_ma_yeu_cau'], 'DANG_XU_LY')
        self.assertEqual(len(mo['bi_danh_khong_ro']), 1)
        muc = mo['bi_danh_khong_ro'][0]
        self.assertEqual(set(muc), {'bi_danh', 'vi_tri'})
        self.assertEqual(set(muc['vi_tri']), KHOA_VI_TRI)
        self.assertEqual((muc['vi_tri']['dong'], muc['vi_tri']['cot']), (2, 1))

        mo = mo_che(**{**payload, 'dong_viec': True}, kho=kho)
        self.assertEqual(set(mo), KHOA_MO)
        self.assertTrue(mo['mo_day_du'])
        self.assertEqual(mo['trang_thai_ma_yeu_cau'], 'DA_DONG')

        # Định danh dính vào chữ khác: hậu kiểm trả nhóm và object vị trí.
        kho.them_dinh_danh('001234567890', 'MA_SO_THUE')
        chan = che('X001234567890Y', [], kho)
        self.kiem_khoa_che(chan)
        self.assertFalse(chan['gui_duoc'])
        self.assertIsNone(chan['van_ban_da_che'])
        self.assertTrue(chan['con_sot'])
        for muc in chan['con_sot']:
            self.assertEqual(set(muc), {'nhom', 'vi_tri'})
            self.assertEqual(set(muc['vi_tri']), KHOA_VI_TRI)

        chan = che('[[CT-0001]]', [], kho)
        self.kiem_khoa_che(chan)
        self.assertFalse(chan['gui_duoc'])
        self.assertIsNone(chan['van_ban_da_che'])
        self.assertEqual(chan['con_sot'], [
            {'ly_do': 'Văn bản đầu vào đã chứa dấu bí danh cần kiểm tra.'}])


if __name__ == '__main__':
    unittest.main()
