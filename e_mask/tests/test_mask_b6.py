"""MASK-B6 nội bộ đã kiểm bằng Core giả (CoreGia), Cloud tắt.

Kiểm bytes thật và các chặn; không tự nhận đã đạt Local/Office/Core thật.
"""
from dataclasses import asdict, replace
from pathlib import Path
import builtins
import io
import logging
import tempfile
import traceback
import unicodedata

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, NganEngine, Viec, ViecDaHuy

from e_mask import tep_excel as tx, tai_nguyen
from e_mask.doc_excel import doc_excel
from e_mask.kho_anh_xa_ram import KhoAnhXaRAM
from e_mask.tra_cuu_dinh_danh import UngVien
from e_mask.va_xml import chuan_bi_va
from e_mask.zip_an_toan import kiem_ban_ghi
from ho_tro_mask_b1 import excel_demo, them_phan, CT_S, S, R
from ho_tro_mask_b3 import goi_office
from ho_tro_mask_b6 import bo, TEN, ALIAS, DS, excel, moi_vung


def che(b, raw, *, ds=DS, giu=True):
    with b.ram.buoc(b.v) as buoc:
        dau = tx.che_excel(raw, buoc=buoc, dinh_danh=ds)
        if giu:
            buoc.cho_ai()
        return dau


def trang_thai(b):
    return b.ram._ban_ghi.du_lieu['tep_excel']


def chan(b, raw, *, ds=DS, ma=None):
    sentinel = object()
    ket = sentinel
    with pytest.raises(LoiNghiepVu) as exc:
        ket = che(b, raw, ds=ds)
    assert ket is sentinel and b.ram._ban_ghi is None and not b.c._tep
    assert TEN not in ''.join(traceback.format_exception(exc.value))
    if ma:
        assert exc.value.ma == ma
    return exc.value


def test_shared_rich_inline_metadata_an_so_tien_ngay_format_va_bat_bien():
    b, raw = bo(), moi_vung()
    dau = che(b, raw)
    s = trang_thai(b)
    x, y = s['tai_lieu'], doc_excel(s['da_che'], kiem_huy=lambda: None)
    assert {'shared_string', 'o', 'core', 'app', 'custom', 'custom_ten', 'ten_sheet', 'app_ten_sheet'} <= {v.ma for v in x.vung}
    for cu, moi in zip(x.vung, y.vung):
        assert moi.chu == cu.chu.replace(TEN, ALIAS)
    assert s['alias_nguyen_van'] == {ALIAS: TEN}
    assert s['giai_doan'] == 'CHO_LOCAL' and s['vung_da_kiem_local'] == ()
    assert s['vung_da_doc'] == tuple(range(len(x.vung)))
    assert dau.so_vung == len(x.vung)
    assert set(asdict(dau)) == {'bam_goc', 'bam_da_che', 'so_vung', 'so_phep_thay'}
    assert x.shared == y.shared and x.tham_chieu_chu == y.tham_chieu_chu == (((0, 'A1'), (0, 'B1')), ())
    assert x.styles == y.styles and x.gop_o == y.gop_o == (('A3:B3',),)
    assert x.epoch1904 == y.epoch1904 is False
    cells = {o.dia_chi: o for o in y.o}
    assert cells['A2'].hang_an and cells['A2'].cot_an
    assert cells['B2'].gia_tri == '1000000' and cells['B2'].kieu is None and cells['B2'].style == 2
    assert cells['C2'].gia_tri == '46325' and cells['C2'].kieu == 'n' and cells['C2'].style == 1
    assert y.styles[2]['formatCode'] == '#,##0" VND"' and y.styles[1]['formatCode'] == 'yyyy-mm-dd'
    assert next(v.chu for v in y.vung if v.o == 'E2') == '0000123'
    assert cells['D2'].gia_tri == '1' and cells['D2'].kieu == 'b'
    # Một source shared có hai nơi dùng + một source unused đều phải che.
    assert all(y.vung[i].chu == ALIAS for i in y.shared)
    assert len({(l.khoang[0].phan, l.khoang[0].dau) for l in s['kich_ban'].lenh}) == len(s['kich_ban'].lenh)
    goc, moi = x.goi.goi.zip, y.goi.goi.zip
    patches, _ = chuan_bi_va(x, s['kich_ban'], lambda: None)
    regs = {r.phan.ten: r for r in kiem_ban_ghi(goc, lambda: None)}
    for r in kiem_ban_ghi(moi, lambda: None):
        p = regs[r.phan.ten]
        if r.phan.ten not in patches:
            assert goc.goc[p.phan.le_dau:p.le_cuoi_ban_ghi] == moi.goc[r.phan.le_dau:r.le_cuoi_ban_ghi]
        else:
            a = z = 0
            for dau, cuoi, data in patches[r.phan.ten]:
                assert p.phan.du_lieu[a:dau] == r.phan.du_lieu[z:z + dau - a]
                z += dau - a
                assert r.phan.du_lieu[z:z + len(data)] == data
                a, z = cuoi, z + len(data)
            assert p.phan.du_lieu[a:] == r.phan.du_lieu[z:]
    assert not b.c._tep


