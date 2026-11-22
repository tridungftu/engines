import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import test from 'node:test';
import {taoGoc,tatCa,chu,tim,nhap} from './core_gia.mjs';
import {taoKet} from './cloud_core_gia.mjs';
const nguon = await readFile(new URL('../../goi/e_hoi_ai/ui/cloud.js',import.meta.url),'utf8');
const {default:nap} = await import(`data:text/javascript;base64,${Buffer.from(nguon).toString('base64')}`);
async function dung(opts) { const ctx=taoKet(opts),goc=taoGoc();await nap(goc,ctx.core);return {goc,...ctx}; }
async function bam(goc,ten) { await tim(goc,'button',ten).goi('click'); }
async function ghi(goc,gt='DEMO-KEY-MOI-7XBB') { const el=nhap(goc,'API key Anthropic');if(el.disabled)return;el.value=gt;await el.goi('input');await tim(goc,'form').goi('submit'); }
function anKey(goc) { assert.equal(nhap(goc,'API key Anthropic').value,'');assert.doesNotMatch(chu(goc),/DEMO-KEY|DEMO-LOI-BI-MAT/); }

test('Cloud khóa mọi đường gửi; nhà cung cấp/model/tỷ lệ chỉ đọc; nhật ký không bịa',async()=>{
  const {goc,calls}=await dung();
  for(const ten of ['Nhà cung cấp','Model','Tỷ lệ kiểm ngẫu nhiên (%)']) assert.equal(nhap(goc,ten).disabled,true);
  assert.equal(tatCa(goc).find(n=>n.thuocTinh.role==='switch').thuocTinh['aria-checked'],'false');
  for(const ten of ['Kiểm tra kết nối Cloud','Xem nhật ký gửi ra ngoài']) { assert.equal(tim(goc,'button',ten).disabled,true);await bam(goc,ten); }
  assert.deepEqual(calls,[{ma:'doc'}]);assert.match(chu(goc),/chưa thể xác minh lịch sử gửi/);assert.match(chu(goc),/M9 và nhóm 07/);
});
test('Đọc metadata, chỉ hiện 4 ký tự cuối; không có nút hiện bản rõ',async()=>{
  const {goc}=await dung();assert.equal(nhap(goc,'API key Anthropic').type,'password');
  assert.match(chu(goc),/Đã lưu · •••• 8QAA/);assert.equal(tatCa(goc).filter(n=>n.type==='password').length,1);anKey(goc);
});
test('Lưu rồi xóa key với CAS tăng đơn điệu, Cloud luôn khóa',async()=>{
  const {goc,calls}=await dung();await ghi(goc);anKey(goc);assert.match(chu(goc),/•••• 7XBB/);
  await bam(goc,'Xóa key');anKey(goc);assert.match(chu(goc),/Chưa lưu key/);
  assert.equal(tim(goc,'button','Xóa key').disabled,true);
  await ghi(goc);assert.deepEqual(calls,[{ma:'doc'},{ma:'luu',rv:7},{ma:'xoa',rv:8},{ma:'luu',rv:9}]);
  assert.match(chu(goc),/Cloud vẫn tạm khóa/);
});
for(const gt of ['', 'short','DEMO KEY ABCD','DEMO-KEY\nABCD','D'.repeat(4097)]) test(`Lỗi nhập key (${gt.length} ký tự), không ghi két`,async()=>{
  const {goc,calls}=await dung();await ghi(goc,gt);assert.equal(calls.length,1);
  assert.match(chu(goc),/API key: nhập từ 8 đến 4096/);assert.equal(nhap(goc,'API key Anthropic').thuocTinh['aria-invalid'],'true');anKey(goc);
});
for(const ma of ['luu','xoa']) test(`CAS tranh chấp khi ${ma}, giữ khóa đến tải lại`,async()=>{
  const {goc,state,calls}=await dung();state.phien_ban=10;
  if(ma==='luu') await ghi(goc);else await bam(goc,'Xóa key');
  assert.match(chu(goc),/Key đã được người khác sửa/);assert.equal(tim(goc,'button','Lưu key').disabled,true);anKey(goc);
  await ghi(goc);assert.equal(calls.length,2);
  await bam(goc,'Tải lại trạng thái key');await ghi(goc);assert.deepEqual(calls.at(-1),{ma:'luu',rv:10});
});
test('Lỗi đọc hoặc thiếu cổng Core khóa két; tải lại phục hồi được',async()=>{
  const {goc,state,calls}=await dung({loiDoc:true});assert.match(chu(goc),/Chưa đọc được két bí mật/);await ghi(goc);assert.equal(calls.length,1);anKey(goc);
  state.loiDoc=false;await bam(goc,'Tải lại trạng thái key');assert.equal(tim(goc,'button','Lưu key').disabled,false);
  const thieu=taoGoc();await nap(thieu,{engine(){return {};}});assert.match(chu(thieu),/Chưa đọc được két bí mật/);assert.equal(nhap(thieu,'API key Anthropic').disabled,true);
});
for(const ma of ['luu','xoa']) test(`Lỗi ${ma} không lộ chi tiết, không retry mù`,async()=>{
  const {goc,state,calls}=await dung({loiGhi:true});if(ma==='luu')await ghi(goc);else await bam(goc,'Xóa key');
  assert.match(chu(goc),/Chưa xác nhận được cập nhật key/);anKey(goc);await ghi(goc);assert.equal(calls.length,2);
  state.loiGhi=false;await bam(goc,'Tải lại trạng thái key');await ghi(goc);assert.match(chu(goc),/Đã lưu key trong két Core/);
});
for(const metaSai of [{da_luu:true,bon_ky_tu_cuoi:'DEMO-KEY-BAN-RO',phien_ban:7},{da_luu:true,bon_ky_tu_cuoi:'ABCD',phien_ban:null},{da_luu:'true',bon_ky_tu_cuoi:'ABCD',phien_ban:7}]) test('Metadata sai bị từ chối, không lộ key hoặc mở ghi',async()=>{
  const {goc}=await dung({metaSai});assert.match(chu(goc),/Chưa đọc được két bí mật/);anKey(goc);assert.equal(tim(goc,'button','Lưu key').disabled,true);
});
test('Khi đang ghi xóa ngay ô mật khẩu, chặn ghi/xóa/đọc song song',async()=>{
  let xong;const cho=new Promise(r=>{xong=r;});const {goc,calls}=await dung({cho});
  const key=nhap(goc,'API key Anthropic');key.value='DEMO-KEY-MOI-7XBB';await key.goi('input');
  const p=tim(goc,'form').goi('submit');
  anKey(goc);await bam(goc,'Xóa key');await bam(goc,'Tải lại trạng thái key');await tim(goc,'form').goi('submit');assert.equal(calls.length,2);
  xong();await p;anKey(goc);
});
for(const metaGhiSai of [{da_luu:false,bon_ky_tu_cuoi:null,phien_ban:8},{da_luu:true,bon_ky_tu_cuoi:'ABCD',phien_ban:7},{da_luu:true,bon_ky_tu_cuoi:'DEMO-KEY-BAN-RO',phien_ban:8}]) test('Phản hồi lưu sai trạng thái/phiên bản không được báo thành công',async()=>{
  const {goc}=await dung({metaGhiSai});await ghi(goc);anKey(goc);assert.match(chu(goc),/Chưa xác nhận được cập nhật key/);assert.doesNotMatch(chu(goc),/Đã lưu key trong két Core/);
});
test('Chỉ dùng cổng engine; không mạng, lưu máy, HTML động; schema đủ hướng dẫn mọi cấp',async()=>{
  assert.doesNotMatch(nguon,/innerHTML|\beval\s*\(|\bfetch\s*\(|XMLHttpRequest|localStorage|sessionStorage|\.thao_tac\s*\(/);
  const schema=JSON.parse(await readFile(new URL('../../goi/e_hoi_ai/cau_hinh.schema.json',import.meta.url),'utf8'));
  function kiem(s){for(const k of ['title','description','examples'])assert.ok(s[k],k);for(const p of Object.values(s.properties||{}))kiem(p);if(s.items)kiem(s.items);}
  kiem(schema);
  const khai=JSON.parse(await readFile(new URL('../../goi/e_hoi_ai/KHAI-SDK-2.1.json',import.meta.url),'utf8'));
  assert.ok(khai.giao_dien_quan_tri.some(m=>m.tep==='ui/cloud.js'));assert.deepEqual(khai.bi_mat,['khoa_api_anthropic']);
});
