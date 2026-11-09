"""OCR-CR-2: cửa Core thuần/mock; PG opt-in do lead chạy, không mở dịch vụ."""
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import os
import traceback
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from kho_tri_thuc.core import kenh_engine as kenh, ocr_doi_chieu as ocr, phien, viec
from kho_tri_thuc.sdk_core.engine import LoiEngine
from tests import test_g2_32_e1 as nen


BAM = 'a' * 64
TEN_TEP = 'Hồ sơ DEMO cần đối chiếu.pdf'


class LoiSQLGia(RuntimeError):
    def __init__(self, sqlstate):
        self.sqlstate = sqlstate
        super().__init__(BAM + ' / ' + TEN_TEP)


def lease_demo():
    return viec.GiuViec(uuid4(), uuid4(), uuid4(), uuid4(), 'crm', 'CRM:DEMO:LAP',
        uuid4(), 7, datetime.now(timezone.utc) + timedelta(minutes=2), phien.MaBiMat('DEMO_LEASE'))


class KetNoiGia:
    def __init__(self):
        self.info = SimpleNamespace(transaction_status=0)
        self.calls, self.events = [], []
        self.raw, self.loi, self.loi_commit = None, None, False
        self.dong_dict = False

    @contextmanager
    def transaction(self):
        self.events.append('begin')
        self.info.transaction_status = 2
        try:
            yield
            if self.loi_commit:
                raise RuntimeError(BAM + ' / ' + TEN_TEP)
            self.events.append('commit')
        except BaseException:
            self.events.append('rollback')
            raise
        finally:
            self.info.transaction_status = 0

    def execute(self, sql, args=None):
        if self.info.transaction_status != 2:
            raise AssertionError('SQL phải nằm trong transaction')
        self.calls.append((sql, args))
        if sql.startswith('SELECT loi_tai_lieu.') and self.loi:
            raise self.loi
        row = {'r': deepcopy(self.raw)} if self.dong_dict else (deepcopy(self.raw),)
        return SimpleNamespace(fetchone=lambda: row)


