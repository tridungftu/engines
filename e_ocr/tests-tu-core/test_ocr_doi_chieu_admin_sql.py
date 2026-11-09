"""OCR-CR-8: kiểm biên SQL Admin; PG opt-in chỉ lead chạy trên kho_test_*.

Không đọc cấu hình kết nối từ tệp, không khởi động dịch vụ. Fixture PG
chỉ provisioning dữ liệu DEMO; ca nghiệp vụ dùng LOGIN Core thật.
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
from threading import Event
import unicodedata
import unittest
from uuid import UUID, uuid4


ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = ROOT / 'src/kho_tri_thuc/core/sql/130_ocr_doi_chieu_admin.sql'
REQUEST_SQL_PATH = SQL_PATH.with_name('131_ocr_chot_admin_request_id.sql')
HELPER = 'loi.ocr_chua_ro_admin_kiem(uuid,uuid)'
LEASE = 'loi.ocr_chua_ro_admin_lease(uuid,uuid)'
DANH_SACH = 'loi_tai_lieu.ocr_chua_ro_ds(uuid,integer)'
CHOT = 'loi_tai_lieu.ocr_chua_ro_chot_admin(uuid,text,bigint,text,text)'
CHOT_REQUEST = 'loi_tai_lieu.ocr_chua_ro_chot_admin(uuid,text,bigint,text,text,uuid)'
AUDIT = 'loi.ghi_kiem_toan_v2(text,text,uuid,text,text,uuid,text,uuid,text,uuid,bigint)'
ENGINE = 'loi_tai_lieu.ocr_chot_luot(uuid,text,uuid,bigint,text,text)'
SIGNATURES = (HELPER, LEASE, DANH_SACH, CHOT, AUDIT, ENGINE)
BAM = 'a' * 64
HANH_DONG = 'CORE:ENGINE:XEM'
QUYEN_CHOT = 'CORE:ENGINE:CAU_HINH'


def doc_sql():
    return SQL_PATH.read_bytes().decode('utf-8', errors='strict')


def than_ham(ten, sql=None):
    match = re.search(r'CREATE OR REPLACE FUNCTION\s+' + re.escape(ten)
        + r'\s*\(.*?\bAS\s+(\$[A-Za-z_0-9]*\$)(.*?)\1\s*;', doc_sql() if sql is None else sql, re.S)
    if match is None:
        raise AssertionError('Thiếu cửa SQL ' + ten)
    return match[2]


class OCRAdminSQLThuanTests(unittest.TestCase):
    def test_utf8_dung_dau_khong_bom_va_runner_doc_dung_migration(self):
        from kho_tri_thuc.core.doi_cau_truc import _doc_chuoi
        raw = SQL_PATH.read_bytes()
        for path in (SQL_PATH, REQUEST_SQL_PATH, Path(__file__),
                     Path(__file__).with_name('test_ocr_doi_chieu_admin.py'),
                     SQL_PATH.parent.parent / 'routes_ocr_doi_chieu.py'):
            source = path.read_bytes()
            content = source.decode('utf-8', errors='strict')
            self.assertFalse(source.startswith(b'\xef\xbb\xbf'), path.name)
            self.assertNotIn('\ufffd', content, path.name)
            self.assertEqual(content, unicodedata.normalize('NFC', content), path.name)
        self.assertEqual(list(SQL_PATH.parent.glob('130_*.sql')), [SQL_PATH])
        files = list(SQL_PATH.parent.glob('[0-9][0-9][0-9]_*.sql'))
        self.assertEqual(_doc_chuoi(files)[130][0].encode('utf-8'), raw)
        self.assertEqual(list(SQL_PATH.parent.glob('131_*.sql')), [REQUEST_SQL_PATH])
        self.assertEqual(_doc_chuoi(files)[131][0].encode('utf-8'), REQUEST_SQL_PATH.read_bytes())

    def test_migration_chi_tien_khong_them_bang_cot_cap_quyen_bang(self):
        sql = doc_sql()
        self.assertNotRegex(sql, r'(?i)\b(?:CREATE\s+TABLE|ADD\s+COLUMN|DROP|DELETE|TRUNCATE)\b')
        self.assertNotRegex(sql, r'(?i)\bGRANT\s+(?:ALL|SELECT|INSERT|UPDATE)\b')
        self.assertNotRegex(sql, r'(?i)\b(?:COMMIT|ROLLBACK)\s*;|dblink|api\.openai|api\.anthropic')
        self.assertIn('loi_tai_lieu.bien_nhan_core', sql)
        self.assertIn('doi_chieu_admin', sql)

    def test_moi_cua_definer_path_co_dinh_acl_toi_thieu(self):
        sql = doc_sql()
        names = re.findall(r'CREATE OR REPLACE FUNCTION\s+([a-z0-9_.]+)\s*\(', sql)
        self.assertEqual(set(names), {signature.split('(')[0] for signature in SIGNATURES})
        for name in names:
            declaration = sql[sql.index('CREATE OR REPLACE FUNCTION ' + name):]
            declaration = declaration[:declaration.index(' AS ') + 4] if ' AS ' in declaration else declaration
            self.assertRegex(declaration, r'SECURITY DEFINER\s+SET search_path\s*=\s*pg_catalog\s*,\s*pg_temp')
        self.assertIn('REVOKE ALL ON FUNCTION %s FROM PUBLIC', sql)
        self.assertIn('a.grantee<>0 AND a.grantee<>p.proowner', sql)
        self.assertNotRegex(sql, r'(?i)\bGRANT[^;]*\bTO\s+PUBLIC\b')

    def test_admin_dua_tren_phien_da_xac_minh_khong_uuid_tu_khai(self):
        body = than_ham('loi.ocr_chua_ro_admin_kiem')
        for part in ('session_user', 'loi.xac_minh_phien', 'loi.mtq_admin', 'thu_hoi_luc',
                     'ktt.ma_phien', 'ktt.module', 'ktt.phap_nhan_id', 'ktt.hanh_dong',
                     'CORE:ENGINE:XEM', 'NGUOI_DUNG'):
            self.assertIn(part, body)
        self.assertRegex(body, r"ERRCODE\s*=\s*'42501'")
        self.assertIn('FOR SHARE', body)
        self.assertIn('giu_den', body)

    def test_chot_khoa_cung_bam_126_va_cas_truoc_hoan_tat(self):
        body = than_ham('loi_tai_lieu.ocr_chua_ro_chot_admin')
        self.assertRegex(body, r"jsonb_build_array\('ocr\.abbyy',\s*p_pn,\s*[^)]+\)::text,\s*126")
        self.assertIn('pg_try_advisory_xact_lock', body)
        self.assertIn("'40001'", body)
        self.assertIn('p_phien_ban', body)
        self.assertIn("'HOAN_TAT'", body)
        self.assertIn('ket_qua_cuoi_luc', body)
        self.assertIn('loi.ocr_chua_ro_admin_kiem', body)
        self.assertNotIn('INSERT INTO loi_tai_lieu.bien_nhan_core', body)

    def test_danh_sach_chi_dau_bam_toi_da_tam_ky_tu(self):
        body = than_ham('loi_tai_lieu.ocr_chua_ro_ds')
        self.assertIn("'ma_bam_dau'", body)
        self.assertRegex(body, r'(?i)\bleft\(\s*[a-z_]+\.ma_bam\s*,\s*8\s*\)')
        self.assertNotRegex(body, r"'ma_bam'\s*,")
        self.assertIn('loi.ocr_chua_ro_admin_kiem', body)
        self.assertIn('p_gioi_han', body)

    def test_dollar_quote_long_khong_trung_va_alias_khong_trung_bien(self):
        for raw in (doc_sql().replace('\r\n', '\n'), doc_sql().replace('\r\n', '\n').replace('\n', '\r\n')):
            tags = re.findall(r'\$(?:[A-Za-z_][A-Za-z_0-9]*)?\$', raw)
            self.assertEqual((tags[0], tags[-1]), ('$migration$', '$migration$'))
            self.assertEqual(len(tags), 2 + 2 * len(SIGNATURES))
            self.assertTrue(all(a == b and a != tags[0] for a, b in zip(tags[1:-1:2], tags[2:-1:2])))
        for signature in SIGNATURES:
            body = than_ham(signature.split('(')[0])
            declare = body.split('BEGIN', 1)[0]
            variables = set(re.findall(r'(?:DECLARE|;)\s*([a-z_]+)\s+', declare))
            aliases = set(re.findall(r'\b(?:FROM|JOIN|UPDATE)\s+[a-z_]+\.[a-z_]+\s+([a-z_]+)', body))
            self.assertFalse(variables & aliases, signature)

    def test_danh_sach_chi_xac_minh_mot_lan_va_lease_khong_khoa(self):
        listing = than_ham('loi_tai_lieu.ocr_chua_ro_ds')
        lease = than_ham('loi.ocr_chua_ro_admin_lease')
        self.assertEqual(listing.count('loi.ocr_chua_ro_admin_kiem('), 1)
        self.assertIn('loi.ocr_chua_ro_admin_lease(p_pn,CASE', listing)
        self.assertNotRegex(lease, r'(?i)\bFOR\s+(?:UPDATE|SHARE|KEY|NO)\b|pg_.*lock')
        self.assertIn('han_lease IS NOT NULL', lease)
        self.assertIn('IF NOT FOUND THEN RETURN false', lease)
        self.assertIn('p_viec IS NOT NULL AND hd IS DISTINCT FROM', than_ham(HELPER.split('(')[0]))

    def test_sql_loc_ma_module_dung_mau_route_truoc_phan_trang(self):
        from kho_tri_thuc.core.routes_ocr_doi_chieu import _DONG
        body = than_ham('loi_tai_lieu.ocr_chua_ro_ds')
        for field in ('ma_tuong_quan', 'module'):
            self.assertIn("~ '" + _DONG['properties'][field]['pattern'] + "'", body)
        self.assertLess(body.index("~ '^ocr:"), body.index('LIMIT p_gioi_han'))

    def test_audit_v2_giu_nguyen_nhanh_module_va_engine_chi_doi_ma_tranh_khoa(self):
        audit = than_ham('loi.ghi_kiem_toan_v2')
        old = than_ham('loi.ghi_kiem_toan_v2',
            (SQL_PATH.parent / '020_sdk_v2.sql').read_bytes().decode('utf-8'))
        marker = 'IF p_module IS NULL OR session_user'
        self.assertEqual(audit[audit.index(marker):].strip().splitlines(),
                         old[old.index(marker):].strip().splitlines())
        for part in ('p_ma IS DISTINCT FROM', 'p_request IS DISTINCT FROM p_doi_tuong_id',
                     "p_hd IS DISTINCT FROM 'CORE:ENGINE:CAU_HINH'", 'loi.ocr_chua_ro_admin_kiem'):
            self.assertIn(part, audit)
        old_engine = than_ham('loi_tai_lieu.ocr_chot_luot',
            (SQL_PATH.parent / '126_ocr_chua_ro.sql').read_bytes().decode('utf-8'))
        self.assertEqual(than_ham('loi_tai_lieu.ocr_chot_luot').strip().splitlines(), old_engine.replace(
            "'OCR_LUOT_DANG_BI_CHAN' USING ERRCODE='P0001'",
            "'OCR_LUOT_XUNG_DOT' USING ERRCODE='40001'").strip().splitlines())

    def test_chot_bat_buoc_quyen_ghi_bang_chung_va_mot_audit_sau_cas(self):
        body = than_ham('loi_tai_lieu.ocr_chua_ro_chot_admin')
        self.assertIn("IS DISTINCT FROM 'CORE:ENGINE:CAU_HINH'", body)
        self.assertIn("btrim(p_ghi_chu)=''", body)
        self.assertIn('length(p_ghi_chu)>500', body)
        self.assertIn("'trang_thai_truoc',tt_truoc", body)
        self.assertEqual(body.count('PERFORM loi.ghi_kiem_toan_v2('), 1)
        self.assertLess(body.index('RETURNING b.ket_qua INTO kq'), body.index('PERFORM loi.ghi_kiem_toan_v2('))
        sql = doc_sql()
        acl = sql[sql.rindex('FOR ham IN SELECT * FROM (VALUES'):]
        self.assertNotIn(AUDIT, acl)  # Không thu hồi ACL SDK module trong loop hội tụ.

    def test_131_chi_them_overload_khong_ghi_lai_ham_cu(self):
        sql = REQUEST_SQL_PATH.read_text(encoding='utf-8')
        declarations = re.findall(r'CREATE OR REPLACE FUNCTION\s+([a-z0-9_.]+)\s*\((.*?)\)\s*RETURNS',
                                  sql, re.S)
        self.assertEqual(len(declarations), 2)
        name, parameters = declarations[0]
        self.assertEqual(name, CHOT_REQUEST.split('(')[0])
        self.assertEqual(len(parameters.split(',')), 6)
        self.assertIn('p_request_id uuid', parameters)
        self.assertNotIn('DEFAULT', parameters)
        self.assertNotRegex(sql, r'(?i)\b(?:CREATE\s+TABLE|ADD\s+COLUMN|DROP|DELETE|TRUNCATE)\b')
        self.assertNotRegex(sql, r'(?i)\bGRANT\s+(?:ALL|SELECT|INSERT|UPDATE)\b')
        self.assertNotRegex(sql, r'(?i)\b(?:COMMIT|ROLLBACK)\s*;|dblink')

    def test_131_audit_chi_tach_request_id_khoi_uuid_bien_nhan(self):
        sql = REQUEST_SQL_PATH.read_text(encoding='utf-8')
        audit = than_ham(AUDIT.split('(')[0], sql)
        expected = than_ham(AUDIT.split('(')[0]).replace(
            'p_request IS DISTINCT FROM p_doi_tuong_id', 'p_request IS NULL')
        self.assertEqual(audit.strip().splitlines(), expected.strip().splitlines())
        body = than_ham(CHOT_REQUEST.split('(')[0], sql)
        self.assertIn('p_request_id IS NULL', body)
        self.assertIn('ai := loi.ocr_chua_ro_admin_kiem(p_pn,NULL)', body)
        self.assertIn('loi.ocr_chua_ro_admin_kiem(p_pn,viec_luot)', body)
        self.assertIn('FOR UPDATE OF b', body)
        self.assertIn("b.ket_qua->'phien_ban'=to_jsonb(p_phien_ban)", body)
        self.assertIn("'ocr_doi_chieu_admin',luot_id,'DAT',p_request_id,'1',NULL,NULL", body)
        self.assertEqual(body.count('PERFORM loi.ghi_kiem_toan_v2('), 1)
        self.assertLess(body.index('RETURNING b.ket_qua INTO kq'), body.index('PERFORM loi.ghi_kiem_toan_v2('))

    def test_131_definer_acl_va_guard_giu_nhu_130(self):
        sql = REQUEST_SQL_PATH.read_text(encoding='utf-8')
        self.assertEqual(sql.count('SECURITY DEFINER SET search_path=pg_catalog,pg_temp'), 2)
        for marker in ("current_setting('role')", 'rolsuper', 'rolbypassrls', 'relforcerowsecurity',
                       'pg_get_userbyid(p.proowner)', 'pg_advisory_xact_lock(742601,1)',
                       'OCR_ADMIN_SAI_OWNER_HAM', 'REVOKE ALL ON FUNCTION %s FROM PUBLIC'):
            self.assertIn(marker, sql)
        acl = sql[sql.rindex('FOR ham IN SELECT * FROM (VALUES'):]
        self.assertIn("('" + CHOT_REQUEST + "',login)", acl)
        self.assertNotIn(CHOT, acl)
        self.assertNotIn(AUDIT, acl)
        self.assertIn('a.grantee<>0 AND a.grantee<>p.proowner', acl)
        self.assertNotRegex(sql, r'(?i)\bGRANT[^;]*\bTO\s+PUBLIC\b')

    def test_131_cu_phap_case_ngoai_if_dollar_quote_alias_khong_trung(self):
        sql = REQUEST_SQL_PATH.read_text(encoding='utf-8')
        tags = re.findall(r'\$(?:[A-Za-z_][A-Za-z_0-9]*)?\$', sql)
        self.assertEqual(tags, ['$migration$', '$chot$', '$chot$', '$audit$', '$audit$', '$migration$'])
        for name in (CHOT_REQUEST.split('(')[0], AUDIT.split('(')[0]):
            body = than_ham(name, sql)
            self.assertNotRegex(body, r'(?ims)^\s*IF\b(?:(?!\bTHEN\b|;).)*\bCASE\b')
            declare = body.split('BEGIN', 1)[0]
            variables = set(re.findall(r'(?:DECLARE|;)\s*([a-z_]+)\s+', declare))
            aliases = set(re.findall(r'\b(?:FROM|JOIN|UPDATE)\s+[a-z_]+\.[a-z_]+\s+([a-z_]+)', body))
            self.assertFalse(variables & aliases, name)


@unittest.skipUnless(os.environ.get('KHO_PG_DSN_TEST'),
                     'CHUA_KIEM PG: chỉ lead chạy với KHO_PG_DSN_TEST')
class OCRAdminPostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Nhập module fixture, không nhập TestCase vào globals để unittest
        # không chạy lại toàn bộ ca PG của OCR-CR-1 trong lát Admin.
        from tests import test_g2_32_f1 as f1
        from tests import test_ocr_doi_chieu_sql as ocr_nen
        cls._ghi = f1.TepTiepNhanPGTest._ghi
        f1.TepTiepNhanPGTest.setUpClass.__func__(cls)
        if re.fullmatch(r'kho_test_[a-z0-9_]+', cls.db) is None:
            raise AssertionError('Fixture Admin chỉ được dùng CSDL test')
        for name in ('_viec', '_giu', '_doc', '_chot', '_ket_noi'):
            setattr(cls, name, getattr(ocr_nen.OCRPostgresTests, name))

    def setUp(self):
        self.g209.TaiLieuPostgresTest.setUp(self)
        self.viec = self._viec()
        self.ma_admin = self._cap(module='core', hd=[HANH_DONG, QUYEN_CHOT])

    def _ngu_canh(self, conn, *, ma=None, pn=None, module='core', action=HANH_DONG):
        conn.execute("SELECT set_config('ktt.ma_phien',%s,true),"
            "set_config('ktt.module',%s,true),set_config('ktt.phap_nhan_id',%s,true),"
            "set_config('ktt.hanh_dong',%s,true)",
            ((ma or self.ma_admin).lay_de_truyen(), module, str(pn or self.pn), action))

    def _ds(self, *, pn=None, ma=None, limit=100):
        with self.core.transaction():
            self._ngu_canh(self.core, ma=ma, pn=pn)
            return self.core.execute('SELECT loi_tai_lieu.ocr_chua_ro_ds(%s,%s)',
                (pn or self.pn, limit)).fetchone()[0]

    def _chot_admin(self, row, *, pn=None, ma=None, version=None, request_id=None, cu=False,
                    result='da_tieu', note='Đã đối chiếu bằng chứng DEMO ABBYY.', conn=None):
        conn = conn or self.core
        with conn.transaction():
            self._ngu_canh(conn, ma=ma, pn=pn, action=QUYEN_CHOT)
            args = (pn or self.pn, row['ma_tuong_quan'],
                    row['phien_ban'] if version is None else version, result, note)
            placeholders = '%s,%s,%s,%s,%s'
            if not cu:
                args += (request_id or uuid4(),)
                placeholders += ',%s'
            return conn.execute('SELECT loi_tai_lieu.ocr_chua_ro_chot_admin(' + placeholders + ')',
                                args).fetchone()[0]

    def _chua_ro(self, *, bam=BAM):
        row = self._giu(bam=bam, correlation='ocr:' + uuid4().hex)
        # Provisioning tình huống ABBYY chưa rõ; không giả runtime/phiên/MTQ.
        self.conn.execute("UPDATE loi_tai_lieu.bien_nhan_core SET trang_thai='CHUA_RO',"
            "ket_qua=ket_qua || '{\"trang_thai\":\"CHUA_RO\",\"phien_ban\":2}'::jsonb "
            'WHERE id=%s', (row['giu_trang_id'],))
        return {**row, 'trang_thai': 'CHUA_RO', 'phien_ban': 2}

    def _lease(self, *, het_han):
        # Dựng đủ FK hàng việc/bước/lần thử bằng dữ liệu DEMO.
        buoc, lan, instance = uuid4(), uuid4(), uuid4()
        phien_id = self.conn.execute('SELECT id FROM loi.phien_xac_thuc '
            "WHERE ma_bam=sha256(convert_to(%s,'UTF8'))",
            (self.ma_admin.lay_de_truyen(),)).fetchone()[0]
        self.conn.execute('INSERT INTO loi.buoc_viec(id,viec_id,phap_nhan_id,module,ma_buoc) '
            "VALUES (%s,%s,%s,'crm','OCR_DEMO')", (buoc, self.viec, self.pn))
        self.conn.execute('INSERT INTO loi.lan_thu(id,buoc_viec_id,viec_id,phap_nhan_id,module,'
            "so_lan,the_he,instance_id,phien_id) VALUES (%s,%s,%s,%s,'crm',1,1,%s,%s)",
            (lan, buoc, self.viec, self.pn, instance, phien_id))
        han = datetime.now(timezone.utc) + timedelta(minutes=-5 if het_han else 10)
        self.conn.execute("UPDATE loi.hang_viec SET trang_thai='DANG_CHAY',so_lan_thu=1,"
            'the_he=1,giu_boi=%s,giu_den=%s,giu_phien_id=%s,lan_thu_id=%s WHERE id=%s',
            (instance, han, phien_id, lan, self.viec))
        self.conn.execute('INSERT INTO loi.lan_thu_trang_thai(lan_thu_id,viec_id,phap_nhan_id,'
            "module,phien_ban_dong,trang_thai,giu_den) VALUES (%s,%s,%s,'crm',1,'DANG_CHAY',%s)",
            (lan, self.viec, self.pn, han))

    def _loi(self, state, fn, *args, **kwargs):
        with self.assertRaises(self.pg.Error) as caught:
            fn(*args, **kwargs)
        self.assertEqual(caught.exception.sqlstate, state)

    def _audit(self, row):
        return self.conn.execute('SELECT nguoi_dung_id,phap_nhan_id,module,hanh_dong,'
            'doi_tuong,doi_tuong_id,ket_luan,request_id FROM loi.nhat_ky_kiem_toan '
            "WHERE doi_tuong='ocr_doi_chieu_admin' AND doi_tuong_id=%s ORDER BY id",
            (row['giu_trang_id'],)).fetchall()

    def _nguoi_khong_admin(self):
        from kho_tri_thuc.core import phien
        actor = uuid4()
        self.conn.execute("INSERT INTO loi.nguoi_dung(id,dang_nhap,ten,vai_tro) VALUES (%s,%s,'DEMO','XEM')",
            (actor, 'demo_' + actor.hex))
        self.conn.execute('INSERT INTO loi.phan_quyen(nguoi_dung_id,phap_nhan_id,module) VALUES (%s,%s,%s)',
            (actor, self.pn, ['core']))
        return phien.cap_phien(self.core, nguoi_dung_id=actor, module='core', phap_nhan_id=self.pn,
            dang_nhap_csdl=self.cac_thong_tin['core']['user'], pham_vi_hanh_dong=[HANH_DONG, QUYEN_CHOT],
            hieu_luc_den=datetime.now(timezone.utc) + timedelta(minutes=10)).ma

    def test_khong_admin_du_biet_ma_tuong_quan_van_bi_tu_choi(self):
        row = self._chua_ro()
        ma = self._nguoi_khong_admin()
        self._loi('42501', self._ds, ma=ma)
        for cu in (False, True):
            with self.subTest(cu=cu):
                self._loi('42501', self._chot_admin, row, ma=ma, cu=cu)
        self.assertEqual(self._doc(), row)

    def test_login_module_khong_duoc_goi_ca_hai_chu_ky_chot(self):
        row = self._chua_ro()
        for cu in (False, True):
            with self.subTest(cu=cu):
                self._loi('42501', self._chot_admin, row, conn=self.module, cu=cu)
        self.assertEqual(self._doc(), row)
        self.assertEqual(self._audit(row), [])

    def test_cas_sai_khong_doi_trang_thai_va_ghi_chu(self):
        row = self._chua_ro()
        self._loi('40001', self._chot_admin, row, version=row['phien_ban'] + 1)
        self.assertEqual(self._doc(), row)
        audit = self.conn.execute('SELECT quyen_doc FROM loi_tai_lieu.bien_nhan_core WHERE id=%s',
            (row['giu_trang_id'],)).fetchone()[0]
        self.assertNotIn('doi_chieu_admin', audit)
        self.assertEqual(self._audit(row), [])

    def test_trang_thai_cuoi_khong_duoc_chot_lan_hai(self):
        row = self._chua_ro()
        final = self._chot_admin(row)
        self._loi('40001', self._chot_admin, final, result='hoan_trang')
        self.assertEqual(self._doc()['trang_thai'], 'DA_TIEU_TRANG')
        self.assertEqual(len(self._audit(row)), 1)

    def test_sau_chot_da_tieu_va_hoan_trang_gui_moi_duoc(self):
        for result, state in (('da_tieu', 'DA_TIEU_TRANG'), ('hoan_trang', 'HOAN_TRANG')):
            with self.subTest(result=result):
                row = self._chua_ro()
                final = self._chot_admin(row, result=result)
                self.assertEqual(final['trang_thai'], state)
                self.assertEqual(final['phien_ban'], row['phien_ban'] + 1)
                next_row = self._giu(viec=self._viec(), correlation='ocr:' + uuid4().hex)
                self.assertNotEqual(next_row['giu_trang_id'], row['giu_trang_id'])
                # Kết thúc lượt DEMO mới để lượt tiếp theo trong cùng ca độc lập.
                self.conn.execute("UPDATE loi_tai_lieu.bien_nhan_core SET trang_thai='HOAN_TAT',"
                    "ket_qua_cuoi_luc=clock_timestamp(),ket_qua=ket_qua || '{\"trang_thai\":\"HOAN_TRANG\"}'::jsonb "
                    'WHERE id=%s', (next_row['giu_trang_id'],))

    def test_danh_sach_khong_tra_bam_day_du_va_gioi_han_theo_phap_nhan(self):
        row = self._chua_ro()
        self._giu(pn=self.pn_khac, viec=self._viec(pn=self.pn_khac),
                  bam='b' * 64, correlation='ocr:' + uuid4().hex)
        page = self._ds(limit=1)
        self.assertEqual(len(page), 1)
        self.assertEqual(set(page[0]), {'ma_tuong_quan', 'so_trang', 'trang_thai', 'giu_luc',
            'module', 'ma_bam_dau', 'phien_ban'})
        self.assertEqual(page[0]['ma_tuong_quan'], row['ma_tuong_quan'])
        self.assertEqual(page[0]['ma_bam_dau'], BAM[:8])
        self.assertNotIn(BAM, json.dumps(page))
        self.assertNotIn('b' * 64, json.dumps(page))

    def test_dang_giu_chua_qua_han_khong_liet_ke_khong_chot(self):
        self._lease(het_han=False)
        row = self._giu(correlation='ocr:' + uuid4().hex)
        self.assertEqual(self._ds(), [])
        self._loi('40001', self._chot_admin, row)
        self.assertEqual(self._doc(), row)

    def test_dang_giu_qua_han_duoc_liet_ke_va_chot(self):
        self._lease(het_han=True)
        row = self._giu(correlation='ocr:' + uuid4().hex)
        page = self._ds()
        self.assertEqual([r['ma_tuong_quan'] for r in page], [row['ma_tuong_quan']])
        self.assertEqual(page[0]['trang_thai'], 'DANG_GIU')
        self.assertEqual(self._chot_admin(row, result='hoan_trang')['trang_thai'], 'HOAN_TRANG')

    def test_ngu_canh_gia_mao_phap_nhan_va_module_khong_qua_cua_sql(self):
        row = self._chua_ro()
        self._loi('42501', self._ds, pn=self.pn_khac)
        self._loi('42501', self._chot_admin, row, pn=self.pn_khac)
        for module, action in (('crm', HANH_DONG), ('core', 'CORE:MODULE:XEM')):
            with self.subTest(module=module, action=action), self.core.transaction():
                self._ngu_canh(self.core, module=module, action=action)
                with self.assertRaises(self.pg.Error) as caught, self.core.transaction():
                    self.core.execute('SELECT loi_tai_lieu.ocr_chua_ro_ds(%s,100)', (self.pn,))
                self.assertEqual(caught.exception.sqlstate, '42501')

    def test_bien_nhan_luu_nguoi_chot_ghi_chu_khong_pha_contract_core(self):
        from kho_tri_thuc.core.ocr_doi_chieu import _doc_ket_qua
        row = self._chua_ro()
        note = 'Đã soát bằng chứng DEMO, đã tiêu 3 trang.'
        request_id = uuid4()
        self._chot_admin(row, note=note, request_id=request_id)
        record, access = self.conn.execute('SELECT ket_qua,quyen_doc '
            'FROM loi_tai_lieu.bien_nhan_core WHERE id=%s', (row['giu_trang_id'],)).fetchone()
        self.assertEqual(_doc_ket_qua(record).phien_ban, 3)
        evidence = access['doi_chieu_admin']
        self.assertIn(str(self.nd), json.dumps(evidence))
        self.assertIn(note, json.dumps(evidence, ensure_ascii=False))
        self.assertEqual(evidence['trang_thai_truoc'], 'CHUA_RO')
        self.assertEqual(set(record), set(row))
        self.assertEqual(self._audit(row), [(self.nd, self.pn, 'core', QUYEN_CHOT,
            'ocr_doi_chieu_admin', UUID(row['giu_trang_id']),
            'DAT', request_id)])

    def test_chu_ky_cu_van_chot_duoc_va_giu_lien_ket_bien_nhan(self):
        row = self._chua_ro()
        final = self._chot_admin(row, cu=True)
        self.assertEqual(final['trang_thai'], 'DA_TIEU_TRANG')
        self.assertEqual(self._audit(row), [(self.nd, self.pn, 'core', QUYEN_CHOT,
            'ocr_doi_chieu_admin', UUID(row['giu_trang_id']), 'DAT', UUID(row['giu_trang_id']))])

    def test_request_id_null_tu_choi_truoc_cas_va_audit(self):
        row = self._chua_ro()
        with self.assertRaises(self.pg.Error) as caught:
            with self.core.transaction():
                self._ngu_canh(self.core, action=QUYEN_CHOT)
                self.core.execute('SELECT loi_tai_lieu.ocr_chua_ro_chot_admin(%s,%s,%s,%s,%s,%s)',
                    (self.pn, row['ma_tuong_quan'], row['phien_ban'], 'da_tieu', 'DEMO', None))
        self.assertEqual(caught.exception.sqlstate, '22023')
        self.assertEqual(self._doc(), row)
        self.assertEqual(self._audit(row), [])

    def test_phien_chi_xem_duoc_danh_sach_khong_duoc_chot(self):
        row = self._chua_ro()
        ma = self._cap(module='core', hd=[HANH_DONG])
        self.assertEqual(self._ds(ma=ma)[0]['ma_tuong_quan'], row['ma_tuong_quan'])
        for cu in (False, True):
            with self.subTest(cu=cu):
                self._loi('42501', self._chot_admin, row, ma=ma, cu=cu)
        self.assertEqual(self._doc(), row)
        self.assertEqual(self._audit(row), [])

    def test_ghi_chu_rong_trang_va_qua_dai_khong_doi_du_lieu(self):
        row = self._chua_ro()
        for note in ('', '   ', '\t\r\n', None, 'ế' * 501):
            with self.subTest(note=note):
                self._loi('22023', self._chot_admin, row, note=note)
                self.assertEqual(self._doc(), row)
                self.assertEqual(self._audit(row), [])
        self.assertEqual(self._chot_admin(row, note='ế' * 500)['phien_ban'], 3)
        self.assertEqual(len(self._audit(row)), 1)

    def test_dang_giu_luu_trang_thai_truoc_va_mot_dong_audit(self):
        self._lease(het_han=True)
        row = self._giu(correlation='ocr:' + uuid4().hex)
        self._chot_admin(row, result='hoan_trang')
        evidence = self.conn.execute("SELECT quyen_doc->'doi_chieu_admin' "
            'FROM loi_tai_lieu.bien_nhan_core WHERE id=%s', (row['giu_trang_id'],)).fetchone()[0]
        self.assertEqual(evidence['trang_thai_truoc'], 'DANG_GIU')
        self.assertEqual(evidence['chot_boi'], str(self.nd))
        self.assertEqual(len(self._audit(row)), 1)

    def test_dang_giu_thieu_lease_hoac_hang_viec_khong_chot(self):
        row = self._giu(correlation='ocr:' + uuid4().hex)
        # Hàng việc mới chưa có lease; rồi metadata tham chiếu hàng việc không tồn tại/sai mẫu.
        for viec in (str(self.viec), str(uuid4()), 'SAI_UUID', None):
            with self.subTest(viec=viec):
                self.conn.execute('UPDATE loi_tai_lieu.bien_nhan_core '
                    'SET ket_qua=jsonb_set(ket_qua,\'{viec_id}\',%s::jsonb) WHERE id=%s',
                    (json.dumps(viec), row['giu_trang_id']))
                self.assertEqual(self._ds(), [])
                self._loi('40001', self._chot_admin, row)
                self.assertEqual(self._doc()['trang_thai'], 'GIU')
                self.assertEqual(self._audit(row), [])

    def test_danh_sach_bo_ma_lech_mau_truoc_gioi_han(self):
        bad = self._chua_ro()
        good = self._chua_ro(bam='b' * 64)
        for correlation in ('DEMO_CU', 'ocr:', 'ocr:ABCD', 'ocr:' + 'a' * 125, 'ocr:ế'):
            with self.subTest(correlation=correlation):
                self.conn.execute('UPDATE loi_tai_lieu.bien_nhan_core '
                    'SET ket_qua=jsonb_set(ket_qua,\'{ma_tuong_quan}\',%s::jsonb) WHERE id=%s',
                    (json.dumps(correlation), bad['giu_trang_id']))
                self.assertEqual([r['ma_tuong_quan'] for r in self._ds(limit=1)], [good['ma_tuong_quan']])

    def test_doc_danh_sach_khong_chan_gia_han_lease_ket_noi_khac(self):
        self._lease(het_han=True)
        row = self._giu(correlation='ocr:' + uuid4().hex)
        with self.core.transaction():
            self.assertEqual(self._ds()[0]['ma_tuong_quan'], row['ma_tuong_quan'])
            # Giao dịch đọc vẫn mở khi engine gia hạn bằng kết nối thứ hai.
            with self.conn.transaction():
                self.conn.execute("SET LOCAL lock_timeout='500ms'")
                self.conn.execute("UPDATE loi.hang_viec SET giu_den=clock_timestamp()+interval '10 minutes' "
                    'WHERE id=%s', (self.viec,))
            self.assertEqual(self._ds(), [])
        self._loi('40001', self._chot_admin, row)
        self.assertEqual(self._doc(), row)

    def test_audit_loi_thi_cas_va_bang_chung_cung_rollback(self):
        row = self._chua_ro()
        sql = self.g209.sql
        owner = sql.Identifier(self.tien_to + 'vai_doi_cau_truc_loi_tai_lieu')
        self.conn.execute(sql.SQL('REVOKE EXECUTE ON FUNCTION {} FROM {}').format(sql.SQL(AUDIT), owner))
        try:
            self._loi('42501', self._chot_admin, row)
        finally:
            self.conn.execute(sql.SQL('GRANT EXECUTE ON FUNCTION {} TO {}').format(sql.SQL(AUDIT), owner))
        self.assertEqual(self._doc(), row)
        self.assertEqual(self._audit(row), [])
        access = self.conn.execute('SELECT quyen_doc FROM loi_tai_lieu.bien_nhan_core WHERE id=%s',
            (row['giu_trang_id'],)).fetchone()[0]
        self.assertNotIn('doi_chieu_admin', access)

    def test_admin_va_engine_cung_luot_chi_mot_thang_ca_hai_thu_tu(self):
        self._lease(het_han=True)
        connections = (self._ket_noi(), self._ket_noi())
        for admin_wins in (True, False):
            with self.subTest(admin_wins=admin_wins):
                bam = uuid4().hex * 2
                row = self._giu(bam=bam, correlation='ocr:' + uuid4().hex)
                locked, lost = Event(), Event()

                def chot(conn, admin):
                    if admin:
                        return self._chot_admin(row, conn=conn)
                    return self._chot(row, 'HOAN_TRANG', conn=conn, bam=bam)

                def winner():
                    try:
                        with connections[0].transaction():
                            result = chot(connections[0], admin_wins)
                            locked.set()
                            if not lost.wait(timeout=10):
                                raise AssertionError('Kết nối cạnh tranh chưa kết thúc')
                        return result
                    finally:
                        locked.set()

                def loser():
                    try:
                        if not locked.wait(timeout=10):
                            raise AssertionError('Chưa có kết nối giữ khóa')
                        with connections[1].transaction():
                            return chot(connections[1], not admin_wins)
                    except self.pg.Error as exc:
                        return exc.sqlstate, exc.diag.message_primary
                    finally:
                        lost.set()

                with ThreadPoolExecutor(max_workers=2) as pool:
                    win = pool.submit(winner)
                    lose = pool.submit(loser)
                    final, error = win.result(timeout=20), lose.result(timeout=20)
                self.assertEqual(error, ('40001', 'OCR_LUOT_XUNG_DOT' if admin_wins else 'OCR_ADMIN_XUNG_DOT'))
                record = self._doc(bam=bam)
                self.assertEqual(record['trang_thai'], 'DA_TIEU_TRANG' if admin_wins else 'HOAN_TRANG')
                self.assertEqual(record['phien_ban'], row['phien_ban'] + 1)
                self.assertEqual(final['phien_ban'], record['phien_ban'])
                self.assertEqual(len(self._audit(row)), int(admin_wins))
                state, access, has_final_time = self.conn.execute('SELECT trang_thai,quyen_doc,ket_qua_cuoi_luc IS NOT NULL '
                    'FROM loi_tai_lieu.bien_nhan_core WHERE id=%s', (row['giu_trang_id'],)).fetchone()
                self.assertEqual(state, 'HOAN_TAT')
                self.assertTrue(has_final_time)
                self.assertEqual('doi_chieu_admin' in access, admin_wins)
                if admin_wins:
                    self.assertEqual(access['doi_chieu_admin']['trang_thai_truoc'], 'DANG_GIU')

    def test_chay_lai_migration_giu_oid_owner_acl_va_du_lieu(self):
        row = self._chua_ro()
        query = 'SELECT oid,proowner,proacl,proconfig,prosecdef,prosrc FROM pg_proc '
        query += 'WHERE oid=ANY(%s::regprocedure[]) ORDER BY oid'
        signatures = list(SIGNATURES) + [CHOT_REQUEST]
        before = self.conn.execute(query, (signatures,)).fetchall()
        for _ in range(2):
            self.conn.execute(REQUEST_SQL_PATH.read_bytes().decode('utf-8'))
            self.assertEqual(self.conn.execute(query, (signatures,)).fetchall(), before)
            self.assertEqual(self._doc(), row)
            self.assertEqual(self._audit(row), [])
        request_id = uuid4()
        self._chot_admin(row, request_id=request_id)
        self.assertEqual(self._audit(row)[0][-1], request_id)

    def test_acl_chi_login_core_helper_chi_owner_tai_lieu(self):
        for signature, grantee in ((HELPER, self.tien_to + 'vai_doi_cau_truc_loi_tai_lieu'),
                                   (LEASE, self.tien_to + 'vai_doi_cau_truc_loi_tai_lieu'),
                                   (DANH_SACH, self.cac_thong_tin['core']['user']),
                                   (CHOT, self.cac_thong_tin['core']['user']),
                                   (CHOT_REQUEST, self.cac_thong_tin['core']['user'])):
            with self.subTest(signature=signature):
                metadata = self.conn.execute('SELECT prosecdef,proconfig FROM pg_proc '
                    'WHERE oid=%s::regprocedure', (signature,)).fetchone()
                self.assertIs(metadata[0], True)
                self.assertEqual([re.sub(r'\s*,\s*', ',', s) for s in metadata[1]],
                                 ['search_path=pg_catalog,pg_temp'])
                grants = self.conn.execute('SELECT pg_get_userbyid(a.grantee),a.privilege_type,'
                    'a.is_grantable FROM pg_proc p,LATERAL aclexplode(p.proacl) a '
                    'WHERE p.oid=%s::regprocedure AND a.grantee<>p.proowner', (signature,)).fetchall()
                self.assertEqual(grants, [(grantee, 'EXECUTE', False)])


if __name__ == '__main__':
    unittest.main()
