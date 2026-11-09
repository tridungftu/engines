"""AI-4b: bootstrap/stdin giả và cổng thật với provider/Mask giả, chỉ DEMO.

CHUA_KIEM: tài khoản Windows riêng/ACL và AI/Mask thực; không khởi server.
"""

from contextlib import redirect_stderr, redirect_stdout
import base64
import io
import json
import logging
import os
from pathlib import Path
import pickle
import sys
import traceback
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from kho_tri_thuc.engines.e_hoi_ai.bi_mat import BiMatRAM, LoiBiMat, tao_cong_ai
from kho_tri_thuc.sdk_core import bootstrap as bs
from kho_tri_thuc.tri_thuc import cong_ai as ca


CANARY = 'AI4B_DEMO_CANARY_KEY_0123456789'
VAN_BAN = 'Lãi suất DEMO 8%/năm.'


def bootstrap_gia(raw):
    """Đối tượng Bootstrap thật, transport stdin và Windows handle giả."""
    cfg = dict(protocol=bs.PROTOCOL, kieu='khoi_dong', pid=os.getpid(),
               dinh_danh_lan_tao='DEMO_FILETIME', cong=23456,
               dia_chi_nghe='127.0.0.1', phien_ban='0.1.0-demo.1', the_he=1,
               issuer='DEMO', module='e_hoi_ai', instance_id='DEMO',
               nonce_khoi_dong='DEMO', socket='REVNTw==',
               tham_so={'cong_khai': 'DEMO'})
    vao, ra = io.BytesIO(), io.BytesIO()
    bs.gui_thong_diep(vao, cfg)
    bs.gui_thong_diep(vao, {'protocol': bs.PROTOCOL, 'kieu': 'bi_mat',
        'du_lieu': base64.b64encode(json.dumps(raw).encode('utf-8')).decode('ascii')})
    # Lệnh kế tiếp phải còn nguyên sau lấy bí mật.
    bs.gui_thong_diep(vao, {'protocol': bs.PROTOCOL, 'kieu': 'nhan_accept'})
    vao.seek(0)
    nghe = Mock()
    nghe.getsockname.return_value = ('127.0.0.1', 23456)
    with patch.object(bs, 'dinh_danh_lan_tao', return_value='DEMO_FILETIME'), \
            patch.object(bs.socket, 'fromshare', return_value=nghe, create=True), \
            patch.object(bs, 'BoDocNguCanh'):
        obj = bs.Bootstrap.nhan(kiem_chu_ky=lambda *a: None, stdin=vao, stdout=ra)
    return obj, vao, ra


def tra_loi():
    return json.dumps({'truong': [{'ten': 'lai_suat', 'gia_tri': '8%/năm',
                                  'trich_dan': VAN_BAN}], 'do_tin_cay': 0.99})


