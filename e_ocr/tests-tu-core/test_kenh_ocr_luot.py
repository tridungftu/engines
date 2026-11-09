"""OCR-CR-3b: wire/proof thật trên queue giả, SQL mock; không PG/server."""
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json
import threading
import traceback
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from tests import test_g2_32_e1 as nen
from tests.test_g2_32_e2 import binding_demo, pin_demo
from tests import test_g2_32_p1 as nen_module
from kho_tri_thuc.core import kenh_engine as e, kenh_module as n, ocr_doi_chieu as ocr
from kho_tri_thuc.core.dich_vu_engine import DichVuEngine
from kho_tri_thuc.sdk_core import kenh_khung as k
from kho_tri_thuc.sdk_core.engine import LoiEngine, SDKEngine


BAM = 'b' * 64
BI_MAT = 'Hồ sơ DEMO nhạy cảm · ' + BAM


class LoiSQL(RuntimeError):
    def __init__(self, code, sqlstate='P0001'):
        self.diag = SimpleNamespace(message_primary=code)
        self.sqlstate = sqlstate
        super().__init__(BI_MAT)


class KetNoi:
    """Mỗi lần mượn kết nối có transaction riêng; trạng thái bền dùng chung."""
    def __init__(self, case):
        self.case, self.info = case, SimpleNamespace(transaction_status=0)

    @contextmanager
    def transaction(self):
        case = self.case
        old = deepcopy((case.receipts, case.rows))
        self.info.transaction_status = 2
        case.sql_events.append(('begin', self))
        self.phase = None
        try:
            yield
            if case.fail_commit is not None and case.fail_commit == self.phase:
                raise RuntimeError(BI_MAT)
            case.sql_events.append(('commit', self, self.phase))
            case.events.append('commit')
        except BaseException:
            case.receipts, case.rows = old
            case.sql_events.append(('rollback', self, self.phase))
            raise
        finally:
            self.info.transaction_status = 0

    def execute(self, sql, args=None):
        case = self.case
        case.assertEqual(self.info.transaction_status, 2)
        case.sql_calls.append((sql, args, self))
        result = None
        if 'loi.nguon_lease_engine(' in sql:
            case.assertEqual(args, (*e.viec._giu(self, case.giu), case.giu.lan_thu_id))
            result = dict(bang='ho_so_demo', id=str(case.tid), phien_ban_contract='1',
                engine_id=str(case.pin.engine_id), buoc_id=str(case.giu.buoc_viec_id),
                lan_thu_id=str(case.giu.lan_thu_id))
        elif 'loi_tai_lieu.bien_nhan_core_v2(' in sql:
            ma, module, pn, hd, op, key, body, ghi, out, quyen, state, job, gen = args
            case.assertEqual((ma, module, pn, hd, job, gen),
                (case.giu.ma.lay_de_truyen(), case.giu.module, case.pn,
                 case.giu.hanh_dong, case.giu.viec_id, case.giu.the_he))
            key = (pn, module, op, key)
            old = case.receipts.get(key)
            if old and old['body'] != body:
                raise LoiSQL('KHOA_CHONG_TRUNG_KHAC_NOI_DUNG')
            if ghi:
                self.phase = 'pending' if state == 'DANG_XU_LY' else 'final'
                case.receipts[key] = dict(body=body, ket_qua=json.loads(out), state=state)
            row = case.receipts.get(key)
            if row:
                result = dict(ket_qua=deepcopy(row['ket_qua']))
        elif 'loi_tai_lieu.ocr_' in sql:
            self.phase = 'ocr'
            case.ocr_calls.append((sql, args, self))
            if case.sql_error:
                raise case.sql_error
            if 'ocr_giu_luot(' in sql:
                pn, bam, job, corr, pages, gid = args
                case.assertEqual((pn, job), (case.giu.phap_nhan_id, case.giu.viec_id))
                old = case.rows.get(bam)
                if old and old['trang_thai'] in ('GIU', 'CHUA_RO'):
                    raise LoiSQL('OCR_LUOT_DANG_BI_CHAN')
                result = dict(giu_trang_id=str(gid), viec_id=str(job), ma_tuong_quan=corr,
                    so_trang=pages, trang_thai='GIU', phien_ban=1)
                case.rows[bam] = result
            elif 'ocr_doc_trang_thai(' in sql:
                case.assertEqual(args[0], case.pn)
                result = case.rows.get(args[1])
            elif 'ocr_chot_luot(' in sql:
                pn, bam, gid, version, old_state, new_state = args
                case.assertEqual(pn, case.pn)
                row = case.rows.get(bam)
                if not row or (row['giu_trang_id'], row['phien_ban'], row['trang_thai']) != (
                        str(gid), version, old_state):
                    raise LoiSQL('OCR_LUOT_XUNG_DOT', '40001')
                result = dict(row, trang_thai=new_state, phien_ban=version + 1)
                case.rows[bam] = result
        return SimpleNamespace(fetchone=lambda: (deepcopy(result),))


