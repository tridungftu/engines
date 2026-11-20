"""PL-8B: quét tĩnh, đối chiếu wheel thật và kiểm màn bằng KttCore giả, không trình duyệt.

SDK 2.2.0 hiện thiếu cổng JS engine: ca đối chiếu ghi xfail rõ ràng,
không coi mock KttCore là bằng chứng đã chạy được trên Core thật/CoreGia.
"""
from pathlib import Path
import hashlib
import re
import shutil
import subprocess
import zipfile

import pytest


GOC = Path(__file__).resolve().parents[2]
TEP_UI = GOC / "e_phan_luong/goi/e_phan_luong/ui/bang_ty_le.js"
SDK = GOC / "docs/goi-gui-engine/sdk-2.2.0"
WHEEL = SDK / "kho_tri_thuc_sdk-2.2.0-py3-none-any.whl"
MA = TEP_UI.read_text(encoding="utf-8")
NODE = shutil.which("node")


@pytest.mark.parametrize("cam", [
    r"\binnerHTML\b", r"\bouterHTML\b", r"\binsertAdjacentHTML\b",
    r"\beval\s*\(", r"\bnew\s+Function\b", r"\bXMLHttpRequest\b",
    r"\bfetch\s*\(", r"https?://", r"\b(?:localStorage|sessionStorage|indexedDB)\b",
])
def test_khong_co_cua_khong_an_toan(cam):
    assert not re.search(cam, MA), f"Màn dùng cửa bị cấm: {cam}"


def test_chi_doc_ngan_cua_dung_engine():
    assert re.search(r'KttCore\.engine\("e_phan_luong"\)', MA)
    cac_loi_goi = set(re.findall(r"\b(?:KttCore|cong)(?:\.[a-z_]+)+(?=\s*\()", MA))
    assert cac_loi_goi == {"KttCore.engine", "cong.ngan.doc", "cong.ngan.tim"}
    assert not re.search(r"\b(?:ghi_lo|luu|thao_tac)\s*\(", MA)
    assert "createElement" in MA and "textContent" in MA
    assert 'export default mount' in MA


def test_wheel_sdk_khop_bam_phat_hanh():
    dong = next(d for d in (SDK / "SHA256SUMS.txt").read_text().splitlines()
                if d.split()[-1] == WHEEL.name)
    assert hashlib.sha256(WHEEL.read_bytes()).hexdigest() == dong.split()[0]


def test_ten_ham_doi_chieu_trinh_duyet_sdk_220():
    with zipfile.ZipFile(WHEEL) as goi:
        ma_sdk = goi.read("kho_tri_thuc_sdk/trinh_duyet.js").decode("utf-8")
    # Kiểm cả hàm cấp cổng và các hàm con; không thay bằng danh sách tự tuyên bố.
    ten = {"engine", "doc", "tim"}
    ham_sdk = set(re.findall(r"\b(?:async\s+)?(?:function\s+)?([a-z_]+)\s*\([^;\n]*?\)\s*\{", ma_sdk))
    ham_sdk.update(re.findall(r"\b([a-z_]+)\s*:\s*(?:async\s*)?(?:function\b|\([^\n]*?\)\s*=>)", ma_sdk))
    thieu = ten - ham_sdk
    if "engine" in thieu:
        pytest.xfail("Cần Core: trinh_duyet.js trong wheel SDK 2.2.0 chưa xuất KttCore.engine; "
                     "chưa đối chiếu được engine.ngan.doc/tim. Màn dừng an toàn khi thiếu cổng.")
    assert not thieu, f"SDK thiếu tên hàm màn gọi: {sorted(thieu)}"
    assert re.search(r"\bngan\b", ma_sdk), "SDK chưa có nhóm engine.ngan"


@pytest.mark.skipif(NODE is None, reason="Máy không có Node để kiểm cú pháp ES module.")
def test_node_check():
    kq = subprocess.run([NODE, "--input-type=module", "--check"], input=MA,
                        capture_output=True, text=True, encoding="utf-8", timeout=20)
    assert kq.returncode == 0, kq.stderr


