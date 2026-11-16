"""MASK-B9b: kiểm cuối trước commit; đã kiểm bằng Core giả (CoreGia)."""
from contextlib import contextmanager
from dataclasses import replace

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu

from ho_tro_mask_b7 import bo as bo_hau, chay, chuan_bi_het, giao as giao_hau
from ho_tro_mask_b9 import bo as bo_mo, giao as giao_mo
from ho_tro_ngan import viec_demo


def _bo(loai, duong, dang='tep'):
    if duong == 'mo':
        b = bo_mo(loai)
        giao_mo(b)
    else:
        b = bo_hau(loai, dang=dang)
        chuan_bi_het(b)
        giao_hau(b)
        b.bg = b.ram._ban_ghi
    return b


def _theo_doi_cua(b, duong, monkeypatch):
    cong = b.mo if duong == 'mo' else b.cong
    ten = 'ban_giao_cuoi' if duong == 'mo' else 'ban_giao_tep_cuoi'
    goc = getattr(cong, ten)
    ra, commit = [], []

    @contextmanager
    def cua(*args, **kw):
        with goc(*args, **kw) as nhan:
            try:
                yield nhan
            except BaseException as exc:
                ra.append(type(exc))
                raise
            else:
                ra.append(None)
        commit.append(True)

    monkeypatch.setattr(cong, ten, cua)
    return ra, commit


def _chen_sau_r4(b, duong, chen, monkeypatch):
    goc = b.ram.buoc
    moc = []

    @contextmanager
    def buoc(viec, **kw):
        with goc(viec, **kw) as handle:
            yield handle
        # R4 đã xong, kiểm cuối của adapter chưa chạy, cửa Core còn mở.
        assert not b.bg.so_huu
        if duong == 'mo':
            assert b.ram._ban_ghi is None and not b.bg.du_lieu
            assert not b.c.ket_qua_cuoi_demo and not b.mo.phat_hanh
        else:
            assert b.bg.trang_thai == 'CHO_AI'
            assert b.bg.du_lieu['giai_doan_ai'] == 'DA_HAU_KIEM'
            assert not b.cong.giao_cuoi
        moc.append(True)
        chen(viec)

    monkeypatch.setattr(b.ram, 'buoc', buoc)
    return moc


def _doi(b, viec, sai):
    if sai == 'ttl':
        b.dh.tien(601, chay_timer=False)
    elif sai == 'huy':
        b.q.bao_ram(b.ctx.ma_yeu_cau, 'HUY')
    elif sai == 'phap_nhan':
        viec.ngu_canh['phap_nhan_id'] = 'pn-khac-DEMO'
    elif sai == 'xac_minh':
        loai = 'mo_che' if (viec.id, 'mo_che') in b.q.ve else 'che'
        b.q.ve[viec.id, loai] = replace(b.q.ve[viec.id, loai], ma_luot='luot-khac-DEMO')
    elif sai == 'xac_minh_ram':
        b.q.ram_sua_ctx = lambda ctx: replace(ctx, instance='instance-khac-DEMO')
    elif sai == 'han_core':
        b.q.ram_han = b.dh()
    elif sai == 'dau_vao':
        viec.tham_so['dong_viec'] = 'DEMO-da-doi'
    elif sai == 'du_lieu':
        b.bg.du_lieu['DEMO'] = True
    else:
        raise AssertionError(sai)


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('duong', ['mo', 'hau'])
@pytest.mark.parametrize('sai', ['ttl', 'huy', 'phap_nhan', 'xac_minh',
                                'xac_minh_ram', 'han_core', 'dau_vao'])
