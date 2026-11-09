"""OCR-CR-3a: DTO/proof thuần RAM và SDK qua kênh mock, không PG/server."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import traceback
import unittest
from unittest.mock import Mock
from uuid import uuid4

from kho_tri_thuc.core.phien import MaBiMat
from kho_tri_thuc.core.viec import GiuViec
from kho_tri_thuc.sdk_core import engine, kenh_khung as k


BAM = '0123456789abcdef' * 4  # Dữ liệu giả, không đọc tệp.
MA = 'ocr-DEMO_01:giu'
DAU_VAO = {
    'ocr.giu_luot': dict(bam_noi_dung=BAM, so_trang=2),
    'ocr.chot_luot': dict(ma_tuong_quan=MA, ket_qua='da_tieu', phien_ban=1),
    'ocr.doc_luot': dict(bam_noi_dung=BAM),
}
DAU_RA = {
    'ocr.giu_luot': dict(ma_tuong_quan=MA, trang_thai='dang_giu', phien_ban=1),
    'ocr.chot_luot': dict(trang_thai='da_tieu'),
    'ocr.doc_luot': dict(trang_thai='chua_ro', phien_ban=2),
}


def lease():
    return GiuViec(viec_id=uuid4(), buoc_viec_id=uuid4(), lan_thu_id=uuid4(),
        phap_nhan_id=uuid4(), module='crm', hanh_dong='CRM:OCR',
        instance_id=uuid4(), the_he=1,
        giu_den=datetime.now(timezone.utc) + timedelta(minutes=5),
        ma=MaBiMat('OCR_DEMO_LEASE_' + 'x' * 32))


class KenhGia(engine.KenhCore):
    def __init__(self):
        self.nhan = Mock(side_effect=lambda operation, giu, **payload: dict(DAU_RA[operation]))

    def goi(self, operation, giu_viec, **payload):
        return self.nhan(operation, giu_viec, **payload)


class DTOLuotOCRTests(unittest.TestCase):
    def test_phan_loai_engine_va_chi_engine_duoc_cap_proof(self):
        self.assertEqual(k.OPERATION_OCR_GHI, {'ocr.giu_luot', 'ocr.chot_luot'})
        self.assertEqual(k.OPERATION_OCR_DOC, {'ocr.doc_luot'})
        for operation in DAU_VAO:
            with self.subTest(operation=operation):
                self.assertIn(operation, k.OPERATION_ENGINE)
                self.assertNotIn(operation, k.OPERATION_CORE | k.OPERATION_CUC_BO)
                h = dict(kieu='request', operation=operation)
                for vai in ('core', 'con'):
                    k.BoProof(b'x' * 32, 'ocr-demo', vai=vai,
                              loai_con='engine').kiem_operation(h)
                    with self.assertRaises(k.LoiKenh) as bat:
                        k.BoProof(b'x' * 32, 'ocr-demo', vai=vai,
                                  loai_con='module').kiem_operation(h)
                    self.assertEqual(bat.exception.ma, 'KENH_KHONG_DU_QUYEN')

    def test_dto_hop_le_tra_ban_sao_dong(self):
        for phan_hoi, tap_mau in ((False, DAU_VAO), (True, DAU_RA)):
            for operation, data in tap_mau.items():
                with self.subTest(operation=operation, phan_hoi=phan_hoi):
                    out = k.kiem_dto_ocr(operation, data, phan_hoi=phan_hoi)
                    self.assertEqual(out, data)
                    self.assertIsNot(out, data)

    def test_cac_trang_thai_doc_va_hai_ket_qua_chot(self):
        for status in ('khong_co', 'dang_giu', 'chua_ro', 'da_tieu', 'hoan_trang'):
            data = dict(trang_thai=status, phien_ban=None if status == 'khong_co' else 2)
            k.kiem_dto_ocr('ocr.doc_luot', data, phan_hoi=True)
        for status in ('da_tieu', 'hoan_trang'):
            k.kiem_dto_ocr('ocr.chot_luot', DAU_VAO['ocr.chot_luot'] | {'ket_qua': status})
            k.kiem_dto_ocr('ocr.chot_luot', dict(trang_thai=status), phan_hoi=True)

    def test_gioi_han_so_trang_va_cas_khop_core(self):
        k.kiem_dto_ocr('ocr.giu_luot', dict(bam_noi_dung=BAM, so_trang=2**31 - 1))
        k.kiem_dto_ocr('ocr.chot_luot', DAU_VAO['ocr.chot_luot'] | {'phien_ban': 2**63 - 2})
        for value in (False, True, None, 0, -1, 1.0, '1', 2**64):
            for operation, field in (('ocr.giu_luot', 'so_trang'), ('ocr.chot_luot', 'phien_ban')):
                with self.subTest(operation=operation, value=value), self.assertRaises(k.LoiKenh):
                    k.kiem_dto_ocr(operation, DAU_VAO[operation] | {field: value})
        for operation, field, value in (('ocr.giu_luot', 'so_trang', 2**31),
                                        ('ocr.chot_luot', 'phien_ban', 2**63 - 1)):
            with self.assertRaises(k.LoiKenh):
                k.kiem_dto_ocr(operation, DAU_VAO[operation] | {field: value})

    def test_bam_chi_nhan_64_hex_thuong_khong_lo_gia_tri(self):
        for value in (None, 1, True, [], {}, '', BAM.upper(), BAM[:-1], BAM + '0',
                      'g' * 64, BAM + '\n'):
            for operation in ('ocr.giu_luot', 'ocr.doc_luot'):
                with self.subTest(operation=operation, value=value), self.assertRaises(k.LoiKenh) as bat:
                    k.kiem_dto_ocr(operation, DAU_VAO[operation] | {'bam_noi_dung': value})
                self.assertEqual(str(bat.exception), 'KENH_DU_LIEU_KHONG_HOP_LE')

    def test_ma_tuong_quan_va_ket_qua_khong_hop_le(self):
        for value in (None, False, [], '', 'x' * 129, '../demo', 'mã DEMO', MA + '\n'):
            with self.subTest(value=value), self.assertRaises(k.LoiKenh):
                k.kiem_dto_ocr('ocr.chot_luot', DAU_VAO['ocr.chot_luot'] | {'ma_tuong_quan': value})
            with self.assertRaises(k.LoiKenh):
                k.kiem_dto_ocr('ocr.giu_luot', DAU_RA['ocr.giu_luot'] | {'ma_tuong_quan': value},
                               phan_hoi=True)
        for value in (None, [], {}, True, 'chua_ro', 'dang_giu', 'DA_TIEU_TRANG'):
            with self.subTest(value=value), self.assertRaises(k.LoiKenh):
                k.kiem_dto_ocr('ocr.chot_luot', DAU_VAO['ocr.chot_luot'] | {'ket_qua': value})

    def test_dto_tu_choi_thieu_truong_va_danh_tinh_tu_khai(self):
        for phan_hoi, tap_mau in ((False, DAU_VAO), (True, DAU_RA)):
            for operation, data in tap_mau.items():
                for field in data:
                    with self.subTest(operation=operation, thieu=field, phan_hoi=phan_hoi), \
                            self.assertRaises(k.LoiKenh):
                        k.kiem_dto_ocr(operation, {key: v for key, v in data.items() if key != field},
                                       phan_hoi=phan_hoi)
                for field in ('phap_nhan_id', 'module', 'actor', 'viec_id', 'lan_thu_id',
                              'khoa', 'truong_la'):
                    with self.subTest(operation=operation, thua=field, phan_hoi=phan_hoi), \
                            self.assertRaises(k.LoiKenh):
                        k.kiem_dto_ocr(operation, data | {field: BAM}, phan_hoi=phan_hoi)

    def test_phien_ban_phan_hoi_la_so_nguyen_khop_core(self):
        # SQL 126 giữ phiên bản trong ket_qua JSONB, không dùng row_version.
        cac_mau = [('ocr.giu_luot', DAU_RA['ocr.giu_luot'])]
        cac_mau.extend(('ocr.doc_luot', dict(trang_thai=status, phien_ban=2))
                      for status in ('dang_giu', 'chua_ro', 'da_tieu', 'hoan_trang'))
        for operation, mau in cac_mau:
            for value in (1, 2, 2**63 - 1):
                data = mau | {'phien_ban': value}
                with self.subTest(operation=operation, status=mau['trang_thai'], value=value):
                    out = k.kiem_dto_ocr(operation, data, phan_hoi=True)
                    self.assertIs(type(out['phien_ban']), int)
                    self.assertEqual(out['phien_ban'], value)
            for value in (False, True, None, 0, -1, 1.0, '1', [], {}, 2**63):
                with self.subTest(operation=operation, status=mau['trang_thai'], value=value), \
                        self.assertRaises(k.LoiKenh) as bat:
                    k.kiem_dto_ocr(operation, mau | {'phien_ban': value}, phan_hoi=True)
                self.assertEqual(bat.exception.ma, 'PHAN_HOI_SAI_CONTRACT')
            with self.subTest(operation=operation, status=mau['trang_thai'], thieu='phien_ban'), \
                    self.assertRaises(k.LoiKenh) as bat:
                k.kiem_dto_ocr(operation, {key: value for key, value in mau.items()
                                         if key != 'phien_ban'}, phan_hoi=True)
            self.assertEqual(bat.exception.ma, 'PHAN_HOI_SAI_CONTRACT')

    def test_doc_khong_co_khong_tao_phien_ban_gia(self):
        data = dict(trang_thai='khong_co')
        self.assertEqual(k.kiem_dto_ocr('ocr.doc_luot', data, phan_hoi=True), data)
        data_null = data | {'phien_ban': None}
        out = k.kiem_dto_ocr('ocr.doc_luot', data_null, phan_hoi=True)
        self.assertEqual(out, data_null)
        self.assertIsNot(out, data_null)
        self.assertIsNone(out['phien_ban'])
        for value in (False, True, 0, -1, 1, 2**63 - 1, 1.0, '1', [], {}):
            with self.subTest(value=value), self.assertRaises(k.LoiKenh) as bat:
                k.kiem_dto_ocr('ocr.doc_luot', data | {'phien_ban': value}, phan_hoi=True)
            self.assertEqual(bat.exception.ma, 'PHAN_HOI_SAI_CONTRACT')

    def test_dto_phan_hoi_khong_tra_bam_va_chot_khong_tra_cas(self):
        for operation, data in DAU_RA.items():
            with self.subTest(operation=operation), self.assertRaises(k.LoiKenh) as bat:
                k.kiem_dto_ocr(operation, data | {'bam_noi_dung': BAM}, phan_hoi=True)
            self.assertEqual(bat.exception.ma, 'PHAN_HOI_SAI_CONTRACT')
        with self.assertRaises(k.LoiKenh) as bat:
            k.kiem_dto_ocr('ocr.chot_luot', DAU_RA['ocr.chot_luot'] | {'phien_ban': 2},
                           phan_hoi=True)
        self.assertEqual(bat.exception.ma, 'PHAN_HOI_SAI_CONTRACT')

    def test_dto_sai_kieu_operation_va_trang_thai(self):
        for operation in (None, [], {}, 'engine.ocr.giu_luot', 'ocr.xoa_luot'):
            with self.subTest(operation=operation), self.assertRaises(k.LoiKenh):
                k.kiem_dto_ocr(operation, {})
        for operation in DAU_VAO:
            for data in (None, [], 'DEMO', False):
                with self.subTest(operation=operation, data=data), self.assertRaises(k.LoiKenh):
                    k.kiem_dto_ocr(operation, data)
            for status in (None, [], {}, False, 'GIU', 'khac', BAM):
                data = DAU_RA[operation] | {'trang_thai': status}
                with self.subTest(operation=operation, status=status), self.assertRaises(k.LoiKenh):
                    k.kiem_dto_ocr(operation, data, phan_hoi=True)


class SDKLuotOCRTests(unittest.TestCase):
    def setUp(self):
        self.giu = lease()
        self.now = self.giu.giu_den - timedelta(minutes=1)
        self.kenh = KenhGia()
        self.sdk = self.api(self.giu)

    def api(self, giu):
        return engine.SDKEngine(giu, kenh_core=self.kenh, dong_ho=lambda: self.now)

    def goi(self, operation, data=None, sdk=None):
        return getattr(sdk or self.sdk, operation.replace('.', '_'))(**(data or DAU_VAO[operation]))

    def khoa_cuoi(self):
        return self.kenh.nhan.call_args.kwargs['khoa']

    def test_ba_api_gui_dung_ten_dto_va_lease_khong_them_danh_tinh(self):
        for operation, data in DAU_VAO.items():
            with self.subTest(operation=operation):
                self.assertEqual(self.goi(operation), DAU_RA[operation])
                call = self.kenh.nhan.call_args
                self.assertEqual(call.args, (operation, self.giu))
                self.assertEqual({key: v for key, v in call.kwargs.items() if key != 'khoa'}, data)
                if operation in k.OPERATION_OCR_GHI:
                    self.assertRegex(call.kwargs['khoa'], '^[0-9a-f]{64}$')
                    self.assertNotEqual(call.kwargs['khoa'], BAM)
                else:
                    self.assertIsNone(call.kwargs['khoa'])

    def test_khoa_con_on_dinh_qua_retry_dung_lai_sdk_va_heartbeat(self):
        for operation in k.OPERATION_OCR_GHI:
            self.goi(operation)
            khoa = self.khoa_cuoi()
            for sdk in (self.sdk, self.api(replace(self.giu,
                    ma=MaBiMat(self.giu.ma.lay_de_truyen())))):
                self.goi(operation, sdk=sdk)
                self.assertEqual(self.khoa_cuoi(), khoa)
            moi = replace(self.giu, giu_den=self.giu.giu_den + timedelta(minutes=2))
            self.kenh.nhan.return_value = moi
            self.kenh.nhan.side_effect = None
            self.sdk.heartbeat()
            self.kenh.nhan.side_effect = lambda op, giu, **payload: dict(DAU_RA[op])
            self.goi(operation)
            self.assertEqual(self.khoa_cuoi(), khoa)

    def test_khoa_doi_theo_lease_doi_tuong_va_cas(self):
        for operation in k.OPERATION_OCR_GHI:
            self.goi(operation)
            khoa = self.khoa_cuoi()
            for giu in (replace(self.giu, viec_id=uuid4()), replace(self.giu, lan_thu_id=uuid4()),
                        replace(self.giu, the_he=2)):
                self.goi(operation, sdk=self.api(giu))
                self.assertNotEqual(self.khoa_cuoi(), khoa)
            field = 'bam_noi_dung' if operation == 'ocr.giu_luot' else 'ma_tuong_quan'
            self.goi(operation, DAU_VAO[operation] | {field: 'a' * 64})
            self.assertNotEqual(self.khoa_cuoi(), khoa)
        self.goi('ocr.chot_luot')
        khoa = self.khoa_cuoi()
        self.goi('ocr.chot_luot', DAU_VAO['ocr.chot_luot'] | {'phien_ban': 2})
        self.assertNotEqual(self.khoa_cuoi(), khoa)

    def test_cung_giu_hoac_cas_khong_doi_khoa_khi_noi_dung_ghi_lech(self):
        # Core sẽ phát hiện cùng khóa nhưng nội dung khác, không tạo lượt ghi mới.
        self.goi('ocr.giu_luot')
        khoa = self.khoa_cuoi()
        self.goi('ocr.giu_luot', DAU_VAO['ocr.giu_luot'] | {'so_trang': 3})
        self.assertEqual(self.khoa_cuoi(), khoa)
        self.goi('ocr.chot_luot')
        khoa = self.khoa_cuoi()
        self.kenh.nhan.side_effect = lambda op, giu, **payload: {'trang_thai': payload['ket_qua']}
        self.goi('ocr.chot_luot', DAU_VAO['ocr.chot_luot'] | {'ket_qua': 'hoan_trang'})
        self.assertEqual(self.khoa_cuoi(), khoa)

    def test_du_lieu_sai_bi_chan_truoc_khi_gui(self):
        for operation, data in (
                ('ocr.giu_luot', DAU_VAO['ocr.giu_luot'] | {'so_trang': True}),
                ('ocr.doc_luot', dict(bam_noi_dung=BAM + 'sai')),
                ('ocr.chot_luot', DAU_VAO['ocr.chot_luot'] | {'phien_ban': 0}),
                ('ocr.chot_luot', DAU_VAO['ocr.chot_luot'] | {'ket_qua': 'chua_ro'})):
            with self.subTest(operation=operation), self.assertRaises(engine.LoiEngine) as bat:
                self.goi(operation, data)
            self.assertEqual((bat.exception.ma, bat.exception.http_status), ('OCR_LUOT_DAU_VAO', 400))
            self.assertNotIn(BAM, str(bat.exception))
        self.kenh.nhan.assert_not_called()

    def test_payload_tu_khai_phap_nhan_module_hoac_khoa_bi_tu_choi(self):
        for operation in DAU_VAO:
            for field in ('phap_nhan_id', 'module', 'khoa', 'lan_thu_id'):
                with self.subTest(operation=operation, field=field), self.assertRaises(TypeError):
                    self.goi(operation, DAU_VAO[operation] | {field: BAM})
        self.kenh.nhan.assert_not_called()

    def test_lease_het_han_chan_ca_ba_api(self):
        self.now = self.giu.giu_den
        for operation in DAU_VAO:
            with self.subTest(operation=operation), self.assertRaises(engine.LoiEngine) as bat:
                self.goi(operation)
            self.assertEqual((bat.exception.ma, bat.exception.http_status), ('VIEC_MAT_LEASE', 409))
        self.kenh.nhan.assert_not_called()

    def test_doc_tra_phien_ban_cua_luot_hien_co(self):
        for status in ('khong_co', 'dang_giu', 'chua_ro', 'da_tieu', 'hoan_trang'):
            result = dict(trang_thai=status, phien_ban=None if status == 'khong_co' else 7)
            self.kenh.nhan.side_effect = None
            self.kenh.nhan.return_value = result
            with self.subTest(status=status):
                out = self.goi('ocr.doc_luot')
                self.assertEqual(out, result)
                self.assertIsNot(out, result)
                if status == 'khong_co':
                    self.assertIsNone(out['phien_ban'])
                else:
                    self.assertIs(type(out['phien_ban']), int)
        self.assertTrue(all(call.args[0] == 'ocr.doc_luot' for call in self.kenh.nhan.call_args_list))

    def test_doc_chan_phien_ban_sai_theo_tung_trang_thai(self):
        self.kenh.nhan.side_effect = None
        for status in ('khong_co', 'dang_giu', 'chua_ro', 'da_tieu', 'hoan_trang'):
            results = [dict(trang_thai=status, phien_ban=value)
                       for value in (False, True, 0, -1, 1.0, '1', [], {}, 2**63)]
            if status == 'khong_co':
                results.extend(dict(trang_thai=status, phien_ban=value)
                               for value in (1, 2**63 - 1))
            else:
                results.extend((dict(trang_thai=status), dict(trang_thai=status, phien_ban=None)))
            for result in results:
                self.kenh.nhan.return_value = result
                with self.subTest(result=result), self.assertRaises(engine.LoiEngine) as bat:
                    self.goi('ocr.doc_luot')
                self.assertEqual((bat.exception.ma, bat.exception.http_status),
                                 ('PHAN_HOI_SAI_CONTRACT', 502))

    def test_doc_khong_co_null_khong_duoc_dung_chot_luot(self):
        self.kenh.nhan.side_effect = None
        self.kenh.nhan.return_value = dict(trang_thai='khong_co', phien_ban=None)
        luot = self.goi('ocr.doc_luot')
        with self.assertRaises(engine.LoiEngine) as bat:
            self.sdk.ocr_chot_luot(ma_tuong_quan=MA, ket_qua='da_tieu',
                                   phien_ban=luot['phien_ban'])
        self.assertEqual((bat.exception.ma, bat.exception.http_status), ('OCR_LUOT_DAU_VAO', 400))
        self.kenh.nhan.assert_called_once()

    def test_chot_gui_lai_dung_phien_ban_core_tra_tu_giu_hoac_doc(self):
        for operation, phien_ban in (('ocr.giu_luot', 1), ('ocr.doc_luot', 7)):
            with self.subTest(operation=operation):
                self.kenh.nhan.side_effect = [
                    DAU_RA[operation] | {'phien_ban': phien_ban},
                    DAU_RA['ocr.chot_luot'],
                ]
                luot = self.goi(operation)
                self.assertEqual(self.sdk.ocr_chot_luot(ma_tuong_quan=MA,
                    ket_qua='da_tieu', phien_ban=luot['phien_ban']), DAU_RA['ocr.chot_luot'])
                call = self.kenh.nhan.call_args
                self.assertEqual(call.args, ('ocr.chot_luot', self.giu))
                self.assertIs(type(call.kwargs['phien_ban']), int)
                self.assertEqual(call.kwargs['phien_ban'], phien_ban)

    def test_phan_hoi_sai_hoac_lo_bam_bi_chan(self):
        for operation in DAU_VAO:
            results = [None, [], DAU_RA[operation] | {'bam_noi_dung': BAM},
                       DAU_RA[operation] | {'module': 'crm'},
                       DAU_RA[operation] | {'trang_thai': BAM}]
            if operation in ('ocr.giu_luot', 'ocr.doc_luot'):
                results.append({key: v for key, v in DAU_RA[operation].items()
                                if key != 'phien_ban'})
                results.extend(DAU_RA[operation] | {'phien_ban': value}
                               for value in (None, False, True, 0, -1, 1.0, '1', 2**63))
            for result in results:
                self.kenh.nhan.side_effect = None
                self.kenh.nhan.return_value = result
                with self.subTest(operation=operation, result=result), self.assertRaises(engine.LoiEngine) as bat:
                    self.goi(operation)
                self.assertEqual((bat.exception.ma, bat.exception.http_status), ('PHAN_HOI_SAI_CONTRACT', 502))
                self.assertNotIn(BAM, ''.join(traceback.format_exception(bat.exception)))
                self.assertIsNone(bat.exception.__context__)
                self.assertIsNone(bat.exception.__cause__)

    def test_chot_khong_nhan_ket_qua_khac_yeu_cau(self):
        self.kenh.nhan.side_effect = None
        self.kenh.nhan.return_value = dict(trang_thai='hoan_trang')
        with self.assertRaises(engine.LoiEngine) as bat:
            self.goi('ocr.chot_luot')
        self.assertEqual(bat.exception.ma, 'PHAN_HOI_SAI_CONTRACT')

    def test_loi_core_huu_han_khong_lo_bam_khong_tu_retry(self):
        for operation in DAU_VAO:
            for code, expect, status in (
                    ('OCR_LUOT_DANG_BI_CHAN', 'OCR_LUOT_DANG_BI_CHAN', 409),
                    ('OCR_LUOT_XUNG_DOT', 'OCR_LUOT_XUNG_DOT', 409),
                    ('42501', '42501', 403), ('MAT_LEASE', 'VIEC_MAT_LEASE', 409),
                    ('PHAN_HOI_QUA_HAN', 'PHAN_HOI_QUA_HAN', 504),
                    (BAM, 'ENGINE_CORE', 503), (dict(bam=BAM), 'ENGINE_CORE', 503)):
                exc = RuntimeError(BAM)
                exc.ma = code
                exc.bam = BAM
                self.kenh.nhan.reset_mock()
                self.kenh.nhan.side_effect = exc
                with self.subTest(operation=operation, code=code), self.assertRaises(engine.LoiEngine) as bat:
                    self.goi(operation)
                loi = bat.exception
                self.assertEqual((loi.ma, loi.http_status), (expect, status))
                self.assertFalse(loi.thu_lai_duoc)
                self.assertNotIn(BAM, str(loi) + repr(loi) + repr(vars(loi)))
                self.assertNotIn(BAM, ''.join(traceback.format_exception(loi)))
                self.assertIsNone(loi.__context__)
                self.assertIsNone(loi.__cause__)
                self.kenh.nhan.assert_called_once()

    def test_moi_ngoai_le_mat_phan_hoi_giu_nguyen_khoa_lan_sau(self):
        self.kenh.nhan.side_effect = TimeoutError(BAM)
        with self.assertRaises(engine.LoiEngine):
            self.goi('ocr.giu_luot')
        khoa = self.khoa_cuoi()
        self.kenh.nhan.side_effect = lambda op, giu, **payload: dict(DAU_RA[op])
        self.goi('ocr.giu_luot')
        self.assertEqual(self.khoa_cuoi(), khoa)


if __name__ == '__main__':
    unittest.main()
