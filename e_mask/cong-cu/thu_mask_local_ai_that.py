"""Đo DEMO ngoài gói bằng CoreGia; mặc định khô, không dò/gọi mạng.

CoreGia và biên nhận budget/tokenizer là fixture, không chứng nhận Core thật.
AI-9 vẫn kiểm IP/model/context/hoàn tất bằng transport nguyên bản. Gold chỉ
được đọc bởi bộ chấm, tuyệt đối không gửi model hoặc dùng làm detector.
"""
from argparse import ArgumentParser
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import math
import re
import sys
import time
from types import SimpleNamespace
import unicodedata

sys.dont_write_bytecode = True
GOC = Path(__file__).resolve().parents[2]
for thu in ('e_mask/goi/e_mask', 'e_hoi_ai/goi/e_hoi_ai', 'e_mask/tests'):
    sys.path.insert(0, str(GOC / thu))

from kho_tri_thuc_sdk.thu import CoreGia
from kho_tri_thuc_sdk.engine import LoiNghiepVu
import kho_tri_thuc_sdk
from e_mask import chuan_bi_ai as cb
from e_mask.chay import tao_app
from e_mask.ho_so_ai import DauHoSoAI, ThamChieuHoSo, bam_bytes, json_chuan
from e_mask.kho_ngan import KHAI_NGAN
from e_mask.ngan import NganBoNho
from ho_tro_hau_kiem_ai import CongHauKiemCoreGia, giao, chay
from ho_tro_ngan import QuyenNganDemo, viec_demo

BO_DEMO = Path(__file__).with_name('mask_2c_4_ung_vien_demo.json')
PROMPT = 'Quy trình đo DEMO MASK-2c-4.\n' + cb.CHI_DAN_BAT_BUOC
MA_PROMPT, PHIEN_PROMPT = 'demo.mask_2c_4', 'DEMO-1'
ALIAS = re.compile(r'\[\[[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\]\]')
CHAN_NGHIEP_VU = {'MASK_DINH_DANH_CHUA_DAT', 'MASK_AI_CON_SOT'}
MA_KY_THUAT = {'AI_TRA_SAI_KHUON', 'LOCAL_AI_KHONG_SAN_SANG', 'MASK_AI_SPAN_KHONG_HOP_LE',
               'MASK_AI_NGUON', 'MASK_AI_HO_SO', 'MASK_AI_CHUA_DAT', 'MASK_AI_CHUA_CO_CUA_CORE',
               'MASK_AI_NGAN_SACH', 'MASK_AI_QUA_GIOI_HAN', 'MASK_AI_PROFILE_KHONG_HOP_LE',
               'VUOT_GIOI_HAN', 'HET_HAN_CHUOI', 'SAI_MODEL'}


def bam(v):
    return bam_bytes(json_chuan(v))


def doc_bo(tep=BO_DEMO):
    v = json.loads(Path(tep).read_text('utf-8'))
    if v['nhan'] != 'DEMO' or v['sha256_noi_dung'] != bam(v['noi_dung']):
        raise ValueError('Bộ DEMO sai nhãn hoặc băm.')
    for tap in v['noi_dung'].values():
        for ca in tap:
            if not ca['van_ban'] or ca['nhom'] not in {'nguoi', 'to_chuc', 'dia_chi', 'thuong', 'bien_the'}:
                raise ValueError('Ca DEMO không hợp lệ.')
            for t in ca['gold']:
                a, b = t['bat_dau'], t['ket_thuc']
                if not 0 <= a < b <= len(ca['van_ban']) or ca['van_ban'][a:b] != t['nguyen_van']:
                    raise ValueError('Gold DEMO sai offset.')
    return v


def vo_hinh(c):
    n = ord(c)
    return unicodedata.category(c) == 'Cf' or 0xFE00 <= n <= 0xFE0F or 0xE0100 <= n <= 0xE01EF


def chuan(chu):
    return ' '.join(unicodedata.normalize('NFC', ''.join(c for c in chu if not vo_hinh(c))).lower().split())


