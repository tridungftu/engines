'use strict';

/** HD-2c — seam DEMO bọc job/portal, không chép thuật toán tải.
 * Dùng lại giao diện H/src/job.js:75 startJob/getState và
 * H/src/portal.js:27 launchAndLogin; nguồn H được ghi tại NGUON.md.
 * Viết mới: nhận kênh bí mật, opts.env trong RAM, ràng buộc profile và
 * che lỗi ở biên adapter. Không nạp server, config, job hoặc portal nguồn.
 *
 * CHUA_KIEM nguồn thật: portal đóng cứng .browser-profile; job giữ state/log
 * toàn cục, không tiêm portal; fetchAllInvoices nuốt lỗi nhóm. Cần lead cấp
 * seam profile + job riêng + coverage, không vá nguồn hoặc giả COMPLETE.
 * Factory dưới đây chỉ dành cho Node giả. HD-3b/Core chịu trách nhiệm cấp
 * tài khoản/ACL, giữ profile đến ACK, dọn sau phiên và phục hồi crash.
 * Adapter không xóa tệp, không tự mở profile hay đọc két Core.
 */
const path = require('node:path');
const { inspect, TextDecoder } = require('node:util');

const GIOI_HAN_BI_MAT = 16384;
const NGUON_THAT = Object.freeze({
  trang_thai: 'CHUA_KIEM',
  can_lead: 'Seam profile, job/portal riêng và coverage nguồn; HD-3b kiểm Windows/ACL/ACK/dọn profile.',
});
const kenhDaDung = new WeakSet();
const profileDaDung = new Set();
const phienDaDung = new Set();
const jobDaDung = new WeakSet();
const portalDaDung = new WeakSet();

function loi(code) { return Object.assign(new Error(code), { code }); }
function text(value) { return typeof value === 'string' && value.length > 0; }
function doiTuong(value) { return value !== null && typeof value === 'object'; }
function envRam(username, password) {
  const env = Object.create(null);
  Object.defineProperties(env, {
    TAX_USERNAME: { value: username, writable: true },
    TAX_PASSWORD: { value: password, writable: true },
    [inspect.custom]: { value: () => 'BiMat(<an>)' },
  });
  return env;
}

/** JSON một dòng trên pipe riêng stdin/handle đã được Core giới hạn quyền.
 * Đây là dữ liệu nội bộ DEMO, không thay bootstrap SDK hay contract nghiệp vụ.
 * Không nhận tên tệp, fd số, env hoặc đối số dòng lệnh. Caller truyền Readable
 * của pipe; không dùng chung pipe bootstrap. Chờ EOF để từ chối frame thừa.
 */
async function nhanBiMat(kenh, phapNhanId, phienId) {
  if (!doiTuong(kenh) || typeof kenh[Symbol.asyncIterator] !== 'function'
      || kenh.path !== undefined || kenh.isTTY || kenhDaDung.has(kenh)) {
    throw loi('HD_KENH_BI_MAT');
  }
  kenhDaDung.add(kenh);
  const chunks = [];
  let raw, data, size = 0;
  try {
    for await (const chunk of kenh) {
      if (!Buffer.isBuffer(chunk)) throw loi('HD_BI_MAT_SAI');
      size += chunk.length;
      if (size > GIOI_HAN_BI_MAT) throw loi('HD_BI_MAT_SAI');
      chunks.push(Buffer.from(chunk));
    }
    raw = Buffer.concat(chunks);
    const line = new TextDecoder('utf-8', { fatal: true }).decode(raw);
    if (!line.endsWith('\n') || line.slice(0, -1).includes('\n')) throw loi('HD_BI_MAT_SAI');
    data = JSON.parse(line);
    if (!doiTuong(data) || Array.isArray(data)
        || Object.keys(data).sort().join(',') !== 'password,phapNhanId,phienId,username'
        || data.phapNhanId !== phapNhanId || data.phienId !== phienId
        || !text(data.username) || !text(data.password)) throw loi('HD_BI_MAT_SAI');
    return envRam(data.username, data.password);
  } catch {
    // Không giữ cause/message/stack từ parser hoặc handle chứa canary.
    throw loi('HD_BI_MAT_SAI');
  } finally {
    raw?.fill(0);
    for (const chunk of chunks) chunk.fill(0);
    if (doiTuong(data)) data.username = data.password = null;
    // Chuỗi JS không bảo đảm zeroization; chỉ thu hẹp thời gian giữ trong RAM.
  }
}

function kiemLenh(lenh) {
  if (!doiTuong(lenh) || lenh.demo !== true || !text(lenh.phapNhanId) || !text(lenh.phienId)
      || !Number.isInteger(lenh.year) || lenh.year < 1900 || lenh.year > 9999
      || !Number.isInteger(lenh.month) || lenh.month < 1 || lenh.month > 12
      || !['mua_vao', 'ban_ra'].includes(lenh.huong)) throw loi('HD_LENH_SAI');
  // Một tháng chính xác như HD-2a; không dùng mode=year tự giới hạn năm hiện tại.
  return Object.freeze({ demo: true, phapNhanId: lenh.phapNhanId, phienId: lenh.phienId,
    year: lenh.year, month: lenh.month, huong: lenh.huong });
}

