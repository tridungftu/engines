"""Bridge tương thích: ``ai_cuc_bo`` đã chuyển sang ``engines/e_hoi_ai/lib/ai_cuc_bo.py`` (G3-GOI-06).

Trỏ tới chính module lõi (cùng đối tượng) để ``patch`` globals từ đường cũ vẫn tới đúng chỗ.
"""
import sys as _sys

from ..engines.e_hoi_ai.lib import ai_cuc_bo as _loi

_sys.modules[__name__] = _loi
