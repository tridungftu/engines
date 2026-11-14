"""Kiểm gói không phụ thuộc Core, không có tệp biên dịch hay liên kết.

Chạy trực tiếp: python e_hoi_ai/tests/kiem_doc_lap.py [thư_mục_gói].
Mã thoát 0 khi đạt; 1 khi có vi phạm hoặc không kiểm được đầy đủ.
"""
import os
from pathlib import Path
import stat
import sys


MAU_CAM = b"kho_tri_thuc."


def _la_lien_ket(thong_tin):
    return stat.S_ISLNK(thong_tin.st_mode) or bool(
        getattr(thong_tin, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def kiem_tra(thu_muc):
    """Không theo symlink/junction, kể cả khi đích nằm ngoài gói."""
    goc = Path(thu_muc).absolute()
    loi = []
    try:
        thong_tin = goc.lstat()
        if _la_lien_ket(thong_tin) or not stat.S_ISDIR(thong_tin.st_mode):
            return ["Đầu vào phải là thư mục gói thật, không phải liên kết."]
    except OSError:
        return ["Không đọc được thư mục gói cần kiểm."]

    def quet(thu_muc_con):
        try:
            with os.scandir(thu_muc_con) as danh_sach:
                cac_muc = sorted(danh_sach, key=lambda muc: muc.name)
        except OSError:
            loi.append("Không đọc được một thư mục trong gói.")
            return
        for muc in cac_muc:
            duong_dan = Path(muc.path)
            ten = duong_dan.relative_to(goc).as_posix()
            try:
                thong_tin = muc.stat(follow_symlinks=False)
                if _la_lien_ket(thong_tin):
                    loi.append(f"Có liên kết trong gói: {ten}")
                    continue
                if muc.name.casefold() == "__pycache__" or duong_dan.suffix.casefold() == ".pyc":
                    loi.append(f"Có tệp hoặc thư mục biên dịch trong gói: {ten}")
                    continue
                if stat.S_ISDIR(thong_tin.st_mode):
                    quet(duong_dan)
                elif stat.S_ISREG(thong_tin.st_mode):
                    if MAU_CAM in duong_dan.read_bytes():
                        loi.append(f"Có tham chiếu Core bị cấm trong gói: {ten}")
                else:
                    loi.append(f"Có mục không phải tệp thường trong gói: {ten}")
            except OSError:
                loi.append(f"Không kiểm được mục trong gói: {ten}")

    quet(goc)
    return loi


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) > 1:
        print("Cách dùng: python kiem_doc_lap.py [thư_mục_gói]")
        return 1
    thu_muc = Path(argv[0]) if argv else Path(__file__).resolve().parents[1] / "goi"
    loi = kiem_tra(thu_muc)
    for cau in loi:
        print(f"[LỖI] {cau}")
    if loi:
        return 1
    print("[ĐẠT] Gói độc lập: không tham chiếu Core, không có tệp biên dịch hay liên kết.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