class KenhOCRLuotTests(unittest.TestCase):
    ket_noi = nen.KenhEngineTest.ket_noi
    dong = nen.KenhEngineTest.dong
    nhan = nen.KenhEngineTest.nhan

    def setUp(self):
        nen.KenhEngineTest.setUp(self)
        self.receipts, self.rows, self.sql_calls, self.ocr_calls = {}, {}, [], []
        self.sql_events, self.connections = [], []
        self.fail_commit, self.sql_error = None, None
        self.pin = pin_demo(ma_engine='e_ocr')
        ghim = binding_demo(self.pin, ma_contract=self.header['contract_id'],
            phien_ban_contract=self.header['phien_ban_contract'])
        service = MagicMock(spec=DichVuEngine)
        service._loai_viec = {(ghim.module, ghim.loai, ghim.phien_ban): ghim}
        service._ghim = {ghim.capability: self.pin}
        hang = e.HangViecCore(ctx=dict(module='crm'), dau_vao=lambda c, g: self.inp,
            ban_giao=self.hang.ban_giao, ghim_loai_viec=ghim, dich_vu_engine=service)
        hang.nhan, hang.kiem = self.hang.nhan, self.hang.kiem
        self.worker._hang = hang
        self.worker._ket_noi = self.mo_ket_noi
        self.provider = MagicMock(side_effect=self.tao_provider)
        self.worker._ocr_doi_chieu = self.provider
        self.kho.tham_chieu.side_effect = lambda c, **kw: dict(tep_id=kw['tep_id'], sha256=BAM)
        self.g, self.sdk = self.nhan()
        original_send = self.worker._wire.gui
        def gui(header, raw, han):
            self.assertTrue(all(c.info.transaction_status == 0 for c in self.connections))
            if header.get('status') == 200 and header.get('operation') in k.OPERATION_OCR_GHI:
                self.assertEqual(self.sql_events[-1][0], 'commit')
                result = k._doc_json(raw)['ket_qua']
                self.assertTrue(any(key[2] == header['operation'] and row['state'] == 'HOAN_TAT'
                    and row['ket_qua'] == result for key, row in self.receipts.items()))
            return original_send(header, raw, han)
        self.send = self.enterContext(patch.object(self.worker._wire, 'gui', side_effect=gui))

    @contextmanager
    def mo_ket_noi(self):
        conn = KetNoi(self)
        self.connections.append(conn)
        yield conn

    def tao_provider(self, conn, *, ngu_canh):
        self.assertEqual(conn.info.transaction_status, 0)
        self.assertEqual(ngu_canh, ocr.NguCanhOCR.tu_lease(self.giu))
        return ocr.OCRDoiChieu(conn, ngu_canh=ngu_canh)

    def giu_luot(self):
        return self.sdk.ocr_giu_luot(bam_noi_dung=BAM, so_trang=3)

    def doc(self):
        return self.sdk.ocr_doc_luot(bam_noi_dung=BAM)

    def chot(self, turn, **doi):
        return self.sdk.ocr_chot_luot(**{**dict(ma_tuong_quan=turn['ma_tuong_quan'],
            ket_qua='da_tieu', phien_ban=turn['phien_ban']), **doi})

    def loi(self, ham, ma=None):
        with self.assertNoLogs(level='DEBUG'), self.assertRaises(LoiEngine) as caught:
            ham()
        error = caught.exception
        if ma:
            self.assertEqual(error.ma, ma)
        self.assertFalse(error.thu_lai_duoc)
        self.assertIsNone(error.__context__)
        self.assertIsNone(error.__cause__)
        detail = ''.join(traceback.format_exception(error))
        self.assertNotIn(BAM, detail)
        self.assertNotIn(BI_MAT, detail)
        for call in self.send.call_args_list:
            # hash_than là metadata của giao thức, không phải băm tệp nguồn.
            self.assertNotIn(BAM.encode(), call.args[1])
            self.assertNotIn(BI_MAT, json.dumps(call.args[0], ensure_ascii=False))
        return error

    def seed(self, state='GIU', **doi):
        self.rows[BAM] = dict(giu_trang_id=str(uuid4()), viec_id=str(self.giu.viec_id),
            ma_tuong_quan='ocr:DEMO', so_trang=3, trang_thai=state, phien_ban=4, **doi)
        return dict(ma_tuong_quan='ocr:DEMO', phien_ban=4)

    def test_ba_operation_qua_wire_dung_dto_va_commit(self):
        self.assertEqual(self.doc(), dict(trang_thai='khong_co', phien_ban=None))
        turn = self.giu_luot()
        self.assertEqual(set(turn), {'ma_tuong_quan', 'trang_thai', 'phien_ban'})
        self.assertEqual((turn['trang_thai'], turn['phien_ban']), ('dang_giu', 1))
        self.assertEqual(self.doc(), dict(trang_thai='dang_giu', phien_ban=1))
        self.assertEqual(self.chot(turn), dict(trang_thai='da_tieu'))
        self.assertEqual(self.doc(), dict(trang_thai='da_tieu', phien_ban=2))
        responses = [x.args[0] for x in self.send.call_args_list if x.args[0]['kieu'] == 'response']
        self.assertEqual([h['operation'] for h in responses],
            ['ocr.doc_luot', 'ocr.giu_luot', 'ocr.doc_luot', 'ocr.chot_luot', 'ocr.doc_luot'])
        self.assertTrue(all(h['da_commit'] for h in responses))
        self.assertTrue(all(c.info.transaction_status == 0 for c in self.connections))

    def test_ghi_phat_lai_sau_dung_lai_sdk_khong_goi_lai_sql(self):
        turn = self.giu_luot()
        before = len(self.ocr_calls)
        self.sdk = SDKEngine(self.g, kenh_core=self.client)
        self.assertEqual(self.giu_luot(), turn)
        self.assertEqual(len(self.ocr_calls), before)
        out = self.chot(turn)
        before = len(self.ocr_calls)
        self.assertEqual(self.chot(turn), out)
        self.assertEqual(len(self.ocr_calls), before)

    def test_cung_khoa_khac_noi_dung_bi_chan(self):
        self.client.goi('ocr.giu_luot', self.g, khoa='DEMO_KEY_00000001', bam_noi_dung=BAM, so_trang=3)
        before = len(self.ocr_calls)
        self.loi(lambda: self.client.goi('ocr.giu_luot', self.g, khoa='DEMO_KEY_00000001',
            bam_noi_dung=BAM, so_trang=4), 'KHOA_CHONG_TRUNG_KHAC_NOI_DUNG')
        self.assertEqual(len(self.ocr_calls), before)

    def test_giu_thieu_khoa_khong_cham_provider(self):
        self.loi(lambda: self.client.goi('ocr.giu_luot', self.g, bam_noi_dung=BAM, so_trang=3))
        self.provider.assert_not_called()

    def test_doc_khong_nhan_khoa_ghi(self):
        self.loi(lambda: self.client.goi('ocr.doc_luot', self.g,
            khoa='DEMO_KEY_00000001', bam_noi_dung=BAM))
        self.provider.assert_not_called()

    def test_provider_thieu_tra_loi_huu_han_truoc_sql(self):
        self.worker._ocr_doi_chieu = None
        before = len(self.sql_calls)
        self.loi(self.giu_luot, 'CHUA_SAN_SANG')
        self.assertEqual(len(self.sql_calls), before)
        self.assertTrue(any(x.args[0].get('status') == 503 for x in self.send.call_args_list))

    def test_ghim_engine_khac_bi_chan(self):
        hang = self.worker._hang
        hang._dich_vu._ghim[hang._ghim.capability] = replace(self.pin, ma_engine='e_mask')
        self.loi(self.giu_luot, 'KENH_KHONG_DU_QUYEN')
        self.provider.assert_not_called()

    def test_bam_ngoai_nguon_core_bi_chan(self):
        self.kho.tham_chieu.side_effect = lambda c, **kw: dict(tep_id=kw['tep_id'], sha256='c'*64)
        self.inp.du_lieu['bam_noi_dung'] = BAM  # Payload công việc không thay được nguồn kho.
        self.loi(self.giu_luot, 'KENH_KHONG_DU_QUYEN')
        self.provider.assert_not_called()
        self.assertEqual(self.receipts, {})

    def test_tham_chieu_tep_sai_bi_chan(self):
        self.kho.tham_chieu.side_effect = lambda c, **kw: dict(tep_id=str(uuid4()), sha256=BAM)
        self.loi(self.doc, 'KENH_KHONG_DU_QUYEN')
        self.provider.assert_not_called()

    def test_lease_thu_hoi_bi_chan_truoc_provider(self):
        self.hang.live = False
        self.loi(self.giu_luot, 'VIEC_MAT_LEASE')
        self.provider.assert_not_called()

    def test_lan_thu_sai_bi_chan(self):
        self.loi(lambda: self.client.goi('ocr.doc_luot', replace(self.g, lan_thu_id=uuid4()),
            bam_noi_dung=BAM), 'VIEC_MAT_LEASE')
        self.provider.assert_not_called()

    def test_ngu_canh_payload_khong_thay_duoc_lease(self):
        self.loi(lambda: self.client.goi('ocr.giu_luot', self.g,
            khoa='DEMO_KEY_00000001', bam_noi_dung=BAM, so_trang=3,
            phap_nhan_id=str(uuid4())), 'KENH_DU_LIEU_KHONG_HOP_LE')
        self.provider.assert_not_called()

    def test_core_tu_chan_payload_gia_danh_du_client_bo_kiem(self):
        original = k.kiem_dto_ocr
        caller = threading.get_ident()
        def kiem(op, data, **kw):
            if threading.get_ident() == caller and not kw.get('phan_hoi'):
                return dict(data)
            return original(op, data, **kw)
        with patch.object(k, 'kiem_dto_ocr', side_effect=kiem):
            self.loi(lambda: self.client.goi('ocr.doc_luot', self.g,
                bam_noi_dung=BAM, module='gia_mao', the_he=99), 'KENH_DU_LIEU_KHONG_HOP_LE')
        self.provider.assert_not_called()
        self.assertEqual(self.receipts, {})

    def test_core_tu_chan_ghi_thieu_khoa_trong_header(self):
        self.doc()
        header = next(k._doc_json(x.args[1]) for x in self.send.call_args_list
            if x.args[0]['kieu'] == 'cap_the')
        header.pop('the_ky')
        header['operation'] = 'ocr.giu_luot'
        with self.assertRaises(k.LoiKenh):
            self.worker._kiem_header(header)
        self.assertEqual(self.receipts, {})

    def test_doc_dang_giu_khong_cap_ma_gui(self):
        self.seed()
        self.assertEqual(self.doc(), dict(trang_thai='dang_giu', phien_ban=4))
        self.loi(self.giu_luot, 'XUNG_DOT')
        self.assertFalse(any('ocr_chot_luot(' in x[0] for x in self.ocr_calls))

    def test_doc_chua_ro_khong_cap_ma_gui(self):
        self.seed('CHUA_RO')
        self.assertEqual(self.doc(), dict(trang_thai='chua_ro', phien_ban=4))
        self.loi(self.giu_luot, 'XUNG_DOT')
        self.assertEqual(self.rows[BAM]['trang_thai'], 'CHUA_RO')

    def test_chot_chua_ro_duoc_hoan_va_giu_nguyen_cas(self):
        turn = self.seed('CHUA_RO')
        self.assertEqual(self.chot(turn, ket_qua='hoan_trang'), dict(trang_thai='hoan_trang'))
        args = next(args for sql, args, conn in self.ocr_calls if 'ocr_chot_luot(' in sql)
        self.assertEqual(args[-3:], (4, 'CHUA_RO', 'HOAN_TRANG'))

    def test_chot_khong_nhan_ma_luot_viec_khac(self):
        turn = self.seed()
        self.rows[BAM]['viec_id'] = str(uuid4())
        self.loi(lambda: self.chot(turn), 'KENH_KHONG_DU_QUYEN')
        self.assertFalse(any('ocr_chot_luot(' in x[0] for x in self.ocr_calls))

    def test_chot_ma_tuong_quan_khong_khop_bi_chan(self):
        turn = self.seed()
        self.loi(lambda: self.chot(turn, ma_tuong_quan='ocr:KHAC'), 'KENH_KHONG_DU_QUYEN')

    def test_chot_sai_cas_bi_chan(self):
        turn = self.seed()
        self.loi(lambda: self.chot(turn, phien_ban=3), 'XUNG_DOT')
        self.assertEqual(self.rows[BAM]['phien_ban'], 4)

    def test_chot_trang_thai_cuoi_khong_chot_lan_hai(self):
        turn = self.seed('HOAN_TRANG')
        self.loi(lambda: self.chot(turn), 'XUNG_DOT')

    def test_pending_commit_loi_khong_goi_provider(self):
        self.fail_commit = 'pending'
        self.loi(self.giu_luot, 'LOI_NOI_BO')
        self.provider.assert_not_called()
        self.assertEqual(self.receipts, {})

    def test_ocr_commit_loi_khong_ack_va_giu_dau_cho_doi_chieu(self):
        self.fail_commit = 'ocr'
        self.loi(self.giu_luot, 'LOI_NOI_BO')
        self.assertEqual(self.rows, {})
        self.assertEqual([x['state'] for x in self.receipts.values()], ['DANG_XU_LY'])

    def test_final_commit_loi_khong_ack_du_ocr_da_commit(self):
        self.fail_commit = 'final'
        self.loi(self.giu_luot, 'LOI_NOI_BO')
        self.assertEqual(self.rows[BAM]['trang_thai'], 'GIU')
        self.assertEqual([x['state'] for x in self.receipts.values()], ['DANG_XU_LY'])
        self.assertFalse(any(x.args[0].get('status') == 200 for x in self.send.call_args_list))

    def test_bien_nhan_dang_xu_ly_chan_goi_lai_provider(self):
        self.giu_luot()
        row = next(iter(self.receipts.values()))
        row.update(ket_qua={'cho_doi_chieu': True}, state='DANG_XU_LY')
        self.provider.reset_mock()
        self.loi(self.giu_luot, 'XUNG_DOT')
        self.provider.assert_not_called()

    def test_provider_loi_khong_lo_bam_va_khong_retry(self):
        self.provider.side_effect = RuntimeError(BI_MAT)
        self.loi(self.giu_luot, 'LOI_NOI_BO')

    def test_sql_42501_anh_xa_403(self):
        self.sql_error = LoiSQL('DEMO', '42501')
        self.loi(self.doc, 'KENH_KHONG_DU_QUYEN')

    def test_provider_tra_bam_ngoai_contract_bi_chan(self):
        service = MagicMock()
        service.doc_trang_thai.return_value = dict(trang_thai='GIU', ma_bam=BAM)
        self.provider.side_effect = None
        self.provider.return_value = service
        self.loi(self.doc, 'PHAN_HOI_SAI_CONTRACT')

    def test_lease_mat_sau_provider_khong_ack(self):
        def provider(conn, *, ngu_canh):
            real = self.tao_provider(conn, ngu_canh=ngu_canh)
            def doc(**kw):
                out = real.doc_trang_thai(**kw)
                self.hang.live = False
                return out
            return SimpleNamespace(doc_trang_thai=doc)
        self.provider.side_effect = provider
        self.loi(self.doc, 'VIEC_MAT_LEASE')

    def test_nguon_doi_sau_provider_khong_ack(self):
        def provider(conn, *, ngu_canh):
            real = self.tao_provider(conn, ngu_canh=ngu_canh)
            def doc(**kw):
                out = real.doc_trang_thai(**kw)
                self.kho.tham_chieu.side_effect = lambda c, **kw: dict(tep_id=kw['tep_id'], sha256='c'*64)
                return out
            return SimpleNamespace(doc_trang_thai=doc)
        self.provider.side_effect = provider
        self.loi(self.doc, 'KENH_KHONG_DU_QUYEN')


