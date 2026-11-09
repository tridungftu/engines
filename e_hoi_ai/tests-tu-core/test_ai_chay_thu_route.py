"""AI-LAT10a: WSGI thật trong tiến trình, CSDL/Local giả, không mở socket."""
from contextlib import contextmanager, nullcontext
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import io
import json
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

from kho_tri_thuc.core import dispatcher as d, http, kenh_engine as ke, phien
from kho_tri_thuc.core import routes_quan_tri as r, ung_dung as u, viec, dich_vu_engine as dv
from kho_tri_thuc.engines.e_hoi_ai import chay as ai
from kho_tri_thuc.sdk_core.engine import KenhCore, SDKEngine
from tests import test_g2_32_e2 as e2
from kho_tri_thuc.engines.e_hoi_ai.lib import cong_ai as ca
from tests import test_g2_18 as g18, test_g2_32a as web


PATH = '/api/v1/quan-tri/hoi-ai/chay-thu'
SECRET = 'CANARY postgresql://bi_mat@may_ai/ Traceback'
TAI_LIEU = 'DEMO: Giá trị hợp đồng 1.000.000 đồng, thanh toán ngày 08/11/2026.'
BODY = dict(ma_module='mau_demo', ma_function='thanh_toan', tai_lieu=TAI_LIEU,
            cau_hoi='Số tiền cần thanh toán là bao nhiêu?')
FUNCTION = dict(ma_module='mau_demo', ten_module='Nghiệp vụ thử nghiệm', ma_function='thanh_toan',
    ten_function='Tra cứu thanh toán', ma_prompt='thanh_toan', phien_ban_prompt='1',
    phien_ban_module='1.0.0', ma_bam_goi='a'*64)
NOW = datetime(2026, 11, 8, 1, 2, 3, tzinfo=timezone.utc)


def sql_error(code, state='42501'):
    err = RuntimeError(SECRET)
    err.diag, err.sqlstate = SimpleNamespace(message_primary=code), state
    return err


class KhoGia:
    def __init__(self):
        self.info = SimpleNamespace(transaction_status=0)
        self.rows, self.jobs, self.calls, self.events = {}, {}, [], []
        self.admin, self.demo, self.valid = True, True, True
        self.fail_commit = False
        self.worker_error = None
        self.fail_finish = False

    @contextmanager
    def transaction(self):
        before = deepcopy((self.rows, self.jobs))
        self.info.transaction_status = 2
        try:
            yield
            if self.fail_commit:
                raise RuntimeError(SECRET)
        except Exception:
            self.rows, self.jobs = before
            self.events.append('rollback')
            raise
        else:
            self.events.append('commit')
        finally:
            self.info.transaction_status = 0

    def execute(self, sql, args=None):
        assert self.info.transaction_status == 2
        self.calls.append((sql, args))
        if sql.startswith('SELECT set_config('):
            return SimpleNamespace(fetchone=lambda: (None,))
        name = sql.split('loi.')[1].split('(')[0]
        if name == 'ai_chay_thu_quyen':
            for ok, code in ((self.valid, 'AI_THU_PHIEN'), (self.admin, 'AI_THU_ADMIN'), (self.demo, 'AI_THU_DEMO')):
                if not ok:
                    raise sql_error(code)
            value = None
        elif name == 'ai_chay_thu_xep':
            ma, actor, pn, identity, module, function, raw = args
            value = str(identity)
            inp = json.loads(raw)
            if value in self.rows:
                row = self.rows[value]
                if (row['ma_module'], row['ma_function'], row['dau_vao']) != (module, function, inp):
                    raise sql_error('AI_THU_CAS', '23505')
            else:
                self.rows[value] = dict(id=value, phap_nhan_id=str(pn), ma_module=module, ma_function=function,
                    dau_vao=inp, trang_thai='dang_cho', ket_qua=None, tao_luc=NOW.isoformat(),
                    bat_dau=None, ket_thuc=None, tao_boi=str(actor))
                self.jobs[value] = 'CHO'
        elif name == 'ai_chay_thu_doc':
            row = self.rows.get(str(args[-1]))
            value = row if row and row['phap_nhan_id'] == str(args[2]) else None
        elif name == 'ai_chay_thu_lich_su':
            value = [row for row in self.rows.values() if row['phap_nhan_id'] == str(args[2])][:args[-1]]
        elif name == 'ai_chay_thu_dau_vao':
            if self.worker_error:
                raise self.worker_error
            value = next(iter(self.rows.values()))
            value['trang_thai'], value['bat_dau'] = 'dang_chay', NOW.isoformat()
        elif name == 'ai_chay_thu_ghi_ket_qua':
            if self.worker_error:
                raise self.worker_error
            row = next(iter(self.rows.values()))
            assert row['trang_thai'] == args[-3]
            row.update(trang_thai=args[-2], ket_qua=json.loads(args[-1]), ket_thuc=NOW.isoformat())
            if self.fail_finish:
                raise sql_error('VIEC_MAT_LEASE', '40001')
            self.jobs[next(iter(self.rows))] = 'XONG' if args[-2] == 'xong' else 'LOI'
            value = True
        elif name == 'viec_ket_thuc':
            if self.fail_finish:
                raise sql_error('VIEC_MAT_LEASE', '40001')
            self.jobs[next(iter(self.rows))] = args[7]
            value = True
        else:
            raise AssertionError(sql)
        return SimpleNamespace(fetchone=lambda: (deepcopy(value),))


