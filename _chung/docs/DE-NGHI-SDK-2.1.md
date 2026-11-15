# Đề nghị chỉnh SDK → 2.1.0: ngăn dữ liệu engine, cấu hình và màn hình của engine

*Lập 15/11/2026 (Claude, lead engine) theo quyết định của Anh Dũng cùng ngày (`QUYET-DINH-ANH-20261115.md` câu 1, 2, 13). Gửi người phụ trách SDK/Core. Đề nghị **chỉ thêm**, không đổi phần engine đã khóa ở 2.0.0, nên đánh số **2.1.0** và giữ tương thích ngược.*

## 1. Kết luận

- **Nguyên tắc Anh chốt:** engine không lưu gì trên máy. Mỗi engine có **một ngăn dữ liệu riêng** do Core cất hộ. Cấu hình (model AI, IP máy Local AI, đường Hot Folder…) **thuộc engine**: engine có màn hình cấu hình riêng, giá trị nằm trong ngăn của engine.
- SDK 2.1 cần thêm **4 phần**:
  - (A) khai ngăn trong phiếu;
  - (B) API + SDK đọc/ghi ngăn có giao dịch và CAS;
  - (C) cấu hình engine;
  - (D) màn quản trị của engine nạp như màn module.
  - Phần (E) thao tác quản trị là tùy chọn. Mục (F) là 5 lỗi nhỏ Codex phát hiện khi dùng 2.0.0.
- Các engine (Hỏi AI, OCR, Mask) **đã được viết như thể có ngăn**, qua một cổng `Ngan`. Hiện cổng này chạy bằng ngăn trong bộ nhớ. Khi SDK 2.1 có `app.ngan`, engine dùng ngăn thật mà không phải viết lại.

## 2. (A) Phiếu `engine.json` — trường mới, đều không bắt buộc

```json
"ngan_du_lieu": [
  {"bang": "luot_abbyy", "ten": "Lượt gửi ABBYY", "pham_vi": "phap_nhan",
   "khoa": ["ma_tuong_quan"],
   "duy_nhat": [["phap_nhan_id", "bam_noi_dung"]],
   "truong": [{"ma": "ma_tuong_quan", "kieu": "van_ban"}, {"ma": "bam_noi_dung", "kieu": "van_ban"},
              {"ma": "so_trang", "kieu": "so"}, {"ma": "trang_thai", "kieu": "van_ban"},
              {"ma": "chi_tiet", "kieu": "json"}],
   "giu_toi_da_ngay": 90}
],
"cau_hinh": {"schema": "cau_hinh.schema.json"},
"giao_dien_quan_tri": [
  {"ma": "cau_hinh", "ten": "Cấu hình", "tep": "ui/cau_hinh.js", "quyen": "admin_core"}
]
```
- `pham_vi`:
  - `engine`: dùng chung cho toàn engine, ví dụ bảng định danh của Mask.
  - `phap_nhan`: Core tự gắn và lọc theo `phap_nhan_id` của việc; engine không đọc được dữ liệu của pháp nhân khác.
- `kieu`: danh mục kiểu cột chung, thêm `json` (đối tượng ≤ 64 KiB). `duy_nhat`: các ràng buộc duy nhất. `giu_toi_da_ngay`: hết hạn thì Core tự dọn.
- Core tạo bảng trong schema `eng_<ma>` lúc cài gói. Đổi cấu trúc bảng thì tăng `phien_ban` engine; Core chuyển dữ liệu theo khai báo, không để engine chạy SQL.

## 3. (B) API và SDK cho ngăn

**API** (thêm vào bảng c.2; cùng xác thực `Bearer` + `X-KTT-Engine` + `X-KTT-Instance`):

| # | Thao tác | HTTP | Gửi → trả |
|---:|---|---|---|
| 11 | Đọc một bản ghi | `POST /api/v1/engine/{ma}/ngan/{bang}/doc` | `{khoa:{…}}` → `{ban_ghi \| null, row_version}` |
| 12 | Tìm | `POST /api/v1/engine/{ma}/ngan/{bang}/tim` | `{loc:{truong: giá trị}, sap_xep?, gioi_han ≤ 500, tiep?}` → `{danh_sach, tiep}` |
| 13 | Ghi lô nguyên tử | `POST /api/v1/engine/{ma}/ngan/ghi-lo` + `Idempotency-Key` | `{lenh:[{thao_tac: "them"\|"sua"\|"xoa"\|"lay_hoac_tao", bang, khoa, gia_tri?, row_version?}] (≤ 100 lệnh)}` → `{ket_qua:[{row_version, da_tao}]}` |

