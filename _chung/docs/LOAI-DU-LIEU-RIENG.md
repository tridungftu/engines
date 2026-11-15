# Loại dữ liệu riêng dùng chung giữa các engine — ĐÃ DUYỆT 15/11/2026

> Anh duyệt cả 4 tên (§1–2) và phần chi tiết `van_ban_da_che` (§3, đề xuất MASK-P) ngày 15/11/2026 — `QUYET-DINH-ANH-20261115.md` câu 3, 11. Các nhãn "đề xuất / chờ Anh" bên dưới chỉ còn giá trị lịch sử.

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

## 4. ĐỀ XUẤT TX-0, chờ Anh — chi tiết `bang_trich_xuat`

*Bổ sung 14/11/2026 (Codex), theo `e_trich_xuat/docs/TX-0-THIET-KE.md` T2(b). Phần này là đề xuất riêng; không sửa định nghĩa/schema của bốn loại ở trên. Chưa tạo `_chung/contract/bang_trich_xuat.schema.json`, chưa đăng ký năng lực hoặc cập nhật gói engine.*

**Cập nhật 15/11/2026:** Anh đã chốt **hướng** bảng loại riêng + tệp Excel, module tự ghép cột (`QUYET-DINH-ANH-20261115.md` câu 5). Nhãn “chờ Anh” của mục này chỉ còn áp dụng cho **payload/schema chi tiết và bước xuất tĩnh**, không hỏi lại lựa chọn T2(b). Đề nghị Core thêm cửa chung **“trường do tham số quyết định”** được ghi C-TX-03 trong `e_trich_xuat/docs/VIEC.md`; không đổi API/phiếu 2.0. Nguyên tắc ngăn/cấu hình/màn theo SDK 2.1 ở thiết kế §6.3; không lưu tệp cấu hình, bộ, hồ sơ hay kết quả trên máy engine.

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
| Bản Excel đi kèm | Đợt 1 bước xuất luôn tải cả JSON bảng và Excel lên Core; module tự ghép cột từ dữ liệu chuẩn, không suy kiểu từ Excel. Xuất tệp lỗi thì báo lỗi, không trả thành công thiếu Excel; tệp tạo trong RAM, tệp tạm nếu cần phải dọn trong `finally` |
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

## 5. ĐỀ XUẤT DC-P, chờ Anh — `ho_so_doi_chieu`

*Lập 15/11/2026 · Codex · Theo `e_doi_chieu/docs/GIAO-CODEX-e_doi_chieu.md` §2 và DC-Q17. Đây là đề xuất mới, **chưa duyệt/kích hoạt**, không thuộc bốn loại đã duyệt ở §1–3. Không tạo schema/gói ở DC-P, không đổi loại/schema hiện có.*

### 5.1 Mục đích và lựa chọn tái dùng

Đề xuất đúng một loại mới:

```json
{"ma": "ho_so_doi_chieu", "ten": "Hồ sơ đối chiếu bản ký"}
```

