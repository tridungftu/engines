"""MASK-3: kho tạm đa tiến trình, dữ liệu giả DEMO, không có nội dung gốc."""
from hashlib import sha256
import json
import multiprocessing
import os
from pathlib import Path
import sys

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu

GOI = Path(__file__).resolve().parents[1] / 'goi/e_mask'
sys.path.insert(0, str(GOI))
from e_mask import kho_tam
from e_mask.kho_tam import KhoTam

BAM = sha256(b'DEMO').hexdigest()
TEN = 'Công ty DEMO Ánh Dương'
TOAN_VAN = TEN + '; 1.000.000 VND; 30/10/2026; nội dung gốc DEMO.'


def ghi(kho, ma='luot-demo', **doi):
    return kho.ghi(vung='DEMO', ma_luot=ma, ma_yeu_cau=TEN, bam_dau_vao=BAM, **doi)


def tranh_ghi(thu_muc, hang, bat_dau):
    kho = KhoTam(thu_muc)
    if not bat_dau.wait(10):
        raise RuntimeError('Hết hạn đợi DEMO.')
    for i in range(25):
        ghi(kho, f'luot-demo-{hang}-{i}')
        ghi(kho, 'luot-demo-chung')


def giu_khoa(thu_muc, da_khoa, tha):
    with KhoTam(thu_muc)._khoa():
        da_khoa.set()
        if not tha.wait(10):
            raise RuntimeError('Hết hạn giữ khóa DEMO.')


def test_hai_tien_trinh_tranh_ghi_khong_mat_dau(tmp_path):
    ctx = multiprocessing.get_context('spawn')
    bat_dau = ctx.Event()
    cac_tien_trinh = [ctx.Process(target=tranh_ghi, args=(str(tmp_path), i, bat_dau)) for i in range(2)]
    for p in cac_tien_trinh:
        p.start()
    bat_dau.set()
    for p in cac_tien_trinh:
        p.join(25)
        assert not p.is_alive()
        assert p.exitcode == 0
    du_lieu = json.loads((tmp_path / 'mask.json').read_text('utf-8'))
    assert len(du_lieu['luot']) == 51
    assert not list(tmp_path.glob('*.tam'))


def test_khoa_da_tien_trinh_het_han_bao_loi_khong_fallback(tmp_path):
    ctx = multiprocessing.get_context('spawn')
    da_khoa, tha = ctx.Event(), ctx.Event()
    p = ctx.Process(target=giu_khoa, args=(str(tmp_path), da_khoa, tha))
    p.start()
    try:
        assert da_khoa.wait(10)
        with pytest.raises(LoiNghiepVu) as exc:
            ghi(KhoTam(tmp_path, cho_khoa_giay=0.08))
        assert exc.value.ma == 'MASK_KHO_TAM_LOI'
        assert not (tmp_path / 'mask.json').exists()
    finally:
        tha.set()
        p.join(10)
    assert p.exitcode == 0


def test_byte_kho_tam_chi_bam_ma_so_khong_ten_toan_van(tmp_path):
    kho = KhoTam(tmp_path)
    ghi(kho, TOAN_VAN, trang_thai=3, bam_chot=BAM)
    for tep in tmp_path.iterdir():
        raw = tep.read_bytes()
        assert TEN.encode('utf-8') not in raw
        assert TOAN_VAN.encode('utf-8') not in raw
        assert b'gia_tri' not in raw and b'van_ban' not in raw
        assert b'1.000.000' not in raw
    assert TEN not in repr(kho) and str(tmp_path) not in repr(kho)


@pytest.mark.parametrize('noi_dung', ['', '{}', '{', '{"phien_ban":1,"luot":{},"luot":{}}',
                                     '{"phien_ban":1,"luot":{},"van_ban":"DEMO"}',
                                     '{"phien_ban":true,"luot":{}}'])
def test_hong_khong_tao_lai_kho_rong(tmp_path, noi_dung):
    tep = tmp_path / 'mask.json'
    tep.write_text(noi_dung, encoding='utf-8')
    with pytest.raises(LoiNghiepVu) as exc:
        ghi(KhoTam(tmp_path))
    assert exc.value.ma == 'MASK_KHO_TAM_LOI'
    assert str(tmp_path) not in str(exc.value)
    assert tep.read_text('utf-8') == noi_dung


