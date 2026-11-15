"""Regression E6 giá trị + dẫn chứng; bộ chuẩn DEMO đã được lead duyệt 15/11/2026.

Băng trả lời rỗng/null dưới đây chỉ kiểm cơ chế. Không gán nhãn được lead
chấp nhận, không tạo file ở tham-chieu và không tự chứng nhận tương đương.
"""

from copy import deepcopy
import io
import json
from pathlib import Path
import socket

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia

from e_trich_xuat.tham_so import bam_bytes, doc_bo, json_bytes
import kiem_e6 as e6
from doi_chieu_cu_e6 import ThieuBangAI, chay_mac_dinh_chuyen_tiep
from mau_docx import NUM, goi_docx, mau_track, p, so
from mau_tx3 import app_tx3, ts_demo


@pytest.fixture
def dm():
    return e6.kiem_nguon()[0]


def demo_thuong():
    # Không có bảng ô gộp: giữ cùng nền text để tách sai khác câu hỏi.
    return goi_docx(p("DEMO — Hợp đồng số DEMO-001") + so("Giá trị hợp đồng")
                   + p("Giá trị hợp đồng là 1.000.000 VND."), numbering=NUM)


def bang_ai_cu(thuong=False):
    # 1 lượt dò; 3 nhóm (thường)/2 nhóm (Track) và 5 nhóm rà lại.
    return {"tim_vi_tri": [{}], "hoi_trich": [[], [], [], [], [], [], []] + ([[]] if thuong else [])}


def null_ai(dm):
    return {r["ma"]: {"gia_tri": None, "don_vi": None, "ghi_chu": None, "trich_dan": []}
            for r in dm.cac_dong}


def ts_bo(dm, module="DEMO-crm"):
    return ts_demo(e6.tao_snapshot(dm, module), prompt="Chỉ trích từ tài liệu DEMO.",
                   ngan_sach_token_vao=100000)


def test_xlsx_that_37_thu_tu_370_o_va_ba_bam_tach_biet(dm):
    _, r = e6.kiem_nguon()
    assert r["bam_xlsx"] == "sha256:" + e6.BAM_XLSX_CU
    assert r["bam_noi_dung_e1"] == "6b8190a73e73ced8784fb22e3339a42d72785826ae15b1a499955facb4d65812"
    assert len({r["bam_xlsx"], "sha256:" + r["bam_noi_dung_e1"], r["bam_snapshot_json_DEMO"]}) == 3
    assert r["nguyen_van_10_cot"] and r["thu_tu_37_ma"]


@pytest.mark.parametrize("a,b,offset", [(b"abc", b"abd", 2), (b"abc", b"abc ", 3),
    (b"", b"x", 0), ("ắ".encode(), "ắ".encode(), 0), (b"a\r\n", b"a\n", 1)])
def test_sai_mot_byte_khong_strip_nfc_hoac_doi_crlf(a, b, offset):
    kq = e6.so_byte(a, b)
    assert not kq["trung_byte"] and kq["byte_khac_dau"] == offset
    assert e6.so_byte(a, a)["trung_byte"]


@pytest.mark.parametrize("phan", e6.CAC_PHAN)
def test_bao_cao_byte_giu_nguyen_ca_phan_chi_tham_khao(phan):
    a = {k: b"DEMO" for k in e6.CAC_PHAN}
    b = {**a, phan: b"DEM0"}
    assert not all(r["trung_byte"] for r in e6.so_cac_phan(a, b).values())


@pytest.mark.parametrize("doi", ["thu_tu", "cot", "cau_hoi", "bang"])
def test_du_37_van_khong_mien_sai_khac(dm, doi):
    v = {"bo_10_cot": [e6.e1.HEADER] + e6.dong_nguyen_van(dm.cac_dong),
         "tham_so": dm.tham_so, "van_ban": "DEMO", "cau_hoi": ["DEMO hỏi"],
         "bang": [{"ma": r["ma"], "gia_tri": None} for r in dm.cac_dong], "phan_hoi": []}
    w = deepcopy(v)
    if doi == "thu_tu":
        w["bo_10_cot"][1:3] = reversed(w["bo_10_cot"][1:3])
    elif doi == "cot":
        w["bo_10_cot"][1][8] += " "
    elif doi == "cau_hoi":
        w["cau_hoi"][0] += " "
    else:
        w["bang"][36]["gia_tri"] = "DEMO"
    assert len(w["bang"]) == 37
    assert not all(x["trung_byte"] for x in e6.so_cac_phan(e6.cac_byte(v), e6.cac_byte(w)).values())


