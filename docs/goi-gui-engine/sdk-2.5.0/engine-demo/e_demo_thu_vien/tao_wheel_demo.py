"""Dựng lại wheel DEMO thuần Python bằng thư viện chuẩn, không cần mạng.

Chạy từ bất kỳ thư mục nào: python -B -X utf8 tao_wheel_demo.py [--dich <thư mục>].
Mặc định ghi vào wheels/ cạnh script; in SHA-256 để đối chiếu requirements.lock.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
from pathlib import Path
import zipfile


TEN_GOI = 'ktt_demo_thu_vien'
PHIEN_BAN = '1.0.0'
MA_NGUON = '''"""Thư viện DEMO: gọn khoảng trắng của văn bản, không có phụ thuộc."""

__version__ = '1.0.0'


def gon_khoang_trang(van_ban):
    """Gộp khoảng trắng và xuống dòng thành một dấu cách; giữ nguyên chữ."""
    return ' '.join(van_ban.split())
'''


def tao_wheel(dich):
    """Trả (đường dẫn wheel, SHA-256); bytes độc lập thời gian và đường dẫn."""
    thong_tin = f'{TEN_GOI}-{PHIEN_BAN}.dist-info'
    noi_dung = {
        f'{TEN_GOI}/__init__.py': MA_NGUON.encode('utf-8'),
        f'{thong_tin}/METADATA': (
            'Metadata-Version: 2.1\nName: ktt-demo-thu-vien\n'
            f'Version: {PHIEN_BAN}\nSummary: Thu vien DEMO gon khoang trang\n'
            'Requires-Python: >=3.11\n\n'
        ).encode('ascii'),
        f'{thong_tin}/WHEEL': (
            'Wheel-Version: 1.0\nGenerator: tao_wheel_demo\n'
            'Root-Is-Purelib: true\nTag: py3-none-any\n'
        ).encode('ascii'),
    }
    record = f'{thong_tin}/RECORD'
    bang = io.StringIO(newline='')
    ghi = csv.writer(bang, lineterminator='\n')
    for ten, raw in sorted(noi_dung.items()):
        bam = base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).rstrip(b'=').decode('ascii')
        ghi.writerow((ten, 'sha256=' + bam, len(raw)))
    ghi.writerow((record, '', ''))
    noi_dung[record] = bang.getvalue().encode('utf-8')
    bo_dem = io.BytesIO()
    with zipfile.ZipFile(bo_dem, 'w', compression=zipfile.ZIP_STORED) as wheel:
        for ten, raw in sorted(noi_dung.items()):
            info = zipfile.ZipInfo(ten, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            wheel.writestr(info, raw)
    raw = bo_dem.getvalue()
    dich = Path(dich)
    dich.mkdir(parents=True, exist_ok=True)
    tep = dich / f'{TEN_GOI}-{PHIEN_BAN}-py3-none-any.whl'
    tep.write_bytes(raw)
    return tep, hashlib.sha256(raw).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dich', type=Path, default=Path(__file__).resolve().parent / 'wheels')
    args = parser.parse_args(argv)
    tep, bam = tao_wheel(args.dich)
    print(f'{bam}  {tep.name}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
