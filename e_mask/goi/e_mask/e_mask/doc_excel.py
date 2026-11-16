"""Reader XLSX nội bộ MASK-B3: mọi vùng đã phân loại, chưa có năng lực SDK.

Không che, gọi AI, đổi tên sheet, dựng workbook hoặc lưu tệp. Kết quả nhạy
cảm chỉ dùng trong việc cho MASK-2b/MASK-2c và writer B4/B6 về sau.
"""

from bisect import bisect_left
from copy import deepcopy
from dataclasses import dataclass, field, replace
from hashlib import sha256
import re
from types import MappingProxyType
import unicodedata
from xml.parsers import expat

from .doc_tep import doc_goi_excel
from .xml_an_toan import (
    S_NS, CP_NS, DC_NS, DCT_NS, EP_NS, CUSTOM_NS, VT_NS, XSI_NS,
    KY_TU_VAO_TOI_DA,
)
from .xml_excel import (
    RID, ChuXML, NutXML, _kiem, _cs, _mot_trong, _mau, BOOL, UINT, _PREFIX,
    giai_st, map_xml, kiem_excel, kiem_theme, so_nguyen, so_thuc, ngay,
)
from .zip_an_toan import _sai, _vuot

S = '{' + S_NS + '}'

_THE_BYTE = re.compile(rb'''<(?:[^<>"']+|"[^"]*"|'[^']*')*>''')
_THUOC_TINH_BYTE = re.compile(rb'''([^\s=<>/'"]+)\s*=\s*(['"])(.*?)\2''', re.DOTALL)


def _map_excel(raw, root, kiem_huy):
    """Map nhanh UTF-8 đơn giản bằng byte index Expat, sau kiểm B1/B3.

    Không thay gate/parser nghiệp vụ. UTF-16/entity/CR/CDATA/whitespace
    chuẩn hóa hoặc encoding khác vẫn dùng nguyên map lexical B3. Mọi
    tag/attribute/leaf đối chiếu cây độc lập B1, không suy offset bằng
    độ dài chuỗi Unicode hay serialize lại XML.
    """
    khong_bom = raw[3:] if raw.startswith(b'\xef\xbb\xbf') else raw
    khai = (re.search(rb'''encoding\s*=\s*['"]([^'"]+)['"]''',
                      khong_bom[:khong_bom.find(b'?>') + 2])
            if khong_bom.startswith(b'<?xml') else None)
    if (any(x in raw for x in (b'\0', b'&', b'\r', b'\n', b'\t', b'<![CDATA['))
            or khai is not None and khai[1].lower() != b'utf-8'):
        return map_xml(raw, root, kiem_huy)
    p = expat.ParserCreate(namespace_separator='}')
    nodes, stack, ket, da_do = iter(root.iter()), [], {}, {}

    def chu_byte(chu, dau):
        # Offset tương đối của chuỗi lặp chỉ tính một lần trong part.
        if chu not in da_do:
            ds, pos = [], 0
            for i, c in enumerate(chu):
                if i % 4096 == 0:
                    kiem_huy()
                cuoi = pos + len(c.encode('utf-8'))
                ds.append((pos, cuoi))
                pos = cuoi
            da_do[chu] = tuple(ds)
        return ChuXML(chu, tuple((dau + a, dau + b) for a, b in da_do[chu]), dau)

    def mo(ten, attrs):
        kiem_huy()
        e = next(nodes, None)
        if e is None or e.tag != ('{' + ten if '}' in ten else ten):
            _sai()
        dau = p.CurrentByteIndex
        m = _THE_BYTE.match(raw, dau)
        if m is None:
            _sai()
        thuoc = {}
        for a in _THUOC_TINH_BYTE.finditer(raw, dau + 1, m.end() - 1):
            name = a[1].decode('utf-8')
            if name == 'xmlns' or name.startswith('xmlns:'):
                continue
            if ':' in name:
                prefix, local = name.split(':')
                if prefix not in _PREFIX:
                    _sai()
                name = '{' + _PREFIX[prefix] + '}' + local
            x = chu_byte(a[3].decode('utf-8'), a.start(3))
            if e.get(name) != x.chu:
                _sai()
            thuoc[name] = x
        if set(thuoc) != set(e.attrib):
            _sai()
        tu_dong = raw[dau:m.end() - 1].rstrip().endswith(b'/')
        stack.append((e, len(ket) + len(stack), dau, m.end(), tu_dong, thuoc, []))

    def chu(text):
        if stack:
            dau = p.CurrentByteIndex
            if raw[dau:dau + len(text.encode('utf-8'))] != text.encode('utf-8'):
                _sai()
            stack[-1][-1].append(chu_byte(text, dau))

    def dong(ten):
        kiem_huy()
        e, so, dau, het, tu_dong, thuoc, xs = stack.pop()
        cuoi = het if tu_dong else raw.find(b'>', p.CurrentByteIndex) + 1
        text = ChuXML(''.join(x.chu for x in xs),
                      tuple(b for x in xs for b in x.byte), None if tu_dong else het)
        if cuoi <= dau or not len(e) and text.chu != (e.text or ''):
            _sai()
        ket[e] = NutXML(so, dau, cuoi, text, MappingProxyType(thuoc))

    p.StartElementHandler, p.CharacterDataHandler, p.EndElementHandler = mo, chu, dong
    try:
        for dau in range(0, len(raw), 65536):
            kiem_huy()
            p.Parse(raw[dau:dau + 65536], False)
        p.Parse(b'', True)
        if stack or next(nodes, None) is not None:
            _sai()
        return MappingProxyType(ket)
    finally:
        p.StartElementHandler = p.CharacterDataHandler = p.EndElementHandler = None
        stack.clear()
        da_do.clear()


