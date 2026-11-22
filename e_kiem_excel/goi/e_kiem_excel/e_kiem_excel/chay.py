"""Cổng SDK kiểm an toàn tệp; kiểm toàn vẹn K1–K8 và báo cáo trong RAM."""

from hashlib import sha256

from kho_tri_thuc_sdk.engine import Engine, LoiDuongTruyen, LoiNghiepVu

from .nhan_dien import CAU_VUOT_TRAN, TEP_TOI_DA_BYTE, kiem_tep
from .so_do import SoDo
from .kiem_tra import KiemTra, ma_hoa_json
from .bao_cao import ghi


app = Engine.tu_khai_bao("engine.json")


def _doc_va_kiem(viec):
    tep = viec.dau_vao["tep"]
    viec.kiem_huy()
    try:
        with viec.mo_tep(tep["tep_id"]) as luong:
            raw = bytearray()
            while len(raw) <= TEP_TOI_DA_BYTE:
                viec.kiem_huy()
                khoi = luong.read(min(64 * 1024, TEP_TOI_DA_BYTE + 1 - len(raw)))
                if not khoi:
                    break
                raw.extend(khoi)
    except LoiDuongTruyen as loi:
        if loi.ma != "VUOT_GIOI_HAN_KICH_THUOC":
            raise
        raise LoiNghiepVu("VUOT_GIOI_HAN", CAU_VUOT_TRAN) from None
    kiem_tep(raw, tep["ten"], kiem_huy=viec.kiem_huy)
    viec.kiem_huy()
    return bytes(raw)


@app.nang_luc("excel.toan_ven@1")
def kiem_toan_ven(viec):
    raw = _doc_va_kiem(viec)
    sd = SoDo(raw)
    try:
        kt = KiemTra(sd, viec.tham_so).chay(viec)
        bam = "sha256:" + sha256(raw).hexdigest()
        phien_ban = "e_kiem_excel " + app.phieu["phien_ban"]
        chi_tiet = kt.ket_qua_json(bam, phien_ban)
        noi_dung_json = ma_hoa_json(chi_tiet)
        noi_dung_bao_cao = ghi(kt)
        viec.kiem_huy()
        tep_json = viec.tai_tep_ra("toan-ven.json", noi_dung_json, "application/json")
        viec.kiem_huy()
        tep_bao_cao = viec.tai_tep_ra("bao-cao-toan-ven.xlsx", noi_dung_bao_cao,
                                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        return {"loai": "truong", "truong": {
            "so_co_cao": sum(p["muc"] == "Cao" for p in kt.ph),
            "so_co_trung_binh": sum(p["muc"] == "Trung bình" for p in kt.ph),
            "so_kiem_soat": sum(p["muc"] == "Kiểm soát" for p in kt.ph),
            "so_ngoai_nhom": kt.so_ngoai_nhom, "o_dich": kt.kq['dich'], "tep_bao_cao": tep_bao_cao,
            "da_tinh_lai": not any(d[8] for d in kt.kq["sheet"]),
            "co_lien_ket_ngoai": bool(kt._ngoai_o),
            "tep_json": tep_json, "bam_dau_vao": bam, "phien_ban_engine": phien_ban}}
    finally:
        sd.dong()


@app.nang_luc("excel.doc_bang@1")
def doc_bang(viec):
    from .doc_bang import doc_klgt
    from .doc_tong_quat import doc_tong_quat

    raw = _doc_va_kiem(viec)
    phien_ban = f"{app.phieu['ma']} {app.phieu['phien_ban']}"
    doc = doc_tong_quat if viec.tham_so.get("khuon") == "tong_quat" else doc_klgt
    truong, noi_dung = doc(raw, viec.tham_so, phien_ban, viec.kiem_huy)
    truong["tep_json"] = viec.tai_tep_ra("bang-da-doc.json", noi_dung, "application/json")
    return {"loai": "truong", "truong": truong}


if __name__ == "__main__":
    app.chay()
