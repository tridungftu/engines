"""Sinh `_chung/docs/DANH-MUC-ENGINE-CHO-MODULE.md` từ `engine.json` của mọi gói.

Cách dùng (tại gốc repo, chỉ cần thư viện chuẩn Python ≥ 3.9):
    python _chung/cong-cu/sinh_danh_muc_engine.py          # ghi lại tệp danh mục
    python _chung/cong-cu/sinh_danh_muc_engine.py --kiem   # chỉ kiểm, mã thoát 1 nếu tệp chưa cập nhật

Script kiểm luôn:
- mọi engine có gói đều có ghi chú trong GHI_CHU;
- mọi chuỗi mẫu trong CHUOI nối đúng `nhan`/`tra` của `engine.json`
  (bước 1 nhận `tep`, bước cuối trả `truong`/`van_ban`/`tep`).
Sai một điều thì mã thoát 1, kèm lý do. Đổi engine.json thì chạy lại script trong cùng PR.
"""
import glob
import json
import os
import sys

GOC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RA = os.path.join(GOC, "_chung", "docs", "DANH-MUC-ENGINE-CHO-MODULE.md")
GHEP_DUOC = ("truong", "van_ban", "tep")
KIEU = {"van_ban": "văn bản", "so": "số", "so_tien": "số tiền", "ngay": "ngày",
        "co_khong": "có/không", "tep": "tệp", "chon": "chọn"}

# Thứ tự hiển thị và ghi chú cho module. Engine mới: thêm một dòng ở đây.
GHI_CHU = {
    "e_ocr": ("PDF scan, ảnh → chữ có vị trí, văn bản thuần, Word giữ bảng",
              "ABBYY trước, Tesseract dự phòng; ABBYY thật chưa chạy thử"),
    "e_hoi_ai": ("Hỏi AI về tài liệu có trích dẫn; bước AI giữa chuỗi của engine khác",
                 "**Chỉ Local AI**; chưa có năng lực Cloud; prompt thuộc module"),
    "e_mask": ("Che/mở che tên, MST, địa chỉ… trước khi đưa ra ngoài",
               "Kho bí danh tạm giữ trong bộ nhớ (mất khi khởi động lại); mở che cần `ma_yeu_cau`"),
    "e_trich_xuat": ("Trích tham số hợp đồng theo bộ tham số của module",
                     "Bộ tham số + mã băm truyền qua Cài đặt bước"),
    "e_hoa_don": ("Đọc XML, ZIP hóa đơn điện tử; lập bảng kê XLSX",
                  "Chưa có PDF, chưa tải cổng thuế"),
    "e_kiem_excel": ("Kiểm toàn vẹn file Excel (K1–K8); đọc bảng nhiều tầng tiêu đề",
                     "Ô đích, bộ nhóm, khuôn cột do module truyền"),
    "e_phan_luong": ("Phân luồng kiểm tra theo khâu, ngưỡng PM/TE/SAD và chọn mẫu",
                     "PL-2: `audit.phan_luong@1` nhận JSON, có DEMO; Excel/CSV, AI, hóa đơn và ghi kết quả chờ lát sau; danh sách Excel để trống tới PL-8"),
    "e_doi_chieu": ("So bản Word chuẩn với bản đã ký",
                    "Bước đầu nhận **tệp JSON cặp** do module lập; chặn hiệu lực là việc của module"),
    "e_tra_cuu": ("Hỏi đáp 3 tầng trên kho tài liệu",
                  "Bước đầu nhận **tệp JSON yêu cầu**; cần Kho tài liệu của Core (chưa có)"),
}

