'use strict';

// Chạy: node --test tests/g3_hd_2b.cjs. Chỉ DEMO tự tạo; không browser/mạng/đĩa xuất.
// KTT_PYTHON tùy chọn trỏ interpreter đã cài, không tự cài hay gọi dịch vụ.
const { test, before } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const Module = require('node:module');
const { spawnSync } = require('node:child_process');
const { createHash } = require('node:crypto');
const adapter = require('../engines/e_hoa_don/bang_ke.cjs');
const sourceRequire = Module.createRequire(adapter.NGUON);
const ExcelJS = sourceRequire('exceljs');

function xml({ number = '000001', net = '100.010000', tax = '10.001000', total = '110.011000', amount = '100.010000', price = '80.008', count = 2 } = {}) {
  const tag = (name, value) => value === null ? '' : `<${name}>${value}</${name}>`;
  const lines = Array.from({ length: count }, (_, i) => `<HHDVu><STT>00${i + 1}</STT>
    <TChat>1</TChat><MHHDVu>000${i + 1}</MHHDVu><THHDVu>DEMO ${i + 1}</THHDVu>
    <DVTinh>CAI</DVTinh><SLuong>1.250000</SLuong><DGia>${price}</DGia>
    <ThTien>${amount}</ThTien><TSuat>10%</TSuat></HHDVu>`).join('');
  // Tổng tường minh cố ý không bằng tổng dòng; adapter phải giữ nguyên nguồn.
  return `<HDon><DLHDon><TTChung><PBan>2.1.0</PBan><KHMSHDon>01</KHMSHDon>
    <KHHDon>DEMO</KHHDon><SHDon>${number}</SHDon><NLap>2026-10-30</NLap><DVTTe>VND</DVTTe>
    </TTChung><NDHDon><NBan><MST>0000000001</MST></NBan><NMua><MST>0000000002</MST></NMua>
    <DSHHDVu>${lines}</DSHHDVu><TToan>${tag('TgTCThue', net)}${tag('TgTThue', tax)}${tag('TgTTTBSo', total)}</TToan>
    </NDHDon></DLHDon></HDon>`;
}

const raws = {
  demo: xml(), second: xml({ number: '000002', total: '-12.340000', count: 1 }),
  big: xml({ total: '999999999999999999.123456' }), missing: xml({ tax: null }),
  zero: xml({ total: '0.000000' }), fraction: xml({ total: '110.011234' }),
  sourceBig: xml({ total: '1000000000000000000' }),
  sourceScale: xml({ total: '0.1234567' }),
  duplicate: xml().replace('<TgTTTBSo>110.011000</TgTTTBSo>', '<TgTTTBSo>110.011000</TgTTTBSo><TgTTTBSo>999</TgTTTBSo>'),
  bad: '<HDon>DEMO', unknown: '<DEMO/>',
};
let fixtures;

before(() => {
  const candidates = [process.env.KTT_PYTHON, 'python', 'python3',
    path.join(process.env.APPDATA || '', 'uv/python/cpython-3.14.7-windows-x86_64-none/python.exe')].filter(Boolean);
  const python = candidates.find(p => spawnSync(p, ['-B', '--version'], { encoding: 'utf8' }).status === 0);
  assert.ok(python, 'NOT_RUN: thiếu Python cho parser HD-1 thật; đặt KTT_PYTHON.');
  const code = String.raw`
import sys, json
sys.path.insert(0, sys.argv[1])
from kho_tri_thuc.engines.e_hoa_don.doc import doc_xml
from kho_tri_thuc.nguon import hoa_don_xml as p
from kho_tri_thuc.ha_tang.primitives import sha256
out = {}
for name, xml in json.load(sys.stdin).items():
    raw = xml.encode('utf8')
    ctx = p.InvoiceReadContext(
        source_instance='DEMO_HD_2B', source_profile_ref=p.PROFILE_REF,
        profile_document_sha256=p.PROFILE_DOCUMENT_SHA256,
        profile_payload_sha256='a'*64, profile_payload_binding='BOUND',
        identity_profile_ref=p.IDENTITY_PROFILE_REF,
        company=p.CompanyFact('0000000002', 'PN_DEMO', 'DEMO_MAP', 1, 'DEMO_SCOPE'),
        expected_raw_ref=p.XmlRawRef(sha256(raw), len(raw)))
    out[name] = p.ra_json(doc_xml(raw, ctx,
        tep_xml_id='10000000-0000-4000-8000-000000000001',
        chi_tiet_nguon_tep_id='10000000-0000-4000-8000-000000000002'))
print(json.dumps(out, ensure_ascii=False))
`;
  const result = spawnSync(python, ['-B', '-X', 'utf8', '-c', code, path.resolve(__dirname, '../src')], {
    input: JSON.stringify(raws), encoding: 'utf8', timeout: 30000, maxBuffer: 4 * 1024 * 1024,
  });
  assert.equal(result.status, 0, result.stderr || result.error?.message);
  fixtures = JSON.parse(result.stdout);
  assert.equal(fixtures.demo.hoa_don.dong.length, 2);
});

