"""OCR-CR-1: SQL nguyên byte; PG opt-in chỉ lead chạy trên kho_test_*.

Không đọc cấu hình/DSN từ tệp, không mở/dừng dịch vụ. Ca PG dùng LOGIN
Core/module thật, hai kết nối cạnh tranh; thiếu môi trường ghi CHUA_KIEM.
"""

from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import re
from threading import Barrier
import unicodedata
import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = ROOT / 'src/kho_tri_thuc/core/sql/126_ocr_chua_ro.sql'
HELPER = 'loi.ocr_viec(uuid,uuid)'
GIU = 'loi_tai_lieu.ocr_giu_luot(uuid,text,uuid,text,integer,uuid)'
CHOT = 'loi_tai_lieu.ocr_chot_luot(uuid,text,uuid,bigint,text,text)'
DOC = 'loi_tai_lieu.ocr_doc_trang_thai(uuid,text)'
SIGNATURES = (HELPER, GIU, CHOT, DOC)
BAM = 'a' * 64


def doc_sql():
    return SQL_PATH.read_bytes().decode('utf-8', errors='strict')


def than_ham(name):
    match = re.search(r'CREATE OR REPLACE FUNCTION ' + re.escape(name)
        + r'\(.*?AS (\$[a-z_]+\$)(.*?)\1;', doc_sql(), re.S)
    if match is None:
        raise AssertionError('Thiếu cửa SQL ' + name)
    return match[2]


def chuan_hoa_proconfig(config):
    # PG có thể chèn khoảng trắng quanh dấu phẩy; giữ nguyên tên schema.
    return [re.sub(r'\s*,\s*', ',', value) for value in config]


