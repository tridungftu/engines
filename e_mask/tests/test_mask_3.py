"""MASK-3: CoreGia và port kho/quyền giả; chỉ DEMO, không chứng minh độ bền."""
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import json
import multiprocessing
from pathlib import Path
from types import SimpleNamespace
import sys
from uuid import UUID

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, Engine, LoiNghiepVu, ViecDaHuy
from kho_tri_thuc_sdk.thu import CoreGia

GOI = Path(__file__).resolve().parents[1] / 'goi/e_mask'
sys.path.insert(0, str(GOI))
from e_mask import che_van_ban, kho_qua_core, tai_nguyen
from e_mask.kho_dinh_danh import KhoDinhDanh
from e_mask.kho_qua_core import KhoQuaCore
from e_mask.kho_tam import KhoTam
from e_mask.quyen_yeu_cau import NguCanhTinCay, loi_kho
from ho_tro_core_gia import KhoCoreGia, MayKhoGia, QuyenCoreGia

TEN = 'Công ty DEMO Ánh Dương'
VAN_BAN = TEN + '; 1.000.000 VND ngày 30/10/2026.'
CHE, MO = 'mask.che_van_ban@1', 'mask.mo_che_van_ban@1'
VECTOR = json.loads((Path(__file__).resolve().parents[1] / 'ma-nguon/tests/vector_kho_luot.json').read_text('utf-8'))


def viec_demo(ma='viec-demo', *, buoc=1, van_ban=VAN_BAN, tham_so=None):
    return SimpleNamespace(id=ma, ngu_canh={'viec_id': ma, 'buoc': buoc, 'phap_nhan_id': 'pn-demo'},
                           dau_vao={'loai': 'van_ban', 'van_ban': van_ban}, tham_so=tham_so or {},
                           kiem_huy=lambda: None)


def ghep(tmp_path, *, core=None, quyen=None, ma='viec-demo'):
    core = core or KhoCoreGia()
    quyen = quyen or QuyenCoreGia(core)
    v = viec_demo(ma)
    ctx = quyen.cap(v.id)
    lop = KhoDinhDanh(goi_kho=core.port(quyen), quyen=quyen, kho_tam=KhoTam(tmp_path))
    return core, quyen, v, ctx, lop


def xu_ly_demo(kho):
    """Dùng protocol Kho nguyên bản; nhật ký không phải log."""
    with kho.giao_dich():
        ma = kho.tao_yeu_cau()
        muc = kho.tra_bi_danh(che_van_ban.chuan_hoa(TEN))
        if muc is None:
            muc, _ = kho.ghi_cho_duyet(TEN, 'CONG_TY', kho.cap_bi_danh_tam(), ma)
        for _ in range(3):
            kho.ghi_nhan_gap_lai(ma, che_van_ban.chuan_hoa(TEN), muc['nhom'])
        kho.ghi_bi_danh_da_dung(ma, [muc['bi_danh']] * 2)
    return dict(gui_duoc=True, con_sot=[], kiem_tien_ngay=True, van_ban_da_che=muc['bi_danh'])


def khong_duoc_chay(kho):
    raise AssertionError('Lượt đã nhận/chốt không được chạy lại nghiệp vụ.')


