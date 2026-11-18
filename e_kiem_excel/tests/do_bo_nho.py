"""Đo workbook nạp đầy đủ hai lần; mỗi cỡ chạy trong tiến trình riêng.

Chỉ công cụ test ghi DEMO trong TemporaryDirectory và tự dọn. Không nới trần
runtime: số đo là openpyxl trực tiếp, có ghi kết quả nhận diện trước khi nạp.
"""

import argparse
import ctypes
import gc
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
import tracemalloc
from zipfile import ZipFile

sys.dont_write_bytecode = True
TESTS = Path(__file__).resolve().parent
sys.path[:0] = [str(TESTS / 'demo'), str(TESTS.parent / 'goi' / 'e_kiem_excel')]
from sinh_demo import NHAN, o, workbook


def rss():
    """RSS hiện tại và đỉnh tiến trình (bytes); không dùng thư viện ngoài."""
    if sys.platform == 'win32':
        from ctypes import wintypes
        class BoNho(ctypes.Structure):
            _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
                (n, ctypes.c_size_t) for n in ('PeakWorkingSetSize','WorkingSetSize',
                'QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage',
                'QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        psapi = ctypes.WinDLL('psapi', use_last_error=True)
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(BoNho), wintypes.DWORD]
        info = BoNho(); info.cb = ctypes.sizeof(info)
        if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(info), info.cb):
            raise ctypes.WinError(ctypes.get_last_error())
        return info.WorkingSetSize, info.PeakWorkingSetSize
    import resource
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    peak *= 1 if sys.platform == 'darwin' else 1024
    if sys.platform.startswith('linux'):
        current = int(Path('/proc/self/statm').read_text().split()[1]) * os.sysconf('SC_PAGE_SIZE')
    else:
        current = peak
    return current, peak


def tao_mau(mib, *, day=False):
    """DEMO nhiều chuỗi số hex khó nén và công thức; không nhồi tệp ngoài.

    Profile phụ day=True: 250.000 ô số/công thức ngắn, kiểm ảnh hưởng mật độ.
    """
    rows = 12499 if day else int(mib * 1048576 / 2150)
    for _ in range(4):
        parts = [f'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1">{o("A1",NHAN)}</row>']
        for r in range(2, rows+2):
            cells=[]
            for c in range(20):
                pos=chr(65+c)+str(r)
                if c % 4 == 3:
                    cells.append(o(pos,r*2,f'{r}*2'))
                elif day:
                    cells.append(o(pos,r*1000000+c))
                else:
                    text='DEMO '+''.join(hashlib.sha256(f'{r}-{c}-{i}'.encode()).hexdigest() for i in range(4))
                    cells.append(o(pos,text))
            parts.append(f'<row r="{r}">{"".join(cells)}</row>')
        parts.append('</sheetData></worksheet>')
        raw=workbook([('DEMO', ''.join(parts).encode(), 'visible')])
        if day or (len(raw) <= mib*1048576 and abs(len(raw)/(mib*1048576)-1) < .01):
            return raw
        rows=max(1, int(rows*mib*1048576/len(raw)*.999))
    return raw


def do_mot(tep):
    import openpyxl
    from openpyxl.xml import DEFUSEDXML
    from e_kiem_excel.nhan_dien import kiem_tep
    from kho_tri_thuc_sdk.engine import LoiNghiepVu
    assert DEFUSEDXML
    raw=Path(tep).read_bytes()
    try:
        nhan_dien=kiem_tep(raw, 'DEMO.xlsx')
    except LoiNghiepVu as loi:
        nhan_dien={'ma_loi':loi.ma}
    with ZipFile(BytesIO(raw)) as z:
        giai_nen=sum(x.file_size for x in z.infolist())
    gc.collect()
    nen=rss()[0]
    tracemalloc.start()
    bat_dau=time.perf_counter()
    wb=openpyxl.load_workbook(BytesIO(raw),data_only=False,read_only=False,keep_vba=False,keep_links=False)
    wv=openpyxl.load_workbook(BytesIO(raw),data_only=True,read_only=False,keep_vba=False,keep_links=False)
    _,peak=tracemalloc.get_traced_memory()
    hien_tai, rss_peak=rss()
    kq=dict(tep_byte=len(raw),giai_nen_byte=giai_nen,so_o=sum(len(ws._cells) for ws in wb),
            giay=round(time.perf_counter()-bat_dau,3),tracemalloc_dinh_byte=peak,
            rss_nen_byte=nen,rss_sau_byte=hien_tai,rss_dinh_byte=rss_peak,
            nhan_dien=nhan_dien,sha256=hashlib.sha256(raw).hexdigest())
    wb.close(); wv.close(); tracemalloc.stop()
    return kq


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--con'); ap.add_argument('--ra',type=Path)
    args=ap.parse_args()
    if args.con:
        print(json.dumps(do_mot(args.con))); return
    kq=dict(nhan=NHAN,python=platform.python_version(),he_dieu_hanh=platform.system(),
            openpyxl='3.1.5',defusedxml='0.7.1',profile='ZIP_DEFLATED; 20 cột, 15 chuỗi DEMO hex/5 công thức mỗi dòng; giữ hai workbook trong RAM',do=[])
    with tempfile.TemporaryDirectory(prefix='excel-DEMO-') as tmp:
        for mib in (5,10,20):
            tep=Path(tmp)/f'{mib}-DEMO.xlsx'; tep.write_bytes(tao_mau(mib))
            run=subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),'--con',str(tep)],check=True,capture_output=True,text=True,timeout=300)
            do=json.loads(run.stdout); do['co_mib']=mib; kq['do'].append(do)
            print(json.dumps(do),flush=True)
        tep=Path(tmp)/'day-DEMO.xlsx'; tep.write_bytes(tao_mau(1,day=True))
        run=subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),'--con',str(tep)],check=True,capture_output=True,text=True,timeout=300)
        kq['mat_do_250k']=json.loads(run.stdout)
    if args.ra:
        args.ra.write_text(json.dumps(kq,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(kq,ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