# Chuỗi mẫu: (mục đích, các bước, cột ngăn nhận). Một bước có nhiều lựa chọn thì dùng tuple.
CHUOI = [
    ("Phân luồng kiểm tra lô JSON theo khâu",
     ["audit.phan_luong@1"], "luồng, lý do, số đếm, tổng tiền Đỏ, tệp JSON, mã lượt và băm"),
    ("Lấy chữ từ PDF scan/ảnh", ["ocr.doc_van_ban@1"], "1 trường văn bản"),
    ("Chuyển PDF scan/ảnh sang Word", ["ocr.xuat_word@1"], "1 trường tệp (DOCX)"),
    ("Hỏi AI về PDF scan/ảnh", ["ocr.doc_tai_lieu@1", "ai.hoi_tai_lieu@1"],
     "trả lời, có căn cứ, trích dẫn, model"),
    ("Hỏi AI về hợp đồng Word", ["trich.doc_docx@1", "ai.hoi_tai_lieu@1"], "như trên"),
    ("Trích tham số hợp đồng Word",
     ["trich.doc_docx@1", "trich.chuan_bi@1", "ai.hoi_theo_yeu_cau@1", "trich.hau_kiem@1", "trich.xuat_ket_qua@1"],
     "tệp JSON, tệp Excel, số tham số, số ô cần soát, có căn cứ"),
    ("Trích tham số hợp đồng PDF",
     ["ocr.doc_tai_lieu@1", "trich.chuan_bi@1", "ai.hoi_theo_yeu_cau@1", "trich.hau_kiem@1", "trich.xuat_ket_qua@1"],
     "như trên"),
    ("Đọc một hóa đơn XML", ["hoa_don.doc_xml@2"], "các trường hóa đơn (số, ngày, MST, tiền…)"),
    ("Đọc gói ZIP hóa đơn", ["hoa_don.doc_zip@1"], "số tệp, đọc được, lỗi, trùng…"),
    ("Lập bảng kê XLSX", [("hoa_don.doc_xml@2", "hoa_don.doc_zip@1"), "hoa_don.bang_ke_xlsx@1"],
     "tệp bảng kê + số đếm"),
    ("Kiểm toàn vẹn file Excel", ["excel.toan_ven@1"], "số cờ Cao/Trung bình, ô đích, báo cáo Excel, JSON"),
    ("Đọc bảng Excel (BOQ, hồ sơ đợt, báo giá…)", ["excel.doc_bang@1"],
     "sheet, số dòng, giá trị HĐ, giá trị đề nghị, JSON"),
    ("Che tệp Word/Excel bằng Local AI, giữ định dạng",
     ["mask.chuan_bi_tep_ai_cuc_bo@1", "ai.hoi_mask_cuc_bo@1", "mask.hau_kiem_tep_giu_dinh_dang@1"],
     "tệp đã che, mã yêu cầu, phần còn sót, kiểm tiền/ngày"),
    ("Đối chiếu bản ký",
     ["doi_chieu.nhan_cap@1", "doi_chieu.so_van_ban@1", "doi_chieu.phat_hien_sua_tay@1", "doi_chieu.chuan_bi_ai@1",
      "ai.hoi_theo_yeu_cau@1", "doi_chieu.phan_loai_diem_lech@1", "doi_chieu.xuat_ket_qua@1"],
     "kết luận, số điểm nghiêm trọng, đề nghị chặn, JSON, PDF"),
    ("Tra cứu tài liệu",
     ["tra_cuu.nhan_yeu_cau@1", "tra_cuu.cat_doan@1", "tra_cuu.chuan_bi_ai@1", "ai.hoi_theo_yeu_cau@1",
      ("tra_cuu.phan_loai_tai_lieu@1", "tra_cuu.phan_tich_cau_hoi@1", "tra_cuu.xep_hang_lai@1", "tra_cuu.soan_tra_loi@1"),
      "tra_cuu.xuat_ket_qua@1"],
     "trả lời, nhãn, tầng, có căn cứ, có mâu thuẫn, cần duyệt, JSON"),
]

LOAI_CHUNG = [
    ("van_ban_tai_lieu", "Văn bản có vị trí trang, bảng, nguồn đọc"),
    ("yeu_cau_ai", "Yêu cầu hỏi AI (prompt, tài liệu, khuôn trả lời)"),
    ("tra_loi_ai", "Trả lời AI có trích dẫn, đã kiểm"),
    ("van_ban_da_che", "Văn bản đã che định danh"),
    ("bang_trich_xuat", "Bảng tham số đã trích"),
    ("ho_so_doi_chieu", "Hồ sơ đối chiếu giữa các bước"),
    ("ho_so_tra_cuu", "Hồ sơ tra cứu giữa các bước"),
]