- **Ghi lô nguyên tử:** mọi lệnh trong lô cùng thành công, hoặc không lệnh nào được ghi.
- **CAS:** `sua`/`xoa` kèm `row_version` lệch với bản hiện tại thì cả lô bị từ chối với **409 `NGAN_XUNG_DOT`**, `thu_lai_duoc: true`.
- **Ràng buộc duy nhất:** vi phạm thì cũng trả 409 `NGAN_XUNG_DOT`.
- `lay_hoac_tao`: theo ràng buộc duy nhất. Có rồi thì trả bản cũ, `da_tao: false`; chưa có thì tạo mới.
- Gọi được cả trong việc (Core ghi `viec_id` để kiểm toán) và ngoài việc (lúc khởi động). Engine chỉ thấy ngăn của chính mình.
- Core lo: giao dịch, sao lưu, phân quyền, nhật ký kiểm toán không chứa giá trị.

**SDK Python:**
```python
ban_ghi = app.ngan.doc("luot_abbyy", {"ma_tuong_quan": m})      # None hoặc .gia_tri, .row_version
ds = app.ngan.tim("han_muc_ngay", loc={"thang": "2026-11"}, gioi_han=100)
with app.ngan.lo() as lo:                                         # gửi khi ra khỏi with; lỗi thì không ghi gì
    lo.lay_hoac_tao("luot_abbyy", {"phap_nhan_id": p, "bam_noi_dung": b}, {...})
    lo.sua("han_muc_ngay", {"ngay": "2026-11-15"}, {"so_trang": 130}, row_version=7)
# xung đột → raise NganXungDot (thu_lai_duoc=True); trong hàm năng lực dùng viec.ngan (cùng API, gắn viec_id)
```
**Core giả:**
- `CoreGia` có ngăn trong bộ nhớ, đúng cùng ngữ nghĩa (lô, CAS, duy nhất, phạm vi pháp nhân).
- Thêm `gay_xung_dot_ngan(bang, so_lan=1)` để test đường thử lại, và `xem_ngan(ma, bang)` để kiểm.
- `MayChuGia` phục vụ cùng đường dẫn HTTP.

