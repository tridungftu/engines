"""Đóng gói bytes đã ghi trong git; chỉ dùng thư viện chuẩn Python."""

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
CAC_ENGINE = ("e_hoa_don", "e_hoi_ai", "e_ocr", "e_trich_xuat", "e_doi_chieu", "e_tra_cuu", "e_mask", "e_kiem_excel", "e_phan_luong")
TEP_GOC = {"engine.json", "README.md", "CHANGELOG.md", "NGUON.md",
           "requirements.lock", "cau_hinh.schema.json", ".gitattributes"}
TEN_CAM = {".venv", "__pycache__", ".pytest-tmp", ".pytest_cache", "luu-tru"}
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


def dong_goi(repo, engines, ra, nhan, ref="HEAD"):
    repo, ra = Path(repo).resolve(), Path(ra).resolve()
    if ra.is_relative_to(repo) and ra != repo / ".dong-goi-thu":
        raise LoiDongGoi("Thư mục đầu ra phải ngoài repo; ngoại lệ thử là .dong-goi-thu ở gốc repo.")
    if not nhan.strip() or len(nhan) > 100 or any(ord(c) < 32 for c in nhan):
        raise LoiDongGoi("Nhãn mốc phải có 1–100 ký tự, không có ký tự điều khiển.")
    if not engines or any(ma not in CAC_ENGINE for ma in engines):
        raise LoiDongGoi("Chỉ nhận bốn mã engine của DONG-GOI-1.")
    if ra.exists() and (not ra.is_dir() or any(ra.iterdir())):
        raise LoiDongGoi("Cần thư mục đầu ra mới hoặc rỗng để tránh trộn bản phát hành.")
    commit = git(repo, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}").decode().strip()
    wheel = git(repo, "show", f"{commit}:{THU_MUC_SDK}/{WHEEL}")
    sums = git(repo, "show", f"{commit}:{THU_MUC_SDK}/SHA256SUMS.txt").decode("utf-8")
    bam_goc = [dong.split()[0] for dong in sums.splitlines()
               if len(dong.split()) == 2 and dong.split()[1] == WHEEL]
    if bam_goc != [sha256(wheel)]:
        raise LoiDongGoi("Wheel SDK 2.2.0 không khớp SHA256SUMS.txt tại mốc git.")
    dau_ra, danh_sach = {WHEEL: wheel}, []
    for ma in sorted(set(engines)):
        cac_tep = doc_goi_git(repo, commit, ma)
        phieu = doc_json(cac_tep["engine.json"])
        if (not isinstance(phieu, dict) or phieu.get("ma") != ma
                or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", str(phieu.get("phien_ban", "")))
                or phieu.get("tuong_thich", {}).get("sdk") != ">=2.2.0 <3.0.0"):
            raise LoiDongGoi("Phiếu sai mã, phiên bản hoặc khoảng SDK 2.2.0.")
        kiem_ke_sql(cac_tep, phieu)
        ten_zip = f"{ma}-{phieu['phien_ban']}.zip"
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
        "nhan": nhan, "commit_git": commit, "sdk": SDK,
        "wheel_sdk": {"tep": WHEEL, "sha256": sha256(wheel)}, "goi": danh_sach,
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
    args = parser.parse_args(argv)
    repo = Path(__file__).resolve().parents[2]
    try:
        ds = dong_goi(repo, args.engine, args.ra, args.nhan, args.ref)
    except (LoiDongGoi, OSError, KeyError, TypeError, UnicodeError) as loi:
        thong_diep = str(loi) if isinstance(loi, LoiDongGoi) else "Không hoàn tất đóng gói; kiểm quyền ghi và cấu trúc gói."
        print(f"[LỖI] {thong_diep}", file=sys.stderr)
        return 1
    for goi in ds:
        print(f"[ĐẠT] {goi['tep_zip']}  {goi['sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
