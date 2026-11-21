// Dữ liệu xuất thực sự từ thành phần UI để parser Python kiểm lại.
import {readFile, writeFile} from 'node:fs/promises';
import {dom, nap, coreGia, dulieu, nhap, gocGoi} from './core_gia.mjs';
const phieu = JSON.parse(await readFile(new URL('engine.json',gocGoi),'utf8'));
const ketQua = [];
for (const demo of phieu.chay_thu_demo) {
  const core=coreGia({tham_so:demo.tham_so,ds_sheet:[]}); core.nguCanh.nang_luc=demo.nang_luc;
  const man=await nap(dom(),core.KttCore,core.nguCanh);
  ketQua.push({nang_luc:demo.nang_luc,tep_demo:demo.dau_vao.tep_demo,tham_so:man.xuat()});
}
const bo = dulieu.sao(dulieu.MAU.bo_nhom_json);
bo.nhom[0].khi.push({vung:['ten_sheet','nhan_dong'],tat_ca:[['=DEMO','giá đợt #'],['dài','rộng']],khong_co:[]});
const core=coreGia({tham_so:{bo_nhom_json:JSON.stringify(bo)}}), goc=dom();
const man=await nap(goc,core.KttCore,core.nguCanh);
await nhap(goc,'Tên bộ nhóm','Nhóm lồng DEMO');
ketQua.push({nang_luc:'excel.toan_ven@1',tep_demo:'demo/K1-K8-DEMO.xlsx',tham_so:man.xuat()});
await writeFile(process.argv[2], JSON.stringify(ketQua,null,2)+'\n','utf8');
