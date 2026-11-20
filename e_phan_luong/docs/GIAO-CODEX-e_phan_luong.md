# Giao Codex — `e_phan_luong` (Phân luồng kiểm tra — Audit) theo SDK 2.2.0

*Lập 20/11/2026 (Claude, lead). Căn cứ: `e_phan_luong/docs/PHIEU-ENGINE-e_phan_luong.md` (Anh duyệt 20/11/2026, §10 không đổi), `AGENTS.md`, SDK 2.2.0, kết quả kiểm 2 điểm "Cần Core" (§4). Giờ là **ước tính, chưa đo**.*

## 1. Kết luận

- **10 lát PL-0 → PL-9 (48 giờ ước tính) như phiếu §9; mỗi lát một nhánh `codex/e_phan_luong-<lát>`, một PR.** Anh yêu cầu (20/11) dùng nhiều Codex nhất có thể: mỗi lát chia thành **việc con** (PL-1A, PL-1B…), mỗi việc con một worktree, một Codex, **sở hữu tệp riêng**. Lead gộp các việc con của cùng lát vào nhánh lát rồi mở một PR. Nhánh việc con chỉ ở máy, không đẩy.
- **Hợp đồng mô-đun cố định trước** (§2): `kieu.py` và `loi.py` do lead viết sẵn, Codex không sửa. Mỗi việc con chỉ viết tệp của mình và test của mình.
- **Điểm dừng:** sau PL-3 (bản dùng được với JSON) lead báo Anh. **Anh yêu cầu thêm (20/11, 21:30): "làm tối đa các việc, dùng nhiều Codex nhất có thể"** → PL-4…PL-8 giao song song ngay (đợt 4, §3.2); nhánh PL-4 trở đi chưa gộp main cho tới khi Anh xem báo cáo PL-3.

| Đợt | Việc | Tệp sở hữu (trong `goi/e_phan_luong/e_phan_luong/` trừ khi ghi khác) | Thuộc PR | Mức | Giờ (ước tính) |
|---|---|---|---|---|---:|
| 1 | PL-0 | khung gói, `engine.json`, `sql/`, `chay.py`, `ngan_chung.py`, `tests/kiem_doc_lap.py`, `tests/conftest.py`, schema `contract/` | PL-0 | vua | 3 |
| 1 | PL-0B | `tests/demo/sinh_demo.py`, `tests/demo/*.json`, `goi/e_phan_luong/demo/*` | PL-0 | vua | 1 |
| 1 | PL-1A | `tien.py`, `doc_lo.py` | PL-1 | vua | 2 |
| 1 | PL-1B | `nguong.py` | PL-1 | vua | 2 |
| 1 | PL-1C | `tu_khoa.py`, `phan_loai.py` | PL-1 | vua | 2 |
| 1 | PL-2A | `thong_ke.py`, `ty_le.py`, `doi_bac.py` | PL-2 (`doi_bac.py` → PL-3) | kho | 3 |
| 1 | PL-2B | `co.py`, `chon_mau.py` | PL-2 | vua | 2 |
| 1 | PL-3A | `ket_qua.py` | PL-3 | vua | 2 |
| 2 | PL-1 ghép | `phan_luong.py` (lớp 1 + phân loại) | PL-1 | vua | 1 |
| 3 | PL-2 ghép | `phan_luong.py` (lớp 2+3), `ngan_luot.py`, `xuat_json.py`, `chay.py` (năng lực `audit.phan_luong@1`) | PL-2 | kho | 2 |
| 3 | PL-3 ghép | `ngan_ket_qua.py`, `chay.py` (năng lực `audit.ghi_ket_qua@1`) | PL-3 | kho | 2 |
| 4 | PL-4A | `ho_so.py` (hồ sơ hành vi thuần) | PL-4 | vua | 2 |
| 4 | PL-4B | `chot_ky.py` (chốt kỳ tháng qua ngăn) | PL-4 | kho | 1 |
| 4 | PL-5A | `chuoi_ai.py` (lập `yeu_cau_ai`, đọc `tra_loi_ai`) | PL-5 | kho | 3 |
| 4 | PL-6A | `doc_bang.py` (Excel/CSV theo khuôn cột) | PL-6 | vua | 3 |
| 4 | PL-7A | `hoa_don.py` (đầu ra `e_hoa_don` → lô) | PL-7 | vua | 2 |
| 4 | PL-8A | `xuat_excel.py` (Excel danh sách Đỏ) | PL-8 | vua | 2 |
| 4 | PL-8B | `ui/bang_ty_le.js` (màn Admin chỉ đọc) | PL-8 | vua | 2 |
| 5 | PL-4…PL-8 ghép | nối vào `chay.py`, `phan_luong.py`, `engine.json` | từng PR | kho | 8 |
| 6 | PL-9 | mô phỏng 12 tháng, C4/C5, đo, đóng gói, danh mục | PL-9 | vua | 3 |
| | **Cộng** | | | | **48** |

Đợt 1 chạy song song (8 Codex). Đợt 2 sau khi PL-0 và PL-1A/1B/1C gộp. Đợt 3: PL-2 ghép và PL-3 ghép chạy song song (khác tệp; `chay.py` mỗi bên chỉ thêm hàm năng lực của mình, lead gộp).

## 2. Hợp đồng chung (mọi việc con phải theo)

### 2.1 Quy tắc làm việc song song
- Chỉ tạo/sửa **tệp sở hữu** của việc mình và test `e_phan_luong/tests/test_<việc>_*.py` (ví dụ `test_pl1a_doc_lo.py`). Không sửa `kieu.py`, `loi.py`, `VIEC.md`, `CHANGELOG.md`, `engine.json` (trừ PL-0 và việc ghép được giao). Lead cập nhật `VIEC.md`, `CHANGELOG.md` khi gộp.
- Việc con đợt 1 có thể chưa có `__init__.py`, `conftest.py`: đầu mỗi tệp test tự thêm đường dẫn gói:
  `sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"))` rồi `from e_phan_luong import <mô-đun>`.
- Mô-đun thuần (đợt 1, trừ PL-0) **không import SDK**, trừ `loi.py` (đã có) để ném lỗi. Không đọc tệp, không gọi mạng, không dùng ngăn. Chỉ thư viện chuẩn (+ `openpyxl` chỉ ở PL-6/PL-8).
- Tiền: `Decimal` + mã tiền tệ (`kieu.Tien`). Không `float` cho tiền. Không tự gán VND. Thiếu dữ liệu để so ngưỡng → Đỏ kèm lý do, không đoán.
- Lỗi: chỉ `raise loi("<MÃ>")` với mã trong `loi.CAU_LOI`. Chi tiết (dòng nào, trường nào) ghi `logging`, không đưa vào câu lỗi.
- Không đưa tỷ lệ, xác suất, bậc vào trường ra, `tep_json`, `tep_ds_do`, câu cảnh báo (C5).
- Chỉ dữ liệu DEMO ("Công ty DEMO Ánh Dương", mã `PC-DEMO-…`, `DEMO-NCC-…`).
- Báo cáo theo `AGENTS.md` §6. Việc con đợt 1 chỉ cần chạy `pytest` test của mình (ghi rõ); ba lệnh `AGENTS.md` §5 chạy ở bước lead ghép lát.

### 2.2 Bố cục gói
```
e_phan_luong/
├── goi/e_phan_luong/
│   ├── engine.json, README.md, CHANGELOG.md, NGUON.md, requirements.lock
│   ├── contract/yeu_cau_ai.schema.json, tra_loi_ai.schema.json   (chép nguyên từ _chung/contract/)
│   ├── sql/001_tao_ngan.sql, sql/kiem_ke.json
│   ├── ui/            (PL-8)
│   ├── demo/          (PL-0B)
│   └── e_phan_luong/  __init__.py, chay.py, kieu.py, loi.py, ngan_chung.py, … (bảng §1)
├── tests/             (ngoài gói)
└── docs/              PHIEU-ENGINE-…, GIAO-CODEX-… (tệp này), VIEC.md
```

### 2.3 Chữ ký hàm từng mô-đun (đợt 1)

`tien.py` (PL-1A)
- `doc_tien(gia_tri, *, cho_phep_null: bool = False) -> Tien | None` — nhận `{"so": "<chuỗi thập phân>" | int | Decimal, "tien_te": "VND" | null}`. `so` không nhận `float` (JSON đọc bằng `parse_float=Decimal`), không NaN/Inf, tối đa 18 chữ số phần nguyên và 6 chữ số lẻ. `tien_te` thiếu/null → `Tien(so, None)` (dòng sẽ Đỏ `CHUA_RO_TIEN_TE`); có thì phải khớp `^[A-Z]{3}$`. Sai → `loi("DU_LIEU_KHONG_HOP_LE")`.
- `tien_ra(t: Tien | None) -> dict | None` — `{"so": "<chuỗi>", "tien_te": ...}`, chuỗi dạng chuẩn hóa không mũ (`format(so, "f")`, bỏ số 0 thừa sau dấu phẩy).

`doc_lo.py` (PL-1A)
- `TOI_DA_BYTE = 20 * 1048576`, `TOI_DA_DONG = 50000`.
- `doc_lo_json(du_lieu: bytes) -> Lo` — UTF-8 (có/không BOM), `json.loads(parse_float=Decimal)`, từ chối khóa trùng trong đối tượng. Quá byte/dòng → `loi("VUOT_GIOI_HAN")`. Không phải JSON → `loi("TEP_KHONG_HO_TRO")`. Thiếu `ma_module` (≤ 31, `^[a-z][a-z0-9_]*$`), `ma` (1–120 ký tự, không ký tự điều khiển), `ngay` (`YYYY-MM-DD`), `so_tien`; `phien_ban` khác 1; mã trùng trong lô; `ky` sai `YYYY-MM`; kiểu sai (`nhap_tay`/`co_do_cung` phải bool, `thuoc_tinh` phải object chữ→chữ/số) → `loi("DU_LIEU_KHONG_HOP_LE")`.
- `noi_dung` của `NghiepVu` gồm `dien_giai`, `tai_khoan_no`, `tai_khoan_co` (nếu có) và `thuoc_tinh.<khóa>` (giá trị đổi ra chữ). `loai` giữ nguyên (chưa kiểm danh mục). `chi_so` theo thứ tự trong lô.

