"""Cửa Core B9 giả ngoài gói, không mạng/model/Office thật; chỉ DEMO."""
from contextlib import contextmanager
import json

from kho_tri_thuc_sdk.engine import LoiNghiepVu, ChuaRo
from e_mask.chay import tao_app
from e_mask.ho_so_ai import bam_bytes, json_chuan
from e_mask.ho_so_tep import MIME
from e_mask.ho_so_tep import CHUAN_BI
from e_mask.kho_anh_xa_ram import _chu
from ho_tro_mask_b7 import bo as bo_b7, chuan_bi_het, giao as giao_local, chay
from ho_tro_mo_ram import CongMoCoreGia

MO = 'mask.mo_che_tep@1'


class CongMoTepSDKGia(CongMoCoreGia):
    def __init__(self, q, dh):
        super().__init__(q, dh)
        self.tep_hop_le = self.budget = True
        self.ngan_sach = []
        self.dang_cach_ly, self.cach_ly, self.phat_hanh = set(), {}, {}
        self.thu_hoi, self.luot_upload = [], 0

    def kiem_tep_mo(self, v, ctx, *, tham_chieu, loai, bam_tep, ngan_sach):
        self.ngan_sach.append(dict(ngan_sach))
        self.moc('kiem_tep_' + ngan_sach['giai_doan'], v)
        return (self.tep_hop_le and self.budget
                and tham_chieu['tep_id'] in self.core.tep_con.get(v.id, ())
                and tham_chieu['mime'] == MIME[loai]
                and bam_bytes(self.core.doc_tep(tham_chieu['tep_id'])) == bam_tep)

    def noi_upload(self):
        tai = self.core._tai_tep_ra
        def goi(ma, viec_id, ten, raw, mime, khoa):
            assert viec_id in self.dang_cach_ly  # Cách ly có trước byte đầu.
            self.luot_upload += 1
            truoc = set(self.core._tep)
            try:
                return tai(ma, viec_id, ten, raw, mime, khoa)
            finally:
                self.cach_ly.setdefault(viec_id, set()).update(set(self.core._tep) - truoc)
        self.core._tai_tep_ra = goi

    @contextmanager
    def ban_giao_cuoi(self, v, ctx, **kw):
        self.dang_cach_ly.add(v.id)
        chu = (ctx.quyen.ma_yeu_cau, ctx.quyen.module, ctx.quyen.nguoi_gui,
               ctx.quyen.tai_lieu, ctx.quyen.vung, ctx.phap_nhan_id)
        han = kw['han_monotonic']
        pending = None
        def kiem():
            self.moc('kiem_quyen', v)
            self.q.xac_minh(v, loai='mo_che', ma_yeu_cau=chu[0], thao_tac='ban_giao')
            v.kiem_huy()
            if self.dh() >= han or _chu(ctx) in self.ram._da_ket_thuc:
                raise LoiNghiepVu('MASK_ANH_XA_KHONG_CON', 'Đã kết thúc DEMO.')
        def nhan(raw):
            nonlocal pending
            kiem()
            self.so_nhan += 1
            pending = raw
            self.moc('nhan', v)
            if self.mat_ack == 'nhan':
                raise ChuaRo('ACK-DEMO')
            return self.tra
        try:
            kiem()
            self.moc('vao', v)
            yield nhan
            self.moc('ra', v)
            kiem()
            self.da_tieu_thu.append(self.ram._ban_ghi is None)
            assert self.ram._ban_ghi is None and pending is not None
            self.core.ket_qua_cuoi_demo[chu] = pending
            self.moc('da_nhan', v)
            if self.mat_ack == 'ra':
                raise ChuaRo('ACK-DEMO')
        finally:
            pending = None
            self.dang_cach_ly.discard(v.id)
            ds = self.cach_ly.pop(v.id, set())
            # Kết quả đã tiếp nhận dù ACK cuối mất được Core giữ đúng quyền.
            if chu in self.core.ket_qua_cuoi_demo:
                for tep_id in ds:
                    self.phat_hanh[tep_id] = chu
            else:
                for tep_id in ds:
                    self.thu_hoi.append(tep_id)
                    self.core._tep.pop(tep_id, None)

    def doc_dung_quyen(self, tep_id, chu):
        if self.phat_hanh.get(tep_id) != chu:
            raise LoiNghiepVu('MASK_MA_YEU_CAU', 'Không có quyền DEMO.')
        return self.core.doc_tep(tep_id)


def bo(loai='docx', *, dang='tep', san=True, **kw):
    b = bo_b7(loai, dang=dang, **kw)
    b.mo = CongMoTepSDKGia(b.q, b.dh)
    b.mo.core, b.mo.ram = b.c, b.ram
    nap_demo = b.app._ham[CHUAN_BI]
    b.app = tao_app(quyen=b.q, cong_chuan_bi_tep=b.cong,
                    cong_hau_kiem_tep=b.cong, cong_mo_tep=b.mo)
    b.app.kho_anh_xa_ram = b.ram
    b.app._ham[CHUAN_BI] = nap_demo
    b.c.ket_qua_cuoi_demo = {}
    if san:
        chuan_bi_het(b)
        giao_local(b)
        k = chay(b)
        assert k['trang_thai'] == 'XONG', k
        b.bg = b.ram._ban_ghi
        s = b.bg.du_lieu['tep_word' if loai == 'docx' else 'tep_excel']
        b.da_che, b.goc_ram = s['da_che'], s['goc']
    b.mo.noi_upload()
    return b


def giao(b, *, raw=None, sua=lambda x: x, json_raw=None, dong=None, tham_so=None, quyen_con=True):
    raw = b.da_che if raw is None else raw
    ref = b.c.them_tep('DEMO-AI.' + b.loai, raw, MIME[b.loai])
    v = dict(ma_yeu_cau=b.ctx.ma_yeu_cau, tep=ref)
    if dong is not None:
        v['dong_viec'] = dong
    v = sua(v)
    boc = b.c.them_tep('DEMO-mau-7.json', json_raw if json_raw is not None else json_chuan(v), 'application/json')
    b.v = b.c.giao_viec(MO, dict(loai='tep', tep=boc), tham_so or {})
    if quyen_con:
        b.c.tep_con[b.v] = {ref['tep_id']}
    b.q.cap(b.v, loai='mo_che', ma_yeu_cau=b.ctx.ma_yeu_cau)
    b.ref_mo, b.boc_mo = ref, boc
    return b


def ket(b):
    k = chay(b)
    assert k['trang_thai'] == 'XONG', k
    t = k['ket_qua']['truong']
    assert set(t) == {'tep_da_mo_che', 'so_cho_mo', 'bi_danh_khong_ro_json', 'mo_day_du', 'trang_thai_ma_yeu_cau'}
    assert t['mo_day_du'] is True and t['bi_danh_khong_ro_json'] == '[]'
    assert t['trang_thai_ma_yeu_cau'] == 'DA_DONG'
    assert b.ram._ban_ghi is None and not b.bg.du_lieu
    return t


def loi(b, *, trang='LOI', don=True):
    k = chay(b)
    assert k['trang_thai'] == trang and k['ket_qua'] is None, k
    if don:
        assert b.ram._ban_ghi is None and not b.bg.du_lieu
    assert not b.mo.phat_hanh and not b.mo.cach_ly
    return k
