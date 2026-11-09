"""MASK-3B: byte SQL + kho mock; PG chỉ lead chạy với dữ liệu DEMO tự sinh.

Không đọc cấu hình/DSN từ tệp, không mở dịch vụ. Test PG không phải chứng cứ
đã chạy khi chỉ kiểm thuần; mỗi ca được đánh dấu CHUA_KIEM nếu chưa có PG.
"""
from contextlib import contextmanager, ExitStack
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import importlib.util
import inspect
import json
import os
from pathlib import Path
import re
from threading import Event
from time import monotonic
import unicodedata
import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from engines.e_mask.che_van_ban import Kho, LoiCheVanBan, che, chuan_hoa, mo_che
from engines.e_mask.nguon.privacy import detectors, leftovers
from kho_tri_thuc.core.kho_mask import KhoMask, LoiKhoMask
from kho_tri_thuc.core.phien import MaBiMat
from tests import test_mask_phien as nen
from tests.test_mask_4a import kiem_cau_truc_sql


ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = ROOT / 'src/kho_tri_thuc/core/sql/119_mask_kho.sql'
CTX = 'text,text,uuid,text,uuid,bigint,uuid'
PUBLIC = {
    'liet_ke_dinh_danh': CTX,
    'liet_ke_bi_danh': CTX,
    'tra_bi_danh': CTX + ',text',
    'ghi_cho_duyet': CTX + ',text,text,text,boolean',
    'doc_yeu_cau': CTX,
    'ghi_bi_danh_da_dung': CTX + ',text[]',
    'tra_dinh_danh': CTX + ',text',
    'dong_yeu_cau': CTX,
}
TEN = 'Công ty DEMO Ánh Dương'
VAN_BAN = TEN + '; thanh toán 1.000.000 VND ngày 07/11/2026.'


def doc_sql():
    return SQL_PATH.read_bytes().decode('utf-8', errors='strict')


def cac_ham():
    return dict(re.findall(r'CREATE OR REPLACE FUNCTION mask\.([a-z_]+)\(.*?'
                           r'AS \$ham\$(.*?)\$ham\$;', doc_sql(), re.S))


@contextmanager
def tai_nguyen_demo():
    """Từ vựng DEMO cố định; không tải hoặc mở danh mục vận hành."""
    caches = (detectors.surnames, detectors.places, detectors.acronyms,
              detectors._ascii_surnames, leftovers.allowlist)
    for ham in caches:
        ham.cache_clear()
    try:
        with ExitStack() as stack:
            tu_dien = {'vn_surnames.txt': ['Nguyễn *', 'Trần *'],
                       'vn_places.txt': [], 'common_acronyms.txt': ['DEMO VND USD VAT GTGT']}
            stack.enter_context(patch.object(detectors, '_lines', side_effect=lambda ten: tu_dien[ten]))
            stack.enter_context(patch.object(leftovers, 'allowlist', return_value=(
                frozenset(), frozenset('demo vnd usd dữ liệu giả ngày thanh toán'.split()))))
            yield
    finally:
        for ham in caches:
            ham.cache_clear()