class TiemOCRTests(unittest.TestCase):
    setUp = nen_module.P1Tests.setUp
    engine_row = nen_module.P1Tests.engine_row

    def tearDown(self):
        self.assertTrue(self.manager.dong(timeout=.1))

    def kiem(self, name):
        hs = replace(self.profiles.engine.return_value, ma_engine=name)
        self.profiles.engine.return_value = hs
        self.network.side_effect = None
        worker = MagicMock(spec=e.WorkerEngine)
        with patch.object(n.so_cong, 'doc', side_effect=lambda *a: self.engine_row()), \
                patch.object(e, 'WorkerEngine', return_value=worker) as factory:
            with self.manager.su_dung_engine(name, phap_nhan_id=self.ctx.phap_nhan_id) as got:
                self.assertIs(got, worker)
                kwargs = factory.call_args.kwargs
                if name == 'e_ocr':
                    self.assertIs(kwargs['ocr_doi_chieu'], ocr.OCRDoiChieu)
                else:
                    self.assertNotIn('ocr_doi_chieu', kwargs)
            worker.crash.assert_called_once()

    def test_e_ocr_duoc_tiem_provider_that(self):
        self.kiem('e_ocr')

    def test_e_mask_khong_duoc_tiem_provider_ocr(self):
        self.kiem('e_mask')

    def test_engine_khac_khong_duoc_tiem_provider_ocr(self):
        self.kiem('engine-demo')


if __name__ == '__main__':
    unittest.main()
