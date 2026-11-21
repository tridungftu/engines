# Giao Codex — Màn cấu hình và trình soạn Cài đặt bước cho mọi engine

*Lập 21/11/2026 (Claude, lead). Căn cứ: yêu cầu của Anh 21/11: "phần cấu hình của các engine phải có UI để người dùng thao tác dễ dàng"; hai ảnh mẫu Anh gửi: `mau-ui/may-ai.png` (Máy AI), `mau-ui/cloud-ai.png` (Kiểm tra chéo Cloud); quyết định 15/11 (cấu hình thuộc engine, màn engine nạp như màn module); rà `main` commit `90d5183`. Giờ là **ước tính của lead, chưa đo**.*

## 1. Kết luận

- **Hiện không màn nào của engine hiện lên trong Core.** SDK 2.2.0 chưa nhận khai báo màn engine (`giao_dien_quan_tri`), nên Core chỉ dựng **ô JSON chung** từ `cau_hinh.schema.json`. Người dùng thấy một ô trống, không có hướng dẫn. 7 engine đã viết sẵn `ui/*.js`, nhưng mới kiểm bằng `KttCore` giả.
- **Hai loại chỗ phải nhập JSON thô:**
  - (a) cấu hình engine (Hỏi AI, OCR, Mask, Trích xuất, Đối chiếu, Tra cứu);
  - (b) **Cài đặt bước** kiểu JSON: Phân luồng 5 ô, Kiểm Excel 3 ô, Trích xuất 3 ô, Đối chiếu 1 ô.
- **Phiếu này giao 11 lát, khoảng 35 giờ công (ước tính):**
  - phía engine viết màn đủ dùng theo nguyên tắc ở mục 2;
  - phía Core cần mở 4 cửa (mục 5). Có 4 cửa này thì màn engine thay ô JSON, không phải sửa lại engine.
- `e_hoa_don` không có cấu hình và không có Cài đặt bước JSON nên **không cần màn**.

## 2. Nguyên tắc màn (bắt buộc cho mọi lát)

1. **Tốt nhất là không nhập JSON thô** (Anh yêu cầu 21/11/2026). Mỗi ý là một ô riêng: chọn, số, công tắc, danh sách thêm/xóa dòng, bảng sửa trực tiếp. JSON chỉ còn trong mục "Nâng cao" thu gọn, chỉ đọc hoặc nhập/xuất tệp.
   **Nếu buộc phải nhập JSON thô** (chưa kịp làm trình soạn, hoặc ô nâng cao), thì **ngay tại ô** phải có đủ:
   - (a) **diễn giải cấu trúc**: bảng các trường gồm tên, kiểu, bắt buộc hay không, ý nghĩa bằng tiếng Việt, giá trị cho phép; trường lồng nhau thì diễn giải từng cấp;
   - (b) **hướng dẫn điền** ngắn: điền khi nào, bỏ trống thì engine làm gì;
   - (c) **mẫu điền sẵn** và nút "Chèn mẫu";
   - (d) **kiểm ngay khi nhập**: lỗi chỉ rõ trường/dòng sai và cách sửa, không chỉ báo "JSON không hợp lệ";
   - (e) nút "Định dạng lại".
   Áp dụng cả cho ô JSON chung mà Core đang dựng (qua `description`/`examples` trong schema, xem điểm 10).
2. **Mỗi ô có nhãn tiếng Việt + một dòng hướng dẫn + giá trị mẫu.** Lỗi hiện ngay cạnh ô, nói rõ cần sửa gì.
3. **Ô kỹ thuật** (mã băm, phiên bản bộ, trần byte, mã phê duyệt…) đặt trong "Nâng cao", có giá trị mặc định hợp lý; màn chính chỉ giữ ô người dùng thực sự cần chỉnh.
4. **Có máy hoặc dịch vụ ngoài thì có nút kiểm:**
   - "Kiểm tra kết nối", "Tự tìm", nhãn trạng thái ("Kết nối được" / "Không kết nối được" + lý do ngắn);
   - danh sách chọn lấy từ máy thật, ví dụ model trên máy AI.
