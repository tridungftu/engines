"""MASK-4/5/6: phong bì, hai handler thật, Admin/vòng đời; chỉ DEMO."""
from copy import deepcopy
from hashlib import sha256
import io
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu, ViecDaHuy
from kho_tri_thuc_sdk.thu import CoreGia

from e_mask import phong_bi, che_van_ban
from e_mask.chay import tao_app
from e_mask.cau_hinh import CauHinhKhongHopLe
from e_mask.duyet_dinh_danh import DuyetDinhDanh
from e_mask.kho_dinh_danh import KhoDinhDanh
from e_mask.kho_ngan import AnhNgan, khoa_muc
from e_mask.kho_ngan import KHAI_NGAN
from e_mask.ngan import NganBoNho, NganKhongHopLe, NganXungDot
from ho_tro_ngan import ADMIN, QuyenNganDemo, TEN, VAN_BAN, ai_demo, viec_demo

ROOT = Path(__file__).resolve().parents[2]
GOI = ROOT / 'e_mask/goi/e_mask'
CHE, MO = 'mask.che_van_ban@1', 'mask.mo_che_van_ban@1'


@pytest.mark.parametrize('ma', ['van_ban_da_che','van_ban_tai_lieu','tra_loi_ai'])
def test_so_schema_chung(ma):
    assert sha256((ROOT/'_chung/contract'/f'{ma}.schema.json').read_bytes()).digest() == sha256((GOI/'e_mask/schemas'/f'{ma}.schema.json').read_bytes()).digest()


@pytest.mark.parametrize('noi_dung', [b'{',b'{"van_ban":"DEMO","van_ban":"x"}',b'{"van_ban":NaN}',b'\xff', b'[]'])
def test_json_sai_khong_loc_ngam(noi_dung):
    v = SimpleNamespace(dau_vao={'loai':'tep','tep':{'tep_id':'demo','mime':'application/json'}},
                        mo_tep=lambda _: io.BytesIO(noi_dung))
    with pytest.raises(LoiNghiepVu) as e:
        phong_bi.doc_che(v)
    assert e.value.ma == 'MASK_DAU_VAO'


def test_gioi_han_utf8_va_noi_dung_long():
    phong_bi.kiem_chuyen_tiep({'demo':'á' * 32760})
    with pytest.raises(LoiNghiepVu) as e:
        phong_bi.kiem_chuyen_tiep({'demo':'á' * 32768})
    assert e.value.ma == 'MASK_QUA_GIOI_HAN'
    phong_bi.kiem_van_ban('a' * 500000)
    with pytest.raises(LoiNghiepVu):
        phong_bi.kiem_van_ban('a' * 500001)
    v = viec_demo(); v.dau_vao = {'loai':'tra_loi_ai','tra_loi_ai':ai_demo('a'*300000,'demo')}
    v.dau_vao['tra_loi_ai']['du_lieu'] = {'demo':'b'*200001}
    with pytest.raises(LoiNghiepVu) as e:
        phong_bi.doc_mo(v)
    assert e.value.ma == 'MASK_QUA_GIOI_HAN'


def test_schema_co_an_toan_khong_chap_nhan_gia():
    dau = {'loai':'van_ban_da_che','van_ban_da_che':dict(phien_ban=1,van_ban='DEMO',ma_yeu_cau='demo',
                                                       con_sot=[],kiem_tien_ngay=True,chuyen_tiep={})}
    assert phong_bi.kiem_loai(dau,'van_ban_da_che')['phien_ban'] == 1
    for k,v in [('con_sot',[{}]),('kiem_tien_ngay',1),('kiem_tien_ngay',False),('phien_ban',True)]:
        hong=deepcopy(dau); hong['van_ban_da_che'][k]=v
        with pytest.raises(LoiNghiepVu):
            phong_bi.kiem_loai(hong,'van_ban_da_che')


def ghep():
    n,q,c = NganBoNho(KHAI_NGAN),QuyenNganDemo(),CoreGia()
    return n,q,c,tao_app(ngan=n,quyen=q)


