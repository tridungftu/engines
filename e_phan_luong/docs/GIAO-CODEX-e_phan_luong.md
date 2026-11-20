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

### 3.3 Đợt 5 — lệnh ghép PL-4 … PL-8 (giao 20/11; lưu nguyên bản đã giao)

Lead tách `quy_trinh.py` (điểm nối có chủ sở hữu) ở đầu nhánh PL-4 để 5 lát ghép chạy song song. PL-5…PL-8 nền trên commit tách; PL-4 bước 2 chạy sau bước 1.

#### PL-4 (bước 1) — sửa sau rà soát độc lập PL-2/PL-3
```
Sửa sau rà soát độc lập PL-2/PL-3 cho e_phan_luong (lead duyệt 20/11/2026). Đọc AGENTS.md; e_phan_luong/docs/PHIEU-ENGINE-e_phan_luong.md §4.3–§4.5, §5.3, §6, §7; GIAO-CODEX-e_phan_luong.md §2, §4 (Q1–Q9); e_phan_luong/goi/e_phan_luong/e_phan_luong/quy_trinh.py (lead tách 20/11). Nhánh này có PL-0…PL-3 + quy_trinh.py + ho_so.py + chot_ky.py (chưa nối). Các lát PL-5…PL-8 đang ghép song song ở nhánh khác: KHÔNG đổi chữ ký hàm công khai của quy_trinh.py; KHÔNG sửa quy_trinh.doc_tep_lo, quy_trinh.xuat_ket_qua, chay.py.
Sửa đúng 7 điểm, mỗi điểm có test chứng minh (tests/test_pl4_sua_ra.py; sửa test cũ nếu cần nhưng không nới mục đích):
M1 (vừa) — chạy lại cùng việc phải idempotent: ma_luot suy từ việc, không từ hạt giống: ma_luot = "PL-" + sha256("e_phan_luong|luot|" + viec.id + "|" + bam_dau_vao). Đầu quy_trinh.chay_phan_luong: doc luot(ma_luot) — đã có → đây là việc Core giao lại → dùng lại hat_giong đã lưu (bytes.fromhex), kết quả trùng từng byte với lần trước; chưa có → hạt giống mới. dong_luot đã có của chính ma_luot này mà luot chưa có (lần trước chạy dở) → ghi đè bằng sua (CAS) cho đúng quyết định của lần chạy hiện tại, không để lẫn quyết định cũ. tra_nop_lai bỏ qua lượt của chính ma_luot hiện tại. Kiểm tái hiện vẫn đúng: cùng hạt giống + đầu vào + viec.id → cùng bytes. Ghi rõ trong README.
M3 (thấp-vừa) — doi_bac.cap_nhat: ty_le.bac đã lưu không còn trong thang cs.bac hiện hành (Admin đổi chinh_sach_json) → ép về bậc gần nhất KHÔNG THẤP HƠN giá trị đã lưu trong thang mới (thận trọng); không ném ValueError thô.
T1 — ngan_luot.tra_nop_lai đọc ket_qua_kiem với gom_het_han=True (luot giữ 400 ngày, kết quả 365 ngày), như ngan_ket_qua._da_ghi.
T2 — ngan_chung.tim_tat_ca và mọi tim có phân trang truyền sap_xep theo các cột khóa của bảng để thứ tự ổn định trên Core thật (CoreGia sắp theo id).
T3 — quy_trinh.chay_phan_luong: Cài đặt bước có ma_module mà khác ma_module của tệp → loi("DU_LIEU_KHONG_HOP_LE").
T4 — ket_qua._doc_tien dùng tien.doc_so_thap_phan (bỏ số 0 lẻ thừa trước khi đếm), một luật đọc số chung.
T5 — ngan_ket_qua: chỉ đọc/kiểm ngưỡng khi có ít nhất một dòng ket_qua = sai; nguong_json sai mà không cần ngưỡng → không làm hỏng cả tệp.
Tệp được sửa: quy_trinh.py (CHỈ hàm chay_phan_luong), ngan_luot.py, ngan_chung.py, doi_bac.py, ket_qua.py, ngan_ket_qua.py, README.md, sql/kiem_ke.json (tính lại), test. Không sửa kieu.py, loi.py, VIEC.md.
Đạt: 3 lệnh AGENTS.md §5 (thu mã 0; pytest 0 lỗi; kiem_doc_lap mã 0); dán kết quả thật.
```

