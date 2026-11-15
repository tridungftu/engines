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
import subprocess
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
from e_mask.ho_so_ai import bam_bytes, json_chuan
from ho_tro_hau_kiem_ai import (CATALOGUE, CongHauKiemCoreGia, giao, chay,
                                tao_bo as tao_bo_ram, ho_so_ram)
from ho_tro_ngan import viec_demo

BO_DEMO = Path(__file__).with_name('mask_2c_4_ung_vien_demo.json')
PROMPT = 'Quy trình đo DEMO MASK-2c-4.\n' + cb.CHI_DAN_BAT_BUOC
MA_PROMPT, PHIEN_PROMPT = 'demo.mask_2c_4', 'DEMO-1'
ALIAS = re.compile(r'\[\[[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\]\]')
CHAN_NGHIEP_VU = {'MASK_DINH_DANH_CHUA_DAT', 'MASK_AI_CON_SOT'}
MA_KY_THUAT = {'AI_TRA_SAI_KHUON', 'LOCAL_AI_KHONG_SAN_SANG', 'MASK_AI_SPAN_KHONG_HOP_LE',
               'MASK_AI_NGUON', 'MASK_AI_HO_SO', 'MASK_AI_CHUA_DAT', 'MASK_AI_CHUA_CO_CUA_CORE',
               'MASK_AI_NGAN_SACH', 'MASK_AI_QUA_GIOI_HAN', 'MASK_AI_PROFILE_KHONG_HOP_LE',
               'VUOT_GIOI_HAN', 'HET_HAN_CHUOI', 'SAI_MODEL'}
TRAN_TIMEOUT = 3600


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
    # Chỉ catalogue DEMO đã cấp trước chuỗi; SDK trả null+cờ. Không đọc
    # kho bản rõ, map nội bộ R4, gold hoặc snapshot Core để suy phép che.
    gia_tri = {alias: chuan(ten) for ten, _nhom, alias in ngan.danh_muc_demo}
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
               so_span_che_thua=None, so_ky_tu_che_thua=None,
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
        # Hợp các khoảng vàng, kể cả khi chồng nhau. Đếm phần phép che nằm
        # ngoài hợp này trên MỌI ca, không chỉ các câu không có định danh.
        vang = []
        for t in sorted(ca['gold'], key=lambda t: t['bat_dau']):
            a, b = t['bat_dau'], t['ket_thuc']
            if vang and a <= vang[-1][1]:
                vang[-1] = (vang[-1][0], max(b, vang[-1][1]))
            else:
                vang.append((a, b))
        thua = [b - a - sum(max(0, min(b, z) - max(a, x)) for x, z in vang) for a, b in phep]
        ket.update(trang_thai='phat_hanh_con_lot' if so_lot else 'phat_hanh_che_du',
                   so_span_lot=so_lot, che_thua=any(thua),
                   so_span_che_thua=sum(n > 0 for n in thua), so_ky_tu_che_thua=sum(thua))
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
        khoa = ctx.ma_yeu_cau
        cu = self.ngan_sach[khoa]
        if not hasattr(self, '_han'):
            self._han = (datetime.now(timezone.utc) + timedelta(seconds=self.han_giay)).isoformat()
        cu['han_chuoi'] = self._han
        cu['han_local_giay'] = max(1, math.ceil(self.han_giay))
        v.update(han_chuoi=cu['han_chuoi'], han_local_giay=cu['han_local_giay'])
        return v

    def kiem_han(self, viec, ctx, *, bien_nhan):
        self._quyen(viec, ctx)
        return (time.monotonic() - self.bat_dau < self.han_giay
                and bien_nhan == self.ngan_sach.get(ctx.ma_yeu_cau))


