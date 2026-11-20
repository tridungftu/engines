"""Hợp đồng PL-0, C4/C5 và bytes thật; đã kiểm bằng Core giả (CoreGia)."""

from hashlib import sha256
import json
from pathlib import Path
import re

import pytest
from kho_tri_thuc_sdk.engine import doc_phieu
from kho_tri_thuc_sdk.thu import CoreGia

from e_phan_luong import __version__
from e_phan_luong.chay import app
from kiem_bam_goi import kiem, tinh_kiem_ke
from kiem_doc_lap import kiem_demo, kiem_doc_lap

CHUA_LAM_CON = frozenset({
    "audit.chuan_bi_phan_loai@1",
    "audit.phan_luong_sau_ai@1",
    "audit.phan_luong_hoa_don@1",
    "audit.ghi_ket_qua@1",
})

GOI = Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"
REPO = GOI.parents[2]


def test_doc_phieu_va_nam_nang_luc_co_demo_phan_luong():
    phieu = doc_phieu(GOI / "engine.json")
    assert phieu["phien_ban_manifest"] == 2
    assert phieu["phien_ban"] == __version__ == "0.1.0"
    assert phieu["tuong_thich"]["sdk"] == ">=2.2.0 <3.0.0"
    assert phieu["tai_nguyen"] == {"so_viec_dong_thoi": 1}
    assert any(vd["nang_luc"] == "audit.phan_luong@1" for vd in phieu["chay_thu_demo"])
    assert kiem_demo(GOI) == []
    ket_qua_demo = CoreGia().chay_thu_demo(app)
    assert len(ket_qua_demo) == len(phieu["chay_thu_demo"])
    assert all(kq["trang_thai"] == "XONG" for kq in ket_qua_demo), ket_qua_demo
    assert "giao_dien_quan_tri" not in phieu
    assert phieu["du_lieu"]["goi_migration"] == {
        "ma": "e_phan_luong", "thu_muc": "sql", "tep_kiem_ke": "sql/kiem_ke.json", "phien_ban_du_lieu": 1}
    assert [(n["ma"], n["nhan"], n["tra"]) for n in phieu["nang_luc"]] == [
        ("audit.phan_luong@1", ["tep"], "truong"),
        ("audit.chuan_bi_phan_loai@1", ["tep"], "yeu_cau_ai"),
        ("audit.phan_luong_sau_ai@1", ["tra_loi_ai"], "truong"),
        ("audit.phan_luong_hoa_don@1", ["truong"], "truong"),
        ("audit.ghi_ket_qua@1", ["tep"], "truong")]
    for nl in phieu["nang_luc"]:
        assert nl["gioi_han"] == {"tep_toi_da_mib": 20, "thoi_han_giay": 300}
        assert nl["huy_duoc"] is True


def test_truong_ra_dung_phieu_va_c5():
    truong_phan_luong = {
        "ma_luot": "van_ban", "luong": "van_ban", "can_nguoi_kiem": "co_khong", "canh_bao": "van_ban",
        **{t: "so" for t in ("so_nghiep_vu", "so_do", "so_do_bat_buoc", "so_do_chon_mau", "so_xanh", "so_chua_phan_loai")},
        "tong_tien_do": "so_tien", "tep_json": "tep", "tep_ds_do": "tep",
        "bam_hat_giong": "van_ban", "bam_dau_vao": "van_ban", "phien_ban_engine": "van_ban"}
    truong_ghi = {t: "so" for t in ("so_dong_nhan", "so_trung", "so_ngoai_mau", "so_cap_doi_bac", "so_sua_loai")}
    truong_ghi["phien_ban_engine"] = "van_ban"
    # Phiếu §5.5 bắt buộc so_cap_doi_bac: ngoại lệ số đếm, không trả bậc.
    # Mâu thuẫn với phép grep "bac" tuyệt đối đã ghi rõ trong VIEC.md.
    ngoai_le = {("audit.ghi_ket_qua@1", "so_cap_doi_bac")}
    for nl in app.phieu["nang_luc"]:
        if nl["tra"] != "truong":
            assert "truong_ra" not in nl
            continue
        ds = {t["ma"]: t["kieu"] for t in nl["truong_ra"]}
        assert ds == (truong_ghi if nl["ma"] == "audit.ghi_ket_qua@1" else truong_phan_luong)
        for ma in ds:
            assert (nl["ma"], ma) in ngoai_le or not any(t in ma for t in ("ty_le", "xac_suat", "bac"))


