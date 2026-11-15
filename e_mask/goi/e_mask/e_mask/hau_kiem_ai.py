"""Hậu kiểm Local: chỉ thêm che theo span, Core chứng thực nguồn và giữ tệp.

Port dưới đây là đề nghị tích hợp, KHÔNG phải API sẵn có của SDK 2.0.
Không có port/ACL/nguồn hoàn tất thì từ chối. Không gọi model/engine khác.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from functools import wraps
import json
import re
import unicodedata
from typing import Protocol

from kho_tri_thuc_sdk.engine import ChuaRo, LoiDuongTruyen, LoiNghiepVu, ViecDaHuy

from . import che_van_ban as che, chuan_bi_ai as cb, phong_bi, tai_nguyen
from .anh_xa_ai import bam_chu, kiem_anh_xa, tao_anh_xa
from .ho_so_ai import (DauHoSoAI, GIOI_HAN_HO_SO, ThamChieuHoSo, _bien_doan,
                       bam_bytes, doc_bytes, json_chuan)
from .kho_dinh_danh import KhoDinhDanh
from .ngan import NganXungDot
from .nguon.privacy.types import bo_ky_tu_vo_hinh, la_bien_to_hop
from .quyen_yeu_cau import xac_minh

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
            raise LoiDuongTruyen(exc.ma, http_status=exc.http_status,
                                thu_lai_duoc=exc.thu_lai_duoc) from None
        except NganXungDot:
            raise loi('MASK_AI_XUNG_DOT') from None
        except LoiNghiepVu as exc:
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
    """Port tin cậy được bên tích hợp tiêm, không đọc từ dữ liệu caller.

    Core kiểm ACL/lease/pháp nhân ngay trong mo_tep và từng thao tác này.
    chung_thuc chỉ true khi bytes/băm đề nghị khớp sổ nguồn Core bất biến:
    snapshot từ bước chuẩn bị, MỌI yêu cầu/đáp từ AI-9, API hoàn tất và bản
    giao cuối chỉ thêm tham chiếu tập phản hồi. Không tin nguon trong tệp.
    ban_giao ghi chứng cứ bước 3 + băm kết quả bền, chống lặp trước ACK.
    Chốt đã nhận chưa trả phải ChuaRo; quyền/lease sai thì dừng ngay.
    """
    def kiem_quyen(self, viec, ctx, *, tham_chieu, thao_tac) -> bool: ...
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


def _ref(v, ten):
    _khoa(v, 'tep_id ten mime kich_thuoc')
    if (type(v['tep_id']) is not str
            or re.fullmatch(r'[A-Za-z0-9_-][A-Za-z0-9_.:-]{0,199}', v['tep_id']) is None
            or v['ten'] != ten or v['mime'] != 'application/json'
            or type(v['kich_thuoc']) is not int or not 0 < v['kich_thuoc'] <= GIOI_HAN_HO_SO):
        raise loi('MASK_AI_HO_SO')
    return ThamChieuHoSo(**v)


def _bam(v):
    if type(v) is not str or re.fullmatch(r'sha256:[0-9a-f]{64}', v) is None:
        raise loi('MASK_AI_HO_SO')
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
    def __init__(self, *, ngan, quyen, cong, phien_ban_engine):
        self.ngan, self.quyen, self.cong = ngan, quyen, cong
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
        viec.kiem_huy()
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
        if ket is not True:
            raise loi('MASK_AI_NGUON')

    def _doc(self, viec, ref, bam):
        self._goi('kiem_quyen', viec, tham_chieu=ref, thao_tac='doc_hau_kiem_ai')
        # Chỉ mo_tep của SDK, không đường máy/URL/đọc kho engine khác.
        with viec.mo_tep(ref.tep_id) as f:
            raw = f.read(GIOI_HAN_HO_SO + 1)
        if type(raw) is not bytes or len(raw) != ref.kich_thuoc or bam_bytes(raw) != _bam(bam):
            raise loi('MASK_AI_HO_SO')
        self._goi('kiem_quyen', viec, tham_chieu=ref, thao_tac='doc_hau_kiem_ai')
        return raw

    def _chan(self, a, b, loai, ly_do):
        self.con_sot.append(dict(nhom=NHOM[loai], vi_tri=dict(bat_dau=a, ket_thuc=b), ly_do=ly_do))
        raise loi('MASK_AI_CON_SOT')

    def _span(self, h, cac_doan):
        goc, m = h.anh_xa.goc, h.anh_xa
        theo_span, o_doan = {}, []
        for d, cac in zip(h.ke_hoach, cac_doan):
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

    def _che_them(self, kho, h, snapshot, moi):
        ma, m = self.ctx.ma_yeu_cau, h.anh_xa
        with kho.giao_dich():
            kho.doc_yeu_cau(ma)
            kq = deepcopy(snapshot['ket_qua_quy_tac'])
            da_dung = {v['bi_danh']: v for v in kq['bi_danh']}
            phep = [(p.goc[0], p.goc[1], m.da_che[slice(*p.dich)])
                    for p in m.goc_che if p.loai == 'thay_bi_danh']
            da_che, so_moi = m.da_che, 0
            # Offset trong bản quy tắc bất biến: thay PHẢI → TRÁI.
            for a, b, u, v, nhom in reversed(moi):
                gia_tri = bo_ky_tu_vo_hinh(m.goc[a:b])
                muc = kho.tra_bi_danh(che.chuan_hoa(gia_tri))
                if muc is not None and muc['nhom'] != nhom:
                    raise loi('MASK_AI_CON_SOT')
                if muc is None:
                    muc, tao = kho.ghi_cho_duyet(gia_tri, nhom, kho.cap_bi_danh_tam(), ma)
                    so_moi += int(tao)
                if muc['nhom'] != nhom or muc['nguon'] not in {'tam', 'chinh_thuc'}:
                    raise loi('MASK_AI_CON_SOT')
                if muc['nguon'] == 'tam':
                    kho.ghi_nhan_gap_lai(ma, che.chuan_hoa(gia_tri), nhom)
                alias = muc['bi_danh']
                da_dung[alias] = dict(bi_danh=alias, nhom=nhom, nguon=muc['nguon'])
                da_che = da_che[:u] + alias + da_che[v:]
                phep.append((a, b, alias))
            map_cuoi = tao_anh_xa(m.goc, sorted(phep))
            kiem_anh_xa(map_cuoi)
            if map_cuoi.da_che != da_che:
                raise loi('MASK_AI_HO_SO')
            # Giữ mọi alias lớp 1 nguyên vị trí tương ứng, không cho AI sửa/gỡ.
            tat_ca = [(t['gia_tri'], t['nhom'], t['nhom'] != 'KHAC')
                      for t in kho.liet_ke_dinh_danh()]
            con_sot, day_du = che._kiem_con_sot(da_che, tat_ca)
            tien_ngay = che._kiem_tien_ngay(m.goc, da_che)
            so_sanh = []
            cuoi = 0
            for a, b, _ in sorted(phep):
                so_sanh.extend((bo_ky_tu_vo_hinh(m.goc[cuoi:a]), '\x00'))
                cuoi = b
            so_sanh.append(bo_ky_tu_vo_hinh(m.goc[cuoi:]))
            tien_ngay = tien_ngay and not che.core.numeric_review(
                ''.join(so_sanh), che._an_bi_danh(da_che), [])['changed']
            if con_sot or not day_du or not tien_ngay:
                self.con_sot.extend(con_sot)
                raise loi('MASK_AI_CON_SOT')
            kho.ghi_bi_danh_da_dung(ma, list(da_dung))
            kq.update(van_ban_da_che=da_che, con_sot=[], kiem_tien_ngay=True, gui_duoc=True,
                      so_cho_thay=kq['so_cho_thay'] + len(moi), bi_danh=list(da_dung.values()),
                      cho_duyet={'so_cum_vua_them': kq['cho_duyet']['so_cum_vua_them'] + so_moi})
            phong_bi.ket_qua_che(kq, m.goc)
            return kq

    @_bao_ve
    def hau_kiem(self, viec):
        dau_vao = deepcopy(viec.dau_vao)
        self.bam_dau_vao = bam_bytes(json_chuan(dau_vao))
        ai = phong_bi.doc_hau_kiem_ai(dau_vao)
        meta = ai['chuyen_tiep']['mask_2c']
        ma = meta['ma_yeu_cau']
        self.ctx, self.danh_tinh = self._ctx(viec, ma)
        ref = _ref(meta['ho_so'], 'mask-2c-ho-so.json')
        tap = _ref(meta['tap_phan_hoi'], 'mask-2c-phan-hoi.json')
        raw = self._doc(viec, ref, meta['bam_ho_so'])
        raw_tap = self._doc(viec, tap, meta['bam_tap_phan_hoi'])
        s = cb.doc_snapshot(raw)
        h = doc_bytes(json_chuan(s['quy_tac']))
        bundle = _json(raw_tap, GIOI_HAN_HO_SO)
        _khoa(bundle, 'phien_ban ma_yeu_cau ke_hoach phan_hoi')
        if (type(bundle['phien_ban']) is not int or bundle['phien_ban'] != 1
                or bundle['ma_yeu_cau'] != ma or s['ket_qua_quy_tac']['ma_yeu_cau'] != ma
                or s['ket_qua_quy_tac']['gui_duoc'] is not True
                or json_chuan(bundle['ke_hoach']) != json_chuan([asdict(d) for d in h.ke_hoach])
                or type(bundle['phan_hoi']) is not list or len(bundle['phan_hoi']) != len(h.ke_hoach)):
            raise loi('MASK_AI_NGUON')
        dau = DauHoSoAI(ref, bam_bytes(raw))
        chung = []
        for i, phan in enumerate(bundle['phan_hoi']):
            viec.kiem_huy()
            _khoa(phan, 'yeu_cau_ai tra_loi_ai nguon')
            chung.append(dict(chi_so_doan=i, bam_yeu_cau=bam_bytes(json_chuan(phan['yeu_cau_ai'])),
                              bam_phan_hoi=bam_bytes(json_chuan(phan['tra_loi_ai'])), nguon=phan['nguon']))
        cuoi = deepcopy(bundle['phan_hoi'][-1]['tra_loi_ai'])
        cuoi['tra_loi_ai']['chuyen_tiep']['mask_2c'].update(
            tap_phan_hoi=asdict(tap), bam_tap_phan_hoi=bam_bytes(raw_tap))
        if json_chuan(cuoi) != json_chuan(dau_vao):
            raise loi('MASK_AI_NGUON')
        de_nghi = json_chuan(dict(phien_ban=1, danh_tinh=self.danh_tinh,
                                  ho_so=asdict(ref), bam_ho_so=bam_bytes(raw),
                                  tap_phan_hoi=asdict(tap), bam_tap_phan_hoi=bam_bytes(raw_tap),
                                  bam_dau_vao=bam_bytes(json_chuan(dau_vao)), phan_hoi=chung))
        def kiem_chot():
            self._goi('kiem_han', viec, bien_nhan=deepcopy(s['bien_nhan']))
            self._goi('chung_thuc', viec, de_nghi=de_nghi)
        kiem_chot()
        # Chứng thực trước khi hiểu trạng thái AI: nếu nguồn đã nhận nhưng
        # chưa trả, port phải ChuaRo, không biến payload rỗng thành an toàn.
        cac_doan = []
        for i, phan in enumerate(bundle['phan_hoi']):
            viec.kiem_huy()
            yc = cb.yeu_cau_cho_doan(s, dau, i)
            if json_chuan(phan['yeu_cau_ai']) != json_chuan(yc):
                raise loi('MASK_AI_NGUON')
            cac_doan.append(_kiem_phan_hoi(yc, phan['tra_loi_ai'], phan['nguon'], s))
        tai_nguyen.nap_tu_goi()
        moi = self._span(h, cac_doan)
        viec.tien_do(25, 'Đang hậu kiểm và che bổ sung định danh.')
        kho = KhoDinhDanh(ngan=self.ngan, quyen=self.quyen)
        kq = kho.xu_ly_hau_kiem_ai(viec, lambda k: self._che_them(k, h, s, moi),
                                  ma_yeu_cau=ma, kiem_chot=kiem_chot)
        ket = phong_bi.ket_qua_che(kq, h.anh_xa.goc, phien_ban_engine=self.phien_ban_engine)
        chung_cu = json_chuan(dict(phien_ban=1, nang_luc=NANG_LUC,
                                  bam_nguon=bam_bytes(de_nghi), bam_ket_qua=bam_bytes(json_chuan(ket)),
                                  bam_van_ban=bam_chu(ket['van_ban_da_che']['van_ban']),
                                  so_doan=len(h.ke_hoach), kiem_tien_ngay=True))
        self._goi('ban_giao', viec, chung_cu=chung_cu, ket_qua=json_chuan(ket))
        kiem_chot()
        viec.tien_do(100, 'Đã hậu kiểm toàn bộ tài liệu bằng AI cục bộ.')
        return ket
