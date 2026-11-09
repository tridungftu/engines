"""AI-5a: Core giả sở hữu SQLite DEMO; engine chỉ gọi SDK qua pipe test.

Không PostgreSQL/dịch vụ/AI thật. Giữ tệp tạm để tuân thủ quy tắc không xóa.
Pipe chỉ là transport fixture, không chứng minh IPC/launcher production.
"""

from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import io
import json
from pathlib import Path
import pickle
import queue
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from kho_tri_thuc.core.phien import MaBiMat
from kho_tri_thuc.core.viec import GiuViec
from kho_tri_thuc.engines.e_hoi_ai.nhat_ky import BoGhiQuaCore, LoiNhatKy
from kho_tri_thuc.sdk_core.engine import KenhCore, LoiEngine, SDKEngine
from kho_tri_thuc.tri_thuc import cong_ai as ca


LOAI = 'BOC_TACH_HOP_DONG'
SETTINGS = {'cong_ai': {'cloud_bat': True, 'kiem_xac_suat': {
    'ty_le_ban_dau': 0.2, 'cua_so': 2, 'bac_thang': [[2, 0.95, 0.05]]}}}
METADATA = dict(bien_the='ai_demo', ma_contract='nhat_ky_ai_demo',
    phien_ban_contract='1', trang_thai='DEMO', ly_do=None,
    revision_truoc=0, nguon=[])


def _lease():
    return GiuViec(viec_id=uuid4(), buoc_viec_id=uuid4(), lan_thu_id=uuid4(),
        phap_nhan_id=uuid4(), module='demo', hanh_dong='DEMO:AI:LAP',
        instance_id=uuid4(), the_he=1,
        giu_den=datetime.now(timezone.utc) + timedelta(minutes=2),
        ma=MaBiMat('AI5A_CANARY_' + 'x' * 32))


def _record(**kw):
    return replace(ca.BanGhiCongAI(ma_yeu_cau=uuid4().hex,
        luc='2026-10-31T10:00:00+00:00', loai_viec=LOAI,
        duong='LOCAL', nha_cung_cap='local', model='demo-local',
        da_gui=True, ket_qua='DAT'), **kw)


def _kiem(dung=True, **kw):
    return _record(duong='CLOUD', nha_cung_cap='demo-cloud', model='demo-model',
        ly_do_chuyen_cloud=('KIEM_XAC_SUAT',),
        ly_do=(ca.LOCAL_DUNG if dung else ca.LOCAL_SAI,), **kw)


def _gate(bo):
    return ca.CongAI(SETTINGS, bo_ghi=bo, moi_truong={}, mask=object())


class CoreDemo(KenhCore):
    """Kho chỉ ở phía Core fixture; SDK engine không có DB hay đường dẫn."""

    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.execute('CREATE TABLE IF NOT EXISTS nhat_ky '
                          '(tep_id TEXT PRIMARY KEY, khoa TEXT UNIQUE, raw TEXT)')
        self.loi_doc = False
        self.che_do = 'ack'
        self.payloads = []
        self.nguon_core = None
        self.yeu_cau = None

    def dong(self):
        self.conn.close()

    def xu_ly(self, operation, payload):
        if operation == 'doc_dau_vao':
            if self.loi_doc:
                raise RuntimeError('AI5A_CANARY_CORE')
            ids = [r[0] for r in self.conn.execute('SELECT tep_id FROM nhat_ky ORDER BY rowid')]
            result = {'nhat_ky_ai': {'tep_ids': ids, 'du_lieu_ket_qua': deepcopy(METADATA),
                                     'revision_tep_truoc': 0}}
            if self.nguon_core is not None or self.yeu_cau is not None:
                result.update(nguon_core=deepcopy(self.nguon_core), yeu_cau=deepcopy(self.yeu_cau))
            return result
        if operation == 'mo_doc':
            row = self.conn.execute('SELECT raw FROM nhat_ky WHERE tep_id=?',
                                    (payload['tep_id'],)).fetchone()
            if row is None:
                raise RuntimeError('Không được cấp tệp')
            return row[0]
        if operation != 'ghi_ket_qua':
            raise AssertionError(operation)
        self.payloads.append(deepcopy(payload))
        if self.che_do == 'loi_truoc':
            raise RuntimeError('AI5A_CANARY_TRUOC_COMMIT')
        record = json.loads(payload['raw'])
        khoa = json.dumps([record['ma_yeu_cau'], record['duong']])
        cu = self.conn.execute('SELECT tep_id, raw FROM nhat_ky WHERE khoa=?', (khoa,)).fetchone()
        if cu is not None:
            if cu[1] != payload['raw']:
                raise RuntimeError('Khác nội dung cùng khóa')
            tid = cu[0]
        else:
            tid = str(uuid4())
            with self.conn:
                self.conn.execute('INSERT INTO nhat_ky VALUES (?, ?, ?)',
                                  (tid, khoa, payload['raw']))
        if self.che_do == 'loi_sau':
            raise RuntimeError('AI5A_CANARY_SAU_COMMIT')
        return {'ket_qua_id': tid, 'da_ban_giao': self.che_do == 'ack'}

    def goi(self, operation, giu_viec, **payload):
        if operation == 'ghi_ket_qua':
            payload = {k: v for k, v in payload.items() if k != 'luong'} | {
                'raw': payload['luong'].read().decode('utf-8')}
        result = self.xu_ly(operation, payload)
        return io.BytesIO(result.encode('utf-8')) if operation == 'mo_doc' else result


