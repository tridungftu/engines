'use strict';

// G3-GOI-25: node engines/e_hoa_don/tests/nguon.cjs.
// Closure ở vị trí giả trong RAM; mọi thư viện ngoài đều mock, không mạng/browser.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { createHash } = require('node:crypto');

const GOI = path.resolve(__dirname, '..');
const CHUYEN_DEN = path.resolve('DEMO_GOI_DI_CHUYEN', 'e_hoa_don');
const TEP_MA = ['bang_ke.cjs', 'portal.cjs', 'vendor/build.js', 'vendor/config.js'];
const GHIM = { exceljs: '4.4.0', 'fast-xml-parser': '4.5.7', playwright: '1.62.1' };
const sha = raw => createHash('sha256').update(raw).digest('hex');
const doc = ten => fs.readFileSync(path.join(GOI, ten));

function goiTrongRam({ sua = null, crlf = false } = {}) {
  const files = new Map(TEP_MA.map(ten => {
    let text = doc(ten).toString('utf8');
    if (crlf) text = text.replace(/\r\n/g, '\n').replace(/\n/g, '\r\n');
    if (ten === sua) text += '\n// DEMO: nguồn bị thay đổi\n';
    return [path.join(CHUYEN_DEN, ten), Buffer.from(text)];
  }));
  const cache = new Map();
  const daDoc = [];
  const daNap = [];
  const sheets = [];
  let moBrowser = 0;
  class Workbook {
    constructor() {
      this.xlsx = { writeFile: async name => { this.out = name; } };
    }
    addWorksheet(title) {
      const sheet = { title, rows: [], getRow: () => ({}),
        addRow(row) { this.rows.push(row); return { getCell: key => ({ value: row[key] }) }; } };
      sheets.push(sheet);
      return sheet;
    }
  }
  class XMLParser {
    parse() { throw new Error('Không dùng parser hiển thị trong ca bảng kê'); }
  }
  const ngoai = {
    exceljs: { Workbook },
    'fast-xml-parser': { XMLParser },
    playwright: { chromium: { launch() { moBrowser++; throw new Error('Không mở Chromium'); } } },
  };
  function read(file) {
    assert.ok(files.has(file), `Đọc ngoài closure: ${file}`);
    daDoc.push(file);
    return files.get(file);
  }
  function load(file) {
    if (cache.has(file)) return cache.get(file).exports;
    const module = { exports: {} };
    cache.set(file, module);
    function requireTrongGoi(spec) {
      daNap.push(spec);
      if (spec === 'node:fs') return { readFileSync: read };
      if (['node:path', 'node:crypto', 'node:util'].includes(spec)) return require(spec);
      if (Object.hasOwn(ngoai, spec)) return ngoai[spec];
      assert.ok(spec.startsWith('.') || path.isAbsolute(spec), `Nạp ngoài closure: ${spec}`);
      let target = path.resolve(path.dirname(file), spec);
      if (!path.extname(target)) target += '.js';
      assert.ok(files.has(target), `Phụ thuộc không đóng gói: ${spec}`);
      return load(target);
    }
    const code = read(file).toString('utf8');
    vm.runInNewContext('(function(require,module,exports,__filename,__dirname){\n' + code + '\n})',
      { Buffer }, { filename: file, timeout: 2000 })(
      requireTrongGoi, module, module.exports, file, path.dirname(file));
    return module.exports;
  }
  return { load: ten => load(path.join(CHUYEN_DEN, ten)), daDoc, daNap, sheets,
    get moBrowser() { return moBrowser; } };
}

test('gói chuyển vị trí nạp sạch với thư viện mock, chỉ đọc nguồn trong gói', () => {
  const ram = goiTrongRam();
  const adapter = ram.load('bang_ke.cjs');
  assert.equal(adapter.NGUON, path.join(CHUYEN_DEN, 'vendor/build.js'));
  assert.deepEqual(ram.daNap, ['node:fs', 'node:path', 'node:crypto']);
  const source = adapter.napNguon();
  for (const name of ['buildExcel', 'parseInvoiceXml', 'createPdfRenderer']) {
    assert.equal(typeof source[name], 'function');
  }
  assert.equal(ram.load('portal.cjs').NGUON_THAT.trang_thai, 'CHUA_KIEM');
  assert.equal(ram.moBrowser, 0);
  assert.ok(ram.daDoc.every(file => file.startsWith(CHUYEN_DEN + path.sep)));
  assert.ok(!ram.daNap.some(spec => /job|server|dotenv|portal\.js|^[A-Za-z]:/.test(spec)
    && !spec.startsWith(CHUYEN_DEN + path.sep)));
});