@dataclass(frozen=True, repr=False)
class ManhExcel:
    phan: str
    so_nut: int
    so_run: int | None
    thuoc_tinh: str | None
    bat_dau: int
    ket_thuc: int
    byte: tuple[tuple[int, int], ...] = field(repr=False)
    neo: int | None


@dataclass(frozen=True, repr=False)
class VungExcel:
    ma: str
    so_sheet: int | None
    o: str | None
    chi_so_chu: int | None
    chu: str = field(repr=False)
    manh: tuple[ManhExcel, ...] = field(repr=False)
    duoc_sua: bool
    bam_chu: str

    def kiem_thay_the(self, chu_moi):
        """B6/B7 phải chặn nếu hai lớp đề nghị đổi tên sheet/metadata phụ thuộc."""
        if type(chu_moi) is not str or not self.duoc_sua and chu_moi != self.chu:
            _sai()

    def khoang_byte(self, dau, cuoi):
        """Quan hệ khoảng Unicode → từng run/node/attribute/bytes, không gộp run."""
        if type(dau) is not int or type(cuoi) is not int or not 0 <= dau < cuoi <= len(self.chu):
            _sai()
        ket_qua = []
        for m in self.manh:
            a, b = max(dau, m.bat_dau), min(cuoi, m.ket_thuc)
            if a < b:
                xs = m.byte[a - m.bat_dau:b - m.bat_dau]
                ket_qua.append((m.phan, m.so_nut, m.so_run, m.thuoc_tinh, xs[0][0], xs[-1][1]))
        return tuple(ket_qua)

    def unicode_tu_byte(self, phan, so_nut, dau, cuoi, *, thuoc_tinh=None):
        """Bytes → khoảng Unicode bao, kể cả byte nằm trong entity/ST/surrogate.

        Quan hệ nhiều byte/một code point; không trả offset bằng phép trừ độ dài.
        Khoảng nằm ngoài text/attribute của vùng trả rỗng, không đoán vị trí.
        """
        if type(dau) is not int or type(cuoi) is not int or not 0 <= dau < cuoi:
            _sai()
        ds = []
        for m in self.manh:
            if (m.phan, m.so_nut, m.thuoc_tinh) != (phan, so_nut, thuoc_tinh):
                continue
            vi = [m.bat_dau + i for i, (a, b) in enumerate(m.byte) if a < cuoi and dau < b]
            if vi:
                ds.append((min(vi), max(vi) + 1))
        return tuple(ds)


