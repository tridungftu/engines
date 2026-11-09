"""G3-TRICH-NOI: E1/WorkerEngine thật trên socket queue DEMO, không PG/server.

Không AI/Word/OCR thật; giữ bản làm việc DEMO. Bàn giao/kho tệp thật qua E1,
chỉ giả DB/socket; không giả capability đã qua TRICH-4b.
"""
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4
import urllib.request
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from kho_tri_thuc.core import kenh_engine as e, ket_qua, tai_lieu, tep
from kho_tri_thuc.engines.e_trich_xuat import tich_hop as trich
from kho_tri_thuc.sdk_core.engine import LoiEngine

try:
    from . import test_g2_32_e1 as e1
    from .test_g3_trich_1b import cong, tao_docx
    from .test_g2_17 import _minimal
except ImportError:
    import test_g2_32_e1 as e1
    from test_g3_trich_1b import cong, tao_docx
    from test_g2_17 import _minimal


def tham_chieu(raw, *, ten='DEMO.docx', mime=trich.MIME_DOCX):
    return dict(contract='tham_chieu_tep.v1', phien_ban='1.0.0',
        tep_id=str(uuid4()), ten_tep=ten, mime=mime, kich_thuoc=len(raw),
        sha256=hashlib.sha256(raw).hexdigest(), het_han_luc=None)


def metadata(bien_the, contract):
    return dict(du_lieu_ket_qua=dict(bien_the=bien_the, ma_contract=contract,
        phien_ban_contract='1.0.0', trang_thai='thanh_cong',
        ly_do='DEMO chưa duyệt nghiệp vụ', revision_truoc=0, nguon=[]),
        revision_tep_truoc=0)


