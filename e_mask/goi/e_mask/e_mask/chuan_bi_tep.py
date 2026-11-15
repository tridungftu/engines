"""B7: chuẩn bị tệp cho Local, nhường handler và giữ nguyên TTL R4."""
import json
import re
from copy import deepcopy
from dataclasses import asdict
from typing import Protocol
from uuid import uuid4

from . import chuan_bi_ai as cb, phong_bi, tep_word as word, tep_excel as excel
from . import che_van_ban as che
from .anh_xa_ai import bam_chu, tao_anh_xa
from .ho_so_ai import DauHoSoRAM, bam_bytes, json_chuan
from .ho_so_tep import (CHUAN_BI, VAN_BAN, GIU_DINH_DANG, HoSoTepRAM,
                        bao_ve, MIME, TRAN_TEP, loi)
from .quyen_yeu_cau import loi_ram


def doc_tep_viec(viec, ref):
    if (type(ref) is not dict or set(ref) != {'tep_id', 'ten', 'mime', 'kich_thuoc'}
            or type(ref['tep_id']) is not str or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,200}', ref['tep_id'])
            or type(ref['ten']) is not str or not 1 <= len(ref['ten']) <= 200
            or any(c in ref['ten'] for c in '/\\:')
            or any(ord(c) < 32 for c in ref['ten'])
            or type(ref['kich_thuoc']) is not int or not 0 < ref['kich_thuoc'] <= TRAN_TEP):
        raise phong_bi.loi('MASK_DAU_VAO')
    viec.kiem_huy()
    with viec.mo_tep(ref['tep_id']) as f:
        raw = f.read(TRAN_TEP + 1)
    viec.kiem_huy()
    if type(raw) is not bytes or len(raw) > TRAN_TEP:
        raise phong_bi.loi('MASK_QUA_GIOI_HAN')
    if len(raw) != ref['kich_thuoc']:
        raise loi_ram('MASK_DAU_VAO_THAY_DOI')
    return raw


def doc_dau_vao(viec):
    """Mẫu 5 hiện hành; dạng trả chỉ do port Core xác thực chọn và ghim."""
    dau = viec.dau_vao
    if type(dau) is not dict or set(dau) != {'loai', 'tep'} or dau['loai'] != 'tep':
        raise phong_bi.loi()
    ref = dau['tep']
    raw, ds = doc_tep_viec(viec, ref), []
    if ref['mime'] == 'application/json':
        def cam(_):
            raise phong_bi.loi()
        v = json.loads(raw.decode('utf-8'), object_pairs_hook=phong_bi._cap, parse_constant=cam)
        if type(v) is not dict or not {'tep'} <= set(v) <= {'tep', 'dinh_danh_da_biet'}:
            raise phong_bi.loi()
        ref, ds = v['tep'], v.get('dinh_danh_da_biet', [])
        # mo_tep của Core phải kiểm quyền tham chiếu con, không chỉ quyền JSON.
        raw = doc_tep_viec(viec, ref)
    loai = next((k for k, m in MIME.items() if ref['mime'] == m), None)
    if loai is None or not ref['ten'].lower().endswith('.' + loai):
        raise loi('MASK_TEP_CHUA_HO_TRO')
    che._kiem_dinh_danh(ds, la_khai_bao=True)
    return raw, ds, loai, ref


