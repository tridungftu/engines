"""CoreGia chứng thực nguồn AI-9 giả, ngoài gói; chỉ DEMO, không model thật."""
from copy import deepcopy
from dataclasses import asdict
import json
from types import SimpleNamespace

from kho_tri_thuc_sdk.thu import CoreGia

from e_mask import chuan_bi_ai as cb
from e_mask.chay import tao_app
from e_mask.hau_kiem_ai import NANG_LUC
from e_mask.ho_so_ai import DauHoSoAI, ThamChieuHoSo, bam_bytes, json_chuan
from e_mask.kho_ngan import KHAI_NGAN
from e_mask.ngan import NganBoNho
from ho_tro_chuan_bi_ai import CongChuanBiCoreGia
from ho_tro_ngan import QuyenNganDemo, ai_demo, viec_demo


class CongHauKiemCoreGia(CongChuanBiCoreGia):
    def __init__(self, core):
        super().__init__(core)
        self.nguon, self.chung_cu = {}, {}
        self.so_chung_thuc, self.so_ban_giao = 0, 0
        self.moc = lambda ten, v: None

    def chung_thuc(self, viec, ctx, *, de_nghi):
        self._quyen(viec, ctx)
        self.so_chung_thuc += 1
        self.moc('chung_thuc', viec)
        v = json.loads(de_nghi)
        return self.nguon.get(self.chu(viec, ctx)) == de_nghi and v['danh_tinh']['phap_nhan_id'] == viec.ngu_canh['phap_nhan_id']

    def ban_giao(self, viec, ctx, *, chung_cu=None, ket_qua=None, dau=None, yeu_cau=None):
        if dau is not None:
            return super().ban_giao(viec, ctx, dau=dau, yeu_cau=yeu_cau)
        self._quyen(viec, ctx)
        self.so_ban_giao += 1
        khoa = self.chu(viec, ctx)
        v = json.loads(chung_cu)
        if (v['bam_ket_qua'] != bam_bytes(ket_qua)
                or v['bam_nguon'] != bam_bytes(self.nguon[khoa])
                or v['nang_luc'] != NANG_LUC):
            return False
        cu = self.chung_cu.setdefault(khoa, (chung_cu, ket_qua))
        self.moc('ban_giao', viec)
        return cu == (chung_cu, ket_qua)


def bo(chu='mạc đĩnh chi; nội dung DEMO; 1.000.000 VND ngày 30/10/2026.'):
    n = NganBoNho([*KHAI_NGAN, *cb.KHAI_NGAN_CHUAN_BI_AI])
    c, q = CoreGia(), QuyenNganDemo()
    cong = CongHauKiemCoreGia(c)
    app = tao_app(ngan=n, quyen=q, cong_chuan_bi_ai=cong, cong_hau_kiem_ai=cong)
    v = c.giao_viec(cb.NANG_LUC, {'loai': 'van_ban', 'van_ban': chu})
    ctx = q.cap(v)
    cong.cap(viec_demo(v), ctx)
    c.chay(app)
    k = c.xem(v)
    assert k['trang_thai'] == 'XONG', k
    meta = k['ket_qua']['yeu_cau_ai']['chuyen_tiep']['mask_2c']
    raw = c.doc_tep(meta['ho_so']['tep_id'])
    s = cb.doc_snapshot(raw)
    dau = DauHoSoAI(ThamChieuHoSo(**meta['ho_so']), bam_bytes(raw))
    ys = [cb.yeu_cau_cho_doan(s, dau, i) for i in range(len(s['quy_tac']['ke_hoach']))]
    return SimpleNamespace(n=n, c=c, q=q, cong=cong, app=app, chu=chu, s=s, dau=dau,
                           ys=ys, ctx=ctx, truoc=k, v_chuan_bi=v)


def thuc_the(b, a, z, loai='nguoi', muc='chac'):
    return dict(loai=loai, nguyen_van=b.chu[a:z], bat_dau=a, ket_thuc=z, muc=muc)


