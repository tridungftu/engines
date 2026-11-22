"""Chạy KttCore giả bằng Node, không mạng."""
from pathlib import Path
import shutil
import subprocess

import pytest


def test_man_admin_node():
    node = shutil.which('node')
    if node is None:
        pytest.skip('Chưa có Node để kiểm màn bằng KttCore giả.')
    tep = sorted((Path(__file__).parent/'ui').glob('*.test.mjs'))
    kq = subprocess.run([node, '--test', *map(str, tep)],
                        capture_output=True, encoding='utf-8', timeout=30)
    assert kq.returncode == 0, kq.stdout + kq.stderr
