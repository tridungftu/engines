"""Kiểm tái hiện và biên so chính xác của chọn mẫu PL-2B (DEMO)."""
import ast
import hashlib
import inspect
import json
import os
import subprocess
import sys
from decimal import Decimal, FloatOperation, localcontext
from pathlib import Path

import pytest

DUONG_GOI = Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"
sys.path.insert(0, str(DUONG_GOI))
from e_phan_luong import chon_mau

HAT_GIONG = bytes(range(32))
MA_MODULE = "demo_thanh_toan"
KHAU = "ktt_duyet"


def ket_qua_byte(hg):
    ket_qua = [
        [ma, chon_mau.duoc_chon(hg, MA_MODULE, KHAU, ma, Decimal("0.20"))]
        for ma in (f"PC-DEMO-{i:05d}" for i in range(500))
    ]
    return json.dumps(ket_qua, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def test_sinh_hat_giong_dung_32_byte_secrets(monkeypatch):
    cac_do_dai = []

    def token_bytes(n):
        cac_do_dai.append(n)
        return HAT_GIONG

    monkeypatch.setattr(chon_mau.secrets, "token_bytes", token_bytes)
    assert chon_mau.sinh_hat_giong() == HAT_GIONG
    assert cac_do_dai == [32]


def test_hat_giong_thuc_la_bytes_32():
    hg = chon_mau.sinh_hat_giong()
    assert isinstance(hg, bytes)
    assert len(hg) == 32


def test_bam_hat_giong():
    assert chon_mau.bam_hat_giong(HAT_GIONG) == (
        "sha256:630dcd2966c4336691125448bbb25b4ff412a49c732db2c8abc1b8581bd710dd"
    )


def test_cong_thuc_bam_utf8_va_thu_tu_byte():
    ma = "PC-DEMO-Ánh-Dương-0001"
    du_lieu = HAT_GIONG + b"\x1f" + MA_MODULE.encode("utf-8") + b"\x1f" + KHAU.encode("utf-8") + b"\x1f" + ma.encode("utf-8")
    mong_doi = int.from_bytes(hashlib.sha256(du_lieu).digest(), "big")
    assert chon_mau.gia_tri_bam(HAT_GIONG, MA_MODULE, KHAU, ma) == mong_doi
    assert 0 <= mong_doi < 1 << 256


def test_tach_truong_va_ngu_canh_tham_gia_bam():
    goc = chon_mau.gia_tri_bam(HAT_GIONG, MA_MODULE, KHAU, "PC-DEMO-0001")
    assert chon_mau.gia_tri_bam(HAT_GIONG, "demo_khac", KHAU, "PC-DEMO-0001") != goc
    assert chon_mau.gia_tri_bam(HAT_GIONG, MA_MODULE, "cfo_duyet", "PC-DEMO-0001") != goc
    assert chon_mau.gia_tri_bam(HAT_GIONG, MA_MODULE, KHAU, "PC-DEMO-0002") != goc
    assert chon_mau.gia_tri_bam(HAT_GIONG, "demo_a", "bc", "PC-DEMO") != chon_mau.gia_tri_bam(HAT_GIONG, "demo_ab", "c", "PC-DEMO")


def test_tai_hien_tung_byte_hai_lan():
    assert ket_qua_byte(HAT_GIONG) == ket_qua_byte(HAT_GIONG)


def test_tai_hien_tung_byte_hai_tien_trinh():
    ma_chay = """
import json, sys
from decimal import Decimal
sys.path.insert(0, sys.argv[1])
from e_phan_luong import chon_mau
hg = bytes(range(32))
kq = [[ma, chon_mau.duoc_chon(hg, "demo_thanh_toan", "ktt_duyet", ma, Decimal("0.20"))]
      for ma in (f"PC-DEMO-{i:05d}" for i in range(500))]
sys.stdout.buffer.write(json.dumps(kq, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
"""
    cac_lan = []
    for hat_bam_python in ("1", "2"):
        moi_truong = os.environ.copy()
        moi_truong["PYTHONHASHSEED"] = hat_bam_python
        lan = subprocess.run(
            [sys.executable, "-B", "-c", ma_chay, str(DUONG_GOI)],
            capture_output=True, check=True, timeout=30, env=moi_truong,
        )
        assert lan.stderr == b""
        cac_lan.append(lan.stdout)
    assert cac_lan[0] == cac_lan[1] == ket_qua_byte(HAT_GIONG)


def test_doi_mot_bit_hat_giong_doi_ket_qua():
    hg_khac = bytes([HAT_GIONG[0] ^ 1]) + HAT_GIONG[1:]
    assert chon_mau.bam_hat_giong(HAT_GIONG) != chon_mau.bam_hat_giong(hg_khac)
    assert ket_qua_byte(HAT_GIONG) != ket_qua_byte(hg_khac)


def test_tan_suat_10000_dong():
    so_chon = sum(
        chon_mau.duoc_chon(HAT_GIONG, MA_MODULE, KHAU, f"PC-DEMO-{i:05d}", Decimal("0.20"))
        for i in range(10000)
    )
    assert 1900 <= so_chon <= 2100, f"Số dòng DEMO được chọn: {so_chon}/10000"


@pytest.mark.parametrize("p,mong_doi", [(Decimal(0), False), (Decimal(1), True)])
def test_p_khong_va_mot(p, mong_doi):
    assert all(
        chon_mau.duoc_chon(HAT_GIONG, MA_MODULE, KHAU, f"PC-DEMO-{i:05d}", p) is mong_doi
        for i in range(100)
    )


@pytest.mark.parametrize("gia_tri", [0, (1 << 256) - 1])
def test_p_khong_va_mot_tai_hai_cuc_bam(monkeypatch, gia_tri):
    monkeypatch.setattr(chon_mau, "gia_tri_bam", lambda *args: gia_tri)
    assert chon_mau.duoc_chon(HAT_GIONG, MA_MODULE, KHAU, "PC-DEMO", Decimal(0)) is False
    assert chon_mau.duoc_chon(HAT_GIONG, MA_MODULE, KHAU, "PC-DEMO", Decimal(1)) is True


@pytest.mark.parametrize("lech,mong_doi", [(-1, True), (0, False), (1, False)])
def test_bien_bam_nguyen_tai_p_mot_phan_hai(monkeypatch, lech, mong_doi):
    monkeypatch.setattr(chon_mau, "gia_tri_bam", lambda *args: (1 << 255) + lech)
    assert chon_mau.duoc_chon(HAT_GIONG, MA_MODULE, KHAU, "PC-DEMO", Decimal("0.5")) is mong_doi


@pytest.mark.parametrize("lech,mong_doi", [(0, True), (1, False)])
def test_bien_p_thap_phan_khong_lam_tron_nguong(monkeypatch, lech, mong_doi):
    # 2^256 không chia hết 5: giá trị nguyên ngay dưới/trên ngưỡng 0,20.
    monkeypatch.setattr(chon_mau, "gia_tri_bam", lambda *args: (1 << 256) // 5 + lech)
    assert chon_mau.duoc_chon(HAT_GIONG, MA_MODULE, KHAU, "PC-DEMO", Decimal("0.20")) is mong_doi


@pytest.mark.parametrize("lech,mong_doi", [(-1, False), (0, False), (1, True)])
def test_hat_giong_thuc_va_p_cach_bam_mot_don_vi_256_bit(lech, mong_doi):
    # Không đảo SHA-256: cố định hạt giống rồi dựng p chính xác quanh băm
    # của nó. Ba ngưỡng chỉ khác 2^-256, float không phân biệt được.
    ma = "PC-DEMO-0001"
    bam = chon_mau.gia_tri_bam(HAT_GIONG, MA_MODULE, KHAU, ma)
    with localcontext() as ctx:
        ctx.prec = 400
        p = Decimal(bam + lech) / Decimal(1 << 256)
    with localcontext() as ctx:
        ctx.prec = 6
        ctx.traps[FloatOperation] = True
        assert chon_mau.duoc_chon(HAT_GIONG, MA_MODULE, KHAU, ma, p) is mong_doi


def test_duong_so_khong_chuyen_float():
    class DecimalCamFloat(Decimal):
        def __float__(self):
            raise AssertionError("Không được chuyển xác suất DEMO sang float")

    chon_mau.duoc_chon(HAT_GIONG, MA_MODULE, KHAU, "PC-DEMO", DecimalCamFloat("0.20"))
    cay = ast.parse(inspect.getsource(chon_mau))
    for nut in ast.walk(cay):
        assert not (isinstance(nut, ast.Constant) and isinstance(nut.value, float))
        assert not isinstance(nut, ast.Div)
        assert not (
            isinstance(nut, ast.Call)
            and (
                isinstance(nut.func, ast.Name) and nut.func.id == "float"
                or isinstance(nut.func, ast.Attribute) and nut.func.attr == "float"
            )
        )


@pytest.mark.parametrize(
    "co_so,he_so,san,mong_doi",
    [
        ("0.20", "1.5", "0.05", "0.30"),
        ("0.01", "2", "0.05", "0.05"),
        ("0.05", "1", "0.05", "0.05"),
        ("0.30", "4", "0.05", "1"),
        ("0.50", "2", "0.05", "1"),
        ("0", "2", "0", "0"),
        ("0.02", "2", "0", "0.04"),
        ("0.02", "1", "0", "0.02"),
    ],
)
def test_tinh_p_kep_san_va_mot(co_so, he_so, san, mong_doi):
    p = chon_mau.tinh_p(Decimal(co_so), Decimal(he_so), Decimal(san))
    assert isinstance(p, Decimal)
    assert p == Decimal(mong_doi)
    assert Decimal(san) <= p <= Decimal(1)


def test_tat_nhan_he_so_duoi_sad():
    assert chon_mau.tinh_p(
        Decimal("0.02"), Decimal("20.25"), Decimal(0), nhan_he_so_duoi_sad=False,
    ) == Decimal("0.02")