def tao_bo(ca, model, han_giay):
    chu = ca['van_ban']
    # Catalogue hồi quy công khai của adapter, độc lập gold và Local.
    # Tên ngoài catalogue vẫn fail-closed, không tự duyệt theo model/gold.
    seeds = [(ten, 'CA_NHAN', '[[MASKCN-DEMO-%04d]]' % i)
             for i, ten in enumerate(CATALOGUE, 1) if chuan(ten) in chuan(chu)]
    return tao_bo_ram(chu, cong=CongDoCoreGia(None, model, han_giay), seeds=seeds)


def chay_buoc(b, nang_luc):
    # tao_bo_ram đã xếp bước chuẩn bị đầu tiên, dùng chính kho R4 của app.
    b.c.chay(b.app)
    k = b.c.xem(b.v)
    if nang_luc == 'mask.che_van_ban@1' and k['trang_thai'] == 'XONG':
        # Baseline quy tắc là phép khảo sát trong RAM, chưa qua Local và
        # không phải public handler mask.che_van_ban (R3 đang đóng).
        from e_mask import phong_bi
        s, _ = ho_so_ram(b)
        return dict(trang_thai='XONG', ket_qua=phong_bi.ket_qua_che(
            s['ket_qua_quy_tac'], b.chu))
    return k


class DemLocal:
    def __init__(self, provider, model):
        self.provider, self.model = provider, model
        self.so_luot, self.thoi_gian = 0, []

    def hoi(self, cau_hinh, model, *a, **kw):
        # Không cho phép chọn model khác khi ưu tiên mất giữa hai bước.
        if model != self.model:
            raise LoiNghiepVu('LOCAL_AI_KHONG_SAN_SANG', 'Model được chỉ định không khả dụng.')
        self.so_luot += 1
        if getattr(self, 'khi_goi', None):
            self.khi_goi()
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
    from e_hoi_ai.cong_ai import CongAI
    from e_hoi_ai.nha_cung_cap import NhaCungCapLocal
    core = CoreGia(ai.app)
    cfg = {'local_ai': {'url': url, 'timeout_giay': timeout},
           'quy_tac_model': [{'mau_ma_prompt': MA_PROMPT,
                              'uu_tien': model, 'du_phong': []}]}
    core.dat_cau_hinh(ai.app.ma, cfg)
    local, cloud = DemLocal(NhaCungCapLocal(), model), DemCloud()
    cu = ai.bo_hoi.cong_ai
    ai.bo_hoi.cong_ai = CongAI(nha_cung_cap={'local': local, 'cloud': cloud})
    return SimpleNamespace(app=ai.app, core=core, cfg=cfg), local, cloud, cu


