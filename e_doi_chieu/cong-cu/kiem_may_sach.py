"""DC-12: kiem offline truoc khi cai, khong tu tai mang.

Mac dinh chi chay kho. --cai tao venv moi, khong dung system-site-packages.
Thieu wheel/hash/tag dung thi ma 2, khong tao venv hoac bao da kiem may sach.
"""
import sys

sys.dont_write_bytecode = True

import argparse
from hashlib import sha256
import os
from pathlib import Path
import re
import subprocess
import venv


GOC = Path(__file__).resolve().parents[2]
GOI = GOC / "e_doi_chieu/goi/e_doi_chieu"
SDK = GOC / "docs/goi-gui-engine/sdk-2.5.0"


def doc_lock(path, *, bat_buoc_hash=True):
    """Lock runtime ASCII, moi dong mot pin; SDK do Core cap rieng."""
    rows = []
    data = path.read_bytes().decode("ascii")
    if "\\" in data or re.search(r"coding\s*[:=]", data, re.I):
        raise ValueError("Lock khong hop le: " + path.name)
    names = set()
    for line in data.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.fullmatch(r"\s*([A-Za-z0-9_.-]+)==([A-Za-z0-9_.+!-]+)((?:\s+--hash=sha256:[0-9a-f]{64})*)\s*", line)
        if not m:
            raise ValueError("Lock khong hop le: " + path.name)
        name = re.sub(r"[-_.]+", "-", m[1]).lower()
        hashes = re.findall(r"sha256:([0-9a-f]{64})", m[3])
        if name.startswith("kho-tri-thuc") or name in names or (bat_buoc_hash and not hashes):
            raise ValueError("Lock khong hop le: " + path.name)
        names.add(name)
        rows.append({"ten": m[1], "phien_ban": m[2], "hash": hashes})
    return rows


def kiem_goi_thu_vien(goi):
    """Kiem goi Core nhan: moi pin dung mot wheel cp313 Windows/py3."""
    from pip._vendor.packaging.utils import canonicalize_name, parse_wheel_filename
    from pip._vendor.packaging.tags import Tag
    rows = doc_lock(goi / "requirements.lock")
    wheels = goi / "wheels"
    if not wheels.is_dir() or wheels.is_symlink():
        raise ValueError("Thieu thu muc wheels hop le.")
    matched = {canonicalize_name(r["ten"]): [] for r in rows}
    for p in wheels.iterdir():
        if not p.is_file() or p.is_symlink() or p.suffix != ".whl":
            raise ValueError("wheels chi duoc chua wheel, khong sdist/thu muc con.")
        name, version, _, tags = parse_wheel_filename(p.name)
        row = next((r for r in rows if canonicalize_name(r["ten"]) == name), None)
        if (row is None or str(version) != row["phien_ban"]
                or sha256(p.read_bytes()).hexdigest() not in row["hash"]
                or not tags.intersection({Tag("cp313", "cp313", "win_amd64"), Tag("py3", "none", "any")})):
            raise ValueError("Wheel khong khop pin/hash/nen tang: " + p.name)
        matched[name].append(p)
    if any(len(ps) != 1 for ps in matched.values()):
        raise ValueError("Moi dong lock phai co dung mot wheel.")
    return rows


def kiem_wheel(row, wheelhouse, tags):
    from pip._vendor.packaging.utils import parse_wheel_filename, canonicalize_name
    candidates = []
    for p in sorted(wheelhouse.glob("*.whl")):
        try:
            name, version, _, wheel_tags = parse_wheel_filename(p.name)
        except ValueError:
            continue
        if canonicalize_name(row["ten"]) != name or row["phien_ban"] != str(version):
            continue
        if not wheel_tags.intersection(tags):
            continue
        candidates.append(p)
    if not row["hash"]:
        return None, f"THIEU hash wheel duoc duyet: {row['ten']}=={row['phien_ban']}"
    for p in candidates:
        if sha256(p.read_bytes()).hexdigest() in row["hash"]:
            return p, None
    return None, f"THIEU wheel dung hash/tag: {row['ten']}=={row['phien_ban']}"


