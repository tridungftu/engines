# 57 · Đặc tả engine Đối chiếu bản ký (`e_doi_chieu`)

*Bản chép từ tài liệu Project `claude/57-dac-ta-engine-doi-chieu-ban-ky.md` (lập 31/10/2026), chép ngày 08/11/2026 cho project engine riêng. Khi khác nhau, bản trong Project là bản gốc.*

**Trạng thái:** bản nháp đặc tả để Anh duyệt, thuộc bộ chuẩn Core (cổng C, TL 55 §3). **Chưa lập trình khi Anh chưa duyệt** (TL 54 §14 #2).

**Căn cứ:**
- Yêu cầu và 4 lựa chọn Anh chốt ngày 31/10/2026 (mục 1).
- Tài liệu liên quan: TL 41 (CRM-G4 Ký kết, CRM-G5 Kiểm mẫu bản ký), TL 42 §8 (Hộp Ký kết), TL 48 (cổng AI), TL 54–55 (chuẩn Core), TL 56 (Kho tài liệu, `e_tra_cuu`).

**Quy ước:**
- Mọi tên schema, bảng, route, capability chỉ là **đề xuất**: tiếng Việt không dấu, snake_case; lead chốt sau G0.
- Chỗ chưa có căn cứ ghi **[CẦN ANH XÁC NHẬN]**; câu hỏi gom ở mục 13.

**Bảo mật:**
- Tài liệu không chứa dữ liệu thật.
- Ngưỡng ghi **[CẦN ĐO]** là chưa có số. Không đưa con số độ chính xác nào khi chưa đo.

**Lưu ý khi đọc ở project engine (08/11):**
- Phần thuộc Core (schema `loi_doi_chieu`, quy trình, route, màn) phải đi qua **cửa chung** theo `..\..\_chung\docs\YEU-CAU-CHUNG-ENGINE.md`.
- Engine không gọi `e_hoi_ai` trực tiếp; Core điều phối bước phân loại.

---

## 0. Kết luận

- **`e_doi_chieu` là engine thứ 7 của Core.** Engine so **bản Word chuẩn** (bản gửi ký) với **bản đã ký** (PDF scan qua OCR) và báo mọi điểm khác nhau.
  - Engine dùng chung, không gắn riêng một module.
  - Điểm vào: icon **"Đối chiếu bản ký"** trong Kho tài liệu, Hộp Ký kết của CRM (G4/G5), các module M2, M4, M9.
- **So theo 2 lớp:**
  - **Lớp 1 — Python so từng chữ.** Lớp này không bỏ sót điểm nào. Python tự xếp mức **Nghiêm trọng** cho mọi lệch về số, ngày, tiền, tỷ lệ, bên ký, mã số.
  - **Lớp 2 — Local AI lọc.** Với từng điểm lệch còn lại, AI trả lời: đây là lỗi OCR hay sửa thật, và quan trọng đến đâu. AI **không được ẩn** điểm lệch mà Python đã xếp Nghiêm trọng.
- **Lỗi dấu tiếng Việt** (OCR mất dấu hoặc sai dấu) xử lý theo 5 bước ở mục 4. Nguyên tắc cốt lõi:
  - Chỉ coi là lỗi OCR khi **từ OCR đọc ra không phải từ có nghĩa**.
  - Hai từ đều có nghĩa (ví dụ *thuê/thuế*, *lãi/lại*, *phạt/phát*) thì **không bao giờ tự bỏ qua**.
- **Sửa tay, gạch xóa trên bản ký:** máy phát hiện vùng có vết mực tay (ngoài chữ ký và con dấu), cắt ảnh vùng đó đưa vào báo cáo cho người xem. Máy không tự đọc chữ tay.
- **Khi có lệch Nghiêm trọng hoặc vùng sửa tay:**
  - gửi báo cáo cho người dùng xử lý;
  - **chặn hiệu lực hợp đồng tới khi người dùng xác nhận** từng điểm;
  - **chỉ dùng Local AI**, không ra Cloud.

## 1. Anh đã chốt (31/10/2026)

| # | Câu hỏi | Anh chốt |
|---|---|---|
| 1 | Đóng gói | **Engine trong Core + icon "Đối chiếu bản ký"**; CRM-G5, M2, M4, M9 gọi chung |
| 2 | Phương pháp | **Python so chữ + Local AI lọc**; *lưu ý xử lý trường hợp OCR thiếu dấu hoặc sai dấu* → mục 4 |
| 3 | Sửa tay / gạch xóa / ký nháy | **Đánh dấu vùng, cắt ảnh để người xem** |
| 4 | Khi lệch Nghiêm trọng | **Báo cáo và gửi người dùng xử lý; chặn hiệu lực khi người dùng chưa xác nhận** |
| 5 | AI | **Local AI** (theo yêu cầu gốc) |

## 2. Vị trí trong Core và quan hệ với tài liệu đã có

| Thành phần | Vai trò |
|---|---|
| **`e_doi_chieu`** (mới) | Đọc DOCX, chuẩn hóa, căn đoạn, so chữ, áp quy tắc cứng, phát hiện vùng sửa tay. **Không đọc/ghi CSDL**, không giữ mật khẩu hay khóa (TL 55 §12) |
| `e_ocr` | Chuyển bản scan thành `van_ban_tai_lieu.v1`. **Cần thêm:** tọa độ từng từ và cờ ký tự nghi ngờ nếu ABBYY xuất được ([Kiểm ở G0]) |
| `e_hoi_ai` | Gọi Local AI để phân loại điểm lệch; khóa **chỉ Local** cho mọi lượt của engine này |
| Core — Kho tài liệu (TL 56) | Lưu tệp gốc, phiên bản, liên kết *bản ký ↔ bản Word*; hiện icon "Đối chiếu bản ký" |
| Core — Workflow Runner | Chạy quy trình `doi_chieu_ban_ky` (mục 3) dưới dạng việc nền, trả 202 + `viec_id` |
| Core — Database Manager | Lưu kết quả vào schema mới `loi_doi_chieu` (mục 8) |
| CRM (TL 41) | **CRM-G5 đổi sang gọi `e_doi_chieu`** thay cho "#6 chế độ đối chiếu". Giữ nguyên quy tắc kiểm mẫu tự điều chỉnh tỷ lệ của G5. CRM-G6 "Hiệu lực" bị khóa khi đối chiếu chưa xác nhận |
| M2, M4, M9 | Nhận sự kiện kết quả. Hợp đồng còn điểm chưa xác nhận ở trạng thái **"Chờ xác nhận đối chiếu"** |

**Khác với CRM-G5 hiện tại:**
- G5 chỉ so **tham số** (giá, lịch thu, bên).
- `e_doi_chieu` so **toàn văn**, bắt được cả sửa chữ trong điều khoản (phạt, bảo hành, chấm dứt), và áp dụng cho mọi hợp đồng, không chỉ hợp đồng sinh từ mẫu CRM.

## 3. Quy trình `doi_chieu_ban_ky`

| Bước | Việc | Ai làm |
|---|---|---|
| 1 | **Nhận cặp tệp.** Bản Word lấy từ kho nếu đã có (CRM xuất DOCX ở G3, hoặc bản "chờ ký" trong Kho tài liệu theo số hợp đồng); chưa có thì người dùng tải lên. Bản ký là PDF. Tính mã băm; cặp đã đối chiếu thì mở kết quả cũ, không chạy lại | Core |
| 2 | **Kiểm bản Word.** Còn *track changes* chưa chấp nhận hoặc còn comment → dừng, hỏi người dùng dùng bản nào. Có nhiều phiên bản → mặc định bản mới nhất ở trạng thái chờ ký; người dùng đổi được | `e_doi_chieu` + Core |
| 3 | **Lấy chữ bản ký.** PDF có lớp chữ thật thì lấy thẳng; PDF scan thì gọi `e_ocr`, giữ tọa độ từng từ và cờ nghi ngờ (nếu có). OCR lỗi → kết quả **"Chưa đối chiếu được"**, **không bao giờ coi là khớp** (giữ quy tắc CRM-G5) | Core → `e_ocr` |
| 4 | **Kiểm trang.** So số trang và thứ tự Điều/Khoản giữa hai bản; báo thiếu, thừa hoặc đảo trang | `e_doi_chieu` |
| 5 | **Chuẩn hóa hai bên.** Unicode NFC; khoảng trắng; ngắt dòng và ngắt từ cuối dòng; dấu nháy, gạch nối; bỏ đầu trang, chân trang, số trang; chuẩn kiểu đánh số (1. / 1) / a.) | `e_doi_chieu` |
| 6 | **Căn đoạn theo cấu trúc** (Điều → Khoản → câu; bảng → dòng → ô), rồi **so từng chữ** trong mỗi cặp đoạn. So hai lượt, **có dấu** và **bỏ dấu** (mục 4) | `e_doi_chieu` |
| 7 | **Python xếp loại theo quy tắc cứng** (mục 5.1) | `e_doi_chieu` |
| 8 | **Local AI phân loại** các điểm chưa được quy tắc cứng xếp (mục 5.2) | `e_hoi_ai` (chỉ Local) |
| 9 | **Phát hiện vùng sửa tay** trên ảnh trang (mục 6) | `e_doi_chieu` |
| 10 | **Lập báo cáo, gửi người dùng, chặn hiệu lực nếu cần** (mục 7). Phát sự kiện | Core |