function loadSource({ failPdf = false } = {}) {
  const files = new Map();
  const html = [];
  const calls = { launch: 0, close: 0, pdf: 0 };
  class MemoryWorkbook extends ExcelJS.Workbook {
    constructor() {
      super();
      this.xlsx.writeFile = async name => { files.set(name, await this.xlsx.writeBuffer()); };
    }
  }
  const chromium = {
    async launch(opts) {
      calls.launch++;
      assert.deepEqual(opts, { headless: true });
      return {
        async newPage() {
          return {
            async setContent(content) { html.push(content); },
            async pdf() {
              calls.pdf++;
              if (failPdf) throw new Error('DEMO_PDF_FAILED');
              // Chỉ giả giao thức page.pdf, không coi buffer này là PDF nghiệm thu.
              return Buffer.from('DEMO_PDF_TRANSPORT');
            },
          };
        },
        async close() { calls.close++; },
      };
    },
  };
  const m = new Module(adapter.NGUON);
  m.filename = adapter.NGUON;
  m.require = spec => {
    if (spec === 'exceljs') return { Workbook: MemoryWorkbook };
    if (spec === 'playwright') return { chromium };
    assert.ok(['fast-xml-parser', './config'].includes(spec), `Import ngoài phạm vi: ${spec}`);
    return sourceRequire(spec);
  };
  // Thực thi đúng bytes nguồn, chỉ tiêm transport Excel trong RAM / Chromium giả.
  m._compile(fs.readFileSync(adapter.NGUON, 'utf8'), adapter.NGUON);
  return { source: m.exports, files, html, calls, exporter: adapter.taoBoXuat(m.exports) };
}

const hasCode = code => e => e.code === code;

test('nguồn đúng SHA/version đã đối chiếu, wrapper mặc định nạp được', () => {
  assert.equal(createHash('sha256').update(fs.readFileSync(adapter.NGUON, 'utf8').replace(/\r\n/g, '\n')).digest('hex'), adapter.SHA256_NGUON);
  assert.equal(sourceRequire('../package.json').version, '1.0.0');
  assert.equal(typeof adapter.napNguon().buildExcel, 'function');
});

test('build Excel nguồn → đọc lại XLSX: đủ hóa đơn, giữ ID/Decimal/tổng nguồn', async () => {
  const s = loadSource();
  const input = [fixtures.demo, fixtures.second, fixtures.big, fixtures.zero];
  const before = JSON.stringify(input);
  assert.equal(await s.exporter.xuatBangKe(input, 'DEMO HD-2b', 'DEMO.xlsx'), 'DEMO.xlsx');
  const wb = new ExcelJS.Workbook();
  await wb.xlsx.load(s.files.get('DEMO.xlsx'));
  const ws = wb.getWorksheet('DEMO HD-2b');
  assert.equal(ws.actualRowCount - 1, input.length);
  const col = (row, title) => {
    const idx = ws.getRow(1).values.findIndex(v => v === title);
    assert.ok(idx > 0);
    return ws.getRow(row).getCell(idx).value;
  };
  assert.equal(col(2, 'So HD'), '000001');
  assert.equal(col(2, 'Ky hieu mau so'), '01');
  assert.equal(col(2, 'MST nguoi ban'), '0000000001');
  assert.equal(col(2, 'MST nguoi mua'), '0000000002');
  assert.equal(col(2, 'Ngay lap'), '30/10/2026');
  assert.equal(col(2, 'Tien chua thue'), '100.010000');
  assert.equal(col(2, 'Tong thanh toan'), '110.011000');
  assert.equal(col(3, 'Tong thanh toan'), '-12.340000');
  assert.equal(col(4, 'Tong thanh toan'), '999999999999999999.123456');
  assert.equal(col(5, 'Tong thanh toan'), '0.000000');
  assert.equal(col(2, 'Trang thai'), ''); // nguồn ghi ô trống, không tự xác nhận thuế hợp lệ
  assert.equal(JSON.stringify(input), before);
  assert.equal(s.calls.launch, 0);
});

