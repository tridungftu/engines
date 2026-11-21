import assert from 'node:assert/strict';
import test from 'node:test';
import {readFile} from 'node:fs/promises';
import {dom, nap, coreGia, DEMO, dulieu, tim, tatCa, oNhap, nhap, bam, gocGoi, nguon} from './core_gia.mjs';
globalThis.fetch = () => { throw Error('Cấm mạng trong test UI.'); };
globalThis.WebSocket = class { constructor() { throw Error('Cấm mạng trong test UI.'); } };
async function dung(tuyChon = {}, nangLuc) {
  const core = coreGia(tuyChon); if (nangLuc) core.nguCanh.nang_luc = nangLuc;
  const goc = dom(), man = await nap(goc,core.KttCore,core.nguCanh); return {goc, man, ...core};
}
const docBang = {khuon:'tong_quat', tien_te:'VND', khuon_cot_json:JSON.stringify(dulieu.MAU.khuon_cot_json)};

test('Đọc, sửa, lưu đúng chuỗi JSON; giữ tham số khác, CAS tăng sau mỗi lần lưu', async () => {
  const {goc,man,daLuu} = await dung({tham_so:{...DEMO, tham_so_module:'giữ nguyên DEMO'}});
  assert.equal(oNhap(goc,'Chọn sheet').value,'BTH');
  await nhap(goc,'Tên nhóm','Đơn giá điều chỉnh DEMO');
  await bam(goc,'Kiểm tra cài đặt'); assert.match(goc.textContent,/Kiểm tra đạt/);
  await bam(goc,'Lưu vào bước'); assert.match(goc.textContent,/Đã lưu cài đặt bước/);
  assert.equal(daLuu[0].phien_ban,7);
  assert.equal(JSON.parse(daLuu[0].tham_so.bo_nhom_json).nhom[0].ten,'Đơn giá điều chỉnh DEMO');
  assert.equal(daLuu[0].tham_so.tham_so_module,'giữ nguyên DEMO');
  await bam(goc,'Lưu vào bước'); assert.equal(daLuu[1].phien_ban,8);
  assert.equal(man.xuat().kiem_nguon_kl,true);
});
test('Ô đích: tên sheet có nháy, ô tuyệt đối, biên XFD và fallback nhãn', async () => {
  const {goc,man} = await dung();
  await nhap(goc,'Chọn sheet',"Sheet DEMO's"); await nhap(goc,'Địa chỉ ô','$XFD$1048576');
  assert.equal(man.xuat().o_dich,"'Sheet DEMO''s'!$XFD$1048576");
  await nhap(goc,'Địa chỉ ô','XFE1'); assert.throws(man.xuat);
  await bam(goc,'Kiểm tra cài đặt'); assert.match(goc.textContent,/Chưa đạt/);
  await nhap(goc,'Chọn sheet',''); await nhap(goc,'Địa chỉ ô','');
  assert.equal(man.xuat().o_dich,'');
  assert.deepEqual(JSON.parse(man.xuat().nhan_o_dich_json),dulieu.MAU.nhan_o_dich_json);
});
test('Nhóm: thêm/xóa/đổi thứ tự; nhiều điều kiện, cụm AND, từ OR, vùng và loại trừ', async () => {
  const {goc,man} = await dung();
  await bam(goc,'Thêm nhóm'); await nhap(goc,'Tên nhóm','Khối lượng DEMO',1); await nhap(goc,'Tài liệu cần đối chiếu','Bảng khối lượng DEMO',1);
  await nhap(goc,'Từ khóa 1','khối lượng',3);
  // Mỗi điều kiện có một cụm; thêm nhánh OR rồi bỏ để kiểm đường chỉnh cấu trúc.
  await bam(goc,'Thêm điều kiện khác',1); await bam(goc,'Bỏ điều kiện',2);
  await bam(goc,'Thêm cụm bắt buộc',1); await nhap(goc,'Từ khóa 1','=lũy kế',4);
  await bam(goc,'Thêm danh sách loại trừ'); await nhap(goc,'Từ khóa 1','tạm tính',5);
  await bam(goc,'Lên một nhóm',1);
  const bo = JSON.parse(man.xuat().bo_nhom_json);
  assert.equal(bo.nhom[0].ten,'Khối lượng DEMO');
  assert.deepEqual(bo.nhom[0].khi[0].tat_ca,[['khối lượng'],['=lũy kế']]);
  assert.deepEqual(bo.nhom[0].khi[0].khong_co,['tạm tính']);
  await bam(goc,'Bỏ nhóm'); assert.equal(JSON.parse(man.xuat().bo_nhom_json).nhom.length,1);
});
test('Lỗi nhập hiện cạnh trường, không lưu; trùng tên/mã, thiếu vùng và thiếu từ khóa', async () => {
  const {goc,man,daLuu} = await dung();
  await nhap(goc,'Tên bộ nhóm','');
  assert.equal(oNhap(goc,'Tên bộ nhóm').thuocTinh['aria-invalid'],'true');
  assert.match(goc.textContent,/Nhập tên bộ nhóm/); assert.throws(man.xuat);
  assert.equal(tim(goc,'button','Lưu vào bước').disabled,true); assert.equal(daLuu.length,0);
  const n = dulieu.sao(dulieu.MAU.bo_nhom_json); n.nhom.push(dulieu.sao(n.nhom[0]));
  n.nhom[0].khi[0].vung=[]; n.nhom[0].khi[0].tat_ca=[['=']];
  const errors = dulieu.kiemJson('bo_nhom_json',n);
  for (const s of ['Mã nhóm đã có','Tên nhóm trùng','Chọn ít nhất','dấu =']) assert.ok(errors.some(e => e.cau.includes(s)));
});
test('Khuôn cột: đọc/sửa kiểu, bắt buộc, dòng dừng, tiền tệ và thêm/xóa cột', async () => {
  const {goc,man,daLuu} = await dung({tham_so:docBang},'excel.doc_bang@1');
  await nhap(goc,'Kiểu dữ liệu','ngay'); await nhap(goc,'Mã tiền tệ','USD');
  await bam(goc,'Thêm cột'); await nhap(goc,'Mã cột kết quả','ghi_chu',2); await nhap(goc,'Từ khóa 1','ghi chú',2);
  const k = JSON.parse(man.xuat().khuon_cot_json); assert.equal(k.cot[0].kieu,'ngay'); assert.equal(k.cot.length,3);
  await bam(goc,'Lưu vào bước'); assert.equal(daLuu[0].tham_so.tien_te,'USD');
  await bam(goc,'Bỏ cột',2); assert.equal(JSON.parse(man.xuat().khuon_cot_json).cot.length,2);
  await nhap(goc,'Mã cột kết quả','Ma SAi'); assert.throws(man.xuat); assert.match(goc.textContent,/Mã cột không trùng/);
  await nhap(goc,'Mã tiền tệ','vnđ'); assert.match(goc.textContent,/3 chữ in hoa/);
});
test('Trống, chèn mẫu, chuyển khuôn không xóa bộ cột đã soạn', async () => {
  const {goc,man} = await dung({tham_so:{}},'excel.doc_bang@1');
  assert.equal(man.xuat().khuon,'xay_dung_klgt');
  await nhap(goc,'Khuôn đọc bảng','tong_quat'); assert.throws(man.xuat);
  await bam(goc,'Chèn mẫu DEMO'); const raw = man.xuat().khuon_cot_json;
  await nhap(goc,'Khuôn đọc bảng','xay_dung_klgt'); assert.equal(man.xuat().khuon_cot_json,raw);
  await bam(goc,'Để trống'); assert.equal(man.xuat().khuon_cot_json,'');
});
test('CAS hai màn: giữ bản sửa, khóa lưu đến khi tải lại bản mới', async () => {
  const core = coreGia(), a = dom(), b = dom();
  await nap(a,core.KttCore,core.nguCanh); await nap(b,core.KttCore,core.nguCanh);
  await nhap(a,'Tên bộ nhóm','Bản A DEMO'); await bam(a,'Lưu vào bước');
  await nhap(b,'Tên bộ nhóm','Bản B DEMO'); await bam(b,'Lưu vào bước');
  assert.match(b.textContent,/đã được người khác sửa, tải lại trước khi lưu/);
  assert.equal(oNhap(b,'Tên bộ nhóm').value,'Bản B DEMO');
  assert.equal(tim(b,'button','Lưu vào bước').disabled,true);
  assert.doesNotMatch(b.textContent,/DEMO_bi_mat/);
  await bam(b,'Tải lại (bỏ sửa trên màn)'); assert.equal(oNhap(b,'Tên bộ nhóm').value,'Bản A DEMO');
});
test('Lỗi đọc/lưu không lộ chi tiết, không lưu đè; thiếu CAS không báo thành công', async () => {
  for (const opts of [{loiDoc:true},{loiLuu:true},{phien:null}]) {
    const {goc,daLuu} = await dung(opts);
    if (opts.loiLuu) { await bam(goc,'Lưu vào bước'); assert.match(goc.textContent,/Chưa xác nhận/); }
    assert.equal(tim(goc,'button','Lưu vào bước').disabled,true);
    assert.doesNotMatch(goc.textContent,/DEMO_bi_mat/);
    assert.equal(daLuu.length,opts.loiLuu ? 1 : 0);
  }
});
test('Đang lưu khóa thao tác, không gửi hai lần; không sửa ngầm dữ liệu lỗi nguồn', async () => {
  let mo; const tre = new Promise(r => { mo=r; });
  const {goc,daLuu} = await dung({tre});
  const b = tim(goc,'button','Lưu vào bước'); const p = b.goi('click'); await b.goi('click');
  assert.equal(daLuu.length,1); mo(); await p;
  const sai = await dung({tham_so:{...DEMO,bo_nhom_json:'{"phien_ban":1,"phien_ban":1}'}});
  assert.throws(sai.man.xuat); assert.match(sai.goc.textContent,/Nguồn được giữ nguyên/);
  await bam(sai.goc,'Chèn mẫu DEMO',1); assert.doesNotThrow(sai.man.xuat);
});
test('UTF-8, trần số dòng/từ, khóa dư, kiểu sai, không cắt ngầm', () => {
  const n = dulieu.sao(dulieu.MAU.bo_nhom_json);
  n.ten_bo='á'.repeat(17000); assert.match(dulieu.kiemJson('bo_nhom_json',n).at(-1).cau,/UTF-8/);
  n.ten_bo='DEMO'; n.nhom[0].khi[0].tat_ca=[Array(201).fill('từ')];
  assert.ok(dulieu.kiemJson('bo_nhom_json',n).some(l=>l.cau.includes('200')));
  n.nhom=Array.from({length:31},(_,i)=>({...n.nhom[0],ma:`n${i}`,ten:`Nhóm ${i}`}));
  assert.ok(dulieu.kiemJson('bo_nhom_json',n).some(l=>l.cau.includes('30')));
  assert.throws(()=>dulieu.docJson('{"nhom":1,"nhom":2}'));
  const k = dulieu.sao(dulieu.MAU.khuon_cot_json); k.cot.forEach(c=>c.bat_buoc=false); k.du=1;
  const errs = dulieu.kiemJson('khuon_cot_json',k);
  assert.ok(errs.some(l=>l.cau.includes('ngoài cấu trúc'))); assert.ok(errs.some(l=>l.cau.includes('ít nhất một cột')));
  assert.ok(dulieu.kiemThamSo('excel.toan_ven@1',{nhan_o_dich_json:JSON.stringify(['á'.repeat(2100)])}).length);
  assert.equal(dulieu.tachODich('BTH!A1\n'),null);
  k.cot[0].ma='ma\n';
  assert.ok(dulieu.kiemJson('khuon_cot_json',k).some(l=>l.truong.endsWith('.ma')));
  assert.ok(dulieu.kiemThamSo('excel.doc_bang@1',{khuon:'xay_dung_klgt',tien_te:'VND\n'}).length);
  assert.ok(dulieu.kiemJson('nhan_o_dich_json',['\ud800']).length);
});
test('Round-trip toàn bộ DEMO manifest và bộ nhóm lồng nhau không mất cấu trúc', async () => {
  const phieu = JSON.parse(await readFile(new URL('engine.json',gocGoi),'utf8'));
  for (const demo of phieu.chay_thu_demo) {
    const {man} = await dung({tham_so:demo.tham_so, ds_sheet:[]},demo.nang_luc);
    const out = man.xuat();
    for (const [k,v] of Object.entries(demo.tham_so)) assert.deepEqual(k.endsWith('_json') ? JSON.parse(out[k]) : out[k],k.endsWith('_json') ? JSON.parse(v) : v);
  }
  const n = dulieu.sao(dulieu.MAU.bo_nhom_json);
  n.nhom[0].khi.push({vung:['ten_sheet','nhan_dong'],tat_ca:[['a,b','line\nbreak'],['=cụm từ']],khong_co:[]});
  const {man} = await dung({tham_so:{...DEMO,bo_nhom_json:JSON.stringify(n)}});
  assert.deepEqual(JSON.parse(man.xuat().bo_nhom_json),n);
});
test('Không mạng/lưu cục bộ/bí mật; nội dung HTML chỉ là văn bản; không lưu khi chưa nối D2', async () => {
  const {goc} = await dung({tham_so:{...DEMO,bo_nhom_json:JSON.stringify({...dulieu.MAU.bo_nhom_json,ten_bo:'<img src=x onerror=alert(1)>'})}});
  assert.equal(oNhap(goc,'Tên bộ nhóm').value,'<img src=x onerror=alert(1)>');
  assert.equal(tatCa(goc).filter(x=>['img','script'].includes(x.the)).length,0);
  for (const f of ['ui/tham_so.js','ui/du_lieu.js','ui/kieu_dang.js']) {
    const s=await readFile(new URL(f,gocGoi),'utf8');
    assert.doesNotMatch(s,/innerHTML|\beval\s*\(|\bfetch\s*\(|XMLHttpRequest|localStorage|sessionStorage|https?:\/\//);
  }
  assert.doesNotMatch(nguon,/\.bi_mat\b/);
  const el=dom(); await nap(el,coreGia().KttCore,{nang_luc:'excel.toan_ven@1',tham_so:{}});
  assert.equal(tim(el,'button','Lưu vào bước').disabled,true);
  assert.match(el.textContent,/Chưa nối lưu bước/);
});