#### PL-4 (bước 2) — ghép hồ sơ hành vi, chốt kỳ, chia nhỏ qua lô
```
Đọc AGENTS.md; e_phan_luong/docs/PHIEU-ENGINE-e_phan_luong.md (đủ); e_phan_luong/docs/GIAO-CODEX-e_phan_luong.md §2 (hợp đồng), §3.2 (việc con đợt 4), §4 (Cần Core, bảng Q1–Q9 Anh chốt); e_phan_luong/goi/e_phan_luong/e_phan_luong/quy_trinh.py (lead tách 20/11: mỗi hàm là một ĐIỂM NỐI có chủ sở hữu, xem docstring đầu tệp).
Nhánh này có PL-0…PL-3 (thu 1/1 ĐẠT, 1115 test) + quy_trinh.py + việc con của lát bạn. Các lát ghép khác chạy SONG SONG ở nhánh khác (PL-4 hồ sơ hành vi/chốt kỳ, PL-5 chuỗi Local AI, PL-6 Excel/CSV, PL-7 hóa đơn, PL-8 Excel danh sách Đỏ + màn Admin): chỉ sửa ĐÚNG điểm nối và tệp ghi trong lệnh của bạn; không đổi chữ ký hàm công khai đã có; không sửa kieu.py, loi.py, VIEC.md, CHANGELOG.md.
Sau khi đổi tệp trong goi/: tính lại kiểm kê (python -B e_phan_luong/tests/kiem_bam_goi.py --cap-nhat); đổi engine.json thì chạy python _chung/cong-cu/sinh_danh_muc_engine.py. Năng lực vừa làm thật thì bỏ khỏi CHUA_LAM_CON trong tests/test_pl0_goi.py. Chạy pytest bằng --basetemp trong worktree nếu thư mục tạm bị chặn.
Đạt: 3 lệnh AGENTS.md §5 (thu mọi ví dụ [ĐẠT] mã 0; pytest 0 lỗi; kiem_doc_lap mã 0); dán kết quả thật; ghi "đã kiểm bằng Core giả (CoreGia)".

LÀM LÁT PL-4 — ghép hồ sơ hành vi, chốt kỳ tháng, chia nhỏ qua lô (phiếu §4.1, §4.4, §4.5). Đã có ho_so.py (PL-4A), chot_ky.py (PL-4B). Tệp được sửa: quy_trinh.py (CHỈ hai hàm bat_dau và chay_phan_luong), chot_ky.py, ty_le.py và co.py (chỉ thêm khóa chính sách ở mục 5, giữ hành vi mặc định), tệp mới ngan_ho_so.py, test tests/test_pl4_*.py.
1. ngan_ho_so.py: doc_ho_so_khau(viec, khau) → dict loai → (HoSo, BanGhi|None), đọc mọi ho_so_hanh_vi của khâu (ngan_chung.tim_tat_ca); ghi_ho_so(viec, khau, loai, ham_cap_nhat) — CAS qua ngan_chung.ghi_lo_thu_lai; chưa có thì lay_hoac_tao rồi sửa CAS; xung đột thì đọc lại và áp lại ham_cap_nhat.
2. quy_trinh.bat_dau: gọi chot_ky.chot_neu_can(viec, doc_chinh_sach_buoc(viec.tham_so), lam_moi_ho_so=hàm (cu, ky) → ho_so.ve_ban_ghi(ho_so.lam_moi(ho_so.tu_ban_ghi(cu), ky))); trả số cặp đã chốt.
3. Sửa chot_ky.py theo ghi nhận PL-4B: tạo bản chụp chot_ky và sửa ty_le (số 12 tháng) trong CÙNG MỘT lô nguyên tử (them chot_ky + sua ty_le CAS); trùng khóa chot_ky (bên khác đã chốt) → coi như đã chốt, không tính lại; xung đột CAS → đọc lại và thử lại. Test chứng minh lỗi giữa chừng không để lại chot_ky mà ty_le chưa tính lại.
4. quy_trinh.chay_phan_luong: trước lớp 1 đọc hồ sơ mọi loại của khâu; tong_truoc(bam, ngay) = tổng tong_ngay của MỌI loại trong khâu (chia nhỏ gom theo đối tác + khâu, không theo loại; Anh chốt Q8: không khử trùng riêng dòng nộp lại); truyền tong_truoc vào xet_lop1_lo và ho_so_theo_loai (loại → ho_so.anh_chup của hồ sơ loại đó; loại chưa có hồ sơ → anh_chup của hồ sơ mới) vào xet_lop23_lo. SAU ngan_luot.ghi_luot: cộng lô vào hồ sơ từng (khâu, loại) bằng ho_so.cong (tien_ss đã trị tuyệt đối của lớp 1, băm đối tác bằng phan_luong.bam_doi_tac, ngày nghiệp vụ, ky = chot_ky.ky_hien_tai), ghi CAS; số đối tác bị bỏ vì trần 20.000 (Q9) ghi logging.
5. ty_le.ChinhSach thêm khóa toi_thieu_ho_so_doi_tac_moi (số nguyên ≥ 0, MẶC ĐỊNH 0 = đúng phiếu: đối tác chưa gặp trong 12 tháng là mới, kể cả khi hồ sơ trống): cờ DOI_TAC_MOI chỉ bật khi hồ sơ loại có so_nghiep_vu ≥ giá trị này. Ghi rõ trong README: theo mặc định, lượt đầu tiên của engine mới coi mọi đối tác là "mới" (×2); Admin đặt khóa này trong chinh_sach_json nếu muốn chờ đủ lịch sử.
Test: chia nhỏ qua 2 lô (lô 1: 1,1 tỷ + 1,1 tỷ; lô 2 hai ngày sau: 1,1 tỷ cùng đối tác, TE 3 tỷ → dòng lô 2 Đỏ NGHI_CHIA_NHO); DOI_TAC_MOI bật ở đối tác chưa gặp, tắt khi đã gặp, theo khóa mới; SO_TIEN_BAT_THUONG chỉ khi ≥ 50 nghiệp vụ; chốt kỳ khi sang tháng (ghim thời gian), chỉ một lần, cả khi hai việc cùng lúc; hồ sơ làm mới bỏ tháng thứ 13; xem_ngan C4 ho_so_hanh_vi không có mã đối tác thô/mã giao dịch/diễn giải; gay_xung_dot_ngan khi ghi hồ sơ → đúng một lần thử lại; chay_thu_demo vẫn ĐẠT.
```

#### PL-5 — ghép chuỗi Local AI
```
Đọc AGENTS.md; e_phan_luong/docs/PHIEU-ENGINE-e_phan_luong.md (đủ); e_phan_luong/docs/GIAO-CODEX-e_phan_luong.md §2 (hợp đồng, nhất là §2.5), §3.2, §4 (Cần Core: Core thật chỉ cho mo_tep khi đầu vào có ĐỐI TƯỢNG có khóa tep_id; bảng Q1–Q9); _chung/docs/LOAI-DU-LIEU-RIENG.md §2.2–2.3; e_phan_luong/goi/e_phan_luong/e_phan_luong/quy_trinh.py (lead tách 20/11: mỗi hàm là một ĐIỂM NỐI có chủ sở hữu).
Nhánh này có PL-0…PL-3 (thu 1/1 ĐẠT, 1115 test) + quy_trinh.py + chuoi_ai.py (PL-5A). Các lát ghép khác chạy SONG SONG ở nhánh khác (PL-4, PL-6, PL-7, PL-8): chỉ sửa ĐÚNG tệp ghi dưới đây; không đổi chữ ký hàm công khai đã có; không sửa kieu.py, loi.py, VIEC.md, CHANGELOG.md.
Sau khi đổi tệp trong goi/: tính lại kiểm kê (python -B e_phan_luong/tests/kiem_bam_goi.py --cap-nhat); đổi engine.json thì chạy python _chung/cong-cu/sinh_danh_muc_engine.py. Năng lực vừa làm thật thì bỏ khỏi CHUA_LAM_CON trong tests/test_pl0_goi.py. Chạy pytest bằng --basetemp trong worktree nếu thư mục tạm bị chặn.
Đạt: 3 lệnh AGENTS.md §5 (thu mọi ví dụ [ĐẠT] mã 0; pytest 0 lỗi; kiem_doc_lap mã 0); dán kết quả thật; ghi "đã kiểm bằng Core giả (CoreGia)".

LÀM LÁT PL-5 — chuỗi Local AI: audit.chuan_bi_phan_loai@1 (tep → yeu_cau_ai) và audit.phan_luong_sau_ai@1 (tra_loi_ai → truong) (phiếu §3 chuỗi b, §4.2 mục 3). Tệp được sửa: chay.py (CHỈ thân hai hàm năng lực trên), chuoi_ai.py, engine.json (chỉ phần hai năng lực này + chay_thu_demo của chúng), tệp mới ngan_chuoi.py nếu cần, test tests/test_pl5_*.py. KHÔNG sửa quy_trinh.py: chỉ gọi quy_trinh.bat_dau, doc_tep_lo, doc_cai_dat, chay_phan_luong(viec, lo, du_lieu, loai_ai=..., canh_bao_them=...).
1. chuan_bi_phan_loai: bat_dau → doc_tep_lo → doc_cai_dat; dòng chưa có loại từ module/quy tắc (phan_loai.gan_loai trả (None, None)) và có nội dung trường phân loại → chuoi_ai.lap_tai_lieu; trần tổng 500.000 ký tự của tai_lieu (giới hạn e_hoi_ai): phần vượt không gửi AI, đếm vào cảnh báo; tải NGUYÊN bytes tệp đầu vào lên Core bằng viec.tai_tep_ra (giữ tên/mime gốc) làm tep_lo; chuyen_tiep (≤ 4 KiB) gồm tep_lo là NGUYÊN đối tượng tệp, bam_tep, khau, khong_can_ai, và băm SHA-256 của (danh_muc_loai_json, bo_phan_loai_json, truong_phan_loai, khuon_cot_json) + băm tai_lieu để bước 3 kiểm khớp; không dòng nào cần AI → vẫn trả yeu_cau_ai với tai_lieu rỗng, khong_can_ai true.
2. phan_luong_sau_ai: bat_dau → chuoi_ai.doc_chuyen_tiep → kiem_tham_chieu_tep (hình dạng nghiêm như Core thật) → viec.mo_tep(tep_lo["tep_id"]) → so SHA-256 với bam_tep (khác → CHUOI_KHONG_KHOP) → đọc lại Lo đúng loại tệp (dựng đầu vào {"tep": tep_lo} rồi dùng logic của quy_trinh.doc_tep_lo qua một hàm phụ trong tệp của bạn, KHÔNG sửa quy_trinh.py) → tính lại tai_lieu, so băm cài đặt và băm tai_lieu (khác → CHUOI_KHONG_KHOP) → chuoi_ai.doc_tra_loi_ai (KHONG_PHAI_LOCAL; khong_thay_can_cu/sai khuôn → không lỗi cả lượt, chỉ cảnh báo) → ánh xạ chỉ số tài liệu → mã nghiệp vụ → loai_ai → quy_trinh.chay_phan_luong(..., loai_ai=loai_ai, canh_bao_them=các cảnh báo). khong_can_ai → bỏ qua phần AI.
3. engine.json: chay_thu_demo cho chuan_bi_phan_loai (lô nhỏ DEMO, cài đặt DEMO có prompt DEMO). Ví dụ phan_luong_sau_ai cần tệp do bước trước tải lên — nếu CLI không hỗ trợ thì KHÔNG thêm ví dụ giả; kiểm bằng test CoreGia nối 2 bước (bước 2 dùng phong bì tra_loi_ai giả DEMO, giữ nguyên chuyen_tiep từ bước 1). Danh mục: CHUOI mẫu audit.chuan_bi_phan_loai@1 → ai.hoi_theo_yeu_cau@1 → audit.phan_luong_sau_ai@1; script phải báo nối đúng.
Test: chuỗi đủ trên CoreGia với 5 phong bì AI giả (đúng enum → loại ai, nguồn ai; sai enum/tin cậy thấp → chua_phan_loai + cảnh báo; cloud → KHONG_PHAI_LOCAL; khong_thay_can_cu → chua_phan_loai, không lỗi lượt); sửa 1 byte tệp → CHUOI_KHONG_KHOP; đổi cài đặt giữa 2 bước → CHUOI_KHONG_KHOP; chuyen_tiep chỉ mang chuỗi tep_id (không phải đối tượng) → CHUOI_KHONG_KHOP; không dòng nào cần AI; C5: cảnh báo, trường ra không có tỷ lệ/độ tin cậy.
```

