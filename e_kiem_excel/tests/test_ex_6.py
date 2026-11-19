"""Hồi quy EX-6: bytes gói và đường ghi báo cáo không tạo tệp tạm."""

from io import BytesIO
import json
from pathlib import Path

import openpyxl
import pytest

from kiem_bam_goi import GOI, KIEM_KE, kiem


def test_bam_nguyen_trang_va_phat_hien_thay_doi(tmp_path):
    import shutil
    ban_sao = tmp_path/'goi'
    shutil.copytree(GOI, ban_sao)
    kiem(ban_sao, KIEM_KE)
    with (ban_sao/'README.md').open('ab') as f:
        f.write(b'\nDEMO thay doi\n')
    with pytest.raises(ValueError, match='không khớp'):
        kiem(ban_sao, KIEM_KE)


def test_bao_cao_khong_tao_tep_tam(monkeypatch):
    from openpyxl.worksheet import _writer
    from e_kiem_excel.chay import app
    from kho_tri_thuc_sdk.thu import CoreGia
    from sinh_demo import bang_kl

    def cam(*args, **kwargs):
        raise AssertionError('Báo cáo phải ghi cả XML worksheet trong RAM.')

    monkeypatch.setattr(_writer, 'create_temporary_file', cam)
    core = CoreGia()
    tep = core.them_tep('bang-DEMO.xlsx', bang_kl())
    kq = core.chay_thu(app, 'excel.toan_ven@1', {'loai':'tep','tep':tep},
                        tham_so={'o_dich':'BTH!J39', 'kiem_nguon_kl':True})
    assert kq['trang_thai'] == 'XONG'
    tr = kq['ket_qua']['truong']
    with BytesIO(core.doc_tep(tr['tep_bao_cao']['tep_id'])) as raw:
        wb = openpyxl.load_workbook(raw)
        try:
            assert len(wb.sheetnames) == 15
            assert wb['K8 Tung dong'].max_row > 30
        finally:
            wb.close()
    assert json.loads(core.doc_tep(tr['tep_json']['tep_id']))['k8_nguon']