CHAY_MAN = r'''
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
const {mount} = await import("data:text/javascript;base64," +
  readFileSync(process.argv[2]).toString("base64"));
class PhanTu {
  constructor(tag, doc) { this.tag = tag; this.ownerDocument = doc; this.children = [];
    this.listeners = {}; this.attrs = {}; this._text = ""; this.value = ""; this.disabled = false; }
  appendChild(e) { this.children.push(e); return e; }
  replaceChildren(...es) { this.children = es; this._text = ""; }
  set textContent(v) { this._text = String(v); this.children = []; }
  get textContent() { return this._text + this.children.map(e => e.textContent).join("|"); }
  setAttribute(k, v) { this.attrs[k] = String(v); }
  addEventListener(k, h) { this.listeners[k] = h; }
}
const doc = {createElement: tag => new PhanTu(tag, doc)};
const goc = new PhanTu("main", doc);
const tatCa = (e = goc) => [e, ...e.children.flatMap(x => tatCa(x))];
const nut = ten => tatCa().find(e => e.tag === "button" && e.textContent === ten);
const bam = e => e.listeners.click({preventDefault() {}});
const oNhap = () => tatCa().find(e => e.tag === "input");
const gui = () => tatCa().find(e => e.tag === "form").listeners.submit({preventDefault() {}});
const banGhi = gia_tri => ({gia_tri});
const hat = "de".repeat(32);
let loi = null, doiTra = null;
const goi = [];
const ds = {
  ty_le: [[{khau:"DEMO-K",loai:"DEMO-L",bac:2,che_do:"bac",diem:"0.05",
    nhan:"rui_ro_cao",mau_tu_doi_bac:60,loi_tu_doi_bac:1,mau_12t:90,loi_12t:2}]],
  ket_qua_kiem: [[{khau:"DEMO-K",loai:"DEMO-L",nguon_loai_sai:"quy_tac"}],
    [{khau:"DEMO-K",loai:"DEMO-L",nguon_loai_sai:"ai"},
     {khau:"DEMO-K",loai:"DEMO-L",nguon_loai_sai:"ai"},
     {khau:"DEMO-K",loai:"DEMO-L",nguon_loai_sai:"module"}]],
  chot_ky: [[{ky:"2026-09",khau:"DEMO-K",loai:"DEMO-L"}],
    [{ky:"2026-10",khau:"DEMO-K",loai:"DEMO-L"}]],
  ho_so_hanh_vi: [[{khau:"DEMO-K",loai:"DEMO-L",so_doi_tac:20000}]],
  dong_luot: [[{ma_luot:"PL-DEMO",ly_do:"VUOT_PM,CO_DO_CUNG"}],
    [{ma_luot:"PL-DEMO",ly_do:"CHON_MAU"},{ma_luot:"PL-DEMO",ly_do:"KHONG_CHON"}]],
};
const KttCore = {engine(ma) {
  assert.equal(ma, "e_phan_luong");
  return {ngan: {
    async tim(bang, q) {
      goi.push([bang,q]);
      if (loi) throw loi;
      const i = q.tiep === null ? 0 : Number(q.tiep);
      const trang = ds[bang] ?? [[]];
      return {danh_sach: trang[i].map(banGhi), tiep: i+1 < trang.length ? String(i+1) : null};
    },
    async doc(bang, q) {
      goi.push([bang,q]);
      assert.equal(bang,"luot");
      if (loi) throw loi;
      if (doiTra) return doiTra;
      if (q.ma_luot === "KHONG-CO-DEMO") return null;
      return banGhi({ma_luot:q.ma_luot,ma_module:"demo_module",khau:"DEMO-K",
        bam_dau_vao:"bam-DEMO-<img onerror=DEMO>",hat_giong:hat});
    },
  }};
}};
const canh = process.argv[3];
if (canh === "thieu_sdk") {
  await mount(goc,{KttCore:{}});
  assert.match(goc.textContent,/chưa có cổng quản trị engine/);
  assert.equal(nut("Tải lại").disabled,true);
  assert.equal(tatCa().find(e => e.tag === "details").open,false);
  assert.equal(goi.length,0);
} else {
  const man = await mount(goc,{KttCore});
  if (canh === "hien_thi") {
    assert.match(goc.textContent,/Rủi ro cao/);
    assert.match(goc.textContent,/chạm trần 20.000/);
    const bangNguon = tatCa().find(e => e.tag === "table" && e.textContent.includes("Quy tắc"));
    const hang = bangNguon.children[1].children[0];
    assert.deepEqual(hang.children.map(e => e.textContent),["DEMO-K","DEMO-L","1","2"]);
    const ls = tatCa().find(e => e.tag === "table" && e.textContent.includes("Kỳ (năm-tháng)"));
    assert.equal(ls.children[1].children[0].children[0].textContent,"2026-10");
    oNhap().value="PL-DEMO"; await gui();
    assert.ok(!goc.textContent.includes(hat));
    assert.deepEqual(goi.filter(([b]) => b === "dong_luot").map(([,q]) => q.loc),
      [{ma_luot:"PL-DEMO"},{ma_luot:"PL-DEMO"}]);
    const luot = tatCa().find(e => e.tag === "table" && e.textContent.includes("Số dòng Đỏ"));
    assert.deepEqual(luot.children[1].children[0].children.slice(-2).map(e => e.textContent),["2","1"]);
    assert.match(goc.textContent,/<img onerror=DEMO>/);
    assert.equal(tatCa().filter(e => e.tag === "img").length,0);
    await bam(nut("Xem")); assert.ok(goc.textContent.includes(hat));
    await bam(nut("Ẩn")); assert.ok(!goc.textContent.includes(hat));
    await bam(nut("Xem"));
    oNhap().listeners.input(); assert.ok(!goc.textContent.includes(hat));
    oNhap().value="KHONG-CO-DEMO"; await gui();
    assert.match(goc.textContent,/Không tìm thấy lượt/);
    // Không có số đếm thì không khẳng định chưa chạm trần.
    ds.ho_so_hanh_vi=[[{khau:"DEMO-K",loai:"DEMO-L"}]]; await man.refresh();
    assert.match(goc.textContent,/Chưa có số đếm đối tác/);
    ds.ho_so_hanh_vi=[[{khau:"DEMO-K",loai:"DEMO-L",bam_doi_tac:JSON.stringify({"bam-DEMO": "2026-10"})}]];
    await man.refresh(); assert.match(goc.textContent,/Chưa ghi nhận hồ sơ chạm trần/);
  } else if (canh === "tu_choi") {
    oNhap().value="PL-DEMO"; await gui(); await bam(nut("Xem"));
    loi={status:403,ma:"CAM_TRUY_CAP",thong_diep:"Không có quyền xem dữ liệu.",message:"DUONG-DAN-BI-MAT-DEMO"};
    await gui();
    assert.match(goc.textContent,/Không có quyền xem dữ liệu/);
    assert.ok(!goc.textContent.includes(hat));
    assert.ok(!goc.textContent.includes("demo_module"));
    assert.ok(!goc.textContent.includes("DUONG-DAN-BI-MAT-DEMO"));
    const ct=tatCa().find(e => e.tag === "details");
    assert.equal(ct.open,false); assert.match(ct.textContent,/CAM_TRUY_CAP/);
  } else if (canh === "trang_hong") {
    // Không coi dữ liệu lỗi là số đếm bằng không hay hiển thị kết quả một phần.
    ds.dong_luot=[[{ma_luot:"PL-DEMO",ly_do:"MA_CHUA_BIET_DEMO"}]];
    oNhap().value="PL-DEMO"; await gui();
    assert.match(goc.textContent,/PL_UI_DU_LIEU_KHONG_HOP_LE/);
    assert.ok(!nut("Xem"));
    const gocHong=new PhanTu("main",doc); let soGoi=0;
    const manHong=await mount(gocHong,{KttCore:{engine() {return {ngan:{
      doc:async()=>null,tim:async()=>{++soGoi; return {danh_sach:[],tiep:"lap-DEMO"};}
    }}}}});
    assert.equal(soGoi,2);
    assert.match(gocHong.textContent,/PL_UI_DU_LIEU_KHONG_HOP_LE/);
    manHong.destroy();
  } else if (canh === "phan_hoi_cu") {
    let traVe;
    doiTra=new Promise(r=>{traVe=r;});
    oNhap().value="PL-DEMO"; const dangTra=gui();
    man.destroy(); traVe(banGhi({ma_luot:"PL-DEMO",hat_giong:hat}));
    await dangTra; assert.equal(goc.textContent,"");
  } else throw new Error("Ca DEMO không tồn tại");
  man.destroy(); assert.equal(goc.textContent,"");
}
console.log("ĐẠT " + canh);
'''


@pytest.mark.skipif(NODE is None, reason="Máy không có Node để chạy KttCore giả trong RAM.")
@pytest.mark.parametrize("canh", ["thieu_sdk", "hien_thi", "tu_choi", "trang_hong", "phan_hoi_cu"])
def test_man_kttcore_gia_khong_trinh_duyet(tmp_path, canh):
    tep = tmp_path / "kiem_man_DEMO.mjs"
    tep.write_text(CHAY_MAN, encoding="utf-8")
    kq = subprocess.run([NODE, str(tep), str(TEP_UI), canh], capture_output=True,
                        text=True, encoding="utf-8", timeout=20)
    assert kq.returncode == 0, kq.stderr
    assert f"ĐẠT {canh}" in kq.stdout
