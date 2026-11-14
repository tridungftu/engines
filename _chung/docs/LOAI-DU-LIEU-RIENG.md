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

## 3. ĐỀ XUẤT TX-0, chờ Anh — `bang_trich_xuat`

*Bổ sung 14/11/2026 (Codex), theo `e_trich_xuat/docs/TX-0-THIET-KE.md` T2(b). Phần này là đề xuất riêng; không sửa định nghĩa/schema của bốn loại ở trên. Chưa tạo `_chung/contract/bang_trich_xuat.schema.json`, chưa đăng ký năng lực hoặc cập nhật gói engine.*

**Đề xuất khai báo thống nhất:**

```json
{"ma": "bang_trich_xuat", "ten": "Bảng thông tin trích xuất"}
```

| Nội dung | Đề xuất |
|---|---|
| Nguồn tạo | `e_trich_xuat`: `trich.hau_kiem@1` |
| Nơi nhận | `e_trich_xuat`: `trich.xuat_ket_qua@1`; module đọc bản JSON để dựng bảng/ghép cột; engine khác chỉ sau khi được khai nhận loại này |
| Mục đích | Danh sách trường thay đổi theo bộ riêng từng module, có kiểu giá trị, nguyên văn, dẫn chứng/vị trí và ô cần soát; không phải năng lực trích bảng TRICH-2a |
| Phiên bản | Payload `phien_ban: 1`; thêm trường tùy chọn giữ số, đổi không tương thích tạo mã `bang_trich_xuat_2` theo quy tắc chung |
| Đầu cuối quy trình | API v1 chỉ ghép `truong`/`van_ban`/`tep` vào cột ngăn. Loại này là bước trung gian, **bắt buộc có bước xuất** trả `truong` tĩnh (`tep_json`, `tep_excel`, `so_tham_so`, `so_can_soat`, `co_can_cu`) khi cần ghép ngăn |
| Giới hạn đề xuất | Tối đa 200 dòng đang trích, phong bì JSON UTF-8 ≤ 20 MiB; mọi trích dẫn thuộc đúng văn bản đã gửi AI. Không nhét toàn văn/cấu trúc vào bảng; hồ sơ hậu kiểm ở tệp tạm Core, có tham chiếu và băm |

### 3.1. Hình dạng phong bì đề xuất

Mẫu DEMO dưới đây minh họa **chọn một trường TT-02** từ bộ 37, nên có một dòng và `so_tham_so=1`. Văn bản/băm bộ và offset trích dẫn lấy từ phép đếm TX-0; `tep_id` là mã giả, `bam_ho_so_hau_kiem` là chỗ điền băm tệp thực khi triển khai, không phải tệp đã được tải lên Core. Bộ 37 hiện chưa khai kiểu tiền có kiểm chứng, nên ô này giữ `kieu="van_ban"` với đơn vị VND trong giá trị; không tự suy kiểu từ mã TT-02.

```json
{"loai": "bang_trich_xuat", "bang_trich_xuat": {
  "phien_ban": 1,
  "module": "crm_demo",
  "loai_hop_dong": "XD",
  "phien_ban_bo": "DEMO-1",
  "bam_bo_tham_so": "sha256:a5a71f215e45c312907dea4d7edbc7ff8028306352e1f676ae094992a2754d04",
  "ma_prompt": "crm_demo.trich_hd",
  "phien_ban_prompt": "DEMO-1",
  "phien_ban_engine": "e_trich_xuat 0.2.0",
  "ma_truong_can_trich": ["TT-02"],
  "nguon": {
    "nguon_doc": "docx",
    "bam_van_ban": "sha256:b6b511f069739ab4b6012ca161882244482b1a8da6da62eee50b6498f1f9e209",
    "ho_so_hau_kiem": {"tep_id": "DEMO-ho-so-hau-kiem", "ten": "DEMO-ho-so-hau-kiem.json", "mime": "application/json", "kich_thuoc": 0},
    "bam_ho_so_hau_kiem": "<sha256 tệp thực, điền khi triển khai>"
  },
  "ai": {"nha_cung_cap": "local", "model": "DEMO-model-gia"},
  "bang": [{
    "ma": "TT-02", "ten": "Giá trị hợp đồng", "kieu": "van_ban",
    "gia_tri": "1.000.000 VND", "nguyen_van": "1.000.000 VND",
    "don_vi_nguyen_van": "VND", "ghi_chu": null,
    "dan_chung": [{
      "cau": "Giá trị hợp đồng là 1.000.000 VND, đã gồm VAT; thuế suất GTGT 10%.",
      "bat_dau": 405, "ket_thuc": 471,
      "vi_tri": {"loai": "doan", "nhan": "Điều 1. Hiệu lực và giá hợp đồng", "so_trang": null, "hop": null}
    }],
    "can_soat": false, "ly_do": [], "kiem_tra_logic": []
  }],
  "tom_tat": {"so_tham_so": 1, "so_can_soat": 0, "co_can_cu": true},
  "canh_bao": ["DEMO; chưa xác định số trang Word, vị trí theo đoạn/Điều/Khoản."]
}}
```

