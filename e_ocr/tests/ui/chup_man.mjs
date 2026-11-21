// Dựng màn thật với KttCore giả, chặn toàn bộ mạng. Không là dependency runtime.
// node e_ocr/tests/ui/chup_man.mjs <thư mục playwright-core đã có trên máy>
import assert from "node:assert/strict";
import {readFile, mkdir} from "node:fs/promises";
import {resolve} from "node:path";
import {pathToFileURL, fileURLToPath} from "node:url";

const thuVien = process.argv[2];
const {chromium} = thuVien ? await import(pathToFileURL(resolve(thuVien, "index.mjs"))) : await import("playwright-core");
const nguon = await readFile(new URL("../../goi/e_ocr/ui/cau_hinh.js", import.meta.url), "utf8");
const dich = new URL("../../docs/anh-ui-ocr/", import.meta.url);
await mkdir(dich, {recursive: true});
const browser = await chromium.launch({headless: true, args: ["--disable-background-networking"]});
try {
  const context = await browser.newContext({viewport: {width: 1160, height: 1000}, locale: "vi-VN", timezoneId: "Asia/Ho_Chi_Minh"});
  let soMang = 0;
  await context.route("**/*", route => { soMang++; return route.abort(); });
  const page = await context.newPage();
  const loiTrang = [];
  page.on("pageerror", e => loiTrang.push(e.message));
  await page.setContent('<!doctype html><html lang="vi"><meta charset="utf-8"><title>DEMO — UI-OCR</title><body style="margin:0;background:#f4f6f9"><p style="font:14px Segoe UI;margin:18px 30px;color:#60758b">DEMO · KttCore giả · Không kết nối nguồn OCR thật</p><main id="goc"></main></body></html>');
  await page.evaluate(async nguon => {
    const {mount} = await import("data:text/javascript;base64," + btoa(unescape(encodeURIComponent(nguon))));
    const luc = Date.parse("2026-11-21T21:26:00+07:00");
    let cauHinh = {abbyy: {bat: true, thu_muc_vao: "C:/DEMO/OCR/nhan", thu_muc_ra: "C:/DEMO/OCR/tra", thoi_han_giay: 900, han_muc_trang_30_ngay: 5000},
      tesseract: {duong_dan: "", ngon_ngu: "vie+eng"}};
    let phien = 7;
    window.demo = {loiKiem: false, xungDot: false, soLuu: 0};
    const KttCore = {engine(ma) {
      if (ma !== "e_ocr") throw Error("Sai engine DEMO.");
      return {
        cau_hinh: {
          async doc() { return {gia_tri: structuredClone(cauHinh), phien_ban_cau_hinh: phien}; },
          async luu(moi, cu) {
            if (window.demo.xungDot || cu !== phien) throw {status: 409};
            cauHinh = structuredClone(moi); window.demo.soLuu++;
            return {phien_ban_cau_hinh: ++phien};
          },
        },
        ngan: {
          async doc(bang, {ma}) {
            if (bang !== "trang_thai_engine") throw Error("Sai bảng DEMO.");
            const gia_tri = ma === "abbyy" ? {abbyy_bat: true, luc_kiem: new Date(luc).toISOString()}
              : ma === "han_muc" ? {dang_giu: '{"DEMO":2}'}
                : {so_luot: 2, theo_ngay: '{"2026-11-20":1,"2026-11-21":1}'};
            return {gia_tri, row_version: 1};
          },
          async tim() { return {danh_sach: [{gia_tri: {ngay: "2026-11-21", da_nhan: '{"0":1250}'}}], tiep: null}; },
        },
        async thao_tac(ma) {
          const dat = !window.demo.loiKiem;
          return {dat, ma: ma === "kiem_hot_folder"
            ? dat ? "HOT_FOLDER_TRUY_CAP_DUOC" : "HOT_FOLDER_KHONG_TRUY_CAP"
            : dat ? "TESSERACT_DU_NGON_NGU" : "TESSERACT_CHUA_DUNG_DUOC"};
        },
      };
    }};
    window.man = await mount(document.getElementById("goc"), {KttCore, dongHo: () => luc});
  }, nguon);

  await page.getByRole("button", {name: "Kiểm tra Hot Folder", exact: true}).click();
  await page.getByRole("button", {name: "Kiểm tra Tesseract", exact: true}).click();
  assert.equal(await page.locator('[data-muc="dat"]').count(), 2);
  await page.screenshot({path: fileURLToPath(new URL("01-may-rong.png", dich)), fullPage: true});
  await page.getByRole("button", {name: "Lưu cấu hình", exact: true}).click();
  assert.equal(await page.evaluate(() => window.demo.soLuu), 1);
  await page.locator('[name="thoi_han_giay"]').fill("901");
  assert.match(await page.locator("#ocr-thoi_han_giay-loi").innerText(), /Thời hạn phải là số nguyên/);
  await page.getByRole("button", {name: "Lưu cấu hình", exact: true}).click();
  assert.equal(await page.evaluate(() => window.demo.soLuu), 1);
  await page.locator('[name="thoi_han_giay"]').fill("900");
  await page.evaluate(() => {window.demo.loiKiem = true;});
  await page.getByRole("button", {name: "Kiểm tra Hot Folder", exact: true}).click();
  await page.getByRole("button", {name: "Kiểm tra Tesseract", exact: true}).click();
  assert.equal(await page.locator('[data-muc="loi"]').count(), 2);
  await page.screenshot({path: fileURLToPath(new URL("02-loi-nguon.png", dich)), fullPage: true});
  await page.evaluate(() => {window.demo.xungDot = true;});
  await page.getByRole("button", {name: "Lưu cấu hình", exact: true}).click();
  assert.ok(await page.getByRole("button", {name: "Lưu cấu hình", exact: true}).isDisabled());
  await page.screenshot({path: fileURLToPath(new URL("03-cas.png", dich)), fullPage: true});
  await page.getByRole("button", {name: "Tải lại cấu hình", exact: true}).click();
  assert.ok(await page.getByRole("button", {name: "Lưu cấu hình", exact: true}).isEnabled());
  await page.setViewportSize({width: 390, height: 844});
  await page.evaluate(() => {window.demo.loiKiem = false;});
  await page.getByRole("button", {name: "Kiểm tra Hot Folder", exact: true}).click();
  await page.getByRole("button", {name: "Kiểm tra Tesseract", exact: true}).click();
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await page.screenshot({path: fileURLToPath(new URL("04-man-hep.png", dich)), fullPage: true});
  assert.deepEqual(loiTrang, []);
  assert.equal(soMang, 0);
  await page.evaluate(() => window.man.destroy());
  assert.equal(await page.locator("#goc").innerText(), "");
  console.log("[ĐẠT] Trình duyệt + KttCore giả: đọc/lưu, lỗi nhập, kiểm hai nguồn đạt/lỗi, CAS/tải lại, màn hẹp; 0 yêu cầu mạng, 0 lỗi trang; 4 ảnh DEMO.");
} finally { await browser.close(); }