@pytest.mark.parametrize('ca', VECTOR['cac_ca'], ids=lambda ca: ca['ma'])
def test_toan_bo_vector_kho_luot(tmp_path, monkeypatch, ca):
    snap = deepcopy(VECTOR['snapshot_mac_dinh'])
    snap.update(deepcopy(ca['snapshot']))
    goc = deepcopy(snap)
    cac_goi = []
    ctx = NguCanhTinCay(VECTOR['ma_yeu_cau'], VECTOR['ma_luot'], 'phien-demo',
                        'module-demo', 'nguoi-demo', 'tai-lieu-demo', 'DEMO')
    quyen = SimpleNamespace(xac_minh=lambda *a, **kw: ctx)
    def port(thao_tac, **payload):
        cac_goi.append((thao_tac, deepcopy(payload)))
        return snap if thao_tac == 'snapshot_luot' else payload['ket_qua']
    kho = KhoQuaCore(goi_kho=port, quyen=quyen, viec=viec_demo(), loai=ca['loai'],
                     ma_yeu_cau=ctx.ma_yeu_cau if ca['loai'] == 'mo_che' else None,
                     bam_dau_vao=sha256(b'DEMO').hexdigest(), kho_tam=KhoTam(tmp_path))
    monkeypatch.setattr(kho_qua_core, 'uuid4', lambda: UUID(VECTOR['uuid_cap']))
    with kho.giao_dich():
        for buoc in ca['thao_tac']:
            kq = getattr(kho, buoc['goi'])(*buoc['doi'])
            assert (list(kq) if isinstance(kq, tuple) else kq) == buoc['ket_qua'], buoc['goi']
    assert len(cac_goi) == 1
    assert kho.nhat_ky == ca['nhat_ky']
    ban_sao = kho.nhat_ky
    ban_sao['cum'].append({'gia_tri': 'DEMO thay bản sao'})
    assert kho.nhat_ky == ca['nhat_ky']
    ket_qua = deepcopy(ca['ket_qua_chot'])
    mong_doi = dict(ket_qua, ma_yeu_cau=ctx.ma_yeu_cau, ma_luot=ctx.ma_luot)
    assert kho.chot(ket_qua) == mong_doi
    assert ket_qua == ca['ket_qua_chot']
    assert cac_goi[-1] == ('chot_luot', dict(ma_yeu_cau=ctx.ma_yeu_cau, ma_luot=ctx.ma_luot,
                                          loai=ca['loai'], phien_ban=goc['phien_ban'],
                                          nhat_ky=ca['nhat_ky_chot'], ket_qua=mong_doi))
    assert snap == goc and kho.nhat_ky == ca['nhat_ky']


@pytest.mark.parametrize('hong', ['thieu_trang_thai', 'thieu_yeu_cau', 'cum_cho_sai_nhom',
                                 'cum_cho_lo_ten', 'trung_gia_tri', 'trung_bi_danh'])
def test_snapshot_hong_tu_choi_truoc_su_dung(tmp_path, hong):
    core, quyen, v, _, _ = ghep(tmp_path)
    snap = deepcopy(VECTOR['snapshot_mac_dinh'])
    muc = dict(gia_tri=TEN, nhom='CONG_TY', bi_danh='[[KH-DEMO-01]]', nguon='chinh_thuc')
    if hong == 'thieu_trang_thai':
        del snap['da_chot']
    elif hong == 'thieu_yeu_cau':
        del snap['yeu_cau']
    elif hong.startswith('cum_cho'):
        cho = dict(nhom='KHONG_CO' if hong.endswith('nhom') else 'CONG_TY',
                   bi_danh='[[MASKTAM-DEMO]]', nguon='tam')
        if hong.endswith('ten'):
            cho['gia_tri'] = TEN
        snap['cum_cho_toan_vung'] = {'f' * 64: cho}
    else:
        snap['danh_muc'] = [muc, dict(muc, gia_tri=TEN.upper() if hong == 'trung_gia_tri' else 'Công ty DEMO Khác')]
    lop = KhoDinhDanh(goi_kho=lambda *a, **kw: snap, quyen=quyen, kho_tam=KhoTam(tmp_path))
    with pytest.raises(LoiNghiepVu) as exc:
        lop.mo_luot(v)
    assert exc.value.ma == 'MASK_KHO_LOI' and TEN not in str(exc.value)


def test_mac_dinh_khong_co_kho_hoac_danh_tinh_tu_khai(tmp_path):
    v = viec_demo(tham_so={'module': 'module-demo', 'nguoi_gui': 'nguoi-demo'})
    v.ngu_canh.update(module='module-demo', nguoi_gui='nguoi-demo')
    for lop, ma in ((KhoDinhDanh(), 'MASK_KHO_CHUA_NOI'),
                    (KhoDinhDanh(goi_kho=lambda *a, **kw: {}, kho_tam=KhoTam(tmp_path)),
                     'MASK_NGU_CANH_CHUA_XAC_MINH')):
        with pytest.raises(LoiNghiepVu) as exc:
            lop.xu_ly(v, khong_duoc_chay)
        assert exc.value.ma == ma


def test_rollback_giao_dich_khong_the_chot(tmp_path):
    core, _, v, _, lop = ghep(tmp_path)
    kho = lop.mo_luot(v)
    with pytest.raises(RuntimeError):
        with kho.giao_dich():
            ma = kho.tao_yeu_cau()
            kho.ghi_cho_duyet(TEN, 'CONG_TY', kho.cap_bi_danh_tam(), ma)
            raise RuntimeError('Lỗi DEMO trong giao dịch.')
    with pytest.raises(LoiNghiepVu):
        kho.chot({'gui_duoc': True})
    assert core.bang['DEMO']['yeu_cau'] == {} and core.bang['DEMO']['cho_duyet'] == {}
    assert len(core.cac_goi) == 1
    assert TEN not in repr(kho)


