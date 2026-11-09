'use strict';

// node --test tests/g3_hd_2c.cjs — toàn bộ DEMO, không mạng/browser/tệp thật.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { Readable } = require('node:stream');
const { EventEmitter } = require('node:events');
const { inspect } = require('node:util');
const { spawnSync } = require('node:child_process');
const adapter = require('../engines/e_hoa_don/portal.cjs');
const CANARY = 'DEMO_PASSWORD_HD2C_KHONG_LO';
let seq = 0;
function lenh(extra = {}) {
  return { demo: true, phapNhanId: 'DEMO_PN_1', phienId: `DEMO_PHIEN_${++seq}`,
    year: 2024, month: 2, huong: 'mua_vao', ...extra };
}
function kenh(l, extra = {}) {
  const raw = Buffer.from(JSON.stringify({ username: 'DEMO_USER', password: CANARY,
    phapNhanId: l.phapNhanId, phienId: l.phienId, ...extra }) + '\n');
  return Readable.from([raw.subarray(0, 7), raw.subarray(7)], { objectMode: false });
}
function gia(overrides = {}) {
  const seen = { close: 0, start: 0, portal: [], env: [], opts: [], profile: [] };
  const seams = {
    kiemPhienWindows: async () => true,
    capProfile: async l => {
      const p = { phapNhanId: l.phapNhanId, phienId: l.phienId, moi: true,
        userDataDir: `D:/DEMO/HD2c/${l.phapNhanId}/${l.phienId}` };
      seen.profile.push(p);
      return p;
    },
    taoPortal: async opts => {
      seen.portal.push(opts);
      return { async launchAndLogin(args) {
        assert.equal(args.password, CANARY);
        assert.equal(args.username, 'DEMO_USER');
        assert.equal(args.userDataDir, opts.userDataDir);
        assert.equal(args.headless, false);
        args.onStatus(CANARY);
        return { context: { async close() { seen.close++; } }, token: CANARY, page: {} };
      } };
    },
    taoJob: async ({ portal }) => {
      const emitter = new EventEmitter();
      return {
        getState: () => ({ emitter, running: false }),
        startJob(opts) {
          seen.start++;
          seen.env.push(opts.env);
          seen.opts.push(opts);
          assert.equal(opts.env.TAX_PASSWORD, CANARY);
          queueMicrotask(async () => {
            try {
              const session = await portal.launchAndLogin({ userDataDir: 'D:/SAI', headless: true });
              await session.context.close();
              emitter.emit('event', { type: 'log', payload: { msg: CANARY } });
              emitter.emit('event', { type: 'done', payload: { ok: true, token: CANARY } });
            } catch (e) {
              emitter.emit('event', { type: 'error', payload: { message: e.message } });
              emitter.emit('event', { type: 'done', payload: { ok: false } });
            }
          });
        },
      };
    },
    ...overrides,
  };
  return { bo: adapter.taoBoTaiDemo(seams), seen, seams };
}

test('stdin/handle vào object RAM, JSON/inspect không lộ canary', async () => {
  const l = lenh();
  const env = await adapter.nhanBiMat(kenh(l), l.phapNhanId, l.phienId);
  assert.equal(env.TAX_PASSWORD, CANARY);
  assert.equal(JSON.stringify(env), '{}');
  assert.equal(inspect(env), 'BiMat(<an>)');
  env.TAX_PASSWORD = env.TAX_USERNAME = null;
});

test('đúng opts job nguồn, portal có màn hình, chỉ đóng browser một lần', async () => {
  const l = lenh();
  const { bo, seen } = gia();
  const kq = await bo.chay(l, kenh(l));
  assert.deepEqual(kq, { trang_thai: 'CHUA_KIEM', ma: 'HD_COVERAGE_CHUA_KIEM' });
  assert.equal(seen.close, 1);
  assert.equal(seen.env[0].TAX_PASSWORD, null);
  assert.equal(seen.env[0].TAX_USERNAME, null);
  assert.deepEqual(seen.opts[0].types, ['purchase']);
  assert.deepEqual(seen.opts[0].formats, ['xml']);
  assert.equal(seen.opts[0].mode, 'month');
  assert.equal(seen.opts[0].month, 2);
  assert.equal(seen.opts[0].year, 2024);
  assert.ok(!JSON.stringify(kq).includes(CANARY));
});

