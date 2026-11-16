"""C-P4-04/05 giả ngoài gói, chỉ DEMO, không gọi Hỏi AI/model/Cloud."""
from copy import deepcopy
from contextlib import contextmanager
import json
from types import SimpleNamespace

from kho_tri_thuc_sdk.thu import CoreGia
from kho_tri_thuc_sdk.engine import LoiNghiepVu

from e_mask.chay import tao_app
from e_mask.chuan_bi_tep import yeu_cau
from e_mask.ho_so_ai import bam_bytes, json_chuan
from e_mask.ho_so_tep import CHUAN_BI, VAN_BAN, GIU_DINH_DANG, MIME
from e_mask.kho_anh_xa_ram import KhoAnhXaRAM
from ho_tro_mask_b5 import TEN, ALIAS, word
from ho_tro_mask_b6 import excel
from ho_tro_mask_r5 import CongRAMCoreGia
from ho_tro_ngan import QuyenNganDemo, ai_demo
from ho_tro_ram import DongHoGia
from test_mask_r2 import _dong, _them


class CongTepCoreGia(CongRAMCoreGia):
    def __init__(self, *, dang='van_ban'):
        super().__init__()
        self.dang, self.tep_hop_le = dang, True
        self.chot, self.dem_chot, self.giao_cuoi = {}, 0, []
        self.core, self.ref_nguon = None, None

    def dang_tra(self, v, ctx):
        self.moc('dang_tra', v)
        return self.dang

    def kiem_tep(self, v, ctx, **kw):
        self.cac_cua.append(('kiem_tep', deepcopy(kw)))
        self.moc('kiem_tep', v)
        self.ref_nguon = kw['tham_chieu']
        return self.tep_hop_le and bam_bytes(self.core.doc_tep(self.ref_nguon['tep_id'])) == kw['bam_tep']

    def kiem_nguon_tep(self, v, ctx, **kw):
        self.cac_cua.append(('kiem_nguon_tep', deepcopy(kw)))
        self.moc('kiem_nguon_tep', v)
        return self.tep_hop_le and bam_bytes(self.core.doc_tep(self.ref_nguon['tep_id'])) == kw['bam_tep']

    def chot_metadata(self, v, ctx, *, chung_cu, metadata, ghi):
        self.cac_cua.append(('chot_metadata', dict(chung_cu=chung_cu, metadata=metadata)))
        self.moc('truoc_chot', v)
        dau = (chung_cu, metadata)
        if ctx.ma_yeu_cau in self.chot:
            return self.chot[ctx.ma_yeu_cau] == dau
        ds = json.loads(metadata)
        assert len(ds) <= 100
        # B9: Core giả chỉ giữ quyền/dấu chống lặp; chính runtime gửi một
        # lô qua viec.ngan thật của SDK. Adapter không tự sửa kho thay engine.
        assert ghi() is True
        self.chot[ctx.ma_yeu_cau] = dau
        self.dem_chot += 1
        self.moc('chot_metadata', v)
        return True

    @contextmanager
    def ban_giao_tep_cuoi(self, v, ctx, *, chung_cu, han_monotonic):
        self.moc('vao_cach_ly', v)
        pending = None
        def kiem():
            self.q.xac_minh(v, loai='che', ma_yeu_cau=ctx.ma_yeu_cau, thao_tac='tep_ai')
            v.kiem_huy()
            if self.dh() >= han_monotonic:
                raise LoiNghiepVu('MASK_ANH_XA_KHONG_CON', 'Hết hạn DEMO.')
        def nhan(raw):
            nonlocal pending
            kiem()
            pending = raw
            return self.ban_giao(v, ctx, chung_cu=chung_cu, ket_qua=raw)
        kiem()
        try:
            yield nhan
            self.moc('ra_cach_ly', v)
            kiem()
            assert pending is not None
        finally:
            pending = None

    def ban_giao(self, v, ctx, **kw):
        if 'yeu_cau' in kw:
            return super().ban_giao(v, ctx, **kw)
        self.cac_cua.append(('ban_giao_cuoi', deepcopy(kw)))
        self.giao_cuoi.append(deepcopy(kw))
        self.moc('ban_giao_cuoi', v)
        return True


class CoreTepGia(CoreGia):
    """Cấp rõ quyền tệp con xuyên bước; SDK CoreGia chuẩn chưa có cửa này."""
    def __init__(self, app):
        super().__init__(app)
        self.tep_con = {}

    def _mo_tep(self, ma, viec_id, tep_id, toi_da_byte):
        if tep_id not in self.tep_con.get(viec_id, ()):
            return super()._mo_tep(ma, viec_id, tep_id, toi_da_byte)
        with self._lock:
            self._dang_giu(ma, viec_id)
            du = self.doc_tep(tep_id)
            if len(du) > toi_da_byte:
                raise LoiNghiepVu('MASK_QUA_GIOI_HAN', 'Dữ liệu DEMO vượt trần.')
            return du


