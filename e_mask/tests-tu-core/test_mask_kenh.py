"""MASK-3F: kênh/proof thật trên queue giả, SQL mock; không mở PG/server."""
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from functools import partial
from hashlib import sha256
import json
import traceback
import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from tests import test_g2_32_e1 as nen
from tests.test_g2_32_e2 import binding_demo, pin_demo
from kho_tri_thuc.core import kenh_engine as e, mask
from kho_tri_thuc.core.dich_vu_engine import DichVuEngine
from kho_tri_thuc.core.dispatcher import KiemSchema
from kho_tri_thuc.sdk_core.engine import LoiEngine


class MaskKenhTests(unittest.TestCase):
    def setUp(self):
        with patch.object(e, 'WorkerEngine', partial(e.WorkerEngine, kho_mask=mask.Mask)):
            nen.KenhEngineTest.setUp(self)

    ket_noi = nen.KenhEngineTest.ket_noi
    dong = nen.KenhEngineTest.dong
    nhan = nen.KenhEngineTest.nhan

    def chuan_bi(self, *, ten_engine='e_mask', loai='che'):
        self.request, self.turn = uuid4(), uuid4()
        self.inp = replace(self.inp, mask=e.DauVaoMask(self.request, self.turn, loai))
        pin = pin_demo(ma_engine=ten_engine)
        ghim = binding_demo(pin, ma_contract=self.header['contract_id'],
                            phien_ban_contract=self.header['phien_ban_contract'])
        service = MagicMock(spec=DichVuEngine)
        service._loai_viec = {(ghim.module, ghim.loai, ghim.phien_ban): ghim}
        service._ghim = {pin.capability: pin}
        hang = e.HangViecCore(ctx=dict(module='crm'), dau_vao=lambda c, g: self.inp,
            ban_giao=self.hang.ban_giao, ghim_loai_viec=ghim, dich_vu_engine=service)
        hang.nhan, hang.kiem = self.hang.nhan, self.hang.kiem
        self.worker._hang = hang
        self.snap = dict(da_chot=False, phien_ban='a'*64, danh_muc=[], yeu_cau=None,
                         bi_danh_bo_sung={}, cum_cho_toan_vung={})
        self.result = dict(ma_yeu_cau=str(self.request), ma_luot=str(self.turn),
            van_ban_da_che=None, con_sot=[dict(ly_do='Chưa kiểm tra đầy đủ định danh.')],
            kiem_tien_ngay=True, gui_duoc=False, so_cho_thay=0, bi_danh=[],
            cho_duyet=dict(so_cum_vua_them=0), canh_bao=[])
        self.payload = dict(ma_yeu_cau=str(self.request), ma_luot=str(self.turn), loai=loai)
        self.sql = []
        def execute(sql, args=None):
            if sql.startswith('SELECT mask.'):
                self.assertEqual(self.conn.info.transaction_status, 2)
                self.sql.append((sql, args))
                value = self.snap if 'snapshot_luot' in sql else self.result
                return nen.SimpleNamespace(fetchone=lambda: (deepcopy(value),))
            return nen.SimpleNamespace(fetchone=lambda: (None,))
        self.conn.execute = execute
        self.g, self.sdk = self.nhan()

    def goi(self, operation='mask.snapshot', **doi):
        return self.client.goi(operation, self.g, **{**self.payload, **doi})

    def chot(self, **doi):
        return self.goi('mask.chot_luot', **{**dict(phien_ban='a'*64,
            nhat_ky=dict(cum=[], bi_danh_tam_moi=[], bi_danh_da_dung=[],
                        cum_da_tra=[], bi_danh_da_tra=[], dong_yeu_cau=True),
            ket_qua=deepcopy(self.result)), **doi})

    def bi_chan(self, ham):
        with self.assertRaises(LoiEngine) as caught:
            ham()
        self.assertEqual(self.sql, [])
        return caught.exception

    def test_snapshot_chot_qua_mask_py_cung_ngu_canh_va_sau_commit(self):
        self.chuan_bi()
        with patch.object(mask.Mask, '_goi', autospec=True, wraps=mask.Mask._goi) as call:
            call.side_effect = lambda obj, *args: mask_call(obj, *args)
            self.assertEqual(self.goi(), self.snap)
            self.assertEqual(self.chot(), self.result)
        self.assertEqual([x.args[1] for x in call.call_args_list], ['snapshot', 'chot'])
        for sql, args in self.sql:
            self.assertEqual(args[:7], (self.g.ma.lay_de_truyen(), self.g.module,
                self.g.phap_nhan_id, self.g.hanh_dong, self.inp.tai_lieu_id,
                self.g.viec_id, self.g.the_he))
            self.assertEqual(args[7:10], (self.request, self.turn, 'che'))
        self.assertEqual(json.loads(self.sql[-1][1][-1]), self.result)
        self.assertEqual(self.conn.info.transaction_status, 0)
        self.assertEqual(self.events[-1], 'commit')

    def test_callable_tuong_thich_adapter_engine(self):
        self.chuan_bi()
        self.assertEqual(self.client.goi_mask('snapshot_luot', self.g, **self.payload), self.snap)
        self.assertEqual(self.client.goi_mask('chot_luot', self.g, **self.payload,
            phien_ban='a'*64, nhat_ky=dict(cum=[], bi_danh_tam_moi=[], bi_danh_da_dung=[],
                cum_da_tra=[], bi_danh_da_tra=[], dong_yeu_cau=True),
            ket_qua=self.result), self.result)

    def test_snapshot_cum_cho_toan_vung_khac_rong_dung_dang_sql(self):
        self.chuan_bi()
        gia_tri = 'Công ty DEMO'
        bam = sha256(mask.che_van_ban.chuan_hoa(gia_tri).encode('utf-8')).hexdigest()
        muc = dict(nhom='CONG_TY', bi_danh='[[MASKTAM-DEMO]]', nguon='tam')
        self.snap['cum_cho_toan_vung'] = {bam: muc}
        snapshot = self.goi()
        self.assertEqual(snapshot, self.snap)
        self.assertNotIn(gia_tri, json.dumps(snapshot, ensure_ascii=False))
        kho = mask.KhoLuot(snapshot, str(self.request), loai='che')
        with kho.giao_dich():
            self.assertEqual(kho.tra_bi_danh(gia_tri), muc)

    def test_callable_tu_choi_operation_khac_khong_chuyen_tiep(self):
        self.chuan_bi()
        with patch.object(e.KenhCore, 'goi', autospec=True) as call:
            for operation in ('doc_dau_vao', 'ket_thuc', 'mask.snapshot', 'snapshot',
                              'ten_la', None, [], {}):
                with self.subTest(operation=operation), self.assertRaises(LoiEngine):
                    self.client.goi_mask(operation, self.g, **self.payload)
            call.assert_not_called()
        self.assertEqual(self.sql, [])
        self.assertEqual(self.sdk.doc_dau_vao(), self.inp.du_lieu)

    def test_doc_dau_vao_thuong_khong_tra_snapshot_hoac_binding_kho(self):
        self.chuan_bi()
        self.assertEqual(self.sdk.doc_dau_vao(), self.inp.du_lieu)
        self.assertEqual(self.sql, [])

    def test_mo_che_dung_snapshot_chot_va_trang_thai(self):
        self.chuan_bi(loai='mo_che')
        self.snap['yeu_cau'] = dict(trang_thai='DANG_XU_LY')
        self.snap['bi_danh_bo_sung'] = {'[[masktam-demo]]': 'Cụm DEMO'}
        self.result = dict(ma_yeu_cau=str(self.request), ma_luot=str(self.turn),
            van_ban_da_mo_che='Cụm DEMO', so_cho_mo=1, bi_danh_khong_ro=[],
            mo_day_du=True, trang_thai_ma_yeu_cau='DA_DONG')
        self.assertEqual(self.goi(), self.snap)
        self.assertEqual(self.chot(), self.result)
        self.assertEqual([args[9] for _, args in self.sql], ['mo_che', 'mo_che'])

    def test_engine_khac_khong_duoc_vao_kho(self):
        self.chuan_bi(ten_engine='e_ocr')
        self.bi_chan(self.goi)

    def test_thieu_ghim_engine_khong_duoc_tin_payload(self):
        self.chuan_bi()
        self.worker._hang._ghim = None
        self.bi_chan(self.goi)

    def test_lease_het_han(self):
        self.chuan_bi()
        self.worker._lease = replace(self.g, giu_den=datetime.now(timezone.utc)-timedelta(seconds=1))
        self.assertEqual(self.bi_chan(self.goi).ma, 'VIEC_MAT_LEASE')

    def test_the_he_lease_sai(self):
        self.chuan_bi()
        self.g = replace(self.g, the_he=self.g.the_he+1)
        self.assertEqual(self.bi_chan(self.goi).ma, 'VIEC_MAT_LEASE')

    def test_instance_khong_con_song(self):
        self.chuan_bi()
        self.song = False
        self.bi_chan(self.goi)

    def test_the_he_tien_trinh_sai(self):
        self.chuan_bi()
        self.client._binding['the_he'] += 1
        self.bi_chan(self.goi)

    def test_thieu_binding_ma_do_core_cap(self):
        self.chuan_bi()
        self.inp = replace(self.inp, mask=None)
        self.bi_chan(self.goi)

    def test_ma_yeu_cau_khac_viec(self):
        self.chuan_bi()
        self.bi_chan(lambda: self.goi(ma_yeu_cau=str(uuid4())))

    def test_ma_luot_khac_viec(self):
        self.chuan_bi()
        self.bi_chan(lambda: self.goi(ma_luot=str(uuid4())))

    def test_loai_khac_viec(self):
        self.chuan_bi()
        self.bi_chan(lambda: self.goi(loai='mo_che'))

    def test_khong_nhan_danh_tinh_hoac_truong_la(self):
        self.chuan_bi()
        self.bi_chan(lambda: self.goi(module='m4', gia_tri='CANARY_GOC_DEMO'))

    def test_chot_khong_nhan_ket_qua_thuoc_yeu_cau_khac(self):
        self.chuan_bi()
        self.result['ma_yeu_cau'] = str(uuid4())
        self.bi_chan(self.chot)

    def test_chot_khong_nhan_ket_qua_thuoc_luot_khac(self):
        self.chuan_bi()
        self.result['ma_luot'] = str(uuid4())
        self.bi_chan(self.chot)

    def test_chot_thieu_cum_da_tra_bi_chan_truoc_sql(self):
        self.chuan_bi()
        nhat_ky = dict(cum=[], bi_danh_tam_moi=[], bi_danh_da_dung=[],
                      bi_danh_da_tra=[], dong_yeu_cau=True)
        self.bi_chan(lambda: self.chot(nhat_ky=nhat_ky))

    def test_chot_thieu_bi_danh_da_tra_bi_chan_truoc_sql(self):
        self.chuan_bi()
        nhat_ky = dict(cum=[], bi_danh_tam_moi=[], bi_danh_da_dung=[],
                      cum_da_tra=[], dong_yeu_cau=True)
        self.bi_chan(lambda: self.chot(nhat_ky=nhat_ky))

    def test_phan_hoi_bi_chan_khong_chua_van_ban(self):
        self.chuan_bi()
        self.result['van_ban_da_che'] = 'CANARY_GOC_DEMO'
        self.bi_chan(self.chot)

    def test_snapshot_da_chot_chi_co_co_chot(self):
        self.chuan_bi()
        self.snap = dict(da_chot=True)
        self.assertEqual(self.goi(), self.snap)
        self.assertEqual(self.chot(phien_ban=None, nhat_ky=None, ket_qua=None), self.result)

    def test_snapshot_truong_la_khong_lo_ra_ngoai(self):
        self.chuan_bi()
        self.snap['cum_goc'] = 'CANARY_GOC_DEMO'
        with self.assertRaises(LoiEngine) as caught:
            self.goi()
        self.assertNotIn('CANARY_GOC_DEMO', ''.join(traceback.format_exception(caught.exception)))

    def test_che_khong_nhan_cum_goc_bo_sung_ngoai_snapshot_can_thiet(self):
        self.chuan_bi()
        self.snap['bi_danh_bo_sung'] = {'[[masktam-demo]]': 'CANARY_GOC_DEMO'}
        with self.assertRaises(LoiEngine):
            self.goi()

    def test_mat_lease_sau_snapshot_khong_cong_bo(self):
        self.chuan_bi()
        def thu_hoi(obj, *args):
            value = mask_call(obj, *args)
            self.hang.live = False
            return value
        with patch.object(mask.Mask, '_goi', thu_hoi), self.assertRaises(LoiEngine) as caught:
            self.goi()
        self.assertEqual(caught.exception.ma, 'VIEC_MAT_LEASE')

    def test_xung_dot_co_ma_thu_lai_khong_lo_noi_dung(self):
        self.chuan_bi()
        with patch.object(mask.Mask, '_goi', side_effect=mask.XungDotLuotMask('CANARY_GOC_DEMO')):
            with self.assertRaises(LoiEngine) as caught:
                self.chot()
        self.assertEqual(caught.exception.ma, 'MASK_XUNG_DOT_LUOT')
        self.assertEqual(caught.exception.http_status, 409)
        self.assertTrue(caught.exception.thu_lai_duoc)
        self.assertNotIn('CANARY_GOC_DEMO', ''.join(traceback.format_exception(caught.exception)))
        self.assertFalse(self.client._dong)
        self.assertFalse(self.worker._dong)
        self.assertEqual(self.revoked, [])
        self.snap['phien_ban'] = 'b'*64
        self.assertEqual(self.goi(), self.snap)
        self.assertEqual(self.chot(phien_ban=self.snap['phien_ban']), self.result)

    def test_xung_dot_snapshot_van_ket_thuc_duoc_lease(self):
        self.chuan_bi()
        self.worker._hang.ket_thuc = self.hang.ket_thuc
        with patch.object(mask.Mask, '_goi', side_effect=mask.XungDotLuotMask('CANARY_GOC_DEMO')):
            with self.assertRaises(LoiEngine) as caught:
                self.goi()
        self.assertEqual(caught.exception.ma, 'MASK_XUNG_DOT_LUOT')
        self.assertTrue(self.client.ket_thuc(self.g, trang_thai='THAT_BAI',
            ma_loi='MASK_XUNG_DOT_LUOT'))
        self.assertTrue(self.hang.done)
        self.assertIsNone(self.worker._lease)
        self.assertEqual(self.revoked, [])

    def test_loi_driver_khong_lo_gia_tri_hoac_ngoai_le_goc(self):
        self.chuan_bi()
        def loi(sql, args=None):
            if sql.startswith('SELECT mask.'):
                raise RuntimeError('CANARY_GOC_DEMO')
            return nen.SimpleNamespace(fetchone=lambda: (None,))
        self.conn.execute = loi
        with self.assertRaises(LoiEngine) as caught:
            self.goi()
        self.assertNotIn('CANARY_GOC_DEMO', ''.join(traceback.format_exception(caught.exception)))
        self.assertIsNone(caught.exception.__context__)
        self.assertIsNone(caught.exception.__cause__)
        self.assertTrue(self.client._dong)

    def test_commit_loi_khong_cong_bo_ket_qua(self):
        self.chuan_bi()
        original = mask.Mask._goi
        def fail(obj, *args):
            self.conn.commit_error = True
            return original(obj, *args)
        with patch.object(mask.Mask, '_goi', fail), self.assertRaises(LoiEngine):
            self.chot()
        self.assertIn('rollback', self.events)


