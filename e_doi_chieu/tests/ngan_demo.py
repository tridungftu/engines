"""Thao tác quản trị DEMO qua việc SDK thật; không dựng kho ngăn khác.

CoreGia giữ ngữ nghĩa lô/CAS/pháp nhân. Helper chỉ giao một việc DEMO
để test sửa dữ liệu giữa hai lượt và đọc bằng xem_ngan sau khi lease hết.
"""
from copy import deepcopy

from kho_tri_thuc_sdk.engine import BanGhi, Engine


def trong_ngan(mau, ham, pn="DEMO-P"):
    phieu = deepcopy(mau.app.phieu)
    phieu["nang_luc"] = [{
        "ma": "demo.ngan@1", "ten": "Kiểm ngăn DEMO", "nhan": ["van_ban"],
        "tra": "van_ban", "gioi_han": {"thoi_han_giay": 30}}]
    phieu["chay_thu_demo"] = []
    app = Engine(phieu, thu_muc_goi=mau.app.thu_muc_goi)
    ket_qua, loi = [], []

    @app.nang_luc("demo.ngan@1")
    def kiem(viec):
        try:
            ket_qua.append(ham(viec.ngan))
        except Exception as exc:
            loi.append(exc)
        return {"loai": "van_ban", "van_ban": "DEMO"}

    vid = mau.core.giao_viec("demo.ngan@1", {"loai": "van_ban", "van_ban": "DEMO"}, phap_nhan_id=pn)
    mau.core.chay(app)
    assert mau.core.xem(vid)["trang_thai"] == "XONG", mau.core.xem(vid)
    if loi:
        raise loi[0]
    return ket_qua[0]


def sua_ngan(mau, khoa, gia_tri, row_version, pn="DEMO-P"):
    from e_doi_chieu.ho_so import dong_phong_bi

    gia_tri = deepcopy(gia_tri)
    if isinstance(gia_tri.get("phong_bi"), dict):
        gia_tri["phong_bi"] = dong_phong_bi(gia_tri["phong_bi"])
    # Các cột này do Core cấp, không gửi lại thành dữ liệu người dùng.
    for k in ("id", "phap_nhan_id", "row_version", "tao_luc", "sua_luc", "het_han_luc", "viec_id"):
        gia_tri.pop(k, None)

    def sua(ngan):
        with ngan.lo() as lo:
            lo.sua("luot_doi_chieu", khoa, gia_tri, row_version=row_version)
    return trong_ngan(mau, sua, pn)


def cac_luot(mau, pn="DEMO-P"):
    from e_doi_chieu.ho_so import mo_phong_bi

    rows = mau.core.xem_ngan(mau.app.ma, "luot_doi_chieu")
    for d in rows:
        for k in ("luc_chiem", "han_chiem"):
            if d.get(k) is not None:
                d[k] = float(d[k])
        if isinstance(d.get("phong_bi"), str):
            d["phong_bi"] = mo_phong_bi(d["phong_bi"])
    return [BanGhi.tu_dict(d) for d in rows if d["phap_nhan_id"] == pn]
