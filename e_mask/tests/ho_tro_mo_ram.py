"""C-P4-02/05 chỉ ở CoreGia: cách ly bàn giao, không cache tại engine."""
from contextlib import contextmanager
from dataclasses import replace
import json
from types import SimpleNamespace

from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, ViecDaHuy
from kho_tri_thuc_sdk.thu import CoreGia
from e_mask.anh_xa_ai import tao_anh_xa
from e_mask.chay import tao_app
from e_mask.kho_anh_xa_ram import KhoAnhXaRAM
from ho_tro_ngan import QuyenNganDemo, ai_demo, viec_demo
from ho_tro_ram import DongHoGia

MO = 'mask.mo_che_van_ban@1'
ALIAS = '[[MASKCT-DEMO-0001]]'
TEN = 'Công ty DEMO Ánh Dương'
DUOI = '; 1.000.000 VND ngày 30/10/2026.'


class CongMoCoreGia:
    def __init__(self, q, dh):
        self.q, self.dh, self.core, self.ram = q, dh, None, None
        self.moc = lambda ten, v: None
        self.mat_ack, self.tra, self.so_nhan = None, True, 0
        self.ngu_canh, self.da_tieu_thu = [], []

    @contextmanager
    def ban_giao_cuoi(self, v, ctx, *, bam_dau_vao, han_monotonic):
        chu = (ctx.quyen.ma_yeu_cau, ctx.quyen.module, ctx.quyen.nguoi_gui,
               ctx.quyen.tai_lieu, ctx.quyen.vung, ctx.phap_nhan_id)
        self.ngu_canh.append((chu, bam_dau_vao, han_monotonic))
        pending = None

        def kiem():
            self.moc('kiem_quyen', v)
            self.q.xac_minh(v, loai='mo_che', ma_yeu_cau=chu[0], thao_tac='ban_giao')
            if self.dh() >= han_monotonic:
                raise LoiNghiepVu('MASK_ANH_XA_KHONG_CON', 'Hết hạn DEMO.')
            v.kiem_huy()

        def nhan(raw):
            nonlocal pending
            kiem()
            self.so_nhan += 1
            assert type(raw) is bytes
            # Giữ cục bộ ở phía Core giả, chưa công khai cho module.
            pending = raw
            self.moc('nhan', v)
            if self.mat_ack == 'nhan':
                raise ChuaRo('chuoi-tu-nguon-khong-duoc-lo')
            return self.tra

        kiem()
        self.moc('vao', v)
        try:
            yield nhan
            self.moc('ra', v)
            kiem()
            self.da_tieu_thu.append(self.ram._ban_ghi is None)
            assert self.ram._ban_ghi is None
            if pending is None:
                raise LoiNghiepVu('MASK_MO_CHE_CHUA_CO_CUA_CORE', 'Chưa nhận DEMO.')
            # Core được giữ kết quả cuối đã tiếp nhận đúng quyền. Không
            # giữ map hoặc giao nó cho Cloud. Engine không có bản cache.
            self.core.ket_qua_cuoi_demo[chu] = pending
            self.moc('da_nhan', v)
            if self.mat_ack == 'ra':
                raise ChuaRo('chuoi-tu-nguon-khong-duoc-lo')
        finally:
            pending = None


def bo(*, goc=None, phep=None, aliases=None):
    q, dh = QuyenNganDemo(), DongHoGia()
    cong = CongMoCoreGia(q, dh)
    app = tao_app(quyen=q, cong_mo_che=cong)
    app.kho_anh_xa_ram = ram = KhoAnhXaRAM(quyen=q, dong_ho=dh, hen_gio=dh.hen_gio)
    c = CoreGia(app)
    c.ket_qua_cuoi_demo = {}
    cong.core, cong.ram = c, ram
    v = viec_demo('che-ram-DEMO')
    v.cau_hinh = {'thoi_han_anh_xa_giay': 600}
    ctx = q.cap(v.id)
    goc = TEN + DUOI if goc is None else goc
    phep = [(0, len(TEN), ALIAS)] if phep is None else phep
    m = tao_anh_xa(goc, phep)
    with ram.buoc(v) as b:
        b.du_lieu.update(anh_xa_cuoi=m, alias_nguyen_van=m.alias_nguyen_van() if aliases is None else aliases,
                         giai_doan_ai='DA_HAU_KIEM')
        b.cho_ai()
    da_don, don = [], ram._don

    def ghi_don(bg):
        da_don.append(id(bg))
        don(bg)

    ram._don = ghi_don
    return SimpleNamespace(q=q, dh=dh, cong=cong, app=app, ram=ram, c=c,
                           ctx=ctx, m=m, da_don=da_don)


def giao(b, *, chu=None, ai=None, dong=False, mau3=None, ma=None):
    ma = b.ctx.ma_yeu_cau if ma is None else ma
    if mau3 is not None:
        raw = json.dumps(mau3, ensure_ascii=False).encode('utf-8')
        dau = {'loai': 'tep', 'tep': b.c.them_tep('mo-ram-DEMO.json', raw, 'application/json')}
    else:
        ai = ai_demo(b.m.da_che if chu is None else chu, ma) if ai is None else ai
        dau = {'loai': 'tra_loi_ai', 'tra_loi_ai': ai}
    v = b.c.giao_viec(MO, dau, {'dong_viec': dong})
    b.q.cap(v, loai='mo_che', ma_yeu_cau=b.ctx.ma_yeu_cau)
    b.v = v
    return v


def chay(b):
    b.c.chay(b.app)
    return b.c.xem(b.v)


def ket(b):
    k = chay(b)
    assert k['trang_thai'] == 'XONG', k
    return k['ket_qua']['truong']