`nguong.py` (PL-1B)
- `doc_nguong(tu_tep: dict | None, tu_tham_so: str | None) -> Nguong` — khối trong tệp thắng `nguong_json` của Cài đặt bước; cả hai trống → `loi("THIEU_NGUONG")`. Mỗi ngưỡng là tiền có tiền tệ; ba ngưỡng cùng tiền tệ; `0 < SAD < TE <= PM`; sai → `loi("THIEU_NGUONG")`. `nguong_json` không phải JSON object → `loi("THAM_SO_KHONG_HOP_LE")`.
- `tien_so_sanh(nv: NghiepVu, ng: Nguong) -> tuple[Tien | None, str | None]` — `so_tien_quy_doi` cùng tiền tệ ngưỡng thì dùng; không thì `so_tien` nếu cùng tiền tệ; `so_tien.tien_te` None → `(None, CHUA_RO_TIEN_TE)`; khác tiền tệ không quy đổi → `(None, CHUA_QUY_DOI)`. **Số tiền âm: so theo giá trị tuyệt đối (Anh chốt Q3, 20/11)**, gói trong một hàm `_gia_tri_so(t)` duy nhất; chia nhỏ cộng theo giá trị tuyệt đối.
- `xet_lop1(nv, ng) -> tuple[str, tuple[str, ...]]` — trả `(vung, ly_do)`: `ly_do` gồm mọi mã bắt buộc áp dụng (`VUOT_PM` khi ≥ PM, `VUOT_TE` khi TE ≤ x < PM, `CHUA_QUY_DOI`, `CHUA_RO_TIEN_TE`, `CO_DO_CUNG`); có mã → `VUNG_BAT_BUOC`; không thì `VUNG_CHON_MAU` (SAD ≤ x < TE) hoặc `VUNG_DUOI_SAD`.
- `tim_chia_nho(ds: Sequence[NghiepVu], ng: Nguong, *, cua_so_ngay: int = 7, tong_truoc: Callable[[str, date], Decimal] | None = None, bam: Callable[[str], str]) -> frozenset[str]` — trả tập `ma` bị `NGHI_CHIA_NHO`. Chỉ xét dòng có đối tác, có tiền so sánh được và < TE. Theo từng đối tác (khóa = `bam(doi_tac)`), mọi cửa sổ `[d − cua_so_ngay + 1, d]`: tổng các khoản trong cửa sổ (+ `tong_truoc(bam, ngay)` cho các ngày trong cửa sổ nếu có — PL-4 cấp từ hồ sơ hành vi) ≥ TE → mọi dòng trong cửa sổ đó bị gắn. Khâu là một trong một lượt nên không cần gom theo khâu.

`tu_khoa.py`, `phan_loai.py` (PL-1C)
- `tu_khoa.py`: chép cách so từ khóa của `e_kiem_excel` (`e_kiem_excel/goi/e_kiem_excel/e_kiem_excel/bo_nhom.py`, phiếu e_kiem_excel §4.1.1): `chuan(chu) -> str` (NFC, bỏ dấu, `đ→d`, chữ thường, gộp khoảng trắng), điều kiện `tat_ca` (mọi mục khớp; mục là `["tu khoa"]` hoặc `["tu khoa", "=tu"]` khớp nguyên từ), `khong_co`, ký tự `#` = một hoặc nhiều chữ số. Không nhận biểu thức chính quy. Trần như e_kiem_excel (32 KiB, ≤ 200 từ khóa/quy tắc). Ghi nguồn chép trong docstring.
- `phan_loai.py`:
  - `doc_danh_muc_loai(chuoi: str | None) -> dict[str, dict]` — `[{"ma","ten","mo_ta"}]`, `ma` `^[a-z][a-z0-9_]{0,39}$`, ≤ 100 loại, không trùng, không chứa `chua_phan_loai`; trống → `{}`; sai → `loi("THAM_SO_KHONG_HOP_LE")`.
  - `doc_bo_phan_loai(chuoi: str | None, danh_muc) -> BoPhanLoai` — `{"phien_ban": 1, "quy_tac": [{"loai": "<mã trong danh mục>", "khi": [{"tat_ca": [...], "khong_co": [...]}]}]}`: một quy tắc khớp nếu **một** điều kiện trong `khi` khớp; xét theo thứ tự, khớp đầu tiên thì dừng. Không có `vung` (chỉ so một trường nội dung). Trống → bộ rỗng. Loại ngoài danh mục, sai cấu trúc → `loi("THAM_SO_KHONG_HOP_LE")`.
  - `lay_noi_dung(nv: NghiepVu, truong_phan_loai: str | None) -> str | None` — trường hợp lệ: `dien_giai`, `tai_khoan_no`, `tai_khoan_co`, `thuoc_tinh.<khóa>`; khác → `loi("THAM_SO_KHONG_HOP_LE")`.
  - `gan_loai(nv, danh_muc, bo, truong_phan_loai) -> tuple[str | None, str | None]` — (1) `nv.loai` có: phải trong danh mục (không thì `loi("DU_LIEU_KHONG_HOP_LE")`) → `(loai, NGUON_MODULE)`; (2) quy tắc khớp → `(loai, NGUON_QUY_TAC)`; (3) không có → `(None, None)` (bước sau: AI ở PL-5, hoặc `chua_phan_loai`).
  - `chot_loai(ket_qua) -> tuple[str, str]` — `(None, None)` → `(CHUA_PHAN_LOAI, NGUON_CHUA)`.

`thong_ke.py`, `ty_le.py`, `doi_bac.py` (PL-2A)
- `thong_ke.can_tren(so_loi: int, so_mau: int, do_tin_cay: Decimal = Decimal("0.95")) -> Decimal` — cận trên **một phía** Clopper-Pearson: `p` sao cho `P(X ≤ so_loi | so_mau, p) = 1 − do_tin_cay`. Thư viện chuẩn (`math.lgamma`/`math.comb`, chia đôi ≥ 60 vòng). `so_mau = 0` → 1. `so_loi = so_mau` → 1. Làm tròn **lên** 6 chữ số lẻ (thận trọng). Kiểm: `so_loi = 0` → `1 − 0,05^(1/n)` (n = 30 → 0,0950; 60 → 0,0487; 100 → 0,0295).
- `ty_le.ChinhSach` (dataclass frozen) mặc định = bộ Anh duyệt: `bac = (0.30, 0.20, 0.10, 0.05)`, `nguong_xuong = (0.10, 0.05, 0.03)`, `mau_toi_thieu = (30, 60, 100)`, `ty_le_chua_phan_loai = 0.30`, `mau_sach_toan_bo = 30`, `nguong_diem_rui_ro = 0.10`, `do_tin_cay = 0.95`, `he_so = {SO_TIEN_BAT_THUONG: 2, DOI_TAC_MOI: 2, SO_TRON: 1.5, NGAY_NGHI: 1.5, CUOI_KY: 1.5, NHAP_TAY: 1.5}`, `don_vi_so_tron = 10000000`, `ty_le_duoi_sad = 0.02`, `san = 0.05` (mọi số là `Decimal`). `doc_chinh_sach(chuoi: str | None, *, ty_le_duoi_sad: Decimal | None = None) -> ChinhSach` — trống → mặc định; JSON ghi đè từng khóa; kiểm `bac` giảm dần trong (0, 1], `len(nguong_xuong) = len(mau_toi_thieu) = len(bac) − 1`, hệ số ≥ 1, ≤ 8 KiB; sai → `loi("THAM_SO_KHONG_HOP_LE")`.
- `ty_le.TrangThai` (dataclass frozen) — đúng các cột bảng `ty_le` (§2.4): `khau, loai, bac, che_do, mau_tu_doi_bac, loi_tu_doi_bac, mau_sach_toan_bo, mau_12t, loi_12t, loi_sad_12t, loi_ngoai_mau_12t, diem, nhan (frozenset), doi_bac_luc`. `moi(khau, loai, cs)` (bậc đầu `cs.bac[0]`, chế độ `bac`), `tu_ban_ghi(dict)`, `ve_ban_ghi(tt) -> dict` (số → chuỗi thập phân, `nhan` → chữ nối dấu phẩy theo thứ tự chữ cái).
- `ty_le.p_bac(tt, cs) -> Decimal` — `che_do = toan_bo` → 1; `loai = chua_phan_loai` → `cs.ty_le_chua_phan_loai` (cố định); còn lại → `tt.bac`.
- `doi_bac.MotKetQua(nguon_mau, ket_qua, muc_sai)`; `doi_bac.cap_nhat(tt, kq, cs, *, luc: str) -> tuple[TrangThai, bool]` (bool = có đổi bậc/chế độ). Luật (phiếu §4.3; chỗ in nghiêng là diễn giải của lead, báo Anh ở PL-3):
  1. `khong_kiem` → không đổi gì.
  2. Đếm: `nguon_mau = chon_mau` → `mau_tu_doi_bac += 1`, `mau_12t += 1`, nếu sai thêm `loi_tu_doi_bac`, `loi_12t`. Sai với `muc_sai ∈ {sad, te}` (mọi nguồn) → `loi_sad_12t += 1`. Sai và `nguon_mau = ngoai_mau` → `loi_ngoai_mau_12t += 1`.
  3. Sai (mọi nguồn), áp **mức nặng nhất**: `te` → chế độ `toan_bo`, `mau_sach_toan_bo = 0`; `sad` hoặc `ngoai_mau` → bậc `bac[0]` (chế độ `bac`); `nho` → lên một bậc (đã ở `bac[0]` thì giữ). **Đang `toan_bo` (Anh chốt Q6, 20/11): chỉ lỗi `te` mới đưa `mau_sach_toan_bo` về 0; lỗi `nho`/`sad`/ngoài mẫu giữ `toan_bo`, không xóa bộ đếm, không cộng mẫu sạch.** Mọi lần đổi bậc/chế độ: `mau_tu_doi_bac = loi_tu_doi_bac = 0`, `doi_bac_luc = luc`.
  4. Đạt: chế độ `toan_bo` → `mau_sach_toan_bo += 1`; đủ `cs.mau_sach_toan_bo` → chế độ `bac`, bậc `bac[0]`. Chế độ `bac` và `nguon_mau = chon_mau` → xét xuống: chỉ số bậc `i` chưa ở sàn, `mau_tu_doi_bac ≥ mau_toi_thieu[i]` **và** `can_tren(loi_tu_doi_bac, mau_tu_doi_bac) ≤ nguong_xuong[i]` → xuống bậc `i + 1`.
  5. *`chua_phan_loai`: không bao giờ đổi bậc hay vào `toan_bo` (30% cố định); vẫn đếm và gắn nhãn.*
  6. Sau mỗi lần cập nhật: `diem = can_tren(loi_12t, mau_12t)` (None khi `mau_12t = 0`); nhãn `rui_ro_cao` khi `diem > nguong_diem_rui_ro` hoặc `loi_sad_12t > 0`; nhãn `loi_ngoai_mau` khi `loi_ngoai_mau_12t > 0`. (PL-4 chốt kỳ tính lại số 12 tháng.)