def khung(chu):
    return ''.join(c for c in unicodedata.normalize('NFD', chu.casefold().replace('đ', 'd'))
                   if c.isalnum() and not vo_hinh(c))


def map_doc_lap(goc, ra, ngan):
    """Đọc lại phép thay từ alias đã chốt + hai chuỗi, không dùng detector/map engine.

    Đi tuần tự từng ký tự giữ nguyên, từng alias phải khớp đúng giá trị đã
    chốt ở vị trí hiện tại. Ánh xạ không duy nhất hoặc không khớp -> lỗi đo.
    Không dùng gold để suy khoảng che; che prefix vẫn để lại phần gold hở.
    """
    gia_tri = {}
    for bang in ('dinh_danh', 'bi_danh_tam', 'cho_duyet'):
        tiep = None
        while True:
            trang = ngan.tim(bang, gioi_han=500, tiep=tiep)
            for ban in trang.danh_sach:
                v = ban.gia_tri
                if 'gia_tri' in v:
                    for k in ('bi_danh', 'bi_danh_tam'):
                        if isinstance(v.get(k), str):
                            gia_tri[v[k]] = chuan(v['gia_tri'])
            tiep = trang.tiep
            if tiep is None:
                break
    vi_tri = [i for i, c in enumerate(goc) if not vo_hinh(c)]
    sach = ''.join(goc[i] for i in vi_tri)
    i = j = 0
    phep = []
    while j < len(ra):
        m = ALIAS.match(ra, j)
        if m:
            dich = gia_tri.get(m.group())
            if dich is None:
                raise ValueError('Không xác minh được alias đo.')
            ung_vien = []
            lan = ALIAS.search(ra, m.end())
            duoi = ra[m.end():lan.start() if lan else len(ra)]
            for k in range(i + 1, min(len(sach), i + 300) + 1):
                if chuan(sach[i:k]) == dich and sach.startswith(duoi, k):
                    if duoi or lan or k == len(sach):
                        ung_vien.append(k)
            if len(ung_vien) != 1:
                raise ValueError('Ánh xạ đo không duy nhất.')
            k = ung_vien[0]
            phep.append((vi_tri[i - 1] + 1 if i else 0, vi_tri[k] if k < len(vi_tri) else len(goc)))
            i, j = k, m.end()
        else:
            if i >= len(sach) or sach[i] != ra[j]:
                raise ValueError('Văn bản đo không khớp phép thay.')
            i, j = i + 1, j + 1
    if i != len(sach):
        raise ValueError('Văn bản đo thiếu đuôi.')
    return phep


def cham(ca, kq, ngan):
    trang = kq['trang_thai']
    ma = (kq.get('loi') or {}).get('ma', '')
    ket = dict(trang_thai='loi_ky_thuat', so_span_lot=None, che_thua=None,
               ma_loi=ma if ma in MA_KY_THUAT | CHAN_NGHIEP_VU else 'LOI_KHAC' if ma else None)
    if trang == 'CHUA_RO':
        ket['trang_thai'] = 'chua_ro'
    elif trang != 'XONG':
        ket['trang_thai'] = 'chan_nghiep_vu' if ma in CHAN_NGHIEP_VU else 'loi_ky_thuat'
    else:
        ra = kq['ket_qua']['van_ban_da_che']['van_ban']
        try:
            phep = map_doc_lap(ca['van_ban'], ra, ngan)
        except ValueError:
            ket['ma_loi'] = 'MAP_DO_KHONG_KHOP'
            return ket
        # Che đủ span VÀ dò độc lập phần nhận diện còn lại; không chỉ tìm cả tên.
        so_lot = sum(not any(a <= t['bat_dau'] and t['ket_thuc'] <= b for a, b in phep)
                     or bool(khung(t['nguyen_van']) and khung(t['nguyen_van']) in khung(ALIAS.sub('', ra)))
                     for t in ca['gold'])
        ket.update(trang_thai='phat_hanh_con_lot' if so_lot else 'phat_hanh_che_du',
                   so_span_lot=so_lot, che_thua=not ca['gold'] and bool(phep))
    return ket