- Tái dùng **nguyên phong bì** `van_ban_tai_lieu` cho mỗi tài liệu; tái dùng `yeu_cau_ai`/`tra_loi_ai` cho bước Local AI do Core điều phối. Không sửa chúng để nhét hai tài liệu vào một trường vốn mang nghĩa một tài liệu.
- `bang_trich_xuat` là bảng trường theo bộ, không mang edit script toàn văn, vùng sửa tay hoặc trạng thái kiểm hai bản; không đổi nghĩa loại đó để phục vụ Đối chiếu.
- Dùng `tep` cho Word/PDF/ảnh/JSON snapshot do Core giữ. Đã cân nhắc trả `tep` JSON ở mọi bước; đề xuất loại hồ sơ để Core phân biệt chỗ nối nghiệp vụ, không chỉ kiểm tệp bất kỳ. Chỉ dùng một loại xuyên các giai đoạn; engine kiểm giai đoạn sâu vì Core chỉ khớp chuỗi mã loại.
- Nguồn tạo/nhận: `e_doi_chieu` ở `nhan_cap`, `so_van_ban`, `phat_hien_sua_tay`, `chuan_bi_ai`, `phan_loai_diem_lech`, `xuat_ket_qua` (đều tiền tố `doi_chieu.`, hậu tố `@1`). Module đọc JSON đã xuất; không có engine nào khác mặc nhiên được khai nhận loại này. Thêm consumer phải cập nhật hợp đồng sau duyệt.
- Phiên bản payload `1`; thêm tùy chọn giữ số, đổi không tương thích tạo mã `ho_so_doi_chieu_2`. Schema nguồn dự kiến `_chung/contract/ho_so_doi_chieu.schema.json`, tạo ở DC-1 **sau duyệt**, chép vào gói và test so SHA-256.
- Loại này là trung gian, **không ghép trực tiếp vào cột ngăn** theo API v1. Bước xuất trả `truong` tĩnh gồm tệp JSON/PDF, kết luận, số đếm và cờ kiểm/chặn (§2.1 phiếu DC-P).

### 5.2 Phong bì đề xuất

Mẫu DEMO dưới đây chỉ minh họa, `tep_id`, băm và kích thước phải được thay bằng giá trị đo từ tệp thật trong CoreGia khi viết fixture. Không dùng mẫu như kết quả đã tải tệp thành công.

```json
{"loai": "ho_so_doi_chieu", "ho_so_doi_chieu": {
  "phien_ban": 1,
  "ma_cap": "DEMO-cap-001",
  "giai_doan": "da_so",
  "nguon": {
    "word": {"tep_id": "DEMO-word", "phien_ban": "DEMO-1", "bam": "<sha256 bytes DOCX>"},
    "ban_ky": {"tep_id": "DEMO-ban-ky", "phien_ban": "DEMO-1", "bam": "<sha256 bytes PDF>"}
  },
  "ho_so": {"tep_id": "DEMO-ho-so", "ten": "DEMO-ho-so.json", "mime": "application/json", "kich_thuoc": 0},
  "bam_ho_so": "<sha256 bytes JSON ho so>",
  "bam_bo_quy_tac": "<sha256 snapshot bo>",
  "phien_ban_engine": "e_doi_chieu 0.1.0",
  "tom_tat": {
    "so_diem": 1, "so_nghiem_trong": 1, "so_can_xem": 0,
    "so_hinh_thuc": 0, "so_nhieu_ocr": 0,
    "so_vung_sua_tay": null, "so_trang_ocr_kem": null
  },
  "kiem_tra": {
    "doc_hai_ban": "dat", "so_van_ban": "dat", "quy_tac_cung": "dat",
    "trang": "chua_kiem", "lech_dau": "chua_kiem",
    "sua_tay": "chua_kiem", "phan_loai_ai": "chua_kiem"
  },
  "da_kiem_du": false,
  "ket_luan": null,
  "de_nghi_chan": true,
  "canh_bao": ["DEMO; chưa kiểm vùng sửa tay và chưa đủ căn cứ phân trang bản Word."]
}}
```

`giai_doan` dự kiến: `da_nhan`, `da_so`, `da_quet_anh`, `cho_ai`, `da_hau_kiem`, `da_tong_hop`. `kiem_tra` dùng `dat`, `khong_dat`, `chua_kiem`, `khong_ap_dung`; `khong_ap_dung` chỉ khi bộ chính sách được duyệt cho phép, có lý do trong snapshot. Không dùng nó để lách kiểm bắt buộc. `ket_luan` là `null` trước tổng hợp hoặc một trong năm mã ở phiếu §2.1. Đã biết lệch nghiêm trọng giữ nguyên trong snapshot và số đếm ngay cả khi chưa kiểm đủ.