class OCRDoiChieuCoreTests(unittest.TestCase):
    def setUp(self):
        self.lease, self.conn, self.giu_id = lease_demo(), KetNoiGia(), uuid4()
        self.ctx = ocr.NguCanhOCR.tu_lease(self.lease)
        self.service = ocr.OCRDoiChieu(self.conn, ngu_canh=self.ctx)
        self.raw = dict(giu_trang_id=str(self.giu_id), viec_id=str(self.lease.viec_id),
            ma_tuong_quan='DEMO_OCR:001', so_trang=3, trang_thai='GIU', phien_ban=1)
        self.conn.raw = deepcopy(self.raw)

    def giu(self, **doi):
        return self.service.giu_luot(**{**dict(ma_bam=BAM, ma_tuong_quan='DEMO_OCR:001',
            so_trang=3, giu_trang_id=self.giu_id), **doi})

    def chot(self, **doi):
        return self.service.chot_luot(**{**dict(ma_bam=BAM, giu_trang_id=self.giu_id,
            phien_ban=1, trang_thai_cu=ocr.TrangThaiLuotOCR.GIU,
            trang_thai_moi=ocr.TrangThaiLuotOCR.CHUA_RO), **doi})

    def kiem_loi(self, ma, ham):
        with self.assertRaises(ocr.LoiOCRDoiChieu) as caught:
            ham()
        error = caught.exception
        self.assertEqual(error.ma, ma)
        self.assertIsNone(error.__context__)
        self.assertIsNone(error.__cause__)
        self.assertFalse(error.thu_lai_duoc)
        detail = str(error) + repr(error) + ''.join(traceback.format_exception(error))
        self.assertNotIn(BAM, detail)
        self.assertNotIn(TEN_TEP, detail)
        return error

    def test_ngu_canh_lay_tu_lease_khong_tu_payload(self):
        self.assertEqual((self.ctx.phap_nhan_id, self.ctx.module, self.ctx.viec_id, self.ctx.the_he),
            (self.lease.phap_nhan_id, self.lease.module, self.lease.viec_id, self.lease.the_he))
        for field in ('phap_nhan_id', 'module', 'viec_id', 'the_he', 'ngu_canh'):
            with self.subTest(field=field), self.assertRaises(TypeError):
                self.giu(**{field: 'DEMO_GIA_MAO'})
        self.assertEqual(self.conn.calls, [])
        with self.assertRaises(FrozenInstanceError):
            self.ctx.module = 'gia_mao'

    def test_context_dict_khong_duoc_coi_la_lease_da_xac_minh(self):
        self.kiem_loi('OCR_LUOT_DAU_VAO', lambda: ocr.NguCanhOCR.tu_lease({}))
        self.kiem_loi('OCR_LUOT_DAU_VAO', lambda: ocr.OCRDoiChieu(self.conn, ngu_canh={}))
        self.kiem_loi('OCR_LUOT_DAU_VAO', lambda: replace(self.ctx, the_he=True))

    def test_giu_dung_sql_context_va_chi_tra_sau_commit(self):
        result = self.giu()
        self.assertIsInstance(result, ocr.KetQuaLuotOCR)
        self.assertIs(result.trang_thai, ocr.TrangThaiLuotOCR.GIU)
        self.assertEqual(result.giu_trang_id, self.giu_id)
        self.assertTrue(result.dang_chan_gui)
        self.assertEqual(self.conn.calls, [
            ('SET TRANSACTION ISOLATION LEVEL READ COMMITTED', None),
            ('SELECT loi_tai_lieu.ocr_giu_luot(%s,%s,%s,%s,%s,%s) AS r',
             (self.ctx.phap_nhan_id, BAM, self.ctx.viec_id, 'DEMO_OCR:001', 3, self.giu_id))])
        self.assertEqual(self.conn.events, ['begin', 'commit'])
        self.assertEqual(self.conn.info.transaction_status, 0)
        with self.assertRaises(FrozenInstanceError):
            result.phien_ban = 9

    def test_dang_xu_ly_hoac_chua_ro_bi_chan_khong_tu_thu_lai(self):
        # SQL 126 trả P0001 cho cả hai dấu bền và tranh khóa cùng pháp nhân/băm.
        for state in ('DANG_XU_LY', 'CHUA_RO'):
            with self.subTest(state=state):
                self.conn.loi = LoiSQLGia('P0001')
                before = len(self.conn.calls)
                error = self.kiem_loi('OCR_LUOT_DANG_BI_CHAN', self.giu)
                self.assertEqual((error.http_status, error.sqlstate), (409, 'P0001'))
                self.assertEqual(len(self.conn.calls) - before, 2)
                self.assertEqual(self.conn.events[-1], 'rollback')

    def test_chot_cas_chua_ro_va_trang_thai_cuoi(self):
        for old, new, version in (('GIU', 'CHUA_RO', 1), ('GIU', 'DA_TIEU_TRANG', 1),
                ('GIU', 'HOAN_TRANG', 1), ('CHUA_RO', 'DA_TIEU_TRANG', 2),
                ('CHUA_RO', 'HOAN_TRANG', 2)):
            with self.subTest(old=old, new=new):
                self.conn.raw = dict(self.raw, trang_thai=new, phien_ban=version + 1)
                result = self.chot(phien_ban=version, trang_thai_cu=old, trang_thai_moi=new)
                self.assertEqual((result.trang_thai, result.phien_ban), (new, version + 1))
                self.assertEqual(self.conn.calls[-1], (
                    'SELECT loi_tai_lieu.ocr_chot_luot(%s,%s,%s,%s,%s,%s) AS r',
                    (self.ctx.phap_nhan_id, BAM, self.giu_id, version, old, new)))
                self.assertEqual(self.conn.events[-1], 'commit')

    def test_chot_sai_phien_ban_hoac_trang_thai_sql_la_xung_dot(self):
        self.conn.loi = LoiSQLGia('40001')
        error = self.kiem_loi('OCR_LUOT_XUNG_DOT', self.chot)
        self.assertEqual((error.http_status, error.sqlstate), (409, '40001'))
        self.assertEqual(self.conn.events, ['begin', 'rollback'])

    def test_chot_trang_thai_khong_hop_le_bi_xung_dot_truoc_sql(self):
        for old, new in (('CHUA_RO', 'CHUA_RO'), ('HOAN_TRANG', 'DA_TIEU_TRANG'),
                         ('GIU', 'GIU'), ('SAI', 'HOAN_TRANG'), ('GIU', TEN_TEP)):
            with self.subTest(old=old, new=new):
                self.kiem_loi('OCR_LUOT_XUNG_DOT', lambda: self.chot(
                    trang_thai_cu=old, trang_thai_moi=new))
        self.assertEqual(self.conn.calls, [])

    def test_doc_chua_co_luot_tra_none_va_commit(self):
        self.conn.raw = None
        self.assertIsNone(self.service.doc_trang_thai(ma_bam=BAM))
        self.assertEqual(self.conn.calls[-1], ('SELECT loi_tai_lieu.ocr_doc_trang_thai(%s,%s) AS r',
            (self.ctx.phap_nhan_id, BAM)))
        self.assertEqual(self.conn.events, ['begin', 'commit'])

    def test_doc_trang_thai_co_kieu_khong_cap_quyen_gui_lai(self):
        for state in ocr.TrangThaiLuotOCR:
            with self.subTest(state=state):
                # Trạng thái chặn có thể thuộc việc/module khác cùng pháp nhân.
                self.conn.raw = dict(self.raw, viec_id=str(uuid4()), trang_thai=state.value)
                self.conn.dong_dict = True
                result = self.service.doc_trang_thai(ma_bam=BAM)
                self.assertIs(result.trang_thai, state)
                self.assertEqual(result.dang_chan_gui, state in (
                    ocr.TrangThaiLuotOCR.GIU, ocr.TrangThaiLuotOCR.CHUA_RO))
                self.assertFalse(hasattr(result, 'gui_duoc'))

    def test_doi_chieu_sau_lease_het_han_do_caller_core_cap_quyen(self):
        lease = replace(self.lease, giu_den=datetime.now(timezone.utc) - timedelta(days=90))
        service = ocr.OCRDoiChieu(self.conn, ngu_canh=ocr.NguCanhOCR.tu_lease(lease))
        self.conn.raw = dict(self.raw, trang_thai='CHUA_RO', phien_ban=2)
        self.assertEqual(service.doc_trang_thai(ma_bam=BAM).trang_thai, 'CHUA_RO')
        self.conn.raw = dict(self.raw, trang_thai='HOAN_TRANG', phien_ban=3)
        self.assertEqual(service.chot_luot(ma_bam=BAM, giu_trang_id=self.giu_id, phien_ban=2,
            trang_thai_cu=ocr.TrangThaiLuotOCR.CHUA_RO,
            trang_thai_moi=ocr.TrangThaiLuotOCR.HOAN_TRANG).trang_thai, 'HOAN_TRANG')

    def test_quyen_42501_va_cac_loi_sql_chi_tra_ma_co_dinh(self):
        for code, ma in (('42501', '42501'), ('22023', 'OCR_LUOT_DAU_VAO'),
                        ('25000', 'OCR_LUOT_GIAO_DICH'), ('55P03', 'OCR_LUOT_DANG_BI_CHAN'),
                        ('40P01', 'OCR_LUOT_XUNG_DOT'), ('XX000', 'OCR_LUOT_THAT_BAI')):
            with self.subTest(code=code):
                self.conn.loi = LoiSQLGia(code)
                error = self.kiem_loi(ma, self.giu)
                if code == '42501':
                    self.assertEqual((error.http_status, error.sqlstate), (403, '42501'))

    def test_loi_driver_khong_co_sqlstate_khong_lo_bam_ten_tep(self):
        self.conn.loi = RuntimeError(BAM + ' / ' + TEN_TEP)
        self.kiem_loi('OCR_LUOT_THAT_BAI', self.giu)

    def test_commit_loi_khong_cong_bo_ket_qua_hoac_tu_thu_lai(self):
        self.conn.loi_commit = True
        self.kiem_loi('OCR_LUOT_THAT_BAI', self.giu)
        self.assertEqual(self.conn.events, ['begin', 'rollback'])
        self.assertEqual(len(self.conn.calls), 2)

    def test_ket_noi_dang_co_transaction_khong_duoc_nested_commit(self):
        self.conn.info.transaction_status = 2
        self.kiem_loi('OCR_LUOT_GIAO_DICH', self.giu)
        self.assertEqual(self.conn.calls, [])
        self.assertEqual(self.conn.events, [])
        self.assertEqual(self.conn.info.transaction_status, 2)

    def test_ket_qua_giu_sai_binding_hoac_trang_thai_khong_duoc_cong_bo(self):
        for changed in (dict(giu_trang_id=str(uuid4())), dict(viec_id=str(uuid4())),
                dict(ma_tuong_quan='SAI'), dict(so_trang=4), dict(trang_thai='CHUA_RO'), dict(phien_ban=2)):
            with self.subTest(changed=changed):
                self.conn.raw = dict(self.raw, **changed)
                self.kiem_loi('OCR_LUOT_THAT_BAI', self.giu)
                self.assertEqual(self.conn.events[-1], 'rollback')

    def test_ket_qua_chot_sai_cas_khong_duoc_cong_bo(self):
        for changed in (dict(giu_trang_id=str(uuid4())), dict(phien_ban=1), dict(trang_thai='GIU')):
            with self.subTest(changed=changed):
                self.conn.raw = dict(self.raw, trang_thai='CHUA_RO', phien_ban=2)
                self.conn.raw.update(changed)
                self.kiem_loi('OCR_LUOT_THAT_BAI', self.chot)

    def test_phan_hoi_sql_sai_contract_hoac_them_noi_dung_bi_chan(self):
        invalid = [None, {}, 'SAI', dict(self.raw, ten_tep=TEN_TEP), dict(self.raw, ma_bam=BAM),
            dict(self.raw, so_trang=True), dict(self.raw, so_trang=0), dict(self.raw, phien_ban=True),
            dict(self.raw, phien_ban=0), dict(self.raw, trang_thai='DANG_XU_LY'),
            dict(self.raw, giu_trang_id=TEN_TEP), dict(self.raw, ma_tuong_quan=TEN_TEP)]
        for raw in invalid:
            with self.subTest(raw=raw):
                self.conn.raw = raw
                self.kiem_loi('OCR_LUOT_THAT_BAI', self.giu)
                self.assertEqual(self.conn.events[-1], 'rollback')

    def test_dau_vao_sai_khong_cham_sql_khong_lo_gia_tri(self):
        for changed in (dict(ma_bam='A' * 64), dict(ma_bam=TEN_TEP), dict(so_trang=True),
                dict(so_trang=0), dict(so_trang=2**31), dict(giu_trang_id=TEN_TEP),
                dict(ma_tuong_quan=TEN_TEP)):
            with self.subTest(changed=changed):
                self.kiem_loi('OCR_LUOT_DAU_VAO', lambda: self.giu(**changed))
        self.kiem_loi('OCR_LUOT_DAU_VAO', lambda: self.chot(phien_ban=True))
        self.assertEqual(self.conn.calls, [])