`co.py`, `chon_mau.py` (PL-2B)
- `co.HoSoLoai(so_nghiep_vu: int, phan_vi_95: Decimal | None, bam_doi_tac: frozenset[str])` — ảnh chụp hồ sơ (khâu, loại). PL-4 cấp; PL-2 truyền `None`.
- `co.tinh_co(nv, tien_ss: Tien | None, ho_so: HoSoLoai | None, bam_dt: str | None, cs) -> tuple[str, ...]` theo `THU_TU_CO`: `SO_TIEN_BAT_THUONG` khi `ho_so` có, `so_nghiep_vu ≥ 50`, `phan_vi_95` có và `tien_ss.so > phan_vi_95`; `DOI_TAC_MOI` khi `ho_so` có, `bam_dt` có và không thuộc `ho_so.bam_doi_tac`; `SO_TRON` khi `tien_ss` có, `> 0` và chia hết `cs.don_vi_so_tron`; `NGAY_NGHI` khi thứ 7/chủ nhật; `CUOI_KY` khi `ngay` thuộc 3 ngày cuối tháng; `NHAP_TAY` khi `nv.nhap_tay`. `ho_so = None` → không xét hai cờ đầu.
- `co.tich_he_so(co, cs) -> Decimal`.
- `chon_mau.sinh_hat_giong() -> bytes` (`secrets.token_bytes(32)`); `chon_mau.bam_hat_giong(hg) -> str` (`"sha256:" + hex`).
- `chon_mau.gia_tri_bam(hg, ma_module, khau, ma) -> int` = `int.from_bytes(sha256(hg + b"\x1f" + ma_module + b"\x1f" + khau + b"\x1f" + ma), "big")` (chuỗi mã hóa UTF-8). Ghi công thức này vào docstring để kiểm toán viên chạy lại.
- `chon_mau.duoc_chon(hg, ma_module, khau, ma, p: Decimal) -> bool` — so chính xác bằng số nguyên/`Fraction`: `gia_tri_bam < p × 2^256` (không qua float).
- `chon_mau.tinh_p(p_co_so: Decimal, he_so: Decimal, san: Decimal) -> Decimal` = `min(1, max(san, p_co_so × he_so))`. Vùng dưới SAD: `p_co_so = cs.ty_le_duoi_sad`, `san = 0`, **có nhân hệ số cờ (Anh chốt Q4, 20/11)**: `p = min(1, ty_le_duoi_sad × tích hệ số)`.

`ket_qua.py` (PL-3A)
- `doc_ket_qua_json(du_lieu: bytes) -> KetQuaTep` — §5.3, thêm khối tùy chọn `"nguong"` cùng dạng §5.1 (**Anh chốt Q1, 20/11: module gửi kèm ngưỡng** trong tệp; không có thì dùng `nguong_json` của Cài đặt bước ghi kết quả; thiếu cả hai mà có dòng `sai` → `THIEU_NGUONG`). `KetQuaTep(ma_module, nguong: dict | None, dong: tuple[DongKetQua, ...], so_trung_trong_tep: int)`; `DongKetQua(chi_so, ma_luot, ma, khau, ket_qua, so_tien_sai: Tien | None, loai_dung: str | None)`. Trần 20 MiB/50.000 dòng (`VUOT_GIOI_HAN`); `ket_qua ∈ {dat, sai, khong_kiem}`; `sai` bắt buộc `so_tien_sai` có tiền tệ; trùng (ma_luot, ma, khau) **trong tệp** → chỉ giữ dòng đầu, đếm trùng. Sai → `loi("DU_LIEU_KHONG_HOP_LE")`.
- `muc_sai(so_tien_sai: Tien, ng: Nguong) -> str` — theo giá trị tuyệt đối (Q3): `< SAD` → `nho`; `SAD ≤ x < TE` → `sad`; `≥ TE` → `te`. **Khác tiền tệ ngưỡng → `loi("DU_LIEU_KHONG_HOP_LE")` (Anh chốt 20/11: từ chối, module gửi số đã quy đổi; không đoán).**
- `nguon_mau(ly_do: str | None) -> str` — chuỗi cột `dong_luot.ly_do`: có `CHON_MAU` → `chon_mau`; có mã bắt buộc → `bat_buoc`; `KHONG_CHON` hoặc `None` (mã không thuộc lượt) → `ngoai_mau`.

### 2.4 Ngăn dữ liệu (`ngan_du_lieu`, đều `pham_vi: "phap_nhan"`, khóa không chứa `phap_nhan_id`)

Cột hệ thống theo mẫu `e_demo_ngan` (`id, phap_nhan_id, row_version, tao_luc, sua_luc, het_han_luc, viec_id`) — **không khai lại** `tao_luc` trong `truong`. Không cột `json`/`jsonb` (bộ duyệt SQL cấm): dữ liệu gộp kiểu JSON lưu `text`, khai `van_ban`. Số đếm, tỷ lệ: `numeric`, khai `so`. **Không cột số tiền, ngày giao dịch, đối tác, nội dung** (C4).

| Bảng | Khóa | Trường (kiểu) | `giu_toi_da_ngay` |
|---|---|---|---|
| `luot` | `ma_luot` | `ma_luot` (van_ban), `ma_module` (van_ban), `khau` (van_ban), `hat_giong` (van_ban, 64 hex), `bam_dau_vao` (van_ban) | 400 |
| `dong_luot` | `ma_luot`, `ma` | `ma_luot`, `ma`, `ma_module`, `khau`, `ly_do`, `loai`, `nguon_loai` (đều van_ban) — **2 cột cuối Anh chốt Q2, 20/11** (mã danh mục, không phải chi tiết giao dịch) | 400 |
| `ket_qua_kiem` | `ma_luot`, `ma`, `khau` | `ma_luot`, `ma`, `khau`, `ma_module`, `loai`, `ket_qua`, `muc_sai`, `nguon_mau`, `nguon_loai_sai` (đều van_ban) | 365 |
| `ty_le` | `khau`, `loai` | `khau`, `loai`, `bac` (so), `che_do` (van_ban), `mau_tu_doi_bac`, `loi_tu_doi_bac`, `mau_sach_toan_bo`, `mau_12t`, `loi_12t`, `loi_sad_12t`, `loi_ngoai_mau_12t` (so), `diem` (so), `nhan` (van_ban), `doi_bac_luc` (thoi_diem) | không |
| `ho_so_hanh_vi` | `khau`, `loai` | `khau`, `loai`, `so_nghiep_vu` (so), `bieu_do` (van_ban, JSON), `bam_doi_tac` (van_ban, JSON), `tong_7_ngay` (van_ban, JSON), `ky_lam_moi` (van_ban) | không |
| `chot_ky` | `ky`, `khau`, `loai` | `ky`, `khau`, `loai` + mọi cột số liệu của `ty_le` (bản chụp) | không |

`duy_nhat` mỗi bảng = `[["phap_nhan_id", <các cột khóa>]]`. Băm đối tác dùng một công thức duy nhất `bam_doi_tac(ma_module, doi_tac) = sha256("e_phan_luong|doi_tac|" + ma_module + "|" + doi_tac)`, lấy 32 ký tự hex đầu (PL-1 ghép đặt trong `phan_luong.py`; mô-đun thuần nhận hàm băm qua tham số).

### 2.5 Chuyển tiếp tệp giữa các bước (PL-5, PL-7 — đã kiểm Core thật bằng đọc mã, §4)
- `chuyen_tiep` của `yeu_cau_ai` mang **nguyên đối tượng tệp** do `viec.tai_tep_ra` trả: `{"phan_luong": {"phien_ban": 1, "tep_lo": {"tep_id", "ten", "mime", "kich_thuoc"}, "bam_tep": "sha256:…", "khau": "…", "khong_can_ai": false}}` (≤ 4 KiB). Core thật chỉ cho `mo_tep` khi đầu vào bước có **đối tượng có khóa `tep_id`** và tệp cùng việc; chuỗi trơn bị từ chối dù CoreGia cho qua. Test phải kiểm đúng hình dạng này.

## 3. Lệnh giao Codex từng việc (dán nguyên khối)

