"""CoreGia điều phối DEMO ngoài gói; biên nhận giả, không đo model thật."""
from copy import deepcopy
from datetime import datetime, timezone

from e_mask.chuan_bi_ai import CHI_DAN_BAT_BUOC
from e_mask.ho_so_ai import bam_bytes, json_chuan
from ho_tro_ho_so_ai import CongHoSoCoreGiaDemo


class CongChuanBiCoreGia(CongHoSoCoreGiaDemo):
    def __init__(self, core=None):
        super().__init__(core)
        self.cfg = dict(ma_prompt='module.demo.mask', phien_ban_prompt='1',
                        prompt='Yêu cầu của quy trình DEMO.\n' + CHI_DAN_BAT_BUOC,
                        model_uu_tien='model-demo', nha_cung_cap_bat_buoc='local')
        self.ngan_sach, self.giao = {}, {}
        self.con_han, self.budget_biet, self.luu_so = True, True, 0
        self.sua_budget = lambda v: v

    def _quyen(self, viec, ctx):
        if not self.kiem_quyen(viec, ctx, tham_chieu=None, thao_tac='DEMO'):
            raise ValueError('DEMO quyền đã thu hồi')

    def cau_hinh(self, viec, ctx):
        self._quyen(viec, ctx)
        return deepcopy(self.cfg)

    def kiem_ngan_sach(self, viec, ctx, *, de_nghi):
        self._quyen(viec, ctx)
        if not self.budget_biet:
            return None
        khoa = self.chu(viec, ctx)
        bam = bam_bytes(json_chuan(de_nghi))
        if khoa not in self.ngan_sach:
            # SỐ GIẢ cho hợp đồng kiểm, không phải số đo tokenizer/model.
            self.ngan_sach[khoa] = dict(
                bam_de_nghi=bam, nha_cung_cap='local', model=de_nghi['cau_hinh']['model_uu_tien'],
                tokenizer='tokenizer-demo-fixture-v1', context_token=16000, token_ra_toi_da=4000,
                token_vao=[6000] * len(de_nghi['ke_hoach']), tung_doan_da_do=True,
                han_chuoi='2026-11-15T23:59:59+07:00', han_local_giay=60)
        return self.sua_budget(deepcopy(self.ngan_sach[khoa]))

    def kiem_han(self, viec, ctx, *, bien_nhan):
        self._quyen(viec, ctx)
        return (self.con_han and bien_nhan == self.ngan_sach.get(self.chu(viec, ctx))
                and datetime.fromisoformat(bien_nhan['han_chuoi']).astimezone(timezone.utc)
                > datetime(2026, 11, 15, tzinfo=timezone.utc))

    def luu(self, viec, ngu_canh, du_lieu):
        self.luu_so += 1
        return super().luu(viec, ngu_canh, du_lieu)

    def ban_giao(self, viec, ctx, *, dau, yeu_cau):
        self._quyen(viec, ctx)
        raw = self.doc(viec, ctx, dau.ho_so)
        if dau.bam_ho_so != bam_bytes(raw):
            return False
        khoa = self.chu(viec, ctx)
        cu = self.giao.setdefault(khoa, (dau, yeu_cau))
        return cu == (dau, yeu_cau)
