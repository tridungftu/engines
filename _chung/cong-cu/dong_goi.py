"""Đóng gói bytes đã ghi trong git; chỉ dùng thư viện chuẩn Python.

Bản Linux lấy wheel từ <engine>/wheels-linux/ ở cùng mốc git, dùng lại
py3-none-any còn thiếu từ gói Windows. Kiểm kê gốc phải đúng trước khi đổi
wheel; kiểm kê Linux được sinh lại đủ mọi tệp trừ chính nó khi gói thay đổi.
Gói không đổi wheel giữ nguyên bytes, kể cả kiểm kê và ZIP.
"""

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import zipfile


SDK = "2.2.0"
WHEEL = f"kho_tri_thuc_sdk-{SDK}-py3-none-any.whl"
THU_MUC_SDK = f"docs/goi-gui-engine/sdk-{SDK}"
# Bản SDK được kèm theo đợt phát hành; gói khai >=2.4.0 phải đi với SDK 2.5.0.
CAC_SDK = ("2.2.0", "2.5.0")
CAC_ENGINE = ("e_hoa_don", "e_hoi_ai", "e_ocr", "e_trich_xuat", "e_doi_chieu", "e_tra_cuu", "e_mask", "e_kiem_excel", "e_phan_luong")
TEP_GOC = {"engine.json", "README.md", "CHANGELOG.md", "NGUON.md",
           "requirements.lock", "cau_hinh.schema.json", ".gitattributes"}
TEN_CAM = {".venv", "__pycache__", ".pytest-tmp", ".pytest_cache", "luu-tru"}
# Gói kèm thư viện (phu_thuoc_python) cần SDK 2.4.0 trở lên phía Core.
KHOANG_SDK = (">=2.2.0 <3.0.0", ">=2.4.0 <3.0.0")
THOI_GIAN = (1980, 1, 1, 0, 0, 0)


class LoiDongGoi(ValueError):
    """Gói hoặc tham số không đủ điều kiện phát hành."""


class BoThamSo(argparse.ArgumentParser):
    def format_usage(self):
        return super().format_usage().replace("usage:", "Cách dùng:", 1)

    def format_help(self):
        return super().format_help().replace("usage:", "Cách dùng:", 1).replace("options:", "Tùy chọn:", 1)

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, "Lỗi: Tham số chưa hợp lệ. Dùng --help để xem hướng dẫn.\n")


def sha256(noi_dung):
    return hashlib.sha256(noi_dung).hexdigest()


def git(repo, *tham_so):
    kq = subprocess.run(["git", "-C", str(repo), *tham_so], capture_output=True)
    if kq.returncode:
        raise LoiDongGoi("Không đọc được mốc git hoặc tệp đã ghi trong git.")
    return kq.stdout


def doc_json(noi_dung):
    def object_khong_lap(cac_cap):
        kq = {}
        for khoa, gia_tri in cac_cap:
            if khoa in kq:
                raise LoiDongGoi("JSON có khóa lặp.")
            kq[khoa] = gia_tri
        return kq
    try:
        return json.loads(noi_dung, object_pairs_hook=object_khong_lap)
    except (ValueError, UnicodeError) as loi:
        raise LoiDongGoi("Không đọc được JSON hợp lệ của gói.") from loi


def kiem_ten(ten, ma):
    p = PurePosixPath(ten)
    if (not ten or p.is_absolute() or "\\" in ten or ":" in ten
            or any(x in ("", ".", "..") for x in ten.split("/"))):
        raise LoiDongGoi("Gói có đường dẫn không an toàn.")
    for phan in p.parts:
        n = phan.casefold()
        if (n in TEN_CAM or n.startswith(".pytest-tmp") or n.startswith(".env")
                or n.endswith((".pyc", ".pyo"))
                or any(x in n for x in ("bi-mat", "secret", "token", "password"))):
            raise LoiDongGoi("Gói có tên tệp hoặc thư mục bị cấm.")
    if ten in TEP_GOC:
        return
    if len(p.parts) == 1 and (p.name in (".gitattributes", "KHAI-SDK-2.1.json") or p.name.endswith(".schema.json")):
        return
    duoi = p.suffix.lower()
    if len(p.parts) > 1 and (
        (p.parts[0] == ma and (duoi == ".py" or p.name == "LICENSE"))
        or (len(p.parts) == 3 and p.parts[0] == ma and p.parts[1] == "schemas" and p.name.endswith(".schema.json"))
        or (len(p.parts) == 3 and p.parts[0] == ma and p.parts[1] == "tu_dien" and duoi in {".txt", ".json"})
        or (len(p.parts) == 2 and p.parts[0] == "wheels" and duoi == ".whl")
        or (p.parts[0] == "contract" and duoi == ".json")
        or (p.parts[0] == "demo" and duoi in
            {".txt", ".json", ".xml", ".pdf", ".png", ".jpg", ".jpeg", ".docx", ".xlsx", ".zip", ".md"})
        or (p.parts[0] == "ui" and duoi in {".js", ".css", ".html"})
        or (p.parts[0] == "tai_nguyen" and duoi in {".txt", ".json", ".ttf", ".otf", ".md"})
        or (len(p.parts) == 2 and p.parts[0].startswith("tham_chieu_") and duoi == ".py")
        or (len(p.parts) == 2 and p.parts[0] == "sql" and
            (p.name == "kiem_ke.json" or re.fullmatch(r"[0-9]{3}_[a-z0-9_]+\.sql", p.name)))
    ):
        return
    raise LoiDongGoi("Gói có tệp ngoài danh sách cho phép: " + ten)


