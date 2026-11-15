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
SDK = GOC / "docs/goi-gui-engine/sdk-2.2.0"


def doc_lock(path):
    """Chi nhan pin == va SHA-256; khong chap nhan URL/lenh pip trong lock."""
    rows = []
    data = "\n".join(l.split("#", 1)[0] for l in path.read_text(encoding="utf-8").splitlines())
    for line in data.replace("\\\n", " ").splitlines():
        if not line.strip():
            continue
        m = re.fullmatch(r"\s*([A-Za-z0-9_.-]+)==([A-Za-z0-9_.+!-]+)((?:\s+--hash=sha256:[0-9a-f]{64})*)\s*", line)
        if not m:
            raise ValueError("Lock khong hop le: " + path.name)
        rows.append({"ten": m[1], "phien_ban": m[2], "hash": re.findall(r"sha256:([0-9a-f]{64})", m[3])})
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
    sdk = SDK / "kho_tri_thuc_sdk-2.2.0-py3-none-any.whl"
    expected = next(l.split()[0] for l in (SDK / "SHA256SUMS.txt").read_text().splitlines()
                    if l.endswith(sdk.name))
    rows = doc_lock(GOI / "requirements.lock")
    sdk_row = next(r for r in rows if r["ten"] == "kho_tri_thuc_sdk")
    if expected not in sdk_row["hash"] or sha256(sdk.read_bytes()).hexdigest() != expected:
        errors.append("SAI hash SDK 2.2.0 so voi lock/SHA256SUMS")
    else:
        selected.append(sdk)
    for row in rows:
        if row is sdk_row:
            continue
        p, error = kiem_wheel(row, wheelhouse, tags)
        if error:
            errors.append(error)
        else:
            selected.append(p)
    if not chi_runtime:
        for row in doc_lock(GOC / "e_doi_chieu/tests/requirements.lock"):
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
    # SDK cai tu wheel repo rieng; cac dependency cai tu dung wheel vua kiem hash.
    # Dung --no-compile de khong sinh pycache trong goi.
    for p in tep:
        subprocess.run([str(py), "-B", "-m", "pip", "--isolated", "install", "--no-index", "--no-deps",
                        "--no-compile", str(p)], check=True, env=env, cwd=GOC)
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
    parser.add_argument("--wheelhouse", type=Path, default=GOC / "wheelhouse")
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