### PL-0 — Khung gói, engine.json, SQL ngăn, kiểm kê
```
Đọc AGENTS.md; e_phan_luong/docs/PHIEU-ENGINE-e_phan_luong.md (đủ); e_phan_luong/docs/GIAO-CODEX-e_phan_luong.md §1–§2 và §4; docs/goi-gui-engine/API-ENGINE-v1.md; docs/goi-gui-engine/sdk-2.2.0/MAU-PHIEU-ENGINE.md, THAY-DOI-2.2.0.md, engine-demo/e_demo_ngan/ (đủ); _chung/docs/CHUYEN-SDK-2.2.md; _chung/docs/LOAI-DU-LIEU-RIENG.md §2.2–2.3.
Mẫu: e_kiem_excel/goi/e_kiem_excel/ (engine.json, chay.py lớp bọc, requirements.lock, NGUON.md), e_kiem_excel/tests/ (kiem_doc_lap.py, conftest.py, kiem_bam_goi.py), e_trich_xuat/goi/e_trich_xuat/engine.json (khai yeu_cau_ai/tra_loi_ai).
Làm lát PL-0 cho e_phan_luong. kieu.py và loi.py đã có trong gói (lead giữ): KHÔNG sửa.
1. Tạo e_phan_luong/goi/e_phan_luong/ theo GIAO-CODEX §2.2: __init__.py (__version__ = "0.1.0"), README.md (tiếng Việt: engine làm gì, 5 năng lực, công thức chọn mẫu để kiểm toán viên chạy lại), CHANGELOG.md, NGUON.md, requirements.lock (ghim openpyxl, et_xmlfile, defusedxml CÙNG phiên bản và hash với e_kiem_excel/goi/e_kiem_excel/requirements.lock).
2. engine.json 2.0, tuong_thich.sdk ">=2.2.0 <3.0.0": đủ 5 năng lực phiếu §1 với nhan/tra, truong_ra §5.5 (ghi_ket_qua: các trường cuối §5.5), tham_so phiếu §6 (đúng toi_da, mặc định; khau bắt buộc ≤ 40; model_uu_tien chỉ ở chuan_bi_phan_loai; loai_nghiep_vu chỉ ở phan_luong_hoa_don), gioi_han (tep_toi_da_mib 20; thoi_han_giay tạm 300), huy_duoc true; loai_du_lieu_rieng yeu_cau_ai, tra_loi_ai khai GIỐNG HỆT LOAI-DU-LIEU-RIENG.md, schema chép nguyên từ _chung/contract/ vào goi/e_phan_luong/contract/; ngan_du_lieu đúng bảng GIAO-CODEX §2.4; du_lieu.goi_migration (phien_ban_du_lieu 1); tai_nguyen.so_viec_dong_thoi 1. Không khai giao_dien_quan_tri (PL-8 thêm). chay_thu_demo: CHỈ khai ví dụ của năng lực đã làm thật (PL-0 chưa có năng lực nào chạy được). Nếu SDK bắt buộc ≥ 1 ví dụ hoặc mọi năng lực phải có hàm thật thì DỪNG phần đó, ghi rõ trong báo cáo, KHÔNG làm thành công giả.
3. sql/001_tao_ngan.sql: 6 bảng trong schema eng_e_phan_luong đúng mẫu e_demo_ngan (cột hệ thống, UNIQUE theo duy_nhat, COMMENT tiếng Việt từng bảng/cột, dòng "kieu: so" ở cột numeric như mẫu), không json/jsonb, không cột tiền/ngày giao dịch/đối tác/nội dung. sql/kiem_ke.json đúng định dạng mẫu (bytes + SHA-256 mọi tệp gói trừ chính nó) và tests/kiem_bam_goi.py để tính lại; tests/test_pl0_goi.py so kiểm kê với tệp thật.
4. chay.py: app = Engine.tu_khai_bao("engine.json") (bọc lỗi như e_kiem_excel, không lộ traceback); hàm năng lực tạm raise LoiNghiepVu("CHUA_LAM", "Năng lực đang được xây dựng.") cho cả 5 năng lực.
5. ngan_chung.py: (a) ghi_lo_thu_lai(viec, lap_lenh, *, so_lan_thu_lai=3) — gọi lap_lenh(lo) bên trong `with viec.ngan.lo() as lo`, NganXungDot thì gọi lại lap_lenh (lap_lenh tự đọc lại dữ liệu), quá 3 lần thử lại → raise loi("NGAN_BAN"); trả số lần đã thử lại. (b) ghi_lay_hoac_tao_nhieu(viec, bang, ds: list[tuple[khoa, gia_tri]]) — chia lô ≤ 100 lệnh lay_hoac_tao. (c) tim_tat_ca(viec, bang, loc, *, gioi_han=500, toi_da=200000) — duyệt hết trang `tiep`. Test bằng CoreGia (gay_xung_dot_ngan, xem_ngan).
6. tests/conftest.py, tests/kiem_doc_lap.py (không import kho_tri_thuc.*, không __pycache__/.pyc/symlink trong goi/, không mạng/socket/subprocess/sqlite/psycopg trong gói, không từ "VND" gán mặc định trong mã gói — kiểm bằng grep có danh sách ngoại lệ là chuỗi trong test/README).
7. test_pl0_*.py: phiếu đọc được (doc_phieu), schema loại riêng trùng băm _chung/contract/, SQL không json/jsonb và không cột cấm (C4), kiểm kê khớp, ngan_chung đúng (đúng một lần thử lại khi gay_xung_dot_ngan(so_lan=1); NGAN_BAN sau 4 lần xung đột), C5: truong_ra không có mã chứa "ty_le"/"xac_suat"/"bac".
8. Hai điểm "Cần Core" (GIAO-CODEX §4): viết tests/test_pl0_can_core.py bằng CoreGia — (a) bước 1 tai_tep_ra rồi bước sau mo_tep tep_id nằm trong đối tượng {"tep_id",...} lồng trong chuyen_tiep của phong bì tra_loi_ai: mở được; (b) ghi chú rằng CoreGia lỏng hơn Core thật (so chuỗi con) — test kèm hàm kiểm hình dạng nghiêm như Core thật (jsonpath $.** ? (@.tep_id == id)) để PL-5 dùng lại.
Đạt: 3 lệnh AGENTS.md §5 (thu: nếu không có ví dụ nào thì ghi kết quả thật, không bịa [ĐẠT]); pytest 0 lỗi; kiem_doc_lap mã 0. Không sửa kieu.py, loi.py. VIEC.md chỉ sửa dòng PL-0 và mục "Cần Core". Tệp tests/demo/* và goi/e_phan_luong/demo/* do PL-0B làm song song: không tạo.
```

### PL-0B — Bộ DEMO và AI giả
```
Đọc AGENTS.md; e_phan_luong/docs/PHIEU-ENGINE-e_phan_luong.md §4–§5, §8; GIAO-CODEX-e_phan_luong.md §2; _chung/docs/LOAI-DU-LIEU-RIENG.md §2.2–2.3 và _chung/contract/tra_loi_ai.schema.json, yeu_cau_ai.schema.json.
Làm việc PL-0B cho e_phan_luong. Chỉ tạo tệp: e_phan_luong/tests/demo/sinh_demo.py, e_phan_luong/tests/demo/*.json, e_phan_luong/goi/e_phan_luong/demo/*, e_phan_luong/tests/test_pl0b_demo.py.
1. sinh_demo.py (thư viện chuẩn, hạt giống cố định, chạy lại ra cùng byte): "Công ty DEMO Ánh Dương", ma_module demo_thanh_toan, kỳ 2026-11, ngưỡng DEMO PM 5.000.000.000 / TE 3.000.000.000 / SAD 250.000.000 VND; 3 khâu kt_kiem, ktt_duyet, cfo_duyet; 5 loại thanh_toan_ncc, tam_ung, luong, chi_phi_khac, thu_tien (+ dòng không khớp quy tắc → chua_phan_loai); 500 nghiệp vụ, ngày tháng 10–11/2026. Cài sẵn và ghi đáp án: vượt TE, vượt PM, chia nhỏ (≥ 3 khoản cùng đối tác trong 7 ngày, từng khoản < TE, tổng ≥ TE), đối tác mới, số tròn 10.000.000, ngày nghỉ, cuối kỳ, nhập tay, cờ đỏ cứng, khác tiền tệ USD chưa quy đổi, USD có quy đổi VND, thiếu tiền tệ, loại module đã gán, dòng chỉ quy tắc phân loại được, dòng không khớp.
2. Ghi ra: tests/demo/lo-500-DEMO.json (§5.1), tests/demo/dap-an-lop1.json (theo mã: ly_do lớp 1 kỳ vọng, loại kỳ vọng + nguồn), tests/demo/danh-muc-loai-DEMO.json, tests/demo/bo-phan-loai-DEMO.json (định dạng GIAO-CODEX §2.3 phan_loai), tests/demo/nguong-DEMO.json, tests/demo/ket-qua-kiem-mau-DEMO.json (§5.3, ma_luot giả "PL-DEMO-…"), lô nhỏ goi/e_phan_luong/demo/lo-nho-DEMO.json (≈ 20 dòng, đủ các ca trên) cho chay_thu_demo.
3. AI giả: tests/demo/tra-loi-ai-*.json — phong bì tra_loi_ai dựng tay, đúng schema _chung/contract/tra_loi_ai.schema.json, nha_cung_cap "local": (a) đúng enum, (b) sai enum, (c) tin_cay thấp 0,4, (d) nha_cung_cap "cloud", (e) khong_thay_can_cu; khuôn trả lời {"phan_loai":[{"chi_so":int,"loai":enum,"tin_cay":0..1}]}; chuyen_tiep theo GIAO-CODEX §2.5 (tep_id giả "tep-DEMO-…").
4. test_pl0b_demo.py: sinh lại cho cùng byte (so SHA với tests/demo/bam-demo.json), mọi tệp JSON đọc được, phong bì AI hợp schema (jsonschema nếu có trong venv, không thì kiểm khóa bắt buộc bằng tay), không có chữ "thật"/MST thật/số tài khoản thật, mọi tên có nhãn DEMO.
Không sửa tệp khác. Chạy pytest test_pl0b_demo.py.
```

### PL-1A — Tiền và đọc JSON lô
```
Đọc AGENTS.md; PHIEU-ENGINE-e_phan_luong.md §5.1, §5.5, §7; GIAO-CODEX-e_phan_luong.md §2 (đủ); e_phan_luong/goi/e_phan_luong/e_phan_luong/kieu.py, loi.py (không sửa); quy ước tiền e_kiem_excel/docs/PHIEU-ENGINE-e_kiem_excel.md §4.3.
Làm việc PL-1A: viết tien.py và doc_lo.py đúng chữ ký GIAO-CODEX §2.3, cùng e_phan_luong/tests/test_pl1a_tien.py, test_pl1a_doc_lo.py. Chỉ thư viện chuẩn + loi.py.
Test (chỉ dữ liệu DEMO dựng trong test): số ≥ 10^12, số lẻ 6 chữ số, số âm, "1e3"/NaN/float bị từ chối, tiền tệ thường "vnd" bị từ chối, thiếu tiền tệ → Tien(so, None) không gán VND; BOM; khóa trùng; mã trùng; thiếu từng trường bắt buộc; ngày sai; vượt 50.000 dòng và vượt 20 MiB (dựng bytes) → VUOT_GIOI_HAN; không phải JSON → TEP_KHONG_HO_TRO; câu lỗi đúng loi.CAU_LOI và không chứa dữ liệu nghiệp vụ; noi_dung lấy đủ dien_giai/tai_khoan/thuoc_tinh.<khóa>.
Không tạo __init__.py, conftest.py; không sửa tệp ngoài danh sách. Chạy pytest hai tệp test của mình.
```