def doc_goi_git(repo, commit, ma):
    goc = f"{ma}/goi/{ma}/"
    ds = git(repo, "ls-tree", "-rz", commit, "--", goc)
    cac_tep = {}
    ten_windows = set()
    for muc in ds.split(b"\0"):
        if not muc:
            continue
        thong_tin, duong_dan = muc.split(b"\t", 1)
        che_do, loai, oid = thong_tin.split()
        ten_day_du = duong_dan.decode("utf-8")
        if not ten_day_du.startswith(goc) or loai != b"blob" or che_do not in (b"100644", b"100755"):
            raise LoiDongGoi("Gói có liên kết hoặc đối tượng git không được phép.")
        ten = ten_day_du[len(goc):]
        kiem_ten(ten, ma)
        if ten.casefold() in ten_windows:
            raise LoiDongGoi("Gói có tên tệp trùng trên Windows.")
        ten_windows.add(ten.casefold())
        # Đọc blob trực tiếp, không qua checkout, text mode hay export-subst.
        cac_tep[ten] = git(repo, "cat-file", "blob", oid.decode("ascii"))
    if not {"engine.json", "README.md", "requirements.lock", "NGUON.md"} <= cac_tep.keys():
        raise LoiDongGoi("Gói thiếu phiếu, hướng dẫn, phụ thuộc hoặc nguồn.")
    return cac_tep


def kiem_ke_sql(cac_tep, phieu):
    co_sql = any(ten.startswith("sql/") for ten in cac_tep)
    migration = phieu.get("du_lieu", {}).get("goi_migration")
    if not co_sql and not migration and not phieu.get("ngan_du_lieu"):
        return
    if (not co_sql or not isinstance(migration, dict)
            or migration.get("thu_muc") != "sql"
            or migration.get("tep_kiem_ke") != "sql/kiem_ke.json"
            or "sql/kiem_ke.json" not in cac_tep
            or not any(ten.endswith(".sql") for ten in cac_tep)):
        raise LoiDongGoi("Ngăn/SQL thiếu khai báo migration hoặc kiểm kê.")
    kk = doc_json(cac_tep["sql/kiem_ke.json"])
    if not isinstance(kk, dict) or kk.get("phien_ban") != phieu["phien_ban"] or not isinstance(kk.get("tep"), list):
        raise LoiDongGoi("Kiểm kê SQL sai cấu trúc hoặc phiên bản.")
    da_kiem = set()
    for muc in kk["tep"]:
        if not isinstance(muc, dict) or not isinstance(muc.get("duong_dan"), str):
            raise LoiDongGoi("Kiểm kê SQL có mục không hợp lệ.")
        ten = muc["duong_dan"]
        if ten in da_kiem or ten == "sql/kiem_ke.json" or ten not in cac_tep:
            raise LoiDongGoi("Kiểm kê SQL có tệp trùng hoặc thừa.")
        noi_dung = cac_tep[ten]
        if (type(muc.get("bytes")) is not int or muc["bytes"] != len(noi_dung)
                or muc.get("sha256") != sha256(noi_dung)):
            raise LoiDongGoi("Kiểm kê SQL sai số bytes hoặc SHA-256.")
        da_kiem.add(ten)
    if da_kiem != set(cac_tep) - {"sql/kiem_ke.json"}:
        raise LoiDongGoi("Kiểm kê SQL chưa bao gồm đúng toàn bộ gói.")