QUY_TAC = """## 2. Quy tắc module phải theo

1. **Quy tắc nối bước** (API v1 b.2):
   - bước 1 nhận `tep`, là tệp người dùng tải ở nút;
   - bước *k* hợp lệ khi loại `tra` của bước *k−1* nằm trong `nhan` của bước *k*; Core tự kiểm khi khai quy trình.
2. **Bước cuối phải trả `truong`, `van_ban` hoặc `tep`** thì mới ghép được vào cột ngăn của module. Năng lực trả loại riêng (mục 4) **chỉ dùng ở giữa chuỗi**.
3. **Bước sau không nhận lại tệp gốc.** Cần hai kết quả khác nhau từ cùng một tệp thì làm **hai nút** (hai quy trình), người dùng tải tệp hai lần. Ví dụ: kiểm toàn vẹn Excel và đọc bảng Excel.
4. **Nhận kết quả:**
   - khi quy trình xong, Core gửi `quy_trinh.xong`; SDK module gọi hàm nhận với `tep_nut` và `ghep` (xem `docs/goi-gui-engine/sdk-2.2.0/HUONG-DAN-VIET-MODULE.md`);
   - trường kiểu `tep` (báo cáo Excel, JSON chi tiết, Word…) là tham chiếu tệp trong kho Core; module đọc nội dung bằng cổng đọc tệp của SDK module.
5. **Tiền** (kiểu `so_tien`):
   - dạng `{"so": "<chuỗi thập phân>", "tien_te": "VND"}`;
   - chưa rõ đơn vị thì **cả trường là `null`**, kèm cờ chưa rõ (nếu engine có);
   - module không tự gán VND.
   - Hiển thị: tiền có dấu chấm hàng nghìn kèm đơn vị; ngày dd/mm/yyyy.
6. **AI:**
   - mọi bước gọi model đi qua `e_hoi_ai`, hiện **chỉ Local**;
   - Cloud chưa có; khi có (bản 2) chỉ nhận `van_ban_da_che`, tức phải có bước Mask đứng trước;
   - M9 và nhóm tài liệu 07-Nhân sự luôn chỉ Local.
7. **Lỗi:** engine trả mã lỗi kèm câu tiếng Việt. Module hiển thị câu đó, không tự diễn giải lại. Quá trần thì engine từ chối, không cắt ngầm.
8. **Dữ liệu thử:** chỉ dùng DEMO (ví dụ "Công ty DEMO Ánh Dương", 1.000.000 VND, 30/10/2026).
9. **Cài đặt bước thuộc module:** prompt, bộ tham số hợp đồng, bộ nhóm dữ liệu gốc, khuôn cột, bộ quy tắc đối chiếu… đặt trong Cài đặt bước của quy trình; engine không có mặc định chung cho các thứ này.
"""

LUU_Y_CHUOI = """**Lưu ý:**
- **Mask:**
  - `mask.che_van_ban@1` và `mask.hau_kiem_ai_cuc_bo@1` trả `van_ban_da_che`, hiện chưa có bước nào nhận tiếp. Bước Cloud thuộc bản 2.
  - Mở che (`mask.mo_che_tep@1`, `mask.mo_che_van_ban@1`) cần đúng `ma_yeu_cau` do Core cấp lúc che.
  - Hỏi lead Mask trước khi thiết kế luồng che/mở che trong module.
- **Đối chiếu, Tra cứu:** bước đầu nhận **tệp JSON** (cặp tài liệu, yêu cầu tra cứu) do module lập, không phải tệp người dùng tải. Thứ tự các bước giữa theo README của gói.
- **Tra cứu** cần Kho tài liệu và chỉ mục của Core. Core chưa có phần này.
"""