@pytest.mark.parametrize('shared', [False, True])
@pytest.mark.parametrize('codec', [None, 'utf-16', 'utf-16-be'])
@pytest.mark.parametrize('dang', ['NFC', 'NFD', 'Cf', 'entity', 'st'])
def test_ten_tach_rich_run_cung_o_unicode_entity_st_va_giu_tien_ngay(shared, codec, dang):
    ten = 'Nguyễn Văn Ánh'
    if dang == 'NFD':
        ten = unicodedata.normalize('NFD', ten)
    elif dang == 'Cf':
        ten = ten.replace('Văn', 'Vă\u200bn')
    a, z = ten.index(' '), ten.rindex(' ')
    manh = [ten[:a + 1], ten[a + 1:z + 1], ten[z + 1:]]
    if dang == 'entity':
        manh[0] = manh[0].replace('ễ', '&#7877;')
    elif dang == 'st':
        manh[0] = manh[0].replace('ễ', '_x1EC5_')
    rich = ('<r><rPr><b/></rPr><t xml:space="preserve">bên: ' + manh[0] + '</t></r>'
            '<r><rPr><i/></rPr><t xml:space="preserve">' + manh[1] + '</t></r>'
            '<r><rPr><color rgb="FF123456"/></rPr><t>' + manh[2] + '; 1.000.000 VND ngày 2026-10-30.</t></r>')
    p = excel_demo(noi_dung='<row r="1"><c r="A1" t="s"><v>0</v></c></row>' if shared else
                   '<row r="1"><c r="A1" t="inlineStr"><is>' + rich + '</is></c></row>')
    p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('DEMO 1', 'bảng')
    if shared:
        them_phan(p, 'xl/sharedStrings.xml', f'<sst xmlns="{S}" count="1" uniqueCount="1"><si>' + rich + '</si></sst>',
                  CT_S + 'sharedStrings+xml', 'sharedStrings', rid='rId11', chu='xl/workbook.xml')
    if codec:
        p = {k: v.encode(codec) for k, v in p.items()}
    b = bo(seeds=((ten, 'CA_NHAN', '[[MASKCN-0001]]'),))
    che(b, goi_office(p), ds=[dict(gia_tri=ten, nhom='CA_NHAN')])
    s = trang_thai(b)
    assert s['alias_nguyen_van'] == {'[[MASKCN-0001]]': ten}
    v = next(v for v in s['tai_lieu_da_che'].vung if v.ma == 'o')
    assert v.chu == 'bên: [[MASKCN-0001]]; 1.000.000 VND ngày 2026-10-30.'
    assert len(v.manh) == 3 and [m.so_run for m in v.manh] == [0, 1, 2]


def test_shared_nhieu_sheet_moi_noi_dung_duoc_doc_lai_va_khong_doi_index():
    b = bo()
    raw = excel(shared=True, so_sheet=2)
    che(b, raw)
    s = trang_thai(b)
    y = s['tai_lieu_da_che']
    assert y.tham_chieu_chu == (((0, 'A1'), (0, 'B1'), (1, 'A1'), (1, 'B1')),)
    assert all(v.chu == ALIAS for v in y.vung if v.ma in ('o', 'shared_string'))
    assert all(o.gia_tri == '0' and o.chi_so_chu == 0 and o.kieu == 's' for o in y.o)
    assert len(s['kich_ban'].lenh) == 1
    assert all(m is s['anh_xa'][0] for i, m in enumerate(s['anh_xa']) if y.vung[i].ma == 'o')


def test_khong_ghep_ten_qua_hai_o_doc_lap(monkeypatch):
    b = bo()
    goi = []
    ham = tx._KhoExcel.tim_ung_vien
    def spy(self, chu, nhom):
        goi.append(chu)
        return ham(self, chu, nhom)
    monkeypatch.setattr(tx._KhoExcel, 'tim_ung_vien', spy)
    raw = excel(noi_dung='<row r="1"><c r="A1" t="inlineStr"><is><t>Công ty DEMO </t></is></c>'
                '<c r="B1" t="inlineStr"><is><t>Ánh Dương</t></is></c></row>')
    chan(b, raw, ma='MASK_DINH_DANH_CHUA_DAT')
    assert TEN not in goi


