"""Profile XML Excel và map lexical nội bộ MASK-B3; không serialize cây.

Cây đã qua Expat/B1 trước khi lập map. Bộ tách lexical chỉ tìm khoảng byte,
không thay parser XML hoặc chuẩn hóa NFC/Cf của nội dung gốc.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
import re
from xml.sax.saxutils import escape

from .xml_an_toan import S_NS, R_NS, XML_NS, A_NS
from .zip_an_toan import _sai, _vuot

_ST = re.compile(r'_x([0-9a-fA-F]{4})_')
_ENTITY = re.compile(r'&(?:#x[0-9a-fA-F]+|#[0-9]+|amp|lt|gt|apos|quot);')
_ATTR = re.compile(r'''([^\s=<>/'"]+)\s*=\s*(['"])(.*?)\2''', re.DOTALL)
_PREFIX = {'xml': XML_NS, 'r': R_NS}
_TRANG = ' \t\r\n'


def chu_xml(chu):
    """Chép chọn lọc chu_xml của Hóa đơn: escape literal ST/control/CR.

    Không ép số sang chuỗi, không cắt ô hoặc dựng workbook. Chỉ helper cho
    patch text ở B4/B6; B3 chỉ đọc. Xem nguồn/quyền và SHA tại NGUON.md.
    """
    if type(chu) is not str or any(0xD800 <= ord(c) <= 0xDFFF for c in chu):
        _sai()
    chu = _ST.sub(lambda m: '_x005F_' + m[0][1:], chu)
    chu = ''.join(c if (c in '\t\n\r' or 0x20 <= ord(c) <= 0xD7FF
                        or 0xE000 <= ord(c) <= 0xFFFD or 0x10000 <= ord(c) <= 0x10FFFF)
                  else f'_x{ord(c):04X}_' for c in chu)
    return escape(chu).replace('\r', '&#13;')


@dataclass(frozen=True, repr=False)
class ChuXML:
    chu: str = field(repr=False)
    byte: tuple[tuple[int, int], ...] = field(repr=False)
    neo: int | None


@dataclass(frozen=True, repr=False)
class NutXML:
    so: int
    bat_dau: int
    ket_thuc: int
    text: ChuXML = field(repr=False)
    thuoc_tinh: object = field(repr=False)


def _giai_xml(chu, offsets, dau, cuoi, *, attr=False, kiem_huy=None):
    ds, vi_tri, pos = [], [], dau
    while pos < cuoi:
        if kiem_huy is not None and (pos - dau) % 4096 == 0:
            kiem_huy()
        het, c = pos + 1, chu[pos]
        if c == '&':
            m = _ENTITY.match(chu, pos, cuoi)
            if m is None:
                _sai()
            ma, het = m[0][1:-1], m.end()
            if ma.startswith('#'):
                c = chr(int(ma[2:], 16) if ma.startswith('#x') else int(ma[1:]))
            else:
                c = {'amp': '&', 'lt': '<', 'gt': '>', 'apos': "'", 'quot': '"'}[ma]
        elif c == '\r':
            if het < cuoi and chu[het] == '\n':
                het += 1
            c = ' ' if attr else '\n'
        elif attr and c in '\n\t':
            c = ' '
        ds.append(c)
        vi_tri.append((offsets[pos], offsets[het]))
        pos = het
    return ChuXML(''.join(ds), tuple(vi_tri), offsets[dau])


def giai_st(x, kiem_huy=None):
    """Một lượt ST_Xstring, rồi ghép surrogate pair; giữ nguyên NFD/Cf/CR."""
    chu, spans, pos = [], [], 0
    while pos < len(x.chu):
        if kiem_huy is not None and pos % 4096 == 0:
            kiem_huy()
        m = _ST.match(x.chu, pos)
        het = m.end() if m else pos + 1
        c = chr(int(m[1], 16)) if m else x.chu[pos]
        span = (x.byte[pos][0], x.byte[het - 1][1])
        if 0xDC00 <= ord(c) <= 0xDFFF:
            _sai()
        if 0xD800 <= ord(c) <= 0xDBFF:
            sau = _ST.match(x.chu, het)
            if sau is None or not 0xDC00 <= int(sau[1], 16) <= 0xDFFF:
                _sai()
            c = chr(0x10000 + ((ord(c) - 0xD800) << 10) + int(sau[1], 16) - 0xDC00)
            het = sau.end()
            span = (span[0], x.byte[het - 1][1])
        chu.append(c)
        spans.append(span)
        pos = het
    return ChuXML(''.join(chu), tuple(spans), x.neo)


def map_xml(raw, root, kiem_huy):
    """Map theo cây đã kiểm, UTF-8/UTF-16; CDATA cần patch riêng nên chặn."""
    from types import MappingProxyType

    if raw.startswith(b'\xef\xbb\xbf'):
        codec, bom = 'utf-8', 3
    elif raw.startswith(b'\xff\xfe'):
        codec, bom = 'utf-16-le', 2
    elif raw.startswith(b'\xfe\xff'):
        codec, bom = 'utf-16-be', 2
    else:
        codec = 'utf-16-le' if raw.startswith(b'<\0') else ('utf-16-be' if raw.startswith(b'\0<') else 'utf-8')
        bom = 0
    try:
        chu = raw[bom:].decode(codec)
    except UnicodeError:
        _sai()
    offsets, byte = [bom], bom
    for i, c in enumerate(chu):
        if i % 4096 == 0:
            kiem_huy()
        byte += len(c.encode(codec))
        offsets.append(byte)
    nodes, stack, muc, pos, so = list(root.iter()), [], {}, 0, 0
    try:
        while pos < len(chu):
            kiem_huy()
            if chu.startswith('<?xml', pos) and chu[pos + 5:pos + 6] in _TRANG:
                het = chu.find('?>', pos)
                if het < 0:
                    _sai()
                pos = het + 2
                continue
            if chu.startswith('<![CDATA[', pos):
                # CDATA/mixed text cần nhiều miền lexical và kiểu escape khác.
                # Chưa có profile patch chứng minh thì từ chối, không map mù
                # một khoảng xuyên delimiter hoặc ghi XML escape vào CDATA.
                _sai()
            if chu[pos] == '<':
                het, quote = pos + 1, None
                while het < len(chu):
                    c = chu[het]
                    if quote:
                        if c == quote:
                            quote = None
                    elif c in "\"'":
                        quote = c
                    elif c == '>':
                        break
                    het += 1
                if het == len(chu):
                    _sai()
                if chu.startswith('</', pos):
                    if not stack:
                        _sai()
                    m = stack.pop()
                    m['cuoi'] = offsets[het + 1]
                else:
                    if so >= len(nodes):
                        _sai()
                    e, so = nodes[so], so + 1
                    attrs = {}
                    for a in _ATTR.finditer(chu, pos, het):
                        ten = a[1]
                        if ten == 'xmlns' or ten.startswith('xmlns:'):
                            continue  # B1 đã kiểm cả khai namespace chưa dùng.
                        if ':' in ten:
                            prefix, local = ten.split(':')
                            if prefix not in _PREFIX:
                                # xsi:type trong core metadata cũng được map đúng.
                                from .xml_an_toan import XSI_NS
                                if prefix != 'xsi':
                                    _sai()
                                ns = XSI_NS
                            else:
                                ns = _PREFIX[prefix]
                            ten = '{' + ns + '}' + local
                        x = _giai_xml(chu, offsets, a.start(3), a.end(3), attr=True, kiem_huy=kiem_huy)
                        if e.get(ten) != x.chu:
                            _sai()
                        attrs[ten] = x
                    if set(attrs) != set(e.attrib):
                        _sai()
                    tu_dong = chu[pos:het].rstrip().endswith('/')
                    m = {'e': e, 'so': so - 1, 'dau': offsets[pos], 'cuoi': offsets[het + 1],
                         'neo': None if tu_dong else offsets[het + 1], 'attrs': attrs, 'text': []}
                    muc[e] = m
                    if not tu_dong:
                        stack.append(m)
                pos = het + 1
            else:
                het = chu.find('<', pos)
                if het < 0:
                    het = len(chu)
                if stack:
                    stack[-1]['text'].append(_giai_xml(chu, offsets, pos, het, kiem_huy=kiem_huy))
                pos = het
        if stack or so != len(nodes):
            _sai()
        kq = {}
        for e, m in muc.items():
            kiem_huy()
            xs = m['text']
            text = ChuXML(''.join(x.chu for x in xs), tuple(s for x in xs for s in x.byte), m['neo'])
            # Với leaf, phải bằng parser thật; node cấu trúc chỉ chứa whitespace.
            if not len(e) and text.chu != (e.text or ''):
                _sai()
            kq[e] = NutXML(m['so'], m['dau'], m['cuoi'], text, MappingProxyType(m['attrs']))
        return MappingProxyType(kq)
    finally:
        stack.clear()
        muc.clear()
        offsets.clear()


def so_nguyen(v, tran=4294967295, *, duoi=0):
    if not isinstance(v, str) or not re.fullmatch(r'[0-9]{1,10}', v):
        _sai()
    so = int(v)
    if not duoi <= so <= tran:
        _sai()
    return so


def so_thuc(v):
    if not isinstance(v, str) or not re.fullmatch(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?', v):
        _sai()
    # Chỉ kiểm lexical, không chuyển float/round khiến đổi giá trị nguồn.
    if len(v) > 128:
        _sai()
    try:
        # Kiểm miền hữu hạn bằng Decimal, vẫn trả nguyên lexical, không float/round.
        if Decimal(v).copy_abs() > Decimal('1.7976931348623157e308'):
            _sai()
    except InvalidOperation:
        _sai()
    return v


def _so_trong(duoi, tren):
    def kiem(v):
        so_thuc(v)
        d = Decimal(v)
        if not Decimal(str(duoi)) <= d <= Decimal(str(tren)):
            _sai()
    return kiem


def ngay(v):
    if not isinstance(v, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}(?:T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})?)?', v):
        _sai()
    try:
        datetime.fromisoformat(v.replace('Z', '+00:00'))
    except ValueError:
        _sai()
    return v


def _mot_trong(*values):
    def kiem(v):
        if v not in values:
            _sai()
    return kiem


def _mau(pattern):
    def kiem(v):
        if not re.fullmatch(pattern, v):
            _sai()
    return kiem


BOOL = _mot_trong('0', '1', 'false', 'true')
UINT = so_nguyen
NUM = so_thuc
FONT = _mot_trong('Calibri', 'Calibri Light', 'Arial', 'Arial Narrow', 'Times New Roman',
                 'Cambria', 'Cambria Math', 'Tahoma', 'Verdana', 'Courier New', 'Aptos',
                 'Aptos Display', 'Aptos Narrow', 'Trebuchet MS', 'Segoe UI', 'Symbol',
                 'Wingdings', 'ＭＳ Ｐゴシック', 'ＭＳ ゴシック', 'ＭＳ 明朝', 'MS Mincho',
                 'MS Gothic', 'Yu Gothic', 'Yu Mincho', '游ゴシック', '游明朝', '宋体', '新宋体',
                 '等线', '等线 Light', 'SimSun', 'SimHei', 'Microsoft YaHei', '微軟正黑體',
                 'Microsoft JhengHei', '新細明體', 'PMingLiU', 'MingLiU', '맑은 고딕',
                 'Malgun Gothic', '굴림', 'Gulim', 'Batang', '바탕', 'Times New Roman',
                 'Angsana New', 'Cordia New', 'Mangal', 'Latha', 'Vrinda', 'Raavi',
                 'Shruti', 'Tunga', 'Gautami', 'Kartika', 'DaunPenh', 'DokChampa',
                 'Iskoola Pota', 'Kalinga', 'Estrangelo Edessa', 'MV Boli', 'Nyala',
                 'Plantagenet Cherokee', 'Euphemia', 'Sylfaen', 'Microsoft Himalaya',
                 'Microsoft Yi Baiti', 'Mongolian Baiti', 'Microsoft Uighur', '')
FORMAT = _mot_trong('General', '0', '0.00', '#,##0', '#,##0.00', '0%', '0.00%', '@',
                   'dd/mm/yyyy', 'yyyy-mm-dd', 'mm-dd-yy', 'dd/mm/yyyy hh:mm',
                   'yyyy-mm-dd hh:mm:ss', 'hh:mm', 'hh:mm:ss', '#,##0" VND"',
                   '#,##0 "VND"', '#,##0.00" VND"', '#,##0 [$VND-42A]')
COLOR = {'rgb': _mau(r'[0-9A-Fa-f]{8}'), 'indexed': UINT, 'auto': BOOL, 'theme': UINT, 'tint': _so_trong(-1, 1)}
REF = _mau(r'[A-Z]{1,3}[1-9][0-9]{0,6}(?::[A-Z]{1,3}[1-9][0-9]{0,6})?')
CELL = _mau(r'[A-Z]{1,3}[1-9][0-9]{0,6}')
RID = '{' + R_NS + '}id'
SPACE = '{' + XML_NS + '}space'


def _kiem(e, attrs, con=(), *, bat_buoc=(), text=False, thu_tu=True):
    if not set(bat_buoc) <= set(e.attrib) or not set(e.attrib) <= set(attrs):
        _sai()
    for k, v in e.attrib.items():
        attrs[k](v)
    if not text and (e.text or '').strip(_TRANG):
        _sai()
    ds = [c.tag.rsplit('}', 1)[-1] for c in e]
    if not thu_tu:
        if set(ds) - {n for n, _, _ in con}:
            _sai()
        for ten, duoi, tren in con:
            if not duoi <= ds.count(ten) <= tren:
                _sai()
        if any((c.tail or '').strip(_TRANG) for c in e):
            _sai()
        return
    pos = 0
    for ten, duoi, tren in con:
        dem = 0
        while pos < len(ds) and ds[pos] == ten:
            dem += 1
            pos += 1
        if not duoi <= dem <= tren:
            _sai()
    if pos != len(ds) or any((c.tail or '').strip(_TRANG) for c in e):
        _sai()


def _cs(*names):
    return tuple((n, 0, 1) for n in names)


# Mỗi attribute được phân loại bằng miền giá trị hoặc chuyển sang vùng text.
_LUAT = {
    'workbook': ({}, _cs('fileVersion', 'workbookPr', 'bookViews') + (('sheets', 1, 1),) + _cs('calcPr')),
    'fileVersion': ({'appName': _mot_trong('xl'), 'lastEdited': UINT, 'lowestEdited': UINT, 'rupBuild': UINT}, ()),
    'workbookPr': ({'date1904': BOOL, 'filterPrivacy': BOOL, 'defaultThemeVersion': UINT,
                    'showObjects': _mot_trong('all', 'placeholders', 'none'),
                    'updateLinks': _mot_trong('userSet', 'never', 'always')}, ()),
    'bookViews': ({}, (('workbookView', 1, 50),)),
    'workbookView': ({**{k: UINT for k in ('xWindow', 'yWindow', 'windowWidth', 'windowHeight', 'activeTab', 'firstSheet', 'tabRatio')},
                      **{k: BOOL for k in ('minimized', 'showHorizontalScroll', 'showVerticalScroll', 'showSheetTabs', 'autoFilterDateGrouping')},
                      'visibility': _mot_trong('visible', 'hidden', 'veryHidden')}, ()),
    'sheets': ({}, (('sheet', 1, 50),)),
    'sheet': ({'name': lambda v: None, 'sheetId': UINT, 'state': _mot_trong('visible'), RID: _mau(r'rId[1-9][0-9]{0,2}')}, ()),
    'calcPr': ({'calcId': UINT, 'fullCalcOnLoad': BOOL, 'forceFullCalc': BOOL,
                'calcMode': _mot_trong('auto', 'manual', 'autoNoTable')}, ()),
    'calcChain': ({}, ()),  # Chỉ chấp nhận phần rỗng; cache tham chiếu công thức bị chặn.
    'worksheet': ({}, _cs('sheetPr', 'dimension', 'sheetViews', 'sheetFormatPr', 'cols')
                   + (('sheetData', 1, 1),) + _cs('mergeCells', 'printOptions', 'pageMargins', 'pageSetup', 'rowBreaks', 'colBreaks', 'ignoredErrors')),
    'sheetPr': ({'enableFormatConditionsCalculation': BOOL, 'published': BOOL}, _cs('tabColor', 'outlinePr', 'pageSetUpPr')),
    'tabColor': (COLOR, ()),
    'outlinePr': ({k: BOOL for k in ('applyStyles', 'summaryBelow', 'summaryRight', 'showOutlineSymbols')}, ()),
    'pageSetUpPr': ({'autoPageBreaks': BOOL, 'fitToPage': BOOL}, ()),
    'dimension': ({'ref': REF}, ()),
    'sheetViews': ({}, (('sheetView', 1, 50),)),
    'sheetView': ({**{k: BOOL for k in ('tabSelected', 'showGridLines', 'showRowColHeaders', 'showZeros', 'rightToLeft', 'showFormulas', 'showOutlineSymbols', 'defaultGridColor')},
                   **{k: UINT for k in ('workbookViewId', 'zoomScale', 'zoomScaleNormal', 'zoomScaleSheetLayoutView', 'zoomScalePageLayoutView', 'colorId')},
                   'topLeftCell': CELL, 'view': _mot_trong('normal', 'pageBreakPreview', 'pageLayout')},
                  _cs('pane') + (('selection', 0, 4),)),
    'pane': ({'xSplit': NUM, 'ySplit': NUM, 'topLeftCell': CELL,
              'activePane': _mot_trong('topLeft', 'topRight', 'bottomLeft', 'bottomRight'),
              'state': _mot_trong('split', 'frozen', 'frozenSplit')}, ()),
    'selection': ({'pane': _mot_trong('topLeft', 'topRight', 'bottomLeft', 'bottomRight'),
                   'activeCell': CELL, 'activeCellId': UINT,
                   'sqref': _mau(r'[A-Z]{1,3}[1-9][0-9]{0,6}(?::[A-Z]{1,3}[1-9][0-9]{0,6})?(?: [A-Z]{1,3}[1-9][0-9]{0,6}(?::[A-Z]{1,3}[1-9][0-9]{0,6})?)*')}, ()),
    'sheetFormatPr': ({**{k: UINT for k in ('baseColWidth', 'outlineLevelRow', 'outlineLevelCol')},
                       **{k: NUM for k in ('defaultColWidth', 'defaultRowHeight')},
                       **{k: BOOL for k in ('customHeight', 'zeroHeight', 'thickTop', 'thickBottom') }}, ()),
    'cols': ({}, (('col', 1, 16384),)),
    'col': ({**{k: UINT for k in ('min', 'max', 'style', 'outlineLevel')}, 'width': NUM,
             **{k: BOOL for k in ('hidden', 'bestFit', 'customWidth', 'collapsed', 'phonetic')}}, ()),
    'sheetData': ({}, (('row', 0, 100000),)),
    'row': ({**{k: UINT for k in ('r', 's', 'outlineLevel')}, 'ht': NUM, 'spans': _mau(r'[1-9][0-9]{0,4}:[1-9][0-9]{0,4}'),
             **{k: BOOL for k in ('hidden', 'customHeight', 'customFormat', 'collapsed', 'thickTop', 'thickBot', 'ph')}}, (('c', 0, 20000),)),
    'c': ({'r': CELL, 's': UINT, 't': _mot_trong('n', 's', 'inlineStr', 'b', 'e', 'd')}, _cs('v', 'is')),
    'v': ({}, ()),
    'is': ({}, _cs('t') + (('r', 0, 100000),)),
    'si': ({}, _cs('t') + (('r', 0, 100000),)),
    'sst': ({'count': UINT, 'uniqueCount': UINT}, (('si', 0, 100000),)),
    't': ({SPACE: _mot_trong('preserve', 'default')}, ()),
    'r': ({}, _cs('rPr') + (('t', 1, 1),)),
    'rPr': ({}, _cs('rFont', 'charset', 'family', 'b', 'i', 'strike', 'outline', 'shadow',
                    'condense', 'extend', 'color', 'sz', 'u', 'vertAlign', 'scheme')),
    'rFont': ({'val': FONT}, ()),
    'name': ({'val': FONT}, ()),
    'b': ({'val': BOOL}, ()), 'i': ({'val': BOOL}, ()), 'strike': ({'val': BOOL}, ()),
    'outline': ({'val': BOOL}, ()), 'shadow': ({'val': BOOL}, ()),
    'condense': ({'val': BOOL}, ()), 'extend': ({'val': BOOL}, ()),
    'charset': ({'val': UINT}, ()), 'family': ({'val': UINT}, ()), 'sz': ({'val': NUM}, ()),
    'u': ({'val': _mot_trong('single', 'double', 'singleAccounting', 'doubleAccounting', 'none')}, ()),
    'vertAlign': ({'val': _mot_trong('baseline', 'superscript', 'subscript')}, ()),
    'scheme': ({'val': _mot_trong('major', 'minor', 'none')}, ()), 'color': (COLOR, ()),
    'mergeCells': ({'count': UINT}, (('mergeCell', 1, 20000),)),
    'mergeCell': ({'ref': REF}, ()),
    'printOptions': ({k: BOOL for k in ('horizontalCentered', 'verticalCentered', 'headings', 'gridLines', 'gridLinesSet')}, ()),
    'pageMargins': ({k: NUM for k in ('left', 'right', 'top', 'bottom', 'header', 'footer')}, ()),
    'pageSetup': ({**{k: UINT for k in ('paperSize', 'scale', 'firstPageNumber', 'fitToWidth', 'fitToHeight', 'horizontalDpi', 'verticalDpi', 'copies')},
                   **{k: BOOL for k in ('useFirstPageNumber', 'usePrinterDefaults', 'blackAndWhite', 'draft')},
                   'orientation': _mot_trong('default', 'portrait', 'landscape'),
                   'cellComments': _mot_trong('none'), 'errors': _mot_trong('displayed', 'blank', 'dash', 'NA')}, ()),
    'rowBreaks': ({'count': UINT, 'manualBreakCount': UINT}, (('brk', 0, 20000),)),
    'colBreaks': ({'count': UINT, 'manualBreakCount': UINT}, (('brk', 0, 20000),)),
    'brk': ({'id': UINT, 'min': UINT, 'max': UINT, 'man': BOOL, 'pt': BOOL}, ()),
    'ignoredErrors': ({}, (('ignoredError', 1, 20000),)),
    'ignoredError': ({'sqref': REF, **{k: BOOL for k in ('evalError', 'twoDigitTextNumber', 'numberStoredAsText', 'emptyCellReference', 'unlockedFormula', 'calculatedColumn') }}, ()),
    'styleSheet': ({}, _cs('numFmts', 'fonts', 'fills', 'borders', 'cellStyleXfs', 'cellXfs', 'cellStyles', 'dxfs', 'tableStyles', 'colors')),
    'numFmts': ({'count': UINT}, (('numFmt', 0, 100000),)),
    'numFmt': ({'numFmtId': UINT, 'formatCode': FORMAT}, ()),
    'fonts': ({'count': UINT}, (('font', 1, 100000),)),
    'font': ({}, _cs('name', 'charset', 'family', 'b', 'i', 'strike', 'outline', 'shadow', 'condense', 'extend', 'color', 'sz', 'u', 'vertAlign', 'scheme')),
    'fills': ({'count': UINT}, (('fill', 1, 100000),)),
    'fill': ({}, (('patternFill', 1, 1),)),
    'patternFill': ({'patternType': _mot_trong('none', 'solid', 'mediumGray', 'darkGray', 'lightGray', 'darkHorizontal', 'darkVertical', 'darkDown', 'darkUp', 'darkGrid', 'darkTrellis', 'lightHorizontal', 'lightVertical', 'lightDown', 'lightUp', 'lightGrid', 'lightTrellis', 'gray125', 'gray0625')}, _cs('fgColor', 'bgColor')),
    'fgColor': (COLOR, ()), 'bgColor': (COLOR, ()),
    'borders': ({'count': UINT}, (('border', 1, 100000),)),
    'border': ({'diagonalUp': BOOL, 'diagonalDown': BOOL, 'outline': BOOL}, _cs('left', 'right', 'top', 'bottom', 'diagonal', 'vertical', 'horizontal')),
    'cellStyleXfs': ({'count': UINT}, (('xf', 1, 100000),)),
    'cellXfs': ({'count': UINT}, (('xf', 1, 100000),)),
    'xf': ({**{k: UINT for k in ('numFmtId', 'fontId', 'fillId', 'borderId', 'xfId')},
            **{k: BOOL for k in ('applyNumberFormat', 'applyFont', 'applyFill', 'applyBorder', 'applyAlignment', 'applyProtection', 'pivotButton', 'quotePrefix')}}, _cs('alignment', 'protection')),
    'alignment': ({'horizontal': _mot_trong('general', 'left', 'center', 'right', 'fill', 'justify', 'centerContinuous', 'distributed'),
                   'vertical': _mot_trong('top', 'center', 'bottom', 'justify', 'distributed'),
                   **{k: UINT for k in ('textRotation', 'indent', 'relativeIndent', 'readingOrder')},
                   **{k: BOOL for k in ('wrapText', 'shrinkToFit', 'justifyLastLine')}}, ()),
    'protection': ({'locked': BOOL, 'hidden': BOOL}, ()),
    'cellStyles': ({'count': UINT}, (('cellStyle', 1, 100000),)),
    'cellStyle': ({'name': _mot_trong('Normal'), 'xfId': UINT, 'builtinId': _mot_trong('0'), 'customBuiltin': _mot_trong('0', 'false'), 'hidden': BOOL}, ()),
    'dxfs': ({'count': _mot_trong('0')}, ()),
    'tableStyles': ({'count': _mot_trong('0'), 'defaultTableStyle': _mau(r'TableStyle(?:Light(?:[1-9]|1[0-9]|2[01])|Medium(?:[1-9]|1[0-9]|2[0-8])|Dark(?:[1-9]|1[01]))'),
                     'defaultPivotStyle': _mau(r'PivotStyle(?:Light|Medium|Dark)(?:[1-9]|1[0-9]|2[0-8])')}, ()),
    'colors': ({}, _cs('indexedColors', 'mruColors')),
    'indexedColors': ({}, (('rgbColor', 1, 64),)),
    'rgbColor': ({'rgb': _mau(r'[0-9A-Fa-f]{8}')}, ()),
    'mruColors': ({}, (('color', 1, 100000),)),
}
for _n in ('left', 'right', 'top', 'bottom', 'diagonal', 'vertical', 'horizontal'):
    _LUAT[_n] = ({'style': _mot_trong('thin', 'medium', 'dashed', 'dotted', 'thick', 'double', 'hair', 'mediumDashed', 'dashDot', 'mediumDashDot', 'dashDotDot', 'mediumDashDotDot', 'slantDashDot')}, _cs('color'))

_LUAT['sz'][0]['val'] = _so_trong(1, 409)
_LUAT['family'][0]['val'] = lambda v: so_nguyen(v, 5)
_LUAT['charset'][0]['val'] = lambda v: so_nguyen(v, 255)
_LUAT['col'][0]['width'] = _so_trong(0, 255)
_LUAT['row'][0]['ht'] = _so_trong(0, 409)
for _n in ('row', 'col'):
    _LUAT[_n][0]['outlineLevel'] = lambda v: so_nguyen(v, 7)
for _n in ('baseColWidth', 'defaultColWidth'):
    _LUAT['sheetFormatPr'][0][_n] = _so_trong(0, 255)
_LUAT['sheetFormatPr'][0]['defaultRowHeight'] = _so_trong(0, 409)
for _n in ('outlineLevelRow', 'outlineLevelCol'):
    _LUAT['sheetFormatPr'][0][_n] = lambda v: so_nguyen(v, 7)
_LUAT['alignment'][0]['readingOrder'] = lambda v: so_nguyen(v, 2)
_LUAT['alignment'][0]['indent'] = lambda v: so_nguyen(v, 250)
for _n in ('xSplit', 'ySplit'):
    _LUAT['pane'][0][_n] = _so_trong(0, 10000000)


def kiem_excel(root, kiem_huy):
    for e in root.iter():
        kiem_huy()
        if not e.tag.startswith('{' + S_NS + '}'):
            _sai()
        ten = e.tag.rsplit('}', 1)[-1]
        luat = _LUAT.get(ten)
        if luat is None:
            _sai()
        _kiem(e, *luat, text=ten in ('t', 'v'), thu_tu=ten not in ('font', 'rPr'))
        if 'count' in e.attrib and ten != 'sst' and int(e.get('count')) != len(e):
            _sai()
        if ten in ('sheet', 'c') and not ({'name', 'sheetId', RID} if ten == 'sheet' else {'r'}) <= set(e.attrib):
            _sai()
        if ten in ('numFmt', 'mergeCell', 'row', 'col'):
            required = {'numFmt': {'numFmtId', 'formatCode'}, 'mergeCell': {'ref'},
                        'row': {'r'}, 'col': {'min', 'max'}}[ten]
            if not required <= set(e.attrib):
                _sai()
        if ten in ('name', 'rFont', 'sz', 'family', 'charset', 'vertAlign', 'scheme') and 'val' not in e.attrib:
            _sai()
        if ten in ('si', 'is') and (bool(e.find('{' + S_NS + '}t') is not None) == bool(e.findall('{' + S_NS + '}r'))):
            _sai()
        if ten in ('color', 'fgColor', 'bgColor', 'tabColor'):
            if len(set(e.attrib) - {'tint'}) > 1:
                _sai()
            if 'theme' in e.attrib and int(e.get('theme')) > 11:
                _sai()
            if 'indexed' in e.attrib and int(e.get('indexed')) > 65:
                _sai()


def kiem_theme(root, kiem_huy):
    """Theme chỉ hình học/màu/font giá trị đã phân loại, không text tùy ý."""
    empty = ({}, ())
    colors = (('dk1', 1, 1), ('lt1', 1, 1), ('dk2', 1, 1), ('lt2', 1, 1)) + tuple((f'accent{i}', 1, 1) for i in range(1, 7)) + (('hlink', 1, 1), ('folHlink', 1, 1))
    trans = _cs('tint', 'shade', 'comp', 'inv', 'gray', 'alpha', 'alphaOff', 'alphaMod', 'hue', 'hueOff', 'hueMod', 'sat', 'satOff', 'satMod', 'lum', 'lumOff', 'lumMod')
    luat = {
        'theme': ({'name': _mot_trong('Office Theme', 'Office')}, (('themeElements', 1, 1),) + _cs('objectDefaults', 'extraClrSchemeLst')),
        'themeElements': ({}, (('clrScheme', 1, 1), ('fontScheme', 1, 1), ('fmtScheme', 1, 1))),
        'clrScheme': ({'name': _mot_trong('Office', 'Office Theme')}, colors),
        'fontScheme': ({'name': _mot_trong('Office', 'Office Theme')}, (('majorFont', 1, 1), ('minorFont', 1, 1))),
        'majorFont': ({}, (('latin', 1, 1), ('ea', 1, 1), ('cs', 1, 1), ('font', 0, 100))),
        'minorFont': ({}, (('latin', 1, 1), ('ea', 1, 1), ('cs', 1, 1), ('font', 0, 100))),
        'font': ({'script': _mot_trong(*'Jpan Hang Hans Hant Arab Hebr Thai Ethi Beng Gujr Khmr Knda Guru Cans Cher Yiii Tibt Thaa Deva Telu Taml Syrc Orya Mlym Laoo Sinh Mong Viet Uigh Geor Armn'.split()), 'typeface': FONT}, ()),
        'fmtScheme': ({'name': _mot_trong('Office', 'Office Theme')}, (('fillStyleLst', 1, 1), ('lnStyleLst', 1, 1), ('effectStyleLst', 1, 1), ('bgFillStyleLst', 1, 1))),
        'fillStyleLst': ({}, (('solidFill', 0, 3), ('gradFill', 0, 3))),
        'bgFillStyleLst': ({}, (('solidFill', 0, 3), ('gradFill', 0, 3))),
        'solidFill': ({}, (('schemeClr', 0, 1), ('srgbClr', 0, 1))),
        'gradFill': ({'rotWithShape': BOOL}, (('gsLst', 1, 1),) + _cs('lin', 'path', 'tileRect')),
        'gsLst': ({}, (('gs', 2, 10),)),
        'gs': ({'pos': UINT}, (('schemeClr', 0, 1), ('srgbClr', 0, 1))),
        'lin': ({'ang': UINT, 'scaled': BOOL}, ()),
        'path': ({'path': _mot_trong('shape', 'circle', 'rect')}, _cs('fillToRect')),
        'fillToRect': ({k: _mau(r'-?[0-9]{1,9}') for k in ('l', 't', 'r', 'b')}, ()),
        'tileRect': ({k: _mau(r'-?[0-9]{1,9}') for k in ('l', 't', 'r', 'b')}, ()),
        'lnStyleLst': ({}, (('ln', 3, 3),)),
        'ln': ({'w': UINT, 'cap': _mot_trong('rnd', 'sq', 'flat'), 'cmpd': _mot_trong('sng', 'dbl', 'thickThin', 'thinThick', 'tri'), 'algn': _mot_trong('ctr', 'in')}, _cs('solidFill', 'prstDash', 'round', 'bevel', 'miter', 'headEnd', 'tailEnd')),
        'prstDash': ({'val': _mot_trong('solid', 'dot', 'dash', 'lgDash', 'dashDot', 'lgDashDot', 'lgDashDotDot', 'sysDash', 'sysDot', 'sysDashDot', 'sysDashDotDot')}, ()),
        'round': empty, 'bevel': empty, 'miter': ({'lim': UINT}, ()),
        'headEnd': ({'type': _mot_trong('none'), 'w': _mot_trong('sm', 'med', 'lg'), 'len': _mot_trong('sm', 'med', 'lg')}, ()),
        'tailEnd': ({'type': _mot_trong('none'), 'w': _mot_trong('sm', 'med', 'lg'), 'len': _mot_trong('sm', 'med', 'lg')}, ()),
        'effectStyleLst': ({}, (('effectStyle', 3, 3),)),
        'effectStyle': ({}, (('effectLst', 1, 1),)),
        'effectLst': ({}, _cs('outerShdw')),
        'outerShdw': ({'blurRad': UINT, 'dist': UINT, 'dir': UINT, 'algn': _mot_trong('ctr', 'b', 't', 'l', 'r', 'bl', 'br', 'tl', 'tr'), 'rotWithShape': BOOL}, (('srgbClr', 1, 1),)),
        'sysClr': ({'val': _mot_trong('windowText', 'window'), 'lastClr': _mau(r'[0-9A-Fa-f]{6}')}, trans),
        'srgbClr': ({'val': _mau(r'[0-9A-Fa-f]{6}')}, trans),
        'schemeClr': ({'val': _mot_trong(*'dk1 lt1 dk2 lt2 accent1 accent2 accent3 accent4 accent5 accent6 hlink folHlink phClr tx1 tx2 bg1 bg2'.split())}, trans),
        'objectDefaults': empty, 'extraClrSchemeLst': empty,
    }
    for n in ('latin', 'ea', 'cs'):
        luat[n] = ({'typeface': FONT, 'panose': _mau(r'[0-9A-Fa-f]{20}'), 'pitchFamily': UINT, 'charset': UINT}, ())
    for n, _, _ in colors:
        luat[n] = ({}, (('sysClr', 0, 1), ('srgbClr', 0, 1)))
    for n, _, _ in trans:
        luat[n] = ({'val': _mau(r'-?[0-9]{1,9}')}, ())
    for e in root.iter():
        kiem_huy()
        ten = e.tag.rsplit('}', 1)[-1]
        if not e.tag.startswith('{' + A_NS + '}') or ten not in luat:
            _sai()
        _kiem(e, *luat[ten], thu_tu=ten not in ('schemeClr', 'srgbClr', 'sysClr'))
        if ten in {n for n, _, _ in colors} | {'solidFill', 'gs'} and len(e) != 1:
            _sai()
        if ten in ('fillStyleLst', 'bgFillStyleLst') and len(e) != 3:
            _sai()