def che_demo(n,q,c,app):
    v=c.giao_viec(CHE, {'loai':'van_ban','van_ban':VAN_BAN}); ctx=q.cap(v)
    c.chay(app); kq=c.xem(v)
    assert kq['trang_thai']=='XONG', kq
    return v,ctx,kq['ket_qua']['van_ban_da_che']


def mo_demo(n,q,c,app,chu,ma,*,dong=False,du_lieu=None,trich_dan=None):
    ai=ai_demo(chu,ma)
    ai['du_lieu']=du_lieu
    ai['trich_dan']=trich_dan or []
    v=c.giao_viec(MO,{'loai':'tra_loi_ai','tra_loi_ai':ai},{'dong_viec':dong}); q.cap(v,loai='mo_che',ma_yeu_cau=ma)
    c.chay(app)
    return v,c.xem(v)


def test_core_gia_khu_hoi_ai_giu_cau_truc_va_ha_trich_dan():
    n,q,c,app=ghep()
    _,ctx,che=che_demo(n,q,c,app)
    b=che['bi_danh'][0]['bi_danh']
    assert TEN not in json.dumps(che,ensure_ascii=False) and che['chuyen_tiep']=={}
    assert '1.000.000 VND' in che['van_ban'] and '30/10/2026' in che['van_ban']
    _,mo=mo_demo(n,q,c,app,che['van_ban']+' nội dung AI thêm.',ctx.ma_yeu_cau,dong=True,
                 du_lieu={'demo':[b,7,True,None,{'ngay':'2026-10-30','tien':{'so':1000000,'tien_te':'VND'}}]},
                 trich_dan=[{'cau':b,'bat_dau':0,'ket_thuc':len(b)}])
    assert mo['trang_thai']=='XONG',mo
    m=mo['ket_qua']['truong']; ai=json.loads(m['tra_loi_ai_da_mo_json'])
    assert m['van_ban_da_mo_che']==VAN_BAN+' nội dung AI thêm.' and m['mo_day_du']
    assert ai['du_lieu']['demo']==[TEN,7,True,None,{'ngay':'2026-10-30','tien':{'so':1000000,'tien_te':'VND'}}]
    assert ai['trich_dan'][0]['cau']==TEN and ai['trich_dan'][0]['can_kiem_lai']
    assert ai['trich_dan'][0]['ket_thuc']==len(b) and ai['kiem_trich_dan']['dat'] is False
    assert m['trang_thai_ma_yeu_cau']=='DA_DONG'
    _,moi=mo_demo(n,q,c,app,b,ctx.ma_yeu_cau)
    assert moi['trang_thai']=='LOI' and moi['loi']['ma']=='MASK_MA_YEU_CAU'


def test_ai_bi_danh_la_trong_du_lieu_khong_dong():
    n,q,c,app=ghep(); _,ctx,che=che_demo(n,q,c,app)
    _,mo=mo_demo(n,q,c,app,che['van_ban'],ctx.ma_yeu_cau,dong=True,du_lieu={'demo':['[[MASKCT-khong-co-DEMO]]']})
    m=mo['ket_qua']['truong']
    assert not m['mo_day_du'] and m['trang_thai_ma_yeu_cau']=='DANG_XU_LY'
    assert json.loads(m['bi_danh_khong_ro_json'])[0]['duong_truong']==['du_lieu','demo',0]


@pytest.mark.parametrize('truong', ['module','nguoi_gui','tai_lieu','vung'])
def test_sai_nguon_quyen_khong_mo(truong):
    n,q,c,app=ghep(); _,ctx,che=che_demo(n,q,c,app)
    setattr(q,truong,'THAT' if truong=='vung' else 'sai-demo')
    _,kq=mo_demo(n,q,c,app,che['van_ban'],ctx.ma_yeu_cau)
    assert kq['trang_thai']=='LOI' and kq['loi']['ma']=='MASK_MA_YEU_CAU'


