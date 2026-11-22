// DOM và Core trong RAM, dùng chung bộ kiểm Node và trang chụp DEMO.
export class PhanTu {
  constructor(tag, doc) {
    this.tagName = tag.toUpperCase(); this.ownerDocument = doc; this.children = [];
    this.parentNode = null; this.listeners = {}; this.attrs = {}; this._text = "";
    this.value = ""; this.checked = false; this.disabled = false; this.className = "";
    this.classList = {add: x => { this.className = [...new Set([...this.className.split(" "), x])].join(" ").trim(); },
      remove: x => { this.className = this.className.split(" ").filter(y => x !== y).join(" "); }};
  }
  appendChild(e) { e.parentNode = this; this.children.push(e); return e; }
  replaceChildren(...es) { for (const e of this.children) e.parentNode = null; this.children = []; this._text = ""; for (const e of es) this.appendChild(e); }
  set textContent(v) { this.replaceChildren(); this._text = String(v); }
  get textContent() { return this._text + this.children.map(e => e.textContent).join(" "); }
  setAttribute(k, v) { this.attrs[k] = String(v); }
  getAttribute(k) { return this.attrs[k] ?? null; }
  addEventListener(k, f) { (this.listeners[k] ??= []).push(f); }
  querySelector(s) { return tatCa(this).find(e => khop(e, s)) ?? null; }
}
function khop(e, s) {
  const m = /^\[([^=\]]+)(?:="([^"]*)")?\]$/.exec(s);
  return m ? Object.hasOwn(e.attrs, m[1]) && (m[2] === undefined || e.attrs[m[1]] === m[2]) : e.tagName.toLowerCase() === s;
}
export const tatCa = e => [e, ...e.children.flatMap(tatCa)];
export function taoGoc() { const doc = {createElement: t => new PhanTu(t, doc)}; return new PhanTu("main", doc); }
export function nut(goc, ten, so = 0) { const e = tatCa(goc).filter(x => x.tagName === "BUTTON" && x.textContent === ten)[so]; if (!e) throw new Error("Không tìm thấy nút " + ten); return e; }
export function oNhap(goc, duongDan) { const e = goc.querySelector(`[data-o="${duongDan}"]`); if (!e) throw new Error("Không tìm thấy ô " + duongDan); return e; }
export async function phat(e, suKien, giaTri) {
  if (giaTri !== undefined) { if (e.type === "checkbox") e.checked = giaTri; else e.value = giaTri; }
  if (suKien === "click") { let x = e; while (x) { if (x.disabled) return; x = x.parentNode; } }
  for (const f of e.listeners[suKien] ?? []) await f({preventDefault() {}, target: e});
}
const chep = v => JSON.parse(JSON.stringify(v));
export function taoCoreGia(thamSo, phien = 7) {
  const core = {tham_so: chep(thamSo), phien, goi: [], loi_doc: null, loi_luu: null, cho_luu: null};
  const cam = () => { throw new Error("Không gọi cấu hình, ngăn, thao tác hoặc bí mật cho tham số bước."); };
  core.KttCore = {engine(ma) { if (ma !== "e_phan_luong") throw new Error("Sai engine.");
    core.goi.push(["engine", ma]); return {cau_hinh: {doc: cam, luu: cam}, ngan: {doc: cam, tim: cam, ghi_lo: cam}, thao_tac: cam, bi_mat: cam}; }};
  core.doc_tham_so = async () => { core.goi.push(["doc"]); if (core.loi_doc) throw core.loi_doc;
    return {tham_so: chep(core.tham_so), phien_ban_tham_so: core.phien}; };
  core.luu_tham_so = async (v, phienBan) => {
    core.goi.push(["luu", chep(v), phienBan]); if (core.cho_luu) await core.cho_luu;
    if (core.loi_luu) throw core.loi_luu;
    if (phienBan !== core.phien) throw {status: 409, ma: "NGAN_XUNG_DOT"};
    core.tham_so = chep(v); return {phien_ban_tham_so: ++core.phien};
  };
  return core;
}
