"""MASK-4a: kiểm byte/guard thuần; PG chỉ lead chạy trên CSDL test riêng.

Không khởi động/dừng dịch vụ, không đọc cấu hình/DSN từ tệp. Dữ liệu tự tạo
đều giả, có nhãn DEMO, kể cả ca kiểm vùng la_demo=false trong CSDL kho_test_*.
"""

from contextlib import contextmanager, nullcontext
from datetime import datetime, timedelta, timezone
import importlib.util
import os
from pathlib import Path
import re
import unittest
import unicodedata
from unittest.mock import MagicMock
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = ROOT / 'src/kho_tri_thuc/core/sql/117_mask_duyet_cho.sql'
PUBLIC = {
    'doc_cho': 'text,uuid,text,text,date,date,timestamp with time zone,uuid,integer',
    'duyet_cho': 'text,uuid,uuid,text',
    'tu_choi_cho': 'text,uuid,uuid',
    'don_bi_danh_tam': 'text,uuid',
}
HD = ['CORE:MODULE:XEM', 'CORE:MODULE:DUYET', 'CORE:MODULE:SUA']


def doc_sql():
    # Đọc byte gốc, không universal-newline để tránh xanh giả với BOM/encoding.
    return SQL_PATH.read_bytes().decode('utf-8', errors='strict')


def cac_ham(sql):
    return dict(re.findall(
        r'CREATE OR REPLACE FUNCTION (?:loi|mask)\.(\w+)\(.*?'
        r'AS \$ham\$(.*?)\$ham\$;', sql, re.S))


TOKEN_SQL = re.compile(
    rb'\s+|--[^\r\n]*|/\*.*?\*/|\'(?:\'\'|[^\'])*\'|"(?:""|[^"])*"|'
    rb'(?P<tag>\$(?:[A-Za-z_][A-Za-z0-9_]*)?\$)(?P<body>.*?)(?P=tag)|'
    rb'[A-Za-z_][A-Za-z0-9_]*|.', re.S)


def token_sql(raw):
    """Giữ chuỗi/dollar quote nguyên khối trước khi bỏ comment, trên byte gốc."""
    tokens, bodies = [], []
    for match in TOKEN_SQL.finditer(raw):
        part = match.group()
        if match.group('tag'):
            tokens.append(b'$BODY$')
            bodies.append((match.group('tag'), match.group('body')))
        elif part.isspace() or part.startswith((b'--', b'/*')):
            continue
        elif part in (b"'", b'"', b'$') or raw.startswith(b'/*', match.start()):
            raise AssertionError('Chuỗi/comment/dollar tag chưa đóng')
        else:
            tokens.append(part if part.startswith((b"'", b'"')) else part.upper())
    return tokens, bodies


def kiem_cau_truc_sql(raw):
    """Guard cấu trúc của 117, không thay thế parser PostgreSQL do lead chạy."""
    tokens, bodies = token_sql(raw)
    if tokens != [b'DO', b'$BODY$', b';'] or len(bodies) != 1 or bodies[0][0] != b'$migration$':
        raise AssertionError('Khối migration/dollar tag không kết thúc đúng')

    def kiem_body(body):
        tokens, nested = token_sql(body)
        for child_tag, child in nested:
            if child_tag == b'$migration$':
                raise AssertionError('Tag hàm trùng migration')
            kiem_body(child)
        pairs = {}
        opens = []
        for i, token in enumerate(tokens):
            if token == b'(':
                opens.append(i)
            elif token == b')':
                if not opens:
                    raise AssertionError('Ngoặc không cân bằng')
                pairs[opens.pop()] = i
            elif token == b'$BODY$' and (tokens[i-1] != b'AS' or tokens[i+1:i+2] != [b';']):
                raise AssertionError('Thân hàm/dollar tag không kết thúc đúng')
        if opens:
            raise AssertionError('Ngoặc không cân bằng')
        blocks, i = [], 0
        while i < len(tokens):
            token = tokens[i]
            if token == b'BEGIN':
                blocks.append(b'BEGIN')
            elif token == b'IF' and (i == 0 or tokens[i-1] in (b';', b'BEGIN', b'THEN', b'ELSE', b'LOOP')):
                blocks.append(b'IF')
                i += 1
                depth = 0
                while i < len(tokens):
                    token = tokens[i]
                    if token == b'CASE' and depth == 0:
                        raise AssertionError('CASE trong điều kiện IF chưa bọc ngoặc')
                    if token == b'THEN' and depth == 0:
                        break
                    if token in (b';', b'END') and depth == 0:
                        raise AssertionError('Điều kiện IF thiếu THEN')
                    depth += (token == b'(') - (token == b')')
                    i += 1
                else:
                    raise AssertionError('Điều kiện IF thiếu THEN')
            elif token == b'CASE':
                # CASE biểu thức trong SELECT/WHERE không đóng khối PL/pgSQL.
                depth = 1
                while depth and i+1 < len(tokens):
                    i += 1
                    if tokens[i] == b';':
                        raise AssertionError('Biểu thức CASE thiếu END')
                    depth += (tokens[i] == b'CASE') - (tokens[i] == b'END')
                if depth:
                    raise AssertionError('Biểu thức CASE thiếu END')
            elif token == b'LOOP':
                blocks.append(b'LOOP')
            elif token == b'END':
                kind = tokens[i+1] if tokens[i+1:i+2] in ([b'IF'], [b'LOOP']) else b'BEGIN'
                if not blocks or blocks.pop() != kind:
                    raise AssertionError('Cặp BEGIN/IF/LOOP và END không khớp')
                if tokens[i-1] not in (b';', b'BEGIN', b'THEN', b'ELSE', b'LOOP'):
                    raise AssertionError('Câu lệnh trước END thiếu dấu chấm phẩy')
                i += kind != b'BEGIN'
                if tokens[i+1:i+2] != [b';']:
                    raise AssertionError('END thiếu dấu chấm phẩy')
            elif token == b'EXECUTE':
                if tokens[i+1:i+3] != [b'FORMAT', b'(']:
                    raise AssertionError('EXECUTE phải dùng format trong migration 117')
                end = pairs[i+2]
                if not tokens[i+3].startswith(b"'") or tokens[end+1:end+2] != [b';']:
                    raise AssertionError('EXECUTE format chưa đóng đúng')
            i += 1
        if blocks or tokens[-2:] != [b'END', b';']:
            raise AssertionError('Khối BEGIN/IF/LOOP chưa kết thúc')

    kiem_body(bodies[0][1])


