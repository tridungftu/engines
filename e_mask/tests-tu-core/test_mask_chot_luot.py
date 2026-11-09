"""MASK-3D: byte SQL gốc, điều phối/kho RAM; PG chỉ lead chạy trên DEMO.

Không đọc DSN/cấu hình từ tệp, không mở/dừng dịch vụ. Ca PG có CHUA_KIEM
khi chỉ chạy thuần. Dùng fixture 118 và các kết nối test đã provision sẵn.
"""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from hashlib import sha256
import importlib.util
import inspect
import json
import os
from pathlib import Path
import re
from threading import Barrier, Event
import unicodedata
import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from engines.e_mask.che_van_ban import Kho, che, chuan_hoa, mo_che
from kho_tri_thuc.core.mask import KhoLuot, LoiLuotMask, Mask, XungDotLuotMask
from kho_tri_thuc.core.phien import MaBiMat
from tests import test_mask_phien as nen
from tests.test_mask_4a import kiem_cau_truc_sql
from tests.test_mask_kho import TEN, VAN_BAN, tai_nguyen_demo


ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = ROOT/'src/kho_tri_thuc/core/sql/120_mask_chot_luot.sql'
CTX = 'text,text,uuid,text,uuid,uuid,bigint,uuid,uuid,text'
PUBLIC = {'snapshot_luot': CTX, 'chot_luot': CTX+',text,jsonb,jsonb'}
RONG = dict(cum=[], bi_danh_tam_moi=[], bi_danh_da_dung=[], dong_yeu_cau=False,
            cum_da_tra=[], bi_danh_da_tra=[])


def doc_sql():
    return SQL_PATH.read_bytes().decode('utf-8', errors='strict')


def cac_ham():
    return dict(re.findall(r'CREATE OR REPLACE FUNCTION mask\.([a-z_]+)\(.*?'
                           r'AS \$ham\$(.*?)\$ham\$;', doc_sql(), re.S))


def snapshot(danh_muc=None, yeu_cau=None):
    return dict(da_chot=False, phien_ban='a'*64,
                danh_muc=[] if danh_muc is None else deepcopy(danh_muc), yeu_cau=yeu_cau)


class SQLThuanTests(unittest.TestCase):
    def test_byte_goc_utf8_nfc_khong_bom_mat_dau(self):
        for path in (SQL_PATH, ROOT/'src/kho_tri_thuc/core/mask.py', Path(__file__)):
            raw = path.read_bytes()
            text = raw.decode('utf-8', errors='strict')
            self.assertFalse(raw.startswith(b'\xef\xbb\xbf'))
            self.assertEqual(raw, text.encode('utf-8'))
            self.assertEqual(text, unicodedata.normalize('NFC', text))
            self.assertNotIn('\ufffd', text)
        self.assertIn('chốt nguyên tử', doc_sql())

    def test_chuoi_120_duy_nhat_doc_nguyen_byte_va_cau_truc(self):
        from kho_tri_thuc.core.doi_cau_truc import _doc_chuoi
        files = list(SQL_PATH.parent.glob('[0-9][0-9][0-9]_*.sql'))
        self.assertEqual([p.name for p in files if p.name.startswith('120_')], [SQL_PATH.name])
        self.assertEqual(_doc_chuoi(files)[120][0], doc_sql())
        kiem_cau_truc_sql(SQL_PATH.read_bytes())
        self.assertEqual(set(cac_ham()), set(PUBLIC) | {'giu_phien_anh_xa', 'phien_ban_luot'})

    def test_guard_truoc_ddl_khop_113_117_118_119(self):
        guard = doc_sql().split("PERFORM set_config('search_path'", 1)[0]
        for part in ("tt !~ '^[a-z][a-z0-9_]*_$'", 'octet_length(', '^kho_test_',
                     'kho_core_demo_g2_', '160000', "vai_cu<>'none'", 'pg_auth_members',
                     'rolcanlogin', 'rolsuper', 'rolbypassrls', 'rolcreatedb', 'rolreplication',
                     'relrowsecurity AND relforcerowsecurity', "polname='vung_demo'",
                     "polname<>'vung_demo'", "polname='tai_lieu_phien'", 'MASK_LUOT_SAI_OWNER',
                     nen.NGU_CANH, nen.TAI_LIEU, nen.MOI, '"und-x-icu"', 'cum_da_gap', 'so_lan_gap'):
            self.assertIn(part, guard)
        self.assertNotRegex(guard, r'\b(?:CREATE|ALTER|GRANT|REVOKE)\b')
        for cua in ('liet_ke_dinh_danh', 'ghi_cho_duyet', 'ghi_bi_danh_da_dung', 'dong_yeu_cau'):
            self.assertIn('mask.'+cua+'(text,text,uuid,text,uuid,bigint,uuid', guard)

    def test_hai_cua_xac_minh_phien_tai_lieu_demo_khoi_phuc_ca_phat_lai(self):
        for cua in PUBLIC:
            body = cac_ham()[cua]
            for part in ('loi.mask_ngu_canh(', 'loi_tai_lieu.mask_kiem_tai_lieu(',
                         'yc.nguoi_gui<>ctx.nguoi_gui', 'yc.module<>p_module',
                         'yc.tai_lieu_id<>p_tai_lieu', 'yc.la_demo<>ctx.la_demo',
                         "current_setting('ktt.mask_la_demo',true)",
                         "set_config('ktt.mask_la_demo',coalesce(cu,''),true)"):
                self.assertIn(part, body, cua)
            self.assertLess(body.index('loi.mask_ngu_canh('), body.index("set_config('ktt.mask_la_demo',ctx.la_demo::text,true)"))
            self.assertLess(body.index('loi_tai_lieu.mask_kiem_tai_lieu('), body.index('SELECT l.* INTO cu_luot'))
        self.assertNotIn('p_la_demo', doc_sql())
        self.assertNotIn('p_nguoi_gui', doc_sql())

    def test_snapshot_qua_119_yeu_cau_moi_chi_savepoint_rollback(self):
        body = cac_ham()['snapshot_luot']
        self.assertIn('mask.liet_ke_dinh_danh(', body)
        self.assertNotIn('mask.tra_dinh_danh(', body)
        self.assertIn("RAISE EXCEPTION 'MASK_SNAPSHOT_TAM' USING ERRCODE='P1200'", body)
        self.assertIn("EXCEPTION WHEN SQLSTATE 'P1200' THEN", body)
        self.assertNotIn('WHEN OTHERS', body)
        self.assertLess(body.index('phien := mask.phien_ban_luot('), body.index('INSERT INTO mask.yeu_cau'))

    def test_phien_ban_tung_anh_xa_chi_so_khoa_da_tra_khong_so_dem(self):
        version = cac_ham()['phien_ban_luot']
        for part in ('sha256(', "'cum'", "'bi_danh'", 'to_jsonb(y)', 'd.gia_tri_chuan', 'c.cum_chuan'):
            self.assertIn(part, version)
        for part in ('to_jsonb(d)', 'to_jsonb(c)', 'so_lan_gap'):
            self.assertNotIn(part, version)
        for cua in PUBLIC:
            body = cac_ham()[cua]
            self.assertIn("current_setting('transaction_isolation')<>'read committed'", body)
            self.assertIn('LOCK TABLE mask.yeu_cau,mask.cho_duyet,mask.dinh_danh IN EXCLUSIVE MODE', body)
        self.assertEqual(doc_sql().count("SET lock_timeout='1s'"), 2)
        body = cac_ham()['chot_luot']
        self.assertLess(body.index('LOCK TABLE'), body.index('phien_moi := mask.phien_ban_luot('))
        self.assertLess(body.index("phien_cu->'cum'->khoa IS DISTINCT FROM"), body.index('INSERT INTO mask.yeu_cau'))
        self.assertIn("p_nhat_ky->'cum_da_tra'", body)
        self.assertIn("p_nhat_ky->'bi_danh_da_tra'", body)
        self.assertIn("ERRCODE='40001'", body)

    def test_phien_ban_tu_metadata_hang_khong_bam_gia_tri_goc(self):
        version = cac_ham()['phien_ban_luot']
        for prefix in ('d:', 'bd:d:'):
            self.assertEqual(version.count("'"+prefix+"'||d.id::text||':'||d.xmin::text"), 1)
        for prefix in ('c:', 'bd:c:'):
            self.assertEqual(version.count("'"+prefix+"'||c.id::text||':'||c.phien_ban_anh_xa::text"), 1)
        for part in ('d.gia_tri,', 'c.cum_goc', 'ax.goc', 'jsonb_build_array('):
            self.assertNotIn(part, version)
        trigger = cac_ham()['giu_phien_anh_xa']
        for column in ('id', 'cum_goc', 'nhom', 'bi_danh_tam', 'la_demo'):
            self.assertIn('NEW.'+column, trigger)
            self.assertIn('OLD.'+column, trigger)
        self.assertIn('OLD.phien_ban_anh_xa+1', trigger)
        self.assertIn('NEW.phien_ban_anh_xa := OLD.phien_ban_anh_xa;', trigger)
        self.assertNotIn('so_lan_gap', trigger)
        self.assertIn('ADD COLUMN IF NOT EXISTS phien_ban_anh_xa bigint NOT NULL DEFAULT 1', doc_sql())
        self.assertIn('tgtype=19', doc_sql())
        self.assertIn("tgattr=''::int2vector", doc_sql())
        self.assertIn("a.atttypid='bigint'::regtype AND a.attnotnull", doc_sql())
        self.assertIn("pg_get_expr(ad.adbin,ad.adrelid)='1'", doc_sql())

    def test_phat_lai_truoc_so_phien_va_ap_nhat_ky_sau_khoa(self):
        body = cac_ham()['chot_luot']
        self.assertLess(body.index('kq := cu_luot.ket_qua'), body.index('phien_moi := mask.phien_ban_luot('))
        for part in ('mask.ghi_cho_duyet(', 'mask.ghi_bi_danh_da_dung(', 'mask.dong_yeu_cau(',
                     'INSERT INTO mask.luot_chot', "muc->>'bi_danh'=ANY(cac_tam)"):
            self.assertIn(part, body)
        self.assertIn('PRIMARY KEY (yeu_cau_id,ma_luot)', doc_sql())
        self.assertNotRegex(body, r'\b(?:COMMIT|ROLLBACK)\b')

    def test_snapshot_hash_toan_vung_va_audit_ngoai_savepoint(self):
        body = cac_ham()['snapshot_luot']
        self.assertIn("'cum_cho_toan_vung',cum_cho", body)
        self.assertIn("sha256(convert_to(c.cum_chuan,'UTF8'))", body)
        self.assertIn("jsonb_build_object('nhom',c.nhom,'bi_danh',c.bi_danh_tam,'nguon','tam')", body)
        self.assertLess(body.index("EXCEPTION WHEN SQLSTATE 'P1200'"),
                        body.index('PERFORM loi.mask_kiem_toan_doc('))
        self.assertNotIn("p_yeu_cau,'TRA'", body)
        chot = cac_ham()['chot_luot']
        self.assertIn("p_yeu_cau,'TRA'", chot)

    def test_acl_chi_core_execute_ket_qua_co_rls_khong_tra_bang(self):
        sql = doc_sql()
        self.assertEqual(sql.count('SECURITY DEFINER SET search_path=pg_catalog,pg_temp'), 2)
        self.assertIn('SECURITY INVOKER SET search_path=pg_catalog,pg_temp', sql)
        self.assertIn('ALTER TABLE mask.luot_chot FORCE ROW LEVEL SECURITY', sql)
        self.assertIn('REVOKE ALL ON TABLE mask.luot_chot FROM PUBLIC CASCADE', sql)
        self.assertIn('REVOKE ALL ON FUNCTION %s FROM PUBLIC CASCADE', sql)
        self.assertIn('aclexplode(b.proacl)', sql)
        self.assertIn("IF b.proname IN ('snapshot_luot','chot_luot') THEN", sql)
        self.assertIn("'GRANT EXECUTE ON FUNCTION %s TO %I',ck,login", sql)
        self.assertNotRegex(sql, r'GRANT (?:SELECT|INSERT|UPDATE|DELETE|REFERENCES)')
        self.assertNotRegex(sql, r'\b(?:DROP|TRUNCATE|DELETE)\b')

    def test_khong_trung_bien_alias_case_co_ngoac_icu(self):
        for name, body in cac_ham().items():
            declarations = body.split('BEGIN', 1)[0]
            variables = set(re.findall(r'(?:DECLARE|;)\s*([a-z_]+)\s+', declarations))
            aliases = set(re.findall(r'\b(?:FROM|JOIN)\s+[a-z_]+\.[a-z_]+\s+([a-z_]+)\b', body))
            self.assertFalse(variables & aliases, (name, variables & aliases))
        self.assertIn('COLLATE "und-x-icu"', cac_ham()['chot_luot'])
        raw = SQL_PATH.read_bytes()
        broken = raw.replace(b'<>(CASE WHEN', b'<>CASE WHEN', 1).replace(b'ELSE chu_mask END)', b'ELSE chu_mask END', 1)
        self.assertNotEqual(raw, broken)
        with self.assertRaises(AssertionError):
            kiem_cau_truc_sql(broken)


