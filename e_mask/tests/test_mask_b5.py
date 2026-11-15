"""MASK-B5: logic nội bộ Word đã kiểm bằng Core giả (CoreGia), 0 Cloud.

Không có handler tệp/nguồn Local thật. Không coi reader hoặc primitive
che bổ sung là bằng chứng hai lớp Local hoặc quyền phát hành.
"""
from dataclasses import asdict
from pathlib import Path
import builtins
import io
import logging
import traceback
import unicodedata

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, NganEngine, Viec, ViecDaHuy

from e_mask import tep_word as tw, tai_nguyen
from e_mask.doc_word import doc_word
from e_mask.mo_che_ram import kiem_map_ram
from e_mask.kho_anh_xa_ram import KhoAnhXaRAM
from e_mask.tra_cuu_dinh_danh import UngVien
from e_mask.va_xml import chuan_bi_va
from e_mask.zip_an_toan import kiem_ban_ghi
from ho_tro_mask_b1 import CT_W, W, word_demo, them_phan
from ho_tro_mask_b2 import zip_office
from ho_tro_mask_b5 import ALIAS, DS, TEN, bo, moi_vung_co_ten, word


def _che(b, raw, *, ds=DS, giu=True):
    with b.ram.buoc(b.v) as buoc:
        dau = tw.che_word(raw, buoc=buoc, dinh_danh=ds)
        if giu:
            buoc.cho_ai()
        return dau


def _s(b):
    return b.ram._ban_ghi.du_lieu['tep_word']


def _chan(b, raw, *, ds=DS, ma=None):
    with pytest.raises(LoiNghiepVu) as exc:
        _che(b, raw, ds=ds)
    if ma:
        assert exc.value.ma == ma
    assert TEN not in str(exc.value)
    assert b.ram._ban_ghi is None
    assert not b.c._tep
    return exc.value


def test_che_moi_story_chu_an_metadata_va_attribute_khong_bo_vung():
    b, raw = bo(), moi_vung_co_ten()
    dau = _che(b, raw)
    s = _s(b)
    truoc, sau = s['tai_lieu'], doc_word(s['da_che'], kiem_huy=lambda: None)
    assert {'than', 'dau_trang', 'chan_trang', 'footnote', 'endnote', 'thuoc_tinh', 'dinh_dang'} <= {v.loai for v in truoc.vung}
    assert any(m.an for v in truoc.vung for m in v.anh_xa)
    assert any(v.o is not None and v.o.gop_tu is not None for v in truoc.vung)
    for v, moi in zip(truoc.vung, sau.vung):
        assert moi.van_ban == v.van_ban.replace(TEN, ALIAS)
    assert s['alias_nguyen_van'] == {ALIAS: TEN}
    assert s['vung_da_doc'] == tuple(range(len(truoc.vung)))
    assert s['vung_da_kiem_local'] == () and s['giai_doan'] == 'CHO_LOCAL'
    assert dau.so_vung == len(truoc.vung)
    assert set(asdict(dau)) == {'bam_goc', 'bam_da_che', 'so_vung', 'so_phep_thay'}
    assert not b.c._tep