class SQLThuanTests(unittest.TestCase):
    def test_utf8_nguyen_byte_khong_bom_hay_mat_dau(self):
        raw = SQL_PATH.read_bytes()
        text = doc_sql()
        self.assertFalse(raw.startswith(b'\xef\xbb\xbf'))
        self.assertEqual(text.encode('utf-8'), raw)
        self.assertNotIn('\ufffd', text)
        self.assertEqual(unicodedata.normalize('NFC', text), text)
        for cum in ('Chỉ cửa Admin Core', 'Không trả cụm gốc', 'không cắt/sửa ngầm'):
            self.assertIn(cum, text)

    def test_117_khong_trung_so_va_chuoi_migration_doc_duoc_byte(self):
        from kho_tri_thuc.core.doi_cau_truc import _doc_chuoi
        files = list(SQL_PATH.parent.glob('[0-9][0-9][0-9]_*.sql'))
        self.assertEqual([p.name for p in files if p.name.startswith('117_')], [SQL_PATH.name])
        chain = _doc_chuoi(files)
        self.assertEqual(chain[117][0], doc_sql())

    def test_dollar_tag_can_bang_va_khong_dong_som_do_ngoac_trong_comment(self):
        sql = doc_sql()
        self.assertEqual(re.findall(r'\$[A-Za-z_]*\$', sql),
                         ['$migration$'] + ['$ham$'] * 12 + ['$migration$'])
        self.assertTrue(sql.rstrip().endswith('$migration$;'))
        self.assertEqual(set(cac_ham(sql)), set(PUBLIC) | {'mask_kiem_admin', 'giu_cum_tu_choi'})
        for body in cac_ham(sql).values():
            self.assertRegex(body, r'(?s)^\s*DECLARE\b.*\bBEGIN\b.*END;\s*$')

    def test_cau_truc_nguyen_byte_migration_va_moi_than_ham(self):
        kiem_cau_truc_sql(SQL_PATH.read_bytes())

    def test_guard_bat_case_tran_trong_if_khong_nham_then_cua_case(self):
        condition = b'IF x<>(CASE WHEN x=1 THEN 2 ELSE 3 END) THEN NULL; END IF;'
        for wrapped in (condition, condition.replace(b'<>(CASE', b'<>CASE').replace(b'END)', b'END')):
            for body in (wrapped, b'CREATE FUNCTION f() RETURNS void AS $ham$ BEGIN '+wrapped+b' END; $ham$;'):
                raw = b'DO $migration$ BEGIN '+body+b' END; $migration$;'
                with self.subTest(boc_ngoac=wrapped == condition, than_ham=body != wrapped):
                    if wrapped == condition:
                        kiem_cau_truc_sql(raw)
                    else:
                        with self.assertRaisesRegex(AssertionError, 'CASE.*IF.*ngoặc'):
                            kiem_cau_truc_sql(raw)
        expression = b'SELECT (CASE WHEN x=1 THEN (CASE WHEN y=1 THEN 2 ELSE 3 END) ELSE 4 END);'
        kiem_cau_truc_sql(b'DO $migration$ BEGIN '+expression+b' END; $migration$;')
        with self.assertRaisesRegex(AssertionError, 'CASE thiếu END'):
            kiem_cau_truc_sql(b'DO $migration$ BEGIN '+expression.replace(b' END)', b')', 1)+b' END; $migration$;')

    def test_guard_bat_tag_thieu_va_tag_ham_trung_migration(self):
        raw = SQL_PATH.read_bytes()
        for broken in (raw.replace(b'$ham$;', b'$sai$;', 1),
                       raw.replace(b'$ham$', b'$migration$'),
                       raw.replace(b'$migration$;', b'$sai$;', 1)):
            with self.subTest(tag=broken.count(b'$ham$')), self.assertRaises(AssertionError):
                kiem_cau_truc_sql(broken)

    def test_guard_bat_khoi_thieu_sai_thu_tu_va_thieu_cham_phay(self):
        raw = SQL_PATH.read_bytes()
        for before, after in ((b'END IF;', b''), (b'END LOOP;', b''),
                              (b'END IF;', b'END LOOP;'), (b'END;', b''),
                              (b'END IF;', b'END IF'), (b'END LOOP;', b'END LOOP'),
                              (b'END;', b'END'), (b'true);\n    END;', b'true)\n    END;')):
            # Mẫu byte giữ nguyên kiểu xuống dòng của tệp, không chuẩn hóa SQL.
            before = before.replace(b'\n', b'\r\n') if b'\r\n' in raw else before
            after = after.replace(b'\n', b'\r\n') if b'\r\n' in raw else after
            self.assertIn(before, raw)
            with self.subTest(before=before), self.assertRaises(AssertionError):
                kiem_cau_truc_sql(raw.replace(before, after, 1))

    def test_guard_bat_execute_format_cat_chuoi_ngoac_va_cham_phay(self):
        raw = SQL_PATH.read_bytes()
        call = b"EXECUTE format('SET LOCAL ROLE %I',chu_mask);"
        for broken in (call.replace(b"%I'", b'%I'), call.replace(b');', b';'),
                       call[:-1], call.replace(b');', b') thua;')):
            with self.subTest(call=broken), self.assertRaises(AssertionError):
                kiem_cau_truc_sql(raw.replace(call, broken, 1))
        # Từ khóa/tag/ngoặc giả trong chuỗi và dấu nháy đơn trong comment không
        # được che mất phần SQL thật hoặc tạo khối giả.
        kiem_cau_truc_sql(b"DO $migration$ BEGIN -- ' END IF; (\n"
                         b"IF true THEN EXECUTE format('END LOOP; $gia$ '' ('); "
                         b"END IF; END; $migration$;")

    def test_guard_truoc_ddl_chan_dich_va_vai_gia(self):
        sql = doc_sql()
        guard = sql[:sql.index('ALTER TABLE mask.cho_duyet')]
        for part in ("tt !~ '^[a-z][a-z0-9_]*_$'", 'octet_length(',
                     "current_database() !~ '^kho_test_'", 'kho_core_demo_g2_',
                     "current_setting('server_version_num')::integer<160000",
                     "vai_cu<>'none'", 'rolsuper', 'rolbypassrls', 'pg_auth_members',
                     'relrowsecurity AND relforcerowsecurity', 'MASK_DUYET_SAI_OWNER'):
            self.assertIn(part, guard)

    def test_tat_ca_cua_definer_search_path_co_dinh(self):
        sql = doc_sql()
        self.assertEqual(sql.count('SECURITY DEFINER SET search_path=pg_catalog,pg_temp'), 5)
        self.assertNotIn('SECURITY INVOKER', sql)
        self.assertIn("'REVOKE ALL ON FUNCTION %s FROM PUBLIC'", sql)
        self.assertIn('aclexplode(b.proacl)', sql)
        self.assertIn("IF b.proname IN ('doc_cho','duyet_cho','tu_choi_cho','don_bi_danh_tam') THEN", sql)
        self.assertIn("ELSIF b.proname='mask_kiem_admin' THEN", sql)
        self.assertIn("'GRANT EXECUTE ON FUNCTION %s TO %I',ck,login", sql)
        self.assertIn("'GRANT EXECUTE ON FUNCTION %s TO %I',ck,chu_mask", sql)
        self.assertNotIn('GRANT SELECT ON', sql)
        self.assertNotRegex(sql, r'GRANT (?:SELECT|INSERT|UPDATE|DELETE)')
        self.assertNotIn('ALTER POLICY', sql)

    def test_phien_admin_suy_demo_sau_xac_minh_khong_tin_guc(self):
        sql = doc_sql()
        helper = cac_ham(sql)['mask_kiem_admin']
        for part in ('session_user::text', "p.loai='NGUOI_DUNG'", 'sha256(convert_to(p_ma,',
                     'loi.xac_minh_phien(', 'ai IS DISTINCT FROM p_nguoi',
                     'loi.mtq_admin', 'a.thu_hoi_luc IS NULL', 'n.id,n.la_demo'):
            self.assertIn(part, helper)
        self.assertLess(helper.index('loi.xac_minh_phien('), helper.index('n.id,n.la_demo'))
        self.assertNotIn('p_la_demo', sql)
        for name in PUBLIC:
            body = cac_ham(sql)[name]
            self.assertLess(body.index('loi.mask_kiem_admin('), body.index("set_config('ktt.mask_la_demo'"))
            self.assertIn("ctx.la_demo::text,true", body)
            self.assertIn("coalesce(cu,''),true", body)

    def test_keyset_loc_nhom_trang_thai_va_ngay_viet_nam(self):
        body = cac_ham(doc_sql())['doc_cho']
        for part in ('(c.tao_luc,c.id)>(p_sau_luc,p_sau_id)', 'ORDER BY c.tao_luc,c.id LIMIT p_gioi_han',
                     'p_gioi_han NOT BETWEEN 1 AND 200', 'c.nhom=p_nhom', 'y.trang_thai=p_trang_thai',
                     "AT TIME ZONE 'Asia/Ho_Chi_Minh'", 'p_den_ngay+1', 'c.so_lan_gap',
                     'GIÁ TRỊ cum_goc chỉ trả ở cửa Admin', '(p_sau_luc IS NULL)<>(p_sau_id IS NULL)'):
            self.assertIn(part, body)
        self.assertNotRegex(body, r'\bOFFSET\b')

    def test_duyet_dung_trigger_113_chuyen_tam_khong_ghi_de(self):
        body = cac_ham(doc_sql())['duyet_cho']
        self.assertIn('FOR UPDATE', body)
        self.assertIn("w.trang_thai='CHO_DUYET'", body)
        self.assertIn('c.cum_goc,c.nhom,p_ma_junsky,c.bi_danh_tam,c.nguon,ctx.la_demo', body)
        self.assertNotIn('ON CONFLICT', body)
        self.assertNotIn('UPDATE mask.dinh_danh', body)
        self.assertIn("c.cum_goc ~ '[\\[\\]]'", body)
        self.assertIn('WHEN unique_violation THEN', body)
        self.assertIn('WHEN check_violation THEN', body)
        self.assertLess(body.index('INSERT INTO mask.dinh_danh'), body.index('DELETE FROM mask.cho_duyet'))

    def test_chi_xoa_dong_cho_khong_xoa_dinh_danh_hay_ma_yeu_cau(self):
        sql = doc_sql()
        self.assertEqual(re.findall(r'DELETE FROM ([a-z_.]+)', sql), ['mask.cho_duyet'] * 2)
        self.assertNotRegex(sql, r'(?i)\b(DROP|TRUNCATE|COMMIT)\s+(TABLE|SCHEMA|DATABASE)\b')

    def test_tu_choi_giu_cap_tam_va_mac_dinh_khong_doc_lai(self):
        sql = doc_sql()
        functions = cac_ham(sql)
        refused, read = functions['tu_choi_cho'], functions['doc_cho']
        self.assertIn("NOT NULL DEFAULT 'CHO_DUYET' CHECK (trang_thai IN ('CHO_DUYET','DA_TU_CHOI'))", sql)
        self.assertIn("UPDATE mask.cho_duyet c SET trang_thai='DA_TU_CHOI'", refused)
        self.assertNotIn('DELETE FROM', refused)
        self.assertNotIn('bi_danh_tam=', refused)
        self.assertIn("c.trang_thai=(CASE WHEN p_trang_thai='DA_TU_CHOI' THEN 'DA_TU_CHOI' ELSE 'CHO_DUYET' END)", read)
        repeat = functions['giu_cum_tu_choi']
        for part in ('so_lan_gap=c.so_lan_gap+1', 'w.la_demo=NEW.la_demo',
                     'w.cum_chuan=mask.chuan_hoa(NEW.cum_goc) FOR UPDATE',
                     "IF FOUND AND dong.trang_thai='DA_TU_CHOI' THEN", 'RETURN NULL;'):
            self.assertIn(part, repeat)
        self.assertLess(repeat.index('FOR UPDATE'), repeat.index("dong.trang_thai='DA_TU_CHOI'"))
        self.assertIn('BEFORE INSERT ON mask.cho_duyet', sql)
        self.assertIn("tgfoid='mask.giu_cum_tu_choi()'::regprocedure", sql)
        trigger = sql[sql.index('CREATE OR REPLACE FUNCTION mask.giu_cum_tu_choi'):]
        self.assertNotIn('SECURITY DEFINER', trigger[:trigger.index('$ham$;')])

    def test_don_chi_cot_tam_bo_qua_moi_ma_dang_xu_ly_cung_vung(self):
        body = cac_ham(doc_sql())['don_bi_danh_tam']
        for part in ('read committed', 'LOCK TABLE mask.yeu_cau IN SHARE MODE',
                     'UPDATE mask.dinh_danh d SET bi_danh_tam=NULL', 'd.la_demo=ctx.la_demo',
                     'NOT EXISTS', 'y.la_demo=ctx.la_demo', "y.trang_thai='DANG_XU_LY'",
                     'd.bi_danh_tam=ANY(y.bi_danh_tam_da_dung)', 'RETURN so;'):
            self.assertIn(part, body)
        self.assertLess(body.index('LOCK TABLE'), body.index('UPDATE mask.dinh_danh'))
        deleted = body[body.index('DELETE FROM mask.cho_duyet'):]
        for part in ("c.la_demo=ctx.la_demo AND c.trang_thai='DA_TU_CHOI'", 'NOT EXISTS',
                     'y.la_demo=ctx.la_demo', "y.trang_thai='DANG_XU_LY'",
                     'c.bi_danh_tam=ANY(y.bi_danh_tam_da_dung)', 'RETURNING c.id LOOP',
                     "PERFORM loi.mask_kiem_admin(p_ma,p_nguoi,'DON',ma)"):
            self.assertIn(part, deleted)

    def test_audit_chi_ma_hanh_dong_co_dinh_va_id_khong_gia_tri(self):
        functions = cac_ham(doc_sql())
        helper = functions['mask_kiem_admin']
        calls = re.findall(r'PERFORM loi\.ghi_kiem_toan\((.*?)\);', helper, re.S)
        self.assertEqual(calls, ["hd,dt,p_id,'DAT',p_ma,'core',pn"])
        mapping = re.findall(r"\('([A-Z_]+)','(CORE:MODULE:[A-Z]+)','(mask\.[a-z_.]+)'\)", helper)
        self.assertEqual(len(mapping), 4)
        self.assertIn('WHERE v.thao_tac=p_thao_tac', helper)
        self.assertIn('IF NOT FOUND THEN', helper)
        for name in PUBLIC:
            self.assertIn('loi.mask_kiem_admin(', functions[name])
            self.assertNotIn('loi.ghi_kiem_toan(', functions[name])
        self.assertIn("PERFORM loi.mask_kiem_admin(p_ma,p_nguoi,'DON',ma)", functions['don_bi_danh_tam'])

    def test_adapter_pg_goi_dung_schema_va_bind_khong_chen_sql(self):
        pg = PostgresTests(methodName='runTest')
        pg.owner = MagicMock()
        pg.login_core = nullcontext
        pg.token, pg.ai = 'DEMO-ma-phien', uuid4()
        ma = "DEMO'); SELECT 'khong_duoc_chen"
        cho = uuid4()
        pg.goi('duyet_cho', cho, ma)
        query, args = pg.owner.execute.call_args.args
        self.assertEqual(query, 'SELECT * FROM mask.duyet_cho(%s,%s,%s,%s)')
        self.assertEqual(args, (pg.token, pg.ai, cho, ma))
        self.assertNotIn(ma, query)