### PL-1B — Ngưỡng PM/TE/SAD, lớp 1, chia nhỏ trong lô
```
Đọc AGENTS.md; PHIEU-ENGINE-e_phan_luong.md §4.1, §5.1, §7; GIAO-CODEX-e_phan_luong.md §2 (đủ); kieu.py, loi.py (không sửa).
Làm việc PL-1B: viết nguong.py đúng chữ ký GIAO-CODEX §2.3 và e_phan_luong/tests/test_pl1b_nguong.py. Chỉ thư viện chuẩn + kieu.py + loi.py (dựng Tien/NghiepVu trực tiếp trong test, không phụ thuộc tien.py/doc_lo.py đang viết song song; muốn đọc khối ngưỡng thì tự kiểm {"so","tien_te"} trong nguong.py).
Test: tệp thắng tham số; thiếu cả hai → THIEU_NGUONG; SAD ≥ TE, TE > PM, khác tiền tệ, ngưỡng âm/0 → THIEU_NGUONG; nguong_json không phải object → THAM_SO_KHONG_HOP_LE; biên đúng (x = SAD → chon_mau; x = TE → VUOT_TE; x = PM → VUOT_PM); quy đổi đúng tiền tệ được dùng; khác tiền tệ không quy đổi → CHUA_QUY_DOI; thiếu tiền tệ → CHUA_RO_TIEN_TE; co_do_cung cộng dồn với lý do khác; chia nhỏ: 3 khoản 1,1 tỷ cùng đối tác trong 7 ngày (TE 3 tỷ) → cả 3 bị gắn; cùng khoản nhưng cách 8 ngày → không; khác đối tác → không; đối tác None → không; tong_truoc giả cộng thêm → bị gắn; không lẫn tiền tệ khi cộng.
Không tạo __init__.py, conftest.py. Chạy pytest test của mình.
```

### PL-1C — Từ khóa và phân loại (module, quy tắc, chưa phân loại)
```
Đọc AGENTS.md; PHIEU-ENGINE-e_phan_luong.md §4.2, §6; GIAO-CODEX-e_phan_luong.md §2 (đủ); e_kiem_excel/docs/PHIEU-ENGINE-e_kiem_excel.md §4.1.1 và e_kiem_excel/goi/e_kiem_excel/e_kiem_excel/bo_nhom.py, chuan_hoa.py; kieu.py, loi.py (không sửa).
Làm việc PL-1C: viết tu_khoa.py (chép-sửa phần so từ khóa của bo_nhom.py/chuan_hoa.py, ghi nguồn và dòng gốc trong docstring; KHÔNG import từ e_kiem_excel) và phan_loai.py đúng chữ ký GIAO-CODEX §2.3; tests e_phan_luong/tests/test_pl1c_tu_khoa.py, test_pl1c_phan_loai.py.
Test: bỏ dấu tiếng Việt (Đ/đ, tổ hợp NFD), "=tu" nguyên từ, "#" chữ số, khong_co, quy tắc đầu tiên thắng, regex trong từ khóa bị coi là chữ thường; danh mục: trùng mã, quá 100, chứa chua_phan_loai, mã sai dạng → THAM_SO_KHONG_HOP_LE; module gán loại ngoài danh mục → DU_LIEU_KHONG_HOP_LE; truong_phan_loai thuoc_tinh.<khóa>; không khớp → (None, None) → chot_loai → (chua_phan_loai, chua_phan_loai); trần 32 KiB.
Không tạo __init__.py, conftest.py. Chạy pytest test của mình.
```

### PL-2A — Clopper-Pearson, bảng tỷ lệ, luật đổi bậc
```
Đọc AGENTS.md; PHIEU-ENGINE-e_phan_luong.md §4.3, §4.4, §6, §8 (mô phỏng 12 tháng); GIAO-CODEX-e_phan_luong.md §2 (đủ, nhất là §2.3 thong_ke/ty_le/doi_bac và §2.4 bảng ty_le); kieu.py, loi.py (không sửa).
Làm việc PL-2A: viết thong_ke.py, ty_le.py, doi_bac.py đúng chữ ký và luật GIAO-CODEX §2.3; tests e_phan_luong/tests/test_pl2a_thong_ke.py, test_pl2a_ty_le.py, test_pl2a_doi_bac.py. Chỉ thư viện chuẩn, mọi tỷ lệ trả Decimal.
Test thong_ke: 0 lỗi n = 29/30/59/60/99/100 so công thức 1 − 0,05^(1/n) (sai ≤ 1e-6, làm tròn lên); 1–5 lỗi so bảng tra tính bằng phương pháp độc lập trong test (cộng dồn nhị thức bằng Fraction, chia đôi); n = 0; so_loi = so_mau; đơn điệu theo so_loi và so_mau; n = 100.000 chạy < 0,1 giây.
Test ty_le: mặc định đúng bộ Anh duyệt; chinh_sach_json ghi đè, sai cấu trúc/bậc tăng/hệ số < 1/quá 8 KiB → THAM_SO_KHONG_HOP_LE; ve_ban_ghi/tu_ban_ghi khứ hồi; p_bac đúng 3 trường hợp.
Test doi_bac: loại sạch xuống 30→20 đúng mẫu thứ 30, 20→10 đúng mẫu thứ 60 sau đó, 10→5 đúng mẫu thứ 100 sau đó, không xuống dưới 5%; lỗi nhỏ lên 1 bậc; lỗi ≥ SAD về 30% + rui_ro_cao; lỗi ≥ TE → toan_bo, 30 mẫu sạch về 30%; lỗi ngoài mẫu → 30% + loi_ngoai_mau; mẫu bắt buộc không đếm vào ước lượng; khong_kiem không đổi; chua_phan_loai luôn 30%; mô phỏng 12 tháng (hạt giống cố định): loại lỗi 8% không xuống dưới 30% và có rui_ro_cao.
Không tạo __init__.py, conftest.py. Chạy pytest test của mình.
```

### PL-2B — Cờ, hệ số, chọn mẫu bằng SHA-256
```
Đọc AGENTS.md; PHIEU-ENGINE-e_phan_luong.md §4.4, §8; GIAO-CODEX-e_phan_luong.md §2 (đủ, nhất là §2.3 co/chon_mau); kieu.py, loi.py (không sửa).
Làm việc PL-2B: viết co.py, chon_mau.py đúng chữ ký GIAO-CODEX §2.3; tests e_phan_luong/tests/test_pl2b_co.py, test_pl2b_chon_mau.py. Chỉ thư viện chuẩn. ChinhSach do PL-2A viết song song: trong co.py chỉ dùng thuộc tính cs.he_so (dict mã cờ → Decimal) và cs.don_vi_so_tron; trong test dùng types.SimpleNamespace thay ChinhSach.
Test co: từng cờ đúng/sai biên (thứ 7, chủ nhật, thứ 6; 3 ngày cuối tháng 2/2028 nhuận và tháng 30 ngày; 10.000.000 chia hết, 15.000.000 không; ho_so None không bật 2 cờ đầu; < 50 nghiệp vụ không bật SO_TIEN_BAT_THUONG); tích hệ số nhiều cờ.
Test chon_mau: tái hiện (cùng hạt giống + đầu vào → cùng kết quả từng byte qua 2 lần chạy và 2 tiến trình); đổi 1 bit hạt giống đổi kết quả; tần suất 10.000 dòng p = 0,20 → 19–21%; p = 1 chọn hết, p = 0 không chọn; so chính xác ở biên (dựng hạt giống để gia_tri_bam sát p × 2^256); tinh_p kẹp [san, 1]; không có float trong đường so.
Không tạo __init__.py, conftest.py. Chạy pytest test của mình.
```

### PL-3A — Đọc JSON kết quả kiểm, mức sai, nguồn mẫu
```
Đọc AGENTS.md; PHIEU-ENGINE-e_phan_luong.md §4.3, §5.3, §6, §7; GIAO-CODEX-e_phan_luong.md §2 (đủ, nhất là §2.3 ket_qua); kieu.py, loi.py (không sửa).
Làm việc PL-3A: viết ket_qua.py đúng chữ ký GIAO-CODEX §2.3 và e_phan_luong/tests/test_pl3a_ket_qua.py. Chỉ thư viện chuẩn + kieu.py + loi.py (tự đọc {"so","tien_te"}, không phụ thuộc tien.py đang viết song song; dùng Decimal, parse_float=Decimal).
Test: đủ ca §5.3; ket_qua lạ; sai thiếu so_tien_sai; so_tien_sai thiếu tiền tệ; trùng trong tệp chỉ giữ dòng đầu và đếm; vượt trần; muc_sai biên SAD/TE; nguon_mau đủ 4 trường hợp; câu lỗi đúng loi.CAU_LOI.
Không tạo __init__.py, conftest.py. Chạy pytest test của mình.
```

### PL-1 — ghép: lớp 1 + phân loại
```
Đọc AGENTS.md; PHIEU §4.1–§4.2; GIAO-CODEX §2. Nhánh này đã có PL-0, PL-1A, PL-1B, PL-1C.
Viết phan_luong.py: bam_doi_tac (GIAO-CODEX §2.4); QuyetDinhLop1 (dataclass frozen: nv, loai, nguon_loai, tien_ss, bat_buoc: tuple[str,...], vung); xet_lop1_lo(lo, tham_so, *, nguong, danh_muc, bo, truong_phan_loai, tong_truoc=None) → tuple[QuyetDinhLop1, ...]: phân loại (gan_loai → chot_loai), xet_lop1, tim_chia_nho (cua_so_chia_nho_ngay), gộp NGHI_CHIA_NHO vào bat_buoc. Chưa nối năng lực (PL-2 nối).
Test e_phan_luong/tests/test_pl1_phan_luong.py trên tests/demo/lo-500-DEMO.json: ly_do lớp 1, loại và nguồn loại khớp tests/demo/dap-an-lop1.json từng mã; lô chỉ có tiền tệ khác → mọi dòng Đỏ CHUA_QUY_DOI; không đoán.
Đạt: 3 lệnh AGENTS.md §5.
```