@pytest.mark.parametrize('codec', [None, 'utf-16', 'utf-16-be'])
@pytest.mark.parametrize('dang', ['NFC', 'NFD', 'Cf', 'entity', 'cdata'])
@pytest.mark.parametrize('ngay', ['30/10/2026', '2026-10-30'])
def test_ten_qua_ba_run_khac_format_unicode_entity_va_bytes_bat_bien(codec, dang, ngay):
    ten = 'Nguyễn Văn Ánh'
    if dang == 'NFD':
        ten = unicodedata.normalize('NFD', ten)
    elif dang == 'Cf':
        ten = ten.replace('Văn', 'Vă\u200bn')
    a, z = ten.index(' '), ten.rindex(' ')
    manh = [ten[:a + 1], ten[a + 1:z + 1], ten[z + 1:]]
    if dang == 'entity':
        manh[0] = manh[0].replace('ễ', '&#7877;')
    if dang == 'cdata':
        manh = ['<![CDATA[' + m + ']]>' for m in manh]
    body = ('<w:p><w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">bên: ' + manh[0] + '</w:t></w:r>'
            '<w:r><w:rPr><w:i/><w:vanish/></w:rPr><w:t xml:space="preserve">' + manh[1] + '</w:t></w:r>'
            '<w:r><w:rPr><w:color w:val="123456"/></w:rPr><w:t>' + manh[2] + '</w:t></w:r>'
            '<w:r><w:t>; 1.000.000 VND ngày ' + ngay + '.</w:t></w:r></w:p>')
    raw = word(noi_dung=body, codec=codec)
    b = bo(seeds=((ten, 'CA_NHAN', '[[MASKCN-0001]]'),))
    ds = [dict(gia_tri=ten, nhom='CA_NHAN')]
    _che(b, raw, ds=ds)
    s = _s(b)
    assert s['tai_lieu_da_che'].vung[0].van_ban == 'bên: [[MASKCN-0001]]; 1.000.000 VND ngày ' + ngay + '.'
    assert s['alias_nguyen_van'] == {'[[MASKCN-0001]]': ten}
    goc = s['tai_lieu'].goi.zip
    moi = s['tai_lieu_da_che'].goi.zip
    patches, _ = chuan_bi_va(s['tai_lieu'], s['kich_ban'], lambda: None)
    for p, q in zip(goc.phan, moi.phan):
        if p.ten in patches:
            at, vi = 0, 0
            for a, z, data in patches[p.ten]:
                assert p.du_lieu[at:a] == q.du_lieu[vi:vi + a - at]
                vi += a - at
                assert q.du_lieu[vi:vi + len(data)] == data
                at, vi = z, vi + len(data)
            assert p.du_lieu[at:] == q.du_lieu[vi:]
        else:
            assert p.du_lieu == q.du_lieu
    regs = {r.phan.ten: r for r in kiem_ban_ghi(goc, lambda: None)}
    for r in kiem_ban_ghi(moi, lambda: None):
        if r.phan.ten not in patches:
            p = regs[r.phan.ten]
            assert goc.goc[p.phan.le_dau:p.le_cuoi_ban_ghi] == moi.goc[r.phan.le_dau:r.le_cuoi_ban_ghi]


def test_nfd_ngoai_ten_giu_nguyen_cf_ngoai_ten_bo_theo_mask_2b():
    prefix = unicodedata.normalize('NFD', 'nội dung')
    b = bo()
    _che(b, word(prefix + '\u200b; ' + TEN + '; 1.000.000 VND ngày 30/10/2026.'))
    s = _s(b)
    assert s['tai_lieu_da_che'].vung[0].van_ban == prefix + '; ' + ALIAS + '; 1.000.000 VND ngày 30/10/2026.'


def test_khong_ghep_ten_qua_hai_o_hoac_hai_story():
    b = bo()
    body = ('<w:tbl><w:tr><w:tc><w:p><w:r><w:t>Công ty DEMO </w:t></w:r></w:p></w:tc>'
            '<w:tc><w:p><w:r><w:t>Ánh Dương</w:t></w:r></w:p></w:tc></w:tr></w:tbl>')
    # Chặn vì thiếu che; không được mượn nửa tên từ ô cạnh để tìm alias.
    _chan(b, word(noi_dung=body), ma='MASK_DINH_DANH_CHUA_DAT')


