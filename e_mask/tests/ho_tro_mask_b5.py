"""Fixture Word/CoreGia của B5; chỉ DEMO, không lưu tài liệu ra đĩa."""
from types import SimpleNamespace

from kho_tri_thuc_sdk.engine import Viec
from kho_tri_thuc_sdk.thu import CoreGia

from e_mask.chay import tao_app
from e_mask.doc_word import doc_word
from e_mask.ghi_zip import ghi_goi
from e_mask.kho_anh_xa_ram import KhoAnhXaRAM
from e_mask.va_xml import lap_kich_ban
from ho_tro_mask_b1 import word_demo
from ho_tro_mask_b2 import word_day_du, zip_office
from ho_tro_ngan import QuyenNganDemo
from ho_tro_ram import DongHoGia
from test_mask_r2 import _dong, _them, _ket_qua_demo

TEN = 'Công ty DEMO Ánh Dương'
ALIAS = '[[MASKCT-0001]]'
DS = [dict(gia_tri=TEN, nhom='CONG_TY')]


def bo(*, seeds=((TEN, 'CONG_TY', ALIAS),), ttl=600):
    q, dh = QuyenNganDemo(), DongHoGia()
    app = tao_app(quyen=q)
    c = CoreGia(app)
    c.dat_cau_hinh('e_mask', {'thoi_han_anh_xa_giay': ttl})
    ma = c.giao_viec('mask.che_van_ban@1', {'loai': 'van_ban', 'van_ban': 'DEMO'})
    q.cap(ma)
    nhan = {}
    def nap(viec):
        nhan['viec'] = viec
        for ten, nhom, alias in seeds:
            dong = _dong(ten, trang_thai='CHINH_THUC')
            dong['nhom'] = nhom
            _them(viec, dong, alias)
        return _ket_qua_demo()
    app._ham['mask.che_van_ban@1'] = nap
    c.chay(app)
    assert c.xem(ma)['trang_thai'] == 'XONG'
    v = nhan['viec']
    # B5 chưa nối handler. Adapter giao lại qua transport CoreGia thật để
    # ngăn giữ kiểm lease/instance thay vì gọi trên một việc đã XONG.
    c._viec[ma]['trang_thai'] = 'CHO'
    c._hang.append(ma)
    assert v._dt.nhan_viec(0)['id'] == ma
    ram = KhoAnhXaRAM(quyen=q, dong_ho=dh, hen_gio=dh.hen_gio)
    return SimpleNamespace(q=q, dh=dh, c=c, v=v, ram=ram, app=app,
                           ma=q.ve[ma, 'che'].ma_yeu_cau)


def word(chu=TEN, *, noi_dung=None, codec=None):
    phan = word_demo(chu=chu, noi_dung=noi_dung)
    if codec:
        phan['word/document.xml'] = phan['word/document.xml'].encode(codec)
    return zip_office(phan)


def moi_vung_co_ten():
    """Thay dữ liệu fixture B2 bằng cùng tên DEMO; không sửa node kỹ thuật."""
    doc = doc_word(zip_office(word_day_du()), kiem_huy=lambda: None)
    thay = []
    for i, v in enumerate(doc.vung):
        if v.phan == 'docProps/custom.xml' and v.van_ban.isdigit():
            continue  # Custom kiểu số phải giữ kiểu/số, không nhét tên vào i4.
        if all(m.kieu != 'ky_hieu' for m in v.anh_xa):
            if v.van_ban:
                them = ' %1' if '%1' in v.van_ban else ''
                if v.phan == 'docProps/custom.xml' and v.anh_xa[0].thuoc_tinh == 'name':
                    them += '; DEMO ' + chr(65 + i)
                thay.append((i, 0, len(v.van_ban), TEN + them))
        else:
            for m in v.anh_xa:
                if m.kieu == 'text' and m.bat_dau < m.ket_thuc:
                    thay.append((i, m.bat_dau, m.ket_thuc, TEN + '; '))
    script = lap_kich_ban(doc, tuple(thay), kiem_huy=lambda: None)
    return ghi_goi(doc, script, kiem_huy=lambda: None)
