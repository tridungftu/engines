"""LHD-C1 vòng 2 (QD-TAM-20261106-07): kiểm thuần SQL; PG chỉ lead opt-in KHO_PG_DSN_TEST.

Loại hợp đồng, phiên bản danh mục, con trỏ "Đang dùng" là dòng của
loi.engine_tep_cau_hinh. Không khởi động/dừng dịch vụ. Fixture PG dùng CSDL
kho_test_* riêng như G2-25 (áp đủ chuỗi 001→108), chỉ tạo metadata DEMO,
không mở Excel hoặc gọi engine/AI.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import unicodedata
import unittest
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = ROOT / 'src/kho_tri_thuc/core/sql/108_danh_muc_trich.sql'
RAW = SQL_PATH.read_bytes()
SQL = RAW.decode('utf-8')
XD = '05846a2acd60f2cde708d13a163a137ee3fb0b4e08fd84f85a7e14e7ef861bcd'
XD_ND = '6b8190a73e73ced8784fb22e3339a42d72785826ae15b1a499955facb4d65812'
XD_TOM_TAT = dict(so_tham_so=37, so_dang_dung=37, so_muc_3=10, so_luon_hoi=5, co_quy_tac=False)
XLSX_XD = ROOT / 'src/kho_tri_thuc/m4/review_goc/trich_xuat/DANH_MUC_THAM_SO.xlsx'
SUMMARY = dict(so_tham_so=30, so_dang_dung=28, so_muc_3=3,
               so_luon_hoi=2, co_quy_tac=False)
HEADERS = re.compile(
    r'CREATE OR REPLACE FUNCTION loi\.(\w+)\((.*?)\)\s*'
    r'RETURNS (.*?) AS \$ham\$(.*?)\$ham\$;', re.S)
FUNCTIONS = {m[1]: m for m in HEADERS.finditer(SQL)}
CUA = ('loai', 'ghi', 'kich_hoat', 'doc')


def _bo_chu_thich(text):
    return re.sub(r'--[^\n]*', '', text)


def _ma_tra_ve():
    """Mọi mã nghiệp vụ LHD_* mà các cửa có thể trả trong jsonb."""
    found = set(re.findall(r"ma:='(LHD_\w+)'", SQL))
    found |= set(re.findall(r"jsonb_build_object\('ma','(LHD_\w+)'", SQL))
    return found


class MigrationTinhTests(unittest.TestCase):
    def test_utf8_khong_bom_khong_ky_tu_dieu_khien(self):
        self.assertFalse(RAW.startswith(b'\xef\xbb\xbf'))
        self.assertEqual(SQL, unicodedata.normalize('NFC', SQL))
        self.assertFalse(any(unicodedata.category(c) in ('Cc', 'Cf')
                             and c not in '\r\n\t' for c in SQL))
        self.assertIn('Hợp đồng xây dựng', SQL)
        self.assertNotIn('�', SQL)

    def test_glob_migration_tu_dong_nhan_108_sau_106(self):
        from kho_tri_thuc.core import doi_cau_truc as dc
        paths = sorted(dc.THU_MUC_SQL.glob('[0-9][0-9][0-9]_*.sql'))
        self.assertIn(SQL_PATH, paths)
        self.assertGreater(int(SQL_PATH.name[:3]), 106)
        self.assertTrue(all(p < SQL_PATH for p in paths if int(p.name[:3]) <= 106))
        chain = dc._doc_chuoi(paths)
        self.assertIn(108, chain)

    def test_rao_csdl_demo_test_pg16_va_owner(self):
        for part in ("current_database() !~ '^(kho_core_demo_g2_",
                     "OR (tt<>'' AND current_database() !~ '^kho_test_')",
                     "current_setting('server_version_num')::integer<160000",
                     "NOT v.rolcanlogin", 'NOT v.rolsuper', 'NOT v.rolcreaterole',
                     'NOT v.rolbypassrls', "EXECUTE format('SET LOCAL ROLE %I',chu)",
                     "set_config('search_path','pg_catalog,pg_temp',true)",
                     "set_config('role',vai_cu,true)", 'LHD_BANG_108_VONG_1'):
            self.assertIn(part, SQL)

    def test_chi_mot_bang_moi_khong_cham_ho_so_chay(self):
        """QD-TAM-07: không dùng ho_so_chay.cau_hinh, bỏ vá ho_so_chay_ghi."""
        self.assertEqual(re.findall(r'CREATE TABLE IF NOT EXISTS ([\w.]+)', SQL),
                         ['loi.engine_tep_cau_hinh'])
        self.assertNotRegex(SQL, r'(?i)\b(?:DROP|ALTER\s+COLUMN|CREATE\s+EXTENSION)\b')
        code = _bo_chu_thich(SQL)
        for part in ('ho_so_chay_ghi', 'ho_so_chay_engine', 'ho_so_chay_schema',
                     'ho_so_chay_kiem_ket', 'pg_get_functiondef', '$neo$', '$chen$',
                     'CREATE OR REPLACE FUNCTION loi.xac_minh_phien(', 'trich_loai_hop_dong'):
            self.assertNotIn(part, code)

    def test_kieu_dong_loai_phien_ban_con_tro(self):
        for part in ("kieu text NOT NULL CHECK (kieu IN ('LOAI','PHIEN_BAN','DANG_DUNG'))",
                     'tham_chieu_id uuid REFERENCES loi.engine_tep_cau_hinh(id)',
                     'UNIQUE(ma_engine,nhom,kieu,khoa,so_phien_ban)',
                     "ON loi.engine_tep_cau_hinh(ma_engine,nhom,khoa,ma_bam) WHERE kieu='PHIEN_BAN'",
                     "CHECK (tao_boi IS NOT NULL OR (khoa='XD' AND so_phien_ban=1))"):
            self.assertIn(part, SQL)
        self.assertRegex(SQL, r'tep_id uuid,\r?\n')  # Không khóa ngoại sang kho tệp (CD-044); nhận LF/CRLF.

    def test_khong_cham_loi_tai_lieu_ngoai_cau_noi(self):
        """Opus vòng 1 điểm 1: owner Core không có USAGE loi_tai_lieu."""
        code = _bo_chu_thich(SQL)
        self.assertNotRegex(code, r'(?i)GRANT\s+USAGE\s+ON\s+SCHEMA\s+loi_tai_lieu')
        self.assertNotRegex(code, r'(?i)GRANT\s+\w+(?:\s*,\s*\w+)*\s+ON\s+(?:TABLE\s+)?loi_tai_lieu\.')
        self.assertNotIn('REFERENCES loi_tai_lieu', code)
        bridge = _bo_chu_thich(FUNCTIONS['trich_danh_muc_tep'][4])
        outside = code.replace(bridge, '')
        self.assertNotRegex(outside, r'(?i)\b(?:FROM|JOIN)\s+loi_tai_lieu\.')
        self.assertNotRegex(outside, r'loi_tai_lieu\.\w+\s*\((?!text,text,uuid,text,uuid,bigint\))')
        self.assertRegex(bridge, r'FROM loi_tai_lieu\.tep_goc')
        self.assertIn('JOIN loi_tai_lieu.ket_qua_xu_ly', bridge)
        self.assertIn("PERFORM loi_tai_lieu.ngu_canh(p_ma,'core',p_pn,p_hd,NULL,NULL)", bridge)
        for name in set(FUNCTIONS) - {'trich_danh_muc_tep'}:
            self.assertNotIn('loi_tai_lieu', FUNCTIONS[name][4], name)

    def test_cau_noi_owner_tai_lieu_definer_chi_core_goi(self):
        m = FUNCTIONS['trich_danh_muc_tep']
        self.assertEqual(m[3].split()[0], 'uuid[]')
        self.assertIn('SECURITY DEFINER SET search_path=pg_catalog,pg_temp', m[3])
        start = SQL.index('CREATE OR REPLACE FUNCTION loi.trich_danh_muc_tep(')
        before, after = SQL[:start], SQL[start:]
        self.assertGreater(before.rindex("SET LOCAL ROLE %I',chu_tl)"),
                           before.rindex("SET LOCAL ROLE %I',chu)"))
        self.assertGreater(before.rindex("GRANT CREATE ON SCHEMA loi TO %I',chu_tl)"),
                           before.rindex('loi.trich_danh_muc_doc(text,text) TO %I'))
        self.assertIn("REVOKE ALL ON FUNCTION loi.trich_danh_muc_tep(text,uuid,text,text,jsonb) FROM PUBLIC", after)
        grants = re.findall(r"GRANT EXECUTE ON FUNCTION loi\.trich_danh_muc_tep\([^)]*\) TO %I',(\w+)\)", SQL)
        self.assertEqual(grants, ['chu'])
        self.assertIn("REVOKE CREATE ON SCHEMA loi FROM %I',chu_tl)", after)
        self.assertNotIn('trich_danh_muc_tep', SQL[SQL.index("EXECUTE format('GRANT EXECUTE ON FUNCTION loi.trich_danh_muc_loai"):start])
        body = m[4]
        self.assertIn('EXCEPTION WHEN insufficient_privilege THEN', body)
        self.assertIn('LIMIT 5', body)
        self.assertIn('DISTINCT ON (t.ma_bam)', body)
        self.assertIn('jsonb_array_length(p_du_lieu)>200', body)
        for part in ('t.kich_thuoc BETWEEN 1 AND 2097152', 't.phap_nhan_id=p_pn',
                     "t.ma_bam=p_du_lieu->>'sha256'", "k.trang_thai='thanh_cong'",
                     "k.ma_contract='tham_so.v1'", "AND k.phien_ban_contract='1.0.0'"):
            self.assertIn(part, body)

    def test_csdl_sach_khong_gap_regclass_hang(self):
        """PG thật 42P01: hằng '...'::regclass bị gập lúc lập kế hoạch khi bảng chưa có."""
        code = _bo_chu_thich(SQL)
        self.assertNotRegex(code, r"'loi\.engine_tep_cau_hinh'::regclass")
        guard = code[:code.index('CREATE TABLE IF NOT EXISTS loi.engine_tep_cau_hinh')]
        self.assertNotRegex(guard, r'(?i)\b(?:FROM|JOIN|INTO)\s+loi\.engine_tep_cau_hinh\b')
        self.assertIn("attrelid=to_regclass('loi.engine_tep_cau_hinh')", code)

    def test_cau_noi_khong_nhan_tep_het_han_luu_giu(self):
        bridge = FUNCTIONS['trich_danh_muc_tep'][4]
        self.assertIn("LIKE '%.xlsx' AND t.het_han_luc IS NULL", bridge)

    def test_khong_gom_moi_loi(self):
        """Opus vòng 1 điểm 7: chỉ bắt lỗi dự kiến."""
        self.assertNotRegex(SQL, r'(?i)WHEN\s+OTHERS')
        self.assertNotIn('LHD_CAN_HO_SO_SCHEMA', SQL)
        self.assertNotIn('LHD_LOI_GHI', SQL)

    def test_chu_thich_dau_tep_anh_xa_ma_http_va_khoa_tra_ve(self):
        header = SQL[:SQL.index('DO $migration$')]
        for code in _ma_tra_ve() | {'LHD_PHIEN', 'LHD_CHI_CORE'}:
            self.assertRegex(header, re.escape(code) + r'\b', code)
        for status in ('200', '401', '403', '409', '422'):
            self.assertIn(status, header)
        self.assertGreaterEqual(header.count('kiem_toan_id'), 5)
        for name in CUA:
            self.assertIn('loi.trich_danh_muc_' + name + '(', header)
        self.assertIn('COMMIT', header)

    def test_definer_hep_kiem_phien_mtq_truoc_doc_ghi(self):
        self.assertEqual(set(FUNCTIONS), {'trich_danh_muc_quyen', 'trich_danh_muc_kiem_toan',
                                         'trich_danh_muc_loai', 'trich_danh_muc_ghi',
                                         'trich_danh_muc_kich_hoat', 'trich_danh_muc_doc',
                                         'trich_danh_muc_tep'})
        for name, action in (('loai', 'SUA'), ('ghi', 'SUA'), ('kich_hoat', 'DUYET'), ('doc', 'XEM')):
            m = FUNCTIONS['trich_danh_muc_' + name]
            self.assertIn('SECURITY DEFINER SET search_path=pg_catalog,pg_temp', m[3])
            body = m[4]
            self.assertIn(f"loi.trich_danh_muc_quyen(p_ma,'CORE:DANH_MUC_TRICH:{action}')", body)
            self.assertLess(body.index('loi.trich_danh_muc_quyen('), body.index('IF '))
            self.assertIn('EXIT kiem WHEN ma IS NOT NULL;', body)
            # Nhật ký ghi trước mọi INSERT dữ liệu và trước khi trả lỗi.
            audit = body.index(f"loi.trich_danh_muc_kiem_toan(q,'CORE:DANH_MUC_TRICH:{action}'")
            self.assertLess(audit, re.search(r'IF ma IS NOT NULL THEN\s+RETURN', body).start())
            if 'INSERT INTO loi.engine_tep_cau_hinh' in body:
                self.assertLess(audit, body.index('INSERT INTO loi.engine_tep_cau_hinh'))
            self.assertNotIn('RAISE EXCEPTION', body)
        auth = FUNCTIONS['trich_danh_muc_quyen'][4]
        for part in ('session_user::text IS DISTINCT FROM', "loai='NGUOI_DUNG'",
                     'loi.xac_minh_phien(', 'loi.mtq_quyet_dinh(', "IS DISTINCT FROM 'true'::jsonb",
                     'v.thu_hoi_luc IS NULL', "v.loai='PHAP_NHAN'", 'AND la_demo'):
            self.assertIn(part, auth)
        self.assertNotIn('mtq_admin', auth)
        for name in ('quyen', 'kiem_toan'):
            self.assertNotIn('SECURITY DEFINER', FUNCTIONS['trich_danh_muc_' + name][3])
        audit = FUNCTIONS['trich_danh_muc_kiem_toan'][4]
        for part in ("'TU_CHOI'", "'KHONG_DAT'", "'DAT'", 'doi_tuong_id'):
            self.assertIn(part, audit)

    def test_grant_chi_cua_cong_khong_grant_helper(self):
        start = SQL.index("EXECUTE format('GRANT EXECUTE ON FUNCTION loi.trich_danh_muc_loai")
        grants = SQL[start:SQL.index(';', start)]
        for name in CUA:
            self.assertIn('trich_danh_muc_' + name + '(', grants)
        self.assertIn("TO %I',login)", grants)
        for name in ('quyen', 'kiem_toan', 'tep'):
            self.assertNotIn('trich_danh_muc_' + name + '(', grants)
        self.assertIn("REVOKE ALL ON FUNCTION %s FROM PUBLIC", SQL)
        self.assertIn('a.grantee<>0 AND a.grantee<>p.proowner', SQL)

    def test_bang_bat_bien_rls_va_thu_hoi_acl(self):
        for part in ('ENABLE ROW LEVEL SECURITY', 'FORCE ROW LEVEL SECURITY',
                     'USING (true) WITH CHECK (true)',
                     'BEFORE UPDATE OR DELETE OR TRUNCATE', 'loi.chan_sua_kiem_toan()',
                     'REVOKE ALL ON TABLE loi.engine_tep_cau_hinh FROM PUBLIC',
                     'a.grantee<>0 AND a.grantee<>c.relowner'):
            self.assertIn(part, SQL)
        self.assertNotIn('GRANT SELECT ON TABLE loi.engine_tep_cau_hinh', SQL)
        self.assertNotIn('UPDATE loi.engine_tep_cau_hinh', SQL)

    def test_ba_hanh_dong_mtq_khong_tu_cap_quyen(self):
        rows = re.findall(r"\(1,'CORE','DANH_MUC_TRICH','(\w+)'", SQL)
        self.assertEqual(rows, ['XEM', 'SUA', 'DUYET'])
        self.assertNotIn("'KICH_HOAT'", SQL)
        self.assertNotIn('INSERT INTO loi.mtq_o', SQL)
        self.assertNotIn('INSERT INTO loi.mtq_gan_vai', SQL)
        self.assertIn('LHD_XUNG_DOT_MTQ', SQL)

    def test_them_loai_tu_man_hinh(self):
        body = FUNCTIONS['trich_danh_muc_loai'][4]
        for part in ("'ten','mo_ta','nhom_danh_muc_hop_dong','co_kiem_logic_rieng','trang_thai'",
                     "('XAY_DUNG','THUE_DAT','BAN_NHA','VAY','MUA','DICH_VU','KHAC')",
                     "NOT IN ('hoat_dong','ngung')", 'LHD_XUNG_DOT_PHIEN_BAN',
                     "kieu='LOAI'", 'coalesce(cu.so_phien_ban,0)+1', 'cu.tom_tat=p_thong_tin'):
            self.assertIn(part, body)

    def test_ghi_danh_muc_chi_metadata_va_tep_qua_cau_noi(self):
        body = FUNCTIONS['trich_danh_muc_ghi'][4]
        for part in ("'DANH_MUC'", "jsonb_build_object('tep_id',p_tep,'sha256',p_bam)",
                     'LHD_TEP_KHONG_HOP_LE', 'LHD_XUNG_DOT_HASH', 'LHD_LOAI_KHONG_THAY',
                     'coalesce(max(so_phien_ban),0)+1', "p_tom_tat-ARRAY[", "'PHIEN_BAN'"):
            self.assertIn(part, body)
        self.assertNotIn('noi_dung_excel', SQL)

    def test_kich_hoat_du_dieu_kien_muc_4_6_chi_viec_core(self):
        body = FUNCTIONS['trich_danh_muc_kich_hoat'][4]
        for part in ('NOT BETWEEN 10 AND 1000', "kieu='PHIEN_BAN' AND khoa=p_loai AND ma_bam=p_bam",
                     "v.trang_thai='XONG'", 'v.ma_loi IS NULL', "interval '30 days'",
                     "v.module='core' AND r.module='core'", 'cardinality(viec)<3',
                     "'chay_thu'='true'::jsonb", "'sha256'=p_bam", 'p.la_demo',
                     'IF NOT quay_lui THEN', "'CHAY_THU'", 'LHD_LOAI_NGUNG',
                     "'ly_do',btrim(p_ly_do)", "'viec_chay_thu',to_jsonb(viec)",
                     "'DANG_DUNG'", 'tham_chieu_id', 'EXIT kiem WHEN dd.ma_bam=p_bam;'):
            self.assertIn(part, body)
        self.assertNotIn('so_o_vang', body)  # Ô vàng không chặn kích hoạt.

    def test_seed_xd_v1_dung_khoa_tom_tat_va_dat_con_tro(self):
        self.assertIn(XD, SQL)
        self.assertIn(XD_ND, SQL)
        seed = re.search(r"xd_tom_tat constant jsonb := '(.*?)';", SQL, re.S)
        self.assertEqual(json.loads(seed[1]), XD_TOM_TAT)
        required = re.search(r"p_tom_tat \?& ARRAY\[(.*?)\]", FUNCTIONS['trich_danh_muc_ghi'][4])
        self.assertEqual(set(re.findall(r"'(\w+)'", required[1])), set(XD_TOM_TAT))
        loai = json.loads(re.search(r"xd_loai constant jsonb := '(.*?)';", SQL, re.S)[1])
        self.assertEqual(set(loai), {'ten', 'mo_ta', 'nhom_danh_muc_hop_dong',
                                     'co_kiem_logic_rieng', 'trang_thai'})
        self.assertEqual(loai['trang_thai'], 'hoat_dong')
        kich = json.loads(re.search(r"xd_kich_hoat constant jsonb := '(.*?)';", SQL, re.S)[1])
        self.assertEqual(kich['ly_do'], 'chuyển từ công cụ gốc, đã kiểm nhanh CD-071')
        for part in ("'DANG_DUNG','XD',1,xd,pb,xd_kich_hoat,kt",
                     "'PHIEN_BAN','XD',1,xd,xd_nd,xd_tom_tat,kt", 'LHD_SEED_XD_KHAC_MAU'):
            self.assertIn(part, SQL)
        self.assertNotIn('decode(', SQL)
        self.assertNotIn('base64', SQL)

    @unittest.skipUnless(XLSX_XD.exists(), 'Thiếu tệp ghim DANH_MUC_THAM_SO.xlsx (lead chép vào worktree)')
    def test_seed_xd_khop_bo_doc_sdk_tren_tep_ghim(self):
        from kho_tri_thuc.sdk_core import danh_muc_tham_so as dm
        data = XLSX_XD.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), XD)
        result = dm.doc_danh_muc(data, XLSX_XD.name)
        self.assertEqual(result.tom_tat, XD_TOM_TAT)
        self.assertEqual(result.ma_bam_noi_dung, XD_ND)

    def test_dollar_quote_va_khong_dynamic_sql_tu_du_lieu_nguoi_dung(self):
        tags = re.findall(r'\$(?:[A-Za-z_][A-Za-z_0-9]*)?\$', SQL)
        self.assertEqual(tags.count('$migration$'), 2)
        self.assertEqual(tags.count('$ham$'), 2 * len(FUNCTIONS))
        self.assertEqual(len(tags), 2 + 2 * len(FUNCTIONS))
        for name in FUNCTIONS:
            self.assertNotRegex(FUNCTIONS[name][4], r'\bEXECUTE\b')


try:
    import test_g2_25 as g225
except ImportError:  # pragma: no cover
    g225 = None


@unittest.skipUnless(g225 is not None and g225.psycopg is not None
                     and os.environ.get('KHO_PG_DSN_TEST'),
                     'CHUA_KIEM PG LHD-C1: lead opt-in KHO_PG_DSN_TEST/psycopg')
class PostgresTests(unittest.TestCase):
    setUpClass = classmethod(g225.PostgresTests.setUpClass.__func__) if g225 else None
    _token = g225.PostgresTests._token if g225 else None

    def setUp(self):
        self.pn, self.person = uuid4(), uuid4()
        self.core = self.connections['core']
        self.owner.execute("INSERT INTO loi.phap_nhan(id,ma,ten,la_demo) VALUES(%s,%s,'Pháp nhân DEMO',true)",
                           (self.pn, self.pn.hex))
        self.owner.execute("INSERT INTO loi.nguoi_dung(id,dang_nhap,ten,vai_tro) VALUES(%s,%s,'Người DEMO','CFO')",
                           (self.person, self.person.hex))
        self.owner.execute("INSERT INTO loi.phan_quyen(nguoi_dung_id,phap_nhan_id,module) VALUES(%s,%s,ARRAY['core'])",
                           (self.person, self.pn))
        self._matrix()
        self.token = self._token('core', 'core', ['CORE:DANH_MUC_TRICH:' + a for a in ('XEM', 'SUA', 'DUYET')])
        self.engine = uuid4()
        self.owner.execute("""INSERT INTO loi.engine_dinh_nghia(id,ma,ten,so_phien_ban,ma_bam_goi,
            ma_adapter,phien_ban_adapter,nang_luc,gioi_han) VALUES(%s,'e_trich_xuat','DEMO',%s,%s,
            'demo','1','[{"ma":"demo.trich@1","dau_vao":"tham_chieu_tep.v1","dau_ra":"demo.v1"}]','{}')""", (self.engine, 'demo-lhd-' + self.engine.hex, 'a' * 64))
        # Sổ loại dùng chung toàn hệ thống: mỗi test một mã loại riêng.
        self.kind = 'T' + uuid4().hex[:8].upper()
        self.catalog_hash = uuid4().hex + uuid4().hex
        self.content_hash = uuid4().hex + uuid4().hex
        self.tep = self._file(self.catalog_hash)

    def _matrix(self):
        phong, snapshot, gan, dong = uuid4(), uuid4(), uuid4(), uuid4()
        self.owner.execute("INSERT INTO loi.mtq_phong(id,phap_nhan_id,ma,ten) VALUES(%s,%s,'DEMO','DEMO')",
                           (phong, self.pn))
        self.owner.execute("INSERT INTO loi.mtq_phien_ban(id,phap_nhan_id,so_phien_ban,tao_boi,ly_do) VALUES(%s,%s,1,%s,'DEMO')",
                           (snapshot, self.pn, self.person))
        self.owner.execute("INSERT INTO loi.mtq_dong(id,phien_ban_id,phap_nhan_id,phong_id,vai) VALUES(%s,%s,%s,%s,'CFO')",
                           (dong, snapshot, self.pn, phong))
        # Trigger 006: mỗi phòng hoạt động cần đủ năm vai trước công bố
        # (mẫu test_cd060_doc_mtq); chỉ dòng CFO có ô DANH_MUC_TRICH.
        self.owner.execute("""INSERT INTO loi.mtq_dong(phien_ban_id,phap_nhan_id,phong_id,vai)
            SELECT %s,%s,%s,v FROM unnest(ARRAY['THUC_HIEN_1','THUC_HIEN_2','TRUONG_PHONG','NGUOI_XEM']) v""",
                           (snapshot, self.pn, phong))
        for action in ('XEM', 'SUA', 'DUYET'):
            if action == 'DUYET' and 'thieu_o' in self._testMethodName:
                continue
            self.owner.execute("INSERT INTO loi.mtq_o(dong_id,module,man,hanh_dong,cho_phep) VALUES(%s,'CORE','DANH_MUC_TRICH',%s,true)",
                               (dong, action))
        self.owner.execute("""INSERT INTO loi.mtq_gan_vai(id,nguoi_dung_id,phap_nhan_id,phong_id,vai,cap_boi,ly_do)
            VALUES(%s,%s,%s,%s,'CFO',%s,'DEMO')""", (gan, self.person, self.pn, phong, self.person))
        self.owner.execute("""INSERT INTO loi.mtq_pham_vi(gan_vai_id,phap_nhan_id,loai,khoa,cap_boi,ly_do)
            VALUES(%s,%s,'PHAP_NHAN',%s,%s,'DEMO')""", (gan, self.pn, str(self.pn), self.person))
        self.owner.execute("""UPDATE loi.mtq_phien_ban SET trang_thai='DA_CONG_BO',cong_bo_boi=%s,
            cong_bo_luc=now(),phien_ban_dong=phien_ban_dong+1 WHERE id=%s""", (self.person, snapshot))
        self.owner.execute("""INSERT INTO loi.mtq_kich_hoat(phap_nhan_id,bat,phien_ban_id,bat_boi,bat_luc)
            VALUES(%s,true,%s,%s,now())""", (self.pn, snapshot, self.person))

    def _file(self, digest, pn=None, expires=None):
        doc, tep = uuid4(), uuid4()
        pn = pn or self.pn
        self.owner.execute("""INSERT INTO loi_tai_lieu.tai_lieu(id,phap_nhan_id,module,loai,ten,
            bang_doi_tuong,doi_tuong_id,phien_ban_contract,tao_boi)
            VALUES(%s,%s,'core','DEMO','Mẫu DEMO','DEMO',%s,'1.0.0',%s)""", (doc, pn, uuid4(), self.person))
        self.owner.execute("""INSERT INTO loi_tai_lieu.tep_goc(id,phap_nhan_id,tai_lieu_id,ten_tep,ma_bam,
            kich_thuoc,mime,khoa_luu_tru,het_han_luc,tao_boi) VALUES(%s,%s,%s,'danh_muc_demo.xlsx',%s,123,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',%s,%s,%s)""",
                           (tep, pn, doc, digest, 'demo/' + tep.hex, expires, self.person))
        return tep

    def _call(self, sql_text, args):
        with self.core.transaction():
            return self.core.execute(sql_text, args).fetchone()[0]

    def _info(self, **over):
        return {'ten': 'Hợp đồng dịch vụ DEMO', 'mo_ta': 'Loại DEMO', 'nhom_danh_muc_hop_dong': 'DICH_VU',
                'co_kiem_logic_rieng': False, 'trang_thai': 'hoat_dong', **over}

    def _add_kind(self, *, info=None, old=0, kind=None, token=None):
        return self._call('SELECT loi.trich_danh_muc_loai(%s,%s,%s::jsonb,%s)',
                          ((token or self.token).lay_de_truyen(), kind or self.kind,
                           json.dumps(info or self._info()), old))

    def _write(self, *, summary=None, token=None, tep=None, kind=None, digest=None, content=None):
        return self._call('SELECT loi.trich_danh_muc_ghi(%s,%s,%s,%s,%s,%s::jsonb)',
                          ((token or self.token).lay_de_truyen(), kind or self.kind,
                           digest or self.catalog_hash, content or self.content_hash,
                           tep or self.tep, json.dumps(SUMMARY if summary is None else summary)))

    def _activate(self, kind=None, digest=None, *, token=None, reason='DEMO kiểm tra kích hoạt'):
        return self._call('SELECT loi.trich_danh_muc_kich_hoat(%s,%s,%s,%s)',
                          ((token or self.token).lay_de_truyen(), kind or self.kind,
                           digest or self.catalog_hash, reason))

    def _read(self, kind):
        return self._call('SELECT loi.trich_danh_muc_doc(%s,%s)', (self.token.lay_de_truyen(), kind))

    def _audit(self, result, status, action):
        row = self.owner.execute('SELECT ket_luan,hanh_dong FROM loi.nhat_ky_kiem_toan WHERE id=%s',
                                 (result['kiem_toan_id'],)).fetchone()
        self.assertEqual(row, (status, 'CORE:DANH_MUC_TRICH:' + action))

    def _rows(self, kieu, khoa):
        return self.owner.execute("""SELECT so_phien_ban,ma_bam,tham_chieu_id,tom_tat,tao_boi
            FROM loi.engine_tep_cau_hinh WHERE kieu=%s AND khoa=%s ORDER BY so_phien_ban""",
                                  (kieu, khoa)).fetchall()

    def _module(self):
        """Module DEMO chỉ ở registry (không schema/vai thật) để có việc ngoài Core."""
        module = 'lhd' + uuid4().hex[:8]
        self.owner.execute("INSERT INTO loi.module_danh_muc(ma,ten,loai,ten_schema,vai_so_huu) "
                           "VALUES(%s,'Module DEMO','MODULE',%s,%s)",
                           (module, 'mod_' + module, self.tt + 'vai_doi_cau_truc_mod_' + module))
        return module

    def _trial(self, *, sample_hash=None, catalog_hash=None, days=0, success=True, module='core'):
        """Metadata DEMO của một lần chạy; không thực thi engine hay tạo bytes."""
        self.owner.execute("""INSERT INTO loi.phien_ban_module(module,so_phien_ban,ma_bam_goi,tuong_thich)
            VALUES(%s,'1.0.0',%s,'{}') ON CONFLICT DO NOTHING""", (module, 'a' * 64))
        self.owner.execute("""INSERT INTO loi.dang_ky_contract(ma,phien_ban,module_so_huu,lop,
            muc_dich,sieu_du_lieu,luoc_do,ma_bam) VALUES('tham_so.v1','1.0.0','core','ky_thuat',
            'Kết quả DEMO','{}','{}',%s) ON CONFLICT DO NOTHING""", ('b' * 64,))
        self.owner.execute("""INSERT INTO loi.quy_trinh(phap_nhan_id,module,ma,phien_ban,
            phien_ban_module,buoc,ma_bam,tao_boi) VALUES(%s,%s,'lhd_demo',1,'1.0.0','[]',%s,%s)
            ON CONFLICT DO NOTHING""", (self.pn, module, 'c' * 64, self.person))
        sample = self._file(sample_hash or (uuid4().hex + uuid4().hex))
        doc = self.owner.execute('SELECT tai_lieu_id FROM loi_tai_lieu.tep_goc WHERE id=%s',
                                  (sample,)).fetchone()[0]
        run, job, output = uuid4(), uuid4(), uuid4()
        body = dict(chay_thu=True, loai_hop_dong=self.kind, tep_id=str(sample),
                    danh_muc={'sha256': catalog_hash or self.catalog_hash})
        steps = {'trich': dict(viec_id=str(job), dau_vao=body)}
        self.owner.execute("""INSERT INTO loi.quy_trinh_lan(id,phap_nhan_id,module,ma,phien_ban,
            tao_boi,hanh_dong,bang_tham_chieu,tham_chieu_id,khoa,dau_vao,buoc)
            VALUES(%s,%s,%s,'lhd_demo',1,%s,'CORE:DU_LIEU:LAP','DEMO',%s,%s,'{}',%s::jsonb)""",
                           (run, self.pn, module, self.person, doc, run.hex, json.dumps(steps)))
        self.owner.execute("""INSERT INTO loi.hang_viec(id,phap_nhan_id,module,loai,phien_ban,engine_id,
            phien_ban_contract,khoa_chong_trung,bang_tham_chieu,tham_chieu_id,hanh_dong,
            pham_vi_hanh_dong,co_tac_dong_ngoai,thu_lai_an_toan,toi_da_lan_thu,thu_lai_giay,
            trang_thai,ma_loi,tao_boi,ket_thuc_luc,quy_trinh_lan_id,quy_trinh_buoc)
            VALUES(%s,%s,%s,'DEMO',1,%s,'1.0.0',%s,'DEMO',%s,'CORE:DU_LIEU:LAP',
            ARRAY['CORE:DU_LIEU:LAP'],false,false,1,1,%s,%s,%s,
            clock_timestamp()-%s*interval '1 day',%s,'trich')""",
                           (job, self.pn, module, self.engine, job.hex, doc,
                            'XONG' if success else 'LOI', None if success else 'DEMO_LOI',
                            self.person, days, run))
        self.owner.execute("""INSERT INTO loi_tai_lieu.ket_qua_xu_ly(id,phap_nhan_id,tai_lieu_id,
            goc_id,revision,bien_the,ma_contract,phien_ban_contract,module,phien_ban_module,
            engine_id,ham,phien_ban_ham,viec_id,buoc_id,lan_thu_id,the_he,trang_thai,ly_do,tao_boi)
            VALUES(%s,%s,%s,%s,1,'noi_dung','tham_so.v1','1.0.0',%s,'1.0.0',%s,
            'DEMO','1',%s,%s,%s,1,%s,'Kết quả DEMO',%s)""",
                           (output, self.pn, doc, output, module, self.engine, job, uuid4(), uuid4(),
                            'thanh_cong' if success else 'loi', self.person))
        self.owner.execute('UPDATE loi.hang_viec SET ket_qua_id=%s WHERE id=%s', (output, job))
        return job

    def _tt(self):
        return self.tt  # Tiền tố vai của CSDL kho_test (setUpClass G2-25).

    # --- Áp chuỗi + quyền catalog -------------------------------------------------
    def test_ap_chuoi_001_108_quyen_cau_noi_va_replay(self):
        tt = self._tt()
        chu, chu_tl = tt + 'vai_doi_cau_truc_loi', tt + 'vai_doi_cau_truc_loi_tai_lieu'
        self.assertIsNotNone(self.owner.execute(
            "SELECT 1 FROM pg_attribute WHERE attrelid='loi.engine_tep_cau_hinh'::regclass AND attname='kieu'").fetchone())
        self.assertFalse(self.owner.execute("SELECT has_schema_privilege(%s,'loi_tai_lieu','USAGE')",
                                            (chu,)).fetchone()[0])
        self.assertFalse(self.owner.execute("SELECT has_schema_privilege(%s,'loi','CREATE')",
                                            (chu_tl,)).fetchone()[0])
        bridge = 'loi.trich_danh_muc_tep(text,uuid,text,text,jsonb)'
        self.assertEqual(self.owner.execute(
            'SELECT pg_get_userbyid(proowner),prosecdef FROM pg_proc WHERE oid=%s::regprocedure',
            (bridge,)).fetchone(), (chu_tl, True))
        self.assertEqual(self.owner.execute(
            "SELECT pg_get_userbyid(a.grantee) FROM pg_proc p,LATERAL aclexplode(coalesce(p.proacl,"
            "acldefault('f',p.proowner))) a WHERE p.oid=%s::regprocedure AND a.grantee<>p.proowner",
            (bridge,)).fetchall(), [(chu,)])
        before = self.owner.execute('SELECT count(*) FROM loi.engine_tep_cau_hinh').fetchone()[0]
        with self.owner.transaction():
            self.owner.execute(SQL)
        self.assertEqual(self.owner.execute('SELECT count(*) FROM loi.engine_tep_cau_hinh').fetchone()[0], before)
        self.assertFalse(self.owner.execute("SELECT has_schema_privilege(%s,'loi','CREATE')",
                                            (chu_tl,)).fetchone()[0])

    def test_runtime_khong_duoc_doc_bang_hoac_goi_helper(self):
        login = self.credentials['core']['user']
        self.assertFalse(self.owner.execute("SELECT has_table_privilege(%s,'loi.engine_tep_cau_hinh','SELECT')", (login,)).fetchone()[0])
        for signature in ('loi.trich_danh_muc_quyen(text,text)',
                          'loi.trich_danh_muc_kiem_toan(jsonb,text,text,uuid)',
                          'loi.trich_danh_muc_tep(text,uuid,text,text,jsonb)'):
            self.assertFalse(self.owner.execute('SELECT has_function_privilege(%s,%s,%s)',
                                               (login, signature, 'EXECUTE')).fetchone()[0])

    def test_bang_bat_bien(self):
        with self.assertRaises(g225.psycopg.Error), self.owner.transaction():
            self.owner.execute("UPDATE loi.engine_tep_cau_hinh SET tom_tat='{}' WHERE khoa='XD'")

    # --- Seed XD -------------------------------------------------------------
    def test_seed_xd_v1_dang_dung_ngay_sau_ap(self):
        self.assertEqual([r[:2] for r in self._rows('PHIEN_BAN', 'XD')][:1], [(1, XD)])
        pointer = self._rows('DANG_DUNG', 'XD')[0]
        self.assertEqual(pointer[:2], (1, XD))
        result = self._read('XD')
        self.assertEqual(result['ma'], 'DAT', result)
        self.assertEqual(result['dang_dung']['ma_bam'], XD)
        self.assertEqual(result['phien_ban'][0]['tom_tat'], XD_TOM_TAT)
        self.assertEqual(result['phien_ban'][0]['ma_bam_noi_dung'], XD_ND)
        self._audit(result, 'DAT', 'XEM')
        listing = self._read(None)
        xd = [x for x in listing['loai'] if x['khoa'] == 'XD'][0]
        self.assertEqual(xd['dang_dung']['ma_bam'], XD)
        self.assertEqual(xd['thong_tin']['ten'], 'Hợp đồng xây dựng')

    def test_xd_dang_dung_kich_hoat_lai_khong_them_dong(self):
        before = len(self._rows('DANG_DUNG', 'XD'))
        result = self._activate('XD', XD)
        self.assertEqual(result['ma'], 'DAT', result)
        self.assertTrue(result['khong_doi'])
        self.assertEqual(len(self._rows('DANG_DUNG', 'XD')), before)
        self._audit(result, 'DAT', 'DUYET')

    # --- Thêm loại -----------------------------------------------------------
    def test_them_loai_dv_replay_va_sua_co_khoa_phien_ban(self):
        first = self._add_kind()
        self.assertEqual((first['ma'], first['so_phien_ban'], first['khong_doi']), ('DAT', 1, False), first)
        self._audit(first, 'DAT', 'SUA')
        again = self._add_kind()
        self.assertEqual((again['id'], again['khong_doi']), (first['id'], True))
        clash = self._add_kind(info=self._info(ten='Tên khác'), old=0)
        self.assertEqual(clash['ma'], 'LHD_XUNG_DOT_PHIEN_BAN')
        self._audit(clash, 'KHONG_DAT', 'SUA')
        second = self._add_kind(info=self._info(ten='Tên khác'), old=1)
        self.assertEqual((second['ma'], second['so_phien_ban']), ('DAT', 2), second)
        self.assertEqual(self._rows('LOAI', self.kind)[-1][4], self.person)
        listing = self._read(None)
        mine = [x for x in listing['loai'] if x['khoa'] == self.kind][0]
        self.assertIsNone(mine['dang_dung'])

    def test_them_loai_sai_dau_vao(self):
        for info in (self._info(nhom_danh_muc_hop_dong='LA'), self._info(trang_thai='dang_dung'),
                     {**self._info(), 'thua': 1}, self._info(ten=' ')):
            result = self._add_kind(info=info)
            self.assertEqual(result['ma'], 'LHD_DAU_VAO', info)
        self.assertEqual(self._add_kind(kind='xd')['ma'], 'LHD_DAU_VAO')

    # --- Ghi phiên bản -------------------------------------------------------
    def test_ghi_phien_ban_va_replay_khong_tang_so(self):
        self.assertEqual(self._add_kind()['ma'], 'DAT')
        first, second = self._write(), self._write()
        self.assertEqual(first['ma'], 'DAT', first)
        self.assertEqual((first['id'], first['so_phien_ban']), (second['id'], second['so_phien_ban']))
        self.assertTrue(second['khong_doi'])
        self.assertEqual(self.owner.execute('SELECT kieu,ma_bam,ma_bam_noi_dung,tom_tat FROM loi.engine_tep_cau_hinh WHERE id=%s',
                                           (first['id'],)).fetchone(),
                         ('PHIEN_BAN', self.catalog_hash, self.content_hash, SUMMARY))
        self._audit(first, 'DAT', 'SUA')
        clash = self._write(content='0' * 64)
        self.assertEqual(clash['ma'], 'LHD_XUNG_DOT_HASH')

    def test_ghi_loai_chua_co(self):
        result = self._write()
        self.assertEqual(result['ma'], 'LHD_LOAI_KHONG_THAY')
        self._audit(result, 'KHONG_DAT', 'SUA')

    def test_ghi_tep_khac_phap_nhan_hoac_sai_sha_qua_cau_noi(self):
        self.assertEqual(self._add_kind()['ma'], 'DAT')
        other = uuid4()
        self.owner.execute("INSERT INTO loi.phap_nhan(id,ma,ten,la_demo) VALUES(%s,%s,'Pháp nhân DEMO 2',true)",
                           (other, other.hex))
        foreign = self._file(self.catalog_hash, pn=other)
        result = self._write(tep=foreign)
        self.assertEqual(result['ma'], 'LHD_TEP_KHONG_HOP_LE')
        self._audit(result, 'KHONG_DAT', 'SUA')
        self.assertEqual(self._write(digest='d' * 64)['ma'], 'LHD_TEP_KHONG_HOP_LE')
        self.assertEqual(self._write(tep=uuid4())['ma'], 'LHD_TEP_KHONG_HOP_LE')
        # Tệp có hạn lưu giữ (059) không làm nguồn danh mục.
        expiring = self._file(self.catalog_hash, expires='2999-01-01T00:00:00+00:00')
        self.assertEqual(self._write(tep=expiring)['ma'], 'LHD_TEP_KHONG_HOP_LE')
        self.assertEqual(self._write()['ma'], 'DAT')

    def test_tu_choi_tom_tat_chua_noi_dung_mo_ta(self):
        self.assertEqual(self._add_kind()['ma'], 'DAT')
        result = self._write(summary={**SUMMARY, 'mo_ta': 'Không lưu nội dung Excel'})
        self.assertEqual(result['ma'], 'LHD_DAU_VAO')
        self._audit(result, 'KHONG_DAT', 'SUA')

    # --- Từ chối có nhật ký --------------------------------------------------
    def test_tu_choi_thieu_quyen_phien_co_audit(self):
        token = self._token('core', 'core', ['CORE:DANH_MUC_TRICH:XEM'])
        result = self._activate('XD', XD, token=token)
        self.assertEqual(result['ma'], 'LHD_TU_CHOI')
        self._audit(result, 'TU_CHOI', 'DUYET')
        result = self._write(token=token)
        self.assertEqual(result['ma'], 'LHD_TU_CHOI')
        self._audit(result, 'TU_CHOI', 'SUA')
        result = self._add_kind(token=token)
        self.assertEqual(result['ma'], 'LHD_TU_CHOI')
        self._audit(result, 'TU_CHOI', 'SUA')
        self.assertEqual(self._rows('LOAI', self.kind), [])

    def test_tu_choi_thieu_o_mtq_ke_ca_admin(self):
        self.owner.execute("INSERT INTO loi.mtq_admin(nguoi_dung_id,cap_boi,ly_do) VALUES(%s,%s,'DEMO')",
                           (self.person, self.person))
        # Trigger mtq_doi_quyen (006) thu hồi token đã cấp trong setUp.
        result = self._activate('XD', XD)
        self.assertEqual(result['ma'], 'LHD_PHIEN', result)
        self._audit(result, 'TU_CHOI', 'DUYET')
        self.assertIsNone(self.owner.execute('SELECT nguoi_dung_id FROM loi.nhat_ky_kiem_toan WHERE id=%s',
                                            (result['kiem_toan_id'],)).fetchone()[0])
        # Phiên mới hợp lệ có quyền DUYET; Admin vẫn thiếu ô DUYET của MTQ.
        token = self._token('core', 'core', ['CORE:DANH_MUC_TRICH:' + a for a in ('XEM', 'SUA', 'DUYET')])
        result = self._activate('XD', XD, token=token)
        self.assertEqual(result['ma'], 'LHD_TU_CHOI')
        self._audit(result, 'TU_CHOI', 'DUYET')
        self.assertEqual(self.owner.execute('SELECT nguoi_dung_id,phap_nhan_id FROM loi.nhat_ky_kiem_toan WHERE id=%s',
                                           (result['kiem_toan_id'],)).fetchone(), (self.person, self.pn))

    def test_tu_choi_phien_sai_co_audit_khong_gan_nham_nguoi(self):
        result = self._call("SELECT loi.trich_danh_muc_kich_hoat('DEMO_PHIEN_SAI','XD',%s,'DEMO kiểm tra từ chối')",
                            (XD,))
        self.assertEqual(result['ma'], 'LHD_PHIEN')
        self._audit(result, 'TU_CHOI', 'DUYET')
        self.assertIsNone(self.owner.execute('SELECT nguoi_dung_id FROM loi.nhat_ky_kiem_toan WHERE id=%s',
                                            (result['kiem_toan_id'],)).fetchone()[0])

    # --- Kích hoạt (4.6) -----------------------------------------------------
    def _ready(self):
        self.assertEqual(self._add_kind()['ma'], 'DAT')
        self.assertEqual(self._write()['ma'], 'DAT')

    def test_phien_ban_moi_chua_du_ba_mau_khong_duoc_kich_hoat(self):
        self._ready()
        result = self._activate()
        self.assertEqual(result['ma'], 'LHD_CHUA_DU_CHAY_THU')
        self._audit(result, 'KHONG_DAT', 'DUYET')
        self.assertEqual(self._rows('DANG_DUNG', self.kind), [])

    def test_ba_mau_xong_kich_hoat_va_ghi_can_cu_thanh_dong(self):
        self._ready()
        jobs = {str(self._trial()) for _ in range(3)}
        result = self._activate()
        self.assertEqual(result['ma'], 'DAT', result)
        self.assertFalse(result['quay_lui'])
        self.assertEqual(set(result['viec_chay_thu']), jobs)
        self._audit(result, 'DAT', 'DUYET')
        rows = self._rows('DANG_DUNG', self.kind)
        self.assertEqual(len(rows), 1)
        so, digest, ref, basis, by = rows[0]
        self.assertEqual((so, digest, by), (1, self.catalog_hash, self.person))
        self.assertEqual(str(ref), self._write()['id'])
        self.assertEqual(basis['ly_do'], 'DEMO kiểm tra kích hoạt')
        self.assertEqual(set(basis['viec_chay_thu']), jobs)
        doc = self._read(self.kind)
        self.assertEqual(doc['dang_dung']['ma_bam'], self.catalog_hash)
        self.assertEqual(len(doc['lich_su_kich_hoat']), 1)

    def test_hai_mau_xong_van_chua_du(self):
        self._ready()
        for _ in range(2):
            self._trial()
        self.assertEqual(self._activate()['ma'], 'LHD_CHUA_DU_CHAY_THU')

    def test_khong_tinh_mau_qua_30_ngay_sai_sha_hoac_loi_engine(self):
        self._ready()
        self._trial()
        self._trial(days=31)
        self._trial(catalog_hash='f' * 64)
        self._trial(success=False)
        self.assertEqual(self._activate()['ma'], 'LHD_CHUA_DU_CHAY_THU')

    def test_khong_tinh_viec_cua_module_khac_core(self):
        self._ready()
        core_jobs = {str(self._trial()) for _ in range(2)}
        module = self._module()
        for _ in range(2):
            self._trial(module=module)
        result = self._activate()
        self.assertEqual(result['ma'], 'LHD_CHUA_DU_CHAY_THU', result)
        self.assertEqual(set(result['viec_chay_thu']), core_jobs)

    def test_tu_choi_phien_phap_nhan_khong_demo_co_audit(self):
        real = uuid4()
        self.owner.execute("INSERT INTO loi.phap_nhan(id,ma,ten,la_demo) VALUES(%s,%s,'Pháp nhân thử không DEMO',false)",
                           (real, real.hex))
        self.owner.execute("INSERT INTO loi.phan_quyen(nguoi_dung_id,phap_nhan_id,module) VALUES(%s,%s,ARRAY['core'])",
                           (self.person, real))
        demo, self.pn = self.pn, real
        try:
            token = self._token('core', 'core', ['CORE:DANH_MUC_TRICH:' + a for a in ('XEM', 'SUA', 'DUYET')])
        finally:
            self.pn = demo
        for result, action in ((self._add_kind(token=token), 'SUA'),
                               (self._activate('XD', XD, token=token), 'DUYET')):
            self.assertEqual(result['ma'], 'LHD_CHI_PHAP_NHAN_DEMO', result)
            self._audit(result, 'TU_CHOI', action)
            self.assertEqual(self.owner.execute('SELECT phap_nhan_id FROM loi.nhat_ky_kiem_toan WHERE id=%s',
                                                (result['kiem_toan_id'],)).fetchone()[0], real)
        self.assertEqual(self._rows('LOAI', self.kind), [])

    def test_ba_lan_cung_bytes_mau_khong_tinh_thanh_ba_hop_dong(self):
        self._ready()
        for _ in range(3):
            self._trial(sample_hash='e' * 64)
        self.assertEqual(self._activate()['ma'], 'LHD_CHUA_DU_CHAY_THU')

    def test_quay_lui_phien_ban_tung_dang_dung_khong_can_chay_lai(self):
        self._ready()
        for _ in range(3):
            self._trial()
        self.assertEqual(self._activate()['ma'], 'DAT')
        first = self.catalog_hash
        second = uuid4().hex + uuid4().hex
        tep2 = self._file(second)
        self.assertEqual(self._write(digest=second, tep=tep2, content='1' * 64)['ma'], 'DAT')
        for _ in range(3):
            self._trial(catalog_hash=second)
        self.assertEqual(self._activate(digest=second)['ma'], 'DAT')
        back = self._activate(digest=first)
        self.assertEqual(back['ma'], 'DAT', back)
        self.assertTrue(back['quay_lui'])
        self.assertEqual(back['viec_chay_thu'], [])
        self.assertEqual([r[1] for r in self._rows('DANG_DUNG', self.kind)], [first, second, first])

    def test_loai_ngung_khong_kich_hoat(self):
        self._ready()
        for _ in range(3):
            self._trial()
        self.assertEqual(self._add_kind(info=self._info(trang_thai='ngung'), old=1)['ma'], 'DAT')
        result = self._activate()
        self.assertEqual(result['ma'], 'LHD_LOAI_NGUNG')
        self._audit(result, 'KHONG_DAT', 'DUYET')

    def test_ly_do_ngan_va_sai_loai_khong_duoc_kich_hoat(self):
        self.assertEqual(self._activate('XD', XD, reason='ngắn')['ma'], 'LHD_DAU_VAO')
        self.assertEqual(self._add_kind()['ma'], 'DAT')
        self.assertEqual(self._activate(self.kind, XD)['ma'], 'LHD_LOAI_PHIEN_BAN')


if __name__ == '__main__':
    unittest.main()
