"""CoreGia B8 ngoài gói: Office/AI chỉ giả lập, bytes DEMO trong RAM."""
from types import SimpleNamespace

from e_mask import phong_bi
from e_mask.ho_so_ai import bam_bytes
from e_mask.ho_so_tep import MoTepRAM, MIME
from ho_tro_mask_b7 import bo as bo_b7, chuan_bi_het, giao as giao_b7, chay as chay_b7
from ho_tro_mo_ram import CongMoCoreGia

MO = 'mask.mo_che_van_ban@1'  # Chỉ slot handler test; B9 mới đăng ký mẫu 7.


class CongMoTepGia(CongMoCoreGia):
    def __init__(self, q, dh):
        super().__init__(q, dh)
        self.kiem_tep = True
        self.budget = True
        self.cua = []

    def kiem_tep_mo(self, v, ctx, *, loai, bam_tep, ngan_sach):
        self.cua.append((loai, bam_tep, dict(ngan_sach)))
        self.moc('kiem_tep_' + ngan_sach['giai_doan'], v)
        ref = v.dau_vao['tep']
        return (self.kiem_tep and self.budget
                and ref['mime'] == MIME[loai]
                and bam_bytes(self.core.doc_tep(ref['tep_id'])) == bam_tep)


def bo(loai='docx', **kw):
    b = bo_b7(loai, dang='tep', **kw)
    chuan_bi_het(b)
    giao_b7(b)
    k = chay_b7(b)
    assert k['trang_thai'] == 'XONG', k
    b.bg = b.ram._ban_ghi
    s = b.bg.du_lieu['tep_word' if loai == 'docx' else 'tep_excel']
    b.da_che = s['da_che']
    b.goc_ram = s['goc']
    b.c.ket_qua_cuoi_demo = {}
    b.mo = CongMoTepGia(b.q, b.dh)
    b.mo.core, b.mo.ram = b.c, b.ram
    b.opener = MoTepRAM(ram=b.ram, quyen=b.q, cong=b.mo)
    b.ket = None
    b.so_don = []
    don = b.ram._don
    def dem(bg):
        b.so_don.append(id(bg))
        don(bg)
    b.ram._don = dem

    def mo(v):
        ket = b.opener.mo(v, b.raw_mo, loai=b.loai_mo, ma_yeu_cau=b.ma_mo,
                          dong_viec=b.dong)
        b.ket = ket
        return phong_bi.ket_qua_mo(dict(van_ban_da_mo_che='Đã mở tệp DEMO.',
            so_cho_mo=ket.so_cho_mo, bi_danh_khong_ro=[], mo_day_du=True,
            trang_thai_ma_yeu_cau='DA_DONG'), None)
    b.app._ham[MO] = mo
    return b


def giao(b, raw=None, *, dong=False, ma=None, loai=None):
    b.raw_mo = b.da_che if raw is None else raw
    b.loai_mo = b.loai if loai is None else loai
    b.dong, b.ma_mo = dong, b.ctx.ma_yeu_cau if ma is None else ma
    ref = b.c.them_tep('DEMO-AI.' + b.loai, b.raw_mo, MIME[b.loai])
    b.v = b.c.giao_viec(MO, {'loai': 'tep', 'tep': ref}, {'dong_viec': dong})
    b.q.cap(b.v, loai='mo_che', ma_yeu_cau=b.ctx.ma_yeu_cau)
    return b


def chay(b):
    b.c.chay(b.app)
    return b.c.xem(b.v)


def ket(b):
    k = chay(b)
    assert k['trang_thai'] == 'XONG', k
    assert b.ket is not None
    return b.ket


def da_don(b):
    assert b.ram._ban_ghi is None and b.bg.du_lieu == {}
    assert b.so_don == [id(b.bg)]
    assert not hasattr(b.opener, 'ket_qua')