def test_json_mau1_mau3_va_ocr():
    n,q,c,app=ghep()
    raw=json.dumps({'van_ban':VAN_BAN,'dinh_danh_da_biet':[{'gia_tri':TEN,'nhom':'CONG_TY'}]}).encode()
    t=c.them_tep('mau-demo.json',raw,'application/json')
    v=c.giao_viec(CHE,{'loai':'tep','tep':t}); ctx=q.cap(v); c.chay(app)
    assert c.xem(v)['trang_thai']=='XONG',c.xem(v)
    che=c.xem(v)['ket_qua']['van_ban_da_che']
    raw=json.dumps({'van_ban':che['van_ban'],'ma_yeu_cau':ctx.ma_yeu_cau,'dong_viec':True}).encode()
    t=c.them_tep('mo-demo.json',raw,'application/json')
    v=c.giao_viec(MO,{'loai':'tep','tep':t},{'dong_viec':False}); q.cap(v,loai='mo_che',ma_yeu_cau=ctx.ma_yeu_cau); c.chay(app)
    assert c.xem(v)['ket_qua']['truong']['van_ban_da_mo_che']==VAN_BAN
    assert c.xem(v)['ket_qua']['truong']['trang_thai_ma_yeu_cau']=='DA_DONG'
    ocr=dict(phien_ban=1,van_ban=VAN_BAN,trang=[],so_trang=0,nguon_doc='tesseract',ly_do_chuyen_nguon=None,
             phien_ban_engine='e_ocr 1.0.0',bam_dau_vao='sha256:'+'0'*64,canh_bao=[])
    v=c.giao_viec(CHE,{'loai':'van_ban_tai_lieu','van_ban_tai_lieu':ocr}); q.cap(v); c.chay(app)
    assert c.xem(v)['trang_thai']=='XONG'
    assert 'trang' not in c.xem(v)['ket_qua']['van_ban_da_che']


def test_duyet_tu_choi_don_hai_yeu_cau_va_giao_lai():
    n,q,c,app=ghep()
    a,ctx,che=che_demo(n,q,c,app)
    _,ctx2,_=che_demo(n,q,c,app)
    admin=DuyetDinhDanh(n,ADMIN)
    muc=admin.danh_sach()[0]; alias=che['bi_danh'][0]['bi_danh']
    ma=admin.duyet(muc['gia_tri']['khoa'],muc['row_version'])
    assert ma.startswith('[[MASKCT-') and admin.danh_sach()==[] and admin.don()==0
    _,mo=mo_demo(n,q,c,app,alias,ctx.ma_yeu_cau,dong=True)
    assert mo['ket_qua']['truong']['van_ban_da_mo_che']==TEN and admin.don()==0
    admin.dong(ctx2.ma_yeu_cau)
    assert admin.don()==1
    assert 'bi_danh_tam' not in n.tim('dinh_danh').danh_sach[0].gia_tri
    # Giao lại lượt che vẫn trả đúng bí danh tạm ban đầu, không tăng đếm.
    with c._lock:
        c._viec[a]['trang_thai']='CHO'; c._hang.append(a)
    c.chay(app)
    assert c.xem(a)['ket_qua']['van_ban_da_che']==che
    # Cụm bị từ chối còn mở được khi yêu cầu vẫn xử lý.
    n,q,c,app=ghep(); _,ctx,che=che_demo(n,q,c,app)
    admin=DuyetDinhDanh(n,ADMIN); muc=admin.danh_sach()[0]
    admin.tu_choi(muc['gia_tri']['khoa'],muc['row_version'])
    assert admin.don()==0 and not admin.danh_sach()
    _,mo=mo_demo(n,q,c,app,che['van_ban'],ctx.ma_yeu_cau,dong=True)
    assert mo['ket_qua']['truong']['van_ban_da_mo_che']==VAN_BAN and admin.don()==1