test('profile riêng giữa pháp nhân và giữa các phiên đồng thời', async () => {
  const { bo, seen } = gia();
  const ls = [lenh(), lenh(), lenh({ phapNhanId: 'DEMO_PN_2', huong: 'ban_ra' })];
  await Promise.all(ls.map(l => bo.chay(l, kenh(l))));
  assert.equal(new Set(seen.portal.map(p => p.userDataDir.toLowerCase())).size, 3);
  assert.equal(seen.close, 3);
  assert.deepEqual(seen.opts[2].types, ['sold']);
});

test('profile đã dùng, kể cả khác hoa/thường và dấu slash, bị chặn', async () => {
  const { bo, seen } = gia({ capProfile: async l => ({ ...l, moi: true,
    userDataDir: 'D:/DEMO/HD2c/PROFILE_CHUNG' }) });
  const a = lenh();
  await bo.chay(a, kenh(a));
  const b = lenh({ phapNhanId: 'DEMO_KHAC' });
  const other = gia({ capProfile: async l => ({ ...l, moi: true,
    userDataDir: 'd:\\demo\\hd2c\\profile_chung\\' }) });
  await assert.rejects(other.bo.chay(b, kenh(b)), { code: 'HD_PHIEN_LOI' });
  assert.equal(seen.start, 1);
  assert.equal(other.seen.start, 0);
});

test('profile thuộc sai pháp nhân/phiên, cũ, nguồn cố định hoặc không tuyệt đối bị chặn', async () => {
  for (const extra of [{ phapNhanId: 'DEMO_SAI' }, { phienId: 'DEMO_SAI' }, { moi: false },
    { userDataDir: 'D:relative' }, { userDataDir: 'D:/DEMO/.browser-profile' },
    { userDataDir: 'D:/DEMO/.BROWSER-PROFILE' },
    { userDataDir: 'D:/' }, { userDataDir: 'D:/DEMO/profile.' }]) {
    const l = lenh();
    const { bo, seen } = gia({ capProfile: async x => ({ ...x, moi: true,
      userDataDir: `D:/DEMO/${x.phienId}`, ...extra }) });
    await assert.rejects(bo.chay(l, kenh(l)), { code: 'HD_PHIEN_LOI' });
    assert.equal(seen.start, 0);
  }
});

test('chưa kiểm Windows/tài khoản/ACL thì không cấp profile hay đọc bí mật', async () => {
  const l = lenh();
  const { bo, seen } = gia({ kiemPhienWindows: async () => false });
  await assert.rejects(bo.chay(l, kenh(l)), { code: 'HD_PHIEN_LOI' });
  assert.equal(seen.profile.length, 0);
  assert.equal(seen.start, 0);
});

test('lệnh chỉ DEMO và tháng hợp lệ, bỏ qua env/args caller chèn', async () => {
  const { bo, seen } = gia();
  for (const extra of [{ demo: false }, { month: 0 }, { month: 13 }, { year: 2024.5 }, { huong: 'khac' }]) {
    const l = lenh(extra);
    await assert.rejects(bo.chay(l, kenh(l)), { code: 'HD_LENH_SAI' });
  }
  const l = lenh({ env: { TAX_PASSWORD: 'SAI' }, args: ['SAI'], userDataDir: 'D:/SAI' });
  await bo.chay(l, kenh(l));
  assert.equal(seen.start, 1);
  assert.equal(seen.opts[0].args, undefined);
});

