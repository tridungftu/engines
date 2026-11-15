"""Chạy bộ UI Node/KttCore giả cùng cổng pytest bắt buộc."""
from pathlib import Path
import subprocess


def test_ui_kttcore_gia():
    kq = subprocess.run(["node", "--test", str(Path(__file__).parent / "ui" / "cau_hinh.test.mjs")],
                        capture_output=True, encoding="utf-8", timeout=20)
    assert kq.returncode == 0, kq.stdout + kq.stderr