def hai_lop(b, ai, model, thong_ke=None, cap_nhat=None):
    if thong_ke is None:
        thong_ke = dict(so_doan_ke_hoach=0, so_doan_ai_xong=0, du_doan=False)
    truoc = chay_buoc(b, cb.NANG_LUC)
    if truoc['trang_thai'] != 'XONG':
        thong_ke['chan_truoc_ai'] = (truoc.get('loi') or {}).get('ma') == 'MASK_DINH_DANH_CHUA_DAT'
        return truoc, thong_ke
    meta = truoc['ket_qua']['yeu_cau_ai']['chuyen_tiep']['mask_2c']
    b.s, b.dau = ho_so_ram(b)
    n = len(b.s['quy_tac']['ke_hoach'])
    for i in range(1, n):
        b.cong.i = i
        b.v = b.c.giao_viec(cb.NANG_LUC, {'loai': 'van_ban', 'van_ban': b.chu})
        ctx = b.q.cap(b.v, ma_yeu_cau=b.ctx.ma_yeu_cau)
        b.cong.cap(viec_demo(b.v), ctx)
        b.c.chay(b.app)
        k = b.c.xem(b.v)
        if k['trang_thai'] != 'XONG': return k, thong_ke
    b.ys = [deepcopy(b.cong.giao[i]) for i in range(n)]
    thong_ke['so_doan_ke_hoach'] = len(b.ys)
    ds = []
    for y in b.ys:
        con_lai = b.cong.han_giay - (time.monotonic() - b.cong.bat_dau)
        if con_lai <= 0:
            thong_ke['het_han'] = True
            return {'trang_thai': 'LOI', 'loi': {'ma': 'HET_HAN_CHUOI'}}, thong_ke
        # Một lần gọi không được dùng lại toàn bộ deadline của ca. Giữ
        # trần timeout 600 giây của cấu hình AI-9 nguyên bản.
        cfg = deepcopy(ai.cfg)
        cfg['local_ai']['timeout_giay'] = min(600, con_lai)
        ai.core.dat_cau_hinh(ai.app.ma, cfg)
        kq = ai.core.chay_thu(ai.app, 'ai.hoi_mask_cuc_bo@1', deepcopy(y))
        if cap_nhat:
            cap_nhat()
        if time.monotonic() - b.cong.bat_dau >= b.cong.han_giay:
            thong_ke['het_han'] = True
            return {'trang_thai': 'CHUA_RO'}, thong_ke
        if kq['trang_thai'] != 'XONG':
            return kq, thong_ke
        thong_ke['so_doan_ai_xong'] += 1
        if cap_nhat:
            cap_nhat()
        if kq['ket_qua']['tra_loi_ai']['model'] != model:
            return {'trang_thai': 'LOI', 'loi': {'ma': 'SAI_MODEL'}}, thong_ke
        ban_model = next((r for r in ai.core.xem_ngan(ai.app.ma, 'model_phat_hien')
                          if r['id_model'] == model), None)
        loai_api = ban_model['loai'] if ban_model else ''
        ds.append(dict(tra_loi_ai=kq['ket_qua'], nguon=dict(
            engine='e_hoi_ai', nang_luc='ai.hoi_mask_cuc_bo@1', nha_cung_cap='local', model=model,
            trang_thai='XONG', hoan_tat=dict(giao_thuc='ollama' if loai_api == 'ollama' else 'openai_compatible',
                                           ket_thuc='stop'))))
    bundle = dict(phien_ban=1, ma_yeu_cau=b.ctx.ma_yeu_cau, phan_hoi=ds)
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


def tong_hop(rows, *, tach=True):
    ket = {}
    for che_do in ('quy_tac', 'hai_lop'):
        ds = [r for r in rows if r['che_do'] == che_do]
        thuong = [r for r in ds if r['nhom'] == 'thuong']
        hop_le = [r for r in ds if r['trang_thai'] not in {'loi_ky_thuat', 'chua_ro'}
                  and r.get('tinh_trang_do') != 'chưa đo đủ']
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
            so_ca_chua_do_du=sum(r.get('tinh_trang_do') == 'chưa đo đủ' for r in ds),
            che_thua_dinh_danh=dict(
                so_ca=sum(r['so_span_gold'] > 0 and r['che_thua'] is True for r in ds),
                so_ca_da_cham=sum(r['so_span_gold'] > 0 and r['che_thua'] is not None for r in ds),
                tong_ca_co_gold=sum(r['so_span_gold'] > 0 for r in ds),
                so_span=sum(r.get('so_span_che_thua') or 0 for r in ds if r['so_span_gold']),
                so_ky_tu=sum(r.get('so_ky_tu_che_thua') or 0 for r in ds if r['so_span_gold'])),
            p50_ms=phan_vi([r['thoi_gian_ms'] for r in ds], .5),
            p95_ms=phan_vi([r['thoi_gian_ms'] for r in ds], .95))
        ket[che_do]['theo_nhom'] = {g: {s: sum(r['nhom'] == g and r['trang_thai'] == s for r in ds)
            for s in ket[che_do]['trang_thai']} for g in ('nguoi', 'to_chuc', 'dia_chi', 'thuong', 'bien_the')}
        v = ket[che_do]
        v['ti_le_lot_ca_phat_hanh'] = v['so_ca_lot'] / v['so_ca_phat_hanh'] if v['so_ca_phat_hanh'] else None
        v['ti_le_lot_span_phat_hanh'] = (v['so_span_lot'] / v['so_span_gold_phat_hanh']
                                       if v['so_span_gold_phat_hanh'] else None)
    if tach:
        ds = [r for r in rows if r['che_do'] == 'hai_lop']
        ket['hai_lop']['phan_tach'] = {
            ten: tong_hop(loc, tach=False)['hai_lop'] for ten, loc in (
                ('chan_truoc_ai', [r for r in ds if r.get('chan_truoc_ai')]),
                ('ai_thuc_su_do', [r for r in ds if r['so_doan_ai_xong'] > 0]),
                ('chua_co_doan_ai_xong', [r for r in ds if not r.get('chan_truoc_ai')
                                         and not r['so_doan_ai_xong']]))}
        ket['hai_lop']['so_ca_ai_da_goi_provider'] = sum(r.get('so_luot_local', 0) > 0 for r in ds)
        ket['hai_lop']['ghi_chu'] = ('0 lọt trên ca bị chặn trước AI là hiển nhiên. '
            'AI thực sự đo = có ít nhất một đoạn AI-9 XONG; đủ đoạn/hợp lệ báo riêng. '
            'Số lọt chưa đo để null từng ca; số 0 tổng chỉ là số quan sát, không chứng minh an toàn.')
    return ket


