"""Hiệu năng Excel trên CoreGia; chỉ dữ liệu DEMO sinh trong RAM."""
import cProfile
from contextlib import ExitStack
import io
import json
from pathlib import Path
import pstats
import sys
from time import perf_counter
from types import SimpleNamespace

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu, ViecDaHuy

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'goi/e_mask'))

from e_mask import tep_excel as tx
from ho_tro_mask_b6 import bo, excel, DS, TEN, ALIAS, moi_vung


def nhieu_hang(so_hang, *, cach=8):
    """Năm cột: tên cần che, văn bản thường, số, tiền, ngày thật."""
    dong = []
    for i in range(1, so_hang + 1):
        dong.append(f'<row r="{i}"><c r="A{i}" t="inlineStr"><is><t>{TEN}</t></is></c>'
                    f'<c r="B{i}" t="inlineStr"><is><t>nội dung</t></is></c>'
                    f'<c r="C{i}"><v>123</v></c>'
                    f'<c r="D{i}" t="inlineStr"><is><t>1.000.000 VND</t></is></c>'
                    f'<c r="E{i}" t="inlineStr"><is><t>2026-10-30</t></is></c></row>')
    return excel(noi_dung=''.join(dong), cach=cach)


def do(so_hang, *, profiler=False, cach=8, truoc=False, vuot_tran=False):
    raw, b = nhieu_hang(so_hang, cach=cach), bo()
    module = tx
    hoan = ExitStack()
    if truoc:
        import subprocess
        import types
        from unittest.mock import patch
        from e_mask import doc_excel as doc, va_xml, ghi_zip
        doc_cu = types.ModuleType('e_mask._b6c_doc_truoc')
        sys.modules[doc_cu.__name__] = doc_cu
        source = subprocess.check_output(['git', 'show', 'HEAD:e_mask/goi/e_mask/e_mask/doc_excel.py'])
        exec(compile(source, '<B6c-doc-truoc>', 'exec'), doc_cu.__dict__)
        # Giữ identity DTO để writer hiện hành nhận bản đọc HEAD.
        for ten in ('ExcelDaDoc', 'VungExcel', 'ManhExcel', 'OExcel'):
            setattr(doc_cu, ten, getattr(doc, ten))
        module = types.ModuleType('e_mask._b6c_truoc')
        sys.modules[module.__name__] = module
        source = subprocess.check_output(['git', 'show', 'HEAD:e_mask/goi/e_mask/e_mask/tep_excel.py'])
        exec(compile(source, '<B6c-truoc>', 'exec'), module.__dict__)
        module.doc_excel = doc_cu.doc_excel
        for m in (va_xml, ghi_zip):
            hoan.enter_context(patch.object(m, 'doc_excel', doc_cu.doc_excel))
    dem = [0]
    ham = b.q.xac_minh
    def xac_minh(*a, **kw):
        dem[0] += 1
        return ham(*a, **kw)
    b.q.xac_minh = xac_minh
    pr = cProfile.Profile() if profiler else None
    # Primitive được gọi trực tiếp nên harness bật đúng vòng gia hạn SDK
    # như Engine.chay(); không tắt kiểm lease để lấy số đo baseline dài.
    from kho_tri_thuc_sdk.engine import _GiaHan
    gia_han = _GiaHan(b.v._dt, b.v, SimpleNamespace(han_giu_giay=60, khoang_gia_han=20))
    gia_han.start()
    dau = perf_counter()
    ket, ma_loi = None, None
    try:
        if pr:
            pr.enable()
        with b.ram.buoc(b.v) as buoc:
            ket = module.che_excel(raw, buoc=buoc, dinh_danh=DS)
    except LoiNghiepVu as exc:
        if not vuot_tran or exc.ma != 'MASK_QUA_GIOI_HAN':
            raise
        ma_loi = exc.ma
    finally:
        if pr:
            pr.disable()
        gia_han.dung()
        hoan.close()
    kq = dict(so_hang=so_hang, so_cot=5, bytes=len(raw),
              giay=round(perf_counter() - dau, 4), xac_minh=dem[0],
              cach=cach, truoc=truoc, ma_loi=ma_loi,
              bam_da_che=ket.bam_da_che if ket else None,
              so_phep_thay=ket.so_phep_thay if ket else None)
    if pr:
        out = io.StringIO()
        pstats.Stats(pr, stream=out).strip_dirs().sort_stats('cumtime').print_stats(30)
        kq['profiler'] = out.getvalue()
    return kq


