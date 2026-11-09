'use strict';

const ExcelJS = require('exceljs');
const { XMLParser } = require('fast-xml-parser');
const { chromium } = require('playwright');
const cfg = require('./config');

/* ============================================================
 *  BANG KE EXCEL
 * ============================================================ */

/**
 * Xuat bang ke danh sach hoa don ra file .xlsx
 * @param {Array<object>} records  danh sach ban ghi tu API
 * @param {string} sheetTitle      ten sheet (vd "Mua vao 09-2026")
 * @param {string} outPath         duong dan file .xlsx
 */
async function buildExcel(records, sheetTitle, outPath) {
  const wb = new ExcelJS.Workbook();
  wb.creator = 'hoadon-downloader';
  const ws = wb.addWorksheet(sheetTitle.slice(0, 31)); // Excel gioi han 31 ky tu

  const cols = cfg.EXCEL_COLUMNS;
  ws.columns = cols.map(([key, header]) => ({
    header,
    key,
    width: guessWidth(key, header),
  }));

  // Dinh dang dong tieu de
  ws.getRow(1).font = { bold: true };
  ws.getRow(1).alignment = { vertical: 'middle', horizontal: 'center', wrapText: true };
  ws.getRow(1).fill = {
    type: 'pattern',
    pattern: 'solid',
    fgColor: { argb: 'FFDCE6F1' },
  };

  records.forEach((rec, idx) => {
    const row = {};
    for (const [key] of cols) {
      if (key === '_stt') {
        row[key] = idx + 1;
      } else if (key === 'tdlap') {
        row[key] = formatDate(rec[key]);
      } else {
        row[key] = rec[key] !== undefined && rec[key] !== null ? rec[key] : '';
      }
    }
    const added = ws.addRow(row);
    // Dinh dang cot tien
    for (const mf of cfg.MONEY_FIELDS) {
      const cell = added.getCell(mf);
      if (typeof cell.value === 'number') cell.numFmt = '#,##0';
    }
  });

  ws.autoFilter = {
    from: { row: 1, column: 1 },
    to: { row: 1, column: cols.length },
  };
  ws.views = [{ state: 'frozen', ySplit: 1 }];

  await wb.xlsx.writeFile(outPath);
  return outPath;
}

function guessWidth(key, header) {
  if (key === '_stt') return 6;
  if (key === 'nbten' || key === 'nmten') return 34;
  if (cfg.MONEY_FIELDS.includes(key)) return 16;
  if (key === 'tdlap') return 12;
  return Math.max(12, header.length + 2);
}

/* ============================================================
 *  PDF - render tu noi dung XML hoa don
 * ============================================================ */

const xmlParser = new XMLParser({
  ignoreAttributes: false,
  attributeNamePrefix: '@_',
  // Giu nguyen chuoi (khong ep kieu so) de bao toan so 0 dau cua MST, so hoa don...
  parseTagValue: false,
  trimValues: true,
});

/**
 * Tao mot "may render PDF" dung chung (headless chromium) de tai su dung.
 * page.pdf() chi chay o che do headless nen ta dung 1 trinh duyet rieng.
 */
async function createPdfRenderer() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  return {
    async render(xmlString) {
      const info = parseInvoiceXml(xmlString);
      const html = invoiceHtml(info);
      await page.setContent(html, { waitUntil: 'load' });
      return page.pdf({
        format: 'A4',
        printBackground: true,
        margin: { top: '12mm', bottom: '12mm', left: '12mm', right: '12mm' },
      });
    },
    async close() {
      await browser.close().catch(() => {});
    },
  };
}

