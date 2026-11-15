"""DC-8: giao thức CoreGia + detector giả tách riêng thuật toán pixel thật."""
from copy import deepcopy
import importlib
import io
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest
from PIL import Image
from kho_tri_thuc_sdk.engine import LoiNghiepVu, ViecDaHuy, ChuaRo

from test_dc3 import Mau, CoreTepConDEMO, chay, hs, PN, MODULE, kiem_loi
from test_dc4 import so
from demo_sua_tay import mau_anh, metadata_anh

st = importlib.import_module("e_doi_chieu.sua_tay")
anh = importlib.import_module("e_doi_chieu.anh")


class CoreAnhDEMO(CoreTepConDEMO):
    """C-DC-05 giả: Core gắn transform/căn cứ, không lấy từ JSON caller."""
    def __init__(self):
        super().__init__()
        self.anh_viec = {}

    def _nhan_viec(self, ma, instance=None):
        v = super()._nhan_viec(ma, instance)
        if v and v["id"] in self.anh_viec:
            v["ngu_canh"]["doi_chieu_anh"] = deepcopy(self.anh_viec[v["id"]])
        return v


def tao_mau(ten="gach", *, ti_le=1, xoay=0, so_trang=1):
    m = Mau(CoreAnhDEMO())
    a = mau_anh(ten, ti_le=ti_le, xoay=xoay)
    ref = m.luu("anh-dc8.png", a["raw"], "image/png")
    m.cap["anh_trang"] = [{"so": i+1, **deepcopy(ref)} for i in range(so_trang)]
    vb = m.vb()
    v = vb["van_ban_tai_lieu"]
    pages = [deepcopy(a["page"]) for _ in range(so_trang)]
    for i, page in enumerate(pages):
        page["so"] = i+1
    text = a["page"]["khoi"][0]["van_ban"]
    v.update(van_ban="\f".join([text]*so_trang), trang=pages, so_trang=so_trang)
    m.dat_vb(vb)
    m.cau_hinh.update(phuong_phap_detector=st.PHUONG_PHAP, phien_ban_detector=st.PHIEN_BAN)
    m.dat_cau_hinh()
    m.anh_mau = a
    m.meta = [metadata_anh(a, ref["bam"]) for _ in range(so_trang)]
    for i, meta in enumerate(m.meta):
        meta["so"] = i+1
    return m


def giao_quet(m, pb, *, metadata=True, pn=PN, quyen=True):
    vid = m.core.giao_viec("doi_chieu.phat_hien_sua_tay@1", pb, {"che_do": "day_du"}, phap_nhan_id=pn)
    m.core.module_viec[vid] = MODULE
    m.core.cap[vid] = set(m.refs) if quyen else set()
    if metadata:
        m.core.anh_viec[vid] = {"phien_ban": 1, "ma_cap": m.cap["ma_cap"],
            "bam_ho_so": pb["ho_so_doi_chieu"]["bam_ho_so"], "bam_ban_ky": m.cap["nguon"]["ban_ky"]["bam"],
            "trang": deepcopy(m.meta)}
    return vid


def quet(m, monkeypatch, pb=None, **kw):

    if pb is None:
        nhan = m.chay()
        assert nhan["trang_thai"] == "XONG", nhan
        pb = nhan["ket_qua"]
    vid = giao_quet(m, pb, **kw)
    m.core.chay(chay.app)
    return m.core.xem(vid)


def doi_snapshot(m, pb, ham):
    s = m.snapshot({"ket_qua": pb})
    ham(s)
    raw = hs.json_bytes(s)
    tep = m.luu("snapshot-da-doi.json", raw, "application/json")["tep"]
    return hs._phong_bi(s, tep, raw)


class DetectorGia:
    """Chỉ kiểm giao thức. Kết quả này không dùng tính precision/recall."""
    da_do_demo = True
    phuong_phap, phien_ban = st.PHUONG_PHAP, st.PHIEN_BAN

    def quet(self, im, tu, kiem):
        kiem()
        return {"da_quet_toan_trang": True, "pham_vi_px": [0, 0, im.width, im.height],
                "so_pixel_da_quet": im.width*im.height,
                "vung": [{"loai": "gach_de", "hop_px": [30, 90, 311, 94]}]}


