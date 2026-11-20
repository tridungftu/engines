"""Đường chạy chung của các năng lực phân luồng (lead tách ở đầu PL-4, 20/11/2026).

Mỗi hàm là một ĐIỂM NỐI có chủ sở hữu riêng để các lát ghép song song không sửa chồng:
- bat_dau          → PL-4 (chốt kỳ tháng ở lượt đầu tiên của tháng mới, mọi năng lực)
- doc_tep_lo       → PL-6 (thêm Excel/CSV theo khuôn cột)
- doc_cai_dat      → chung (lead)
- chay_phan_luong  → PL-4 (hồ sơ hành vi: cờ, chia nhỏ qua lô, cập nhật hồ sơ);
                     PL-5/PL-7 chỉ GỌI hàm này (loai_ai, canh_bao_them), không sửa thân
- xuat_ket_qua     → PL-8 (tệp Excel danh sách Đỏ)
Không đổi hành vi so với PL-2/PL-3.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256

from . import __version__, chon_mau, ngan_luot
from .doc_lo import doc_lo_json
from .kieu import KetQuaDong, Lo, Nguong
from .loi import loi
from .nguong import doc_nguong
from .phan_loai import BoPhanLoai, doc_bo_phan_loai, doc_danh_muc_loai
from .phan_luong import xet_lop1_lo, xet_lop23_lo
from .ty_le import ChinhSach, doc_chinh_sach
from .xuat_json import tao_tep_json, tao_truong_ra


@dataclass(frozen=True)
class CaiDat:
    nguong: Nguong
    danh_muc: dict[str, dict]
    bo: BoPhanLoai
    cs: ChinhSach


def bat_dau(viec) -> int:
    """Gọi đầu MỌI năng lực; chốt tháng và làm mới hồ sơ, trả số cặp đã chốt."""
    from . import chot_ky, ho_so

    return chot_ky.chot_neu_can(
        viec, doc_chinh_sach_buoc(viec.tham_so),
        lam_moi_ho_so=lambda cu, ky: ho_so.ve_ban_ghi(
            ho_so.lam_moi(ho_so.tu_ban_ghi(cu), ky)),
    )


def doc_tep_lo(viec) -> tuple[Lo, bytes]:
    """Đọc JSON hoặc bảng theo khuôn cột; giữ bytes gốc để băm kiểm toán."""
    from . import doc_bang

    tep = viec.dau_vao["tep"]
    with viec.mo_tep(tep["tep_id"]) as f:
        du_lieu = f.read(doc_bang.TOI_DA_BYTE + 1)
    kieu = doc_bang.nhan_dien(du_lieu, tep.get("ten"), tep.get("mime"))
    if kieu == "json":
        return doc_lo_json(du_lieu), du_lieu
    ts = viec.tham_so
    khuon, ma_module = ts.get("khuon_cot_json"), ts.get("ma_module")
    if (not isinstance(khuon, str) or not khuon.strip()
            or not isinstance(ma_module, str) or not ma_module.strip()):
        raise loi("THAM_SO_KHONG_HOP_LE")
    lo = doc_bang.doc_lo_bang(
        du_lieu, kieu, khuon_cot_json=khuon, ma_module=ma_module,
        tien_te=ts.get("tien_te") or None, ky=ts.get("ky") or None,
    )
    return lo, du_lieu


def _so_tham_so(gia_tri) -> Decimal | None:
    if gia_tri is None:
        return None
    # Cổng SDK trả số JSON bằng float; đổi qua chuỗi, không Decimal(float).
    if isinstance(gia_tri, bool) or not isinstance(gia_tri, (int, float, Decimal)):
        raise loi("THAM_SO_KHONG_HOP_LE")
    return Decimal(str(gia_tri))


def doc_chinh_sach_buoc(tham_so: Mapping[str, object]) -> ChinhSach:
    return doc_chinh_sach(tham_so.get("chinh_sach_json"),
                          ty_le_duoi_sad=_so_tham_so(tham_so.get("ty_le_duoi_sad")))


def doc_cai_dat(tham_so: Mapping[str, object], lo: Lo) -> CaiDat:
    ng = doc_nguong(lo.nguong, tham_so.get("nguong_json"))
    danh_muc = doc_danh_muc_loai(tham_so.get("danh_muc_loai_json"))
    bo = doc_bo_phan_loai(tham_so.get("bo_phan_loai_json"), danh_muc)
    return CaiDat(ng, danh_muc, bo, doc_chinh_sach_buoc(tham_so))


def chay_phan_luong(viec, lo: Lo, du_lieu: bytes, *,
                    loai_ai: Mapping[str, str] | None = None,
                    canh_bao_them: Sequence[str] = ()) -> dict:
    """Lớp 1 → 2 → 3, tệp kết quả, ghi lượt (dong_luot trước, luot sau cùng).

    loai_ai: mã nghiệp vụ → loại do Local AI gán (PL-5); chỉ dùng cho dòng chưa có loại
    từ module/quy tắc. canh_bao_them: câu cảnh báo bổ sung (không chứa tỷ lệ, C5).
    """
    import logging
    from decimal import localcontext

    from . import chot_ky, ho_so, ngan_ho_so
    from .phan_luong import bam_doi_tac

    ts = viec.tham_so
    if ts.get("ma_module") and ts["ma_module"] != lo.ma_module:
        raise loi("DU_LIEU_KHONG_HOP_LE")
    bam_dau_vao = "sha256:" + sha256(du_lieu).hexdigest()
    ma_luot = ngan_luot.ma_luot_cua_viec(viec, bam_dau_vao)
    # Ngữ cảnh riêng của việc; giữ nguyên chữ ký lớp 2/3 và các điểm nối PL-5/PL-7.
    viec._ma_luot_phan_luong = ma_luot
    luot_cu = viec.ngan.doc("luot", {"ma_luot": ma_luot})
    hat_giong = (bytes.fromhex(luot_cu.gia_tri["hat_giong"]) if luot_cu is not None
                 else chon_mau.sinh_hat_giong())
    viec.tien_do(10, "Đang kiểm tra lô nghiệp vụ.")
    cd = doc_cai_dat(ts, lo)
    cac_ho_so = ngan_ho_so.doc_ho_so_khau(viec, ts["khau"])
    canh_bao = list(canh_bao_them)
    if any(hs.tien_te is not None and hs.tien_te != cd.nguong.tien_te
           for hs, _ in cac_ho_so.values()):
        canh_bao.append("Tiền tệ ngưỡng đã đổi; lịch sử số tiền được tính lại, vẫn giữ lịch sử đối tác.")
    # Chia nhỏ gom theo đối tác + khâu, kể cả lịch sử thuộc loại khác (Q8).
    tong_ngay = {}
    with localcontext() as ctx:
        ctx.prec = 40
        for hs, _ in cac_ho_so.values():
            hs = ho_so.theo_tien_te(hs, cd.nguong.tien_te)
            for bam, cac_ngay in hs.tong_ngay.items():
                ngay_so = tong_ngay.setdefault(bam, {})
                for ngay, so in cac_ngay.items():
                    ngay_so[ngay] = ngay_so.get(ngay, Decimal(0)) + so

    def tong_truoc(bam, ngay):
        return tong_ngay.get(bam, {}).get(ngay.isoformat(), Decimal(0))

    ds_lop1 = xet_lop1_lo(lo, ts, nguong=cd.nguong, danh_muc=cd.danh_muc, bo=cd.bo,
                          truong_phan_loai=ts.get("truong_phan_loai"), loai_ai=loai_ai,
                          tong_truoc=tong_truoc)
    anh_chup = {
        loai: ho_so.anh_chup(
            cac_ho_so[loai][0] if loai in cac_ho_so else ho_so.moi(ts["khau"], loai),
            tien_te_nguong=cd.nguong.tien_te,
        ) for loai in dict.fromkeys(qd.loai for qd in ds_lop1)
    }
    thong_tin = {
        "ma_luot": ma_luot, "bam_hat_giong": chon_mau.bam_hat_giong(hat_giong),
        "bam_dau_vao": bam_dau_vao, "phien_ban_engine": __version__,
        "khau": ts["khau"], "ma_module": lo.ma_module,
    }
    viec.tien_do(50, "Đang chọn mẫu kiểm tra.")
    ds_dong = xet_lop23_lo(viec, lo, ds_lop1, khau=ts["khau"], cs=cd.cs,
                          hat_giong=hat_giong, ho_so_theo_loai=anh_chup.__getitem__)
    if luot_cu is not None:
        from .kieu import KHONG_CHON, tach_ly_do
        from .ngan_chung import tim_tat_ca

        # Tỷ lệ/lịch sử có thể đã đổi sau lần chạy đầu; giữ quyết định đã chốt.
        da_luu = {bg.gia_tri["ma"]: bg.gia_tri for bg in tim_tat_ca(
            viec, "dong_luot", {"ma_luot": ma_luot})}
        da_chot = []
        for dong in ds_dong:
            if dong.ma not in da_luu:
                raise loi("NGAN_BAN")
            gt = da_luu[dong.ma]
            ly_do = tach_ly_do(gt["ly_do"])
            da_chot.append(KetQuaDong(
                dong.ma, "xanh" if ly_do == (KHONG_CHON,) else "do", ly_do,
                dong.co, gt["loai"], gt["nguon_loai"]))
        ds_dong = tuple(da_chot)
    theo_loai = {}
    for qd in ds_lop1:
        nv = qd.nv
        bam = bam_doi_tac(lo.ma_module, nv.doi_tac) if nv.doi_tac is not None else None
        theo_loai.setdefault(qd.loai, []).append((qd.tien_ss, bam, nv.ngay))
    ky = chot_ky.ky_hien_tai()
    ngay_xu_ly = chot_ky.ngay_hien_tai()
    cua_so = int(Decimal(str(ts.get("cua_so_chia_nho_ngay", 7))))
    so_bo = {}

    def ham_cong(loai, ds):
        def cap_nhat(hs):
            moi, so_bo[loai] = ho_so.cong(
                hs, ds, ky=ky, cua_so_ngay=cua_so, te=cd.nguong.te.so,
                tien_te_nguong=cd.nguong.tien_te, ngay_xu_ly=ngay_xu_ly)
            return moi
        return cap_nhat

    cap_nhat = {loai: ham_cong(loai, ds) for loai, ds in theo_loai.items()}
    if luot_cu is None:
        # Chỉ tính trên ảnh chụp đã đọc, thuần và không ghi ngăn trước khi xuất.
        for loai, ham in cap_nhat.items():
            ham(cac_ho_so[loai][0] if loai in cac_ho_so else ho_so.moi(ts["khau"], loai))
        if sum(so_bo.values()):
            canh_bao.append("Hồ sơ hành vi vượt trần 20.000 đối tác; đã bỏ đối tác lâu không gặp.")
        so_bo.clear()  # Nhật ký bên dưới chỉ dùng số thực sự cộng qua CAS.
    truong = xuat_ket_qua(viec, lo, cd.nguong, ds_dong, thong_tin=thong_tin,
                          canh_bao_them=canh_bao)
    viec.tien_do(90, "Đang ghi kết quả lượt phân luồng.")
    # Hồ sơ cộng CÙNG lô nguyên tử với dấu luot: Core giao lại việc không cộng hai lần.
    # Lô ≤ 100 lệnh nên tối đa 99 hồ sơ đi cùng luot; phần dư (chỉ khi lô có
    # trên 99 loại, danh mục tối đa 100 + chua_phan_loai) ghi trước, không nguyên tử.
    cac_loai = list(cap_nhat)
    du, cuoi = cac_loai[:-99], cac_loai[-99:]
    ngan_ho_so.tao_ho_so_rong(viec, ts["khau"], cac_loai)
    if luot_cu is None:
        for loai in du:
            ngan_ho_so.ghi_ho_so(viec, ts["khau"], loai, cap_nhat[loai])
    ngan_luot.ghi_luot(viec, {
        "ma_luot": ma_luot, "ma_module": lo.ma_module, "khau": ts["khau"],
        "hat_giong": hat_giong.hex(), "bam_dau_vao": bam_dau_vao,
    }, ds_dong, lenh_cuoi=lambda lo_ngan: ngan_ho_so.them_lenh_cap_nhat(
        viec, lo_ngan, ts["khau"], {loai: cap_nhat[loai] for loai in cuoi}))
    if sum(so_bo.values()):
        logging.getLogger(__name__).warning(
            "Hồ sơ hành vi vượt trần 20.000 đối tác; đã bỏ %d đối tác lâu không gặp.",
            sum(so_bo.values()))
    return truong


def xuat_ket_qua(viec, lo: Lo, ng: Nguong, ds_dong: Sequence[KetQuaDong], *,
                 thong_tin: dict, canh_bao_them: Sequence[str] = ()) -> dict:
    """Tải JSON và Excel dòng Đỏ lên Core; lô không có Đỏ trả tep_ds_do null."""
    noi_dung = tao_tep_json(ds_dong, thong_tin=thong_tin)
    tep_json = viec.tai_tep_ra("phan-luong.json", noi_dung, "application/json")
    truong = tao_truong_ra(lo, ng, ds_dong, thong_tin=thong_tin, tep_json=tep_json)
    if any(d.luong == "do" for d in ds_dong):
        # Nạp khi cần Excel; đường import khung không buộc nạp thư viện Excel.
        from . import xuat_excel

        du_lieu = xuat_excel.lap_ds_do(ds_dong, **{
            cot: thong_tin[cot]
            for cot in ("ma_luot", "ma_module", "khau", "phien_ban_engine")
        })
        truong["tep_ds_do"] = viec.tai_tep_ra(
            "ds-can-kiem.xlsx", du_lieu,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    if canh_bao_them:
        them = "; ".join(c for c in canh_bao_them if c)
        cu = truong.get("canh_bao") or ""
        truong["canh_bao"] = ((cu + "; " if cu else "") + them)[:500]
    return truong