def nguon_local(s, *, kiem):
    """Băng nguyên văn và quan hệ khoảng chỉ RAM, không ghép thực thể qua ô.

    Đọc mọi vùng B2/B3, thêm ngữ cảnh cả hàng cho ô bất biến Excel và scalar
    metadata đã được whitelist nhưng không có miền patch. Bản lặp ngữ cảnh
    cũng tính vào trần; không âm thầm cắt để vừa model.
    """
    doc = s['tai_lieu']
    cac, mien, phep, pos = [], [], [], 0

    def them(chu, vi=None):
        nonlocal pos
        kiem()
        if not chu:
            return
        if cac:
            cac.append('\n')
            pos += 1
        if pos + len(chu) > 500000:
            raise phong_bi.loi('MASK_QUA_GIOI_HAN')
        mien.append((pos, pos + len(chu), vi))
        if vi is not None and s['anh_xa'][vi] is not None:
            phep.extend((pos + a, pos + b, alias) for a, b, alias in word._phep_alias(s['anh_xa'][vi]))
        cac.append(chu)
        pos += len(chu)

    try:
        for i, v in enumerate(doc.vung):
            them(v.van_ban if s['loai'] == 'docx' else v.chu, i)
        if s['loai'] == 'xlsx':
            hang, can = {}, set()
            for o in doc.o:
                kiem()
                khoa = (o.so_sheet, re.sub(r'^[A-Z]+', '', o.dia_chi))
                hang.setdefault(khoa, []).append(o)
                if o.vung is None and o.gia_tri is not None:
                    can.add(khoa)
            names = {v.so_sheet: i for i, v in enumerate(doc.vung) if v.ma == 'ten_sheet'}
            for khoa, os in hang.items():
                kiem()
                if khoa not in can:
                    continue
                i = names[khoa[0]]
                them(doc.vung[i].chu, i)
                for o in os:
                    them(doc.vung[o.vung].chu if o.vung is not None else o.gia_tri, o.vung)
        # Scalar metadata của CẢ Word/Excel chưa có miền patch. Không lấy
        # kiểm kiểu số làm bằng chứng rằng giá trị không chứa định danh.
        cay = doc.goi.cay if s['loai'] == 'docx' else doc.goi.goi.cay
        for phan, root in cay.items():
            kiem()
            if phan.startswith('docProps/'):
                for e in root.iter():
                    kiem()
                    ten = e.tag.rsplit('}', 1)[-1]
                    if ten in {'created', 'modified', 'lastPrinted', 'revision', 'date', 'filetime',
                               'i1', 'i2', 'i4', 'i8', 'int', 'ui1', 'ui2', 'ui4', 'ui8', 'uint',
                               'r4', 'r8', 'decimal', 'bool', 'Pages', 'Words', 'Characters', 'Lines',
                               'Paragraphs', 'TotalTime', 'DocSecurity', 'ScaleCrop', 'SharedDoc',
                               'Slides', 'Notes', 'HiddenSlides', 'MMClips', 'CharactersWithSpaces',
                               'LinksUpToDate', 'HyperlinksChanged'}:
                        if ten not in {'created', 'modified', 'lastPrinted', 'date', 'filetime',
                                       'bool', 'ScaleCrop', 'SharedDoc', 'LinksUpToDate', 'HyperlinksChanged'}:
                            con, du = che._kiem_con_sot(e.text or '', [])
                            if con or not du:
                                # Scalar số không có miền patch/inverse; Local
                                # nhận diện tên không thay lớp số/MST/tài khoản.
                                raise loi('MASK_TEP_CHUA_HO_TRO')
                        them(e.text)
        goc = ''.join(cac)
        phong_bi.kiem_van_ban(goc, cho_dinh_dang=True)
        m = tao_anh_xa(goc, tuple(phep))
        m.alias_nguyen_van()
        return m, tuple(mien)
    finally:
        cac.clear()
        phep.clear()


class CongChuanBiTep(Protocol):
    """C-P4-04/05 đề nghị, thiếu bất kỳ cửa nào thì từ chối.

    Dạng trả do Core ghim từ quy trình/module đã xác thực. kiem_tep kiểm
    ACL tệp con và băm, không cất gốc/map. Các biên nhận token bao cả
    prompt/khuôn/đoạn/đầu ra, do Core đo, không ước từ số ký tự tại Mask.
    ban_giao chỉ chuyển yêu cầu Local hiện tại, không lưu hồ sơ phụ trợ.
    """
    def dang_tra(self, viec, ctx) -> str: ...
    def kiem_tep(self, viec, ctx, *, tham_chieu, bam_tep) -> bool: ...
    def cau_hinh(self, viec, ctx) -> dict: ...
    def kiem_ngan_sach(self, viec, ctx, *, de_nghi) -> dict: ...
    def kiem_han(self, viec, ctx, *, bien_nhan) -> bool: ...
    def chi_so_doan(self, viec, ctx, *, so_doan) -> int: ...
    def ban_giao(self, viec, ctx, *, dau, yeu_cau: bytes) -> bool: ...