@pytest.mark.parametrize('dang', ['comment', 'revision', 'field', 'textbox', 'content_control', 'attr', 'part'])
def test_unsupported_chan_ca_tep_khong_xoa_vung(dang):
    p = word_demo(chu=TEN)
    bad = {'comment': '<w:commentRangeStart w:id="0"/>',
           'revision': '<w:ins w:author="DEMO"><w:r><w:t>DEMO</w:t></w:r></w:ins>',
           'field': '<w:fldSimple w:instr="DEMO"/>',
           'textbox': '<w:txbxContent><w:p/></w:txbxContent>',
           'content_control': '<w:sdt><w:sdtContent><w:p/></w:sdtContent></w:sdt>'}
    if dang in bad:
        p['word/document.xml'] = p['word/document.xml'].replace('</w:body>', bad[dang] + '</w:body>')
    elif dang == 'attr':
        p['word/document.xml'] = p['word/document.xml'].replace('<w:t>', '<w:t w:author="DEMO">')
    else:
        them_phan(p, 'word/comments.xml', f'<w:comments xmlns:w="{W}"/>', CT_W + 'comments+xml', 'comments')
    _chan(bo(), zip_office(p), ma='MASK_TEP_CHUA_HO_TRO')


def test_ten_moi_chua_du_bao_dam_core_chan_khong_ghi_cho_duyet():
    b = bo(seeds=())
    _chan(b, word())
    assert b.c.so_lan_ghi['ngan'] == 0


def test_cung_alias_nhieu_nguyen_van_khac_run_story_metadata_chan():
    b = bo()
    goc = unicodedata.normalize('NFD', TEN)
    body = '<w:p><w:r><w:t>' + TEN + '</w:t></w:r></w:p><w:p><w:r><w:t>' + goc + '</w:t></w:r></w:p>'
    _chan(b, word(noi_dung=body), ma='MASK_MO_CHE_KHONG_DAY_DU')


def test_spi_khong_ghi_ngan_tep_log_core_chuyen_tiep_va_chi_tim_bang_chinh_xac(monkeypatch, capsys, caplog):
    b, raw = bo(), moi_vung_co_ten()
    tai_nguyen.nap_tu_goi()
    goi_tim = []
    tim = NganEngine.tim
    def spy(self, bang, **kw):
        goi_tim.append((bang, kw))
        return tim(self, bang, **kw)
    def cam(*a, **kw):
        pytest.fail('Không được ghi hoặc tải map/tệp nội bộ ra ngoài RAM.')
    mo_that = io.open
    thu_muc_tu_dien = Path(tai_nguyen.__file__).parent / 'tu_dien'
    def chi_doc_tu_dien(tep, mode='r', *a, **kw):
        assert Path(tep).parent == thu_muc_tu_dien
        assert not any(c in mode for c in 'wax+')
        return mo_that(tep, mode, *a, **kw)
    ghi_truoc = dict(b.c.so_lan_ghi)
    with monkeypatch.context() as mp:
        mp.setattr(NganEngine, 'tim', spy)
        mp.setattr(NganEngine, 'lo', cam)
        mp.setattr(Viec, 'mo_tep', cam)
        mp.setattr(Viec, 'tai_tep_ra', cam)
        mp.setattr(builtins, 'open', chi_doc_tu_dien)
        mp.setattr(io, 'open', chi_doc_tu_dien)
        mp.setattr(Path, 'write_bytes', cam)
        mp.setattr(Path, 'write_text', cam)
        caplog.set_level(logging.DEBUG)
        dau = _che(b, raw)
    assert capsys.readouterr() == ('', '') and not caplog.records
    assert TEN not in repr(dau) and not b.c._tep
    assert b.c.so_lan_ghi == ghi_truoc
    dinh_danh = [kw for bang, kw in goi_tim if bang == 'dinh_danh']
    assert sum(kw['loc']['gia_tri_chuan'] == 'công ty demo ánh dương' for kw in dinh_danh) == 1
    assert len(dinh_danh) == len({kw['loc']['gia_tri_chuan'] for kw in dinh_danh})
    assert all(kw['loc'].get('gia_tri_chuan') for kw in dinh_danh)
    assert all(set(kw['loc']) == {'gia_tri_chuan', 'phien_ban_chuan_hoa', 'vung_du_lieu'} for kw in dinh_danh)
    assert not any('chuyen_tiep' in k for k in asdict(dau))


