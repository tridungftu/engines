"""Khai báo ngăn RAM từ bản khai SDK 2.1 đi kèm gói độc lập."""
import json
from pathlib import Path

from .ngan import NganBoNho

KHAI_BAO_NGAN = json.loads(
    (Path(__file__).resolve().parents[1] / "KHAI-SDK-2.1.json").read_text(encoding="utf-8")
)["ngan_du_lieu"]


def tao_ngan_bo_nho():
    return NganBoNho(KHAI_BAO_NGAN)