def bo(loai='docx', *, dang='van_ban', raw=None, seeds=((TEN, 'CONG_TY', ALIAS),), ttl=600, boc=False):
    q, cong, dh = QuyenNganDemo(), CongTepCoreGia(dang=dang), DongHoGia()
    app = tao_app(quyen=q, cong_chuan_bi_tep=cong, cong_hau_kiem_tep=cong)
    app.kho_anh_xa_ram = ram = KhoAnhXaRAM(quyen=q, dong_ho=dh, hen_gio=dh.hen_gio)
    c = CoreTepGia(app)
    cong.core, cong.q, cong.dh, cong.ram = c, q, dh, ram
    c.dat_cau_hinh('e_mask', {'thoi_han_anh_xa_giay': ttl})
    raw = (word() if loai == 'docx' else excel()) if raw is None else raw
    ref = c.them_tep('DEMO.' + loai, raw, MIME[loai])
    dau = dict(loai='tep', tep=ref)
    if boc:
        j = c.them_tep('DEMO.json', json_chuan(dict(tep=ref, dinh_danh_da_biet=[])), 'application/json')
        dau = dict(loai='tep', tep=j)
    v = c.giao_viec(CHUAN_BI, dau)
    if boc:
        c.tep_con[v] = {ref['tep_id']}
    ctx = q.cap(v)
    cb = app._ham[CHUAN_BI]
    con_seed = list(seeds)
    def nap(viec):
        for ten, nhom, alias in con_seed:
            dong = _dong(ten, trang_thai='CHINH_THUC')
            dong['nhom'] = nhom
            _them(viec, dong, alias)
        con_seed.clear()
        return cb(viec)
    app._ham[CHUAN_BI] = nap
    return SimpleNamespace(q=q, cong=cong, dh=dh, app=app, ram=ram, c=c, v=v,
                           ctx=ctx, ref=ref, dau=dau, raw=raw, loai=loai)


def chay(b):
    b.c.chay(b.app)
    return b.c.xem(b.v)


def chuan_bi(b):
    k = chay(b)
    assert k['trang_thai'] == 'XONG', k
    return k


def chuan_bi_het(b):
    k = chuan_bi(b)
    n = k['ket_qua']['yeu_cau_ai']['chuyen_tiep']['mask_2c']['so_doan']
    for i in range(1, n):
        b.cong.i = i
        b.v = b.c.giao_viec(CHUAN_BI, b.dau)
        b.q.cap(b.v, ma_yeu_cau=b.ctx.ma_yeu_cau)
        chuan_bi(b)
    return k


def giao(b, *, spans=None, sua=lambda v: v, nang_luc=None):
    h = b.ram._ban_ghi.du_lieu['ho_so_tep']
    goc = h['map_quy_tac'].goc
    if spans is None:
        spans = [(p.goc[0], p.goc[1], 'to_chuc', 'chac')
                 for p in h['map_quy_tac'].goc_che if p.loai == 'thay_bi_danh']
    ds = []
    for i, y in sorted(b.cong.giao.items()):
        d = h['ke_hoach'][i]
        cac = [dict(loai=l, muc=m, nguyen_van=goc[a:z], bat_dau=a-d.bat_dau, ket_thuc=z-d.bat_dau)
               for a, z, l, m in spans if d.bat_dau <= a < z <= d.ket_thuc]
        ai = ai_demo('Không thấy căn cứ.', b.ctx.ma_yeu_cau)
        ai.update(du_lieu=dict(da_quet_het=True, thuc_the=cac),
            trang_thai='co_can_cu' if cac else 'khong_thay_can_cu',
            trich_dan=[dict(cau=t['nguyen_van'], bat_dau=t['bat_dau'], ket_thuc=t['ket_thuc']) for t in cac],
            chuyen_tiep=deepcopy(y['yeu_cau_ai']['chuyen_tiep']),
            ma_prompt=y['yeu_cau_ai']['ma_prompt'], phien_ban_prompt=y['yeu_cau_ai']['phien_ban_prompt'],
            bam_dau_vao=bam_bytes(json_chuan(y)))
        ds.append(dict(tra_loi_ai=dict(loai='tra_loi_ai', tra_loi_ai=ai),
            nguon=dict(engine='e_hoi_ai', nang_luc='ai.hoi_mask_cuc_bo@1', nha_cung_cap='local',
                       model='model-demo', trang_thai='XONG', hoan_tat=dict(giao_thuc='openai_compatible', ket_thuc='stop'))))
    bundle = sua(dict(phien_ban=1, ma_yeu_cau=b.ctx.ma_yeu_cau, phan_hoi=ds))
    raw = json_chuan(bundle)
    dau_vao = deepcopy(ds[-1]['tra_loi_ai'])
    b.v = b.c.giao_viec(nang_luc or h['nang_luc_cuoi'], dau_vao)
    b.q.cap(b.v, ma_yeu_cau=b.ctx.ma_yeu_cau)
    chung = [dict(chi_so_doan=i, bam_yeu_cau=bam_bytes(json_chuan(yeu_cau(h, b.ctx.ma_yeu_cau, i % len(h['ke_hoach'])))),
        bam_phan_hoi=bam_bytes(json_chuan(p['tra_loi_ai'])), nguon=p['nguon']) for i, p in enumerate(bundle['phan_hoi'])]
    b.cong.nguon = json_chuan(dict(phien_ban=1, ma_yeu_cau=b.ctx.ma_yeu_cau,
        ma_ho_so_ram=h['dau'].ma_ho_so_ram, bam_ho_so=h['dau'].bam_ho_so,
        bam_tap_phan_hoi=bam_bytes(raw), bam_dau_vao=bam_bytes(json_chuan(dau_vao)), phan_hoi=chung))
    b.cong.raw, b.bundle = raw, bundle
    return b
