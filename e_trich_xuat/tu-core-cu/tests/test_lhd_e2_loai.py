"""LHD-E2: DEMO tất định, không AI/mạng/COM/PG; giữ tệp bằng chứng ở temp.

Chạy trực tiếp --bang-chung <thư mục mới> trước sửa engine, thêm --sau
sau sửa. Công cụ kiem_nhanh_trich chấm cùng DOCX/đáp án DEMO; stdout
chỉ số và SHA. Không dùng kết quả này để kết luận độ chính xác AI thật.
"""

import argparse
import ast
from copy import deepcopy
from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import socket
import tempfile
import unittest
from unittest.mock import patch

from kho_tri_thuc.engines.e_trich_xuat import tich_hop as trich
from kho_tri_thuc.sdk_core import danh_muc_tham_so as dm, xlsx_mini
from kho_tri_thuc.sdk_core.engine import SDKEngine, KenhCore
from kho_tri_thuc.tri_thuc.cong_ai import CongAI, KetQuaAI, TruongAI
from tests.fixtures import trich_bien_the_xd as xd
from tests.fixtures import trich_mau_dv_demo as dv
from tests.test_g3_trich_1b import cong
from tests.test_g3_trich_3a import _lease, _metadata


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'src/kho_tri_thuc/m4/review_goc/trich_xuat/DANH_MUC_THAM_SO.xlsx'
TEP_ID = '00000000-0000-0000-0000-000000000001'
DM_ID = '00000000-0000-0000-0000-000000000002'

# Đo TRƯỚC sửa engine, V0–V4, AI giả theo hash DTO; không sinh từ code mới.
# Thứ tự: bảng, câu hỏi, phản hồi đầy đủ bỏ giờ/thời lượng, cấu trúc.
NEN_XD = {
    'V0': ('6a6784a79eee574c9d9186f27024129527d06a21b55a827c0d8573cd4cb2562f',
           '959a40dc047e32f70bb57dbaf19a56405379efca9f37a958f69ca57327596501',
           'bec6c4fef8e1c5189b0723c2db0037af73e0443a68d7aa6a532608e26a9d0758',
           'caa7938f4a5dbcb21fa537daed92ed69a3c6a6cf47fd03c2553a1ad1e8755114'),
    'V1': ('6a6784a79eee574c9d9186f27024129527d06a21b55a827c0d8573cd4cb2562f',
           '959a40dc047e32f70bb57dbaf19a56405379efca9f37a958f69ca57327596501',
           '52c16e40e7715f4528152c639417dc7ff78359f93e7c484d78bcfcb1f1799653',
           '46b310d71ff8615c8c4651991e6789994359a8a953fcf2c57816ce10166e6ace'),
    'V2': ('b2f6729b138c18fcf00547171d81bd25da4ebb9cf63b1f1b2fe5e2856050f57f',
           'c68edb442d8b6f7f54ba09130fe6306df38b8ef9b707af5bc11b640999138a84',
           '372714de68ee1e540ebf10474732620346b7eb65e1c02aa6ff263e7005a4bdfb',
           '5593ce9a690632c94700b46a264e04c225ff56aea6675307efa3a8a2357e96e0'),
    'V3': ('9bac1fe41ae13705db05d54d8de55b16b949ad9140895cf70949eb837d7ff0fb',
           'a147dd90f3a184505d82ce6fcdeab7abe48b062422afddcf98e6e02a1a8d9799',
           '6a6524f75aa703c51e044a40de23b1119cd22fbdbe0d02f5383ac83a9e9eec74',
           '2dcc64c89faa06290ddb4199576483bbf69a8275a57c568cf75c4a6c002b9bbc'),
    'V4': ('aa908a7816380ba81145467115eda6bbe52c131a6f72c7f171ca816c64ced4f2',
           '9f5aaf188a97a3d3125041b9d797f8acd92b7a2b4ef777e9fe3131d0a600a2e6',
           '1e3b7a75b9a8f4d2ee54f2ea8a0dae7949533c1a9b807f01c88639086c456ac9',
           'a87596f133e94145c55327bb34a99c6c688bb2498efb678cce9860818f38b371'),
}


