"""AI-LAT10a: kiểm SQL offline; PG opt-in do lead cấp KHO_PG_DSN_TEST.

Không đọc tệp kết nối, không chạy/dừng PostgreSQL; không DROP CSDL/vai.
Fixture PG tạo kho_test_* riêng, dữ liệu hoàn toàn giả, đọc migration bằng bytes.
"""
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import re
import sqlite3
import unittest
from uuid import uuid4


SQL_PATH = Path(__file__).resolve().parents[1] / 'src/kho_tri_thuc/core/sql/129_ai_chay_thu.sql'
SQL = SQL_PATH.read_bytes().decode('utf-8')
ROOT_SQL = SQL_PATH.parent


class SQLChayThuTests(unittest.TestCase):
    def test_mot_bang_rieng_khong_them_jsonb_hang_viec(self):
        self.assertEqual(re.findall(r'CREATE TABLE\s+([\w.]+)', SQL), ['loi.ai_chay_thu'])
        self.assertNotRegex(SQL, r'ALTER TABLE loi\.hang_viec')
        self.assertIn("'loi.ai_chay_thu',p_id,'2.0.0'", SQL)
        self.assertIn("'CHAY_THU_HOI_AI',1,eid", SQL)
        self.assertIn("eid,'ai.hoi@1','tra_loi_ai.v2'", SQL)

    def test_nguong_unicode_va_ket_qua_kin(self):
        for token in ("length(dau_vao->>'tai_lieu')<=20000", "length(dau_vao->>'cau_hoi')<=2000",
                      "length(ket_qua->>'tra_loi')<=20000", "length(ket_qua->>'model')<=128",
                      "length(ket_qua->>'ly_do_chon')<=255", "ARRAY['thong_diep_viet','ma_ho_tro']"):
            self.assertIn(token, SQL)
        self.assertIn("ket_qua - ARRAY['tra_loi','model','ly_do_chon','loi']='{}'::jsonb", SQL)

    def test_rls_force_acl_va_definer_path_kin(self):
        self.assertIn('ENABLE ROW LEVEL SECURITY', SQL)
        self.assertIn('FORCE ROW LEVEL SECURITY', SQL)
        self.assertIn('x.phap_nhan_id=ai_chay_thu.phap_nhan_id', SQL)
        self.assertIn('REVOKE ALL ON loi.ai_chay_thu FROM PUBLIC', SQL)
        self.assertIn('REVOKE ALL ON FUNCTION %s FROM PUBLIC', SQL)
        for header in re.findall(r'CREATE FUNCTION loi\.ai_chay_thu_.*?AS \$ham\$', SQL, re.S):
            self.assertIn('SECURITY DEFINER SET search_path=pg_catalog,pg_temp', header)

    def test_admin_demo_lease_cas_va_don(self):
        self.assertIn("AND p.loai='NGUOI_DUNG'", SQL)
        self.assertIn('a.thu_hoi_luc IS NULL', SQL)
        self.assertIn('p.id=p_pn AND p.la_demo', SQL)
        self.assertIn("hashtextextended('demo|'||p_pn::text,23)", SQL)
        self.assertEqual(SQL.count('job := loi.viec_giu('), 2)
        self.assertIn('a.trang_thai=p_cu', SQL)
        self.assertIn('DELETE FROM loi.ai_chay_thu a WHERE a.phap_nhan_id=p_pn', SQL)
        self.assertIn("p.id=a.phap_nhan_id AND p.la_demo", SQL)
        self.assertIn("v.trang_thai IN ('CHO','DANG_CHAY')", SQL)
        self.assertIn('p_gioi_han NOT BETWEEN 1 AND 50', SQL)

    def test_va_hai_overload_dung_moc_nen_va_nhan_chi_loai_moi(self):
        original = (ROOT_SQL/'052_viec_core.sql').read_bytes().decode('utf-8')
        anchor = "IF p_loai IS DISTINCT FROM 'XUAT_DU_LIEU' OR p_phien_ban IS DISTINCT FROM 1"
        self.assertEqual(original.count(anchor), 1)
        self.assertIn('integer,integer,integer,uuid,text,text)', SQL)
        self.assertIn('cardinality(string_to_array(nguon,moc))<>2', SQL)
        self.assertNotIn('ai_chay_thu_nhan', SQL)
        self.assertIn("p_capability IS DISTINCT FROM 'ai.hoi@1'", SQL)
        self.assertIn("p_ma_contract IS DISTINCT FROM 'tra_loi_ai.v2'", SQL)

    def test_utf8_khong_icu_case_if_va_khong_sql_ngoai_loi(self):
        self.assertFalse(SQL_PATH.read_bytes().startswith(b'\xef\xbb\xbf'))
        self.assertNotIn('\ufffd', SQL)
        self.assertNotRegex(SQL, r'(?i)\bICU\b|\bCOLLATE\b|\bDROP\b')
        self.assertNotRegex(SQL, r'(?is)\bIF\b(?:(?!THEN).)*\bCASE\b')
        self.assertNotRegex(SQL, r'(?i)(?:FROM|JOIN|UPDATE|REFERENCES)\s+(?:mod_|cong_bo_)')

    def test_ket_qua_va_ket_thuc_chung_ham_va_tran_200_co_khoa(self):
        function = SQL.split('CREATE FUNCTION loi.ai_chay_thu_ghi_ket_qua', 1)[1].split('$ham$;', 1)[0]
        self.assertLess(function.index('UPDATE loi.ai_chay_thu'), function.index('PERFORM loi.viec_ket_thuc'))
        self.assertIn('count(*)::integer-199', SQL)
        self.assertIn('LIMIT can_don', SQL)
        self.assertIn('>=200 THEN', SQL)
        self.assertIn('ai_chay_thu_don(p_ma text,p_nguoi uuid', SQL)

    def test_doc_suy_trang_thai_tu_hang_viec_va_lich_su_dung_cung_cua(self):
        self.assertIn("job.trang_thai NOT IN ('CHO','DANG_CHAY')", SQL)
        self.assertIn('job.giu_den<=clock_timestamp()', SQL)
        self.assertIn('loi.ai_chay_thu_doc(p_ma,p_nguoi,p_pn,s.id)', SQL)

    def test_worker_xuat_giu_bo_loc_null_cua_082(self):
        old = (ROOT_SQL/'082_viec_capability.sql').read_bytes().decode('utf-8')
        self.assertIn('AND capability IS NULL AND ma_contract IS NULL', old)
        self.assertNotIn('loi.viec_nhan(', SQL)
        # Tất cả neo vá nhánh Core đều đúng một dòng trong 052.
        original = (ROOT_SQL/'052_viec_core.sql').read_bytes().decode('utf-8')
        anchors = ["OR p_engine IS NOT NULL",
            "OR p_hd IS DISTINCT FROM 'CORE:DU_LIEU:LAP' OR p_contract IS DISTINCT FROM '1.2'",
            "WHERE module='core' AND loai=p_loai AND phien_ban=p_phien_ban AND engine_id IS NULL"]
        for newline in ('\n', '\r\n'):
            body = original.replace('\r\n', '\n').replace('\n', newline)
            for anchor in anchors:
                self.assertEqual(body.count(anchor), 1)

    def test_loai_tru_xuat_du_lieu_demo_tam_giu_nguyen_danh_sach_cu(self):
        from tests.test_ban_do_xuat import exclusions, missing_maps

        old = exclusions((ROOT_SQL/'090_ban_do_xuat_bang_moi.sql').read_bytes().decode('utf-8'))
        current = exclusions(SQL)
        self.assertEqual(current.pop('loi.ai_chay_thu'),
                         'dữ liệu chạy thử DEMO tạm, có hàm dọn, không thuộc dữ liệu công ty')
        self.assertEqual(current, old)
        self.assertEqual(missing_maps({SQL_PATH.name: SQL}), {})

    def test_neo_nhan_va_binding_lich_su_mot_dong_crlf_lf(self):
        originals = [((ROOT_SQL/'068_ket_qua_engine.sql').read_text(encoding='utf-8'),
                      'AND tao_boi=ai AND hanh_dong=p_hd'),
                     ((ROOT_SQL/'082_viec_capability.sql').read_text(encoding='utf-8'),
                      'AND (engine_id,capability,ma_contract,phien_ban_contract)'),
                     ((ROOT_SQL/'068_ket_qua_engine.sql').read_text(encoding='utf-8'),
                      'phien:=loi.cap_phien(p_ma_moi,ai,p_module,p_pn,session_user::text,pham_vi,den,')]
        for source, anchor in originals:
            self.assertIn("neo := '" + anchor + "';", SQL)
            for newline in ('\n', '\r\n'):
                self.assertEqual(source.replace('\n', newline).count(anchor), 1)

    def test_nhan_chi_mo_rong_dung_loai_ai_giu_cac_bo_loc_cu(self):
        patch = re.search(r"moi := replace\(nguon,neo,\$patch\$(AND \(tao_boi=ai.*?)\$patch\$\);", SQL, re.S)[1]
        conn = sqlite3.connect(':memory:')
        self.addCleanup(conn.close)
        conn.execute('CREATE TABLE hang_viec(module,loai,capability,engine_id,ma_contract,phien_ban_contract,tao_boi,hanh_dong)')
        conn.execute("ATTACH DATABASE ':memory:' AS loi")
        conn.execute('CREATE TABLE loi.engine_dinh_nghia(id,ma)')
        conn.execute("INSERT INTO loi.engine_dinh_nghia VALUES ('ai','e_hoi_ai'),('khac','e_khac')")
        predicate = patch.replace('SELECT FROM', 'SELECT 1 FROM')
        predicate = predicate.replace('tao_boi=ai','tao_boi=:ai')
        for name in ('p_engine', 'p_hd'):
            predicate = re.sub(r'\b' + name + r'\b', ':' + name, predicate)
        base = ['core','CHAY_THU_HOI_AI','ai.hoi@1','ai','tra_loi_ai.v2','2.0.0','admin_a','CORE:DU_LIEU:LAP']
        for index, value in ((None,None),(0,'crm'),(1,'KHAC'),(2,'khac@1'),(3,'khac'),(4,'khac.v1'),(5,'1')):
            with self.subTest(index=index):
                row = base.copy()
                if index is not None:
                    row[index] = value
                conn.execute('DELETE FROM hang_viec')
                conn.execute('INSERT INTO hang_viec VALUES (?,?,?,?,?,?,?,?)', row)
                count = conn.execute('SELECT count(*) FROM hang_viec WHERE true ' + predicate,
                    dict(ai='kenh_b',p_engine='ai',p_hd=base[-1])).fetchone()[0]
                self.assertEqual(count, int(index is None))
                self.assertEqual(conn.execute('SELECT count(*) FROM hang_viec WHERE true ' + predicate,
                    dict(ai='admin_a',p_engine='ai',p_hd=base[-1])).fetchone()[0], 1)

    def test_lease_uy_nhiem_dung_nguoi_tao_khong_noi_cua_xac_minh_chung(self):
        source = (ROOT_SQL/'014_viec.sql').read_text(encoding='utf-8')
        self.assertIn('AND v.tao_boi=p.nguoi_dung_id AND v.the_he=p.the_he',source)
        self.assertIn('IF ai<>v.tao_boi OR p_hd<>v.hanh_dong THEN',source)
        self.assertNotIn("f := 'loi.viec_giu(",SQL)
        self.assertNotIn("f := 'loi.xac_minh_phien(",SQL)
        patch = re.search(r'moi := replace\(moi,neo,\$patch\$(IF v\.module=.*?)\$patch\$\);',SQL,re.S)[1]
        for condition in ("v.module='core'", "v.loai='CHAY_THU_HOI_AI'", 'v.phien_ban=1',
                          "v.capability='ai.hoi@1'", "v.ma_contract='tra_loi_ai.v2'",
                          "v.phien_ban_contract='2.0.0'"):
            self.assertIn(condition,patch)
        self.assertIn('ai := v.tao_boi;',patch)
        self.assertIn("pham_vi := ARRAY['CORE:DU_LIEU:LAP'];",patch)
        self.assertIn('phien:=loi.cap_phien(p_ma_moi,ai,p_module,p_pn,session_user::text,pham_vi,den,',patch)

    def test_chon_cau_hinh_dang_kich_hoat_khong_chon_ban_dang_ky_moi(self):
        statements = re.findall(r'SELECT e\.id INTO eid FROM loi\.engine_dinh_nghia e.*?;',SQL,re.S)
        self.assertEqual(len(statements), 2)
        self.assertEqual(' '.join(statements[0].split()), ' '.join(statements[1].split()))
        statement = statements[0]
        statement = statement.replace(' INTO eid','').replace('SELECT FROM','SELECT 1 FROM')
        statement = statement.replace('jsonb_array_elements','json_each')
        for key in ('ma','dau_vao','dau_ra'):
            statement = statement.replace("c->>'"+key+"'", "json_extract(c.value,'$."+key+"')")
        conn = sqlite3.connect(':memory:')
        self.addCleanup(conn.close)
        conn.executescript("""
            ATTACH DATABASE ':memory:' AS loi;
            CREATE TABLE loi.engine_dinh_nghia(id,ma,nang_luc);
            CREATE TABLE loi.engine_ho_so_chay(id,engine_id,het_hieu_luc_luc);
            CREATE TABLE loi.ho_so_chay_engine(ma_engine,phien_ban_dong,ho_so_mau_id,engine_id);
            INSERT INTO loi.engine_ho_so_chay VALUES ('h1','cu',NULL),('h2','moi',NULL);
            INSERT INTO loi.ho_so_chay_engine VALUES ('e_hoi_ai',1,'h1','cu');
        """)
        capabilities = '[{"ma":"ai.hoi@1","dau_vao":"hoi_ai.v2","dau_ra":"tra_loi_ai.v2"}]'
        conn.executemany("INSERT INTO loi.engine_dinh_nghia VALUES (?,'e_hoi_ai',?)",
            [('cu',capabilities),('moi',capabilities)])
        self.assertEqual(conn.execute(statement).fetchone()[0],'cu')
        conn.execute("INSERT INTO loi.ho_so_chay_engine VALUES ('e_hoi_ai',2,'h2','moi')")
        self.assertEqual(conn.execute(statement).fetchone()[0],'moi')
        conn.execute("UPDATE loi.engine_ho_so_chay SET het_hieu_luc_luc=1 WHERE id='h2'")
        self.assertIsNone(conn.execute(statement).fetchone())

    def test_doc_cai_lai_chi_bao_loi_luot_cho_khong_ghi_csdl(self):
        function = SQL.split('CREATE FUNCTION loi.ai_chay_thu_doc(', 1)[1].split('$ham$;', 1)[0]
        self.assertNotRegex(function, r'(?i)\b(?:INSERT|UPDATE|DELETE|MERGE)\b')
        conditions = [re.search(pattern, function)[1] for pattern in (
            r'IF (luot\.trang_thai=.*?) THEN', r'IF (eid IS NOT NULL.*?) THEN')]
        predicate = '(' + ') AND ('.join(conditions) + ')'
        for variable in ('luot.trang_thai', 'job.trang_thai', 'job.engine_id', 'eid'):
            predicate = predicate.replace(variable, ':' + variable.replace('.', '_'))
        conn = sqlite3.connect(':memory:')
        self.addCleanup(conn.close)
        for luot, job, engine, current, expected in (
                ('dang_cho','CHO','cu','moi',True),
                ('dang_cho','CHO','cu','cu',False),
                ('dang_cho','CHO','cu',None,False),
                ('dang_cho','DANG_CHAY','cu','moi',False),
                ('dang_chay','DANG_CHAY','cu','moi',False),
                ('xong','XONG','cu','moi',False),
                ('loi','LOI','cu','moi',False)):
            with self.subTest(luot=luot, job=job, engine=engine, current=current):
                result = conn.execute('SELECT ' + predicate, dict(luot_trang_thai=luot,
                    job_trang_thai=job, job_engine_id=engine, eid=current)).fetchone()[0]
                self.assertEqual(bool(result), expected)