@dataclass(frozen=True, repr=False)
class OExcel:
    so_sheet: int
    dia_chi: str
    kieu: str | None
    gia_tri: str | None = field(repr=False)
    style: int
    style_goc: str | None
    style_hang: int | None
    style_cot: int | None
    style_hieu_luc: int
    chi_so_chu: int | None
    vung: int | None
    hang_an: bool
    cot_an: bool
    byte_bat_dau: int
    byte_ket_thuc: int
    xml_goc: bytes = field(repr=False)


@dataclass(frozen=True, repr=False)
class ExcelDaDoc:
    goi: object = field(repr=False)
    vung: tuple[VungExcel, ...] = field(repr=False)
    o: tuple[OExcel, ...] = field(repr=False)
    shared: tuple[int, ...]
    tham_chieu_chu: tuple[tuple[tuple[int, str], ...], ...] = field(repr=False)
    styles: tuple[object, ...] = field(repr=False)
    gop_o: tuple[tuple[str, ...], ...]
    epoch1904: bool
    so_ky_tu: int
    bam_tep: str


def _bool(v):
    return v in ('1', 'true')


def _dia_chi(v):
    m = re.fullmatch(r'([A-Z]{1,3})([1-9][0-9]{0,6})', v or '')
    if m is None:
        _sai()
    cot = 0
    for c in m[1]:
        cot = cot * 26 + ord(c) - 64
    hang = int(m[2])
    if cot > 16384 or hang > 1048576:
        _sai()
    return hang, cot


def _pham_vi(v):
    xs = v.split(':')
    if len(xs) not in (1, 2):
        _sai()
    dau, cuoi = _dia_chi(xs[0]), _dia_chi(xs[-1])
    if dau[0] > cuoi[0] or dau[1] > cuoi[1]:
        _sai()
    return dau, cuoi


def _chi_so(e, ten, tran, mac_dinh=0):
    i = so_nguyen(e.get(ten, str(mac_dinh)))
    if i >= tran:
        _sai()
    return i


def _styles(root, kiem_huy):
    if root is None:
        return (MappingProxyType({'numFmtId': '0'}),)
    counts = {k: len(root.find(S + k)) if root.find(S + k) is not None else 0
              for k in ('fonts', 'fills', 'borders', 'cellStyleXfs', 'cellXfs')}
    if not all(counts.values()):
        _sai()
    formats = {}
    for e in root.findall(S + 'numFmts/' + S + 'numFmt'):
        kiem_huy()
        n = so_nguyen(e.get('numFmtId'), duoi=164)
        if n in formats or 'formatCode' not in e.attrib:
            _sai()
        formats[n] = e.get('formatCode')
    for loai in ('cellStyleXfs', 'cellXfs'):
        for e in root.find(S + loai):
            kiem_huy()
            for attr, muc in (('fontId', 'fonts'), ('fillId', 'fills'), ('borderId', 'borders')):
                _chi_so(e, attr, counts[muc])
            fmt = so_nguyen(e.get('numFmtId', '0'))
            if fmt not in set(range(23)) | set(range(37, 50)) and fmt not in formats:
                _sai()
            if loai == 'cellXfs':
                _chi_so(e, 'xfId', counts['cellStyleXfs'])
            elif 'xfId' in e.attrib:
                _sai()
    for e in root.findall(S + 'cellStyles/' + S + 'cellStyle'):
        kiem_huy()
        if e.get('name') != 'Normal' or e.get('builtinId') != '0':
            _sai()
        _chi_so(e, 'xfId', counts['cellStyleXfs'])
    return tuple(MappingProxyType({**e.attrib, 'formatCode': formats.get(int(e.get('numFmtId', '0')))})
                 for e in root.find(S + 'cellXfs'))


def _kiem_gop(ds, kiem_huy):
    """Sweep theo hàng; không mở rộng vùng gộp lớn thành hàng triệu ô."""
    events = []
    for v in ds:
        kiem_huy()
        (r1, c1), (r2, c2) = _pham_vi(v)
        if (r1, c1) == (r2, c2):
            _sai()
        events.extend(((r1, 1, c1, c2), (r2 + 1, 0, c1, c2)))
    active = []
    for _, them, c1, c2 in sorted(events):
        kiem_huy()
        i = bisect_left(active, (c1, c2))
        if them:
            if (i and active[i - 1][1] >= c1) or (i < len(active) and active[i][0] <= c2):
                _sai()
            active.insert(i, (c1, c2))
        else:
            if i >= len(active) or active[i] != (c1, c2):
                _sai()
            active.pop(i)