## 4. Xử lý OCR thiếu dấu hoặc sai dấu

**Vấn đề:**
- OCR tiếng Việt hay nhầm dấu: mất dấu nặng (*ạ→a*), nhầm hỏi với ngã (*ả↔ã*), mất móc (*ư→u, ơ→o*), *đ→d*, *ă/â→a*, *ệ→ê*.
- Báo tất cả thì người dùng ngập trong lệch giả.
- Tự bỏ hết thì lọt các cặp từ đổi nghĩa thật: **thuê/thuế**, **lãi/lại**, **phạt/phát**, **bán/bàn**, **không/khống**, **hạn/hàn**.

**Năm bước, theo thứ tự:**
1. **Tách nhóm "chỉ lệch dấu".**
   - Điểm lệch biến mất khi bỏ dấu cả hai bên thì xếp vào nhóm lệch dấu.
   - Điểm vẫn lệch sau khi bỏ dấu là lệch chữ thật, đi tiếp như mọi điểm khác.
2. **Kiểm từ có nghĩa.** Với mỗi từ lệch dấu, tra **từ điển âm tiết và từ tiếng Việt**:
   - **Từ OCR không có nghĩa** (ví dụ *hơp đông*) → coi là **lỗi OCR có căn cứ**, xếp *Nhiễu OCR*. Điểm này ẩn mặc định, xem lại được.
   - **Cả hai đều có nghĩa** → đây là **cặp đổi nghĩa**. Không tự bỏ qua; chuyển sang bước 3.