class CongDoCoreGia(CongHauKiemCoreGia):
    """Budget/deadline Core GIẢ; không nhận đây là token đo trên model thật."""
    def __init__(self, core, model, han_giay):
        super().__init__(core)
        self.cfg.update(ma_prompt=MA_PROMPT, phien_ban_prompt=PHIEN_PROMPT,
                        prompt=PROMPT, model_uu_tien=model)
        self.han_giay = han_giay
        self.bat_dau = time.monotonic()

    def kiem_ngan_sach(self, viec, ctx, *, de_nghi):
        v = super().kiem_ngan_sach(viec, ctx, de_nghi=de_nghi)
        # Không dùng hạn fixture 15/11 cho các lần Anh chạy sau ngày đó.
        from datetime import timedelta
        khoa = self.chu(viec, ctx)
        cu = self.ngan_sach[khoa]
        if not hasattr(self, '_han'):
            self._han = (datetime.now(timezone.utc) + timedelta(seconds=self.han_giay)).isoformat()
        cu['han_chuoi'] = self._han
        cu['han_local_giay'] = self.han_giay
        v.update(han_chuoi=cu['han_chuoi'], han_local_giay=cu['han_local_giay'])
        return v

    def kiem_han(self, viec, ctx, *, bien_nhan):
        self._quyen(viec, ctx)
        return (time.monotonic() - self.bat_dau < self.han_giay
                and bien_nhan == self.ngan_sach.get(self.chu(viec, ctx)))


def tao_bo(ca, model, han_giay):
    n, c, q = NganBoNho([*KHAI_NGAN, *cb.KHAI_NGAN_CHUAN_BI_AI]), CoreGia(), QuyenNganDemo()
    cong = CongDoCoreGia(c, model, han_giay)
    app = tao_app(ngan=n, quyen=q, cong_chuan_bi_ai=cong, cong_hau_kiem_ai=cong)
    return SimpleNamespace(n=n, c=c, q=q, cong=cong, app=app, chu=ca['van_ban'])


def chay_buoc(b, nang_luc):
    v = b.c.giao_viec(nang_luc, {'loai': 'van_ban', 'van_ban': b.chu})
    b.ctx = b.q.cap(v)
    b.cong.cap(viec_demo(v), b.ctx)
    b.c.chay(b.app)
    return b.c.xem(v)


class DemLocal:
    def __init__(self, provider, model):
        self.provider, self.model = provider, model
        self.so_luot, self.thoi_gian = 0, []

    def hoi(self, cau_hinh, model, *a, **kw):
        # Không cho phép chọn model khác khi ưu tiên mất giữa hai bước.
        if model != self.model:
            raise LoiNghiepVu('LOCAL_AI_KHONG_SAN_SANG', 'Model được chỉ định không khả dụng.')
        self.so_luot += 1
        t = time.perf_counter()
        try:
            return self.provider.hoi(cau_hinh, model, *a, **kw)
        finally:
            self.thoi_gian.append((time.perf_counter() - t) * 1000)


class DemCloud:
    def __init__(self):
        self.so_luot = 0

    def hoi(self, *a, **kw):
        self.so_luot += 1
        raise RuntimeError('Công cụ chỉ cho phép Local.')


def ai_ram(url, model, timeout):
    from e_hoi_ai import chay as ai
    from e_hoi_ai.ngan_engine import tao_ngan_bo_nho
    from e_hoi_ai.cong_ai import CongAI
    from e_hoi_ai.nha_cung_cap import NhaCungCapLocal
    ngan = tao_ngan_bo_nho()
    with ngan.lo() as lo:
        lo.them('cau_hinh', {}, {'local_ai': {'url': url, 'timeout_giay': timeout},
                                'quy_tac_model': [{'mau_ma_prompt': MA_PROMPT,
                                                   'uu_tien': model, 'du_phong': []}]})
    local, cloud = DemLocal(NhaCungCapLocal(), model), DemCloud()
    cu = ai.app.ngan, ai.bo_hoi.cong_ai
    ai.app.ngan = ngan
    ai.bo_hoi.cong_ai = CongAI(nha_cung_cap={'local': local, 'cloud': cloud})
    return ai, local, cloud, cu


