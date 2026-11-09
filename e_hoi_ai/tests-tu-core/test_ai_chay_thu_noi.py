"""AI-LAT10a vòng 8: composition Core → HTTP → kênh → Local → ACK → GET.

WSGI/socket đôi/CSDL giả trong RAM; không PostgreSQL, server hay Cloud.
"""
from contextlib import nullcontext
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from kho_tri_thuc.core import bi_mat, chay_core, dich_vu_engine as dv, http
from kho_tri_thuc.core import kenh_engine as ke, phien, ung_dung as u, viec
from kho_tri_thuc.engines.e_hoi_ai import chay as ai
from kho_tri_thuc.engines.e_hoi_ai.lib import cong_ai as ca
from kho_tri_thuc.sdk_core.engine import SDKEngine
from tests import test_ai_chay_thu_route as route, test_g2_32_e2 as e2


class KhoNoi(route.KhoGia):
    def __init__(self):
        super().__init__()
        self.job, self.step, self.attempt = uuid4(), uuid4(), uuid4()

    def execute(self, sql, args=None):
        if 'loi.nhan_viec_engine(' not in sql:
            return super().execute(sql, args)
        assert self.info.transaction_status == 2
        self.calls.append((sql,args))
        identity = next(iter(self.jobs))
        if self.jobs[identity] != 'CHO':
            return SimpleNamespace(fetchone=lambda: (None,))
        ma, module, pn, hd, instance, new_ma, seconds, loai, version, cap, eid, contract, cv = args
        self.jobs[identity] = 'DANG_CHAY'
        value = dict(viec_id=str(self.job),buoc_viec_id=str(self.step),lan_thu_id=str(self.attempt),
            phap_nhan_id=str(pn),module=module,hanh_dong=hd,instance_id=str(instance),the_he=1,
            giu_den=(datetime.now(timezone.utc)+timedelta(seconds=seconds)).isoformat(),
            loai=loai,phien_ban=version,capability=cap,engine_id=str(eid),ma_contract=contract,
            phien_ban_contract=cv)
        return SimpleNamespace(fetchone=lambda: (deepcopy(value),))