3. **Cặp đổi nghĩa — xét ngữ cảnh và bằng chứng:**
   - Gửi Local AI câu chứa từ đó của cả hai bản. AI trả lời *lỗi OCR* / *sửa thật* / *không chắc*, kèm lý do.
   - Lấy **cờ ký tự nghi ngờ** của ABBYY tại vị trí đó (nếu có) làm thêm một căn cứ.
   - **OCR lại riêng vùng chữ đó** ở độ phân giải cao hơn. Có thể dùng thêm bộ OCR thứ hai (`ocr-dual-release`) nếu Anh cấp vị trí thư mục (TL 55 §9). Hai lần đọc cùng ra từ của bản Word → lỗi OCR.
   - Chỉ xếp *Nhiễu OCR* khi **cả AI và lần OCR lại đều cho kết quả lỗi OCR**. Các trường hợp còn lại xếp **Cần xem**, kèm **ảnh cắt vùng chữ** trên bản scan để người dùng nhìn tận mắt.
4. **Không áp dụng cho vùng quy tắc cứng.** Lệch dấu trong tên bên ký, tên dự án, địa chỉ, số tiền bằng chữ hoặc mã số **luôn lên Nghiêm trọng hoặc Cần xem**, không bao giờ thành Nhiễu OCR (mục 5.1).
5. **Trang OCR kém.** Trang có tỷ lệ lệch dấu vượt ngưỡng **[CẦN ĐO]** được đánh dấu **cả trang "OCR kém – cần xem trang"**, kèm ảnh cả trang, thay vì liệt kê hàng trăm điểm. Các điểm Nghiêm trọng trên trang đó vẫn liệt kê riêng.