#### PL-6 — ghép Excel/CSV
```
Đọc AGENTS.md; e_phan_luong/docs/PHIEU-ENGINE-e_phan_luong.md (đủ); e_phan_luong/docs/GIAO-CODEX-e_phan_luong.md §2, §3.2, §4 (bảng Q1–Q9); e_phan_luong/goi/e_phan_luong/e_phan_luong/quy_trinh.py (lead tách 20/11: mỗi hàm là một ĐIỂM NỐI có chủ sở hữu).
Nhánh này có PL-0…PL-3 (thu 1/1 ĐẠT, 1115 test) + quy_trinh.py + doc_bang.py (PL-6A). Các lát ghép khác chạy SONG SONG ở nhánh khác (PL-4, PL-5, PL-7, PL-8): chỉ sửa ĐÚNG tệp ghi dưới đây; không đổi chữ ký hàm công khai đã có; không sửa kieu.py, loi.py, VIEC.md, CHANGELOG.md.
Sau khi đổi tệp trong goi/: tính lại kiểm kê (python -B e_phan_luong/tests/kiem_bam_goi.py --cap-nhat); đổi engine.json thì chạy python _chung/cong-cu/sinh_danh_muc_engine.py. Chạy pytest bằng --basetemp trong worktree nếu thư mục tạm bị chặn.
Đạt: 3 lệnh AGENTS.md §5 (thu mọi ví dụ [ĐẠT] mã 0; pytest 0 lỗi; kiem_doc_lap mã 0); dán kết quả thật; ghi "đã kiểm bằng Core giả (CoreGia)".

LÀM LÁT PL-6 — Excel/CSV theo khuôn cột cho audit.phan_luong@1 (phiếu §5.2). Tệp được sửa: quy_trinh.py (CHỈ hàm doc_tep_lo), doc_bang.py, engine.json (chỉ mime/đuôi nhận của audit.phan_luong@1 và audit.chuan_bi_phan_loai@1 + một chay_thu_demo Excel), goi/e_phan_luong/demo/ (thêm tệp .xlsx DEMO sinh bằng tests/demo/sinh_bang_demo.py), test tests/test_pl6_*.py.
1. Môi trường: .venv của worktree phải có đủ openpyxl, et_xmlfile, defusedxml đúng requirements.lock (pip install --require-hashes -r e_phan_luong/goi/e_phan_luong/requirements.lock; không có mạng thì cài từ cache pip hoặc từ site-packages của .venv tại D:/Claude/engines-wt/e_kiem_excel-ex-6 — ghi rõ cách đã làm và phiên bản).
2. quy_trinh.doc_tep_lo: dùng doc_bang.nhan_dien; json → doc_lo_json như cũ; xlsx/csv → doc_bang.doc_lo_bang với khuon_cot_json, ma_module, tien_te, ky từ Cài đặt bước (thiếu khuon_cot_json hoặc ma_module → THAM_SO_KHONG_HOP_LE; ngưỡng lấy từ nguong_json — doc_cai_dat đã báo THIEU_NGUONG khi thiếu); .xls → TEP_KHONG_HO_TRO. Trả (Lo, bytes gốc).
3. engine.json: nhận mime .xlsx và text/csv cho audit.phan_luong@1 và audit.chuan_bi_phan_loai@1 (dùng chung doc_tep_lo); một chay_thu_demo Excel DEMO.
Test: cùng dữ liệu ở JSON/xlsx/csv → cùng danh sách luồng với cùng hạt giống (ghim sinh_hat_giong); thiếu cột tiền tệ và không có tien_te → dòng Đỏ CHUA_RO_TIEN_TE, không gán VND; .xls → TEP_KHONG_HO_TRO; thiếu khuon_cot_json → THAM_SO_KHONG_HOP_LE; thiếu nguong_json → THIEU_NGUONG.
```

