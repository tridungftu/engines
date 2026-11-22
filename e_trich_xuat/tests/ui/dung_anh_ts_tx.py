"""Dựng trang DEMO không mạng bằng màn thật + KttCore giả để chụp headless."""
import json
from pathlib import Path
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
GOC = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(GOC / "e_trich_xuat/goi/e_trich_xuat"))
from e_trich_xuat.soan_bo import ham_thao_tac


def dung():
    bo = {"phien_ban":1,"module":"module_demo","loai_hop_dong":"DEMO","phien_ban_bo":"demo-1","quy_tac":[],
          "cac_dong":[{"ma":"TT-01","nhom":"Thông tin chung","mo_ta":"Trích tên hợp đồng và tên các bên theo văn bản DEMO.",
                       "tk":"thông tin; @mo_dau","bk":"tên hợp đồng","dung":True,"muc":1,"bat_buoc":"","loai_tru":"","luon_cloud":False}]}
    kq = ham_thao_tac(SimpleNamespace(dau_vao={"lenh":"kiem_bo","bo":bo}))
    assert kq["dat"]
    ma = (GOC / "e_trich_xuat/goi/e_trich_xuat/ui/soan_bo_tham_so.js").read_text(encoding="utf-8")
    ma = ma.replace("export async function nap", "async function nap").replace("export default nap;", "")
    script = "const kq=" + json.dumps(kq,ensure_ascii=False) + ";\n" + ma + """
const KttCore={engine(ma){if(ma!=="e_trich_xuat")throw Error();return {thao_tac:async()=>structuredClone(kq)};}};
await nap({goc:document.getElementById("goc"),KttCore,tham_so:kq.tham_so});
document.documentElement.dataset.daNap="true";
"""
    html = """<!doctype html><html lang="vi"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'none'; img-src 'none'">
<title>TS-TX · DEMO bằng KttCore giả</title>
<style>body{margin:0;background:#f4f6fa;padding:24px} .demo{max-width:1180px;margin:auto;color:#63768a;font:14px 'Segoe UI',Arial,sans-serif}@media(max-width:700px){body{padding:12px}}</style>
<p class="demo">DEMO · Bộ tham số của module · KttCore giả · 21/11/2026</p><main id="goc"></main>
<script type="module">""" + script.replace("</script", "<\\/script") + "</script></html>"
    dich = GOC / "e_trich_xuat/docs/anh-ts-tx"
    dich.mkdir(parents=True,exist_ok=True)
    p = dich / "DEMO-ts-tx.html"
    p.write_text(html,encoding="utf-8")
    print(p)


if __name__ == "__main__":
    dung()
