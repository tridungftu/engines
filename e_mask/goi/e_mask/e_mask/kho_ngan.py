"""Kho định danh qua API ngăn chung. Không ghi tệp, không giữ tài liệu.

Một dòng CAS chung cho mỗi vùng bảo vệ snapshot nhiều bảng, gồm cả dọn và
duyệt. Dấu lượt chỉ giữ băm/số đếm và lựa chọn định danh để tái tạo khi giao
lại, không lưu văn bản hoặc kết quả AI. Mọi ghi nghiệp vụ trong cùng một lô.
"""
from copy import deepcopy
from functools import wraps
from hashlib import sha256
import json
from uuid import uuid4

from kho_tri_thuc_sdk.engine import ChuaRo, LoiDuongTruyen, LoiNghiepVu, ViecDaHuy

from .che_van_ban import chuan_hoa, chuan_bi_danh
from .ngan import CauHinhKhongHopLe, NganKhongHopLe, NganXungDot
from .quyen_yeu_cau import loi_kho, xac_minh


BANG = ('dinh_danh', 'bi_danh_tam', 'cho_duyet', 'ma_yeu_cau', 'dau_gap')
TIEN_TO = {'CONG_TY': 'MASKCT', 'CA_NHAN': 'MASKCN', 'DIA_CHI': 'MASKDC',
           'MA_SO_THUE': 'MASKMST', 'TAI_KHOAN': 'MASKTK'}
CAC_TIEN_TO = frozenset((*TIEN_TO.values(), 'MASKKHAC', 'MASKTAM'))
# Chỉ khai kho RAM nội bộ; không khai ngan_du_lieu/migration trong engine.json.
KHAI_NGAN = [dict(bang=bang, pham_vi='engine', khoa=['vung', 'khoa'],
                  duy_nhat=[['vung', 'bi_danh']] if bang in BANG[:3] else [])
             for bang in BANG]


def khoa_dau(*phan):
    return json.dumps(phan, ensure_ascii=True, separators=(',', ':'))


def khoa_muc(vung, khoa):
    return {'vung': vung, 'khoa': khoa}


def bi_danh_moi(nhom):
    return '[[' + TIEN_TO.get(nhom, 'MASKKHAC') + '-' + uuid4().hex + ']]'


def _bam_ket_qua(kq):
    return sha256(json.dumps(kq, sort_keys=True, ensure_ascii=True,
                             allow_nan=False, separators=(',', ':')).encode()).hexdigest()


def bao_ve_loi_ngan(ham):
    """Chặn thông điệp ngoại lệ của ngăn trước khi SDK có thể in traceback."""
    @wraps(ham)
    def goi(*args, **kwargs):
        try:
            return ham(*args, **kwargs)
        except (ChuaRo, ViecDaHuy, LoiDuongTruyen):
            raise
        except NganXungDot:
            raise loi_kho('MASK_XUNG_DOT') from None
        except (NganKhongHopLe, CauHinhKhongHopLe) as exc:
            lop = type(exc)
            raise LoiNghiepVu(lop.ma, lop.thong_diep, thu_lai_duoc=lop.thu_lai_duoc) from None
        except LoiNghiepVu as exc:
            # Ngăn tương lai có thể ném ngay LoiNghiepVu. Không coi câu của
            # bên ngoài là an toàn chỉ vì ngoại lệ đã mang kiểu nghiệp vụ.
            if exc.ma == 'MASK_QUA_GIOI_HAN':
                raise LoiNghiepVu('MASK_QUA_GIOI_HAN', 'Số thay đổi vượt giới hạn một giao dịch. Cần chia nhỏ yêu cầu.') from None
            raise loi_kho(exc.ma) from None
        except Exception:
            raise loi_kho() from None
    return goi


def doc_het(ngan, bang, vung):
    ds, tiep = {}, None
    while True:
        trang = ngan.tim(bang, loc={'vung': vung}, gioi_han=500, tiep=tiep)
        for muc in trang.danh_sach:
            ds[muc.gia_tri['khoa']] = muc
        tiep = trang.tiep
        if tiep is None:
            return ds