class _DocExcel:
    def __init__(self, goi, kiem_huy):
        self.goi, self.kiem_huy = goi, kiem_huy
        self.raw = {p.ten: p.du_lieu for p in goi.goi.zip.phan}
        self.maps = {}
        self.vung, self.o, self.shared, self.refs, self.gop = [], [], [], [], []
        self.chu_dem = 0
        self.them_lap = 0

    def map(self, phan):
        if phan not in self.maps:
            ham = _map_excel if phan.startswith('xl/worksheets/') else map_xml
            self.maps[phan] = ham(self.raw[phan], self.goi.goi.cay[phan], self.kiem_huy)
        return self.maps[phan]

    def vung_moi(self, ma, phan, nodes, *, so_sheet=None, o=None, chi_so=None, attr=None,
                 st=False, duoc_sua=True, run=False):
        self.kiem_huy()
        mapping = self.map(phan)
        chu, manh, pos = [], [], 0
        for i, e in enumerate(nodes):
            self.kiem_huy()
            n = mapping[e]
            x = n.thuoc_tinh[attr] if attr else n.text
            if st and '_x' in x.chu:
                x = giai_st(x, self.kiem_huy)
            chu.append(x.chu)
            manh.append(ManhExcel(phan, n.so, i if run else None, attr,
                                  pos, pos + len(x.chu), x.byte, x.neo))
            pos += len(x.chu)
        text = ''.join(chu)
        self.chu_dem += len(text)
        if self.chu_dem > KY_TU_VAO_TOI_DA:
            _vuot()
        v = VungExcel(ma, so_sheet, o, chi_so, text, tuple(manh), duoc_sua,
                       'sha256:' + sha256(text.encode('utf-8')).hexdigest())
        self.vung.append(v)
        return len(self.vung) - 1

    def _chu_o(self, ma, phan, e, **kwargs):
        nodes = [e.find(S + 't')] if e.find(S + 't') is not None else [r.find(S + 't') for r in e.findall(S + 'r')]
        vi = self.vung_moi(ma, phan, nodes, st=True, run=True, **kwargs)
        # Excel đếm UTF-16; vượt thì từ chối, tuyệt đối không cắt 32767.
        if len(self.vung[vi].chu.encode('utf-16-le')) // 2 > 32767:
            _vuot()
        return vi

    def shared_strings(self):
        root = self.goi.goi.cay.get('xl/sharedStrings.xml')
        if root is None:
            return
        if 'uniqueCount' in root.attrib and int(root.get('uniqueCount')) != len(root):
            _sai()
        for i, e in enumerate(root):
            self.kiem_huy()
            self.shared.append(self._chu_o('shared_string', 'xl/sharedStrings.xml', e, chi_so=i))
            self.refs.append([])

    def sheets(self, styles):
        cay, qh = self.goi.goi.cay, self.goi.goi.quan_he
        book = cay['xl/workbook.xml']
        names, ids, parts = set(), set(), set()
        ten_sheet = []
        sheets = book.find(S + 'sheets')
        for so, e in enumerate(sheets):
            self.kiem_huy()
            sid = so_nguyen(e.get('sheetId'), duoi=1)
            v = self.vung_moi('ten_sheet', 'xl/workbook.xml', [e], attr='name', st=True,
                              so_sheet=so, duoc_sua=False)
            ten = self.vung[v].chu
            chuan = unicodedata.normalize('NFC', ten).casefold()
            if (not ten or len(ten.encode('utf-16-le')) // 2 > 31
                    or any(c in ten for c in '[]:*?/\\') or ten.startswith("'") or ten.endswith("'")
                    or any(unicodedata.category(c).startswith('C') for c in ten)
                    or chuan in names or sid in ids):
                _sai()
            names.add(chuan)
            ids.add(sid)
            ten_sheet.append(ten)
            rel = qh.get('xl/workbook.xml', {}).get(e.get(RID))
            if rel is None or rel[0].rsplit('/', 1)[-1] != 'worksheet' or rel[1] in parts:
                _sai()
            phan = rel[1]
            parts.add(phan)
            self.sheet(so, phan, cay[phan], styles)
        if parts != {p for p in cay if p.startswith('xl/worksheets/')}:
            _sai()
        for e in book.findall(S + 'bookViews/' + S + 'workbookView'):
            if int(e.get('activeTab', '0')) >= len(sheets) or int(e.get('firstSheet', '0')) >= len(sheets):
                _sai()
        return ten_sheet

    def sheet(self, so, phan, root, styles):
        # Mọi ref đều kiểm biên, kể cả selection/dimension/ignoredError không chứa ô.
        for e in root.iter():
            self.kiem_huy()
            for attr in ('ref', 'activeCell', 'topLeftCell', 'sqref'):
                if attr in e.attrib:
                    for x in e.get(attr).split(' '):
                        _pham_vi(x)
        columns = []
        cuoi_cot = 0
        for c in root.findall(S + 'cols/' + S + 'col'):
            a, b = so_nguyen(c.get('min'), 16384, duoi=1), so_nguyen(c.get('max'), 16384, duoi=1)
            if a > b or a <= cuoi_cot:
                _sai()
            cuoi_cot = b
            _chi_so(c, 'style', len(styles))
            columns.append((a, b, _bool(c.get('hidden')), int(c.get('style')) if 'style' in c.attrib else None))
        cuoi_hang = 0
        for row in root.find(S + 'sheetData'):
            self.kiem_huy()
            hang = so_nguyen(row.get('r'), 1048576, duoi=1)
            if hang <= cuoi_hang:
                _sai()
            cuoi_hang, cuoi_cot = hang, 0
            _chi_so(row, 's', len(styles))
            if 's' in row.attrib and not _bool(row.get('customFormat')):
                _sai()
            style_hang = int(row.get('s', '0')) if _bool(row.get('customFormat')) else None
            if 'spans' in row.attrib:
                a, b = [int(x) for x in row.get('spans').split(':')]
                if not 1 <= a <= b <= 16384:
                    _sai()
            for e in row:
                self.kiem_huy()
                r, c = _dia_chi(e.get('r'))
                if r != hang or c <= cuoi_cot:
                    _sai()
                cuoi_cot = c
                style = _chi_so(e, 's', len(styles))
                typ = e.get('t')
                val, inline = e.find(S + 'v'), e.find(S + 'is')
                vi, index = None, None
                if typ == 'inlineStr':
                    if inline is None or val is not None:
                        _sai()
                    vi = self._chu_o('o', phan, inline, so_sheet=so, o=e.get('r'))
                elif inline is not None:
                    _sai()
                elif typ == 's':
                    index = so_nguyen(None if val is None else val.text)
                    if index >= len(self.shared):
                        _sai()
                    goc = self.vung[self.shared[index]]
                    self.refs[index].append((so, e.get('r')))
                    self.them_lap += len(goc.chu)
                    self.chu_dem += len(goc.chu)
                    if (self.chu_dem > KY_TU_VAO_TOI_DA or
                            self.goi.goi.thong_ke['so_ky_tu'] + self.them_lap > KY_TU_VAO_TOI_DA):
                        _vuot()
                    vi = len(self.vung)
                    self.vung.append(VungExcel('o', so, e.get('r'), index, goc.chu,
                                               goc.manh, True, goc.bam_chu))
                elif val is not None:
                    value = val.text or ''
                    if typ in (None, 'n'):
                        so_thuc(value)
                    elif typ == 'b':
                        _mot_trong('0', '1')(value)
                    elif typ == 'e':
                        _mot_trong('#NULL!', '#DIV/0!', '#VALUE!', '#REF!', '#NAME?', '#NUM!', '#N/A', '#GETTING_DATA')(value)
                    elif typ == 'd':
                        ngay(value)
                    else:
                        _sai()
                elif typ not in (None, 'n'):
                    _sai()
                n = self.map(phan)[e]
                style_cot = next((st for a, b, _, st in columns if a <= c <= b), None)
                style_hieu_luc = (style if 's' in e.attrib else
                                   style_hang if style_hang is not None else
                                   style_cot if style_cot is not None else 0)
                self.o.append(OExcel(so, e.get('r'), typ, None if val is None else val.text,
                                      style, e.get('s'), style_hang, style_cot, style_hieu_luc,
                                      index, vi, _bool(row.get('hidden')),
                                      any(a <= c <= b and an for a, b, an, _ in columns),
                                      n.bat_dau, n.ket_thuc, self.raw[phan][n.bat_dau:n.ket_thuc]))
        merges = tuple(e.get('ref', '') for e in root.findall(S + 'mergeCells/' + S + 'mergeCell'))
        _kiem_gop(merges, self.kiem_huy)
        self.gop.append(merges)

    def core(self, root):
        if root.attrib or (root.text or '').strip(' \t\r\n'):
            _sai()
        da_co = set()
        chu = {DC_NS: {'title', 'subject', 'creator', 'description', 'identifier', 'language'},
               CP_NS: {'keywords', 'lastModifiedBy', 'category', 'contentStatus', 'version'}}
        for e in root:
            self.kiem_huy()
            ns, ten = e.tag[1:].split('}')
            if e.tag in da_co or (e.tail or '').strip(' \t\r\n'):
                _sai()
            da_co.add(e.tag)
            if ten in chu.get(ns, set()):
                _kiem(e, {}, text=True)
                self.vung_moi('core', 'docProps/core.xml', [e])
            elif ns == DCT_NS and ten in ('created', 'modified'):
                _kiem(e, {'{' + XSI_NS + '}type': _mot_trong('dcterms:W3CDTF')}, text=True)
                ngay(e.text)
            elif ns == CP_NS and ten == 'lastPrinted':
                _kiem(e, {}, text=True)
                ngay(e.text)
            elif ns == CP_NS and ten == 'revision':
                _kiem(e, {}, text=True)
                so_nguyen(e.text)
            else:
                _sai()

    def app(self, root, ten_sheet):
        if root.attrib or (root.text or '').strip(' \t\r\n'):
            _sai()
        da_co = set()
        text = set('Template Manager Company PresentationFormat Application AppVersion'.split())
        ints = set('Pages Words Characters Lines Paragraphs Slides Notes TotalTime HiddenSlides MMClips CharactersWithSpaces DocSecurity'.split())
        bools = set('ScaleCrop LinksUpToDate SharedDoc HyperlinksChanged'.split())
        for e in root:
            self.kiem_huy()
            ten = e.tag.rsplit('}', 1)[-1]
            if e.tag != '{' + EP_NS + '}' + ten or ten in da_co or (e.tail or '').strip(' \t\r\n'):
                _sai()
            da_co.add(ten)
            if ten in text:
                _kiem(e, {}, text=True)
                self.vung_moi('app', 'docProps/app.xml', [e])
            elif ten in ints | bools:
                _kiem(e, {}, text=True)
                (so_nguyen if ten in ints else BOOL)(e.text)
            elif ten == 'TitlesOfParts':
                _kiem(e, {}, (('vector', 1, 1),))
                v = e[0]
                if v.tag != '{' + VT_NS + '}vector':
                    _sai()
                _kiem(v, {'size': UINT, 'baseType': _mot_trong('lpstr')}, (('lpstr', len(ten_sheet), len(ten_sheet)),), bat_buoc=('size', 'baseType'))
                if int(v.get('size')) != len(ten_sheet):
                    _sai()
                for i, t in enumerate(v):
                    if t.tag != '{' + VT_NS + '}lpstr':
                        _sai()
                    _kiem(t, {}, text=True)
                    if (t.text or '') != ten_sheet[i]:
                        _sai()
                    self.vung_moi('app_ten_sheet', 'docProps/app.xml', [t], so_sheet=i, duoc_sua=False)
            elif ten == 'HeadingPairs':
                _kiem(e, {}, (('vector', 1, 1),))
                v = e[0]
                if v.tag != '{' + VT_NS + '}vector':
                    _sai()
                _kiem(v, {'size': _mot_trong('2'), 'baseType': _mot_trong('variant')}, (('variant', 2, 2),), bat_buoc=('size', 'baseType'))
                for var, loai in zip(v, ('lpstr', 'i4')):
                    if var.tag != '{' + VT_NS + '}variant':
                        _sai()
                    _kiem(var, {}, ((loai, 1, 1),))
                    if var[0].tag != '{' + VT_NS + '}' + loai:
                        _sai()
                    _kiem(var[0], {}, text=True)
                if v[0][0].text != 'Worksheets' or so_nguyen(v[1][0].text) != len(ten_sheet):
                    _sai()
            else:
                _sai()

    def custom(self, root):
        if root.attrib or (root.text or '').strip(' \t\r\n'):
            _sai()
        ids, names = set(), set()
        for e in root:
            self.kiem_huy()
            if e.tag != '{' + CUSTOM_NS + '}property' or (e.tail or '').strip(' \t\r\n'):
                _sai()
            _kiem(e, {'fmtid': _mot_trong('{D5CDD505-2E9C-101B-9397-08002B2CF9AE}'), 'pid': UINT, 'name': lambda v: None},
                  tuple((n, 0, 1) for n in ('lpstr', 'lpwstr', 'bstr', 'i1', 'i2', 'i4', 'i8', 'int', 'ui1', 'ui2', 'ui4', 'ui8', 'uint', 'r4', 'r8', 'decimal', 'bool', 'date', 'filetime')),
                  bat_buoc=('fmtid', 'pid', 'name'))
            pid = so_nguyen(e.get('pid'), duoi=2)
            name = unicodedata.normalize('NFC', e.get('name')).casefold()
            if not name or pid in ids or name in names or len(e) != 1:
                _sai()
            ids.add(pid)
            names.add(name)
            self.vung_moi('custom_ten', 'docProps/custom.xml', [e], attr='name')
            v = e[0]
            ten = v.tag.rsplit('}', 1)[-1]
            if v.tag != '{' + VT_NS + '}' + ten:
                _sai()
            _kiem(v, {}, text=True)
            if ten in ('lpstr', 'lpwstr', 'bstr'):
                self.vung_moi('custom', 'docProps/custom.xml', [v])
            elif ten in ('date', 'filetime'):
                ngay(v.text)
            elif ten == 'bool':
                BOOL(v.text)
            else:
                so_thuc(v.text)
                if ten == 'decimal' and ('e' in v.text.lower()):
                    _sai()
                if ten == 'r4':
                    from decimal import Decimal
                    if Decimal(v.text).copy_abs() > Decimal('3.4028234663852886e38'):
                        _sai()
                if ten not in ('r4', 'r8', 'decimal'):
                    if not re.fullmatch(r'-?[0-9]{1,20}', v.text) or ten.startswith('u') and v.text.startswith('-'):
                        _sai()
                    bits = {'i1': 8, 'i2': 16, 'i4': 32, 'i8': 64, 'int': 32,
                            'ui1': 8, 'ui2': 16, 'ui4': 32, 'ui8': 64, 'uint': 32}[ten]
                    a, b = (0, 2 ** bits - 1) if ten.startswith('u') else (-2 ** (bits - 1), 2 ** (bits - 1) - 1)
                    if not a <= int(v.text) <= b:
                        _sai()