Trần phong bì ≤ 64 KiB JSON UTF-8; snapshot JSON ≤ 20 MiB, tối đa 10.000 điểm. Không nhét toàn văn, ảnh base64, toàn bộ điểm hoặc prompt vào phong bì. Mọi băm runtime dạng `sha256:<64 hex>`, mọi tham chiếu tệp có metadata thật; thiếu/sai thì lỗi, không chấp nhận placeholder như mẫu. Phong bì không tự khai danh tính người dùng/quyền bằng `ma_cap` hoặc metadata nguồn.

### 5.3 Snapshot và quan hệ kiểm bằng Python

Tệp `ho_so` trong kho Core chứa dữ liệu đủ để tái lập kết quả; không phải tệp bền trên máy engine:

| Thành phần | Nội dung / ràng buộc |
|---|---|
| Hai bản nguồn | Tham chiếu Word/PDF gốc và phiên bản/băm; hai phong bì `van_ban_tai_lieu` nguyên vẹn hoặc tham chiếu+băm JSON của chúng; ảnh trang/bản chuẩn phân trang nếu có. Kiểm quan hệ tới bytes nguồn và quyền Core cấp |
| Văn bản/cấu trúc | Nguyên văn bất biến, bản chuẩn hóa và ánh xạ offset Unicode `[bat_dau, ket_thuc)` về nguồn, bảng/ô rỗng/ô gộp; không bịa số trang/hộp cho DOCX chưa render |
| `diem_lech` | Mã ổn định, phép so, nguyên văn/offset/vị trí hai bên, nhóm lệch dấu, vùng bảo vệ, quy tắc trúng, `muc_san` Python, mức cuối/lý do/nguồn. Mức: `nghiem_trong`, `can_xem`, `hinh_thuc`, `nhieu_ocr`; ứng viên chưa phân loại giữ cờ rõ |
| Bằng chứng OCR/AI | Đúng mã điểm, băm cặp/trang/vùng; trích dẫn hai bên kiểm lại được, model/nguồn Local, phiên bản prompt; cờ nghi ngờ không thay kết quả OCR lại. Không cho AI thay sàn/quyền/băm |
| Sửa tay/trang OCR kém | Danh sách vùng, trang và hộp đúng hệ tọa độ, ảnh cắt có quyền; nhật ký trang thực sự đã quét, phương pháp/phiên bản detector, mẫu số/ngưỡng đã đo. Không đọc chữ tay, không coi chưa quét là không có vùng |
| Bộ và nguồn gốc | Snapshot/băm bộ quy tắc, từ điển, ngưỡng và phiên bản cấu hình; băm tệp gốc khác băm văn bản; dữ liệu kiểu tiền luôn `{so, tien_te}`, ngày `YYYY-MM-DD` |
| Kết luận/số đếm | Khớp phong bì và mọi điểm; chỉ Khớp khi kiểm bắt buộc đầy đủ. Thiếu kiểm → chưa đối chiếu được và đề nghị chặn bảo thủ; lỗi OCR/nguồn không được đổi thành Khớp |

Không ghép danh sách điểm theo vị trí mảng hoặc để mất đoạn không căn được; edit script phải tái dựng được hai bên. Không dùng `muc_san` để hạ mức cứng bằng AI; điểm còn lại chỉ được xếp nhiễu khi có bằng chứng theo DAC-TA §4. Vùng quy tắc cứng không bao giờ thành nhiễu. Không tự xóa điểm khi gom trang OCR kém hoặc ẩn bộ lọc UI.

### 5.4 Qua Local AI, đầu vào cặp và quyền Core

Trong phần **đã cho phép mở** `yeu_cau_ai.chuyen_tiep`, dùng khóa `doi_chieu` gồm `phien_ban`, `ma_cap`, tham chiếu+băm tệp hồ sơ, băm bộ và băm ngữ cảnh AI. Mục tiêu ≤ 4 KiB, trần chung vẫn 64 KiB. Hỏi AI giữ nguyên sang `tra_loi_ai`; model không được sinh lại metadata này. `tai_lieu` chứa ngữ cảnh có phân biệt trái/phải, hậu kiểm kiểm offset tại đó rồi ánh xạ về nguồn. Không đổi schema `yeu_cau_ai`/`tra_loi_ai`, không gửi Cloud.

