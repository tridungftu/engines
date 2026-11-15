"""Adapter C-P4-04 ngoài gói, chỉ CoreGia/DEMO; không API Core thật."""
from copy import deepcopy
from dataclasses import asdict
import json
from types import SimpleNamespace

from kho_tri_thuc_sdk.thu import CoreGia
from e_mask import chuan_bi_ai as cb
from e_mask.chay import tao_app
from e_mask.hau_kiem_ai import HauKiemAI, NANG_LUC
from e_mask.ho_so_ai import bam_bytes, json_chuan
from ho_tro_ngan import QuyenNganDemo, ai_demo, viec_demo
from ho_tro_ram import DongHoGia
from e_mask.kho_anh_xa_ram import KhoAnhXaRAM
from test_mask_r2 import _dong, _them


class CongRAMCoreGia:
    def __init__(self):
        self.cfg = dict(ma_prompt='module.demo.mask', phien_ban_prompt='1',
                        prompt='Quy trình DEMO.\n' + cb.CHI_DAN_BAT_BUOC,
                        model_uu_tien='model-demo', nha_cung_cap_bat_buoc='local')
        self.i, self.giao, self.budget, self.nguon, self.raw = 0, {}, {}, None, None
        self.con_han, self.cac_cua = True, []
        self.moc = lambda ten, v: None

    def cau_hinh(self, v, ctx):
        self.cac_cua.append(('cau_hinh', {}))
        self.moc('cau_hinh', v)
        return deepcopy(self.cfg)

    def chi_so_doan(self, v, ctx, *, so_doan):
        self.cac_cua.append(('chi_so_doan', dict(so_doan=so_doan)))
        self.moc('chi_so_doan', v)
        return self.i

    def kiem_ngan_sach(self, v, ctx, *, de_nghi):
        self.cac_cua.append(('kiem_ngan_sach', deepcopy(de_nghi)))
        self.moc('kiem_ngan_sach', v)
        self.budget.setdefault(ctx.ma_yeu_cau, dict(
            bam_de_nghi=bam_bytes(json_chuan(de_nghi)), nha_cung_cap='local', model='model-demo',
            tokenizer='tokenizer-DEMO', context_token=16000, token_ra_toi_da=4000,
            token_vao=[6000] * len(de_nghi['ke_hoach']), tung_doan_da_do=True,
            han_chuoi='2026-11-15T23:59:59+07:00', han_local_giay=60))
        return deepcopy(self.budget[ctx.ma_yeu_cau])

    def kiem_han(self, v, ctx, *, bien_nhan):
        self.cac_cua.append(('kiem_han', deepcopy(bien_nhan)))
        self.moc('kiem_han', v)
        return self.con_han and bien_nhan == self.budget[ctx.ma_yeu_cau]

    def ban_giao(self, v, ctx, **kw):
        self.cac_cua.append(('ban_giao', deepcopy(kw)))
        self.moc('ban_giao', v)
        if 'yeu_cau' in kw:
            y = json.loads(kw['yeu_cau'])
            i = y['yeu_cau_ai']['chuyen_tiep']['mask_2c']['chi_so_doan']
            return self.giao.setdefault(i, y) == y
        return True

    def nhan_phan_hoi(self, v, ctx, **kw):
        self.cac_cua.append(('nhan_phan_hoi', deepcopy(kw)))
        self.moc('nhan_phan_hoi', v)
        return self.raw

    def chung_thuc(self, v, ctx, *, de_nghi):
        self.cac_cua.append(('chung_thuc', de_nghi))
        self.moc('chung_thuc', v)
        return de_nghi == self.nguon


def noi_handler(app, q, cong, *, seeds=()):
    # R6 đã nối kho R4 trong chay.py. Fixture chỉ nạp catalogue DEMO;
    # toàn bộ kiểm R5 tiếp tục đi qua handler runtime thật, không thay nó.
    cb_that = app._ham[cb.NANG_LUC]
    con_seed = list(seeds)
    def chuan_bi(v):
        for ten, nhom, alias in con_seed:
            dong = _dong(ten, trang_thai='CHINH_THUC')
            dong['nhom'] = nhom
            _them(v, dong, alias)
        con_seed.clear()
        return cb_that(v)
    app._ham[cb.NANG_LUC] = chuan_bi
    return cb_that


