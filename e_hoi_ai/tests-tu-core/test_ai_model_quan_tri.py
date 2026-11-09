"""AI-MAN: factory/WSGI thật, hồ sơ CAS và máy AI giả; không mạng/PG."""
from contextlib import contextmanager, nullcontext
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from kho_tri_thuc.core import dispatcher as d, ho_so_chay as hs, http, routes_quan_tri as r, ung_dung as u
import test_emcfg_http as cfg

PATH = '/api/v1/quan-tri/engine/e_hoi_ai/local'
ADDRESS = 'http://192.168.90.123:11434'
SECRET = 'sk-DEMO_CANARY_AI_MAN_123456789'


def model(ma='qwen-demo', ten='Qwen thử nghiệm', bat=True, trang_thai='san_sang'):
    return dict(ma=ma, ten=ten, bat=bat, trang_thai=trang_thai)


def rule():
    return dict(chuc_nang='hoi_dap', ten='Hỏi đáp tài liệu', che_do='tu_chon',
                uu_tien='qwen-demo', du_phong=None)


def stored_model(*args, **kwargs):
    row = model(*args, **kwargs)
    return dict(id_model=row['ma'], ten=row['ten'], bat=row['bat'],
        trang_thai={'san_sang': 'san_sang', 'moi': 'da_tai', 'khong_con': 'chua_ro'}[row['trang_thai']],
        loai_phan_mem='openai_compatible', phat_hien_luc='2026-11-07T01:00:00Z')


def stored_rule(value=None):
    row = rule() if value is None else value
    return dict(module='*', function=row['chuc_nang'], ten=row['ten'], bat=True,
        che_do=row['che_do'], uu_tien=row['uu_tien'] or '',
        du_phong=[row['du_phong']] if row['du_phong'] else [])


def metadata():
    manifest = json.loads((Path(__file__).resolve().parents[1] /
        'engines/e_hoi_ai/engine.json').read_text(encoding='utf-8'))
    schema = manifest['cau_hinh_schema']
    return dict(phien_ban_engine=manifest['phien_ban'],
        ma_bam_schema=hashlib.sha256(hs._json(schema).encode('utf-8')).hexdigest(),
        cau_hinh_schema=schema)


class KhoGia:
    def __init__(self):
        self.meta = metadata()
        self.profile = cfg.base.ho_so(phien_ban_engine=self.meta['phien_ban_engine'],
            ma_bam_schema=self.meta['ma_bam_schema'], cau_hinh=dict(
                model_phat_hien=[stored_model()], quy_tac_model=[stored_rule()],
                local_ai=dict(enabled=True, url=ADDRESS + '/v1/chat/completions', ket_noi=True,
                    kiem_luc='2026-11-07T01:00:00Z', do_tre_ms=12)))
        self.info = SimpleNamespace(transaction_status=0)
        self.admin = True
        self.has_schema = True
        self.race = self.commit_error = False
        self.calls, self.receipts, self.events = [], {}, []

    @contextmanager
    def transaction(self):
        before = deepcopy((self.profile, self.receipts))
        self.info.transaction_status = 2
        try:
            yield
            if self.commit_error:
                raise RuntimeError(SECRET)
        except Exception:
            self.profile, self.receipts = before
            self.events.append('rollback')
            raise
        else:
            self.events.append('commit')
        finally:
            self.info.transaction_status = 0

    def execute(self, sql, args):
        assert self.info.transaction_status == 2
        assert sql.startswith('SELECT loi.ho_so_chay_'), sql
        assert args[:2] == ('e_hoi_ai', 'DEMO_EMCFG_HTTP')
        self.calls.append((sql, args))
        if not self.admin:
            raise hs.LoiHoSoChay('HO_SO_CHAY_CHI_ADMIN')
        name = sql.split('loi.')[1].split('(')[0]
        if name == 'ho_so_chay_doc':
            if not self.has_schema:
                raise hs.LoiHoSoChay('CAU_HINH_CHUA_KHAI_BAO')
            result = self.profile if args[2] else {k: self.profile[k] for k in hs._CU}
        elif name == 'ho_so_chay_doc_schema':
            result = self.meta
        elif name == 'ho_so_chay_phat_lai':
            result = self.receipts.get(args[-1])
        elif name == 'ho_so_chay_ghi':
            data = json.loads(args[3])
            if self.race or data['row_version'] != self.profile['row_version']:
                raise hs.LoiHoSoChay('XUNG_DOT_PHIEN_BAN')
            self.profile = deepcopy(data)
            self.profile['row_version'] = str(int(data['row_version']) + 1)
            result = self.receipts[args[-1]] = deepcopy(self.profile)
        else:
            raise AssertionError(sql)
        return SimpleNamespace(fetchone=lambda: (deepcopy(result),))


