"""Gói độc lập, không tạo mã biên dịch trong thư mục gói."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'goi/e_mask'))
