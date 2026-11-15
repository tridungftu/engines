// KttCore giả, không mạng; kiểm CAS cả lô, lọc và không chèn HTML.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import { webcrypto } from 'node:crypto';

globalThis.crypto ??= webcrypto;
const code = await readFile(new URL('../../goi/e_mask/ui/duyet_dinh_danh.js', import.meta.url), 'utf8');
const { taoMan } = await import(`data:text/javascript;base64,${Buffer.from(code).toString('base64')}`);

class PhanTu {
  constructor(ten) { this.ten=ten; this.children=[]; this.textContent=''; this.value=''; this.events={}; }
  append(...con) { this.children.push(...con); }
  replaceChildren(...con) { this.children=con; }
  addEventListener(ten, ham) { this.events[ten]=ham; }
  setAttribute() {}
  set innerHTML(v) { throw new Error('Cấm chèn HTML'); }
}
const document = { createElement: (t) => new PhanTu(t) };
const khoa = (k) => JSON.stringify(Object.entries(k).sort());
function giaLap() {
  let phien=0;
  let bang=Object.fromEntries(['cho_duyet','dinh_danh','bi_danh_tam','ma_yeu_cau','dau_gap'].map((b)=>[b,new Map()]));
  let choPhep=true, xungDot=false;
  const them = (b,k,v) => bang[b].set(khoa(k), {gia_tri:{...v,...k},row_version:++phien});
  const n = {
    async doc(b,k) { if(!choPhep) throw {ma:'CAM'}; return structuredClone(bang[b].get(khoa(k)) ?? null); },
    async tim(b,{loc={},gioi_han=500,tiep=null}) {
      if(!choPhep) throw {ma:'CAM'};
      const ds=[...bang[b].values()].filter((m)=>Object.entries(loc).every(([k,v])=>m.gia_tri[k]===v));
      const dau=Number(tiep||0),cuoi=dau+gioi_han;
      return {danh_sach:structuredClone(ds.slice(dau,cuoi)),tiep:cuoi<ds.length?String(cuoi):null};
    },
    async ghi_lo({lenh}) {
      if(!choPhep) throw {ma:'CAM'};
      if(xungDot) throw {ma:'NGAN_XUNG_DOT'};
      assert.ok(lenh.length<=100);
      const moi=structuredClone(bang);
      for(const l of lenh) {
        const k=khoa(l.khoa),cu=moi[l.bang].get(k);
        if(l.thao_tac==='them' ? !!cu : !cu || cu.row_version!==l.row_version) throw {ma:'NGAN_XUNG_DOT'};
        if(l.thao_tac==='xoa') moi[l.bang].delete(k);
        else moi[l.bang].set(k,{gia_tri:{...l.gia_tri,...l.khoa},row_version:++phien});
      }
      bang=moi;
    },
  };
  them('dau_gap',{vung:'DEMO',khoa:'phien'},{so:0});
  them('cho_duyet',{vung:'DEMO',khoa:'demo'},{gia_tri:'<img src=x onerror=alert(1)> DEMO',nhom:'CONG_TY',bi_danh:'[[MASKTAM-DEMO]]',nguon:'tam',so_lan_gap:2});
  them('bi_danh_tam',{vung:'DEMO',khoa:'[[masktam-demo]]'},{gia_tri:'Tên DEMO',nhom:'CONG_TY',bi_danh:'[[MASKTAM-DEMO]]',nguon:'tam'});
  them('ma_yeu_cau',{vung:'DEMO',khoa:'yc-demo'},{trang_thai:'DANG_XU_LY'});
  them('dau_gap',{vung:'DEMO',khoa:'tham-chieu-demo'},{loai_dau:'tham_chieu',ma_yeu_cau:'yc-demo',bi_danh:'[[masktam-demo]]'});
  const KttCore={engine(ma){assert.equal(ma,'e_mask');return{ngan:n};}};
  return {n,KttCore,them,cam(){choPhep=false;},xung(){xungDot=true;},xem(){return bang;}};
}

test('Duyệt qua KttCore, cấp alias, giữ mã tạm và lọc cột',async()=>{
  const f=giaLap(),goc=new PhanTu('main');
  const man=taoMan({KttCore:f.KttCore,goc,document}); await man.nap();
  const bang=goc.children[0].children[3];
  assert.equal(bang.children.length,2);
  assert.ok(bang.children[1].children[0].textContent.startsWith('<img'));
  man.loc.gia_tri.value='không có'; man.loc.gia_tri.events.input(); assert.equal(bang.children.length,1);
  man.loc.gia_tri.value=''; man.loc.gia_tri.events.input();
  const muc=(await f.n.tim('cho_duyet',{})).danh_sach[0];
  assert.equal(await man.duyet(muc,'KH-DEMO-001'),true);
  assert.equal((await f.n.tim('cho_duyet',{})).danh_sach.length,0);
  const chinh=(await f.n.tim('dinh_danh',{})).danh_sach[0].gia_tri;
  assert.equal(chinh.bi_danh,'[[KH-DEMO-001]]'); assert.equal(chinh.bi_danh_tam,'[[MASKTAM-DEMO]]');
  await man.don('DEMO'); assert.equal((await f.n.tim('bi_danh_tam',{})).danh_sach.length,1);
  const yc=await f.n.doc('ma_yeu_cau',{vung:'DEMO',khoa:'yc-demo'});
  await f.n.ghi_lo({lenh:[{thao_tac:'sua',bang:'ma_yeu_cau',khoa:{vung:'DEMO',khoa:'yc-demo'},gia_tri:{trang_thai:'DA_DONG'},row_version:yc.row_version}]});
  await man.don('DEMO'); assert.equal((await f.n.tim('bi_danh_tam',{})).danh_sach.length,0);
});

test('CAS lỗi hiện câu tiếng Việt và không ghi nửa lô',async()=>{
  const f=giaLap(),man=taoMan({KttCore:f.KttCore,goc:new PhanTu('main'),document}); await man.nap();
  const muc=(await f.n.tim('cho_duyet',{})).danh_sach[0]; f.xung();
  assert.equal(await man.duyet(muc),false);
  assert.match(man.thongBao.textContent,/vừa thay đổi/);
  assert.equal((await f.n.tim('dinh_danh',{})).danh_sach.length,0);
  assert.equal((await f.n.tim('cho_duyet',{})).danh_sach.length,1);
});

test('Từ chối giữ alias đang dùng; quyền bị thu hồi chặn ghi',async()=>{
  const f=giaLap(),man=taoMan({KttCore:f.KttCore,goc:new PhanTu('main'),document}); await man.nap();
  const muc=(await f.n.tim('cho_duyet',{})).danh_sach[0];
  assert.equal(await man.tuChoi(muc),true); await man.don('DEMO');
  assert.equal((await f.n.tim('bi_danh_tam',{})).danh_sach.length,1);
  f.cam(); assert.equal(await man.tuChoi(muc),false);
  assert.match(man.thongBao.textContent,/quyền quản trị/);
});

test('Từ chối Junsky trùng tiền tố MASK, mã tự sinh đúng nhóm',async()=>{
  const f=giaLap(),man=taoMan({KttCore:f.KttCore,goc:new PhanTu('main'),document}); await man.nap();
  const muc=(await f.n.tim('cho_duyet',{})).danh_sach[0];
  assert.equal(await man.duyet(muc,'MASKCT-DEMO'),false);
  assert.equal(await man.duyet(muc),true);
  assert.match((await f.n.tim('dinh_danh',{})).danh_sach[0].gia_tri.bi_danh,/^\[\[MASKCT-[a-f0-9]+\]\]$/);
});
