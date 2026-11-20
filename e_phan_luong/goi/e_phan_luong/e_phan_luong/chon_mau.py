"""Chọn mẫu SHA-256 có thể tái hiện, không dùng số thực nhị phân."""
from __future__ import annotations

import hashlib
import secrets
from decimal import Decimal
from fractions import Fraction


def sinh_hat_giong() -> bytes:
    """Sinh 32 byte ngẫu nhiên cho một lượt; bên gọi lưu qua Core."""
    return secrets.token_bytes(32)


def bam_hat_giong(hg) -> str:
    """Băm công bố trong kết quả, không công bố hạt giống gốc."""
    return "sha256:" + hashlib.sha256(hg).hexdigest()


def gia_tri_bam(hg, ma_module, khau, ma) -> int:
    """Công thức tái hiện dành cho kiểm toán viên:

    int.from_bytes(sha256(hg + b"\\x1f" + ma_module.encode("utf-8")
                         + b"\\x1f" + khau.encode("utf-8")
                         + b"\\x1f" + ma.encode("utf-8")).digest(), "big")
    """
    du_lieu = b"\x1f".join(
        (hg, ma_module.encode("utf-8"), khau.encode("utf-8"), ma.encode("utf-8"))
    )
    return int.from_bytes(hashlib.sha256(du_lieu).digest(), "big")


def duoc_chon(hg, ma_module, khau, ma, p: Decimal) -> bool:
    """So nghiêm ngặt băm < p × 2^256 bằng số nguyên chính xác.

    Fraction(Decimal) giữ nguyên mọi chữ số, độc lập độ chính xác của
    Decimal context. Nhân chéo tránh làm tròn ngưỡng và không qua float.
    """
    phan_so = Fraction(p)
    return (
        gia_tri_bam(hg, ma_module, khau, ma) * phan_so.denominator
        < phan_so.numerator * (1 << 256)
    )


def tinh_p(
    p_co_so: Decimal,
    he_so: Decimal,
    san: Decimal,
    *,
    nhan_he_so_duoi_sad: bool = True,
) -> Decimal:
    """Kẹp p trong [san, 1]; mặc định nhân hệ số cờ.

    Dưới SAD: bên gọi truyền p_co_so = cs.ty_le_duoi_sad và san = 0.
    Khi cần tắt nhân cờ riêng cho vùng này, truyền
    nhan_he_so_duoi_sad=False (điểm chờ quyết định Q4, GIAO-CODEX §2.3).
    """
    p = p_co_so * he_so if nhan_he_so_duoi_sad else p_co_so
    return min(Decimal(1), max(san, p))
