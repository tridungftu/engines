# Loại dữ liệu riêng dùng chung giữa các engine — ĐỀ XUẤT, chờ Anh duyệt tên (Q3)

*Lập 14/11/2026 (Claude, lead). Căn cứ: `API-ENGINE-v1.md` b.2–b.3 (Core chỉ có 3 loại gốc `tep`, `van_ban`, `truong`; engine khai thêm ở `loai_du_lieu_rieng`, Core chỉ so khớp chuỗi `ma`).*

## 1. Kết luận

- Cần **4 loại riêng dùng chung**, vì 3 loại gốc không mang được vị trí trang, trích dẫn hay khuôn trả lời:

| Mã loại | Tên hiển thị | Engine tạo ra | Engine nhận |
|---|---|---|---|
| `van_ban_tai_lieu` | Văn bản tài liệu có vị trí | `e_ocr` | `e_hoi_ai`, `e_trich_xuat`, `e_doi_chieu`, `e_tra_cuu` |
| `yeu_cau_ai` | Yêu cầu hỏi AI | `e_trich_xuat` (bước chuẩn bị), engine khác sau này | `e_hoi_ai` |
| `tra_loi_ai` | Trả lời AI có trích dẫn | `e_hoi_ai` | `e_trich_xuat` (bước hậu kiểm), `e_mask` (mở che) |
| `van_ban_da_che` | Văn bản đã che định danh | `e_mask` | `e_hoi_ai` (năng lực Cloud) |

- **Mọi engine dùng một loại phải khai giống hệt** `{"ma": "...", "ten": "..."}` trong `loai_du_lieu_rieng`. Nguồn duy nhất là tệp này.
- Mỗi phong bì có trường `phien_ban` (bắt đầu `1`). Thêm trường không bắt buộc thì giữ số; **đổi không tương thích thì tạo mã mới** (`van_ban_tai_lieu_2`), giữ mã cũ cho quy trình đang chạy.
- Schema JSON máy kiểm đặt tại `_chung/contract/<ma>.schema.json` (Codex tạo ở lát đầu của engine tạo ra loại đó). Mỗi engine **chép** schema vào gói của mình (gói phải độc lập) và test so băm với bản ở `_chung/contract/`.

## 2. Định nghĩa

### 2.1 `van_ban_tai_lieu`
```json
{"loai": "van_ban_tai_lieu", "van_ban_tai_lieu": {
  "phien_ban": 1,
  "van_ban": "Toàn văn, các trang nối bằng \f",
  "trang": [{"so": 1, "rong": 595.0, "cao": 842.0, "don_vi": "pt",
             "khoi": [{"loai": "doan", "van_ban": "…", "hop": [x0, y0, x1, y1],
                       "dong": [{"van_ban": "…", "hop": [..], "tu": [{"van_ban": "…", "hop": [..], "nghi_ngo": false}]}]},
                      {"loai": "bang", "hop": [..],
                       "o": [{"hang": 0, "cot": 0, "gop_hang": 1, "gop_cot": 2, "van_ban": ""}]}]}],
  "nguon_doc": "abbyy | tesseract | lop_chu_san | docx",
  "ly_do_chuyen_nguon": null,
  "so_trang": 3,
  "phien_ban_engine": "e_ocr 1.0.0",
  "bam_dau_vao": "sha256:…",
  "canh_bao": []
}}
```
- `dong`/`tu` không bắt buộc (nguồn không có tọa độ từ thì bỏ). `nghi_ngo` lấy từ cờ của nguồn nhận dạng; không có thì bỏ.
- Ô trống giữ `"van_ban": ""`; ô gộp ghi `gop_hang`/`gop_cot` ở ô gốc.

### 2.2 `yeu_cau_ai`
```json
{"loai": "yeu_cau_ai", "yeu_cau_ai": {
  "phien_ban": 1,
  "ma_prompt": "trich.xay_dung.q01", "phien_ban_prompt": "3",
  "prompt": "Câu hỏi/khung yêu cầu của module",
  "tai_lieu": "Văn bản làm căn cứ",
  "khuon_tra_loi": null,
  "bat_buoc_trich_dan": true,
  "model_uu_tien": null,
  "chuyen_tiep": {}
}}
```
- `khuon_tra_loi`: JSON Schema (draft 2020-12, ≤ 32 KiB) mà AI phải trả đúng; `null` = trả lời tự do.
- `chuyen_tiep`: đối tượng bất kỳ ≤ 64 KiB, `e_hoi_ai` **trả lại nguyên vẹn** trong `tra_loi_ai` (để bước sau có lại bộ tham số, băm, vị trí… mà không phải gọi engine trước).

### 2.3 `tra_loi_ai`
```json
{"loai": "tra_loi_ai", "tra_loi_ai": {
  "phien_ban": 1,
  "trang_thai": "co_can_cu | khong_thay_can_cu",
  "tra_loi": "Câu trả lời",
  "du_lieu": null,
  "trich_dan": [{"cau": "nguyên văn trong tài liệu", "bat_dau": 120, "ket_thuc": 168}],
  "kiem_trich_dan": {"dat": true, "loi": []},
  "nha_cung_cap": "local | cloud",
  "model": "qwen3:8b", "ly_do_chon_model": "quy tắc module/function",
  "ma_prompt": "…", "phien_ban_prompt": "…",
  "phien_ban_engine": "e_hoi_ai 1.0.0",
  "bam_dau_vao": "sha256:…",
  "chuyen_tiep": {},
  "canh_bao": []
}}
```
- `du_lieu`: đối tượng đúng `khuon_tra_loi` khi có khuôn; ngược lại `null`.
- `kiem_trich_dan.dat = false` → `trang_thai` hạ về `khong_thay_can_cu` hoặc có cảnh báo, theo quy tắc AI-5.

### 2.4 `van_ban_da_che` (khung — `e_mask` chốt chi tiết khi tới lượt)
```json
{"loai": "van_ban_da_che", "van_ban_da_che": {
  "phien_ban": 1, "van_ban": "… [[CT-0001]] …", "ma_yeu_cau": "…",
  "con_sot": [], "kiem_tien_ngay": true, "chuyen_tiep": {}
}}
```
- `e_hoi_ai` từ chối nếu `con_sot` khác rỗng hoặc `kiem_tien_ngay` khác `true`; **không gửi `ma_yeu_cau` ra Cloud**; chép `ma_yeu_cau` vào `chuyen_tiep` của `tra_loi_ai` để bước mở che dùng.
