"""CoreGia SDK 2.2.0 + RAM R4; không mô phỏng kho snapshot cũ.

Catalogue DEMO được cấp trước chuỗi, chỉ để kiểm alias đã duyệt. Không
dùng gold làm detector; tên mới thiếu C-P4-03 vẫn bị runtime chặn.
"""
from copy import deepcopy
import json
from types import SimpleNamespace

from kho_tri_thuc_sdk.thu import CoreGia

from e_mask import che_van_ban as che, chuan_bi_ai as cb, tai_nguyen
from e_mask.chay import tao_app
from e_mask.hau_kiem_ai import NANG_LUC
from e_mask.ho_so_ai import bam_bytes, json_chuan
from e_mask.kho_anh_xa_ram import KhoAnhXaRAM
from ho_tro_chuan_bi_ai import CongChuanBiCoreGia
from ho_tro_mask_r5 import noi_handler
from ho_tro_ngan import QuyenNganDemo, ai_demo, viec_demo
from ho_tro_ram import DongHoGia


# Catalogue hồi quy đã khai độc lập với gold/response Local. Không phải
# chứng nhận dữ liệu đã duyệt trên Core thật hoặc chất lượng detector.
CATALOGUE = ('mạc đĩnh chi', 'mạc đĩnh', 'lương thế vinh', 'từ minh tâm',
             'văn tiến dũng', 'orvella mivanta', 'orvella linero', 'ánh veloria',
             'norella finero', 'nội dung')
CATALOGUE_QUY_TAC = (('tran bao long', 'CA_NHAN', '[[MASKCN-QT-0001]]'),
                    ('Nguyễn Văn An', 'CA_NHAN', '[[MASKCN-QT-0002]]'),
                    ('DEMO', 'CONG_TY', '[[MASKCT-QT-0003]]'))


class CongHauKiemCoreGia(CongChuanBiCoreGia):
    def __init__(self, core=None):
        super().__init__(core)
        self.nguon, self.chung_cu = {}, {}
        self.so_chung_thuc, self.so_ban_giao = 0, 0

    def nhan_phan_hoi(self, viec, ctx, **kw):
        self._quyen(viec, ctx)
        self.moc('nhan_phan_hoi', viec)
        return self.raw

    def chung_thuc(self, viec, ctx, *, de_nghi):
        self._quyen(viec, ctx)
        self.so_chung_thuc += 1
        self.moc('chung_thuc', viec)
        v = json.loads(de_nghi)
        return (self.nguon.get(self.chu(viec, ctx)) == de_nghi
                and v['danh_tinh']['phap_nhan_id'] == viec.ngu_canh['phap_nhan_id'])

    def ban_giao(self, viec, ctx, *, chung_cu=None, ket_qua=None, **kw):
        if chung_cu is None:
            return super().ban_giao(viec, ctx, **kw)
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


class QuanSatNgan:
    """Đọc bản chiếu null+cờ CoreGia, kể cả bảng lịch sử phải rỗng."""
    def __init__(self, core):
        self.core = core
        self.anh = {}

    def tim(self, bang, **_):
        if bang in {'dinh_danh', 'bi_danh', 'dau_gap', 'ma_yeu_cau'}:
            return deepcopy(self.anh.get(bang, SimpleNamespace(danh_sach=[], tiep=None)))
        return SimpleNamespace(danh_sach=[SimpleNamespace(gia_tri=r)
            for r in self.core.xem_ngan('e_mask', bang)], tiep=None)




def tao_bo(chu, *, dau=None, cong=None, seeds=()):
    q, dh = QuyenNganDemo(), DongHoGia()
    cong = cong or CongHauKiemCoreGia()
    app = tao_app(quyen=q, cong_chuan_bi_ai=cong, cong_hau_kiem_ai=cong)
    app.kho_anh_xa_ram = ram = KhoAnhXaRAM(quyen=q, dong_ho=dh, hen_gio=dh.hen_gio)
    # Một giá trị chuẩn hóa chỉ có một hàng. Không dùng null để ghép tên.
    danh_muc = {}
    for ten, nhom, alias in [*CATALOGUE_QUY_TAC, *seeds]:
        if che.chuan_hoa(ten) in che.chuan_hoa(chu):
            danh_muc[che.chuan_hoa(ten)] = (ten, nhom, alias)
    noi_handler(app, q, cong, seeds=list(danh_muc.values()))
    c = CoreGia(app)
    cong.core = c
    v = c.giao_viec(cb.NANG_LUC, dau or {'loai': 'van_ban', 'van_ban': chu})
    ctx = q.cap(v)
    cong.cap(viec_demo(v), ctx)
    quan_sat = QuanSatNgan(c)
    ham = app._ham[cb.NANG_LUC]
    def ghi_nhan_cua(viec):
        ket = ham(viec)
        for bang in ('dinh_danh', 'bi_danh'):
            quan_sat.anh[bang] = viec.ngan.tim(bang)
        return ket
    app._ham[cb.NANG_LUC] = ghi_nhan_cua
    # Catalogue đầu vào của fixture chấm DEMO, không phải map của runtime.
    quan_sat.danh_muc_demo = tuple(danh_muc.values())
    return SimpleNamespace(n=quan_sat, c=c, q=q, cong=cong, app=app,
                           v=v, ctx=ctx, chu=chu, ram=ram, dh=dh)


