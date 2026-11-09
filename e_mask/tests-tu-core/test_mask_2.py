"""MASK-2: chỉ dữ liệu tự sinh DEMO; PostgreSQL do lead chủ động chạy."""
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import tempfile
import unicodedata
import unittest
from uuid import uuid4

from tools import chuyen_danh_muc_mask as cm


GOC = Path(__file__).resolve().parents[1]
SQL_PATH = GOC / 'src/kho_tri_thuc/core/sql/113_mask_dinh_danh.sql'
CHU_VIET = (
    ('À Á Ả Ã Ạ', 'à á ả ã ạ'),
    ('Ă Ằ Ắ Ẳ Ẵ Ặ', 'ă ằ ắ ẳ ẵ ặ'),
    ('Â Ầ Ấ Ẩ Ẫ Ậ', 'â ầ ấ ẩ ẫ ậ'),
    ('Đ đ', 'đ đ'),
    ('È É Ẻ Ẽ Ẹ', 'è é ẻ ẽ ẹ'),
    ('Ê Ề Ế Ể Ễ Ệ', 'ê ề ế ể ễ ệ'),
    ('Ì Í Ỉ Ĩ Ị', 'ì í ỉ ĩ ị'),
    ('Ò Ó Ỏ Õ Ọ', 'ò ó ỏ õ ọ'),
    ('Ô Ồ Ố Ổ Ỗ Ộ', 'ô ồ ố ổ ỗ ộ'),
    ('Ơ Ờ Ớ Ở Ỡ Ợ', 'ơ ờ ớ ở ỡ ợ'),
    ('Ù Ú Ủ Ũ Ụ', 'ù ú ủ ũ ụ'),
    ('Ư Ừ Ứ Ử Ữ Ự', 'ư ừ ứ ử ữ ự'),
    ('Ỳ Ý Ỷ Ỹ Ỵ', 'ỳ ý ỷ ỹ ỵ'),
)


class LoiDEMOCSDL(Exception):
    def __init__(self, state):
        self.sqlstate = state
        super().__init__('CANARY_DEMO_GIA_TRI_DSN')


class KetNoiDEMO:
    """Mock transaction/savepoint, không nối mạng hoặc gọi driver."""
    def __init__(self):
        self.dong = []
        self.lenh = []
        self.co_demo = None
        self.ket_qua = None
        self.loi = None

    @contextmanager
    def transaction(self):
        cu = deepcopy((self.dong, self.co_demo))
        try:
            yield
        except Exception:
            self.dong, self.co_demo = cu
            raise

    def execute(self, sql, params=()):
        self.lenh.append((sql, params))
        if 'set_config' in sql:
            cu = self.co_demo
            self.co_demo = params[0]
            self.ket_qua = (cu,)
        elif 'current_setting' in sql:
            self.ket_qua = (self.co_demo,)
        elif 'count(*)' in sql:
            self.ket_qua = (sum(d['la_demo'] == params[0] for d in self.dong),)
        elif sql.startswith('SELECT EXISTS'):
            self.ket_qua = (any(d['la_demo'] == params[0] and d['ma_junsky'] is not None
                               and ('[['+d['ma_junsky']+']]').lower() == params[1].lower()
                               for d in self.dong),)
        elif sql.lstrip().startswith('SELECT'):
            found = next((d for d in self.dong if d['la_demo'] == params[0]
                          and cm.chuan_hoa(d['gia_tri']) == cm.chuan_hoa(params[1])), None)
            self.ket_qua = (found['nhom'], found['ma_junsky']) if found else None
        elif sql.lstrip().startswith('INSERT'):
            loi = self.loi.pop(0) if isinstance(self.loi, list) else self.loi
            if loi:
                raise LoiDEMOCSDL(loi)
            gia_tri, nhom, ma, demo = params
            if any(d['la_demo'] == demo and cm.chuan_hoa(d['gia_tri']) == cm.chuan_hoa(gia_tri)
                   for d in self.dong):
                raise LoiDEMOCSDL('23505')
            self.dong.append(dict(gia_tri=gia_tri, nhom=nhom, ma_junsky=ma, la_demo=demo))
        else:
            raise AssertionError('Mock gặp SQL chưa được mô tả')
        return self

    def fetchone(self):
        return self.ket_qua


def muc_demo(**sua):
    return dict(source='Công ty DEMO Ánh Dương', category='CONG_TY',
                token='[CONG_TY_001]', enabled=True, **sua)


def duyet_module_demo(test, owner):
    from kho_tri_thuc.core import kich_hoat
    from test_g2_24 import GoiDemoTests

    # Cùng fixture và cửa provisioning G2-25: Core tự tạo vai/schema/helper
    # và cấp quyền runtime đầy đủ, không phụ thuộc module đã có của bộ chạy.
    fixture = GoiDemoTests(methodName='runTest')
    test.addCleanup(fixture.doCleanups)
    fixture.setUp()
    ma_module = 'mask_demo_'+uuid4().hex[:8]
    fixture.manifest['ma'] = ma_module
    fixture.manifest['giao_dien']['trang_dau'] = '#'+ma_module+'/chinh'
    fixture.manifest['du_lieu_rieng']['goi_migration']['ma'] = ma_module
    fixture.manifest['contract']['cong_bo'] = []
    fixture.manifest['cong_bo'] = []
    fixture.save_manifest()
    bao_cao = fixture.stage()
    test.assertEqual(bao_cao.ket_luan, 'DAT', bao_cao.ly_do)
    kich_hoat.duyet_goi(owner, bao_cao, phien_ban_core='1.0.0')
    return ma_module


