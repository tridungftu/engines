"""Đối chiếu thẻ chỉ đọc với tài nguyên thật của gói, không sửa runtime."""
import hashlib
import json
from pathlib import Path
import subprocess
import shutil

from e_mask.kho_ngan import CAC_TIEN_TO
from e_mask.tai_nguyen import TEN_TAI_NGUYEN

GOI = Path(__file__).resolve().parents[1] / 'goi/e_mask'


def test_metadata_ui_khop_nguon_goi():
    node = shutil.which('node')
    assert node, 'Cần Node để kiểm UI-MASK.'
    uri = (Path(__file__).parent / 'ui/nap_module.mjs').as_uri()
    code = (f"import {{napModule}} from {json.dumps(uri)}; "
            "const {tienTo,tuDien}=await napModule(); console.log(JSON.stringify({tienTo,tuDien}));")
    kq = subprocess.run([node, '--input-type=module', '-e', code], capture_output=True,
                        encoding='utf-8', timeout=30, check=True)
    du_lieu = json.loads(kq.stdout)
    assert {ma for _, ma in du_lieu['tienTo']} == CAC_TIEN_TO
    assert {tep for _, tep, _ in du_lieu['tuDien']} == TEN_TAI_NGUYEN
    thu_muc = GOI / 'e_mask/tu_dien'
    bam = json.loads((thu_muc / 'SHA256.json').read_text('utf-8'))
    for tep in TEN_TAI_NGUYEN:
        assert hashlib.sha256((thu_muc / tep).read_bytes()).hexdigest() == bam[tep]


def test_schema_mo_ta_day_du_va_khai_ui_khong_doi_manifest():
    schema = json.loads((GOI / 'cau_hinh.schema.json').read_text('utf-8'))
    for muc in [schema, *schema['properties'].values()]:
        assert all(muc.get(k) for k in ('title', 'description', 'examples'))
    assert schema['examples'] == [{'thoi_han_anh_xa_giay': 600}]
    assert schema['properties']['thoi_han_anh_xa_giay']['default'] == 600
    phieu = json.loads((GOI / 'engine.json').read_text('utf-8'))
    assert phieu['bi_mat'] == []
    assert 'giao_dien_quan_tri' not in phieu