@pytest.mark.parametrize("raw", [demo_thuong(), mau_track()], ids=["thuong", "track_changes"])
def test_hai_duong_khac_cau_hoi_bang_nhung_gia_tri_null_khop(dm, raw):
    track = raw == mau_track()
    cu = chay_mac_dinh_chuyen_tiep(e6.ENGINE / "tham-chieu/DANH_MUC_THAM_SO.xlsx", raw, bang_ai_cu(not track))
    moi, meta = e6.chay_module(raw, ts_bo(dm), null_ai(dm))
    diff = e6.so_cac_phan(e6.byte_cu(cu), moi)
    assert len(cu["cau_hoi"]) == (8 if track else 9) and len(cu["bang"]) == meta["so_dong"] == 37
    assert cu["track_changes"] == (2 if track else 0)
    assert all(diff[k]["trung_byte"] for k in ("bo_10_cot", "tham_so", "van_ban"))
    assert all(not diff[k]["trung_byte"] for k in ("cau_hoi", "bang", "phan_hoi"))
    assert all(r["dat"] for r in e6.so_tung_ma(cu["bang"], json.loads(moi["bang"]),
               moi["van_ban"].decode(), [r["ma"] for r in dm.cac_dong]))


def test_ai_gia_co_dinh_tai_lap_khong_mang_khong_ghi_dia(dm, monkeypatch):
    # Chặn network và mọi open ghi, gồm cả các hàm nguồn được bọc.
    import builtins
    mo_cu, mo_path, mo_io = builtins.open, Path.open, io.open
    def cam_mang(*a, **kw):
        pytest.fail("Không được gọi mạng trong E6.")
    def boc_mo(ham):
        def mo(*a, **kw):
            mode = kw.get("mode", a[1] if len(a) > 1 else "r")
            assert not set(mode) & set("wax+"), "Không được ghi tệp trong đối chiếu E6."
            return ham(*a, **kw)
        return mo
    monkeypatch.setattr(socket.socket, "connect", cam_mang)
    monkeypatch.setattr(builtins, "open", boc_mo(mo_cu))
    monkeypatch.setattr(Path, "open", boc_mo(mo_path))
    monkeypatch.setattr(io, "open", boc_mo(mo_io))
    a = e6.chay_module(mau_track(), ts_bo(dm), null_ai(dm))[0]
    b = e6.chay_module(mau_track(), ts_bo(dm), null_ai(dm))[0]
    assert a == b
    c = chay_mac_dinh_chuyen_tiep(e6.ENGINE / "tham-chieu/DANH_MUC_THAM_SO.xlsx", mau_track(), bang_ai_cu())
    d = chay_mac_dinh_chuyen_tiep(e6.ENGINE / "tham-chieu/DANH_MUC_THAM_SO.xlsx", mau_track(), bang_ai_cu())
    assert e6.byte_cu(c) == e6.byte_cu(d)


def test_hai_module_cung_app_ngan_bo_rieng_khong_ghi_de(dm):
    app = app_tx3()
    a = ts_bo(dm, "DEMO-crm")
    b = ts_bo(dm, "DEMO-m3")
    bo_b = json.loads(b["bo_tham_so_json"])
    bo_b["cac_dong"][0]["mo_ta"] += " DEMO riêng"
    bo_b.pop("ma_bam_noi_dung")
    b = ts_demo(bo_b, prompt="Trích DEMO riêng.", ngan_sach_token_vao=100000)
    truoc = e6.chay_module(mau_track(), a, null_ai(dm), app=app)
    khac = e6.chay_module(mau_track(), b, null_ai(dm), app=app)
    sau = e6.chay_module(mau_track(), a, null_ai(dm), app=app)
    assert truoc == sau and truoc[1]["module"] != khac[1]["module"]
    assert truoc[0]["bo_10_cot"] != khac[0]["bo_10_cot"]