def hai_lop(b, ai, model):
    truoc = chay_buoc(b, cb.NANG_LUC)
    thong_ke = dict(so_doan_ke_hoach=0, so_doan_ai_xong=0, du_doan=False)
    if truoc['trang_thai'] != 'XONG':
        return truoc, thong_ke
    meta = truoc['ket_qua']['yeu_cau_ai']['chuyen_tiep']['mask_2c']
    raw = b.c.doc_tep(meta['ho_so']['tep_id'])
    b.s = cb.doc_snapshot(raw)
    b.dau = DauHoSoAI(ThamChieuHoSo(**meta['ho_so']), bam_bytes(raw))
    b.ys = [cb.yeu_cau_cho_doan(b.s, b.dau, i) for i in range(len(b.s['quy_tac']['ke_hoach']))]
    thong_ke['so_doan_ke_hoach'] = len(b.ys)
    ds = []
    for y in b.ys:
        if time.monotonic() - b.cong.bat_dau >= b.cong.han_giay:
            return {'trang_thai': 'LOI', 'loi': {'ma': 'HET_HAN_CHUOI'}}, thong_ke
        kq = CoreGia().chay_thu(ai.app, 'ai.hoi_mask_cuc_bo@1', deepcopy(y))
        if kq['trang_thai'] != 'XONG':
            return kq, thong_ke
        thong_ke['so_doan_ai_xong'] += 1
        if kq['ket_qua']['tra_loi_ai']['model'] != model:
            return {'trang_thai': 'LOI', 'loi': {'ma': 'SAI_MODEL'}}, thong_ke
        ban_model = ai.app.ngan.doc('model_phat_hien', {'id_model': model})
        loai_api = ban_model.gia_tri['loai'] if ban_model else ''
        ds.append(dict(yeu_cau_ai=y, tra_loi_ai=kq['ket_qua'], nguon=dict(
            engine='e_hoi_ai', nang_luc='ai.hoi_mask_cuc_bo@1', nha_cung_cap='local', model=model,
            trang_thai='XONG', hoan_tat=dict(giao_thuc='ollama' if loai_api == 'ollama' else 'openai_compatible',
                                           ket_thuc='stop'))))
    bundle = dict(phien_ban=1, ma_yeu_cau=b.ctx.ma_yeu_cau,
                  ke_hoach=deepcopy(b.s['quy_tac']['ke_hoach']), phan_hoi=ds)
    giao(b, bundle)
    ket = chay(b)
    thong_ke['du_doan'] = len(ds) == len(b.ys)
    return ket, thong_ke


def phan_vi(ds, p):
    if not ds:
        return None
    ds = sorted(ds)
    vi = (len(ds) - 1) * p
    a = int(vi)
    return round(ds[a] + (ds[min(a + 1, len(ds) - 1)] - ds[a]) * (vi - a), 3)