test('Excel thiếu tổng/trùng tổng nguồn → ô trống, không suy ra 0 hoặc tổng dòng', async () => {
  const s = loadSource();
  await s.exporter.xuatBangKe([fixtures.missing, fixtures.duplicate], 'DEMO', 'missing.xlsx');
  const wb = new ExcelJS.Workbook();
  await wb.xlsx.load(s.files.get('missing.xlsx'));
  assert.equal(wb.worksheets[0].getRow(2).getCell(12).value, '');
  assert.equal(wb.worksheets[0].getRow(3).getCell(13).value, '');
});

test('Excel không gọi parser hiển thị hoặc PDF', async () => {
  const s = loadSource();
  s.source.parseInvoiceXml = () => assert.fail('Không được dùng parser hiển thị cho bảng kê');
  s.source.createPdfRenderer = () => assert.fail('Không được mở browser');
  await s.exporter.xuatBangKe([fixtures.demo], 'DEMO', 'strict.xlsx');
});

test('từ chối XML hỏng/profile lạ/API record/parser hiển thị trước I/O', async () => {
  const s = loadSource();
  for (const invalid of [fixtures.bad, fixtures.unknown, { shdon: '000001' }, s.source.parseInvoiceXml(raws.demo), fixtures.demo.hoa_don]) {
    await assert.rejects(s.exporter.xuatBangKe([fixtures.demo, invalid], 'DEMO', 'bad.xlsx'), hasCode('BANG_KE_STRICT_REQUIRED'));
  }
  assert.equal(s.files.size, 0);
});

test('XML DEMO qua HD-1 thật: Excel giữ decimal nguồn ngoài miền tiền chuẩn 18/6', async () => {
  const s = loadSource();
  const cases = [['sourceBig', '1000000000000000000'], ['sourceScale', '0.1234567']];
  const input = cases.map(([name, text]) => {
    const kq = fixtures[name];
    const total = kq.hoa_don.tong_tien.find(t => t.ma === 'thanh_toan');
    assert.equal(total.gia_tri_nguon.trang_thai, 'PRECISION_UNDECLARED');
    assert.equal(total.gia_tri_nguon.gia_tri, text);
    assert.equal(total.tien_chuan, null);
    assert.equal(adapter.chieuBanGhi(kq).tgtttbso, text);
    return kq;
  });
  const before = JSON.stringify(input);
  await s.exporter.xuatBangKe(input, 'DEMO', 'source-decimal.xlsx');
  const wb = new ExcelJS.Workbook();
  await wb.xlsx.load(s.files.get('source-decimal.xlsx'));
  const ws = wb.getWorksheet('DEMO');
  assert.equal(ws.actualRowCount - 1, cases.length);
  cases.forEach(([, text], i) => {
    const cell = ws.getRow(i + 2).getCell(13);
    assert.equal(cell.type, ExcelJS.ValueType.String);
    assert.equal(cell.value, text);
  });
  assert.equal(JSON.stringify(input), before);
  assert.equal(s.calls.launch, 0);
});