def test_giao_thuc_detector_gia_khong_la_so_do(monkeypatch):
    m = tao_mau()
    monkeypatch.setattr(st, "chon_detector", lambda _: DetectorGia())
    r = quet(m, monkeypatch)
    s = m.snapshot(r)
    assert s["quet_anh"]["so_do_chat_luong_ho_so"] is None
    assert s["giai_doan"] == "da_quet_anh" and len(s["vung_sua_tay"]) == 1
    assert s["kiem_tra"]["sua_tay"] == "chua_kiem" and s["de_nghi_chan"]
    v = s["vung_sua_tay"][0]
    assert v["muc_san"] == v["muc"] == "nghiem_trong" and v["bat_buoc_xac_nhan"]
    raw = m.core.doc_tep(v["anh_cat"]["tep_id"])
    assert hs.bam(raw) == v["bam_anh_cat"] and len(raw) == v["anh_cat"]["kich_thuoc"]
    assert s["quet_anh"]["trang"][0]["so_pixel_da_quet"] == 480*240
    assert not s["da_kiem_du"] and s["ket_luan"] is None


@pytest.mark.parametrize("ten", ["gach", "chen", "sat_chu"])
def test_thuat_toan_that_co_vet(monkeypatch, ten):
    m = tao_mau(ten)
    r = quet(m, monkeypatch)
    assert r["trang_thai"] == "XONG", r
    s = m.snapshot(r)
    assert s["vung_sua_tay"]
    assert all(v["chu_tay"] is None for v in s["vung_sua_tay"])
    if ten == "gach":
        assert s["vung_sua_tay"][0]["chu_in_bi_de"]
    else:
        assert all(v["chu_in_bi_de"] is None for v in s["vung_sua_tay"])


@pytest.mark.parametrize("ten", ["khong_vet", "muc_mau_in", "net_xa_chu"])
def test_khong_mac_dinh_muc_mau_ngoai_ocr_la_sua(monkeypatch, ten):
    m = tao_mau(ten)
    r = quet(m, monkeypatch)
    assert r["trang_thai"] == "XONG", r
    s = m.snapshot(r)
    assert s["vung_sua_tay"] == [] and s["tom_tat"]["so_vung_sua_tay"] == 0
    assert s["quet_anh"]["trang"][0]["da_quet_toan_trang"]
    assert not s["quet_anh"]["du_dieu_kien_ket_luan_sach"]
    assert s["kiem_tra"]["sua_tay"] == "chua_kiem" and s["de_nghi_chan"]


@pytest.mark.parametrize("ten", ["chu_ky", "dau", "ky_nhay"])
def test_loai_vung_da_xac_nhan_khong_che_noi_dung(monkeypatch, ten):
    m = tao_mau(ten)
    r = quet(m, monkeypatch)
    assert r["trang_thai"] == "XONG", r
    s = m.snapshot(r)
    assert s["vung_sua_tay"] == []
    assert s["quet_anh"]["trang"][0]["vung_loai_tru"][0]["duoc_loai"]


def test_chu_ky_chong_chu_khong_loai_ca_khoi(monkeypatch):
    m = tao_mau("ky_chong_chu")
    r = quet(m, monkeypatch)
    assert r["trang_thai"] == "XONG", r
    s = m.snapshot(r)
    assert not s["quet_anh"]["trang"][0]["vung_loai_tru"][0]["duoc_loai"]
    # Mock tạo một nét gạch thực nằm trong khối chồng; phải giữ nguyên.
    class ChiuChong(DetectorGia):
        def quet(self, im, tu, kiem):
            k = super().quet(im, tu, kiem)
            k["vung"][0]["hop_px"] = [66, 90, 100, 94]
            return k
    monkeypatch.setattr(st, "chon_detector", lambda _: ChiuChong())
    s = m.snapshot(quet(m, monkeypatch))
    assert len(s["vung_sua_tay"]) == 1 and s["vung_sua_tay"][0]["vung_loai_tru_chua_du_can_cu"]


@pytest.mark.parametrize("sai", [None, {}, {"nguon": "caller", "ma": "DEMO"}])
def test_thieu_can_cu_chu_ky_can_xem(monkeypatch, sai):
    m = tao_mau("chu_ky")
    m.meta[0]["vung_loai_tru"][0]["can_cu"] = sai
    s = m.snapshot(quet(m, monkeypatch))
    assert s["vung_sua_tay"] and s["vung_sua_tay"][0]["can_xem"]


