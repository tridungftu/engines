// Core kiểm quyền admin_core trước khi nạp và trước mỗi thao tác ngăn.
// Chỉ dùng API Core và textContent; không hiển thị lỗi kỹ thuật từ nguồn.
export function taoMan({ KttCore, goc, document = globalThis.document }) {
  const ngan = KttCore.engine("e_mask").ngan;
  const chuan = (b) => b.replace(/\s/g, "").toLowerCase();
  const khoa = (vung, k) => ({ vung, khoa: k });
  const noi = document.createElement("div");
  const thongBao = document.createElement("p");
  const boLoc = document.createElement("div");
  const bang = document.createElement("table");
  const loc = {};
  const tao = (ten, chu) => { const e = document.createElement(ten); e.textContent = chu; return e; };
  noi.append(tao("h2", "Duyệt danh sách chờ"), thongBao, boLoc, bang);
  goc.append(noi);
  const cacLoc = [["gia_tri", "Tên cần duyệt"], ["nhom", "Nhóm"], ["so_lan_gap", "Số lần gặp"]];
  for (const [ma, ten] of cacLoc) {
    const nhan = tao("label", ten);
    const o = document.createElement("input"); o.setAttribute("aria-label", ten);
    loc[ma] = o; o.addEventListener("input", ve); nhan.append(o); boLoc.append(nhan);
  }
  let danhSach = [];
  async function het(b, dieuKien = {}) {
    const ds = []; let tiep = null;
    do {
      const trang = await ngan.tim(b, { loc: dieuKien, gioi_han: 500, tiep });
      ds.push(...trang.danh_sach); tiep = trang.tiep;
    } while (tiep != null);
    return ds;
  }
  const giaTri = (m) => m.gia_tri;
  async function luu(vung, phien, lenh) {
    if (lenh.length + 1 > 100) throw new Error("gioi_han");
    await ngan.ghi_lo({ lenh: [{ thao_tac: "sua", bang: "dau_gap", khoa: khoa(vung, "phien"),
      gia_tri: { so: phien.gia_tri.so + 1 }, row_version: phien.row_version }, ...lenh] });
  }
  async function bao(ham) {
    try { await ham(); thongBao.textContent = "Đã cập nhật danh sách."; await nap(); }
    catch (loi) {
      thongBao.textContent = ["NGAN_XUNG_DOT", "MASK_XUNG_DOT"].includes(loi?.ma)
        ? "Danh sách vừa thay đổi. Hãy tải lại và thử lại."
        : "Không thể cập nhật. Hãy kiểm tra quyền quản trị và tải lại danh sách.";
      return false;
    }
    return true;
  }
  async function duyet(muc, maJunsky = "") {
    return bao(async () => {
      const m = giaTri(muc), vung = m.vung;
      const phien = await ngan.doc("dau_gap", khoa(vung, "phien"));
      let biDanh;
      const tienTo = ["MASKCT", "MASKCN", "MASKDC", "MASKMST", "MASKTK", "MASKKHAC", "MASKTAM"];
      if (maJunsky) {
        if (!/^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$/.test(maJunsky) ||
            tienTo.some((t) => maJunsky.toUpperCase().startsWith(t))) throw new Error("ma");
        biDanh = `[[${maJunsky}]]`;
      } else {
        const t = { CONG_TY: "MASKCT", CA_NHAN: "MASKCN", DIA_CHI: "MASKDC", MA_SO_THUE: "MASKMST", TAI_KHOAN: "MASKTK" };
        biDanh = `[[${t[m.nhom] || "MASKKHAC"}-${globalThis.crypto.randomUUID().replace(/-/g, "")}]]`;
      }
      for (const b of ["dinh_danh", "bi_danh_tam", "cho_duyet"]) {
        const ds = await het(b, { vung });
        if (ds.some((r) => {
          const v = giaTri(r);
          return v.gia_tri !== m.gia_tri && [v.bi_danh, v.bi_danh_tam].some((a) => a && chuan(a) === chuan(biDanh));
        })) throw { ma: "MASK_XUNG_DOT" };
      }
      const moi = { ...m, bi_danh: biDanh, bi_danh_tam: m.bi_danh, nguon: "chinh_thuc" };
      delete moi.so_lan_gap;
      await luu(vung, phien, [
        { thao_tac: "them", bang: "dinh_danh", khoa: khoa(vung, m.khoa), gia_tri: moi },
        { thao_tac: "xoa", bang: "cho_duyet", khoa: khoa(vung, m.khoa), row_version: muc.row_version },
      ]);
    });
  }
  async function tuChoi(muc) {
    return bao(async () => {
      const m = giaTri(muc);
      const phien = await ngan.doc("dau_gap", khoa(m.vung, "phien"));
      await luu(m.vung, phien, [{ thao_tac: "xoa", bang: "cho_duyet", khoa: khoa(m.vung, m.khoa), row_version: muc.row_version }]);
    });
  }
  async function don(vung) {
    return bao(async () => {
      const phien = await ngan.doc("dau_gap", khoa(vung, "phien"));
      const yc = await het("ma_yeu_cau", { vung });
      const mo = new Set(yc.filter((m) => giaTri(m).trang_thai === "DANG_XU_LY").map((m) => giaTri(m).khoa));
      const dau = await het("dau_gap", { vung });
      const giu = new Set(dau.filter((m) => giaTri(m).loai_dau === "tham_chieu" && mo.has(giaTri(m).ma_yeu_cau)).map((m) => giaTri(m).bi_danh));
      for (const m of await het("cho_duyet", { vung })) giu.add(chuan(giaTri(m).bi_danh));
      const xoa = (await het("bi_danh_tam", { vung })).filter((m) => !giu.has(giaTri(m).khoa));
      const maXoa = new Set(xoa.map((m) => giaTri(m).khoa));
      const lenh = xoa.map((m) => ({ thao_tac: "xoa", bang: "bi_danh_tam", khoa: khoa(vung, giaTri(m).khoa), row_version: m.row_version }));
      for (const r of await het("dinh_danh", { vung })) {
        const m = giaTri(r);
        if (m.bi_danh_tam && maXoa.has(chuan(m.bi_danh_tam))) {
          const moi = { ...m }; delete moi.bi_danh_tam;
          lenh.push({ thao_tac: "sua", bang: "dinh_danh", khoa: khoa(vung, m.khoa), gia_tri: moi, row_version: r.row_version });
        }
      }
      await luu(vung, phien, lenh);
    });
  }
  function nut(ten, ham) {
    const n = tao("button", ten);
    n.addEventListener("click", async () => { n.disabled = true; try { await ham(); } finally { n.disabled = false; } });
    return n;
  }
  function ve() {
    bang.replaceChildren();
    const dau = document.createElement("tr");
    for (const ten of ["Tên cần duyệt", "Nhóm", "Số lần gặp", "Mã đối tác (nếu có)", "Thao tác"]) dau.append(tao("th", ten));
    bang.append(dau);
    const nhom = { CONG_TY: "Công ty", CA_NHAN: "Cá nhân", DIA_CHI: "Địa chỉ", MA_SO_THUE: "Mã số thuế", TAI_KHOAN: "Tài khoản", KHAC: "Khác" };
    for (const r of danhSach) {
      const m = giaTri(r);
      if (cacLoc.some(([k]) => !String(k === "nhom" ? nhom[m[k]] || "Khác" : m[k]).toLocaleLowerCase("vi").includes(loc[k].value.toLocaleLowerCase("vi")))) continue;
      const hang = document.createElement("tr");
      hang.append(tao("td", m.gia_tri), tao("td", nhom[m.nhom] || "Khác"), tao("td", String(m.so_lan_gap)));
      const o = document.createElement("input"); o.setAttribute("aria-label", "Mã đối tác");
      const cot = document.createElement("td"); cot.append(o); hang.append(cot);
      const tac = document.createElement("td"); tac.append(nut("Duyệt", () => duyet(r, o.value.trim())), nut("Từ chối", () => tuChoi(r)));
      hang.append(tac); bang.append(hang);
    }
  }
  async function nap() { danhSach = await het("cho_duyet"); ve(); }
  noi.append(nut("Tải lại", () => bao(nap)), nut("Dọn bí danh tạm", async () => {
    let cacVung;
    if (!await bao(async () => {
      cacVung = new Set((await het("bi_danh_tam")).map((m) => giaTri(m).vung));
    })) return;
    for (const v of cacVung) if (!await don(v)) return;
  }));
  return { nap, duyet, tuChoi, don, thongBao, loc };
}

export default taoMan;
