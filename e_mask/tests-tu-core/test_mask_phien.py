"""MASK-3-PHIEN: kiểm byte SQL; PG chỉ lead chạy trên dữ liệu tự sinh DEMO.

Không đọc cấu hình, không khởi động dịch vụ, không dùng kho/dữ liệu thật.
"""

from contextlib import contextmanager, nullcontext
from datetime import datetime, timedelta, timezone
import importlib.util
import json
import os
from pathlib import Path
import re
import unicodedata
import unittest
from unittest.mock import MagicMock
from uuid import uuid4

from tests.test_mask_4a import kiem_cau_truc_sql, token_sql


ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = ROOT / 'src/kho_tri_thuc/core/sql/118_mask_phien.sql'
CU = 'mask.cap_ma_yeu_cau(text,uuid,uuid,boolean)'
MOI = 'mask.cap_ma_yeu_cau(text,text,uuid,text,uuid,uuid,bigint)'
NGU_CANH = 'loi.mask_ngu_canh(text,text,uuid,text,uuid,bigint)'
TAI_LIEU = 'loi_tai_lieu.mask_kiem_tai_lieu(text,text,uuid,text,uuid,uuid,bigint)'


def doc_sql():
    return SQL_PATH.read_bytes().decode('utf-8', errors='strict')


def cac_ham(sql):
    return dict(re.findall(
        r'CREATE OR REPLACE FUNCTION ([a-z_]+\.[a-z_]+)\(.*?'
        r'AS \$ham\$(.*?)\$ham\$;', sql, re.S))


def tao_fixture_tai_lieu(fx):
    """Theo fixture G2-09; cờ DEMO đặt ngay INSERT, trước MTQ/tài liệu."""
    fx.nd, fx.pn, fx.pn_khac, fx.pn_thuong = (uuid4() for _ in range(4))
    fx.conn.execute("INSERT INTO loi.nguoi_dung(id,dang_nhap,ten,vai_tro) VALUES(%s,%s,'DEMO','XEM')",
                    (fx.nd, 'demo_'+fx.nd.hex))
    for pn, la_demo in ((fx.pn, True), (fx.pn_khac, True), (fx.pn_thuong, False)):
        fx.conn.execute("INSERT INTO loi.phap_nhan(id,ma,ten,la_demo) VALUES(%s,%s,'DEMO',%s)",
                        (pn, pn.hex, la_demo))
        fx.conn.execute('INSERT INTO loi.phan_quyen(nguoi_dung_id,phap_nhan_id,module) VALUES(%s,%s,%s)',
                        (fx.nd, pn, ['crm', 'core']))
        phong, pb, dong, gan = (uuid4() for _ in range(4))
        fx.conn.execute("INSERT INTO loi.mtq_phong(id,phap_nhan_id,ma,ten) VALUES(%s,%s,'DEMO','DEMO')",
                        (phong, pn))
        fx.conn.execute("INSERT INTO loi.mtq_phien_ban(id,phap_nhan_id,so_phien_ban,tao_boi,ly_do) "
                        "VALUES(%s,%s,1,%s,'DEMO')", (pb, pn, fx.nd))
        for vai in ('CFO', 'THUC_HIEN_1', 'THUC_HIEN_2', 'TRUONG_PHONG', 'NGUOI_XEM'):
            fx.conn.execute('INSERT INTO loi.mtq_dong(id,phien_ban_id,phap_nhan_id,phong_id,vai) VALUES(%s,%s,%s,%s,%s)',
                            (dong if vai == 'CFO' else uuid4(), pb, pn, phong, vai))
        for hd in ('XEM', 'LAP', 'SUA', 'DUYET'):
            fx.conn.execute("INSERT INTO loi.mtq_o(dong_id,module,man,hanh_dong,cho_phep) "
                            "VALUES(%s,'CRM','TIEP_NHAN',%s,true)", (dong, hd))
        fx.conn.execute("UPDATE loi.mtq_phien_ban SET trang_thai='DA_CONG_BO',cong_bo_boi=%s,"
                        "cong_bo_luc=now(),phien_ban_dong=2 WHERE id=%s", (fx.nd, pb))
        fx.conn.execute("INSERT INTO loi.mtq_gan_vai(id,nguoi_dung_id,phap_nhan_id,phong_id,vai,cap_boi,ly_do) "
                        "VALUES(%s,%s,%s,%s,'CFO',%s,'DEMO')", (gan, fx.nd, pn, phong, fx.nd))
        fx.conn.execute("INSERT INTO loi.mtq_pham_vi(gan_vai_id,phap_nhan_id,loai,khoa,cap_boi,ly_do) "
                        "VALUES(%s,%s,'PHAP_NHAN',%s,%s,'DEMO')", (gan, pn, str(pn), fx.nd))
        fx.conn.execute('INSERT INTO loi.mtq_kich_hoat(phap_nhan_id,bat,phien_ban_id,bat_boi,bat_luc) '
                        'VALUES(%s,true,%s,%s,now())', (pn, pb, fx.nd))
        fx.conn.execute("INSERT INTO loi.module_cong_tac(module,phap_nhan_id,phien_ban_dong,che_do,tao_boi) "
                        "VALUES('crm',%s,1,'VAN_HANH',%s)", (pn, fx.nd))
    fx.conn.execute("INSERT INTO loi.mtq_admin(nguoi_dung_id,cap_boi,ly_do) VALUES(%s,%s,'DEMO')", (fx.nd, fx.nd))
    pn_demo = fx.pn
    for pn in (pn_demo, fx.pn_thuong):
        fx.pn, fx.obj, fx.tai_lieu_id = pn, uuid4(), uuid4()
        # Mỗi đối tượng chỉ trỏ một pháp nhân, không trộn DEMO với vùng thường.
        fx.conn.execute('INSERT INTO mod_crm.doi_tuong(id,tap) VALUES(%s,%s::jsonb)',
                        (fx.obj, json.dumps([dict(pn=str(pn), hop_le=True, loai='TIEP_NHAN', so_tien_vnd='0')])))
        fx.ma = fx._cap()
        fx._tao()
        if pn == pn_demo:
            obj_demo, tai_lieu_demo, ma_demo = fx.obj, fx.tai_lieu_id, fx.ma
        else:
            fx.tai_lieu_thuong_id = fx.tai_lieu_id
    fx.pn, fx.obj, fx.tai_lieu_id, fx.ma = pn_demo, obj_demo, tai_lieu_demo, ma_demo