/** Doc XML hoa don -> object chuan hoa (best-effort, chiu duoc nhieu bien the). */
function parseInvoiceXml(xmlString) {
  let obj = {};
  try {
    obj = xmlParser.parse(xmlString);
  } catch (_) {
    return { raw: xmlString };
  }

  const seller = findFirst(obj, ['NBan']) || {};
  const buyer = findFirst(obj, ['NMua']) || {};

  const info = {
    thdon: text(findFirst(obj, ['THDon'])),
    khmshdon: text(findFirst(obj, ['KHMSHDon'])),
    khhdon: text(findFirst(obj, ['KHHDon'])),
    shdon: text(findFirst(obj, ['SHDon'])),
    nlap: text(findFirst(obj, ['NLap'])),
    dvtte: text(findFirst(obj, ['DVTTe'])) || '',
    seller: {
      ten: text(findFirst(seller, ['Ten'])),
      mst: text(findFirst(seller, ['MST'])),
      dchi: text(findFirst(seller, ['DChi'])),
    },
    buyer: {
      // To chuc: ten o <Ten>. Ca nhan: <Ten> trong, ten o <HVTNMHang>.
      ten: text(findFirst(buyer, ['Ten'])) || text(findFirst(buyer, ['HVTNMHang'])),
      mst: text(findFirst(buyer, ['MST'])),
      // Ca nhan khong co MST, thay bang so CCCD/giay to
      cccd: text(findFirst(buyer, ['CCCDan', 'CCCD'])),
      dchi: text(findFirst(buyer, ['DChi'])),
    },
    items: extractItems(obj),
    tgtcthue: num(findFirst(obj, ['TgTCThue'])),
    tgtthue: num(findFirst(obj, ['TgTThue'])),
    tgtttbso: num(findFirst(obj, ['TgTTTBSo'])),
    tgtttbchu: text(findFirst(obj, ['TgTTTBChu'])),
  };
  return info;
}

function extractItems(obj) {
  let list = findFirst(obj, ['HHDVu']);
  if (!list) return [];
  if (!Array.isArray(list)) list = [list];
  return list.map((it) => ({
    stt: text(findFirst(it, ['STT'])),
    ten: text(findFirst(it, ['THHDVu'])),
    dvt: text(findFirst(it, ['DVTinh'])),
    sluong: text(findFirst(it, ['SLuong'])),
    dgia: num(findFirst(it, ['DGia'])),
    tsuat: text(findFirst(it, ['TSuat'])),
    thtien: num(findFirst(it, ['ThTien'])),
  }));
}

/** Tim gia tri dau tien theo ten tag (khong phan biet hoa thuong), de quy. */
function findFirst(node, names) {
  const wanted = names.map((n) => n.toLowerCase());
  let found;
  (function walk(n) {
    if (found !== undefined || n === null || typeof n !== 'object') return;
    for (const key of Object.keys(n)) {
      if (wanted.includes(key.toLowerCase())) {
        found = n[key];
        return;
      }
    }
    for (const key of Object.keys(n)) {
      walk(n[key]);
      if (found !== undefined) return;
    }
  })(node);
  return found;
}

function text(v) {
  if (v === undefined || v === null) return '';
  if (typeof v === 'object') return '';
  return String(v);
}
function num(v) {
  const n = Number(text(v).replace(/,/g, ''));
  return Number.isFinite(n) ? n : 0;
}