def han_ca(ca, timeout=None, timeout_toi_da=TRAN_TIMEOUT):
    for n in (timeout, timeout_toi_da):
        if n is not None and (isinstance(n, bool) or not math.isfinite(n) or n <= 0):
            raise ValueError('Thời hạn phải là số giây dương hữu hạn.')
    so_doan = len(cb.lap_ke_hoach(ca['van_ban']))
    return min(timeout if timeout is not None else 120 * so_doan, timeout_toi_da), so_doan


def dong_chua_do(ca, che_do, *, ma='CHUA_DO', **dem):
    return dict(ca=ca['ma'], nhom=ca['nhom'], che_do=che_do,
                so_span_gold=len(ca['gold']), trang_thai='loi_ky_thuat',
                so_span_lot=None, che_thua=None, so_span_che_thua=None, so_ky_tu_che_thua=None,
                ma_loi=ma, thoi_gian_ms=0, so_doan_ke_hoach=0, so_doan_ai_xong=0,
                du_doan=False, chan_truoc_ai=False, tinh_trang_do='chưa đo đủ', **dem)


# Lead đóng băng bộ held-out 15/11/2026 sau kiểm độc lập (190 ca, 124 span vàng).
DONG_BANG_SHA = "sha256:b720fb2d9a330110ed5c4d5fd777b9728887f863651a2b0c46dc395dc45c95ad"


def chot_bao_cao(ket, rows):
    ket.update(trang_thai_local='ĐÃ THỬ Local qua CoreGia; chưa nghiệm thu độc lập',
               ket_qua=tong_hop(rows), tung_ca=rows)
    hai = ket['ket_qua']['hai_lop']
    ai = hai['phan_tach']['ai_thuc_su_do']
    ket['muc_tieu_0_lot'] = ('KHÔNG ĐẠT' if hai['so_ca_lot'] else 'CHƯA ĐO ĐỦ'
        if hai['ca_hop_le'] < ket['so_ca'] or not ai['so_span_gold_phat_hanh']
        or ket.get('loi_giua_chung') else '0 lọt quan sát trên ứng viên; chờ lead')
    return ket