def chuan_bi_phien(cls):
    from tests import test_g2_09 as g209
    # Dùng provisioning/resolver/contract G2-09 trước khi các cửa cũ bị siết.
    g209.TaiLieuPostgresTest.setUpClass.__func__(cls)
    cls.fx = g209.TaiLieuPostgresTest(methodName='runTest')
    for name in ('conn', 'core', 'cai_dat', 'tien_to', 'cac_thong_tin'):
        setattr(cls.fx, name, getattr(cls, name))
    cls.fx._resolver()
    cls.fx.ct = cls.fx._contract('crm', ma='demo_'+uuid4().hex[:10])
    # 023 mới có cột la_demo; tạo pháp nhân mới trước MTQ/tài liệu, không UPDATE cờ.
    g209.dc.ap_doi_cau_truc(cls.conn, so_phien_ban=23)
    tao_fixture_tai_lieu(cls.fx)
    g209.dc.ap_doi_cau_truc(cls.conn)
    cls.g209, cls.pg, cls.sql = g209, g209.psycopg, g209.sql


class SQLThuanTests(unittest.TestCase):
    def test_utf8_nfc_nguyen_byte_khong_bom_hay_mat_dau(self):
        raw = SQL_PATH.read_bytes()
        text = doc_sql()
        self.assertFalse(raw.startswith(b'\xef\xbb\xbf'))
        self.assertEqual(text.encode('utf-8'), raw)
        self.assertNotIn('\ufffd', text)
        self.assertEqual(unicodedata.normalize('NFC', text), text)
        self.assertIn('xác minh phiên', text)

    def test_118_duy_nhat_va_chuoi_migration_doc_dung_byte(self):
        from kho_tri_thuc.core.doi_cau_truc import _doc_chuoi
        files = list(SQL_PATH.parent.glob('[0-9][0-9][0-9]_*.sql'))
        self.assertEqual([p.name for p in files if p.name.startswith('118_')], [SQL_PATH.name])
        self.assertEqual(_doc_chuoi(files)[118][0], doc_sql())

    def test_tag_khoi_case_va_execute_format_tren_byte_goc(self):
        raw = SQL_PATH.read_bytes()
        kiem_cau_truc_sql(raw)
        self.assertEqual(re.findall(rb'\$[A-Za-z_]*\$', raw),
                         [b'$migration$'] + [b'$ham$'] * 6 + [b'$migration$'])
        self.assertEqual(set(cac_ham(doc_sql())), {
            'loi.mask_ngu_canh', 'loi_tai_lieu.mask_kiem_tai_lieu', 'mask.cap_ma_yeu_cau'})

    def test_guard_chan_dich_truoc_ddl_khop_113_117(self):
        sql = doc_sql()
        guard = sql[:sql.index("PERFORM set_config('search_path'")]
        for text in ('^kho_test_', 'kho_core_demo_g2_', '160000', "vai_cu<>'none'",
                     'rolsuper', 'rolbypassrls', 'rolcanlogin', 'pg_auth_members',
                     'relrowsecurity AND relforcerowsecurity', "polname='vung_demo'",
                     "polname<>'vung_demo'", 'MASK_PHIEN_SAI_OWNER', CU,
                     'loi.mask_kiem_admin(text,uuid,text,uuid)',
                     'loi.xac_minh_phien(text,text,uuid,text,uuid,bigint)'):
            self.assertIn(text, guard)
        self.assertNotIn('CREATE OR REPLACE FUNCTION', guard)

    def test_definer_path_acl_chi_core_va_helper_chi_owner_mask(self):
        sql = doc_sql()
        self.assertEqual(sql.count('SECURITY DEFINER SET search_path=pg_catalog,pg_temp'), 3)
        self.assertIn('REVOKE ALL ON FUNCTION %s FROM PUBLIC', sql)
        self.assertIn('aclexplode(b.proacl)', sql)
        self.assertIn("'GRANT EXECUTE ON FUNCTION %s TO %I',ck,login", sql)
        self.assertIn("'GRANT EXECUTE ON FUNCTION %s TO %I',ck,chu_mask", sql)
        self.assertNotRegex(sql, r'GRANT (?:SELECT|INSERT|UPDATE|DELETE|REFERENCES)')
        self.assertNotIn('ALTER POLICY', sql)

    def test_danh_tinh_demo_suy_tu_phien_khong_nhan_co_tu_khai(self):
        sql = doc_sql()
        helper = cac_ham(sql)['loi.mask_ngu_canh']
        self.assertIn('session_user::text', helper)
        self.assertIn('loi.xac_minh_phien(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he)', helper)
        self.assertIn('n.id=ctx.phap_nhan_id', helper)
        self.assertIn('ctx.nguoi_dung_id,n.id,n.la_demo', helper)
        self.assertLess(helper.index('loi.xac_minh_phien('), helper.index('n.la_demo'))
        self.assertIn('ctx.nguoi_dung_id IS NULL', helper)
        self.assertIn('upper(p_module COLLATE "und-x-icu")', helper)
        self.assertNotIn('p_la_demo', sql)
        self.assertNotIn('p_nguoi_gui', sql)

    def test_tai_lieu_dung_module_phap_nhan_va_quyen_hien_hanh(self):
        helper = cac_ham(doc_sql())['loi_tai_lieu.mask_kiem_tai_lieu']
        for text in ('loi_tai_lieu.ngu_canh(', 'tl.id=p_tai_lieu', 'tl.module=p_module',
                     'tl.phap_nhan_id=p_pn', 'loi_tai_lieu.kiem_quyen(', "'cho_xem'",
                     'loi_tai_lieu.duoc_xem_noi_dung(p_tai_lieu,ai,\'goc\')'):
            self.assertIn(text, helper)
        self.assertLess(helper.index('loi_tai_lieu.ngu_canh('), helper.index('FROM loi_tai_lieu.tai_lieu'))
        for setting in ('ma_phien', 'module', 'phap_nhan_id', 'hanh_dong', 'viec_id', 'the_he'):
            self.assertIn("current_setting('ktt." + setting + "',true)", helper)
            self.assertIn("set_config('ktt." + setting + "',coalesce(", helper)

    def test_guc_demo_dat_sau_hai_lan_kiem_va_khoi_phuc(self):
        body = cac_ham(doc_sql())['mask.cap_ma_yeu_cau']
        set_demo = body.index("set_config('ktt.mask_la_demo',ctx.la_demo::text,true)")
        self.assertLess(body.index('loi.mask_ngu_canh('), set_demo)
        self.assertLess(body.index('loi_tai_lieu.mask_kiem_tai_lieu('), set_demo)
        self.assertLess(set_demo, body.index('INSERT INTO mask.yeu_cau'))
        self.assertIn('VALUES(p_module,ctx.nguoi_gui,p_tai_lieu,ctx.la_demo)', body)
        self.assertLess(body.index('RETURNING id INTO ma'),
                        body.index("set_config('ktt.mask_la_demo',coalesce(cu,''),true)"))
        self.assertIn('RETURN ma;', body)

    def test_khep_cua_cu_chi_revoke_caller_giu_owner_cho_validator_113(self):
        sql = doc_sql()
        self.assertIn('REVOKE EXECUTE ON FUNCTION ' + CU + ' FROM PUBLIC CASCADE', sql)
        self.assertIn('aclexplode(coalesce(p.proacl,acldefault(\'f\',p.proowner)))', sql)
        self.assertIn('REVOKE EXECUTE ON FUNCTION ' + CU + ' FROM %I CASCADE', sql)
        self.assertIn('AND a.grantee<>0 AND a.grantee<>p.proowner LOOP', sql)
        self.assertNotIn('CREATE OR REPLACE FUNCTION mask.cap_ma_yeu_cau(p_module', sql)
        self.assertNotRegex(sql, r'\bALTER FUNCTION\b')
        self.assertNotIn('GRANT EXECUTE ON FUNCTION ' + CU, sql)

    def test_fixture_tao_moi_demo_va_thuong_khong_doi_co(self):
        fx = MagicMock()
        tao_fixture_tai_lieu(fx)
        calls = [c.args for c in fx.conn.execute.call_args_list]
        phap_nhan = [ts for cau, ts in calls if cau.startswith('INSERT INTO loi.phap_nhan(')]
        self.assertEqual([(ts[0], ts[2]) for ts in phap_nhan],
                         [(fx.pn, True), (fx.pn_khac, True), (fx.pn_thuong, False)])
        self.assertFalse(any(re.search(r'UPDATE\s+loi\.phap_nhan\s+SET\s+la_demo', cau, re.I)
                             for cau, _ in calls))
        self.assertNotEqual(fx.tai_lieu_id, fx.tai_lieu_thuong_id)
        self.assertEqual(fx._tao.call_count, 2)
        doi_tuong = [json.loads(ts[1]) for cau, ts in calls if cau.startswith('INSERT INTO mod_crm.doi_tuong')]
        self.assertEqual([[d['pn'] for d in tap] for tap in doi_tuong], [[str(fx.pn)], [str(fx.pn_thuong)]])

    def test_khong_trung_bien_declare_va_bi_danh_bang(self):
        for name, body in cac_ham(doc_sql()).items():
            declarations = body.split('BEGIN', 1)[0]
            variables = set(re.findall(r'(?:DECLARE|;)\s*([a-z_]+)\s+', declarations))
            aliases = set(re.findall(r'\b(?:FROM|JOIN)\s+[a-z_]+\.[a-z_]+\s+([a-z_]+)\b', body))
            self.assertFalse(variables & aliases, (name, variables & aliases))

    def test_guard_cau_truc_bat_tag_case_va_khoi_hong(self):
        raw = SQL_PATH.read_bytes()
        newline = b'\r\n' if b'\r\n' in raw else b'\n'
        mutations = [raw.replace(b'$ham$;', b'$ham$' , 1),
                     raw.replace(b'END;'+newline+b'$migration$;', b'END'+newline+b'$migration$;'),
                     raw.replace(b'<>(CASE WHEN', b'<>CASE WHEN', 1).replace(b'ELSE chu_mask END)', b'ELSE chu_mask END', 1)]
        for broken in mutations:
            self.assertNotEqual(raw, broken)
            with self.assertRaises(AssertionError):
                kiem_cau_truc_sql(broken)

    def test_khong_xoa_du_lieu_khong_doi_113_117_hay_capability(self):
        tokens, _ = token_sql(SQL_PATH.read_bytes())
        self.assertEqual(tokens, [b'DO', b'$BODY$', b';'])
        sql = doc_sql()
        self.assertNotRegex(sql, r'\b(?:DROP|TRUNCATE|DELETE|UPDATE|CREATE TABLE|ALTER TABLE)\b')
        self.assertNotIn('INSERT INTO loi.', sql)
        self.assertIn("set_config('search_path',path_cu,true)", sql)
        self.assertIn("set_config('role',vai_cu,true)", sql)

    def test_loi_goi_bind_khong_chen_ma_phien_vao_sql(self):
        pg = PostgresTests(methodName='runTest')
        pg.conn, pg.g209 = MagicMock(), MagicMock()
        pg.session = lambda role=None: nullcontext()
        pg.token, pg.pn, pg.tai_lieu = "DEMO'); SELECT 'gia", uuid4(), uuid4()
        pg.g209.XEM = 'CRM:TIEP_NHAN:XEM'
        pg.cap_ma()
        query, values = pg.conn.execute.call_args.args
        self.assertEqual(query, 'SELECT mask.cap_ma_yeu_cau(%s,%s,%s,%s,%s,%s,%s)')
        self.assertEqual(values, (pg.token, 'crm', pg.pn, pg.g209.XEM, pg.tai_lieu, None, None))
        self.assertNotIn(pg.token, query)