def dau_vao_catalog(raw, *, loai='XD', ten='Hợp đồng xây dựng', version=1):
    return dict(loai_hop_dong=loai, ten_loai=ten, so_phien_ban=version,
                danh_muc_id=loai, danh_muc_sha256=hashlib.sha256(raw).hexdigest(),
                danh_muc=dict(tep_id=DM_ID, sha256=hashlib.sha256(raw).hexdigest()))


def excel_dv(mau):
    rows = [dm.HEADER]
    for row in mau.dap_an:
        rows.append([row.ma, 'Dịch vụ DEMO', row.ten, '', '',
                     'Không' if row.ma in dv.MA_TAT_DV else 'Có', 2, '', '', 'Không'])
    out = io.BytesIO()
    xlsx_mini.write_xlsx(out, {'Danh_muc': {'rows': rows}})
    return out.getvalue()


def dap_an_dv(mau):
    return [dict(ma=r.ma, gia_tri=r.gia_tri, trich_dan=r.trich_dan) for r in mau.dap_an]


class KenhDemo(KenhCore):
    """Chỉ giả kênh Core; SDK/đọc bytes/engine/ánh xạ/bàn giao chạy thật."""
    def __init__(self, data, files):
        self.data, self.files = data, files
        self.streams, self.reads, self.saved = [], [], {}

    def goi(self, operation, giu_viec, **payload):
        if operation == 'doc_dau_vao':
            return deepcopy(self.data)
        if operation == 'heartbeat':
            return replace(giu_viec, giu_den=datetime.now(timezone.utc) + timedelta(seconds=900))
        if operation == 'mo_doc':
            self.reads.append(payload['tep_id'])
            stream = io.BytesIO(self.files[payload['tep_id']])
            self.streams.append(stream)
            return stream
        assert operation == 'ghi_ket_qua'
        raw = payload['luong'].read()
        name = payload['ten']
        self.saved[name] = json.loads(raw)
        return dict(da_ban_giao=True,
                    ket_qua_id=f'00000000-0000-0000-0000-{len(self.saved) + 2:012d}',
                    tep=dict(tep_id=f'00000000-0000-0000-0000-{len(self.saved) + 4:012d}',
                             sha256=hashlib.sha256(raw).hexdigest()))


def bam(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    allow_nan=False).encode('utf-8')).hexdigest()


class AIGia:
    """Phản hồi chỉ phụ thuộc câu hỏi + bộ đáp án DEMO, mã lượt = hash DTO."""
    def __init__(self, dap_an):
        self.dap_an = {r['ma']: r for r in dap_an}
        self.cau_hoi = []

    def goi(self, yc):
        dto = asdict(yc)
        self.cau_hoi.append(dto)
        fields = {}
        for name in yc.truong:
            if name.endswith('.1'):
                line = next(iter(re.findall(r'^R\d+ \|.*', yc.van_ban, re.M)), '')
                if line:
                    fields[name] = TruongAI(name, line.split(' | ')[0], line, 'LOCAL')
            elif '.' not in name and name in self.dap_an:
                row = self.dap_an[name]
                if row['trich_dan'] in yc.van_ban:
                    fields[name] = TruongAI(name, row['gia_tri'], row['trich_dan'], 'LOCAL')
                    if row.get('don_vi'):
                        key = name + '.don_vi'
                        fields[key] = TruongAI(key, row['don_vi'], row['trich_dan'], 'LOCAL')
        return KetQuaAI(yc.loai_viec, 'VANG', fields, 'LOCAL', 'DEMO tất định',
                        ma_yeu_cau=bam(dto))


