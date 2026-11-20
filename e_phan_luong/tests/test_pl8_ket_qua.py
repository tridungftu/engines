"""PL-8 tích hợp: đã kiểm bằng Core giả (CoreGia), chỉ dữ liệu DEMO.

jsonschema chỉ là dependency test, không đưa vào requirements runtime.
CC-5 được kiểm bằng wheel SDK thật; mock JS không chứng minh quyền Core thật.
"""
from io import BytesIO
import json
from pathlib import Path
import shutil
import unicodedata
from zipfile import ZipFile

from jsonschema import Draft202012Validator, ValidationError
import openpyxl
import pytest
from kho_tri_thuc_sdk.engine import doc_phieu, LoiPhieu, Viec
from kho_tri_thuc_sdk.thu import CoreGia

from e_phan_luong import chon_mau, kieu, xuat_excel
from e_phan_luong.chay import app
from e_phan_luong.ket_qua import doc_ket_qua_json


TESTS = Path(__file__).resolve().parent
GOI = TESTS.parent / "goi/e_phan_luong"
DEMO = TESTS / "demo"
SCHEMA = json.loads((TESTS / "schema/tep_json.schema.json").read_text(encoding="utf-8"))
KIEM = Draft202012Validator(SCHEMA)
MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
KHAU = "ktt_duyet"
HAT = bytes(range(32))


def tham_so(khau=KHAU):
    return {"khau": khau, "truong_phan_loai": "dien_giai", **{
        ten: (DEMO / tep).read_text(encoding="utf-8") for ten, tep in (
            ("danh_muc_loai_json", "danh-muc-loai-DEMO.json"),
            ("bo_phan_loai_json", "bo-phan-loai-DEMO.json"),
        )}}


def ma_hoa(du_lieu):
    return json.dumps(du_lieu, ensure_ascii=False).encode("utf-8")


def phan_luong(core, du_lieu, khau=KHAU):
    tep = core.them_tep("lo-DEMO.json", du_lieu, "application/json")
    kq = core.chay_thu(app, "audit.phan_luong@1", {"loai": "tep", "tep": tep}, tham_so(khau))
    assert kq["trang_thai"] == "XONG", kq
    truong = kq["ket_qua"]["truong"]
    tep_json = json.loads(core.doc_tep(truong["tep_json"]["tep_id"]))
    KIEM.validate(tep_json)
    return truong, tep_json


@pytest.fixture(autouse=True)
def ghim_hat_giong(monkeypatch):
    monkeypatch.setattr(chon_mau, "sinh_hat_giong", lambda: HAT)


def bo_dau(chu):
    return "".join(c for c in unicodedata.normalize("NFD", chu)
                   if unicodedata.category(c) != "Mn").lower().replace("đ", "d").replace("_", " ")


@pytest.mark.parametrize("khau", ["kt_kiem", KHAU, "cfo_duyet"])
def test_500_demo_excel_dung_dong_do_va_c5(khau):
    core = CoreGia()
    truong, tep_json = phan_luong(core, (DEMO / "lo-500-DEMO.json").read_bytes(), khau)
    tep = truong["tep_ds_do"]
    assert tep["ten"] == "ds-can-kiem.xlsx" and tep["mime"] == MIME_XLSX
    raw = core.doc_tep(tep["tep_id"])
    assert len(raw) == tep["kich_thuoc"]
    wb = openpyxl.load_workbook(BytesIO(raw))
    try:
        ws = wb["Can kiem"]
        ds_do = [d for d in tep_json["nghiep_vu"] if d["luong"] == "do"]
        assert len(ds_do) == truong["so_do"] > 0
        assert ws.max_row == len(ds_do) + 2
        assert [r[0] for r in ws.iter_rows(min_row=3, values_only=True)] == [d["ma"] for d in ds_do]
        assert (ws["B1"].value, ws["D1"].value) == (truong["ma_luot"], khau)
        for sheet in wb:
            for row in sheet:
                for cell in row:
                    assert cell.data_type != "f"
                    assert not any(c in bo_dau(str(cell.value or ""))
                                   for c in ("ty le", "xac suat", "bac", "hat giong"))
        assert all(c.value is None for r in ws.iter_rows(min_row=3, min_col=6) for c in r)
    finally:
        wb.close()
    assert HAT.hex().encode() not in ma_hoa(tep_json)
    for nut in [truong, tep_json, *tep_json["nghiep_vu"]]:
        assert not set(nut) & {"p", "ty_le", "xac_suat", "bac", "hat_giong", "he_so"}


