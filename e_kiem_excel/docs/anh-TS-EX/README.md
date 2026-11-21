# Ảnh nghiệm thu TS-EX — 21/11/2026

Đã kiểm bằng Core giả (CoreGia); màn dựng bằng KttCore giả, chỉ dữ liệu DEMO.
Chưa phải ảnh màn đã nối Core thật. Cửa D2 được giả lập bằng callback đọc/lưu
của bước quy trình, kiểm CAS trong bộ nhớ.

| Ảnh | Nội dung | Chiều rộng |
|---|---|---:|
| [Toàn vẹn desktop](toan-ven-desktop.png) | Ô đích, nhãn tìm, bộ nhóm và điều kiện/loại trừ | 1180 px |
| [Khuôn cột desktop](khuon-cot-desktop.png) | Bảng cột, từ khóa, kiểu, bắt buộc và nhãn dòng dừng | 1180 px |
| [Toàn vẹn mobile](toan-ven-mobile.png) | Cùng thành phần, tự xếp một cột | 390 px |

Tái lập từ gốc repo: `node e_kiem_excel/tests/ui/chup_man.mjs`.
Script dùng Node 24 và Edge headless trên Windows; Linux có thể chỉ định
Chromium qua `KTT_TRINH_DUYET`. Không cần npm package, không đọc hồ sơ trình
duyệt thật. HTML tự chứa mã module và CSP chặn nguồn ngoài; hồ sơ/HTML chụp
đặt trong `.venv`, ngoài gói engine. Kết quả kiểm bố cục nằm ở `ket-qua.json`.

Đối chiếu `_chung/docs/mau-ui/may-ai.png`: thẻ trắng, tiêu đề/biểu tượng,
trạng thái góc phải, viền xanh xám, ô hai cột trên desktop/một cột trên mobile.
TS-EX không có dịch vụ ngoài/bí mật nên không có nút kiểm kết nối/API key;
nút Kiểm tra cài đặt chỉ kiểm cấu trúc trước khi lưu vào bước.
