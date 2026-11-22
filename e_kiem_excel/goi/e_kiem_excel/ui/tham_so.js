import {VUNG, KIEU, MAU, sao, docJson, kiemJson, kiemThamSo, tachODich, ghepODich} from './du_lieu.js';
import css from './kieu_dang.js';

// Thành phần D2 thuần cục bộ. doc/luu là callback của màn bước Core, CHƯA là SDK.
// Không dùng cau_hinh/ngan của engine để cất tham số thuộc quy trình.
export default async function thamSo(goc, KttCore = globalThis.KttCore, nguCanh = {}) {
  const doc = goc.ownerDocument;
  const nangLuc = nguCanh.nang_luc;
  const laKiem = nangLuc === 'excel.toan_ven@1';
  let ts = {}, duLieu = {}, loiNguon = {}, sheets = [], phien = null;
  let docDuoc = false, xungDot = false, dangLuu = false, biHuy = false;
  let refs = new Map(), tongLoi, trangThai, luu, khung, xemJson, nhan;
  let demId = 0;
  const maJson = laKiem ? ['nhan_o_dich_json', 'bo_nhom_json'] : ['khuon_cot_json'];
  const ten = {nhan_o_dich_json: 'Cụm từ tìm ô đích', bo_nhom_json: 'Bộ nhóm dữ liệu gốc', khuon_cot_json: 'Khuôn cột'};
  function tao(the, chu, cha, cls) {
    const el = doc.createElement(the);
    if (chu !== undefined) el.textContent = chu;
    if (cls) el.className = cls;
    if (cha) cha.appendChild(el);
    return el;
  }
  function nut(cha, chu, fn) {
    const b = tao('button', chu, cha); b.type = 'button';
    b.addEventListener('click', async () => { if (!dangLuu && !biHuy) await fn(); }); return b;
  }
  function nhap(cha, nhanO, giaTri, p, huongDan, viDu, doi, luaChon = null) {
    const div = tao('div', undefined, cha);
    const id = `ex-${++demId}`;
    const label = tao('label', nhanO, div); label.htmlFor = id;
    const el = tao(luaChon ? 'select' : 'input', undefined, div); el.id = id;
    if (luaChon) for (const [v, t] of Object.entries(luaChon)) { const o = tao('option', t, el); o.value = v; }
    else el.type = 'text';
    el.value = giaTri ?? ''; el.placeholder = viDu;
    tao('small', huongDan, div).id = id + '-goi-y';
    const err = tao('div', '', div, 'loi'); err.id = id + '-loi';
    el.setAttribute('aria-describedby', `${id}-goi-y ${id}-loi`);
    refs.set(p, {el, err});
    el.addEventListener(luaChon ? 'change' : 'input', () => { doi(el.value); kiem(false); });
    return el;
  }
  function congTac(cha, chu, giaTri, doi) {
    const l = tao('label', undefined, cha, 'chon');
    const el = tao('input', undefined, l); el.type = 'checkbox'; el.checked = giaTri;
    tao('span', chu, l);
    el.addEventListener('change', () => { doi(el.checked); kiem(false); }); return el;
  }
  function loiTai(cha, p) { refs.set(p, {err:tao('div', '', cha, 'loi')}); }
  function dsTu(cha, ds, p, moTa) {
    tao('small', moTa, cha);
    const bao = tao('div', '', cha, 'loi'); refs.set(p, {err: bao});
    ds.forEach((v, i) => {
      const hang = tao('div', undefined, cha, 'hang');
      nhap(hang, `Từ khóa ${i + 1}`, v, `${p}.${i}`, 'Một cụm từ, giữ nguyên dấu câu.', '=tổng cộng', t => { ds[i] = t; });
      nut(hang, 'Bỏ từ khóa', () => { ds.splice(i, 1); ve(); });
    });
    nut(cha, 'Thêm từ khóa', () => { ds.push(''); ve(); });
  }
  function the(tieuDe, bieuTuong, nhanThe) {
    const card = tao('section', undefined, khung, 'the');
    const dau = tao('div', undefined, card, 'dau-the');
    tao('h3', `${bieuTuong}  ${tieuDe}`, dau); tao('span', nhanThe, dau, 'nhan-trang-thai');
    return tao('div', undefined, card, 'than-the');
  }
  function mau(cha, ma) {
    if (loiNguon[ma]) tao('p', loiNguon[ma], cha, 'loi');
    nut(cha, 'Chèn mẫu DEMO', () => { duLieu[ma] = sao(MAU[ma]); delete loiNguon[ma]; ve(); });
    nut(cha, 'Để trống', () => { duLieu[ma] = null; delete loiNguon[ma]; ve(); });
    tao('small', ' Chèn mẫu thay nội dung của phần này; Để trống bỏ toàn bộ phần này.', cha);
  }
  function quanLy(cha, ds, i, danhTu) {
    const hang = tao('div', undefined, cha, 'hang');
    const len = nut(hang, `Lên một ${danhTu}`, () => { [ds[i-1], ds[i]] = [ds[i], ds[i-1]]; ve(); }); len.disabled = i === 0;
    const xuong = nut(hang, `Xuống một ${danhTu}`, () => { [ds[i+1], ds[i]] = [ds[i], ds[i+1]]; ve(); }); xuong.disabled = i === ds.length - 1;
    nut(hang, `Bỏ ${danhTu}`, () => { ds.splice(i, 1); ve(); });
  }
  function nangCao(cha, chu) {
    const d = tao('details', undefined, cha); tao('summary', chu, d); return d;
  }
  function boNhom() {
    const cha = the('Bộ nhóm dữ liệu gốc', '▤', 'Xét từ trên xuống');
    tao('p', 'Nhóm đầu tiên khớp được chọn. Không có bộ nhóm: các lá là Chưa phân nhóm, số ngoài nhóm chưa xác định.', cha, 'goi-y');
    mau(cha, 'bo_nhom_json');
    loiTai(cha, 'bo_nhom_json');
    const b = duLieu.bo_nhom_json; if (!b) return;
    nhap(cha, 'Tên bộ nhóm', b.ten_bo, 'bo_nhom_json.ten_bo', 'Tên dễ nhận biết của bộ quy tắc.', 'Nhóm DEMO', v => { b.ten_bo = v; });
    b.nhom.forEach((n, i) => {
      const det = tao('details', undefined, cha, 'nhom'); det.open = true;
      tao('summary', `Nhóm ${i + 1} · ${n.ten || 'Chưa đặt tên'}`, det);
      const p = `bo_nhom_json.nhom.${i}`;
      const grid = tao('div', undefined, det, 'luoi');
      nhap(grid, 'Tên nhóm', n.ten, `${p}.ten`, 'Tên nhóm không trùng trong bộ.', 'Đơn giá DEMO', v => { n.ten = v; });
      nhap(grid, 'Tài liệu cần đối chiếu', n.tai_lieu, `${p}.tai_lieu`, 'Tài liệu cần yêu cầu khi phát hiện vấn đề.', 'Bảng giá DEMO', v => { n.tai_lieu = v; });
      const adv = nangCao(det, 'Nâng cao · mã nhóm');
      nhap(adv, 'Mã nhóm', n.ma, `${p}.ma`, 'Mã nhận diện duy nhất, giữ ổn định khi sửa tên.', 'don_gia', v => { n.ma = v; });
      tao('p', 'Chỉ cần một điều kiện dưới đây khớp. Trong mỗi điều kiện, mọi cụm bắt buộc đều phải khớp trên phần văn bản ghép từ các vùng đã chọn.', det, 'goi-y');
      loiTai(det, `${p}.khi`);
      n.khi.forEach((dk, j) => {
        const r = `${p}.khi.${j}`;
        const f = tao('fieldset', undefined, det); tao('legend', `Điều kiện ${j + 1}`, f);
        const vung = tao('div', undefined, f, 'hang');
        for (const [k, t] of Object.entries(VUNG)) congTac(vung, t, dk.vung.includes(k), v => {
          dk.vung = v ? [...dk.vung, k] : dk.vung.filter(x => x !== k);
        });
        const err = tao('div', '', f, 'loi'); refs.set(`${r}.vung`, {err});
        loiTai(f, `${r}.tat_ca`);
        dk.tat_ca.forEach((cum, k) => {
          const ff = tao('fieldset', undefined, f); tao('legend', `Cụm bắt buộc ${k + 1}`, ff);
          dsTu(ff, cum, `${r}.tat_ca.${k}`, 'Khớp ít nhất một từ khóa trong cụm này.');
          nut(ff, 'Bỏ cụm bắt buộc', () => { dk.tat_ca.splice(k, 1); ve(); });
        });
        nut(f, 'Thêm cụm bắt buộc', () => { dk.tat_ca.push(['']); ve(); });
        const loaiTru = tao('fieldset', undefined, f); tao('legend', 'Từ khóa loại trừ', loaiTru);
        dsTu(loaiTru, dk.khong_co || [], `${r}.khong_co`, 'Không được có bất kỳ từ khóa nào trong danh sách này.');
        // Chỉ tạo khóa tùy chọn khi thao tác thêm, giữ nguyên dạng JSON đã đọc.
        if (!Object.hasOwn(dk, 'khong_co')) {
          loaiTru.replaceChildren(); tao('legend', 'Từ khóa loại trừ', loaiTru);
          nut(loaiTru, 'Thêm danh sách loại trừ', () => { dk.khong_co = ['']; ve(); });
        }
        nut(f, 'Bỏ điều kiện', () => { n.khi.splice(j, 1); ve(); });
      });
      nut(det, 'Thêm điều kiện khác', () => { n.khi.push({vung:['tieu_de_cot'], tat_ca:[['']]}); ve(); });
      quanLy(det, b.nhom, i, 'nhóm');
    });
    nut(cha, 'Thêm nhóm', () => {
      let i = b.nhom.length + 1; while (b.nhom.some(n => n.ma === `nhom_${i}`)) i++;
      b.nhom.push({ma:`nhom_${i}`, ten:'', tai_lieu:'', khi:[{vung:['tieu_de_cot'], tat_ca:[['']]}]}); ve();
    });
  }
  function khuonCot() {
    const cha = the('Khuôn cột', '▦', 'Đọc bảng tổng quát');
    tao('p', 'Mỗi dòng khai một cột cần đọc; cần ít nhất một cột bắt buộc. Cột số tiền dùng mã tiền tệ được khai hoặc đơn vị ghi rõ trong tệp.', cha, 'goi-y');
    mau(cha, 'khuon_cot_json'); const k = duLieu.khuon_cot_json; if (!k) return;
    loiTai(cha, 'khuon_cot_json');
    k.cot.forEach((c, i) => {
      const f = tao('fieldset', undefined, cha); tao('legend', `Cột ${i + 1}`, f);
      const p = `khuon_cot_json.cot.${i}`, grid = tao('div', undefined, f, 'bang-cot');
      nhap(grid, 'Mã cột kết quả', c.ma, `${p}.ma`, 'Chữ thường không dấu, số, gạch dưới; không trùng.', 'don_gia', v => { c.ma = v; });
      const ds = tao('div', undefined, grid); tao('label', 'Từ khóa tiêu đề', ds);
      dsTu(ds, c.tu_khoa, `${p}.tu_khoa`, 'Chỉ cần một từ khóa khớp.');
      const typ = tao('div', undefined, grid);
      nhap(typ, 'Kiểu dữ liệu', c.kieu, `${p}.kieu`, 'Ngày xuất dạng dữ liệu YYYY-MM-DD; khi hiển thị dùng dd/mm/yyyy.', '', v => { c.kieu = v; }, KIEU);
      congTac(typ, 'Cột bắt buộc', c.bat_buoc, v => { c.bat_buoc = v; });
      quanLy(f, k.cot, i, 'cột');
    });
    nut(cha, 'Thêm cột', () => { k.cot.push({ma:'', tu_khoa:[''], bat_buoc:false, kieu:'van_ban'}); ve(); });
    const f = tao('fieldset', undefined, cha); tao('legend', 'Dừng đọc tại dòng tổng', f);
    dsTu(f, k.dong_dung, 'khuon_cot_json.dong_dung', 'Xét ô có dữ liệu bên trái trong các cột nhận diện. Trống: đọc đến hết bảng.');
  }
  function xuat() {
    const out = sao(ts);
    for (const ma of maJson) if (!loiNguon[ma]) out[ma] = duLieu[ma] === null ? '' : JSON.stringify(duLieu[ma]);
    const errors = kiemThamSo(nangLuc, out, sheets);
    if (!docDuoc) errors.unshift({truong:'', cau:'Chưa đọc được cài đặt; cần tải lại trước khi lưu.'});
    for (const ma of Object.keys(loiNguon)) if (!errors.some(l => l.truong.startsWith(ma))) errors.push({truong:ma, cau:loiNguon[ma]});
    if (errors.length) { const err = Error('Cài đặt bước còn lỗi.'); err.loi = errors; throw err; }
    return out;
  }
  function kiem(baoThanhCong = true) {
    let errors = [];
    try { const out = xuat(); xemJson.textContent = JSON.stringify(out, null, 2); }
    catch (e) { errors = e.loi || [{truong:'', cau:'Không đọc được cài đặt; cần tải lại.'}]; xemJson.textContent = 'Chưa xuất: cần sửa các lỗi đang hiển thị.'; }
    for (const r of refs.values()) { r.err.textContent = ''; r.el?.setAttribute('aria-invalid', 'false'); }
    tongLoi.replaceChildren();
    for (const l of errors) {
      const r = refs.get(l.truong);
      if (r) { r.err.textContent = l.cau; r.el?.setAttribute('aria-invalid','true'); }
      tao('div', `${ten[l.truong.split('.')[0]] || 'Cài đặt bước'}: ${l.cau}`, tongLoi);
    }
    nhan.textContent = errors.length ? 'Cần sửa cài đặt' : '✓ Cấu trúc hợp lệ';
    nhan.className = 'nhan-trang-thai' + (errors.length ? '' : ' tot');
    luu.disabled = !nguCanh.luu || !docDuoc || errors.length > 0 || xungDot || dangLuu || phien === null;
    if (baoThanhCong) trangThai.textContent = errors.length ? 'Chưa đạt. Sửa các trường được đánh dấu.' : 'Kiểm tra đạt. Cấu trúc hợp lệ; chưa kiểm nội dung tệp Excel.';
    return errors;
  }
  async function ghi() {
    if (dangLuu || xungDot || !nguCanh.luu || phien === null || kiem(false).length) return;
    const out = xuat(); dangLuu = true; khung.disabled = true; luu.disabled = true;
    trangThai.textContent = 'Đang lưu cài đặt bước…';
    try {
      const kq = await nguCanh.luu(sao(out), phien);
      if (kq?.phien_ban === undefined || kq.phien_ban === null || kq.phien_ban === phien) throw Error('Chưa có xác nhận phiên bản mới.');
      if (biHuy) return;
      phien = kq.phien_ban; ts = sao(out); trangThai.textContent = 'Đã lưu cài đặt bước.';
    } catch (e) {
      if (biHuy) return;
      xungDot = e?.status === 409 || ['NGAN_XUNG_DOT','CAU_HINH_XUNG_DOT','THAM_SO_XUNG_DOT'].includes(e?.ma);
      trangThai.textContent = xungDot ? 'Cài đặt bước đã được người khác sửa, tải lại trước khi lưu. Nội dung đang sửa được giữ trên màn.' : 'Chưa xác nhận được lưu cài đặt. Tải lại để kiểm tra trước khi lưu tiếp.';
      if (!xungDot) docDuoc = false;
    } finally { dangLuu = false; khung.disabled = false; kiem(false); }
  }
  function ve() {
    if (biHuy) return;
    refs = new Map(); goc.replaceChildren(); goc.classList.add('ktt-ex');
    tao('style', css, goc);
    const dau = tao('div', undefined, goc, 'dau-the'); tao('h2', laKiem ? 'Cài đặt bước · Kiểm toàn vẹn Excel' : 'Cài đặt bước · Đọc bảng Excel', dau);
    nhan = tao('span', '', dau, 'nhan-trang-thai');
    tao('p', 'Soạn từng trường để tạo cài đặt cho quy trình. Từ khóa không phân biệt hoa thường và dấu tiếng Việt.', goc, 'goi-y');
    if (!nguCanh.luu) tao('p', 'Chưa nối lưu bước của Core. Có thể soạn và kiểm tra; cài đặt chỉ được giữ trong phiên đang mở.', goc, 'canh-bao');
    khung = tao('fieldset', undefined, goc, 'bo-khung'); tao('legend', 'Cài đặt bước', khung);
    if (laKiem) {
      const cha = the('Ô đích cần truy vết', '▣', 'Chọn ô hoặc tìm theo nhãn');
      const dich = ts.o_dich ? tachODich(ts.o_dich) : null;
      const grid = tao('div', undefined, cha, 'luoi');
      let sheet = dich?.sheet || '', o = dich?.o || '';
      const ghiDich = () => { ts.o_dich = sheet || o ? ghepODich(sheet, o) : ''; };
      nhap(grid, sheets.length ? 'Chọn sheet' : 'Tên sheet', sheet, 'o_dich', sheets.length ? 'Danh sách do màn bước cung cấp từ tệp đã chọn.' : 'Chưa có tệp mẫu; nhập đúng tên sheet. Ví dụ: BTH.', 'BTH', v => { sheet = v; ghiDich(); }, sheets.length ? Object.fromEntries([['','Chọn sheet'], ...[...new Set([...sheets, ...(sheet && !sheets.includes(sheet) ? [sheet] : [])])].map(s => [s,s])]) : null);
      nhap(grid, 'Địa chỉ ô', o, 'dia_chi_o', 'Ô từ A1 đến XFD1048576. Ví dụ: J39.', 'J39', v => { o = v; ghiDich(); });
      // Lỗi địa chỉ xuất hiện ngay cạnh ô; tên sheet có danh sách kiểm riêng.
      refs.set('o_dich', refs.get('dia_chi_o'));
      tao('p', 'Ô đích được ưu tiên. Để trống cả sheet và ô để tìm bằng các cụm từ bên dưới. Nếu không tìm được: K7 có một mục Kiểm soát.', cha, 'goi-y');
      mau(cha, 'nhan_o_dich_json');
      if (duLieu.nhan_o_dich_json) dsTu(cha, duLieu.nhan_o_dich_json, 'nhan_o_dich_json', 'Tìm trong 80 dòng đầu, 12 cột đầu của sheet hiện; lấy số đầu trong 6 ô bên phải nhãn.');
      congTac(cha, 'Kiểm nguồn khối lượng (K8)', ts.kiem_nguon_kl ?? false, v => { ts.kiem_nguon_kl = v; });
      boNhom();
    } else {
      const cha = the('Cách đọc bảng', '▣', 'Hai khuôn có sẵn');
      const grid = tao('div', undefined, cha, 'luoi');
      const chon = nhap(grid, 'Khuôn đọc bảng', ts.khuon, 'khuon', 'Khuôn xây dựng dùng bộ nhận diện sẵn; tổng quát dùng bảng cột bên dưới.', '', v => { ts.khuon = v; }, {xay_dung_klgt:'Bảng khối lượng xây dựng', tong_quat:'Bảng theo khuôn cột'});
      chon.addEventListener('change', ve);
      nhap(grid, 'Mã tiền tệ', ts.tien_te, 'tien_te', 'Ví dụ VND, USD. Trống: lấy đơn vị rõ trong tệp; chưa rõ thì không tự gán.', 'VND', v => { ts.tien_te = v; });
      if (ts.khuon === 'tong_quat' || duLieu.khuon_cot_json || loiNguon.khuon_cot_json) khuonCot();
    }
    tao('p', 'Từ khóa: văn bản thường = chứa chuỗi; tiền tố = khớp nguyên từ/cụm từ; # khớp một hoặc nhiều chữ số. Ký tự khác hiểu nguyên văn, không chạy regex.', khung, 'goi-y');
    const adv = nangCao(khung, 'Nâng cao · JSON đầu ra chỉ đọc');
    tao('p', 'Phiên bản cấu trúc: 1. Bộ nhóm/khuôn cột: tối đa 30 dòng, 200 từ khóa, 32 KiB UTF-8. Nhãn ô đích: 4 KiB UTF-8. Không cắt bớt khi vượt trần.', adv, 'goi-y');
    xemJson = tao('pre', '', adv);
    tongLoi = tao('div', '', goc, 'loi'); tongLoi.setAttribute('role','alert');
    const chan = tao('div', undefined, goc, 'chan');
    nut(chan, 'Kiểm tra cài đặt', () => kiem());
    luu = nut(chan, 'Lưu vào bước', ghi); luu.className = 'chinh';
    if (nguCanh.doc) nut(chan, 'Tải lại (bỏ sửa trên màn)', nap);
    trangThai = tao('p', '', goc); trangThai.setAttribute('role','status'); trangThai.setAttribute('aria-live','polite');
    kiem(false);
  }
  async function nap() {
    if (dangLuu || biHuy) return;
    docDuoc = false;
    try {
      const data = nguCanh.doc ? await nguCanh.doc() : nguCanh;
      if (biHuy) return;
      if (!data || !data.tham_so || typeof data.tham_so !== 'object' || Array.isArray(data.tham_so)) throw Error('Thiếu tham số.');
      ts = sao(data.tham_so); phien = data.phien_ban ?? null;
      sheets = Array.isArray(data.ds_sheet) && data.ds_sheet.every(s => typeof s === 'string') ? sao(data.ds_sheet) : [];
      if (!laKiem) { ts.khuon ??= 'xay_dung_klgt'; ts.tien_te ??= ''; }
      duLieu = {}; loiNguon = {};
      for (const ma of maJson) {
        duLieu[ma] = null; const raw = ts[ma] ?? '';
        if (raw === '') continue;
        try {
          if (typeof raw !== 'string' || new TextEncoder().encode(raw).length > (ma === 'nhan_o_dich_json' ? 4096 : 32768)) throw Error('Quá trần.');
          const d = docJson(raw);
          if (kiemJson(ma,d).length) throw Error('Sai cấu trúc.');
          duLieu[ma] = d;
        } catch { loiNguon[ma] = 'Cài đặt đã lưu sai cấu trúc hoặc vượt trần. Nguồn được giữ nguyên; tải lại hoặc chèn mẫu để thay phần này.'; }
      }
      docDuoc = true; xungDot = false; ve();
      if (nguCanh.luu && phien === null) trangThai.textContent = 'Core chưa cấp phiên bản bước để kiểm tranh chấp; chưa thể lưu.';
    } catch {
      ve(); trangThai.textContent = 'Không đọc được cài đặt bước. Tải lại trước khi lưu; nội dung lỗi kỹ thuật không được hiển thị.';
    }
  }
  await nap();
  return {xuat, kiem, nap, huy() { biHuy = true; goc.replaceChildren(); }};
}