class SQLThuanTests(unittest.TestCase):
    def test_byte_goc_utf8_nfc_khong_bom_hay_mat_dau(self):
        for path in (SQL_PATH, ROOT/'src/kho_tri_thuc/core/kho_mask.py', Path(__file__)):
            raw = path.read_bytes()
            text = raw.decode('utf-8', errors='strict')
            self.assertFalse(raw.startswith(b'\xef\xbb\xbf'))
            self.assertEqual(raw, text.encode('utf-8'))
            self.assertNotIn('\ufffd', text)
            self.assertEqual(text, unicodedata.normalize('NFC', text))
        self.assertIn('xác minh lại phiên', doc_sql())

    def test_119_duy_nhat_chuoi_migration_doc_dung_byte(self):
        from kho_tri_thuc.core.doi_cau_truc import _doc_chuoi
        files = list(SQL_PATH.parent.glob('[0-9][0-9][0-9]_*.sql'))
        self.assertEqual([p.name for p in files if p.name.startswith('119_')], [SQL_PATH.name])
        self.assertEqual(_doc_chuoi(files)[119][0], doc_sql())

    def test_cau_truc_byte_case_tag_execute_format(self):
        raw = SQL_PATH.read_bytes()
        kiem_cau_truc_sql(raw)
        self.assertEqual(re.findall(rb'\$[A-Za-z_]*\$', raw),
                         [b'$migration$'] + [b'$ham$']*20 + [b'$migration$'])
        self.assertEqual(set(cac_ham()), set(PUBLIC) | {'kiem_yeu_cau'})

    def test_guard_truoc_ddl_khop_113_117_118(self):
        sql = doc_sql()
        guard = sql[:sql.index("PERFORM set_config('search_path'")]
        for part in ("tt !~ '^[a-z][a-z0-9_]*_$'", 'octet_length(', '^kho_test_',
                     'kho_core_demo_g2_', '160000', "vai_cu<>'none'", 'pg_auth_members',
                     'rolcanlogin', 'rolsuper', 'rolbypassrls', 'rolcreatedb', 'rolreplication',
                     'relrowsecurity AND relforcerowsecurity', "polname='vung_demo'",
                     "polname<>'vung_demo'", "polname='tai_lieu_phien'", 'MASK_KHO_SAI_OWNER',
                     nen.NGU_CANH, nen.TAI_LIEU, nen.MOI, '"und-x-icu"'):
            self.assertIn(part, guard)
        self.assertNotRegex(guard, r'\b(?:CREATE|ALTER|GRANT|REVOKE)\b')

    def test_moi_cua_xac_minh_lai_va_demo_dat_sau_kiem_khoi_phuc(self):
        for name, body in cac_ham().items():
            with self.subTest(cua=name):
                call = 'loi.mask_ngu_canh(' if name == 'kiem_yeu_cau' else 'mask.kiem_yeu_cau('
                self.assertIn(call, body)
                self.assertLess(body.index(call), body.index("set_config('ktt.mask_la_demo',ctx.la_demo::text,true)"))
                self.assertIn("current_setting('ktt.mask_la_demo',true)", body)
                self.assertIn("set_config('ktt.mask_la_demo',coalesce(cu,''),true)", body)
        self.assertNotIn('p_la_demo', doc_sql())
        self.assertNotIn('p_nguoi_gui', doc_sql())

    def test_yeu_cau_khoa_hang_kiem_chu_vung_trang_thai_va_tai_lieu(self):
        helper = cac_ham()['kiem_yeu_cau']
        for part in ('LOCK TABLE mask.yeu_cau IN ROW EXCLUSIVE MODE', 'FOR UPDATE',
                     'y.module=p_module', 'y.nguoi_gui=ctx.nguoi_gui', 'y.la_demo=ctx.la_demo',
                     "y.trang_thai='DANG_XU_LY'", 'loi_tai_lieu.mask_kiem_tai_lieu(',
                     'yc.tai_lieu_id,p_viec,p_the_he', "ERRCODE='42501'"):
            self.assertIn(part, helper)

    def test_dem_gap_lai_upsert_nguyen_tu_va_dau_chong_lap(self):
        sql, body = doc_sql(), cac_ham()['ghi_cho_duyet']
        self.assertIn('ADD COLUMN IF NOT EXISTS cum_da_gap text[]', sql)
        for part in ('mask.chuan_hoa(p_gia_tri)', 'chuan=ANY(y.cum_da_gap)',
                     'ON CONFLICT (la_demo,cum_chuan) DO UPDATE',
                     'so_lan_gap=c.so_lan_gap+(NOT da_dem AND c.yeu_cau_id<>p_yeu_cau)::integer',
                     'array_append(y.cum_da_gap,chuan)', "'vua_them',hang.id=moi_id",
                     'IF p_chi_gap_lai THEN', 'FOR UPDATE'):
            self.assertIn(part, body)
        self.assertLess(body.index('ON CONFLICT'), body.index('UPDATE mask.yeu_cau'))
        self.assertNotIn('xmax', body)

    def test_chi_hai_cua_tra_gia_tri_goc(self):
        for name, body in cac_ham().items():
            if name in {'liet_ke_dinh_danh', 'tra_dinh_danh'}:
                continue
            self.assertNotRegex(body, r"jsonb_build_object\([^;]*'(?:gia_tri|cum_goc|cum_da_gap)'",
                                name)
            self.assertNotRegex(body, r'RETURN(?: QUERY)?\s+SELECT\s+\*', name)
        self.assertIn('SELECT d.gia_tri INTO kq', cac_ham()['tra_dinh_danh'])
        self.assertIn('SELECT c.cum_goc INTO kq', cac_ham()['tra_dinh_danh'])

    def test_acl_chi_core_helper_chi_owner_khong_cap_bang(self):
        sql = doc_sql()
        self.assertEqual(sql.count('SECURITY DEFINER SET search_path=pg_catalog,pg_temp'), 10)
        self.assertIn('REVOKE ALL ON FUNCTION %s FROM PUBLIC CASCADE', sql)
        self.assertIn('aclexplode(b.proacl)', sql)
        self.assertIn("ELSIF b.proname<>'kiem_yeu_cau' THEN", sql)
        self.assertIn("'GRANT EXECUTE ON FUNCTION %s TO %I',ck,login", sql)
        self.assertNotRegex(sql, r'GRANT (?:SELECT|INSERT|UPDATE|DELETE|REFERENCES)')
        self.assertNotRegex(sql, r'\b(?:DROP|TRUNCATE|DELETE|CREATE TABLE|ALTER POLICY)\b')
        self.assertIn("set_config('role',vai_cu,true)", sql)
        self.assertIn("set_config('search_path',path_cu,true)", sql)

    def test_khong_trung_bien_declare_voi_bi_danh(self):
        for name, body in cac_ham().items():
            declarations = body.split('BEGIN', 1)[0]
            variables = set(re.findall(r'(?:DECLARE|;)\s*([a-z_]+)\s+', declarations))
            aliases = set(re.findall(r'\b(?:FROM|JOIN)\s+[a-z_]+\.[a-z_]+\s+([a-z_]+)\b', body))
            self.assertFalse(variables & aliases, (name, variables & aliases))

    def test_bi_danh_so_hoa_thuong_dung_icu(self):
        sql = doc_sql()
        for lower in re.findall(r'lower\(([^)]*)\)', sql):
            self.assertIn('COLLATE "und-x-icu"', lower)
        self.assertIn('y.bi_danh_tam_da_dung,hang.bi_danh_tam)', sql)
        self.assertIn('tam := array_append(tam,bd_goc)', sql)
        self.assertNotIn('tam := array_append(tam,ma_bd)', sql)
        self.assertIn('d.bi_danh_tam', cac_ham()['tra_dinh_danh'])

    def test_khoa_cho_truoc_khi_doc_chinh_thuc_va_giu_cum_tu_choi(self):
        body = cac_ham()['ghi_cho_duyet']
        self.assertLess(body.index('c.cum_chuan=chuan FOR UPDATE'), body.index('SELECT d.* INTO chinh'))
        self.assertIn('d.gia_tri_chuan=chuan FOR KEY SHARE', body)
        self.assertIn('WHERE c.id=hang.id AND c.la_demo=ctx.la_demo RETURNING c.* INTO hang', body)
        self.assertIn('SELECT c.* INTO STRICT hang', body)

    def test_doc_goc_co_audit_co_dinh_va_pham_vi_cho_theo_tai_lieu(self):
        bodies = cac_ham()
        for name, action in (('liet_ke_dinh_danh', 'LIET_KE'), ('tra_dinh_danh', 'TRA')):
            self.assertIn('loi.mask_kiem_toan_doc(', bodies[name])
            self.assertIn("p_yeu_cau,'"+action+"'", bodies[name])
        listing = bodies['liet_ke_dinh_danh']
        for part in ('y.module=yc.module', 'y.nguoi_gui=yc.nguoi_gui', 'y.tai_lieu_id=yc.tai_lieu_id'):
            self.assertIn(part, listing)
        aliases = bodies['liet_ke_bi_danh']
        self.assertNotRegex(aliases, r'\b(?:gia_tri|gia_tri_chuan|cum_goc|cum_chuan|nhom|nguon)\b')
        helper = doc_sql().split('CREATE OR REPLACE FUNCTION loi.mask_kiem_toan_doc', 1)[1].split('$ham$;', 1)[0]
        self.assertIn("('LIET_KE','mask.dinh_danh.liet_ke'),('TRA','mask.dinh_danh.tra')", helper)
        self.assertIn("loi.ghi_kiem_toan(p_hd,dt,p_yeu_cau,'DAT',p_ma,p_module,", helper)
        self.assertNotRegex(helper, r'\b(?:gia_tri|bi_danh|cum_goc)\b')

    def test_guard_bat_case_khong_boc_ngoac_tren_byte_goc(self):
        raw = SQL_PATH.read_bytes()
        broken = raw.replace(b'<>(CASE WHEN', b'<>CASE WHEN', 1).replace(b'ELSE chu_mask END)', b'ELSE chu_mask END', 1)
        self.assertNotEqual(raw, broken)
        with self.assertRaises(AssertionError):
            kiem_cau_truc_sql(broken)