def _sao_ban_doc(doc, kiem_huy):
    """Bản đọc độc lập: không đưa cây/map trong cache cho writer sửa.

    Chỉ bytes/chuỗi/tuple nguyên thủy bất biến được dùng chung. Kể cả các
    dataclass frozen và mappingproxy đều có vỏ mới; cây XML deep-copy.
    Cache thuộc callback của đúng primitive Excel, dọn trong finally.
    """
    def sao(cac, ham):
        ket = []
        for i, v in enumerate(cac):
            if i % 64 == 0:
                kiem_huy()
            ket.append(ham(v))
        return tuple(ket)

    g = doc.goi.goi
    parts = sao(g.zip.phan, lambda p: replace(p))
    cay = {}
    for ten, root in g.cay.items():
        kiem_huy()
        cay[ten] = deepcopy(root)
    goi = replace(doc.goi, goi=replace(g,
        zip=replace(g.zip, phan=parts), cay=MappingProxyType(cay),
        quan_he=MappingProxyType({k: MappingProxyType(dict(qs))
                                 for k, qs in g.quan_he.items()}),
        thong_ke=MappingProxyType(dict(g.thong_ke))),
        # ban_ghi giữ PhanZip header-only, khác zip.phan đã giải nén.
        # Sao đúng giá trị nguồn để đọc ngoài cache ở B7 vẫn đối chiếu được.
        ban_ghi=sao(doc.goi.ban_ghi, lambda b: replace(b, phan=replace(b.phan))))
    def sao_vung(v):
        manh = tuple(ManhExcel(m.phan, m.so_nut, m.so_run, m.thuoc_tinh,
                              m.bat_dau, m.ket_thuc, m.byte, m.neo) for m in v.manh)
        return VungExcel(v.ma, v.so_sheet, v.o, v.chi_so_chu, v.chu, manh, v.duoc_sua, v.bam_chu)

    def sao_o(o):
        return OExcel(o.so_sheet, o.dia_chi, o.kieu, o.gia_tri, o.style, o.style_goc,
                      o.style_hang, o.style_cot, o.style_hieu_luc, o.chi_so_chu,
                      o.vung, o.hang_an, o.cot_an, o.byte_bat_dau, o.byte_ket_thuc, o.xml_goc)

    return replace(doc, goi=goi, vung=sao(doc.vung, sao_vung), o=sao(doc.o, sao_o),
        styles=tuple(MappingProxyType(dict(s)) for s in doc.styles))