class KhoLuotThuanTests(unittest.TestCase):
    def test_cum_cho_tai_lieu_khac_chi_hash_dung_lai_bi_danh(self):
        ma, tam = str(uuid4()), '[[MASKTAM-'+uuid4().hex+']]'
        goc = snapshot()
        bam = sha256(chuan_hoa(TEN).encode('utf-8')).hexdigest()
        goc['cum_cho_toan_vung'] = {bam: dict(nhom='CONG_TY', bi_danh=tam, nguon='tam')}
        self.assertNotIn(TEN, json.dumps(goc, ensure_ascii=False))
        kho = KhoLuot(goc, ma, loai='che')
        with tai_nguyen_demo():
            kq = che(VAN_BAN, None, kho)
        self.assertTrue(kq['gui_duoc'])
        self.assertIn(tam, kq['van_ban_da_che'])
        self.assertEqual(kq['cho_duyet']['so_cum_vua_them'], 0)
        self.assertEqual(kho.nhat_ky['bi_danh_tam_moi'], [])
        self.assertEqual(len(kho.nhat_ky['cum']), 1)
        self.assertTrue(kho.nhat_ky['cum'][0]['chi_gap_lai'])
        self.assertEqual(kho.nhat_ky['cum'][0]['bi_danh'], tam)
        self.assertEqual(kho.nhat_ky['cum_da_tra'], [bam])
        self.assertEqual(goc['danh_muc'], [])

    def test_cum_cho_khac_nhom_tra_dung_nhom_truoc_khi_cap_bi_danh(self):
        ma, tam = str(uuid4()), '[[MASKTAM-'+uuid4().hex+']]'
        goc = snapshot()
        bam = sha256(chuan_hoa(TEN).encode('utf-8')).hexdigest()
        goc['cum_cho_toan_vung'] = {bam: dict(nhom='CA_NHAN', bi_danh=tam, nguon='tam')}
        kho = KhoLuot(goc, ma, loai='che')
        with tai_nguyen_demo(), patch.object(kho, 'cap_bi_danh_tam') as cap:
            kq = che(VAN_BAN, None, kho)
        cap.assert_not_called()
        self.assertTrue(kq['gui_duoc'], kq)
        self.assertEqual(kq['bi_danh'], [dict(nhom='CA_NHAN', bi_danh=tam, nguon='tam')])
        self.assertEqual(kho.nhat_ky['bi_danh_tam_moi'], [])
        self.assertEqual(kho.nhat_ky['cum'], [dict(gia_tri=chuan_hoa(TEN), nhom='CA_NHAN',
                                                bi_danh=tam, chi_gap_lai=True)])
        self.assertEqual(goc['danh_muc'], [])

    def test_tra_cum_cho_chi_nap_cum_duoc_hoi_va_khong_de_len_danh_muc(self):
        ma, tam = str(uuid4()), '[[MASKTAM-'+uuid4().hex+']]'
        bam = sha256(chuan_hoa(TEN).encode('utf-8')).hexdigest()
        goc = snapshot()
        goc['cum_cho_toan_vung'] = {bam: dict(nhom='CA_NHAN', bi_danh=tam, nguon='tam')}
        kho = KhoLuot(goc, ma, loai='che')
        with kho.giao_dich():
            self.assertIsNone(kho.tra_bi_danh('DEMO chưa có'))
            self.assertEqual(kho.liet_ke_dinh_danh(), [])
            muc = kho.tra_bi_danh(TEN)
            self.assertEqual(muc, dict(nhom='CA_NHAN', bi_danh=tam, nguon='tam'))
            muc['nhom'] = 'DIA_CHI'
            self.assertEqual(kho.tra_bi_danh(TEN)['nhom'], 'CA_NHAN')
            kho.ghi_nhan_gap_lai(ma, TEN, 'CA_NHAN')
        goc['danh_muc'] = [dict(gia_tri=TEN, nhom='CONG_TY', bi_danh='[[KH-DEMO-01]]', nguon='chinh_thuc')]
        kho = KhoLuot(goc, ma, loai='che')
        with kho.giao_dich():
            self.assertEqual(kho.tra_bi_danh(TEN)['bi_danh'], '[[KH-DEMO-01]]')

    def test_ghi_cum_cho_khac_nhom_bo_bi_danh_vua_cap_va_dem_mot_lan(self):
        ma, tam = str(uuid4()), '[[MASKTAM-'+uuid4().hex+']]'
        goc = snapshot()
        bam = sha256(chuan_hoa(TEN).encode('utf-8')).hexdigest()
        goc['cum_cho_toan_vung'] = {bam: dict(nhom='CA_NHAN', bi_danh=tam, nguon='tam')}
        kho = KhoLuot(goc, ma, loai='che')
        with kho.giao_dich():
            muc, moi = kho.ghi_cho_duyet(TEN, 'CONG_TY', kho.cap_bi_danh_tam(), ma)
            self.assertFalse(moi)
            self.assertEqual(muc, dict(nhom='CA_NHAN', bi_danh=tam, nguon='tam'))
            kho.ghi_nhan_gap_lai(ma, TEN, muc['nhom'])
        self.assertEqual(kho.nhat_ky['bi_danh_tam_moi'], [])
        self.assertEqual(len(kho.nhat_ky['cum']), 1)

    def test_port_kho_cung_chu_ky(self):
        for name, func in Kho.__dict__.items():
            if not name.startswith('_') and callable(func):
                self.assertEqual(inspect.signature(getattr(KhoLuot, name)).parameters.keys(),
                                 inspect.signature(func).parameters.keys(), name)

    def test_nhat_ky_tao_cum_gap_lai_bi_danh_chi_mot_lan(self):
        ma = str(uuid4())
        goc = snapshot()
        kho = KhoLuot(goc, ma, loai='che')
        with kho.giao_dich():
            self.assertEqual(kho.tao_yeu_cau(), ma)
            tam = kho.cap_bi_danh_tam()
            muc, moi = kho.ghi_cho_duyet(TEN, 'CONG_TY', tam, ma)
            self.assertTrue(moi)
            self.assertNotIn('gia_tri', muc)
            for _ in range(3):
                kho.ghi_nhan_gap_lai(ma, chuan_hoa(TEN), 'CONG_TY')
                kho.ghi_bi_danh_da_dung(ma, [tam, tam])
            self.assertEqual(kho.tra_dinh_danh(tam.lower()), TEN)
        self.assertEqual(goc, snapshot())
        self.assertEqual(len(kho.nhat_ky['cum']), 1)
        self.assertEqual(kho.nhat_ky['bi_danh_tam_moi'], [tam])
        self.assertEqual(kho.nhat_ky['bi_danh_da_dung'], [tam])
        ban_sao = kho.nhat_ky
        ban_sao['cum'].clear()
        self.assertEqual(len(kho.nhat_ky['cum']), 1)

    def test_cum_tam_cu_va_bi_danh_tam_cu_cua_danh_muc_chinh(self):
        ma = str(uuid4())
        tam = '[[MASKTAM-'+uuid4().hex+']]'
        danh_muc = [dict(gia_tri=TEN, nhom='CONG_TY', bi_danh=tam, nguon='tam', so_lan_gap=3),
                    dict(gia_tri='Công ty DEMO Mặt Trời', nhom='CONG_TY', bi_danh='[[KH-DEMO-02]]',
                         bi_danh_tam='[[MASKTAM-'+uuid4().hex+']]', nguon='chinh_thuc')]
        kho = KhoLuot(snapshot(danh_muc, {'trang_thai': 'DANG_XU_LY'}), ma, loai='mo_che')
        with kho.giao_dich():
            kho.doc_yeu_cau(ma)
            for _ in range(2):
                kho.ghi_nhan_gap_lai(ma, chuan_hoa(TEN), 'CONG_TY')
            self.assertEqual(kho.tra_dinh_danh(danh_muc[1]['bi_danh_tam'].lower()), danh_muc[1]['gia_tri'])
            copy = kho.liet_ke_dinh_danh()
            copy[0]['gia_tri'] = 'DEMO khác'
            self.assertEqual(kho.tra_dinh_danh(tam), TEN)
            kho.dong_yeu_cau(ma)
        self.assertEqual(len(kho.nhat_ky['cum']), 1)
        self.assertTrue(kho.nhat_ky['cum'][0]['chi_gap_lai'])
        self.assertTrue(kho.nhat_ky['dong_yeu_cau'])

    def test_loi_trong_luot_huy_nhat_ky_khong_tai_su_dung(self):
        ma = str(uuid4())
        kho = KhoLuot(snapshot(), ma, loai='che')
        with self.assertRaisesRegex(RuntimeError, 'DEMO'), kho.giao_dich():
            kho.ghi_cho_duyet(TEN, 'CONG_TY', kho.cap_bi_danh_tam(), ma)
            raise RuntimeError('DEMO')
        with self.assertRaises(LoiLuotMask):
            _ = kho.nhat_ky
        with self.assertRaises(LoiLuotMask), kho.giao_dich():
            pass
        with self.assertRaises(LoiLuotMask):
            kho.tra_dinh_danh('[[KH-DEMO]]')

    def test_mo_bi_danh_tam_bi_danh_muc_chinh_thuc_che_khuat(self):
        ma = str(uuid4())
        tam = '[[MASKTAM-'+uuid4().hex+']]'
        snap = snapshot([dict(gia_tri=TEN, nhom='CONG_TY', bi_danh='[[KH-DEMO-01]]', nguon='chinh_thuc')],
                        {'trang_thai': 'DANG_XU_LY'})
        snap['bi_danh_bo_sung'] = {tam.lower(): TEN}
        kho = KhoLuot(snap, ma, loai='mo_che')
        kq = mo_che(tam.lower(), ma, kho)
        self.assertTrue(kq['mo_day_du'])
        self.assertEqual(kq['van_ban_da_mo_che'], TEN)
        self.assertEqual(kho.nhat_ky['cum'], [])
        self.assertEqual(kho.nhat_ky['bi_danh_da_tra'], [tam.lower()])

    def test_tu_choi_sai_ma_va_bi_danh_khong_cap(self):
        ma = str(uuid4())
        kho = KhoLuot(snapshot(), ma, loai='che')
        with kho.giao_dich():
            with self.assertRaises(LoiLuotMask):
                kho.ghi_cho_duyet(TEN, 'CONG_TY', '[[MASKTAM-'+'a'*32+']]', ma)
            with self.assertRaises(LoiLuotMask):
                kho.ghi_bi_danh_da_dung(str(uuid4()), [])