def test_admin_quyen_cas_nhap_lap_va_don_tranh_chot():
    n,q,c,app=ghep(); _,_,_=che_demo(n,q,c,app)
    admin=DuyetDinhDanh(n,ADMIN); muc=admin.danh_sach()[0]
    with pytest.raises(LoiNghiepVu) as e:
        DuyetDinhDanh(n,None).danh_sach()
    assert e.value.ma=='MASK_KHONG_CO_QUYEN'
    with pytest.raises(LoiNghiepVu) as e:
        admin.duyet(muc['gia_tri']['khoa'],muc['row_version']+1)
    assert e.value.ma=='MASK_XUNG_DOT'
    # Snapshot dọn cũ không được ghi sau khi một lượt mới thêm tham chiếu.
    anh=AnhNgan(n,'DEMO')
    che_demo(n,q,c,app)
    with pytest.raises(LoiNghiepVu) as e:
        anh.chot()
    assert e.value.ma=='MASK_XUNG_DOT'
    ds=[{'gia_tri':'Công ty DEMO Bình Minh','nhom':'CONG_TY','ma_junsky':'KH-DEMO-002'}]
    assert admin.nhap_demo(ds)['so_dong_them']==1
    assert n.tim('dinh_danh').danh_sach==[]
    admin.nhap_demo(ds,thuc_hien=True)
    assert admin.nhap_demo(ds,thuc_hien=True)['so_dong_them']==0


@pytest.mark.parametrize('thao_tac', ['ket_qua','ket_thuc'])
def test_sdk_mat_ack_giao_lai_khong_dem_lap(thao_tac):
    n,q,c,app=ghep()
    c.gay_mat_xac_nhan(thao_tac,so_lan=1)
    v,_,che=che_demo(n,q,c,app)
    with c._lock:
        c._viec[v]['trang_thai']='CHO'; c._hang.append(v)
    c.chay(tao_app(ngan=n,quyen=q))
    assert c.xem(v)['ket_qua']['van_ban_da_che']==che
    assert n.tim('cho_duyet').danh_sach[0].gia_tri['so_lan_gap']==1


def test_huy_truoc_chot_khong_ghi_nghiep_vu():
    n,q=NganBoNho(KHAI_NGAN),QuyenNganDemo(); v=viec_demo(); q.cap(v.id)
    def ham(kho):
        from e_mask import tai_nguyen
        tai_nguyen.nap_tu_goi()
        kq=che_van_ban.che(VAN_BAN,[],kho)
        v.kiem_huy=lambda: (_ for _ in ()).throw(ViecDaHuy())
        return kq
    with pytest.raises(ViecDaHuy):
        KhoDinhDanh(ngan=n,quyen=q).xu_ly(v,ham)
    assert n.tim('cho_duyet').danh_sach==[] and n.tim('ma_yeu_cau').danh_sach==[]


def test_moi_vi_du_bang_core_gia():
    from chay_demo import chay
    ds=chay()
    assert len(ds)==2 and all(m['trang_thai']=='XONG' for m in ds),ds


@pytest.mark.parametrize('loai', ['van_ban','van_ban_tai_lieu','tep'])
def test_bien_noi_dung_handler(loai):
    for so,dat in [(500000,True),(500001,False)]:
        v=viec_demo(); chu='a' * so
        if loai=='van_ban':
            v.dau_vao={'loai':loai,loai:chu}
        elif loai=='tep':
            v.dau_vao={'loai':loai,'tep':{'tep_id':'demo','mime':'application/json'}}
            v.mo_tep=lambda _:io.BytesIO(json.dumps({'van_ban':chu}).encode())
        else:
            v.dau_vao={'loai':loai,loai:dict(phien_ban=1,van_ban=chu,trang=[],so_trang=0,nguon_doc='tesseract',
                ly_do_chuyen_nguon=None,phien_ban_engine='e_ocr 1.0.0',bam_dau_vao='sha256:'+'0'*64,canh_bao=[])}
        if dat:
            assert len(phong_bi.doc_che(v)[0])==so
        else:
            with pytest.raises(LoiNghiepVu) as e:
                phong_bi.doc_che(v)
            assert e.value.ma=='MASK_QUA_GIOI_HAN'


def test_nhieu_cum_vuot_100_lenh_tu_choi_toan_bo():
    from e_mask.kho_ngan import BANG
    n=NganBoNho(KHAI_NGAN); anh=AnhNgan(n,'DEMO')
    for i in range(100):
        anh.dat('cho_duyet',f'demo-{i}',{'gia_tri':f'DEMO {i}'})
    with pytest.raises(LoiNghiepVu) as e:
        anh.chot()
    assert e.value.ma=='MASK_QUA_GIOI_HAN'
    assert n.tim('cho_duyet').danh_sach==[]