def test_runtime_hash_sai_tra_nguyen_loi_khong_fallback(dm):
    ts = ts_bo(dm)
    ts["bo_tham_so_json"] += " "
    with pytest.raises(LoiNghiepVu) as exc:
        doc_bo(ts)
    assert exc.value.ma == "SAI_BAM_BO_THAM_SO"
    assert exc.value.thong_diep == "Bộ tham số không khớp mã kiểm tra."
    core, app = CoreGia(), app_tx3()
    vao = deepcopy(__import__("mau_tx3").VD["dau_vao"])
    kq = core.chay_thu(app, "trich.chuan_bi@1", vao, ts)
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "SAI_BAM_BO_THAM_SO"
    assert core.so_lan_ghi["tep"] == 0


def test_cong_mac_dinh_bo_chuan_da_duoc_lead_duyet(capsys):
    # Lead duyệt bộ chuẩn DEMO 15/11/2026 (chap_nhan_lead="đã duyệt" + bien_ban_lead).
    assert e6.main([]) == 0
    r = json.loads(capsys.readouterr().out)
    assert r["chap_nhan_lead"] == "đã duyệt" and r["ket_qua_do"] == "dat"
    assert r["trang_thai"] != "chua_kiem"
    assert len(r["cac_ca"]) == 2 and r["cloud"] == 0


@pytest.mark.parametrize("loai", ["thieu_xlsx", "sai_xlsx", "sai_ghim"])
def test_loi_nguon_thieu_sai_bam_khong_sua_ghim(tmp_path, loai):
    ref = tmp_path / "tham-chieu"
    ref.mkdir()
    nguon = (e6.ENGINE / "tham-chieu/NGUON.md").read_bytes()
    raw = (e6.ENGINE / "tham-chieu/DANH_MUC_THAM_SO.xlsx").read_bytes()
    (ref / "NGUON.md").write_bytes(nguon.replace(e6.BAM_XLSX_CU.encode(), b"0" * 64) if loai == "sai_ghim" else nguon)
    if loai != "thieu_xlsx":
        (ref / "DANH_MUC_THAM_SO.xlsx").write_bytes(raw + b" " if loai == "sai_xlsx" else raw)
    truoc = (ref / "NGUON.md").read_bytes()
    with pytest.raises(e6.LoiKiemE6) as exc:
        e6.kiem_nguon(tmp_path)
    assert str(exc.value) == (e6.THIEU if loai == "thieu_xlsx" else e6.SAI_BAM)
    assert exc.value.ma_thoat == (2 if loai == "thieu_xlsx" else 3)
    assert (ref / "NGUON.md").read_bytes() == truoc


def test_bang_ai_thieu_hoac_du_khong_tu_sinh_tra_loi():
    for tape in ({"tim_vi_tri": [], "hoi_trich": []},
                 {"tim_vi_tri": [{}], "hoi_trich": [[], [], [], [], [], [], [], []]}):
        with pytest.raises(ThieuBangAI):
            chay_mac_dinh_chuyen_tiep(e6.ENGINE / "tham-chieu/DANH_MUC_THAM_SO.xlsx", mau_track(), tape)


def test_fixture_thieu_hash_sai_va_khong_doc_ngoai_goc(tmp_path):
    for spec, cau in [({"tep": "thieu.json", "bam": "sha256:" + "0" * 64}, e6.THIEU),
                      ({"tep": "../DEMO.json", "bam": "sha256:" + "0" * 64}, e6.THIEU)]:
        with pytest.raises(e6.LoiKiemE6, match=cau):
            e6._doc_ghim(tmp_path, spec)
    (tmp_path / "DEMO.json").write_bytes(b"DEMO")
    with pytest.raises(e6.LoiKiemE6, match=e6.SAI_BAM):
        e6._doc_ghim(tmp_path, {"tep": "DEMO.json", "bam": "sha256:" + "0" * 64})


def test_thieu_bat_ky_phan_ban_vang_deu_chan():
    with pytest.raises(e6.LoiKiemE6, match=e6.THIEU):
        e6.so_cac_phan({}, {k: b"DEMO" for k in e6.CAC_PHAN})


def test_so_bytes_khong_dua_vao_hash_de_nhan_dat(monkeypatch):
    monkeypatch.setattr(e6, "bam_bytes", lambda raw: "DEMO-cung-bam-gia")
    assert not e6.so_byte(b"DEMO", b"DEM0")["trung_byte"]


