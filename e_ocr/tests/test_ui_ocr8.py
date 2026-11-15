"""Chạy màn OCR với KttCore và DOM giả của Node, không mạng."""

from pathlib import Path
import shutil
import subprocess


def test_ui_bang_kttcore_gia():
    node = shutil.which("node")
    assert node, "Cần Node để kiểm màn cấu hình OCR bằng KttCore giả."
    ket_qua = subprocess.run(
        [node, "--test", str(Path(__file__).parent / "ui" / "test_cau_hinh.mjs")],
        capture_output=True, encoding="utf-8", timeout=30,
    )
    assert ket_qua.returncode == 0, ket_qua.stdout + ket_qua.stderr