class OCRSQLThuanTests(unittest.TestCase):
    def test_ket_noi_thu_hai_ghep_options_khong_doi_fixture(self):
        for login in ('core', 'module'):
            for options in (None, '', '-c application_name=OCR_DEMO -c statement_timeout=120000'):
                with self.subTest(login=login, options=options):
                    info = {'dbname': 'kho_test_ocr126', 'user': 'demo_' + login}
                    if options is not None:
                        info['options'] = options
                    original = dict(info)
                    case = OCRPostgresTests(methodName='runTest')
                    self.addCleanup(case.doCleanups)
                    case.pg = MagicMock()
                    case.cac_thong_tin = {login: info}
                    conn = case._ket_noi(login)
                    self.assertIs(conn, case.pg.connect.return_value)
                    case.pg.connect.assert_called_once_with(**{
                        **original, 'autocommit': True, 'connect_timeout': 10,
                        'options': ((options or '')
                            + ' -c statement_timeout=15000 -c lock_timeout=5000').strip()})
                    self.assertEqual(case.cac_thong_tin, {login: original})
                    conn.close.assert_not_called()
                    case.doCleanups()
                    conn.close.assert_called_once_with()

    def test_proconfig_pg_chuan_hoa_khoang_trang_van_dung_hai_schema(self):
        expected = ['search_path=pg_catalog,pg_temp']
        for config in (expected, ['search_path=pg_catalog, pg_temp'],
                       ['search_path=pg_catalog ,\tpg_temp']):
            with self.subTest(config=config):
                self.assertEqual(chuan_hoa_proconfig(config), expected)
        for config in ([], ['search_path=pg_catalog'], ['search_path=pg_temp, pg_catalog'],
                       ['search_path=public, pg_temp'], ['search_path=pg_catalog, public'],
                       ['search_path=pg_catalog, pg_temp, public'],
                       ['search_path=pg_catalog, pg_temp_khac'],
                       ['search_path=pg_cata log, pg_temp'],
                       ['search_path=pg_catalog, pg_temp', 'row_security=off']):
            with self.subTest(config=config):
                self.assertNotEqual(chuan_hoa_proconfig(config), expected)

    def test_byte_goc_utf8_nfc_khong_bom_mat_dau(self):
        for path in (SQL_PATH, Path(__file__)):
            raw = path.read_bytes()
            text = raw.decode('utf-8', errors='strict')
            self.assertFalse(raw.startswith(b'\xef\xbb\xbf'))
            self.assertEqual(text.encode('utf-8'), raw)
            self.assertEqual(text, unicodedata.normalize('NFC', text))
            self.assertNotIn('\ufffd', text)
        self.assertIn('pháp nhân'.encode('utf-8'), SQL_PATH.read_bytes())

    def test_doc_nguyen_byte_khong_dich_newline(self):
        raw = SQL_PATH.read_bytes()
        with patch.object(Path, 'read_text', side_effect=AssertionError('Không dịch newline')):
            self.assertEqual(doc_sql().encode('utf-8'), raw)

    def test_dollar_tag_long_tren_byte_goc_lf_va_crlf(self):
        raw = SQL_PATH.read_bytes()
        lf = raw.replace(b'\r\n', b'\n')
        expected = [b'$migration$', b'$viec$', b'$viec$', b'$giu$', b'$giu$',
                    b'$chot$', b'$chot$', b'$doc$', b'$doc$', b'$migration$']
        for content in (raw, lf, lf.replace(b'\n', b'\r\n')):
            self.assertEqual(re.findall(rb'\$(?:[A-Za-z_][A-Za-z_0-9]*)?\$', content), expected)
            self.assertRegex(content, rb'\bDO\s+\$migration\$\s+DECLARE\b')
            self.assertRegex(content, rb'\bEND;\s*\$migration\$;\s*\Z')
            for tag in (b'viec', b'giu', b'chot', b'doc'):
                self.assertRegex(content, rb'(?s)AS \$' + tag + rb'\$\s+DECLARE\b.*?END;\s*\$' + tag + rb'\$;')

    def test_migration_126_duy_nhat_runner_doc_dung_byte(self):
        from kho_tri_thuc.core.doi_cau_truc import _doc_chuoi
        files = list(SQL_PATH.parent.glob('[0-9][0-9][0-9]_*.sql'))
        self.assertEqual(list(SQL_PATH.parent.glob('126_*.sql')), [SQL_PATH])
        self.assertEqual(_doc_chuoi(files)[126][0], doc_sql())

    def test_guard_chan_dich_that_va_ten_gan_dung(self):
        sql = doc_sql()
        pattern = re.search(r"current_database\(\) COLLATE \"C\" !~ '(\^\(.*?)'", sql)[1]
        for name in ('kho_test_ocr126', 'kho_core_demo_g2_ocr126'):
            self.assertIsNotNone(re.fullmatch(pattern, name))
        for name in ('postgres', 'template1', 'kho_that', 'kho_crm_demo', 'kho_test_',
                     'kho_core_demo_g2_', 'kho_test_A', 'kho_test_a\nthat', 'xkho_test_a'):
            self.assertIsNone(re.fullmatch(pattern, name), name)

    def test_guard_pg16_owner_vai_rls_truoc_ddl(self):
        guard = doc_sql().split("PERFORM set_config('search_path'", 1)[0]
        for part in ('octet_length(chu_tl)>63', "tt COLLATE \"C\" !~ '^[a-z][a-z0-9_]*_$'",
                     "tt<>'' AND current_database() COLLATE \"C\" !~ '^kho_test_'",
                     "current_setting('server_version_num')::integer<160000",
                     'rolname=current_user AND rolsuper', "vai_cu COLLATE \"C\"<>'none'",
                     'NOT r.rolcanlogin', 'NOT r.rolsuper', 'NOT r.rolcreaterole',
                     'NOT r.rolbypassrls', 'NOT r.rolcreatedb', 'NOT r.rolreplication',
                     'pg_auth_members', 'c.relrowsecurity AND c.relforcerowsecurity',
                     "('loi.hang_viec',chu,'viec_chu')",
                     "('loi_tai_lieu.bien_nhan_core',chu_tl,'tiep_nhan_phien')",
                     'pg_get_userbyid(p.proowner)<>ham.chu_so_huu'):
            self.assertIn(part, guard)
        self.assertNotRegex(guard, r'(?im)^\s*(?:CREATE|ALTER|GRANT|REVOKE)\b')

    def test_dung_bien_nhan_hang_viec_khong_bang_cot_hay_sdk_moi(self):
        sql = doc_sql()
        self.assertIn('INSERT INTO loi_tai_lieu.bien_nhan_core', sql)
        self.assertNotRegex(sql, r'(?i)CREATE\s+TABLE|ADD\s+COLUMN|\bDROP\b|\bDELETE\b|\bTRUNCATE\b')
        self.assertNotRegex(sql, r'(?i)\b(?:COMMIT|ROLLBACK|dblink)\s*;|api\.openai|api\.anthropic')
        self.assertNotIn('sdk_core', sql)

    def test_helper_kiem_viec_dung_phap_nhan_khong_cap_bang(self):
        body = than_ham('loi.ocr_viec')
        self.assertIn('FROM loi.hang_viec v WHERE v.id=p_viec AND v.phap_nhan_id=p_pn', body)
        self.assertIn("jsonb_build_object('module',v.module,'tao_boi',v.tao_boi)", body)
        self.assertIn("'OCR_LUOT_SAI_VIEC' USING ERRCODE='22023'", body)
        self.assertNotRegex(doc_sql(), r'(?i)GRANT\s+(?:SELECT|INSERT|UPDATE|ALL)\b')

    def test_moi_cua_definer_chi_core_truoc_truy_cap_du_lieu(self):
        sql = doc_sql()
        names = re.findall(r'CREATE OR REPLACE FUNCTION ([a-z_.]+)\(', sql)
        self.assertEqual(names, [s.split('(')[0] for s in SIGNATURES])
        self.assertEqual(sql.count('SECURITY DEFINER SET search_path=pg_catalog,pg_temp'), 4)
        for name in names:
            body = than_ham(name)
            check = body.index('IF session_user::text COLLATE "C" IS DISTINCT FROM')
            self.assertLess(check, body.index("'OCR_LUOT_CHI_CORE' USING ERRCODE='42501'"))
            self.assertLess(check, min((body.find(token) for token in
                ('FROM loi.', 'FROM loi_tai_lieu.', 'UPDATE loi_tai_lieu.', 'PERFORM pg_advisory')
                if token in body), default=len(body)))

    def test_khoa_nguyen_tu_cung_cap_khong_kem_module_nguoi(self):
        for name in ('ocr_giu_luot', 'ocr_chot_luot'):
            body = than_ham('loi_tai_lieu.' + name)
            self.assertIn("jsonb_build_array('ocr.abbyy',p_pn,p_bam)::text,126", body)
            self.assertIn('IF NOT pg_try_advisory_xact_lock(hashtextextended(', body)
            self.assertIn("'OCR_LUOT_CAN_READ_COMMITTED' USING ERRCODE='25000'", body)
            self.assertLess(body.index('pg_advisory_xact_lock_shared(742601,1)'),
                            body.index('pg_try_advisory_xact_lock('))
        body = than_ham('loi_tai_lieu.ocr_giu_luot')
        check = body[body.index('IF EXISTS (SELECT'):body.index('viec := loi.ocr_viec')]
        for part in ('b.phap_nhan_id=p_pn', 'b.ma_bam COLLATE "C"=p_bam',
                     "b.operation COLLATE \"C\"='ocr.abbyy'", "('DANG_XU_LY','CHUA_RO')"):
            self.assertIn(part, check)
        self.assertNotRegex(check, r'\b(?:module|tao_boi)\b')
        self.assertLess(body.index('pg_try_advisory_xact_lock('), body.index('IF EXISTS (SELECT'))
        self.assertLess(body.index('IF EXISTS (SELECT'), body.index('INSERT INTO'))

    def test_dau_luot_chi_metadata_co_dinh_khong_payload_tu_do(self):
        body = than_ham('loi_tai_lieu.ocr_giu_luot')
        build = body.split('kq := jsonb_build_object(', 1)[1].split(');', 1)[0]
        self.assertEqual(re.findall(r"'([a-z_]+)'\s*,", build),
            ['giu_trang_id', 'viec_id', 'ma_tuong_quan', 'so_trang', 'trang_thai', 'phien_ban'])
        self.assertIn("'trang_thai','GIU','phien_ban',1", build)
        self.assertIn("p_bam,kq,'{}'::jsonb,'DANG_XU_LY'", body)
        self.assertNotRegex(body, r'(?i)\b(?:p_noi_dung|p_ten_tep|p_duong_dan|p_ket_qua|p_module|p_tao_boi)\b')

    def test_cas_so_phien_va_trang_thai_chan_chot_hai_lan(self):
        body = than_ham('loi_tai_lieu.ocr_chot_luot')
        for part in ('b.id=p_giu_trang AND b.phap_nhan_id=p_pn', 'b.ma_bam COLLATE "C"=p_bam',
                     'b.ket_qua->\'phien_ban\'=to_jsonb(p_phien_ban)',
                     '(b.ket_qua->>\'trang_thai\') COLLATE "C"=p_trang_thai_cu',
                     "'phien_ban',p_phien_ban+1", "'GIU','CHUA_RO'", "'DA_TIEU_TRANG','HOAN_TRANG'",
                     'IF NOT FOUND THEN', "'OCR_LUOT_XUNG_DOT' USING ERRCODE='40001'",
                     "THEN 'CHUA_RO' ELSE 'HOAN_TAT' END", 'THEN clock_timestamp() END'):
            self.assertIn(part, body)
        self.assertIn('b.trang_thai COLLATE "C"=(CASE WHEN', body)
        self.assertNotIn('INSERT INTO', body)

    def test_chua_ro_khong_ttl_khong_phu_thuoc_viec_da_xong(self):
        for name in ('ocr_giu_luot', 'ocr_chot_luot', 'ocr_doc_trang_thai'):
            body = than_ham('loi_tai_lieu.' + name)
            self.assertNotRegex(body, r'(?i)\binterval\b|bien_nhan_core_con_hieu_luc')
            if name != 'ocr_giu_luot':
                self.assertNotIn('loi.ocr_viec', body)
        body = than_ham('loi_tai_lieu.ocr_doc_trang_thai')
        self.assertIn("ORDER BY (b.trang_thai COLLATE \"C\" IN ('DANG_XU_LY','CHUA_RO')) DESC", body)
        self.assertIn('b.tao_luc DESC,b.id DESC LIMIT 1', body)
        self.assertNotRegex(body, r'b\.(?:module|tao_boi)\s*=')

    def test_policy_noi_bo_gioi_han_operation_login_phap_nhan(self):
        sql = doc_sql()
        policy = sql.split("EXECUTE format('ALTER POLICY ocr_luot_core", 1)[1].split("',login);", 1)[0]
        self.assertEqual(policy.count('operation COLLATE "C"=\'\'ocr.abbyy\'\''), 2)
        self.assertEqual(policy.count('session_user::text COLLATE "C"=%1$L'), 2)
        self.assertEqual(policy.count('phap_nhan_id::text COLLATE "C"=current_setting'), 2)
        self.assertIn('p.polroles=ARRAY[r.oid] AND r.rolname=chu_tl', sql)
        for name in ('ocr_giu_luot', 'ocr_chot_luot', 'ocr_doc_trang_thai'):
            body = than_ham('loi_tai_lieu.' + name)
            self.assertIn("set_config('ktt.ocr_phap_nhan_id',p_pn::text,true)", body)
            self.assertIn("set_config('ktt.ocr_phap_nhan_id',coalesce(pn_cu,''),true)", body)

    def test_chay_lai_giu_oid_owner_va_acl_hep(self):
        sql = doc_sql()
        for signature in SIGNATURES:
            self.assertEqual(sql.count("'" + signature + "'"), 2)
            self.assertIn('ALTER FUNCTION ' + signature + ' OWNER TO %I', sql)
        self.assertIn("('loi.ocr_viec(uuid,uuid)',chu_tl)", sql)
        self.assertIn('REVOKE ALL ON FUNCTION %s FROM PUBLIC', sql)
        self.assertIn('a.grantee<>0 AND a.grantee<>p.proowner', sql)
        self.assertIn("GRANT EXECUTE ON FUNCTION %s TO %I',ham.chu_ky,ham.duoc_goi", sql)
        self.assertIn("set_config('search_path',path_cu,true)", sql)
        self.assertIn("set_config('role',vai_cu,true)", sql)
        self.assertNotRegex(sql, r'(?i)GRANT[^;]*\b(?:PUBLIC|vai_chay_mod_|dang_nhap_mod_)\b')

    def test_khong_trung_bien_declare_voi_alias_bang(self):
        for signature in SIGNATURES:
            body = than_ham(signature.split('(')[0])
            declare = body.split('BEGIN', 1)[0]
            variables = set(re.findall(r'(?:DECLARE|;)\s*([a-z_]+)\s+', declare))
            aliases = set(re.findall(r'\b(?:FROM|JOIN|UPDATE)\s+[a-z_]+\.[a-z_]+\s+([a-z_]+)', body))
            self.assertFalse(variables & aliases, signature)