5. **Bí mật** (API key…): ô nhập kiểu mật khẩu, sau khi lưu chỉ hiện "Đã lưu · •••• 4 ký tự cuối", có nút "Xóa key". Giá trị đi vào két bí mật của Core, **không lưu tệp trên máy engine**.
6. **Không xưng hô** trên màn: không dùng "Anh", "bạn". Ngày dd/mm/yyyy; tiền có dấu chấm hàng nghìn kèm đơn vị; không hiện mã kỹ thuật ngoài mục "Nâng cao".
7. **Lưu có kiểm tranh chấp** (`phien_ban_cau_hinh`/CAS). Người khác đã sửa thì báo "Cấu hình đã được người khác sửa, tải lại trước khi lưu".
8. Bố cục theo mẫu `mau-ui/may-ai.png`: thẻ có tiêu đề, biểu tượng, nhãn trạng thái góc phải; ô xếp 2 cột trên màn rộng, 1 cột trên màn hẹp. Màn tạm khóa thì có hộp cảnh báo vàng nói rõ vì sao, như `mau-ui/cloud-ai.png`.
9. Kỹ thuật:
   - màn ở `goi/<ma>/ui/*.js`, chỉ gọi `KttCore.engine(ma)` (`.cau_hinh`, `.ngan`, `.thao_tac`, `.bi_mat`) theo `DE-NGHI-SDK-2.1.md` §5–6 và mục 5 dưới đây;
   - không gọi mạng ngoài, không `eval`/`innerHTML` chưa lọc;
   - test bằng `KttCore` giả trong `tests/ui/` (Node, không mạng);
   - khai màn và thao tác dự kiến vào `goi/<ma>/KHAI-SDK-2.1.json` (chưa khai vào `engine.json` khi SDK còn từ chối).
10. Trong lúc Core chưa nạp màn:
   - bổ sung `title`, `description`, `examples` tiếng Việt cho **mọi** trường trong `cau_hinh.schema.json`, kể cả trường lồng nhau;
   - `description` gốc của schema chứa diễn giải cấu trúc và một mẫu điền đầy đủ, để ô JSON chung đáp ứng điểm 1(a)–(c);
   - tham số Cài đặt bước dạng JSON: ghi diễn giải cấu trúc, hướng dẫn và mẫu vào `mo_ta` của tham số trong `engine.json` (nếu SDK nhận) và vào `README.md` của gói.
   - Lead Core cần cho ô JSON chung hiển thị các mô tả này (mục 5, cửa D).

## 3. Rà hiện trạng (21/11/2026)

