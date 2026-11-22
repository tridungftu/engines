"""SDK25: gói thư viện offline và cửa công khai khi Core cấp SDK."""

import shutil

import pytest
from kho_tri_thuc_sdk.engine import Engine

from e_kiem_excel.chay import app
from kiem_bam_goi import GOI, doc_lock, kiem_wheel
from kiem_doc_lap import kiem_doc_lap


def test_goi_lock_va_wheel():
    kiem_wheel(GOI)
    assert type(app) is Engine


@pytest.mark.parametrize('noi_dung', [
    'thu_vien==1.0 --hash=sha256:'+'a'*64+' # chu thich',
    'thu_vien==1.0 \\\n --hash=sha256:'+'a'*64,
    'thu_vien==1.0; python_version>="3.11" --hash=sha256:'+'a'*64,
    'thu_vien==1.0',
    '# coding: ascii\n',
    '# tiếng Việt\n',
    '\ufeff# BOM\n',
    *[ten+'==1.0 --hash=sha256:'+'a'*64
      for ten in ('kho_tri_thuc_sdk', 'Kho.Tri.Thuc.SDK', 'kho-tri-thuc')],
    '\n'.join(ten+'==1.0 --hash=sha256:'+'a'*64
              for ten in ('thu-vien', 'thu_vien')),
])
def test_lock_tu_choi_khuon_cu_va_ten_cam(tmp_path, noi_dung):
    (tmp_path/'requirements.lock').write_text(noi_dung, encoding='utf-8')
    with pytest.raises(ValueError):
        doc_lock(tmp_path)


def test_lock_cho_phep_hash_linux_cung_dong(tmp_path):
    raw = (GOI/'requirements.lock').read_text(encoding='ascii')
    raw = raw.replace('openpyxl==3.1.5', 'openpyxl==3.1.5 --hash=sha256:'+'a'*64)
    (tmp_path/'requirements.lock').write_text(raw, encoding='ascii')
    shutil.copytree(GOI/'wheels', tmp_path/'wheels')
    assert len(doc_lock(tmp_path)['openpyxl'][1]) == 2
    kiem_wheel(tmp_path)


@pytest.mark.parametrize('loi', ['thieu', 'thua', 'bam', 'sdist', 'thu_muc', 'sai_ban'])
def test_phat_hien_goi_wheel_sai(tmp_path, loi):
    shutil.copyfile(GOI/'requirements.lock', tmp_path/'requirements.lock')
    wheels = tmp_path/'wheels'
    wheels.mkdir()
    for tep in (GOI/'wheels').iterdir():
        if tep.name.startswith('openpyxl-'):
            if loi == 'thieu':
                continue
            if loi == 'sai_ban':
                shutil.copyfile(tep, wheels/tep.name.replace('3.1.5', '3.1.6'))
                continue
        shutil.copyfile(tep, wheels/tep.name)
    if loi == 'thua':
        tep = next(wheels.glob('openpyxl-*.whl'))
        shutil.copyfile(tep, wheels/tep.name.replace('-py2.py3-', '-1-py2.py3-'))
    elif loi == 'bam':
        with next(wheels.glob('openpyxl-*.whl')).open('ab') as f:
            f.write(b'DEMO')
    elif loi == 'sdist':
        (wheels/'thu_vien-1.0.tar.gz').write_bytes(b'DEMO')
    elif loi == 'thu_muc':
        (wheels/'thu_muc').mkdir()
    with pytest.raises(ValueError):
        kiem_wheel(tmp_path)


def test_import_ngoai_lock_bi_tu_choi(tmp_path):
    shutil.copyfile(GOI/'requirements.lock', tmp_path/'requirements.lock')
    (tmp_path/'demo.py').write_text('import thu_vien_chua_ghim\n', encoding='ascii')
    assert any('import bị cấm hoặc chưa ghim' in loi for loi in kiem_doc_lap(tmp_path))