test('frame lỗi, quá dài, UTF8 hỏng, sai binding và nhiều frame không lộ bí mật', async () => {
  const l = lenh();
  const inputs = [Buffer.from(CANARY + '\n'), Buffer.alloc(16385, 65),
    Buffer.from([0xff, 10]), Buffer.from('{}\n{}\n'), Buffer.from('{}'),
    Buffer.from(JSON.stringify(CANARY) + '\n'), Buffer.from('true\n'), Buffer.from('17\n'),
    kenh(l, { phienId: 'DEMO_SAI' }), kenh(l, { phapNhanId: 'DEMO_SAI' }),
    kenh(l, { password: '' }), kenh(l, { them: CANARY })];
  for (const input of inputs) {
    const stream = Buffer.isBuffer(input) ? Readable.from([input]) : input;
    await assert.rejects(adapter.nhanBiMat(stream, l.phapNhanId, l.phienId), e => {
      assert.equal(e.code, 'HD_BI_MAT_SAI');
      assert.ok(!inspect(e).includes(CANARY));
      assert.equal(e.cause, undefined);
      return true;
    });
  }
});

test('không nhận đường dẫn/fd/tệp; không đọc hai lần một handle', async () => {
  const l = lenh();
  for (const input of ['D:/DEMO/password', 3, Object.assign(kenh(l), { path: 'D:/DEMO/password' })]) {
    await assert.rejects(adapter.nhanBiMat(input, l.phapNhanId, l.phienId), { code: 'HD_KENH_BI_MAT' });
  }
  const stream = kenh(l);
  await adapter.nhanBiMat(stream, l.phapNhanId, l.phienId);
  await assert.rejects(adapter.nhanBiMat(stream, l.phapNhanId, l.phienId), { code: 'HD_KENH_BI_MAT' });
});

test('lỗi portal/job được che và mật khẩu được bỏ sau khi job thực sự kết thúc', async () => {
  let env;
  const { bo } = gia({ taoJob: async () => ({
    getState: () => ({ emitter: new EventEmitter(), running: false }),
    startJob(opts) { env = opts.env; throw new Error(CANARY); },
  }) });
  const l = lenh();
  await assert.rejects(bo.chay(l, kenh(l)), e => {
    assert.equal(e.code, 'HD_PHIEN_LOI');
    assert.ok(!inspect(e).includes(CANARY));
    return true;
  });
  assert.equal(env.TAX_PASSWORD, null);
  const failed = gia({ taoPortal: async () => ({ launchAndLogin: async () => { throw new Error(CANARY); } }) });
  const b = lenh();
  await assert.rejects(failed.bo.chay(b, kenh(b)), { code: 'HD_PHIEN_LOI' });
  assert.equal(failed.seen.env[0].TAX_PASSWORD, null);
});

test('lỗi đóng browser giữ chặn profile, không giả thành công', async () => {
  const { bo, seen } = gia({ taoPortal: async () => ({ launchAndLogin: async () => ({
    context: { close: async () => { throw new Error(CANARY); } }, token: CANARY,
  }) }) });
  const l = lenh();
  await assert.rejects(bo.chay(l, kenh(l)), { code: 'HD_DONG_BROWSER_LOI' });
  assert.equal(seen.env[0].TAX_PASSWORD, null);
  await assert.rejects(bo.chay(l, kenh(l)), { code: 'HD_PHIEN_LOI' });
});

test('module không nạp nguồn/server/.env hay I/O/mạng, kể cả khi env/argv có canary', () => {
  const script = `
    const Module = require('node:module');
    const load = Module._load;
    const allowed = new Set(['node:path', 'node:util']);
    const file = process.argv[1];
    Module._load = function(id, ...rest) {
      if (id !== file && !allowed.has(id)) throw Error('NAP_NGOAI_SEAM');
      return load.call(this, id, ...rest);
    };
    const a = require(file);
    if (a.NGUON_THAT.trang_thai !== 'CHUA_KIEM') process.exit(2);
    try { a.taoBoTaiDemo(); process.exit(3); }
    catch (e) { if (e.code !== 'HD_CAN_SEAM_DEMO') process.exit(4); }
  `;
  const child = spawnSync(process.execPath, ['-e', script,
    require.resolve('../engines/e_hoa_don/portal.cjs'), CANARY],
  { encoding: 'utf8', env: { ...process.env, TAX_PASSWORD: CANARY }, timeout: 10000 });
  assert.equal(child.status, 0, child.stderr);
  assert.equal(child.stdout, '');
  assert.equal(child.stderr, '');
});
