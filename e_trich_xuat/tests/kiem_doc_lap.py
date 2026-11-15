"""Quét toàn bộ goi/, không theo symlink/junction; exit 0/1."""

import os
from pathlib import Path
import stat
import sys


MAU_CAM = (b"kho_tri_thuc.", b"kenh_engine", b"SDKEngine", b"Bootstrap")


def _lien_ket(st):
    return stat.S_ISLNK(st.st_mode) or bool(
        getattr(st, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def kiem_tra(thu_muc):
    goc, loi = Path(thu_muc).absolute(), []
    try:
        st = goc.lstat()
        if _lien_ket(st) or not stat.S_ISDIR(st.st_mode):
            return ["Đầu vào phải là thư mục gói thật."]
    except OSError:
        return ["Không đọc được thư mục gói."]

    def quet(goc_con):
        try:
            with os.scandir(goc_con) as ds:
                for muc in ds:
                    p = Path(muc.path)
                    st = muc.stat(follow_symlinks=False)
                    if _lien_ket(st):
                        loi.append("Có liên kết trong gói.")
                    elif muc.name.casefold() == "__pycache__" or p.suffix.casefold() in (".pyc", ".pyo"):
                        loi.append("Có tệp hoặc thư mục biên dịch trong gói.")
                    elif stat.S_ISDIR(st.st_mode):
                        quet(p)
                    elif stat.S_ISREG(st.st_mode):
                        if st.st_size > 20 * 1048576:
                            loi.append("Có tệp quá lớn trong gói.")
                        elif any(m in p.read_bytes() for m in MAU_CAM):
                            loi.append("Có tham chiếu Core hoặc kênh cũ trong gói.")
                    else:
                        loi.append("Có mục không phải tệp thường trong gói.")
        except OSError:
            loi.append("Không kiểm được đầy đủ một mục trong gói.")

    quet(goc)
    return loi


def main():
    if len(sys.argv) > 2:
        print("Cách dùng: python kiem_doc_lap.py [thư_mục_gói]")
        return 1
    goc = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[1] / "goi"
    loi = kiem_tra(goc)
    for cau in loi:
        print("[LỖI] " + cau)
    if not loi:
        print("[ĐẠT] Gói độc lập: không import Core/kênh cũ, không bytecode hoặc liên kết.")
    return int(bool(loi))


if __name__ == "__main__":
    raise SystemExit(main())
