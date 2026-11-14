"""Nạp gói độc lập; giữ gói sạch tệp biên dịch khi chạy pytest."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_hoi_ai"))