class OCRDiemTiemTests(unittest.TestCase):
    setUp = nen.KenhEngineTest.setUp
    ket_noi = nen.KenhEngineTest.ket_noi
    dong = nen.KenhEngineTest.dong
    nhan = nen.KenhEngineTest.nhan

    def tao_worker(self, provider):
        return kenh.WorkerEngine(MagicMock(), proof=MagicMock(), kiem_the=self.worker._kiem,
            khoa_rieng=self.key, kiem_instance=lambda: True, ket_noi=self.ket_noi,
            hang_viec=self.hang, kho_tep=self.kho, instance_id=self.instance,
            thu_hoi=self.revoked.append, ngu_canh=self.header, ocr_doi_chieu=provider)

    def test_mac_dinh_thieu_dich_vu_tu_choi_giu_luot_qua_wire(self):
        self.assertIsNone(self.worker._ocr_doi_chieu)
        g, _ = self.nhan()
        with patch.object(self.conn, 'execute', wraps=self.conn.execute) as execute:
            with self.assertRaises(LoiEngine):
                self.client.goi('ocr_giu_luot', g, ma_bam=BAM)
            execute.assert_not_called()

    def test_diem_tiem_chap_nhan_callable_khong_tu_goi_provider(self):
        provider = MagicMock()
        worker = self.tao_worker(provider)
        self.assertIs(worker._ocr_doi_chieu, provider)
        provider.assert_not_called()

    def test_diem_tiem_tu_choi_provider_khong_callable(self):
        with self.assertRaises(kenh.k.LoiKenh):
            self.tao_worker(object())

    def test_tiem_dich_vu_van_khong_mo_operation_hoac_carrier_ocr(self):
        provider = MagicMock()
        self.worker._ocr_doi_chieu = provider
        g, _ = self.nhan()
        with self.assertRaises(LoiEngine):
            self.client.goi('doc_dau_vao', g, ocr=dict(operation='giu_luot', ma_bam=BAM))
        provider.assert_not_called()