class NoiChayThuTests(unittest.TestCase):
    def setUp(self):
        self.conn = KhoNoi()
        self.connect = Mock(side_effect=lambda **kw: nullcontext(self.conn))
        self.pin = e2.pin_demo(capability='ai.hoi@1',ma_engine='e_hoi_ai',
            dau_vao=dv.GhimContract('hoi_ai.v2','2.0.0','b'*64),
            dau_ra=dv.GhimContract('tra_loi_ai.v2','2.0.0','c'*64))
        self.controller, self.message = e2.runtime_demo(self.pin)
        self.runtime = Mock(return_value=(self.controller,self.message))
        self.token = phien.MaBiMat('AI_THU_KENH_KHAC_ADMIN')
        self.session = http.PhienHTTP(route.g18.USER,phien.MaBiMat('CSRF_CANARY'),
            Mock(return_value=phien.MaBiMat('AI_THU_ADMIN_A')),route.g18.NOW,route.g18.NOW)
        self.guards = [self.enterContext(patch(target,side_effect=AssertionError('Cấm I/O thật')))
            for target in ('socket.socket','socket.create_connection','socket.getaddrinfo','subprocess.Popen')]
        self.enterContext(patch.object(u,'nap_cau_hinh',return_value=route.web.CONFIG))
        self.enterContext(patch.object(ke,'doc_function_chay_thu_hoi_ai',return_value=[deepcopy(route.FUNCTION)]))
        self.enterContext(patch('kho_tri_thuc.core.ho_so_module.doc_hoi_ai',return_value=('a'*64,
            dict(chi_dan='Trả lời theo hợp đồng DEMO.',ma_function='thanh_toan',
                 ma_prompt='thanh_toan',phien_ban_prompt='1'))))
        self.enterContext(patch.object(dv.dang_ky,'doc_dang_ky',side_effect=self.registry))
        self.enterContext(patch.object(dv.ho_so_chay,'bootstrap',return_value=dict(
            row_version=self.pin.row_version,ho_so_mau_id=str(self.pin.ho_so_mau_id),
            phien_ban_engine=self.pin.phien_ban_engine,ma_bam_schema=self.pin.ma_bam_schema)))
        self.enterContext(patch.object(dv.so_cong,'doc',return_value=dict(module=None,
            engine_ho_so_id=str(self.pin.ho_so_mau_id),giu_boi=str(self.controller.instance_id),
            the_he=self.controller.the_he,trang_thai='CON_GIU',het_hieu_luc_luc=None,
            dia_chi_nghe='127.0.0.1',cong=19001,
            giu_den=(datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat())))
        self.enterContext(patch.object(viec,'trang_thai_lease',return_value=dict(
            con_giu=True,lan_thu_id=str(self.conn.attempt))))
        self.local = Mock(return_value=json.dumps(dict(truong=[dict(ten='tra_loi',gia_tri='1.000.000 đồng',
            trich_dan=route.TAI_LIEU)],do_tin_cay=0.99),ensure_ascii=False))
        self.cloud, self.mask = Mock(), Mock()
        self.portal = ca.CongAI(dict(local_ai=dict(enabled=True,model='local-DEMO',
            url='http://127.0.0.1:1234/v1/chat/completions'),cong_ai=dict(cloud_bat=True),
            model_phat_hien=[dict(id_model='local-DEMO',trang_thai='san_sang',bat=True)],
            quy_tac_model=[dict(module='mau_demo',function='thanh_toan',bat=True,
                uu_tien='local-DEMO',du_phong=[],che_do='tu_chon')]),
            bo_ghi=ca.BoGhiBoNho(),local_transport=self.local,nha_cung_cap=self.cloud,mask=self.mask,moi_truong={})
        self.enterContext(patch.dict(ca.ai_cuc_bo._CONNECTION_FAILURES,{},clear=True))
        self.enterContext(patch.object(ca.ai_cuc_bo,'discover_local_models',return_value=dict(
            ma_loi='',model_phat_hien=[dict(id_model='local-DEMO',trang_thai='san_sang')])))
        self.config = Path(tempfile.mkdtemp(prefix='ai_noi_demo_'))/'var/core-demo/ai-noi/ket-noi.local.json'

    def registry(self, conn, *, loai, ma=None):
        p = self.pin
        if loai == 'engine':
            return [dict(id=str(p.engine_id),ma=p.ma_engine,so_phien_ban=p.phien_ban_engine,
                ma_bam_goi=p.ma_bam_goi,ma_adapter=p.ma_adapter,phien_ban_adapter=p.phien_ban_adapter,
                nang_luc=[dict(ma=p.capability,dau_vao=p.dau_vao.ma,dau_ra=p.dau_ra.ma)])]
        if loai == 'contract':
            return [dict(ma=c.ma,phien_ban=c.phien_ban,ma_bam=c.ma_bam,trang_thai='dang_dung')
                for c in (p.dau_vao,p.dau_ra) if c.ma == ma]
        if loai == 'phien_ban_module':
            return [dict(module='mau_demo',so_phien_ban='1.0.0',trang_thai='da_cai',ma_bam_goi='a'*64)]
        raise AssertionError(loai)

    def build(self, *, pins=None, bindings=()):
        ket = Mock()
        ket.doc.return_value = bi_mat.BiMat(b'AI_NOI_CURSOR_DEMO_'*3)
        kt = [e2.KetQuaKiem('KT10','DAT','C0',(),self.pin.ma_engine,self.pin.phien_ban_engine)]
        with patch.object(u,'tao_ung_dung',wraps=u.tao_ung_dung) as factory:
            app = chay_core.dung_ung_dung(self.config,ket=ket,ket_noi=self.connect,
                doc_phien=lambda _: self.session,doc_kt=Mock(return_value=kt),
                dong_ho=lambda: route.g18.NOW,ghim_engine=[self.pin] if pins is None else pins,
                loai_viec=bindings,ho_so_runtime=self.runtime,kenh_module=Mock())
        self.connect.assert_not_called()
        self.runtime.assert_not_called()
        return app, factory.call_args.kwargs['dich_vu_engine']

    def tearDown(self):
        for guard in self.guards:
            guard.assert_not_called()
        self.cloud.tra_loi.assert_not_called()
        self.mask.che.assert_not_called()

    def test_core_khoi_dong_tu_noi_binding_xep_nhan_local_ack_get_xong(self):
        app, service = self.build()
        self.assertIsInstance(service,dv.DichVuEngine)
        self.assertNotIn('loai_viec',app.dieu_phoi_con_thieu)
        self.binding = service._loai_viec[('core','CHAY_THU_HOI_AI',1)]
        self.assertEqual(self.binding.engine_id,self.pin.engine_id)
        response = route.web.wsgi(app,route.PATH,'POST',body=deepcopy(route.BODY))
        self.assertEqual(response['status'],202,response)
        identity = response['body']['ma_luot']
        self.assertEqual(self.conn.events[-1],'commit')
        self.assertEqual(self.conn.rows[identity]['tao_boi'],str(route.g18.USER))
        self.local.assert_not_called()
        self.input, self.ban_giao = Mock(), Mock()
        self.hang = ke.HangViecCore(ctx=dict(ma=self.token,module='core',phap_nhan_id=route.g18.PN,
            hanh_dong='CORE:DU_LIEU:LAP'),dau_vao=self.input,ban_giao=self.ban_giao,
            ghim_loai_viec=self.binding,dich_vu_engine=service)
        # Dùng socket đôi đã có; service.nhan_viec/viec.nhan_engine vẫn chạy thật.
        self.giu = SimpleNamespace(instance_id=self.controller.instance_id)
        with route.EngineChayThuTests.wire(self) as (client,worker):
            lease = client.nhan_viec()
            self.assertEqual(lease.viec_id,self.conn.job)
            sdk = SDKEngine(lease,kenh_core=client)
            ack = ai.xu_ly_viec(sdk,provider=self.portal,kiem_schema=route.d.KiemSchema().kiem)
            self.assertTrue(ack['da_ban_giao'])
            self.assertEqual(ack['ket_qua_id'],identity)
            self.assertEqual(self.conn.events[-1],'commit')
            self.assertTrue(client.ket_thuc(lease,ket_qua_id=identity))
            self.assertIsNone(worker._lease)
        result = route.web.wsgi(app,route.PATH+'/'+identity,'GET')
        self.assertEqual(result['status'],200,result)
        self.assertEqual(result['body']['trang_thai'],'xong')
        self.assertIn('1.000.000 đồng',result['body']['ket_qua']['tra_loi'])
        self.assertEqual(result['body']['ket_qua']['model'],'local-DEMO')
        self.assertEqual(self.conn.jobs[identity],'XONG')
        receive, = [args for sql,args in self.conn.calls if 'loi.nhan_viec_engine(' in sql]
        self.assertEqual(receive[0],'AI_THU_KENH_KHAC_ADMIN')
        self.local.assert_called_once()
        self.input.assert_not_called()
        self.ban_giao.ghi.assert_not_called()

    def test_binding_tuong_minh_duoc_giu_khong_them_trung(self):
        binding = e2.binding_demo(self.pin,module='core',loai='CHAY_THU_HOI_AI')
        _, service = self.build(bindings=[binding])
        self.assertEqual(tuple(service._loai_viec.values()),(binding,))

    def test_khong_co_pin_ai_giu_cua_engine_dong(self):
        app, service = self.build(pins=[])
        self.assertIsNone(service)
        self.assertIn('ghim_engine',app.dieu_phoi_con_thieu)

    def test_pin_chi_kiem_ke_khong_duoc_suy_thanh_binding(self):
        _, service = self.build(pins=[SimpleNamespace(ma_engine='e_hoi_ai',phien_ban_engine='1.0.0')])
        self.assertIsNone(service)

    def test_binding_tuong_minh_khac_engine_bi_tu_choi(self):
        from dataclasses import replace
        binding = e2.binding_demo(self.pin,module='core',loai='CHAY_THU_HOI_AI')
        with self.assertRaises(ValueError):
            self.build(bindings=[replace(binding,engine_id=uuid4())])


if __name__ == '__main__':
    unittest.main()