class AIChayThuHTTPTests(unittest.TestCase):
    def setUp(self):
        self.conn = KhoGia()
        self.ma = phien.MaBiMat('AI_THU_PHIEN_DEMO')
        self.session = http.PhienHTTP(g18.USER, phien.MaBiMat('CSRF_CANARY'),
            Mock(return_value=self.ma), g18.NOW, g18.NOW)
        self.connect = Mock(side_effect=lambda **kw: nullcontext(self.conn))
        self.enterContext(patch.object(u, 'nap_cau_hinh', return_value=web.CONFIG))
        self.catalog = Mock(return_value=[deepcopy(FUNCTION)])
        self.enterContext(patch.object(ke, 'doc_function_chay_thu_hoi_ai', self.catalog))
        self.guards = [self.enterContext(patch(target, side_effect=AssertionError('Cấm I/O thật')))
            for target in ('socket.socket', 'socket.create_connection', 'socket.getaddrinfo', 'subprocess.Popen')]
        self.portal = self.enterContext(patch.object(ca.CongAI, 'goi', side_effect=AssertionError('Web không gọi AI')))
        self.app = u.tao_ung_dung('CAU_HINH_GIA_KHONG_DOC', ket_noi=self.connect,
            doc_phien=lambda _: self.session, doc_kt=Mock(side_effect=AssertionError('Không gọi engine')),
            kiem=d.KiemSchema(), dong_ho=lambda: g18.NOW)

    def tearDown(self):
        for guard in self.guards:
            guard.assert_not_called()
        self.portal.assert_not_called()

    def call(self, suffix='', method='GET', body=None, headers=None):
        result = web.wsgi(self.app, PATH + suffix, method, body=body, headers=headers)
        for value in (SECRET, 'AI_THU_PHIEN_DEMO', 'CSRF_CANARY'):
            self.assertNotIn(value, repr(result))
        self.assertEqual(result['headers']['Cache-Control'], 'no-store')
        return result

    def post(self, body=None, headers=None):
        return self.call(method='POST', body=deepcopy(BODY) if body is None else body, headers=headers)

    def test_factory_dang_ky_du_bon_route_khong_io(self):
        self.connect.assert_not_called()
        self.catalog.assert_not_called()
        registry = self.app.http.dispatcher.registry
        for method, suffix in (('GET', '/function'), ('POST', ''), ('GET', '/'+str(uuid4())), ('GET', '')):
            route, _ = registry.tra(method, PATH + suffix)
            self.assertEqual(route.hanh_dong, 'CORE:ENGINE:CAU_HINH')
            self.assertIs(route, self.app.http.dispatcher.core.registry.tra(method, PATH + suffix)[0])

    def test_function_chi_metadata_khong_prompt_bam_va_phien_ban_goi(self):
        result = self.call('/function')
        self.assertEqual(result['status'], 200, result)
        item, = result['body']['danh_sach']
        self.assertEqual(item['ten_function'], FUNCTION['ten_function'])
        self.assertNotIn('ma_bam_goi', item)
        self.assertNotIn('phien_ban_module', item)
        self.assertNotIn('chi_dan', item)

    def test_post_202_sau_commit_gim_prompt_va_khong_chay_ai(self):
        result = self.post()
        self.assertEqual(result['status'], 202, result)
        identity = result['body']['ma_luot']
        self.assertEqual(result['headers']['Location'], PATH + '/' + identity)
        self.assertEqual(self.conn.info.transaction_status, 0)
        self.assertEqual(self.conn.events, ['commit'])
        row = self.conn.rows[identity]
        self.assertEqual(row['dau_vao']['ma_bam_goi'], 'a'*64)
        self.assertEqual(row['dau_vao']['phien_ban_prompt'], '1')
        self.assertEqual(self.conn.jobs[identity], 'CHO')

    def test_replay_khong_lap_viec_cung_khoa_khac_noi_dung_409(self):
        a, b = self.post(), self.post()
        self.assertEqual(a['body'], b['body'])
        self.assertEqual(len(self.conn.jobs), 1)
        result = self.post({**BODY, 'cau_hoi': 'Câu hỏi khác'})
        self.assertEqual(result['status'], 409, result)
        self.assertEqual(len(self.conn.jobs), 1)

    def test_lich_su_doc_mot_ngay_viet_khong_tra_dau_vao(self):
        identity = self.post()['body']['ma_luot']
        result = self.call('/'+identity)
        self.assertEqual(result['status'], 200, result)
        self.assertEqual(result['body']['tao_luc'], '08/11/2026 08:02:03')
        self.assertEqual(result['body']['trang_thai'], 'dang_cho')
        self.assertNotIn('dau_vao', result['body'])
        self.assertEqual(self.call('?gioi_han=50')['body']['danh_sach'], [result['body']])
        self.assertEqual(self.conn.calls[-1][1][-1], 50)

    def test_401_403_truoc_provider_cho_ca_bon_route(self):
        for flag, status in (('valid', 401), ('admin', 403), ('demo', 403)):
            setattr(self.conn, flag, False)
            for suffix, method, body in (('/function', 'GET', None), ('', 'POST', BODY),
                    ('/'+str(uuid4()), 'GET', None), ('', 'GET', None)):
                self.assertEqual(self.call(suffix, method, body)['status'], status)
            setattr(self.conn, flag, True)
        self.catalog.assert_not_called()
        self.assertFalse(self.conn.jobs)

    def test_thieu_sai_csrf_origin_phien_va_phap_nhan(self):
        for headers in ({'X-CSRF-Token': None}, {'X-CSRF-Token': 'sai'}, {'Origin': 'http://khac.invalid'}):
            self.assertEqual(self.post(headers=headers)['status'], 403)
        for pn in (None, 'sai'):
            self.assertEqual(self.post(headers={'X-Phap-Nhan-Id': pn})['status'], 400)
        self.session = None
        self.assertEqual(self.call('/function')['status'], 401)
        self.assertEqual(self.post()['status'], 403)
        self.catalog.assert_not_called()

    def test_thieu_phap_nhan_huong_dan_chon_demo_truoc_doc_goi(self):
        for suffix, method, body in (('/function', 'GET', None), ('', 'POST', BODY),
                ('/'+str(uuid4()), 'GET', None), ('', 'GET', None)):
            with self.subTest(suffix=suffix, method=method):
                result = self.call(suffix, method, body, headers={'X-Phap-Nhan-Id': None})
                self.assertEqual(result['status'], 400)
                self.assertEqual(result['body']['thong_diep'], 'Chọn pháp nhân DEMO để chạy thử.')
        self.catalog.assert_not_called()
        self.assertFalse(self.conn.calls)

    def test_dung_phien_core_theo_phap_nhan_nhu_mask_khong_muon_bootstrap(self):
        selected = uuid4()
        lay_ma = Mock(side_effect=lambda module, pn: self.ma if (module, pn) == ('core', selected) else None)
        self.session = replace(self.session, lay_ma=lay_ma)
        result = self.call('/function', headers={'X-Phap-Nhan-Id': str(selected)})
        self.assertEqual(result['status'], 200, result)
        lay_ma.assert_called_once_with('core', selected)
        self.assertEqual(self.conn.calls[0][1], (self.ma.lay_de_truyen(), g18.USER, selected))
        self.catalog.reset_mock()
        result = self.call('/function')
        self.assertEqual(result['status'], 401, result)
        self.assertEqual(result['body']['ma'], 'AI_THU_PHIEN')
        self.assertIn('Chọn pháp nhân DEMO để chạy thử', result['body']['thong_diep'])
        self.assertIn('đăng nhập lại', result['body']['thong_diep'])
        self.catalog.assert_not_called()
        self.assertNotIn(('core', None), [call.args for call in lay_ma.call_args_list])

    def test_kho_phien_chung_dang_nhap_cap_core_cho_tung_phap_nhan(self):
        other = uuid4()
        tokens = {g18.PN: self.ma, other: phien.MaBiMat('PHIEN_DEMO_THU_HAI')}
        scopes = {('core', pn): ('CORE:PHAP_NHAN:XEM', 'CORE:ENGINE:CAU_HINH') for pn in tokens}
        kho = u._KhoPhien(self.connect, lambda conn, actor: scopes, lambda: g18.NOW)
        with patch.object(self.conn, 'execute') as execute, \
                patch.object(u.mat_khau, 'xac_thuc', return_value=SimpleNamespace(http_status=200, nguoi_dung_id=g18.USER)), \
                patch.object(phien, 'cap_phien', side_effect=lambda conn, **kw: SimpleNamespace(ma=tokens[kw['phap_nhan_id']])) as cap, \
                patch.object(phien, 'xac_minh_phien', return_value=SimpleNamespace(nguoi_dung_id=g18.USER)):
            execute.return_value.fetchone.return_value = ('login_demo',)
            kho._dang_nhap(dict(ten_dang_nhap='nguoi_demo', mat_khau='mat_khau_gia'), 'dia_chi_gia')
        self.assertEqual({(c.kwargs['module'], c.kwargs['phap_nhan_id']) for c in cap.call_args_list}, set(scopes))
        self.session = next(iter(kho._ban.values())).http
        for pn, token in tokens.items():
            result = self.call('/function', headers={'X-Phap-Nhan-Id': str(pn)})
            self.assertEqual(result['status'], 200, result)
            self.assertEqual(self.conn.calls[-1][1], (token.lay_de_truyen(), g18.USER, pn))

    def test_tran_kich_thuoc_sai_kieu_truong_la_va_thieu_prompt(self):
        for change in ({'tai_lieu': 'x'*20001}, {'cau_hoi': 'x'*2001}, {'tai_lieu': 1},
                       {'prompt': 'không nhận prompt HTTP'}, {'ma_module': '../goi'}):
            self.assertEqual(self.post({**BODY, **change})['status'], 422)
        self.catalog.assert_not_called()
        self.assertEqual(self.post({**BODY, 'tai_lieu': ' '})['status'], 422)
        self.catalog.return_value = []
        self.assertEqual(self.post()['status'], 422)
        self.assertFalse(self.conn.rows)

    def test_dung_tran_unicode_duoc_xep(self):
        self.assertEqual(self.post({**BODY, 'tai_lieu': 'ệ'*20000, 'cau_hoi': 'ồ'*2000})['status'], 202)

    def test_gioi_han_sai_uuid_khong_thay_va_method(self):
        for value in ('0', '51', '-1', 'true', '1.0'):
            self.assertEqual(self.call('?gioi_han='+value)['status'], 422)
        self.assertEqual(self.call('?cot_la=x')['status'], 422)
        self.assertEqual(self.call('/sai')['status'], 422)
        self.assertEqual(self.call('/'+str(uuid4()))['status'], 404)
        self.assertEqual(self.call('/function', 'DELETE')['status'], 405)

    def test_tran_luot_dang_cho_chay_bao_ro_can_cho_hoan_tat(self):
        original = self.conn.execute

        def execute(sql, args=None):
            if 'loi.ai_chay_thu_xep(' in sql:
                raise sql_error('AI_THU_GIOI_HAN', '54000')
            return original(sql, args)

        with patch.object(self.conn, 'execute', side_effect=execute):
            result = self.post()
        self.assertEqual(result['status'], 409)
        self.assertEqual(result['body']['thong_diep'],
            'Đang có quá nhiều lượt chạy thử chưa xong, chờ các lượt trước hoàn tất')

    def test_khac_phap_nhan_khong_doc_duoc_luot(self):
        identity = self.post()['body']['ma_luot']
        result = self.call('/'+identity, headers={'X-Phap-Nhan-Id': str(uuid4())})
        self.assertEqual(result['status'], 404)

    def test_commit_loi_khong_tra_202_khong_giu_dong_mo_coi(self):
        self.conn.fail_commit = True
        self.assertEqual(self.post()['status'], 503)
        self.assertFalse(self.conn.rows)
        self.assertFalse(self.conn.jobs)
        self.assertEqual(self.conn.events, ['rollback'])

    def test_provider_loi_khong_phan_chieu_duong_dan(self):
        self.catalog.side_effect = RuntimeError(SECRET)
        self.assertEqual(self.call('/function')['status'], 503)