def test_chu_lap_chi_do_mot_lan_nhung_van_tinh_du_budget(monkeypatch):
    b, dem = bo(), []
    thu = tx.che.thu_thap_ung_vien
    def spy(chu, *a):
        dem.append(chu)
        return thu(chu, *a)
    monkeypatch.setattr(tx.che, 'thu_thap_ung_vien', spy)
    with b.ram.buoc(b.v) as buoc:
        tx.che_excel(nhieu_hang(10), buoc=buoc, dinh_danh=DS)
        s = buoc.du_lieu['tep_excel']
        assert dem.count(TEN) == 1
        assert s['alias_nguyen_van'] == {ALIAS: TEN}
        assert sum(v.chu == ALIAS for v in s['tai_lieu_da_che'].vung) == 10
        assert len(s['ngan_sach']['vi_tri']) >= 10
    assert b.ram._ban_ghi is None and not b.c._tep


@pytest.mark.parametrize('budget', ['vi_tri', 'ky_tu_do'])
def test_cache_khong_lam_giam_budget(budget, monkeypatch):
    b = bo()
    if budget == 'vi_tri':
        monkeypatch.setattr(tx, 'TRAN_VI_TRI', 2)
    else:
        monkeypatch.setattr(tx, 'TRAN_KY_TU_DO', len(TEN) * 3)
    with pytest.raises(LoiNghiepVu) as exc:
        with b.ram.buoc(b.v) as buoc:
            tx.che_excel(nhieu_hang(10), buoc=buoc, dinh_danh=DS)
    assert exc.value.ma == 'MASK_UNG_VIEN_QUA_TRAN'
    assert b.ram._ban_ghi is None


def test_cache_khong_gop_chu_khac_byte_cung_alias():
    import unicodedata
    nfd = unicodedata.normalize('NFD', TEN)
    body = (f'<row r="1"><c r="A1" t="inlineStr"><is><t>{TEN}</t></is></c>'
            f'<c r="B1" t="inlineStr"><is><t>{nfd}</t></is></c></row>')
    b = bo()
    with pytest.raises(LoiNghiepVu) as exc:
        with b.ram.buoc(b.v) as buoc:
            tx.che_excel(excel(noi_dung=body), buoc=buoc, dinh_danh=DS)
    assert exc.value.ma == 'MASK_MO_CHE_KHONG_DAY_DU'
    assert b.ram._ban_ghi is None


@pytest.mark.parametrize('truong', ['module', 'nguoi_gui', 'tai_lieu', 'vung', 'thu_hoi', 'ram_phap_nhan', 'ram_han'])
@pytest.mark.parametrize('cach', ['so_callback', 'thoi_gian'])
def test_quyen_doi_khi_cache_con_hieu_luc_bi_kiem_lai(truong, cach, monkeypatch):
    b = bo()
    with pytest.raises(LoiNghiepVu):
        with b.ram.buoc(b.v) as buoc:
            luot = tx._BuocExcel(buoc)
            setattr(b.q, truong, True if truong == 'thu_hoi' else
                    b.dh() - 1 if truong == 'ram_han' else
                    'THAT' if truong == 'vung' else 'DEMO-khac')
            if cach == 'thoi_gian':
                monkeypatch.setattr(tx, 'monotonic', lambda: luot._luc + .051)
                luot.kiem()
            else:
                for _ in range(4096):
                    luot.kiem()
            pytest.fail('Phải dừng khi quyền hoặc deadline thay đổi.')
    assert b.ram._ban_ghi is None


@pytest.mark.parametrize('dang', ['huy', 'ttl', 'lifecycle'])
def test_checkpoint_cuc_bo_khong_cho_den_rpc(dang):
    b = bo()
    with pytest.raises((ViecDaHuy, LoiNghiepVu)):
        with b.ram.buoc(b.v) as buoc:
            luot = tx._BuocExcel(buoc)
            if dang == 'huy':
                b.v._huy.set()
            elif dang == 'ttl':
                b.dh.tien(600, chay_timer=False)
            else:
                b.q.bao_ram(b.ma, 'MAT_LEASE')
            for _ in range(64):
                luot.kiem()
            pytest.fail('Phải dừng ở checkpoint cục bộ.')
    assert b.ram._ban_ghi is None


