# Phiếu engine — `e_phan_luong` (Phân luồng kiểm tra — Audit)

*Lập 20/11/2026 theo yêu cầu của Anh Dũng. **Trạng thái: ĐÃ DUYỆT TIẾN HÀNH 20/11/2026.** Anh đã chốt toàn bộ câu hỏi (bảng quyết định §10); lead Claude Code lập lệnh giao từng lát và code theo phiếu này. Mọi con số % và hệ số là **đề xuất của lead đã được Anh duyệt** (C2, C3), chưa phải số đo; giờ công là **ước tính, chưa đo**.*

*Căn cứ đã đọc (repo `tridungftu/engines`, commit `d12eea0`, 20/11/2026): `AGENTS.md`; SDK 2.2.0 (`MAU-PHIEU-ENGINE.md`, `HUONG-DAN-VIET-ENGINE.md`, `THAY-DOI-2.2.0.md`, `API-CORE-v1.md`, `HUONG-DAN-VIET-MODULE.md`, mẫu `engine-demo/e_demo_ngan/`); `_chung/docs/DE-NGHI-SDK-2.1.md`, `CHUYEN-SDK-2.2.md`, `QUYET-DINH-ANH-20261115*.md`, `LOAI-DU-LIEU-RIENG.md` (§2.2–2.3 `yeu_cau_ai`, `tra_loi_ai`, trường `chuyen_tiep`), `DANH-MUC-ENGINE-CHO-MODULE.md`; `e_kiem_excel/docs/PHIEU-ENGINE-e_kiem_excel.md` (mẫu phiếu, quy ước tiền §4.3).*

---

## 1. Kết luận

- **Engine mới `e_phan_luong`, 5 năng lực, ngăn riêng theo pháp nhân** (SDK 2.2.0). Engine chia từng nghiệp vụ vào **Đỏ** (người phải kiểm trước khi duyệt) hoặc **Xanh** (cho qua), mỗi dòng có lý do:

| Năng lực | Nhận → Trả | Dùng khi |
|---|---|---|
| `audit.phan_luong@1` | `tep` → `truong` | Lô JSON/Excel/CSV, phân loại bằng quy tắc hoặc module đã gán loại |
| `audit.chuan_bi_phan_loai@1` | `tep` → `yeu_cau_ai` | Bước 1 của chuỗi có Local AI: quy tắc trước, dòng chưa khớp gửi AI |
| `audit.phan_luong_sau_ai@1` | `tra_loi_ai` → `truong` | Bước 3 của chuỗi có Local AI: nhận loại AI gán rồi phân luồng |
| `audit.phan_luong_hoa_don@1` | `truong` → `truong` | Nối sau `hoa_don.doc_xml@2` / `hoa_don.doc_zip@1` |
| `audit.ghi_ket_qua@1` | `tep` → `truong` | Nhận kết quả người kiểm → cập nhật thống kê, tỷ lệ |

- **Đợt này chỉ dựng engine, kiểm bằng DEMO** (Anh chốt C1a); module gắn sau. §3 là hướng dẫn nhúng để module làm theo.
- **Quyết định theo 3 lớp:** (1) ngưỡng PM/TE/SAD → (2) tỷ lệ kiểm theo **khâu × loại nghiệp vụ**, tự học từ kết quả kiểm → (3) chọn ngẫu nhiên tái hiện được bằng SHA-256.
- **Phân loại nghiệp vụ** (Anh chốt C1b–C1d): quy tắc từ khóa trên trường nội dung do Admin chọn; dòng không khớp gửi **Local AI** (AI chỉ được chọn trong danh mục loại); không phân loại được → loại `chua_phan_loai`, kiểm **30% cố định**.
- **Tự học, cập nhật định kỳ:** kết quả kiểm cập nhật tỷ lệ ngay; mỗi lượt phân tích cập nhật hồ sơ hành vi (số liệu gộp, không lưu chi tiết giao dịch); chốt kỳ tháng ở lượt đầu tiên của tháng mới.
- **Ngăn engine giữ tối thiểu** (Anh chốt C4): mã module, mã giao dịch, lý do (kèm khóa kỹ thuật lượt/khâu); 400 ngày. Chi tiết giao dịch nằm ở ngăn module.
- **Quyền xem phân tầng** (C5): engine không trả tỷ lệ hay xác suất trong kết quả cho người duyệt; tỷ lệ và mã ngẫu nhiên chỉ xem ở màn engine (Admin).
- **An toàn:** thiếu dữ liệu để so ngưỡng → Đỏ kèm lý do, không đoán; không tự gán VND; AI chỉ Local.
- **Thư viện ngoài:** `openpyxl` + `et_xmlfile` + `defusedxml` (đọc Excel), ghim cùng phiên bản `e_kiem_excel`. Thống kê bằng thư viện chuẩn.
- **Giờ công: 48 giờ, ƯỚC TÍNH, chưa đo** (§9).