@pytest.mark.parametrize('moc', ['alias', 'dem', 'hang_cho', 'tham_chieu', 'yeu_cau', 'luot'])
def test_chot_loi_giua_chung_rollback_toan_bo(tmp_path, moc):
    core, _, v, _, lop = ghep(tmp_path)
    truoc = deepcopy(core.bang)
    core.loi_sau = moc
    with pytest.raises(LoiNghiepVu) as exc:
        lop.xu_ly(v, xu_ly_demo)
    assert exc.value.ma == 'MASK_KHO_LOI'
    assert core.bang == truoc and core.so_chot == 0
    core.loi_sau = None
    lop.xu_ly(v, xu_ly_demo)
    assert core.so_chot == 1
    assert core.bang['DEMO']['cho_duyet'][che_van_ban.chuan_hoa(TEN)]['so_lan_gap'] == 1


def test_gap_lai_retry_khoi_dong_lai_khong_cap_dem_moi(tmp_path, monkeypatch):
    core, quyen, v, ctx, lop = ghep(tmp_path)
    dau = lop.xu_ly(v, xu_ly_demo)
    truoc = deepcopy(core.bang)
    v.lan_thu = 100
    v.ngu_canh['phap_nhan_id'] = 'pn-demo-khac'
    monkeypatch.setattr(kho_qua_core, 'uuid4', lambda: (_ for _ in ()).throw(AssertionError('Không cấp lại.')))
    lop_moi = KhoDinhDanh(goi_kho=core.port(quyen), quyen=quyen, kho_tam=KhoTam(tmp_path))
    assert lop_moi.xu_ly(v, khong_duoc_chay) == dau
    assert core.bang == truoc and core.so_chot == 1
    assert core.cac_goi[-2][0] == 'snapshot_luot' and core.cac_goi[-1][1]['nhat_ky'] is None
    monkeypatch.undo()
    v2 = viec_demo('viec-demo-khac')
    ctx2 = quyen.cap(v2.id)
    sau = lop_moi.xu_ly(v2, xu_ly_demo)
    assert sau['van_ban_da_che'] == dau['van_ban_da_che']
    assert sau['ma_yeu_cau'] != ctx.ma_yeu_cau
    dl = core.bang['DEMO']
    assert len(dl['cho_duyet']) == 1 and dl['cho_duyet'][che_van_ban.chuan_hoa(TEN)]['so_lan_gap'] == 2
    for ma in (ctx.ma_yeu_cau, ctx2.ma_yeu_cau):
        assert dl['yeu_cau'][ma]['bi_danh_tam_da_dung'] == {che_van_ban.chuan_bi_danh(dau['van_ban_da_che'])}


def test_hai_snapshot_tranh_chot_xung_dot_thu_lai(tmp_path):
    core, quyen, v, _, lop = ghep(tmp_path)
    v2 = viec_demo('viec-demo-2')
    quyen.cap(v2.id)
    a, b = lop.mo_luot(v), lop.mo_luot(v2)
    ka, kb = xu_ly_demo(a), xu_ly_demo(b)
    a.chot(ka)
    truoc = deepcopy(core.bang)
    with pytest.raises(LoiNghiepVu) as exc:
        b.chot(kb)
    assert exc.value.ma == 'MASK_XUNG_DOT' and exc.value.thu_lai_duoc
    assert core.bang == truoc
    sau = lop.xu_ly(v2, xu_ly_demo)
    assert sau['van_ban_da_che'] == ka['van_ban_da_che']
    assert len(core.bang['DEMO']['cho_duyet']) == 1


def ghep_tien_trinh(chung, hang, thu_muc):
    def doc(kq):
        dat, gia_tri = kq
        if not dat:
            raise loi_kho(gia_tri)
        return gia_tri
    quyen = SimpleNamespace(xac_minh=lambda viec, **doi:
                            doc(chung.xac_minh(hang, viec.id, viec.ngu_canh['buoc'], **doi)))
    return KhoDinhDanh(goi_kho=lambda thao_tac, **p: doc(chung.goi(hang, thao_tac, **p)),
                       quyen=quyen, kho_tam=KhoTam(thu_muc))