@pytest.mark.parametrize('dang', ['chu', 'so', 'cay', 'zip', 'ban_ghi', 'style'])
def test_reader_cache_tra_ban_doc_doc_lap(dang):
    from dataclasses import replace
    from e_mask.doc_excel import doc_excel
    b, raw = bo(), moi_vung()
    with b.ram.buoc(b.v) as buoc:
        luot = tx._BuocExcel(buoc)
        x = doc_excel(raw, kiem_huy=luot.kiem)
        y = doc_excel(raw, kiem_huy=luot.kiem)
        assert x == replace(y, goi=x.goi)
        if dang == 'chu':
            object.__setattr__(x.vung[0], 'chu', 'DEMO-sai')
            assert y.vung[0].chu != 'DEMO-sai'
        elif dang == 'so':
            object.__setattr__(x.o[0], 'gia_tri', 'DEMO-sai')
            assert y.o[0].gia_tri != 'DEMO-sai'
        elif dang == 'cay':
            x.goi.goi.cay['xl/workbook.xml'].clear()
            assert len(y.goi.goi.cay['xl/workbook.xml'])
        elif dang == 'zip':
            object.__setattr__(x.goi.goi.zip.phan[0], 'crc', -1)
            assert y.goi.goi.zip.phan[0].crc != -1
        elif dang == 'ban_ghi':
            object.__setattr__(x.goi.ban_ghi[0].phan, 'crc', -1)
            assert y.goi.ban_ghi[0].phan.crc != -1
        else:
            assert x.styles[0] is not y.styles[0]
        z = doc_excel(raw, kiem_huy=luot.kiem)
        assert z == replace(y, goi=z.goi)
        luot.doc_excel_cache.clear()


@pytest.mark.parametrize('raw', [excel(), moi_vung()])
def test_ban_cache_va_ban_doc_moi_cung_duoc_writer_chap_nhan(raw):
    from dataclasses import fields
    from e_mask.doc_excel import doc_excel
    from e_mask.va_xml import doc_lai_nguon
    b = bo()
    with b.ram.buoc(b.v) as buoc:
        luot = tx._BuocExcel(buoc)
        co_cache = doc_excel(raw, kiem_huy=luot.kiem)
        khong_cache = doc_lai_nguon(co_cache, buoc.kiem)
        # Đọc nguồn ngoài primitive (đường B7) phải giữ cả header-only.
        assert co_cache.goi.ban_ghi == khong_cache.goi.ban_ghi
        assert all(not x.phan.du_lieu for x in co_cache.goi.ban_ghi)
        assert co_cache.goi.goi.zip == khong_cache.goi.goi.zip
        for f in fields(co_cache):
            if f.name != 'goi':
                assert getattr(co_cache, f.name) == getattr(khong_cache, f.name)
        # Đường ngược lại cũng phải qua kiểm writer trong cùng lượt.
        doc_lai_nguon(khong_cache, luot.kiem)


@pytest.mark.parametrize('co_cache', [True, False])
def test_writer_van_chan_header_bi_sua_trong_ban_doc(co_cache):
    from e_mask.doc_excel import doc_excel
    from e_mask.va_xml import doc_lai_nguon
    b = bo()
    with pytest.raises(LoiNghiepVu) as exc:
        with b.ram.buoc(b.v) as buoc:
            luot = tx._BuocExcel(buoc)
            kiem = luot.kiem if co_cache else buoc.kiem
            doc = doc_excel(excel(), kiem_huy=kiem)
            object.__setattr__(doc.goi.ban_ghi[0].phan, 'crc', -1)
            doc_lai_nguon(doc, kiem)
    assert exc.value.ma == 'MASK_TEP_CHUA_HO_TRO'