| Engine | Cấu hình engine | Màn đã viết | Vấn đề |
|---|---|---|---|
| `e_hoi_ai` | `local_ai.url`, `timeout_giay`, `quy_tac_model[]` | `cau_hinh.js` | Một ô URL; chưa tách IP/cổng, chưa có nút kiểm/tự tìm, chưa chọn model từ máy; schema ghi "do Core quản", cho `https` trong khi mã chỉ nhận `http`; **chưa có màn Cổng Cloud AI** |
| `e_ocr` | ABBYY: bật, thư mục vào/ra, thời hạn, hạn mức; Tesseract: đường dẫn, ngôn ngữ | `cau_hinh.js` (cấu hình + hạn mức + trạng thái ABBYY) | Chưa có nút kiểm Hot Folder, kiểm Tesseract; tiêu đề schema "do Core quản lý" |
| `e_mask` | `thoi_han_anh_xa_giay` | `duyet_dinh_danh.js` (chỉ duyệt) | Chưa có màn cấu hình; chưa hiện bộ tiền tố, từ điển nhận diện đang dùng |
| `e_trich_xuat` | `ngan_sach_token_vao_toi_da` | `cau_hinh.js` | Cài đặt bước JSON: `bo_tham_so_json`, `ma_truong_can_trich_json`, `yeu_cau_them_json` |
| `e_doi_chieu` | 20 trường, phần lớn là kỹ thuật (mã/băm bộ chuẩn hóa, từ điển, detector, các trần) | `cau_hinh.js`, `ket_qua.js`, `loi_ocr.js` | Màn hiện thẳng ô kỹ thuật; **xưng "Anh"** trên màn; Cài đặt bước JSON `bo_quy_tac_json` |
| `e_tra_cuu` | Quy tắc nhóm, phân loại, cắt đoạn, 14 trần ngân sách | `cau_hinh.js`, `trang_thai.js` | Ô kỹ thuật lẫn với ô nghiệp vụ; **xưng "Anh"**; Cài đặt bước `prompt` dài |
| `e_phan_luong` | (không) | `bang_ty_le.js` (xem) | Cài đặt bước JSON nặng nhất: `bo_phan_loai_json`, `chinh_sach_json`, `danh_muc_loai_json`, `khuon_cot_json`, `nguong_json` trên 5 năng lực |
| `e_kiem_excel` | (không) | (không) | Cài đặt bước JSON: `bo_nhom_json`, `khuon_cot_json`, `nhan_o_dich_json` |
| `e_hoa_don` | (không) | (không) | Không cần màn |

## 4. Các lát

| Lát | Engine | Nội dung | Giờ (ước tính) |
|---|---|---|---:|
| UI-AI-1 | e_hoi_ai | Màn **Máy AI** theo `mau-ui/may-ai.png` + thao tác `kiem_ket_noi`, `tim_may_ai`, `lay_danh_sach_model`; quy tắc model dạng bảng; sửa schema | 3 |
| UI-AI-2 | e_hoi_ai | Màn **Cổng Cloud AI** theo `mau-ui/cloud-ai.png`, trạng thái **Tạm khóa**: nhà cung cấp, model, API key (bí mật), nhật ký gửi ra ngoài. Không bật gọi Cloud | 3 |
| UI-OCR | e_ocr | Bổ sung nút "Kiểm tra Hot Folder", "Kiểm tra Tesseract" + nhãn trạng thái; chia thẻ ABBYY / Tesseract / Hạn mức; sửa schema | 3 |
| UI-MASK | e_mask | Màn cấu hình (thời hạn ánh xạ) + thẻ chỉ đọc "Bộ tiền tố" và "Từ điển nhận diện đang dùng"; gộp với màn duyệt bằng thẻ | 2 |
| UI-TX | e_trich_xuat | Hoàn thiện màn ngân sách token theo nguyên tắc §2; sửa schema | 1 |
| UI-DC | e_doi_chieu | Màn cấu hình chia "Cơ bản" (trần trang/ký tự/điểm lệch) và "Nâng cao" (mã/băm/detector chỉ đọc); bỏ xưng hô ở cả 3 màn | 3 |
| UI-TC | e_tra_cuu | Tương tự UI-DC: "Cơ bản" (ngưỡng phân loại, độ dài đoạn) / "Nâng cao" (14 trần); bỏ xưng hô | 3 |
| TS-EX | e_kiem_excel | **Trình soạn Cài đặt bước**: ô đích (chọn sheet + ô, hoặc cụm từ tìm), bộ nhóm (bảng nhóm → từ khóa, vùng, loại trừ), khuôn cột (bảng cột → từ khóa, kiểu, bắt buộc); xuất ra đúng JSON hiện có | 4 |
| TS-PL | e_phan_luong | Trình soạn cho 5 ô JSON: danh mục loại, bộ phân loại, ngưỡng (PM/TE/SAD dạng ô số), chính sách, khuôn cột; dùng chung một thành phần cho cả 5 năng lực | 6 |
| TS-DC | e_doi_chieu | Trình soạn `bo_quy_tac_json` (danh sách quy tắc cứng, cặp đổi nghĩa) | 3 |
| TS-TX | e_trich_xuat | Thành phần soạn **bộ tham số** để module nhúng vào màn quản lý bộ của module (Anh chốt 07/11 bộ thuộc module): nhập Excel (dùng E1), xem/sửa bảng, tính băm, xuất `bo_tham_so_json` + `bam_bo_tham_so` | 4 |
| | | **Tổng** | **35** |

