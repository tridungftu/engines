"""TS-DC: đã kiểm bằng Core giả (CoreGia); không kiểm Core thật."""
import hashlib
import json
from pathlib import Path
import subprocess

from e_doi_chieu.quy_tac import CAC_QUY_TAC, kiem_bo_cung
from e_doi_chieu.tu_dien import CAP_CO_NGHIA


ROOT = Path(__file__).resolve().parents[2]


def test_ui_ts_dc_va_du_lieu_xuat_khop_loi_python():
    # Node không mạng. Không skip khi thiếu Node: đây là điều kiện của lát UI.
    result = subprocess.run(
        ["node", "e_doi_chieu/tests/ui/ts_dc.test.mjs", "--xuat-demo"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    ts = json.loads(next(line.removeprefix("TS_DC_DEMO=") for line in result.stdout.splitlines()
                         if line.startswith("TS_DC_DEMO=")))
    raw = ts["bo_quy_tac_json"].encode("utf-8")
    assert ts["bam_bo_quy_tac"] == "sha256:" + hashlib.sha256(raw).hexdigest()
    bo = json.loads(raw)
    checked = kiem_bo_cung(bo)
    assert checked["da_khai"]
    assert checked["dinh_dang_so"] == [{"nghin": " ", "thap_phan": ","}]
    assert len(CAC_QUY_TAC) == 8 and len(CAP_CO_NGHIA) == 6


def test_danh_sach_ui_khop_chinh_xac_python():
    # Đọc export JS bằng Node để phát hiện drift giữa màn và quy tắc thực sự chạy.
    script = """
import {readFile} from 'node:fs/promises';
const code = await readFile('e_doi_chieu/goi/e_doi_chieu/ui/soan_quy_tac.js', 'utf8');
const m = await import('data:text/javascript;base64,' + Buffer.from(code).toString('base64'));
console.log(JSON.stringify({quy_tac: m.QUY_TAC.map(r => r[0]), cap: m.CAP_DOI_NGHIA}));
"""
    result = subprocess.run(["node", "--input-type=module", "-e", script], cwd=ROOT,
                            capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert result.returncode == 0, result.stderr
    actual = json.loads(result.stdout)
    assert actual["quy_tac"] == list(CAC_QUY_TAC)
    assert actual["cap"] == [list(cap) for cap in CAP_CO_NGHIA]