function giuProfile(profile, lenh) {
  if (!doiTuong(profile) || profile.phapNhanId !== lenh.phapNhanId
      || profile.phienId !== lenh.phienId || profile.moi !== true
      || !text(profile.userDataDir) || !path.win32.isAbsolute(profile.userDataDir)
      || !/^[a-z]:[\\/]/i.test(profile.userDataDir)) throw loi('HD_PROFILE_SAI');
  const dir = path.win32.normalize(profile.userDataDir);
  if (dir.toLowerCase().split(/[\\/]/).includes('.browser-profile')
      || dir === path.win32.parse(dir).root || /[. ]$/.test(dir)
      || /[. ](?:[\\/])/.test(dir)) throw loi('HD_PROFILE_SAI');
  const key = dir.toLowerCase().replace(/[\\/]+$/, '');
  if (profileDaDung.has(key) || phienDaDung.has(lenh.phienId)) throw loi('HD_PROFILE_DA_DUNG');
  // Không nhả để dùng lại sau lỗi/hủy; Core/HD-3b mới quản lý dọn/ACK bền vững.
  profileDaDung.add(key);
  phienDaDung.add(lenh.phienId);
  return dir;
}

function choJob(job, opts) {
  return new Promise((resolve, reject) => {
    const state = job.getState();
    if (!state?.emitter || state.running) return reject(loi('HD_JOB_SAI'));
    let failed = false;
    const onEvent = event => {
      if (event?.type === 'error') failed = true;
      if (event?.type === 'done') {
        state.emitter.removeListener('event', onEvent);
        resolve(!failed && event.payload?.ok !== false);
      }
    };
    state.emitter.on('event', onEvent);
    try { job.startJob(opts); } catch {
      state.emitter.removeListener('event', onEvent);
      reject(loi('HD_JOB_LOI'));
    }
  });
}

/** Factories chỉ là seam giả, không phải loader cho nguồn H chưa đáp ứng.
 * kiemPhienWindows/capProfile do Core giả cấp; không tự kiểm bằng cờ caller.
 * taoPortal phải đóng context mở dở nếu launchAndLogin ném lỗi.
 */
function taoBoTaiDemo({ taoJob, taoPortal, capProfile, kiemPhienWindows } = {}) {
  if ([taoJob, taoPortal, capProfile, kiemPhienWindows].some(f => typeof f !== 'function')) {
    throw loi('HD_CAN_SEAM_DEMO');
  }
  return Object.freeze({
    async chay(input, kenh) {
      const lenh = kiemLenh(input);
      let env;
      const contexts = new Set();
      let dongLoi = false;
      try {
        // Truyền snapshot đã chọn field; không truyền env/args/profile do caller chèn.
        if (await kiemPhienWindows(lenh) !== true) throw loi('HD_PHIEN_WINDOWS');
        const userDataDir = giuProfile(await capProfile(lenh), lenh);
        env = await nhanBiMat(kenh, lenh.phapNhanId, lenh.phienId);
        const portal = await taoPortal(Object.freeze({ userDataDir, headless: false }));
        if (!doiTuong(portal) || typeof portal.launchAndLogin !== 'function'
            || portalDaDung.has(portal)) throw loi('HD_PORTAL_SAI');
        portalDaDung.add(portal);
        // Giữ thuật toán portal trong seam; không chuyển thông báo nguồn thô ra ngoài.
        const portalBoc = Object.freeze({
          async launchAndLogin() {
            const session = await portal.launchAndLogin({
              username: env.TAX_USERNAME, password: env.TAX_PASSWORD,
              userDataDir, headless: false, onStatus: () => {},
            });
            if (!session?.context || typeof session.context.close !== 'function') throw loi('HD_PORTAL_SAI');
            const context = session.context;
            contexts.add(context);
            let closing;
            const close = context.close.bind(context);
            // Job nguồn cũng gọi close: đóng tối đa một lần, giữ lỗi để báo Core.
            context.close = () => {
              if (!closing) closing = Promise.resolve().then(close);
              return closing;
            };
            return session;
          },
        });
        const job = await taoJob(Object.freeze({ portal: portalBoc }));
        if (!doiTuong(job) || typeof job.startJob !== 'function'
            || typeof job.getState !== 'function' || jobDaDung.has(job)) throw loi('HD_JOB_SAI');
        jobDaDung.add(job);
        const ok = await choJob(job, {
          mode: 'month', year: lenh.year, month: lenh.month,
          types: [lenh.huong === 'mua_vao' ? 'purchase' : 'sold'], formats: ['xml'], env,
        });
        if (!ok) throw loi('HD_JOB_LOI');
      } catch {
        throw loi('HD_PHIEN_LOI');
      } finally {
        for (const context of contexts) {
          try { await context.close(); } catch { dongLoi = true; }
        }
        if (env) env.TAX_USERNAME = env.TAX_PASSWORD = null;
        if (dongLoi) throw loi('HD_DONG_BROWSER_LOI');
      }
      // done nguồn không chứng minh đầy đủ nhóm, bàn giao Core hay xóa profile.
      return Object.freeze({ trang_thai: 'CHUA_KIEM', ma: 'HD_COVERAGE_CHUA_KIEM' });
    },
  });
}

module.exports = { GIOI_HAN_BI_MAT, NGUON_THAT, nhanBiMat, taoBoTaiDemo };