#### PL-7 — ghép nối sau e_hoa_don
```
Đọc AGENTS.md; e_phan_luong/docs/PHIEU-ENGINE-e_phan_luong.md (đủ); e_phan_luong/docs/GIAO-CODEX-e_phan_luong.md §2, §3.2, §4 (Cần Core: Core thật chỉ cho mo_tep khi đầu vào có ĐỐI TƯỢNG có khóa tep_id; bảng Q1–Q9); e_phan_luong/goi/e_phan_luong/e_phan_luong/quy_trinh.py (lead tách 20/11: mỗi hàm là một ĐIỂM NỐI có chủ sở hữu); e_hoa_don/goi/e_hoa_don/engine.json.
Nhánh này có PL-0…PL-3 (thu 1/1 ĐẠT, 1115 test) + quy_trinh.py + hoa_don.py (PL-7A). Các lát ghép khác chạy SONG SONG ở nhánh khác (PL-4, PL-5, PL-6, PL-8): chỉ sửa ĐÚNG tệp ghi dưới đây; không đổi chữ ký hàm công khai đã có; không sửa kieu.py, loi.py, VIEC.md, CHANGELOG.md.
Sau khi đổi tệp trong goi/: tính lại kiểm kê (python -B e_phan_luong/tests/kiem_bam_goi.py --cap-nhat); đổi engine.json thì chạy python _chung/cong-cu/sinh_danh_muc_engine.py. Năng lực vừa làm thật thì bỏ khỏi CHUA_LAM_CON trong tests/test_pl0_goi.py. Chạy pytest bằng --basetemp trong worktree nếu thư mục tạm bị chặn.
Đạt: 3 lệnh AGENTS.md §5 (thu mọi ví dụ [ĐẠT] mã 0; pytest 0 lỗi; kiem_doc_lap mã 0); dán kết quả thật; ghi "đã kiểm bằng Core giả (CoreGia)".

LÀM LÁT PL-7 — audit.phan_luong_hoa_don@1 (truong → truong), nối sau hoa_don.doc_xml@2 / hoa_don.doc_zip@1 (phiếu §5.4). Tệp được sửa: chay.py (CHỈ thân hàm phan_luong_hoa_don), hoa_don.py, engine.json (chỉ phần năng lực này + chay_thu_demo của nó), test tests/test_pl7_*.py. KHÔNG sửa quy_trinh.py: chỉ gọi quy_trinh.bat_dau và quy_trinh.chay_phan_luong.
1. phan_luong_hoa_don: bat_dau; đầu vào là truong của bước e_hoa_don; có tệp chi tiết (hoa_don.lay_tep_chi_tiet) → viec.mo_tep(tep["tep_id"]) đọc tối đa TOI_DA_BYTE + 1 → lo_tu_chi_tiet_zip; không có → lo_tu_hoa_don (một hóa đơn); ma_module, loai_nghiep_vu, nguong_json từ Cài đặt bước (lô hóa đơn không mang ngưỡng); bytes để băm đầu vào = JSON chuẩn hóa (sort_keys, separators gọn, UTF-8) của trường đầu vào, hoặc bytes tệp chi tiết khi có; quy_trinh.chay_phan_luong(viec, lo, du_lieu, canh_bao_them=["Bỏ N hóa đơn không đọc được"] khi N > 0).
2. engine.json: khai nhan/trường vào của năng lực khớp trường ra của hoa_don.doc_xml@2 và hoa_don.doc_zip@1; chay_thu_demo một hóa đơn DEMO. Danh mục: CHUOI mẫu hoa_don.doc_xml@2 → audit.phan_luong_hoa_don@1 (phiếu §8); script phải báo nối đúng.
Test: XML một hóa đơn; ZIP nhiều hóa đơn qua mo_tep (tệp chi tiết đặt trong đầu vào bằng đối tượng có khóa tep_id, đúng như Core thật); can_kiem_tra → Đỏ CO_DO_CUNG; thiếu tiền tệ → CHUA_RO_TIEN_TE; thiếu nguong_json → THIEU_NGUONG; mã số thuế bán không xuất hiện trong xem_ngan (C4).
```

#### PL-8 — ghép tệp kết quả, màn Admin
```
Đọc AGENTS.md; e_phan_luong/docs/PHIEU-ENGINE-e_phan_luong.md (đủ); e_phan_luong/docs/GIAO-CODEX-e_phan_luong.md §2, §3.2, §4 (Cần Core; bảng Q1–Q9); e_phan_luong/goi/e_phan_luong/e_phan_luong/quy_trinh.py (lead tách 20/11: mỗi hàm là một ĐIỂM NỐI có chủ sở hữu).
Nhánh này có PL-0…PL-3 (thu 1/1 ĐẠT, 1115 test) + quy_trinh.py + xuat_excel.py (PL-8A) + ui/bang_ty_le.js (PL-8B). Các lát ghép khác chạy SONG SONG ở nhánh khác (PL-4, PL-5, PL-6, PL-7): chỉ sửa ĐÚNG tệp ghi dưới đây; không đổi chữ ký hàm công khai đã có; không sửa kieu.py, loi.py, VIEC.md, CHANGELOG.md.
Sau khi đổi tệp trong goi/: tính lại kiểm kê (python -B e_phan_luong/tests/kiem_bam_goi.py --cap-nhat); đổi engine.json thì chạy python _chung/cong-cu/sinh_danh_muc_engine.py. Chạy pytest bằng --basetemp trong worktree nếu thư mục tạm bị chặn.
Đạt: 3 lệnh AGENTS.md §5 (thu mọi ví dụ [ĐẠT] mã 0; pytest 0 lỗi; kiem_doc_lap mã 0); dán kết quả thật; ghi "đã kiểm bằng Core giả (CoreGia)".

LÀM LÁT PL-8 — tệp kết quả: Excel danh sách Đỏ, schema tep_json, màn Admin (phiếu §5.5, §6, C5). Tệp được sửa: quy_trinh.py (CHỈ hàm xuat_ket_qua), xuat_excel.py, xuat_json.py, ui/bang_ty_le.js, engine.json (chỉ giao_dien_quan_tri và mô tả trường tep_ds_do), tests/schema/tep_json.schema.json, test tests/test_pl8_*.py.
1. Môi trường: .venv có openpyxl, et_xmlfile, defusedxml đúng requirements.lock (pip install --require-hashes; không có mạng thì cài từ cache pip hoặc site-packages của .venv tại D:/Claude/engines-wt/e_kiem_excel-ex-6 — ghi rõ cách đã làm).
2. quy_trinh.xuat_ket_qua: có ≥ 1 dòng Đỏ → tep_ds_do = viec.tai_tep_ra("ds-can-kiem.xlsx", xuat_excel.lap_ds_do(...), mime xlsx); không có dòng Đỏ → tep_ds_do null. Giữ nguyên tep_json.
3. tests/schema/tep_json.schema.json: JSON Schema chốt cấu trúc tep_json hiện có (additionalProperties false); test mọi tep_json DEMO hợp schema.
4. engine.json giao_dien_quan_tri theo báo cáo PL-8B: [{"ma":"bang_ty_le","ten":"Bảng tỷ lệ kiểm tra","tep":"ui/bang_ty_le.js","quyen":"admin_core"}] — kiểm doc_phieu của SDK 2.2.0 nhận khai báo này (đúng tên khóa theo MAU-PHIEU-ENGINE.md); không nhận thì KHÔNG khai, ghi "Cần Core" trong báo cáo (SDK 2.2.0 chưa có KttCore.engine — CC-5).
Test: phân luồng lô 500 DEMO → tep_ds_do mở được, đúng số dòng Đỏ, không có tỷ lệ/xác suất/bậc/hạt giống (C5); lô toàn Xanh → tep_ds_do null; khứ hồi người kiểm điền tệp → JSON §5.3 → audit.ghi_ket_qua@1 nhận đúng; tep_json hợp schema; chay_thu_demo vẫn ĐẠT.
```

### 3.4 Đợt 6 — việc con PL-9 (giao 21/11; lưu nguyên bản đã giao)

Nền: nhánh PL-8 sau khi nối đủ PL-4 → PL-8. Ba việc con sở hữu tệp riêng, chạy song song; lead gộp vào nhánh `codex/e_phan_luong-pl-9`, sinh lại kiểm kê và danh mục.