**Học dần, có duyệt:**
- Cặp lỗi OCR được người dùng xác nhận nhiều lần sẽ được **đề xuất** vào danh mục `loi_ocr_thuong_gap`. Chỉ nhận cặp **không đổi nghĩa** (ví dụ *hơp→hợp*).
- Admin duyệt rồi lần sau mới tự xếp Nhiễu.
- Cặp đổi nghĩa **không bao giờ** được đưa vào danh mục này.

## 5. Xếp mức điểm lệch

### 5.1 Quy tắc cứng (Python, AI không ghi đè được)

| Loại lệch | Mức |
|---|---|
| Bất kỳ chữ số nào khác nhau, so sau khi chuẩn dấu phân cách nghìn/thập phân. Nhầm OCR kiểu *0/O, 1/l, 5/S, 8/B* vẫn báo, có ghi chú "nghi nhầm OCR" | **Nghiêm trọng** |
| Ngày, tháng, năm; thời hạn; số ngày | **Nghiêm trọng** |
| Số tiền (bằng số và bằng chữ); đơn vị tiền tệ; tỷ lệ % | **Nghiêm trọng** |
| **Số tiền bằng số không khớp số tiền bằng chữ** ngay trong bản ký, kể cả khi khớp với Word | **Nghiêm trọng** |
| Tên bên ký, người đại diện, chức vụ, MST, STK, địa chỉ, số hợp đồng | **Nghiêm trọng** |
| Thiếu, thừa hoặc đảo trang; thiếu hoặc thừa cả Điều/Khoản | **Nghiêm trọng** |
| Thêm hoặc bớt từ phủ định (*không, chưa, chỉ, trừ, ngoại trừ*) hoặc từ bắt buộc (*phải, được, có thể*) | **Nghiêm trọng** |
| Vùng sửa tay hoặc gạch xóa (mục 6) | **Nghiêm trọng** (chưa biết nội dung) [CẦN ANH XÁC NHẬN — trả lời sau] |

### 5.2 Local AI xếp phần còn lại
- **Cần xem:** thay đổi từ ngữ có thể đổi nghĩa; cặp đổi nghĩa chưa đủ bằng chứng (mục 4 bước 3); AI không chắc.
- **Thay đổi hình thức:** đổi từ đồng nghĩa không đổi nghĩa pháp lý, đổi thứ tự liệt kê. Hiện trong báo cáo nhưng không chặn.
- **Nhiễu OCR:** chỉ khi đúng điều kiện ở mục 4. Ẩn mặc định.
- AI chỉ được **nâng mức**, không được hạ một điểm Python đã xếp.
- Mọi kết luận của AI có lý do và trích câu nguyên văn của hai bản. Python kiểm câu trích; không đúng nguyên văn thì giữ mức **Cần xem**.

### 5.3 Kết luận của một lượt đối chiếu

| Kết luận | Điều kiện |
|---|---|
| **Khớp** | Không có Nghiêm trọng, Cần xem, vùng sửa tay hay trang OCR kém |
| **Khớp – có thay đổi hình thức** | Chỉ có Thay đổi hình thức và/hoặc Nhiễu OCR |
| **Cần xem** | Có Cần xem hoặc trang OCR kém, không có Nghiêm trọng |
| **Lệch nghiêm trọng** | Có ít nhất một Nghiêm trọng hoặc một vùng sửa tay |
| **Chưa đối chiếu được** | OCR lỗi, tệp hỏng, không căn được cấu trúc |

## 6. Phát hiện vùng sửa tay

- Tìm trên ảnh trang các vùng có **vết mực tay**: nét viết tay, gạch ngang chữ in, chữ chèn giữa dòng.
- **Loại trừ** khối chữ ký, con dấu, chữ ký nháy ở lề hoặc góc trang. Nếu Anh muốn **kiểm có ký nháy/đóng dấu giáp lai trên từng trang** thì đó là việc khác [CẦN ANH XÁC NHẬN — trả lời sau].
- Kết quả: trang, tọa độ, ảnh cắt vùng, chữ in bị đè hoặc gạch (nếu xác định được).
- **Máy không tự đọc nội dung chữ tay.** Người dùng xem ảnh rồi ghi lại nội dung sửa nếu là sửa thật.
- Cách phát hiện (xử lý ảnh, hoặc model thị giác Local nếu máy AI có) do lead chọn sau khi **đo ở DC-0** trên bộ mẫu. Chưa có số đo nên chưa cam kết tỷ lệ phát hiện.

