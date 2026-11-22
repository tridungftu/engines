// DOM và cửa nhúng bước D2 giả, chỉ ở bộ nhớ Node; không mở mạng.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
export const gocGoi = new URL('../../goi/e_kiem_excel/', import.meta.url);
export const dataUrl = s => `data:text/javascript;base64,${Buffer.from(s).toString('base64')}`;
const duLieu = await readFile(new URL('ui/du_lieu.js', gocGoi), 'utf8');
const css = await readFile(new URL('ui/kieu_dang.js', gocGoi), 'utf8');
export const nguon = await readFile(new URL('ui/tham_so.js', gocGoi), 'utf8');
export const moduleUrl = dataUrl(nguon.replace("'./du_lieu.js'", JSON.stringify(dataUrl(duLieu))).replace("'./kieu_dang.js'", JSON.stringify(dataUrl(css))));
export const {default: nap} = await import(moduleUrl);
export const dulieu = await import(dataUrl(duLieu));
export class PhanTu {
  constructor(the, doc) {
    this.the = the; this.ownerDocument = doc; this.con = []; this.suKien = {};
    this.thuocTinh = {}; this.value = ''; this._chu = ''; this.disabled = false;
    this.classList = {add: c => { this.className = c; }};
  }
  set textContent(v) { this._chu = String(v); this.con = []; }
  get textContent() { return this._chu + this.con.map(x => x.textContent).join(' '); }
  appendChild(el) { this.con.push(el); el.cha = this; return el; }
  replaceChildren(...xs) { this._chu = ''; this.con = []; xs.forEach(x => this.appendChild(x)); }
  setAttribute(k,v) { this.thuocTinh[k] = v; }
  addEventListener(k, fn) { (this.suKien[k] ??= []).push(fn); }
  async goi(k) { for (const fn of this.suKien[k] || []) await fn({preventDefault(){}}); }
}
export function dom() { const doc = {createElement: t => new PhanTu(t,doc)}; return new PhanTu('main',doc); }
export function tatCa(el) { return [el, ...el.con.flatMap(tatCa)]; }
export function tim(goc, the, chu, stt = 0) {
  const ds = tatCa(goc).filter(x => x.the === the && (chu === undefined || x.textContent === chu));
  assert.ok(ds[stt], `Không tìm thấy ${the}: ${chu}`); return ds[stt];
}
export function oNhap(goc, nhan, stt = 0) {
  const l = tim(goc,'label',nhan,stt); return tatCa(goc).find(x => x.id === l.htmlFor);
}
export async function nhap(goc, nhan, v, stt = 0) {
  const el = oNhap(goc,nhan,stt); el.value = v; await el.goi(el.the === 'select' ? 'change' : 'input');
}
export async function bam(goc, chu, stt = 0) {
  const b = tim(goc,'button',chu,stt); assert.equal(b.disabled,false,`${chu} bị khóa`); await b.goi('click');
}
export const DEMO = {o_dich:'BTH!J39', kiem_nguon_kl:true,
  bo_nhom_json:JSON.stringify(dulieu.MAU.bo_nhom_json), nhan_o_dich_json:JSON.stringify(dulieu.MAU.nhan_o_dich_json)};
export function coreGia({tham_so = DEMO, ds_sheet = ['BTH',"Sheet DEMO's"], loiDoc = false, loiLuu = false, xungDot = false, tre = null, phien = 7} = {}) {
  const daLuu = []; let dang = structuredClone(tham_so), phienBan = phien;
  const KttCore = {engine(ma) {
    assert.equal(ma,'e_kiem_excel');
    return new Proxy({}, {get() { throw Error('TS-EX không dùng cấu hình, ngăn, thao tác hay bí mật engine.'); }});
  }};
  // Core quản lý quy trình gọi các callback này; không phải API engine mới.
  const nguCanh = {nang_luc:'excel.toan_ven@1',
    async doc() {
      if (loiDoc) throw Error('DEMO_bi_mat_123456789');
      return {tham_so:structuredClone(dang), ds_sheet, phien_ban:phienBan};
    },
    async luu(ts, rv) {
      daLuu.push({tham_so:structuredClone(ts), phien_ban:rv});
      if (tre) await tre;
      if (xungDot || rv !== phienBan) throw {status:409, ma:'THAM_SO_XUNG_DOT', message:'DEMO_bi_mat_123456789'};
      if (loiLuu) throw Error('DEMO_bi_mat_123456789');
      dang = structuredClone(ts); return {phien_ban:++phienBan};
    }};
  return {KttCore, nguCanh, daLuu, doiNgoai() { phienBan++; }};
}
