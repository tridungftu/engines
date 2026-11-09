"""MASK-3G: tiêm kho theo hồ sơ Core; chỉ queue, kết nối và dịch vụ giả."""
from copy import deepcopy
from dataclasses import replace
from functools import partial
import json
import time
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from tests import test_g2_32_e1 as nen
from tests import test_g2_32_p1 as nen_module
from tests import test_mask_kenh as nen_mask
from kho_tri_thuc.core import kenh_engine as e, kenh_module as n, mask
from kho_tri_thuc.sdk_core import kenh_khung as k
from kho_tri_thuc.sdk_core.engine import LoiEngine


class WorkerMaskNoiTests(unittest.TestCase):
    def chuan_bi(self, kho_mask=None):
        case = nen_mask.MaskKenhTests()
        self.addCleanup(case.doCleanups)
        # Bỏ tham số khi không được cấp kho để kiểm đúng mặc định constructor.
        kwargs = {} if kho_mask is None else dict(kho_mask=kho_mask)
        with patch.object(e, 'WorkerEngine', partial(e.WorkerEngine, **kwargs)):
            nen.KenhEngineTest.setUp(case)
        case.chuan_bi()
        return case

    def test_khong_cap_kho_tu_choi_hai_thao_tac_truoc_ket_noi(self):
        for operation in ('mask.snapshot', 'mask.chot_luot'):
            with self.subTest(operation=operation):
                case = self.chuan_bi()
                goi = case.goi if operation == 'mask.snapshot' else case.chot
                with patch.object(case.worker, '_ket_noi') as connect, \
                        patch.object(case.worker._wire, 'gui', wraps=case.worker._wire.gui) as send:
                    with self.assertRaises(LoiEngine):
                        goi()
                    connect.assert_not_called()
                    errors = [call.args[0] for call in send.call_args_list
                              if call.args[0]['kieu'] == 'response']
                    self.assertEqual(len(errors), 1)
                    self.assertEqual(errors[0]['loi']['ma'], 'KENH_KHONG_DU_QUYEN')
                    self.assertFalse(errors[0]['da_commit'])
                self.assertEqual(case.sql, [])

    def test_cua_kho_khong_cap_provider_tu_choi_truoc_ket_noi(self):
        case = self.chuan_bi()
        for operation in ('mask.snapshot', 'mask.chot_luot'):
            with self.subTest(operation=operation), patch.object(case.worker, '_ket_noi') as connect:
                with self.assertRaises(k.LoiKenh) as error:
                    case.worker._mask(dict(operation=operation, du_lieu=case.payload),
                                      {}, time.monotonic() + 30)
                self.assertEqual(error.exception.ma, 'KENH_KHONG_DU_QUYEN')
                connect.assert_not_called()

    def test_kho_gia_nhan_snapshot_va_chot_cung_ngu_canh_lease(self):
        kho = Mock()
        factory = Mock(return_value=kho)
        case = self.chuan_bi(factory)
        # Dữ liệu nghiệp vụ do engine đọc không được dùng làm danh tính kho.
        case.inp = replace(case.inp, du_lieu=dict(module='module_la',
            phap_nhan_id=str(uuid4()), tai_lieu_id=str(uuid4()),
            viec_id=str(uuid4()), the_he=999, ma='DEMO_KHONG_TIN_CAY'))
        kho._goi.side_effect = lambda ten, *args: deepcopy(
            case.snap if ten == 'snapshot' else case.result)
        self.assertEqual(case.goi(), case.snap)
        self.assertEqual(case.chot(), case.result)
        self.assertEqual(factory.call_count, 2)
        giu = case.worker._lease
        for call in factory.call_args_list:
            self.assertEqual(call.args, (case.conn,))
            self.assertEqual(call.kwargs, dict(ma=giu.ma, module=giu.module,
                phap_nhan_id=giu.phap_nhan_id, hanh_dong=giu.hanh_dong,
                tai_lieu_id=case.inp.tai_lieu_id, viec_id=giu.viec_id,
                the_he=giu.the_he))
        snapshot, chot = kho._goi.call_args_list
        self.assertEqual(snapshot.args, ('snapshot', case.request, case.turn, 'che'))
        self.assertEqual(chot.args[:5], ('chot', case.request, case.turn, 'che', 'a' * 64))
        self.assertEqual(json.loads(chot.args[5]), dict(cum=[], bi_danh_tam_moi=[],
            bi_danh_da_dung=[], cum_da_tra=[], bi_danh_da_tra=[], dong_yeu_cau=True))
        self.assertEqual(json.loads(chot.args[6]), case.result)
        self.assertEqual(case.sql, [])

    def test_payload_tu_khai_module_phap_nhan_bi_chan_truoc_kho_gia(self):
        for operation in ('mask.snapshot', 'mask.chot_luot'):
            for field, value in (('module', 'module_la'), ('phap_nhan_id', str(uuid4()))):
                with self.subTest(operation=operation, field=field):
                    factory = Mock()
                    case = self.chuan_bi(factory)
                    goi = case.goi if operation == 'mask.snapshot' else case.chot
                    with self.assertRaises(LoiEngine):
                        goi(**{field: value})
                    factory.assert_not_called()
                    self.assertEqual(case.sql, [])

    def test_ghim_engine_khac_van_bi_chan_du_da_tiem_kho(self):
        factory = Mock()
        case = self.chuan_bi(factory)
        service = case.worker._hang._dich_vu
        capability, pin = next(iter(service._ghim.items()))
        service._ghim[capability] = replace(pin, ma_engine='e_ocr')
        with self.assertRaises(LoiEngine):
            case.goi()
        factory.assert_not_called()
        self.assertEqual(case.sql, [])

    def test_loi_kho_gia_khong_lo_noi_dung_trong_phan_hoi_ngoai_le_log(self):
        canary = 'Văn bản DEMO · cụm DEMO · [[MASKTAM-DEMO]]'
        factory = Mock(side_effect=RuntimeError(canary))
        case = self.chuan_bi(factory)
        with self.assertNoLogs(level='DEBUG'), \
                patch.object(case.worker._wire, 'gui', wraps=case.worker._wire.gui) as send:
            with self.assertRaises(LoiEngine) as error:
                case.goi()
        self.assertNotIn(canary, str(error.exception))
        self.assertIsNone(error.exception.__context__)
        self.assertIsNone(error.exception.__cause__)
        for call in send.call_args_list:
            self.assertNotIn(canary, json.dumps(call.args[0], ensure_ascii=False))
            self.assertNotIn(canary.encode('utf-8'), call.args[1])


