"""Gọn khoảng trắng bằng thư viện DEMO ngoài; SDK do Core cấp."""

import kho_tri_thuc_sdk
from kho_tri_thuc_sdk.engine import Engine
from ktt_demo_thu_vien import gon_khoang_trang


app = Engine.tu_khai_bao('engine.json')


@app.nang_luc('van_ban.gon_khoang_trang@1')
def gon_van_ban(viec):
    viec.tien_do(50, 'Đang làm gọn văn bản')
    return {'loai': 'van_ban', 'van_ban': gon_khoang_trang(viec.dau_vao['van_ban'])}


if __name__ == '__main__':
    app.chay()