class KhoThuanTests(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.token = "DEMO'); SELECT 'khong-chen"
        self.pn, self.tai_lieu, self.ma = uuid4(), uuid4(), uuid4()
        self.kho = KhoMask(self.conn, ma=MaBiMat(self.token), module='crm',
            phap_nhan_id=self.pn, hanh_dong='CRM:TIEP_NHAN:XEM', tai_lieu_id=self.tai_lieu)

    def tra(self, value):
        self.conn.execute.return_value.fetchone.return_value = (value,)

    def test_cai_dung_chu_ky_port_kho(self):
        for name, func in Kho.__dict__.items():
            if not name.startswith('_') and callable(func):
                self.assertEqual(inspect.signature(getattr(KhoMask, name)).parameters.keys(),
                                 inspect.signature(func).parameters.keys(), name)

    def test_phai_dung_ma_phien_an_khong_nhan_chu_demo_tu_khai(self):
        with self.assertRaises(ValueError):
            KhoMask(self.conn, ma=self.token, module='crm', phap_nhan_id=self.pn,
                    hanh_dong='CRM:TIEP_NHAN:XEM', tai_lieu_id=self.tai_lieu)
        self.assertNotIn(self.token, repr(self.kho))

    def test_cap_ma_bind_dung_cua_118_va_mot_transaction(self):
        self.tra(self.ma)
        with self.kho.giao_dich():
            self.assertEqual(self.kho.tao_yeu_cau(), str(self.ma))
        query, args = self.conn.execute.call_args.args
        self.assertEqual(query, 'SELECT mask.cap_ma_yeu_cau(%s,%s,%s,%s,%s,%s,%s)')
        self.assertEqual(args, (self.token, 'crm', self.pn, 'CRM:TIEP_NHAN:XEM', self.tai_lieu, None, None))
        self.assertNotIn(self.token, query)
        self.assertEqual(self.conn.transaction.call_count, 1)

    def test_chi_goi_cua_khong_sql_bang_khong_tu_ket_noi(self):
        source = inspect.getsource(inspect.getmodule(KhoMask))
        self.assertNotIn('psycopg', source)
        self.assertNotRegex(source, r'\b(?:FROM|JOIN|UPDATE|INSERT INTO)\s+mask\.')
        self.tra(self.ma)
        with self.kho.giao_dich():
            self.kho.tao_yeu_cau()
            for call, value in ((lambda: self.kho.liet_ke_dinh_danh(), []),
                                (lambda: self.kho.tra_bi_danh(chuan_hoa(TEN)), None),
                                (lambda: self.kho.tra_dinh_danh('[[kh-demo]]'), TEN)):
                self.tra(value)
                self.assertEqual(call(), value)
        for call in self.conn.execute.call_args_list:
            query, args = call.args
            self.assertRegex(query, r'^SELECT mask\.[a-z_]+\((?:%s,)*%s\)$')
            self.assertEqual(query.count('%s'), len(args))

    def test_ghi_va_gap_lai_cung_cua_dem_khong_lo_gia_tri_goc(self):
        self.tra(self.ma)
        bi_danh = self.kho.cap_bi_danh_tam()
        self.assertRegex(bi_danh, r'^\[\[MASKTAM-[0-9a-f]{32}\]\]$')
        with self.kho.giao_dich():
            self.kho.tao_yeu_cau()
            self.tra(dict(nhom='CONG_TY', bi_danh=bi_danh, nguon='tam', vua_them=True))
            muc, moi = self.kho.ghi_cho_duyet(TEN, 'CONG_TY', bi_danh, str(self.ma))
            self.assertTrue(moi)
            self.assertNotIn('vua_them', muc)
            self.assertNotIn(TEN, repr(muc))
            self.assertEqual(self.conn.execute.call_args.args[1][-4:], (TEN, 'CONG_TY', bi_danh, False))
            self.tra(dict(muc, vua_them=False))
            self.kho.ghi_nhan_gap_lai(str(self.ma), chuan_hoa(TEN), 'CONG_TY')
            self.assertEqual(self.conn.execute.call_args.args[1][-4:], (chuan_hoa(TEN), 'CONG_TY', None, True))

    def test_tham_chieu_dong_va_kiem_moi_lan_giu_ma_yeu_cau(self):
        self.tra({'trang_thai': 'DANG_XU_LY'})
        with self.kho.giao_dich():
            self.kho.doc_yeu_cau(str(self.ma))
            self.tra(True)
            self.kho.ghi_bi_danh_da_dung(str(self.ma), ['[[DEMO-001]]'])
            self.assertEqual(self.conn.execute.call_args.args[1][-2:], (self.ma, ['[[DEMO-001]]']))
            self.kho.dong_yeu_cau(str(self.ma))
            with self.assertRaises(LoiKhoMask):
                self.kho.dong_yeu_cau(str(uuid4()))
        self.assertEqual(self.conn.transaction.call_count, 3)

    def test_tra_goc_can_ma_trong_luot_va_khong_giu_ma_sau_loi(self):
        with self.assertRaises(LoiKhoMask):
            self.kho.tra_dinh_danh('[[DEMO]]')
        with self.assertRaisesRegex(RuntimeError, 'DEMO'), self.kho.giao_dich():
            self.tra(self.ma)
            self.kho.tao_yeu_cau()
            raise RuntimeError('DEMO')
        self.assertIsNone(self.kho._yeu_cau)
        with self.kho.giao_dich(), self.assertRaises(LoiKhoMask):
            self.kho.tra_dinh_danh('[[DEMO]]')
        self.assertEqual(self.conn.execute.call_count, 1)

    def test_doc_sai_yeu_cau_xoa_ngu_canh_khong_cho_tra_tiep(self):
        self.conn.execute.side_effect = RuntimeError('DEMO-LOI-DRIVER')
        with self.kho.giao_dich():
            with self.assertRaises(LoiKhoMask):
                self.kho.doc_yeu_cau(str(self.ma))
            self.assertIsNone(self.kho._yeu_cau)
            with self.assertRaises(LoiKhoMask):
                self.kho.tra_dinh_danh('[[DEMO]]')

    def test_loi_driver_va_loi_commit_khong_giu_exception_hay_tham_so(self):
        for luc in ('execute', 'commit'):
            with self.subTest(luc=luc):
                self.conn = MagicMock()
                kho = KhoMask(self.conn, ma=MaBiMat(self.token), module='crm',
                    phap_nhan_id=self.pn, hanh_dong='CRM:TIEP_NHAN:XEM', tai_lieu_id=self.tai_lieu)
                if luc == 'execute':
                    self.conn.execute.side_effect = RuntimeError(self.token + TEN)
                else:
                    self.conn.execute.return_value.fetchone.return_value = (self.ma,)
                    self.conn.transaction.return_value.__exit__.side_effect = RuntimeError(self.token + TEN)
                with kho.giao_dich(), self.assertRaises(LoiKhoMask) as caught:
                    kho.tao_yeu_cau()
                self.assertIsNone(caught.exception.__context__)
                self.assertIsNone(caught.exception.__cause__)
                self.assertNotIn(self.token, str(caught.exception))
                self.assertNotIn(TEN, str(caught.exception))

    def test_giao_dich_chi_pham_vi_ma_chua_co_chot_toan_luot(self):
        # Hạn chế lát B được kiểm rõ: hai call = hai transaction; lỗi sau
        # không tạo rollback giả cho call trước. Lát D mới thay bảo đảm này.
        self.tra(self.ma)
        with self.assertRaisesRegex(RuntimeError, 'DEMO'), self.kho.giao_dich():
            self.kho.tao_yeu_cau()
            self.tra([])
            self.kho.liet_ke_dinh_danh()
            raise RuntimeError('DEMO')
        self.assertEqual(self.conn.transaction.call_count, 2)
        for call in self.conn.transaction.return_value.__exit__.call_args_list:
            self.assertEqual(call.args, (None, None, None))

    def test_che_mo_che_qua_kho_mask_mock_du_lieu_demo(self):
        bi_danh = '[[KH-DEMO-001]]'
        muc = dict(gia_tri=TEN, nhom='CONG_TY', bi_danh=bi_danh, bi_danh_tam=None, nguon='chinh_thuc')

        def execute(query, args):
            name = query.split('mask.', 1)[1].split('(', 1)[0]
            kq = {'cap_ma_yeu_cau': self.ma, 'liet_ke_dinh_danh': [muc],
                  'liet_ke_bi_danh': [{'bi_danh': bi_danh}],
                  'tra_bi_danh': {k: v for k, v in muc.items() if k != 'gia_tri'},
                  'ghi_bi_danh_da_dung': True, 'doc_yeu_cau': {'trang_thai': 'DANG_XU_LY'},
                  'tra_dinh_danh': TEN, 'dong_yeu_cau': True}[name]
            cursor = MagicMock()
            cursor.fetchone.return_value = (kq,)
            return cursor

        self.conn.execute.side_effect = execute
        with tai_nguyen_demo():
            kq = che(VAN_BAN, None, self.kho)
            self.assertTrue(kq['gui_duoc'], kq)
            self.assertNotIn(TEN, json.dumps(kq, ensure_ascii=False))
            self.assertIn('07/11/2026', kq['van_ban_da_che'])
            mo = mo_che(kq['van_ban_da_che'], kq['ma_yeu_cau'], self.kho, dong_viec=True)
        self.assertTrue(mo['mo_day_du'])
        self.assertEqual(mo['van_ban_da_mo_che'], VAN_BAN)
        self.assertEqual(mo['trang_thai_ma_yeu_cau'], 'DA_DONG')
        calls = [call.args[0].split('mask.', 1)[1].split('(', 1)[0]
                 for call in self.conn.execute.call_args_list]
        self.assertEqual(calls.count('liet_ke_dinh_danh'), 1)
        self.assertEqual(calls.count('liet_ke_bi_danh'), 1)

    def test_mo_che_danh_sach_ma_khong_doc_goc_va_luot_sau_khong_giu_co(self):
        with self.kho.giao_dich():
            self.tra({'trang_thai': 'DANG_XU_LY'})
            self.kho.doc_yeu_cau(str(self.ma))
            self.tra([{'bi_danh': '[[DEMO-001]]'}])
            self.assertEqual(self.kho.liet_ke_dinh_danh(), [{'bi_danh': '[[DEMO-001]]'}])
            self.assertIn('mask.liet_ke_bi_danh(', self.conn.execute.call_args.args[0])
        with self.kho.giao_dich():
            self.tra(self.ma)
            self.kho.tao_yeu_cau()
            self.tra([])
            self.kho.liet_ke_dinh_danh()
            self.assertIn('mask.liet_ke_dinh_danh(', self.conn.execute.call_args.args[0])


@unittest.skipUnless(os.environ.get('KHO_PG_DSN_TEST') and importlib.util.find_spec('psycopg'),
                     'CHUA_KIEM PG MASK-3B: chỉ lead chạy; worker chỉ thuần/mock')
class PostgresTests(unittest.TestCase):
    # Dùng fixture 118 đã kiểm quyền/tài liệu; không kế thừa/chạy lặp ca 118.
    session = nen.PostgresTests.session
    cap_phien = nen.PostgresTests.cap_phien
    cap_ma = nen.PostgresTests.cap_ma
    setUp = nen.PostgresTests.setUp

    @classmethod
    def setUpClass(cls):
        nen.PostgresTests.setUpClass.__func__(cls)

    def kho(self, *, token=None, pn=None, tai_lieu=None):
        return KhoMask(self.conn, ma=MaBiMat(self.token if token is None else token), module='crm',
            phap_nhan_id=self.pn if pn is None else pn, hanh_dong=self.g209.XEM,
            tai_lieu_id=self.tai_lieu if tai_lieu is None else tai_lieu)

    def goi(self, name, ma, *args, token=None, pn=None, module='crm', hd=None, viec=None, the_he=None):
        values = (self.token if token is None else token, module, self.pn if pn is None else pn,
                  self.g209.XEM if hd is None else hd, viec, the_he, ma, *args)
        with self.session():
            return self.conn.execute('SELECT mask.'+name+'('+','.join(['%s']*len(values))+')', values).fetchone()[0]

    def cap_admin(self):
        from kho_tri_thuc.core import phien
        with self.session():
            return phien.cap_phien(self.conn, nguoi_dung_id=self.ai, module='core',
                phap_nhan_id=self.pn, dang_nhap_csdl=self.cac_thong_tin['core']['user'],
                pham_vi_hanh_dong=['CORE:MODULE:XEM', 'CORE:MODULE:DUYET', 'CORE:MODULE:SUA'],
                hieu_luc_den=datetime.now(timezone.utc)+timedelta(minutes=5)).ma.lay_de_truyen()

    # Fixture G2-06 giữ kết nối provisioning ở cls.admin; không dùng tên đó cho hàm.
    def goi_admin(self, name, *args):
        token = self.cap_admin()
        with self.session():
            return self.conn.execute('SELECT * FROM mask.'+name+'('+','.join(['%s']*(2+len(args)))+')',
                (token, self.ai, *args)).fetchone()[0]

    def test_che_mo_che_demo_khu_hoi_tam_giu_tien_ngay_va_dong(self):
        with self.session(), tai_nguyen_demo():
            kho = self.kho()
            kq = che(VAN_BAN, None, kho)
            self.assertTrue(kq['gui_duoc'], kq)
            self.assertNotIn(TEN, json.dumps(kq, ensure_ascii=False))
            mo = mo_che(kq['van_ban_da_che'], kq['ma_yeu_cau'], kho, dong_viec=True)
            self.assertEqual(mo['van_ban_da_mo_che'], VAN_BAN)
            self.assertEqual(mo['trang_thai_ma_yeu_cau'], 'DA_DONG')
            with self.assertRaises(LoiCheVanBan):
                mo_che(kq['van_ban_da_che'], kq['ma_yeu_cau'], kho)

    def test_chinh_thuc_va_bi_danh_tam_cu_tra_toan_bang_dung_vung(self):
        tam = '[[MASKTAM-' + uuid4().hex + ']]'
        self.conn.execute('INSERT INTO mask.dinh_danh(gia_tri,nhom,ma_junsky,bi_danh_tam,nguon,la_demo) '
            "VALUES(%s,'CONG_TY','KH-DEMO-001',%s,'DEMO',true)", (TEN, tam))
        with self.session(), tai_nguyen_demo():
            kho = self.kho()
            kq = che(VAN_BAN, None, kho)
            self.assertTrue(kq['gui_duoc'], kq)
            self.assertIn('[[KH-DEMO-001]]', kq['van_ban_da_che'])
            mo = mo_che(tam.lower()+'; [[kh-demo-001]]', kq['ma_yeu_cau'], kho)
            self.assertEqual(mo['van_ban_da_mo_che'], TEN+'; '+TEN)
        self.assertEqual(self.conn.execute('SELECT bi_danh_tam_da_dung FROM mask.yeu_cau WHERE id=%s',
                         (kq['ma_yeu_cau'],)).fetchone()[0], [tam])

    def test_cac_cua_giu_dung_cap_tam_khi_don_yeu_cau_con_mo(self):
        ma = self.cap_ma()
        tam = '[[MASKTAM-'+uuid4().hex+']]'
        self.goi('ghi_cho_duyet', ma, TEN, 'CONG_TY', tam, False)
        self.assertEqual(self.conn.execute('SELECT bi_danh_tam_da_dung FROM mask.yeu_cau WHERE id=%s',
                         (ma,)).fetchone()[0], [tam])
        cho = self.conn.execute('SELECT id FROM mask.cho_duyet').fetchone()[0]
        self.goi_admin('tu_choi_cho', cho)
        self.assertEqual(self.goi_admin('don_bi_danh_tam'), 0)
        for _ in range(3):
            muc = self.goi('ghi_cho_duyet', ma, TEN, 'CONG_TY', None, True)
            self.assertEqual(muc['bi_danh'], tam)
            self.assertFalse(muc['vua_them'])
        self.assertEqual(self.conn.execute('SELECT so_lan_gap,trang_thai FROM mask.cho_duyet').fetchone(),
                         (1, 'DA_TU_CHOI'))
        # Kiểm riêng cửa ghi tham chiếu với chữ thường và dạng trộn hoa/thường.
        self.conn.execute('UPDATE mask.yeu_cau SET bi_danh_tam_da_dung=ARRAY[]::text[] WHERE id=%s', (ma,))
        self.goi('ghi_bi_danh_da_dung', ma, [tam.lower(), tam.replace('MASKTAM', 'MaskTam')])
        self.assertEqual(self.goi_admin('don_bi_danh_tam'), 0)
        self.assertEqual(self.goi('tra_dinh_danh', ma, tam.lower()), TEN)
        self.assertEqual(self.conn.execute('SELECT bi_danh_tam_da_dung FROM mask.yeu_cau WHERE id=%s',
                         (ma,)).fetchone()[0], [tam])
        self.goi('dong_yeu_cau', ma)
        self.assertEqual(self.goi_admin('don_bi_danh_tam'), 1)

    def test_bi_danh_tam_da_duyet_duoc_giu_den_khi_dong_yeu_cau(self):
        ma = self.cap_ma()
        tam = '[[MASKTAM-'+uuid4().hex+']]'
        self.goi('ghi_cho_duyet', ma, TEN, 'CONG_TY', tam, False)
        cho = self.conn.execute('SELECT id FROM mask.cho_duyet').fetchone()[0]
        self.goi_admin('duyet_cho', cho, None)
        self.assertEqual(self.goi_admin('don_bi_danh_tam'), 0)
        self.conn.execute('UPDATE mask.yeu_cau SET bi_danh_tam_da_dung=ARRAY[]::text[] WHERE id=%s', (ma,))
        self.goi('ghi_bi_danh_da_dung', ma, [tam.lower()])
        self.assertEqual(self.goi_admin('don_bi_danh_tam'), 0)
        self.assertEqual(self.goi('tra_dinh_danh', ma, tam), TEN)
        self.assertEqual(self.conn.execute('SELECT bi_danh_tam FROM mask.dinh_danh').fetchone(), (tam,))
        self.goi('dong_yeu_cau', ma)
        self.assertEqual(self.goi_admin('don_bi_danh_tam'), 1)

    def test_pham_vi_doc_goc_va_audit_khong_chua_dinh_danh(self):
        ma, ma_khac = self.cap_ma(), uuid4()
        tam = '[[MASKTAM-'+uuid4().hex+']]'
        khac = 'Công ty DEMO Riêng Biệt'
        self.goi('ghi_cho_duyet', ma, TEN, 'CONG_TY', tam, False)
        self.conn.execute("INSERT INTO mask.yeu_cau(id,module,nguoi_gui,tai_lieu_id,la_demo) "
                          "VALUES(%s,'crm',%s,%s,true)", (ma_khac, uuid4(), uuid4()))
        self.conn.execute("INSERT INTO mask.cho_duyet(cum_goc,nhom,yeu_cau_id,la_demo,nguon) "
                          "VALUES(%s,'CONG_TY',%s,true,'DEMO')", (khac, ma_khac))
        danh_sach = self.goi('liet_ke_dinh_danh', ma)
        self.assertEqual([m['gia_tri'] for m in danh_sach], [TEN])
        aliases = self.goi('liet_ke_bi_danh', ma)
        self.assertEqual(len(aliases), 2)
        for muc in aliases:
            self.assertLessEqual(set(muc), {'bi_danh', 'bi_danh_tam'})
        self.assertEqual(self.goi('tra_dinh_danh', ma, tam.lower()), TEN)
        rows = self.conn.execute("SELECT to_jsonb(n) FROM loi.nhat_ky_kiem_toan n "
            "WHERE request_id=%s AND doi_tuong IN ('mask.dinh_danh.liet_ke','mask.dinh_danh.tra') ORDER BY id",
            (ma,)).fetchall()
        self.assertEqual([r[0]['doi_tuong'] for r in rows], ['mask.dinh_danh.liet_ke', 'mask.dinh_danh.tra'])
        for value in (TEN, khac, tam, self.token):
            self.assertNotIn(value, json.dumps(rows, ensure_ascii=False))

    def test_dem_gap_lai_chi_mot_lan_moi_yeu_cau_va_cum_chuan(self):
        with self.session(), tai_nguyen_demo():
            kho = self.kho()
            a = che(TEN+'; '+TEN, None, kho)
            b = che(TEN, None, kho)
            self.assertTrue(a['gui_duoc'], a)
            self.assertTrue(b['gui_duoc'], b)
            self.assertEqual(a['cho_duyet']['so_cum_vua_them'], 1)
            self.assertEqual(b['cho_duyet']['so_cum_vua_them'], 0)
            self.assertEqual(a['bi_danh'], b['bi_danh'])
            with kho.giao_dich():
                kho.doc_yeu_cau(a['ma_yeu_cau'])
                for _ in range(3):
                    kho.ghi_nhan_gap_lai(a['ma_yeu_cau'], chuan_hoa(TEN), 'CONG_TY')
                    kho.ghi_cho_duyet('  CÔNG TY DEMO ÁNH DƯƠNG  ', 'CONG_TY', kho.cap_bi_danh_tam(), a['ma_yeu_cau'])
                muc = kho.tra_bi_danh(chuan_hoa(TEN))
                self.assertEqual(muc['so_lan_gap'], 2)
                self.assertNotIn('gia_tri', muc)
        rows = self.conn.execute('SELECT cum_da_gap FROM mask.yeu_cau WHERE id IN (%s,%s)',
                                 (a['ma_yeu_cau'], b['ma_yeu_cau'])).fetchall()
        self.assertEqual(rows, [([chuan_hoa(TEN)],), ([chuan_hoa(TEN)],)])

    def test_cum_khac_cung_yeu_cau_deu_dem_mot_lan(self):
        ma = self.cap_ma()
        for ten in (TEN, 'Công ty DEMO Ngôi Sao', TEN):
            self.goi('ghi_cho_duyet', ma, ten, 'CONG_TY', '[[MASKTAM-'+uuid4().hex+']]', False)
        self.assertEqual(self.conn.execute('SELECT so_lan_gap FROM mask.cho_duyet ORDER BY cum_chuan').fetchall(),
                         [(1,), (1,)])

    def test_gap_lai_khong_tao_cum_la_va_loi_khong_de_lai_dem(self):
        ma = self.cap_ma()
        with self.assertRaises(self.pg.errors.InvalidParameterValue):
            self.goi('ghi_cho_duyet', ma, TEN, 'CONG_TY', None, True)
        tam = '[[MASKTAM-'+uuid4().hex+']]'
        self.goi('ghi_cho_duyet', ma, TEN, 'CONG_TY', tam, False)
        with self.assertRaises(self.pg.errors.InvalidParameterValue):
            self.goi('ghi_cho_duyet', ma, TEN, 'CA_NHAN', None, True)
        self.assertEqual(self.conn.execute('SELECT so_lan_gap FROM mask.cho_duyet').fetchone(), (1,))

    def test_cum_cu_truoc_119_khong_dem_lai_yeu_cau_tao(self):
        ma = self.cap_ma()
        tam = '[[MASKTAM-'+uuid4().hex+']]'
        # Dòng tạo theo 113/117, chưa có dấu cum_da_gap nhưng đã đếm lần đầu.
        self.conn.execute('INSERT INTO mask.cho_duyet(cum_goc,nhom,bi_danh_tam,yeu_cau_id,la_demo,nguon) '
                          "VALUES(%s,'CONG_TY',%s,%s,true,'DEMO')", (TEN, tam, ma))
        self.goi('ghi_cho_duyet', ma, TEN, 'CONG_TY', None, True)
        self.goi('ghi_cho_duyet', ma, TEN, 'CONG_TY', None, True)
        self.assertEqual(self.conn.execute('SELECT so_lan_gap FROM mask.cho_duyet').fetchone(), (1,))

    def test_gap_lai_chinh_thuc_dung_nhom_khong_tao_hang_cho(self):
        self.conn.execute('INSERT INTO mask.dinh_danh(gia_tri,nhom,nguon,la_demo) '
                          "VALUES(%s,'CONG_TY','DEMO',true)", (TEN,))
        ma = self.cap_ma()
        muc = self.goi('ghi_cho_duyet', ma, TEN, 'CONG_TY', None, True)
        self.assertEqual(muc['nguon'], 'chinh_thuc')
        self.assertFalse(muc['vua_them'])
        with self.assertRaises(self.pg.errors.InvalidParameterValue):
            self.goi('ghi_cho_duyet', ma, TEN, 'CA_NHAN', None, True)
        self.assertEqual(self.conn.execute('SELECT count(*) FROM mask.cho_duyet').fetchone(), (0,))

    def test_sai_chu_yeu_cau_bi_tu_choi_o_moi_cua(self):
        ma = self.cap_ma()
        ai = uuid4()
        self.conn.execute("INSERT INTO loi.nguoi_dung(id,dang_nhap,ten,vai_tro) VALUES(%s,%s,'DEMO','XEM')", (ai, ai.hex))
        self.conn.execute('INSERT INTO loi.phan_quyen(nguoi_dung_id,phap_nhan_id,module) VALUES(%s,%s,%s)',
                          (ai, self.pn, ['crm']))
        self._kiem_moi_cua_tu_choi(ma, token=self.cap_phien(ai=ai))

    def _kiem_moi_cua_tu_choi(self, ma, **kwargs):
        args = {'liet_ke_dinh_danh': (), 'liet_ke_bi_danh': (), 'tra_bi_danh': (chuan_hoa(TEN),),
                'ghi_cho_duyet': (TEN, 'CONG_TY', '[[MASKTAM-'+uuid4().hex+']]', False),
                'doc_yeu_cau': (), 'ghi_bi_danh_da_dung': ([],),
                'tra_dinh_danh': ('[[KH-DEMO-001]]',), 'dong_yeu_cau': ()}
        for name, values in args.items():
            with self.subTest(cua=name), self.assertRaises(self.pg.errors.InsufficientPrivilege):
                self.goi(name, ma, *values, **kwargs)

    def test_phien_gia_sai_module_viec_va_yeu_cau_da_dong(self):
        ma = self.cap_ma()
        for kwargs in ({'token': 'DEMO-gia'}, {'module': 'core'}, {'viec': uuid4(), 'the_he': 1}):
            self._kiem_moi_cua_tu_choi(ma, **kwargs)
        self.goi('dong_yeu_cau', ma)
        self._kiem_moi_cua_tu_choi(ma)
        self._kiem_moi_cua_tu_choi(uuid4())

    def test_sai_phap_nhan_cua_tai_lieu_va_thu_hoi_quyen_goc(self):
        ma = self.cap_ma()
        old = self.pn
        self.pn = self.fx.pn_khac
        try:
            token = self.cap_phien()
        finally:
            self.pn = old
        self._kiem_moi_cua_tu_choi(ma, token=token, pn=self.fx.pn_khac)
        self.conn.execute("INSERT INTO loi_tai_lieu.quyen_tai_lieu"
            '(phap_nhan_id,tai_lieu_id,nguoi_dung_id,bien_the,hanh_dong,so_phien_ban,cho_phep,tao_boi) '
            "VALUES(%s,%s,%s,'goc','XEM',1,false,%s)", (self.pn, self.tai_lieu, self.ai, self.ai))
        self._kiem_moi_cua_tu_choi(ma)

    def test_demo_tach_bat_chap_guc_caller_va_cung_cum_khac_bi_danh(self):
        ma_demo = self.cap_ma()
        a = self.goi('ghi_cho_duyet', ma_demo, TEN, 'CONG_TY', '[[MASKTAM-'+uuid4().hex+']]', False)
        # Fixture kế thừa đã INSERT pháp nhân mới với cờ DEMO cố định (CD-044).
        self.pn, self.tai_lieu = self.fx.pn_thuong, self.fx.tai_lieu_thuong_id
        self.token = self.cap_phien()
        self.conn.execute("SELECT set_config('ktt.mask_la_demo','true',true)")
        ma_khac = self.cap_ma()
        self.assertIsNone(self.goi('tra_bi_danh', ma_khac, chuan_hoa(TEN)))
        self.assertIsNone(self.goi('tra_dinh_danh', ma_khac, a['bi_danh']))
        b = self.goi('ghi_cho_duyet', ma_khac, TEN, 'CONG_TY', '[[MASKTAM-'+uuid4().hex+']]', False)
        self.assertNotEqual(a['bi_danh'], b['bi_danh'])
        self.assertEqual(len(self.goi('liet_ke_dinh_danh', ma_khac)), 1)
        self._kiem_moi_cua_tu_choi(ma_demo)
        self.assertEqual(self.conn.execute('SELECT la_demo,so_lan_gap FROM mask.cho_duyet ORDER BY la_demo').fetchall(),
                         [(False, 1), (True, 1)])
        self.assertEqual(self.conn.execute("SELECT current_setting('ktt.mask_la_demo')").fetchone(), ('true',))

    def test_moi_cua_khoi_phuc_guc_khi_thanh_cong_va_bi_tu_choi(self):
        ma = self.cap_ma()
        settings = ('ktt.mask_la_demo', 'ktt.module', 'ktt.phap_nhan_id', 'ktt.ma_phien',
                    'ktt.hanh_dong', 'ktt.viec_id', 'ktt.the_he')
        for setting in settings:
            self.conn.execute('SELECT set_config(%s,%s,true)', (setting, 'false' if setting==settings[0] else 'DEMO-gia'))
        def chup():
            return [self.conn.execute('SELECT current_setting(%s,true)', (s,)).fetchone()[0] for s in settings]
        before = chup()
        tam = '[[MASKTAM-'+uuid4().hex+']]'
        for name, args in (('doc_yeu_cau', ()), ('ghi_cho_duyet', (TEN, 'CONG_TY', tam, False)),
                           ('tra_bi_danh', (chuan_hoa(TEN),)), ('liet_ke_dinh_danh', ()),
                           ('liet_ke_bi_danh', ()),
                           ('ghi_bi_danh_da_dung', ([tam],)), ('tra_dinh_danh', (tam,)), ('dong_yeu_cau', ())):
            self.goi(name, ma, *args)
            self.assertEqual(chup(), before, name)
        self._kiem_moi_cua_tu_choi(ma)
        self.assertEqual(chup(), before)

    def test_acl_core_chi_execute_helper_va_bang_khong_mo_cho_module(self):
        core = self.cac_thong_tin['core']['user']
        for name, signature in PUBLIC.items():
            sig = 'mask.'+name+'('+signature+')'
            self.assertTrue(self.conn.execute("SELECT has_function_privilege(%s,%s,'EXECUTE')", (core, sig)).fetchone()[0])
            for role in (self.module_login, self.tien_to+'vai_chay_mask'):
                self.assertFalse(self.conn.execute("SELECT has_function_privilege(%s,%s,'EXECUTE')", (role, sig)).fetchone()[0])
        self.assertFalse(self.conn.execute("SELECT has_function_privilege(%s,%s,'EXECUTE')",
                         (core, 'mask.kiem_yeu_cau('+CTX+')')).fetchone()[0])
        sig = 'loi.mask_kiem_toan_doc('+CTX+',text)'
        for role in (core, self.module_login, self.tien_to+'vai_chay_mask'):
            self.assertFalse(self.conn.execute("SELECT has_function_privilege(%s,%s,'EXECUTE')", (role, sig)).fetchone()[0])
        with self.assertRaises(self.pg.errors.InsufficientPrivilege), self.session():
            self.conn.execute('SELECT * FROM mask.yeu_cau')

    def test_chay_lai_113_117_118_119_khong_doi_du_lieu_oid_acl_policy(self):
        ma = self.cap_ma()
        self.goi('ghi_cho_duyet', ma, TEN, 'CONG_TY', '[[MASKTAM-'+uuid4().hex+']]', False)
        def chup():
            return [self.conn.execute('SELECT * FROM mask.'+name+' ORDER BY id').fetchall()
                    for name in ('dinh_danh', 'cho_duyet', 'yeu_cau')] + [
                self.conn.execute('SELECT p.oid,p.proowner,p.proacl,pg_get_functiondef(p.oid) FROM pg_proc p '
                    "WHERE p.pronamespace='mask'::regnamespace ORDER BY p.oid").fetchall(),
                # So biểu thức SQL, không so cây nội bộ chứa vị trí ký tự trong nguồn.
                self.conn.execute('SELECT oid,polname,polrelid,polcmd,polpermissive,polroles,'
                    'pg_get_expr(polqual,polrelid),pg_get_expr(polwithcheck,polrelid) '
                    "FROM pg_policy WHERE polrelid IN ('mask.dinh_danh'::regclass,"
                    "'mask.cho_duyet'::regclass,'mask.yeu_cau'::regclass) ORDER BY oid").fetchall(),
                self.conn.execute("SELECT oid,proowner,proacl,pg_get_functiondef(oid) FROM pg_proc "
                    "WHERE oid='loi.mask_kiem_toan_doc("+CTX+",text)'::regprocedure").fetchall()]
        before = chup()
        for _ in range(2):
            for name in ('113_mask_dinh_danh.sql', '117_mask_duyet_cho.sql', '118_mask_phien.sql', SQL_PATH.name):
                self.conn.execute((SQL_PATH.parent/name).read_bytes().decode('utf-8', errors='strict'))
        self.assertEqual(chup(), before)

    def test_chay_lai_thu_quyen_la_va_guard_sai_dich(self):
        for name, signature in PUBLIC.items():
            self.conn.execute(self.sql.SQL('GRANT EXECUTE ON FUNCTION mask.'+name+'('+signature+') TO {} WITH GRANT OPTION')
                              .format(self.sql.Identifier(self.module_login)))
        self.conn.execute(doc_sql())
        for name, signature in PUBLIC.items():
            self.assertFalse(self.conn.execute("SELECT has_function_privilege(%s,%s,'EXECUTE')",
                (self.module_login, 'mask.'+name+'('+signature+')')).fetchone()[0])
        with self.assertRaises(self.pg.errors.RaiseException) as caught, self.conn.transaction():
            self.conn.execute("SELECT set_config('kho_tri_thuc.tien_to_vai','DEMO-sai',true)")
            self.conn.execute(doc_sql())
        self.assertEqual(caught.exception.diag.message_primary, 'MASK_KHO_SAI_DICH')


@unittest.skipUnless(os.environ.get('KHO_PG_DSN_TEST') and importlib.util.find_spec('psycopg'),
                     'CHUA_KIEM PG hai kết nối MASK-3B: chỉ lead chạy')
class PostgresHaiKetNoiTests(unittest.TestCase):
    # Fixture riêng đã commit, hai kết nối mới nhìn thấy cùng phiên/tài liệu.
    # Không kế thừa ca đơn kết nối; toàn bộ dữ liệu nằm trong kho_test_* tự sinh.
    setUpClass = classmethod(PostgresTests.setUpClass.__func__)
    session = PostgresTests.session
    cap_phien = PostgresTests.cap_phien
    cap_ma = PostgresTests.cap_ma
    goi = PostgresTests.goi
    cap_admin = PostgresTests.cap_admin
    goi_admin = PostgresTests.goi_admin

    def setUp(self):
        self.pn, self.ai = self.fx.pn, self.fx.nd
        self.tai_lieu = self.fx.tai_lieu_id
        self.token = self.cap_phien()
        self.ten = 'Công ty DEMO Đồng Thời '+uuid4().hex

    @contextmanager
    def ket_noi_thu_hai(self):
        with self.pg.connect(**self.cac_thong_tin['core'], autocommit=True) as kn:
            self.assertNotEqual(kn.info.backend_pid, self.conn.info.backend_pid,
                                'Hai kết nối phải dùng hai phiên PostgreSQL riêng.')
            kn.execute("SET lock_timeout='10s'")
            kn.execute("SET statement_timeout='15s'")
            yield kn

    def goi_kn(self, kn, name, ma, *args):
        values = (self.token, 'crm', self.pn, self.g209.XEM, None, None, ma, *args)
        return kn.execute('SELECT mask.'+name+'('+','.join(['%s']*len(values))+')', values).fetchone()[0]

    def doi_khoa(self, kn, future):
        # Xác nhận thực sự bị khóa, không chỉ gửi hai lời gọi gần nhau.
        den = monotonic()+5
        while monotonic()<den:
            if self.conn.execute('SELECT cardinality(pg_blocking_pids(%s))>0',
                                 (kn.info.backend_pid,)).fetchone()[0]:
                return
            if future.done():
                future.result()
                self.fail('Lời gọi kết thúc mà chưa chờ khóa đồng thời.')
            Event().wait(0.01)
        self.fail('Chưa quan sát được hai kết nối chờ nhau trong thời hạn.')

    def test_dem_gap_lai_hai_yeu_cau_dong_thoi_khong_mat_dem_hay_doi_cap(self):
        ma1, ma2 = self.cap_ma(), self.cap_ma()
        with self.ket_noi_thu_hai() as kn, ThreadPoolExecutor(max_workers=1) as pool:
            with self.conn.transaction():
                dau = self.goi('ghi_cho_duyet', ma1, self.ten, 'CONG_TY', '[[MASKTAM-'+uuid4().hex+']]', False)
                future = pool.submit(self.goi_kn, kn, 'ghi_cho_duyet', ma2, self.ten,
                                     'CONG_TY', '[[MASKTAM-'+uuid4().hex+']]', False)
                self.doi_khoa(kn, future)
            sau = future.result(timeout=15)
            for _ in range(3):
                self.goi_kn(kn, 'ghi_cho_duyet', ma2, self.ten, 'CONG_TY', None, True)
        self.assertEqual(dau['bi_danh'], sau['bi_danh'])
        self.assertEqual((dau['so_lan_gap'], sau['so_lan_gap']), (1, 2))
        self.assertEqual(self.conn.execute('SELECT so_lan_gap FROM mask.cho_duyet WHERE cum_chuan=mask.chuan_hoa(%s)',
                         (self.ten,)).fetchone(), (2,))
        for ma in (ma1, ma2):
            self.assertEqual(self.conn.execute('SELECT bi_danh_tam_da_dung FROM mask.yeu_cau WHERE id=%s',
                             (ma,)).fetchone()[0], [dau['bi_danh']])

    def test_duyet_dong_thoi_khong_chen_lai_cum_vua_duyet(self):
        ma1, ma2 = self.cap_ma(), self.cap_ma()
        tam = '[[MASKTAM-'+uuid4().hex+']]'
        self.goi('ghi_cho_duyet', ma1, self.ten, 'CONG_TY', tam, False)
        cho = self.conn.execute('SELECT id FROM mask.cho_duyet WHERE bi_danh_tam=%s', (tam,)).fetchone()[0]
        with self.ket_noi_thu_hai() as kn, ThreadPoolExecutor(max_workers=1) as pool:
            with self.conn.transaction():
                self.goi_admin('duyet_cho', cho, None)
                future = pool.submit(self.goi_kn, kn, 'ghi_cho_duyet', ma2, self.ten,
                                     'CONG_TY', '[[MASKTAM-'+uuid4().hex+']]', False)
                self.doi_khoa(kn, future)
            muc = future.result(timeout=15)
        self.assertEqual(muc['nguon'], 'chinh_thuc')
        self.assertFalse(muc['vua_them'])
        self.assertEqual(muc['bi_danh_tam'], tam)
        self.assertEqual(self.conn.execute('SELECT count(*) FROM mask.cho_duyet WHERE cum_chuan=mask.chuan_hoa(%s)',
                         (self.ten,)).fetchone(), (0,))

    def test_don_dong_thoi_doi_ghi_tham_chieu_va_giu_cap_tam_con_mo(self):
        ma = self.cap_ma()
        tam = '[[MASKTAM-'+uuid4().hex+']]'
        self.conn.execute("INSERT INTO mask.dinh_danh(gia_tri,nhom,bi_danh_tam,nguon,la_demo) "
                          "VALUES(%s,'CONG_TY',%s,'DEMO',true)", (self.ten, tam))
        token_admin = self.cap_admin()
        with self.ket_noi_thu_hai() as kn, ThreadPoolExecutor(max_workers=1) as pool:
            with self.conn.transaction():
                self.goi('ghi_bi_danh_da_dung', ma, [tam.lower()])
                future = pool.submit(lambda: kn.execute('SELECT mask.don_bi_danh_tam(%s,%s)',
                                                       (token_admin, self.ai)).fetchone()[0])
                self.doi_khoa(kn, future)
            self.assertEqual(future.result(timeout=15), 0)
        self.assertEqual(self.conn.execute('SELECT bi_danh_tam FROM mask.dinh_danh WHERE gia_tri_chuan=mask.chuan_hoa(%s)',
                         (self.ten,)).fetchone(), (tam,))
        self.assertEqual(self.conn.execute('SELECT bi_danh_tam_da_dung FROM mask.yeu_cau WHERE id=%s',
                         (ma,)).fetchone()[0], [tam])
        self.goi('dong_yeu_cau', ma)
        self.assertEqual(self.goi_admin('don_bi_danh_tam'), 1)


class FixtureThuanTests(unittest.TestCase):
    def test_cua_quan_tri_khong_trung_ket_noi_admin_cua_fixture(self):
        def chuan_bi_gia(cls):
            cls.admin = object()  # Connection của fixture không phải callable.
            cls.conn = MagicMock()

        with patch.object(nen, 'chuan_bi_phien', side_effect=chuan_bi_gia):
            for base in (PostgresTests, PostgresHaiKetNoiTests):
                with self.subTest(lop=base.__name__):
                    lop = type('FixtureDemo', (base,), {})
                    lop.setUpClass()
                    ca = lop(methodName='runTest')
                    ca.ai, cho = uuid4(), uuid4()
                    ca.cap_admin = MagicMock(return_value='DEMO-phien-quan-tri')
                    ca.session = MagicMock()
                    ca.conn.execute.return_value.fetchone.return_value = (1,)
                    self.assertEqual(ca.goi_admin('duyet_cho', cho, None), 1)
                    ca.cap_admin.assert_called_once_with()
                    ca.session.assert_called_once_with()
                    ca.conn.execute.assert_called_once_with(
                        'SELECT * FROM mask.duyet_cho(%s,%s,%s,%s)',
                        ('DEMO-phien-quan-tri', ca.ai, cho, None))
                    self.assertFalse(callable(ca.admin))

    def test_ket_noi_thu_hai_mo_moi_va_tu_choi_backend_dung_chung(self):
        for pid in (102, 101):
            with self.subTest(backend_thu_hai=pid):
                ca = PostgresHaiKetNoiTests(methodName='runTest')
                ca.pg, ca.conn = MagicMock(), MagicMock()
                ca.conn.info.backend_pid = 101
                ca.cac_thong_tin = {'core': dict(host='127.0.0.1', dbname='kho_test_demo',
                    user='demo_dang_nhap_loi', password='DEMO')}
                kn = ca.pg.connect.return_value.__enter__.return_value
                kn.info.backend_pid = pid
                if pid == 101:
                    with self.assertRaisesRegex(AssertionError, 'hai phiên PostgreSQL riêng'):
                        with ca.ket_noi_thu_hai():
                            self.fail('Không được dùng chung backend.')
                    kn.execute.assert_not_called()
                else:
                    with ca.ket_noi_thu_hai() as moi:
                        self.assertIs(moi, kn)
                    self.assertEqual([c.args[0] for c in kn.execute.call_args_list],
                                     ["SET lock_timeout='10s'", "SET statement_timeout='15s'"])
                ca.pg.connect.assert_called_once_with(**ca.cac_thong_tin['core'], autocommit=True)
                ca.pg.connect.return_value.__exit__.assert_called_once()


if __name__ == '__main__':
    unittest.main()
