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

## 3. ĐỀ XUẤT MASK-P, chờ Anh — chi tiết `van_ban_da_che`

*Lập 14/11/2026 khi soạn `e_mask/docs/GIAO-CODEX-e_mask.md`. Đây là đề xuất bổ sung cho khung §2.4, chưa thay định nghĩa đang có, chưa tạo schema hoặc sửa engine. Không thêm mã loại mới; giữ tên “Văn bản đã che định danh” và `phien_ban: 1`. Chỉ thêm trường tùy chọn tương thích; nếu cần đổi trường bắt buộc/nghĩa cũ phải trình mã loại mới theo §1.*

### 3.1 Sáu trường gốc và điều kiện tạo kết quả

| Trường trong `van_ban_da_che` | Ngữ nghĩa đề xuất |
|---|---|
| `phien_ban` | Số nguyên `1`. |
| `van_ban` | Chuỗi đã che, không rỗng; chỉ xuất sau hậu kiểm. Trần đầu vào Mask 500.000 ký tự không tự trở thành trần đầu ra; bí danh có thể làm chuỗi dài hơn. Bước nhận phải kiểm trần riêng, không cắt ngầm. |
| `ma_yeu_cau` | Mã opaque do Core cấp và quản, gắn module/người gửi/tài liệu từ nguồn tin cậy. Không dùng quy tắc mã lượt cũ (hết hạn/64 ký tự) để tự đổi hợp đồng. Không gửi Cloud. |
| `con_sot` | Mảng rỗng khi trả thành công; kết quả chưa kiểm hết không được tạo loại này. Các dấu vết nội bộ chỉ có nhóm/vị trí/lý do chung, không cụm gốc. |
| `kiem_tien_ngay` | Phải là boolean `true` từ đối chiếu thực tế trước/sau che; cờ tự khai hoặc schema đúng không chứng minh đã bảo toàn. |
| `chuyen_tiep` | Đối tượng nội bộ, mặc định `{}`, tối đa 64 KiB JSON UTF-8. Không chép nguyên trang/khối OCR, văn bản nguồn, danh mục hoặc cụm gốc mới vào đây. Không dùng nó để tự khai danh tính/quyền. |

Mask còn sót, thiếu tài nguyên detector, kiểm tiền/ngày không đạt hoặc chưa chốt kho → `LoiNghiepVu`, **không trả thành công với `van_ban: null`, bản che dở hoặc cờ an toàn giả**. Không công bố bảng đối chiếu. Kho bí danh/quyền tin cậy là phụ thuộc riêng; kết quả test bằng fixture DEMO không chứng nhận kho thật.

### 3.2 Trường tùy chọn đề xuất

| Trường | Kiểu / nội dung |
|---|---|
| `so_cho_thay` | Số nguyên không âm; bằng 0 không tự chứng minh không sót. |
| `bi_danh` | Mảng `{bi_danh, nhom, nguon}`; `nguon` là `chinh_thuc` hoặc `tam`. Chỉ bí danh, không giá trị gốc hoặc bảng tra ngược. |
| `cho_duyet` | `{so_cum_vua_them: <số nguyên không âm>}`; không trả cụm gốc mới. |
| `vung_da_quet` | Mảng mã vùng/chỉ số vị trí đã kiểm (thân, đầu/chân, bình luận, lịch sử sửa, thuộc tính, sheet/ô ẩn…). Không đưa tên sheet/nhãn/path chứa định danh chưa che vào báo cáo. Chỉ liệt kê vùng thực sự đã kiểm; không mặc nhiên khẳng định đủ mọi vùng tệp. |
| `phien_ban_engine` | Chuỗi phiên bản engine tạo kết quả. |
| `bam_dau_vao` | Chuỗi `sha256:<64 chữ số hệ 16>`, tính trên bytes đầu vào hoặc UTF-8 của chuỗi gốc; không đưa lên Cloud. |
| `canh_bao` | Mảng câu tiếng Việt cố định, không chứa cụm gốc, đoạn trích chưa che, đường máy hoặc bí mật. |

Schema dự kiến `_chung/contract/van_ban_da_che.schema.json` được tạo tại MASK-4 **sau khi phần đề xuất được chốt**, rồi chép vào gói Mask, test so SHA. Engine dùng loại này kiểm ngữ nghĩa bên trong vì SDK chỉ kiểm khớp mã loại. Không sửa các schema `van_ban_tai_lieu`, `yeu_cau_ai`, `tra_loi_ai` đang có trong MASK-P.

### 3.3 Nối Hỏi AI và mở che

- Core phải bảo đảm loại này thực sự do bước Mask tạo; so khớp chuỗi `loai` hoặc tin hai cờ từ caller chưa đủ chống giả mạo kết quả đã che. Việc này thuộc cửa chung, không route riêng Mask.
- Khi Hỏi AI bản 2 được bật: chỉ nội dung `van_ban` đã che được dùng làm căn cứ gửi Cloud; prompt và phần khác có nội dung nhạy cảm cũng phải đi qua kiểm tương ứng, không tự được miễn vì nhận loại này. **Không tuần tự hóa cả payload** gửi ra ngoài: loại `ma_yeu_cau`, `chuyen_tiep`, báo cáo/băm và mọi dữ liệu kho khỏi request nhà cung cấp.
- `ma_yeu_cau` chỉ chép nội bộ vào `tra_loi_ai.chuyen_tiep.ma_yeu_cau`, không cho model tạo lại. Mask lấy mã này khi mở che, Core vẫn kiểm đúng module/người gửi/tài liệu; biết mã không thay quyền. Vị trí OCR/trích dẫn trước che không mặc nhiên đúng sau thay thế; không giữ kết luận kiểm nguyên văn cho câu trích đã đổi chữ khi mở che.
- DOCX/XLSX giữ định dạng được Mask trả bằng loại gốc `truong` với trường `tep` và báo cáo tĩnh (phiếu Mask §2); **không giả `van_ban_da_che` để mang tệp ra Cloud**. Luồng AI sửa tệp chỉ giả lập trong đợt này; Cloud vẫn tắt theo phiếu Hỏi AI.

Chờ Anh chốt bổ sung này cùng Q3/Q4 của `GIAO-CODEX-THU-TU.md`; không coi nhãn đề xuất là bằng chứng contract đã đăng ký/kích hoạt hoặc engine đủ điều kiện gửi Cloud.
