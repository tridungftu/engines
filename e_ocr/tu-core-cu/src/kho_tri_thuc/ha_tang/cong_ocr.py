"""Bridge G3-GOI-16: cùng module cổng OCR, kể cả globals được patch.

Lõi thuộc ``engines/e_ocr/lib/cong_ocr.py``; đường legacy giữ cùng lớp,
exception, hằng và khóa với engine, không nạp một bản implementation khác.
"""

import sys as _sys

from ..engines.e_ocr.lib import cong_ocr as _loi

_sys.modules[__name__] = _loi