def tong_hop(rows):
    ket = {}
    for che_do in ('quy_tac', 'hai_lop'):
        ds = [r for r in rows if r['che_do'] == che_do]
        thuong = [r for r in ds if r['nhom'] == 'thuong']
        hop_le = [r for r in ds if r['trang_thai'] not in {'loi_ky_thuat', 'chua_ro'}]
        thuong_hop_le = [r for r in thuong if r in hop_le]
        nham = sum(r['trang_thai'] == 'chan_nghiep_vu' or r['che_thua'] is True for r in thuong)
        ket[che_do] = dict(
            tong_ca=len(ds), ca_hop_le=len(hop_le),
            trang_thai={s: sum(r['trang_thai'] == s for r in ds) for s in (
                'phat_hanh_che_du', 'phat_hanh_con_lot', 'chan_nghiep_vu', 'loi_ky_thuat', 'chua_ro')},
            so_ca_phat_hanh=sum(r['trang_thai'].startswith('phat_hanh') for r in ds),
            so_ca_lot=sum(r['trang_thai'] == 'phat_hanh_con_lot' for r in ds),
            so_span_gold=sum(r['so_span_gold'] for r in ds),
            so_span_lot=sum(r['so_span_lot'] or 0 for r in ds),
            so_span_gold_phat_hanh=sum(r['so_span_gold'] for r in ds if r['trang_thai'].startswith('phat_hanh')),
            so_span_che_du=sum(r['so_span_gold'] - (r['so_span_lot'] or 0) for r in ds
                              if r['trang_thai'].startswith('phat_hanh')),
            ma_loi={ma: sum(r['ma_loi'] == ma for r in ds) for ma in sorted(
                {r['ma_loi'] for r in ds if r['ma_loi']})},
            cau_thuong=dict(tu_so=nham, mau_so=len(thuong), so_ca_hop_le=len(thuong_hop_le),
                            ti_le=nham / len(thuong) if thuong else None,
                            ti_le_tren_ca_hop_le=nham / len(thuong_hop_le) if thuong_hop_le else None,
                            nguyen_ven=sum(r['trang_thai'] == 'phat_hanh_che_du' and not r['che_thua'] for r in thuong)),
            so_doan_ke_hoach=sum(r['so_doan_ke_hoach'] for r in ds),
            so_doan_ai_xong=sum(r['so_doan_ai_xong'] for r in ds),
            so_ca_co_ke_hoach=sum(r['so_doan_ke_hoach'] > 0 for r in ds),
            so_ca_ai_du_doan=sum(r.get('du_doan', False) for r in ds),
            p50_ms=phan_vi([r['thoi_gian_ms'] for r in ds], .5),
            p95_ms=phan_vi([r['thoi_gian_ms'] for r in ds], .95))
        ket[che_do]['theo_nhom'] = {g: {s: sum(r['nhom'] == g and r['trang_thai'] == s for r in ds)
            for s in ket[che_do]['trang_thai']} for g in ('nguoi', 'to_chuc', 'dia_chi', 'thuong', 'bien_the')}
    return ket