Thứ tự đề xuất: UI-AI-1 → UI-OCR → UI-AI-2 → TS-EX → TS-PL → các lát còn lại. Các lát độc lập, giao song song được.

## 5. Cần Core (gửi lead Core qua Anh)

| Cửa | Nội dung | Lát cần |
|---|---|---|
| **D. Nạp màn engine** | Nhận `giao_dien_quan_tri[]` trong `engine.json`; nạp `ui/*.js` trong Quản lý engine như màn module, thay ô JSON chung khi engine có màn | Tất cả UI-* |
| **D2. Trình soạn Cài đặt bước** | Khi Admin sửa Cài đặt bước của một bước trong quy trình, nếu năng lực khai `giao_dien_tham_so` thì Core nạp màn soạn của engine thay ô văn bản; màn trả về đúng chuỗi giá trị tham số, Core vẫn kiểm `toi_da`/kiểu như hiện nay | TS-* |
| **E. Thao tác quản trị** | Nút trên màn gọi `KttCore.engine(ma).thao_tac(ma_thao_tac, dau_vao)`; Core chuyển thành việc ưu tiên cho engine, chờ kết quả ≤ thời hạn khai, trả về màn (`DE-NGHI-SDK-2.1.md` §6) | UI-AI-1, UI-OCR, UI-AI-2 |
| **F. Bí mật** | Ô nhập bí mật trong két Core theo tên khai ở `bi_mat[]`; màn chỉ thấy "đã lưu + 4 ký tự cuối"; engine đọc giá trị theo tên (`app.bi_mat(ten)`), không ghi log | UI-AI-2 |

## 6. Lệnh giao Codex (dán nguyên khối, thay `<LÁT>`)

```
Đọc AGENTS.md (đặc biệt quy tắc 13–14), _chung/docs/GIAO-CODEX-UI-CAU-HINH.md (đủ §2 nguyên tắc), _chung/docs/DE-NGHI-SDK-2.1.md §5–6, ảnh _chung/docs/mau-ui/may-ai.png và cloud-ai.png.
Làm lát <LÁT> theo bảng §4 của phiếu UI.
- Màn trong goi/<ma>/ui/, chỉ dùng KttCore.engine(ma) (.cau_hinh/.ngan/.thao_tac/.bi_mat); không gọi mạng ngoài, không eval/innerHTML chưa lọc; không xưng hô; ngày dd/mm/yyyy; tiền có đơn vị.
- Thao tác quản trị phía engine (nếu lát cần): viết hàm Python trong gói, kiểm bằng CoreGia + máy giả; khai dự kiến vào goi/<ma>/KHAI-SDK-2.1.json, KHÔNG thêm khóa mới vào engine.json khi SDK 2.2.0 còn từ chối.
- Bổ sung title/description/examples tiếng Việt cho mọi trường cau_hinh.schema.json của engine (nếu có).
- tests/ui/: KttCore giả (Node, không mạng) cho mọi đường: đọc, lưu, lỗi nhập, CAS tranh chấp, nút kiểm thành công/thất bại, bí mật chỉ hiện 4 ký tự cuối.
- Không đổi hành vi xử lý việc của engine; nếu đổi engine.json thì sinh lại danh mục (_chung/cong-cu/sinh_danh_muc_engine.py).
Đạt: 3 lệnh AGENTS.md §5 + test UI xanh; PR kèm ảnh chụp màn (dựng bằng KttCore giả) để lead so với ảnh mẫu.
```
