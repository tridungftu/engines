"""Không tạo bytecode trong gói; môi trường kiểm dùng SDK 2.5.0."""
import os
import sys

sys.dont_write_bytecode = True

# Cac subprocess tra JSON/loi tieng Viet bang UTF-8 tren Windows va Linux.
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