#### PL-9A — mô phỏng 12 tháng, tiêu chí §8
```
Đọc AGENTS.md; e_phan_luong/docs/PHIEU-ENGINE-e_phan_luong.md (đủ, nhất là §4.3, §8, §10); e_phan_luong/docs/GIAO-CODEX-e_phan_luong.md §2 (hợp đồng) và §4 (Q1–Q11 Anh chốt); e_phan_luong/goi/e_phan_luong/README.md.
Nhánh này có đủ PL-0…PL-8 (5 năng lực chạy thật; thu ĐẠT; ~1.500 test). Hai việc con PL-9 khác chạy SONG SONG ở nhánh khác (PL-9B: C4/C5 tổng + đo hiệu năng; PL-9C: đóng gói, NGUON/CHANGELOG/README, kiểm máy sạch). Chỉ tạo/sửa ĐÚNG tệp ghi dưới đây; KHÔNG sửa mã trong goi/ (thấy lỗi mã → mô tả ca tái hiện trong mục "Cần lead").

LÀM VIỆC CON PL-9A — mô phỏng 12 tháng + tiêu chí §8 (tái hiện, tần suất, đồng thời). Tệp được tạo: tests/demo/mo_phong_12_thang.py (script sinh dữ liệu DEMO tất định, hạt giống cố định, chạy lại ra cùng bytes), tests/test_pl9a_mo_phong.py. Chỉ dữ liệu DEMO "Công ty DEMO Ánh Dương".
1. Mô phỏng qua cổng công khai: mỗi tháng (ghim thời gian bằng monkeypatch chot_ky.ky_hien_tai và mọi hàm lấy ngày/giờ mà mã đang dùng) chạy audit.phan_luong@1 rồi audit.ghi_ket_qua@1 bằng CoreGia (cùng một CoreGia suốt 12 tháng để ngăn giữ trạng thái; chốt kỳ tự chạy khi sang tháng). Người kiểm giả: kết quả của dòng Đỏ sinh tất định theo tỷ lệ lỗi của loại (băm SHA-256 của mã nghiệp vụ, không dùng random toàn cục).
2. Ba loại chính: (a) loại SẠCH (0% lỗi), (b) loại LỖI 8% (lỗi nhỏ < SAD), (c) dòng chua_phan_loai. Quy mô DEMO: khoảng 100 nghiệp vụ/loại/tháng cho một khâu (ghi rõ con số dùng).
3. Khẳng định theo §8: loại sạch xuống bậc ĐÚNG tháng mà §4.3 dự tính (tính độc lập trong test bằng Fraction + công thức 1 − 0,05^(1/n) và số mẫu ngẫu nhiên CHON_MAU đã kiểm kể từ lần đổi bậc gần nhất; không gọi lại hàm của gói để tính đáp án); loại lỗi 8% giữ hoặc lên 30% và có nhãn rui_ro_cao khi gặp lỗi ≥ SAD (thêm vài lỗi ≥ SAD có chủ đích) ; chua_phan_loai luôn 30%. Đọc bậc qua xem_ngan("ty_le") (chỉ trong test, không đưa ra trường ra).
4. Ghi rõ trong báo cáo bảng từng tháng: số mẫu ngẫu nhiên đã kiểm, số lỗi, bậc của mỗi loại. Thêm một ca riêng (test có đánh dấu rõ, KHÔNG xfail) chạy quy mô lớn: loại lỗi 8% với khoảng 1.000 mẫu ngẫu nhiên/12 tháng — ghi bậc thực tế quan sát được vào báo cáo (lead đang hỏi Anh về điểm này: cận trên CP với n lớn có thể < 10% nên có thể xuống 20%); test chỉ khẳng định điều đúng theo quy tắc hiện hành, không tự đổi quy tắc.
5. Tái hiện: cùng hạt giống (monkeypatch chon_mau.sinh_hat_giong) + cùng đầu vào + cùng trạng thái ngăn → tep_json giống từng byte (hai CoreGia độc lập).
6. Tần suất: 10.000 dòng, p = 20% (đặt trạng thái ty_le của cặp ở bậc 20% bằng ghi ngăn qua một việc DEMO, hoặc qua chinh_sach_json) → tỷ lệ chọn thực tế trong [19%, 21%].
7. Đồng thời: hai ghi_ket_qua cùng lúc (gay_xung_dot_ngan("ty_le", so_lan=1)) → đúng một lần thử lại, số đếm không lệch, không trùng.
Test nhanh: toàn bộ test_pl9a_mo_phong.py chạy < 120 giây trên máy này (đo, ghi vào báo cáo); ca quy mô lớn có thể đánh dấu pytest.mark.slow nhưng vẫn chạy mặc định nếu < 120 giây.
Đạt: pytest e_phan_luong/tests/test_pl9a_mo_phong.py 0 lỗi; dán kết quả thật; ghi "đã kiểm bằng Core giả (CoreGia)".
```

#### PL-9B — C4/C5 mọi năng lực, đo hiệu năng
```
Đọc AGENTS.md; e_phan_luong/docs/PHIEU-ENGINE-e_phan_luong.md (đủ, nhất là C4, C5, §5, §8); e_phan_luong/docs/GIAO-CODEX-e_phan_luong.md §2 (hợp đồng, §2.4 bảng ngăn) và §4 (Cần Core CC-6: tra_nop_lai đọc từng dòng); e_kiem_excel/tests/do_hieu_nang.py và do_bo_nho.py (mẫu đo).
Nhánh này có đủ PL-0…PL-8 (5 năng lực chạy thật; thu ĐẠT; ~1.500 test). Hai việc con PL-9 khác chạy SONG SONG (PL-9A: mô phỏng 12 tháng; PL-9C: đóng gói, NGUON/CHANGELOG/README, kiểm máy sạch). Chỉ tạo/sửa ĐÚNG tệp ghi dưới đây.

LÀM VIỆC CON PL-9B — kiểm C4/C5 trên MỌI năng lực + đo hiệu năng. Tệp được tạo/sửa: tests/test_pl9b_c4_c5.py, tests/do_hieu_nang.py, tests/test_pl9b_hieu_nang.py; ĐƯỢC sửa e_phan_luong/goi/e_phan_luong/e_phan_luong/ngan_luot.py (CHỈ thân hàm tra_nop_lai, giữ chữ ký và mọi test cũ đạt) nếu số đo ở mục 3 vượt ngân sách. Không sửa tệp khác trong goi/.
1. C4 (tối thiểu dữ liệu): chạy MỌI ví dụ chay_thu_demo + một vòng đủ 5 năng lực (phan_luong JSON/Excel/CSV, chuỗi chuan_bi_phan_loai → tra_loi_ai DEMO dựng tay → phan_luong_sau_ai, phan_luong_hoa_don, ghi_ket_qua có sửa loại và ngoài mẫu) trên cùng CoreGia; đọc xem_ngan của CẢ 6 bảng; khẳng định không ô nào chứa: số tiền (mọi số tiền DEMO đã dùng, dạng chuỗi/thập phân), ngày nghiệp vụ, mã/tên đối tác thô, diễn giải/nội dung, mã số thuế. Băm đối tác 32 ký tự hex được phép. Danh sách cột mỗi bảng khớp đúng §2.4 (không thừa cột).
2. C5 (quyền xem): mọi trường ra, mọi tep_json, mọi tep_ds_do (mở bằng openpyxl), mọi yeu_cau_ai của 5 năng lực không chứa khóa hoặc chữ (bỏ dấu, không phân biệt hoa thường) "ty le", "xac suat", "bac", "hat giong", "he so", không chứa giá trị hạt giống hex, không chứa số dạng phần trăm từ bảng tỷ lệ.
3. Hiệu năng (do_hieu_nang.py là script đo, test_pl9b_hieu_nang.py là ca nhỏ chạy nhanh): đo thời gian và bộ nhớ đỉnh (tracemalloc) của audit.phan_luong@1 với lô JSON 50.000 dòng DEMO (đúng TOI_DA_DONG) ở hai trạng thái: (a) ngăn trống; (b) đã có một lượt trước 50.000 dòng cùng mã (để tra_nop_lai phải tra từng mã — CC-6). Ngân sách: thoi_han_giay của năng lực trong engine.json (300 giây) với dư ≥ 2 lần trên máy này. Thêm đo Excel 50.000 dòng và ghi_ket_qua 5.000 dòng. Ghi bảng số đo thật vào báo cáo (giây, MB). Nếu (b) vượt ngân sách: tối ưu thân tra_nop_lai (ví dụ tìm dong_luot theo lô thay vì từng mã nếu ngăn hỗ trợ loc bằng; giữ đúng ngữ nghĩa Q5) rồi đo lại; không thể đạt → ghi "Cần lead/Cần Core" kèm số đo.
Test nhanh: test_pl9b_c4_c5.py + test_pl9b_hieu_nang.py chạy < 120 giây (ca 50.000 dòng chỉ trong do_hieu_nang.py, không trong pytest mặc định).
Đạt: pytest hai tệp test 0 lỗi; nếu sửa ngan_luot.py thì pytest toàn engine 0 lỗi và tính lại kiểm kê (python -B e_phan_luong/tests/kiem_bam_goi.py --cap-nhat); dán kết quả thật; ghi "đã kiểm bằng Core giả (CoreGia)".
```