def tranh_chot(chung, hang, thu_muc, hang_rao, tra):
    lop = ghep_tien_trinh(chung, hang, thu_muc)
    kho = lop.mo_luot(viec_demo(f'viec-demo-{hang}'))
    kq = xu_ly_demo(kho)
    hang_rao.wait(10)
    try:
        kho.chot(kq)
        tra.put((hang, 'XONG'))
    except LoiNghiepVu as exc:
        tra.put((hang, exc.ma))


def test_hai_tien_trinh_tranh_chot_cung_ben_kho_gia(tmp_path):
    ctx = multiprocessing.get_context('spawn')
    with MayKhoGia(ctx=ctx) as may:
        chung = may.kho()
        hang_rao, tra = ctx.Barrier(2), ctx.Queue()
        cac_tien_trinh = [ctx.Process(target=tranh_chot, args=(chung, i, str(tmp_path), hang_rao, tra))
                         for i in range(2)]
        for p in cac_tien_trinh:
            p.start()
        ket_qua = [tra.get(timeout=20) for _ in range(2)]
        for p in cac_tien_trinh:
            p.join(10)
            assert not p.is_alive() and p.exitcode == 0
        assert {ma for _, ma in ket_qua} == {'XONG', 'MASK_XUNG_DOT'}
        bang, so_chot = chung.xem()
        dl = bang['DEMO']
        assert so_chot == 1 and len(dl['cho_duyet']) == len(dl['yeu_cau']) == len(dl['luot']) == 1
        assert dl['cho_duyet'][che_van_ban.chuan_hoa(TEN)]['so_lan_gap'] == 1
        hang = next(i for i, ma in ket_qua if ma == 'MASK_XUNG_DOT')
        ghep_tien_trinh(chung, hang, tmp_path).xu_ly(viec_demo(f'viec-demo-{hang}'), xu_ly_demo)
        bang, so_chot = chung.xem()
        assert so_chot == 2 and len(bang['DEMO']['cho_duyet']) == 1
        assert bang['DEMO']['cho_duyet'][che_van_ban.chuan_hoa(TEN)]['so_lan_gap'] == 2


def test_bang_chung_khac_module_phap_nhan_va_mo_bi_danh_chua_tham_chieu(tmp_path):
    core, _, v, _, lop = ghep(tmp_path)
    kq_a = lop.xu_ly(v, xu_ly_demo)
    quyen_b = QuyenCoreGia(core, phien='phien-demo-b', module='module-demo-b',
                           nguoi_gui='nguoi-demo-b', tai_lieu='tai-lieu-demo-b')
    v_b = viec_demo('viec-demo-b', van_ban='nội dung DEMO')
    v_b.ngu_canh['phap_nhan_id'] = 'pn-demo-b'
    ctx_b = quyen_b.cap(v_b.id)
    lop_b = KhoDinhDanh(goi_kho=core.port(quyen_b), quyen=quyen_b, kho_tam=KhoTam(tmp_path))
    def khong_bi_danh(kho):
        with kho.giao_dich():
            kho.tao_yeu_cau()
        return dict(gui_duoc=True, con_sot=[], kiem_tien_ngay=True, van_ban_da_che='nội dung DEMO')
    lop_b.xu_ly(v_b, khong_bi_danh)
    assert core.bang['DEMO']['yeu_cau'][ctx_b.ma_yeu_cau]['bi_danh_tam_da_dung'] == set()
    v_mo = viec_demo('mo-demo-b', van_ban=kq_a['van_ban_da_che'])
    quyen_b.cap(v_mo.id, loai='mo_che', ma_yeu_cau=ctx_b.ma_yeu_cau)
    mo = lop_b.xu_ly(v_mo, lambda kho: che_van_ban.mo_che(kq_a['van_ban_da_che'], ctx_b.ma_yeu_cau, kho),
                     loai='mo_che', ma_yeu_cau=ctx_b.ma_yeu_cau)
    assert mo['van_ban_da_mo_che'] == TEN and mo['mo_day_du']
    assert len(core.bang['DEMO']['cho_duyet']) == 1
    assert core.bang['DEMO']['yeu_cau'][ctx_b.ma_yeu_cau]['bi_danh_tam_da_dung']
    assert core.bang['THAT']['yeu_cau'] == {} and core.bang['THAT']['cho_duyet'] == {}


@pytest.mark.parametrize('truong,gia_tri', [('module', 'module-demo-sai'), ('nguoi_gui', 'nguoi-demo-sai'),
                                         ('tai_lieu', 'tai-lieu-demo-sai'), ('vung', 'THAT')])
