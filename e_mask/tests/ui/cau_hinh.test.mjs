import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile } from 'node:fs/promises';
import { napModule } from './nap_module.mjs';
const { taoMan, nap, tienTo, tuDien } = await napModule();

class PhanTu {
  constructor(ten) { this.ten=ten; this.children=[]; this.textContent=''; this.value=''; this.events={}; this.attributes={}; }
  append(...con) {
    for (const c of con) {
      if (c.parent) c.parent.children=c.parent.children.filter(v=>v!==c);
      c.parent=this; this.children.push(c);
    }
  }
  replaceChildren(...con) { this.children=[]; this.append(...con); }
  addEventListener(k,v) { this.events[k]=v; }
  setAttribute(k,v) { this.attributes[k]=v; }
  set innerHTML(v) { assert.fail('Cấm HTML'); }
}
const document={createElement:t=>new PhanTu(t)};
const chu=e=>e.textContent+e.children.map(chu).join(' ');
const tatCa=e=>[e,...e.children.flatMap(tatCa)];
const TEN='<img src=x onerror=alert(1)> Công ty DEMO không được lộ';
function giaLap() {
  const f={gia_tri:{thoi_han_anh_xa_giay:600},phien:4,ghi:[],doc:0,ngan:0};
  const engine={cau_hinh:{
    async doc() {
      f.doc++; if(f.loiDoc) throw new Error(TEN);
      return f.banDoc??{gia_tri:structuredClone(f.gia_tri),phien_ban_cau_hinh:f.phien};
    },
    async luu(gia_tri,phien) {
      f.ghi.push(structuredClone({gia_tri,phien})); if(f.hen) await f.hen;
      if(f.loiGhi) throw f.loiGhi;
      if(phien!==f.phien) throw {ma:'CAU_HINH_XUNG_DOT'};
      if(f.ack!==undefined) return f.ack;
      f.gia_tri=structuredClone(gia_tri); f.phien++;
      return {phien_ban_cau_hinh:f.phien};
    }
  },ngan:{async tim(b,k) {
    f.ngan++; assert.equal(b,'dinh_danh'); assert.equal(k.loc.trang_thai,'CHO_DUYET');
    if(f.loiNgan) throw new Error(TEN); return {danh_sach:[],tiep:null};
  },ghi_lo(){assert.fail('Không ghi ngăn');}},
  bi_mat:new Proxy({},{get(){assert.fail('Mask không dùng bí mật');}}),
  thao_tac(){assert.fail('Không gọi quản trị khi chỉ nạp cấu hình');}};
  f.goc=new PhanTu('main');
  f.KttCore={engine(ma){assert.equal(ma,'e_mask');return engine;}};
  f.man=taoMan({goc:f.goc,document,KttCore:f.KttCore});
  return f;
}

test('Đọc, thẻ chỉ đọc, gộp duyệt và không lộ dữ liệu',async()=>{
  const f=giaLap(); assert.equal(f.man.nutLuu.disabled,true);
  assert.equal(await f.man.nap(),true); assert.equal(f.ngan,1); assert.equal(f.doc,1);
  assert.equal(f.man.oThoiHan.value,'600'); assert.equal(f.man.nutLuu.disabled,false);
  assert.equal(tatCa(f.goc).filter(e=>e.ten==='input').length,1);
  for(const [ten,ma] of tienTo) {assert.ok(chu(f.goc).includes(ten));assert.ok(chu(f.goc).includes(ma));}
  for(const [ten,tep] of tuDien) {assert.ok(chu(f.goc).includes(ten));assert.ok(chu(f.goc).includes(tep));}
  assert.match(chu(f.goc),/Danh sách chờ duyệt/); assert.ok(!chu(f.goc).includes(TEN));
  assert.doesNotMatch(chu(f.goc),/\b(?:Anh|bạn)\b/u);
});
for(const n of [60,600,900]) test(`Lưu ${n} giây, CAS tăng phiên`,async()=>{
  const f=giaLap(); await f.man.doc(); f.man.oThoiHan.value=String(n);
  assert.equal(await f.man.luu(),true);
  assert.deepEqual(f.ghi,[{gia_tri:{thoi_han_anh_xa_giay:n},phien:4}]);
  assert.match(f.man.thongBao.textContent,/Đã lưu cấu hình/);
  f.man.oThoiHan.value='700'; assert.equal(await f.man.luu(),true); assert.equal(f.ghi[1].phien,5);
});
for(const v of ['', '59','901','60.5','-60','NaN','Infinity','6e2',' 600 ',TEN])
  test(`Lỗi nhập (${JSON.stringify(v)}) chỉ rõ trường, không gửi`,async()=>{
    const f=giaLap(); await f.man.doc(); f.man.oThoiHan.value=v; f.man.oThoiHan.events.input();
    assert.equal(await f.man.luu(),false); assert.equal(f.ghi.length,0);
    assert.match(f.man.loiO.textContent,/Thời hạn ánh xạ.*60.*900.*600/);
    assert.equal(f.man.oThoiHan.attributes['aria-invalid'],'true'); assert.ok(!chu(f.goc).includes(TEN));
    f.man.oThoiHan.value='600'; f.man.oThoiHan.events.input(); assert.equal(f.man.loiO.textContent,'');
  });
