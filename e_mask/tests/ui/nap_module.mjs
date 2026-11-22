// Nạp ESM không cần package.json/type=module, dùng được với Node 18+ trên Linux.
// Chỉ thay địa chỉ import và base tài nguyên; không thay logic của màn.
import { readFile } from 'node:fs/promises';
export async function napModule() {
  const base = new URL('../../goi/e_mask/ui/', import.meta.url);
  const duyet = await readFile(new URL('duyet_dinh_danh.js', base), 'utf8');
  const duyetUrl = `data:text/javascript;base64,${Buffer.from(duyet).toString('base64')}`;
  const tep = new URL('cau_hinh.js', base);
  const nguon = (await readFile(tep, 'utf8'))
    .replace("'./duyet_dinh_danh.js'", JSON.stringify(duyetUrl))
    .replaceAll('import.meta.url', JSON.stringify(tep.href));
  return import(`data:text/javascript;base64,${Buffer.from(nguon).toString('base64')}`);
}