class DieuPhoiThuanTests(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.conn.info.transaction_status = 0
        self.token = "DEMO'); SELECT 'khong-chen"
        self.pn, self.tl, self.yc, self.luot = (uuid4() for _ in range(4))
        self.mask = Mask(self.conn, ma=MaBiMat(self.token), module='crm',
                         phap_nhan_id=self.pn, hanh_dong='CRM:TIEP_NHAN:XEM', tai_lieu_id=self.tl)
        self.snap = snapshot()
        self.calls = []

        def execute(sql, args):
            self.calls.append((sql, args))
            result = deepcopy(self.snap) if 'snapshot_luot(' in sql else json.loads(args[-1])
            cursor = MagicMock()
            cursor.fetchone.return_value = (result,)
            return cursor
        self.conn.execute.side_effect = execute

    def che(self, text=VAN_BAN):
        return self.mask.che(text, ma_yeu_cau=self.yc, ma_luot=self.luot)

    def test_che_that_chi_hai_rpc_va_chot_toan_nhat_ky(self):
        with tai_nguyen_demo():
            kq = self.che(TEN+'; '+TEN+'; ngày 07/11/2026; 1.000.000 VND.')
        self.assertTrue(kq['gui_duoc'], kq)
        self.assertNotIn(TEN, json.dumps(kq, ensure_ascii=False))
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(self.conn.transaction.call_count, 2)
        sql, args = self.calls[-1]
        self.assertIn('mask.chot_luot(', sql)
        self.assertEqual(args[:10], (self.token, 'crm', self.pn, 'CRM:TIEP_NHAN:XEM', self.tl,
                                    None, None, self.yc, self.luot, 'che'))
        self.assertNotIn(self.token, sql)
        self.assertEqual(sql.count('%s'), len(args))
        nhat_ky = json.loads(args[-2])
        self.assertEqual(len(nhat_ky['cum']), 1)
        self.assertEqual(len(nhat_ky['bi_danh_tam_moi']), 1)
        self.assertEqual(len(nhat_ky['bi_danh_da_dung']), 1)
        self.assertIn('07/11/2026', kq['van_ban_da_che'])
        self.assertIn('1.000.000 VND', kq['van_ban_da_che'])
        self.assertEqual(self.snap, snapshot())

    def test_loi_giua_luot_sau_khi_da_tao_cum_khong_goi_chot(self):
        from kho_tri_thuc.core import mask as module

        def hong(van_ban, da_biet, kho):
            with kho.giao_dich():
                ma = kho.tao_yeu_cau()
                kho.ghi_cho_duyet(TEN, 'CONG_TY', kho.cap_bi_danh_tam(), ma)
                kho.ghi_nhan_gap_lai(ma, chuan_hoa(TEN), 'CONG_TY')
                raise RuntimeError(self.token+TEN)
        with patch.object(module.che_van_ban, 'che', side_effect=hong), self.assertRaises(LoiLuotMask) as caught:
            self.che()
        self.assertEqual(len(self.calls), 1)
        self.assertIn('snapshot_luot(', self.calls[0][0])
        self.assertIsNone(caught.exception.__context__)
        self.assertIsNone(caught.exception.__cause__)
        self.assertNotIn(TEN, str(caught.exception))

    def test_kho_ram_khong_rpc_trong_khi_engine_dang_chay(self):
        from kho_tri_thuc.core import mask as module
        goc = module.che_van_ban.che

        def xu_ly(van_ban, da_biet, kho):
            self.assertEqual(len(self.calls), 1)
            kq = goc(van_ban, da_biet, kho)
            self.assertEqual(len(self.calls), 1)
            return kq
        with tai_nguyen_demo(), patch.object(module.che_van_ban, 'che', side_effect=xu_ly):
            self.che()

    def test_xung_dot_gioi_han_ba_lan_cung_ma_khong_cong_bo(self):
        class XungDotGia(RuntimeError):
            sqlstate = '40001'
        original = self.conn.execute.side_effect

        def execute(sql, args):
            if 'chot_luot(' in sql:
                raise XungDotGia(self.token+TEN)
            return original(sql, args)
        self.conn.execute.side_effect = execute
        with tai_nguyen_demo(), self.assertRaises(XungDotLuotMask) as caught:
            self.che()
        self.assertEqual(self.conn.execute.call_count, 6)
        self.assertEqual(len({c.args[1][7:10] for c in self.conn.execute.call_args_list}), 1)
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn(TEN, str(caught.exception))

    def test_xung_dot_lay_snapshot_moi_chay_lai_cung_ma_va_bi_danh_moi(self):
        class XungDotGia(RuntimeError):
            sqlstate = '40001'
        original = self.conn.execute.side_effect
        lan_chot, phien = [], []
        tam = '[[MASKTAM-'+uuid4().hex+']]'

        def execute(sql, args):
            if 'chot_luot(' in sql:
                lan_chot.append(deepcopy(args))
                if len(lan_chot) == 1:
                    self.snap['phien_ban'] = 'b'*64
                    self.snap['cum_cho_toan_vung'] = {
                        sha256(chuan_hoa(TEN).encode('utf-8')).hexdigest():
                        dict(nhom='CONG_TY', bi_danh=tam, nguon='tam')}
                    raise XungDotGia(self.token+TEN)
            else:
                phien.append(self.snap['phien_ban'])
            return original(sql, args)
        self.conn.execute.side_effect = execute
        with tai_nguyen_demo():
            kq = self.che()
        self.assertIn(tam, kq['van_ban_da_che'])
        self.assertEqual(self.conn.execute.call_count, 4)
        self.assertEqual(phien, ['a'*64, 'b'*64])
        self.assertEqual([a[7:10] for a in lan_chot], [(self.yc, self.luot, 'che')]*2)
        self.assertEqual([a[10] for a in lan_chot], phien)
        self.assertEqual(json.loads(lan_chot[-1][-2])['bi_danh_tam_moi'], [])

    def test_lock_timeout_o_snapshot_va_chot_lay_lai_snapshot_cung_ma(self):
        class HetGioKhoa(RuntimeError):
            sqlstate = '55P03'
        original = self.conn.execute.side_effect
        for cua in ('snapshot_luot(', 'chot_luot('):
            with self.subTest(cua=cua):
                self.conn.reset_mock()
                da_loi = False

                def execute(sql, args):
                    nonlocal da_loi
                    if cua in sql and not da_loi:
                        da_loi = True
                        raise HetGioKhoa(self.token+TEN)
                    return original(sql, args)
                self.conn.execute.side_effect = execute
                with tai_nguyen_demo():
                    self.assertTrue(self.che()['gui_duoc'])
                calls = self.conn.execute.call_args_list
                self.assertEqual(len(calls), 3 if cua == 'snapshot_luot(' else 4)
                self.assertEqual(sum('snapshot_luot(' in c.args[0] for c in calls), 2)
                self.assertEqual({c.args[1][7:10] for c in calls}, {(self.yc, self.luot, 'che')})

    def test_lock_timeout_chi_thu_ba_lan_khong_cong_bo(self):
        class HetGioKhoa(RuntimeError):
            sqlstate = '55P03'
        original = self.conn.execute.side_effect

        def execute(sql, args):
            if 'chot_luot(' in sql:
                raise HetGioKhoa(self.token+TEN)
            return original(sql, args)
        self.conn.execute.side_effect = execute
        with tai_nguyen_demo(), self.assertRaises(XungDotLuotMask) as caught:
            self.che()
        self.assertEqual(self.conn.execute.call_count, 6)
        self.assertEqual(len({c.args[1][7:10] for c in self.conn.execute.call_args_list}), 1)
        self.assertIsNone(caught.exception.__context__)
        self.assertIsNone(caught.exception.__cause__)
        self.assertNotIn(self.token, str(caught.exception))
        self.assertNotIn(TEN, str(caught.exception))

    def test_che_bi_chan_chot_dong_yeu_cau(self):
        with tai_nguyen_demo():
            kq = self.che(TEN+' [[MASKTAM-'+'a'*32+']]')
        self.assertFalse(kq['gui_duoc'])
        self.assertIsNone(kq['van_ban_da_che'])
        self.assertTrue(json.loads(self.calls[-1][1][-2])['dong_yeu_cau'])

    def test_loi_khong_phai_xung_dot_khong_retry(self):
        self.conn.execute.side_effect = RuntimeError(self.token+TEN)
        with self.assertRaises(LoiLuotMask):
            self.che()
        self.assertEqual(self.conn.execute.call_count, 1)

    def test_loi_commit_khong_cong_bo_ket_qua(self):
        self.conn.transaction.return_value.__exit__.side_effect = [False, RuntimeError(self.token+TEN)]
        with tai_nguyen_demo(), self.assertRaises(LoiLuotMask) as caught:
            self.che()
        self.assertEqual(self.conn.execute.call_count, 2)
        self.assertIsNone(caught.exception.__context__)
        self.assertIsNone(caught.exception.__cause__)

    def test_phat_lai_lay_cu_qua_chot_khong_chay_engine(self):
        self.snap = {'da_chot': True}
        cu = dict(ma_yeu_cau=str(self.yc), ma_luot=str(self.luot), van_ban_da_che='[[KH-DEMO]]')
        self.conn.execute.side_effect = None
        self.conn.execute.return_value.fetchone.side_effect = [(self.snap,), (cu,)]
        from kho_tri_thuc.core import mask as module
        with patch.object(module.che_van_ban, 'che') as engine:
            self.assertEqual(self.che(), cu)
        engine.assert_not_called()
        self.assertEqual(self.conn.execute.call_args.args[1][-3:], (None, None, None))

    def test_mo_che_that_tren_snapshot_toan_bang_va_chot_dong(self):
        bd = '[[KH-DEMO-001]]'
        self.snap = snapshot([dict(gia_tri=TEN, nhom='CONG_TY', bi_danh=bd, nguon='chinh_thuc')],
                             {'trang_thai': 'DANG_XU_LY'})
        kq = self.mask.mo_che(bd.lower(), str(self.yc), ma_luot=self.luot, dong_viec=True)
        self.assertEqual(kq['van_ban_da_mo_che'], TEN)
        self.assertEqual(kq['trang_thai_ma_yeu_cau'], 'DA_DONG')
        self.assertEqual(kq['ma_yeu_cau'], str(self.yc))
        self.assertTrue(json.loads(self.calls[-1][1][-2])['dong_yeu_cau'])

    def test_ket_qua_tra_ve_la_ket_qua_cua_chot(self):
        cu = {'da_xac_nhan': True}
        original = self.conn.execute.side_effect

        def execute(sql, args):
            if 'chot_luot(' in sql:
                cursor = MagicMock()
                cursor.fetchone.return_value = (cu,)
                return cursor
            return original(sql, args)
        self.conn.execute.side_effect = execute
        with tai_nguyen_demo():
            self.assertEqual(self.che(), cu)

    def test_tu_choi_transaction_cua_caller_truoc_khi_rpc(self):
        self.conn.info.transaction_status = 2
        with self.assertRaises(LoiLuotMask):
            self.che()
        self.conn.execute.assert_not_called()

    def test_khong_tu_ket_noi_khong_sql_bang_khong_goi_kho_cu_ghi_tung_lan(self):
        source = inspect.getsource(inspect.getmodule(Mask))
        self.assertNotIn('psycopg', source)
        self.assertNotRegex(source, r'\b(?:FROM|JOIN|UPDATE|INSERT INTO)\s+mask\.')
        self.assertNotIn('KhoMask(', source)


@unittest.skipUnless(os.environ.get('KHO_PG_DSN_TEST') and importlib.util.find_spec('psycopg'),
                     'CHUA_KIEM PG MASK-3D: chỉ lead chạy; worker chỉ thuần/mock')
class PostgresTests(unittest.TestCase):
    session = nen.PostgresTests.session
    cap_phien = nen.PostgresTests.cap_phien

    @classmethod
    def setUpClass(cls):
        nen.PostgresTests.setUpClass.__func__(cls)

    def setUp(self):
        # Không bọc transaction rollback ngoài: kiểm commit thật và hai kết nối.
        # CSDL kho_test_* riêng do fixture cũ quản lý; mọi tên/cụm đều DEMO.
        self.pn, self.ai, self.tai_lieu = self.fx.pn, self.fx.nd, self.fx.tai_lieu_id
        self.token = self.cap_phien()
        self.yc, self.luot = uuid4(), uuid4()
        self.ten = TEN+' '+''.join(chr(65+int(c, 16)) for c in uuid4().hex)
        self.van_ban = self.ten+'; thanh toán 1.000.000 VND ngày 07/11/2026.'
        self.mask = self.tao_mask()

    def tao_mask(self, *, token=None, tai_lieu=None):
        conn = self.pg.connect(**self.cac_thong_tin['core'], autocommit=True)
        self.addCleanup(conn.close)
        return Mask(conn, ma=MaBiMat(self.token if token is None else token), module='crm',
                    phap_nhan_id=self.pn, hanh_dong=self.g209.XEM,
                    tai_lieu_id=self.tai_lieu if tai_lieu is None else tai_lieu)

    def chuan_bi(self, mask=None, yc=None, luot=None):
        mask, yc, luot = mask or self.mask, yc or self.yc, luot or self.luot
        snap = mask._goi('snapshot', yc, luot, 'che')
        kho = KhoLuot(snap, yc, loai='che')
        with tai_nguyen_demo():
            kq = che(self.van_ban, None, kho)
        self.assertTrue(kq['gui_duoc'], kq)
        kq.update(ma_yeu_cau=str(yc), ma_luot=str(luot))
        return snap, kho.nhat_ky, kq

    def chot(self, snap, nhat_ky, kq, *, mask=None, yc=None, luot=None):
        return (mask or self.mask)._goi('chot', yc or self.yc, luot or self.luot, 'che',
            snap['phien_ban'], json.dumps(nhat_ky, ensure_ascii=False), json.dumps(kq, ensure_ascii=False))

    def dem(self):
        return self.conn.execute('SELECT so_lan_gap FROM mask.cho_duyet WHERE cum_chuan=%s AND la_demo',
                                 (chuan_hoa(self.ten),)).fetchone()

    def audit(self, yc=None):
        return [r[0] for r in self.conn.execute('SELECT to_jsonb(n) FROM loi.nhat_ky_kiem_toan n '
            "WHERE request_id=%s AND doi_tuong IN ('mask.dinh_danh.liet_ke','mask.dinh_danh.tra') ORDER BY id",
            (self.yc if yc is None else yc,)).fetchall()]

    def test_hai_tai_lieu_cung_cum_dung_lai_bi_danh_tam_chot_thanh_cong(self):
        with tai_nguyen_demo():
            a = self.mask.che(self.van_ban, ma_yeu_cau=self.yc, ma_luot=self.luot)
        tai_lieu_b, yc_b, luot_b = uuid4(), uuid4(), uuid4()
        with patch.object(self.fx, 'tai_lieu_id', tai_lieu_b), patch.object(self.fx, 'ma', self.fx._cap()):
            self.fx._tao()
        mask_b = self.tao_mask(tai_lieu=tai_lieu_b)
        b = self.chuan_bi(mask_b, yc_b, luot_b)
        bam = sha256(chuan_hoa(self.ten).encode('utf-8')).hexdigest()
        self.assertEqual(b[0]['cum_cho_toan_vung'][bam],
                         dict(nhom='CONG_TY', bi_danh=a['bi_danh'][0]['bi_danh'], nguon='tam'))
        self.assertNotIn(self.ten, json.dumps(b[0], ensure_ascii=False))
        self.assertEqual(b[1]['bi_danh_tam_moi'], [])
        self.assertEqual(self.chot(*b, mask=mask_b, yc=yc_b, luot=luot_b)['van_ban_da_che'], a['van_ban_da_che'])
        self.assertEqual(self.dem(), (2,))
        self.assertEqual(self.conn.execute('SELECT count(*) FROM mask.luot_chot WHERE yeu_cau_id IN (%s,%s)',
                                          (self.yc, yc_b)).fetchone(), (2,))

    def test_cum_cho_tai_lieu_khac_khac_nhom_khong_ket_mask_nhom(self):
        from kho_tri_thuc.core.kho_mask import KhoMask
        kho_cu = KhoMask(self.mask._ket_noi, ma=MaBiMat(self.token), module='crm',
                        phap_nhan_id=self.pn, hanh_dong=self.g209.XEM, tai_lieu_id=self.tai_lieu)
        with kho_cu.giao_dich():
            ma = kho_cu.tao_yeu_cau()
            muc, _ = kho_cu.ghi_cho_duyet(self.ten, 'CA_NHAN', kho_cu.cap_bi_danh_tam(), ma)
        tai_lieu_b, yc_b, luot_b = uuid4(), uuid4(), uuid4()
        with patch.object(self.fx, 'tai_lieu_id', tai_lieu_b), patch.object(self.fx, 'ma', self.fx._cap()):
            self.fx._tao()
        mask_b = self.tao_mask(tai_lieu=tai_lieu_b)
        b = self.chuan_bi(mask_b, yc_b, luot_b)
        self.assertEqual(b[1]['bi_danh_tam_moi'], [])
        self.assertEqual(b[1]['cum'][0]['nhom'], 'CA_NHAN')
        self.assertEqual(b[2]['bi_danh'], [dict(nhom='CA_NHAN', bi_danh=muc['bi_danh'], nguon='tam')])
        self.assertTrue(self.chot(*b, mask=mask_b, yc=yc_b, luot=luot_b)['gui_duoc'])
        self.assertEqual(self.dem(), (2,))
        self.assertEqual(self.conn.execute('SELECT count(*) FROM mask.luot_chot WHERE yeu_cau_id=%s',
                                          (yc_b,)).fetchone(), (1,))

    def test_phien_ban_bi_danh_chinh_va_tam_chi_tu_metadata_hang(self):
        with tai_nguyen_demo():
            kq = self.mask.che(self.van_ban, ma_yeu_cau=self.yc, ma_luot=self.luot)
        ten_chinh = self.ten+' Chi nhánh DEMO'
        d_id, d_xmin, bd = self.conn.execute(
            "INSERT INTO mask.dinh_danh(gia_tri,nhom,nguon,la_demo) VALUES(%s,'CONG_TY','DEMO',true) "
            'RETURNING id::text,xmin::text,bi_danh', (ten_chinh,)).fetchone()
        c_id, c_phien = self.conn.execute('SELECT id::text,phien_ban_anh_xa FROM mask.cho_duyet '
                                         'WHERE cum_chuan=%s AND la_demo', (chuan_hoa(self.ten),)).fetchone()
        snap = self.mask._goi('snapshot', uuid4(), uuid4(), 'che')
        phien = json.loads(snap['phien_ban'])
        for alias, gia_tri, metadata in ((bd, ten_chinh, 'd:'+d_id+':'+d_xmin),
                (kq['bi_danh'][0]['bi_danh'], self.ten, 'c:'+c_id+':'+str(c_phien))):
            with self.subTest(bi_danh=alias):
                bam_goc = sha256(gia_tri.encode('utf-8')).hexdigest()
                self.assertNotIn(bam_goc, phien['bi_danh'].values())
                self.assertNotIn(bam_goc, phien['cum'].values())
                self.assertEqual(phien['bi_danh'][alias.lower()], sha256(('bd:'+metadata).encode('utf-8')).hexdigest())
                khoa_cum = sha256(chuan_hoa(gia_tri).encode('utf-8')).hexdigest()
                self.assertEqual(phien['cum'][khoa_cum], sha256(metadata.encode('utf-8')).hexdigest())
        self.assertTrue(set(phien['bi_danh'].values()).isdisjoint(phien['cum'].values()))

    def test_audit_yeu_cau_moi_song_qua_savepoint_va_chi_tra_bi_danh_da_mo(self):
        a = self.chuan_bi()
        self.assertEqual([r['doi_tuong'] for r in self.audit()], ['mask.dinh_danh.liet_ke'])
        self.assertEqual(self.conn.execute('SELECT count(*) FROM mask.yeu_cau WHERE id=%s', (self.yc,)).fetchone(), (0,))
        kq = self.chot(*a)
        luot_mo = uuid4()
        self.mask._goi('snapshot', self.yc, luot_mo, 'mo_che')
        self.assertFalse(any(r['doi_tuong']=='mask.dinh_danh.tra' for r in self.audit()))
        self.mask.mo_che(kq['van_ban_da_che'], str(self.yc), ma_luot=luot_mo)
        rows = self.audit()
        self.assertEqual(sum(r['doi_tuong']=='mask.dinh_danh.tra' for r in rows), 1)
        for value in (self.ten, kq['bi_danh'][0]['bi_danh'], self.token):
            self.assertNotIn(value, json.dumps(rows, ensure_ascii=False))
        self.mask.mo_che('DEMO phát lại', str(self.yc), ma_luot=luot_mo)
        self.assertEqual(self.audit(), rows)

    def test_che_bi_chan_dong_yeu_cau_trong_cung_chot(self):
        with tai_nguyen_demo():
            kq = self.mask.che(self.van_ban+' [[MASKTAM-'+'a'*32+']]',
                               ma_yeu_cau=self.yc, ma_luot=self.luot)
        self.assertFalse(kq['gui_duoc'])
        self.assertEqual(self.conn.execute('SELECT trang_thai,dong_luc IS NOT NULL FROM mask.yeu_cau WHERE id=%s',
                                          (self.yc,)).fetchone(), ('DA_DONG', True))
        self.assertEqual(self.mask.che('DEMO phát lại', ma_yeu_cau=self.yc, ma_luot=self.luot), kq)

    def test_thay_doi_cum_khac_khong_lam_luot_dang_cho_xung_dot(self):
        a = self.chuan_bi()
        mask_b, yc_b, luot_b = self.tao_mask(), uuid4(), uuid4()
        with patch.object(self, 'van_ban', 'Công ty DEMO Khác '+''.join(chr(65+int(c, 16)) for c in uuid4().hex)):
            b = self.chuan_bi(mask_b, yc_b, luot_b)
        self.chot(*b, mask=mask_b, yc=yc_b, luot=luot_b)
        self.assertTrue(self.chot(*a)['gui_duoc'])
        self.assertEqual(self.dem(), (1,))

    def test_chi_tang_so_lan_gap_khong_lam_snapshot_cung_cum_xung_dot(self):
        with tai_nguyen_demo():
            self.mask.che(self.van_ban, ma_yeu_cau=self.yc, ma_luot=self.luot)
        yc_b, luot_b, yc_c, luot_c = (uuid4() for _ in range(4))
        a = self.chuan_bi(self.mask, yc_b, luot_b)
        b = self.chuan_bi(self.mask, yc_c, luot_c)
        self.chot(*a, yc=yc_b, luot=luot_b)
        self.assertTrue(self.chot(*b, yc=yc_c, luot=luot_c)['gui_duoc'])
        self.assertEqual(self.dem(), (3,))

    def test_bi_danh_da_tra_doi_gia_tri_phai_xung_dot(self):
        self.conn.execute("INSERT INTO mask.dinh_danh(gia_tri,nhom,nguon,la_demo) VALUES(%s,'CONG_TY','DEMO',true)",
                          (self.ten,))
        with tai_nguyen_demo():
            kq = self.mask.che(self.van_ban, ma_yeu_cau=self.yc, ma_luot=self.luot)
        luot = uuid4()
        snap = self.mask._goi('snapshot', self.yc, luot, 'mo_che')
        kho = KhoLuot(snap, self.yc, loai='mo_che')
        mo = mo_che(kq['van_ban_da_che'], str(self.yc), kho)
        mo.update(ma_yeu_cau=str(self.yc), ma_luot=str(luot))
        self.conn.execute('UPDATE mask.dinh_danh SET gia_tri=%s WHERE gia_tri=%s AND la_demo',
                          (self.ten+' DEMO đổi', self.ten))
        with self.assertRaises(XungDotLuotMask):
            self.mask._goi('chot', self.yc, luot, 'mo_che', snap['phien_ban'],
                           json.dumps(kho.nhat_ky, ensure_ascii=False), json.dumps(mo, ensure_ascii=False))

    def test_bi_danh_tam_da_tra_doi_goc_cung_cum_phai_xung_dot(self):
        with tai_nguyen_demo():
            kq = self.mask.che(self.van_ban, ma_yeu_cau=self.yc, ma_luot=self.luot)
        luot = uuid4()
        snap = self.mask._goi('snapshot', self.yc, luot, 'mo_che')
        kho = KhoLuot(snap, self.yc, loai='mo_che')
        mo = mo_che(kq['van_ban_da_che'], str(self.yc), kho)
        mo.update(ma_yeu_cau=str(self.yc), ma_luot=str(luot))
        truoc = self.conn.execute('SELECT phien_ban_anh_xa FROM mask.cho_duyet '
            'WHERE cum_chuan=%s AND la_demo', (chuan_hoa(self.ten),)).fetchone()[0]
        self.conn.execute('UPDATE mask.cho_duyet SET cum_goc=%s WHERE cum_chuan=%s AND la_demo',
                          (self.ten.swapcase(), chuan_hoa(self.ten)))
        self.assertEqual(self.conn.execute('SELECT phien_ban_anh_xa FROM mask.cho_duyet '
            'WHERE cum_chuan=%s AND la_demo', (chuan_hoa(self.ten),)).fetchone(), (truoc+1,))
        with self.assertRaises(XungDotLuotMask):
            self.mask._goi('chot', self.yc, luot, 'mo_che', snap['phien_ban'],
                           json.dumps(kho.nhat_ky, ensure_ascii=False), json.dumps(mo, ensure_ascii=False))

    def test_cua_chot_gioi_han_cho_khoa_va_rollback_khong_ghi(self):
        a = self.chuan_bi()
        conn = self.mask._ket_noi
        truoc = conn.execute('SHOW lock_timeout').fetchone()
        with self.conn.transaction():
            self.conn.execute('LOCK TABLE mask.cho_duyet IN EXCLUSIVE MODE')
            with self.assertRaises(XungDotLuotMask):
                self.chot(*a)
        self.assertEqual(conn.execute('SHOW lock_timeout').fetchone(), truoc)
        self.assertIsNone(self.dem())
        self.assertEqual(self.conn.execute('SELECT count(*) FROM mask.luot_chot WHERE yeu_cau_id=%s',
                                          (self.yc,)).fetchone(), (0,))

    def test_lock_timeout_that_retry_toan_luot_sau_khi_tha_khoa(self):
        da_khoa, tha_khoa = Event(), Event()
        calls, xung_dot, tac_vu = [], [], []
        original = self.mask._goi

        def giu_khoa():
            with self.conn.transaction():
                self.conn.execute('LOCK TABLE mask.cho_duyet IN EXCLUSIVE MODE')
                da_khoa.set()
                if not tha_khoa.wait(timeout=10):
                    raise AssertionError('DEMO chưa nhả khóa thử nghiệm')

        with ThreadPoolExecutor(max_workers=1) as pool:
            def goi(*args):
                calls.append(args[:4])
                if args[0] == 'chot' and not tac_vu:
                    tac_vu.append(pool.submit(giu_khoa))
                    self.assertTrue(da_khoa.wait(timeout=10))
                try:
                    return original(*args)
                except XungDotLuotMask:
                    xung_dot.append(True)
                    tha_khoa.set()
                    tac_vu[0].result(timeout=10)
                    self.assertIsNone(self.dem())
                    raise
            try:
                with tai_nguyen_demo(), patch.object(self.mask, '_goi', side_effect=goi):
                    kq = self.mask.che(self.van_ban, ma_yeu_cau=self.yc, ma_luot=self.luot)
            finally:
                tha_khoa.set()
                if tac_vu:
                    tac_vu[0].result(timeout=10)
        self.assertTrue(kq['gui_duoc'])
        self.assertEqual(xung_dot, [True])
        self.assertEqual([c[0] for c in calls], ['snapshot', 'chot', 'snapshot', 'chot'])
        self.assertEqual({c[1:] for c in calls}, {(self.yc, self.luot, 'che')})
        self.assertEqual(self.dem(), (1,))
        self.assertEqual(self.conn.execute('SELECT count(*) FROM mask.luot_chot WHERE yeu_cau_id=%s',
                                          (self.yc,)).fetchone(), (1,))

    def test_snapshot_va_loi_giua_luot_khong_ghi_ke_ca_ma_yeu_cau(self):
        from kho_tri_thuc.core import mask as module

        def hong(van_ban, da_biet, kho):
            with kho.giao_dich():
                ma = kho.tao_yeu_cau()
                kho.ghi_cho_duyet(self.ten, 'CONG_TY', kho.cap_bi_danh_tam(), ma)
                raise RuntimeError('DEMO lỗi giữa lượt')
        with patch.object(module.che_van_ban, 'che', side_effect=hong), self.assertRaises(LoiLuotMask):
            self.mask.che(self.van_ban, ma_yeu_cau=self.yc, ma_luot=self.luot)
        self.assertEqual(self.conn.execute('SELECT count(*) FROM mask.yeu_cau WHERE id=%s', (self.yc,)).fetchone(), (0,))
        self.assertIsNone(self.dem())
        self.assertEqual(self.conn.execute('SELECT count(*) FROM mask.luot_chot WHERE yeu_cau_id=%s', (self.yc,)).fetchone(), (0,))

    def test_khu_hoi_che_mo_che_demo_giu_tien_ngay_va_dong(self):
        with tai_nguyen_demo():
            kq = self.mask.che(self.van_ban, ma_yeu_cau=self.yc, ma_luot=self.luot)
        self.assertTrue(kq['gui_duoc'], kq)
        self.assertNotIn(self.ten, json.dumps(kq, ensure_ascii=False))
        mo = self.mask.mo_che(kq['van_ban_da_che'], str(self.yc), dong_viec=True)
        self.assertEqual(mo['van_ban_da_mo_che'], self.van_ban)
        self.assertEqual(mo['trang_thai_ma_yeu_cau'], 'DA_DONG')
        self.assertEqual(self.dem(), (1,))

    def test_hai_luot_dong_thoi_cung_cum_mot_xung_dot_retry_khong_dem_doi(self):
        mask_b, yc_b, luot_b = self.tao_mask(), uuid4(), uuid4()
        a = self.chuan_bi()
        b = self.chuan_bi(mask_b, yc_b, luot_b)
        hen = Barrier(2)

        def ghi(thu):
            hen.wait(timeout=10)
            try:
                if thu == 0:
                    return self.chot(*a)
                return self.chot(*b, mask=mask_b, yc=yc_b, luot=luot_b)
            except XungDotLuotMask:
                return 'XUNG_DOT'
        with ThreadPoolExecutor(max_workers=2) as pool:
            kq = list(pool.map(ghi, range(2)))
        self.assertEqual(kq.count('XUNG_DOT'), 1)
        self.assertEqual(self.dem(), (1,))
        thua = kq.index('XUNG_DOT')
        mask, yc, luot = (self.mask, self.yc, self.luot) if thua == 0 else (mask_b, yc_b, luot_b)
        self.assertEqual(self.conn.execute('SELECT count(*) FROM mask.yeu_cau WHERE id=%s', (yc,)).fetchone(), (0,))
        with tai_nguyen_demo():
            retry = mask.che(self.van_ban, ma_yeu_cau=yc, ma_luot=luot)
        self.assertTrue(retry['gui_duoc'])
        self.assertEqual(self.dem(), (2,))
        self.assertEqual(mask.che('DEMO phát lại', ma_yeu_cau=yc, ma_luot=luot), retry)
        self.assertEqual(self.dem(), (2,))
        self.assertEqual(self.conn.execute('SELECT count(*) FROM mask.luot_chot WHERE yeu_cau_id IN (%s,%s)',
                                          (self.yc, yc_b)).fetchone(), (2,))

    def test_phat_lai_tra_cu_ca_khi_da_dong_khong_tang_dem(self):
        with tai_nguyen_demo():
            kq = self.mask.che(self.van_ban, ma_yeu_cau=self.yc, ma_luot=self.luot)
        luot_mo = uuid4()
        mo = self.mask.mo_che(kq['van_ban_da_che'], str(self.yc), dong_viec=True, ma_luot=luot_mo)
        self.assertEqual(self.mask.che('DEMO khác', ma_yeu_cau=self.yc, ma_luot=self.luot), kq)
        self.assertEqual(self.mask.mo_che('DEMO khác', str(self.yc), ma_luot=luot_mo), mo)
        self.assertEqual(self.dem(), (1,))
        self.assertEqual(self.conn.execute('SELECT count(*) FROM mask.luot_chot WHERE yeu_cau_id=%s', (self.yc,)).fetchone(), (2,))
        with self.assertRaises(LoiLuotMask):
            self.mask.mo_che(kq['van_ban_da_che'], str(self.yc))

    def test_mo_bi_danh_tam_cu_sau_khi_co_danh_muc_chinh_thuc_cung_cum(self):
        with tai_nguyen_demo():
            kq = self.mask.che(self.van_ban, ma_yeu_cau=self.yc, ma_luot=self.luot)
        self.conn.execute("INSERT INTO mask.dinh_danh(gia_tri,nhom,nguon,la_demo) VALUES(%s,'CONG_TY','DEMO',true)",
                          (self.ten,))
        mo = self.mask.mo_che(kq['van_ban_da_che'], str(self.yc))
        self.assertTrue(mo['mo_day_du'])
        self.assertEqual(mo['van_ban_da_mo_che'], self.van_ban)

    def test_loi_cuoi_chot_rollback_ca_cum_dem_tham_chieu_va_yeu_cau(self):
        snap, nhat_ky, kq = self.chuan_bi()
        nhat_ky['bi_danh_da_dung'].append('[[KH-DEMO-KHONG-TON-TAI]]')
        with self.assertRaises(LoiLuotMask):
            self.chot(snap, nhat_ky, kq)
        self.assertIsNone(self.dem())
        self.assertEqual(self.conn.execute('SELECT count(*) FROM mask.yeu_cau WHERE id=%s', (self.yc,)).fetchone(), (0,))
        self.assertEqual(self.conn.execute('SELECT count(*) FROM mask.luot_chot WHERE yeu_cau_id=%s', (self.yc,)).fetchone(), (0,))

    def test_thay_doi_qua_119_lam_snapshot_xung_dot(self):
        snap, nhat_ky, kq = self.chuan_bi()
        # Cửa cũ vẫn được dùng bởi lát B; phiên bản phải bắt được thay đổi này.
        from kho_tri_thuc.core.kho_mask import KhoMask
        kho_cu = KhoMask(self.mask._ket_noi, ma=MaBiMat(self.token), module='crm',
                        phap_nhan_id=self.pn, hanh_dong=self.g209.XEM, tai_lieu_id=self.tai_lieu)
        with kho_cu.giao_dich():
            ma = kho_cu.tao_yeu_cau()
            kho_cu.ghi_cho_duyet(self.ten, 'CONG_TY', kho_cu.cap_bi_danh_tam(), ma)
        with self.assertRaises(XungDotLuotMask):
            self.chot(snap, nhat_ky, kq)
        self.assertEqual(self.dem(), (1,))

    def test_ca_hai_cua_tu_choi_phien_gia_va_phat_lai_sau_thu_hoi_quyen(self):
        snap, nhat_ky, kq = self.chuan_bi()
        self.chot(snap, nhat_ky, kq)
        for loai in ('snapshot', 'chot'):
            mask = self.tao_mask(token='DEMO phiên giả')
            values = () if loai == 'snapshot' else (None, None, None)
            with self.assertRaises(LoiLuotMask):
                mask._goi(loai, self.yc, self.luot, 'che', *values)
        # Quyền nội dung gốc bị thu hồi: kết quả đã lưu cũng không được đọc lại.
        with self.conn.transaction(force_rollback=True):
            self.conn.execute('INSERT INTO loi_tai_lieu.quyen_tai_lieu'
                '(phap_nhan_id,tai_lieu_id,nguoi_dung_id,bien_the,hanh_dong,so_phien_ban,cho_phep,tao_boi) '
                "VALUES(%s,%s,%s,'goc','XEM',1,false,%s)", (self.pn, self.tai_lieu, self.ai, self.ai))
            # Cùng connection để nhìn thấy sự kiện chưa commit, nhưng giả lập
            # đúng login bằng session(); gọi SQL trực tiếp, không điều phối.
            with self.assertRaises(self.pg.errors.InsufficientPrivilege), self.session():
                self.conn.execute('SELECT mask.chot_luot('+','.join(['%s']*13)+')',
                    (self.token, 'crm', self.pn, self.g209.XEM, self.tai_lieu, None, None,
                     self.yc, self.luot, 'che', None, None, None))

    def test_hai_cua_khoi_phuc_guc_ca_khi_loi_va_phat_lai(self):
        conn = self.mask._ket_noi
        conn.execute("SELECT set_config('ktt.mask_la_demo','false',false)")
        snap, nhat_ky, kq = self.chuan_bi()
        self.assertEqual(conn.execute("SELECT current_setting('ktt.mask_la_demo')").fetchone(), ('false',))
        self.chot(snap, nhat_ky, kq)
        self.mask.che('DEMO phát lại', ma_yeu_cau=self.yc, ma_luot=self.luot)
        self.assertEqual(conn.execute("SELECT current_setting('ktt.mask_la_demo')").fetchone(), ('false',))
        with self.assertRaises(LoiLuotMask):
            self.mask.mo_che('', str(uuid4()))
        self.assertEqual(conn.execute("SELECT current_setting('ktt.mask_la_demo')").fetchone(), ('false',))

    def test_acl_chi_core_execute_khong_doc_ket_qua_bang(self):
        core = self.cac_thong_tin['core']['user']
        for name, signature in PUBLIC.items():
            sig = 'mask.'+name+'('+signature+')'
            self.assertTrue(self.conn.execute("SELECT has_function_privilege(%s,%s,'EXECUTE')", (core, sig)).fetchone()[0])
            for role in (self.module_login, self.tien_to+'vai_chay_mask'):
                self.assertFalse(self.conn.execute("SELECT has_function_privilege(%s,%s,'EXECUTE')", (role, sig)).fetchone()[0])
        self.assertFalse(self.conn.execute("SELECT has_function_privilege(%s,'mask.phien_ban_luot(uuid)','EXECUTE')", (core,)).fetchone()[0])
        self.assertFalse(self.conn.execute("SELECT has_function_privilege(%s,'mask.giu_phien_anh_xa()','EXECUTE')", (core,)).fetchone()[0])
        for role in (core, self.module_login, self.tien_to+'vai_chay_mask'):
            self.assertFalse(self.conn.execute("SELECT has_table_privilege(%s,'mask.luot_chot','SELECT')", (role,)).fetchone()[0])

    def test_chay_lai_120_khong_doi_du_lieu_oid_acl_policy(self):
        snap, nhat_ky, kq = self.chuan_bi()
        self.chot(snap, nhat_ky, kq)

        def chup():
            return [self.conn.execute('SELECT * FROM mask.'+name+' ORDER BY 1,2').fetchall()
                    for name in ('dinh_danh', 'cho_duyet', 'yeu_cau', 'luot_chot')] + [
                self.conn.execute('SELECT p.oid,p.proowner,p.proacl,pg_get_functiondef(p.oid) FROM pg_proc p '
                    "WHERE p.pronamespace='mask'::regnamespace ORDER BY p.oid").fetchall(),
                self.conn.execute("SELECT * FROM pg_policy WHERE polrelid='mask.luot_chot'::regclass ORDER BY oid").fetchall()]
        truoc = chup()
        self.conn.execute(doc_sql())
        self.conn.execute(doc_sql())
        self.assertEqual(chup(), truoc)

    def test_chay_lai_thu_acl_la_ca_quyen_cot_va_guard_sai_tien_to(self):
        for name, signature in PUBLIC.items():
            self.conn.execute(self.sql.SQL('GRANT EXECUTE ON FUNCTION mask.'+name+'('+signature+') TO {} WITH GRANT OPTION')
                              .format(self.sql.Identifier(self.module_login)))
        self.conn.execute(self.sql.SQL('GRANT SELECT (ket_qua) ON TABLE mask.luot_chot TO {}')
                          .format(self.sql.Identifier(self.module_login)))
        self.conn.execute(doc_sql())
        for name, signature in PUBLIC.items():
            self.assertFalse(self.conn.execute("SELECT has_function_privilege(%s,%s,'EXECUTE')",
                (self.module_login, 'mask.'+name+'('+signature+')')).fetchone()[0])
        self.assertFalse(self.conn.execute("SELECT has_column_privilege(%s,'mask.luot_chot','ket_qua','SELECT')",
                                          (self.module_login,)).fetchone()[0])
        with self.assertRaises(self.pg.errors.RaiseException) as caught, self.conn.transaction():
            self.conn.execute("SELECT set_config('kho_tri_thuc.tien_to_vai','DEMO sai',true)")
            self.conn.execute(doc_sql())
        self.assertEqual(caught.exception.diag.message_primary, 'MASK_LUOT_SAI_DICH')


if __name__ == '__main__':
    unittest.main()