def test_tham_so_dung_tran_mac_dinh_va_pham_vi():
    tran = {"khau": 40, "ma_module": 31, "nguong_json": 4096, "danh_muc_loai_json": 16384,
            "truong_phan_loai": 60, "bo_phan_loai_json": 32768, "khuon_cot_json": 32768,
            "tien_te": 3, "chinh_sach_json": 8192}
    mac_dinh = {"nguong_tin_cay": 0.7, "ty_le_duoi_sad": 0.02, "cua_so_chia_nho_ngay": 7}
    cac_ma = set()
    for nl in app.phieu["nang_luc"]:
        ds = {t["ma"]: t for t in nl["tham_so"]}
        cac_ma.update(ds)
        assert ds["khau"]["bat_buoc"] is True
        assert "mac_dinh" not in ds["khau"]
        assert ("model_uu_tien" in ds) == (nl["ma"] == "audit.chuan_bi_phan_loai@1")
        assert ("loai_nghiep_vu" in ds) == (nl["ma"] == "audit.phan_luong_hoa_don@1")
        for ma, t in ds.items():
            if ma in tran:
                assert t["toi_da"] == tran[ma]
            if ma in mac_dinh:
                assert t["kieu"] == "so"
                assert t["mac_dinh"] == mac_dinh[ma]
            elif ma != "khau":
                assert t["mac_dinh"] == ""
    assert cac_ma == set(tran) | set(mac_dinh) | {
        "ma_prompt", "phien_ban_prompt", "prompt", "model_uu_tien", "loai_nghiep_vu"}


def test_loai_rieng_dung_ten_va_schema_trung_bam():
    assert app.phieu["loai_du_lieu_rieng"] == [
        {"ma": "yeu_cau_ai", "ten": "Yêu cầu hỏi AI"},
        {"ma": "tra_loi_ai", "ten": "Trả lời AI có trích dẫn"}]
    for ma in ("yeu_cau_ai", "tra_loi_ai"):
        ten = ma + ".schema.json"
        goc = (REPO / "_chung" / "contract" / ten).read_bytes()
        chep = (GOI / "contract" / ten).read_bytes()
        # Bản chép giữ nguyên bytes nguồn lúc nhận (Windows: CRLF).
        # Nguồn _chung chưa khóa eol, Linux checkout thành LF. Chỉ chuẩn hóa
        # CRLF/LF trong RAM khi so nguồn; kiểm kê vẫn băm bytes gói nguyên trạng.
        assert sha256(goc.replace(b"\r\n", b"\n")).digest() == sha256(chep.replace(b"\r\n", b"\n")).digest()


def test_lock_giu_nguyen_phien_ban_va_hash_mau():
    assert (GOI / "requirements.lock").read_bytes() == (
        REPO / "e_kiem_excel/goi/e_kiem_excel/requirements.lock").read_bytes()