@unittest.skipUnless(os.environ.get('KHO_PG_DSN_TEST') and importlib.util.find_spec('psycopg'),
                     'CHUA_KIEM PG MASK-3-PHIEN: chỉ lead chạy; worker chỉ thuần/mock')
class PostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chuan_bi_phien(cls)

    def setUp(self):
        self.enterContext(self.conn.transaction(force_rollback=True))
        self.pn, self.ai = self.fx.pn, self.fx.nd
        self.tai_lieu = self.fx.tai_lieu_id
        self.token = self.cap_phien()

    @contextmanager
    def session(self, role=None):
        with self.conn.transaction():
            self.conn.execute(self.sql.SQL('SET LOCAL SESSION AUTHORIZATION {}').format(
                self.sql.Identifier(role or self.cac_thong_tin['core']['user'])))
            try:
                yield
            finally:
                if self.conn.info.transaction_status != self.pg.pq.TransactionStatus.INERROR:
                    self.conn.execute('RESET SESSION AUTHORIZATION')

    def cap_phien(self, *, ai=None, pn=None, actions=None, **kwargs):
        from kho_tri_thuc.core import phien
        # Phiên con luôn kết thúc trước phiên gốc đã cấp ở setUp.
        han = kwargs.pop('hieu_luc_den', datetime.now(timezone.utc)+timedelta(
            minutes=2 if kwargs.get('loai', '').startswith('UY_NHIEM') else 5))
        with self.session():
            return phien.cap_phien(self.conn, nguoi_dung_id=ai or self.ai,
                module='crm', phap_nhan_id=self.pn if pn is None else pn,
                dang_nhap_csdl=kwargs.pop('dang_nhap_csdl', self.cac_thong_tin['core']['user']),
                pham_vi_hanh_dong=actions or [self.g209.XEM, self.g209.LAP],
                hieu_luc_den=han,
                **kwargs).ma.lay_de_truyen()

    def cap_ma(self, *, token=None, module='crm', pn=None, hd=None, tai_lieu=None,
               viec=None, the_he=None, role=None):
        with self.session(role):
            return self.conn.execute('SELECT mask.cap_ma_yeu_cau(%s,%s,%s,%s,%s,%s,%s)',
                (self.token if token is None else token, module, self.pn if pn is None else pn,
                 self.g209.XEM if hd is None else hd,
                 self.tai_lieu if tai_lieu is None else tai_lieu, viec, the_he)).fetchone()[0]

    def bi_tu_choi(self, **kwargs):
        before = self.conn.execute('SELECT count(*) FROM mask.yeu_cau').fetchone()
        with self.assertRaises(self.pg.errors.InsufficientPrivilege):
            self.cap_ma(**kwargs)
        self.assertEqual(self.conn.execute('SELECT count(*) FROM mask.yeu_cau').fetchone(), before)

    def test_phien_gia_sai_module_phap_nhan_hanh_dong_va_the_he(self):
        for kwargs in ({'token': 'DEMO-phien-gia'}, {'token': ''}, {'module': 'core'},
                       {'pn': self.fx.pn_khac}, {'hd': self.g209.DUYET},
                       {'viec': uuid4(), 'the_he': 1}, {'the_he': 1}):
            with self.subTest(kwargs=kwargs):
                self.bi_tu_choi(**kwargs)

    def test_phien_het_han_va_thu_hoi_bi_tu_choi(self):
        for column, value in (('hieu_luc_den', datetime.now(timezone.utc)-timedelta(seconds=1)),
                              ('thu_hoi_luc', datetime.now(timezone.utc))):
            with self.subTest(column=column), self.conn.transaction(force_rollback=True):
                if column == 'hieu_luc_den':
                    self.conn.execute("UPDATE loi.phien_xac_thuc SET tao_luc=%s "
                        "WHERE ma_bam=sha256(convert_to(%s,'UTF8'))", (value-timedelta(minutes=1), self.token))
                self.conn.execute(self.sql.SQL('UPDATE loi.phien_xac_thuc SET {}=%s '
                    'WHERE ma_bam=sha256(convert_to(%s,\'UTF8\'))').format(self.sql.Identifier(column)),
                    (value, self.token))
                self.bi_tu_choi()

    def test_phien_nguoi_khac_khong_duoc_dung_tai_lieu(self):
        ai = uuid4()
        self.conn.execute("INSERT INTO loi.nguoi_dung(id,dang_nhap,ten,vai_tro) VALUES(%s,%s,'DEMO','XEM')",
                          (ai, ai.hex))
        self.conn.execute('INSERT INTO loi.phan_quyen(nguoi_dung_id,phap_nhan_id,module) VALUES(%s,%s,%s)',
                          (ai, self.pn, ['crm']))
        self.bi_tu_choi(token=self.cap_phien(ai=ai))

    def test_phien_rang_buoc_login_csdl(self):
        from kho_tri_thuc.core.phien import MaBiMat
        token = self.cap_phien(loai='UY_NHIEM_PHIEN', ma_goc=MaBiMat(self.token),
                              dang_nhap_csdl=self.module_login)
        self.bi_tu_choi(token=token)

    def test_mat_quyen_module_khong_duoc_cap_ma(self):
        self.conn.execute('UPDATE loi.phan_quyen SET module=%s WHERE nguoi_dung_id=%s AND phap_nhan_id=%s',
                          (['core'], self.ai, self.pn))
        self.bi_tu_choi()

    def test_tai_lieu_khong_ton_tai_hoac_sai_phap_nhan_bi_tu_choi(self):
        self.bi_tu_choi(tai_lieu=uuid4())
        token = self.cap_phien()
        from kho_tri_thuc.core import phien
        with self.session():
            khac = phien.cap_phien(self.conn, nguoi_dung_id=self.ai, module='crm',
                phap_nhan_id=self.fx.pn_khac, dang_nhap_csdl=self.cac_thong_tin['core']['user'],
                pham_vi_hanh_dong=[self.g209.XEM],
                hieu_luc_den=datetime.now(timezone.utc)+timedelta(minutes=5)).ma.lay_de_truyen()
        self.bi_tu_choi(token=khac, pn=self.fx.pn_khac)
        self.assertNotEqual(token, khac)

    def test_thu_hoi_quyen_noi_dung_goc_bi_tu_choi(self):
        # Nhật ký quyền bất biến: sự kiện riêng goc ưu tiên hơn quyền '*'.
        self.conn.execute("""INSERT INTO loi_tai_lieu.quyen_tai_lieu
            (phap_nhan_id,tai_lieu_id,nguoi_dung_id,bien_the,hanh_dong,so_phien_ban,cho_phep,tao_boi)
            VALUES(%s,%s,%s,'goc','XEM',1,false,%s)""",
            (self.pn, self.tai_lieu, self.ai, self.ai))
        self.bi_tu_choi()

    def test_demo_tu_phien_bat_chap_guc_gia_va_khoi_phuc_du_ngu_canh(self):
        settings = ('ktt.mask_la_demo', 'ktt.ma_phien', 'ktt.module', 'ktt.phap_nhan_id',
                    'ktt.hanh_dong', 'ktt.viec_id', 'ktt.the_he')
        for setting in settings:
            self.conn.execute('SELECT set_config(%s,%s,true)', (setting, 'false' if setting==settings[0] else 'DEMO-gia'))
        before = [self.conn.execute('SELECT current_setting(%s,true)', (s,)).fetchone()[0] for s in settings]
        ma = self.cap_ma()
        self.assertEqual(self.conn.execute('SELECT module,nguoi_gui,tai_lieu_id,la_demo FROM mask.yeu_cau WHERE id=%s',
                         (ma,)).fetchone(), ('crm', self.ai, self.tai_lieu, True))
        self.assertEqual([self.conn.execute('SELECT current_setting(%s,true)', (s,)).fetchone()[0]
                          for s in settings], before)

    def test_loi_tai_lieu_khoi_phuc_guc_va_khong_cap_ma(self):
        self.conn.execute("SELECT set_config('ktt.mask_la_demo','false',true),set_config('ktt.module','DEMO-cu',true)")
        self.bi_tu_choi(tai_lieu=uuid4())
        self.assertEqual(self.conn.execute("SELECT current_setting('ktt.mask_la_demo'),current_setting('ktt.module')").fetchone(),
                         ('false', 'DEMO-cu'))

    def test_co_demo_tu_khai_khong_doi_vung_phap_nhan(self):
        # Vẫn chỉ dữ liệu tự sinh trong kho_test_*, không nối kho vận hành.
        token = self.cap_phien(pn=self.fx.pn_thuong)
        self.conn.execute("SELECT set_config('ktt.mask_la_demo','true',true)")
        ma = self.cap_ma(token=token, pn=self.fx.pn_thuong, tai_lieu=self.fx.tai_lieu_thuong_id)
        self.assertEqual(self.conn.execute('SELECT nguoi_gui,tai_lieu_id,la_demo FROM mask.yeu_cau WHERE id=%s',
                         (ma,)).fetchone(), (self.ai, self.fx.tai_lieu_thuong_id, False))
        self.assertEqual(self.conn.execute("SELECT current_setting('ktt.mask_la_demo')").fetchone(), ('true',))

    def test_uy_nhiem_phien_suy_dung_nguoi_gui_va_demo(self):
        from kho_tri_thuc.core.phien import MaBiMat
        token = self.cap_phien(loai='UY_NHIEM_PHIEN', ma_goc=MaBiMat(self.token))
        ma = self.cap_ma(token=token)
        self.assertEqual(self.conn.execute('SELECT nguoi_gui,la_demo FROM mask.yeu_cau WHERE id=%s',
                         (ma,)).fetchone(), (self.ai, True))

    def test_cua_cu_giu_ham_nhung_core_va_module_khong_goi_duoc(self):
        self.assertIsNotNone(self.conn.execute('SELECT to_regprocedure(%s)', (CU,)).fetchone()[0])
        self.assertTrue(self.conn.execute('SELECT has_function_privilege(%s,%s,\'EXECUTE\')',
                        (self.tien_to+'vai_doi_cau_truc_mask', CU)).fetchone()[0])
        for role in (self.cac_thong_tin['core']['user'], self.module_login):
            self.assertFalse(self.conn.execute('SELECT has_function_privilege(%s,%s,\'EXECUTE\')',
                             (role, CU)).fetchone()[0])
            with self.assertRaises(self.pg.errors.InsufficientPrivilege), self.session(role):
                self.conn.execute('SELECT mask.cap_ma_yeu_cau(%s,%s,%s,%s)',
                                  ('crm', self.ai, self.tai_lieu, True))

    def test_acl_cua_moi_helper_va_bang_khong_mo_cho_module(self):
        core = self.cac_thong_tin['core']['user']
        self.assertTrue(self.conn.execute('SELECT has_function_privilege(%s,%s,\'EXECUTE\')', (core, MOI)).fetchone()[0])
        for role in (core, self.module_login, self.tien_to+'vai_chay_mask'):
            for signature in (NGU_CANH, TAI_LIEU):
                self.assertFalse(self.conn.execute('SELECT has_function_privilege(%s,%s,\'EXECUTE\')',
                                 (role, signature)).fetchone()[0])
        for role in (self.module_login, self.tien_to+'vai_chay_mask'):
            self.assertFalse(self.conn.execute('SELECT has_function_privilege(%s,%s,\'EXECUTE\')', (role, MOI)).fetchone()[0])
        self.bi_tu_choi(role=self.module_login)
        with self.assertRaises(self.pg.errors.InsufficientPrivilege), self.session():
            self.conn.execute('SELECT * FROM mask.yeu_cau')

    def test_chay_lai_118_khong_doi_du_lieu_oid_acl_policy(self):
        self.cap_ma()

        def chup():
            return [self.conn.execute('SELECT * FROM mask.yeu_cau ORDER BY id').fetchall(),
                self.conn.execute("""SELECT p.oid,p.proowner,p.proacl,pg_get_functiondef(p.oid)
                    FROM pg_proc p WHERE p.oid IN (%s::regprocedure,%s::regprocedure,%s::regprocedure,%s::regprocedure)
                    ORDER BY p.oid""", (CU, MOI, NGU_CANH, TAI_LIEU)).fetchall(),
                self.conn.execute("SELECT * FROM pg_policy WHERE polrelid IN ('mask.yeu_cau'::regclass,"
                    "'mask.cho_duyet'::regclass,'mask.dinh_danh'::regclass) ORDER BY oid").fetchall()]

        before = chup()
        self.conn.execute(doc_sql())
        self.assertEqual(chup(), before)

    def test_chay_lai_thu_hoi_acl_la_ke_ca_cua_cu(self):
        for signature in (CU, MOI, NGU_CANH, TAI_LIEU):
            self.conn.execute(self.sql.SQL('GRANT EXECUTE ON FUNCTION '+signature+' TO {} WITH GRANT OPTION').format(
                self.sql.Identifier(self.module_login)))
        self.conn.execute(doc_sql())
        for signature in (CU, MOI, NGU_CANH, TAI_LIEU):
            self.assertFalse(self.conn.execute('SELECT has_function_privilege(%s,%s,\'EXECUTE\')',
                             (self.module_login, signature)).fetchone()[0])

    def test_guard_sai_dich_khong_doi_quyen(self):
        with self.assertRaises(self.pg.errors.RaiseException) as caught, self.conn.transaction():
            self.conn.execute("SELECT set_config('kho_tri_thuc.tien_to_vai','DEMO-sai',true)")
            self.conn.execute(doc_sql())
        self.assertEqual(caught.exception.diag.message_primary, 'MASK_PHIEN_SAI_DICH')


if __name__ == '__main__':
    unittest.main()
