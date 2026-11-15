// DOM tối thiểu và KttCore giả; không mô phỏng quyền Admin toàn engine.
import assert from "node:assert/strict";

export class Nut {
  constructor(tag, doc) {this.tagName = tag; this.ownerDocument = doc; this.children = []; this.listeners = new Map(); this.value = ""; this.disabled = false; this.text = "";}
  set textContent(v) {this.text = String(v); this.children = [];}
  get textContent() {return this.text + this.children.map(c => c.textContent).join("\n");}
  set innerHTML(_) {throw new Error("Không được dựng HTML từ chuỗi.");}
  appendChild(c) {this.children.push(c); return c;}
  replaceChildren(...cs) {this.text = ""; this.children = cs;}
  setAttribute(k, v) {this[k] = v;}
  addEventListener(k, fn) {this.listeners.set(k, fn);}
  removeEventListener(k, fn) {if (this.listeners.get(k) === fn) this.listeners.delete(k);}
  async fire(k) {if (!this.disabled) await this.listeners.get(k)?.({preventDefault() {}});}
  all() {return [this, ...this.children.flatMap(c => c.all())];}
  ten(v) {return this.all().find(n => n.name === v);}
  nut(v) {return this.all().find(n => n.tagName === "button" && n.textContent === v);}
}
export function goc() {const d = {createElement: tag => new Nut(tag, d)}; return new Nut("main", d);}
export function cauHinh() {return {phien_ban: 1, quy_tac_nhom: {tep_id: "tep-DEMO", bam: "sha256:" + "a".repeat(64)}};}
export function ban(p = "DEMO-P", ma = "DEMO-1") {
  return {gia_tri: {phap_nhan_id: p, ma_dot: ma, trang_thai: "chua_do", chi_so: JSON.stringify({tra_loi_dung: null}), bao_cao: null}, row_version: 1};
}
export function coreGia({cau_hinh = cauHinh(), phap_nhan = ["DEMO-P"], cacBan = [ban()], kichThuocTrang = 500} = {}) {
  let c = structuredClone(cau_hinh), phien = c == null ? null : 1;
  const quyen = new Set(phap_nhan), cursors = new Map();
  const goi = [], luu = [], engines = [];
  let loiDoc = null, loiTim = null, loiChiTiet = null, loiLuu = null, soCursor = 0;
  function cam() {throw Object.assign(new Error("DEMO path/noi-dung-khong-duoc-hien"), {ma: "KHONG_DU_QUYEN", status: 403});}
  function kiem(bang, scope) {
    assert.equal(bang, "dot_kiem");
    if (!scope || Object.hasOwn(scope, "phap_nhan_id") || !quyen.has(phap_nhan[0])) cam();
  }
  const cong = {
    cau_hinh: {
      async doc() {if (loiDoc) throw loiDoc; return c == null ? null : structuredClone({gia_tri: c, phien_ban_cau_hinh: phien});},
      async luu(v, ver) {
        luu.push(structuredClone({v, ver}));
        if (loiLuu) throw loiLuu;
        if (ver !== phien) throw Object.assign(new Error("DEMO noi-dung-rieng"), {ma: "NGAN_XUNG_DOT", status: 409});
        c = structuredClone(v); phien = (phien ?? 0) + 1;
        return {phien_ban_cau_hinh: phien};
      },
    },
    ngan: {
      async tim(bang, opts) {
        goi.push(["tim", bang, structuredClone(opts)]); kiem(bang, opts.loc);
        assert.ok(Number.isInteger(opts.gioi_han) && opts.gioi_han > 0 && opts.gioi_han <= 500);
        if (loiTim) throw loiTim;
        const nhan = JSON.stringify([bang, phap_nhan[0], opts.loc]);
        let offset = 0;
        if (opts.tiep != null) {
          const saved = cursors.get(opts.tiep);
          if (!saved || saved.nhan !== nhan) cam();
          offset = saved.offset;
        }
        const ds = cacBan.filter(b => b.gia_tri.phap_nhan_id === phap_nhan[0]);
        const dem = Math.min(kichThuocTrang, opts.gioi_han);
        let tiep = null;
        if (offset + dem < ds.length) {
          tiep = `DEMO-cursor-${++soCursor}`;
          cursors.set(tiep, {nhan, offset: offset + dem});
        }
        return structuredClone({danh_sach: ds.slice(offset, offset + dem), tiep});
      },
      async doc(bang, khoa) {
        goi.push(["doc", bang, structuredClone(khoa)]); kiem(bang, khoa);
        if (loiChiTiet) throw loiChiTiet;
        return structuredClone(cacBan.find(b => b.gia_tri.phap_nhan_id === phap_nhan[0] && b.gia_tri.ma_dot === khoa.ma_dot) ?? null);
      },
      async ghi_lo() {throw new Error("Màn trạng thái không được ghi.");},
    },
  };
  return {cong, goi, luu, engines, quyen, cursors,
    KttCore: {engine(ma) {assert.equal(ma, "e_tra_cuu"); engines.push(ma); return cong;}},
    doiCauHinh(v) {c = structuredClone(v); phien = (phien ?? 0) + 1;},
    loi({doc = null, tim = null, chiTiet = null, ghi = null}) {loiDoc = doc; loiTim = tim; loiChiTiet = chiTiet; loiLuu = ghi;},
  };
}

globalThis.fetch = () => {throw new Error("Test không được gọi mạng.");};
globalThis.XMLHttpRequest = class {constructor() {throw new Error("Test không được gọi mạng.");}};
globalThis.WebSocket = class {constructor() {throw new Error("Test không được gọi mạng.");}};
