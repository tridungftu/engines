# e_mask — Che định danh: yêu cầu và hiện trạng

*Lập ngày 08/11/2026.*

**Căn cứ:**
- `QUYET-DINH-CUOI-e_mask.md` (06/11, hợp nhất 20:35, 21:00, 21:05); quyết định này thay phương án trong `PHIEU-ENGINE-e_mask.md` và các điểm trái với nó trong `TOM-TAT-SCHEMA-MASK-CHO-ANH.md`.
- `PHIEU-MASK-CHAY-THU-DEMO.md`.
- Yêu cầu chung: `..\_chung\docs\YEU-CAU-CHUNG-ENGINE.md`.

**Hiện trạng** đối chiếu `ma-nguon\CHANGELOG.md` (tới MASK-J8, 07/11). Ký hiệu: ✅ có, đã kiểm bằng mock / 🟡 một phần / ❌ chưa có.
**Mọi kiểm tra tới nay đều bằng mock hoặc vector; chưa chạy trên PostgreSQL hay Core thật.**

## 0. Kết luận
- **Engine Mask = lõi Mask file v2 (phần mềm nội bộ) + API.** Không lấy phần OCR. Bảng định danh – bí danh nằm trong **CSDL Core**. Bí danh dạng `[[...]]`: đối tác có mã Junsky dùng `[[<mã Junsky>]]`; định danh khác dùng mã tự sinh.
- Làm theo **8 mẫu trao đổi**: 4 mẫu văn bản, 4 mẫu tệp. Mở che bắt buộc có **mã yêu cầu**, đúng module và đúng người gửi.
- **Đã có (mock):** lõi che/mở che văn bản (mẫu 1–4), kho định danh và danh sách chờ, công cụ chuyển danh mục, vòng nhận việc.
- **Chưa có:**
  - che tệp Word/Excel (mẫu 5–8, lát 8);
  - màn duyệt danh sách chờ;
  - màn thử DEMO (chờ duyệt phiếu);
  - J8b;
  - chạy thật.
- **Kho bí danh hiện nằm bằng mã riêng trong Core** (`mask.py`, `kho_mask.py`, `routes_mask.py`, SQL 113, 117–120; `kenh_engine` có nhánh `goi_mask`). Theo cổng chung, phần này phải thành **ngăn dữ liệu của engine** (`eng_e_mask`), đi qua thao tác ngăn chung.

## 1. Yêu cầu

### 1.1 Phạm vi và luồng
| Mã | Yêu cầu |
|---|---|
| MK-1 | Lõi Mask v2 + API; **tách bỏ OCR**. Giữ mã che Word/Excel. Kiểm kê phụ thuộc (gồm cryptography) |
| MK-2 | **Luồng chuẩn:** module gửi văn bản hoặc tệp qua Core → Mask che theo bảng định danh – bí danh → cụm nghi ngờ **vẫn che bằng bí danh tạm** và vào danh sách chờ → trả kết quả đã che kèm **mã yêu cầu** → Admin duyệt danh sách chờ → ghi vào CSDL |
| MK-3 | **Luồng tệp tham khảo AI:** Word/Excel che → ra AI → AI trả tệp đã sửa → module gửi tệp kèm mã yêu cầu → Mask đổi bí danh về tên gốc → trả **đúng module đã gửi** |
| MK-4 | **Đầu ra:** mặc định trả văn bản đã che. Riêng Word và Excel, module được chọn nhận lại tệp cùng định dạng. PDF (có lớp chữ hoặc scan) chỉ trả văn bản |
| MK-5 | Tệp scan hoặc ảnh: Core điều phối OCR → Mask (mẫu 1). Mask không tự nhận dạng chữ |
| MK-6 | Mốc này không nối Cloud. Bước "AI sửa tệp" do lead giả lập. Gửi Cloud thật thuộc Hỏi AI bản 2 |

