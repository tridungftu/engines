"""OCR-VUNG: ảnh DEMO trong RAM, Pillow/numpy thật; chỉ mock nhận dạng/IPC."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest.mock import Mock, patch
from uuid import UUID

import numpy as np
from PIL import Image

from kho_tri_thuc.engines.e_ocr import chay, vung
from kho_tri_thuc.sdk_core.engine import GiuViec, KenhCore, SDKEngine
from kho_tri_thuc.sdk_core.ngu_canh import MaBiMat
from kho_tri_thuc.sdk_core.primitives import DataError


GOI = Path(__file__).resolve().parents[1]
TEP_ID = '10000000-0000-4000-8000-000000000001'
POINTS = [[4, 3], [44, 3], [44, 23], [4, 23]]
TEXT = 'DEMO Ánh Dương, 0007, 1.234,50 VND, 06/11/2026'


def anh_demo(*, fmt='PNG', mode='RGB'):
    stream = io.BytesIO()
    Image.new(mode, (60, 40), 'white').save(stream, format=fmt)
    return stream.getvalue()


def request(raw, *, mime='image/png', points=None):
    return dict(contract='vung_anh.v1', phien_ban='1.0.0', bon_diem=deepcopy(POINTS if points is None else points),
                tham_chieu_tep=dict(contract='tham_chieu_tep.v1', phien_ban='1.0.0', tep_id=TEP_ID,
                                   ten_tep='vung-DEMO.png', mime=mime, kich_thuoc=len(raw),
                                   sha256=hashlib.sha256(raw).hexdigest(), het_han_luc=None))


class HinhHocTests(unittest.TestCase):
    def test_kich_thuoc_goc_va_thu_tu_quAD_pillow(self):
        image = Image.new('RGB', (100, 100), 'white')
        points = [[10, 10], [75, 15], [65, 80], [15, 60]]
        original = np.array(points, dtype=np.float32)
        expected = (max(int(np.linalg.norm(original[0] - original[1])),
                        int(np.linalg.norm(original[2] - original[3])), 2),
                    max(int(np.linalg.norm(original[0] - original[3])),
                        int(np.linalg.norm(original[1] - original[2])), 2))
        transform = Image.Image.transform
        seen = []

        def spy(self, size, method, data, **kwargs):
            seen.append((size, method, data, kwargs))
            return transform(self, size, method, data, **kwargs)

        with patch.object(Image.Image, 'transform', spy):
            crop = vung.crop_quad(image, points)
        self.assertEqual(crop.size, expected)
        self.assertEqual(seen[0], (expected, Image.Transform.QUAD,
                                  [10., 10., 15., 60., 65., 80., 75., 15.],
                                  {'resample': Image.Resampling.BICUBIC}))
        self.assertEqual(points, [[10, 10], [75, 15], [65, 80], [15, 60]])

    def test_huong_anh_giu_dung_bon_goc(self):
        image = Image.new('RGB', (80, 80))
        for y in range(80):
            for x in range(80):
                image.putpixel((x, y), (255, 0, 0) if x < 40 and y < 40 else
                               (0, 255, 0) if y < 40 else (0, 0, 255) if x >= 40 else (255, 255, 0))
        crop = vung.crop_quad(image, [[0, 0], [79, 0], [79, 79], [0, 79]])
        self.assertEqual(crop.size, (79, 79))
        self.assertEqual([crop.getpixel(p) for p in [(5, 5), (73, 5), (73, 73), (5, 73)]],
                         [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)])

    def test_toi_thieu_hai_pixel_nhu_goc(self):
        self.assertEqual(vung.crop_quad(Image.new('RGB', (4, 4)),
                                       [[1, 1], [1.5, 1], [1.5, 1.5], [1, 1.5]]).size, (2, 2))

    def test_vung_sai_bi_chan_truoc_transform(self):
        bad = [[], [[0, 0]] * 4, [[0, 0], [1, 1], [2, 2], [3, 3]],
               [[1, 1], [8, 8], [8, 1], [1, 8]],  # tự cắt
               [[1, 1], [8, 1], [3, 3], [1, 8]],  # lõm
               [[-1, 1], [8, 1], [8, 8], [1, 8]],
               [[1, 1], [10, 1], [8, 8], [1, 8]],
               [[1, 1], [8, 1], [8, 10], [1, 8]],
               [[float('nan'), 1], [8, 1], [8, 8], [1, 8]],
               [[float('inf'), 1], [8, 1], [8, 8], [1, 8]],
               [['1', 1], [8, 1], [8, 8], [1, 8]],
               [[True, False]] * 4, [0, 0, 8, 0, 8, 8, 0, 8]]
        with patch.object(Image.Image, 'transform', side_effect=AssertionError('Không được cắt')):
            for points in bad:
                with self.subTest(points=points), self.assertRaises(DataError):
                    vung.crop_quad(Image.new('RGB', (10, 10)), points)

    def test_gioi_han_anh_va_dich_truoc_transform(self):
        with patch.object(vung, 'MAX_PIXELS', 100), self.assertRaises(DataError):
            vung.crop_quad(Image.new('RGB', (11, 10)), POINTS)
        # Tích cạnh đích có thể lớn hơn diện tích ảnh đầu vào.
        with patch.object(vung, 'MAX_PIXELS', 10100), self.assertRaises(DataError):
            vung.crop_quad(Image.new('RGB', (100, 100)), [[0, 0], [99, 98], [99, 99], [0, 99]])

    def test_vung_ngoai_anh_giu_loi_va_huong_dan_chon_lai(self):
        image = Image.new('RGB', (10, 10))
        for points in ([[-1, 1], [8, 1], [8, 8], [1, 8]],
                       [[1, 1], [10, 1], [8, 8], [1, 8]],
                       [[1, 1], [8, 1], [8, 10], [1, 8]]):
            with self.subTest(points=points), self.assertRaises(DataError) as caught:
                vung.crop_quad(image, points)
            self.assertEqual(caught.exception.code, 'OCR_VUNG_NGOAI_ANH')
            self.assertEqual(str(caught.exception), 'Vùng chọn nằm ngoài ảnh; cần chọn lại trong ảnh.')

    def test_vung_qua_lon_giu_loi_va_huong_dan_chon_nho_hon(self):
        with patch.object(vung, 'MAX_PIXELS', 10100), self.assertRaises(DataError) as caught:
            vung.crop_quad(Image.new('RGB', (100, 100)), [[0, 0], [99, 98], [99, 99], [0, 99]])
        self.assertEqual(caught.exception.code, 'OCR_VUNG_QUA_LON')
        self.assertEqual(str(caught.exception),
                         'Vùng chọn vượt 20 triệu điểm ảnh; cần chọn vùng nhỏ hơn.')


class TrichVungTests(unittest.TestCase):
    def test_chi_ocr_anh_da_cat_va_giu_chu_nguon(self):
        raw = anh_demo()
        req = request(raw)
        original = deepcopy(req)

        def read(png):
            with Image.open(io.BytesIO(png)) as image:
                self.assertEqual((image.format, image.mode, image.size), ('PNG', 'RGB', (40, 20)))
            self.assertNotEqual(png, raw)
            return TEXT

        result = vung.trich_vung(raw, req, revision=7, image_text=read)
        self.assertEqual(result['van_ban'], TEXT)
        self.assertEqual(result['revision'], 7)
        self.assertEqual(result['nguon_tep_ids'], [TEP_ID])
        self.assertEqual(result['nguon_doc'], 'mask_ocr_tesseract')
        self.assertTrue(result['nghi_ngo'])
        self.assertFalse(result['vung_rong'])
        self.assertIsNone(result['do_tin_cay'])
        self.assertEqual(result['ly_do_nghi_ngo'], ['chua_co_do_tin_cay'])
        self.assertEqual(req, original)
        result['bon_diem'][0][0] = 30
        self.assertEqual(req, original)
        json.dumps(result, ensure_ascii=False, allow_nan=False)

    def test_rong_va_khoang_trang_co_co_nghi_ngo(self):
        raw = anh_demo()
        for text in ('', ' \n\t'):
            with self.subTest(text=text):
                result = vung.trich_vung(raw, request(raw), image_text=lambda _: text)
                self.assertEqual(result['van_ban'], text)
                self.assertTrue(result['vung_rong'])
                self.assertTrue(result['nghi_ngo'])
                self.assertIn('vung_rong', result['ly_do_nghi_ngo'])

    def test_jpeg_va_anh_bang_mau(self):
        for fmt, mode in (('JPEG', 'RGB'), ('PNG', 'P'), ('PNG', '1'), ('PNG', 'RGBA')):
            with self.subTest(fmt=fmt, mode=mode):
                raw = anh_demo(fmt=fmt, mode=mode)
                result = vung.trich_vung(raw, request(raw, mime='image/jpeg' if fmt == 'JPEG' else 'image/png'),
                                         image_text=lambda _: TEXT)
                self.assertEqual(result['van_ban'], TEXT)

    def test_nguon_yeu_cau_va_revision_sai_khong_ocr(self):
        raw = anh_demo()
        req = request(raw)
        bad = []
        for key, value in [('mime', 'application/pdf'), ('sha256', '0' * 64),
                           ('kich_thuoc', len(raw) + 1), ('ten_tep', '../anh.png'),
                           ('tep_id', 'khong-phai-id'), ('het_han_luc', '2000-01-01T00:00:00Z'),
                           ('het_han_luc', 'sai'), ('sha256', None)]:
            item = deepcopy(req)
            item['tham_chieu_tep'][key] = value
            bad.append(item)
        item = deepcopy(req)
        item['duong_dan'] = 'khong-duoc-doc'
        bad.extend([item, {}, request(raw, points=[[0, 0]] * 4)])
        for value in (True, float('inf'), 10**400):
            item = deepcopy(req)
            item['bon_diem'][0][0] = value
            bad.append(item)
        read = Mock(side_effect=AssertionError('Không được OCR'))
        for item in bad:
            with self.subTest(item=item), self.assertRaises(DataError):
                vung.trich_vung(raw, item, image_text=read)
        for revision in (0, -1, True, 1.5):
            with self.subTest(revision=revision), self.assertRaises(DataError):
                vung.trich_vung(raw, req, revision=revision, image_text=read)
        read.assert_not_called()

    def test_anh_hong_mime_khong_khop_khong_ocr(self):
        read = Mock(side_effect=AssertionError('Không được OCR'))
        for raw, mime in ((b'DEMO anh hong', 'image/png'), (anh_demo(), 'image/jpeg')):
            with self.subTest(mime=mime), self.assertRaises(DataError):
                vung.trich_vung(raw, request(raw, mime=mime), image_text=read)
        read.assert_not_called()

    def test_ocr_loi_khong_tra_chu_gia_va_khong_lo_chi_tiet(self):
        raw = anh_demo()
        for value in (None, {}, b'chu', 'x' * 500001):
            with self.subTest(value=type(value)), self.assertRaises(DataError):
                vung.trich_vung(raw, request(raw), image_text=lambda _: value)
        with self.assertRaises(DataError) as caught:
            vung.trich_vung(raw, request(raw), image_text=Mock(side_effect=RuntimeError('DEMO-chi-tiet-rieng')))
        self.assertNotIn('DEMO-chi-tiet-rieng', str(caught.exception))

    def test_thieu_dependency_bao_loi_tieng_viet(self):
        raw = anh_demo()
        with patch.object(vung, '_nhap_parser_nguon', side_effect=ModuleNotFoundError('DEMO-thieu-dependency')):
            with self.assertRaises(DataError) as caught:
                vung.trich_vung(raw, request(raw))
        self.assertEqual(caught.exception.code, 'OCR_VUNG_CHUA_SAN_SANG')
        self.assertNotIn('DEMO-thieu-dependency', str(caught.exception))

    def test_mac_dinh_dung_dung_image_text_vendor_khong_doc_cau_hinh(self):
        # Chạy chính image_text nguồn, mock MuPDF/Tesseract; không đọc model/config.
        mupdf, xml = ModuleType('pymupdf'), ModuleType('defusedxml')
        xml.ElementTree = ModuleType('ElementTree')
        pix = Mock(width=40, height=20, alpha=False)
        pix.colorspace.n = 3
        pix.pdfocr_tobytes.return_value = b'DEMO PDF OCR'
        mupdf.Pixmap = Mock(return_value=pix)
        pdf = Mock()
        pdf.__getitem__ = Mock(return_value=Mock(get_text=Mock(return_value=TEXT)))
        context = Mock()
        context.__enter__ = Mock(return_value=pdf)
        context.__exit__ = Mock(return_value=False)
        mupdf.open = Mock(return_value=context)
        with patch.dict(sys.modules, {'pymupdf': mupdf, 'defusedxml': xml}):
            extraction, _ = vung._nhap_parser_nguon()
            with patch.object(extraction, 'pymupdf', mupdf), \
                    patch.object(extraction, 'require_ocr', return_value={'language': 'vie+eng', 'tessdata': 'DEMO'}), \
                    patch.object(extraction, 'image_text', wraps=extraction.image_text) as read:
                raw = anh_demo()
                result = vung.trich_vung(raw, request(raw))
            read.assert_called_once()
        self.assertEqual(result['van_ban'], TEXT)
        pix.pdfocr_tobytes.assert_called_once_with(language='vie+eng', tessdata='DEMO')


class KenhGia(KenhCore):
    def __init__(self, raw, *, mat_ack=False):
        self.anh = raw
        self.input = dict(capability=vung.CAPABILITY, yeu_cau=request(raw), revision_tep_truoc=2,
                          du_lieu_ket_qua=dict(bien_the='vung', ma_contract='van_ban_vung.v1',
                                              phien_ban_contract='1.0.0', trang_thai='CAN_SOAT', ly_do=None,
                                              revision_truoc=4, nguon=[]))
        self.calls, self.outputs, self.mat_ack = [], [], mat_ack

    def goi(self, operation, giu_viec, **payload):
        self.calls.append(operation)
        if operation == 'doc_dau_vao':
            return self.input
        if operation == 'mo_doc':
            assert payload['tep_id'] == TEP_ID
            self.stream = io.BytesIO(self.anh)
            return self.stream
        if operation == 'ghi_ket_qua':
            self.outputs.append(payload['luong'].read())
            self.metadata, self.ten = payload['du_lieu'], payload['ten']
            if self.mat_ack and len(self.outputs) == 1:
                raise RuntimeError('DEMO mất ACK')
            return {'da_ban_giao': True}
        raise AssertionError(operation)


def sdk(kenh):
    now = datetime(2026, 11, 6, tzinfo=timezone.utc)
    lease = GiuViec(UUID(int=1), UUID(int=2), UUID(int=3), UUID(int=4),
                    'demo', 'ocr', UUID(int=5), 1, now + timedelta(minutes=1), MaBiMat('DEMO'))
    return SDKEngine(lease, kenh_core=kenh, dong_ho=lambda: now)


class DinhTuyenTests(unittest.TestCase):
    def test_sdk_mo_anh_va_ack_retry_khong_ocr_lai(self):
        kenh = KenhGia(anh_demo(), mat_ack=True)
        read = Mock(return_value=TEXT)
        backend = Mock(side_effect=AssertionError('Không gọi backend DEMO'))
        with patch.object(chay.time, 'sleep'):
            ack = chay.xu_ly_viec(sdk(kenh), backend=backend, image_text=read)
        self.assertEqual(ack, {'da_ban_giao': True})
        self.assertEqual(kenh.calls, ['doc_dau_vao', 'mo_doc', 'ghi_ket_qua', 'ghi_ket_qua'])
        self.assertTrue(kenh.stream.closed)
        self.assertEqual(kenh.outputs[0], kenh.outputs[1])
        self.assertEqual(json.loads(kenh.outputs[0])['revision'], 5)
        self.assertEqual(kenh.ten, 'ocr-vung.json')
        self.assertEqual(kenh.metadata, kenh.input['du_lieu_ket_qua'])
        read.assert_called_once()
        backend.xu_ly.assert_not_called()

    def test_nang_luc_va_metadata_sai_chan_truoc_mo_anh(self):
        for capability, contract in (('ocr.chua_co@1', 'van_ban_vung.v1'),
                                     (vung.CAPABILITY, 'van_ban_tai_lieu.v1')):
            kenh = KenhGia(anh_demo())
            kenh.input['capability'] = capability
            kenh.input['du_lieu_ket_qua']['ma_contract'] = contract
            with self.subTest(capability=capability), self.assertRaises(DataError):
                chay.xu_ly_viec(sdk(kenh), backend=Mock())
            self.assertEqual(kenh.calls, ['doc_dau_vao'])

    def test_function_da_cong_bo_co_callable(self):
        raw = anh_demo()
        self.assertEqual(chay.xu_ly_function(vung.CAPABILITY, raw, request(raw),
                                          image_text=lambda _: TEXT)['van_ban'], TEXT)
        with self.assertRaises(DataError):
            chay.xu_ly_function('ocr.chua_co@1', raw, request(raw))


class ContractTests(unittest.TestCase):
    def test_bundle_day_du_khop_core_va_manifest(self):
        bundle = json.loads((GOI / 'contract/schemas.json').read_text(encoding='utf-8'))
        core_path = GOI.parents[1] / 'src/kho_tri_thuc/core/contract/ky_thuat.json'
        core = json.loads(core_path.read_text(encoding='utf-8')) if core_path.is_file() else None
        manifest = json.loads((GOI / 'engine.json').read_text(encoding='utf-8'))
        for identity, schema in bundle.items():
            if core is not None:
                self.assertEqual(schema, core[identity])
            # Closure có đủ trong gói, kể cả $ref ở các $defs chưa được dùng.
            def kiem_ref(node):
                if isinstance(node, dict):
                    if '$ref' in node:
                        uri, _, fragment = node['$ref'].partition('#')
                        target = bundle[uri or identity]
                        for token in fragment.lstrip('/').split('/') if fragment else []:
                            token = token.replace('~1', '/').replace('~0', '~')
                            target = target[int(token)] if isinstance(target, list) else target[token]
                    for value in node.values():
                        kiem_ref(value)
                elif isinstance(node, list):
                    for value in node:
                        kiem_ref(value)
            kiem_ref(schema)
        cap = next(c for c in manifest['capability'] if c['ma'] == vung.CAPABILITY)
        self.assertEqual((cap['dau_vao'], cap['dau_ra']), ('vung_anh.v1', 'van_ban_vung.v1'))
        for capability in manifest['capability']:
            for key in ('dau_vao', 'dau_ra'):
                self.assertIn('urn:ktt:contract:' + capability[key], bundle)

    def test_schema_that_kiem_vi_du_ket_qua_va_ca_am(self):
        try:
            from jsonschema import Draft202012Validator, FormatChecker
            from referencing import Registry, Resource
        except ImportError:
            self.skipTest('CHUA_KIEM: chưa có bộ kiểm JSON Schema; không cài thêm')
        bundle = json.loads((GOI / 'contract/schemas.json').read_text(encoding='utf-8'))
        registry = Registry().with_resources((k, Resource.from_contents(s)) for k, s in bundle.items())
        for schema in bundle.values():
            Draft202012Validator.check_schema(schema)
            validator = Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())
            for example in schema.get('examples', []):
                validator.validate(example)
        raw = anh_demo()
        req = request(raw)
        validator_in = Draft202012Validator(bundle['urn:ktt:contract:vung_anh.v1'], registry=registry)
        validator_out = Draft202012Validator(bundle['urn:ktt:contract:van_ban_vung.v1'], registry=registry)
        validator_in.validate(req)
        for text in (TEXT, '', ' \n'):
            result = vung.trich_vung(raw, req, image_text=lambda _: text)
            validator_out.validate(result)
            bad = result | {'vung_rong': not result['vung_rong']}
            self.assertFalse(validator_out.is_valid(bad))
            self.assertFalse(validator_out.is_valid(result | {'do_tin_cay': 0.99}))
        self.assertFalse(validator_in.is_valid(req | {'bon_diem': [[0, 0]] * 3}))
        self.assertFalse(validator_in.is_valid(req | {'duong_dan': 'DEMO'}))


if __name__ == '__main__':
    unittest.main()