@pytest.mark.parametrize("ti_le", [1, 2, 3])
@pytest.mark.parametrize("xoay", [0, 90, 180, 270])
def test_xoay_ty_le_hop_va_crop_thuc(monkeypatch, ti_le, xoay):
    m = tao_mau(ti_le=ti_le, xoay=xoay)
    r = quet(m, monkeypatch)
    assert r["trang_thai"] == "XONG", r
    s = m.snapshot(r)
    assert s["vung_sua_tay"]
    v = s["vung_sua_tay"][0]
    assert abs(v["hop"][0]-30) <= 1 and abs(v["hop"][2]-311) <= 1
    raw = m.core.doc_tep(v["anh_cat"]["tep_id"])
    with Image.open(io.BytesIO(raw)) as cut, Image.open(io.BytesIO(m.anh_mau["raw"])) as original:
        expected = original.crop(tuple(v["hop_cat_anh_px"]))
        assert cut.size == expected.size and cut.tobytes() == expected.tobytes()
        expected.close()


@pytest.mark.parametrize("key,val", [("ti_le", 0), ("ti_le", 3), ("xoay", 45), ("xoay", True),
    ("he_toa_do", "goc_duoi_trai"), ("rong_nguon", 479), ("rong_px", 479), ("don_vi", "mm"),
    ("bam_anh", "sha256:"+"0"*64)])
def test_metadata_sai_tu_choi(monkeypatch, key, val):
    m = tao_mau()
    m.meta[0][key] = val
    kiem_loi(quet(m, monkeypatch), "DC_THIEU_ANH")


def test_thieu_metadata_core_khong_tin_vung_caller(monkeypatch):
    m = tao_mau()
    kiem_loi(quet(m, monkeypatch, metadata=False), "DC_THIEU_ANH")


def test_thieu_mot_trang_khong_quet_do_roi_bao_xong(monkeypatch):
    m = tao_mau(so_trang=2)

    pb = m.chay()["ket_qua"]
    pb = doi_snapshot(m, pb, lambda s: s["anh_trang"].pop())
    before = m.core.so_tai
    kiem_loi(quet(m, monkeypatch, pb), "DC_THIEU_ANH")
    assert before == m.core.so_tai


def test_quet_du_hai_trang(monkeypatch):
    m = tao_mau(so_trang=2)
    s = m.snapshot(quet(m, monkeypatch))
    assert [p["so_trang"] for p in s["quet_anh"]["trang"]] == [1, 2]
    assert {v["so_trang"] for v in s["vung_sua_tay"]} == {1, 2}


@pytest.mark.parametrize("sai", ["bo", "phien_ban", "chu_do", "chi_vung", "quet_mot_phan", "pixel"])
def test_detector_chua_co_khong_cho_danh_sach_rong_gia(monkeypatch, sai):
    m = tao_mau()
    if sai == "bo":
        m.cau_hinh["phuong_phap_detector"] = "chua_co"
        m.dat_cau_hinh()
    elif sai == "phien_ban":
        m.cau_hinh["phien_ban_detector"] = "chua_do"
        m.dat_cau_hinh()
    else:
        class KhongDu(DetectorGia):
            da_do_demo = sai != "chu_do"
            def quet(self, im, tu, kiem):
                k = super().quet(im, tu, kiem)
                if sai == "chi_vung":
                    return []
                if sai == "quet_mot_phan":
                    k["pham_vi_px"] = [0, 0, 20, 20]
                if sai == "pixel":
                    k["so_pixel_da_quet"] = 1
                return k
        monkeypatch.setattr(st, "chon_detector", lambda _: KhongDu())
    kiem_loi(quet(m, monkeypatch), "DC_CHUA_CO_BO_PHAT_HIEN")


def test_detector_loi_khong_lo_noi_dung(monkeypatch, capsys):
    m = tao_mau()
    class Loi(DetectorGia):
        def quet(self, *a):
            raise RuntimeError("DEMO-bi-mat-khong-duoc-log")
    monkeypatch.setattr(st, "chon_detector", lambda _: Loi())
    r = quet(m, monkeypatch)
    assert r["trang_thai"] == "LOI" and r["ket_qua"] is None
    assert "DEMO-bi-mat" not in capsys.readouterr().err+json.dumps(r)