### 3.2. Ràng buộc khi viết schema/lõi ở TX-3 sau khi duyệt

- Các trường metadata trên (trừ cảnh báo có thể rỗng) phải hiện diện và khớp snapshot đã ghim. `ma_truong_can_trich` giữ đúng danh sách/thứ tự đang hỏi; `bang` có đúng một ô cho mỗi mã, không bỏ mã thiếu và không chấp nhận mã lạ/trùng. `so_tham_so=len(bang)`, `so_can_soat` bằng số ô cờ true, `co_can_cu` nghĩa là có ít nhất một giá trị đã kiểm chứng, không phải mọi ô đều đúng.
- `kieu` dùng sáu kiểu cột chung: `van_ban`, `so`, `so_tien`, `ngay`, `co_khong`, `tep`. `gia_tri` theo kiểu đó hoặc `null`; ví dụ kiểu `so_tien` phải là `{"so": 1000000, "tien_te": "VND"}`, ngày là `"2026-10-30"`. Chỉ chuyển kiểu khi bộ module có quy tắc rõ và căn cứ kiểm được; không lấy số lớn nhất trong chuỗi làm tiền, không đoán tiền tệ.
- Thiếu/không có căn cứ kiểm được: `gia_tri=null`, `can_soat=true`, `ly_do` nêu rõ; phản hồi chưa kiểm giữ ở `nguyen_van`, không biến nó thành giá trị đã xác nhận. Lỗi logic giữ giá trị trích có căn cứ để người soát xem, đồng thời bật cờ và ghi lý do.
- `dan_chung` có câu nguyên văn và offset Unicode `[bat_dau, ket_thuc)` trong đúng văn bản có `bam_van_ban`; kiểm lại lát chuỗi bằng Python, không dùng chỉ số byte/UTF-16 của UI. PDF giữ số trang/hộp thực từ OCR; DOCX chưa phân trang thì để `so_trang=null`, `hop=null` và ghi định vị theo đoạn, không bịa tọa độ.
- Trong `nguon` runtime phải giữ thêm `bam_dau_vao` của tài liệu gốc từ `van_ban_tai_lieu`; nó khác `bam_van_ban` của văn bản đã chuẩn hóa. Tham chiếu hồ sơ phải trỏ tới tệp thực có kích thước/băm đã kiểm, Core kiểm quyền theo chuỗi/pháp nhân/module. Mẫu giả ở trên không được dùng làm fixture chạy đạt.
- Module quyết định lưu/sửa/xác nhận và giữ lịch sử; không cho engine ghi ngược kho bộ. Core giữ kết quả/tệp tạm tới khi module xác nhận lưu/đóng, xử lý lặp xác nhận không gây dọn/lưu hai lần.
- Sau duyệt mới tạo schema nguồn tại `_chung/contract/`, chép vào gói và test so băm đúng quy tắc chung. Engine tự kiểm quan hệ/căn cứ mà JSON Schema không chứng minh được; Core chỉ khớp mã loại.

### 3.3. Không đổi `yeu_cau_ai` trong TX-0

T3(a) dùng nguyên `yeu_cau_ai` phiên bản 1. Đề xuất dùng khóa riêng của engine trong phần **đã cho phép mở** `chuyen_tiep`:

```json
{"trich_xuat": {
  "phien_ban": 1, "module": "crm_demo", "loai_hop_dong": "XD", "phien_ban_bo": "DEMO-1",
  "bam_bo_tham_so": "<sha256 snapshot JSON>",
  "ho_so_hau_kiem": {"tep_id": "DEMO-ho-so-hau-kiem", "ten": "DEMO-ho-so-hau-kiem.json", "mime": "application/json", "kich_thuoc": 0},
  "bam_ho_so_hau_kiem": "<sha256 tệp thực>"
}}
```

Đây là quy ước nội bộ của bước chuẩn bị/hậu kiểm, **không phải thêm trường bắt buộc vào loại chung**. Hỏi AI giữ nguyên phần này trong `tra_loi_ai`, không đưa nó vào prompt gửi model. Nội dung bộ/văn bản/vị trí nằm trong hồ sơ hậu kiểm tạm tại Core; kiểm byte để phần chuyển tiếp không vượt 64 KiB (mục tiêu riêng ≤ 4 KiB). Cần Core xác nhận quyền/vòng đời tệp giữa các bước; SDK có thao tác tệp không tự chứng minh yêu cầu này đã được Core thật thực hiện.

Nếu T3(b) được chọn sau này, phải trình riêng request/result batch, giới hạn số lượt, cách hợp nhất, hủy/lỗi/chưa rõ và tương thích; không thêm mảng câu hỏi vào schema v1 rồi coi consumer cũ hỗ trợ.