## 2. Phạm vi

| Làm | Không làm |
|---|---|
| Phân luồng Đỏ/Xanh từng nghiệp vụ, theo khâu duyệt | Kiểm nội dung chứng từ: việc của người kiểm hoặc engine khác |
| Ngưỡng PM/TE/SAD, chống chia nhỏ né ngưỡng | Tính PM/TE/SAD: Anh/KTT nhập, module truyền |
| Phân loại bằng quy tắc + Local AI | Gọi thẳng `e_hoi_ai` (Core nối chuỗi); dùng Cloud AI |
| Học tỷ lệ theo khâu × loại, xếp hạng rủi ro | Đọc CSDL phần mềm kế toán |
| Đọc JSON chuẩn, `.xlsx`, CSV UTF-8 theo khuôn cột | `.xls` cũ, PDF |
| Nối sau `e_hoa_don` | Lưu chi tiết giao dịch trong ngăn engine |
| Trả tệp JSON, Excel danh sách Đỏ | Chặn nút Duyệt, phân quyền người xem: module làm |

## 3. Cách nhúng vào module (hướng dẫn cho module làm sau)

```
Chứng từ chờ duyệt ở khâu K
   └─ module lập JSON lô (§5.1) ─→ nút "Kiểm tra cảnh báo – khâu K"
        └─ Core chạy quy trình (Cài đặt bước: khau = K), một trong hai:
             (a) audit.phan_luong@1
             (b) audit.chuan_bi_phan_loai@1 → ai.hoi_theo_yeu_cau@1 → audit.phan_luong_sau_ai@1
        └─ quy_trinh.xong → ghép trường ra vào ngăn module
             └─ module: cờ Đỏ/Xanh + lý do; Đỏ → người duyệt phải mở cảnh báo trước khi Duyệt
Người kiểm ghi đạt/sai (+ loại đúng nếu loại bị gán sai) trong module
   └─ module lập JSON kết quả (§5.3) ─→ nút "Gửi kết quả kiểm" → audit.ghi_ket_qua@1
```

- **Mỗi khâu một nút, một quy trình** (Anh chốt: thống kê riêng từng khâu). Mã khâu do module đặt, ví dụ `kt_kiem`, `ktt_duyet`, `cfo_duyet`.
- **Quyền xem (C5) do module thực thi:** người lập không thấy luồng; người duyệt thấy luồng + lý do của chứng từ mình duyệt; module không hiển thị bảng tỷ lệ. Engine hỗ trợ bằng cách **không** đưa tỷ lệ, xác suất vào trường ra và tệp kết quả.
- **Cần Core kiểm ở PL-0:** chạy nút bằng tệp module tự lập (Blob JSON gửi multipart), không qua hộp chọn tệp. Không được → ghi "Cần Core" trong `VIEC.md`.

## 4. Thuật toán

### 4.1 Lớp 1 — Ngưỡng tiền (Anh chốt 2A: PM, TE, SAD)

- **Nguồn ngưỡng:** khối `nguong` trong tệp JSON (theo pháp nhân + kỳ) thắng Cài đặt bước `nguong_json`; không có cả hai → `THIEU_NGUONG`. Ngưỡng kèm tiền tệ; kiểm `SAD < TE ≤ PM`, cùng tiền tệ.
- **So tiền:** dùng `so_tien_quy_doi` (cùng tiền tệ ngưỡng) nếu có, ngược lại `so_tien` khi cùng tiền tệ. Khác tiền tệ, không có quy đổi → **Đỏ** `CHUA_QUY_DOI`.

