"""Kiểm gói độc lập; mã thoát 0 khi đạt, 1 khi không đạt."""
import ast
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys

CAM = re.compile(r"(?i)(?:kho_tri_thuc\.|kenh_engine|SDKEngine|Bootstrap|shim[_-]kho|\bsql\b|sqlite|psycopg|postgres|mysql|pymysql|pyodbc|sqlalchemy|https?://(?!json-schema\.org/)|urllib|requests|httpx|aiohttp|subprocess|socket)")
LUU_TREN_MAY = re.compile(r"(?i)KTT_ENGINE_DU_LIEU|KTT_ENGINE_CAU_HINH|PROGRAMDATA")


def _co_migration(goi):
    phieu = json.loads((goi / 'engine.json').read_text(encoding='utf-8'))
    migration = phieu.get('du_lieu', {}).get('goi_migration')
    return (phieu.get('ma') == 'e_mask' and isinstance(migration, dict)
            and set(migration) == {'ma', 'thu_muc', 'tep_kiem_ke', 'phien_ban_du_lieu'}
            and migration['ma'] == 'e_mask' and migration['thu_muc'] == 'sql'
            and migration['tep_kiem_ke'] == 'sql/kiem_ke.json'
            and type(migration['phien_ban_du_lieu']) is int
            and migration['phien_ban_du_lieu'] >= 1)


def _kiem_ke(goi, noi_dung):
    """Kiểm bytes thật, không chuẩn hóa xuống dòng trước khi băm."""
    kk = json.loads(noi_dung)
    phieu = json.loads((goi / 'engine.json').read_text(encoding='utf-8'))
    if (not _co_migration(goi) or set(kk) != {'phien_ban', 'tep'}
            or kk['phien_ban'] != phieu['phien_ban'] or not isinstance(kk['tep'], list)):
        raise ValueError
    da_co = set()
    for muc in kk['tep']:
        if not isinstance(muc, dict) or set(muc) != {'duong_dan', 'bytes', 'sha256'}:
            raise ValueError
        ten = muc['duong_dan']
        if (not isinstance(ten, str) or '\\' in ten or not ten
                or PurePosixPath(ten).is_absolute() or ':' in ten
                or '..' in PurePosixPath(ten).parts or PurePosixPath(ten).as_posix() != ten
                or ten in da_co or ten == 'sql/kiem_ke.json'):
            raise ValueError
        tep = goi / ten
        if (not tep.resolve().is_relative_to(goi.resolve()) or tep.is_symlink()
                or getattr(tep.lstat(), 'st_file_attributes', 0) & 0x400):
            raise ValueError
        du_lieu = tep.read_bytes()
        if (type(muc['bytes']) is not int or muc['bytes'] != len(du_lieu)
                or muc['sha256'] != hashlib.sha256(du_lieu).hexdigest()):
            raise ValueError
        da_co.add(ten)
    if da_co != {p.relative_to(goi).as_posix() for p in goi.rglob('*')
                 if p.is_file() and p != goi / 'sql/kiem_ke.json'}:
        raise ValueError
    # Chỉ bỏ các đường dẫn đã kiểm khỏi phép quét từ cấm; vẫn quét metadata.
    for muc in kk['tep']:
        muc['duong_dan'] = muc['duong_dan'].replace('sql/', '').replace('.sql', '')
    return json.dumps(kk, ensure_ascii=False)