def yeu_cau(h, ma, i):
    """Giữ nguyên profile AI-9/R5; metadata RAM không có tệp tương ứng."""
    d, cfg, dau = h['ke_hoach'][i], h['cau_hinh'], h['dau']
    m = h['map_quy_tac']
    tiep = dict(phien_ban=1, ma_yeu_cau=ma, nha_cung_cap_bat_buoc='local',
        ho_so=dict(tep_id='ram-' + dau.ma_ho_so_ram, ten='mask-2c-ram.json',
                   mime='application/json', kich_thuoc=len(json_chuan(h['mo_ta']))),
        bam_ho_so=dau.bam_ho_so, bam_goc=m.bam_goc, bam_da_che_quy_tac=m.bam_da_che,
        phien_ban_map=m.phien_ban, chi_so_doan=i, so_doan=len(h['ke_hoach']),
        bat_dau_doan=d.bat_dau, ket_thuc_doan=d.ket_thuc, bam_doan=d.bam_doan,
        he_offset='unicode_code_point', bam_prompt=bam_chu(cfg['prompt']),
        bam_khuon=bam_bytes(json_chuan(h['khuon'])), bam_profile=bam_bytes(json_chuan(cb.profile())))
    ket = dict(loai='yeu_cau_ai', yeu_cau_ai=dict(phien_ban=1,
        ma_prompt=cfg['ma_prompt'], phien_ban_prompt=cfg['phien_ban_prompt'],
        prompt=cfg['prompt'], tai_lieu=m.goc[d.bat_dau:d.ket_thuc],
        khuon_tra_loi=deepcopy(h['khuon']), bat_buoc_trich_dan=True,
        model_uu_tien=cfg['model_uu_tien'], chuyen_tiep={'mask_2c': tiep}))
    phong_bi.kiem_yeu_cau_ai(ket)
    return ket