def test_kiem_cuoi_loi_phai_huy_truoc_commit(loai, duong, sai, monkeypatch):
    b = _bo(loai, duong)
    ra, commit = _theo_doi_cua(b, duong, monkeypatch)
    moc = _chen_sau_r4(b, duong, lambda v: _doi(b, v, sai), monkeypatch)
    k = chay(b)
    assert moc == [True]
    assert k['trang_thai'] == 'LOI' and k['ket_qua'] is None, k
    assert len(ra) == 1 and ra[0] is not None
    assert issubclass(ra[0], LoiNghiepVu)
    assert not commit
    assert b.ram._ban_ghi is None and not b.bg.du_lieu
    if duong == 'mo':
        assert not b.c.ket_qua_cuoi_demo and not b.mo.phat_hanh
        assert not b.mo.cach_ly and len(b.mo.thu_hoi) == 1
        assert b.mo.luot_upload == b.mo.so_nhan == 1
    else:
        assert not b.cong.giao_cuoi and b.cong.dem_chot == 1


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
def test_mo_kiem_du_lieu_da_tieu_thu_truoc_commit(loai, monkeypatch):
    b = _bo(loai, 'mo')
    ra, commit = _theo_doi_cua(b, 'mo', monkeypatch)
    _chen_sau_r4(b, 'mo', lambda v: _doi(b, v, 'du_lieu'), monkeypatch)
    k = chay(b)
    assert k['trang_thai'] == 'LOI' and k['ket_qua'] is None
    assert ra == [LoiNghiepVu] and not commit
    assert not b.c.ket_qua_cuoi_demo and not b.mo.phat_hanh
    # Chèn vào bản ghi đã tiêu thụ để kiểm gate, không phải map mở lại.
    assert b.ram._ban_ghi is None


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('duong,dang', [('mo', 'tep'), ('hau', 'tep'), ('hau', 'van_ban')])
def test_binh_thuong_phat_hanh_dung_mot_lan_sau_kiem_cuoi(loai, duong, dang, monkeypatch):
    b = _bo(loai, duong, dang)
    ra, commit = _theo_doi_cua(b, duong, monkeypatch)
    moc = _chen_sau_r4(b, duong, lambda v: None, monkeypatch)
    k = chay(b)
    assert k['trang_thai'] == 'XONG', k
    assert moc == [True] and ra == [None] and commit == [True]
    if duong == 'mo':
        assert b.mo.so_nhan == b.mo.luot_upload == len(b.mo.phat_hanh) == 1
        assert len(b.c.ket_qua_cuoi_demo) == 1
        assert b.ram._ban_ghi is None and not b.bg.du_lieu
    else:
        assert len(b.cong.giao_cuoi) == b.cong.dem_chot == 1
        assert b.ram._ban_ghi is b.bg and b.bg.trang_thai == 'CHO_AI'


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('loi', [LoiNghiepVu('MASK_MA_YEU_CAU', 'Lỗi DEMO.'), ChuaRo('ACK-DEMO')])
def test_core_gia_hau_kiem_nhan_chi_cach_ly_ngoai_le_huy(loai, loi):
    b = _bo(loai, 'hau')
    viec = viec_demo(b.v)
    with pytest.raises(type(loi)):
        with b.cong.ban_giao_tep_cuoi(viec, b.q.ve[b.v, 'che'], chung_cu=b'DEMO',
                                     han_monotonic=b.dh() + 600) as nhan:
            assert nhan(b'DEMO') is True
            assert not b.cong.giao_cuoi
            raise loi
    assert not b.cong.giao_cuoi


@pytest.mark.parametrize('loai', ['docx', 'xlsx'])
@pytest.mark.parametrize('duong', ['mo', 'hau'])
def test_chua_ro_truoc_commit_la_ket_thuc_khong_giu_map(loai, duong, monkeypatch):
    b = _bo(loai, duong)
    ra, commit = _theo_doi_cua(b, duong, monkeypatch)

    def chen(viec):
        raise ChuaRo('ACK-DEMO')

    _chen_sau_r4(b, duong, chen, monkeypatch)
    k = chay(b)
    assert k['trang_thai'] == 'CHUA_RO' and k['ket_qua'] is None, k
    assert ra == [ChuaRo] and not commit
    assert b.ram._ban_ghi is None and not b.bg.du_lieu
    if duong == 'mo':
        assert not b.mo.phat_hanh and not b.c.ket_qua_cuoi_demo
    else:
        assert not b.cong.giao_cuoi