#### PL-9C — đóng gói 0.1.0
```
Đọc AGENTS.md; e_phan_luong/docs/PHIEU-ENGINE-e_phan_luong.md (đủ); e_phan_luong/docs/GIAO-CODEX-e_phan_luong.md (đủ, nhất là §4 Cần Core CC-1…CC-6 và Q1–Q11); e_phan_luong/docs/VIEC.md (chỉ đọc); mẫu đóng gói của e_kiem_excel: e_kiem_excel/goi/e_kiem_excel/NGUON.md, CHANGELOG.md, README.md, e_kiem_excel/tests/kiem_may_sach.sh, KIEM-MAY-SACH.cmd, demo/bam-goi.json; _chung/cong-cu/dong_goi.py.
Nhánh này có đủ PL-0…PL-8 (5 năng lực chạy thật; thu ĐẠT; ~1.500 test). Hai việc con PL-9 khác chạy SONG SONG (PL-9A: mô phỏng 12 tháng — tệp test mới; PL-9B: C4/C5 + đo hiệu năng, có thể sửa thân ngan_luot.tra_nop_lai). Chỉ tạo/sửa ĐÚNG tệp ghi dưới đây.

LÀM VIỆC CON PL-9C — đóng gói phát hành 0.1.0. Tệp được sửa/tạo: goi/e_phan_luong/README.md, NGUON.md, CHANGELOG.md, requirements.lock (chỉ rà, giữ đúng hash đã ghim), tests/kiem_may_sach.sh, tests/KIEM-MAY-SACH.cmd, tests/demo/bam-goi.json (nếu mẫu cần), tests/test_pl9c_dong_goi.py; _chung/cong-cu/dong_goi.py (CHỈ thêm "e_phan_luong" vào CAC_ENGINE nếu cần để đóng gói, không đổi hành vi engine khác).
1. README.md: đủ cho người viết module: 5 năng lực, đầu vào/ra, cài đặt bước (bảng khóa, giới hạn), chuỗi mẫu (b) Local AI và hóa đơn, lỗi §7 bằng câu tiếng Việt, khóa chinh_sach_json (gồm toi_thieu_ho_so_doi_tac_moi: mặc định 0 = lượt đầu coi mọi đối tác là mới), cách học từ kết quả kiểm, nộp lại (Q5), chia nhỏ (Q8), trần 20.000 đối tác (Q9). Mục "Đang chờ Core": CC-5 màn Admin bảng tỷ lệ (SDK 2.2.0 từ chối giao_dien_quan_tri, chưa có KttCore.engine) và các điểm CC còn mở theo GIAO-CODEX §4. Ghi rõ: hồ sơ hành vi được cộng trong CÙNG lô nguyên tử với dấu luot (Core giao lại việc không cộng hai lần; chỉ khi một lô có trên 99 loại thì phần dư ghi trước, không nguyên tử). Không có tỷ lệ/xác suất trong phần dành cho người dùng cuối (C5) — phần chính sách dành cho Admin ghi rõ là của Admin.
2. CHANGELOG.md: mục 0.1.0 liệt kê PL-0…PL-9 (mỗi lát 1–3 dòng).
3. NGUON.md: trạng thái hiện hành PL-0…PL-9; nguồn, giấy phép, SHA-256 thư viện (giữ bảng đang có); ghi rằng SHA-256 mọi tệp gói nằm ở sql/kiem_ke.json (tính bằng tests/kiem_bam_goi.py).
4. kiem_may_sach.sh (Linux CI Python 3.11, không mạng, cài wheel offline --require-hashes) và KIEM-MAY-SACH.cmd (Windows, Anh tự chạy; Codex KHÔNG chạy .cmd) theo đúng mẫu e_kiem_excel: cài SDK wheel + requirements.lock vào venv tạm, chép gói, chạy kiem_bam_goi --kiem-ke, kho_tri_thuc_sdk.thu, kiem_doc_lap. Tệp .cmd chỉ ký tự ASCII.
5. Đóng gói bằng _chung/cong-cu/dong_goi.py ra thư mục tạm ngoài repo (không commit tệp zip); test_pl9c_dong_goi.py khẳng định: gói zip tất định (đóng hai lần cùng bytes), có đủ tệp gốc, không có .venv/__pycache__/tệp ngoài gói, kiểm kê khớp.
Sau khi đổi tệp trong goi/: tính lại kiểm kê (python -B e_phan_luong/tests/kiem_bam_goi.py --cap-nhat).
Đạt: 3 lệnh AGENTS.md §5 (thu mọi ví dụ [ĐẠT] mã 0; pytest toàn engine 0 lỗi; kiem_doc_lap mã 0) + kiem_may_sach.sh chạy được trên máy này bằng Git Bash nếu có Python 3.11 (không có thì ghi rõ, không giả kết quả); dán kết quả thật; ghi "đã kiểm bằng Core giả (CoreGia)".
```

Sau rà soát độc lập PL-4…PL-8 (agent Sonnet, 21/11: 1 cao, 7 vừa, 4 thấp; không lỗi cao về tiền/C4/C5) lead giao thêm PL-9D, PL-9E và giao lại PL-9B lần 2. Hai điểm cần Anh quyết (mã hóa đơn gồm người bán; quy tắc CP ở cỡ mẫu lớn) và CC-7 ghi ở §4.