### PL-2 — ghép: lớp 2 + 3, năng lực `audit.phan_luong@1`, ngăn lượt
```
Đọc AGENTS.md; PHIEU §3, §4, §5.1, §5.5, §6, §8; GIAO-CODEX §2. Nhánh này đã có PL-0…PL-1, PL-2A, PL-2B.
1. ngan_luot.py: doc_ty_le(viec, khau, loai, cs) → TrangThai (chưa có → ty_le.moi, không ghi); tra_nop_lai(viec, ma_module, khau, ds_ma) → tập ma có lần trước gần nhất là Đỏ (tìm dong_luot theo {ma_module, khau, ma}; chỉ tính dòng có luot tồn tại; lần gần nhất theo tao_luc của luot) — **Anh chốt Q5 (20/11): lần gần nhất Đỏ mà CHƯA có ket_qua_kiem (dat/sai) cho (ma_luot, ma, khau) → NOP_LAI; đã có kết quả kiểm → xét bình thường với hạt giống mới; lần gần nhất Xanh → bình thường**; ghi_luot(viec, luot, ds_dong) — dong_luot trước (lay_hoac_tao, lô ≤ 100), luot SAU CÙNG (dấu hoàn tất).
2. phan_luong.py thêm lớp 2 + 3: p theo GIAO-CODEX §2.3 (p_bac, he_so từ co.tinh_co với ho_so=None, tinh_p; vùng dưới SAD = ty_le_duoi_sad × tích hệ số, Q4), duoc_chon; NOP_LAI; ra KetQuaDong cho mọi dòng; dong_luot ghi cả loai, nguon_loai (Q2).
3. xuat_json.py: tep_json (mỗi dòng: ma, luong, ly_do, co, loai, nguon_loai — KHÔNG tỷ lệ/xác suất/bậc; kèm ma_luot, bam_hat_giong, bam_dau_vao, phien_ban_engine, khau, ma_module), canh_bao ≤ 500 ký tự chỉ lý do; tep_ds_do tạm null nếu SDK cho trường tệp rỗng (PL-8 làm Excel), không thì ghi rõ.
4. chay.py: năng lực audit.phan_luong@1 (mo_tep JSON; Excel/CSV → TEP_KHONG_HO_TRO tới PL-6) trả đủ truong_ra §5.5; chay_thu_demo với goi/e_phan_luong/demo/lo-nho-DEMO.json.
Test: tái hiện từng byte với hạt giống cố định (mock sinh_hat_giong); xem_ngan mọi bảng không có số tiền/ngày giao dịch/đối tác/nội dung (C4); trường ra và tep_json không có tỷ lệ/xác suất/bậc (C5); nộp lại; lô 500 DEMO qua CoreGia; luot ghi sau cùng.
Đạt: 3 lệnh AGENTS.md §5; chạy _chung/cong-cu/sinh_danh_muc_engine.py (thêm GHI_CHU e_phan_luong).
```

### PL-3 — ghép: năng lực `audit.ghi_ket_qua@1`
```
Đọc AGENTS.md; PHIEU §4.3, §4.5, §5.3, §6, §7, §8; GIAO-CODEX §2. Nhánh này đã có PL-0…PL-2 và ket_qua.py, doi_bac.py.
1. ngan_ket_qua.py: ngưỡng = nguong.doc_nguong(khối "nguong" của tệp, tham số nguong_json) (Q1); kiểm luot có thật (không → LUOT_KHONG_TON_TAI), ma_module/khau khớp; dòng không thuộc lượt → ngoai_mau; gửi trùng (đã có ket_qua_kiem) → so_trung; loại = loai_dung nếu có, không thì dong_luot.loai (Q2); loai_dung khác dong_luot.loai → so_sua_loai += 1, nguon_loai_sai = dong_luot.nguon_loai; dòng ngoài lượt không có loại → dùng loai_dung, không có thì chua_phan_loai; gom theo (khau, loai): đọc ty_le (CAS row_version), áp doi_bac.cap_nhat lần lượt, ghi ket_qua_kiem + ty_le cùng lô (≤ 99 kết quả + 1 ty_le mỗi lô) qua ngan_chung.ghi_lo_thu_lai; cặp mới dùng lay_hoac_tao rồi sửa CAS.
2. chay.py: năng lực audit.ghi_ket_qua@1 trả so_dong_nhan, so_trung, so_ngoai_mau, so_cap_doi_bac, so_sua_loai, phien_ban_engine; chay_thu_demo: chạy phan_luong DEMO rồi ghi kết quả (nếu CLI không nối được 2 bước thì dựng ngăn bằng dữ liệu DEMO trong test, ghi rõ).
Test: hai ghi_ket_qua cùng lúc (gay_xung_dot_ngan) → đúng một lần thử lại, số đếm không lệch; NGAN_BAN sau 3 lần thử lại; đổi bậc hiệu lực ngay ở lượt phân luồng kế tiếp; lỗi ngoài mẫu; sửa loại; xem_ngan C4; kết quả không có tỷ lệ (C5).
Đạt: 3 lệnh AGENTS.md §5.
```

### 3.2 Đợt 4 — việc con PL-4 … PL-8 (giao 20/11 theo yêu cầu "làm tối đa")

Nền chung: nhánh có PL-0, PL-1 (đã sửa sau rà), PL-2A (Q6), PL-2B. PL-2 ghép và PL-3 ghép đang làm song song ở nhánh khác: việc con đợt 4 KHÔNG sửa `chay.py`, `engine.json`, `phan_luong.py`, `ngan_luot.py`, `ngan_ket_qua.py`, `xuat_json.py`, `sql/`. Mỗi việc chỉ tạo tệp sở hữu + test `tests/test_<việc>_*.py`; báo cáo ghi đoạn cần nối (để lead/việc ghép đưa vào).

### PL-4A — Hồ sơ hành vi (thuần)
```
Đọc AGENTS.md; PHIEU-ENGINE-e_phan_luong.md §4.1, §4.4, §4.5, §6 (C4); GIAO-CODEX-e_phan_luong.md §2 (đủ), §3.2, §4 (Q8, Q9); kieu.py, co.py (HoSoLoai), nguong.py (tim_chia_nho, tong_truoc). Không sửa tệp ngoài sở hữu.
Làm việc PL-4A: viết ho_so.py và e_phan_luong/tests/test_pl4a_ho_so.py. Chỉ thư viện chuẩn.
- HoSo (dataclass frozen) cho một (khau, loai): bieu_do theo tháng {ky "YYYY-MM": {bucket int: so_luong int}} (thang log: bucket = floor(10 × log10(|so|)) với |so| ≥ 1, |so| < 1 → bucket 0; tính bằng Decimal, không float), doi_tac {bam: ky gặp gần nhất}, tong_ngay {bam: {ngay ISO: tổng |so| Decimal}}, ky_lam_moi (str|None). so_nghiep_vu = tổng số đếm các tháng đang giữ (thuộc tính tính được).
- moi(khau, loai); tu_ban_ghi(dict) / ve_ban_ghi(hs) -> dict đúng cột §2.4 (so_nghiep_vu, bieu_do, bam_doi_tac, tong_7_ngay, ky_lam_moi; ba cột JSON là chuỗi JSON chuẩn: ensure_ascii=False, sort_keys=True, separators=(",",":"), số tiền là chuỗi thập phân). Chuỗi hỏng → coi như hồ sơ mới + ghi logging (không lỗi cả lượt).
- cong(hs, ds, *, ky, cua_so_ngay=7) — ds là các bộ (tien_ss: Tien|None đã trị tuyệt đối, bam_dt: str|None, ngay: date); cộng bieu_do[ky] (dòng có tiền), doi_tac[bam] = max(ky cũ, ky), tong_ngay[bam][ngay] += |so|; sau đó chỉ giữ tong_ngay các ngày > (ngày lớn nhất đang giữ − cua_so_ngay). Anh chốt Q8: KHÔNG khử trùng riêng dòng nộp lại.
- Trần Anh chốt Q9: tối đa 20.000 đối tác mỗi (khau, loai); vượt thì bỏ đối tác có ky gặp gần nhất cũ nhất (cùng ky thì theo băm tăng dần, tái hiện được), trả kèm số đã bỏ để màn engine cảnh báo: cong(...) -> tuple[HoSo, int].
- anh_chup(hs, *, tien_te_nguong) -> co.HoSoLoai: phan_vi_95 = cận trên của bucket chứa phân vị 95 (10^((b+1)/10), Decimal làm tròn lên số nguyên), None khi so_nghiep_vu < 50; bam_doi_tac = tập khóa doi_tac.
- tong_truoc(hs) -> Callable[[str, date], Decimal] cho nguong.tim_chia_nho (ngày không có → 0).
- lam_moi(hs, ky_moi) -> HoSo: chỉ giữ 12 tháng gần nhất tính tới tháng trước ky_moi trong bieu_do và doi_tac; ky_lam_moi = ky_moi.
Test: biên bucket (1, 9,99, 10, 10^9, số lẻ), phân vị trên 50/49 nghiệp vụ, khứ hồi ve/tu, chuỗi hỏng, cửa sổ 7 ngày, trần 20.000 (dựng 20.005 băm), lam_moi bỏ tháng thứ 13, C4: ve_ban_ghi không chứa mã đối tác thô, mã giao dịch, diễn giải (dựng dữ liệu có chuỗi nhận biết rồi tìm trong JSON).
Không tạo __init__.py, conftest.py. Chạy pytest test của mình (dùng --basetemp trong worktree nếu thư mục tạm bị chặn).
```

### PL-4B — Chốt kỳ tháng
```
Đọc AGENTS.md; PHIEU-ENGINE-e_phan_luong.md §4.3, §4.5, §6; GIAO-CODEX-e_phan_luong.md §2 (đủ), §3.2; kieu.py, ty_le.py, doi_bac.py, thong_ke.py, ngan_chung.py; engine.json phần ngan_du_lieu (bảng ty_le, chot_ky, ket_qua_kiem, ho_so_hanh_vi). SDK 2.2.0: viec.ngan.doc/tim/lo, lay_hoac_tao (KetQuaLenh.da_tao), NganXungDot.
Làm việc PL-4B: viết chot_ky.py và e_phan_luong/tests/test_pl4b_chot_ky.py (CoreGia, dữ liệu DEMO dựng trong test bằng app.ngan/viec.ngan).
- ky_hien_tai(luc: datetime | None = None) -> "YYYY-MM" theo giờ Việt Nam (UTC+7); ky_truoc(ky) -> "YYYY-MM".
- chot_neu_can(viec, cs, *, luc=None, lam_moi_ho_so: Callable[[dict, str], dict] | None = None) -> int — gọi ĐẦU mọi năng lực. ky_moi = ky_hien_tai(luc), kt = ky_truoc(ky_moi). Đọc mọi ty_le (ngan_chung.tim_tat_ca) và mọi chot_ky loc {"ky": kt}; với mỗi (khau, loai) chưa có chot_ky của kt: lay_hoac_tao chot_ky (ky=kt, khau, loai) với bản chụp các cột số liệu ty_le hiện tại; CHỈ khi da_tao = True mới: tính lại mau_12t, loi_12t, loi_sad_12t, loi_ngoai_mau_12t từ ket_qua_kiem còn hạn (loc {khau, loai}; chỉ ket_qua dat/sai; mau/loi chỉ nguon_mau chon_mau; loi_sad gồm muc sad|te mọi nguồn; loi_ngoai_mau = sai và nguon_mau ngoai_mau), tính lại diem/nhan như doi_bac (dùng lại hàm của doi_bac/thong_ke, không viết lại công thức), sửa ty_le bằng CAS qua ngan_chung.ghi_lo_thu_lai; nếu có lam_moi_ho_so và có bản ghi ho_so_hanh_vi (khau, loai) thì sửa CAS bằng giá trị lam_moi_ho_so(gia_tri_cu, ky_moi). Trả số cặp đã chốt.
- Hai việc chốt cùng lúc → chỉ một bên chốt (lay_hoac_tao), bên kia trả 0; xung đột CAS → thử lại theo ngan_chung (quá → NGAN_BAN).
Test: tháng đầu tiên (chưa có ty_le) → 0; có 3 cặp → chốt 3, gọi lại cùng tháng → 0; sang tháng sau → chốt tiếp; 12 tháng tính lại đúng số liệu từ ket_qua_kiem DEMO (dựng cả dòng hết hạn bằng het_han nếu CoreGia hỗ trợ, không thì ghi rõ); gay_xung_dot_ngan → đúng một lần thử lại; bản chụp chot_ky không chứa số tiền/ngày/đối tác (C4).
Không tạo __init__.py, conftest.py nếu chưa có (nhánh đã có conftest của PL-0 thì dùng). Chạy pytest test của mình.
```