# Wheel thuần dùng được mọi nền: tag Python có py3 (py3, py2.py3), ABI none, nền any.
_THUAN = re.compile(r"-(?:[A-Za-z0-9_]+\.)*py3(?:\.[A-Za-z0-9_]+)*-none-any\.whl$")


def kiem_nen_wheel(ten, nen):
    # Cùng khuôn tên wheel của Core; hỗ trợ cả build tag và tag nền ghép.
    khop = re.fullmatch(
        r"wheels/([A-Za-z0-9][A-Za-z0-9._]*)-([0-9][A-Za-z0-9.!+_]*)"
        r"(?:-[0-9][A-Za-z0-9_]*)?-([A-Za-z0-9_.]+)-([A-Za-z0-9_.]+)"
        r"-([A-Za-z0-9_.]+)\.whl", ten)
    if not khop:
        raise LoiDongGoi("Tên wheel không hợp lệ: " + ten)
    python, abi, nen_tag = khop[3], khop[4], khop[5]
    if nen == "windows":
        hop_le = all(tag == "win_amd64" or (tag == "any" and abi == "none")
                     for tag in nen_tag.split("."))
    elif nen_tag == "any":
        hop_le = "py3" in python.split(".") and abi == "none"
    else:
        def manylinux(tag):
            if tag in {"manylinux1_x86_64", "manylinux2010_x86_64", "manylinux2014_x86_64"}:
                return True
            m = re.fullmatch(r"manylinux_2_([0-9]+)_x86_64", tag)
            return m is not None and int(m[1]) <= 39
        hop_le = all(manylinux(tag) for tag in nen_tag.split("."))
    if not hop_le:
        raise LoiDongGoi(f"Wheel không đúng nền {nen}: " + ten)
    return khop[1], khop[2]


def kiem_thu_vien(cac_tep, phieu, nen="windows"):
    """Lock một dòng/thư viện, mỗi dòng đúng một wheel khớp băm; không wheel thừa (phiếu Core CĐ-50 mục 6)."""
    wheels = {ten for ten in cac_tep if ten.startswith("wheels/")}
    khai = phieu.get("phu_thuoc_python")
    if khai is None:
        if wheels:
            raise LoiDongGoi("Gói có wheels/ nhưng phiếu chưa khai phu_thuoc_python.")
        return
    if (khai != {"lock": "requirements.lock", "wheels": "wheels"}
            or phieu["tuong_thich"]["sdk"] != ">=2.4.0 <3.0.0"):
        raise LoiDongGoi("Khai báo thư viện phải là lock requirements.lock, wheels wheels, SDK >=2.4.0.")
    raw = cac_tep["requirements.lock"]
    if any(b not in (10, 13) and not 32 <= b <= 126 for b in raw):
        raise LoiDongGoi("requirements.lock chỉ được dùng ASCII.")
    chuan = lambda t: re.sub(r"[-_.]+", "-", t).lower()
    lock = {}
    for dong in raw.decode("ascii").splitlines():
        if not dong.strip() or dong.startswith("#"):
            continue
        m = re.fullmatch(r"([A-Za-z0-9][A-Za-z0-9._-]*)==([0-9][A-Za-z0-9.!+_]*)((?: --hash=sha256:[0-9a-f]{64})+)", dong)
        if not m or chuan(m[1]).startswith("kho-tri-thuc") or chuan(m[1]) in lock:
            raise LoiDongGoi("requirements.lock có dòng sai khuôn, trùng hoặc chứa SDK: " + dong[:60])
        lock[chuan(m[1])] = (m[2], set(re.findall(r"[0-9a-f]{64}", m[3])))
    gap = {}
    for ten in sorted(wheels):
        ten_tv, ban = kiem_nen_wheel(ten, nen)
        ma = chuan(ten_tv)
        if ma not in lock or ma in gap or ban != lock[ma][0] or sha256(cac_tep[ten]) not in lock[ma][1]:
            raise LoiDongGoi("Wheel thừa, trùng, sai phiên bản hoặc sai băm: " + ten)
        gap[ma] = ten
    if set(gap) != set(lock):
        raise LoiDongGoi("Thiếu wheel cho: " + ", ".join(sorted(set(lock) - set(gap))))


