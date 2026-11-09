"""MASK-3a: chỉ dữ liệu DEMO trong RAM; tài nguyên sạch được mock rõ ràng."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
import json
import os
from pathlib import Path
import subprocess
import sys
from threading import Barrier
from time import perf_counter
import unicodedata
import unittest
from unittest.mock import patch

from engines.e_mask import che_van_ban as xu_ly
from engines.e_mask.che_van_ban import LoiCheVanBan, che, mo_che
from engines.e_mask.kho_bo_nho import KhoBoNho
from engines.e_mask.nguon.privacy import detectors, leftovers


CONG_TY = 'Công ty DEMO Ánh Dương'
TEN_MOI = 'Công ty DEMO Ngôi Sao'
SO_GIA = '001234567890'
VAN_BAN = CONG_TY + '; thanh toán 1.000.000 VND ngày 30/10/2026.'


def xoa_cache():
    for ham in (detectors.surnames, detectors.places, detectors.acronyms,
                detectors._ascii_surnames, leftovers.allowlist):
        ham.cache_clear()


class CheVanBanDemoTests(unittest.TestCase):
    def setUp(self):
        xoa_cache()
        self.tai_nguyen = ExitStack()
        self.addCleanup(xoa_cache)
        self.addCleanup(self.tai_nguyen.close)
        # Chỉ fixture từ vựng DEMO, không thêm tài nguyên vào lõi nguồn.
        tu_dien = {'vn_surnames.txt': ['Nguyễn *', 'Trần *'],
                   'vn_places.txt': [], 'common_acronyms.txt': ['DEMO VND USD VAT GTGT']}
        self.tai_nguyen.enter_context(patch.object(
            detectors, '_lines', side_effect=lambda ten: tu_dien[ten]))
        self.tai_nguyen.enter_context(patch.object(
            leftovers, 'allowlist', return_value=(frozenset(), frozenset(
                'demo vnd usd dữ liệu giả ngày thanh toán giá trị nội dung ai bổ sung'.split()))))
        self.kho = KhoBoNho([{'gia_tri': CONG_TY, 'nhom': 'CONG_TY', 'ma_junsky': 'KH-DEMO-001'}])

    def che_dat(self, van_ban=VAN_BAN, da_biet=None, kho=None):
        kq = che(van_ban, da_biet, self.kho if kho is None else kho)
        self.assertTrue(kq['gui_duoc'], kq['con_sot'])
        self.assertEqual(kq['con_sot'], [])
        self.assertTrue(kq['kiem_tien_ngay'])
        return kq

    def test_che_mo_khu_hoi_chinh_thuc_va_giu_tien_ngay(self):
        kq = self.che_dat()
        self.assertEqual(kq['van_ban_da_che'], '[[KH-DEMO-001]]; thanh toán 1.000.000 VND ngày 30/10/2026.')
        self.assertEqual(kq['so_cho_thay'], 1)
        self.assertEqual(kq['bi_danh'], [{'bi_danh': '[[KH-DEMO-001]]', 'nhom': 'CONG_TY', 'nguon': 'chinh_thuc'}])
        self.assertEqual(kq['cho_duyet']['so_cum_vua_them'], 0)
        mo = mo_che(kq['van_ban_da_che'], kq['ma_yeu_cau'], self.kho)
        self.assertEqual(mo['van_ban_da_mo_che'], VAN_BAN)
        self.assertTrue(mo['mo_day_du'])
        self.assertEqual(mo['so_cho_mo'], 1)
        self.assertEqual(mo['trang_thai_ma_yeu_cau'], 'DANG_XU_LY')

    def test_tu_do_cum_moi_che_tam_khong_lo_cum_goc(self):
        kq = self.che_dat(TEN_MOI + '; 1.000.000 VND; 30/10/2026.')
        self.assertNotIn(TEN_MOI, json.dumps(kq, ensure_ascii=False))
        self.assertEqual(kq['cho_duyet']['so_cum_vua_them'], 1)
        self.assertEqual(self.kho.so_cum_cho_duyet(), 1)
        self.assertEqual(kq['bi_danh'][0]['nguon'], 'tam')
        self.assertRegex(kq['bi_danh'][0]['bi_danh'], r'^\[\[MASKTAM-[0-9a-f]{32}\]\]$')
        self.assertEqual(mo_che(kq['van_ban_da_che'], kq['ma_yeu_cau'], self.kho)['van_ban_da_mo_che'],
                         TEN_MOI + '; 1.000.000 VND; 30/10/2026.')

    def test_da_biet_chua_co_cung_vao_cho_khong_lo(self):
        kq = self.che_dat('đơn vị demo xanh', [{'gia_tri': 'đơn vị demo xanh', 'nhom': 'CONG_TY'}])
        self.assertEqual(kq['cho_duyet']['so_cum_vua_them'], 1)
        self.assertNotIn('đơn vị demo xanh', repr(kq))

    def test_tai_su_dung_tam_khong_dem_lai_cum_moi_va_giu_tham_chieu(self):
        a = self.che_dat(TEN_MOI + '; ' + TEN_MOI)
        self.assertEqual(self.kho.tra_bi_danh(xu_ly.chuan_hoa(TEN_MOI))['so_lan_gap'], 1)
        b = self.che_dat(TEN_MOI)
        self.assertNotEqual(a['ma_yeu_cau'], b['ma_yeu_cau'])
        self.assertEqual(self.kho.tra_bi_danh(xu_ly.chuan_hoa(TEN_MOI))['so_lan_gap'], 2)
        self.assertEqual(a['so_cho_thay'], 2)
        self.assertEqual(len(a['bi_danh']), 1)
        self.assertEqual(b['cho_duyet']['so_cum_vua_them'], 0)
        self.assertEqual(a['bi_danh'], b['bi_danh'])
        self.assertEqual(len(self.kho.doc_yeu_cau(b['ma_yeu_cau'])['bi_danh_tam_da_dung']), 1)
        for kq in (a, b):
            self.assertNotIn(TEN_MOI, json.dumps(kq, ensure_ascii=False))

    def test_retry_cung_ma_yeu_cau_khong_dem_lai_cum_tam(self):
        a = self.che_dat(TEN_MOI + '; ' + TEN_MOI)
        # Kho/adapter tin cậy tái dùng mã khi phát lại; không thêm mã vào đầu vào che.
        with patch.object(self.kho, 'tao_yeu_cau', return_value=a['ma_yeu_cau']):
            b = self.che_dat(TEN_MOI)
            c = self.che_dat(TEN_MOI + '; ' + TEN_MOI)
        self.assertEqual(self.kho.tra_bi_danh(xu_ly.chuan_hoa(TEN_MOI))['so_lan_gap'], 1)
        self.assertEqual(self.kho.so_cum_cho_duyet(), 1)
        for kq in (b, c):
            self.assertEqual(kq['ma_yeu_cau'], a['ma_yeu_cau'])
            self.assertEqual(kq['bi_danh'], a['bi_danh'])
            self.assertEqual(kq['cho_duyet'], {'so_cum_vua_them': 0})
            self.assertNotIn(TEN_MOI, json.dumps(kq, ensure_ascii=False))

    def test_cung_ma_khac_cum_deu_duoc_dem_mot_lan(self):
        ten_khac = 'Công ty DEMO Hướng Dương'
        chu = TEN_MOI + '; ' + ten_khac + '; ' + TEN_MOI
        a = self.che_dat(chu)
        with patch.object(self.kho, 'tao_yeu_cau', return_value=a['ma_yeu_cau']):
            b = self.che_dat(chu)
        self.assertEqual(a['cho_duyet'], {'so_cum_vua_them': 2})
        self.assertEqual(b['cho_duyet'], {'so_cum_vua_them': 0})
        for ten in (TEN_MOI, ten_khac):
            self.assertEqual(self.kho.tra_bi_danh(xu_ly.chuan_hoa(ten))['so_lan_gap'], 1)
            for kq in (a, b):
                self.assertNotIn(ten, json.dumps(kq, ensure_ascii=False))

    def test_ghi_nhan_gap_lai_chuan_hoa_va_hai_ma_khac_nhau(self):
        a = self.che_dat(TEN_MOI)
        cac_dang = (TEN_MOI, unicodedata.normalize('NFD', TEN_MOI.upper()),
                    '  Công   ty DEMO Ngôi\tSao  ')
        for chu in cac_dang:
            self.kho.ghi_nhan_gap_lai(a['ma_yeu_cau'], chu, 'CONG_TY')
        self.assertEqual(self.kho.tra_bi_danh(xu_ly.chuan_hoa(TEN_MOI))['so_lan_gap'], 1)
        ma_khac = self.kho.tao_yeu_cau()
        for chu in cac_dang:
            self.kho.ghi_nhan_gap_lai(ma_khac, chu, 'CONG_TY')
        self.assertEqual(self.kho.tra_bi_danh(xu_ly.chuan_hoa(TEN_MOI))['so_lan_gap'], 2)

    def test_cum_chinh_thuc_khong_ghi_nhan_gap_lai(self):
        with patch.object(self.kho, 'ghi_nhan_gap_lai', create=True) as ghi:
            self.che_dat()
        ghi.assert_not_called()
        self.assertEqual(self.kho.so_cum_cho_duyet(), 0)

    def test_ghi_nhan_gap_lai_tu_choi_ma_sai_phien_sai_va_da_dong(self):
        a = self.che_dat(TEN_MOI)
        for module, nguoi in (('khac', 'nguoi_demo_a'), ('demo_mask', 'nguoi_khac')):
            khac = self.kho.theo_phien(module=module, nguoi_gui=nguoi)
            with self.assertRaises(ValueError):
                khac.ghi_nhan_gap_lai(a['ma_yeu_cau'], xu_ly.chuan_hoa(TEN_MOI), 'CONG_TY')
        with self.assertRaises(ValueError):
            self.kho.ghi_nhan_gap_lai('ma_khong_co', xu_ly.chuan_hoa(TEN_MOI), 'CONG_TY')
        self.kho.dong_yeu_cau(a['ma_yeu_cau'])
        with self.assertRaises(ValueError):
            self.kho.ghi_nhan_gap_lai(a['ma_yeu_cau'], xu_ly.chuan_hoa(TEN_MOI), 'CONG_TY')
        self.assertEqual(self.kho.tra_bi_danh(xu_ly.chuan_hoa(TEN_MOI))['so_lan_gap'], 1)

    def test_ghi_nhan_gap_lai_dong_thoi_nguyen_tu_va_chong_dem_lap(self):
        self.che_dat(TEN_MOI)
        cac_ma = [self.kho.tao_yeu_cau() for _ in range(16)]
        cho = Barrier(8)

        def ghi(ma):
            cho.wait(timeout=5)
            self.kho.ghi_nhan_gap_lai(ma, xu_ly.chuan_hoa(TEN_MOI), 'CONG_TY')

        # Gọi trực tiếp port để kiểm khóa của thao tác đếm, không dựa khóa giao dịch ngoài.
        with ThreadPoolExecutor(max_workers=8) as nhom:
            list(nhom.map(ghi, [ma for ma in cac_ma for _ in range(4)]))
        self.assertEqual(self.kho.tra_bi_danh(xu_ly.chuan_hoa(TEN_MOI))['so_lan_gap'], 17)

    def test_gap_lai_rollback_ca_bo_dem_va_dau_chong_lap(self):
        self.che_dat(TEN_MOI)
        ma = self.kho.tao_yeu_cau()
        with patch.object(self.kho, 'tao_yeu_cau', return_value=ma):
            with patch.object(self.kho, 'ghi_bi_danh_da_dung', side_effect=RuntimeError(TEN_MOI)):
                with self.assertRaises(LoiCheVanBan) as loi:
                    che(TEN_MOI, [], self.kho)
            self.assertNotIn(TEN_MOI, str(loi.exception))
            self.assertEqual(self.kho.tra_bi_danh(xu_ly.chuan_hoa(TEN_MOI))['so_lan_gap'], 1)
            self.che_dat(TEN_MOI)
            self.che_dat(TEN_MOI)
        self.assertEqual(self.kho.tra_bi_danh(xu_ly.chuan_hoa(TEN_MOI))['so_lan_gap'], 2)

    def test_loi_ghi_nhan_gap_lai_rollback_khong_lo_cum_goc(self):
        a = self.che_dat(TEN_MOI)
        with patch.object(self.kho, 'ghi_nhan_gap_lai', create=True, side_effect=RuntimeError(TEN_MOI)):
            with self.assertRaises(LoiCheVanBan) as loi:
                che(TEN_MOI, [], self.kho)
        self.assertNotIn(TEN_MOI, str(loi.exception))
        self.assertEqual(set(self.kho._du_lieu.yeu_cau), {a['ma_yeu_cau']})
        self.assertEqual(self.kho.tra_bi_danh(xu_ly.chuan_hoa(TEN_MOI))['so_lan_gap'], 1)

    def test_danh_muc_tu_sinh_theo_nhom_khong_cat_so_lon(self):
        kho = KhoBoNho()
        kho._du_lieu.so = 9999
        muc = kho.them_dinh_danh(CONG_TY, 'CONG_TY')
        self.assertEqual(muc['bi_danh'], '[[MASKCT-10000]]')
        self.assertEqual(self.che_dat(kho=kho)['bi_danh'][0]['nguon'], 'chinh_thuc')

    def test_da_biet_nfc_chu_hoa_va_khoang_trang_tra_dung_danh_muc(self):
        chu = unicodedata.normalize('NFD', 'CÔNG TY DEMO ÁNH   DƯƠNG')
        kq = self.che_dat(chu, [{'gia_tri': CONG_TY, 'nhom': 'CONG_TY'}])
        self.assertEqual(kq['van_ban_da_che'], '[[KH-DEMO-001]]')
        self.assertEqual(kq['cho_duyet']['so_cum_vua_them'], 0)

    def test_khong_chuan_hoa_phan_van_ban_khong_bi_che(self):
        duoi = unicodedata.normalize('NFD', '; thanh toán 1.000.000 VND ngày 30/10/2026.')
        kq = self.che_dat(CONG_TY + duoi)
        self.assertEqual(kq['van_ban_da_che'], '[[KH-DEMO-001]]' + duoi)

    def test_tan_dung_knowntext_che_bien_the_khong_dau(self):
        kq = self.che_dat('cong ty demo anh duong', [{'gia_tri': CONG_TY, 'nhom': 'CONG_TY'}])
        self.assertEqual(kq['van_ban_da_che'], '[[KH-DEMO-001]]')

    def test_ai_sua_hoa_thuong_khoang_trang_tach_tung_ky_tu(self):
        kq = self.che_dat()
        for sua in ('[[kh-demo-001]]', '[[  KH-DEMO-001  ]]',
                    '[ [ k h - d e m o - 0 0 1 ] ]', '[[KH-\nDEMO-\n001]]'):
            with self.subTest(kieu=sua):
                mo = mo_che(sua + '; nội dung AI bổ sung.', kq['ma_yeu_cau'], self.kho)
                self.assertEqual(mo['van_ban_da_mo_che'], CONG_TY + '; nội dung AI bổ sung.')
                self.assertTrue(mo['mo_day_du'])

    def test_mo_bi_danh_tam_sua_hoa_thuong_va_tach_doan(self):
        kq = self.che_dat(TEN_MOI)
        bi_danh = kq['bi_danh'][0]['bi_danh']
        sua = '\n '.join(bi_danh.upper())
        mo = mo_che(sua, kq['ma_yeu_cau'], self.kho)
        self.assertEqual(mo['van_ban_da_mo_che'], TEN_MOI)

    def test_bi_danh_la_tra_vi_tri_khong_doan_khong_tu_dong(self):
        kq = self.che_dat()
        chu = 'nội dung AI\n[[KH-DEMO-001]]; [[KH-DEMO-999]]; [[KH-DEMO-998]]'
        mo = mo_che(chu, kq['ma_yeu_cau'], self.kho, dong_viec=True)
        self.assertFalse(mo['mo_day_du'])
        self.assertEqual(mo['so_cho_mo'], 1)
        self.assertEqual(mo['trang_thai_ma_yeu_cau'], 'DANG_XU_LY')
        self.assertEqual(len(mo['bi_danh_khong_ro']), 2)
        for muc in mo['bi_danh_khong_ro']:
            v = muc['vi_tri']
            self.assertEqual(chu[v['bat_dau']:v['ket_thuc']], muc['bi_danh'])
            self.assertEqual(v['dong'], 2)
        self.assertEqual(mo['bi_danh_khong_ro'][0]['vi_tri']['cot'], 18)
        self.assertIn('[[KH-DEMO-999]]', mo['van_ban_da_mo_che'])

    def test_bi_danh_hong_hoac_thieu_ngoac_khong_bao_mo_day_du(self):
        kq = self.che_dat()
        for chu in ('[[KH-DEMO-00?]]', '[[KH-DEMO-001', '[[KH-DEMO-001]',
                    '[KH-DEMO-001]', 'KH-DEMO-001]]'):
            with self.subTest(chu=chu):
                mo = mo_che(chu, kq['ma_yeu_cau'], self.kho)
                self.assertFalse(mo['mo_day_du'])
                self.assertEqual(mo['so_cho_mo'], 0)
                self.assertEqual(mo['van_ban_da_mo_che'], chu)

    def test_manh_bi_danh_ngoac_le_giu_yeu_cau_mo_va_tra_dung_vi_tri(self):
        for manh in ('[KH-DEMO-001', 'KH-DEMO-001]', '[ K H - D E M O - 0 0 1',
                     'K H - D E M O - 0 0 1 ]', '[MASKTAM-' + 'a' * 32,
                     '[MASKCN-0001', '[KH-DEMO-001; nội dung'):
            with self.subTest(manh=manh):
                kq = self.che_dat()
                chu = '[[KH-DEMO-001]];\n' + manh
                mo = mo_che(chu, kq['ma_yeu_cau'], self.kho, dong_viec=True)
                self.assertFalse(mo['mo_day_du'])
                self.assertEqual(mo['so_cho_mo'], 1)
                self.assertEqual(mo['trang_thai_ma_yeu_cau'], 'DANG_XU_LY')
                self.assertEqual(self.kho.doc_yeu_cau(kq['ma_yeu_cau'])['trang_thai'], 'DANG_XU_LY')
                self.assertEqual(len(mo['bi_danh_khong_ro']), 1)
                muc = mo['bi_danh_khong_ro'][0]
                vi_tri = muc['vi_tri']
                self.assertEqual(chu[vi_tri['bat_dau']:vi_tri['ket_thuc']], muc['bi_danh'])
                self.assertEqual((vi_tri['dong'], vi_tri['cot']), (2, 1))

    def test_manh_bi_danh_co_san_khong_duoc_gui(self):
        for chu in ('[KH-DEMO-001', 'KH-DEMO-001]', '[ K H - D E M O - 0 0 1'):
            with self.subTest(chu=chu):
                kq = che(chu, [], self.kho)
                self.assertFalse(kq['gui_duoc'])
                self.assertIsNone(kq['van_ban_da_che'])

    def test_mo_tra_toan_bang_ke_ca_bi_danh_tam_cu_khong_thuoc_yeu_cau(self):
        cu = '[[MASKTAM-' + 'a' * 32 + ']]'
        kho = KhoBoNho([{'gia_tri': CONG_TY, 'nhom': 'CONG_TY', 'bi_danh_tam': cu}])
        kq = self.che_dat('1.000.000 VND ngày 30/10/2026.', kho=kho)
        mo = mo_che(cu.lower(), kq['ma_yeu_cau'], kho)
        self.assertEqual(mo['van_ban_da_mo_che'], CONG_TY)
        self.assertIn(cu.lower(), kho.doc_yeu_cau(kq['ma_yeu_cau'])['bi_danh_tam_da_dung'])

    def test_mo_tam_cua_yeu_cau_khac_trong_cung_bang(self):
        a = self.che_dat(TEN_MOI)
        b = self.che_dat()
        mo = mo_che(a['van_ban_da_che'], b['ma_yeu_cau'], self.kho)
        self.assertEqual(mo['van_ban_da_mo_che'], TEN_MOI)
        self.assertEqual(len(self.kho.doc_yeu_cau(b['ma_yeu_cau'])['bi_danh_tam_da_dung']), 1)

    def test_ma_sai_thieu_khac_module_khac_nguoi_gui_bi_tu_choi(self):
        kq = self.che_dat()
        for ma, kho in (
                ('', self.kho), ('khong_ton_tai', self.kho), (None, self.kho),
                (kq['ma_yeu_cau'], self.kho.theo_phien(module='demo_khac', nguoi_gui='nguoi_demo_a')),
                (kq['ma_yeu_cau'], self.kho.theo_phien(module='demo_mask', nguoi_gui='nguoi_demo_b'))):
            with self.subTest(ma_sai=ma != kq['ma_yeu_cau']):
                with self.assertRaises(LoiCheVanBan) as loi:
                    mo_che('[[KH-DEMO-001]]', ma, kho)
                self.assertNotIn(CONG_TY, str(loi.exception))

    def test_ma_thuoc_kho_demo_khac_bi_tu_choi(self):
        kq = self.che_dat()
        with self.assertRaises(LoiCheVanBan):
            mo_che(kq['van_ban_da_che'], kq['ma_yeu_cau'], KhoBoNho())

    def test_dong_viec_ro_rang_va_tu_choi_ma_da_dong(self):
        kq = self.che_dat()
        mo = mo_che(kq['van_ban_da_che'], kq['ma_yeu_cau'], self.kho, dong_viec=True)
        self.assertEqual(mo['trang_thai_ma_yeu_cau'], 'DA_DONG')
        with self.assertRaises(LoiCheVanBan):
            mo_che(kq['van_ban_da_che'], kq['ma_yeu_cau'], self.kho)

    def test_khong_tin_co_demo_trong_dinh_danh(self):
        kq = self.che_dat(VAN_BAN, [{'gia_tri': CONG_TY, 'nhom': 'CONG_TY', 'la_demo': False}])
        self.assertIs(self.kho.doc_yeu_cau(kq['ma_yeu_cau'])['la_demo'], True)
        with self.assertRaises(TypeError):
            KhoBoNho(la_demo=False)

    def test_con_sot_da_biet_dinh_vao_chu_khac_thi_chan_khong_lo(self):
        # Số khai trực tiếp bị từ chối theo QD-TAM-03; bảng kho vẫn phải được dò.
        self.kho.them_dinh_danh(SO_GIA, 'MA_SO_THUE')
        kq = che('X' + SO_GIA + 'Y', [], self.kho)
        self.assertFalse(kq['gui_duoc'])
        self.assertTrue(kq['con_sot'])
        self.assertIsNone(kq['van_ban_da_che'])
        self.assertNotIn(SO_GIA, repr(kq))

    def test_kiem_sau_che_bat_con_sot_detector_khong_cho_gui(self):
        phat_hien = xu_ly._phat_hien
        def con_sot(chu):
            cum, day_du = phat_hien(chu)
            if '\x00' in chu:
                cum.append(('dấu vết demo còn lại', 'KHAC'))
            return cum, day_du
        with patch.object(xu_ly, '_phat_hien', side_effect=con_sot):
            kq = che(VAN_BAN, [], self.kho)
        self.assertFalse(kq['gui_duoc'])
        self.assertTrue(kq['con_sot'])
        self.assertNotIn('dấu vết demo còn lại', repr(kq))

    def test_hau_kiem_chan_dinh_danh_chu_thuong_va_mst_co_cham(self):
        for chu, gia_tri, nhom in (
                ('công ty demo ngôi sao', 'công ty demo ngôi sao', 'CONG_TY'),
                ('Họ và tên: nguyễn văn demo', 'nguyễn văn demo', 'CA_NHAN'),
                ('Địa chỉ: số 1 đường demo ánh dương', 'số 1 đường demo ánh dương', 'DIA_CHI'),
                ('MST: 123.456.7890', '123.456.7890', 'MA_SO_THUE')):
            with self.subTest(chu=chu):
                kq = che(chu, [], self.kho)
                self.assertFalse(kq['gui_duoc'])
                self.assertIsNone(kq['van_ban_da_che'])
                self.assertNotIn(gia_tri, repr(kq))
                muc = next(m for m in kq['con_sot'] if m.get('nhom') == nhom)
                v = muc['vi_tri']
                self.assertEqual(chu[v['bat_dau']:v['ket_thuc']], gia_tri)

    def test_hau_kiem_doc_lap_detector_cho_moi_nhan_truong(self):
        for nhan, gia_tri, nhom in (
                ('Họ và tên', 'nguyễn văn demo', 'CA_NHAN'),
                ('Họ tên', 'nguyễn văn demo', 'CA_NHAN'),
                ('Ông', 'nguyễn văn demo', 'CA_NHAN'),
                ('Bà', 'trần thị demo', 'CA_NHAN'),
                ('Ông/Bà', 'nguyễn văn demo', 'CA_NHAN'),
                ('Địa chỉ', 'số 1 đường demo', 'DIA_CHI'),
                ('MST', '123.456.7890', 'MA_SO_THUE'),
                ('Mã số thuế', '1234567890001', 'MA_SO_THUE'),
                ('CCCD', '001234567890', 'GIAY_TO'),
                ('CMND', '001234567', 'GIAY_TO'),
                ('Số tài khoản', '1912345678901', 'TAI_KHOAN'),
                ('STK', '1912345678901', 'TAI_KHOAN'),
                ('Điện thoại', '0900000000', 'DIEN_THOAI')):
            with self.subTest(nhan=nhan), patch.object(xu_ly, '_phat_hien', return_value=([], True)):
                kq = che(nhan + ': ' + gia_tri, [], self.kho)
                self.assertFalse(kq['gui_duoc'])
                self.assertNotIn(gia_tri, repr(kq))
                muc = next(m for m in kq['con_sot'] if m.get('nhom') == nhom)
                self.assertEqual(muc['vi_tri']['bat_dau'], len(nhan) + 2)

    def test_nhan_cuoi_dong_va_gia_tri_nhieu_dong_chan_gui(self):
        for gia_tri, nhom, nhan in (
                ('số 1 đường demo\nphường demo', 'DIA_CHI', 'Địa chỉ'),
                ('nguyễn văn demo', 'CA_NHAN', 'Họ tên'),
                ('123456', 'TAI_KHOAN', 'STK'),
                ('lienhe@example.invalid', 'EMAIL', 'Email')):
            with self.subTest(nhan=nhan), patch.object(xu_ly, '_phat_hien', return_value=([], True)):
                chu = nhan + ':\r\n' + gia_tri + '\n\nNội dung công khai'
                kq = che(chu, [], self.kho)
                self.assertFalse(kq['gui_duoc'])
                self.assertIsNone(kq['van_ban_da_che'])
                muc = next(m for m in kq['con_sot'] if m.get('nhom') == nhom)
                v = muc['vi_tri']
                self.assertEqual(chu[v['bat_dau']:v['ket_thuc']], gia_tri)
                self.assertEqual((v['dong'], v['cot']), (2, 1))
                self.assertNotIn(gia_tri, repr(kq))

    def test_nhan_nhieu_dong_dung_o_nhan_ke_va_khong_an_tien_ngay(self):
        chu = 'Địa chỉ:\nsố 1 đường demo\nphường demo\nSTK:\n123456\n\nTổng tiền: $1000000; ngày 30 tháng 10 năm 2026'
        with patch.object(xu_ly, '_phat_hien', return_value=([], True)):
            kq = che(chu, [], self.kho)
        vung = [(m['nhom'], chu[m['vi_tri']['bat_dau']:m['vi_tri']['ket_thuc']])
                for m in kq['con_sot'] if 'vi_tri' in m]
        self.assertIn(('DIA_CHI', 'số 1 đường demo\nphường demo'), vung)
        self.assertIn(('TAI_KHOAN', '123456'), vung)
        self.assertTrue(kq['kiem_tien_ngay'])

    def test_mau_giay_to_dien_thoai_email_doc_lap_detector(self):
        for gia_tri, nhom in (
                ('123456789', 'GIAY_TO'), ('991234567890', 'GIAY_TO'),
                ('0901234567', 'DIEN_THOAI'), ('+84 901 234 567', 'DIEN_THOAI'),
                ('(024) 3123 4567', 'DIEN_THOAI'),
                ('lienhe@example.invalid', 'EMAIL')):
            with self.subTest(nhom=nhom, gia_tri=gia_tri), \
                    patch.object(xu_ly, '_phat_hien', return_value=([], True)):
                kq = che(gia_tri, [], self.kho)
                self.assertFalse(kq['gui_duoc'])
                muc = next(m for m in kq['con_sot'] if m.get('nhom') == nhom)
                self.assertEqual(muc['vi_tri']['bat_dau'], 0)
                self.assertEqual(muc['vi_tri']['ket_thuc'], len(gia_tri))
        for so in ('123456', '1234567890123456789'):
            with self.subTest(do_dai=len(so)), patch.object(xu_ly, '_phat_hien', return_value=([], True)):
                kq = che('Số tài khoản:\n' + so, [], self.kho)
                self.assertTrue(any(m.get('nhom') == 'TAI_KHOAN' for m in kq['con_sot']))

    def test_hau_kiem_mst_10_13_so_khong_nhan_va_khong_nham_tien(self):
        for gia_tri in ('1234567890', '123.456.7890', '123-456-7890',
                        '1234567890001', '123.456.7890-001', '123 456 7890 001',
                        '123.456.789.0', '123.456.789.000.1'):
            with self.subTest(gia_tri=gia_tri), patch.object(xu_ly, '_phat_hien', return_value=([], True)):
                kq = che(gia_tri, [], self.kho)
                self.assertFalse(kq['gui_duoc'])
                self.assertTrue(any(m.get('nhom') == 'MA_SO_THUE' for m in kq['con_sot']))
        self.che_dat('tổng tiền 1000000000 VND; ngày 30/10/2026')

    def test_khong_mat_dau_cong_ty_khi_che_tien_to_ten_chu_thuong(self):
        kq = che('công ty demo ánh dương ngôi sao', [], self.kho)
        self.assertFalse(kq['gui_duoc'])
        self.assertIsNone(kq['van_ban_da_che'])
        self.assertTrue(any(m.get('nhom') == 'CONG_TY' for m in kq['con_sot']))

    def test_hau_kiem_vi_tri_nfd_sau_bi_danh_va_gia_tri_che_roi(self):
        gia_tri = unicodedata.normalize('NFD', 'nguyễn văn demo')
        chu = CONG_TY + ';\nHọ tên: ' + gia_tri
        with patch.object(xu_ly, '_phat_hien', return_value=([], True)):
            kq = che(chu, [], self.kho)
        muc = next(m for m in kq['con_sot'] if m.get('nhom') == 'CA_NHAN')
        ban_che = '[[KH-DEMO-001]];\nHọ tên: ' + gia_tri
        v = muc['vi_tri']
        self.assertEqual(ban_che[v['bat_dau']:v['ket_thuc']], gia_tri)
        self.assertEqual((v['dong'], v['cot']), (2, 9))
        self.che_dat('Họ tên: ' + CONG_TY)

    def test_thieu_tai_nguyen_khong_tu_coi_la_kiem_het(self):
        with patch.object(detectors, 'places', side_effect=FileNotFoundError('không in ' + TEN_MOI)):
            kq = che(VAN_BAN, [], self.kho)
        self.assertFalse(kq['gui_duoc'])
        self.assertIsNone(kq['van_ban_da_che'])
        self.assertTrue(kq['con_sot'])
        self.assertNotIn(TEN_MOI, repr(kq))

    def test_ngoai_le_detector_khong_bao_dat_gia(self):
        with patch.object(detectors, 'detect', side_effect=RuntimeError(TEN_MOI)):
            kq = che(VAN_BAN, [], self.kho)
        self.assertFalse(kq['gui_duoc'])
        self.assertNotIn(TEN_MOI, repr(kq))

    def test_tu_choi_dinh_danh_da_biet_co_dang_tien_ngay(self):
        for gia_tri in ('0.00', '0,00', '0.000', '1.000.000', '30/10/2026',
                        '30-10-2026', '30.10.2026', '1000000 VND', '1000000'):
            with self.subTest(loai=gia_tri):
                with self.assertRaisesRegex(LoiCheVanBan, 'tiền|ngày') as loi:
                    che('giá trị ' + gia_tri, [{'gia_tri': gia_tri, 'nhom': 'KHAC'}], self.kho)
                self.assertNotIn(gia_tri, str(loi.exception))
        self.assertEqual(self.kho._du_lieu.yeu_cau, {})

    def test_dinh_danh_khai_so_tien_ky_hieu_va_ngay_chu_bi_tu_choi_truoc_giao_dich(self):
        for gia_tri in ('$1000000', '₫1000000', 'đ1000000', 'VND 1000000',
                        'USD1000000', '1000000₫', '1000000đ', '1000000USD',
                        '001234567890', '123456', '1 234 567', '1; 2', '+1,234.50', '1_234',
                        'ngày 30 tháng 10 năm 2026', '30 tháng 10'):
            with self.subTest(gia_tri=gia_tri), patch.object(self.kho, 'giao_dich') as giao_dich:
                with self.assertRaisesRegex(LoiCheVanBan, 'tiền|ngày') as loi:
                    che('nội dung', [{'gia_tri': gia_tri, 'nhom': 'KHAC'}], self.kho)
                self.assertNotIn(gia_tri, str(loi.exception))
                giao_dich.assert_not_called()

    def test_so_tap_tien_ky_hieu_va_ngay_viet_chu(self):
        for gia_tri in ('$1000000', '$1 000 000', '₫1000000', '1000000đ', 'USD1000000', '2026-10-30',
                        'ngày 30 tháng 10 năm 2026', '30 tháng 10'):
            with self.subTest(gia_tri=gia_tri):
                goc = gia_tri + '; ' + gia_tri
                self.assertFalse(xu_ly._kiem_tien_ngay(goc, gia_tri))
                self.assertFalse(xu_ly._kiem_tien_ngay(gia_tri, goc))
                self.assertFalse(xu_ly._kiem_tien_ngay(gia_tri, gia_tri.replace('0', '1', 1)))
                self.assertTrue(xu_ly._kiem_tien_ngay(goc, goc + '; [[KH-DEMO-001]]'))

    def test_mat_tien_ky_hieu_hoac_ngay_chu_chan_gui_ke_ca_kho_cu(self):
        for gia_tri in ('$1000000', 'ngày 30 tháng 10 năm 2026', '30 tháng 10'):
            with self.subTest(gia_tri=gia_tri), \
                    patch.object(self.kho, 'liet_ke_dinh_danh', return_value=[{'gia_tri': gia_tri, 'nhom': 'KHAC'}]), \
                    patch.object(self.kho, 'tra_bi_danh', return_value=self.kho.tra_bi_danh(xu_ly.chuan_hoa(CONG_TY))), \
                    patch.object(xu_ly, '_phat_hien', return_value=([], True)), \
                    patch.object(xu_ly, '_vung_tien_ngay', return_value=detectors.Spans()):
                kq = che(gia_tri, [], self.kho)
                self.assertFalse(kq['kiem_tien_ngay'])
                self.assertFalse(kq['gui_duoc'])
                self.assertIsNone(kq['van_ban_da_che'])

    def test_tien_ky_hieu_ngay_chu_duoc_bao_ve_khi_detector_chon_nham(self):
        for gia_tri in ('$1000000', 'ngày 30 tháng 10 năm 2026', '30 tháng 10'):
            with self.subTest(gia_tri=gia_tri), \
                    patch.object(xu_ly, '_phat_hien', side_effect=[([(gia_tri, 'KHAC')], True), ([], True)]):
                kq = self.che_dat(gia_tri)
                self.assertEqual(kq['van_ban_da_che'], gia_tri)
                self.assertEqual(kq['so_cho_thay'], 0)

    def test_manh_bi_danh_chuan_hoa_ngoac_le_ky_tu_hong_va_mat_ngoac(self):
        for manh in ('K H - D E M O - 0 0 1', 'KH-DEMO-001',
                     'K H - D E M O - 0 0 ? ]', '[ ? H - D E M O - 0 0 1',
                     'M A S K C N - 0 0 ? ]', '[ M A S K T A M - a ? b',
                     'K H - D E M O - 0 0 ? ] ]', '] K H - D E M O - 0 0 1',
                     'K H - D E M O - 0 0 1 ['):
            with self.subTest(manh=manh):
                kq = self.che_dat()
                chu = '[[KH-DEMO-001]];\n' + manh
                mo = mo_che(chu, kq['ma_yeu_cau'], self.kho, dong_viec=True)
                self.assertFalse(mo['mo_day_du'])
                self.assertEqual(mo['so_cho_mo'], 1)
                self.assertEqual(mo['trang_thai_ma_yeu_cau'], 'DANG_XU_LY')
                self.assertEqual(self.kho.doc_yeu_cau(kq['ma_yeu_cau'])['trang_thai'], 'DANG_XU_LY')
                self.assertEqual(mo['van_ban_da_mo_che'], CONG_TY + ';\n' + manh)
                muc = mo['bi_danh_khong_ro'][0]
                v = muc['vi_tri']
                self.assertEqual(chu[v['bat_dau']:v['ket_thuc']], manh)
                self.assertEqual(muc['bi_danh'], manh)
                self.assertEqual((v['dong'], v['cot']), (2, 1))

    def test_mo_khong_coi_van_xuoi_va_ma_chua_cap_la_bi_danh(self):
        kq = self.che_dat()
        chu = 'Nội dung AI bổ sung; mã KH-DEMO-999 đã công khai.'
        mo = mo_che(chu, kq['ma_yeu_cau'], self.kho, dong_viec=True)
        self.assertTrue(mo['mo_day_du'])
        self.assertEqual(mo['trang_thai_ma_yeu_cau'], 'DA_DONG')

    def _kiem_manh_hong_khong_dong_viec(self, cac_manh):
        for manh in cac_manh:
            with self.subTest(manh=manh):
                kq = self.che_dat()
                chu = '[[KH-DEMO-001]];\n' + manh
                mo = mo_che(chu, kq['ma_yeu_cau'], self.kho, dong_viec=True)
                self.assertFalse(mo['mo_day_du'])
                self.assertEqual(mo['so_cho_mo'], 1)
                self.assertEqual(mo['van_ban_da_mo_che'], CONG_TY + ';\n' + manh)
                self.assertEqual(mo['trang_thai_ma_yeu_cau'], 'DANG_XU_LY')
                self.assertEqual(self.kho.doc_yeu_cau(kq['ma_yeu_cau'])['trang_thai'], 'DANG_XU_LY')
                self.assertEqual(mo['bi_danh_khong_ro'], [{
                    'bi_danh': manh, 'vi_tri': {
                        'bat_dau': len('[[KH-DEMO-001]];\n'), 'ket_thuc': len(chu),
                        'dong': 2, 'cot': 1}}])

    def test_manh_khong_ngoac_ky_tu_la_thay_mot_ky_tu(self):
        self._kiem_manh_hong_khong_dong_viec((
            'KH-DEMO-00?', '?H-DEMO-001', 'KH-D?MO-001',
            'KH-DEMO-00\ufffd', 'KH-D*MO-001'))

    def test_manh_khong_ngoac_ky_tu_la_chen(self):
        self._kiem_manh_hong_khong_dong_viec((
            'KH-DEMO-00?1', 'K?H-DEMO-001', 'KH-DEMO-00\ufffd1',
            'KH-DEMO-00*1'))

    def test_manh_khong_ngoac_khoang_trang_chen_va_ky_tu_hong(self):
        self._kiem_manh_hong_khong_dong_viec((
            'K H - D E M O - 0 0 1', 'K H - D E M O - 0 0 ?',
            'K H - D E M O - 0 0 ? 1', 'KH-\tDEMO-\u00a000?1'))

    def test_manh_mot_ngoac_va_dau_hoi_khong_dong_viec(self):
        self._kiem_manh_hong_khong_dong_viec((
            '[KH-DEMO-00?', 'KH-DEMO-00?1]', '[K H - D E M O - 0 0 ? 1'))

    def test_ma_tran_hong_chua_cap_va_van_xuoi_khong_bi_bat_nham(self):
        for chu in ('Nội dung AI bổ sung; KH-DEMO-99?; KH-DEMO-99?9.',
                    'Nội dung AI bổ sung; K H - D E M O - 9 9 ? 9.',
                    'Nội dung AI bổ sung; MASKCN-00?1; MASKTAM-ab?cd.',
                    'Nội dung AI bổ sung; KH-DEMO-00?9.',
                    'Nội dung AI bổ sung; XKH-DEMO-00?.',
                    'Nội dung AI bổ sung; KH-DEMO-00?XYZ.',
                    'Nội dung AI bổ sung; mã KH-DEMO-00x đã công khai.'):
            with self.subTest(chu=chu):
                kq = self.che_dat()
                mo = mo_che(chu, kq['ma_yeu_cau'], self.kho, dong_viec=True)
                self.assertTrue(mo['mo_day_du'])
                self.assertEqual(mo['so_cho_mo'], 0)
                self.assertEqual(mo['bi_danh_khong_ro'], [])
                self.assertEqual(mo['van_ban_da_mo_che'], chu)
                self.assertEqual(mo['trang_thai_ma_yeu_cau'], 'DA_DONG')

    def test_manh_tam_mat_ngoac_va_ngay_chu_nfd(self):
        kq = self.che_dat(TEN_MOI)
        manh = ' \n'.join(kq['bi_danh'][0]['bi_danh'][2:-2].upper())
        mo = mo_che(manh, kq['ma_yeu_cau'], self.kho, dong_viec=True)
        self.assertFalse(mo['mo_day_du'])
        self.assertEqual(mo['bi_danh_khong_ro'][0]['bi_danh'], manh)
        self.assertEqual(mo['trang_thai_ma_yeu_cau'], 'DANG_XU_LY')
        ngay = unicodedata.normalize('NFD', 'ngày 30 tháng 10 năm 2026')
        self.assertFalse(xu_ly._kiem_tien_ngay(ngay, 'nội dung'))

    def test_hieu_nang_ba_chuoi_benh_ly_500_nghin_ky_tu(self):
        mau_con = os.environ.get('MASK_3A_MAU_HIEU_NANG')
        if mau_con is not None:
            chu = (mau_con * (500_000 // len(mau_con) + 1))[:500_000]
            bat_dau = perf_counter()
            kq = che(chu, [], KhoBoNho())
            giay = perf_counter() - bat_dau
            self.assertLessEqual(giay, 5, f'{mau_con!r}: {giay:.3f} giây')
            self.assertTrue(kq['kiem_tien_ngay'])
            self.assertEqual(kq['so_cho_thay'], 0)
            if mau_con == '1 ':
                self.assertFalse(kq['gui_duoc'])
                self.assertIsNone(kq['van_ban_da_che'])
                self.assertIn({'nhom': 'TAI_KHOAN', 'vi_tri': {
                    'bat_dau': 0, 'ket_thuc': 499_999, 'dong': 1, 'cot': 1}}, kq['con_sot'])
                self.assertTrue(all('nhom' in m for m in kq['con_sot']))
            else:
                self.assertTrue(kq['gui_duoc'])
                self.assertEqual(kq['van_ban_da_che'], chu)
                self.assertEqual(kq['con_sot'], [])
            print(f'Hiệu năng {mau_con!r}: {giay:.3f} giây')
            return
        # Chỉ tiến trình test con bị giới hạn; không thao tác dịch vụ/PG.
        for mau in ('1; ', '1, ', '1 '):
            with self.subTest(mau=mau):
                moi_truong = dict(os.environ, MASK_3A_MAU_HIEU_NANG=mau)
                try:
                    chay = subprocess.run(
                        [sys.executable, '-X', 'utf8', '-B', '-m', 'unittest', 'discover',
                         '-s', str(Path(__file__).parent), '-p', Path(__file__).name,
                         '-k', 'test_hieu_nang_ba_chuoi_benh_ly_500_nghin_ky_tu'],
                        env=moi_truong, capture_output=True, text=True, encoding='utf-8', timeout=12)
                except subprocess.TimeoutExpired:
                    self.fail(f'{mau!r}: vượt 12 giây kể cả khởi tạo tiến trình; ngưỡng xử lý là 5 giây')
                self.assertEqual(chay.returncode, 0, chay.stdout + chay.stderr)
                print(chay.stdout.strip())

    def test_so_dai_sau_che_cong_ty_van_chan_va_giu_toa_do_nfc_nfd(self):
        so = ('1 ' * 200).rstrip()
        for ten in (CONG_TY, unicodedata.normalize('NFD', CONG_TY)):
            with self.subTest(nfd=ten != CONG_TY):
                kq = che(ten + ';\n' + so + ';\n' + so, [], self.kho)
                self.assertFalse(kq['gui_duoc'])
                self.assertIsNone(kq['van_ban_da_che'])
                self.assertTrue(kq['kiem_tien_ngay'])
                self.assertEqual(kq['so_cho_thay'], 1)
                ban_che = '[[KH-DEMO-001]];\n' + so + ';\n' + so
                vung = [m['vi_tri'] for m in kq['con_sot'] if m.get('nhom') == 'TAI_KHOAN']
                self.assertEqual(len(vung), 2)
                self.assertEqual([(v['dong'], v['cot']) for v in vung], [(2, 1), (3, 1)])
                for v in vung:
                    self.assertEqual(ban_che[v['bat_dau']:v['ket_thuc']], so)

    def test_quyet_dinh_tien_ngay_giu_dang_phan_cach_lien_tiep(self):
        for so in ('1.,2', '1..2', '0,.0', '1,,2', '+1.,2', '-0..0'):
            with self.subTest(so=so):
                self.assertEqual(xu_ly._cac_tien_ngay(so), [(0, len(so), 'tien', so)])
                self.assertFalse(xu_ly._kiem_tien_ngay(so, ''))
                self.assertFalse(xu_ly._kiem_tien_ngay(so, so + '; ' + so))
                self.assertTrue(xu_ly._kiem_tien_ngay(so, so))

    def test_cum_so_dai_khop_nhu_loi_voi_bien_the_va_vung_chong_nhau(self):
        gia_tri = ' '.join(['1'] * 161)
        cac_dang = (gia_tri, gia_tri.replace(' ', ''), gia_tri.replace(' ', ' / '),
                    gia_tri.replace(' ', '\t'), gia_tri.replace(' ', '    '),
                    gia_tri.replace(' ', ' \u00a0 '), gia_tri.replace(' ', '\n'),
                    '1 ' * 10 + gia_tri + ' 1' * 10,
                    'X' + gia_tri + 'Y', 'X' + gia_tri.replace(' ', '    ') + 'Y')
        for dang in cac_dang:
            for loose, boundary, masking in ((False, True, False), (True, True, False),
                                              (True, False, False), (True, False, True)):
                with self.subTest(dang=dang[:12], loose=loose, boundary=boundary, masking=masking):
                    chu = 'nội dung; ' + dang + '; kết thúc'
                    cu = xu_ly.core.KnownText(chu).spans(gia_tri, loose, boundary, masking)
                    moi = xu_ly._BoDo(chu).spans(gia_tri, loose, boundary, masking)
                    self.assertEqual(moi, cu)

    def test_cum_dai_it_chu_so_khong_tu_mo_rong_cach_viet(self):
        for dau in (' ', '.', ','):
            gia_tri = '1' + dau * 300 + '2'
            chu = gia_tri + '; 12; 1 2'
            with self.subTest(dau=dau):
                cu = xu_ly.core.KnownText(chu).spans(gia_tri, boundary=False)
                self.assertEqual(xu_ly._BoDo(chu).spans(gia_tri, boundary=False), cu)
                self.assertIn((0, len(gia_tri)), cu)
                vi_tri_so_lien = chu.index('12')
                self.assertNotIn((vi_tri_so_lien, vi_tri_so_lien + 2), cu)

    def test_bo_cum_dai_van_giu_thu_tu_uu_tien_khi_trung_chuan_hoa(self):
        dai = 'Công' + ' ' * 301 + 'ty DEMO'
        ngan = 'Công ty DEMO'
        with patch.object(xu_ly, '_phat_hien', return_value=(
                [(dai, 'CONG_TY'), (ngan, 'CONG_TY')], True)):
            kq = che(ngan, [], self.kho)
        self.assertEqual(kq['so_cho_thay'], 0)
        self.assertFalse(kq['gui_duoc'])
        self.assertTrue(kq['kiem_tien_ngay'])

    def test_tien_ngay_so_goc_khong_duoc_loai_vung_da_che_khoi_phep_so(self):
        gia_tri = 'dữ liệu demo 0.00 ngày 30/10/2026'
        muc = self.kho.tra_bi_danh(xu_ly.chuan_hoa(CONG_TY))
        # Mô phỏng kho cũ có mục sai và bỏ lọt lớp bảo vệ: hậu kiểm vẫn phải chặn.
        with patch.object(self.kho, 'liet_ke_dinh_danh', return_value=[{'gia_tri': gia_tri, 'nhom': 'KHAC'}]), \
                patch.object(self.kho, 'tra_bi_danh', return_value=muc), \
                patch.object(xu_ly, '_vung_tien_ngay', return_value=detectors.Spans()):
            kq = che(gia_tri, [], self.kho)
        self.assertFalse(kq['kiem_tien_ngay'])
        self.assertFalse(kq['gui_duoc'])
        self.assertIsNone(kq['van_ban_da_che'])

    def test_tien_khong_va_ngay_khong_bi_detector_che_mat(self):
        self.che_dat('giá trị 0.00; 0,00; 0.000; 30/10/2026')

    def test_so_tap_tien_ngay_giu_ca_gia_tri_va_so_lan(self):
        goc = '0.00; 0,00; 0.000; 1.000.000 VND; 30/10/2026; 30/10/2026'
        for sau in (goc.replace('0.00;', '', 1), goc.replace('0,00', '0,01'),
                    goc + '; 0.000', goc.replace('; 30/10/2026', '', 1)):
            with self.subTest(sau=sau):
                self.assertFalse(xu_ly._kiem_tien_ngay(goc, sau))
        self.assertTrue(xu_ly._kiem_tien_ngay(goc, goc + '; [[KH-DEMO-001]]'))

    def test_kiem_tien_ngay_khong_dat_thi_chan_gui_ke_ca_khong_con_sot(self):
        with patch.object(xu_ly.core, 'numeric_review', return_value={'changed': True}):
            kq = che(VAN_BAN, [], self.kho)
        self.assertFalse(kq['kiem_tien_ngay'])
        self.assertEqual(kq['con_sot'], [])
        self.assertFalse(kq['gui_duoc'])
        self.assertIsNone(kq['van_ban_da_che'])

    def test_so_tien_lien_khong_bi_che_va_tai_khoan_van_che(self):
        chu = 'tổng tiền 1000000000 VND; tài khoản: 1912345678901 VND; 30/10/2026'
        kq = self.che_dat(chu)
        self.assertIn('1000000000 VND', kq['van_ban_da_che'])
        self.assertNotIn('1912345678901', kq['van_ban_da_che'])
        self.assertIn('30/10/2026', kq['van_ban_da_che'])

    def test_ma_so_thue_email_dien_thoai_va_dia_chi_demo(self):
        chu = 'MST: 001234567890; email: lienhe@example.invalid; ĐT: 0900000000; Địa chỉ: Số 1 đường DEMO Ánh Dương'
        kq = self.che_dat(chu)
        for gia_tri in (SO_GIA, 'lienhe@example.invalid', '0900000000', 'Số 1 đường DEMO Ánh Dương'):
            self.assertNotIn(gia_tri, repr(kq))
        self.assertGreaterEqual(kq['so_cho_thay'], 4)

    def test_tran_van_ban_chap_nhan_dung_500_nghin_tu_choi_vuot(self):
        chu = ('nội dung ' * 55_556)[:500_000]
        kq = self.che_dat(chu)
        self.assertEqual(len(kq['van_ban_da_che']), 500_000)
        for ham in (lambda: che('x' * 500_001, [], self.kho),
                    lambda: mo_che('x' * 500_001, kq['ma_yeu_cau'], self.kho)):
            with self.assertRaises(LoiCheVanBan):
                ham()

    def test_khoi_lien_rong_500_nghin_khong_treo_khong_bao_dat_gia(self):
        kq = che('x' * 500_000, [], self.kho)
        self.assertFalse(kq['gui_duoc'])
        self.assertIsNone(kq['van_ban_da_che'])
        self.assertTrue(kq['con_sot'])

    def test_tran_500_dinh_danh_khong_cat_ngam(self):
        danh_sach = [{'gia_tri': 'mục demo ' + str(i), 'nhom': 'KHAC'} for i in range(500)]
        self.che_dat('nội dung', danh_sach)
        with self.assertRaises(LoiCheVanBan):
            che('nội dung', danh_sach + danh_sach[:1], self.kho)

    def test_detector_hon_500_cum_khong_bi_cat_theo_tran_da_biet(self):
        dia_chi = ['demo' + str(i) + '@example.invalid' for i in range(501)]
        kq = self.che_dat('; '.join(dia_chi))
        self.assertEqual(kq['so_cho_thay'], 501)
        self.assertEqual(kq['cho_duyet']['so_cum_vua_them'], 501)
        self.assertEqual(len(kq['bi_danh']), 501)
        self.assertNotIn('@example.invalid', repr(kq))

    def test_tran_gia_tri_va_nhom_tu_choi_khong_lo_dinh_danh(self):
        self.che_dat('nội dung', [{'gia_tri': 'x' * 300, 'nhom': 'KHAC'}])
        for muc in ({'gia_tri': 'x' * 301, 'nhom': 'KHAC'},
                    {'gia_tri': CONG_TY, 'nhom': 'x' * 21},
                    {'gia_tri': CONG_TY, 'nhom': 'nhóm lạ'},
                    {'gia_tri': '[[KH-DEMO-001]]', 'nhom': 'KHAC'}):
            with self.assertRaises(LoiCheVanBan) as loi:
                che(VAN_BAN, [muc], self.kho)
            self.assertNotIn(CONG_TY, str(loi.exception))

    def test_dau_vao_sai_kieu_rong_va_xung_dot_nhom(self):
        for chu, ds in ((None, []), ('', []), ('  \n', []), (VAN_BAN, {}),
                        (VAN_BAN, [None]), (VAN_BAN, [{'gia_tri': CONG_TY, 'nhom': 'CONG_TY'},
                                                    {'gia_tri': CONG_TY, 'nhom': 'CA_NHAN'}])):
            with self.assertRaises(LoiCheVanBan):
                che(chu, ds, self.kho)

    def test_loi_kho_rollback_khong_lo_dinh_danh(self):
        with patch.object(self.kho, 'ghi_bi_danh_da_dung', side_effect=RuntimeError(TEN_MOI)):
            with self.assertRaises(LoiCheVanBan) as loi:
                che(TEN_MOI, [], self.kho)
        self.assertNotIn(TEN_MOI, str(loi.exception))
        self.assertEqual(self.kho.so_cum_cho_duyet(), 0)
        self.assertEqual(self.kho._du_lieu.yeu_cau, {})

    def test_loi_kho_mo_khong_lo_driver_hay_dinh_danh(self):
        kq = self.che_dat()
        with patch.object(self.kho, 'tra_dinh_danh', side_effect=RuntimeError(CONG_TY)):
            with self.assertRaises(LoiCheVanBan) as loi:
                mo_che(kq['van_ban_da_che'], kq['ma_yeu_cau'], self.kho)
        self.assertNotIn(CONG_TY, str(loi.exception))

    def test_bi_danh_co_san_trong_dau_vao_khong_bao_kiem_dat(self):
        kq = che('[[KH-DEMO-001]]', [], self.kho)
        self.assertFalse(kq['gui_duoc'])
        self.assertIsNone(kq['van_ban_da_che'])

    def test_khong_luu_gia_tri_khong_xuat_hien_vao_cho(self):
        kq = self.che_dat(VAN_BAN, [{'gia_tri': TEN_MOI, 'nhom': 'CONG_TY'}])
        self.assertEqual(kq['cho_duyet']['so_cum_vua_them'], 0)
        self.assertEqual(self.kho.so_cum_cho_duyet(), 0)

    def test_chuan_hoa_khop_mask_2_va_khong_trung_ma_junsky(self):
        from tools.chuyen_danh_muc_mask import chuan_hoa
        for chu in (CONG_TY.upper(), '  DEMO\u001c\u00a0Ánh\tDương  ', unicodedata.normalize('NFD', CONG_TY)):
            self.assertEqual(xu_ly.chuan_hoa(chu), chuan_hoa(chu))
        for ma in ('MASKDEMO', 'mask-demo', 'KH-DEMO-001'):
            with self.assertRaises(ValueError):
                self.kho.them_dinh_danh(TEN_MOI, 'CONG_TY', ma_junsky=ma)


if __name__ == '__main__':
    unittest.main()
