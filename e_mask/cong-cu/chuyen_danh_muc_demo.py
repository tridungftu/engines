"""Công cụ chuyển danh mục DEMO, chỉ RAM; mặc định chạy khô, không đọc tệp."""
import argparse
import json
from pathlib import Path
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'goi/e_mask'))
from e_mask.duyet_dinh_danh import DuyetDinhDanh
from e_mask.kho_ngan import KHAI_NGAN
from e_mask.ngan import NganBoNho


def main():
    parser = argparse.ArgumentParser(description='Chuyển danh mục giả DEMO vào ngăn RAM.')
    parser.add_argument('--ghi-demo', action='store_true', help='Ghi vào RAM DEMO; thoát sẽ mất dữ liệu.')
    doi = parser.parse_args()
    port = DuyetDinhDanh(NganBoNho(KHAI_NGAN), SimpleNamespace(xac_minh_admin=lambda: 'DEMO'))
    ds = [{'gia_tri': 'Công ty DEMO Ánh Dương', 'nhom': 'CONG_TY', 'ma_junsky': 'KH-DEMO-001'}]
    print(json.dumps(port.nhap_demo(ds, thuc_hien=doi.ghi_demo), ensure_ascii=False))


if __name__ == '__main__':
    main()
