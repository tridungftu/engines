"""Hợp đồng ngăn và nghiệp vụ MASK-3b; toàn bộ chỉ dữ liệu DEMO."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from threading import Barrier
from types import SimpleNamespace

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu

from e_mask import che_van_ban, tai_nguyen
from e_mask.cau_hinh import doc_cau_hinh
from e_mask.duyet_dinh_danh import DuyetDinhDanh
from e_mask.kho_dinh_danh import KhoDinhDanh
from e_mask.kho_ngan import AnhNgan, BANG, CAC_TIEN_TO, TIEN_TO, bi_danh_moi, khoa_muc
from e_mask.kho_ngan import KHAI_NGAN
from e_mask.ngan import NganBoNho, NganKhongHopLe, NganXungDot, chon_ngan
from ho_tro_ngan import ADMIN, QuyenNganDemo, TEN, VAN_BAN, viec_demo

ROOT = Path(__file__).resolve().parents[2]
GOI = ROOT / 'e_mask/goi/e_mask'


def bam_lf(tep):
    return sha256(tep.read_bytes().replace(b'\r\n', b'\n')).digest()


@pytest.mark.parametrize('ten', ['ngan.py', 'cau_hinh.py'])
def test_so_bam_mau_chung(ten):
    assert bam_lf(ROOT/'_chung/mau-ma'/ten) == bam_lf(GOI/'e_mask'/ten)


@pytest.mark.parametrize('ten', sorted(tai_nguyen.TEN_TAI_NGUYEN))
def test_so_bam_tu_dien_sach(ten):
    assert bam_lf(ROOT/'e_mask/tham-chieu/tu-dien'/ten) == bam_lf(GOI/'e_mask/tu_dien'/ten)


def test_lo_cas_duy_nhat_rollback_va_phan_trang():
    n = NganBoNho([{'bang':'demo', 'khoa':['ma'], 'duy_nhat':[['ten']]}])
    with n.lo() as lo:
        lo.them('demo', {'ma':'1'}, {'ten':'DEMO'})
    cu = n.doc('demo', {'ma':'1'})
    with pytest.raises(NganXungDot):
        with n.lo() as lo:
            lo.sua('demo', {'ma':'1'}, {'ten':'DEMO mới'}, row_version=cu.row_version)
            lo.them('demo', {'ma':'2'}, {'ten':'DEMO mới'})
    assert n.doc('demo', {'ma':'1'}) == cu
    assert n.doc('demo', {'ma':'2'}) is None
    with pytest.raises(NganXungDot):
        with n.lo() as lo:
            lo.xoa('demo', {'ma':'1'}, row_version=cu.row_version+1)
    with pytest.raises(RuntimeError):
        with n.lo() as lo:
            lo.xoa('demo', {'ma':'1'}, row_version=cu.row_version)
            raise RuntimeError('DEMO')
    assert n.doc('demo', {'ma':'1'}) == cu
    with n.lo() as lo:
        lo.them('demo', {'ma':'2'}, {'ten':'DEMO khác'})
    a = n.tim('demo', gioi_han=1)
    assert len(a.danh_sach) == 1 and a.tiep
    assert len(n.tim('demo', gioi_han=1, tiep=a.tiep).danh_sach) == 1


def test_lay_hoac_tao_hai_luong_duy_nhat():
    n = NganBoNho([{'bang':'demo','khoa':['ma'],'duy_nhat':[['ten']]}])
    rao = Barrier(2)
    def ghi(i):
        rao.wait()
        with n.lo() as lo:
            kq = lo.lay_hoac_tao('demo', {'ten':'DEMO'}, {'ma':str(i)})
        assert kq.ban_ghi.gia_tri == kq.gia_tri
        assert kq.row_version > 0
        return kq.da_tao
    with ThreadPoolExecutor(2) as pool:
        assert sorted(pool.map(ghi, (1,2))) == [False, True]
    assert len(n.tim('demo').danh_sach) == 1


def test_pham_vi_phap_nhan_khong_doc_cheo():
    n = NganBoNho([{'bang':'demo','khoa':['ma'],'duy_nhat':[['ten']],'pham_vi':'phap_nhan'}])
    a, b = n.cho_phap_nhan('pn-demo-a'), n.cho_phap_nhan('pn-demo-b')
    with a.lo() as lo:
        lo.them('demo', {'ma':'1'}, {'ten':'DEMO'})
    assert b.doc('demo', {'ma':'1'}) is None and b.tim('demo').danh_sach == []
    with b.lo() as lo:
        lo.them('demo', {'ma':'1'}, {'ten':'DEMO'})
    with pytest.raises(NganKhongHopLe):
        b.doc('demo', {'ma':'1','phap_nhan_id':'pn-demo-a'})
    with pytest.raises(NganKhongHopLe):
        with b.lo() as lo:
            lo.them('demo', {'ma':'2'}, {'ten':'DEMO','phap_nhan_id':'pn-demo-a'})


def test_chon_ngan_va_doc_cau_hinh_mac_dinh(monkeypatch, capsys):
    from e_mask import ngan
    monkeypatch.setattr(ngan, '_DA_CANH_BAO', False)
    app = SimpleNamespace()
    n = chon_ngan(app)
    assert n is chon_ngan(app)
    assert capsys.readouterr().err.count('Đang lưu tạm') == 1
    assert chon_ngan(SimpleNamespace(ngan=n)) is n
    s = {'type':'object', 'properties':{'so':{'type':'integer','default':7}},'additionalProperties':False}
    assert doc_cau_hinh(n,s) is None
    with n.lo() as lo:
        lo.them('cau_hinh', {}, {})
    assert doc_cau_hinh(n,s) == {'so':7}
    assert n.doc('cau_hinh', {}).gia_tri == {}


def test_tien_to_va_junsky_demo():
    assert CAC_TIEN_TO == {'MASKCT','MASKCN','MASKDC','MASKMST','MASKTK','MASKKHAC','MASKTAM'}
    for nhom, t in dict(TIEN_TO, KHAC='MASKKHAC').items():
        assert bi_danh_moi(nhom).startswith('[['+t+'-')
    ma_demo = ['KH-DEMO-001','NCC-DEMO-001','CN-DEMO-001','CT-DEMO-001']
    assert all(not ma.startswith(t) for ma in ma_demo for t in CAC_TIEN_TO)
    for t in CAC_TIEN_TO:
        with pytest.raises(LoiNghiepVu):
            DuyetDinhDanh(NganBoNho(KHAI_NGAN), ADMIN).nhap_demo([{'gia_tri':TEN,'nhom':'CONG_TY','ma_junsky':t+'-DEMO'}])


def ghep(n=None):
    n = n or NganBoNho(KHAI_NGAN)
    q, v = QuyenNganDemo(), viec_demo()
    ctx = q.cap(v.id)
    return n, q, v, ctx, KhoDinhDanh(ngan=n,quyen=q)


def xu_ly(kho):
    tai_nguyen.nap_tu_goi()
    return che_van_ban.che(VAN_BAN, [], kho)


def test_ngan_chot_retry_khong_ghi_tep_va_khong_luu_tai_lieu(tmp_path, monkeypatch):
    n,q,v,ctx,k = ghep()
    monkeypatch.chdir(tmp_path)
    a = k.xu_ly(v,xu_ly)
    b = KhoDinhDanh(ngan=n,quyen=q).xu_ly(v,xu_ly)
    assert a == b
    assert len(n.tim('cho_duyet').danh_sach) == 1
    assert n.tim('cho_duyet').danh_sach[0].gia_tri['so_lan_gap'] == 1
    assert list(tmp_path.iterdir()) == []
    du_lieu = json.dumps({b:[m.gia_tri for m in n.tim(b).danh_sach] for b in BANG}, ensure_ascii=False)
    assert VAN_BAN not in du_lieu and 'van_ban_da_che' not in du_lieu
    v2 = viec_demo('viec-demo-2'); q.cap(v2.id)
    c = k.xu_ly(v2,xu_ly)
    assert c['van_ban_da_che'] != a['van_ban_da_che']  # Yêu cầu khác có bí danh tạm riêng.
    assert n.tim('cho_duyet').danh_sach[0].gia_tri['so_lan_gap'] == 2


def test_hai_snapshot_chot_nguyen_tu_xung_dot():
    n,q,v,ctx,k = ghep()
    v2 = viec_demo('viec-demo-2'); q.cap(v2.id)
    a,b = k.mo_luot(v),k.mo_luot(v2)
    ka,kb = xu_ly(a),xu_ly(b)
    a.chot(ka)
    truoc = {bang:deepcopy(n.tim(bang)) for bang in BANG if bang != 'dau_gap'}
    with pytest.raises(LoiNghiepVu) as e:
        b.chot(kb)
    assert e.value.ma == 'MASK_XUNG_DOT' and e.value.thu_lai_duoc
    assert {bang:n.tim(bang) for bang in truoc} == truoc
    assert k.xu_ly(v2,xu_ly)['van_ban_da_che'] != ka['van_ban_da_che']


def test_chua_ro_khong_mat_khi_ghi_dau_loi(monkeypatch, tmp_path):
    from test_mask_3 import ghep as ghep_cu, xu_ly_demo
    core,_,v,_,k = ghep_cu(tmp_path)
    core.mat_phan_hoi = True
    kho = k.mo_luot(v)
    ghi = kho._ghi_dau
    def loi_ghi(tt):
        if tt == 3:
            raise RuntimeError('Lỗi DEMO ghi dấu')
        return ghi(tt)
    monkeypatch.setattr(kho,'_ghi_dau',loi_ghi)
    with pytest.raises(ChuaRo) as e:
        kho.chot(xu_ly_demo(kho))
    assert e.value.ma_tuong_quan.startswith('mask-') and core.so_chot == 1


def test_trung_alias_khong_ghi_de_gia_tri_goc(monkeypatch):
    from e_mask import kho_qua_core
    from uuid import UUID
    monkeypatch.setattr(kho_qua_core, 'uuid4', lambda: UUID(int=1))
    n,q,v,ctx,k = ghep()
    k.xu_ly(v,xu_ly)
    cu = deepcopy(n.tim('bi_danh_tam'))
    v2=viec_demo('viec-demo-khac'); v2.dau_vao['van_ban']='Công ty DEMO Bình Minh'; q.cap(v2.id)
    def ham(kho):
        return che_van_ban.che(v2.dau_vao['van_ban'],[],kho)
    with pytest.raises(LoiNghiepVu) as e:
        k.xu_ly(v2,ham)
    assert e.value.ma=='MASK_XUNG_DOT' and n.tim('bi_danh_tam')==cu


def test_ngan_chua_ro_sau_lo_chot_doc_lai_khong_dem_lap():
    class NganMatAck(NganBoNho):
        mat_ack = True
        def lo(self):
            ngoai, lo_goc = self, super().lo()
            class LoMatAck:
                co_yeu_cau = False
                def __enter__(self):
                    lo_goc.__enter__()
                    return self
                def them(self, bang, khoa, gia_tri):
                    self.co_yeu_cau |= bang == 'ma_yeu_cau'
                    return lo_goc.them(bang, khoa, gia_tri)
                def __getattr__(self, ten):
                    return getattr(lo_goc, ten)
                def __exit__(self, *doi):
                    kq=lo_goc.__exit__(*doi)
                    if doi[0] is None and ngoai.mat_ack and self.co_yeu_cau:
                        ngoai.mat_ack=False
                        raise ChuaRo('ma-nguon-demo')
                    return kq
            return LoMatAck()
    n,q,v,ctx,k=ghep(NganMatAck(KHAI_NGAN))
    with pytest.raises(ChuaRo):
        k.xu_ly(v,xu_ly)
    assert n.tim('cho_duyet').danh_sach[0].gia_tri['so_lan_gap']==1
    assert k.xu_ly(v,xu_ly)['gui_duoc']
    assert n.tim('cho_duyet').danh_sach[0].gia_tri['so_lan_gap']==1


def test_ban_khai_khop_truong_ngan_da_ghi():
    n,q,v,ctx,k=ghep()
    k.xu_ly(v,xu_ly)
    admin=DuyetDinhDanh(n,ADMIN); muc=admin.danh_sach()[0]
    admin.duyet(muc['gia_tri']['khoa'],muc['row_version'])
    khai=json.loads((GOI/'KHAI-SDK-2.1.json').read_text('utf-8'))
    for bang in khai['ngan_du_lieu']:
        assert bang['pham_vi']=='engine'
        truong={m['ma'] for m in bang['truong']}
        for muc in n.tim(bang['bang']).danh_sach:
            assert set(muc.gia_tri)<=truong, (bang['bang'],set(muc.gia_tri)-truong)