def do(bo, *, that=False, url=None, model=None, timeout=None, timeout_toi_da=TRAN_TIMEOUT,
       tap='ung_vien', cap_nhat=None):
    ca = bo['noi_dung'][tap]
    ket = dict(nhan='DEMO', trang_thai_local='CHƯA ĐO Local thật', core='CoreGia',
               canh_bao='CoreGia không chứng nhận cửa Core thật; nợ CAO còn mở, Cloud giữ tắt.',
               held_out_doc_lap=(tap == 'ung_vien' and bo['sha256_noi_dung'] == DONG_BANG_SHA),
               tinh_trang_gold=('ĐÃ ĐÓNG BĂNG — lead 15/11/2026' if tap == 'ung_vien'
                   and bo['sha256_noi_dung'] == DONG_BANG_SHA else bo['tinh_trang_gold']),
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
    for c in ca:
        han_ca(c, timeout, timeout_toi_da)
    ket.update(phien_ban_sdk=kho_tri_thuc_sdk.__version__, phien_ban_cong_cu='MASK-R5-RAM-1',
               bam_cong_cu=bam_bytes(Path(__file__).read_bytes()),
               timeout=dict(giay=timeout, mac_dinh_giay_moi_doan=120, tran_giay=timeout_toi_da),
               bam_cau_hinh_khong_url=bam(dict(model=model, timeout_giay=timeout,
                                               timeout_toi_da=timeout_toi_da, profile=cb.profile())),
               thoi_diem_utc=datetime.now(timezone.utc).isoformat(),
               dinh_nghia_luot_local='Số gọi provider Local, kể cả lỗi trước POST; số đoạn AI xong báo riêng.',
               so_timeout_xac_dinh=None,
               ghi_chu_timeout='AI-9 gom timeout/mất phản hồi/202 vào ChuaRo; không suy số timeout bằng 0.',
               gioi_han_ket_luan='AI chỉ cứu khi báo đủ; báo thiếu một phần tên thì phần còn lại có thể lọt.')
    ket['gioi_han_kho'] = ('Catalogue DEMO đã duyệt, độc lập gold/phản hồi Local; '
                         'tên mới thiếu bảo đảm Core bị chặn. Chưa chứng nhận chất lượng thật.')
    # Khô chỉ kiểm bộ/băm/cấu trúc. Không có số đo detector hoặc Local giả.
    if not that:
        return ket
    if not url or not model:
        raise ValueError('Chạy thật cần đủ URL và model.')
    rows = [dong_chua_do(c, che_do) for c in ca for che_do in ('quy_tac', 'hai_lop')]
    ai = local = cloud = cu = b = None
    def tien_do():
        if local:
            ket.update(so_luot_cloud=cloud.so_luot, so_luot_local=local.so_luot,
                       local_p50_ms=phan_vi(local.thoi_gian, .5),
                       local_p95_ms=phan_vi(local.thoi_gian, .95),
                       thoi_gian_local_ms=local.thoi_gian[:])
        chot_bao_cao(ket, rows)
        if cap_nhat:
            cap_nhat(ket)
    try:
        ai, local, cloud, cu = ai_ram(url, model, min(timeout or 120, timeout_toi_da, 600))
        ket['phien_ban_hoi_ai'] = ai.app.phieu['phien_ban']
        for i, c in enumerate(ca):
            han, so_doan = han_ca(c, timeout, timeout_toi_da)
            for j, che_do in enumerate(('quy_tac', 'hai_lop')):
                row = rows[2 * i + j]
                b = tao_bo(c, model, han)
                start = time.perf_counter()
                thong_ke = dict(so_doan_ke_hoach=0, so_doan_ai_xong=0, du_doan=False,
                                chan_truoc_ai=False, het_han=False)
                luot = local.so_luot
                row.update(timeout_giay=han, so_doan_du_kien=so_doan)
                def cap_nhat_ca():
                    row.update(**thong_ke, so_luot_local=local.so_luot - luot)
                    tien_do()
                local.khi_goi = cap_nhat_ca
                cap_nhat_ca()
                if che_do == 'quy_tac':
                    kq = chay_buoc(b, 'mask.che_van_ban@1')
                else:
                    kq, thong_ke = hai_lop(b, ai, model, thong_ke, cap_nhat_ca)
                # Chỉ mã ca cố định/đếm/băm/thời gian; không phản chiếu lỗi/provider.
                row.update(cham(c, kq, b.n))
                if hasattr(b.q, 'ram_ctx') and b.ctx.ma_yeu_cau in b.q.ram_ctx:
                    b.q.bao_ram(b.ctx.ma_yeu_cau, 'KET_THUC')
                row.update(tinh_trang_do='chưa đo đủ' if thong_ke['het_han']
                           or row['trang_thai'] in {'loi_ky_thuat', 'chua_ro'} else 'đã đo',
                           so_luot_local=local.so_luot - luot,
                           thoi_gian_ms=round((time.perf_counter() - start) * 1000, 3), **thong_ke)
                tien_do()
    except (Exception, KeyboardInterrupt):
        ket['loi_giua_chung'] = 'NGOAI_LE_KHI_DO'
        # Không phản chiếu message/traceback của provider hay dữ liệu gốc.
        for row in rows:
            if row['tinh_trang_do'] == 'chưa đo đủ' and row['ma_loi'] == 'CHUA_DO':
                row['ma_loi'] = 'NGOAI_LE_KHI_DO'
    finally:
        if b is not None and hasattr(b.q, 'ram_ctx') and b.ctx.ma_yeu_cau in b.q.ram_ctx:
            b.q.bao_ram(b.ctx.ma_yeu_cau, 'KET_THUC')
        if cu is not None:
            from e_hoi_ai import chay as ai_module
            ai_module.bo_hoi.cong_ai = cu
    tien_do()
    return ket


def do_cach_ly(bo, *, url, model, timeout=None, timeout_toi_da=TRAN_TIMEOUT, tap='ung_vien'):
    """Mỗi ca một process để timeout cứng không để transport treo nền.

    Child chỉ gửi checkpoint đếm/băm, không message lỗi/gốc/URL. Pipe chỉ
    giữ trong RAM; dừng child chưa chứng minh backend đã hủy request.
    """
    ket = do(bo, model=model, timeout=timeout, timeout_toi_da=timeout_toi_da, tap=tap)
    cac = bo['noi_dung'][tap]
    rows = [dong_chua_do(c, cd) for c in cac for cd in ('quy_tac', 'hai_lop')]
    thoi_gian = []
    so_het_han = 0
    try:
        for i, c in enumerate(cac):
            han, so_doan = han_ca(c, timeout, timeout_toi_da)
            mot = deepcopy(bo)
            mot['noi_dung'] = {tap: [c]}
            tham_so = dict(bo=mot, url=url, model=model, timeout=timeout,
                           timeout_toi_da=timeout_toi_da, tap=tap)
            het_han = False
            try:
                p = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(Path(__file__).resolve()),
                                    '--_ca-con'], input=json.dumps(tham_so, ensure_ascii=False).encode('utf-8'),
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=han)
                raw = p.stdout
                loi = p.returncode != 0
            except subprocess.TimeoutExpired as exc:
                # subprocess.run đã kill VÀ wait child trước khi trả ngoại lệ.
                raw, loi, het_han = exc.stdout or b'', False, True
                so_het_han += 1
            ban = None
            for dong in raw.decode('utf-8', errors='replace').splitlines():
                try:
                    v = json.loads(dong)
                    if isinstance(v, dict) and 'bao_cao' in v:
                        ban = v['bao_cao']
                except ValueError:
                    continue  # Checkpoint cuối có thể bị cắt lúc kill.
            if ban:
                rows[2*i:2*i+2] = ban['tung_ca']
                ket['so_luot_local'] += ban['so_luot_local']
                ket['so_luot_cloud'] += ban['so_luot_cloud']
                thoi_gian.extend(ban.get('thoi_gian_local_ms', []))
                if 'phien_ban_hoi_ai' in ban:
                    ket['phien_ban_hoi_ai'] = ban['phien_ban_hoi_ai']
                loi = loi or bool(ban.get('loi_giua_chung'))
            if het_han:
                for row in rows[2*i:2*i+2]:
                    if row['tinh_trang_do'] == 'chưa đo đủ':
                        row.update(ma_loi='HET_HAN_CHUOI', het_han=True,
                                   timeout_giay=han, so_doan_du_kien=so_doan)
            elif loi or ban is None:
                ket['loi_giua_chung'] = 'NGOAI_LE_KHI_DO'
                break
    except (Exception, KeyboardInterrupt):
        ket['loi_giua_chung'] = 'NGOAI_LE_KHI_DO'
    ket.update(so_ca_het_han_cung=so_het_han, local_p50_ms=phan_vi(thoi_gian, .5),
               local_p95_ms=phan_vi(thoi_gian, .95))
    return chot_bao_cao(ket, rows)