class KenhModuleMaskNoiTests(unittest.TestCase):
    setUp = nen_module.P1Tests.setUp
    engine_row = nen_module.P1Tests.engine_row

    def tearDown(self):
        self.assertTrue(self.manager.dong(timeout=.1))

    def kiem_kho(self, ma_engine):
        hs = replace(self.profiles.engine.return_value, ma_engine=ma_engine)
        self.profiles.engine.return_value = hs
        worker = Mock(spec=e.WorkerEngine)
        self.network.side_effect = None
        with patch.object(n.so_cong, 'doc', side_effect=lambda *a: self.engine_row()), \
                patch.object(e, 'WorkerEngine', return_value=worker) as factory:
            with self.manager.su_dung_engine(ma_engine, phap_nhan_id=self.ctx.phap_nhan_id) as got:
                self.assertIs(got, worker)
                self.assertIn((hs.ma_engine, hs.phien_ban), self.kt.call_args.args[0])
                kwargs = factory.call_args.kwargs
                if ma_engine == 'e_mask':
                    self.assertIs(kwargs['kho_mask'], mask.Mask)
                else:
                    self.assertNotIn('kho_mask', kwargs)
            worker.crash.assert_called_once()

    def test_ho_so_mask_duoc_tiem_dung_lop_kho(self):
        self.kiem_kho('e_mask')

    def test_engine_khac_khong_duoc_truyen_kho_mask(self):
        self.kiem_kho('e_ocr')

    def test_ho_so_mask_khong_khop_bi_chan_truoc_dung_worker(self):
        hs = replace(self.profiles.engine.return_value, ma_engine='e_mask')
        self.profiles.engine.return_value = replace(hs,
            ngu_canh=dict(hs.ngu_canh, contract_id='contract_la'))
        with patch.object(e, 'WorkerEngine') as factory:
            with self.assertRaises(n.LoiHTTP):
                with self.manager.su_dung_engine('e_mask', phap_nhan_id=self.ctx.phap_nhan_id):
                    self.fail('Hồ sơ không hợp lệ vẫn dựng worker')
            factory.assert_not_called()
        self.connect.assert_not_called()
        self.network.assert_not_called()

    def test_mask_chua_qua_kiem_tra_van_bi_chan_truoc_dung_worker(self):
        self.profiles.engine.return_value = replace(self.profiles.engine.return_value,
                                                    ma_engine='e_mask')
        self.kt.side_effect = n.LoiHTTP(503)
        with patch.object(e, 'WorkerEngine') as factory:
            with self.assertRaises(n.LoiHTTP):
                with self.manager.su_dung_engine('e_mask', phap_nhan_id=self.ctx.phap_nhan_id):
                    self.fail('Hồ sơ chưa qua kiểm tra vẫn dựng worker')
            factory.assert_not_called()
        self.connect.assert_not_called()
        self.network.assert_not_called()