class DonLuotQuaHanTests(unittest.TestCase):
    """Chạy chính câu DELETE của migration trên dữ liệu RAM, không gọi PG."""

    def kho(self):
        conn = sqlite3.connect(':memory:')
        self.addCleanup(conn.close)
        conn.execute("ATTACH DATABASE ':memory:' AS loi")
        conn.create_function('clock_timestamp', 0, lambda: 1000)
        conn.executescript('''
            CREATE TABLE loi.phap_nhan(id TEXT, la_demo INTEGER);
            INSERT INTO loi.phap_nhan VALUES ('demo',1),('khac',1);
            CREATE TABLE loi.ai_chay_thu(id TEXT,phap_nhan_id TEXT,tao_luc INTEGER,ket_thuc INTEGER);
            CREATE TABLE loi.hang_viec(module TEXT,phap_nhan_id TEXT,loai TEXT,
                tham_chieu_id TEXT,trang_thai TEXT,yeu_cau_dung INTEGER,giu_den INTEGER);
        ''')
        return conn

    def them(self, conn, identity, state, *, pn='demo', deadline=None, stop=False):
        conn.execute('INSERT INTO loi.ai_chay_thu VALUES (?,?,1,NULL)', (identity,pn))
        conn.execute("INSERT INTO loi.hang_viec VALUES ('core',?,'CHAY_THU_HOI_AI',?,?,?,?)",
                     (pn,identity,state,stop,deadline))

    def don(self, conn, function):
        source = SQL.split('CREATE FUNCTION loi.' + function + '(', 1)[1].split('$ham$;', 1)[0]
        statement = re.search(r'DELETE FROM loi\.ai_chay_thu.*?;', source, re.S)[0]
        # SQLite chỉ khác cú pháp alias và tên tham số; giữ nguyên predicate SQL.
        statement = statement.replace('DELETE FROM loi.ai_chay_thu a', 'DELETE FROM loi.ai_chay_thu AS a')
        statement = statement.replace('SELECT FROM', 'SELECT 1 FROM')
        for name in ('p_pn', 'p_cu_hon', 'can_don'):
            statement = re.sub(r'\b' + name + r'\b', ':' + name, statement)
        return conn.execute(statement, dict(p_pn='demo', p_cu_hon=60, can_don=1)).rowcount

    def test_200_luot_cho_chay_con_han_khong_bi_don(self):
        for function in ('ai_chay_thu_xep', 'ai_chay_thu_don'):
            with self.subTest(function=function):
                conn = self.kho()
                for i in range(200):
                    self.them(conn, str(i), 'CHO' if i % 2 else 'DANG_CHAY',
                              deadline=None if i % 2 else 1001)
                self.assertEqual(self.don(conn, function), 0)
                self.assertEqual(conn.execute('SELECT count(*) FROM loi.ai_chay_thu').fetchone()[0], 200)

    def test_loi_het_lease_dung_va_thieu_viec_deu_tu_don_dung_phap_nhan(self):
        for function in ('ai_chay_thu_xep', 'ai_chay_thu_don'):
            for state, deadline, stop in (('LOI',None,False), ('DANG_CHAY',999,False),
                                          ('DANG_CHAY',1000,False), ('CHO',None,True),
                                          ('DANG_CHAY',1001,True), (None,None,False)):
                with self.subTest(function=function, state=state, deadline=deadline, stop=stop):
                    conn = self.kho()
                    self.them(conn, 'dang_cho', 'CHO')
                    self.them(conn, 'dang_chay', 'DANG_CHAY', deadline=1001)
                    self.them(conn, 'can_don', state, deadline=deadline, stop=stop)
                    if state is None:
                        conn.execute("DELETE FROM loi.hang_viec WHERE tham_chieu_id='can_don'")
                    self.them(conn, 'khac_pn', 'LOI', pn='khac')
                    self.assertEqual(self.don(conn, function), 1)
                    self.assertEqual({r[0] for r in conn.execute('SELECT id FROM loi.ai_chay_thu')},
                                     {'dang_cho','dang_chay','khac_pn'})


