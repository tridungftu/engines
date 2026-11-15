"""Adapter Local CoreGia chỉ RAM R4; không cung cấp cửa snapshot Core."""
from copy import deepcopy

from ho_tro_mask_r5 import CongRAMCoreGia


class CongChuanBiCoreGia(CongRAMCoreGia):
    def __init__(self, core=None):
        super().__init__()
        self.core = core
        self._ve, self.thu_hoi = set(), False
        self.budget_biet, self.luu_so = True, 0
        self.sua_budget = lambda v: v
        self.ngan_sach = self.budget

    @staticmethod
    def chu(viec, ctx):
        return (ctx.ma_yeu_cau, ctx.phien, ctx.module, ctx.nguoi_gui,
                ctx.tai_lieu, ctx.vung, viec.ngu_canh['phap_nhan_id'])

    def cap(self, viec, ctx):
        self._ve.add(self.chu(viec, ctx))

    def kiem_quyen(self, viec, ctx, **_):
        viec.kiem_huy()
        return not self.thu_hoi and self.chu(viec, ctx) in self._ve

    def _quyen(self, viec, ctx):
        if not self.kiem_quyen(viec, ctx):
            raise ValueError('Quyền DEMO đã thu hồi.')

    def cau_hinh(self, viec, ctx):
        self._quyen(viec, ctx)
        return super().cau_hinh(viec, ctx)

    def chi_so_doan(self, viec, ctx, **kw):
        self._quyen(viec, ctx)
        return super().chi_so_doan(viec, ctx, **kw)

    def kiem_ngan_sach(self, viec, ctx, **kw):
        self._quyen(viec, ctx)
        if not self.budget_biet:
            return None
        return self.sua_budget(super().kiem_ngan_sach(viec, ctx, **kw))

    def kiem_han(self, viec, ctx, **kw):
        self._quyen(viec, ctx)
        return super().kiem_han(viec, ctx, **kw)

    def ban_giao(self, viec, ctx, **kw):
        self._quyen(viec, ctx)
        return super().ban_giao(viec, ctx, **kw)

    def luu(self, *a, **kw):
        raise AssertionError('Không được ghi snapshot Core.')

    def doc(self, *a, **kw):
        raise AssertionError('Không được đọc snapshot Core.')