class ChuanBiTep(HoSoTepRAM):
    @bao_ve
    def chuan_bi(self, viec):
        with self.so_huu(viec) as buoc:
            return self._chuan_bi()

    def _chuan_bi(self):
        raw = ds = m = h = s = None
        try:
            raw, ds, loai, ref = doc_dau_vao(self.viec)
            self.dung('kiem_tep', tham_chieu=deepcopy(ref), bam_tep=bam_bytes(raw))
            dang = self.goi('dang_tra')
            if type(dang) is not str or dang not in {'van_ban', 'tep'}:
                raise loi()
            cuoi = VAN_BAN if dang == 'van_ban' else GIU_DINH_DANG
            cfg = cb._cau_hinh(self.goi('cau_hinh'))
            bam_vao = bam_bytes(json_chuan([self.viec.dau_vao, self.viec.tham_so, bam_bytes(raw), ds]))
            du = self.buoc.du_lieu
            if 'ho_so_tep' not in du:
                if any(k in du for k in ('ho_so_ai', 'tep_word', 'tep_excel', 'alias_nguyen_van')):
                    raise loi_ram('MASK_VONG_DOI_KHONG_HOP_LE')
                module = word if loai == 'docx' else excel
                (module.che_word if loai == 'docx' else module.che_excel)(raw, buoc=self.buoc, dinh_danh=ds)
                s = du['tep_word' if loai == 'docx' else 'tep_excel']
                # B5/B6 chỉ giữ state dưới handle R4, không ghi ngăn/hồ sơ.
                with self.ram._khoa:
                    self.ram._kiem_buoc(self.buoc)
                    s['loai'] = loai
                m, mien = nguon_local(s, kiem=self.kiem)
                ke = cb.lap_ke_hoach(m.goc)
                de_nghi = cb._de_nghi(m.goc, ke, cfg)
                bn = cb._ngan_sach(self.goi('kiem_ngan_sach', de_nghi=deepcopy(de_nghi)), de_nghi)
                self.dung('kiem_han', bien_nhan=deepcopy(bn))
                mo_ta = dict(phien_ban=1, nang_luc=CHUAN_BI, nang_luc_cuoi=cuoi,
                    bam_tep=s['bam_goc'], bam_quy_tac=s['bam_da_che'],
                    bam_goc=m.bam_goc, bam_da_che=m.bam_da_che, phien_ban_map=m.phien_ban,
                    phien_ban_engine=self.phien_ban_engine, cau_hinh=cfg,
                    ke_hoach=[asdict(d) for d in ke], bien_nhan=bn)
                h = dict(phien_ban=1, giai_doan='CHO_LOCAL', loai=loai, dang_tra=dang,
                    nang_luc_cuoi=cuoi, bam_tep=s['bam_goc'], bam_quy_tac=s['bam_da_che'],
                    bam_dau_vao=bam_vao, phien_ban_engine=self.phien_ban_engine,
                    cau_hinh=cfg, khuon=cb.khuon_tra_loi(), bien_nhan=bn,
                    map_quy_tac=m, mien=mien, ke_hoach=ke, mo_ta=mo_ta,
                    dau=DauHoSoRAM(uuid4().hex, bam_bytes(json_chuan(mo_ta))),
                    da_giao={}, doan_theo_luot={})
                self.kiem()
                with self.ram._khoa:
                    self.ram._kiem_buoc(self.buoc)
                    du['ho_so_tep'] = h
            else:
                h, s = self.doc()
                if (h['bam_dau_vao'] != bam_vao or h['cau_hinh'] != cfg or h['loai'] != loai
                        or h['nang_luc_cuoi'] != cuoi or h['phien_ban_engine'] != self.phien_ban_engine):
                    raise loi_ram('MASK_DAU_VAO_THAY_DOI')
                de_nghi = cb._de_nghi(h['map_quy_tac'].goc, h['ke_hoach'], cfg)
                bn = cb._ngan_sach(self.goi('kiem_ngan_sach', de_nghi=deepcopy(de_nghi)), de_nghi)
                if bn != h['bien_nhan']:
                    raise cb.loi('MASK_AI_XUNG_DOT')
            self.dung('kiem_han', bien_nhan=deepcopy(h['bien_nhan']))
            i = self.goi('chi_so_doan', so_doan=len(h['ke_hoach']))
            if type(i) is not int or not 0 <= i < len(h['ke_hoach']):
                raise cb.loi()
            theo_luot, da_giao = h['doan_theo_luot'], h['da_giao']
            if (self.ctx.ma_luot in theo_luot and theo_luot[self.ctx.ma_luot] != i
                    or i != len(da_giao) and i not in da_giao):
                raise cb.loi('MASK_AI_XUNG_DOT')
            ket = yeu_cau(h, self.ctx.ma_yeu_cau, i)
            raw_yc = json_chuan(ket)
            if i in da_giao and da_giao[i] != bam_bytes(raw_yc):
                raise cb.loi('MASK_AI_XUNG_DOT')
            # Ghi băm trước bàn giao để mất ACK còn retry cùng đoạn, cùng TTL.
            with self.ram._khoa:
                self.ram._kiem_buoc(self.buoc)
                theo_luot[self.ctx.ma_luot] = i
                da_giao[i] = bam_bytes(raw_yc)
            self.buoc.cho_ai()
            self.dung('ban_giao', dau=h['dau'], yeu_cau=raw_yc)
            self.dung('kiem_han', bien_nhan=deepcopy(h['bien_nhan']))
            raw_cuoi, ds_cuoi, loai_cuoi, ref_cuoi = doc_dau_vao(self.viec)
            if (raw_cuoi != raw or ds_cuoi != ds or loai_cuoi != loai or ref_cuoi != ref):
                raise loi_ram('MASK_DAU_VAO_THAY_DOI')
            self.dung('kiem_tep', tham_chieu=deepcopy(ref), bam_tep=bam_bytes(raw_cuoi))
            self.doc()
            self.viec.tien_do(100, 'Đã chuẩn bị đoạn tệp cho AI cục bộ qua Core.')
            self.kiem()
            return ket
        finally:
            raw = ds = m = h = s = None