def chay_demo(path, dap_an, out, **data):
    fake = AIGia(dap_an)
    with patch.object(CongAI, 'goi', lambda self, yc: fake.goi(yc)), \
            patch.object(socket.socket, 'connect', side_effect=AssertionError('Cấm mạng')):
        raw, text = trich.BackendTrichXuat(cong_ai=cong()).xu_ly(dict(
            tep_id=TEP_ID, docx=path, out_dir=out, loai_hop_dong='XD',
            danh_muc_id='XD', danh_muc_sha256=trich.DANH_MUC_SHA256) | data)
    stable = deepcopy(raw)
    stable.pop('tao_luc')
    stable['tom_tat'].pop('thoi_gian_giay')
    return raw, text, fake.cau_hoi, stable


def bang_chung(root, *, sau=False):
    # Import công cụ chấm ở test, không đưa dependency m4 vào engine.
    from tools import kiem_nhanh_trich as tool
    root = Path(root)
    if not sau:
        files = xd.tao_bo_bien_the(root)
    else:
        files = {v: (root / f'DEMO_XD_{v}.docx', root / f'DAP_AN_DEMO_XD_{v}.tsv')
                 for v in xd.BIEN_THE}
    phase = 'sau' if sau else 'truoc'
    summaries = {}
    for variant, (path, answer) in files.items():
        inputs = (dau_vao_catalog(CATALOG.read_bytes()) | dict(
            danh_muc_bytes=CATALOG.read_bytes())) if sau else {}
        raw, _, questions, stable = chay_demo(path, xd.dap_an(variant),
                                             root / phase / variant, **inputs)
        result = root / f'{variant}-{phase}.json'
        result.write_text(json.dumps(raw, ensure_ascii=False), encoding='utf-8')
        evidence = dict(cau_hoi=questions, phan_hoi=stable)
        record = root / f'{variant}-{phase}-bang-chung.json'
        record.write_text(json.dumps(evidence, ensure_ascii=False), encoding='utf-8')
        before = root / f'{variant}-truoc.json'
        old_structure = root / 'truoc' / variant / path.stem / (path.stem + '_cau_truc.json')
        structure = root / phase / variant / path.stem / (path.stem + '_cau_truc.json')
        args = ['--dap-an', str(answer), '--tep-nguon', str(path),
                '--ket-qua-goc', str(before), '--ket-qua-engine', str(result),
                '--cau-truc-goc', str(old_structure), '--cau-truc-engine', str(structure),
                '--nguon-goc', str(ROOT / trich.NGUON),
                str(ROOT / 'src/kho_tri_thuc/m4/review_goc/trich_xuat/danh_muc.py'),
                str(ROOT / 'src/kho_tri_thuc/m4/review_goc/trich_xuat/kiem_tra.py'),
                '--nguon-engine', trich.__file__, '--phien-ban-goc', 'DEMO-truoc',
                '--phien-ban-engine', 'DEMO-' + phase, '--model', 'DEMO-tat-dinh',
                '--cau-hinh', '{"cloud":false,"ra_lai":true,"tham_so_them":[]}']
        status = tool.main(args)
        if status:
            raise AssertionError('Kiểm nhanh DEMO chưa đạt')
        hashes = dict(bang=bam(raw['bang']), cau_hoi=bam(questions),
                      phan_hoi=bam(stable), cau_truc=bam(json.loads(structure.read_text(encoding='utf-8'))))
        if sau:
            old = json.loads((root / f'{variant}-truoc-bang-chung.json').read_text(encoding='utf-8'))
            assert bam(old) == bam(evidence), 'XD đổi câu hỏi hoặc phản hồi'
        summaries[variant] = hashes
        print(variant, json.dumps(hashes, ensure_ascii=False, sort_keys=True))
    return summaries