class EngineChayThuTests(unittest.TestCase):
    def setUp(self):
        self.conn = KhoGia()
        self.identity = str(uuid4())
        self.conn.rows[self.identity] = dict(id=self.identity, ma_module='mau_demo', ma_function='thanh_toan',
            dau_vao=dict(tai_lieu=TAI_LIEU, cau_hoi=BODY['cau_hoi'], **{key: FUNCTION[key]
                for key in ('phien_ban_module','ma_bam_goi','ma_prompt','phien_ban_prompt')}),
            trang_thai='dang_cho', bat_dau=None)
        self.conn.fail_finish = False
        self.conn.jobs[self.identity] = 'DANG_CHAY'
        self.giu = viec.GiuViec(uuid4(), uuid4(), uuid4(), g18.PN, 'core', 'CORE:DU_LIEU:LAP',
            uuid4(), 1, datetime.now(timezone.utc)+timedelta(minutes=5), phien.MaBiMat('x'*43))
        self.prompt = self.enterContext(patch('kho_tri_thuc.core.ho_so_module.doc_hoi_ai',
            return_value=('a'*64, dict(chi_dan='Trả lời theo hợp đồng DEMO.',
                ma_function='thanh_toan', ma_prompt='thanh_toan', phien_ban_prompt='1'))))
        self.enterContext(patch('socket.socket', side_effect=AssertionError('Không mở mạng')))
        self.local = Mock(return_value=json.dumps(dict(truong=[dict(ten='tra_loi', gia_tri='1.000.000 đồng',
            trich_dan=TAI_LIEU)], do_tin_cay=0.99), ensure_ascii=False))
        self.cloud, self.mask = Mock(), Mock()
        self.log = ca.BoGhiBoNho()
        self.portal = ca.CongAI(dict(local_ai=dict(enabled=True, model='local-DEMO',
            url='http://127.0.0.1:1234/v1/chat/completions'), cong_ai=dict(cloud_bat=True),
            model_phat_hien=[dict(id_model='local-DEMO', trang_thai='san_sang', bat=True)],
            quy_tac_model=[dict(module='mau_demo', function='thanh_toan', bat=True,
                uu_tien='local-DEMO', du_phong=[], che_do='tu_chon')]),
            bo_ghi=self.log, local_transport=self.local, nha_cung_cap=self.cloud, mask=self.mask, moi_truong={})
        self.enterContext(patch.dict(ca.ai_cuc_bo._CONNECTION_FAILURES, {}, clear=True))
        self.enterContext(patch.object(ca.ai_cuc_bo, 'discover_local_models', return_value=dict(
            ma_loi='', model_phat_hien=[dict(id_model='local-DEMO', trang_thai='san_sang')])))

        pin = e2.pin_demo(capability='ai.hoi@1', ma_engine='e_hoi_ai',
            dau_vao=dv.GhimContract('hoi_ai.v2', '2.0.0', 'b'*64),
            dau_ra=dv.GhimContract('tra_loi_ai.v2', '2.0.0', 'c'*64))
        self.binding = e2.binding_demo(pin, module='core', loai='CHAY_THU_HOI_AI')
        self.service = dv.DichVuEngine([pin], loai_viec=[self.binding],
            ho_so_runtime=Mock(), doc_kt=Mock(), doc_hoi_ai=self.prompt)
        self.enterContext(patch.object(self.service, '_doi_chieu'))
        self.enterContext(patch.object(dv.dang_ky, 'doc_dang_ky', return_value=[dict(
            module='mau_demo', so_phien_ban='1.0.0', trang_thai='da_cai', ma_bam_goi='a'*64)]))
        self.enterContext(patch.object(viec, 'trang_thai_lease',
            return_value=dict(con_giu=True, lan_thu_id=str(self.giu.lan_thu_id))))
        self.receive = self.enterContext(patch.object(self.service, 'nhan_viec', return_value=self.giu))
        self.input = Mock(side_effect=AssertionError('Không cấp đầu vào module cho việc Core'))
        self.hang = ke.HangViecCore(ctx=dict(ma=self.giu.ma, module='core',
            phap_nhan_id=g18.PN, hanh_dong='CORE:DU_LIEU:LAP'), dau_vao=self.input,
            ban_giao=Mock(), ghim_loai_viec=self.binding, dich_vu_engine=self.service)
        self.worker = object.__new__(ke.WorkerEngine)
        self.worker._hang, self.worker._lease = self.hang, None
        self.worker._ket_noi = lambda: nullcontext(self.conn)
        self.worker._song, self.worker._dong = lambda: True, False
        self.worker._ai_thu_ack = self.worker._hoi_ai_dau_vao = self.worker._ket_qua = None
        self.worker._drain = False
        self.worker._instance = self.giu.instance_id
        self.worker._binding = dict(contract_id='tra_loi_ai.v2')
        outer = self

        class KenhGia(KenhCore):
            def goi(self, operation, giu_viec, **payload):
                content = payload.pop('luong', None)
                header = dict(module='core', phap_nhan_id=str(g18.PN), hanh_dong='CORE:DU_LIEU:LAP',
                    request_id=str(uuid4()), stream=dict(ten=payload.get('ten')))
                result, stream, after = outer.worker._thuc_thi(operation, payload, content,
                    header, time.monotonic()+30, None)
                if after is not None:
                    after()
                return result
        self.kenh = KenhGia()
        self.sdk = SDKEngine(self.kenh.goi('nhan_viec', None) and self.giu, kenh_core=self.kenh)

    def tearDown(self):
        self.cloud.tra_loi.assert_not_called()
        self.mask.che.assert_not_called()
        self.input.assert_not_called()
        self.hang.ban_giao.ghi.assert_not_called()

    def run_worker(self):
        return ai.xu_ly_viec(self.sdk, provider=self.portal, kiem_schema=d.KiemSchema().kiem)

    def test_engine_doc_hoi_v2_prompt_da_cai_cau_hoi_trong_du_lieu_va_ghi_cung_tx(self):
        def local(*args, **kw):
            self.assertEqual(self.conn.info.transaction_status, 0)
            return self.local.return_value
        self.local.side_effect = local
        result = self.run_worker()
        self.assertTrue(result['da_ban_giao'])
        self.assertEqual(result['ket_qua_id'], self.identity)
        row = self.conn.rows[self.identity]
        self.assertIn('1.000.000 đồng', row['ket_qua']['tra_loi'])
        self.assertEqual(row['ket_qua']['model'], 'local-DEMO')
        self.assertEqual(row['ket_qua']['ly_do_chon'], 'uu_tien')
        self.assertEqual(self.conn.jobs[self.identity], 'XONG')
        self.assertEqual(self.receive.call_args.args[1], 'ai.hoi@1')
        payload = json.loads(self.local.call_args.args[1])
        self.assertIn(BODY['cau_hoi'], payload['messages'][1]['content'])
        self.assertNotIn(BODY['cau_hoi'], payload['messages'][0]['content'])
        self.assertEqual(self.log.ban_ghi[-1].ma_function, 'thanh_toan')
        self.assertEqual(self.log.ban_ghi[-1].ma_module, 'mau_demo')
        self.assertEqual(self.log.ban_ghi[-1].loai_viec, 'CHAY_THU')

    def test_chon_model_du_phong_ghi_dung_thu_tu_thuc_te(self):
        cfg = self.portal.cau_hinh_model
        cfg['model_phat_hien'] = [dict(id_model='du-phong-DEMO', bat=True, trang_thai='san_sang')]
        cfg['quy_tac_model'][0]['du_phong'] = ['chua-san-sang-DEMO', 'du-phong-DEMO']
        with patch.object(ca.ai_cuc_bo, 'discover_local_models', return_value=dict(
                ma_loi='', model_phat_hien=deepcopy(cfg['model_phat_hien']))):
            self.run_worker()
        result = self.conn.rows[self.identity]['ket_qua']
        self.assertEqual((result['model'], result['ly_do_chon']), ('du-phong-DEMO', 'du_phong:2'))
        self.assertEqual(self.log.ban_ghi[-1].ly_do_chon_model, result['ly_do_chon'])

    def test_chon_model_co_dinh_ghi_dung_ly_do(self):
        self.portal.cau_hinh_model['quy_tac_model'][0]['che_do'] = 'co_dinh'
        self.run_worker()
        self.assertEqual(self.conn.rows[self.identity]['ket_qua']['ly_do_chon'], 'co_dinh')
        self.assertEqual(self.log.ban_ghi[-1].ly_do_chon_model, 'co_dinh')

    def test_ack_sau_commit_phat_lai_khong_goi_ai_va_ket_thuc_lease(self):
        ack = self.run_worker()
        self.assertEqual(self.conn.events[-1], 'commit')
        before = len(self.conn.calls)
        data = self.worker._ai_thu_ack
        self.assertIsNotNone(data)
        self.assertTrue(self.kenh.goi('ket_thuc', self.giu, trang_thai='XONG',
            ket_qua_id=ack['ket_qua_id'], ma_loi=None))
        self.assertEqual(len(self.conn.calls), before)
        self.assertIsNone(self.worker._lease)
        self.assertIsNone(self.worker._ai_thu_ack)
        self.local.assert_called_once()

    def test_ack_cu_khong_cho_ket_thuc_voi_ma_khac(self):
        self.run_worker()
        with self.assertRaises(ke.k.LoiKenh):
            self.kenh.goi('ket_thuc', self.giu, trang_thai='XONG', ket_qua_id=str(uuid4()), ma_loi=None)

    def test_ket_thuc_loi_rollback_ca_ket_qua_va_khong_ack(self):
        self.sdk.doc_dau_vao()
        out = ai._hoi_v2(self.sdk.doc_dau_vao(), provider=self.portal, kiem_schema=d.KiemSchema().kiem)
        self.conn.fail_finish = True
        inp = self.sdk.doc_dau_vao()
        with self.assertRaises(ke.LoiEngine):
            self.sdk.ghi_ket_qua(luong=io.BytesIO(json.dumps(out).encode('utf-8')), ten='tra-loi-ai.json',
                du_lieu=inp['du_lieu_ket_qua'], revision_tep_truoc=0)
        self.assertNotIn('ket_qua', self.conn.rows[self.identity])
        self.assertEqual(self.conn.jobs[self.identity], 'DANG_CHAY')
        self.assertEqual(self.conn.events[-1], 'rollback')
        self.assertIsNone(self.worker._ai_thu_ack)

    def test_core_tu_choi_trich_dan_ngoai_tai_lieu_va_rong(self):
        inp = self.sdk.doc_dau_vao()
        out = ai._hoi_v2(inp, provider=self.portal, kiem_schema=d.KiemSchema().kiem)
        for forged in ('Nội dung không có trong hợp đồng DEMO', ' \n\t'):
            with self.subTest(trich_dan=forged):
                invalid = deepcopy(out)
                invalid['truong'][0]['dan_chung'][0]['trich_dan'] = forged
                with self.assertRaises(ke.LoiEngine):
                    self.sdk.ghi_ket_qua(luong=io.BytesIO(json.dumps(invalid).encode('utf-8')),
                        ten='tra-loi-ai.json', du_lieu=inp['du_lieu_ket_qua'], revision_tep_truoc=0)
                self.assertNotIn('ket_qua', self.conn.rows[self.identity])
                self.assertIsNone(self.worker._ai_thu_ack)

    def test_mat_lease_truoc_doc_khong_doc_prompt_khong_goi_ai(self):
        self.conn.worker_error = sql_error('VIEC_MAT_LEASE', '40001')
        with self.assertRaises(ke.LoiEngine):
            self.sdk.doc_dau_vao()
        self.prompt.assert_not_called()
        self.local.assert_not_called()

    def test_goi_da_thay_bam_bi_chan_truoc_model(self):
        self.prompt.return_value = ('b'*64, self.prompt.return_value[1])
        with self.assertRaises(ke.LoiEngine):
            self.sdk.doc_dau_vao()
        self.local.assert_not_called()

    def test_local_loi_khong_cloud_va_loi_viet(self):
        self.local.side_effect = RuntimeError(SECRET)
        self.run_worker()
        result = self.conn.rows[self.identity]['ket_qua']
        self.assertEqual(result['loi']['ma_ho_tro'], 'AI_THU_LOCAL')
        self.assertEqual(result['ly_do_chon'], 'uu_tien')
        self.assertNotIn(SECRET, repr(result))
        self.assertEqual(self.conn.jobs[self.identity], 'LOI')

    def test_khong_can_cu_la_ket_qua_hop_le(self):
        self.local.return_value = json.dumps(dict(truong=[], do_tin_cay=0.99))
        with patch.object(self.worker, '_ghi_chay_thu', wraps=self.worker._ghi_chay_thu) as ghi:
            self.run_worker()
        out = ghi.call_args.args[2]
        self.assertEqual(out['ly_do'], ['KHONG_THAY_CAN_CU'])
        self.assertTrue(d.KiemSchema().kiem({'$ref': 'urn:ktt:contract:tra_loi_ai.v2'}, out))
        row = self.conn.rows[self.identity]
        self.assertEqual(row['trang_thai'], 'xong')
        self.assertEqual(row['ket_qua']['tra_loi'], 'Không thấy căn cứ trong tài liệu.')
        self.assertEqual(row['ket_qua']['model'], 'local-DEMO')
        # Vòng 6: Core chưa đọc được nhật ký provenance; contract đã duyệt chỉ
        # cho KHONG_THAY_CAN_CU. Để rỗng cho màn hiện “—”, không suy lý do chọn.
        self.assertEqual(row['ket_qua']['ly_do_chon'], '')
        self.assertIsNone(row['ket_qua']['loi'])
        record = self.log.ban_ghi[-1]
        self.assertEqual(record.ma_yeu_cau, out['ma_yeu_cau_nguon'])
        self.assertEqual(record.viec_id, str(self.giu.viec_id))
        self.assertEqual((record.model, record.ly_do_chon_model), ('local-DEMO', 'uu_tien'))

    def test_model_trich_lai_cau_hoi_bi_tu_choi_khong_ghi_ket_qua(self):
        self.local.return_value = json.dumps(dict(truong=[dict(ten='tra_loi',
            gia_tri=BODY['cau_hoi'], trich_dan=BODY['cau_hoi'])], do_tin_cay=0.99),
            ensure_ascii=False)
        inp = self.sdk.doc_dau_vao()
        out = ai._hoi_v2(inp, provider=self.portal, kiem_schema=d.KiemSchema().kiem)
        self.assertEqual(out['truong'][0]['dan_chung'][0]['trich_dan'], BODY['cau_hoi'])
        with self.assertRaises(ke.LoiEngine):
            self.sdk.ghi_ket_qua(luong=io.BytesIO(json.dumps(out).encode('utf-8')),
                ten='tra-loi-ai.json', du_lieu=inp['du_lieu_ket_qua'], revision_tep_truoc=0)
        self.assertNotIn('ket_qua', self.conn.rows[self.identity])
        self.assertEqual(self.conn.jobs[self.identity], 'DANG_CHAY')
        self.assertEqual(self.conn.events[-1], 'rollback')
        self.assertIsNone(self.worker._ai_thu_ack)

    def test_core_khong_con_duong_goi_ai_truc_tiep(self):
        for name in ('chay_thu_hoi_ai', 'chay_mot_hoi_ai_thu'):
            self.assertFalse(hasattr(ke, name))
        self.assertFalse(hasattr(viec, 'nhan_chay_thu_hoi_ai'))

    def test_nhan_engine_core_truyen_du_binding_va_chan_loai_khac(self):
        conn = Mock()
        conn.info.transaction_status = 2
        conn.execute.return_value.fetchone.return_value = (None,)
        ctx = dict(ma=self.giu.ma, module='core', phap_nhan_id=g18.PN, hanh_dong='CORE:DU_LIEU:LAP')
        self.assertIsNone(viec.nhan_engine(conn, self.giu.instance_id, ghim_loai_viec=self.binding, **ctx))
        self.assertIn('loi.nhan_viec_engine(', conn.execute.call_args.args[0])
        self.assertEqual(conn.execute.call_args.args[1][-4:],
            ('ai.hoi@1', self.binding.engine_id, 'tra_loi_ai.v2', '2.0.0'))
        with self.assertRaises(ValueError):
            viec.nhan_engine(conn, self.giu.instance_id,
                ghim_loai_viec=replace(self.binding, loai='XUAT_DU_LIEU'), **ctx)

    @contextmanager
    def wire(self):
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from tests.test_g2_32_e1 import SocketGia
        k = ke.k
        a, b = SocketGia(), SocketGia()
        a.peer, b.peer = b, a
        b.kiem_tx = lambda: self.assertEqual(self.conn.info.transaction_status, 0)
        key = Ed25519PrivateKey.generate()
        bind = dict(issuer='core', core_epoch='DEMO', instance_id=str(self.giu.instance_id),
                    the_he=1, nonce_khoi_dong='n'*43, module='core')
        header = dict(bind, pham_vi='phap_nhan', phap_nhan_id=str(g18.PN),
            nguoi_dung_id=str(g18.USER), hanh_dong='CORE:DU_LIEU:LAP',
            contract_id='tra_loi_ai.v2', phien_ban_contract='2.0.0', ma_bam_schema='a'*64)
        checker = lambda: k.BoKiemThe(key.public_key(), **bind)
        secret, cid = b'CANARY_CREDENTIAL'*3, str(uuid4())
        client = ke.KenhCore(a, proof=k.BoProof(secret, cid, vai='con', loai_con='engine'),
            kiem_the=checker(), ngu_canh=header)
        worker = ke.WorkerEngine(b, proof=k.BoProof(secret, cid, vai='core', loai_con='engine'),
            kiem_the=checker(), khoa_rieng=key, kiem_instance=lambda: True,
            ket_noi=lambda: nullcontext(self.conn), hang_viec=self.hang, kho_tep=Mock(),
            instance_id=self.giu.instance_id, thu_hoi=Mock(), ngu_canh=header)
        thread = threading.Thread(target=worker.phuc_vu, daemon=True)
        thread.start()
        try:
            yield client, worker
        finally:
            client.dong()
            worker.crash()
            thread.join(2)
        self.assertFalse(thread.is_alive())

    def test_wire_engine_nhan_hoi_v2_stream_ack_phat_lai_va_ket_thuc(self):
        with self.wire() as (client, worker):
            lease = client.nhan_viec()
            sdk = SDKEngine(lease, kenh_core=client)
            inp = sdk.doc_dau_vao()
            with patch.object(worker, '_ghi_chay_thu', wraps=worker._ghi_chay_thu) as ghi:
                ack = ai.xu_ly_viec(sdk, provider=self.portal, kiem_schema=d.KiemSchema().kiem)
            out = ghi.call_args.args[2]
            raw = json.dumps(out, ensure_ascii=False, allow_nan=False).encode('utf-8')
            before = len(self.conn.calls)
            replay = sdk.ghi_ket_qua(luong=io.BytesIO(raw), ten='tra-loi-ai.json',
                du_lieu=inp['du_lieu_ket_qua'], revision_tep_truoc=0)
            self.assertEqual(replay, ack)
            self.assertEqual(len(self.conn.calls), before)
            self.assertTrue(client.ket_thuc(lease, ket_qua_id=ack['ket_qua_id']))
            self.assertIsNone(worker._lease)
        self.local.assert_called_once()

    def test_wire_tai_lieu_va_cau_hoi_nhieu_dong_chuan_hoa_crlf(self):
        text = 'Hợp đồng DEMO.\r\n\tThanh toán 1.000.000 đồng.\n Câu hỏi: Điều kiện DEMO.'
        question = 'Số tiền thanh toán?\r\n\t Câu hỏi: Điều kiện thanh toán?'
        self.conn.rows[self.identity]['dau_vao'].update(tai_lieu=text, cau_hoi=question)
        normalized = text.replace('\r\n', '\n')
        self.local.return_value = json.dumps(dict(truong=[dict(ten='tra_loi',
            gia_tri='1.000.000 đồng', trich_dan=normalized)], do_tin_cay=0.99), ensure_ascii=False)
        with self.wire() as (client, worker):
            lease = client.nhan_viec()
            sdk = SDKEngine(lease, kenh_core=client)
            inp = sdk.doc_dau_vao()
            self.assertIn(normalized, inp['yeu_cau']['van_ban'])
            self.assertIn(question.replace('\r\n', '\n'), inp['yeu_cau']['van_ban'])
            self.assertNotIn('\r', inp['yeu_cau']['van_ban'])
            out = ai._hoi_v2(inp, provider=self.portal, kiem_schema=d.KiemSchema().kiem)
            ack = sdk.ghi_ket_qua(luong=io.BytesIO(json.dumps(out, ensure_ascii=False).encode('utf-8')),
                ten='tra-loi-ai.json', du_lieu=inp['du_lieu_ket_qua'], revision_tep_truoc=0)
            self.assertTrue(client.ket_thuc(lease, ket_qua_id=ack['ket_qua_id']))
        result = self.conn.rows[self.identity]['ket_qua']
        self.assertEqual(self.conn.jobs[self.identity], 'XONG')
        self.assertIn(' '.join(normalized.split()), result['tra_loi'])
        self.assertEqual(result['ly_do_chon'], 'uu_tien')

    def test_cau_tra_loi_duoc_cat_truoc_luu(self):
        text = 'ệ'*12000
        self.conn.rows[self.identity]['dau_vao']['tai_lieu'] = text
        self.local.return_value = json.dumps(dict(truong=[dict(ten='tra_loi', gia_tri=text,
            trich_dan=text)], do_tin_cay=0.99), ensure_ascii=False)
        self.run_worker()
        self.assertEqual(len(self.conn.rows[self.identity]['ket_qua']['tra_loi']), 20000)

    def test_engine_bao_loi_ket_thuc_ghi_loi_viet_cung_viec(self):
        self.assertTrue(self.kenh.goi('ket_thuc', self.giu,
            trang_thai='LOI', ket_qua_id=None, ma_loi='AI_XU_LY_LOI'))
        self.assertEqual(self.conn.jobs[self.identity], 'LOI')
        self.assertEqual(self.conn.rows[self.identity]['ket_qua']['loi']['ma_ho_tro'], 'AI_THU_XU_LY')