@pytest.mark.parametrize('giai_doan', ['doc', 'ghi', 'doi_ten'])
def test_loi_io_khong_lo_du_lieu_khong_thanh_cong_gia(tmp_path, monkeypatch, giai_doan):
    kho = KhoTam(tmp_path)
    ghi(kho)
    truoc = (tmp_path / 'mask.json').read_bytes()
    def hong(*a, **kw):
        raise PermissionError(TOAN_VAN + str(tmp_path))
    if giai_doan == 'doc':
        monkeypatch.setattr(kho, '_doc', hong)
    elif giai_doan == 'ghi':
        monkeypatch.setattr(kho_tam.os, 'fsync', hong)
    else:
        monkeypatch.setattr(kho_tam.os, 'replace', hong)
    with pytest.raises(LoiNghiepVu) as exc:
        ghi(kho, 'khac-demo')
    assert exc.value.ma == 'MASK_KHO_TAM_LOI'
    assert TEN not in str(exc.value) and str(tmp_path) not in str(exc.value)
    assert (tmp_path / 'mask.json').read_bytes() == truoc


def test_cung_luot_khac_noi_dung_la_xung_dot(tmp_path):
    kho = KhoTam(tmp_path)
    ghi(kho)
    with pytest.raises(LoiNghiepVu) as exc:
        kho.ghi(vung='DEMO', ma_luot='luot-demo', ma_yeu_cau=TEN, bam_dau_vao='f' * 64)
    assert exc.value.ma == 'MASK_XUNG_DOT' and exc.value.thu_lai_duoc


def test_giu_bam_chot_khi_giao_lai_va_tach_vung(tmp_path):
    kho = KhoTam(tmp_path)
    cu = ghi(kho, trang_thai=3, bam_chot=BAM)
    assert ghi(KhoTam(tmp_path)) == cu
    assert ghi(kho, trang_thai=3)['chot'] == BAM
    that_gia = kho.ghi(vung='THAT', ma_luot='luot-demo', ma_yeu_cau=TEN, bam_dau_vao=BAM)
    assert that_gia['tuong_quan'] != cu['tuong_quan']
    assert len(json.loads((tmp_path / 'mask.json').read_text('utf-8'))['luot']) == 2


def test_duong_dan_dung_phieu(tmp_path, monkeypatch):
    monkeypatch.setenv('KTT_ENGINE_DU_LIEU', str(tmp_path / 'du-lieu-demo'))
    ghi(KhoTam())
    assert (tmp_path / 'du-lieu-demo/mask.json').is_file()
    monkeypatch.delenv('KTT_ENGINE_DU_LIEU')
    monkeypatch.setenv('PROGRAMDATA', str(tmp_path))
    if os.name == 'nt':
        ghi(KhoTam())
        assert (tmp_path / 'KhoTriThuc/engines/e_mask/du-lieu/mask.json').is_file()
    else:
        with pytest.raises(LoiNghiepVu) as exc:
            KhoTam()
        assert exc.value.ma == 'MASK_KHO_TAM_LOI'


@pytest.mark.parametrize('duong_dan', ['', 'du-lieu-demo-tuong-doi', str(GOI)])
def test_khong_ghi_trong_goi_hoac_duong_dan_sai(monkeypatch, duong_dan):
    monkeypatch.setenv('KTT_ENGINE_DU_LIEU', duong_dan)
    with pytest.raises(LoiNghiepVu) as exc:
        KhoTam()
    assert exc.value.ma == 'MASK_KHO_TAM_LOI'


def test_thu_muc_khong_ghi_duoc(tmp_path):
    tep = tmp_path / 'tep-demo'
    tep.write_text('DEMO', encoding='utf-8')
    with pytest.raises(LoiNghiepVu) as exc:
        ghi(KhoTam(tep))
    assert exc.value.ma == 'MASK_KHO_TAM_LOI'


def test_khong_cho_noi_dung_vao_truong_bam(tmp_path):
    with pytest.raises(LoiNghiepVu) as exc:
        ghi(KhoTam(tmp_path), bam_chot=TOAN_VAN)
    assert exc.value.ma == 'MASK_KHO_TAM_LOI'
    assert not (tmp_path / 'mask.json').exists()
