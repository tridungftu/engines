"""Đọc lock và kiểm wheel ngoại tuyến bằng thư viện chuẩn, dùng cả khi kiểm venv mới."""

import hashlib
from email.parser import BytesParser
from pathlib import Path
import re
import zipfile


MAU_DONG = re.compile(
    r"([A-Za-z0-9][A-Za-z0-9._-]*)==([A-Za-z0-9][A-Za-z0-9.!+_-]*)"
    r"((?: --hash=sha256:[0-9a-f]{64})+)"
)


def chuan_ten(ten):
    return re.sub(r"[-_.]+", "-", ten).lower()


def doc_lock(tep):
    try:
        noi_dung = Path(tep).read_bytes().decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("Lock phải là ASCII, không có BOM.") from exc
    ds = {}
    for so, dong in enumerate(noi_dung.splitlines(), 1):
        if "\\" in dong or re.search(r"coding\s*[:=]", dong, re.I):
            raise ValueError(f"Lock dòng {so}: không được nối dòng hoặc khai coding.")
        if not dong.strip() or dong.lstrip().startswith("#"):
            continue
        khop = MAU_DONG.fullmatch(dong)
        if khop is None:
            raise ValueError(f"Lock dòng {so}: cần ten==ban và các --hash=sha256 hợp lệ.")
        ten, ban, bam = khop.groups()
        ten = chuan_ten(ten)
        if ten.startswith("kho-tri-thuc") or ten in ds:
            raise ValueError(f"Lock dòng {so}: tên SDK bị cấm hoặc thư viện bị lặp.")
        ds[ten] = {"phien_ban": ban, "bam": set(re.findall(r"sha256:([0-9a-f]{64})", bam))}
    if not ds:
        raise ValueError("Lock chưa có thư viện đã ghim.")
    return ds


def kiem_goi_phu_thuoc(goi):
    goi = Path(goi)
    ds = doc_lock(goi / "requirements.lock")
    da_gap = {}
    for tep in sorted((goi / "wheels").iterdir()):
        if tep.is_symlink() or not tep.is_file() or tep.suffix != ".whl":
            raise ValueError("Kho wheel chỉ được chứa tệp .whl, không sdist hoặc thư mục con.")
        phan = tep.stem.split("-")
        if len(phan) not in (5, 6):
            raise ValueError("Tên wheel không đúng khuôn.")
        ten, ban = chuan_ten(phan[0]), phan[1]
        if ten not in ds or ten in da_gap or ban != ds[ten]["phien_ban"]:
            raise ValueError("Wheel thừa, lặp hoặc không khớp tên/phiên bản trong lock.")
        py, abi, nen = phan[-3:]
        thuan = "py3" in py.split(".") and abi == "none" and nen == "any"
        cp = re.fullmatch(r"cp3([0-9]+)", py)
        windows = nen == "win_amd64" and (
            py == "cp313" and abi == "cp313"
            or cp is not None and int(cp[1]) <= 13 and abi == "abi3")
        if not (thuan or windows):
            raise ValueError("Wheel phải dùng được trên CPython 3.13 win_amd64.")
        if hashlib.sha256(tep.read_bytes()).hexdigest() not in ds[ten]["bam"]:
            raise ValueError("Wheel không khớp SHA-256 trong lock.")
        with zipfile.ZipFile(tep) as z:
            metadata = [n for n in z.namelist() if n.endswith(".dist-info/METADATA")]
            if len(metadata) != 1:
                raise ValueError("Wheel phải có đúng một METADATA.")
            meta = BytesParser().parsebytes(z.read(metadata[0]))
            if chuan_ten(meta.get("Name", "")) != ten or meta.get("Version") != ban:
                raise ValueError("Metadata wheel không khớp tên/phiên bản đã ghim.")
        da_gap[ten] = tep
    if set(da_gap) != set(ds):
        raise ValueError("Kho wheel còn thiếu thư viện đã ghim.")
    return da_gap


def cac_module_da_ghim(goi):
    ten = set()
    for tep in kiem_goi_phu_thuoc(goi).values():
        with zipfile.ZipFile(tep) as z:
            for muc in z.namelist():
                goc = muc.split("/", 1)[0]
                if "/" not in muc and muc.endswith((".py", ".pyd")):
                    goc = goc.split(".", 1)[0]
                if goc.isidentifier():
                    ten.add(goc)
    return ten