| Vùng | Điều kiện | Xử lý |
|---|---|---|
| Bắt buộc | số tiền ≥ TE | **Đỏ** 100%, lý do `VUOT_TE` (≥ PM: `VUOT_PM`) |
| Chọn mẫu | SAD ≤ số tiền < TE | Lớp 2 + 3 |
| Dưới SAD | số tiền < SAD | Anh chốt 6A: chọn với tỷ lệ sàn `ty_le_duoi_sad` = 2% |

- **Chống chia nhỏ:** gom theo (đối tác, khâu, cửa sổ 7 ngày) trong lô và trong hồ sơ hành vi; từng khoản < TE nhưng tổng ≥ TE → cả nhóm **Đỏ** `NGHI_CHIA_NHO`. Hồ sơ hành vi chỉ giữ **tổng tiền theo (băm đối tác, ngày)** trong 7 ngày gần nhất, không giữ mã giao dịch.
- **Cờ đỏ cứng do module truyền** (`co_do_cung: true`) → Đỏ `CO_DO_CUNG`.

### 4.2 Phân loại nghiệp vụ (Anh chốt C1b–C1d)

Thứ tự gán loại cho mỗi dòng, dừng ở bước đầu tiên có kết quả:

1. **Module đã gán** `loai` trong JSON → dùng, phải nằm trong `danh_muc_loai_json`.
2. **Quy tắc từ khóa:** Cài đặt bước `truong_phan_loai` chọn trường nội dung (ví dụ `dien_giai`, `tai_khoan_no`, `tai_khoan_co`, hoặc một khóa trong `thuoc_tinh`); `bo_phan_loai_json` so từ khóa (bỏ dấu, chữ thường), cùng định dạng điều kiện `tat_ca`/`khong_co`/`=tu`/`#` của `e_kiem_excel` §4.1.1, không nhận biểu thức chính quy. Xét theo thứ tự, khớp đầu tiên thì dừng.
3. **Local AI** (chỉ chuỗi (b) §3):
   - `audit.chuan_bi_phan_loai@1` lập `yeu_cau_ai`: `tai_lieu` = danh sách giá trị trường nội dung **đã khử trùng** của các dòng chưa có loại, mỗi giá trị một chỉ số; prompt lấy từ Cài đặt bước (`ma_prompt`, `phien_ban_prompt`, `prompt` — thuộc module); `khuon_tra_loi` do engine dựng, `loai` là **enum** đúng danh mục: `{"phan_loai":[{"chi_so":int,"loai":enum,"tin_cay":0..1}]}`.
   - Lô đã chuẩn hóa + kết quả quy tắc tải lên Core bằng `viec.tai_tep_ra`; `chuyen_tiep` chỉ chứa tham chiếu tệp + băm + mã khâu (≤ 4 KiB, trần 64 KiB).
   - `audit.phan_luong_sau_ai@1` mở lại tệp bằng `viec.mo_tep` (PL-0 kiểm được không), kiểm băm, kiểm `nha_cung_cap = "local"` (khác → `KHONG_PHAI_LOCAL`), kiểm chỉ số và enum; `tin_cay < nguong_tin_cay` (mặc định 0,7) → chưa phân loại.
   - AI trả `khong_thay_can_cu`, sai khuôn → mọi dòng chờ AI thành chưa phân loại, có cảnh báo; **không** báo lỗi cả lượt.
   - Không dòng nào cần AI → bước chuẩn bị vẫn trả `yeu_cau_ai` với `tai_lieu` rỗng và cờ `khong_can_ai` trong `chuyen_tiep`; bước sau bỏ qua kết quả AI.
4. **Không có kết quả** → loại `chua_phan_loai`: kiểm **30% cố định, không xuống bậc**; vẫn nhân hệ số cờ, vẫn áp lớp 1.

- Mỗi dòng ghi nguồn loại: `module` / `quy_tac` / `ai` / `chua_phan_loai` (trong tệp kết quả, không lưu ngăn).
- **Học từ sửa loại:** người kiểm ghi `loai_dung` trong §5.3 → kết quả kiểm tính cho **loại đúng**; engine đếm số lần sai loại theo nguồn (`quy_tac`, `ai`) và hiện ở màn engine để Admin sửa bộ quy tắc/prompt.

### 4.3 Lớp 2 — Tỷ lệ theo khâu × loại (Anh chốt 4A, 5A, C2)

