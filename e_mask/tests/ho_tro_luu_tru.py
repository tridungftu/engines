"""Nạp hiện vật lịch sử riêng cho test, giữ nguyên byte sau khi chuyển kho."""
from pathlib import Path
import sys

from e_mask import quyen_yeu_cau

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'LUU-TRU'))
# Hiện vật dùng relative import cũ; nối phụ thuộc chỉ trong test, kể cả
# khi multiprocessing spawn nhập lại mô-đun test trên Windows/Linux.
sys.modules['mask_truoc_ngan.quyen_yeu_cau'] = quyen_yeu_cau
from mask_truoc_ngan import cau_hinh_may, kho_tam
from mask_truoc_ngan.kho_tam import KhoTam