class AnhNgan:
    """Đọc trước CAS chung; nếu snapshot đổi thì lô chốt bị từ chối toàn bộ."""
    @bao_ve_loi_ngan
    def __init__(self, ngan, vung):
        self.ngan, self.vung = ngan, vung
        khoa = khoa_muc(vung, 'phien')
        if ngan.doc('dau_gap', khoa) is None:
            with ngan.lo() as lo:
                lo.lay_hoac_tao('dau_gap', khoa, {'so': 0})
        self.phien = ngan.doc('dau_gap', khoa)
        self.cu = {b: doc_het(ngan, b, vung) for b in BANG}
        self.moi = {b: {k: deepcopy(m.gia_tri) for k, m in ds.items()} for b, ds in self.cu.items()}

    def dat(self, bang, khoa, gia_tri):
        self.moi[bang][khoa] = dict(deepcopy(gia_tri), **khoa_muc(self.vung, khoa))

    @bao_ve_loi_ngan
    def chot(self):
        lenh = []
        for b in BANG:
            for k in self.cu[b].keys() | self.moi[b].keys():
                if b == 'dau_gap' and k == 'phien':
                    continue
                cu, moi = self.cu[b].get(k), self.moi[b].get(k)
                if cu is not None and cu.gia_tri == moi:
                    continue
                lenh.append((b, k, cu, moi))
        # sua là bản vá: bỏ trường phải xóa/tạo lại trong cùng lô có CAS.
        so_lenh = sum(2 if cu is not None and moi is not None
                      and cu.gia_tri.keys() - moi.keys() else 1
                      for _, _, cu, moi in lenh)
        if so_lenh + 1 > 100:
            raise LoiNghiepVu('MASK_QUA_GIOI_HAN', 'Số thay đổi vượt giới hạn một giao dịch. Cần chia nhỏ yêu cầu.')
        try:
            with self.ngan.lo() as lo:
                lo.sua('dau_gap', khoa_muc(self.vung, 'phien'),
                       {'so': self.phien.gia_tri['so'] + 1}, row_version=self.phien.row_version)
                for b, k, cu, moi in lenh:
                    khoa = khoa_muc(self.vung, k)
                    if cu is None:
                        lo.them(b, khoa, moi)
                    elif moi is None:
                        lo.xoa(b, khoa, row_version=cu.row_version)
                    elif cu.gia_tri.keys() - moi.keys():
                        lo.xoa(b, khoa, row_version=cu.row_version)
                        lo.them(b, khoa, moi)
                    else:
                        lo.sua(b, khoa, moi, row_version=cu.row_version)
        except NganXungDot:
            raise loi_kho('MASK_XUNG_DOT') from None


class DauNgan:
    """Dấu phục hồi của port MASK-3, cùng ngăn; không chứa tên/tài liệu."""
    def __init__(self, ngan):
        self.ngan = ngan

    @bao_ve_loi_ngan
    def ghi(self, *, vung, ma_luot, ma_yeu_cau, bam_dau_vao, trang_thai=1, bam_chot=None):
        tuong_quan = sha256(json.dumps([vung, ma_luot], ensure_ascii=True).encode()).hexdigest()
        khoa = khoa_muc(vung, khoa_dau('phuc_hoi', tuong_quan))
        cu = self.ngan.doc('dau_gap', khoa)
        moi = dict(yeu_cau=sha256(ma_yeu_cau.encode()).hexdigest(), dau_vao=bam_dau_vao,
                   chot=bam_chot or '0' * 64, tuong_quan=tuong_quan, trang_thai=trang_thai)
        if cu:
            if any(cu.gia_tri[k] != moi[k] for k in ('yeu_cau', 'dau_vao')):
                raise loi_kho('MASK_XUNG_DOT')
            if trang_thai == 1 or cu.gia_tri['trang_thai'] == 4:
                return deepcopy(cu.gia_tri)
            if bam_chot is None:
                moi['chot'] = cu.gia_tri['chot']
        try:
            with self.ngan.lo() as lo:
                if cu:
                    lo.sua('dau_gap', khoa, moi, row_version=cu.row_version)
                else:
                    lo.them('dau_gap', khoa, moi)
        except NganXungDot:
            raise loi_kho('MASK_XUNG_DOT') from None
        return deepcopy(moi)


