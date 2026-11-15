// KttCore và DOM tối thiểu trong bộ nhớ; Node không cần gói ngoài/mạng.
import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import test from "node:test";

const nguon = await readFile(new URL("../../goi/e_hoi_ai/ui/cau_hinh.js", import.meta.url), "utf8");
const {default: nap} = await import(`data:text/javascript;base64,${Buffer.from(nguon).toString("base64")}`);

class PhanTu {
  constructor(the, doc) {
    this.the = the; this.ownerDocument = doc; this.con = []; this.suKien = {};
    this.thuocTinh = {}; this.classList = {add() {}};
    this.value = ""; this.textContent = "";
  }
  appendChild(el) { this.con.push(el); el.cha = this; return el; }
  replaceChildren() { this.con = []; }
  remove() { this.cha.con = this.cha.con.filter(el => el !== this); }
  setAttribute(k, v) { this.thuocTinh[k] = v; }
  addEventListener(k, fn) { this.suKien[k] = fn; }
  reportValidity() { return true; }
  async goi(k) { await this.suKien[k]?.({preventDefault() {}}); }
}
function tatCa(el) { return [el, ...el.con.flatMap(tatCa)]; }
function chu(el) { return el.textContent + el.con.map(chu).join(" "); }
function tim(el, the, ten) { return tatCa(el).find(n => n.the === the && (!ten || n.textContent === ten)); }
function nhap(el, ten) { return tim(el, "label", ten).con[0]; }
const DEMO = {local_ai: {url: "http://127.0.0.1:12345", timeout_giay: 60},
  quy_tac_model: [{mau_ma_prompt: "demo.*", uu_tien: "model-demo", du_phong: ["model-demo-b"]}]};

async function dung({xungDot = false, loiDoc = false, trong = false} = {}) {
  const doc = {createElement: the => new PhanTu(the, doc)};
  const goc = new PhanTu("main", doc);
  const daLuu = [], daTim = [];
  let phien = 7;
  const core = {engine(ma) {
    assert.equal(ma, "e_hoi_ai");
    return {
      cau_hinh: {
        async doc() {
          if (loiDoc) throw Error("DEMO chi tiet khong lo");
          return {cau_hinh: trong ? null : structuredClone(DEMO), phien_ban_cau_hinh: phien};
        },
        async luu(giaTri, rv) {
          daLuu.push({giaTri: structuredClone(giaTri), rv});
          if (xungDot) throw {ma: "NGAN_XUNG_DOT", message: "DEMO bi mat khong hien"};
          assert.equal(rv, phien);
          return {phien_ban_cau_hinh: ++phien};
        },
      },
      ngan: {async tim(bang, thamSo) {
        assert.equal(bang, "model_phat_hien");
        daTim.push(thamSo);
        if (trong) return {danh_sach: [], tiep: null};
        return {danh_sach: [{gia_tri: {id_model: thamSo.tiep ? "model-demo-b" : "model-demo",
          kha_dung: true, thu_tu: thamSo.tiep ? 1 : 0}}], tiep: thamSo.tiep ? null : "1"};
      }},
    };
  }};
  await nap(goc, core);
  return {goc, daLuu, daTim};
}

test("Đọc đủ trang, sửa và lưu qua Core với CAS; giữ quy tắc dự phòng", async () => {
  const {goc, daLuu, daTim} = await dung();
  assert.equal(daTim.length, 2);
  assert.deepEqual(daTim[0].loc, {url: DEMO.local_ai.url});
  assert.match(chu(goc), /Cổng Local AI/);
  assert.match(chu(goc), /model-demo-b/);
  nhap(goc, "Địa chỉ máy Local AI").value = "http://127.0.0.1:12346";
  nhap(goc, "Thời hạn chờ (giây)").value = "25";
  const form = tim(goc, "form");
  await form.goi("submit");
  assert.deepEqual(daLuu[0], {giaTri: {...DEMO,
    local_ai: {url: "http://127.0.0.1:12346", timeout_giay: 25}}, rv: 7});
  assert.match(chu(goc), /Đã lưu cấu hình/);
  await form.goi("submit");
  assert.equal(daLuu[1].rv, 8);
  const cloud = tatCa(goc).find(n => n.the === "fieldset" && tim(n, "legend", "Cổng Cloud AI"));
  assert.match(chu(cloud), /Chưa áp dụng ở bản 1/);
  assert.equal(tatCa(cloud).filter(n => ["button", "input"].includes(n.the)).length, 0);
});

test("Xung đột CAS hiện câu tiếng Việt và giữ nguyên nội dung đang sửa", async () => {
  const {goc, daLuu} = await dung({xungDot: true});
  nhap(goc, "Thời hạn chờ (giây)").value = "30";
  await tim(goc, "form").goi("submit");
  assert.equal(daLuu.length, 1);
  assert.match(chu(goc), /Cấu hình đã được người khác thay đổi. Hãy tải lại màn hình trước khi lưu/);
  assert.equal(nhap(goc, "Thời hạn chờ (giây)").value, "30");
  assert.doesNotMatch(chu(goc), /DEMO bi mat/);
});

test("Thêm và bỏ quy tắc, màn chưa cấu hình vẫn lưu được địa chỉ", async () => {
  const {goc, daLuu} = await dung({trong: true});
  assert.match(chu(goc), /Chưa có kết quả kiểm/);
  nhap(goc, "Địa chỉ máy Local AI").value = DEMO.local_ai.url;
  await tim(goc, "button", "Thêm quy tắc").goi("click");
  nhap(goc, "Mẫu mã prompt").value = "demo.*";
  await tim(goc, "button", "Bỏ quy tắc").goi("click");
  await tim(goc, "form").goi("submit");
  assert.deepEqual(daLuu[0].giaTri.quy_tac_model, []);
});

test("Lỗi đọc không cho lưu đè; đầu vào hiển thị qua textContent", async () => {
  const {goc, daLuu} = await dung({loiDoc: true});
  await tim(goc, "form").goi("submit");
  assert.equal(daLuu.length, 0);
  assert.match(chu(goc), /Hãy tải lại màn hình/);
  assert.doesNotMatch(chu(goc), /DEMO chi tiet/);
  assert.doesNotMatch(nguon, /innerHTML|\beval\s*\(|\bfetch\s*\(|XMLHttpRequest|localStorage|sessionStorage/);
});