@unittest.skipUnless(os.environ.get('KHO_PG_DSN_TEST'),
                     'CHUA_KIEM PG: chỉ lead chạy với KHO_PG_DSN_TEST')
class OCRDoiChieuPostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tests import test_ocr_doi_chieu_sql as sql
        cls.nen_sql = sql.OCRPostgresTests
        cls._viec = cls.nen_sql._viec
        cls.nen_sql.setUpClass.__func__(cls)

    def setUp(self):
        self.nen_sql.setUp(self)
        self.service = ocr.OCRDoiChieu(self.core,
            ngu_canh=ocr.NguCanhOCR(self.pn, 'crm', self.viec, 1))

    def giu(self):
        return self.service.giu_luot(ma_bam=BAM, ma_tuong_quan='DEMO_OCR:' + uuid4().hex,
            so_trang=3, giu_trang_id=uuid4())

    def test_giu_chua_ro_chan_gui_lai_va_cas_that(self):
        row = self.giu()
        result = self.service.chot_luot(ma_bam=BAM, giu_trang_id=row.giu_trang_id,
            phien_ban=row.phien_ban, trang_thai_cu=row.trang_thai,
            trang_thai_moi=ocr.TrangThaiLuotOCR.CHUA_RO)
        self.assertEqual(self.service.doc_trang_thai(ma_bam=BAM), result)
        with self.assertRaises(ocr.LoiOCRDoiChieu) as caught:
            self.giu()
        self.assertEqual(caught.exception.ma, 'OCR_LUOT_DANG_BI_CHAN')
        with self.assertRaises(ocr.LoiOCRDoiChieu) as caught:
            self.service.chot_luot(ma_bam=BAM, giu_trang_id=row.giu_trang_id,
                phien_ban=row.phien_ban, trang_thai_cu=row.trang_thai,
                trang_thai_moi=ocr.TrangThaiLuotOCR.HOAN_TRANG)
        self.assertEqual(caught.exception.ma, 'OCR_LUOT_XUNG_DOT')

    def test_login_module_bi_42501(self):
        service = ocr.OCRDoiChieu(self.module,
            ngu_canh=ocr.NguCanhOCR(self.pn, 'crm', self.viec, 1))
        with self.assertRaises(ocr.LoiOCRDoiChieu) as caught:
            service.doc_trang_thai(ma_bam=BAM)
        self.assertEqual((caught.exception.ma, caught.exception.sqlstate), ('42501', '42501'))


if __name__ == '__main__':
    unittest.main()