def test_sau_bang_c4_sql_phieu_cot_he_thong_va_comment():
    cs_ty_le = "bac che_do mau_tu_doi_bac loi_tu_doi_bac mau_sach_toan_bo mau_12t loi_12t loi_sad_12t loi_ngoai_mau_12t diem nhan doi_bac_luc".split()
    mong = {
        "luot": (["ma_luot"], "ma_luot ma_module khau hat_giong bam_dau_vao".split(), 400),
        "dong_luot": (["ma_luot", "ma"], "ma_luot ma ma_module khau ly_do loai nguon_loai".split(), 400),
        "ket_qua_kiem": (["ma_luot", "ma", "khau"], "ma_luot ma khau ma_module loai ket_qua muc_sai nguon_mau nguon_loai_sai".split(), 365),
        "ty_le": (["khau", "loai"], ["khau", "loai"] + cs_ty_le, None),
        "ho_so_hanh_vi": (["khau", "loai"], "khau loai so_nghiep_vu bieu_do bam_doi_tac tong_7_ngay ky_lam_moi".split(), None),
        "chot_ky": (["ky", "khau", "loai"], ["ky", "khau", "loai"] + cs_ty_le, None)}
    he_thong = {"id": "uuid", "phap_nhan_id": "uuid", "row_version": "bigint", "tao_luc": "timestamptz",
                "sua_luc": "timestamptz", "het_han_luc": "timestamptz", "viec_id": "uuid"}
    cot_so = set("bac mau_tu_doi_bac loi_tu_doi_bac mau_sach_toan_bo mau_12t loi_12t loi_sad_12t loi_ngoai_mau_12t diem so_nghiep_vu".split())
    sql = (GOI / "sql/001_tao_ngan.sql").read_text(encoding="utf-8")
    assert not re.search(r"\bjsonb?\b", re.sub(r"'[^']*'|--[^\n]*", "", sql), re.I)
    tao = re.findall(r"CREATE TABLE (eng_e_phan_luong\.\w+) \((.*?)\n\);", sql, re.S)
    assert len(tao) == 6
    assert {n.split(".")[1] for n, _ in tao} == set(mong)
    assert len(app.phieu["ngan_du_lieu"]) == 6
    for b in app.phieu["ngan_du_lieu"]:
        khoa, cot, han = mong[b["bang"]]
        assert b["pham_vi"] == "phap_nhan"
        assert b["khoa"] == khoa
        assert b["duy_nhat"] == [["phap_nhan_id"] + khoa]
        assert b.get("giu_toi_da_ngay") == han
        assert [t["ma"] for t in b["truong"]] == cot
        assert not set(cot) & set(he_thong)
        assert not set(cot) & {"so_tien", "tien_te", "ngay", "ngay_giao_dich", "doi_tac", "noi_dung", "dien_giai"}
        ten = "eng_e_phan_luong." + b["bang"]
        than = dict(tao)[ten]
        sql_cot = dict(re.findall(r"^\s+(\w+) (uuid|bigint|timestamptz|text|numeric)\b", than, re.M))
        assert sql_cot == {**he_thong, **{c: "numeric" if c in cot_so else "timestamptz" if c == "doi_bac_luc" else "text" for c in cot}}
        assert "UNIQUE (" + ", ".join(["phap_nhan_id"] + khoa) + ")" in than
        assert f"COMMENT ON TABLE {ten} IS '" in sql
        assert "phap_nhan_id uuid NOT NULL" in than
        assert "row_version bigint NOT NULL DEFAULT 1" in than
        assert "tao_luc timestamptz NOT NULL DEFAULT now()" in than
        for c in sql_cot:
            chu = re.search(r"COMMENT ON COLUMN " + re.escape(ten + "." + c) + r" IS '([^']+)';", sql)
            assert chu, c
            if c in cot_so:
                assert "\nkieu: so" in chu[1]
        for t in b["truong"]:
            assert t["kieu"] == ("so" if t["ma"] in cot_so else "thoi_diem" if t["ma"] == "doi_bac_luc" else "van_ban")


def test_kiem_ke_toan_bo_bytes_that():
    assert kiem() == len(tinh_kiem_ke()["tep"])
    du_lieu = json.loads((GOI / "sql/kiem_ke.json").read_text(encoding="utf-8"))
    assert du_lieu == tinh_kiem_ke()
    assert "sql/kiem_ke.json" not in {t["duong_dan"] for t in du_lieu["tep"]}


