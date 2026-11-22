"""Dữ liệu do UI Node xuất phải chạy được trên CoreGia với nguyên parser engine."""
import json
from pathlib import Path
import shutil
import subprocess

from kho_tri_thuc_sdk.thu import CoreGia
from e_kiem_excel.chay import app
from e_kiem_excel.bo_nhom import doc_bo_nhom
from e_kiem_excel.doc_tong_quat import doc_khuon

TESTS = Path(__file__).resolve().parent
GOI = TESTS.parent/'goi/e_kiem_excel'


def test_ui_node_va_du_lieu_xuat_thuc_chay_core_gia(tmp_path):
    node = shutil.which('node')
    assert node, 'Cần Node để nghiệm thu TS-EX, không bỏ qua test UI.'
    run = subprocess.run([node, '--test', str(TESTS/'ui/tham_so.test.mjs')], capture_output=True,
                         text=True, encoding='utf-8', timeout=30)
    assert run.returncode == 0, run.stdout + run.stderr
    ra = tmp_path/'tham-so-DEMO.json'
    run = subprocess.run([node, str(TESTS/'ui/xuat_demo.mjs'), str(ra)], capture_output=True,
                         text=True, encoding='utf-8', timeout=30)
    assert run.returncode == 0, run.stdout + run.stderr
    ds = json.loads(ra.read_text(encoding='utf-8'))
    assert len(ds) == 6
    for demo in ds:
        ts = demo['tham_so']
        if ts.get('bo_nhom_json'):
            assert doc_bo_nhom(ts['bo_nhom_json'])
        if ts.get('khuon_cot_json'):
            assert doc_khuon(ts['khuon_cot_json'])
        core = CoreGia()
        tep = core.them_tep('bang-DEMO.xlsx', (GOI/demo['tep_demo']).read_bytes())
        kq = core.chay_thu(app, demo['nang_luc'], {'loai':'tep','tep':tep}, tham_so=ts)
        assert kq['trang_thai'] == 'XONG', kq