def test_sai_module_nguoi_tai_lieu_vung_khong_mo(tmp_path, truong, gia_tri):
    core, _, v, ctx, lop = ghep(tmp_path)
    lop.xu_ly(v, xu_ly_demo)
    doi = {truong: gia_tri}
    quyen = QuyenCoreGia(core, **doi)
    v2 = viec_demo('mo-demo-sai')
    quyen.cap(v2.id, loai='mo_che', ma_yeu_cau=ctx.ma_yeu_cau)
    sai = KhoDinhDanh(goi_kho=core.port(quyen), quyen=quyen, kho_tam=KhoTam(tmp_path))
    truoc = deepcopy(core.bang)
    with pytest.raises(LoiNghiepVu) as exc:
        sai.xu_ly(v2, khong_duoc_chay, loai='mo_che', ma_yeu_cau=ctx.ma_yeu_cau)
    assert exc.value.ma == 'MASK_MA_YEU_CAU'
    assert core.bang == truoc


@pytest.mark.parametrize('thao_tac', ['snapshot', 'chot', 'doc_lai'])
def test_kiem_quyen_lai_tung_cua(tmp_path, thao_tac):
    core, quyen, v, _, lop = ghep(tmp_path)
    if thao_tac == 'doc_lai':
        lop.xu_ly(v, xu_ly_demo)
    kho = None if thao_tac == 'snapshot' else lop.mo_luot(v)
    ket_qua = xu_ly_demo(kho) if thao_tac == 'chot' else None
    truoc = deepcopy(core.bang)
    quyen.thu_hoi = True
    with pytest.raises(LoiNghiepVu) as exc:
        if kho is None:
            lop.mo_luot(v)
        else:
            kho.chot(ket_qua)
    assert exc.value.ma == 'MASK_MA_YEU_CAU' and core.bang == truoc


def test_port_kho_tu_kiem_quyen_ngay_ca_nguon_quyen_cu(tmp_path, monkeypatch):
    core, quyen, v, ctx, lop = ghep(tmp_path)
    kho = lop.mo_luot(v)
    ket_qua = xu_ly_demo(kho)
    quyen.thu_hoi = True
    monkeypatch.setattr(quyen, 'xac_minh', lambda *a, **kw: ctx)
    with pytest.raises(LoiNghiepVu) as exc:
        kho.chot(ket_qua)
    assert exc.value.ma == 'MASK_MA_YEU_CAU' and core.so_chot == 0


def test_ngu_canh_doi_giua_luot_bi_tu_choi(tmp_path, monkeypatch):
    _, quyen, v, ctx, lop = ghep(tmp_path)
    kho = lop.mo_luot(v)
    kq = xu_ly_demo(kho)
    monkeypatch.setattr(quyen, 'xac_minh', lambda *a, **kw: replace(ctx, module='module-demo-khac'))
    with pytest.raises(LoiNghiepVu) as exc:
        kho.chot(kq)
    assert exc.value.ma == 'MASK_NGU_CANH_CHUA_XAC_MINH'


@pytest.mark.parametrize('nguon', ['kho', 'quyen'])
def test_loi_port_khong_lo_ten_duong_dan(tmp_path, nguon):
    core, quyen, v, _, _ = ghep(tmp_path)
    def hong(*a, **kw):
        raise RuntimeError(TEN + str(tmp_path))
    if nguon == 'quyen':
        quyen.xac_minh = hong
    lop = KhoDinhDanh(goi_kho=hong if nguon == 'kho' else core.port(quyen),
                      quyen=quyen, kho_tam=KhoTam(tmp_path))
    with pytest.raises(LoiNghiepVu) as exc:
        lop.mo_luot(v)
    assert exc.value.ma == ('MASK_KHO_LOI' if nguon == 'kho' else 'MASK_NGU_CANH_CHUA_XAC_MINH')
    assert TEN not in str(exc.value) and str(tmp_path) not in str(exc.value)


@pytest.mark.parametrize('ma', [None, '', 'ma-demo-khong-co'])
def test_ma_mo_thieu_sai_bi_tu_choi(tmp_path, ma):
    core, quyen, v, ctx, lop = ghep(tmp_path)
    lop.xu_ly(v, xu_ly_demo)
    v_mo = viec_demo('mo-demo')
    quyen.cap(v_mo.id, loai='mo_che', ma_yeu_cau=ctx.ma_yeu_cau)
    with pytest.raises(LoiNghiepVu) as exc:
        lop.xu_ly(v_mo, khong_duoc_chay, loai='mo_che', ma_yeu_cau=ma)
    assert exc.value.ma == 'MASK_MA_YEU_CAU'


