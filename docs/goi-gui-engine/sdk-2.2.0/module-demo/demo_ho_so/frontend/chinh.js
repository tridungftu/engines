// Màn của module DEMO "Hồ sơ DEMO": danh sách hồ sơ + chỗ đặt nút "Đọc tệp".
// Core vẽ khung, chọn pháp nhân và vẽ nút ở chỗ đánh dấu data-ktt-nut khi nút đã gắn quy trình đã áp dụng và
// người dùng có quyền của nút (hợp đồng a.10 điểm 4); chưa gắn thì người dùng không thấy nút. Lỗi chỉ hiện câu dễ hiểu qua sdk.thong_bao.loi.
const MA_MODULE = 'demo_ho_so';
const COT = [
  { ma: 'ten_ho_so', nhan: 'Tên hồ sơ' },
  { ma: 'so_tu', nhan: 'Số từ' },
  { ma: 'so_dong', nhan: 'Số dòng' },
  { ma: 'ngay_tao', nhan: 'Ngày tạo' },
];

export async function hienThi(target, { sdk, signal }) {
  const doc = target.ownerDocument;
  const el = (tag, text) => {
    const node = doc.createElement(tag);
    if (text !== undefined) node.textContent = text;
    return node;
  };
  const khung = el('section'), choNut = el('div'), thongBao = el('p'), bang = el('div');
  khung.className = 'demo-ho-so';
  choNut.className = 'demo-ho-so-nut';
  choNut.setAttribute('data-ktt-nut', 'doc_tep'); // chỗ Core đặt nút "Đọc tệp"
  thongBao.setAttribute('role', 'status');
  khung.append(el('h2', 'Hồ sơ'), choNut, thongBao, bang);
  target.replaceChildren(khung);
  if (typeof sdk.nut?.dat === 'function') sdk.nut.dat('doc_tep', choNut);

  async function tai() {
    thongBao.textContent = 'Đang tải danh sách hồ sơ…';
    try {
      const kq = await sdk.api.goi({ duong_dan: `/api/v1/module/${MA_MODULE}/ho-so`, signal });
      if (signal?.aborted) return;
      const dong = (Array.isArray(kq?.danh_sach) ? kq.danh_sach : []).map(h => ({
        ten_ho_so: h.ten_ho_so || 'Hồ sơ chưa đặt tên',
        so_tu: h.so_tu,
        so_dong: h.so_dong,
        ngay_tao: typeof h.tao_luc === 'string' ? h.tao_luc.slice(0, 10) : '',
      }));
      thongBao.textContent = dong.length ? '' : 'Chưa có hồ sơ nào.';
      sdk.bang.dung(bang, { cot: COT, dong });
    } catch (loi) {
      if (!signal?.aborted) {
        thongBao.textContent = '';
        sdk.thong_bao.loi(bang, loi);
      }
    }
  }

  await tai();
  return () => target.replaceChildren();
}
