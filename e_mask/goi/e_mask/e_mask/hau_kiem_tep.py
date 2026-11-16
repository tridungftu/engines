"""B7: đủ nguồn Local, span và bytes cuối mới được bàn giao bản che."""
from bisect import bisect_right
from copy import deepcopy
from types import SimpleNamespace
import re
from typing import Protocol

from kho_tri_thuc_sdk.engine import ChuaRo, LoiDuongTruyen

from . import che_van_ban as che, chuan_bi_ai as cb, hau_kiem_ai as hk, phong_bi
from . import tep_word as word, tep_excel as excel
from .anh_xa_ai import bam_chu, kiem_anh_xa
from .chuan_bi_tep import yeu_cau, nguon_local
from .doc_tep import KY_TU_RA_TOI_DA, BYTE_CHU_RA_TOI_DA, JSON_BAO_CAO_TOI_DA
from .ho_so_ai import GIOI_HAN_HO_SO, bam_bytes, json_chuan
from .ho_so_tep import (VAN_BAN, GIU_DINH_DANG, MIME, HoSoTepRAM, bao_ve,
                        loi)


def chieu_span(s, moi):
    mien = s['mien']
    dau = [a for a, _b, _i in mien]
    ket = set()
    for a, b, _u, _v, nhom in moi:
        j = bisect_right(dau, a) - 1
        if j < 0:
            raise hk.loi('MASK_AI_CON_SOT')
        x, y, i = mien[j]
        if i is None or not x <= a < b <= y:
            raise hk.loi('MASK_AI_CON_SOT')
        ket.add((i, word.UngVien(a - x, b - x, nhom, 'local')))
    return tuple(sorted(ket, key=lambda p: (p[0], p[1].bat_dau, p[1].ket_thuc, p[1].nhom)))


class CongHauKiemTep(Protocol):
    """C-P4-02/03/04/05 đề nghị; không phải API SDK đã phát hành.

    Core xác thực tập nguồn và kiểm lại tệp gốc qua BĂM/ACL; không trả gốc
    hoặc snapshot. chot_metadata là cửa xác nhận giao dịch metadata chung
    theo ID/phiên bản và dấu chống lặp, không nhận tên. Thiếu bảo đảm này
    phải từ chối, không dùng bộ đếm/map RAM làm giao dịch bền dự phòng.
    ban_giao cách ly bản che/upload tới khi SDK chốt và vẫn còn quyền,
    lease, hạn chuỗi. Core thu hồi upload khi lỗi/hủy, giải quyết mất ACK.
    """
    def nhan_phan_hoi(self, viec, ctx, *, dau, bam_dau_vao) -> bytes: ...
    def kiem_han(self, viec, ctx, *, bien_nhan) -> bool: ...
    def chung_thuc(self, viec, ctx, *, de_nghi: bytes) -> bool: ...
    def kiem_nguon_tep(self, viec, ctx, *, bam_tep) -> bool: ...
    def chot_metadata(self, viec, ctx, *, chung_cu: bytes, metadata: bytes) -> bool: ...
    def ban_giao(self, viec, ctx, *, chung_cu: bytes, ket_qua: bytes) -> bool: ...


def _kiem_cuoi(s, *, kiem, buoc):
    """Đọc/patch lại bytes thực; so map và tiền/ngày trên từng vùng gốc."""
    module = word if s['loai'] == 'docx' else excel
    raw, sau, kich_ban = module._ghi(s['tai_lieu'], s['anh_xa'], buoc)
    if raw != s['da_che'] or bam_bytes(raw) != s['bam_da_che'] or kich_ban != s['kich_ban']:
        raise loi()
    for i, (v, m) in enumerate(zip(sau.vung, s['anh_xa'])):
        kiem()
        chu = v.van_ban if s['loai'] == 'docx' else v.chu
        if m is None:
            if chu:
                raise loi()
            continue
        kiem_anh_xa(m)
        if chu != m.da_che or module._kiem_vung(m.goc, module._phep_alias(m), buoc) != m:
            raise loi('MASK_DINH_DANH_CHUA_DAT')
        # Kiểm nhãn tài khoản/giấy tờ dạng ngày theo B5b, kể cả B6 cũ.
        con, du = che._kiem_con_sot(chu, [(g, 'KHAC', True) for g in m.alias_nguyen_van().values()])
        ngay = sorted((a, b) for a, b, loai, _ in che._cac_tien_ngay(chu) if loai == 'ngay')
        if not du or any(not che._duoc_mien_ngay(chu, x['vi_tri']['bat_dau'],
                x['vi_tri']['ket_thuc'], x['nhom'], ngay)
                for x in module._canh_bao_chu_chua_dat(chu, con)):
            raise loi('MASK_DINH_DANH_CHUA_DAT')
    return sau