class PortNgan:
    """Adapter snapshot/chốt cho lõi MASK-3, chỉ dùng API Ngan công bố."""
    def __init__(self, ngan, quyen, viec, *, loai, ma_yeu_cau, bam_dau_vao):
        self.ngan, self.quyen, self.viec = ngan, quyen, viec
        self.loai, self.ma, self.bam = loai, ma_yeu_cau, bam_dau_vao
        self.ctx = xac_minh(quyen, viec, loai=loai, ma_yeu_cau=ma_yeu_cau)
        self.anh = None

    def _kiem(self, thao_tac):
        ctx = xac_minh(self.quyen, self.viec, loai=self.loai, ma_yeu_cau=self.ctx.ma_yeu_cau,
                       thao_tac=thao_tac)
        if ctx != self.ctx:
            raise loi_kho('MASK_NGU_CANH_CHUA_XAC_MINH')
        return ctx

    def __call__(self, thao_tac, *, ma_yeu_cau, ma_luot, loai, **p):
        try:
            return self._goi(thao_tac, ma_yeu_cau, ma_luot, loai, p)
        except NganXungDot:
            raise loi_kho('MASK_XUNG_DOT') from None

    def _goi(self, thao_tac, ma, luot, loai, p):
        ctx = self._kiem('snapshot' if thao_tac == 'snapshot_luot' else 'chot')
        if (ma, luot, loai) != (ctx.ma_yeu_cau, ctx.ma_luot, self.loai):
            raise loi_kho('MASK_MA_YEU_CAU')
        if thao_tac == 'snapshot_luot':
            self.anh = AnhNgan(self.ngan, ctx.vung)
        anh, yc_khoa = self.anh, ma
        dl = anh.moi
        yc = dl['ma_yeu_cau'].get(yc_khoa)
        da_chot = dl['dau_gap'].get(khoa_dau('luot', luot))
        if yc and any(yc[k] != getattr(ctx, k) for k in ('module', 'nguoi_gui', 'tai_lieu')):
            raise loi_kho('MASK_MA_YEU_CAU')
        if da_chot and (da_chot['bam'] != self.bam or da_chot['ma_yeu_cau'] != ma or da_chot['loai'] != loai):
            raise loi_kho('MASK_XUNG_DOT')
        if (loai == 'mo_che' and yc is None) or (yc and yc['trang_thai'] != 'DANG_XU_LY' and not da_chot):
            raise loi_kho('MASK_MA_YEU_CAU')
        if thao_tac == 'snapshot_luot':
            danh_muc = list(dl['dinh_danh'].values()) + list(dl['cho_duyet'].values())
            tam_duoc_dung = {m['bi_danh'] for m in dl['dau_gap'].values()
                            if m.get('loai_dau') == 'tham_chieu' and m.get('ma_yeu_cau') == ma}
            bo_sung = {k: m['gia_tri'] for k, m in dl['bi_danh_tam'].items() if k in tam_duoc_dung}
            tam_theo_cum = {chuan_hoa(m['gia_tri']): m for b, m in dl['bi_danh_tam'].items() if b in tam_duoc_dung}
            # Một cụm chờ có thể đã được che trong nhiều yêu cầu bằng các mã
            # tạm khác nhau. Chỉ chọn lại mã đã sinh cho yêu cầu hiện tại.
            for i, muc in enumerate(danh_muc):
                if muc['nguon'] == 'tam':
                    rieng = tam_theo_cum.get(chuan_hoa(muc['gia_tri']))
                    if rieng:
                        danh_muc[i] = dict(muc, bi_danh=rieng['bi_danh'])
            # Giao lại dùng đúng lựa chọn đã chốt; duyệt/dọn không đổi kết quả cũ.
            if da_chot:
                chon = [m for m in dl['dau_gap'].values() if m.get('loai_dau') == 'lua_chon' and m.get('ma_luot') == luot]
                danh_muc = [dict(m['dinh_danh']) for m in chon if m.get('de_che')]
                bo_sung = {chuan_bi_danh(m['dinh_danh']['bi_danh']): m['dinh_danh']['gia_tri']
                           for m in chon if chuan_bi_danh(m['dinh_danh']['bi_danh']) in tam_duoc_dung}
                if loai == 'mo_che':
                    danh_muc = list(dl['dinh_danh'].values())
            if yc and da_chot:
                yc = dict(yc, trang_thai='DANG_XU_LY')
            return dict(da_chot=False, phien_ban=anh.phien.row_version, yeu_cau=deepcopy(yc),
                        danh_muc=deepcopy(danh_muc), bi_danh_bo_sung=bo_sung,
                        bi_danh_tam_duoc_dung=sorted(tam_duoc_dung),
                        cum_cho_toan_vung={}, da_phuc_hoi=bool(da_chot))
        if thao_tac != 'chot_luot' or p.get('nhat_ky') is None or p.get('phien_ban') != anh.phien.row_version:
            raise loi_kho('MASK_XUNG_DOT')
        nk, kq = p['nhat_ky'], deepcopy(p['ket_qua'])
        if da_chot:
            if loai == 'che':
                kq['cho_duyet'] = {'so_cum_vua_them': da_chot['so_moi']}
            if _bam_ket_qua(kq) != da_chot['bam_ket_qua']:
                # Thay tài nguyên/logic không được âm thầm đổi kết quả đã chốt.
                raise loi_kho('MASK_XUNG_DOT')
            anh.chot()  # CAS bảo vệ cả lần đọc lại với quyền mới kiểm.
            return kq
        for muc in nk['cum']:
            khoa = chuan_hoa(muc['gia_tri'])
            hien = dl['dinh_danh'].get(khoa) or dl['cho_duyet'].get(khoa)
            b = chuan_bi_danh(muc['bi_danh'])
            if not muc['chi_gap_lai']:
                if muc['bi_danh'] not in nk['bi_danh_tam_moi'] or b in dl['bi_danh_tam']:
                    raise loi_kho('MASK_XUNG_DOT')
                for bang in ('dinh_danh', 'cho_duyet', 'bi_danh_tam'):
                    if any(b in {chuan_bi_danh(m['bi_danh']), chuan_bi_danh(m.get('bi_danh_tam') or '')}
                           for m in dl[bang].values()):
                        raise loi_kho('MASK_XUNG_DOT')
                tam = dict(gia_tri=muc['gia_tri'], nhom=muc['nhom'], bi_danh=muc['bi_danh'], nguon='tam')
                anh.dat('bi_danh_tam', b, tam)
            if hien is None:
                hien = dict(gia_tri=muc['gia_tri'], nhom=muc['nhom'], bi_danh=muc['bi_danh'],
                            nguon='tam', so_lan_gap=0)
                anh.dat('cho_duyet', khoa, hien)
            if hien['nhom'] != muc['nhom'] or (hien['nguon'] == 'chinh_thuc' and hien['bi_danh'] != muc['bi_danh']):
                raise loi_kho('MASK_XUNG_DOT')
            dau = khoa_dau('gap', ma, khoa)
            if hien['nguon'] == 'tam' and dau not in dl['dau_gap']:
                hien = dict(hien, so_lan_gap=hien['so_lan_gap'] + 1)
                anh.dat('cho_duyet', khoa, hien)
                anh.dat('dau_gap', dau, {'ma_yeu_cau': ma, 'cum': khoa})
        for bi_danh in set(nk['bi_danh_da_dung'] + nk['bi_danh_da_tra']):
            b = chuan_bi_danh(bi_danh)
            muc = next((m for bang in ('bi_danh_tam', 'dinh_danh', 'cho_duyet') for m in dl[bang].values()
                        if b in {chuan_bi_danh(m['bi_danh']), chuan_bi_danh(m.get('bi_danh_tam') or '')}), None)
            if muc is None:
                continue  # Bí danh lạ được báo bởi lõi, không đoán/ghi tham chiếu.
            if b in dl['bi_danh_tam']:
                ref = khoa_dau('tham_chieu', ma, b)
                moi = any(chuan_bi_danh(m) == b for m in nk['bi_danh_tam_moi'])
                if ref not in dl['dau_gap'] and not (loai == 'che' and moi):
                    if bi_danh not in nk['bi_danh_da_dung']:
                        continue  # Tra hụt bí danh tạm khác yêu cầu: không nhận tham chiếu.
                    raise loi_kho('MASK_MA_YEU_CAU')
                anh.dat('dau_gap', khoa_dau('tham_chieu', ma, b),
                        {'loai_dau': 'tham_chieu', 'ma_yeu_cau': ma, 'bi_danh': b})
            chon = {k: deepcopy(muc[k]) for k in ('gia_tri', 'nhom', 'bi_danh', 'nguon')}
            if loai == 'mo_che':
                chon['bi_danh'] = bi_danh
            anh.dat('dau_gap', khoa_dau('lua_chon', luot, b),
                    {'loai_dau': 'lua_chon', 'ma_luot': luot, 'de_che': loai == 'che', 'dinh_danh': chon})
        yc = deepcopy(yc) if yc else {k: getattr(ctx, k) for k in ('module', 'nguoi_gui', 'tai_lieu')}
        yc['trang_thai'] = 'DA_DONG' if nk['dong_yeu_cau'] else 'DANG_XU_LY'
        anh.dat('ma_yeu_cau', ma, yc)
        anh.dat('dau_gap', khoa_dau('luot', luot),
                {'bam': self.bam, 'ma_yeu_cau': ma, 'loai': loai,
                 'bam_ket_qua': _bam_ket_qua(kq),
                 'so_moi': kq.get('cho_duyet', {}).get('so_cum_vua_them', 0)})
        self.viec.kiem_huy()
        self._kiem('chot')
        anh.chot()
        return kq