API v1 mỗi bước chỉ nhận một phong bì. Đầu vào cặp đề xuất là `tep` JSON do Core/module lập chứa tham chiếu+băm các tệp được cấp cho việc, **không phải** phong bì hai đầu vào mới. Cần Core chốt cửa chung ghép nguồn/quyền mở tệp con và vòng đời giữa các bước (C-DC-02); SDK có `mo_tep` không chứng minh tệp bất kỳ đều được mở. Test CoreGia không chứng nhận quyền thật. Chưa có cửa thì runtime từ chối; không đọc đường máy, gọi engine khác hoặc truy cập CSDL.

Snapshot/kết quả/ảnh lưu qua kho tệp Core, chỉ mục/cấu hình qua `Ngan`; RAM tạm khi chưa có SDK 2.1, không đệm bền. Nhật ký xác nhận thuộc ngăn/cửa Core chỉ-thêm có danh tính/quyền/CAS, **không** đặt trong hồ sơ máy rồi coi là đã xác nhận hợp đồng. Module sở hữu chặn/mở hiệu lực và sự kiện nghiệp vụ.

## 6. MASK-2c-P — profile Local nhận diện thực thể (lead duyệt 15/11/2026 là quy ước kỹ thuật trong trường mở chuyen_tiep; không thêm loại/trường bắt buộc)

*15/11/2026; chỉ tài liệu. Nhãn lịch sử ở đầu sổ không áp dụng mục này: **đây là đề xuất mới, chưa duyệt/kích hoạt**. Quyết định của Anh (nguyên văn): "Thêm AI cục bộ". Quyết định về mục tiêu không được hiểu là đã duyệt mọi chi tiết payload sau đây.*

Dùng nguyên ba loại đã có: `yeu_cau_ai` cho văn bản **gốc chỉ Local**, `tra_loi_ai` cho kết quả Local, `van_ban_da_che` cho đầu ra cuối Mask. Không tạo mã loại mới, không sửa schema chung hoặc thêm trường bắt buộc cấp payload trong MASK-2c-P. Chi tiết chuỗi/kiểm/offset/lát ở `e_mask/docs/GIAO-CODEX-e_mask.md` §6 và AI-9 trong phiếu Hỏi AI.

Đề xuất khóa mới trong phần **đã mở** `yeu_cau_ai.chuyen_tiep.mask_2c`, được Hỏi AI trả nguyên trong `tra_loi_ai.chuyen_tiep.mask_2c`:

| Khóa | Nội dung / nguồn tạo |
|---|---|
| `phien_ban` | Integer 1, phiên bản profile, không thay phiên bản loại chung |
| `ma_yeu_cau` | Mã opaque Core cấp, cùng yêu cầu/quyền xuyên ba bước, không đưa vào model |
| `nha_cung_cap_bat_buoc` | Hằng `local`; thiếu/khác thì AI-9 và bước Mask hậu kiểm từ chối |
| `ho_so`, `bam_ho_so` | Tham chiếu tệp snapshot ở kho Core (`tep_id,ten,mime,kich_thuoc`) + SHA bytes; tên kỹ thuật an toàn, không path/URL/tên gốc. Snapshot gồm gốc, bản quy tắc, edit map và kế hoạch đoạn |
| `bam_goc`, `bam_da_che_quy_tac`, `phien_ban_map` | SHA UTF-8 từng chuỗi bất biến và phiên bản quan hệ offset; không nhầm băm tệp nguồn với băm chuỗi |
| `chi_so_doan`, `so_doan`, `bat_dau_doan`, `ket_thuc_doan`, `bam_doan` | Chỉ số 0-based, số đoạn, khoảng Unicode code point trong gốc, SHA UTF-8 đoạn. Core lập kế hoạch phủ đủ và ghim, Mask hậu kiểm kiểm lại |
| `he_offset` | Hằng `unicode_code_point`, khoảng nửa mở `[bat_dau,ket_thuc)`; offset AI tương đối đoạn, cộng `bat_dau_doan` để về gốc |
| `bam_prompt`, `bam_khuon`, `bam_profile` | SHA của prompt UTF-8, schema và profile JSON chuẩn hóa; profile là cấu hình cố định của tác vụ (loại/mức/span/trần/đoạn), không tự chứa băm chính nó. Snapshot giữ bản chuẩn để tái tính, cùng mã/phiên bản prompt sẵn có |
| `tap_phan_hoi`, `bam_tap_phan_hoi` (tùy chọn) | Tham chiếu+băm tệp tổng hợp do Core tạo, chỉ có trên lượt giao cuối cho bước 3. Chứa nguyên mọi yeu_cau_ai/tra_loi_ai đã được cấp quyền, dấu nguồn Core và kế hoạch đoạn, không được model tạo |

