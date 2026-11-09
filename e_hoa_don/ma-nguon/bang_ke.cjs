'use strict';

/** HD-2b / G3-GOI-25 — bọc build.js nội bộ, hoadon-downloader 1.0.0.
 * Nguồn, quyền dùng và SHA-256 gốc/bản chép: NGUON.md cạnh tệp này.
 * Bản chép chỉ đổi đường require config; không đổi thuật toán.
 * Đầu vào nội bộ: ra_json(KetQuaDocHoaDon) của doc.py HD-1; không nhận
 * bản ghi API/parser hiển thị. Đây không phải contract báo cáo ZIP mới.
 * Excel: một dòng/hóa đơn, tiền là text exact; không cộng lại tổng nguồn.
 * PDF: chỉ dùng parser nguồn để đối chiếu khả năng HIỂN THỊ sau strict;
 * không dùng kết quả ấy làm dữ liệu nghiệp vụ. Thiếu/mất chính xác → lỗi.
 * Chromium do caller/Core quản lý; test thuần tiêm nguồn với Chromium giả.
 */
const fs = require('node:fs');
const path = require('node:path');
const { createHash } = require('node:crypto');

const NGUON = path.join(__dirname, 'vendor', 'build.js');
const SHA256_NGUON = '5664548e0f08936e6b15536dc4ec23bd55a04417d6c66ef439362415a16ab3d5';
// Git trên Windows có thể checkout CRLF: chỉ chấp nhận hai bộ bytes đã ghim.
const SHA256_NGUON_CRLF = '6e7b23e937b40740817b94e629647f8080e089cf66f57cca9561ea9a0d9ab614';
const SHA256_CONFIG = '48cb8cb1b0253cd4a5110f1628150053a0372a00b3503f359a01849281f90b02';
const SHA256_CONFIG_CRLF = '35c86b295812793e98dd0ed65b3b34f247b1b67cb318e0e2d7fded0f1a57c3df';
// Cùng miền decimal nguồn của HD-1; kết thúc tuyệt đối như Python fullmatch.
const DECIMAL_NGUON = /^-?[0-9]+(?:\.[0-9]+)?(?![\s\S])/;
const TONG = { tgtcthue: 'truoc_thue', tgtthue: 'thue', tgtttbso: 'thanh_toan' };
const DAU = {
  khmshdon: 'mau_so', khhdon: 'ky_hieu', shdon: 'so_hoa_don',
  tdlap: 'ngay_lap', nbmst: 'ma_so_thue_ban', nmmst: 'ma_so_thue_mua', dvtte: 'don_vi_tien',
};

function loi(code, message) {
  throw Object.assign(new Error(message), { code });
}

function napNguon() {
  for (const [file, hashes] of [
    [NGUON, [SHA256_NGUON, SHA256_NGUON_CRLF]],
    [path.join(__dirname, 'vendor', 'config.js'), [SHA256_CONFIG, SHA256_CONFIG_CRLF]],
  ]) {
    if (!hashes.includes(createHash('sha256').update(fs.readFileSync(file)).digest('hex'))) {
      loi('BANG_KE_SOURCE_CHANGED', 'Nguồn xuất bảng kê khác bản đã kiểm; cần kiểm tra lại gói.');
    }
  }
  // Chỉ nạp build/config; không nạp job, portal, server hay .env.
  return require(NGUON);
}

function kiemKetQua(kq) {
  const h = kq?.hoa_don;
  const ct = kq?.chi_tiet_nguon;
  if (!h || h.contract !== 'hoa_don.v1' || h.phien_ban !== '1.0.0'
      || !['XONG', 'CHO'].includes(kq.trang_thai)
      || h.dang_cau_truc !== 'SUPPORTED_SUBSET' || ct?.shape !== 'SUPPORTED_SUBSET'
      || !h.dau_hoa_don || !Array.isArray(h.dong) || !Array.isArray(h.tong_tien)
      || !Array.isArray(ct.lines) || h.dong.length !== ct.lines.length
      || !/^[a-f0-9]{64}$/.test(ct.raw_ref?.native_sha256 ?? '')
      || !Number.isSafeInteger(ct.raw_ref?.byte_length)) {
    loi('BANG_KE_STRICT_REQUIRED', 'Cần kết quả HD-1 strict đọc được, kèm chi tiết nguồn.');
  }
  return h;
}

function chieuBanGhi(kq) {
  const h = kiemKetQua(kq);
  const rec = {};
  for (const [key, field] of Object.entries(DAU)) {
    const value = h.dau_hoa_don[field];
    if (value !== null && typeof value !== 'string') {
      loi('BANG_KE_FIELD_INVALID', `Field ${field} phải là text/null từ strict.`);
    }
    rec[key] = value;
  }
  for (const [key, code] of Object.entries(TONG)) {
    const matches = h.tong_tien.filter(t => t.ma === code);
    if (matches.length > 1) loi('BANG_KE_TOTAL_DUPLICATE', `Trùng tổng ${code}.`);
    const total = matches[0];
    const text = total?.gia_tri_nguon?.gia_tri;
    if (text != null && (typeof text !== 'string' || !DECIMAL_NGUON.test(text))) {
      loi('BANG_KE_MONEY_INVALID', `Tiền ${code} ngoài miền contract; không làm tròn.`);
    }
    // Decimal nguồn không bị giới hạn 18/6 của tien_chuan, kể cả PRECISION_UNDECLARED.
    // Không thay null bằng 0, không lấy số chuẩn hóa hoặc cộng từ dòng hàng.
    rec[key] = text ?? null;
  }
  // Tên/CCCD/trạng thái thuế không thuộc đầu hóa đơn strict: để nguồn xuất ô trống.
  return rec;
}