def chay_lai_chuoi_mask(conn):
    # Không dùng bộ chạy có checksum: các ca này chủ ý áp lại từng DDL.
    for name in ('113_mask_dinh_danh.sql', '117_mask_duyet_cho.sql', '118_mask_phien.sql'):
        try:
            conn.execute((SQL_PATH.parent / name).read_bytes().decode('utf-8', errors='strict'))
        except Exception as exc:
            # Chỉ SQL migration cố định, không in SQL/bind/DSN hay cấu hình.
            diag = getattr(exc, 'diag', None)
            raise AssertionError(f'{name}: sqlstate={getattr(exc, "sqlstate", None)}; '
                                 f'message_primary={getattr(diag, "message_primary", None)}') from None


class ChuyenDanhMucTests(unittest.TestCase):
    def setUp(self):
        self.tmp = self.enterContext(tempfile.TemporaryDirectory(prefix='mask2_demo_'))
        self.tep = Path(self.tmp) / 'danh_muc_DEMO.json'
        self.db = KetNoiDEMO()
        self.db.co_demo = 'true'

    def ghi(self, data):
        self.tep.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    def chuyen(self, data, **kwargs):
        self.ghi(data)
        return cm.chuyen_danh_muc(self.tep, self.db, la_demo=True, **kwargs)

    def test_chuan_hoa_nfc_hoa_thuong_va_khoang_trang(self):
        self.assertEqual(cm.chuan_hoa('  CÔNG\tTY\nDEMO A\u0301nh  Dương '),
                         cm.chuan_hoa('công ty demo ánh dương'))

    def test_chuan_hoa_chu_viet_co_dau_ke_ca_d_va_dang_tach_dau(self):
        for hoa, thuong in CHU_VIET:
            for dang in ('NFC', 'NFD'):
                with self.subTest(chu=hoa, dang=dang):
                    gia_tri = unicodedata.normalize(dang, hoa)
                    self.assertEqual(cm.chuan_hoa(' \t'+gia_tri+'\n '), thuong)
                    self.assertEqual(cm.chuan_hoa(thuong), thuong)

    def test_chuan_hoa_cung_tap_khoang_trang_sql_ke_ca_dau_tach_nhom(self):
        sql = SQL_PATH.read_text(encoding='utf-8')
        mau_sql = re.search(r"U&'(\[[^']+\]\+)'", sql).group(1)
        mau_sql = re.sub(r'\\([0-9A-Fa-f]{4})', lambda m: chr(int(m[1], 16)), mau_sql)
        khoang_trang = ('\t\n\v\f\r\x1c\x1d\x1e\x1f \x85\xa0\u1680'
                        '\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007'
                        '\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000')
        for ky_tu in khoang_trang:
            with self.subTest(ma=ord(ky_tu)):
                gia_tri = ky_tu+'ĐÔ'+ky_tu*2+'THỊ'+ky_tu
                self.assertEqual(cm.chuan_hoa(gia_tri), 'đô thị')
                self.assertEqual(re.sub(mau_sql, ' ', gia_tri).strip(' ').lower(), 'đô thị')
        # Ký tự liền kề nhưng không thuộc tập khoảng trắng phải được giữ nguyên.
        for ky_tu in ('\x1b', '\u200b', '\u2060'):
            with self.subTest(ma=ord(ky_tu)):
                self.assertEqual(cm.chuan_hoa('ĐÔ'+ky_tu+'THỊ'), 'đô'+ky_tu+'thị')
                self.assertIsNone(re.search(mau_sql, ky_tu))

    def test_dau_tach_nhom_duoc_nhan_dien_trung_khi_chay_lai(self):
        self.chuyen([muc_demo()], chay_thu=False)
        for ky_tu in ('\x1c', '\x1d', '\x1e', '\x1f'):
            with self.subTest(ma=ord(ky_tu)):
                kq = self.chuyen([dict(source='CÔNG'+ky_tu+'TY DEMO ÁNH DƯƠNG', category='CONG_TY')])
                self.assertEqual((kq.se_them, kq.se_bo_qua, kq.loi), ({}, {'CONG_TY': 1}, {}))

    def test_quy_tac_junsky_va_sinh_theo_nhom(self):
        self.assertEqual(cm.bi_danh('CONG_TY', ma_junsky='KH-DEMO-00123'), '[[KH-DEMO-00123]]')
        self.assertEqual(cm.bi_danh('CONG_TY', so=1), '[[MASKCT-0001]]')
        self.assertEqual(cm.bi_danh('MA_SO_THUE', so=10000), '[[MASKMST-10000]]')
        self.assertEqual(cm.bi_danh('DIA_CHI', so=2), '[[MASKDC-0002]]')

    def test_tien_to_khong_trung_ke_ca_hoa_thuong_va_khong_dau_gach(self):
        for ma in ('MASKCT-0001', 'masktk.demo', 'MASKTAMabc', 'MASKKHAC_123'):
            with self.subTest(ma=ma), self.assertRaises(ValueError):
                cm.bi_danh('CONG_TY', ma_junsky=ma)
        for so in (0, -1, True, 1.5):
            with self.subTest(so=so), self.assertRaises(ValueError):
                cm.bi_danh('CONG_TY', so=so)

    def test_khong_suy_ma_junsky_tu_token_cu(self):
        kq = self.chuyen([muc_demo()], chay_thu=False)
        self.assertEqual((kq.truoc, kq.sau, kq.loi), (0, 1, {}))
        self.assertIsNone(self.db.dong[0]['ma_junsky'])

    def test_junsky_truyen_ro_va_nguon_co_dinh_khong_luu_duong_dan(self):
        kq = self.chuyen({'rules': [muc_demo(ma_junsky='KH-DEMO-01')]}, chay_thu=False)
        self.assertEqual(kq.sau, 1)
        self.assertEqual(self.db.dong[0]['ma_junsky'], 'KH-DEMO-01')
        ins = next(sql for sql, _ in self.db.lenh if sql.lstrip().startswith('INSERT'))
        self.assertIn("'MASK_V2'", ins)
        self.assertNotIn(str(self.tep), ins)

    def test_chay_lai_khong_them_va_khong_doi_ma(self):
        data = [muc_demo(ma_junsky='KH-DEMO-01')]
        self.chuyen(data, chay_thu=False)
        kq = self.chuyen(data, chay_thu=False)
        self.assertEqual((kq.truoc, kq.sau, kq.loi), (1, 1, {}))

    def test_trung_chuan_hoa_khac_nhom_khong_ghi_de(self):
        self.chuyen([muc_demo()], chay_thu=False)
        kq = self.chuyen([dict(source=' CÔNG TY DEMO ÁNH DƯƠNG ', category='DIA_CHI')], chay_thu=False)
        self.assertEqual(kq.loi, {'xung_dot': 1})
        self.assertEqual(self.db.dong[0]['nhom'], 'CONG_TY')

    def test_trung_trong_tep_va_loi_tien_to_duoc_dem_rieng(self):
        kq = self.chuyen([muc_demo(), muc_demo(),
                          dict(source='Tên DEMO khác', category='CONG_TY', ma_junsky='MASKCT-01')],
                         chay_thu=False)
        self.assertEqual((kq.sau, kq.loi), (1, {'trung_trong_tep': 1, 'tien_to': 1}))

    def test_chay_thu_mac_dinh_chi_select_khong_ghi_hay_dat_context(self):
        kq = self.chuyen([muc_demo()])
        self.assertEqual((kq.truoc, kq.sau, self.db.dong), (0, 0, []))
        self.assertEqual((kq.se_them, kq.se_bo_qua, kq.se_cho_duyet, kq.chua_doi_chieu),
                         ({'CONG_TY': 1}, {}, {}, {}))
        self.assertTrue(all(sql.lstrip().startswith('SELECT') and 'set_config' not in sql
                            for sql, _ in self.db.lenh))

    def test_chay_thu_khong_ket_noi_van_kiem_dinh_dang(self):
        self.ghi([muc_demo()])
        kq = cm.chuyen_danh_muc(self.tep, None, la_demo=True)
        self.assertEqual((kq.truoc, kq.sau, kq.loi), (0, 0, {}))
        self.assertEqual((kq.se_them, kq.se_bo_qua, kq.chua_doi_chieu), ({}, {}, {'CONG_TY': 1}))

    def test_chay_thu_dem_them_bo_qua_va_cho_duyet_theo_nhom(self):
        self.chuyen([muc_demo()], chay_thu=False)
        dong_cu = deepcopy(self.db.dong)
        bat_dau = len(self.db.lenh)
        kq = self.chuyen([muc_demo(), dict(source='Địa chỉ DEMO mới', category='DIA_CHI'),
                          muc_demo(canonical='Tên chuẩn DEMO'),
                          dict(source='Tên DEMO một', category='CA_NHAN', token='[CA_NHAN_001]'),
                          dict(source='Tên DEMO hai', category='CA_NHAN', token='[CA_NHAN_001]'),
                          dict(source='Tên DEMO tắt', category='KHAC', enabled=False)])
        self.assertEqual((kq.truoc, kq.sau), (1, 1))
        self.assertEqual((kq.se_them, kq.se_bo_qua, kq.se_cho_duyet, kq.chua_doi_chieu),
                         ({'DIA_CHI': 1}, {'CONG_TY': 1}, {'CONG_TY': 1, 'CA_NHAN': 2}, {}))
        self.assertEqual(kq.loi, {'ten_khac': 3, 'muc_tat': 1})
        self.assertEqual(self.db.dong, dong_cu)
        self.assertTrue(all(sql.lstrip().startswith('SELECT') and 'set_config' not in sql
                            for sql, _ in self.db.lenh[bat_dau:]))

    def test_chay_thu_khong_dem_xung_dot_hoac_trung_tep_la_se_them(self):
        self.chuyen([muc_demo(ma_junsky='KH-DEMO-01')], chay_thu=False)
        kq = self.chuyen([muc_demo(),
                          dict(source='Tên DEMO khác', category='CONG_TY', ma_junsky='kh-demo-01'),
                          dict(source='Tên DEMO mới', category='CA_NHAN'),
                          dict(source='Tên DEMO mới', category='CA_NHAN')])
        self.assertEqual((kq.se_them, kq.se_bo_qua, kq.se_cho_duyet), ({'CA_NHAN': 1}, {}, {}))
        self.assertEqual(kq.loi, {'trung_trong_tep': 1, 'xung_dot': 2})

    def test_chay_thu_loi_doi_chieu_khong_cong_bo_du_kien_gia(self):
        execute = self.db.execute
        def gay_loi(sql, params=()):
            if 'count(*)' in sql and any('gia_tri_chuan=' in lenh for lenh, _ in self.db.lenh):
                raise LoiDEMOCSDL('XX000')
            return execute(sql, params)
        self.db.execute = gay_loi
        kq = self.chuyen([muc_demo()])
        self.assertEqual((kq.se_them, kq.se_bo_qua, kq.chua_doi_chieu, kq.loi),
                         ({}, {}, {'CONG_TY': 1}, {'csdl': 1}))

    def test_chay_thu_sai_vung_khong_bao_xanh_gia(self):
        self.db.co_demo = 'false'
        kq = self.chuyen([muc_demo()])
        self.assertEqual(kq.loi, {'quyen': 1})
        self.assertEqual((kq.se_them, kq.se_bo_qua, kq.chua_doi_chieu), ({}, {}, {'CONG_TY': 1}))
        self.assertEqual(self.db.dong, [])

    def test_chay_thu_bat_trung_ma_junsky_voi_dinh_danh_khac(self):
        self.chuyen([muc_demo(ma_junsky='KH-DEMO-01')], chay_thu=False)
        kq = self.chuyen([dict(source='Đối tác DEMO khác', category='CONG_TY', ma_junsky='kh-demo-01')])
        self.assertEqual((kq.truoc, kq.sau, kq.loi), (1, 1, {'xung_dot': 1}))
        so_khop = next(sql for sql, _ in self.db.lenh if sql.startswith('SELECT EXISTS'))
        self.assertIn('lower(bi_danh COLLATE "und-x-icu")=lower(%s COLLATE "und-x-icu")', so_khop)

    def test_chay_thu_bat_trung_ma_junsky_trong_cung_tep(self):
        kq = self.chuyen([muc_demo(ma_junsky='KH-DEMO-01'),
                          dict(source='Tên DEMO khác', category='CONG_TY', ma_junsky='kh-demo-01')])
        self.assertEqual(kq.loi, {'xung_dot': 1})

    def test_nhieu_ten_dung_chung_token_khong_tu_tach_bi_danh(self):
        data = [muc_demo(), dict(source='DEMO Ánh Dương', category='CONG_TY', token='[CONG_TY_001]')]
        kq = self.chuyen(data, chay_thu=False)
        self.assertEqual((kq.sau, kq.loi), (0, {'ten_khac': 2}))

    def test_khong_ket_noi_khong_duoc_ghi(self):
        self.ghi([muc_demo()])
        kq = cm.chuyen_danh_muc(self.tep, None, la_demo=True, chay_thu=False)
        self.assertEqual(kq.loi, {'ket_noi': 1})

    def test_phan_loai_loi_csdl_khong_in_gia_tri_va_van_nhap_dong_hop_le(self):
        for state, loai in (('23505', 'xung_dot'), ('23514', 'rang_buoc'),
                            ('42501', 'quyen'), ('XX000', 'csdl')):
            with self.subTest(state=state):
                self.db.loi = state
                kq = self.chuyen([muc_demo()], chay_thu=False)
                self.assertEqual(kq.loi, {loai: 1})
                self.assertEqual(kq.sau, 0)
                self.assertNotIn('CANARY', repr(kq))

    def test_khong_chen_sql_va_khoi_phuc_context(self):
        self.db.co_demo = 'false'
        self.chuyen([dict(source="DEMO '); SELECT 'DEMO", category='KHAC')], chay_thu=False)
        self.assertEqual(self.db.co_demo, 'false')
        ins, params = next(x for x in self.db.lenh if x[0].lstrip().startswith('INSERT'))
        self.assertNotIn(params[0], ins)

    def test_savepoint_mot_dong_loi_van_nhap_dong_khac(self):
        self.db.loi = ['23514', None]
        kq = self.chuyen([muc_demo(), dict(source='Địa chỉ DEMO số một', category='DIA_CHI')],
                         chay_thu=False)
        self.assertEqual((kq.truoc, kq.sau, kq.loi), (0, 1, {'rang_buoc': 1}))
        self.assertEqual(self.db.dong[0]['nhom'], 'DIA_CHI')

    def test_loi_cuoi_transaction_lui_toan_bo_va_khong_lo_driver(self):
        execute = self.db.execute
        dem = 0
        def gay_loi(sql, params=()):
            nonlocal dem
            if 'count(*)' in sql:
                dem += 1
                if dem == 2:
                    raise LoiDEMOCSDL('XX000')
            return execute(sql, params)
        self.db.execute = gay_loi
        kq = self.chuyen([muc_demo()], chay_thu=False)
        self.assertEqual((kq.truoc, kq.sau, kq.loi, self.db.dong), (0, 0, {'csdl': 1}, []))

    def test_khong_chuyen_muc_tat_hoac_ten_rut_gon_ma_khong_bao(self):
        kq = self.chuyen([dict(source='DEMO tắt', category='KHAC', enabled=False),
                          muc_demo(canonical='Tên chuẩn DEMO')], chay_thu=False)
        self.assertEqual(kq.loi, {'muc_tat': 1, 'ten_khac': 1})
        self.assertEqual(kq.sau, 0)

    def test_tat_ca_nhom_nguon_duoc_chuyen_va_khong_cat_gia_tri(self):
        data = [dict(source='DEMO '+nhom, category=nhom) for nhom in cm.TIEN_TO]
        data.append(dict(source='X'*301, category='KHAC'))
        kq = self.chuyen(data, chay_thu=False)
        self.assertEqual((kq.sau, kq.loi), (len(cm.TIEN_TO), {'dinh_dang': 1}))

    def test_json_hong_bom_va_thieu_tep_chi_bao_so_loi(self):
        self.tep.write_text('{"CANARY_DEMO":', encoding='utf-8')
        self.assertEqual(cm.chuyen_danh_muc(self.tep, None, la_demo=True).loi, {'tep': 1})
        self.tep.write_text('\ufeff'+json.dumps([muc_demo()]), encoding='utf-8')
        self.assertEqual(cm.chuyen_danh_muc(self.tep, None, la_demo=True).loi, {})
        self.assertEqual(cm.chuyen_danh_muc(Path(self.tmp)/'KHONG_CO_DEMO.json', None,
                                          la_demo=True).loi, {'tep': 1})

    def test_cli_chi_in_so_dem_ke_ca_loi_tham_so(self):
        self.ghi([muc_demo()])
        for args in ([str(self.tep), '--chay-thu'], ['CANARY_DEMO', '--tham-so-sai']):
            with self.subTest(args=args), redirect_stdout(io.StringIO()) as out, \
                    redirect_stderr(io.StringIO()) as err:
                cm.main(args)
                self.assertNotIn('CANARY', out.getvalue()+err.getvalue())
                self.assertNotIn('Công ty DEMO Ánh Dương', out.getvalue()+err.getvalue())
                self.assertNotIn(str(self.tep), out.getvalue()+err.getvalue())
                self.assertIn('Số dòng trước:', out.getvalue())

    def test_cli_chay_thu_in_du_kien_va_nhom_nghiep_vu_khong_lo_gia_tri(self):
        self.chuyen([muc_demo()], chay_thu=False)
        self.ghi([muc_demo(), dict(source='Địa chỉ CANARY_DEMO', category='DIA_CHI'),
                  dict(source='Tên CANARY_DEMO', category='CA_NHAN', canonical='Tên chuẩn DEMO')])
        with redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
            self.assertEqual(cm.main([str(self.tep), '--chay-thu'], ket_noi=self.db), 1)
        for dong in ('Sẽ thêm: 1', 'Sẽ thêm (Địa chỉ): 1', 'Sẽ bỏ qua (đã có): 1',
                     'Sẽ bỏ qua (đã có) (Công ty): 1', 'Sẽ vào danh sách chờ: 1',
                     'Sẽ vào danh sách chờ (Cá nhân): 1', 'Chưa đối chiếu: 0'):
            self.assertIn(dong, out.getvalue())
        for bi_mat in ('CANARY', 'Ánh Dương', str(self.tep), 'DIA_CHI', 'CA_NHAN', 'CONG_TY'):
            self.assertNotIn(bi_mat, out.getvalue()+err.getvalue())

    def test_cli_chay_thu_thieu_ket_noi_bao_chua_doi_chieu(self):
        self.ghi([muc_demo()])
        with redirect_stdout(io.StringIO()) as out:
            self.assertEqual(cm.main([str(self.tep), '--chay-thu']), 0)
        self.assertIn('Sẽ thêm: 0', out.getvalue())
        self.assertIn('Chưa đối chiếu (Công ty): 1', out.getvalue())


