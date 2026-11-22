# UI-DC — ảnh DEMO 21/11/2026

Đã kiểm bằng Core giả (CoreGia); trang dựng bằng KttCore giả, chưa kiểm trong Core thật.
Tất cả nội dung là DEMO. Không gọi OCR, AI, Cloud hoặc dịch vụ ngoài.

| Ảnh | Nội dung |
|---|---|
| [Cơ bản](co-ban.png) | Bốn trần thường dùng, Nâng cao thu gọn, trạng thái góc phải |
| [Nâng cao](nang-cao.png) | Bộ chuẩn hóa/từ điển/detector/ngưỡng học chỉ đọc, trần kỹ thuật có hướng dẫn |
| [Mobile](mobile.png) | Viewport thật 390 px, một cột, không tràn ngang |
| [Lỗi nhập](loi-nhap.png) | Trần trang vượt 60, lỗi ngay cạnh ô |
| [CAS](cas.png) | Người khác sửa cấu hình, khóa lưu và yêu cầu tải lại |
| [Thiếu bộ](thieu-bo.png) | Chưa cấp bộ kiểm, khóa lưu |
| [Kết quả](ket-qua.png) | Hai bản DEMO, phần chưa kiểm và quyền chỉ xem |
| [Lỗi OCR](loi-ocr.png) | Danh mục chỉ đọc, không tự duyệt |

[Số đo layout thực](kiem-layout.json): tám trạng thái không tràn ngang; desktop hai cột,
mobile một cột. Ảnh được xem lại trực quan sau khi chụp.

Tái dựng từ thư mục gốc repo:

```powershell
node e_doi_chieu/tests/ui/dung_anh_ui_dc.mjs
node e_doi_chieu/tests/ui/chup_anh_ui_dc.mjs <chuong-trinh-Chrome>
node --test e_doi_chieu/tests/ui/*.test.mjs
```

`demo.html` chứa bản chụp mã màn và fixture KttCore, không thuộc gói engine.
Công cụ chụp dùng CDP loopback của Chrome cục bộ để đặt viewport chính xác;
trang DEMO có CSP chặn mạng. Bộ test Node dùng DOM/KttCore trong RAM và cấm mạng.
Không cần cài thư viện mới. Profile Chrome chỉ là dữ liệu công cụ kiểm, nằm trong
thư mục kiểm bị Git bỏ qua; không thuộc đường chạy engine.

UI-DC không có máy ngoài, nút kiểm kết nối hoặc API key. Các ca kiểm kết nối
thành công/thất bại và che bốn ký tự cuối không áp dụng cho lát này; test xác nhận
màn cấu hình không gọi `.thao_tac` hoặc `.bi_mat`.

Ba màn đã được khai trong `KHAI-SDK-2.1.json`; không có màn hay thao tác mới.
Core vẫn cần cửa D để nạp màn và hiển thị mô tả/mẫu schema trên ô JSON chung.

## Điểm chặn phạm vi

`so_chu.py` dùng bộ kiểm schema nội bộ chỉ chấp nhận tập từ khóa khép kín và
không nhận annotation `examples`. Thêm `examples` theo phiếu UI khiến bước
so văn bản từ chối snapshot hợp lệ với `DC_SAI_NGUON`.

[Diff tương thích đề xuất](../UI-DC-TUONG-THICH-SCHEMA.patch) chỉ bỏ `examples`
khỏi bản schema nội bộ dùng để kiểm snapshot, giữ nguyên các ràng buộc.
`git apply --check` đã đạt. **Chưa áp dụng** vì ghi chú lead giới hạn UI-* chỉ sửa
màn/schema/test; cần mở rộng phạm vi thêm `so_chu.py`. Không được gộp bộ thay đổi
schema hiện tại khi chưa giải quyết điểm chặn này.
