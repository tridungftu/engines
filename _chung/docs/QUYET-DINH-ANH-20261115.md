# Quyết định của Anh — 15/11/2026 (bảng chọn, 4 lượt)

*Ghi nhận: Claude (lead), 15/11/2026 sáng. Văn bản này **thay** mục "quyết định tạm" của `GIAO-CODEX-THU-TU.md` §2 và trả lời §4 (Q1–Q4) của tài liệu đó. Khi khác với phiếu giao Codex cũ, văn bản này thắng.*

## 1. Kết luận

- **Engine không lưu gì trên máy.** Mọi dữ liệu engine cần giữ (cả cấu hình) nằm trong **ngăn dữ liệu của chính engine** do Core cất hộ. SDK 2.0 chưa có ngăn → mã viết **như thể đã có ngăn**, tạm chạy bằng ngăn trong bộ nhớ (RAM). Lead gửi đặc tả chỉnh SDK: `DE-NGHI-SDK-2.1.md`.
- **Cấu hình thuộc engine:** mỗi engine có **màn hình cấu hình riêng** (model AI, địa chỉ IP máy Local AI, đường dẫn Hot Folder…). Giữ đơn giản, vì cấu hình rất ít dữ liệu. Màn của engine **nạp thẳng như màn module**.
- **Mở tiếp:** Trích xuất TX-0; Mask từ MASK-4; Hóa đơn lập phiếu ZIP + bảng kê Excel. Đối chiếu và Tra cứu lập phiếu **sau khi TX-0 xong**.

## 2. Bảng quyết định

| # | Câu | Anh chốt | Hệ quả cho Codex / lead |
|---|---|---|---|
| 1 | Cấu hình máy tạm bằng tệp JSON ngoài gói (Q1 cũ) | **Không.** Cấu hình đặt ở engine: engine có màn hình cấu hình riêng; đừng làm phức tạp | Bỏ `cau_hinh_may.py` đọc tệp ngoài gói khỏi đường chạy engine. Cấu hình = một bản ghi trong ngăn của engine, sửa qua màn cấu hình của engine. Công cụ Anh tự chạy (AI-7, OCR-7) vẫn nhận tham số dòng lệnh |
| 2 | Dữ liệu tạm trên máy engine (Q2 cũ) | **Mỗi engine có một ngăn dữ liệu; engine không lưu thông tin gì.** Trong lúc chờ: lưu tạm trong bộ nhớ engine; cứ lập trình như đã có ngăn của Core; lead đưa đoạn đề nghị chỉnh SDK | Thay `kho_tam` (tệp JSON trên đĩa) bằng cổng `Ngan` + bản `NganBoNho` (RAM). Khi SDK có `app.ngan` thì tự dùng ngăn thật. Hệ quả chấp nhận: khởi động lại engine thì mất hạn mức ABBYY đã dùng và dấu chống trùng **cho tới khi có SDK 2.1** |
| 3 | Tên 4 loại dữ liệu chung (Q3 cũ) | **Duyệt cả 4:** `van_ban_tai_lieu`, `yeu_cau_ai`, `tra_loi_ai`, `van_ban_da_che` | `LOAI-DU-LIEU-RIENG.md` §1–2 thành hợp đồng chính thức |
| 4 | Cloud chỉ nhận `van_ban_da_che` (Q4 cũ) | **Đồng ý** | Năng lực Cloud bản 2 chỉ `nhan: ["van_ban_da_che"]`; M9 và nhóm 07 luôn chỉ Local |
| 5 | Giao TX-0 (Trích xuất) | **Giao ngay**, theo hướng lead nghiêng: bộ tham số qua Cài đặt bước; kết quả bảng + tệp Excel, module tự ghép cột; đo thật sức chứa model | Dùng lệnh TX-0 trong `GIAO-CODEX-e_trich_xuat.md` §4, kèm định hướng này |
| 6 | Phạm vi Hóa đơn | **Chốt XML là mốc 1; mở ZIP + bảng kê Excel.** PDF và tải cổng thuế để sau | Lập phiếu lát ZIP (báo cáo từng tệp trong gói, không gọi "đầy đủ" khi có tệp lỗi) + bảng kê XLSX (giữ đúng tiền, số 0 đầu, mã tiền tệ) |
| 7 | Tệp gốc `DANH_MUC_THAM_SO.xlsx` cho E6 | **Lấy từ bản review gốc** `D:\Claude\Ho tro review ho so xay dung\review_xaydung` | Lead (máy Anh) chép chỉ đọc, ghi SHA-256; xác nhận tệp chỉ là danh mục tham số, không có dữ liệu thật |
| 8 | Tiền tố bí danh tự sinh của Mask | **Dùng bộ MASK…:** `MASKCT`, `MASKCN`, `MASKDC`, `MASKMST`, `MASKTK`, `MASKKHAC`, `MASKTAM` | Ví dụ `[[MASKCT-0001]]`; đối tác có mã Junsky vẫn `[[<mã Junsky>]]` |
| 9 | Từ điển nhận diện của Mask | **Lấy từ Mask v2 gốc, lọc sạch** `D:\GPT\Phan mem Mask file\Mask file v2` | Lead chép, bỏ mọi tên riêng đối tác, ghi SHA; **trình Anh xem danh sách trước khi gộp** |
| 10 | Màn thử riêng của Mask | **Bỏ** `PHIEU-MASK-CHAY-THU-DEMO.md` | Thử DEMO dùng màn Chạy thử chung của Core. Màn duyệt danh sách chờ là màn của engine Mask |
| 11 | Chi tiết `van_ban_da_che` (đề xuất MASK-P) | **Duyệt, mở tiếp MASK-4** | `LOAI-DU-LIEU-RIENG.md` §3 thành chính thức; MASK-4 → MASK-6 làm ngay; MASK-7 đo DEMO rồi trình Anh trần tệp và phương án Word/Excel |
| 12 | Đối chiếu bản ký, Tra cứu | **Lập phiếu sau khi TX-0 xong.** Đối chiếu trước | Lead gộp 17 câu chờ Anh thành một bảng chọn khi lập phiếu |
| 13 | Cách gắn màn engine vào Core | **Nạp thẳng như màn module** (Anh không chọn khung cách ly) | Màn engine dùng SDK trình duyệt `KttCore` như module. Bù rủi ro: màn chỉ gọi API Core, không gọi mạng ngoài, không dùng `eval`/HTML chưa lọc; lead Core review mã màn trước khi cài gói |

## 3. Việc Anh tự làm (không phải câu hỏi)

- Chạy `e_ocr\cong-cu\KIEM-TESSERACT.cmd`, `e_hoi_ai\cong-cu\THU-LOCAL-AI-THAT.cmd`, `e_ocr\cong-cu\THU-ABBYY-THAT.cmd`.
- Xác nhận giấy phép FineReader Corporate trước khi chuyển ABBYY lên máy chủ.
- Gửi `DE-NGHI-SDK-2.1.md` cho người phụ trách SDK/Core.