def test_thieu_ram_quyen_hoac_ghim_khong_chay(monkeypatch):
    with pytest.raises(LoiNghiepVu, match='Không còn dữ liệu'):
        tw.che_word(word(), buoc=None)
    b = bo()
    b.q.ram_ghim = False
    _chan(b, word(), ma='MASK_CHUOI_CHUA_GHIM')
    b = bo()
    b.q.thu_hoi = True
    _chan(b, word(), ma='MASK_MA_YEU_CAU')


@pytest.mark.parametrize('su_kien', ['HUY', 'LOI', 'KET_THUC', 'MAT_LEASE', 'MAT_QUYEN', 'HET_HAN'])
def test_vong_doi_don_map_bytes_patch_ca_luc_ranh(su_kien):
    b = bo()
    _che(b, word())
    s = _s(b)
    b.q.bao_ram(b.ma, su_kien)
    assert b.ram._ban_ghi is None and not s
    assert not b.c._tep


@pytest.mark.parametrize('ttl', [60, 600, 900])
def test_ttl_tuyet_doi_retry_khong_gia_han_va_don_chu_dong(ttl):
    b, raw = bo(ttl=ttl), word()
    dau = _che(b, raw)
    han = b.ram._ban_ghi.han
    b.dh.tien(ttl - 1)
    assert _che(b, raw) == dau and b.ram._ban_ghi.han == han
    s = _s(b)
    b.dh.tien(1)
    assert not s and b.ram._ban_ghi is None
    _chan(b, raw, ma='MASK_ANH_XA_KHONG_CON')


def test_retry_cung_ref_doi_bytes_don_map_khong_tra_tep_cu():
    b = bo()
    _che(b, word())
    s = _s(b)
    _chan(b, word(TEN + '; DEMO thay đổi'), ma='MASK_DAU_VAO_THAY_DOI')
    assert not s


def test_lop_quy_tac_reader_va_caller_flag_khong_chung_minh_local():
    b = bo()
    _che(b, word())
    with pytest.raises(LoiNghiepVu):
        with b.ram.buoc(b.v) as buoc:
            kiem_map_ram(buoc)  # R6 không nhận tệp CHO_LOCAL làm map đã hậu kiểm.
    assert b.ram._ban_ghi is None
    assert not any('tep' in ma for ma in b.app._ham)


@pytest.mark.parametrize('dang', ['restart', 'instance'])
def test_map_word_khong_di_sang_ram_moi_hoac_instance_khac(dang):
    b = bo()
    _che(b, word())
    cu = b.ram
    s = _s(b)
    if dang == 'instance':
        b.q.ram_instance = 'instance-DEMO-khac'
    b.ram = KhoAnhXaRAM(quyen=b.q, dong_ho=b.dh, hen_gio=b.dh.hen_gio)
    _chan(b, word(), ma='MASK_ANH_XA_KHONG_CON')
    assert s and cu._ban_ghi is not None
    b.q.bao_ram(b.ma, 'KET_THUC')
    assert not s and cu._ban_ghi is None


@pytest.mark.parametrize('truong', ['module', 'nguoi_gui', 'tai_lieu', 'vung'])
def test_khong_dung_map_word_nguoi_module_tai_lieu_vung_khac(truong):
    b = bo()
    _che(b, word())
    s = _s(b)
    cu = getattr(b.q, truong)
    ctx_cu = b.q.ram_ctx[b.ma]
    setattr(b.q, truong, 'THAT' if truong == 'vung' else 'DEMO-khac')
    with pytest.raises(LoiNghiepVu):
        _che(b, word())
    assert s  # Sai caller không được nhận hay xóa map của chủ cũ.
    setattr(b.q, truong, cu)
    b.q.ram_ctx[b.ma] = ctx_cu
    b.q.bao_ram(b.ma)
    assert not s