def main(argv=None):
    p = ArgumentParser(description=__doc__)
    p.add_argument('--that', action='store_true')
    p.add_argument('--url')
    p.add_argument('--model')
    p.add_argument('--bao-cao')
    p.add_argument('--thu-muc-bao-cao', help='Thư mục đích chỉ định rõ khi lưu báo cáo trong repo.')
    p.add_argument('--timeout', type=float, help='Giây mỗi ca; mặc định 120 × số đoạn.')
    p.add_argument('--timeout-toi-da', type=float, default=TRAN_TIMEOUT,
                   help='Trần giây mỗi ca, mặc định 3600; không đổi trần runtime AI-9.')
    p.add_argument('--tap', choices=['ung_vien', 'development', 'hoi_quy_lead_cu'], default='ung_vien')
    a = p.parse_args(argv)
    if a.that and (not a.url or not a.model):
        p.error('--that cần đủ --url và --model.')
    try:
        dich = Path(a.bao_cao).resolve() if a.bao_cao else None
        thu_dich = Path(a.thu_muc_bao_cao).resolve() if a.thu_muc_bao_cao else None
        if thu_dich is not None and (not thu_dich.is_dir() or thu_dich == GOC or dich is None):
            raise ValueError('Cần chỉ định thư mục báo cáo riêng và tệp báo cáo mới.')
        if dich is not None:
            trong_repo = dich.is_relative_to(GOC)
            chi_dinh = thu_dich is not None and dich.parent == thu_dich
            # Không dùng cờ chỉ định để ghi vào mã/gói/tài liệu hoặc .git.
            tuong_doi = dich.relative_to(GOC) if trong_repo else None
            thu_cam = tuong_doi is not None and (tuong_doi.parts[0].startswith(('e_', '.git'))
                                                or tuong_doi.parts[0] in {'docs', '_chung'})
            if (dich.suffix.lower() != '.json' or dich.exists() or not dich.parent.is_dir()
                    or trong_repo and (not chi_dinh or thu_cam)
                    or thu_dich is not None and not chi_dinh):
                raise ValueError('Báo cáo cần ở ngoài repo hoặc đúng thư mục báo cáo riêng đã chỉ định.')
        bo = doc_bo()
        if a.that:
            ket = do_cach_ly(bo, url=a.url, model=a.model, timeout=a.timeout,
                             timeout_toi_da=a.timeout_toi_da, tap=a.tap)
        else:
            ket = do(bo, timeout=a.timeout, timeout_toi_da=a.timeout_toi_da, tap=a.tap)
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
    if sys.argv[1:] == ['--_ca-con']:
        tham_so = json.load(sys.stdin)
        bo = tham_so.pop('bo')
        do(bo, that=True, cap_nhat=lambda k: print(json.dumps({'bao_cao': k}, ensure_ascii=False,
            allow_nan=False), flush=True), **tham_so)
    else:
        raise SystemExit(main())