### PL-5A — Lập `yeu_cau_ai`, đọc `tra_loi_ai`
```
Đọc AGENTS.md; PHIEU-ENGINE-e_phan_luong.md §3 (chuỗi b), §4.2 mục 3, §7, §8 (AI giả); GIAO-CODEX-e_phan_luong.md §2 (đủ, nhất là §2.5), §3.2, §4 (kết quả kiểm Core thật về mo_tep); _chung/docs/LOAI-DU-LIEU-RIENG.md §2.2–2.3 (đủ); _chung/contract/yeu_cau_ai.schema.json, tra_loi_ai.schema.json; mẫu lập yêu cầu: e_doi_chieu/goi/e_doi_chieu/e_doi_chieu/chuan_bi_ai.py, e_trich_xuat (chuỗi chuẩn bị → ai.hoi_theo_yeu_cau@1 → hậu kiểm); AI giả DEMO: e_phan_luong/tests/demo/tra-loi-ai-*.json, yeu-cau-ai-DEMO.json.
Làm việc PL-5A: viết chuoi_ai.py và e_phan_luong/tests/test_pl5a_chuoi_ai.py. Chỉ thư viện chuẩn (+ jsonschema CHỈ trong test nếu venv có). Không gọi mạng, không gọi engine khác.
- lap_tai_lieu(ds: Sequence[tuple[int, str]]) -> tuple[list[dict], dict[int, list[int]]] — ds = (chi_so dòng, nội dung trường phân loại); khử trùng theo nội dung đã chuẩn hóa NFC + gộp khoảng trắng (giữ nguyên chữ gốc lần đầu gặp); trả tai_lieu đánh chỉ số 0..n-1 và ánh xạ chỉ số tài liệu → các chi_so dòng. Trần: ≤ 5.000 giá trị, mỗi giá trị cắt KHÔNG được (quá 2.000 ký tự → dòng đó không gửi AI, để chua_phan_loai, đếm).
- khuon_tra_loi(danh_muc) -> dict JSON Schema: {"phan_loai":[{"chi_so":int,"loai":enum mã danh mục,"tin_cay":number 0..1}]}, additionalProperties false.
- lap_chuyen_tiep(tep_lo: dict, bam_tep: str, khau: str, khong_can_ai: bool) -> dict đúng GIAO-CODEX §2.5 (tep_lo là NGUYÊN đối tượng {"tep_id","ten","mime","kich_thuoc"}), ≤ 4 KiB.
- lap_yeu_cau_ai(tai_lieu, danh_muc, tham_so, chuyen_tiep) -> dict phong bì {"loai": "yeu_cau_ai", "yeu_cau_ai": {...}} đúng schema và LOAI-DU-LIEU-RIENG §2.2: prompt lấy từ tham_so (ma_prompt, phien_ban_prompt, prompt — thuộc module, engine không viết prompt nghiệp vụ; thiếu prompt → THAM_SO_KHONG_HOP_LE), model_uu_tien nếu có, chỉ Local; tai_lieu rỗng khi khong_can_ai.
- doc_chuyen_tiep(phong_bi_tra_loi) -> dict — thiếu/sai dạng → loi("CHUOI_KHONG_KHOP").
- doc_tra_loi_ai(phong_bi, *, danh_muc, so_tai_lieu, nguong_tin_cay: Decimal) -> tuple[dict[int, str], list[str]] — nha_cung_cap khác "local" → loi("KHONG_PHAI_LOCAL"); khong_thay_can_cu hoặc sai khuôn → {} + cảnh báo (KHÔNG lỗi cả lượt); chỉ số ngoài [0, so_tai_lieu), loai ngoài danh mục, tin_cay < nguong_tin_cay → bỏ mục đó + cảnh báo; chỉ số trùng → lấy mục đầu.
- kiem_tham_chieu_tep(dau_vao) — dùng lại cách kiểm hình dạng nghiêm như Core thật đã có ở tests/test_pl0_can_core.py (đối tượng có khóa tep_id); không có → CHUOI_KHONG_KHOP.
Test với 5 phong bì AI giả DEMO (đúng enum, sai enum, tin cậy thấp, cloud, khong_thay_can_cu) + khuôn sai + chuyen_tiep thiếu; yêu cầu hợp schema; chuyen_tiep ≤ 4 KiB; tài liệu khử trùng; không có tỷ lệ/xác suất trong cảnh báo.
Không tạo __init__.py, conftest.py nếu chưa có. Chạy pytest test của mình.
```

### PL-6A — Excel/CSV theo khuôn cột
```
Đọc AGENTS.md; PHIEU-ENGINE-e_phan_luong.md §5.1, §5.2, §7; GIAO-CODEX-e_phan_luong.md §2 (đủ), §3.2; e_kiem_excel/docs/PHIEU-ENGINE-e_kiem_excel.md §4.2 (khuôn tong_quat, khuon_cot_json) và e_kiem_excel/goi/e_kiem_excel/e_kiem_excel/doc_tong_quat.py, nhan_dien.py (mẫu nhận diện .xlsx/.xls, trần giải nén); kieu.py, tien.py (doc_so_thap_phan, doc_tien), doc_lo.py (luật kiểm dòng, trần), tu_khoa.py (chuan).
Làm việc PL-6A: viết doc_bang.py và e_phan_luong/tests/test_pl6a_doc_bang.py; tests/demo/sinh_bang_demo.py sinh .xlsx (zipfile tự ghi XML như e_kiem_excel, có giá trị lưu) và .csv DEMO (UTF-8 có/không BOM, phân cách , và ;). openpyxl đã ghim trong goi/e_phan_luong/requirements.lock (cài vào .venv bằng pip --require-hashes nếu thiếu).
- nhan_dien(du_lieu: bytes, ten: str | None, mime: str | None) -> "json" | "xlsx" | "csv": ZIP + đuôi .xlsx → xlsx (kiểm trần giải nén/entry như e_kiem_excel trước khi mở); chữ ký OLE (.xls) → TEP_KHONG_HO_TRO; bắt đầu bằng { (sau BOM/khoảng trắng) → json; đuôi .csv hoặc text/csv → csv; còn lại → TEP_KHONG_HO_TRO.
- doc_lo_bang(du_lieu, kieu, *, khuon_cot_json: str, ma_module: str, tien_te: str | None, ky: str | None) -> Lo (nguong=None). khuon_cot_json {"phien_ban":1, "sheet": tên|null, "cot":[{"ma": <trường §5.1 | tien_te | tien_te_quy_doi | thuoc_tinh.<khóa>>, "tu_khoa": [...], "bat_buoc": bool}], "dong_dung": [từ khóa dừng như "cộng", "tổng cộng"]}; dòng tiêu đề = dòng đầu tiên khớp đủ cột bắt buộc (so bằng tu_khoa.chuan); thiếu cột bắt buộc (ma, ngay, so_tien) → THAM_SO_KHONG_HOP_LE. .xlsx đọc read_only=True, data_only=True; ô ngày (datetime) hoặc chuỗi YYYY-MM-DD hoặc DD/MM/YYYY; ô số (int/float từ openpyxl → Decimal(repr(x)), ghi rõ giới hạn 15 chữ số của Excel) hoặc chuỗi theo tien.doc_so_thap_phan; dòng trống bỏ qua.
- Tiền tệ: cột tien_te có giá trị thì dùng; không có cột và tien_te (Cài đặt bước) có → dùng; không có cả hai → Tien(so, None) (dòng sẽ Đỏ CHUA_RO_TIEN_TE, KHÔNG tự gán VND).
- Cùng luật và trần với doc_lo.py (mã trùng, ≤ 50.000 dòng, ≤ 20 MiB, mã không ký tự điều khiển); dùng lại hàm của doc_lo/tien, không viết lại.
Test: xlsx và csv DEMO cho cùng Lo với JSON tương ứng; thiếu cột bắt buộc; .xls giả → TEP_KHONG_HO_TRO; bom nén → VUOT_GIOI_HAN; CSV ; và ,; BOM; dòng dừng "Cộng"; ngày DD/MM/YYYY; thiếu tiền tệ → tien_te None.
Không tạo __init__.py, conftest.py nếu chưa có. Chạy pytest test của mình.
```