def test_doc_lai_ket_qua_chua_dat_khong_bao_thanh_cong(tmp_path):
    core, _, v, ctx, lop = ghep(tmp_path)
    lop.xu_ly(v, xu_ly_demo)
    core.bang['DEMO']['luot'][ctx.ma_luot]['gui_duoc'] = False
    with pytest.raises(LoiNghiepVu) as exc:
        lop.xu_ly(v, khong_duoc_chay)
    assert exc.value.ma == 'MASK_DINH_DANH_CHUA_DAT'


def test_ma_opaque_khong_ep_uuid_64_ky_tu(tmp_path):
    core = KhoCoreGia()
    quyen = QuyenCoreGia(core)
    v = viec_demo()
    ma = 'yeu-cau-demo-Ω-' + 'x' * 140
    quyen.cap(v.id, ma_yeu_cau=ma)
    lop = KhoDinhDanh(goi_kho=core.port(quyen), quyen=quyen, kho_tam=KhoTam(tmp_path))
    assert lop.xu_ly(v, xu_ly_demo)['ma_yeu_cau'] == ma
    assert ma.encode('utf-8') not in (tmp_path / 'mask.json').read_bytes()


def test_khong_tin_ma_yeu_cau_tu_payload_khi_che(tmp_path):
    core, _, v, ctx, lop = ghep(tmp_path)
    v.dau_vao['ma_yeu_cau'] = 'ma-demo-tu-khai'
    v.tham_so.update(module='module-demo-gia', nguoi_gui='nguoi-demo-gia')
    assert lop.xu_ly(v, xu_ly_demo)['ma_yeu_cau'] == ctx.ma_yeu_cau
    assert core.bang['DEMO']['yeu_cau'][ctx.ma_yeu_cau]['module'] == 'module-demo-a'


def test_chua_ro_sau_chot_giao_lai_doc_port_khong_tinh_lai(tmp_path):
    core, quyen, v, ctx, lop = ghep(tmp_path)
    core.mat_phan_hoi = True
    with pytest.raises(ChuaRo) as exc:
        lop.xu_ly(v, xu_ly_demo)
    ma_tuong_quan = exc.value.ma_tuong_quan
    dau = next(iter(json.loads((tmp_path / 'mask.json').read_text('utf-8'))['luot'].values()))
    assert dau['trang_thai'] == 3 and dau['chot'] != '0' * 64
    assert ma_tuong_quan == 'mask-' + dau['tuong_quan']
    assert core.so_chot == 1
    lop_moi = KhoDinhDanh(goi_kho=core.port(quyen), quyen=quyen, kho_tam=KhoTam(tmp_path))
    kq = lop_moi.xu_ly(v, khong_duoc_chay)
    assert kq == core.bang['DEMO']['luot'][ctx.ma_luot] and core.so_chot == 1
    assert [t[0] for t in core.cac_goi[-2:]] == ['snapshot_luot', 'chot_luot']
    for tep in tmp_path.iterdir():
        assert TEN.encode('utf-8') not in tep.read_bytes() and VAN_BAN.encode('utf-8') not in tep.read_bytes()


def test_chua_ro_nguon_con_dang_cho_khong_chay_lai(tmp_path):
    core, quyen, v, ctx, lop = ghep(tmp_path)
    core.cho_chot = True
    with pytest.raises(ChuaRo) as lan1:
        lop.xu_ly(v, xu_ly_demo)
    dau1 = (tmp_path / 'mask.json').read_bytes()
    lop_moi = KhoDinhDanh(goi_kho=core.port(quyen), quyen=quyen, kho_tam=KhoTam(tmp_path))
    with pytest.raises(ChuaRo) as lan2:
        lop_moi.xu_ly(v, khong_duoc_chay)
    assert lan1.value.ma_tuong_quan == lan2.value.ma_tuong_quan
    assert (tmp_path / 'mask.json').read_bytes() == dau1
    assert core.so_chot == 0 and len(core.dang_cho) == 1
    core.hoan_tat(ctx.ma_luot)
    kq = lop_moi.xu_ly(v, khong_duoc_chay)
    assert kq['ma_yeu_cau'] == ctx.ma_yeu_cau and core.so_chot == 1
    assert core.bang['DEMO']['cho_duyet'][che_van_ban.chuan_hoa(TEN)]['so_lan_gap'] == 1