@pytest.mark.parametrize('dang', ['hidden', 'veryHidden', 'formula', 'formula_str', 'cache_str', 'definedNames',
    'external', 'comment', 'threaded', 'persons', 'chart', 'drawing', 'embedding', 'macro', 'unknown', 'orphan', 'cdata'])
def test_blockers_chan_ca_workbook_khong_giu_canh_bao(dang):
    p = excel_demo(noi_dung='<row r="1"><c r="A1" t="inlineStr"><is><t>' + TEN + '</t></is></c></row>')
    sheet = p['xl/worksheets/sheet1.xml']
    if dang in ('hidden', 'veryHidden'):
        p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('sheetId="1"', 'sheetId="1" state="' + dang + '"')
    elif dang in ('formula', 'formula_str', 'cache_str'):
        cell = '<c r="A1"' + (' t="str"' if dang != 'formula' else '') + '>'
        cell += ('<f>&quot;Công ty DEMO Ánh Dương&quot;</f>' if dang != 'cache_str' else '') + '<v>Công ty DEMO Ánh Dương</v></c>'
        p['xl/worksheets/sheet1.xml'] = f'<worksheet xmlns="{S}"><sheetData><row r="1">' + cell + '</row></sheetData></worksheet>'
    elif dang == 'definedNames':
        p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('</workbook>', '<definedNames/></workbook>')
    elif dang == 'external':
        p['xl/_rels/workbook.xml.rels'] = p['xl/_rels/workbook.xml.rels'].replace('</Relationships>',
             f'<Relationship Id="rId9" Type="{R}/hyperlink" Target="DEMO" TargetMode="External"/></Relationships>')
    elif dang == 'cdata':
        p['xl/worksheets/sheet1.xml'] = sheet.replace(TEN, '<![CDATA[' + TEN + ']]>')
    else:
        name = {'comment': 'xl/comments1.xml', 'threaded': 'xl/threadedComments/threadedComment1.xml',
                'persons': 'xl/persons/person.xml', 'chart': 'xl/charts/chart1.xml', 'drawing': 'xl/drawings/drawing1.xml',
                'embedding': 'xl/embeddings/oleObject1.bin', 'macro': 'xl/vbaProject.bin',
                'unknown': 'xl/DEMO-la.xml', 'orphan': 'xl/worksheets/sheet2.xml'}[dang]
        p[name] = f'<worksheet xmlns="{S}"><sheetData/></worksheet>'
    chan(bo(), goi_office(p), ma='MASK_TEP_CHUA_HO_TRO')


def test_ten_sheet_can_doi_chan_ca_tu_quy_tac_va_local():
    b = bo()
    p = excel_demo(noi_dung='<row r="1"><c r="A1" t="inlineStr"><is><t>' + TEN + '</t></is></c></row>')
    p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('DEMO 1', TEN)
    chan(b, goi_office(p), ma='MASK_TEP_CHUA_HO_TRO')
    ten = 'demo sáng'
    b = bo(seeds=((ten, 'CA_NHAN', '[[MASKCN-0001]]'),))
    p = excel_demo(noi_dung='<row r="1"><c r="A1" t="inlineStr"><is><t>nội dung</t></is></c></row>')
    p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('DEMO 1', 'nội dung; ' + ten + '.')
    che(b, goi_office(p), ds=[])
    s = trang_thai(b)
    vi = next(i for i, v in enumerate(s['tai_lieu'].vung) if v.ma == 'ten_sheet')
    with pytest.raises(LoiNghiepVu) as exc:
        with b.ram.buoc(b.v) as buoc:
            a = s['tai_lieu'].vung[vi].chu.index(ten)
            tx.che_them_excel(((vi, UngVien(a, a + len(ten), 'CA_NHAN', 'local')),), buoc=buoc)
    assert exc.value.ma == 'MASK_TEP_CHUA_HO_TRO' and b.ram._ban_ghi is None