**Gợi ý:** lượt bền "chưa rõ" (#10 `luot-ben`, đã hẹn ở đợt 2) làm được trên ngăn có CAS, như bảng `luot_abbyy` ở trên. Core cân nhắc dùng ngăn thay cho một thao tác riêng.

## 4. (C) Cấu hình của engine

- Phiếu khai `cau_hinh.schema` (JSON Schema trong gói). Giá trị là **một bản ghi trong ngăn hệ thống của engine**, có `phien_ban_cau_hinh` (CAS).
- `san-sang` trả `{cau_hinh: {…đã kiểm schema, đã điền mặc định…}, phien_ban_cau_hinh}`. SDK đưa ra thành `app.cau_hinh` và `viec.cau_hinh` (bản chụp lúc nhận việc).
- Đổi cấu hình thì Core phát `engine.cau_hinh_doi`. SDK tự nạp lại; engine đăng ký thêm xử lý bằng `@app.khi_doi_cau_hinh` nếu cần.
- Cấu hình **không chứa bí mật**. Khóa Cloud và khóa cầu nối ABBYY đi qua `bi_mat[]` (đề nghị riêng, chưa cần ở đợt này).
- Core giả: `CoreGia().dat_cau_hinh(ma_engine, {...})`.

## 5. (D) Màn quản trị của engine — nạp như màn module

- Gói có `ui/*.js`, khai ở `giao_dien_quan_tri`. Core nạp màn trong **Quản lý engine › tên engine**, cùng cơ chế nạp màn module, chỉ người có `quyen` khai mới mở được.
- SDK trình duyệt `KttCore` (`trinh_duyet.js`) thêm nhóm `KttCore.engine(ma)`:
  - `.cau_hinh.doc()`, `.cau_hinh.luu(gia_tri, phien_ban_cau_hinh)`: Core kiểm schema + CAS, ghi kiểm toán, phát `engine.cau_hinh_doi`.
  - `.ngan.doc / .tim / .ghi_lo`: Admin đọc/ghi ngăn của engine đó. Dùng cho màn duyệt danh sách chờ của Mask, màn xem hạn mức của OCR, danh sách model phát hiện của Hỏi AI.
  - `.thao_tac(ma, dau_vao)`: xem mục 6.
- **An toàn khi nạp thẳng** (Anh chọn không dùng khung cách ly):
  - màn chỉ gọi API Core qua `KttCore`; chính sách bảo mật nội dung (CSP) chặn gọi ra ngoài;
  - không `eval`, không `innerHTML` chưa lọc;
  - Core quét tĩnh mã màn khi cài gói và từ chối gói vi phạm;
  - lead Core review mã màn trước khi cài.
- Ngày dd/mm/yyyy, tiền có dấu chấm hàng nghìn và mã tiền tệ: Core cấp hàm định dạng chung trong `KttCore`.

## 6. (E) Thao tác quản trị — tùy chọn

Cần cho các nút như "Phát hiện model" (Hỏi AI), "Kiểm Hot Folder" (OCR), "Duyệt cụm" (Mask).
- Phiếu: `"thao_tac_quan_tri": [{"ma": "phat_hien_model", "ten": "Phát hiện model", "thoi_han_giay": 30}]`.
- Core chuyển lệnh thành **việc ưu tiên** loại `quan_tri` cho engine, chờ kết quả tối đa `thoi_han_giay`, rồi trả về màn.
- SDK: `@app.thao_tac_quan_tri("phat_hien_model")`, hàm nhận `tac` (có `.dau_vao`, `.ngan`, `.cau_hinh`) và trả `dict`.
- Nếu chưa làm (E): engine tự ghi trạng thái vào ngăn theo chu kỳ, màn chỉ đọc ngăn. Cách này đủ cho đợt đầu.

## 7. (F) Sửa nhỏ Codex phát hiện khi dùng SDK 2.0.0

1. `mo_tep` vượt trần: Core giả trả 413 `VUOT_GIOI_HAN_KICH_THUOC`, nhưng SDK ánh xạ thành `KHONG_TRAO_DOI_DUOC_CORE`. Cần một lỗi giới hạn chung, câu tiếng Việt rõ.
2. Lỗi bất ngờ trong hàm năng lực: SDK in toàn bộ traceback ra nhật ký, có thể lộ nội dung tài liệu hoặc đường dẫn. Cần nhật ký an toàn (lọc) cho cả lỗi ngoài hàm năng lực.
3. Cho engine tự đặt mã lỗi khi thiếu tham số bắt buộc (Hỏi AI cần trả `THIEU_PROMPT`). Kiểm `ky_tu_toi_da` cả trường văn bản **bên trong loại riêng**.
4. Cấp mốc hàng chờ (vị trí, số việc đang chờ) cho engine và màn: OCR cần cho ca "báo số việc đang chờ".
5. SDK đọc `han_giu` Core trả về (nợ c.2 điểm 5).

## 8. Engine nào dùng ngăn gì (để Core ước dung lượng)

| Engine | Bảng ngăn dự kiến | Phạm vi |
|---|---|---|
| `e_hoi_ai` | `cau_hinh` (địa chỉ Local AI, thời hạn, quy tắc chọn model); `model_phat_hien`; bản 2: `thong_ke_chinh_xac` theo function | engine |
| `e_ocr` | `cau_hinh` (thư mục Hot Folder, hạn mức 5.000 trang/30 ngày, đường Tesseract); `han_muc_ngay`; `luot_abbyy` (duy nhất theo pháp nhân + băm) | engine / phap_nhan |
| `e_mask` | `cau_hinh`; `dinh_danh` (giá trị chuẩn → bí danh, duy nhất); `bi_danh_tam`; `cho_duyet`; `ma_yeu_cau`; `dau_gap` | engine (bảng định danh chung toàn tập đoàn) |
| `e_hoa_don` | chưa cần cho XML/ZIP/bảng kê; phần tải cổng thuế cần sau | — |

## 9. Nghiệm thu đề nghị

- Engine mẫu `e_demo_ngan`: đếm số lần gọi theo pháp nhân bằng ngăn. Chạy trên `CoreGia` và `MayChuGia`, có ca hai việc đồng thời gây xung đột CAS (đúng một việc phải thử lại).
- Màn mẫu `ui/cau_hinh.js` của `e_demo_ngan` sửa một ô cấu hình. Engine nhận `engine.cau_hinh_doi` mà không phải khởi động lại.
- Engine 2.0.0 cũ không khai trường mới vẫn cài và chạy được trên Core 2.1.
