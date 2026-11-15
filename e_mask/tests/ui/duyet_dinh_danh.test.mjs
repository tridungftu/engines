// KttCore giả, không mạng; cửa C-P4-06 chỉ là adapter test ngoài gói.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
const code = await readFile(new URL('../../goi/e_mask/ui/duyet_dinh_danh.js', import.meta.url), 'utf8');
const { taoMan } = await import(`data:text/javascript;base64,${Buffer.from(code).toString('base64')}`);
const ID = 'a'.repeat(32), ID2 = 'b'.repeat(32), TOKEN = 'c'.repeat(32);
const TEN = '<img src=x onerror=alert(1)> Công ty DEMO Ánh Dương';
class PhanTu {
  constructor(ten) { this.ten=ten; this.children=[]; this.textContent=''; this.value=''; this.events={}; }
  append(...con) { this.children.push(...con); }
  replaceChildren(...con) { this.children=con; }
  addEventListener(ten, ham) { this.events[ten]=ham; }
  setAttribute(k,v) { this[k]=v; }
  set innerHTML(v) { throw new Error('Cấm chèn HTML'); }
}
const document = { createElement: (t) => new PhanTu(t) };
const chu = (e) => e.textContent + e.children.map(chu).join('');
function giaLap() {
  const f = { xem: true, duyet: true, admin: true, xungDot: false, coCua: true,
    veSai: null, ackSai: undefined, lenh: [], tim: [], alias: new Set(), ve: new Map() };
  f.dong = { gia_tri: {id_dinh_danh:ID, vung_du_lieu:'DEMO', nhom:'CONG_TY',
    trang_thai:'CHO_DUYET', so_gap:'2', gia_tri_goc:null, gia_tri_chuan:null,
    gia_tri_goc_da_ma_hoa:true, gia_tri_chuan_da_ma_hoa:true, cot_la:TEN}, row_version:1 };
  const n = { async tim(b,kw) {
    assert.equal(b,'dinh_danh'); assert.deepEqual(kw.loc,{trang_thai:'CHO_DUYET'});
    assert.equal(kw.gioi_han,100); f.tim.push(structuredClone(kw));
    if (!f.admin) throw {ma:'CAM', message:TEN};
    return {danh_sach: f.dong.gia_tri.trang_thai==='CHO_DUYET'?[structuredClone(f.dong)]:[],tiep:null};
  }, async ghi_lo() { assert.fail('UI không được ghi ngăn'); } };
  async function thao_tac(ma,dl) {
    if (!f.coCua) throw new Error(TEN);
    f.lenh.push(structuredClone({ma,dl}));
    assert.equal(dl.id_dinh_danh,ID); assert.equal(dl.bang,'dinh_danh');
    assert.equal(dl.vung_du_lieu,'DEMO');
    if (!f.admin || !f.xem) throw {ma:'CAM',message:TEN};
    if (ma==='xem_du_lieu') {
      if (f.hen) await f.hen;
      if (dl.row_version!==f.dong.row_version) throw {ma:'MASK_XUNG_DOT'};
      f.ve.set(TOKEN, dl.row_version);
      return f.veSai ?? {id_dinh_danh:ID,row_version:dl.row_version,bien_nhan:TOKEN};
    }
    assert.equal(ma,'quyet_dinh_duyet');
    if (!f.duyet || f.ve.get(dl.bien_nhan)!==dl.row_version) throw {ma:'CAM',message:TEN};
    f.ve.delete(dl.bien_nhan);
    if (f.xungDot || dl.row_version!==f.dong.row_version) throw {ma:'NGAN_XUNG_DOT'};
    const alias = dl.quyet_dinh==='DUYET' ? `[[${dl.ma_junsky || 'MASKCT-0001'}]]` : null;
    if (alias && f.alias.has(alias.toLowerCase())) throw {ma:'MASK_XUNG_DOT'};
    if(alias) f.alias.add(alias.toLowerCase());
    f.dong.row_version++;
    f.dong.gia_tri.trang_thai = dl.quyet_dinh==='DUYET'?'CHINH_THUC':'TU_CHOI';
    const kq={id_dinh_danh:ID,bi_danh:alias,trang_thai:f.dong.gia_tri.trang_thai};
    return f.ackSai === undefined ? kq : f.ackSai;
  }
  f.KttCore={engine(ma){assert.equal(ma,'e_mask');return {ngan:n, thao_tac};}};
  f.goc=new PhanTu('main'); f.man=taoMan({KttCore:f.KttCore,goc:f.goc,document});
  f.muc={id_dinh_danh:ID,row_version:1};
  return f;
}
function khongTen(f) {
  assert.ok(!chu(f.goc).includes(TEN));
  assert.ok(!JSON.stringify(f.lenh).includes(TEN));
  assert.ok(!JSON.stringify(f.tim).includes(TEN));
}

