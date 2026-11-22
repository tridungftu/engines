import { taoMan as taoManDuyet } from './duyet_dinh_danh.js';

// Metadata của tài nguyên cố định trong gói; test đối chiếu với Python/SHA.
export const tienTo = [
  ['Công ty', 'MASKCT'], ['Cá nhân', 'MASKCN'], ['Địa chỉ', 'MASKDC'],
  ['Mã số thuế', 'MASKMST'], ['Tài khoản', 'MASKTK'], ['Khác', 'MASKKHAC'],
  ['Tạm thời', 'MASKTAM'],
];
export const tuDien = [
  ['Họ người Việt', 'vn_surnames.txt', 'Nhận diện ứng viên tên người.'],
  ['Địa danh Việt Nam', 'vn_places.txt', 'Đối chiếu địa danh khi nhận diện.'],
  ['Chữ viết tắt thông dụng', 'common_acronyms.txt', 'Giảm nhận diện nhầm chữ viết tắt.'],
  ['Cụm từ được phép còn lại', 'leftover_allowlist.txt', 'Đối chiếu khi kiểm tra nội dung còn sót.'],
];

export function taoMan({ KttCore, goc, document = globalThis.document }) {
  const engine = KttCore.engine('e_mask');
  const tao = (ten, chu = '', lop = '') => {
    const e = document.createElement(ten); e.textContent = chu;
    if (lop) e.className = lop;
    return e;
  };
  const noi = tao('section', '', 'mask-ui');
  // CSS đi cùng module, không phụ thuộc stylesheet của trang chủ.
  const css = tao('link'); css.rel = 'stylesheet';
  css.href = new URL('./cau_hinh.css', import.meta.url).href;
  noi.append(css, tao('h1', 'Che định danh'),
    tao('p', 'Cấu hình thời hạn mở che và xem bộ nhận diện trong gói.', 'mask-mo-ta'));
  goc.append(noi);
  function the(bieuTuong, ten, trangThai, lop = '') {
    const the = tao('section', '', `mask-the ${lop}`);
    const dau = tao('header', '', 'mask-dau');
    const tieuDe = tao('h2'); tieuDe.append(tao('span', bieuTuong, 'mask-bieu-tuong'), tao('span', ten));
    const nhan = tao('span', trangThai, 'mask-nhan');
    dau.append(tieuDe, nhan);
    const than = tao('div', '', 'mask-than'); the.append(dau, than); noi.append(the);
    return { the, than, nhan };
  }
  const ch = the('◷', 'Thời hạn ánh xạ', 'Chưa tải');
  const form = tao('form', '', 'mask-luoi');
  const cot = tao('div'); const nhan = tao('label', 'Thời hạn ánh xạ trong RAM (giây)');
  const o = tao('input'); o.id = 'mask-thoi-han'; o.type = 'number';
  o.min = '60'; o.max = '900'; o.step = '1'; o.placeholder = '600'; o.required = true;
  nhan.htmlFor = o.id;
  const huongDan = tao('p', 'Nhập số nguyên từ 60 đến 900 giây. Mặc định 600 giây (10 phút).', 'mask-goi-y');
  huongDan.id = 'mask-huong-dan';
  const loiO = tao('p', '', 'mask-loi'); loiO.id = 'mask-loi-thoi-han';
  loiO.setAttribute('aria-live', 'polite');
  o.setAttribute('aria-describedby', `${huongDan.id} ${loiO.id}`);
  cot.append(nhan, o, huongDan, loiO);
  const giaiThich = tao('div', '', 'mask-ghi-chu');
  giaiThich.append(tao('strong', 'Chỉ giữ trong cùng chu kỳ'),
    tao('p', 'Ánh xạ chỉ nằm trong RAM của tiến trình Mask. Hết hạn hoặc mất RAM thì cần chạy lại toàn chuỗi. Truy cập không gia hạn.'),
    tao('p', 'Thay đổi áp dụng cho chuỗi bắt đầu sau khi lưu.'));
  form.append(cot, giaiThich);
  const tac = tao('div', '', 'mask-tac');
  const luu = tao('button', 'Lưu cấu hình', 'mask-chinh'); luu.type = 'submit';
  const taiLai = tao('button', 'Tải lại'); taiLai.type = 'button';
  tac.append(luu, taiLai); form.append(tac); ch.than.append(form);
  const thongBao = tao('p', '', 'mask-thong-bao'); thongBao.setAttribute('role', 'status'); ch.than.append(thongBao);
  const luoi = tao('div', '', 'mask-luoi mask-danh-muc'); noi.append(luoi);
  const tt = the('◇', 'Bộ tiền tố', 'Chỉ đọc');
  const td = the('≡', 'Từ điển nhận diện đang dùng', 'Trong gói');
  // Chuyển hai thẻ vào cùng hàng trên màn rộng.
  luoi.append(tt.the, td.the);
  tt.than.append(tao('p', 'Bộ tiền tố cố định cho bí danh tự sinh. Đối tác có mã Junsky dùng mã đã được duyệt.', 'mask-goi-y'));
  const ds = tao('dl', '', 'mask-tien-to');
  for (const [ten, ma] of tienTo) ds.append(tao('dt', ten), tao('dd', ma));
  tt.than.append(ds);
  td.than.append(tao('p', 'Bốn từ điển sạch đi cùng gói; engine kiểm mã băm khi nạp. Thiếu hoặc sai tài nguyên thì từ chối xử lý.', 'mask-goi-y'));
  const nangCao = tao('details'); nangCao.append(tao('summary', 'Nâng cao · Tên tệp tài nguyên'));
  for (const [ten, tep, moTa] of tuDien) {
    const muc = tao('div', '', 'mask-tu-dien'); muc.append(tao('strong', ten), tao('p', moTa)); td.than.append(muc);
    nangCao.append(tao('p', `${ten}: ${tep}`));
  }
  td.than.append(nangCao);
  const duyet = the('✓', 'Duyệt định danh', 'Chờ Core');
  const canhBao = tao('p', 'Thao tác xem và duyệt cần cửa xác minh của Core. Khi chưa có cửa này, danh sách chỉ hiển thị metadata và chưa thể duyệt.', 'mask-canh-bao');
  duyet.than.append(canhBao);
  const manDuyet = taoManDuyet({ KttCore, goc: duyet.than, document });
  let phien = null, banDoc = {}, dangChay = false, tranhChap = false;
  function khoa() {
    o.disabled = dangChay || phien === null || tranhChap;
    luu.disabled = o.disabled; taiLai.disabled = dangChay;
  }
  function kiem() {
    const dung = /^\d+$/.test(o.value) && Number.isSafeInteger(Number(o.value)) && Number(o.value) >= 60 && Number(o.value) <= 900;
    loiO.textContent = dung ? '' : 'Thời hạn ánh xạ: nhập số nguyên từ 60 đến 900 giây, ví dụ 600.';
    o.setAttribute('aria-invalid', String(!dung)); return dung;
  }
  function docBan(kq) {
    const c = kq?.gia_tri, p = kq?.phien_ban_cau_hinh;
    if (!c || typeof c !== 'object' || Array.isArray(c) ||
        Object.keys(c).some(k => k !== 'thoi_han_anh_xa_giay') ||
        !Number.isSafeInteger(p) || p < 0) throw new Error('ban_doc');
    const giay = Object.hasOwn(c, 'thoi_han_anh_xa_giay') ? c.thoi_han_anh_xa_giay : 600;
    if (!Number.isInteger(giay) || giay < 60 || giay > 900) throw new Error('thoi_han');
    return { c: { ...c }, p, giay };
  }
  async function doc() {
    if (dangChay) return false;
    dangChay = true; khoa();
    try {
      const { c, p, giay } = docBan(await engine.cau_hinh.doc());
      banDoc = c; phien = p; o.value = String(giay); tranhChap = false;
      loiO.textContent = ''; o.setAttribute('aria-invalid', 'false');
      thongBao.textContent = 'Đã tải cấu hình.'; ch.nhan.textContent = 'Đã tải'; return true;
    } catch {
      phien = null; o.value = ''; ch.nhan.textContent = 'Chưa tải được';
      thongBao.textContent = 'Không đọc được cấu hình. Tải lại để thử lại.'; return false;
    } finally { dangChay = false; khoa(); }
  }
  async function ghi() {
    if (dangChay || phien === null || tranhChap || !kiem()) return false;
    dangChay = true; khoa();
    try {
      const giaTri = { ...banDoc, thoi_han_anh_xa_giay: Number(o.value) };
      const kq = await engine.cau_hinh.luu(giaTri, phien);
      // Không tự gửi lại nếu mất ACK. Chỉ chấp nhận phiên mới từ Core.
      const p = kq?.phien_ban_cau_hinh;
      if (!Number.isSafeInteger(p) || p <= phien) throw new Error('xac_nhan');
      banDoc = giaTri; phien = p; ch.nhan.textContent = 'Đã lưu';
      thongBao.textContent = 'Đã lưu cấu hình. Áp dụng cho chuỗi mới.'; return true;
    } catch (loi) {
      const ma = loi?.ma ?? loi?.loi?.ma;
      tranhChap = true; ch.nhan.textContent = 'Cần tải lại';
      thongBao.textContent = ['CAU_HINH_XUNG_DOT', 'NGAN_XUNG_DOT'].includes(ma) || loi?.status === 409 || loi?.http_status === 409
        ? 'Cấu hình đã được người khác sửa, tải lại trước khi lưu.'
        : 'Chưa xác nhận được việc lưu cấu hình. Tải lại trước khi lưu tiếp.';
      return false;
    } finally { dangChay = false; khoa(); }
  }
  o.addEventListener('input', kiem);
  form.addEventListener('submit', e => { e.preventDefault(); return ghi(); });
  taiLai.addEventListener('click', doc);
  khoa();
  const nap = async () => { const [a, b] = await Promise.all([doc(), manDuyet.nap()]); return a && b; };
  return { nap, doc, luu: ghi, oThoiHan: o, nutLuu: luu, nutTaiLai: taiLai, loiO, thongBao, manDuyet };
}
// Điểm nạp như màn module; taoMan giữ API điều khiển để kiểm offline.
export async function nap({ goc, KttCore = globalThis.KttCore }) {
  goc.replaceChildren();
  const man = taoMan({ goc, KttCore, document: goc.ownerDocument });
  await man.nap();
  return () => goc.replaceChildren();
}
export default nap;