## 7. Báo cáo, gửi người dùng, chặn hiệu lực

### 7.1 Màn kết quả (SDK JS, dùng chung mọi điểm vào)
- **Đầu màn:** kết luận (mục 5.3), số điểm theo mức, số vùng sửa tay, số trang OCR kém.
- **Danh sách điểm lệch** lọc theo mức. Mặc định chỉ hiện Nghiêm trọng, Cần xem, Thay đổi hình thức; Nhiễu OCR nằm sau nút "Xem nhiễu OCR (n)".
- **Mỗi điểm hiển thị hai cột:**
  - trái: đoạn bản Word, tô chỗ khác;
  - phải: **ảnh cắt bản scan** đúng vị trí, kèm chữ OCR;
  - kèm vị trí (trang, Điều, Khoản), mức, lý do (quy tắc cứng hoặc lý do của AI).
- **Xác nhận từng điểm** Nghiêm trọng, Cần xem và vùng sửa tay, chọn một trong bốn:
  1. **Lỗi OCR**: bản ký thực tế giống Word.
  2. **Thay đổi đã thống nhất**: bản ký là bản đúng. Ghi nội dung đúng; dữ liệu và tham số lấy theo bản ký.
  3. **Bản ký sai**: cần ký lại hoặc làm phụ lục. Hợp đồng giữ trạng thái chặn, tạo việc theo dõi.
  4. **Không ảnh hưởng**: bắt buộc có lý do.
- Mỗi xác nhận ghi nhật ký chỉ-ghi-thêm (người, giờ, lựa chọn, lý do), có `row_version` để tránh hai người xác nhận đè nhau.
- **Xuất báo cáo** PDF để lưu kèm hồ sơ hợp đồng trong Kho tài liệu.

### 7.2 Gửi người dùng
- Kết quả về **người đã yêu cầu đối chiếu**: số đỏ trên icon "Đối chiếu bản ký" và một dòng trong màn duyệt chung K5 (TL 37).
- [CẦN ANH XÁC NHẬN — trả lời sau]: người dùng ở đây là người nộp, người phụ trách hợp đồng, hay cả hai; có cần người thứ hai duyệt khi chọn *Thay đổi đã thống nhất* cho điểm Nghiêm trọng hay không.

### 7.3 Chặn hiệu lực
- Kết luận **Lệch nghiêm trọng** → Core phát `doi_chieu.co_lech_nghiem_trong`. Module sở hữu hợp đồng đặt trạng thái **"Chờ xác nhận đối chiếu"**:
  - CRM: nút "Hiệu lực" ở G6 bị khóa;
  - Kho tài liệu và `e_trich_xuat`: tham số trích từ bản ký **không được duyệt thành dữ liệu tầng 1** (TL 56 §5);
  - M2, M4, M9: hợp đồng chưa dùng làm căn cứ.
- **Mở chặn** khi mọi điểm Nghiêm trọng và vùng sửa tay đã xác nhận, không còn điểm nào chọn "Bản ký sai". Core phát `doi_chieu.da_xac_nhan`.
- Còn điểm "Bản ký sai" → giữ chặn tới khi có bản ký mới hoặc phụ lục; khi đó đối chiếu lại cặp mới.
- Kết luận **Cần xem**: không chặn, nhưng hiện cảnh báo trên hợp đồng tới khi xác nhận.

## 8. CSDL — schema mới `loi_doi_chieu` (Core sở hữu; chuẩn TL 55 §1)

Quy ước áp cho mọi bảng: UUID; có `phap_nhan_id`; RLS; `timestamptz`; `row_version`; nhật ký chỉ ghi thêm; migration trong `loi*`.