def _kiem_lenh_sql(noi_dung):
    """Ngoại lệ R1: chỉ tạo bảng và chú thích trong eng_e_mask."""
    chu = re.sub(r'--[^\n]*', '', noi_dung)
    lenh = [s.strip() for s in chu.split(';') if s.strip()]
    cot = (r'[a-z][a-z0-9_]*\s+(?:uuid|text|bytea|numeric|bigint|timestamptz)'
           r'(?:\s+(?:PRIMARY KEY|NOT NULL|DEFAULT (?:1|now\(\))))*')
    duy_nhat = r'UNIQUE\s*\([a-z][a-z0-9_]*(?:\s*,\s*[a-z][a-z0-9_]*)*\)'
    tao = (r'CREATE TABLE eng_e_mask\.[a-z][a-z0-9_]*\s*\(\s*'
           + cot + r'(?:\s*,\s*(?:' + cot + '|' + duy_nhat + r'))*\s*\)')
    chu_thich = (r"COMMENT ON (?:TABLE|COLUMN) eng_e_mask\.[a-z][a-z0-9_]*"
                r"(?:\.[a-z][a-z0-9_]*)? IS '(?:[^']|'')*'")
    if not lenh or any(not re.fullmatch(tao + '|' + chu_thich, s) for s in lenh):
        raise ValueError


def _noi_dung_quet(p, noi_dung):
    if p.name == 'engine.json':
        phieu = json.loads(noi_dung)
        if phieu.get('du_lieu', {}).get('goi_migration') is not None:
            if not _co_migration(p.parent):
                raise ValueError
            del phieu['du_lieu']['goi_migration']
            return json.dumps(phieu, ensure_ascii=False)
    if p.name == 'kiem_ke.json' and p.parent.name == 'sql':
        return _kiem_ke(p.parent.parent, noi_dung)
    if p.suffix.lower() == '.sql':
        if p.parent.name != 'sql' or not _co_migration(p.parent.parent):
            raise ValueError
        _kiem_lenh_sql(noi_dung)
    return noi_dung


def kiem_tra(thu_muc):
    goc = Path(thu_muc).absolute()
    loi = []
    def quet(p):
        try:
            st = p.lstat()
            if stat.S_ISLNK(st.st_mode) or getattr(st, "st_file_attributes", 0) & 0x400:
                loi.append("Có liên kết trong gói."); return
            if p.name.casefold() == "__pycache__" or p.suffix.casefold() == ".pyc":
                loi.append("Có tệp hoặc thư mục biên dịch."); return
            if stat.S_ISDIR(st.st_mode):
                for con in p.iterdir(): quet(con)
            elif stat.S_ISREG(st.st_mode):
                noi_dung = p.read_text(encoding="utf-8")
                if CAM.search(_noi_dung_quet(p, noi_dung)):
                    loi.append(f"Có tham chiếu bị cấm: {p.relative_to(goc)}")
                if p.suffix == ".py":
                    if LUU_TREN_MAY.search(noi_dung):
                        loi.append(f"Có mã lưu dữ liệu máy trong gói: {p.relative_to(goc)}")
                    cay = ast.parse(noi_dung)
                    for nut in ast.walk(cay):
                        if isinstance(nut, (ast.Import, ast.ImportFrom)):
                            ten = [a.name for a in nut.names] if isinstance(nut, ast.Import) else [nut.module or ""]
                            if any(CAM.search(t) or t == "kho_tri_thuc" for t in ten):
                                loi.append(f"Import bị cấm: {p.relative_to(goc)}")
                            if any(t.rsplit('.', 1)[-1] in {'kho_tam', 'cau_hinh_may'} for t in ten + [a.name for a in nut.names]):
                                loi.append(f"Import mã lưu trữ trong gói: {p.relative_to(goc)}")
            else: loi.append("Có mục không phải tệp thường.")
        except (OSError, UnicodeError, SyntaxError, ValueError, KeyError, TypeError, AttributeError):
            loi.append("Không kiểm được một mục trong gói.")
    quet(goc)
    return loi

def main():
    if len(sys.argv) > 2:
        print("Cách dùng: kiem_doc_lap.py [thư mục gói]"); return 1
    goc = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[1] / "goi"
    loi = kiem_tra(goc)
    for cau in loi: print("[LỖI]", cau)
    if loi: return 1
    print("[ĐẠT] Gói độc lập, không có tham chiếu bị cấm hoặc tệp biên dịch.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