def test_local_bo_sung_shared_tat_ca_o_chi_trong_ram_chua_phat_hanh():
    ten = 'demo sáng'
    b = bo(seeds=((ten, 'CA_NHAN', '[[MASKCN-0001]]'),))
    che(b, excel('nội dung; ' + ten + '.', shared=True, so_sheet=2), ds=[])
    s = trang_thai(b)
    vi = next(i for i, v in enumerate(s['tai_lieu'].vung) if v.so_sheet == 1 and v.o == 'B1')
    a = s['tai_lieu'].vung[vi].chu.index(ten)
    with b.ram.buoc(b.v) as buoc:
        tx.che_them_excel(((vi, UngVien(a, a + len(ten), 'CA_NHAN', 'local')),), buoc=buoc)
        assert s['alias_nguyen_van'] == {'[[MASKCN-0001]]': ten}
        assert all(v.chu == 'nội dung; [[MASKCN-0001]].' for v in s['tai_lieu_da_che'].vung if v.ma in ('o', 'shared_string'))
        assert len(s['kich_ban'].lenh) == 1 and s['vung_da_kiem_local'] == ()
        assert s['giai_doan'] == 'CHO_LOCAL'
        buoc.cho_ai()
    assert not any('tep' in ma for ma in b.app._ham)


@pytest.mark.parametrize('dang', ['khong_co_alias', 'nguon', 'offset', 'nhom', 'tien_ngay', 'overlap'])
def test_local_sai_span_nhom_nguon_hoac_tien_ngay_chan(dang):
    ten = 'demo sáng'
    b = bo(seeds=() if dang == 'khong_co_alias' else ((ten, 'CA_NHAN', '[[MASKCN-0001]]'),))
    chu = 'nội dung; ' + ten + '.; 1.000.000 VND ngày 30/10/2026.'
    che(b, excel(chu, shared=True), ds=[])
    s = trang_thai(b)
    a, z = chu.index(ten), chu.index(ten) + len(ten)
    nhom, nguon = 'CA_NHAN', 'local'
    if dang == 'nguon': nguon = 'quy_tac'
    elif dang == 'offset': z -= 1
    elif dang == 'nhom': nhom = 'CONG_TY'
    elif dang == 'tien_ngay': a, z = chu.index('1.000'), chu.index(' VND')
    muc = ((0, UngVien(a, z, nhom, nguon)),)
    if dang == 'overlap': muc += ((0, UngVien(a, z - 1, nhom, nguon)),)
    with pytest.raises(LoiNghiepVu):
        with b.ram.buoc(b.v) as buoc:
            tx.che_them_excel(muc, buoc=buoc)
    assert not s and b.ram._ban_ghi is None and not b.c._tep


def test_alias_nhieu_nguyen_van_across_cells_metadata_chan():
    b = bo()
    raw = excel(noi_dung='<row r="1"><c r="A1" t="inlineStr"><is><t>' + TEN + '</t></is></c>'
                '<c r="B1" t="inlineStr"><is><t>' + unicodedata.normalize('NFD', TEN) + '</t></is></c></row>')
    chan(b, raw, ma='MASK_MO_CHE_KHONG_DAY_DU')


def test_spy_khong_luu_map_goc_ho_so_core_ngan_tep_tam_log_stderr(monkeypatch, capsys, caplog):
    b, raw = bo(), moi_vung()
    tai_nguyen.nap_tu_goi()
    goi_tim = []
    tim = NganEngine.tim
    def spy(self, bang, **kw):
        goi_tim.append((bang, kw))
        return tim(self, bang, **kw)
    def cam(*a, **kw):
        pytest.fail('Không được lưu dữ liệu ngoài RAM.')
    mo = io.open
    tu_dien = Path(tai_nguyen.__file__).parent / 'tu_dien'
    def chi_doc_tu_dien(p, mode='r', *a, **kw):
        assert Path(p).parent == tu_dien and not any(c in mode for c in 'wax+')
        return mo(p, mode, *a, **kw)
    ghi_truoc = dict(b.c.so_lan_ghi)
    with monkeypatch.context() as mp:
        mp.setattr(NganEngine, 'tim', spy)
        for obj, name in ((NganEngine, 'lo'), (Viec, 'mo_tep'), (Viec, 'tai_tep_ra'),
                          (tempfile, 'TemporaryFile'), (tempfile, 'NamedTemporaryFile'), (tempfile, 'mkstemp'),
                          (Path, 'write_bytes'), (Path, 'write_text')):
            mp.setattr(obj, name, cam)
        mp.setattr(builtins, 'open', chi_doc_tu_dien)
        mp.setattr(io, 'open', chi_doc_tu_dien)
        caplog.set_level(logging.DEBUG)
        dau = che(b, raw)
    assert capsys.readouterr() == ('', '') and not caplog.records
    assert not b.c._tep and b.c.so_lan_ghi == ghi_truoc and TEN not in repr(dau)
    tim_ten = [kw for bang, kw in goi_tim if bang == 'dinh_danh']
    assert sum(kw['loc']['gia_tri_chuan'] == 'công ty demo ánh dương' for kw in tim_ten) == 1
    assert all(set(kw['loc']) == {'gia_tri_chuan', 'phien_ban_chuan_hoa', 'vung_du_lieu'} for kw in tim_ten)
    assert len(tim_ten) == len({kw['loc']['gia_tri_chuan'] for kw in tim_ten})