def test_chan_doan_khong_duoc_thanh_chung_nhan_e6(capsys):
    assert e6.main(["--chan-doan"]) == 2
    r = json.loads(capsys.readouterr().out)
    assert r["trang_thai"] == "chua_kiem" and len(r["cac_ca"]) == 2
    assert all(c["ket_qua_chan_doan"] == "dat" for c in r["cac_ca"])


def tao_manifest_test(tmp_path, dm):
    """Nguồn giả chỉ để test cổng thất bại; không cấp bản vàng nghiệm thu."""
    ref = tmp_path / "tham-chieu"
    ref.mkdir()
    for ten in ("NGUON.md", "DANH_MUC_THAM_SO.xlsx"):
        (ref / ten).write_bytes((e6.ENGINE / "tham-chieu" / ten).read_bytes())
    cases = []
    for i, (loai, raw, tape) in enumerate((("thuong", demo_thuong(), bang_ai_cu(True)),
                                         ("track_changes", mau_track(), bang_ai_cu()))):
        gold = {"nhan": "DEMO", "gia_tri": {r["ma"]: None for r in dm.cac_dong}}
        values = {"docx": raw, "ai": json_bytes({"cu": tape, "moi": null_ai(dm)}),
                  "tham_so": json_bytes(ts_bo(dm, f"DEMO-module-{i}")), "vang": json_bytes(gold)}
        case = {"ma": f"DEMO-test-cong-{i}", "loai": loai}
        for k, data in values.items():
            name = f"DEMO-{i}-{k}.bin"
            (ref / name).write_bytes(data)
            case[k] = {"tep": name, "bam": bam_bytes(data)}
        cases.append(case)
    m = {"phien_ban": 2, "nhan": "DEMO", "chap_nhan_lead": "đã duyệt",
         "bien_ban_lead": "DEMO-UNIT-TEST-KHONG-NGHIEM-THU",
         "cac_ca": cases}
    path = ref / "DEMO-manifest.json"
    path.write_bytes(json_bytes(m))
    return path, m


def test_cong_day_du_khac_byte_tham_khao_van_dat_nhung_vang_sai_phai_chan(tmp_path, dm):
    path, m = tao_manifest_test(tmp_path, dm)
    report, code = e6.kiem_manifest(path, goc=tmp_path)
    assert code == 0 and report["trang_thai"] == "dat"
    assert len(report["cac_ca"]) == 2
    for c in report["cac_ca"]:
        assert all(v["trung_byte"] for v in c["byte_bat_buoc"].values())
        assert not c["tham_khao_khong_cham"]["cau_hoi"]["trung_byte"]
    # Bản vàng sai một byte dù băm tệp được cập nhật vẫn không đạt.
    c = m["cac_ca"][0]
    gp = path.parent / c["vang"]["tep"]
    gold = json.loads(gp.read_bytes())
    gold["gia_tri"]["TC-01"] = "DEMO giá trị sai"
    raw = json_bytes(gold)
    gp.write_bytes(raw)
    c["vang"]["bam"] = bam_bytes(raw)
    path.write_bytes(json_bytes(m))
    report, code = e6.kiem_manifest(path, goc=tmp_path)
    assert code == 1 and not report["cac_ca"][0]["tung_ma"][0]["cu_khop_vang"]


@pytest.mark.parametrize("doi,code", [("chua_duyet", 2), ("thieu_ca_track", 2), ("sai_hash_ai", 3),
                                     ("thieu_vang", 2), ("ai_thieu_luot", 2),
                                     ("sai_bo_quy_tac", 1), ("sai_bam_xlsx_khai", 1)])