class SQLThuanTests(unittest.TestCase):
    def test_chay_lai_dung_thu_tu_113_117_118_va_nguyen_byte(self):
        from unittest.mock import MagicMock
        conn = MagicMock()
        chay_lai_chuoi_mask(conn)
        self.assertEqual([c.args for c in conn.execute.call_args_list], [
            ((SQL_PATH.parent / name).read_bytes().decode('utf-8', errors='strict'),)
            for name in ('113_mask_dinh_danh.sql', '117_mask_duyet_cho.sql', '118_mask_phien.sql')])

    def test_chay_lai_bao_sqlstate_va_message_goc_khong_in_sql_hay_dsn(self):
        from unittest.mock import MagicMock
        conn = MagicMock()
        loi = LoiDEMOCSDL('42501')
        loi.diag = MagicMock(message_primary='permission denied for function cap_ma_yeu_cau')
        conn.execute.side_effect = loi
        with self.assertRaises(AssertionError) as caught:
            chay_lai_chuoi_mask(conn)
        self.assertEqual(str(caught.exception), '113_mask_dinh_danh.sql: sqlstate=42501; '
                         'message_primary=permission denied for function cap_ma_yeu_cau')
        self.assertEqual(conn.execute.call_count, 1)
        self.assertNotIn('CANARY', str(caught.exception))

    def test_fixture_module_demo_qua_kiem_goi_va_cua_duyet_core(self):
        from unittest.mock import MagicMock

        owner = MagicMock()
        goi_id = uuid4()
        owner.execute.return_value.fetchone.side_effect = [None, (goi_id,)]
        ma_module = duyet_module_demo(self, owner)
        # Chạy thật kiểm gói/snapshot/kế hoạch; chỉ giả kết nối, không gọi PG.
        self.assertEqual(owner.execute.call_count, 2)
        lenh, tham_so = owner.execute.call_args_list[0].args
        self.assertEqual(lenh, 'SELECT phien_ban,the_he FROM loi.module_da_cai WHERE module=%s')
        self.assertEqual(tham_so, (ma_module,))
        lenh, tham_so = owner.execute.call_args_list[1].args
        self.assertEqual(lenh, 'SELECT loi.duyet_goi(%s::jsonb)')
        ke_hoach = json.loads(tham_so[0])
        self.assertRegex(ma_module, r'^mask_demo_[0-9a-f]{8}$')
        self.assertEqual(ke_hoach['manifest']['ma'], ma_module)
        self.assertEqual(ke_hoach['the_he_cu'], 0)
        self.assertEqual(len(ke_hoach['migration']), 1)
        self.assertEqual(ke_hoach['contract'], [])

    def test_guard_icu_tieng_viet_dung_truoc_khi_doi_csdl(self):
        sql = SQL_PATH.read_text(encoding='utf-8')
        self.assertIn('IF to_regcollation(\'"und-x-icu"\') IS NULL THEN', sql)
        for chu, thuong in (('Ô', 'ô'), ('Đ', 'đ')):
            self.assertIn(f'lower(\'{chu}\' COLLATE "und-x-icu")=\'{thuong}\'', sql)
        self.assertLess(sql.index('MASK_THIEU_COLLATION_UND_ICU'), sql.index('IF NOT (lower('))
        self.assertLess(sql.index('MASK_ICU_KHONG_HO_TRO_TIENG_VIET'), sql.index('CREATE ROLE'))
        self.assertNotIn('MASK_LC_CTYPE_KHONG_HO_TRO_TIENG_VIET', sql)
        self.assertIn('Không thể áp danh mục Mask', sql)

    def test_tien_to_python_va_csdl_khong_lech(self):
        import re
        sql = SQL_PATH.read_text(encoding='utf-8')
        cap = dict(re.findall(r"WHEN '([A-Z_]+)' THEN '(MASK[A-Z]+)'", sql))
        self.assertEqual(cap, cm.TIEN_TO)

    def test_migration_khong_doi_ban_cu_va_khong_phu_thuoc_111_112(self):
        sql = SQL_PATH.read_text(encoding='utf-8')
        self.assertNotIn('111_', sql)
        self.assertNotIn('112_', sql)
        self.assertNotIn('\ufffd', sql)
        self.assertFalse(SQL_PATH.read_bytes().startswith(b'\xef\xbb\xbf'))
        self.assertIn('NOBYPASSRLS', sql)
        self.assertIn('pg_auth_members', sql)

    def test_bang_rieng_khong_xuat_dinh_danh_va_co_rao_demo(self):
        sql = SQL_PATH.read_text(encoding='utf-8')
        for table in ('dinh_danh', 'yeu_cau', 'cho_duyet'):
            self.assertIn('CREATE TABLE IF NOT EXISTS mask.'+table, sql)
        self.assertIn('FORCE ROW LEVEL SECURITY', sql)
        self.assertIn('ktt.mask_la_demo', sql)
        self.assertIn('Không đăng ký loi.xuat_dang_ky_bang', sql)
        self.assertNotIn('phap_nhan_id uuid', sql)