def ho_so_ram(b):
    v = b.ram._ban_ghi.du_lieu
    return deepcopy(v['ho_so_ai']), v['dau_ho_so_ai']


def chay(b):
    b.c.chay(b.app)
    return b.c.xem(b.v)


def chuan_bi_cac_doan(b):
    k = chay(b)
    assert k['trang_thai'] == 'XONG', k
    s, dau = ho_so_ram(b)
    n = len(s['quy_tac']['ke_hoach'])
    b.v_chuan_bi = b.v
    for i in range(1, n):
        b.cong.i = i
        b.v = b.c.giao_viec(cb.NANG_LUC, {'loai': 'van_ban', 'van_ban': b.chu})
        ctx = b.q.cap(b.v, ma_yeu_cau=b.ctx.ma_yeu_cau)
        b.cong.cap(viec_demo(b.v), ctx)
        assert chay(b)['trang_thai'] == 'XONG'
    b.s, b.dau, b.truoc = s, dau, k
    b.ys = [deepcopy(b.cong.giao[i]) for i in range(n)]
    return b


def bo(chu='mạc đĩnh chi đang ký; nội dung DEMO; 1.000.000 VND ngày 30/10/2026.', *, seeds=None):
    if seeds is None:
        seeds = [(ten, 'CA_NHAN', '[[MASKCN-DEMO-%04d]]' % i)
                 for i, ten in enumerate(CATALOGUE, 1) if che.chuan_hoa(ten) in che.chuan_hoa(chu)]
    return chuan_bi_cac_doan(tao_bo(chu, seeds=seeds))


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
                     model=v['model_uu_tien'], trang_thai='XONG',
                     hoan_tat=dict(giao_thuc='openai_compatible', ket_thuc='stop'))
        ds.append(dict(tra_loi_ai={'loai': 'tra_loi_ai', 'tra_loi_ai': ai}, nguon=nguon))
    return dict(phien_ban=1, ma_yeu_cau=b.ctx.ma_yeu_cau, phan_hoi=ds)


def giao(b, bundle, *, nguon_that=True, raw=None):
    raw = json_chuan(bundle) if raw is None else raw
    dau_vao = deepcopy(bundle['phan_hoi'][-1]['tra_loi_ai'])
    v = b.c.giao_viec(NANG_LUC, dau_vao)
    ctx = b.q.cap(v, ma_yeu_cau=b.ctx.ma_yeu_cau)
    vd = viec_demo(v)
    b.cong.cap(vd, ctx)
    de_nghi = dict(phien_ban=1, danh_tinh=dict(
        ma_yeu_cau=ctx.ma_yeu_cau, phien=ctx.phien, module=ctx.module, nguoi_gui=ctx.nguoi_gui,
        tai_lieu=ctx.tai_lieu, vung=ctx.vung, phap_nhan_id='pn-demo'),
        ma_ho_so_ram=b.dau.ma_ho_so_ram, bam_ho_so=b.dau.bam_ho_so,
        bam_tap_phan_hoi=bam_bytes(raw), bam_dau_vao=bam_bytes(json_chuan(dau_vao)),
        phan_hoi=[dict(chi_so_doan=i, bam_yeu_cau=bam_bytes(json_chuan(b.ys[i])),
                      bam_phan_hoi=bam_bytes(json_chuan(p['tra_loi_ai'])), nguon=p['nguon'])
                  for i, p in enumerate(bundle['phan_hoi'])])
    if nguon_that:
        b.cong.nguon[b.cong.chu(vd, ctx)] = json_chuan(de_nghi)
    b.cong.raw = raw
    b.v, b.dau_vao, b.bundle = v, dau_vao, bundle
    return b