### 1.2 Quy tắc dữ liệu (các câu đã chốt)
| Mã | Quy tắc |
|---|---|
| MK-10 | Chỉ dữ liệu cần che (tên, địa chỉ, MST…) lưu trong CSDL Core, gắn sẵn bí danh. Không còn bảng đối chiếu trong bộ nhớ |
| MK-11 | Bí danh `[[<mã Junsky>]]` cho đối tác có mã Junsky; mã tự sinh theo loại cho định danh khác (ví dụ `[[CT-0001]]`). Hai loại **không trùng tiền tố**; lead đề xuất bộ tiền tố |
| MK-12 | **Mã yêu cầu** do Core cấp khi che. Gắn module, người gửi, tài liệu. Trạng thái: đang xử lý / đã đóng. **Bắt buộc khi mở che.** Từ chối khi khác module, khác người gửi hoặc mã không tồn tại. Không gửi mã cho Cloud |
| MK-13 | Mở che tra ngược bảng chung (bí danh chính thức + cột tạm). Nhận diện mềm: không phân biệt hoa thường, bỏ dấu cách thừa, ghép bí danh bị tách đoạn |
| MK-14 | Bí danh không mở được: **không đoán**. Trả danh sách kèm vị trí; không công bố là mở đầy đủ |
| MK-15 | Khi duyệt cụm chờ: cấp bí danh mới, bí danh tạm cũ lưu ở cột tạm. Từ chối: xóa khỏi danh sách |
| MK-16 | Dọn bí danh tạm chỉ khi không còn mã yêu cầu nào "đang xử lý" dùng nó. Tệp đã ra AI giữ trạng thái "đang xử lý" tới khi mở che xong hoặc module đóng việc |
| MK-17 | Phạm vi bí danh: chung toàn tập đoàn. Người duyệt: **Admin** |
| MK-18 | Cụm gốc mới: ghi thẳng vào danh sách chờ trong CSDL. **Không** trả trong phản hồi, không vào nhật ký, không vào contract. Phản hồi chỉ báo số cụm chờ duyệt |
| MK-19 | Bảng định danh nằm trong khối dữ liệu riêng, giới hạn quyền, không mã hóa cột |
| MK-20 | Điều kiện đi Cloud (khi bật ở bản 2), thiếu một điều kiện là chặn: engine sẵn sàng; không sót định danh; tiền và ngày giữ nguyên; Mask không lỗi. Chỉ nội dung đã che ra ngoài |
| MK-21 | Giới hạn: văn bản ≤ 500.000 ký tự; định danh đã biết ≤ 500 mục, mỗi giá trị ≤ 300 ký tự, nhóm ≤ 20 ký tự. Trần dung lượng tệp và trần đầu ra: lead trình sau khi thử DEMO. Vượt trần thì từ chối, không cắt ngầm |
| MK-22 | Test chỉ dùng DEMO. Chuyển danh mục thật làm riêng, Anh xác nhận số dòng trước và sau |

### 1.3 Tám mẫu trao đổi
- **Văn bản:**
  - Mẫu 1: gửi che.
  - Mẫu 2: kết quả che: mã yêu cầu, văn bản đã che, phần còn sót (phải rỗng), kiểm tiền/ngày, số chỗ đã thay, bí danh đã dùng (nguồn chính thức/tạm), số cụm chờ, cảnh báo.
  - Mẫu 3: gửi mở che, kèm mã yêu cầu và cờ "đóng việc sau khi mở".
  - Mẫu 4: kết quả mở che: văn bản, số chỗ đã mở, bí danh chưa mở kèm vị trí, trạng thái mã yêu cầu.
- **Tệp:**
  - Mẫu 5: gửi che tệp docx / xlsx / pdf có lớp chữ; chọn dạng trả về.
  - Mẫu 6: kết quả che tệp, kèm danh sách vùng đã quét.
  - Mẫu 7: gửi mở che tệp.
  - Mẫu 8: kết quả mở che tệp.
- **Tiêu chí lát 8 (tệp):**
  - Không sót ở chỗ ẩn. Word: đầu/chân trang, ghi chú, bình luận, lịch sử sửa, thuộc tính tệp. Excel: tên sheet, sheet ẩn, ô ẩn, bình luận, nhãn biểu đồ, thuộc tính tệp.
  - Mở che tệp đã bị AI sửa: khôi phục đúng, kể cả khi bí danh bị đổi hoa thường, thêm dấu cách hoặc bị tách đoạn; giữ đoạn AI thêm mới.
  - Tiền và ngày, kể cả ô số Excel, giữ nguyên. Không còn tệp gốc trên đĩa.