| Bảng | Nội dung chính |
|---|---|
| `luot_doi_chieu` | `tep_id` bản Word + phiên bản, `tep_id` bản ký + phiên bản, hợp đồng liên quan (khóa chung `danh_muc`), module gọi, người yêu cầu, kết luận, số điểm theo mức, phiên bản engine, thời gian |
| `diem_lech` | Lượt; vị trí hai bên (trang, Điều/Khoản, tọa độ); chữ bản Word, chữ bản ký; loại lệch, mức, nguồn xếp mức (quy tắc cứng / AI), lý do; đường dẫn ảnh cắt (trong kho tệp) |
| `vung_sua_tay` | Lượt, trang, tọa độ, ảnh cắt, chữ in bị đè/gạch (nếu có) |
| `trang_ocr_kem` | Lượt, trang, tỷ lệ lệch dấu |
| `xac_nhan_diem_lech` | Chỉ ghi thêm: điểm, người, lựa chọn (1–4), nội dung đúng (nếu có), lý do, thời gian |
| `loi_ocr_thuong_gap` | Cặp lỗi không đổi nghĩa đã duyệt, số lần xác nhận, người duyệt, hiệu lực |

Không sao chép nội dung văn bản hai bản vào schema này. Chỉ giữ **đoạn ngắn tại điểm lệch** và tham chiếu tới `ket_qua_xu_ly` (biến thể `ocr`) trong `loi_tai_lieu`.

## 9. Engine — capability

| Capability | Vào | Ra |
|---|---|---|
| `doi_chieu.doc_docx@1` | `tham_chieu_tep.v1` (DOCX) | `van_ban_tai_lieu.v1` + cờ track changes/comment |
| `doi_chieu.so_van_ban@1` | 2 × `van_ban_tai_lieu.v1` + `loi_ocr_thuong_gap` (Core truyền vào) | danh sách `diem_lech.v1` đã áp quy tắc cứng + nhóm lệch dấu |
| `doi_chieu.phan_loai_diem_lech@1` | điểm lệch + câu ngữ cảnh hai bản | mức + lý do. **Qua `e_hoi_ai`, khóa chỉ Local** |
| `doi_chieu.phat_hien_sua_tay@1` | ảnh trang | danh sách vùng |
| `ocr.trich_vung@1` (**bổ sung cho `e_ocr`**) | ảnh cắt + độ phân giải | chữ + cờ nghi ngờ (dùng ở mục 4 bước 3) |

- **Contract mới:** `diem_lech.v1`, `ket_qua_doi_chieu.v1`.
- **Dùng lại:** `tham_chieu_tep.v1`, `van_ban_tai_lieu.v1`, `tra_loi_ai.v1`. Anh duyệt trước khi kích hoạt (TL 55 §11.4).
- **Vòng đời:** theo chuẩn engine: tiến trình riêng; Core giữ và nhả cổng; tự kích hoạt, tự đóng; test mẫu bằng dữ liệu giả (TL 55 §10, §12).

## 10. API, SDK, sự kiện

| Route | Việc |
|---|---|
| `POST /api/v1/doi-chieu` | Tạo lượt: hai `tep_id`, hoặc `hop_dong_id` + bản ký; trả **202 + `viec_id`** |
| `GET /api/v1/doi-chieu/{id}` | Kết luận và số đếm |
| `GET /api/v1/doi-chieu/{id}/diem-lech` | Danh sách, lọc theo mức, phân trang |
| `POST /api/v1/doi-chieu/diem-lech/{id}/xac-nhan` | Xác nhận một điểm (`row_version` → 409 khi xung đột) |
| `GET /api/v1/doi-chieu/{id}/bao-cao` | Xuất báo cáo PDF |
| `GET/POST /api/v1/quan-tri/doi-chieu/loi-ocr` | Duyệt danh mục lỗi OCR thường gặp (Admin) |

- **SDK JS:** `ManDoiChieu` (màn kết quả mục 7.1), `NutDoiChieu` (để CRM, M2, M4, M9 nhúng).
- **SDK Python:** nhóm `doi_chieu`, hàm `tao()`, `ket_qua()`.
- **Sự kiện:**
  - Phát: `doi_chieu.hoan_tat`, `doi_chieu.co_lech_nghiem_trong`, `doi_chieu.da_xac_nhan`.
  - Nhận: `tai_lieu.da_xep` khi bản ký vào kho mà đã có bản Word chờ ký cùng số hợp đồng → **gợi ý đối chiếu**, không tự chạy [CẦN ANH XÁC NHẬN — trả lời sau].