def test_manifest_thieu_duyet_fixture_va_hash_khong_dat(tmp_path, dm, doi, code):
    path, m = tao_manifest_test(tmp_path, dm)
    if doi == "chua_duyet":
        m["chap_nhan_lead"] = ""
    elif doi == "thieu_ca_track":
        m["cac_ca"] = m["cac_ca"][:1]
    elif doi == "sai_hash_ai":
        m["cac_ca"][0]["ai"]["bam"] = "sha256:" + "0" * 64
    elif doi == "thieu_vang":
        m["cac_ca"][0]["vang"]["tep"] = "DEMO-khong-co.bin"
    elif doi == "ai_thieu_luot":
        spec = m["cac_ca"][0]["ai"]
        raw = json_bytes({"cu": {"tim_vi_tri": [], "hoi_trich": []}, "moi": null_ai(dm)})
        (path.parent / spec["tep"]).write_bytes(raw)
        spec["bam"] = bam_bytes(raw)
    else:
        spec = m["cac_ca"][0]["tham_so"]
        ts = json.loads((path.parent / spec["tep"]).read_bytes())
        bo = json.loads(ts["bo_tham_so_json"])
        if doi == "sai_bo_quy_tac":
            bo["quy_tac"] = [{"kieu": "Có thì phải có", "ma_tham_so": ["TC-01"],
                              "dieu_kien": "", "doi_chieu": "TC-02"}]
        else:
            bo["bam_tep_goc"] = "sha256:" + "0" * 64
        ts["bo_tham_so_json"] = json_bytes(bo).decode("utf-8")
        ts["bam_bo_tham_so"] = bam_bytes(ts["bo_tham_so_json"].encode("utf-8"))
        raw = json_bytes(ts)
        (path.parent / spec["tep"]).write_bytes(raw)
        spec["bam"] = bam_bytes(raw)
    path.write_bytes(json_bytes(m))
    r, k = e6.kiem_manifest(path, goc=tmp_path)
    assert k == code and r["trang_thai"] == ("chua_dat" if code == 1 else "chua_kiem")
    assert r["loi"] == ("Bộ module khác nguồn đối chiếu E6." if code == 1
                         else e6.SAI_BAM if code == 3 else e6.THIEU)


def doi_gia_tri(cu, moi, *, text=None, qs=None):
    text = text if text is not None else (moi or "DEMO")
    if qs is None:
        qs = [{"cau": text, "bat_dau": 0, "ket_thuc": len(text)}]
    return e6.so_tung_ma([{"ma": "DEMO", "gia_tri": cu}],
        [{"ma": "DEMO", "gia_tri": moi, "dan_chung": qs,
          "ly_do": ["Lý do hậu kiểm DEMO."]}], text, ["DEMO"])[0]


@pytest.mark.parametrize("cu,moi,nhan", [
    (" DEMO \n", "DEMO", "khớp"), (None, None, "khớp"),
    ("DEMO", None, "cũ có-mới null"), (None, "DEMO", "cũ null-mới có"),
    ("A", "B", "khác"), ("", None, "khớp"),
    ("Không tìm thấy trong HĐ", None, "khớp"),
    ("Không quy định", None, "cũ có-mới null"),
    ("Không áp dụng", None, "cũ có-mới null"),
    ("1.000.000 VND", "1000000 VND", "khác"),
    ("2026-10-30", "30/10/2026", "khác"), ("10,0", "10.0", "khác"),
    ("DEMO  A", "DEMO A", "khác"), ("ắ", "ắ", "khác")])
def test_bon_loai_ket_qua_va_khong_chuan_hoa_so_tien_ngay(cu, moi, nhan):
    r = doi_gia_tri(cu, moi)
    assert r["ket_qua"] == nhan and bool(r["ly_do"])
    assert r["dat"] == (nhan == "khớp")


@pytest.mark.parametrize("qs", [[],
    [{"cau": "DEMO", "bat_dau": 1, "ket_thuc": 5}],
    [{"cau": "DEMO", "bat_dau": True, "ket_thuc": 4}],
    [{"cau": "DEMO", "bat_dau": 0, "ket_thuc": 99}],
    [{"cau": "SAI", "bat_dau": 0, "ket_thuc": 3}],
    [{"cau": "DEMO", "bat_dau": 0, "ket_thuc": 4},
     {"cau": "SAI", "bat_dau": 0, "ket_thuc": 3}]])
def test_gia_tri_khop_nhung_dan_chung_sai_van_chan(qs):
    r = doi_gia_tri("DEMO", "DEMO", qs=qs)
    assert r["ket_qua"] == "khớp" and not r["dat"] and not r["dan_chung_hop_le"]


def test_cau_dung_offset_nhung_khong_ho_tro_gia_tri_van_chan():
    assert not doi_gia_tri("1.000 VND", "1.000 VND", text="Giá là 11.000 VND.")["dat"]