def test_replay_khong_am_tham_doi_ket_qua_da_chot():
    from e_mask import tai_nguyen
    n,q=NganBoNho(KHAI_NGAN),QuyenNganDemo(); v=viec_demo(); q.cap(v.id)
    k=KhoDinhDanh(ngan=n,quyen=q)
    def ham(kho):
        tai_nguyen.nap_tu_goi()
        return che_van_ban.che(VAN_BAN,[],kho)
    k.xu_ly(v,ham)
    def ham_doi(kho):
        kq=ham(kho); kq['so_cho_thay']+=1
        return kq
    with pytest.raises(LoiNghiepVu) as e:
        k.xu_ly(v,ham_doi)
    assert e.value.ma=='MASK_XUNG_DOT'


def test_app_tu_khai_bao_ngan_ram_va_giu_ngan_duoc_cap():
    q,c=QuyenNganDemo(),CoreGia()
    app=tao_app(quyen=q)
    n=app.ngan
    che_demo(n,q,c,app)
    assert n.tim('cho_duyet').danh_sach[0].gia_tri['so_lan_gap']==1
    assert tao_app(ngan=n,quyen=q).ngan is n


@pytest.mark.parametrize('loai_loi', [NganXungDot, NganKhongHopLe, CauHinhKhongHopLe])
@pytest.mark.parametrize('nang_luc', [CHE, MO])
def test_loi_cong_chung_thanh_loi_nghiep_vu(monkeypatch, loai_loi, nang_luc):
    n,q,c,app=ghep()
    def loi_demo(*args, **kw):
        raise loai_loi()
    monkeypatch.setattr(KhoDinhDanh,'xu_ly',loi_demo)
    dau=({'loai':'van_ban','van_ban':VAN_BAN} if nang_luc==CHE else
         {'loai':'tra_loi_ai','tra_loi_ai':ai_demo('DEMO','ma-DEMO')})
    kq=c.chay_thu(app,nang_luc,dau)
    assert kq['trang_thai']=='LOI' and kq['ket_qua'] is None
    assert kq['loi']['ma']==loai_loi.ma
    assert kq['loi']['thong_diep']==loai_loi.thong_diep
    assert kq['loi']['thu_lai_duoc']==loai_loi.thu_lai_duoc


def test_xoa_truong_van_chiu_cas_va_tran_lo():
    n=NganBoNho(KHAI_NGAN)
    with n.lo() as lo:
        for i in range(50):
            lo.them('dau_gap',khoa_muc('DEMO',f'demo-{i}'),{'so':i,'cu':True})
    anh=AnhNgan(n,'DEMO')
    for i in range(50):
        anh.dat('dau_gap',f'demo-{i}',{'so':i})
    with pytest.raises(LoiNghiepVu) as e:
        anh.chot()
    assert e.value.ma=='MASK_QUA_GIOI_HAN'
    assert all(m.gia_tri['cu'] for m in n.tim('dau_gap',loc={'cu':True}).danh_sach)
    del anh.moi['dau_gap']['demo-49']
    anh.chot()  # 49 cặp xóa/thêm + 1 xóa + 1 CAS = 100 lệnh.
    assert not n.tim('dau_gap',loc={'cu':True}).danh_sach
    assert n.doc('dau_gap',khoa_muc('DEMO','demo-49')) is None
    with pytest.raises(LoiNghiepVu) as e:
        anh.chot()
    assert e.value.ma=='MASK_XUNG_DOT'


def test_loi_ngan_khi_doc_snapshot_khong_bi_mat_ma():
    class NganLoi(NganBoNho):
        def tim(self, *args, **kw):
            raise NganKhongHopLe()
    q,c=QuyenNganDemo(),CoreGia()
    app=tao_app(ngan=NganLoi(KHAI_NGAN),quyen=q)
    v=c.giao_viec(CHE,{'loai':'van_ban','van_ban':VAN_BAN}); q.cap(v)
    c.chay(app)
    kq=c.xem(v)
    assert kq['trang_thai']=='LOI' and kq['ket_qua'] is None
    assert kq['loi']['ma']=='NGAN_KHONG_HOP_LE'
