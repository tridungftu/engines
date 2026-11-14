"""Thử Hot Folder DEMO riêng; mặc định chỉ mô tả, không truy cập cấu hình."""
import argparse
import json
import os
from pathlib import Path
import sys
import time
import uuid
import zipfile
from io import BytesIO
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'e_ocr' / 'goi' / 'e_ocr'), str(ROOT / 'e_ocr' / 'tests')]


def kiem_word(raw):
    w = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    with zipfile.ZipFile(BytesIO(raw)) as z:
        root = ET.fromstring(z.read('word/document.xml'))
    bang = list(root.iter(w + 'tbl'))
    return {'so_bang': len(bang), 'dung_cau_truc': len(bang) == 3 and all(
        len(t.findall(w + 'tr')) == 4 and len(t.find(w + 'tblGrid')) == 3
        and len(list(t.iter(w + 'tc'))) == 10
        and [x.get(w + 'val') for x in t.iter(w + 'gridSpan')] == ['3']
        and sum(not list(c.iter(w + 't')) for c in t.iter(w + 'tc')) == 1
        for t in bang)}


def kiem_duong_dan(p):
    if not p.is_absolute():
        raise ValueError('Thư mục phải là đường dẫn tuyệt đối.')
    p = p.resolve(strict=True)
    if not p.is_dir() or any(x.casefold() == 'abbyy-hotfolder' for x in p.parts):
        raise ValueError('Chỉ dùng thư mục DEMO riêng, ngoài abbyy-hotfolder.')
    if not any('demo' in x.casefold() for x in p.parts):
        raise ValueError('Đường dẫn thư mục phải có thành phần chứa DEMO.')
    return p


def chay(config, ket_qua_dir):
    from demo.tao_bo_demo import tao_bo_demo, TIEN, NGAY
    from e_ocr.lop_chu import doc_lop_chu
    from e_ocr.xuat_word import dung_docx
    tep_cau_hinh = Path(config).resolve(strict=True)
    cam = {'.env', 'cau_hinh.that.toml', 'abbyy-hotfolder', 'plhn-that', 'web-that', 'bi-mat'}
    if any(x.casefold() in cam for x in tep_cau_hinh.parts):
        raise ValueError('Kh?ng d?ng t?p c?u h?nh thu?c khu v?c b? c?m.')
    cfg = json.loads(tep_cau_hinh.read_text(encoding='utf-8-sig'))['abbyy']
    if cfg.get('bat') is not True:
        raise ValueError('Cấu hình ABBYY chưa bật.')
    vao, ra = (kiem_duong_dan(Path(cfg[k])) for k in ('thu_muc_vao', 'thu_muc_ra'))
    dich = kiem_duong_dan(Path(ket_qua_dir))
    if any(a == b or a in b.parents or b in a.parents for a, b in ((vao, ra), (vao, dich), (ra, dich))):
        raise ValueError('Ba thư mục vào, ra, kết quả phải tách biệt.')
    han = cfg['thoi_han_giay']
    if type(han) is not int or not 1 <= han <= 3600:
        raise ValueError('Thời hạn phải từ 1 đến 3600 giây.')
    ma = uuid.uuid4().hex
    lan = dich / ('DEMO-' + ma)
    lan.mkdir()
    bao_cao = {'nhan': 'DEMO', 'ma_tuong_quan': ma, 'trang_thai': 'loi',
               'bien_nhan_loi': {'trang_thai': 'chua_kiem_chung', 'ly_do': 'Lượt thành công hoặc im lặng không chứng minh nguồn có sinh biên nhận từ chối.'}}
    start = time.monotonic()
    try:
        bo = tao_bo_demo(lan / 'du-lieu', ca_loi=False)
        # Công bố nguyên tử, chỉ thao tác tên ngẫu nhiên do lượt này tạo.
        tam = vao / (ma + '.tmp')
        with tam.open('xb') as f:
            f.write(bo.pdf_quet.read_bytes())
            f.flush()
            os.fsync(f.fileno())
        os.replace(tam, vao / (ma + '.pdf'))
        dau = None
        while time.monotonic() - start < han:
            loi = ra / (ma + '.loi.json')
            pdf = ra / (ma + '.pdf')
            if loi.exists():
                if loi.is_symlink() or loi.stat().st_size > 2048:
                    bao_cao['bien_nhan_loi'] = {'trang_thai': 'khong_hop_le'}
                else:
                    try:
                        data = json.loads(loi.read_text(encoding='utf-8'))
                        hop_le = data == {'ma_tuong_quan': ma, 'trang_thai': 'tu_choi', 'da_tieu_trang': False} and data.get('da_tieu_trang') is False and not pdf.exists()
                    except (ValueError, OSError):
                        hop_le = False
                    bao_cao['bien_nhan_loi'] = {'trang_thai': 'dung_quy_uoc' if hop_le else 'khong_hop_le'}
                bao_cao['trang_thai'] = 'nguon_tra_loi'
                break
            if pdf.exists() and not pdf.is_symlink():
                stat = pdf.stat()
                moi = (stat.st_size, stat.st_mtime_ns)
                if moi == dau and 0 < stat.st_size <= 20 * 1024**2:
                    raw = pdf.read_bytes()
                    if (pdf.stat().st_size, pdf.stat().st_mtime_ns) == moi and b'%%EOF' in raw[-1024:]:
                        doc = doc_lop_chu(raw)
                        word = dung_docx({'phien_ban': 1, 'so_trang': len(doc.pages), 'trang': doc.pages})
                        (lan / 'DEMO-ket-qua.docx').write_bytes(word)
                        bao_cao.update(trang_thai='da_nhan_pdf', so_trang=len(doc.pages),
                            so_sanh={'tien': [TIEN in t for t in doc.text.split('\f')], 'ngay': [NGAY in t for t in doc.text.split('\f')]},
                            word=kiem_word(word))
                        break
                dau = moi
            time.sleep(0.2)
        else:
            bao_cao['trang_thai'] = 'qua_thoi_han_chua_ro'
    except Exception:
        bao_cao['trang_thai'] = 'loi_xu_ly'
    finally:
        bao_cao['thoi_gian_giay'] = round(time.monotonic() - start, 3)
        (lan / 'ket-qua.json').write_text(json.dumps(bao_cao, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return bao_cao, lan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--that', action='store_true')
    parser.add_argument('--cau-hinh')
    parser.add_argument('--ket-qua')
    args = parser.parse_args()
    if not args.that:
        print('Chạy khô: không đọc cấu hình, không gửi PDF. Dùng --that --cau-hinh <JSON> --ket-qua <thư mục DEMO>.')
        return 0
    if not args.cau_hinh or not args.ket_qua:
        parser.error('--that cần --cau-hinh và --ket-qua.')
    try:
        report, folder = chay(args.cau_hinh, args.ket_qua)
        print('Kết quả DEMO:', report['trang_thai'], '; JSON:', folder / 'ket-qua.json')
        return 0 if report['trang_thai'] == 'da_nhan_pdf' and len(report['so_sanh']['tien']) == 3 and all(report['so_sanh']['tien'] + report['so_sanh']['ngay']) and report['word']['dung_cau_truc'] else 1
    except (OSError, ValueError, KeyError, ImportError):
        print('Không thể chạy: kiểm tra cấu hình, thư mục DEMO và thư viện cần thiết.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

