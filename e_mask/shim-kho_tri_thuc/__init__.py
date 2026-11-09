"""Shim nguồn: giữ tên gói ``kho_tri_thuc.engines.e_mask``, mã nằm ở ``engines/e_mask``.

Chỉ đặt ``__path__`` sang thư mục gói ở gốc repo (suy từ vị trí tệp này,
không dùng cwd, không đổi ``sys.path``, không nạp cấu hình/engine khác).
Không có mã nghiệp vụ ở đây; thiếu gói thì báo lỗi rõ, không lùi sang bản khác.
Mask chưa có engine.json (chưa công bố capability) nên kiểm theo chay.py.
"""

from pathlib import Path as _Path

_GOC = _Path(__file__).resolve().parents[4] / 'engines' / 'e_mask'
if not (_GOC / 'chay.py').is_file():
    raise ImportError('Thiếu gói engine e_mask tại thư mục engines của repo.')
__path__ = [str(_GOC)]