test('Duyệt qua KttCore, chỉ metadata và biên nhận; cùng ID không HTML/lọc tên',async()=>{
  const f=giaLap(); assert.equal(await f.man.nap(),true);
  assert.equal(f.man.loc,undefined); assert.equal(f.man.don,undefined);
  assert.ok(chu(f.goc).includes(ID)); khongTen(f);
  assert.equal(await f.man.duyet(f.muc,'KH-DEMO-001'),false); assert.equal(f.lenh.length,0);
  assert.equal(await f.man.xem(f.muc),true);
  assert.equal(await f.man.duyet(f.muc,'KH-DEMO-001'),true);
  assert.equal(f.dong.gia_tri.trang_thai,'CHINH_THUC'); assert.equal(f.dong.row_version,2);
  assert.equal(f.dong.gia_tri.gia_tri_goc,null); assert.equal(f.dong.gia_tri.gia_tri_goc_da_ma_hoa,true);
  assert.equal(f.lenh[1].dl.ma_junsky,'KH-DEMO-001'); khongTen(f);
  assert.equal(await f.man.duyet(f.muc),false); // Replay, không gửi lần hai.
  assert.equal(f.lenh.length,2);
});

test('CAS lỗi hiện câu tiếng Việt, mất vé và không ghi nửa lô',async()=>{
  const f=giaLap(); await f.man.nap(); await f.man.xem(f.muc); f.xungDot=true;
  assert.equal(await f.man.duyet(f.muc),false);
  assert.match(f.man.thongBao.textContent,/vừa thay đổi/);
  assert.equal(f.dong.gia_tri.trang_thai,'CHO_DUYET'); assert.equal(f.alias.size,0);
  assert.equal(await f.man.duyet(f.muc),false); assert.equal(f.lenh.length,2); khongTen(f);
});

test('Từ chối bằng trạng thái, quyền bị thu hồi chặn ghi',async()=>{
  const f=giaLap(); await f.man.nap(); await f.man.xem(f.muc);
  f.duyet=false; assert.equal(await f.man.tuChoi(f.muc),false);
  assert.equal(f.dong.gia_tri.trang_thai,'CHO_DUYET'); khongTen(f);
  f.duyet=true; await f.man.xem(f.muc); assert.equal(await f.man.tuChoi(f.muc),true);
  assert.equal(f.dong.gia_tri.trang_thai,'TU_CHOI'); assert.equal(f.dong.gia_tri.gia_tri_chuan,null);
});

test('Từ chối Junsky trùng tiền tố MASK, mã tự sinh qua cửa Core đúng nhóm',async()=>{
  const f=giaLap(); await f.man.nap(); await f.man.xem(f.muc);
  assert.equal(await f.man.duyet(f.muc,'MASKCT-DEMO'),false);
  await f.man.xem(f.muc); assert.equal(await f.man.duyet(f.muc),true);
  assert.ok(f.alias.has('[[maskct-0001]]'));
});

for (const thieu of ['cua','xem','duyet','admin','phien']) test(`Thiếu ${thieu} giữ chờ và không lộ tên`,async()=>{
  const f=giaLap(); await f.man.nap();
  if(thieu==='cua') f.coCua=false;
  else if(thieu==='xem') f.xem=false;
  if(['cua','xem'].includes(thieu)) assert.equal(await f.man.xem(f.muc),false);
  else {
    await f.man.xem(f.muc);
    if(thieu==='phien') f.dong.row_version++; else f[thieu]=false;
    assert.equal(await f.man.duyet(f.muc),false);
  }
  assert.equal(f.dong.gia_tri.trang_thai,'CHO_DUYET'); khongTen(f);
});