@pytest.mark.parametrize("luc", ["quet", "cat", "tai"])
def test_huy_khong_tra_snapshot_thanh_cong(monkeypatch, luc):
    m = tao_mau()
    def huy(*args, **kw):
        raise ViecDaHuy()
    if luc == "quet":
        monkeypatch.setattr(st.BoPhatHienNet, "quet", huy)
    elif luc == "cat":
        monkeypatch.setattr(st, "cat_png", huy)
    else:
        monkeypatch.setattr(m.core, "_tai_tep_ra", m.core._tai_tep_ra)
    if luc == "tai":

        pb = m.chay()["ket_qua"]
        original = m.core._tai_tep_ra
        def tai(ma, vid, ten, raw, mime, khoa):
            if mime == "image/png":
                m.core.huy(vid)
                raise ViecDaHuy()
            return original(ma, vid, ten, raw, mime, khoa)
        monkeypatch.setattr(m.core, "_tai_tep_ra", tai)
        r = quet(m, monkeypatch, pb)
    else:
        r = quet(m, monkeypatch)
    assert r["trang_thai"] == "HUY" and r["ket_qua"] is None


def test_so_truoc_quet_khong_mat_diem_lech(monkeypatch):
    m = tao_mau()

    r = so(m)
    assert r["trang_thai"] == "XONG", r
    before = m.snapshot(r)
    after = m.snapshot(quet(m, monkeypatch, r["ket_qua"]))
    for k in ("diem_lech", "edit_script", "kiem_trang", "nguon", "chuan_hoa", "bo_quy_tac"):
        assert after[k] == before[k]
    assert before["diem_lech"]