def test_kho_tam_hong_khong_gui_chot(tmp_path, monkeypatch):
    core, _, v, _, lop = ghep(tmp_path)
    kho = lop.mo_luot(v)
    kq = xu_ly_demo(kho)
    def hong(*a, **kw):
        raise PermissionError('DEMO không ghi được')
    monkeypatch.setattr(kho._kho_tam, '_ghi', hong)
    with pytest.raises(LoiNghiepVu) as exc:
        kho.chot(kq)
    assert exc.value.ma == 'MASK_KHO_TAM_LOI'
    assert core.so_chot == 0 and len(core.cac_goi) == 1


def test_dau_da_chot_nhung_port_mat_trang_thai_thi_tu_choi(tmp_path):
    core, _, v, _, lop = ghep(tmp_path)
    lop.xu_ly(v, xu_ly_demo)
    core.bang['DEMO']['luot'].clear()
    with pytest.raises(LoiNghiepVu) as exc:
        lop.xu_ly(v, khong_duoc_chay)
    assert exc.value.ma == 'MASK_XUNG_DOT'


def test_huy_truoc_chot_khong_ghi(tmp_path):
    core, _, v, _, lop = ghep(tmp_path)
    def ham(kho):
        kq = xu_ly_demo(kho)
        v.kiem_huy = lambda: (_ for _ in ()).throw(ViecDaHuy())
        return kq
    with pytest.raises(ViecDaHuy):
        lop.xu_ly(v, ham)
    assert core.so_chot == 0


@pytest.mark.parametrize('co', ['con_sot', 'kiem_tien_ngay'])
def test_ket_qua_chua_dat_khong_chot(tmp_path, co):
    core, _, v, _, lop = ghep(tmp_path)
    def ham(kho):
        kq = xu_ly_demo(kho)
        kq[co] = [{'ly_do': 'DEMO chưa đạt'}] if co == 'con_sot' else False
        return kq
    with pytest.raises(LoiNghiepVu):
        lop.xu_ly(v, ham)
    assert core.so_chot == 0 and core.bang['DEMO']['cho_duyet'] == {}


@pytest.fixture
def tu_vung_demo(monkeypatch):
    tai_nguyen.xoa_cache()
    tu_vung = {'vn_surnames.txt': ('Nguyễn *', 'Trần *'), 'vn_places.txt': (),
               'common_acronyms.txt': ('DEMO VND USD VAT GTGT',),
               'leftover_allowlist.txt': ('words: demo nội dung thanh toán ngày giá trị vnd usd',)}
    monkeypatch.setattr(tai_nguyen, 'doc_dong', lambda ten: tu_vung[ten])
    yield
    tai_nguyen.xoa_cache()


def tao_app_demo(core_kho, quyen, thu_muc, cac_lan):
    """Adapter chỉ trong tests để kiểm port qua SDK; handler sản phẩm ở MASK-5."""
    app = Engine.tu_khai_bao(str(GOI / 'engine.json'))
    lop = KhoDinhDanh(goi_kho=core_kho.port(quyen), quyen=quyen, kho_tam=KhoTam(thu_muc))
    @app.nang_luc(CHE)
    def che(viec):
        def ham(kho):
            cac_lan.append(viec.id)
            return che_van_ban.che(viec.dau_vao['van_ban'], [], kho)
        kq = lop.xu_ly(viec, ham)
        return {'loai': 'van_ban_da_che', 'van_ban_da_che':
                dict(phien_ban=1, van_ban=kq['van_ban_da_che'], ma_yeu_cau=kq['ma_yeu_cau'],
                     con_sot=kq['con_sot'], kiem_tien_ngay=kq['kiem_tien_ngay'], chuyen_tiep={})}
    @app.nang_luc(MO)
    def mo(viec):
        dau = viec.dau_vao['tra_loi_ai']
        ma = dau['chuyen_tiep']['ma_yeu_cau']
        kq = lop.xu_ly(viec, lambda kho: che_van_ban.mo_che(dau['tra_loi'], ma, kho,
                         dong_viec=viec.tham_so['dong_viec']), loai='mo_che', ma_yeu_cau=ma)
        return {'loai': 'truong', 'truong':
                dict(van_ban_da_mo_che=kq['van_ban_da_mo_che'], so_cho_mo=kq['so_cho_mo'],
                     bi_danh_khong_ro_json=json.dumps(kq['bi_danh_khong_ro']), mo_day_du=kq['mo_day_du'],
                     trang_thai_ma_yeu_cau=kq['trang_thai_ma_yeu_cau'], tra_loi_ai_da_mo_json=None)}
    return app