def thay_wheel_linux(repo, commit, ma, cac_tep, phieu):
    """Chỉ đọc blob wheel từ git; không đưa metadata ngoài gói vào ZIP."""
    goc = f"{ma}/wheels-linux/"
    ds = git(repo, "ls-tree", "-rz", commit, "--", goc)
    wheels = {}
    for muc in ds.split(b"\0"):
        if not muc:
            continue
        thong_tin, duong_dan = muc.split(b"\t", 1)
        che_do, loai, oid = thong_tin.split()
        ten_day_du = duong_dan.decode("utf-8")
        if not ten_day_du.endswith(".whl"):
            continue
        if not ten_day_du.startswith(goc) or loai != b"blob" or che_do not in (b"100644", b"100755"):
            raise LoiDongGoi("Wheel Linux có liên kết hoặc đối tượng git không được phép.")
        ten = "wheels/" + ten_day_du[len(goc):]
        kiem_ten(ten, ma)
        kiem_nen_wheel(ten, "linux")
        wheels[ten] = git(repo, "cat-file", "blob", oid.decode("ascii"))
    chuan = lambda ten: re.sub(r"[-_.]+", "-", ten.split("/")[-1].split("-")[0]).lower()
    co_linux = {chuan(ten) for ten in wheels}
    for ten, raw in cac_tep.items():
        if (ten.startswith("wheels/") and _THUAN.search(ten)
                and chuan(ten) not in co_linux):
            wheels[ten] = raw
    kq = {ten: raw for ten, raw in cac_tep.items() if not ten.startswith("wheels/")}
    kq.update(wheels)
    kiem_thu_vien(kq, phieu, "linux")
    if kq != cac_tep:
        migration = phieu.get("du_lieu", {}).get("goi_migration")
        if migration:
            ten_kk = migration["tep_kiem_ke"]
            kk = doc_json(cac_tep[ten_kk])
            kk["tep"] = [{"duong_dan": ten, "bytes": len(raw), "sha256": sha256(raw)}
                         for ten, raw in sorted(kq.items()) if ten != ten_kk]
            kq[ten_kk] = (json.dumps(kk, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            kiem_ke_sql(kq, phieu)
    return kq


def tao_zip(ma, cac_tep):
    bo_nho = io.BytesIO()
    # ZIP_STORED tránh phụ thuộc phiên bản zlib; đổi kích thước lấy tính tất định.
    with zipfile.ZipFile(bo_nho, "w", compression=zipfile.ZIP_STORED) as goi:
        for ten in sorted(cac_tep):
            info = zipfile.ZipInfo(f"{ma}/{ten}", date_time=THOI_GIAN)
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_STORED
            goi.writestr(info, cac_tep[ten])
    return bo_nho.getvalue()


def dong_goi(repo, engines, ra, nhan, ref="HEAD", sdk=SDK, nen="windows"):
    repo, ra = Path(repo).resolve(), Path(ra).resolve()
    if ra.is_relative_to(repo) and ra != repo / ".dong-goi-thu":
        raise LoiDongGoi("Thư mục đầu ra phải ngoài repo; ngoại lệ thử là .dong-goi-thu ở gốc repo.")
    if not nhan.strip() or len(nhan) > 100 or any(ord(c) < 32 for c in nhan):
        raise LoiDongGoi("Nhãn mốc phải có 1–100 ký tự, không có ký tự điều khiển.")
    if not engines or any(ma not in CAC_ENGINE for ma in engines):
        raise LoiDongGoi("Chỉ nhận bốn mã engine của DONG-GOI-1.")
    if ra.exists() and (not ra.is_dir() or any(ra.iterdir())):
        raise LoiDongGoi("Cần thư mục đầu ra mới hoặc rỗng để tránh trộn bản phát hành.")
    if sdk not in CAC_SDK:
        raise LoiDongGoi("Bản SDK kèm phát hành không được hỗ trợ.")
    if nen not in ("windows", "linux"):
        raise LoiDongGoi("Nền phát hành phải là windows hoặc linux.")
    wheel_ten, thu_muc_sdk = f"kho_tri_thuc_sdk-{sdk}-py3-none-any.whl", f"docs/goi-gui-engine/sdk-{sdk}"
    commit = git(repo, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}").decode().strip()
    wheel = git(repo, "show", f"{commit}:{thu_muc_sdk}/{wheel_ten}")
    sums = git(repo, "show", f"{commit}:{thu_muc_sdk}/SHA256SUMS.txt").decode("utf-8")
    bam_goc = [dong.split()[0] for dong in sums.splitlines()
               if len(dong.split()) == 2 and dong.split()[1] == wheel_ten]
    if bam_goc != [sha256(wheel)]:
        raise LoiDongGoi(f"Wheel SDK {sdk} không khớp SHA256SUMS.txt tại mốc git.")
    dau_ra, danh_sach = {wheel_ten: wheel}, []
    for ma in sorted(set(engines)):
        cac_tep = doc_goi_git(repo, commit, ma)
        phieu = doc_json(cac_tep["engine.json"])
        if (not isinstance(phieu, dict) or phieu.get("ma") != ma
                or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", str(phieu.get("phien_ban", "")))
                or phieu.get("tuong_thich", {}).get("sdk") not in KHOANG_SDK):
            raise LoiDongGoi("Phiếu sai mã, phiên bản hoặc khoảng SDK.")
        if phieu["tuong_thich"]["sdk"] == ">=2.4.0 <3.0.0" and sdk == "2.2.0":
            raise LoiDongGoi("Gói kèm thư viện cần SDK 2.4.0 trở lên; đóng gói với --sdk 2.5.0.")
        kiem_ke_sql(cac_tep, phieu)
        kiem_thu_vien(cac_tep, phieu)
        if nen == "linux":
            cac_tep = thay_wheel_linux(repo, commit, ma, cac_tep, phieu)
        hau_to = "-linux_x86_64" if nen == "linux" else ""
        ten_zip = f"{ma}-{phieu['phien_ban']}{hau_to}.zip"
        dau_ra[ten_zip] = tao_zip(ma, cac_tep)
        danh_sach.append({
            "ma": ma, "ten": phieu["ten"], "phien_ban": phieu["phien_ban"],
            "sdk": phieu["tuong_thich"]["sdk"],
            "nang_luc": [muc["ma"] for muc in phieu["nang_luc"]],
            "co_ngan": bool(phieu.get("ngan_du_lieu")),
            "co_sql": any(ten.startswith("sql/") for ten in cac_tep),
            "tep_zip": ten_zip, "sha256": sha256(dau_ra[ten_zip]), "commit_git": commit,
        })
    # Kiểm hết bốn gói trước khi ghi bất kỳ artifact nào.
    bang_bam = "".join(f"{sha256(noi_dung)}  {ten}\n" for ten, noi_dung in sorted(dau_ra.items()))
    dau_ra["SHA256SUMS.txt"] = bang_bam.encode("utf-8")
    dau_ra["DANH-SACH-GOI.json"] = (json.dumps({
        "nhan": nhan, "commit_git": commit, "sdk": sdk, "nen": nen,
        "wheel_sdk": {"tep": wheel_ten, "sha256": sha256(wheel)}, "goi": danh_sach,
    }, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    ra.mkdir(parents=True, exist_ok=True)
    for ten, noi_dung in sorted(dau_ra.items()):
        with (ra / ten).open("xb") as tep:
            tep.write(noi_dung)
    return danh_sach


def main(argv=None):
    parser = BoThamSo(description=__doc__, add_help=False)
    parser.add_argument("-h", "--help", action="help", help="Hiện hướng dẫn và thoát.")
    parser.add_argument("--engine", action="append", required=True, choices=CAC_ENGINE, help="Mã engine; được lặp.")
    parser.add_argument("--ra", required=True, type=Path, help="Thư mục mới/rỗng ngoài repo.")
    parser.add_argument("--nhan", required=True, help="Nhãn mốc phát hành, ví dụ thu (không phải git ref).")
    parser.add_argument("--ref", default="HEAD", help="Git commit/tag/nhánh nguồn; mặc định HEAD.")
    parser.add_argument("--sdk", default=SDK, choices=CAC_SDK, help="Bản SDK kèm phát hành; mặc định 2.2.0.")
    parser.add_argument("--nen", default="windows", choices=("windows", "linux"), help="Nền phát hành; mặc định windows.")
    args = parser.parse_args(argv)
    repo = Path(__file__).resolve().parents[2]
    try:
        ds = dong_goi(repo, args.engine, args.ra, args.nhan, args.ref, args.sdk, args.nen)
    except (LoiDongGoi, OSError, KeyError, TypeError, UnicodeError) as loi:
        thong_diep = str(loi) if isinstance(loi, LoiDongGoi) else "Không hoàn tất đóng gói; kiểm quyền ghi và cấu trúc gói."
        print(f"[LỖI] {thong_diep}", file=sys.stderr)
        return 1
    for goi in ds:
        print(f"[ĐẠT] {goi['tep_zip']}  {goi['sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