- Khởi đầu **30%** cho mọi cặp (khâu, loại) mới.
- **Bậc thang `30% → 20% → 10% → 5%` (sàn)**, không về 0. Xuống bậc khi, kể từ lần đổi bậc gần nhất, đủ mẫu ngẫu nhiên đã kiểm và **cận trên một phía 95% Clopper-Pearson** ≤ ngưỡng:

| Đổi bậc | Cận trên ≤ | Mẫu sạch tối thiểu (0 lỗi), theo `1 − 0,05^(1/n)` |
|---|---|---|
| 30% → 20% | 10% | 30 (9,50%) |
| 20% → 10% | 5% | 60 (4,87%) |
| 10% → 5% | 3% | 100 (2,95%) |

- **Lên bậc:** lỗi < SAD → lên 1 bậc; lỗi ≥ SAD → về 30% + nhãn `rui_ro_cao`; lỗi ≥ TE → **100%** tới khi đạt 30 mẫu sạch rồi về 30%; lỗi ở nghiệp vụ Xanh (ngoài mẫu) → về 30% + nhãn `loi_ngoai_mau`.
- **Ước lượng chỉ dùng mẫu ngẫu nhiên** (`CHON_MAU`); lỗi từ mọi nguồn đều kích hoạt lên bậc.
- **Cửa sổ 12 tháng:** `ket_qua_kiem` có `giu_toi_da_ngay: 365`; số đếm tính lại khi chốt kỳ.
- **Xếp hạng rủi ro:** điểm = cận trên 95% tỷ lệ lỗi 12 tháng; `rui_ro_cao` khi điểm > 10% hoặc có lỗi ≥ SAD trong 12 tháng.
- `chinh_sach_json` (Cài đặt bước) cho Admin chỉnh mức bậc, ngưỡng, hệ số; trống = bộ Anh đã duyệt.

### 4.4 Lớp 3 — Chọn ngẫu nhiên tái hiện được (Anh chốt C3)

- `p = min(1, max(san, p_bac(khau, loai) × Π he_so_co))`.

| Cờ | Điều kiện | Hệ số |
|---|---|---|
| `SO_TIEN_BAT_THUONG` | > phân vị 95 của loại (cần ≥ 50 nghiệp vụ trong hồ sơ) | × 2 |
| `DOI_TAC_MOI` | đối tác chưa gặp ở loại này trong 12 tháng | × 2 |
| `SO_TRON` | chia hết 10.000.000 (đơn vị ngưỡng) | × 1,5 |
| `NGAY_NGHI` | thứ 7, chủ nhật | × 1,5 |
| `CUOI_KY` | 3 ngày cuối tháng | × 1,5 |
| `NHAP_TAY` | module truyền `nhap_tay: true` | × 1,5 |

- Mỗi lượt sinh `hat_giong` 32 byte (`secrets`). Dòng **Đỏ** `CHON_MAU` khi `int(SHA256(hat_giong ‖ ma_module ‖ khau ‖ ma)) / 2^256 < p`; không bị chọn → Xanh `KHONG_CHON`.
- `hat_giong` lưu ở bảng lượt (cần để kiểm toán viên chạy lại); tệp kết quả chỉ có `bam_hat_giong`.
- **Nộp lại cùng mã ở cùng khâu:** lần trước Đỏ → giữ Đỏ `NOP_LAI` (không cho nộp lại tới khi ra Xanh); lần trước Xanh → chạy lại bình thường với hạt giống mới.

### 4.5 Cập nhật thống kê định kỳ (Anh chốt 3A)

| Lúc | Engine làm |
|---|---|
| Mỗi lượt phân luồng | Đọc bảng tỷ lệ + hồ sơ hành vi; sau đó cộng vào hồ sơ hành vi (khâu, loại): số nghiệp vụ, biểu đồ tần suất số tiền thang log, băm đối tác, tổng tiền theo (băm đối tác, ngày) 7 ngày |
| Mỗi `ghi_ket_qua` | Ghi kết quả từng dòng, cập nhật số mẫu/lỗi, đổi bậc — hiệu lực ngay lượt sau |
| Lượt đầu tiên của tháng mới (bất kỳ năng lực) | **Chốt kỳ:** tính lại số đếm 12 tháng, chụp bảng tỷ lệ vào `chot_ky`, làm mới hồ sơ hành vi theo 12 tháng |

