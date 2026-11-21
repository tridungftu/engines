// Chụp Chromium cục bộ; không thay đổi ExecutionPolicy hoặc trình duyệt đang dùng.
import {spawnSync} from "node:child_process";
import {existsSync, mkdirSync, statSync, writeFileSync} from "node:fs";
import {fileURLToPath, pathToFileURL} from "node:url";
import {resolve, join} from "node:path";
const repo = fileURLToPath(new URL("../../../", import.meta.url));
const browser = (process.argv[2]?.startsWith("--") ? undefined : process.argv[2]) ?? [
  join(process.env.ProgramFiles ?? "", "Google/Chrome/Application/chrome.exe"),
  join(process.env["ProgramFiles(x86)"] ?? "", "Microsoft/Edge/Application/msedge.exe"),
].find(existsSync);
if (!browser) throw new Error("Cần đường dẫn Chromium để chụp ảnh DEMO.");
const html = resolve(repo, ".venv/ui-ts-pl-DEMO.html");
const dung = spawnSync(process.execPath, [fileURLToPath(new URL("./dung_anh.mjs", import.meta.url)), html], {cwd: repo, encoding: "utf8", windowsHide: true});
if (dung.status) throw new Error("Không dựng được trang DEMO.");
mkdirSync(new URL("./anh/", import.meta.url), {recursive: true});
for (const [ten, the, w, h, mode] of [
  ["danh-muc", "danh_muc_loai_json", 1200, 1000, ""],
  ["phan-loai", "bo_phan_loai_json", 1200, 2250, ""],
  ["khuon-cot", "khuon_cot_json", 1200, 3600, ""],
  ["di-dong-loi", "nguong_json", 500, 1700, "loi"],
  ["cas", "nguong_json", 1200, 1150, "cas"],
  ["nguong-chinh-sach", "nguong_json,chinh_sach_json", 1200, 1770, ""],
]) {
  const chi = process.argv.find(v => v.startsWith("--chi="))?.slice(6);
  if (chi && chi !== ten) continue;
  const anh = fileURLToPath(new URL(`./anh/ts-pl-${ten}.png`, import.meta.url));
  const url = pathToFileURL(html); url.searchParams.set("the", the); url.searchParams.set("che_do", mode);
  const kq = spawnSync(browser, ["--headless", "--no-sandbox", "--disable-gpu", "--in-process-gpu", "--no-first-run",
    "--no-default-browser-check", "--disable-background-networking", "--disable-component-update", "--hide-scrollbars",
    "--force-device-scale-factor=1", `--user-data-dir=${resolve(repo, ".venv", "chrome-DEMO-ts-pl-" + ten)}`,
    `--window-size=${w},${h}`, "--virtual-time-budget=3000", `--screenshot=${anh}`, "--dump-dom", url.href],
  {cwd: repo, encoding: "utf8", windowsHide: true, maxBuffer: 4 * 1024 * 1024, timeout: 30000});
  writeFileSync(resolve(repo, ".venv", `ts-pl-${ten}-dom.txt`), kq.stdout ?? "", "utf8");
  writeFileSync(resolve(repo, ".venv", `ts-pl-${ten}-browser.txt`), kq.stderr ?? "", "utf8");
  if (kq.status !== 0 || !kq.stdout.includes('data-demo-da-dung="true"')) throw new Error("Không dựng được ảnh DEMO: " + ten);
  const kichThuoc = JSON.parse(kq.stdout.match(/data-demo-kich-thuoc="([^"]*)"/)[1].replaceAll("&quot;", '"'));
  if (kichThuoc.viewport > w) throw new Error("Ảnh hẹp hơn viewport Chromium, có thể bị cắt cạnh: " + ten);
  if (kq.stdout.includes('data-tran-ngang="true"')) throw new Error("Màn bị tràn ngang: " + ten);
  console.log(`Đã chụp ts-pl-${ten}.png (${statSync(anh).size} byte), không tràn ngang.`);
}