def giao_lai(core, ma):
    """Mô phỏng supervisor giao lại cùng việc/bước, tăng lan_thu của CoreGia."""
    with core._lock:
        core._viec[ma]['trang_thai'] = 'CHO'
        core._hang.append(ma)


@pytest.mark.parametrize('so_lan_mat', [1, 4])
def test_core_gia_mat_ack_sdk_retry_khoi_dong_lai_va_dong(tmp_path, tu_vung_demo, so_lan_mat):
    core, ben_kho = CoreGia(), KhoCoreGia()
    quyen, cac_lan = QuyenCoreGia(ben_kho), []
    ma_viec = core.giao_viec(CHE, {'loai': 'van_ban', 'van_ban': VAN_BAN})
    ctx = quyen.cap(ma_viec)
    app = tao_app_demo(ben_kho, quyen, tmp_path, cac_lan)
    core.gay_mat_xac_nhan('ket_qua', so_lan=so_lan_mat)
    core.chay(app)
    kq = core.xem(ma_viec)
    assert kq['trang_thai'] == ('XONG' if so_lan_mat == 1 else 'DANG_CHAY')
    assert core.so_lan_ghi['ket_qua'] == 1 and ben_kho.so_chot == 1
    for _ in range(2):
        giao_lai(core, ma_viec)
        core.chay(tao_app_demo(ben_kho, quyen, tmp_path, cac_lan))
        assert core.xem(ma_viec)['ket_qua'] == kq['ket_qua']
    assert cac_lan == [ma_viec] and ben_kho.so_chot == 1
    assert core.xem(ma_viec)['lan_thu'] == 3
    da_che = kq['ket_qua']['van_ban_da_che']['van_ban']
    assert TEN not in da_che
    ma_mo = core.giao_viec(MO, {'loai': 'tra_loi_ai', 'tra_loi_ai':
                              {'tra_loi': da_che, 'chuyen_tiep': {'ma_yeu_cau': ctx.ma_yeu_cau}}},
                           {'dong_viec': True})
    quyen.cap(ma_mo, loai='mo_che', ma_yeu_cau=ctx.ma_yeu_cau)
    core.chay(tao_app_demo(ben_kho, quyen, tmp_path, cac_lan))
    mo = core.xem(ma_mo)
    assert mo['trang_thai'] == 'XONG' and mo['ket_qua']['truong']['van_ban_da_mo_che'] == VAN_BAN
    assert mo['ket_qua']['truong']['trang_thai_ma_yeu_cau'] == 'DA_DONG'
    giao_lai(core, ma_mo)
    core.chay(tao_app_demo(ben_kho, quyen, tmp_path, cac_lan))
    assert core.xem(ma_mo)['ket_qua'] == mo['ket_qua'] and ben_kho.so_chot == 2
    ma_mo_moi = core.giao_viec(MO, core._viec[ma_mo]['dau_vao'])
    quyen.cap(ma_mo_moi, loai='mo_che', ma_yeu_cau=ctx.ma_yeu_cau)
    core.chay(tao_app_demo(ben_kho, quyen, tmp_path, cac_lan))
    assert core.xem(ma_mo_moi)['loi']['ma'] == 'MASK_MA_YEU_CAU'
    for tep in tmp_path.iterdir():
        assert TEN.encode('utf-8') not in tep.read_bytes() and VAN_BAN.encode('utf-8') not in tep.read_bytes()


def test_core_gia_chua_ro_khong_bao_xong_gia(tmp_path, tu_vung_demo):
    core, ben_kho = CoreGia(), KhoCoreGia()
    quyen, cac_lan = QuyenCoreGia(ben_kho), []
    ma = core.giao_viec(CHE, {'loai': 'van_ban', 'van_ban': VAN_BAN})
    quyen.cap(ma)
    ben_kho.mat_phan_hoi = True
    core.chay(tao_app_demo(ben_kho, quyen, tmp_path, cac_lan))
    assert core.xem(ma)['trang_thai'] == 'CHUA_RO' and core.xem(ma)['ket_qua'] is None
    giao_lai(core, ma)
    core.chay(tao_app_demo(ben_kho, quyen, tmp_path, cac_lan))
    assert core.xem(ma)['trang_thai'] == 'XONG' and ben_kho.so_chot == 1 and cac_lan == [ma]
