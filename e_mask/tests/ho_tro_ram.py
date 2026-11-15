"""Adapter vòng đời CoreGia/đồng hồ giả, tuyệt đối ngoài gói chạy."""
from dataclasses import replace

from e_mask.quyen_yeu_cau import GhimTienTrinh, NguCanhRAM, SuKienRAM


class VongDoiCoreGia:
    """Mixin chỉ cấp dữ liệu DEMO, không chứng minh ghim trên Core thật."""
    def dang_ky_vong_doi_ram(self, ham, *, phien_ram):
        if not hasattr(self, 'ram_dang_ky'):
            self.ram_dang_ky, self.ram_da_cap, self.ram_ctx = {}, {}, {}
        self.ram_dang_ky[phien_ram] = ham
        return GhimTienTrinh(getattr(self, 'ram_instance', 'instance-DEMO'), phien_ram,
                            getattr(self, 'ram_ghim', True), getattr(self, 'ram_bao', True))

    def xac_minh_ram(self, viec, *, ngu_canh, phien_ram, thao_tac):
        ma = ngu_canh.ma_yeu_cau
        tao = ma not in self.ram_da_cap
        if tao:
            self.ram_da_cap[ma] = (getattr(self, 'ram_instance', 'instance-DEMO'), phien_ram)
        instance, phien = self.ram_da_cap[ma]
        ctx = NguCanhRAM(ngu_canh, getattr(self, 'ram_phap_nhan', 'pn-demo'), instance, phien,
                         getattr(self, 'ram_han', None), tao)
        ctx = getattr(self, 'ram_sua_ctx', lambda v: v)(ctx)
        self.ram_ctx[ma] = ctx
        return ctx

    def bao_ram(self, ma, ket_thuc='HUY', **doi):
        ctx = replace(self.ram_ctx[ma], **doi)
        for ham in tuple(self.ram_dang_ky.values()):
            ham(SuKienRAM(ctx, ket_thuc))


class DongHoGia:
    def __init__(self):
        self.luc, self.hen = 100.0, []

    def __call__(self):
        return self.luc

    def hen_gio(self, giay, ham):
        hen = HenGia(self, self.luc + giay, ham)
        self.hen.append(hen)
        return hen

    def tien(self, giay, *, chay_timer=True):
        self.luc += giay
        if chay_timer:
            for hen in tuple(self.hen):
                if hen.da_bat and not hen.da_huy and hen.luc <= self.luc:
                    hen.no()


class HenGia:
    def __init__(self, dong_ho, luc, ham):
        self.dong_ho, self.luc, self.ham = dong_ho, luc, ham
        self.da_bat, self.da_huy = False, False

    def start(self):
        self.da_bat = True

    def cancel(self):
        self.da_huy = True

    def no(self):
        # Có thể cố tình gọi timer cũ đã cancel để kiểm callback đang đua.
        self.da_huy = True
        self.ham()