#### PL-9B lần 2 — nới đúng ngoại lệ C4/C5 của hợp đồng, đo hiệu năng bằng đếm lần gọi + ngăn giả có chỉ mục
```
Tiếp việc con PL-9B trong cùng worktree (giữ 3 tệp bạn đã tạo: tests/test_pl9b_c4_c5.py, tests/do_hieu_nang.py, tests/test_pl9b_hieu_nang.py). Lead đã đọc báo cáo lần 1 và chốt:
1. C4: ho_so_hanh_vi.tong_7_ngay là NGOẠI LỆ Anh duyệt ở phiếu §4.1 ("Hồ sơ hành vi chỉ giữ tổng tiền theo (băm đối tác, ngày) trong 7 ngày gần nhất, không giữ mã giao dịch"). Test C4 bỏ cột này khỏi phép dò số tiền/ngày nhưng kiểm cấu trúc: JSON object, khóa ngoài là băm 32 ký tự hex, khóa trong là ngày ISO, ≤ 7 ngày mỗi băm, giá trị là chuỗi thập phân ≥ 0; không có đối tác thô/diễn giải/mã giao dịch ở đâu trong cột. Mọi cột/bảng khác giữ nguyên phép dò.
2. C5: tên trường thuộc hợp đồng đầu ra được phép: bam_hat_giong (chỉ là SHA-256 của hạt giống, không phải hạt giống) và so_cap_doi_bac (số cặp đổi bậc, không lộ bậc). Test vẫn cấm GIÁ TRỊ hạt giống hex, mọi khóa/chữ khác chứa "ty le", "xac suat", "bac", "hat giong", "he so" và số phần trăm từ bảng tỷ lệ; danh sách cho phép ghi rõ trong test kèm lý do.
3. Hiệu năng: CoreGia quét tuyến tính và sao chép ngăn nên không dùng được để đo 50.000 dòng. Đổi cách đo trong do_hieu_nang.py (script, không chạy trong pytest mặc định) và test nhỏ trong test_pl9b_hieu_nang.py:
   (a) ĐẾM số lần gọi Core qua ngăn (doc, tim, lô ghi) và tải tệp của từng năng lực, đo thật với N = 1.000, 5.000, 10.000 dòng trên CoreGia, ở hai trạng thái (ngăn trống; đã có một lượt trước cùng mã để tra_nop_lai phải tra); ngoại suy tuyến tính lên 50.000 và ghi rõ là "ước tính".
   (b) Thời gian máy của chính engine với 50.000 dòng: dùng một ngăn giả CHỈ TRONG TEST có chỉ mục theo khóa (dict), đúng ngữ nghĩa doc/tim(loc bằng, sap_xep, gioi_han, tiep)/lô nguyên tử/CAS row_version đủ cho các đường engine dùng — không sửa SDK, không sửa gói. Đo giây + MB đỉnh (tracemalloc) cho phan_luong JSON, phan_luong Excel 4 cột, ghi_ket_qua 5.000 dòng.
   (c) Bảng ước tính thời gian trên Core thật = (b) + số lần gọi (a) × độ trễ mỗi lần gọi giả định 2 / 5 / 10 ms (ghi rõ "ước tính", chưa đo trên Core thật), so với thoi_han_giay 300 giây. Kết luận: cỡ lô tối đa an toàn ước tính theo mỗi độ trễ, và tra_nop_lai (gọi tim từng mã — CC-6) chiếm bao nhiêu phần số lần gọi.
   (d) Nếu ước tính cho thấy vượt 300 giây ở 5 ms/lần với 50.000 dòng: KHÔNG tự đổi thiết kế ngăn; được tối ưu thân tra_nop_lai trong ngan_luot.py chỉ khi giữ đúng ngữ nghĩa Q5 và giảm được số lần gọi mà không cần cửa mới của Core; không thì ghi "Cần Core" (lọc tim theo danh sách giá trị, CC-6) kèm số liệu.
Đạt: pytest hai tệp test 0 lỗi, < 120 giây; nếu sửa ngan_luot.py thì pytest toàn engine 0 lỗi và tính lại kiểm kê; dán kết quả thật; ghi "đã kiểm bằng Core giả (CoreGia)".
```