@unittest.skipUnless(os.environ.get('KHO_PG_DSN_TEST'), 'CHUA_KIEM PG: thiếu KHO_PG_DSN_TEST; lead chạy')
class PGChayThuTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Chỉ import fixture khi lead bật PG. G2-25 giữ DB test, không DROP cleanup.
        from tests import test_g2_25 as fixture
        if fixture.psycopg is None:
            raise unittest.SkipTest('CHUA_KIEM PG: thiếu psycopg')
        cls.psycopg = fixture.psycopg
        fixture.PostgresTests.setUpClass.__func__(cls)
        from psycopg.types.json import Jsonb
        # Registry giữ lịch sử trong CSDL thử riêng: nhập, duyệt rồi đưa vào dùng.
        # Không bỏ trigger, không xóa đăng ký và không bỏ qua xung đột phiên bản.
        for contract in ('hoi_ai.v2', 'tra_loi_ai.v2'):
            cls.owner.execute("""INSERT INTO loi.dang_ky_contract(ma,phien_ban,module_so_huu,lop,muc_dich,
                sieu_du_lieu,luoc_do,ma_bam) VALUES(%s,'2.0.0','core','ky_thuat','DEMO',
                '{}','{}',%s)""", (contract,'b'*64))
            cls.owner.execute("""UPDATE loi.dang_ky_contract SET trang_thai='anh_duyet',
                bang_chung_duyet='DEMO',duyet_luc=clock_timestamp()
                WHERE ma=%s AND phien_ban='2.0.0'""", (contract,))
            cls.owner.execute("""UPDATE loi.dang_ky_contract SET trang_thai='dang_dung'
                WHERE ma=%s AND phien_ban='2.0.0'""", (contract,))
        cls.engine_id, cls.profile_id, cls.port_id, cls.instance_id = (uuid4() for _ in range(4))
        cls.owner.execute("""INSERT INTO loi.engine_dinh_nghia(id,ma,ten,so_phien_ban,ma_bam_goi,
            ma_adapter,phien_ban_adapter,nang_luc,gioi_han) VALUES(%s,'e_hoi_ai','DEMO','0.1.1-demo.1',
            %s,'hoi_ai','2.0.0',%s,'{}')""", (cls.engine_id,'a'*64,Jsonb([
                dict(ma='ai.hoi@1',dau_vao='hoi_ai.v2',dau_ra='tra_loi_ai.v2')])))
        cls.owner.execute("""INSERT INTO loi.engine_ho_so_chay(id,engine_id,may_chu_id,executable,
            doi_so,so_viec_dong_thoi,timeout_giay) VALUES(%s,%s,%s,'DEMO/khong-chay.exe','[]',1,120)""",
            (cls.profile_id,cls.engine_id,uuid4()))
        cls.owner.execute("""INSERT INTO loi.ho_so_chay_schema(engine_id,ma_engine,phien_ban_engine,ho_so_mau_id)
            VALUES(%s,'e_hoi_ai','0.1.1-demo.1',%s)""", (cls.engine_id,cls.profile_id))
        cls.owner.execute("""INSERT INTO loi.so_cong(id,may_chu_id,dia_chi_nghe,cong,engine_ho_so_id,
            giu_boi,the_he,giu_den,trang_thai) VALUES(%s,%s,'127.0.0.1',19001,%s,%s,1,
            now()+interval '1 hour','CON_GIU')""", (cls.port_id,uuid4(),cls.profile_id,cls.instance_id))
        cls.owner.execute("""INSERT INTO loi.engine_phien_chay(id,so_cong_id,engine_ho_so_id,phien_ban_thuc,
            the_he,pid,dinh_danh_lan_tao,nhan_yeu_cau_luc,san_sang_luc)
            VALUES(%s,%s,%s,'0.1.1-demo.1',1,1234,'DEMO',now(),now())""",
            (cls.instance_id,cls.port_id,cls.profile_id))

    def setUp(self):
        from psycopg.types.json import Jsonb
        from kho_tri_thuc.core import phien
        self.Jsonb = Jsonb
        self.core = self.connections['core']
        self.pn, self.other, self.other_demo, self.actor, self.non_admin = (uuid4() for _ in range(5))
        for actor in (self.actor,self.non_admin):
            self.owner.execute("INSERT INTO loi.nguoi_dung(id,dang_nhap,ten,vai_tro) VALUES(%s,%s,'DEMO','CFO')",
                               (actor,actor.hex))
        # Cờ DEMO đặt ngay khi tạo, trước mọi cấu hình MTQ/dữ liệu liên quan.
        for pn, demo in ((self.pn, True), (self.other, False), (self.other_demo, True)):
            self.owner.execute("INSERT INTO loi.phap_nhan(id,ma,ten,la_demo) VALUES(%s,%s,'DEMO',%s)", (pn,pn.hex,demo))
            for actor in (self.actor,self.non_admin):
                self.owner.execute('INSERT INTO loi.phan_quyen(nguoi_dung_id,phap_nhan_id,module) VALUES(%s,%s,%s)',
                                   (actor,pn,['core']))
            phong, version, row = (uuid4() for _ in range(3))
            self.owner.execute("INSERT INTO loi.mtq_phong(id,phap_nhan_id,ma,ten) VALUES(%s,%s,'DEMO','DEMO')", (phong,pn))
            self.owner.execute("INSERT INTO loi.mtq_phien_ban(id,phap_nhan_id,so_phien_ban,tao_boi,ly_do) VALUES(%s,%s,1,%s,'DEMO')",
                               (version,pn,self.actor))
            for role in ('CFO','THUC_HIEN_1','THUC_HIEN_2','TRUONG_PHONG','NGUOI_XEM'):
                self.owner.execute('INSERT INTO loi.mtq_dong(id,phien_ban_id,phap_nhan_id,phong_id,vai) VALUES(%s,%s,%s,%s,%s)',
                                   (row if role=='CFO' else uuid4(),version,pn,phong,role))
            for action in ('LAP','XEM'):
                self.owner.execute("INSERT INTO loi.mtq_o(dong_id,module,man,hanh_dong,cho_phep) VALUES(%s,'CORE','DU_LIEU',%s,true)", (row,action))
            self.owner.execute("UPDATE loi.mtq_phien_ban SET trang_thai='DA_CONG_BO',cong_bo_boi=%s,cong_bo_luc=now(),phien_ban_dong=2 WHERE id=%s",
                               (self.actor,version))
            for actor in (self.actor,self.non_admin):
                assigned = uuid4()
                self.owner.execute("INSERT INTO loi.mtq_gan_vai(id,nguoi_dung_id,phap_nhan_id,phong_id,vai,cap_boi,ly_do) VALUES(%s,%s,%s,%s,'CFO',%s,'DEMO')",
                                   (assigned,actor,pn,phong,self.actor))
                self.owner.execute("INSERT INTO loi.mtq_pham_vi(gan_vai_id,phap_nhan_id,loai,khoa,cap_boi,ly_do) VALUES(%s,%s,'PHAP_NHAN',%s,%s,'DEMO')",
                                   (assigned,pn,str(pn),self.actor))
            self.owner.execute('INSERT INTO loi.mtq_kich_hoat(phap_nhan_id,bat,phien_ban_id,bat_boi,bat_luc) VALUES(%s,true,%s,%s,now())',
                               (pn,version,self.actor))
            self.owner.execute("INSERT INTO loi.module_cong_tac(module,phap_nhan_id,phien_ban_dong,che_do,tao_boi) VALUES('core',%s,1,'VAN_HANH',%s)",
                               (pn,self.actor))
        self.owner.execute("INSERT INTO loi.mtq_admin(nguoi_dung_id,cap_boi,ly_do) VALUES(%s,%s,'DEMO')", (self.actor,self.actor))
        self.tokens = {}
        for pn in (self.pn,self.other,self.other_demo):
            self.tokens[pn] = phien.cap_phien(self.core, nguoi_dung_id=self.actor, module='core', phap_nhan_id=pn,
                dang_nhap_csdl=self.core.info.user, pham_vi_hanh_dong=['CORE:ENGINE:CAU_HINH','CORE:DU_LIEU:LAP','CORE:DU_LIEU:XEM'],
                hieu_luc_den=datetime.now(timezone.utc)+timedelta(minutes=5)).ma
        # Chỉ actor có Admin; người còn lại có cùng quyền nghiệp vụ và phiên hợp lệ.
        self.non_admin_token = phien.cap_phien(self.core, nguoi_dung_id=self.non_admin,
            module='core', phap_nhan_id=self.pn, dang_nhap_csdl=self.core.info.user,
            pham_vi_hanh_dong=['CORE:ENGINE:CAU_HINH','CORE:DU_LIEU:LAP','CORE:DU_LIEU:XEM'],
            hieu_luc_den=datetime.now(timezone.utc)+timedelta(minutes=5)).ma
        self.data = dict(tai_lieu='Hợp đồng DEMO 1.000.000 đồng.', cau_hoi='Số tiền?',
            phien_ban_module='1.0.0', ma_bam_goi='a'*64, ma_prompt='thanh_toan', phien_ban_prompt='1')
        self.kich_hoat(self.engine_id, self.profile_id)

    def kich_hoat(self, engine_id, profile_id):
        self.owner.execute("""INSERT INTO loi.ho_so_chay_engine(ma_engine,phien_ban_dong,ho_so_mau_id,
            cho_khoi_dong_giay,ranh_toi_da_giay,che_do_chay,engine_id)
            SELECT 'e_hoi_ai',coalesce(max(h.phien_ban_dong),0)+1,%s,120,300,'tu_kich_hoat_tu_dong',%s
            FROM loi.ho_so_chay_engine h WHERE h.ma_engine='e_hoi_ai'""", (profile_id,engine_id))

    def engine_moi(self):
        eid, hid = uuid4(), uuid4()
        version = '0.1.1-demo.' + eid.hex
        self.owner.execute("""INSERT INTO loi.engine_dinh_nghia(id,ma,ten,so_phien_ban,ma_bam_goi,
            ma_adapter,phien_ban_adapter,nang_luc,gioi_han)
            SELECT %s,ma,ten,%s,ma_bam_goi,ma_adapter,phien_ban_adapter,nang_luc,gioi_han
            FROM loi.engine_dinh_nghia WHERE id=%s""", (eid,version,self.engine_id))
        self.owner.execute("""INSERT INTO loi.engine_ho_so_chay(id,engine_id,may_chu_id,executable,
            doi_so,so_viec_dong_thoi,timeout_giay) VALUES(%s,%s,%s,'DEMO/khong-chay.exe','[]',1,120)""",
            (hid,eid,uuid4()))
        self.owner.execute("""INSERT INTO loi.ho_so_chay_schema(engine_id,ma_engine,phien_ban_engine,ho_so_mau_id)
            VALUES(%s,'e_hoi_ai',%s,%s)""", (eid,version,hid))
        return eid, hid

    def xep(self, *, pn=None, identity=None, data=None, actor=None, ma=None):
        pn, identity = pn or self.pn, identity or uuid4()
        with self.core.transaction():
            return self.core.execute('SELECT loi.ai_chay_thu_xep(%s,%s,%s,%s,%s,%s,%s)',
                ((ma or self.tokens[pn]).lay_de_truyen(),actor or self.actor,pn,identity,
                 'mau_demo','thanh_toan',self.Jsonb(data or self.data))).fetchone()[0]

    def nhan(self, *, ma=None, instance=None, engine_id=None):
        from kho_tri_thuc.core import viec
        with self.core.transaction():
            return viec.nhan_engine(self.core,instance or self.instance_id,ma=ma or self.tokens[self.pn],
                module='core',phap_nhan_id=self.pn,hanh_dong='CORE:DU_LIEU:LAP',
                ghim_loai_viec=viec.GhimLoaiViec('core','CHAY_THU_HOI_AI',1,'ai.hoi@1',
                    engine_id or self.engine_id,'tra_loi_ai.v2','2.0.0'))

    def test_kenh_khac_admin_tao_nhan_ai_nhung_khong_nhan_loai_khac(self):
        from kho_tri_thuc.core import phien
        identity = self.xep()
        actor_b, assigned = uuid4(), uuid4()
        self.owner.execute("INSERT INTO loi.nguoi_dung(id,dang_nhap,ten,vai_tro) VALUES(%s,%s,'DEMO','CFO')",
            (actor_b,actor_b.hex))
        self.owner.execute("INSERT INTO loi.phan_quyen(nguoi_dung_id,phap_nhan_id,module) VALUES(%s,%s,ARRAY['core'])",
            (actor_b,self.pn))
        self.owner.execute("""INSERT INTO loi.mtq_gan_vai(id,nguoi_dung_id,phap_nhan_id,phong_id,vai,cap_boi,ly_do)
            SELECT %s,%s,phap_nhan_id,phong_id,vai,%s,'DEMO' FROM loi.mtq_gan_vai
            WHERE nguoi_dung_id=%s AND phap_nhan_id=%s""", (assigned,actor_b,self.actor,self.actor,self.pn))
        self.owner.execute("""INSERT INTO loi.mtq_pham_vi(gan_vai_id,phap_nhan_id,loai,khoa,cap_boi,ly_do)
            VALUES(%s,%s,'PHAP_NHAN',%s,%s,'DEMO')""", (assigned,self.pn,str(self.pn),self.actor))
        token = phien.cap_phien(self.core,nguoi_dung_id=actor_b,module='core',phap_nhan_id=self.pn,
            dang_nhap_csdl=self.core.info.user,pham_vi_hanh_dong=['CORE:DU_LIEU:LAP'],
            hieu_luc_den=datetime.now(timezone.utc)+timedelta(minutes=5)).ma
        lease = self.nhan(ma=token)
        self.assertEqual(self.owner.execute("SELECT nguoi_dung_id FROM loi.phien_xac_thuc "
            "WHERE ma_bam=sha256(convert_to(%s,'UTF8'))",(lease.ma.lay_de_truyen(),)).fetchone()[0],self.actor)
        self.assertEqual(self.dau_vao(lease)['id'],str(identity))
        self.assertTrue(self.ket_qua(lease))
        self.assertEqual(self.owner.execute('SELECT tao_boi FROM loi.hang_viec WHERE id=%s',
            (lease.viec_id,)).fetchone()[0],self.actor)
        other = uuid4()
        self.owner.execute("INSERT INTO loi.dang_ky_loai_viec(module,loai,phien_ban,engine_id) VALUES('core',%s,1,%s)",
            ('KHAC_'+other.hex.upper(),self.engine_id))
        # Bản sao giả tối thiểu của một loại khác, vẫn giữ người tạo Admin A.
        self.owner.execute("""INSERT INTO loi.hang_viec(phap_nhan_id,module,loai,phien_ban,engine_id,capability,
            ma_contract,phien_ban_contract,khoa_chong_trung,bang_tham_chieu,tham_chieu_id,hanh_dong,
            pham_vi_hanh_dong,co_tac_dong_ngoai,thu_lai_an_toan,toi_da_lan_thu,thu_lai_giay,tao_boi)
            SELECT phap_nhan_id,module,%s,phien_ban,engine_id,capability,ma_contract,phien_ban_contract,
                %s,bang_tham_chieu,tham_chieu_id,hanh_dong,pham_vi_hanh_dong,co_tac_dong_ngoai,
                thu_lai_an_toan,toi_da_lan_thu,thu_lai_giay,tao_boi FROM loi.hang_viec WHERE id=%s""",
            ('KHAC_'+other.hex.upper(),other.hex,lease.viec_id))
        self.assertIsNone(self.core.execute("""SELECT loi.nhan_viec_engine(%s,'core',%s,'CORE:DU_LIEU:LAP',
            %s,%s,120,%s,1,'ai.hoi@1',%s,'tra_loi_ai.v2','2.0.0')""",
            (token.lay_de_truyen(),self.pn,self.instance_id,'x'*43,'KHAC_'+other.hex.upper(),self.engine_id)).fetchone()[0])

    def test_instance_khac_engine_hoac_da_dung_khong_nhan(self):
        from kho_tri_thuc.core import viec
        self.xep()
        eid, hid = self.engine_moi()
        instance, port = uuid4(), uuid4()
        self.owner.execute("""INSERT INTO loi.so_cong(id,may_chu_id,dia_chi_nghe,cong,engine_ho_so_id,
            giu_boi,the_he,giu_den,trang_thai) VALUES(%s,%s,'127.0.0.1',19002,%s,%s,1,
            now()+interval '1 hour','CON_GIU')""", (port,uuid4(),hid,instance))
        self.owner.execute("""INSERT INTO loi.engine_phien_chay(id,so_cong_id,engine_ho_so_id,phien_ban_thuc,
            the_he,pid,dinh_danh_lan_tao,nhan_yeu_cau_luc,san_sang_luc)
            SELECT %s,%s,%s,so_phien_ban,1,1235,'DEMO',now(),now() FROM loi.engine_dinh_nghia WHERE id=%s""",
            (instance,port,hid,eid))
        with self.assertRaises(viec.LoiViec):
            self.nhan(instance=instance)
        self.assertIsNotNone(self.nhan())
        self.kich_hoat(eid,hid)
        identity = self.xep()
        self.owner.execute('UPDATE loi.engine_phien_chay SET ket_thuc_luc=now() WHERE id=%s',(instance,))
        with self.assertRaises(viec.LoiViec):
            self.nhan(instance=instance,engine_id=eid)
        self.assertEqual(self.owner.execute('SELECT trang_thai FROM loi.hang_viec WHERE tham_chieu_id=%s',
            (identity,)).fetchone()[0],'CHO')

    def test_cai_lai_doi_binding_va_loi_luot_cho_giu_nguyen_lease(self):
        other_type = 'KHAC_'+uuid4().hex.upper()
        self.owner.execute("INSERT INTO loi.dang_ky_loai_viec(module,loai,phien_ban,engine_id) VALUES('core',%s,1,%s)",
            (other_type,self.engine_id))
        running = self.xep()
        lease = self.nhan()
        self.dau_vao(lease)
        queued = self.xep()
        # Có thêm bản đăng ký nhưng chưa kích hoạt: vẫn xếp vào engine hiện hành.
        eid, hid = self.engine_moi()
        untouched = self.xep()
        self.assertEqual(self.owner.execute('SELECT engine_id FROM loi.hang_viec WHERE tham_chieu_id=%s',
            (untouched,)).fetchone()[0],self.engine_id)
        self.assertEqual(self.doc(queued)['trang_thai'],'dang_cho')
        self.kich_hoat(eid,hid)
        # Đọc ngay sau cài lại, chưa có lượt xếp mới để đổi đăng ký loại việc.
        self.assertEqual(self.owner.execute("SELECT engine_id FROM loi.dang_ky_loai_viec WHERE module='core' AND loai='CHAY_THU_HOI_AI' AND phien_ban=1").fetchone()[0],self.engine_id)
        history = self.core.execute('SELECT loi.ai_chay_thu_lich_su(%s,%s,%s,50)',
            (self.tokens[self.pn].lay_de_truyen(),self.actor,self.pn)).fetchone()[0]
        history = {row['id']:row for row in history}
        for identity in (queued,untouched):
            for result in (self.doc(identity),history[str(identity)]):
                self.assertEqual(result['trang_thai'],'loi')
                self.assertEqual(result['ket_qua']['loi']['thong_diep_viet'],
                    'Engine Hỏi AI vừa được cài lại, cần gửi lượt mới')
                self.assertEqual(result['ket_qua']['loi']['ma_ho_tro'],'AI_THU_ENGINE_CAI_LAI')
            self.assertEqual(self.owner.execute("SELECT a.trang_thai,a.ket_qua,a.bat_dau,a.ket_thuc,v.trang_thai "
                "FROM loi.ai_chay_thu a JOIN loi.hang_viec v ON v.tham_chieu_id=a.id "
                "WHERE a.id=%s",(identity,)).fetchone(),('dang_cho',None,None,None,'CHO'))
        self.assertEqual(self.doc(running)['trang_thai'],'dang_chay')
        fresh = self.xep()
        self.assertEqual(self.owner.execute("SELECT engine_id FROM loi.dang_ky_loai_viec WHERE module='core' AND loai='CHAY_THU_HOI_AI' AND phien_ban=1").fetchone()[0],eid)
        self.assertEqual(self.owner.execute('SELECT engine_id FROM loi.hang_viec WHERE tham_chieu_id=%s',
            (fresh,)).fetchone()[0],eid)
        self.assertEqual(self.owner.execute("SELECT engine_id FROM loi.dang_ky_loai_viec WHERE module='core' AND loai=%s",
            (other_type,)).fetchone()[0],self.engine_id)
        for identity in (queued,untouched):
            result = self.doc(identity)
            self.assertEqual(result['trang_thai'],'loi')
            self.assertEqual(result['ket_qua']['loi']['thong_diep_viet'],
                'Engine Hỏi AI vừa được cài lại, cần gửi lượt mới')
        self.assertEqual(self.doc(running)['trang_thai'],'dang_chay')
        self.assertTrue(self.ket_qua(lease))

    def test_cai_lai_khong_dong_lease_chua_doc_va_khong_du_phong_ban_cu(self):
        identity = self.xep()
        lease = self.nhan()
        eid, hid = self.engine_moi()
        self.kich_hoat(eid,hid)
        self.assertEqual(self.doc(identity)['trang_thai'],'dang_cho')
        self.xep()
        self.assertEqual(self.owner.execute('SELECT trang_thai FROM loi.ai_chay_thu WHERE id=%s',
            (identity,)).fetchone()[0],'dang_cho')
        self.assertEqual(self.owner.execute('SELECT trang_thai FROM loi.hang_viec WHERE id=%s',
            (lease.viec_id,)).fetchone()[0],'DANG_CHAY')
        self.owner.execute('UPDATE loi.engine_ho_so_chay SET het_hieu_luc_luc=now() WHERE id=%s',(hid,))
        with self.assertRaises(self.psycopg.Error) as caught:
            self.xep()
        self.assertEqual(caught.exception.diag.message_primary,'AI_THU_CHUA_SAN_SANG')

    def ket_qua(self, lease, *, state='xong', result=None):
        args = (lease.ma.lay_de_truyen(),self.pn,lease.viec_id,lease.instance_id,lease.the_he)
        result = result or dict(tra_loi='1.000.000 đồng',model='local-DEMO',ly_do_chon='Mô hình ưu tiên',loi=None)
        with self.core.transaction():
            return self.core.execute('SELECT loi.ai_chay_thu_ghi_ket_qua(%s,%s,%s,%s,%s,%s,%s,%s)',
                (*args,'dang_chay',state,self.Jsonb(result))).fetchone()[0]

    def test_admin_xep_mot_dong_mot_viec_replay_va_khac_noi_dung_cas(self):
        identity = self.xep()
        self.assertEqual(self.xep(identity=identity),identity)
        row = self.owner.execute("SELECT tham_chieu_id,bang_tham_chieu FROM loi.hang_viec WHERE phap_nhan_id=%s AND loai='CHAY_THU_HOI_AI'", (self.pn,)).fetchall()
        self.assertEqual(row,[(identity,'loi.ai_chay_thu')])
        with self.assertRaises(self.psycopg.errors.UniqueViolation):
            self.xep(identity=identity,data={**self.data,'cau_hoi':'Câu hỏi khác'})

    def test_khong_admin_bi_tu_choi(self):
        with self.assertRaises(self.psycopg.errors.InsufficientPrivilege) as caught:
            self.xep(actor=self.non_admin,ma=self.non_admin_token)
        self.assertEqual(caught.exception.diag.message_primary,'AI_THU_ADMIN')

    def test_phap_nhan_khong_demo_bi_tu_choi(self):
        with self.assertRaises(self.psycopg.errors.InsufficientPrivilege) as caught:
            self.xep(pn=self.other)
        self.assertEqual(caught.exception.diag.message_primary,'AI_THU_DEMO')

    def test_tran_ky_tu_unicode_kieu_va_truong_la(self):
        self.xep(data={**self.data,'tai_lieu':'ệ'*20000,'cau_hoi':'ồ'*2000})
        for change in ({'tai_lieu':'x'*20001},{'cau_hoi':'x'*2001},{'cau_hoi':None},{'tai_lieu':5},{'truong_la':'x'}):
            with self.subTest(change=list(change)), self.assertRaises(self.psycopg.errors.CheckViolation):
                self.xep(data={**self.data,**change})

    def test_lease_that_cas_ghi_ket_qua_khong_ghi_lan_hai_hoac_lease_gia(self):
        identity = self.xep()
        lease = self.nhan()
        args = (lease.ma.lay_de_truyen(),self.pn,lease.viec_id,lease.instance_id,lease.the_he)
        with self.core.transaction():
            row = self.core.execute('SELECT loi.ai_chay_thu_dau_vao(%s,%s,%s,%s,%s)',args).fetchone()[0]
        self.assertEqual(row['id'],str(identity))
        from dataclasses import replace
        with self.assertRaises(self.psycopg.Error):
            self.ket_qua(replace(lease,the_he=lease.the_he+1))
        self.assertTrue(self.ket_qua(lease))
        with self.assertRaises(self.psycopg.Error) as caught:
            self.ket_qua(lease)
        self.assertEqual(caught.exception.diag.message_primary,'VIEC_MAT_LEASE')

    def test_tran_ket_qua_va_ghi_truoc_dau_vao_bi_chan(self):
        self.xep()
        lease = self.nhan()
        with self.assertRaises(self.psycopg.Error) as caught:
            self.ket_qua(lease)
        self.assertEqual(caught.exception.diag.message_primary,'AI_THU_CAS')
        with self.core.transaction():
            self.core.execute('SELECT loi.ai_chay_thu_dau_vao(%s,%s,%s,%s,%s)',
                (lease.ma.lay_de_truyen(),self.pn,lease.viec_id,lease.instance_id,lease.the_he))
        for change in ({'tra_loi':'x'*20001},{'model':'x'*129},{'ly_do_chon':'x'*256},
                       {'loi':{'thong_diep_viet':'x'*501,'ma_ho_tro':'DEMO'}}):
            result = dict(tra_loi='DEMO',model='local-DEMO',ly_do_chon='',loi=None)
            result.update(change)
            with self.subTest(change=list(change)), self.assertRaises(self.psycopg.errors.CheckViolation):
                self.ket_qua(lease,state='loi' if result['loi'] else 'xong',result=result)

    def test_doc_dung_phap_nhan_lich_su_tran_50_va_rls_acl(self):
        identity = self.xep()
        args = (self.tokens[self.pn].lay_de_truyen(),self.actor,self.pn)
        self.assertEqual(self.core.execute('SELECT loi.ai_chay_thu_doc(%s,%s,%s,%s)',(*args,identity)).fetchone()[0]['id'],str(identity))
        self.assertIsNone(self.core.execute('SELECT loi.ai_chay_thu_doc(%s,%s,%s,%s)',(*args,uuid4())).fetchone()[0])
        for limit in (0,51):
            with self.assertRaises(self.psycopg.errors.InvalidParameterValue):
                self.core.execute('SELECT loi.ai_chay_thu_lich_su(%s,%s,%s,%s)',(*args,limit))
        with self.assertRaises(self.psycopg.errors.InsufficientPrivilege):
            self.core.execute('SELECT * FROM loi.ai_chay_thu')
        self.assertEqual(self.owner.execute("SELECT relrowsecurity,relforcerowsecurity FROM pg_class WHERE oid='loi.ai_chay_thu'::regclass").fetchone(),(True,True))

    def test_don_chi_demo_giu_viec_dang_chay_va_replay_sau_don(self):
        identity = self.xep()
        self.owner.execute("UPDATE loi.ai_chay_thu SET tao_luc=now()-interval '2 days' WHERE id=%s",(identity,))
        self.assertEqual(self.core.execute("SELECT loi.ai_chay_thu_don(%s,%s,%s,interval '1 day')",
            (self.tokens[self.pn].lay_de_truyen(),self.actor,self.pn)).fetchone()[0],0)
        with self.assertRaises(self.psycopg.errors.InsufficientPrivilege):
            self.core.execute("SELECT loi.ai_chay_thu_don(%s,%s,%s,interval '1 day')",
                (self.tokens[self.other].lay_de_truyen(),self.actor,self.other))
        lease = self.nhan()
        with self.core.transaction():
            self.core.execute('SELECT loi.ai_chay_thu_dau_vao(%s,%s,%s,%s,%s)',
                (lease.ma.lay_de_truyen(),self.pn,lease.viec_id,lease.instance_id,lease.the_he))
        self.ket_qua(lease)
        self.owner.execute("UPDATE loi.ai_chay_thu SET ket_thuc=now()-interval '2 days' WHERE id=%s",(identity,))
        self.assertEqual(self.core.execute("SELECT loi.ai_chay_thu_don(%s,%s,%s,interval '1 day')",
            (self.tokens[self.pn].lay_de_truyen(),self.actor,self.pn)).fetchone()[0],1)
        with self.assertRaises(self.psycopg.errors.UniqueViolation):
            self.xep(identity=identity)

    def doc(self, identity, pn=None):
        pn = pn or self.pn
        return self.core.execute('SELECT loi.ai_chay_thu_doc(%s,%s,%s,%s)',
            (self.tokens[pn].lay_de_truyen(),self.actor,pn,identity)).fetchone()[0]

    def dau_vao(self, lease):
        return self.core.execute('SELECT loi.ai_chay_thu_dau_vao(%s,%s,%s,%s,%s)',
            (lease.ma.lay_de_truyen(),self.pn,lease.viec_id,lease.instance_id,lease.the_he)).fetchone()[0]

    def test_worker_xuat_khong_nhan_viec_ai_binding_nhan_dung_engine(self):
        identity = self.xep()
        with self.core.transaction():
            # Cửa SQL Core; facade viec.nhan công khai chỉ dành cho module.
            self.assertIsNone(self.core.execute("SELECT loi.viec_nhan(%s,'core',%s,'CORE:DU_LIEU:LAP',%s,%s,%s,120)",
                (self.tokens[self.pn].lay_de_truyen(),self.pn,uuid4(),'x'*43,self.core.info.user)).fetchone()[0])
        lease = self.nhan()
        self.assertIsNotNone(lease)
        delegated = self.owner.execute("SELECT nguoi_dung_id,loai,pham_vi_hanh_dong FROM loi.phien_xac_thuc "
            "WHERE ma_bam=sha256(convert_to(%s,'UTF8'))",(lease.ma.lay_de_truyen(),)).fetchone()
        self.assertEqual(delegated,(self.actor,'UY_NHIEM_VIEC',['CORE:DU_LIEU:LAP']))
        for action in ('CORE:DU_LIEU:XEM','CORE:ENGINE:CAU_HINH'):
            self.assertIsNone(self.core.execute("SELECT * FROM loi.xac_minh_phien(%s,'core',%s,%s,%s,%s)",
                (lease.ma.lay_de_truyen(),self.pn,action,lease.viec_id,lease.the_he)).fetchone())
        self.assertEqual(self.dau_vao(lease)['id'],str(identity))
        row = self.owner.execute('SELECT engine_id,capability,ma_contract,phien_ban_contract FROM loi.hang_viec WHERE id=%s',
            (lease.viec_id,)).fetchone()
        self.assertEqual(row,(self.engine_id,'ai.hoi@1','tra_loi_ai.v2','2.0.0'))

    def test_ket_qua_va_hang_viec_commit_rollback_cung_nhau(self):
        identity = self.xep()
        lease = self.nhan()
        self.dau_vao(lease)
        with self.assertRaisesRegex(RuntimeError,'DEMO_ROLLBACK'):
            with self.core.transaction():
                self.ket_qua(lease)
                raise RuntimeError('DEMO_ROLLBACK')
        self.assertEqual(self.doc(identity)['trang_thai'],'dang_chay')
        self.assertEqual(self.owner.execute('SELECT trang_thai FROM loi.hang_viec WHERE id=%s',
            (lease.viec_id,)).fetchone()[0],'DANG_CHAY')
        self.ket_qua(lease)
        self.assertEqual(self.doc(identity)['trang_thai'],'xong')
        self.assertEqual(self.owner.execute('SELECT trang_thai,ket_qua_id FROM loi.hang_viec WHERE id=%s',
            (lease.viec_id,)).fetchone(),('XONG',identity))

    def test_lease_gia_han_dung_nhip_mat_lease_khong_ghi(self):
        from kho_tri_thuc.core import viec
        identity = self.xep()
        lease = self.nhan()
        self.dau_vao(lease)
        with self.core.transaction():
            renewed = viec.gia_han(self.core,lease,lease_giay=180)
        self.assertGreater(renewed.giu_den,lease.giu_den)
        self.owner.execute("UPDATE loi.hang_viec SET giu_den=now()-interval '1 second' WHERE id=%s",(lease.viec_id,))
        with self.assertRaises(self.psycopg.Error):
            self.ket_qua(lease)
        self.assertIsNone(self.owner.execute('SELECT ket_qua FROM loi.ai_chay_thu WHERE id=%s',(identity,)).fetchone()[0])
        self.assertEqual(self.doc(identity)['trang_thai'],'loi')
        self.assertEqual(self.doc(identity)['ket_qua']['loi']['ma_ho_tro'],'AI_THU_GIAN_DOAN')
        self.assertIsNotNone(self.xep())

    def test_huy_va_loi_hang_viec_suy_ra_loi_khong_treo_lich_su(self):
        for state in ('LOI','DA_DUNG','GIAN_DOAN'):
            identity = self.xep()
            stamp = datetime.now(timezone.utc) if state in ('LOI','DA_DUNG') else None
            self.owner.execute("UPDATE loi.hang_viec SET trang_thai=%s,ket_thuc_luc=%s,ma_loi='DEMO_LOI' WHERE tham_chieu_id=%s",
                               (state,stamp,identity))
            self.assertEqual(self.doc(identity)['trang_thai'],'loi')
        rows = self.core.execute('SELECT loi.ai_chay_thu_lich_su(%s,%s,%s,50)',
            (self.tokens[self.pn].lay_de_truyen(),self.actor,self.pn)).fetchone()[0]
        self.assertTrue(all(row['trang_thai']=='loi' for row in rows))

    def test_don_bat_buoc_admin_va_phien_nguoi_dung(self):
        self.xep()
        with self.assertRaises(self.psycopg.errors.InsufficientPrivilege) as caught:
            self.core.execute("SELECT loi.ai_chay_thu_don(%s,%s,%s,interval '1 day')",
                (self.non_admin_token.lay_de_truyen(),self.non_admin,self.pn))
        self.assertEqual(caught.exception.diag.message_primary,'AI_THU_ADMIN')
        lease = self.nhan()
        with self.assertRaises(self.psycopg.errors.InsufficientPrivilege) as caught:
            self.core.execute("SELECT loi.ai_chay_thu_don(%s,%s,%s,interval '1 day')",
                (lease.ma.lay_de_truyen(),self.actor,self.pn))
        self.assertEqual(caught.exception.diag.message_primary,'AI_THU_PHIEN')

    def test_tran_200_tu_don_cu_nhat_giu_dang_cho(self):
        identities = [self.xep() for _ in range(200)]
        self.assertEqual(self.owner.execute('SELECT count(*) FROM loi.ai_chay_thu WHERE phap_nhan_id=%s',(self.pn,)).fetchone()[0],200)
        with self.assertRaises(self.psycopg.Error) as caught:
            self.xep()
        self.assertEqual(caught.exception.diag.message_primary,'AI_THU_GIOI_HAN')
        oldest = identities[0]
        self.owner.execute("UPDATE loi.hang_viec SET trang_thai='LOI',ket_thuc_luc=now(),ma_loi='DEMO_LOI' WHERE tham_chieu_id=%s",(oldest,))
        self.xep()
        self.assertIsNone(self.doc(oldest))
        self.assertIsNotNone(self.doc(identities[-1]))
        self.assertEqual(self.owner.execute('SELECT count(*) FROM loi.ai_chay_thu WHERE phap_nhan_id=%s',(self.pn,)).fetchone()[0],200)
        lease = self.nhan()
        expired = self.dau_vao(lease)['id']
        self.owner.execute("UPDATE loi.hang_viec SET giu_den=now()-interval '1 second' WHERE id=%s",
                           (lease.viec_id,))
        self.assertEqual(self.doc(expired)['trang_thai'], 'loi')
        self.xep()
        self.assertIsNone(self.doc(expired))
        self.assertEqual(self.owner.execute('SELECT count(*) FROM loi.ai_chay_thu WHERE phap_nhan_id=%s',
                                           (self.pn,)).fetchone()[0],200)

    def test_khac_phap_nhan_khong_doc_duoc_va_core_16_khong_bo_capability(self):
        identity = self.xep()
        # Pháp nhân DEMO thứ hai có sẵn phiên hợp lệ để kiểm đúng cách ly dữ liệu.
        self.assertIsNone(self.doc(identity,self.other_demo))
        self.assertEqual(self.core.execute('SELECT loi.ai_chay_thu_lich_su(%s,%s,%s,50)',
            (self.tokens[self.other_demo].lay_de_truyen(),self.actor,self.other_demo)).fetchone()[0],[])
        with self.assertRaises(self.psycopg.errors.InsufficientPrivilege):
            self.core.execute("SELECT loi.viec_tao(%s,'core',%s,'CORE:DU_LIEU:LAP','CHAY_THU_HOI_AI',1,%s,'loi.ai_chay_thu',%s,'1.2',false,true,3,60,1,NULL)",
                (self.tokens[self.pn].lay_de_truyen(),self.pn,uuid4().hex,identity))
        with self.assertRaises(self.psycopg.errors.InsufficientPrivilege):
            self.core.execute("SELECT loi.viec_tao(%s,'core',%s,'CORE:DU_LIEU:LAP','CHAY_THU_HOI_AI',1,%s,'loi.ai_chay_thu',%s,'2.0.0',false,true,3,60,1,%s,'demo.sai@1','tra_loi_ai.v2')",
                (self.tokens[self.pn].lay_de_truyen(),self.pn,uuid4().hex,identity,self.engine_id))


if __name__ == '__main__':
    unittest.main()