class BiMatTest(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch('socket.socket', side_effect=AssertionError('Cấm mạng')))
        self.enterContext(patch.object(ca, 'doc_khoa_mask',
                                      side_effect=AssertionError('Cấm tệp khóa')))
        self.enterContext(patch.object(ca, 'MaskV2',
                                      side_effect=AssertionError('Cấm Mask mặc định')))
        self.enterContext(patch.object(ca.os, 'environ',
                                      {'ANTHROPIC_API_KEY': 'OS_ENV_DEMO_CAM'}))
        self.mask = Mock()
        self.mask.co_khoa.return_value = True
        self.mask.che.side_effect = lambda text, ids: ca.LuotChe('DEMO_LUOT', text)
        self.mask.mo_che.side_effect = lambda ma, text, **kw: text
        self.cloud = Mock()
        self.cloud.tra_loi.return_value = ca.PhanHoiCloud(tra_loi(), 'DEMO_MODEL', 1, 2)
        self.local = Mock(return_value=tra_loi())
        self.ghi = ca.BoGhiBoNho()  # Chỉ trong test, runtime dùng BoGhiQuaCore.

    def cong(self, raw=None, **changes):
        bootstrap, _, _ = bootstrap_gia({'ANTHROPIC_API_KEY': CANARY}
                                       if raw is None else raw)
        settings = {'local_ai': {'enabled': True, 'model': 'DEMO_LOCAL',
                    'url': 'http://127.0.0.1:1234/v1/chat/completions'},
                    'cong_ai': {'cloud_bat': True, **changes}}
        bi_mat = BiMatRAM.tu_bootstrap(bootstrap, settings)
        return tao_cong_ai(settings, bi_mat=bi_mat, mask=self.mask, bo_ghi=self.ghi,
                           nha_cung_cap=self.cloud, local_transport=self.local), bi_mat

    def goi(self, cong):
        return cong.goi(ca.YeuCauAI('BOC_TACH_HOP_DONG', VAN_BAN,
                                  'Trích lãi suất DEMO', ('lai_suat',)))

    def test_bootstrap_tieu_thu_mot_lan_khong_doc_lenh_ke_tiep(self):
        bootstrap, vao, ra = bootstrap_gia({'ANTHROPIC_API_KEY': CANARY})
        raw = bootstrap.bi_mat
        pos = vao.tell()
        bi_mat = BiMatRAM.tu_bootstrap(bootstrap)
        self.assertEqual(bi_mat['ANTHROPIC_API_KEY'], CANARY)
        with self.assertRaisesRegex(bs.LoiBootstrap, 'BM_DA_LAY'):
            raw.lay_mot_lan()
        self.assertEqual(bootstrap.tham_so, {'cong_khai': 'DEMO'})
        self.assertEqual(vao.tell(), pos)
        self.assertEqual(bs.doc_thong_diep(vao.readline()),
                         {'protocol': bs.PROTOCOL, 'kieu': 'nhan_accept'})
        self.assertEqual(ra.getvalue(), b'')
        with self.assertRaises(LoiBiMat):
            BiMatRAM.tu_bootstrap(bootstrap)

    def test_repr_log_exception_pickle_khong_lo_canary(self):
        bootstrap, _, _ = bootstrap_gia({'ANTHROPIC_API_KEY': CANARY})
        bi_mat = BiMatRAM.tu_bootstrap(bootstrap)
        out, err, logs = io.StringIO(), io.StringIO(), io.StringIO()
        handler = logging.StreamHandler(logs)
        logger = logging.getLogger('AI4B_DEMO')
        logger.addHandler(handler)
        try:
            with redirect_stdout(out), redirect_stderr(err):
                print(bi_mat, bootstrap)
                logger.warning('%r', bi_mat)
                for action in (lambda: pickle.dumps(bi_mat), lambda: bi_mat[CANARY]):
                    try:
                        action()
                    except Exception as exc:
                        logger.exception('DEMO lỗi đã ẩn')
                        self.assertNotIn(CANARY, repr(exc))
                        self.assertNotIn(CANARY, ''.join(traceback.format_exception(exc)))
        finally:
            logger.removeHandler(handler)
        self.assertNotIn(CANARY, out.getvalue() + err.getvalue() + logs.getvalue())
        self.assertNotIn(CANARY, repr(bi_mat.items()))
        with self.assertRaises(TypeError):
            bi_mat['ANTHROPIC_API_KEY'] = 'DEMO'

    def test_du_lieu_sai_khong_lo_exception_va_xoa_raw(self):
        for raw in (None, [], CANARY, {'DSN': CANARY}, {CANARY: CANARY},
                    {'ANTHROPIC_API_KEY': {'secret': CANARY}},
                    {'ANTHROPIC_API_KEY': CANARY + '\n'},
                    {'ANTHROPIC_API_KEY': ''}, {'ANTHROPIC_API_KEY': 'x' * 4097}):
            with self.subTest(kieu=type(raw).__name__):
                bootstrap, _, _ = bootstrap_gia(raw)
                held = bootstrap.bi_mat
                try:
                    BiMatRAM.tu_bootstrap(bootstrap)
                except LoiBiMat as exc:
                    self.assertNotIn(CANARY, ''.join(traceback.format_exception(exc)))
                    self.assertIsNone(exc.__context__)
                else:
                    self.fail('Phải từ chối bí mật sai')
                self.assertNotIn('bi_mat', bootstrap.tham_so)
                with self.assertRaisesRegex(bs.LoiBootstrap, 'BM_DA_LAY'):
                    held.lay_mot_lan()
        with self.assertRaises(LoiBiMat):
            BiMatRAM.tu_bootstrap({'bi_mat': CANARY})

    def test_cloud_di_qua_mask_va_nhan_dung_khoa_ram(self):
        cong, bi_mat = self.cong()
        self.local.return_value = '{}'
        self.assertEqual(self.goi(cong).duong, 'CLOUD')
        self.assertIs(cong._moi_truong, bi_mat)
        self.assertIs(cong._mask, self.mask)
        self.assertEqual(self.cloud.tra_loi.call_args.kwargs['khoa'], CANARY)
        self.mask.che.assert_called_once()
        self.mask.mo_che.assert_called_once()
        self.assertIs(self.mask.mo_che.call_args.kwargs['ket_thuc_luot'], True)
        self.assertNotIn(CANARY, repr(self.ghi.ban_ghi))

    def test_local_truoc_cloud_va_cloud_tat_khong_dung_khoa(self):
        cong, _ = self.cong()
        self.assertEqual(self.goi(cong).duong, 'LOCAL')
        self.cloud.tra_loi.assert_not_called()
        self.mask.che.assert_not_called()
        cong, _ = self.cong(cloud_bat=False)
        self.local.return_value = '{}'
        self.goi(cong)
        self.cloud.tra_loi.assert_not_called()
        self.mask.co_khoa.assert_not_called()

    def test_thieu_va_thu_hoi_khoa_khong_fallback_env(self):
        for raw in ({}, {'OPENAI_API_KEY': CANARY}, {'ANTHROPIC_API_KEY': CANARY}):
            cong, bi_mat = self.cong(raw, bien_khoa_api=next(iter(raw), 'ANTHROPIC_API_KEY'))
            bi_mat.thu_hoi()
            bi_mat.thu_hoi()
            self.local.return_value = '{}'
            result = self.goi(cong)
            self.assertIn('CHUA_CO_KHOA_API', result.ly_do)
            self.assertIs(cong._moi_truong, bi_mat)
            self.assertEqual(len(bi_mat), 0)
        self.cloud.tra_loi.assert_not_called()
        self.mask.che.assert_not_called()

    def test_khoa_tuy_chinh_va_cach_ly_hai_instance(self):
        cong, bi_mat = self.cong({'DEMO_API_KEY': CANARY}, bien_khoa_api='DEMO_API_KEY')
        other, other_keys = self.cong({'DEMO_API_KEY': 'OTHER_DEMO'},
                                     bien_khoa_api='DEMO_API_KEY')
        self.local.return_value = '{}'
        self.goi(cong)
        self.assertEqual(self.cloud.tra_loi.call_args.kwargs['khoa'], CANARY)
        bi_mat.thu_hoi()
        self.goi(other)
        self.assertEqual(self.cloud.tra_loi.call_args.kwargs['khoa'], 'OTHER_DEMO')
        self.assertEqual(len(other_keys), 1)

    def test_mask_tu_choi_khong_gui_cloud(self):
        cong, _ = self.cong()
        self.local.return_value = '{}'
        self.mask.che.side_effect = ca.MaskKhongGui('MASK_DANH_MUC_KHOA')
        self.assertIn('MASK_DANH_MUC_KHOA', self.goi(cong).ly_do)
        self.cloud.tra_loi.assert_not_called()

    def test_factory_bat_buoc_seam_va_an_loi_cau_hinh(self):
        for changes in ({'bi_mat': None}, {'bi_mat': {}}, {'mask': None},
                        {'bo_ghi': None}):
            kwargs = dict(settings={}, bi_mat=BiMatRAM(), mask=self.mask, bo_ghi=self.ghi)
            kwargs.update(changes)
            with self.assertRaises(LoiBiMat) as caught:
                tao_cong_ai(**kwargs)
            self.assertNotIn(CANARY, repr(caught.exception))
            self.assertIsNone(caught.exception.__context__)
        with patch('kho_tri_thuc.engines.e_hoi_ai.bi_mat.CongAI',
                   side_effect=ValueError(CANARY)):
            with self.assertRaises(LoiBiMat) as caught:
                tao_cong_ai({}, bi_mat=BiMatRAM(), mask=self.mask, bo_ghi=self.ghi)
        self.assertNotIn(CANARY, repr(caught.exception))
        self.assertIsNone(caught.exception.__context__)
        self.cloud.tra_loi.assert_not_called()


if __name__ == '__main__':
    unittest.main()
