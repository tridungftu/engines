import {readFileSync} from "node:fs";
const ui = new URL("../../goi/e_phan_luong/ui/", import.meta.url);
const data = readFileSync(new URL("du_lieu_tham_so.js", ui), "utf8");
export const diaChiData = "data:text/javascript;base64," + Buffer.from(data).toString("base64");
export const duLieu = await import(diaChiData);
const maMan = readFileSync(new URL("tham_so.js", ui), "utf8").replace('"./du_lieu_tham_so.js"', JSON.stringify(diaChiData));
export const {mount} = await import("data:text/javascript;base64," + Buffer.from(maMan).toString("base64"));
export {maMan, data};