const nf = new Intl.NumberFormat('vi-VN');
function money(n) {
  return nf.format(Number(n) || 0);
}
function esc(s) {
  return String(s === undefined || s === null ? '' : s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

/** Sinh HTML hoa don de in ra PDF. */
function invoiceHtml(info) {
  if (info.raw) {
    return `<!doctype html><html><head><meta charset="utf-8"></head>
      <body style="font-family:Arial,'DejaVu Sans',sans-serif;padding:16px;">
      <p style="color:#b00">Khong doc duoc cau truc XML - hien thi noi dung tho:</p>
      <pre style="white-space:pre-wrap;font-size:10px;">${esc(info.raw).slice(0, 20000)}</pre>
      </body></html>`;
  }

  const rows =
    info.items && info.items.length
      ? info.items
          .map(
            (it, i) => `<tr>
        <td style="text-align:center">${esc(it.stt || i + 1)}</td>
        <td>${esc(it.ten)}</td>
        <td style="text-align:center">${esc(it.dvt)}</td>
        <td style="text-align:right">${esc(it.sluong)}</td>
        <td style="text-align:right">${money(it.dgia)}</td>
        <td style="text-align:center">${esc(it.tsuat)}</td>
        <td style="text-align:right">${money(it.thtien)}</td>
      </tr>`
          )
          .join('')
      : `<tr><td colspan="7" style="text-align:center;color:#888">(Khong co dong hang hoa/dich vu)</td></tr>`;

  const cur = info.dvtte || '';

  return `<!doctype html>
<html lang="vi"><head><meta charset="utf-8">
<style>
  * { box-sizing: border-box; }
  body { font-family: Arial, 'DejaVu Sans', sans-serif; font-size: 12px; color:#111; }
  h1 { font-size: 18px; text-align:center; margin: 0 0 4px; }
  .sub { text-align:center; color:#444; margin-bottom: 12px; }
  .meta td { padding: 2px 4px; vertical-align: top; }
  .party { border:1px solid #ccc; padding:8px; margin:8px 0; border-radius:4px; }
  .label { color:#666; }
  table.items { width:100%; border-collapse: collapse; margin-top:8px; }
  table.items th, table.items td { border:1px solid #999; padding:4px 6px; font-size:11px; }
  table.items th { background:#f0f4fa; }
  .totals { margin-top:8px; width:100%; }
  .totals td { padding:3px 4px; }
  .totals .r { text-align:right; }
  .amount { font-weight:bold; }
  .note { margin-top:6px; font-style: italic; }
  .cur { color:#666; font-weight:normal; }
</style></head>
<body>
  <h1>${esc(info.thdon || 'HOA DON DIEN TU')}</h1>
  <div class="sub">
    Ky hieu: ${esc(info.khmshdon)}${esc(info.khhdon)} &nbsp;|&nbsp;
    So: ${esc(info.shdon)} &nbsp;|&nbsp;
    Ngay lap: ${esc(info.nlap)}
    ${cur ? `&nbsp;|&nbsp; Don vi tien te: <b>${esc(cur)}</b>` : ''}
  </div>

  <div class="party">
    <div><span class="label">Nguoi ban:</span> <b>${esc(info.seller.ten)}</b></div>
    <div><span class="label">MST:</span> ${esc(info.seller.mst)}</div>
    <div><span class="label">Dia chi:</span> ${esc(info.seller.dchi)}</div>
  </div>
  <div class="party">
    <div><span class="label">Nguoi mua:</span> <b>${esc(info.buyer.ten)}</b></div>
    <div><span class="label">${info.buyer.mst ? 'MST' : (info.buyer.cccd ? 'CCCD/Giay to' : 'MST')}:</span> ${esc(info.buyer.mst || info.buyer.cccd)}</div>
    <div><span class="label">Dia chi:</span> ${esc(info.buyer.dchi)}</div>
  </div>

  <table class="items">
    <thead><tr>
      <th style="width:32px">STT</th>
      <th>Ten hang hoa, dich vu</th>
      <th style="width:50px">DVT</th>
      <th style="width:60px">So luong</th>
      <th style="width:90px">Don gia</th>
      <th style="width:50px">Thue suat</th>
      <th style="width:100px">Thanh tien</th>
    </tr></thead>
    <tbody>${rows}</tbody>
  </table>

  <table class="totals">
    <tr><td class="r label">Cong tien hang (chua thue):</td><td class="r amount">${money(info.tgtcthue)} <span class="cur">${esc(cur)}</span></td></tr>
    <tr><td class="r label">Tien thue GTGT:</td><td class="r amount">${money(info.tgtthue)} <span class="cur">${esc(cur)}</span></td></tr>
    <tr><td class="r label">Tong thanh toan:</td><td class="r amount">${money(info.tgtttbso)} <span class="cur">${esc(cur)}</span></td></tr>
  </table>
  ${info.tgtttbchu ? `<div class="note">Bang chu: ${esc(info.tgtttbchu)}</div>` : ''}

  <div class="note" style="color:#888;margin-top:14px;font-size:10px;">
    * Ban PDF nay duoc dung lai tu du lieu XML goc de tien tra soat. File XML goc moi la ban co gia tri phap ly de luu tru/ke khai.
  </div>
</body></html>`;
}

module.exports = {
  buildExcel,
  createPdfRenderer,
  parseInvoiceXml,
  formatDate,
};

/* ---- helper dung chung ---- */
function formatDate(v) {
  if (v === undefined || v === null || v === '') return '';
  // So (epoch ms)
  if (typeof v === 'number') {
    const d = new Date(v);
    if (!isNaN(d)) return pad(d);
  }
  const s = String(v);
  // ISO hoac yyyy-MM-dd...
  const d = new Date(s);
  if (!isNaN(d) && /\d{4}-\d{2}-\d{2}/.test(s)) return pad(d);
  return s; // giu nguyen neu khong parse duoc
}
function pad(d) {
  const dd = String(d.getDate()).padStart(2, '0');
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  return `${dd}/${mm}/${d.getFullYear()}`;
}
