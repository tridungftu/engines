// DEMO trong RAM: không dùng thư viện ngoài hoặc mạng.
import assert from 'node:assert/strict';
export const DEMO = {local_ai:{url:'http://127.0.0.1:11434',timeout_giay:60},
  quy_tac_model:[{mau_ma_prompt:'demo.*',uu_tien:'model-demo',du_phong:['model-demo-b']}]};
export const MODELS = [{id_model:'model-demo',kha_dung:true},{id_model:'model-demo-b',kha_dung:true}];
export function taoCore(tuyChon = {}) {
  const daLuu = [], daTim = [], daGoi = [], trangThai = {phien:7,...tuyChon};
  const core = {engine(ma) {
    assert.equal(ma,'e_hoi_ai');
    return {
      cau_hinh:{
        async doc() { if (trangThai.loiDoc) throw Error('DEMO-CHI-TIET-KHONG-HIEN-8QAA');
          return {cau_hinh:trangThai.trong ? null : structuredClone(trangThai.cauHinh || DEMO),phien_ban_cau_hinh:trangThai.phien}; },
        async luu(gt,rv) {
          daLuu.push({giaTri:structuredClone(gt),rv});
          if (trangThai.xungDot) throw {ma:'NGAN_XUNG_DOT',message:'DEMO-CHI-TIET-KHONG-HIEN-8QAA'};
          if (trangThai.loiLuu) throw Error('DEMO-CHI-TIET-KHONG-HIEN-8QAA');
          assert.equal(rv,trangThai.phien); return {phien_ban_cau_hinh:++trangThai.phien};
        }},
      ngan:{async tim(bang,thamSo) {
        assert.equal(bang,'model_phat_hien'); daTim.push(thamSo);
        if (trangThai.loiNgan) throw Error('DEMO-CHI-TIET-KHONG-HIEN-8QAA');
        return trangThai.trong ? {danh_sach:[],tiep:null} : {danh_sach:[{gia_tri:MODELS[thamSo.tiep ? 1:0]}],tiep:thamSo.tiep ? null:'1'};
      }},
      async thao_tac(ma,gt) {
        daGoi.push({ma,gt}); if (trangThai.cho) await trangThai.cho;
        if (trangThai.loiKiem) throw Error('DEMO-CHI-TIET-KHONG-HIEN-8QAA');
        if (ma === 'tim_may_ai') return {danh_sach:trangThai.khongMay ? []:[{url:'http://127.0.0.1:1234'}],so_da_kiem:2};
        return {url:gt.url,ket_noi:!trangThai.matKetNoi,models:trangThai.matKetNoi ? []:(trangThai.models || MODELS),kiem_luc:'2026-11-21T14:25:00Z'};
      },
      // UI-AI-1 không có bí mật; mọi lời gọi két đều là lỗi phạm vi.
      bi_mat:new Proxy({}, {get() { throw Error('Không được đọc bí mật ở Máy AI'); }}),
    };
  }};
  return {core,daLuu,daTim,daGoi,trangThai};
}
export class PhanTu {
  constructor(the,doc) { this.the=the;this.ownerDocument=doc;this.con=[];this.suKien={};this.thuocTinh={};this.classList={add(){}};this.value='';this.textContent=''; }
  appendChild(el) { this.con.push(el);el.cha=this;return el; }
  replaceChildren() { this.con=[]; }
  setAttribute(k,v) { this.thuocTinh[k]=v; }
  addEventListener(k,fn) { (this.suKien[k] ||= []).push(fn); }
  async goi(k) { if (k === 'click' && this.disabled) return; for (const fn of this.suKien[k] || []) await fn({preventDefault(){}}); }
}
export function taoGoc() { const doc={createElement:the=>new PhanTu(the,doc)};return new PhanTu('main',doc); }
export function tatCa(el) { return [el,...el.con.flatMap(tatCa)]; }
export function chu(el) { return el.textContent + el.con.map(chu).join(' '); }
export function tim(el,the,ten) { return tatCa(el).find(n=>n.the===the && (!ten || n.textContent===ten)); }
export function nhap(el,ten) { return tatCa(el).find(n=>n.thuocTinh['aria-label']===ten); }