def test_r4_tieu_thu_mot_lan_don_bytes_word_khong_tuyen_bo_da_mo_word():
    b = bo()
    _che(b, word())
    s = _s(b)
    b.q.cap(b.v.id, loai='mo_che', ma_yeu_cau=b.ma)
    with b.ram.buoc(b.v, loai='mo_che', ma_yeu_cau=b.ma) as buoc:
        assert buoc.du_lieu['tep_word'] is s
    assert not s and b.ram._ban_ghi is None
    with pytest.raises(LoiNghiepVu):
        with b.ram.buoc(b.v, loai='mo_che', ma_yeu_cau=b.ma):
            pytest.fail('Không được tiêu thụ lần hai.')


def test_typed_metadata_so_va_ngay_giu_nguyen_bytes_sau_che():
    b, raw = bo(), moi_vung_co_ten()
    _che(b, raw)
    s = _s(b)
    parts = {p.ten: p.du_lieu for p in s['tai_lieu_da_che'].goi.zip.phan}
    for chu in (b'<cp:revision>1</cp:revision>', b'2026-10-30T00:00:00Z'):
        assert chu in parts['docProps/core.xml']
    assert b'<vt:i4>1000000</vt:i4>' in parts['docProps/custom.xml']
    assert b'<Pages>1</Pages><Words>100</Words><Characters>500</Characters>' in parts['docProps/app.xml']


def test_canh_bao_so_ngoai_ngay_khong_duoc_mien_theo_ngay_iso():
    b = bo()
    _chan(b, word(TEN + '; ngày 2026-10-30; số tài khoản 1234567890123456.'),
          ma='MASK_DINH_DANH_CHUA_DAT')


def test_money_split_runs_ngay_split_runs_giu_dung_nguyen_van():
    b = bo()
    body = ('<w:p><w:r><w:t>' + TEN + '; 1.000.</w:t></w:r><w:r><w:rPr><w:i/></w:rPr>'
            '<w:t>000 VND ngày 2026-</w:t></w:r><w:r><w:t>10-30.</w:t></w:r></w:p>')
    _che(b, word(noi_dung=body))
    assert _s(b)['tai_lieu_da_che'].vung[0].van_ban == ALIAS + '; 1.000.000 VND ngày 2026-10-30.'


def test_cf_bieu_dien_bang_markup_khong_duoc_xoa_markup_gia_an_toan():
    b = bo()
    body = '<w:p><w:r><w:t>nội dung</w:t><w:softHyphen/><w:t>; ' + TEN + '</w:t></w:r></w:p>'
    _chan(b, word(noi_dung=body), ma='MASK_TEP_CHUA_HO_TRO')


def test_che_ten_co_xml_entity_giu_nguyen_van_map():
    ten = 'Công ty DEMO A&B'
    b = bo(seeds=((ten, 'CONG_TY', ALIAS),))
    _che(b, word('bên: Công ty DEMO A&amp;B.'), ds=[dict(gia_tri=ten, nhom='CONG_TY')])
    assert _s(b)['alias_nguyen_van'] == {ALIAS: ten}


def test_vung_rong_va_doan_trong_khong_bia_da_quet_local():
    b = bo()
    _che(b, word(noi_dung='<w:p/><w:p><w:r><w:t/></w:r></w:p>'), ds=[])
    s = _s(b)
    assert s['anh_xa'] == (None, None) and s['vung_da_doc'] == (0, 1)
    assert s['goc'] == s['da_che'] and not s['vung_da_kiem_local']


def test_kiem_map_bi_sua_trong_ram_chan_truoc_bo_sung():
    b = bo()
    _che(b, word())
    s = _s(b)
    s['alias_nguyen_van'][ALIAS] = 'nguyên văn DEMO sai'
    with pytest.raises(LoiNghiepVu):
        with b.ram.buoc(b.v) as buoc:
            tw.che_them_word((), buoc=buoc)
    assert not s and b.ram._ban_ghi is None