function textField(fields, name) {
  const matches = fields?.filter(f => f.name === name);
  const f = matches?.length === 1 ? matches[0] : null;
  const v = f?.occurrences?.length === 1 && !f.mixed_content ? f.occurrences[0] : null;
  if (v?.state === 'TEXT') return v.lexeme;
  if (v?.state === 'EMPTY' || v?.state === 'ABSENT') return '';
  loi('BANG_KE_PDF_AMBIGUOUS', `PDF không thể biểu diễn field mơ hồ ${name}.`);
}

function chuanSo(s) {
  if (typeof s !== 'string' || !/^-?[0-9]+(?:\.[0-9]+)?$/.test(s)) return null;
  let [whole, frac = ''] = s.split('.');
  const negative = whole.startsWith('-');
  whole = whole.replace(/^-/, '').replace(/^0+(?=\d)/, '');
  frac = frac.replace(/0+$/, '');
  return `${negative && (whole !== '0' || frac) ? '-' : ''}${whole}${frac ? '.' + frac : ''}`;
}

function kiemSoPdf(actual, exact) {
  const normalized = chuanSo(exact);
  // Number/Intl của nguồn không bảo toàn mọi Decimal; fail trước khi mở browser.
  const printed = new Intl.NumberFormat('vi-VN').format(actual)
    .replace(/\./g, '').replace(',', '.');
  if (normalized === null || typeof actual !== 'number' || !Number.isFinite(actual)
      || chuanSo(String(actual)) !== normalized || chuanSo(printed) !== normalized) {
    loi('BANG_KE_PDF_MONEY_LOSS', 'PDF nguồn thiếu tiền hoặc làm mất chính xác Decimal.');
  }
}

function doiChieuPdf(kq, rawXml, nguon) {
  const h = kiemKetQua(kq);
  const rec = chieuBanGhi(kq);
  const ref = kq.chi_tiet_nguon.raw_ref;
  if (!Buffer.isBuffer(rawXml) || rawXml.length !== ref.byte_length
      || createHash('sha256').update(rawXml).digest('hex') !== ref.native_sha256) {
    loi('BANG_KE_XML_MISMATCH', 'XML PDF không khớp bytes đã đọc strict.');
  }
  const xml = rawXml.toString('utf8');
  const info = nguon.parseInvoiceXml(xml);
  const same = (a, b) => {
    if (a !== b) loi('BANG_KE_PDF_MISMATCH', 'PDF nguồn khác dữ liệu strict.');
  };
  for (const key of ['khmshdon', 'khhdon', 'shdon', 'dvtte']) same(info[key], rec[key] ?? '');
  same(info.nlap, rec.tdlap ?? '');
  same(info.seller?.mst, rec.nbmst ?? '');
  same(info.buyer?.mst, rec.nmmst ?? '');
  for (const key of Object.keys(TONG)) kiemSoPdf(info[key], rec[key]);
  if (!Array.isArray(info.items)) loi('BANG_KE_PDF_MISMATCH', 'PDF nguồn thiếu bảng hàng.');
  same(info.items.length, h.dong.length);
  kq.chi_tiet_nguon.lines.forEach((line, i) => {
    const item = info.items[i];
    for (const [key, tag] of Object.entries({ stt: 'STT', ten: 'THHDVu', dvt: 'DVTinh', sluong: 'SLuong', tsuat: 'TSuat' })) {
      const text = textField(line.fields, tag);
      // Nguồn tự điền STT khi rỗng; không cho PDF âm thầm đổi giá trị nguồn.
      if (key === 'stt' && !text) loi('BANG_KE_PDF_AMBIGUOUS', 'PDF nguồn tự điền STT thiếu.');
      same(item[key], text);
    }
    kiemSoPdf(item.dgia, line.unit_price?.exact_text);
    kiemSoPdf(item.thtien, line.source_amount?.exact_text);
  });
  return xml;
}

function taoBoXuat(nguon = napNguon()) {
  return {
    async xuatBangKe(ketQua, sheetTitle, outPath) {
      if (!Array.isArray(ketQua) || typeof sheetTitle !== 'string' || !sheetTitle
          || typeof outPath !== 'string' || !outPath) {
        loi('BANG_KE_ARGUMENT_INVALID', 'Cần danh sách HD-1, tên sheet và đường dẫn Core cấp.');
      }
      // Kiểm toàn bộ trước I/O; không xuất một phần khi có đầu vào sai.
      const records = ketQua.map(chieuBanGhi);
      return nguon.buildExcel(records, sheetTitle, outPath);
    },
    async xuatPdf(kq, rawXml) {
      const xml = doiChieuPdf(kq, rawXml, nguon);
      const renderer = await nguon.createPdfRenderer();
      try {
        return await renderer.render(xml);
      } finally {
        await renderer.close();
      }
    },
  };
}

module.exports = { NGUON, SHA256_NGUON, napNguon, chieuBanGhi, doiChieuPdf, taoBoXuat };
