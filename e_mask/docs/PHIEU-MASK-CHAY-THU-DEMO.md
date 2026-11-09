# PHIẾU — Bật màn "Chạy thử che định danh" trên Core DEMO

Lead soạn 07/11/2026 16:15. Trạng thái: **CHỜ ANH ĐỒNG Ý** trước khi lập trình (CLAUDE.md mục 0b). Căn cứ khảo sát: `KS-MASK-3J-BAT-CHAY-THU.md`.

## 1. Anh sẽ thấy gì khi xong
Admin làm lần lượt trên Core DEMO:
1. Vào Quản trị Core → Quản lý engine → Che định danh → **Chạy thử**.
2. Chọn pháp nhân DEMO, dán một đoạn văn bản mẫu có tên người, số tiền và ngày.
3. Bấm **Che**: thấy bản đã che. Số tiền và ngày giữ nguyên, tên được thay bằng bí danh.
4. Bấm **Mở che**: thấy lại bản gốc.

Pháp nhân thật bị từ chối. Văn bản thử tự xóa sau một thời hạn.

## 2. Hiện trạng
- Đã gộp: kho Mask phía Core (SQL 118–120), kênh engine (lát F, G), đường quản trị (lát H), màn nối đường quản trị (lát I).
- Còn thiếu để bấm được thật:
  - nơi lưu văn bản thử;
  - module nguồn đứng tên việc chạy thử;
  - engine Mask được khởi chạy trên Core DEMO, có vòng nhận việc;
  - đọc kết quả;
  - dọn dữ liệu thử theo hạn.

## 3. Các lát (mỗi lát ≤ 3 tệp, Codex làm, lead kiểm)

| # | Lát | Phụ thuộc | Migration |
|---|---|---|---|
| J1 | Bảng tham chiếu chạy thử (người, phiên, pháp nhân DEMO, hạn) + cửa kiểm quyền | — | 130 |
| J2–J3 | Module nguồn nội bộ `mask_thu` (chỉ DEMO): hồ sơ, hành động lập/xem, contract kỹ thuật | J1 | có thể |
| J4 | Chuẩn bị đầu vào: lưu văn bản thử thành tệp JSON trong kho tệp Core | J1–J3 | không |
| J5 | Đọc kết quả, kiểm lại quyền khi đọc | J4 | không |
| J6–J7 | Contract và hồ sơ engine `e_mask` | — | không |
| J8 | Vòng nhận việc của engine Mask (`engines/e_mask/chay.py`) | — | không |
| J8b | Core đối soát khi engine mất phản hồi xác nhận sau lúc kết quả đã ghi: thu hồi lease, không ghi trùng ở lần thử mới (review J8, 07/11 17:00) | J8 | có thể |
| J9 | Hồ sơ engine thật cho kênh (`kenh_bi_mat.py`) | J6–J7 | không |
| J10 | Ghép vào khởi chạy Core DEMO (`chay_core.py`) | J4, J5, J9 | không |
| J11 | Dọn dữ liệu thử theo hạn (văn bản, kết quả, bí danh tạm, lượt chốt) | J1 | 131 |
| J12 | Màn: F5 và mở lại | J10 | không |
| Test cuối | Trình duyệt thật trên Core thử, có ảnh: luồng mục 1, F5, pháp nhân thật bị từ chối, phiên khác bị từ chối, hết hạn | tất cả | — |

Ước lượng 8–12 giờ (chưa đo).

Lịch sử đổi số — 08/11/2026 03:45: migration của phiếu dời sang **130/131** theo QD-TAM-20261108-03; 128 đã dùng cho nhãn ma trận, 129 dành cho chạy thử Hỏi AI, thay các số dự kiến trước đó.

## 4. Lead chốt tạm (QD-TAM-20261107-09) — Anh xem lại
- **A. Module đứng tên:** một module nguồn nội bộ riêng `mask_thu`, chỉ chạy dưới pháp nhân DEMO. Không cho Admin hay Core tự đứng tên module.
- **B. Hạn lưu:** văn bản thử và kết quả giữ **8 giờ** rồi dọn. Nhật ký và biên nhận giữ nguyên, không chứa nội dung.
- **C. F5:** bản đầu không khôi phục được phiên thử cũ; sau F5 phải nhập lại.

## 5. Trong lúc chờ Anh
Chỉ làm **J8** (vòng nhận việc của engine), thuộc phần adapter engine Mask đã được duyệt (CD-101, lát E). Các lát khác chờ Anh đồng ý.