@pytest.mark.parametrize('buoc_bo_sung', [False, True])
@pytest.mark.parametrize('dang', ['ttl', 'huy'])
def test_khong_tai_tao_map_sau_timer_huy_giua_checkpoint_va_ghi_ram(monkeypatch, buoc_bo_sung, dang):
    b, raw = bo(), word()
    if buoc_bo_sung:
        _che(b, raw)
    luu = tw._luu_ram
    bg = []
    def het_han(buoc, *a, **kw):
        bg.append(buoc._ban_ghi)
        if dang == 'ttl':
            b.dh.tien(600)
        else:
            b.q.bao_ram(b.ma, 'HUY')
        return luu(buoc, *a, **kw)
    monkeypatch.setattr(tw, '_luu_ram', het_han)
    with pytest.raises(LoiNghiepVu):
        with b.ram.buoc(b.v) as buoc:
            if buoc_bo_sung:
                tw.che_them_word((), buoc=buoc)
            else:
                tw.che_word(raw, buoc=buoc, dinh_danh=DS)
    assert len(bg) == 1
    assert bg[0].du_lieu == {} and b.ram._ban_ghi is None


def test_loi_reader_sau_patch_khong_luu_map_hoac_tra_tep_do(monkeypatch):
    b = bo()
    doc = tw.doc_word
    dem = 0
    def sai(raw, **kw):
        nonlocal dem
        dem += 1
        if dem == 2:
            raise RuntimeError(TEN)
        return doc(raw, **kw)
    monkeypatch.setattr(tw, 'doc_word', sai)
    exc = _chan(b, word(), ma='MASK_WORD_RAM')
    assert TEN not in ''.join(traceback.format_exception(exc))


@pytest.mark.parametrize('dang', ['huy', 'loi', 'chua_ro', 'thu_hoi', 'ttl'])
def test_loi_tai_writer_don_ngay_ke_ca_caller_bat_loi_trong_handle(monkeypatch, dang):
    b = bo()
    def sai(*a, **kw):
        if dang == 'huy': raise ViecDaHuy(TEN)
        if dang == 'chua_ro': raise ChuaRo(TEN)
        if dang == 'thu_hoi':
            b.q.thu_hoi = True
            kw['kiem_huy']()
        if dang == 'ttl':
            b.dh.tien(600)
            kw['kiem_huy']()
        raise RuntimeError(TEN)
    monkeypatch.setattr(tw, 'ghi_goi', sai)
    with pytest.raises((LoiNghiepVu, ChuaRo, ViecDaHuy)) as exc:
        with b.ram.buoc(b.v) as buoc:
            try:
                tw.che_word(word(), buoc=buoc, dinh_danh=DS)
            except BaseException:
                assert 'tep_word' not in buoc._ban_ghi.du_lieu
                raise
    assert TEN not in ''.join(traceback.format_exception(exc.value))
    assert b.ram._ban_ghi is None and not b.c._tep


def test_che_bo_sung_chi_tu_nguyen_van_ram_va_van_cho_local():
    ten = 'demo sáng'
    b = bo(seeds=((ten, 'CA_NHAN', '[[MASKCN-0001]]'),))
    _che(b, word('nội dung; ' + ten + '.'), ds=[])
    assert not _s(b)['alias_nguyen_van']  # Lớp quy tắc không dùng matcher danh mục.
    with b.ram.buoc(b.v) as buoc:
        a = _s(b)['anh_xa'][0].goc.index(ten)
        tw.che_them_word(((0, UngVien(a, a + len(ten), 'CA_NHAN', 'local')),), buoc=buoc)
        assert _s(b)['alias_nguyen_van'] == {'[[MASKCN-0001]]': ten}
        assert _s(b)['tai_lieu_da_che'].vung[0].van_ban == 'nội dung; [[MASKCN-0001]].'
        assert _s(b)['vung_da_kiem_local'] == ()
        buoc.cho_ai()