Mỗi yêu cầu/đáp AI-9 giữ nguyên `chuyen_tiep`; **Core** tạo bản giao cuối bổ sung tham chiếu tập phản hồi vào bản sao của phản hồi cuối, lưu cả bản gốc để kiểm chuyển tiếp nguyên vẹn và provenance. Phần bổ sung này phải do cửa tin cậy Core chứng thực; không là quyền cho caller tự thay chuyen_tiep. Không đòi e_hoi_ai đọc ngăn/tệp riêng của Mask. `bam_dau_vao` của `tra_loi_ai` vẫn theo mã hiện tại: SHA JSON chuẩn hóa **toàn phong bì yêu cầu**, không đổi sang `bam_goc`/`bam_doan`. Core lưu bytes chuẩn để Mask kiểm lại.

Mục tiêu metadata ≤4 KiB, trần toàn `chuyen_tiep` vẫn 64 KiB JSON UTF-8, khuôn ≤32 KiB. Không đưa gốc, alias mapping hoặc danh sách thực thể vào phần chuyển tiếp. Quy ước JSON chuẩn hóa: UTF-8, `ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False`, từ chối khóa trùng; SHA runtime `sha256:<64 hex>`. Mỗi tham chiếu phải có bytes/kích thước/băm thực ở Core, có quyền mở giữa các bước; ví dụ placeholder không dùng để nhận đạt.

**Không thêm trường mới vào `tra_loi_ai`:** `du_lieu` (phần đã cho mang schema của yêu cầu) dùng `{da_quet_het,thuc_the[]}`; mỗi thực thể có `loai,nguyen_van,bat_dau,ket_thuc,muc`, khuôn chặt theo phiếu Mask §6.3. Đây là nội dung nhạy cảm **nội bộ Local/Core/Mask**, không đầu vào Cloud. AI-9 kiểm từng span chứ không bắt metadata nằm trong câu trích, giữ trích dẫn từng vị trí lặp. Rỗng hợp lệ có `trang_thai=khong_thay_can_cu`, `kiem_trich_dan.dat=true`; không tự chứng minh an toàn khi thiếu nguồn/đủ đoạn/hoàn tất. Sai khuôn, timeout/ChuaRo, nguồn khác Local, thiếu map/đoạn → không phát hành.

**Không thêm cờ an toàn caller tự khai vào `van_ban_da_che`:** dùng contract hiện có khi hậu kiểm cả hai lớp thực sự đạt. Chứng cứ lớp 2 gắn băm bản cuối/nguồn bước 3 lưu do Core quản, cửa Cloud kiểm chứng cứ này và từ chối đầu ra lớp 1 cũ thiếu chứng cứ. Không gửi ma_yeu_cau/chuyen_tiep/snapshot/băm/trích dẫn gốc ra Cloud; chỉ nội dung cuối đã che, prompt chứa dữ liệu cũng phải che. BAT_CLOUD vẫn False. Mục này chờ duyệt chi tiết profile và cửa Core; không đổi hợp đồng kỹ thuật API v1/SDK 2.0 đã khóa.