@unittest.skipUnless(os.environ.get('KHO_PG_DSN_TEST') and importlib.util.find_spec('psycopg'),
                     'CHUA_KIEM PG MASK-4a: chỉ lead chạy; worker chỉ thuần/mock')
class PostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import test_g2_25 as pg
        cls.pg = pg
        pg.PostgresTests.setUpClass.__func__(cls)

    def setUp(self):
        # Cùng một kết nối để fixture không commit và các ca không để dữ liệu lại.
        self.enterContext(self.owner.transaction(force_rollback=True))
        self.pn, self.ai = uuid4(), uuid4()
        self.owner.execute("INSERT INTO loi.phap_nhan(id,ma,ten,la_demo) VALUES(%s,%s,'DEMO',true)",
                           (self.pn, self.pn.hex))
        self.owner.execute("INSERT INTO loi.nguoi_dung(id,dang_nhap,ten,vai_tro) VALUES(%s,%s,'DEMO','CFO')",
                           (self.ai, self.ai.hex))
        self.owner.execute("INSERT INTO loi.phan_quyen(nguoi_dung_id,phap_nhan_id,module) VALUES(%s,%s,ARRAY['core'])",
                           (self.ai, self.pn))
        self.owner.execute("INSERT INTO loi.mtq_admin(nguoi_dung_id,cap_boi,ly_do) VALUES(%s,%s,'DEMO')",
                           (self.ai, self.ai))
        self.token = self.cap_phien()
        self.owner.execute("SELECT set_config('ktt.mask_la_demo','true',true)")

    @contextmanager
    def login_core(self):
        with self.owner.transaction():
            self.owner.execute(self.pg.sql.SQL('SET LOCAL SESSION AUTHORIZATION {}').format(
                self.pg.sql.Identifier(self.tt + 'dang_nhap_loi')))
            try:
                yield
            finally:
                # Nếu SQL lỗi, savepoint ngoài tự khôi phục; không chạy RESET trong
                # transaction đã lỗi vì sẽ che mất lỗi cần kiểm.
                if self.owner.info.transaction_status != self.pg.psycopg.pq.TransactionStatus.INERROR:
                    self.owner.execute('RESET SESSION AUTHORIZATION')

    def cap_phien(self, actions=None):
        from kho_tri_thuc.core import phien
        with self.login_core():
            return phien.cap_phien(self.owner, nguoi_dung_id=self.ai, module='core',
                phap_nhan_id=self.pn, dang_nhap_csdl=self.tt+'dang_nhap_loi',
                pham_vi_hanh_dong=actions or HD,
                hieu_luc_den=datetime.now(timezone.utc)+timedelta(minutes=5)).ma.lay_de_truyen()

    def goi(self, name, *args, token=None, ai=None):
        values = (token or self.token, ai or self.ai, *args)
        with self.login_core():
            return self.owner.execute('SELECT * FROM mask.' + name + '(' +
                ','.join(['%s'] * len(values)) + ')', values).fetchall()

    @contextmanager
    def loi_mask(self, error, message):
        # Cùng SQLSTATE có nhiều nhánh từ chối; phải chạm đúng hàng rào cần kiểm.
        with self.assertRaises(error) as caught:
            yield
        self.assertEqual(caught.exception.diag.message_primary, message)
        self.assertIsNone(caught.exception.diag.message_detail)

    def cho(self, *, nhom='CONG_TY', demo=True, cum=None, trang_thai='DANG_XU_LY', luc=None):
        value = cum or 'Công ty DEMO ' + uuid4().hex
        y = self.owner.execute("""INSERT INTO mask.yeu_cau(module,nguoi_gui,tai_lieu_id,la_demo)
            VALUES('demo',%s,%s,%s) RETURNING id""", (self.ai, uuid4(), demo)).fetchone()[0]
        c = self.owner.execute("""INSERT INTO mask.cho_duyet(cum_goc,nhom,yeu_cau_id,nguon,la_demo,tao_luc)
            VALUES(%s,%s,%s,'DEMO',%s,coalesce(%s,statement_timestamp())) RETURNING id,bi_danh_tam""",
            (value, nhom, y, demo, luc)).fetchone()
        self.owner.execute('UPDATE mask.yeu_cau SET bi_danh_tam_da_dung=ARRAY[%s] WHERE id=%s', (c[1], y))
        if trang_thai == 'DA_DONG':
            self.dong(y)
        return c[0], c[1], y, value

    def dong(self, y):
        self.owner.execute("UPDATE mask.yeu_cau SET trang_thai='DA_DONG',dong_luc=clock_timestamp() WHERE id=%s", (y,))

    def thu_hoi_admin(self):
        # Giữ Admin dự phòng và lịch sử cấp quyền đúng bất biến MTQ.
        admin_khac = uuid4()
        self.owner.execute("INSERT INTO loi.nguoi_dung(id,dang_nhap,ten,vai_tro) VALUES(%s,%s,'DEMO','CFO')",
                           (admin_khac, admin_khac.hex))
        self.owner.execute("INSERT INTO loi.mtq_admin(nguoi_dung_id,cap_boi,ly_do) VALUES(%s,%s,'DEMO')",
                           (admin_khac, self.ai))
        self.owner.execute('UPDATE loi.mtq_admin SET thu_hoi_luc=clock_timestamp(),thu_hoi_boi=%s,'
            'phien_ban_dong=phien_ban_dong+1 WHERE nguoi_dung_id=%s AND thu_hoi_luc IS NULL',
            (admin_khac, self.ai))

    def test_login_core_that_khong_doc_bang_va_acl_ham_chi_core(self):
        for name, types in PUBLIC.items():
            signature = 'mask.' + name + '(' + types + ')'
            for role in ('vai_chay_loi', 'vai_chay_mask', 'dang_nhap_cai_dat', 'vai_xuat_phap_nhan'):
                self.assertFalse(self.owner.execute('SELECT has_function_privilege(%s,%s,%s)',
                    (self.tt+role, signature, 'EXECUTE')).fetchone()[0])
            self.assertTrue(self.owner.execute('SELECT has_function_privilege(%s,%s,%s)',
                (self.tt+'dang_nhap_loi', signature, 'EXECUTE')).fetchone()[0])
        self.assertFalse(self.owner.execute('SELECT has_function_privilege(%s,%s,%s)',
            (self.tt+'dang_nhap_loi', 'loi.mask_kiem_admin(text,uuid,text,uuid)', 'EXECUTE')).fetchone()[0])
        for table in ('dinh_danh', 'cho_duyet', 'yeu_cau'):
            with self.subTest(bang=table), self.assertRaises(self.pg.psycopg.errors.InsufficientPrivilege):
                with self.login_core():
                    self.assertEqual(self.owner.execute('SELECT session_user').fetchone()[0], self.tt+'dang_nhap_loi')
                    self.owner.execute('SELECT * FROM mask.'+table)
        for role in ('dang_nhap_loi', 'vai_chay_mask', 'vai_chay_loi'):
            self.assertFalse(self.owner.execute('SELECT has_function_privilege(%s,%s,%s)',
                (self.tt+role, 'mask.giu_cum_tu_choi()', 'EXECUTE')).fetchone()[0])

    def test_khong_admin_tu_choi_moi_cua(self):
        c = self.cho()
        # Thu hồi có lưu lịch sử; phiên bị thu hồi khi đổi quyền cũng phải từ chối.
        self.thu_hoi_admin()
        for name, args in (('doc_cho', ()), ('duyet_cho', (c[0],)),
                           ('tu_choi_cho', (c[0],)), ('don_bi_danh_tam', ())):
            with self.subTest(cua=name), self.loi_mask(self.pg.psycopg.errors.InsufficientPrivilege, 'MASK_PHIEN'):
                self.goi(name, *args)
        self.assertEqual(self.owner.execute('SELECT count(*) FROM mask.cho_duyet WHERE id=%s', (c[0],)).fetchone()[0], 1)

    def test_admin_da_thu_hoi_va_thieu_pham_vi_khong_duoc_duyet(self):
        c = self.cho()
        chi_doc = self.cap_phien(actions=['CORE:MODULE:XEM'])
        self.assertEqual([r[0] for r in self.goi('doc_cho', token=chi_doc)], [c[0]])
        with self.loi_mask(self.pg.psycopg.errors.InsufficientPrivilege, 'MASK_PHIEN'):
            self.goi('duyet_cho', c[0], token=chi_doc)
        self.thu_hoi_admin()
        for name, args in (('doc_cho', ()), ('duyet_cho', (c[0],)),
                           ('tu_choi_cho', (c[0],)), ('don_bi_danh_tam', ())):
            with self.subTest(cua=name), self.loi_mask(self.pg.psycopg.errors.InsufficientPrivilege, 'MASK_PHIEN'):
                self.goi(name, *args)

    def test_chua_tung_admin_co_pham_vi_module_van_bi_chan_dung_cua(self):
        c = self.cho()
        self.ai = uuid4()
        self.owner.execute("INSERT INTO loi.nguoi_dung(id,dang_nhap,ten,vai_tro) VALUES(%s,%s,'DEMO','CFO')",
                           (self.ai, self.ai.hex))
        self.owner.execute("INSERT INTO loi.phan_quyen(nguoi_dung_id,phap_nhan_id,module) VALUES(%s,%s,ARRAY['core'])",
                           (self.ai, self.pn))
        # Dùng cửa cấp phiên sẵn có, không sửa bảng phiên/không từng cấp Admin.
        self.token = self.cap_phien(actions=HD)
        self.assertEqual(self.owner.execute('SELECT count(*) FROM loi.mtq_admin WHERE nguoi_dung_id=%s',
                                           (self.ai,)).fetchone()[0], 0)
        for name, args in (('doc_cho', ()), ('duyet_cho', (c[0],)),
                           ('tu_choi_cho', (c[0],)), ('don_bi_danh_tam', ())):
            with self.subTest(cua=name), self.loi_mask(self.pg.psycopg.errors.InsufficientPrivilege, 'MASK_CHI_ADMIN'):
                self.goi(name, *args)
        self.assertEqual(self.owner.execute('SELECT trang_thai FROM mask.cho_duyet WHERE id=%s',
                                           (c[0],)).fetchone()[0], 'CHO_DUYET')

    def test_phien_sai_nguoi_het_han_va_thu_hoi_khong_doc_cum(self):
        for token, ai in (('DEMO-khong-co-phien', self.ai), (self.token, uuid4())):
            with self.subTest(ai=ai), self.loi_mask(self.pg.psycopg.errors.InsufficientPrivilege, 'MASK_PHIEN'):
                self.goi('doc_cho', token=token, ai=ai)
        for assignment in ("thu_hoi_luc=statement_timestamp()",
                           "tao_luc=statement_timestamp()-interval '2 hours',hieu_luc_den=statement_timestamp()-interval '1 hour'"):
            with self.owner.transaction(force_rollback=True):
                self.owner.execute('UPDATE loi.phien_xac_thuc SET '+assignment+' WHERE nguoi_dung_id=%s', (self.ai,))
                with self.loi_mask(self.pg.psycopg.errors.InsufficientPrivilege, 'MASK_PHIEN'):
                    self.goi('doc_cho')

    def test_duyet_junsky_chuyen_tam_va_ma_yeu_cau_giu_nguyen(self):
        c = self.cho()
        before = self.owner.execute('SELECT * FROM mask.yeu_cau ORDER BY id').fetchall()
        official = 'KH-DEMO-'+uuid4().hex
        result = self.goi('duyet_cho', c[0], official)[0]
        self.assertEqual(result[1], '[['+official+']]')
        self.assertEqual(self.owner.execute('SELECT bi_danh_tam,gia_tri,ma_junsky FROM mask.dinh_danh WHERE id=%s',
            (result[0],)).fetchone(), (c[1], c[3], official))
        self.assertEqual(self.owner.execute('SELECT count(*) FROM mask.cho_duyet WHERE id=%s', (c[0],)).fetchone()[0], 0)
        self.assertEqual(self.owner.execute('SELECT * FROM mask.yeu_cau ORDER BY id').fetchall(), before)

    def test_duyet_tu_sinh_dung_moi_loai_113(self):
        from tools.chuyen_danh_muc_mask import TIEN_TO
        for nhom, prefix in TIEN_TO.items():
            c = self.cho(nhom=nhom)
            alias = self.goi('duyet_cho', c[0])[0][1]
            self.assertRegex(alias, r'^\[\['+prefix+r'-[0-9]{4,}\]\]$')

    def test_ngoac_va_junsky_trung_khong_lo_gia_tri_khong_mat_dong_cho(self):
        c = self.cho(cum='Cụm [DEMO CANARY]')
        with self.assertRaises(self.pg.psycopg.errors.InvalidParameterValue) as caught:
            self.goi('duyet_cho', c[0])
        self.assertEqual(caught.exception.diag.message_primary, 'MASK_CUM_KHONG_HOP_LE')
        self.assertNotIn('CANARY', caught.exception.diag.message_primary)
        self.assertIsNone(caught.exception.diag.message_detail)
        c1, c2 = self.cho(), self.cho()
        self.goi('duyet_cho', c1[0], 'KH-DEMO-Canary')
        for ma, message in (('kh-demo-canary', 'MASK_XUNG_DOT_DANH_MUC'),
                            ('MASKCT-0001', 'MASK_MA_JUNSKY'),
                            ('Mã DEMO không hợp lệ', 'MASK_MA_JUNSKY')):
            with self.subTest(ma=ma), self.assertRaises(self.pg.psycopg.errors.InvalidParameterValue) as caught:
                self.goi('duyet_cho', c2[0], ma)
            self.assertEqual(caught.exception.diag.message_primary, message)
            self.assertNotIn('Canary', caught.exception.diag.message_primary)
            self.assertIsNone(caught.exception.diag.message_detail)
        self.assertEqual(self.owner.execute('SELECT count(*) FROM mask.cho_duyet WHERE id IN (%s,%s)',
            (c[0], c2[0])).fetchone()[0], 2)

    def test_tu_choi_giu_cap_tam_mo_che_va_khong_chay_lai_duyet(self):
        c, other = self.cho(), self.cho()
        before = self.owner.execute('SELECT * FROM mask.yeu_cau ORDER BY id').fetchall()
        self.assertEqual(self.goi('tu_choi_cho', c[0]), [(True,)])
        self.assertEqual({r[0] for r in self.owner.execute('SELECT id FROM mask.cho_duyet').fetchall()},
                         {c[0], other[0]})
        self.assertEqual([r[0] for r in self.goi('doc_cho')], [other[0]])
        self.assertEqual([r[0] for r in self.goi('doc_cho', None, 'DANG_XU_LY')], [other[0]])
        self.assertEqual([r[0] for r in self.goi('doc_cho', None, 'CHO_DUYET')], [other[0]])
        refused = self.goi('doc_cho', None, 'DA_TU_CHOI')
        self.assertEqual([(r[0], r[5]) for r in refused], [(c[0], 'DA_TU_CHOI')])
        # Đường tra SQL dùng mở che: tài liệu đang xử lý vẫn tìm được cặp tạm.
        self.assertEqual(self.owner.execute("""SELECT w.bi_danh_tam,w.cum_goc
            FROM mask.cho_duyet w JOIN mask.yeu_cau y ON w.la_demo=y.la_demo
            WHERE y.id=%s AND y.trang_thai='DANG_XU_LY'
                AND w.bi_danh_tam=ANY(y.bi_danh_tam_da_dung)""", (c[2],)).fetchall(), [(c[1], c[3])])
        self.assertEqual(self.owner.execute('SELECT count(*) FROM mask.dinh_danh').fetchone()[0], 0)
        self.assertEqual(self.owner.execute('SELECT * FROM mask.yeu_cau ORDER BY id').fetchall(), before)
        for name in ('duyet_cho', 'tu_choi_cho'):
            with self.subTest(cua=name), self.loi_mask(self.pg.psycopg.errors.InvalidParameterValue, 'MASK_KHONG_THAY'):
                self.goi(name, c[0])

    def test_gap_lai_cum_tu_choi_chi_tang_dem_khong_vao_lai_danh_sach(self):
        c = self.cho(cum='Công ty DEMO Đặng '+uuid4().hex)
        self.goi('tu_choi_cho', c[0])
        for cum in (c[3], unicodedata.normalize('NFD', '  '+c[3].upper()+'  ')):
            with self.subTest(cum=cum):
                inserted = self.owner.execute("""INSERT INTO mask.cho_duyet(cum_goc,nhom,yeu_cau_id,nguon,la_demo)
                    VALUES(%s,'CA_NHAN',%s,'DEMO',true) RETURNING id""", (cum, c[2])).fetchall()
                self.assertEqual(inserted, [])
        self.assertEqual(self.owner.execute('SELECT id,bi_danh_tam,cum_goc,nhom,yeu_cau_id,trang_thai,so_lan_gap '
            'FROM mask.cho_duyet').fetchall(), [(c[0], c[1], c[3], 'CONG_TY', c[2], 'DA_TU_CHOI', 3)])
        self.assertEqual(self.goi('doc_cho'), [])
        self.assertEqual(self.goi('doc_cho', None, 'DA_TU_CHOI')[0][3], 3)
        self.assertEqual(self.owner.execute('SELECT count(*) FROM mask.dinh_danh').fetchone()[0], 0)

    def test_don_dong_tu_choi_sau_khi_dong_het_ma_dung_cap_tam(self):
        c, pending = self.cho(), self.cho(trang_thai='DA_DONG')
        other = self.cho(demo=False, cum=c[3])
        self.owner.execute("UPDATE mask.cho_duyet SET trang_thai='DA_TU_CHOI',bi_danh_tam=%s WHERE id=%s",
                           (c[1], other[0]))
        self.goi('tu_choi_cho', c[0])
        second = self.owner.execute("INSERT INTO mask.yeu_cau(module,nguoi_gui,tai_lieu_id,la_demo,bi_danh_tam_da_dung) "
            "VALUES('demo',%s,%s,true,ARRAY[%s]) RETURNING id", (self.ai, uuid4(), c[1])).fetchone()[0]
        self.assertEqual(self.goi('don_bi_danh_tam'), [(0,)])
        self.dong(c[2])
        self.assertEqual(self.goi('don_bi_danh_tam'), [(0,)])
        self.assertEqual(self.owner.execute('SELECT bi_danh_tam,cum_goc FROM mask.cho_duyet WHERE id=%s',
                                           (c[0],)).fetchone(), (c[1], c[3]))
        self.dong(second)
        before = self.owner.execute('SELECT * FROM mask.yeu_cau ORDER BY id').fetchall()
        self.assertEqual(self.goi('don_bi_danh_tam'), [(1,)])
        self.assertEqual({r[0] for r in self.owner.execute('SELECT id FROM mask.cho_duyet').fetchall()},
                         {pending[0], other[0]})
        self.assertEqual(self.owner.execute('SELECT * FROM mask.yeu_cau ORDER BY id').fetchall(), before)
        self.assertEqual(self.goi('doc_cho', None, 'DA_TU_CHOI'), [])
        self.assertEqual(self.goi('don_bi_danh_tam'), [(0,)])

    def test_don_bo_qua_bat_ky_ma_dang_xu_ly_va_khong_xoa_bi_danh_chinh(self):
        active, closed = self.cho(), self.cho(trang_thai='DA_DONG')
        da = self.goi('duyet_cho', active[0])[0]
        dc = self.goi('duyet_cho', closed[0])[0]
        # Một mã đóng và một mã khác còn mở cùng dùng bí danh active.
        self.owner.execute("INSERT INTO mask.yeu_cau(module,nguoi_gui,tai_lieu_id,la_demo,bi_danh_tam_da_dung) "
            "VALUES('demo',%s,%s,true,ARRAY[%s])", (self.ai, uuid4(), active[1]))
        self.dong(active[2])
        self.assertEqual(self.goi('don_bi_danh_tam'), [(1,)])
        self.assertEqual(self.owner.execute('SELECT bi_danh,bi_danh_tam FROM mask.dinh_danh WHERE id=%s',
            (dc[0],)).fetchone(), (dc[1], None))
        self.assertEqual(self.owner.execute('SELECT bi_danh_tam FROM mask.dinh_danh WHERE id=%s',
            (da[0],)).fetchone()[0], active[1])
        self.owner.execute("UPDATE mask.yeu_cau SET trang_thai='DA_DONG',dong_luc=clock_timestamp() WHERE trang_thai='DANG_XU_LY'")
        self.assertEqual(self.goi('don_bi_danh_tam'), [(1,)])
        self.assertEqual(self.goi('don_bi_danh_tam'), [(0,)])

    def test_keyset_khong_lap_cung_thoi_diem_loc_va_so_lan_gap(self):
        luc = datetime(2026, 11, 6, 17, tzinfo=timezone.utc)  # 00:00 ngày 07/11 VN.
        cs = [self.cho(luc=luc) for _ in range(3)]
        old = self.cho(luc=luc-timedelta(microseconds=1), nhom='CA_NHAN')
        closed = self.cho(luc=luc+timedelta(days=1)-timedelta(microseconds=1), trang_thai='DA_DONG')
        after = self.cho(luc=luc+timedelta(days=1))
        self.owner.execute('UPDATE mask.cho_duyet SET so_lan_gap=7 WHERE id=%s', (cs[0][0],))
        d = luc.astimezone(timezone(timedelta(hours=7))).date()
        rows = self.goi('doc_cho', 'CONG_TY', 'DANG_XU_LY', d, d, None, None, 2)
        tail = self.goi('doc_cho', 'CONG_TY', 'DANG_XU_LY', d, d, rows[-1][4], rows[-1][0], 2)
        self.assertEqual([r[0] for r in rows+tail], sorted(c[0] for c in cs))
        self.assertEqual(next(r[3] for r in rows+tail if r[0] == cs[0][0]), 7)
        self.assertEqual([r[0] for r in self.goi('doc_cho', None, 'DA_DONG', d, d)], [closed[0]])
        all_ids = {r[0] for r in self.goi('doc_cho', None, None, d, d)}
        self.assertFalse({old[0], after[0]} & all_ids)

    def test_bo_loc_sai_bi_tu_choi_khong_cat_ngam(self):
        for args in (('NHOM_SAI',), (None, 'DA_DUYET'), (None, None, None, None, None, None, 0),
                     (None, None, None, None, None, None, 201),
                     (None, None, None, None, None, uuid4())):
            with self.subTest(args=args), self.loi_mask(self.pg.psycopg.errors.InvalidParameterValue, 'MASK_BO_LOC'):
                self.goi('doc_cho', *args)

    def test_demo_tu_phien_ghi_de_guc_gia_khoi_phuc_context(self):
        c = self.cho()
        # Chỉ dữ liệu giả trong CSDL kho_test; không kết nối vùng vận hành thật.
        other = self.cho(demo=False, cum=c[3])
        self.owner.execute("SELECT set_config('ktt.mask_la_demo','false',true)")
        self.assertEqual([r[0] for r in self.goi('doc_cho')], [c[0]])
        self.assertEqual(self.owner.execute("SELECT current_setting('ktt.mask_la_demo')").fetchone()[0], 'false')
        for name in ('duyet_cho', 'tu_choi_cho'):
            with self.subTest(cua=name), self.loi_mask(self.pg.psycopg.errors.InvalidParameterValue, 'MASK_KHONG_THAY'):
                self.goi(name, other[0])
        result = self.goi('duyet_cho', c[0])[0]
        self.assertEqual(self.owner.execute('SELECT la_demo FROM mask.dinh_danh WHERE id=%s',
            (result[0],)).fetchone()[0], True)
        # Bí danh trùng chuỗi giữa hai vùng không được cản việc dọn của nhau.
        self.owner.execute("""INSERT INTO mask.dinh_danh(gia_tri,nhom,nguon,la_demo,bi_danh_tam)
            VALUES(%s,'KHAC','DEMO',false,%s)""", ('DEMO '+uuid4().hex, c[1]))
        self.dong(c[2])
        self.assertEqual(self.goi('don_bi_danh_tam'), [(1,)])
        self.assertEqual(self.owner.execute('SELECT count(*) FROM mask.dinh_danh WHERE NOT la_demo AND bi_danh_tam=%s',
            (c[1],)).fetchone()[0], 1)

    def test_phien_vung_false_khong_doc_duyet_hay_don_vung_demo(self):
        demo = self.cho()
        da = self.goi('duyet_cho', demo[0])[0]
        self.dong(demo[2])
        self.pn = uuid4()
        self.owner.execute("INSERT INTO loi.phap_nhan(id,ma,ten,la_demo) VALUES(%s,%s,'DEMO giả vùng false',false)",
                           (self.pn, self.pn.hex))
        self.owner.execute("INSERT INTO loi.phan_quyen(nguoi_dung_id,phap_nhan_id,module) VALUES(%s,%s,ARRAY['core'])",
                           (self.ai, self.pn))
        self.token = self.cap_phien()
        other = self.cho(demo=False, trang_thai='DA_DONG')
        self.owner.execute("SELECT set_config('ktt.mask_la_demo','true',true)")
        self.assertEqual([r[0] for r in self.goi('doc_cho')], [other[0]])
        self.assertEqual(self.goi('don_bi_danh_tam'), [(0,)])
        db = self.goi('duyet_cho', other[0])[0]
        self.assertEqual(self.goi('don_bi_danh_tam'), [(1,)])
        self.assertEqual(self.owner.execute('SELECT la_demo,bi_danh_tam FROM mask.dinh_danh WHERE id=%s',
                                           (da[0],)).fetchone(), (True, demo[1]))
        self.assertEqual(self.owner.execute('SELECT la_demo,bi_danh_tam FROM mask.dinh_danh WHERE id=%s',
                                           (db[0],)).fetchone(), (False, None))

    def test_audit_moi_cua_chi_id_khong_cum_goc_va_bi_danh(self):
        c, refused = self.cho(cum='Cụm DEMO CANARY kiểm toán'), self.cho()
        self.goi('doc_cho')
        self.goi('duyet_cho', c[0])
        self.goi('tu_choi_cho', refused[0])
        self.dong(c[2])
        self.goi('don_bi_danh_tam')
        rows = self.owner.execute("SELECT * FROM loi.nhat_ky_kiem_toan WHERE phap_nhan_id=%s AND doi_tuong LIKE 'mask.%%'",
                                  (self.pn,)).fetchall()
        self.assertEqual(len(rows), 5)
        self.assertNotIn('CANARY', repr(rows))
        self.assertNotIn(c[1], repr(rows))
        self.assertNotIn(self.token, repr(rows))

    def test_chay_lai_117_khong_doi_du_lieu_oid_acl_policy_hay_so_cap(self):
        c = self.cho()
        self.goi('duyet_cho', c[0])
        self.cho()
        refused = self.cho()
        self.goi('tu_choi_cho', refused[0])
        self.owner.execute("""INSERT INTO mask.cho_duyet(cum_goc,nhom,yeu_cau_id,nguon,la_demo)
            VALUES(%s,'CONG_TY',%s,'DEMO',true)""", (refused[3], refused[2]))

        def chup():
            result = [self.owner.execute('SELECT * FROM mask.'+t+' ORDER BY id').fetchall()
                      for t in ('dinh_danh', 'cho_duyet', 'yeu_cau')]
            result.append(self.owner.execute("""SELECT p.oid,p.proowner,p.proacl,pg_get_functiondef(p.oid)
                FROM pg_proc p WHERE (p.pronamespace='loi'::regnamespace AND p.proname='mask_kiem_admin')
                    OR p.pronamespace='mask'::regnamespace ORDER BY p.oid""").fetchall())
            result.append(self.owner.execute("""SELECT c.oid,c.relname,c.relowner,c.relacl,c.relrowsecurity,c.relforcerowsecurity
                FROM pg_class c WHERE c.relnamespace='mask'::regnamespace ORDER BY c.oid""").fetchall())
            result.append(self.owner.execute("SELECT * FROM pg_policy WHERE polrelid IN ('mask.dinh_danh'::regclass,"
                "'mask.cho_duyet'::regclass,'mask.yeu_cau'::regclass) ORDER BY oid").fetchall())
            result.append(self.owner.execute('SELECT last_value,is_called FROM mask.so_bi_danh').fetchone())
            result.append(self.owner.execute("SELECT * FROM pg_trigger WHERE tgrelid='mask.cho_duyet'::regclass ORDER BY oid").fetchall())
            return result

        before = chup()
        self.owner.execute(doc_sql())
        self.assertEqual(chup(), before)

    def test_guard_tu_choi_tien_to_gia_truoc_khi_doi_quyen(self):
        with self.assertRaises(self.pg.psycopg.errors.RaiseException) as caught, self.owner.transaction():
            self.owner.execute("SELECT set_config('kho_tri_thuc.tien_to_vai','DEMO-sai',true)")
            self.owner.execute(doc_sql())
        self.assertEqual(caught.exception.diag.message_primary, 'MASK_DUYET_SAI_DICH')

    def test_chay_lai_113_khong_mat_quyen_cua_117(self):
        from tests.test_mask_2 import chay_lai_chuoi_mask
        c = self.cho()
        chay_lai_chuoi_mask(self.owner)
        self.assertEqual([r[0] for r in self.goi('doc_cho')], [c[0]])
        self.assertRegex(self.goi('duyet_cho', c[0])[0][1], r'^\[\[MASKCT-[0-9]{4,}\]\]$')
        self.assertFalse(self.owner.execute('SELECT has_function_privilege(%s,%s,\'EXECUTE\')',
            (self.tt+'dang_nhap_loi', 'mask.cap_ma_yeu_cau(text,uuid,uuid,boolean)')).fetchone()[0])
        with self.assertRaises(self.pg.psycopg.errors.InsufficientPrivilege), self.login_core():
            self.owner.execute("SELECT mask.cap_ma_yeu_cau('core',%s,%s,true)", (self.ai, uuid4()))


if __name__ == '__main__':
    unittest.main()