@pytest.mark.parametrize("raw", [b"DEMO", b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff\xd9"])
def test_anh_hong_giai_ma_thuc(raw):
    with pytest.raises(LoiNghiepVu) as e:
        anh.doc_anh(raw, "image/png", 20000000, lambda: None)
    assert e.value.ma == "DC_THIEU_ANH"


def test_anh_qua_lon_chan_truoc_load(monkeypatch):
    raw = mau_anh("khong_vet")["raw"]
    with pytest.raises(LoiNghiepVu) as e:
        anh.doc_anh(raw, "image/png", 100, lambda: None)
    assert e.value.ma == "DC_QUA_GIOI_HAN"


def test_lock_pillow_nguyen_version_hash():
    root = Path(__file__).resolve().parents[2]
    def dong(path):
        text = path.read_text(encoding="utf-8")
        return text[text.index("Pillow=="):].splitlines()[:3]
    assert dong(root/"e_doi_chieu/goi/e_doi_chieu/requirements.lock") == dong(root/"e_ocr/goi/e_ocr/requirements.lock")


@pytest.mark.parametrize("sai", ["bam", "kich_thuoc", "quyen"])
def test_anh_sai_bam_size_mat_quyen(monkeypatch, sai):
    m = tao_mau()

    pb = m.chay()["ket_qua"]
    if sai == "quyen":
        m.core.cam.add(m.cap["anh_trang"][0]["tep"]["tep_id"])
    else:
        def sua(s):
            if sai == "bam":
                s["anh_trang"][0]["bam"] = "sha256:"+"0"*64
            else:
                s["anh_trang"][0]["tep"]["kich_thuoc"] += 1
        pb = doi_snapshot(m, pb, sua)
        if sai == "bam":
            m.meta[0]["bam_anh"] = "sha256:"+"0"*64
    before = m.core.so_tai
    kiem_loi(quet(m, monkeypatch, pb), "DC_THIEU_ANH" if sai == "quyen" else "DC_SAI_NGUON")
    assert m.core.so_tai == before


def test_anh_hong_qua_core_gia(monkeypatch):
    m = tao_mau()

    pb = m.chay()["ket_qua"]
    ref = m.luu("hong.png", b"DEMO-anh-hong", "image/png")
    pb = doi_snapshot(m, pb, lambda s: s["anh_trang"][0].update(ref))
    m.meta[0]["bam_anh"] = ref["bam"]
    kiem_loi(quet(m, monkeypatch, pb), "DC_THIEU_ANH")


def test_anh_qua_lon_qua_core_gia(monkeypatch):
    m = tao_mau()
    m.meta[0].update(rong_px=20001, cao_px=1000)
    before = m.core.so_tai
    kiem_loi(quet(m, monkeypatch), "DC_QUA_GIOI_HAN")
    assert m.core.so_tai == before+1  # Chỉ snapshot nhận cặp, chưa có ảnh cắt.


def test_thieu_toa_do_tu_khong_gia_sach(monkeypatch):
    m = tao_mau()
    vb = m.vb()
    for dong in vb["van_ban_tai_lieu"]["trang"][0]["khoi"][0]["dong"]:
        dong.pop("tu")
    m.dat_vb(vb)
    kiem_loi(quet(m, monkeypatch), "DC_CHUA_CO_BO_PHAT_HIEN")


def test_mot_trang_loi_khong_tai_crop_trang_truoc(monkeypatch):
    m = tao_mau(so_trang=2)

    pb = m.chay()["ket_qua"]
    class LoiTrangHai(DetectorGia):
        lan = 0
        def quet(self, *args):
            self.lan += 1
            if self.lan == 2:
                raise RuntimeError("DEMO")
            return super().quet(*args)
    monkeypatch.setattr(st, "chon_detector", lambda _: LoiTrangHai())
    before = m.core.so_tai
    kiem_loi(quet(m, monkeypatch, pb), "DC_LOI_XU_LY")
    assert before == m.core.so_tai


def test_ma_vung_khong_trung_giua_cac_trang(monkeypatch):
    m = tao_mau(so_trang=2)
    s = m.snapshot(quet(m, monkeypatch))
    ids = [v["ma"] for v in s["vung_sua_tay"]]
    assert len(set(ids)) == len(ids) == 2


def test_vung_chong_chu_chua_phat_hien_van_can_xem(monkeypatch):
    m = tao_mau("ky_chong_chu")
    s = m.snapshot(quet(m, monkeypatch))
    assert s["vung_sua_tay"] and s["vung_sua_tay"][0]["nguon_ung_vien"] == "metadata_can_xem"
    assert s["quet_anh"]["trang"][0]["so_ung_vien_pixel"] == 0
    assert s["quet_anh"]["trang"][0]["so_vung_can_xem_tu_metadata"] == 1


def test_can_cu_loai_tru_khong_chep_truong_la(monkeypatch):
    m = tao_mau("chu_ky")
    m.meta[0]["vung_loai_tru"][0]["can_cu"]["ngoai_pham_vi"] = "DEMO-khong-chep"
    s = m.snapshot(quet(m, monkeypatch))
    assert "ngoai_pham_vi" not in s["quet_anh"]["trang"][0]["vung_loai_tru"][0]["can_cu"]


def test_gioi_han_thoi_gian_khong_cho_900_giay(monkeypatch):
    clock = iter([0, 1000])
    monkeypatch.setattr(st, "time", SimpleNamespace(perf_counter=lambda: next(clock)))
    viec = st._ViecCoHan(SimpleNamespace(kiem_huy=lambda: None), 900)
    with pytest.raises(LoiNghiepVu) as e:
        viec.kiem_huy()
    assert e.value.ma == "DC_QUA_GIOI_HAN"


def test_huy_trong_vong_pixel():
    a = mau_anh("gach")
    meta = metadata_anh(a, hs.bam(a["raw"]))
    with anh.doc_anh(a["raw"], "image/png", 20000000, lambda: None) as im:
        he = anh.HeToaDo.tu_core(a["page"], meta, im.size)
        tu = st._tu_trang(a["page"], he, lambda: None)
        calls = 0
        def kiem():
            nonlocal calls
            calls += 1
            if calls == 10:
                raise ViecDaHuy()
        with pytest.raises(ViecDaHuy):
            st.BoPhatHienNet().quet(im, tu, kiem)


def test_engine_khong_ghi_dia_hoac_goi_mang(monkeypatch):
    import builtins
    import socket
    import tempfile
    m = tao_mau()

    pb = m.chay()["ket_qua"]
    original = builtins.open
    def mo(file, mode="r", *args, **kw):
        assert not any(c in mode for c in "wxa+"), "Không ghi đĩa trong engine"
        return original(file, mode, *args, **kw)
    def cam(*args, **kw):
        raise AssertionError("Không tệp tạm/mạng trong engine")
    monkeypatch.setattr(builtins, "open", mo)
    monkeypatch.setattr(Path, "write_bytes", cam)
    monkeypatch.setattr(Path, "write_text", cam)
    monkeypatch.setattr(tempfile, "NamedTemporaryFile", cam)
    monkeypatch.setattr(socket, "create_connection", cam)
    r = quet(m, monkeypatch, pb)
    assert r["trang_thai"] == "XONG", r


@pytest.mark.parametrize("mime", ["image/png", "image/jpeg"])
def test_doc_anh_dinh_dang_thuc(mime):
    with Image.new("RGB", (24, 16), "white") as im, io.BytesIO() as out:
        im.save(out, format="JPEG" if mime.endswith("jpeg") else "PNG")
        raw = out.getvalue()
    with anh.doc_anh(raw, mime, 20000000, lambda: None) as result:
        assert result.size == (24, 16)
    with pytest.raises(LoiNghiepVu) as e:
        anh.doc_anh(raw[:-25], mime, 20000000, lambda: None)
    assert e.value.ma == "DC_THIEU_ANH"


def test_exif_xoay_khong_tu_dong_ap_hai_lan():
    with Image.new("RGB", (24, 16), "white") as im, io.BytesIO() as out:
        exif = Image.Exif()
        exif[274] = 6
        im.save(out, format="JPEG", exif=exif)
        raw = out.getvalue()
    with pytest.raises(LoiNghiepVu) as e:
        anh.doc_anh(raw, "image/jpeg", 20000000, lambda: None)
    assert e.value.ma == "DC_THIEU_ANH"


def test_pillow_sai_phien_ban_tu_choi(monkeypatch):
    import PIL
    monkeypatch.setattr(PIL, "__version__", "DEMO-khac")
    with pytest.raises(LoiNghiepVu) as e:
        anh.doc_anh(b"DEMO", "image/png", 20000000, lambda: None)
    assert e.value.ma == "DC_CHUA_CO_BO_PHAT_HIEN"


def test_cong_cu_chay_kho_khong_bia_so_do():
    script = Path(__file__).resolve().parents[1]/"cong-cu/do_sua_tay_demo.py"
    r = subprocess.run([sys.executable, str(script), "--chay-kho"], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["cloud"] == 0 and data["anh"] is None
    assert data["local_vision"]["ket_qua"] is None and data["local_vision"]["model"] is None
    assert len(data["chay_kho"]["anh"]) == 12


@pytest.mark.parametrize("key", ["phuong_phap_detector", "phien_ban_detector"])
def test_thieu_phuong_phap_trong_cau_hinh(monkeypatch, key):
    m = tao_mau()

    pb = m.chay()["ket_qua"]
    m.cau_hinh.pop(key)
    m.dat_cau_hinh()
    kiem_loi(quet(m, monkeypatch, pb), "DC_CHUA_CO_BO_PHAT_HIEN")


@pytest.mark.parametrize("xoay", [0, 90, 180, 270])
def test_anh_lam_tron_pixel_van_map_dung_bien(xoay):
    page = {"rong": 479.8, "cao": 239.8, "don_vi": "pt"}
    size = (240, 480) if xoay in (90, 270) else (480, 240)
    meta = {"rong_nguon": 479.8, "cao_nguon": 239.8, "don_vi": "pt", "ti_le": 1,
            "xoay": xoay, "rong_px": size[0], "cao_px": size[1], "he_toa_do": "goc_tren_trai"}
    he = anh.HeToaDo.tu_core(page, meta, size)
    box = he.hop_thang([0, 0, 479.8, 239.8])
    assert he.hop_anh(box) == [0, 0, *size]
    assert he.hop_nguon(box) == [0, 0, 479.8, 239.8]


def test_cong_cu_do_that_ghi_ca_bo_sot():
    script = Path(__file__).resolve().parents[1]/"cong-cu/do_sua_tay_demo.py"
    r = subprocess.run([sys.executable, str(script), "--do-demo"], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    stats = data["anh"]["ket_qua"]
    assert stats["tp"]+stats["fn"] == 6 and stats["fn"] >= 1
    assert data["local_vision"]["ket_qua"] is None
    assert not data["anh"]["du_dieu_kien_van_hanh"]