@pytest.mark.parametrize('su_kien', ['HUY', 'LOI', 'KET_THUC', 'MAT_LEASE', 'MAT_QUYEN', 'HET_HAN'])
def test_lifecycle_don_map_bytes_khi_ranh(su_kien):
    b = bo()
    che(b, excel())
    s = trang_thai(b)
    b.q.bao_ram(b.ma, su_kien)
    assert not s and b.ram._ban_ghi is None


@pytest.mark.parametrize('ttl', [60, 600, 900])
def test_ttl_tuyet_doi_retry_khong_gia_han_va_timer_don(ttl):
    b, raw = bo(ttl=ttl), excel()
    dau = che(b, raw)
    han = b.ram._ban_ghi.han
    b.dh.tien(ttl - 1)
    assert che(b, raw) == dau and b.ram._ban_ghi.han == han
    s = trang_thai(b)
    b.dh.tien(1)
    assert not s and b.ram._ban_ghi is None
    chan(b, raw, ma='MASK_ANH_XA_KHONG_CON')


@pytest.mark.parametrize('dang', ['restart', 'instance'])
def test_ram_restart_instance_khac_khong_cuu_map(dang):
    b = bo()
    che(b, excel())
    cu, s = b.ram, trang_thai(b)
    if dang == 'instance': b.q.ram_instance = 'DEMO-khac'
    b.ram = KhoAnhXaRAM(quyen=b.q, dong_ho=b.dh, hen_gio=b.dh.hen_gio)
    chan(b, excel(), ma='MASK_ANH_XA_KHONG_CON')
    assert s and cu._ban_ghi is not None
    b.q.bao_ram(b.ma, 'KET_THUC')
    assert not s


@pytest.mark.parametrize('truong', ['module', 'nguoi_gui', 'tai_lieu', 'vung'])
def test_quyen_cheo_khong_nhan_hoac_xoa_map_chu(truong):
    b = bo()
    che(b, excel())
    s = trang_thai(b)
    cu, ctx = getattr(b.q, truong), b.q.ram_ctx[b.ma]
    setattr(b.q, truong, 'THAT' if truong == 'vung' else 'DEMO-khac')
    with pytest.raises(LoiNghiepVu): che(b, excel())
    assert s
    setattr(b.q, truong, cu)
    b.q.ram_ctx[b.ma] = ctx
    b.q.bao_ram(b.ma)
    assert not s


def test_tieu_thu_mot_lan_don_bytes_chua_tu_nhan_da_mo_excel():
    b = bo()
    che(b, excel())
    s = trang_thai(b)
    b.q.cap(b.v.id, loai='mo_che', ma_yeu_cau=b.ma)
    with b.ram.buoc(b.v, loai='mo_che', ma_yeu_cau=b.ma) as buoc:
        assert buoc.du_lieu['tep_excel'] is s
    assert not s and b.ram._ban_ghi is None
    with pytest.raises(LoiNghiepVu):
        with b.ram.buoc(b.v, loai='mo_che', ma_yeu_cau=b.ma):
            pytest.fail('Không được tiêu thụ lần hai.')


@pytest.mark.parametrize('bo_sung', [False, True])
@pytest.mark.parametrize('dang', ['ttl', 'huy'])
def test_khong_dung_lai_map_sau_timer_huy_giua_checkpoint_va_ghi(monkeypatch, bo_sung, dang):
    b, raw = bo(), excel()
    if bo_sung: che(b, raw)
    luu = tx._luu_ram
    bg = []
    def don(buoc, *a, **kw):
        bg.append(buoc._ban_ghi)
        if dang == 'ttl': b.dh.tien(600)
        else: b.q.bao_ram(b.ma, 'HUY')
        return luu(buoc, *a, **kw)
    monkeypatch.setattr(tx, '_luu_ram', don)
    with pytest.raises(LoiNghiepVu):
        with b.ram.buoc(b.v) as buoc:
            if bo_sung: tx.che_them_excel((), buoc=buoc)
            else: tx.che_excel(raw, buoc=buoc, dinh_danh=DS)
    assert len(bg) == 1 and not bg[0].du_lieu and b.ram._ban_ghi is None