mask_call = mask.Mask._goi


class MaskSchemaTests(unittest.TestCase):
    def test_cum_cho_toan_vung_la_object_dong_khong_nhan_cum_goc(self):
        checker = KiemSchema()
        schema = {'$ref': 'urn:ktt:contract:mask_snapshot_ra_noi_bo.v1'}
        muc = dict(nhom='CONG_TY', bi_danh='[[MASKTAM-DEMO]]', nguon='tam')
        snapshot = dict(da_chot=False, phien_ban='a'*64, danh_muc=[], yeu_cau=None,
                        cum_cho_toan_vung={'b'*64: muc})
        self.assertTrue(checker.kiem(schema, snapshot))
        sai = [muc['bi_danh'], dict(muc, gia_tri='CANARY_GOC_DEMO'),
               dict(muc, nguon='chinh_thuc'), dict(muc, nhom=''), dict(muc, bi_danh='')]
        sai.extend({key: value for key, value in muc.items() if key != thieu}
                   for thieu in muc)
        for value in sai:
            with self.subTest(value=value):
                self.assertFalse(checker.kiem(schema,
                    dict(snapshot, cum_cho_toan_vung={'b'*64: value})))
        self.assertFalse(checker.kiem(schema,
            dict(snapshot, cum_cho_toan_vung={'hash_sai': muc})))

    def test_dto_dong_va_vi_tri_object_mo_che(self):
        checker = KiemSchema()
        result = dict(ma_yeu_cau=str(uuid4()), ma_luot=str(uuid4()), van_ban_da_mo_che='DEMO',
            so_cho_mo=0, bi_danh_khong_ro=[dict(bi_danh='[[MASKTAM-DEMO]]',
                vi_tri=dict(bat_dau=0, ket_thuc=16, dong=1, cot=1))],
            mo_day_du=False, trang_thai_ma_yeu_cau='DANG_XU_LY')
        schema = {'$ref': 'urn:ktt:contract:mask_chot_ra_noi_bo.v1'}
        self.assertTrue(checker.kiem(schema, result))
        self.assertFalse(checker.kiem(schema, dict(result, cum_goc='DEMO')))
        result['bi_danh_khong_ro'][0]['vi_tri'] = [0, 16]
        self.assertFalse(checker.kiem(schema, result))


if __name__ == '__main__':
    unittest.main()