### PL-7A — Đầu ra `e_hoa_don` → lô nghiệp vụ
```
Đọc AGENTS.md; PHIEU-ENGINE-e_phan_luong.md §5.4; GIAO-CODEX-e_phan_luong.md §2 (đủ), §3.2, §4 (mo_tep Core thật); e_hoa_don/goi/e_hoa_don/engine.json (truong_ra của hoa_don.doc_xml@2 và hoa_don.doc_zip@1, tệp chi_tiet_nguon) và mã/tài liệu e_hoa_don liên quan; kieu.py, tien.py, doc_lo.py.
Làm việc PL-7A: viết hoa_don.py và e_phan_luong/tests/test_pl7a_hoa_don.py (+ tests/demo/hoa-don-*-DEMO.json dựng theo đúng trường ra e_hoa_don, dữ liệu DEMO).
- lo_tu_hoa_don(truong: dict, *, ma_module: str, loai_nghiep_vu: str | None) -> Lo — một hóa đơn = một nghiệp vụ; ma = mẫu số + ký hiệu + số (nối bằng "-", ghi rõ); so_tien = tong_thanh_toan kèm tiền tệ hóa đơn (không có tiền tệ → tien_te None, KHÔNG tự gán VND); ngay = ngày hóa đơn; doi_tac = ma_so_thue_ban (engine băm khi dùng, không lưu thô); co_do_cung = (can_kiem_tra là true); loai = loai_nghiep_vu nếu có; tên trường lấy đúng engine.json của e_hoa_don (ghi bảng ánh xạ trong docstring).
- lo_tu_chi_tiet_zip(du_lieu: bytes, *, ma_module, loai_nghiep_vu) -> Lo — đọc tệp chi_tiet_nguon (định dạng do e_hoa_don sinh), mỗi hóa đơn một nghiệp vụ; hóa đơn lỗi đọc trong tệp nguồn → bỏ và đếm (trả kèm số bỏ: tuple[Lo, int]); trần như doc_lo.
- lay_tep_chi_tiet(truong) -> dict — đối tượng tệp chi_tiet_nguon (có khóa tep_id) để bước ghép gọi viec.mo_tep; không có → DU_LIEU_KHONG_HOP_LE.
Test: ánh xạ đủ trường từ phong bì DEMO đúng hình dạng e_hoa_don; can_kiem_tra true → co_do_cung; thiếu tiền tệ; tệp chi tiết nhiều hóa đơn + một hóa đơn hỏng; trùng mã.
Không tạo __init__.py, conftest.py nếu chưa có. Chạy pytest test của mình.
```

### PL-8A — Excel danh sách Đỏ
```
Đọc AGENTS.md; PHIEU-ENGINE-e_phan_luong.md §5.3, §5.5 (tep_ds_do), C5; GIAO-CODEX-e_phan_luong.md §2 (đủ), §3.2; kieu.py (KetQuaDong, mã lý do, cờ); mẫu ghi Excel trong RAM: e_kiem_excel/goi/e_kiem_excel/e_kiem_excel/bao_cao.py.
Làm việc PL-8A: viết xuat_excel.py và e_phan_luong/tests/test_pl8a_xuat_excel.py. Dùng openpyxl (đã ghim).
- TEN_LY_DO, TEN_CO: câu tiếng Việt ngắn cho từng mã lý do/cờ trong kieu.py (ví dụ VUOT_TE → "Vượt ngưỡng TE"); không nêu tỷ lệ, xác suất, bậc, giá trị ngưỡng.
- lap_ds_do(ds: Sequence[KetQuaDong], *, ma_luot, ma_module, khau, phien_ban_engine) -> bytes — sheet "Can kiem" chỉ dòng Đỏ: cột Mã, Lý do (tiếng Việt, nối "; "), Cờ, Loại, Nguồn loại, rồi các cột TRỐNG để người kiểm ghi: Kết quả (dat/sai/khong_kiem, có Data Validation danh sách), Số tiền sai, Tiền tệ, Loại đúng; dòng đầu ghi ma_luot, khau (để module lập JSON §5.3); sheet "Huong dan" giải thích cách ghi. Không có cột tỷ lệ/xác suất/bậc/hạt giống. Bytes tái hiện được: đặt cố định workbook.properties.created/modified, không thời điểm hiện tại.
- doc_ds_do_da_ghi(du_lieu: bytes) -> dict — đọc lại tệp người kiểm đã điền thành JSON kết quả §5.3 (ma_luot, khau từ dòng đầu; bỏ dòng chưa ghi kết quả) để module dùng thử; sai mẫu → DU_LIEU_KHONG_HOP_LE.
Test: mở lại được bằng openpyxl; chỉ dòng Đỏ; không có chữ "ty le", "xac suat", "bac", "hat giong" (bỏ dấu) ở bất kỳ ô nào (C5); 2 lần gọi cùng đầu vào → cùng bytes; khứ hồi điền kết quả → JSON §5.3 hợp lệ với ket_qua.doc_ket_qua_json.
Không tạo __init__.py, conftest.py nếu chưa có. Chạy pytest test của mình.
```

### PL-8B — Màn Admin `ui/bang_ty_le.js`
```
Đọc AGENTS.md (§4 quy tắc 13); PHIEU-ENGINE-e_phan_luong.md §4.2 (sai loại theo nguồn), §4.3, §6 (giao_dien_quan_tri), C5; GIAO-CODEX-e_phan_luong.md §2.4 (bảng ngăn), §3.2; docs/goi-gui-engine/sdk-2.2.0/MAU-PHIEU-ENGINE.md (giao_dien_quan_tri), API-CORE-v1.md và trinh_duyet.js trong wheel SDK 2.2.0 (KttCore.engine(ma): đọc ngăn, cấu hình); mẫu màn engine: e_ocr/goi/e_ocr/ui/, e_mask/goi/e_mask/ui/ (nếu có).
Làm việc PL-8B: viết goi/e_phan_luong/ui/bang_ty_le.js và e_phan_luong/tests/test_pl8b_ui.py. KHÔNG sửa engine.json: ghi trong báo cáo đúng đoạn JSON giao_dien_quan_tri (vai admin_core, chỉ đọc) để lead nối.
- Màn chỉ đọc, chỉ Admin: (1) bảng khâu × loại từ ngăn ty_le: bậc, chế độ, điểm, nhãn, mẫu/lỗi từ lần đổi bậc, mẫu/lỗi 12 tháng; (2) số lần sai loại theo nguồn (quy_tac, ai) đếm từ ket_qua_kiem.nguon_loai_sai; (3) lịch sử chot_ky theo kỳ; (4) tra lượt theo ma_luot: ma_module, khau, bam_dau_vao, hạt giống (chỉ hiện khi Admin bấm "Xem"), số dòng Đỏ/Xanh của lượt; (5) cảnh báo khi hồ sơ hành vi đã chạm trần 20.000 đối tác (nếu có trường đếm).
- Không gọi mạng ngoài (chỉ API Core qua KttCore), không eval/new Function, không innerHTML/outerHTML/insertAdjacentHTML với dữ liệu (dùng textContent/createElement); câu tiếng Việt; lỗi hiện câu dễ hiểu, mã lỗi trong "Chi tiết hỗ trợ" thu gọn.
Test (Python, không cần trình duyệt): quét bang_ty_le.js không có innerHTML/outerHTML/insertAdjacentHTML/eval/new Function/fetch( tới http(s) ngoài/XMLHttpRequest trực tiếp; chỉ gọi hàm KttCore có trong trinh_duyet.js của SDK 2.2.0 (đối chiếu tên hàm); nếu máy có node thì chạy node --check.
Chạy pytest test của mình.
```

## 4. Cần Core / Chờ Anh

**Kiểm 2 điểm "Cần Core" (20/11/2026, lead đọc mã Core `ma-nguon-core-sach` HEAD `a07e061` và CoreGia SDK 2.2.0; chưa chạy trên Core thật):**

| Điểm | Kết luận | Căn cứ | Cách làm của engine |
|---|---|---|---|
| 1. Module chạy nút bằng tệp tự lập (Blob JSON), không qua hộp chọn tệp | **Được** về cơ chế. Core không phân biệt Blob hay tệp chọn; mime dò theo byte (JSON → `application/json`). SDK 2.2.0 **chưa có** hàm JS `nut.chay` (chỉ có ở mã Core 2.4.0); module dùng `api.goi({tep: new File([blob], "lo.json")})` gọi `POST /api/v1/module/{ma}/nut/{nut}/chay`; nút phải khai `nhan_tep.mime` có `application/json` | `core/cong_quy_trinh.py:128-132`, `core/tep.py:132-154`, `trinh_duyet.js` 2.2.0 dòng 378-390 | Ghi vào §3 hướng dẫn nhúng (README). Cần Core: phát hành `nut.chay` trong SDK cho module; chạy thật một lần trên Core tập |
| 2. Bước 3 `mo_tep` tệp do bước 1 tải lên | **Được có điều kiện:** đầu vào bước phải chứa **đối tượng có khóa `tep_id`** (Core thật dùng `jsonb_path_exists '$.** ? (@.tep_id == $t)'`), tệp cùng việc. CoreGia lỏng hơn (so chuỗi con, kho tệp toàn cục) | `core/sql/134_engine_keo_viec.sql:392-413`, `thu.py:548-557` | `chuyen_tiep` mang nguyên đối tượng tệp (§2.5); test kiểm hình dạng nghiêm. Cần Core: CoreGia cùng ngữ nghĩa Core thật; chạy thật chuỗi 3 bước trên Core tập |

**Anh chốt 20/11/2026** (lead hỏi vì phiếu chưa rõ; đã ghi vào các mục §2–§3 ở trên):

| # | Câu | Anh chốt |
|---|---|---|
| Q1 | Ngưỡng để xếp mức sai khi ghi kết quả kiểm | Module gửi kèm khối `nguong` trong JSON kết quả (không có thì `nguong_json` của Cài đặt bước); không thêm cột |
| Q2 | Loại, nguồn loại của dòng khi ghi kết quả | Thêm 2 cột `loai`, `nguon_loai` vào `dong_luot` |
| Q3 | Số tiền âm | So theo giá trị tuyệt đối |
| Q4 | Dưới SAD có nhân hệ số cờ | Có: `p = min(1, 2% × tích hệ số)` |
| Q5 | Nộp lại | Lần trước Đỏ chưa có kết quả kiểm → giữ Đỏ `NOP_LAI`; đã có kết quả → xét lại bình thường |
| Q6 | Lỗi khi đang 100% | Chỉ lỗi ≥ TE mới đếm lại 30 mẫu sạch |
| Q7 | `so_tien_sai` khác tiền tệ ngưỡng | Từ chối (`DU_LIEU_KHONG_HOP_LE`), module gửi số đã quy đổi |
| Q8 | Nộp lại làm cộng trùng tổng chia nhỏ | Không xử lý riêng: "Đã có chống trùng rồi. Không lo việc chia nhỏ vì việc xác lập TE để phân luồng chỉ thực hiện bởi admin, người dùng cũng không biết ngưỡng" |
| Q9 | Trần tập băm đối tác trong hồ sơ hành vi | 20.000 đối tác mỗi (khâu, loại); vượt thì bỏ đối tác lâu không gặp nhất, cảnh báo ở màn engine |