- Ghi ngăn bằng lô nguyên tử; `NganXungDot` → thử lại tối đa 3 lần, quá thì `NGAN_BAN` (`thu_lai_duoc=True`). Chốt kỳ dùng `lay_hoac_tao` trên (kỳ, khâu, loại) để chỉ chốt một lần.

## 5. Dữ liệu vào / ra

### 5.1 JSON lô nghiệp vụ

```json
{"phien_ban": 1, "ma_module": "demo_thanh_toan", "ky": "2026-11",
 "nguong": {"pm": {"so": "5000000000", "tien_te": "VND"},
            "te": {"so": "3000000000", "tien_te": "VND"},
            "sad": {"so": "250000000", "tien_te": "VND"}},
 "nghiep_vu": [
   {"ma": "PC-DEMO-0001", "loai": null, "ngay": "2026-10-30",
    "so_tien": {"so": "1000000", "tien_te": "VND"}, "so_tien_quy_doi": null,
    "doi_tac": "DEMO-NCC-01", "dien_giai": "Thanh toán DEMO đợt 1",
    "tai_khoan_no": "331", "tai_khoan_co": "1121",
    "nhap_tay": false, "co_do_cung": false, "thuoc_tinh": {}}
 ]}
```

- Bắt buộc: `ma_module`, `ma`, `ngay`, `so_tien`. `doi_tac` là **mã**, engine chỉ giữ băm. Trường nội dung chỉ dùng trong lúc chạy, **không lưu ngăn**.
- Ngưỡng trong ví dụ là **DEMO**. Số tiền chuỗi thập phân, xử lý bằng `Decimal`.
- Trần: ≤ 20 MiB, ≤ 50.000 dòng/lô; mã trùng trong lô → `DU_LIEU_KHONG_HOP_LE`.

### 5.2 Excel / CSV theo khuôn cột

- `khuon_cot_json`: ánh xạ cột → trường §5.1 theo từ khóa tiêu đề (bỏ dấu), định dạng như khuôn `tong_quat` của `e_kiem_excel` §4.2. `.xlsx` đọc giá trị đã lưu (`read_only`, `data_only`); CSV UTF-8 (có/không BOM), phân cách `,` hoặc `;`.
- `ma_module` và ngưỡng lấy từ Cài đặt bước (`ma_module`, `nguong_json`) — bắt buộc với Excel/CSV.
- Không có cột tiền tệ và không có `tien_te` → dòng Đỏ `CHUA_RO_TIEN_TE`.

### 5.3 JSON kết quả kiểm (`audit.ghi_ket_qua@1`)

```json
{"phien_ban": 1, "ma_module": "demo_thanh_toan", "ket_qua": [
  {"ma_luot": "PL-…", "ma": "PC-DEMO-0001", "khau": "ktt_duyet",
   "ket_qua": "dat|sai|khong_kiem", "so_tien_sai": {"so": "0", "tien_te": "VND"},
   "loai_dung": null}]}
```

- Kiểm `ma_luot` có thật và dòng thuộc lượt; không thuộc lượt → `ngoai_mau`. Gửi trùng (lượt + mã + khâu) → bỏ qua, đếm `so_trung`. Người kiểm, ghi chú: module giữ, không gửi engine.

### 5.4 Nối sau `e_hoa_don`

- `doc_xml@2`: một hóa đơn = một nghiệp vụ; `ma` = mẫu số + ký hiệu + số; `so_tien` = `tong_thanh_toan`; `doi_tac` = băm `ma_so_thue_ban`; `can_kiem_tra = true` → cờ đỏ cứng.
- `doc_zip@1`: đọc tệp `chi_tiet_nguon` bằng `viec.mo_tep` để phân luồng từng hóa đơn; PL-0 kiểm, không được → chỉ hỗ trợ `doc_xml@2`, ghi "Cần Core".
- `ma_module`, `loai_nghiep_vu` (ví dụ `hoa_don_dau_vao`), `nguong_json` từ Cài đặt bước.

### 5.5 Trường ra (mọi năng lực phân luồng)