def esc(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def doc_engine():
    ds = {}
    for p in sorted(glob.glob(os.path.join(GOC, "*", "goi", "*", "engine.json"))):
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        ds[d["ma"]] = d
    return ds


def kiem_chuoi(ds):
    nl = {n["ma"]: n for d in ds.values() for n in d["nang_luc"]}
    loi = []
    for muc_dich, buoc, _ in CHUOI:
        truoc = {"tep"}
        for i, b in enumerate(buoc):
            lua = b if isinstance(b, tuple) else (b,)
            ra = set()
            for m in lua:
                if m not in nl:
                    loi.append(f"Chuỗi «{muc_dich}»: năng lực {m} không còn trong engine.json")
                    continue
                if not truoc & set(nl[m]["nhan"]):
                    loi.append(f"Chuỗi «{muc_dich}»: bước {i + 1} {m} không nhận {sorted(truoc)}")
                ra.add(nl[m]["tra"])
            truoc = ra
        if truoc - set(GHEP_DUOC):
            loi.append(f"Chuỗi «{muc_dich}»: bước cuối trả {sorted(truoc)}, không ghép được vào cột ngăn")
    return loi


def gh(g):
    p = []
    if g.get("tep_toi_da_mib"):
        p.append(f"tệp ≤ {g['tep_toi_da_mib']} MiB")
    if g.get("ky_tu_toi_da"):
        p.append(f"≤ {g['ky_tu_toi_da']:,} ký tự".replace(",", "."))
    if g.get("thoi_han_giay"):
        p.append(f"thời hạn {g['thoi_han_giay']} giây")
    if g.get("mime"):
        p.append("loại tệp: " + ", ".join(f"`{m}`" for m in g["mime"]))
    return "; ".join(p) or "—"


def chi_tiet(d):
    out = []
    rieng = ", ".join(f"`{x['ma']}`" for x in d.get("loai_du_lieu_rieng", [])) or "không"
    out.append(f"### {d['ma']} — {d['ten']} (gói {d['phien_ban']})\n")
    out.append(f"Loại dữ liệu riêng: {rieng}. Số việc đồng thời: {d.get('tai_nguyen', {}).get('so_viec_dong_thoi', '—')}.\n")
    for n in d["nang_luc"]:
        nhan = ", ".join(f"`{x}`" for x in n["nhan"])
        out.append(f"#### `{n['ma']}` — {n.get('ten', '')}\n")
        out.append(f"- **Nhận:** {nhan} → **Trả:** `{n['tra']}`"
                   + (" (ghép được vào cột ngăn)" if n["tra"] in GHEP_DUOC else " (chỉ dùng ở giữa chuỗi)"))
        out.append(f"- **Giới hạn:** {gh(n.get('gioi_han', {}))}; hủy được: {'có' if n.get('huy_duoc') else 'không'}")
        ts = n.get("tham_so", [])
        if ts:
            out.append("- **Cài đặt bước:**\n")
            out.append("| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |")
            out.append("|---|---|---|---|---|---|")
            for t in ts:
                lc = ", ".join(f"`{x['ma']}` ({x['ten']})" for x in t.get("lua_chon", []))
                tran = []
                if "toi_thieu" in t:
                    tran.append(f"≥ {t['toi_thieu']}")
                if "toi_da" in t:
                    tran.append(f"≤ {t['toi_da']}" + (" ký tự" if t["kieu"] == "van_ban" else ""))
                md = t.get("mac_dinh", "")
                md = "trống" if md == "" else f"`{json.dumps(md, ensure_ascii=False)}`"
                out.append(f"| `{t['ma']}` | {esc(t.get('ten', ''))} | {KIEU.get(t['kieu'], t['kieu'])} | "
                           f"{'có' if t.get('bat_buoc') else 'không'} | {md} | {esc(lc or ' · '.join(tran) or '—')} |")
            out.append("")
        tr = n.get("truong_ra", [])
        if tr:
            out.append("- **Trường trả ra (ghép vào cột ngăn của module):**\n")
            out.append("| Mã | Tên | Kiểu |")
            out.append("|---|---|---|")
            for t in tr:
                out.append(f"| `{t['ma']}` | {esc(t.get('ten', ''))} | {KIEU.get(t['kieu'], t['kieu'])} |")
        out.append("")
    return out


def sinh(ds):
    thu_tu = [m for m in GHI_CHU if m in ds]
    tong = sum(len(ds[m]["nang_luc"]) for m in thu_tu)
    phien_ban = ", ".join(f"`{m}` {ds[m]['phien_ban']}" for m in thu_tu)
    o = []
    o.append("# Danh mục engine cho lập trình module\n")
    o.append("*Tệp **sinh tự động** bằng `python _chung/cong-cu/sinh_danh_muc_engine.py` từ `engine.json` của mọi gói; "
             "không sửa tay. Muốn đổi ghi chú hay chuỗi mẫu: sửa `GHI_CHU`/`CHUOI` trong script rồi chạy lại. "
             "Kiểm tự động trên GitHub báo đỏ khi tệp chưa cập nhật theo `engine.json` hoặc một chuỗi mẫu nối sai.*\n")
    o.append(f"*Phiên bản gói lúc sinh: {phien_ban}.*\n")
    o.append("## 1. Kết luận\n")
    o.append(f"- **{len(thu_tu)} engine, {tong} năng lực.** Tất cả mới **kiểm bằng Core giả (CoreGia)**, chưa nối Core thật, "
             "nên chưa engine nào \"SẴN SÀNG\". Module lập trình và test bằng dữ liệu DEMO.")
    o.append("- **Module không gọi engine.** Module khai **nút** trong phiếu module. Admin tạo **quy trình** (chuỗi bước engine) "
             "gắn vào nút trên Core. Kết quả bước cuối về **ngăn** của module.")
    o.append("- Tải gói: mục **Releases** của repo `tridungftu/engines`; chọn bản có tệp `<engine>-<phiên bản gói>.zip` khớp cột "
             "\"Gói\" dưới đây. Mỗi bản có `SHA256SUMS.txt`, `DANH-SACH-GOI.json`, `HUONG-DAN-CAI-NGHIEM-THU.md` và wheel SDK.\n")
    o.append("| Engine | Tên | Gói | Số năng lực | Dùng khi | Lưu ý cho module |")
    o.append("|---|---|---|---:|---|---|")
    for m in thu_tu:
        d = ds[m]
        dung, luu_y = GHI_CHU[m]
        o.append(f"| `{m}` | {esc(d['ten'])} | {d['phien_ban']} | {len(d['nang_luc'])} | {dung} | {luu_y} |")
    o.append("")
    o.append(QUY_TAC)
    o.append("## 3. Chuỗi bước mẫu (quy trình)\n")
    o.append("Script đã kiểm mọi chuỗi dưới đây nối đúng `nhan`/`tra` trong `engine.json`. Tên trường ra chi tiết ở mục 5.\n")
    o.append("| # | Mục đích | Chuỗi bước | Cột ngăn nhận |")
    o.append("|---:|---|---|---|")
    for i, (muc_dich, buoc, cot) in enumerate(CHUOI, 1):
        s = " → ".join(" / ".join(f"`{x}`" for x in b) if isinstance(b, tuple) else f"`{b}`" for b in buoc)
        o.append(f"| {i} | {muc_dich} | {s} | {cot} |")
    o.append("")
    o.append(LUU_Y_CHUOI)
    o.append("## 4. Loại dữ liệu dùng chung giữa các bước\n")
    o.append("| Mã | Ý nghĩa | Năng lực tạo ra | Năng lực nhận |")
    o.append("|---|---|---|---|")
    for ma, y in LOAI_CHUNG:
        tao = [n["ma"] for m in thu_tu for n in ds[m]["nang_luc"] if n["tra"] == ma]
        nhan = [n["ma"] for m in thu_tu for n in ds[m]["nang_luc"] if ma in n["nhan"]]
        o.append(f"| `{ma}` | {y} | {', '.join(f'`{x}`' for x in tao) or '—'} | {', '.join(f'`{x}`' for x in nhan) or '— (chưa có)'} |")
    o.append("")
    o.append("Module **không đọc** các loại này: chúng chỉ đi giữa các bước. Định nghĩa đầy đủ: `_chung/docs/LOAI-DU-LIEU-RIENG.md`.\n")
    o.append("## 5. Chi tiết từng năng lực (sinh từ `engine.json`)\n")
    for m in thu_tu:
        o.extend(chi_tiet(ds[m]))
    return "\n".join(o).rstrip() + "\n"


def main():
    ds = doc_engine()
    loi = [f"Engine {m} chưa có ghi chú trong GHI_CHU của script" for m in ds if m not in GHI_CHU]
    loi += kiem_chuoi(ds)
    if loi:
        print("\n".join("LỖI: " + x for x in loi))
        return 1
    moi = sinh(ds)
    if "--kiem" in sys.argv:
        cu = open(RA, encoding="utf-8").read() if os.path.exists(RA) else ""
        if cu != moi:
            print("LỖI: _chung/docs/DANH-MUC-ENGINE-CHO-MODULE.md chưa cập nhật. "
                  "Chạy: python _chung/cong-cu/sinh_danh_muc_engine.py rồi commit.")
            return 1
        print("[ĐẠT] Danh mục engine khớp engine.json; mọi chuỗi mẫu nối đúng.")
        return 0
    with open(RA, "w", encoding="utf-8", newline="\n") as f:
        f.write(moi)
    print(f"Đã ghi {os.path.relpath(RA, GOC)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
