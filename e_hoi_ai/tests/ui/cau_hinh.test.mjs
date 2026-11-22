import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import test from 'node:test';
import {DEMO,taoCore,taoGoc,tatCa,chu,tim,nhap} from './core_gia.mjs';
const nguon=await readFile(new URL('../../goi/e_hoi_ai/ui/cau_hinh.js',import.meta.url),'utf8');
const {default:nap}=await import(`data:text/javascript;base64,${Buffer.from(nguon).toString('base64')}`);
async function dung(opts) { const ctx=taoCore(opts);const goc=taoGoc();await nap(goc,ctx.core);return {goc,...ctx}; }
async function bam(goc,ten) { await tim(goc,'button',ten).goi('click'); }
async function sua(goc,ten,gt) { const el=nhap(goc,ten);el.value=gt;await el.goi(el.the==='select'?'change':'input'); }
async function luu(goc) { await tim(goc,'form').goi('submit'); }

test('Đọc phân trang, tách IP/cổng, lưu và tăng CAS; giữ thứ tự dự phòng',async()=>{
  const {goc,daLuu,daTim}=await dung();assert.equal(daTim.length,2);assert.deepEqual(daTim[0].loc,{url:DEMO.local_ai.url});
  assert.equal(nhap(goc,'Địa chỉ IP').value,'127.0.0.1');assert.equal(nhap(goc,'Cổng').value,'11434');
  assert.match(chu(goc),/Máy AI/);assert.match(chu(goc),/lần kiểm trước/);
  await sua(goc,'Cổng','1234');await sua(goc,'Thời hạn chờ (giây)','25');await luu(goc);
  assert.deepEqual(daLuu[0],{giaTri:{...DEMO,local_ai:{url:'http://127.0.0.1:1234',timeout_giay:25}},rv:7});
  await luu(goc);assert.equal(daLuu[1].rv,8);assert.match(chu(goc),/Đã lưu cấu hình/);
});
test('CAS xung đột giữ dữ liệu và khóa lưu đến khi tải lại',async()=>{
  const {goc,daLuu,trangThai}=await dung({xungDot:true});await sua(goc,'Thời hạn chờ (giây)','30');await luu(goc);
  assert.match(chu(goc),/Cấu hình đã được người khác sửa, tải lại trước khi lưu/);
  assert.equal(nhap(goc,'Thời hạn chờ (giây)').value,'30');await luu(goc);assert.equal(daLuu.length,1);
  trangThai.xungDot=false;trangThai.phien=9;await bam(goc,'Tải lại cấu hình');await luu(goc);assert.equal(daLuu[1].rv,9);
});
for (const [ten,gt,loi] of [['Địa chỉ IP','8.8.8.8',/Nhập IP nội bộ/],['Địa chỉ IP','127.0.0.01',/Nhập IP nội bộ/],['Địa chỉ IP','ai.example',/Nhập IP nội bộ/],['Địa chỉ IP','http://127.0.0.1:1234',/Nhập IP nội bộ/],['Cổng','65536',/Nhập số nguyên/],['Cổng','1.5',/Nhập số nguyên/],['Cổng','',/Nhập số nguyên/],['Thời hạn chờ (giây)','0',/Nhập thời hạn/],['Thời hạn chờ (giây)','601',/Nhập thời hạn/]]) {
  test(`Lỗi cạnh ô ${ten}: ${gt}`,async()=>{const {goc,daLuu}=await dung();await sua(goc,ten,gt);await luu(goc);assert.equal(daLuu.length,0);assert.match(chu(goc),loi);assert.equal(nhap(goc,ten).thuocTinh['aria-invalid'],'true');});
}
test('Tạo cấu hình từ trống, thêm/bỏ quy tắc và lỗi nhập tại dòng',async()=>{
  const {goc,daLuu}=await dung({trong:true});await sua(goc,'Địa chỉ IP','127.0.0.1');
  await bam(goc,'Thêm quy tắc');await luu(goc);assert.equal(daLuu.length,0);assert.match(chu(goc),/Dòng 1: nhập mẫu mã prompt/);
  await bam(goc,'Kiểm tra kết nối');await sua(goc,'Mẫu mã prompt','*');await sua(goc,'Model ưu tiên','model-demo');
  await bam(goc,'Thêm dự phòng');await luu(goc);assert.match(chu(goc),/chọn model dự phòng 1 hoặc bỏ ô/);
  await sua(goc,'Dự phòng 1','model-demo-b');await luu(goc);assert.deepEqual(daLuu[0].giaTri.quy_tac_model,[{mau_ma_prompt:'*',uu_tien:'model-demo',du_phong:['model-demo-b']}]);
  await bam(goc,'Bỏ quy tắc');await luu(goc);assert.deepEqual(daLuu[1].giaTri.quy_tac_model,[]);
});
test('Đổi thứ tự quy tắc/dự phòng giữ đúng ý nghĩa runtime',async()=>{
  const cauHinh=structuredClone(DEMO);cauHinh.quy_tac_model.push({mau_ma_prompt:'*',uu_tien:'model-demo-b',du_phong:['model-demo-b','model-demo']});
  const {goc,daLuu}=await dung({cauHinh});let rows=tim(goc,'tbody').con;
  await tim(rows[1].con[3],'button','Lên').goi('click');rows=tim(goc,'tbody').con;
  await tatCa(rows[0].con[2]).filter(n=>n.the==='button'&&n.textContent==='Lên')[1].goi('click');
  await luu(goc);assert.equal(daLuu[0].giaTri.quy_tac_model[0].mau_ma_prompt,'*');assert.deepEqual(daLuu[0].giaTri.quy_tac_model[0].du_phong,['model-demo','model-demo-b']);
});
for (const ten of ['Kiểm tra kết nối','Cập nhật model']) {
  test(`${ten}: thành công, thất bại, model rỗng và lỗi Core`,async()=>{
    const {goc,daGoi,trangThai}=await dung();await bam(goc,ten);
    assert.match(chu(goc),/✓ Kết nối được/);assert.match(chu(goc),/21\/11\/2026/);assert.equal(daGoi[0].gt.url,DEMO.local_ai.url);
    trangThai.models=[];await bam(goc,ten);assert.match(chu(goc),/chưa có model khả dụng/);
    trangThai.matKetNoi=true;await bam(goc,ten);assert.match(chu(goc),/Không kết nối được/);
    trangThai.loiKiem=true;await bam(goc,ten);assert.match(chu(goc),/Chưa kiểm được máy AI/);assert.doesNotMatch(chu(goc),/DEMO-CHI-TIET/);
  });
}
test('Tự tìm: chọn máy, không tìm được, Core lỗi',async()=>{
  const {goc,daGoi,trangThai}=await dung();await bam(goc,'Tự tìm máy AI');assert.match(chu(goc),/Tìm thấy 1 máy/);
  assert.deepEqual(daGoi[0],{ma:'tim_may_ai',gt:{}});await bam(goc,'Chọn http://127.0.0.1:1234');assert.equal(nhap(goc,'Cổng').value,'1234');assert.match(chu(goc),/Chưa kiểm tra/);
  trangThai.khongMay=true;await bam(goc,'Tự tìm máy AI');assert.match(chu(goc),/Không tìm thấy máy AI/);
  trangThai.loiKiem=true;await bam(goc,'Tự tìm máy AI');assert.match(chu(goc),/Chưa kiểm được máy AI/);
});
test('Phản hồi kiểm máy cũ không ghi đè khi địa chỉ đang sửa',async()=>{
  let xong;const cho=new Promise(r=>{xong=r;});const {goc}=await dung({cho});
  const pending=bam(goc,'Kiểm tra kết nối');await sua(goc,'Cổng','1234');xong();await pending;
  assert.doesNotMatch(chu(goc),/✓ Kết nối được/);assert.match(chu(goc),/Địa chỉ đang sửa/);
});
for (const opts of [{loiDoc:true},{loiNgan:true}]) test('Lỗi đọc chặn lưu đè và có nút tải lại',async()=>{
  const {goc,daLuu,trangThai}=await dung(opts);await luu(goc);assert.equal(daLuu.length,0);assert.match(chu(goc),/Chưa đọc được cấu hình/);
  trangThai.loiDoc=false;trangThai.loiNgan=false;await bam(goc,'Tải lại cấu hình');await luu(goc);assert.equal(daLuu.length,1);
});
test('Lỗi lưu chung được ẩn chi tiết, vẫn thử lại được',async()=>{
  const {goc,daLuu,trangThai}=await dung({loiLuu:true});await luu(goc);assert.match(chu(goc),/Không lưu được cấu hình/);assert.doesNotMatch(chu(goc),/DEMO-CHI-TIET/);
  trangThai.loiLuu=false;await luu(goc);assert.equal(daLuu.length,2);
});
for (const url of ['http://[::1]:1234/v1','http://127.0.0.1:1234/v1/chat/completions','http://127.0.0.1:80']) test(`Lưu giữ đường dẫn/IPv6: ${url}`,async()=>{
  const cauHinh={...DEMO,local_ai:{url,timeout_giay:60}};const {goc,daLuu}=await dung({cauHinh});await luu(goc);assert.equal(daLuu[0].giaTri.local_ai.url,url);
});
test('Model không khả dụng giữ giá trị cũ; mã HTML không thành DOM; không có bí mật ở lát này',async()=>{
  const {goc}=await dung({models:[{id_model:'<img src=x onerror=alert(1)>',kha_dung:true},{id_model:'remote-demo',kha_dung:false}]});
  await bam(goc,'Cập nhật model');assert.match(chu(goc),/chưa khả dụng/);assert.equal(tatCa(goc).filter(n=>n.the==='img').length,0);
  assert.equal(tatCa(goc).filter(n=>n.type==='password').length,0);assert.doesNotMatch(chu(goc),/DEMO-CHI-TIET/);
  const cloud=tim(goc,'form').con[1];assert.match(chu(cloud),/Chưa áp dụng ở bản 1/);assert.equal(tatCa(cloud).filter(n=>['button','input'].includes(n.the)).length,0);
  assert.doesNotMatch(nguon,/innerHTML|\beval\s*\(|\bfetch\s*\(|XMLHttpRequest|localStorage|sessionStorage|\.bi_mat/);
});
