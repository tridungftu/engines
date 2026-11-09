"""MASK-3H: factory/WSGI thật, hàng việc và SQL giả; không PG/server."""
from contextlib import nullcontext
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from io import BytesIO
import json
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, Mock, patch
from uuid import uuid4

from kho_tri_thuc.core import dispatcher as d, http as h, phien, ung_dung as u
from kho_tri_thuc.core import routes_mask as r
from kho_tri_thuc.core.dich_vu_engine import DichVuEngine
from tests.test_g2_18 import KetNoiGia
from tests.test_g2_32_e2 import pin_demo, binding_demo


CANARY = 'Công ty DEMO CANARY_GOC_KHONG_GHI_NHAT_KY'


class MaskHTTPTests(unittest.TestCase):
    def setUp(self):
        self.conn = KetNoiGia()
        self.connect = Mock(side_effect=lambda **kw: nullcontext(self.conn))
        self.user, self.pn, self.doc = uuid4(), uuid4(), uuid4()
        self.admin, self.demo, self.actor_ok = True, True, True
        self.sql = []
        self.conn.execute = self.execute
        now = datetime.now(timezone.utc)
        self.ma = phien.MaBiMat('PHIEN_CORE_DEMO')
        self.module_ma = phien.MaBiMat('PHIEN_MODULE_DEMO')
        self.session = h.PhienHTTP(self.user, phien.MaBiMat('CSRF_DEMO'),
            lambda m, pn: self.ma if m == 'core' else self.module_ma, now, now)
        self.enterContext(patch.object(u, 'nap_cau_hinh',
            return_value=u.CauHinhDemo({}, 8790)))
        self.xac = self.enterContext(patch.object(phien, 'xac_minh_phien',
            side_effect=self.identity))
        self.mtq = self.enterContext(patch.object(d.mtq, 'quyet_dinh_phien',
            return_value=dict(ket_luan='DAT', cho_phep=True)))
        self.receipt_read = self.enterContext(patch.object(d.tiep_nhan, 'tra_core',
            side_effect=AssertionError('Không đưa toàn văn vào biên nhận')))
        self.receipt_write = self.enterContext(patch.object(d.tiep_nhan, 'ghi_core',
            side_effect=AssertionError('Không ghi toàn văn vào biên nhận')))
        self.engine = MagicMock(spec=DichVuEngine)
        pin = pin_demo(ma_engine='e_mask', capability='mask.che@1')
        self.engine._ghim = {pin.capability: pin}
        self.binding = binding_demo(pin)
        self.engine._loai_viec = {('crm', self.binding.loai, 1): self.binding}
        self.engine.gui_viec.side_effect = self.enqueue
        self.source = r.NguonChayThuMask(module='crm', hanh_dong='CRM:DEMO:LAP',
            capability=pin.capability, loai_viec=self.binding.loai, phien_ban=1,
            tai_lieu_id=self.doc, bang_tham_chieu='tai_lieu', tham_chieu_id=self.doc)
        self.prepare = Mock(return_value=self.source)
        self.result = dict(trang_thai='queued', ket_qua=None)
        self.read = Mock(side_effect=lambda *a, **kw: deepcopy(self.result))
        self.service = r.DichVuChayThuMask(self.engine, self.prepare, self.read)
        self.jobs = []
        self.make()

    def make(self, service=True):
        self.app = u.tao_ung_dung('CAU_HINH_GIA_KHONG_DOC', ket_noi=self.connect,
            doc_phien=lambda sid: self.session, doc_kt=Mock(side_effect=AssertionError()),
            dich_vu_mask=self.service if service else None)

    def identity(self, conn, **ctx):
        if not self.actor_ok:
            return None
        return SimpleNamespace(nguoi_dung_id=self.user, module=ctx['module'],
            phap_nhan_id=ctx['phap_nhan_id'], hanh_dong=ctx['hanh_dong'],
            viec_id=None, the_he=None)

    def execute(self, sql, args):
        self.assertEqual(self.conn.info.transaction_status, 2)
        self.sql.append((sql, args))
        if 'la_admin_bootstrap' in sql:
            return SimpleNamespace(fetchone=lambda: (self.admin,))
        if 'phap_nhan_cua_toi' in sql:
            return SimpleNamespace(fetchall=lambda: [(self.pn, 'Công ty DEMO', self.demo, self.user)])
        raise AssertionError('Không được đọc bảng nội bộ')

    def enqueue(self, conn, capability, **kwargs):
        self.assertEqual(conn.info.transaction_status, 2)
        self.assertNotIn(CANARY, repr(kwargs))
        job = uuid4()
        self.jobs.append(job)
        return job

    def call(self, suffix='che-van-ban', *, method='POST', body=None, csrf=True,
             key='MASK_DEMO_00000001', cookie='SID_DEMO', raw=None, **headers):
        if body is None and method == 'POST':
            body = dict(van_ban=CANARY, dinh_danh_da_biet=[])
        raw = raw if raw is not None else (b'' if body is None else
            json.dumps(body, ensure_ascii=False).encode('utf-8'))
        env = dict(PATH_INFO=r.TIEN_TO + '/' + str(suffix), QUERY_STRING='',
            REQUEST_METHOD=method, CONTENT_LENGTH=str(len(raw)), CONTENT_TYPE='application/json',
            HTTP_HOST='127.0.0.1:8790', HTTP_ORIGIN='http://127.0.0.1:8790',
            HTTP_COOKIE='__Host-ktt_phien=' + cookie, HTTP_X_PHAP_NHAN_ID=str(self.pn),
            HTTP_IDEMPOTENCY_KEY=key)
        if csrf:
            env['HTTP_X_CSRF_TOKEN'] = 'CSRF_DEMO'
        env.update(headers)
        env['wsgi.input'] = BytesIO(raw)
        response = {}
        def start(status, pairs):
            response.update(status=int(status.split()[0]), headers=dict(pairs))
        response['body'] = json.loads(b''.join(self.app(env, start)))
        return response

    def submit(self):
        response = self.call()
        self.assertEqual(response['status'], 202, response)
        self.assertEqual(response['headers']['Location'],
                         r.TIEN_TO + '/' + response['body']['viec_id'])
        return response['body']['viec_id']

    def che_result(self, *, blocked=False):
        return dict(ma_yeu_cau=str(uuid4()), ma_luot=str(uuid4()),
            van_ban_da_che=None if blocked else '[[CONG_TY_DEMO]]',
            con_sot=[dict(nhom='CONG_TY', vi_tri=dict(bat_dau=0, ket_thuc=5, dong=1, cot=1))]
                if blocked else [], kiem_tien_ngay=True, gui_duoc=not blocked,
            so_cho_thay=0, bi_danh=[], cho_duyet=dict(so_cum_vua_them=0), canh_bao=[])

    def mo_body(self):
        job = self.submit()
        self.result = dict(trang_thai='succeeded', ket_qua=self.che_result())
        response = self.call(job, method='GET')
        self.assertEqual(response['status'], 200, response)
        return dict(ma_yeu_cau=response['body']['ket_qua']['ma_yeu_cau'],
                    van_ban_co_bi_danh='[[CONG_TY_DEMO]]', dong_viec=False)

    def test_factory_khong_mo_ket_noi(self):
        self.connect.assert_not_called()

    def test_khong_admin_ca_ba_route_403(self):
        self.admin = False
        for suffix, method, body in [('che-van-ban', 'POST', None),
                ('mo-che-van-ban', 'POST', dict(ma_yeu_cau=str(uuid4()),
                    van_ban_co_bi_danh='DEMO', dong_viec=False)), (uuid4(), 'GET', None)]:
            with self.subTest(method=method, suffix=suffix):
                self.assertEqual(self.call(suffix, method=method, body=body)['status'], 403)
        self.prepare.assert_not_called()
        self.read.assert_not_called()

    def test_thieu_csrf_ca_post_va_get_bi_tu_choi(self):
        for method, suffix in [('POST', 'che-van-ban'), ('GET', uuid4())]:
            self.assertEqual(self.call(suffix, method=method, csrf=False)['status'], 403)
        self.connect.assert_not_called()

    def test_phap_nhan_that_tu_choi_ca_ba_route(self):
        body = self.mo_body()
        self.demo = False
        for suffix, method, data in [('che-van-ban', 'POST', None),
                ('mo-che-van-ban', 'POST', body), (self.jobs[0], 'GET', None)]:
            self.assertEqual(self.call(suffix, method=method, body=data)['status'], 403)

    def test_dich_vu_none_tra_cau_tieng_viet(self):
        self.make(False)
        for suffix, method in [('che-van-ban', 'POST'), (uuid4(), 'GET')]:
            response = self.call(suffix, method=method)
            self.assertEqual(response['status'], 503, response)
            self.assertEqual(response['body']['thong_diep'], 'Chức năng chạy thử chưa được bật')
            self.assertIn('ma', response['body'])

    def test_post_202_chi_sau_commit_va_gui_tham_chieu_chuan(self):
        job = self.submit()
        self.assertEqual(self.conn.events[-1], 'commit')
        kwargs = self.engine.gui_viec.call_args.kwargs
        self.assertEqual(kwargs['module'], 'crm')
        self.assertEqual(kwargs['phap_nhan_id'], self.pn)
        self.assertEqual(kwargs['hanh_dong'], 'CRM:DEMO:LAP')
        self.assertEqual(kwargs['tham_chieu_id'], self.doc)
        self.assertNotIn('van_ban', kwargs)
        self.assertEqual(set(kwargs), {'loai', 'phien_ban', 'khoa_dedupe',
            'bang_tham_chieu', 'tham_chieu_id', 'ma', 'module', 'phap_nhan_id', 'hanh_dong'})
        self.assertEqual(self.call(job, method='GET')['status'], 200)

    def test_than_khong_duoc_chen_danh_tinh_nguon(self):
        for field in ('module', 'phap_nhan_id', 'hanh_dong', 'tai_lieu_id', 'nguon'):
            response = self.call(body=dict(van_ban=CANARY, dinh_danh_da_biet=[], **{field: 'GIA_MAO'}))
            self.assertEqual(response['status'], 422, response)
        self.prepare.assert_not_called()

    def test_get_phien_khac_cung_nguoi_bi_tu_choi_truoc_provider(self):
        job = self.submit()
        self.assertEqual(self.call(job, method='GET', cookie='SID_KHAC')['status'], 403)
        self.read.assert_not_called()

    def test_get_kiem_lai_quyen_admin_va_module(self):
        job = self.submit()
        self.admin = False
        self.assertEqual(self.call(job, method='GET')['status'], 403)
        self.admin = True
        self.mtq.return_value = dict(ket_luan='DAT', cho_phep=False)
        self.assertEqual(self.call(job, method='GET')['status'], 403)
        self.read.assert_not_called()

    def test_phien_backend_thu_hoi_bi_tu_choi(self):
        job = self.submit()
        self.actor_ok = False
        self.assertEqual(self.call(job, method='GET')['status'], 401)
        self.read.assert_not_called()

    def test_phien_http_het_han_bi_tu_choi(self):
        self.session = replace(self.session, tao_luc=self.session.tao_luc-timedelta(days=1))
        self.assertEqual(self.call()['status'], 401)
        self.prepare.assert_not_called()

    def test_get_khong_thay_viec_khong_doc_provider(self):
        self.assertEqual(self.call(uuid4(), method='GET')['status'], 404)
        self.read.assert_not_called()

    def test_tra_ket_qua_che_bi_chan_null_va_vi_tri_object(self):
        job = self.submit()
        self.result = dict(trang_thai='succeeded', ket_qua=self.che_result(blocked=True))
        response = self.call(job, method='GET')
        self.assertEqual(response['status'], 200, response)
        self.assertIsNone(response['body']['ket_qua']['van_ban_da_che'])
        self.assertIsInstance(response['body']['ket_qua']['con_sot'][0]['vi_tri'], dict)

    def test_ket_qua_bi_chan_co_van_ban_khong_duoc_cong_bo(self):
        job = self.submit()
        result = self.che_result(blocked=True)
        result['van_ban_da_che'] = CANARY
        self.result = dict(trang_thai='succeeded', ket_qua=result)
        response = self.call(job, method='GET')
        self.assertEqual(response['status'], 502, response)
        self.assertNotIn(CANARY, json.dumps(response, ensure_ascii=False))

    def test_vi_tri_sai_dang_khong_cong_bo(self):
        job = self.submit()
        result = self.che_result(blocked=True)
        result['con_sot'][0]['vi_tri'] = [0, 5]
        self.result = dict(trang_thai='succeeded', ket_qua=result)
        self.assertEqual(self.call(job, method='GET')['status'], 502)

    def test_mo_che_post_202_va_get_dung_dang(self):
        body = self.mo_body()
        response = self.call('mo-che-van-ban', body=body, key='MASK_MO_DEMO_0001')
        self.assertEqual(response['status'], 202, response)
        self.result = dict(trang_thai='succeeded', ket_qua=dict(ma_yeu_cau=body['ma_yeu_cau'],
            ma_luot=str(uuid4()), van_ban_da_mo_che=CANARY, so_cho_mo=1,
            bi_danh_khong_ro=[], mo_day_du=True, trang_thai_ma_yeu_cau='DANG_XU_LY'))
        response = self.call(response['body']['viec_id'], method='GET')
        self.assertEqual(response['status'], 200, response)
        self.assertEqual(response['body']['ket_qua']['van_ban_da_mo_che'], CANARY)
        self.assertTrue(response['body']['ket_qua']['mo_day_du'])
        self.assertEqual(self.prepare.call_args.kwargs['nguon_goc'], self.source)

    def test_mo_che_khong_nhan_ma_yeu_cau_phien_khac(self):
        body = self.mo_body()
        self.prepare.reset_mock()
        response = self.call('mo-che-van-ban', body=body, cookie='SID_KHAC', key='MASK_MO_KHAC_0001')
        self.assertEqual(response['status'], 403, response)
        self.prepare.assert_not_called()

    def test_mo_che_khong_cho_provider_doi_tai_lieu(self):
        body = self.mo_body()
        self.prepare.return_value = replace(self.source, tai_lieu_id=uuid4())
        self.assertEqual(self.call('mo-che-van-ban', body=body,
            key='MASK_MO_SAI_NGUON_0001')['status'], 503)
        self.assertEqual(len(self.jobs), 1)

    def test_nguon_khong_phai_mask_bi_tu_choi(self):
        pin = next(iter(self.engine._ghim.values()))
        self.engine._ghim[pin.capability] = replace(pin, ma_engine='e_ocr')
        self.assertEqual(self.call()['status'], 503)
        self.engine.gui_viec.assert_not_called()

    def test_retry_cung_khoa_khong_gui_hai_viec_va_van_kiem_quyen(self):
        job = self.submit()
        self.assertEqual(self.call()['body']['viec_id'], job)
        self.assertEqual(self.prepare.call_count, 1)
        self.assertEqual(self.engine.gui_viec.call_count, 1)
        self.admin = False
        self.assertEqual(self.call()['status'], 403)

    def test_commit_loi_khong_tra_202_va_khong_nho_so_huu(self):
        self.conn.loi_commit = True
        response = self.call()
        self.assertEqual(response['status'], 503, response)
        self.conn.loi_commit = False
        self.assertEqual(self.call(self.jobs[0], method='GET')['status'], 404)

    def test_van_ban_qua_tran_ky_tu_va_byte_bi_chan(self):
        for raw in (json.dumps(dict(van_ban='a'*500001, dinh_danh_da_biet=[])).encode(),
                    json.dumps(dict(van_ban='ế'*400000, dinh_danh_da_biet=[]), ensure_ascii=False).encode()):
            response = self.call(raw=raw)
            self.assertIn(response['status'], (413, 422), response)
        self.prepare.assert_not_called()
        self.assertEqual(h.GIOI_HAN_JSON, 1024*1024)

    def test_loi_provider_khong_lo_toan_van_vao_log_bien_nhan_va_loi(self):
        self.prepare.side_effect = RuntimeError(CANARY)
        with patch('logging.Logger._log') as log:
            response = self.call()
        self.assertEqual(response['status'], 503, response)
        self.assertNotIn(CANARY, json.dumps(response, ensure_ascii=False))
        self.assertNotIn(CANARY, repr(self.sql))
        self.assertNotIn(CANARY, repr(log.call_args_list))
        self.receipt_read.assert_not_called()
        self.receipt_write.assert_not_called()

    def test_loi_http_provider_gia_ma_noi_bo_van_bi_an_thong_diep(self):
        self.prepare.side_effect = h.LoiHTTP(503, ma='MASK_THU_CHUA_SAN_SANG',
                                            thong_diep=CANARY)
        response = self.call()
        self.assertEqual(response['status'], 503, response)
        self.assertEqual(response['body']['thong_diep'],
                         'Chưa xử lý được yêu cầu chạy thử. Thử lại sau.')
        self.assertNotIn(CANARY, json.dumps(response, ensure_ascii=False))

    def test_loi_http_doc_ket_qua_khong_tra_nguyen_ma_va_thong_diep(self):
        job = self.submit()
        self.read.side_effect = h.LoiHTTP(403, ma='MASK_THU_' + CANARY, thong_diep=CANARY)
        response = self.call(job, method='GET')
        self.assertEqual(response['status'], 403, response)
        self.assertNotIn(CANARY, json.dumps(response, ensure_ascii=False))

    def test_bien_mask_giu_nguyen_route_khac(self):
        response = self.call(method='GET', PATH_INFO='/api/v1/healthz')
        self.assertEqual(response['status'], 200, response)
        self.assertEqual(response['body'], dict(trang_thai='song'))
        self.assertEqual(self.call(method='GET', PATH_INFO='/api/v1/khong-ton-tai')['status'], 404)
        self.prepare.assert_not_called()


if __name__ == '__main__':
    unittest.main()