@pytest.mark.parametrize('dang', ['van_ban', 'tep'])
def test_b7_doi_primitive_khong_giu_cache_hoac_handle(dang, monkeypatch):
    from ho_tro_mask_b7 import bo as bo_tep, chuan_bi_het, giao, chay
    da_tao, cls = [], tx._BuocExcel
    class Spy(cls):
        def __init__(self, *a):
            super().__init__(*a)
            da_tao.append(self)
    monkeypatch.setattr(tx, '_BuocExcel', Spy)
    b = bo_tep('xlsx', dang=dang)
    assert chuan_bi_het(b)['trang_thai'] == 'XONG'
    assert len(da_tao) == 1
    assert da_tao[0].goc is None and not da_tao[0].doc_excel_cache
    giao(b)
    ket = chay(b)
    assert ket['trang_thai'] == 'XONG', ket.get('loi')
    assert len(da_tao) == 2 and da_tao[0] is not da_tao[1]
    assert all(x.goc is None and not x.doc_excel_cache for x in da_tao)
    assert b.cong.dem_chot == 1
    b.q.bao_ram(b.ctx.ma_yeu_cau, 'KET_THUC')
    assert b.ram._ban_ghi is None


def test_cache_reader_va_handle_duoc_don_ca_thanh_cong_va_loi(monkeypatch):
    da_tao, cls = [], tx._BuocExcel
    class Spy(cls):
        def __init__(self, *a):
            super().__init__(*a)
            da_tao.append(self)
    monkeypatch.setattr(tx, '_BuocExcel', Spy)
    for raw in (excel(), b'DEMO khong phai ZIP'):
        b = bo()
        try:
            with b.ram.buoc(b.v) as buoc:
                tx.che_excel(raw, buoc=buoc, dinh_danh=DS)
        except LoiNghiepVu:
            assert raw.startswith(b'DEMO')
        assert da_tao[-1].goc is None and not da_tao[-1].doc_excel_cache


def test_so_rpc_khong_tang_theo_tung_o():
    kq = do(200)
    assert kq['xac_minh'] < 1000  # Trước sửa: hơn 154.000, không ghim tốc độ CI.


@pytest.mark.parametrize('codec', ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-be'])
@pytest.mark.parametrize('chu', [TEN, 'Ánh\u200b Dương', 'A\u0301nh', 'DEMO 😀',
                                'a&amp;b', '_x005F_x000D_', '', 'a\nb'])
def test_map_nhanh_bang_nguyen_map_lexical_cu(codec, chu):
    from xml.etree import ElementTree as ET
    from e_mask.doc_excel import _map_excel
    from e_mask.xml_excel import map_xml
    from ho_tro_mask_b1 import S, R
    raw = (f'<worksheet xmlns="{S}" xmlns:r="{R}"><sheetData><row r="1">'
           '<c r="A1" t="inlineStr"><is><r><t xml:space="preserve">' + chu + '</t></r>'
           '<r><t> DEMO</t></r></is></c><c r="B1"><v>123</v></c><c r="C1"/>'
           '</row><row r="2"/></sheetData></worksheet>').encode(codec)
    root = ET.fromstring(raw)
    assert _map_excel(raw, root, lambda: None) == map_xml(raw, root, lambda: None)


def test_encoding_ngoai_utf8_sau_khai_bao_dai_van_di_map_cu(monkeypatch):
    from xml.etree import ElementTree as ET
    from e_mask import doc_excel as doc
    from ho_tro_mask_b1 import S
    raw = ('<?xml version="1.0"' + ' ' * 256 + 'encoding="iso-8859-1"?>'
           f'<worksheet xmlns="{S}"><sheetData/></worksheet>').encode('ascii')
    root = ET.fromstring(raw)
    dem, cu = [], doc.map_xml
    def spy(*a):
        dem.append(True)
        return cu(*a)
    monkeypatch.setattr(doc, 'map_xml', spy)
    assert doc._map_excel(raw, root, lambda: None) == cu(raw, root, lambda: None)
    assert dem == [True]


if __name__ == '__main__':
    print(json.dumps(do(int(sys.argv[1]), profiler='--profile' in sys.argv,
                        cach=0 if '--khong-nen' in sys.argv else 8,
                        truoc='--truoc' in sys.argv,
                        vuot_tran='--vuot-tran' in sys.argv), ensure_ascii=False, indent=2))