### 1.4 Tám lát, theo thứ tự
1 → 2 → 3 → 4 → 8 → 6 → 7; lát 5 (màn thử DEMO, chỉ Admin) chạy song song lát 3–4.

## 2. Hiện trạng

| Yêu cầu / lát | Trạng thái | Bằng chứng |
|---|---|---|
| Lát 1 — lõi v2 bỏ OCR (MK-1) | ✅ | MASK-1; gói 0.1.0-demo.1 (G3-GOI-27); `che_van_ban.py`, `nguon\` |
| Lát 2 — kho định danh, danh sách chờ, chuyển danh mục (MK-10, 11, 19, 22) | ✅ mock | MASK-2 (`c8ef19c1`, `5a1f007d`). Công cụ chuyển danh mục có chạy thử, chỉ báo số đếm (`tu-core-cu\tools\chuyen_danh_muc_mask.py`). SQL 113, 117–120 **nằm trong Core** |
| Lát 3 — che/mở che văn bản, mẫu 1–4 (MK-12 … 14, 18, 21) | ✅ mock | MASK-3A (chặn khi còn sót, giữ tiền/ngày, ≤ 500.000 ký tự); 3C (ghi gặp lại cụm, chống đếm lặp); 3E/3E-BS (nối kho qua Core, gửi lại tối đa 3 lượt). **Chưa xác nhận tính nguyên tử trên PostgreSQL** |
| Lát 4 — danh sách chờ + màn duyệt Admin (MK-15, 16) | 🟡 | Logic duyệt/dọn có ở kho; **màn duyệt chưa có** |
| Lát 8 — che/mở che tệp, mẫu 5–8 | ❌ | Chưa làm |
| Lát 6 — công bố và đóng gói, 8 contract | 🟡 | G3-GOI-27 có gói; G3-GOI-30 mới có tài liệu. Contract hiện chỉ có `du_thao.json` |
| Lát 7 — bài test 11 bước | ❌ | |
| Lát 5 — màn thử DEMO | 🟡 | `chay_thu_mask.js` **nằm trong Core**; phiếu `PHIEU-MASK-CHAY-THU-DEMO.md` chờ Anh duyệt |
| Vòng nhận việc | ✅ mock | MASK-J8 (`0a470d88`, `87d93e75`). **J8b** (đối soát mất xác nhận phía Core) **chưa làm** |

## 3. Bài test tổng thể cuối
11 bước, ước 135 phút, chỉ DEMO; nội dung đầy đủ ở `QUYET-DINH-CUOI-e_mask.md` §4.

## 4. Thư mục
| Thư mục | Nội dung |
|---|---|
| `ma-nguon\` | 29 tệp: `che_van_ban.py`, `kho_bo_nho.py`, `kho_qua_core.py`, `vong_doi.py`, `chay.py`, `nguon\` (lõi Mask v2), `contract\du_thao.json`, `tests\` |
| `tests-tu-core\` | 16 test cũ trong Core (kho, phiên, HTTP, kênh, chốt lượt, màn chạy thử) |
| `tu-core-cu\tools\` | `chuyen_danh_muc_mask.py` |
| `tu-core-cu\phia-core\` | Bản sao mã riêng Mask trong Core: `mask.py` (import `engines.e_mask`, **đã hỏng sau khi tách**), `kho_mask.py`, `routes_mask.py`, `chay_thu_mask.js`, SQL 113, 117, 118, 119, 120 |
| `docs\` | Quyết định cuối, phiếu, phiếu màn chạy thử, khảo sát 3B/3J, tóm tắt schema |

## 5. Thứ tự đề xuất
1. Chuyển kho bí danh sang **ngăn của engine** theo cổng chung. Thảo luận với lead Core để giữ dữ liệu và SQL đã có.
2. Lát 4 (màn duyệt Admin, là giao diện của engine) và lát 5 (màn thử DEMO).
3. Lát 8: tệp Word/Excel.
4. Lát 6 (8 contract, Anh duyệt tên) → lát 7 (bài 11 bước).

## 6. Chờ Anh
- Duyệt `PHIEU-MASK-CHAY-THU-DEMO.md`.
- Tên 8 contract: lead trình trước khi đăng ký.
- Trần dung lượng tệp và trần đầu ra: lead trình sau khi thử DEMO.
- Bộ tiền tố mã tự sinh: lead đề xuất.