class KenhPipe(KenhCore):
    """Engine con không nhận CoreDemo/SQLite/path, chỉ stream stdin/stdout."""

    def goi(self, operation, giu_viec, **payload):
        if operation == 'ghi_ket_qua':
            payload = {k: v for k, v in payload.items() if k != 'luong'} | {
                'raw': payload['luong'].read().decode('utf-8')}
        print(json.dumps({'operation': operation, 'payload': payload}), flush=True)
        result = json.loads(sys.stdin.readline())
        return io.BytesIO(result.encode('utf-8')) if operation == 'mo_doc' else result


def _child():
    def cam(event, args):
        if event in ('sqlite3.connect', 'socket.connect', 'socket.getaddrinfo'):
            raise AssertionError('Engine không được login CSDL/kết nối mạng')
    sys.addaudithook(cam)
    records = json.loads(sys.stdin.readline())
    bo = BoGhiQuaCore(SDKEngine(_lease(), kenh_core=KenhPipe()))
    for record in records:
        for key in ('ly_do', 'ly_do_chuyen_cloud'):
            record[key] = tuple(record[key])
        bo.ghi(ca.BanGhiCongAI(**record))
    assert bo.da_ban_giao()
    gate = _gate(bo)
    with patch.object(ca.random, 'random', return_value=0.1):
        chon = gate._chon_kiem(ca.loai_viec(LOAI))
    print(json.dumps({'result': {'thong_ke': gate.thong_ke(), 'chon': chon}}), flush=True)