test('Chưa tải không lưu; cấu hình rỗng hợp lệ dùng 600, phiên 0',async()=>{
  const f=giaLap(); assert.equal(await f.man.luu(),false); assert.equal(f.ghi.length,0);
  f.gia_tri={}; f.phien=0; assert.equal(await f.man.doc(),true); assert.equal(f.man.oThoiHan.value,'600');
  assert.equal(await f.man.luu(),true); assert.equal(f.ghi[0].phien,0);
});
for(const loi of [{ma:'CAU_HINH_XUNG_DOT'},{ma:'NGAN_XUNG_DOT'},{status:409}])
  test('CAS tranh chấp giữ đầu vào, tải lại mới lưu tiếp',async()=>{
    const f=giaLap(); await f.man.doc(); f.man.oThoiHan.value='700'; f.loiGhi=loi;
    assert.equal(await f.man.luu(),false);
    assert.match(f.man.thongBao.textContent,/Cấu hình đã được người khác sửa, tải lại trước khi lưu/);
    assert.equal(f.man.oThoiHan.value,'700'); assert.equal(f.man.nutLuu.disabled,true);
    assert.equal(await f.man.luu(),false); assert.equal(f.ghi.length,1);
    f.loiGhi=null; f.gia_tri.thoi_han_anh_xa_giay=800; f.phien=9;
    await f.man.doc(); assert.equal(f.man.oThoiHan.value,'800');
    assert.equal(await f.man.luu(),true); assert.equal(f.ghi[1].phien,9);
  });
test('Tải lại thành công/thất bại; lỗi danh sách không khóa cấu hình',async()=>{
  const f=giaLap(); f.loiDoc=true; assert.equal(await f.man.nap(),false);
  assert.match(f.man.thongBao.textContent,/Không đọc được/); assert.equal(f.man.nutLuu.disabled,true);
  assert.ok(!chu(f.goc).includes(TEN)); f.loiDoc=false;
  await f.man.nutTaiLai.events.click(); assert.equal(f.man.nutLuu.disabled,false);
  f.loiNgan=true; assert.equal(await f.man.nap(),false); assert.equal(f.man.nutLuu.disabled,false);
  assert.ok(!chu(f.goc).includes(TEN));
});
for(const ban of [
  {gia_tri:null,phien_ban_cau_hinh:1},{gia_tri:{},phien_ban_cau_hinh:'1'},
  {gia_tri:{},phien_ban_cau_hinh:-1},{gia_tri:[],phien_ban_cau_hinh:1},
  {gia_tri:{thoi_han_anh_xa_giay:901},phien_ban_cau_hinh:1},
  {gia_tri:{thoi_han_anh_xa_giay:'600'},phien_ban_cau_hinh:1},
  {gia_tri:{thoi_han_anh_xa_giay:null},phien_ban_cau_hinh:1},
  {gia_tri:{cot_la:TEN},phien_ban_cau_hinh:1}])
  test('Bản đọc sai không dùng mặc định/làm mất trường',async()=>{
    const f=giaLap(); f.banDoc=ban; assert.equal(await f.man.doc(),false);
    assert.equal(await f.man.luu(),false); assert.equal(f.ghi.length,0); assert.ok(!chu(f.goc).includes(TEN));
  });
for(const ack of [null,{}, {phien_ban_cau_hinh:4},{phien_ban_cau_hinh:'5'}])
  test('Mất ACK không báo thành công, không tự gửi lại',async()=>{
    const f=giaLap(); await f.man.doc(); f.ack=ack;
    assert.equal(await f.man.luu(),false); assert.equal(await f.man.luu(),false);
    assert.equal(f.ghi.length,1); assert.match(f.man.thongBao.textContent,/Chưa xác nhận được/);
  });
test('Double click và lỗi nguồn không lộ nội dung',async()=>{
  const f=giaLap(); await f.man.doc(); let xong; f.hen=new Promise(r=>{xong=r;});
  const a=f.man.luu(); assert.equal(f.man.nutLuu.disabled,true);
  assert.equal(await f.man.luu(),false); assert.equal(await f.man.doc(),false);
  xong(); assert.equal(await a,true); assert.equal(f.ghi.length,1);
  f.loiGhi=new Error(TEN); assert.equal(await f.man.luu(),false); assert.ok(!chu(f.goc).includes(TEN));
});
test('Submit bằng bàn phím cùng đường kiểm/CAS',async()=>{
  const f=giaLap(); await f.man.doc(); let chan=false;
  const form=tatCa(f.goc).find(e=>e.ten==='form');
  assert.equal(await form.events.submit({preventDefault(){chan=true;}}),true);
  assert.equal(chan,true); assert.equal(f.ghi.length,1);
});
test('Điểm nạp module thay màn cũ và trả hàm dọn màn',async()=>{
  const f=giaLap(); f.goc.ownerDocument=document;
  const don=await nap({goc:f.goc,KttCore:f.KttCore});
  assert.equal(f.goc.children.length,1); assert.equal(f.doc,1); assert.equal(f.ngan,1);
  don(); assert.equal(f.goc.children.length,0);
});
test('Không mạng/eval/HTML/log/lưu máy/bí mật, CSS responsive và focus',async()=>{
  for(const ten of ['cau_hinh.js','duyet_dinh_danh.js']) {
    const code=await readFile(new URL(`../../goi/e_mask/ui/${ten}`,import.meta.url),'utf8');
    assert.doesNotMatch(code,/\b(?:fetch|XMLHttpRequest|WebSocket|eval|Function)\s*\(|innerHTML|console\.|localStorage|sessionStorage|\.bi_mat/);
  }
  const css=await readFile(new URL('../../goi/e_mask/ui/cau_hinh.css',import.meta.url),'utf8');
  assert.match(css,/@media\(max-width:720px\)/); assert.match(css,/focus-visible/);
});