class TrichNoiTests(unittest.TestCase):
    def setUp(self):
        # Chỉ mượn fixture queue hữu hạn của E1; không mở socket TCP.
        self.w = e1.KenhEngineTest()
        self.w.setUp()
        self.addCleanup(self.w.doCleanups)
        transaction = self.w.conn.transaction
        @contextmanager
        def nested_transaction():
            # Savepoint không commit/đưa transaction gốc về idle.
            if self.w.conn.info.transaction_status == 2:
                yield
            else:
                with transaction():
                    yield
        self.w.conn.transaction = nested_transaction
        for obj, name in ((socket, 'create_connection'), (socket.socket, 'connect'),
                          (subprocess, 'Popen'), (urllib.request, 'urlopen')):
            guard = patch.object(obj, name, side_effect=AssertionError(name))
            guard.start()
            self.addCleanup(guard.stop)
        raw = io.BytesIO()
        with zipfile.ZipFile(raw, 'w') as z:
            z.writestr('word/document.xml', '<document>DEMO dữ liệu giả</document>')
        self.raw = raw.getvalue()
        self.ref = tham_chieu(self.raw)
        self.data = dict(tham_chieu_tep=self.ref, loai_hop_dong='XD',
            danh_muc_id=trich.DANH_MUC_ID, danh_muc_sha256=trich.DANH_MUC_SHA256,
            phan_hoi=metadata('phan_hoi_nguon', 'phan_hoi_trich_demo'),
            tham_so=metadata('noi_dung', 'tham_so'))
        self.w.hang.inp = e.DauVaoEngine(self.w.tid,
            (dict(tep_id=self.ref['tep_id'], bien_the='goc', ten=self.ref['ten_tep']),), self.data)
        self.streams, self.saved, self.refs = [], {}, {}
        self.work = Path(tempfile.mkdtemp(prefix='ktt_DEMO_trich_noi_'))
        self.kho = ket_qua.KhoTepEngine.boc(tep.KhoTep(
            self.work / 'var' / 'core-demo' / 'trich' / 'kho-file'))
        self.backend = Mock()
        self.backend.xu_ly.side_effect = lambda data: (
            dict(bang=[], nguon=dict(tep_id=data['tep_id'], sha256=self.ref['sha256'])), 'DEMO')
        self.w.kho.mo_doc.side_effect = self.mo_doc
        self.w.hang.ban_giao = ket_qua.BanGiaoKetQua(self.kho,
            xac_minh_core=self.xac_minh, cua_engine_069=True)
        for name, callback in (('ghi_tep_da_kiem', self.ghi_tep),
                               ('gan_bien_the', lambda *a, **kw: None),
                               ('_goi', self.ghi_sql), ('lay', self.doc_sql)):
            self.enterContext(patch.object(tai_lieu, name, side_effect=callback))
        self.ack = self.w.hang.ban_giao.xac_nhan_da_commit
        self.sdk = self.w.client.cap_sdk()

    def mo_doc(self, *args, **kwargs):
        stream = io.BytesIO(self.raw)
        self.streams.append(stream)
        return stream

    def xac_minh(self, conn, giu):
        self.w.hang.kiem(conn, giu)
        return ket_qua.NguonCore(giu.module, giu.phap_nhan_id, '1.0.0',
            self.w.instance, 'trich', '1.0.0', giu.viec_id, giu.the_he,
            giu.buoc_viec_id, giu.lan_thu_id)

    def ghi_tep(self, conn, **data):
        fid = str(uuid4())
        self.refs[fid] = self.kho._tham_chieu(fid, data['thong_tin'])
        return fid

    def ghi_sql(self, conn, sql, args):
        self.assertIn('loi_tai_lieu.ghi_ket_qua_engine', sql)
        self.assertEqual(conn.info.transaction_status, 2)
        if args[-1]:
            return getattr(self, 'replay', None)
        data = json.loads(args[9])
        ref = self.refs[data['tep_id']]
        kid = str(uuid4())
        self.saved[ref['ten_tep']] = dict(
            raw=self.kho._path('raw/'+ref['sha256']).read_bytes(), kid=kid,
            tep_id=ref['tep_id'], metadata=data, ref=ref)
        self.w.events.append('ghi')
        return dict(ket_qua_id=kid)

    def doc_sql(self, conn, **data):
        self.assertTrue(conn.autocommit)
        self.assertEqual(conn.info.transaction_status, 0)
        self.assertIn(self.w.events[-1], ('commit', 'readback_hash'))
        self.w.events.append('readback_hash')
        rows = [r for r in self.saved.values()
                if r['metadata']['bien_the'] == data['bien_the']]
        return dict(ket_qua=[dict(id=r['kid'], tep_id=r['tep_id']) for r in rows],
                    tep=[dict(tham_chieu=r['ref']) for r in rows])

    def run_job(self):
        # Mock catalog đủ 37 mã; không cần tệp Review ghim cho ca wiring.
        params = [dict(ma=ma, ten=ma) for ma in trich._MA_DANH_MUC]
        with patch.object(trich, 'danh_muc_xd', return_value=params):
            return trich.xu_ly_viec_noi(self.sdk, backend=self.backend,
                                       thu_muc_lam_viec=self.work)

    def test_docx_e1_hash_ack_tham_chieu_va_ket_thuc(self):
        original = deepcopy(self.ref)
        input_original = deepcopy(self.data)
        result = self.run_job()
        self.assertNotIn('phan_hoi_da_ghi', self.sdk.doc_dau_vao())
        self.assertEqual(self.data, input_original)
        self.assertEqual(list(self.saved), ['phan-hoi-nguon.json', 'tham-so.json'])
        source = json.loads(self.saved['phan-hoi-nguon.json']['raw'])
        mapped = json.loads(self.saved['tham-so.json']['raw'])
        self.assertEqual(source['nguon']['tham_chieu_tep'], original)
        self.assertEqual(mapped['phan_hoi_nguon_tep_id'], self.saved['phan-hoi-nguon.json']['tep_id'])
        self.assertNotEqual(mapped['phan_hoi_nguon_tep_id'], self.saved['phan-hoi-nguon.json']['kid'])
        self.assertEqual(mapped['nguon_tep_ids'], [original['tep_id']])
        self.assertEqual(len(mapped['tham_so']), 37)
        self.assertEqual(self.ref, original)
        self.assertTrue(all(s.closed for s in self.streams))
        local = self.backend.xu_ly.call_args.args[0]
        self.assertEqual(local['docx'].read_bytes(), self.raw)
        self.assertTrue(local['out_dir'].is_relative_to(self.work))
        self.assertIn(str(self.w.giu.lan_thu_id), str(local['docx']))
        self.assertEqual(result['ket_qua_id'], self.saved['tham-so.json']['kid'])
        self.assertEqual(result['tep'], self.saved['tham-so.json']['ref'])
        self.assertTrue(self.w.client.ket_thuc(getattr(self.sdk, '_SDKEngine__giu'),
                                             ket_qua_id=result['ket_qua_id']))
        self.assertTrue(self.w.worker.drain())

    def test_anh_xa_chi_sau_commit_va_doc_lai_nguon(self):
        original = trich.anh_xa_tham_so
        def anh_xa(*args, **kwargs):
            self.assertEqual(list(self.saved), ['phan-hoi-nguon.json'])
            self.assertEqual(self.w.events[-1], 'readback_hash')
            self.assertEqual(self.w.conn.info.transaction_status, 0)
            return original(*args, **kwargs)
        with patch.object(trich, 'anh_xa_tham_so', side_effect=anh_xa) as mapped:
            self.run_job()
        mapped.assert_called_once()

    def test_replay_chi_co_ket_qua_id_van_ack_du_tham_chieu(self):
        value = dict(DEMO='Phản hồi nguồn')
        first, sha = trich._ban_giao_noi(self.sdk, value,
            ten='phan-hoi-nguon.json', metadata=self.data['phan_hoi'])
        self.replay = dict(ket_qua_id=first['ket_qua_id'])
        with patch.object(self.kho, 'tai_len', side_effect=AssertionError('Upload lại replay')):
            replay, bam = trich._ban_giao_noi(self.sdk, value,
                ten='phan-hoi-nguon.json', metadata=self.data['phan_hoi'])
        self.assertEqual(replay, first)
        self.assertEqual(replay['tep']['sha256'], sha)
        self.assertEqual(bam, sha)
        self.assertEqual(len(self.saved), 1)

    def test_raw_phan_hoi_hong_sau_commit_khong_ack_hay_anh_xa(self):
        mo_doc = self.kho.mo_doc
        def hong(reader, **data):
            self.assertEqual(self.w.conn.info.transaction_status, 0)
            self.assertEqual(self.w.events[-1], 'readback_hash')
            row = self.saved['phan-hoi-nguon.json']
            self.assertEqual(data['tep_id'], row['tep_id'])
            self.kho._path('raw/'+row['ref']['sha256']).write_bytes(b'DEMO hong')
            return mo_doc(reader, **data)
        with patch.object(self.kho, 'mo_doc', side_effect=hong) as doc, \
                patch.object(trich, 'anh_xa_tham_so') as mapped:
            with self.assertRaises(LoiEngine):
                self.run_job()
        doc.assert_called_once()
        mapped.assert_not_called()
        self.assertEqual(list(self.saved), ['phan-hoi-nguon.json'])

    def test_thu_hoi_quyen_tai_mo_doc_sau_commit_khong_ack_hay_anh_xa(self):
        def thu_hoi(reader, **data):
            self.assertTrue(reader.autocommit)
            self.assertEqual(reader.info.transaction_status, 0)
            self.assertEqual(self.w.events[-1], 'readback_hash')
            self.assertEqual(data['tep_id'], self.saved['phan-hoi-nguon.json']['tep_id'])
            self.assertEqual(data['bien_the'], 'phan_hoi_nguon')
            self.assertEqual(data['hanh_dong'].split(':')[-1], 'XEM')
            raise tai_lieu.LoiTaiLieu('TAI_LIEU_NOI_DUNG')
        with patch.object(self.kho, 'mo_doc', side_effect=thu_hoi) as doc, \
                patch.object(trich, 'anh_xa_tham_so') as mapped:
            with self.assertRaises(LoiEngine):
                self.run_job()
        doc.assert_called_once()
        mapped.assert_not_called()
        self.assertEqual(list(self.saved), ['phan-hoi-nguon.json'])

    def test_hai_luot_khong_dung_chung_ban_lam_viec(self):
        self.run_job()
        first = self.backend.xu_ly.call_args.args[0]['docx']
        self.run_job()
        second = self.backend.xu_ly.call_args.args[0]['docx']
        self.assertNotEqual(first, second)
        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_ocr_da_commit_docx_moi_duoc_trich_giu_nguon_pdf(self):
        pdf = tham_chieu(b'%PDF-DEMO', ten='DEMO.pdf', mime='application/pdf')
        self.data['ocr'] = dict(ket_qua_id=str(uuid4()), nguon=pdf,
                                docx=deepcopy(self.ref), da_ban_giao=True)
        self.run_job()
        source = json.loads(self.saved['phan-hoi-nguon.json']['raw'])
        self.assertEqual(source['nguon']['ocr'], self.data['ocr'])
        self.assertEqual(self.w.kho.mo_doc.call_args.kwargs['tep_id'], self.ref['tep_id'])

    def test_pdf_khong_di_thang_va_khong_mo_stream(self):
        self.ref.update(ten_tep='DEMO.pdf', mime='application/pdf')
        with self.assertRaises(trich.ChuaKiem):
            self.run_job()
        self.assertEqual(self.streams, [])
        self.backend.xu_ly.assert_not_called()
        self.assertFalse(self.saved)

    def test_pdf_gia_docx_bi_chan_truoc_backend(self):
        self.raw = b'%PDF-DEMO'
        self.ref.update(kich_thuoc=len(self.raw), sha256=hashlib.sha256(self.raw).hexdigest())
        with self.assertRaises(zipfile.BadZipFile):
            self.run_job()
        self.backend.xu_ly.assert_not_called()

    def test_sai_hash_bi_chan_truoc_ai_va_ban_giao(self):
        self.ref['sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'TRICH_TEP_SAI_HASH'):
            self.run_job()
        self.backend.xu_ly.assert_not_called()
        self.assertFalse(self.saved)
        self.assertTrue(all(s.closed for s in self.streams))

    def test_ocr_chua_ack_khong_trich(self):
        self.data['ocr'] = dict(docx=self.ref, da_ban_giao=False)
        with self.assertRaisesRegex(ValueError, 'TRICH_OCR_CHUA_XAC_NHAN'):
            self.run_job()
        self.backend.xu_ly.assert_not_called()
        self.assertEqual(self.streams, [])

    def test_het_han_qua_co_va_duong_dan_kho_bi_chan(self):
        self.ref['het_han_luc'] = (datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()
        with self.assertRaisesRegex(ValueError, 'TRICH_THAM_CHIEU_HET_HAN'):
            self.run_job()
        self.ref['het_han_luc'] = None
        self.ref['kich_thuoc'] = trich.GIOI_HAN_DOCX+1
        with self.assertRaisesRegex(ValueError, 'TRICH_TEP_QUA_LON'):
            self.run_job()
        self.data['docx'] = 'DEMO-khong-duoc-mo.docx'
        with self.assertRaisesRegex(ValueError, 'TRICH_KHONG_NHAN_DUONG_DAN_KHO'):
            self.run_job()
        self.backend.xu_ly.assert_not_called()

    def test_mat_lease_khong_ai_khong_ban_giao(self):
        self.w.hang.live = False
        with self.assertRaisesRegex(LoiEngine, 'VIEC_MAT_LEASE'):
            self.run_job()
        self.backend.xu_ly.assert_not_called()
        self.assertFalse(self.saved)

    def test_thieu_tep_id_sau_ack_khong_suy_tu_ket_qua_id(self):
        ack = self.ack
        def thieu(reader, **data):
            result = ack(reader, **data)
            result['tep'].pop('tep_id')
            return result
        self.w.hang.ban_giao.xac_nhan_da_commit = thieu
        with self.assertRaisesRegex(ValueError, 'TRICH_THIEU_THAM_CHIEU_PHAN_HOI_CORE'):
            self.run_job()
        self.assertEqual(list(self.saved), ['phan-hoi-nguon.json'])
        self.backend.xu_ly.assert_called_once()

    def test_hash_phan_hoi_doc_lai_sai_khong_ban_giao_tham_so(self):
        ack = self.ack
        def sai(reader, **data):
            result = ack(reader, **data)
            result['tep']['sha256'] = '0'*64
            return result
        self.w.hang.ban_giao.xac_nhan_da_commit = sai
        with self.assertRaisesRegex(ValueError, 'TRICH_THIEU_THAM_CHIEU_PHAN_HOI_CORE'):
            self.run_job()
        self.assertEqual(list(self.saved), ['phan-hoi-nguon.json'])

    def test_cho_ack_nguon_khong_anh_xa_hay_trich_lai(self):
        cho, mo = threading.Event(), threading.Event()
        ack = self.ack
        def giu(reader, **data):
            if data['bien_the'] == 'phan_hoi_nguon':
                cho.set()
                if not mo.wait(5):
                    raise AssertionError('DEMO timeout ACK')
            return ack(reader, **data)
        self.w.hang.ban_giao.xac_nhan_da_commit = giu
        errors = []
        def run():
            try:
                self.run_job()
            except Exception as exc:
                errors.append(exc)
        thread = threading.Thread(target=run)
        thread.start()
        try:
            self.assertTrue(cho.wait(5))
            self.assertTrue(thread.is_alive())
            self.assertEqual(list(self.saved), ['phan-hoi-nguon.json'])
            self.backend.xu_ly.assert_called_once()
        finally:
            mo.set()
            thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertEqual(errors, [])
        self.assertIn('tham-so.json', self.saved)

    def test_mat_ack_khong_lap_va_khong_ban_giao_tham_so(self):
        self.w.hang.ban_giao.xac_nhan_da_commit = Mock(side_effect=RuntimeError('DEMO mất ACK'))
        with self.assertRaises(LoiEngine):
            self.run_job()
        self.assertEqual(list(self.saved), ['phan-hoi-nguon.json'])
        self.backend.xu_ly.assert_called_once()
        self.assertEqual(len(list(self.work.glob('*/dau-vao.docx'))), 1)

    def test_nguon_doi_sau_backend_khong_ban_giao(self):
        def doi(data):
            data['docx'].write_bytes('DEMO thay đổi'.encode('utf-8'))
            return dict(bang=[]), 'DEMO'
        self.backend.xu_ly.side_effect = doi
        with self.assertRaisesRegex(ValueError, 'TRICH_TEP_NGUON_DA_DOI'):
            self.run_job()
        self.assertFalse(self.saved)

    def test_local_loi_khong_fallback_cloud(self):
        transport = Mock(side_effect=ConnectionError('DEMO Local hỏng'))
        c = cong(transport)
        self.raw = tao_docx().read_bytes()
        self.ref.update(kich_thuoc=len(self.raw), sha256=hashlib.sha256(self.raw).hexdigest())
        self.backend = trich.BackendTrichXuat(cong_ai=c)
        # Ca pipeline thật cần Review ghim; ca wiring ở trên luôn chạy.
        try:
            trich.danh_muc_xd()
        except (OSError, ValueError) as exc:
            self.skipTest('Thiếu/sai tệp catalog Review ghim: ' + str(exc))
        trich.xu_ly_viec_noi(self.sdk, backend=self.backend, thu_muc_lam_viec=self.work)
        self.assertGreater(transport.call_count, 0)
        self.assertEqual(c._mask.mock_calls + c._nha_cung_cap.mock_calls, [])
        mapped = json.loads(self.saved['tham-so.json']['raw'])
        self.assertTrue(all(row['can_soat'] for row in mapped['tham_so']))


class EntrypointTests(unittest.TestCase):
    def test_manifest_schema_va_khong_ready_khi_chua_4b(self):
        path = Path(trich.__file__).with_name('engine.json')
        manifest = json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(manifest['ho_so_chay_mau']['diem_vao'], trich.__name__+'.chay_noi')
        self.assertIn('TRICH-4b', manifest['ten'])
        self.assertEqual(manifest['capability'][0]['dau_ra'], 'tham_so.v1')
        self.assertEqual(manifest['capability'][0]['mime'], [trich.MIME_DOCX])
        schemas = json.loads((Path(__file__).resolve().parents[1] /
            'src/kho_tri_thuc/core/contract/manifest.json').read_text(encoding='utf-8'))
        schema = schemas['urn:ktt:manifest:engine.v1']
        _minimal(manifest, schema, schema, schemas)
        b = Mock()
        with patch.object(trich, 'BackendTrichXuat') as backend, \
                patch.object(trich.Bootstrap, 'nhan', return_value=b), \
                patch.object(trich, '_VongNhanNoi') as vong:
            vong.return_value.drain.return_value = True
            trich.chay_noi(kiem_chu_ky=lambda *_: None, nhan_viec=lambda *_: None,
                cong_ai=Mock(), thu_muc_lam_viec='DEMO-khong-tao')
        self.assertEqual(b.bao_san_sang.call_args.kwargs['contracts'], [])
        self.assertIn('TRICH-4b', trich.LY_DO_CHUA_SAN_SANG)
        backend.assert_called_once()

    def test_vong_keo_e1_chi_ket_thuc_sau_hai_ack(self):
        b, channel, sdk = Mock(), Mock(), Mock()
        b.accept.return_value = (Mock(), ('DEMO', 0))
        b.accept.return_value[0].__enter__ = Mock(return_value=b.accept.return_value[0])
        b.accept.return_value[0].__exit__ = Mock(return_value=False)
        channel.cap_sdk.return_value = sdk
        sdk._SDKEngine__giu = object()
        vong = trich._VongNhanNoi(b, lambda *_: channel, Mock(), 'DEMO')
        def done(*args, **kwargs):
            vong.ngung_accept()
            return dict(ket_qua_id='DEMO hai ACK')
        with patch.object(trich, 'xu_ly_viec_noi', side_effect=done):
            vong._chay()
        channel.ket_thuc.assert_called_once_with(sdk._SDKEngine__giu, ket_qua_id='DEMO hai ACK')
        self.assertFalse(vong.loi)

    def test_vong_cho_readiness_va_hang_rong_tren_cung_kenh(self):
        b, channel, sdk = Mock(), Mock(), Mock()
        conn = Mock()
        conn.__enter__, conn.__exit__ = Mock(return_value=conn), Mock(return_value=False)
        b.accept.return_value = (conn, ('DEMO', 0))
        loi = LoiEngine('CHUA_SAN_SANG')
        loi.thu_lai_duoc = True
        channel.cap_sdk.side_effect = [loi, None, sdk]
        sdk._SDKEngine__giu = object()
        vong = trich._VongNhanNoi(b, lambda *_: channel, Mock(), 'DEMO')
        def done(*args, **kwargs):
            vong.ngung_accept()
            return dict(ket_qua_id='DEMO')
        with patch.object(trich, 'xu_ly_viec_noi', side_effect=done), \
                patch.object(trich.time, 'sleep'):
            vong._chay()
        b.accept.assert_called_once()
        self.assertEqual(channel.cap_sdk.call_count, 3)
        channel.ket_thuc.assert_called_once()
        self.assertFalse(vong.loi)

    def test_vong_loi_ban_giao_khong_ket_thuc_hay_bao_drain_xong(self):
        b, channel = Mock(), Mock()
        conn = Mock()
        conn.__enter__, conn.__exit__ = Mock(return_value=conn), Mock(return_value=False)
        b.accept.return_value = (conn, ('DEMO', 0))
        vong = trich._VongNhanNoi(b, lambda *_: channel, Mock(), 'DEMO')
        with patch.object(trich, 'xu_ly_viec_noi', side_effect=LoiEngine('VIEC_MAT_LEASE')):
            vong._chay()
        channel.ket_thuc.assert_not_called()
        self.assertTrue(vong.loi)
        self.assertTrue(vong.dung)
        # Thread chưa start trong unit test; drain vẫn phải giữ lỗi cần đối chiếu.
        vong.worker = Mock()
        vong.worker.is_alive.return_value = False
        self.assertFalse(vong.drain())


if __name__ == '__main__':
    unittest.main()