def do(bo, *, that=False, url=None, model=None, timeout=120, tap='ung_vien'):
    ca = bo['noi_dung'][tap]
    ket = dict(nhan='DEMO', trang_thai_local='CHƯA ĐO Local thật', core='CoreGia',
               canh_bao='CoreGia không chứng nhận cửa Core thật; nợ CAO còn mở, Cloud giữ tắt.',
               held_out_doc_lap=False, tinh_trang_gold=bo['tinh_trang_gold'],
               bam_bo=bo['sha256_noi_dung'], tap=tap, so_ca=len(ca),
               so_ten_co_so=sum(c['nhom'] == 'nguoi' for c in ca),
               so_span_gold=sum(len(c['gold']) for c in ca),
               bam_model=bam(model) if model else None,
               model=model if model and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}', model) else None,
               prompt=dict(ma=MA_PROMPT, phien_ban=PHIEN_PROMPT, bam=bam_bytes(PROMPT.encode())),
               bam_khuon=bam(cb.khuon_tra_loi()), bam_profile=bam(cb.profile()),
               profile=cb.profile(), phien_ban_sdk='2.0.0',
               phien_ban_mask=tao_app().phieu['phien_ban'],
               budget_core='Fixture CoreGia; token chưa đo, AI-9 kiểm context/byte bảo thủ nguyên bản.',
               so_luot_cloud=0, so_luot_local=0, ket_qua=None)
    ket.update(phien_ban_sdk=kho_tri_thuc_sdk.__version__, phien_ban_cong_cu='MASK-2c-4-1',
               bam_cong_cu=bam_bytes(Path(__file__).read_bytes()),
               bam_cau_hinh_khong_url=bam(dict(model=model, timeout_giay=timeout, profile=cb.profile())),
               thoi_diem_utc=datetime.now(timezone.utc).isoformat(),
               dinh_nghia_luot_local='Số gọi provider Local, kể cả lỗi trước POST; số đoạn AI xong báo riêng.',
               so_timeout_xac_dinh=None,
               ghi_chu_timeout='AI-9 gom timeout/mất phản hồi/202 vào ChuaRo; không suy số timeout bằng 0.',
               gioi_han_ket_luan='AI chỉ cứu khi báo đủ; báo thiếu một phần tên thì phần còn lại có thể lọt.')
    # Khô chỉ kiểm bộ/băm/cấu trúc. Không có số đo detector hoặc Local giả.
    if not that:
        return ket
    if not url or not model:
        raise ValueError('Chạy thật cần đủ URL và model.')
    ai, local, cloud, cu = ai_ram(url, model, timeout)
    ket['phien_ban_hoi_ai'] = ai.app.phieu['phien_ban']
    rows = []
    try:
        for c in ca:
            for che_do in ('quy_tac', 'hai_lop'):
                b = tao_bo(c, model, max(1, math.ceil(timeout)))
                start = time.perf_counter()
                thong_ke = dict(so_doan_ke_hoach=0, so_doan_ai_xong=0, du_doan=False)
                if che_do == 'quy_tac':
                    kq = chay_buoc(b, 'mask.che_van_ban@1')
                else:
                    kq, thong_ke = hai_lop(b, ai, model)
                row = cham(c, kq, b.n)
                # Chỉ mã ca cố định/đếm/băm/thời gian; không phản chiếu lỗi/provider.
                row.update(ca=c['ma'], nhom=c['nhom'], che_do=che_do, so_span_gold=len(c['gold']),
                           thoi_gian_ms=round((time.perf_counter() - start) * 1000, 3), **thong_ke)
                rows.append(row)
        ket.update(trang_thai_local='ĐÃ THỬ Local qua CoreGia; chưa nghiệm thu độc lập',
                   so_luot_cloud=cloud.so_luot, so_luot_local=local.so_luot,
                   local_p50_ms=phan_vi(local.thoi_gian, .5), local_p95_ms=phan_vi(local.thoi_gian, .95),
                   ket_qua=tong_hop(rows), tung_ca=rows)
        hai = ket['ket_qua']['hai_lop']
        ket['muc_tieu_0_lot'] = ('KHÔNG ĐẠT' if hai['so_ca_lot']
                                    else 'CHƯA ĐO ĐỦ' if hai['ca_hop_le'] < len(ca) or not local.so_luot
                                    or not hai['so_span_gold_phat_hanh']
                                    else '0 lọt quan sát trên ứng viên; chờ lead')
    finally:
        ai.app.ngan, ai.bo_hoi.cong_ai = cu
    return ket


def main(argv=None):
    p = ArgumentParser(description=__doc__)
    p.add_argument('--that', action='store_true')
    p.add_argument('--url')
    p.add_argument('--model')
    p.add_argument('--bao-cao')
    p.add_argument('--tap', choices=['ung_vien', 'development', 'hoi_quy_lead_cu'], default='ung_vien')
    a = p.parse_args(argv)
    if a.that and (not a.url or not a.model):
        p.error('--that cần đủ --url và --model.')
    try:
        dich = Path(a.bao_cao).resolve() if a.bao_cao else None
        if dich is not None:
            tuong_doi = dich.relative_to(GOC) if dich.is_relative_to(GOC) else None
            trong_engine = (tuong_doi is not None and len(tuong_doi.parts) > 1
                            and tuong_doi.parts[0].startswith('e_'))
            if dich.suffix.lower() != '.json' or trong_engine or dich.exists() or not dich.parent.is_dir():
                raise ValueError('Báo cáo phải là tệp JSON mới ngoài thư mục engine.')
        ket = do(doc_bo(), that=a.that, url=a.url, model=a.model, tap=a.tap)
        raw = json.dumps(ket, ensure_ascii=False, allow_nan=False, indent=2) + '\n'
        if dich is not None:
            with dich.open('x', encoding='utf-8') as f:
                f.write(raw)
        print(raw, end='')
        if a.that:
            return 0 if ket['muc_tieu_0_lot'].startswith('0 lọt') and ket['so_luot_cloud'] == 0 else 1
        return 0
    except Exception:
        print('Không hoàn tất phép đo DEMO. Kiểm tra tham số, bộ DEMO và môi trường; chưa có kết luận Local.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