test('SDK chỉ có ngăn thì thiếu cửa Core, không fallback ghi ngăn',async()=>{
  const f=giaLap(); const engine=f.KttCore.engine('e_mask'); delete engine.thao_tac;
  const man=taoMan({KttCore:{engine:()=>engine},goc:new PhanTu('main'),document});
  await man.nap(); assert.equal(await man.xem(f.muc),false); assert.equal(await man.duyet(f.muc),false);
  assert.equal(f.lenh.length,0);
});

for (const v of [{id_dinh_danh:ID2,row_version:1,bien_nhan:TOKEN},
  {id_dinh_danh:ID,row_version:2,bien_nhan:TOKEN},
  {id_dinh_danh:ID,row_version:1,bien_nhan:TOKEN,ten:TEN},
  {id_dinh_danh:ID,row_version:1,bien_nhan:TOKEN,da_xem:true},
  {id_dinh_danh:ID,row_version:true,bien_nhan:TOKEN}]) test('Vé sai ID/phiên bản/tên/cờ không duyệt mù',async()=>{
  const f=giaLap(); f.veSai=v; await f.man.nap(); assert.equal(await f.man.xem(f.muc),false);
  assert.equal(await f.man.duyet(f.muc),false); assert.equal(f.lenh.length,1); khongTen(f);
});

for(const gia_tri of [{gia_tri_goc:TEN}, {nhom:TEN}, {id_dinh_danh:TEN}, {so_gap:TEN},
  {gia_tri_chuan_da_ma_hoa:false}]) test('Metadata sai hoặc bí mật trả bản rõ chặn cả trang',async()=>{
  const f=giaLap(); Object.assign(f.dong.gia_tri,gia_tri);
  assert.equal(await f.man.nap(),false); assert.ok(!chu(f.goc).includes(ID)); khongTen(f);
});

test('Tải lại vô hiệu vé; alias trùng không ghi; mã XSS không tới cửa Core',async()=>{
  const f=giaLap(); await f.man.nap(); await f.man.xem(f.muc); await f.man.nap();
  assert.equal(await f.man.duyet(f.muc),false); assert.equal(f.lenh.length,1);
  await f.man.xem(f.muc); assert.equal(await f.man.duyet(f.muc,TEN),false); khongTen(f);
  f.alias.add('[[kh-demo-001]]'); await f.man.xem(f.muc);
  assert.equal(await f.man.duyet(f.muc,'KH-DEMO-001'),false);
  assert.equal(f.dong.gia_tri.trang_thai,'CHO_DUYET');
});

test('Double click chỉ một cửa xem; lỗi nguồn/tên không console hay DOM',async()=>{
  const f=giaLap(); await f.man.nap(); let xong;
  f.hen=new Promise((r)=>{xong=r;}); const a=f.man.xem(f.muc);
  assert.equal(await f.man.xem(f.muc),false); xong(); assert.equal(await a,true);
  assert.equal(f.lenh.length,1); khongTen(f);
});

for(const ack of [null, false, {id_dinh_danh:ID,bi_danh:'[[KH-DEMO]]',trang_thai:'CHINH_THUC',ten:TEN}])
  test('Thiếu xác nhận không báo thành công hoặc tự gửi lại',async()=>{
    const f=giaLap(); f.ackSai=ack; await f.man.nap(); await f.man.xem(f.muc);
    assert.equal(await f.man.duyet(f.muc),false); assert.equal(await f.man.duyet(f.muc),false);
    assert.equal(f.lenh.length,2); khongTen(f);
  });

test('Mã màn chỉ gọi Core, không mạng/eval/HTML chưa lọc/log',()=>{
  assert.doesNotMatch(code,/\b(?:fetch|XMLHttpRequest|WebSocket|eval|Function)\s*\(|innerHTML|console\./);
  assert.doesNotMatch(code,/ghi_lo|gia_tri.*includes|localStorage|sessionStorage/);
});