def kiem_truoc(wheelhouse, chi_runtime=False):
    from pip._vendor.packaging.tags import sys_tags
    tags = set(sys_tags())
    errors, selected = [], []
    sdk = SDK / "kho_tri_thuc_sdk-2.5.0-py3-none-any.whl"
    expected = next(l.split()[0] for l in (SDK / "SHA256SUMS.txt").read_text().splitlines()
                    if l.endswith(sdk.name))
    rows = kiem_goi_thu_vien(GOI)
    if sha256(sdk.read_bytes()).hexdigest() != expected:
        errors.append("SAI hash SDK 2.5.0 so voi SHA256SUMS")
    else:
        selected.append(sdk)
    for row in rows:
        p, error = kiem_wheel(row, wheelhouse, tags)
        if error:
            errors.append(error)
        else:
            selected.append(p)
    if not chi_runtime:
        for row in doc_lock(GOC / "e_doi_chieu/tests/requirements.lock", bat_buoc_hash=False):
            p, error = kiem_wheel(row, wheelhouse, tags)
            if error:
                errors.append(error)
            else:
                selected.append(p)
    return selected, errors


def cai_va_kiem(tep, dich, chi_runtime):
    # Khong ghi de/xoa/move moi truong da co.
    if dich.exists():
        raise ValueError("Dich venv da ton tai; chon thu muc moi.")
    if not dich.resolve().is_relative_to(GOC.resolve()):
        raise ValueError("Venv phai nam trong worktree.")
    venv.EnvBuilder(with_pip=True, system_site_packages=False).create(dich)
    py = dich / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
               PIP_NO_INDEX="1", PIP_DISABLE_PIP_VERSION_CHECK="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    # SDK tach khoi lock runtime; cai phu thuoc theo dung lenh offline cua Core.
    pip = [str(py), "-I", "-X", "utf8", "-m", "pip", "install", "--isolated",
           "--no-index", "--no-deps", "--no-compile", "--only-binary", ":all:"]
    subprocess.run([*pip, str(tep[0])], check=True, env=env, cwd=GOC)
    runtime = doc_lock(GOI / "requirements.lock")
    so_runtime = len(runtime)
    links = sorted({str(p.parent) for p in tep[1:1 + so_runtime]})
    tim_wheel = [arg for link in links for arg in ("--find-links", link)]
    subprocess.run([*pip, *tim_wheel, "--require-hashes", "-r", str(GOI / "requirements.lock")],
                   check=True, env=env, cwd=GOC)
    for p in tep[1 + so_runtime:]:
        subprocess.run([*pip, str(p)], check=True, env=env, cwd=GOC)
    subprocess.run([str(py), "-B", "-m", "kho_tri_thuc_sdk.thu", str(GOI)], check=True, env=env, cwd=GOC)
    if not chi_runtime:
        for args in (["-m", "pytest", "e_doi_chieu/tests", "-q"],
                     ["e_doi_chieu/tests/chay_demo_voi_core_gia.py"]):
            subprocess.run([str(py), "-B", *args], check=True, env=env, cwd=GOC)
        scripts = sorted((GOC / "e_doi_chieu/tests/ui").glob("*.test.mjs"))
        subprocess.run(["node", "--test", *(str(p) for p in scripts)], check=True, env=env, cwd=GOC)
    subprocess.run([str(py), "-B", "e_doi_chieu/tests/kiem_doc_lap.py"], check=True, env=env, cwd=GOC)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheelhouse", type=Path, default=GOI / "wheels",
                        help="Mac dinh wheels cua goi; Linux chon kho offline co hash Linux trong lock.")
    parser.add_argument("--venv", type=Path, default=GOC / ".venv-dc12-sach")
    parser.add_argument("--chi-runtime", action="store_true", help="Khong tinh la da kiem pytest/UI/harness")
    parser.add_argument("--cai", action="store_true", help="Chi cai khi tat ca wheel/hash/tag dat")
    args = parser.parse_args(argv)
    selected, errors = kiem_truoc(args.wheelhouse, args.chi_runtime)
    print("DC-12: CHAY KHO offline" if not args.cai else "DC-12: kiem truoc cai offline")
    for error in errors:
        print(error)
    if errors:
        print("CHUA KIEM may sach; khong tao venv, khong tai mang.")
        return 2
    if not args.cai:
        print("Du wheel duoc pin cho nen tang hien tai; chua cai/chay may sach.")
        return 0
    cai_va_kiem(selected, args.venv, args.chi_runtime)
    print("Da kiem runtime/CoreGia" if args.chi_runtime else "Da kiem bang Core gia (CoreGia), chua Core that.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print("CHUA DAT cong cu offline: " + str(exc), file=sys.stderr)
        raise SystemExit(2)