| `ma` | `ten` | `kieu` | Ghi chú |
|---|---|---|---|
| `ma_luot` | Mã lượt phân luồng | `van_ban` | Dùng khi gửi kết quả kiểm |
| `luong` | Luồng | `van_ban` | `do` nếu có ≥ 1 dòng Đỏ, ngược lại `xanh` |
| `can_nguoi_kiem` | Cần người kiểm | `co_khong` | |
| `canh_bao` | Cảnh báo | `van_ban` | ≤ 500 ký tự, chỉ lý do, **không có tỷ lệ** |
| `so_nghiep_vu`, `so_do`, `so_do_bat_buoc`, `so_do_chon_mau`, `so_xanh`, `so_chua_phan_loai` | Số đếm | `so` | |
| `tong_tien_do` | Tổng tiền luồng Đỏ | `so_tien` | `null` khi lẫn tiền tệ chưa quy đổi |
| `tep_json` | Kết quả chi tiết | `tep` | Mỗi dòng: mã, luồng, lý do, cờ, nguồn loại; **không có xác suất/tỷ lệ** |
| `tep_ds_do` | Danh sách cần kiểm (Excel) | `tep` | Dòng Đỏ, cột lý do, cột trống ghi kết quả + loại đúng |
| `bam_hat_giong`, `bam_dau_vao`, `phien_ban_engine` | | `van_ban` | |

`ghi_ket_qua` trả: `so_dong_nhan`, `so_trung`, `so_ngoai_mau`, `so_cap_doi_bac`, `so_sua_loai`, `phien_ban_engine` (bảng tỷ lệ chỉ xem ở màn engine, theo C5).

## 6. Phiếu `engine.json` — phần chính

- `loai_du_lieu_rieng`: `yeu_cau_ai`, `tra_loi_ai`, khai **giống hệt** `LOAI-DU-LIEU-RIENG.md`; chép schema `_chung/contract/` vào gói, test so băm.
- **Cài đặt bước:** `khau` (bắt buộc, ≤ 40), `ma_module` (≤ 31), `nguong_json` (≤ 4096), `danh_muc_loai_json` (≤ 16384: `[{ma, ten, mo_ta}]`, ≤ 100 loại), `truong_phan_loai` (≤ 60), `bo_phan_loai_json` (≤ 32768), `nguong_tin_cay` (so, 0,7), `ma_prompt`, `phien_ban_prompt`, `prompt`, `model_uu_tien` (chỉ `chuan_bi_phan_loai`), `khuon_cot_json` (≤ 32768), `tien_te` (≤ 3), `loai_nghiep_vu` (chỉ hóa đơn), `chinh_sach_json` (≤ 8192), `ty_le_duoi_sad` (so, 0,02), `cua_so_chia_nho_ngay` (so, 7).
- **`ngan_du_lieu`** (đều `pham_vi: "phap_nhan"`; khóa không chứa `phap_nhan_id`). Theo C4, **không lưu chi tiết giao dịch** (số tiền, ngày, đối tác, nội dung):

| Bảng | Khóa | Trường | Giữ |
|---|---|---|---|
| `luot` | `ma_luot` | `ma_module`, `khau`, `hat_giong`, `bam_dau_vao`, `tao_luc` | 400 ngày |
| `dong_luot` | `ma_luot`, `ma` | `ma_module`, `khau`, `ly_do` | 400 ngày |
| `ket_qua_kiem` | `ma_luot`, `ma`, `khau` | `ma_module`, `loai`, `ket_qua`, `muc_sai` (`nho`/`sad`/`te`), `nguon_mau`, `nguon_loai_sai` | 365 ngày (cửa sổ 12 tháng) |
| `ty_le` | `khau`, `loai` | bậc, mẫu/lỗi từ lần đổi bậc, mẫu/lỗi 12 tháng, điểm, nhãn | không hết hạn |
| `ho_so_hanh_vi` | `khau`, `loai` | số nghiệp vụ, biểu đồ tần suất (json), băm đối tác (json), tổng theo băm đối tác + ngày 7 ngày (json) | không hết hạn, làm mới khi chốt kỳ |
| `chot_ky` | `ky`, `khau`, `loai` | bản chụp `ty_le` | không hết hạn |

