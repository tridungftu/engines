import {duLieu as d} from "./nap_man.mjs";
const nl = "audit.phan_luong@1";
const mau = Object.fromEntries(d.CAC_O.map(k => [k, d.vietJson(d.MAU[k])]));
const ds = [{ten: "Nguyên mẫu DEMO", tham_so: mau}];
const mo = d.docThamSo(mau, nl);
mo.du_lieu.nguong_json.pm.so = "999999999999999999.123456";
d.doi(mo, "nguong_json", mo.du_lieu.nguong_json);
mo.du_lieu.chinh_sach_json = d.docJson('{"he_so":{"NGAY_NGHI":2.5},"toi_thieu_ho_so_doi_tac_moi":5}');
d.doi(mo, "chinh_sach_json", mo.du_lieu.chinh_sach_json);
ds.push({ten: "Sửa ngưỡng lớn và chính sách DEMO", tham_so: d.xuatThamSo(mo)});
const lon = d.docThamSo(mau, nl);
lon.du_lieu.nguong_json.pm.so = d.docJson("999999999999999999.123456");
d.doi(lon, "nguong_json", lon.du_lieu.nguong_json);
ds.push({ten: "Số tiền JSON không bọc chuỗi DEMO", tham_so: d.xuatThamSo(lon)});
for (const cs of ["{}", '{"bac":[0.5,0.1],"nguong_xuong":[0.1],"mau_toi_thieu":[25]}', '{"he_so":{"SO_TRON":3}}',
  '{"bac":[0.3000000000000000002,0.3000000000000000001],"nguong_xuong":[0.1],"mau_toi_thieu":[30],"do_tin_cay":0.9999999999999999999}'])
  ds.push({ten: "Chính sách riêng DEMO", tham_so: {...mau, chinh_sach_json: cs}});
ds.push({ten: "Giữ nghĩa rỗng DEMO", tham_so: Object.fromEntries(d.CAC_O.map(k => [k, ""]))});
for (const [k, v] of [["danh_muc_loai_json", [{ma: "demo", ten: "DEMO", mo_ta: ""}, {ma: "demo", ten: "DEMO trùng", mo_ta: ""}]],
  ["bo_phan_loai_json", {phien_ban: 1, quy_tac: [{loai: "khong_co_demo", khi: [{tat_ca: [["DEMO"]]}]}]}],
  ["nguong_json", {...d.MAU.nguong_json, sad: {so: "3000000001", tien_te: "VND"}}],
  ["chinh_sach_json", {bac: [0.1, 0.2]}], ["chinh_sach_json", {he_so: {NHAP_TAY: 0.9}}],
  ["khuon_cot_json", {...d.MAU.khuon_cot_json, cot: [{ma: "ma", tu_khoa: ["Mã"], bat_buoc: true}]}]])
  ds.push({ten: "Từ chối cấu trúc sai DEMO", tham_so: {...mau, [k]: d.vietJson(v)}});
console.log(JSON.stringify(ds.map(x => ({...x, hop_le: !d.kiemThamSo(d.docThamSo(x.tham_so, nl), nl).length}))));