def _metadata(s):
    ket = {}
    for _nhom, muc in s['ngan_sach']['da_tim'].values():
        if muc is not None and muc['bi_danh'] in s['alias_nguyen_van']:
            ket[muc['id_dinh_danh']] = {k: muc[k] for k in (
                'id_dinh_danh', 'id_bi_danh', 'bi_danh', 'nhom', 'row_version')}
    if {m['bi_danh'] for m in ket.values()} != set(s['alias_nguyen_van']):
        raise loi()
    # Tối đa một lô SDK; tạo tên mới/unique bí mật vẫn bị R2/R3 chặn.
    if len(ket) > 100:
        raise hk.loi('MASK_AI_QUA_GIOI_HAN')
    return [ket[k] for k in sorted(ket)]


def _ket_qua(h, s, m, metadata, ma, phien_ban):
    chu = m.da_che
    if len(chu) > KY_TU_RA_TOI_DA or len(chu.encode('utf-8')) > BYTE_CHU_RA_TOI_DA:
        raise phong_bi.loi('MASK_QUA_GIOI_HAN')
    # Mã vùng/chỉ số, không tên sheet/đường XML/tên tệp nguồn.
    vung = ['vung_' + str(i) for i in range(len(s['anh_xa']))]
    if s['loai'] == 'xlsx' and any(o.vung is None and o.gia_tri is not None for o in s['tai_lieu'].o):
        vung.append('o_bat_bien')
    aliases = [dict(bi_danh=t['bi_danh'], nhom=t['nhom'], nguon='chinh_thuc') for t in metadata]
    so_cho = sum(len(word._phep_alias(x)) for x in s['anh_xa'])
    muc = dict(phien_ban=1, van_ban=chu, ma_yeu_cau=ma, con_sot=[], kiem_tien_ngay=True,
        chuyen_tiep={}, so_cho_thay=so_cho, bi_danh=aliases, cho_duyet={'so_cum_vua_them': 0},
        vung_da_quet=vung, phien_ban_engine=phien_ban, bam_dau_vao=h['bam_tep'], canh_bao=[])
    bao_cao = {k: v for k, v in muc.items() if k != 'van_ban'}
    if len(json_chuan(bao_cao)) > JSON_BAO_CAO_TOI_DA:
        raise phong_bi.loi('MASK_QUA_GIOI_HAN')
    if h['nang_luc_cuoi'] == VAN_BAN:
        ket = dict(loai='van_ban_da_che', van_ban_da_che=muc)
        phong_bi.kiem_loai(ket, 'van_ban_da_che')
        return ket
    ket = dict(loai='truong', truong=dict(tep_da_che=None, ma_yeu_cau=ma, con_sot_json='[]',
        kiem_tien_ngay=True, so_cho_thay=so_cho, bi_danh_json=phong_bi.json_chu(aliases),
        so_cum_vua_them=0, vung_da_quet_json=phong_bi.json_chu(vung), canh_bao_json='[]'))
    preview = deepcopy(ket)
    preview['truong']['tep_da_che'] = dict(tep_id='x' * 200, ten='mask-da-che.' + h['loai'],
                                          mime=MIME[h['loai']], kich_thuoc=len(s['da_che']))
    if len(json_chuan(preview)) > JSON_BAO_CAO_TOI_DA:
        raise phong_bi.loi('MASK_QUA_GIOI_HAN')
    return ket