- `dong_luot` lưu cả dòng Xanh (`KHONG_CHON`) để `ghi_ket_qua` nhận ra lỗi ngoài mẫu và để luật nộp lại hoạt động. Loại của dòng không lưu ở `dong_luot`; `ghi_ket_qua` lấy loại từ tệp kết quả kiểm hoặc `loai_dung` — PL-3 chốt: module gửi kèm `loai` trong §5.3 (thêm trường bắt buộc) **hoặc** thêm cột `loai` vào `dong_luot`; lead chọn cách ít dữ liệu hơn mà vẫn đúng.
- **`hat_giong`:** để trường thường (không `bi_mat`), vì SDK 2.2.0 chưa có đường giải mã mà kiểm toán cần đọc lại; chỉ màn engine (Admin) đọc. Ghi "Cần Core" nếu muốn mã hóa sau.
- `sql/` migration 6 bảng trong schema `eng_e_phan_luong` + `sql/kiem_ke.json`, đúng mẫu `e_demo_ngan`.
- `giao_dien_quan_tri`: `ui/bang_ty_le.js` (`admin_core`, chỉ đọc): bảng khâu × loại (bậc, điểm, nhãn), số lần sai loại theo nguồn, lịch sử chốt kỳ, tra lượt theo mã (xem hạt giống). Không gọi mạng ngoài, không `innerHTML` chưa lọc.

## 7. Lỗi (câu tiếng Việt)

| Mã | Khi nào | Câu |
|---|---|---|
| `TEP_KHONG_HO_TRO` | Không phải JSON/.xlsx/.csv | Chỉ nhận tệp JSON, Excel .xlsx hoặc CSV UTF-8. |
| `DU_LIEU_KHONG_HOP_LE` | Sai cấu trúc, thiếu trường, mã trùng, loại ngoài danh mục | Dữ liệu nghiệp vụ chưa đúng mẫu. Vui lòng kiểm tra lại tệp gửi. |
| `THIEU_NGUONG` | Không có ngưỡng, hoặc SAD/TE/PM sai thứ tự | Chưa có ngưỡng PM/TE/SAD hợp lệ cho kỳ này. Quản trị viên cần nhập ngưỡng. |
| `THAM_SO_KHONG_HOP_LE` | Cài đặt bước sai | Cài đặt bước chưa đúng. Quản trị viên kiểm tra lại cài đặt của quy trình. |
| `KHONG_PHAI_LOCAL` | Trả lời AI không từ Local | Bước phân loại chỉ nhận kết quả từ AI nội bộ. |
| `CHUOI_KHONG_KHOP` | Tệp chuyển tiếp mất hoặc sai băm | Không khớp dữ liệu giữa các bước. Vui lòng chạy lại kiểm tra cảnh báo. |
| `LUOT_KHONG_TON_TAI` | `ghi_ket_qua` không thấy lượt | Không tìm thấy lượt phân luồng. Vui lòng chạy lại kiểm tra cảnh báo. |
| `NGAN_BAN` | Xung đột ngăn quá 3 lần | Dữ liệu thống kê đang được cập nhật. Vui lòng thử lại sau ít phút. |
| `VUOT_GIOI_HAN` | Quá trần | Tệp vượt giới hạn xử lý. Vui lòng tách lô nhỏ hơn. |

## 8. DEMO và tiêu chí đạt

- Bộ DEMO do script trong `tests/` sinh: "Công ty DEMO Ánh Dương", 3 khâu, 5 loại + `chua_phan_loai`, 500 nghiệp vụ; cài sẵn vượt TE, chia nhỏ, đối tác mới, số tròn, khác tiền tệ chưa quy đổi, dòng không khớp quy tắc.
- **AI giả:** test chuỗi (b) bằng phong bì `tra_loi_ai` DEMO dựng tay (không cần máy AI): đúng enum, sai enum, tin cậy thấp, `nha_cung_cap = cloud`, `khong_thay_can_cu`.
- **Mô phỏng 12 tháng:** loại sạch xuống bậc đúng thời điểm §4.3; loại lỗi 8% giữ/lên 30% và có `rui_ro_cao`; `chua_phan_loai` luôn 30%.
- **Tái hiện:** cùng hạt giống + đầu vào → cùng danh sách luồng từng byte.
- **Tần suất:** 10.000 dòng với p = 20% → tỷ lệ chọn thực tế 19–21%.
- **Đồng thời:** hai `ghi_ket_qua` cùng lúc (`gay_xung_dot_ngan`) → đúng một lần thử lại, số đếm không lệch.
- **Tối thiểu dữ liệu (C4):** test đọc `xem_ngan` mọi bảng, khẳng định không có số tiền, ngày, đối tác, nội dung giao dịch.
- **Quyền xem (C5):** test khẳng định trường ra và `tep_json`, `tep_ds_do` không chứa xác suất, tỷ lệ, bậc.
- Điều kiện đạt chung `AGENTS.md` §5; ghi "đã kiểm bằng Core giả (CoreGia)". Cập nhật `DANH-MUC-ENGINE-CHO-MODULE.md` bằng script, thêm chuỗi mẫu (b) và `hoa_don.doc_xml@2 → audit.phan_luong_hoa_don@1`.

