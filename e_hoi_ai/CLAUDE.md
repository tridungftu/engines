# CLAUDE.md — Project engine `e_hoi_ai` · Hỏi AI (cổng AI dùng chung)

Người đặt yêu cầu: **Anh Dũng** (CFO).
- Trả lời bằng tiếng Việt, ngắn gọn, kết luận trước.
- Không bịa số liệu; giờ ước phải ghi "ước tính"; tiền luôn ghi đơn vị (VND, USD).

**Tóm tắt engine:** Bản 1 chỉ Local AI; prompt thuộc module; tự phát hiện/chọn model; luôn có màn Cổng Local và Cổng Cloud.

## 0. Đọc trước khi làm
1. `..\_chung\docs\YEU-CAU-CHUNG-ENGINE.md` — **cổng gắn engine vào Core (API · SDK · webhook thống nhất)**. Đây là yêu cầu bắt buộc.
2. `docs\YEU-CAU-VA-HIEN-TRANG.md` — yêu cầu chi tiết của engine này; cái đã có, cái chưa có.
3. Tài liệu gốc:
   - `docs\QUYET-DINH-CUOI-e_hoi_ai.md`
   - `docs\PHIEU-ENGINE-e_hoi_ai.md`
   - `docs\KS-AI-MODEL.md`
4. `docs\VIEC.md` — danh sách việc duy nhất.
5. Quy tắc Core: `D:\Claude\Core\docs\YEU-CAU-CORE.md` (G14, Phụ lục A) và `D:\Claude\Core\docs\NGUYEN-TAC-CORE.md`.

## 1. Ba yêu cầu bắt buộc
1. **Gắn vào Core chỉ qua cổng engine chung** (API, SDK, webhook thống nhất); khai báo bằng `engine.json`.
   - Không đòi Core viết mã, route, màn hay bảng riêng cho engine này.
   - Thiếu cửa nào thì ghi vào `docs\VIEC.md` mục "Cần Core", để Anh chuyển cho lead Core.
2. **Engine không gọi engine khác, không có mật khẩu CSDL, không SQL.**
   - Bước trước hoặc bước sau do Core điều phối theo chuỗi mà module khai.
   - Dữ liệu cần giữ lâu dài nằm trong **ngăn của engine** do Core quản.
3. **Gói độc lập:** chỉ import SDK của Core (`D:\Claude\Core\goi-san-sang\sdk-phat-hanh\`); ghim thư viện; có `NGUON.md`; cài được trên máy sạch; test chạy được với Core giả của SDK.

## 2. Thư mục
- `ma-nguon\`: mã engine hiện có, là điểm xuất phát.
- `shim-kho_tri_thuc\`: shim đường cũ. Không dùng cho gói mới.
- `tests-tu-core\`, `tu-core-cu\`: test và mã thế hệ cũ chuyển từ Core sang, để tận dụng.
  - `tu-core-cu\phia-core\` là **bản sao** mã phía Core viết riêng cho engine này, chỉ để tham chiếu. Bản gốc vẫn ở Core; lead Core sẽ gỡ.
- `docs\`: tài liệu.

## 3. Cách làm
- **Chỉ dùng Claude Code.**
- Tận dụng tối đa mã đã có. Phần không dùng thì chuyển `LUU-TRU\`, không xóa.
- **SẴN SÀNG = bấm trên trình duyệt thật trong khung Core, có ảnh từng bước.** Trước mốc đó, ghi rõ "đã kiểm bằng mock".
- Giao diện ẩn hẳn thông tin kỹ thuật:
  - phiên bản và cấu trúc chỉ hiện ở phần thông tin engine trong Quản lý engine;
  - ngày dạng dd/mm/yyyy; tiền có dấu chấm hàng nghìn, kèm đơn vị;
  - lỗi viết bằng câu tiếng Việt dễ hiểu.
- Không đứng chờ Anh. Câu chờ Anh ghi vào `docs\VIEC.md`, rồi chuyển sang việc khác.

## 4. Ràng buộc cứng
- Không xóa tệp.
- Không đọc, sửa hay in: `.env`, `cau_hinh.that.toml`, `var\plhn-that`, `var\web-that`, `D:\DU-LIEU-KE-TOAN\bi-mat`.
- Không đưa mật khẩu hay khóa vào chat, log hoặc git.
- **Test chỉ dùng dữ liệu DEMO.**
- Cloud chỉ qua Mask.
- Không gửi email. Không push GitHub khi chưa có lệnh.
- Thay đổi hệ thống Windows: soạn tệp `.cmd` ASCII để Anh tự chạy.
- **Không sửa mã Core trong project này.**
