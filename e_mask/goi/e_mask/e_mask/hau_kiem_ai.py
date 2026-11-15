"""Hậu kiểm Local trên hồ sơ RAM; chỉ Core điều phối từng đoạn/phản hồi.

C-P4-04 chưa là API SDK. Không đọc/ghi snapshot Core/ngăn/tệp, không
phục hồi map khi mất RAM, không gọi model hoặc engine khác.
"""
from __future__ import annotations

from copy import deepcopy
from functools import wraps
import json
import re
import unicodedata
from typing import Protocol

from kho_tri_thuc_sdk.engine import ChuaRo, LoiDuongTruyen, LoiNghiepVu, ViecDaHuy

from . import che_van_ban as che, chuan_bi_ai as cb, phong_bi, tai_nguyen
from .anh_xa_ai import bam_chu
from .ho_so_ai import (GIOI_HAN_HO_SO, _bien_doan, bam_bytes, json_chuan,
                       du_lieu_ram, kiem_kho_ram, nhuong_luot)
from .kho_dinh_danh import KhoDinhDanh
from .ngan import NganXungDot
from .nguon.privacy.types import bo_ky_tu_vo_hinh, la_bien_to_hop
from .quyen_yeu_cau import xac_minh, loi_ram
from .tra_cuu_dinh_danh import UngVien, chan_phat_hanh

NANG_LUC = 'mask.hau_kiem_ai_cuc_bo@1'
NANG_LUC_AI = 'ai.hoi_mask_cuc_bo@1'
NHOM = {'nguoi': 'CA_NHAN', 'to_chuc': 'CONG_TY', 'dia_chi': 'DIA_CHI'}
_CAU = {
    'MASK_AI_CHUA_DAT': 'Chưa kiểm tra đủ điều kiện an toàn bằng AI cục bộ.',
    'MASK_AI_CHUA_CO_CUA_CORE': 'Chưa có đủ cổng Core cho hậu kiểm AI cục bộ.',
    'MASK_AI_NGUON': 'Chưa xác minh được nguồn nhận diện cục bộ cho toàn bộ tài liệu.',
    'MASK_AI_HO_SO': 'Không xác minh được hồ sơ nội bộ. Cần thực hiện lại yêu cầu.',
    'MASK_AI_CON_SOT': 'Còn định danh cần kiểm tra. Không thể phát hành văn bản.',
    'MASK_AI_XUNG_DOT': 'Dữ liệu vừa thay đổi. Hãy thử lại cùng yêu cầu.',
    'MASK_AI_QUA_GIOI_HAN': 'Nội dung vượt giới hạn hậu kiểm hoặc một giao dịch.',
}


def loi(ma='MASK_AI_CHUA_DAT'):
    return LoiNghiepVu(ma, _CAU[ma], thu_lai_duoc=ma == 'MASK_AI_XUNG_DOT')


def _bao_ve(ham):
    @wraps(ham)
    def goi(*a, **kw):
        try:
            return ham(*a, **kw)
        except ChuaRo as exc:
            # Không chuyển mã/câu tùy ý của nguồn ra log hoặc phản hồi.
            raise ChuaRo('mask-ai-' + bam_chu(exc.ma_tuong_quan)[7:]) from None
        except ViecDaHuy:
            raise
        except LoiDuongTruyen as exc:
            raise LoiDuongTruyen('MASK_AI_DUONG_TRUYEN', http_status=exc.http_status,
                                thu_lai_duoc=exc.thu_lai_duoc) from None
        except NganXungDot:
            raise loi('MASK_AI_XUNG_DOT') from None
        except LoiNghiepVu as exc:
            if exc.ma in {'MASK_ANH_XA_KHONG_CON', 'MASK_CHUOI_CHUA_GHIM',
                          'MASK_CHUOI_DANG_XU_LY', 'MASK_BUOC_DANG_XU_LY',
                          'MASK_DAU_VAO_THAY_DOI', 'MASK_VONG_DOI_KHONG_HOP_LE'}:
                raise loi_ram(exc.ma) from None
            ma = exc.ma if exc.ma in _CAU else 'MASK_AI_CHUA_DAT'
            if exc.ma == 'MASK_XUNG_DOT':
                ma = 'MASK_AI_XUNG_DOT'
            if exc.ma == 'MASK_QUA_GIOI_HAN':
                ma = 'MASK_AI_QUA_GIOI_HAN'
            raise loi(ma) from None
        except Exception:
            raise loi() from None
    return goi