class AILocalHTTPTests(unittest.TestCase):
    def setUp(self):
        self.conn = KhoGia()
        self.ma = d.phien.MaBiMat('DEMO_EMCFG_HTTP')
        self.session = http.PhienHTTP(cfg.web.g18.USER, d.phien.MaBiMat('CSRF_CANARY'),
            Mock(return_value=self.ma), cfg.web.g18.NOW, cfg.web.g18.NOW)
        self.sessions = Mock(side_effect=lambda sid: self.session)
        self.connect = Mock(side_effect=lambda **kw: nullcontext(self.conn))
        self.enterContext(patch.object(u, 'nap_cau_hinh', return_value=cfg.web.CONFIG))
        if not cfg.CO_SCHEMA:
            self.enterContext(patch.object(hs.goi, '_bo_schema', return_value=(cfg._ValidatorTest, None, None, None)))
        self.app = u.tao_ung_dung('CAU_HINH_GIA_KHONG_DOC', ket_noi=self.connect,
            doc_phien=self.sessions, doc_kt=Mock(side_effect=AssertionError('Không gọi engine')),
            kiem=d.KiemSchema() if cfg.CO_SCHEMA else cfg.web.g18.KiemTest(),
            dong_ho=lambda: cfg.web.g18.NOW)
        self.count = 0

    def call(self, path=PATH, method='GET', body=None, headers=None):
        self.count += 1
        response = cfg.web.wsgi(self.app, path, method, body=body,
            headers={'X-Phap-Nhan-Id': None, 'Idempotency-Key': 'demo-ai-man-%016d' % self.count,
                     **(headers or {})})
        raw = repr(response)
        for secret in (ADDRESS, '192.168.90.123', SECRET, 'DEMO_EMCFG_HTTP', 'CSRF_CANARY', cfg.base.REF):
            self.assertNotIn(secret, raw)
        self.assertEqual(response['headers']['Cache-Control'], 'no-store')
        return response

    def service(self, **extra):
        service = Mock(return_value=dict(ket_noi=True, do_tre_ms=8,
            models=[dict(ma='qwen-demo', ten='Qwen thử nghiệm'),
                    dict(ma='moi-demo', ten='Mô hình mới')], **extra))
        r.dang_ky_ai_local(self.app, dich_vu=service)
        return service

    def detect(self, version='1', headers=None):
        return self.call(PATH + '/phat-hien', 'POST', {'row_version': version}, headers)

    def save(self, body=None, version='1', headers=None):
        return self.call(PATH + '/quy-tac', 'PUT', body if body is not None else
            dict(row_version=version, quy_tac_model=[rule()], models=[dict(ma='qwen-demo', bat=True)]), headers)

    def test_factory_dang_ky_that_khong_mo_ket_noi_khi_dung(self):
        self.connect.assert_not_called()
        route, _ = self.app.http.dispatcher.registry.tra('GET', PATH)
        self.assertEqual(route.hanh_dong, 'CORE:ENGINE:CAU_HINH')
        self.assertEqual(route.pham_vi, 'he_thong')
        result = self.call()
        self.assertEqual(result['status'], 200, result)
        self.assertEqual(result['body']['dia_chi_che'], 'Máy AI (đã che)')
        self.assertEqual(result['body']['models'], [model()])
        self.assertEqual(result['body']['quy_tac'], [rule()])

    def test_khong_admin_403_truoc_dich_vu_ca_khi_khong_callback(self):
        service = self.service()
        self.conn.admin = False
        for result in (self.call(), self.detect(), self.save()):
            self.assertEqual(result['status'], 403, result)
            self.assertIn('Chỉ Admin', result['body']['thong_diep'])
        service.assert_not_called()

    def test_callback_la_chot_bo_sung(self):
        self.app.http.dispatcher.core.quyen_he_thong = Mock(return_value=False)
        self.assertEqual(self.call()['status'], 403)
        self.assertEqual(self.save()['status'], 403)
        self.assertEqual(self.conn.calls, [])

    def test_thieu_sai_csrf_origin_va_phien_deu_chan_truoc_dich_vu(self):
        service = self.service()
        for headers in ({'X-CSRF-Token': None}, {'X-CSRF-Token': 'sai'},
                        {'Origin': 'http://khac.invalid'}):
            self.assertEqual(self.detect(headers=headers)['status'], 403)
            self.assertEqual(self.save(headers=headers)['status'], 403)
        self.session = None
        self.assertEqual(self.call()['status'], 401)
        # HTTP chặn ghi không có phiên ngay tại cửa kiểm CSRF.
        self.assertEqual(self.save()['status'], 403)
        service.assert_not_called()
        self.assertEqual(self.conn.calls, [])

    def test_dich_vu_none_tra_cau_viet_khong_ghi(self):
        before = deepcopy(self.conn.profile)
        result = self.detect()
        self.assertEqual(result['status'], 200, result)
        self.assertEqual(result['body']['thong_diep'], 'Chưa kết nối máy AI cục bộ')
        self.assertFalse(result['body']['ket_noi'])
        self.assertEqual(self.conn.profile, before)

    def test_chua_co_schema_van_co_trang_thai_none_khong_tao_cas_gia(self):
        service = self.service()
        self.conn.has_schema = False
        for result in (self.call(), self.detect()):
            self.assertEqual(result['status'], 200, result)
            self.assertIsNone(result['body']['row_version'])
            self.assertFalse(result['body']['da_cau_hinh'])
            self.assertEqual(result['body']['thong_diep'], 'Chưa kết nối máy AI cục bộ')
        service.assert_not_called()
        self.assertEqual(self.conn.receipts, {})
        self.assertEqual(self.save()['status'], 422)
        self.assertEqual(self.conn.receipts, {})
        self.conn.admin = False
        self.assertEqual(self.call()['status'], 403)

    def test_phat_hien_luu_cas_model_moi_tat_model_mat_giu_lai(self):
        self.conn.profile['cau_hinh']['model_phat_hien'].append(stored_model('cu-demo', 'Mô hình cũ'))
        service = self.service(dia_chi=ADDRESS, api_key=SECRET)
        result = self.detect()
        self.assertEqual(result['status'], 200, result)
        self.assertEqual(result['body']['row_version'], '2')
        rows = {m['ma']: m for m in result['body']['models']}
        self.assertEqual(rows['qwen-demo']['trang_thai'], 'san_sang')
        self.assertEqual(rows['cu-demo']['trang_thai'], 'khong_con')
        self.assertEqual(rows['moi-demo'], model('moi-demo', 'Mô hình mới', False, 'moi'))
        self.assertEqual(service.call_args.kwargs['cau_hinh']['local_ai']['url'], ADDRESS + '/v1/chat/completions')
        self.assertEqual(self.conn.profile['cau_hinh']['quy_tac_model'], [stored_rule()])
        self.assertEqual(self.call()['body'], result['body'])
        self.assertEqual(self.conn.events[-1], 'commit')

    def test_cas_cu_409_truoc_dich_vu_va_race_409_khong_ghi(self):
        service = self.service()
        result = self.detect('2')
        self.assertEqual(result['status'], 409, result)
        self.assertIn('Dữ liệu đã thay đổi', result['body']['thong_diep'])
        service.assert_not_called()
        before = deepcopy(self.conn.profile)
        self.conn.race = True
        result = self.detect()
        self.assertEqual(result['status'], 409, result)
        self.assertEqual(self.conn.profile, before)

    def test_toan_luong_luu_chi_tra_dto_che_giu_dia_chi_cloud_va_ho_so(self):
        service = self.service()
        opened = self.call()
        detected = self.detect(opened['body']['row_version'])
        before = deepcopy(self.conn.profile)
        rules = [dict(rule(), uu_tien=None)]
        result = self.save(dict(row_version=detected['body']['row_version'],
            quy_tac_model=rules, models=[dict(ma='qwen-demo', bat=False), dict(ma='moi-demo', bat=True)]))
        self.assertEqual(result['status'], 200, result)
        self.assertEqual(result['body']['row_version'], '3')
        self.assertEqual(result['body']['dia_chi_che'], 'Máy AI (đã che)')
        self.assertEqual(self.call()['body'], result['body'])
        expected = deepcopy(before)
        expected['row_version'] = '3'
        expected['cau_hinh']['model_phat_hien'][0]['bat'] = False
        expected['cau_hinh']['model_phat_hien'][1].update(bat=True, trang_thai='san_sang')
        expected['cau_hinh']['quy_tac_model'] = [stored_rule(row) for row in rules]
        self.assertEqual(self.conn.profile, expected)
        self.assertEqual(self.conn.profile['cau_hinh']['local_ai']['url'], ADDRESS + '/v1/chat/completions')
        self.assertEqual(self.conn.events[-1], 'commit')
        self.assertEqual(service.call_count, 1, 'Lưu không dò mạng hoặc gọi AI')

    def test_luu_chi_quy_tac_khong_doi_model_va_cas_lon_giu_nguyen_chuoi(self):
        self.conn.profile['row_version'] = '9007199254740993'
        before = deepcopy(self.conn.profile['cau_hinh']['model_phat_hien'])
        result = self.save(dict(row_version='9007199254740993',
            quy_tac_model=[dict(rule(), che_do='co_dinh')]))
        self.assertEqual(result['status'], 200, result)
        self.assertEqual(result['body']['row_version'], '9007199254740994')
        self.assertEqual(self.conn.profile['cau_hinh']['model_phat_hien'], before)

    def test_luu_cas_cu_va_race_409_khong_ghi_khong_lo_dia_chi(self):
        before = deepcopy(self.conn.profile)
        for race in (False, True):
            with self.subTest(race=race):
                self.conn.race = race
                result = self.save(version='1' if race else '2')
                self.assertEqual(result['status'], 409, result)
                self.assertIn('Dữ liệu đã thay đổi', result['body']['thong_diep'])
                self.assertEqual(self.conn.profile, before)
                self.assertEqual(self.conn.receipts, {})

    def test_luu_tu_choi_truong_la_va_dia_chi_o_moi_vi_tri_trong_than(self):
        valid = dict(row_version='1', quy_tac_model=[rule()], models=[dict(ma='qwen-demo', bat=True)])
        bad = [{**valid, field: value} for field, value in (
            ('dia_chi', ADDRESS), ('cau_hinh', {'local_ai': {'dia_chi': ADDRESS}}),
            ('cloud_bat', True), ('truong_la', True))]
        for field in ('dia_chi', 'ten', 'trang_thai'):
            body = deepcopy(valid)
            body['models'][0][field] = ADDRESS
            bad.append(body)
        for field in ('dia_chi', 'chuc_nang', 'ten', 'che_do', 'uu_tien', 'du_phong'):
            body = deepcopy(valid)
            body['quy_tac_model'][0][field] = ADDRESS
            bad.append(body)
        body = deepcopy(valid)
        body['models'][0]['ma'] = ADDRESS
        bad.append(body)
        for field, value in (('models', [dict(ma='qwen-demo', bat='true')]),
                             ('row_version', 1), ('quy_tac_model', [rule()] * 201)):
            bad.append({**valid, field: value})
        before = deepcopy(self.conn.profile)
        for body in bad:
            with self.subTest(body=body):
                self.assertEqual(self.save(body)['status'], 422)
                self.assertEqual(self.conn.profile, before)
                self.assertEqual(self.conn.receipts, {})

    def test_luu_tu_choi_model_la_trung_mat_va_quy_tac_khong_san_sang(self):
        before = deepcopy(self.conn.profile)
        bad = [dict(row_version='1', quy_tac_model=[rule()], models=flags) for flags in (
            [dict(ma='khong-co', bat=True)], [dict(ma='qwen-demo', bat=True)] * 2,
            [dict(ma='qwen-demo', bat=False)])]
        bad.extend(dict(row_version='1', quy_tac_model=rules) for rules in (
            [rule(), rule()], [dict(rule(), che_do='co_dinh', uu_tien=None)],
            [dict(rule(), uu_tien='khong-co')], [dict(rule(), du_phong='khong-co')]))
        for body in bad:
            with self.subTest(body=body):
                self.assertEqual(self.save(body)['status'], 422)
                self.assertEqual(self.conn.profile, before)
                self.assertEqual(self.conn.receipts, {})
        self.conn.profile['cau_hinh']['model_phat_hien'].append(
            stored_model('mat-demo', 'Mô hình đã mất', False, 'khong_con'))
        body = dict(row_version='1', quy_tac_model=[rule()], models=[dict(ma='mat-demo', bat=True)])
        self.assertEqual(self.save(body)['status'], 422)

    def test_luu_giu_model_mat_da_bat_khong_tu_thay_trang_thai(self):
        missing = model('mat-demo', 'Mô hình đã mất', True, 'khong_con')
        self.conn.profile['cau_hinh']['model_phat_hien'].append(
            stored_model('mat-demo', 'Mô hình đã mất', True, 'khong_con'))
        result = self.save(dict(row_version='1', quy_tac_model=[rule()],
            models=[dict(ma='qwen-demo', bat=True), dict(ma='mat-demo', bat=True)]))
        self.assertEqual(result['status'], 200, result)
        self.assertEqual(result['body']['models'][-1], missing)

    def test_luu_commit_loi_rollback_khong_bao_thanh_cong(self):
        before = deepcopy(self.conn.profile)
        self.conn.commit_error = True
        result = self.save()
        self.assertEqual(result['status'], 503, result)
        self.assertEqual(self.conn.profile, before)
        self.assertEqual(self.conn.receipts, {})

    def test_dich_vu_loi_503_khong_lo_bi_mat(self):
        service = self.service()
        service.side_effect = RuntimeError(SECRET + ADDRESS)
        result = self.detect()
        self.assertEqual(result['status'], 503, result)
        self.assertEqual(result['body']['thong_diep'], 'Chưa kết nối máy AI cục bộ')

    def test_ket_noi_hong_khong_ket_luan_model_khong_con(self):
        service = self.service()
        service.return_value = dict(ket_noi=False, models=[], do_tre_ms=None)
        result = self.detect()
        self.assertEqual(result['status'], 200, result)
        self.assertEqual(result['body']['models'], [model()])
        self.assertFalse(result['body']['ket_noi'])

    def test_du_lieu_dich_vu_sai_va_commit_loi_rollback(self):
        service = self.service()
        before = deepcopy(self.conn.profile)
        for bad in (dict(ket_noi=True, models=[dict(ma='x', ten=SECRET)]),
                    dict(ket_noi=True, models=[dict(ma='x', ten=ADDRESS)]),
                    dict(ket_noi=True, models=[], do_tre_ms=float('nan'))):
            service.return_value = bad
            self.assertEqual(self.detect()['status'], 502)
            self.assertEqual(self.conn.profile, before)
        service.return_value = dict(ket_noi=True, models=[], do_tre_ms=0)
        self.conn.commit_error = True
        self.assertEqual(self.detect()['status'], 503)
        self.assertEqual(self.conn.profile, before)

    def test_manifest_that_route_luu_launcher_runtime_dung_model_quy_tac_dia_chi_0_cloud(self):
        import io
        from kho_tri_thuc.engines.e_hoi_ai import chay as ai
        from kho_tri_thuc.engines.e_hoi_ai.lib.cong_ai import CongAI
        from kho_tri_thuc.sdk_core.bootstrap import BiMatBootstrap
        from kho_tri_thuc.sdk_core.engine import SDKEngine
        from test_g3_ai_4a import KenhHoiV2, _lease, VAN_BAN

        result = self.save(dict(row_version='1',
            quy_tac_model=[dict(rule(), chuc_nang='trich_hop_dong')]))
        self.assertEqual(result['status'], 200, result)
        settings = deepcopy(self.conn.profile['cau_hinh'])
        hs._kiem_cau_hinh(self.conn.meta['cau_hinh_schema'], settings)
        self.assertEqual(set(settings), {'local_ai', 'model_phat_hien', 'quy_tac_model'})
        check = d.KiemSchema().kiem
        bootstrap = ai.Bootstrap()
        bootstrap.socket, bootstrap.bo_doc, bootstrap._ra = Mock(), Mock(), io.BytesIO()
        bootstrap.bi_mat = BiMatBootstrap(b'{}')
        bo = Mock()
        bo.da_ban_giao.return_value = True
        local = Mock(return_value=json.dumps(dict(truong=[dict(ten='so_tien',
            gia_tri='1.234.567 đồng', trich_dan=VAN_BAN)], do_tin_cay=.99), ensure_ascii=False))
        discover = dict(ma_loi='', model_phat_hien=[dict(id_model='qwen-demo', trang_thai='san_sang')])
        original = ai.bm.tao_cong_ai
        with patch('socket.socket', side_effect=AssertionError('Không mở mạng')), \
                patch.object(CongAI, '_cloud', side_effect=AssertionError('Không Cloud')) as cloud, \
                patch.object(ai.bm, 'tao_cong_ai', wraps=ai.bm.tao_cong_ai) as tao, \
                patch.object(ai.ai_cuc_bo, 'discover_local_models', return_value=discover), \
                patch.object(ai.Bootstrap, 'bao_san_sang',
                    side_effect=lambda **kw: self.assertTrue(kw['kiem_san_sang']())), \
                patch.object(ai.Bootstrap, 'cho_thu_hoi'), patch.object(ai, '_VongNhan') as vong:
            # Launcher cấp đúng settings của hồ sơ, engine dùng cổng thật và transport giả.
            tao.side_effect = lambda *a, **kw: original(*a, **dict(kw, local_transport=local))
            ai.chay_tu_core(bootstrap=bootstrap, kiem_chu_ky=Mock(), nhan_viec=Mock(),
                settings=settings, bo_ghi=bo, kiem_schema=check)
            provider = vong.call_args.args[2]
            self.assertEqual(provider.local_ai['url'], ADDRESS + '/v1/chat/completions')
            self.assertEqual(provider.cau_hinh_model, {k: settings[k] for k in (
                'model_phat_hien', 'quy_tac_model')})
            lease = _lease()
            channel = KenhHoiV2(lease)
            self.assertEqual(ai.xu_ly_viec(SDKEngine(lease, kenh_core=channel),
                provider=provider, kiem_schema=check), channel.ack)
            self.assertEqual(channel.results[-1]['duong'], 'LOCAL')
            self.assertEqual(json.loads(local.call_args.args[1])['model'], 'qwen-demo')
            self.assertEqual(local.call_args.args[0], ADDRESS + '/v1/chat/completions')
            cloud.assert_not_called()
        self.assertEqual(settings, self.conn.profile['cau_hinh'])

    def test_luu_giu_scope_co_bat_va_nhieu_model_du_phong(self):
        config = self.conn.profile['cau_hinh']
        config['model_phat_hien'].extend(stored_model(code, 'Mô hình dự phòng')
            for code in ('du-phong-1', 'du-phong-2'))
        config['quy_tac_model'][0]['du_phong'] = ['du-phong-1', 'du-phong-2']
        config['quy_tac_model'].append(dict(config['quy_tac_model'][0], module='demo', bat=False))
        before = deepcopy(config)
        opened = self.call()
        self.assertEqual(opened['status'], 200, opened)
        self.assertEqual([row['chuc_nang'] for row in opened['body']['quy_tac']],
                         ['hoi_dap', 'demo:hoi_dap'])
        saved = self.save(dict(row_version='1', quy_tac_model=opened['body']['quy_tac']))
        self.assertEqual(saved['status'], 200, saved)
        self.assertEqual(self.conn.profile['cau_hinh'], before)

    def test_rule_module_wildcard_va_rule_tat_giu_model_da_mat_van_luu_duoc(self):
        config = self.conn.profile['cau_hinh']
        config['model_phat_hien'].append(stored_model('cu-demo', 'Mô hình cũ', False, 'khong_con'))
        config['quy_tac_model'].extend([
            dict(stored_rule(), module='demo', function='*'),
            dict(stored_rule(), module='demo', function='da_tat', bat=False,
                 uu_tien='cu-demo', du_phong=['cu-demo'])])
        before = deepcopy(config)
        opened = self.call()
        self.assertEqual(opened['status'], 200, opened)
        self.assertEqual(opened['body']['quy_tac'][1]['chuc_nang'], 'demo:*')
        result = self.save(dict(row_version='1', quy_tac_model=opened['body']['quy_tac']))
        self.assertEqual(result['status'], 200, result)
        self.assertEqual(self.conn.profile['cau_hinh'], before)

    def test_cau_hinh_cu_bao_can_luu_lai_khong_am_tham_bo(self):
        self.conn.profile['cau_hinh'] = dict(local_ai=dict(dia_chi=ADDRESS,
            models=[model()], quy_tac=[rule()]))
        before = deepcopy(self.conn.profile)
        service = self.service()
        for response in (self.call(), self.detect(), self.save()):
            self.assertEqual(response['status'], 422, response)
            self.assertIn('Cần lưu lại cấu hình', response['body']['thong_diep'])
        self.assertEqual(self.conn.profile, before)
        service.assert_not_called()

    def test_manifest_that_khoa_la_va_dia_chi_ngoai_noi_bo_bi_chan_truoc_dich_vu(self):
        service = self.service()
        original = deepcopy(self.conn.profile['cau_hinh'])
        bad = []
        for section in (None, 'local_ai', 'model_phat_hien', 'quy_tac_model'):
            config = deepcopy(original)
            target = config if section is None else config[section]
            if isinstance(target, list):
                target = target[0]
            target['truong_la'] = True
            bad.append(config)
        for address in ('http://8.8.8.8:1234/v1/chat/completions',
                        'http://ai.example.invalid:1234/v1/chat/completions',
                        'http://169.254.1.1:1234/v1/chat/completions'):
            config = deepcopy(original)
            config['local_ai']['url'] = address
            bad.append(config)
        for config in bad:
            self.conn.profile['cau_hinh'] = config
            before = deepcopy(self.conn.profile)
            with self.subTest(config=config):
                self.assertEqual(self.detect()['status'], 422)
                self.assertEqual(self.save()['status'], 422)
                self.assertEqual(self.conn.profile, before)
        service.assert_not_called()

    def test_khong_co_api_cloud_va_method_query_ngoai_contract(self):
        for suffix in ('/cloud', '/cloud/bat', '/cloud/goi'):
            self.assertEqual(self.call(PATH.rsplit('/local', 1)[0] + suffix, 'POST', {})['status'], 404)
        self.assertEqual(self.call(PATH, 'PUT', {})['status'], 405)
        self.assertEqual(self.call(PATH + '?dia_chi=khac')['status'], 422)
        self.assertEqual(self.call(PATH + '/phat-hien', 'POST', {'row_version': '1', 'dia_chi': ADDRESS})['status'], 422)
        self.assertEqual(self.call(PATH + '/quy-tac', 'GET')['status'], 405)
        self.assertEqual(self.call(PATH + '/quy-tac', 'POST', {})['status'], 405)
        self.assertEqual(self.call(PATH + '/quy-tac?dia_chi=khac', 'PUT',
            dict(row_version='1', quy_tac_model=[rule()]))['status'], 422)
        self.assertEqual(self.save(headers={'Idempotency-Key': None})['status'], 400)
        self.assertEqual(self.save(headers={'X-Phap-Nhan-Id': str(cfg.web.g18.USER)})['status'], 400)


if __name__ == '__main__':
    unittest.main()