@pytest.mark.parametrize('dang', ['huy', 'loi', 'chua_ro', 'thu_hoi', 'ttl'])
def test_writer_loi_don_ngay_ke_ca_caller_bat_loi_trong_with(monkeypatch, dang):
    b = bo()
    def sai(*a, **kw):
        if dang == 'huy': raise ViecDaHuy(TEN)
        if dang == 'chua_ro': raise ChuaRo(TEN)
        if dang == 'thu_hoi': b.q.thu_hoi = True
        if dang == 'ttl': b.dh.tien(600)
        kw['kiem_huy']()
        raise RuntimeError(TEN)
    monkeypatch.setattr(tx, 'ghi_goi', sai)
    with pytest.raises((LoiNghiepVu, ChuaRo, ViecDaHuy)) as exc:
        with b.ram.buoc(b.v) as buoc:
            try: tx.che_excel(excel(), buoc=buoc, dinh_danh=DS)
            except BaseException:
                assert 'tep_excel' not in buoc._ban_ghi.du_lieu
                raise
    assert TEN not in ''.join(traceback.format_exception(exc.value))
    assert b.ram._ban_ghi is None and not b.c._tep


@pytest.mark.parametrize('dang', ['reader_loi', 'chu_sai', 'so_sai', 'index_sai', 'style_sai'])
def test_reader_lai_bytes_phat_hien_loi_khong_tra_workbook_do(monkeypatch, dang):
    b, raw = bo(), moi_vung()
    doc = tx.doc_excel
    dem = 0
    def sai(raw, **kw):
        nonlocal dem
        dem += 1
        x = doc(raw, **kw)
        if dem == 2:
            if dang == 'reader_loi': raise RuntimeError(TEN)
            if dang == 'chu_sai': return replace(x, vung=(replace(x.vung[0], chu='DEMO-sai'),) + x.vung[1:])
            if dang == 'index_sai': return replace(x, tham_chieu_chu=())
            if dang == 'style_sai': return replace(x, styles=())
            i = next(i for i, o in enumerate(x.o) if o.vung is None)
            return replace(x, o=x.o[:i] + (replace(x.o[i], gia_tri='999'),) + x.o[i+1:])
        return x
    monkeypatch.setattr(tx, 'doc_excel', sai)
    chan(b, raw, ma='MASK_EXCEL_RAM')


@pytest.mark.parametrize('dang', ['container_vao', 'container_ra', 'ky_tu', 'node', 'ratio', 'o', 'sheet'])
def test_tran_ke_thua_b1_b4_ca_vao_ra_khong_cat(monkeypatch, dang):
    from e_mask import zip_an_toan as za, xml_an_toan as xa, ghi_zip as gz
    b, raw = bo(), excel()
    if dang == 'container_vao': monkeypatch.setattr(za, 'TEP_TOI_DA', len(raw) - 1)
    elif dang == 'container_ra':
        ten = 'Đá'
        ds = [dict(gia_tri=ten, nhom='CONG_TY')]
        seeds = ((ten, 'CONG_TY', '[[MASKCT-' + 'a' * 90 + ']]'),)
        raw = excel(ten)
        do = bo(seeds=seeds)
        che(do, raw, ds=ds)
        cap = len(trang_thai(do)['da_che']) - 1
        assert len(raw) <= cap
        b = bo(seeds=seeds)
        monkeypatch.setattr(gz, 'TEP_TOI_DA', cap)
        chan(b, raw, ds=ds, ma='MASK_QUA_GIOI_HAN')
        return
    elif dang == 'ky_tu': monkeypatch.setattr(xa, 'KY_TU_VAO_TOI_DA', 10)
    elif dang == 'node': monkeypatch.setattr(xa, 'SO_NUT_TOI_DA', 1)
    elif dang == 'ratio': monkeypatch.setattr(za, 'TY_LE_TOI_DA', 1)
    elif dang == 'o': monkeypatch.setattr(xa, 'SO_O_TOI_DA', 0)
    else: monkeypatch.setattr(xa, 'SO_SHEET_TOI_DA', 0)
    chan(b, raw, ma='MASK_QUA_GIOI_HAN')


def test_thieu_handle_quyen_ghim_ten_moi_chan_khong_ghi_kho():
    with pytest.raises(LoiNghiepVu): tx.che_excel(excel(), buoc=None)
    b = bo()
    b.q.ram_ghim = False
    chan(b, excel(), ma='MASK_CHUOI_CHUA_GHIM')
    b = bo()
    b.q.thu_hoi = True
    chan(b, excel(), ma='MASK_MA_YEU_CAU')
    b = bo(seeds=())
    chan(b, excel())
    assert b.c.so_lan_ghi['ngan'] == 0


