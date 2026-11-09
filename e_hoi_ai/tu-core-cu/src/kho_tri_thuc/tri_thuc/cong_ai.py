"""Bridge tương thích: lõi cổng AI đã chuyển sang ``engines/e_hoi_ai/lib/cong_ai.py`` (G3-GOI-06).

Đường import cũ ``kho_tri_thuc.tri_thuc.cong_ai`` trỏ tới CHÍNH module lõi (cùng đối tượng,
không sao chép) nên ``patch.object``/globals từ consumer cũ tới đúng nơi. ``BoGhiPostgres``
thuộc phía Core (``core.nhat_ky_ai_legacy``) được gắn lại vào module này để API cũ đủ.
"""
import sys as _sys

from ..core import nhat_ky_ai_legacy as _pg
from ..engines.e_hoi_ai.lib import cong_ai as _loi

_loi.BoGhiPostgres = _pg.BoGhiPostgres
_sys.modules[__name__] = _loi