class CongHauKiemAI(Protocol):
    """Cửa C-P4-04 đề nghị: chỉ chuyển phản hồi Local cần thiết.

    nhan_phan_hoi trả bytes JSON nghiêm, gồm từng phản hồi + nguồn Core;
    không yêu cầu gốc/map/hồ sơ hay yêu cầu AI có tai_lieu để phục hồi.
    chung_thuc đối chiếu băm sổ nguồn và quyền xuyên bước, không tin cờ
    caller. ban_giao chỉ nhận bản che cuối và bằng chứng không nguyên văn.
    Core cách ly chúng tới khi chốt kết quả SDK/ACK còn quyền và còn hạn
    (C-P4-02); gọi port không tự có nghĩa đã phát hành.
    """
    def nhan_phan_hoi(self, viec, ctx, *, dau, bam_dau_vao) -> bytes: ...
    def kiem_han(self, viec, ctx, *, bien_nhan) -> bool: ...
    def chung_thuc(self, viec, ctx, *, de_nghi: bytes) -> bool: ...
    def ban_giao(self, viec, ctx, *, chung_cu: bytes, ket_qua: bytes) -> bool: ...


def _khoa(v, khoa):
    if type(v) is not dict or set(v) != set(khoa.split()):
        raise loi()


def _json(raw, toi_da):
    if type(raw) is not bytes or not 0 < len(raw) <= toi_da:
        raise loi('MASK_AI_QUA_GIOI_HAN')
    def cam(_):
        raise loi()
    v = json.loads(raw.decode('utf-8'), object_pairs_hook=phong_bi._cap, parse_constant=cam)
    if json_chuan(v) != raw:
        raise loi()
    return v


def _kiem_phan_hoi(yeu_cau, phan_hoi, nguon, snapshot):
    """Kiểm lại độc lập; rỗng chỉ hợp lệ sau khuôn/span/trích dẫn/nguồn."""
    ai = phong_bi.kiem_loai(phan_hoi, 'tra_loi_ai')
    y = yeu_cau['yeu_cau_ai']
    _khoa(nguon, 'engine nang_luc nha_cung_cap model trang_thai hoan_tat')
    _khoa(nguon['hoan_tat'], 'giao_thuc ket_thuc')
    if (nguon['engine'] != 'e_hoi_ai' or nguon['nang_luc'] != NANG_LUC_AI
            or nguon['nha_cung_cap'] != 'local' or nguon['trang_thai'] != 'XONG'
            or nguon['model'] != ai['model'] or ai['model'] != snapshot['bien_nhan']['model']
            or nguon['hoan_tat']['giao_thuc'] not in {'ollama', 'openai_compatible'}
            or nguon['hoan_tat']['ket_thuc'] != 'stop'
            or ai['nha_cung_cap'] != 'local'
            or json_chuan(ai['chuyen_tiep']) != json_chuan(y['chuyen_tiep'])
            or ai['chuyen_tiep']['mask_2c']['nha_cung_cap_bat_buoc'] != 'local'
            or ai['bam_dau_vao'] != bam_bytes(json_chuan(yeu_cau))
            or ai['ma_prompt'] != y['ma_prompt'] or ai['phien_ban_prompt'] != y['phien_ban_prompt']
            or ai['kiem_trich_dan'] != {'dat': True, 'loi': []} or ai['canh_bao'] != []):
        raise loi('MASK_AI_NGUON')
    if len(json_chuan(phan_hoi)) > cb.profile()['json_phan_hoi_toi_da']:
        raise loi('MASK_AI_QUA_GIOI_HAN')
    phong_bi._kiem_schema(deepcopy(ai['du_lieu']), snapshot['khuon'])
    cac = ai['du_lieu']['thuc_the']
    if ai['trang_thai'] != ('co_can_cu' if cac else 'khong_thay_can_cu'):
        raise loi()
    trich = []
    for t in cac:
        a, b = t['bat_dau'], t['ket_thuc']
        if not 0 <= a < b <= len(y['tai_lieu']) or y['tai_lieu'][a:b] != t['nguyen_van']:
            raise loi()
        trich.append(dict(cau=t['nguyen_van'], bat_dau=a, ket_thuc=b))
    if json_chuan(ai['trich_dan']) != json_chuan(trich):
        raise loi()
    return cac


