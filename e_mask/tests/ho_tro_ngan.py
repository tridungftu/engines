"""Quyền DEMO tin cậy được test cấp riêng; không nằm trong gói."""
from dataclasses import replace
from types import SimpleNamespace

from e_mask.quyen_yeu_cau import NguCanhTinCay, loi_kho

TEN = 'Công ty DEMO Ánh Dương'
VAN_BAN = TEN + '; 1.000.000 VND ngày 30/10/2026.'


class QuyenNganDemo:
    def __init__(self):
        self.ve, self.thu_hoi = {}, False
        self.module, self.nguoi_gui, self.tai_lieu, self.vung = 'module-demo', 'nguoi-demo', 'tai-lieu-demo', 'DEMO'

    def cap(self, viec_id, *, loai='che', ma_yeu_cau=None):
        ctx = NguCanhTinCay(ma_yeu_cau or 'yeu-cau-demo-' + viec_id, 'luot-demo-' + viec_id,
                           'phien-demo', self.module, self.nguoi_gui, self.tai_lieu, self.vung)
        self.ve[viec_id, loai] = ctx
        return ctx

    def xac_minh(self, viec, *, loai, ma_yeu_cau, thao_tac):
        if self.thu_hoi or (viec.id, loai) not in self.ve:
            raise loi_kho('MASK_MA_YEU_CAU')
        ctx = self.ve[viec.id, loai]
        if ma_yeu_cau is not None and ma_yeu_cau != ctx.ma_yeu_cau:
            raise loi_kho('MASK_MA_YEU_CAU')
        return replace(ctx, module=self.module, nguoi_gui=self.nguoi_gui, tai_lieu=self.tai_lieu, vung=self.vung)


def viec_demo(ma='viec-demo'):
    return SimpleNamespace(id=ma, ngu_canh={'buoc': 1, 'viec_id': ma, 'phap_nhan_id': 'pn-demo'},
                           dau_vao={'loai': 'van_ban', 'van_ban': VAN_BAN}, tham_so={}, kiem_huy=lambda: None)


ADMIN = SimpleNamespace(xac_minh_admin=lambda: 'DEMO')


def ai_demo(chu, ma):
    return dict(phien_ban=1, trang_thai='co_can_cu', tra_loi=chu, du_lieu=None,
                trich_dan=[], kiem_trich_dan={'dat': True, 'loi': []}, nha_cung_cap='local',
                model='model-demo', ly_do_chon_model='DEMO', ma_prompt='demo', phien_ban_prompt='1',
                phien_ban_engine='e_hoi_ai 1.0.0', bam_dau_vao='sha256:' + '0'*64,
                chuyen_tiep={'ma_yeu_cau': ma}, canh_bao=[])