@pytest.mark.parametrize('dang', ['nhom', 'offset', 'nguon', 'tien_ngay', 'khong_co_alias'])
def test_bo_sung_sai_bien_nguon_nhom_tien_ngay_khong_phat_hanh(dang):
    ten = 'demo sáng'
    b = bo(seeds=((ten, 'CA_NHAN', '[[MASKCN-0001]]'),) if dang != 'khong_co_alias' else ())
    chu = 'nội dung; ' + ten + '.; 1.000.000 VND ngày 30/10/2026.'
    _che(b, word(chu), ds=[])
    a, z, nhom, nguon = chu.index(ten), chu.index(ten) + len(ten), 'CA_NHAN', 'local'
    if dang == 'nhom': nhom = 'CONG_TY'
    elif dang == 'offset': z -= 1
    elif dang == 'nguon': nguon = 'quy_tac'
    elif dang == 'tien_ngay': a, z = chu.index('1.000'), chu.index(' VND')
    with pytest.raises(LoiNghiepVu):
        with b.ram.buoc(b.v) as buoc:
            tw.che_them_word(((0, UngVien(a, z, nhom, nguon)),), buoc=buoc)
    assert b.ram._ban_ghi is None and not b.c._tep


def test_budget_ung_vien_tinh_chung_moi_vung_khong_lap_rpc(monkeypatch):
    do = bo()
    _che(do, word())
    cap = len(_s(do)['ngan_sach']['da_tim'])
    b = bo()
    monkeypatch.setattr(tw, 'TRAN_UNG_VIEN', cap)
    _che(b, word(noi_dung=('<w:p><w:r><w:t>' + TEN + '</w:t></w:r></w:p>') * 3))
    assert len(_s(b)['ngan_sach']['da_tim']) == cap
    b = bo()
    raw = word(noi_dung='<w:p><w:r><w:t>' + TEN + '</w:t></w:r></w:p><w:p><w:r><w:t>nội dung DEMO</w:t></w:r></w:p>')
    _chan(b, raw, ma='MASK_UNG_VIEN_QUA_TRAN')


@pytest.mark.parametrize('dang', ['container_vao', 'container_ra', 'ky_tu', 'node', 'ratio'])
def test_tran_ke_thua_b1_b4_hai_chieu_khong_cat_ngam(monkeypatch, dang):
    from e_mask import zip_an_toan as za, xml_an_toan as xa
    b, raw = bo(), word()
    if dang == 'container_vao':
        monkeypatch.setattr(za, 'TEP_TOI_DA', len(raw) - 1)
    elif dang == 'container_ra':
        from e_mask import ghi_zip as gz
        ten = 'Đá'
        ds = [dict(gia_tri=ten, nhom='CONG_TY')]
        raw = word(ten)
        seeds = ((ten, 'CONG_TY', '[[MASKCT-' + 'a' * 90 + ']]'),)
        do = bo(seeds=seeds)
        _che(do, raw, ds=ds)
        cap = len(_s(do)['da_che']) - 1
        assert len(raw) <= cap
        b = bo(seeds=seeds)
        monkeypatch.setattr(gz, 'TEP_TOI_DA', cap)
        _chan(b, raw, ds=ds, ma='MASK_QUA_GIOI_HAN')
        return
    elif dang == 'ky_tu':
        monkeypatch.setattr(xa, 'KY_TU_VAO_TOI_DA', 10)
    elif dang == 'node':
        monkeypatch.setattr(xa, 'SO_NUT_TOI_DA', 1)
    else:
        monkeypatch.setattr(za, 'TY_LE_TOI_DA', 1)
    _chan(b, raw, ma='MASK_QUA_GIOI_HAN')