class LoaiTests(unittest.TestCase):
    def test_engine_khong_import_m4_core_ha_tang_nguon(self):
        from importlib.util import resolve_name
        from kho_tri_thuc.engines.e_trich_xuat import ai_chung
        for module in (trich, ai_chung):
            for node in ast.walk(ast.parse(Path(module.__file__).read_text(encoding='utf-8'))):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [resolve_name('.' * node.level + (node.module or ''), module.__package__)
                             if node.level else node.module or '']
                for name in names:
                    self.assertFalse(any(name == 'kho_tri_thuc.' + p or name.startswith('kho_tri_thuc.' + p + '.')
                                         for p in ('m4', 'core', 'ha_tang', 'nguon')), name)

    def test_xd_sdk_tham_so_giong_het_nguon(self):
        self.assertEqual(dm.doc_danh_muc(CATALOG.read_bytes()).tham_so, trich.danh_muc_xd())

    def test_xd_legacy_giu_duong_catalog_khong_suy_tu_sdk(self):
        from kho_tri_thuc.engines.e_trich_xuat import tham_so
        self.assertEqual(trich.DANH_MUC_THAM_SO, CATALOG)
        self.assertEqual(trich.DANH_MUC_THAM_SO, tham_so.DANH_MUC_THAM_SO)
        with patch.object(xlsx_mini, '__file__', str(ROOT / 'SDK-DEMO-khong-co.py')):
            self.assertEqual(trich.danh_muc_xd(), tham_so.danh_muc_xd())

    def test_xd_legacy_hash_lech_tu_choi_truoc_parse(self):
        read_bytes = Path.read_bytes

        def bytes_doi(path):
            raw = read_bytes(path)
            return raw + b'DEMO doi bytes' if path == CATALOG else raw

        with patch.object(Path, 'read_bytes', bytes_doi), \
                patch.object(xlsx_mini, 'read_xlsx') as parse:
            with self.assertRaisesRegex(ValueError, '^TRICH_DANH_MUC_SAI_HASH$'):
                trich.danh_muc_xd()
            parse.assert_not_called()

    def test_xd_v0_v4_cau_hoi_phan_hoi_bang_cau_truc_giu_nguyen_hash(self):
        root = Path(tempfile.mkdtemp(prefix='LHD-E2-XD-test-'))
        catalog = CATALOG.read_bytes()
        for variant, (path, _) in xd.tao_bo_bien_the(root).items():
            with self.subTest(variant=variant):
                raw, _, questions, stable = chay_demo(path, xd.dap_an(variant), root / 'out',
                    **dau_vao_catalog(catalog), danh_muc_bytes=catalog)
                structure = root / 'out' / path.stem / (path.stem + '_cau_truc.json')
                actual = (bam(raw['bang']), bam(questions), bam(stable),
                          bam(json.loads(structure.read_text(encoding='utf-8'))))
                self.assertEqual(actual, NEN_XD[variant])

    def kenh(self, raw_catalog, raw_docx, **doi):
        data = dau_vao_catalog(raw_catalog, loai='DV', ten='Hợp đồng dịch vụ', version=3)
        data.update(tham_chieu_tep=dict(contract='tham_chieu_tep.v1', phien_ban='1.0.0',
            tep_id=TEP_ID, ten_tep='DEMO_DV.docx', mime=trich.MIME_DOCX,
            kich_thuoc=len(raw_docx), sha256=hashlib.sha256(raw_docx).hexdigest(), het_han_luc=None),
            phan_hoi=_metadata('phan_hoi_trich_demo'), tham_so=_metadata('tham_so'))
        data.update(doi)
        return KenhDemo(data, {TEP_ID: raw_docx, DM_ID: raw_catalog})

    def test_ba_hop_dong_dv_qua_sdk_27_ma_ten_loai_phien_ban_va_anh_xa(self):
        for mau in dv.bo_mau_dv_demo():
            with self.subTest(mau=mau.ma):
                kenh = self.kenh(excel_dv(mau), dv.docx_bytes(mau))
                fake = AIGia(dap_an_dv(mau))
                before = deepcopy(kenh.data)
                with patch.object(CongAI, 'goi', lambda self, yc: fake.goi(yc)), \
                        patch.object(socket.socket, 'connect', side_effect=AssertionError('Cấm mạng')):
                    trich.xu_ly_viec_noi(SDKEngine(_lease(), kenh_core=kenh),
                        backend=trich.BackendTrichXuat(cong_ai=cong()),
                        thu_muc_lam_viec=tempfile.mkdtemp(prefix='LHD-E2-DV-DEMO-'))
                self.assertEqual(kenh.data, before)
                self.assertEqual(kenh.reads, [DM_ID, TEP_ID])
                self.assertTrue(all(s.closed for s in kenh.streams))
                source = kenh.saved['phan-hoi-nguon.json']
                mapped = kenh.saved['tham-so.json']
                codes = tuple(r.ma for r in mau.dap_an if r.ma not in dv.MA_TAT_DV)
                self.assertEqual(tuple(r['ma'] for r in source['bang']), codes)
                self.assertEqual(tuple(r['ma'] for r in mapped['tham_so']), codes)
                self.assertEqual(source['nguon']['so_phien_ban'], 3)
                self.assertEqual(mapped['loai_hop_dong'], 'DV')
                self.assertEqual(mapped['danh_muc_sha256'], before['danh_muc']['sha256'])
                self.assertTrue(any(r['gia_tri']['kieu'] == 'van_ban' for r in mapped['tham_so']))
                self.assertTrue(fake.cau_hoi)
                self.assertTrue(all('\nTHAM SỐ:\n' in q['chi_dan'] for q in fake.cau_hoi))
                chi_dan = [q['chi_dan'].partition('\nTHAM SỐ:\n')[0] for q in fake.cau_hoi]
                self.assertTrue(all('xây dựng' not in text for text in chi_dan))
                self.assertTrue(any('Hợp đồng dịch vụ' in text for text in chi_dan))
                self.assertTrue(any('MỤC LỤC HỢP ĐỒNG DỊCH VỤ' in text for text in chi_dan))

    def test_dv_trich_va_tim_vi_tri_giu_nguyen_bytes_mo_ta_danh_muc(self):
        mo_ta = (
            'Số hợp đồng xây dựng được tư vấn; không lấy số hợp đồng dịch vụ hiện tại',
            'Tên trong MỤC LỤC HỢP ĐỒNG; giữ  nguyên chữ.\nTHAM SỐ:\nNội dung mô tả',
        )
        rows = [dm.HEADER] + [
            [f'DV-{i:02d}', 'Dịch vụ DEMO', text, '', '', 'Có', 2, '', '', 'Không']
            for i, text in enumerate(mo_ta, 1)]
        out = io.BytesIO()
        xlsx_mini.write_xlsx(out, {'Danh_muc': {'rows': rows}})
        raw = out.getvalue()
        params, loai, ten, _, _ = trich._danh_muc_dau_vao(
            dau_vao_catalog(raw, loai='DV', ten='Hợp đồng dịch vụ') |
            dict(danh_muc_bytes=raw))
        self.assertEqual(tuple(p['mo_ta'].encode('utf-8') for p in params),
                         tuple(text.encode('utf-8') for text in mo_ta))
        before = deepcopy(params)
        expected = '\n'.join(f'- DV-{i:02d} | {text}' for i, text in enumerate(mo_ta, 1))
        fake = AIGia([])
        ai = trich.AIChung(cong(), loai_hop_dong=loai, ten_loai=ten)
        row = dict(dieu='0', khoan='', tieu_de_khoan='', noi_dung='Số hợp đồng DEMO: DV-00007.')
        yc = trich.build_prompt(params, {'R001': row}, ['R001'])
        with patch.object(CongAI, 'goi', lambda self, yc: fake.goi(yc)), \
                patch.object(socket.socket, 'connect', side_effect=AssertionError('Cấm mạng')):
            ai.hoi_trich(yc)
            ai.tim_vi_tri(params, 'R001 | Phần mở đầu | Số hợp đồng DEMO: DV-00007.', {'R001'})
        self.assertEqual(params, before)
        self.assertEqual(yc.chi_dan, trich.CHI_DAN_TRICH + '\nTHAM SỐ:\n' + expected)
        self.assertEqual(len(fake.cau_hoi), 2)
        for duong, question, ten_trong_cau in zip(
                ('trích xuất', 'tìm vị trí'), fake.cau_hoi,
                ('Trích tham số Hợp đồng dịch vụ,', 'MỤC LỤC HỢP ĐỒNG DỊCH VỤ')):
            with self.subTest(duong=duong):
                chi_dan, moc, tham_so = question['chi_dan'].partition('\nTHAM SỐ:\n')
                self.assertEqual(moc, '\nTHAM SỐ:\n')
                self.assertIn(ten_trong_cau, chi_dan)
                self.assertNotIn('hợp đồng xây dựng', chi_dan)
                self.assertEqual(tham_so.encode('utf-8'), expected.encode('utf-8'))

    def test_hash_lech_chan_truoc_doc_docx_parse_ai_va_ban_giao(self):
        mau = dv.bo_mau_dv_demo()[0]
        kenh = self.kenh(excel_dv(mau), dv.docx_bytes(mau))
        kenh.files[DM_ID] += b'DEMO doi bytes'
        with patch.object(CongAI, 'goi') as ai, \
                patch.object(dm, 'doc_danh_muc') as parse, \
                patch.object(trich.BackendTrichXuat, 'xu_ly') as run:
            with self.assertRaisesRegex(ValueError, '^TRICH_DANH_MUC_SAI_HASH$'):
                trich.xu_ly_viec_noi(SDKEngine(_lease(), kenh_core=kenh),
                    backend=trich.BackendTrichXuat(cong_ai=cong()),
                    thu_muc_lam_viec=tempfile.mkdtemp(prefix='LHD-E2-hash-DEMO-'))
            ai.assert_not_called()
            parse.assert_not_called()
            run.assert_not_called()
        self.assertEqual(kenh.reads, [DM_ID])
        self.assertEqual(kenh.saved, {})
        self.assertTrue(all(s.closed for s in kenh.streams))

    def test_loai_thieu_phien_ban_ten_sai_excel_khong_muon_xd(self):
        mau = dv.bo_mau_dv_demo()[0]
        raw = excel_dv(mau)
        good = dau_vao_catalog(raw, loai='DV', ten='Hợp đồng dịch vụ') | dict(danh_muc_bytes=raw)
        bad = [good | {key: value} for key, value in (
            ('loai_hop_dong', ''), ('ten_loai', ''), ('so_phien_ban', None),
            ('so_phien_ban', True), ('so_phien_ban', 0), ('danh_muc_id', 'XD'))]
        bad.append({k: v for k, v in good.items() if k not in ('danh_muc', 'danh_muc_bytes')})
        bad.append(dict(loai_hop_dong='XD', danh_muc_id='XD',
                        danh_muc_sha256=trich.DANH_MUC_SHA256, so_phien_ban=2))
        with patch.object(trich, 'danh_muc_xd', side_effect=AssertionError('Không fallback XD')), \
                patch.object(CongAI, 'goi') as ai:
            for data in bad:
                with self.subTest(data=data.keys()), self.assertRaises(ValueError):
                    trich._danh_muc_dau_vao(data)
            # Hash khớp nhưng Excel hỏng vẫn bị SDK từ chối.
            invalid = b'DEMO khong phai Excel'
            with self.assertRaises(dm.LoiDanhMuc):
                trich._danh_muc_dau_vao(dau_vao_catalog(invalid, loai='DV', ten='Dịch vụ') |
                                       dict(danh_muc_bytes=invalid))
            ai.assert_not_called()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bang-chung')
    parser.add_argument('--sau', action='store_true')
    args, rest = parser.parse_known_args()
    if args.bang_chung:
        bang_chung(args.bang_chung, sau=args.sau)
    else:
        unittest.main(argv=[__file__, *rest])