test('bảng kê dùng build đóng gói giữ số 0 đầu, Decimal và ngày dd/mm/yyyy', async () => {
  const ram = goiTrongRam();
  const source = ram.load('bang_ke.cjs').napNguon();
  const input = [{ shdon: '0000123', tdlap: '2026-11-06', tgtcthue: '100.010000',
    tgtthue: null, tgtttbso: '999999999999999999.123456' }];
  const before = JSON.stringify(input);
  assert.equal(await source.buildExcel(input, 'Bảng kê DEMO', 'DEMO.xlsx'), 'DEMO.xlsx');
  const row = ram.sheets[0].rows[0];
  assert.equal(row.shdon, '0000123');
  assert.equal(row.tdlap, '06/11/2026');
  assert.equal(row.tgtcthue, '100.010000');
  assert.equal(row.tgtthue, '');
  assert.equal(row.tgtttbso, '999999999999999999.123456');
  assert.equal(JSON.stringify(input), before);
  assert.equal(ram.moBrowser, 0);
});

for (const file of ['vendor/build.js', 'vendor/config.js']) {
  test(`SHA lệch ở ${file} bị chặn trước khi nạp thư viện`, () => {
    const ram = goiTrongRam({ sua: file });
    assert.throws(() => ram.load('bang_ke.cjs').napNguon(),
      error => error.code === 'BANG_KE_SOURCE_CHANGED');
    assert.ok(!ram.daNap.some(spec => Object.hasOwn(GHIM, spec)));
  });
}

test('bản checkout CRLF vẫn phải khớp đúng các SHA đã ghim', () => {
  const ram = goiTrongRam({ crlf: true });
  assert.equal(typeof ram.load('bang_ke.cjs').napNguon().buildExcel, 'function');
});

test('NGUON ghi đúng quyền dùng và mã băm từng tệp nguồn/metadata đã đóng gói', () => {
  const text = doc('NGUON.md').toString('utf8');
  assert.ok(text.includes('phần mềm nội bộ, Anh xác nhận 06/11/2026, chỉ dùng nội bộ'));
  assert.ok(text.includes('D:\\Claude\\Phan mem download hoa don'));
  assert.ok(text.includes('hoadon-downloader 1.0.0'));
  for (const file of ['vendor/build.js', 'vendor/config.js', 'package.json', 'package-lock.json']) {
    const row = text.split(/\r?\n/).find(line => line.startsWith(`| \`${file}\` |`));
    assert.ok(row, `Thiếu nguồn/mã băm: ${file}`);
    assert.ok(row.includes(sha(doc(file))), `SHA không khớp NGUON.md: ${file}`);
    const lf = doc(file).toString('utf8').replace(/\r\n/g, '\n');
    assert.ok(row.includes(sha(lf)));
    assert.ok(row.includes(sha(lf.replace(/\n/g, '\r\n'))));
  }
});

test('bản chép chỉ đổi require config, giữ nguyên thuật toán và config nguồn', () => {
  const source = doc('vendor/build.js').toString('utf8').replace(/\r\n/g, '\n')
    .replace("require('./config')", "require('../config')");
  assert.equal(sha(source), 'ca7fe35cafe7c802d5ebe7506db9fd7a1294552d833569306f03b1a03976f209');
  assert.equal(sha(doc('vendor/config.js').toString('utf8').replace(/\r\n/g, '\n')),
    '48cb8cb1b0253cd4a5110f1628150053a0372a00b3503f359a01849281f90b02');
});

test('lock chỉ giữ closure ba thư viện đã ghim, đủ dependency và integrity', () => {
  const pkg = JSON.parse(doc('package.json'));
  const lock = JSON.parse(doc('package-lock.json'));
  assert.deepEqual(pkg.dependencies, GHIM);
  assert.equal(pkg.private, true);
  assert.equal(pkg.scripts, undefined);
  assert.equal(lock.lockfileVersion, 3);
  assert.equal(lock.name, pkg.name);
  assert.equal(lock.version, pkg.version);
  assert.deepEqual(lock.packages[''].dependencies, pkg.dependencies);
  const seen = new Set();
  function visit(from, name) {
    let current = from;
    let key;
    while (true) {
      key = (current ? current + '/' : '') + 'node_modules/' + name;
      if (lock.packages[key]) break;
      assert.ok(current, `Thiếu lock: ${from} -> ${name}`);
      const at = current.lastIndexOf('/node_modules/');
      current = at < 0 ? '' : current.slice(0, at);
    }
    if (seen.has(key)) return;
    seen.add(key);
    const item = lock.packages[key];
    assert.match(item.resolved, /^https:\/\/registry\.npmjs\.org\//);
    assert.match(item.integrity, /^sha512-[A-Za-z0-9+/]+=*$/);
    assert.equal(item.peerDependencies, undefined);
    for (const child of Object.keys({ ...item.dependencies, ...item.optionalDependencies })) visit(key, child);
  }
  for (const [name, version] of Object.entries(GHIM)) {
    assert.equal(lock.packages['node_modules/' + name].version, version);
    visit('', name);
  }
  assert.deepEqual([...seen].sort(), Object.keys(lock.packages).filter(key => key).sort());
  for (const name of ['dotenv', 'express', 'adm-zip']) {
    assert.equal(lock.packages['node_modules/' + name], undefined);
  }
});