class ProviderGoiTests(unittest.TestCase):
    def setUp(self):
        # Mỗi fixture dùng Mock kết nối mới; id(conn) có thể được Python dùng
        # lại. Tách cache giữa các ca, vẫn kiểm cache/thế hệ ngay trong từng ca.
        self.enterContext(patch.dict(ke._FUNCTION_CACHE, {}, clear=True))
        from tests.test_ai_ham_khai import HamHoiAIKhaiTests
        self.fixture = HamHoiAIKhaiTests(methodName='runTest')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def test_catalog_doc_goi_da_cai_sha_khong_launch_backend(self):
        f = self.fixture
        result = ke.doc_function_chay_thu_hoi_ai(f.conn)
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['ma_bam_goi'],f.bam)
        self.assertEqual(result[0]['phien_ban_prompt'],'1')
        self.assertEqual(result[0]['ma_function'],'trich_hop_dong')
        self.assertNotIn('chi_dan',result[0])
        self.assertNotIn(str(f.root),repr(result))

    def test_sua_bytes_prompt_sau_cai_bi_chan(self):
        from kho_tri_thuc.core.goi import LoiGoi
        f = self.fixture
        (f.folder/'prompt/trich_tien.txt').write_bytes('Prompt đã bị đổi'.encode('utf-8'))
        with self.assertLogs(ke.__name__, level='WARNING'):
            self.assertEqual(ke.doc_function_chay_thu_hoi_ai(f.conn), [])

    def test_khong_co_khai_bao_khong_tu_tao_prompt_mac_dinh(self):
        f = self.fixture
        f.manifest['ham_hoi_ai'] = []
        f.cai()
        self.assertEqual(ke.doc_function_chay_thu_hoi_ai(f.conn),[])

    def test_hai_ban_da_cai_cung_function_bi_chan_khong_tu_chon(self):
        f = self.fixture
        f.rows *= 2
        with self.assertLogs(ke.__name__, level='WARNING'):
            self.assertEqual(ke.doc_function_chay_thu_hoi_ai(f.conn), [])

    def test_cache_the_he_cai_lai_va_tra_ban_sao(self):
        f = self.fixture
        first = ke.doc_function_chay_thu_hoi_ai(f.conn)
        count = f.conn.execute.call_count
        first[0]['ten_function'] = 'Đã đổi bản sao'
        self.assertNotEqual(ke.doc_function_chay_thu_hoi_ai(f.conn), first)
        self.assertEqual(f.conn.execute.call_count, count)
        f.rows[0]['the_he'] = 2
        ke.doc_function_chay_thu_hoi_ai(f.conn)
        self.assertGreater(f.conn.execute.call_count, count)

    def test_prompt_loi_va_trung_chi_bo_muc_loi_giu_chuc_nang_khac(self):
        from kho_tri_thuc.core import ho_so_module
        f = self.fixture
        package = SimpleNamespace(manifest=dict(ten='Nghiệp vụ DEMO', ham_hoi_ai=[
            dict(ma_function=name, ma_prompt=name, phien_ban_prompt=1, tep_prompt=name)
            for name in ('tot', 'trang', 'trung', 'trung')]),
            cac_tep={'tot': b'DEMO', 'trang': b' ', 'trung': b'DEMO'})
        with patch.object(ho_so_module, '_doc_goi_da_cai', return_value=(None,package)), \
                self.assertLogs(ke.__name__, level='WARNING') as logs:
            self.assertEqual([r['ma_function'] for r in ke.doc_function_chay_thu_hoi_ai(f.conn)], ['tot'])
        self.assertNotIn(str(f.root), repr(logs.output))


if __name__ == '__main__':
    unittest.main()