#### PL-9D — sửa sau rà soát: hồ sơ hành vi, chốt kỳ
```
Đọc AGENTS.md; e_phan_luong/docs/PHIEU-ENGINE-e_phan_luong.md §4.1 (chống chia nhỏ: "từng khoản < TE nhưng tổng ≥ TE"), §4.4–§4.5, §6 (C4), §7; e_phan_luong/docs/GIAO-CODEX-e_phan_luong.md §2 (hợp đồng, §2.4 bảng ngăn) và §4 (Q1, Q8, Q9); e_phan_luong/goi/e_phan_luong/README.md.
Nhánh này có đủ PL-0…PL-8. Việc con khác chạy SONG SONG: PL-9B (chỉ thân ngan_luot.tra_nop_lai + test PL-9B), PL-9E (xuat_excel.py, doc_bang.py, doc_lo.py). Chỉ tạo/sửa ĐÚNG tệp ghi dưới đây; không đổi chữ ký hàm công khai đang có (được THÊM tham số từ khóa có mặc định); không sửa README/CHANGELOG/NGUON/VIEC.md (lead cập nhật).

LÀM VIỆC CON PL-9D — sửa sau rà soát độc lập PL-4…PL-8, phần hồ sơ hành vi và chốt kỳ. Tệp được sửa: e_phan_luong/goi/e_phan_luong/e_phan_luong/{ho_so.py, ngan_ho_so.py, chot_ky.py, ngan_chung.py (chỉ THÊM hàm), quy_trinh.py (CHỈ hàm chay_phan_luong)}, sql/001_tao_ngan.sql và engine.json (CHỈ thêm cột ở mục 3; engine 0.1.0 chưa phát hành, chưa cài lên Core thật nên sửa thẳng migration 001), test mới tests/test_pl9d_*.py; được sửa kỳ vọng test cũ nếu hành vi đổi đúng các mục dưới (ghi rõ trong báo cáo, không nới mục đích test).
1. (vừa) Chỉ khoản < TE vào lịch sử chia nhỏ: ho_so.cong nhận thêm te: Decimal | None (đơn vị = tiền tệ ngưỡng); dòng có tien_ss.so ≥ te KHÔNG cộng vào tong_ngay (vẫn cộng bieu_do, doi_tac). quy_trinh.chay_phan_luong truyền TE của lô. Test: lượt 1 đối tác A một khoản ≥ TE (Đỏ VUOT_TE); lượt 2 A một khoản nhỏ trong 7 ngày → không NGHI_CHIA_NHO.
2. (vừa) Ngày tương lai không phá cửa sổ: khi cộng, bỏ khỏi tong_ngay các dòng có ngày > ngày xử lý (giờ Việt Nam UTC+7, dùng cùng nguồn giờ với chot_ky.ky_hien_tai để test ghim được) + 1 ngày; mốc cắt cửa sổ tính từ ngày lớn nhất còn giữ. lam_moi cũng bỏ các ngày > ngày xử lý + 1 đã lỡ lưu. Test: cong với một dòng năm 2062 và một dòng hôm nay → dòng hôm nay vẫn còn; hồ sơ cũ có ngày 2062 → sau lam_moi lịch sử hôm nay không bị cắt.
3. (vừa) Tiền tệ hồ sơ: thêm cột tien_te (van_ban, ≤ 3, mã ISO) vào bảng ho_so_hanh_vi (sql/001_tao_ngan.sql có COMMENT tiếng Việt như các cột khác; engine.json ngan_du_lieu truong). Hồ sơ ghi tiền tệ ngưỡng của lô đã cộng (mọi số trong tong_ngay/bieu_do theo đơn vị này). Khi đọc: hồ sơ có tien_te khác tiền tệ ngưỡng của lô mới → coi như hồ sơ trống cho lượt này (không dùng tong_ngay, bieu_do, phan_vi_95; DOI_TAC_MOI vẫn theo tập băm đối tác vì không phụ thuộc tiền tệ) và khi cộng thì bắt đầu lại tong_ngay + bieu_do theo tiền tệ mới, giữ tập đối tác; thêm câu cảnh báo tiếng Việt vào canh_bao_them (không chứa tỷ lệ, C5). Hồ sơ cũ chưa có tien_te → nhận tiền tệ của lô đầu tiên ghi vào. Test VND rồi USD.
4. (thấp) Q9 hiện lên màn engine: tính số đối tác sẽ bị bỏ vì trần 20.000 TRƯỚC xuat_ket_qua (chạy ho_so.cong trên ảnh chụp đã đọc, thuần, không ghi ngăn) và nếu > 0 đưa câu cảnh báo tiếng Việt vào canh_bao_them; vẫn giữ logging. Không lộ băm/đối tác.
5. (vừa) Chốt kỳ không chặn cả engine: chot_ky._tinh_lai đang dùng ngan_chung.tim_tat_ca (trần 200.000, giữ cả danh sách). Thêm ngan_chung.dem_theo_trang(viec, bang, loc, ham) (duyệt trang như tim_tat_ca, gọi ham(ban_ghi) từng bản ghi, không giữ danh sách, không trần) và dùng nó để đếm. Ngoài ra lỗi của MỘT cặp khi chốt không làm hỏng cả việc: ghi logging, bỏ qua cặp đó lượt này (lượt sau thử lại), trừ NGAN_BAN vẫn ném để Core thử lại. Test bằng CoreGia (gay_xung_dot_ngan, ghim giờ).
Sau khi đổi tệp trong goi/: tính lại kiểm kê (python -B e_phan_luong/tests/kiem_bam_goi.py --cap-nhat); đổi engine.json thì chạy python _chung/cong-cu/sinh_danh_muc_engine.py.
Đạt: 3 lệnh AGENTS.md §5 (thu mọi ví dụ [ĐẠT] mã 0; pytest toàn engine 0 lỗi; kiem_doc_lap mã 0); dán kết quả thật; ghi "đã kiểm bằng Core giả (CoreGia)".
```

#### PL-9E — sửa sau rà soát: đọc tệp, xuất Excel
```
Đọc AGENTS.md; e_phan_luong/docs/PHIEU-ENGINE-e_phan_luong.md §5 (đầu vào, khuôn cột Excel/CSV), §5.5 (tệp ra), §7 (lỗi); e_phan_luong/docs/GIAO-CODEX-e_phan_luong.md §2 (hợp đồng); e_phan_luong/goi/e_phan_luong/README.md.
Nhánh này có đủ PL-0…PL-8. Việc con khác chạy SONG SONG: PL-9B (chỉ thân ngan_luot.tra_nop_lai), PL-9D (ho_so.py, ngan_ho_so.py, chot_ky.py, ngan_chung.py, quy_trinh.chay_phan_luong, sql, engine.json). Chỉ tạo/sửa ĐÚNG tệp ghi dưới đây; không đổi chữ ký hàm công khai đang có; không sửa README/CHANGELOG/NGUON/VIEC.md (lead cập nhật).

LÀM VIỆC CON PL-9E — sửa sau rà soát độc lập PL-4…PL-8, phần đọc tệp và xuất Excel. Tệp được sửa: e_phan_luong/goi/e_phan_luong/e_phan_luong/{xuat_excel.py, doc_bang.py, doc_lo.py}, test mới tests/test_pl9e_*.py; được sửa kỳ vọng test cũ nếu hành vi đổi đúng các mục dưới (ghi rõ, không nới mục đích test).
1. (CAO) xuat_excel.lap_ds_do chậm theo bình phương số dòng Đỏ: vòng lặp gọi ws.max_row mỗi dòng (openpyxl 3.1.5 duyệt toàn bộ ô mỗi lần). Dùng biến đếm dòng; tính vùng DataValidation/auto_filter từ biến đếm. Test: 20.000 dòng Đỏ DEMO dựng < 30 giây trên máy này (đo, ghi số); nội dung tệp giống hệt bản cũ với lô nhỏ (so bytes hoặc so từng ô).
2. (vừa) doc_bang: khuôn cột có so_tien_quy_doi nhưng KHÔNG có cột tien_te_quy_doi thì không được lấy tham số tien_te (dự phòng của so_tien) làm tiền tệ quy đổi. Coi như không có số quy đổi (dòng xét theo so_tien như JSON thiếu so_tien_quy_doi) — không bao giờ tự gán tiền tệ. Test: tien_te="VND", cột quy đổi không có tiền tệ → so_tien_quy_doi None.
3. (thấp) doc_lo: mã nghiệp vụ toàn khoảng trắng → DU_LIEU_KHONG_HOP_LE ngay khi đọc (như mã rỗng), áp cho mọi đường vào (JSON, bảng, hóa đơn dùng doc_lo). Test: ma=" " co_do_cung=true bị từ chối ở bước đọc, không phải ở bước Excel.
4. (thấp) doc_bang dễ dùng hơn mà vẫn an toàn: (a) trần ô O_TOI_DA đồng bộ với trần dòng: đủ cho TOI_DA_DONG dòng × số cột của khuôn (giữ trần byte và chặn vùng ô thưa như cũ); (b) ô số kiểu float từ Excel (ví dụ 0.30000000000000004, 1234.5600000000002) làm tròn về 15 chữ số có nghĩa trước khi kiểm tối đa 6 chữ số lẻ; số thật sự có > 6 chữ số lẻ sau khi làm tròn vẫn từ chối. Không dùng float trong tính toán tiền sau bước đọc (Decimal). Test cả hai.
Sau khi đổi tệp trong goi/: tính lại kiểm kê (python -B e_phan_luong/tests/kiem_bam_goi.py --cap-nhat).
Đạt: 3 lệnh AGENTS.md §5 (thu mọi ví dụ [ĐẠT] mã 0; pytest toàn engine 0 lỗi; kiem_doc_lap mã 0); dán kết quả thật; ghi "đã kiểm bằng Core giả (CoreGia)".
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
| Q10 | Dưới SAD khi cặp đang kiểm 100% | Vẫn 2% × hệ số; 100% chỉ áp vùng chọn mẫu |
| Q11 | Chưa phân loại, số tiền dưới SAD | 2% × hệ số như mọi loại; 30% cố định chỉ cho vùng chọn mẫu |
