from copy import deepcopy
import json
import pytest
from ho_tro_tc_2 import NGU_CANH
from ho_tro_tc_3 import BoCatDoan
from ho_tro_tc_5 import BoPhanLoai
from ho_tro_tc_6 import BoHauKiem
from ho_tro_tc_7 import BoTraLoi


def xuat(bo, ra, *, sua_cap=None, sua_pb=None):
    assert ra['trang_thai'] == 'XONG', ra
    pb = deepcopy(ra['ket_qua']);
    if sua_pb: sua_pb(pb)
    h = pb['ho_so_tra_cuu']
    i = bo.core.giao_viec('tra_cuu.xuat_ket_qua@1', pb, {}, phap_nhan_id='DEMO-P')
    ref = {'tep': h['ho_so'], 'bam': h['bam_ho_so']}
    bo.core.tep_duoc_mo[i] = {ref['tep']['tep_id']}
    cap = {'ma_yeu_cau': h['ma_yeu_cau'], 'tac_vu': h['tac_vu'], 'dau_vao': deepcopy(pb),
           'ngu_canh_core': deepcopy(bo.snapshot(ra)['ngu_canh_core']), 'tep': {r['tep']['tep_id']: deepcopy(r) for r in [*bo.refs, ref]},
           'nguon': deepcopy(bo.nguon_duoc_cap)}
    if sua_cap: sua_cap(cap)
    bo.core.cua.giay_cap[i] = cap
    bo.core.chay(bo.app)
    return bo.core.xem(i)


def bo_cat():
    bo=BoCatDoan(); bo.nhan(); return bo, bo.cat()


def bo_phan_loai():
    bo=BoPhanLoai(); bo.chuan_bi_phan_loai(); return bo, bo.phan_loai()


def bo_hau(tac):
    bo=BoHauKiem(); bo.chuan_bi_hau(tac); bo.local_gia(bo.du_lieu_local()); return bo, bo.hau_kiem()


def bo_tra(bang=True, ai=False):
    bo=BoTraLoi(); bo.nhan_soan(bang=None if bang else [])
    if ai: bo.chuan_bi_soan(); bo.local_soan()
    return bo, bo.soan()


@pytest.mark.parametrize('tao', [bo_cat, bo_phan_loai, lambda: bo_hau('phan_tich_cau_hoi'), lambda: bo_hau('xep_hang_lai'), bo_tra, lambda: bo_tra(False), lambda: bo_tra(ai=True)])
def test_xuat_demodu(tao):
    bo, truoc=tao(); snapshot=bo.snapshot(truoc); ra=xuat(bo, truoc)
    assert ra['trang_thai']=='XONG', ra
    t=ra['ket_qua']['truong']; tep=t['tep_json']; raw=bo.core.doc_tep(tep['tep_id']); out=json.loads(raw)
    assert len(raw)==tep['kich_thuoc'] and tep['mime']=='application/json'
    assert out['ket_qua']==snapshot['ket_qua'] and out['nguon']==snapshot['nguon']
    assert t['tac_vu']==snapshot['tac_vu']
    if t['tac_vu']=='cat_doan': assert t['so_doan']==len(snapshot['ket_qua']['doan'])
    if t['tac_vu']=='xep_hang_lai': assert t['so_ung_vien']==len(snapshot['ket_qua']['xep_hang'])
    if t['tac_vu']=='soan_tra_loi': assert t['nhan']==snapshot['ket_qua']['nhan']


def test_khong_co_quyen():
    bo, ra=bo_cat(); k=xuat(bo, ra, sua_cap=lambda c: c['tep'].clear())
    assert k['trang_thai']=='LOI'


@pytest.mark.parametrize('thay,ma', [
    (lambda h: h.update(giai_doan='da_nhan'), 'TC_SAI_GIAI_DOAN'),
    (lambda h: h.update(tac_vu='sai'), 'TC_SAI_GIAI_DOAN'),
    (lambda h: h['tom_tat'].update(so_doan=999), 'TC_SAI_NGUON'),
    (lambda h: h.update(bam_cau_hinh='sha256:' + '0'*64), 'TC_SAI_NGUON'),
])
def test_phong_bi_sai(thay, ma):
    bo, ra=bo_cat(); k=xuat(bo, ra, sua_pb=lambda pb: thay(pb['ho_so_tra_cuu']))
    assert k['trang_thai']=='LOI' and k['loi']['ma']==ma


def test_nguon_sai():
    bo, ra=bo_cat(); k=xuat(bo, ra, sua_cap=lambda c: c['nguon']['DEMO-NGUON-1'].update(phien_ban_nguon='sai'))
    assert k['trang_thai']=='LOI' and k['loi']['ma']=='TC_SAI_NGUON'


def test_phong_bi_qua_tran():
    bo, ra=bo_cat(); k=xuat(bo, ra, sua_pb=lambda pb: pb['ho_so_tra_cuu'].update(canh_bao=['x'*65536]))
    assert k['trang_thai']=='LOI' and k['loi']['ma']=='TC_QUA_GIOI_HAN'


def test_tai_tep_that_bai_khong_xong(monkeypatch):
    from kho_tri_thuc_sdk.engine import LoiDuongTruyen
    bo, ra=bo_cat()
    def that_bai(*args, **kwargs): raise LoiDuongTruyen('DEMO', http_status=503)
    monkeypatch.setattr(bo.core, '_tai_tep_ra', that_bai)
    k=xuat(bo, ra)
    assert k['trang_thai'] != 'XONG' and k['ket_qua'] is None


def test_huy_khi_tai_khong_xong(monkeypatch):
    bo, ra=bo_cat(); tai=bo.core._tai_tep_ra
    def huy(ma, viec_id, *args):
        k=tai(ma, viec_id, *args); bo.core.huy(viec_id); return k
    monkeypatch.setattr(bo.core, '_tai_tep_ra', huy)
    k=xuat(bo, ra)
    assert k['trang_thai'] != 'XONG' and k['ket_qua'] is None


def test_mau_thuan_giu_hai_ben():
    from test_tc_7 import bo_mau_thuan
    bo=bo_mau_thuan(1); truoc=bo.soan(); ra=xuat(bo, truoc)
    assert ra['trang_thai']=='XONG', ra
    t=ra['ket_qua']['truong']; assert t['co_mau_thuan'] and t['can_duyet'] and t['nhan']=='vang'
    k=json.loads(bo.core.doc_tep(t['tep_json']['tep_id']))['ket_qua']
    assert len(k['mau_thuan'])==2 and {x['gia_tri']['so'] for x in k['mau_thuan']}=={1000000,2000000}
    assert not k['de_nghi_k5']['da_tao_viec']


def test_mat_ack_khong_xong_gia():
    bo, truoc=bo_cat(); bo.core.gay_mat_xac_nhan('tep', 4)
    k=xuat(bo, truoc)
    assert k['trang_thai'] != 'XONG' and k['ket_qua'] is None


def test_snapshot_qua_tran():
    bo, truoc=bo_cat()
    k=xuat(bo, truoc, sua_pb=lambda pb: pb['ho_so_tra_cuu']['ho_so'].update(kich_thuoc=20971521))
    assert k['trang_thai']=='LOI' and k['loi']['ma']=='TC_QUA_GIOI_HAN'