## 11. Đo chất lượng trước khi bật

- **Bộ mẫu thử:**
  - Lấy hợp đồng Word thật, **cố ý sửa một danh sách điểm đã biết**: số tiền, ngày, cặp đổi nghĩa *thuê/thuế*, thêm *không*, xóa một khoản.
  - In ra, ký, sửa tay vài chỗ, rồi scan. Làm vài bộ với chất lượng scan khác nhau.
  - Đáp án là danh sách điểm đã sửa.
- **Chỉ số:**
  1. **Tỷ lệ bắt được điểm Nghiêm trọng đã cài**: yêu cầu **bắt đủ toàn bộ**.
  2. Tỷ lệ bắt được vùng sửa tay.
  3. Số lệch giả trên mỗi trang (Cần xem mà thực ra là lỗi OCR).
  4. Tỷ lệ Nhiễu OCR bị xếp sai (sửa thật mà bị ẩn): yêu cầu **bằng 0**.
- **Dữ liệu:** bộ mẫu chỉ dùng trên máy chủ nội bộ, không đưa vào `tests\fixtures`. Test tự động dùng văn bản giả.

## 12. Lát công việc (sau khi Anh duyệt cổng C; chưa ghi thời lượng vì chưa đo)

| Mã | Việc | Phụ thuộc |
|---|---|---|
| DC-0 | Khảo sát: ABBYY có xuất tọa độ từ và cờ ký tự nghi ngờ không; từ điển tiếng Việt dùng được; cách phát hiện sửa tay; dựng bộ mẫu thử mục 11 | G0 |
| DC-1 | `doi_chieu.doc_docx@1` + chuẩn hóa + kiểm trang + căn đoạn + so chữ hai lượt (có dấu / bỏ dấu) + quy tắc cứng | DC-0 |
| DC-2 | Xử lý lệch dấu (mục 4) + `ocr.trich_vung@1` + phân loại qua `e_hoi_ai` chỉ Local | DC-1, `e_ocr`, `e_hoi_ai` |
| DC-3 | Phát hiện vùng sửa tay | DC-0 |
| DC-4 | Schema `loi_doi_chieu`, quy trình, API, sự kiện chặn/mở chặn | Core G2 |
| DC-5 | `ManDoiChieu`, icon trong Kho tài liệu, nhúng vào CRM-G4/G5; đo chất lượng trên bộ mẫu | DC-2, DC-3, DC-4 |
| DC-6 | Danh mục lỗi OCR thường gặp (đề xuất → Admin duyệt) | DC-5 |

Mỗi lát có test bằng dữ liệu giả và review chéo.

## 13. Cần Anh chốt (trả lời sau, không chặn việc viết tiếp đặc tả)

1. **Người xác nhận:** người nộp đối chiếu, người phụ trách hợp đồng, hay cả hai? Khi chọn *Thay đổi đã thống nhất* cho điểm Nghiêm trọng có cần người thứ hai (kế toán/CFO) duyệt không? (mục 7.2)
2. **Vùng sửa tay** có chặn hiệu lực như Nghiêm trọng không? Đề xuất: **có**, vì chưa biết nội dung sửa. (mục 5.1)
3. **Bắt buộc đối chiếu 100%** cho nhóm hợp đồng nào (ví dụ vay, xây dựng)? Hay giữ kiểm mẫu ngẫu nhiên như CRM-G5 và chỉ chạy khi có người yêu cầu?
4. **Kiểm ký nháy / đóng dấu giáp lai trên từng trang** có cần không? (mục 6)
5. **Tự gợi ý đối chiếu** khi bản ký vào Kho tài liệu mà đã có bản Word cùng số hợp đồng? (mục 10)
6. **Hợp đồng song ngữ** (Việt – Anh) có không? Nếu có thì so cả hai phần ngôn ngữ, hay chỉ phần tiếng Việt?
7. **Vị trí thư mục `ocr-dual-release`** (đã hỏi ở TL 55 §9), dùng làm bộ OCR thứ hai ở mục 4 bước 3.
8. **Cấu hình máy Local AI** (đã hỏi ở TL 56 §13): có model thị giác hay không quyết định cách làm mục 6.