def test_retry_cung_ma_doi_bytes_dinh_danh_chan_va_don():
    b = bo()
    che(b, excel())
    s = trang_thai(b)
    chan(b, excel(TEN + '; nội dung'), ma='MASK_DAU_VAO_THAY_DOI')
    assert not s
    b = bo()
    che(b, excel())
    chan(b, excel(), ds=[], ma='MASK_DAU_VAO_THAY_DOI')


def test_shared_map_bi_thay_doc_lap_chan_truoc_bo_sung():
    b = bo()
    che(b, excel(shared=True))
    s = trang_thai(b)
    ds = list(s['anh_xa'])
    i = next(i for i, v in enumerate(s['tai_lieu'].vung) if v.ma == 'o')
    ds[i] = replace(ds[i], da_che='DEMO-sai')
    s['anh_xa'] = tuple(ds)
    with pytest.raises(LoiNghiepVu):
        with b.ram.buoc(b.v) as buoc:
            tx.che_them_excel((), buoc=buoc)
    assert not s and b.ram._ban_ghi is None


@pytest.mark.parametrize('shared', [False, True])
@pytest.mark.parametrize('supplementary', [False, True])
def test_o_32767_utf16_va_vuot_mot_don_vi_khong_cat(shared, supplementary):
    chu = ('a; ' * 11000)[:32765 if supplementary else 32767] + ('💡' if supplementary else '')
    b = bo()
    che(b, excel(chu, shared=shared, cach=0), ds=[])
    assert all(v.chu == chu for v in trang_thai(b)['tai_lieu_da_che'].vung if v.ma in ('o', 'shared_string'))
    chan(bo(), excel(chu + 'a', shared=shared, cach=0), ds=[], ma='MASK_QUA_GIOI_HAN')


@pytest.mark.parametrize('shared', [False, True])
@pytest.mark.parametrize('vuot', [False, True])
def test_alias_dai_khuech_dai_o_ra_32767_va_32768(shared, vuot):
    ten, alias = 'Đá', '[[MASKCT-' + 'a' * 90 + ']]'
    b = bo(seeds=((ten, 'CONG_TY', alias),))
    chu = ('a; ' * 11000)[:32767 + int(vuot) - len(alias) - 2] + '; ' + ten
    raw = excel(chu, shared=shared, cach=0)
    ds = [dict(gia_tri=ten, nhom='CONG_TY')]
    if vuot:
        chan(b, raw, ds=ds, ma='MASK_QUA_GIOI_HAN')
    else:
        che(b, raw, ds=ds)
        assert all(len(v.chu.encode('utf-16-le')) // 2 == 32767
                   and v.chu.endswith(alias) for v in trang_thai(b)['tai_lieu_da_che'].vung if v.ma in ('o', 'shared_string'))


def test_o_so_0_dau_boolean_loi_ngay_iso_style_1904_khong_bien_thanh_chu():
    noi_dung = ('<row r="1"><c r="A1" t="inlineStr"><is><t>' + TEN + '</t></is></c>'
                '<c r="B1"><v>0000123</v></c><c r="C1" t="b"><v>0</v></c>'
                '<c r="D1" t="d"><v>2026-10-30</v></c><c r="E1" t="e"><v>#N/A</v></c></row>')
    p = excel_demo(noi_dung=noi_dung)
    p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('DEMO 1', 'bảng').replace('<sheets>', '<workbookPr date1904="1"/><sheets>')
    b = bo()
    che(b, goi_office(p))
    s = trang_thai(b)
    assert s['tai_lieu_da_che'].epoch1904
    for cu, moi in zip(s['tai_lieu'].o, s['tai_lieu_da_che'].o):
        if cu.vung is None:
            assert cu.xml_goc == moi.xml_goc and cu.gia_tri == moi.gia_tri and cu.kieu == moi.kieu


def test_empty_noop_giu_nguyen_container_chua_co_local():
    b, raw = bo(), excel('', shared=True)
    che(b, raw, ds=[])
    s = trang_thai(b)
    assert s['goc'] == s['da_che'] == raw
    assert not s['kich_ban'].lenh and not s['alias_nguyen_van'] and not s['vung_da_kiem_local']


