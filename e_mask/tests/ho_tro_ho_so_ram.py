"""Fixture unit của HoSoAI trên kho RAM R4, không phải API runtime."""
from copy import deepcopy
from dataclasses import replace
from types import SimpleNamespace
from uuid import uuid4

from kho_tri_thuc_sdk.engine import LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia
from e_mask.ho_so_ai import DauHoSoRAM, bam_bytes, json_chuan
from e_mask.kho_anh_xa_ram import KhoAnhXaRAM
from ho_tro_hau_kiem_ai import QuanSatNgan
from ho_tro_ngan import QuyenNganDemo, viec_demo
from ho_tro_ram import DongHoGia


class HoSoRAMDemo:
    def __init__(self, ram):
        self.ram = ram
        self.moc = lambda ten, v: None

    def luu(self, viec, ma, h):
        raw = h.thanh_bytes()  # Kiểm map/Unicode/trần thực sự trước lưu RAM.
        with self.ram.buoc(viec, ma_yeu_cau=ma) as buoc:
            self.moc('luu', viec)
            buoc.kiem()
            du = buoc.du_lieu
            bam = bam_bytes(raw)
            if 'dau' in du and du['dau'].bam_ho_so != bam:
                raise LoiNghiepVu('MASK_AI_XUNG_DOT', 'Nội dung yêu cầu đã thay đổi.', thu_lai_duoc=True)
            du.setdefault('dau', DauHoSoRAM(uuid4().hex, bam))
            du['ho_so'] = h
            buoc.cho_ai()
            self.moc('chot', viec)
            buoc.kiem()
            buoc.cho_ai()
            return du['dau']

    def doc(self, viec, ma, dau):
        with self.ram.buoc(viec, ma_yeu_cau=ma) as buoc:
            self.moc('doc', viec)
            du = buoc.du_lieu
            if (type(dau) is not DauHoSoRAM or du.get('dau') != dau
                    or 'ho_so' not in du or bam_bytes(du['ho_so'].thanh_bytes()) != dau.bam_ho_so):
                raise LoiNghiepVu('MASK_AI_HO_SO', 'Không xác minh được hồ sơ trong RAM.')
            buoc.cho_ai()
            return du['ho_so']


def bo_kho():
    class QuyenHoSoRAM(QuyenNganDemo):
        def xac_minh_ram(self, viec, **kw):
            ctx = super().xac_minh_ram(viec, **kw)
            return replace(ctx, phap_nhan_id=viec.ngu_canh.get('phap_nhan_id'))
    v, q, dh, c = viec_demo(), QuyenHoSoRAM(), DongHoGia(), CoreGia()
    v.cau_hinh = {'thoi_han_anh_xa_giay': 600}
    ctx = q.cap(v.id)
    ram = KhoAnhXaRAM(quyen=q, dong_ho=dh, hen_gio=dh.hen_gio)
    return SimpleNamespace(viec=v, q=q, ctx=ctx, ram=ram, dh=dh,
                           cong=SimpleNamespace(core=c), n=QuanSatNgan(c), kho=HoSoRAMDemo(ram))