## 9. Lát (giờ ƯỚC TÍNH, chưa đo)

| Lát | Nội dung | Giờ |
|---|---|---:|
| PL-0 | Khung gói, `engine.json`, SQL ngăn + kiểm kê, DEMO; kiểm 2 điểm "Cần Core": chạy nút bằng Blob, `mo_tep` tệp bước trước | 4 |
| PL-1 | Đọc + kiểm JSON lô, ngưỡng, lớp 1; phân loại bằng module/quy tắc, `chua_phan_loai` | 7 |
| PL-2 | Lớp 2 + 3: bảng tỷ lệ, Clopper-Pearson, hệ số cờ, chọn băm, nộp lại | 6 |
| PL-3 | `ghi_ket_qua`: kiểm lượt, đổi bậc, ngoài mẫu, sửa loại, CAS thử lại | 5 |
| PL-4 | Hồ sơ hành vi, chốt kỳ tháng, chia nhỏ qua lô | 4 |
| PL-5 | Chuỗi Local AI: `chuan_bi_phan_loai`, `phan_luong_sau_ai` | 6 |
| PL-6 | Excel/CSV theo khuôn cột | 4 |
| PL-7 | `phan_luong_hoa_don` | 4 |
| PL-8 | Tệp JSON, Excel danh sách Đỏ, màn `ui/bang_ty_le.js` | 5 |
| PL-9 | Mô phỏng 12 tháng, test C4/C5, đo hiệu năng, kiểm độc lập, đóng gói, danh mục | 3 |
| | **Cộng** | **48** |

Thứ tự: PL-0 → PL-1 → PL-2 → PL-3 (bản dùng được với JSON) → PL-4 → PL-5 → PL-6 → PL-7 → PL-8 → PL-9.

## 10. Quyết định của Anh (20/11/2026)

| # | Câu | Anh chốt |
|---|---|---|
| 1 | Đầu vào | JSON chuẩn từ module; Excel/CSV từ phần mềm kế toán; nối sau engine Hóa đơn. Engine nhúng vào module qua nút cảnh báo người duyệt, có thể ở từng khâu |
| 2 | PM/TE | 2A: ba ngưỡng PM, TE, SAD; đi trong tệp đầu vào, kèm tiền tệ |
| 3 | Học từ kết quả kiểm | 3A: năng lực ghi kết quả, thống kê trong ngăn; **cập nhật thống kê định kỳ từ phân tích** để lượt sau dùng ngay |
| 4 | Quy tắc tỷ lệ | 4A: bậc thang |
| 5 | Tỷ lệ khởi đầu | 5A: mọi loại 30% |
| 6 | Dưới SAD | 6A: chọn với tỷ lệ sàn |
| — | Theo khâu | Tỷ lệ và thống kê riêng từng khâu |
| C1a | Module dùng trước | Chỉ dựng engine, module gắn sau |
| C1b–c | Phân loại | Có trường nội dung để phân loại; gán qua trường nội dung hoặc Local AI → quy tắc trước, AI phần còn lại |
| C1d | Chưa phân loại | Loại `chua_phan_loai`, 30% cố định |
| C2 | Bậc thang | 30 → 20 → 10 → 5% |
| C3 | Hệ số cờ | × 2 và × 1,5 như §4.4 |
| C4 | Lưu ngăn engine | 400 ngày; chỉ dữ liệu tối thiểu: mã module, mã giao dịch, lý do; chi tiết giao dịch nằm ở ngăn module |
| C5 | Quyền xem | Phân tầng: người lập không thấy; người duyệt thấy luồng + lý do; tỷ lệ và mã ngẫu nhiên chỉ Admin |
