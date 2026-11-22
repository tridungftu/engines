import assert from 'node:assert/strict';
export function taoKet(opts = {}) {
  const state = {da_luu:true,bon_ky_tu_cuoi:'8QAA',phien_ban:7,...opts};
  const calls = [];
  function meta() { return {da_luu:state.da_luu,bon_ky_tu_cuoi:state.bon_ky_tu_cuoi,phien_ban:state.phien_ban}; }
  const core = {engine(ma) {
    assert.equal(ma,'e_hoi_ai');
    return {bi_mat:{
      async trang_thai(ten) {
        assert.equal(ten,'khoa_api_anthropic'); calls.push({ma:'doc'});
        if (state.loiDoc) throw Error('DEMO-LOI-BI-MAT-KHONG-HIEN');
        return state.metaSai || meta();
      },
      async luu(ten,gt,rv) { return ghi('luu',ten,rv,gt); },
      async xoa(ten,rv) { return ghi('xoa',ten,rv); },
    }};
  }};
  async function ghi(ma,ten,rv,gt) {
    assert.equal(ten,'khoa_api_anthropic'); calls.push({ma,rv});
    if (state.cho) await state.cho;
    if (rv !== state.phien_ban || state.xungDot) throw {status:409,ma:'BI_MAT_XUNG_DOT',message:'DEMO-LOI-BI-MAT-KHONG-HIEN'};
    if (state.loiGhi) throw Error('DEMO-LOI-BI-MAT-KHONG-HIEN');
    state.phien_ban++; state.da_luu = ma === 'luu';
    state.bon_ky_tu_cuoi = ma === 'luu' ? gt.slice(-4) : null;
    return state.metaGhiSai || meta();
  }
  return {core,state,calls};
}