@pytest.mark.parametrize("rong", [False, True])
def test_toan_xanh_hoac_rong_khong_tai_excel(monkeypatch, rong):
    core = CoreGia()
    lo = json.loads((DEMO / "lo-500-DEMO.json").read_bytes())
    lo["nghiep_vu"] = [] if rong else [{
        "ma": "PC-DEMO-XANH", "ngay": "2026-11-16", "loai": "chi_phi_khac",
        "so_tien": {"so": "1000000", "tien_te": "VND"}}]
    monkeypatch.setattr(chon_mau, "duoc_chon", lambda *a: False)
    def cam(*a, **kw):
        pytest.fail("Không có Đỏ thì không dựng Excel")
    monkeypatch.setattr(xuat_excel, "lap_ds_do", cam)
    truong, tep_json = phan_luong(core, ma_hoa(lo))
    assert truong["tep_ds_do"] is None
    assert truong["luong"] == "xanh" and truong["so_do"] == 0
    assert all(d["luong"] == "xanh" for d in tep_json["nghiep_vu"])


def test_khu_hoi_nguoi_kiem_dien_excel_gui_json_roi_ghi_ngan():
    core = CoreGia()
    lo = json.loads((DEMO / "lo-500-DEMO.json").read_bytes())
    truong, _ = phan_luong(core, ma_hoa(lo))
    wb = openpyxl.load_workbook(BytesIO(core.doc_tep(truong["tep_ds_do"]["tep_id"])))
    try:
        ws = wb["Can kiem"]
        ma = [ws.cell(r, 1).value for r in (3, 4, 5)]
        loai_cu = ws["D4"].value
        nguon_cu = ws["E4"].value
        loai_dung = next(d["ma"] for d in json.loads(tham_so()["danh_muc_loai_json"])
                         if d["ma"] != loai_cu)
        ws["F3"], ws["F4"], ws["F5"] = "dat", "sai", "khong_kiem"
        ws["G4"], ws["H4"], ws["I4"] = "1000000.123456", "VND", loai_dung
        out = BytesIO()
        wb.save(out)
    finally:
        wb.close()
    gui = xuat_excel.doc_ds_do_da_ghi(out.getvalue())
    assert len(gui["ket_qua"]) == 3  # Các dòng chưa điền không được gửi.
    assert [d["ma"] for d in gui["ket_qua"]] == ma
    assert all(d["ma_luot"] == truong["ma_luot"] and d["khau"] == KHAU for d in gui["ket_qua"])
    gui["nguong"] = lo["nguong"]  # Module ghép ngưỡng, không có trong Excel.
    da_doc = doc_ket_qua_json(ma_hoa(gui))
    assert str(da_doc.dong[1].so_tien_sai.so) == "1000000.123456"
    tep = core.them_tep("ket-qua-kiem-DEMO.json", ma_hoa(gui), "application/json")
    ts = {cot: tham_so()[cot] for cot in ("khau", "danh_muc_loai_json")}
    kq = core.chay_thu(app, "audit.ghi_ket_qua@1", {"loai": "tep", "tep": tep}, ts)
    assert kq["trang_thai"] == "XONG", kq
    kq = kq["ket_qua"]["truong"]
    assert (kq["so_dong_nhan"], kq["so_trung"], kq["so_ngoai_mau"], kq["so_sua_loai"]) == (3, 0, 0, 1)
    dong = {d["ma"]: d for d in core.xem_ngan(app.ma, "ket_qua_kiem")}
    assert {m: dong[m]["ket_qua"] for m in ma} == dict(zip(ma, ("dat", "sai", "khong_kiem")))
    assert dong[ma[1]]["loai"] == loai_dung
    assert dong[ma[1]]["muc_sai"] == "nho"
    assert dong[ma[1]]["nguon_loai_sai"] == nguon_cu


