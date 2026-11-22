"""Tự kiểm lock và wheel ngoại tuyến bằng thư viện chuẩn, không dùng SDK nội bộ."""

from email.parser import BytesParser
from hashlib import sha256
from pathlib import Path
import re


GOI = Path(__file__).resolve().parents[1] / "goi" / "e_ocr"
_DONG = re.compile(r"([A-Za-z0-9][A-Za-z0-9_.-]*)==([0-9][A-Za-z0-9.!+_-]*)((?: --hash=sha256:[0-9a-f]{64})+)")


def ten_chuan(ten):
    return re.sub(r"[-_.]+", "-", ten).lower()


def doc_lock(tep):
    """Trả tên chuẩn hóa → (phiên bản, tập hash); từ chối khuôn pip khác."""
    van_ban = Path(tep).read_bytes().decode("ascii")
    if "\\" in van_ban or re.search(r"coding\s*[:=]", van_ban, re.I):
        raise ValueError("Lock không được nối dòng hoặc khai coding.")
    cac_pin = {}
    for so, dong in enumerate(van_ban.splitlines(), 1):
        if not dong.strip() or dong.startswith("#"):
            continue
        khop = _DONG.fullmatch(dong)
        if khop is None:
            raise ValueError(f"Lock sai khuôn tại dòng {so}.")
        ten, ban, bam = khop.groups()
        ten = ten_chuan(ten)
        if ten.startswith("kho-tri-thuc") or ten in cac_pin:
            raise ValueError(f"Lock có tên dành riêng hoặc lặp tại dòng {so}.")
        cac_pin[ten] = (ban, set(re.findall(r"--hash=sha256:([0-9a-f]{64})", bam)))
    if not cac_pin:
        raise ValueError("Lock phải khai thư viện của gói.")
    return cac_pin


def kiem_goi_thu_vien(goi=GOI):
    """Đúng một wheel Python 3.13 Windows cho mỗi pin; metadata và hash khớp."""
    from zipfile import ZipFile

    goi = Path(goi)
    cac_pin = doc_lock(goi / "requirements.lock")
    da_thay = set()
    for tep in sorted((goi / "wheels").iterdir()):
        if tep.is_symlink() or not tep.is_file() or tep.suffix != ".whl":
            raise ValueError("wheels chỉ được chứa tệp wheel, không có thư mục hay sdist.")
        phan = tep.stem.split("-")
        if len(phan) not in (5, 6):
            raise ValueError("Tên wheel không hợp lệ.")
        ten, ban = ten_chuan(phan[0]), phan[1]
        if ten not in cac_pin or ten in da_thay:
            raise ValueError("Wheel thừa hoặc có nhiều wheel cho một pin.")
        ban_lock, cac_bam = cac_pin[ten]
        if ban != ban_lock or sha256(tep.read_bytes()).hexdigest() not in cac_bam:
            raise ValueError("Phiên bản hoặc SHA-256 wheel không khớp lock.")
        python, abi, nen = phan[-3:]
        thuan_python = python in {"py3", "py2.py3"} and abi == "none"
        cp313 = python == "cp313" and abi in {"cp313", "none"}
        abi3 = bool(re.fullmatch(r"cp3[0-9]+", python)) and abi == "abi3" and 32 <= int(python[2:]) <= 313
        if not ((thuan_python and nen in {"any", "win_amd64"})
                or ((cp313 or abi3) and nen == "win_amd64")):
            raise ValueError("Wheel không phù hợp Python 3.13 win_amd64.")
        with ZipFile(tep) as zip:
            metadata = [p for p in zip.namelist() if p.endswith(".dist-info/METADATA")]
            if len(metadata) != 1:
                raise ValueError("Wheel phải có đúng một METADATA.")
            thong_tin = BytesParser().parsebytes(zip.read(metadata[0]))
        if ten_chuan(thong_tin.get("Name", "")) != ten or thong_tin.get("Version") != ban:
            raise ValueError("Metadata wheel không khớp tên hoặc phiên bản.")
        da_thay.add(ten)
    if da_thay != set(cac_pin):
        raise ValueError("Thiếu wheel đã khai trong lock.")
    return cac_pin


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        print(f"[ĐẠT] Lock và {len(kiem_goi_thu_vien())} wheel khớp khuôn, phiên bản và SHA-256.")
    except (OSError, ValueError) as loi:
        print(f"[LỖI] {loi}")
        raise SystemExit(1)
