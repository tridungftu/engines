"""Bridge G3-GOI-22: giữ cùng module/hàm/DTO với reader trong gói hóa đơn."""

import sys as _sys

from ..engines.e_hoa_don.lib import hoa_don_xml as _reader

_sys.modules[__name__] = _reader