class NhatKyCoreTest(unittest.TestCase):
    def setUp(self):
        self.path = Path(tempfile.mkdtemp(prefix='ktt-ai5a-demo-')) / 'core-demo.sqlite'
        self.core = CoreDemo(self.path)
        self.addCleanup(lambda: self.core.dong())
        self.bo = BoGhiQuaCore(SDKEngine(_lease(), kenh_core=self.core))

    def test_metadata_day_du_ghi_core_dong_mo_lai_doc_dung(self):
        b = _kiem(token_vao=12, token_ra=34, chi_phi_uoc_usd=0.012,
            so_ky_tu_gui=123, so_ky_tu_nhan=456, thoi_gian_ms=78,
            ma_luot_mask='DEMO-MASK', so_truong_bi_loai=1, trich_dan_hop_le=True,
            phap_nhan_id=str(uuid4()), viec_id=str(uuid4()), de_xuat_id=str(uuid4()))
        self.bo.ghi(b)
        raw = self.core.conn.execute('SELECT raw FROM nhat_ky').fetchone()[0]
        self.assertEqual(json.loads(raw), json.loads(json.dumps(b.thanh_dict())))
        self.assertEqual(self.core.payloads[0]['du_lieu'], METADATA)
        self.assertEqual(self.core.payloads[0]['revision_tep_truoc'], 0)
        self.core.dong()
        self.core = CoreDemo(self.path)
        moi = BoGhiQuaCore(SDKEngine(_lease(), kenh_core=self.core))
        self.assertEqual(moi.thong_ke(2)[LOAI], dict(so_luot=0, so_kiem=1,
                           so_kiem_cua_so=1, so_dung_cua_so=1))

    def _tien_trinh(self, records):
        proc = subprocess.Popen([sys.executable, '-B', '-X', 'utf8',
            str(Path(__file__).resolve()), '--child'], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        def dong():
            if proc.poll() is None:
                proc.kill()  # Chỉ tiến trình DEMO do test này tạo.
            proc.communicate(timeout=10)
        self.addCleanup(dong)
        q = queue.Queue()
        def doc():
            for line in proc.stdout:
                q.put(line)
            q.put(None)
        threading.Thread(target=doc, daemon=True).start()
        proc.stdin.write(json.dumps([r.thanh_dict() for r in records]) + '\n')
        proc.stdin.flush()
        while True:
            line = q.get(timeout=15)
            if line is None:
                self.fail('Engine thoát trước kết quả: ' + proc.stderr.read())
            message = json.loads(line)
            if 'result' in message:
                proc.wait(timeout=10)
                self.assertEqual(proc.returncode, 0, proc.stderr.read())
                return message['result']
            result = self.core.xu_ly(message['operation'], message['payload'])
            proc.stdin.write(json.dumps(result) + '\n')
            proc.stdin.flush()

    def test_dung_tien_trinh_restart_giu_thong_ke_do_chinh_xac_va_chon_mau(self):
        truoc = self._tien_trinh([_record(), _kiem(), _kiem()])
        self.core.dong()
        self.core = CoreDemo(self.path)
        sau = self._tien_trinh([])
        self.assertEqual(sau, truoc)
        tk = next(r for r in sau['thong_ke'] if r['loai_viec'] == LOAI)
        self.assertEqual((tk['so_luot'], tk['so_kiem'], tk['phan_tram_chinh_xac'],
                          tk['ty_le_kiem_hien_hanh']), (1, 2, 100, 0.05))
        self.assertFalse(sau['chon'])  # random=0.1: mặc định 20% sẽ chọn, 5% không chọn.

    def test_cua_so_thu_tu_va_loai_bo_luot_khong_du_dieu_kien_nhu_nguon(self):
        records = [_record(), _kiem(), _kiem(False),
            _kiem(luc='2026-10-30T10:00:00+00:00'),
            _kiem(ket_qua='LOI'), _kiem(da_gui=False),
            replace(_kiem(), ly_do=(ca.LOCAL_DUNG, ca.LOCAL_SAI)),
            replace(_kiem(), ly_do_chuyen_cloud=('DUOI_NGUONG',)),
            _record(loai_viec='DEMO_KHAC', da_gui=False)]
        goc = ca.BoGhiBoNho()
        for record in records:
            self.bo.ghi(record)
            goc.ghi(record)
        for n in (1, 2, 100):
            with self.subTest(cua_so=n):
                self.assertEqual(self.bo.thong_ke(n), goc.thong_ke(n))
        self.assertEqual(self.bo.thong_ke(1)[LOAI]['so_dung_cua_so'], 0)
        self.bo.ghi(_kiem(False, luc='2026-11-01T10:00:00+00:00'))
        tk = next(r for r in _gate(self.bo).thong_ke() if r['loai_viec'] == LOAI)
        self.assertEqual(tk['ty_le_kiem_hien_hanh'], 0.2)
        self.assertEqual(tk['canh_bao'], 'LOCAL_DUOI_NGUONG_CHINH_XAC')

    def test_chua_ack_loi_truoc_sau_commit_giu_bytes_thu_lai(self):
        for che_do in ('chua_ack', 'loi_truoc', 'loi_sau'):
            with self.subTest(che_do=che_do):
                bo = BoGhiQuaCore(SDKEngine(_lease(), kenh_core=self.core))
                self.core.che_do = che_do
                b = _record()
                with self.assertRaises((LoiNhatKy, LoiEngine)):
                    bo.ghi(b)
                self.assertFalse(bo.da_ban_giao())
                payload = deepcopy(self.core.payloads[-1])
                with self.assertRaises(LoiNhatKy):
                    bo.thong_ke(2)
                self.core.che_do = 'ack'
                bo.thu_lai()
                self.assertEqual(self.core.payloads[-1], payload)
                self.assertTrue(bo.da_ban_giao())
                self.assertEqual(self.core.conn.execute(
                    'SELECT count(*) FROM nhat_ky WHERE khoa=?',
                    (json.dumps([b.ma_yeu_cau, b.duong]),)).fetchone()[0], 1)

    def test_loi_snapshot_qua_cong_ai_giu_ban_ghi_chan_drain_retry_restart(self):
        snapshots = ({}, {'nhat_ky_ai': {'tep_ids': []}},
            {'nhat_ky_ai': {'tep_ids': [], 'du_lieu_ket_qua': METADATA,
                           'revision_tep_truoc': -1}})
        for loi in ('loi_doc', *snapshots):
            with self.subTest(loi=loi):
                b = _kiem()
                gate = _gate(self.bo)
                goi_goc = self.core.goi

                def goi(operation, giu_viec, **payload):
                    if operation == 'doc_dau_vao':
                        if loi == 'loi_doc':
                            raise RuntimeError('AI5A_CANARY_DOC')
                        return deepcopy(loi)
                    return goi_goc(operation, giu_viec, **payload)

                with patch.object(self.core, 'goi', side_effect=goi), \
                        self.assertLogs(ca._LOG, level='ERROR') as log:
                    gate._ghi(b)
                    self.assertFalse(self.bo.da_ban_giao())
                    with self.assertRaises((LoiEngine, LoiNhatKy)):
                        self.bo.thu_lai()
                    self.assertFalse(self.bo.da_ban_giao())
                    with self.assertRaises(LoiNhatKy):
                        self.bo.thong_ke(2)
                self.assertNotIn('AI5A_CANARY', str(log.output))
                self.bo.thu_lai()
                self.assertTrue(self.bo.da_ban_giao())
                self.assertEqual(json.loads(self.core.payloads[-1]['raw']),
                                 json.loads(json.dumps(b.thanh_dict())))
        self.core.dong()
        self.core = CoreDemo(self.path)
        sau = self._tien_trinh([])
        tk = next(r for r in sau['thong_ke'] if r['loai_viec'] == LOAI)
        self.assertEqual((tk['so_kiem'], tk['phan_tram_chinh_xac']), (4, 100))

    def test_cong_ai_goi_local_cloud_cho_ack_giu_du_hang_doi_qua_restart(self):
        van_ban = 'CANARY_NOI_DUNG_DEMO giá trị 123 đồng.'
        reply = json.dumps({'truong': [{'ten': 'gia_tri', 'gia_tri': '123 đồng',
                           'trich_dan': van_ban}], 'do_tin_cay': 1})
        cfg = deepcopy(SETTINGS)
        cfg['local_ai'] = {'enabled': True,
            'url': 'http://127.0.0.1:1234/v1/chat/completions', 'model': 'demo-local'}
        mask = Mock()
        mask.co_khoa.return_value = True
        mask.che.return_value = ca.LuotChe('DEMO-MASK', van_ban)
        mask.mo_che.side_effect = lambda ma, data, **kw: data
        provider = Mock()
        provider.tra_loi.return_value = ca.PhanHoiCloud(reply, 'demo-model', 12, 34)
        khoa_demo = 'AI5A_CANARY_KHOA_DEMO'
        gate = ca.CongAI(cfg, bo_ghi=self.bo,
                        moi_truong={'ANTHROPIC_API_KEY': khoa_demo}, mask=mask,
                        kiem_xac_suat=lambda loai: True)
        for che_do in ('chua_ack', 'loi_truoc', 'loi_sau'):
            with self.subTest(che_do=che_do):
                self.core.che_do = che_do
                with patch.object(ca.ai_cuc_bo, 'ask_local', return_value=reply), \
                        patch.object(gate, '_provider', return_value=provider), \
                        patch('socket.socket', side_effect=AssertionError('Không mạng')), \
                        self.assertLogs(ca._LOG, level='ERROR'):
                    kq = gate.goi(ca.YeuCauAI(LOAI, van_ban, 'Đọc DEMO', ('gia_tri',)))
                self.assertTrue(kq.co_ket_qua)
                self.assertFalse(self.bo.da_ban_giao())
                dau = deepcopy(self.core.payloads[-1])
                self.core.che_do = 'ack'
                # ACK Local rồi lỗi Cloud: drain vẫn phải bị chặn.
                goi_goc = self.core.goi

                def goi(operation, giu_viec, **payload):
                    if operation == 'ghi_ket_qua':
                        raw = payload['luong'].getvalue().decode('utf-8')
                        if json.loads(raw)['duong'] == 'CLOUD':
                            raise RuntimeError('AI5A_CANARY_CLOUD_COMMIT')
                    return goi_goc(operation, giu_viec, **payload)

                with patch.object(self.core, 'goi', side_effect=goi):
                    with self.assertRaises(LoiEngine):
                        self.bo.thu_lai()
                self.assertEqual(self.core.payloads[-1], dau)
                self.assertFalse(self.bo.da_ban_giao())
                with self.assertRaises(LoiNhatKy):
                    self.bo.thong_ke(2)
                self.bo.thu_lai()
                self.assertTrue(self.bo.da_ban_giao())
                rows = [json.loads(r[0]) for r in self.core.conn.execute(
                    'SELECT raw FROM nhat_ky ORDER BY rowid')]
                luot = [r for r in rows if r['ma_yeu_cau'] == kq.ma_yeu_cau]
                self.assertEqual([r['duong'] for r in luot], ['LOCAL', 'CLOUD'])
                self.assertIn(ca.LOCAL_DUNG, luot[1]['ly_do'])
                self.assertNotIn('CANARY', json.dumps(rows))
        self.assertEqual(provider.tra_loi.call_count, 3)  # Retry chỉ bàn giao metadata.
        for call in provider.tra_loi.call_args_list:
            self.assertEqual(call.kwargs['khoa'], khoa_demo)
        self.core.dong()
        self.core = CoreDemo(self.path)
        sau = self._tien_trinh([])
        tk = next(r for r in sau['thong_ke'] if r['loai_viec'] == LOAI)
        self.assertEqual((tk['so_luot'], tk['so_kiem'], tk['phan_tram_chinh_xac'],
                          tk['ty_le_kiem_hien_hanh']), (3, 3, 100, 0.05))
        self.assertFalse(sau['chon'])

    def test_khoa_api_rong_khong_goi_cloud(self):
        mask, provider = Mock(), Mock()
        gate = ca.CongAI(SETTINGS, bo_ghi=self.bo,
                        moi_truong={'ANTHROPIC_API_KEY': ''}, mask=mask,
                        nha_cung_cap=provider)
        with patch('socket.socket', side_effect=AssertionError('Không mạng')) as mang:
            kq = gate.goi(ca.YeuCauAI(LOAI, 'Nội dung DEMO', 'Đọc DEMO'))
        self.assertFalse(kq.co_ket_qua)
        self.assertIn('CHUA_CO_KHOA_API', kq.ly_do)
        provider.tra_loi.assert_not_called()
        mask.che.assert_not_called()
        mang.assert_not_called()
        rows = [json.loads(r[0]) for r in self.core.conn.execute(
            'SELECT raw FROM nhat_ky ORDER BY rowid')]
        cloud = [r for r in rows if r['duong'] == 'CLOUD']
        self.assertEqual(len(cloud), 1)
        self.assertFalse(cloud[0]['da_gui'])
        self.assertEqual(cloud[0]['ket_qua'], 'KHONG_GUI')
        self.assertEqual(cloud[0]['ly_do_khong_gui'], 'CHUA_CO_KHOA_API')
        self.assertTrue(self.bo.da_ban_giao())

    def test_loi_doc_khong_am_tham_tra_rong_hay_giam_ty_le(self):
        self.bo.ghi(_kiem())
        self.bo.ghi(_kiem())
        self.core.loi_doc = True
        with self.assertRaises(LoiEngine):
            self.bo.thong_ke(2)
        with self.assertLogs(ca._LOG, level='ERROR') as log:
            tk = next(r for r in _gate(self.bo).thong_ke() if r['loai_viec'] == LOAI)
        self.assertFalse(tk['thong_ke_san_sang'])
        self.assertIsNone(tk['so_kiem'])
        self.assertEqual(tk['ty_le_kiem_hien_hanh'], 0.2)
        self.assertNotIn('AI5A_CANARY', str(log.output))
        self.core.loi_doc = False
        self.assertEqual(self.bo.thong_ke(2)[LOAI]['so_kiem'], 2)

    def test_snapshot_thieu_tap_tin_hong_bi_tu_choi_khong_dung_cache(self):
        self.assertEqual(self.bo.thong_ke(2), {})
        for data in ({}, {'nhat_ky_ai': {}}, {'nhat_ky_ai': {'tep_ids': ['x', 'x']}}):
            with self.subTest(data=data), patch.object(self.core, 'goi', return_value=data):
                with self.assertRaises(LoiNhatKy):
                    self.bo.thong_ke(2)
        self.bo.ghi(_record())
        for raw in ('{', '{}', '{"van_ban": "DEMO"}'):
            with self.core.conn:
                self.core.conn.execute('UPDATE nhat_ky SET raw=?', (raw,))
            with self.assertRaises(LoiNhatKy):
                self.bo.thong_ke(2)

    def test_local_qua_cong_ai_chi_luu_metadata_khong_luu_van_ban(self):
        van_ban = 'CANARY_NOI_DUNG_DEMO giá trị 123 đồng.'
        cfg = {'local_ai': {'enabled': True, 'url': 'http://127.0.0.1:1234/v1/chat/completions',
                            'model': 'demo-local'}}
        gate = ca.CongAI(cfg, bo_ghi=self.bo, moi_truong={}, mask=object())
        reply = json.dumps({'truong': [{'ten': 'gia_tri', 'gia_tri': '123 đồng',
                           'trich_dan': van_ban}], 'do_tin_cay': 1})
        with patch.object(ca.ai_cuc_bo, 'ask_local', return_value=reply), \
                patch('socket.socket', side_effect=AssertionError('Không mạng')):
            gate.goi(ca.YeuCauAI(LOAI, van_ban, 'Đọc DEMO', ('gia_tri',)))
        raw = ''.join(r[0] for r in self.core.conn.execute('SELECT raw FROM nhat_ky'))
        for canary in ('CANARY_NOI_DUNG_DEMO', '123 đồng', 'Đọc DEMO', 'AI5A_CANARY_'):
            self.assertNotIn(canary, raw)
        self.assertEqual(self.bo.thong_ke(2)[LOAI]['so_luot'], 1)

    def test_lease_het_han_khong_doc_ghi_core(self):
        giu = replace(_lease(), giu_den=datetime.now(timezone.utc) - timedelta(seconds=1))
        bo = BoGhiQuaCore(SDKEngine(giu, kenh_core=self.core))
        with patch.object(self.core, 'goi') as goi:
            for action in (lambda: bo.thong_ke(2), lambda: bo.ghi(_record()), bo.thu_lai):
                with self.assertRaisesRegex(LoiEngine, 'VIEC_MAT_LEASE'):
                    action()
            self.assertFalse(bo.da_ban_giao())
            with self.assertRaisesRegex(LoiNhatKy, 'NHAT_KY_CHO_ACK'):
                bo.thong_ke(2)
            goi.assert_not_called()

    def test_cua_so_dto_nan_va_bi_mat(self):
        for n in (0, -1, True, 1.5, None):
            with self.subTest(n=n), self.assertRaises(ValueError):
                self.bo.thong_ke(n)
        with self.assertRaises(TypeError):
            BoGhiQuaCore(object())
        with self.assertRaises(TypeError):
            self.bo.ghi({'van_ban': 'DEMO'})
        with self.assertRaises(ValueError):
            self.bo.ghi(_record(chi_phi_uoc_usd=float('nan')))
        self.assertFalse(hasattr(self.bo, '__dict__'))
        self.assertNotIn('CANARY', repr(self.bo))
        with self.assertRaises(TypeError):
            pickle.dumps(self.bo)


class ProvenanceCoreTest(unittest.TestCase):
    """Provider gói đã cài được Core giả tiêm, tách khỏi payload engine."""

    def setUp(self):
        from kho_tri_thuc.core.dispatcher import KiemSchema
        from kho_tri_thuc.engines.e_hoi_ai.hoi import AdapterHoiAI
        self.path = Path(tempfile.mkdtemp(prefix='ktt-ai1b09-demo-')) / 'core-demo.sqlite'
        self.core = CoreDemo(self.path)
        self.addCleanup(self.core.dong)
        self.lease = _lease()
        tep = str(uuid4())
        self.nguon = dict(ma_module=self.lease.module, ma_function='trich_hop_dong',
            ma_prompt='trich_tien_demo', phien_ban_prompt='3',
            phap_nhan_id=str(self.lease.phap_nhan_id), viec_id=str(self.lease.viec_id),
            revision=1, nguon_tep_ids=[tep], vi_tri=dict(tep_id=tep, dinh_vi='doan:1'))
        # Đây là đầu ra tin cậy của Core.nguon_hoi_ai sau provider/SHA gói.
        # Không coi fixture này là bài kiểm PG/cài gói production.
        self.core.nguon_core = deepcopy(self.nguon)
        self.prompt = 'CANARY_PROMPT_DEMO: trích giá trị có căn cứ, không đoán.'
        self.van_ban = 'CANARY_TAI_LIEU_DEMO: giá trị CANARY_TRA_LOI_DEMO.'
        self.url = 'http://127.0.0.1:1234/v1/chat/completions'
        self.khoa = 'CANARY_KHOA_DEMO_1b09'
        self.core.yeu_cau = dict(chi_dan=self.prompt, van_ban=self.van_ban,
            ma_prompt='gia_danh_tu_payload', phien_ban_prompt='999',
            nguon_core=dict(ma_prompt='gia_danh_long_payload'))
        self.bo = BoGhiQuaCore(SDKEngine(self.lease, kenh_core=self.core))
        self.cfg = dict(local_ai=dict(enabled=True, url=self.url, model='local-DEMO'),
            cong_ai=dict(cloud_bat=True),
            model_phat_hien=[dict(id_model='local-DEMO', bat=True, trang_thai='san_sang'),
                             dict(id_model='du-phong-DEMO', bat=True, trang_thai='san_sang')],
            quy_tac_model=[dict(module=self.lease.module, function='trich_hop_dong',
                bat=True, che_do='tu_chon', uu_tien='local-DEMO', du_phong=['du-phong-DEMO'])])
        self.mask, self.cloud = Mock(), Mock()
        self.gate = ca.CongAI(self.cfg, bo_ghi=self.bo, moi_truong={'ANTHROPIC_API_KEY': self.khoa},
            mask=self.mask, nha_cung_cap=self.cloud)
        self.adapter = AdapterHoiAI(self.gate, kiem_schema=KiemSchema().kiem)
        self.enterContext(patch.object(ca.ai_cuc_bo, 'discover_local_models', return_value=dict(
            ma_loi='', model_phat_hien=deepcopy(self.cfg['model_phat_hien']))))
        self.local = self.enterContext(patch.object(ca.ai_cuc_bo, 'ask_local', return_value=json.dumps(
            dict(truong=[dict(ten='gia_tri', gia_tri='CANARY_TRA_LOI_DEMO', trich_dan=self.van_ban)],
                 do_tin_cay=1), ensure_ascii=False)))
        self.enterContext(patch('socket.socket', side_effect=AssertionError('Cấm mạng thật')))
        self.cloud_path = self.enterContext(patch.object(ca.CongAI, '_cloud',
            side_effect=AssertionError('Bản 1 phải có 0 lượt Cloud')))
        self.enterContext(patch.object(ca, 'doc_khoa_mask', side_effect=AssertionError('Cấm đọc khóa')))

    def goi(self, loai=LOAI):
        yc = dict(loai_viec=loai, van_ban=self.van_ban, chi_dan=self.prompt, truong=['gia_tri'],
            **{k: self.nguon[k] for k in ('ma_function', 'ma_prompt', 'phien_ban_prompt')})
        return self.adapter.goi(yc, nguon_core=self.nguon)

    def rows(self):
        return [json.loads(r[0]) for r in self.core.conn.execute('SELECT raw FROM nhat_ky ORDER BY rowid')]

    def kiem_khong_lo(self, row):
        raw = json.dumps(row, ensure_ascii=False)
        for value in (self.prompt, self.van_ban, 'CANARY_TRA_LOI_DEMO', self.khoa,
                      self.url, '127.0.0.1', 'gia_danh_tu_payload', 'gia_danh_long_payload',
                      'AI5A_CANARY_'):
            self.assertNotIn(value, raw)

    def tearDown(self):
        self.cloud_path.assert_not_called()
        self.cloud.tra_loi.assert_not_called()
        self.mask.che.assert_not_called()

    def test_du_truong_nguon_goi_cai_thoi_diem_va_ket_qua_kiem(self):
        dau, cuoi = '2026-11-08T01:02:03+00:00', '2026-11-08T01:02:04+00:00'
        with patch.object(ca, '_luc', side_effect=[dau, cuoi]):
            out = self.goi()
        row, = self.rows()
        self.assertEqual(set(row), set(_record().thanh_dict()) | ca.TRUONG_PROVENANCE)
        self.assertEqual(row['ma_yeu_cau'], out['ma_yeu_cau_nguon'])
        self.assertEqual({k: row[k] for k in ('ma_module', 'ma_function', 'ma_prompt', 'phien_ban_prompt')},
                         {k: self.nguon[k] for k in ('ma_module', 'ma_function', 'ma_prompt', 'phien_ban_prompt')})
        self.assertEqual((row['model'], row['ly_do_chon_model']), ('local-DEMO', 'uu_tien'))
        self.assertEqual((row['luc_bat_dau'], row['luc_ket_thuc']), (dau, cuoi))
        self.assertEqual((row['ket_qua_kiem'], row['ma_ly_do_kiem']), ('dat', 'DAT'))
        self.kiem_khong_lo(row)
        self.kiem_khong_lo(self.core.payloads[-1]['du_lieu'])
        self.assertTrue(self.bo.da_ban_giao())
        self.assertEqual(self.bo.thong_ke(2)[LOAI]['so_luot'], 1)

    def test_mo_hinh_du_phong_va_co_dinh_ghi_dung_ly_do(self):
        self.gate.cau_hinh_model['model_phat_hien'][0]['bat'] = False
        self.goi()
        self.assertEqual((self.rows()[-1]['model'], self.rows()[-1]['ly_do_chon_model']),
                         ('du-phong-DEMO', 'du_phong:1'))
        rule = self.gate.cau_hinh_model['quy_tac_model'][0]
        rule.update(che_do='co_dinh', uu_tien='du-phong-DEMO')
        self.goi()
        self.assertEqual(self.rows()[-1]['ly_do_chon_model'], 'co_dinh')
        self.assertEqual(self.local.call_count, 2)

    def test_chay_thu_nhat_ky_nguon_that_va_thong_ke_rieng(self):
        out = self.goi('CHAY_THU')
        row, = self.rows()
        self.assertEqual(row['loai_viec'], 'CHAY_THU')
        self.assertEqual((row['ma_module'], row['ma_function']),
                         (self.lease.module, 'trich_hop_dong'))
        self.assertEqual(row['ly_do_chon_model'], 'uu_tien')
        self.assertIn('uu_tien', out['ly_do'])
        self.assertNotIn('uu_tien', out['thong_bao'])
        self.kiem_khong_lo(row)
        reloaded = BoGhiQuaCore(SDKEngine(self.lease, kenh_core=self.core))
        stats = reloaded.thong_ke(2)
        self.assertEqual(stats['CHAY_THU']['so_luot'], 1)
        self.assertNotIn('HOI_DAP_VAY', stats)
        self.assertNotIn(LOAI, stats)
        from kho_tri_thuc.engines.e_hoi_ai.nhat_ky import _ban_ghi
        self.assertEqual(_ban_ghi(row).loai_viec, 'CHAY_THU')
        with self.assertRaises(LoiNhatKy):
            _ban_ghi({**row, 'loai_viec': 'LOAI_CHUA_KHAI_BAO'})

    def test_loi_local_van_ghi_ma_dong_khong_giu_thong_diep_loi(self):
        for exc, ma in ((ca.ai_cuc_bo.LocalAIUnavailable(self.prompt), 'LOCAL_KHONG_CHAY'),
                        (RuntimeError(self.prompt + self.khoa + self.url), 'LOCAL_LOI')):
            with self.subTest(ma=ma):
                self.local.side_effect = exc
                self.goi()
                row = self.rows()[-1]
                self.assertEqual((row['ket_qua_kiem'], row['ma_ly_do_kiem'], row['loi']),
                                 ('tu_choi', ma, ma))
                self.assertEqual(row['ma_prompt'], self.nguon['ma_prompt'])
                self.assertLessEqual(datetime.fromisoformat(row['luc_bat_dau']),
                                     datetime.fromisoformat(row['luc_ket_thuc']))
                self.kiem_khong_lo(row)
        self.assertEqual(len(self.rows()), 2)

    def test_thieu_model_tu_choi_va_khong_can_cu_la_ket_qua_hop_le(self):
        self.gate.cau_hinh_model['quy_tac_model'][0]['bat'] = False
        self.goi()
        row, = self.rows()
        self.assertEqual((row['model'], row['ma_ly_do_kiem']), ('', 'LOCAL_KHONG_CO_MODEL'))
        self.local.assert_not_called()
        self.gate.cau_hinh_model['quy_tac_model'][0]['bat'] = True
        self.local.return_value = json.dumps(dict(truong=[], do_tin_cay=1))
        self.goi()
        self.assertEqual((self.rows()[-1]['ket_qua_kiem'], self.rows()[-1]['ma_ly_do_kiem']),
                         ('dat', 'KHONG_THAY_CAN_CU'))

    def test_ket_qua_kiem_tu_choi_khi_json_hoac_trich_dan_sai(self):
        for answer, ma in (('không phải JSON', 'PHAN_HOI_KHONG_HOP_LE'),
                (json.dumps(dict(truong=[dict(ten='gia_tri', gia_tri='sai',
                    trich_dan='không có trong tài liệu')], do_tin_cay=1)), 'TRICH_DAN_SAI')):
            with self.subTest(ma=ma):
                self.local.return_value = answer
                self.goi()
                self.assertEqual((self.rows()[-1]['ket_qua_kiem'], self.rows()[-1]['ma_ly_do_kiem']),
                                 ('tu_choi', ma))

    def test_ack_phat_lai_cung_ma_khong_trung_va_khong_goi_ai_lai(self):
        self.core.che_do = 'loi_sau'
        with self.assertLogs(ca._LOG, level='ERROR'):
            self.goi()
        dau = deepcopy(self.core.payloads[-1])
        self.assertFalse(self.bo.da_ban_giao())
        self.core.nguon_core['ma_prompt'] = 'prompt_moi_khong_duoc_doi_retry'
        self.core.che_do = 'ack'
        self.bo.thu_lai()
        self.assertEqual(self.core.payloads[-1], dau)
        self.local.assert_called_once()
        self.assertEqual(len(self.rows()), 1)
        self.core.nguon_core = deepcopy(self.nguon)
        row, = self.rows()
        for key in ('ly_do', 'ly_do_chuyen_cloud'):
            row[key] = tuple(row[key])
        # Cùng mã tương quan, kể cả bộ ghi vừa khởi động lại.
        moi = BoGhiQuaCore(SDKEngine(self.lease, kenh_core=self.core))
        so_lan_ghi = len(self.core.payloads)
        moi.ghi(ca.BanGhiHoiAI(**row))
        self.assertEqual(len(self.core.payloads), so_lan_ghi)  # Không dựa vào UNIQUE của Core giả.
        self.assertEqual(len(self.rows()), 1)
        self.assertEqual(moi.thong_ke(2)[LOAI]['so_luot'], 1)

    def test_thieu_nguon_provider_giu_hang_doi_khong_lay_payload(self):
        self.core.nguon_core = None
        with self.assertLogs(ca._LOG, level='ERROR'):
            self.goi()
        self.assertEqual(self.rows(), [])
        self.assertFalse(self.bo.da_ban_giao())
        self.core.nguon_core = deepcopy(self.nguon)
        self.bo.thu_lai()
        self.assertEqual(self.rows()[0]['ma_prompt'], 'trich_tien_demo')
        self.local.assert_called_once()

    def test_ma_prompt_tu_payload_engine_khong_the_thay_nguon_provider(self):
        self.goi()
        row, = self.rows()
        row['ma_prompt'] = 'gia_danh_tu_payload'
        for key in ('ly_do', 'ly_do_chuyen_cloud'):
            row[key] = tuple(row[key])
        with self.assertRaisesRegex(LoiNhatKy, 'NHAT_KY_NGUON_KHONG_KHOP'):
            self.bo.ghi(ca.BanGhiHoiAI(**row))
        self.assertEqual(len(self.rows()), 1)

    def test_nguon_khac_module_function_phap_nhan_viec_bi_chan(self):
        for key in ('ma_module', 'ma_function', 'phap_nhan_id', 'viec_id'):
            with self.subTest(key=key):
                self.core.nguon_core[key] = str(uuid4()) if key.endswith('_id') else 'gia_danh'
                truoc = len(self.rows())
                with self.assertLogs(ca._LOG, level='ERROR'):
                    self.goi()
                self.assertEqual(len(self.rows()), truoc)
                self.assertFalse(self.bo.da_ban_giao())
                self.core.nguon_core = deepcopy(self.nguon)
                self.bo.thu_lai()
                self.assertEqual(len(self.rows()), truoc + 1)

    def test_phat_lai_cung_ma_khac_noi_dung_bi_chan(self):
        self.goi()
        row, = self.rows()
        row['model'] = 'du-phong-DEMO'
        so_lan_ghi = len(self.core.payloads)
        with self.assertRaisesRegex(LoiNhatKy, 'NHAT_KY_TRUNG_MA_KHAC_NOI_DUNG'):
            self.bo.ghi(ca.BanGhiHoiAI(**row))
        self.assertEqual(len(self.core.payloads), so_lan_ghi)
        self.assertEqual(len(self.rows()), 1)

    def test_mutation_prompt_trong_bat_ky_truong_nhat_ky_bi_phat_hien(self):
        from kho_tri_thuc.engines.e_hoi_ai.nhat_ky import _ban_ghi
        self.goi()
        row, = self.rows()
        for key in row:
            with self.subTest(key=key):
                mutated = {**row, key: self.prompt}
                with self.assertRaises(LoiNhatKy):
                    _ban_ghi(mutated)
                # Chứng minh kiểm chống rò đỏ ngay cả khi serializer gán
                # prompt vào một tên trường đã được cho phép.
                with self.assertRaises(AssertionError):
                    self.kiem_khong_lo(mutated)
        for key in ('ket_qua_kiem', 'ma_ly_do_kiem', 'ly_do', 'loi', 'ly_do_chon_model'):
            with self.subTest(ma_ngoai_danh_sach=key), self.assertRaises(LoiNhatKy):
                _ban_ghi({**row, key: ['MA_TU_CHE'] if key == 'ly_do' else 'MA_TU_CHE'})
        for value in (self.url, self.van_ban):
            with self.subTest(model=value), self.assertRaises(LoiNhatKy):
                _ban_ghi({**row, 'model': value})
        with self.assertRaises(AssertionError):
            self.kiem_khong_lo({**row, 'model': self.khoa})


if __name__ == '__main__':
    if '--child' in sys.argv:
        _child()
    else:
        unittest.main()