def doc_excel(du_lieu, *, kiem_huy):
    """Đọc bytes thật, tái dùng tối đa hai bản kiểm trong cùng primitive.

    Khóa là toàn bytes, không phải băm/map caller. Mỗi lần trả bản độc
    lập để doc_lai_nguon vẫn bắt mọi sửa cây/map/CRC/offset. Ngoài lượt
    có callback cung cấp cache riêng thì luôn chạy reader đầy đủ.
    """
    kiem_huy()
    cache = getattr(getattr(kiem_huy, '__self__', None), 'doc_excel_cache', None)
    if type(cache) is not dict:
        return _doc_excel(du_lieu, kiem_huy=kiem_huy)
    if du_lieu not in cache:
        doc = _doc_excel(du_lieu, kiem_huy=kiem_huy)
        if len(cache) >= 2:
            cache.clear()
        cache[du_lieu] = doc
    doc = _sao_ban_doc(cache[du_lieu], kiem_huy)
    kiem_huy()
    return doc


def _doc_excel(du_lieu, *, kiem_huy):
    """Bytes → mọi đơn vị logic/map và raw ô; chỉ trả sau khi cả gói đạt.

    Không có preview/cắt dữ liệu, cờ đạt hai lớp, đường mạng hoặc file máy.
    Đối tượng này chứa gốc, không được đưa vào báo cáo/kết quả cho Cloud.
    """
    kiem_huy()
    goi = doc_goi_excel(du_lieu, kiem_huy=kiem_huy)
    doc = _DocExcel(goi, kiem_huy)
    try:
        for phan, root in goi.goi.cay.items():
            kiem_huy()
            if phan.startswith('xl/') and phan.endswith('.xml'):
                (kiem_theme if phan == 'xl/theme/theme1.xml' else kiem_excel)(root, kiem_huy)
        styles = _styles(goi.goi.cay.get('xl/styles.xml'), kiem_huy)
        doc.shared_strings()
        names = doc.sheets(styles)
        sst = goi.goi.cay.get('xl/sharedStrings.xml')
        if sst is not None and 'count' in sst.attrib and int(sst.get('count')) != sum(len(x) for x in doc.refs):
            _sai()
        for phan, method in (('docProps/core.xml', doc.core), ('docProps/app.xml', lambda r: doc.app(r, names)),
                              ('docProps/custom.xml', doc.custom)):
            if phan in goi.goi.cay:
                method(goi.goi.cay[phan])
        pr = goi.goi.cay['xl/workbook.xml'].find(S + 'workbookPr')
        kiem_huy()
        return ExcelDaDoc(goi, tuple(doc.vung), tuple(doc.o), tuple(doc.shared),
                           tuple(tuple(x) for x in doc.refs), styles, tuple(doc.gop),
                           pr is not None and _bool(pr.get('date1904')), doc.chu_dem,
                           'sha256:' + sha256(du_lieu).hexdigest())
    finally:
        # Không có tệp tạm. Giải phóng bảng làm việc cả khi XML/trần/hủy lỗi.
        doc.maps.clear()
        doc.raw.clear()
        doc.vung.clear()
        doc.o.clear()
        doc.refs.clear()
