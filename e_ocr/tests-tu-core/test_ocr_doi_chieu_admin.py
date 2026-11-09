"""OCR-CR-8: factory WSGI thật, phiên và SQL giả; không PG/server/ABBYY."""
from contextlib import nullcontext
from copy import deepcopy
from datetime import datetime, timezone
from io import BytesIO
import json
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

from kho_tri_thuc.core import dispatcher as d, http as h, phien, ung_dung as u
from kho_tri_thuc.core import routes_ocr_doi_chieu as r
from tests.test_g2_18 import KetNoiGia


MA = 'ocr:' + 'a' * 32
CANARY = 'BÍ_MẬT_DRIVER_KHÔNG_CÔNG_BỐ'


class OCRAdminHTTPTests(unittest.TestCase):
    def setUp(self):
        self.conn = KetNoiGia()
        self.conn.execute = Mock(side_effect=self.execute)
        self.connect = Mock(side_effect=lambda **kw: nullcontext(self.conn))
        self.user, self.pn = uuid4(), uuid4()
        self.admin = True
        self.actions = {'CORE:ENGINE:XEM', 'CORE:ENGINE:CAU_HINH'}
        self.sql_error = None
        self.rows = [dict(ma_tuong_quan=MA, so_trang=3, trang_thai='CHUA_RO',
            giu_luc='2026-11-08T03:04:05Z', module='crm', ma_bam_dau='a'*8, phien_ban=2)]
        self.final = dict(ma_tuong_quan=MA, so_trang=3, trang_thai='HOAN_TRANG', phien_ban=3)
        now = datetime.now(timezone.utc)
        self.token = phien.MaBiMat('PHIEN_CORE_DEMO')
        self.session = h.PhienHTTP(self.user, phien.MaBiMat('CSRF_DEMO'),
            Mock(return_value=self.token), now, now)
        self.enterContext(patch.object(u, 'nap_cau_hinh', return_value=u.CauHinhDemo({}, 8790)))
        self.identity = SimpleNamespace(nguoi_dung_id=self.user, module='core',
            phap_nhan_id=self.pn, hanh_dong='CORE:ENGINE:XEM', viec_id=None, the_he=None)
        self.auth = self.enterContext(patch.object(phien, 'xac_minh_phien',
            side_effect=self.xac_minh))
        self.context = self.enterContext(patch.object(r.mtq, 'dat_ngu_canh'))
        self.kt = Mock(side_effect=AssertionError('Không gọi KT hoặc engine'))
        self.app = u.tao_ung_dung('CAU_HINH_GIA_KHONG_DOC', ket_noi=self.connect,
            doc_phien=lambda sid: self.session, doc_kt=self.kt)

    def xac_minh(self, *args, hanh_dong, **kwargs):
        if hanh_dong not in self.actions or self.identity is None:
            return None
        values = vars(self.identity).copy()
        if values['hanh_dong'] == 'CORE:ENGINE:XEM':
            values['hanh_dong'] = hanh_dong
        return SimpleNamespace(**values)

    def execute(self, sql, args):
        self.assertEqual(self.conn.info.transaction_status, 2)
        if sql == 'SELECT loi.la_admin_bootstrap(%s)':
            return SimpleNamespace(fetchone=lambda: (self.admin,))
        if self.sql_error:
            raise self.sql_error
        if 'ocr_chua_ro_ds(' in sql:
            return SimpleNamespace(fetchone=lambda: (deepcopy(self.rows),))
        if 'ocr_chua_ro_chot_admin(' in sql:
            return SimpleNamespace(fetchone=lambda: (deepcopy(self.final),))
        raise AssertionError('Chỉ được gọi cửa Core đã duyệt')

    def call(self, *, method='GET', query=None, suffix='', body=None, csrf=True,
             cookie=True, pn_header=None, **headers):
        if query is None:
            query = 'phap_nhan_id=' + str(self.pn) if method == 'GET' else ''
        if method == 'POST' and body is None:
            body = dict(ket_qua='hoan_trang', phien_ban=2, ghi_chu='Đã đối chiếu bằng chứng DEMO.')
        raw = b'' if body is None else json.dumps(body, ensure_ascii=False).encode('utf-8')
        env = dict(PATH_INFO=r.TIEN_TO + suffix, QUERY_STRING=query, REQUEST_METHOD=method,
            CONTENT_LENGTH=str(len(raw)), CONTENT_TYPE='application/json',
            HTTP_HOST='127.0.0.1:8790', HTTP_ORIGIN='http://127.0.0.1:8790')
        if cookie:
            env['HTTP_COOKIE'] = '__Host-ktt_phien=SID_DEMO'
        if csrf:
            env['HTTP_X_CSRF_TOKEN'] = 'CSRF_DEMO'
        if pn_header is not None or method == 'POST':
            env['HTTP_X_PHAP_NHAN_ID'] = str(pn_header or self.pn)
        env.update(headers)
        env['wsgi.input'] = BytesIO(raw)
        response = {}
        def start(status, pairs):
            response.update(status=int(status.split()[0]), headers=dict(pairs))
        response['body'] = json.loads(b''.join(self.app(env, start)))
        return response

    def post(self, **kwargs):
        return self.call(method='POST', suffix='/' + MA + '/chot', **kwargs)

    def assert_safe_error(self, response, status):
        self.assertEqual(response['status'], status, response)
        self.assertTrue(response['body']['ma'].startswith('OCR_ADMIN_'), response)
        text = json.dumps(response, ensure_ascii=False)
        self.assertNotIn(CANARY, text)
        self.assertNotRegex(response['body']['thong_diep'], r'\b(?:Anh|anh|bạn)\b')
        self.assertIn('request_id', response['body'])

    def test_factory_dang_ky_hai_route_khong_mo_ket_noi(self):
        self.connect.assert_not_called()
        self.kt.assert_not_called()
        for method, path in [('GET', r.TIEN_TO), ('POST', r.TIEN_TO + '/' + MA + '/chot')]:
            route, _ = self.app.http.dispatcher.registry.tra(method, path)
            self.assertIn('CORE.OCR.DOI_CHIEU.', route.operation)

    def test_get_theo_phap_nhan_mac_dinh_va_dinh_dang_ngay(self):
        response = self.call()
        self.assertEqual(response['status'], 200, response)
        self.assertEqual(response['body']['danh_sach'][0]['giu_luc'], '08/11/2026 10:04:05')
        self.assertEqual(response['headers']['Cache-Control'], 'no-store')
        self.assertEqual(self.conn.execute.call_args.args,
            ('SELECT loi_tai_lieu.ocr_chua_ro_ds(%s,%s)', (self.pn, 25)))
        self.assertEqual(self.conn.events[-1], 'commit')
        self.context.assert_called_once_with(self.conn, ma=self.token, module='core',
            phap_nhan_id=self.pn, hanh_dong='CORE:ENGINE:XEM')

    def test_gioi_han_hop_le_va_dang_giu_qua_han(self):
        self.rows[0]['trang_thai'] = 'DANG_GIU'
        response = self.call(query='phap_nhan_id=' + str(self.pn) + '&gioi_han=100')
        self.assertEqual(response['status'], 200, response)
        self.assertEqual(self.conn.execute.call_args.args[1], (self.pn, 100))

    def test_get_rong_hop_le(self):
        self.rows = []
        self.assertEqual(self.call()['body']['danh_sach'], [])

    def test_khong_admin_tu_choi_ca_get_post_truoc_cua_ocr(self):
        self.admin = False
        for response in (self.call(), self.post()):
            self.assert_safe_error(response, 403)
        self.context.assert_not_called()
        self.assertTrue(all('ocr_chua_ro' not in c.args[0] for c in self.conn.execute.call_args_list))

    def test_phien_het_han_va_thieu_cookie(self):
        self.assert_safe_error(self.call(cookie=False), 401)
        self.identity = None
        self.assert_safe_error(self.call(), 401)
        self.context.assert_not_called()

    def test_phien_khac_nguoi_phap_nhan_module_hoac_lease_bi_tu_choi(self):
        for field, value in [('nguoi_dung_id', uuid4()), ('phap_nhan_id', uuid4()),
                ('module', 'crm'), ('hanh_dong', 'CORE:MODULE:XEM'),
                ('viec_id', uuid4()), ('the_he', 1)]:
            with self.subTest(field=field):
                old = getattr(self.identity, field)
                setattr(self.identity, field, value)
                self.assert_safe_error(self.call(), 403)
                setattr(self.identity, field, old)
        self.context.assert_not_called()

    def test_post_csrf_va_origin_bat_buoc_truoc_ket_noi(self):
        for kwargs in [dict(csrf=False), dict(HTTP_X_CSRF_TOKEN='SAI'),
                dict(HTTP_ORIGIN='https://khac.invalid')]:
            with self.subTest(kwargs=kwargs):
                self.assert_safe_error(self.post(**kwargs), 403)
        self.connect.assert_not_called()

    def test_get_phap_nhan_va_gioi_han_khong_hop_le(self):
        base = 'phap_nhan_id=' + str(self.pn)
        for query, status in [('', 400), ('phap_nhan_id=SAI', 400),
                (base+'&gioi_han=0', 422), (base+'&gioi_han=101', 400),
                (base+'&gioi_han=abc', 422), (base+'&gioi_han=01', 422),
                (base+'&khac=1', 422), (base+'&phap_nhan_id='+str(uuid4()), 400)]:
            with self.subTest(query=query):
                self.assert_safe_error(self.call(query=query), status)
        self.connect.assert_not_called()

    def test_get_header_query_khac_phap_nhan_bi_tu_choi(self):
        self.assert_safe_error(self.call(pn_header=uuid4()), 400)
        self.connect.assert_not_called()

    def test_post_hoan_trang_sql_tham_so_hoa_va_200_sau_commit(self):
        response = self.post()
        self.assertEqual(response['status'], 200, response)
        self.assertEqual(response['body']['trang_thai'], 'HOAN_TRANG')
        self.assertEqual(self.conn.events[-1], 'commit')
        sql, args = self.conn.execute.call_args.args
        self.assertEqual(sql, 'SELECT loi_tai_lieu.ocr_chua_ro_chot_admin(%s,%s,%s,%s,%s,%s)')
        self.assertEqual(args, (self.pn, MA, 2, 'hoan_trang', 'Đã đối chiếu bằng chứng DEMO.',
                               UUID(response['headers']['X-Request-Id'])))
        self.auth.assert_called_once_with(self.conn, ma=self.token, module='core',
            phap_nhan_id=self.pn, hanh_dong='CORE:ENGINE:CAU_HINH')
        self.context.assert_called_once_with(self.conn, ma=self.token, module='core',
            phap_nhan_id=self.pn, hanh_dong='CORE:ENGINE:CAU_HINH')

    def test_chot_truyen_request_id_may_chu_khong_tin_header_client(self):
        seen = set()
        for client_id in (str(uuid4()), 'KHONG_PHAI_UUID'):
            with self.subTest(client_id=client_id):
                response = self.post(HTTP_X_REQUEST_ID=client_id)
                self.assertEqual(response['status'], 200, response)
                request_id = response['headers']['X-Request-Id']
                self.assertNotEqual(request_id, client_id)
                self.assertNotIn(request_id, seen)
                seen.add(request_id)
                self.assertEqual(self.conn.execute.call_args.args[1][-1], UUID(request_id))

    def test_phien_chi_xem_doc_duoc_nhung_khong_chot(self):
        self.actions = {'CORE:ENGINE:XEM'}
        self.assertEqual(self.call()['status'], 200)
        response = self.post()
        self.assertIn(response['status'], (401, 403), response)
        self.assertTrue(all('ocr_chua_ro_chot_admin' not in call.args[0]
                            for call in self.conn.execute.call_args_list))

    def test_ghi_chu_bat_buoc_co_bang_chung(self):
        for note in ('', '   ', '\t\r\n', None, 'ế' * 501):
            with self.subTest(note=note):
                response = self.post(body=dict(ket_qua='hoan_trang', phien_ban=2, ghi_chu=note))
                self.assert_safe_error(response, 422)
                self.assertEqual(response['body']['thong_diep'], 'Cần ghi bằng chứng đối chiếu ABBYY.')
        self.connect.assert_not_called()

    def test_post_da_tieu_va_ghi_chu_500_ky_tu(self):
        self.final['trang_thai'] = 'DA_TIEU_TRANG'
        response = self.post(body=dict(ket_qua='da_tieu', phien_ban=2, ghi_chu='ế'*500))
        self.assertEqual(response['status'], 200, response)
        self.assertEqual(response['body']['trang_thai'], 'DA_TIEU_TRANG')

    def test_get_cong_bo_quyen_chot_do_may_chu_xac_minh(self):
        self.assertIs(self.call()['body']['co_quyen_chot'], True)
        self.actions = {'CORE:ENGINE:XEM'}
        self.assertIs(self.call()['body']['co_quyen_chot'], False)
        self.assertTrue(all('ocr_chua_ro_chot_admin' not in c.args[0]
                            for c in self.conn.execute.call_args_list))

    def test_get_quyen_chot_khong_tin_khai_bao_tu_trinh_duyet(self):
        self.actions = {'CORE:ENGINE:XEM'}
        response = self.call(HTTP_X_OCR_CO_QUYEN_CHOT='true')
        self.assertEqual(response['status'], 200)
        self.assertIs(response['body']['co_quyen_chot'], False)

    def test_get_quyen_chot_kiem_lai_dung_danh_tinh_va_quyen_he_thong(self):
        auth = self.xac_minh
        def sai_danh_tinh(*args, hanh_dong, **kwargs):
            result = auth(*args, hanh_dong=hanh_dong, **kwargs)
            if hanh_dong == 'CORE:ENGINE:CAU_HINH':
                result.phap_nhan_id = uuid4()
            return result
        self.auth.side_effect = sai_danh_tinh
        self.assertIs(self.call()['body']['co_quyen_chot'], False)
        self.auth.side_effect = auth
        gate = Mock(side_effect=lambda conn, ctx: ctx.hanh_dong == 'CORE:ENGINE:XEM')
        self.app.http.dispatcher.core.quyen_he_thong = gate
        self.assertIs(self.call()['body']['co_quyen_chot'], False)
        self.assertEqual(gate.call_args.args[1].operation, 'CORE.OCR.DOI_CHIEU.CHOT')

    def test_tai_nguyen_man_doi_chieu_duoc_dang_ky_tinh(self):
        path = '/core/ui/ocr_doi_chieu.js'
        self.assertIn(path, u._TINH)
        file, mime = u._TINH[path]
        self.assertTrue(file.is_file())
        self.assertEqual(mime, 'text/javascript; charset=utf-8')

    def test_post_khong_nhan_actor_bam_pn_va_than_sai(self):
        valid = dict(ket_qua='hoan_trang', phien_ban=2, ghi_chu='DEMO')
        invalid = [{}, [], dict(ket_qua='hoan_trang', phien_ban=2),
            *[{**valid, field: value} for field, value in [
                ('ket_qua', 'CHUA_RO'), ('phien_ban', 0), ('phien_ban', True),
                ('phien_ban', '2'), ('phien_ban', 2**63-1), ('ghi_chu', 'ế'*501),
                ('ghi_chu', None), ('chot_boi', str(self.user)), ('ma_bam', 'a'*64),
                ('phap_nhan_id', str(self.pn)), ('request_id', str(uuid4()))]]]
        for body in invalid:
            with self.subTest(body=body):
                self.assert_safe_error(self.post(body=body), 422)
        self.context.assert_not_called()

    def test_ket_qua_thua_khong_lo_bam_ghi_chu_hay_noi_dung(self):
        self.rows[0].update(ma_bam=CANARY, ghi_chu=CANARY, du_lieu=CANARY)
        self.final.update(ma_bam=CANARY, ghi_chu=CANARY)
        for response in (self.call(), self.post()):
            self.assertEqual(response['status'], 200, response)
            self.assertNotIn(CANARY, json.dumps(response))

    def test_dto_sai_bam_day_du_ngay_naive_va_trang_thai_bi_chan(self):
        for field, value in [('ma_bam_dau', 'a'*64), ('giu_luc', '2026-11-08T03:04:05'),
                ('so_trang', 0), ('phien_ban', True), ('trang_thai', 'HOAN_TAT')]:
            with self.subTest(field=field):
                old = self.rows[0][field]
                self.rows[0][field] = value
                self.assert_safe_error(self.call(), 502)
                self.rows[0][field] = old
        self.assertIn('rollback', self.conn.events)

    def test_ket_qua_chot_phai_khop_cas_ma_va_ket_luan(self):
        for field, value in [('phien_ban', 9), ('ma_tuong_quan', 'ocr:bbbb'),
                ('trang_thai', 'DA_TIEU_TRANG')]:
            with self.subTest(field=field):
                old = self.final[field]
                self.final[field] = value
                self.assert_safe_error(self.post(), 502)
                self.final[field] = old

    def test_loi_sql_chi_tra_ma_ho_tro_huu_han(self):
        for code, status in [('42501', 403), ('22023', 400), ('40001', 409),
                ('55P03', 409), ('40P01', 409), ('XX000', 503)]:
            with self.subTest(code=code):
                error = RuntimeError(CANARY)
                error.sqlstate = code
                self.sql_error = error
                self.assert_safe_error(self.post(), status)

    def test_commit_loi_khong_tra_200_va_khong_tu_gui_lai(self):
        self.conn.loi_commit = True
        self.assert_safe_error(self.post(), 503)
        self.assertEqual(sum('ocr_chua_ro_chot_admin' in c.args[0]
            for c in self.conn.execute.call_args_list), 1)
        self.assertEqual(self.conn.events[-1], 'rollback')

    def test_ket_noi_dang_trong_giao_dich_tu_choi(self):
        self.conn.info.transaction_status = 2
        self.assert_safe_error(self.post(), 503)
        self.conn.execute.assert_not_called()


if __name__ == '__main__':
    unittest.main()