def test_moi_tep_json_chay_thu_demo_hop_schema():
    core = CoreGia()
    for kq in core.chay_thu_demo(app):
        assert kq["trang_thai"] == "XONG", kq
        truong = kq["ket_qua"]["truong"]
        KIEM.validate(json.loads(core.doc_tep(truong["tep_json"]["tep_id"])))


def test_schema_dong_bo_ma_cong_bo():
    Draft202012Validator.check_schema(SCHEMA)
    dong = SCHEMA["$defs"]["dong"]["properties"]
    assert dong["ly_do"]["items"]["enum"] == list(kieu.THU_TU_LY_DO)
    assert dong["co"]["items"]["enum"] == list(kieu.THU_TU_CO)
    assert dong["nguon_loai"]["enum"] == list(kieu.CAC_NGUON_LOAI)


@pytest.mark.parametrize("o_dong", [False, True])
@pytest.mark.parametrize("cot", ["ty_le", "xac_suat", "bac", "hat_giong", "cot_la"])
def test_schema_tu_choi_truong_la_va_thong_tin_noi_bo(o_dong, cot):
    _, tep = phan_luong(CoreGia(), (GOI / "demo/lo-nho-DEMO.json").read_bytes())
    (tep["nghiep_vu"][0] if o_dong else tep)[cot] = "DEMO"
    with pytest.raises(ValidationError):
        KIEM.validate(tep)


def test_upload_excel_loi_khong_ghi_luot_thanh_cong(monkeypatch):
    from e_phan_luong.loi import LoiNghiepVu
    goc = Viec.tai_tep_ra
    def tai(viec, ten, du_lieu, mime):
        if mime == MIME_XLSX:
            raise LoiNghiepVu("DEMO_TAI_TEP", "Không tải được tệp DEMO.")
        return goc(viec, ten, du_lieu, mime)
    monkeypatch.setattr(Viec, "tai_tep_ra", tai)
    core = CoreGia()
    tep = core.them_tep("lo-DEMO.json", (GOI / "demo/lo-nho-DEMO.json").read_bytes(), "application/json")
    kq = core.chay_thu(app, "audit.phan_luong@1", {"loai": "tep", "tep": tep}, tham_so())
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "DEMO_TAI_TEP"
    assert core.xem_ngan(app.ma, "luot") == core.xem_ngan(app.ma, "dong_luot") == []


def test_cc5_doc_phieu_sdk220_tu_choi_khai_bao_admin(tmp_path):
    goi = tmp_path / "goi-DEMO"
    shutil.copytree(GOI, goi)
    tep = goi / "engine.json"
    phieu = doc_phieu(tep)
    assert "giao_dien_quan_tri" not in phieu
    phieu["giao_dien_quan_tri"] = [{"ma": "bang_ty_le", "ten": "Bảng tỷ lệ kiểm tra",
                                  "tep": "ui/bang_ty_le.js", "quyen": "admin_core"}]
    tep.write_bytes(ma_hoa(phieu))
    with pytest.raises(LoiPhieu) as err:
        doc_phieu(tep)
    assert 'trường lạ "giao_dien_quan_tri"' in str(err.value)
    # Đối chiếu wheel thật: không coi KttCore giả là SDK đã hỗ trợ.
    wheel = GOI.parents[2] / "docs/goi-gui-engine/sdk-2.2.0/kho_tri_thuc_sdk-2.2.0-py3-none-any.whl"
    with ZipFile(wheel) as z:
        js = z.read("kho_tri_thuc_sdk/trinh_duyet.js").decode("utf-8")
    assert "function engine(" not in js
