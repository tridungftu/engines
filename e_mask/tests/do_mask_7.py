"""Đo DEMO MASK-7; stdout chỉ số đo, không ghi tài liệu/tệp kết quả.

Chạy mỗi ca trong tiến trình mới; không phải test tốc độ có ngưỡng đạt/rớt.
"""
import argparse
import ctypes
from datetime import datetime, timezone
import gc
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
import time
import tracemalloc
import zlib

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'goi/e_mask'))
from ho_tro_khao_sat_tep import (NGUON, RULES, TEN, chu_xml, excel_demo,
                               nap_nguon, so_zip, word_demo)


def ram_dinh():
    if os.name == 'nt':
        from ctypes import wintypes
        class BoDem(ctypes.Structure):
            _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
                (n, ctypes.c_size_t) for n in ('PeakWorkingSetSize', 'WorkingSetSize',
                'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage',
                'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]
        psapi, kernel = ctypes.WinDLL('psapi'), ctypes.WinDLL('kernel32')
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(BoDem), wintypes.DWORD]
        dem = BoDem()
        dem.cb = ctypes.sizeof(dem)
        if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(dem), dem.cb):
            raise OSError('Không đo được RAM tiến trình DEMO.')
        return dem.PeakWorkingSetSize
    import resource
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value if sys.platform == 'darwin' else value * 1024


def tao_chu(n, kieu):
    if kieu == 'lap':
        don_vi = TEN + ' DEMO; 1.000.000 VND; 30/10/2026. '
        return (don_vi * (n // len(don_vi) + 1))[:n]
    rng = random.Random(7)
    # Có cả tiền/ngày và Unicode; entropy khác fixture lặp, vẫn hoàn toàn DEMO.
    duoi = ' DEMO; 1.000.000 VND; 30/10/2026; ánh sáng. '
    ds = []
    while sum(map(len, ds)) < n:
        ds.append(TEN + ' ' + rng.randbytes(200).hex() + duoi)
    return ''.join(ds)[:n]


def do_ca(loai, n, kieu):
    excel, _, rev = nap_nguon()
    chu = tao_chu(n, kieu)
    dau = None
    if loai == 'docx':
        dau = word_demo(chu)
        xu_ly = lambda: rev.accept_tracked_changes(dau)[0]
    elif loai == 'xlsx':
        dau = excel_demo(chu)
        def xu_ly():
            kq = excel.ExcelWorkbook(dau, 'DEMO.xlsx').mask(RULES)
            assert kq.output and not kq.blockers
            return kq.output
    else:
        from kho_tri_thuc_sdk.thu import CoreGia
        from e_mask.chay import tao_app
        from ho_tro_duyet_lich_su import DuyetDinhDanh
        from e_mask.kho_ngan import KHAI_NGAN
        from e_mask.ngan import NganBoNho
        from ho_tro_ngan import ADMIN, QuyenNganDemo
        ngan, quyen, core = NganBoNho(KHAI_NGAN), QuyenNganDemo(), CoreGia()
        DuyetDinhDanh(ngan, ADMIN).nhap_demo([
            {'gia_tri': TEN, 'nhom': 'KHAC', 'ma_junsky': 'KH-DEMO-007'}], thuc_hien=True)
        app = tao_app(ngan=ngan, quyen=quyen)
        def xu_ly():
            ma = core.giao_viec('mask.che_van_ban@1', {'loai': 'van_ban', 'van_ban': chu})
            quyen.cap(ma)
            core.chay(app)
            kq = core.xem(ma)
            assert kq['trang_thai'] == 'XONG', kq.get('loi')
            return kq['ket_qua']['van_ban_da_che']['van_ban']
    gc.collect()
    ram_truoc = ram_dinh()
    tracemalloc.start()
    bat_dau = time.perf_counter()
    out = xu_ly()
    giay = time.perf_counter() - bat_dau
    _, dinh = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    ram_sau = ram_dinh()
    kq = {'loai': loai, 'kich_thuoc_chu_fixture': n, 'kieu': kieu,
          'giay_xu_ly': round(giay, 6), 'tracemalloc_dinh_byte': dinh,
          'ram_dinh_tien_trinh_truoc_byte': ram_truoc, 'ram_dinh_tien_trinh_sau_byte': ram_sau,
          'ky_tu_vao': len(chu) if dau is None else chu_xml(dau),
          'ky_tu_ra': len(out) if dau is None else chu_xml(out)}
    if dau is not None:
        kq.update(vao=so_zip(dau), ra=so_zip(out))
    else:
        kq.update(byte_utf8_vao=len(chu.encode()), byte_utf8_ra=len(out.encode()),
                  vao=None, ra=None)
    return kq


def main():
    parser = argparse.ArgumentParser(description='Đo helper nguồn repo và văn bản CoreGia, chỉ DEMO.')
    parser.add_argument('--ca', choices=['docx', 'xlsx', 'van_ban'])
    parser.add_argument('--bao-cao', type=Path, help='Ghi JSON số đo UTF-8 ngoài gói engine.')
    parser.add_argument('--n', type=int, default=1000)
    parser.add_argument('--kieu', choices=['lap', 'da_dang'], default='lap')
    args = parser.parse_args()
    if args.ca:
        print(json.dumps(do_ca(args.ca, args.n, args.kieu), ensure_ascii=False))
        return
    import kho_tri_thuc_sdk
    report = {'nhan': 'DEMO — khảo sát, chưa chốt trần',
              'thoi_diem_utc': datetime.now(timezone.utc).isoformat(),
              'moi_truong': {'python': platform.python_version(), 'he_dieu_hanh': platform.system(),
                  'ban_he_dieu_hanh': platform.release(), 'build': platform.version(),
                  'kien_truc': platform.machine(), 'sdk': kho_tri_thuc_sdk.__version__,
                  'zlib': zlib.ZLIB_RUNTIME_VERSION, 'cpu_logic': os.cpu_count()},
              'sha256_lf_nguon': {n: sha256((NGUON / n).read_bytes().replace(b'\r\n', b'\n')).hexdigest()
                  for n in ('core.py', 'types.py', 'excel.py', 'excel_values.py', 'docx_revisions.py')},
              'so_do': []}
    for loai in ('docx', 'xlsx', 'van_ban'):
        for n, kieu in ((1000, 'lap'), (100000, 'lap'), (500000, 'lap'), (500000, 'da_dang')):
            try:
                p = subprocess.run([sys.executable, '-X', 'utf8', '-B', str(Path(__file__).resolve()),
                                    '--ca', loai, '--n', str(n), '--kieu', kieu],
                                   capture_output=True, text=True, encoding='utf-8', timeout=60)
                if p.returncode:
                    raise RuntimeError(f'Ca DEMO {loai}/{n}/{kieu} không đạt; chưa có số đo hợp lệ.')
                report['so_do'].append({'trang_thai': 'DO_DUOC', **json.loads(p.stdout)})
            except subprocess.TimeoutExpired:
                report['so_do'].append({'loai': loai, 'kich_thuoc_chu_fixture': n, 'kieu': kieu,
                    'trang_thai': 'VUOT_NGAN_SACH_DO', 'timeout_giay': 60,
                    'giay_xu_ly': None, 'tracemalloc_dinh_byte': None,
                    'ram_dinh_tien_trinh_sau_byte': None, 'ky_tu_ra': None})
            if args.bao_cao:
                args.bao_cao.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if not args.bao_cao:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Đã ghi {len(report['so_do'])} ca DEMO; timeout được ghi riêng, không phải số đo hoàn tất.")


if __name__ == '__main__':
    main()