test('không nhận tiền Number hoặc sai miền decimal nguồn/duplicate trong payload', () => {
  for (const value of [110.011, 1000000000000000000, 0.1234567, '1e3', '+1', '1,23', '.1', '1.', '', ' 1', '1 ', '1\n', 'NaN', 'Infinity']) {
    const changed = structuredClone(fixtures.demo);
    changed.hoa_don.tong_tien.find(t => t.ma === 'thanh_toan').gia_tri_nguon.gia_tri = value;
    assert.throws(() => adapter.chieuBanGhi(changed), hasCode('BANG_KE_MONEY_INVALID'));
  }
  const duplicate = structuredClone(fixtures.demo);
  duplicate.hoa_don.tong_tien.push(duplicate.hoa_don.tong_tien[0]);
  assert.throws(() => adapter.chieuBanGhi(duplicate), hasCode('BANG_KE_TOTAL_DUPLICATE'));
});

test('PDF nguồn với Chromium giả: số dòng/ID/tiền khớp strict', async () => {
  const s = loadSource();
  const result = await s.exporter.xuatPdf(fixtures.demo, Buffer.from(raws.demo));
  assert.equal(result.toString(), 'DEMO_PDF_TRANSPORT');
  const html = s.html[0];
  const body = html.match(/<tbody>([\s\S]*?)<\/tbody>/)[1];
  assert.equal((body.match(/<tr>/g) || []).length, fixtures.demo.hoa_don.dong.length);
  assert.ok(html.includes('So: 000001'));
  assert.ok(body.includes('100,01'));
  assert.ok(html.includes('110,011'));
  assert.deepEqual(s.calls, { launch: 1, close: 1, pdf: 1 });
});

test('PDF âm và 0 tường minh vẫn giữ giá trị', async () => {
  const s = loadSource();
  await s.exporter.xuatPdf(fixtures.second, Buffer.from(raws.second));
  await s.exporter.xuatPdf(fixtures.zero, Buffer.from(raws.zero));
  assert.ok(s.html[0].includes('-12,34'));
  assert.match(s.html[1], /Tong thanh toan:<\/td><td class="r amount">0 /);
});

test('PDF từ chối XML lệch hash/độ dài trước parser/browser', async () => {
  const s = loadSource();
  s.source.parseInvoiceXml = () => assert.fail('Chưa được parse XML lệch binding');
  for (const raw of [Buffer.from(raws.second), Buffer.from(raws.demo + ' '), raws.demo]) {
    await assert.rejects(s.exporter.xuatPdf(fixtures.demo, raw), hasCode('BANG_KE_XML_MISMATCH'));
  }
  assert.equal(s.calls.launch, 0);
});

test('PDF thiếu/trùng tiền/Decimal bị Number hoặc Intl làm mất chính xác → từ chối', async () => {
  const s = loadSource();
  for (const name of ['big', 'missing', 'duplicate', 'fraction']) {
    await assert.rejects(s.exporter.xuatPdf(fixtures[name], Buffer.from(raws[name])), hasCode('BANG_KE_PDF_MONEY_LOSS'));
  }
  assert.equal(s.calls.launch, 0);
});

test('parser hiển thị sai số dòng hoặc tổng không thể thay kết quả strict', async () => {
  for (const mutate of [info => info.items.pop(), info => { info.tgtttbso = 999; }]) {
    const s = loadSource();
    const parse = s.source.parseInvoiceXml;
    s.source.parseInvoiceXml = raw => { const info = parse(raw); mutate(info); return info; };
    await assert.rejects(s.exporter.xuatPdf(fixtures.demo, Buffer.from(raws.demo)), e => /^BANG_KE_PDF_/.test(e.code));
    assert.equal(s.calls.launch, 0);
  }
});

test('render PDF lỗi vẫn đóng renderer', async () => {
  const s = loadSource({ failPdf: true });
  await assert.rejects(s.exporter.xuatPdf(fixtures.demo, Buffer.from(raws.demo)), /DEMO_PDF_FAILED/);
  assert.equal(s.calls.close, 1);
});

test('tham số xuất không hợp lệ không ghi bảng kê', async () => {
  const s = loadSource();
  await assert.rejects(s.exporter.xuatBangKe(null, 'DEMO', 'demo.xlsx'), hasCode('BANG_KE_ARGUMENT_INVALID'));
  await assert.rejects(s.exporter.xuatBangKe([], '', 'demo.xlsx'), hasCode('BANG_KE_ARGUMENT_INVALID'));
  assert.equal(s.files.size, 0);
});
