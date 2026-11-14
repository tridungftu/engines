"""Kiểm tra chuỗi tiếng Việt trong công cụ không bị hỏng mã hóa."""
import ast
from pathlib import Path
import re


def test_chuoi_khong_co_dau_hoi_giua_hai_chu_cai():
    nguon = (Path(__file__).resolve().parents[1] / 'cong-cu' / 'thu_abbyy_that.py').read_text(encoding='utf-8')
    for nut in ast.walk(ast.parse(nguon)):
        if isinstance(nut, ast.Constant) and isinstance(nut.value, str):
            assert not re.search(r'[^\W\d_]\?[^\W\d_]', nut.value), nut.value