def _bien_thuc_the(m, a, b):
    """Kiểm biên trên bản dò và cụm Unicode gốc, không cắt NFD/Cf nối từ.

    Cf/selector được bỏ cả ngoài alias bởi chính map; cho phép chúng nằm
    trong span, kể cả cuối tên, nhưng không biến prefix của một từ thành tên.
    """
    chu = bo_ky_tu_vo_hinh(m.goc[a:b])
    vung = m.chuyen('goc', 'ban_do', a, b)
    return (la_bien_to_hop(m.goc, a) and la_bien_to_hop(m.goc, b)
            and len(vung) == 1 and vung[0][0] < vung[0][1]
            and _bien_doan(m.ban_do, vung[0][0]) and _bien_doan(m.ban_do, vung[0][1])
            and bool(chu) and chu[0].isalnum()
            and (chu[-1].isalnum() or unicodedata.category(chu[-1]).startswith('M')))


class HauKiemAI:
    def __init__(self, *, ngan, quyen, cong, phien_ban_engine, ram=None):
        self.quyen, self.cong, self.ram = quyen, cong, ram
        self.phien_ban_engine = phien_ban_engine
        self.con_sot = []  # Chỉ nhóm/vị trí/lý do, không phát hành trường này.

    def _ctx(self, viec, ma):
        ctx = xac_minh(self.quyen, viec, loai='che', ma_yeu_cau=ma, thao_tac='hau_kiem_ai')
        pn = viec.ngu_canh.get('phap_nhan_id')
        if self.cong is None or type(pn) is not str or not pn.strip():
            raise loi('MASK_AI_CHUA_CO_CUA_CORE')
        return ctx, dict(ma_yeu_cau=ctx.ma_yeu_cau, phien=ctx.phien, module=ctx.module,
                         nguoi_gui=ctx.nguoi_gui, tai_lieu=ctx.tai_lieu, vung=ctx.vung, phap_nhan_id=pn)

    def _kiem_ctx(self, viec):
        self.buoc.kiem()
        if (self._ctx(viec, self.ctx.ma_yeu_cau) != (self.ctx, self.danh_tinh)
                or bam_bytes(json_chuan(viec.dau_vao)) != self.bam_dau_vao):
            raise loi('MASK_AI_NGUON')

    def _goi(self, ten, viec, **kw):
        self._kiem_ctx(viec)
        ham = getattr(self.cong, ten, None)
        if not callable(ham):
            raise loi('MASK_AI_CHUA_CO_CUA_CORE')
        try:
            ket = ham(viec, self.ctx, **kw)
        except (TimeoutError, ConnectionError):
            if ten == 'ban_giao':
                # Lệnh ghi có thể đã được Core nhận; không báo lỗi xác định
                # hoặc tự gọi lại khi chưa biết ACK. Core tra cùng dấu này.
                raise ChuaRo('mask-ai-' + bam_bytes(json_chuan(self.danh_tinh))[7:]) from None
            raise
        self._kiem_ctx(viec)
        if ten == 'nhan_phan_hoi':
            return ket
        if ket is not True:
            raise loi('MASK_AI_NGUON')

    def _chan(self, a, b, loai, ly_do):
        self.con_sot.append(dict(nhom=NHOM[loai], vi_tri=dict(bat_dau=a, ket_thuc=b), ly_do=ly_do))
        raise loi('MASK_AI_CON_SOT')

    def _span(self, h, cac_doan, *, kiem=lambda: None):
        goc, m = h.anh_xa.goc, h.anh_xa
        theo_span, o_doan = {}, []
        for d, cac in zip(h.ke_hoach, cac_doan):
            kiem()
            trong_doan = set()
            for t in cac:
                a, b = d.bat_dau + t['bat_dau'], d.bat_dau + t['ket_thuc']
                k = (a, b)
                moc = (t['loai'], t['muc'])
                if k in theo_span and theo_span[k] != moc:
                    self._chan(a, b, t['loai'], 'Các đoạn nhận diện mâu thuẫn.')
                theo_span[k] = moc
                trong_doan.add(k)
            o_doan.append(trong_doan)
        cac = sorted(theo_span)
        for i, (a, b) in enumerate(cac):
            kiem()
            loai, muc = theo_span[a, b]
            if i and a < cac[i - 1][1]:
                self._chan(a, b, loai, 'Các khoảng nhận diện chồng lấn.')
            # Một đoạn phủ trọn span phải xác nhận cùng span; không bỏ qua
            # mảng rỗng trái với đoạn lân cận hoặc span chạm mép chưa đủ bao.
            bao_du = False
            for j, d in enumerate(h.ke_hoach):
                noi = (d.bat_dau < a or a == 0) and (b < d.ket_thuc or b == len(goc))
                if d.bat_dau <= a < b <= d.ket_thuc and noi:
                    if (a, b) not in o_doan[j]:
                        self._chan(a, b, loai, 'Các đoạn chưa xác nhận cùng khoảng.')
                    bao_du = True
            if not bao_du:
                self._chan(a, b, loai, 'Chưa có đoạn bao đầy đủ định danh.')
        moi = []
        bao_ve = che._vung_tien_ngay(goc)
        for a, b in cac:
            kiem()
            loai, muc = theo_span[a, b]
            if m.da_che_tron(a, b):
                continue
            if (muc != 'chac' or not _bien_thuc_the(m, a, b)
                    or bao_ve.hit(a, b)
                    or any(p.loai == 'thay_bi_danh' and a < p.goc[1] and p.goc[0] < b
                           for p in m.goc_che)
                    or any(a < p.end() and p.start() < b for p in che._VUNG_BI_DANH.finditer(goc))):
                self._chan(a, b, loai, 'Chưa chắc biên, loại hoặc vùng cần bảo toàn.')
            try:
                che._kiem_dinh_danh([dict(gia_tri=goc[a:b], nhom=NHOM[loai])])
            except che.LoiCheVanBan:
                self._chan(a, b, loai, 'Định danh chưa đủ điều kiện che thêm.')
            dich = m.chuyen('goc', 'da_che', a, b)
            if len(dich) != 1 or not dich[0][0] < dich[0][1]:
                self._chan(a, b, loai, 'Không ánh xạ được khoảng cần che.')
            u, v = dich[0]
            if m.da_che[u:v] != bo_ky_tu_vo_hinh(goc[a:b]):
                self._chan(a, b, loai, 'Khoảng đã bị thay đổi hoặc che một phần.')
            moi.append((a, b, u, v, NHOM[loai]))
        return moi

    def _tra_ung_vien_ram(self, luot, moi):
        """Sau _span/nguồn Local tin cậy: cùng budget và map với lớp 1.

        Chỉ nhận tọa độ; TraCuu lấy tên tại đầu vào RAM, không dùng tên
        model trả hoặc đọc lại danh mục. R5 nối đời sống luot xuyên bước.
        """
        for a, b, _u, _v, nhom in moi:
            luot.them(UngVien(a, b, nhom, 'local'))
        return luot.ket_qua()

    def _che_them(self, kho, h, snapshot, moi):
        """Cửa giao dịch lịch sử đã đóng; không rơi về kho bản rõ cũ."""
        chan_phat_hanh()

    def _che_them_ram(self, h, snapshot, moi, buoc):
        v = buoc.du_lieu
        luot = v['luot_ung_vien']
        # R3 giữ cùng budget/tập ứng viên trong RAM; thay callback/việc
        # ngay trong quyền sở hữu bước mới, không giữ handle cũ khi chờ.
        luot._kiem_huy = buoc.kiem
        luot._kho = KhoDinhDanh(quyen=self.quyen).mo_kho_nhan_dien(viec=self.viec)
        for a, b, _u, _v, nhom in moi:
            luot.them(UngVien(a, b, nhom, 'local'))
            if luot._da_tim[che.chuan_hoa(h.anh_xa.goc[a:b])][1] is None:
                # Chưa có bảo đảm duy nhất tên mới C-P4-03: tuyệt đối
                # không gọi kho RAM cũ hoặc ghi bản rõ vào metadata.
                chan_phat_hanh()
        do = luot.ket_qua()
        cu = {(p.goc[0], p.goc[1], h.anh_xa.da_che[slice(*p.dich)])
              for p in h.anh_xa.goc_che if p.loai == 'thay_bi_danh'}
        if not cu <= set(do.phep_thay):
            raise loi('MASK_AI_CON_SOT')
        kq, m, aliases = cb.ket_qua_ram(self.ctx.ma_yeu_cau, h.anh_xa.goc, do.phep_thay, buoc=buoc)
        kq['bi_danh'] = [dict(bi_danh=a, nhom=nh, nguon='chinh_thuc')
                          for a, _g, nh in luot._alias.values() if a in aliases]
        if any(aliases.get(a) != g for a, g in v['alias_nguyen_van'].items()):
            raise loi('MASK_AI_CON_SOT')
        buoc.du_lieu.update(alias_nguyen_van=aliases, anh_xa_cuoi=m)
        return kq

    @_bao_ve
    def hau_kiem(self, viec):
        with kiem_kho_ram(self.ram).buoc(viec, loai='che') as buoc:
            self.buoc, self.viec = buoc, viec
            try:
                return self._hau_kiem(viec, buoc)
            finally:
                luot = buoc._ban_ghi.du_lieu.get('luot_ung_vien')
                nhuong_luot(luot)
                self.buoc = self.viec = None

    def _hau_kiem(self, viec, buoc):
        dau_vao = deepcopy(viec.dau_vao)
        self.bam_dau_vao = bam_bytes(json_chuan(dau_vao))
        ai = phong_bi.doc_hau_kiem_ai(dau_vao)
        meta = ai['chuyen_tiep']['mask_2c']
        ma = meta['ma_yeu_cau']
        self.ctx, self.danh_tinh = self._ctx(viec, ma)
        if self.danh_tinh['phap_nhan_id'] != buoc._ctx.phap_nhan_id:
            raise loi('MASK_AI_NGUON')
        s, dau = du_lieu_ram(buoc)
        h = cb._kiem_snapshot(s)
        v = buoc.du_lieu
        if (v.get('giai_doan_ai') != 'CHO_LOCAL'
                or s['ket_qua_quy_tac']['ma_yeu_cau'] != ma
                or set(v['da_giao']) != set(range(len(h.ke_hoach)))
                or meta['ma_ho_so_ram'] != dau.ma_ho_so_ram
                or meta['bam_ho_so'] != dau.bam_ho_so):
            raise loi('MASK_AI_NGUON')
        # Chỉ nguồn Local chưa rõ được giữ RAM; mọi lỗi xác định hoặc
        # ChuaRo sau khi đã kết thúc xử lý/chốt đều dọn, không phát hành.
        try:
            raw = self._goi('nhan_phan_hoi', viec, dau=dau, bam_dau_vao=self.bam_dau_vao)
            bundle = _json(raw, GIOI_HAN_HO_SO)
            _khoa(bundle, 'phien_ban ma_yeu_cau phan_hoi')
            if (type(bundle['phien_ban']) is not int or bundle['phien_ban'] != 1
                    or bundle['ma_yeu_cau'] != ma or type(bundle['phan_hoi']) is not list
                    or len(bundle['phan_hoi']) != len(h.ke_hoach)):
                raise loi('MASK_AI_NGUON')
            buoc.du_lieu['phan_hoi_local'] = bundle
            chung = []
            for i, phan in enumerate(bundle['phan_hoi']):
                buoc.kiem()
                _khoa(phan, 'tra_loi_ai nguon')
                yc = cb.yeu_cau_cho_doan(s, dau, i)
                if v['da_giao'][i] != bam_bytes(json_chuan(yc)):
                    raise loi('MASK_AI_NGUON')
                # Chứng thực có thể trả ChuaRo trước khi diễn giải AI.
                # Chỉ nhãn kỹ thuật an toàn đi qua cửa chứng thực, không
                # cho nguon giả chèn nguyên văn/object lồng vào đề nghị.
                nguon = phan['nguon']
                _khoa(nguon, 'engine nang_luc nha_cung_cap model trang_thai hoan_tat')
                _khoa(nguon['hoan_tat'], 'giao_thuc ket_thuc')
                if any(type(n) is not str or not re.fullmatch(r'[A-Za-z0-9_.:@-]{1,100}', n)
                       for n in [*(nguon[k] for k in nguon if k != 'hoan_tat'),
                                 *nguon['hoan_tat'].values()]):
                    raise loi('MASK_AI_NGUON')
                chung.append(dict(chi_so_doan=i, bam_yeu_cau=bam_bytes(json_chuan(yc)),
                                  bam_phan_hoi=bam_bytes(json_chuan(phan['tra_loi_ai'])), nguon=phan['nguon']))
            if json_chuan(bundle['phan_hoi'][-1]['tra_loi_ai']) != json_chuan(dau_vao):
                raise loi('MASK_AI_NGUON')
            de_nghi = json_chuan(dict(phien_ban=1, danh_tinh=self.danh_tinh,
                                      ma_ho_so_ram=dau.ma_ho_so_ram, bam_ho_so=dau.bam_ho_so,
                                      bam_tap_phan_hoi=bam_bytes(raw), bam_dau_vao=self.bam_dau_vao,
                                      phan_hoi=chung))
            self._goi('kiem_han', viec, bien_nhan=deepcopy(s['bien_nhan']))
            self._goi('chung_thuc', viec, de_nghi=de_nghi)
        except ChuaRo:
            buoc.cho_ai()
            raise
        cac_doan = []
        for i, phan in enumerate(bundle['phan_hoi']):
            buoc.kiem()
            yc = cb.yeu_cau_cho_doan(s, dau, i)
            cac_doan.append(_kiem_phan_hoi(yc, phan['tra_loi_ai'], phan['nguon'], s))
        tai_nguyen.nap_tu_goi()
        moi = self._span(h, cac_doan, kiem=buoc.kiem)
        viec.tien_do(25, 'Đang hậu kiểm và che bổ sung định danh.')
        kq = self._che_them_ram(h, s, moi, buoc)
        ket = phong_bi.ket_qua_che(kq, h.anh_xa.goc, phien_ban_engine=self.phien_ban_engine)
        chung_cu = json_chuan(dict(phien_ban=1, nang_luc=NANG_LUC,
                                  bam_nguon=bam_bytes(de_nghi), bam_ket_qua=bam_bytes(json_chuan(ket)),
                                  bam_van_ban=bam_chu(ket['van_ban_da_che']['van_ban']),
                                  so_doan=len(h.ke_hoach), kiem_tien_ngay=True))
        self._goi('kiem_han', viec, bien_nhan=deepcopy(s['bien_nhan']))
        self._goi('chung_thuc', viec, de_nghi=de_nghi)
        self._goi('ban_giao', viec, chung_cu=chung_cu, ket_qua=json_chuan(ket))
        self._goi('kiem_han', viec, bien_nhan=deepcopy(s['bien_nhan']))
        self._goi('chung_thuc', viec, de_nghi=de_nghi)
        du_lieu_ram(buoc)
        buoc.du_lieu['giai_doan_ai'] = 'DA_HAU_KIEM'
        # Phản hồi chứa nguyên văn không cần sau hậu kiểm; alias/map còn
        # trong RAM cho bước mở cùng chu kỳ R6, giữ nguyên hạn tuyệt đối.
        buoc.du_lieu.pop('phan_hoi_local', None)
        viec.tien_do(100, 'Đã hậu kiểm toàn bộ tài liệu bằng AI cục bộ.')
        buoc.cho_ai()
        return ket
