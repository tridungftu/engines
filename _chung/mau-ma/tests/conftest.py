"""Thêm factory tương thích SDK vào CAC_BAN_NGAN để chạy lại cùng hợp đồng."""

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ngan import NganBoNho


KHAI_BAO = [
    {"bang": "danh_muc", "khoa": ["ma"], "pham_vi": "engine",
     "duy_nhat": [["bam"], ["bi_danh"]]},
    {"bang": "han_muc", "khoa": ["ngay"], "pham_vi": "engine"},
    {"bang": "luot", "khoa": ["ma"], "pham_vi": "phap_nhan",
     "duy_nhat": [["phap_nhan_id", "bam"]]},
]

# Factory nhận khai_bao, trả ngăn gốc mới, không chia sẻ giữa các test.
CAC_BAN_NGAN = [pytest.param(NganBoNho, id="RAM")]


@pytest.fixture(params=CAC_BAN_NGAN)
def tao_ngan(request):
    return request.param


@pytest.fixture
def ngan(tao_ngan):
    return tao_ngan(KHAI_BAO)
