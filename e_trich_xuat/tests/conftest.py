"""Đưa gói tự chứa vào đường import khi test trên Windows hoặc Linux."""

from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi/e_trich_xuat"))
