# Bàn giao UI-OCR — 21/11/2026

Kết luận: **Đạt trong phạm vi lát UI-OCR**, đã kiểm bằng Core giả (CoreGia),
máy giả và KttCore giả; chưa nghiệm thu với Core/ABBYY thật.

Đã làm: ba thẻ ABBYY / Tesseract / Hạn mức theo ảnh mẫu; nút kiểm nguồn,
nhãn trạng thái, hướng dẫn/mẫu/lỗi từng ô và CAS. Hai hàm quản trị chỉ kiểm
metadata/quyền Hot Folder hoặc bộ ngôn ngữ Tesseract, không gửi tài liệu,
không lưu cấu hình hay ghi hạn mức. Mọi trường schema có tiêu đề/mô tả/ví
dụ, gốc có cấu trúc và mẫu đầy đủ. Khai màn/hàm dự kiến trong
`KHAI-SDK-2.1.json`; giữ nguyên engine.json và mã xử lý việc hiện có.
Đã cập nhật VIEC.md, CHANGELOG.md, README.md và kiểm kê 45 tệp gói.

Kết quả kiểm (Python 3.13.14 trong `.venv`, SDK 2.2.0; đặt
`PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`):

```text
> .venv/Scripts/python -m kho_tri_thuc_sdk.thu e_ocr/goi/e_ocr
6/6 ví dụ [ĐẠT]
Engine e_ocr 1.0.9: mọi ví dụ chạy thử DEMO đều đạt.
Mã thoát: 0.

> .venv/Scripts/python -m pytest e_ocr/tests -q --basetemp=.pytest-tmp-ui-ocr-full-2
318 passed in 107.93s (0:01:47)
0 skipped. Mã thoát: 0.

> .venv/Scripts/python e_ocr/tests/kiem_doc_lap.py
[ĐẠT] Gói e_ocr độc lập; không import Core/kênh cũ, không có tệp biên dịch sẵn.
Mã thoát: 0.

> node --test e_ocr/tests/ui/test_cau_hinh.mjs
22 tests; 22 pass; 0 fail; 0 skipped. Mã thoát: 0.

> .venv/Scripts/python -m pytest e_ocr/tests/test_quan_tri.py -q
24 passed in 3.22s. Mã thoát: 0.

> node e_ocr/tests/ui/chup_man.mjs <thư mục playwright-core đã có>
[ĐẠT] Trình duyệt + KttCore giả: đọc/lưu, lỗi nhập, kiểm hai nguồn đạt/lỗi,
CAS/tải lại, màn hẹp; 0 yêu cầu mạng, 0 lỗi trang; 4 ảnh DEMO.

> .venv/Scripts/python -m pytest e_ocr/tests/test_ui_ocr8.py e_ocr/tests/test_sdk_22.py::test_kiem_ke_sql_du_tung_tep_va_dung_bam_bytes -q
2 passed in 3.44s. Mã thoát: 0.

> git diff --check
Không lỗi khoảng trắng.
```

Log gốc: [SDK DEMO](kiem-demo.log), [pytest cuối](kiem-pytest.log).
Lượt pytest đầu có **1 failed, 317 passed trong 181.63s** tại ca cũ
`test_huy_hoac_loi_sau_abbyy_tra_pdf_phai_don_ke_ca_chua_doc[True]`:
nhận LOI thay vì HUY. Hai biến thể kiểm riêng đạt **2 passed trong 3.98s**;
lượt toàn bộ tiếp theo đạt 318/318. Giữ [log lượt đầu](kiem-pytest-lan-1.log),
không sửa test cũ hoặc mã OCR để che lỗi. Chưa đủ căn cứ xác định nguyên
nhân; cần theo dõi tính ổn định của ca máy giả này. Sau tinh chỉnh thông
báo lỗi nhập trên UI đã chạy lại Node, trình duyệt, kiểm UI trong pytest,
kiểm kê và kiểm độc lập.

Ảnh đã xem trực tiếp: [màn rộng](01-may-rong.png), [lỗi nguồn](02-loi-nguon.png),
[CAS](03-cas.png), [màn hẹp](04-man-hep.png). Dữ liệu chỉ DEMO, Chromium
không phát sinh yêu cầu mạng; bố cục hai cột/một cột, không tràn ngang
ở 390 px. Script chụp nằm ngoài gói tại `tests/ui/chup_man.mjs`.

Thời gian thực tế: **0.47 giờ**, bắt đầu **21/11/2026 21:26:00**,
kết thúc **21/11/2026 21:54:25** (UTC+7); ước tính phiếu: **3 giờ**.

Lệch khỏi phiếu / quyết định tạm đã dùng: không đổi phạm vi nghiệp vụ.
SDK 2.2.0 chưa hỗ trợ thao tác quản trị nên CoreGia dùng adapter chỉ
trong test; khai dự kiến không vào engine.json. Kiểm Hot Folder không
chứng minh FineReader đang chạy/quyền ghi ACL thực tế. UI-OCR không khai
bí mật nên ca chỉ hiện bốn ký tự cuối không áp dụng; đã kiểm không gọi
két và không hiện/gửi trường bí mật ngoài schema. Venv kế thừa thư viện
đã cài bằng system-site-packages; SDK cài riêng từ wheel nội bộ, băm
khớp SHA256SUMS. Chưa là kiểm Linux hoặc cài máy sạch. Không thêm thư viện
runtime, không dùng mạng; playwright-core có sẵn chỉ dùng ngoài gói.

Cần Core / Chờ Anh mới phát sinh: **cửa D và E** theo phiếu UI §5:
nạp màn như module + cổng cấu hình/CAS/ngăn cho Admin; nhận thao tác quản
trị ưu tiên, quyền Admin và thời hạn 15 giây. Khi chưa có cổng, màn báo
chờ hỗ trợ. Ô JSON chung cần hiển thị mô tả/ví dụ/hướng dẫn schema.
Không có câu Chờ Anh mới. PR: **chờ lead mở**, nhánh
`codex/e_ocr-ui-ocr`; không commit/push.
