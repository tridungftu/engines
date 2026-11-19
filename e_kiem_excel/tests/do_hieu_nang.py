"""Đo toàn năng lực qua CoreGia; mỗi mẫu/năng lực dùng tiến trình mới.

Không bật tracemalloc để tránh làm sai thời gian. RSS đỉnh gồm Python, SDK,
bytes vào/ra, workbook và báo cáo; không gồm tiến trình sinh DEMO.
"""

import argparse
from datetime import datetime
from io import BytesIO
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
from zipfile import ZipFile

sys.dont_write_bytecode = True
TESTS = Path(__file__).resolve().parent
sys.path[:0] = [str(TESTS), str(TESTS / 'demo'), str(TESTS.parent / 'goi' / 'e_kiem_excel')]
from do_bo_nho import rss, tao_mau
from sinh_demo import bang_kl, workbook, o, NS


def ghep(raw):
    """Bảng KL có 30 dòng thật và sheet tải; không đệm ZIP bằng tệp lạ."""
    with ZipFile(BytesIO(bang_kl())) as z:
        ds = [(ten, z.read(f'xl/worksheets/sheet{i}.xml'), 'visible')
              for i, ten in enumerate(('BTH', 'Nguon'), 1)]
    with ZipFile(BytesIO(raw)) as z:
        ds.append(('Tai DEMO', z.read('xl/worksheets/sheet1.xml'), 'visible'))
    return workbook(ds)


def tao_bien(loai):
    if loai == 'giai_nen':
        # Gần 128 MiB XML có nội dung ô thật, mỗi chuỗi < 32.767 ký tự.
        n, text = 4090, 'DEMO ' + 'a' * 32700
        xml = f'<worksheet xmlns="{NS}"><sheetData>'
        xml += ''.join(f'<row r="{r}">{o("A"+str(r), text)}</row>' for r in range(1, n+1))
    else:
        # 248.977 ô thực trên sheet tải; ghép bảng KL thành 249.421 ô.
        xml = f'<worksheet xmlns="{NS}"><sheetData>'
        xml += ''.join(f'<row r="{r}">' + ''.join(o(c+str(r), r) for c in 'ACEGIKMOQSUWY')
                       + '</row>' for r in range(1, 19153))
        # Một ô cuối đưa vùng sát 500.000; giữ số ô thực dưới 250.000.
        xml += f'<row r="19190">{o("Z19190", 1)}</row>'
    xml += '</sheetData></worksheet>'
    return ghep(workbook([('DEMO', xml.encode(), 'visible')]))


def do_mot(tep, nang_luc):
    from e_kiem_excel.chay import app
    from e_kiem_excel.nhan_dien import kiem_tep
    from kho_tri_thuc_sdk.thu import CoreGia
    raw = Path(tep).read_bytes()
    nhan_dien = kiem_tep(raw, 'tai-DEMO.xlsx')
    core = CoreGia()
    dau_vao = {'loai': 'tep', 'tep': core.them_tep('tai-DEMO.xlsx', raw)}
    tham_so = ({'o_dich': 'BTH!J39', 'kiem_nguon_kl': True,
                 'bo_nhom_json': (TESTS/'demo/bo_nhom_review_ttkl.json').read_text(encoding='utf-8')}
                if nang_luc == 'excel.toan_ven@1' else {'tien_te': 'VND'})
    nen = rss()[0]
    bat_dau = time.perf_counter()
    kq = core.chay_thu(app, nang_luc, dau_vao, tham_so=tham_so)
    giay = time.perf_counter() - bat_dau
    dinh = rss()[1]
    if kq['trang_thai'] != 'XONG':
        raise RuntimeError(f"DEMO không XONG: {kq.get('loi')}")
    truong = kq['ket_qua']['truong']
    if nang_luc == 'excel.doc_bang@1':
        assert truong['so_dong'] == 30
    else:
        assert truong['o_dich'] == 'BTH!J39'
        # Có K8 và cây K7 thực sự, không chỉ đo nhánh mặc định.
        chi_tiet = json.loads(core.doc_tep(truong['tep_json']['tep_id']))
        assert chi_tiet['k8_nguon'] and chi_tiet['k7_cay']
    return dict(nang_luc=nang_luc, trang_thai=kq['trang_thai'], giay=round(giay, 4),
                rss_nen_byte=nen, rss_dinh_byte=dinh, tep_byte=len(raw),
                sha256=hashlib.sha256(raw).hexdigest(), **nhan_dien)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--con', type=Path)
    ap.add_argument('--nang-luc')
    ap.add_argument('--ra', type=Path)
    ap.add_argument('--lap', type=int, default=3)
    args = ap.parse_args()
    if args.lap < 1:
        ap.error('Số lượt đo phải từ 1 trở lên.')
    if args.con:
        print(json.dumps(do_mot(args.con, args.nang_luc))); return
    goi = TESTS.parent/'goi/e_kiem_excel'
    kq = dict(python=platform.python_version(), he_dieu_hanh=platform.platform(),
              cpu=platform.processor(), so_cpu_logic=os.cpu_count(),
              bat_dau=datetime.now().astimezone().isoformat(),
              phien_ban_engine=json.loads((goi/'engine.json').read_text(encoding='utf-8'))['phien_ban'],
              bam_runtime={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sorted((goi/'e_kiem_excel').glob('*.py'))},
              sdk='2.2.0', openpyxl='3.1.5', lap=args.lap,
              phuong_phap='RSS đỉnh tiến trình; perf_counter quanh CoreGia.chay_thu; không tracemalloc; sinh/nạp module ngoài đồng hồ', do=[])
    with tempfile.TemporaryDirectory(prefix='EX6-DEMO-') as tmp:
        for profile in (1, 5, 10, 20, 'mat_do', 'giai_nen'):
            raw = ghep(tao_mau(profile)) if isinstance(profile, int) else tao_bien(profile)
            tep = Path(tmp)/'tai-DEMO.xlsx'
            tep.write_bytes(raw)
            del raw
            for nl in ('excel.toan_ven@1', 'excel.doc_bang@1'):
                for lan in range(1, args.lap+1):
                    run = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()),
                        '--con', str(tep), '--nang-luc', nl], capture_output=True,
                        text=True, encoding='utf-8', timeout=600, check=True)
                    do = dict(profile=profile, lan=lan, **json.loads(run.stdout))
                    kq['do'].append(do)
                    kq['cap_nhat_luc'] = datetime.now().astimezone().isoformat()
                    print(json.dumps(do), flush=True)
                    if args.ra:
                        args.ra.write_text(json.dumps(kq, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
