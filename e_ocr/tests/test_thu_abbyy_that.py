import importlib.util
import json
from pathlib import Path
import threading
import time

spec = importlib.util.spec_from_file_location('thu_abbyy_that', Path(__file__).parents[1] / 'cong-cu' / 'thu_abbyy_that.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_abbyy_gia(tmp_path):
    from demo.tao_bo_demo import tao_bo_demo
    goc = tmp_path / 'DEMO'
    vao, ra, ketqua = [goc / x for x in ('vao', 'ra', 'ketqua')]
    for p in (vao, ra, ketqua):
        p.mkdir(parents=True)
    bo = tao_bo_demo(goc / 'fixture', ca_loi=False)
    cfg = goc / 'config.json'
    cfg.write_text(json.dumps({'abbyy': {'bat': True, 'thu_muc_vao': str(vao), 'thu_muc_ra': str(ra), 'thoi_han_giay': 30}}), encoding='utf-8')
    def gia():
        for _ in range(600):
            ds = list(vao.glob('*.pdf'))
            if ds:
                (ra / ds[0].name).write_bytes(bo.pdf_abbyy_gia.read_bytes())
                return
            time.sleep(.05)
    t = threading.Thread(target=gia)
    t.start()
    report, lan = mod.chay(cfg, ketqua)
    t.join()
    assert report['trang_thai'] == 'da_nhan_pdf'
    assert all(report['so_sanh']['tien'] + report['so_sanh']['ngay'])
    assert report['word']['dung_cau_truc']
    assert report['bien_nhan_loi']['trang_thai'] == 'chua_kiem_chung'
    assert json.loads((lan / 'ket-qua.json').read_text(encoding='utf-8')) == report


def test_chan_hotfolder(tmp_path):
    import pytest
    p = tmp_path / 'DEMO' / 'abbyy-hotfolder' / 'in'
    p.mkdir(parents=True)
    with pytest.raises(ValueError):
        mod.kiem_duong_dan(p)
