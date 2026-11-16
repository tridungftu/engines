"""MASK-B10: công cụ DEMO ngoài gói, mặc định khô, Cloud luôn tắt.

Chạy: .venv/Scripts/python -B e_mask/cong-cu/thu_mask_tep_that.py --tu-kiem
      .venv/Scripts/python -B e_mask/cong-cu/thu_mask_tep_that.py --bien
      THU-MASK-TEP-THAT.cmd --that --thu-muc-demo <thư mục mới>

--that chỉ dành cho Anh: mở/lưu/mở lại Office bằng tay, không COM/macro.
Chế độ này vẫn dùng Local giả; Local/Core thật luôn CHƯA ĐO. Công cụ không
nhận tài liệu người dùng, URL, khóa hoặc cấu hình thật. Hiện vật DEMO chỉ
được ghi vào thư mục Anh chỉ định; không ghi map/hồ sơ/gốc RAM của engine.
Gold là bộ ứng viên đến khi lead xác nhận SHA bộ dữ liệu VÀ SHA công cụ
bằng --xac-nhan-gold/--xac-nhan-cong-cu. Xác nhận không chứng nhận chất lượng.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from copy import deepcopy
from dataclasses import dataclass, replace
from hashlib import sha256
from importlib.metadata import version
import io
import json
import logging
import os
from pathlib import Path
import random
import re
import stat
import struct
import subprocess
import sys
import time
import tracemalloc
from types import SimpleNamespace
import unicodedata as ud
from uuid import uuid4
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, quoteattr
import zipfile
import zlib

sys.dont_write_bytecode = True
THU_MUC = Path(__file__).resolve().parent
GOI = THU_MUC.parent / 'goi' / 'e_mask'
sys.path.insert(0, str(GOI))

from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, ViecDaHuy
from kho_tri_thuc_sdk.thu import CoreGia
from e_mask.chay import tao_app
from e_mask import chuan_bi_ai as cb
from e_mask.che_van_ban import chuan_hoa, chuan_bi_danh
from e_mask.chuan_bi_tep import yeu_cau
from e_mask.ho_so_tep import CHUAN_BI, GIU_DINH_DANG, MIME
from e_mask.kho_anh_xa_ram import KhoAnhXaRAM, _chu
from e_mask.khoi_tao_ngan import PHIEN_BAN_CHUAN_HOA
from e_mask.quyen_yeu_cau import (GhimTienTrinh, NguCanhTinCay, NguCanhRAM,
                                SuKienRAM, loi_kho)

MO = 'mask.mo_che_tep@1'
PHIEN_BAN = 'MASK-B10.1'
MIB = 1048576
NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    's': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'ct': 'http://schemas.openxmlformats.org/package/2006/content-types',
    'pr': 'http://schemas.openxmlformats.org/package/2006/relationships',
    'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'dcterms': 'http://purl.org/dc/terms/',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'ep': 'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties',
    'cust': 'http://schemas.openxmlformats.org/officeDocument/2006/custom-properties',
    'vt': 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes',
}
DUOI = '; 1.246.800 VND; 2026-10-29.'
MOI = 'Nội dung DEMO bổ sung; 2.468.000 VND; 2026-11-02.'


def json_bytes(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def bam(raw):
    return 'sha256:' + sha256(raw).hexdigest()


def doi_chieu(dieu_kien, ma='B10_SAI_KY_VONG'):
    if not dieu_kien:
        raise KiemLoi(ma)


class KiemLoi(Exception):
    """Chỉ mã cố định; không ghép nội dung/đường dẫn vào exception."""


def xml(the, noi='', **ns):
    attrs = ''.join(' xmlns:' + k + '=' + quoteattr(NS[k]) for k in ns)
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><' + the + attrs + '>' + noi + '</' + the + '>'


def nen(phan, *, cach=zipfile.ZIP_DEFLATED):
    """Chỉ dựng fixture/AI giả, không thay writer của engine."""
    f = io.BytesIO()
    with zipfile.ZipFile(f, 'w', compression=cach, compresslevel=6) as z:
        for ten, raw in sorted(phan.items()):
            info = zipfile.ZipInfo(ten, (2026, 11, 16, 5, 4, 0))
            # ZipInfo trên Windows tự đổi backslash thành slash. Fixture
            # tấn công phải giữ tên thô, không biến thành đường hợp lệ.
            info.filename = ten
            info.compress_type, info.create_system = cach, 0
            info.external_attr = 32
            z.writestr(info, raw.encode('utf-8') if isinstance(raw, str) else raw)
    return f.getvalue()


def doc_phan(raw):
    # Chỉ dùng với fixture nhỏ của công cụ hoặc bytes đã qua runtime gate.
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        return {i.filename: z.read(i) for i in z.infolist()}


def quan_he(ds):
    noi = ''.join('<pr:Relationship Id="rId%d" Type=%s Target=%s/>' %
                  (i + 1, quoteattr(k), quoteattr(t)) for i, (k, t) in enumerate(ds))
    return xml('pr:Relationships', noi, pr=True)


def ket_goi(p, loai, qh, phu=()):
    r = NS['r']
    chinh = 'word/document.xml' if loai == 'docx' else 'xl/workbook.xml'
    props = [('docProps/core.xml', 'application/vnd.openxmlformats-package.core-properties+xml',
              'http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties'),
             ('docProps/app.xml', 'application/vnd.openxmlformats-officedocument.extended-properties+xml', r + '/extended-properties'),
             ('docProps/custom.xml', 'application/vnd.openxmlformats-officedocument.custom-properties+xml', r + '/custom-properties')]
    types = {chinh: 'application/vnd.openxmlformats-officedocument.' +
             ('wordprocessingml.document.main+xml' if loai == 'docx' else 'spreadsheetml.sheet.main+xml')}
    roots = [(r + '/officeDocument', chinh)]
    for ten, ct, kieu in props:
        if ten in p:
            types[ten] = ct
            roots.append((kieu, ten))
    for ten, ct in phu:
        types[ten] = ct
    noi = '<ct:Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    noi += ''.join('<ct:Override PartName=%s ContentType=%s/>' % (quoteattr('/' + t), quoteattr(c)) for t, c in sorted(types.items()))
    p['[Content_Types].xml'] = xml('ct:Types', noi, ct=True)
    p['_rels/.rels'] = quan_he(roots)
    p['word/_rels/document.xml.rels' if loai == 'docx' else 'xl/_rels/workbook.xml.rels'] = quan_he(qh)
    return p


def props(ten, kiem_thuat=False):
    ket = {
        'docProps/core.xml': xml('cp:coreProperties', '<dc:creator>' + escape(ten) + '</dc:creator><dc:title>DEMO</dc:title><dcterms:created xsi:type="dcterms:W3CDTF">2026-10-29T00:00:00Z</dcterms:created>', cp=True, dc=True, dcterms=True, xsi=True),
        'docProps/app.xml': xml('ep:Properties', '<ep:Application>DEMO</ep:Application><ep:Company>' + escape(ten) + '</ep:Company>', ep=True),
        'docProps/custom.xml': xml('cust:Properties', '<cust:property fmtid="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" pid="2" name="DEMO"><vt:lpwstr>' + escape(ten) + '</vt:lpwstr></cust:property>', cust=True, vt=True),
    }
    if kiem_thuat:
        ket = {t: v.replace('>DEMO<', '>nội dung.<').replace('name="DEMO"', 'name="nội dung"') for t, v in ket.items()}
    return ket


def doan_word(chu, *, tach=False, an=False):
    cac = [chu] if not tach else [chu[:9], chu[9:17], chu[17:]]
    return '<w:p>' + ''.join('<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>' +
        ('<w:b/>' if i == 0 else '<w:i/>') + ('<w:vanish/>' if an else '') +
        '</w:rPr><w:t xml:space="preserve">' + escape(c) + '</w:t></w:r>' for i, c in enumerate(cac)) + '</w:p>'


def dung_word(ca):
    ten, kieu = ca['dinh_danh'][0]['chu'], ca['bien_the']
    noi = doan_word(ten + DUOI, tach=kieu == 'run', an=kieu == 'story')
    thuong = 'nội dung. ' * 2000 if ca.get('lap_doan') else ('nội dung.' if ca.get('kiem_thuat') else 'DEMO số sổ cái 73; tổng thu đã kiểm tra.')
    noi += doan_word(thuong)
    p, qh, phu = {}, [], []
    if kieu == 'bang_notes':
        noi += '<w:tbl><w:tblGrid><w:gridCol w:w="2400"/><w:gridCol w:w="2400"/></w:tblGrid><w:tr><w:tc><w:tcPr><w:gridSpan w:val="2"/></w:tcPr>' + doan_word(ten) + '</w:tc></w:tr></w:tbl>'
        noi += '<w:p><w:r><w:footnoteReference w:id="1"/><w:endnoteReference w:id="1"/></w:r></w:p>'
        for loai in ('footnote', 'endnote'):
            p['word/' + loai + 's.xml'] = xml('w:' + loai + 's', '<w:' + loai + ' w:id="1">' + doan_word(ten) + '</w:' + loai + '>', w=True)
            qh.append((NS['r'] + '/' + loai + 's', loai + 's.xml'))
            phu.append(('word/' + loai + 's.xml', 'application/vnd.openxmlformats-officedocument.wordprocessingml.' + loai + 's+xml'))
    if kieu == 'story':
        for i, (t, root) in enumerate((('header', 'hdr'), ('footer', 'ftr'))):
            p['word/' + t + '1.xml'] = xml('w:' + root, doan_word(ten), w=True)
            qh.append((NS['r'] + '/' + t, t + '1.xml'))
            phu.append(('word/' + t + '1.xml', 'application/vnd.openxmlformats-officedocument.wordprocessingml.' + t + '+xml'))
        noi += '<w:sectPr><w:headerReference w:type="default" r:id="rId1"/><w:footerReference w:type="default" r:id="rId2"/></w:sectPr>'
    p['word/document.xml'] = xml('w:document', '<w:body>' + noi + '</w:body>', w=True, r=True)
    p.update(props(ten, ca.get('kiem_thuat', False)))
    return ket_goi(p, 'docx', qh, phu)


def dung_excel(ca):
    ten, kieu = ca['dinh_danh'][0]['chu'], ca['bien_the']
    sst = kieu in {'rich', 'merge', 'unicode'}
    rich = '<s:r><s:rPr><s:b/></s:rPr><s:t xml:space="preserve">' + escape(ten[:9]) + '</s:t></s:r><s:r><s:rPr><s:i/></s:rPr><s:t xml:space="preserve">' + escape(ten[9:] + DUOI) + '</s:t></s:r>'
    val = rich if kieu == 'rich' else '<s:t>' + escape(ten + DUOI) + '</s:t>'
    a1 = '<s:c r="A1" s="0" t="s"><s:v>0</s:v></s:c>' if sst else '<s:c r="A1" s="0" t="inlineStr"><s:is>' + val + '</s:is></s:c>'
    noi = '<s:cols><s:col min="1" max="1" width="28" customWidth="1"' + (' hidden="1"' if kieu == 'an' else '') + '/></s:cols>'
    noi += '<s:sheetData><s:row r="1"' + (' hidden="1"' if kieu == 'an' else '') + '>' + a1 + '<s:c r="C1" s="1"><s:v>1246800</s:v></s:c><s:c r="D1" s="2"><s:v>46324</s:v></s:c></s:row>'
    noi += '<s:row r="2"><s:c r="A2" t="inlineStr"><s:is><s:t>' + ('nội dung.' if ca.get('kiem_thuat') else 'DEMO số sổ cái 73; tổng thu đã kiểm tra.') + '</s:t></s:is></s:c></s:row></s:sheetData>'
    if kieu == 'merge':
        noi += '<s:mergeCells count="1"><s:mergeCell ref="A1:B1"/></s:mergeCells>'
    p = {'xl/workbook.xml': xml('s:workbook', '<s:workbookPr date1904="0"/><s:sheets><s:sheet name="DEMO" sheetId="1" r:id="rId1"/></s:sheets>', s=True, r=True),
         'xl/worksheets/sheet1.xml': xml('s:worksheet', noi, s=True),
         'xl/styles.xml': xml('s:styleSheet', '<s:fonts count="1"><s:font><s:name val="Calibri"/><s:sz val="11"/></s:font></s:fonts><s:fills count="2"><s:fill><s:patternFill patternType="none"/></s:fill><s:fill><s:patternFill patternType="gray125"/></s:fill></s:fills><s:borders count="1"><s:border/></s:borders><s:cellStyleXfs count="1"><s:xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></s:cellStyleXfs><s:cellXfs count="3"><s:xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><s:xf numFmtId="4" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/><s:xf numFmtId="14" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/></s:cellXfs>', s=True)}
    qh = [(NS['r'] + '/worksheet', 'worksheets/sheet1.xml'), (NS['r'] + '/styles', 'styles.xml')]
    phu = [('xl/worksheets/sheet1.xml', 'application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml'), ('xl/styles.xml', 'application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml')]
    if sst:
        p['xl/sharedStrings.xml'] = xml('s:sst', '<s:si>' + val + '</s:si>', s=True)
        qh.append((NS['r'] + '/sharedStrings', 'sharedStrings.xml'))
        phu.append(('xl/sharedStrings.xml', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml'))
    p.update(props(ten, ca.get('kiem_thuat', False)))
    if ca.get('kiem_thuat'):
        p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('name="DEMO"', 'name="Sheet1"')
    return ket_goi(p, 'xlsx', qh, phu)


def dung(ca):
    p = dung_word(ca) if ca['loai'] == 'docx' else dung_excel(ca)
    chan = ca.get('chan')
    main = 'word/document.xml' if ca['loai'] == 'docx' else 'xl/worksheets/sheet1.xml'
    if chan == 'comments':
        p['word/comments.xml' if ca['loai'] == 'docx' else 'xl/comments1.xml'] = b'<DEMO/>'
    elif chan == 'revisions':
        p[main] = p[main].replace('<w:p>', '<w:p><w:ins w:id="7" w:author="DEMO"/>', 1)
    elif chan == 'sheet_an':
        p['xl/workbook.xml'] = p['xl/workbook.xml'].replace('name="DEMO"', 'name="DEMO" state="veryHidden"')
    elif chan in {'formula', 'cache'}:
        p[main] = p[main].replace('<s:row r="2">', '<s:row r="2"><s:c r="E2" t="str"><s:f>"DEMO"</s:f><s:v>DEMO</s:v></s:c>', 1)
    elif chan == 'chart':
        p['xl/charts/chart1.xml'] = b'<DEMO/>'
    elif chan == 'links':
        rel = 'word/_rels/document.xml.rels' if ca['loai'] == 'docx' else 'xl/_rels/workbook.xml.rels'
        p[rel] = p[rel].replace('</pr:Relationships>', '<pr:Relationship Id="rId90" Type="' + NS['r'] + '/hyperlink" Target="https://demo.invalid/" TargetMode="External"/></pr:Relationships>')
    elif chan == 'nhung':
        p['word/embeddings/DEMO.bin' if ca['loai'] == 'docx' else 'xl/embeddings/DEMO.bin'] = b'DEMO'
    elif chan == 'macro':
        p['word/vbaProject.bin' if ca['loai'] == 'docx' else 'xl/vbaProject.bin'] = b'DEMO'
    elif chan == 'part_la':
        p['DEMO.xml'] = b'<DEMO/>'
    elif chan == 'zip_traversal':
        p['../DEMO.xml'] = b'<DEMO/>'
    elif chan == 'zip_symlink':
        raw = bytearray(nen(p))
        at = raw.find(b'PK\x01\x02')
        struct.pack_into('<H', raw, at + 4, (3 << 8) | 20)
        struct.pack_into('<I', raw, at + 38, (stat.S_IFLNK | 0o777) << 16)
        return bytes(raw)
    return nen(p)


class DongHo:
    def __init__(self):
        self.luc, self.hen = 100., []

    def __call__(self):
        return self.luc

    def hen_gio(self, giay, ham):
        h = SimpleNamespace(luc=self.luc + giay, ham=ham, bat=False, huy=False)
        h.start = lambda: setattr(h, 'bat', True)
        h.cancel = lambda: setattr(h, 'huy', True)
        self.hen.append(h)
        return h

    def tien(self, giay):
        self.luc += giay
        for h in tuple(self.hen):
            if h.bat and not h.huy and h.luc <= self.luc:
                h.huy = True
                h.ham()


class QuyenGia:
    """Nguồn tin cậy giả do adapter cấp, không lấy quyền từ input."""
    def __init__(self, *, instance='b10-instance-a', dang_ky=None):
        self.ve, self.ctx, self.su_kien = {}, {}, {}
        self.da_cap = {} if dang_ky is None else dang_ky
        self.instance, self.han, self.ghim = instance, None, True
        self.scope, self.thu_hoi = {}, False

    def cap(self, v, *, ma=None, loai='che'):
        q = NguCanhTinCay(ma or uuid4().hex, uuid4().hex, 'phien-demo-b10',
                         'module-demo-b10', 'nguoi-demo-b10', 'tai-lieu-demo-b10', 'DEMO')
        self.ve[v, loai] = q
        return q

    def xac_minh(self, v, *, loai, ma_yeu_cau, thao_tac):
        q = self.ve.get((v.id, loai))
        if self.thu_hoi or q is None or ma_yeu_cau is not None and q.ma_yeu_cau != ma_yeu_cau:
            raise loi_kho('MASK_MA_YEU_CAU')
        return replace(q, **self.scope)

    def dang_ky_vong_doi_ram(self, ham, *, phien_ram):
        self.su_kien[phien_ram] = ham
        return GhimTienTrinh(self.instance, phien_ram, self.ghim, True)

    def xac_minh_ram(self, v, *, ngu_canh, phien_ram, thao_tac):
        ma = ngu_canh.ma_yeu_cau
        moi = ma not in self.da_cap
        instance, phien = self.da_cap.setdefault(ma, (self.instance, phien_ram))
        ctx = NguCanhRAM(ngu_canh, 'pn-demo', instance, phien, self.han, moi)
        self.ctx[ma] = ctx
        return ctx

    def bao(self, ma, trang_thai):
        for ham in tuple(self.su_kien.values()):
            ham(SuKienRAM(self.ctx[ma], trang_thai))


class CoreTepGia(CoreGia):
    """CoreGia SDK giữ lease/ngăn thật; chỉ bổ sung ACL tham chiếu con giả."""
    def __init__(self, app):
        super().__init__(app)
        self.tep_con, self.cach_ly, self.da_phat_hanh = {}, set(), set()
        self.so_upload, self.so_doc_goc_luc_mo = 0, 0
        self.ref_goc, self.dang_mo = None, False
        self.seed_xong, self.ten_demo = False, []

    def _ngan_ghi_lo(self, ma, instance, lenh, khoa, *, viec_id=None):
        for cmd in lenh:
            # Chỉ lệnh seed của adapter được ghi giá trị vào cột bi_mat.
            cat = deepcopy(cmd)
            gia = cat.get('gia_tri', {})
            for secret in ('gia_tri_goc', 'gia_tri_chuan'):
                if secret in gia:
                    doi_chieu(not self.seed_xong and cat['bang'] == 'dinh_danh'
                              and cat['thao_tac'] == 'them', 'B10_MAP_GHI_BI_MAT_TRA_HINH')
                    gia.pop(secret)
            kiem_metadata(cat)
            chu = json_bytes(cat).decode('utf-8')
            for ten in self.ten_demo:
                doi_chieu(ten not in chu and chuan_hoa(ten) not in chu, 'B10_BAN_RO_NGOAI_COT_BI_MAT')
        return super()._ngan_ghi_lo(ma, instance, lenh, khoa, viec_id=viec_id)

    def _mo_tep(self, ma, viec_id, tep_id, toi_da_byte):
        if self.dang_mo and tep_id == self.ref_goc:
            self.so_doc_goc_luc_mo += 1
            raise KiemLoi('B10_DOC_LAI_GOC_CORE')
        if tep_id not in self.tep_con.get(viec_id, ()):
            return super()._mo_tep(ma, viec_id, tep_id, toi_da_byte)
        with self._lock:
            self._dang_giu(ma, viec_id)
            raw = self.doc_tep(tep_id)
            if len(raw) > toi_da_byte:
                raise LoiNghiepVu('MASK_QUA_GIOI_HAN', 'Dữ liệu DEMO vượt trần.')
            return raw

    def _tai_tep_ra(self, ma, viec_id, ten, raw, mime, khoa):
        doi_chieu(viec_id in self.cach_ly, 'B10_UPLOAD_CHUA_CACH_LY')
        self.so_upload += 1
        return super()._tai_tep_ra(ma, viec_id, ten, raw, mime, khoa)


def kiem_metadata(v):
    """Spy cấm bản sao phục hồi. Không cấm bi_mat ở lệnh seed riêng."""
    cam = {'gia_tri_goc', 'gia_tri_chuan', 'goc', 'da_che', 'alias_nguyen_van',
           'anh_xa', 'map_quy_tac', 'bytes_goc', 'tai_lieu', 'nguyen_van'}
    if isinstance(v, dict):
        doi_chieu(not (cam & v.keys()), 'B10_MAP_RA_CUA_CORE')
        for x in v.values():
            kiem_metadata(x)
    elif isinstance(v, (list, tuple)):
        for x in v:
            kiem_metadata(x)


class CongCoreGia:
    """C-P4-01…05 giả, không tự nhận là binding SDK/Core thật."""
    def __init__(self, q, dh, ram):
        self.q, self.dh, self.ram = q, dh, ram
        self.i, self.local, self.budget, self.da_chot = 0, {}, {}, {}
        self.raw_phan_hoi = self.nguon = None
        self.core = None
        self.mat_ack, self.sua_nguon, self.moc = None, lambda b: b, lambda m, v: None
        self.dem = Counter()
        self.cfg = dict(ma_prompt='module.demo.b10', phien_ban_prompt='1',
            prompt='Dữ liệu giả DEMO, chỉ Local.\n' + cb.CHI_DAN_BAT_BUOC,
            model_uu_tien='b10-local-gia', nha_cung_cap_bat_buoc='local')

    def cau_hinh(self, v, ctx):
        return deepcopy(self.cfg)

    def dang_tra(self, v, ctx):
        return 'tep'

    def chi_so_doan(self, v, ctx, *, so_doan):
        return self.i

    def kiem_tep(self, v, ctx, *, tham_chieu, bam_tep):
        self.ref = tham_chieu
        return bam(self.core.doc_tep(tham_chieu['tep_id'])) == bam_tep

    def kiem_nguon_tep(self, v, ctx, **kw):
        return bam(self.core.doc_tep(self.ref['tep_id'])) == kw['bam_tep']

    def kiem_ngan_sach(self, v, ctx, *, de_nghi):
        # Token/budget giả có nhãn riêng; không là số đo tokenizer/model.
        return deepcopy(self.budget.setdefault(ctx.ma_yeu_cau, dict(
            bam_de_nghi=bam(json_bytes(de_nghi)), nha_cung_cap='local', model='b10-local-gia',
            tokenizer='B10-GIA-CHUA-DO', context_token=16000, token_ra_toi_da=4000,
            token_vao=[6000] * len(de_nghi['ke_hoach']), tung_doan_da_do=True,
            han_chuoi='2026-11-16T23:59:59+07:00', han_local_giay=60)))

    def kiem_han(self, v, ctx, *, bien_nhan):
        return bien_nhan == self.budget[ctx.ma_yeu_cau]

    def ban_giao(self, v, ctx, **kw):
        if 'yeu_cau' in kw:
            y = json.loads(kw['yeu_cau'])
            m = y['yeu_cau_ai']['chuyen_tiep']['mask_2c']
            kiem_metadata(m)
            doi_chieu(m['nha_cung_cap_bat_buoc'] == 'local', 'B10_PROVIDER')
            i = m['chi_so_doan']
            doi_chieu(self.local.setdefault(i, y) == y, 'B10_RETRY_DOI_INPUT')
        else:
            kiem_metadata(json.loads(kw['ket_qua']))
        self.dem['ban_giao'] += 1
        self.moc('ban_giao', v)
        return True

    def nhan_phan_hoi(self, v, ctx, **kw):
        self.moc('nhan_local', v)
        return self.raw_phan_hoi

    def chung_thuc(self, v, ctx, *, de_nghi):
        return de_nghi == self.nguon

    def chot_metadata(self, v, ctx, *, chung_cu, metadata, ghi):
        ds = json.loads(metadata)
        kiem_metadata(ds)
        doi_chieu(len(ds) <= 100, 'B10_LO_QUA_TRAN')
        dau = (chung_cu, metadata)
        if ctx.ma_yeu_cau in self.da_chot:
            return self.da_chot[ctx.ma_yeu_cau] == dau
        doi_chieu(ghi() is True, 'B10_CHOT')
        self.da_chot[ctx.ma_yeu_cau] = dau
        self.dem['chot'] += 1
        if self.mat_ack == 'chot':
            raise ChuaRo('B10-ACK-DEMO')
        return True

    def _kiem_giao(self, v, ctx, han, *, mo):
        q = ctx.quyen if mo else ctx
        moi = self.q.xac_minh(v, loai='mo_che' if mo else 'che', ma_yeu_cau=q.ma_yeu_cau, thao_tac='ban_giao')
        if moi != q:
            raise LoiNghiepVu('MASK_MA_YEU_CAU', 'Không xác minh được quyền bàn giao DEMO.')
        v.kiem_huy()
        if self.dh() >= han:
            raise LoiNghiepVu('MASK_ANH_XA_KHONG_CON', 'Chuỗi DEMO đã kết thúc.')

    @contextmanager
    def ban_giao_tep_cuoi(self, v, ctx, *, chung_cu, han_monotonic):
        self.core.cach_ly.add(v.id)
        truoc, pending = set(self.core._tep), None
        def nhan(raw):
            nonlocal pending
            self._kiem_giao(v, ctx, han_monotonic, mo=False)
            pending = raw
            self.dem['che_duoc_nhan'] += 1
            return True
        try:
            yield nhan
            self._kiem_giao(v, ctx, han_monotonic, mo=False)
            doi_chieu(pending is not None, 'B10_BAN_GIAO_RONG')
            self.core.da_phat_hanh.update(set(self.core._tep) - truoc)
        finally:
            self.core.cach_ly.discard(v.id)
            for ref in (set(self.core._tep) - truoc) - self.core.da_phat_hanh:
                self.core._tep.pop(ref, None)
            pending = None

    def kiem_tep_mo(self, v, ctx, *, tham_chieu, loai, bam_tep, ngan_sach):
        kiem_metadata(ngan_sach)
        return (tham_chieu['tep_id'] in self.core.tep_con.get(v.id, ())
                and tham_chieu['mime'] == MIME[loai]
                and bam(self.core.doc_tep(tham_chieu['tep_id'])) == bam_tep)

    @contextmanager
    def ban_giao_cuoi(self, v, ctx, *, bam_dau_vao, han_monotonic):
        self.core.cach_ly.add(v.id)
        truoc, pending, da_nhan = set(self.core._tep), None, False
        def nhan(raw):
            nonlocal pending
            self._kiem_giao(v, ctx, han_monotonic, mo=True)
            pending = raw
            self.moc('mo_nhan', v)
            if self.mat_ack == 'nhan':
                raise ChuaRo('B10-ACK-DEMO')
            return True
        try:
            yield nhan
            self._kiem_giao(v, ctx, han_monotonic, mo=True)
            doi_chieu(self.ram._ban_ghi is None and pending is not None, 'B10_CHUA_TIEU_THU')
            self.core.da_phat_hanh.update(set(self.core._tep) - truoc)
            da_nhan = True
            self.dem['mo_duoc_nhan'] += 1
            if self.mat_ack == 'ra':
                raise ChuaRo('B10-ACK-DEMO')
        finally:
            self.core.cach_ly.discard(v.id)
            if not da_nhan:
                for ref in (set(self.core._tep) - truoc) - self.core.da_phat_hanh:
                    self.core._tep.pop(ref, None)
            pending = None

    def don(self):
        self.local.clear()
        self.budget.clear()
        self.raw_phan_hoi = self.nguon = None


def seed_ngan(v, ds):
    """Ngoại lệ bi_mat P4 §3; không ghi map yêu cầu hoặc trường rõ khác."""
    for t in ds:
        dinh, alias = uuid4().hex, uuid4().hex
        with v.ngan.lo() as lo:
            lo.them('dinh_danh', dict(id_dinh_danh=dinh, vung_du_lieu='DEMO',
                gia_tri_goc=t['chu'], gia_tri_chuan=chuan_hoa(t['chu']),
                phien_ban_chuan_hoa=PHIEN_BAN_CHUAN_HOA,
                nhom=t['nhom'], trang_thai='CHINH_THUC', so_gap=1))
            lo.them('bi_danh', dict(id_bi_danh=alias, id_dinh_danh=dinh,
                vung_du_lieu='DEMO', bi_danh=t['alias'], bi_danh_chuan=chuan_bi_danh(t['alias']),
                trang_thai='CHINH_THUC'))


IO_DANG_KIEM = [False, 0, 0]


def audit(event, args):
    if not IO_DANG_KIEM[0]:
        return
    if event == 'socket.connect':
        IO_DANG_KIEM[2] += 1
        raise KiemLoi('B10_MANG_MAC_DINH')
    if event == 'open':
        mode, flags = args[1], args[2]
        if isinstance(mode, str) and any(x in mode for x in 'wax+') or isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC):
            IO_DANG_KIEM[1] += 1
            raise KiemLoi('B10_ENGINE_GHI_TEP')


sys.addaudithook(audit)


@contextmanager
def giam_sat():
    """Không dump traceback/log, đếm mọi phát ngôn và syscall ghi/mạng."""
    f, e = io.StringIO(), io.StringIO()
    cu = IO_DANG_KIEM[0]
    IO_DANG_KIEM[0] = True
    try:
        with redirect_stdout(f), redirect_stderr(e):
            yield
    finally:
        IO_DANG_KIEM[0] = cu
        doi_chieu(not f.getvalue() and not e.getvalue(), 'B10_RUNTIME_XUAT_LOG')
        f.close()
        e.close()


def os_peak():
    """High-water mark của cả PID, byte; không lấy hiệu hai đỉnh."""
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        class PMC(ctypes.Structure):
            _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [(x, ctypes.c_size_t) for x in ('PeakWorkingSetSize', 'WorkingSetSize', 'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage', 'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]
        a = PMC()
        a.cb = ctypes.sizeof(a)
        ham = ctypes.windll.psapi.GetProcessMemoryInfo
        ham.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
        ham.restype = wintypes.BOOL
        proc = ctypes.windll.kernel32.GetCurrentProcess
        proc.restype = wintypes.HANDLE
        return int(a.PeakWorkingSetSize) if ham(proc(), ctypes.byref(a), a.cb) else 'CHƯA ĐO'
    try:
        import resource
        x = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return int(x if sys.platform == 'darwin' else x * 1024)
    except (ImportError, OSError):
        return 'CHƯA ĐO'


def kich_ram(v, da=None):
    """sys.getsizeof đệ quy, mỗi object một lần; ước lượng đồ thị Python."""
    da = set() if da is None else da
    if id(v) in da:
        return 0
    da.add(id(v))
    n = sys.getsizeof(v)
    if isinstance(v, dict):
        return n + sum(kich_ram(k, da) + kich_ram(x, da) for k, x in v.items())
    if isinstance(v, (list, tuple, set, frozenset)):
        return n + sum(kich_ram(x, da) for x in v)
    if hasattr(v, '__dict__') and not callable(v):
        return n + kich_ram(vars(v), da)
    if hasattr(type(v), '__slots__') and not callable(v):
        return n + sum(kich_ram(getattr(v, k), da) for k in type(v).__slots__ if hasattr(v, k))
    return n


class Chuoi:
    def __init__(self, ca, *, ttl=600, core_han=None, clock_thuc=False):
        self.ca, self.raw = ca, dung(ca)
        self.q, self.dh = QuyenGia(), DongHoThuc() if clock_thuc else DongHo()
        self.q.han = core_han
        self.ram = KhoAnhXaRAM(quyen=self.q, dong_ho=self.dh, hen_gio=self.dh.hen_gio)
        self.cong = CongCoreGia(self.q, self.dh, self.ram)
        self.app = tao_app(quyen=self.q, cong_chuan_bi_tep=self.cong,
                          cong_hau_kiem_tep=self.cong, cong_mo_tep=self.cong)
        self.app.kho_anh_xa_ram = self.ram
        self.c = CoreTepGia(self.app)
        self.c.ten_demo = [t['chu'] for t in ca['dinh_danh'] + ca.get('kho_ngoai_yeu_cau', [])]
        self.cong.core = self.c
        self.c.dat_cau_hinh('e_mask', {'thoi_han_anh_xa_giay': ttl})
        self.ref = self.c.them_tep('DEMO.' + ca['loai'], self.raw, MIME[ca['loai']])
        self.c.ref_goc = self.ref['tep_id']
        self.dau = dict(loai='tep', tep=self.ref)
        self.v = self.c.giao_viec(CHUAN_BI, self.dau)
        self.ctx = self.q.cap(self.v)
        self.goc_bg = None
        self.do, self.cac_kq, self.doan = [], [], 0
        cb_that = self.app._ham[CHUAN_BI]
        ds = ca['dinh_danh'] + ca.get('kho_ngoai_yeu_cau', [])
        def nap(v):
            if ds:
                seed_ngan(v, ds)
                ds.clear()
                self.c.seed_xong = True
            return cb_that(v)
        self.app._ham[CHUAN_BI] = nap

    def chay(self, buoc):
        dau = time.perf_counter()
        with giam_sat():
            self.c.chay(self.app)
        k = self.c.xem(self.v)
        self.do.append(dict(buoc=buoc, giay=time.perf_counter() - dau,
                            trang_thai=k['trang_thai']))
        self.cac_kq.append(k)
        return k

    def chuan_bi(self):
        self.c.dang_mo = False
        k = self.chay('chuan_bi')
        if k['trang_thai'] != 'XONG':
            return k
        n = k['ket_qua']['yeu_cau_ai']['chuyen_tiep']['mask_2c']['so_doan']
        for i in range(1, n):
            self.cong.i = i
            self.v = self.c.giao_viec(CHUAN_BI, self.dau)
            self.q.cap(self.v, ma=self.ctx.ma_yeu_cau)
            k = self.chay('chuan_bi')
            if k['trang_thai'] != 'XONG':
                return k
        self.goc_bg = self.ram._ban_ghi
        self.doan = n
        return k

    def local_gia(self, *, provider='local', thieu=False, sai_span=False):
        """Oracle gold giả chỉ để kiểm chuỗi; không đo recall model thật."""
        dau = time.perf_counter()
        ds = []
        for i, y in sorted(self.cong.local.items()):
            v, ts = y['yeu_cau_ai'], []
            for t in self.ca['dinh_danh']:
                for m in re.finditer(re.escape(t['chu']), v['tai_lieu']):
                    ts.append(dict(loai=t['loai_ai'], muc='chac', nguyen_van=m[0],
                                   bat_dau=m.start() + int(sai_span), ket_thuc=m.end()))
            ai = dict(phien_ban=1, trang_thai='co_can_cu' if ts else 'khong_thay_can_cu',
                tra_loi='DEMO', du_lieu=dict(da_quet_het=True, thuc_the=ts),
                trich_dan=[dict(cau=t['nguyen_van'], bat_dau=t['bat_dau'], ket_thuc=t['ket_thuc']) for t in ts],
                kiem_trich_dan=dict(dat=True, loi=[]), nha_cung_cap=provider,
                model='b10-local-gia', ly_do_chon_model='DEMO', ma_prompt=v['ma_prompt'],
                phien_ban_prompt=v['phien_ban_prompt'], phien_ban_engine='AI-9-gia-B10',
                bam_dau_vao=bam(json_bytes(y)), chuyen_tiep=deepcopy(v['chuyen_tiep']), canh_bao=[])
            ds.append(dict(tra_loi_ai=dict(loai='tra_loi_ai', tra_loi_ai=ai),
                nguon=dict(engine='e_hoi_ai', nang_luc='ai.hoi_mask_cuc_bo@1', nha_cung_cap=provider,
                    model='b10-local-gia', trang_thai='XONG', hoan_tat=dict(giao_thuc='openai_compatible', ket_thuc='stop'))))
        doi_chieu(bool(ds), 'B10_KHONG_CO_DOAN')
        dau_vao = deepcopy(ds[-1]['tra_loi_ai'])
        if thieu:
            ds = ds[:-1]
        bundle = dict(phien_ban=1, ma_yeu_cau=self.ctx.ma_yeu_cau, phan_hoi=ds)
        bundle = self.cong.sua_nguon(bundle)
        raw = json_bytes(bundle)
        h = self.ram._ban_ghi.du_lieu['ho_so_tep']
        chung = [dict(chi_so_doan=i, bam_yeu_cau=bam(json_bytes(self.cong.local[i])),
            bam_phan_hoi=bam(json_bytes(p['tra_loi_ai'])), nguon=p['nguon']) for i, p in enumerate(bundle['phan_hoi'])]
        self.cong.nguon = json_bytes(dict(phien_ban=1, ma_yeu_cau=self.ctx.ma_yeu_cau,
            ma_ho_so_ram=h['dau'].ma_ho_so_ram, bam_ho_so=h['dau'].bam_ho_so,
            bam_tap_phan_hoi=bam(raw), bam_dau_vao=bam(json_bytes(dau_vao)), phan_hoi=chung))
        self.cong.raw_phan_hoi = raw
        self.v = self.c.giao_viec(GIU_DINH_DANG, dau_vao)
        self.q.cap(self.v, ma=self.ctx.ma_yeu_cau)
        self.do.append(dict(buoc='local_gia', giay=time.perf_counter() - dau, trang_thai='GIA'))
        return self

    def hau_kiem(self):
        k = self.chay('hau_kiem')
        self.cong.don()
        if k['trang_thai'] == 'XONG':
            self.ref_che = k['ket_qua']['truong']['tep_da_che']
            self.da_che = self.c.doc_tep(self.ref_che['tep_id'])
        return k

    def giao_mo(self, raw=None, *, ma=None, quyen=True):
        raw = self.da_che if raw is None else raw
        ref = self.c.them_tep('DEMO-AI.' + self.ca['loai'], raw, MIME[self.ca['loai']])
        boc = self.c.them_tep('DEMO-mau7.json', json_bytes(dict(
            ma_yeu_cau=ma or self.ctx.ma_yeu_cau, tep=ref)), 'application/json')
        self.v = self.c.giao_viec(MO, dict(loai='tep', tep=boc))
        if quyen:
            self.c.tep_con[self.v] = {ref['tep_id']}
        self.q.cap(self.v, ma=self.ctx.ma_yeu_cau, loai='mo_che')
        self.c.dang_mo = True
        return self

    def mo(self):
        k = self.chay('mo')
        if k['trang_thai'] == 'XONG':
            t = k['ket_qua']['truong']
            doi_chieu(t['mo_day_du'] is True and t['bi_danh_khong_ro_json'] == '[]', 'B10_MO_THIEU')
            self.da_mo = self.c.doc_tep(t['tep_da_mo_che']['tep_id'])
        return k

    def don(self):
        if self.ram._ban_ghi is not None:
            self.q.bao(self.ctx.ma_yeu_cau, 'KET_THUC')
        self.cong.don()


def chu_xml(e):
    if e is None:
        raise KiemLoi('B10_THIEU_VUNG_GOLD')
    return ''.join(x.text or '' for x in e.iter()
                   if x.tag.rsplit('}', 1)[-1] == 't') if list(e) else (e.text or '')


def vung_doc_lap(raw, vung):
    """Reader gold độc lập, không dùng reader/map/matcher của engine."""
    p = doc_phan(raw)
    root = ET.fromstring(p[vung['phan']])
    if 'o' in vung:
        e = root.find('.//s:c[@r="' + vung['o'] + '"]', NS)
        doi_chieu(e is not None, 'B10_THIEU_O_GOLD')
        if e.get('t') == 's':
            idx = int(e.find('s:v', NS).text)
            return chu_xml(list(ET.fromstring(p['xl/sharedStrings.xml']))[idx])
        if e.get('t') == 'inlineStr':
            return chu_xml(e.find('s:is', NS))
        return e.find('s:v', NS).text
    return chu_xml(root.find(vung['xpath'], NS))


def cau_truc(raw):
    def doi(e):
        return [e.tag, sorted(e.attrib.items()), [doi(x) for x in e]]
    return {t: doi(ET.fromstring(b)) for t, b in doc_phan(raw).items() if t.endswith('.xml') or t.endswith('.rels')}


def payloads(raw):
    ket = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        for i in z.infolist():
            at = i.header_offset
            n, x = struct.unpack_from('<HH', raw, at + 26)
            dau = at + 30 + n + x
            ket[i.filename] = raw[dau:dau + i.compress_size]
    return ket


def kiem_format(truoc, sau):
    doi_chieu(cau_truc(truoc) == cau_truc(sau), 'B10_DOI_FORMAT_CAU_TRUC')
    p, q = doc_phan(truoc), doc_phan(sau)
    cp, cq = payloads(truoc), payloads(sau)
    doi_chieu(set(p) == set(q), 'B10_DOI_PART')
    for t in p:
        if p[t] == q[t]:
            doi_chieu(cp[t] == cq[t], 'B10_DOI_PAYLOAD_BAT_BIEN')


def bo_dau(chu):
    # Oracle dò lọt cố tình khác normalization runtime, bỏ cả punctuation/Cf.
    return ''.join(c for c in ud.normalize('NFKD', chu).casefold()
                   if c.isalnum() and ud.category(c) != 'Mn')


def phan_nhan_dien_con(goc, chu):
    """Oracle bảo thủ với từng thành tố tên, kể cả chỉ còn hậu tố tên.

    Bỏ token alias rồi so tên đầy đủ và các âm tiết riêng của gold. Không
    dùng detector/matcher hoặc map của engine. Sai khác không còn thành tố
    gốc được ghi riêng là không khớp gold, không tự gọi là rò bản rõ.
    """
    chu = re.sub(r'\[\[.*?\]\]', '', chu, flags=re.S)
    sach = bo_dau(chu)
    if bo_dau(goc) in sach:
        return True
    danh_tu_chung = {'cong', 'ty', 'demo', 'trach', 'nhiem', 'huu', 'han', 'co', 'phan'}
    words = re.findall(r'[^\W_]+', ''.join(c for c in ud.normalize('NFKD', goc).casefold()
                        if ud.category(c) not in {'Mn', 'Cf'}))
    return any(bo_dau(w) in sach for w in words if w not in danh_tu_chung)


def kiem_gold(ca, raw, *, che):
    ket = dict(vung=0, span=0, span_lot=0, vung_lot=0, vung_bao_nham=0,
               tien_ngay_sai=0, gold_khong_khop=0, ma_vung_loi=[])
    for v in ca['gold']['vung']:
        chu = vung_doc_lap(raw, v)
        muon = v['chu']
        spans = v.get('span', [])
        if che:
            for a, z, i in reversed(spans):
                muon = muon[:a] + ca['dinh_danh'][i]['alias'] + muon[z:]
        ket['vung'] += 1
        ket['span'] += len(spans)
        if che and spans:
            so_lot = sum(phan_nhan_dien_con(v['chu'][a:z], chu) for a, z, _ in spans)
            ket['span_lot'] += so_lot
            ket['vung_lot'] += int(bool(so_lot))
            if not so_lot and chu != muon:
                ket['vung_bao_nham'] += 1
        elif chu != muon:
            ket['vung_bao_nham'] += 1
        if chu != muon:
            ket['ma_vung_loi'].append(v['ma'])
            ket['gold_khong_khop'] += 1
        for t in v.get('bat_bien', []):
            if t not in chu:
                ket['tien_ngay_sai'] += 1
    return ket


def sua_ai(raw, ca, kieu):
    """AI sửa DEMO: thêm chữ/tiền/ngày/format, hoặc phá alias có chủ đích."""
    p = {t: v.decode('utf-8') for t, v in doc_phan(raw).items()}
    alias = ca['dinh_danh'][0]['alias']
    moi = alias
    if kieu == 'mem':
        moi = ' '.join(alias.lower())
    elif kieu == 'hong':
        moi = alias[:-2] + '?]'
    elif kieu == 'la':
        moi = '[[B10-DEMO-CHUA-DUNG]]'
    elif kieu == 'ngoai_yeu_cau':
        moi = ca['kho_ngoai_yeu_cau'][0]['alias']
    if kieu in {'mem', 'hong', 'la', 'ngoai_yeu_cau'}:
        dem = 0
        for t in p:
            dem += p[t].count(alias)
            p[t] = p[t].replace(alias, moi)
        doi_chieu(dem > 0, 'B10_KHONG_CO_ALIAS_DE_THU')
    if ca['loai'] == 'docx':
        t = 'word/document.xml'
        p[t] = p[t].replace('</w:body>', doan_word(MOI) + '</w:body>')
        if kieu == 'run':
            doi_chieu(alias in p[t], 'B10_ALIAS_TACH_SAN')
            p[t] = p[t].replace(alias, alias[:6].lower() + '</w:t></w:r><w:r><w:rPr><w:b/><w:i/></w:rPr><w:t xml:space="preserve">' + alias[6:].lower(), 1)
        if kieu == 'format':
            p[t] = p[t].replace('<w:rPr>', '<w:rPr><w:color w:val="FF0000"/>', 1)
    else:
        t = 'xl/worksheets/sheet1.xml'
        them = '<s:row r="3"><s:c r="A3" t="inlineStr"><s:is><s:r><s:rPr><s:b/></s:rPr><s:t>' + escape(MOI) + '</s:t></s:r></s:is></s:c></s:row>'
        p[t] = p[t].replace('</s:sheetData>', them + '</s:sheetData>')
        if kieu == 'run':
            target = 'xl/sharedStrings.xml' if 'xl/sharedStrings.xml' in p else t
            # Đổi is/si tối giản thành rich text, giữ cell style/merge/hidden.
            x = re.search(r'<s:(?:si|is)><s:t>([^<]*)</s:t></s:(?:si|is)>', p[target])
            doi_chieu(x is not None and alias in x[1], 'B10_ALIAS_TACH_SAN')
            chu = x[1].replace(alias, alias.lower())
            duoi = chu[6:]
            start = x[0].split('>')[0] + '>'
            end = '</s:si>' if start.startswith('<s:si') else '</s:is>'
            p[target] = p[target][:x.start()] + start + '<s:r><s:rPr><s:b/></s:rPr><s:t>' + chu[:6] + '</s:t></s:r><s:r><s:rPr><s:i/></s:rPr><s:t>' + duoi + '</s:t></s:r>' + end + p[target][x.end():]
        if kieu == 'format':
            p['xl/styles.xml'] = p['xl/styles.xml'].replace('<s:font>', '<s:font><s:b/>', 1)
    return nen(p)


def kiem_noi_dung_moi(raw, loai):
    p = doc_phan(raw)
    if loai == 'docx':
        root = ET.fromstring(p['word/document.xml'])
        cac = [chu_xml(e) for e in root.findall('.//w:p', NS)]
        doi_chieu(MOI in cac, 'B10_MAT_NOI_DUNG_AI')
    else:
        v = dict(phan='xl/worksheets/sheet1.xml', o='A3')
        doi_chieu(vung_doc_lap(raw, v) == MOI, 'B10_MAT_NOI_DUNG_AI')


def doc_gold():
    raw = (THU_MUC / 'demo/mask_tep_held_out.json').read_bytes()
    v = json.loads(raw)
    doi_chieu(v['chi_demo'] is True and v['cloud'] is False, 'B10_GOLD_KHONG_DEMO')
    muon = v['sha256_noi_dung']
    doi_chieu(bam(json_bytes({k: x for k, x in v.items() if k != 'sha256_noi_dung'})) == muon, 'B10_SHA_GOLD_SAI')
    for ca in v['ca']:
        doi_chieu(bam(json_bytes(ca['gold'])) == ca['sha256_gold'], 'B10_SHA_GOLD_VUNG')
        doi_chieu(bam(dung(ca)) == ca['sha256_tep'], 'B10_SHA_FIXTURE_DOI')
        # Gold phải khớp nguyên văn trước bất kỳ handler/detector nào.
        if ca['ky_vong'] == 'ho_tro':
            for g in ca['gold']['vung']:
                doi_chieu(vung_doc_lap(dung(ca), g) == g['chu'], 'B10_GOLD_KHONG_KHOP_NGUON')
    return v, bam(raw)


def ma_loi(k):
    return k.get('loi', {}).get('ma', 'B10_KHONG_CO_MA') if k.get('loi') else 'B10_KHONG_CO_MA'


def phan_loai(k, ca):
    if k['trang_thai'] == 'XONG':
        return 'phat_hanh'
    if k['trang_thai'] == 'CHUA_RO':
        return 'chua_ro'
    if k['trang_thai'] == 'HUY':
        return 'huy'
    ma = ma_loi(k)
    if ma in {'MASK_TEP_CHUA_HO_TRO', 'MASK_QUA_GIOI_HAN', 'MASK_DINH_DANH_CHUA_DAT',
              'MASK_R3_CHUA_CHUNG_MINH', 'MASK_KHO_CAN_CORE', 'MASK_UNG_VIEN_CHUA_DAT'}:
        return 'chan_dung' if ca['ky_vong'] == 'chan' else 'chan_sai'
    return 'loi'


def kiem_ngan_khong_map(b):
    for bang in ('dinh_danh', 'bi_danh'):
        # xem_ngan là cửa debug của CoreGia, cố ý giữ giá trị seed bí mật.
        # Chỉ quan sát ảnh mà NganEngine thật trả cho engine (null+cờ).
        trang = b.app.ngan.tim(bang, loc={'vung_du_lieu': 'DEMO'}, gioi_han=100)
        doi_chieu(trang.tiep is None, 'B10_THIEU_TRANG_NGAN')
        ds = [d.gia_tri for d in trang.danh_sach]
        chu = json_bytes(ds).decode('utf-8')
        for t in b.ca['dinh_danh']:
            doi_chieu(t['chu'] not in chu and chuan_hoa(t['chu']) not in chu, 'B10_BAN_RO_RA_NGAN')
        doi_chieu(b.ctx.ma_yeu_cau not in chu, 'B10_MAP_YEU_CAU_RA_NGAN')
        if bang == 'dinh_danh':
            for d in ds:
                # CoreGia trả ảnh ngăn đã che đúng ngữ nghĩa SDK.
                gia = d
                if 'gia_tri_goc' in gia:
                    doi_chieu(gia['gia_tri_goc'] is None and gia['gia_tri_chuan'] is None, 'B10_NGAN_TRA_BAN_RO')
    kiem_metadata(b.c.nhat_ky)
    log = json_bytes(b.c.nhat_ky).decode('utf-8')
    doi_chieu(all(t['chu'] not in log for t in b.ca['dinh_danh']), 'B10_BAN_RO_RA_LOG')


def chay_ca(ca, *, sua='khong', thu_cong=None):
    b = None
    tracemalloc.start()
    dau = time.perf_counter()
    r = dict(ma=ca['ma'], loai=ca['loai'], ky_vong=ca['ky_vong'], sua=sua,
             sha256_tep=ca['sha256_tep'], phat_hanh=0, lot_span=0, lot_tep=0,
             bao_nham_vung=0, gold_span=0, gold_vung=0, mo='CHƯA ĐO',
             khong_ho_tro=0, ma_vung_loi=[], loi_kiem=[],
             gold_span_tong=sum(len(v['span']) for v in ca['gold']['vung']),
             gold_vung_tong=len(ca['gold']['vung']))
    try:
        b = Chuoi(ca, clock_thuc=bool(thu_cong))
        k = b.chuan_bi()
        if k['trang_thai'] == 'XONG':
            b.local_gia()
            k = b.hau_kiem()
        r['ket_qua'] = phan_loai(k, ca)
        if k['trang_thai'] != 'XONG':
            r['ma_loi'] = ma_loi(k)
            r['khong_ho_tro'] = int(ma_loi(k) == 'MASK_TEP_CHUA_HO_TRO')
            doi_chieu(b.ram._ban_ghi is None, 'B10_LOI_CHUA_DON_MAP')
            return r
        r['phat_hanh'] = 1
        doi_chieu(ca['ky_vong'] == 'ho_tro', 'B10_PHAT_HANH_TEP_PHAI_CHAN')
        g = kiem_gold(ca, b.da_che, che=True)
        r.update(lot_span=g['span_lot'], lot_tep=int(bool(g['span_lot'])),
                 bao_nham_vung=g['vung_bao_nham'], gold_span=g['span'], gold_vung=g['vung'],
                 ma_vung_loi=g['ma_vung_loi'], tien_ngay_sai=g['tien_ngay_sai'], gold_khong_khop=g['gold_khong_khop'])
        if g['gold_khong_khop']:
            r['loi_kiem'].append('B10_BAN_CHE_KHONG_KHOP_GOLD')
        kiem_format(b.raw, b.da_che)
        kiem_ngan_khong_map(b)
        r['sha256_che'] = bam(b.da_che)
        du = b.ram._ban_ghi.du_lieu
        r['ram_do_thi_bytes_map'] = kich_ram(du)
        s = du['tep_word' if ca['loai'] == 'docx' else 'tep_excel']
        r['bytes_goc_va_che'] = len(s['goc']) + len(s['da_che'])
        r['alias_trong_map'] = len(s['alias_nguyen_van']) if 'alias_nguyen_van' in s else len(s.get('aliases', {}))
        r['so_doan_local_gia'] = b.doan
        r['doi_local_that_giay'] = 'CHƯA ĐO'
        if thu_cong:
            raw_mo = thu_cong(b, r)
            if raw_mo is None:
                r['mo'] = 'Chờ Anh'
                return r
            sua = 'office_luu_lai' if raw_mo != b.da_che else 'khong'
            r['sua'] = sua
        else:
            raw_mo = b.da_che if sua == 'khong' else sua_ai(b.da_che, ca, sua)
        b.giao_mo(raw_mo)
        k = b.mo()
        if sua in {'hong', 'la', 'ngoai_yeu_cau'}:
            doi_chieu(k['trang_thai'] == 'LOI' and k['ket_qua'] is None
                      and ma_loi(k) == 'MASK_MO_CHE_KHONG_DAY_DU', 'B10_ALIAS_HONG_PHAT_HANH')
            r['mo'] = 'chan_dung'
        elif k['trang_thai'] == 'XONG':
            r['mo'] = 'du'
            r['sha256_mo'] = bam(b.da_mo)
            if sua == 'khong':
                # Chỉ so SHA toàn tệp khi bytes gốc được giữ tại RAM lúc mở.
                doi_chieu(b.da_mo == b.raw, 'B10_SHA_KHU_HOI_SAI')
            else:
                kiem_format(raw_mo, b.da_mo)
                if sua != 'office_luu_lai':
                    kiem_noi_dung_moi(b.da_mo, ca['loai'])
            gg = kiem_gold(ca, b.da_mo, che=False)
            doi_chieu(not gg['ma_vung_loi'], 'B10_MO_SAI_GOLD')
            if thu_cong:
                thu_cong.sau_mo(b, r)
        else:
            r['mo'], r['ma_loi_mo'] = k['trang_thai'], ma_loi(k)
            r['loi_kiem'].append('B10_MO_DU_KY_VONG_NHUNG_KHONG_CO_KET_QUA')
        doi_chieu(b.ram._ban_ghi is None and not b.goc_bg.du_lieu, 'B10_MO_CHUA_DON_MAP')
        doi_chieu(not b.c.cach_ly and b.c.so_doc_goc_luc_mo == 0, 'B10_CACH_LY_HOAC_DOC_GOC')
        return r
    except Exception as exc:
        r.setdefault('ket_qua', 'loi')
        r['loi_kiem'].append(str(exc) if isinstance(exc, KiemLoi) else 'B10_LOI_CONG_CU_' + type(exc).__name__)
        return r
    finally:
        r['toan_chuoi_giay'] = time.perf_counter() - dau
        r['python_peak_byte'] = tracemalloc.get_traced_memory()[1]
        r['os_peak_pid_byte'] = os_peak()
        r['buoc'] = b.do if b else []
        tracemalloc.stop()
        if b:
            b.don()


def thong_ke(ds):
    hop_le = [r for r in ds if not r['loi_kiem']]
    phat = [r for r in ds if r['phat_hanh']]
    so = Counter(r['ket_qua'] for r in ds)
    return dict(so_tep=len(ds), so_ma_tep_phan_biet=len({r['ma'] for r in ds}),
        so_ho_tro=sum(r['ky_vong'] == 'ho_tro' for r in ds),
        so_phai_chan=sum(r['ky_vong'] == 'chan' for r in ds), so_do_hop_le=len(hop_le),
        gold_span_toan_bo=sum(r['gold_span_tong'] for r in ds),
        gold_vung_toan_bo=sum(r['gold_vung_tong'] for r in ds),
        gold_span_nhom_ho_tro=sum(r['gold_span_tong'] for r in ds if r['ky_vong'] == 'ho_tro'),
        phat_hanh_che=sum(r['phat_hanh'] for r in ds), ket_qua=dict(so),
        khong_ho_tro=sum(r['khong_ho_tro'] for r in ds),
        loi_cong_cu_hoac_gold=sum(bool(r['loi_kiem']) for r in ds),
        lot_tep=dict(tu=sum(r['lot_tep'] for r in phat), mau=len(phat)),
        lot_span=dict(tu=sum(r['lot_span'] for r in phat), mau=sum(r['gold_span'] for r in phat)),
        bao_nham_vung=dict(tu=sum(r['bao_nham_vung'] for r in phat), mau=sum(r['gold_vung'] for r in phat)),
        bao_nham_tep_ho_tro=dict(tu=sum(r['ket_qua'] == 'chan_sai' or bool(r['bao_nham_vung']) for r in ds if r['ky_vong'] == 'ho_tro'), mau=sum(r['ky_vong'] == 'ho_tro' for r in ds)),
        mo=dict(Counter(r['mo'] for r in ds)),
        ket_luan_chat_luong='CHƯA ĐO Local thật; oracle gold giả không chứng minh recall/0 lọt. Chặn hết không đạt.')


def ca_kiem_thuat(g, loai='docx', i=0):
    """Đối chứng development tách hoàn toàn khỏi mẫu số held-out/ứng viên."""
    c = deepcopy([c for c in g['ca'] if c['loai'] == loai and c['ky_vong'] == 'ho_tro'][i])
    c['ma'], c['kiem_thuat'] = 'KT-' + loai + '-' + str(i), True
    for v in c['gold']['vung']:
        if v['chu'] == 'DEMO số sổ cái 73; tổng thu đã kiểm tra.':
            v['chu'] = 'nội dung.'
    c['sha256_tep'] = bam(dung(c))
    return c


def thu_do(ma, ham, *, ky_vong='nhan', lop='primitive', dai_luong=None,
           ma_ky_vong=('MASK_QUA_GIOI_HAN',)):
    """Đo gate thật, không thay hằng trần. Tách khỏi số đo toàn chuỗi."""
    tracemalloc.start()
    dau = time.perf_counter()
    ket = dict(ma=ma, lop=lop, ky_vong=ky_vong, dai_luong=dai_luong)
    try:
        with giam_sat():
            ham()
        ket['thuc_te'] = 'nhan'
    except LoiNghiepVu as exc:
        ket['thuc_te'], ket['ma_loi'] = 'chan', exc.ma
    except Exception as exc:
        ket['thuc_te'] = 'loi'
        ket['ma_loi'] = str(exc) if isinstance(exc, KiemLoi) else 'B10_LOI_CONG_CU_' + type(exc).__name__
    finally:
        ket['giay'] = time.perf_counter() - dau
        ket['python_peak_byte'] = tracemalloc.get_traced_memory()[1]
        ket['os_peak_pid_byte'] = os_peak()
        tracemalloc.stop()
    ket['dat'] = ket['thuc_te'] == ky_vong
    if ket['thuc_te'] == 'chan' and ky_vong == 'chan':
        ket['dat'] = ket['ma_loi'] in ma_ky_vong
    return ket


def zip_tho(ten, raw, payload):
    ten = ten.encode('ascii')
    crc, n, z = zlib.crc32(raw), len(raw), len(payload)
    h = struct.pack('<4s5H3I2H', b'PK\x03\x04', 20, 0, 8, 0, 33, crc, z, n, len(ten), 0) + ten
    c = struct.pack('<4s6H3I5H2I', b'PK\x01\x02', 20, 20, 0, 8, 0, 33, crc, z, n, len(ten), 0, 0, 0, 0, 32, 0) + ten
    return h + payload + c + struct.pack('<4s4H2IH', b'PK\x05\x06', 0, 0, 1, 1, len(c), len(h) + z, 0)


def zip_ratio(vuot=0):
    """DEFLATE EOF/CRC thật: ratio chính xác 200:1 hoặc +1 byte giải nén."""
    rg = random.Random(1611261007)
    for k in range(60):
        raw = rg.randbytes(k) + b'A' * (60000 + vuot - k)
        co = zlib.compressobj(6, wbits=-15)
        p = co.compress(raw) + co.flush(zlib.Z_SYNC_FLUSH)
        so = 300 - len(p) - 5
        if so >= 0 and so % 5 == 0:
            p += b'\x00\x00\x00\xff\xff' * (so // 5) + b'\x01\x00\x00\xff\xff'
            doi_chieu(zlib.decompress(p, -15) == raw and len(p) == 300, 'B10_RATIO_FIXTURE')
            return zip_tho('DEMO', raw, p)
    raise KiemLoi('B10_KHONG_DUNG_DUOC_RATIO')


def zip_giai_nen(n):
    rg = random.Random(1611261008)
    p = {}
    for i in range((n + 2*MIB - 1) // (2*MIB)):
        dai = min(2*MIB, n - i * 2*MIB)
        mau = rg.randbytes(24576)
        p['DEMO' + str(i)] = (mau * ((dai + len(mau) - 1) // len(mau)))[:dai]
    raw = nen(p)
    doi_chieu(len(raw) < MIB, 'B10_BIEN_CHAM_TRAN_KHAC')
    return raw


def chay_bien():
    from e_mask import zip_an_toan as z, xml_an_toan as x, doc_tep as d, ghi_zip as w
    rs = []
    khong = lambda: None
    # Mỗi fixture được dựng ngoài khoảng đo. Không dùng header khai giả.
    for plus in (0, 1):
        n = MIB + plus
        raw = nen({'DEMO': b'a' * (n - 106)}, cach=zipfile.ZIP_STORED)
        doi_chieu(len(raw) == n, 'B10_SAI_BIEN_CONTAINER')
        rs.append(thu_do('ZIP_VAO_' + str(plus), lambda raw=raw: z.doc_zip(raw, khong),
                         ky_vong='chan' if plus else 'nhan', dai_luong=dict(byte=n)))
        rs.append(thu_do('ZIP_RA_' + str(plus), lambda n=n: w._BoDem().ghi(b'a' * n),
                         ky_vong='chan' if plus else 'nhan', lop='bo_dem_writer', dai_luong=dict(byte=n)))
        for ten, n in (('PHAN', 2*MIB + plus), ('TONG', 8*MIB + plus)):
            raw = zip_giai_nen(n) if ten == 'TONG' else nen({'DEMO': (random.Random(71).randbytes(24576) * 86)[:n]})
            rs.append(thu_do('ZIP_' + ten + '_' + str(plus), lambda raw=raw: z.doc_zip(raw, khong),
                ky_vong='chan' if plus else 'nhan', dai_luong=dict(byte_giai_nen=n, byte_zip=len(raw))))
        raw = nen({'D' + str(i): b'DEMO' for i in range(256 + plus)})
        rs.append(thu_do('ZIP_SO_PHAN_' + str(plus), lambda raw=raw: z.doc_zip(raw, khong),
                         ky_vong='chan' if plus else 'nhan', dai_luong=dict(so_phan=256 + plus)))
        raw = zip_ratio(plus)
        rs.append(thu_do('ZIP_RATIO_' + str(plus), lambda raw=raw: z.doc_zip(raw, khong),
                         ky_vong='chan' if plus else 'nhan', dai_luong=dict(byte_nen=300, byte_giai_nen=60000 + plus)))
        for ten, noi, ns, luong in (
            ('DO_SAU', '<w:n>' * (64 + plus) + '</w:n>' * (64 + plus), 'w', 64 + plus),
            ('SO_NUT', '<w:n>' + '<w:n/>' * (99999 + plus) + '</w:n>', 'w', 100000 + plus),
            ('SO_SHEET', '<s:n>' + '<s:sheet/>' * (50 + plus) + '</s:n>', 's', 50 + plus),
            ('SO_O', '<s:n>' + '<s:c/>' * (20000 + plus) + '</s:n>', 's', 20000 + plus),
            ('KY_TU_VAO', '<w:n>' + 'a' * (500000 + plus) + '</w:n>', 'w', 500000 + plus)):
            noi = noi.replace('>', ' xmlns:' + ns + '=' + quoteattr(NS[ns]) + '>', 1).encode('utf-8')
            rs.append(thu_do('XML_' + ten + '_' + str(plus),
                lambda raw=noi, ns=ns: x.doc_xml(raw, namespace={NS[ns]}, ngan_sach=x.NganSachXML(), kiem_huy=khong),
                ky_vong='chan' if plus else 'nhan', dai_luong=dict(so=luong, byte_xml=len(noi))))
        for ten, ham, luong in (
            ('KY_TU_RA', lambda n=2000000+plus: d.kiem_van_ban_ra('a' * n, kiem_huy=khong), 2000000 + plus),
            ('BYTE_RA', lambda n=8*MIB+plus: d.kiem_byte_chu_ra(n), 8*MIB + plus)):
            rs.append(thu_do(ten + '_' + str(plus), ham, ky_vong='chan' if plus else 'nhan',
                             lop='gate_so_byte' if ten == 'BYTE_RA' else 'gate_van_ban', dai_luong=dict(so=luong)))
        for loai, cap in (('bao_cao', 256*1024), ('chuyen_tiep', 64*1024), ('khuon', 32*1024)):
            v = {'v': 'a' * (cap - 8 + plus)}
            doi_chieu(len(json_bytes(v)) == cap + plus, 'B10_SAI_BIEN_JSON')
            rs.append(thu_do('JSON_' + loai.upper() + '_' + str(plus),
                lambda v=v, loai=loai: d.ma_hoa_json_noi_bo(v, loai=loai, kiem_huy=khong),
                ky_vong='chan' if plus else 'nhan', dai_luong=dict(byte=cap + plus)))
    rs.append(dict(ma='BYTE_RA_DOC_LAP_TOAN_CHUOI', dat=None, thuc_te='CHƯA ĐO',
        ly_do='8 MiB UTF-8 không thể chạm độc lập khi đồng thời <=2.000.000 Unicode scalar (tối đa 8.000.000 byte). Gate số byte đã đo riêng; không nhận full B + Local ở các trần này.'))
    rs.append(dict(ma='BUDGET_MAY_DICH_CONCURRENCY', dat=None, thuc_te='CHƯA ĐO',
        ly_do='60/300 giây là dự toán, chưa hard cap production; budget/affinity/streaming/413 và Local thật Chờ Core/Anh.'))
    return rs


def bo_ram(*, ttl=600, han=None, instance='b10-instance-a', dang_ky=None, ma=None):
    q, dh = QuyenGia(instance=instance, dang_ky=dang_ky), DongHo()
    q.han = han
    ram = KhoAnhXaRAM(quyen=q, dong_ho=dh, hen_gio=dh.hen_gio)
    v = SimpleNamespace(id='viec-demo-b10', dau_vao=dict(loai='van_ban', van_ban='nội dung.'),
        tham_so={}, ngu_canh=dict(phap_nhan_id='pn-demo'),
        cau_hinh=dict(thoi_han_anh_xa_giay=ttl), kiem_huy=lambda: None)
    ctx = q.cap(v.id, ma=ma)
    with ram.buoc(v) as h:
        h.du_lieu['canary_b10'] = bytearray(b'DEMO-canary-b10')
        h.cho_ai()
    return SimpleNamespace(q=q, dh=dh, ram=ram, v=v, ctx=ctx, bg=ram._ban_ghi)


def doi_loi(ham, ma):
    try:
        ham()
    except LoiNghiepVu as exc:
        doi_chieu(exc.ma == ma, 'B10_SAI_MA_LOI')
        return
    raise KiemLoi('B10_THIEU_LOI')


def thu_mo_ram(b, *, ram=None, v=None, ma=None):
    vv = v or b.v
    if (vv.id, 'mo_che') not in b.q.ve:
        b.q.cap(vv.id, ma=b.ctx.ma_yeu_cau, loai='mo_che')
    with (ram or b.ram).buoc(vv, loai='mo_che', ma_yeu_cau=ma or b.ctx.ma_yeu_cau) as h:
        h.kiem()


def chay_vong_doi(g):
    rs = []
    def test(ma, ham):
        rs.append(thu_do(ma, ham, lop='vong_doi_CoreGia'))
    for ttl in (60, 600, 900):
        for delta in (-0.001, 0, 1):
            def ham(ttl=ttl, delta=delta):
                b = bo_ram(ttl=ttl)
                b.dh.tien(ttl + delta)
                if delta < 0:
                    doi_chieu(b.ram._ban_ghi is b.bg, 'B10_HET_HAN_SOM')
                    thu_mo_ram(b)
                else:
                    doi_chieu(b.ram._ban_ghi is None and not b.bg.du_lieu, 'B10_TIMER_KHI_RANH')
                    doi_loi(lambda: thu_mo_ram(b), 'MASK_ANH_XA_KHONG_CON')
                doi_chieu(b.ram._ban_ghi is None and not b.bg.du_lieu, 'B10_MAP_CON_SAU_MO')
            test('TTL_' + str(ttl) + '_' + str(delta), ham)
    for delta in (-0.001, 0, 1):
        def ham(delta=delta):
            b = bo_ram(han=130.)
            doi_chieu(b.bg.han == 130., 'B10_KHONG_LAY_HAN_CORE_SOM')
            b.dh.tien(30 + delta)
            if delta < 0:
                thu_mo_ram(b)
            else:
                doi_loi(lambda: thu_mo_ram(b), 'MASK_ANH_XA_KHONG_CON')
            doi_chieu(not b.bg.du_lieu, 'B10_CORE_HAN_CHUA_DON')
        test('HAN_CORE_' + str(delta), ham)
    def snapshot():
        b = bo_ram()
        b.v.cau_hinh['thoi_han_anh_xa_giay'] = 900
        b.dh.tien(600)
        doi_chieu(b.ram._ban_ghi is None and not b.bg.du_lieu, 'B10_TTL_TRUOT_CAU_HINH')
    test('TTL_SNAPSHOT_KHONG_TRUOT', snapshot)
    for trang in ('HUY', 'LOI', 'KET_THUC', 'MAT_QUYEN', 'MAT_LEASE'):
        def ham(trang=trang):
            b = bo_ram()
            b.q.bao(b.ctx.ma_yeu_cau, trang)
            doi_chieu(b.ram._ban_ghi is None and not b.bg.du_lieu, 'B10_VONG_DOI_KHI_RANH')
            doi_loi(lambda: thu_mo_ram(b), 'MASK_ANH_XA_KHONG_CON')
        test('AI_DANG_CHO_' + trang, ham)
    def khong_day_map():
        b = bo_ram()
        v2 = deepcopy(b.v)
        v2.id = 'viec-demo-b10-hai'
        b.q.cap(v2.id)
        def hai():
            with b.ram.buoc(v2):
                pass
        doi_loi(hai, 'MASK_CHUOI_DANG_XU_LY')
        doi_chieu(b.ram._ban_ghi is b.bg and bool(b.bg.du_lieu), 'B10_DAY_MAP_CU')
        thu_mo_ram(b)
    test('CHUOI_THU_HAI_KHONG_DAY_MAP', khong_day_map)
    def retry():
        b = bo_ram()
        han = b.bg.han
        with b.ram.buoc(b.v) as h:
            doi_chieu(h.thu_lai, 'B10_KHONG_NHAN_RETRY')
            h.cho_ai()
        doi_chieu(b.bg.han == han, 'B10_RETRY_NOI_TTL')
        b.v.dau_vao['van_ban'] += 'thêm.'
        def doi():
            with b.ram.buoc(b.v):
                pass
        doi_loi(doi, 'MASK_DAU_VAO_THAY_DOI')
        doi_chieu(not b.bg.du_lieu, 'B10_RETRY_DOI_CHUA_DON')
    test('RETRY_VA_DOI_INPUT', retry)
    def worker():
        b = bo_ram()
        q = QuyenGia(instance='b10-instance-b', dang_ky=b.q.da_cap)
        q.ve = b.q.ve.copy()
        q.cap(b.v.id, ma=b.ctx.ma_yeu_cau, loai='mo_che')
        ram = KhoAnhXaRAM(quyen=q, dong_ho=b.dh, hen_gio=b.dh.hen_gio)
        def mo():
            with ram.buoc(b.v, loai='mo_che', ma_yeu_cau=b.ctx.ma_yeu_cau):
                pass
        doi_loi(mo, 'MASK_ANH_XA_KHONG_CON')
        doi_chieu(b.ram._ban_ghi is b.bg and bool(b.bg.du_lieu), 'B10_WORKER_PHA_MAP_KHAC')
        thu_mo_ram(b)
    test('WORKER_KHAC_KHONG_AFFINITY', worker)
    def restart():
        b = bo_ram()
        b.q.bao(b.ctx.ma_yeu_cau, 'KET_THUC')
        ram = KhoAnhXaRAM(quyen=b.q, dong_ho=b.dh, hen_gio=b.dh.hen_gio)
        doi_loi(lambda: thu_mo_ram(b, ram=ram), 'MASK_ANH_XA_KHONG_CON')
        doi_chieu(not b.bg.du_lieu, 'B10_RESTART_MAP_CON')
    test('RESTART_GIUA_AI_VA_MO', restart)
    def double_open():
        from concurrent.futures import ThreadPoolExecutor
        from threading import Event
        b, vao, tiep = bo_ram(), Event(), Event()
        b.q.cap(b.v.id, ma=b.ctx.ma_yeu_cau, loai='mo_che')
        def mot():
            with b.ram.buoc(b.v, loai='mo_che', ma_yeu_cau=b.ctx.ma_yeu_cau):
                vao.set()
                doi_chieu(tiep.wait(2), 'B10_DONG_BO_THREAD')
        with ThreadPoolExecutor(max_workers=2) as ex:
            f = ex.submit(mot)
            doi_chieu(vao.wait(2), 'B10_DONG_BO_THREAD')
            try:
                doi_loi(lambda: thu_mo_ram(b), 'MASK_BUOC_DANG_XU_LY')
            finally:
                tiep.set()
            f.result(timeout=2)
        doi_loi(lambda: thu_mo_ram(b), 'MASK_ANH_XA_KHONG_CON')
        doi_chieu(not b.bg.du_lieu, 'B10_DOUBLE_OPEN_MAP_CON')
    test('DOUBLE_OPEN_DONG_THOI_VA_REPLAY', double_open)
    for field in ('module', 'nguoi_gui', 'tai_lieu', 'vung'):
        def ham(field=field):
            b = bo_ram()
            b.q.scope = {field: 'THAT' if field == 'vung' else 'khac-demo'}
            doi_loi(lambda: thu_mo_ram(b), 'MASK_MA_YEU_CAU')
            b.q.scope.clear()
            thu_mo_ram(b)
        test('QUYEN_' + field.upper(), ham)
    def caller():
        b = bo_ram()
        doi_loi(lambda: thu_mo_ram(b, ma='ma-caller-demo'), 'MASK_MA_YEU_CAU')
        thu_mo_ram(b)
    test('MA_CALLER_KHONG_CAP_QUYEN', caller)
    for ttl in (59, 901, True, 600.5):
        test('TTL_CAU_HINH_SAI_' + str(ttl), lambda ttl=ttl: doi_loi(lambda: bo_ram(ttl=ttl), 'MASK_CAU_HINH_KHONG_HOP_LE'))
    return rs


def chuoi_san(g, loai='docx'):
    b = Chuoi(ca_kiem_thuat(g, loai))
    try:
        doi_chieu(b.chuan_bi()['trang_thai'] == 'XONG', 'B10_DOI_CHUNG_CHUAN_BI')
        b.local_gia()
        doi_chieu(b.hau_kiem()['trang_thai'] == 'XONG', 'B10_DOI_CHUNG_HAU_KIEM')
        return b
    except BaseException:
        b.don()
        raise


def chay_tich_hop(g):
    rs, tep = [], []
    # 12 đối chứng cấu trúc: cùng các vùng nhưng văn bản kiểm cơ học tách
    # khỏi gold chất lượng. Không đổi nhãn/bytes bộ ứng viên sau khi xem đo.
    for loai in ('docx', 'xlsx'):
        for i in range(6):
            tep.append(chay_ca(ca_kiem_thuat(g, loai, i)))
        for sua in ('them', 'format', 'mem', 'run', 'hong', 'la', 'ngoai_yeu_cau'):
            tep.append(chay_ca(ca_kiem_thuat(g, loai), sua=sua))
    def test(ma, ham):
        rs.append(thu_do(ma, ham, lop='chuoi_CoreGia'))
    for provider in ('cloud', 'sai_span', 'thieu'):
        def ham(provider=provider):
            b = Chuoi(ca_kiem_thuat(g))
            try:
                doi_chieu(b.chuan_bi()['trang_thai'] == 'XONG', 'B10_DOI_CHUNG_CHUAN_BI')
                b.local_gia(provider='cloud' if provider == 'cloud' else 'local',
                            sai_span=provider == 'sai_span', thieu=provider == 'thieu')
                k = b.hau_kiem()
                doi_chieu(k['trang_thai'] == 'LOI' and k['ket_qua'] is None, 'B10_LOCAL_SAI_PHAT_HANH')
                doi_chieu(b.ram._ban_ghi is None and b.c.so_upload == 0, 'B10_LOCAL_SAI_CON_MAP')
            finally:
                b.don()
        test('LOCAL_' + provider.upper(), ham)
    for trang in ('HUY', 'LOI', 'MAT_LEASE', 'MAT_QUYEN'):
        def ham(trang=trang):
            b = Chuoi(ca_kiem_thuat(g))
            try:
                doi_chieu(b.chuan_bi()['trang_thai'] == 'XONG', 'B10_DOI_CHUNG_CHUAN_BI')
                bg = b.ram._ban_ghi
                b.q.bao(b.ctx.ma_yeu_cau, trang)
                doi_chieu(not bg.du_lieu and b.ram._ban_ghi is None and b.c.so_upload == 0, 'B10_AI_LOI_CON_MAP')
            finally:
                b.don()
        test('CHUOI_AI_' + trang, ham)
    for ack in ('nhan', 'ra'):
        def ham(ack=ack):
            b = chuoi_san(g)
            try:
                bg = b.ram._ban_ghi
                b.cong.mat_ack = ack
                b.giao_mo()
                k = b.mo()
                doi_chieu(k['trang_thai'] == 'CHUA_RO' and k['ket_qua'] is None, 'B10_ACK_BAO_THANH_CONG')
                doi_chieu(b.ram._ban_ghi is None and not bg.du_lieu and not b.c.cach_ly, 'B10_ACK_CON_MAP')
                nhan = b.cong.dem['mo_duoc_nhan']
                doi_chieu(nhan == int(ack == 'ra'), 'B10_ACK_KHONG_RO_BIEN_TIEP_NHAN')
                b.giao_mo()
                k = b.mo()
                doi_chieu(k['trang_thai'] == 'LOI' and k['ket_qua'] is None
                          and ma_loi(k) == 'MASK_ANH_XA_KHONG_CON', 'B10_ACK_TAI_TAO_MAP')
            finally:
                b.don()
        test('ACK_MO_' + ack.upper(), ham)
    def hai_chuoi():
        b = chuoi_san(g)
        try:
            alias = b.ca['dinh_danh'][0]['alias']
            doi_chieu(alias in vung_doc_lap(b.da_che, b.ca['gold']['vung'][0]), 'B10_THIEU_ALIAS_CHINH_THUC')
            bg = b.ram._ban_ghi
            b.giao_mo(); doi_chieu(b.mo()['trang_thai'] == 'XONG')
            doi_chieu(not bg.du_lieu and b.ram._ban_ghi is None)
            cu = b.ctx.ma_yeu_cau
            b.ctx = b.q.cap('chuoi-hai-demo')
            doi_chieu(cu != b.ctx.ma_yeu_cau)
            b.cong.i = 0
            b.v = b.c.giao_viec(CHUAN_BI, b.dau)
            b.q.cap(b.v, ma=b.ctx.ma_yeu_cau)
            doi_chieu(b.chuan_bi()['trang_thai'] == 'XONG')
            b.local_gia(); doi_chieu(b.hau_kiem()['trang_thai'] == 'XONG')
            doi_chieu(alias in vung_doc_lap(b.da_che, b.ca['gold']['vung'][0]), 'B10_ALIAS_CHINH_THUC_KHONG_DUNG_LAI')
            doi_chieu(bg is not b.ram._ban_ghi and not bg.du_lieu, 'B10_MAP_QUA_CHUOI')
            kiem_ngan_khong_map(b)
            b.giao_mo(); doi_chieu(b.mo()['trang_thai'] == 'XONG')
        finally:
            b.don()
    test('HAI_CHUOI_ALIAS_CHUNG_MAP_RIENG', hai_chuoi)
    def het_han_luc_mo():
        b = chuoi_san(g)
        try:
            bg = b.ram._ban_ghi
            b.cong.moc = lambda m, v: b.dh.tien(600) if m == 'mo_nhan' else None
            b.giao_mo(); k = b.mo()
            doi_chieu(k['trang_thai'] == 'LOI' and k['ket_qua'] is None, 'B10_TTL_GIUA_BAN_GIAO')
            doi_chieu(not bg.du_lieu and b.ram._ban_ghi is None and not b.c.cach_ly)
            doi_chieu(b.cong.dem['mo_duoc_nhan'] == 0)
        finally:
            b.don()
    test('TTL_DUA_BAN_GIAO_KHONG_PHAT_HANH', het_han_luc_mo)
    def duyet_giua_chuoi():
        from e_mask.kho_ngan import KhoNganBiMat
        from e_mask.duyet_dinh_danh import DuyetDinhDanh
        b = chuoi_san(g)
        try:
            bg, aliases = b.ram._ban_ghi, dict(b.ram._ban_ghi.du_lieu['tep_word']['alias_nguyen_van'])
            nl = 'mask.che_van_ban@1'
            def admin(v):
                # Mô phỏng Core/Admin đặt lại trạng thái cần duyệt trên cùng ID.
                # Không sao bí mật hoặc sửa map hiện có. R7 duyệt qua biên nhận.
                t = v.ngan.tim('dinh_danh', loc={'gia_tri_chuan': chuan_hoa(b.ca['dinh_danh'][0]['chu'])}, gioi_han=1).danh_sach[0]
                ident = t.gia_tri['id_dinh_danh']
                with v.ngan.lo() as lo:
                    lo.sua('dinh_danh', {'id_dinh_danh': ident}, {'trang_thai': 'CHO_DUYET'}, row_version=t.row_version)
                d = v.ngan.doc('dinh_danh', {'id_dinh_danh': ident})
                class Admin:
                    def xac_minh_admin(self):
                        return 'DEMO'
                    @contextmanager
                    def bien_nhan_duyet(self, viec, **kw):
                        doi_chieu(kw['bien_nhan'] == 'b' * 32)
                        yield dict(id_dinh_danh=ident, row_version=d.row_version)
                DuyetDinhDanh(v, Admin()).duyet(ident, d.row_version,
                    bien_nhan='b' * 32, ma_junsky='KH-DEMO-B10-DA-DUYET')
                return dict(loai='van_ban_da_che', van_ban_da_che=dict(phien_ban=1,
                    van_ban='nội dung.', ma_yeu_cau=b.ctx.ma_yeu_cau, con_sot=[], kiem_tien_ngay=True, chuyen_tiep={}))
            b.app._ham[nl] = admin
            b.v = b.c.giao_viec(nl, dict(loai='van_ban', van_ban='nội dung.'))
            doi_chieu(b.chay('admin_gia')['trang_thai'] == 'XONG', 'B10_ADMIN_GIA_LOI')
            doi_chieu(bg.du_lieu['tep_word']['alias_nguyen_van'] == aliases, 'B10_ADMIN_DOI_MAP_DANG_SONG')
            b.giao_mo(); doi_chieu(b.mo()['trang_thai'] == 'XONG')
            doi_chieu(b.da_mo == b.raw and not bg.du_lieu, 'B10_ADMIN_LAM_HONG_MO')
        finally:
            b.don()
    test('ADMIN_DUYET_GIUA_CHUOI_MAP_GHIM', duyet_giua_chuoi)
    for thieu in (False, True):
        def nhieu_doan(thieu=thieu):
            ca = ca_kiem_thuat(g)
            ca['lap_doan'] = True
            b = Chuoi(ca)
            try:
                doi_chieu(b.chuan_bi()['trang_thai'] == 'XONG' and b.doan > 1, 'B10_KHONG_CO_NHIEU_DOAN')
                b.local_gia(thieu=thieu)
                k = b.hau_kiem()
                if thieu:
                    doi_chieu(k['trang_thai'] == 'LOI' and k['ket_qua'] is None
                              and b.ram._ban_ghi is None and b.c.so_upload == 0, 'B10_THIEU_DOAN_PHAT_HANH')
                else:
                    doi_chieu(k['trang_thai'] == 'XONG', 'B10_DU_DOAN_BI_LOI')
                    b.giao_mo(); doi_chieu(b.mo()['trang_thai'] == 'XONG' and b.da_mo == b.raw)
                    doi_chieu(b.ram._ban_ghi is None and not b.goc_bg.du_lieu)
            finally:
                b.don()
        test('LOCAL_NHIEU_DOAN_' + ('THIEU' if thieu else 'DU'), nhieu_doan)
    def chua_ro_dang_cho():
        b = bo_ram()
        def cho():
            with b.ram.buoc(b.v) as h:
                h.cho_ai()
                raise ChuaRo('DEMO-ACK')
        try:
            cho()
        except ChuaRo:
            pass
        doi_chieu(b.ram._ban_ghi is b.bg and bool(b.bg.du_lieu), 'B10_CHUA_RO_DON_QUA_SOM')
        b.dh.tien(600)
        doi_chieu(b.ram._ban_ghi is None and not b.bg.du_lieu, 'B10_CHUA_RO_VUOT_TTL')
    test('AI_CHUA_RO_CHI_GIU_TRONG_TTL', chua_ro_dang_cho)
    def ack_chot():
        b = Chuoi(ca_kiem_thuat(g))
        try:
            doi_chieu(b.chuan_bi()['trang_thai'] == 'XONG')
            b.local_gia()
            b.cong.mat_ack = 'chot'
            k = b.hau_kiem()
            doi_chieu(k['trang_thai'] == 'CHUA_RO' and k['ket_qua'] is None, 'B10_CHOT_ACK_KHONG_CHUA_RO')
            doi_chieu(b.cong.dem['chot'] == 1 and b.ram._ban_ghi is None
                      and b.c.so_upload == 0, 'B10_CHOT_ACK_CON_MAP')
        finally:
            b.don()
    test('MAT_ACK_SAU_CHOT_METADATA', ack_chot)
    def acl_tep_con():
        b = chuoi_san(g)
        try:
            b.giao_mo(quyen=False)
            k = b.mo()
            doi_chieu(k['trang_thai'] == 'LOI' and k['ket_qua'] is None, 'B10_SAI_ACL_TEP_PHAT_HANH')
            doi_chieu(b.ram._ban_ghi is None and b.cong.dem['mo_duoc_nhan'] == 0, 'B10_ACL_CON_MAP')
        finally:
            b.don()
    test('MO_SAI_ACL_THAM_CHIEU_CON', acl_tep_con)
    return rs, tep


class DongHoThuc:
    def __call__(self):
        return time.monotonic()

    def hen_gio(self, giay, ham):
        from threading import Timer
        t = Timer(giay, ham)
        t.daemon = True
        return t


def kiem_worker_rieng():
    q, dh = QuyenGia(), DongHo()
    ram = KhoAnhXaRAM(quyen=q, dong_ho=dh, hen_gio=dh.hen_gio)
    v = SimpleNamespace(id='worker-demo', dau_vao={'loai': 'van_ban', 'van_ban': 'nội dung.'},
        tham_so={}, ngu_canh={'phap_nhan_id': 'pn-demo'}, cau_hinh={}, kiem_huy=lambda: None)
    q.cap(v.id, ma='chuoi-demo-khong-truyen-map', loai='mo_che')
    def mo():
        with ram.buoc(v, loai='mo_che', ma_yeu_cau='chuoi-demo-khong-truyen-map'):
            pass
    with giam_sat():
        doi_loi(mo, 'MASK_ANH_XA_KHONG_CON')
    return dict(dat=True, ghi_tep=IO_DANG_KIEM[1], mang=IO_DANG_KIEM[2])


def kiem_them():
    rs = []
    def processes():
        # Hai Python PID sạch, không argv/IPC/env mang map/gốc/mã yêu cầu.
        b = bo_ram(ma='chuoi-demo-khong-truyen-map')
        cu = IO_DANG_KIEM[0]
        IO_DANG_KIEM[0] = False
        try:
            for _ in range(2):
                p = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--worker-gia'],
                    capture_output=True, timeout=30, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                doi_chieu(p.returncode == 0 and not p.stderr, 'B10_WORKER_THAT_LOI')
                d = json.loads(p.stdout)
                doi_chieu(d == dict(dat=True, ghi_tep=0, mang=0), 'B10_WORKER_TRUYEN_DU_LIEU')
                doi_chieu(b.ram._ban_ghi is b.bg and bool(b.bg.du_lieu), 'B10_PROCESS_DAY_MAP_CHA')
        finally:
            IO_DANG_KIEM[0] = cu
            thu_mo_ram(b)
    rs.append(thu_do('HAI_PROCESS_GIA_DOC_LAP_KHONG_MAP', processes, lop='process_CoreGia'))
    def timer_thread():
        from threading import Timer, Event
        q, dh, done = QuyenGia(), DongHo(), Event()
        def hen(giay, ham):
            def goi():
                ham()
                done.set()
            t = Timer(.03, goi)
            t.daemon = True
            return t
        ram = KhoAnhXaRAM(quyen=q, dong_ho=dh, hen_gio=hen)
        v = SimpleNamespace(id='timer-demo', dau_vao=dict(loai='van_ban', van_ban='nội dung.'),
            tham_so={}, ngu_canh={'phap_nhan_id': 'pn-demo'}, cau_hinh={}, kiem_huy=lambda: None)
        q.cap(v.id)
        with ram.buoc(v) as h:
            h.du_lieu['canary_b10'] = b'DEMO'
            h.cho_ai()
        bg = ram._ban_ghi
        dh.luc += 600  # Đổi clock giả; callback chạy bằng thread Timer thật.
        doi_chieu(done.wait(2) and ram._ban_ghi is None and not bg.du_lieu, 'B10_TIMER_THREAD_KHI_RANH')
    rs.append(thu_do('TIMER_THREAD_KHI_RANH_CLOCK_GIA', timer_thread, lop='timer_R4'))
    def ghim():
        q = QuyenGia()
        q.ghim = False
        ram = KhoAnhXaRAM(quyen=q)
        doi_loi(ram.kiem_san_sang, 'MASK_CHUOI_CHUA_GHIM')
    rs.append(thu_do('CONCURRENCY_MOT_KHONG_THAY_AFFINITY', ghim, lop='R4'))
    return rs


def kiem_tan_cong(g):
    from e_mask.zip_an_toan import doc_zip
    from e_mask.doc_word import doc_word
    from e_mask.doc_excel import doc_excel
    rs = []
    khong = lambda: None
    goc = nen({'DEMO': b'DEMO'})
    for ten in ('/DEMO', 'C:/DEMO', 'DEMO\\x', '//DEMO/x'):
        raw = nen({ten: b'DEMO'})
        rs.append(thu_do('ZIP_TEN_TAN_CONG_' + str(len(rs)), lambda raw=raw: doc_zip(raw, khong),
            ky_vong='chan', lop='ZIP_tan_cong', ma_ky_vong=('MASK_TEP_CHUA_HO_TRO',)))
    raw = nen({'DEMO': b'DEMO', 'demo': b'DEMO'})
    rs.append(thu_do('ZIP_TRUNG_CASEFOLD', lambda: doc_zip(raw, khong), ky_vong='chan',
                     lop='ZIP_tan_cong', ma_ky_vong=('MASK_TEP_CHUA_HO_TRO',)))
    for ten in ('encrypted', 'method', 'crc', 'size', 'overlap', 'trailing'):
        raw = bytearray(goc)
        c = raw.find(b'PK\x01\x02')
        if ten == 'encrypted':
            struct.pack_into('<H', raw, 6, 1); struct.pack_into('<H', raw, c+8, 1)
        elif ten == 'method':
            struct.pack_into('<H', raw, 8, 12); struct.pack_into('<H', raw, c+10, 12)
        elif ten == 'crc':
            struct.pack_into('<I', raw, 14, 1); struct.pack_into('<I', raw, c+16, 1)
        elif ten == 'size':
            struct.pack_into('<I', raw, 22, 1); struct.pack_into('<I', raw, c+24, 1)
        elif ten == 'overlap':
            struct.pack_into('<I', raw, c+42, 1)
        else:
            raw.extend(b'DEMO')
        raw = bytes(raw)
        rs.append(thu_do('ZIP_' + ten.upper(), lambda raw=raw: doc_zip(raw, khong), ky_vong='chan',
            lop='ZIP_tan_cong', ma_ky_vong=('MASK_TEP_CHUA_HO_TRO', 'MASK_QUA_GIOI_HAN')))
    for loai, ham in (('docx', doc_word), ('xlsx', doc_excel)):
        for kieu, them in (('DTD', '<!DOCTYPE DEMO [<!ENTITY x "DEMO">]>'),
                           ('PI', '<?DEMO private?>'), ('COMMENT', '<!--DEMO-->')):
            ca = ca_kiem_thuat(g, loai)
            p = doc_phan(dung(ca))
            ten = 'word/document.xml' if loai == 'docx' else 'xl/workbook.xml'
            s = p[ten].decode('utf-8')
            idx = s.find('?>') + 2
            p[ten] = (s[:idx] + them + s[idx:]).encode('utf-8')
            raw = nen(p)
            rs.append(thu_do(loai.upper() + '_' + kieu, lambda raw=raw, ham=ham: ham(raw, kiem_huy=khong),
                ky_vong='chan', lop='OOXML_tan_cong', ma_ky_vong=('MASK_TEP_CHUA_HO_TRO',)))
    return rs


def ghi_hien_vat(thu_muc, ten, raw):
    p = thu_muc / ten
    doi_chieu(p.parent.resolve() == thu_muc.resolve() and not p.exists(), 'B10_HIEN_VAT_DA_CO')
    with p.open('xb') as f:
        f.write(raw)
    return p


class OfficeThuCong:
    """Chỉ Anh chọn --that; không tự mở app, COM, macro hay gọi mạng."""
    def __init__(self, thu_muc):
        self.thu_muc = thu_muc

    def __call__(self, b, r):
        ca, folder = b.ca, self.thu_muc
        ma = re.sub('[^A-Za-z0-9_-]', '-', ca['ma'])
        # Nguồn là fixture công cụ tự dựng, không xuất state/gốc RAM engine.
        ghi_hien_vat(folder, 'DEMO-' + ma + '-nguon.' + ca['loai'], dung(ca))
        p = ghi_hien_vat(folder, 'DEMO-' + ma + '-da-che.' + ca['loai'], b.da_che)
        print('Anh mở nguồn và tệp đã che DEMO-' + ma + ' bằng Office thủ công; kiểm font/run/bảng/merge/notes/ẩn hàng-cột/style/tiền-ngày/properties/repair warning.')
        print('Anh lưu, đóng rồi mở lại tệp đã che. Bytes thay đổi sẽ đi nhánh AI-sửa trong chu kỳ này; TTL vẫn chạy, không gia hạn.')
        chon = input('Gõ mo để kiểm mở che, hoặc bo để bỏ qua: ').strip().lower()
        r['office'] = dict(nguon_va_che='Chờ Anh', mo_luu_mo_lai='Chờ Anh', repair_warning='Chờ Anh')
        if chon != 'mo':
            return None
        doi_chieu(not p.is_symlink() and not (getattr(p.lstat(), 'st_file_attributes', 0) & 0x400), 'B10_HIEN_VAT_LIEN_KET')
        with p.open('rb') as f:
            raw = f.read(MIB + 1)
        doi_chieu(len(raw) <= MIB, 'B10_OFFICE_LUU_VUOT_TRAN')
        r['office']['nguon_va_che'] = 'Anh xác nhận thao tác mở/lưu/mở lại; chưa xác nhận toàn bộ hình thức'
        return raw

    def sau_mo(self, b, r):
        ma = re.sub('[^A-Za-z0-9_-]', '-', b.ca['ma'])
        ghi_hien_vat(self.thu_muc, 'DEMO-' + ma + '-da-mo-che.' + b.ca['loai'], b.da_mo)
        print('Anh mở/lưu/đóng/mở lại tệp đã mở che DEMO-' + ma + '; đối chiếu từng mục font/run/bảng/merge/notes/ẩn hàng-cột/style/tiền-ngày/properties, kể cả cảnh báo repair.')
        x = input('Gõ dat khi mọi mục đạt và không repair warning; khong nếu có lỗi; bo nếu chưa kiểm: ').strip().lower()
        r['office']['mo_luu_mo_lai'] = {'dat': 'Anh xác nhận đạt', 'khong': 'Anh xác nhận có lỗi'}.get(x, 'Chờ Anh')
        r['office']['repair_warning'] = 'Anh xác nhận không có' if x == 'dat' else 'Chờ Anh/không đạt'


def tham_so(argv=None):
    p = argparse.ArgumentParser(prog=Path(__file__).name, description=__doc__)
    p.add_argument('--that', action='store_true', help='Chỉ Anh: kiểm Office thủ công với DEMO; Local vẫn giả, Cloud tắt.')
    p.add_argument('--thu-muc-demo', type=Path, help='Thư mục hiện vật mới do Anh chỉ định; không ghi đè.')
    p.add_argument('--ca', choices=[t + str(i).zfill(2) for t, n in (('D', 14), ('X', 17)) for i in range(1, n+1)], help='Chọn một mã tệp trong bộ ứng viên.')
    p.add_argument('--doi-chung', action='store_true', help='Đối chứng development để kiểm chuỗi/Office, tách khỏi mẫu số chất lượng.')
    p.add_argument('--tu-kiem', action='store_true', help='Kiểm cơ học công cụ, lifecycle, AI-sửa và các trần; không nghiệm thu chất lượng.')
    p.add_argument('--bien', action='store_true', help='Chỉ đo các gate biên/+1, không phải benchmark toàn chuỗi.')
    p.add_argument('--chi-tiet', action='store_true', help='In cả từng ca/bước/đỉnh RAM; mặc định in tóm tắt.')
    p.add_argument('--bao-cao', type=Path, help='Chỉ ghi khi Anh chỉ định, JSON số đếm/băm, tạo mới độc quyền.')
    p.add_argument('--xac-nhan-gold', help='SHA-256 bytes tệp gold đã được lead xem/đóng băng.')
    p.add_argument('--xac-nhan-cong-cu', help='SHA-256 bytes công cụ đã được lead xem/đóng băng.')
    p.add_argument('--worker-gia', action='store_true', help=argparse.SUPPRESS)
    a = p.parse_args(argv)
    doi_chieu(not a.that or a.thu_muc_demo is not None, 'B10_THIEU_THU_MUC_HIEN_VAT')
    doi_chieu(a.that or a.thu_muc_demo is None, 'B10_KHO_KHONG_GHI_HIEN_VAT')
    doi_chieu(not a.that or not (a.tu_kiem or a.bien), 'B10_KHONG_GHEP_THAT_TU_KIEM')
    return a


def tong_do(ds):
    vals = {}
    for k in ('toan_chuoi_giay', 'python_peak_byte', 'os_peak_pid_byte', 'bytes_goc_va_che', 'ram_do_thi_bytes_map'):
        xs = sorted(r[k] for r in ds if isinstance(r.get(k), (int, float)))
        vals[k] = dict(n=len(xs), min=xs[0], max=xs[-1]) if xs else 'CHƯA ĐO'
    buoc = {}
    for r in ds:
        for x in r.get('buoc', []):
            buoc.setdefault(x['buoc'], []).append(x['giay'])
    for k, xs in buoc.items():
        xs.sort()
        buoc[k] = dict(n=len(xs), min=xs[0], max=xs[-1], p50=xs[len(xs)//2], p95=xs[max(0, (95*len(xs)+99)//100-1)])
    vals['tung_buoc_giay'] = buoc
    vals['doi_AI_that'] = 'CHƯA ĐO'
    vals['dien_giai'] = 'Có overhead tracemalloc; OS là high-water mark cả PID, không riêng engine. Đồ thị bytes+map là getsizeof có khử trùng, không budget production. Local/tokenizer giả; không có số đợi AI thật.'
    return vals


def tom_tat(baocao):
    ket = {k: v for k, v in baocao.items() if k not in {'ca', 'doi_chung', 'kiem'}}
    for ten in ('ca', 'doi_chung'):
        ds = baocao.get(ten, [])
        ket[ten] = dict(thong_ke=thong_ke(ds), so_do=tong_do(ds),
            chi_so_can_xem=[{k: r[k] for k in ('ma', 'sua', 'ket_qua', 'ma_loi', 'mo', 'ma_loi_mo', 'loi_kiem') if k in r}
                            for r in ds if r['loi_kiem'] or r['ket_qua'] != 'phat_hanh' or r['mo'] not in {'du', 'chan_dung'}])
    ks = baocao.get('kiem', [])
    ket['kiem'] = dict(tong=len(ks), dat=sum(r['dat'] is True for r in ks),
                       chua_do=sum(r['dat'] is None for r in ks),
                       chua_dat=[r for r in ks if r['dat'] is False],
                       ghi_chu_chua_do=[r for r in ks if r['dat'] is None])
    return ket


def main(argv=None):
    a = tham_so(argv)
    if a.worker_gia:
        print(json_bytes(kiem_worker_rieng()).decode('utf-8'))
        return 0
    gold, sha_gold = doc_gold()
    sha_tool = bam(Path(__file__).read_bytes())
    dong_bang = a.xac_nhan_gold == sha_gold and a.xac_nhan_cong_cu == sha_tool
    if a.xac_nhan_gold or a.xac_nhan_cong_cu:
        doi_chieu(dong_bang, 'B10_XAC_NHAN_SHA_KHONG_KHOP')
    doi_chieu(len(gold['ca']) >= 24 and len({c['sha256_tep'] for c in gold['ca']}) == len(gold['ca']), 'B10_SO_TEP_HOAC_TRUNG_FIXTURE')
    for loai in ('docx', 'xlsx'):
        for ky in ('ho_tro', 'chan'):
            doi_chieu(sum(c['loai'] == loai and c['ky_vong'] == ky for c in gold['ca']) >= 6, 'B10_THIEU_NHOM_GOLD')
    cmd = THU_MUC / 'THU-MASK-TEP-THAT.cmd'
    cmd_bytes = cmd.read_bytes()
    doi_chieu(cmd_bytes.isascii() and b'"%B10_PY%" -B "%~dp0thu_mask_tep_that.py"' in cmd_bytes, 'B10_CMD_ASCII_QUOTE')
    report = dict(phien_ban=PHIEN_BAN,
        ket_luan='Chưa đạt nghiệm thu chung; đã kiểm bằng Core giả (CoreGia).',
        che_do='Office thủ công do Anh chọn' if a.that else 'mock/chạy khô',
        bo='Bộ đã xác nhận SHA; chờ lead chốt tính độc lập' if dong_bang else 'BỘ ỨNG VIÊN — Chờ lead đóng băng độc lập',
        doc_lap_da_xac_nhan=gold['provenance']['doc_lap_da_xac_nhan'],
        sha256_gold=sha_gold, sha256_noi_dung_gold=gold['sha256_noi_dung'], sha256_cong_cu=sha_tool,
        phien_ban_sdk=version('kho-tri-thuc-sdk'), python=sys.version.split()[0], zlib=zlib.ZLIB_RUNTIME_VERSION,
        phien_ban_engine=json.loads((GOI / 'engine.json').read_bytes())['phien_ban'],
        Cloud=0, engine_khac=0, Local_that='CHƯA ĐO — Chờ Anh', Core_that='CHƯA ĐO — Chờ Core',
        Office_that='Chờ Anh' if not a.that else 'Chỉ theo xác nhận thủ công từng tệp; không chứng nhận Core/Local',
        so_luot_mang=0, so_luot_engine_ghi_tep=0,
        can_core=['C-P4-01/02: quyền, mã Core cấp, ghim instance, lifecycle kể cả khi rảnh; concurrency=1 không chứng minh affinity.',
                  'C-P4-03/04/06: tìm chính xác bí mật/CAS/quota, Local đủ đoạn/nguồn, Admin xem và biên nhận; không giải mã.',
                  'C-P4-05/C-MS22-01: budget RAM/job/concurrency máy đích, streaming/trần/413, quyền tệp, upload cách ly và ACK; CLI thiếu quyền.',
                  'Chờ lead chốt chất lượng sau bỏ matcher rõ; giữ nợ CAO và Cloud tắt.'], ca=[], doi_chung=[], kiem=[])
    if a.that:
        doi_chieu(not a.thu_muc_demo.exists(), 'B10_THU_MUC_HIEN_VAT_DA_CO')
        doi_chieu(not any(p.is_symlink() or p.exists() and getattr(p.lstat(), 'st_file_attributes', 0) & 0x400 for p in (a.thu_muc_demo, *a.thu_muc_demo.parents)), 'B10_THU_MUC_LIEN_KET')
        a.thu_muc_demo.mkdir(parents=True, exist_ok=False)
    if a.bien:
        report['kiem'] = chay_bien()
    elif a.tu_kiem:
        report['kiem'] = chay_vong_doi(gold) + kiem_them() + chay_bien() + kiem_tan_cong(gold)
        them, tep = chay_tich_hop(gold)
        report['kiem'] += them
        report['doi_chung'] = tep
    else:
        cac = [c for c in gold['ca'] if not a.ca or c['ma'] == a.ca]
        if a.doi_chung:
            cac = [c for c in cac if c['ky_vong'] == 'ho_tro']
            doi_chieu(bool(cac), 'B10_DOI_CHUNG_CHI_NHOM_HO_TRO')
            cac = [ca_kiem_thuat(gold, c['loai'], [d for d in gold['ca'] if d['loai'] == c['loai'] and d['ky_vong'] == 'ho_tro'].index(c)) for c in cac]
        for c in cac:
            r = chay_ca(c, thu_cong=OfficeThuCong(a.thu_muc_demo) if a.that else None)
            report['doi_chung' if a.doi_chung else 'ca'].append(r)
    report['so_luot_mang'], report['so_luot_engine_ghi_tep'] = IO_DANG_KIEM[2], IO_DANG_KIEM[1]
    report['gate_bien_toan_chuoi'] = 'CHƯA ĐO: matrix đo từng gate thật cô lập; reader/writer còn cap 500.000 khi đọc lại. Chưa có full B + Local thật ở mọi trần.'
    if a.bao_cao:
        with a.bao_cao.open('xb') as f:
            f.write(json_bytes(report) + b'\n')
    print(json.dumps(report if a.chi_tiet else tom_tat(report), ensure_ascii=False, indent=2, allow_nan=False))
    loi = any(r['dat'] is False for r in report['kiem']) or any(r['loi_kiem'] for r in report['ca'] + report['doi_chung'])
    if loi or report['so_luot_mang'] or report['so_luot_engine_ghi_tep']:
        return 1
    # Mã 0 của --tu-kiem/--bien chỉ nghĩa công cụ kiểm đúng kỳ vọng kỹ thuật.
    return 0 if a.tu_kiem or a.bien else 2


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        print('Đã dừng công cụ DEMO; chuỗi đang mở phải chạy lại.', file=sys.stderr)
        sys.exit(130)
    except Exception as exc:
        ma = str(exc) if isinstance(exc, KiemLoi) else 'B10_LOI_CONG_CU_' + type(exc).__name__
        print('Không hoàn tất công cụ DEMO. Mã: ' + ma, file=sys.stderr)
        sys.exit(1)