class HauKiemTep(HoSoTepRAM):
    @bao_ve
    def hau_kiem(self, viec, *, nang_luc):
        with self.so_huu(viec):
            return self._hau_kiem(nang_luc)

    def _hau_kiem(self, nang_luc):
        h = s = bundle = raw = m = moi = ket = dau_vao = None
        try:
            dau_vao = deepcopy(self.viec.dau_vao)
            ai = phong_bi.doc_hau_kiem_ai(dau_vao)
            h, s = self.doc()
            if (nang_luc not in {VAN_BAN, GIU_DINH_DANG} or h['nang_luc_cuoi'] != nang_luc
                    or h['phien_ban_engine'] != self.phien_ban_engine
                    or ai['chuyen_tiep']['mask_2c']['ma_yeu_cau'] != self.ctx.ma_yeu_cau
                    or set(h['da_giao']) != set(range(len(h['ke_hoach'])))):
                raise hk.loi('MASK_AI_NGUON')
            try:
                self.dung('kiem_nguon_tep', bam_tep=h['bam_tep'])
                raw = self.goi('nhan_phan_hoi', dau=h['dau'], bam_dau_vao=bam_bytes(json_chuan(dau_vao)))
                bundle = hk._json(raw, GIOI_HAN_HO_SO)
                hk._khoa(bundle, 'phien_ban ma_yeu_cau phan_hoi')
                if (type(bundle['phien_ban']) is not int or bundle['phien_ban'] != 1
                        or bundle['ma_yeu_cau'] != self.ctx.ma_yeu_cau
                        or type(bundle['phan_hoi']) is not list
                        or len(bundle['phan_hoi']) != len(h['ke_hoach'])):
                    raise hk.loi('MASK_AI_NGUON')
                chung = []
                for i, phan in enumerate(bundle['phan_hoi']):
                    self.kiem()
                    hk._khoa(phan, 'tra_loi_ai nguon')
                    nguon = phan['nguon']
                    hk._khoa(nguon, 'engine nang_luc nha_cung_cap model trang_thai hoan_tat')
                    hk._khoa(nguon['hoan_tat'], 'giao_thuc ket_thuc')
                    if any(type(n) is not str or not re.fullmatch(r'[A-Za-z0-9_.:@-]{1,100}', n)
                           for n in [*(nguon[k] for k in nguon if k != 'hoan_tat'), *nguon['hoan_tat'].values()]):
                        raise hk.loi('MASK_AI_NGUON')
                    yc = yeu_cau(h, self.ctx.ma_yeu_cau, i)
                    bam_yc = bam_bytes(json_chuan(yc))
                    if h['da_giao'][i] != bam_yc:
                        raise hk.loi('MASK_AI_NGUON')
                    chung.append(dict(chi_so_doan=i, bam_yeu_cau=bam_yc,
                        bam_phan_hoi=bam_bytes(json_chuan(phan['tra_loi_ai'])), nguon=nguon))
                if json_chuan(bundle['phan_hoi'][-1]['tra_loi_ai']) != json_chuan(dau_vao):
                    raise hk.loi('MASK_AI_NGUON')
                de_nghi = json_chuan(dict(phien_ban=1, ma_yeu_cau=self.ctx.ma_yeu_cau,
                    ma_ho_so_ram=h['dau'].ma_ho_so_ram, bam_ho_so=h['dau'].bam_ho_so,
                    bam_tap_phan_hoi=bam_bytes(raw), bam_dau_vao=bam_bytes(json_chuan(dau_vao)), phan_hoi=chung))
                self.dung('kiem_han', bien_nhan=deepcopy(h['bien_nhan']))
                self.dung('chung_thuc', de_nghi=de_nghi)
                self.ghi(h, phan_hoi_local=bundle)
            except ChuaRo:
                self.buoc.cho_ai()
                raise
            cac_doan = []
            for i, phan in enumerate(bundle['phan_hoi']):
                self.kiem()
                ts = hk._kiem_phan_hoi(yeu_cau(h, self.ctx.ma_yeu_cau, i), phan['tra_loi_ai'], phan['nguon'], h)
                if any(t['muc'] != 'chac' for t in ts):
                    raise hk.loi('MASK_AI_CON_SOT')
                cac_doan.append(ts)
            noi = hk.HauKiemAI(ngan=None, quyen=self.quyen, cong=None, phien_ban_engine=self.phien_ban_engine)
            moi = noi._span(SimpleNamespace(anh_xa=h['map_quy_tac'], ke_hoach=h['ke_hoach']),
                            cac_doan, kiem=self.kiem)
            them = chieu_span(h, moi)
            if h['loai'] == 'docx':
                word.che_them_word(them, buoc=self.buoc)
            else:
                excel.che_them_excel(them, buoc=self.buoc)
            # B5/B6 giữ đúng dict state; map/bytes mới vẫn dưới cùng handle.
            s = self.buoc.du_lieu['tep_word' if h['loai'] == 'docx' else 'tep_excel']
            _kiem_cuoi(s, kiem=self.kiem, buoc=self.buoc)
            m, mien = nguon_local(s, kiem=self.kiem)
            if mien != h['mien'] or m.goc != h['map_quy_tac'].goc:
                raise loi()
            meta = _metadata(s)
            ket = _ket_qua(h, s, m, meta, self.ctx.ma_yeu_cau, self.phien_ban_engine)
            chung_cu = json_chuan(dict(phien_ban=1, nang_luc=nang_luc,
                bam_nguon=bam_bytes(de_nghi), bam_tep_goc=h['bam_tep'], bam_tep_da_che=s['bam_da_che'],
                bam_van_ban=bam_chu(m.da_che), so_doan=len(h['ke_hoach']),
                so_vung=len(s['anh_xa']), kiem_tien_ngay=True))
            self.dung('kiem_han', bien_nhan=deepcopy(h['bien_nhan']))
            self.dung('chung_thuc', de_nghi=de_nghi)
            self.dung('kiem_nguon_tep', bam_tep=h['bam_tep'])
            # Đến đây mới xác nhận metadata; mọi trần/reader/span/nguồn đã đạt.
            # ChuaRo từ chốt/bàn giao là kết thúc, không giữ map để chốt lại.
            self.dung('chot_metadata', chung_cu=chung_cu, metadata=json_chuan(meta))
            if nang_luc == GIU_DINH_DANG:
                self.kiem()
                try:
                    ref = self.viec.tai_tep_ra('mask-da-che.' + h['loai'], s['da_che'], MIME[h['loai']])
                except LoiDuongTruyen as exc:
                    if exc.thu_lai_duoc or exc.http_status is None or exc.http_status >= 500:
                        raise ChuaRo('mask-tep-' + s['bam_da_che'][7:]) from None
                    raise
                except (TimeoutError, ConnectionError):
                    raise ChuaRo('mask-tep-' + s['bam_da_che'][7:]) from None
                self.kiem()
                if (type(ref) is not dict or set(ref) != {'tep_id', 'ten', 'mime', 'kich_thuoc'}
                        or type(ref['tep_id']) is not str or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,200}', ref['tep_id'])
                        or ref.get('ten') != 'mask-da-che.' + h['loai']
                        or ref.get('mime') != MIME[h['loai']] or ref.get('kich_thuoc') != len(s['da_che'])):
                    raise loi()
                ket['truong']['tep_da_che'] = ref
            self.dung('ban_giao', chung_cu=chung_cu, ket_qua=json_chuan(ket))
            self.dung('kiem_han', bien_nhan=deepcopy(h['bien_nhan']))
            self.dung('chung_thuc', de_nghi=de_nghi)
            self.kiem()
            with self.ram._khoa:
                self.ram._kiem_buoc(self.buoc)
                du = self.buoc._ban_ghi.du_lieu
                h['giai_doan'] = s['giai_doan'] = 'DA_HAU_KIEM'
                s['vung_da_kiem_local'] = tuple(range(len(s['anh_xa'])))
                h.pop('phan_hoi_local', None)
                du.update(giai_doan_ai='DA_HAU_KIEM', anh_xa_cuoi=m,
                          alias_nguyen_van=s['alias_nguyen_van'].copy())
            self.viec.tien_do(100, 'Đã hậu kiểm đủ đoạn và bytes tệp bằng AI cục bộ.')
            self.buoc.cho_ai()
            return ket
        finally:
            h = s = bundle = raw = m = moi = ket = dau_vao = None
