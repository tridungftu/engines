"""Kiểm SHA-256 bytes thật toàn gói; tạo kiểm kê và ZIP thử khi được yêu cầu.

NGUON.md liệt kê mọi tệp khác; SHA của chính NGUON.md nằm trong kiểm kê
ngoài gói để tránh băm tự tham chiếu. Không chuẩn hóa xuống dòng khi kiểm.
"""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

TESTS = Path(__file__).resolve().parent
GOI = TESTS.parent / 'goi' / 'e_kiem_excel'
KIEM_KE = TESTS / 'demo' / 'bam-goi.json'
BAT_DAU = '<!-- BAT-DAU-SHA256-EX6 -->'
KET_THUC = '<!-- KET-THUC-SHA256-EX6 -->'


def cac_tep(goi):
    kq = {}
    for p in sorted(goi.rglob('*')):
        if p.is_symlink() or (hasattr(p, 'is_junction') and p.is_junction()):
            raise ValueError('Gói có liên kết.')
        if p.name == '__pycache__' or p.suffix in {'.pyc', '.pyo'}:
            raise ValueError('Gói có bytecode.')
        if p.is_file():
            kq[p.relative_to(goi).as_posix()] = p.read_bytes()
    return kq


def bang_bam(tep):
    return {ten: {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
            for ten, raw in tep.items()}


def cap_nhat(goi, kiem_ke):
    tep = cac_tep(goi)
    nguon = (goi/'NGUON.md').read_text(encoding='utf-8')
    assert nguon.count(BAT_DAU) == nguon.count(KET_THUC) == 1
    truoc, con = nguon.split(BAT_DAU)
    _, sau = con.split(KET_THUC)
    bang = '\n\n| Tệp trong gói | Bytes | SHA-256 |\n|---|---:|---|\n'
    for ten, muc in bang_bam(tep).items():
        if ten != 'NGUON.md':
            bang += f"| `{ten}` | {muc['bytes']} | `{muc['sha256']}` |\n"
    (goi/'NGUON.md').write_text(truoc+BAT_DAU+bang+'\n'+KET_THUC+sau, encoding='utf-8', newline='\n')
    kiem_ke.write_text(json.dumps({'phien_ban': 1, 'bam': 'SHA-256 bytes nguyên trạng',
        'tep': bang_bam(cac_tep(goi))}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')


def kiem(goi, kiem_ke):
    mong = json.loads(kiem_ke.read_text(encoding='utf-8'))['tep']
    thuc = bang_bam(cac_tep(goi))
    if mong != thuc:
        raise ValueError('Kiểm kê không khớp toàn bộ bytes/SHA-256/tên tệp của gói.')
    nguon = (goi/'NGUON.md').read_text(encoding='utf-8')
    for ten, muc in thuc.items():
        if ten != 'NGUON.md' and f"| `{ten}` | {muc['bytes']} | `{muc['sha256']}` |" not in nguon:
            raise ValueError('NGUON.md thiếu băm hiện hành.')
    print(f'[ĐẠT] SHA-256 nguyên trạng {len(thuc)}/{len(thuc)} tệp, gồm NGUON.md.')


def kiem_phu_thuoc():
    """SDK chỉ dùng phần engine theo hướng dẫn --no-deps của bộ phát hành."""
    from importlib.metadata import version
    import subprocess
    import sys
    from openpyxl.xml import DEFUSEDXML
    for ten, ban in {'kho_tri_thuc_sdk':'2.2.0', 'openpyxl':'3.1.5',
                     'et_xmlfile':'2.0.0', 'defusedxml':'0.7.1'}.items():
        assert version(ten) == ban, 'Thư viện không đúng bản ghim.'
    assert DEFUSEDXML, 'Chưa bật bộ phân tích XML an toàn.'
    run = subprocess.run([sys.executable, '-B', '-m', 'pip', 'check'],
                         capture_output=True, text=True, check=False)
    # Chỉ hai dependency phần MODULE của wheel SDK được phép không cài.
    cho_phep = {'kho-tri-thuc-sdk 2.2.0 requires cryptography, which is not installed.',
                'kho-tri-thuc-sdk 2.2.0 requires jsonschema, which is not installed.'}
    loi = set(run.stdout.splitlines())
    if run.returncode and (run.returncode != 1 or not loi or not loi <= cho_phep or run.stderr):
        raise ValueError('Dependency thiếu/xung đột ngoài phần module SDK được loại trừ.')
    print('[ĐẠT] Ba dependency runtime đúng bản; DEFUSEDXML bật. '
          'Theo SDK --no-deps: không cài cryptography/jsonschema của phần module.')


def dong_thu(goi):
    """Dùng đúng bộ kiểm tên/tạo ZIP của dong_goi.py, không tạo commit git."""
    from io import BytesIO
    import subprocess
    from zipfile import ZipFile
    repo = TESTS.parents[1]
    spec = importlib.util.spec_from_file_location('dong_goi', repo/'_chung/cong-cu/dong_goi.py')
    dg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dg)
    tep = cac_tep(goi)
    for ten in tep:
        dg.kiem_ten(ten, 'e_kiem_excel')
    phieu = dg.doc_json(tep['engine.json'])
    dg.kiem_ke_sql(tep, phieu)
    raw = dg.tao_zip('e_kiem_excel', tep)
    with ZipFile(BytesIO(raw)) as z:
        assert {p[len('e_kiem_excel/'):]: z.read(p) for p in z.namelist()} == tep
    ra = repo/'.dong-goi-thu'
    ra.mkdir(exist_ok=True)
    ten_zip = f"e_kiem_excel-{phieu['phien_ban']}-EX6-worktree.zip"
    with (ra/ten_zip).open('xb') as f:
        f.write(raw)
    # Kiểm kê rời bao gồm mọi tệp và băm bản ZIP, không tự tham chiếu.
    du_lieu = dict(loai='BẢN THỬ từ worktree chưa commit; không phải gói phát hành',
        head_tham_chieu=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip(),
        cong_cu='_chung/cong-cu/dong_goi.py: kiem_ten/doc_json/kiem_ke_sql/tao_zip',
        zip=ten_zip, sha256=dg.sha256(raw), tep=bang_bam(tep))
    with (ra/'KIEM-KE-EX6.json').open('x', encoding='utf-8', newline='\n') as f:
        json.dump(du_lieu, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'[ĐẠT] ZIP thử {len(tep)} tệp, bytes khớp worktree: {dg.sha256(raw)}')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--goi', type=Path, default=GOI)
    ap.add_argument('--kiem-ke', type=Path, default=KIEM_KE)
    ap.add_argument('--cap-nhat', action='store_true')
    ap.add_argument('--dong-goi-thu', action='store_true')
    ap.add_argument('--phu-thuoc', action='store_true')
    args = ap.parse_args()
    if args.cap_nhat:
        cap_nhat(args.goi, args.kiem_ke)
    kiem(args.goi, args.kiem_ke)
    if args.phu_thuoc:
        kiem_phu_thuoc()
    if args.dong_goi_thu:
        dong_thu(args.goi)


if __name__ == '__main__':
    main()