@unittest.skipUnless(os.environ.get('KHO_PG_DSN_TEST'),
                     'CHUA_KIEM PG: chỉ lead chạy với KHO_PG_DSN_TEST')
class OCRPostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tests import test_g2_32_f1 as f1
        cls.f1 = f1
        cls._ghi = f1.TepTiepNhanPGTest._ghi
        f1.TepTiepNhanPGTest.setUpClass.__func__(cls)
        cls.assert_test_db = re.fullmatch(r'kho_test_[a-z0-9_]+', cls.db)
        if not cls.assert_test_db:
            raise AssertionError('CHUA_KIEM: fixture phải ở CSDL test')

    def setUp(self):
        self.g209.TaiLieuPostgresTest.setUp(self)
        self.viec = self._viec()

    def _viec(self, pn=None, module='crm', actor=None):
        # Chỉ provisioning dữ liệu DEMO, không giả runtime hoặc nới quyền bảng.
        return self.conn.execute('''INSERT INTO loi.hang_viec(phap_nhan_id,module,loai,phien_ban,
            khoa_chong_trung,bang_tham_chieu,tham_chieu_id,phien_ban_contract,hanh_dong,
            pham_vi_hanh_dong,co_tac_dong_ngoai,thu_lai_an_toan,toi_da_lan_thu,thu_lai_giay,tao_boi)
            VALUES (%s,%s,'OCR_DEMO',1,%s,'doi_tuong',%s,'1','CRM:TIEP_NHAN:LAP',
                ARRAY['CRM:TIEP_NHAN:LAP'],true,false,1,60,%s) RETURNING id''',
            (pn or self.pn, module, uuid4().hex, self.obj, actor or self.nd)).fetchone()[0]

    def _giu(self, *, conn=None, pn=None, viec=None, bam=BAM, giu=None, pages=3, correlation=None):
        return (conn or self.core).execute('SELECT loi_tai_lieu.ocr_giu_luot(%s,%s,%s,%s,%s,%s)',
            (pn or self.pn, bam, viec or self.viec, correlation or uuid4().hex, pages, giu or uuid4())).fetchone()[0]

    def _doc(self, *, conn=None, pn=None, bam=BAM):
        return (conn or self.core).execute('SELECT loi_tai_lieu.ocr_doc_trang_thai(%s,%s)',
            (pn or self.pn, bam)).fetchone()[0]

    def _chot(self, row, state, *, conn=None, version=None, old=None, pn=None, bam=BAM):
        return (conn or self.core).execute('SELECT loi_tai_lieu.ocr_chot_luot(%s,%s,%s,%s,%s,%s)',
            (pn or self.pn, bam, row['giu_trang_id'], row['phien_ban'] if version is None else version,
             old or row['trang_thai'], state)).fetchone()[0]

    def _loi(self, code, fn, *args, **kwargs):
        with self.assertRaises(self.pg.Error) as caught, self.core.transaction():
            fn(*args, **kwargs)
        self.assertEqual(caught.exception.sqlstate, code)
        return caught.exception

    def _ket_noi(self, login='core'):
        info = dict(self.cac_thong_tin[login])
        info['options'] = (info.get('options', '')
            + ' -c statement_timeout=15000 -c lock_timeout=5000').strip()
        conn = self.pg.connect(**info, autocommit=True, connect_timeout=10)
        self.addCleanup(conn.close)
        return conn

    def test_giu_doc_ben_qua_ket_noi_moi_khong_lo_payload(self):
        self.assertIsNone(self._doc())
        row = self._giu()
        self.assertEqual(self._doc(conn=self._ket_noi()), row)
        self.assertEqual(set(row), {'giu_trang_id', 'viec_id', 'ma_tuong_quan', 'so_trang', 'trang_thai', 'phien_ban'})
        self.assertEqual((row['trang_thai'], row['phien_ban'], row['so_trang']), ('GIU', 1, 3))
        self.assertEqual(row['viec_id'], str(self.viec))

    def test_hai_yeu_cau_cung_bam_mot_giu_mot_tu_choi_hai_ket_noi(self):
        barrier = Barrier(2)
        jobs = (self.viec, self._viec())
        connections = (self._ket_noi(), self._ket_noi())

        def run(index):
            barrier.wait(timeout=10)
            try:
                with connections[index].transaction():
                    return 'GIU', self._giu(conn=connections[index], viec=jobs[index])
            except self.pg.Error as exc:
                return exc.sqlstate, exc.diag.message_primary

        with ThreadPoolExecutor(max_workers=2) as pool:
            result = list(pool.map(run, range(2)))
        self.assertCountEqual([r[0] for r in result], ['GIU', 'P0001'])
        self.assertEqual([r[1] for r in result if r[0] == 'P0001'], ['OCR_LUOT_DANG_BI_CHAN'])
        count = self.conn.execute("SELECT count(*) FROM loi_tai_lieu.bien_nhan_core "
            "WHERE phap_nhan_id=%s AND ma_bam=%s AND operation='ocr.abbyy'", (self.pn, BAM)).fetchone()[0]
        self.assertEqual(count, 1)

    def test_luot_chua_commit_van_chan_ket_noi_thu_hai(self):
        second = self._ket_noi()
        other_job = self._viec()
        with self.core.transaction():
            row = self._giu()
            # Kết nối khác chưa thấy dòng nhưng phải bị khóa cặp chặn ngay.
            with self.assertRaises(self.pg.Error) as caught:
                self._giu(conn=second, viec=other_job)
            self.assertEqual((caught.exception.sqlstate, caught.exception.diag.message_primary),
                             ('P0001', 'OCR_LUOT_DANG_BI_CHAN'))
        self.assertEqual(self._doc(conn=second), row)

    def test_khac_phap_nhan_doc_lap_ke_ca_dang_giu_khoa(self):
        second = self._ket_noi()
        other_job = self._viec(pn=self.pn_khac)
        with self.core.transaction():
            one = self._giu()
            two = self._giu(conn=second, pn=self.pn_khac, viec=other_job)
        self.assertNotEqual(one['giu_trang_id'], two['giu_trang_id'])
        self.assertEqual(self._doc(pn=self.pn_khac), two)

    def test_module_khac_cung_phap_nhan_van_bi_chan(self):
        other = self._viec(module='core')
        self._giu()
        self.assertEqual(self._loi('P0001', self._giu, viec=other).diag.message_primary, 'OCR_LUOT_DANG_BI_CHAN')

    def test_nguoi_tao_khac_cung_phap_nhan_van_bi_chan(self):
        actor = uuid4()
        self.conn.execute("INSERT INTO loi.nguoi_dung(id,dang_nhap,ten,vai_tro) VALUES (%s,%s,'DEMO','XEM')",
            (actor, 'demo_' + actor.hex))
        other = self._viec(actor=actor)
        self._giu()
        self._loi('P0001', self._giu, viec=other)

    def test_chua_ro_khong_het_han_khi_viec_xong_fallback(self):
        row = self._chot(self._giu(), 'CHUA_RO')
        self.conn.execute("UPDATE loi.hang_viec SET trang_thai='XONG',ket_thuc_luc=clock_timestamp() WHERE id=%s", (self.viec,))
        self.conn.execute("UPDATE loi_tai_lieu.bien_nhan_core SET tao_luc=clock_timestamp()-interval '90 days' WHERE id=%s",
            (row['giu_trang_id'],))
        self.assertEqual(self._doc(conn=self._ket_noi()), row)
        self._loi('P0001', self._giu, viec=self._viec())
        self.assertEqual(self._chot(row, 'DA_TIEU_TRANG')['trang_thai'], 'DA_TIEU_TRANG')

    def test_chot_sai_phien_ban_trang_thai_phap_nhan_bam_bi_tu_choi(self):
        row = self._giu()
        for changed in ({'version': 2}, {'old': 'CHUA_RO'}, {'pn': self.pn_khac}, {'bam': 'b' * 64}):
            with self.subTest(changed=changed):
                self._loi('40001', self._chot, row, 'HOAN_TRANG', **changed)
        self.assertEqual(self._doc(), row)

    def test_chot_cuoi_tu_giu_va_chua_ro_khong_hoan_tieu_lan_hai(self):
        for old in ('GIU', 'CHUA_RO'):
            for state in ('DA_TIEU_TRANG', 'HOAN_TRANG'):
                with self.subTest(old=old, state=state):
                    held = self._giu()
                    row = self._chot(held, 'CHUA_RO') if old == 'CHUA_RO' else held
                    final = self._chot(row, state)
                    self.assertEqual(final['phien_ban'], row['phien_ban'] + 1)
                    self.assertEqual(self._doc(), final)
                    self._loi('40001', self._chot, row, state)
                    self._loi('22023', self._chot, final, 'HOAN_TRANG')
                    self.assertEqual(self.conn.execute('SELECT trang_thai,ket_qua_cuoi_luc IS NOT NULL '
                        'FROM loi_tai_lieu.bien_nhan_core WHERE id=%s', (row['giu_trang_id'],)).fetchone(), ('HOAN_TAT', True))

    def test_cas_hai_yeu_cau_chot_chi_mot_thang(self):
        row = self._giu()
        barrier = Barrier(2)
        connections = (self._ket_noi(), self._ket_noi())

        def run(index):
            barrier.wait(timeout=10)
            try:
                return self._chot(row, ('DA_TIEU_TRANG', 'HOAN_TRANG')[index], conn=connections[index])['trang_thai']
            except self.pg.Error as exc:
                return exc.sqlstate

        with ThreadPoolExecutor(max_workers=2) as pool:
            result = list(pool.map(run, range(2)))
        self.assertEqual(sum(v in ('DA_TIEU_TRANG', 'HOAN_TRANG') for v in result), 1)
        self.assertTrue(any(v in ('40001', 'P0001') for v in result))

    def test_rollback_khong_giu_trang_phantom_va_uuid_khong_tai_dung(self):
        class Rollback(Exception):
            pass
        ident = uuid4()
        with self.assertRaises(Rollback), self.core.transaction():
            self._giu(giu=ident)
            raise Rollback
        self.assertIsNone(self._doc())
        row = self._giu(giu=ident)
        self._chot(row, 'HOAN_TRANG')
        self._loi('23505', self._giu, giu=ident)
        self.assertEqual(self._giu()['trang_thai'], 'GIU')

    def test_viec_khac_phap_nhan_va_dau_vao_sai_khong_ghi(self):
        self._loi('22023', self._giu, pn=self.pn_khac)
        for changed in ({'bam': 'A' * 64}, {'bam': 'á' * 64}, {'pages': 0},
                        {'correlation': 'ten/tep.pdf'}, {'viec': uuid4()}):
            with self.subTest(changed=changed):
                self._loi('22023', self._giu, **changed)
        self.assertIsNone(self._doc())

    def test_isolation_cu_bi_chan_va_phuc_hoi_ngu_canh(self):
        with self.core.transaction():
            self.core.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ')
            with self.assertRaises(self.pg.Error) as caught, self.core.transaction():
                self._giu()
            self.assertEqual(caught.exception.sqlstate, '25000')
        with self.core.transaction():
            self.core.execute("SELECT set_config('ktt.ocr_phap_nhan_id','DEMO_CU',true)")
            self._giu()
            self._doc()
            self.assertEqual(self.core.execute("SELECT current_setting('ktt.ocr_phap_nhan_id')").fetchone()[0], 'DEMO_CU')

    def test_module_khong_core_goi_bi_42501_ke_ca_lo_cap_execute(self):
        sql = self.g209.sql
        for grant in (False, True):
            with self.subTest(grant=grant):
                if grant:
                    for signature in SIGNATURES:
                        self.conn.execute(sql.SQL('GRANT EXECUTE ON FUNCTION {} TO {}').format(
                            sql.SQL(signature), sql.Identifier(self.module_login)))
                try:
                    for query, args in (
                        ('SELECT loi_tai_lieu.ocr_giu_luot(%s,%s,%s,%s,3,%s)',
                         (self.pn, BAM, self.viec, uuid4().hex, uuid4())),
                        ('SELECT loi_tai_lieu.ocr_chot_luot(%s,%s,%s,1,\'GIU\',\'HOAN_TRANG\')',
                         (self.pn, BAM, uuid4())),
                        ('SELECT loi_tai_lieu.ocr_doc_trang_thai(%s,%s)', (self.pn, BAM)),
                        ('SELECT loi.ocr_viec(%s,%s)', (self.pn, self.viec))):
                        with self.assertRaises(self.pg.Error) as caught:
                            self.module.execute(query, args)
                        self.assertEqual(caught.exception.sqlstate, '42501')
                finally:
                    if grant:
                        self.conn.execute(doc_sql())

    def test_runtime_khong_doc_ghi_bang_hay_goi_helper_truc_tiep(self):
        for conn in (self.core, self.module):
            for query in ('SELECT * FROM loi_tai_lieu.bien_nhan_core LIMIT 1',
                          'INSERT INTO loi_tai_lieu.bien_nhan_core DEFAULT VALUES',
                          'SELECT loi.ocr_viec(NULL::uuid,NULL::uuid)'):
                with self.subTest(login=conn.info.user, query=query), self.assertRaises(self.pg.Error) as caught:
                    conn.execute(query)
                self.assertEqual(caught.exception.sqlstate, '42501')

    def test_guard_tu_choi_runtime_va_owner_ham_sai_truoc_ddl(self):
        with self.assertRaises(self.pg.Error) as caught:
            self.core.execute(doc_sql())
        self.assertEqual(caught.exception.diag.message_primary, 'OCR_LUOT_SAI_DICH')
        sql = self.g209.sql
        with self.assertRaises(self.pg.Error) as caught, self.conn.transaction():
            self.conn.execute(sql.SQL('ALTER FUNCTION {} OWNER TO {}').format(
                sql.SQL(GIU), sql.Identifier(self.tien_to + 'vai_doi_cau_truc_loi')))
            self.conn.execute(doc_sql())
        self.assertEqual(caught.exception.diag.message_primary, 'OCR_LUOT_SAI_OWNER_HAM')

    def test_chay_lai_nguyen_byte_giu_oid_owner_acl_va_du_lieu(self):
        row = self._chot(self._giu(), 'CHUA_RO')
        query = 'SELECT oid,proowner,proacl,proconfig,prosecdef FROM pg_proc WHERE oid=ANY(%s::regprocedure[]) ORDER BY oid'
        before = self.conn.execute(query, (list(SIGNATURES),)).fetchall()
        policy = self.conn.execute("SELECT oid FROM pg_policy WHERE polrelid='loi_tai_lieu.bien_nhan_core'::regclass "
            "AND polname='ocr_luot_core'").fetchone()
        for _ in range(2):
            self.conn.execute(doc_sql())
            self.assertEqual(self.conn.execute(query, (list(SIGNATURES),)).fetchall(), before)
            self.assertEqual(self._doc(), row)
        self.assertEqual(self.conn.execute("SELECT oid FROM pg_policy WHERE polrelid='loi_tai_lieu.bien_nhan_core'::regclass "
            "AND polname='ocr_luot_core'").fetchone(), policy)
        for signature, owner, grantee in ((HELPER, 'loi', self.tien_to + 'vai_doi_cau_truc_loi_tai_lieu'),
            *((signature, 'loi_tai_lieu', self.cac_thong_tin['core']['user']) for signature in (GIU, CHOT, DOC))):
            metadata = self.conn.execute('SELECT pg_get_userbyid(proowner),prosecdef,proconfig '
                'FROM pg_proc WHERE oid=%s::regprocedure', (signature,)).fetchone()
            self.assertEqual((metadata[0], metadata[1], chuan_hoa_proconfig(metadata[2])),
                (self.tien_to + 'vai_doi_cau_truc_' + owner, True, ['search_path=pg_catalog,pg_temp']))
            grants = self.conn.execute('SELECT pg_get_userbyid(a.grantee),a.privilege_type,a.is_grantable '
                'FROM pg_proc p,LATERAL aclexplode(p.proacl) a WHERE p.oid=%s::regprocedure AND a.grantee<>p.proowner',
                (signature,)).fetchall()
            self.assertEqual(grants, [(grantee, 'EXECUTE', False)])


if __name__ == '__main__':
    unittest.main()