def tap_phan_hoi(b, ts=()):
    ds = []
    for y in b.ys:
        v = y['yeu_cau_ai']
        m = v['chuyen_tiep']['mask_2c']
        cac = []
        for t in ts:
            if m['bat_dau_doan'] <= t['bat_dau'] < t['ket_thuc'] <= m['ket_thuc_doan']:
                t = deepcopy(t)
                t['bat_dau'] -= m['bat_dau_doan']
                t['ket_thuc'] -= m['bat_dau_doan']
                cac.append(t)
        ai = ai_demo('Không thấy căn cứ.', b.ctx.ma_yeu_cau)
        ai.update(du_lieu=dict(da_quet_het=True, thuc_the=cac),
                  trang_thai='co_can_cu' if cac else 'khong_thay_can_cu',
                  trich_dan=[dict(cau=t['nguyen_van'], bat_dau=t['bat_dau'], ket_thuc=t['ket_thuc']) for t in cac],
                  chuyen_tiep=deepcopy(v['chuyen_tiep']), ma_prompt=v['ma_prompt'],
                  phien_ban_prompt=v['phien_ban_prompt'], bam_dau_vao=bam_bytes(json_chuan(y)))
        nguon = dict(engine='e_hoi_ai', nang_luc='ai.hoi_mask_cuc_bo@1', nha_cung_cap='local',
                     model='model-demo', trang_thai='XONG',
                     hoan_tat=dict(giao_thuc='openai_compatible', ket_thuc='stop'))
        ds.append(dict(yeu_cau_ai=deepcopy(y), tra_loi_ai={'loai': 'tra_loi_ai', 'tra_loi_ai': ai}, nguon=nguon))
    return dict(phien_ban=1, ma_yeu_cau=b.ctx.ma_yeu_cau,
                ke_hoach=deepcopy(b.s['quy_tac']['ke_hoach']), phan_hoi=ds)


def giao(b, bundle, *, nguon_that=True, raw=None):
    raw = json_chuan(bundle) if raw is None else raw
    ref = ThamChieuHoSo(**b.c.them_tep('mask-2c-phan-hoi.json', raw, 'application/json'))
    dau_vao = deepcopy(bundle['phan_hoi'][-1]['tra_loi_ai'])
    dau_vao['tra_loi_ai']['chuyen_tiep']['mask_2c'].update(
        tap_phan_hoi=asdict(ref), bam_tap_phan_hoi=bam_bytes(raw))
    v = b.c.giao_viec(NANG_LUC, dau_vao)
    ctx = b.q.cap(v, ma_yeu_cau=b.ctx.ma_yeu_cau)
    vd = viec_demo(v)
    b.cong.cap(vd, ctx)
    b.cong._chu[ref.tep_id] = b.cong.chu(vd, ctx)
    b.cong._tham_chieu[ref.tep_id] = ref
    # Sổ chứng thực giả được ghi lúc Core nhận nguồn, trước khi caller sửa.
    de_nghi = dict(phien_ban=1, danh_tinh=dict(
        ma_yeu_cau=ctx.ma_yeu_cau, phien=ctx.phien, module=ctx.module, nguoi_gui=ctx.nguoi_gui,
        tai_lieu=ctx.tai_lieu, vung=ctx.vung, phap_nhan_id='pn-demo'),
        ho_so=asdict(b.dau.ho_so), bam_ho_so=b.dau.bam_ho_so, tap_phan_hoi=asdict(ref),
        bam_tap_phan_hoi=bam_bytes(raw), bam_dau_vao=bam_bytes(json_chuan(dau_vao)),
        phan_hoi=[dict(chi_so_doan=i, bam_yeu_cau=bam_bytes(json_chuan(p['yeu_cau_ai'])),
                      bam_phan_hoi=bam_bytes(json_chuan(p['tra_loi_ai'])), nguon=p['nguon'])
                  for i, p in enumerate(bundle['phan_hoi'])])
    if nguon_that:
        b.cong.nguon[b.cong.chu(vd, ctx)] = json_chuan(de_nghi)
    b.v, b.dau_vao, b.bundle, b.ref = v, dau_vao, bundle, ref
    return b


def chay(b):
    b.c.chay(b.app)
    return b.c.xem(b.v)