@pytest.mark.parametrize('budget', ['vi_tri', 'ky_tu_do'])
def test_budget_tinh_chung_moi_o_doc_lap(budget, monkeypatch):
    if budget == 'vi_tri': monkeypatch.setattr(tx, 'TRAN_VI_TRI', 1)
    else: monkeypatch.setattr(tx, 'TRAN_KY_TU_DO', 1)
    body = '<row r="1"><c r="A1" t="inlineStr"><is><t>' + TEN + '</t></is></c><c r="B1" t="inlineStr"><is><t>' + TEN + '</t></is></c></row>'
    chan(bo(), excel(noi_dung=body), ma='MASK_UNG_VIEN_QUA_TRAN')


def test_no_matcher_danh_muc_de_phat_hien_ten_dac_biet():
    ten = 'demo sáng'
    b = bo(seeds=((ten, 'CA_NHAN', '[[MASKCN-0001]]'),))
    che(b, excel('nội dung; ' + ten + '.'), ds=[])
    s = trang_thai(b)
    assert not s['alias_nguyen_van'] and s['goc'] == s['da_che']
    assert s['giai_doan'] == 'CHO_LOCAL' and s['vung_da_kiem_local'] == ()
    # Chưa đo độ phủ Local/R3; không coi việc giữ nguyên này là che đạt.


@pytest.mark.parametrize('du_lieu', ['tep_word', 'ho_so_ai', 'alias_nguyen_van'])
def test_khong_tron_kieu_ho_so_hoac_map_trong_cung_chuoi(du_lieu):
    b = bo()
    with pytest.raises(LoiNghiepVu) as exc:
        with b.ram.buoc(b.v) as buoc:
            buoc.du_lieu[du_lieu] = {'DEMO': 'nhạy cảm DEMO'}
            tx.che_excel(excel(), buoc=buoc, dinh_danh=DS)
    assert exc.value.ma == 'MASK_VONG_DOI_KHONG_HOP_LE' and b.ram._ban_ghi is None


@pytest.mark.parametrize('dang', ['mst', 'tai_khoan', 'da_biet'])
def test_dinh_danh_trong_o_so_chan_khong_doi_thanh_chu(dang):
    gia_tri = '0101234567' if dang == 'mst' else '1234567890123456' if dang == 'tai_khoan' else '0000123'
    ds = [dict(gia_tri=gia_tri, nhom='KHAC')] if dang == 'da_biet' else []
    raw = excel(noi_dung='<row r="1"><c r="A1"><v>' + gia_tri + '</v></c></row>')
    chan(bo(), raw, ds=ds, ma='MASK_DINH_DANH_CHUA_DAT' if dang == 'da_biet' else 'MASK_TEP_CHUA_HO_TRO')


def test_so_tien_lon_format_tien_giu_nguyen_bytes():
    from ho_tro_mask_b3 import phan_demo
    p = phan_demo()
    # Dữ liệu DEMO giữ kiểu số có style tiền, không dùng làm mã định danh.
    p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('DEMO 1', 'bảng')
    p['xl/worksheets/sheet1.xml'] = f'<worksheet xmlns="{S}"><sheetData><row r="1"><c r="A1" s="2"><v>1000000000</v></c></row></sheetData></worksheet>'
    p['xl/sharedStrings.xml'] = f'<sst xmlns="{S}" count="0" uniqueCount="0"/>'
    b = bo()
    che(b, goi_office(p), ds=[])
    s = trang_thai(b)
    assert s['goc'] == s['da_che'] and s['tai_lieu_da_che'].o[0].gia_tri == '1000000000'


@pytest.mark.parametrize('gia_tri,dat', [('1000000', True), ('1234567890123456', False)])
def test_metadata_kieu_so_giu_kieu_hoac_chan_neu_can_che(gia_tri, dat):
    from ho_tro_mask_b3 import CUSTOM, VT
    p = excel_demo(noi_dung='<row r="1"><c r="A1" t="inlineStr"><is><t>' + TEN + '</t></is></c></row>')
    p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('DEMO 1', 'bảng')
    them_phan(p, 'docProps/custom.xml', f'<Properties xmlns="{CUSTOM}" xmlns:vt="{VT}">'
              '<property fmtid="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" pid="2" name="giá trị">'
              '<vt:i8>' + gia_tri + '</vt:i8></property></Properties>',
              'application/vnd.openxmlformats-officedocument.custom-properties+xml', 'custom-properties', rid='rId4', chu='')
    b, raw = bo(), goi_office(p)
    if dat:
        che(b, raw)
        sau = trang_thai(b)['tai_lieu_da_che']
        part = next(z.du_lieu for z in sau.goi.goi.zip.phan if z.ten == 'docProps/custom.xml')
        assert ('<vt:i8>' + gia_tri + '</vt:i8>').encode() in part
    else:
        chan(b, raw, ma='MASK_TEP_CHUA_HO_TRO')