@pytest.mark.parametrize("ma_nang_luc", sorted(CHUA_LAM_CON))
def test_nang_luc_tam_tra_loi_chua_lam(ma_nang_luc):
    nl = {n["ma"]: n for n in app.phieu["nang_luc"]}[ma_nang_luc]
    core = CoreGia()
    loai = nl["nhan"][0]
    if loai == "tep":
        dau_vao = {"loai": "tep", "tep": core.them_tep("lo-DEMO.json", b"{}", "application/json")}
    else:
        dau_vao = {"loai": loai, loai: {}}
    kq = core.chay_thu(app, nl["ma"], dau_vao, {"khau": "ktt_duyet"})
    assert kq["trang_thai"] == "LOI", kq
    assert kq["loi"] == {"ma": "CHUA_LAM", "thong_diep": "Năng lực đang được xây dựng.", "thu_lai_duoc": False}


def test_boc_nhat_ky_khong_lo_noi_dung_ngoai_le(capsys):
    from e_phan_luong.chay import Engine
    phieu = dict(app.phieu, chay_thu_demo=[], nang_luc=[{
        "ma": "demo.loi@1", "ten": "Lỗi DEMO", "nhan": ["van_ban"], "tra": "van_ban",
        "gioi_han": {"thoi_han_giay": 300}}])
    thu = Engine(phieu)

    @thu.nang_luc("demo.loi@1")
    def loi_gia(viec):
        raise ValueError("NOI_DUNG_DEMO_KHONG_DUOC_LO")

    kq = CoreGia().chay_thu(thu, "demo.loi@1", {"loai": "van_ban", "van_ban": "DEMO"})
    assert kq["trang_thai"] == "LOI"
    log = capsys.readouterr().err
    assert "PL_SDK_THONG_BAO" in log
    assert "NOI_DUNG_DEMO_KHONG_DUOC_LO" not in log + json.dumps(kq, ensure_ascii=False)
    assert "Traceback" not in log


def test_kiem_doc_lap_va_chan_vi_pham(tmp_path):
    assert kiem_doc_lap() == []
    # Thử bộ kiểm bằng mẫu vi phạm, không đặt chúng vào gói gửi Core.
    for ma in ("kho_tri_thuc.core", "socket", "subprocess", "sqlite3", "psycopg", "httpx"):
        (tmp_path / "cam.py").write_text("import " + ma, encoding="utf-8")
        assert kiem_doc_lap(tmp_path)
    (tmp_path / "cam.py").write_text('tien_te = "VND"', encoding="utf-8")
    assert any("tiền tệ" in s for s in kiem_doc_lap(tmp_path))
    (tmp_path / "co.pyc").write_bytes(b"DEMO")
    assert any("bytecode" in s for s in kiem_doc_lap(tmp_path))


@pytest.mark.parametrize("duong_dan,noi_dung,co_loi", [
    ("demo/mau.json", b'{"nhan":"DEMO"}', False),
    ("demo/thieu.json", None, True),
    ("demo/mau.json", b'{}', True),
    ("mau.json", b'{"nhan":"DEMO"}', True),
    ("demo/../mau.json", b'{"nhan":"DEMO"}', True),
    (None, None, True),
])
def test_kiem_moi_vi_du_demo_co_tep_va_nhan(tmp_path, duong_dan, noi_dung, co_loi):
    demo = tmp_path / "demo"
    demo.mkdir()
    (demo / "dung.json").write_bytes(b'{"nhan":"DEMO"}')
    if noi_dung is not None:
        (tmp_path / duong_dan).write_bytes(noi_dung)
    # Ví dụ hợp lệ đầu tiên không được che lỗi của ví dụ phía sau.
    phieu = {"chay_thu_demo": [
        {"dau_vao": {"loai": "tep", "tep_demo": "demo/dung.json"}},
        {"dau_vao": {"loai": "tep", "tep_demo": duong_dan}},
    ]}
    (tmp_path / "engine.json").write_text(json.dumps(phieu), encoding="utf-8")
    loi = kiem_demo(tmp_path)
    assert bool(loi) is co_loi
    if co_loi:
        assert len(loi) == 1
        assert "DEMO thứ 2" in loi[0]