@pytest.mark.parametrize("doi", ["mat_ma", "trung_ma", "dao_ma", "vang_thieu"])
def test_thieu_trung_dao_ma_hoac_thieu_vang_khong_duoc_dat(doi):
    a = [{"ma": "A", "gia_tri": None}, {"ma": "B", "gia_tri": None}]
    b = [{"ma": r["ma"], "gia_tri": None, "dan_chung": []} for r in a]
    gold = {"A": None, "B": None}
    if doi == "mat_ma":
        b.pop()
    elif doi == "trung_ma":
        b[1]["ma"] = "A"
    elif doi == "dao_ma":
        b.reverse()
    else:
        gold.pop("B")
    with pytest.raises(e6.LoiKiemE6):
        e6.so_tung_ma(a, b, "DEMO", ["A", "B"], gold)


def test_bo_chuan_khop_vang_va_bang_ai_cung_cau_tra_loi_khong_tu_chung_nhan():
    ref = e6.ENGINE / "tham-chieu/e6"
    truoc = {p.name: p.read_bytes() for p in ref.iterdir() if p.is_file()}
    report, code = e6.kiem_manifest(e6.ENGINE / "tham-chieu/e6/chap-nhan.json")
    assert truoc == {p.name: p.read_bytes() for p in ref.iterdir() if p.is_file()}
    assert code == 0 and report["ket_qua_do"] == "dat"
    assert [c["track_changes_da_nhan"] for c in report["cac_ca"]] == [0, 2]
    for c in report["cac_ca"]:
        assert len(c["tung_ma"]) == 37
        assert all(r["cu_khop_vang"] and r["moi_khop_vang"] and r["dan_chung_hop_le"]
                   for r in c["tung_ma"])


def test_bo_chuan_tai_lap_tu_bang_tac_gia_va_khong_ghi_de_vang(tmp_path):
    from tao_demo_e6 import soan_ca, tao_docx, ghi_nguon
    for track, ten in ((False, "DEMO-thuong"), (True, "DEMO-track-changes")):
        vals, quotes = soan_ca(track)
        ref = e6.ENGINE / "tham-chieu/e6"
        assert tao_docx(vals, quotes, track) == (ref / (ten + ".docx")).read_bytes()
        gold = json.loads((ref / (ten + ".vang.json")).read_bytes())
        assert gold["gia_tri"] == vals and gold["can_cu"] == quotes
        assert all(vals[ma] in quote for ma, quote in quotes.items())
    p = tmp_path / "DEMO-vang.json"
    p.write_bytes(b"DEMO vang doc lap")
    with pytest.raises(ValueError, match="không ghi đè"):
        ghi_nguon(p, b"DEMO dau ra engine")
    assert p.read_bytes() == b"DEMO vang doc lap"


@pytest.mark.parametrize("phan", e6.BAT_BUOC_BYTE)
def test_cong_that_chan_sai_byte_bat_buoc_du_gia_tri_khop(tmp_path, dm, monkeypatch, phan):
    path, _ = tao_manifest_test(tmp_path, dm)
    ham = e6.chay_module
    def boc(*a, **kw):
        artifacts, meta = ham(*a, **kw)
        artifacts[phan] += b" "
        return artifacts, meta
    monkeypatch.setattr(e6, "chay_module", boc)
    report, code = e6.kiem_manifest(path, goc=tmp_path)
    assert code == 1 and all(not c["byte_bat_buoc"][phan]["trung_byte"] for c in report["cac_ca"])


def test_cho_lead_nhung_gia_tri_sai_van_bao_chua_dat(tmp_path, dm):
    path, m = tao_manifest_test(tmp_path, dm)
    m["chap_nhan_lead"] = "chờ lead"
    spec = m["cac_ca"][0]["vang"]
    raw = json_bytes({"nhan": "DEMO", "gia_tri": {r["ma"]: "DEMO" for r in dm.cac_dong}})
    (path.parent / spec["tep"]).write_bytes(raw)
    spec["bam"] = bam_bytes(raw)
    path.write_bytes(json_bytes(m))
    r, code = e6.kiem_manifest(path, goc=tmp_path)
    assert code == 1 and r["ket_qua_do"] == r["trang_thai"] == "chua_dat"