def bo(chu='nội dung; 1.000.000 VND ngày 30/10/2026.', *, seeds=()):
    q, cong, dh = QuyenNganDemo(), CongRAMCoreGia(), DongHoGia()
    app = tao_app(quyen=q, cong_chuan_bi_ai=cong, cong_hau_kiem_ai=cong)
    app.kho_anh_xa_ram = ram = KhoAnhXaRAM(quyen=q, dong_ho=dh, hen_gio=dh.hen_gio)
    noi_handler(app, q, cong, seeds=seeds)
    c = CoreGia(app)
    v = c.giao_viec(cb.NANG_LUC, {'loai': 'van_ban', 'van_ban': chu})
    ctx = q.cap(v)
    return SimpleNamespace(q=q, cong=cong, dh=dh, ram=ram, c=c, app=app, v=v, ctx=ctx, chu=chu)


def chay(b):
    b.c.chay(b.app)
    return b.c.xem(b.v)


def chuan_bi(b):
    k = chay(b)
    assert k['trang_thai'] == 'XONG', k
    return k


def chuan_bi_tat_ca(b):
    k = chuan_bi(b)
    n = k['ket_qua']['yeu_cau_ai']['chuyen_tiep']['mask_2c']['so_doan']
    for i in range(1, n):
        b.cong.i = i
        b.v = b.c.giao_viec(cb.NANG_LUC, {'loai': 'van_ban', 'van_ban': b.chu})
        b.q.cap(b.v, ma_yeu_cau=b.ctx.ma_yeu_cau)
        chuan_bi(b)
    return k


def giao(b, ts=(), *, sua=lambda v: v):
    ds = []
    for i, y in sorted(b.cong.giao.items()):
        m = y['yeu_cau_ai']['chuyen_tiep']['mask_2c']
        cac = []
        for a, z, loai, muc in ts:
            if m['bat_dau_doan'] <= a < z <= m['ket_thuc_doan']:
                cac.append(dict(loai=loai, muc=muc, nguyen_van=b.chu[a:z],
                                bat_dau=a-m['bat_dau_doan'], ket_thuc=z-m['bat_dau_doan']))
        ai = ai_demo('Không thấy căn cứ.', b.ctx.ma_yeu_cau)
        ai.update(du_lieu=dict(da_quet_het=True, thuc_the=cac), trang_thai='co_can_cu' if cac else 'khong_thay_can_cu',
                  trich_dan=[dict(cau=t['nguyen_van'], bat_dau=t['bat_dau'], ket_thuc=t['ket_thuc']) for t in cac],
                  chuyen_tiep=deepcopy(y['yeu_cau_ai']['chuyen_tiep']),
                  ma_prompt=y['yeu_cau_ai']['ma_prompt'], phien_ban_prompt=y['yeu_cau_ai']['phien_ban_prompt'],
                  bam_dau_vao=bam_bytes(json_chuan(y)))
        ds.append(dict(tra_loi_ai=dict(loai='tra_loi_ai', tra_loi_ai=ai),
                       nguon=dict(engine='e_hoi_ai', nang_luc='ai.hoi_mask_cuc_bo@1', nha_cung_cap='local',
                                  model='model-demo', trang_thai='XONG',
                                  hoan_tat=dict(giao_thuc='openai_compatible', ket_thuc='stop'))))
    bundle = sua(dict(phien_ban=1, ma_yeu_cau=b.ctx.ma_yeu_cau, phan_hoi=ds))
    raw = json_chuan(bundle)
    dau_vao = deepcopy(bundle['phan_hoi'][-1]['tra_loi_ai'])
    b.v = b.c.giao_viec(NANG_LUC, dau_vao)
    ctx = b.q.cap(b.v, ma_yeu_cau=b.ctx.ma_yeu_cau)
    dau = b.ram._ban_ghi.du_lieu['dau_ho_so_ai']
    chung = [dict(chi_so_doan=i, bam_yeu_cau=bam_bytes(json_chuan(b.cong.giao[i])),
                  bam_phan_hoi=bam_bytes(json_chuan(p['tra_loi_ai'])), nguon=p['nguon'])
             for i, p in enumerate(bundle['phan_hoi'])]
    danh_tinh = dict(ma_yeu_cau=ctx.ma_yeu_cau, phien=ctx.phien, module=ctx.module,
                     nguoi_gui=ctx.nguoi_gui, tai_lieu=ctx.tai_lieu, vung=ctx.vung, phap_nhan_id='pn-demo')
    b.cong.nguon = json_chuan(dict(phien_ban=1, danh_tinh=danh_tinh,
        ma_ho_so_ram=dau.ma_ho_so_ram, bam_ho_so=dau.bam_ho_so,
        bam_tap_phan_hoi=bam_bytes(raw), bam_dau_vao=bam_bytes(json_chuan(dau_vao)), phan_hoi=chung))
    b.cong.raw, b.bundle, b.dau_vao = raw, bundle, dau_vao
    return b