@unittest.skipUnless(os.environ.get('KHO_PG_DSN_TEST') and importlib.util.find_spec('psycopg'),
                     'CHUA_KIEM PG MASK-2: chỉ lead chạy; worker chỉ thuần/mock')
class PostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Cùng provisioning G2-09 và fixture phiên/tài liệu của MASK-3-PHIEN;
        # chỉ một CSDL test cho lớp, không dùng cửa cấp mã cũ sau 118.
        import test_g2_25 as pg
        from tests.test_mask_phien import chuan_bi_phien
        chuan_bi_phien(cls)
        cls.pg = pg
        cls.owner, cls.tt = cls.conn, cls.tien_to

    def setUp(self):
        self.enterContext(self.owner.transaction(force_rollback=True))
        self.owner.execute("SELECT set_config('ktt.mask_la_demo','true',true)")

    def them(self, gia_tri=None, nhom='CONG_TY', ma=None):
        return self.owner.execute("""INSERT INTO mask.dinh_danh(gia_tri,nhom,ma_junsky,nguon,la_demo)
            VALUES(%s,%s,%s,'DEMO',true) RETURNING bi_danh""",
            (gia_tri or 'Tên DEMO '+uuid4().hex, nhom, ma)).fetchone()[0]

    def test_tao_bang_va_phan_quyen_module_khac_bi_tu_choi(self):
        ma_module = duyet_module_demo(self, self.owner)
        module = self.tt+'vai_chay_mod_'+ma_module
        self.assertIsNotNone(self.owner.execute('SELECT to_regrole(%s)', (module,)).fetchone()[0])
        # Chứng minh đây là vai runtime được Core cấp quyền, tránh vai trống.
        self.assertTrue(self.owner.execute('SELECT has_function_privilege(%s,%s,%s)',
            (module, 'loi.xac_minh_phien(text,text,uuid,text,uuid,bigint)', 'EXECUTE')).fetchone()[0])
        self.assertTrue(self.owner.execute('SELECT pg_has_role(%s,%s,%s)',
            (self.tt+'dang_nhap_mod_'+ma_module, module, 'USAGE')).fetchone()[0])
        cac_vai = [self.tt+vai for vai in ('vai_chay_loi', 'vai_xuat_phap_nhan', 'vai_kiem_demo')]
        cac_vai.append(module)
        for table in ('dinh_danh', 'yeu_cau', 'cho_duyet'):
            self.assertIsNotNone(self.owner.execute('SELECT to_regclass(%s)', ('mask.'+table,)).fetchone()[0])
            for role in cac_vai:
                with self.subTest(vai=role, bang=table), \
                        self.assertRaises(self.pg.psycopg.errors.InsufficientPrivilege), self.owner.transaction():
                    self.owner.execute(self.pg.sql.SQL('SET LOCAL ROLE {}').format(self.pg.sql.Identifier(role)))
                    self.owner.execute('SELECT * FROM mask.'+table)
        # Kiểm ACL riêng để tránh xanh giả do guard session_user từ chối superuser.
        self.assertFalse(self.owner.execute('SELECT has_function_privilege(%s,%s,%s)',
            (module, 'mask.cap_ma_yeu_cau(text,uuid,uuid,boolean)', 'EXECUTE')).fetchone()[0])
        with self.assertRaises(self.pg.psycopg.errors.InsufficientPrivilege), self.owner.transaction():
            self.owner.execute(self.pg.sql.SQL('SET LOCAL SESSION AUTHORIZATION {}').format(
                self.pg.sql.Identifier(module)))
            self.owner.execute("SELECT mask.cap_ma_yeu_cau('demo',%s,%s,true)", (uuid4(), uuid4()))

    def test_chuan_hoa_python_khop_sql_ke_ca_dau_tach_nhom(self):
        for ky_tu in ('\t', '\n', '\v', '\f', '\r', '\x1c', '\x1d', '\x1e', '\x1f',
                      ' ', '\x85', '\xa0', '\u1680', '\u2000', '\u2007', '\u200a',
                      '\u2028', '\u2029', '\u202f', '\u205f', '\u3000'):
            with self.subTest(ma=ord(ky_tu)):
                gia_tri = ky_tu+'ĐÔ'+ky_tu+'THI\u0323'+ky_tu
                self.assertEqual(self.owner.execute('SELECT mask.chuan_hoa(%s)', (gia_tri,)).fetchone()[0],
                                 cm.chuan_hoa(gia_tri))

    def test_chuan_hoa_chu_viet_khop_sql_icu_va_chi_muc(self):
        for hoa, thuong in CHU_VIET:
            for dang in ('NFC', 'NFD'):
                with self.subTest(chu=hoa, dang=dang):
                    gia_tri = unicodedata.normalize(dang, hoa)
                    sql = self.owner.execute('SELECT mask.chuan_hoa(%s), '
                        'lower(normalize(%s,NFC) COLLATE "und-x-icu")',
                        (gia_tri, gia_tri)).fetchone()
                    self.assertEqual(sql, (thuong, thuong))
                    self.assertEqual(cm.chuan_hoa(gia_tri), sql[0])
        for ten in ('dinh_danh_bi_danh', 'dinh_danh_bi_danh_tam'):
            with self.subTest(chi_muc=ten):
                dinh_nghia = self.owner.execute('SELECT pg_get_indexdef(to_regclass(%s))',
                                               ('mask.'+ten,)).fetchone()[0]
                self.assertIn('COLLATE "und-x-icu"', dinh_nghia)

    def test_duy_nhat_chuan_hoa_bat_ke_nhom(self):
        ten = 'Công ty DEMO '+uuid4().hex
        self.them(ten)
        with self.assertRaises(self.pg.psycopg.errors.UniqueViolation), self.owner.transaction():
            self.them('  '+ten.upper().replace(' ', '\t')+'  ', nhom='DIA_CHI')

    def test_quy_tac_ma_va_khong_cat_so_lon(self):
        ma = 'KH-DEMO-'+uuid4().hex
        self.assertEqual(self.them(ma=ma), '[['+ma+']]')
        self.assertRegex(self.them(), r'^\[\[MASKCT-[0-9]{4,}\]\]$')
        with self.assertRaises(self.pg.psycopg.errors.CheckViolation), self.owner.transaction():
            self.them(ma='maskCT-0001')

    def test_rls_engine_tach_demo_va_khong_mac_dinh_doc_van_hanh(self):
        self.them()
        self.owner.execute(self.pg.sql.SQL('SET LOCAL ROLE {}').format(
            self.pg.sql.Identifier(self.tt+'vai_chay_mask')))
        self.owner.execute("SELECT set_config('ktt.mask_la_demo','',true)")
        self.assertEqual(self.owner.execute('SELECT count(*) FROM mask.dinh_danh').fetchone()[0], 0)
        with self.assertRaises(self.pg.psycopg.errors.InsufficientPrivilege), self.owner.transaction():
            self.them()
        self.owner.execute("SELECT set_config('ktt.mask_la_demo','true',true)")
        self.assertGreater(self.owner.execute('SELECT count(*) FROM mask.dinh_danh').fetchone()[0], 0)
        self.owner.execute("SELECT set_config('ktt.mask_la_demo','false',true)")
        self.assertEqual(self.owner.execute('SELECT count(*) FROM mask.dinh_danh').fetchone()[0], 0)

    def test_core_cap_ma_va_khong_duoc_doc_bang(self):
        from kho_tri_thuc.core import phien
        # Chạy đúng session login Core; không dùng SET ROLE giả session_user.
        nguoi, tep = self.fx.nd, self.fx.tai_lieu_id
        self.owner.execute(self.pg.sql.SQL('SET LOCAL SESSION AUTHORIZATION {}').format(
            self.pg.sql.Identifier(self.tt+'dang_nhap_loi')))
        token = phien.cap_phien(self.owner, nguoi_dung_id=nguoi, module='crm', phap_nhan_id=self.fx.pn,
            dang_nhap_csdl=self.tt+'dang_nhap_loi', pham_vi_hanh_dong=[self.g209.XEM],
            hieu_luc_den=datetime.now(timezone.utc)+timedelta(minutes=5)).ma.lay_de_truyen()
        ma = self.owner.execute('SELECT mask.cap_ma_yeu_cau(%s,%s,%s,%s,%s,%s,%s)',
            (token, 'crm', self.fx.pn, self.g209.XEM, tep, None, None)).fetchone()[0]
        for table in ('dinh_danh', 'yeu_cau', 'cho_duyet'):
            with self.subTest(bang=table), \
                    self.assertRaises(self.pg.psycopg.errors.InsufficientPrivilege), self.owner.transaction():
                self.owner.execute('SELECT * FROM mask.'+table)
        self.owner.execute('RESET SESSION AUTHORIZATION')
        self.assertEqual(self.owner.execute('SELECT module,nguoi_gui,tai_lieu_id,trang_thai,dong_luc '
                                            'FROM mask.yeu_cau WHERE id=%s', (ma,)).fetchone(),
                         ('crm', nguoi, tep, 'DANG_XU_LY', None))

    def test_trang_thai_dong_va_cho_duyet_khong_lien_ket_cheo_demo(self):
        ma = self.owner.execute("""INSERT INTO mask.yeu_cau(module,nguoi_gui,tai_lieu_id,la_demo)
            VALUES('demo',%s,%s,true) RETURNING id""", (uuid4(), uuid4())).fetchone()[0]
        with self.assertRaises(self.pg.psycopg.errors.CheckViolation), self.owner.transaction():
            self.owner.execute("UPDATE mask.yeu_cau SET trang_thai='DA_DONG' WHERE id=%s", (ma,))
        self.owner.execute("UPDATE mask.yeu_cau SET trang_thai='DA_DONG',dong_luc=clock_timestamp() WHERE id=%s", (ma,))
        with self.assertRaises(self.pg.psycopg.errors.ForeignKeyViolation), self.owner.transaction():
            self.owner.execute("""INSERT INTO mask.cho_duyet(cum_goc,nhom,yeu_cau_id,nguon,la_demo)
                VALUES('Cụm DEMO','KHAC',%s,'DEMO',false)""", (ma,))
        bi_danh = self.owner.execute("""INSERT INTO mask.cho_duyet(cum_goc,nhom,yeu_cau_id,nguon,la_demo)
            VALUES('Cụm DEMO','KHAC',%s,'DEMO',true) RETURNING bi_danh_tam""", (ma,)).fetchone()[0]
        self.assertRegex(bi_danh, r'^\[\[MASKTAM-[0-9a-f]{32}\]\]$')

    def test_chuyen_demo_chay_thu_roi_ghi_va_chay_lai(self):
        role = self.tt+'vai_chay_mask'
        self.owner.execute(self.pg.sql.SQL('SET LOCAL ROLE {}').format(self.pg.sql.Identifier(role)))
        self.assertEqual(self.owner.execute('SELECT current_user').fetchone()[0], role)
        with tempfile.TemporaryDirectory(prefix='mask2_pg_DEMO_') as thu_muc:
            tep = Path(thu_muc)/'DEMO.json'
            tep.write_text(json.dumps([dict(source='Công ty DEMO '+uuid4().hex,
                                            category='CONG_TY', ma_junsky='KH-DEMO-'+uuid4().hex)]),
                           encoding='utf-8')
            thu = cm.chuyen_danh_muc(tep, self.owner, la_demo=True)
            self.assertEqual(thu.truoc, thu.sau)
            self.assertEqual((thu.se_them, thu.se_bo_qua, thu.loi), ({'CONG_TY': 1}, {}, {}))
            ghi = cm.chuyen_danh_muc(tep, self.owner, la_demo=True, chay_thu=False)
            self.assertEqual((ghi.sau, ghi.loi), (ghi.truoc+1, {}))
            lap = cm.chuyen_danh_muc(tep, self.owner, la_demo=True, chay_thu=False)
            self.assertEqual((lap.truoc, lap.sau, lap.loi), (ghi.sau, ghi.sau, {}))
            thu_lai = cm.chuyen_danh_muc(tep, self.owner, la_demo=True)
            self.assertEqual((thu_lai.se_them, thu_lai.se_bo_qua, thu_lai.loi), ({}, {'CONG_TY': 1}, {}))
            # Ngay trên kết nối chạy công cụ: GUC DEMO phải chặn ghi sang vùng thật.
            with self.assertRaises(self.pg.psycopg.errors.InsufficientPrivilege), self.owner.transaction():
                self.owner.execute("""INSERT INTO mask.dinh_danh(gia_tri,nhom,nguon,la_demo)
                    VALUES(%s,'CONG_TY','DEMO',false)""", ('Tên DEMO '+uuid4().hex,))

    def test_chay_lai_113_khong_doi_du_lieu_owner_acl_va_doi_tuong(self):
        self.them()
        def chup():
            return self.owner.execute("""SELECT c.oid,c.relname,c.relowner,c.relacl,
                c.relrowsecurity,c.relforcerowsecurity FROM pg_class c
                WHERE c.relnamespace='mask'::regnamespace ORDER BY c.oid""").fetchall(), \
                self.owner.execute('SELECT * FROM mask.dinh_danh ORDER BY id').fetchall(), \
                self.owner.execute("""SELECT p.oid,p.proowner,p.proacl,pg_get_functiondef(p.oid)
                    FROM pg_proc p WHERE p.pronamespace='mask'::regnamespace ORDER BY p.oid""").fetchall(), \
                self.owner.execute("""SELECT oid,tgrelid,tgname,tgfoid,tgtype FROM pg_trigger
                    WHERE tgrelid IN ('mask.dinh_danh'::regclass,'mask.yeu_cau'::regclass,
                        'mask.cho_duyet'::regclass) ORDER BY oid""").fetchall(), \
                self.owner.execute('SELECT last_value,is_called FROM mask.so_bi_danh').fetchone()
        truoc = chup()
        chay_lai_chuoi_mask(self.owner)
        self.assertEqual(chup(), truoc)
        cu = 'mask.cap_ma_yeu_cau(text,uuid,uuid,boolean)'
        self.assertFalse(self.owner.execute('SELECT has_function_privilege(%s,%s,\'EXECUTE\')',
                         (self.tt+'dang_nhap_loi', cu)).fetchone()[0])
        with self.assertRaises(self.pg.psycopg.errors.InsufficientPrivilege), self.owner.transaction():
            self.owner.execute(self.pg.sql.SQL('SET LOCAL SESSION AUTHORIZATION {}').format(
                self.pg.sql.Identifier(self.tt+'dang_nhap_loi')))
            self.owner.execute("SELECT mask.cap_ma_yeu_cau('crm',%s,%s,true)",
                               (self.fx.nd, self.fx.tai_lieu_id))


if __name__ == '__main__':
    unittest.main()
