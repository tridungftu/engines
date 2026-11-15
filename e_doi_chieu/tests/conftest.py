"""Không tạo bytecode trong gói; môi trường kiểm dùng SDK 2.2.0."""
import sys

sys.dont_write_bytecode = True
