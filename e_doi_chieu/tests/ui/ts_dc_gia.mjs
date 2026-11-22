// Chỉ DEMO, CoreGia cho cửa D2 trong RAM; không mạng hoặc lưu tệp từ màn.
export const BO_DEMO = {phien_ban: 1, phien_ban_bo: "DEMO-1", ma_bo_chuan_hoa: "DEMO-NFC-1",
  chuan_hoa: {unicode: "NFC", khoang_trang: "gop", dau_nhay: "thang", gach_noi: "thong_nhat",
    ngat_dong: "noi_trong_doan", ngat_tu_cuoi_dong: "chi_gach_noi_mem", dau_chan_trang: [], bo_so_trang: false},
  quy_tac_cung: {phien_ban: 1, dinh_dang_so: [{nghin: ".", thap_phan: ","}],
    don_vi_tien: {VND: "VND", "đồng": "VND"}, dinh_dang_ngay: ["YYYY-MM-DD"], vung_bao_ve: []},
  lech_dau: {phien_ban: 1, ghi_chu_demo: "Phần đã ghim được giữ nguyên"}};

export function coreGia() {
  return {engine(ma) {
    if (ma !== "e_doi_chieu") throw Error("Sai engine DEMO");
    return new Proxy({}, {get() {throw Error("Trình soạn không đọc/ghi cấu hình, ngăn hoặc bí mật engine");}});
  }};
}
export function cuaGia(thamSo, mode = {}) {
  let phienBan = 7, data = structuredClone(thamSo);
  const calls = [];
  const cua = {
    async doc() {calls.push(["doc"]); if (mode.loiDoc) throw Error("DEMO-chi-tiet-khong-lo"); return {tham_so: structuredClone(data), phien_ban: phienBan};},
    async luu(y) {
      calls.push(["luu", structuredClone(y)]);
      if (mode.cho) await mode.cho;
      if (mode.xungDot) throw {status: 409, message: "DEMO-chi-tiet-khong-lo"};
      if (mode.loiLuu) throw Error("DEMO-chi-tiet-khong-lo");
      if (y.phien_ban !== phienBan) throw {ma: "BUOC_XUNG_DOT"};
      // Chỉ gộp hai tham số của TS-DC, giữ các tham số bước khác.
      data = {...data, ...structuredClone(y.tham_so)}; phienBan++;
      return mode.matAck ? {} : {da_luu: true, phien_ban: phienBan};
    },
  };
  return {cua, calls, xem: () => ({tham_so: structuredClone(data), phien_ban: phienBan}), mode};
}

export class PhanTu {
  constructor(the, doc) {
    this.the = the; this.ownerDocument = doc; this.con = []; this.events = {}; this.attrs = {};
    this.value = ""; this.disabled = false; this._text = "";
    this.classList = {add() {}};
  }
  set textContent(s) {this._text = String(s); this.con = [];}
  get textContent() {return this._text;}
  set innerHTML(_) {throw Error("Cấm HTML");}
  appendChild(e) {this.con.push(e); return e;}
  replaceChildren() {this.con = []; this._text = "";}
  setAttribute(k, v) {this.attrs[k] = v;}
  addEventListener(k, f) {this.events[k] = f;}
  querySelectorAll(selector) {const tags = selector.split(","); return tatCa(this).slice(1).filter(e => tags.includes(e.the));}
  async goi(k) {if (this.disabled) return; await this.events[k]?.({preventDefault() {}});}
}
export const tatCa = e => [e, ...e.con.flatMap(tatCa)];
export const chu = e => e.textContent + " " + e.con.map(chu).join(" ");
export const nut = (e, ten) => tatCa(e).find(x => x.the === "button" && x.textContent === ten);
export const oNhap = (e, ten) => tatCa(e).find(x => x.attrs["aria-label"] === ten);
export function gocGia() {const doc = {createElement: t => new PhanTu(t, doc)}; return doc.createElement("main");}
